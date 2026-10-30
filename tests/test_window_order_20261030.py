"""30 Oct 2026, lessons UL210 and UL211 (the user on real06 run 20261029-100801-full: "Big windows next to small windows
not making any sense needs better solution", "This window all the way to the edge of a wall not making any sense needs
better solution"): one facade, one window language (``wenart.blender.window_order``). Pure tests on a small house;
real06 and real04 are only the test cases."""
import copy

from wenart.audit import kinds as K
from wenart.blender import architect_actions as AA
from wenart.blender import looks as LK
from wenart.blender import model_review as MR
from wenart.blender import parametric as P
from wenart.blender import shell as SH
from wenart.blender import window_order as WO

T = 0.25


def _wall(wid, a, b, lid="L0", t=T, exterior=True):
    return {"id": wid, "level_id": lid, "start": list(a), "end": list(b), "thickness": t, "height": 2.85,
            "exterior": exterior}


def _win(oid, x, width, sill, height, wall="w_n", lid="L0", y=6.0, **kw):
    return dict({"id": oid, "type": "window", "level_id": lid, "wall_id": wall, "center": [x, y], "width": width,
                 "sill_height": sill, "height": height, "assumed": ["height", "sill_height"]}, **kw)


def _house(lid="L0", elevation=0.0):
    """A 10 x 6 m house: a bathroom (x < 5) and a bedroom behind a 0.1 m partition, the north facade on y = 6."""
    walls = [_wall("w_s", (0, 0), (10, 0), lid), _wall("w_e", (10, 0), (10, 6), lid), _wall("w_n", (10, 6), (0, 6), lid),
             _wall("w_w", (0, 6), (0, 0), lid), _wall("w_p", (5, 0), (5, 6), lid, 0.1, False)]
    rooms = [{"id": "r_bath", "level_id": lid, "room_type": "bathroom",
              "polygon": [[0.125, 0.125], [4.95, 0.125], [4.95, 5.875], [0.125, 5.875]]},
             {"id": "r_bed", "level_id": lid, "room_type": "bedroom",
              "polygon": [[5.05, 0.125], [9.875, 0.125], [9.875, 5.875], [5.05, 5.875]]}]
    levels = [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.85}]
    if lid != "L0":
        levels.append({"id": lid, "elevation": elevation, "ceiling_height": 2.85})
    return {"levels": levels, "walls": walls, "rooms": rooms, "openings": [], "furniture": []}


def _pair(**kw):
    """The bathroom's window over its basin (H2 raised it to a 1.25 m sill) 0.2 m from the bedroom's window."""
    b = _house(**kw)
    lid = b["walls"][0]["level_id"]
    b["openings"] = [
        _win("o_bath", 4.55, 0.7, 1.25, 0.85, lid=lid, drawn_sill_height=0.9, drawn_height=1.2,
             adjusted_by_ai={"by": "architect", "reason": "a bathroom window over the basin: sill 0.90 -> 1.25 m"}),
        _win("w_bed", 5.85, 1.5, 0.9, 1.2, lid=lid)]
    b["furniture"] = [{"id": "f_basin", "type": "vanity", "level_id": lid, "room_id": "r_bath",
                       "footprint": {"center": [4.55, 5.6], "size": [0.8, 0.45], "rotation_deg": 0.0}}]
    return b


def test_side_by_side_windows_take_one_sill_and_one_head_with_a_fixed_lower_light():
    b = _pair()
    assert [sorted(g["ids"]) for g in WO.groups(b)] == [["o_bath", "w_bed"]]
    found, _n = WO.review(b)
    assert [f["kind"] for f in found] == ["staggered_windows"]
    recs = WO.compose(b)
    by = {o["id"]: o for o in b["openings"]}
    bath, bed = by["o_bath"], by["w_bed"]
    assert (bath["sill_height"], bath["height"]) == (0.9, 1.2) == (bed["sill_height"], bed["height"])
    # the basin keeps its 1.25 m behind a fixed satin lower light; the wet room's glass is satin, the bedroom's clear
    assert bath["lower_light"]["at_m"] == 1.25 and bath["lower_light"]["glass"] == "satin"
    assert bath["glass"] == "satin" and bed.get("glass") is None and "lower_light" not in bed
    assert bath["drawn_sill_height"] == 0.9 and bath["window_group"]["was"] == [1.25, 2.1]
    assert {r["id"] for r in recs if r["action"] == "lines"} == {"o_bath"}
    assert sorted(bath["composition"]) == sorted(bed["composition"]) == ["o_bath", "w_bed"]
    assert WO.review(b)[0] == []
    # idempotent
    again = copy.deepcopy(b)
    assert WO.compose(again) == [] and again == b


