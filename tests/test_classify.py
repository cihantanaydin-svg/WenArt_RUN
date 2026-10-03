"""Page classification (wenart/ingest/classify.py) on the synthetic projects."""
import json
import shutil
from pathlib import Path

import pytest

from wenart import building as B
from wenart.ingest import classify as C
from wenart.ingest import dwg as dwg_mod
from wenart.ingest.model import METRES_PER_POINT, page_class_for, parse_number, parse_scale_text, text_role

from conftest import PROJECTS

FIXTURES_06_TITLED = Path(__file__).parent / "fixtures" / "synthetic-06-titled"


def by_page(records):
    return {(r.file, r.page): r for r in records}


def test_synthetic_01_pages():
    recs = by_page(C.classify_pages(PROJECTS / "synthetic-01"))
    assert set(recs) == {("zemin_kat.dxf", 1), ("1_kat.pdf", 1), ("1_kat_scan.png", 1)}
    dxf = recs[("zemin_kat.dxf", 1)]
    assert (dxf.format, dxf.kind, dxf.page_class, dxf.level_id, dxf.level_label) == ("dxf", "vector", "floor_plan", "L0", "Zemin Kat")
    assert dxf.level_label_raw == "ZEMİN KAT PLANI" and dxf.confidence == 1.0 and dxf.skip_reason is None
    assert dxf.scale["method"] == "dxf_insunits" and dxf.scale["metres_per_unit"] == 0.001
    assert dxf.scale["evidence"]["entity"] == "$INSUNITS=4"
    assert dxf.evidence[0]["text"] == "ZEMİN KAT PLANI" and dxf.evidence[0]["entity"].startswith("TEXT:")
    pdf = recs[("1_kat.pdf", 1)]
    assert (pdf.format, pdf.kind, pdf.page_class, pdf.level_id, pdf.level_order) == ("pdf", "vector", "floor_plan", "L1", 1)
    assert pdf.scale["method"] == "pdf_scale_text"
    assert pdf.scale["metres_per_unit"] == pytest.approx(100 * METRES_PER_POINT)
    assert pdf.evidence[0]["page"] == 1 and pdf.evidence[0]["entity"].startswith("char:")
    # Milestone 7 (§4.1): the scan's title is read by OCR (Tesseract) and the page goes to the raster adapter.
    scan = recs[("1_kat_scan.png", 1)]
    assert (scan.format, scan.kind, scan.page_class, scan.level_id) == ("image", "scan", "floor_plan", "L1")
    assert scan.skip_reason is None and scan.classifier == "ocr" and scan.extractor == "raster"
    assert scan.evidence[0]["method"] == "ocr" and scan.evidence[0]["text"] == "1. KAT PLANI"
    assert scan.confidence <= C.RASTER_TITLE_MAX_CONFIDENCE and scan.scale is None
    assert scan.is_extractable() and dxf.is_extractable() and pdf.is_extractable()


def test_synthetic_02_raster_kinds():
    recs = by_page(C.classify_pages(PROJECTS / "synthetic-02"))
    assert recs[("plan_scan.png", 1)].kind == "scan"
    assert recs[("plan_photo.jpg", 1)].kind == "photo"
    # Milestone 7: both pages are floor plans by their OCR title; the scan/photo decision is image processing.
    for rec in recs.values():
        assert rec.page_class == "floor_plan" and rec.skip_reason is None and rec.level_id == "L0"
        assert rec.evidence[0]["method"] == "ocr"
        assert rec.evidence[-1]["method"] == "raster" and rec.evidence[-1]["text"].startswith("kind: ")


def test_synthetic_03_pages():
    recs = by_page(C.classify_pages(PROJECTS / "synthetic-03"))
    assert [recs[("kat_planlari.pdf", p)].level_id for p in (1, 2, 3)] == ["L-1", "L0", "L1"]
    assert all(recs[("kat_planlari.pdf", p)].page_class == "floor_plan" for p in (1, 2, 3))
    assert recs[("kat_planlari.pdf", 1)].level_label == "Bodrum Kat"
    dxf = recs[("mobilya_plani.dxf", 1)]
    assert dxf.page_class == "furniture_plan" and dxf.level_id == "L0"
    assert dxf.level_label_raw == "ZEMİN KAT MOBİLYA PLANI"


