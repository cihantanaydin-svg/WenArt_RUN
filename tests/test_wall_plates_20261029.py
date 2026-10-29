"""29 Oct 2026 (lesson UL112, user on real06 run 20261029-100801-full: "Also includes some power sockets and light on
offs"): the wall-plate rule (wenart/blender/wall_plates.py), the model review's M25 and Argus U29 on small synthetic
rooms (CPU, pure; no Blender)."""
import copy
import json
import math
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart.agent import causes as CS
from wenart.audit import kinds as K
from wenart.audit import lessons as L
from wenart.blender import common
from wenart.blender import geom2d
from wenart.blender import model_review as MR
from wenart.blender import schemas
from wenart.blender import wall_plates as WP

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "runs" / "20261029-100801-full" / "results" / "renders" / "real06" / "building_built.json"
HW = WP.PLATE["size_m"] / 2.0


def _wall(wid, a, b, t=0.2, exterior=True):
    return {"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t, "height": 2.7,
            "exterior": exterior, "status": "verified"}


def _door(oid, wall, c, w=0.9, **kw):
    return dict({"id": oid, "type": "door", "level_id": "L0", "wall_id": wall, "center": list(c), "width": w,
                 "height": 2.1, "sill_height": 0.0, "swing_side": None, "status": "verified"}, **kw)


def _window(oid, wall, c, w=1.2, sill=0.9, h=1.2):
    return {"id": oid, "type": "window", "level_id": "L0", "wall_id": wall, "center": list(c), "width": w,
            "height": h, "sill_height": sill, "status": "verified"}


def _room(rid, rtype, poly):
    return {"id": rid, "level_id": "L0", "room_type": rtype, "polygon": [list(p) for p in poly], "status": "verified"}


def _piece(fid, room, ftype, c, size, front, h=None, rot=0.0, **kw):
    return dict({"id": fid, "level_id": "L0", "room_id": room, "type": ftype, "source": "from_documents",
                 "footprint": {"center": list(c), "size": list(size), "rotation_deg": rot}, "front_deg": front,
                 "height": h, "asset": None, "status": "verified"}, **kw)


def _building(walls, openings, rooms, furniture, decor=()):
    return {"project": {"id": "plates_test"}, "status": "ok",
            "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7, "kind": "floor"}],
            "walls": walls, "openings": openings, "rooms": rooms, "furniture": furniture, "decor": list(decor)}


def _house(door_kw=None, pieces=None, openings=None, decor=()):
    """A 6 x 4 m house (outer wall centre lines): a bedroom west of an inner wall at x = 4.0 (its door d_bed at y = 1.0,
    0.9 m), a hall east of it with the entrance d_in in the east wall; the bedroom's double bed against its west wall
    with a nightstand on each side, a window in its south wall, a wardrobe against its north wall."""
    walls = [_wall("w_s", (0, 0), (6, 0)), _wall("w_e", (6, 0), (6, 4)), _wall("w_n", (6, 4), (0, 4)),
             _wall("w_w", (0, 4), (0, 0)), _wall("w_in", (4.0, 0.1), (4.0, 3.9), 0.1, False)]
    ops = [_door("d_bed", "w_in", (4.0, 1.0), **(door_kw or {})), _door("d_in", "w_e", (6.0, 2.0)),
           _window("win_bed", "w_s", (2.0, 0.0))] + list(openings or [])
    rooms = [_room("r_bed", "bedroom", [(0.1, 0.1), (3.95, 0.1), (3.95, 3.9), (0.1, 3.9)]),
             _room("r_hall", "hall", [(4.05, 0.1), (5.9, 0.1), (5.9, 3.9), (4.05, 3.9)])]
    furniture = [_piece("f_bed", "r_bed", "bed_double", (1.1, 2.0), (2.0, 1.6), 0.0, 0.5),
                 _piece("f_ns1", "r_bed", "nightstand", (0.3, 0.95), (0.4, 0.4), 0.0, 0.55),
                 _piece("f_ns2", "r_bed", "nightstand", (0.3, 3.05), (0.4, 0.4), 0.0, 0.55),
                 _piece("f_wardrobe", "r_bed", "wardrobe", (2.0, 3.6), (1.8, 0.6), 270.0, 2.1)]
    if pieces is not None:
        furniture = pieces
    return _building(walls, ops, rooms, furniture, decor)


def _plan(b, style=None):
    return WP.plan_level(b, b["levels"][0], style)


def _of(plan, room, use=None, kind=None):
    return [p for p in plan["plates"] if p["room_id"] == room and (use is None or p["use"] == use)
            and (kind is None or p["kind"] == kind)]


