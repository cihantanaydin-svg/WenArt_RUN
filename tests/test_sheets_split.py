"""The split of a sheet into drawing regions (docs/milestone10.md §3.1 item 1): frames, title boxes, strays, texts by
their point, small parts joining their drawing, the reading order, and the region clip of the pipeline."""
from __future__ import annotations

import pytest

from _sheets_fixture import PLANS, write_sheet
from wenart.ingest import dxf_generic
from wenart.ingest.generic.model import DimensionPrim, GenericPage, Stroke, TextRun
from wenart.sheets import read as RD
from wenart.sheets import split as SP
from wenart.sheets.model import Ent, Sheet, Txt, entities_from_page, top_entity


@pytest.fixture(scope="module")
def sheet(tmp_path_factory):
    folder = tmp_path_factory.mktemp("sheet")
    write_sheet(folder / "sheet.dxf")
    docs = RD.read_documents(folder, None)
    return docs[0].sheets[0]


def _ent(eid, box, rect=False):
    return Ent(id=eid, kind=eid.split(":")[0], layer="0", box=box, rect=box if rect else None)


def _txt(tid, text, x, y, h=10.0):
    return Txt(id=tid, text=text, box=(x, y, x + len(text) * 0.8 * h, y + h), height=h)


def test_top_entity_ids():
    assert top_entity("INSERT:4B[2]/3") == "INSERT:4B"
    assert top_entity("LWPOLYLINE:2F:1") == "LWPOLYLINE:2F"
    assert top_entity("HATCH:5C#0") == "HATCH:5C"
    assert top_entity("MTEXT:2B:1") == "MTEXT:2B"
    assert top_entity("path:12") == "path:12"


def test_entities_group_strokes_and_join_mtext_paragraphs():
    page = GenericPage(file="a.dxf", page=1, source_kind="dxf", units="dxf", units_to_m=0.01, size=(10, 10),
                       strokes=[Stroke(id="INSERT:4B/0", kind="line", pts=[(0, 0), (1, 0)], block="DOOR"),
                                Stroke(id="INSERT:4B/1", kind="line", pts=[(1, 0), (1, 2)], block="DOOR"),
                                Stroke(id="LWPOLYLINE:9", kind="polyline", pts=[(0, 0), (4, 0), (4, 3), (0, 3)],
                                       closed=True)],
                       texts=[TextRun(id="MTEXT:2B:0", text="SALON", box=(0, 1, 5, 2), height=1),
                              TextRun(id="MTEXT:2B:1", text="46M2", box=(0, 0, 4, 1), height=1)],
                       dimensions=[DimensionPrim(id="DIMENSION:7", p1=(0, 0), p2=(4, 0), measured_units=4.0)])
    ents, texts = entities_from_page(page, "a.dxf")
    by_id = {e.id: e for e in ents}
    assert by_id["INSERT:4B"].box == (0, 0, 1, 2) and by_id["INSERT:4B"].block == "DOOR"
    assert by_id["LWPOLYLINE:9"].rect == (0.0, 0.0, 4.0, 3.0)
    assert by_id["DIMENSION:7"].dim is not None
    assert [t.text for t in texts] == ["SALON 46M2"] and texts[0].box == (0, 0, 5, 2)


def test_fixture_sheet_regions_frames_and_strays(sheet):
    res = SP.split_sheet(sheet)
    assert len(res.frames) == 1 and res.frames[0]["box"] == [0.0, 0.0, 6000.0, 5000.0]
    assert res.gap == pytest.approx(0.015 * (6000 ** 2 + 5000 ** 2) ** 0.5)
    kinds = [c.kind for c in res.clusters]
    assert len(res.clusters) == 6 and kinds[0] == "box"
    titles = [sorted(t.text for t in c.texts) for c in res.clusters]
    assert "PLANLAR" in titles[0]
    # Reading order: the title box, the row of three plans left to right, then the attic and the section.
    for k, key in enumerate(("ground", "basement", "alternative"), start=1):
        x0 = res.clusters[k].geometry_box[0]
        assert x0 == pytest.approx(PLANS[key][0][0])
        assert PLANS[key][1] in titles[k]
    assert any("ÇATI KAT PLANI" in t for t in titles[4])
    assert len(res.strays) == 1 and res.strays[0][0].ents[0].kind == "LINE"


