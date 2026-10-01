"""OCR for raster plan pages: PaddleOCR (GPU, primary) and Tesseract (CPU, cross-check).

One output shape for both engines: ``{"text", "text_norm", "box", "confidence", "engine"}``
with ``box = [x0, y0, x1, y1]`` in page pixels (origin top-left).

PaddleOCR 3.7 (verified in the PaddleOCR repo at tag v3.7.0,
docs/version3.x/pipeline_usage/OCR.en.md and paddleocr/_pipelines/ocr.py):
``PaddleOCR(lang=..., ocr_version=..., device=..., use_doc_orientation_classify=...,
use_doc_unwarping=..., use_textline_orientation=...)``; ``ocr.predict(path)`` returns
one result per page whose ``json["res"]`` (same content as ``save_to_json``) carries
``rec_texts`` (list[str]), ``rec_scores`` (list[float]), ``rec_boxes`` (n x 4 int
``[x_min, y_min, x_max, y_max]``) and ``rec_polys``. ``lang="tr"`` (Turkish) is listed
for PP-OCRv5 and PP-OCRv6; with ``ocr_version="PP-OCRv5"`` it selects the
``latin_PP-OCRv5_mobile_rec`` recognition model. ``device="gpu:0"`` or ``"cpu"``.

Tesseract 5: ``tesseract <image> stdout --oem 1 --psm 11 -l tur tsv``; the TSV has
one row per word (level 5) with ``block_num/par_num/line_num`` and ``left/top/
width/height/conf``. Words of one line are merged into one item here, because the
plan labels are multi-word (``YATAK ODASI``) and the truth lists them as one text.

Both engines are imported/started lazily so this module imports without paddle
or a tesseract binary.
"""
from __future__ import annotations

import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any, Optional

from wenart import geometry as G
from wenart.building import turkish_lower

PADDLE_LANG = "tr"
PADDLE_OCR_VERSION = "PP-OCRv5"
TESSERACT_LANG = "tur"
TESSERACT_PSM = 11
TESSERACT_OEM = 1
CROSS_CHECK_IOU = 0.5

_DECIMAL_COMMA = re.compile(r"(?<=\d),(?=\d)")
_AREA_UNIT = re.compile(r"\bm2\b")


# --------------------------------------------------------------------------
# Normalisation (shared with metrics.py)
# --------------------------------------------------------------------------

def normalise_text(text: str) -> str:
    """Comparison form of a plan text: NFC, Turkish lower-case, single spaces,
    decimal comma -> dot inside numbers, ``m2`` -> ``m²``, no edge punctuation.

    ``ZEMİN KAT PLANI`` -> ``zemin kat planı``; ``SALON 24,50 m2`` -> ``salon 24.50 m²``.
    Dotted/dotless i are kept apart on purpose: an OCR engine that reads ``ZEMIN``
    for ``ZEMİN`` made a mistake and the metric should see it.
    """
    value = unicodedata.normalize("NFC", text)
    value = turkish_lower(value)
    value = _DECIMAL_COMMA.sub(".", value)
    value = _AREA_UNIT.sub("m²", value)
    value = re.sub(r"\s+", " ", value).strip()
    return value.strip(" .,:;-_|")


def make_item(text: str, box, confidence: float, engine: str) -> dict:
    """The one item shape used by both engines."""
    return {
        "text": text,
        "text_norm": normalise_text(text),
        "box": [round(float(v), 1) for v in box],
        "confidence": round(float(confidence), 4),
        "engine": engine,
    }


# --------------------------------------------------------------------------
# Tesseract (CPU)
# --------------------------------------------------------------------------

