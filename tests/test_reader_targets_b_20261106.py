"""6 Nov 2026 (Milestone 14, the reader targets): general rules the user's corrections and the machine reviewers showed,
each with the project that showed it as its test case only (user rule of 26 Oct 2026: "fix should be general").

- Stairs read from their numbered treads (``generic.stair_numbers``): numbers on a circle are a curved stair
  (synthetic-22, real07's curved stair); the number at an arm's turn end that stands a different step away is the first
  winder (synthetic-15, UL286); a stair piece of the stair rule that holds a chain of numbers takes what the numbers
  say (the treads drawn, the winders, the rise direction and the flights' order, the turn).
- A door drawn across a continuous wall (``openings._continuous_symbols``): the open leaf is the line that fits the
  end-point rule best (a door block's closed leaf in the wall, 2 cm short of the arc's end, is not it), and the door
  lies on the wall its closed leaf runs along (real21: six bedroom doors hinged at a wall corner were put on the
  perpendicular wall and their closed leaves read as windows).
- An inner wall gets a window only from a symbol of its own (``openings._continuous_windows``): a wall drawn with two
  pairs of lines (structure on DUVAR, plaster on SIVA) has its inner pair between the faces, and a stretch of it
  between a door and a cross wall is no window (real06 C0064, user: "these windows are not making sense").
- A door-high size tag on a plain text layer is a door's (``core._door_tags``): real10's fire-stair door '140/230'
  (C0035) on the layer TEXT.
CPU only."""
from __future__ import annotations

import dataclasses
import math
from types import SimpleNamespace

import pytest
from shapely.geometry import Point

import _real01_page as R
from wenart.ingest.generic import openings as O
from wenart.ingest.generic import stair_numbers as SN


def _t(v, x, y):
    return SimpleNamespace(text=str(v), height=0.12, box=(x - 0.05, y - 0.05, x + 0.05, y + 0.05), id=f"T{v}")


def _line(a, b, layer=None, sid=None):
    st = R.stroke([a, b])
    st.layer = layer
    if sid:
        st.id = sid
    return st


# --------------------------------------------------------------------------
# Numbered treads
# --------------------------------------------------------------------------

def _curved(cx=10.2, cy=7.35, r_in=0.3, r_out=1.3, n=18, a0=-90.0, sweep=180.0):
    texts, strokes = [], []
    rm = (r_in + r_out) / 2
    for k in range(n + 1):
        a = math.radians(a0 + sweep * k / n)
        strokes.append(_line((cx + r_in * math.cos(a), cy + r_in * math.sin(a)),
                             (cx + r_out * math.cos(a), cy + r_out * math.sin(a)), "MERDIVEN"))
    for k in range(n):
        a = math.radians(a0 + sweep * (k + 0.5) / n)
        texts.append(_t(k + 1, cx + rm * math.cos(a), cy + rm * math.sin(a)))
    return texts, strokes


def test_numbers_on_a_circle_are_a_curved_stair():
    texts, strokes = _curved()
    chain = SN.chains(texts)[0]
    st = SN.stair_of(chain, strokes)
    assert not st.get("skip"), st
    assert st["turn"] == "curved" and st["steps"] == 18
    cv = st["curved"]
    assert cv["centre"] == pytest.approx([10.2, 7.35], abs=0.02)
    assert cv["radius_inner"] == pytest.approx(0.3, abs=0.02) and cv["radius_outer"] == pytest.approx(1.3, abs=0.02)
    assert abs(cv["sweep_deg"]) == pytest.approx(180.0, abs=1.0)
    # the footprint is the rectangle round the half ring: 1.3 m out from the centre, 2.6 m along the chord
    xs = [x for x, _ in st["polygon"].exterior.coords]
    ys = [y for _, y in st["polygon"].exterior.coords]
    assert max(xs) - min(xs) == pytest.approx(1.3, abs=0.03) and max(ys) - min(ys) == pytest.approx(2.6, abs=0.03)
    # the chord flights run along the walking line, one after the other, every tread counted once (review B S2: chords
    # of 30 degrees at most, 2 lines each at least; one tread, the turn, between a chord's last line and the next one's
    # first)
    fl = st["flights"]
    assert sum(f["lines"] for f in fl) == 18 and len(fl) == 6 and all(f["lines"] >= 2 for f in fl)
    tread = 2 * 0.8 * math.sin(math.radians(5.0))                         # 10 degrees a tread on the 0.8 m walking line
    assert all(math.dist(a["end"], b["start"]) == pytest.approx(tread, abs=0.01) for a, b in zip(fl, fl[1:]))
    assert st["turn_winders"] == [0] * 5


def test_numbers_on_a_straight_line_are_no_curved_stair():
    texts = [_t(k, 1.0 + 0.27 * k, 2.0) for k in range(1, 12)]
    assert SN.curved_stair_of(SN.chains(texts)[0], [])["skip"]
    st = SN.stair_of(SN.chains(texts)[0], [])
    assert st["turn"] == "straight"


_S15_PTS = ([(8.835 + 0.27 * k, 6.5735) for k in range(6)]
            + [(10.5749, 6.5264), (10.9874, 6.8261), (11.145, 7.311), (10.9874, 7.7959), (10.5749, 8.0956)]
            + [(10.185 - 0.27 * k, 8.0485) for k in range(6)])


def _s15_lines(winder_lines=True):
    """synthetic-15's tread lines as its generator draws them (``synthetic.failure_classes.u_stair``): square to the
    arms at every tread's edge; radial from the well's end (10.32, 7.325) at the winders' edges, every 36 degrees (or,
    ``winder_lines`` False, none there)."""
    lines = [_line((8.7 + 0.27 * k, 5.95), (8.7 + 0.27 * k, 7.225), "MERDIVEN") for k in range(7)]
    lines += [_line((8.7 + 0.27 * k, 7.425), (8.7 + 0.27 * k, 8.7), "MERDIVEN") for k in range(7)]
    if winder_lines:
        pv = (10.32, 7.325)
        for k in range(1, 5):
            a = math.radians(-90 + 36 * k)
            t = min((11.7 - pv[0]) / math.cos(a), 1.375 / abs(math.sin(a)))
            lines.append(_line(pv, (pv[0] + t * math.cos(a), pv[1] + t * math.sin(a)), "MERDIVEN"))
    return lines


def test_the_first_winder_is_not_the_arms_last_tread():
    """synthetic-15 (UL286): 1-6 on the lower arm (0.27 m apart), 7-11 round the turn (0.39-0.51 m apart, 7 only 7
    degrees off the arm's line), 12-17 back on the upper arm: five winders, not three. Review B S10: the radial line
    each winder number stands on decides, not the label's offset angle."""
    texts = [_t(k + 1, x, y) for k, (x, y) in enumerate(_S15_PTS)]
    chain = SN.chains(texts)[0]
    assert [v for v, _p, _t in chain] == list(range(1, 18))
    segs = SN._near_segs([c[1] for c in chain], _s15_lines())
    arms = SN._arms([c[1] for c in chain], segs)
    assert [len(a) for a in arms] == [6, 6]
    st = SN.stair_of(chain, _s15_lines())
    assert st["winders"] == 5 and st["turn"] == "U" and st["turn_winders"] == [5]
    assert [f["lines"] for f in st["flights"]] == [6, 6]
    # no line drawn in the turn: nothing says the 7 and the 11 turn, they stay their arms' last and first treads
    st = SN.stair_of(chain, _s15_lines(winder_lines=False))
    assert [f["lines"] for f in st["flights"]] == [7, 7] and st["turn_winders"] == [3]


def test_a_deeper_tread_on_a_square_line_is_no_winder_and_on_a_diagonal_line_is_one():
    """real18 (the regression set): a U stair with a half landing numbers its 8 and 9 by the landing, 0.41 and 0.36 m
    on, standing on tread lines square to the arms: they stay the arms' treads (no winders). Review B S10: the same
    numbers standing on diagonal lines are winders, at both ends of the U alike."""
    pts = [(7.0 + 0.26 * k, 8.75) for k in range(7)] + [(8.96, 8.75), (8.61, 6.67)]
    pts += [(8.25 - 0.25 * k, 6.67) for k in range(7)]
    chain = SN.chains([_t(k + 1, x, y) for k, (x, y) in enumerate(pts)])[0]
    assert [f["lines"] for f in SN.stair_of(chain, [])["flights"]] == [8, 8]            # no line drawn: no turn
    square = [_line((8.96, 8.2), (8.96, 9.3), "MERDIVEN"), _line((8.61, 6.12), (8.61, 7.22), "MERDIVEN")]
    st = SN.stair_of(chain, square)
    assert [f["lines"] for f in st["flights"]] == [8, 8] and st["winders"] == 0
    diagonal = [_line((8.66, 8.25), (9.26, 9.25), "MERDIVEN"), _line((8.31, 7.17), (8.91, 6.17), "MERDIVEN"),
                _line((8.70, 8.2), (8.70, 9.3), "MERDIVEN"), _line((8.43, 6.12), (8.43, 7.22), "MERDIVEN")]  # the risers
    st = SN.stair_of(chain, diagonal)
    assert [f["lines"] for f in st["flights"]] == [7, 7] and st["winders"] == 2 and st["turn_winders"] == [2]


def test_a_stair_piece_holding_a_chain_takes_what_the_numbers_say():
    """The stair rule's piece keeps its footprint and flights; the numbers give the treads drawn, the winders, the rise
    direction (drawn, so the architect never flips it) and the flights' order (the flight by number 1 first)."""
    texts = [_t(k + 1, x, y) for k, (x, y) in enumerate(_S15_PTS)]
    chain = SN.chains(texts)[0]
    # the stair rule read the upper flight first, both running +x, with a flat landing and an assumed direction
    stair = {"flights": [{"start": [8.97, 8.06], "end": [10.05, 8.06], "width": 1.2, "lines": 5, "spacing": 0.27},
                         {"start": [8.97, 6.59], "end": [10.05, 6.59], "width": 1.2, "lines": 5, "spacing": 0.27}],
             "landing": {"polygon": [[10.05, 5.95], [11.7, 5.95], [11.7, 8.7], [10.05, 8.7]], "depth": 1.65},
             "direction": [1.0, 0.0], "direction_assumed": True, "turn": "U", "turn_assumed": True, "reason": "rule"}
    piece = SimpleNamespace(details={"stair": stair}, evidence={"note": "stair rule"})
    said = SN.enrich(piece, chain, SN.stair_of(chain, _s15_lines()))
    assert "17 treads drawn" in said and "5 winder(s)" in said
    assert stair["steps_drawn"] == 17 and stair["winders"] == 5
    assert stair["direction_assumed"] is False and stair["turn_assumed"] is False
    # review B S1/S8: built in the numbers' order, with their treads (6 + 6) and the 5 winders of the turn
    assert stair["flights_ordered"] is True and stair["turn_winders"] == [5]
    assert [f["lines"] for f in stair["flights"]] == [6, 6]
    # the lower flight (number 1 at x 8.84) first, rising +x; the upper flight turned round, rising -x
    assert stair["flights"][0]["start"] == [8.97, 6.59] and stair["flights"][0]["end"] == [10.05, 6.59]
    assert stair["flights"][1]["start"] == [10.05, 8.06] and stair["flights"][1]["end"] == [8.97, 8.06]
    assert stair["direction"] == [1.0, 0.0]


