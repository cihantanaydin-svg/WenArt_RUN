"""27 Oct 2026 (user on the bathrooms of real06 run 20261027-180412-full: "clashing sink and bath, also bath is not in
proper place"): drawn fixed equipment stands where it is drawn and never through another drawn fixture
(``wenart.furniture.fixture_seat``; CPU only, synthetic bathrooms).

The case (real06, both floors, moved here into a 2.40 x 2.85 m bathroom): a corner bath drawn in the corner beside the
window, a basin on a vanity to its left and a curved bath screen were read as one outline, 2.54 x 1.01 m at 161.5 deg,
holding the basin. ``infer.ai_named_members`` typed it a bathtub and kept the outline's centre and angle for the
1.80 x 0.80 m product: a bath turned 18 deg across the room, 0.33 m into the basin; the reading, the build's clash
resolver (F5) and Argus's moves all left it there.

Rules (general): 1. a misread or merged outline of a fixture is seated: the real product with its back on a wall and
along it, covering most of the outline, clear of the other drawn fixtures and the door swings; 2. a drawn fixture on a
wall moves only along it; 3. of two drawn fixtures that cut each other the weaker reading gives way; 4. the reading,
the build (F5), the architect's move_piece and Argus (a code decision) all use them.
"""
from __future__ import annotations

import copy
import math

import pytest
from shapely.geometry import Polygon

from test_decor_m8 import room_building
from wenart.audit import argus_ai as AI
from wenart.audit import process as PR
from wenart.blender import architect_actions as AA
from wenart.blender import clashes as CL
from wenart.furniture import fixture_seat as FS
from wenart.furniture import infer as INF
from wenart.furniture import sizes
from wenart.ingest.generic import reading as RD
from wenart.ingest.pipeline import ProjectBuild

W, D = 2.40, 2.85                                      # the bathroom (inner faces), the window wall at y = D
OUTLINE = {"center": [1.322, 2.4352], "size": [2.544, 1.0076], "rotation_deg": 161.545}   # bath + screen + vanity
BASIN = ("washbasin", (0.4994, 2.5961), 0.0, (0.531, 0.342))                              # against the window wall
TOILET = ("toilet", (2.0684, 0.9823), 270.0, (0.445, 0.705))                             # on the east wall


def _rect(fp: dict):
    return FS.footprint_rect(fp)


def _cut(a: dict, b: dict) -> float:
    return FS.cut_depth(_rect(a["footprint"]), _rect(b["footprint"]))


def _bathroom(bath: dict) -> dict:
    """The bathroom with its drawn basin (both AI passes agreed), its toilet and ``bath`` (a footprint dict and fields)
    as the third piece; a door in the south wall swinging in."""
    b = room_building(W, D, "bathroom", furniture=[BASIN, TOILET, ("bathtub", (1.0, 1.0), 0.0, (1.7, 0.75))],
                      doors=(("d1", "s", 0.55, 0.9, True),), windows=(("win1", "n", 1.6, 1.5),))
    basin, toilet, tub = b["furniture"]
    for f in (basin, toilet):
        f["type_method"] = "ai_two_pass"
    tub.update(bath)
    return b


def _untyped_outline() -> dict:
    return {"type": "unknown", "type_method": "none", "status": "unverified", "front_deg": None, "build": False,
            "not_built_reason": "untyped (CLAUDE.md: no untyped piece is built)", "footprint": dict(OUTLINE),
            "evidence": [{"file": "x.dxf", "method": "vector", "confidence": 0.9},
                         {"file": "x.dxf", "method": "ai", "confidence": 0.9, "entity": "recognition:sym_5"}],
            "type_candidates": [
                {"type": "unknown", "model_key": "qwen", "pass": 1, "reason": "a curved shape with a faucet and basin, "
                 "resembling a sink or bathtub"},
                {"type": "not_furniture", "model_key": "glm", "pass": 2, "reason": "a curved bathtub shape"}]}