def test_raster_kind_detection():
    assert C.raster_kind(PROJECTS / "synthetic-02" / "plan_scan.png")[0] == "scan"
    assert C.raster_kind(PROJECTS / "synthetic-01" / "1_kat_scan.png")[0] == "scan"
    kind, reason = C.raster_kind(PROJECTS / "synthetic-02" / "plan_photo.jpg")
    assert kind == "photo" and "quadrilateral" in reason


def test_text_helpers():
    assert parse_scale_text("ÖLÇEK 1/100") == 100
    assert parse_scale_text("OLCEK 1:50") == 50
    assert parse_scale_text("SALON") is None
    assert parse_number("3,45") == 3.45 and parse_number("3.45") == 3.45
    assert parse_number("345 cm") == pytest.approx(3.45) and parse_number("SALON") is None
    assert page_class_for("ZEMİN KAT PLANI") == "floor_plan"
    assert page_class_for("ZEMİN KAT MOBİLYA PLANI") == "furniture_plan"
    assert page_class_for("A-A KESİTİ") == "section"
    assert page_class_for("KUZEY GÖRÜNÜŞÜ") == "elevation"
    assert page_class_for("VAZİYET PLANI") == "site_plan"
    assert page_class_for("YATAK ODASI") is None
    assert text_role("ÖLÇEK 1/100") == "scale" and text_role("3,45") == "dimension"
    assert text_role("1. KAT PLANI") == "title" and text_role("SALON 24,50 m²") == "room_label"


def test_classify_texts_prefers_keyword_title():
    from wenart.ingest.model import TextItem
    texts = [TextItem("YATAK ODASI", (0, 0), [0, 0, 1, 1], 0, "TEXT:1", 200, role="room_label"),
             TextItem("ZEMİN KAT", (0, 0), [0, 0, 1, 1], 0, "TEXT:2", 300, role="title"),
             TextItem("ZEMİN KAT PLANI", (0, 0), [0, 0, 1, 1], 0, "TEXT:3", 500, role="title")]
    page_class, title, confidence = C.classify_texts(texts)
    assert page_class == "floor_plan" and title.entity == "TEXT:3" and confidence == 1.0
    page_class, title, confidence = C.classify_texts(texts[:2])
    assert page_class == "floor_plan" and title.entity == "TEXT:2" and confidence == 0.7
    assert C.classify_texts(texts[:1])[0] == "other"


def test_dwg_without_converter(tmp_path, monkeypatch):
    project = tmp_path / "p"
    project.mkdir()
    (project / "plan.dwg").write_bytes(b"AC1024" + b"\0" * 64)
    monkeypatch.setattr(dwg_mod, "available_converters", lambda: [])
    with pytest.raises(dwg_mod.ConverterNotFound, match="dwg2dxf"):
        dwg_mod.dwg_to_dxf(project / "plan.dwg", tmp_path / "work")
    recs = C.classify_pages(project, work_dir=tmp_path / "work")
    assert len(recs) == 1
    rec = recs[0]
    assert rec.format == "dwg" and rec.page_class == "other" and not rec.is_extractable()
    assert "DWG conversion failed" in rec.skip_reason and "dwg2dxf" in rec.skip_reason


HAS_LIBREDWG = dwg_mod.find_tool("dwg2dxf") is not None and dwg_mod.find_tool("dxf2dwg") is not None
HAS_GENERIC_CORE = (Path(C.__file__).parent / "generic" / "core.py").is_file()


@pytest.mark.skipif(not HAS_LIBREDWG, reason="LibreDWG 0.14 (dwg2dxf, dxf2dwg) not built here (scripts/cloud-setup.sh)")
def test_dwg_round_trip(tmp_path):
    import math
    import ezdxf
    src = PROJECTS / "synthetic-01" / "zemin_kat.dxf"
    # LibreDWG 0.14's dxf2dwg stops at an MTEXT rotation angle (the dimension blocks of the synthetic DXFs have
    # upright texts): a copy with the direction vector instead, as wenart.synthetic.dxf_writer.write_cad_dxf writes.
    doc = ezdxf.readfile(str(src))
    for blk in doc.blocks:
        for e in blk:
            if e.dxftype() == "MTEXT" and e.dxf.hasattr("rotation"):
                angle = math.radians(e.dxf.rotation)
                e.dxf.discard("rotation")
                e.dxf.text_direction = (math.cos(angle), math.sin(angle), 0.0)
    ready = tmp_path / "zemin_kat_ready.dxf"
    doc.saveas(ready)
    dwg = dwg_mod.dxf_to_dwg(ready, tmp_path / "zemin_kat.dwg")
    dxf_path, converter = dwg_mod.dwg_to_dxf(dwg, tmp_path / "work")
    assert dxf_path.is_file() and converter.startswith("libredwg dwg2dxf ") and "audit: 0 errors" in converter
    original = ezdxf.readfile(str(src)).modelspace()
    converted = ezdxf.readfile(str(dxf_path)).modelspace()
    for dxftype in ("LWPOLYLINE", "INSERT", "TEXT", "DIMENSION"):
        assert len(original.query(dxftype)) == len(converted.query(dxftype)), dxftype