# ---------------------------------------------------------------------------------------------------- switches
def test_a_switch_beside_the_door_on_the_side_with_more_free_wall_at_1_05_m():
    b = _house()
    before = copy.deepcopy(b)
    plan = _plan(b)
    assert b == before                                             # the plan never writes into the building
    (sw,) = _of(plan, "r_bed", "door")
    assert sw["kind"] == "switch" and sw["for"] == "d_bed" and sw["side"] == "latch"
    # the bedroom's face of the inner wall is x = 3.95; the door spans y 0.55 .. 1.45: 2.45 m free above, 0.45 m below
    assert sw["center"][0] == pytest.approx(3.95) and sw["center"][2] == pytest.approx(WP.HEIGHTS["switch"])
    edge = 1.0 + 0.45 + WP.CLEAR["frame_overhang"]
    assert sw["center"][1] - edge == pytest.approx(0.12, abs=1e-3)            # its centre 0.12 m from the frame
    assert 0.10 <= sw["center"][1] - edge <= 0.15
    assert sw["n"] == [-1.0, 0.0] and sw["inferred"] and "the documents give no hinge side" in sw["reason"]
    assert WP.HEIGHTS["switch"] == 1.05 and WP.HEIGHTS["socket"] == 0.30


def test_a_drawn_hinge_puts_the_switch_on_the_latch_side():
    # opening into the bedroom, hinged on the left seen from the bedroom (facing +x, the left is +y): latch below
    b = _house({"swing_side": "r_bed", "hinge_side": "left"})
    (sw,) = _of(_plan(b), "r_bed", "door")
    assert sw["center"][1] < 1.0 - 0.45 and sw["side"] == "latch" and "drawn hinge side" in sw["reason"]
    b2 = _house({"hinge": [4.0, 0.55]})                            # a hinge point at the lower jamb: latch above
    (sw2,) = _of(_plan(b2), "r_bed", "door")
    assert sw2["center"][1] > 1.45 and "drawn hinge" in sw2["reason"]


def test_a_tall_piece_beside_the_door_moves_the_switch_to_the_other_side_never_behind_it():
    pieces = _house()["furniture"] + [_piece("f_shelf", "r_bed", "bookshelf", (3.75, 2.2), (1.4, 0.35), 180.0,
                                             2.0, rot=90.0)]
    # no drawn hinge: the bookshelf leaves no free wall above the door, so the latch is assumed below it
    (sw,) = _of(_plan(_house(pieces=pieces)), "r_bed", "door")
    assert sw["center"][1] < 0.55 and sw["side"] == "latch"
    # a drawn hinge at the lower jamb, the door opening into the hall: the latch side (above) is blocked by the
    # bookshelf, so the switch goes on the hinge side, never behind the bookshelf
    (sw,) = _of(_plan(_house({"swing_side": "r_hall", "hinge": [4.0, 0.55]}, pieces=pieces)), "r_bed", "door")
    assert sw["center"][1] < 0.55 and sw["side"] == "hinge" and "f_shelf" in sw["reason"]
    # ... opening into the bedroom: the hinge side is under the open leaf, no switch there (listed, M25 finds it)
    b = _house({"swing_side": "r_bed", "hinge": [4.0, 0.55]}, pieces=pieces)
    plan = _plan(b)
    assert not _of(plan, "r_bed", "door") and any(s["for"] == "d_bed" for s in plan["skipped"])


def test_each_door_of_a_room_gets_its_switch_and_a_terrace_door_none():
    ops = [_door("d_bed2", "w_in", (4.0, 3.2), 0.8),
           _door("d_terr", "w_w", (0.0, 3.4), 0.8, guard={"kind": "balustrade"}),
           _door("d_slide", "w_s", (3.2, 0.0), 1.2, operation="sliding", glazed=True)]
    pieces = [p for p in _house()["furniture"] if p["id"] != "f_wardrobe"]
    plan = _plan(_house(pieces=pieces, openings=ops))
    assert sorted(p["for"] for p in _of(plan, "r_bed", "door")) == ["d_bed", "d_bed2"]
    # the hall's two doors: the entrance has its own switch beside it, the bedroom doors share the hall's
    hall = _of(plan, "r_hall", "door")
    assert "d_in" in {p["for"] for p in hall}
    served = {d for p in hall for d in (p.get("serves") or [p["for"]])}
    assert {"d_in", "d_bed", "d_bed2"} <= served
    ent = next(p for p in hall if p["for"] == "d_in")
    assert G.distance(ent["center"][:2], (5.9, 2.0)) < 0.45 + WP.CLEAR["frame_overhang"] + 0.15 + HW
    rec = plan["rooms"]["r_bed"]
    assert rec["switches"] == 2 and set(rec["doors"]) == {"d_bed", "d_bed2"}


