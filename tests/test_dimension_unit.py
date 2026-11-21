"""The drawing unit from DIMENSION entities that print their own measurement (21 Nov 2026, dataset bench: 35 floors in
centimetres with no unit header or a millimetre header read nothing).

Rule: a DIMENSION without a text override prints its measurement (its block's text, else measurement x DIMLFAC); a bare
whole number says the drawing unit is the dimension's text unit, cm or mm. The physical checks (door widths, text
height, wall thickness, area labels) choose between the two (``units_check.dimension_unit``); a header naming the other
unit is a reported ``unit_mismatch``; when the checks disagree nothing is chosen. A single-plan CAD page takes the
checked unit like a region of a multi-region project (``classify.single_plan_units``)."""
from __future__ import annotations

from pathlib import Path

import ezdxf
import pytest

from wenart.ingest import classify as CL
from wenart.ingest import dxf_generic as DG
from wenart.sheets import read as RD
from wenart.sheets import split as SP
from wenart.sheets import units_check as UC
from wenart.sheets.model import Region


def _rect(msp, x0, y0, x1, y1, layer="DUVAR"):
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": layer})


def write_plan(path: Path, insunits: int, dimlfac: float = 1.0) -> Path:
    """A 10 x 8 m flat drawn in centimetres: 20 cm outer walls, a 10 cm partition, five 90 cm door swings, room names
    15 cm tall and a chain of DIMENSIONs printing their own measurement (no override)."""
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = insunits
    msp = doc.modelspace()
    W, D, T = 1000.0, 800.0, 20.0
    _rect(msp, 0, 0, W, T)
    _rect(msp, 0, D - T, W, D)
    _rect(msp, 0, T, T, D - T)
    _rect(msp, W - T, T, W, D - T)
    _rect(msp, 495, T, 505, D - T)
    for k, (x, y) in enumerate([(100, 100), (300, 300), (600, 150), (750, 500), (850, 300)]):
        msp.add_arc((x, y), 90, 0, 90, dxfattribs={"layer": "KAPI"})
        msp.add_line((x, y), (x, y + 90), dxfattribs={"layer": "KAPI"})
    for name, (x, y) in (("SALON", (200, 420)), ("YATAK ODASI", (700, 420)), ("MUTFAK", (200, 200))):
        msp.add_text(name, height=15, dxfattribs={"insert": (x, y), "layer": "YAZI"})
    for a, b in ((0, 495), (495, 1000), (0, 1000)):
        dim = msp.add_linear_dim(base=(a, -80), p1=(a, 0), p2=(b, 0), dimstyle="EZDXF",
                                 override={"dimlfac": dimlfac, "dimtxt": 15})
        dim.render()
    dim = msp.add_linear_dim(base=(W + 80, 0), p1=(W, 0), p2=(W, D), angle=90, dimstyle="EZDXF",
                             override={"dimlfac": dimlfac, "dimtxt": 15})
    dim.render()
    doc.saveas(path)
    return path


def _check(folder: Path) -> UC.UnitResult:
    doc = RD.read_documents(folder, None)[0]
    regions = []
    for sheet in doc.sheets:
        if sheet.raster or not sheet.ents:
            continue
        for k, c in enumerate(SP.split_sheet(sheet).clusters, start=1):
            regions.append(Region(id=f"r{k}", file=doc.file, sheet=sheet, box=c.box, geometry_box=c.geometry_box,
                                  ents=c.ents, texts=c.texts, kind=c.kind))
    return UC.check_units(doc.insunits, regions, doc.file)


def test_printed_measurement_is_the_number_the_drawing_shows(tmp_path):
    path = write_plan(tmp_path / "plan.dxf", 0)
    page = DG.read_page(path, "plan.dxf")
    printed = sorted(d.printed for d in page.dimensions)
    assert printed == ["1000", "495", "505", "800"] and all(d.text is None for d in page.dimensions)


