"""The sheets stage end to end on the fixture sheet (docs/milestone10.md §1.2, §3.1 items 3-10): sheets.json valid,
levels, the alternative, the registration, the heights, the roof, the report and the debug image; brief variants;
an unclear base; an untitled single plan."""
from __future__ import annotations

import json

import pytest

import wenart.sheets as SH
from _sheets_fixture import EXPECTED, NORTH_DEG, PLANS, write_sheet


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
        # p_ref = R . (p_source . metres_per_unit) + shift_m (§1.6b row 1); the reference maps onto itself.
        g = PLANS["ground"][0]
        assert r["registration"]["shift_m"] == pytest.approx([(g[0] - ox) * 0.01, (g[1] - oy) * 0.01], abs=0.01)
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
    # level_mark = printed mark - datum (building z); level_mark_target_z = the line the mark points at.
    lv = {e["level_id"]: e for e in h["levels"]}
    assert lv["L-1"]["level_mark"]["value"] == pytest.approx(-3.0) and "40.00" in lv["L-1"]["level_mark"]["note"]
    assert lv["L-1"]["level_mark_target_z"]["value"] == pytest.approx(-3.15, abs=0.01)
    assert lv["L0"]["level_mark"]["value"] == pytest.approx(0.0) and lv["L1"]["level_mark"] is None
    # Profile s from the left outer wall face; the knee wall = the roof's top surface there minus the attic floor.
    assert roof["profile"][0] == pytest.approx([-0.5, 3.65], abs=0.01)
    assert roof["knee_wall"]["value"] == pytest.approx(0.5 + 0.05 * 300 / 55, abs=0.01)
    assert h["cut_at"] is None and h["flipped"] is None


def test_no_section_assumes_heights(tmp_path):
    # §1.6b row 6: no section: floor to floor 3.00 m, slab and ceiling from the brief, all assumed (note, conf. 0).
    res = _run(tmp_path, section=False, brief="slab_thickness: 0.2\nceiling_height: 2.6\n")
    h = res.doc["heights"]
    lv = {e["level_id"]: e for e in h["levels"]}
    assert {k: v["floor_z"]["value"] for k, v in lv.items()} == pytest.approx({"L-1": -3.0, "L0": 0.0, "L1": 3.0})
    for e in h["levels"]:
        for key, want in (("floor_to_floor", 3.0), ("ceiling_height", 2.6)):
            v = e[key]
            assert v["value"] == pytest.approx(want) and v["method"] == "assumed"
            assert v["confidence"] == 0 and v["note"]
    assert all(s["thickness"]["value"] == pytest.approx(0.2) for s in h["slabs"])
    assert SH.validation_errors(res.doc) == []


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


def test_brief_variants_base_reads_the_alternative_but_does_not_list_it(tmp_path):
    # §1.6b row 7: variants: base: alternatives read but not in variants[].
    res = _run(tmp_path, brief="variants: base\n")
    alt = next(r for r in res.doc["regions"] if r["class"] == "alternative_floor_plan")
    assert alt["use"] == "read" and alt["level"]["id"] == "L-1b"
    assert [v["id"] for v in res.doc["variants"]] == ["base"]
    assert any("alternatives read, not built: l-1b-acik-mutfak" in w for w in res.doc["warnings"])


def test_brief_variants_list_matches_name_slug_gloss_or_id(tmp_path):
    for name in ("Açık mutfak", "acik-mutfak", "open kitchen", "l-1b-acik-mutfak"):
        res = _run(tmp_path, name=f"p_{len(name)}_{name[:3]}", brief=f"variants: ['{name}']\n")
        assert [v["id"] for v in res.doc["variants"]] == ["base", "l-1b-acik-mutfak"], name
    res = _run(tmp_path, name="p_unknown", brief="variants: ['sauna']\n")
    assert [v["id"] for v in res.doc["variants"]] == ["base"]
    assert any("sauna not found among the alternatives" in w for w in res.doc["warnings"])