def test_a_door_beside_a_jog_of_its_wall_puts_its_switch_on_the_jogged_face():
    """The face beside a door may lie a few cm further back (a thicker wall next to it): the switch goes there."""
    walls = [_wall("w_s", (0, 0), (4, 0)), _wall("w_e", (4, 0), (4, 3)), _wall("w_n", (4, 3), (0, 3)),
             _wall("w_w", (0, 3), (0, 0)), _wall("w_a", (0.1, 2.0), (1.0, 2.0), 0.1, False),
             _wall("w_b", (1.0, 2.05), (3.9, 2.05), 0.2, False)]
    ops = [_door("d_a", "w_a", (0.55, 2.0), 0.8)]
    rooms = [_room("r_a", "bedroom", [(0.1, 0.1), (3.9, 0.1), (3.9, 1.95), (1.0, 1.95), (1.0, 1.95), (0.1, 1.95)])]
    rooms[0]["polygon"] = [[0.1, 0.1], [3.9, 0.1], [3.9, 1.95], [1.0, 1.95], [1.0, 1.95], [0.1, 1.95]]
    b = _building(walls, ops, rooms, [])
    plan = _plan(b)
    (sw,) = _of(plan, "r_a", "door")
    assert sw["center"][0] > 0.95 + WP.CLEAR["frame_overhang"] and sw["center"][2] == pytest.approx(1.05)


def test_an_open_side_gets_its_switch_at_its_end_and_an_alcove_is_lit_from_its_neighbour():
    """A living room with no door, open to its hall along a separator line (no wall), gets its switch on the wall at
    the separator's end; a stair well whose only way in is a doorless opening filling its wall, with no free wall, is
    lit from the hall's switch (no M25 finding)."""
    walls = [_wall("w_s", (0, 0), (8, 0)), _wall("w_e", (8, 0), (8, 4)), _wall("w_n", (8, 4), (0, 4)),
             _wall("w_w", (0, 4), (0, 0)), _wall("w_a", (4.0, 0.1), (4.0, 2.0), 0.1, False),
             _wall("w_b", (5.5, 2.0), (5.5, 3.9), 0.1, False), _wall("w_c", (4.0, 2.0), (5.5, 2.0), 0.1, False)]
    ops = [{"id": "sep_1", "type": "opening", "level_id": "L0", "wall_id": None, "virtual": True,
            "line": [[4.0, 2.05], [4.0, 3.9]], "center": [4.0, 2.97], "width": 1.85},
           _door("d_in", "w_e", (8.0, 1.0)),
           {"id": "o_well", "type": "opening", "level_id": "L0", "wall_id": "w_c", "center": [4.75, 2.0],
            "width": 1.4, "height": 2.1, "sill_height": 0.0}]
    rooms = [_room("r_liv", "living", [(0.1, 0.1), (3.95, 0.1), (3.95, 2.05), (4.0, 2.05), (4.0, 3.9), (0.1, 3.9)]),
             _room("r_hall", "hall", [(4.05, 0.1), (7.9, 0.1), (7.9, 3.9), (5.55, 3.9), (5.55, 1.95), (4.05, 1.95)]),
             _room("r_well", "stair", [(4.05, 2.05), (5.45, 2.05), (5.45, 3.9), (4.05, 3.9)])]
    rooms[1]["polygon"] = [[4.05, 0.1], [7.9, 0.1], [7.9, 3.9], [5.55, 3.9], [5.55, 1.95], [4.05, 1.95]]
    stair = _piece("f_stair", "r_well", "stair", (4.75, 2.975), (1.4, 1.85), 0.0, 3.0)
    b = _building(walls, ops, rooms, [stair])
    plan = _plan(b)
    (sw,) = _of(plan, "r_liv", "door")
    assert sw["for"] == "sep_1" and sw["side"] == "return" and "open side" in sw["reason"]
    assert min(G.distance(sw["center"][:2], e) for e in ((4.0, 2.05), (4.0, 3.9))) <= WP.SWITCH_NEAR_M + 0.05
    assert not _of(plan, "r_well", "door")
    probs, _n = WP.review(b, plan["plates"])
    assert not [p for p in probs if p["problem"] == "no_switch"]
    hall_off = [p for p in plan["plates"] if p["room_id"] != "r_hall"]
    assert {p["target"] for p in WP.review(b, hall_off)[0] if p["problem"] == "no_switch"} == {"r_hall", "r_well"}


