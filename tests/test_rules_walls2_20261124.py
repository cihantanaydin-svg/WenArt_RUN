"""24 Nov 2026, walls round 2, C0099 and short steps (lessons UL380, UL381, UL382-UL384): the rules and their
must-not-fire cases.

- ``walls.drop_hole_pairs`` (UL382): a face-line pair whose band lies in a hole of its layer's even-odd fill of closed
  outlines (a duct box beside a wall, the cavity between two thin leaves) is no wall piece; a band in one ring (a
  wall's own outline) or in none (loose face lines), or a hole a column fills, is not judged.
- ``topology.unlabelled_face_type`` (UL382): an unlabelled face under 0.5 m2 that no opening reaches is a duct
  (``VOID``), never a room; a small closet with a door stays.
- ``split._line_strip`` (UL383): a plan's overall dimension line and its title's underline, a little farther below it
  than the clustering gap, are a strip of that plan, never a drawing of their own.
- ``openings.lone_furniture_leaf`` (UL380, the user's C0099 on real15 L0): one loose closed shape on a furniture
  layer is no sliding leaf without door evidence (a door layer or block, a second leaf, a track, a door-high tag).
- ``symbols.short_steps`` (UL381): 2-3 risers on the stair layer with a stair's mark are steps; a narrower run, a
  threshold pair, a run with stray lines, unmarked lines are not.
"""
from __future__ import annotations

import math

from shapely.geometry import LineString

from wenart.ingest.generic import openings as O
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic import walls as W
from wenart.ingest.generic.model import GenericPage, Stroke
from wenart.ingest.model import OpeningItem, WallItem
from wenart.sheets import split as SP


# --- helpers ---------------------------------------------------------------------------------------------------------

def _poly(sid, pts, layer="DUVAR", fill=None, kind="polyline"):
    return Stroke(sid, kind, list(pts) + [pts[0]], closed=True, layer=layer, fill=fill)


def _box(sid, x0, y0, x1, y1, layer="DUVAR", fill=None):
    return _poly(sid, [(x0, y0), (x1, y0), (x1, y1), (x0, y1)], layer, fill)


def _page(strokes):
    return GenericPage(file="t.dxf", page=1, source_kind="vector", units="dxf", units_to_m=1.0, size=(20.0, 20.0),
                       strokes=list(strokes), texts=[])


def _pairs(page, layer="DUVAR"):
    pieces = W._straight_pieces(page, 1.0)[layer]
    out = []
    for u, n, group in W._direction_groups(pieces):
        out.extend(W._pairs_of(W._merge_lines(group, u, n), layer, u, n))
    return out


# --- UL382: a hole of the wall material is no wall ------------------------------------------------------------------

def _duct_page(column=False, hatch_twice=False):
    """A wall body drawn as closed outlines (bench style): a 4 x 0.6 m block whose inside holds a 3 x 0.2 m duct (the
    hole ring), i.e. a 0.2 m wall at y 0-0.2, the duct at 0.2-0.4, a 0.2 m wall at 0.4-0.6."""
    s = [_box("ext", 0.0, 0.0, 4.0, 0.6), _box("hole", 0.5, 0.2, 3.5, 0.4)]
    if hatch_twice:                       # the hatch's boundary paths over the same rings, on the same layer
        s += [_box("HATCH:1#0", 0.0, 0.0, 4.0, 0.6), _box("HATCH:1#1", 0.5, 0.2, 3.5, 0.4)]
    if column:
        s.append(_box("col", 0.5, 0.2, 3.5, 0.4, layer="KOLON", fill=(0.2, 0.2, 0.2)))
    return _page(s)


def test_a_duct_box_inside_the_wall_outline_is_no_wall_piece():
    page = _duct_page()
    rings, solids = W.layer_rings(page, 1.0)
    pairs = [p for p in _pairs(page) if p.width < 0.3 and abs(p.u[0]) > 0.9]
    kept, dropped = W.drop_hole_pairs(pairs, rings["DUVAR"], solids)
    assert len(dropped) == 1 and abs(dropped[0].width - 0.2) < 1e-6
    mid = dropped[0].polygon().centroid
    assert 0.2 < mid.y < 0.4                                  # the duct's band
    assert all(not (0.2 < p.polygon().centroid.y < 0.4) for p in kept)
    assert any(p.polygon().centroid.y < 0.2 for p in kept) and any(p.polygon().centroid.y > 0.4 for p in kept)