def parse_tesseract_tsv(tsv: str, engine: str = "tesseract") -> list[dict]:
    """Merge the word rows of a Tesseract TSV into line items (pure, testable)."""
    lines: dict[tuple[str, str, str, str], dict] = {}
    rows = tsv.splitlines()
    if not rows:
        return []
    header = rows[0].split("\t")
    col = {name: i for i, name in enumerate(header)}
    for row in rows[1:]:
        parts = row.split("\t")
        if len(parts) < len(header):
            continue
        if parts[col["level"]] != "5":
            continue
        word = parts[col["text"]].strip()
        conf = float(parts[col["conf"]])
        if not word or conf < 0:
            continue
        key = (parts[col["page_num"]], parts[col["block_num"]], parts[col["par_num"]], parts[col["line_num"]])
        left, top = float(parts[col["left"]]), float(parts[col["top"]])
        width, height = float(parts[col["width"]]), float(parts[col["height"]])
        box = [left, top, left + width, top + height]
        entry = lines.setdefault(key, {"words": [], "confs": [], "box": box})
        entry["words"].append(word)
        entry["confs"].append(conf)
        b = entry["box"]
        entry["box"] = [min(b[0], box[0]), min(b[1], box[1]), max(b[2], box[2]), max(b[3], box[3])]
    items = []
    for entry in lines.values():
        conf = sum(entry["confs"]) / len(entry["confs"]) / 100.0
        items.append(make_item(" ".join(entry["words"]), entry["box"], conf, engine))
    return items


def ocr_tesseract(image: str | Path, lang: str = TESSERACT_LANG, psm: int = TESSERACT_PSM,
                  oem: int = TESSERACT_OEM, timeout_s: float = 600.0) -> list[dict]:
    """Run the tesseract binary on an image file and return line items."""
    cmd = ["tesseract", str(image), "stdout", "--oem", str(oem), "--psm", str(psm), "-l", lang, "tsv"]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, check=True)
    return parse_tesseract_tsv(proc.stdout)


# --------------------------------------------------------------------------
# PaddleOCR (GPU)
# --------------------------------------------------------------------------

_paddle_pipelines: dict[tuple, Any] = {}


def paddle_pipeline(lang: str = PADDLE_LANG, ocr_version: str = PADDLE_OCR_VERSION,
                    device: Optional[str] = None):
    """A cached ``paddleocr.PaddleOCR`` pipeline (the import happens here, lazily)."""
    key = (lang, ocr_version, device)
    if key not in _paddle_pipelines:
        from paddleocr import PaddleOCR  # heavy: only on the pod
        kwargs: dict[str, Any] = {
            "lang": lang,
            "ocr_version": ocr_version,
            # The scans are upright pages with a known orientation: skip the
            # document-level preprocessing models (faster, fewer downloads).
            "use_doc_orientation_classify": False,
            "use_doc_unwarping": False,
            "use_textline_orientation": True,  # dimension texts along vertical walls are rotated
        }
        if device is not None:
            kwargs["device"] = device
        _paddle_pipelines[key] = PaddleOCR(**kwargs)
    return _paddle_pipelines[key]


def _paddle_result_dict(res) -> dict:
    """The plain dict of one PaddleOCR result (``res.json["res"]`` per the docs, with fallbacks)."""
    try:
        data = res.json
        if isinstance(data, dict) and "res" in data:
            return data["res"]
        if isinstance(data, dict):
            return data
    except AttributeError:
        pass
    return dict(res)


def paddle_items_from_result(res_dict: dict, engine: str = "paddleocr") -> list[dict]:
    """``rec_texts`` / ``rec_scores`` / ``rec_boxes`` (or ``rec_polys``) -> items (pure, testable)."""
    texts = list(res_dict.get("rec_texts") or [])
    scores = list(res_dict.get("rec_scores") or [])
    boxes = res_dict.get("rec_boxes")
    polys = res_dict.get("rec_polys")
    items = []
    for i, text in enumerate(texts):
        if boxes is not None and len(boxes) > i:
            box = [float(v) for v in list(boxes[i])[:4]]
        elif polys is not None and len(polys) > i:
            box = G.bbox([(float(p[0]), float(p[1])) for p in polys[i]])
        else:
            continue
        score = float(scores[i]) if i < len(scores) else 0.0
        if not str(text).strip():
            continue
        items.append(make_item(str(text), box, score, engine))
    return items


