"""CPU tests for wenart.ingest.generic.scale: dimension finder and scale rules (docs/milestone7.md §2.3),
on hand-made pages, on real01 and on the synthetic PDF pages (read with a small local pdfplumber helper,
since the CAD-PDF adapter of §2.2 is another area's file)."""
import json
import math
from pathlib import Path

import pdfplumber
import pytest
import yaml
from shapely.geometry import Point, box

from wenart import units as U
from wenart.ingest.generic import labels as L
from wenart.ingest.generic import scale as S
from wenart.ingest.generic.model import DimensionPrim, GenericPage, Stroke, TextRun
from wenart.ingest.model import METRES_PER_POINT
from wenart.ingest.pdf_extract import merge_chars

ROOT = Path(__file__).resolve().parents[1]
REAL01 = ROOT / "projects" / "real01" / "real01.pdf"
REFERENCE = ROOT / "tests" / "fixtures" / "real01_reference.yaml"
H = 10.0   # text height of the hand-made pages (points)


# --------------------------------------------------------------------------
# Local helper: one pdfplumber page -> GenericPage (y up, Béziers flattened from curve['path'])
# --------------------------------------------------------------------------

def _rgb(colour):
    if colour is None:
        return None
    if isinstance(colour, (int, float)):
        return (float(colour),) * 3
    c = tuple(float(v) for v in colour)
    if len(c) == 1:
        return c * 3
    if len(c) == 4:
        k = c[3]
        return tuple((1 - v) * (1 - k) for v in c[:3])
    return c if len(c) == 3 else None


def _flatten(path, height, steps=8):
    pts, closed = [], False
    for op in path:
        if op[0] in ("m", "l"):
            pts.append((op[1][0], height - op[1][1]))
        elif op[0] == "c":
            p0 = pts[-1]
            c1, c2, p3 = [(x, height - y) for x, y in op[1:4]]
            for i in range(1, steps + 1):
                t = i / steps
                m = 1 - t
                pts.append(tuple(m ** 3 * p0[k] + 3 * m * m * t * c1[k] + 3 * m * t * t * c2[k] + t ** 3 * p3[k]
                                 for k in (0, 1)))
        elif op[0] == "h":
            closed = True
    if len(pts) > 2 and math.dist(pts[0], pts[-1]) < 1e-6:
        closed = True
    return pts, closed


def pdf_page(path, page_no=1, file_rel=None, scale=1.0, raster=False, dpi=None):
    """``scale`` multiplies every coordinate (pt -> px for the raster stand-in)."""
    with pdfplumber.open(str(path)) as pdf:
        pg = pdf.pages[page_no - 1]
        height = float(pg.height)
        strokes = []
        for kind, objs in (("line", pg.lines), ("curve", pg.curves), ("rect", pg.rects)):
            for obj in objs:
                pts, closed = _flatten(obj["path"], height)
                pts = [(x * scale, y * scale) for x, y in pts]
                bezier = any(op[0] == "c" for op in obj["path"])
                strokes.append(Stroke(
                    id=f"path:{len(strokes)}", kind="line" if len(pts) == 2 else "curve" if bezier else "polyline",
                    pts=pts, closed=closed or kind == "rect",
                    colour=_rgb(obj.get("stroking_color")) if obj.get("stroke") else None,
                    fill=_rgb(obj.get("non_stroking_color")) if obj.get("fill") else None,
                    width=float(obj.get("linewidth") or 0.0) * scale,
                    source="raster" if raster else "vector"))
        texts = [TextRun(id=t.entity, text=t.text, box=tuple(v * scale for v in t.box), height=t.height * scale,
                         rotation_deg=t.rotation_deg, source="ocr" if raster else "vector")
                 for t in merge_chars(pg.chars)]
        return GenericPage(file=file_rel or str(path), page=page_no,
                           source_kind="raster_scan" if raster else "cad_pdf", units="px" if raster else "pt",
                           units_to_m=None, size=(float(pg.width) * scale, height * scale), strokes=strokes,
                           texts=texts, dpi=dpi)


# --------------------------------------------------------------------------
# Hand-made pages
# --------------------------------------------------------------------------

def line(sid, a, b):
    return Stroke(id=sid, kind="line", pts=[a, b])


def arrow(sid, tip, direction, length=4.0, half=1.0):
    """Filled triangle with its tip at ``tip`` pointing along ``direction``."""
    ux, uy = direction
    bx, by = tip[0] - ux * length, tip[1] - uy * length
    nx, ny = -uy, ux
    return Stroke(id=sid, kind="polyline", pts=[(bx + nx * half, by + ny * half), (bx - nx * half, by - ny * half),
                                                tip, (bx + nx * half, by + ny * half)],
                  closed=True, fill=(1.0, 0.0, 0.0), colour=(1.0, 0.0, 0.0))