# ---------------------------------------------------------------------------------------------------- sockets
def test_sockets_beside_both_nightstands_of_a_double_bed_at_0_30_m():
    plan = _plan(_house())
    beds = _of(plan, "r_bed", "bed")
    assert sorted(p["side"] for p in beds) == ["left", "right"]
    ys = sorted(p["center"][1] for p in beds)
    # the nightstands span y 0.75 .. 1.15 and 2.85 .. 3.25 on the head wall x = 0.1
    assert ys[0] == pytest.approx(0.75 - WP.CLEAR["beside"] - HW, abs=1e-3)
    assert ys[1] == pytest.approx(3.25 + WP.CLEAR["beside"] + HW, abs=1e-3)
    assert all(p["center"][0] == pytest.approx(0.1) and p["center"][2] == pytest.approx(0.30) for p in beds)
    assert all("nightstand" in p["reason"] for p in beds)


def test_a_dresser_beside_the_bed_takes_its_socket_over_its_bed_end():
    pieces = [_piece("f_bed", "r_bed", "bed_double", (1.1, 2.0), (2.0, 1.6), 0.0, 0.5),
              _piece("f_ns2", "r_bed", "nightstand", (0.3, 3.05), (0.4, 0.4), 0.0, 0.55),
              _piece("f_dresser", "r_bed", "dresser", (0.35, 0.6), (0.5, 1.0), 0.0, 0.8)]
    plan = _plan(_house(pieces=pieces))
    low = min(_of(plan, "r_bed", "bed"), key=lambda p: p["center"][1])
    assert "dresser" in low["reason"] and low["center"][2] == pytest.approx(0.8 + WP.HEIGHTS["bedside_over_top"])
    assert 1.1 - 0.10 - HW - 1e-6 <= low["center"][1] <= 1.1                 # over its end by the bed
    probs, _n = WP.review(_house(pieces=pieces), plan["plates"])
    assert not [p for p in probs if p["problem"] == "bed_no_socket"]


def test_no_socket_behind_a_wardrobe_on_a_window_or_behind_a_curtain():
    curtain = {"id": "dec_c", "type": "curtain", "level_id": "L0", "room_id": "r_bed", "center": [3.2, 0.2, 0.05],
               "size": [1.0, 0.1, 2.5], "wall_point": [3.2, 0.1]}
    ops = [_window("win_low", "w_s", (3.2, 0.0), 0.6, 0.2, 2.2)]
    plan = _plan(_house(openings=ops, decor=[curtain]))
    for p in _of(plan, "r_bed"):
        x, y, z = p["center"]
        if abs(y - 3.9) < 0.01:                                    # the wardrobe's wall: x 1.1 .. 2.9, 2.1 m high
            assert not 1.1 - HW <= x <= 2.9 + HW, p
        if abs(y - 0.1) < 0.01:                                    # the south wall: windows and the curtain
            assert not (1.4 - HW <= x <= 2.6 + HW and 0.9 <= z <= 2.1), p
            assert not 2.7 - HW <= x <= 3.7 + HW, p
    walls = _of(plan, "r_bed", "wall")
    assert 1 <= len(walls) <= WP.FREE_WALL_MAX["bedroom"]
    probs, _n = WP.review(_house(openings=ops, decor=[curtain]), plan["plates"])
    assert not [p for p in probs if p["problem"] in ("on_glass", "in_opening", "behind_piece")]


def _kitchen():
    walls = [_wall("w_s", (0, 0), (5, 0)), _wall("w_e", (5, 0), (5, 4)), _wall("w_n", (5, 4), (0, 4)),
             _wall("w_w", (0, 4), (0, 0))]
    ops = [_door("d_k", "w_s", (4.3, 0.0), 0.9), _window("win_k", "w_n", (2.25, 4.0), 0.4, 1.0, 1.0)]
    rooms = [_room("r_kit", "kitchen", [(0.1, 0.1), (4.9, 0.1), (4.9, 3.9), (0.1, 3.9)])]
    furniture = [_piece("f_run", "r_kit", "kitchen_counter", (2.5, 3.6), (4.0, 0.6), 270.0, 0.9),
                 _piece("f_hob", "r_kit", "stove", (1.0, 3.6), (0.6, 0.6), 270.0, 0.9),
                 _piece("f_sink", "r_kit", "sink_kitchen", (3.6, 3.6), (0.8, 0.6), 270.0, 0.9),
                 _piece("f_fridge", "r_kit", "fridge", (4.6, 3.6), (0.6, 0.6), 270.0, 2.0)]
    return _building(walls, ops, rooms, furniture)


