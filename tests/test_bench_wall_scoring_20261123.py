"""The dataset bench's fair wall scoring (23 Nov 2026; user queue: "first a separate fix of the bench's wall scoring").

Each fault of the first bench scorer has a small hand-made case with both sides: the correct reading is no longer
counted wrong, and the real error is still counted (once). The gate's ``score.match_walls`` is not changed (checked).
"""
from __future__ import annotations

import pytest
from shapely.geometry import box

from wenart.datasets import bench as BE
from wenart.reading_check import score as SC


def _w(a, b, t=0.2, **kw):
    return {"start": list(a), "end": list(b), "thickness": t, **kw}


def _counted(v: dict) -> tuple[dict, dict]:
    return v["truth_class"], v["read_class"]


# --- fault 1: the longest overlap first, not the share of the shorter wall -------------------------------------------

def test_long_wall_takes_its_truth_wall_from_a_tiny_piece():
    truth = [_w((0, 0), (2.7, 0))]
    read = [_w((-0.004, 0), (2.666, 0)), _w((1.0, 0), (1.04, 0))]         # the wall (share 0.9985), a 4 cm piece
    assert SC.match_walls(truth, read) == [(0, 1)]                            # the gate's matcher: the piece (kept)
    assert BE.bench_match_walls(truth, read) == [(0, 0)]                      # the bench: the wall that reads it


def test_tiny_piece_with_the_right_thickness_does_not_hide_a_thickness_misread():
    truth = [_w((0, 0), (2.7, 0), 0.2)]
    read = [_w((0.02, 0), (2.69, 0), 0.4), _w((1.0, 0), (1.04, 0), 0.2)]     # misread at 0.40; a 4 cm piece at 0.20
    v = BE.wall_verdicts(truth, read)
    assert v["pairs"] == []
    assert v["truth_class"] == {0: "wall read with another thickness"}       # the real error, once
    assert v["thick"] == [(0, 0)] and 0 not in v["read_class"]


def test_wall_read_twice_on_one_line_leaves_no_neighbour_unmatched():
    """b3431 L0: a line of 0.11 / 0.175 / 0.11 walls read once at 0.13 and its middle again at 0.185."""
    truth = [_w((5.62, 0), (6.19, 0), 0.11), _w((6.13, 0.025), (9.09, 0.025), 0.175), _w((9.02, 0), (9.59, 0), 0.11)]
    read = [_w((5.605, -0.01), (9.575, -0.01), 0.13), _w((6.105, 0.018), (9.085, 0.018), 0.185)]
    pairs = BE.bench_match_walls(truth, read)
    assert sorted(pairs) == [(0, 0), (1, 1)]
    v = BE.wall_verdicts(truth, read)
    assert v["truth_class"] == {2: "walls merged (read as part of a neighbouring wall on its line)"}


# --- fault 2: a match covers 30 % of the truth wall ------------------------------------------------------------------

def test_few_cm_piece_is_not_the_reading_of_a_long_wall():
    truth = [_w((7.18, 0.11), (8.6, 0.11), 0.215)]                          # b15885 L0 w_L0_008, 1.42 m
    read = [_w((7.5, 0.11), (7.556, 0.11), 0.215)]                           # a 5.6 cm piece
    assert SC.match_walls(truth, read) == [(0, 0)]                            # the gate's matcher counts it read
    v = BE.wall_verdicts(truth, read)
    assert v["pairs"] == [] and v["truth_class"] == {0: "wall missed"}       # the bench: the wall is missed


def test_wall_read_in_short_pieces_is_still_read():
    truth = [_w((0, 0), (3, 0))]
    pieces = [_w((0, 0), (0.7, 0)), _w((0.75, 0), (1.45, 0)), _w((1.5, 0), (2.2, 0)), _w((2.25, 0), (3, 0))]
    v = BE.wall_verdicts(truth, pieces)
    assert len(v["pairs"]) == 1 and v["pairs"][0][1] == 3                    # the longest piece (0.75 m, 25 %)
    assert sorted(v["read_class"].values()) == ["wall split (a piece of a drawn wall read as a wall of its own)"] * 3
    one_third = BE.wall_verdicts(truth, [_w((0, 0), (1.0, 0))])               # one piece of 33 %: read
    assert len(one_third["pairs"]) == 1


# --- fault 3: a thickness misread is one error -----------------------------------------------------------------------