def test_the_same_ring_drawn_twice_counts_once():
    page = _duct_page(hatch_twice=True)
    rings, solids = W.layer_rings(page, 1.0)
    assert len(rings["DUVAR"]) == 2
    pairs = [p for p in _pairs(page) if p.width < 0.3 and abs(p.u[0]) > 0.9]
    assert len(W.drop_hole_pairs(pairs, rings["DUVAR"], solids)[1]) == 1


def test_must_not_fire_a_column_in_the_hole_a_walls_own_outline_loose_lines():
    page = _duct_page(column=True)                            # a filled column fills the 'hole': material
    rings, solids = W.layer_rings(page, 1.0)
    pairs = [p for p in _pairs(page) if p.width < 0.3 and abs(p.u[0]) > 0.9]
    assert W.drop_hole_pairs(pairs, rings["DUVAR"], solids)[1] == []
    # one wall drawn as its own closed outline: inside one ring, material
    page = _page([_box("w", 0.0, 0.0, 4.0, 0.2)])
    rings, solids = W.layer_rings(page, 1.0)
    pairs = _pairs(page)
    assert pairs and W.drop_hole_pairs(pairs, rings["DUVAR"], solids)[1] == []
    # faces drawn as loose lines (no rings): nothing is judged
    lines = [Stroke(f"l{k}", "line", [(0.0, y), (4.0, y)], layer="DUVAR") for k, y in enumerate((0.0, 0.2, 0.4, 0.6))]
    page = _page(lines)
    rings, solids = W.layer_rings(page, 1.0)
    assert "DUVAR" not in rings
    assert W.drop_hole_pairs(_pairs(page), rings.get("DUVAR") or [], solids)[1] == []


def test_the_cavity_between_two_separate_leaf_outlines_is_no_wall_piece():
    # swiss-b465 L1: two 0.095 m leaves, each its own closed outline (the outline cut at the doors), 0.215 m apart
    page = _page([_box("a", 0.0, 0.0, 0.095, 3.0), _box("b", 0.31, 0.0, 0.405, 3.0)])
    rings, solids = W.layer_rings(page, 1.0)
    pairs = [p for p in _pairs(page) if abs(p.u[1]) > 0.9]
    kept, dropped = W.drop_hole_pairs(pairs, rings["DUVAR"], solids)
    assert [round(p.width, 3) for p in dropped] == [0.215]
    assert sorted(round(p.width, 3) for p in kept) == [0.095, 0.095]


def test_must_not_fire_a_partition_between_two_rooms_drawn_as_rings():
    # each room drawn as the closed ring of its inner faces, no building ring: the 0.2 m partition lies in no ring,
    # but the rings beyond its faces are rooms (wider than any wall), so it stays a wall piece
    page = _page([_box("r1", 0.0, 0.0, 3.0, 4.0), _box("r2", 3.2, 0.0, 6.0, 4.0)])
    rings, solids = W.layer_rings(page, 1.0)
    pairs = [p for p in _pairs(page) if abs(p.width - 0.2) < 1e-6]
    assert pairs and W.drop_hole_pairs(pairs, rings["DUVAR"], solids)[1] == []


def test_a_room_drawn_as_a_ring_inside_the_building_ring_keeps_its_walls():
    # building outline 6 x 4, one room ring inside it (0.2 m walls): every wall band is inside one ring only
    page = _page([_box("out", 0.0, 0.0, 6.0, 4.0), _box("room", 0.2, 0.2, 5.8, 3.8)])
    rings, solids = W.layer_rings(page, 1.0)
    pairs = _pairs(page)
    assert pairs and W.drop_hole_pairs(pairs, rings["DUVAR"], solids)[1] == []


def _wall(x0, y0, x1, y1, t=0.2):
    return WallItem(start=(x0, y0), end=(x1, y1), thickness=t, box=[0, 0, 0, 0], entity="w", evidence={})


def _door(x, y, w=0.8):
    return OpeningItem(kind="door", width=w, center=(x, y), rotation_deg=0.0, box=[0, 0, 0, 0], entity="d", evidence={})


