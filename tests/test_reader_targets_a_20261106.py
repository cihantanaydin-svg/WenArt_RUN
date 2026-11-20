"""The Milestone 14 reader targets of 6 Nov 2026 (found by the machine reviewers on current readings, verified by blind
judges), each a general rule with the project that showed it as its test case only (user rule of 26 Oct 2026: "fix
should be general ... don't ever forget that"):

1. model-space ATTDEFs are texts (real18: OTOPARK, A:102.52M2 and the room names of two floors are ATTDEF tags);
2. (withdrawn on 12 Nov 2026 after the review: the region-box frame rule dropped the outer walls of a building drawn
   tight in its region (tests/test_sheets_pipeline.py), the frame-layer and paper-face rules fired on no real reading;
   RC14 keeps finding a sheet frame read as walls);
3. notation phrases are split off a label before naming (real11: 'Bına Taban Hattı Yatak Odası'), one table for the
   reader and RC14; a floor's name or a lone area-summary word is no label (real19: 'NORMAL', 'BRÜT' over their areas);
4. a room schedule is a list, never labels (real14: 'MAHAL / SALON / MUTFAK / ...' beside every plan);
5. a small room's label names only its own sub-space of a much larger face holding a stair or another label (real20,
   real11: 'Asansör' over the stair hall).
"""
from __future__ import annotations

from pathlib import Path

import ezdxf
import pytest

from wenart.ingest import dxf_generic as DG


def _doc(insunits: int = 5):
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = insunits
    return doc


def _save(doc, tmp_path: Path, name: str = "plan.dxf") -> Path:
    path = tmp_path / name
    doc.saveas(path)
    return path


# --------------------------------------------------------------------------
# 1. Model-space ATTDEFs
# --------------------------------------------------------------------------

def _attdef_doc():
    doc = _doc()
    doc.layers.add("03_Yazi")
    msp = doc.modelspace()
    name = msp.add_attdef("OTOPARK", (100, 200), "Y.ODASI", height=15, dxfattribs={"layer": "03_Yazi",
                                                                                  "prompt": "BÖLÜM"})
    area = msp.add_attdef("A:102.52M2", (100, 180), "A:10.00m2", height=12.5, dxfattribs={"layer": "03_Yazi"})
    hidden = msp.add_attdef("GIZLI", (0, 0), "x", height=10)
    hidden.dxf.flags = 1                                                # an invisible definition: data, not drawn
    tag = doc.blocks.new("ROOMTAG")
    tag.add_attdef("NAME", (0, 0), height=9)                            # a block's template: never a text
    ref = msp.add_blockref("ROOMTAG", (10, 20), dxfattribs={"layer": "A-ANNO"})
    ref.add_auto_attribs({"NAME": "KITCHEN"})
    return doc, name, area


def test_model_space_attdefs_are_read_as_the_tag_cad_shows(tmp_path):
    doc, name, area = _attdef_doc()
    page = DG.read_page(_save(doc, tmp_path), "plan.dxf")
    texts = {t.text: t for t in page.texts}
    assert set(texts) == {"OTOPARK", "A:102.52M2", "KITCHEN"}          # the tag, never the default value
    t = texts["OTOPARK"]
    assert t.id == f"ATTDEF:{name.dxf.handle}" and t.height == 15
    assert t.box[0] == pytest.approx(100) and t.box[1] < 200 < t.box[3]
    ev = t.evidence[0]
    assert ev["layer"] == "03_Yazi" and ev["entity"] == t.id and ev["text"] == "OTOPARK"
    assert (ev["attdef_tag"], ev["attdef_default"], ev["attdef_prompt"]) == ("OTOPARK", "Y.ODASI", "BÖLÜM")
    assert "attrib_tag" not in ev                    # the tag is the text itself, not a level-mark attribute's name
    assert texts["A:102.52M2"].id == f"ATTDEF:{area.dxf.handle}"
    assert not any("ATTDEF" in w for w in page.warnings)


def test_attdefs_are_texts_for_the_sheets_stage_too(tmp_path):
    doc, _name, _area = _attdef_doc()
    path = _save(doc, tmp_path)
    texts = {t.text for t in DG.collect_texts(ezdxf.readfile(path), "plan.dxf")}
    assert texts == {"OTOPARK", "A:102.52M2", "KITCHEN"}


def test_attdef_room_name_and_area_make_one_label_block(tmp_path):
    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic import labels as LB

    doc, _name, _area = _attdef_doc()
    page = DG.read_page(_save(doc, tmp_path), "plan.dxf")
    _strokes, texts_m = GC.to_metres(page, 0.01)
    blocks = [b for b in LB.merge_label_blocks(texts_m, "plan.dxf") if "OTOPARK" in b.name]
    assert len(blocks) == 1 and blocks[0].area_m2 == pytest.approx(102.52)


# --------------------------------------------------------------------------
# helpers: walls, label blocks (page metres = building metres here)
# --------------------------------------------------------------------------

def _wall(start, end, t=0.2, entity="w"):
    from wenart import building as B
    from wenart.ingest.model import WallItem

    return WallItem(tuple(start), tuple(end), t, [0, 0, 0, 0], entity, B.evidence("p.dxf", "vector", 1.0,
                                                                                  entity=entity))


def _box_walls(x0, y0, x1, y1, t=0.2, tag="b"):
    h = t / 2
    return [_wall((x0, y0 + h), (x1, y0 + h), t, f"{tag}1"), _wall((x1 - h, y0), (x1 - h, y1), t, f"{tag}2"),
            _wall((x0, y1 - h), (x1, y1 - h), t, f"{tag}3"), _wall((x0 + h, y0), (x0 + h, y1), t, f"{tag}4")]


def _run(text, x, y, h=0.2, k=0):
    from wenart.ingest.generic.model import TextRun

    w = 0.8 * h * len(text)
    return TextRun(id=f"TEXT:{k}", text=text, box=(x - w / 2, y - 0.25 * h, x + w / 2, y + h), height=h)


def _labels(*items):
    """TextItems with label blocks from (name, (x, y)) items (one run each)."""
    from wenart.ingest.generic import labels as LB
    from wenart.ingest.model import TextItem

    runs = [_run(name, x, y, k=k) for k, (name, (x, y)) in enumerate(items)]
    blocks = LB.merge_label_blocks(runs, "p.dxf")
    out = [TextItem(b.name, b.anchor, list(b.box), 0.0, b.name_runs[0].id, 0.2, role="room_label",
                    evidence=b.evidence[0], block=b, turkish=True) for b in blocks]
    return out, [b.anchor for b in blocks]


# --------------------------------------------------------------------------
# 3. Notation is split off a label before naming
# --------------------------------------------------------------------------

def test_notation_phrases_are_split_off_a_label_line():
    from wenart.ingest.generic import labels as LB

    assert LB.split_notation("TESİSAT DUVARI H: 1.20 Cm")[0] == ""
    assert LB.split_notation("Bına Taban Hattı Yatak Odası")[0] == "Yatak Odası"
    assert LB.split_notation("BİNA TABAN HATTI")[0] == ""
    assert LB.split_notation("SAÇAK İZDÜŞÜMÜ")[0] == ""
    assert LB.split_notation("GİRİŞ SAÇAK")[0] == "GİRİŞ SAÇAK"          # a canopy, an outdoor space (real11)
    assert LB.split_notation("SAÇAK ALTI")[0] == "SAÇAK ALTI" and LB.split_notation("SAÇAK")[0] == "SAÇAK"
    # real11: 'GİRİŞ' over 'SAÇAK' (two texts) is the entrance canopy, one block with both words
    runs = [_run("GİRİŞ", 5, 5.3, k=1), _run("SAÇAK", 5, 5.0, k=2)]
    assert [b.name for b in LB.merge_label_blocks(runs, "p.dxf")] == ["GİRİŞ SAÇAK"]
    assert LB.split_notation("-3.00 KOTU OTOPARK")[0] == "OTOPARK"
    assert LB.split_notation("TESİSAT ODASI") == ("TESİSAT ODASI", [])            # a services room is a room
    assert not LB._is_name_text("TESİSAT DUVARI", False) and LB._is_name_text("Tesisat", False)


def test_a_notation_line_never_joins_a_room_label_block():
    from wenart.ingest.generic import labels as LB

    runs = [_run("BİNA TABAN HATTI", 5, 5.3, k=1), _run("YATAK ODASI", 5, 5.0, k=2),
            _run("TESİSAT DUVARI", 12, 5.3, k=3), _run("H: 1.20 Cm", 12, 5.0, k=4),
            _run("Bina Taban Hattı Salon", 20, 5, k=5)]
    names = sorted(b.name for b in LB.merge_label_blocks(runs, "p.dxf"))
    assert names == ["Salon", "YATAK ODASI"]


def test_a_floor_name_or_a_lone_summary_word_over_an_area_is_no_label():
    """real19 L1-L3 (once the frame was no room): the sheet's area summary 'NORMAL' / 'BRÜT' / 'OTURUM' over '253 M2'
    stood as room labels outside the walls and marked the floors low-confidence."""
    from wenart.ingest.generic import labels as LB

    assert LB.is_floor_name("NORMAL") and LB.is_floor_name("ZEMİN") and not LB.is_floor_name("TERAS")
    assert not LB.is_floor_name("SALON") and not LB.is_floor_name("1. NORMAL")
    assert LB.is_annotation("BRÜT") and LB.is_annotation("OTURUM") and not LB.is_annotation("SALON")
    runs = [_run("NORMAL", 5, 5.3, k=1), _run("253 M2", 5, 5.0, k=2), _run("BRÜT", 9, 5.3, k=3),
            _run("280 M2", 9, 5.0, k=4), _run("SALON", 15, 5.3, k=5), _run("24 M2", 15, 5.0, k=6)]
    blocks = LB.merge_label_blocks(runs, "p.dxf")
    assert [b.name for b in blocks] == ["SALON"] and blocks[0].area_m2 == pytest.approx(24.0)


def test_a_finish_note_is_no_label():
    """real15: 'SERAMIK 33X33' of the finishes table beside the plan stood as a room label outside the walls; a finish
    line under a room's name never joins the name either."""
    from wenart.ingest.generic import labels as LB

    assert LB.is_finish_note("SERAMIK  33X33") and LB.is_finish_note("AHŞAP PARKE") and LB.is_finish_note("K:MARLEY")
    assert not LB.is_finish_note("SALON") and not LB.is_finish_note("ASMA KAT") and not LB.is_finish_note("33X33")
    runs = [_run("SERAMIK 33X33", 5, 5.0, k=1), _run("SALON", 15, 5.3, k=2), _run("PARKE", 15, 5.0, k=3)]
    assert [b.name for b in LB.merge_label_blocks(runs, "p.dxf")] == ["SALON"]


def test_the_reader_and_the_checker_share_one_notation_table():
    from wenart.ingest.generic import labels as LB
    from wenart.reading_check import sense as SE

    assert SE.NOTATION_PHRASES is LB.NOTATION_PHRASES and SE._NOTATION_RE is LB.NOTATION_RE
    assert SE.notation_in("Bına Taban Hattı Yatak Odası") == ["the building's footprint line"]


# --------------------------------------------------------------------------
# 4. A room schedule is a list, never labels
# --------------------------------------------------------------------------

SCHEDULE = ("SALON", "MUTFAK", "ODA", "YATAK ODASI", "WC", "BANYO", "ANTRE")


def _schedule_runs(x=50.0, y=10.0, header="MAHAL", skip=()):
    runs = [_run(header, x, y + 0.5, h=0.35, k=900)] if header else []
    for k, name in enumerate(SCHEDULE):
        if name not in skip:
            runs.append(_run(name, x, y - 0.5 * k, k=k + 100))
        runs.append(_run("PARKE", x + 3, y - 0.5 * k, k=k + 200))          # the finishes column beside it
    return runs


def test_a_column_of_room_words_under_a_header_is_a_schedule():
    from wenart.ingest.generic import labels as LB

    found = LB.schedules(_schedule_runs())
    assert len(found) == 1 and found[0]["header"] == "MAHAL" and found[0]["axis"] == "column"
    assert found[0]["room_words"][:2] == ["SALON", "MUTFAK"] and "header" in found[0]["why"]
    plan = [_run("SALON", 2, 2, k=1), _run("MUTFAK", 2, 6, k=2), _run("YATAK ODASI", 6, 2, k=3),
            _run("BANYO", 6, 6, k=4)]
    blocks = LB.merge_label_blocks(plan + _schedule_runs())
    assert sorted(b.name for b in blocks) == ["BANYO", "MUTFAK", "SALON", "YATAK ODASI"]
    # the schedule with two empty cells (real14 L5) is still one list under its header
    found = LB.schedules(_schedule_runs(skip=("MUTFAK", "ODA")))
    assert len(found) == 1 and found[0]["room_words"][0] == "SALON"


def test_a_schedule_under_an_upright_header_with_wider_rows_is_found():
    """real15: 'MAHAL' 'LİSTESİ' written upright (90 degrees, twice the entries' height) over a column whose rows stand
    4.2 line heights apart; without a header such a column is not a list."""
    from dataclasses import replace

    from wenart.ingest.generic import labels as LB

    runs = [_run(name, 50.0, 10.0 - 0.84 * k, k=k + 100) for k, name in enumerate(SCHEDULE)]
    header = _run("MAHAL", 0, 0, h=0.4, k=900)
    w = header.box[2] - header.box[0]
    header = replace(header, box=(49.5, 10.6, 49.5 + 0.5, 10.6 + w), rotation_deg=90.0)
    found = LB.schedules(runs + [header])
    assert len(found) == 1 and found[0]["header"] == "MAHAL" and len(found[0]["room_words"]) >= 6
    from shapely.geometry import box
    assert LB.schedules(runs, hull=box(0, 0, 20, 20)) == []        # 4.2 heights apart and no header: not a list


