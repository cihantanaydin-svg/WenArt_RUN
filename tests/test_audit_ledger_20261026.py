"""The source ledger, line 1 of the auditor (26 Oct 2026; user: "the audit is very weak, only the looks being judged,
everything needs to be judged. There was a veranda in real06, it has been fully missed ... think to solve issues like
veranda"). The pipeline writes an inventory of the documents' items (``wenart.ingest.source_items``,
``<out>/source_items.json``); ``wenart.audit.ledger`` checks that each meaningful item is used by the model or
explained by a logged reason. General rules, tested on real06's trimmed reading (the veranda texts TEXT:29585C /
TEXT:29585D and its unbuilt site area) and on hand-made inputs (CPU)."""
from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from wenart.audit import ledger as L
from wenart.ingest import source_items as SI
from wenart.ingest.generic.labels import LabelBlock
from wenart.ingest.generic.model import GenericPage, Stroke, TextRun
from wenart.ingest.model import TextItem

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "real06_ledger_20261026.json"


def _real06():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return data["building"], data["source_items"]


def _by_target(result: dict) -> dict:
    return {f["target"]: f for f in result["findings"]}


# --------------------------------------------------------------------------
# real06: the veranda
# --------------------------------------------------------------------------

def test_real06_veranda_is_a_critical_finding_with_its_evidence():
    building, items = _real06()
    f = _by_target(L.ledger(building, items))["sa_L0_veranda"]
    assert (f["line"], f["check"], f["severity"], f["owner"]) == ("source", "A1", "critical", "site")
    ev = f["evidence"]
    assert (ev["file"], ev["entity"], ev["layer"], ev["text"], ev["level_id"]) == \
        ("real06.dwg", "TEXT:29585C", "YAZıMAHAL", "VERANDA", "L0")
    assert ev["position"] == pytest.approx([1.99, 0.909], abs=0.01)
    assert "VERANDA" in f["message"] and "builds nothing" in f["message"]
    assert "A2" in f["also"]                                  # the unbuilt site area, carried by the same finding
    assert {"entity": "TEXT:29585D", "text": "22,80m²"} in f["related"]
    assert any("recorded in site" in w for w in f["warnings"])
    fix = f["fix"]
    assert (fix["action"], fix["kind"], fix["level_id"], fix["element_id"]) == \
        ("build_outdoor_space", "veranda", "L0", "sa_L0_veranda")
    assert fix["area_m2"] == pytest.approx(22.8)
    # The railing on layer BALKON (read as site decor of kind "other", never built) gives the outline hint.
    assert fix["railing_layer"] == "BALKON" and len(fix["polygon_hint"]) >= 3
    from shapely.geometry import Polygon
    assert Polygon(fix["polygon_hint"]).area == pytest.approx(22.8, rel=0.3)


def test_real06_upper_balcony_the_site_dropped_is_critical():
    building, items = _real06()
    f = _by_target(L.ledger(building, items))["TEXT:295843"]
    assert (f["check"], f["severity"], f["evidence"]["text"], f["evidence"]["level_id"]) == \
        ("A1", "critical", "BALKON", "L1")
    assert "no element of the model uses it" in f["message"]
    assert any("areas read outside the walls of L1 not used" in w for w in f["warnings"])
    assert f["fix"]["area_m2"] == pytest.approx(11.8)


def test_real06_merged_labels_hall_in_kitchen_major_dining_in_living_minor():
    building, items = _real06()
    found = _by_target(L.ledger(building, items))
    antre = found["r_L0_mutfak:TEXT:294BCF"]
    assert (antre["check"], antre["severity"], antre["fix"]["action"], antre["fix"]["room_id"]) == \
        ("A3", "major", "split_room", "r_L0_mutfak")
    assert found["r_L0_salon:TEXT:295858"]["severity"] == "minor"     # YEMEK BÖLÜMÜ: open plan


