"""23 Nov 2026 (the user's C0097 and C0098 on real15; lessons UL371, UL372): a narrow 'door' onto nothing is no door,
and an empty gap's 'exterior wall' note follows the building's outline.

The cause of C0097 on the drawing: real15 L1's facade has a 0.60 x 0.30 m column (Z_kolon, hatched) where the
bedroom | bathroom partition meets it; the wall reading reads the column's material as a wall piece in the facade's
band and leaves a 0.50 m gap in the facade run beside the partition. A wardrobe block 'GARDOLAP 2' (Z_tefriş) stands
against the partition below the column; three of its rails, 0.45 m long and 4 mm apart, stand across the wall at the
gap's jamb like a door leaf opened at 90 degrees. The open-leaf rule took them for the leaf of a 0.50 m door, and the
drawn leaf kept the gap from the wall material (``_inside_wall``).

- ``openings.furniture_line`` / ``_leaf_zone``: a stroke of a block named for a piece of furniture (none of its chain
  named for a door) is never a door's leaf, opened at 90 degrees or sliding (``Gap.furniture_leaf`` says whose lines
  they were). The layer alone does not decide (real03 draws doors on a furniture layer).
- ``sense_rules.doors_onto_nothing`` (rule ``narrow_door``): an upper-storey door onto nothing narrower than any door
  (``NARROW_DOOR_M`` 0.60), with no swing, door block, window evidence or door-high tag, is no door: closed with what
  the drawing holds in its gap (``narrow_gap_content``: a column, wall material), the wall runs on. For drawings whose
  layers and blocks say nothing (a PDF, a scan).
- ``twins.lift_doors``: an inferred landing door narrower than ``LIFT_DOOR_MIN_W_M`` is not inferred (the bench's
  0.32-0.41 m doors on a shaft's short side, none drawn).
- C0098 (UL372): ``sense_rules.empty_gap_notes``: the reader's 'empty gap in an exterior wall' note follows the
  building's outline at the gap once the walls are final (rooms on both sides: an inner wall's gap); and
  ``twins.passage_case`` takes a wall flagged exterior as an inner partition where a room lies on both sides of the gap
  (``indoor_both_sides``; real15 o_L0_001, whose wall's early flag the outline rule clears later).
- Must not fire: a narrow door with a drawn swing (a WC or shaft access door), a narrow sliding door with a door-high
  tag, a pair of narrow leaves forming a wider door, a narrow window, a door leaf in a block named for a door, a narrow
  door between two rooms.
- synthetic-37-narrow-door read end to end through the CPU pipeline (generated into a temporary folder).
"""
from __future__ import annotations

import math

import pytest

from wenart.ingest import sense_rules as SR
from wenart.ingest import twins as TW
from wenart.ingest.generic import openings as O
from wenart.ingest.generic.model import Stroke
from wenart.synthetic import failure_classes as FC
from wenart.synthetic import weak_projects as WP


# --- helpers: a wall along x on y = 0 (band -t/2 .. t/2); the room is y < 0 ------------------------------------------

def _gap(a=0.0, b=0.50, t=0.30):
    return O.Gap("run", "h", 0.0, t, a, b, [])


def _line(sid, p, q, layer="0", block=None):
    return Stroke(sid, "line", [p, q], layer=layer, block=block)


def _rect(sid, x0, y0, x1, y1, layer="0", block=None):
    return Stroke(sid, "polyline", [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], closed=True, layer=layer,
                  block=block)


def _arc(sid, c, r, a0, a1, layer="KAPI"):
    pts = [(c[0] + r * math.cos(math.radians(a0 + (a1 - a0) * k / 16)),
            c[1] + r * math.sin(math.radians(a0 + (a1 - a0) * k / 16))) for k in range(17)]
    return Stroke(sid, "arc", pts, layer=layer, arc={"center": c, "radius": r, "start_deg": a0, "end_deg": a1})


def _classify(g, *strokes):
    O._classify_gap_rules(g, O.StrokeIndex(list(strokes), 0.0), set())
    return g