def _held_plan(stair, chain, strokes=()):
    """``stair_numbers.enrich`` on a stair-rule piece holding ``chain``, then ``parametric.stair_plan`` at a 3.0 m rise."""
    from wenart.blender import parametric as P
    piece = SimpleNamespace(details={"stair": stair}, evidence={}, center=(9.5, 7.3), size=(1.2, 2.5), rotation_deg=0.0)
    said = SN.enrich(piece, chain, SN.stair_of(chain, list(strokes)))
    fp = {"center": list(piece.center), "size": list(piece.size), "rotation_deg": piece.rotation_deg}
    return said, P.stair_plan({"footprint": fp, "stair": stair}, 3.0)


def test_a_stair_piece_of_other_flights_takes_the_numbers_when_its_risers_are_too_high():
    """review B2 FC-03 / B2-ST5 (real09's core stair on four floors, real18 L-2: the stair rule read the straight middle
    run of a numbered U as one flight of 5-6 lines, built as risers of 0.50 m): the numbers' reading (its flights in
    order, the winders of its turn, its footprint) replaces the rule's, which is kept as drawn_stair."""
    chain = SN.chains([_t(k + 1, x, y) for k, (x, y) in enumerate(_S15_PTS)])[0]
    stair = {"flights": [{"start": [8.97, 6.59], "end": [10.05, 6.59], "width": 1.2, "lines": 5, "spacing": 0.27}],
             "landing": None, "direction": [1.0, 0.0], "direction_assumed": True, "turn": "straight",
             "turn_assumed": True, "reason": "rule"}
    said, plan = _held_plan(stair, chain, _s15_lines())
    assert "replace the rule" in said and stair["flights_ordered"] is True
    assert stair["drawn_stair"]["flights"][0]["lines"] == 5 and stair["adjusted_by_ai"]["by"] == "code"
    assert plan["risers"] == 17 and plan["riser_m"] <= 0.20
    # a 6-line rule flight holding a numbered U of 16 (real18 L-2)
    pts = [(7.0 + 0.26 * k, 8.75) for k in range(8)] + [(8.82 - 0.26 * k, 6.67) for k in range(8)]
    chain = SN.chains([_t(k + 1, x, y) for k, (x, y) in enumerate(pts)])[0]
    stair = {"flights": [{"start": [8.11, 7.075], "end": [6.88, 7.075], "width": 1.0, "lines": 6, "spacing": 0.25}],
             "landing": None, "direction": [-1.0, 0.0], "direction_assumed": True, "turn": "straight",
             "turn_assumed": True, "reason": "rule"}
    _said, plan = _held_plan(stair, chain)
    assert plan["risers"] == 16 and plan["riser_m"] <= 0.20


def test_a_stair_piece_of_other_flights_keeps_them_when_they_climb():
    """real09 (found by the regression set): a rule piece whose flights give a stair one climbs keeps them; the
    numbers' other count is noted, not claimed (review B S8)."""
    chain = SN.chains([_t(k + 1, x, y) for k, (x, y) in enumerate(_S15_PTS)])[0]
    stair = {"flights": [{"start": [8.97, 6.59], "end": [12.97, 6.59], "width": 1.2, "lines": 17, "spacing": 0.25}],
             "landing": None, "direction": [1.0, 0.0], "direction_assumed": True, "turn": "straight",
             "turn_assumed": True, "reason": "rule"}
    piece = SimpleNamespace(details={"stair": stair}, evidence={}, center=(9.5, 7.3), size=(1.2, 4.2), rotation_deg=0.0)
    said = SN.enrich(piece, chain, SN.stair_of(chain, []))
    assert "steps_drawn" not in stair and "winders" not in stair and stair["turn"] == "straight"
    assert "flights_ordered" not in stair and "the rule's flights kept as drawn" in said


def test_numbered_treads_that_fit_no_shape_change_nothing():
    """review B S8: a chain that fits no shape claims no tread count the build would not follow."""
    texts = [_t(k, 1.0 + 0.27 * k, 2.0) for k in range(1, 12)]
    chain = SN.chains(texts)[0]
    piece = SimpleNamespace(details={"stair": {"flights": [], "direction_assumed": True}}, evidence={})
    assert SN.enrich(piece, chain, {"skip": "no shape"}) == ""
    assert "steps_drawn" not in piece.details["stair"] and piece.details["stair"]["direction_assumed"] is True


def test_each_number_goes_to_its_nearest_flight():
    """review B S9: a U stair with no eye (1-8 rising +x at y 0.50, 9-16 rising -x at y 1.45, flights 0.95 m wide)
    listed by the stair rule upper flight first: number 1 is within one width of the upper flight too, but belongs to
    the lower one; the upper flight rises -x."""
    texts = [_t(k + 1, 0.2 + 0.27 * k, 0.50) for k in range(8)] + [_t(9 + k, 2.09 - 0.27 * k, 1.45) for k in range(8)]
    chain = SN.chains(texts)[0]
    stair = {"flights": [{"start": [0.2, 1.45], "end": [2.09, 1.45], "width": 0.95, "lines": 8, "spacing": 0.27},
                         {"start": [0.2, 0.50], "end": [2.09, 0.50], "width": 0.95, "lines": 8, "spacing": 0.27}],
             "landing": None, "direction": [1.0, 0.0], "direction_assumed": True, "turn": "U", "turn_assumed": True,
             "reason": "rule"}
    SN.enrich(SimpleNamespace(details={"stair": stair}, evidence={}), chain, SN.stair_of(chain, []))
    assert stair["flights"][0]["start"] == [0.2, 0.50] and stair["flights"][0]["end"] == [2.09, 0.50]
    assert stair["flights"][1]["start"] == [2.09, 1.45] and stair["flights"][1]["end"] == [0.2, 1.45]


_REAL13_A = {1: (3.91, 0.89), 2: (3.68, 0.88), 3: (3.41, 0.88), 4: (2.46, 1.37), 5: (2.45, 1.62), 6: (2.45, 1.90),
             7: (2.58, 2.42), 8: (2.91, 2.75), 9: (3.31, 2.87), 10: (3.64, 2.87), 11: (3.89, 2.87), 12: (4.14, 2.87),
             13: (4.39, 2.87), 14: (4.64, 2.87), 15: (4.89, 2.87), 16: (5.42, 2.75), 17: (5.75, 2.28), 18: (5.77, 1.93)}
_REAL13_B = {1: (0.11, 0.86), 2: (0.11, 1.11), 3: (0.11, 1.36), 4: (0.11, 1.61), 5: (0.11, 1.86), 6: (0.11, 2.17),
             7: (0.11, 2.60), 8: (-0.91, 2.96), 9: (-1.72, 2.22), 10: (-1.72, 1.86), 11: (-1.72, 1.66),
             12: (-1.72, 1.40), 13: (-1.72, 1.11), 14: (-1.72, 0.86), 15: (-1.72, 0.61)}


def test_two_numbered_stairs_side_by_side_keep_their_own_numbers():
    """real13 L-1 (the two stairs of the basement, 'MER 18'): the near U stair's 7 ends its arm and its 8 stands on the
    landing 1.1 m on, the other stair's 7 and 8 lead on 2.5-2.8 m away: each stair keeps its own numbers."""
    texts = [_t(v, x, y) for v, (x, y) in _REAL13_B.items()] + [_t(v, x, y) for v, (x, y) in _REAL13_A.items()]
    for t in texts[:len(_REAL13_B)]:
        t.id = "B" + t.id
    got = sorted([t.id for _v, _p, t in c] for c in SN.chains(texts))
    assert got == sorted([["T%d" % v for v in range(1, 19)], ["BT%d" % v for v in range(1, 16)]])
    b = next(c for c in SN.chains(texts) if c[0][2].id.startswith("B"))
    st = SN.stair_of(b, [])
    assert st["turn"] == "U" and st["steps"] == 15


def test_a_chain_may_start_at_two_when_no_one_stands_by_it():
    """review B-X1: the top floor's plan numbers the arriving stair 2-17 (its first tread under the plan's cut, real10
    L7, real07 L1): a 2 with no 1 within a step starts a chain. A 2 with its 1 one step away is that chain's second
    tread, never a chain of its own."""
    top = [_t(v, 1.0 + 0.27 * (v - 2), 2.0) for v in range(2, 12)]
    assert [[v for v, _p, _t in c] for c in SN.chains(top)] == [list(range(2, 12))]
    full = [_t(v, 1.0 + 0.27 * (v - 1), 2.0) for v in range(1, 12)]
    assert [[v for v, _p, _t in c] for c in SN.chains(full)] == [list(range(1, 12))]
    # a 2 far from any 1 but with no 3 after it within a step is no chain
    lone = [_t(2, 5.0, 5.0), _t(3, 7.0, 5.0)] + full
    assert [[v for v, _p, _t in c] for c in SN.chains(lone)] == [list(range(1, 12))]


def test_a_row_of_grid_numbers_is_no_stair():
    """real06 (found by the regression set): the structural grid's numbers 1-8, 1.3 m apart in a row outside the
    building, gave a 'stair' of six treads when a number on a landing could be up to 3 m on; that holds only after an
    arm of tread steps."""
    grid = [_t(v, 3.0 + 1.3 * v, 17.0) for v in range(1, 9)]
    assert SN.chains(grid) == []
    texts = [_t(v, x, y) for v, (x, y) in _REAL13_B.items()] + grid
    assert [[v for v, _p, _t in c] for c in SN.chains(texts)] == [list(range(1, 16))]


def test_three_numbered_stairs_side_by_side_each_keep_their_numbers():
    """real18 L3 (the target: "treads 1-16"): a U stair 1-16 between two L stairs 1-15; its 8 is 1.6 m from the near L
    stair's 9 and 2.1 m from its own 9 (across its half landing). The longest regular chains win and the U stair is
    built again without the numbers they took."""
    lower = [(8.5, 5.62), (8.5, 5.8), (8.48, 6.02), (8.4, 6.18), (8.18, 6.22), (8.0, 6.24), (7.83, 6.23), (7.61, 6.22),
             (7.42, 6.22), (7.24, 6.22), (7.04, 6.22), (6.81, 6.22), (6.61, 6.22), (6.41, 6.22), (6.23, 6.22)]
    upper = [(x, 15.47 - y) for x, y in lower]                                # the mirror image about y 7.735
    u = [(7.0 + 0.2794 * k, 8.75) for k in range(8)] + [(8.61 - 0.2686 * k, 6.67) for k in range(8)]
    texts = []
    for tag, pts in (("L", lower), ("M", upper), ("U", u)):
        for k, (x, y) in enumerate(pts):
            t = _t(k + 1, x, y)
            t.id = f"{tag}{k + 1}"
            texts.append(t)
    got = sorted((c[0][2].id[0], [t.id[0] for _v, _p, t in c].count(c[0][2].id[0]), len(c)) for c in SN.chains(texts))
    assert got == [("L", 15, 15), ("M", 15, 15), ("U", 16, 16)]


