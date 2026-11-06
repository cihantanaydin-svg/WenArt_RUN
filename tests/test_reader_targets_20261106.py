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

import math
from types import SimpleNamespace

import pytest

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
    # the chord flights run along the walking line, one after the other, every tread counted once
    fl = st["flights"]
    assert sum(f["lines"] for f in fl) == 18
    assert all(math.dist(a["end"], b["start"]) < 1e-6 for a, b in zip(fl, fl[1:]))


def test_numbers_on_a_straight_line_are_no_curved_stair():
    texts = [_t(k, 1.0 + 0.27 * k, 2.0) for k in range(1, 12)]
    assert SN.curved_stair_of(SN.chains(texts)[0], [])["skip"]
    st = SN.stair_of(SN.chains(texts)[0], [])
    assert st["turn"] == "straight"


def test_the_first_winder_is_not_the_arms_last_tread():
    """synthetic-15 (UL286): 1-6 on the lower arm (0.27 m apart), 7-11 round the turn (0.39-0.51 m apart, 7 only 7
    degrees off the arm's line), 12-17 back on the upper arm: five winders, not three."""
    pts = [(8.835 + 0.27 * k, 6.5735) for k in range(6)]
    pts += [(10.5749, 6.5264), (10.9874, 6.8261), (11.145, 7.311), (10.9874, 7.7959), (10.5749, 8.0956)]
    pts += [(10.185 - 0.27 * k, 8.0485) for k in range(6)]
    texts = [_t(k + 1, x, y) for k, (x, y) in enumerate(pts)]
    chain = SN.chains(texts)[0]
    assert [v for v, _p, _t in chain] == list(range(1, 18))
    arms = SN._arms([c[1] for c in chain])
    assert [len(a) for a in arms] == [6, 6]
    st = SN.stair_of(chain, [])
    assert st["winders"] == 5 and st["turn"] == "U"


def test_a_stair_piece_holding_a_chain_takes_what_the_numbers_say():
    """The stair rule's piece keeps its footprint and flights; the numbers give the treads drawn, the winders, the rise
    direction (drawn, so the architect never flips it) and the flights' order (the flight by number 1 first)."""
    pts = [(8.835 + 0.27 * k, 6.5735) for k in range(6)]
    pts += [(10.5749, 6.5264), (10.9874, 6.8261), (11.145, 7.311), (10.9874, 7.7959), (10.5749, 8.0956)]
    pts += [(10.185 - 0.27 * k, 8.0485) for k in range(6)]
    texts = [_t(k + 1, x, y) for k, (x, y) in enumerate(pts)]
    chain = SN.chains(texts)[0]
    # the stair rule read the upper flight first, both running +x, with a flat landing and an assumed direction
    stair = {"flights": [{"start": [8.97, 8.06], "end": [10.05, 8.06], "width": 1.2, "lines": 5, "spacing": 0.27},
                         {"start": [8.97, 6.59], "end": [10.05, 6.59], "width": 1.2, "lines": 5, "spacing": 0.27}],
             "landing": {"polygon": [[10.05, 5.95], [11.7, 5.95], [11.7, 8.7], [10.05, 8.7]], "depth": 1.65},
             "direction": [1.0, 0.0], "direction_assumed": True, "turn": "U", "turn_assumed": True, "reason": "rule"}
    piece = SimpleNamespace(details={"stair": stair}, evidence={"note": "stair rule"})
    said = SN.enrich(piece, chain, SN.stair_of(chain, []))
    assert "17 treads drawn" in said and "5 winder(s)" in said
    assert stair["steps_drawn"] == 17 and stair["winders"] == 5
    assert stair["direction_assumed"] is False and stair["turn_assumed"] is False
    # the lower flight (number 1 at x 8.84) first, rising +x; the upper flight turned round, rising -x
    assert stair["flights"][0]["start"] == [8.97, 6.59] and stair["flights"][0]["end"] == [10.05, 6.59]
    assert stair["flights"][1]["start"] == [10.05, 8.06] and stair["flights"][1]["end"] == [8.97, 8.06]
    assert stair["direction"] == [1.0, 0.0]


def test_numbered_treads_that_fit_no_shape_still_give_the_treads_drawn():
    texts = [_t(k, 1.0 + 0.27 * k, 2.0) for k in range(1, 12)]
    chain = SN.chains(texts)[0]
    piece = SimpleNamespace(details={"stair": {"flights": [], "direction_assumed": True}}, evidence={})
    assert SN.enrich(piece, chain, {"skip": "no shape"}) == "11 treads drawn"
    assert piece.details["stair"]["steps_drawn"] == 11 and piece.details["stair"]["direction_assumed"] is True


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


def test_a_wide_or_low_tag_on_a_text_layer_is_no_door():
    """A '165/210' (real10's kitchen windows, C0055) or a '120/120' on a plain text layer says no door."""
    from wenart.ingest.generic import core as C
    from wenart.ingest.model import OpeningItem

    gap = OpeningItem(kind="opening", width=1.65, center=(2.0, 0.0), rotation_deg=0.0, box=[0, 0, 1, 1], entity="g",
                      evidence={}, type_raw="unclassified gap content")
    for text in ("165/210", "120/120"):
        assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [gap], [_tag(text, 2.0, 0.3, "TEXT")], 1.0) is None


def test_a_door_high_tag_on_a_text_layer_leaves_a_drawn_window_alone():
    from wenart.ingest.generic import core as C
    from wenart.ingest.model import OpeningItem

    win = OpeningItem(kind="window", width=1.2, center=(2.0, 0.0), rotation_deg=0.0, box=[0, 0, 1, 1], entity="w",
                      evidence={})
    assert C._door_tags(SimpleNamespace(notes=[]), "x", [], [win], [_tag("120/210", 2.0, 0.3, "TEXT")], 1.0) is None


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