def test_thickness_misread_counts_once():
    truth = [_w((0, 0), (4, 0), 0.3)]
    read = [_w((0, 0.02), (4, 0.02), 0.15)]
    old = BE.errors("p", {"levels": [{"id": "L0"}], "per_level": {"L0": {"walls": truth}}},
                    {"levels": [{"id": "L0"}], "per_level": {"L0": {"walls": read}}})
    assert [e["class"] for e in old] == ["wall read with another thickness"]
    stats, _v = BE.bench_wall_stats({"levels": [{"id": "L0"}], "per_level": {"L0": {"walls": truth}}},
                                    {"levels": [{"id": "L0"}], "per_level": {"L0": {"walls": read}}})
    assert (stats["truth"], stats["read"], stats["matched"]) == (1, 1, 0)   # still a wrong reading for F1


def test_second_piece_of_another_thickness_is_still_a_split():
    truth = [_w((0, 0), (4, 0), 0.2)]
    read = [_w((0, 0), (3, 0), 0.2), _w((3, 0), (4, 0), 0.1)]
    v = BE.wall_verdicts(truth, read)
    assert v["pairs"] == [(0, 0)] and v["thick"] == []
    assert v["read_class"] == {1: "wall split (a piece of a drawn wall read as a wall of its own)"}


# --- fault 4: a block on the drawing's wall material ----------------------------------------------------------------

def test_block_on_drawn_material_is_neither_match_nor_invented():
    truth = [_w((0, 0), (4, 0), 0.2)]                                       # listed; a column at (6, 1) is not
    material = box(-0.1, -0.1, 4.1, 0.1).union(box(5.85, 0.85, 6.15, 1.15))
    column = _w((5.85, 1.0), (6.15, 1.0), 0.3)                                # a column read as a 0.3 m block
    jog = _w((4.0, 0.0), (4.1, 0.0), 0.2)                                     # a 10 cm nub at the wall end
    stray = _w((8.0, 1.0), (8.2, 1.0), 0.2)                                   # a block where nothing is drawn
    v = BE.wall_verdicts(truth, [_w((0, 0), (4, 0), 0.2), column, jog, stray], material)
    assert v["pairs"] == [(0, 0)]
    assert set(v["read_skip"]) == {1, 2}
    assert v["read_class"] == {3: "wall invented (on no drawn wall line)"}
    v0 = BE.wall_verdicts(truth, [_w((0, 0), (4, 0), 0.2), column], None)    # no drawing: the old verdict
    assert v0["read_class"] == {1: "wall invented (on no drawn wall line)"}


def test_long_wall_on_drawn_material_is_not_a_block():
    truth = [_w((0, 0), (4, 0), 0.2)]
    material = box(-0.1, -0.1, 4.1, 0.1).union(box(5.0, 0.9, 8.0, 1.1))     # an unlisted ... long wall is listed
    read = [_w((0, 0), (4, 0), 0.2), _w((5.0, 1.0), (8.0, 1.0), 0.2)]
    v = BE.wall_verdicts(truth, read, material)
    assert v["read_class"] == {1: "wall invented (on no drawn wall line)"}   # only blocks are left to the reader


def test_truth_material_reads_the_drawn_hatches(tmp_path):
    from shapely import affinity
    from shapely.geometry import Point
    from wenart.datasets import swiss_convert as SCV
    from wenart.reading_check import truth as TR

    def row(sub, etype, poly, area_id=""):
        return {"apartment_id": "a1", "area_id": area_id, "building_id": "515151", "entity_subtype": sub,
                "entity_type": etype, "floor_id": "9001", "geometry": affinity.translate(poly, 100, 50).wkt,
                "site_id": "7", "unit_id": "u1"}
    t = 0.25
    walls = [box(0, 0, 8, t), box(0, 5 - t, 8, 5), box(0, 0, t, 5), box(8 - t, 0, 8, 5), box(3.94, t, 4.06, 5 - t)]
    rows = [row("WALL", "separator", w) for w in walls]
    rows += [row("COLUMN", "separator", box(1.8, 2.3, 2.1, 2.6)), row("DOOR", "opening", box(3.94, 2.05, 4.06, 2.95)),
             row("WINDOW", "opening", box(1.5, 0.0, 2.7, t)), row("WINDOW", "opening", box(5.0, 0.0, 6.2, t)),
             row("LIVING_ROOM", "area", box(t, t, 3.94, 5 - t), "1"), row("BEDROOM", "area", box(4.06, t, 8 - t, 5 - t), "2")]
    truth = SCV.convert_building({"9001": rows}, tmp_path, "swiss-mat", seed=3)
    mat = BE.truth_material(tmp_path / "swiss-mat", truth)
    assert set(mat) == {"L0"}
    tw = TR.positives(truth["per_level"]["L0"]["walls"])
    for w in tw:                                                              # every listed wall, less its openings
        fp = BE._footprint(w)
        assert fp.intersection(mat["L0"].buffer(0.01)).area >= 0.6 * fp.area
    x0 = min(min(w["start"][0], w["end"][0]) - w["thickness"] / 2 for w in tw)
    y0 = min(min(w["start"][1], w["end"][1]) - w["thickness"] / 2 for w in tw)
    assert mat["L0"].contains(Point(x0 + 1.95, y0 + 2.45))                   # the column the truth does not list
    assert not mat["L0"].contains(Point(x0 + 2.1, y0 + t / 2))               # the window cut is no material
    assert not mat["L0"].contains(Point(x0 + 3.0, y0 + 3.0))                 # the room is no material


