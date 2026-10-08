"""The unit check of CAD documents (docs/milestone10.md §3.1 item 6, user decision 8): the header is used unless
>= 2 independent checks agree on another unit and none supports it (``unit_mismatch``); checks that contradict the
header without agreement need review; the committed projects keep their headers."""
from __future__ import annotations

from pathlib import Path

import pytest

from _sheets_fixture import write_sheet
from wenart.sheets import read as RD
from wenart.sheets import split as SP
from wenart.sheets import units_check as UC
from wenart.sheets.model import Region

ROOT = Path(__file__).resolve().parents[1]


def _regions(folder: Path, work: Path | None = None) -> list[tuple[object, list[Region]]]:
    out = []
    for doc in RD.read_documents(folder, work):
        regions = []
        for sheet in doc.sheets:
            if sheet.raster or not sheet.ents:
                continue
            res = SP.split_sheet(sheet)
            for k, c in enumerate(res.clusters, start=1):
                regions.append(Region(id=f"r{k}", file=doc.file, sheet=sheet, box=c.box, geometry_box=c.geometry_box,
                                      ents=c.ents, texts=c.texts, kind=c.kind))
        out.append((doc, regions))
    return out


def _check(tmp_path, **opts) -> UC.UnitResult:
    folder = tmp_path / "p"
    folder.mkdir(exist_ok=True)
    write_sheet(folder / "sheet.dxf", **opts)
    doc, regions = _regions(folder)[0]
    return UC.check_units(doc.insunits, regions, doc.file)


def test_header_mm_drawn_in_cm_is_overridden(tmp_path):
    res = _check(tmp_path, insunits=4)
    assert res.unit == "cm" and res.metres_per_unit == 0.01 and res.method == "unit_check"
    assert res.conflict and "says mm" in res.conflict and res.review is None
    by = {c.check: c for c in res.checks}
    assert by["level_marks"].unit == "cm" and by["level_marks"].samples == 1
    assert by["door_widths"].unit == "cm" and by["door_widths"].samples == 4
    assert by["area_labels"].unit == "cm"
    assert by["text_height"].unit is None and "fit equally well" in by["text_height"].note


def test_header_cm_is_used_without_conflict(tmp_path):
    res = _check(tmp_path, insunits=5)
    assert res.unit == "cm" and res.method == "dxf_insunits" and res.conflict is None and res.review is None


def test_unitless_header_takes_the_agreed_unit(tmp_path):
    res = _check(tmp_path, insunits=0)
    assert res.unit == "cm" and res.method == "unit_check" and res.conflict is None
    assert any("names no unit" in w for w in res.warnings)


def test_one_contradicting_check_without_agreement_needs_review():
    checks = [UC.Check("area_labels", "cm", 1.0, 3), UC.Check("level_marks", None, None, 0),
              UC.Check("door_widths", "m", 1.0, 4)]
    # Through the decision of check_units: fake the checks by monkeypatching the five check functions.
    import wenart.sheets.units_check as mod
    saved = (mod.check_area_labels, mod.check_level_marks, mod.check_door_widths, mod.check_wall_thickness,
             mod.check_text_height, mod.check_dimensions)
    try:
        mod.check_area_labels = lambda regions: checks[0]
        mod.check_level_marks = lambda regions: (checks[1], [])
        mod.check_door_widths = lambda regions: checks[2]
        mod.check_wall_thickness = lambda regions: UC.Check("wall_thickness", None, None, 0)
        mod.check_text_height = lambda regions: UC.Check("text_height", None, None, 0)
        mod.check_dimensions = lambda regions: UC.Check("dimensions", None, None, 0)
        res = UC.check_units(4, [], "x.dxf")
        assert res.review and "no two independent checks agree" in res.review and res.metres_per_unit is None
        checks[2] = UC.Check("door_widths", "mm", 1.0, 4)
        res = UC.check_units(4, [], "x.dxf")
        assert res.unit == "mm" and res.method == "dxf_insunits" and res.review is None
        assert any("support it" in w for w in res.warnings)
    finally:
        (mod.check_area_labels, mod.check_level_marks, mod.check_door_widths, mod.check_wall_thickness,
         mod.check_text_height, mod.check_dimensions) = saved


def test_decide_needs_a_clear_winner():
    assert UC._decide("door_widths", {"cm": 3, "in": 3}, 3).unit is None
    assert UC._decide("door_widths", {"cm": 3}, 3).unit == "cm"
    assert UC._decide("door_widths", {"cm": 2}, 2).unit is None                 # too few samples
    assert UC._decide("wall_thickness", {"cm": 6, "in": 5}, 10).unit is None    # 0.6 vs 0.5: no margin


def test_mark_texts_and_points():
    from wenart.ingest.generic.model import Stroke
    from wenart.sheets.model import Txt
    texts = [Txt("MTEXT:1", "43.00", (100, 60, 180, 80), 20), Txt("MTEXT:2", "±0.00", (0, 0, 1, 1), 1),
             Txt("MTEXT:3", "+3,15", (0, 0, 1, 1), 1), Txt("MTEXT:4", "SALON", (0, 0, 1, 1), 1)]
    assert [v for _, v in UC.mark_texts(texts)] == [43.0, 0.0, 3.15]
    v = [Stroke("LINE:a", "line", [(120, 20), (105, 35)]), Stroke("LINE:b", "line", [(120, 20), (135, 35)])]
    assert UC.mark_point(texts[0], UC.segments(v)) == (120, 20, "triangle")


@pytest.mark.parametrize("project", ["synthetic-01", "synthetic-03", "synthetic-04", "synthetic-05", "synthetic-06"])
def test_committed_projects_keep_their_header(project, tmp_path):
    from wenart.ingest import dwg

    if project == "synthetic-06" and not dwg.available_converters():
        pytest.skip("LibreDWG dwg2dxf not installed")
    for doc, regions in _regions(ROOT / "projects" / project, tmp_path):
        if doc.format not in ("dxf", "dwg") or doc.skip_reason:
            continue
        res = UC.check_units(doc.insunits, regions, doc.file)
        assert res.method == "dxf_insunits" and res.conflict is None and res.review is None, (doc.file, res.checks)
        assert res.unit == UC.INSUNITS_NAME[doc.insunits]
        assert any(c.unit == res.unit for c in res.checks)            # at least one check supports the header
