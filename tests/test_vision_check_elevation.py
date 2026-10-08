"""CPU tests of the elevation check (docs/milestone10.md §3.3 item 4, wenart/vision_check/elevation.py).

The toy house of tests/vc_ext_toy.py (south wall: two windows at x = 2 m and 6 m and a door at 4 m; east wall: a
window; roof eaves 2.7 m, ridge 4.5 m) is compared with drawn elevations: the matching one, one with the roof
overhang as an offset, a wrong count, a mirrored one, an elevation without a side; the built roof heights against
the section; the sheets.json fallback and the Milestone 10 example building.
"""
import copy
import json
from pathlib import Path

import pytest

import vc_ext_toy as E
from wenart.vision_check import elevation as EL
from wenart.vision_check import expected as X

ROOT = Path(__file__).resolve().parents[1]
CFG = X.load_cfg()


def south_elevation(**kw) -> dict:
    ev = {"region_id": "r7", "title": "GÜNEY GÖRÜNÜŞÜ", "side": "south", "view_bearing_deg": 90.0, "windows": 2,
          "doors": 1, "plan_check": None,
          "positions_m": [{"kind": "window", "x": 2.0, "sill": 0.9, "head": 2.1},
                          {"kind": "door", "x": 4.0, "sill": 0.0, "head": 2.1},
                          {"kind": "window", "x": 6.0, "sill": 0.9, "head": 2.1}]}
    ev.update(kw)
    return ev


def check(elevations, scene=None, sheets=None, building=None):
    b = building or E.toy_building(elevations)
    if building is not None:
        b["facade"] = {"faces": [], "elevations": elevations, "evidence": []}
    return EL.elevation_check(b, scene or E.toy_scene("x"), sheets, CFG)


def south(check_result) -> dict:
    return next(f for f in check_result["facades"] if f["side"] == "south")


def test_a_matching_elevation_agrees():
    res = check([south_elevation()])
    f = south(res)
    assert f["result"] == "ok" and f["direction_from"] == "view_bearing_deg"
    assert f["building"]["windows"] == 2 and f["building"]["doors"] == 1
    assert [(o["id"], o["x"], o["sill"], o["head"]) for o in f["building"]["openings"]] == [
        ("win_s1", 2.0, 0.9, 2.1), ("d_s1", 4.0, 0.0, 2.1), ("win_s2", 6.0, 0.9, 2.1)]
    assert f["positions"]["matched"] == 3 and f["positions"]["offset_x_m"] == 0.0 and not f["positions"]["mirrored"]
    assert f["counts"] == {"windows": "ok", "doors": "ok"}
    assert res["summary"] == {"facades": 1, "ok": 1, "mismatch": 0, "not_checked": 0, "roof": "ok"}
    assert EL.lines(res) == []


def test_the_roof_overhang_is_a_common_offset_not_a_mismatch():
    # The drawn outline starts 0.5 m left of the wall (the roof overhang): every x is 0.5 m larger.
    moved = [dict(p, x=p["x"] + 0.5) for p in south_elevation()["positions_m"]]
    f = south(check([south_elevation(positions_m=moved)]))
    assert f["result"] == "ok" and f["positions"]["offset_x_m"] == pytest.approx(0.5)
    far = [dict(p, x=p["x"] + 2.0) for p in south_elevation()["positions_m"]]
    g = south(check([south_elevation(positions_m=far)]))
    assert g["result"] == "mismatch" and any("more than the" in n for n in g["notes"])


def test_a_wrong_count_is_a_mismatch_with_the_side_named():
    res = check([south_elevation(windows=3, positions_m=[])])
    f = south(res)
    assert f["result"] == "mismatch" and f["counts"] == {"windows": "fewer", "doors": "ok"}
    assert f["positions"] is None and any("counts only" in n for n in f["notes"])
    assert EL.lines(res) == ["south (r7): windows fewer; the elevation lists no opening positions: counts only"]


def test_an_opening_the_building_has_and_the_elevation_does_not_draw_is_listed():
    f = south(check([south_elevation(windows=1, positions_m=south_elevation()["positions_m"][:2])]))
    assert f["result"] == "mismatch" and f["counts"]["windows"] == "more"
    assert [o["id"] for o in f["positions"]["extra_in_building"]] == ["win_s2"]


def test_a_position_off_by_more_than_the_tolerance_is_a_mismatch():
    off = south_elevation()["positions_m"]
    off[0] = dict(off[0], sill=1.4, head=2.6)                   # a window drawn 0.5 m higher
    f = south(check([south_elevation(positions_m=off)]))
    assert f["result"] == "mismatch" and len(f["positions"]["missing_in_building"]) == 1


def test_match_openings_tries_the_mirrored_order():
    built = [{"kind": "window", "x": x, "sill": 0.9, "head": 2.1, "id": f"w{i}"} for i, x in enumerate((0.5, 1.0, 4.0))]
    drawn = [{"kind": "window", "x": x, "sill": 0.9, "head": 2.1} for x in (0.5, 3.5, 4.0)]      # 4.5 - x
    m = EL.match_openings(drawn, built)
    assert m["mirrored"] is True and m["matched"] == 3 and m["extra_in_building"] == []
    same = EL.match_openings(built, built)
    assert same["mirrored"] is False and same["matched"] == 3 and same["offset_x_m"] == 0.0


