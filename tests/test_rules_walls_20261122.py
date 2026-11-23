"""Wall pieces (22 Nov 2026, the user's "start on the wall split and invented walls", lesson UL366):
``wenart.ingest.generic.wall_pieces``. A block of wall material (a piece no longer than 1.5 x its thickness) is part of
the wall that runs into it; one wall on one line is one wall. Each must-not-fire case is a real short wall the rule
keeps. Pure: building dicts in building metres."""
from __future__ import annotations

import copy

from shapely.ops import unary_union

from wenart.ingest.generic import wall_pieces as WP


def _w(wid, s, e, t, **kw):
    d = {"id": wid, "level_id": "L0", "start": list(s), "end": list(e), "thickness": t, "height": 2.7,
         "exterior": False, "status": "verified", "evidence": [{"method": "vector", "rule": "face_pairs"}]}
    d.update(kw)
    return d


def _b(walls, openings=()):
    return {"walls": list(walls), "openings": list(openings), "rooms": []}


def _ids(b):
    return sorted(w["id"] for w in b["walls"])


def _area(b):
    return unary_union([WP.rect(w) for w in b["walls"]]).area


def _wall(b, wid):
    return next(w for w in b["walls"] if w["id"] == wid)


# --- the block test --------------------------------------------------------------------------------------------------

def test_block_is_short_against_its_thickness():
    assert WP.is_block(_w("a", (0, 0), (0.25, 0), 0.335))          # a junction square
    assert WP.is_block(_w("a", (0, 0), (0.29, 0), 0.10))           # shorter than 0.30 m
    assert not WP.is_block(_w("a", (0, 0), (0.60, 0), 0.20))       # 3 x its thickness: a wall run
    assert not WP.is_block(_w("a", (0, 0), (0.45, 0), 0.25))       # a short wall of 0.45 m stays a wall


# --- what folds ------------------------------------------------------------------------------------------------------

def test_junction_square_goes_to_the_wall_running_into_it():
    """swiss-b1074 L0: a vertical wall changes from 0.17 to 0.22 m where a 0.23 m wall meets it from the side; the
    junction square (0.335 x 0.25 m) was a wall of its own. The side wall runs on through it, the material is kept."""
    b = _b([_w("lower", (10.28, 9.73), (10.28, 10.331), 0.17),
            _w("upper", (10.304, 10.581), (10.304, 13.086), 0.22),
            _w("square", (10.362, 10.331), (10.362, 10.581), 0.335),
            _w("side", (10.53, 10.461), (12.33, 10.461), 0.23)])
    before = _area(b)
    notes = WP.fold_blocks(b)
    assert [n["walls"][0] for n in notes] == ["square"]
    assert "square" not in _ids(b)
    assert _wall(b, "side")["start"][0] < 10.21                    # runs on to the square's far face
    assert abs(_area(b) - before) < 0.02 * 0.25 * 0.335 + 0.005
    gone = b["walls_merged"][0]
    assert gone["merged_into"] == "side" and gone["corrected_by_ai"]["rule"] == WP.RULE_FOLD
    assert _wall(b, "side")["folded_blocks"][0]["id"] == "square"


def test_step_between_two_offset_walls_goes_to_both():
    """swiss-b1074 L0 [10.22, 9.591]-[10.22, 9.731]: a 0.14 m step where a wall jogs 6 cm sideways: both walls run
    into it and together cover it."""
    b = _b([_w("below", (10.157, 7.981), (10.157, 9.591), 0.155),
            _w("step", (10.22, 9.591), (10.22, 9.731), 0.28),
            _w("above", (10.28, 9.731), (10.28, 10.331), 0.17)])
    WP.fold_blocks(b)
    assert _ids(b) == ["above", "below"]
    assert _wall(b, "below")["end"][1] > 9.72 and _wall(b, "above")["start"][1] < 9.60


def test_block_inside_a_crossing_wall_goes():
    b = _b([_w("long", (0, 0), (5, 0), 0.30), _w("dup", (2.0, -0.10), (2.0, 0.10), 0.12)])
    notes = WP.fold_blocks(b)
    assert _ids(b) == ["long"] and "inside long" in notes[0]["text"]
    assert _wall(b, "long")["end"] == [5, 0]