def test_the_kitchen_row_sits_on_the_splashback_over_the_worktop_clear_of_the_hob_and_the_sink():
    b = _kitchen()
    plan = _plan(b)
    row = _of(plan, "r_kit", "worktop")
    assert row and all(p["kind"] in WP.SOCKET_KINDS for p in row)
    for p in row:
        x, y, z = p["center"]
        hw = p["width_m"] / 2.0
        assert z == pytest.approx(0.9 + WP.HEIGHTS["worktop_over"]) and 0.15 <= z - 0.9 <= 0.20
        assert p["standoff_m"] == pytest.approx(0.010)            # on the 8 mm splashback tiles, 2 mm off the wall
        assert y == pytest.approx(3.9 - 0.010)
        assert x - hw >= 1.3 + WP.CLEAR["hob"] - 1e-6 or x + hw <= 0.7 - WP.CLEAR["hob"] + 1e-6   # the hob
        assert x + hw <= 3.2 - WP.CLEAR["sink"] + 1e-6 or x - hw >= 4.0 + WP.CLEAR["sink"] - 1e-6  # the sink
        assert not 2.05 - hw <= x <= 2.45 + hw                      # the window over the worktop
        assert 0.5 <= x - hw and x + hw <= 4.5                      # over the worktop, never the fridge
    assert len(row) <= WP.CLEAR["kitchen_max"]
    assert "socket_double" in {p["kind"] for p in row}
    assert not [p for p in WP.review(b, plan["plates"])[0] if p["severity"] != "minor"]


def test_a_module_run_holds_its_built_in_sink_and_hob_and_its_hood_never_blocks_the_row():
    b = _kitchen()
    plan_m = {"builder": "kitchen_run", "worktop_m": 0.9, "modules": [
        {"kind": "base_unit", "size_m": [4.0, 0.6, 0.76], "pos_m": [0.0, 0.0], "z_m": 0.1},
        {"kind": "worktop", "size_m": [4.0, 0.6, 0.04], "pos_m": [0.0, 0.0], "z_m": 0.86},
        {"kind": "hood", "size_m": [0.6, 0.5, 1.3], "pos_m": [-1.5, 0.05], "z_m": 1.55}],
        "built_ins": [{"id": "f_sink", "kind": "sink", "x_m": 1.1, "w_m": 0.8},
                      {"id": "f_hob", "kind": "hob", "x_m": -1.5, "w_m": 0.6}]}
    run = dict(b["furniture"][0], asset={"method": "module", "module_plan": plan_m})
    sink = dict(b["furniture"][2], asset={"method": "module", "module_plan": {"built_into": "f_run", "kind": "sink"}})
    b["furniture"] = [run, sink]
    # the run's own x axis along +x (rotation 0): its sink at x 2.5 + 1.1 = 3.6, its hob at 2.5 - 1.5 = 1.0
    assert WP.piece_boxes(sink) == [] and len(WP.piece_boxes(run)) == 3
    hood = WP.piece_boxes(run)[2]
    assert hood[0]["center"][0] == pytest.approx(1.0) and hood[1:] == (1.55, pytest.approx(2.85))
    row = _of(_plan(b), "r_kit", "worktop")
    assert row
    for p in row:
        x, hw = p["center"][0], p["width_m"] / 2.0
        clear_of_sink = x + hw <= 3.2 - WP.CLEAR["sink"] + 1e-6 or x - hw >= 4.0 + WP.CLEAR["sink"] - 1e-6
        assert x - hw >= 1.3 + WP.CLEAR["hob"] - 1e-6 and clear_of_sink


def test_the_bathroom_socket_beside_the_mirror_at_1_20_m_outside_the_shower_zone():
    walls = [_wall("w_s", (0, 0), (3, 0)), _wall("w_e", (3, 0), (3, 2.5)), _wall("w_n", (3, 2.5), (0, 2.5)),
             _wall("w_w", (0, 2.5), (0, 0))]
    ops = [_door("d_b", "w_n", (1.0, 2.5), 0.8)]
    rooms = [_room("r_bath", "bathroom", [(0.1, 0.1), (2.9, 0.1), (2.9, 2.4), (0.1, 2.4)])]
    furniture = [_piece("f_basin", "r_bath", "washbasin", (1.5, 0.325), (0.6, 0.45), 90.0, 0.85),
                 _piece("f_shower", "r_bath", "shower", (2.45, 0.55), (0.9, 0.9), 90.0, 2.0)]
    mirror = {"id": "dec_m", "type": "mirror", "level_id": "L0", "room_id": "r_bath", "wall_point": [1.5, 0.1],
              "center": [1.5, 0.12], "size": [0.6, 0.03], "bottom_m": 1.1}
    plan = _plan(_building(walls, ops, rooms, furniture, [mirror]))
    (s,) = _of(plan, "r_bath", "mirror")
    assert s["center"][2] == pytest.approx(1.20) and s["center"][0] < 1.2                # the side away from the shower
    shower = furniture[1]["footprint"]
    assert WP._point_rect_distance(s["center"][:2], shower) >= WP.CLEAR["wet_zone"]
    assert s["for"] == "dec_m" and "mirror" in s["reason"]


