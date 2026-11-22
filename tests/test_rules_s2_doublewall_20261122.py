"""22 Nov 2026 (the user's "build S2 and double-wall rule"): two reader rules, each with its synthetic project read end to
end through the CPU pipeline (generated into a temporary folder), its pure parts and its machine check (RC14).

- S2 (``walls.stair_edge_spans``, ``walls.split_stair_edges``): a flight's open side drawn as part of a longer thin
  wall piece is split off at the flight's ends when the same room lies on both of its sides; the parts beyond stay
  walls (synthetic-28-stair-edge-run). Check: ``sense.stair_edge_wall``.
- The double-leaf rule (``double_leaf.merge_double_leaves``, ``double_leaf.facing_gaps``): a facade drawn as two leaves
  with a cavity of at most 10 cm is one wall of their total thickness, the gaps facing each other one opening; an empty
  gap in a band just outside a facade facing its opening is that opening read again (synthetic-33-double-wall; the
  user's C0086 on real10). Check: ``sense.double_leaf_walls``.
"""
from __future__ import annotations

import copy
import math

import pytest

from wenart.ingest.generic import decisions as DEC
from wenart.ingest.generic import double_leaf as DL
from wenart.ingest.generic import walls as W
from wenart.reading_check import sense as SN
from wenart.synthetic import failure_classes as FC
from wenart.synthetic import weak_projects as WP


def _read(project, root):
    from wenart.ingest import pipeline as PL

    FC.generate_failure_project(project, root)
    building, _build = PL.run_project(root / project.name, root / f"{project.name}-out", no_ai=True)
    return building


def _score(project, root, building):
    from wenart.reading_check import score as SC
    from wenart.reading_check import truth as TR

    truth = TR.synthetic_truth(project.name, root / project.name / FC.TRUTH_FILE)
    return SC.match(truth, TR.extract(building, project=project.name), building)["total"]


@pytest.fixture(scope="module")
def root(tmp_path_factory):
    return tmp_path_factory.mktemp("rules_s2_doublewall")


# --- S2: the pure parts ----------------------------------------------------------------------------------------------

def _pair(lo, hi, o0, o1, s0=None, s1=None):
    lines = (W._Line(o0, lo if s0 is None else s0, hi if s1 is None else s1, ["a"]),
             W._Line(o1, lo if s0 is None else s0, hi if s1 is None else s1, ["b"]))
    return W._Pair("DUVAR", (1.0, 0.0), (0.0, 1.0), lo, hi, lines)


def _treads(x0, n, going, y_from, y_to):
    return [((x0 + k * going, y_from), (x0 + k * going, y_to)) for k in range(n + 1)]


def test_tread_run_span_gives_the_longest_even_run():
    assert W._tread_run_span([0.0, 0.25, 0.5, 0.75, 1.0, 3.0]) == (4, 0.0, 1.0)
    assert W._tread_run_span([0.0, 2.0]) == (0, 0.0, 0.0)


def test_a_flight_ending_on_one_face_gives_its_span_and_a_u_well_none():
    edge = _pair(0.0, 5.5, -0.10, 0.0)                     # a thin piece 0..5.5, its upper face at y = 0
    flight = _treads(0.0, 16, 0.25, 0.0, 1.0)              # treads 0..4 ending on the upper face
    assert [(p is edge, round(a, 2), round(b, 2)) for p, a, b in W.stair_edge_spans([edge], flight)] == \
        [(True, 0.0, 4.0)]
    well = flight + _treads(0.0, 16, 0.25, -0.10, -1.10)   # treads on both faces: a U stair's well
    assert W.stair_edge_spans([edge], well) == []
    thick = _pair(0.0, 5.5, -0.18, 0.0)                    # a 0.18 m wall is never an edge
    assert W.stair_edge_spans([thick], flight) == []


def _room(x0, y0, x1, y1):
    """The four walls (0.15 m pairs) of a room."""
    t = 0.15
    return [W._Pair("DUVAR", (1.0, 0.0), (0.0, 1.0), x0, x1, (W._Line(y0 - t, x0, x1, ["r"]), W._Line(y0, x0, x1, ["r"]))),
            W._Pair("DUVAR", (1.0, 0.0), (0.0, 1.0), x0, x1, (W._Line(y1, x0, x1, ["r"]), W._Line(y1 + t, x0, x1, ["r"]))),
            W._Pair("DUVAR", (0.0, 1.0), (-1.0, 0.0), y0 - t, y1 + t,
                    (W._Line(-x0, y0 - t, y1 + t, ["r"]), W._Line(-x0 + t, y0 - t, y1 + t, ["r"]))),
            W._Pair("DUVAR", (0.0, 1.0), (-1.0, 0.0), y0 - t, y1 + t,
                    (W._Line(-x1 - t, y0 - t, y1 + t, ["r"]), W._Line(-x1, y0 - t, y1 + t, ["r"])))]


