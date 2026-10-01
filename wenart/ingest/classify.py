"""Page classification: one ``PageRecord`` per file/page of a project folder.

Per page we decide
- ``kind``: ``vector`` (PDF page with paths and a text layer, DXF/DWG),
  ``scan`` (image or PDF page without a text layer whose paper outline is a
  rectangle filling the image) or ``photo`` (EXIF camera tags, or a paper
  outline that is a non-rectangular quadrilateral);
- ``page_class`` from title keywords (``KAT PLANI`` -> floor_plan, ``MOBİLYA``
  -> furniture_plan, ``KESİT`` -> section, ``GÖRÜNÜŞ`` -> elevation,
  ``VAZİYET`` -> site_plan);
- the level (``level_label_raw`` -> normalised label, order, ``level_id``);
- the scale source (``$INSUNITS`` or ``ÖLÇEK 1/100``), with evidence.

Raster pages have no text layer here. When an ``ocr`` callable is given
(the Milestone 2 bake-off supplies one later) its texts are classified with
confidence 0.5; otherwise the page is ``other`` with a ``skip_reason``.
Nothing is guessed from the file name.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import cv2
import numpy as np
import pdfplumber
from PIL import Image

from wenart import building as B
from wenart.ingest import dwg as dwg_mod
from wenart.ingest.dxf_extract import metres_per_unit_from_insunits, read_dxf
from wenart.ingest.model import METRES_PER_POINT, TextItem, page_class_for, parse_scale_text, text_role
from wenart.ingest.pdf_extract import read_page_objects

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
SKIP_DIRS = {"truth", "outputs", "debug"}
RASTER_SKIP_REASON = "no text layer: raster pages need OCR/VLM recognition (Milestone 2 bake-off), not run here"

# EXIF tags that identify a camera (Make, Model).
_EXIF_CAMERA_TAGS = (271, 272)


@dataclass
class PageRecord:
    """Classification result for one page; serialised into ``documents[].pages[]``."""
    file: str                                  # project-relative path
    page: int                                  # 1-based
    format: str                                # dwg | dxf | pdf | image
    kind: str                                  # vector | scan | photo
    page_class: str = "other"
    confidence: float = 0.0
    level_label_raw: Optional[str] = None
    level_label: Optional[str] = None
    level_order: Optional[int] = None
    level_id: Optional[str] = None
    scale: Optional[dict] = None
    evidence: list = field(default_factory=list)
    skip_reason: Optional[str] = None
    converter: Optional[str] = None            # DWG only
    source_path: Optional[str] = None          # the file to extract from (converted DXF for DWG)
    texts: list = field(default_factory=list)  # TextItems used for the decision (not serialised)

    def is_extractable(self) -> bool:
        return self.kind == "vector" and self.page_class in ("floor_plan", "furniture_plan") and self.skip_reason is None

    def to_json(self) -> dict:
        return {
            "page": self.page, "class": self.page_class, "skip_reason": self.skip_reason, "kind": self.kind,
            "level_id": self.level_id, "level_label_raw": self.level_label_raw, "scale": self.scale,
            "transform_to_building": None, "confidence": self.confidence, "evidence": list(self.evidence),
            "debug_image": None,
        }


def document_format(file: str) -> Optional[str]:
    suffix = Path(file).suffix.lower()
    if suffix == ".dxf":
        return "dxf"
    if suffix == ".dwg":
        return "dwg"
    if suffix == ".pdf":
        return "pdf"
    if suffix in IMAGE_SUFFIXES:
        return "image"
    return None


def project_documents(project_dir: Path) -> list[Path]:
    """Document files of a project folder (top level only, sorted, known formats)."""
    files = []
    for path in sorted(Path(project_dir).iterdir()):
        if path.is_file() and not path.name.startswith(".") and document_format(path.name):
            files.append(path)
    return files


# --------------------------------------------------------------------------
# Decisions from texts
# --------------------------------------------------------------------------

def classify_texts(texts: list[TextItem]) -> tuple[str, Optional[TextItem], float]:
    """(page_class, title text, confidence) from the texts of a page.

    The title is the text with a class keyword; among several the tallest
    wins. A level label without a class keyword (e.g. ``ZEMİN KAT``) counts
    as a floor plan with lower confidence.
    """
    candidates = []
    for item in texts:
        page_class = page_class_for(item.text)
        if page_class is not None:
            candidates.append((item.height, 1.0, page_class, item))
        elif B.normalise_level_label(item.text) is not None:
            candidates.append((item.height, 0.7, "floor_plan", item))
    if not candidates:
        return "other", None, 0.5 if texts else 0.0
    candidates.sort(key=lambda c: (c[1], c[0]), reverse=True)
    _, confidence, page_class, item = candidates[0]
    return page_class, item, confidence


def apply_level(record: PageRecord, title: Optional[TextItem]) -> None:
    """Fill the level fields of a record from its title text."""
    if title is None:
        return
    record.level_label_raw = title.text
    level = B.normalise_level_label(title.text)
    if level is not None:
        record.level_label, record.level_order = level
        record.level_id = B.level_id(record.level_order)


# --------------------------------------------------------------------------
# Per format
# --------------------------------------------------------------------------

def _classify_dxf(file_rel: str, path: Path, fmt: str, converter: Optional[str]) -> PageRecord:
    doc, auditor = read_dxf(path)
    texts = []
    for ent in doc.modelspace().query("TEXT MTEXT"):
        text = ent.dxf.text if ent.dxftype() == "TEXT" else ent.plain_text()
        height = float(ent.dxf.height if ent.dxftype() == "TEXT" else ent.dxf.char_height)
        texts.append(TextItem(text=text, start=(ent.dxf.insert.x, ent.dxf.insert.y), box=[0, 0, 0, 0],
                              rotation_deg=float(ent.dxf.rotation), entity=f"{ent.dxftype()}:{ent.dxf.handle}",
                              height=height, role=text_role(text)))
    page_class, title, confidence = classify_texts(texts)
    record = PageRecord(file=file_rel, page=1, format=fmt, kind="vector", page_class=page_class,
                        confidence=confidence, converter=converter, source_path=str(path), texts=texts)
    apply_level(record, title)
    if title is not None:
        record.evidence.append(B.evidence(file_rel, "vector", confidence, layer=None, entity=title.entity, text=title.text))
    insunits = doc.header.get("$INSUNITS", 0)
    mpu = metres_per_unit_from_insunits(insunits)
    if mpu is not None:
        record.scale = {"metres_per_unit": mpu, "method": "dxf_insunits", "confidence": 1.0,
                        "evidence": B.evidence(file_rel, "vector", 1.0, entity=f"$INSUNITS={insunits}")}
    if page_class == "other":
        record.skip_reason = "no plan title found (KAT PLANI, MOBİLYA PLANI, KESİT, GÖRÜNÜŞ, VAZİYET)"
    if auditor.has_errors:
        record.confidence = min(record.confidence, 0.9)
    return record


def _classify_dwg(file_rel: str, path: Path, work_dir: Optional[Path]) -> PageRecord:
    try:
        dxf_path, converter = dwg_mod.dwg_to_dxf(path, work_dir)
    except (dwg_mod.ConverterNotFound, dwg_mod.ConversionError, FileNotFoundError) as exc:
        return PageRecord(file=file_rel, page=1, format="dwg", kind="vector", page_class="other", confidence=0.0,
                          skip_reason=f"DWG conversion failed: {exc}")
    record = _classify_dxf(file_rel, dxf_path, "dwg", converter)
    return record


def _classify_pdf(file_rel: str, path: Path, ocr: Optional[Callable]) -> list[PageRecord]:
    records = []
    with pdfplumber.open(str(path)) as pdf:
        for number, page in enumerate(pdf.pages, start=1):
            objects = read_page_objects(page)
            if objects.paths and objects.n_chars:
                page_class, title, confidence = classify_texts(objects.texts)
                record = PageRecord(file=file_rel, page=number, format="pdf", kind="vector", page_class=page_class,
                                    confidence=confidence, source_path=str(path), texts=objects.texts)
                apply_level(record, title)
                if title is not None:
                    record.evidence.append(B.evidence(file_rel, "vector", confidence, page=number,
                                                      entity=title.entity, text=title.text))
                scale_text = next((t for t in objects.texts if t.role == "scale"), None)
                if scale_text is not None and parse_scale_text(scale_text.text):
                    record.scale = {"metres_per_unit": parse_scale_text(scale_text.text) * METRES_PER_POINT,
                                    "method": "pdf_scale_text", "confidence": 1.0,
                                    "evidence": B.evidence(file_rel, "vector", 1.0, page=number,
                                                           entity=scale_text.entity, text=scale_text.text)}
                if page_class == "other":
                    record.skip_reason = "no plan title found (KAT PLANI, MOBİLYA PLANI, KESİT, GÖRÜNÜŞ, VAZİYET)"
            else:
                # No text layer: an embedded scan (or an empty page). OCR of PDF
                # pages would need rendering first; the raster path does that.
                record = PageRecord(file=file_rel, page=number, format="pdf", kind="scan", source_path=str(path))
                _classify_raster_record(record, None, ocr)
            records.append(record)
    return records


def raster_kind(path: Path) -> tuple[str, str]:
    """``(kind, reason)`` for an image: photo when EXIF names a camera or the
    paper outline is a non-rectangular quadrilateral; scan otherwise."""
    try:
        with Image.open(path) as im:
            exif = im.getexif()
            if any(tag in exif for tag in _EXIF_CAMERA_TAGS):
                return "photo", "EXIF camera tags"
    except Exception:  # noqa: BLE001 - unreadable EXIF is not fatal
        pass
    gray = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if gray is None:
        return "scan", "image not readable by OpenCV, assumed scan"
    h, w = gray.shape
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return "scan", "no paper outline found"
    biggest = max(contours, key=cv2.contourArea)
    approx = cv2.approxPolyDP(biggest, 0.02 * cv2.arcLength(biggest, True), True).reshape(-1, 2)
    coverage = cv2.contourArea(biggest) / float(w * h)
    if len(approx) == 4 and coverage < 0.97:
        corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
        # Distance of each paper corner to the nearest image corner, relative to the size.
        shifts = [min(np.hypot(*(p - c)) for c in corners) / max(w, h) for p in approx.astype(np.float32)]
        if max(shifts) > 0.02:
            return "photo", f"paper outline is a skewed quadrilateral (corners moved up to {max(shifts) * 100:.1f}%)"
    return "scan", "paper outline fills the image"


def _classify_raster_record(record: PageRecord, path: Optional[Path], ocr: Optional[Callable]) -> None:
    if ocr is None or path is None:
        record.page_class = "other"
        record.confidence = 0.0
        record.skip_reason = RASTER_SKIP_REASON
        return
    texts = []
    for item in ocr(path):
        texts.append(TextItem(text=item["text"], start=(item["box"][0], item["box"][1]), box=list(item["box"]),
                              rotation_deg=0.0, entity="pixel_box", height=item["box"][3] - item["box"][1],
                              role=text_role(item["text"])))
    page_class, title, _ = classify_texts(texts)
    record.texts = texts
    record.page_class = page_class if page_class != "other" else "floor_plan"
    record.confidence = 0.5
    apply_level(record, title)
    if title is not None:
        record.evidence.append(B.evidence(record.file, "ocr", 0.5, pixel_box=title.box, text=title.text))
    record.skip_reason = "raster page: geometry needs the recognition path (not in the vector pipeline)"


def _classify_image(file_rel: str, path: Path, ocr: Optional[Callable]) -> PageRecord:
    kind, reason = raster_kind(path)
    record = PageRecord(file=file_rel, page=1, format="image", kind=kind, source_path=str(path))
    _classify_raster_record(record, path, ocr)
    record.evidence.append(B.evidence(file_rel, "ai", 0.8 if kind == "photo" else 0.9, text=f"kind: {reason}"))
    return record


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def classify_pages(project_dir: str | Path, work_dir: Optional[str | Path] = None,
                   ocr: Optional[Callable] = None) -> list[PageRecord]:
    """Classify every page of every document in ``project_dir``.

    ``work_dir`` receives DWG conversions (default: next to the DWG).
    ``ocr`` is an optional callable ``(image_path) -> [{"text", "box", "confidence"}]``.
    """
    project_dir = Path(project_dir)
    work = Path(work_dir) if work_dir else None
    records: list[PageRecord] = []
    for path in project_documents(project_dir):
        file_rel = path.relative_to(project_dir).as_posix()
        fmt = document_format(path.name)
        if fmt == "dxf":
            records.append(_classify_dxf(file_rel, path, "dxf", None))
        elif fmt == "dwg":
            records.append(_classify_dwg(file_rel, path, work))
        elif fmt == "pdf":
            records.extend(_classify_pdf(file_rel, path, ocr))
        else:
            records.append(_classify_image(file_rel, path, ocr))
    return records