def test_real06_noise_is_counted_never_a_finding():
    building, items = _real06()
    result = L.ledger(building, items)
    targets = set(_by_target(result))
    for t in items["texts"]:
        if L.classify_text(t) in ("dimension", "grid", "opening_tag", "number", "title", "note"):
            assert t["id"] not in targets, t
    cov = result["coverage"]["by_kind"]
    assert cov["text:dimension"]["must"] == 0 and cov["text:dimension"]["items"] >= 1
    assert cov["text:level_mark"]["accounted"] == cov["text:level_mark"]["items"]   # the marks the levels read
    assert result["items"] >= result["accounted"] > 0


def test_real06_built_veranda_clears_the_finding():
    building, items = _real06()
    poly = [[-0.5, -1.8], [4.6, -1.8], [4.6, 3.5], [-0.5, 3.5]]
    built = copy.deepcopy(building)
    built["site"]["paving"] = [{"id": "sp_veranda", "polygon": poly, "area_id": "sa_L0_veranda", "build": True}]
    assert "sa_L0_veranda" not in _by_target(L.ledger(built, items))
    as_room = copy.deepcopy(building)
    as_room["site"]["areas"] = []
    as_room["rooms"].append({"id": "r_L0_veranda", "level_id": "L0", "label": "Veranda", "label_raw": "VERANDA",
                             "room_type": "balcony", "polygon": poly,
                             "evidence": [{"file": "real06.dwg", "method": "vector", "confidence": 1.0,
                                           "entity": "TEXT:29585C", "text": "VERANDA"}]})
    found = _by_target(L.ledger(as_room, items))
    assert "sa_L0_veranda" not in found and "TEXT:29585C" not in found
    # An outdoor space built by a later stage in a list of its own, from the site area's evidence.
    own_list = copy.deepcopy(building)
    own_list["outdoor_spaces"] = [{"id": "os_L0_veranda", "level_id": "L0", "kind": "veranda", "polygon": poly,
                                   "evidence": copy.deepcopy(building["site"]["areas"][0]["evidence"])}]
    found = _by_target(L.ledger(own_list, items))
    assert "sa_L0_veranda" not in found and "TEXT:29585C" not in found


# --------------------------------------------------------------------------
# Vocabulary and text kinds
# --------------------------------------------------------------------------

@pytest.mark.parametrize("text, kind", [
    ("VERANDA", "veranda"), ("Verandası", "veranda"), ("KIŞ BAHÇESİ", "winter_garden"),
    ("Wintergarten", "winter_garden"),
    ("TERAS", "terrace"), ("Çatı Terası", "terrace"), ("Terrasse", "terrace"), ("GÜNEŞLENME ALANI", "terrace"),
    ("BALKON", "balcony"), ("Balcony", "balcony"), ("SUNDURMA", "porch"), ("Porch", "porch"), ("Patio", "patio"),
    ("AVLU", "patio"), ("Deck", "deck"), ("Loggia", "loggia"), ("Pergola", "pergola"), ("24M2 HAVUZ", "pool"),
    ("Swimming pool", "pool"), ("OTOPARK ALANI", "parking"), ("Carport", "parking"), ("BAHÇE", "garden"),
])
def test_outdoor_space_vocabulary(text, kind):
    assert L.outdoor_kind(text)[0] == kind


@pytest.mark.parametrize("text", ["SALON", "Mutfak", "Kitchen", "Deckenhöhe", "Poolside lamp shade x", "Brüt Alan ="])
def test_not_outdoor_spaces(text):
    assert L.outdoor_kind(text) is None or L.classify_text({"text": text}) == "note"


@pytest.mark.parametrize("row, kind", [
    ({"text": "Brüt Alan = 120,50 m²", "role": "room_label", "label_part": "name"}, "note"),
    ({"text": "Daire Tipi Net Alan =", "role": "room_label"}, "note"),
    ({"text": "+0,50", "layer": "kot yazıları"}, "level_mark"),
    ({"text": "±0,00"}, "level_mark"),
    ({"text": "22,80m²"}, "area"),
    ({"text": "345", "role": "dimension"}, "dimension"),
    ({"text": "A", "layer": "AKS YAZI"}, "grid"),
    ({"text": "230", "layer": "kapı pen. yazısı"}, "opening_tag"),
    ({"text": "çamaşır mak.", "layer": "kapı pen. yazısı"}, "furniture_name"),
    ({"text": "BANYO"}, "space_name"),
    ({"text": "VERANDA"}, "outdoor_space"),
    ({"text": "Ölçek 1/50"}, "note"),
])
def test_text_kinds(row, kind):
    assert L.classify_text(row) == kind