def _rails(x=0.0, t=0.30, length=0.45, layer="Z_tefriş", block="GARDOLAP 2"):
    """real15's wardrobe rails: three lines 4 mm apart standing across the wall at the jamb ``x``, from 5 cm inside
    the room face into the room."""
    y0 = -t / 2 - 0.05
    return [_line(f"r{k}", (x + 0.004 * k, y0), (x + 0.004 * k, y0 - length), layer, block) for k in range(3)]


# --- the furniture line ----------------------------------------------------------------------------------------------

def test_a_furniture_block_names_its_lines_a_door_block_never():
    assert O.furniture_line(_line("a", (0, 0), (1, 0), "Z_tefriş", "GARDOLAP 2")) == "GARDOLAP 2"
    assert O.furniture_line(_line("b", (0, 0), (1, 0), "0", "PLAN/YATAK_CIFT")) == "YATAK_CIFT"
    assert O.furniture_line(_line("c", (0, 0), (1, 0), "Z_tefriş", "KAPI 90")) is None        # a door block
    assert O.furniture_line(_line("d", (0, 0), (1, 0), "0", "DOLAP/KAPI_KANAT")) is None       # a door in the chain
    assert O.furniture_line(_line("e", (0, 0), (1, 0), "TEFRIS")) is None                      # a layer alone: no
    assert O.furniture_line(_line("f", (0, 0), (1, 0), "0", "BLOK_17")) is None                # a name says nothing


def test_c0097_a_wardrobes_rails_at_a_narrow_gap_are_no_door_leaf():
    g = _classify(_gap(), *_rails())
    assert g.cls != "door"
    assert g.furniture_leaf and "GARDOLAP 2" in g.furniture_leaf and "opened at 90 degrees" in g.furniture_leaf


def test_the_same_lines_on_the_door_layer_or_in_a_door_block_are_a_leaf():
    assert _classify(_gap(), *_rails(layer="KAPI", block=None)).cls == "door"
    assert _classify(_gap(), *_rails(layer="Z_tefriş", block="KAPI 50")).cls == "door"
    assert _classify(_gap(), *_rails(layer="Z_tefriş", block=None)).cls == "door"     # furniture layer, no block (real03)


def test_a_wardrobes_sliding_front_in_a_gap_is_no_sliding_door():
    leaf = _rect("s", 0.10, -0.02, 0.60, 0.02, "Z_tefriş", "GARDIROP_SURGULU")
    g = _classify(_gap(0.0, 0.9, 0.2), leaf)
    assert g.cls != "door" and "sliding" in (g.furniture_leaf or "")
    assert _classify(_gap(0.0, 0.9, 0.2), _rect("s", 0.10, -0.02, 0.60, 0.02, "KAPI")).cls == "door"


def test_must_not_fire_a_narrow_swing_and_a_pair_of_narrow_leaves():
    # a 0.50 m shaft access door with its swing (and its leaf) drawn
    g = _classify(_gap(), _arc("a", (0.0, -0.15), 0.50, 270.0, 360.0),
                  _line("l1", (0.0, -0.15), (0.0, -0.65), "KAPI"), _line("l2", (0.03, -0.15), (0.03, -0.65), "KAPI"))
    assert g.cls == "door"
    # two 0.45 m leaves opened at 90 degrees at both jambs of a 0.90 m gap: one double door
    leaves = [_line(f"p{k}", (x + dx, -0.15), (x + dx, -0.60), "KAPI") for k, (x, dx) in
              enumerate([(0.0, 0.0), (0.0, 0.04), (0.86, 0.0), (0.86, 0.04)])]
    g = _classify(_gap(0.0, 0.90), *leaves)
    assert g.cls == "door" and g.found.get("double")


# --- the building rule: a narrow door onto nothing -------------------------------------------------------------------

class _Drawn:
    """The drawing's strokes in building metres for the rule (straight pieces and arcs)."""

    def __init__(self, segments=(), arcs=()):
        self._segments, self._arcs = list(segments), list(arcs)

    def segments(self, poly):
        from shapely.geometry import Point
        return [s for s in self._segments if poly.contains(Point(((s["a"][0] + s["b"][0]) / 2,
                                                                  (s["a"][1] + s["b"][1]) / 2)))]

    def arcs(self, poly):
        return list(self._arcs)


