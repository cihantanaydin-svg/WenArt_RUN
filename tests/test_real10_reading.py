"""real10 (``projects/real10/real10.dwg``, the user's DWG of 1 Nov 2026): the drawing-reading rules it needed.

The DWG is an apartment block (A BLOK): two basements, a ground floor, six normal floors and a roof terrace, drawn in
metres shrunk to 1:50 (as real06) with no frames; its ten drawings (four plans, two sections, four elevations) stand
in one row 0.7-3 m apart, each titled at its bottom right. Its plan titles count the basements downwards
(``2.BODRUM KAT PLANI``), draw one typical plan for the upper floors (``NORMAL KAT PLANI``) and a roof terrace floor
(``TERAS KAT PLANI``). Each rule is checked on its own here and on the real DWG at the end (LibreDWG needed).
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest

from conftest import PROJECTS
from wenart.ingest import dwg
from wenart.ingest.generic.model import Stroke
from wenart.ingest.generic import walls as W
from wenart.sheets import levels as LV
from wenart.sheets import split as SP
from wenart.sheets.levels import level_of
from wenart.sheets.model import Ent, Sheet, Txt


def _line(eid, a, b, layer="0"):
    st = Stroke(id=eid, kind="line", pts=[tuple(a), tuple(b)], layer=layer)
    return Ent(id=eid, kind="LINE", layer=layer, box=(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]),
                                                      max(a[1], b[1])), strokes=[st])


def _grid(prefix, x0, x1, y0=0.0, y1=80.0, n=12):
    """A dense drawing: n horizontal and n vertical lines over its box (every slice through it crosses many)."""
    out = []
    for k in range(n):
        y = y0 + (y1 - y0) * k / (n - 1)
        x = x0 + (x1 - x0) * k / (n - 1)
        out.append(_line(f"LINE:{prefix}h{k}", (x0, y), (x1, y)))
        out.append(_line(f"LINE:{prefix}v{k}", (x, y0), (x, y1)))
    return out


def _txt(tid, text, x, y, h):
    return Txt(id=tid, text=text, box=(x, y, x + len(text) * 0.7 * h, y + h), height=h)


def _labels(prefix, x0, n=6):
    return [_txt(f"TEXT:{prefix}l{k}", "oda", x0 + 10 + 12 * k, 40.0, 1.0) for k in range(n)]


# --------------------------------------------------------------------------
# Title cuts
# --------------------------------------------------------------------------

def test_title_cuts_split_a_strip_of_close_drawings():
    """Four drawings 3 units apart in a row (the sheet's gap, 1.5 % of the strip's diagonal, is about 6 units: the
    clustering joins them all), a ground line running under the last two; each titled at its bottom right. The
    title cuts give four regions, each with its own title."""
    names = ["ZEMİN KAT PLANI", "A - A KESİTİ", "GÜNEY CEPHE", "KUZEY CEPHE"]
    ents, texts = [], []
    for k, name in enumerate(names):
        x0 = k * 103.0
        ents += _grid(f"d{k}", x0, x0 + 100.0)
        texts += _labels(f"d{k}", x0)
        texts.append(_txt(f"TEXT:t{k}", name, x0 + 90.0, -6.0, 3.0))
    ents.append(_line("LINE:ground", (206.0 - 2.0, -1.0), (309.0 + 2.0, -1.0), layer="1.2"))
    sheet = Sheet(id="s1", space="model", file="t.dxf", page=1, ents=ents, texts=texts)
    assert SP.split_sheet(sheet).gap > 3.0
    res = SP.split_sheet(sheet)
    drawings = sorted((c for c in res.clusters if c.kind == "drawing"), key=lambda c: c.geometry_box[0])
    assert len(drawings) == 4
    for c, name in zip(drawings, names):
        assert [t.text for t in SP.drawing_titles(c.texts)] == [name]


def test_title_cut_never_cuts_inside_one_drawing():
    """One drawing with its title below and a second title-size class word inside (a section mark labelled
    ``KESİT``): no band between them is clear, so the drawing stays one region."""
    ents = _grid("d", 0.0, 100.0)
    texts = _labels("d", 0.0) + [_txt("TEXT:t1", "KAT PLANI", 90.0, -6.0, 3.0),
                                  _txt("TEXT:t2", "KESİT", 20.0, 50.0, 3.0)]
    sheet = Sheet(id="s1", space="model", file="t.dxf", page=1, ents=ents, texts=texts)
    res = SP.split_sheet(sheet)
    assert len([c for c in res.clusters if c.kind == "drawing"]) == 1


def test_drawing_titles_are_title_size_class_words():
    texts = [_txt("TEXT:a", "salon", 0, 0, 1.0), _txt("TEXT:b", "mutfak", 0, 0, 1.0),
             _txt("TEXT:c", "NORMAL KAT PLANI", 0, 0, 3.5), _txt("TEXT:d", "ÖLÇEK :1/50", 0, 0, 2.5),
             _txt("TEXT:e", "plan", 0, 0, 1.0)]
    assert [t.text for t in SP.drawing_titles(texts)] == ["NORMAL KAT PLANI"]


# --------------------------------------------------------------------------
# Level words
# --------------------------------------------------------------------------

@pytest.mark.parametrize("title,order,kind,typical", [
    ("2.BODRUM KAT PLANI", -2, "basement", False),
    ("1.BODRUM KAT PLANI", -1, "basement", False),
    ("BODRUM KAT PLANI", -1, "basement", False),
    ("2nd basement plan", -2, "basement", False),
    ("NORMAL KAT PLANI", 1, "floor", True),
    ("TİP KAT PLANI", 1, "floor", True),
    ("Typical floor plan", 1, "floor", True),
    ("3. NORMAL KAT", 3, "floor", False),
    ("ZEMİN KAT", 0, "floor", False),
    ("1. KAT PLANI", 1, "floor", False),
    ("TERAS KAT PLANI", None, "roof_terrace", False),
    ("ÇATI KATI PLANI", None, "attic", False),
])
def test_level_words_of_an_apartment_block(title, order, kind, typical):
    lw = level_of(title)
    assert lw is not None and (lw.order, lw.kind, lw.typical) == (order, kind, typical)


def _plan(rid, title):
    return SimpleNamespace(id=rid, file="real10.dwg", title={"text": title}, evidence=[], level=None, use="read")


STOREYS = {-2: "2. Bodrum Kat", -1: "1. Bodrum Kat", 0: "Zemin Kat", 1: "1. Normal Kat", 2: "2. Normal Kat",
           3: "3. Normal Kat", 4: "4. Normal Kat", 5: "5. Normal Kat", 6: "6. Normal Kat"}


def test_storeys_are_the_level_words_of_the_sections():
    texts = [SimpleNamespace(text=t) for t in ("2. BODRUM KAT", "1. BODRUM KAT", "ZEMİN KAT", "1. NORMAL KAT",
                                               "6. NORMAL KAT", "asma tavan", "+ 2.50")]
    assert LV.storey_words([SimpleNamespace(texts=texts)]) == {-2: "2. Bodrum Kat", -1: "1. Bodrum Kat",
                                                              0: "Zemin Kat", 1: "1. Normal Kat", 6: "6. Normal Kat"}


def test_typical_floor_stands_for_the_storeys_the_sections_name():
    """real10: four plans; the sections name the basements, the ground floor and six normal floors. The typical plan
    stands for L0-L6 (L0, the ground floor without a plan of its own, inferred); the roof terrace is L7."""
    plans = [_plan("r10", "2.BODRUM KAT PLANI"), _plan("r7", "1.BODRUM KAT PLANI"), _plan("r8", "NORMAL KAT PLANI"),
             _plan("r9", "TERAS KAT PLANI")]
    review, warnings = [], []
    LV.assign_levels(plans, review, warnings, STOREYS)
    assert not review
    assert [p.level["id"] for p in plans] == ["L-2", "L-1", "L0", "L7"]
    typ = plans[2].level["typical"]
    assert typ["ids"] == ["L0", "L1", "L2", "L3", "L4", "L5", "L6"] and typ["inferred"] == ["L0"]
    assert typ["labels"][0] == "Zemin Kat" and typ["labels"][-1] == "6. Normal Kat" and typ["how"] == "section"
    assert plans[3].level.get("roof_terrace") is True and plans[3].level["kind"] == "floor"
    assert any("typical floor plan" in w and "inferred" in w for w in warnings)


def test_typical_floor_with_its_own_ground_floor_plan_and_no_sections():
    plans = [_plan("r1", "ZEMİN KAT PLANI"), _plan("r2", "NORMAL KAT PLANI")]
    LV.assign_levels(plans, [], [], {})
    assert plans[1].level["typical"]["ids"] == ["L1"] and plans[1].level["typical"]["how"] == "assumed"
    plans = [_plan("r1", "ZEMİN KAT PLANI"), _plan("r2", "NORMAL KAT PLANI")]
    LV.assign_levels(plans, [], [], {0: "Zemin Kat", 1: "1. Normal Kat", 2: "2. Normal Kat"})
    assert plans[1].level["typical"]["ids"] == ["L1", "L2"] and plans[1].level["typical"]["inferred"] == []


# --------------------------------------------------------------------------
# Axis grids are no walls
# --------------------------------------------------------------------------

def _hpair(y, x0, x1, w=0.10):
    return W._Pair(layer="L", u=(1.0, 0.0), n=(0.0, 1.0), lo=x0, hi=x1,
                   lines=(W._Line(y - w / 2, x0, x1, ["a"]), W._Line(y + w / 2, x0, x1, ["b"])))


def _vpair(x, y0, y1, w=0.10):
    # u = +y, n = -x: point(s, o) = (-o, s)
    return W._Pair(layer="L", u=(0.0, 1.0), n=(-1.0, 0.0), lo=y0, hi=y1,
                   lines=(W._Line(-x - w / 2, y0, y1, ["c"]), W._Line(-x + w / 2, y0, y1, ["d"])))


def test_axis_grid_pieces_cross_straight_through():
    """real10's axis layer (double lines 0.10 m apart) closed in 8 of 9 labelled rooms and won over the walls: its
    pieces cross straight through each other (+), the walls meet at T and L joints."""
    grid = [_hpair(y, -2.0, 22.0) for y in (0.0, 5.0, 10.0)] + [_vpair(x, -2.0, 12.0) for x in (0.0, 10.0, 20.0)]
    through, meet = W.grid_crossings(grid)
    assert (through, meet) == (9, 9)
    room = [_hpair(0.0, 0.0, 6.0, 0.2), _hpair(4.0, 0.0, 6.0, 0.2), _vpair(0.0, 0.1, 3.9, 0.2),
            _vpair(6.0, 0.1, 3.9, 0.2), _vpair(3.0, 0.1, 3.9, 0.1)]
    through, meet = W.grid_crossings(room)
    assert through == 0 and meet >= 6


# --------------------------------------------------------------------------
# Walls drawn by masonry, plaster and concrete layers (exploded drawing)
# --------------------------------------------------------------------------

def test_a_piece_stopping_at_the_plaster_runs_on_to_the_wall_it_meets():
    """The masonry faces of a partition stop 3 cm short of the wall they meet (the plaster coat): the partition runs
    on to it and the walls are one network."""
    outer = _hpair(0.1, 0.0, 6.0, 0.2)
    part = _vpair(3.05, 0.23, 3.0, 0.1)
    assert W._parts_count(W._network([outer, part], [])) == 1
    far = _vpair(3.05, 0.30, 3.0, 0.1)                                   # 10 cm short: a gap, not plaster
    assert W._parts_count(W._network([outer, far], [])) == 2


def _st(layer, a, b, prefix):
    import _real01_page as R

    st = R.stroke([a, b], prefix=prefix)
    st.layer = layer
    return st


def _box(layer, x0, y0, x1, y1, prefix, over=0.01):
    """A rectangle drawn as four separate LINEs whose ends run ``over`` past the corners."""
    return [_st(layer, (x0 - over, y0), (x1 + over, y0), prefix), _st(layer, (x1, y0 - over), (x1, y1 + over), prefix),
            _st(layer, (x1 + over, y1), (x0 - over, y1), prefix), _st(layer, (x0, y1 + over), (x0, y0 - over), prefix)]


def test_columns_drawn_as_four_lines_are_column_candidates():
    """real10's kolon layer: columns and shear walls as four loose LINEs (25 x 80 cm, 25 x 210 cm). An empty box on a
    furniture layer full of other lines, and a box with a line inside (a wardrobe's rail), are no columns."""
    import _real01_page as R

    strokes = _box("kolon", 0, 0, 0.25, 0.8, "k1") + _box("kolon", 5, 0, 5.25, 2.1, "k2")
    strokes += _box("MOB", 2, 2, 2.4, 3.9, "m1") + [_st("MOB", (3, y / 10), (4, y / 10), "m2") for y in range(20)]
    strokes += _box("kolon", 8, 0, 8.6, 2.0, "k3") + [_st("kolon", (8.3, 0.2), (8.3, 1.8), "k3")]
    cols = W._line_loop_columns(R.synthetic_page(strokes), 1.0)
    sizes = sorted(tuple(round(v, 2) for v in sorted(W._rect_sides(p.minimum_rotated_rectangle))) for p, _ in cols)
    assert sizes == [(0.25, 0.8), (0.25, 2.1)]


def test_stair_treads_are_no_wall_pieces():
    """Treads drawn on the plaster layer: six parallel lines 0.27 m apart pair into 'walls'; such an even run is no
    wall. A wall drawn with plaster and masonry lines on one layer (2, 20, 2 cm) keeps its pieces."""
    treads = [W._Line(0.27 * k, 0.0, 1.2, [f"t{k}"]) for k in range(6)]
    assert W._drop_tread_runs(W._pairs_of(treads, "SIVA", (1.0, 0.0), (0.0, 1.0))) == []
    wall = [W._Line(o, 0.0, 4.0, [f"w{k}"]) for k, o in enumerate((0.0, 0.02, 0.22, 0.24))]
    assert W._drop_tread_runs(W._pairs_of(wall, "SIVA", (1.0, 0.0), (0.0, 1.0)))


def test_the_walls_part_the_labels_into_rooms():
    """The typical floor's layer 0 rings the building with its balcony outlines (all labels in one face); the walls
    part the labels into their rooms."""
    from shapely.geometry import Polygon as P

    ring = [P([(0, 0), (10, 0), (10, 0.1), (0, 0.1)]), P([(0, 5), (10, 5), (10, 5.1), (0, 5.1)]),
            P([(0, 0), (0.1, 0), (0.1, 5.1), (0, 5.1)]), P([(9.9, 0), (10, 0), (10, 5.1), (9.9, 5.1)])]
    labels = [(2.0, 2.5), (8.0, 2.5)]
    assert W.separate_rooms(labels, ring) == 1
    assert W.separate_rooms(labels, ring + [P([(5, 0), (5.1, 0), (5.1, 5.1), (5, 5.1)])]) == 2


def test_a_second_layer_drawing_the_same_walls_lies_along_them():
    from shapely.geometry import Polygon as P

    siva = [W._Element("face_pair", P([(0, -0.02), (6, -0.02), (6, 0.22), (0, 0.22)]), ["s"])]
    duvar = [W._Element("face_pair", P([(0, 0), (6, 0), (6, 0.2), (0, 0.2)]), ["d"])]
    railing = [W._Element("face_pair", P([(0, 1.5), (6, 1.5), (6, 1.55), (0, 1.55)]), ["r"])]
    assert W.along_share(duvar, siva) > 0.99 and W.along_share(railing, siva) == 0.0


def test_a_wing_holding_a_label_next_to_the_building_is_building():
    """The typical floor: the bedroom wing closes its rooms; the kitchen wing, 1 m away across the hall openings,
    holds the kitchen label inside its outline but in no closed face (the kitchen opens to the hall)."""
    import _real01_page as R
    from wenart.ingest.generic import topology as TP

    walls = [R.wall((0, 5), (6, 5)), R.wall((6, 5), (6, 9)), R.wall((6, 9), (0, 9)), R.wall((0, 9), (0, 5)),
             R.wall((0, 4), (0, 0)), R.wall((0, 0), (6, 0)), R.wall((6, 0), (6, 4))]
    labels = [SimpleNamespace(anchor=(3.0, 7.0), exterior=False, name="yatak"),
              SimpleNamespace(anchor=(3.0, 2.0), exterior=False, name="mutfak")]
    bwalls, site, warnings = TP.split_plot(walls, [], labels)
    assert len(bwalls) == 7 and not site["boundary_walls"]
    assert any("a wing of the building" in w for w in warnings)


def test_a_plan_with_too_few_labels_takes_the_documents_wall_layers():
    """real10's 2nd basement (3 labels) and roof terrace (2 labels): too little evidence of their own; they take the
    wall layers the document's other plans chose by evidence."""
    from test_generic_walls import _face_plan

    page, _, _ = _face_plan(texts=False)
    assert not W.face_pair_walls(page, 1.0, [])[1]["used"]
    page.document_wall_layers = ("W1",)
    prims, choice = W.face_pair_walls(page, 1.0, [])
    assert choice["used"] and choice["layer"] == "W1" and choice["reason"] == "the document's other plans"
    assert prims and {p.layer for p in prims} == {"W1"}


# --------------------------------------------------------------------------
# Doors and windows of the exploded drawing
# --------------------------------------------------------------------------

def _gaps(walls, strokes):
    from wenart.ingest.generic import openings as O

    return O.gaps_and_openings(walls, strokes, "test.pdf", 1)


def _leaf(x0, y0, x1, y1):
    import _real01_page as R

    return R.stroke(R.rect(x0, y0, x1, y1), closed=True)


def test_a_door_drawn_open_without_a_swing_arc():
    """real10's doors: a leaf standing at the jamb, opened 90 degrees, no arc. One leaf as long as the gap is a door;
    two leaves of half the gap at both ends (the building entrance) are a double door."""
    import _real01_page as R

    walls = [R.wall((0, 0), (2, 0)), R.wall((2.9, 0), (5, 0))]
    _, openings, _, _ = _gaps(walls, [_leaf(2.0, 0.1, 2.04, 0.95)])
    assert [o.kind for o in openings] == ["door"] and openings[0].width == pytest.approx(0.9)
    walls = [R.wall((0, 0), (2, 0)), R.wall((3.85, 0), (6, 0))]
    _, openings, log, _ = _gaps(walls, [_leaf(2.0, 0.1, 2.04, 0.95), _leaf(3.81, 0.1, 3.85, 0.95)])
    assert [o.kind for o in openings] == ["door"]
    assert [e for e in log if e["kind"] == "run"][0]["class"] == "door"


def test_a_framed_door_hinged_behind_its_frame():
    """real10's balcony door: a 0.70 m leaf in a 0.85 m gap, its hinge 9.5 cm in from the jamb (the frame)."""
    import _real01_page as R

    walls = [R.wall((0, 0), (2, 0)), R.wall((2.85, 0), (5, 0))]
    arc = R.arc((2.095, 0.05), 0.70, 0, 90)
    _, openings, _, _ = _gaps(walls, [arc])
    assert [o.kind for o in openings] == ["door"]


def test_a_double_door_hinged_behind_jamb_blocks():
    """real10's building entrance: a 2.40 m gap, two 0.93 m leaves hinged 0.27 m in from each jamb."""
    import _real01_page as R

    walls = [R.wall((0, 0), (2, 0)), R.wall((4.4, 0), (6, 0))]
    arcs = [R.arc((2.27, 0.05), 0.93, 0, 90), R.arc((4.13, 0.05), 0.93, 90, 180)]
    _, openings, log, _ = _gaps(walls, arcs)
    assert [o.kind for o in openings] == ["door"] and openings[0].width == pytest.approx(2.4)


def test_a_corner_window_gets_a_corner_post():
    """The typical floor's living rooms: glass from the side wall's end round the corner to the front wall's end, no
    wall piece at the corner. A corner post goes where the two walls' lines meet; each leg is a window."""
    import _real01_page as R

    walls = [R.wall((0, 2.1), (0, 5)), R.wall((1.4, 0), (5, 0))]
    glass = [R.stroke([(-0.03, -0.1), (-0.03, 2.1)]), R.stroke([(0.03, -0.1), (0.03, 2.1)]),
             R.stroke([(-0.1, -0.03), (1.4, -0.03)]), R.stroke([(-0.1, 0.03), (1.4, 0.03)])]
    out, openings, _, _ = _gaps(walls, glass)
    posts = [w for w in out if w.entity.startswith("corner:")]
    assert len(posts) == 1 and posts[0].evidence["method"] == "derived"
    assert sorted(o.kind for o in openings) == ["window", "window"]


def test_a_door_right_at_an_l_corner():
    """The master bedroom's balcony door: the wall below it ends inside the balcony wall it meets (no free end);
    the gap from that wall's far face to the pier above holds a door."""
    import _real01_page as R

    walls = [R.wall((0, 0), (3.1, 0)), R.wall((3, -3), (3, 0)), R.wall((3, 0.95), (3, 1.6))]
    arc = R.arc((3.05, 0.12), 0.80, 90, 180)
    _, openings, _, _ = _gaps(walls, [arc])
    assert [o.kind for o in openings] == ["door"]
    assert openings[0].center[0] == pytest.approx(3.0, abs=0.05)


def test_a_column_only_one_wall_ends_on_is_a_pier_kept_whole():
    """The building entrance: a 35 x 80 cm column with one short wall ending on it and no wall through it stands
    free: it is kept whole (a column inside a wall is cut to the wall's band)."""
    from shapely.geometry import box

    col = box(1.0, 0.0, 1.35, 0.8)
    wall = _hpair(0.7, 0.0, 0.97, 0.1)                       # stops 3 cm short (the plaster coat)
    elems = W._network([wall], [(col, "kolon:1")])
    cols = [e for e in elems if e.kind == "column"]
    assert len(cols) == 1 and cols[0].polygon.area == pytest.approx(col.area)


def test_slits_up_to_the_plaster_gap_close_in_the_faces():
    """A 4 cm slit between two walls (masonry stopping at the plaster coat) closes when the faces are made."""
    import _real01_page as R
    from wenart.ingest.generic import topology as TP

    walls = [R.wall((0, 0), (4, 0)), R.wall((4, 0), (4, 3)), R.wall((4, 3), (0, 3)), R.wall((0, 3), (0, 0.12))]
    assert len(TP.faces(walls)) == 1


def test_labels_with_spaced_letters_and_drawing_titles():
    from wenart.ingest.generic import labels as L

    assert L.collapse_spaced("s a l o n") == "salon" and L.collapse_spaced("e. yatak od.") == "e. yatak od."
    assert L.is_drawing_title("TERAS KAT PLANI ÖLÇEK : 1/50") and not L.is_drawing_title("teras")
    from wenart import building as B
    assert B.room_type_for("günlük oda") == "living" and B.room_type_for("SIĞINAK") == "storage"


# --------------------------------------------------------------------------
# Mirrored flats, the roof terrace
# --------------------------------------------------------------------------

def _room(rid, poly, label=None, rtype="hall", level="L0"):
    return {"id": rid, "level_id": level, "polygon": poly, "label": label or "Oda", "label_raw": label,
            "room_type": rtype}


def test_the_unlabelled_mirrored_flat_takes_the_labels_of_the_labelled_one():
    """real10 names the rooms of the left flat only; the right flat mirrors it about the building's axis."""
    from wenart.ingest import twins as TW

    rooms = [_room("a", [[0, 0], [4, 0], [4, 3], [0, 3]], "mutfak", "kitchen"),
             _room("b", [[0, 3], [3, 3], [3, 6], [0, 6]], "salon", "living"),
             _room("c", [[16, 0], [20, 0], [20, 3], [16, 3]]),
             _room("d", [[17, 3], [20, 3], [20, 6], [17, 6]]),
             _room("e", [[8, 0], [12, 0], [12, 6], [8, 6]], "merdiven", "stair")]
    notes = TW.mirror_labels(rooms)
    by = {r["id"]: r for r in rooms}
    assert (by["c"]["label"], by["c"]["room_type"]) == ("mutfak", "kitchen")
    assert (by["d"]["label"], by["d"]["room_type"]) == ("salon", "living")
    assert by["c"]["label_raw"] is None and by["c"]["inferred"] is True
    assert by["c"]["label_inferred"]["method"] == "mirror" and by["c"]["label_inferred"]["axis"] == ["x", 10.0]
    assert len(notes) == 2


def _t(text, y, h=0.2):
    return SimpleNamespace(text=text, height=h, point=(0.0, y), box=(0.0, y - h / 2, 1.0, y + h / 2))


def test_roof_terrace_heights_from_the_section_marks():
    """real10's section A-A: storey labels beside their marks, window heads (+3.30, +21.30) between them, the roof
    terrace at +23.50 (one storey above 6. NORMAL KAT), its parapet +24.40, a door head +25.70, the stair house's
    roof +26.50 and its parapet +26.90."""
    texts = [_t("2. BODRUM KAT", -3.5), _t("- 3.50", -3.5), _t("ZEMİN KAT", 2.5), _t("+ 2.50", 2.5), _t("+ 3.30", 3.3),
             _t("1. NORMAL KAT", 5.5), _t("+ 5.50", 5.5), _t("6. NORMAL KAT", 20.5), _t("+ 20.50", 20.5),
             _t("+ 21.30", 21.3), _t("+ 23.50", 23.5), _t("+ 24.40", 24.4), _t("+ 25.70", 25.7), _t("+ 26.50", 26.5),
             _t("+ 26.90", 26.9)]
    rt = LV.roof_terrace_heights([SimpleNamespace(texts=texts)])
    assert rt["floor_mark"] == 23.5 and rt["parapet_height"] == pytest.approx(0.9)
    assert rt["house_height"] == pytest.approx(3.0)


def test_a_roof_terrace_floor_has_parapets_and_a_flat_roof_over_its_stair_house():
    from wenart.sheets import to_building as TB

    b = {"levels": [{"id": "L7", "order": 7, "elevation": 21.0, "ceiling_height": 2.7, "roof_terrace": True}],
         "rooms": [{"id": "st", "level_id": "L7", "polygon": [[8, 6], [12, 6], [12, 10], [8, 10]]}],
         "walls": [{"id": "h1", "level_id": "L7", "start": [8, 10], "end": [12, 10], "thickness": 0.2, "height": 2.7},
                   {"id": "p1", "level_id": "L7", "start": [0, 0], "end": [20, 0], "thickness": 0.2, "height": 2.7}]}
    sheets = {"heights": {"roof_terrace": {"floor_mark": 23.5, "parapet_height": 0.9, "house_height": 3.0}}}
    terrace = TB.roof_terrace(b, sheets, lambda t: None)
    walls = {w["id"]: w for w in b["walls"]}
    # 4 Nov 2026 (user: "Too much wall on top a little wall with handrails should have been enough"): the 0.9 m mark is
    # the guard's top; the parapet is a 0.5 m low wall with a handrail on it
    assert walls["p1"]["height"] == 0.5 and walls["p1"]["parapet"] is True
    assert walls["p1"]["guard"]["top_m"] == 1.1
    assert walls["h1"]["height"] == 3.0 and not walls["h1"].get("parapet")
    roof = TB.roof_block(sheets, b["levels"], b["rooms"], b["walls"], terrace=terrace)
    assert roof["type"] == "flat" and roof["over_level_id"] == "L7" and roof["eaves_height"]["value"] == 24.0
    xs = [p[0] for p in roof["outline"]]
    assert 7.7 <= min(xs) <= 8.0 and 12.0 <= max(xs) <= 12.3              # the stair house, not the terrace


def test_a_typical_floor_copy_is_rendered_once():
    """The rooms of the levels a typical floor plan stands for are the same as that plan's first level's: the base
    variant renders the first level's room only."""
    from wenart import views as VW

    b = {"levels": [{"id": "L0", "order": 0}, {"id": "L1", "order": 1, "typical_of": "L0"}],
         "rooms": [{"id": "r0", "level_id": "L0"}, {"id": "r1", "level_id": "L1", "same_as": "r0"}],
         "variants": [{"id": "base", "label": "Base", "base": True, "levels": ["L0", "L1"]}]}
    v = VW.views_for(b, twin_rooms="one", exterior_views=True)
    assert v["rooms"] == ["r0"]
    assert {"room_id": "r1", "reason": "same as r0 (typical floor)"} in v["skipped"]


# --------------------------------------------------------------------------
# The real DWG
# --------------------------------------------------------------------------

needs_real10 = pytest.mark.skipif(not dwg.available_converters() or not (PROJECTS / "real10").is_dir(),
                                  reason="LibreDWG dwg2dxf not installed")


@pytest.fixture(scope="module")
def real10_sheet(tmp_path_factory):
    from wenart.sheets import read as RD

    work = tmp_path_factory.mktemp("real10")
    docs = RD.read_documents(PROJECTS / "real10", work)
    return docs[0].sheets[0]


@needs_real10
def test_real10_ten_drawings_with_their_titles(real10_sheet):
    res = SP.split_sheet(real10_sheet)
    drawings = sorted((c for c in res.clusters if c.kind == "drawing"), key=lambda c: c.geometry_box[0])
    titles = [[" ".join(t.text.split()) for t in SP.drawing_titles(c.texts)] for c in drawings]
    assert titles == [["2.BODRUM KAT PLANI"], ["1.BODRUM KAT PLANI"], ["NORMAL KAT PLANI"], ["TERAS KAT PLANI"],
                      ["A - A KESİTİ"], ["B - B KESİTİ"], ["GÜNEY CEPHE"], ["DOĞU CEPHE"], ["KUZEY CEPHE"],
                      ["BATI CEPHE"]]
