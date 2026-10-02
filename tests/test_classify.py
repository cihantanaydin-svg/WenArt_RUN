"""Page classification (wenart/ingest/classify.py) on the synthetic projects."""
import shutil
from pathlib import Path

import pytest

from wenart.ingest import classify as C
from wenart.ingest import dwg as dwg_mod
from wenart.ingest.model import METRES_PER_POINT, page_class_for, parse_number, parse_scale_text, text_role

from conftest import PROJECTS


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
    scan = recs[("1_kat_scan.png", 1)]
    assert (scan.format, scan.kind, scan.page_class) == ("image", "scan", "other")
    assert scan.skip_reason and "OCR" in scan.skip_reason
    assert scan.level_id is None and scan.scale is None
    assert not scan.is_extractable() and dxf.is_extractable() and pdf.is_extractable()


def test_synthetic_02_raster_kinds():
    recs = by_page(C.classify_pages(PROJECTS / "synthetic-02"))
    assert recs[("plan_scan.png", 1)].kind == "scan"
    assert recs[("plan_photo.jpg", 1)].kind == "photo"
    for rec in recs.values():
        assert rec.page_class == "other" and rec.skip_reason
        assert rec.evidence and rec.evidence[0]["method"] == "ai"


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


@pytest.mark.skipif(not dwg_mod.available_converters() or shutil.which("dxf2dwg") is None,
                    reason="no DWG converter (dwg2dxf/ezdwg) and dxf2dwg installed")
def test_dwg_round_trip(tmp_path):
    import subprocess
    import ezdxf
    src = PROJECTS / "synthetic-01" / "zemin_kat.dxf"
    dwg = tmp_path / "zemin_kat.dwg"
    subprocess.run(["dxf2dwg", "-y", "-o", str(dwg), str(src)], check=True, capture_output=True)
    dxf_path, converter = dwg_mod.dwg_to_dxf(dwg, tmp_path / "work")
    assert dxf_path.is_file() and "audit" in converter
    original = ezdxf.readfile(str(src)).modelspace()
    converted = ezdxf.readfile(str(dxf_path)).modelspace()
    for dxftype in ("LWPOLYLINE", "INSERT", "TEXT", "DIMENSION"):
        assert len(original.query(dxftype)) == len(converted.query(dxftype)), dxftype


def test_ocr_hook_classifies_raster_pages():
    def fake_ocr(path: Path):
        return [{"text": "ZEMİN KAT PLANI", "box": [100, 50, 400, 80], "confidence": 0.9},
                {"text": "ÖLÇEK 1/100", "box": [500, 50, 600, 80], "confidence": 0.9}]

    recs = by_page(C.classify_pages(PROJECTS / "synthetic-02", ocr=fake_ocr))
    scan = recs[("plan_scan.png", 1)]
    assert scan.page_class == "floor_plan" and scan.confidence == 0.5 and scan.level_id == "L0"
    assert scan.evidence[0]["method"] == "ocr" and scan.evidence[0]["pixel_box"] == [100, 50, 400, 80]
    assert scan.skip_reason and not scan.is_extractable()


def test_project_documents_skips_truth_and_brief():
    files = [p.name for p in C.project_documents(PROJECTS / "synthetic-03")]
    assert files == ["kat_planlari.pdf", "mobilya_plani.dxf"]
