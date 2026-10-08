"""Region classes from titles (Turkish, English, German, French), level and alternative words, and the geometry
rules for untitled regions (docs/milestone10.md §3.1 items 2-4)."""
from __future__ import annotations

import pytest

from wenart.ingest.generic.model import GenericPage, Stroke
from wenart.sheets import classify as CL
from wenart.sheets import titles as T
from wenart.sheets.model import Ent, Region, Sheet, Txt


@pytest.mark.parametrize("text, cls, lang", [
    ("ZEMİN KAT PLANI", "floor_plan", "tr"),
    ("ÇATI KAT PLANI", "floor_plan", "tr"),
    ("ÇATI PLANI", "roof_plan", "tr"),
    ("ZEMİN KAT MOBİLYA PLANI", "furniture_plan", "tr"),
    ("A-A KESİTİ", "section", "tr"),
    ("GÜNEY GÖRÜNÜŞÜ", "elevation", "tr"),
    ("VAZİYET PLANI", "site_plan", "tr"),
    ("LEJANT", "legend", "tr"),
    ("DETAY 3", "detail", "tr"),
    ("GROUND FLOOR PLAN", "floor_plan", "en"),
    ("SECTION B-B", "section", "en"),
    ("ROOF PLAN", "roof_plan", "en"),
    ("FIRST FLOOR FURNITURE PLAN", "furniture_plan", "en"),
    ("GRUNDRISS ERDGESCHOSS", "floor_plan", "de"),
    ("SCHNITT A-A", "section", "de"),
    ("ANSICHT SÜD", "elevation", "de"),
    ("LAGEPLAN", "site_plan", "de"),
    ("DACHAUFSICHT", "roof_plan", "de"),
    ("PLAN DU REZ-DE-CHAUSSÉE", "floor_plan", "fr"),
    ("COUPE A-A", "section", "fr"),
    ("FAÇADE NORD", "elevation", "fr"),
    ("PLAN DE MASSE", "site_plan", "fr"),
])
def test_class_words(text, cls, lang):
    hit = T.class_of(text)
    assert hit is not None and hit[0] == cls and hit[2] == lang


@pytest.mark.parametrize("text", ["PLANLAR", "SALON 46M2", "ÖLÇEK 1/100", "BANYO", "43.00"])
def test_no_class_without_a_class_word(text):
    assert T.class_of(text) is None


@pytest.mark.parametrize("text, order, kind, label", [
    ("BODRUM KAT PLANI BRÜT 92 M2", -1, "basement", "Bodrum Kat"),
    ("ZEMİN KAT PLANI", 0, "floor", "Zemin Kat"),
    ("1. KAT PLANI", 1, "floor", "1. Kat"),
    ("ÇATI KAT PLANI", None, "attic", "Çatı Katı"),
    ("BASEMENT PLAN", -1, "basement", "Basement"),
    ("SECOND FLOOR PLAN", 2, "floor", "Second Floor"),
    ("3RD FLOOR PLAN", 3, "floor", "3rd Floor"),
    ("ATTIC PLAN", None, "attic", "Attic"),
    ("GRUNDRISS 1. OG", 1, "floor", "1. Obergeschoss"),
    ("GRUNDRISS DACHGESCHOSS", None, "attic", "Dachgeschoss"),
    ("PLAN DU SOUS-SOL", -1, "basement", "Sous-sol"),
])
def test_level_words(text, order, kind, label):
    lw = T.level_of(text)
    assert (lw.order, lw.kind, lw.label) == (order, kind, label)


@pytest.mark.parametrize("text, expect", [
    ("BODRUM KAT PLANI BRÜT 92 M2 ( Açık mutfak)", ("Açık mutfak", "bracket")),
    ("BODRUM KAT PLANI BRÜT 92 M2 ", None),
    ("ZEMİN KAT PLANI ALTERNATİF 2", ("2", "word")),
    ("GROUND FLOOR PLAN - OPTION B", ("B", "word")),
    ("ZEMİN KAT PLANI (92 m²)", None),
    ("1. KAT PLANI (1/100)", None),
])
def test_alternative_words(text, expect):
    assert T.alternative_of(text) == expect


