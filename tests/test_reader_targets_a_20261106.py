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
    from wenart.sheets import levels as LV

    got = LV.storey_elevations([_mark_section()])
    assert got[0] == 0.5 and got[1] == 3.5                 # not the landing's +2.00 under 'ZEMİN KAT'
    sec = _mark_section()
    assert sorted(set(LV.floor_marks(sec, __import__("wenart.sheets.units_check", fromlist=["x"]).mark_texts(
        sec.texts), 0.0, 0.01))) == [0.0, 0.5, 3.5, 6.5]
    # without strokes (an old sheets reading) every mark counts, as before
    from types import SimpleNamespace
    assert LV.floor_marks(SimpleNamespace(texts=sec.texts), [], 0.0, 0.01) == []


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
    openings, walls = [], []
    TW.stair_cores(rooms, furniture)
    notes = TW.split_core_landings(rooms, openings, furniture, walls)
    for lid in ("L0", "L1", "L2"):
        got = sorted((r["label"], r["room_type"]) for r in rooms if r["level_id"] == lid)
        assert got == [("Asansör", "shaft"), ("Merdiven", "stair")], (lid, got)
    lifts = [r for r in rooms if r["label"] == "Asansör"]
    assert all(r["label_inferred"]["method"] == "sub_space" and not r.get("sub_spaces") for r in lifts)
    assert any("stacks on the lift" in r["label_inferred"]["reason"] for r in lifts)        # L1, L2: no label there
    assert not any(r.get("sub_spaces") for r in rooms) and openings == []                  # no open joint
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
    assert openings == [] and len(walls) == 2 and abs(walls[1].start[1] - 1.0) < 1e-6 and abs(walls[1].end[1] - 3.0) < 1e-6
    assert "a wall, not an opening" in ex.notes[-1]
    # one face broken at the gap (a real opening), or the lines on a furniture layer: the gap stays
    broken = [faces[0], _line((5.575, 0.0), (5.575, 1.0), 3, layer="Z_sıva"), _line((5.575, 3.0), (5.575, 4.0), 4,
                                                                                   layer="Z_sıva")]
    assert GC._faces_through_gaps(_ex2(), "p", [wall], [gap], broken)[1] == [gap]
    furn = [_line(a.pts[0], a.pts[1], 10 + k, layer="Z_tefriş") for k, a in enumerate(faces)]
    assert GC._faces_through_gaps(_ex2(), "p", [wall], [gap], furn)[1] == [gap]


def test_a_door_leafs_swing_in_an_unclassified_gap_makes_it_a_door():
    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic.model import Stroke

    wall = _wall((0.0, 3.0), (6.0, 3.0), t=0.25, entity="w1")
    gap = _gap((3.0, 3.0), 1.32)
    gap.rotation_deg = 0.0
    arc = Stroke(id="INSERT:9/23", kind="arc", pts=[(2.4, 3.0), (2.4, 2.3)], layer="KAPI", block="wererte",
                 arc={"center": (2.4, 3.0), "radius": 0.7, "start_deg": 270.0, "end_deg": 360.0})
    ex = _ex2()
    got = GC._door_blocks_in_gaps(ex, "p", [wall], [gap], [arc])
    assert got[0].kind == "door" and abs(got[0].width - 0.75) < 1e-6 and got[0].status == "verified"
    assert "door leaf's swing" in ex.notes[-1]
    # a sanitary arc (a basin) or a swing hinged far from the gap is no door
    basin = Stroke(id="ARC:5", kind="arc", pts=[(2.4, 3.0), (2.4, 2.3)], layer="Z_tefriş",
                   arc={"center": (2.4, 3.0), "radius": 0.7, "start_deg": 270.0, "end_deg": 360.0})
    assert GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap], [basin])[0].kind == "opening"
    far = Stroke(id="INSERT:9/24", kind="arc", pts=[(2.4, 1.0)], layer="KAPI",
                 arc={"center": (2.4, 1.5), "radius": 0.7, "start_deg": 270.0, "end_deg": 360.0})
    assert GC._door_blocks_in_gaps(_ex2(), "p", [wall], [gap], [far])[0].kind == "opening"


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