def test_entity_ids_ranges_and_block_paths():
    assert L.expand_entities("LINE:295900-295902,ARC:2A") == ["LINE:295900", "LINE:295901", "LINE:295902", "ARC:2A"]
    keys = L.id_keys("INSERT:4B[2]/3/0")
    assert {"INSERT:4B[2]/3/0", "INSERT:4B[2]/3", "INSERT:4B[2]", "INSERT:4B", "INSERT:4B/3"} <= keys
    assert {"LWPOLYLINE:2F:1", "LWPOLYLINE:2F"} <= L.id_keys("LWPOLYLINE:2F:1")
    assert "HATCH:5C" in L.id_keys("HATCH:5C#0")
    assert SI.entity_id("LWPOLYLINE:2F:1") == "LWPOLYLINE:2F" and SI.entity_id("INSERT:4B/3#0") == "INSERT:4B/3"


# --------------------------------------------------------------------------
# Hand-made inputs: one rule each
# --------------------------------------------------------------------------

SQ = [[0, 0], [5, 0], [5, 4], [0, 4]]


def _ev(entity, text=None, method="vector"):
    out = {"file": "x.dwg", "method": method, "confidence": 1.0, "entity": entity}
    if text:
        out["text"] = text
    return out


def _building(**kw) -> dict:
    b = {"project": {"id": "t"}, "levels": [{"id": "L0"}], "walls": [], "openings": [], "rooms": [], "furniture": [],
         "site": {"areas": [], "decor": []}, "warnings": [], "needs_review": [], "symbols": [], "level_marks": [],
         "conflicts": []}
    b.update(kw)
    return b


def _room(rid, label, poly=SQ, text_id=None, room_type="living", level="L0"):
    ev = [_ev(text_id, label)] if text_id else [_ev("derived-from:w_1", method="inferred")]
    return {"id": rid, "level_id": level, "label": label, "label_raw": label, "room_type": room_type,
            "polygon": poly, "evidence": ev}


def _page(**kw) -> dict:
    p = {"id": "p1", "file": "x.dwg", "page": 1, "format": "dwg", "class": "floor_plan", "region_id": None,
         "region_class": None, "level_id": "L0", "read": True, "skip_reason": None}
    p.update(kw)
    return p


def _t(tid, text, pos, **kw) -> dict:
    t = {"id": tid, "page": "p1", "text": text, "layer": "YAZI", "pos": list(pos), "role": "other", "label": None,
         "label_part": None, "label_id": None}
    t.update(kw)
    return t


def _items(**kw) -> dict:
    it = {"schema": SI.SCHEMA, "pages": [_page()], "texts": [], "blocks": [], "containers": [], "layers": [],
          "hatches": [], "outlines": []}
    it.update(kw)
    return it


def test_a_room_label_no_room_uses_is_critical():
    b = _building(rooms=[_room("r_salon", "SALON", text_id="TEXT:1")])
    items = _items(texts=[_t("TEXT:1", "SALON", (2, 2), role="room_label", label="SALON", label_part="name",
                             label_id="TEXT:1"),
                          _t("TEXT:2", "MUTFAK", (12, 2), role="room_label", label="MUTFAK", label_part="name",
                             label_id="TEXT:2"),
                          _t("TEXT:3", "12,00m²", (12, 1.7), role="room_label", label="MUTFAK", label_part="area",
                             label_id="TEXT:2")])
    found = _by_target(L.ledger(b, items))
    f = found["TEXT:2"]
    assert (f["check"], f["severity"], f["fix"]["action"], f["fix"]["area_m2"]) == ("A1", "critical", "add_room", 12.0)
    assert "TEXT:3" not in found and "TEXT:1" not in found          # its area joins it; SALON is a room