def test_frames_never_bridge_and_texts_never_bridge():
    # Two drawings 300 apart inside a frame; a long title text between them belongs to the nearest one only.
    ents = [_ent("LWPOLYLINE:F", (0, 0, 2000, 1000), rect=True),
            _ent("LINE:1", (100, 100, 700, 700)), _ent("LINE:2", (1000, 100, 1600, 700))]
    texts = [_txt("TEXT:T", "ZEMİN KAT PLANI", 100, 30, h=20)]
    res = SP.split_sheet(Sheet(id="s1", space="model", file="x.dxf", page=1, ents=ents, texts=texts))
    assert len(res.frames) == 1
    assert len(res.clusters) == 2
    holder = [c for c in res.clusters if c.texts]
    assert len(holder) == 1 and holder[0].ents[0].id == "LINE:1"


def _house(dx: float, prefix: str) -> list[Ent]:
    """A 10 x 8 m outline drawn as one closed polyline with three inner walls running into it (cm)."""
    return [_ent(f"LWPOLYLINE:{prefix}O", (dx, 0, dx + 1000, 800), rect=True),
            _ent(f"LINE:{prefix}1", (dx + 400, 0, dx + 410, 800)), _ent(f"LINE:{prefix}2", (dx, 400, dx + 400, 410)),
            _ent(f"LINE:{prefix}3", (dx + 700, 0, dx + 710, 800))] + \
        [_ent(f"LINE:{prefix}f{k}", (dx + 100 + k * 20.0, 100, dx + 110 + k * 20.0, 150)) for k in range(8)]


def test_small_parts_join_their_drawing():
    # Two houses; next to the first a dimension chain 80 units outside it (thin) and a table in a room centre.
    ents = _house(0.0, "a") + [_ent("LINE:D", (0, -80, 1000, -80)), _ent("INSERT:T", (500, 450, 600, 550))]
    ents += _house(2500.0, "b")
    res = SP.split_sheet(Sheet(id="s1", space="model", file="x.dxf", page=1, ents=ents, texts=[]))
    assert res.frames == []                    # a building outline with walls running into it is no frame
    assert len(res.clusters) == 2
    ids = {e.id for e in res.clusters[0].ents}
    assert {"LINE:D", "INSERT:T", "LWPOLYLINE:aO"} <= ids


def test_reading_order_rows():
    from wenart.sheets.split import Cluster
    boxes = {"a": (0, 900, 100, 1000), "b": (500, 880, 600, 990), "c": (0, 0, 100, 100), "d": (300, 400, 400, 600)}
    cs = {k: Cluster(ents=[_ent(f"LINE:{k}", b)]) for k, b in boxes.items()}
    order = SP.reading_order(list(cs.values()))
    assert [c.ents[0].id for c in order] == ["LINE:a", "LINE:b", "LINE:d", "LINE:c"]


def test_clip_page_keeps_entities_by_their_centre(sheet):
    page = sheet.generic_page
    (ox, oy), _ = PLANS["ground"]
    clipped = dxf_generic.clip_page(page, [ox - 10, oy - 200, ox + 1010, oy + 810])
    ents = {dxf_generic.stroke_entity(st.id) for st in clipped.strokes}
    assert any(e.startswith("INSERT:") for e in ents)
    texts = {t.text for t in clipped.texts}
    assert "ZEMİN KAT PLANI" in texts and "SALON" in texts
    # Nothing of the basement plan next to it, nor of the frame whose centre lies elsewhere.
    xs = [p[0] for st in clipped.strokes for p in st.pts]
    assert min(xs) >= ox - 10 and max(xs) <= ox + 1010
    assert len(clipped.strokes) < len(page.strokes) / 3