def tick(sid, centre, angle_deg=45.0, half=2.0):
    dx, dy = half * math.cos(math.radians(angle_deg)), half * math.sin(math.radians(angle_deg))
    return line(sid, (centre[0] - dx, centre[1] - dy), (centre[0] + dx, centre[1] + dy))


def dot(sid, centre):
    return Stroke(id=sid, kind="line", pts=[centre, centre])


def text(tid, s, centre, rotation=0.0, h=H, source="vector"):
    w = 0.6 * h * len(s)
    if rotation in (90.0, 270.0):
        bx = (centre[0] - h / 2, centre[1] - w / 2, centre[0] + h / 2, centre[1] + w / 2)
    else:
        bx = (centre[0] - w / 2, centre[1] - h / 2, centre[0] + w / 2, centre[1] + h / 2)
    return TextRun(id=tid, text=s, box=bx, height=h, rotation_deg=rotation, source=source)


def page(strokes=(), texts=(), dims=(), **kw):
    args = dict(file="plan.pdf", page=1, source_kind="cad_pdf", units="pt", units_to_m=None, size=(842.0, 595.0))
    args.update(kw)
    return GenericPage(strokes=list(strokes), texts=list(texts), dimensions=list(dims), **args)


def found(pg):
    return [(d.text, round(d.measured_units, 3), d.end_marks) for d in S.find_dimensions(pg)]


# --------------------------------------------------------------------------
# Dimension finder
# --------------------------------------------------------------------------

def test_arrowheads_and_text_in_the_gap_of_a_vertical_line():
    """real01's 30': upright text inside the gap of a vertical line, arrow tips beyond the line ends."""
    pg = page(strokes=[line("l1", (0, 0), (0, 44)), line("l2", (0, 56), (0, 100)),
                       arrow("a1", (0, -4), (0, -1)), arrow("a2", (0, 104), (0, 1)),
                       line("e1", (-8, -4), (8, -4)), line("e2", (-8, 104), (8, 104))],
              texts=[text("t", "30'", (0.2, 50))])
    dims = S.find_dimensions(pg)
    assert [(d.text, d.how, d.end_marks) for d in dims] == [("30'", "gap", ("arrow", "arrow"))]
    d = dims[0]
    assert d.measured_units == pytest.approx(108.0)
    assert d.p1 == pytest.approx((0, -4)) and d.p2 == pytest.approx((0, 104))
    assert d.length.metres == pytest.approx(30 * U.FT) and d.ratio == pytest.approx(30 * U.FT / 108.0)
    assert set(d.stroke_ids) == {"l1", "l2", "a1", "a2"} and d.extension_ids == ["e1", "e2"]
    assert d.text_id == "t"


def test_arrowheads_drawn_inside_the_line():
    pg = page(strokes=[line("l", (0, 0), (100, 0)), arrow("a1", (0, 0), (-1, 0)), arrow("a2", (100, 0), (1, 0))],
              texts=[text("t", "4,30", (50, 7))])
    assert found(pg) == [("4,30", 100.0, ("arrow", "arrow"))]


def test_ticks_parallel_text_and_extension_lines():
    """The synthetic convention: 45-degree ticks at the ends, extension lines through them, text above."""
    pg = page(strokes=[line("l", (0, 0), (100, 0)), tick("k1", (0, 0)), tick("k2", (100, 0)),
                       line("e1", (0, -20), (0, 3)), line("e2", (100, -20), (100, 3))],
              texts=[text("t", "4,30", (50, 7))])
    dims = S.find_dimensions(pg)
    assert [(d.text, d.measured_units, d.end_marks, d.how) for d in dims] == [("4,30", 100.0, ("tick", "tick"),
                                                                                 "parallel")]
    assert set(dims[0].stroke_ids) == {"l", "k1", "k2"} and dims[0].extension_ids == ["e1", "e2"]


def test_dots_and_plain_extension_lines():
    dots = page(strokes=[line("l", (0, 0), (100, 0)), dot("d1", (0, 0)), dot("d2", (100, 0))],
                texts=[text("t", "4,30", (50, 7))])
    assert found(dots) == [("4,30", 100.0, ("dot", "dot"))]
    ext = page(strokes=[line("l", (-5, 0), (105, 0)), line("e1", (-5, -20), (-5, 3)), line("e2", (105, -20), (105, 3))],
               texts=[text("t", "4,30", (50, 7))])
    assert found(ext) == [("4,30", 110.0, ("extension", "extension"))]


def test_a_chain_splits_at_its_ticks():
    pg = page(strokes=[line("l", (0, 0), (100, 0)), tick("k1", (0, 0)), tick("k2", (40, 0)), tick("k3", (100, 0))],
              texts=[text("t1", "4,00", (20, 7)), text("t2", "6,00", (70, 7))])
    assert found(pg) == [("4,00", 40.0, ("tick", "tick")), ("6,00", 60.0, ("tick", "tick"))]