def test_a_mirrored_elevation_is_a_mismatch_with_a_note():
    b = E.toy_building()
    for o in b["openings"]:
        if o["id"] == "win_s2":
            o["center"][0] = 7.0                                  # the south wall is no longer symmetric
    wins = [{"kind": "window", "x": 1.0, "sill": 0.9, "head": 2.1}, {"kind": "door", "x": 4.0, "sill": 0.0, "head": 2.1},
            {"kind": "window", "x": 6.0, "sill": 0.9, "head": 2.1}]       # 8 - x of the building's 2 / 4 / 7
    f = south(check([south_elevation(positions_m=wins)], building=b))
    assert f["result"] == "mismatch" and f["positions"]["mirrored"] is True
    assert any("mirrored" in n for n in f["notes"])


def test_an_elevation_without_a_side_or_a_bearing_is_not_checked():
    res = check([south_elevation(side=None, view_bearing_deg=None)])
    f = res["facades"][0]
    assert f["result"] == "not_checked" and "neither a view bearing nor a side" in f["notes"][0]
    assert res["summary"]["not_checked"] == 1


def test_a_compass_side_alone_gives_the_direction():
    f = south(check([south_elevation(view_bearing_deg=None)]))
    assert f["result"] == "ok" and f["direction_from"] == "side"
    east = check([south_elevation(side="east", view_bearing_deg=180.0, windows=1, doors=0,
                                  positions_m=[{"kind": "window", "x": 3.0, "sill": 0.9, "head": 2.1}])])
    e = east["facades"][0]
    # The east wall seen from outside (looking west): the viewer's right is +Y.. the window at y = 3 m: x = 3 m.
    assert e["result"] == "ok" and e["building"]["windows"] == 1 and e["building"]["doors"] == 0


def test_a_facade_no_outer_wall_faces_is_not_checked():
    b = E.toy_building()
    for w in b["walls"]:
        if w["id"] == "w_w":
            w["exterior"] = False
    res = check([south_elevation(side="west", view_bearing_deg=0.0, windows=0, doors=0, positions_m=[])],
                building=b)
    assert res["facades"][0]["result"] == "not_checked" and "no outer wall" in res["facades"][0]["notes"][0]


def test_the_built_roof_heights_are_compared_with_the_section():
    sheets = {"heights": {"roof": {"eaves": {"value": 2.7, "method": "vector"},
                                   "ridge": {"value": 4.5, "method": "vector"}}}}
    ok = check([], sheets=sheets)["roof"]
    assert ok["result"] == "ok" and ok["built"]["eaves"] == 2.7 and ok["built"]["ridge"] == 4.5
    assert ok["deltas"] == {"eaves": 0.0, "ridge": 0.0}
    high = {"heights": {"roof": {"eaves": {"value": 2.7, "method": "vector"},
                                 "ridge": {"value": 4.2, "method": "vector"}}}}
    bad = check([], sheets=high)
    assert bad["roof"]["result"] == "mismatch" and bad["roof"]["deltas"]["ridge"] == pytest.approx(0.3)
    assert EL.lines(bad) == ["roof: built eaves +0.00 m, ridge +0.30 m from the section"]
    within = {"heights": {"roof": {"eaves": {"value": 2.73, "method": "vector"},
                                   "ridge": {"value": 4.46, "method": "vector"}}}}
    assert check([], sheets=within)["roof"]["result"] == "ok"                          # 5 cm


def test_an_assumed_roof_height_is_not_checked_against_nothing():
    b = E.toy_building()
    b["roof"]["ridge_height"] = {"value": 4.0, "method": "assumed", "confidence": 0.0, "evidence": [],
                                 "note": "not drawn"}
    roof = EL.elevation_check(b, E.toy_scene("x"), None, CFG)["roof"]
    assert roof["result"] == "ok" and roof["deltas"] == {"eaves": 0.0}
    assert any("ridge: the building's value is assumed" in n for n in roof["notes"])
    no_scene = EL.elevation_check(E.toy_building(), None, None, CFG)["roof"]
    assert no_scene["result"] == "not_checked" and "no roof object" in no_scene["notes"][0]


def test_the_sheets_openings_seen_are_the_fallback_for_the_elevations():
    sheets = {"exterior": {"openings_seen": [
        {"region": "r7", "side": "south", "view_bearing_deg": 90.0, "windows": 2, "doors": 1,
         "positions_m": south_elevation()["positions_m"], "plan_check": None, "title": "GÜNEY"}]}}
    res = EL.elevation_check(E.toy_building(), E.toy_scene("x"), sheets, CFG)
    assert res["source"] == "sheets.json exterior.openings_seen" and south(res)["result"] == "ok"
    assert EL.elevation_check(E.toy_building(), E.toy_scene("x"), None, CFG)["facades"] == []


def test_the_m10_example_building_runs_for_both_variants():
    b = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))
    base = EL.elevation_check(b, None, None, CFG, "base")
    alt = EL.elevation_check(b, None, None, CFG, "l-1b-acik-mutfak")
    assert base["source"] == "building.json facade.elevations" and len(base["facades"]) == 2
    f = south(base)
    assert f["drawn"] == {"windows": 4, "doors": 1, "positions": 0} and f["building"]["windows"] >= 0
    assert alt["variant"] == "l-1b-acik-mutfak" and len(alt["facades"]) == 2
    assert base["roof"]["result"] == "not_checked"                                    # no scene manifest here


def test_the_check_is_json_serialisable():
    json.dumps(check([south_elevation()]))
