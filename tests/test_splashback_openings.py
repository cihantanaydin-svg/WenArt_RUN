"""CPU tests of the rule "a wall finish never covers an opening" (wenart/blender/shell.py ``wall_face_openings``,
``split_band``, ``splashback_bands``, ``splashback_plan``; 26 Oct 2026, Argus on real06: the splashback behind the
counter f_L0_032 covered the 2.9 m pass-through o_L0_001 and the door ray through it hit the tiles). The rule is
general; real06 is only the test case: a splashback is cut at every door, window, plain opening and virtual separator
of its wall with the opening's width and height range; beside an opening the band keeps its height, under a window
sill above the counter a strip stays; a band the openings cover entirely is left out (and logged)."""
import pytest

from wenart.blender import shell

CLEAR = shell.WALL_FINISH_OPENING_CLEAR


def _pieces(expected):
    """``pytest.approx`` per piece (it does not reach into nested tuples)."""
    return [pytest.approx(x) for x in expected]


def _kitchen(openings=(), walls=None, front=90.0):
    """A 4 x 3 m kitchen, its south wall on y = -0.1 (0.2 m: the face on y = 0), a 2.4 m counter against it (x 0.8 to
    3.2): the splashback band runs on y = 0 from x 0.8 to 3.2, 0.90 to 1.50 m high."""
    room = {"id": "k", "level_id": "L0", "room_type": "kitchen", "polygon": [[0, 0], [4, 0], [4, 3], [0, 3]]}
    piece = {"id": "c1", "type": "kitchen_counter", "room_id": "k", "level_id": "L0", "front_deg": front,
             "footprint": {"center": [2.0, 0.33], "size": [2.4, 0.6], "rotation_deg": 0.0}}
    if walls is None:
        walls = [{"id": "w_s", "level_id": "L0", "start": [-0.1, -0.1], "end": [4.1, -0.1], "thickness": 0.2},
                 {"id": "w_w", "level_id": "L0", "start": [-0.1, -0.1], "end": [-0.1, 3.1], "thickness": 0.2},
                 {"id": "w_far", "level_id": "L0", "start": [-0.1, 1.0], "end": [4.1, 1.0], "thickness": 0.1}]
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "rooms": [room], "furniture": [piece],
            "walls": walls, "openings": list(openings)}


def _opening(oid, kind, x, width, wall="w_s", y=-0.1, sill=None, height=None, level="L0"):
    return {"id": oid, "type": kind, "level_id": level, "wall_id": wall, "center": [x, y], "width": width,
            "sill_height": sill, "height": height}


# --------------------------------------------------------------------------
# split_band
# --------------------------------------------------------------------------

def test_split_band_cuts_every_opening_with_its_width_and_height():
    band = (0.0, 2.4, 0.9, 1.5)
    assert shell.split_band(*band, []) == [band]
    # a door in the middle: two full-height pieces beside it, the clearance off its edges
    assert shell.split_band(*band, [(1.0, 1.9, 0.0, 2.1)]) == _pieces([(0.0, 1.0 - CLEAR, 0.9, 1.5),
                                                                             (1.9 + CLEAR, 2.4, 0.9, 1.5)])
    # a window with its sill at 1.10 m above the counter: a strip stays under it
    got = shell.split_band(*band, [(0.7, 1.7, 1.1, 2.1)])
    assert got == _pieces([(0.0, 0.7 - CLEAR, 0.9, 1.5), (0.7 - CLEAR, 1.7 + CLEAR, 0.9, 1.1 - CLEAR),
                                 (1.7 + CLEAR, 2.4, 0.9, 1.5)])
    # a window from the counter top (sill 0.90): no strip under it
    assert shell.split_band(*band, [(0.7, 1.7, 0.9, 2.1)]) == _pieces([(0.0, 0.7 - CLEAR, 0.9, 1.5),
                                                                            (1.7 + CLEAR, 2.4, 0.9, 1.5)])
    # an opening wider than the band: nothing left; a sliver under the minimum piece is left out
    assert shell.split_band(*band, [(-0.25, 2.65, 0.0, 2.1)]) == []
    assert shell.split_band(*band, [(0.03, 2.4, 0.0, 2.1)]) == []
    # an opening over the band (a high window) does not touch it
    assert shell.split_band(*band, [(0.5, 1.5, 1.6, 2.4)]) == [band]