def test_the_documents_keep_their_lines_and_the_review_names_the_pair():
    b = _pair()
    b["openings"][1]["sill_height_source"] = "the north elevation"
    recs = WO.compose(b)
    assert {r["action"] for r in recs} == {"kept"} and b["openings"][0]["sill_height"] == 1.25
    assert WO.review(b)[0][0]["kind"] == "staggered_windows"


def test_an_upper_storey_window_lowered_with_its_group_keeps_a_guarding_lower_light():
    b = _house("L1", 3.0)
    b["openings"] = [_win("w_stair", 4.6, 0.7, 0.3, 1.8, lid="L1", guard={"top_m": 1.1, "kind": "balustrade"}),
                     _win("w_bed", 5.85, 1.5, 0.9, 1.2, lid="L1")]
    WO.compose(b)
    bed = {o["id"]: o for o in b["openings"]}["w_bed"]
    assert (bed["sill_height"], bed["height"]) == (0.3, 1.8)
    assert bed["lower_light"]["at_m"] == WO.GUARD_SILL_M and bed["lower_light"]["glass"] == "glass"


def test_a_window_that_would_keep_too_little_glass_stays():
    b = _pair()
    b["furniture"].append({"id": "f_robe", "type": "wardrobe", "level_id": "L0", "room_id": "r_bed",
                           "footprint": {"center": [5.85, 5.6], "size": [1.6, 0.6], "rotation_deg": 0.0}})
    b["openings"][1].update(sill_height=1.25, height=0.85)
    b["openings"][0].update(sill_height=0.9, height=1.2)
    recs = WO.compose(b)
    assert any(r["id"] == "w_bed" and r["action"] == "kept" for r in recs)


def test_a_window_at_the_outer_corner_moves_away_from_it():
    b = _house()
    b["openings"] = [_win("w_corner", 9.55, 0.7, 0.9, 1.2)]             # its frame 0.08 m from the corner
    found, _n = WO.review(b, "scandinavian")
    assert [f["kind"] for f in found] == ["window_at_corner"]
    recs = WO.piers(b, "scandinavian")
    o = b["openings"][0]
    assert recs[0]["action"] == "moved" and o["drawn_center"] == [9.55, 6.0]
    gap = 10.125 - (o["center"][0] + 0.35 + WO.frame_extra("scandinavian"))
    assert abs(gap - WO.PIER_MIN_M) < 1e-3 and o["corrected_by_ai"]["rule"] == WO.RULE_PIER
    assert WO.review(b, "scandinavian")[0] == []


def test_a_window_in_a_recess_or_an_inner_corner_keeps_its_place():
    b = _house()
    # a 1.2 m recess in the north facade, 0.3 m deep, the window filling its back
    b["walls"] = [w for w in b["walls"] if w["id"] != "w_n"] + [
        _wall("w_n1", (10, 6), (6.2, 6)), _wall("w_r1", (6.2, 6), (6.2, 5.7)), _wall("w_rb", (6.2, 5.7), (5.0, 5.7)),
        _wall("w_r2", (5.0, 5.7), (5.0, 6)), _wall("w_n2", (5.0, 6), (0, 6))]
    b["openings"] = [_win("w_rec", 5.6, 1.2 - T, 0.9, 1.2, wall="w_rb", y=5.7)]
    assert WO.piers(b) == [] and WO.review(b)[0] == []


def _corner_room(b):
    b["walls"].append(_wall("w_p2", (8.8, 0), (8.8, 6), "L0", 0.1, False))     # a small room in the corner
    b["rooms"][1]["polygon"] = [[5.05, 0.125], [8.75, 0.125], [8.75, 5.875], [5.05, 5.875]]
    b["rooms"].append({"id": "r_wc", "level_id": "L0", "room_type": "wc",
                       "polygon": [[8.85, 0.125], [9.875, 0.125], [9.875, 5.875], [8.85, 5.875]]})
    return b


