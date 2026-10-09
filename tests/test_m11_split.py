"""Milestone 11 group splitting of the generic core (docs/milestone11.md §1.2 U8, U10, U12; wenart/ingest/generic/
symbols.py): a table drawn with its chairs (as one named block, or as one unnamed composite) becomes the table and one
chair per chair part, each facing the table; a kitchen counter run drawn as a closed outline along the walls becomes
counter legs (and a free block: the peninsula) with the hob block on it; a block's own strokes are never a counter
run; the answers of the AI candidates follow their crops when a split renumbers the keys."""
import math

import pytest

import _real01_page as R
from wenart.ingest.generic import symbols as SY
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke

TABLE = SY.load_size_table()[0]


def _room(x0=0.0, y0=0.0, x1=6.0, y1=5.0, t=0.2):
    return [R.wall((x0, y0), (x1, y0), t), R.wall((x1, y0), (x1, y1), t), R.wall((x1, y1), (x0, y1), t),
            R.wall((x0, y1), (x0, y0), t)]


def _furn(strokes, walls=None, faces=(), notes=None):
    walls = walls or _room()
    outline = TP.building_outline(walls, [])
    return SY.furniture(strokes, set(), walls, [], [], [], outline, list(faces), level_id="L0", file_rel="t.dxf",
                        page_no=None, size_table=TABLE, notes=notes)


def _line(sid, a, b, block=None):
    return Stroke(id=sid, kind="line", pts=[tuple(map(float, a)), tuple(map(float, b))], block=block)


def _poly(sid, pts, closed=True, block=None):
    return Stroke(id=sid, kind="polyline", pts=[tuple(map(float, p)) for p in pts], closed=closed, block=block)


def _chair_u(prefix, x0, y0, x1, y1, open_side, block=None, start=0):
    """A chair drawn as three lines, open on the side that touches the table (its seat under the table edge)."""
    corners = {"s": [((x0, y0), (x0, y1)), ((x0, y1), (x1, y1)), ((x1, y1), (x1, y0))],
               "n": [((x0, y1), (x0, y0)), ((x0, y0), (x1, y0)), ((x1, y0), (x1, y1))],
               "w": [((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1))],
               "e": [((x1, y0), (x0, y0)), ((x0, y0), (x0, y1)), ((x0, y1), (x1, y1))]}[open_side]
    return [_line(f"{prefix}/{start + k}", a, b, block) for k, (a, b) in enumerate(corners)]


def _table_with_chairs(block=None, prefix="INSERT:T1", xs=(2.1, 2.8, 3.5), x1=4.2):
    """A 2.4 x 1.0 m table (x 1.8-4.2, y 2.0-3.0) with three chairs on each long side: 0.3 m deep visible parts
    touching the table edge (as real02's masa / MASA111 blocks draw them)."""
    table = [_poly(f"{prefix}/0", [(1.8, 2.0), (x1, 2.0), (x1, 3.0), (1.8, 3.0)], block=block)]
    chairs = []
    for k, x in enumerate(xs):
        chairs += _chair_u(prefix, x, 1.7, x + 0.5, 2.0, "n", block, start=10 + 6 * k)      # south side, open to the table
        chairs += _chair_u(prefix, x, 3.0, x + 0.5, 3.3, "s", block, start=13 + 6 * k)      # north side
    return table + chairs


# --------------------------------------------------------------------------
# Table + chairs (U10)
# --------------------------------------------------------------------------

def test_split_table_chairs_finds_the_table_and_six_chairs():
    segs = SY._segments(_table_with_chairs(), set())
    split = SY.split_table_chairs(SY.Cluster(segs), TABLE, 0.0)
    assert split is not None and len(split["chairs"]) == 6
    assert split["table_poly"].bounds == pytest.approx((1.8, 2.0, 4.2, 3.0))


def test_a_named_table_block_with_its_chairs_is_split_and_the_chairs_face_the_table():
    notes = []
    pieces, cands, _ = _furn(_table_with_chairs(block="masa"), notes=notes)
    assert not cands
    tables = [p for p in pieces if p.type == "table_dining"]
    chairs = [p for p in pieces if p.type == "chair"]
    assert len(tables) == 1 and tables[0].type_method == "block_name" and tables[0].status == "verified"
    assert sorted(tables[0].size) == pytest.approx([1.0, 2.4], abs=1e-3)
    assert len(chairs) == 6 and all(c.type_method == "rule" and c.status == "verified" for c in chairs)
    for c in chairs:
        # The visible 0.3 m are grown under the table edge to a 0.45 m deep chair; the front faces the table.
        assert sorted(c.size) == pytest.approx([0.45, 0.5], abs=1e-3)
        assert c.front_deg == (90.0 if c.center[1] < 2.5 else 270.0)
    assert any("holds a table and 6 chairs" in n for n in notes)


def test_an_unnamed_table_and_chairs_composite_is_split_by_rule():
    # 2.9 x 1.6 m with the chairs: no type fits the whole (an unknown composite before, never asked: as real02's
    # MASA111 group of 2.87 x 1.57 m), so the split cannot change any AI candidate.
    group = _table_with_chairs(block=None, prefix="g", xs=(2.0, 2.65, 3.3, 3.95), x1=4.7)
    pieces, cands, _ = _furn(group)
    assert not cands
    assert sorted(p.type for p in pieces) == ["chair"] * 8 + ["table_dining"]
    table = next(p for p in pieces if p.type == "table_dining")
    assert table.type_method == "rule" and "split" in table.evidence["note"]


