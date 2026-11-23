"""Long walls where none is drawn (23 Nov 2026, the user's queue: "then the next wall class (long walls where none is
drawn)"; lesson UL374): an inferred wall needs the drawing to show something where it stands. A wide gap with nothing
drawn across it is an open passage (no bridge); a mirror copy onto an empty band is no wall. Most tests are must-not-fire
cases: a gap closed by a sliding door, a garage door line, a glazed screen, a door swing or a hatch keeps its bridge,
and so does an empty gap between two labelled rooms; a mirror copy along drawn face lines stays. Pure geometry in
page metres."""
from __future__ import annotations

from wenart.ingest.generic import wide_gaps as WG
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import OpeningItem, WallItem


def _st(pts, layer="0", arc=None, sid=None):
    return Stroke(id=sid or f"s{abs(hash((tuple(map(tuple, pts)), layer))) % 10 ** 8}", kind="arc" if arc else "line",
                  pts=[tuple(p) for p in pts], layer=layer, arc=arc)


GAP = ((2.0, 0.0), (6.0, 0.0))            # a 4 m gap between two jambs on y = 0, walls 0.25 m thick


# --- gap_drawn: what closes a gap ------------------------------------------------------------------------------------

def test_empty_gap_is_not_drawn():
    drawn, why = WG.gap_drawn(*GAP, 0.25, [])
    assert not drawn and "nothing drawn" in why


def test_annotations_never_close_a_gap():
    strokes = [_st([(0, 0.0), (8, 0.0)], "AKS"),                  # the grid line along the facade
               _st([(2, 0.05), (6, 0.05)], "OLCU"),               # a dimension line
               _st([(2, -0.02), (6, -0.02)], "YAZI")]             # a text underline
    assert not WG.gap_drawn(*GAP, 0.25, strokes)[0]


def test_lines_across_the_gap_are_no_closure():
    strokes = [_st([(4.0, -2.0), (4.0, 2.0)], "DUVAR"),          # a wall or railing running into the gap
               _st([(2.02, -0.12), (2.02, 0.12)], "DUVAR")]       # the jamb's cap line
    assert not WG.gap_drawn(*GAP, 0.25, strokes)[0]


def test_sliding_door_leaves_close_the_gap():
    """real07: the 1.9 m sliding door to the terrace, two leaves on tracks and no swing."""
    strokes = [_st([(2.05, 0.03), (4.1, 0.03)], "KAPI"), _st([(3.9, -0.03), (5.95, -0.03)], "KAPI")]
    assert WG.gap_drawn(*GAP, 0.25, strokes)[0]


def test_garage_door_line_closes_the_gap():
    strokes = [_st([(2.0, 0.0), (6.0, 0.0)], "GARAJ")]             # one line of an unknown layer along the gap
    assert WG.gap_drawn(*GAP, 0.25, strokes)[0]


def test_door_swing_closes_the_gap():
    arc = {"center": (2.1, 0.12), "radius": 0.9, "start_deg": 0.0, "end_deg": 90.0}
    pts = [(2.1 + 0.9 * c, 0.12 + 0.9 * s) for c, s in ((1, 0), (0.92, 0.38), (0.71, 0.71), (0.38, 0.92), (0, 1))]
    assert WG.gap_drawn(*GAP, 0.25, [_st([(3.0, -0.2), (3.0, 0.2)] + pts, "KAPI", arc=arc)])[0]


def test_door_swing_touching_only_the_jambs_closes_the_gap():
    """swiss-b16820 L1: 0.8 m door gaps whose leaf stands open into the room and whose arc meets the wall face only at
    the far jamb (the first version looked for arcs inside the trimmed band and dropped seven door gaps)."""
    import math
    gap = ((2.0, 0.0), (2.8, 0.0))
    arc = {"center": (2.0, 0.125), "radius": 0.8, "start_deg": 0.0, "end_deg": 90.0}
    pts = [(2.0 + 0.8 * math.cos(math.radians(a)), 0.125 + 0.8 * math.sin(math.radians(a))) for a in range(0, 91, 10)]
    assert WG.gap_drawn(*gap, 0.25, [_st(pts, "KAPI", arc=arc)])[0]
    leaf = _st([(2.0, 0.125), (2.0, 0.925)], "KAPI")                 # the open leaf alone runs across: no closure
    assert not WG.gap_drawn(*gap, 0.25, [leaf])[0]


def test_hatch_boundary_closes_the_gap():
    """A wall the drawing shows as hatch only (no face lines read as a wall)."""
    ring = [(2.0, -0.125), (6.0, -0.125), (6.0, 0.125), (2.0, 0.125), (2.0, -0.125)]
    assert WG.gap_drawn(*GAP, 0.25, [_st(ring, "TARAMA")])[0]


def test_short_pieces_along_the_gap_must_add_up():
    few = [_st([(3.0, 0.0), (3.3, 0.0)], "PENCERE")]               # 0.3 m of 4 m
    assert not WG.gap_drawn(*GAP, 0.25, few)[0]
    many = [_st([(2.1 + k, 0.0), (2.4 + k, 0.0)], "PENCERE") for k in range(4)]   # 1.2 m of 4 m
    assert WG.gap_drawn(*GAP, 0.25, many)[0]


