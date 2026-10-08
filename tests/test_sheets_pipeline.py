"""The pipeline on a multi-region sheet (docs/milestone10.md §1.6a): one page record per region, the unit of the unit
check, every level in the registered frame with its heights from the section, alternatives as their own levels with
``same_as`` rooms, variants, slabs with stair voids, the roof, the site ground, the levels left out
(``failed_levels``), and a stale ``sheets.json`` analysed again."""
from __future__ import annotations

import json

import pytest

import wenart.sheets as SH
from _sheets_fixture import write_sheet
from wenart import building as B
from wenart.ingest import pipeline as P


def _build(tmp_path, name="p", brief=None, **opts):
    project = tmp_path / name
    project.mkdir()
    write_sheet(project / "sheet.dxf", **opts)
    if brief is not None:
        (project / "brief.yaml").write_text(brief, encoding="utf-8")
    building, build = P.run_project(project, tmp_path / f"{name}_out", no_ai=True)
    return building, build, tmp_path / f"{name}_out"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    return _build(tmp_path_factory.mktemp("pipe"))


def test_status_and_schema(built):
    building, build, out = built
    assert building["status"] == "ok", building["warnings"]
    assert B.validation_errors(building) == []
    assert (out / "sheets.json").is_file() and (out / "report.md").is_file()
    assert "## Building (sheets)" in (out / "report.md").read_text(encoding="utf-8")


def test_one_page_record_per_region(built):
    building, _, out = built
    pages = building["documents"][0]["pages"]
    assert [p["region_id"] for p in pages] == ["r1", "r2", "r3", "r4", "r5", "r6"]
    assert [p["class"] for p in pages] == ["title_block", "floor_plan", "floor_plan", "floor_plan", "floor_plan",
                                           "section"]
    assert pages[3]["region_class"] == "alternative_floor_plan" and pages[3]["variant"] == "Açık mutfak"
    assert pages[0]["skip_reason"].startswith("title_block") and pages[5]["skip_reason"].startswith("section")
    for p in pages[1:5]:
        assert p["scale"]["metres_per_unit"] == 0.01 and "unit check" in p["scale"]["evidence"]["text"]
        assert p["debug_image"] == f"debug/sheet_dxf_p1_{p['region_id']}.png" and (out / p["debug_image"]).is_file()


def test_levels_with_heights_from_the_section(built):
    building, _, _ = built
    levels = {lv["id"]: lv for lv in building["levels"]}
    assert list(levels) == ["L-1", "L-1b", "L0", "L1"]
    assert {k: lv["kind"] for k, lv in levels.items()} == {"L-1": "basement", "L-1b": "basement", "L0": "floor",
                                                           "L1": "attic"}
    assert {k: lv["elevation"] for k, lv in levels.items()} == pytest.approx({"L-1": -3.0, "L-1b": -3.0, "L0": 0.0,
                                                                              "L1": 3.15}, abs=0.001)
    assert all(lv["elevation_source"] == "section" and lv["ceiling_height_source"] == "section"
               for lv in levels.values())
    assert levels["L0"]["ceiling_height"] == pytest.approx(3.0, abs=0.001)
    assert levels["L0"]["floor_to_floor"]["value"] == pytest.approx(3.15, abs=0.001)
    assert levels["L-1b"]["variant"] == "Açık mutfak" and levels["L-1b"]["base_level_id"] == "L-1"
    assert levels["L-1b"]["variant_group"] == "vg_L-1" and levels["L-1"]["variant"] == "base"
    assert {lv["region_id"] for lv in levels.values()} == {"r2", "r3", "r4", "r5"}
    walls = [w for w in building["walls"] if w["level_id"] == "L0"]
    assert all(w["height"] == pytest.approx(3.0, abs=0.001) for w in walls)


def test_every_level_in_one_frame(built):
    building, _, _ = built
    for level_id in ("L-1", "L-1b", "L0", "L1"):
        walls = [w for w in building["walls"] if w["level_id"] == level_id]
        xs = [p[0] for w in walls for p in (w["start"], w["end"])]
        ys = [p[1] for w in walls for p in (w["start"], w["end"])]
        # 20 cm outer walls around a 10 x 8 m outline whose outer corner is the frame's origin, on every level.
        assert (min(xs), min(ys), max(xs), max(ys)) == pytest.approx((0.0, 0.1, 10.0, 7.9), abs=0.02), level_id


