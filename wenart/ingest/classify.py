"""Page classification: one ``PageRecord`` per file/page of a project folder.

Per page we decide
- ``kind``: ``vector`` (PDF page with paths and a text layer, DXF/DWG),
  ``scan`` (image or PDF page without a text layer whose paper outline is a
  rectangle filling the image) or ``photo`` (EXIF camera tags, or a paper
  outline that is a non-rectangular quadrilateral);
- ``page_class`` from title keywords (``KAT PLANI`` -> floor_plan, ``MOBİLYA``
  -> furniture_plan, ``KESİT`` -> section, ``GÖRÜNÜŞ`` -> elevation,
  ``VAZİYET`` -> site_plan; English ``FLOOR PLAN``, ``FURNITURE (LAYOUT)
  PLAN``);
- the level (``level_label_raw`` -> normalised label, order, ``level_id``;
  Turkish titles and English ``GROUND FLOOR``, ``FIRST FLOOR``, ``BASEMENT``,
  ``3RD FLOOR``, ...);
- the scale source (``$INSUNITS`` or ``ÖLÇEK 1/100``), with evidence;
- which extractor reads the page (``extractor``): the synthetic readers
  (``pdf_extract``, ``dxf_extract``) for pages drawn the synthetic way, the
  generic core (``generic.core``) for everything else.

Generic rule (docs/milestone7.md §2.1): a vector page without a title is a
floor plan (confidence 0.6, ``classifier "generic_labels"``, evidence = the
room-name runs) when it carries at least two room-name labels (English or
Turkish, ``generic.labels.room_name_runs``) **and** a cheap wall test
passes (``wall_structure``: a hatch comb, dark grey fills, closed thin
polygons, or for DXF a hatch/solid/closed polyline on a wall layer). Labels
alone never make a plan. A project with exactly one plan page and no level
title gets level ``L0`` "Ground floor" as an *assumed* value
(``label_source "assumed"``); several untitled plan pages cannot be ordered
(``level_problem``, the pipeline stops with ``needs_review``).

DWG: a DWG with a DXF of the same name in the project is recorded with
``skip_reason "DXF of the same name is used"`` and not converted (the DXF
wins). Otherwise ``dwg.convert`` writes the DXF into ``work_dir``; its
version, entity counts and audit are kept in ``conversion``.

PDF pages with paths but no characters and no large image are vector pages
whose texts are drawn as geometry (AutoCAD SHX fonts): they need OCR, which
the raster area builds later; until then they are skipped with
``skip_reason "text drawn as geometry ..."`` and the pipeline reports
``needs_review``.

Raster pages (docs/milestone7.md §2.1, §4): images (``.png``, ``.jpg``,
``.tif``, ...) and PDF pages with no paths and an image covering >= 50 % of
the page (rendered at 200 dpi) are read by the raster adapter
(``wenart.ingest.raster``: rectification, Tesseract at 0° and 90°, strokes,
wall mask) while they are classified; the ``RasterPage`` is kept on the record
(``raster_page``) for the pipeline. Their texts classify them: a title gives
the class and the level (``classifier "ocr"``, confidence = the title's OCR
confidence, at most 0.9); an untitled page is a floor plan (confidence 0.5,
``classifier "generic_labels"``) when OCR reads >= 2 room names or the adapter
found >= 2 dimension texts with their lines; otherwise ``other``. A photo
without a page quadrilateral is ``other`` with that reason. An ``ocr``
callable (tests, the Milestone 2 bake-off) replaces Tesseract for the
classification texts. Nothing is guessed from the file name.
"""
from __future__ import annotations

import math
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import cv2
import numpy as np
import pdfplumber
from PIL import Image

from wenart import building as B
from wenart.ingest import cad_pdf
from wenart.ingest import dwg as dwg_mod
from wenart.ingest import dxf_generic
from wenart.ingest.dxf_extract import has_synthetic_layers, metres_per_unit_from_insunits, read_dxf
from wenart.ingest.generic import labels as generic_labels
from wenart.ingest.generic.model import GenericPage, TextRun
from wenart.ingest.model import (METRES_PER_POINT, TextItem, normalise_level, page_class_for, parse_scale_text,
                                 text_role)