def test_a_stair_of_many_arms_is_still_a_stair():
    """real13 L-1's other stair, 1-18 round a well (three straight runs, winders between): numbered treads always give
    a stair, its runs the flights, the turn 'other'."""
    chain = SN.chains([_t(v, x, y) for v, (x, y) in _REAL13_A.items()])[0]
    st = SN.stair_of(chain, [])
    assert not st.get("skip"), st
    assert st["turn"] == "other" and st["steps"] == 18 and len(st["flights"]) >= 3
    # review B S8: every number a tread line of a flight or a winder of a turn (16-18 turning away after the last run:
    # a short flight of their own)
    assert st["winders"] == 18 - sum(f["lines"] for f in st["flights"]) == sum(st["turn_winders"])


# --------------------------------------------------------------------------
# The numbered stairs as the builder climbs them (review B S1, S4, S8, S12)
# --------------------------------------------------------------------------

def _built(texts, strokes):
    """The numbered stair read from ``texts`` (``stair_numbers.apply``) as ``parametric.stair_plan`` builds it."""
    from wenart.blender import parametric as P
    notes = []
    pieces, _c, _p = SN.apply([], [], texts, strokes, 1.0, "t.dxf", 1, notes)
    (piece,) = [p for p in pieces if p.type == "stair"]
    data = piece.details["stair"]
    fp = {"center": list(piece.center), "size": list(piece.size), "rotation_deg": piece.rotation_deg}
    plan = P.stair_plan({"footprint": fp, "stair": data}, 3.0)
    return data, plan


def _climbs(data, plan, first, last, treads):
    """The built stair: the flights in the numbers' order, each starting by where the one before ends (across one
    turn), the floor rising all the way, a riser for every tread drawn, number 1 at its foot and the last at its top."""
    fl = plan["flights"]
    assert [f["index"] for f in fl] == list(range(len(data["flights"])))
    assert plan["risers"] == treads
    zs = [z for f in fl for z in (f["base_z"], f["top_z"])]
    assert zs == sorted(zs) and fl[-1]["top_z"] == pytest.approx(3.0)
    turns = plan.get("turns") or []
    for i, (a, b) in enumerate(zip(fl, fl[1:])):
        k = data["turn_winders"][i]
        assert b["base_z"] == pytest.approx(a["top_z"] + k * plan["riser_m"])
        assert math.dist(a["nosings"][-1], b["nosings"][0]) <= 2.5 * max(a["width"], b["width"])
    assert math.dist(fl[0]["nosings"][0], first) <= fl[0]["width"]
    assert math.dist(fl[-1]["nosings"][-1], last) <= fl[-1]["width"]
    return turns


def test_a_numbered_curved_stair_is_built_climbing_round_its_curve():
    texts, strokes = _curved()
    data, plan = _built(texts, strokes)
    turns = _climbs(data, plan, (texts[0].box[0] + 0.05, texts[0].box[1] + 0.05),
                    (texts[-1].box[0] + 0.05, texts[-1].box[1] + 0.05), 18)
    assert len(turns) == 5 and all(t["role"] == "flat" for t in turns)
    # every chord flight on the drawn ring (its treads between the radii, the walking line through them)
    for f in plan["flights"]:
        for q in f["nosings"]:
            assert 0.3 - 0.05 <= math.dist(q, (10.2, 7.35)) <= 1.3


def test_a_numbered_stair_of_many_arms_is_built_in_the_numbers_order():
    texts = [_t(v, x, y) for v, (x, y) in _REAL13_A.items()]
    data, plan = _built(texts, [])
    turns = _climbs(data, plan, _REAL13_A[1], _REAL13_A[18], 18)
    assert sum(len(t["winders"]) for t in turns) == sum(k + 1 for k in data["turn_winders"] if k)


def test_a_numbered_l_stair_has_its_landing_at_the_junction_and_climbs_from_number_one():
    """review B S4: 1-3 running -y, 4-15 running -x (real18 L3's flat stairs without their fan): the landing is the
    square where the arms meet, never a strip along the long flight, and the stair climbs from number 1."""
    pts = [(8.5, 6.6 - 0.25 * k) for k in range(3)] + [(7.9 - 0.25 * k, 5.95) for k in range(12)]
    texts = [_t(k + 1, x, y) for k, (x, y) in enumerate(pts)]
    data, plan = _built(texts, [])
    land = data["landing"]
    if land is not None:
        xs, ys = [q[0] for q in land["polygon"]], [q[1] for q in land["polygon"]]
        assert min(xs) >= 7.9 - 0.05 and max(ys) <= 6.6 + 0.05     # beyond the long arm's first line, by the corner
    _climbs(data, plan, pts[0], pts[-1], 15)


def test_a_numbered_u_stair_with_winders_builds_them_all():
    """review B S8/S12: synthetic-15, 6 + 5 winders + 6: 17 risers, the winders in the turn."""
    texts = [_t(k + 1, x, y) for k, (x, y) in enumerate(_S15_PTS)]
    data, plan = _built(texts, _s15_lines())
    turns = _climbs(data, plan, _S15_PTS[0], _S15_PTS[-1], 17)
    land = plan["landing"]
    built = len(land["winders"]) if land is not None and land["role"] == "winders" else \
        sum(len(t["winders"]) for t in turns)
    assert built == 6                                                   # 5 winder risers: 6 treads in the turn


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

def _box_with_inner_wall(entrances=True):
    """Two rooms (south, north) of a 6 x 4 m box split by an inner wall at y = 2; with ``entrances`` the south room's
    door gap in the outer wall (x 4.0-4.9) and a door gap in the inner wall (x 4.0-4.9)."""
    south = ([R.wall((0, 0), (4.0, 0), t=0.25, entity="S1"), R.wall((4.9, 0), (6, 0), t=0.25, entity="S2")]
             if entrances else [R.wall((0, 0), (6, 0), t=0.25, entity="S")])
    inner = ([R.wall((0.125, 2.0), (4.0, 2.0), t=0.15, entity="I1"), R.wall((4.9, 2.0), (5.875, 2.0), t=0.15, entity="I2")]
             if entrances else [R.wall((0.125, 2.0), (5.875, 2.0), t=0.15, entity="I")])
    return south + [R.wall((6, 0), (6, 4), t=0.25, entity="E"), R.wall((6, 4), (0, 4), t=0.25, entity="N"),
                    R.wall((0, 4), (0, 0), t=0.25, entity="W")] + inner


def _wall_lines(layer, block=None, x0=1.0, x1=1.8, y=2.0):
    lines = [_line((x0, y - 0.05), (x1, y - 0.05), layer), _line((x0, y + 0.05), (x1, y + 0.05), layer)]
    for st in lines:
        st.block = block
    return lines


def test_an_inner_wall_stretch_drawn_with_two_pairs_of_lines_is_no_window():
    """real06 L1 (C0064): the DUVAR pair 5 cm inside the plaster faces between a door's frame and a cross wall. Review
    L2 (real06 L0's pier between two doors): the south room's door gap to the outside no longer makes its walls outer
    ones (the outline is closed at its doors)."""
    _walls, openings, log, _owned = O.gaps_and_openings(_box_with_inner_wall(), _wall_lines("DUVAR"), "t.dxf", 1)
    assert [o.kind for o in openings] == ["opening", "opening"]
    dropped = [e for e in log if e.get("rule") == "inner_wall_faces"]
    assert dropped and "inner wall" in dropped[0]["note"] and "DUVAR" in dropped[0]["note"]


def test_an_inner_wall_window_drawn_on_a_window_layer_stays():
    _walls, openings, _log, _owned = O.gaps_and_openings(_box_with_inner_wall(), _wall_lines("PENCERE"), "t.dxf", 1)
    assert [round(o.width, 2) for o in openings if o.kind == "window"] == [0.8]


def test_an_inner_wall_window_block_inserted_on_a_wall_layer_stays():
    """review L5: a window block's lines take the wall layer it was inserted on; the block's name says window."""
    lines = _wall_lines("DUVAR", block="PENCERE_80")
    _walls, openings, _log, _owned = O.gaps_and_openings(_box_with_inner_wall(), lines, "t.dxf", 1)
    assert [round(o.width, 2) for o in openings if o.kind == "window"] == [0.8]


def test_a_window_towards_a_closed_space_no_door_enters_stays():
    """review B-OPN-03 / L5: the north part is a light well (no door or doorless opening enters it): the wall towards
    it is an outer wall, its window drawn with wall-layer lines stays."""
    walls = _box_with_inner_wall()
    walls = [w for w in walls if w.entity != "I1" and w.entity != "I2"] + [R.wall((0.125, 2.0), (5.875, 2.0), t=0.15,
                                                                                   entity="I")]
    _walls, openings, log, _owned = O.gaps_and_openings(walls, _wall_lines("DUVAR"), "t.dxf", 1)
    assert [round(o.width, 2) for o in openings if o.kind == "window"] == [0.8]
    assert not [e for e in log if e.get("rule") == "inner_wall_faces"]


def test_a_window_towards_a_labelled_outdoor_space_stays():
    """review B-OPN-03: a courtyard or balcony a door opens onto is a closed face, but its label says it is outside."""
    lines = _wall_lines("DUVAR")
    _walls, openings, _log, _owned = O.gaps_and_openings(_box_with_inner_wall(), lines, "t.dxf", 1,
                                                         outdoor_points=[(3.0, 3.0)])
    assert [round(o.width, 2) for o in openings if o.kind == "window"] == [0.8]


def test_an_outer_wall_window_drawn_with_wall_layer_lines_stays():
    """real06's facade windows: the same two DUVAR lines in an outer wall are its window, as before."""
    lines = _wall_lines("DUVAR", x0=1.0, x1=2.5, y=4.0)
    _walls, openings, _log, _owned = O.gaps_and_openings(_box_with_inner_wall(), lines, "t.dxf", 1)
    assert [round(o.width, 2) for o in openings if o.kind == "window"] == [1.5]


def test_wall_face_layers():
    """review B-OPN-09: the shared layer table's window and glass words, word by word."""
    assert O.wall_face_layer("DUVAR") and O.wall_face_layer("SIVA") and O.wall_face_layer("A-WALL")
    assert not O.wall_face_layer("PENCERE") and not O.wall_face_layer("DUVAR-PENCERE")
    assert not O.wall_face_layer("A-WALL-GLAZ") and not O.wall_face_layer("0") and not O.wall_face_layer(None)
    for name in ("DUVAR-PENC", "DUVAR DOGRAMA", "MUR-VERRE", "A-WALL-CURTAIN", "WALL-FINESTRA"):
        assert not O.wall_face_layer(name), name
    assert O.wall_face_layer("DUVAR-CAMBAZ")                 # a word that only starts like CAM is no glass word


# --------------------------------------------------------------------------
# A door-high size tag on a plain text layer
# --------------------------------------------------------------------------

def _tag(text, x, y, layer):
    from wenart.ingest.generic.model import TextRun
    return TextRun(id="T" + text, text=text, box=(x - 0.2, y - 0.05, x + 0.2, y + 0.05), height=0.1,
                   rotation_deg=0.0, evidence=[{"layer": layer}])