def test_rotated_text_along_a_vertical_line():
    pg = page(strokes=[line("l", (0, 0), (0, 100)), tick("k1", (0, 0)), tick("k2", (0, 100))],
              texts=[text("t", "4,30", (-7, 50), rotation=90.0)])
    assert found(pg) == [("4,30", 100.0, ("tick", "tick"))]


def test_no_dimension_without_end_marks_or_a_length_text():
    bare = page(strokes=[line("l", (0, 0), (100, 0))], texts=[text("t", "4,30", (50, 7))])
    assert S.find_dimensions(bare) == []
    one_end = page(strokes=[line("l", (0, 0), (100, 0)), tick("k1", (0, 0))], texts=[text("t", "4,30", (50, 7))])
    assert S.find_dimensions(one_end) == []
    marked = [line("l", (0, 0), (100, 0)), tick("k1", (0, 0)), tick("k2", (100, 0))]
    assert S.find_dimensions(page(strokes=marked, texts=[text("t", "Bed Room", (50, 7))])) == []
    assert S.find_dimensions(page(strokes=marked, texts=[text("t", "11' x 10'", (50, 7))])) == []
    far = page(strokes=marked, texts=[text("t", "4,30", (50, 30))])                     # 3 x text height away
    assert S.find_dimensions(far) == []
    ai = page(strokes=marked, texts=[text("t", "4,30", (50, 7), source="ai")])          # VLM texts never count
    assert S.find_dimensions(ai) == []


def test_a_hatch_crossing_the_line_is_no_tick():
    comb = [tick(f"h{i}", (float(i), 0.0)) for i in range(0, 6)] + \
           [tick(f"g{i}", (100.0 - i, 0.0)) for i in range(0, 6)]
    pg = page(strokes=[line("l", (0, 0), (100, 0))] + comb, texts=[text("t", "4,30", (50, 7))])
    assert S.find_dimensions(pg) == []


def test_one_line_one_text():
    """Two texts near one marked line: the nearer one takes it."""
    pg = page(strokes=[line("l", (0, 0), (100, 0)), tick("k1", (0, 0)), tick("k2", (100, 0))],
              texts=[text("far", "4,30", (50, 20)), text("near", "4,30", (50, 7))])
    dims = S.find_dimensions(pg)
    assert [d.text_id for d in dims] == ["near"]


def test_dxf_dimension_entities():
    prims = [DimensionPrim(id="DIM:1", p1=(0, 0), p2=(168, 0), measured_units=168.0, text="14'-0\""),
             DimensionPrim(id="DIM:2", p1=(0, 0), p2=(144, 0), measured_units=144.0, text=None),
             DimensionPrim(id="DIM:3", p1=(0, 0), p2=(144, 0), measured_units=144.0, text="<> TYP"),
             DimensionPrim(id="DIM:4", p1=(0, 0), p2=(0, 0), measured_units=0.0, text="1'")]
    dims = S.find_dimensions(page(dims=prims, source_kind="dxf", units="dxf"))
    assert [(d.text, d.how, d.end_marks, d.stroke_ids) for d in dims] == [
        ("14'-0\"", "dimension_entity", ("dimension", "dimension"), ["DIM:1"])]
    assert dims[0].ratio == pytest.approx(U.INCH)


def test_bare_numbers_on_an_imperial_page_are_feet():
    pg = page(strokes=[line("l", (0, 0), (100, 0)), tick("k1", (0, 0)), tick("k2", (100, 0))],
              texts=[text("t", "12", (50, 7)), text("x", "50'", (400, 400)), text("y", "30'", (400, 300))])
    dims = S.find_dimensions(pg)
    assert len(dims) == 1 and dims[0].length.system == "imperial"
    assert dims[0].length.metres == pytest.approx(12 * U.FT)


# --------------------------------------------------------------------------
# real01 and the synthetic PDFs
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real01():
    return pdf_page(REAL01, 1, "projects/real01/real01.pdf")


@pytest.fixture(scope="module")
def real01_dims(real01):
    return S.find_dimensions(real01)


@pytest.fixture(scope="module")
def reference():
    return yaml.safe_load(REFERENCE.read_text(encoding="utf-8"))


def test_real01_two_dimensions(real01_dims):
    by_text = {d.text: d for d in real01_dims}
    assert sorted(by_text) == ["30'", "50'"]
    assert by_text["50'"].measured_units == pytest.approx(621.72, abs=0.01)
    assert by_text["30'"].measured_units == pytest.approx(373.08, abs=0.01)
    assert by_text["50'"].p1 == pytest.approx((128.44, 501.88), abs=0.01)
    assert by_text["30'"].p1 == pytest.approx((91.84, 97.84), abs=0.01)
    for d in real01_dims:
        assert d.how == "gap" and d.end_marks == ("arrow", "arrow")
        assert len(d.stroke_ids) == 4 and len(d.extension_ids) == 2