def test_the_open_side_is_split_off_when_one_room_lies_on_both_sides():
    walls = _room(0.0, 0.0, 7.0, 4.4)
    edge = _pair(1.0, 7.0, 3.2, 3.3)                       # the open side from the flight's foot to the right wall
    flight = _treads(1.0, 16, 0.25, 3.3, 4.3)              # x 1..5, ending on the edge's upper face
    spans = W.stair_edge_spans([edge], flight)
    out, split = W.split_stair_edges(spans, walls + [edge], [], [(3.0, 1.5)])
    assert len(split) == 1 and split[0][0] is edge
    assert [(round(p.lo, 2), round(p.hi, 2)) for p in split[0][1]] == [(5.0, 7.0)]   # the partition beyond the flight
    assert edge not in out and len(out) == len(walls) + 1


def test_a_stair_hall_wall_with_another_room_beyond_stays():
    walls = _room(0.0, 0.0, 7.0, 4.4)
    wall = _pair(0.0, 7.0, 3.2, 3.3)                       # a wall right across the room: another room above it
    flight = _treads(1.0, 16, 0.25, 3.3, 4.3)
    out, split = W.split_stair_edges(W.stair_edge_spans([wall], flight), walls + [wall], [],
                                     [(3.0, 1.5), (6.0, 3.9)])
    assert split == [] and wall in out
    # no label at all: nothing to judge by
    assert W.split_stair_edges(W.stair_edge_spans([wall], flight), walls + [wall], [], [])[1] == []


def test_the_stair_edge_part_rule_is_registered():
    assert "stair_edge_part" in DEC.RULE_CONFIDENCE


# --- the double-leaf rule: the pure parts ----------------------------------------------------------------------------

def _wall(wid, a, b, t, ext=False):
    return {"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t, "exterior": ext,
            "status": "verified", "evidence": [{"method": "vector", "rule": "face_pairs"}]}


def _op(oid, kind, wall, c, w, **kw):
    return dict({"id": oid, "type": kind, "level_id": "L0", "wall_id": wall, "center": list(c), "width": w,
                 "status": "unverified", "evidence": [{"method": "derived", "entity": "gap:LINE:1"}]}, **kw)


def _facade_building(outer_t=0.10, cavity=0.04, outer_from=0.0, inner_len=12.0, outer_ext=True):
    """A room (y 0.34..5) behind a facade of an inner 0.20 m leaf (y 0.14..0.34) and an outer leaf below it."""
    yo = outer_from + outer_t / 2.0
    yi = outer_from + outer_t + cavity + 0.10
    return {"walls": [_wall("w_in", (0.0, yi), (inner_len, yi), 0.20, ext=False),
                      _wall("w_out", (0.0, yo), (12.0, yo), outer_t, ext=outer_ext)],
            "openings": [_op("win_a", "window", "w_in", (2.0, yi), 1.5,
                             evidence=[{"method": "vector", "rule": "size_tag", "entity": "TEXT:1"}]),
                         _op("o_b", "opening", "w_out", (2.2, yo), 1.4,
                             evidence=[{"method": "derived", "entity": "gap:LINE:2"}])],
            "rooms": [{"id": "r", "level_id": "L0", "label": "Salon", "label_raw": "SALON",
                       "polygon": [[0.0, yi + 0.10], [12.0, yi + 0.10], [12.0, 5.0], [0.0, 5.0]]}]}


def test_two_leaves_of_a_facade_are_one_wall_with_one_opening():
    b = _facade_building()
    recs = DL.merge_double_leaves(b)
    assert len(recs) == 1 and recs[0]["kind"] == "leaves"
    assert [w["id"] for w in b["walls"]] == ["w_in"] or [w["id"] for w in b["walls"]] == ["w_out"]
    w = b["walls"][0]
    assert math.isclose(w["thickness"], 0.34, abs_tol=1e-3) and math.isclose(w["start"][1], 0.17, abs_tol=1e-3)
    assert w["exterior"] is True and len(w["leaves"]) == 2
    assert [o["id"] for o in b["openings"]] == ["win_a"]                 # one opening, the better typed one
    o = b["openings"][0]
    assert o["wall_id"] == w["id"] and math.isclose(o["center"][1], 0.17, abs_tol=1e-3)
    assert math.isclose(o["center"][0], 2.2, abs_tol=1e-3)               # at the drawn gap (the tag placed it at 2.0)
    assert b["openings_merged"][0]["merged_into"] == "win_a"
    assert b["walls_merged"][0]["corrected_by_ai"]["rule"] == DL.RULE


@pytest.mark.parametrize("why, kw", [
    ("a shaft or duct: a 0.15 m gap", {"cavity": 0.15}),
    ("a fins band 0.30 m thick is no leaf", {"outer_t": 0.30}),
    ("leaves of very different lengths", {"inner_len": 4.0}),
])
def test_close_parallel_walls_that_are_not_one_wall_stay(why, kw):
    b = _facade_building(**kw)
    assert DL.merge_double_leaves(b) == [], why
    assert len(b["walls"]) == 2