def test_a_desk_socket_under_its_top_and_a_tv_pair_beside_the_unit():
    walls = [_wall("w_s", (0, 0), (5, 0)), _wall("w_e", (5, 0), (5, 4)), _wall("w_n", (5, 4), (0, 4)),
             _wall("w_w", (0, 4), (0, 0))]
    ops = [_door("d_l", "w_s", (4.3, 0.0), 0.9)]
    rooms = [_room("r_liv", "living", [(0.1, 0.1), (4.9, 0.1), (4.9, 3.9), (0.1, 3.9)])]
    furniture = [_piece("f_desk", "r_liv", "desk", (2.5, 3.6), (1.2, 0.6), 270.0, 0.75),
                 _piece("f_tv", "r_liv", "tv_unit", (0.3, 1.8), (1.6, 0.4), 0.0, 0.5, rot=90.0)]
    plan = _plan(_building(walls, ops, rooms, furniture))
    (desk,) = _of(plan, "r_liv", "desk")
    assert 1.9 + HW <= desk["center"][0] <= 3.1 - HW and desk["center"][1] == pytest.approx(3.9)
    assert desk["center"][2] == pytest.approx(0.30) and "under its top" in desk["reason"]
    (tv,) = _of(plan, "r_liv", "tv")
    assert tv["kind"] == "socket_double" and tv["width_m"] == pytest.approx(WP.PLATE["double_w_m"])
    assert tv["center"][0] == pytest.approx(0.1) and not 1.0 - 0.0765 < tv["center"][1] < 2.6 + 0.0765
    probs, _n = WP.review(_building(walls, ops, rooms, furniture), plan["plates"])
    assert not [p for p in probs if p["problem"] == "behind_piece"]


def test_a_hall_gets_one_socket_and_the_counts_stay_realistic():
    plan = _plan(_house())
    assert len(_of(plan, "r_hall", "hall")) == 1
    bed = plan["rooms"]["r_bed"]
    assert bed["switches"] == 1 and 3 <= bed["sockets"] <= 2 + WP.FREE_WALL_MAX["bedroom"]
    sockets = [p for p in _of(plan, "r_bed") if p["kind"] in WP.SOCKET_KINDS and p["use"] == "wall"]
    for a in sockets:                                              # never one every 50 cm
        for c in _of(plan, "r_bed"):
            if c is not a and c["kind"] in WP.SOCKET_KINDS:
                assert G.distance(a["center"][:2], c["center"][:2]) >= WP.CLEAR["spacing"] - 1e-6


def test_the_finish_follows_the_style_family():
    assert WP.finish_of({"family": "scandinavian"})["plate"] == "painted_wood_white"
    assert WP.finish_of(None)["colour"] == "white"
    assert WP.finish_of({"family": "industrial"})["plate"] == "steel_brushed"
    assert WP.finish_of({"family": "Modern Minimal"})["name"] == "matte black"
    assert WP.plan_level(_house(), _house()["levels"][0], {"wall_plates": "off"})["plates"] == []


# ---------------------------------------------------------------------------------------------------- the look
def _normal(verts, f):
    return geom2d.face_normal(verts, f)


def test_the_plates_are_real_products_with_outward_faces():
    for kind in ("switch", "socket", "socket_double"):
        verts, faces, slots = WP.plate_mesh(kind)
        assert len(faces) == len(slots) and set(slots) <= {0, 1} and all(len(f) >= 3 for f in faces)
        xs, ys, zs = zip(*verts)
        width = WP.PLATE["double_w_m"] if kind == "socket_double" else WP.PLATE["size_m"]
        assert max(xs) - min(xs) == pytest.approx(width) and max(zs) - min(zs) == pytest.approx(0.082)
        assert 0.0 < min(ys) and max(ys) <= WP.PLATE["depth_m"] + 0.0041          # proud of the wall, 9 mm
        front = [f for f in faces if all(abs(verts[i][1] - WP.PLATE["depth_m"]) < 1e-9 for i in f)]
        assert front and all(_normal(verts, f)[1] > 0.99 for f in front)          # the front faces into the room
        for f in faces:                                                            # sides outwards (the body)
            n = _normal(verts, f)
            assert math.isclose(math.sqrt(sum(c * c for c in n)), 1.0, abs_tol=1e-6)
    _v, faces, slots = WP.plate_mesh("socket")
    assert slots.count(1) >= 2                                     # the two pin holes in the dark insert
    assert 1 not in WP.plate_mesh("switch")[2]                     # the switch: plate and rocker, one finish
    _v, _f, s_black = WP.plate_mesh("socket", WP.finish_of({"family": "modern minimal"}))
    assert s_black.count(1) > slots.count(1)                       # a black plate's well in the dark insert


