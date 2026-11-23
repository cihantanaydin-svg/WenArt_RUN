"""23 Nov 2026 (real10 L-1, the user: "after walls, fix the light well and the two bathroom windows"; lessons UL367,
UL368, UL369): two openings with a drawn pier between them are two openings, and a wall read in two layers holds one opening.

The cause on the drawing: real10 L-1's light slot between two flats (1.72 x 3.73 m, no door) has the two bathrooms'
0.50 m windows on its inner side, with a 0.60 m pier between them: the T-head of the partition between the bathrooms,
drawn on DUVAR with its faces cut by the partition (no face pair as long as it is thick, so the wall reading drops it).
The gap split rule only cuts at wall pieces reaching into the band, so the two windows were one 1.80 m unclassified gap.
The 0.32 m slot wall is read as the bathrooms' 0.16 m wall and a 0.16 m layer of the slot's plaster beside it, each with
its gap; the slot's layer's gap kept the existing light-well rule (a doorless face that windows of other rooms open
onto) from typing the slot. The dataset bench's drawings lose their piers the same way: a closed DUVAR box with its hatch
between two windows, shorter than three times its thickness, touching no kept wall, dropped by the wall mask.

- ``openings._drawn_piers`` / ``_pier_parts``: wall material drawn inside a run gap between jamb lines on a wall or
  structure layer, its faces drawn, no window line across it, splits the gap; kept when a part is a door or window.
- ``openings._window_layer_lines``: lines on a window or glass layer confined to a gap that together span it are a
  window (real10's bathroom windows: a frame in 7 cm corner pieces round sash lines of 0.30-0.40 m in a 0.50 m gap).
- ``topology.stacked_windows``: an untyped gap of one layer of a wall read in two layers (parallel walls whose bands
  touch) that the other layer's windows face is those windows read again (no door), and they open onto the face.
- Must not fire: one window with a mullion on the window layer, a frame running on across a mullion drawn on the wall
  layer, jamb stubs at the gap ends only, a pier narrower than a masonry pier, a part narrower than an opening, lines
  that fill an empty gap with no door or window beside them, a door in the other layer, layers that do not touch.
- synthetic-36-light-well-piers read end to end through the CPU pipeline (generated into a temporary folder).
"""
from __future__ import annotations

import pytest
from shapely.geometry import Polygon

from wenart.ingest.generic import openings as O
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import OpeningItem, WallItem


# --- helpers: a wall along x on y = 0 (band -t/2 .. t/2) -------------------------------------------------------------

def _gap(a=0.0, b=1.8, t=0.25):
    return O.Gap("run", "h", 0.0, t, a, b, [])


def _line(sid, p, q, layer="0"):
    return Stroke(sid, "line", [p, q], layer=layer)


