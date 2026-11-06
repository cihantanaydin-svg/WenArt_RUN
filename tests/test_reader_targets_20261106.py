"""The Milestone 14 reader targets of 6 Nov 2026 (found by the machine reviewers on current readings, verified by blind
judges), each a general rule with the project that showed it as its test case only (user rule of 26 Oct 2026: "fix
should be general ... don't ever forget that"):

1. model-space ATTDEFs are texts (real18: OTOPARK, A:102.52M2 and the room names of two floors are ATTDEF tags);
2. the sheet frame is notation and the paper no room (real19: four frame walls on the region box and a 441 m2 room;
   real15: the frame on layer 'Z_antet' closed the whole sheet as one 1257 m2 room);
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
# 2. The sheet frame is notation, the paper is no room
# --------------------------------------------------------------------------

def test_frame_and_title_block_layers_are_named_in_the_sheets_vocabulary():
    from wenart.sheets import split as SP

    for name in ("Z_antet", "A_Antet", "A_Cerceve", "PAFTA", "A-ANNO-TTLB-FRAME", "BORDER", "Schriftfeld",
                 "CARTOUCHE", "TITLE"):
        assert SP.is_frame_layer(name), name
    for name in ("A-GLAZ-FRAME", "DOOR_FRAME", "PENCERE ÇERÇEVESİ", "FRAMING", "DUVAR", "0", "03_Yazı", "KAPI KASA"):
        assert not SP.is_frame_layer(name), name


def _page_with(strokes):
    from wenart.ingest.generic.model import GenericPage

    return GenericPage(file="p.dxf", page=1, source_kind="dxf", units="dxf", units_to_m=1.0, size=(40, 40),
                       strokes=strokes)


def _ex():
    from wenart.ingest.model import LevelExtraction

    ex = LevelExtraction(file="p.dxf", page=1, level_id="L0", units="dxf", page_size=[40.0, 40.0])
    ex.report = {}
    return ex


def test_walls_drawn_only_on_frame_layers_are_notation_after_the_walls_are_read():
    """real15: the sheet frame (with the title block's notch) on layer 'Z_antet' was read as walls and closed the sheet as
    one room. The walls drawn only by frame-layer strokes go; the walls of any other layer stay, and the wall layers
    are still chosen by evidence first (the rule runs on the walls read)."""
    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic.model import Stroke
    from wenart.ingest.model import OpeningItem

    frame_st = Stroke(id="LWPOLYLINE:F", kind="polyline", pts=[(0, 0), (30, 0), (30, 20), (0, 20), (0, 0)],
                      closed=True, layer="Z_antet")
    wall_st = Stroke(id="LINE:W", kind="line", pts=[(5, 5), (15, 5)], layer="Z_ duvar")
    frame = _box_walls(0, 0, 30, 20, 0.1, tag="f")
    for w in frame:
        w.entity, w.evidence["layer"] = "LWPOLYLINE:F", "Z_antet"
    house = _box_walls(5, 5, 15, 12, tag="h") + [_wall((5 + k, 5), (5 + k, 12), 0.1, f"p{k}") for k in range(1, 10)]
    for w in house:
        w.entity, w.evidence["layer"] = "LINE:W", None
    ex = _ex()
    kept = GC._drop_frame_walls(ex, "p.dxf", _page_with([frame_st, wall_st]), frame + house, [], 1.0)
    assert [w.entity for w in kept] == ["LINE:W"] * 13
    assert ex.report["frame_layers"]["layers"] == ["Z_antet"] and ex.report["frame_layers"]["walls"] == 4
    # a frame-layer wall carrying an opening is a wall; a plan drawn on its 'PAFTA' layer keeps its walls
    door = OpeningItem("door", 0.9, (15.0, 0.05), 0.0, [0, 0, 0, 0], "d", {})
    ex2 = _ex()
    assert len(GC._drop_frame_walls(ex2, "p.dxf", _page_with([frame_st, wall_st]), frame + house, [door], 1.0)) == 14
    for w in house:
        w.evidence["layer"] = "PAFTA-01"
    ex3 = _ex()
    assert len(GC._drop_frame_walls(ex3, "p.dxf", _page_with([wall_st]), house, [], 1.0)) == 13
    assert "kept as the plan's walls" in ex3.notes[-1]


def test_walls_on_the_region_box_with_no_opening_and_no_join_are_the_sheet_frame():
    from types import SimpleNamespace

    from wenart.ingest.generic import core as GC
    from wenart.ingest.model import LevelExtraction, OpeningItem

    house = _box_walls(5, 5, 15, 12, tag="h") + [_wall((10, 5), (10, 12), 0.1, "h5")]
    frame = _box_walls(0, 0, 30, 20, 0.05, tag="f")
    page = SimpleNamespace(region_box=(0.0, 0.0, 3000.0, 2000.0), strokes=[])        # drawing units (cm)
    ex = LevelExtraction(file="p.dxf", page=1, level_id="L1", units="dxf", page_size=[30.0, 20.0])
    ex.report = {}
    kept = GC._drop_frame_walls(ex, "p.dxf", page, house + frame, [], 0.01)
    assert [w.entity for w in kept] == [w.entity for w in house]
    assert ex.report["frame_walls"]["walls"] == 4 and ex.report["frame_walls"]["share"] > 0.99
    # a building drawn tight in its box: its outer walls carry a window and the inner wall ends on them -> kept
    tight = _box_walls(0, 0, 10, 7, tag="t") + [_wall((5, 0.2), (5, 6.8), 0.1, "t5")]
    window = OpeningItem("window", 1.2, (2.5, 0.1), 0.0, [0, 0, 0, 0], "w", {})
    ex2 = LevelExtraction(file="p.dxf", page=1, level_id="L1", units="dxf", page_size=[10.0, 7.0])
    ex2.report = {}
    assert len(GC._drop_frame_walls(ex2, "p.dxf", SimpleNamespace(region_box=(0, 0, 1000, 700), strokes=[]), tight, [window],
                                    0.01)) == 5
    assert "kept" in ex2.notes[-1] and "frame_walls" not in ex2.report


def test_clip_page_keeps_the_region_box_for_the_core(tmp_path):
    doc = _doc()
    doc.modelspace().add_line((0, 0), (100, 0))
    page = DG.read_page(_save(doc, tmp_path), "plan.dxf", region_box=(-10, -10, 200, 50))
    assert page.region_box == (-10.0, -10.0, 200.0, 50.0)
    assert DG.read_page(_save(doc, tmp_path, "b.dxf"), "b.dxf").region_box is None


def test_a_face_covering_the_region_box_with_other_rooms_labels_is_no_room():
    from wenart.ingest import rooms as R

    walls = _box_walls(0, 0, 30, 20)                       # the frame closed as one face: 29.6 x 19.6 m
    labels, points = _labels(("MUTFAK", (5, 5)), ("SALON", (12, 5)), ("YATAK ODASI", (20, 12)))
    res = R.derive_rooms("L0", walls, labels, points, None, "p.dxf", region_box=[0, 0, 30, 20])
    assert res.rooms == [] and len(res.unplaced_labels) == 3
    assert res.paper_faces and sorted(res.paper_faces[0]["labels"]) == ["MUTFAK", "SALON", "YATAK ODASI"]
    # the same face with its own name and one other label, or without the region box, stays a room
    two, pts2 = _labels(("MUTFAK", (5, 5)), ("SALON", (12, 5)))
    assert len(R.derive_rooms("L0", walls, two, pts2, None, "p.dxf", region_box=[0, 0, 30, 20]).rooms) == 1
    assert len(R.derive_rooms("L0", walls, labels, points, None, "p.dxf").rooms) == 1
    # a building filling a tight box with one terrace label is a room (synthetic-21's roof terrace)
    one, pts1 = _labels(("TERAS", (5, 5)),)
    assert len(R.derive_rooms("L0", walls, one, pts1, None, "p.dxf", region_box=[0, 0, 30, 20]).rooms) == 1


def test_sense_uses_the_readers_frame_rule():
    from wenart.ingest.generic import frame as FR
    from wenart.reading_check import sense as SE

    assert SE.frame_walls is FR.frame_walls and SE.FRAME_SHARE_MIN == FR.FRAME_SHARE_MIN == 0.60
    assert SE.FRAME_TOL_M == FR.FRAME_TOL_M == 0.10 and SE.FRAME_JOINS_MAX == FR.FRAME_JOINS_MAX == 2


# --------------------------------------------------------------------------
# 3. Notation is split off a label before naming
# --------------------------------------------------------------------------

def test_notation_phrases_are_split_off_a_label_line():
    from wenart.ingest.generic import labels as LB

    assert LB.split_notation("TESİSAT DUVARI H: 1.20 Cm")[0] == ""
    assert LB.split_notation("Bına Taban Hattı Yatak Odası")[0] == "Yatak Odası"
    assert LB.split_notation("BİNA TABAN HATTI")[0] == ""
    assert LB.split_notation("SAÇAK İZDÜŞÜMÜ")[0] == "" and LB.split_notation("SAÇAK")[0] == ""
    assert LB.split_notation("GİRİŞ SAÇAK")[0] == "GİRİŞ SAÇAK"          # a canopy, an outdoor space (real11)
    assert LB.split_notation("SAÇAK ALTI")[0] == "SAÇAK ALTI"
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