def test_a_door_high_tag_on_a_text_layer_makes_its_gap_a_door():
    """real10 (C0035): the fire stair's '140/230' on the layer TEXT over the 1.40 m gap from the shared hall."""
    from wenart.ingest.generic import core as C
    from wenart.ingest.model import OpeningItem

    gap = OpeningItem(kind="opening", width=1.4, center=(11.19, 6.29), rotation_deg=0.0, box=[0, 0, 1, 1], entity="g",
                      evidence={}, type_raw="unclassified gap content")
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [gap], [_tag("140/230", 10.91, 6.35, "TEXT")], 1.0)
    assert got[0].kind == "door" and got[0].width == pytest.approx(1.4) and got[0].height == pytest.approx(2.3)


def _op(kind, w, c, rot=0.0, rule=None, type_raw=None):
    from wenart.ingest.model import OpeningItem
    ev = {"rule": rule} if rule else {}
    return OpeningItem(kind=kind, width=w, center=c, rotation_deg=rot, box=[0, 0, 1, 1], entity=f"{kind}{c}",
                       evidence=ev, type_raw=type_raw)


def _gap(w, c, rot=0.0, rule=None):
    return _op("opening", w, c, rot, rule, "unclassified gap content")


def _box(x0, y0, x1, y1):
    from shapely.geometry import box
    return box(x0, y0, x1, y1)


def test_a_low_tag_on_a_text_layer_is_no_door():
    from wenart.ingest.generic import core as C
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [_gap(1.2, (2.0, 0.0))],
                        [_tag("120/120", 2.0, 0.3, "TEXT")], 1.0) is None


def test_a_wide_door_high_tag_on_a_text_layer_decides_by_the_wall_not_by_its_width():
    """review B-OPN-08 (the 150 cm cap fitted between real10's 140/230 door and its 165/210 kitchen windows): a door-high
    plain tag makes an inner wall's gap a door at any door width (a 170 double door), never a gap in an outer wall
    (a door-high opening there may be a window)."""
    from wenart.ingest.generic import core as C
    outline = _box(0.0, -6.0, 10.0, 0.0)                         # the building lies south of y = 0
    inner = _gap(1.7, (2.0, -3.0))
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [inner], [_tag("170/210", 2.0, -2.7, "TEXT")], 1.0,
                       outline=outline)
    assert got[0].kind == "door" and got[0].width == pytest.approx(1.7)
    facade = _gap(1.65, (2.0, 0.0))
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [facade], [_tag("165/210", 2.0, -0.3, "TEXT")], 1.0,
                        outline=outline) is None


def test_a_text_layer_tag_leaves_a_gap_with_window_frame_lines_or_far_wider_than_itself():
    """review B-OPN-01 (real18 L1-L3: the '80/210' of a door the reader missed made the 2.75 m gap of a facade window
    a 0.80 m door): a gap holding lines along it (a window's frame) or wider than two such doors is not the tag's."""
    from wenart.ingest.generic import core as C
    framed = _gap(1.1, (2.0, -3.0), rule="no_glass")
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [framed], [_tag("80/210", 2.4, -2.6, "TEXT")], 1.0) is None
    wide = _gap(2.75, (2.0, -3.0))
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [wide], [_tag("80/210", 2.4, -2.6, "TEXT")], 1.0) is None


def test_a_door_high_tag_on_a_text_layer_leaves_a_drawn_window_alone():
    from wenart.ingest.generic import core as C
    win = _op("window", 1.2, (2.0, 0.0))
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [win], [_tag("120/210", 2.0, 0.3, "TEXT")], 1.0) is None


def test_a_tag_beside_its_own_door_is_used_up_by_it():
    """real10 (found by the regression set): an '80/210' beside its 0.80 m door went on to the next opening within
    reach, a 0.70 m gap window 1.2 m away, and made it a door; the tag belongs to the door it stands by."""
    from wenart.ingest.generic import core as C
    door = _op("door", 0.8, (8.74, 13.99), rot=90.0)
    gap_win = _op("window", 0.7, (10.17, 13.72), type_raw="unclassified gap content")
    tag = _tag("80/210", 9.02, 13.58, "TEXT")
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [door, gap_win], [tag], 1.0) is None


def test_a_tag_never_resizes_a_door_of_another_width_nearer_than_its_own():
    """review B-r10-tag (real10 L-1..L6: the flat doors' '90/210' made two crossed shaft boxes, read as 0.43 m doors,
    0.90 m doors, 16 times): a door further than DOOR_TAG_DOOR_W_M off the tag's width is another door."""
    from wenart.ingest.generic import core as C
    box = _op("door", 0.43, (5.39, 9.19), rot=0.0)
    own = _op("door", 0.90, (5.69, 9.89), rot=90.0)
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [box, own], [_tag("90/210", 5.19, 9.55, "TEXT")],
                        1.0) is None


def test_tags_are_matched_nearest_pairs_first_not_in_text_order():
    """review B-r10-tag-greedy (real10's typical floors): the '100/225' read first stood 0.764 m from the door of the
    '90/210' and 0.765 m from its own; the '90/210' stands 0.58 m from its door. Nearest pairs first: each tag its own
    door."""
    from wenart.ingest.generic import core as C
    d14 = _op("door", 0.90, (14.96, 6.48), rot=90.0)
    d19 = _op("door", 1.10, (13.64, 7.24), rot=0.0)
    tags = [_tag("100/225", 14.343, 6.899, "TEXT"), _tag("90/210", 15.225, 5.968, "TEXT")]
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [d14, d19], tags, 1.0)
    assert got[0].width == pytest.approx(0.90) and got[1].width == pytest.approx(1.00)
    assert got[1].height == pytest.approx(2.25)


def test_a_tag_as_near_a_drawn_door_as_a_gap_is_the_doors():
    """real07 C0047 (the user's correction: 'the entrance to the room is wrong door'): the '80/210' stands as near the
    Kat Kal. door's span (0.85 m, drawn) as the 1.56 m gap read over it; the drawn door takes it, no second door."""
    from wenart.ingest.generic import core as C
    gap = _gap(1.56, (5.36, 2.19))
    door = _op("door", 0.85, (5.815, 2.19))
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [gap, door], [_tag("80/210", 5.63, 1.74, "DOGRAMA")],
                        1.0) is None


def test_two_tags_never_resize_doors_on_one_spot():
    """review B-r10-tag-greedy (real10: two copies of one door and another door on one spot took the '90/210' and the
    '110/230'): a spot takes one tag; the second is logged as two door symbols on one spot."""
    from wenart.ingest.generic import core as C
    stack = [_op("door", 0.80, (6.94, 6.387), rot=90.0), _op("door", 1.0, (6.94, 6.387), rot=90.0)]
    ex = SimpleNamespace(notes=[])
    got = C._door_tags(ex, "x", [], stack, [_tag("90/210", 7.181, 5.968, "TEXT"), _tag("110/230", 6.712, 5.866, "TEXT")],
                       1.0)
    assert sum(1 for o in got if o.type_raw and "size tag" in o.type_raw) == 1
    assert any("one spot" in n for n in ex.notes)


def test_a_door_layer_tag_beside_its_own_door_leaves_a_window_alone():
    """review B-OPN-02 / B-T1: a door-layer '80/220' beside its 0.80 m balcony door left the door and made the drawn
    0.90 m window beside it a second door. Its own door is nearer: the tag is used up."""
    from wenart.ingest.generic import core as C
    door = _op("door", 0.80, (2.0, 0.0))
    win = _op("window", 0.90, (3.0, 0.0))
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [door, win], [_tag("80/220", 2.2, 0.3, "kapi-yazi")],
                        1.0) is None
    wc_win = _op("window", 0.60, (2.0, 0.0))
    door2 = _op("door", 0.80, (1.0, 0.0))
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [door2, wc_win], [_tag("80/210", 1.2, 0.25, "kapi-yazi")],
                        1.0) is None


def test_each_door_layer_tag_finds_its_own_gap_beside_a_neighbour_door():
    """real07 (the regression set): a '90/210' on the joinery layer stands near the next door, already 0.90 m and
    labelled by its own tag, and near its own 1.10 m gap: the neighbour keeps its tag, the gap takes this one."""
    from wenart.ingest.generic import core as C
    door = _op("door", 0.9, (3.0, 3.3))
    gap = _gap(1.1, (3.79, 2.79), rot=90.0)
    tags = [_tag("90/210", 3.0, 3.55, "kapi-yazi"), _tag("90/210", 3.5, 2.8, "kapi-yazi")]
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [door, gap], tags, 1.0)
    assert got[0].width == pytest.approx(0.9) and got[1].kind == "door" and got[1].width == pytest.approx(0.9)


def test_a_door_high_tag_on_a_door_layer_decides_door_over_a_drawn_window_of_its_width():
    """real16 L1: the shower rooms' '80/220' (layer kapi-yazi) beside a 0.68 m 'window' (the closed leaf's lines in the
    wall); a 1.50 m window beside the same tag keeps its kind."""
    from wenart.ingest.generic import core as C
    from wenart.ingest.model import OpeningItem

    def win(w):
        return OpeningItem(kind="window", width=w, center=(4.2, 13.18), rotation_deg=0.0, box=[0, 0, 1, 1], entity="w",
                           evidence={})
    tag = _tag("80/220", 4.2, 12.96, "kapi-yazi")
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [win(0.68)], [tag], 1.0)
    assert got[0].kind == "door" and got[0].width == pytest.approx(0.8) and got[0].height == pytest.approx(2.2)
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [win(1.5)], [tag], 1.0) is None


# --------------------------------------------------------------------------
# A door leaf read as a thin wall goes back to its door
# --------------------------------------------------------------------------

def test_a_door_leaf_read_as_a_thin_wall_goes_back_to_its_door():
    """real03: the bedrooms' door blocks draw the open leaf as a 0.80 x 0.05 m rectangle on the door layer; the wall mask
    read it as a thin wall, so the swing in the continuous wall had no leaf and the bedroom no door."""
    vert = R.wall((13.4539, 10.6), (13.4539, 14.05), t=0.1, entity="RING")
    leaf_rect = R.stroke([(14.303, 10.8005), (14.303, 10.7505), (13.503, 10.7505), (13.503, 10.8005)], closed=True)
    leaf_rect.layer = "MYD - KAPI"
    leaf_wall = R.wall((13.5039, 10.7755), (14.303, 10.7755), t=0.05, entity=leaf_rect.id)
    hinge = (13.503, 10.7505)
    swing = R.arc(hinge, 0.80, 0.0, 90.0)                           # from the open (+x) to the closed (+y) position
    swing.layer = "MYD - KAPI"
    walls, openings, log, owned = O.gaps_and_openings([vert, leaf_wall], [swing], "t.dxf", 1,
                                                      wall_strokes=[leaf_rect])
    assert [str(w.entity) for w in walls] == ["RING"]
    doors = [o for o in openings if o.kind == "door"]
    assert len(doors) == 1 and doors[0].width == pytest.approx(0.8, abs=0.01)
    assert doors[0].center == pytest.approx((13.4539, 11.1505), abs=0.01)
    assert leaf_rect.id in owned
    assert any(e.get("kind") == "wall_piece" and "door leaf" in e["note"] for e in log)