def test_two_plain_titles_of_one_level_are_a_copy_not_an_alternative(tmp_path):
    # §1.6b row 4: the same level with the same title is a copy (secondary_regions), never an alternative.
    res = _run(tmp_path, alternative_title="BODRUM KAT PLANI")
    basement = next(lv for lv in res.doc["levels"] if lv["id"] == "L-1")
    assert basement["alternatives"] == [] and basement["secondary_regions"] == ["r4"]
    assert basement["base_region"] == "r3"
    assert [v["id"] for v in res.doc["variants"]] == ["base"]
    assert "variant_base_unclear" not in [c["kind"] for c in res.doc["conflicts"]]


def test_all_titles_with_alternative_words_make_the_base_unclear(tmp_path):
    res = _run(tmp_path, titles={"basement": "BODRUM KAT PLANI ALTERNATİF 1"},
               alternative_title="BODRUM KAT PLANI ALTERNATİF 2")
    kinds = [c["kind"] for c in res.doc["conflicts"]]
    assert "variant_base_unclear" in kinds
    basement = next(lv for lv in res.doc["levels"] if lv["id"] == "L-1")
    assert basement["base_region"] == "r3" and basement["alternatives"][0]["region"] == "r4"
    assert basement["alternatives"][0]["base_unclear"] is True
    for rid in ("r3", "r4"):
        assert _region(res.doc, rid)["status"] == "unverified"


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


def test_site_plan_and_elevation(tmp_path):
    # §1.6b rows 1, 12: the site plan registered through the building's outline (site_outline), its evidence in
    # building metres, the north turned with it; an elevation's faces in building z, its viewer's direction.
    res = _run(tmp_path, exterior=True)
    doc = res.doc
    assert SH.validation_errors(doc) == []
    site_region = next(r for r in doc["regions"] if r["class"] == "site_plan")
    assert site_region["use"] == "exterior" and site_region["registration"]["method"] == "site_outline"
    assert site_region["registration"]["residual_m"] <= 0.01 and site_region["registration"]["rotation_deg"] == 0.0
    ex = doc["exterior"]
    site = ex["site"]
    xs = [p[0] for p in site["plot"]]
    ys = [p[1] for p in site["plot"]]
    # The building's outline is drawn at (7, 6) m on the site plan: the plot lands 7 m left and 6 m below the origin.
    assert (min(xs), min(ys), max(xs), max(ys)) == pytest.approx((-7.0, -6.0, 17.0, 14.0), abs=0.01)
    assert site["parking"][0]["polygon"][0] == pytest.approx([12.0, 8.0], abs=0.01)
    assert site["trees"][0]["points"][0] == pytest.approx([-4.0, 11.0], abs=0.01)
    assert {lab["kind"] for lab in site["labels"]} == {"parking", "garden"}
    assert ex["north"]["value"] == pytest.approx(NORTH_DEG, abs=3.0)
    assert ex["north"]["evidence"][0]["region_id"] == site_region["id"]
    elev = next(r for r in doc["regions"] if r["class"] == "elevation")
    faces = {f["material"]: f for f in ex["facade"]}
    assert set(faces) == {"render", "stone_cladding"}
    assert faces["stone_cladding"]["side"] == "south" and faces["stone_cladding"]["z_range"] == pytest.approx([0, 1])
    assert faces["render"]["z_range"] is None and all(f["colour"] is None for f in faces.values())
    seen = ex["openings_seen"][0]
    assert seen["region"] == elev["id"] and (seen["windows"], seen["doors"]) == (3, 1)
    # The viewer of the south facade looks north: north is ~30 deg clockwise from +Y, i.e. ~60 deg ccw from +X.
    assert seen["view_bearing_deg"] == pytest.approx((90.0 + NORTH_DEG) % 360.0, abs=3.0)
    assert [p["x"] for p in seen["positions_m"]] == pytest.approx([1.5, 1.5, 4.5, 7.0])
    assert seen["plan_check"] is None


def test_frames_stay_frames_and_plot_lines_hold_their_site(tmp_path):
    res = _run(tmp_path, exterior=True)
    frames = res.doc["documents"][0]["sheets"][0]["frames"]
    assert [f["box"] for f in frames] == [[0.0, 0.0, 9000.0, 5000.0]]
    site = next(r for r in res.doc["regions"] if r["class"] == "site_plan")
    assert site["box"][0] == pytest.approx(6200.0) and site["box"][2] == pytest.approx(8600.0)