def test_a_list_without_a_header_is_a_schedule_only_outside_the_walls():
    from shapely.geometry import box

    from wenart.ingest.generic import labels as LB

    runs = _schedule_runs(header=None)
    assert LB.schedules(runs) == []
    assert len(LB.schedules(runs, hull=box(0, 0, 20, 20))) == 1                     # outside the building
    assert LB.schedules(runs, hull=box(40, 0, 60, 20)) == []                         # inside it: labels
    # plan labels stand rooms apart, never a list
    plan = [_run(n, 2 + 4 * (k % 2), 2 + 4 * (k // 2), k=k) for k, n in enumerate(SCHEDULE)]
    assert LB.schedules(plan, hull=box(100, 100, 120, 120)) == []


def test_the_schedules_found_are_handed_back_without_their_runs():
    from wenart.ingest.generic import labels as LB

    out: list = []
    LB.merge_label_blocks(_schedule_runs(), schedules_out=out)
    assert out and "_runs" not in out[0] and out[0]["run_ids"][-1] == "TEXT:900"


# --------------------------------------------------------------------------
# 5. A small room's label names only its own sub-space of a much larger face
# --------------------------------------------------------------------------

def _stair(x, y):
    from types import SimpleNamespace

    return SimpleNamespace(center=(x, y), type="stair")


def test_a_lift_label_over_the_stair_hall_does_not_name_it():
    from wenart.ingest import rooms as R

    walls = _box_walls(0, 0, 4.2, 4.2)                     # a 16 m2 face (4.0 x 4.0 inside)
    labels, points = _labels(("Asansör", (1.0, 1.0)),)
    res = R.derive_rooms("L0", walls, labels, points, None, "p.dxf", stairs=[_stair(2.5, 2.5)],
                         unlabelled_label="Oda", face_type=lambda poly: ("hall", "unlabelled face holding the stair"))
    assert [r["label"] for r in res.rooms] == ["Oda"] and res.rooms[0]["room_type"] == "hall"
    assert res.rooms[0]["status"] == "unverified" and res.sub_space_labels[0]["type"] == "lift"
    assert any("names only its own sub-space" in w for w in res.warnings)
    # with the hall's own label in the face, that label names it
    labels, points = _labels(("Asansör", (1.0, 1.0)), ("Merdiven Holü", (2.5, 3.0)))
    res = R.derive_rooms("L0", walls, labels, points, None, "p.dxf", stairs=[_stair(2.5, 2.5)])
    assert [r["label"] for r in res.rooms] == ["Merdiven Holü"]


def test_a_small_room_keeps_its_name_when_the_face_fits_it_or_nothing_else_stands_in_it():
    from wenart.ingest import rooms as R

    lift = _box_walls(0, 0, 2.2, 2.2)                      # a 4 m2 lift shaft
    labels, points = _labels(("Asansör", (1.0, 1.0)),)
    assert R.derive_rooms("L0", lift, labels, points, None, "p.dxf", stairs=[_stair(1.1, 1.1)]
                          ).rooms[0]["label"] == "Asansör"
    big = _box_walls(0, 0, 4.2, 4.2)                       # 16 m2, nothing else in it: the rule does not apply
    assert R.derive_rooms("L0", big, labels, points, None, "p.dxf").rooms[0]["label"] == "Asansör"
    # two WCs in one face (their partition unread) stay a WC: no other kind of room stands in it
    wcs, pts = _labels(("WC", (1.0, 1.0)), ("WC", (3.0, 3.0)))
    assert R.derive_rooms("L0", big, wcs, pts, None, "p.dxf").rooms[0]["label"] == "WC"


def test_the_reader_and_the_checker_share_the_area_table():
    from wenart.ingest.generic import labels as LB
    from wenart.reading_check import sense as SE

    assert SE.AREA_RANGES is LB.AREA_RANGES and SE.SENSE_WORDS is LB.SENSE_WORDS
    assert LB.sub_space_type("Asansör", "shaft") == "lift"
    assert LB.sub_space_type("Asansör Makina Dairesi", "shaft") is None
    assert LB.sub_space_type("WC", "wc") == "wc" and LB.sub_space_type("Banyo-wc", "wc") is None
    assert LB.sub_space_type("Vestiyer", "other") == "closet" and LB.sub_space_type("Salon", "living") is None


# --------------------------------------------------------------------------
# Review of 12 Nov 2026, item 1 (real07): storey marks on their floor lines, slabs follow, a garage door's drive
# --------------------------------------------------------------------------

def _mark_section(landing: bool = True):
    """A section 12 m wide (units: cm): the storey marks ±0.00 (ground), +0.50 (ZEMİN KAT) and +3.50 (I.KAT) in both
    columns beside the cut on their floor and slab lines, the eaves +6.50; a stair-landing mark +2.00 inside the cut
    on a 1.2 m landing line; the storey names in the middle of their storeys."""
    from types import SimpleNamespace

    from wenart.ingest.generic.model import Stroke
    from wenart.sheets.model import Txt

    h = 15.0
    strokes, texts = [], []

    def line(x0, x1, y):
        strokes.append(Stroke(id=f"L{len(strokes)}", kind="line", pts=[(x0, y), (x1, y)]))

    def mark(x, y, text):
        # the mark's triangle: two short sloped strokes meeting at their lowest point (the apex) on the line
        strokes.append(Stroke(id=f"T{len(strokes)}", kind="line", pts=[(x, y), (x - 10.0, y + 12.0)]))
        strokes.append(Stroke(id=f"T{len(strokes)}", kind="line", pts=[(x, y), (x + 10.0, y + 12.0)]))
        texts.append(Txt(id=f"m{len(texts)}", text=text, box=(x - 25.0, y + 14.0, x + 25.0, y + 14.0 + h), height=h))

    line(-300.0, 1500.0, 0.0)                              # the ground line
    line(0.0, 1200.0, 50.0)                                # the ground floor's slab
    line(0.0, 1200.0, 350.0)                               # the 1st floor's slab
    line(0.0, 1200.0, 650.0)                               # the roof
    for x in (-150.0, 1350.0):                             # the two mark columns beside the cut
        line(x - 60.0, x + 60.0, 0.0)
        for y, t in ((0.0, "±0.00"), (50.0, "+0.50"), (350.0, "+3.50"), (650.0, "+6.50")):
            mark(x, y, t)
    if landing:
        line(500.0, 620.0, 200.0)                          # the half landing (1.2 m)
        mark(560.0, 200.0, "+2.00")
    texts.append(Txt(id="n0", text="ZEMİN KAT", box=(300.0, 210.0, 420.0, 225.0), height=h))
    texts.append(Txt(id="n1", text="I.KAT", box=(300.0, 500.0, 380.0, 515.0), height=h))
    return SimpleNamespace(id="r5", texts=texts, use="heights", cls="section", strokes=lambda: list(strokes))


def test_a_section_names_its_storeys_by_the_marks_on_their_floor_lines_never_a_landing_mark():
    from types import SimpleNamespace

    from wenart.sheets import levels as LV
    from wenart.sheets import units_check as UC

    got = LV.storey_elevations([_mark_section()])
    assert got[0] == 0.5 and got[1] == 3.5                 # not the landing's +2.00 under 'ZEMİN KAT'
    sec = _mark_section()
    ev = LV.mark_evidence(sec, UC.mark_texts(sec.texts), 0.0, 0.01)
    assert ev[0.5]["repeated"] and ev[2.0] == {"on_line": False, "repeated": False}     # the landing: lone, short line
    # without strokes (an old sheets reading) every mark counts, as before
    assert LV.mark_evidence(SimpleNamespace(texts=sec.texts), [], 0.0, 0.01) == {}


def _columns_section(storeys, slabs=(), names=(), lone=(), line_len=1200.0, split=False):
    """A section (units cm, 1 unit = 1 cm): ``storeys`` (value m) printed in two columns beside the cut with no long
    line at their apex; ``slabs`` (value m) printed once on a long line; ``lone`` (value m) printed once on a short
    line; ``names`` (text, value m of the floor it stands on)."""
    from wenart.ingest.generic.model import Stroke
    from wenart.sheets.model import Txt

    strokes, texts = [], []

    def mark(x, v, text=None):
        y = v * 100.0
        strokes.append(Stroke(id=f"T{len(strokes)}", kind="line", pts=[(x, y), (x - 10.0, y + 12.0)]))
        strokes.append(Stroke(id=f"T{len(strokes)}", kind="line", pts=[(x, y), (x + 10.0, y + 12.0)]))
        texts.append(Txt(id=f"m{len(texts)}", text=text or f"{v:+.2f}", box=(x - 25, y + 14, x + 25, y + 29), height=15.0))

    for v in storeys:
        for x in (-150.0, 1350.0):
            strokes.append(Stroke(id=f"S{len(strokes)}", kind="line", pts=[(x - 40, v * 100), (x + 40, v * 100)]))
            mark(x, v)
    for v in slabs:
        if split:                                          # the slab line cut at the walls into 2 m pieces
            for x0 in range(0, int(line_len), 200):
                strokes.append(Stroke(id=f"L{len(strokes)}", kind="line", pts=[(x0, v * 100), (x0 + 200, v * 100)]))
        else:
            strokes.append(Stroke(id=f"L{len(strokes)}", kind="line", pts=[(0.0, v * 100), (line_len, v * 100)]))
        mark(600.0, v)
    for v in lone:
        strokes.append(Stroke(id=f"W{len(strokes)}", kind="line", pts=[(500.0, v * 100), (720.0, v * 100)]))
        mark(610.0, v)
    for k, (text, v) in enumerate(names):
        texts.append(Txt(id=f"n{k}", text=text, box=(300.0, v * 100 + 120, 420.0, v * 100 + 135), height=15.0))
    from types import SimpleNamespace
    return SimpleNamespace(id="rX", texts=texts, cls="section", strokes=lambda: list(strokes))


def test_storey_marks_in_columns_win_over_slab_marks_on_long_lines_and_a_short_roof_line_keeps_its_mark():
    from wenart.sheets import levels as LV

    # real13: storey marks (four columns, no long line) 0.3 m above slab marks on long lines
    sec = _columns_section([3.7, 6.4, 9.1, 11.8], slabs=[3.4, 6.1, 7.9, 10.6],
                           names=[("ZEMİN KAT", 3.7), ("1.KAT", 6.4), ("2.KAT", 9.1), ("3.KAT", 11.8)])
    assert LV.storey_elevations([sec]) == {0: 3.7, 1: 6.4, 2: 9.1, 3: 11.8}
    # real09: the roof storey's mark printed once on a short line keeps its value, never the storey below's
    roof = _columns_section([0.0, 2.5, 5.5, 8.5], lone=[11.5],
                            names=[("1.BODRUM KAT", 0.0), ("ZEMİN KAT", 2.5), ("1.NORMAL KAT", 5.5),
                                   ("2.NORMAL KAT", 8.5), ("ÇATI KAT", 11.5)])
    assert LV.storey_elevations([roof])["top"] == 11.5
    # a slab line cut at its walls into 2 m pieces is one floor line; a value printed in one column stays
    split = _columns_section([0.0, 3.0], slabs=[6.0], split=True,
                             names=[("ZEMİN KAT", 0.0), ("1.KAT", 3.0), ("2.KAT", 6.0)])
    assert LV.storey_elevations([split]) == {0: 0.0, 1: 3.0, 2: 6.0}


def test_the_datum_from_the_storey_marks_is_the_ground_floors_floor_mark():
    from wenart.sheets import heights as HT
    from wenart.sheets import levels as LV

    storey_el = LV.storey_elevations([_mark_section()])
    levels = [{"id": "L0", "order": 0, "kind": "floor"}, {"id": "L1", "order": 1, "kind": "floor"}]
    out = {"levels": [], "slabs": [{"between": [None, "L0"]}, {"between": ["L0", "L1"]}]}
    HT.apply_storey_marks(out, levels, storey_el, 0.2, "x.dwg", "r5")
    assert out["datum"]["relative"] == 0.5
    assert {e["level_id"]: e["floor_z"]["value"] for e in out["levels"]} == {"L0": 0.0, "L1": 3.0}
    assert [s["z_top"]["value"] for s in out["slabs"]] == [0.0, 3.0]


def test_a_level_moved_by_its_floor_marks_takes_its_slab_and_keeps_its_place_among_the_storeys():
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    b = F.building(label="1. Kat", order=1, elevation=3.0)
    b["levels"].insert(0, dict(b["levels"][0], id="L00", order=0, elevation=0.0, label="Zemin Kat"))
    b["slabs"] = [{"id": "sl_L00", "below_level_id": None, "above_level_id": "L00", "z_top": 0.0},
                  {"id": "sl_L0", "below_level_id": "L00", "above_level_id": "L0", "z_top": 3.0}]
    b["level_marks"] = [F.mark("lm_001", 3.20, kind="floor", point=(3.0, 4.0), room_id="r_living"),
                        F.mark("lm_002", 3.20, kind="floor", point=(8.0, 4.0), room_id="r_hall")]
    n = M.infer_levels(b)
    assert next(x for x in n["levels"] if x["id"] == "L0")["elevation"] == 3.2
    assert {s["id"]: s["z_top"] for s in n["slabs"]} == {"sl_L00": 0.0, "sl_L0": 3.2}
    assert any("slab sl_L0" in w for w in n["level_inference"]["warnings"])
    # marks that would put the 1st floor on or under the ground floor are no floor marks of it
    for m in b["level_marks"]:
        m["value"] = m["z"] = -0.5
    n = M.infer_levels(b)
    assert next(x for x in n["levels"] if x["id"] == "L0")["elevation"] == 3.0
    assert {s["id"]: s["z_top"] for s in n["slabs"]} == {"sl_L00": 0.0, "sl_L0": 3.0}
    assert any("out of the storeys' order" in w for w in n["level_inference"]["warnings"])


def _garage_building(rise: float = 0.5, width: float = 2.5, rtype: str = "garage", label: str = "Garaj"):
    from tests import _levels_fixture as F

    b = F.building()
    b["project"]["brief"] = {"levels": {"ground_rise": rise}}
    b["rooms"][1].update(room_type=rtype, label=label, label_raw=label.upper())
    b["openings"][0]["width"] = width
    return b


def test_a_garage_door_gets_a_drive_down_to_the_ground_never_steps():
    from wenart.blender import site as S
    from wenart.levels import checks as LC
    from wenart.levels import model as M

    b = M.infer_levels(_garage_building())
    e = next(x for x in b["site"]["entrances"] if x["door_id"] == "d_front")
    assert e["solution"] == "drive" and e["steps"] is None and e["landing"] is None
    assert e["ramp"]["drive"] is True and e["ramp"]["slope"] == 0.12 and e["ramp"]["width"] == 3.1
    assert e["ramp"]["length"] == pytest.approx(0.5 / 0.12, abs=1e-3) and e["ramp"]["handrails"] is False
    assert not [v for v in LC.check_levels(b) if v.get("target") == "d_front" or v.get("element_id") == "d_front"]
    import json

    import jsonschema
    schema = json.loads((Path(__file__).resolve().parents[1] / "wenart" / "schema" / "building.schema.json")
                        .read_text(encoding="utf-8"))
    entrances = schema["properties"]["site"]
    assert "drive" in json.dumps(entrances) and not [
        e for e in jsonschema.Draft202012Validator(schema).iter_errors(b) if "entrances" in list(e.absolute_path)]
    # the site builds it straight out from the door, centred, from the floor down to the ground; no landing
    ent = {"opening_id": "d_front", "centre": [8.0, 0.0], "outward": [0.0, -1.0], "half_t": 0.1, "width": 2.5,
           "bottom": 0.0, "ground_z": -0.5, "rise": 0.5, "record": e}
    st = S.entrance_steps(ent)
    assert st["solution"] == "drive" and st["blocks"] == [] and st["rails"] == []
    poly = st["ramp"]["polygon"]
    assert st["ramp"]["z_start"] == 0.0 and st["ramp"]["z_end"] == -0.5
    ys = sorted({round(p[1], 3) for p in poly})
    xs = sorted({round(p[0], 3) for p in poly})
    assert ys == [round(-0.1 - 0.5 / 0.12, 3), -0.1] and xs == [6.45, 9.55]
    assert round(poly[0][1], 3) == -0.1 and round(poly[-1][1], 3) == -0.1     # ramp_solid: z_start at the door
    # a narrow door into a garage (a person's door) keeps its steps; a garage door type always drives
    assert _ent_solution(_garage_building(width=0.9)) == "steps"
    b2 = _garage_building(width=0.9, rtype="storage", label="Depo")
    b2["openings"][0]["door_type"] = "garage_sectional"
    assert _ent_solution(b2) == "drive"


def _ent_solution(b):
    from wenart.levels import model as M

    return next(x for x in M.infer_levels(b)["site"]["entrances"] if x["door_id"] == "d_front")["solution"]


# --------------------------------------------------------------------------
# Review of 12 Nov 2026, item 3 (real11, real20): a lift keeps its shaft and its label
# --------------------------------------------------------------------------

def _core_levels(lift_label_on=("L0",), levels=("L0", "L1", "L2")):
    """A stair core of 5.0 x 3.0 m inside (15 m2) on three levels: the stair (3.3 x 3.0 m) on the left, the lift
    (1.7 x 3.0 m) on the right with no wall read between them; the lift's label 'Asansör' on ``lift_label_on``. The
    rooms of ``derive_rooms`` (the face unnamed: the lift's label gives it up) and the stairs as building pieces."""
    from wenart.ingest import rooms as R

    walls = _box_walls(0, 0, 5.2, 3.2)
    rooms, furniture = [], []
    for lid in levels:
        labels, points = _labels(("Asansör", (4.25, 1.6)),) if lid in lift_label_on else ([], [])
        res = R.derive_rooms(lid, walls, labels, points, None, "p.dxf", stairs=[_stair(1.75, 1.6)],
                             unlabelled_label="Oda", face_type=lambda poly: ("hall", "unlabelled face, the stair"))
        rooms += res.rooms
        furniture.append({"id": f"f_{lid}_stair", "type": "stair", "level_id": lid,
                          "footprint": {"center": [1.75, 1.6], "size": [3.3, 3.0], "rotation_deg": 0.0}})
    return rooms, furniture


def test_a_lift_label_set_aside_by_the_stair_core_names_its_own_part_after_the_core_split():
    from wenart.ingest import twins as TW

    rooms, furniture = _core_levels()
    l0 = next(r for r in rooms if r["level_id"] == "L0")
    assert l0["label"] == "Oda" and l0["sub_spaces"][0]["type"] == "lift"
    assert abs(l0["sub_spaces"][0]["anchor"][0] - 4.25) < 0.1 and abs(l0["sub_spaces"][0]["anchor"][1] - 1.6) < 0.1
    openings = [{"id": f"o_{lid}_in", "type": "opening", "level_id": lid, "center": [1.75, 0.1], "width": 1.0}
                for lid in ("L0", "L1", "L2")]                  # the stair's way in from the floor
    walls = []
    TW.stair_cores(rooms, furniture)
    notes = TW.split_core_landings(rooms, openings, furniture, walls)
    for lid in ("L0", "L1", "L2"):
        got = sorted((r["label"], r["room_type"]) for r in rooms if r["level_id"] == lid)
        assert got == [("Asansör", "shaft"), ("Merdiven", "stair")], (lid, got)
    lifts = [r for r in rooms if r["label"] == "Asansör"]
    assert all(r["label_inferred"]["method"] == "sub_space" and not r.get("sub_spaces") for r in lifts)
    assert any("stacks on the lift" in r["label_inferred"]["reason"] for r in lifts)        # L1, L2: no label there
    assert not any(r.get("sub_spaces") for r in rooms) and len(openings) == 3            # no open joint
    assert len(walls) == 3 and all(w["inferred"] and w["thickness"] == 0.1 for w in walls)  # the shaft wall
    assert all(abs(w["start"][0] - 3.4) < 1e-6 and abs(w["end"][0] - 3.4) < 1e-6 for w in walls)
    assert not any("Kat Holü" in n for n in notes)


def test_without_a_lift_the_core_landing_stays_the_shared_hall():
    from wenart.ingest import twins as TW

    rooms, furniture = _core_levels(lift_label_on=())
    openings = []
    TW.stair_cores(rooms, furniture)
    TW.split_core_landings(rooms, openings, furniture, [])
    assert sorted(r["label"] for r in rooms if r["level_id"] == "L0") == ["Kat Holü", "Merdiven"]
    assert len(openings) == 3


def test_an_unresolved_sub_space_is_an_rc14_finding_and_a_lift_carved_on_its_drawn_outline():
    from wenart.ingest import rooms as R
    from wenart.ingest import twins as TW
    from wenart.reading_check import sense as SE

    walls = _box_walls(0, 0, 4.2, 4.2)                     # a 14.4 m2 core: lift, stair and landing, no wall read
    labels, points = _labels(("Asansör", (1.0, 1.0)),)
    res = R.derive_rooms("L0", walls, labels, points, None, "p.dxf", stairs=[_stair(3.0, 2.5)],
                         unlabelled_label="Oda", face_type=lambda poly: ("hall", "unlabelled face holding the stair"))
    building = {"rooms": res.rooms, "levels": [{"id": "L0"}], "walls": [], "openings": [], "furniture": []}
    got = [f for f in SE.label_names_larger_face(building) if f.get("sub_space") == "Asansör"]
    assert got and got[0]["severity"] == "major" and abs(got[0]["place"][0] - 1.0) < 0.1 and "not built" in got[0]["message"]
    # the lift's shaft outline drawn as an untyped piece of a lift's size under the label: carved out as the lift
    piece = {"id": "f_L0_002", "type": "unknown", "level_id": "L0",
             "footprint": {"center": [1.0, 1.0], "size": [1.7, 1.7], "rotation_deg": 0.0}}
    new_walls = []
    notes = TW.carve_sub_spaces(res.rooms, [piece], new_walls)
    lift = next(r for r in res.rooms if r["label"] == "Asansör")
    assert lift["room_type"] == "shaft" and abs(lift["area_computed"] - 1.65 * 1.65) < 0.05
    rest = next(r for r in res.rooms if r is not lift)
    assert abs(rest["area_computed"] - (3.8 * 3.8 - 1.65 * 1.65)) < 0.05 and not rest.get("sub_spaces")
    assert piece["build"] is False and piece["details"]["not_furniture"]["room_id"] == lift["id"]
    assert len(new_walls) == 2 and notes                     # the shaft's two sides towards the landing
    assert not [f for f in SE.label_names_larger_face(building) if f.get("sub_space")]


def test_lift_lobbies_voids_and_stair_halls_keep_their_names_with_a_stair_in_them():
    from wenart import building as B
    from wenart.ingest import rooms as R
    from wenart.ingest.generic import labels as LB

    walls = _box_walls(0, 0, 5.4, 4.4)                     # 5.2 x 4.2 m = 21.8 m2 with the stair
    for name, rtype in (("Asansör Holü", "hall"), ("ASANSÖR ÖNÜ", "hall"), ("Lift Lobby", "hall"),
                        ("Asansör ve Merdiven Holü", "stair"), ("GALERİ", "shaft"), ("GALERİ BOŞLUĞU", "shaft"),
                        ("BOŞLUK", "shaft"), ("VOID", "shaft")):
        labels, points = _labels((name, (1.0, 1.0)),)
        res = R.derive_rooms("L0", walls, labels, points, None, "p.dxf", stairs=[_stair(3.5, 2.5)])
        assert [r["label_raw"] for r in res.rooms] == [name] and not res.sub_space_labels, name
        assert res.rooms[0]["room_type"] == rtype and LB.sub_space_type(name, B.room_type_for(name)) is None, name


def test_turkish_room_word_abbreviations_compounds_and_odasi_names():
    from wenart import building as B
    from wenart.ingest.generic import labels as LB

    assert B.room_type_for("Y.ODASI") == B.room_type_for("Y.odası") == "bedroom"
    assert B.room_type_for("Ç.ODASI") == "bedroom" and B.room_type_for("E.YAT.OD.") == "bedroom"
    assert B.room_type_for("SUDEPOSU") == B.room_type_for("SU DEPOSU") == "storage"
    assert B.room_type_for("YANGINMERDIVENI") == "stair" and B.room_type_for("SUTUN") == "other"
    assert B.room_type_for("SPOR ODASI") == "other" and B.room_type_for("YATAK ODASI") == "bedroom"
    assert B.room_type_for("ODA") == "bedroom" and B.generic_room_label("ODA")       # ODA alone stays generic
    blocks = LB.merge_label_blocks([_run("SPOR ODASI", 0.0, 0.0, k=1), _run("43.00 m²", 0.0, -0.35, k=2)], "p.dxf")
    assert [(b.name, b.area_m2) for b in blocks] == [("SPOR ODASI", 43.0)]


# --------------------------------------------------------------------------
# Review of 12 Nov 2026, item 6 (real18): a tile grid is no stair; a hall's own stair does not cut the hall
# --------------------------------------------------------------------------

def _line(a, b, k, layer="0"):
    from wenart.ingest.generic.model import Stroke

    return Stroke(id=f"LINE:{k}", kind="line", pts=[a, b], layer=layer)


def _stair_of(strokes):
    from wenart.ingest.generic import symbols as SY

    return SY.stair_rule(SY.Cluster(SY._segments(strokes, set())), 0.0)


def test_a_tile_grid_cut_by_text_gaps_is_no_stair_and_a_real_stair_stays_one():
    rows = [_line((0.0, 0.3 * k), (2.4, 0.3 * k), k) for k in range(9)]             # tile joints every 0.30 m
    cols = []
    for j in range(9):                                                               # the cross joints, cut by texts
        x = 0.3 * j
        spans = [(0.0, 0.9), (1.2, 2.4)] if j % 2 else [(0.0, 0.6), (1.5, 2.4)]
        cols += [_line((x, a), (x, b), 100 + 10 * j + n) for n, (a, b) in enumerate(spans)]
    assert _stair_of(rows + cols) is None
    # a stair: 8 treads, two stringers, the dividing line and an arrow line keep it a stair
    treads = [_line((1.0, 1.0 + 0.27 * k), (2.6, 1.0 + 0.27 * k), 300 + k) for k in range(8)]
    sides = [_line((1.0, 1.0), (1.0, 2.89), 400), _line((2.6, 1.0), (2.6, 2.89), 401),
             _line((1.8, 1.0), (1.8, 3.5), 402), _line((1.4, 1.1), (1.4, 2.8), 403)]
    st = _stair_of(treads + sides)
    assert st is not None and sum(f["lines"] for f in st["flights"]) >= 8
    from wenart.ingest.generic import symbols as SY
    assert SY._tile_grid([0.0, 0.3, 0.6, 1.2, 1.5], 0.3) and not SY._tile_grid([0.0, 0.4, 1.6], 0.27)
    assert not SY._tile_grid([0.0, 0.8, 1.6, 2.4, 3.2], 0.27)                      # far wider than the treads


def test_a_stair_separator_is_refused_when_the_halls_printed_area_holds_the_stair():
    from types import SimpleNamespace

    from shapely.geometry import box

    from wenart.ingest.generic import topology as TP

    before = [box(0, 0, 3.2, 2.0)]                                                  # 6.4 m2: the Antre with its stair
    after = [box(0, 0, 1.0, 2.0), box(1.0, 0, 3.2, 2.0)]
    antre = SimpleNamespace(name="ANTRE", anchor=(0.5, 1.0), area_m2=6.42)
    assert TP._area_text_holds(before, after, [antre]) == "ANTRE"
    no_area = SimpleNamespace(name="ANTRE", anchor=(0.5, 1.0), area_m2=None)
    assert TP._area_text_holds(before, after, [no_area]) is None
    small = SimpleNamespace(name="ANTRE", anchor=(0.5, 1.0), area_m2=2.0)          # the drawing says: without the stair
    assert TP._area_text_holds(before, after, [small]) is None


# --------------------------------------------------------------------------
# Review of 12 Nov 2026, items 7 and 8: area lines, field-name tags, schedule headers, KOTUNDA, negative cases
# --------------------------------------------------------------------------

def test_a_room_area_line_written_with_net_or_brut_keeps_the_rooms_area():
    from wenart.ingest.generic import labels as LB

    for line, area in (("NET 24.50 M2", 24.5), ("BRÜT 30.00 M2", 30.0), ("NET: 24,50 m²", 24.5)):
        blocks = LB.merge_label_blocks([_run("SALON", 0.0, 0.0, k=1), _run(line, 0.0, -0.35, k=2)], "p.dxf")
        assert [(b.name, b.area_m2) for b in blocks] == [("SALON", area)], line
    # a building summary line is no room's area; a lone summary word stays no label
    blocks = LB.merge_label_blocks([_run("SALON", 0.0, 0.0, k=1), _run("OTURUM 108 M2", 0.0, -0.35, k=2)], "p.dxf")
    assert [(b.name, b.area_m2) for b in blocks] == [("SALON", None)]
    assert LB.merge_label_blocks([_run("BRÜT", 0.0, 0.0, k=1), _run("253 M2", 0.0, -0.35, k=2)], "p.dxf") == []


def test_attdef_field_names_are_no_texts_and_special_codes_are_decoded(tmp_path):
    from wenart.ingest.dxf_generic import attdef_field_name as F

    doc = _doc()
    msp = doc.modelspace()
    for k, (tag, prompt, default) in enumerate((("MAHAL", "MAHAL-ADI", ""), ("BITMISKOT", "", ""),
                                                ("ASNAME", "", ""), ("ODA_ADI", "", ""), ("%%P0.00", "Kotu girin", "x"),
                                                ("SALON", "Mahal adi giriniz", ""), ("SUDEPOSU", "", ""))):
        a = msp.add_attdef(tag, (k * 5.0, 0.0), dxfattribs={"height": 0.25, "layer": "YAZI"})
        a.dxf.prompt = prompt
        a.dxf.text = default
    page = DG.read_page(_save(doc, tmp_path), "plan.dxf")
    assert sorted(t.text for t in page.texts) == ["SALON", "SUDEPOSU", "±0.00"]
    assert F("KOT", "Kotu girin") and F("ÇİZİMADI") and not F("+2.00", "Kotu girin") and not F("10000", "MAHAL-NO")
    assert not F("OTOPARK") and not F("A:102.52M2") and not F("Y.odası") and not F("YATAK_ODASI")


def _headed_schedule(header_h=0.2, title=None, cols=1):
    runs = [_run("MAHAL ADI", 50.0, 10.5, h=header_h, k=899)] if header_h else []
    if title:
        runs.append(_run(title, 50.0 + 4.5, 11.0, h=0.2, k=898))             # centred over four columns
    for k, name in enumerate(SCHEDULE):
        runs.append(_run(name, 50.0, 10.0 - 0.5 * k, k=k + 100))
        for c in range(1, cols):
            runs.append(_run("PARKE", 50.0 + 3.0 * c, 10.0 - 0.5 * k, k=k + 200 + 20 * c))
    return runs


def test_a_header_cell_of_the_entries_height_or_a_centred_title_heads_a_schedule():
    from shapely.geometry import box

    from wenart.ingest.generic import labels as LB

    for kw in ({}, {"hull": box(40, 0, 60, 20)}):                    # no walls known; a hull covering the list
        found = LB.schedules(_headed_schedule(), **kw)
        assert len(found) == 1 and found[0]["header"] == "MAHAL ADI", kw
        assert found[0]["run_ids"].count("TEXT:899") == 1
        found = LB.schedules(_headed_schedule(header_h=0, title="MAHAL LİSTESİ", cols=4), **kw)
        assert len(found) == 1 and found[0]["header"] == "MAHAL LİSTESİ", kw
    # the same rooms without a header inside the walls stay labels
    assert LB.schedules(_headed_schedule(header_h=0), hull=box(40, 0, 60, 20)) == []


def test_inflected_level_mark_words_are_notation_and_floor_names_inside_the_walls_are_rooms():
    from shapely.geometry import box

    from wenart.ingest.generic import labels as LB

    assert LB.split_notation("-0.50 KOTUNDA TERAS")[0] == "TERAS" and LB.split_notation("TERAS KOTUNDA")[0] == "TERAS"
    assert LB.split_notation("KOTA")[0] == "KOTA"
    runs = [_run("LOFT", 5.0, 5.0, k=1), _run("24.50 m²", 5.0, 4.65, k=2)]
    assert LB.merge_label_blocks(runs, "p.dxf") == []                    # no walls known: a floor's name
    inside = LB.merge_label_blocks(runs, "p.dxf", hull=box(0, 0, 10, 10))
    assert [(b.name, b.area_m2) for b in inside] == [("LOFT", 24.5)]
    outside = LB.merge_label_blocks([_run("NORMAL", 50.0, 5.0, k=1), _run("253 M2", 50.0, 4.65, k=2)], "p.dxf",
                                    hull=box(0, 0, 10, 10))
    assert outside == []


def test_finish_word_rooms_stay_labels_and_field_like_names_give_no_label():
    from wenart.ingest.generic import labels as LB

    for name in ("PARKE DEPOSU", "ÇALIŞMA ALANI"):
        blocks = LB.merge_label_blocks([_run(name, 0.0, 0.0, k=1)], "p.dxf")
        assert [b.name for b in blocks] == [name], name
    for name in ("ODA_ADI", "ROOM_NAME", "NAME"):
        assert LB.merge_label_blocks([_run(name, 0.0, 0.0, k=1)], "p.dxf") == [], name


# --------------------------------------------------------------------------
# Review of 12 Nov 2026, item 4 (real15 F1, F2): a solid wall is no gap, a door block in a gap is a door
# --------------------------------------------------------------------------

def _gap(center, width, note="unclassified gap content: X"):
    from wenart.ingest.model import OpeningItem

    return OpeningItem("opening", width, center, 90.0, [0, 0, 0, 0], "gap:LINE:1,LINE:2",
                       {"method": "derived", "note": note}, status="unverified", type_raw="unclassified gap content")


def _ex2():
    from wenart.ingest.model import LevelExtraction

    ex = LevelExtraction(file="p.dxf", page=1, level_id="L0", units="dxf", page_size=[10.0, 10.0])
    ex.report = {}
    return ex


def test_a_gap_whose_wall_face_lines_run_through_it_is_a_wall():
    from wenart.ingest.generic import core as GC

    wall = _wall((5.5, 0.0), (5.5, 4.0), t=0.15, entity="w1")              # the wall run through the gap
    gap = _gap((5.5, 2.0), 2.0)
    faces = [_line((5.425, 0.0), (5.425, 4.0), 1, layer="Z_sıva"), _line((5.575, 4.0), (5.575, 0.0), 2, layer="Z_sıva")]
    ex = _ex2()
    walls, openings = GC._faces_through_gaps(ex, "p", [wall], [gap], faces)
    assert openings == [] and len(walls) == 1                 # the run already spans the gap: no second piece
    lab = walls[0].corrected_by_ai
    assert lab["rule"] == "faces_through_gap" and lab["before"]["width"] == 2.0 and len(lab["evidence"]) == 2
    assert "a wall, not an opening" in ex.notes[-1]
    # one face broken at the gap (a real opening), or the lines on a furniture layer: the gap stays
    broken = [faces[0], _line((5.575, 0.0), (5.575, 1.0), 3, layer="Z_sıva"), _line((5.575, 3.0), (5.575, 4.0), 4,
                                                                                   layer="Z_sıva")]
    assert GC._faces_through_gaps(_ex2(), "p", [wall], [gap], broken)[1] == [gap]
    furn = [_line(a.pts[0], a.pts[1], 10 + k, layer="Z_tefriş") for k, a in enumerate(faces)]
    assert GC._faces_through_gaps(_ex2(), "p", [wall], [gap], furn)[1] == [gap]


def _arc(sid, center, r, a0, a1, layer="KAPI", block=None):
    from wenart.ingest.generic.model import Stroke

    import math
    pts = [(center[0] + r * math.cos(math.radians(a)), center[1] + r * math.sin(math.radians(a))) for a in (a0, a1)]
    return Stroke(id=sid, kind="arc", pts=pts, layer=layer, block=block,
                  arc={"center": center, "radius": r, "start_deg": a0, "end_deg": a1})


def test_a_door_leafs_swing_in_an_unclassified_gap_makes_a_door_on_the_leafs_chord():
    from wenart.ingest.generic import core as GC

    wall = _wall((0.0, 3.0), (6.0, 3.0), t=0.25, entity="w1")
    gap = _gap((3.0, 3.0), 1.32)
    gap.rotation_deg = 0.0
    ex = _ex2()
    got = GC._door_blocks_in_gaps(ex, "p", [wall], [gap], [_arc("INSERT:9/23", (2.4, 3.0), 0.7, 270.0, 360.0)])
    assert [o.kind for o in got] == ["door", "opening"] and abs(got[0].width - 0.7) < 1e-6
    assert abs(got[0].center[0] - 2.75) < 1e-6 and got[0].status == "verified"        # on the leaf, not the gap centre
    assert got[0].operation == "swing"
    # the rest of the gap is read again from its lines (openings.doors_in_gaps): nothing drawn there, an open rest
    assert abs(got[1].width - 0.56) < 1e-3 and got[1].evidence.get("rest_of")
    assert "chord" in ex.notes[-1] and "rest of the gap read again" in ex.notes[-1]
    # a basin's arc, or a swing hinged off the wall, is no door
    basin = _arc("ARC:5", (2.4, 3.0), 0.7, 270.0, 360.0, layer="Z_tefriş")
    assert GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap], [basin])[0].kind == "opening"
    far = _arc("INSERT:9/24", (2.4, 1.5), 0.7, 270.0, 360.0)
    assert GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap], [far])[0].kind == "opening"