@pytest.mark.skipif(not (HAS_LIBREDWG and HAS_GENERIC_CORE), reason="needs LibreDWG and the generic core (G3)")
def test_untitled_dwg_is_a_floor_plan_by_its_room_labels(tmp_path):
    rec = C.classify_pages(PROJECTS / "synthetic-06", work_dir=tmp_path / "work")[0]
    assert (rec.file, rec.format, rec.kind, rec.page_class) == ("synthetic-06.dwg", "dwg", "vector", "floor_plan")
    assert rec.confidence == 0.6 and getattr(rec, "classifier", None) == "generic_labels" and rec.skip_reason is None
    assert rec.converter.startswith("libredwg dwg2dxf 0.14 d9468ae")
    assert rec.scale["method"] == "dxf_insunits" and rec.scale["metres_per_unit"] == 0.0254


@pytest.mark.skipif(not (HAS_LIBREDWG and HAS_GENERIC_CORE), reason="needs LibreDWG and the generic core (G3)")
def test_same_stem_dxf_wins_over_the_dwg(tmp_path):
    """docs/milestone7.md §2.1: in any project a DWG next to a DXF of the same stem is recorded, not read, and is
    not a review reason."""
    project = tmp_path / "p"
    project.mkdir()
    shutil.copyfile(PROJECTS / "synthetic-06" / "synthetic-06.dwg", project / "plan.dwg")
    shutil.copyfile(PROJECTS / "synthetic-06" / "source" / "synthetic-06.dxf", project / "plan.dxf")
    recs = {r.format: r for r in C.classify_pages(project, work_dir=tmp_path / "work")}
    assert recs["dwg"].skip_reason == "DXF of the same name is used" and not recs["dwg"].is_extractable()
    assert recs["dxf"].skip_reason is None and recs["dxf"].page_class == "floor_plan"
    from wenart.ingest.pipeline import build_project
    building = build_project(project, tmp_path / "out")
    assert not any("plan.dwg" in w and w.startswith("needs review") for w in building["warnings"])


def test_ocr_hook_classifies_raster_pages():
    def fake_ocr(path: Path):
        return [{"text": "ZEMİN KAT PLANI", "box": [100, 50, 400, 80], "confidence": 0.9},
                {"text": "ÖLÇEK 1/100", "box": [500, 50, 600, 80], "confidence": 0.9}]

    recs = by_page(C.classify_pages(PROJECTS / "synthetic-02", ocr=fake_ocr))
    scan = recs[("plan_scan.png", 1)]
    assert scan.page_class == "floor_plan" and scan.confidence == 0.5 and scan.level_id == "L0"
    assert scan.evidence[0]["method"] == "ocr" and scan.evidence[0]["pixel_box"] == [100, 50, 400, 80]
    # Milestone 7: a titled raster page is extractable (raster adapter).
    assert scan.skip_reason is None and scan.is_extractable() and scan.extractor == "raster"


def test_project_documents_skips_truth_and_brief():
    files = [p.name for p in C.project_documents(PROJECTS / "synthetic-03")]
    assert files == ["kat_planlari.pdf", "mobilya_plani.dxf"]


# --------------------------------------------------------------------------
# Milestone 7 (docs/milestone7.md §2.1): generic labels, level assumption, English titles, extractors
# --------------------------------------------------------------------------

def _pdf(path: Path, *, texts=(), lines=(), rects=(), size=(842, 595), rect_width=1.0) -> Path:
    """A small vector PDF: ``texts`` = (x, y, text), ``lines`` = (x0, y0, x1, y1), ``rects`` = (x, y, w, h) drawn
    with ``rect_width``."""
    from reportlab.pdfgen import canvas as rl_canvas
    c = rl_canvas.Canvas(str(path), pagesize=size)
    c.setLineWidth(rect_width)
    for x0, y0, x1, y1 in lines:
        c.line(x0, y0, x1, y1)
    for x, y, w, h in rects:
        c.rect(x, y, w, h)
    c.setFont("Helvetica", 10)
    for x, y, text in texts:
        c.drawString(x, y, text)
    c.showPage()
    c.save()
    return path