def test_an_outdoor_word_the_reading_did_not_take_as_a_label_is_still_found():
    """SUNDURMA is no room keyword of the reading: the ledger's own vocabulary finds it."""
    b = _building(rooms=[_room("r_salon", "SALON", text_id="TEXT:1")])
    items = _items(texts=[_t("TEXT:1", "SALON", (2, 2), role="room_label", label="SALON", label_part="name",
                             label_id="TEXT:1"),
                          _t("TEXT:9", "SUNDURMA", (2, -1.5))])
    f = _by_target(L.ledger(b, items))["TEXT:9"]
    assert (f["check"], f["severity"], f["fix"]["kind"]) == ("A1", "critical", "porch")


def test_items_on_pages_not_read_or_not_plans_need_not_be_used():
    b = _building()
    items = _items(pages=[_page(), _page(id="p2", **{"class": "section", "read": False,
                                                     "skip_reason": "section: read for the heights"})],
                   texts=[_t("TEXT:9", "BALKON", (2, -1.5), page="p2")])
    result = L.ledger(b, items)
    assert not [f for f in result["findings"] if f["check"] in ("A1", "A8")]


def test_unbuilt_piece_needs_a_logged_reason():
    piece = {"id": "f_L0_001", "level_id": "L0", "type": "unknown", "build": False,
             "footprint": {"center": [1, 1], "size": [0.5, 0.5]}, "evidence": [_ev("LINE:1,LINE:2")]}
    found = _by_target(L.ledger(_building(furniture=[piece]), _items()))
    assert (found["f_L0_001"]["check"], found["f_L0_001"]["severity"]) == ("A2", "major")
    warned = _building(furniture=[piece], warnings=["f_L0_001: not built (rug or group outline): outline 2 x 1 m"])
    assert "f_L0_001" not in _by_target(L.ledger(warned, _items()))
    reasoned = _building(furniture=[dict(piece, not_built_reason="detail inside a kitchen counter leg")])
    assert "f_L0_001" not in _by_target(L.ledger(reasoned, _items()))


def test_an_unbuilt_space_needs_more_than_no_outline():
    area = {"id": "sa_L0_teras", "level_id": "L0", "label": "TERAS", "label_raw": "TERAS", "polygon": None,
            "anchor": [2.0, -2.0], "kind": "terrace", "build": False, "note": "no outline: not a room",
            "evidence": [_ev("TEXT:7", "TERAS")]}
    f = _by_target(L.ledger(_building(site={"areas": [area], "decor": []}), _items()))["sa_L0_teras"]
    assert (f["check"], f["severity"], f["fix"]["action"]) == ("A2", "critical", "build_outdoor_space")
    dup = dict(area, note="duplicate of sa_L0_teras_2 (the same label drawn twice)")
    assert "sa_L0_teras" not in _by_target(L.ledger(_building(site={"areas": [dup], "decor": []}), _items()))


def test_a_level_mark_no_level_mark_uses_is_found():
    items = _items(texts=[_t("TEXT:5", "+0,50", (1, 1), layer="kot")])
    f = _by_target(L.ledger(_building(), items))["TEXT:5"]
    assert (f["check"], f["severity"], f["owner"], f["fix"]["value"]) == ("A5", "major", "levels", 0.5)
    read = _building(level_marks=[{"id": "lm_001", "value": 0.5, "evidence": [_ev("TEXT:5", "+0,50")]}])
    assert "TEXT:5" not in _by_target(L.ledger(read, items))


def _block(name, iid, pos=(1, 1), size=(1.6, 2.0)):
    return {"name": name, "count": 1, "inserts": [{"id": iid, "page": "p1", "layer": "MOBILYA", "pos": list(pos),
                                                     "size": list(size), "depth": 0, "nested": [], "strokes": 8}]}