# real06's upper bathroom: the same cluster read 2.42 x 0.98 m at 158.3 deg (27 % over the bath's length: under the
# reading's 30 % misread share, still no product)
OUTLINE_UPPER = {"center": [1.4197, 2.451], "size": [2.4229, 0.9765], "rotation_deg": 158.296}


def _turned_bath(outline: dict = OUTLINE) -> dict:
    """What the old rule left: the 1.80 x 0.80 m product at the merged outline's centre and angle (over the basin)."""
    return {"type": "bathtub", "type_method": "inferred", "status": "unverified", "front_deg": None, "inferred": True,
            "footprint": {"center": list(outline["center"]), "size": [1.8, 0.8],
                          "rotation_deg": outline["rotation_deg"]},
            "drawn_footprint": dict(outline), "drawn_type": "unknown",
            "adjusted_by_ai": {"by": "code", "rule": "ai_member", "reason": "the nearest real product inside it",
                               "changed": {"footprint": dict(outline)}}}


def _seated_ok(bath: dict, b: dict) -> None:
    """On the window wall and along it, a real product, inside the room, clear of the basin and the toilet."""
    fp = bath["footprint"]
    assert round(fp["rotation_deg"]) % 180 == 0 and bath["front_deg"] == 270.0
    assert math.isclose(fp["center"][1] + fp["size"][1] / 2.0, D, abs_tol=1e-3)            # its back on the wall
    assert sizes.fits("bathtub", fp["size"], 0.0)
    assert Polygon(_rect(fp)).difference(Polygon(b["rooms"][0]["polygon"]).buffer(0.011)).area < 1e-6
    for other in b["furniture"]:
        if other is not bath and other["type"] in ("washbasin", "toilet"):
            assert _cut(bath, other) == 0.0, other["id"]


# --------------------------------------------------------------------------
# The rules on their own
# --------------------------------------------------------------------------

def test_a_merged_outline_seats_the_product_on_its_wall_in_the_corner_beside_the_basin():
    b = _bathroom({})
    basin, toilet = b["furniture"][:2]
    got = FS.seat("bathtub", OUTLINE, b["rooms"][0]["polygon"], [_rect(basin["footprint"]), _rect(toilet["footprint"])])
    fp = got["footprint"]
    # the largest product of the 1.61 m run between the basin and the east wall (real06: 1.55 m, a column there)
    assert fp["size"] == [1.6, 0.75] and fp["rotation_deg"] == 0.0 and got["front_deg"] == 270.0
    assert fp["center"] == [round(0.4994 + 0.531 / 2 + FS.CLEAR_M + 0.8, 4), D - 0.375]    # beside the basin
    assert got["walls"] == [1, 2] and got["drawn_share"] > 0.9                              # its corner, on the outline
    assert "merged" in got["reason"] and "in a corner" in got["reason"]
    # nothing seats a product where the outline is not: an outline in the middle of a large room
    far = room_building(6.0, 6.0, "bathroom")
    assert FS.seat("bathtub", {"center": [3.0, 3.0], "size": [2.5, 1.0], "rotation_deg": 20.0},
                   far["rooms"][0]["polygon"]) is None


def test_a_fixture_on_a_wall_slides_along_it_and_a_free_standing_one_does_not():
    room = [[0, 0], [3, 0], [3, 2], [0, 2]]
    basin = {"center": [1.0, 1.775], "size": [0.6, 0.45], "rotation_deg": 0.0}           # back on the north wall
    wc = _rect({"center": [1.45, 1.65], "size": [0.4, 0.7], "rotation_deg": 0.0})
    dx, dy, dist = FS.slide(basin, room, [wc])
    assert dy == 0.0 and dx < 0 and dist <= FS.MOVE_MAX_M                                  # along the wall, away
    moved = dict(basin, center=[basin["center"][0] + dx, basin["center"][1]])
    assert FS.cut_depth(_rect(moved), wc) == 0.0
    assert FS.slide({"center": [1.5, 1.0], "size": [0.6, 0.45], "rotation_deg": 0.0}, room, [wc]) is None