def _hatch(x0, y0, x1, y1, step=0.6):
    """45-degree hatch lines clipped to a box (a wall drawn the CAD way)."""
    out = []
    k = x0 - (y1 - y0)
    while k <= x1:
        a = (max(k, x0), y0 + max(k, x0) - k)
        b = (min(k + (y1 - y0), x1), y0 + min(k + (y1 - y0), x1) - k)
        if b[0] > a[0]:
            out.append((a[0], a[1], b[0], b[1]))
        k += step
    return out


def test_real01_is_a_floor_plan_by_its_room_labels_and_hatch():
    recs = C.classify_pages(PROJECTS / "real01")
    assert len(recs) == 1
    rec = recs[0]
    assert (rec.kind, rec.page_class, rec.confidence, rec.classifier, rec.extractor) == \
        ("vector", "floor_plan", 0.6, "generic_labels", "generic")
    assert rec.skip_reason is None and rec.is_extractable() and rec.wall_test.startswith("hatch comb of")
    assert [e["text"] for e in rec.evidence].count("Bed Room") == 2 and all(e["page"] == 1 for e in rec.evidence)
    # The only plan page has no level title: L0 "Ground floor", assumed.
    assert (rec.level_id, rec.level_label, rec.level_order, rec.label_source) == ("L0", "Ground floor", 0, "assumed")
    assert rec.scale is None                                   # the scale comes from the dimensions (core)
    assert rec.to_json()["classifier"] == "generic_labels"
    assert rec.generic_page is not None and rec.generic_page.source_kind == "cad_pdf"


def test_room_labels_alone_or_a_wall_structure_alone_are_no_plan(tmp_path):
    project = tmp_path / "p"
    project.mkdir()
    _pdf(project / "labels.pdf", texts=[(100, 100, "LIVING ROOM"), (300, 100, "KITCHEN")], lines=[(0, 0, 10, 10)])
    walls = [ln for x in range(0, 400, 80) for ln in _hatch(100 + x, 300, 160 + x, 312)]
    _pdf(project / "walls.pdf", texts=[(100, 100, "NOTES")], lines=walls)
    recs = {r.file: r for r in C.classify_pages(project)}
    labels, hatch = recs["labels.pdf"], recs["walls.pdf"]
    assert labels.page_class == "other" and "generic rule not met: no wall structure" in labels.skip_reason
    assert hatch.page_class == "other" and "only 0 room-name label(s)" in hatch.skip_reason
    assert labels.classifier is None and not labels.is_extractable()


def test_hatch_dark_fill_and_thin_polygon_wall_tests():
    from wenart.ingest.generic.model import GenericPage, Stroke

    def page(strokes):
        return GenericPage(file="t.pdf", page=1, source_kind="cad_pdf", units="pt", units_to_m=None,
                           size=(842.0, 595.0), strokes=strokes)

    lines = [ln for x in range(0, 400, 80) for ln in _hatch(100 + x, 300, 160 + x, 312)]
    hatch = [Stroke(id=f"h{i}", kind="line", pts=[(a, b), (c, d)], colour=(0.0, 0.0, 0.0))
             for i, (a, b, c, d) in enumerate(lines)]
    assert len(hatch) >= 200 and C.wall_structure(page(hatch)).startswith("hatch comb of")
    assert C.wall_structure(page(hatch[:150])) is None                # too few lines
    wide = [Stroke(id=f"w{i}", kind="line", pts=[(i * 10.0, 0.0), (i * 10.0 + 5, 5.0)], colour=(0.0, 0.0, 0.0))
            for i in range(300)]
    assert C.wall_structure(page(wide)) is None                       # a step of 10 pt is no comb
    dark = Stroke(id="f", kind="polyline", pts=[(0, 0), (100, 0), (100, 8), (0, 8)], closed=True,
                  colour=None, fill=(0.2, 0.2, 0.2))
    green = Stroke(id="g", kind="polyline", pts=[(0, 0), (100, 0), (100, 8), (0, 8)], closed=True,
                   colour=None, fill=(0.1, 0.4, 0.1))
    arrow = Stroke(id="a", kind="polyline", pts=[(0, 0), (6, 2), (0, 4)], closed=True, colour=None,
                   fill=(0.0, 0.0, 0.0))
    assert C.wall_structure(page([dark])) == "dark grey fill f"
    assert C.wall_structure(page([green, arrow])) is None             # chroma, and an arrowhead is not wall-sized
    thin = [Stroke(id=f"t{i}", kind="polyline", pts=[(0, i * 20.0), (200, i * 20.0), (200, i * 20.0 + 6),
                                                       (0, i * 20.0 + 6)], closed=True, colour=(0.0, 0.0, 0.0))
            for i in range(4)]
    assert C.wall_structure(page(thin)) == "4 closed thin polygons"
    assert C.wall_structure(page(thin[:3])) is None


