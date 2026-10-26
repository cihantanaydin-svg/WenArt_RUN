"""CPU tests of the camera search's fix round after the real06 run (26 Oct 2026; wenart.blender.camsearch).

Pod run 20261026-183115-full: the AI judge scored real06's bathroom views 1-2 of 5 for framing a blank wall, a door
or a corner while the toilet, shower and basins were out of the frame (cam_r_L1_banyo_3: 1/5, cam_r_L0_banyo_1 and
_2, cam_r_L1_dus_2: 2/5), and a living room view whose centre was a bare column. The rules checked here hold for
every project: the room's anchors and set (``view_set``), a piece's in-frame fraction (``box_in_frame``), the set
in the score (``anchors``), the door and bare-centre penalties (``bare_centre``), the anchor rule of the pick (no
view without one of the room's anchors inside the frame while one exists), a small room's later views adding a
piece of its set, the gain-aware later picks, and wall-hung pieces below the lens as camera obstacles
(``floor_obstacle``). A synthetic bathroom shows the Milestone 11 score picking a corner-wall view the new rules
drop; real06's three bathrooms (tests/fixtures/camsearch_real06_bathrooms_20261026.json, with the pod's cameras and
the judge's scores) are replayed.
"""
import json
import math
from pathlib import Path

import numpy as np
import pytest

from test_camsearch import _building
from wenart.blender import cameras, camsearch as C, geom2d
from wenart.blender.parametric import obstacle_rect

FIXTURE = Path(__file__).resolve().parent / "fixtures" / "camsearch_real06_bathrooms_20261026.json"


def _piece(fid, ftype, room="r", group=None, size=(0.5, 0.5), center=(1.0, 1.0), rotation=0.0, bbox=None):
    f = {"id": fid, "type": ftype, "room_id": room, "level_id": "L0", "front_deg": 0.0,
         "footprint": {"center": list(center), "size": list(size), "rotation_deg": rotation}}
    if bbox is not None:
        f["asset"] = {"method": "library", "bbox_m": list(bbox)}
    if group is not None:
        f["group"] = dict(zip(("group_id", "role"), group))
    return f


# --------------------------------------------------------------------------
# The room's anchors and set
# --------------------------------------------------------------------------

def test_view_set_takes_the_room_types_anchors_and_their_groups():
    bath = {"room_type": "bathroom"}
    pieces = [_piece("wc", "toilet"), _piece("wb", "washbasin"), _piece("sh", "shower"),
              _piece("wm", "washing_machine")]
    assert C.view_set(bath, pieces) == (["wc", "wb", "sh"], ["wc", "wb", "sh"])
    living = {"room_type": "living"}
    pieces = [_piece("so", "sofa", group=("g", "anchor")), _piece("ct", "table_coffee", group=("g", "partner")),
              _piece("ar", "armchair"), _piece("pl", "potted_plant"), _piece("tv", "tv_unit", group=("h", "partner"))]
    # the sofa and the armchair are anchors of a living room; the coffee table is in the sofa's group
    assert C.view_set(living, pieces) == (["so", "ar"], ["so", "ct", "ar"])
    # a room type without anchors of its own: the group anchors, else the pieces of the highest type weight
    other = {"room_type": "other"}
    assert C.view_set(other, [_piece("de", "desk", group=("w", "anchor")), _piece("oc", "office_chair",
                                                                               group=("w", "partner"))]) == \
        (["de"], ["de", "oc"])
    hall = {"room_type": "hall"}
    assert C.view_set(hall, [_piece("st", "stair"), _piece("co", "console_table"), _piece("pl", "potted_plant")]) == \
        (["co", "pl"], ["co", "pl"])                     # a stair is no view of a hall with something else in it
    assert C.view_set(hall, [_piece("st", "stair")]) == (["st"], ["st"])
    assert C.view_set(bath, []) == ([], [])
    # a corner sofa weighs as a sofa (it was the default 1.0, as an ottoman)
    assert C.type_weight("sofa_corner") == C.type_weight("sofa") == 3.0


