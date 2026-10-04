"""Room labels of raster pages: one question per room face, accepted by two passes or one pass + Tesseract (§3.4).

Why: Tesseract read 0 of 5 room labels on the synthetic-02 scan (docs/milestone7.md research) while both VLMs read
5/5 in the Milestone 2 bake-off, but a VLM text alone is never trusted (CLAUDE.md: two passes, keep what agrees).

- ``render_crop(image, face_box_px, px_per_m, out_dir, key)``: the face's box on the rectified page grown by 0.5 m,
  as a grey PNG whose longer side is 768 px (``<key>.png``, keys ``lbl_<level>_<n>``); ``input_sha256`` covers the
  sha256 of the decoded grey source pixels and their shape, the pixel rectangle, ``CROP_VERSION`` and the question
  (§1.4), never PNG bytes.
- ``question(face)``: the ``room_label`` request item (``answers.write_requests``).
- ``tesseract_items(image, rotations=(0, 90))``: Tesseract 5 (``eng+tur``, ``--psm 11``) as a subprocess like
  ``ocr.ocr_tesseract``, at 0° and 90° (the image turned clockwise, boxes mapped back), line items in the image's
  pixels; ``tesseract_face`` runs it on a face's crop and maps the boxes back to the rectified page;
  ``items_inside`` keeps the page items whose box centre lies in the face. Items given to ``decide`` must be in
  rectified-page pixels.
- ``decide(face, answers, tesseract=None)``: **one rule for every field** (label, size_text, area_text): a value is
  accepted when both passes give the same normalised value, or when one pass equals a Tesseract text read inside the
  face (a line, or up to three stacked lines joined with a space); else the field is None, both candidates are
  listed and, for the label, the room is ``unverified``. Null or "" never agree. Normalised = NFC, typographic
  quote marks as ASCII, Turkish-aware lower case then casefold, dotted and dotless i folded together (an upper-case
  ``I`` is ``i`` in English and ``ı`` in Turkish, so the two cannot be told apart), whitespace collapsed. Size and
  area texts count for scale corroboration only when accepted here (the caller's rule). The accepted label's box (the
  Tesseract box on the Tesseract path, else the union of the agreeing passes' boxes) is returned in page pixels for
  the blanking before the final clustering (S, §4.2).

``face`` = ``{"key", "file", "page", "level", "room_id", "crop": render_crop(...)}``; ``answers`` =
``{model_key: answer dict | None}`` as ``answers.load`` gives per key.
"""
from __future__ import annotations

import re
import subprocess
import tempfile
import unicodedata
from pathlib import Path
from typing import Optional

import numpy as np

from wenart import building as B
from wenart.recognition import answers as A
from wenart.recognition import crops as C
from wenart.recognition import ocr, schemas

TASK = "room_label"
FIELDS: tuple[str, ...] = ("label", "size_text", "area_text")
CROP_LONG_PX = 768
GROW_M = 0.5
TESSERACT_LANG = "eng+tur"
TESSERACT_PSM = 11
TESSERACT_OEM = 1
TESSERACT_ENGINE = f"tesseract --oem {TESSERACT_OEM} --psm {TESSERACT_PSM} -l {TESSERACT_LANG}"
MAX_JOIN_LINES = 3                 # a label printed on up to three lines is compared joined
JOIN_GAP = 1.5                     # stacked: the next line starts within 1.5 x the line height below
JOIN_OVERLAP = 0.3                 # and overlaps the line horizontally by >= 30 % of the narrower one
# Evidence confidences (the room-label schema has no confidence field; these record the acceptance path).
AGREE_CONFIDENCE = 0.85
TESSERACT_CONFIDENCE = 0.8
UNACCEPTED_CONFIDENCE = 0.3

_QUOTES = str.maketrans({"’": "'", "‘": "'", "′": "'", "`": "'", "´": "'", "”": '"', "“": '"', "″": '"'})


# --------------------------------------------------------------------------
# Normalised values
# --------------------------------------------------------------------------

def norm_value(text) -> Optional[str]:
    """The comparison form of a label, size or area text (see the module docstring); None for null or blank."""
    if text is None:
        return None
    value = unicodedata.normalize("NFC", str(text)).translate(_QUOTES)
    value = B.turkish_lower(value).casefold()
    value = value.replace("i̇", "i").replace("ı", "i")
    value = re.sub(r"\s+", " ", value).strip()
    return value or None


# --------------------------------------------------------------------------
# Crop and question
# --------------------------------------------------------------------------