def test_a_table_with_something_else_beside_it_is_not_split():
    strokes = _table_with_chairs(prefix="g") + [_poly("g/99", [(4.2, 2.1), (5.4, 2.1), (5.4, 2.9), (4.2, 2.9)])]
    assert SY.split_table_chairs(SY.Cluster(SY._segments(strokes, set())), TABLE, 0.0) is None


# --------------------------------------------------------------------------
# Kitchen counter runs drawn as closed outlines (U8) and block strokes (U12)
# --------------------------------------------------------------------------

def _u_kitchen():
    """A 4 x 4 m kitchen (walls 0.2 m): a U counter outline 0.6 m deep along the west, north and east walls drawn as
    one closed polyline, a hob block on the north leg and a dishwasher block inside the east leg."""
    walls = _room(0, 0, 4, 4)
    i = 0.1                                                             # inner wall faces at 0.1 / 3.9
    outline = _poly("LWPOLYLINE:K1", [(i, 1.0), (i + 0.6, 1.0), (i + 0.6, 3.3), (3.3, 3.3), (3.3, 1.5), (3.9, 1.5),
                                       (3.9, 3.9), (i, 3.9)])
    hob = [Stroke(id=f"INSERT:H1/{k}", kind="line", pts=seg, block="ocak_")
           for k, seg in enumerate((((1.6, 3.3), (2.2, 3.3)), ((2.2, 3.3), (2.2, 3.85)), ((2.2, 3.85), (1.6, 3.85)),
                                    ((1.6, 3.85), (1.6, 3.3))))]
    dishwasher = [Stroke(id=f"INSERT:D1/{k}", kind="line", pts=seg, block="bulmak")
                  for k, seg in enumerate((((3.3, 2.0), (3.85, 2.0)), ((3.85, 2.0), (3.85, 2.55)),
                                           ((3.85, 2.55), (3.3, 2.55)), ((3.3, 2.55), (3.3, 2.0))))]
    return walls, [outline] + hob + dishwasher


def test_counter_legs_of_a_u_outline_give_the_corners_to_the_longer_legs():
    walls, strokes = _u_kitchen()
    to_f, _ = SY._frame(0.0)
    faces = SY._wall_faces(walls, [], to_f)
    poly = SY._outline_polygons(SY._segments(strokes[:1], set()), to_f)[0][0]
    legs, blocks = SY.counter_legs(poly, faces)
    rects = sorted(tuple(round(v, 3) for v in lg["rect"]) for lg in legs)
    assert rects == [(0.1, 1.0, 0.7, 3.3), (0.1, 3.3, 3.9, 3.9), (3.3, 1.5, 3.9, 3.3)]   # north (3.8 m) is longest
    assert not blocks


def test_a_kitchen_counter_outline_with_a_hob_block_becomes_legs_and_a_named_hob():
    walls, strokes = _u_kitchen()
    notes = []
    pieces, cands, _ = _furn(strokes, walls=walls, notes=notes)
    assert not cands
    counters = [p for p in pieces if p.type == "kitchen_counter"]
    assert len(counters) == 3 and all(p.type_method == "rule" and p.front_deg is not None for p in counters)
    hob = [p for p in pieces if p.type == "stove"]
    assert len(hob) == 1 and hob[0].type_method == "block_name" and hob[0].front_deg == 270.0
    detail = [p for p in pieces if p.type == "unknown"]
    assert len(detail) == 1 and detail[0].details.get("build") is False          # the dishwasher inside the leg
    assert any("kitchen counter cluster split" in n for n in notes)


def test_a_peninsula_of_the_outline_is_a_kitchen_island():
    walls = _room(0, 0, 4, 4)
    outline = _poly("LWPOLYLINE:K2", [(0.1, 1.0), (2.0, 1.0), (2.0, 1.6), (0.7, 1.6), (0.7, 3.3), (3.9, 3.3),
                                       (3.9, 3.9), (0.1, 3.9)])
    to_f, _ = SY._frame(0.0)
    poly = SY._outline_polygons(SY._segments([outline], set()), to_f)[0][0]
    legs, blocks = SY.counter_legs(poly, SY._wall_faces(walls, [], to_f))
    assert len(legs) == 2 and [tuple(round(v, 3) for v in b) for b in blocks] == [(0.7, 1.0, 2.0, 1.6)]


def test_the_counter_rule_never_reads_a_blocks_own_strokes():
    # U12: five strokes of a wardrobe block along a wall read as counter legs before.
    walls = _room(0, 0, 4, 4)
    chain = [Stroke(id=f"INSERT:W1/{k}", kind="line", pts=seg, block="dolap")
             for k, seg in enumerate((((0.8, 3.9), (0.8, 3.3)), ((0.8, 3.3), (3.3, 3.3)), ((3.3, 3.3), (3.3, 2.0)),
                                      ((3.3, 2.0), (3.9, 2.0))))]
    cl = SY.Cluster(SY._segments(chain, set()))
    assert SY.counter_rule(cl, walls, [], 0.0) == []
    loose = [Stroke(id=f"s{k}", kind="line", pts=s.pts) for k, s in enumerate(chain)]
    assert len(SY.counter_rule(SY.Cluster(SY._segments(loose, set())), walls, [], 0.0)) == 2