def test_the_weaker_reading_gives_way():
    basin = {"id": "a", "type": "washbasin", "status": "verified", "type_method": "ai_two_pass",
             "footprint": {"center": [0, 0], "size": [0.53, 0.34], "rotation_deg": 0}}
    bath = {"id": "b", "type": "bathtub", "status": "unverified", "type_method": "inferred",
            "footprint": {"center": [0, 0], "size": [1.8, 0.8], "rotation_deg": 0}, "drawn_footprint": dict(OUTLINE)}
    assert FS.gives_way(basin, bath) is bath and FS.gives_way(bath, basin) is bath
    twin = dict(basin, id="c", footprint={"center": [0, 0], "size": [0.6, 0.45], "rotation_deg": 0})
    assert FS.gives_way(basin, twin) is basin                                                # a tie: the smaller
    counter = {"id": "k", "type": "kitchen_counter", "footprint": basin["footprint"]}
    sink = dict(basin, type="sink_kitchen")
    assert FS.hosted_pair(sink, counter) and not FS.fixture_pair(sink, counter)


# --------------------------------------------------------------------------
# The reading: the AI-named member is seated; a turned bath over its basin is seated by fix_fixed
# --------------------------------------------------------------------------

def test_the_bath_the_ai_passes_named_is_seated_in_its_merged_outline_not_turned_over_the_basin():
    b = _bathroom(_untyped_outline())
    props = INF.ai_named_members(b)
    assert [(p["piece_id"], p["type"]) for p in props] == [("f_L0_003", "bathtub")]
    assert "seated" in props[0]["reason"] and "centre and rotation kept" not in props[0]["reason"]
    out = INF.apply_inferences(b, props)
    bath = out["furniture"][2]
    _seated_ok(bath, out)
    assert bath["drawn_footprint"] == OUTLINE and bath["adjusted_by_ai"]["by"] == "code"
    assert bath["adjusted_by_ai"]["changed"]["front_deg"] is None
    assert bath["adjusted_by_ai"]["crop"] == "recognition/crops/sym_5_ctx.png"


@pytest.mark.parametrize("outline", [OUTLINE, OUTLINE_UPPER])
def test_fix_fixed_seats_a_turned_bath_left_over_its_basin_and_keeps_the_earlier_record(outline):
    b = _bathroom(_turned_bath(outline))
    bath, basin = b["furniture"][2], b["furniture"][0]
    assert _cut(bath, basin) > 0.2                                                          # the run's clash
    build = ProjectBuild(b)
    assert RD.fix_fixed(build, {}) == ["f_L0_003"]
    _seated_ok(bath, b)
    assert basin["footprint"]["center"] == [0.4994, 2.5961] and "adjusted_by_ai" not in basin   # the basin stays
    label = bath["adjusted_by_ai"]
    assert label["rule"] == RD.FIXED_RULE and label["rules"] == ["ai_member", RD.FIXED_RULE]
    assert "on f_L0_001 (washbasin)" in label["reason"] and "seated" in label["reason"]
    assert label["changed"]["footprint"] == outline                                         # the earliest kept
    assert bath["drawn_footprint"] == outline