def test_column_inside_a_wall_band_joins_the_wall():
    """A column no thicker than the wall, between two pieces of it: the wall runs on through it (one wall)."""
    b = _b([_w("a", (0, 0), (3.0, 0), 0.20), _w("col", (3.0, 0), (3.2, 0), 0.20), _w("b", (3.2, 0), (6.0, 0), 0.20)])
    WP.fold_blocks(b)
    WP.merge_collinear(b)
    assert len(b["walls"]) == 1 and b["walls"][0]["start"] == [0.0, 0.0] and b["walls"][0]["end"] == [6.0, 0.0]


# --- what must not fold ----------------------------------------------------------------------------------------------

def test_pilaster_beside_a_wall_stays():
    b = _b([_w("wall", (0, 0), (5, 0), 0.20), _w("pilaster", (2.5, 0.10), (2.5, 0.30), 0.30)])
    assert WP.fold_blocks(b) == [] and "pilaster" in _ids(b)


def test_protruding_column_in_a_wall_line_stays():
    b = _b([_w("a", (0, 0), (3.0, 0), 0.20), _w("col", (3.0, 0), (3.4, 0), 0.40), _w("b", (3.4, 0), (6.0, 0), 0.20)])
    assert WP.fold_blocks(b) == [] and "col" in _ids(b)


def test_free_standing_column_stays():
    b = _b([_w("wall", (0, 0), (5, 0), 0.20), _w("col", (2.0, 2.0), (2.3, 2.0), 0.30)])
    assert WP.fold_blocks(b) == [] and "col" in _ids(b)


def test_return_at_a_jamb_stays():
    """A wall end turning at a door jamb: the 0.25 m return stands across the wall, its extension does not cover it."""
    b = _b([_w("wall", (0, 0), (3.0, 0), 0.10), _w("return", (2.95, 0.05), (2.95, 0.30), 0.10),
            _w("far", (3.9, 0), (6.0, 0), 0.10)],
           [{"id": "d1", "level_id": "L0", "type": "door", "wall_id": "wall", "center": [3.45, 0.0], "width": 0.9,
             "status": "verified"}])
    assert WP.fold_blocks(b) == [] and "return" in _ids(b)


def test_pier_between_two_openings_stays():
    b = _b([_w("a", (0, 0), (2.0, 0), 0.20), _w("pier", (2.9, 0), (3.2, 0), 0.20), _w("b", (4.1, 0), (6.0, 0), 0.20)],
           [{"id": "w1", "level_id": "L0", "type": "window", "wall_id": "a", "center": [2.45, 0.0], "width": 0.9,
             "status": "verified"},
            {"id": "w2", "level_id": "L0", "type": "window", "wall_id": "b", "center": [3.65, 0.0], "width": 0.9,
             "status": "verified"}])
    assert WP.fold_blocks(b) == [] and "pier" in _ids(b)


def test_block_holding_an_opening_stays():
    b = _b([_w("a", (0, 0), (3.0, 0), 0.30), _w("nub", (3.0, 0), (3.3, 0), 0.30)],
           [{"id": "o", "level_id": "L0", "type": "window", "wall_id": "nub", "center": [3.15, 0], "width": 0.2}])
    assert WP.fold_blocks(b) == []


def test_block_thinner_than_a_sliver_is_never_covered_by_its_slivers():
    """swiss-b745 L0: a 0.26 m jog 4 cm thick between two thin walls is a real short wall."""
    b = _b([_w("v1", (0.06, 3.0), (0.06, 4.17), 0.04), _w("jog", (0.09, 4.15), (0.35, 4.15), 0.04),
            _w("v2", (0.37, 4.13), (0.37, 6.0), 0.04)])
    WP.fold_blocks(b)
    assert "jog" in _ids(b)


def test_other_height_or_an_inferred_wall_never_takes_a_drawn_block():
    par = _w("par", (0, 0), (3.0, 0), 0.20, height=1.0)
    b = _b([par, _w("blk", (3.0, 0), (3.2, 0), 0.20)])
    assert WP.fold_blocks(b) == []
    inf = _w("inf", (0, 0), (3.0, 0), 0.20, status="unverified", inferred=True)
    b = _b([inf, _w("blk", (3.0, 0), (3.2, 0), 0.20)])
    assert WP.fold_blocks(b) == []


# --- one wall on one line --------------------------------------------------------------------------------------------

def test_two_pieces_on_one_line_are_one_wall_and_its_openings_follow():
    b = _b([_w("a", (0, 0), (4.0, 0), 0.20), _w("c", (4.0, 0.005), (6.0, 0.005), 0.21)],
           [{"id": "d", "level_id": "L0", "type": "door", "wall_id": "c", "center": [5.0, 0.0], "width": 0.9}])
    notes = WP.merge_collinear(b)
    assert len(notes) == 1 and _ids(b) == ["a"]
    assert _wall(b, "a")["end"] == [6.0, 0.0] and b["openings"][0]["wall_id"] == "a"
    assert b["walls_merged"][0]["corrected_by_ai"]["rule"] == WP.RULE_MERGE