def _box(sid, x0, y0, x1, y1, layer="DUVAR"):
    return Stroke(sid, "polyline", [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer=layer, closed=True)


def _index(*strokes):
    return O.StrokeIndex(list(strokes), 0.0)


def _window(sid, x0, x1, t=0.25, layer="PENCERE"):
    """A window's lines from ``x0`` to ``x1``: both faces and two glass lines (the synthetic convention)."""
    h = t / 2
    return [_line(f"{sid}{k}", (x0, o), (x1, o), layer) for k, o in enumerate((-h, -h / 3, h / 3, h))]


def _pier_box(x0, x1, t=0.25, layer="DUVAR"):
    return [_box("pier", x0, -t / 2, x1, t / 2, layer)]


def _real10_pier(t=0.25):
    """real10 L-1's pier: the T-head of the partition between the two bathrooms (x 0.60 .. 1.20 of a 1.80 m gap), its
    face on the bathrooms' side cut by the 0.25 m partition (x 0.775 .. 1.025) running down from it, both jambs drawn."""
    h = t / 2
    return [_line("j0", (0.60, -h), (0.60, h), "DUVAR"), _line("j1", (1.20, -h), (1.20, h), "DUVAR"),
            _line("top", (0.60, h), (1.20, h), "DUVAR"),
            _line("bl", (0.60, -h), (0.775, -h), "DUVAR"), _line("br", (1.025, -h), (1.20, -h), "DUVAR"),
            _line("pl", (0.775, -h), (0.775, -2.0), "DUVAR"), _line("pr", (1.025, -h), (1.025, -2.0), "DUVAR")]


def _partition(t=0.25):
    """The partition's wall piece (vertical, ending at the band's face)."""
    w = WallItem(start=(0.9, -2.0), end=(0.9, -t / 2), thickness=0.25, box=[], entity="part", evidence={})
    return O.Piece(0, "v", 0.9, 0.25, -2.0, -t / 2, w)


# --- the drawn pier ---------------------------------------------------------------------------------------------------

def test_real10_pier_splits_the_gap_into_two_windows():
    g = _gap()
    strokes = _real10_pier() + _window("a", 0.10, 0.60) + _window("b", 1.20, 1.70)
    found = O._pier_parts(g, _index(*strokes), set(), [_partition()])
    assert found is not None
    assert [(round(a, 3), round(b, 3)) for a, b in found["parts"]] == [(0.0, 0.6), (1.2, 1.8)]
    assert found["kinds"] == ["window", "window"]
    assert "drawn pier" in found["note"]


def _real10_exact():
    """real10 L-1's slot wall as drawn (x from the column face at 10.29 m, y from the 0.16 m band's centre at 12.49 m):
    jamb stubs of 7 cm 3 cm off the columns, each 0.50 m window a frame in 7 cm corner pieces round sash lines of 0.30,
    0.36 and 0.40 m (PENCERE), the 0.60 m pier the partition's T-head (DUVAR), the band 0.16 m against the drawn 0.25 m."""
    def L(sid, x0, y0, x1, y1, layer):
        return _line(sid, (round(x0 - 10.29, 4), round(y0 - 12.49, 4)), (round(x1 - 10.29, 4), round(y1 - 12.49, 4)),
                     layer)
    out = []
    for k, (x0, x1) in enumerate(((10.321, 10.391), (11.991, 12.061))):           # the jamb stubs
        out += [L(f"s{k}a", x0, 12.439, x1, 12.439, "DUVAR"), L(f"s{k}b", x0, 12.689, x1, 12.689, "DUVAR"),
                L(f"s{k}c", x0, 12.439, x0, 12.689, "DUVAR"), L(f"s{k}d", x1, 12.439, x1, 12.689, "DUVAR")]
    out += [L("pj0", 10.891, 12.439, 10.891, 12.689, "DUVAR"), L("pj1", 11.491, 12.439, 11.491, 12.689, "DUVAR"),
            L("pt0", 10.891, 12.689, 11.191, 12.689, "DUVAR"), L("pt1", 11.191, 12.689, 11.491, 12.689, "DUVAR"),
            L("pb0", 10.891, 12.439, 11.066, 12.439, "DUVAR"), L("pb1", 11.316, 12.439, 11.491, 12.439, "DUVAR"),
            L("pl", 11.066, 12.439, 11.066, 10.469, "DUVAR"), L("pr", 11.316, 12.439, 11.316, 10.469, "DUVAR")]
    for k, x in enumerate((10.391, 11.491)):                                         # the two windows
        out += [L(f"w{k}a", x, 12.509, x + 0.07, 12.509, "PENCERE"), L(f"w{k}b", x, 12.559, x + 0.07, 12.559, "PENCERE"),
                L(f"w{k}c", x + 0.43, 12.509, x + 0.5, 12.509, "PENCERE"),
                L(f"w{k}d", x + 0.43, 12.559, x + 0.5, 12.559, "PENCERE"),
                L(f"w{k}e", x + 0.05, 12.484, x + 0.45, 12.484, "PENCERE"),
                L(f"w{k}f", x + 0.07, 12.534, x + 0.43, 12.534, "PENCERE"),
                L(f"w{k}g", x + 0.10, 12.509, x + 0.40, 12.509, "PENCERE"),
                L(f"w{k}h", x + 0.07, 12.509, x + 0.07, 12.559, "PENCERE"),
                L(f"w{k}i", x + 0.43, 12.509, x + 0.43, 12.559, "PENCERE")]
    return out


def test_real10_exact_drawing_reads_two_windows_of_the_drawn_width():
    g = _gap(0.0, 1.80, 0.16)
    part = WallItem(start=(0.90, -2.0), end=(0.90, -0.08), thickness=0.31, box=[], entity="part", evidence={})
    found = O._pier_parts(g, _index(*_real10_exact()), set(), [O.Piece(0, "v", 0.90, 0.31, -2.0, -0.08, part)])
    assert found is not None
    assert [(round(a, 3), round(b, 3)) for a, b in found["parts"]] == [(0.101, 0.601), (1.201, 1.701)]
    assert found["kinds"] == ["window", "window"]              # never the jamb lines read as a door's open leaves
    # the whole 1.80 m gap is no window by itself (the windows' lines cover 1.0 m of it)
    g2 = _gap(0.0, 1.80, 0.16)
    O._classify_gap_rules(g2, _index(*_real10_exact()), set())
    assert g2.cls != "window"


def _part(a=0.0, b=0.5, t=0.16):
    return O.Gap("split", "h", 0.0, t, a, b, [], pier_part=True)


def test_window_layer_lines_rule():
    # in a part beside a drawn pier: a frame in corner pieces round a sash, all on the window layer, together spanning
    # the part: a window
    strokes = [_line("a", (0.0, 0.019), (0.07, 0.019), "PENCERE"), _line("b", (0.43, 0.019), (0.5, 0.019), "PENCERE"),
               _line("c", (0.05, -0.006), (0.45, -0.006), "PENCERE"), _line("d", (0.07, 0.044), (0.43, 0.044), "PENCERE")]
    g = _part()
    O._classify_gap_rules(g, _index(*strokes), set())
    assert g.cls == "window" and g.found.get("window_layer")
    assert O.gap_rule(g, {})[0] == "window_layer_lines"
    # a gap no pier bounds keeps the cascade's answer (real10's 0.40 m closet doors and its '140/230' glazed door have
    # lines on the window layer: C0020, C0035)
    g = _gap(0.0, 0.5, 0.16)
    O._classify_gap_rules(g, _index(*strokes), set())
    assert g.cls != "window"
    # the same lines on a furniture layer, or running on past the jamb, are none
    g = _part()
    O._classify_gap_rules(g, _index(*[_line(s.id, s.pts[0], s.pts[1], "TEFRIS") for s in strokes]), set())
    assert g.cls != "window"
    g = _part()
    O._classify_gap_rules(g, _index(strokes[0], _line("c", (0.05, -0.006), (0.9, -0.006), "PENCERE")), set())
    assert g.cls != "window"


def test_window_layer_lines_come_before_open_leaves_in_a_pier_part():
    # two 5 cm frame lines at a 0.5 m window's jambs, each drawn twice (real10 L-1), would fit a double door's leaves;
    # in a part beside a drawn pier the window's lines decide first
    frames = [_line("f1", (0.40, -0.006), (0.40, 0.044), "PENCERE"), _line("f2", (0.40, -0.006), (0.40, 0.044), "PENCERE"),
              _line("f3", (0.45, -0.006), (0.45, 0.044), "PENCERE"), _line("f4", (0.45, -0.006), (0.45, 0.044), "PENCERE")]
    sash = [_line("a", (0.0, 0.019), (0.07, 0.019), "PENCERE"), _line("b", (0.43, 0.019), (0.5, 0.019), "PENCERE"),
            _line("c", (0.05, -0.006), (0.45, -0.006), "PENCERE"), _line("d", (0.07, 0.044), (0.43, 0.044), "PENCERE")]
    g = _part()
    O._classify_gap_rules(g, _index(*(frames + sash)), set())
    assert g.cls == "window"


def test_real10_pier_needs_the_partition_or_its_faces():
    # without the partition's piece the cut face covers 0.35 of 0.60 m (58 %): still a pier
    strokes = _real10_pier() + _window("a", 0.10, 0.60) + _window("b", 1.20, 1.70)
    assert O._drawn_piers(_gap(), _index(*strokes), set()) is not None
    # with only the two jamb lines (no face drawn between them) it is no pier
    bare = [s for s in _real10_pier() if s.id in ("j0", "j1")] + _window("a", 0.10, 0.60) + _window("b", 1.20, 1.70)
    assert O._drawn_piers(_gap(), _index(*bare), set()) is None


def test_bench_pier_box_splits_and_jamb_stubs_trim():
    # the dataset's drawing: a closed DUVAR box (0.40 m) between two 1.0 m windows; jamb stubs of 3 cm at both ends
    g = _gap(0.0, 2.46, 0.275)
    strokes = (_pier_box(1.03, 1.43, 0.275) + [_box("s0", 0.0, -0.1375, 0.03, 0.1375), _box("s1", 2.43, -0.1375, 2.46, 0.1375)]
               + _window("a", 0.03, 1.03, 0.275, "DOGRAMA") + _window("b", 1.43, 2.43, 0.275, "DOGRAMA"))
    found = O._pier_parts(g, _index(*strokes), set())
    assert found is not None
    assert [(round(a, 3), round(b, 3)) for a, b in found["parts"]] == [(0.03, 1.03), (1.43, 2.43)]


def test_a_gap_open_by_its_width_stays_open():
    # swiss-b1613 / b2294: two windows and their DUVAR pier in a gap over 3 m: the gap stays open by its width (the outer
    # ring's closure downstream depends on it); _drawn_piers still sees the pier, the run-gap loop never asks
    g = _gap(0.0, 4.48, 0.47)
    strokes = _pier_box(2.05, 2.43, 0.47) + _window("a", 0.0, 2.05, 0.47) + _window("b", 2.43, 4.48, 0.47)
    assert O._drawn_piers(g, _index(*strokes), set()) is not None
    import inspect
    src = inspect.getsource(O.gaps_and_openings_frame)
    assert src.index("if any(b - a > GAP_MAX_M for a, b in subs):") < src.index("_pier_parts(")


def test_no_pier_along_a_wall_read_twice_nor_a_column_as_a_part():
    strokes = _pier_box(1.0, 1.4) + _window("a", 0.0, 1.0) + _window("b", 1.4, 2.4)
    # real06 L0: a 0.25 m wall 2.6 cm off this run's line holds the windows along the whole gap
    twin = WallItem(start=(-1.0, 0.026), end=(4.0, 0.026), thickness=0.25, box=[], entity="twin", evidence={})
    pieces = [O.Piece(1, "h", 0.026, 0.25, -1.0, 0.0, twin, run=7), O.Piece(2, "h", 0.026, 0.25, 1.0, 1.4, twin, run=7),
              O.Piece(3, "h", 0.026, 0.25, 2.4, 4.0, twin, run=7)]              # its own window gaps between them
    assert O._pier_parts(_gap(0.0, 2.4), _index(*strokes), set(), pieces) is None
    # real10: the jamb stubs at the gap's ends (7 cm boxes 7 cm off the band's line) and a run of columns metres off its
    # ends are no such wall
    stub = WallItem(start=(0.03, 0.074), end=(0.10, 0.074), thickness=0.25, box=[], entity="stub", evidence={})
    others = [O.Piece(4, "h", 0.074, 0.25, -0.04, 0.03, stub, run=9), O.Piece(5, "h", 0.074, 0.25, 2.40, 2.47, stub, run=9),
              O.Piece(6, "h", 0.075, 0.25, -3.5, -2.75, stub, run=10), O.Piece(7, "h", 0.075, 0.25, 4.5, 5.25, stub, run=10)]
    assert O._pier_parts(_gap(0.0, 2.4), _index(*strokes), set(), others) is not None
    # real07 L1: one part is a hatched column, not an opening (only the other part holds a window)
    hatch = [_line(f"h{k}", (0.1 * k, -0.125), (0.1 * k + 0.25, 0.125), "KOLTAR") for k in range(9)]
    strokes = _pier_box(1.0, 1.4) + hatch + _window("b", 1.4, 2.4)
    assert O._pier_parts(_gap(0.0, 2.4), _index(*strokes), set()) is None


def test_a_wardrobe_back_on_the_face_does_not_hide_the_pier():
    # swiss-b1739: a wardrobe's back edge 5 mm outside the wall face runs across the pier
    g = _gap(0.0, 2.4, 0.275)
    strokes = (_pier_box(1.0, 1.4, 0.275) + _window("a", 0.0, 1.0, 0.275) + _window("b", 1.4, 2.4, 0.275)
               + [_box("ward", 1.2, 0.1425, 3.4, 0.75, "A-TEFRIS")])
    assert O._pier_parts(g, _index(*strokes), set()) is not None


def test_door_beside_a_window_across_a_pier():
    from wenart.ingest.generic.model import Stroke as S
    import math
    g = _gap(0.0, 2.05)
    r, hinge = 0.9, (1.15, -0.125)
    arc_pts = [(hinge[0] + r * math.cos(math.radians(a)), hinge[1] + r * math.sin(math.radians(a)))
               for a in [-90 + 90 * k / 16 for k in range(17)]]
    arc = S("arc", "arc", [(round(x, 6), round(y, 6)) for x, y in arc_pts], layer="KAPI",
            arc={"center": hinge, "radius": r, "start_deg": -90.0, "end_deg": 0.0})
    leaf = _line("leaf", hinge, (hinge[0], hinge[1] - r), "KAPI")
    strokes = _pier_box(0.9, 1.15) + _window("a", 0.0, 0.9) + [arc, leaf]
    found = O._pier_parts(g, _index(*strokes), set())
    assert found is not None and found["kinds"] == ["window", "door"]


@pytest.mark.parametrize("case", ["mullion_window_layer", "frame_over_wall_mullion", "narrow", "short_part",
                                  "no_symbol", "stubs_only"])
def test_must_not_fire(case):
    g = _gap(0.0, 2.4)
    if case == "mullion_window_layer":
        # one window with a mullion: frame and glass lines run on across it, the mullion on the window layer
        strokes = _window("w", 0.0, 2.4) + [_line("m0", (1.17, -0.125), (1.17, 0.125), "PENCERE"),
                                           _line("m1", (1.23, -0.125), (1.23, 0.125), "PENCERE")]
    elif case == "frame_over_wall_mullion":
        # a post drawn on the wall layer, the window's glass running on across it: one window
        strokes = _window("w", 0.0, 2.4) + _pier_box(1.1, 1.3)
    elif case == "narrow":
        # a 6 cm post between two panes: a mullion, not a masonry pier
        strokes = _window("a", 0.0, 1.17) + _window("b", 1.23, 2.4) + _pier_box(1.17, 1.23)
    elif case == "short_part":
        # material 0.15 m from a jamb: a return, not a pier (the part would be narrower than an opening)
        strokes = _window("a", 0.4, 2.4) + _pier_box(0.15, 0.4)
    elif case == "no_symbol":
        # wall material in a gap with nothing drawn beside it: no opening the pier stands between
        strokes = _pier_box(1.0, 1.4)
    else:
        strokes = [_box("s0", 0.0, -0.125, 0.05, 0.125), _box("s1", 2.35, -0.125, 2.4, 0.125)] + _window("w", 0.05, 2.35)
    assert O._pier_parts(g, _index(*strokes), set()) is None


def test_material_layers():
    assert O._material(Stroke("a", "line", [(0, 0), (1, 0)], layer="DUVAR"))
    assert O._material(Stroke("a", "line", [(0, 0), (1, 0)], layer="kolon"))
    assert not O._material(Stroke("a", "line", [(0, 0), (1, 0)], layer="SIVA"))
    assert O._material(Stroke("a", "line", [(0, 0), (1, 0)], layer="SIVA"), O.PIER_FACE_ROLES)
    assert not O._material(Stroke("a", "line", [(0, 0), (1, 0)], layer="DUVAR-PENC"))
    assert not O._material(Stroke("a", "line", [(0, 0), (1, 0)], layer="PENCERE"))


# --- the wall read in two layers --------------------------------------------------------------------------------------

def _wall(y, t, x0=0.0, x1=6.0):
    return WallItem(start=(x0, y), end=(x1, y), thickness=t, box=[], entity=f"w{y}", evidence={})


def _op(kind, x, width, y, rule=None):
    ev = {"rule": rule} if rule else {}
    return OpeningItem(kind=kind, width=width, center=(x, y), rotation_deg=0.0, box=None, entity=f"{kind}{x}",
                       evidence=ev)


def _slot_case(kind="opening", gap_y=0.16):
    """real10's slot wall: the bathrooms' 0.16 m wall at y 0 (windows 0.50 m at x 2.25 and 3.35) and a 0.16 m layer of
    the slot's plaster beside it at y ``gap_y`` (bands touching at 0.16), its one 1.52 m gap facing both windows."""
    walls = [_wall(0.0, 0.16), _wall(gap_y, 0.16, 2.0, 3.6)]
    ops = [_op("window", 2.25, 0.5, 0.0), _op("window", 3.35, 0.5, 0.0), _op(kind, 2.8, 1.52, gap_y)]
    return walls, ops


def test_stacked_layer_gap_is_the_windows_behind_it():
    walls, ops = _slot_case()
    assert len(TP.stacked_windows(ops[2], walls, ops)) == 2


@pytest.mark.parametrize("case", ["door", "apart", "no_windows"])
def test_stacked_layer_must_not_fire(case):
    walls, ops = _slot_case("door" if case == "door" else "opening", 0.40 if case == "apart" else 0.16)
    if case == "no_windows":
        ops = ops[2:]
    assert TP.stacked_windows(ops[-1], walls, ops) == []


def test_slot_with_layered_wall_is_a_light_well():
    walls, ops = _slot_case()
    ops = [_op("window", 2.25, 0.5, 0.0), _op("window", 3.35, 0.5, 0.0), _op("opening", 2.8, 1.52, 0.16)]
    slot = Polygon([(2.0, 0.24), (3.6, 0.24), (3.6, 3.6), (2.0, 3.6)])
    baths = [Polygon([(0.0, -3.0), (2.8, -3.0), (2.8, -0.08), (0.0, -0.08)]),
             Polygon([(2.8, -3.0), (6.0, -3.0), (6.0, -0.08), (2.8, -0.08)])]
    rtype, reason = TP.unlabelled_face_type(slot, walls, ops, others=[slot] + baths)
    assert rtype == "shaft" and reason.startswith("light well"), reason
    assert "two layers" in reason
    # the same slot whose layer's gap is a door: a room with a door, never a light well
    ops[2] = _op("door", 2.8, 0.9, 0.16)
    rtype, reason = TP.unlabelled_face_type(slot, walls, ops, others=[slot] + baths)
    assert rtype != "shaft"


def test_small_room_with_a_door_and_a_window_onto_it_stays_a_room():
    walls = [_wall(0.0, 0.16), _wall(3.0, 0.16)]
    ops = [_op("window", 1.0, 0.6, 0.0), _op("opening", 1.0, 0.8, 3.0)]   # its door read as a gap, no layer behind
    room = Polygon([(0.0, 0.08), (2.0, 0.08), (2.0, 2.92), (0.0, 2.92)])
    other = Polygon([(0.0, -2.0), (2.0, -2.0), (2.0, -0.08), (0.0, -0.08)])
    rtype, _reason = TP.unlabelled_face_type(room, walls, ops, others=[room, other])
    assert rtype != "shaft"


# --- end to end -------------------------------------------------------------------------------------------------------

@pytest.fixture(scope="module")
def reading(tmp_path_factory):
    from wenart.ingest import pipeline as PL
    from wenart.synthetic import failure_classes as FC
    from wenart.synthetic import weak_projects as WP

    root = tmp_path_factory.mktemp("rules_lightwell")
    project = WP.project_36()
    FC.generate_failure_project(project, root)
    building, _build = PL.run_project(root / project.name, root / f"{project.name}-out", no_ai=True)
    return project, root, building


def _near(b, x, y, kind=None, r=0.3):
    import math
    return [o for o in b["openings"] if (kind is None or o["type"] == kind) and math.dist(o["center"][:2], (x, y)) <= r]


def test_synthetic_36_reads_the_piers_and_the_well(reading):
    from shapely.geometry import Point

    _project, _root, b = reading
    assert sorted((round(o["center"][1], 2), o["width"]) for o in _near(b, 5.4, 7.6, r=0.7)) == [(7.2, 0.5), (8.0, 0.5)]
    assert all(o["type"] == "window" for o in _near(b, 5.4, 7.6, r=0.7))
    assert [o["type"] for o in _near(b, 11.875, 2.1)] == ["window"]          # the window beside the door, a pier between
    assert [o["type"] for o in _near(b, 11.875, 3.3)] == ["door"]
    salon = _near(b, 3.5, 0.125, r=0.5)
    assert len(salon) == 1 and salon[0]["type"] == "window" and salon[0]["width"] == pytest.approx(2.4, abs=0.02)
    well = [r for r in b["rooms"] if Polygon(r["polygon"]).contains(Point(6.3, 7.7))]
    assert len(well) == 1 and well[0]["room_type"] == "shaft"
    depo = [r for r in b["rooms"] if Polygon(r["polygon"]).contains(Point(6.3, 6.2))]
    assert len(depo) == 1 and depo[0]["room_type"] == "storage"


def test_synthetic_36_scores_100(reading):
    from wenart.reading_check import score as SC
    from wenart.reading_check import truth as TR
    from wenart.synthetic import failure_classes as FC

    project, root, b = reading
    truth = TR.synthetic_truth(project.name, root / project.name / FC.TRUTH_FILE)
    assert SC.match(truth, SC.reading_for(truth, b, project.name), b)["total"] == 100.0