def _real01_faces(reference, blocks, mpu, labelled=True):
    """Reference room boxes (feet) as faces in page metres at ``mpu``, each with the block whose anchor it holds."""
    s = reference["scale"]["pt_per_ft"]
    y0 = reference["source"]["page_size_pt"][1] - 459.84
    faces = []
    for room in reference["rooms"]:
        x_lo, y_lo, x_hi, y_hi = room["bbox_ft"]
        face = box((165.64 + x_lo * s) * mpu, (y0 + y_lo * s) * mpu, (165.64 + x_hi * s) * mpu, (y0 + y_hi * s) * mpu)
        holder = [b for b in blocks if face.contains(Point(b.anchor))]
        faces.append((face, holder[0] if holder and labelled else None))
    return faces


def test_real01_scale_is_provisional_then_confirmed_by_the_size_labels(real01, real01_dims, reference):
    scale, reasons = S.provisional_scale(real01, real01_dims)
    assert scale["provisional"] == "two_dimensions" and scale["method"] == "dimension_text"
    pt_per_ft = U.FT / scale["metres_per_unit"]
    assert pt_per_ft == pytest.approx(reference["scale"]["pt_per_ft"], rel=reference["scale"]["tol"]["rel"])
    assert scale["metres_per_unit"] == pytest.approx(reference["scale"]["m_per_pt"], rel=1e-4)
    assert "provisional scale from 2 dimension texts" in reasons[-1]
    mpu = scale["metres_per_unit"]
    texts_m = [TextRun(id=t.id, text=t.text, box=tuple(v * mpu for v in t.box), height=t.height * mpu,
                       rotation_deg=t.rotation_deg) for t in real01.texts]
    blocks = L.merge_label_blocks(texts_m, real01.file, 1)
    confirmed, conflicts, warnings = S.confirm_scale(scale, real01_dims, blocks, _real01_faces(reference, blocks, mpu))
    assert confirmed["confidence"] == 0.85 and "provisional" not in confirmed
    assert confirmed["metres_per_unit"] == mpu and confirmed["evidence"]["confidence"] == 0.85
    assert confirmed["evidence"]["file"] == "projects/real01/real01.pdf" and confirmed["evidence"]["page"] == 1
    assert conflicts == []
    assert warnings == ["scale from 2 dimensions, corroborated by 8 room sizes"]
    # Without the size labels the two dimensions are not enough.
    none, conflicts, warnings = S.confirm_scale(scale, real01_dims, blocks,
                                                _real01_faces(reference, blocks, mpu, labelled=False))
    assert none is None and conflicts == []
    assert warnings[-1].startswith("scale not corroborated: 0 of 0 room-size labels")
    assert "'30''" in warnings[-1] and "'50''" in warnings[-1]


def _truth_pages(project):
    pages = json.loads((ROOT / "projects" / project / "truth" / "pages.json").read_text(encoding="utf-8"))["pages"]
    return [p for p in pages if p["kind"] == "vector" and p["file"].endswith(".pdf")]


SYNTHETIC_PDF_PAGES = [(name, p["file"], p["page"]) for name in ("synthetic-01", "synthetic-02", "synthetic-03",
                                                                  "synthetic-04") for p in _truth_pages(name)]


@pytest.mark.parametrize("project, file, page_no", SYNTHETIC_PDF_PAGES)
def test_synthetic_pdf_pages_keep_their_scale(project, file, page_no):
    """The synthetic PDFs give the same scale as pdf_extract (note confirmed by the ticked dimensions,
    confidence 1.0) and the dimensions of the truth with the same measured lengths."""
    truth = [p for p in _truth_pages(project) if p["file"] == file and p["page"] == page_no][0]
    pg = pdf_page(ROOT / "projects" / project / file, page_no, file)
    dims = S.find_dimensions(pg)
    scale, reasons = S.provisional_scale(pg, dims)
    assert scale["method"] == "pdf_scale_text" and scale["confidence"] == 1.0
    assert scale["metres_per_unit"] == pytest.approx(truth["scale_metres_per_unit"], rel=1e-12)
    assert "provisional" not in scale and "confirmed by" in reasons[-1]
    got = sorted((d.text, round(d.measured_units * scale["metres_per_unit"], 3)) for d in dims)
    assert got == sorted((d["printed"], round(d["measured"], 3)) for d in truth["dimensions"])
    assert all(d.end_marks == ("tick", "tick") for d in dims)
    final, conflicts, _ = S.confirm_scale(scale, dims, [], [])
    assert final == scale
    # The new rule: every dimension text off the scale by more than 1 % is listed (synthetic-03's 3,99).
    off = [d["printed"] for d in truth["dimensions"]
           if abs(U.parse_length(d["printed"]).metres - d["measured"]) / d["measured"] > 0.01]
    assert [c["kind"] for c in conflicts] == ["scale_disagreement"] * len(off)
    assert all(any(f"'{t}'" in c["description"] for c in conflicts) for t in off)