def test_borrowed_swings_sashes_tags_and_doors_already_read_make_no_new_door():
    from wenart.ingest.generic import core as GC
    from wenart.ingest.model import OpeningItem

    wall = _wall((0.0, 3.0), (8.0, 3.0), t=0.25, entity="w1")

    def gap(cx, w):
        g = _gap((cx, 3.0), w)
        g.rotation_deg = 0.0
        return g

    # the neighbour's swing hinged 0.08 m past the gap's end, its leaf away from the gap (real21)
    neighbour = _arc("LW:1", (4.08, 3.0), 0.84, 0.0, 90.0)
    assert GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap(2.865, 2.27)], [neighbour])[0].kind == "opening"
    # one arc between two gaps serves one of them at most
    arc = _arc("A:1", (4.0, 3.0), 0.7, 180.0, 270.0)
    got = GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap(3.5, 1.2), gap(4.6, 1.2)], [arc])
    assert sum(1 for o in got if o.kind == "door") <= 1
    # a casement sash of 0.52 m sweeping 35 degrees on a door-and-window layer is a window's
    sash = _arc("ARC:735", (2.0, 3.0), 0.52, 0.0, 35.0, layer="kapı-pencere")
    assert GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap(2.5, 1.5)], [sash])[0].kind == "opening"
    # a window size tag beside the gap keeps it a window's
    tag = _run("P:150/150", 2.5, 3.6, k=7)
    hinge = _arc("A:2", (1.8, 3.0), 0.8, 270.0, 360.0)
    assert GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap(2.5, 1.5)], [hinge], texts_m=[tag])[0].kind == "opening"
    # ... but the tag of the window beside it speaks for that window only (real15's kitchen door)
    window = OpeningItem("window", 1.5, (4.2, 3.0), 0.0, [0, 0, 0, 0], "win", {})
    near_window = _run("P:150/150", 3.5, 3.6, k=8)                 # 1.17 m from the gap's centre, nearer the window
    got = GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap(2.5, 1.5), window], [hinge], texts_m=[near_window])
    assert [o.kind for o in got] == ["door", "opening", "window"]           # the door, its gap's open rest, the window
    # an arc an opening already owns is not borrowed; a door already read in the gap is its opening
    assert GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap(2.5, 1.5)], [hinge], owned={"A:2"})[0].kind == "opening"
    door = OpeningItem("door", 0.9, (2.2, 3.0), 0.0, [0, 0, 0, 0], "d", {})
    got = GC._door_blocks_in_gaps(_ex2(), "p", [wall], [door, gap(2.4, 1.3)], [hinge])
    assert [o.kind for o in got] == ["door", "opening"]             # the gap stays as it is, no second door
    got = GC._door_blocks_in_gaps(_ex2(), "p", [wall], [door, gap(3.2, 2.8)], [hinge])
    assert [o.kind for o in got] == ["door", "opening"]            # a wider gap stays as read


def test_two_leaves_meeting_in_a_gap_make_one_double_door():
    from wenart.ingest.generic import core as GC

    wall = _wall((0.0, 3.0), (6.0, 3.0), t=0.25, entity="w1")
    g = _gap((3.0, 3.0), 1.25)
    g.rotation_deg = 0.0
    leaves = [_arc("A:1", (2.4, 3.0), 0.6, 270.0, 360.0), _arc("A:2", (3.6, 3.0), 0.6, 180.0, 270.0)]
    got = GC._door_blocks_in_gaps(_ex2(), "p", [wall], [g], leaves)
    assert len(got) == 1 and got[0].kind == "door" and abs(got[0].width - 1.2) < 1e-6
    assert got[0].operation == "double"


def test_a_door_block_or_lone_fixtures_never_make_a_window_onto_an_open_recess():
    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic.model import Stroke

    door = _gap((3.0, 3.0), 1.3, note="unclassified gap content: INSERT:9/1,INSERT:9/2")
    by_id = {"INSERT:9/1": Stroke(id="INSERT:9/1", kind="line", pts=[(2.5, 3.0), (2.5, 2.4)], layer="KAPI",
                                  block="wererte"),
             "INSERT:9/2": Stroke(id="INSERT:9/2", kind="line", pts=[(2.6, 3.0), (2.6, 2.4)], layer="0")}
    assert GC._gap_fixture(door, by_id).startswith("a door piece")
    sink = _gap((3.0, 3.0), 1.3, note="unclassified gap content: ARC:7")
    assert GC._gap_fixture(sink, {}).startswith("an arc")
    lines = _gap((3.0, 3.0), 1.3, note="unclassified gap content: LINE:8,LINE:9")
    assert GC._gap_fixture(lines, {"LINE:8": Stroke(id="LINE:8", kind="line", pts=[(0, 0), (1, 0)], layer="PENCERE")}) \
        is None
    # real10: a counter's edge beside the window's frame lines keeps the window; the counter alone is a fixture
    both = {"LINE:8": Stroke(id="LINE:8", kind="line", pts=[(0, 0), (1, 0)], layer="PENCERE"),
            "LINE:9": Stroke(id="LINE:9", kind="line", pts=[(0, 0.1), (1, 0.1)], layer="TEFRİŞ")}
    assert GC._gap_fixture(lines, both) is None
    assert GC._gap_fixture(lines, {"LINE:9": both["LINE:9"]}).startswith("a furniture piece")


def test_many_flights_in_a_small_footprint_are_a_tile_grid_for_the_reader_and_the_checker():
    from wenart.ingest.generic import symbols as SY
    from wenart.reading_check import sense as SE

    treads = [_line((0.0, 0.27 * k), (2.0, 0.27 * k), 500 + k) for k in range(8)]
    cuts = [_line((x, -0.05), (x, 2.0), 600 + j) for j, x in enumerate(
        (0.07, 0.15, 0.26, 0.31, 0.43, 0.5, 0.62, 0.71, 0.85, 0.93, 1.05, 1.12, 1.26, 1.33, 1.47, 1.55, 1.68, 1.75, 1.88, 1.95))]
    assert _stair_of(treads + cuts) is None                       # strips of tiles, no walkable flight: no stair
    assert SE.GRID_FLIGHTS_MIN is SY.GRID_FLIGHTS_MIN and SE.FLIGHT_MIN_AREA_M2 is SY.FLIGHT_MIN_AREA_M2
    wide = [_line((0.0, 0.27 * k), (2.4, 0.27 * k), 700 + k) for k in range(12)]
    assert _stair_of(wide + [_line((1.2, -0.05), (1.2, 3.5), 800)]) is not None   # a U stair: 2 flights in 8 m2


# --------------------------------------------------------------------------
# Review of 12 Nov 2026, round 3: level elevations from floor marks
# --------------------------------------------------------------------------

def _stack(n=4, start=0):
    """A building of levels L{start}..L{start+n-1} (orders, assumed 3 m apart), each with the fixture's two rooms."""
    import copy

    from tests import _levels_fixture as F

    b = F.building()
    base_lv, base_rooms = b["levels"][0], b["rooms"]
    b["levels"], b["rooms"] = [], []
    for k in range(start, start + n):
        lid = f"L{k}"
        b["levels"].append(dict(copy.deepcopy(base_lv), id=lid, order=k, elevation=3.0 * k,
                                elevation_source="assumed_default", label=f"{k}. Kat"))
        for r in base_rooms:
            b["rooms"].append(dict(copy.deepcopy(r), id=f"{r['id']}_{lid}", level_id=lid))
    return b


def _marks(b, values: dict, kind="floor"):
    from tests import _levels_fixture as F

    out = []
    for lid, vals in values.items():
        for k, v in enumerate(vals if isinstance(vals, (list, tuple)) else [vals]):
            out.append(F.mark(f"lm_{lid}_{k}", v, kind=kind, point=(3.0, 4.0), room_id=f"r_living_{lid}", level=lid))
    b["level_marks"] = (b.get("level_marks") or []) + out
    return b


def _elev(b):
    from wenart.levels import model as M

    n = M.infer_levels(b)
    return {lv["id"]: lv["elevation"] for lv in n["levels"]}, n


def test_a_wrong_top_mark_is_refused_and_the_right_marks_below_it_are_kept():
    got, n = _elev(_marks(_stack(), {"L1": [3.2, 3.2], "L2": [6.4, 6.4], "L3": [0.0, 0.0]}))
    assert got == {"L0": 0.0, "L1": 3.2, "L2": 6.4, "L3": 9.4}            # L3 follows L2's move, its '0.00' refused
    assert any("level L3" in w and "out of the storeys' order" in w for w in n["level_inference"]["warnings"])


def test_a_tall_ground_storey_moves_the_assumed_levels_above_it_and_a_7_m_storey_is_refused():
    got, _n = _elev(_marks(_stack(3), {"L1": [4.5, 4.5]}))
    assert got == {"L0": 0.0, "L1": 4.5, "L2": 7.5}                       # L2 assumed: it follows L1
    got, n = _elev(_marks(_stack(5), {"L4": [16.0, 16.0, 16.0]}))       # real13: a roof mark over an assumed L3
    assert got["L4"] == 12.0 and got["L3"] == 9.0
    assert any("level L4" in w and "out of the storeys' order" in w for w in n["level_inference"]["warnings"])


def test_the_plans_height_frame_comes_from_the_ground_floors_own_marks():
    from tests import _levels_fixture as F

    b = _stack(3, start=-1)                                              # L-1, L0, L1
    b["rooms"].append(dict(b["rooms"][1], id="r_stair_L0", room_type="stair", level_id="L0"))
    b["level_marks"] = [F.mark("lm_a", 2.5, kind="floor", point=(8.0, 4.0), room_id="r_stair_L0", level="L0"),
                        F.mark("lm_b", 2.5, kind="threshold", point=(8.0, 0.0), level="L0"),
                        F.mark("lm_c", -0.5, kind="floor", point=(3.0, 4.0), room_id="r_living_L-1", level="L-1"),
                        F.mark("lm_d", -0.5, kind="ground", point=(3.0, -2.0), level="L-1")]
    got, n = _elev(b)
    assert got == {"L-1": -3.0, "L0": 0.0, "L1": 3.0}
    marks = {m["id"]: m for m in n["level_marks"]}
    assert marks["lm_d"]["z"] == -3.0 and marks["lm_c"]["frame_shift"] == 2.5
    assert any(i["item"] == "plan height frame" for i in n["level_inference"]["inferred"])


def test_a_variants_slab_stays_with_its_alternative_and_a_moved_slab_carries_its_evidence():
    b = _marks(_stack(2), {"L1": [3.5, 3.5]})
    b["slabs"] = [{"id": "sl_L1", "below_level_id": "L0", "above_level_id": "L1", "z_top": 3.0, "variants": [],
                   "evidence": []},
                  {"id": "sl_L1__v1b", "below_level_id": "L0", "above_level_id": "L1", "z_top": 3.0,
                   "variants": ["l1b-v1b"], "evidence": []}]
    _got, n = _elev(b)
    sl = {s["id"]: s for s in n["slabs"]}
    assert sl["sl_L1"]["z_top"] == 3.5 and sl["sl_L1"]["z_top_before"] == 3.0
    assert sl["sl_L1"]["evidence"][-1]["rule"] == "level_elevation" and sl["sl_L1"]["evidence"][-1]["method"] == "inferred"
    assert sl["sl_L1__v1b"]["z_top"] == 3.0                               # the alternative's slab did not move


def test_technical_odasi_rooms_wc_odasi_and_one_letter_abbreviations_need_evidence():
    from wenart import building as B
    from wenart.furniture import program as PR

    assert B.room_type_for("ELK. PANO ODASI", 6.8, 1.3) == "technical" and B.room_type_for("TRAFO ODASI") == "technical"
    # 19 Nov 2026 (review A3, A3FC-4: real11's 'ELEKTR.ODASI'): abbreviated plant words, ODA and DAIRESI too
    for label in ("ELEKTR.ODASI", "ELEK. ODASI", "SAYAÇ ODASI", "TEKNİK ODA", "MAKİNE DAİRESİ", "AS.MAK.DAIRESI"):
        assert B.room_type_for(label) == "technical", label
    assert B.room_type_for("MAKYAJ ODASI") != "technical" and B.room_type_for("ELEKTRIK") != "technical"
    assert "technical" in PR.NOT_FURNISHED                     # a plant room is never furnished
    assert B.room_type_for("W.C. ODASI") == "wc" and B.room_type_for("W.C.ODASI") == "wc"
    assert B.room_type_for("Y.ODASI", 9.0, 1.2) == "bedroom" and B.room_type_for("Y.ODASI", 4.0, 1.2) == "other"
    assert B.room_type_for("YATAK ODASI", 4.0, 1.2) == "bedroom"   # the written word needs no evidence
    # a label named only by the generic '<word> ODASI' names its room but does not vote for the wall layers
    assert B.generic_odasi_only("SPOR ODASI") and not B.generic_odasi_only("YATAK ODASI")
    # nor does a plant room named by its plant-room word alone (the basement keeps the document's wall layers)
    assert B.generic_odasi_only("ELK. PANO ODASI") and B.generic_odasi_only("TRAFO ODASI")
    assert not B.generic_odasi_only("KAZAN DAIRESI DEPO") and not B.generic_odasi_only("WC")



def test_a_core_part_holding_the_landing_stays_the_hall_and_the_lift_is_carved_on_its_outline():
    from wenart.ingest import twins as TW

    rooms, furniture = _core_levels()
    # the right-hand part (1.7 x 3.0 m) holds the lift label and both flats' doors: it is the landing, not the lift
    openings = []
    for lid in ("L0", "L1", "L2"):
        openings += [{"id": f"o_{lid}_in", "type": "opening", "level_id": lid, "center": [1.75, 0.1], "width": 1.0},
                     {"id": f"d_{lid}_a", "type": "door", "level_id": lid, "center": [5.1, 0.8], "width": 0.9},
                     {"id": f"d_{lid}_b", "type": "door", "level_id": lid, "center": [5.1, 2.4], "width": 0.9}]
    TW.stair_cores(rooms, furniture)
    TW.split_core_landings(rooms, openings, furniture, [])
    l0 = sorted(r["label"] for r in rooms if r["level_id"] == "L0")
    assert l0 == ["Kat Holü", "Merdiven"]
    hall = next(r for r in rooms if r["level_id"] == "L0" and r["label"] == "Kat Holü")
    assert hall["sub_spaces"][0]["type"] == "lift"              # the label goes with the hall part, still pending
    piece = {"id": "f_L0_9", "type": "unknown", "level_id": "L0",
             "footprint": {"center": [4.25, 2.3], "size": [1.6, 1.4], "rotation_deg": 0.0}}
    TW.carve_sub_spaces(rooms, [piece], [])
    assert sorted(r["label"] for r in rooms if r["level_id"] == "L0") == ["Asansör", "Kat Holü", "Merdiven"]