def _leaf_piece(length, layer):
    piece = R.stroke([(0, 0), (length, 0), (length, 0.05), (0, 0.05)], closed=True)
    piece.layer = layer
    return piece, R.wall((0, 0.025), (length, 0.025), t=0.05, entity=piece.id)


def test_a_thin_wall_is_a_leaf_only_with_its_swing_and_its_size():
    """review B-OPN-10: a thin piece on the door layer is a door leaf only when a door swing hinged at one of its ends
    has its length for a radius; a WC partition or a sliding screen on the door layer stays a wall, and so does a
    piece longer than any leaf, a frame or a jamb block (too short) and anything on a wall layer."""
    swing = R.arc((0.0, 0.0), 0.8, 0.0, 90.0)
    piece, w = _leaf_piece(0.8, "KAPI")
    assert O.leaf_walls([w], [piece], [swing]) == {0: [piece.id]}
    assert O.leaf_walls([w], [piece], []) == {}                                 # no swing: a partition
    far = R.arc((3.0, 2.0), 0.8, 0.0, 90.0)
    assert O.leaf_walls([w], [piece], [far]) == {}                              # a swing of another door
    big = R.arc((0.0, 0.0), 1.5, 0.0, 90.0)
    assert O.leaf_walls([w], [piece], [big]) == {}                              # its radius is no leaf of 0.8 m
    piece, w = _leaf_piece(0.8, "DUVAR")
    assert O.leaf_walls([w], [piece], [swing]) == {}
    piece, long_ = _leaf_piece(3.6, "KAPI")
    assert O.leaf_walls([long_], [piece], [R.arc((0.0, 0.0), 3.6, 0.0, 90.0)]) == {}
    piece, short = _leaf_piece(0.2, "KAPI")
    assert O.leaf_walls([short], [piece], [R.arc((0.0, 0.0), 0.2, 0.0, 90.0)]) == {}


def test_a_leaf_with_a_background_line_on_it_is_still_a_leaf():
    """review B-r03-leaf-incomplete (real03's fire-stair and safety-lobby doors): the leaf is a line of the door block
    plus a background-view line on 'MYD - GOR-ARKA'; its longest stroke is the door's, none is on a wall layer."""
    leaf = R.stroke([(0, 0), (0.9, 0)])
    leaf.layer, leaf.block = "0", "D BLOK_MERDIVEN_NK$0$KAPI - 100"
    view = R.stroke([(0.05, 0.05), (0.85, 0.05)])
    view.layer = "MYD - GOR-ARKA"
    w = R.wall((0, 0.025), (0.9, 0.025), t=0.06, entity=f"{leaf.id},{view.id}")
    swing = R.arc((0.0, 0.0), 0.9, 0.0, 90.0)
    assert O.leaf_walls([w], [leaf, view], [swing]) == {0: [leaf.id, view.id]}
    view.layer = "DUVAR"
    assert O.leaf_walls([w], [leaf, view], [swing]) == {}


# --------------------------------------------------------------------------
# A labelled room the walls leave open keeps its drawn outline
# --------------------------------------------------------------------------

def test_a_room_the_walls_leave_open_is_cut_off_along_its_drawn_outline():
    """review B-OPN-06 / B-R1 / B-r03-hol (real03: 'HOL 3.85 m2' lies open to the living room, no wall, no door, but its
    net-area outline is drawn): the run of the labelled outline inside the face two names share separates them, so
    the hall keeps its drawn area; without the outline the names share the face as before."""
    from shapely.geometry import Polygon
    from wenart.ingest.generic import topology as TP
    walls = [R.wall((0, 0), (6, 0), t=0.2, entity="S"), R.wall((6, 0), (6, 4), t=0.2, entity="E"),
             R.wall((6, 4), (0, 4), t=0.2, entity="N"), R.wall((0, 4), (0, 0), t=0.2, entity="W")]
    hol = SimpleNamespace(name="HOL", anchor=(1.5, 0.6), exterior=False, area_m2=3.0)
    living = SimpleNamespace(name="YASAMA", anchor=(3.0, 2.8), exterior=False, area_m2=None)
    outline = Polygon([(0.1, 0.1), (3.1, 0.1), (3.1, 1.1), (0.1, 1.1)])
    seps, log = TP.separators(walls, [], [], [hol, living], [], outlines=lambda: [outline])
    assert len(seps) == 2 and all("outline of 'HOL'" in o.evidence["note"] for o in seps)
    faces = TP.faces(walls, [], seps)
    hall = next(f for f in faces if f.contains(Point(1.5, 0.6)))
    assert hall.area == pytest.approx(3.0, abs=0.05)
    seps, _log = TP.separators(walls, [], [], [hol, living], [])
    assert seps == []


# --------------------------------------------------------------------------
# Duplicates, doors in gaps, double doors (review B-dup, B-R2, B-r10-dups, B-OPN-07, B-r16-double)
# --------------------------------------------------------------------------

def _swing(hinge, r, a0, a1, layer="kapi"):
    """A door swing and its open leaf (from the hinge to the arc's start)."""
    arc = R.arc(hinge, r, a0, a1)
    arc.layer = layer
    tip = (hinge[0] + r * math.cos(math.radians(a0)), hinge[1] + r * math.sin(math.radians(a0)))
    return [arc, _line(hinge, tip, layer)]


def test_a_door_drawn_twice_is_one_door():
    """review B-r10-dups (real10 L-1: two identical swings on one layer): the copy of a swing already read is no second
    door, and it is logged."""
    walls = [R.wall((0.0, 0.0), (6.0, 0.0), t=0.2, entity="H")]
    door = _swing((2.0, 0.0), 0.8, 90.0, 0.0)                     # open +y, closing onto (2.8, 0)
    copy = _swing((2.0, 0.0), 0.8, 90.0, 0.0)
    _w, openings, log, _o = O.gaps_and_openings(walls, door + copy, "t.dxf", 1)
    assert [(o.kind, round(o.width, 2)) for o in openings] == [("door", 0.8)]
    assert any(e.get("rule") == "duplicate_symbol" for e in log)


def test_a_door_in_a_gap_opening_of_its_wall_takes_its_part_of_the_gap():
    """review B-dup (real09: a 0.80 m door inside the 1.73 m gap opening of its wall): the gap keeps the rest beside the
    door; a gap no wider than the door is the door's."""
    from wenart.ingest.model import OpeningItem
    host = SimpleNamespace(axis="h", c=0.0, t=0.2)
    gap = OpeningItem(kind="opening", width=1.73, center=(4.22, 0.0), rotation_deg=0.0, box=[0, 0, 1, 1], entity="g",
                      evidence={"note": "unclassified gap content"}, type_raw="unclassified gap content")
    existing = [gap]
    ctx = SimpleNamespace(box=lambda pts: [0, 0, 1, 1])
    ev = {}
    assert O._door_in_gap(existing, host, 4.64, 0.80, 0.0, ctx, ev) is None
    rest = existing[0]
    assert rest.width == pytest.approx(4.24 - 3.355, abs=0.01) and rest.center[0] == pytest.approx(3.7975, abs=0.01)
    assert "takes its part of the gap" in ev["note"]
    own = OpeningItem(kind="opening", width=0.85, center=(4.64, 0.0), rotation_deg=0.0, box=[0, 0, 1, 1], entity="g2",
                      evidence={})
    assert O._door_in_gap([own], host, 4.64, 0.80, 0.0, ctx, {}) == 0
    other_wall = OpeningItem(kind="opening", width=1.73, center=(4.22, 1.0), rotation_deg=0.0, box=[0, 0, 1, 1],
                             entity="g3", evidence={})
    assert O._door_in_gap([other_wall], host, 4.64, 0.80, 0.0, ctx, {}) is None and other_wall.width == 1.73


def test_two_leaves_closing_onto_one_point_are_one_double_door():
    """review B-OPN-07 / B-r16-double (real16's '170/210' entrance): two swings hinged 1.6 m apart in a continuous wall,
    both closing onto its middle, are one 1.6 m double door; two doors side by side that close apart stay two."""
    walls = [R.wall((0.0, 0.0), (6.0, 0.0), t=0.2, entity="H")]
    left = _swing((1.0, 0.0), 0.8, 90.0, 0.0)                     # closes onto (1.8, 0)
    right = _swing((2.6, 0.0), 0.8, 90.0, 180.0)                  # closes onto (1.8, 0)
    _w, openings, _l, _o = O.gaps_and_openings(walls, left + right, "t.dxf", 1)
    doors = [o for o in openings if o.kind == "door"]
    assert len(doors) == 1 and doors[0].width == pytest.approx(1.6, abs=0.01)
    assert doors[0].center == pytest.approx((1.8, 0.0), abs=0.01) and doors[0].operation == "double"
    apart = _swing((1.0, 0.0), 0.8, 90.0, 0.0) + _swing((4.0, 0.0), 0.8, 90.0, 0.0)
    _w, openings, _l, _o = O.gaps_and_openings(walls, apart, "t.dxf", 1)
    assert sorted(round(o.width, 2) for o in openings if o.kind == "door") == [0.8, 0.8]


def test_a_narrow_gap_by_a_lift_shaft_is_not_its_landing_door():
    """review B-OPN-05 / B-r21-lift (real21: the 0.25 m gap at the partition between two lift shafts became a sliding
    'lift door'): a drawn opening is the landing door only when it is door-wide; else the door is inferred towards the
    hall as before. (Which wall of the shaft faces the hall is the building-sense branch's rule.)"""
    from wenart.ingest import twins as TW

    def room(rid, label, rtype, poly):
        return {"id": rid, "level_id": "L1", "label": label, "room_type": rtype, "polygon": poly}

    shaft = room("r_L1_asansor", "Asansör", "shaft", [[0, 0], [1.6, 0], [1.6, 1.8], [0, 1.8]])
    hall = room("r_L1_hall", "Kat Holü", "hall", [[0, 2.0], [4, 2.0], [4, 4], [0, 4]])
    walls = [{"id": "w1", "level_id": "L1", "start": [-0.1, 1.9], "end": [4.1, 1.9], "thickness": 0.2}]
    slit = {"id": "o1", "level_id": "L1", "type": "opening", "center": [1.7, 0.9], "width": 0.25}
    openings = [slit]
    TW.lift_doors([shaft, hall], openings, walls)
    assert slit["type"] == "opening" and "operation" not in slit
    assert len(openings) == 2 and openings[1]["type"] == "door" and openings[1]["operation"] == "sliding"


def test_a_core_hall_takes_no_slivers_round_the_stair():
    """review B-r10-L7-hall (real10 L7: the hall ran round the stair box in 3-6 cm slivers, its opening '10 m' wide on a
    0.15 m line): the slivers beside the stair are the stair's; the hall is the landing strip, joined along its
    straight edge, the opening as wide as its line."""
    from shapely.geometry import Polygon
    from wenart.ingest import twins as TW
    core = {"id": "core", "level_id": "L7", "label": "Merdiven", "label_raw": None, "room_type": "stair",
            "label_inferred": {"method": "stair_core"}, "evidence": [{"file": "a.dwg"}],
            "polygon": [[10.748, 6.67], [13.516, 6.67], [13.516, 10.19], [10.748, 10.19]]}
    stairs = [{"type": "stair", "level_id": "L7", "footprint": {"center": [12.147, 8.946], "size": [2.677, 2.428],
                                                                "rotation_deg": 0}}]
    rooms, openings = [core], []
    assert len(TW.split_core_landings(rooms, openings, stairs)) == 1
    hall = Polygon(rooms[1]["polygon"])
    assert hall.bounds[3] == pytest.approx(7.732, abs=0.01)             # the landing strip only
    (ax, ay), (bx, by) = openings[0]["line"]
    assert openings[0]["width"] == pytest.approx(math.dist((ax, ay), (bx, by)), abs=1e-3)
    assert openings[0]["width"] == pytest.approx(2.68, abs=0.1)


