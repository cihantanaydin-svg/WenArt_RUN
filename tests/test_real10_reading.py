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