def test_party_walls_with_rooms_on_both_sides_stay():
    b = _facade_building()
    b["rooms"].append({"id": "r2", "level_id": "L0", "label": "Oda", "label_raw": "ODA",
                       "polygon": [[0.0, -5.0], [12.0, -5.0], [12.0, -0.05], [0.0, -0.05]]})
    assert DL.merge_double_leaves(b) == []


def test_an_empty_gap_outside_a_facade_facing_its_window_is_that_window():
    b = _facade_building(outer_t=0.10, cavity=0.24)        # a band 0.24 m outside the facade: no leaf, a surround
    b["walls"][0]["exterior"] = True
    assert DL.merge_double_leaves(b) == []
    recs = DL.facing_gaps(b)
    assert len(recs) == 1 and recs[0]["openings"] == ["o_b", "win_a"]
    assert [o["id"] for o in b["openings"]] == ["win_a"]
    pieces = sorted((w for w in b["walls"] if w["id"].startswith("w_out")), key=lambda w: w["start"][0])
    assert [(round(w["start"][0], 2), round(w["end"][0], 2)) for w in pieces] == [(0.0, 1.5), (2.9, 12.0)]


def test_a_gap_in_one_leaf_only_keeps_what_the_reader_decided():
    b = _facade_building()
    b["openings"][1]["center"] = [8.0, b["openings"][1]["center"][1]]    # the outer gap faces nothing
    DL.merge_double_leaves(b)
    assert sorted(o["id"] for o in b["openings"]) == ["o_b", "win_a"]
    assert {o["type"] for o in b["openings"]} == {"window", "opening"}


# --- the synthetic projects end to end ---------------------------------------------------------------------------------

def test_s2_synthetic_28_reads_the_partition_and_no_wall_along_the_flight(root):
    project = WP.project_28()
    b = _read(project, root)
    ys = 4.4 - FC.INT_T / 2 - 0.05 - 1.0 - 0.05          # the partition's centre line
    on_line = [w for w in b["walls"] if w["level_id"] == "L0" and abs(w["start"][1] - ys) < 0.06
               and abs(w["end"][1] - ys) < 0.06]
    assert len(on_line) == 1
    x0, x1 = sorted((on_line[0]["start"][0], on_line[0]["end"][0]))
    assert x0 >= 5.4 - 0.05 and x1 >= 6.9                 # the partition beyond the flight's top end only
    assert not [o for o in b["openings"] if o["level_id"] == "L0" and abs(o["center"][1] - ys) < 0.1]
    assert _score(project, root, b) == 100.0
    assert SN.stair_edge_wall(b) == []


def test_double_wall_synthetic_33_reads_one_facade_one_window_one_door_and_the_shaft(root):
    project = WP.project_33()
    b = _read(project, root)
    facade = [w for w in b["walls"] if w["level_id"] == "L0" and abs(w["start"][1] - w["end"][1]) < 0.01
              and w["start"][1] < 0.4]
    assert len(facade) == 1 and abs(facade[0]["thickness"] - 0.34) <= 0.03
    on = [o for o in b["openings"] if o.get("wall_id") == facade[0]["id"]]
    assert sorted(o["type"] for o in on) == ["door", "window"]
    assert any(abs(w["start"][1] - 0.54) < 0.03 and abs(w["thickness"] - 0.10) < 0.03 for w in b["walls"])
    assert _score(project, root, b) == 100.0
    assert SN.double_leaf_walls(b) == []


def test_the_checks_flag_a_reading_without_the_rules():
    b = _facade_building()
    found = SN.double_leaf_walls({"walls": b["walls"], "openings": b["openings"], "rooms": b["rooms"]})
    assert [f["severity"] for f in found] == ["major"] and "win_a" in found[0]["element_ids"]
    # the check works on a copy: the reading is untouched
    assert len(b["walls"]) == 2 and len(b["openings"]) == 2
    flight_b = {"levels": [{"id": "L0"}],
                "walls": [_wall("w_e", (1.0, 3.25), (7.0, 3.25), 0.10)],
                "rooms": [{"id": "r_s", "level_id": "L0", "label": "Salon", "label_raw": "SALON",
                           "polygon": [[0, 0], [7, 0], [7, 3.2], [0, 3.2]]},
                          {"id": "r_x", "level_id": "L0", "label": "Oda", "label_raw": None,
                           "polygon": [[0, 3.3], [7, 3.3], [7, 4.4], [0, 4.4]]}],
                "furniture": [{"id": "f_s", "level_id": "L0", "type": "stair",
                               "stair": {"flights": [{"start": [1.0, 3.8], "end": [5.0, 3.8], "width": 1.0}]}}],
                "openings": []}
    found = SN.stair_edge_wall(copy.deepcopy(flight_b))
    assert [f["rule"] for f in found] == ["stair_edge_wall"] and "w_e" in found[0]["element_ids"]
    flight_b["rooms"][1]["label_raw"] = "MERDİVEN HOLÜ"            # a room of its own behind the flight: a wall
    assert SN.stair_edge_wall(flight_b) == []