def test_synthetic_02_scan_does_not_take_the_scale_note():
    """§0/§2.3: a raster page's scale note counts only with a verified pixel size and never against the
    dimensions. The page is synthetic-02's plan as the 150 dpi scan sees it (its vector source in pixel units,
    texts as OCR read them, incl. 'ÖLÇEK 1/100'); the scan PNG carries no dpi."""
    px = 150.0 / 72.0
    truth_mpu = 0.016933333333333335            # truth/pages.json: plan_scan.png at 150 dpi
    unknown = pdf_page(ROOT / "projects" / "synthetic-02" / "truth" / "plan.pdf", 1, "plan_scan.png", scale=px,
                       raster=True, dpi=None)
    assert any(S.note_ratio(t.text) == 100 for t in unknown.texts)
    dims = S.find_dimensions(unknown)
    assert len(dims) == 6
    scale, reasons = S.provisional_scale(unknown, dims)
    assert scale["method"] == "dimension_text" and scale["confidence"] == 0.9
    assert scale["metres_per_unit"] == pytest.approx(truth_mpu, rel=2e-3)
    assert scale["evidence"]["method"] == "ocr"
    assert any("ignored: raster page without a verified pixel size" in r for r in reasons)
    # With a verified pixel size the note counts ...
    verified = pdf_page(ROOT / "projects" / "synthetic-02" / "truth" / "plan.pdf", 1, "plan_scan.png", scale=px,
                        raster=True, dpi=150.0)
    scale, _ = S.provisional_scale(verified, S.find_dimensions(verified))
    assert scale["method"] == "pdf_scale_text" and scale["confidence"] == 1.0
    assert scale["metres_per_unit"] == pytest.approx(truth_mpu, rel=1e-9)
    # ... but never against the dimensions (a wrong pixel size).
    wrong = pdf_page(ROOT / "projects" / "synthetic-02" / "truth" / "plan.pdf", 1, "plan_scan.png", scale=px,
                     raster=True, dpi=300.0)
    scale, reasons = S.provisional_scale(wrong, S.find_dimensions(wrong))
    assert scale["method"] == "dimension_text"
    assert scale["metres_per_unit"] == pytest.approx(truth_mpu, rel=2e-3)
    assert any("never counts against the dimensions" in r for r in reasons)


# --------------------------------------------------------------------------
# Scale rules on given dimensions
# --------------------------------------------------------------------------

def dim(printed, measured_units, tid=None, source="vector"):
    return S.DimCandidate(text=printed, length=U.parse_length(printed), p1=(0.0, 0.0), p2=(measured_units, 0.0),
                          measured_units=measured_units, end_marks=("tick", "tick"), stroke_ids=[],
                          text_id=tid or f"char:{printed}", source=source)


MPU = 100 * METRES_PER_POINT      # 1:100 on a PDF page


def at(metres, off=0.0):
    """A dimension whose line measures ``metres`` at 1:100, printed ``off`` relative too long."""
    return dim(f"{metres * (1 + off):.2f}".replace(".", ","), metres / MPU)


def test_scale_note_rules_on_a_vector_page():
    note = [text("n", "ÖLÇEK 1/100", (700, 50))]
    scale, reasons = S.provisional_scale(page(texts=note), [])
    assert (scale["method"], scale["confidence"]) == ("pdf_scale_text", 0.9)
    assert scale["metres_per_unit"] == pytest.approx(MPU) and scale["evidence"]["text"] == "ÖLÇEK 1/100"
    scale, _ = S.provisional_scale(page(texts=note), [at(4.3), at(1.7), at(3.6)])
    assert scale["confidence"] == 1.0
    scale, reasons = S.provisional_scale(page(texts=note), [at(4.3, 0.2), at(1.7, 0.2), at(3.6, 0.2)])
    assert scale["confidence"] == 0.5 and scale["method"] == "pdf_scale_text" and "scale note kept" in reasons[-1]
    final, conflicts, _ = S.confirm_scale(scale, [at(4.3, 0.2), at(1.7, 0.2), at(3.6, 0.2)], [], [])
    assert final["confidence"] == 0.5 and len(conflicts) == 3


def test_scale_notes_english_and_imperial():
    assert S.note_ratio("SCALE 1:50") == 50
    assert S.note_ratio("SCALE: 1/100") == 100
    assert S.note_ratio("SCALE 1/4\" = 1'-0\"") == pytest.approx(48)
    assert S.note_ratio("1/8\" = 1'-0\"") == pytest.approx(96)
    assert S.note_ratio("1\" = 10'") == pytest.approx(120)
    assert S.note_ratio("SCALE: 1/4\" = 1'-0\" (A3)") == pytest.approx(48)   # never 1:4
    assert S.note_ratio("1 inch = 20 feet") == pytest.approx(240)
    assert S.note_ratio("SCALE 1/4\" = ?") is None
    assert S.note_ratio("Bed Room") is None and S.note_ratio("11' x 10'") is None
    scale, _ = S.provisional_scale(page(texts=[text("n", "SCALE 1/4\" = 1'-0\"", (700, 50))]), [])
    assert scale["metres_per_unit"] == pytest.approx(48 * METRES_PER_POINT)


