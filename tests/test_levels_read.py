"""CPU tests of the reading of level marks into the building (docs/milestone12.md §3.1, B11; wenart/levels/read.py and
the pipeline hook wenart/ingest/generic/levels.py): marks and companions, the datum and its conflicts, the kind by
position, mark symbols out of the furniture, drawn ramps, and apply_levels on a pipeline build."""
from types import SimpleNamespace

import pytest

from wenart.ingest.model import LevelExtraction, TextItem
from wenart.levels import model as M
from wenart.levels import read as RD
from tests import _levels_fixture as F

P = M.level_params()


def _t(text, point, entity="TEXT:1", tag=None, level="L0"):
    ev = {"file": "t.dxf", "method": "vector", "confidence": 1.0, "entity": entity, "text": text}
    if tag:
        ev["attrib_tag"] = tag
    return {"text": text, "point": point, "level_id": level, "entity": entity, "evidence": ev, "attrib_tag": tag}


def test_marks_and_their_companions_in_one_block_reference_give_the_datum():
    texts = [_t("+0.00", (8.0, 1.0), "INSERT:7C9C9/48/attrib0", "KOT"),
             _t("93.20", (8.0, 0.8), "INSERT:7C9C9/48/attrib1"),           # no tag: a companion of the mark
             _t("93.20", (40.0, 40.0), "TEXT:loose"),                       # a bare number alone: no mark
             _t("SALON", (3.0, 4.0), "TEXT:2")]
    res = RD.read_marks(texts, F.building(), P)
    marks = res["marks"]
    assert [m["raw"] for m in marks] == ["+0.00", "93.20"]
    assert res["datum"]["value"] == 93.2 and res["datum"]["sources"] == ["lm_001+lm_002"]
    assert marks[1]["relative"] is True and marks[1]["value"] == 0.0 and marks[1]["absolute"] == 93.2
    assert marks[0]["group"] == "INSERT:7C9C9/48" and "datum" in marks[0]["used_for"]
    assert marks[0]["evidence"][0]["attrib_tag"] == "KOT"


def test_a_site_note_pair_gives_the_datum_and_absolute_marks_are_converted():
    texts = [_t("TESVİYE 0.00 KOTU : 93.20", (60.0, -20.0), "MTEXT:a"), _t("SB. KOTU : 93.65", (60.0, -21.0), "MTEXT:b"),
             _t("92.80", (20.0, -3.0), "ATTRIB:9", "KOT-ARAZI")]
    res = RD.read_marks(texts, F.building(), P)
    m = {x["raw"]: x for x in res["marks"]}
    assert res["datum"]["value"] == 93.2
    assert m["SB. KOTU : 93.65"]["value"] == pytest.approx(0.45) and m["SB. KOTU : 93.65"]["absolute"] == 93.65
    assert m["92.80"]["z"] == pytest.approx(-0.4) and m["92.80"]["kind_hint"] == "ground_natural"
    assert m["TESVİYE 0.00 KOTU : 93.20"]["note"] is True


def test_datums_that_disagree_are_a_conflict_and_without_a_datum_absolute_marks_are_not_used():
    texts = [_t("±0.00 = 93.20", (1, 1), "TEXT:a"), _t("±0.00 = 93.20", (5, 5), "TEXT:b"),
             _t("±0.00 = 95.00", (9, 9), "TEXT:c")]
    res = RD.read_marks(texts, F.building(), P)
    assert res["datum"]["value"] == 93.2
    assert res["conflicts"][0]["kind"] == "level_mark_mismatch" and "95.00" in res["conflicts"][0]["description"]
    res = RD.read_marks([_t("SB. KOTU : 93.65", (60, -20), "TEXT:z")], F.building(), P)
    assert res["datum"] is None and res["marks"][0]["z"] is None and any("no datum" in w for w in res["warnings"])
    sec = RD.read_marks([], F.building(), P, section={"levels": [{"level_id": "L0", "level_mark": {
        "value": 0.0, "method": "vector", "evidence": [{"file": "s.dxf", "method": "vector", "confidence": 1.0}]}}]})
    assert sec["marks"][0]["kind"] == "slab_top" and sec["marks"][0]["placement"] == "section"


def test_kind_by_position():
    b = F.building()
    texts = [_t("+0.00", (3.0, 4.0), "TEXT:room"),            # in the living room: its floor
             _t("-0.15", (8.0, -0.8), "TEXT:door"),           # outside, 0.7 m in front of the front door: threshold
             _t("-0.30", (3.0, -4.0), "TEXT:out"),            # outside, 4 m out: the ground
             _t("T.Z. -0.60", (-3.0, 4.0), "TEXT:tz"),        # outside with a keyword: natural ground
             _t("+44.80", (300.0, 0.0), "TEXT:far"),          # another drawing on the sheet
             _t("SB. KOTU : 93.65", (60.0, -20.0), "TEXT:n")]  # a site note: position-free
    res = RD.read_marks(texts, b, P)
    warnings = RD.classify(res["marks"], b, P)
    k = {m["evidence"][0]["entity"]: m for m in res["marks"]}
    assert k["TEXT:room"]["kind"] == "floor" and k["TEXT:room"]["room_id"] == "r_living"
    assert k["TEXT:door"]["kind"] == "threshold" and k["TEXT:door"]["door_id"] == "d_front"
    assert k["TEXT:out"]["kind"] == "ground_finished" and k["TEXT:out"]["side"] == "front"
    assert k["TEXT:tz"]["kind"] == "ground_natural" and k["TEXT:tz"]["side"] == "left"
    assert k["TEXT:far"]["kind"] == "unknown" and any("another drawing" in w for w in warnings)
    assert k["TEXT:n"]["kind"] == "plinth"