def test_two_drawn_fixtures_that_cut_each_other_the_weaker_slides_along_its_wall():
    b = room_building(3.0, 2.0, "bathroom", furniture=[("toilet", (1.45, 1.65), 0.0, (0.4, 0.7)),
                                                       ("washbasin", (1.0, 1.775), 0.0, (0.6, 0.45), "unverified")])
    wc, basin = b["furniture"]
    wc["type_method"], basin["type_method"] = "ai_two_pass", "inferred"
    assert _cut(wc, basin) > FS.CLASH_M
    build = ProjectBuild(copy.deepcopy(b))
    assert RD.fix_fixed(build, {}) == ["f_L0_002"]
    wc2, basin2 = build.building["furniture"]
    assert wc2["footprint"] == wc["footprint"] and _cut(wc2, basin2) == 0.0
    assert basin2["footprint"]["center"][1] == 1.775 and basin2["footprint"]["rotation_deg"] == 0.0   # on its wall
    assert math.dist(basin2["footprint"]["center"], basin["footprint"]["center"]) <= RD.MOVE_MAX_M
    assert "along its wall" in basin2["adjusted_by_ai"]["reason"]
    # the build's resolver does the same (F5): along the wall, never off it
    res = CL.resolve(copy.deepcopy(b))
    assert res["left"] == [] and [(x["id"], x["action"]) for x in res["fixed"]] == [("f_L0_002", "moved")]


# --------------------------------------------------------------------------
# The build (F5), the architect's move and Argus
# --------------------------------------------------------------------------

def _fitted(bath: dict) -> dict:
    bath["asset"] = {"library": "lib", "asset_id": "tub1", "method": "library", "scaling": "uniform",
                     "fit_scale": [1.1811, 1.1811, 1.1811], "bbox_m": [1.8, 0.87, 0.435]}
    return bath


def test_the_build_resolver_seats_a_turned_bath_and_its_model_follows_the_new_size():
    b = _bathroom(_fitted(_turned_bath()))
    res = CL.resolve(b)
    assert res["left"] == []
    assert [(x["id"], x["other"], x["action"]) for x in res["fixed"]] == [("f_L0_003", "f_L0_001", "seated")]
    bath = b["furniture"][2]
    _seated_ok(bath, b)
    assert bath["adjusted_by_ai"]["rule"] == "architect F5" and bath["adjusted_by_ai"]["previous"][0]["rule"] == \
        "ai_member"
    k = bath["footprint"]["size"][0] / 1.8
    assert bath["asset"]["fit_scale"] == [round(1.1811 * k, 4)] * 3                   # the model has the new length
    assert bath["asset"]["bbox_m"][0] == bath["footprint"]["size"][0]
    assert bath["asset"]["refit"]["from_size"] == [1.8, 0.8]
    assert CL.remaining(b["furniture"]) == []


def test_argus_turns_a_clash_left_into_a_move_decision_and_the_move_seats_the_bath():
    b = _bathroom(_turned_bath())
    rep = {"findings": [{"line": "process", "check": "P3", "severity": "major", "target": "F5:f_L0_001",
                         "message": "the architect's question F5 (clashing furniture) is open for f_L0_001: f_L0_001 "
                                    "(washbasin) and f_L0_003 still overlap 0.33 m: no free place within the move "
                                    "limits"}],
           "unmatched_warnings": ["furniture clash left: f_L0_003 and f_L0_001 overlap 0.33 m"]}
    decisions = AI.clash_decisions(rep, b)
    assert [(d["action"], d["element"], d["value"]) for d in decisions] == [("move_piece", "f_L0_003", "f_L0_001")]
    assert decisions[0]["aid"] == "c:F5:f_L0_003" and decisions[0]["finding"]["check"] == "P3"
    plan = AA.Plan(copy.deepcopy(b))
    ok, text = AA.act_move_piece(plan, "AI.move_piece:f_L0_003", {"by": "argus"}, "f_L0_003", "f_L0_001")
    assert ok, text
    bath = next(f for f in plan.b["furniture"] if f["id"] == "f_L0_003")
    _seated_ok(bath, plan.b)
    assert bath["adjusted_by_ai"]["by"] == "architect" and "seated" in bath["adjusted_by_ai"]["reason"]
    # the warning is a known kind now (a recurring kind gets its rule): major, geometry
    assert PR.classify("furniture clash left: f_L0_003 and f_L0_001 overlap 0.33 m")[:3] == \
        ("clash_left", "major", "geometry")
