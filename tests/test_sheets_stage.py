"""The sheets stage end to end on the fixture sheet (docs/milestone10.md §1.2, §3.1 items 3-10): sheets.json valid,
levels, the alternative, the registration, the heights, the roof, the report and the debug image; brief variants;
an unclear base; an untitled single plan."""
from __future__ import annotations

import json

import pytest

import wenart.sheets as SH
from _sheets_fixture import EXPECTED, PLANS, write_sheet


def _run(tmp_path, name="p", brief: str | None = None, **opts):
    project = tmp_path / name
    project.mkdir()
    write_sheet(project / "sheet.dxf", **opts)
    if brief is not None:
        (project / "brief.yaml").write_text(brief, encoding="utf-8")
    return SH.run(project, tmp_path / f"{name}_out", no_ai=True)


@pytest.fixture(scope="module")
def result(tmp_path_factory):
    return _run(tmp_path_factory.mktemp("stage"))


def _region(doc, region_id):
    return next(r for r in doc["regions"] if r["id"] == region_id)


def test_sheets_json_is_written_and_valid(result, tmp_path_factory):
    doc = result.doc
    assert SH.validation_errors(doc) == []
    assert doc["kind"] == "sheets" and doc["multi_region"] is True
    assert len(doc["regions"]) == EXPECTED["regions"]
    assert [r["class"] for r in doc["regions"]] == ["title_block", "floor_plan", "floor_plan",
                                                    "alternative_floor_plan", "floor_plan", "section"]
    assert [r["use"] for r in doc["regions"]] == ["ignored", "read", "read", "read", "read", "heights"]
    assert doc["regions"][0]["title"]["text"] == "PLANLAR"
    assert [s["entity"].split(":")[0] for s in doc["stray"]] == ["LINE"]
    assert doc["stray"][0]["distance_m"] > 900
    assert result.review == [] and doc["needs_review"] == []
    assert doc["inputs"][0]["file"] == "sheet.dxf" and len(doc["inputs"][0]["sha256"]) == 64


def test_units_mismatch_is_listed(result):
    units = result.doc["documents"][0]["units"]
    assert units["insunits"] == 4 and units["metres_per_unit"] == 0.01 and units["method"] == "unit_check"
    decided = {c["check"]: c["unit"] for c in units["checks"]}
    assert decided["area_labels"] == "cm" and decided["level_marks"] == "cm" and decided["door_widths"] == "cm"
    kinds = [c["kind"] for c in result.doc["conflicts"]]
    assert "unit_mismatch" in kinds


def test_levels_alternative_and_variants(result):
    doc = result.doc
    assert {lv["id"]: lv["kind"] for lv in doc["levels"]} == EXPECTED["levels"]
    basement = next(lv for lv in doc["levels"] if lv["id"] == "L-1")
    alt = basement["alternatives"][0]
    exp = EXPECTED["alternative"]
    assert (alt["level_id"], alt["slug"], alt["variant"], alt["base_unclear"]) == (exp["level_id"], exp["slug"],
                                                                                   exp["variant"], False)
    r4 = _region(doc, alt["region"])
    assert r4["variant_gloss"] == exp["gloss"] and r4["variant_group"] == "vg_L-1" and r4["level"]["id"] == "L-1b"
    base = _region(doc, basement["base_region"])
    assert base["variant"] == "base" and base["variant_slug"] == "base"
    assert [v["id"] for v in doc["variants"]] == ["base", "l-1b-acik-mutfak"]
    assert doc["variants"][1]["levels"] == ["L-1b", "L0", "L1"]
    assert doc["variants"][1]["label"] == "Bodrum Kat: Açık mutfak (open kitchen)"


def test_registration_puts_every_plan_in_one_frame(result):
    doc = result.doc
    plans = [r for r in doc["regions"] if r["use"] == "read"]
    ground = next(r for r in plans if r["level"]["id"] == "L0")
    assert ground["registration"]["method"] == "reference"
    for r in plans:
        tf = r["transform_to_building"]
        key = {"L0": "ground", "L-1": "basement", "L-1b": "alternative", "L1": "attic"}[r["level"]["id"]]
        (ox, oy), _ = PLANS[key]
        # The outer corner of every dwelling lands at the building origin (each plan drawn at its own place).
        x = tf[0] * ox + tf[1] * oy + tf[2]
        y = tf[3] * ox + tf[4] * oy + tf[5]
        assert (x, y) == pytest.approx((0.0, 0.0), abs=0.01), r["id"]
        assert r["registration"]["residual_m"] <= 0.05
        assert r["registration"]["rotation_deg"] == 0.0
    attic = next(r for r in plans if r["level"]["id"] == "L1")
    assert attic["registration"]["stairs_aligned"] is True