# --------------------------------------------------------------------------
# wall_face_openings
# --------------------------------------------------------------------------

def test_wall_face_openings_are_the_openings_of_the_wall_the_face_lies_on():
    ops = [_opening("o_pass", "opening", 2.0, 1.0),
           _opening("win_far", "window", 2.0, 1.0, wall="w_far", y=1.0, sill=0.9, height=1.2),   # a wall 1 m in
           _opening("d_west", "door", -0.1, 0.9, wall="w_w", y=1.5, height=2.1),                # a perpendicular wall
           _opening("win_up", "window", 2.0, 1.0, sill=0.9, height=1.2, level="L1"),             # another level
           _opening("d_east", "door", 3.4, 0.8, height=2.1),                                     # over the face's end
           _opening("d_end", "door", 3.9, 0.6, height=2.1),                                      # past the face's end
           {"id": "v1", "type": "opening", "level_id": "L0", "wall_id": None, "virtual": True,
            "line": [[1.2, 0.0], [1.6, 0.0]], "center": [1.4, 0.0], "width": 0.4}]
    b = _kitchen(ops)
    got = {o["id"]: o for o in shell.wall_face_openings(b, b["levels"][0], (0.8, 0.0), (3.2, 0.0))}
    assert set(got) == {"o_pass", "v1", "d_east"}
    assert (got["o_pass"]["t0"], got["o_pass"]["t1"]) == pytest.approx((0.7, 1.7))
    assert (got["o_pass"]["z0"], got["o_pass"]["z1"]) == pytest.approx((0.0, 2.7))   # a plain opening: full height
    assert (got["v1"]["t0"], got["v1"]["t1"], got["v1"]["type"]) == pytest.approx((0.4, 0.8, "virtual"))
    assert got["d_east"]["t0"] == pytest.approx(2.2) and got["d_east"]["z1"] == pytest.approx(2.1)
    # the band behind the counter: cut at the pass-through, the virtual separator and the door over its end
    (band,) = shell.splashback_bands(b, b["levels"][0])
    assert sorted(band["openings"]) == ["d_east", "o_pass", "v1"]
    assert band["pieces"] == _pieces([(0.0, 0.4 - CLEAR, 0.9, 1.5), (1.7 + CLEAR, 2.2 - CLEAR, 0.9, 1.5)])


# --------------------------------------------------------------------------
# splashback_bands / splashback_plan
# --------------------------------------------------------------------------

def test_a_pass_through_wider_than_the_counter_leaves_no_splashback():
    b = _kitchen([_opening("o_pass", "opening", 2.0, 3.0, height=2.1)])
    (band,) = shell.splashback_bands(b, b["levels"][0])
    assert band["openings"] == ["o_pass"] and band["pieces"] == []
    assert shell.splashback_plan(b, b["levels"][0]) == []


def test_a_window_over_the_counter_keeps_the_tiles_beside_and_under_it():
    b = _kitchen([_opening("win", "window", 2.0, 1.0, sill=1.1, height=1.0)])
    boxes = shell.splashback_plan(b, b["levels"][0])
    assert len(boxes) == 3 and all(x["cut_at"] == ["win"] and x["piece_id"] == "c1" for x in boxes)
    by_x = sorted(boxes, key=lambda x: (x["center"][0], x["center"][2]))
    left, under, right = by_x
    assert left["size"][0] == pytest.approx(0.7 - CLEAR) and left["size"][2] == pytest.approx(0.6)
    assert right["size"][0] == pytest.approx(0.7 - CLEAR)
    assert right["center"][0] == pytest.approx(3.2 - 0.35 + CLEAR / 2)
    assert under["size"][0] == pytest.approx(1.0 + 2 * CLEAR) and under["center"][0] == pytest.approx(2.0)
    assert under["center"][2] - under["size"][2] / 2 == pytest.approx(0.9)          # from the counter top ...
    assert under["center"][2] + under["size"][2] / 2 == pytest.approx(1.1 - CLEAR)  # ... to just under the sill
    for x in boxes:                                    # on the wall face, into the room, as before the cut
        assert x["center"][1] == pytest.approx(shell.SPLASHBACK["gap"] + shell.SPLASHBACK["thickness"] / 2)