def test_furniture_blocks_must_be_used_annotation_blocks_need_not():
    items = _items(blocks=[_block("YATAK_CIFT", "INSERT:4B"), _block("KUZEY_OKU", "INSERT:5C"),
                           _block("SANDALYE", "INSERT:6D/2")])
    piece = {"id": "f_L0_001", "level_id": "L0", "type": "chair", "footprint": {"center": [1, 1], "size": [0.5, 0.5]},
             "evidence": [_ev("INSERT:6D/2/0,INSERT:6D/2/1")]}
    found = _by_target(L.ledger(_building(furniture=[piece]), items))
    bed = found["INSERT:4B"]
    assert (bed["check"], bed["severity"], bed["fix"]["action"], bed["fix"]["type"]) == \
        ("A6", "major", "add_piece", "bed_double")
    assert "INSERT:5C" not in found and "INSERT:6D/2" not in found     # a north arrow; a chair used through its path


def test_a_block_only_site_decor_records_is_not_accounted():
    decor = {"id": "sd_L0_001", "level_id": "L0", "kind": "other", "center": [1, 1], "size": [1, 1],
             "evidence": [_ev("INSERT:4B/0")]}
    items = _items(blocks=[_block("KOLTUK", "INSERT:4B")])
    f = _by_target(L.ledger(_building(site={"areas": [], "decor": [decor]}), items))["INSERT:4B"]
    assert f["check"] == "A6" and "sd_L0_001" in f["message"]


def test_a_furniture_name_with_an_untyped_piece_beside_it_suggests_its_type():
    piece = {"id": "f_L0_009", "level_id": "L0", "type": "unknown", "build": False,
             "footprint": {"center": [3.0, 3.0], "size": [0.6, 0.6]}, "evidence": [_ev("LINE:9")]}
    b = _building(furniture=[piece], needs_review=[{"id": "f_L0_009", "reason": "has no type: not built"}])
    items = _items(texts=[_t("TEXT:8", "çamaşır mak.", (3.2, 3.1))])
    f = _by_target(L.ledger(b, items))["TEXT:8"]
    assert (f["check"], f["fix"]["action"], f["fix"]["element_id"], f["fix"]["type"]) == \
        ("A6", "type_piece", "f_L0_009", "washing_machine")
    typed = _building(furniture=[dict(piece, type="washing_machine", build=True)])
    assert "TEXT:8" not in _by_target(L.ledger(typed, items))


def test_reading_warnings_that_drop_something():
    b = _building(furniture=[{"id": "f_L0_001", "level_id": "L0", "type": "unknown", "build": False,
                              "evidence": [_ev("LINE:1")]}],
                  warnings=["site: 2 areas read outside the walls of L1 not used (the site is the ground floor's, L0)",
                            "f_L0_001: not built (rug or group outline): outline 2.0 x 1.0 m",
                            "x.dwg r5: section: read for the heights by the sheets stage (sheets.json r5)",
                            "x.dwg: entity types not read: ATTDEF x4",
                            "x.dwg: room label 'Brüt Alan =' at (3.0, 4.0) m lies outside the building"])
    a7 = [f for f in L.ledger(b, _items())["findings"] if f["check"] == "A7"]
    assert len(a7) == 1 and a7[0]["severity"] == "major" and "2 areas" in a7[0]["message"]


def test_levels_and_plan_pages_not_read():
    b = _building(levels_left_out=[{"label": "Level 2", "region_id": "r7", "reason": "outer walls do not close"}])
    items = _items(pages=[_page(),
                          _page(id="p2", region_id="r8", region_class="floor_plan", read=False,
                                skip_reason="alternative read, not built: the variants (base) do not select it"),
                          _page(id="p3", region_id="r9", region_class="floor_plan", read=False,
                                skip_reason="no scale source"),
                          _page(id="p4", region_id="r10", **{"class": "site_plan"}, region_class="site_plan",
                                read=False, region_use="ignored", region_features={"room_labels": 3},
                                skip_reason="not read")])
    found = _by_target(L.ledger(b, items))
    assert found["level:Level 2"]["severity"] == "critical" and found["page:p3"]["severity"] == "critical"
    assert found["page:p4"]["severity"] == "major" and "page:p2" not in found