def _upper(width=0.50, tag=None, extra_walls=()):
    """L1 at +3.00 with a facade wall on y = 0 (0.30 m) and a door of ``width`` in it."""
    ev = [{"file": "x.dwg", "method": "vector", "confidence": 0.95, "entity": "INSERT:1/15"}]
    if tag:
        ev.append({"method": "vector", "text": tag, "rule": "size_tag"})
    walls = [{"id": "w_f", "level_id": "L1", "start": [0.0, 0.0], "end": [6.0, 0.0], "thickness": 0.30,
              "exterior": True}] + list(extra_walls)
    return {"levels": [{"id": "L0", "elevation": 0.0}, {"id": "L1", "elevation": 3.0}], "walls": walls,
            "openings": [{"id": "d1", "type": "door", "level_id": "L1", "wall_id": "w_f", "center": [3.0, 0.0],
                          "width": width, "height": 2.1, "evidence": ev}], "rooms": []}


@pytest.fixture
def into_air(monkeypatch):
    from wenart.reading_check import structure as STR

    monkeypatch.setattr(STR, "doors_into_air", lambda b, shapes=None: [
        {"level_id": "L1", "element_ids": ["d1"], "place": [3.0, 0.0]}] if b.get("openings") else [])


def test_c0097_a_narrow_door_onto_nothing_is_closed_with_what_the_drawing_holds(into_air):
    column = [{"a": (2.76, -0.14), "b": (3.24, -0.14), "length": 0.48, "id": "c1", "layer": "Z_kolon"},
              {"a": (2.76, 0.14), "b": (3.24, 0.14), "length": 0.48, "id": "c2", "layer": "Z_kolon"}]
    piece = {"id": "w_col", "level_id": "L1", "start": [2.75, -0.02], "end": [3.25, -0.02], "thickness": 0.35}
    b = _upper(extra_walls=[piece])
    recs = SR.doors_onto_nothing(b, {"L1": _Drawn(column)}, {"L1": []})
    assert [r["how"] for r in recs] == ["closed"] and not b["openings"]
    gone = b["openings_merged"][0]
    assert gone["closed"] and gone["corrected_by_ai"]["rule"] == "narrow_door"
    assert "a column (Z_kolon)" in gone["corrected_by_ai"]["reason"] and "w_col" in gone["corrected_by_ai"]["reason"]


def test_must_not_fire_a_door_high_tag_a_wide_door_a_swing_or_a_window_layer(into_air):
    for b in (_upper(tag="55/210"), _upper(width=0.80)):
        recs = SR.doors_onto_nothing(b, {"L1": _Drawn()}, {"L1": []})
        assert [r["how"] for r in recs] == ["question"] and b["openings"]
    b = _upper()
    swing = {"center": (2.75, 0.0), "radius": 0.5, "ends": [(3.25, 0.0), (2.75, -0.5)], "id": "a1", "layer": "KAPI"}
    assert SR.doors_onto_nothing(b, {"L1": _Drawn(arcs=[swing])}, {"L1": []}) == [] and b["openings"]
    b = _upper()
    glass = [{"a": (2.78, 0.0), "b": (3.22, 0.0), "length": 0.44, "id": "g", "layer": "PENCERE"}]
    recs = SR.doors_onto_nothing(b, {"L1": _Drawn(glass)}, {"L1": []})
    assert [r["how"] for r in recs] == ["door to window"] and b["openings"][0]["type"] == "window"


def test_door_tag_reads_the_openings_own_tag_and_one_beside_it():
    assert SR.door_tag({"evidence": [{"text": "60/210"}]}, []) == "60/210"
    assert SR.door_tag({"evidence": [{"text": "60/150"}]}, []) is None                       # window-high
    o = {"center": [3.0, 0.0], "width": 0.5, "evidence": []}
    assert SR.door_tag(o, [{"text": "55/220", "x": 3.1, "y": 0.4}]) == "55/220"
    assert SR.door_tag(o, [{"text": "55/220", "x": 5.0, "y": 0.4}]) is None                  # another door's


# --- the inferred lift door ------------------------------------------------------------------------------------------