def _box_of(face_box_px) -> tuple[float, float, float, float]:
    """A pixel box [c0, r0, c1, r1] or a polygon [[x, y], ...] -> its bounds."""
    arr = np.asarray(face_box_px, dtype=np.float64)
    if arr.ndim == 2:
        return float(arr[:, 0].min()), float(arr[:, 1].min()), float(arr[:, 0].max()), float(arr[:, 1].max())
    x0, y0, x1, y1 = (float(v) for v in arr)
    return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)


def crop_rect(face_box_px, px_per_m: float) -> list[int]:
    """The face's pixel box grown by GROW_M on every side, as whole pixels [c0, r0, c1, r1)."""
    x0, y0, x1, y1 = _box_of(face_box_px)
    g = GROW_M * float(px_per_m)
    return [int(np.floor(x0 - g)), int(np.floor(y0 - g)), int(np.ceil(x1 + g)), int(np.ceil(y1 + g))]


def out_size(rect: list[int]) -> tuple[int, int]:
    """(width, height) of the crop image: the longer side CROP_LONG_PX, the aspect kept."""
    w, h = max(1, rect[2] - rect[0]), max(1, rect[3] - rect[1])
    s = CROP_LONG_PX / max(w, h)
    return max(1, int(round(w * s))), max(1, int(round(h * s)))


def render_crop(image, face_box_px, px_per_m: float, out_dir: Path, key: str) -> dict:
    """Write ``<out_dir>/<key>.png``; return ``{"png", "input_sha256", "crop": {"rect_px", "size"}}``."""
    page = np.asarray(image)
    if page.ndim == 3:
        import cv2
        page = cv2.cvtColor(page, cv2.COLOR_RGB2GRAY)
    page = page.astype(np.uint8)
    rect = crop_rect(face_box_px, px_per_m)
    src = C.cut(page, rect)
    width, height = out_size(rect)
    desc = {"crop_version": C.CROP_VERSION, "kind": "raster_face", "rect_px": rect, "size": [width, height],
            "pixels": C.array_sha256(src), "question": C.question_digest(TASK)}
    png = C.save_png(C.resize_to(src, width, height), Path(out_dir) / f"{key}.png")
    return {"png": str(png), "input_sha256": C.canonical_sha256(desc),
            "crop": {"rect_px": rect, "size": [width, height], "crop_version": C.CROP_VERSION}}


def question(face: dict) -> dict:
    """The ``room_label`` request item of one room face (image relative to ``<out>/recognition``)."""
    crop = face.get("crop")
    if not crop or "input_sha256" not in crop:
        raise ValueError(f"face {face.get('key')!r}: render its crop first (room_labels.render_crop)")
    return {
        "key": face["key"],
        "task": TASK,
        "page": face.get("page"),
        "images": [f"{A.CROPS_DIR}/{Path(crop['png']).name}"],
        "context": {"file": face.get("file"), "level": face.get("level"), "room_id": face.get("room_id"),
                    "crop": crop.get("crop")},
        "input_sha256": crop["input_sha256"],
    }


def box_to_page(box_1000, crop: dict) -> Optional[list[float]]:
    """A 0..1000 box of the crop image -> page pixels of the rectified page (None for no box)."""
    if box_1000 is None:
        return None
    c0, r0, c1, r1 = crop["rect_px"]
    x0, y0, x1, y1 = (float(v) / schemas.BOX_MAX for v in box_1000)
    xs = sorted((c0 + x0 * (c1 - c0), c0 + x1 * (c1 - c0)))
    ys = sorted((r0 + y0 * (r1 - r0), r0 + y1 * (r1 - r0)))
    return [round(xs[0], 1), round(ys[0], 1), round(xs[1], 1), round(ys[1], 1)]


# --------------------------------------------------------------------------
# Tesseract
# --------------------------------------------------------------------------

def _rotate_box_back(box, height: int) -> list[float]:
    """A box of the image turned 90° clockwise -> the original image (x = y', y = H - x')."""
    x0, y0, x1, y1 = box
    return [y0, height - x1, y1, height - x0]