# --- fault 5: overlapping truth walls are one drawn solid ------------------------------------------------------------

PARAPETS = [_w((4.165, -1.595), (12.455, -1.595), 0.11, parapet=True),     # b3431 L1: two railings overlapping
            _w((10.77, -1.55), (18.74, -1.55), 0.11, parapet=True)]


def test_reading_of_two_overlapping_parapets_counts_nothing_wrong():
    three = [_w((4.149, -1.597), (10.757, -1.597), 0.11), _w((10.757, -1.574), (12.447, -1.574), 0.155),
             _w((12.447, -1.552), (18.647, -1.552), 0.11)]
    v = BE.wall_verdicts(PARAPETS, three)
    assert sorted(v["pairs"]) == [(0, 0), (1, 2)] and set(v["read_skip"]) == {1}
    assert _counted(v) == ({}, {})
    one = [_w((4.15, -1.575), (18.7, -1.575), 0.13)]                          # the railing line read as one wall
    v1 = BE.wall_verdicts(PARAPETS, one)
    assert len(v1["pairs"]) == 1 and len(v1["truth_skip"]) == 1 and _counted(v1) == ({}, {})


def test_two_leaves_read_as_one_leaf_still_miss_the_other():
    leaves = [_w((0, 0), (5, 0), 0.10), _w((0, 0.10), (5, 0.10), 0.10)]     # a party wall: two touching leaves
    v = BE.wall_verdicts(leaves, [_w((0, 0), (5, 0), 0.10)])                  # one leaf read, the other empty
    assert v["pairs"] == [(0, 0)] and v["truth_skip"] == {}
    assert list(v["truth_class"]) == [1]                                      # counted
    both = BE.wall_verdicts(leaves, [_w((0, 0.05), (5, 0.05), 0.20)])         # the drawn solid read as one wall
    assert _counted(both) == ({}, {}) and len(both["truth_skip"]) == 2


def test_leaves_with_an_insulation_gap_are_two_walls():
    leaves = [_w((0, 0), (5, 0), 0.10), _w((0, 0.15), (5, 0.15), 0.10)]     # a 5 cm gap between the leaves
    v = BE.wall_verdicts(leaves, [_w((0, 0.075), (5, 0.075), 0.25)])          # read as one thick wall
    assert v["truth_skip"] == {} and v["read_skip"] == {}
    assert len(v["truth_class"]) == 2                                         # both leaves counted wrong


def test_gate_matcher_unchanged():
    """The gate's ``score.match_walls`` keeps its ranking (the share of the shorter wall first)."""
    truth = [_w((0, 0), (2.7, 0))]
    read = [_w((-0.004, 0), (2.666, 0)), _w((1.0, 0), (1.04, 0))]
    assert SC.match_walls(truth, read) == [(0, 1)]
    assert SC.WALL_OVERLAP_SHARE == 0.5 and SC.WALL_LATERAL_M == 0.15 and SC.WALL_THICKNESS_M == 0.05


@pytest.mark.parametrize("length,t,unlisted", [(0.29, 0.1, True), (0.31, 0.2, False), (0.40, 0.3, True),
                                               (0.45, 0.3, False)])
def test_unlisted_size_follows_the_truth(length, t, unlisted):
    assert BE.unlisted_size(_w((0, 0), (length, 0), t)) is unlisted