def test_a_free_standing_shaft_is_cut_out_of_its_room_with_no_overlap():
    from shapely.geometry import Polygon

    from wenart.ingest import rooms as R
    from wenart.ingest import twins as TW

    walls = _box_walls(0, 0, 5.4, 4.4)                         # 5.0 x 4.0 m inside
    labels, points = _labels(("Asansör", (2.6, 2.2)),)
    res = R.derive_rooms("L0", walls, labels, points, None, "p.dxf", stairs=[_stair(4.5, 1.0)],
                         unlabelled_label="Oda", face_type=lambda poly: ("hall", "unlabelled face holding the stair"))
    piece = {"id": "f_L0_2", "type": "unknown", "level_id": "L0",
             "footprint": {"center": [2.6, 2.2], "size": [1.7, 1.7], "rotation_deg": 0.0}}
    TW.carve_sub_spaces(res.rooms, [piece], [])
    host = next(r for r in res.rooms if r["label"] != "Asansör")
    lift = next(r for r in res.rooms if r["label"] == "Asansör")
    hp, lp = Polygon(host["polygon"]), Polygon(lift["polygon"])
    assert abs(hp.area - host["area_computed"]) < 0.02 and hp.intersection(lp).area < 0.01



def test_rails_walk_lines_and_a_two_line_well_keep_a_drawn_stair():
    # a straight flight, 18 treads 1.2 m wide, with rail lines 5 cm inside each side (single, then double lines)
    treads = [_line((0.0, 0.28 * k), (1.2, 0.28 * k), 900 + k) for k in range(18)]
    end = 0.28 * 17
    sides = [_line((0.0, 0.0), (0.0, end), 950), _line((1.2, 0.0), (1.2, end), 951)]
    single = [_line((x, -0.02), (x, end + 0.02), 960 + j) for j, x in enumerate((0.05, 1.15))]
    double = single + [_line((x, -0.02), (x, end + 0.02), 970 + j) for j, x in enumerate((0.1, 1.1))]
    for rails in (single, double):
        st = _stair_of(treads + sides + rails)
        assert st is not None and max(f["width"] for f in st["flights"]) >= 1.0
    # a walk line and one rail
    st = _stair_of(treads + sides + [_line((0.6, -0.02), (0.6, end + 0.02), 980), single[0]])
    assert st is not None and all(f["width"] >= 0.5 for f in st["flights"])
    # a compact U stair: two 1.0 m flights either side of a 0.3 m well drawn as two lines
    u = [_line((0.0, 0.28 * k), (2.3, 0.28 * k), 1000 + k) for k in range(10)]
    well = [_line((x, -0.02), (x, 0.28 * 9 + 0.02), 1100 + j) for j, x in enumerate((1.0, 1.3))]
    st = _stair_of(u + well)
    assert st is not None and sorted(round(f["width"], 2) for f in st["flights"]) == [1.0, 1.0]


def test_a_hall_mosaic_grid_broken_around_its_label_is_no_stair():
    lines, k = [], 2000
    pitch = 0.21875
    for i in range(int(3.0 / pitch) + 1):                       # 300 x 180 cm, lines broken around a label block
        x = i * pitch
        spans = [(0.0, 0.6), (1.2, 1.8)] if 1.0 < x < 2.0 else [(0.0, 1.8)]
        for a, b in spans:
            lines.append(_line((x, a), (x, b), k))
            k += 1
    for j in range(int(1.8 / pitch) + 1):
        y = j * pitch
        spans = [(0.0, 1.0), (2.0, 3.0)] if 0.6 < y < 1.2 else [(0.0, 3.0)]
        for a, b in spans:
            lines.append(_line((a, y), (b, y), k))
            k += 1
    assert _stair_of(lines) is None


def test_room_word_tags_vent_sizes_and_room_like_floor_words():
    from wenart.ingest.dxf_generic import attdef_field_name as F
    from wenart.ingest.generic import core as GC
    from wenart.reading_check import sense as SE

    assert F("SALON", "SALON") is None and F("WC", "WC") is None and F("BANYO", "Banyo adini girin") is None
    assert F("MAHAL", "MAHAL-ADI") and F("KOT", "Kotu girin")               # field names still skipped
    assert GC.DOOR_TAG_LOW_H_CM == 180                                       # '75/45' or '50/50' is no door size
    assert SE.notation_in("LOFT") == [] and SE.notation_in("Attic") == [] and SE.notation_in("Normal")


def test_one_garage_door_predicate_a_drive_path_as_wide_as_the_drive_and_no_override_on_a_drive():
    from wenart.blender import site as S
    from wenart.levels import edits as ED
    from wenart.levels import model as M

    b2 = _garage_building(width=2.1)                                 # under the reader's 2.2 m: a person's door
    assert _ent_solution(b2) == "steps"
    b = M.infer_levels(_garage_building())
    e = next(x for x in b["site"]["entrances"] if x["door_id"] == "d_front")
    try:
        ED._set_entrance(b, {"door_id": "d_front", "solution": "steps", "reason": "x"}, {})
        raise AssertionError("a drive took an override")
    except ED.Rejected as exc:
        assert "garage door" in str(exc)
    ent = {"opening_id": "d_front", "centre": [8.0, 0.0], "outward": [0.0, -1.0], "half_t": 0.1, "width": 2.5,
           "bottom": 0.0, "ground_z": -0.5, "rise": 0.5, "record": e}
    st = S.entrance_steps(ent)
    assert st["drive_rise"] == 0.5 and "a drive" in st["reason"]
    paths = S.entrance_paths([ent], {"d_front": st}, [(-5, -20), (20, -20), (20, 20), (-5, 20)])
    assert paths and paths[0]["width"] >= 3.0 and paths[0].get("kind") == "drive"
    # a flush sectional door into a storage room is kept level, never a step up
    flush = dict(ent, rise=0.0, ground_z=0.0, record=dict(e, solution="none", ramp=None, room_id="r_hall"))
    bb = _garage_building(width=2.5, rtype="storage", label="Depo")
    bb["openings"][0]["door_type"] = "garage_sectional"
    assert S.entrance_threshold(flush, bb)["kind"] == "keep"


def test_every_small_label_of_a_face_is_its_own_sub_space_whatever_the_reading_order():
    from wenart.ingest import rooms as R

    walls = _box_walls(0, 0, 4.2, 4.2)                     # 14.4 m2 holding a stair
    for items in ((("Merdiven Holü", (2.5, 3.6)), ("Asansör", (1.0, 1.0))),
                  (("Asansör", (1.0, 1.0)), ("Merdiven Holü", (2.5, 3.6)))):
        labels, points = _labels(*items)
        res = R.derive_rooms("L0", walls, labels, points, None, "p.dxf", stairs=[_stair(2.5, 2.5)])
        assert [r["label"] for r in res.rooms] == ["Merdiven Holü"]
        assert [s["label"] for s in res.rooms[0]["sub_spaces"]] == ["Asansör"]
    labels, points = _labels(("Asansör", (1.0, 1.0)), ("Asansör", (3.2, 1.0)), ("WC", (1.0, 3.2)))
    res = R.derive_rooms("L0", walls, labels, points, None, "p.dxf", stairs=[_stair(2.5, 2.5)],
                         unlabelled_label="Oda", face_type=lambda poly: ("hall", "unlabelled"))
    subs = res.rooms[0]["sub_spaces"]
    assert sorted(s["type"] for s in subs) == ["lift", "lift", "wc"] and len(res.sub_space_labels) == 3
    assert sum("names only its own sub-space" in w for w in res.warnings) == 3



def test_the_regression_compares_heights_datum_slabs_and_entrances_when_the_baseline_has_them():
    from wenart.reading_check import regress as RG

    base = {"levels": ["L0", "L4"], "heights": {"L4": {"elevation": 12.0, "source": "assumed_default"}}, "datum": 3.7,
            "slabs": {"sl_L4": 12.0}, "entrances": {"d1": "steps"}}
    new = {"levels": ["L0", "L4"], "heights": {"L4": {"elevation": 16.0, "source": "level_mark"}}, "datum": None,
           "slabs": {"sl_L4": 16.0}, "entrances": {"d1": "drive"}}
    got = RG.compare(base, new)
    assert any(d.startswith("L4 elevation") for d in got) and "datum: 3.7 -> None" in got
    assert any(d.startswith("slab sl_L4") for d in got) and "entrance d1: steps -> drive" in got
    assert not [d for d in RG.compare({"levels": ["L0", "L4"]}, new) if "elevation" in d]   # old baselines: not compared
    assert RG.notes({"levels": []}, {"levels": ["L0"]})[0].startswith("the baseline holds no level")


class _St:
    def __init__(self, sid, pts, layer="MB", closed=False):
        self.id, self.pts, self.layer, self.closed, self.arc, self.source = sid, pts, layer, closed, None, "vector"


def _ramp_symbol(ax=7.86, ay=-0.1, length=2.8, width=3.7, sides=True, base=True):
    x0, x1, yf = ax - width / 2.0, ax + width / 2.0, ay - length
    st = [_St("ent:D1", [(x0, yf), (ax, ay)]), _St("ent:D2", [(x1, yf), (ax, ay)])]
    if base:
        st.append(_St("ent:B", [(x0, yf), (x1, yf)]))
    if sides:
        st += [_St("ent:S1", [(x0, yf), (x0, ay)]), _St("ent:S2", [(x1, ay), (x1, yf)])]
    return st


def test_a_drawn_ramp_symbol_in_front_of_a_garage_door_gives_the_drive_its_size_and_place():
    from shapely.geometry import box

    from wenart.blender import site as S
    from wenart.levels import checks as LC
    from wenart.levels import model as M
    from wenart.levels import read as RD

    house = box(0.0, -0.1, 16.0, 10.0)
    got = RD.ramp_outlines(_ramp_symbol(), house)
    assert len(got) == 1 and got[0]["length"] == 2.8 and got[0]["width"] == 3.7 and got[0]["apex"] == [7.86, -0.1]
    assert got[0]["entities"] == ["ent:B", "ent:D1", "ent:D2", "ent:S1", "ent:S2"]
    # the same symbol drawn as one closed outline and two diagonals is read too
    x0, x1 = 7.86 - 1.85, 7.86 + 1.85
    closed = [_St("ent:R", [(x0, -0.1), (x0, -2.9), (x1, -2.9), (x1, -0.1)], closed=True)] + _ramp_symbol()[:2]
    assert [r["length"] for r in RD.ramp_outlines(closed, house)] == [2.8]
    # no side lines (a gable or an arrow head), no far edge, or the symbol inside the building: no ramp
    assert RD.ramp_outlines(_ramp_symbol(sides=False), house) == []
    assert RD.ramp_outlines(_ramp_symbol(base=False), house) == []
    assert RD.ramp_outlines(_ramp_symbol(ay=5.0), house) == []
    # the levels: the door's drive takes the drawn outline (length, width, place across the door, its own slope)
    b = _garage_building()
    b["site"] = {"boundary_walls": [], "areas": [], "decor": [], "openings": []}
    b["site"]["drawn_ramps"] = RD.drawn_ramps([], b, M.level_params(M._brief_of(b, None)),
                                              [dict(got[0], level_id="L0", file="p.dxf")])
    assert [r["door_id"] for r in b["site"]["drawn_ramps"]] == ["d_front"]
    out = M.infer_levels(b)
    e = next(x for x in out["site"]["entrances"] if x["door_id"] == "d_front")
    assert e["solution"] == "drive" and e["drawn"] is True and e["ramp"]["drawn"] is True
    assert e["ramp"]["length"] == 2.8 and e["ramp"]["width"] == 3.7 and e["ramp"]["shift"] == -0.14
    assert e["ramp"]["slope"] == pytest.approx(0.5 / 2.8, abs=1e-3) and "drawn ramp" in e["reason"]
    assert any("ent:D1" in (ev.get("entity") or "") for ev in e["evidence"])
    found = [v for v in LC.check_levels(out) if v.get("target") == "d_front" and v["check"] == "L5"]
    assert found and all(v["severity"] == "minor" and "as drawn" in v["message"] for v in found)
    ent = {"opening_id": "d_front", "centre": [8.0, 0.0], "outward": [0.0, -1.0], "half_t": 0.1, "width": 2.5,
           "bottom": 0.0, "ground_z": -0.5, "rise": 0.5, "record": e}
    st = S.entrance_steps(ent)
    xs = sorted({round(p[0], 3) for p in st["ramp"]["polygon"]})
    ys = sorted({round(p[1], 3) for p in st["ramp"]["polygon"]})
    assert xs == [6.01, 9.71] and ys == [-2.9, -0.1] and "(drawn)" in st["reason"]
    # a symbol beside the door (its apex off the door's width) is not that door's ramp
    far = RD.ramp_outlines(_ramp_symbol(ax=12.0), house)
    assert far and RD.drawn_ramps([], b, M.level_params(M._brief_of(b, None)),
                                  [dict(far[0], level_id="L0", file="p.dxf")]) == []


def test_a_drive_is_paved_as_the_drive_and_steps_stay_in_the_steps_stone():
    from wenart.blender import site as S

    drive = {"solution": "drive", "ramp": {"drive": True}}
    assert S.step_floor_use(drive, {"kind": "site_ramp"}) == "drive"
    assert S.step_floor_use({"solution": "steps_and_ramp", "ramp": {"slope": 0.06}}, {"kind": "site_ramp"}) == "steps"
    assert S.step_floor_use(drive, {"kind": "site_step"}) == "steps"


def test_a_gap_on_a_wall_read_inside_the_band_of_the_wall_with_the_window_leaves_a_light_well_a_light_well():
    from shapely.geometry import box

    from wenart.ingest.generic import topology as TP
    from wenart.ingest.model import OpeningItem, WallItem

    def wall(x, y0, y1, t):
        return WallItem(start=(x, y0), end=(x, y1), thickness=t, box=[0, 0, 0, 0], entity="ent:W", evidence={})

    def gap(kind, x, y, width):
        return OpeningItem(kind=kind, width=width, center=(x, y), rotation_deg=90.0, box=[0, 0, 0, 0], entity="ent:O",
                           evidence={})

    walls = [wall(0.0, -2.0, 4.0, 0.26), wall(0.021, 0.5, 2.0, 0.24)]       # one wall, read twice in its band
    well, room = box(0.141, 0.6, 0.8, 1.6), box(-3.0, -2.0, -0.13, 4.0)
    window, vent = gap("window", 0.0, 1.1, 0.9), gap("opening", 0.021, 1.1, 0.98)
    kind, reason = TP.unlabelled_face_type(well, walls, [window, vent], others=[well, room])
    assert kind == "shaft" and reason.startswith("light well")
    assert TP.twin_band_window(vent, walls, [window, vent]) is True
    # with no window in the other wall's band the gap is a door of the face, as before
    assert TP.twin_band_window(vent, walls, [vent]) is False
    assert TP.unlabelled_face_type(well, walls, [vent], others=[well, room])[0] != "shaft"
    # a gap beside the window (covering under half of it) is its own opening
    side = gap("opening", 0.021, 1.75, 0.5)
    assert TP.twin_band_window(side, walls, [window, side]) is False


def test_a_stored_entrance_override_a_drive_cannot_take_is_said_not_applied():
    from wenart.levels import model as M

    b = _garage_building()
    b["site"] = {"boundary_walls": [], "areas": [], "decor": [], "openings": [],
                 "entrance_overrides": {"d_front": {"solution": "steps", "reason": "an older edit"}}}
    out = M.infer_levels(b)
    e = next(x for x in out["site"]["entrances"] if x["door_id"] == "d_front")
    assert e["solution"] == "drive"
    assert any("override of d_front (steps) not applied" in w and "drive" in w
               for w in out["level_inference"]["warnings"])


def test_the_building_frame_shift_moves_every_correction_record_of_a_wall():
    from wenart.ingest.generic import core as C
    from wenart.ingest.model import WallItem

    w = WallItem(start=(10.0, 5.0), end=(14.0, 5.0), thickness=0.2, box=[0, 0, 0, 0], entity="ent:W", evidence={})
    w.corrected_by_ai = {"rule": "faces_through_gap", "before": {"opening": "gap", "center": [12.0, 5.0], "width": 0.3},
                         "also": [{"rule": "lined_gap", "before": {"start": [10.0, 5.0], "end": [11.0, 5.0]}}]}
    C._shift_wall(w, C._Shift(10.0, 5.0))
    assert tuple(w.start) == (0.0, 0.0) and w.corrected_by_ai["before"]["center"] == [2.0, 0.0]
    assert w.corrected_by_ai["also"][0]["before"]["end"] == [1.0, 0.0]


def test_a_lift_landing_door_opens_to_the_hall_never_into_the_stair():
    from wenart.ingest import twins as TW

    def room(rid, label, rtype, poly):
        return {"id": rid, "level_id": "L1", "label": label, "room_type": rtype, "polygon": poly}

    shaft = room("r_L1_asansor", "Asansör", "shaft", [[0, 0], [1.6, 0], [1.6, 1.8], [0, 1.8]])
    hall = room("r_L1_hall", "Kat Holü", "hall", [[0, 2.0], [4, 2.0], [4, 4], [0, 4]])
    stair = room("r_L1_stair", "Merdiven", "stair", [[1.85, 0], [4, 0], [4, 1.8], [1.85, 1.8]])
    walls = [{"id": "w1", "level_id": "L1", "start": [-0.1, 1.9], "end": [4.1, 1.9], "thickness": 0.2},
             {"id": "w2", "level_id": "L1", "start": [1.725, 0], "end": [1.725, 1.8], "thickness": 0.25}]
    # a wider gap read in the shear wall towards the stair, the drawn landing opening towards the hall
    drawn = [{"id": "o_shear", "level_id": "L1", "type": "opening", "center": [1.725, 0.9], "width": 1.26},
             {"id": "o_hall", "level_id": "L1", "type": "opening", "center": [0.8, 1.9], "width": 1.09}]
    notes = TW.lift_doors([shaft, hall, stair], drawn, walls)
    got = {o["id"]: o for o in drawn}
    assert got["o_hall"]["type"] == "door" and got["o_hall"]["operation"] == "sliding"
    assert "o_shear" not in got and any("opens into the stair" in n for n in notes)   # never its door: closed
    # only a gap towards the stair: a landing door is inferred towards the hall instead, the gap closed
    only = [{"id": "o_shear", "level_id": "L1", "type": "opening", "center": [1.725, 0.9], "width": 1.26}]
    TW.lift_doors([shaft, hall, stair], only, walls)
    assert [o["id"] for o in only] == ["d_r_L1_asansor_lift"] and only[0]["lift_door"] is True



def test_basements_moved_by_their_marks_never_carry_the_ground_floor_the_marks_take_its_frame():
    # real11: the basement plans print -0.50 and -3.30 in a frame where the ground floor stands at +2.50 (its bathroom's
    # floor mark '+2.50' says so: 19 Nov 2026, review A3 A3C-2, the frame needs the ground floor's own mark)
    b = _marks(_stack(4, start=-2), {"L-1": [-0.5], "L-2": [-3.3], "L0": [2.5]})
    got, n = _elev(b)
    assert got == {"L-2": -5.8, "L-1": -3.0, "L0": 0.0, "L1": 3.0}
    rec = n["level_inference"]
    assert any("frame with the ground floor at +2.50" in w for w in rec["warnings"])
    assert any(i.get("item") == "plan height frame" and i.get("value") == 2.5 for i in rec.get("inferred") or [])
    zs = {m["id"]: (m["z"], m.get("frame_shift")) for m in n["level_marks"]}
    assert zs["lm_L-1_0"] == (-3.0, 2.5) and zs["lm_L-2_0"] == (-5.8, 2.5)


def test_a_basement_mark_never_moves_the_ground_floor_or_the_other_marks_without_the_ground_floors_own_mark():
    """19 Nov 2026 (review A3, A3C-2: a basement's two '-2.80' marks made the assumed ground floor follow it +0.20 and
    every plan mark moved -0.20; A3C-3: two outside threshold marks '-0.15' outvoted the room's '±0.00', a stair
    landing's '+1.50' shifted the whole building)."""
    from tests import _levels_fixture as F

    got, n = _elev(_marks(_stack(3, start=-1), {"L-1": [-2.8, -2.8]}))
    assert got == {"L-1": -2.8, "L0": 0.0, "L1": 3.0}
    assert all(m["z"] == -2.8 and not m.get("frame_shift") for m in n["level_marks"])
    assert any("none of its own floor or threshold marks reads that" in w for w in n["level_inference"]["warnings"])
    # a level between the moved basement and the ground floor follows the ground floor, not the basement
    got, _n = _elev(_marks(_stack(3, start=-2), {"L-2": [-5.8, -5.8]}))
    assert got == {"L-2": -5.8, "L-1": -3.0, "L0": 0.0}
    # the ground floor's room reads ±0.00, two outside landings -0.15: no frame
    b = _marks(_stack(2), {"L0": [0.0], "L1": [3.0, 3.0]})
    b["level_marks"] += [F.mark(f"lm_t{k}", -0.15, kind="threshold", point=(9.0 + k, -1.0), room_id=None, level="L0")
                         for k in range(2)]
    got, n = _elev(b)
    assert got == {"L0": 0.0, "L1": 3.0} and not any(m.get("frame_shift") for m in n["level_marks"])
    # only the stair landing's '+1.50' twice: no frame either
    b = _marks(_stack(2), {"L1": [3.0, 3.0]})
    for r in b["rooms"]:
        if r["id"] == "r_living_L0":
            r["room_type"] = "stair"
    b = _marks(b, {"L0": [1.5, 1.5]})
    got, n = _elev(b)
    assert got == {"L0": 0.0, "L1": 3.0} and not any(m.get("frame_shift") for m in n["level_marks"])