def test_wall_broken_by_a_shaft_or_another_thickness_stays_two():
    b = _b([_w("a", (0, 0), (3.0, 0), 0.20), _w("c", (3.6, 0), (6.0, 0), 0.20)])
    assert WP.merge_collinear(b) == []
    b = _b([_w("a", (0, 0), (3.0, 0), 0.20), _w("c", (3.0, 0), (6.0, 0), 0.30)])
    assert WP.merge_collinear(b) == []
    b = _b([_w("a", (0, 0), (3.0, 0), 0.20), _w("c", (3.0, 0), (6.0, 0), 0.20, height=1.0)])
    assert WP.merge_collinear(b) == []
    b = _b([_w("a", (0, 0), (3.0, 0), 0.20), _w("c", (3.0, 0), (6.0, 0), 0.20, exterior=True)])
    assert WP.merge_collinear(b) == []


def test_wide_gap_bridge_of_drawn_windows_joins_the_drawn_wall():
    """swiss-b1167 L0: a 3.44 m wide gap with two drawn windows was bridged by an inferred wall next to the drawn one."""
    bridge = _w("br", (0.27, 7.16), (0.27, 10.6), 0.53, status="unverified", inferred=True,
                evidence=[{"method": "inferred", "rule": "wide_gap"}])
    wins = [{"id": f"w{i}", "level_id": "L0", "type": "window", "wall_id": "br", "center": [0.27, y], "width": 1.4,
             "status": "verified"} for i, y in ((1, 7.86), (2, 9.89))]
    b = _b([_w("drawn", (0.27, 3.99), (0.27, 7.16), 0.53), bridge], wins)
    WP.merge_collinear(b)
    assert _ids(b) == ["drawn"] and _wall(b, "drawn")["status"] == "verified"
    assert _wall(b, "drawn")["end"] == [0.27, 10.6] and {o["wall_id"] for o in b["openings"]} == {"drawn"}
    # an inferred bridge over an undrawn gap (an unverified opening as wide as it) stays apart
    b2 = _b([_w("drawn", (0.27, 3.99), (0.27, 7.16), 0.53), copy.deepcopy(bridge)],
            [{"id": "o", "level_id": "L0", "type": "opening", "wall_id": "br", "center": [0.27, 8.88], "width": 3.44,
              "status": "unverified"}])
    assert WP.merge_collinear(b2) == []


def test_other_levels_are_never_mixed():
    b = _b([_w("a", (0, 0), (3.0, 0), 0.20), dict(_w("c", (3.0, 0), (6.0, 0), 0.20), level_id="L1")])
    assert WP.merge_collinear(b) == []


def test_a_wall_read_twice_goes_but_a_thin_wall_in_a_thick_band_stays():
    """A wall run lying in a wall of its own thickness is the same wall read twice; a thin piece on the centre line of
    a thicker wall is RC14's wall_in_wall (which one is right the drawing must say: swiss-b3005 L0, a 0.115 m wall read
    inside a 0.19 m band), so it stays."""
    b = _b([_w("a", (0, 0), (5.0, 0), 0.20), _w("twice", (1.0, 0.005), (2.5, 0.005), 0.20)])
    WP.fold_blocks(b)
    assert _ids(b) == ["a"]
    b = _b([_w("thick", (5.4, 11.452), (5.88, 11.452), 0.19), _w("thin", (5.492, 11.452), (5.78, 11.452), 0.115)])
    WP.fold_blocks(b)
    assert _ids(b) == ["thick", "thin"]
    b = _b([_w("thick", (0, 0), (5.0, 0), 0.40), _w("thin", (1.0, 0.0), (3.0, 0.0), 0.12)])
    WP.fold_blocks(b)
    assert _ids(b) == ["thick", "thin"]


def test_a_sliver_along_a_thick_wall_face_goes():
    """swiss-b1074 L1: a 0.255 m sliver 6.5 cm thick along the face of a 0.30 m wall is part of it."""
    b = _b([_w("wall", (10.30, 8.0), (10.30, 10.5), 0.30), _w("sliver", (10.197, 9.116), (10.197, 9.371), 0.065)])
    WP.fold_blocks(b)
    assert _ids(b) == ["wall"]