def test_a_small_doorless_face_is_a_duct_a_closet_with_a_door_is_not():
    walls = [_wall(0.0, 0.0, 1.0, 0.0), _wall(1.0, 0.0, 1.0, 0.4), _wall(1.0, 0.4, 0.0, 0.4), _wall(0.0, 0.4, 0.0, 0.0)]
    face = [(0.1, 0.1), (0.9, 0.1), (0.9, 0.3), (0.1, 0.3)]           # 0.16 m2
    kind, why = TP.unlabelled_face_type(face, walls, [])
    assert kind == TP.VOID and why.startswith("duct")
    kind, _why = TP.unlabelled_face_type(face, walls, [_door(0.5, 0.0, 0.6)])
    assert kind != TP.VOID                                            # a door reaches it
    big = [(0.1, 0.1), (1.9, 0.1), (1.9, 1.9), (0.1, 1.9)]
    assert TP.unlabelled_face_type(big, walls, [])[0] != TP.VOID      # 3.24 m2: no duct


# --- UL383: a dimension line and a title underline are a strip of their plan ----------------------------------------

def _ent(kind, box, rect=None):
    from wenart.sheets.model import Ent
    return Ent(id=f"{kind}:1", kind=kind, layer="0", box=box, rect=rect)


def test_a_dimension_and_an_underline_are_a_strip_a_drawing_is_not():
    c = SP.Cluster(ents=[_ent("DIMENSION", (990, 830, 2852, 869)), _ent("LINE", (1742, 690, 2100, 690))])
    assert SP._line_strip(c, 1862, 179)
    # a small drawing: a closed rectangle, an insert, or more than three pieces
    assert not SP._line_strip(SP.Cluster(ents=[_ent("LINE", (0, 0, 10, 10), rect=(0, 0, 10, 10))]), 10, 10)
    assert not SP._line_strip(SP.Cluster(ents=[_ent("INSERT", (0, 0, 100, 5))]), 100, 5)
    assert not SP._line_strip(SP.Cluster(ents=[_ent("LINE", (0, k, 100, k)) for k in range(4)]), 100, 3)
    # a square group of lines is no strip
    assert not SP._line_strip(SP.Cluster(ents=[_ent("LINE", (0, 0, 100, 0)), _ent("LINE", (0, 0, 0, 100))]), 100, 100)


# --- UL380 (C0099): one loose furniture-layer rectangle is no sliding door ------------------------------------------

def _gap(a=0.0, b=0.55, t=0.20):
    return O.Gap("run", "h", 0.0, t, a, b, [])


def _rect(sid, x0, y0, x1, y1, layer="Z_tefriş", block=None):
    return Stroke(sid, "polyline", [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)], closed=True, layer=layer,
                  block=block)


def _classify(g, *strokes):
    O._classify_gap_rules(g, O.StrokeIndex(list(strokes), 0.0), set())
    return g


def test_c0099_one_loose_furniture_rectangle_is_no_sliding_door():
    g = _classify(_gap(), _rect("15C010", 0.05, -0.02, 0.40, 0.02))
    assert g.cls != "door" and g.lone_leaf
    assert "Z_tefriş" in O.lone_leaf_note(g) and "UL380" in O.lone_leaf_note(g)


def test_must_not_fire_a_door_layer_a_door_block_two_leaves_or_a_track():
    assert _classify(_gap(), _rect("s", 0.05, -0.02, 0.40, 0.02, layer="KAPI")).cls == "door"
    assert _classify(_gap(), _rect("s", 0.05, -0.02, 0.40, 0.02, block="SURME_KAPI")).cls == "door"
    assert _classify(_gap(), _rect("s", 0.05, -0.02, 0.40, 0.02, layer="0")).cls == "door"   # a layer with no role
    track = Stroke("t", "line", [(0.0, 0.03), (0.55, 0.03)], layer="KAPI")
    assert _classify(_gap(), _rect("s", 0.05, -0.02, 0.40, 0.02), track).cls == "door"
    # two leaves on the furniture layer (a two-panel door drawn there): the rule wants one shape only
    leaves = [_rect("a", 0.0, -0.02, 0.35, 0.02), _rect("b", 0.25, 0.02, 0.55, 0.06)]
    assert not O.lone_furniture_leaf(_gap(), [O._S(leaves[0], leaves[0].pts, LineString(leaves[0].pts)),
                                             O._S(leaves[1], leaves[1].pts, LineString(leaves[1].pts))], [])