def ocr_paddle(image: str | Path, lang: str = PADDLE_LANG, ocr_version: str = PADDLE_OCR_VERSION,
               device: Optional[str] = None) -> list[dict]:
    """Run PaddleOCR on an image file and return items."""
    pipeline = paddle_pipeline(lang, ocr_version, device)
    items: list[dict] = []
    for res in pipeline.predict(str(image)):
        items.extend(paddle_items_from_result(_paddle_result_dict(res), f"paddleocr-{ocr_version}-{lang}"))
    return items


# --------------------------------------------------------------------------
# Cross-check and the page entry point
# --------------------------------------------------------------------------

def cross_check(primary: list[dict], secondary: list[dict], iou_thresh: float = CROSS_CHECK_IOU) -> list[dict]:
    """Mark every primary item with what the secondary engine read at the same place.

    Adds ``cross_text`` (the overlapping secondary text or None) and ``agrees``
    (True when the normalised texts are equal). Items are copied, not changed.
    """
    out = []
    for item in primary:
        best, best_iou = None, 0.0
        for other in secondary:
            iou = G.box_iou(item["box"], other["box"])
            if iou >= iou_thresh and iou > best_iou:
                best, best_iou = other, iou
        copy = dict(item)
        copy["cross_text"] = best["text"] if best else None
        copy["agrees"] = bool(best and best["text_norm"] == item["text_norm"])
        out.append(copy)
    return out


def _looks_like_gpu_problem(exc: BaseException) -> bool:
    text = str(exc).lower()
    return any(k in text for k in ("gpu architecture", "cuda", "cudnn", "gpu", "device"))


def ocr_page(image: str | Path, *, use_paddle: bool = True, use_tesseract: bool = True,
             device: Optional[str] = None) -> dict:
    """OCR one page with both engines.

    Returns ``{"items": [...], "paddle": [...], "tesseract": [...], "primary": name,
    "errors": {...}}``. ``items`` are the primary engine's items (PaddleOCR when it ran,
    else Tesseract) with the cross-check fields from the other engine.
    """
    paddle_items: list[dict] = []
    tess_items: list[dict] = []
    errors: dict[str, str] = {}
    if use_paddle:
        try:
            paddle_items = ocr_paddle(image, device=device)
        except Exception as exc:  # noqa: BLE001 - reported, never hidden
            errors["paddle"] = f"{type(exc).__name__}: {exc}"
            # A PaddlePaddle wheel without kernels for this GPU (seen on Blackwell with the
            # CUDA 12.6 wheel: "Unsupported GPU architecture") still works on the CPU. The
            # GPU error stays recorded; the CPU result is marked as such.
            if device != "cpu" and _looks_like_gpu_problem(exc):
                _paddle_pipelines.pop((PADDLE_LANG, PADDLE_OCR_VERSION, device), None)
                try:
                    paddle_items = ocr_paddle(image, device="cpu")
                    errors["paddle"] += " -> retried on the CPU, which worked"
                    for item in paddle_items:
                        item["engine"] += "-cpu"
                except Exception as exc2:  # noqa: BLE001
                    errors["paddle_cpu"] = f"{type(exc2).__name__}: {exc2}"
    if use_tesseract:
        try:
            tess_items = ocr_tesseract(image)
        except Exception as exc:  # noqa: BLE001
            errors["tesseract"] = f"{type(exc).__name__}: {exc}"
    if paddle_items:
        primary, items = "paddle", cross_check(paddle_items, tess_items)
    else:
        primary, items = "tesseract", cross_check(tess_items, paddle_items)
    return {"items": items, "paddle": paddle_items, "tesseract": tess_items, "primary": primary, "errors": errors}