def test_a_window_the_partition_stops_narrows_from_the_corner_side():
    b = _corner_room(_house())
    b["openings"] = [_win("w_wc", 9.375, 0.95, 1.3, 0.8)]                   # from the partition to the corner
    recs = WO.piers(b)
    o = b["openings"][0]
    assert recs[0]["action"] in ("narrowed", "moved") and WO.MIN_WIDTH_M <= o["width"] < 0.95
    lo, hi = o["center"][0] - o["width"] / 2.0, o["center"][0] + o["width"] / 2.0
    assert lo >= 8.85 - 1e-6                                                  # never into the partition or past it
    assert 10.125 - (hi + WO.frame_extra(None)) >= WO.PIER_MIN_M - 1e-3
    # a window too small to give up its width stays, with its reason (the review still reports it)
    b2 = _corner_room(_house())
    b2["openings"] = [_win("w_wc", 9.55, 0.6, 1.3, 0.8)]
    b2["walls"][-1].update(start=[9.2, 0], end=[9.2, 6])
    b2["rooms"][-1]["polygon"] = [[9.25, 0.125], [9.875, 0.125], [9.875, 5.875], [9.25, 5.875]]
    recs = WO.piers(b2)
    assert recs[0]["action"] == "kept" and b2["openings"][0]["width"] == 0.6
    assert WO.review(b2)[0][0]["kind"] == "window_at_corner"


def test_a_corner_window_of_a_drawn_pair_narrows_and_keeps_its_mullion_gap():
    b = _house()
    # a pair drawn 2.6 cm apart, the first one's frame at the corner: it cannot move into its partner, it narrows
    b["openings"] = [_win("w_a", 9.6, 1.0, 0.9, 1.2), _win("w_b", 8.474, 1.2, 0.9, 1.2)]
    recs = WO.piers(b)
    a, bb = b["openings"]
    assert [r["action"] for r in recs] == ["narrowed"] and bb["center"] == [8.474, 6.0]
    assert abs((a["center"][0] - a["width"] / 2.0) - 9.1) < 1e-6                 # the far jamb as drawn
    assert abs(10.125 - (a["center"][0] + a["width"] / 2.0 + WO.frame_extra(None)) - WO.PIER_MIN_M) < 1e-3
    assert a["drawn_width"] == 1.0 and WO.review(b)[0] == []
    assert WO.piers(b) == []                                                       # idempotent


def test_a_window_the_architect_widens_keeps_its_pier():
    b = _house()
    b["walls"][1]["thickness"] = 0.1                                                # a thin east wall
    b["rooms"][1]["polygon"] = [[5.05, 0.125], [9.95, 0.125], [9.95, 5.875], [5.05, 5.875]]
    b["openings"] = [_win("w_bed", 8.6, 1.0, 0.9, 1.2)]            # its widening reaches the corner
    done = AA.apply_answers(b, {"L1:r_bed": {"option": "enlarge_windows", "by": "architect"}})
    o = b["openings"][0]
    assert done[0]["ok"] and o["width"] > 1.0 and WO.LESSON_PIER in done[0]["change"]
    assert 10.05 - (o["center"][0] + o["width"] / 2.0 + WO.frame_extra(None)) >= WO.PIER_MIN_M - 1e-3
    assert o["window_pier"]["rule"] == WO.RULE_PIER and o["drawn_width"] == 1.0


def test_the_product_builds_a_transom_and_a_satin_lower_light():
    parts, rec = P.window_product_parts({"material": "painted_metal_white"}, 1.1, 1.2, 0.25, sill=0.9,
                                        transom_at=0.35, glass_keys=("satin", "satin"))
    assert any(p["role"] == "transom" for p in parts)
    glass = [p for p in parts if p["role"] == "glass"]
    assert glass and {p["key"] for p in glass} == {"satin"}
    assert rec["product"]["lower_light"]["transom_m"] == 0.35 and rec["product"]["glass"] == "satin"
    plain, rec2 = P.window_product_parts({"material": "painted_metal_white"}, 1.1, 1.2, 0.25, sill=0.9)
    assert "lower_light" not in rec2["product"] and {p["key"] for p in plain if p["role"] == "glass"} == {"glass"}
    low = P.fixed_light_parts(None, 1.1, 0.35, 0.25, -1, "satin")
    assert [p["key"] for p in low if p["role"] == "glass"] == ["satin"]

    class Mat:
        def __init__(self, name):
            self.name = name
    _v, _f, mats, _i = SH.opening_parts_mesh(glass, {"glass": Mat("glass"), "satin": Mat("satin_glass")}, (0, 0, 0), 0)
    assert [m.name for m in mats] == ["satin_glass"]


def test_a_window_of_a_composition_is_the_real_product_and_the_review_knows_m36():
    assert LK.window_geometry_m10({"window_frame": {"material": "upvc"}}, {"composition": ["a", "b"]})
    assert "M36" in MR.CHECKS and K.CHECK_KIND["M36"] == "no_sense"
    assert WO.PIER_MIN_M == 0.40 and WO.GROUP_GAP_M == 0.60
    assert "shower" in WO.SEE_THROUGH_TYPES and "shower" in AA.WALL_BACKED_TYPES     # glass: never a blocker