def test_a_line_outside_the_band_is_no_closure():
    assert not WG.gap_drawn(*GAP, 0.25, [_st([(2, 0.6), (6, 0.6)], "PENCERE")])[0]   # a railing 0.6 m out


# --- the wide-gap bridge in the outer ring ---------------------------------------------------------------------------

def _wall(a, b, t=0.25):
    return WallItem(start=a, end=b, thickness=t, box=[], entity=f"LINE:{a}-{b}", evidence={"method": "vector"})


class _Ex:
    def __init__(self):
        self.notes = []
        self.report = {}


class _Lbl:
    def __init__(self, name, anchor, exterior=False):
        self.name, self.text, self.anchor, self.exterior = name, name, anchor, exterior
        self.room_type = None
        self.area_m2 = None


def _ring_with_gap():
    """A 10 x 6 m box whose bottom wall stops at x = 2 and starts again at x = 6: a 4 m gap in the outer ring."""
    return [_wall((0, 0), (2, 0)), _wall((6, 0), (10, 0)), _wall((10, 0), (10, 6)), _wall((10, 6), (0, 6)),
            _wall((0, 6), (0, 0))]


def test_outer_gap_with_nothing_drawn_is_marked_empty():
    from wenart.ingest.generic import core as C
    walls = _ring_with_gap()
    cands = WG.bridges(walls)
    assert cands                                                  # the gap is a candidate
    kept = C._sound_bridges(_Ex(), "L0", walls, cands, [])
    assert len(kept) == 1 and "nothing drawn" in kept[0]["empty_gap"]


def _closure(walls, labels):
    from wenart.ingest.generic import core as C
    from wenart.ingest.generic import topology as TP
    bw, _site, sw = TP.split_plot(walls, [], labels, level_id="L0")
    res = C._outer_gaps(_Ex(), "L0", walls, [], labels, "L0", sw, TP.outer_loop_problem(bw, []), [])
    return None if res is None else [w for w in res[0] if getattr(w, "inferred", False)]


def test_empty_gap_the_room_needs_keeps_its_bridge():
    """A room's own outer wall with an empty 4 m gap and no other closure: the bridge closes the room (as before;
    the level is never left without rooms, swiss-b2383)."""
    bridges = _closure(_ring_with_gap(), [_Lbl("SALON", (5, 3))])
    assert bridges is not None and len(bridges) == 1


def test_empty_gap_of_an_open_loggia_gets_no_bridge():
    """swiss-b1747 L1, b2486 L2: beside the gap the room needs, an open loggia's mouth (nothing drawn across it, no
    label in it) is no wall: its bridge is left out, the one the room needs stays."""
    walls = _ring_with_gap() + [_wall((10, 6), (13, 6)), _wall((13, 6), (13, 3)), _wall((10, 0), (13, 0))]
    cands = WG.bridges(walls)
    assert len(cands) == 2                                        # the room's gap and the loggia's mouth
    bridges = _closure(walls, [_Lbl("SALON", (5, 3))])
    assert bridges is not None and len(bridges) == 1
    (x0, y0), (x1, y1) = bridges[0].start, bridges[0].end
    assert abs(y0) < 0.01 and abs(y1) < 0.01                      # the room's own gap on y = 0


def test_outer_gap_with_a_sliding_door_keeps_its_bridge():
    from wenart.ingest.generic import core as C
    walls = _ring_with_gap()
    strokes = [_st([(2.05, 0.03), (4.1, 0.03)], "KAPI"), _st([(3.9, -0.03), (5.95, -0.03)], "KAPI")]
    cands = WG.bridges(walls)
    assert C._sound_bridges(_Ex(), "L0", walls, cands, strokes) == cands


def test_empty_gap_that_holds_a_wing_in_the_building_keeps_its_bridge():
    """swiss-b2294 (a first version): without the bridge a wing of drawn walls fell out of the building (to the site)
    and the plan's origin moved 2.92 m; a bridge whose removal sends a drawn wall out of the building stays."""
    walls = _ring_with_gap() + [_wall((10, 6), (17, 6)), _wall((17, 6), (17, 3)), _wall((17, 0), (17, -4)),
                                _wall((17, -4), (20, -4))]
    bridges = _closure(walls, [_Lbl("SALON", (5, 3))])
    assert bridges is not None and len(bridges) == 2


def test_empty_gap_between_two_labelled_rooms_keeps_its_bridge():
    """The user's must-not-fire: a wall the drawing shows by the room labels on both sides."""
    from wenart.ingest.generic import core as C
    walls = _ring_with_gap() + [_wall((0, -4), (10, -4)), _wall((0, -4), (0, 0)), _wall((10, -4), (10, 0))]
    labels = [_Lbl("SALON", (5, 3)), _Lbl("TERAS", (5, -2))]
    cands = WG.bridges(walls)
    kept = C._sound_bridges(_Ex(), "L0", walls, cands, [], labels=labels)
    assert kept == cands and not any(b.get("empty_gap") for b in kept)
    one = C._sound_bridges(_Ex(), "L0", walls, cands, [], labels=labels[:1])       # one room only: marked empty
    assert all(b.get("empty_gap") for b in one)