@pytest.mark.parametrize("insunits", [0, 4])
def test_dimensions_and_doors_give_cm(tmp_path, insunits):
    folder = tmp_path / "p"
    folder.mkdir()
    write_plan(folder / "plan.dxf", insunits)
    res = _check(folder)
    by = {c.check: c for c in res.checks}
    assert by["dimensions"].samples == 4 and by["dimensions"].unit is None          # cm or mm: decides neither
    assert UC.fitting_units(by["dimensions"]) == {"cm", "mm"}
    assert res.unit == "cm" and res.metres_per_unit == 0.01 and res.method == "unit_check" and res.review is None
    if insunits == 4:
        assert res.conflict and "says mm" in res.conflict and "print their lengths" in res.conflict
    else:
        assert any("names no unit" in w and "print their lengths" in w for w in res.warnings)


def test_header_cm_confirmed_is_kept(tmp_path):
    folder = tmp_path / "p"
    folder.mkdir()
    write_plan(folder / "plan.dxf", 5)
    res = _check(folder)
    assert res.unit == "cm" and res.method == "dxf_insunits" and res.conflict is None


def test_disagreeing_checks_choose_nothing():
    dims = UC.Check("dimensions", None, 1.0, 4, shares={"cm": 1.0, "mm": 1.0})
    doors = UC.Check("door_widths", "cm", 0.9, 10, shares={"cm": 0.9})
    text = UC.Check("text_height", None, None, 20, values=[15.0] * 20)          # cm or in
    walls_mm = UC.Check("wall_thickness", "mm", 0.8, 50, shares={"mm": 0.8})
    assert UC.dimension_unit([dims, doors, text]) is not None
    assert UC.dimension_unit([dims, doors, text])[0] == "cm"
    assert UC.dimension_unit([dims, doors, text, walls_mm]) is None                 # sources disagree: no guess
    assert UC.dimension_unit([dims, doors]) is None                                 # one check is no agreement
    marks_m = UC.Check("level_marks", "m", 1.0, 2, shares={"m": 1.0})
    assert UC.dimension_unit([dims, doors, text, marks_m]) is None                  # a unit the dimensions rule out


def test_single_plan_takes_the_checked_unit():
    rec = CL.PageRecord(file="plan.dxf", page=1, format="dxf", kind="vector", page_class="floor_plan",
                        confidence=1.0, converter=None, source_path="plan.dxf")
    rec.extractor = "generic"
    same = CL.PageRecord(file="other.dxf", page=1, format="dxf", kind="vector", page_class="floor_plan",
                         confidence=1.0, converter=None, source_path="other.dxf")
    same.extractor = "generic"
    sheets = {"multi_region": False, "documents": [
        {"file": "plan.dxf", "units": {"insunits": 4, "metres_per_unit": 0.01, "method": "unit_check",
                                       "checks": [{"check": "door_widths", "unit": "cm"}]}},
        {"file": "other.dxf", "units": {"insunits": 5, "metres_per_unit": 0.01, "method": "dxf_insunits"}}]}
    out = CL.region_records([rec, same], sheets)
    assert out[0].units_override == 0.01 and out[0].scale["method"] == "unit_check"
    assert out[1].units_override is None                                             # the header holds


def test_scale_misread_is_flagged_on_any_reading():
    from wenart.reading_check import structure as SR

    page = {"level_id": "L0", "scale": {"metres_per_unit": 0.001, "method": "dxf_insunits"}}
    b = {"documents": [{"file": "plan.dxf", "pages": [page]}], "levels": [{"id": "L0", "elevation": 0.0}],
         "walls": []}
    f = SR.scales_misread(b)
    assert len(f) == 1 and f[0]["rule"] == "scale_misread" and "read no wall" in f[0]["message"]
    b["walls"] = [{"id": "w1", "level_id": "L0", "start": [0, 0], "end": [1.0, 0], "thickness": 0.02},
                  {"id": "w2", "level_id": "L0", "start": [0, 0], "end": [0, 0.8], "thickness": 0.02}]
    assert "implausible" in SR.scales_misread(b)[0]["message"]                    # a cm drawing read in mm
    b["walls"] = [dict(w, end=[v * 10 for v in w["end"]], thickness=0.2) for w in b["walls"]]
    assert SR.scales_misread(b) == []