def test_a_level_is_one_mesh_on_its_walls():
    plan = _plan(_house())
    verts, faces, slots = WP.level_mesh(plan["plates"], plan["finish"])
    assert len(faces) == len(slots) and len(verts) < 120 * len(plan["plates"])
    sw = next(p for p in plan["plates"] if p["kind"] == "switch" and p["room_id"] == "r_bed")
    one, _f, _s = WP.plate_mesh("switch")
    k = [p["id"] for p in plan["plates"]].index(sw["id"])
    start = sum(len(WP.plate_mesh(p["kind"])[0]) for p in plan["plates"][:k])
    placed = verts[start:start + len(one)]
    # the bedroom's face x = 3.95, the room at x < 3.95: every vertex between the wall face and 13 mm into the room
    assert all(3.95 - 0.0135 <= x < 3.95 for x, _y, _z in placed)


class _Mat:
    def __init__(self, name):
        self.name = name


class _Lib:
    def __init__(self):
        self.calls = []

    def get(self, slug, asset=None, colour=None, **kw):
        self.calls.append((slug, colour))
        return _Mat(slug)

    def textured(self, mat):
        return False


def test_the_builder_makes_one_object_per_level_and_records_every_plate(monkeypatch):
    made = []

    class _Ob:
        def __init__(self, name):
            self.name = name

    def fake(name, verts, faces, *, collection, wenart_id, kind, status, materials=(), face_material_indices=None):
        assert kind in common.KINDS and kind in schemas.WHOLE_BUILDING_KINDS
        made.append((name, len(verts), len(faces), kind, status, list(materials), len(face_material_indices)))
        return _Ob(name)

    monkeypatch.setattr(common, "new_mesh_object", fake)
    b = _house()
    plan = _plan(b, {"family": "industrial"})
    manifest, assumed, lib = [], [], _Lib()
    name = WP.build_wall_plates(plan, b["levels"][0], None, lib, manifest, assumed)
    assert name == "wall_plates_L0" and len(made) == 1                     # all plates: one object
    assert made[0][3] == "wall_plate" and made[0][4] == "assumed" and made[0][2] == made[0][6]
    assert lib.calls[0] == ("steel_brushed", None) and lib.calls[1][0] == WP.INSERT_MATERIAL
    (rec,) = manifest
    assert rec["detail"] == "wall_plates" and len(rec["plates"]) == len(plan["plates"]) and rec["inferred"]
    assert "parent" not in rec                                              # not a design detail of one element
    assert len(assumed) == len(plan["plates"])
    assert all(a["kind"] == "wall_plate" and a["parent"] in ("r_bed", "r_hall") and a["reason"].startswith("inferred")
               for a in assumed)
    assert WP.plates_of({"objects": manifest}) == rec["plates"]
    assert WP.build_wall_plates({"plates": []}, b["levels"][0], None, lib, [], []) is None


# --------------------------------------------------------------------------------------------- M25 and U29
def test_m25_finds_a_room_without_a_switch_a_plate_on_glass_or_behind_a_wardrobe_and_a_bed_without_a_socket():
    b = _house()
    plates = _plan(b)["plates"]
    assert WP.review(b, plates)[0] == []
    no_switch = [p for p in plates if not (p["room_id"] == "r_bed" and p["kind"] == "switch")]
    got = WP.review(b, no_switch)[0]
    assert [(p["problem"], p["severity"], p["target"]) for p in got] == [("no_switch", "major", "r_bed")]
    sock = next(p for p in plates if p["use"] == "wall" and p["room_id"] == "r_bed")
    on_glass = dict(sock, center=[2.0, 0.1, 1.5], u=[1.0, 0.0], n=[0.0, 1.0], standoff_m=0.0)   # the window
    behind = dict(sock, center=[2.0, 3.9, 0.3], u=[-1.0, 0.0], n=[0.0, -1.0], standoff_m=0.0)  # the wardrobe
    got = WP.review(b, [p for p in plates if p is not sock] + [on_glass])[0]
    assert [(p["problem"], p["severity"]) for p in got] == [("on_glass", "critical")]
    got = WP.review(b, [p for p in plates if p is not sock] + [behind])[0]
    assert [(p["problem"], p["severity"], p["piece"]) for p in got] == [("behind_piece", "major", "f_wardrobe")]
    no_bed = [p for p in plates if p["use"] != "bed"]
    no_bed = [p for p in no_bed if not (p["use"] == "wall" and p["center"][0] < 1.0)]
    got = [p for p in WP.review(b, no_bed)[0] if p["problem"] == "bed_no_socket"]
    assert [(p["severity"], p["target"]) for p in got] == [("major", "f_bed")]
    one_side = [p for p in plates if not (p["use"] == "bed" and p["side"] == "left")]
    got = [p for p in WP.review(b, one_side)[0] if p["problem"] == "bed_no_socket"]
    assert [(p["severity"], p["target"]) for p in got] == [("minor", "f_bed")]
    # a double bed in a corner needs a socket on its free side only
    corner = _house(pieces=[_piece("f_bed", "r_bed", "bed_double", (1.1, 0.9), (2.0, 1.6), 0.0, 0.5)])
    assert WP.bed_sides(WP._room_ctx(WP._level_ctx(corner, corner["levels"][0]), corner["rooms"][0]),
                        corner["furniture"][0], [])["need"] == 1