def test_without_openings_the_band_is_one_box_as_before():
    b = _kitchen([_opening("d_far", "door", 2.0, 0.9, wall="w_far", y=1.0, height=2.1)])
    (box,) = shell.splashback_plan(b, b["levels"][0])
    assert box["size"] == [pytest.approx(2.4), shell.SPLASHBACK["thickness"], shell.SPLASHBACK["height"]]
    assert box["center"] == pytest.approx([2.0, 0.006, 1.2]) and box["cut_at"] == []


def test_real06_kitchen_openings_are_not_covered():
    # real06 (runs/20261026-170020-full, building_built.json, level L0): the 2.4 m counter f_L0_032 stands in front of
    # the 2.9 m pass-through o_L0_001 (w_L0_009) and the 1.95 m serving window d_L0_002 (w_L0_010, the same wall line
    # drawn twice); the sink f_L0_020 stands under the 1.45 m window o_L0_004 (sill 0.90 m) of the west wall w_L0_022
    room = {"id": "r_L0_mutfak", "level_id": "L0", "room_type": "kitchen",
            "polygon": [[0.45, 9.35], [7.0, 9.35], [7.0, 11.29], [6.0, 11.29], [6.0, 11.3], [5.7494, 11.3],
                        [5.7494, 13.8], [5.7, 13.8], [5.7, 14.3], [3.6501, 14.3], [3.65, 13.55], [3.65, 13.3],
                        [3.6, 13.3], [3.6, 11.3], [3.35, 11.3], [3.35, 13.05], [2.95, 13.05], [2.95, 13.3],
                        [0.95, 13.3], [0.95, 13.2543], [0.45, 13.2543]]}
    walls = [{"id": "w_L0_009", "level_id": "L0", "start": [0.45, 9.2], "end": [4.6, 9.2], "thickness": 0.3},
             {"id": "w_L0_010", "level_id": "L0", "start": [0.95, 9.225], "end": [3.85, 9.225], "thickness": 0.25},
             {"id": "w_L0_022", "level_id": "L0", "start": [0.325, 4.05], "end": [0.325, 13.276], "thickness": 0.25}]
    openings = [{"id": "o_L0_001", "type": "opening", "level_id": "L0", "wall_id": "w_L0_009", "center": [2.4, 9.2],
                 "width": 2.9, "height": 2.1, "sill_height": None, "assumed": ["height"], "threshold_z": 0.0},
                {"id": "d_L0_002", "type": "window", "level_id": "L0", "wall_id": "w_L0_010", "center": [2.275, 9.225],
                 "width": 1.95, "height": 1.15, "sill_height": 0.95},
                {"id": "o_L0_004", "type": "window", "level_id": "L0", "wall_id": "w_L0_022", "center": [0.325, 11.325],
                 "width": 1.45, "height": 1.2, "sill_height": 0.9}]
    furniture = [{"id": "f_L0_032", "type": "kitchen_counter", "room_id": "r_L0_mutfak", "level_id": "L0",
                  "front_deg": 90.0,
                  "footprint": {"center": [2.2259, 9.6252], "size": [2.4, 0.6], "rotation_deg": 180.0}},
                 {"id": "f_L0_020", "type": "sink_kitchen", "room_id": "r_L0_mutfak", "level_id": "L0", "height": 0.9,
                  "front_deg": 0.0,
                  "footprint": {"center": [0.7552, 11.302], "size": [1.2, 0.45], "rotation_deg": 90.0}}]
    b = {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.85}], "rooms": [room], "walls": walls,
         "openings": openings, "furniture": furniture}
    bands = {x["piece_id"]: x for x in shell.splashback_bands(b, b["levels"][0])}
    assert sorted(bands["f_L0_032"]["openings"]) == ["d_L0_002", "o_L0_001"] and bands["f_L0_032"]["pieces"] == []
    assert bands["f_L0_020"]["openings"] == ["o_L0_004"] and bands["f_L0_020"]["pieces"] == []
    assert shell.splashback_plan(b, b["levels"][0]) == []