def test_a_drawn_door_read_on_a_wall_copy_outranks_the_gap_read_over_it():
    """real07 C0047 (the user's correction: 'the entrance to the room is wrong door'): the Kat Kal. door (its drawn
    swing) was read on one copy of a wall read twice, a 1.56 m unclassified gap over it on the kept copy; the door was
    merged into the gap and lost. The drawn door stays, the gap is merged into it; a door without drawn evidence (the
    architect's) still goes into the drawn opening (real06)."""
    from wenart.ingest.generic import twin_walls as TWW

    def wall(wid, a, b, t):
        return {"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t, "evidence": []}

    def b(door_ev, operation="swing"):
        return {"walls": [wall("w_12", (3.0, 2.19), (9.0, 2.19), 0.2), wall("w_11", (3.5, 2.19), (8.0, 2.19), 0.2)],
                "openings": [{"id": "o_2", "type": "opening", "level_id": "L0", "wall_id": "w_12", "center": [5.36, 2.19],
                              "width": 1.56, "evidence": [{"method": "derived", "note": "unclassified gap content"}]},
                             {"id": "d_1", "type": "door", "level_id": "L0", "wall_id": "w_11", "center": [5.815, 2.19],
                              "width": 0.85, "evidence": door_ev, "operation": operation}]}
    swing = [{"method": "vector", "entity": "ARC:4434A", "note": "swing arc without a drawn leaf"}]
    drawn = b(swing)
    TWW.merge_twin_walls(drawn)
    assert [o["id"] for o in drawn["openings"]] == ["d_1"] and drawn["openings"][0]["wall_id"] == "w_12"
    assert drawn["openings_merged"][0]["id"] == "o_2" and drawn["openings_merged"][0]["merged_into"] == "d_1"
    inferred = b([])
    TWW.merge_twin_walls(inferred)
    assert [o["id"] for o in inferred["openings"]] == ["o_2"]
    # real06 (user, 29 Oct 2026: "is there a door behind it?"): a 'sliding door' of leaf lines without a swing is no
    # drawn door; the gap stays
    leaves = b([{"method": "vector", "note": "6 leaf/leaves drawn parallel to the wall without a swing arc"}], "sliding")
    TWW.merge_twin_walls(leaves)
    assert [o["id"] for o in leaves["openings"]] == ["o_2"]


# --------------------------------------------------------------------------
# Turns between ordered flights (review B2 CB-1, B2-ST1, B2-ST2, B2-ST3)
# --------------------------------------------------------------------------

def _treads_covered(plan):
    """The largest share of a tread's depth any turn covers (a tread: between two nosings across the flight)."""
    from shapely.geometry import Polygon
    from wenart.blender import parametric as P
    worst = 0.0
    for t in plan.get("turns") or []:
        tp = Polygon(t["polygon"])
        for f in plan["flights"]:
            for n0, n1 in zip(f["nosings"], f["nosings"][1:]):
                depth = math.dist(n0, n1)
                tread = P._band(n0, f["rise_dir"], f["width"], 0.0, depth)
                worst = max(worst, tp.intersection(tread).area / max(f["width"], 1e-9))
    return worst


def _ordered(flights, landing=None, winders=None):
    from wenart.blender import parametric as P
    stair = {"flights": flights, "landing": landing, "direction": None, "direction_assumed": False,
             "flights_ordered": True, "turn_winders": winders or [0] * (len(flights) - 1), "turn_assumed": False}
    return P.stair_plan({"footprint": {"center": [8.5, 4.5], "size": [3.0, 2.5], "rotation_deg": 0.0},
                         "stair": stair}, 3.0)


def test_a_staggered_u_turn_lies_beyond_the_first_flights_end():
    """review B2 CB-1 (real07 L0, the stair the user corrected: flight 2 starts one tread behind flight 1's end; the
    turn was the strip between the two rows, over flight 1's last tread, a 0.30 m step): the half landing lies beyond
    flight 1's last nosing, the stair's width deep, and covers no tread."""
    plan = _ordered([{"start": [9.6697, 3.96], "end": [7.4697, 3.96], "width": 0.96, "lines": 9},
                     {"start": [7.7447, 5.12], "end": [9.8704, 5.12], "width": 0.96, "lines": 9}])
    (turn,) = plan["turns"]
    xs = [q[0] for q in turn["polygon"]]
    assert max(xs) <= 7.7447 + 1e-6 and min(xs) <= 7.4697 - 0.9            # beyond flight 1's end, a width deep
    assert _treads_covered(plan) <= 0.03
    f1, f2 = plan["flights"]
    assert turn["z"] == pytest.approx(f1["top_z"]) and f2["base_z"] == pytest.approx(f1["top_z"])


def test_a_u_turn_with_offset_rows_is_a_full_half_landing():
    """review B2-ST2: arms offset by +-0.10 m: the turn is the stair's width deep beyond both arms, never a strip."""
    for off in (-0.10, 0.0, 0.10):
        plan = _ordered([{"start": [0.5, 0.0], "end": [0.5, 1.96], "width": 1.0, "lines": 8},
                         {"start": [1.6, 1.96 + off], "end": [1.6, 0.0], "width": 1.0, "lines": 8}])
        (turn,) = plan["turns"]
        ys = [q[1] for q in turn["polygon"]]
        assert max(ys) - max(1.96, 1.96 + off) >= 1.0 - 1e-6, off
        assert _treads_covered(plan) <= 0.03, off


def test_a_turn_stops_at_the_wall_beyond_it():
    """review B2 CB-1: the half landing stops at the first wall (real07: the stair hall's wall 1.05 m past flight 1)."""
    from wenart.blender import parametric as P
    stair = {"flights": [{"start": [9.6697, 3.96], "end": [7.4697, 3.96], "width": 0.96, "lines": 9},
                         {"start": [7.7447, 5.12], "end": [9.8704, 5.12], "width": 0.96, "lines": 9}],
             "landing": None, "direction": None, "direction_assumed": False, "flights_ordered": True,
             "turn_winders": [0], "turn_assumed": False}
    walls = [{"start": [6.52, 3.0], "end": [6.52, 6.0], "thickness": 0.33}]
    plan = P.stair_plan({"footprint": {"center": [8.5, 4.5], "size": [3.0, 2.5], "rotation_deg": 0.0},
                         "stair": stair}, 3.0, walls=walls)
    xs = [q[0] for q in plan["turns"][0]["polygon"]]
    assert min(xs) == pytest.approx(6.52 + 0.165, abs=1e-3)


def test_a_curved_stairs_turns_cover_no_tread():
    """review B2-ST1 (synthetic-22: each chord's flat turn covered 70 % of the chord's last tread, 4.9 cm left): the
    tread between two chords lies between their lines."""
    texts, strokes = _curved()
    _data, plan = _built(texts, strokes)
    assert len(plan["turns"]) == 5 and _treads_covered(plan) <= 0.03


def test_overlapping_flights_are_named_and_their_turn_stays_off_their_treads():
    """review B2-ST3 (real18 L3's side stairs: the 3-line arm and the 12-line arm overlap in plan)."""
    plan = _ordered([{"start": [8.2685, 5.6173], "end": [8.2685, 6.0175], "width": 0.71, "lines": 3},
                     {"start": [8.3957, 5.9996], "end": [6.2288, 5.9996], "width": 0.70, "lines": 12}])
    assert any("overlap in plan" in w for w in plan["warnings"])
    assert _treads_covered(plan) <= 0.03


# --------------------------------------------------------------------------
# Review B2: openings
# --------------------------------------------------------------------------

def test_a_room_whose_entrance_gap_holds_a_stray_line_keeps_the_inner_wall_guard():
    """review B2-GEN-01 (real03's living rooms, real07's dining room: their entrances read as 'unclassified gap
    content' made them light wells): a gap of a door's width is a room's way in, whatever lies in it."""
    walls = _box_with_inner_wall()
    stray = _line((4.3, 1.98), (4.6, 2.02), "KAPI")
    _w, openings, log, _o = O.gaps_and_openings(walls, _wall_lines("DUVAR") + [stray], "t.dxf", 1)
    assert not [o for o in openings if o.kind == "window"]
    assert [e for e in log if e.get("rule") == "inner_wall_faces"]


def test_a_closed_room_with_a_room_label_is_never_open_to_the_sky():
    """review B2-GEN-01: no door read into the north room, but its label says it is a room one lives in."""
    walls = [w for w in _box_with_inner_wall() if w.entity not in ("I1", "I2")]
    walls.append(R.wall((0.125, 2.0), (5.875, 2.0), t=0.15, entity="I"))
    _w, openings, log, _o = O.gaps_and_openings(walls, _wall_lines("DUVAR"), "t.dxf", 1, room_points=[(3.0, 3.0)])
    assert not [o for o in openings if o.kind == "window"]
    _w, openings, log, _o = O.gaps_and_openings(walls, _wall_lines("DUVAR"), "t.dxf", 1)
    assert [round(o.width, 2) for o in openings if o.kind == "window"] == [0.8]          # no label: a light well


def _framed(walls):
    """``walls`` inside a frame loop 20 x 20 m (a sheet frame read as walls), well clear of them."""
    return walls + [R.wall((-7, -7), (13, -7), t=0.1, entity="F1"), R.wall((13, -7), (13, 13), t=0.1, entity="F2"),
                    R.wall((13, 13), (-7, 13), t=0.1, entity="F3"), R.wall((-7, 13), (-7, -7), t=0.1, entity="F4")]


def test_a_frame_loop_round_the_building_makes_no_inner_wall_outer_and_no_outer_wall_inner():
    """review B2 FC-02 (real15: the sheet frame read as walls, its hole holding the balconies' labels, switched the
    inner-wall rule off for whole levels): faces, not holes; the ground between the frame and the building is outside."""
    walls = _framed(_box_with_inner_wall())
    _w, openings, log, _o = O.gaps_and_openings(walls, _wall_lines("DUVAR"), "t.dxf", 1, outdoor_points=[(9.0, 2.0)])
    assert not [o for o in openings if o.kind == "window"]
    assert [e for e in log if e.get("rule") == "inner_wall_faces"]
    lines = _wall_lines("DUVAR", x0=1.0, x1=2.5, y=4.0)
    _w, openings, _l, _o = O.gaps_and_openings(walls, lines, "t.dxf", 1)
    assert [round(o.width, 2) for o in openings if o.kind == "window"] == [1.5]


def test_on_a_page_that_draws_its_windows_wall_face_lines_alone_are_no_window():
    """review B2 FC-04 (real06: its windows are PENCERE frames with DENIZLIK sills; three solid piers per floor were
    read as windows from the DUVAR pair between the plaster faces): on such a page, an outer-wall stretch whose only
    'glass' is wall-face lines is no window; a window drawn on the window layer stays."""
    walls = _box_with_inner_wall()
    pier = _wall_lines("DUVAR", x0=1.0, x1=2.5, y=4.0)
    window = _wall_lines("PENCERE", x0=3.0, x1=4.0, y=4.0)
    _w, openings, log, _o = O.gaps_and_openings(walls, pier + window, "t.dxf", 1)
    assert [round(o.width, 2) for o in openings if o.kind == "window"] == [1.0]
    assert [e for e in log if e.get("rule") == "wall_faces_only"]
    assert O.window_symbols(window) and not O.window_symbols(pier)


def _rest_index(strokes):
    return O.StrokeIndex(strokes, 0.0)


def test_the_rest_of_a_gap_beside_a_door_is_read_again_window_and_pier():
    """review B2 FC-01 / REG-1 (real06 L1: the 1.95 m balcony gap holds a 0.90 m window, PENCERE glass and DENIZLIK
    sills, a 0.30 m DUVAR pier and the drawn 0.70 m door; the rest beside the door was typed a 1.23 m balcony door):
    the rest is a window, the pier is wall."""
    from wenart.ingest.model import OpeningItem
    host = SimpleNamespace(axis="h", c=0.0, t=0.25)
    strokes = [_line((2.18, -0.03), (3.08, -0.03), "PENCERE"), _line((2.18, 0.03), (3.08, 0.03), "PENCERE"),
               _line((2.18, -0.12), (3.08, -0.12), "DENIZLIK"), _line((2.18, 0.12), (3.08, 0.12), "DENIZLIK"),
               _line((3.08, -0.10), (3.38, -0.10), "DUVAR"), _line((3.08, 0.10), (3.38, 0.10), "DUVAR")]
    gap = OpeningItem(kind="opening", width=1.95, center=(3.175, 0.0), rotation_deg=0.0, box=[0, 0, 1, 1], entity="g",
                      evidence={"note": "unclassified gap content"}, type_raw="unclassified gap content")
    existing = [gap]
    ctx = SimpleNamespace(box=lambda pts: [0, 0, 1, 1], evidence=lambda m, c, e, box_units=None: {"method": m})
    assert O._door_in_gap(existing, host, 3.776, 0.70, 0.0, ctx, {}, index=_rest_index(strokes)) is None
    (rest,) = existing
    assert rest.kind == "window" and rest.width == pytest.approx(3.08 - 2.20, abs=0.01)
    assert rest.evidence["rule"] == "gap_rest_window"


def test_the_rest_of_a_gap_over_a_column_is_wall_and_an_open_rest_is_the_doors_leftover():
    """review B2 REG-4 (real07 L1: a 0.40 m rest kept through a column and a jamb nub): a rest under wall-drawing faces
    is wall; with no open part left the gap is the door's. An open rest is marked the door's leftover (rest_of), which
    the facade-gap and unsure-passage rules leave alone."""
    from wenart.blender import architect_actions as AA
    from wenart.ingest.model import OpeningItem
    host = SimpleNamespace(axis="v", c=11.74, t=0.25)
    column = _line((11.692, 5.191), (11.692, 5.891), "KOLON"), _line((11.792, 5.191), (11.792, 5.891), "KOLON")
    gap = OpeningItem(kind="opening", width=1.54, center=(11.74, 6.12), rotation_deg=90.0, box=[0, 0, 1, 1], entity="g",
                      evidence={}, type_raw="unclassified gap content")
    ctx = SimpleNamespace(box=lambda pts: [0, 0, 1, 1])
    existing = [gap]
    assert O._door_in_gap(existing, host, 6.44, 0.90, 0.0, ctx, {}, index=_rest_index(list(column))) == 0
    open_gap = OpeningItem(kind="opening", width=1.54, center=(11.74, 6.12), rotation_deg=90.0, box=[0, 0, 1, 1],
                           entity="g", evidence={}, type_raw="unclassified gap content")
    existing = [open_gap]
    assert O._door_in_gap(existing, host, 6.44, 0.90, 0.0, ctx, {}, index=_rest_index([]), door_name="d") is None
    assert existing[0].evidence["rest_of"] == "d" and existing[0].width == pytest.approx(0.64, abs=0.01)
    as_dict = {"type": "opening", "type_raw": "unclassified gap content", "evidence": [existing[0].evidence]}
    assert not AA.unsure_passage(as_dict)


def test_any_drawn_door_in_a_gap_of_its_wall_takes_its_part_and_drawn_stubs_stay_wall():
    """review B2 FC-06 / REG-3 (real07 L1: a 1.72 m gap over the 0.90 m door made by the gap classifier and its tag,
    across 0.30 m and 0.60 m DUVAR stubs): one 0.90 m door, no opening."""
    from wenart.ingest.model import OpeningItem
    walls = [R.wall((9.0, 7.09), (12.5, 7.09), t=0.18, entity="W")]
    gap = OpeningItem(kind="opening", width=1.72, center=(10.7924, 7.09), rotation_deg=0.0, box=[0, 0, 1, 1],
                      entity="g", evidence={}, type_raw="unclassified gap content")
    door = OpeningItem(kind="door", width=0.90, center=(10.6474, 7.09), rotation_deg=0.0, box=[0, 0, 1, 1], entity="d",
                       evidence={"method": "vector"}, operation="swing")
    stubs = [_line((9.892, 7.04), (10.192, 7.04), "DUVAR"), _line((9.892, 7.14), (10.192, 7.14), "DUVAR"),
             _line((11.092, 7.04), (11.692, 7.04), "DUVAR"), _line((11.092, 7.14), (11.692, 7.14), "DUVAR")]
    got = O.doors_in_gaps(walls, [gap, door], stubs, "t.dxf", 1, 1.0)
    assert [(o.kind, round(o.width, 2)) for o in got] == [("door", 0.9)]
    assert "takes its part of the gap" in got[0].evidence["note"]
    # a 'door' of parallel leaf lines alone (real06's kitchen gap) takes no gap
    slide = dataclasses.replace(door, operation="sliding")
    assert O.doors_in_gaps(walls, [gap, slide], stubs, "t.dxf", 1, 1.0) is None


def test_window_and_glass_words_of_wall_layers():
    """review B2 FC-09: 'A-WALL-CURT' (AIA), 'DUVAR_CAMLI' and 'DUVARCAM' name glass on a wall layer."""
    for name in ("A-WALL-CURT", "DUVAR_CAMLI", "DUVARCAM"):
        assert not O.wall_face_layer(name), name
    assert O.wall_face_layer("DUVARLAR") and O.wall_face_layer("DUVAR-CAMBAZ")


def test_a_drawn_double_door_on_a_wall_copy_outranks_the_gap_over_it():
    """review B2 CB-3: the C0047 rule for double doors (two swings drawn)."""
    from wenart.ingest.generic import twin_walls as TWW

    def wall(wid, a, b, t):
        return {"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t, "evidence": []}
    b = {"walls": [wall("w_12", (3.0, 2.19), (9.0, 2.19), 0.2), wall("w_11", (3.5, 2.19), (8.0, 2.19), 0.2)],
         "openings": [{"id": "o_2", "type": "opening", "level_id": "L0", "wall_id": "w_12", "center": [5.5, 2.19],
                       "width": 1.9, "evidence": [{"method": "derived", "note": "unclassified gap content"}]},
                      {"id": "d_1", "type": "door", "level_id": "L0", "wall_id": "w_11", "center": [5.5, 2.19],
                       "width": 1.6, "operation": "double", "evidence": [{"method": "vector", "entity": "ARC:1,ARC:2"}]}]}
    TWW.merge_twin_walls(b)
    assert [o["id"] for o in b["openings"]] == ["d_1"] and b["openings_merged"][0]["id"] == "o_2"


# --------------------------------------------------------------------------
# Review B2: size tags and lift doors
# --------------------------------------------------------------------------

def test_tags_go_to_the_doors_whose_leaves_they_are_written_along():
    """review B2 FC-05 (real10 L0-L6, right half: '90/210' along door A's leaf, '110/230' along B's, '100/225' along
    C's, but the 100/225 nearer A's span): each tag goes to the door whose drawn leaf it stands by."""
    from wenart.ingest.generic import core as C
    from wenart.ingest.model import OpeningItem

    def door(w, c, rot, ent):
        return OpeningItem(kind="door", width=w, center=c, rotation_deg=rot, box=[0, 0, 1, 1], entity=ent,
                           evidence={"entity": ent})
    a, b, c = door(1.05, (14.96, 6.48), 0.0, "LA"), door(1.03, (16.07, 6.48), 0.0, "LB"), door(1.10, (13.64, 7.24),
                                                                                                90.0, "LC")
    leaves = [_line((15.31, 5.63), (15.31, 6.48), "KAPI", sid="LA"), _line((15.615, 5.48), (15.615, 6.48), "KAPI",
                                                                          sid="LB"),
              _line((13.82, 6.815), (14.71, 6.815), "KAPI", sid="LC")]
    tags = [_tag("100/225", 14.343, 6.899, "TEXT"), _tag("90/210", 15.225, 5.968, "TEXT"),
            _tag("110/230", 15.744, 5.866, "TEXT")]
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [a, b, c], tags, 1.0, strokes=leaves)
    assert [round(o.width, 2) for o in got] == [0.9, 1.1, 1.0]


def test_a_tag_by_a_drawn_door_and_a_gap_5mm_nearer_stays_the_doors_whatever_the_rounding():
    """review B2 CB-6: equally near is within 1 cm of the tag's nearest pair, not a centimetre bucket."""
    from wenart.ingest.generic import core as C
    for y in (1.7451, 1.7400, 1.7399, 1.7351):
        gap = _gap(1.56, (5.36, 2.19))
        door = _op("door", 0.85, (5.815, 2.195))
        assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [gap, door], [_tag("80/210", 5.63, y, "DOGRAMA")],
                            1.0) is None, y