def _lift_case(side):
    """A lift shaft 1.2 m deep whose side towards the hall is ``side`` long (the rest of it against a bedroom)."""
    shaft = {"id": "r_asansor", "level_id": "L0", "room_type": "shaft", "label": "ASANSÖR", "label_raw": "ASANSÖR",
             "polygon": [[0.0, 0.0], [side, 0.0], [side, 1.2], [0.0, 1.2]]}
    hall = {"id": "r_hol", "level_id": "L0", "room_type": "hall", "label": "HOL",
            "polygon": [[0.0, 1.3], [4.0, 1.3], [4.0, 3.0], [0.0, 3.0]]}
    walls = [{"id": "w_s", "level_id": "L0", "start": [0.0, 1.25], "end": [4.0, 1.25], "thickness": 0.10},
             {"id": "w_b", "level_id": "L0", "start": [side + 0.05, 0.0], "end": [side + 0.05, 1.2], "thickness": 0.10}]
    return [shaft, hall], walls


def test_no_landing_door_narrower_than_a_door_is_inferred():
    rooms, walls = _lift_case(0.45)
    openings, review = [], []
    notes = TW.lift_doors(rooms, openings, walls, review=review)
    assert not openings and any("too short" in n for n in notes)
    assert review and review[0]["kind"] == "lift_door_too_narrow"
    rooms, walls = _lift_case(1.6)                       # a real shaft side: the door as before
    openings = []
    TW.lift_doors(rooms, openings, walls)
    assert [round(o["width"], 2) for o in openings] == [0.9]


# --- C0098: the exterior note and the passage rule --------------------------------------------------------------------

def _two_rooms(note=SR.EMPTY_EXTERIOR_NOTE, flag=False):
    """Two rooms (0..3 and 3..6 by 0..4) inside four outer walls, the partition on x = 3 with an empty 0.85 m gap; and
    an empty 0.80 m gap in the outer wall on y = 0 noted as nothing."""
    t, ti = 0.30, 0.15
    walls = [{"id": "e1", "level_id": "L0", "start": [-0.15, -0.15], "end": [6.15, -0.15], "thickness": t},
             {"id": "e2", "level_id": "L0", "start": [6.15, -0.15], "end": [6.15, 4.15], "thickness": t},
             {"id": "e3", "level_id": "L0", "start": [6.15, 4.15], "end": [-0.15, 4.15], "thickness": t},
             {"id": "e4", "level_id": "L0", "start": [-0.15, 4.15], "end": [-0.15, -0.15], "thickness": t},
             {"id": "p1", "level_id": "L0", "start": [3.0, 0.0], "end": [3.0, 4.0], "thickness": ti,
              "exterior": flag}]
    for w in walls[:4]:
        w["exterior"] = True
    rooms = [{"id": "r_mutfak", "level_id": "L0", "room_type": "kitchen", "label": "MUTFAK",
              "polygon": [[0.0, 0.0], [2.925, 0.0], [2.925, 4.0], [0.0, 4.0]]},
             {"id": "r_hol", "level_id": "L0", "room_type": "hall", "label": "HOL",
              "polygon": [[3.075, 0.0], [6.0, 0.0], [6.0, 4.0], [3.075, 4.0]]}]
    ops = [{"id": "o_in", "type": "opening", "level_id": "L0", "wall_id": "p1", "center": [3.0, 2.0], "width": 0.85,
            "status": "unverified", "evidence": [{"method": "derived", "entity": "gap:LINE:1", "note": note,
                                                  "passage": "clear"}]},
           {"id": "o_out", "type": "opening", "level_id": "L0", "wall_id": "e1", "center": [1.5, -0.15],
            "width": 0.80, "status": "verified", "evidence": [{"method": "derived", "entity": "gap:LINE:2"}]}]
    return {"levels": [{"id": "L0", "elevation": 0.0}], "walls": walls, "rooms": rooms, "openings": ops}