def test_untitled_dxf_without_synthetic_layers_is_generic(tmp_path):
    project = tmp_path / "p"
    project.mkdir()
    shutil.copyfile(PROJECTS / "synthetic-06" / "source" / "synthetic-06.dxf", project / "plan.dxf")
    rec = C.classify_pages(project)[0]
    assert (rec.page_class, rec.classifier, rec.extractor, rec.confidence) == \
        ("floor_plan", "generic_labels", "generic", 0.6)
    assert rec.wall_test.startswith("HATCH:") and "A-WALL" in rec.wall_test
    texts = [e["text"] for e in rec.evidence]
    assert "KITCHEN" in texts and "LIVING ROOM" in texts                    # ATTRIB of a ROOMTAG block, MTEXT
    assert any(e.get("block") == "ROOMTAG" for e in rec.evidence)
    assert rec.scale["metres_per_unit"] == 0.0254 and (rec.level_id, rec.label_source) == ("L0", "assumed")


def test_titled_dxf_without_synthetic_layers_keeps_its_title_and_goes_generic(tmp_path):
    project = tmp_path / "p"
    project.mkdir()
    shutil.copyfile(FIXTURES_06_TITLED / "synthetic-06-titled.dxf", project / "plan.dxf")
    rec = C.classify_pages(project)[0]
    assert (rec.page_class, rec.classifier, rec.extractor, rec.confidence) == ("floor_plan", "title", "generic", 1.0)
    # English titles are title case like the Turkish ones (D's titled fixture truth: "Ground Floor"); only the
    # assumed level of an untitled page is "Ground floor".
    assert (rec.level_id, rec.level_label, rec.label_source, rec.level_label_raw) == \
        ("L0", "Ground Floor", "title", "GROUND FLOOR PLAN")
    truth = json.loads((FIXTURES_06_TITLED / "truth" / "building.json").read_text(encoding="utf-8"))
    assert (truth["levels"][0]["label"], truth["levels"][0]["order"]) == (rec.level_label, rec.level_order)


def test_synthetic_pages_keep_the_synthetic_extractors():
    recs = by_page(C.classify_pages(PROJECTS / "synthetic-01"))
    assert recs[("zemin_kat.dxf", 1)].extractor == "synthetic" and recs[("1_kat.pdf", 1)].extractor == "synthetic"
    assert recs[("zemin_kat.dxf", 1)].classifier == "title" and recs[("1_kat.pdf", 1)].label_source == "title"


def test_titled_pdf_page_without_wall_rectangles_goes_generic(tmp_path):
    project = tmp_path / "p"
    project.mkdir()
    _pdf(project / "plan.pdf", texts=[(100, 550, "ZEMİN KAT PLANI"), (200, 200, "SALON")],
         lines=[(100, 100, 400, 100), (100, 100, 100, 300)])
    # The synthetic convention: walls are closed rectangles drawn at 0.5 pt.
    _pdf(project / "old.pdf", texts=[(100, 550, "1. KAT PLANI")], rects=[(100, 100, 200, 6)], rect_width=0.5)
    recs = {r.file: r for r in C.classify_pages(project)}
    assert (recs["plan.pdf"].page_class, recs["plan.pdf"].classifier, recs["plan.pdf"].extractor) == \
        ("floor_plan", "title", "generic")
    assert (recs["old.pdf"].page_class, recs["old.pdf"].extractor) == ("floor_plan", "synthetic")


def test_several_untitled_plan_pages_cannot_be_ordered(tmp_path):
    project = tmp_path / "p"
    project.mkdir()
    shutil.copyfile(PROJECTS / "real01" / "real01.pdf", project / "a.pdf")
    shutil.copyfile(PROJECTS / "real01" / "real01.pdf", project / "b.pdf")
    recs = C.classify_pages(project)
    assert [r.page_class for r in recs] == ["floor_plan", "floor_plan"]
    assert all(r.level_id is None and r.label_source is None for r in recs)
    assert all(r.level_problem == "cannot order untitled plan pages (a.pdf p1, b.pdf p1)" for r in recs)