def tesseract_items(image, rotations=(0, 90), lang: str = TESSERACT_LANG, psm: int = TESSERACT_PSM,
                    oem: int = TESSERACT_OEM, timeout_s: float = 300.0) -> list[dict]:
    """Tesseract line items (``ocr.make_item`` shape + ``rotation``) of an image file or grey array, boxes in the
    image's pixels. 90 = the image turned clockwise first (text running bottom-to-top), boxes mapped back."""
    import cv2
    if isinstance(image, (str, Path)):
        arr = cv2.imread(str(image), cv2.IMREAD_GRAYSCALE)
        if arr is None:
            raise FileNotFoundError(image)
    else:
        arr = np.asarray(image).astype(np.uint8)
    height = arr.shape[0]
    items: list[dict] = []
    with tempfile.TemporaryDirectory() as tmp:
        for rot in rotations:
            img = arr if rot == 0 else cv2.rotate(arr, cv2.ROTATE_90_CLOCKWISE)
            path = Path(tmp) / f"r{rot}.png"
            cv2.imwrite(str(path), img)
            cmd = ["tesseract", str(path), "stdout", "--oem", str(oem), "--psm", str(psm), "-l", lang, "tsv"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s, check=True)
            for item in ocr.parse_tesseract_tsv(proc.stdout, engine=f"tesseract-{lang}-psm{psm}"):
                if rot == 90:
                    item["box"] = [round(v, 1) for v in _rotate_box_back(item["box"], height)]
                elif rot != 0:
                    raise ValueError(f"rotation {rot} not supported (0 or 90)")
                item["rotation"] = rot
                items.append(item)
    return items


def tesseract_face(face: dict, rotations=(0, 90)) -> list[dict]:
    """Tesseract on a face's crop PNG (``face["crop"]["png"]``), boxes mapped back to rectified-page pixels."""
    crop = face["crop"]
    c0, r0, c1, r1 = crop["crop"]["rect_px"]
    width, height = crop["crop"]["size"]
    sx, sy = (c1 - c0) / float(width), (r1 - r0) / float(height)
    items = tesseract_items(crop["png"], rotations=rotations)
    for item in items:
        x0, y0, x1, y1 = item["box"]
        item["box"] = [round(c0 + x0 * sx, 1), round(r0 + y0 * sy, 1), round(c0 + x1 * sx, 1),
                       round(r0 + y1 * sy, 1)]
    return items


def items_inside(items: list[dict], face_px) -> list[dict]:
    """The items whose box centre lies inside the face (a pixel box or polygon)."""
    arr = np.asarray(face_px, dtype=np.float64)
    if arr.ndim == 2:
        from shapely.geometry import Point, Polygon
        poly = Polygon(arr.tolist())
        return [i for i in items
                if poly.covers(Point((i["box"][0] + i["box"][2]) / 2.0, (i["box"][1] + i["box"][3]) / 2.0))]
    x0, y0, x1, y1 = _box_of(face_px)
    out = []
    for i in items:
        cx, cy = (i["box"][0] + i["box"][2]) / 2.0, (i["box"][1] + i["box"][3]) / 2.0
        if x0 <= cx <= x1 and y0 <= cy <= y1:
            out.append(i)
    return out


def _stacked(upper: dict, lower: dict) -> bool:
    ub, lb = upper["box"], lower["box"]
    h = max(1e-6, ub[3] - ub[1])
    if not (0 <= lb[1] - ub[1] <= h * (1.0 + JOIN_GAP)):
        return False
    overlap = min(ub[2], lb[2]) - max(ub[0], lb[0])
    narrower = max(1e-6, min(ub[2] - ub[0], lb[2] - lb[0]))
    return overlap >= JOIN_OVERLAP * narrower


def tesseract_texts(tesseract) -> list[dict]:
    """The comparable Tesseract texts: every line and every stack of 2..3 lines joined with a space.

    ``tesseract`` = line items (``tesseract_items``) or plain strings; returns ``[{"text", "box", "confidence"}]``
    (box and confidence None for plain strings).
    """
    out: list[dict] = []
    lines = []
    for t in tesseract or []:
        if isinstance(t, str):
            if t.strip():
                out.append({"text": t, "box": None, "confidence": None})
        elif str(t.get("text") or "").strip():
            lines.append(t)
    lines.sort(key=lambda i: (i.get("rotation", 0), i["box"][1], i["box"][0]))
    for i, line in enumerate(lines):
        out.append({"text": line["text"], "box": list(line["box"]), "confidence": line.get("confidence")})
        stack = [line]
        for nxt in lines[i + 1:]:
            if len(stack) >= MAX_JOIN_LINES:
                break
            if nxt.get("rotation", 0) == line.get("rotation", 0) and _stacked(stack[-1], nxt):
                stack.append(nxt)
                boxes = [s["box"] for s in stack]
                out.append({"text": " ".join(s["text"] for s in stack),
                            "box": [min(b[0] for b in boxes), min(b[1] for b in boxes),
                                    max(b[2] for b in boxes), max(b[3] for b in boxes)],
                            "confidence": min(float(s.get("confidence") or 0.0) for s in stack)})
    return out


# --------------------------------------------------------------------------
# Decision
# --------------------------------------------------------------------------

def _usable(data) -> Optional[dict]:
    if not isinstance(data, dict) or schemas.validation_errors(TASK, data):
        return None
    return data