def test_a_door_read_in_a_twin_wall_outranks_the_unclassified_gap_it_is_read_twice_as():
    from wenart.ingest.generic import twin_walls as TW

    b = {"walls": [{"id": "w_keep", "level_id": "L0", "start": [0.0, 0.0], "end": [6.0, 0.0], "thickness": 0.25},
                   {"id": "w_dup", "level_id": "L0", "start": [1.0, 0.02], "end": [5.0, 0.02], "thickness": 0.2}],
         "openings": [{"id": "o_gap", "level_id": "L0", "type": "opening", "wall_id": "w_keep", "center": [2.95, 0.0],
                       "width": 1.32, "status": "unverified", "type_raw": "unclassified gap content",
                       "evidence": [{"file": "p.dxf", "method": "derived", "confidence": 0.5}]},
                      {"id": "d_door", "level_id": "L0", "type": "door", "wall_id": "w_dup", "center": [2.785, 0.02],
                       "width": 0.9, "status": "verified", "operation": "swing", "operation_source": "geometry",
                       "swing_side": [2.785, 0.8],
                       "evidence": [{"file": "p.dxf", "method": "vector", "confidence": 0.95, "entity": "INSERT:1/23"}]}]}
    assert TW.merge_twin_walls(b) == ["w_dup"]
    (o,) = b["openings"]                                 # (one mechanism since the merge with reader B: ``_drawn``)
    assert o["id"] == "d_door" and o["type"] == "door" and o["width"] == 0.9 and o["wall_id"] == "w_keep"
    assert b["openings_merged"][0]["id"] == "o_gap" and b["openings_merged"][0]["merged_into"] == "d_door"
    # a classified opening of the kept wall stays as it was (the copy is merged into it)
    b2 = {"walls": [dict(w) for w in b["walls"][:1]] + [{"id": "w_dup", "level_id": "L0", "start": [1.0, 0.02],
                                                         "end": [5.0, 0.02], "thickness": 0.2}],
          "openings": [{"id": "win", "level_id": "L0", "type": "window", "wall_id": "w_keep", "center": [2.95, 0.0],
                        "width": 1.3},
                       {"id": "d2", "level_id": "L0", "type": "door", "wall_id": "w_dup", "center": [2.8, 0.02],
                        "width": 0.9}]}
    TW.merge_twin_walls(b2)
    assert [(x["id"], x["type"]) for x in b2["openings"]] == [("win", "window")]
    # a 'sliding door' read from parallel lines without an arc gives no class (real06's kitchen pass-through)
    b3 = {"walls": [{"id": "w_keep", "level_id": "L0", "start": [0.0, 0.0], "end": [6.0, 0.0], "thickness": 0.25},
                    {"id": "w_dup", "level_id": "L0", "start": [1.0, 0.02], "end": [5.0, 0.02], "thickness": 0.2}],
          "openings": [{"id": "o_pass", "level_id": "L0", "type": "opening", "wall_id": "w_keep", "center": [2.4, 0.0],
                        "width": 2.9, "status": "unverified", "type_raw": "unclassified gap content"},
                       {"id": "d_lines", "level_id": "L0", "type": "door", "wall_id": "w_dup", "center": [2.27, 0.02],
                        "width": 1.95, "status": "verified", "operation": "sliding", "operation_source": "geometry"}]}
    TW.merge_twin_walls(b3)
    assert [(x["id"], x["type"], x["width"]) for x in b3["openings"]] == [("o_pass", "opening", 2.9)]


def _rule_stair(width=0.8, length=2.6, center=(2.0, 1.0)):
    from wenart.ingest.model import FurnitureItem

    return FurnitureItem(type="stair", type_raw=None, center=center, size=(length, width), rotation_deg=0.0,
                         front_deg=None, box=[0, 0, 0, 0], entity="LINE:1", type_method="rule",
                         evidence={"note": "stair rule: 1 flight(s), 9 tread lines"},
                         details={"stair": {"flights": [{"width": width, "lines": 9}], "direction": [1.0, 0.0]}})


def _lines(segs):
    from wenart.ingest.generic.model import Stroke

    return [Stroke(id=f"LINE:{k}", kind="line", pts=[a, b], layer="0") for k, (a, b) in enumerate(segs)]


def test_a_narrow_rule_flight_needs_numbers_an_arrow_or_a_riser_tag_and_a_tile_grid_in_a_tiled_room_is_no_stair():
    from shapely.geometry import box

    from wenart.ingest.generic import symbols as SY

    notes: list = []
    room = box(0.0, 0.0, 4.0, 3.0)
    # a 0.8 m 'flight' with nothing of a stair beside it goes; numbered treads, a riser tag or an arrow keep it
    assert SY.check_rule_stairs([_rule_stair()], [], [], [room], notes) == [] and "no stair" in notes[-1]
    numbers = [_run(str(k + 1), 1.0 + 0.27 * k, 1.0, h=0.12, k=k) for k in range(5)]
    assert len(SY.check_rule_stairs([_rule_stair()], numbers, [], [room], [])) == 1
    assert len(SY.check_rule_stairs([_rule_stair()], [_run("17x17", 2.0, 1.0, k=9)], [], [room], [])) == 1
    head = _lines([((3.0, 1.0), (2.85, 1.08)), ((3.0, 1.0), (2.85, 0.92))])
    assert len(SY.check_rule_stairs([_rule_stair()], [], head, [room], [])) == 1
    # a wide flight needs no mark
    assert len(SY.check_rule_stairs([_rule_stair(width=1.2)], [], [], [room], [])) == 1
    # in a room whose finish is mosaic, lines crossing like a tile grid are no stair (unless the treads are numbered)
    treads = [((0.8 + 0.25 * k, 0.4), (0.8 + 0.25 * k, 1.6)) for k in range(10)]
    cross = [((0.8, y), (3.05, y)) for y in (0.6, 0.85, 1.1, 1.35)]
    grid = _lines(treads + cross)
    finish = [_run("ANTRE A:6.42M2 K:K.MOZAİK", 2.0, 2.4, k=20)]
    wide = _rule_stair(width=1.2)
    assert SY.check_rule_stairs([wide], finish, grid, [room], notes) == [] and "tile grid" in notes[-1]
    assert len(SY.check_rule_stairs([_rule_stair(width=1.2)], finish + numbers, grid, [room], [])) == 1
    assert len(SY.check_rule_stairs([_rule_stair(width=1.2)], [], grid, [room], [])) == 1   # no finish word


def test_a_doors_own_plan_gives_its_ground_first_its_threshold_mark_when_it_prints_no_ground_mark():
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    def entrance(marks):
        b = F.building()
        b["level_marks"] = marks
        return next(x for x in M.infer_levels(b)["site"]["entrances"] if x["door_id"] == "d_front")

    # an upper floor's plan prints the ground beside the building 3.00 m higher; the door's own plan its threshold
    other = F.mark("lm_up", 3.0, kind="ground_finished", point=(8.0, -1.0), level="L1")
    sill = F.mark("lm_sill", 0.0, kind="threshold", point=(8.0, -0.4), level="L0")
    e = entrance([other, sill])
    assert e["below_ground"] is False and e["ground_z"] == 0.0 and "threshold mark lm_sill" in e["ground_source"]
    # a ground mark of the door's own plan comes before the other plan's nearer one
    own = F.mark("lm_own", -0.45, kind="ground_finished", point=(8.0, -2.5), level="L0")
    e = entrance([other, own])
    assert e["ground_source"] == "ground mark lm_own" and e["ground_z"] == -0.45
    # with only the other plan's mark, never that mark: the door stands on the terrain (19 Nov 2026, review A3, OA3-08)
    assert entrance([other])["ground_source"].startswith("terrain")


def test_the_plans_title_elevations_set_the_floors_and_the_datum():
    from wenart.sheets import heights as HT

    levels = [{"id": f"L{k}", "order": k, "kind": "floor"} for k in (-1, 0, 1, 2)]
    out = {"levels": [], "slabs": [{"between": ["L0", "L1"]}], "datum": None}
    lines = HT.apply_storey_marks(out, levels, {-1: -0.5, 0: 2.5, 1: 5.2, 2: 7.9}, 0.2, "p.dxf", "r8",
                                  rule="plan_title_marks", source="the floor elevations the plans' titles print")
    z = {e["level_id"]: e["floor_z"]["value"] for e in out["levels"]}
    assert z == {"L-1": -3.0, "L0": 0.0, "L1": 2.7, "L2": 5.4} and out["datum"]["relative"] == 2.5
    assert out["datum"]["evidence"][0]["rule"] == "plan_title_marks" and "title mark" in lines[0]
    # 19 Nov 2026 (review A3, A3C-6): only a title's own elevation, every storey 2-6 m above the one below
    import wenart.sheets as SH
    from wenart.sheets import levels as LV

    assert LV.title_elevations("1.KAT PLANI") is None and LV.title_elevations("ZEMİN KAT PLANI (+2.50 KOTU)") == (2.5, 2.5)
    assert SH.title_storey_gaps({-1: -0.5, 0: 2.5, 1: 5.2, 2: 7.9}) == []
    assert SH.title_storey_gaps({0: 0.0, 1: 98.5}) == [(0, 1, 98.5)]
    assert SH.title_storey_gaps({0: 0.0, 2: 6.0, 3: 7.0}) == [(2, 3, 1.0)]


def test_a_lift_shaft_keeps_its_landing_door_and_no_gap_window_or_sliver_read_from_its_walls_lines():
    from wenart.ingest import twins as TW

    def room(rid, label, rtype, poly):
        return {"id": rid, "level_id": "L1", "label": label, "room_type": rtype, "polygon": poly}

    shaft = room("r_L1_asansor", "Asansör", "shaft", [[0, 0], [1.6, 0], [1.6, 1.8], [0, 1.8]])
    hall = room("r_L1_hall", "Kat Holü", "hall", [[0, 2.0], [4, 2.0], [4, 4], [0, 4]])
    stair = room("r_L1_stair", "Merdiven", "stair", [[1.85, 0], [4, 0], [4, 1.8], [1.85, 1.8]])
    walls = [{"id": "w1", "level_id": "L1", "start": [-0.1, 1.9], "end": [4.1, 1.9], "thickness": 0.2},
             {"id": "w2", "level_id": "L1", "start": [1.725, -0.1], "end": [1.725, 1.8], "thickness": 0.25}]
    derived = [{"file": "p.dxf", "method": "derived", "confidence": 0.5}]
    ops = [{"id": "o_land", "level_id": "L1", "type": "opening", "wall_id": "w1", "center": [0.8, 1.9], "width": 1.09,
            "evidence": derived},
           {"id": "o_gap", "level_id": "L1", "type": "opening", "wall_id": "w2", "center": [1.725, 0.9], "width": 1.26,
            "status": "unverified", "type_raw": "unclassified gap content", "evidence": derived},
           {"id": "win_x", "level_id": "L1", "type": "window", "wall_id": "w2", "center": [1.725, 0.5], "width": 0.6,
            "evidence": [{"file": "p.dxf", "method": "derived", "rule": "gap_behind_furniture"}]},
           {"id": "d_sliver", "level_id": "L1", "type": "door", "wall_id": "w1", "center": [1.2, 1.9], "width": 0.33,
            "evidence": derived},
           {"id": "d_flat", "level_id": "L1", "type": "door", "wall_id": "w1", "center": [3.0, 1.9], "width": 0.9,
            "evidence": [{"file": "p.dxf", "method": "vector"}]}]
    notes = TW.lift_doors([shaft, hall, stair], ops, walls)      # (one mechanism since the merge with reader B)
    assert sorted(o["id"] for o in ops) == ["d_flat", "o_land"] and ops[0]["lift_door"] is True
    assert sum(1 for n in notes if "into lift shaft" in n) == 3
    # a door drawn as a door (a block, a swing) in the shaft's wall stays
    ops2 = [{"id": "o_land", "level_id": "L1", "type": "opening", "wall_id": "w1", "center": [0.8, 1.9], "width": 1.09,
             "evidence": derived},
            {"id": "d_drawn", "level_id": "L1", "type": "door", "wall_id": "w2", "center": [1.725, 0.9],
             "width": 0.9, "evidence": [{"file": "p.dxf", "method": "vector"}]}]
    TW.lift_doors([shaft, hall, stair], ops2, walls)
    assert sorted(o["id"] for o in ops2) == ["d_drawn", "o_land"]


def test_drawn_lift_cars_in_one_unnamed_face_make_one_lift_shaft_each_with_its_landing_door():
    import copy

    from wenart.ingest import twins as TW

    def room(rid, label, rtype, poly, raw=None):
        return {"id": rid, "level_id": "L0", "label": label, "label_raw": raw, "room_type": rtype, "polygon": poly}

    box_ = room("r_L0_oda", "Oda", "unknown", [[0, 0], [4.2, 0], [4.2, 2.6], [0, 2.6]])
    hall = room("r_L0_hall", "Kat Holü", "hall", [[0, -2.0], [4.2, -2.0], [4.2, -0.2], [0, -0.2]], raw="KAT HOLÜ")
    cars = [{"id": f"sy_L0_{k}", "kind": "other", "level_id": "L0",
             "footprint": {"center": [x, 1.3], "size": [1.85, 2.0], "rotation_deg": 0.0}} for k, x in ((1, 1.05), (2, 3.15))]
    gaps = [{"id": f"o_L0_{k}", "level_id": "L0", "type": "opening", "wall_id": "w_s", "center": [x, -0.1],
             "width": 1.09, "status": "unverified"} for k, x in ((1, 1.05), (2, 3.15))]
    walls = [{"id": "w_s", "level_id": "L0", "start": [0, -0.1], "end": [4.2, -0.1], "thickness": 0.2}]
    rooms, ops, ws = [copy.deepcopy(box_), hall], copy.deepcopy(gaps), copy.deepcopy(walls)
    notes = TW.lift_cars(rooms, cars, [], ops, ws)
    lifts = [r for r in rooms if r["label"] == "Asansör"]
    assert len(notes) == 1 and len(lifts) == 2 and all(r["room_type"] == "shaft" for r in lifts)
    assert sorted(round(r["area_computed"], 1) for r in lifts) == [5.5, 5.5]
    assert any(w["id"].startswith("w_r_L0_oda_cars") for w in ws)
    TW.lift_doors(rooms, ops, ws)
    assert all(o["type"] == "door" and o["operation"] == "sliding" for o in ops)
    # a window, a hinged door or a typed piece (a bed) says it is no lift
    for extra_op, pieces, syms in (
            ({"id": "win", "level_id": "L0", "type": "window", "wall_id": "w_n", "center": [2.1, 2.7], "width": 1.2}, [], cars),
            ({"id": "d_sw", "level_id": "L0", "type": "door", "wall_id": "w_s", "center": [2.1, -0.1], "width": 0.9,
              "operation": "swing"}, [], cars),
            (None, [dict(c, type="bed", kind=None) for c in cars], [])):
        rooms2 = [copy.deepcopy(box_), hall]
        ops2 = copy.deepcopy(gaps) + ([extra_op] if extra_op else [])
        if not syms:
            for p in pieces:
                p.pop("kind")
        assert TW.lift_cars(rooms2, syms, pieces, ops2, copy.deepcopy(walls)) == []


def test_a_door_drawing_an_outside_gap_a_door_tag_or_an_unstacked_face_makes_no_lift_shaft():
    """19 Nov 2026 (review A3, POD-A3-01 / M1: real09's street-entrance vestibule became a one-storey lift shaft, its only
    street door walled up; the 'car' was the box of an unequal double door's swing on 'kapı-pencere')."""
    import copy

    from wenart.ingest import twins as TW

    def room(rid, label, rtype, poly, lv="L0", raw=None):
        return {"id": rid, "level_id": lv, "label": label, "label_raw": raw, "room_type": rtype, "polygon": poly}

    box_ = room("r_L0_oda", "Oda", "unknown", [[0, 0], [2.2, 0], [2.2, 2.6], [0, 2.6]])
    hall = room("r_L0_hall", "Kat Holü", "hall", [[0, -2.0], [4.2, -2.0], [4.2, -0.2], [0, -0.2]], raw="KAT HOLÜ")
    car = {"id": "f_L0_1", "type": "unknown", "level_id": "L0",
           "footprint": {"center": [1.1, 1.3], "size": [1.85, 2.0], "rotation_deg": 0.0},
           "evidence": [{"file": "p.dxf", "method": "vector", "confidence": 0.9, "entity": "LINE:1,LINE:2"}]}
    gap = {"id": "o_L0_1", "level_id": "L0", "type": "opening", "wall_id": "w_s", "center": [1.1, -0.1], "width": 1.09}
    walls = [{"id": "w_s", "level_id": "L0", "start": [0, -0.1], "end": [4.2, -0.1], "thickness": 0.2}]

    def run(cars=(car,), extra=(), texts=(), levels=(), rooms_more=()):
        rooms = [copy.deepcopy(box_), hall] + list(rooms_more)
        notes = TW.lift_cars(rooms, [], [copy.deepcopy(c) for c in cars], [copy.deepcopy(gap)] + list(extra),
                             copy.deepcopy(walls), list(texts), list(levels))
        return rooms[0]["room_type"] == "shaft", notes

    assert run()[0]                                               # the plain case: a lift shaft
    # an outline holding arcs (a door's swing) or drawn on a door layer is no car
    arcs = dict(car, evidence=[dict(car["evidence"][0], entity="LINE:1,ARC:48B1,ARC:48C3")])
    made, notes = run(cars=(arcs,))
    assert not made and any("ARC:48B1" in n and "no lift car" in n for n in notes)
    layer = dict(car, evidence=[dict(car["evidence"][0], layer="kapı-pencere")])
    assert not run(cars=(layer,))[0]
    # a door size tag inside the face
    made, notes = run(texts=[{"text": "K:100/210", "point": [1.5, 2.0], "level_id": "L0"}])
    assert not made and any("door size tag 'K:100/210'" in n for n in notes)
    assert run(texts=[{"text": "75/45", "point": [1.5, 2.0], "level_id": "L0"}])[0]        # a vent's size: no door
    # a gap onto nothing (the outside)
    street = {"id": "o_L0_2", "level_id": "L0", "type": "opening", "center": [1.1, 2.7], "width": 1.5}
    made, notes = run(extra=[street])
    assert not made and any("o_L0_2 opens onto nothing" in n for n in notes)
    # the storey above reads a bedroom there and no shaft: no lift; a lift there: a lift
    levels = [{"id": "L0", "elevation": 0.0}, {"id": "L1", "elevation": 3.0}]
    bed = room("r_L1_yatak", "Yatak Odası", "bedroom", [[-0.5, -0.5], [3.0, -0.5], [3.0, 3.0], [-0.5, 3.0]], lv="L1")
    made, notes = run(levels=levels, rooms_more=[bed])
    assert not made and any("r_L1_yatak" in n and "stacks" in n for n in notes)
    lift = room("r_L1_asansor", "Asansör", "shaft", [[0, 0], [2.2, 0], [2.2, 2.6], [0, 2.6]], lv="L1", raw="ASANSÖR")
    assert run(levels=levels, rooms_more=[bed, lift])[0]
    assert run(levels=[{"id": "L0", "elevation": 0.0}])[0]          # a single storey (real03's typical floor)


def test_an_inferred_landing_door_stands_on_the_shaft_side_with_the_deepest_landing_never_on_a_corner():
    """19 Nov 2026 (review A3, POD-A3-02: real20's free-standing shaft got its door on its corner, half past its wall's
    end, facing the 0.40 m slot beside the stair; the landing is on its north side). M3: never towards a stair room."""
    from shapely.geometry import LineString, Point

    from wenart.ingest import twins as TW

    def room(rid, label, rtype, poly):
        return {"id": rid, "level_id": "L0", "label": label, "label_raw": label.upper(), "room_type": rtype,
                "polygon": poly}

    shaft = room("r_L0_asansor", "Asansör", "shaft", [[4.77, 2.22], [6.47, 2.22], [6.47, 3.95], [4.77, 3.95]])
    # the hall wraps the shaft: 0.15 m west, 0.37 m south, 0.40 m east to the stair, a 0.15 m wall and the 1.2 m landing
    # north (real20 L0)
    outer = TW._poly(room("x", "x", "hall", [[4.62, 1.85], [9.37, 1.85], [9.37, 4.1], [9.42, 4.1], [9.42, 5.3],
                                              [4.57, 5.3], [4.57, 4.1], [6.62, 4.1], [6.62, 3.95], [4.62, 3.95]]))
    cut = outer.difference(TW._poly(shaft))
    hall = room("r_L0_hall", "Kat Holü", "hall", [list(p) for p in cut.exterior.coords][:-1])
    stair = {"id": "f_st", "type": "stair", "level_id": "L0",
             "footprint": {"center": [8.125, 2.975], "size": [2.5, 2.25], "rotation_deg": 0.0}}
    walls = [{"id": f"w{k}", "level_id": "L0", "start": a, "end": b, "thickness": 0.1}
             for k, (a, b) in enumerate([([4.77, 2.22], [6.47, 2.22]), ([6.47, 2.22], [6.47, 3.95]),
                                         ([6.47, 3.95], [4.77, 3.95]), ([4.77, 3.95], [4.77, 2.22])])]
    ops = []
    notes = TW.lift_doors([shaft, hall], ops, walls, [stair])
    door = ops[0]
    assert door["wall_id"] == "w2" and abs(door["center"][1] - 3.95) < 0.01 and abs(door["center"][0] - 5.62) < 0.01
    assert any("1.20 m clear in front" in n for n in notes)
    # never past the wall's ends
    c = TW._clamped(LineString([(0, 0), (1.0, 0)]), Point(0.0, 0.0), 0.9)
    assert abs(c.x - 0.5) < 1e-9
    c = TW._clamped(LineString([(0, 0), (3.0, 0)]), Point(0.0, 0.0), 0.9)
    assert abs(c.x - 0.5) < 1e-9
    # M3: a stair room whose flight stands in front of the shaft is no landing; a flat's room never is
    st_room = room("r_L0_merdiven", "Merdiven", "stair", [[6.6, 1.9], [9.3, 1.9], [9.3, 4.0], [6.6, 4.0]])
    bath = room("r_L0_banyo", "Banyo", "bathroom", [[2.5, 2.0], [4.7, 2.0], [4.7, 4.2], [2.5, 4.2]])
    ops = []
    notes = TW.lift_doors([shaft, st_room, bath], ops, walls, [stair])
    assert not ops and any("no landing door inferred" in n for n in notes)
    # ... but a stair room with its landing in front of the shaft is its landing (real14's core 'Merdiven')
    landing = room("r_L0_merdiven", "Merdiven", "stair", [[4.0, 0.0], [7.5, 0.0], [7.5, 2.12], [4.0, 2.12]])
    flight = {"id": "f_st2", "type": "stair", "level_id": "L0",
              "footprint": {"center": [7.0, 1.0], "size": [1.0, 2.0], "rotation_deg": 0.0}}
    ops = []
    TW.lift_doors([shaft, landing, bath], ops, walls, [flight])
    assert [o["wall_id"] for o in ops] == ["w0"] and abs(ops[0]["center"][1] - 2.22) < 0.01