def test_c0098_an_empty_gap_between_two_rooms_is_noted_in_an_inner_wall():
    b = _two_rooms()
    recs = SR.empty_gap_notes(b)
    inner, outer = b["openings"]
    assert "inner wall" in inner["evidence"][0]["note"] and inner["status"] == "verified"
    assert inner["evidence"][0]["exterior_note_was"] == SR.EMPTY_EXTERIOR_NOTE
    assert outer["evidence"][0]["note"] == SR.EMPTY_EXTERIOR_NOTE and outer["status"] == "unverified"
    assert sorted((r["opening"], r["exterior"]) for r in recs) == [("o_in", False), ("o_out", True)]


def test_an_unclassified_gaps_note_is_left_alone():
    b = _two_rooms(note="unclassified gap content: LINE:9")
    SR.empty_gap_notes(b)
    assert b["openings"][0]["evidence"][0]["note"] == "unclassified gap content: LINE:9"


def test_a_stale_exterior_flag_does_not_keep_a_passage_between_two_rooms_shut():
    b = _two_rooms(flag=True)
    walls = {w["id"]: w for w in b["walls"]}
    case = TW.passage_case(b["openings"][0], b["rooms"], walls, b["openings"])
    assert case["open"], case["why"]
    # a gap in a wall with the open air on one side stays shut whatever the flag
    o = dict(b["openings"][1], evidence=[{"method": "derived", "passage": "clear"}])
    walls["e1"]["thickness"] = 0.15
    assert not TW.passage_case(o, b["rooms"], walls, b["openings"])["open"]


# --- synthetic-37 ----------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def reading(tmp_path_factory):
    from wenart.ingest import pipeline as PL

    root = tmp_path_factory.mktemp("narrow_door")
    project = WP.project_37()
    FC.generate_failure_project(project, root)
    building, _build = PL.run_project(root / project.name, root / f"{project.name}-out", no_ai=True)
    return project, root, building


def test_synthetic_37_scores_100(reading):
    from wenart.reading_check import score as SC
    from wenart.reading_check import truth as TR

    project, root, building = reading
    truth = TR.synthetic_truth(project.name, root / project.name / FC.TRUTH_FILE)
    res = SC.match(truth, TR.extract(building, project=project.name), building)
    assert res["total"] == 100.0, res


def test_synthetic_37_no_door_at_the_column_the_others_keep_their_kind(reading):
    _project, _root, b = reading
    near = lambda at, tol=0.35: [o for o in b["openings"] if o["level_id"] == "L1"           # noqa: E731
                                 and math.dist(o["center"][:2], at) <= tol]
    assert not near((6.4, 0.125))                                       # the column: the facade runs on
    assert [o["type"] for o in near((5.2, 5.8))] == ["door"]            # the WC's 0.55 m door, its swing
    assert [o["type"] for o in near((2.0, 5.8))] == ["door"]            # the tagged 0.55 m sliding door
    assert [o["type"] for o in near((3.0, 4.4))] == ["door"]            # two 0.45 m leaves: one 0.90 m door
    assert [o["type"] for o in near((5.25, 8.875))] == ["window"]       # the 0.45 m window


# --- the old WIP re-checked (c87df9ad): the side paths' turns ---------------------------------------------------------

def test_the_stored_side_paths_walk_the_turns_of_ordered_flights():
    """The old WIP's side-path item (review B2-ST4): the side paths ``stair_rails.plan_guards`` builds the balustrade
    from carry the turn between ordered flights (real07's staggered U: before, its half landing's open edge had no leg,
    so no guard)."""
    from wenart.blender import parametric as P

    stair = {"flights": [{"start": [9.6697, 3.96], "end": [7.4697, 3.96], "width": 0.96, "lines": 9},
                         {"start": [7.7447, 5.12], "end": [9.8704, 5.12], "width": 0.96, "lines": 9}],
             "landing": None, "direction": None, "direction_assumed": False, "flights_ordered": True,
             "turn_winders": [0], "turn_assumed": False}
    plan = P.stair_plan({"footprint": {"center": [8.5, 4.5], "size": [3.0, 2.5], "rotation_deg": 0.0},
                         "stair": stair}, 3.0)
    assert plan["turns"]
    turn_legs = [leg for s in plan["sides"] for leg in s["legs"] if leg["what"] in ("landing", "winders")]
    assert turn_legs and all(not leg["wall"] for leg in turn_legs)