def test_a_door_drawn_twice_does_not_use_up_its_neighbours_tag():
    """review B2 CB-4: a spot clash skips the pair, the tag may still reach its own gap."""
    from wenart.ingest.generic import core as C
    stack = [_op("door", 0.80, (0.0, 0.0)), _op("door", 0.80, (0.0, 0.0)), _gap(0.80, (1.3, 0.0))]
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], stack,
                       [_tag("80/210", 0.0, 0.3, "TEXT"), _tag("80/210", 0.62, 0.3, "TEXT")], 1.0)
    assert got is not None and got[2].kind == "door"


def test_a_mattress_size_is_no_door_tag_on_a_plain_layer():
    """review B2-GEN-02: '160/200' (a bed's size) on YAZI or '0' beside a 0.90 m gap changes nothing; a plain tag never
    widens a gap past its jambs; on a door layer a 200 cm tag still sets its door."""
    from wenart.ingest.generic import core as C
    for layer in ("YAZI", "0"):
        assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [_gap(0.90, (2.0, -3.0))],
                            [_tag("160/200", 2.0, -2.7, layer)], 1.0) is None, layer
        assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [_gap(0.90, (2.0, -3.0))],
                            [_tag("160/210", 2.0, -2.7, layer)], 1.0) is None, layer
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [_gap(0.80, (2.0, -3.0))], [_tag("80/200", 2.0, -2.7, "KAPI")],
                       1.0)
    assert got[0].kind == "door" and got[0].height == pytest.approx(2.0)