def test_a_drawn_surface_outside_every_room():
    b = _building(rooms=[_room("r_salon", "SALON", text_id="TEXT:1")])
    hatch = {"id": "HATCH:9", "page": "p1", "layer": "ZEMIN", "area_m2": 12.0, "pos": [2.5, -2.5],
             "polygon": [[0, -1], [5, -1], [5, -3.4], [0, -3.4]]}
    inside = dict(hatch, id="HATCH:10", polygon=[[1, 1], [4, 1], [4, 3], [1, 3]], area_m2=6.0)
    legend = dict(hatch, id="HATCH:11", layer="MYD - LEJAND")
    items = _items(texts=[_t("TEXT:1", "SALON", (2, 2), role="room_label", label="SALON", label_part="name",
                             label_id="TEXT:1")], hatches=[hatch, inside, legend])
    found = _by_target(L.ledger(b, items))
    assert (found["HATCH:9"]["check"], found["HATCH:9"]["severity"]) == ("A9", "major")
    assert "HATCH:10" not in found and "HATCH:11" not in found
    # A terrace label inside that surface: the surface becomes its outline hint, not a finding of its own.
    items["texts"].append(_t("TEXT:2", "TERAS", (2.5, -2.2)))
    found = _by_target(L.ledger(b, items))
    assert "HATCH:9" not in found and found["TEXT:2"]["fix"]["polygon_hint"] == hatch["polygon"]


def test_unused_geometry_layers():
    b = _building(walls=[{"id": "w_1", "start": [0, 0], "end": [5, 0], "thickness": 0.2,
                          "evidence": [_ev("LINE:1")]}],
                  warnings=["x.dwg: walls drawn as face lines: layer 'SIVA' chosen; runner-up 'DUVAR' (5 of 6)"])

    def lay(name, ids):
        return {"name": name, "page": "p1", "entities": len(ids), "types": {"LINE": len(ids)}, "ids": ids}

    many = [f"LINE:{k}" for k in range(100, 112)]
    items = _items(layers=[lay("KORKULUK", many), lay("SIVA", ["LINE:1"] + many), lay("DUVAR", many),
                           lay("OLCU", many), lay("XREF_A$0$MYD - CIZGI", many)])
    found = _by_target(L.ledger(b, items))
    assert found["layer:p1:KORKULUK"]["severity"] == "major"
    assert found["layer:p1:XREF_A$0$MYD - CIZGI"]["severity"] == "minor"
    assert not {"layer:p1:SIVA", "layer:p1:DUVAR", "layer:p1:OLCU"} & set(found)


def test_text_matching_never_through_the_block_a_whole_plan_is_drawn_in():
    """real03: the whole plan is one block; a room's label id INSERT:7/1/21/attrib1 must not make every text in the
    plan block 'used'."""
    room = _room("r_yatak", "YATAK ODASI", text_id="INSERT:7/1/21/attrib1", room_type="bedroom")
    b = _building(rooms=[room])
    items = _items(texts=[_t("INSERT:7/1/21/attrib1", "YATAK ODASI", (2, 2), role="room_label", label="YATAK ODASI",
                             label_part="name", label_id="INSERT:7/1/21/attrib1"),
                          _t("INSERT:7/1/21/attrib2", "14,20 m²", (2, 1.7), role="room_label", label="YATAK ODASI",
                             label_part="area", label_id="INSERT:7/1/21/attrib1"),
                          _t("INSERT:7/1/40/attrib1", "BALKON", (2, -1.5), role="room_label", label="BALKON",
                             label_part="name", label_id="INSERT:7/1/40/attrib1")])
    found = _by_target(L.ledger(b, items))
    assert found["INSERT:7/1/40/attrib1"]["check"] == "A1"
    assert "INSERT:7/1/21/attrib2" not in found


def test_no_inventory_is_a_finding():
    result = L.ledger(_building(), None)
    assert result["findings"][0]["check"] == "A8" and result["findings"][0]["target"] == "source_items"