def _piece(pid, centre, size, ftype="unknown", entity="INSERT:7C9C9/48/0,INSERT:7C9C9/48/1"):
    return {"id": pid, "level_id": "L0", "room_id": "r_hall", "type": ftype, "type_raw": None,
            "source": "from_documents", "footprint": {"center": list(centre), "size": list(size), "rotation_deg": 0.0},
            "front_deg": None, "height": None, "asset": None, "status": "verified",
            "evidence": [{"file": "t.dxf", "method": "vector", "confidence": 0.9, "entity": entity}]}


def test_level_mark_symbols_leave_the_furniture():
    """real03 f_L0_142 (INSERT 7C9C9/48, 0.90 x 0.34 m, 'potted plant'): the block reference holds the mark."""
    b = F.building()
    b["furniture"] = [_piece("f_L0_142", (8.0, 6.0), (0.90, 0.34)),
                      _piece("f_lamp", (3.0, 4.0), (0.49, 0.49), "floor_lamp", "INSERT:9/1/0"),
                      _piece("f_bed", (3.0, 6.0), (2.0, 1.6), "bed_double", "INSERT:9/2/0")]
    texts = [_t("+0.00", (8.1, 6.2), "INSERT:7C9C9/48/attrib0", "KOT"),
             _t("+0.00", (3.05, 4.0), "TEXT:lamp"),           # a mark text on a small untyped-looking piece
             _t("+0.00", (3.0, 6.3), "TEXT:bed")]             # a mark over a bed: the bed stays
    marks = RD.read_marks(texts, b, P)["marks"]
    moved = {m["piece_id"]: m for m in RD.mark_symbols(b, marks)}
    assert set(moved) == {"f_L0_142", "f_lamp"}
    sym = moved["f_L0_142"]["symbol"]
    assert sym["kind"] == "level_mark" and sym["former_piece_id"] == "f_L0_142" and sym["id"] == "sym_f_L0_142"
    assert "block reference" in sym["reason"] and len(sym["evidence"]) == 2


def test_drawn_ramp_texts():
    b = F.building()
    ramps = RD.drawn_ramps([_t("RAMPA %8", (9.5, -2.0), "TEXT:r"), _t("RAMPA", (3.0, 4.0), "TEXT:in")], b, P)
    assert [(r["door_id"], r["text"]) for r in ramps] == [("d_front", "RAMPA %8")]


def _work(texts, transform=(1, 0, 0, 0, 1, 0)):
    ex = LevelExtraction(file="t.dxf", page=1, level_id="L0", units="dxf", transform_to_building=list(transform))
    for k, (text, (x, y), entity, tag) in enumerate(texts):
        ev = {"file": "t.dxf", "method": "vector", "confidence": 1.0, "entity": entity, "text": text}
        if tag:
            ev["attrib_tag"] = tag
        ex.texts.append(TextItem(text=text, start=(x, y), box=[x - 0.1, y - 0.1, x + 0.1, y + 0.1], rotation_deg=0.0,
                                 entity=entity, height=0.2, evidence=ev))
    return SimpleNamespace(record=SimpleNamespace(level_id="L0", format="dxf", page=1), extraction=ex)


def test_apply_levels_on_a_pipeline_build():
    from wenart.ingest import pipeline as PL
    from wenart.ingest.generic import levels as LV
    b = F.building()
    b["furniture"] = [_piece("f_L0_142", (8.0, 6.0), (0.90, 0.34))]
    build = PL.ProjectBuild(b)
    works = {("t.dxf", 1): _work([("+0.00", (8.1, 6.2), "INSERT:7C9C9/48/attrib0", "KOT"),
                                  ("93.20", (8.1, 5.9), "INSERT:7C9C9/48/attrib1", "KOT2"),
                                  ("TESVİYE 0.00 KOTU : 93.20", (40.0, -20.0), "MTEXT:n", None),
                                  ("RAMPA", (9.0, -2.0), "TEXT:r", None)])}
    LV.apply_levels(build, works)
    assert build.building is b                                   # updated in place (the pipeline keeps the dict)
    assert [f["id"] for f in b["furniture"]] == [] and b["symbols"][0]["former_piece_id"] == "f_L0_142"
    assert b["project"]["datum"]["value"] == 93.2 and b["project"]["datum"]["method"] == "vector"
    kinds = sorted(m["kind"] for m in b["level_marks"])
    assert kinds == ["floor", "floor", "ground_finished"]
    assert b["site"]["ground"]["source"] == "site_note" and b["roof"]["kind"] == "flat_cut"
    e = b["site"]["entrances"][0]
    assert e["door_id"] == "d_front" and e["solution"] == "none" and e["rise"] == 0.0     # flush, as drawn
    assert any(w.startswith("levels: 3 level mark(s) read") for w in b["warnings"])
    assert not [c for c in build.raw_conflicts if c["kind"] == "level_mark_mismatch"]
    from wenart import building as B
    assert not B.validation_errors(b)


def test_apply_levels_without_marks_still_fills_the_levels():
    from wenart.ingest import pipeline as PL
    from wenart.ingest.generic import levels as LV
    b = F.building()
    build = PL.ProjectBuild(b)
    LV.apply_levels(build, {})
    assert b["level_marks"] == [] and b["site"]["ground"]["source"] == "D3a"
    assert "levels: no level mark read; ground: D3a; 1 entrance(s): d_front steps" in b["warnings"]