def test_a_door_hung_at_a_jamb_is_marked_inferred():
    """review B2-GEN-04: a size-tag door moved to the jamb nearer its tag is an inference (method inferred, position
    assumed); a tag over the gap's middle third leaves it in the middle, the place still inferred."""
    from wenart.ingest.generic import core as C
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [_gap(1.56, (5.36, -3.0))], [_tag("80/210", 5.9, -2.7, "TEXT")],
                       1.0)
    door = got[0]
    assert door.center[0] == pytest.approx(6.14 - 0.40) and door.evidence["method"] == "inferred"
    assert door.evidence["rule"] == "size_tag_jamb" and "position" in door.assumed
    got = C._door_tags(SimpleNamespace(notes=[]), "x", [], [_gap(1.56, (5.36, -3.0))],
                       [_tag("80/210", 5.40, -2.7, "TEXT")], 1.0)
    assert got[0].center[0] == pytest.approx(5.36) and got[0].evidence["method"] == "inferred"


def test_a_lift_door_is_on_the_landing_side_and_no_wider_than_a_lift_door():
    """review B2 FC-07 (real21: the second shaft took a 2.22 m gap towards a flat's bedroom; real10 C0034, the user: 'a
    sliding lift door on each floor onto the shared hall'): a gap wider than a lift door, or one into a flat's room
    only, is no landing door; the door is inferred towards the hall."""
    from wenart.ingest import twins as TW

    def room(rid, label, rtype, poly):
        return {"id": rid, "level_id": "L1", "label": label, "room_type": rtype, "polygon": poly}
    shaft = room("r_L1_asansor", "Asansör", "shaft", [[0, 0], [1.6, 0], [1.6, 1.8], [0, 1.8]])
    hall = room("r_L1_hall", "Kat Holü", "hall", [[0, 2.0], [4, 2.0], [4, 4], [0, 4]])
    bed = room("r_L1_oda", "Oda", "bedroom", [[1.8, 0], [4, 0], [4, 1.8], [1.8, 1.8]])
    walls = [{"id": "w1", "level_id": "L1", "start": [-0.1, 1.9], "end": [4.1, 1.9], "thickness": 0.2}]
    for width in (2.2, 0.9):
        gap = {"id": "o1", "level_id": "L1", "type": "opening", "center": [1.7, 0.9], "width": width}
        openings = [gap]
        TW.lift_doors([shaft, hall, bed], openings, walls)
        assert gap["type"] == "opening", width
        assert openings[-1]["id"] == "d_r_L1_asansor_lift" and abs(openings[-1]["center"][1] - 1.9) < 1e-6
    good = {"id": "o2", "level_id": "L1", "type": "opening", "center": [0.8, 1.9], "width": 0.9}
    far = {"id": "o3", "level_id": "L1", "type": "opening", "center": [1.7, 0.9], "width": 1.2}
    TW.lift_doors([shaft, hall, bed], [far, good], walls)
    assert good["type"] == "door" and good.get("lift_door") and far["type"] == "opening"


# --------------------------------------------------------------------------
# Review B2: tread numbers
# --------------------------------------------------------------------------

def test_a_dimension_text_and_an_unconfirmed_skip_join_no_stair():
    """review B2 REG-2 (real07 L0, the user-corrected stair: the wall dimension '20' on OLÇÜ 0.18 m past the '18' made
    the upper arm 11 treads, 0.65 m into the Antre): a number on a dimension layer joins no chain of numbers on another
    layer, a skip needs the next number to confirm it, and a number past the last drawn tread line adds no tread."""
    pts = [(9.67 - 0.275 * k, 3.96) for k in range(9)] + [(7.74 + 0.266 * k, 5.12) for k in range(9)]
    texts = [_t(k + 1, x, y) for k, (x, y) in enumerate(pts)]
    dim = _t(20, 9.90, 5.30)
    dim.evidence = [{"layer": "OLÇÜ"}]
    chain = SN.chains(texts + [dim])[0]
    assert [v for v, _p, _t in chain] == list(range(1, 19))
    plain20 = _t(20, 9.90, 5.30)
    assert [v for v, _p, _t in SN.chains(texts + [plain20])[0]] == list(range(1, 19))     # 19 missing: no bridge
    # a trailing number past the last drawn riser line is the arrival, no tread (the drawn lines decide)
    riser_lines = [_line((7.74 + 0.266 * k - 0.133, 4.64), (7.74 + 0.266 * k - 0.133, 5.60), "MB") for k in range(9)]
    riser_lines += [_line((9.67 - 0.275 * k + 0.1375, 3.48), (9.67 - 0.275 * k + 0.1375, 4.44), "MB") for k in range(9)]
    st = SN.stair_of(chain, riser_lines)
    assert [f["lines"] for f in st["flights"]] == [9, 9]


def test_a_u_stair_with_close_arms_keeps_its_first_number_after_the_turn():
    """review B2 CB-2: arms 0.9-1.1 m apart: the 9 across the turn was skipped for the 10 and turned into a winder."""
    for gap_m in (0.9, 1.0, 1.1, 1.3):
        pts = [(0.5, 0.2 + 0.27 * k) for k in range(8)] + [(0.5 + gap_m, 0.2 + 0.27 * (7 - k)) for k in range(8)]
        chain = SN.chains([_t(k + 1, x, y) for k, (x, y) in enumerate(pts)])[0]
        assert [v for v, _p, _t in chain] == list(range(1, 17)), gap_m
        st = SN.stair_of(chain, [])
        assert [f["lines"] for f in st["flights"]] == [8, 8] and st["turn_winders"] == [0], gap_m


def test_the_build_path_knows_the_turns_of_ordered_flights():
    """review B2-ST4 (synthetic-22: the balustrade broke at every chord turn, the turns stood outside the stair's area
    and its floor opening): each side path runs on across every turn, the turns are in the stair's area and, where
    they lack headroom, in the opening; the surface over a turn is the turn's."""
    from shapely.geometry import Polygon
    from wenart.blender import stair_access as SA
    from wenart.blender import stair_rails as SR
    texts, strokes = _curved()
    _data, plan = _built(texts, strokes)
    turns = plan["turns"]
    for side in SR.side_paths(plan):
        legs = side["legs"]
        assert sum(1 for g in legs if g["what"] == "landing") >= len(turns)
        assert all(math.dist(a["b"], b["a"]) < 1e-6 for a, b in zip(legs, legs[1:]))
    area = SA.stair_area(plan)
    assert all(area.buffer(1e-6).contains(Polygon(t["polygon"]).representative_point()) for t in turns)
    hole = Polygon(SA.opening_polygon(plan, 2.8))
    high = [t for t in turns if 2.8 - t["z"] < SA.HEADROOM_M]
    assert high and all(hole.buffer(1e-6).contains(Polygon(t["polygon"]).representative_point()) for t in high)
    t = turns[0]
    c = Polygon(t["polygon"]).representative_point()
    assert SR.surface_z(plan, (c.x, c.y)) == pytest.approx(t["z"])


def _r18_u():
    pts = [(7.0 + 0.26 * k, 8.75) for k in range(6)] + [(8.50, 8.709), (8.908, 8.706), (8.558, 6.621)]
    pts += [(8.25 - 0.25 * k, 6.67) for k in range(7)]
    lines = [_line((7.0 + 0.26 * k + 0.13, 8.25), (7.0 + 0.26 * k + 0.13, 9.25), "MERD") for k in range(-1, 5)]
    lines += [_line((8.377, 8.25), (8.377, 9.25), "MERD"), _line((8.377, 6.17), (8.377, 7.17), "MERD")]
    lines += [_line((8.125 - 0.25 * k, 6.17), (8.125 - 0.25 * k, 7.17), "MERD") for k in range(7)]
    walls = [_line((9.377, 6.55), (9.377, 8.95), "DUVAR"), _line((9.527, 6.55), (9.527, 8.95), "DUVAR")]
    return pts, lines, walls


def test_both_ends_of_a_u_turn_are_judged_alike():
    """review B2 REG-5 (real18's U stairs: the 7 and the 9 are wedges between a riser and a radial from the newel, the
    8 the turn tread beyond the radials; only the 9 was read as a winder): a number whose tread a radial bounds, ahead
    of it or behind it, is a winder at either end."""
    pts, lines, walls = _r18_u()
    radials = [_line((8.377, 7.85), (8.855, 8.95), "MERD"), _line((8.377, 7.65), (8.855, 6.55), "MERD")]
    chain = SN.chains([_t(k + 1, x, y) for k, (x, y) in enumerate(pts)])[0]
    st = SN.stair_of(chain, lines + radials + walls)
    assert [f["lines"] for f in st["flights"]] == [6, 7] and st["turn_winders"] == [3]


def test_a_u_landing_stops_at_the_end_wall():
    """review B2 REG-5: the half landing's band is built from the stair's own lines and stops at the inside face of the
    first wall line across the arms beyond them (real18: it ran through the 0.15 m end wall)."""
    pts, lines, walls = _r18_u()
    pts[6:9] = [(8.75, 8.45), (9.0, 7.95), (9.0, 7.4)]                # the turn's numbers, no line drawn at them
    chain = SN.chains([_t(k + 1, x, y) for k, (x, y) in enumerate(pts)])[0]
    st = SN.stair_of(chain, lines + walls)
    assert st["landing"] is not None and max(q[0] for q in st["landing"]["polygon"]) <= 9.377 + 1e-6
    assert max(x for x, _y in st["polygon"].exterior.coords) <= 9.377 + 1e-6


def test_a_fan_of_winders_at_a_treads_step_is_read_as_winders():
    """review B2 FC-08 (real13 L3: 1-10 straight, 11-14 between radial lines from the inner corner, then 15): the
    radial edges mark winders even where their steps look like a tread's (as many as an arm of three numbers leaves)."""
    p13 = [(6.42 - 0.2 * k, -0.29) for k in range(10)] + [(4.27, -0.31), (3.83, -0.31), (3.73, -0.63), (3.73, -0.90),
                                                           (3.71, -1.19)]
    l13 = [_line((6.42 - 0.2 * k + 0.1, -0.75), (6.42 - 0.2 * k + 0.1, 0.15), "MERD") for k in range(10)]
    l13 += [_line((4.4, -1.03), (4.09, -0.13), "MERD"), _line((4.4, -1.03), (3.41, -0.13), "MERD"),
            _line((4.4, -1.03), (3.41, -0.66), "MERD"), _line((4.56, -0.75), (4.56, 0.15), "MERD"),
            _line((3.3, -1.08), (4.3, -1.08), "MERD")]
    chain = SN.chains([_t(k + 1, x, y) for k, (x, y) in enumerate(p13)])[0]
    st = SN.stair_of(chain, l13)
    assert [f["lines"] for f in st["flights"]][0] == 10 and st["turn_winders"][0] >= 2