# --------------------------------------------------------------------------
# The inventory
# --------------------------------------------------------------------------

def _stroke(sid, pts, layer, block=None, closed=False, fill=None):
    return Stroke(id=sid, kind="polyline" if closed else "line", pts=pts, closed=closed, layer=layer, block=block,
                  fill=fill)


def test_inventory_lists_blocks_inside_a_plan_block_layers_and_surfaces():
    """Page units are cm (0.01 m per unit). A plan drawn as one block PLAN (21 m wide: a container) holds a double bed
    block and a 12 m² terrace hatch; a chair block and a closed outline are drawn at the top level."""
    page = GenericPage(file="x.dxf", page=1, source_kind="dxf", units="dxf", units_to_m=0.01, size=(3000, 2000))
    page.strokes = [
        _stroke("LINE:1", [(0, 0), (500, 0)], "DUVAR"),
        _stroke("INSERT:10/7", [(0, 0), (2100, 0)], "DUVAR", block="PLAN"),
        _stroke("INSERT:10/5/0", [(100, 100), (260, 100)], "MOBILYA", block="PLAN/YATAK_CIFT"),
        _stroke("INSERT:10/5/1", [(100, 100), (100, 300)], "MOBILYA", block="PLAN/YATAK_CIFT"),
        _stroke("INSERT:10/8#0", [(0, -100), (300, -100), (300, -500), (0, -500)], "TERAS", block="PLAN",
                closed=True),
        _stroke("INSERT:20/0", [(600, 600), (650, 650)], "MOBILYA", block="SANDALYE"),
        _stroke("LWPOLYLINE:41", [(700, 0), (900, 0), (900, 200), (700, 200)], "ZEMIN", closed=True),
        _stroke("HATCH:30#0", [(0, 0), (50, 0), (50, 50), (0, 50)], "ZEMIN", closed=True),
    ]
    summary = SI.page_summary(page)
    run = TextRun(id="TEXT:1", text="TERAS", box=(100, -300, 200, -280), height=20)
    area = TextRun(id="TEXT:2", text="12,00 m²", box=(100, -330, 220, -310), height=20)
    block = LabelBlock(name="TERAS", name_runs=[run], size_text=None, area_text="12,00 m²", anchor=(150, -290),
                       room_type="balcony", exterior=False, evidence=[], runs=[run, area])
    texts = [TextItem(text="TERAS", start=(100, -300), box=[100, -300, 200, -280], rotation_deg=0, entity="TEXT:1",
                      height=20, role="room_label", evidence={"layer": "YAZI", "entity": "TEXT:1"}),
             TextItem(text="12,00 m²", start=(100, -330), box=[100, -330, 220, -310], rotation_deg=0,
                      entity="TEXT:2", height=20, role="room_label", evidence={"layer": "YAZI", "entity": "TEXT:2"})]
    labels = [TextItem(text="TERAS", start=(1.5, -2.9), box=[100, -330, 220, -280], rotation_deg=0, entity="TEXT:1",
                       height=20, role="room_label", block=block)]
    ex = SimpleNamespace(transform_to_building=[0.01, 0.0, 0.0, 0.0, 0.01, 0.0], report={"units_to_m": 0.01},
                         texts=texts, labels=labels)
    rec = SimpleNamespace(key=("x.dxf", 1, None), file="x.dxf", page=1, format="dxf", kind="vector",
                          page_class="floor_plan", region_id=None, region_class=None, level_id="L0", skip_reason=None,
                          texts=[])
    other = SimpleNamespace(key=("y.pdf", 2, None), file="y.pdf", page=2, format="pdf", kind="vector",
                            page_class="section", region_id=None, region_class=None, level_id=None,
                            skip_reason="class section not used by the vector path",
                            texts=[TextItem(text="KESİT A-A", start=(5, 5), box=[0, 0, 0, 0], rotation_deg=0,
                                            entity="char:1", height=3, role="title")])
    build = SimpleNamespace(source_pages={rec.key: summary}, sheets=None, building={"project": {"id": "t"}})
    inv = SI.inventory(build, [rec, other], {rec.key: SimpleNamespace(extraction=ex)})
    assert inv["schema"] == SI.SCHEMA and [p["read"] for p in inv["pages"]] == [True, False]
    blocks = {b["name"]: b for b in inv["blocks"]}
    assert set(blocks) == {"YATAK_CIFT", "SANDALYE"}
    bed = blocks["YATAK_CIFT"]["inserts"][0]
    assert bed["id"] == "INSERT:10/5" and bed["depth"] == 1 and bed["size"] == pytest.approx([1.6, 2.0])
    assert [c["id"] for c in inv["containers"]] == ["INSERT:10"]
    layers = {lay["name"]: lay for lay in inv["layers"]}
    assert layers["DUVAR"]["ids"] == ["LINE:1", "INSERT:10/7"]
    assert layers["MOBILYA"]["entities"] == 3 and len(layers["MOBILYA"]["boxes"]) == 3
    assert [h["id"] for h in inv["hatches"]] == ["INSERT:10/8"]       # the 0.25 m² hatch is only counted
    assert inv["hatches"][0]["area_m2"] == pytest.approx(12.0)
    assert [o["id"] for o in inv["outlines"]] == ["LWPOLYLINE:41"]
    texts_by_id = {t["id"]: t for t in inv["texts"]}
    assert texts_by_id["TEXT:2"]["label"] == "TERAS" and texts_by_id["TEXT:2"]["label_part"] == "area"
    assert texts_by_id["TEXT:1"]["pos"] == pytest.approx([1.5, -2.9])
    assert texts_by_id["char:1"]["page"] == "p2" and texts_by_id["char:1"]["role"] == "title"
    # The ledger on it: the terrace texts are flagged once, with the hatch as outline hint.
    result = L.ledger({"project": {"id": "t"}, "rooms": [], "warnings": []}, inv)
    f = _by_target(result)["TEXT:1"]
    assert f["check"] == "A1" and f["fix"]["polygon_hint"] and f["fix"]["area_m2"] == pytest.approx(12.0)
    assert "INSERT:10/8" not in _by_target(result)
    assert _by_target(result)["INSERT:10/5"]["fix"]["type"] == "bed_double"