def test_several_different_scale_notes_are_not_used():
    texts = [text("n1", "ÖLÇEK 1/100", (700, 50)), text("n2", "ÖLÇEK 1/50", (700, 80))]
    scale, reasons = S.provisional_scale(page(texts=texts), [at(4.3), at(1.7), at(3.6)])
    assert scale["method"] == "dimension_text" and "several different scale notes" in reasons[0]


def test_three_agreeing_dimensions():
    scale, reasons = S.provisional_scale(page(), [at(4.3), at(1.7), at(3.6)])
    assert (scale["method"], scale["confidence"]) == ("dimension_text", 0.9) and "provisional" not in scale
    assert scale["metres_per_unit"] == pytest.approx(MPU, rel=1e-3)
    dims = [at(4.3), at(1.7), at(3.6), at(2.0, 0.05)]
    scale, reasons = S.provisional_scale(page(), dims)
    assert scale["confidence"] == 0.7 and "disagreeing" in reasons[-1]
    final, conflicts, _ = S.confirm_scale(scale, dims, [], [])
    assert final == scale
    assert [c["kind"] for c in conflicts] == ["scale_disagreement"] and "'2,10'" in conflicts[0]["description"]
    # Three that agree but are no majority: no scale.
    split = [at(4.3), at(1.7), at(3.6), at(2.0, -0.1), at(2.5, -0.2), at(3.0, 0.1), at(3.2, 0.2)]
    scale, reasons = S.provisional_scale(page(), split)
    assert scale is None and "not the majority" in reasons[-1]


def _size_faces(n_agree, n_off=0, off=0.08):
    """(face in page metres, block) pairs: rooms 4 x 3 m whose labels agree, or are ``off`` too large."""
    faces = []
    for i in range(n_agree + n_off):
        k = 1.0 + (off if i >= n_agree else 0.0)
        runs = [TextRun(id=f"n{i}", text="Bed Room", box=(10 * i, 1.0, 10 * i + 1.5, 1.2), height=0.2),
                TextRun(id=f"s{i}", text=f"{4 * k:.2f} x {3 * k:.2f}".replace(".", ","),
                        box=(10 * i, 0.75, 10 * i + 1.5, 0.95), height=0.2)]
        block = L.merge_label_blocks(runs)[0]
        faces.append((box(10 * i - 1.0, -1.0, 10 * i + 3.0, 2.0), block))
    return faces


def test_two_dimensions_need_two_size_labels():
    dims = [at(9.60), at(4.30, 0.003)]
    scale, reasons = S.provisional_scale(page(), dims)
    assert scale["provisional"] == "two_dimensions" and scale["confidence"] == 0.85
    assert scale["metres_per_unit"] == pytest.approx((dims[0].ratio + dims[1].ratio) / 2)
    blocks = [b for _, b in _size_faces(2)]
    final, conflicts, warnings = S.confirm_scale(scale, dims, blocks, _size_faces(2))
    assert final["confidence"] == 0.85 and "provisional" not in final and conflicts == []
    assert warnings == ["scale from 2 dimensions, corroborated by 2 room sizes"]
    final, _, warnings = S.confirm_scale(scale, dims, blocks, _size_faces(1, n_off=3))
    assert final is None and warnings[-1].startswith("scale not corroborated: 1 of 4 room-size labels")
    # Two dimensions 0.8 % apart are no provisional scale.
    scale, reasons = S.provisional_scale(page(), [at(9.60), at(4.30, 0.008)])
    assert scale is None and "do not agree" in reasons[-1]
    # Two agreeing and one odd: the pair is the majority; the odd one becomes a conflict.
    dims = [at(9.60), at(4.30, 0.002), at(3.00, 0.04)]
    scale, _ = S.provisional_scale(page(), dims)
    assert scale["provisional"] == "two_dimensions"
    final, conflicts, _ = S.confirm_scale(scale, dims, [], _size_faces(3))
    assert final is not None and len(conflicts) == 1 and "'3,12'" in conflicts[0]["description"]


def test_one_dimension_needs_three_size_labels():
    dims = [at(9.60)]
    scale, _ = S.provisional_scale(page(), dims)
    assert scale["provisional"] == "one_dimension"
    final, _, warnings = S.confirm_scale(scale, dims, [], _size_faces(3, n_off=1))
    assert final["confidence"] == 0.7 and "provisional" not in final
    assert "scale from one dimension, corroborated by 3 room sizes" in warnings
    assert any("1 of 4 room-size labels differ" in w for w in warnings)
    final, _, warnings = S.confirm_scale(scale, dims, [], _size_faces(2))
    assert final is None and "need 3" in warnings[-1]