def test_untitled_plan_page_next_to_a_titled_one_is_not_assumed():
    titled = C.PageRecord(file="a.pdf", page=1, format="pdf", kind="vector", page_class="floor_plan", level_id="L0")
    untitled = C.PageRecord(file="b.pdf", page=1, format="pdf", kind="vector", page_class="floor_plan")
    C.assign_untitled_levels([titled, untitled])
    assert untitled.level_id is None and "next to titled plan pages" in untitled.level_problem
    assert titled.level_problem is None


def test_text_drawn_as_geometry_page(tmp_path):
    project = tmp_path / "p"
    project.mkdir()
    _pdf(project / "shx.pdf", lines=[(100, 100, 400, 100), (100, 100, 100, 300)])
    rec = C.classify_pages(project)[0]
    assert (rec.kind, rec.page_class, rec.skip_reason) == ("vector", "other", C.SHX_TEXT_REASON)
    assert not rec.is_extractable()


def test_same_stem_dxf_wins_without_converting_the_dwg(tmp_path, monkeypatch):
    project = tmp_path / "p"
    project.mkdir()
    (project / "Plan.dwg").write_bytes(b"AC1015" + b"\0" * 64)
    shutil.copyfile(PROJECTS / "synthetic-01" / "zemin_kat.dxf", project / "plan.dxf")

    def no_conversion(*args, **kwargs):
        raise AssertionError("the DWG must not be converted")

    monkeypatch.setattr(dwg_mod, "convert", no_conversion)
    recs = {r.format: r for r in C.classify_pages(project, work_dir=tmp_path / "work")}
    assert recs["dwg"].skip_reason == C.SAME_STEM_REASON and not recs["dwg"].is_extractable()
    assert recs["dxf"].page_class == "floor_plan" and recs["dxf"].level_id == "L0"


def test_english_titles_and_class_words():
    from wenart.ingest.model import TextItem, english_level_label, normalise_level
    assert english_level_label("GROUND FLOOR PLAN") == ("Ground Floor", 0)
    assert english_level_label("First Floor") == ("First Floor", 1)
    assert english_level_label("SECOND FLOOR FURNITURE LAYOUT PLAN") == ("Second Floor", 2)
    assert english_level_label("3RD FLOOR") == ("3rd Floor", 3)
    assert english_level_label("12th floor") == ("12th Floor", 12)
    assert english_level_label("BASEMENT") == ("Basement", -1) and english_level_label("Bed Room") is None
    assert normalise_level("ZEMİN KAT PLANI") == ("Zemin Kat", 0)
    assert normalise_level("GROUND FLOOR PLAN") == B.normalise_level_label("GROUND FLOOR PLAN") == ("Ground Floor", 0)
    assert page_class_for("GROUND FLOOR PLAN") == "floor_plan"
    assert page_class_for("FIRST FLOOR FURNITURE PLAN") == "furniture_plan"
    assert page_class_for("FURNITURE LAYOUT PLAN") == "furniture_plan" and page_class_for("Floor") is None
    texts = [TextItem("LIVING ROOM", (0, 0), [0, 0, 1, 1], 0, "T:1", 100, role="room_label"),
             TextItem("FIRST FLOOR PLAN", (0, 0), [0, 0, 1, 1], 0, "T:2", 300, role="title")]
    page_class, title, confidence = C.classify_texts(texts)
    assert (page_class, title.entity, confidence) == ("floor_plan", "T:2", 1.0)
    rec = C.PageRecord(file="x.pdf", page=1, format="pdf", kind="vector")
    C.apply_level(rec, title)
    assert (rec.level_id, rec.level_label, rec.label_source, rec.classifier) == ("L1", "First Floor", "title", "title")
    assert C.classify_texts(texts[:1])[0] == "other"


def test_imperial_texts_scale_notes_and_numbers():
    assert parse_scale_text('SCALE 1/4" = 1\'-0"') is None          # imperial: not 1:4
    assert parse_scale_text("SCALE: 1/48\"") is None and parse_scale_text("SCALE 1:50") == 50
    assert parse_scale_text("OLCEK 1/50.") == 50
    assert parse_number("50'") is None and text_role("50'") == "dimension"
    assert text_role("14'-0\"") == "dimension" and text_role("11' x 10'") == "room_label"
    assert text_role("GROUND FLOOR") == "title"