def test_rooms_alternatives_and_variants(built):
    building, _, _ = built
    rooms = {r["id"]: r for r in building["rooms"]}
    assert rooms["r_L-1b_salon"]["same_as"] == "r_L-1_salon"
    assert rooms["r_L-1b_acik_mutfak"]["same_as"] is None
    assert rooms["r_L1_cocuk_odasi"]["room_subtype"] == "child"
    assert all("twin_of" in r for r in rooms.values())
    variants = {v["id"]: v for v in building["variants"]}
    assert variants["base"]["levels"] == ["L-1", "L0", "L1"]
    alt = variants["l-1b-acik-mutfak"]
    assert alt["levels"] == ["L-1b", "L0", "L1"] and alt["rooms_changed"] == ["r_L-1b_acik_mutfak"]
    assert alt["changes"] == [{"variant_group": "vg_L-1", "level_id": "L-1b", "replaces": "L-1"}]


def test_slabs_roof_and_site(built):
    building, _, _ = built
    slabs = {s["id"]: s for s in building["slabs"]}
    assert set(slabs) == {"sl_L-1", "sl_L-1b", "sl_L0", "sl_L1"}
    assert slabs["sl_L0"]["below_level_id"] == "L-1" and slabs["sl_L0"]["z_top"] == pytest.approx(0.0)
    assert all(s["thickness"] == pytest.approx(0.15) and s["thickness_source"] == "section" for s in slabs.values())
    assert [o["kind"] for o in slabs["sl_L0"]["openings"]] == ["stair_void"]
    stair = next(f for f in building["furniture"] if f["id"] == slabs["sl_L0"]["openings"][0]["furniture_id"])
    assert stair["type"] == "stair" and stair["level_id"] == "L-1"
    assert slabs["sl_L-1b"]["variants"] == ["l-1b-acik-mutfak"] and slabs["sl_L0"]["variants"] == []
    roof = building["roof"]
    assert roof["type"] == "mansard" and roof["type_source"] == "plan_roof_lines" and roof["planes"] == []
    assert roof["over_level_id"] == "L1" and roof["eaves_height"]["value"] == pytest.approx(3.65, abs=0.01)
    assert building["facade"]["faces"] == [] and "default" not in building["facade"]
    site = building["site"]
    assert site["north_deg"]["method"] == "assumed"
    assert [g["side"] for g in site["ground"]["levels"]] == ["left", "right"] and site["ground"]["terrain"] == "flat"
    kinds = {c["kind"] for c in building["conflicts"]}
    assert {"unit_mismatch", "level_mark_mismatch"} <= kinds


def test_failed_level_is_left_out_with_the_levels_above(tmp_path):
    building, build, _ = _build(tmp_path, walls={"ground": False})
    left = {x["region_id"]: x["reason"] for x in building["levels_left_out"]}
    assert set(left) == {"r2", "r5"}
    assert "no building walls" in left["r2"] and "above the left-out level L0" in left["r5"]
    assert [lv["id"] for lv in building["levels"]] == ["L-1", "L-1b"]
    assert building["status"] == "ok"
    assert [v["levels"] for v in building["variants"]] == [["L-1"], ["L-1b"]]


def test_failed_levels_stop(tmp_path):
    building, build, _ = _build(tmp_path, brief="failed_levels: stop\n", walls={"ground": False})
    assert building["status"] == "needs_review"
    assert any("r2 (L0)" in r for r in build.review_reasons)


def test_a_stale_sheets_json_is_analysed_again(tmp_path, built):
    project = tmp_path / "p"
    project.mkdir()
    write_sheet(project / "sheet.dxf")
    out = tmp_path / "out"
    SH.run(project, out, no_ai=True)
    doc = json.loads((out / "sheets.json").read_text(encoding="utf-8"))
    doc["inputs"][0]["sha256"] = "0" * 64
    doc["multi_region"] = False
    (out / "sheets.json").write_text(json.dumps(doc), encoding="utf-8")
    building, build = P.run_project(project, out, no_ai=True)
    assert any("ran again" in w for w in building["warnings"])
    assert len(building["levels"]) == 4


def test_a_crashing_analysis_falls_back_to_pages(tmp_path, monkeypatch):
    project = tmp_path / "p"
    project.mkdir()
    write_sheet(project / "sheet.dxf")

    def boom(*args, **kwargs):
        raise RuntimeError("broken")

    monkeypatch.setattr(SH, "run", boom)
    building, build = P.run_project(project, tmp_path / "out", no_ai=True)
    assert any(w.startswith("sheet analysis failed (RuntimeError: broken)") for w in building["warnings"])
    assert all("region_id" not in p for p in building["documents"][0]["pages"])