def test_size_labels_alone_never_give_a_scale():
    scale, reasons = S.provisional_scale(page(), [])
    assert scale is None and "no dimension text" in reasons[-1]
    assert S.confirm_scale(None, [], [], _size_faces(5)) == (None, [], [])


def test_non_rectangular_faces_do_not_corroborate():
    from shapely.geometry import Polygon
    runs = [TextRun(id="n", text="Bed Room", box=(0, 1.0, 1.5, 1.2), height=0.2),
            TextRun(id="s", text="4,00 x 3,00", box=(0, 0.75, 1.5, 0.95), height=0.2)]
    block = L.merge_label_blocks(runs)[0]
    l_face = Polygon([(0, 0), (4, 0), (4, 1.5), (2, 1.5), (2, 3), (0, 3)])
    scale, _ = S.provisional_scale(page(), [at(9.60), at(4.30)])
    final, _, warnings = S.confirm_scale(scale, [], [block], [(l_face, block), (l_face, block)])
    assert final is None and "0 of 0 room-size labels" in warnings[-1]


def test_dxf_units_are_the_scale_and_dimensions_are_checked():
    prims = [DimensionPrim(id="DIM:1", p1=(0, 0), p2=(168, 0), measured_units=168.0, text="14'-0\""),
             DimensionPrim(id="DIM:2", p1=(0, 0), p2=(150, 0), measured_units=150.0, text="12'-0\"")]
    pg = page(dims=prims, source_kind="dxf", units="dxf", units_to_m=U.INCH,
              texts=[text("n", "SCALE 1:50", (0, 0))])
    dims = S.find_dimensions(pg)
    scale, _ = S.provisional_scale(pg, dims)
    assert (scale["method"], scale["confidence"], scale["metres_per_unit"]) == ("dxf_insunits", 1.0, U.INCH)
    assert "page" not in scale["evidence"]
    final, conflicts, _ = S.confirm_scale(scale, dims, [], [])
    assert final == scale and len(conflicts) == 1 and "'12'-0\"'" in conflicts[0]["description"]
    # Unitless DXF ($INSUNITS 0): the dimension rules decide; a note says nothing about drawing units.
    unitless = page(dims=prims[:1], source_kind="dxf", units="dxf", units_to_m=None,
                    texts=[text("n", "SCALE 1:50", (0, 0))])
    scale, _ = S.provisional_scale(unitless, S.find_dimensions(unitless))
    assert scale["provisional"] == "one_dimension" and scale["metres_per_unit"] == pytest.approx(U.INCH)


def test_ocr_dimensions_give_ocr_evidence_on_raster_pages():
    ev = {"file": "scan.png", "method": "ocr", "confidence": 0.93, "model": "tesseract", "pixel_box": [1, 2, 3, 4]}
    strokes, texts = [], []
    for i, (printed, y) in enumerate((("4,30", 0.0), ("1,70", 100.0), ("3,60", 200.0))):
        length = U.parse_length(printed).metres / (100 * 0.0254 / 150)      # px at 1:100, 150 dpi
        strokes += [line(f"l{i}", (0, y), (length, y)), tick(f"a{i}", (0, y)), tick(f"b{i}", (length, y))]
        texts.append(TextRun(id=f"ocr:{i}", text=printed, box=(length / 2 - 12, y + 2, length / 2 + 12, y + 12),
                             height=10.0, source="ocr", evidence=[dict(ev)]))
    texts.append(TextRun(id="ocr:n", text="ÖLÇEK 1/100", box=(500, 500, 560, 510), height=10.0, source="ocr"))
    pg = page(strokes=strokes, texts=texts, file="scan.png", source_kind="raster_scan", units="px", dpi=None)
    dims = S.find_dimensions(pg)
    assert len(dims) == 3 and all(d.source == "ocr" for d in dims)
    scale, _ = S.provisional_scale(pg, dims)
    assert scale["method"] == "dimension_text" and scale["metres_per_unit"] == pytest.approx(100 * 0.0254 / 150)
    assert scale["evidence"]["method"] == "ocr" and scale["evidence"]["model"] == "tesseract"
    assert scale["evidence"]["pixel_box"] == [1, 2, 3, 4] and scale["evidence"]["confidence"] == 0.9


def test_a_label_corroborates_once():
    faces = _size_faces(1)
    scale, _ = S.provisional_scale(page(), [at(9.60), at(4.30)])
    final, _, warnings = S.confirm_scale(scale, [], [], faces + faces)
    assert final is None and "1 of 1 room-size labels" in warnings[-1]


# --------------------------------------------------------------------------
# Bare integer dimension texts on metric pages (review2 ingest-7)
# --------------------------------------------------------------------------