def test_rc16_names_a_riser_no_one_can_climb():
    """19 Nov 2026 (review A3, POD-A3-03: real10 L-1 f_L-1_004 built 7 risers of 0.43 m on a 1.2 m flight read from
    furnishing lines, and RC16 said nothing): a riser outside 0.15-0.22 m is a major 'risers' finding."""
    from wenart.reading_check import stairs as ST

    def building(lines: int, length: float) -> dict:
        flight = {"start": [0.0, 1.0], "end": [length, 1.0], "width": 1.0, "lines": lines,
                  "spacing": round(length / max(lines - 1, 1), 3)}
        f = {"id": "f_L0_001", "level_id": "L0", "room_id": "r", "type": "stair", "source": "from_documents",
             "footprint": {"center": [length / 2.0, 1.0], "size": [length, 1.0], "rotation_deg": 0.0},
             "status": "unverified", "evidence": [{"file": "p.dxf", "method": "vector", "confidence": 0.9}],
             "stair": {"flights": [flight], "landing": None, "direction": [1.0, 0.0], "direction_assumed": True,
                       "turn": "straight", "turn_assumed": True, "void_assumed": True, "riser_m": None,
                       "riser_source": None, "reason": "test"}}
        return {"levels": [{"id": "L0", "elevation": 0.0}, {"id": "L1", "elevation": 3.0}], "walls": [],
                "furniture": [f]}

    steep = [f for f in ST.findings_of(building(7, 1.2)) if f["rule"] == "risers"]
    assert steep and steep[0]["severity"] == "major" and "0.15-0.22 m" in steep[0]["message"]
    ok = [f for f in ST.findings_of(building(17, 4.4)) if f["rule"] == "risers" and "0.15-0.22" in f["message"]]
    assert ok == []


def test_a_face_broken_only_where_a_cross_wall_or_a_stair_line_meets_it_still_runs_through_the_gap():
    """19 Nov 2026 (review A3, M6: real15 L0's 1.17 m gap between the kitchen and the stair foot: its bottom face broken
    only at the T-junction of the kitchen's cross wall, its top face only where the stair's diagonal meets it)."""
    from wenart.ingest.generic import core as GC

    wall = _wall((5.5, 0.0), (5.5, 4.0), t=0.26, entity="w1")
    gap = _gap((5.5, 2.0), 1.17)
    west = [_line((5.37, 0.0), (5.37, 1.9), 1, layer="Z_duvar"), _line((5.37, 2.01), (5.37, 4.0), 2, layer="Z_duvar")]
    east = [_line((5.63, 0.0), (5.63, 2.1), 3, layer="Z_duvar"), _line((5.63, 2.25), (5.63, 4.0), 4, layer="Z_duvar")]
    cross = [_line((4.0, 1.9), (5.37, 1.9), 5, layer="Z_duvar"), _line((4.0, 2.01), (5.37, 2.01), 6, layer="Z_duvar")]
    stair = [_line((5.63, 2.12), (7.0, 3.5), 7, layer="merdiven")]
    walls, openings = GC._faces_through_gaps(_ex2(), "p", [wall], [gap], west + east + cross + stair)
    assert openings == [] and walls[0].corrected_by_ai["rule"] == "faces_through_gap"
    # the same breaks with nothing crossing there: a gap
    assert GC._faces_through_gaps(_ex2(), "p", [wall], [gap], west + east)[1] == [gap]
    # a break longer than the wall is thick, even with a line ending in it: a gap
    far = [_line((5.63, 0.0), (5.63, 1.7), 8, layer="Z_duvar"), _line((5.63, 2.3), (5.63, 4.0), 9, layer="Z_duvar")]
    assert GC._faces_through_gaps(_ex2(), "p", [wall], [gap], west + far + cross + stair)[1] == [gap]


def test_a_door_read_from_an_arc_alone_in_a_drawn_doors_gap_is_that_door_read_twice():
    """19 Nov 2026 (review A3, M5: real09 L0, d_L0_014 from ARC:82D alone, the swing of the flat's entrance door, and
    d_L0_020 from its own arc and leaf in one bedroom door's gap)."""
    from wenart.ingest.generic import twin_walls as TWW

    wall = {"id": "w1", "level_id": "L0", "start": [7.63, 4.09], "end": [13.63, 4.09], "thickness": 0.26}
    alone = {"id": "d_L0_014", "type": "door", "level_id": "L0", "wall_id": "w1", "center": [8.105, 4.09], "width": 0.95,
             "operation": "swing", "evidence": [{"file": "p.dxf", "method": "vector", "confidence": 0.7,
                                                 "entity": "ARC:82D", "note": TWW.LEAFLESS_NOTE}]}
    drawn = {"id": "d_L0_020", "type": "door", "level_id": "L0", "wall_id": "w1", "center": [8.08, 4.09], "width": 0.8,
             "operation": "swing", "evidence": [{"file": "p.dxf", "method": "vector", "confidence": 0.85,
                                                 "entity": "ARC:803,LINE:80A,LINE:808"}]}
    other = dict(drawn, id="d_L0_021", center=[13.18, 4.09])
    b = {"walls": [wall], "openings": [alone, drawn, other]}
    assert TWW.one_door_per_gap(b) == ["d_L0_014"]
    assert [o["id"] for o in b["openings"]] == ["d_L0_020", "d_L0_021"]
    rec = b["openings_merged"][0]
    assert rec["merged_into"] == "d_L0_020" and rec["corrected_by_ai"]["rule"] == TWW.ONE_DOOR_RULE
    # two leaves side by side (a double door read as two) stay
    left = dict(alone, center=[8.0, 4.09], width=0.8)
    right = dict(drawn, id="d_r", center=[8.8, 4.09], width=0.8)
    b = {"walls": [wall], "openings": [left, right]}
    assert TWW.one_door_per_gap(b) == [] and len(b["openings"]) == 2
    # A3FC-3 (real13's main entrance): a 1.50 m 'sliding door' read from the frame lines of the 100 cm leaf, the leaf's
    # 0.91 m swing door inside it: one 1.50 m double door
    frame = {"id": "d_L-1_002", "type": "door", "level_id": "L0", "wall_id": "w1", "center": [9.16, 4.09], "width": 1.5,
             "operation": "sliding", "evidence": [{"file": "p.dxf", "method": "vector", "confidence": 0.85,
                                                   "entity": "LINE:9A356D,LINE:9A3582",
                                                   "note": "2 leaf/leaves drawn parallel to the wall without a swing "
                                                           "arc: a sliding door"}]}
    leaf = dict(drawn, id="d_L-1_003", center=[9.41, 4.09], width=0.911,
                evidence=[{"file": "p.dxf", "method": "vector", "confidence": 0.95, "entity": "ELLIPSE:9A3584,LINE:1"}])
    b = {"walls": [wall], "openings": [frame, leaf]}
    assert TWW.one_door_per_gap(b) == ["d_L-1_002"]
    (door,) = b["openings"]
    assert door["id"] == "d_L-1_003" and door["width"] == 1.5 and door["operation"] == "double"
    assert abs(door["center"][0] - 9.16) < 1e-6 and door["corrected_by_ai"]["before"]["width"] == 0.911


def test_a_swing_stored_across_0_degrees_on_a_door_and_window_layer_is_a_door():
    """19 Nov 2026 (review A3, A3C-5: dxf_generic stores a 270-360 quarter as 270 -> 0; abs(end - start) % 360 read it as
    270 degrees, so one door in four orientations on 'kapı-pencere' stayed an opening)."""
    from wenart.ingest.generic import core as GC

    wall = _wall((0.0, 3.0), (6.0, 3.0), t=0.25, entity="w1")
    for a0, a1 in ((270.0, 360.0), (270.0, 0.0)):
        gap = _gap((3.0, 3.0), 1.32)
        gap.rotation_deg = 0.0
        arc = _arc("ARC:9", (2.4, 3.0), 0.8, a0, a1, layer="kapı-pencere")
        got = GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap], [arc])
        assert got[0].kind == "door", (a0, a1)


def test_a_flight_split_by_its_walking_line_into_two_narrow_strips_is_one_flight():
    """19 Nov 2026 (review A3, A3C-4: a 1.0-1.19 m straight flight with a walking line down its middle was split into two
    strips under 0.6 m and lost; a 1.3 m one became two 0.65 m flights the narrow-flight rule then dropped)."""
    from wenart.ingest.generic import symbols as SY

    for width in (1.0, 1.1, 1.3):
        treads = [_line((1.0, 1.0 + 0.28 * k), (1.0 + width, 1.0 + 0.28 * k), 300 + k) for k in range(10)]
        stringers = [_line((1.0, 1.0), (1.0, 3.52), 400), _line((1.0 + width, 1.0), (1.0 + width, 3.52), 401)]
        walk = [_line((1.0 + width / 2, 1.0), (1.0 + width / 2, 3.52), 402)]
        st = _stair_of(treads + stringers + walk)
        assert st is not None, width
        widths = sorted(round(f["width"], 2) for f in st["flights"])
        assert widths == ([width] if width < 2 * SY.FLIGHT_MIN_WIDTH_M else [width / 2, width / 2]), (width, widths)
    # the two 0.65 m flights side by side count as one 1.3 m stair for the narrow-flight rule
    flights = [{"start": [0.0, 0.0], "end": [0.0, 2.5], "width": 0.65},
               {"start": [0.65, 2.5], "end": [0.65, 0.0], "width": 0.65}]
    assert abs(SY._stair_width(flights) - 1.3) < 1e-9
    apart = [flights[0], dict(flights[1], start=[2.0, 2.5], end=[2.0, 0.0])]
    assert abs(SY._stair_width(apart) - 0.65) < 1e-9


def test_a_size_tag_lower_than_a_door_on_a_door_layer_makes_its_gap_a_window_with_the_parapet_sill():
    """19 Nov 2026 (review A3, OA3-01: real11's '80/150' with 'PARAPET:90CM' on its door layer KAPI made no door, and the
    gap's three-line window symbol became a 1.02 m sliding door on L0-L6)."""
    from types import SimpleNamespace

    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic.model import TextRun
    from wenart.ingest.model import OpeningItem

    def tag(text, x, y, layer="KAPI"):
        return TextRun(id="T" + text, text=text, box=(x - 0.2, y - 0.05, x + 0.2, y + 0.05), height=0.1,
                       rotation_deg=0.0, evidence=[{"layer": layer}])

    wall = _wall((0.0, 3.0), (6.0, 3.0), t=0.35, entity="w1")
    sliding = OpeningItem("door", 1.02, (3.0, 3.0), 0.0, [0, 0, 0, 0], "LINE:1,LINE:2",
                          {"method": "vector", "note": "2 leaf/leaves drawn parallel to the wall without a swing arc: a "
                                                       "sliding door"}, operation="sliding", operation_source="geometry")
    texts = [tag("80/150", 3.0, 3.5), tag("PARAPET:90CM", 3.0, 3.8, layer="YAZI")]
    got = GC._window_tags(SimpleNamespace(notes=[]), "x", [wall], [sliding], texts, 1.0)
    assert got is not None and [o.kind for o in got] == ["window"]
    assert abs(got[0].width - 0.8) < 1e-6 and got[0].height == 1.5 and got[0].sill == 0.9 and not got[0].assumed
    # a door-high tag on a door layer is a door's (``_door_tags``), never a window's here
    assert GC._window_tags(SimpleNamespace(notes=[]), "x", [wall], [sliding], [tag("80/210", 3.0, 3.5)], 1.0) is None