def test_m25_in_the_model_review_reads_the_scene_and_an_older_scene_has_no_switches():
    b = _house()
    plan = _plan(b)
    scene = {"objects": [{"detail": "wall_plates", "kind": "wall_plate", "plates": plan["plates"]}]}
    got, n = MR.wall_plates_review(b, scene)
    assert got == [] and n == 2
    old, _n = MR.wall_plates_review(b, {"objects": []})
    assert {f["metrics"]["problem"] for f in old} >= {"no_switch", "bed_no_socket"}
    assert all(f["check"] == "M25" and f["owner"] == "build" and f["metrics"]["lesson"] == "UL112" for f in old)
    planned, _n = MR.wall_plates_review(b, None)                   # no scene: the plan's plates
    assert planned == []
    rec = MR.review(b, {"objects": []}, {"whole": False})
    assert "M25" in MR.CHECKS and rec["checks"]["M25"]["status"] == "ok" and rec["checks"]["M25"]["failed"] >= 2
    glass = dict(plan["plates"][0], center=[2.0, 0.1, 1.5], u=[1.0, 0.0], n=[0.0, 1.0], room_id="r_bed")
    bad, _n = MR.wall_plates_review(b, {"objects": [{"detail": "wall_plates", "plates": plan["plates"] + [glass]}]})
    assert [f.get("kind") for f in bad if f["metrics"]["problem"] == "on_glass"] == ["no_sense"]
    assert K.CHECK_KIND["M25"] == "taste" and K.kind_of({"check": "M25", "line": "model"}) == "taste"
    assert CS.CHECK_CAUSE["M25"] == "wall_plates" and CS.REPORT_TO["wall_plates"] == "build"
    assert "wall_plates" in CS.NO_TOOL_REASON and "wall_plates" in CS.CAUSES


def test_u29_finds_the_rooms_without_plates_in_the_scene():
    b = _house()
    man = {"objects": []}
    got = L.wall_plates(b, man)
    assert got and all(f["check"] == "U29" and f["line"] == "lessons" and f["evidence"]["lesson"] == "UL112"
                       for f in got)
    assert {f["kind"] for f in got} == {"taste"}
    plan = _plan(b)
    built = {"objects": [{"detail": "wall_plates", "kind": "wall_plate", "plates": plan["plates"]}]}
    assert L.wall_plates(b, built) == []
    behind = dict(next(p for p in plan["plates"] if p["use"] == "wall"), center=[2.0, 3.9, 0.3], u=[-1.0, 0.0],
                  n=[0.0, -1.0], room_id="r_bed")
    bad = L.wall_plates(b, {"objects": [{"detail": "wall_plates", "plates": plan["plates"] + [behind]}]})
    assert [(f["kind"], f["evidence"]["problem"]) for f in bad] == [("no_sense", "behind_piece")]
    assert L.CHECK_LESSONS["U29"] == ("UL112",) and K.CHECK_KIND["U29"] == "taste"
    res = L.audit(b, man)
    assert res["checked"]["U29"] == len(got)
    assert L.audit(b, None)["checked"]["U29"] == "no scene manifest: not run"


# ------------------------------------------------------------------------------------------ the real house
@pytest.mark.skipif(not REAL06.is_file(), reason="the real06 run 20261029-100801-full is not in this checkout")
def test_the_real06_house_gets_a_sensible_set():
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    plan = WP.plan(b, {"family": "scandinavian"})
    rooms = plan["rooms"]
    assert all(r["switches"] >= 1 for r in rooms.values() if r["doors"])
    assert rooms["r_L0_mutfak"]["outlets"] >= 2 and rooms["r_L1_ebeveyn_y_odasi"]["sockets"] >= 2
    assert 20 <= len(plan["plates"]) <= 60
    probs, _n = WP.review(b, plan["plates"])
    assert not [p for p in probs if p["severity"] == "critical"]


def test_lesson_ul112_is_built():
    data = json.loads((ROOT / "wenart" / "blender" / "architect_lessons.json").read_text(encoding="utf-8"))
    x = next(x for x in data["lessons"] if x["id"] == "UL112")
    assert x["status"] == "built" and x["checks"] == ["build"] and "M25" in x["lesson"] and "U29" in x["lesson"]