def _bare_page(printed_units, h=H, size=(842.0, 595.0), labels=()):
    """Horizontal ticked dimension lines, one per (printed text, measured page units), text above the line."""
    strokes, texts = [], []
    for i, (printed, units_long) in enumerate(printed_units):
        y = 60.0 * i
        strokes += [line(f"l{i}", (0, y), (units_long, y)), tick(f"a{i}", (0, y)), tick(f"b{i}", (units_long, y))]
        texts.append(text(f"t{i}", printed, (units_long / 2, y + 7), h=h))
    return page(strokes=strokes, texts=texts + list(labels), size=size)


def _bare_faces(size_texts):
    """Rooms 4 x 3 m (page metres) whose size labels are written as given."""
    faces = []
    for i, size_text in enumerate(size_texts):
        runs = [TextRun(id=f"n{i}", text="Bed Room", box=(10 * i, 1.0, 10 * i + 1.5, 1.2), height=0.2),
                TextRun(id=f"s{i}", text=size_text, box=(10 * i, 0.75, 10 * i + 1.5, 0.95), height=0.2)]
        block = L.merge_label_blocks(runs)[0]
        faces.append((box(10 * i - 1.0, -1.0, 10 * i + 3.0, 2.0), block))
    return faces


@pytest.mark.parametrize("unit, factor", [("mm", 1000), ("cm", 100)])
def test_bare_integer_dimensions_are_read_in_the_one_plausible_unit(unit, factor):
    """'9600' / '4300' (or '960' / '430') on a 1:100 metric page: read as metres the drawing would be kilometres wide
    with 350 m (or 35 m) tall text; only mm (or cm) gives a plausible page, so that unit is taken, as assumed."""
    pg = _bare_page([(f"{round(9.6 * factor)}", 9.6 / MPU), (f"{round(4.3 * factor)}", 4.3 / MPU)])
    dims = S.find_dimensions(pg)
    assert [d.text for d in dims] == [f"{round(9.6 * factor)}", f"{round(4.3 * factor)}"]
    assert [d.unit_assumed for d in dims] == [unit, unit]
    assert [d.length.metres for d in dims] == pytest.approx([9.6, 4.3])
    assert all(f"read as {unit} (assumed" in d.unit_note for d in dims)
    scale, reasons = S.provisional_scale(pg, dims)
    assert scale["provisional"] == "two_dimensions" and scale["metres_per_unit"] == pytest.approx(MPU, rel=1e-3)
    assert scale["unit_assumed"] == unit and "assumed" in scale["evidence"]["note"]
    assert f"read as {unit} (assumed" in reasons[0]
    # The size labels (in metres, or bare integers in the same unit) corroborate it.
    for labels in (["4,00 x 3,00"] * 2, [f"{4 * factor} x {3 * factor}"] * 2):
        faces = _bare_faces(labels)
        final, conflicts, warnings = S.confirm_scale(scale, dims, [b for _, b in faces], faces)
        assert final is not None and final["unit_assumed"] == unit and conflicts == []
        assert any(f"bare integers read in {unit} (assumed unit" in w for w in warnings)
        assert faces[0][1].size[0].metres == pytest.approx(4.0)


def test_bare_integer_dimensions_with_an_unclear_unit_name_the_problem():
    # 5 m per page unit as metres: 50 m tall text and a 4.8 km drawing; as cm 0.5 m / 48 m, as mm 0.05 m / 4.8 m:
    # both fit, the unit cannot be told, the metres stay and the reasons say why.
    pg = _bare_page([("4800", 960.0), ("2400", 480.0)], size=(1200.0, 800.0))
    dims = S.find_dimensions(pg)
    assert [d.unit_assumed for d in dims] == [None, None]
    assert all("likely a unit problem" in d.unit_note and "cm or mm would fit" in d.unit_note for d in dims)
    scale, reasons = S.provisional_scale(pg, dims)
    assert scale["metres_per_unit"] == pytest.approx(5.0) and "unit_assumed" not in scale
    assert "likely a unit problem" in reasons[0]
    final, _, warnings = S.confirm_scale(scale, dims, [], [])
    assert final is None and warnings[-1].startswith("scale not corroborated")
    assert "likely a unit problem" in warnings[-1]
    # A metre reading that fits the page is kept without a note ('12' on a 1:100 page: 0.35 m text).
    plain = _bare_page([("12", 12 / MPU), ("6", 6 / MPU)])
    dims = S.find_dimensions(plain)
    assert [(d.unit_assumed, d.unit_note) for d in dims] == [(None, None), (None, None)]
    assert [d.length.metres for d in dims] == [12.0, 6.0]
    # Dimension texts with a unit or a decimal are never re-read.
    explicit = _bare_page([("9600 mm", 9.6 / MPU), ("4,30", 4.3 / MPU)])
    assert [d.unit_assumed for d in S.find_dimensions(explicit)] == [None, None]
