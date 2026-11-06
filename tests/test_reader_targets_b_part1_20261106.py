"""6 Nov 2026 (Milestone 14, reader targets B, the part merged first for the real21 structure run): a door drawn
across a continuous wall lies on the wall its closed leaf runs along, its open leaf the line that fits the end-point
rule best (real21: bedroom doors hinged at a wall corner were put on the perpendicular wall and their closed leaves read
as windows); a small swing on a door layer is a door (real16's shower rooms); an inner wall gets a window only from a
symbol of its own (real06 C0064). The rest of reader targets B (tests/test_reader_targets_20261106.py on its branch)
merges after its review round; this file then goes into that one. CPU only."""
from __future__ import annotations

import pytest

import _real01_page as R
from wenart.ingest.generic import openings as O


def _line(a, b, layer=None, sid=None):
    st = R.stroke([a, b])
    st.layer = layer
    if sid:
        st.id = sid
    return st

# --------------------------------------------------------------------------
# A door across a continuous wall at a wall corner
# --------------------------------------------------------------------------

def test_a_door_hinged_at_a_wall_corner_lies_on_the_wall_its_closed_leaf_runs_along():
    """real21: the vertical wall runs on through the door (lintel lines across it), the horizontal wall ends at its
    face; the swing is hinged in the vertical wall 8 cm under the horizontal wall's face, the open leaf drawn from the
    hinge to the arc's end, the door block's closed leaf a line in the vertical wall 2 cm short of the arc's other end."""
    vert = R.wall((3.52, 4.0), (3.52, 8.0), t=0.1, entity="V")
    horiz = R.wall((0.0, 6.096), (3.47, 6.096), t=0.1, entity="H")
    hinge = (3.5205, 5.97)
    swing = R.arc(hinge, 0.74, 180.0, 270.0)                        # from the open (-x) to the closed (-y) position
    open_leaf = _line(hinge, (hinge[0] - 0.74, hinge[1]), "kapi")
    closed_leaf = _line((3.5205, hinge[1] - 0.018), (3.5206, hinge[1] - 0.726), "kapi")
    _walls, openings, _log, _owned = O.gaps_and_openings([vert, horiz], [swing, open_leaf, closed_leaf], "t.dxf", 1)
    doors = [o for o in openings if o.kind == "door"]
    assert len(doors) == 1
    assert doors[0].center == pytest.approx((3.52, hinge[1] - 0.37), abs=0.01)
    assert doors[0].width == pytest.approx(0.74, abs=0.01)
    assert not [o for o in openings if o.kind == "window"]


def test_a_small_swing_with_its_leaf_on_a_door_layer_is_a_door():
    """real16 L1: the shower rooms' doors draw a 0.54 m swing and its open leaf on the layer 'kapi'; the same on a
    furniture layer (a corner basin, a shelf) stays no door (0.6 m at least there)."""
    walls = [R.wall((0.0, 13.18), (8.0, 13.18), t=0.2, entity="H")]
    hinge = (4.4749, 13.1779)

    def door(layer):
        swing = R.arc(hinge, 0.54, 270.0, 180.0)                     # from the open (-y) to the closed (-x) position
        leaf = _line(hinge, (hinge[0], hinge[1] - 0.54), layer)
        swing.layer = layer
        return [swing, leaf]
    _w, openings, _l, _o = O.gaps_and_openings(walls, door("kapi"), "t.dxf", 1)
    assert [(o.kind, round(o.width, 2)) for o in openings] == [("door", 0.54)]
    _w, openings, _l, _o = O.gaps_and_openings(walls, door("TEFRIS"), "t.dxf", 1)
    assert not [o for o in openings if o.kind == "door"]


# --------------------------------------------------------------------------
# No window in an inner wall from the wall's own face lines
# --------------------------------------------------------------------------

def _box_with_inner_wall():
    walls = [R.wall((0, 0), (6, 0), t=0.25, entity="S"), R.wall((6, 0), (6, 4), t=0.25, entity="E"),
             R.wall((6, 4), (0, 4), t=0.25, entity="N"), R.wall((0, 4), (0, 0), t=0.25, entity="W"),
             R.wall((0.125, 2.0), (5.875, 2.0), t=0.15, entity="I")]
    return walls


def test_an_inner_wall_stretch_drawn_with_two_pairs_of_lines_is_no_window():
    """real06 L1 (C0064): the DUVAR pair 5 cm inside the plaster faces between a door's frame and a cross wall."""
    lines = [_line((1.0, 1.95), (1.8, 1.95), "DUVAR"), _line((1.0, 2.05), (1.8, 2.05), "DUVAR")]
    _walls, openings, log, _owned = O.gaps_and_openings(_box_with_inner_wall(), lines, "t.dxf", 1)
    assert not [o for o in openings if o.kind == "window"]
    dropped = [e for e in log if e.get("rule") == "inner_wall_faces"]
    assert dropped and "inner wall" in dropped[0]["note"] and "DUVAR" in dropped[0]["note"]


def test_an_inner_wall_window_drawn_on_a_window_layer_stays():
    lines = [_line((1.0, 1.95), (1.8, 1.95), "PENCERE"), _line((1.0, 2.05), (1.8, 2.05), "PENCERE")]
    _walls, openings, _log, _owned = O.gaps_and_openings(_box_with_inner_wall(), lines, "t.dxf", 1)
    assert [round(o.width, 2) for o in openings if o.kind == "window"] == [0.8]


def test_an_outer_wall_window_drawn_with_wall_layer_lines_stays():
    """real06's facade windows: the same two DUVAR lines in an outer wall are its window, as before."""
    lines = [_line((2.0, -0.05), (3.5, -0.05), "DUVAR"), _line((2.0, 0.05), (3.5, 0.05), "DUVAR")]
    _walls, openings, _log, _owned = O.gaps_and_openings(_box_with_inner_wall(), lines, "t.dxf", 1)
    assert [round(o.width, 2) for o in openings if o.kind == "window"] == [1.5]


def test_wall_face_layers():
    assert O.wall_face_layer("DUVAR") and O.wall_face_layer("SIVA") and O.wall_face_layer("A-WALL")
    assert not O.wall_face_layer("PENCERE") and not O.wall_face_layer("DUVAR-PENCERE")
    assert not O.wall_face_layer("A-WALL-GLAZ") and not O.wall_face_layer("0") and not O.wall_face_layer(None)