def test_the_pipeline_never_fails_on_the_inventory(monkeypatch, tmp_path):
    from wenart.ingest import pipeline as P

    assert "error" in P._page_summary(SimpleNamespace(strokes=[SimpleNamespace(pts=[(0, 0)], id=None)]))
    build = P.ProjectBuild({"warnings": []})

    def boom(*a, **k):
        raise RuntimeError("disk full")

    monkeypatch.setattr(SI, "write", boom)
    P._write_source_items(build, [], {}, tmp_path)
    assert any("source inventory not written" in w for w in build.building["warnings"])


# --------------------------------------------------------------------------
# A real reading end to end (real01: a vector PDF with stored recognition answers)
# --------------------------------------------------------------------------

@pytest.mark.slow
@pytest.mark.skipif(not (ROOT / "projects" / "real01").is_dir() or
                    not (ROOT / "results" / "recognition" / "real01").is_dir(), reason="real01 not in this checkout")
def test_real01_reading_writes_the_inventory_and_the_ledger_finds_only_the_parking(tmp_path):
    from wenart.ingest import pipeline as P

    rec = tmp_path / "recognition"
    rec.mkdir()
    for f in (ROOT / "results" / "recognition" / "real01").glob("*.json"):
        shutil.copy(f, rec / f.name)
    building, _ = P.run_project(ROOT / "projects" / "real01", tmp_path, answers=rec)
    items = SI.load(tmp_path)
    assert items["counts"]["pages_read"] == 1 and items["counts"]["texts"] >= 20
    result = L.ledger(building, items)
    assert result["summary"]["by_severity"]["critical"] == 0
    parking = _by_target(result)["sa_L0_parking"]
    assert (parking["check"], parking["severity"], parking["fix"]["kind"]) == ("A1", "major", "parking")
    assert result["summary"]["by_severity"]["major"] <= 2