def test_a_door_high_tag_at_the_gap_gives_the_lone_leaf_back():
    from wenart.ingest.generic import decisions as DEC
    from wenart.ingest.generic.model import TextRun

    g = _gap()
    tag = DEC._classify_text(TextRun("t1", "55/210", (0.15, 0.25, 0.40, 0.33), 0.08))
    far = DEC._classify_text(TextRun("t2", "55/210", (3.15, 0.25, 3.40, 0.33), 0.08))
    low = DEC._classify_text(TextRun("t3", "55/140", (0.15, 0.25, 0.40, 0.33), 0.08))
    assert tag is not None and O.door_tag_at(g, [tag])
    assert not O.door_tag_at(g, [far]) and not O.door_tag_at(g, [low]) and not O.door_tag_at(g, [])


# --- UL381: short steps are read, narrow runs not --------------------------------------------------------------------

def _segs(strokes):
    return SY._segments(strokes, set())


def _steps(n_lines=4, width=0.8, pitch=0.32, sides=True, arrow=False, layer="MERDIVEN", extra=()):
    st = [Stroke(f"t{k}", "line", [(0.0, k * pitch), (width, k * pitch)], layer=layer) for k in range(n_lines)]
    top = (n_lines - 1) * pitch
    if sides:
        st += [Stroke("sl", "line", [(0.0, 0.0), (0.0, top)], layer=layer),
               Stroke("sr", "line", [(width, 0.0), (width, top)], layer=layer)]
    if arrow:
        x = width / 2.0
        st += [Stroke("w", "line", [(x, 0.05), (x, top - 0.05)], layer=layer),
               Stroke("h1", "line", [(x, top - 0.05), (x - 0.06, top - 0.15)], layer=layer),
               Stroke("h2", "line", [(x, top - 0.05), (x + 0.06, top - 0.15)], layer=layer)]
    return SY.Cluster(_segs(st + list(extra)))


def test_three_risers_in_a_box_and_two_with_an_arrow_are_steps():
    st = SY.short_steps(_steps(4), 0.0)
    assert st is not None and st["short_steps"] == 3 and len(st["flights"]) == 1
    assert abs(st["flights"][0]["width"] - 0.8) < 1e-6 and st["short_steps_mark"] == "a closed outline"
    st = SY.short_steps(_steps(3, sides=False, arrow=True), 0.0)
    assert st is not None and st["short_steps"] == 2 and "arrow" in st["short_steps_mark"]


def test_a_run_of_steps_at_an_angle_is_read_in_its_frame():
    cl = _steps(3, sides=False, arrow=True)
    a = math.radians(4.0)
    for s in cl.segs:
        s.pts = [(p[0] * math.cos(a) - p[1] * math.sin(a), p[0] * math.sin(a) + p[1] * math.cos(a)) for p in s.pts]
        s.geom = LineString(s.pts) if len(s.pts) > 1 else s.geom
    st = SY.short_steps(cl, 0.0)
    assert st is not None and st["short_steps"] == 2 and abs(st["angled_deg"] - 4.0) < 0.5


def test_must_not_fire_narrow_unmarked_a_threshold_pair_strays_tiles_or_a_long_flight():
    assert SY.short_steps(_steps(4, width=0.5), 0.0) is None                      # under 0.60 m: stays unread
    assert SY.short_steps(_steps(4, sides=False), 0.0) is None                    # no box, no arrow
    assert SY.short_steps(_steps(2), 0.0) is None                                 # a threshold or kerb pair
    stray = Stroke("x", "line", [(0.2, 0.5), (0.6, 0.9)], layer="MERDIVEN")
    assert SY.short_steps(_steps(4, extra=[stray]), 0.0) is None                  # something else drawn in it
    assert SY.short_steps(_steps(4, pitch=0.10), 0.0) is None                     # tiles or a grille, not a going
    assert SY.short_steps(_steps(6), 0.0) is None                                 # 5 risers: the stair rule's
    assert SY.short_steps(_steps(4, layer="KARO"), 0.0) is None                   # floor-finish lines