def test_slug_and_gloss():
    assert T.slug("Açık mutfak") == "acik-mutfak"
    assert T.gloss("Açık mutfak") == "open kitchen" and T.gloss("Something") is None


def _region(ents, texts, kind="drawing") -> Region:
    sheet = Sheet(id="s1", space="model", file="x.dxf", page=1,
                  generic_page=GenericPage(file="x.dxf", page=1, source_kind="dxf", units="dxf", units_to_m=0.01,
                                           size=(1, 1)))
    from wenart.sheets.model import box_union
    box = box_union([e.box for e in ents]) if ents else box_union([t.box for t in texts])
    return Region(id="r1", file="x.dxf", sheet=sheet, box=box, geometry_box=box, ents=ents, texts=texts, kind=kind)


def _line_ent(eid, a, b):
    st = Stroke(id=eid, kind="line", pts=[a, b], layer="0")
    return Ent(id=eid, kind="LINE", layer="0", box=st.bbox(), strokes=[st])


def test_title_decides_and_the_tallest_keyword_text_wins():
    ents = [_line_ent("LINE:1", (0, 0), (1000, 0)), _line_ent("LINE:2", (0, 0), (0, 800))]
    texts = [Txt("TEXT:1", "SALON", (100, 100, 160, 115), 15), Txt("TEXT:2", "ZEMİN KAT PLANI", (0, -200, 600, -150),
                                                                  50)]
    r = _region(ents, texts)
    assert CL.by_title(r)
    assert (r.cls, r.class_method, r.status) == ("floor_plan", "title", "verified")
    assert r.title["text"] == "ZEMİN KAT PLANI" and r.title["language"] == "tr"
    assert r.evidence[0]["rule"] == "title_keyword" and r.evidence[0]["entity"] == "TEXT:2"


def test_section_by_geometry():
    lines = []
    for x in (0.0, 20.0, 980.0, 1000.0):
        lines.append(((x, 0.0), (x, 615.0)))
    for y in (0.0, 15.0, 300.0, 315.0, 615.0, 630.0):
        lines.append(((0.0, y), (1000.0, y)))
    lines += [((-50.0, 680.0), (500.0, 980.0)), ((500.0, 980.0), (1050.0, 680.0))]
    ents = [_line_ent(f"LINE:{k}", a, b) for k, (a, b) in enumerate(lines)]
    r = _region(ents, [])
    f = CL.features(r, 0.01)
    assert f["slab_bands"] == 3 and f["roof_lines"] == 2 and f["outer_walls"]
    assert CL.by_geometry(r, f, [], 100.0)
    assert (r.cls, r.class_method) == ("section", "geometry")
    CL.use_of(r)
    assert r.use == "heights"


def test_lone_rectangle_with_a_text_is_a_title_block():
    st = Stroke(id="LWPOLYLINE:9", kind="polyline", pts=[(0, 0), (5000, 0), (5000, 400), (0, 400)], closed=True)
    ent = Ent(id="LWPOLYLINE:9", kind="LWPOLYLINE", layer="0", box=(0, 0, 5000, 400), strokes=[st],
              rect=(0, 0, 5000, 400))
    r = _region([ent], [Txt("MTEXT:1", "PLANLAR", (100, 100, 1000, 300), 200)], kind="box")
    f = CL.features(r, 0.01)
    assert CL.by_geometry(r, f, [], 100.0) and r.cls == "title_block" and r.title["text"] == "PLANLAR"
    CL.use_of(r)
    assert r.use == "ignored" and r.ignored_reason == "title block"


def test_room_labels_alone_never_make_a_plan():
    r = _region([], [Txt("TEXT:1", "SALON", (0, 0, 60, 15), 15), Txt("TEXT:2", "MUTFAK", (200, 0, 260, 15), 15)],
                kind="text")
    f = CL.features(r, 0.01)
    assert not CL.by_geometry(r, f, [], 100.0)
    CL.use_of(r)
    assert r.use == "ignored" and r.class_method == "none"


@pytest.mark.parametrize("label, subtype", [("ÇOCUK ODASI", "child"), ("Kid's room", "child"), ("Nursery", "child"),
                                            ("BEBEK ODASI", "child"), ("YATAK ODASI", None), ("Salon", None)])
def test_room_subtype(label, subtype):
    assert CL.room_subtype(label) == subtype