from wenart.ingest.pdf_extract import LW_TOLERANCE, LW_WALL, read_page_objects

IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp"}
SKIP_DIRS = {"truth", "outputs", "debug"}
RASTER_SKIP_REASON = "raster page: no plan title, no room names and no dimension texts readable by OCR"
RASTER_GENERIC_CONFIDENCE = 0.5
RASTER_TITLE_MAX_CONFIDENCE = 0.9
NO_TITLE_REASON = "no plan title found (KAT PLANI, MOBİLYA PLANI, KESİT, GÖRÜNÜŞ, VAZİYET, FLOOR PLAN)"
SAME_STEM_REASON = "DXF of the same name is used"
SHX_TEXT_REASON = ("text drawn as geometry (no text layer, e.g. AutoCAD SHX fonts): such pages need OCR of the "
                   "vector page, not built yet")
GENERIC_CONFIDENCE = 0.6
ASSUMED_LEVEL = ("Ground floor", 0)

# Cheap wall test (§2.1), page units, no scale yet; fractions of the page's short side.
HATCH_MIN_LINES = 200
HATCH_ANGLE_TOL_DEG = 1.0
HATCH_STEP_REL = 0.005           # median perpendicular step of the comb
HATCH_LENGTH_REL = 0.05          # hatch lines are short
DARK_FILL_LUMINANCE = 0.35       # dark grey fills (walls.py's rule) ...
DARK_FILL_CHROMA = 0.10
DARK_FILL_MIN_REL = 0.05         # ... at least one wall-sized (not an arrowhead or a dot)
THIN_POLYGONS_MIN = 4            # closed thin polygons (outline walls)
THIN_POLYGON_WIDTH_REL = 0.02
THIN_POLYGON_ELONGATION = 4.0

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
    # Milestone 7 (docs/milestone7.md §2.1); not serialised unless said so.
    classifier: Optional[str] = None           # title | generic_labels | ocr (serialised)
    extractor: str = "synthetic"               # synthetic (pdf_extract / dxf_extract) | generic (generic.core)
    label_source: Optional[str] = None         # title | assumed (levels[].label_source)
    level_problem: Optional[str] = None        # why the level cannot be decided (needs_review)
    wall_test: Optional[str] = None            # what passed the cheap wall test
    conversion: Optional[dict] = None          # DWG: dwg.Conversion.to_json()
    generic_page: Optional[GenericPage] = None  # the page as read for the generic test (reused by the pipeline)
    raster_page: Optional[object] = None       # raster pages: raster.RasterPage read while classifying (pipeline)

    def is_extractable(self) -> bool:
        readable = self.kind == "vector" or (self.kind in ("scan", "photo") and self.extractor == "raster")
        return readable and self.page_class in ("floor_plan", "furniture_plan") and self.skip_reason is None

    def to_json(self) -> dict:
        return {
            "page": self.page, "class": self.page_class, "skip_reason": self.skip_reason, "kind": self.kind,
            "level_id": self.level_id, "level_label_raw": self.level_label_raw, "classifier": self.classifier,
            "scale": self.scale, "transform_to_building": None, "confidence": self.confidence,
            "evidence": list(self.evidence), "debug_image": None,
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
        elif normalise_level(item.text) is not None:
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
    record.classifier = record.classifier or "title"
    level = normalise_level(title.text)
    if level is not None:
        record.level_label, record.level_order = level
        record.level_id = B.level_id(record.level_order)
        record.label_source = "title"


# --------------------------------------------------------------------------
# Generic rule: room-name labels + a wall structure (§2.1)
# --------------------------------------------------------------------------

def _straight_ends(st) -> Optional[tuple[tuple[float, float], tuple[float, float]]]:
    """End points of an open, unfilled stroke whose points lie on its chord (a hatch line candidate)."""
    if st.closed or st.fill is not None or len(st.pts) < 2 or st.arc is not None:
        return None
    a, b = st.pts[0], st.pts[-1]
    length = math.dist(a, b)
    if length <= 0:
        return None
    if len(st.pts) > 2:
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        if any(abs((p[0] - a[0]) * uy - (p[1] - a[1]) * ux) > 1e-3 * length for p in st.pts[1:-1]):
            return None
    return a, b


def _hatch_test(page: GenericPage, short: float) -> Optional[str]:
    """>= 200 strokes of one colour within +-1 deg, each <= 5 % of the short side, whose perpendicular offsets
    have a median step <= 0.5 % of it (a hatch comb)."""
    by_colour: dict = {}
    for st in page.strokes:
        ends = _straight_ends(st)
        if ends is None:
            continue
        (ax, ay), (bx, by) = ends
        length = math.hypot(bx - ax, by - ay)
        if length > HATCH_LENGTH_REL * short:
            continue
        angle = math.degrees(math.atan2(by - ay, bx - ax)) % 180.0
        key = tuple(round(c, 3) for c in st.colour) if st.colour else None
        by_colour.setdefault(key, []).append((angle, (ax + bx) / 2.0, (ay + by) / 2.0))
    for colour, items in by_colour.items():
        if len(items) < HATCH_MIN_LINES:
            continue
        arr = np.array(items, dtype=float)
        counts = np.bincount(np.round(arr[:, 0]).astype(int) % 180, minlength=180)
        for peak in np.argsort(counts)[::-1][:3]:
            diff = np.abs((arr[:, 0] - peak + 90.0) % 180.0 - 90.0)
            group = arr[diff <= HATCH_ANGLE_TOL_DEG]
            if len(group) < HATCH_MIN_LINES:
                continue
            t = math.radians(float(np.median(group[:, 0])))
            offsets = np.unique(np.round(-group[:, 1] * math.sin(t) + group[:, 2] * math.cos(t), 4))
            if len(offsets) < 2:
                continue
            step = float(np.median(np.diff(offsets)))
            if step <= HATCH_STEP_REL * short:
                return (f"hatch comb of {len(group)} lines at {math.degrees(t):.0f} deg, median step "
                        f"{step:.3g} {page.units}")
    return None


def _luminance(rgb) -> float:
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def wall_structure(page: GenericPage) -> Optional[str]:
    """The cheap wall test of §2.1 in page units (no scale yet): what passed, or None. A hatch comb; or a dark grey
    fill of wall size (one bbox side >= 5 % of the page's short side, so arrowheads and dots do not count); or
    >= 4 closed thin polygons (4-12 vertices, short side <= 2 % of the page's short side, >= 4 x longer)."""
    from shapely.geometry import Polygon

    short = max(min(page.size), 1e-9)
    hatch = _hatch_test(page, short)
    if hatch:
        return hatch
    thin = 0
    for st in page.strokes:
        if not st.closed or len(st.pts) < 3:
            continue
        xs = [p[0] for p in st.pts]
        ys = [p[1] for p in st.pts]
        if st.fill is not None:
            lum, chroma = _luminance(st.fill), max(st.fill) - min(st.fill)
            if lum <= DARK_FILL_LUMINANCE and chroma <= DARK_FILL_CHROMA \
                    and max(max(xs) - min(xs), max(ys) - min(ys)) >= DARK_FILL_MIN_REL * short:
                return f"dark grey fill {st.id}"
        if st.colour is not None and 4 <= len(st.pts) <= 12:
            poly = Polygon(st.pts)
            if not poly.is_valid or poly.area <= 0:
                continue
            rect = list(poly.minimum_rotated_rectangle.exterior.coords)
            a, b = math.dist(rect[0], rect[1]), math.dist(rect[1], rect[2])
            lo, hi = min(a, b), max(a, b)
            if 0 < lo <= THIN_POLYGON_WIDTH_REL * short and hi >= THIN_POLYGON_ELONGATION * lo:
                thin += 1
                if thin >= THIN_POLYGONS_MIN:
                    return f"{thin} closed thin polygons"
    return None


def dxf_wall_layer_entities(doc) -> Optional[str]:
    """DXF: a HATCH or SOLID, or a closed polyline, on a wall-hint layer (``WALL``, ``A-WALL``, ``DUVAR``, ...)."""
    for ent in doc.modelspace():
        layer = ent.dxf.get("layer") or ""
        if not dxf_generic.is_wall_hint_layer(layer):
            continue
        kind = ent.dxftype()
        if kind in ("HATCH", "SOLID"):
            return f"{kind}:{ent.dxf.handle} on layer {layer}"
        if kind == "LWPOLYLINE" and ent.closed or kind == "POLYLINE" and ent.is_closed:
            return f"closed {kind}:{ent.dxf.handle} on layer {layer}"
    return None


def _text_runs(texts: list[TextItem]) -> list[TextRun]:
    return [TextRun(id=t.entity, text=t.text, box=tuple(t.box), height=t.height, rotation_deg=t.rotation_deg)
            for t in texts]


def apply_generic_rule(record: PageRecord, runs: list[TextRun], wall_test: Optional[str], page_no: Optional[int],
                       evidence_of=None) -> bool:
    """Turn an untitled vector page into a ``generic_labels`` floor plan when >= 2 room-name runs and a wall
    structure exist; the evidence lists the runs. Returns whether it applied."""
    names = generic_labels.room_name_runs(runs)
    if len(names) < 2 or not wall_test:
        why = (f"only {len(names)} room-name label(s)" if len(names) < 2 else "no wall structure (hatch, dark fill, "
               "thin outlines or wall-layer entities)")
        record.skip_reason = f"{NO_TITLE_REASON}; generic rule not met: {why}"
        return False
    record.page_class = "floor_plan"
    record.confidence = GENERIC_CONFIDENCE
    record.classifier = "generic_labels"
    record.extractor = "generic"
    record.wall_test = wall_test
    record.skip_reason = None
    for run in names:
        if evidence_of is not None:
            record.evidence.append(evidence_of(run))
        else:
            record.evidence.append(B.evidence(record.file, "vector", 1.0, page=page_no, entity=run.id,
                                              text=run.text))
    return True


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
    synthetic = has_synthetic_layers(doc)
    record.extractor = "synthetic" if synthetic else "generic"
    apply_level(record, title)
    if title is not None:
        record.evidence.append(B.evidence(file_rel, "vector", confidence, layer=None, entity=title.entity, text=title.text))
    insunits = doc.header.get("$INSUNITS", 0)
    # The exact factors for in, ft, mm, cm, m (ezdxf's table gives 0.0254000000001 for inches); others from ezdxf.
    mpu = dxf_generic.units_to_m(insunits) or metres_per_unit_from_insunits(insunits)
    if mpu is not None:
        record.scale = {"metres_per_unit": mpu, "method": "dxf_insunits", "confidence": 1.0,
                        "evidence": B.evidence(file_rel, "vector", 1.0, entity=f"$INSUNITS={insunits}")}
    if page_class == "other":
        record.skip_reason = NO_TITLE_REASON
        if not synthetic:
            # Texts of the whole model space, block texts and ATTRIBs included (room tags are often blocks).
            runs = dxf_generic.collect_texts(doc, file_rel)
            wall = dxf_wall_layer_entities(doc)
            if wall is None and len(generic_labels.room_name_runs(runs)) >= 2:
                page = dxf_generic.read_page(path, file_rel)
                record.generic_page = page
                wall = wall_structure(page)
            apply_generic_rule(record, runs, wall, None,
                               evidence_of=lambda r: dict(r.evidence[0]) if r.evidence else
                               B.evidence(file_rel, "vector", 1.0, entity=r.id, text=r.text))
    if auditor.has_errors:
        record.confidence = min(record.confidence, 0.9)
    return record


def same_stem_dxf(path: Path) -> Optional[Path]:
    """A DXF next to the DWG with the same stem (any letter case), or None."""
    for other in sorted(path.parent.iterdir()):
        if other.is_file() and other.suffix.lower() == ".dxf" and other.stem.lower() == path.stem.lower():
            return other
    return None


def _classify_dwg(file_rel: str, path: Path, work_dir: Optional[Path]) -> PageRecord:
    if same_stem_dxf(path) is not None:
        return PageRecord(file=file_rel, page=1, format="dwg", kind="vector", page_class="other", confidence=0.0,
                          skip_reason=SAME_STEM_REASON)
    try:
        conversion = dwg_mod.convert(path, work_dir)
    except (dwg_mod.ConverterNotFound, dwg_mod.ConversionError, FileNotFoundError) as exc:
        return PageRecord(file=file_rel, page=1, format="dwg", kind="vector", page_class="other", confidence=0.0,
                          skip_reason=f"DWG conversion failed: {exc}")
    record = _classify_dxf(file_rel, conversion.dxf_path, "dwg", conversion.converter)
    record.conversion = conversion.to_json()
    return record


def _wall_rectangles(objects) -> int:
    """Closed 4-corner paths of the synthetic wall line width (``pdf_extract.LW_WALL``)."""
    return sum(1 for p in objects.paths if abs(p.linewidth - LW_WALL) <= LW_TOLERANCE and p.corners())


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
                    record.skip_reason = NO_TITLE_REASON
                    generic_page = cad_pdf.page_from_pdfplumber(page, number, file_rel)
                    runs = generic_page.texts
                    wall = wall_structure(generic_page) if len(generic_labels.room_name_runs(runs)) >= 2 else None
                    if apply_generic_rule(record, runs, wall, number):
                        record.generic_page = generic_page
                elif _wall_rectangles(objects) == 0:
                    # A titled page not drawn the synthetic way (no 0.5 pt wall rectangles): the generic core.
                    record.extractor = "generic"
            elif objects.paths and not objects.n_chars and not _large_image(page):
                record = PageRecord(file=file_rel, page=number, format="pdf", kind="vector", page_class="other",
                                    source_path=str(path), skip_reason=SHX_TEXT_REASON)
            else:
                # No text layer: an embedded scan (or an empty page), read by the raster adapter at 200 dpi.
                record = PageRecord(file=file_rel, page=number, format="pdf", kind="scan", source_path=str(path))
                _classify_raster_record(record, path, ocr)
            records.append(record)
    return records


def _large_image(page) -> bool:
    """An embedded image covering >= 50 % of the page (a scanned or raster-only page)."""
    area = float(page.width) * float(page.height)
    for im in page.images:
        w = abs(float(im["x1"]) - float(im["x0"]))
        h = abs(float(im["bottom"]) - float(im["top"]))
        if area > 0 and w * h >= 0.5 * area:
            return True
    return False


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


def _raster_text_items(rp) -> list[TextItem]:
    """The adapter's OCR runs as ``TextItem``s (page units of the rectified page, y up)."""
    out = []
    for run in rp.page.texts:
        ev = dict(run.evidence[0]) if run.evidence else None
        out.append(TextItem(text=run.text, start=(run.box[0], run.box[1]), box=list(run.box),
                            rotation_deg=run.rotation_deg, entity=run.id, height=run.height,
                            role=text_role(run.text), evidence=ev))
    return out


def _classify_raster_record(record: PageRecord, path: Optional[Path], ocr: Optional[Callable]) -> None:
    """A raster page (image or raster-only PDF page): class, level and evidence from its OCR texts (module
    docstring). The ``RasterPage`` is kept on the record for the pipeline."""
    from wenart.ingest import raster as raster_mod

    record.extractor = "raster"
    rp = None
    if ocr is not None:
        texts = []
        for item in ocr(path):
            texts.append(TextItem(text=item["text"], start=(item["box"][0], item["box"][1]), box=list(item["box"]),
                                  rotation_deg=0.0, entity="pixel_box", height=item["box"][3] - item["box"][1],
                                  role=text_role(item["text"]),
                                  evidence=B.evidence(record.file, "ocr", 0.5, pixel_box=list(item["box"]),
                                                      text=item["text"])))
    else:
        try:
            rp = raster_mod.read_page(path, record.page, record.file, record.kind)
        except (OSError, ValueError, subprocess.SubprocessError, cv2.error) as exc:
            record.page_class, record.confidence = "other", 0.0
            record.skip_reason = f"raster page not readable: {exc}"
            return
        record.raster_page = rp
        if rp.review and rp.rect.review:
            record.page_class, record.confidence = "other", 0.0
            record.skip_reason = f"{record.kind} page: {rp.rect.review}"
            return
        texts = _raster_text_items(rp)
    record.texts = texts
    page_class, title, _ = classify_texts(texts)
    if title is not None:
        record.page_class = page_class
        title_conf = float((title.evidence or {}).get("confidence", 0.5))
        record.confidence = round(min(RASTER_TITLE_MAX_CONFIDENCE, title_conf), 2)
        apply_level(record, title)
        record.classifier = "ocr"
        record.evidence.append(dict(title.evidence) if title.evidence else
                               B.evidence(record.file, "ocr", 0.5, pixel_box=title.box, text=title.text))
        record.skip_reason = None
        return
    runs = [TextRun(id=t.entity, text=t.text, box=tuple(t.box), height=t.height, rotation_deg=t.rotation_deg,
                    source="ocr", evidence=[t.evidence] if t.evidence else []) for t in texts]
    names = generic_labels.room_name_runs(runs)
    dims = (rp.info.get("dims") or []) if rp is not None else []
    if len(names) >= 2 or len(dims) >= 2:
        record.page_class = "floor_plan"
        record.confidence = RASTER_GENERIC_CONFIDENCE
        record.classifier = "generic_labels"
        record.skip_reason = None
        for run in names:
            record.evidence.append(dict(run.evidence[0]) if run.evidence else
                                   B.evidence(record.file, "ocr", 0.5, text=run.text))
        if not names:
            record.evidence.append(B.evidence(record.file, "ocr", 0.5, text=f"{len(dims)} dimension texts with lines"))
        return
    record.page_class, record.confidence = "other", 0.0
    record.skip_reason = RASTER_SKIP_REASON


def _classify_image(file_rel: str, path: Path, ocr: Optional[Callable]) -> PageRecord:
    kind, reason = raster_kind(path)
    record = PageRecord(file=file_rel, page=1, format="image", kind=kind, source_path=str(path))
    _classify_raster_record(record, path, ocr)
    # The scan/photo decision is image processing (EXIF tags, the paper outline), not an AI answer.
    record.evidence.append(B.evidence(file_rel, "raster", 0.8 if kind == "photo" else 0.9, text=f"kind: {reason}"))
    return record


# --------------------------------------------------------------------------
# Entry point
# --------------------------------------------------------------------------

def assign_untitled_levels(records: list[PageRecord]) -> None:
    """Level of untitled plan pages (§2.1): a project whose only plan page has no level title gets ``L0`` "Ground
    floor" as an assumed value (``label_source "assumed"``); several untitled plan pages, or an untitled page next
    to titled ones, cannot be ordered (``level_problem``)."""
    plans = [r for r in records if r.is_extractable()]
    untitled = [r for r in plans if r.level_id is None]
    if not untitled:
        return
    if len(plans) == 1:
        record = untitled[0]
        record.level_label, record.level_order = ASSUMED_LEVEL
        record.level_id = B.level_id(record.level_order)
        record.label_source = "assumed"
        return
    where = ", ".join(f"{r.file} p{r.page}" for r in untitled)
    for record in untitled:
        record.level_problem = (f"cannot order untitled plan pages ({where})" if len(untitled) > 1 else
                                f"{record.page_class} without a level title next to titled plan pages "
                                f"(found: {record.level_label_raw!r})")


def classify_pages(project_dir: str | Path, work_dir: Optional[str | Path] = None,
                   ocr: Optional[Callable] = None) -> list[PageRecord]:
    """Classify every page of every document in ``project_dir``.

    ``work_dir`` receives DWG conversions (required for a DWG: a converted DXF is never written into the
    project folder; without it the DWG is recorded as not convertible).
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
    assign_untitled_levels(records)
    return records