def _union(boxes: list) -> Optional[list[float]]:
    boxes = [b for b in boxes if b is not None]
    if not boxes:
        return None
    return [min(b[0] for b in boxes), min(b[1] for b in boxes), max(b[2] for b in boxes), max(b[3] for b in boxes)]


def decide(face: dict, answers: Optional[dict], tesseract=None) -> dict:
    """The §3.4 rule for one face; see the module docstring.

    Returns ``{"label", "size_text", "area_text", "box", "status", "fields": {field: {"value", "path":
    "two_pass"|"tesseract"|None, "candidates": [...], "tesseract_match"}}, "evidence", "warnings"}``; ``box`` is
    the accepted label's box in rectified-page pixels (None when the label is not accepted or no box was given).
    """
    answers = answers or {}
    models = A.load_models()
    crop = (face.get("crop") or {}).get("crop")
    key = face.get("key")
    warnings: list[str] = []
    passes = []
    for mk in A.MODEL_KEYS:
        info = A.model_info(mk, models)
        raw = answers.get(mk)
        data = _usable(raw)
        if data is None:
            warnings.append(f"{key}: pass {info['pass']} ({info['id']}) gave "
                            f"{'no answer' if raw is None else 'an invalid answer'}")
            continue
        box_px = box_to_page(data.get("box"), crop) if crop else None
        passes.append({"key": mk, "info": info, "data": data, "box_px": box_px})
    texts = tesseract_texts(tesseract)
    by_norm: dict[str, dict] = {}
    for t in texts:
        n = norm_value(t["text"])
        if n is not None and n not in by_norm:
            by_norm[n] = t
    fields: dict[str, dict] = {}
    for field in FIELDS:
        cands = [{"model_key": p["key"], "pass": p["info"]["pass"], "model": p["info"]["id"],
                  "value": p["data"].get(field)} for p in passes]
        norms = [norm_value(c["value"]) for c in cands]
        entry = {"value": None, "path": None, "candidates": cands, "tesseract_match": None, "passes": []}
        if len(cands) == 2 and norms[0] is not None and norms[0] == norms[1]:
            entry.update(value=cands[0]["value"], path="two_pass", passes=[0, 1])
        else:
            matched = [(i, by_norm[n]) for i, n in enumerate(norms) if n is not None and n in by_norm]
            if len({norms[i] for i, _ in matched}) == 1:
                i, t = matched[0]
                entry.update(value=cands[i]["value"], path="tesseract", tesseract_match=t,
                             passes=[j for j, _ in matched])
            elif matched:
                warnings.append(f"{key}: {field}: the passes match different Tesseract texts "
                                f"({', '.join(repr(cands[i]['value']) for i, _ in matched)}): not accepted")
            if entry["value"] is None and any(n is not None for n in norms):
                warnings.append(f"{key}: {field} not accepted: "
                                + ", ".join(f"pass {c['pass']} {c['value']!r}" for c in cands))
        fields[field] = entry
    label = fields["label"]
    box = None
    if label["path"] == "two_pass":
        box = _union([passes[i]["box_px"] for i in label["passes"]])
    elif label["path"] == "tesseract":
        box = label["tesseract_match"].get("box") or _union([passes[i]["box_px"] for i in label["passes"]])
    evidence = []
    file, page = str(face.get("file") or ""), face.get("page")
    for idx, p in enumerate(passes):
        agreed = idx in label["passes"]
        conf = (AGREE_CONFIDENCE if label["path"] == "two_pass" else TESSERACT_CONFIDENCE) if agreed \
            else UNACCEPTED_CONFIDENCE
        evidence.append(B.evidence(file, "ai", conf, page=page, entity=f"recognition:{key}", model=p["info"]["id"],
                                   pass_=p["info"]["pass"], pixel_box=p["box_px"],
                                   text=p["data"].get("label")))
    for field in FIELDS:
        t = fields[field]["tesseract_match"]
        if t is not None:
            evidence.append(B.evidence(file, "ocr", float(t["confidence"]) if t.get("confidence") is not None
                                       else TESSERACT_CONFIDENCE, page=page, model=TESSERACT_ENGINE,
                                       pixel_box=t.get("box"), text=t["text"]))
    for f in fields.values():
        del f["passes"]
    return {
        "label": fields["label"]["value"],
        "size_text": fields["size_text"]["value"],
        "area_text": fields["area_text"]["value"],
        "box": box,
        "status": "verified" if fields["label"]["value"] is not None else "unverified",
        "fields": fields,
        "evidence": evidence,
        "warnings": warnings,
    }