def test_heights_from_the_section(result):
    h = result.doc["heights"]
    assert h["cut_axis"] == "x" and h["datum"]["value"] == 43.0
    floors = {lv["level_id"]: lv["floor_z"]["value"] for lv in h["levels"]}
    assert floors == pytest.approx(EXPECTED["floor_z"], abs=0.01)
    ceilings = {lv["level_id"]: lv["ceiling_height"]["value"] for lv in h["levels"]}
    for k, v in EXPECTED["ceiling"].items():
        assert ceilings[k] == pytest.approx(v, abs=0.01)
    assert all(s["thickness"]["value"] == pytest.approx(EXPECTED["slab"], abs=0.01) for s in h["slabs"])
    assert [s["between"] for s in h["slabs"]] == [[None, "L-1"], ["L-1", "L0"], ["L0", "L1"]]
    roof = h["roof"]
    assert roof["pitches_deg"][0]["value"] == pytest.approx(EXPECTED["pitch_deg"], abs=0.1)
    attic_floor = floors["L1"]
    assert roof["eaves_z"]["value"] - attic_floor == pytest.approx(EXPECTED["eaves_above_attic"], abs=0.01)
    assert roof["ridge_z"]["value"] - attic_floor == pytest.approx(EXPECTED["ridge_above_attic"], abs=0.01)
    assert roof["overhang"]["value"] == pytest.approx(EXPECTED["overhang"], abs=0.01)
    assert roof["thickness"]["value"] == pytest.approx(EXPECTED["roof_thickness"], abs=0.01)
    assert [g["side"] for g in h["ground"]] == ["left", "right"]
    assert all(g["z"]["value"] == pytest.approx(0.0, abs=0.01) for g in h["ground"])
    # The 40.00 mark points at the bottom of the lowest slab: listed, geometry wins.
    mism = [c for c in result.doc["conflicts"] if c["kind"] == "level_mark_mismatch"]
    assert len(mism) == 1 and "0.15 m apart" in mism[0]["description"]
    every_value = [lv["floor_z"] for lv in h["levels"]] + [s["thickness"] for s in h["slabs"]]
    assert all(v["method"] == "vector" and v["evidence"] for v in every_value)


def test_marks_that_agree_give_no_conflict(tmp_path):
    res = _run(tmp_path, mark40_at_bottom=False)
    assert not [c for c in res.doc["conflicts"] if c["kind"] == "level_mark_mismatch"]


def test_mansard_from_the_attic_plan_lines(result):
    roof = result.doc["exterior"]["roof"]
    assert roof["type"] == "mansard" and roof["type_source"] == "plan_roof_lines"
    xs = [p[0] for p in roof["outline"]]
    ys = [p[1] for p in roof["outline"]]
    assert (min(xs), max(xs), min(ys), max(ys)) == pytest.approx((-0.5, 10.5, -0.5, 8.5), abs=0.01)
    assert len(roof["break_line"]) == 4
    assert result.doc["exterior"]["facade"] == [] and result.doc["exterior"]["north"] is None


def test_report_and_debug_image_are_written(result, tmp_path_factory):
    out = next(p for p in tmp_path_factory.getbasetemp().rglob("sheets_report.md"))
    text = out.read_text(encoding="utf-8")
    assert "unit_mismatch" in text and "| r4 |" in text and "mansard" in text
    debug = result.doc["documents"][0]["sheets"][0]["debug_image"]
    assert debug == "sheets_debug/sheet_dxf_s1.png"
    assert (out.parent / debug).is_file()


def test_brief_variants_base_leaves_the_alternative_out(tmp_path):
    res = _run(tmp_path, brief="variants: base\n")
    alt = next(r for r in res.doc["regions"] if r["class"] == "alternative_floor_plan")
    assert alt["use"] == "ignored" and "not selected" in alt["ignored_reason"]
    assert [v["id"] for v in res.doc["variants"]] == ["base"]


def test_two_plain_titles_of_one_level_make_the_base_unclear(tmp_path):
    res = _run(tmp_path, alternative_title="BODRUM KAT PLANI")
    kinds = [c["kind"] for c in res.doc["conflicts"]]
    assert "variant_base_unclear" in kinds
    basement = next(lv for lv in res.doc["levels"] if lv["id"] == "L-1")
    assert basement["alternatives"][0]["base_unclear"] is True
    assert basement["alternatives"][0]["variant"] == "Alternative 2"


def test_one_drawing_per_page_is_not_multi_region(tmp_path):
    import ezdxf

    project = tmp_path / "single"
    project.mkdir()
    doc = ezdxf.new("R2013")
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()
    for x0, y0, x1, y1 in ((0, 0, 8000, 200), (0, 5800, 8000, 6000), (0, 0, 200, 6000), (7800, 0, 8000, 6000)):
        msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": "DUVAR"})
    msp.add_text("SALON 30 m²", height=200, dxfattribs={"insert": (1000, 3000)})
    msp.add_text("MUTFAK", height=200, dxfattribs={"insert": (5000, 3000)})
    doc.saveas(project / "plan.dxf")
    res = SH.run(project, tmp_path / "single_out", no_ai=True)
    assert res.doc["multi_region"] is False
    plans = [r for r in res.doc["regions"] if r["use"] == "read"]
    assert len(plans) == 1 and plans[0]["level"]["id"] == "L0" and plans[0]["level"]["method"] == "assumed"
    assert plans[0]["registration"] is None
    assert res.doc["documents"][0]["units"]["method"] == "dxf_insunits"


def test_load_reads_what_run_wrote(result, tmp_path_factory):
    out = next(p for p in tmp_path_factory.getbasetemp().rglob("sheets.json") if "stage" in str(p))
    assert SH.load(out.parent) == json.loads(out.read_text(encoding="utf-8"))