def test_set_cover_by_hand():
    assert C.set_cover([1.0, 0.5, 0.0], [2.0, 2.0, 1.0]) == pytest.approx((2.0 + 1.0) / 5.0)
    assert C.set_cover([1.5, -0.2], [1.0, 1.0]) == pytest.approx(0.5)            # clamped to 0..1
    assert C.set_cover([], []) == 0.0


# --------------------------------------------------------------------------
# A piece in the frame
# --------------------------------------------------------------------------

@pytest.mark.parametrize("y0, y1, x0, x1, inside", [
    (-0.5, 0.5, 2.0, 3.0, 1.0),                   # straight ahead: wholly inside
    (-2.5, -1.5, 2.0, 3.0, 2.0 / 3.0),            # to the right: slopes 0.5 .. 1.25, the frame ends at 1.0
    (-0.5, 0.5, -3.0, -2.0, 0.0),                 # behind the camera
])
def test_box_in_frame_by_hand(y0, y1, x0, x1, inside):
    # 18 mm, no shift: the frame's slopes are a in [-1, 1] (right), b in [-0.5625, 0.5625] (up); the camera at 1.25 m
    # looks along +X (yaw 0: right = -Y); a box from 1.0 to 1.5 m high.
    bounds = C.frame_bounds(18.0, 0.0, 0.0)
    assert bounds == pytest.approx((-1.0, 1.0, -0.5625, 0.5625))
    corners = C.box_corners((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, 1.0, 1.5)
    f, r, u = C.yaw_axes([0.0])
    got, area, middle = C.box_in_frame(corners, (0.0, 0.0, 1.25), f, r, u, bounds)
    assert got[0] == pytest.approx(inside)
    if inside == 1.0:                             # a = -y / x: -0.25 .. 0.25, b = (z - 1.25) / x: -0.125 .. 0.125
        assert area[0] == pytest.approx(0.5 * 0.25 / (2.0 * 1.125)) and middle[0]
    if inside == 0.0:
        assert area[0] == 0.0 and not middle[0]
    if 0.0 < inside < 1.0:
        assert not middle[0]                      # its part in the frame (a 0.5 .. 1.0) is right of the middle third


def test_a_box_beside_the_lens_is_out_of_the_frame():
    """A piece the camera stands beside (its box from 1 m behind to 1 m ahead of the lens, 0.5 m to the right) projects
    through the near plane far outside the frame: it is not a piece in the frame, as in the render (only its front end
    shows at the edge)."""
    bounds = C.frame_bounds(18.0, 0.0, -0.1)
    corners = C.box_corners(0.0, -1.0, 2.0, 1.0, 0.0, 0.8)
    got, _area, _middle = C.box_in_frame(corners, (0.0, 0.0, 1.25), *C.yaw_axes([0.0]), bounds)
    assert got[0] < 0.1
    # turned 90 degrees towards it, the same box 2.5 m ahead is in the frame
    got, _area, _middle = C.box_in_frame(C.box_corners(0.0, -3.0, 2.0, 1.0, 0.0, 0.8), (0.0, 0.0, 1.25),
                                         *C.yaw_axes([270.0]), bounds)
    assert got[0] == pytest.approx(1.0)


# --------------------------------------------------------------------------
# The score: the set, the door, the bare centre
# --------------------------------------------------------------------------

def test_score_terms_with_the_set_the_door_and_the_centre_by_hand():
    m = {"furn": 0.25, "open": 0.12, "floor": 0.25, "wall": 0.3, "window": 0.1, "ceiling": 0.0, "near": 0.0,
         "max_single": 0.2, "d_wall": 3.0}
    base = C.score_terms(m)
    assert base["anchors"] == 0.0 and base["total"] == pytest.approx(1.0 + 1.0 + 1.0 + 1.0)
    s = C.score_terms(dict(m, anchors=2.0 / 3.0, door=0.30, centre=0.80))
    assert s["anchors"] == pytest.approx(2.0)                      # 3 x two thirds of the set
    assert s["penalties"] == pytest.approx(4.0 * 0.20 + 3.0 * 0.50)
    assert s["total"] == pytest.approx(base["total"] + 2.0 - 2.3)


def _grid_labels(rows):
    """Labels and depths of a hand-made 6 x 4 frame (cols x rows) from strings: f floor, w wall at 2 m, W wall at
    6 m, d door (code 5) at 2 m, p piece (code 6) at 2 m."""
    code = {"f": C.FLOOR, "w": C.WALL, "W": C.WALL, "d": 5, "p": 6}
    far = {"f": 1.5, "w": 2.0, "W": 6.0, "d": 2.0, "p": 2.0}
    labels = np.array([[code[c] for c in r] for r in rows]).ravel()[None, :]
    depth = np.array([[far[c] for c in r] for r in rows]).ravel()[None, :]
    return labels, depth


@pytest.mark.parametrize("rows, centre", [
    (["wwwwww", "wwwwww", "wwwwww", "ffffff"], 1.0),     # a bare wall 2 m away across the middle
    (["wwwwww", "wwwwww", "ffppff", "ffffff"], 0.0),     # a piece stands in front of it
    (["wwwwww", "wwwwww", "wwpwww", "ffffff"], 0.5),     # one of the two middle columns is bare
    (["WWWWWW", "WWWWWW", "WWWWWW", "ffffff"], 0.0),     # the wall is 6 m away: the room's depth, not a bare wall
    (["wwddww", "wwddww", "wwddww", "ffffff"], 1.0),     # a door leaf in the middle
])
def test_bare_centre_by_hand(rows, centre):
    labels, depth = _grid_labels(rows)
    assert C.bare_centre(labels, depth, (6, 4), [5])[0] == pytest.approx(centre)


def test_a_column_in_the_middle_of_the_frame_is_a_bare_centre():
    """real06's cam_r_L0_salon_1 (judge 2/5: "a large blank concrete column and wall eat the center of the frame"):
    a 0.8 m wall stub 2.5 m ahead in the middle of the frame, an armchair on either side: the middle columns see the
    stub standing on the floor; moved 1.5 m aside, the middle shows the far wall 5.5 m away (no bare centre)."""
    def room(stub_y):
        b = _building(6.0, 4.0, furniture=[("a1", "armchair", (1.0, 0.8), (0.8, 0.8), 0.0, (0.8, 0.8, 0.8)),
                                           ("a2", "armchair", (1.0, 3.2), (0.8, 0.8), 0.0, (0.8, 0.8, 0.8))])
        b["rooms"][0]["room_type"] = "living"
        b["walls"].append({"id": "w_col", "level_id": "L0", "start": [3.0, stub_y - 0.4], "end": [3.0, stub_y + 0.4],
                           "thickness": 0.3})
        return b

    plan = {"room_id": "r", "position": [5.5, 2.0, 1.25], "target": [4.5, 2.0, 1.25], "lens_mm": 18.0,
            "shift_y": C.SHIFT_Y}
    hit = C.score_camera(room(2.0), plan)
    assert hit["shares"]["centre"] > 0.45 and hit["terms"]["penalties"] > 0.4
    clear = C.score_camera(room(3.5), plan)
    assert clear["shares"]["centre"] == 0.0
    assert clear["terms"]["total"] > hit["terms"]["total"] + 0.4


def test_a_set_piece_in_the_frame_is_no_looming_edge():
    """Milestone 11's edge_near (a tall element near the lens at the frame edge: a door leaf, a wardrobe side) counts
    only the outside part of a set piece that is in the frame (the room's own shower is the subject); a door leaf
    keeps its full share."""
    b = _building(2.4, 2.9, furniture=[("sh", "shower", (1.95, 2.45), (0.9, 0.9), 270.0, (0.9, 0.9, 2.0))])
    b["rooms"][0]["room_type"] = "bathroom"
    model = C.RoomModel(b["rooms"][0], b)
    (cand,) = C.score_candidates(model, [(0.5, 1.5)], yaws=[30])
    m = cand["shares"]
    assert m["inside"]["sh"] >= C.SCORE["anchor_inside"] and m["anchors_in"] == ["sh"]
    bare = C.RoomModel(b["rooms"][0], b)
    bare.anchor_ids, bare.set_ids = [], []                  # the score before this fix round
    (old,) = C.score_candidates(bare, [(0.5, 1.5)], yaws=[30])
    assert old["shares"]["edge_near"] > 0.1
    assert m["edge_near"] == pytest.approx(old["shares"]["edge_near"] * (1.0 - m["inside"]["sh"]), abs=1e-3)


# --------------------------------------------------------------------------
# The pick
# --------------------------------------------------------------------------

def _cand(total, x, y, yaw, anchored=None, set_in=None, shown=None, blocked=False):
    c = {"total": total, "x": x, "y": y, "yaw": yaw, "blocked": blocked, "anchored": anchored,
         "shares": {"shown": shown or {}}}
    if set_in is not None:
        c["set_in"] = set_in
    return c


def test_no_view_without_an_anchor_while_one_shows_it():
    cands = [_cand(5.0, 1.0, 1.0, 0, anchored=False), _cand(3.0, 2.0, 2.0, 90, anchored=True),
             _cand(2.9, 3.0, 3.0, 180, anchored=True), _cand(4.0, 3.0, 1.0, 270, anchored=False)]
    picks, warning = C.select_views(cands, 3)
    assert [p["yaw"] for p in picks] == [90, 180] and warning is None
    # no candidate shows an anchor: the best one only, with the note (fewer views beat views of a wall)
    picks, warning = C.select_views([_cand(5.0, 1.0, 1.0, 0, anchored=False),
                                     _cand(4.0, 3.0, 1.0, 270, anchored=False)], 3)
    assert [p["yaw"] for p in picks] == [0] and warning == C.NO_ANCHOR_NOTE
    # a room without anchors (anchored None) keeps the rule of Milestone 6
    picks, _ = C.select_views([_cand(5.0, 1.0, 1.0, 0), _cand(4.0, 3.0, 1.0, 270)], 3)
    assert len(picks) == 2


def test_a_small_rooms_later_view_adds_a_piece_of_its_set():
    cands = [_cand(5.0, 1.0, 1.0, 0, True, ["wc", "sh"]), _cand(4.9, 2.0, 2.0, 120, True, ["sh"]),
             _cand(4.0, 1.0, 2.0, 240, True, ["wb", "sh"]), _cand(3.9, 2.5, 1.0, 180, True, ["wc", "wb"])]
    picks, _ = C.select_views(cands, 3, small=True)
    assert [p["yaw"] for p in picks] == [0, 240]            # 120 shows nothing new; 180 adds nothing after 240
    picks, _ = C.select_views(cands, 3, small=False)
    assert [p["yaw"] for p in picks] == [0, 120, 240]


def test_later_picks_weigh_what_they_add_to_the_set():
    w = {"bed": 3.0, "ward": 1.5}
    cands = [_cand(6.0, 1.0, 1.0, 0, True, ["bed"], {"bed": 1.0}),
             _cand(5.0, 3.0, 1.0, 90, True, ["bed"], {"bed": 1.0}),
             _cand(4.6, 1.0, 3.0, 180, True, ["bed", "ward"], {"bed": 0.8, "ward": 1.0})]
    # by score alone the second view repeats the bed; the gain (3 x 1.5 / 4.5 = 1.0) of the wardrobe view wins
    assert [p["yaw"] for p in C.select_views(cands, 2)[0]] == [0, 90]
    assert [p["yaw"] for p in C.select_views(cands, 2, weights=w)[0]] == [0, 180]
    assert C.cover_gain(cands[2], {"bed": 1.0}, w) == pytest.approx(1.5 / 4.5)
    # the drop rule weighs the gain too: 3.9 + 1.0 >= 0.7 x 6.0, 3.9 alone is below it
    low = [cands[0], dict(cands[2], total=3.9)]
    assert len(C.select_views(low, 2)[0]) == 1 and len(C.select_views(low, 2, weights=w)[0]) == 2


# --------------------------------------------------------------------------
# Camera points: a basin hung below the lens is an obstacle
# --------------------------------------------------------------------------

def test_a_basin_hung_below_the_lens_keeps_the_camera_points_away():
    """real06's cam_r_L1_banyo_3 stood over the washbasin f_L1_021 (hung at 0.15 m, 0.85 m top): wall-hung pieces were
    no floor obstacles (Milestone 10, for wall cabinets at 1.45 m). A piece hung below the lens now is; one hung at
    or above it is not."""
    basin = _piece("wb", "washbasin", size=(0.6, 0.56), center=(2.0, 3.65), bbox=(0.6, 0.56, 0.7))
    basin["mount_bottom_m"] = 0.15
    cab = _piece("wc", "wall_cabinet", size=(1.0, 0.35), center=(2.0, 3.8), bbox=(1.0, 0.35, 0.7))
    cab["mount_bottom_m"] = 1.45
    assert C.floor_obstacle(basin) and not C.floor_obstacle(cab) and C.floor_obstacle(_piece("t", "toilet"))
    plain = _building(4.0, 4.0)
    hung = _building(4.0, 4.0)
    hung["furniture"] = [dict(basin), dict(cab)]
    points, _ = C.candidate_positions(hung["rooms"][0], hung)
    rect = obstacle_rect(basin)
    assert points and all(geom2d.distance_to_rect(p, rect["center"], rect["size"], rect["rotation_deg"])
                          >= C.OBSTACLE_CLEARANCE - 1e-9 for p in points)
    assert len(points) < len(C.candidate_positions(plain["rooms"][0], plain)[0])


# --------------------------------------------------------------------------
# A synthetic bathroom: the corner-wall view of the old score is dropped
# --------------------------------------------------------------------------

def _bathroom():
    """A 2.4 x 2.9 m bathroom as real06's: the door at the west end of the south wall, a window in the north wall,
    the toilet on the east wall, a 0.9 m shower box in the north-east corner, a basin hung on the north wall."""
    b = _building(2.4, 2.9, openings=[("door", "door", "s", 0.45, 0.8, 0.0, 2.1),
                                      ("win", "window", "n", 1.1, 1.0, 1.0, 1.0)],
                  furniture=[("wc", "toilet", (2.05, 1.0), (0.45, 0.7), 270.0, (0.45, 0.74, 0.88)),
                             ("sh", "shower", (1.95, 2.45), (0.9, 0.9), 270.0, (0.9, 0.9, 2.0)),
                             ("wb", "washbasin", (0.6, 2.71), (0.53, 0.38), 0.0, (0.53, 0.38, 0.55))])
    b["rooms"][0]["room_type"] = "bathroom"
    b["furniture"][2]["mount_bottom_m"] = 0.3
    return b


def test_a_small_bathroom_gets_views_of_its_fixtures_not_of_its_walls(monkeypatch):
    b = _bathroom()
    room = b["rooms"][0]
    plans = C.plan_room(room, b)[0]
    assert plans and C.room_view_count(room, b) == 3
    for p in plans:
        s = C.score_camera(b, p)["shares"]
        assert p["anchors_in_frame"] and p["warning"] is None, p["name"]
        assert s["centre"] <= C.SCORE["penalties"]["centre"][1] and s["door"] <= C.SCORE["penalties"]["door"][1]
    assert set(plans[0]["anchors_in_frame"]) == {"sh", "wb"}
    # The score and the pick of Milestone 11 (no set term, no door and centre penalties, later views down to half
    # the best) kept a second view from the corner by the toilet: the door, a basin far off and the bare corner.
    old = C.RoomModel(room, b)
    old.anchor_ids, old.set_ids = [], []
    cands = C.score_candidates(old, C.candidate_positions(room, b)[0], lens_mm=cameras.room_lens(room)[0])
    factor, allowed = C.SCORE["penalties"]["door"]
    for c in cands:
        c["total"] += factor * max(0.0, c["shares"]["door"] - allowed)
    monkeypatch.setattr(C, "DROP_BELOW_BEST", 0.5)
    picks, _ = C.select_views(cands, 3)
    corner = [c for c in picks if C.score_camera(b, {"room_id": "r", "position": [c["x"], c["y"], 1.25],
                                                     "target": [c["x"] + math.cos(math.radians(c["yaw"])),
                                                                c["y"] + math.sin(math.radians(c["yaw"])), 1.25],
                                                     "lens_mm": 18.0, "shift_y": C.SHIFT_Y})["shares"]["centre"] >= 0.9]
    assert len(picks) == 3 and corner == [picks[1]]
    assert all(math.dist((p["position"][0], p["position"][1]), (c["x"], c["y"])) > 0.3 for p in plans for c in corner)


# --------------------------------------------------------------------------
# real06's bathrooms (pod run 20261026-183115-full)
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real06():
    building = json.loads(FIXTURE.read_text(encoding="utf-8"))
    plans = [p for level in building["levels"] for p in C.plan_level(building, level["id"])]
    return building, plans


def test_real06_bathroom_views_show_fixtures_and_together_the_whole_set(real06):
    building, plans = real06
    by_room = {}
    for p in plans:
        by_room.setdefault(p["room_id"], []).append(p)
    assert sorted(by_room) == ["r_L0_banyo", "r_L1_banyo", "r_L1_dus"]
    for room in building["rooms"]:
        model = C.RoomModel(room, building)
        views = by_room[room["id"]]
        shown = set()
        for p in views:
            s = C.score_camera(building, p)["shares"]
            assert p["anchors_in_frame"] and not p["score"]["blocked"] and p["warning"] is None, p["name"]
            assert s["centre"] <= 0.5 and s["door"] <= C.SCORE["penalties"]["door"][1], p["name"]
            shown |= set(p["set_in_frame"])
        assert shown == set(model.set_ids), room["id"]          # toilet, shower and basin; the two basins of L1


def test_real06_pod_views_of_walls_and_doors_are_not_picked(real06):
    """The pod views the judge marked for framing a wall, a door or a corner: the model sees a bare centre (0.95-1.0)
    and scores them below every new view of their room; none of them is picked again."""
    building, plans = real06
    pod = {c["name"]: c for c in building["pod_cameras"]}
    for name in ("cam_r_L0_banyo_1", "cam_r_L0_banyo_2", "cam_r_L1_dus_2", "cam_r_L1_banyo_3"):
        cam = pod[name]
        assert cam["judge_score"] <= 2, name
        old = C.score_camera(building, cam)
        assert old["shares"]["centre"] >= 0.95, name
        mine = [p for p in plans if p["room_id"] == cam["room_id"]]
        assert old["terms"]["total"] < min(p["score"]["total"] for p in mine), name
        old_yaw = math.degrees(math.atan2(cam["target"][1] - cam["position"][1], cam["target"][0] - cam["position"][0]))
        for p in mine:
            assert math.dist(p["position"][:2], cam["position"][:2]) > 0.3 or \
                C.yaw_difference(p["score"]["yaw_deg"], old_yaw) > 30.0, (name, p["name"])
    # cam_r_L1_banyo_3 stood over the basin f_L1_021 (hung below the lens): no camera point there now
    room = next(r for r in building["rooms"] if r["id"] == "r_L1_banyo")
    basin = next(f for f in building["furniture"] if f["id"] == "f_L1_021")
    rect = obstacle_rect(basin)
    points, _ = C.candidate_positions(room, building)
    assert C.mount_bottom(basin) > 0.0 and geom2d.distance_to_rect(
        pod["cam_r_L1_banyo_3"]["position"][:2], rect["center"], rect["size"], rect["rotation_deg"]) == 0.0
    assert all(geom2d.distance_to_rect(p, rect["center"], rect["size"], rect["rotation_deg"]) >= 0.2 - 1e-9
               for p in points)