def test_a_lift_machine_room_is_a_technical_room_never_a_shaft():
    """19 Nov 2026 (review A3, OA3-03: real13's 'ASANSÖR MAKİNA HİDROLİK' and 'ASANSÖR MAK.DAİR.', real14's 'ASANSÖR
    MAKN.DAİRESİ' became lift shafts with sliding landing doors, one into a stair)."""
    from wenart import building as B
    from wenart.ingest import twins as TW

    for label in ("ASANSÖR MAKİNA HİDROLİK", "ASANSÖR MAK.DAİR.", "ASANSÖR MAKN.DAİRESİ", "MAKİNE DAİRESİ"):
        assert B.room_type_for(label) == "technical" and B.machine_room(label), label
    assert B.room_type_for("ASANSÖR") == "shaft" and not B.machine_room("ASANSÖR HOLÜ")
    # even typed shaft by an older reading, a machine room gets no landing door and keeps its drawn swing door
    room = {"id": "r_L7_mak", "level_id": "L7", "label": "Asansör Makn.Dairesi", "label_raw": "ASANSÖR MAKN.DAİRESİ",
            "room_type": "shaft", "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}
    hall = {"id": "r_L7_hol", "level_id": "L7", "label": "Hol", "room_type": "hall",
            "polygon": [[0, 4.2], [4, 4.2], [4, 6], [0, 6]]}
    door = {"id": "d1", "level_id": "L7", "type": "door", "operation": "swing", "center": [2.0, 4.1], "width": 0.9,
            "evidence": [{"file": "p.dxf", "method": "vector", "confidence": 0.9}]}
    ops = [door]
    TW.lift_doors([room, hall], ops, [{"id": "w", "level_id": "L7", "start": [0, 4.1], "end": [4, 4.1],
                                       "thickness": 0.2}])
    assert ops == [door] and door["operation"] == "swing" and not door.get("lift_door")


def test_an_outdoor_label_outline_makes_no_outline_wall_and_a_section_arrow_no_wall():
    """19 Nov 2026 (review A3, OA3-07: real18 L0's BALKON tile hatches became 2.7 m exterior walls; OA3-04: real13's
    section arrows, solid triangles on KOLON, became walls and a 2.24 m wide-gap wall out of the façade)."""
    from shapely.geometry import Point, Polygon

    from wenart.ingest.generic import outlines as OL
    from wenart.ingest.generic import walls as W
    from wenart.ingest.generic.model import Stroke

    def block(name):
        from types import SimpleNamespace
        return SimpleNamespace(name=name, anchor=(1.0, 0.5), exterior=False, area_m2=None, room_type=None)

    ring = Stroke(id="HATCH:1", kind="polyline", pts=[(0, 0), (4, 0), (4, 1), (0, 1)], closed=True, layer="0")
    assert OL.labelled_outlines([ring], [block("BALKON")]) == []
    assert len(OL.labelled_outlines([ring], [block("SALON")])) == 1
    assert W.symbol_fill(Polygon([(0, 0), (0.5, 0), (0.25, 0.25)]))                    # a section arrow
    assert not W.symbol_fill(Polygon([(0, 0), (0.3, 0), (0.3, 0.3), (0, 0.3)]))        # a column
    assert not W.symbol_fill(Point(0, 0).buffer(0.2))                                  # a round column


def test_a_lift_label_in_an_oversized_part_cuts_the_lift_out_of_it():
    """19 Nov 2026 (review A3, OA3-02: real11's lift was built on one storey; on the others the landing strip and the
    lift box stayed one part too long for a lift and the ASANSOR label gave up). Review A4 (A4FC-1 / A4C-01): the shaft
    is the drawn wall faces round the label, the same on every storey drawn the same; an arm cut on no drawn line (it
    ran through the car) is never taken; the landing door goes into the drawn opening of the shaft's wall."""
    import copy

    from wenart.ingest import twins as TW

    def hall(lv):
        # the landing strip and the lift box of one L-shaped part (real11 L1), the label in the box
        return {"id": f"r_{lv}_hall", "level_id": lv, "label": "Kat Holü", "room_type": "hall",
                "polygon": [[13.58, 9.19], [8.91, 9.19], [8.91, 9.63], [8.86, 9.63], [8.86, 10.24], [11.68, 10.24],
                            [11.68, 10.79], [13.58, 10.79]],
                "sub_spaces": [{"label": "ASANSOR", "type": "lift", "anchor": [12.23, 9.90], "min_m2": 1.0,
                                "max_m2": 8.0}]}

    # the drawn shaft faces: 165 x 160 inside, the west wall's inner face at 11.93 with its 0.65 m door opening
    faces = [((11.93, 9.19), (13.58, 9.19)), ((11.93, 10.79), (13.58, 10.79)), ((13.58, 9.19), (13.58, 10.79)),
             ((11.93, 9.19), (11.93, 9.64)), ((11.93, 10.29), (11.93, 10.79))]
    rooms, walls = [hall("L1"), hall("L2")], []
    notes = TW.carve_stacked_lifts(rooms, walls, {"L1": faces, "L2": faces})
    lifts = {r["level_id"]: r for r in rooms if r["id"].endswith("_lift")}
    assert sorted(lifts) == ["L1", "L2"] and len(notes) == 2
    assert all(abs(r["area_computed"] - 2.64) < 0.02 and r["room_type"] == "shaft" for r in lifts.values())
    assert TW._iou(TW._poly(lifts["L1"]), TW._poly(lifts["L2"])) > 0.99                   # the same outline
    assert all(not r.get("sub_spaces") for r in rooms if not r["id"].endswith("_lift")) and walls
    # the landing door into the drawn opening of the west wall, towards the hall
    ops = []
    TW.lift_doors([r for r in rooms if r["level_id"] == "L1"], ops,
                  walls + [{"id": "w_west", "level_id": "L1", "start": [11.805, 9.19], "end": [11.805, 10.79],
                            "thickness": 0.25}], (), None, None, {"L1": faces})
    assert len(ops) == 1 and abs(ops[0]["center"][1] - 9.965) < 0.02 and abs(ops[0]["width"] - 0.65) < 0.01
    # with no drawn faces, no arm through the car is cut
    assert TW.carve_stacked_lifts([copy.deepcopy(hall("L3"))], []) == []
    # with no label in the part, nothing is cut
    bare = copy.deepcopy(hall("L3"))
    bare.pop("sub_spaces")
    assert TW.carve_stacked_lifts([bare], [], {"L3": faces}) == []


def test_a_wide_gap_holding_a_tagged_window_is_that_wall_with_its_window():
    """19 Nov 2026 (review A3, OA3-02: real11's façade between the bathrooms' wall ends, a wall with its 120/120 window,
    was one 5.91 m wide-gap opening)."""
    from types import SimpleNamespace

    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic.model import TextRun
    from wenart.ingest.model import OpeningItem

    wall = _wall((7.95, 13.86), (13.87, 13.86), t=0.23, entity="w130")
    gap = OpeningItem("opening", 5.91, (10.91, 13.86), 0.0, [0, 0, 0, 0], "gap",
                      {"method": "inferred", "rule": "wide_gap"}, status="unverified")
    tag = TextRun(id="T1", text="120/120", box=(10.1, 13.9, 10.5, 14.0), height=0.1, rotation_deg=0.0,
                  evidence=[{"layer": "KAPI"}])
    got = GC._window_tags(SimpleNamespace(notes=[]), "x", [wall], [gap], [tag], 1.0)
    assert got is not None and [o.kind for o in got] == ["window"] and abs(got[0].width - 1.2) < 1e-6


def test_a_wide_gap_bridge_never_runs_through_drawn_furniture_or_beside_a_drawn_wall_from_a_corner():
    """19 Nov 2026 (review A3, OA3-05: real13's salons cut along the column axis by wide-gap walls through the dining
    table and the sofa, and a 0.34 m sliver room left beside a drawn wall)."""
    from types import SimpleNamespace

    from wenart.ingest.generic import core as GC

    walls = [_wall((0.0, 0.0), (0.0, 1.5), t=0.2, entity="a"), _wall((0.0, 6.0), (0.0, 4.5), t=0.2, entity="b"),
             _wall((0.6, 0.0), (0.6, 6.0), t=0.15, entity="c")]
    run_on = {"wall": 0, "start": (0.0, 1.5), "end": (0.0, 4.5), "width": 3.0, "to": 1, "from_free_end": False}
    free = dict(run_on, from_free_end=True)
    ex = SimpleNamespace(notes=[])
    assert GC._sound_bridges(ex, "x", walls, [run_on], []) == []                     # beside wall c, 0.6 m off
    assert GC._sound_bridges(ex, "x", walls, [free], []) == [free]                   # from a free end it stays
    table = _line((-0.5, 3.0), (0.5, 3.0), 77, layer="TEFRIS")
    assert GC._sound_bridges(ex, "x", walls[:2], [free], [table]) == []              # through a drawn table
    assert any("drawn furniture" in n for n in ex.notes)


def _lift_core(lv: str, depot: bool = False) -> tuple:
    """A real17-like lift core: a 2.0 x 1.8 m shaft, its east wall 0.25 m with the 'Kat Holü' 1.10 m deep beyond it, a
    shop north of it 2.2 m deep; ``depot``: the shaft stands free in a basement depot (every side 3 m deep)."""
    def room(rid, label, rtype, poly):
        return {"id": rid, "level_id": lv, "label": label, "label_raw": label.upper(), "room_type": rtype,
                "polygon": poly}

    shaft = room(f"r_{lv}_asansor", "Asansör", "shaft", [[11.92, 15.86], [13.92, 15.86], [13.92, 17.66], [11.92, 17.66]])
    if depot:
        rooms = [shaft, room(f"r_{lv}_depo", "Depo", "storage", [[8.0, 12.0], [18.0, 12.0], [18.0, 21.0], [8.0, 21.0]])]
    else:
        rooms = [shaft, room(f"r_{lv}_hall", "Kat Holü", "hall", [[14.17, 15.0], [15.27, 15.0], [15.27, 18.5], [14.17, 18.5]]),
                 room(f"r_{lv}_dukkan", "Dükkan", "other", [[11.0, 17.91], [16.0, 17.91], [16.0, 20.1], [11.0, 20.1]])]
    walls = [{"id": f"w_{lv}_e", "level_id": lv, "start": [14.045, 15.86], "end": [14.045, 17.66], "thickness": 0.25},
             {"id": f"w_{lv}_n", "level_id": lv, "start": [11.92, 17.785], "end": [14.17, 17.785], "thickness": 0.25},
             {"id": f"w_{lv}_s", "level_id": lv, "start": [11.92, 15.735], "end": [14.17, 15.735], "thickness": 0.25},
             {"id": f"w_{lv}_w", "level_id": lv, "start": [11.795, 15.86], "end": [11.795, 17.66], "thickness": 0.25}]
    return rooms, walls


def test_a_landing_door_frame_drawn_in_the_shaft_wall_is_its_door_and_the_storeys_without_one_follow_it():
    """19 Nov 2026 (review A4, SW-A4-02 / POD-A4-02: real17 L0's and real20's lift blocks draw the landing door's frame
    on a detail layer in a wall whose faces run through, and the door was inferred into a shop or 7.5 cm off the frame;
    SW-A4-01: real17 L-1's free-standing shaft took the first of four equally deep sides, into the concrete)."""
    import copy

    from wenart.ingest import twins as TW

    # the shaft's inner faces drawn through, the east wall's outer face at x 14.17
    faces = [((11.92, 15.86), (13.92, 15.86)), ((13.92, 15.86), (13.92, 17.66)), ((13.92, 17.66), (11.92, 17.66)),
             ((11.92, 17.66), (11.92, 15.86)), ((14.17, 15.86), (14.17, 17.66))]
    # the landing door's frame in the east wall (two runs and their jambs), and the counterweight's rails inside the
    # shaft by its west wall (a rectangle of the same kind, all inside: no frame)
    frame = [((13.971, 16.049), (13.971, 17.449)), ((14.171, 16.049), (14.171, 17.449)),
             ((13.971, 16.049), (14.171, 16.049)), ((13.971, 17.449), (14.171, 17.449))]
    rails = [((12.066, 16.225), (12.066, 17.286)), ((12.183, 16.225), (12.183, 17.286)),
             ((12.066, 16.225), (12.183, 16.225)), ((12.066, 17.286), (12.183, 17.286))]
    rooms, walls = _lift_core("L0")
    ops = []
    notes = TW.lift_doors(rooms, ops, walls, (), [], [], {"L0": faces}, {"L0": frame + rails})
    assert len(ops) == 1 and ops[0]["wall_id"] == "w_L0_e" and abs(ops[0]["center"][1] - 16.749) < 0.01
    assert abs(ops[0]["width"] - 1.40) < 0.01 and ops[0]["evidence"][0]["method"] == "derived"
    assert any("where the drawing shows it (frame)" in n for n in notes)
    # with no frame drawn, the shop is never the lift's landing (merge of 20 Nov 2026, the building-sense branch's
    # MF3: a unit's own use): the door goes to the hall ...
    ops2 = []
    TW.lift_doors(copy.deepcopy(rooms), ops2, copy.deepcopy(walls), (), [], [], {"L0": faces}, {"L0": rails})
    assert ops2[0]["wall_id"] == "w_L0_e"
    # ... but a storey with no frame drawn takes the side of the drawn door of the shaft stacked on it, ahead of the
    # depth rule (L1: the same core) and of list order (L-1: free in a depot, every side 3 m deep)
    up, wu = _lift_core("L1")
    down, wd = _lift_core("L-1", depot=True)
    ops3 = []
    notes = TW.lift_doors(down + up + rooms, ops3, wd + wu + walls, (), [], [], {"L0": faces}, {"L0": frame})
    by = {o["level_id"]: o for o in ops3}
    assert sorted(by) == ["L-1", "L0", "L1"]
    assert all(abs(o["center"][0] - 14.0) < 0.1 for o in by.values()), by     # every storey's door faces east
    assert sum("stacked shaft's drawn landing door" in n for n in notes) == 2


def test_a_lift_pit_storey_gets_no_landing_door_and_a_house_lift_opens_into_its_living_room():
    """19 Nov 2026 (review A4, A4FC-1: real11 L-2's bare pit, its floor mark -1.80 over the storey's -3.30, got a door
    into the shelter; A4C-04: a lift whose only neighbour is a dwelling's living room got no landing door)."""
    import copy

    from wenart.ingest import twins as TW

    rooms, walls = _lift_core("L-2", depot=True)
    texts = [{"text": "-1.80", "point": [12.9, 16.7], "level_id": "L-2"},
             {"text": "-3.30", "point": [10.0, 14.0], "level_id": "L-2"},
             {"text": "-3.30", "point": [16.0, 19.0], "level_id": "L-2"}]
    ops = []
    notes = TW.lift_doors(copy.deepcopy(rooms), ops, copy.deepcopy(walls), (), [], [], None, None, texts)
    assert not ops and any("pit below the lowest stop" in n for n in notes)
    # the pit's mark below the storey's floor (the lowest stop draws its pit's depth): a door
    low = [dict(t, text="-4.80") if t["text"] == "-1.80" else t for t in texts]
    ops = []
    TW.lift_doors(copy.deepcopy(rooms), ops, copy.deepcopy(walls), (), [], [], None, None, low)
    assert len(ops) == 1
    # A4C-04: beside a living room only, the house's own lift opens into it; beside a bathroom only, never
    for rtype, n in (("living", 1), ("dining", 1), ("bathroom", 0), ("bedroom", 0)):
        rs, ws = _lift_core("L0", depot=True)
        rs[1]["room_type"] = rtype
        ops = []
        TW.lift_doors(rs, ops, ws, ())
        assert len(ops) == n, rtype


def test_twin_lifts_in_one_hall_get_unique_rooms_walls_and_doors():
    """19 Nov 2026 (review A4, A4C-03: a second carve in one room reused the first one's room id, wall ids and door id;
    two stacked twins carved only the first label)."""
    import copy

    from wenart.ingest import twins as TW

    def hall(lv):
        return {"id": f"r_{lv}_hall", "level_id": lv, "label": "Kat Holü", "room_type": "hall",
                "polygon": [[0.0, 0.0], [8.0, 0.0], [8.0, 5.0], [0.0, 5.0]],
                "sub_spaces": [{"label": "ASANSÖR", "type": "lift", "anchor": [1.0, 4.0], "min_m2": 1.0, "max_m2": 8.0},
                               {"label": "ASANSÖR", "type": "lift", "anchor": [3.0, 4.0], "min_m2": 1.0, "max_m2": 8.0}]}

    def car(lv, k, x):
        return {"id": f"f_{lv}_{k}", "type": "unknown", "level_id": lv,
                "footprint": {"center": [x, 4.15], "size": [1.6, 1.5], "rotation_deg": 0.0}}

    def lifts_of(rooms):
        return [r for r in rooms if "_lift" in r["id"]]

    def check(rooms, walls):
        lifts = lifts_of(rooms)
        assert len(lifts) >= 2 and len({r["id"] for r in rooms}) == len(rooms)
        assert len({w["id"] for w in walls}) == len(walls)
        assert all(not r.get("sub_spaces") for r in rooms)
        ops = []
        for r in lifts:
            r["room_type"], r["label_raw"] = "shaft", "ASANSÖR"
        TW.lift_doors(rooms, ops, walls, ())
        assert len({o["id"] for o in ops}) == len(ops) == len(lifts)

    # (a) both twins on their drawn outlines
    rooms, walls = [hall("L1")], []
    TW.carve_sub_spaces(rooms, [car("L1", 1, 1.0), car("L1", 2, 3.0)], walls)
    check(rooms, walls)
    # (b) one on its outline, the other stacked on the storey below
    below = [{"id": "r_L0_lift_b", "level_id": "L0", "label": "Asansör", "label_raw": "ASANSÖR", "room_type": "shaft",
              "polygon": [[2.2, 3.4], [3.8, 3.4], [3.8, 4.9], [2.2, 4.9]]}]
    rooms, walls = [hall("L1")] + copy.deepcopy(below), []
    TW.carve_sub_spaces(rooms, [car("L1", 1, 1.0)], walls)
    TW.carve_stacked_lifts(rooms, walls)
    check([r for r in rooms if r["level_id"] == "L1"], walls)
    # (c) both stacked
    below.append(dict(below[0], id="r_L0_lift_a", polygon=[[0.2, 3.4], [1.8, 3.4], [1.8, 4.9], [0.2, 4.9]]))
    rooms, walls = [hall("L1")] + copy.deepcopy(below), []
    TW.carve_stacked_lifts(rooms, walls)
    check([r for r in rooms if r["level_id"] == "L1"], walls)


def test_the_lifts_own_landing_door_tag_inside_the_shaft_is_no_veto():
    """19 Nov 2026 (review A4, A4C-05: the landing door's '90/210' written just behind the landing gap, inside the
    shaft's face, refused the lift)."""
    import copy

    from wenart.ingest import twins as TW

    box_ = {"id": "r_L0_oda", "level_id": "L0", "label": "Oda", "room_type": "unknown",
            "polygon": [[0, 0], [2.2, 0], [2.2, 2.6], [0, 2.6]]}
    hall = {"id": "r_L0_hall", "level_id": "L0", "label": "Kat Holü", "label_raw": "KAT HOLÜ", "room_type": "hall",
            "polygon": [[0, -2.0], [4.2, -2.0], [4.2, -0.2], [0, -0.2]]}
    car = {"id": "f_L0_1", "type": "unknown", "level_id": "L0",
           "footprint": {"center": [1.1, 1.3], "size": [1.85, 2.0], "rotation_deg": 0.0},
           "evidence": [{"file": "p.dxf", "method": "vector", "confidence": 0.9, "entity": "LINE:1,LINE:2"}]}
    gap = {"id": "o_L0_1", "level_id": "L0", "type": "opening", "wall_id": "w_s", "center": [1.1, -0.1], "width": 1.09}
    walls = [{"id": "w_s", "level_id": "L0", "start": [0, -0.1], "end": [4.2, -0.1], "thickness": 0.2}]
    for text, at, made in (("90/210", [1.1, 0.25], True), ("K:90/210", [1.0, 0.2], True),
                           ("K1 100/220", [1.9, 2.4], False)):
        rooms = [copy.deepcopy(box_), hall]
        TW.lift_cars(rooms, [], [copy.deepcopy(car)], [copy.deepcopy(gap)], copy.deepcopy(walls),
                     [{"text": text, "point": at, "level_id": "L0"}], [])
        assert (rooms[0]["room_type"] == "shaft") is made, text


def test_a_fill_in_a_drawn_square_is_that_outline_and_columns_and_mitred_pieces_stay_walls():
    """19 Nov 2026 (review A4, A4FC-2: real14's flues, a half hatch in each 25 x 25 cm square on 'baca', were dropped as
    symbols and the squares became tall cabinets; A4C-06: octagonal and hexagonal columns and mitred wall pieces were
    dropped, and a dark arrow came back through the dark fills)."""
    import math

    from shapely.geometry import Polygon

    from wenart.ingest.generic import symbols as SY
    from wenart.ingest.generic import walls as W
    from wenart.ingest.generic.model import GenericPage, Stroke

    def ngon(n, r, rot=0.0):
        return Polygon([(r * math.cos(rot + 2 * math.pi * k / n), r * math.sin(rot + 2 * math.pi * k / n))
                        for k in range(n)])

    assert not W.symbol_fill(ngon(8, 0.2, math.pi / 8)) and not W.symbol_fill(ngon(6, 0.2))       # columns
    assert not W.symbol_fill(Polygon([(0, 0), (0.9, 0), (0.65, 0.25), (0.25, 0.25)]))               # a 45-degree pier
    assert not W.symbol_fill(Polygon([(0, 0), (1.2, 0), (1.0, 0.2), (0, 0.2)]))                     # one mitre
    assert not W.symbol_fill(Polygon([(0, 0), (1.0, 0), (1.115, 0.2), (0.115, 0.2)]))               # a 60-degree wall
    assert W.symbol_fill(Polygon([(0, 0), (0.5, 0), (0.25, 0.25)]))                                 # an arrow head
    assert W.symbol_fill(Polygon([(0, 0), (0.25, 0.12), (0, 0.25), (0.02, 0.15), (-0.3, 0.15), (-0.3, 0.1),
                                  (0.02, 0.1)]))                                                    # a whole arrow

    def page(strokes):
        return GenericPage(file="p.dxf", page=1, source_kind="dxf", units="dxf", units_to_m=1.0, size=(10.0, 10.0),
                           strokes=strokes, wall_hint_layers=("duvar",))

    # two neighbouring flue squares on 'baca', each drawn with its diagonal, each half hatched on the wall layer
    squares = [Stroke(id=f"LWPOLYLINE:{k}", kind="polyline", layer="baca",
                      pts=[(x, 0), (x + 0.25, 0), (x + 0.25, 0.25), (x, 0.25), (x, 0), (x + 0.25, 0.25)])
               for k, x in ((1, 0.0), (2, 0.25))]
    halves = [Stroke(id=f"HATCH:9#{k}", kind="polyline", layer="duvar", closed=True, fill=(0.0, 0.0, 0.0),
                     pts=[(x, 0), (x + 0.25, 0), (x, 0.25)]) for k, x in ((0, 0.0), (1, 0.25))]
    arrow = Stroke(id="HATCH:7#0", kind="polyline", layer="duvar", closed=True, fill=(0.0, 0.0, 0.0),
                   pts=[(5.0, 5.0), (5.5, 5.0), (5.25, 5.25)])
    used: set = set()
    pg = page(squares + halves + [arrow])
    owners: dict = {}
    hatches = W._dxf_hatches(pg, 1.0, used, owners)
    assert [h.entity for h in hatches] == ["HATCH:9"] and len(hatches[0].polygons) == 2      # the flue stays wall
    assert "HATCH:7#0" in used                                         # the arrow is a symbol, used up ...
    assert W._dark_fills(pg, 1.0, used, owners) == []                  # ... and no dark fill either
    used2: set = set()
    pg2 = page(halves + [arrow])                                       # no squares drawn: lone triangles are symbols
    assert W._dxf_hatches(pg2, 1.0, used2, {}) == []
    # a flue's square is never furniture
    assert SY.layer_kind("baca") == "flue" and SY.NOT_FURNITURE_AS["flue"] == "flue"
    assert SY.layer_kind("ASANSOR SAFTI") == "other"


def test_one_machine_room_test_and_plant_words_with_word_ends():
    """19 Nov 2026 (review A4, POD-A4-01: real10's 13.3 m2 'Asansör Mahali' on the roof stayed a shaft for the reader
    while the lift rules took it for a machine room; A4C-07: 'PANORAMA ODASI', 'KLİMALI ODA', 'ELEK.ŞOH. YATAK ODASI',
    'ASANSÖR MAKSIMUM 8 KİŞİ' and 'MAKİNE DAİRESİZ ASANSÖR' were plant or machine rooms; SW-A4-04: real16's 'TEKNİK
    HACİM' was furnished as a work room)."""
    from wenart import building as B
    from wenart.ingest import twins as TW
    from wenart.reading_check import sense as SE

    assert B.room_type_for("Asansör Mahali", 13.3, 1.5) == "technical" and B.machine_room("Asansör Mahali", 13.3)
    assert B.room_type_for("ASANSÖR MAHALLİ", 1.6, 1.1) == "shaft" and not B.machine_room("ASANSÖR MAHALLİ", 1.6)
    big = {"id": "m", "level_id": "L7", "label": "Asansör Mahali", "room_type": "shaft", "area_computed": 13.3,
           "polygon": [[0, 0], [3.5, 0], [3.5, 3.8], [0, 3.8]]}
    small = dict(big, id="s", polygon=[[0, 0], [1.25, 0], [1.25, 1.3], [0, 1.3]], area_computed=1.6)
    assert TW._machine(big) and not TW._machine(small)
    assert SE.sense_type(big) == "technical" and SE.sense_type(small) == "lift"
    for label in ("TEKNİK HACİM", "TESİSAT HACMİ", "TEKNİK ALAN", "ELEKTRİK MAHALLİ", "ELK. PANO ODASI", "MOTOR ODASI",
                  "MOTOR ROOM", "JENERATÖR ODASI"):
        assert B.room_type_for(label) == "technical", label
    for label, rtype in (("PANORAMA ODASI", "other"), ("KLİMALI ODA", "other"), ("DEPOLU ODA", "storage"),
                         ("MAKİNA MÜHENDİSİ ODASI", "other"), ("ELEK.ŞOH. YATAK ODASI", "bedroom"),
                         ("YATAK ODASI KLİMA", "bedroom"), ("ODA (KLİMA)", "other"), ("ELEKTRIK", "other"),
                         ("MAKYAJ ODASI", "other"), ("ASANSÖR MAKSIMUM 8 KİŞİ", "shaft"),
                         ("MAKİNE DAİRESİZ ASANSÖR", "shaft"), ("ASANSÖR (MAKİNE DAİRESİZ)", "shaft")):
        assert B.room_type_for(label, 9.0, 1.2) == rtype, label


def test_a_face_line_under_a_plaster_coat_carries_the_face_whatever_a_tenth_of_a_millimetre():
    """19 Nov 2026 (review A4, POD-A4-03: real09 L2 kept a 0.73 m gap beside the chimney box that L0 and L1 closed: the
    masonry line, 3 cm inside the plaster face, stood 0.0301 m off it on L2 and 0.0299 m on L0)."""
    from wenart.ingest.generic import core as GC

    def run(shift):
        wall = _wall((5.5 + shift, 0.0), (5.5 + shift, 4.0), t=0.26, entity="w1")
        gap = _gap((5.5 + shift, 2.0), 0.73)
        # the east face: plaster through; the west face: plaster stops at the box, the masonry 3 cm inside runs through
        faces = [_line((5.63, 0.0), (5.63, 4.0), 1, layer="sıva"), _line((5.37, 0.0), (5.37, 1.2), 2, layer="sıva"),
                 _line((5.40, 0.0), (5.40, 4.0), 3, layer="duvar")]
        return GC._faces_through_gaps(_ex2(), "p", [wall], [gap], faces)[1]

    assert run(0.0) == [] and run(0.0001) == [] and run(-0.0001) == []
    # a single line on the axis covers neither face
    wall = _wall((5.5, 0.0), (5.5, 4.0), t=0.26, entity="w1")
    gap = _gap((5.5, 2.0), 0.73)
    assert GC._faces_through_gaps(_ex2(), "p", [wall], [gap], [_line((5.5, 0.0), (5.5, 4.0), 4, layer="duvar")])[1] \
        == [gap]


def test_terrain_from_the_ground_floors_own_plan_and_an_rc_check_for_it():
    """19 Nov 2026 (review A3, OA3-08, critical: real14's terrain was a TIN at +15 to +21 m from the '+ 3,50 kotu'
    heads of the sheets' finish tables and the roof terrace's marks, the ground floor buried; no reading check said
    so)."""
    from tests import _levels_fixture as F
    from wenart.levels import read as LR
    from wenart.reading_check import crossdoc as CD

    b = F.building()
    b["levels"].append(dict(b["levels"][0], id="L1", order=1, elevation=3.0, label="1. Kat"))
    b["walls"] += [dict(w, id=w["id"] + "_up", level_id="L1") for w in b["walls"] if w.get("level_id") == "L0"]
    params = __import__("wenart.levels.model", fromlist=["x"]).level_params(b)
    up = F.mark("lm_up", 21.5, kind=None, point=(8.0, -3.0), level="L1")
    title = F.mark("lm_t", 3.5, kind=None, point=(8.0, -4.0), level="L0")
    title["raw"] = "+ 3,50 kotu"
    ground = F.mark("lm_g", -0.45, kind=None, point=(8.0, -2.5), level="L0")
    b["levels"].append(dict(b["levels"][0], id="L-1", order=-1, elevation=-3.0, label="Bodrum Kat"))
    b["walls"] += [dict(w, id=w["id"] + "_b", level_id="L-1") for w in b["walls"] if w.get("level_id") == "L0"]
    garden = F.mark("lm_b", -3.5, kind=None, point=(8.0, -3.0), level="L-1")   # a basement's garden on a slope
    warnings = LR.classify([up, title, ground, garden], b, params)
    assert up["kind"] == "unknown" and title["kind"] == "unknown" and ground["kind"] == "ground_finished"
    assert garden["kind"] == "ground_finished"
    assert any("never a ground mark" in w for w in warnings)
    # the RC check: the terrain 18 m over the ground floor at its entrances
    ents = [{"door_id": "d1", "level_id": "L0", "threshold_z": 0.0, "ground_z": 18.4, "main": True, "centre": [1, 2]},
            {"door_id": "d2", "level_id": "L0", "threshold_z": 0.0, "ground_z": -0.15}]
    b2 = dict(b, site={"entrances": ents})
    f = CD.terrain_at_entrances(b2)
    assert len(f) == 1 and f[0]["severity"] == "critical" and f[0]["element_ids"] == ["d1"]
    ents[0]["main"] = False
    assert CD.terrain_at_entrances(b2)[0]["severity"] == "major"
    ents[0]["ground_z"] = -0.3
    assert CD.terrain_at_entrances(b2) == []


def test_an_open_air_rooms_mark_never_refuses_the_plan_frame_and_its_railing_gap_is_no_window():
    """19 Nov 2026 (review A4, A4C-02: a ground-floor terrace room marked ±0.00 refused the plan frame; A4FC-4: real18's
    railing gap on a balcony room was typed a window)."""
    from wenart.levels import model as M

    assert M._open_air({"room_type": "balcony"}) and M._open_air({"label": "TERAS"}) and not M._open_air(
        {"room_type": "living", "label": "SALON"})

    def frame(terrace_type):
        rooms = [{"id": "r_live", "level_id": "L0", "room_type": "living", "label": "Salon"},
                 {"id": "r_st", "level_id": "L0", "room_type": "stair", "label": "Merdiven"},
                 {"id": "r_ter", "level_id": "L0", "room_type": terrace_type,
                  "label": "Teras" if terrace_type == "balcony" else "Oda"}]
        b = {"rooms": rooms, "levels": [{"id": "L0", "order": 0, "elevation": 0.0}]}
        marks = [{"id": f"m{k}", "level_id": "L0", "kind": "floor", "room_id": rid, "z": z, "value": z}
                 for k, (rid, z) in enumerate((("r_live", 2.5), ("r_st", 2.5), ("r_ter", 0.0)))]
        marks.append({"id": "mt", "level_id": "L0", "kind": "threshold", "z": 2.5, "value": 2.5})
        return M._plan_frame(b, marks, b["levels"][0], 0.05, [], [])

    assert abs(frame("balcony") - 2.5) < 1e-9          # the terrace's ±0.00 is the garden's, not a room floor
    assert frame("living") == 0.0                      # an indoor room at ±0.00 keeps the marks as printed


def test_a_balcony_with_no_stated_area_closes_from_its_railing_further_away():
    """19 Nov 2026 (review A4, A4FC-3: real18 L0's south BALKON label stood 4.85 m from both legs of its L-shaped
    railing and became a 3 x 2.23 m rectangle past it)."""
    from shapely.geometry import box

    from wenart.levels import outdoor as OD

    facade = box(1.05, 0.0, 10.0, 8.0)
    # the L-shaped railing: south strip 9.9 x 1.45 m and an east leg up the facade; the corners meet within 1e-11
    rail = [{"id": "r1", "layer": "Merd&Balkon", "pts": [(1.05, 0.0), (1.05, -1.45)]},
            {"id": "r2", "layer": "Merd&Balkon", "pts": [(1.05, -1.45), (10.95, -1.45 + 1e-11)]},
            {"id": "r3", "layer": "Merd&Balkon", "pts": [(10.95, -1.45), (10.95, 5.675)]},
            {"id": "r4", "layer": "Merd&Balkon", "pts": [(10.95, 5.675), (10.0, 5.675)]}]
    got = OD.close_region((5.9, -1.11), rail, facade)
    assert got is not None and got["method"] == "strokes" and abs(got["area_m2"] - 19.75) < 0.2


def test_a_room_closed_along_its_own_outline_names_that_step_and_a_kitchen_sharing_its_balconys_face_is_found():
    """19 Nov 2026 (review A4, A4FC-5: such walls said 'glazed_facade'; A4FC-4: real18's south kitchen shared one face
    with its balcony and was never closed along its outline)."""
    from types import SimpleNamespace

    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic import facade as FC

    walls = [_wall((0, 0), (4, 0), t=0.2, entity="a"), _wall((4, 0), (4, 5), t=0.2, entity="b"),
             _wall((4, 5), (0, 5), t=0.2, entity="c"), _wall((0, 5), (0, 0), t=0.2, entity="d")]
    kitchen = SimpleNamespace(name="MUTFAK", anchor=(2.0, 3.5), exterior=False, room_type="kitchen")
    balcony = SimpleNamespace(name="BALKON", anchor=(2.0, 0.8), exterior=False, room_type="balcony")
    assert GC._shared_outdoor(walls, [], [kitchen, balcony]) == [(2.0, 3.5)]
    assert GC._shared_outdoor(walls, [], [kitchen]) == []
    from shapely.geometry import box

    new = FC.facade_wall_items(walls, [box(0.1, 1.6, 3.9, 4.9)], [], "p.dxf", 1, units_to_m=1.0,
                               rule="room_outline_closure", why=lambda mid, t: ("the room's own outline", "LWPOLY:9"))
    assert new and all(w.evidence["rule"] == "room_outline_closure" and w.evidence["entity"] == "LWPOLY:9"
                       and w.entity == "inferred:room_outline_closure" for w in new)
    assert GC.OPEN_OUTLINE_RULE == "room_outline_closure"


def test_a_confirmed_assumed_level_says_so_and_rc16_skips_a_top_floors_drawn_arrival():
    """19 Nov 2026 (review A4, SW-A4-05: real07's levels said level_mark while the warnings said assumed; SW-A4-03:
    RC16 planned real06's top-floor drawing of the stair below as a new stair of 0.43 m risers)."""
    from wenart.reading_check import crossdoc as CD
    from wenart.reading_check import stairs as ST

    b = {"levels": [{"id": "L0", "elevation": 0.0, "elevation_source": "level_mark", "order": 0}],
         "conflicts": []}
    sheets = {"heights": {"section_regions": ["r5"],
                          "levels": [{"level_id": "L0", "floor_z": {"method": "assumed", "value": 0.0}}]}}
    assert not [f for f in CD.rc9(b, sheets) if "is assumed" in f["message"]]
    b["levels"][0]["elevation_source"] = "assumed"
    assert [f for f in CD.rc9(b, sheets) if "is assumed" in f["message"]]

    def stair(fid, lv, x):
        flight = {"start": [x, 1.0], "end": [x + 2.5, 1.0], "width": 1.0, "lines": 7 if lv == "L1" else 18,
                  "spacing": 0.3}
        return {"id": fid, "level_id": lv, "type": "stair", "source": "from_documents",
                "footprint": {"center": [x + 1.25, 1.0], "size": [2.5, 1.0], "rotation_deg": 0.0},
                "stair": {"flights": [flight], "landing": None, "direction": [1.0, 0.0], "turn": "straight"}}

    bld = {"levels": [{"id": "L0", "elevation": 0.0}, {"id": "L1", "elevation": 3.0}], "walls": [],
           "slabs": [{"id": "s1", "above_level_id": "L1"}],
           "furniture": [stair("f_L0_001", "L0", 0.0), stair("f_L1_001", "L1", 0.0)]}
    rec = next(r for r in ST.stairs(bld) if r["id"] == "f_L1_001")
    assert rec["violations"] == [] and rec["arrives_from"] == "f_L0_001"


def test_a_headed_schedule_columns_last_cell_out_of_line_is_still_the_schedules():
    """19 Nov 2026 (review A3, OA3-13: real13's last 'MAHAL ADI' cell 'DAİRE GİR. HOL.', written 1.1 line heights left
    of the column, stayed a room label outside the walls on five floors)."""
    from wenart.ingest.generic import labels as LB

    cell = _run("DAİRE GİR. HOL.", 51.4, 10.0 - 0.5 * len(SCHEDULE), k=990)
    found = LB.schedules(_schedule_runs() + [cell])
    assert len(found) == 1 and found[0]["room_words"][-1] == "DAİRE GİR. HOL."
    plan = [_run("SALON", 2, 2, k=1), _run("MUTFAK", 2, 6, k=2), _run("YATAK ODASI", 6, 2, k=3)]
    assert sorted(b.name for b in LB.merge_label_blocks(plan + _schedule_runs() + [cell])) == \
        ["MUTFAK", "SALON", "YATAK ODASI"]
    # far below the column (more than a pitch), a label is no cell
    far = _run("DAİRE GİR. HOL.", 51.4, 10.0 - 0.5 * len(SCHEDULE) - 3.0, k=991)
    assert LB.schedules(_schedule_runs() + [far])[0]["room_words"][-1] == "ANTRE"


def test_rc3_compares_a_rooms_printed_area_with_its_area_less_its_stairs():
    """19 Nov 2026 (review A3, OA3-14: real15's 'Giriş Holü' 12.10 m2 against 17.5 m2 with its 5.80 m2 stair)."""
    from types import SimpleNamespace

    from wenart import reading_check as RC

    room = {"id": "r1", "label": "Giriş Holü", "polygon": [[0, 0], [5, 0], [5, 3.5], [0, 3.5]], "area_computed": 17.5}
    stair = {"id": "f1", "room_id": "r1", "type": "stair",
             "footprint": {"center": [4.0, 1.75], "size": [2.0, 2.9], "rotation_deg": 0.0}}
    page = SimpleNamespace(texts=[_run("GİRİŞ HOLÜ", 2.0, 2.0, k=1), _run("12.10 m2", 2.0, 1.6, k=2)])
    tf = [1, 0, 0, 0, 1, 0]
    assert [f for f in RC.area_findings(page, tf, [room], "L0") if f["severity"] == "major"]
    assert not [f for f in RC.area_findings(page, tf, [room], "L0", [stair]) if f["severity"] == "major"]


def test_a_lifts_void_label_names_its_shaft_not_a_slab_void():
    """19 Nov 2026 (review A3, OA3-03 (2): real13's 'ASANSÖR BOŞLUĞU', the lift's pit, became a slab void and its room
    an unlabelled 'Oda')."""
    from wenart import building as B

    assert not B.is_void_label("ASANSÖR BOŞLUĞU") and B.room_type_for("ASANSÖR BOŞLUĞU", 2.6, 1.0) == "shaft"
    assert B.is_void_label("GALERİ BOŞLUĞU") and B.is_void_label("BOŞLUK")


def test_rc9_names_a_level_whose_floor_marks_sit_off_it():
    """19 Nov 2026 (review A3, OA3-09 (5): real15's L1 at +7.82 m against five '+3.50' floor marks on its plan)."""
    from wenart.reading_check import crossdoc as CD

    b = {"levels": [{"id": "L0", "elevation": 0.0, "order": 0}, {"id": "L1", "elevation": 7.82, "order": 1,
                                                                   "elevation_source": "section"}],
         "rooms": [{"id": "r1", "level_id": "L1", "room_type": "living"}, {"id": "r2", "level_id": "L1",
                                                                          "room_type": "bedroom"}],
         "level_marks": [{"id": f"lm{k}", "kind": "floor", "room_id": rid, "z": 3.0, "point": [k, 0]}
                         for k, rid in enumerate(("r1", "r2"))]}
    f = CD.marks_off_levels(b)
    assert len(f) == 1 and f[0]["level_id"] == "L1" and f[0]["severity"] == "major"
    b["levels"][1]["elevation"] = 3.0
    assert CD.marks_off_levels(b) == []


def test_rc2_takes_the_axes_of_each_direction_apart():
    """19 Nov 2026 (review A3, OA3-10 (b): real13 L-2 lay 1.32 m off in y while its x axes matched; the pooled median
    of the axes of both directions said nothing)."""
    from wenart import reading_check as RC

    ref = {"axes": {"1": ("v", 1.0), "2": ("v", 5.0), "A": ("h", 2.0), "B": ("h", 6.0)},
           "stairs": [((3.0, 3.0), {0.12, 0.17, 0.2})]}
    off = {"axes": {"1": ("v", 1.0), "2": ("v", 5.0), "A": ("h", 0.68), "B": ("h", 4.68)},
           "stairs": [((3.0, 3.0), {0.12, 0.17, 0.2})]}
    out = RC.stacking({"L0": ref, "L-2": off}, "L0")
    assert [f["level_id"] for f in out] == ["L-2"] and abs(out[0]["offset_m"] - 1.32) < 0.01


def test_a_ground_mark_is_an_outlier_only_against_its_own_plans_marks():
    """19 Nov 2026 (review A3, OA3-08 follow-up: real13's street marks '+2.50' on its ground floor's plan fell 4 m off the
    median its basements' garden marks set on a steep site, and its entrance hall's door stood 3.9 m over the ground)."""
    from tests import _levels_fixture as F
    from wenart.levels import model as M

    b = F.building()
    b["site"] = {}
    marks = [F.mark("lm_s1", 0.0, kind="ground_finished", point=(2.0, -2.0), level="L0"),
             F.mark("lm_s2", 0.0, kind="ground_finished", point=(9.0, -2.0), level="L0")] + [
        F.mark(f"lm_g{k}", -6.5, kind="ground_finished", point=(x, 10.0), level="L-1")
        for k, x in enumerate((1.0, 5.0, 9.0))]
    warnings: list = []
    M._ground(b, marks, M.level_params(None), b["levels"][0], M.level_outline(b, "L0"), [], warnings)
    pts = b["site"]["ground"]["points"]
    assert len(pts) == 5 and all(p["used"] for p in pts), warnings
    # one plan's mark far off its own plan's others is still an outlier
    marks.append(F.mark("lm_x", 9.0, kind="ground_finished", point=(5.0, -3.0), level="L0"))
    marks.append(F.mark("lm_s3", 0.0, kind="ground_finished", point=(5.0, -2.0), level="L0"))
    b["site"] = {}
    M._ground(b, marks, M.level_params(None), b["levels"][0], M.level_outline(b, "L0"), [], warnings)
    assert [p["mark_id"] for p in b["site"]["ground"]["points"] if not p["used"]] == ["lm_x"]


def test_a_shaft_the_drawing_closes_on_one_storey_has_no_stop_there_and_undrawn_doors_are_inferred_everywhere():
    """20 Nov 2026 (coordinator, round 5: real17 L-1's closed shaft took the door of the storeys above; real13 L-2's
    'ASANSÖR BOŞLUĞU' got an inferred door): (2) the drawing draws the landing door on other storeys of the stacked
    shaft and closes this storey's faces: no stop, a review entry; (3) a void or pit label: no door; (4) no storey
    draws a door: the door is inferred on every storey."""
    import copy

    from wenart.ingest import twins as TW

    faces = [((11.92, 15.86), (13.92, 15.86)), ((13.92, 15.86), (13.92, 17.66)), ((13.92, 17.66), (11.92, 17.66)),
             ((11.92, 17.66), (11.92, 15.86)), ((14.17, 15.86), (14.17, 17.66))]
    frame = [((13.971, 16.049), (13.971, 17.449)), ((14.171, 16.049), (14.171, 17.449)),
             ((13.971, 16.049), (14.171, 16.049)), ((13.971, 17.449), (14.171, 17.449))]
    up, wu = _lift_core("L0")
    down, wd = _lift_core("L-1", depot=True)
    # (2) L0 draws its frame, L-1's drawn faces close the shaft
    ops, review = [], []
    notes = TW.lift_doors(copy.deepcopy(down + up), ops, wd + wu, (), [], review, {"L0": faces, "L-1": faces},
                          {"L0": frame})
    assert [o["level_id"] for o in ops] == ["L0"]
    assert review and review[0]["kind"] == "lift_no_stop" and review[0]["level_id"] == "L-1"
    assert any("no lift stop drawn" in n for n in notes)
    # ... a storey with no drawing of its own (a typical floor's copy) still takes the stacked door
    ops = []
    TW.lift_doors(copy.deepcopy(down + up), ops, wd + wu, (), [], [], {"L0": faces}, {"L0": frame})
    assert sorted(o["level_id"] for o in ops) == ["L-1", "L0"]
    # (3) the storey's label names the shaft's void or pit
    pit = copy.deepcopy(down)
    pit[0]["label"], pit[0]["label_raw"] = "Asansör Boşluğu", "ASANSÖR BOŞLUĞU"
    ops = []
    notes = TW.lift_doors(pit + copy.deepcopy(up), ops, wd + wu, (), [], [], {"L0": faces}, {"L0": frame})
    assert [o["level_id"] for o in ops] == ["L0"] and any("void or pit" in n for n in notes)
    # (4) no storey draws a landing door: inferred on both, though both storeys' faces are closed
    ops = []
    TW.lift_doors(copy.deepcopy(down + up), ops, wd + wu, (), [], [], {"L0": faces, "L-1": faces}, {})
    assert sorted(o["level_id"] for o in ops) == ["L-1", "L0"]


def test_everything_a_section_read_moves_into_the_storey_marks_frame_and_a_roof_under_its_floor_is_a_frame_error():
    """20 Nov 2026 (pre-pod check, R09-10: real09's A-A mapped 2 slab bands over 5 levels; the datum stayed the
    2.Normal's 8,50 and the roof was built 6 m low, in front of the L2 windows)."""
    from wenart.sheets import heights as HT
    from wenart.sheets import to_building as TB

    levels = [{"id": f"L{k}", "order": k, "kind": "floor"} for k in (-1, 0, 1, 2, 3)]
    v = lambda z: {"value": z, "method": "vector", "confidence": 1.0, "evidence": []}   # noqa: E731
    out = {"levels": [], "slabs": [], "datum": dict(v(8.5), relative=8.5),
           "roof": {"eaves_z": v(3.422), "ridge_z": v(6.508), "profile": [[0.0, 3.422], [5.0, 6.508]]},
           "ground": [{"side": "front", "z": v(-6.0)}],
           # the section's relative marks against the band z they point at: 6 m off the storey marks' frame
           "_mark_frame": [(0.0, -8.5), (2.5, -6.0), (5.5, -3.0), (8.5, 0.0), (11.5, 3.0)]}
    HT.apply_storey_marks(out, levels, {-1: 0.0, 0: 2.5, 1: 5.5, 2: 8.5, 3: 11.5}, 0.2, "x.dwg", "r6")
    assert out["datum"]["value"] == 2.5 and out["datum"]["relative"] == 2.5
    assert out["roof"]["eaves_z"]["value"] == 9.422 and out["roof"]["ridge_z"]["value"] == 12.508
    assert out["roof"]["profile"][0][1] == 9.422
    # the guard: a roof whose eaves stand under the floor of the level it covers is moved and named
    roof = {"over_level_id": "L3", "eaves_height": v(3.42), "ridge_height": v(6.5),
            "profile": {"points": [[0.0, 3.42], [5.0, 6.5]]}}
    lv = [{"id": "L3", "elevation": 9.0}]
    why = TB.roof_frame_guard(roof, lv, {"heights": {"roof": {"eaves_rise_m": 0.42}}})
    assert why and "frame error" in why and abs(roof["eaves_height"]["value"] - 9.42) < 1e-6
    assert abs(roof["ridge_height"]["value"] - 12.5) < 1e-6 and abs(roof["profile"]["points"][1][1] - 12.5) < 1e-6
    assert TB.roof_frame_guard(roof, lv, {}) is None                     # it stands right now


def test_a_dashed_beam_outline_makes_no_wall_and_a_leaf_touching_a_ring_is_still_a_leaf():
    """20 Nov 2026 (pre-pod check, R03-03: real03's entrance lobby was sealed off from the Kat Holü by a wall built from a
    HIDDEN2 overhead beam outline on 'MYD - IZ-1'; once it went, a bedroom door's leaf touching the flat's wall ring was
    cited with the ring and stayed a wall)."""
    from wenart.ingest.generic import openings as O
    from wenart.ingest.generic import walls as W
    from wenart.ingest.generic.model import GenericPage, Stroke
    from wenart.ingest.model import WallItem

    beam = Stroke(id="INSERT:1/86", kind="polyline", layer="D BLOK$0$MYD - IZ-1", closed=True,
                  linetype="D BLOK$0$HIDDEN2", pts=[(0.0, 0.0), (5.85, 0.0), (5.85, 0.35), (0.0, 0.35)])
    solid = Stroke(id="INSERT:1/87", kind="polyline", layer="DUVAR", closed=True, linetype="Continuous",
                   pts=[(0.0, 2.0), (5.85, 2.0), (5.85, 2.25), (0.0, 2.25)])
    assert W.dashed_stroke(beam) and not W.dashed_stroke(solid)
    page = GenericPage(file="p.dxf", page=1, source_kind="dxf", units="dxf", units_to_m=1.0, size=(10.0, 10.0),
                       strokes=[beam, solid])
    used: set = set()
    assert [p.entity for p in W._outline_walls(page, 1.0, used)] == ["INSERT:1/87"]
    # the leaf piece cites the wall ring it touches as well: still a leaf
    leaf = Stroke(id="INSERT:7/6/1/0", kind="polyline", layer="X$0$MYD - KAPI", closed=True,
                  pts=[(0.0, 0.0), (0.81, 0.0), (0.81, 0.06), (0.0, 0.06)])
    swing = Stroke(id="ARC:1", kind="arc", layer="X$0$MYD - KAPI",
                   pts=[(0.81 * __import__("math").cos(a / 20 * 1.5708), 0.81 * __import__("math").sin(a / 20 * 1.5708))
                        for a in range(21)],
                   arc={"center": (0.0, 0.0), "radius": 0.81, "start_deg": 0.0, "end_deg": 90.0})
    w = WallItem(start=(0.0, 0.03), end=(0.81, 0.03), thickness=0.06, box=[0, 0, 0, 0],
                 entity="ring:INSERT:7,INSERT:7/6/1/0", evidence={})
    assert O.leaf_walls([w], [leaf], [swing]) != {}
