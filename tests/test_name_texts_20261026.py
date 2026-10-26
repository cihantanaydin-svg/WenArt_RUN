"""Furniture names written as texts in the plans (26 Oct 2026; Argus, source ledger A6; ``wenart.furniture.names``).

Every rule is general; real06 (L1: three "*SIFONIYER", one "çamaşır mak.") is the test case:

1. A furniture name text types the untyped drawn footprint it names (``infer.type_by_code``, method ``name_text``
   after the block name): on or within ``names.NAME_NEAR_M``, the size fits, the room may hold the type; the nearer
   text wins; a text whose type does not fit says why (``infer.name_text_note``).
1b. A name text written on a piece the AI passes typed as another family corrects it (``infer.name_text_retypes``).
2. A name text with no drawn piece near it adds the named piece ``from_documents`` (``names.add_named_pieces``),
   placed by the placer at the text; when no valid place lies within ``names.NAME_PLACE_M`` it is listed for review.
"""
import copy
import json
from pathlib import Path

import pytest

import _m11_room as M
from wenart.audit import ledger as L
from wenart.furniture import infer as INF
from wenart.furniture import names as NM
from wenart.furniture import placer

FIXTURE = Path(__file__).parent / "fixtures" / "real06_name_texts_20261026.json"


# --------------------------------------------------------------------------
# The vocabulary
# --------------------------------------------------------------------------

@pytest.mark.parametrize("text, ftype", [
    ("*SIFONIYER", "dresser"), ("Şifonyer", "dresser"), ("çamaşır mak.", "washing_machine"),
    ("ÇAMAŞIR MAKİNESİ", "washing_machine"), ("Kleiderschrank", "wardrobe"), ("lave-linge", "washing_machine"),
    ("Lavatrice", "washing_machine"), ("Cómoda", "dresser"), ("Mesita de noche", "nightstand"),
    ("Orta sehpa", "table_coffee"), ("Çalışma masası", "desk"), ("table de chevet", "nightstand"),
    ("Kühlschrank", "fridge"), ("Duş teknesi", "shower"), ("TV ünitesi", "tv_unit"),
    ("Tek kişilik yatak", "bed_single"), ("Komodinler", "nightstand"), ("Bulaşık mak.", "kitchen_counter"),
    ("Esstisch", "table_dining"),
])
def test_names_in_six_languages(text, ftype):
    hit = NM.furniture_name({"text": text})
    assert hit is not None and hit["type"] == ftype


@pytest.mark.parametrize("text, family, types", [
    ("Bett", "bed", ("bed_double", "bed_single")), ("Schrank", "storage", ("wardrobe", "tall_cabinet")),
    ("Sehpa", "table", ("table_coffee", "side_table")),
])
def test_generic_names_name_a_family(text, family, types):
    hit = NM.furniture_name({"text": text})
    assert hit["type"] is None and hit["family"] == family and hit["types"] == types


@pytest.mark.parametrize("row", [
    {"text": "YATAK"}, {"text": "BANYO"}, {"text": "Lavabo"}, {"text": "OCAK 2024"},
    {"text": "Tableau des surfaces"}, {"text": "YATAK + KOMODİN"}, {"text": "Bureau"}, {"text": "Planta baja"},
    {"text": "SIFONYER", "role": "room_label"}, {"text": "SIFONYER", "label_part": "name"},
    {"text": "KOMODIN", "role": "dimension"}, {"text": "ÇAMAŞIRLIK"}, {"text": "Çatıya çıkış merd."},
])
def test_not_furniture_names(row):
    assert NM.furniture_name(row) is None


def test_the_ledger_classifies_with_the_same_function():
    assert L.classify_text({"text": "Çalışma masası"}) == "furniture_name"      # its room word is inside the name
    assert L.classify_text({"text": "YATAK"}) == "space_name"
    assert L._furniture_type("*SIFONIYER") == "dresser" and L._furniture_type("Bett") == "bed"
    assert L.NAME_NEAR_M == NM.NAME_NEAR_M and L.FAMILIES is NM.FAMILIES
    assert "furniture_texts" in L.DATA_KEYS                  # the reading's record never "uses" a text


def test_code_methods_order():
    assert INF.CODE_TYPE_METHODS == ("twin", "level", "same_block", "block", "name_text", "zone_label", "group_member")


# --------------------------------------------------------------------------
# Rule 1: an untyped drawn footprint named by a text
# --------------------------------------------------------------------------

def _text(tid, text, pos, room_id=M.ROOM_ID, level_id="L0"):
    hit = NM.furniture_name({"text": text})
    return {"id": tid, "level_id": level_id, "room_id": room_id, "text": text, "type": hit["type"],
            "types": list(hit["types"]), "family": hit["family"], "word": hit["word"], "pos": list(pos),
            "layer": "MOBILYA ISIMLERI", "file": "plan.dxf", "page": None, "method": "vector"}


def _untyped(pid, center, size, rotation=0.0):
    return M.fp(pid, "unknown", center, size, rotation, front=None, status="unverified", build=False,
                not_built_reason="untyped (CLAUDE.md: no untyped piece is built)")


def _bedroom(furniture, texts, room_type="bedroom", **kw):
    b = M.building(furniture=furniture, room_type=room_type, **kw)
    b["furniture_texts"] = texts
    return b


def test_a_name_text_on_an_untyped_footprint_types_it():
    piece = _untyped("f_L0_001", (0.3, 2.0), (1.2, 0.55), 90.0)          # against the west wall
    b = _bedroom([piece], [_text("TEXT:1", "*SIFONIYER", (0.35, 2.3))])
    found = INF.type_by_code(b, piece)
    assert found["type"] == "dresser" and found["method"] == "name_text"
    ev = found["evidence"]
    assert ev["entity"] == "TEXT:1" and ev["method"] == "inferred" and ev["name_text"]["text"] == "*SIFONIYER"
    assert ev["rule"] == NM.RULE_TYPE
    typed, props = INF.apply_code_types(b)
    f = typed["furniture"][0]
    assert (f["type"], f["type_method"], f["inferred"], f["build"]) == ("dresser", "name_text", True, True)
    # the ledger: the text is used by the built piece
    items = {"pages": [{"id": "p1", "level_id": "L0", "read": True, "class": "floor_plan"}],
             "texts": [{"id": "TEXT:1", "page": "p1", "text": "*SIFONIYER", "pos": [0.35, 2.3], "role": "other"}]}
    assert not [x for x in L.ledger(typed, items)["findings"] if x["check"] == "A6"]
    assert [x for x in L.ledger(b, items)["findings"] if x["check"] == "A6"]


def test_a_name_text_too_far_or_of_another_size_or_room_is_not_used():
    piece = _untyped("f_L0_001", (0.3, 2.0), (1.2, 0.55), 90.0)
    def method(b):
        return (INF.type_by_code(b, piece) or {}).get("method")    # the room's missing member may still type it

    far = _bedroom([piece], [_text("TEXT:1", "*SIFONIYER", (2.5, 2.0))])            # 1.9 m away
    assert method(far) != "name_text" and INF.name_text_note(far, piece) is None
    machine = _bedroom([piece], [_text("TEXT:2", "çamaşır mak.", (0.35, 2.3))])      # 1.2 x 0.55 is no washer
    assert method(machine) != "name_text"
    assert "washing_machine" in INF.name_text_note(machine, piece) and "does not fit" in INF.name_text_note(
        machine, piece)
    living = _bedroom([piece], [_text("TEXT:3", "*SIFONIYER", (0.35, 2.3))], room_type="living")
    assert method(living) != "name_text"
    assert "holds no dresser" in INF.name_text_note(living, piece)


def test_the_nearer_text_wins_and_a_text_names_one_piece():
    piece = _untyped("f_L0_001", (0.3, 2.0), (1.2, 0.55), 90.0)
    b = _bedroom([piece], [_text("TEXT:1", "Çalışma masası", (0.9, 2.0)), _text("TEXT:2", "*SIFONIYER", (0.3, 2.1))])
    assert INF.type_by_code(b, piece)["type"] == "dresser"
    # two dresser-size footprints, the text on the first: only the first is named
    a = _untyped("f_L0_001", (0.3, 1.0), (1.2, 0.55), 90.0)
    c = _untyped("f_L0_002", (0.3, 2.6), (1.2, 0.55), 90.0)
    b2 = _bedroom([a, c], [_text("TEXT:1", "*SIFONIYER", (0.3, 1.2))])
    assert INF.type_by_code(b2, a)["type"] == "dresser"
    assert (INF.type_by_code(b2, c) or {}).get("method") != "name_text"
    assert "f_L0_001" in INF.name_text_note(b2, c)


# --------------------------------------------------------------------------
# Rule 1b: a name text written on a piece the AI typed as something else
# --------------------------------------------------------------------------

def _bath(furniture, texts):
    b = _bedroom(furniture, texts, room_type="bathroom", w=2.4, h=2.85, door_x=0.6, window=None)
    return b


def test_a_name_text_on_an_ai_typed_piece_corrects_it():
    basin = M.fp("f_L0_021", "washbasin", (2.1, 1.0), (0.6, 0.6), 0.0, front=None, type_method="ai_two_pass",
                 evidence=[{"file": "plan.dxf", "method": "vector", "confidence": 1.0, "entity": "LINE:1"},
                           {"file": "plan.dxf", "method": "ai", "confidence": 0.9, "entity": "recognition:sym_1"}])
    b = _bath([basin], [_text("TEXT:9", "çamaşır mak.", (1.88, 1.31))])
    props = INF.name_text_retypes(b)
    assert [(p["piece_id"], p["type"]) for p in props] == [("f_L0_021", "washing_machine")]
    out = INF.apply_inferences(b, props)["furniture"][0]
    assert (out["type"], out["type_method"], out["drawn_type"]) == ("washing_machine", "name_text", "washbasin")
    assert out["adjusted_by_ai"]["by"] == "code" and out["adjusted_by_ai"]["rule"] == "name_text"
    assert any(e.get("entity") == "TEXT:9" for e in out["evidence"])
    assert out["adjusted_by_ai"]["crop"] == "recognition/crops/sym_1_ctx.png"
    # infer_types runs it
    assert any(p["piece_id"] == "f_L0_021" and p["type"] == "washing_machine" for p in INF.infer_types(b))
    # never a block-named piece, never a text that only stands near it
    block = copy.deepcopy(basin)
    block["type_method"] = "block_name"
    assert INF.name_text_retypes(_bath([block], [_text("TEXT:9", "çamaşır mak.", (1.88, 1.31))])) == []
    assert INF.name_text_retypes(_bath([basin], [_text("TEXT:9", "çamaşır mak.", (1.3, 1.0))])) == []
    # a piece of the named family already there: the text is used
    machine = M.fp("f_L0_030", "washing_machine", (2.1, 2.0), (0.6, 0.6), 0.0, front=None)
    assert INF.name_text_retypes(_bath([basin, machine], [_text("TEXT:9", "çamaşır mak.", (2.1, 1.5))])) == []


# --------------------------------------------------------------------------
# Rule 2: a name text with no drawn piece near it adds the named piece
# --------------------------------------------------------------------------

def test_a_name_text_alone_adds_the_named_piece_from_the_documents():
    bed = M.fp("f_L0_001", "bed_double", (2.5, 3.0), (1.6, 2.0), 0.0, front=270.0)
    b = _bedroom([bed], [_text("TEXT:7", "*SIFONIYER", (4.7, 1.6))])
    out = NM.add_named_pieces(b)
    assert len(out["added"]) == 1 and not out["review"]
    p = next(f for f in b["furniture"] if f["id"] == out["added"][0])
    assert (p["type"], p["source"], p["type_method"], p["inferred"], p["named_by"]) == \
        ("dresser", "from_documents", "name_text", True, "TEXT:7")
    assert p["footprint_inferred"] is True and p["status"] == "unverified"
    assert [e.get("entity") for e in p["evidence"]] == ["TEXT:7", "TEXT:7"]
    assert {e["method"] for e in p["evidence"]} == {"vector", "inferred"}
    assert ((p["footprint"]["center"][0] - 4.7) ** 2 + (p["footprint"]["center"][1] - 1.6) ** 2) ** 0.5 <= 1.0
    assert abs(p["footprint"]["center"][0] - (5.0 - 0.25 - placer.SNAP_GAP_M)) < 0.01     # back on the east wall
    assert abs(p["front_deg"] - 180.0) < 1e-6
    ctx = placer.room_context(b, b["rooms"][0])
    pieces = [placer.drawn_piece(f, i) for i, f in enumerate(b["furniture"])]
    assert not placer.failed_checks(placer.check_all(pieces, ctx)[-1])
    assert b["rooms"][0]["has_documented_furniture"] is True
    assert out["warnings"] and out["warnings"][0].startswith(p["id"])
    # run again: the text is used now, nothing more is added
    assert NM.add_named_pieces(b)["added"] == []


def test_a_name_text_without_a_valid_place_near_it_is_listed_for_review():
    # the wardrobe wall is full: no valid place for a dresser within 1 m of the text
    pieces = [M.fp(f"f_L0_00{k}", "wardrobe", (4.7, 0.6 + 1.0 * k), (1.0, 0.6), 90.0, front=180.0) for k in range(3)]
    pieces.append(M.fp("f_L0_009", "bed_double", (2.4, 2.0), (1.6, 2.0), 90.0, front=180.0))
    b = _bedroom(pieces, [_text("TEXT:7", "*SIFONIYER", (3.8, 1.6))], w=5.0, h=3.2, window=None)
    out = NM.add_named_pieces(b)
    assert out["added"] == [] and len(out["review"]) == 1
    nr = out["review"][0]
    assert nr["id"] == "TEXT:7" and nr["kind"] == NM.NAMED_REVIEW_KIND and "not added" in nr["reason"]
    assert any(n["id"] == "TEXT:7" for n in b["needs_review"])


def test_the_critic_asks_for_an_unplaced_named_piece_until_one_stands_there():
    from wenart.agent import critic_code as CC

    b = _bedroom([], [_text("TEXT:7", "*SIFONIYER", (4.7, 1.6))])
    b["needs_review"] = [NM._review(b["furniture_texts"][0], "the documents name a dresser ...: not added: x")]
    nr = [f for f in CC.reading_items(b) if f["check"] == "NR"]
    assert len(nr) == 1 and nr[0]["target"] == "TEXT:7" and nr[0]["message"].startswith("piece the documents name")
    b["furniture"].append(M.fp("f_L0_050", "dresser", (4.72, 1.6), (1.2, 0.5), 90.0, source="added_by_ai"))
    assert not [f for f in CC.reading_items(b) if f["check"] == "NR"]


@pytest.mark.parametrize("text, why", [("Bett", "generic name"), ("TV", "may be a mark")])
def test_generic_and_short_names_never_add(text, why):
    b = _bedroom([], [_text("TEXT:5", text, (4.7, 1.6))])
    out = NM.add_named_pieces(b)
    assert out["added"] == [] and why in out["review"][0]["reason"]


def test_a_name_text_beside_its_drawn_footprint_adds_nothing():
    piece = _untyped("f_L0_001", (0.3, 2.0), (1.2, 0.55), 90.0)
    b = _bedroom([piece], [_text("TEXT:1", "*SIFONIYER", (0.9, 2.0))], room_type="living")
    out = NM.add_named_pieces(b)
    assert out == {"added": [], "review": [], "warnings": []}


# --------------------------------------------------------------------------
# A zone label inside a room ("YEMEK BÖLÜMÜ" in the salon) types the footprint drawn in its zone
# --------------------------------------------------------------------------

@pytest.mark.parametrize("text, kind", [
    ("YEMEK BÖLÜMÜ", "dining"), ("Essbereich", "dining"), ("Salle à manger", "dining"), ("Zona pranzo", "dining"),
    ("Comedor", "dining"), ("Dining area", "dining"), ("Oturma alanı", "living"), ("Wohnbereich", "living"),
    ("Kochnische", "kitchen"), ("Çalışma alanı", "other"), ("SALON", "living"), ("ANTRE", None),
    ("MUTFAK VE YEMEK", None),
])
def test_zone_kinds(text, kind):
    assert NM.zone_kind(text) == kind


def _salon(furniture, label_pos=(1.5, 2.0)):
    """A 6 x 4 m living room labelled SALON at its east end and 'YEMEK BÖLÜMÜ' at ``label_pos``."""
    b = M.building(furniture=furniture, room_type="living", w=6.0, h=4.0, window=None)
    room = b["rooms"][0]
    b["zone_labels"] = NM.zone_records(b, room, [
        {"id": "TEXT:20", "text": "SALON", "label": "SALON", "pos": [4.5, 2.0]},
        {"id": "TEXT:21", "text": "YEMEK BÖLÜMÜ", "label": "YEMEK BÖLÜMÜ", "pos": list(label_pos)}],
        file="plan.dxf")
    return b


def test_a_dining_zone_label_types_its_table_before_the_group_member_rule():
    table = _untyped("f_L0_011", (1.5, 2.1), (1.69, 1.69), 84.7)       # a round table drawn with its chairs
    b = _salon([table])
    assert [(z["id"], z["kind"], z["anchors"]) for z in b["zone_labels"]] == [("TEXT:21", "dining", ["table_dining"])]
    found = INF.type_by_code(b, table)
    assert (found["type"], found["method"]) == ("table_dining", "zone_label")
    assert found["evidence"]["entity"] == "TEXT:21" and "chairs" in found["reason"]
    # without the zone label the living room's missing seating anchor took it (real06 f_L0_011: sofa_corner)
    plain = copy.deepcopy(b)
    plain["zone_labels"] = []
    assert (INF.type_by_code(plain, table) or {}).get("type") != "table_dining"
    # a footprint in the dining zone that is no table is never the living room's seating anchor
    sofa_like = _untyped("f_L0_012", (1.0, 3.4), (2.2, 0.9), 0.0)
    b2 = _salon([sofa_like])
    assert (INF.type_by_code(b2, sofa_like) or {}).get("type") not in ("sofa", "sofa_corner")
    # outside the zone (nearer SALON) the rule does not apply
    far = _untyped("f_L0_013", (4.8, 2.0), (1.69, 1.69), 0.0)
    assert (INF.type_by_code(_salon([far]), far) or {}).get("method") != "zone_label"


def test_a_zone_with_its_anchor_drawn_types_nothing_more():
    drawn = M.fp("f_L0_001", "table_dining", (1.4, 2.0), (1.6, 0.9), 0.0, front=None)
    other = _untyped("f_L0_002", (1.0, 3.3), (1.2, 0.8), 0.0)
    b = _salon([drawn, other])
    assert (INF.type_by_code(b, other) or {}).get("method") != "zone_label"


# --------------------------------------------------------------------------
# The room misses a set member the AI passes named in their answers or reasons
# --------------------------------------------------------------------------

def test_an_untyped_piece_the_ai_named_as_the_missing_member_is_typed_and_snapped():
    toilet = M.fp("f_L0_024", "toilet", (2.0, 0.4), (0.45, 0.7), 0.0, front=90.0, type_method="ai_two_pass")
    basin = M.fp("f_L0_025", "washbasin", (0.2, 1.2), (0.53, 0.34), 90.0, type_method="ai_two_pass")
    tub = _untyped("f_L0_011", (1.25, 2.4), (2.42, 0.98), 0.0)
    tub["type_candidates"] = [
        {"type": "unknown", "model_key": "qwen", "pass": 1, "reason": "The object has a curved shape and is in a "
         "bathroom, likely a bathtub or shower, not matching any furniture type."},
        {"type": "bunk_bed", "model_key": "glm", "pass": 2, "reason": "a bunk bed with a ladder"}]
    tub["evidence"].append({"file": "plan.dxf", "method": "ai", "confidence": 0.9, "entity": "recognition:sym_6"})
    b = _bath([toilet, basin, tub], [])
    props = INF.ai_named_members(b)
    assert [(p["piece_id"], p["type"]) for p in props] == [("f_L0_011", "bathtub")]
    p = props[0]
    assert "bathtub" in p["reason"] and "misses" in p["reason"] and "bunk_bed" in p["reason"]
    assert p["footprint"]["size"] == [1.8, 0.8]                    # the nearest real product inside 2.42 x 0.98
    out = {f["id"]: f for f in INF.apply_inferences(b, props)["furniture"]}["f_L0_011"]
    assert (out["type"], out["type_method"], out["inferred"], out["build"]) == ("bathtub", "inferred", True, True)
    assert out["drawn_footprint"]["size"] == [2.42, 0.98] and out["footprint"]["size"] == [1.8, 0.8]
    assert out["adjusted_by_ai"]["by"] == "code" and out["adjusted_by_ai"]["crop"] == "recognition/crops/sym_6_ctx.png"
    assert "not_built_reason" not in out
    # nothing when the bathroom already has its bath or shower, or when no pass named the member
    shower = M.fp("f_L0_030", "shower", (2.0, 2.4), (0.9, 0.9), 0.0, type_method="ai_two_pass")
    assert INF.ai_named_members(_bath([toilet, basin, tub, shower], [])) == []
    silent = copy.deepcopy(tub)
    silent["type_candidates"] = [{"type": "bunk_bed", "pass": 2, "reason": "a bunk bed"}]
    assert INF.ai_named_members(_bath([toilet, basin, silent], [])) == []


# --------------------------------------------------------------------------
# A room whose program needs a wardrobe run: the drawn run along its wall is that wardrobe
# --------------------------------------------------------------------------

def _dressing(furniture):
    b = M.building(furniture=furniture, room_type="other", w=2.4, h=2.45, door_x=1.2, window=None)
    b["rooms"][0].update(label="Soyunma Odası", label_raw="SOYUNMA ODASI")
    return b


def test_drawn_runs_in_a_dressing_room_are_its_wardrobes_snapped_to_a_real_depth():
    east = _untyped("f_L0_014", (2.4 - 0.426, 1.25), (2.27, 0.85), 90.0)
    west = _untyped("f_L0_015", (0.426, 1.25), (2.27, 0.85), 90.0)
    east["type_candidates"] = [{"type": "stair", "pass": 2, "reason": "parallel tread lines"}]
    b = _dressing([east, west])
    typed, props = INF.apply_code_types(b)
    assert sorted((p["piece_id"], p["type"], p["type_method"]) for p in props) == [
        ("f_L0_014", "wardrobe", "group_member"), ("f_L0_015", "wardrobe", "group_member")]
    by_id = {f["id"]: f for f in typed["furniture"]}
    e = by_id["f_L0_014"]
    assert e["footprint"]["size"] == [2.27, 0.6] and abs(e["footprint"]["center"][0] - (2.4 - 0.3)) < 2e-3
    assert e["front_deg"] == 180.0 and e["drawn_footprint"]["size"] == [2.27, 0.85]
    assert e["adjusted_by_ai"]["by"] == "code" and e["adjusted_by_ai"]["rule"] == INF.WARDROBE_RULE
    assert "dressing room" in e["inferred_reason"] and e["build"] is True
    assert by_id["f_L0_015"]["front_deg"] == 0.0 and abs(by_id["f_L0_015"]["footprint"]["center"][0] - 0.3) < 2e-3
    # the completion path types it and keeps the drawn footprint (locked check)
    proposed = {f["id"]: f for f in INF.apply_code_types(b, proposal=True)[0]["furniture"]}
    assert proposed["f_L0_014"]["type"] == "wardrobe" and proposed["f_L0_014"]["footprint"] == east["footprint"]


def test_a_bedroom_missing_its_wardrobe_takes_its_one_drawn_run():
    bed = M.fp("f_L0_001", "bed_double", (2.5, 3.0), (1.6, 2.0), 0.0, front=270.0)
    run = _untyped("f_L0_002", (4.574, 1.5), (1.8, 0.85), 90.0)          # on the east wall
    found = INF.type_by_code(M.building(furniture=[bed, run]), run)
    assert found["type"] == "wardrobe" and found["snapped"] and found["footprint"]["size"] == [1.8, 0.6]
    # two candidates: the plan crop decides; a wardrobe there already: nothing
    run2 = _untyped("f_L0_003", (0.426, 1.5), (1.8, 0.85), 90.0)
    assert (INF.type_by_code(M.building(furniture=[bed, run, run2]), run) or {}).get("type") != "wardrobe"
    ward = M.fp("f_L0_004", "wardrobe", (0.3, 1.5), (1.8, 0.6), 90.0)
    assert (INF.type_by_code(M.building(furniture=[bed, run, ward]), run) or {}).get("type") != "wardrobe"


# --------------------------------------------------------------------------
# The reading records the name texts of the read pages (inventory rows, building metres)
# --------------------------------------------------------------------------

def test_the_reading_records_the_furniture_texts():
    from types import SimpleNamespace

    from wenart.ingest.generic import reading as RD
    from wenart.ingest.model import LevelExtraction, TextItem

    def text(eid, value, x, y, role="other"):
        return TextItem(text=value, start=(x, y), box=[x - 50, y - 20, x + 50, y + 20], rotation_deg=0.0, entity=eid,
                        height=40.0, role=role, evidence={"layer": "MOBILYA ISIMLERI", "method": "vector"})

    # page units mm, building metres = mm / 1000
    ex = LevelExtraction(file="plan.dxf", page=1, level_id="L0", units="mm",
                         transform_to_building=[0.001, 0.0, 0.0, 0.0, 0.001, 0.0],
                         texts=[text("TEXT:1", "*SIFONIYER", 4700, 1600),
                                text("TEXT:2", "ODA", 2500, 2000, "room_label"),
                                text("TEXT:3", "Kleiderschrank", 5100, 1000), text("TEXT:4", "345", 1000, 1000),
                                text("TEXT:5", "çamaşır mak.", 9000, 9000)])
    work = SimpleNamespace(record=SimpleNamespace(level_id="L0", file="plan.dxf", page=1, format="dxf"), extraction=ex)
    build = SimpleNamespace(building=M.building(), generic=[])
    rows = RD.furniture_texts(build, {"k": work})
    assert [(t["id"], t["type"], t["room_id"]) for t in rows] == [
        ("TEXT:1", "dresser", M.ROOM_ID),                    # in the room
        ("TEXT:3", "wardrobe", M.ROOM_ID),                   # 0.10 m outside it (on the wall line): the nearest room
        ("TEXT:5", "washing_machine", None)]                 # far from every room
    t1 = rows[0]
    assert t1["pos"] == [4.7, 1.6] and t1["layer"] == "MOBILYA ISIMLERI" and t1["file"] == "plan.dxf"
    assert NM.room_of_point(build.building, "L0", (5.0 + NM.TEXT_ROOM_M + 0.05, 1.0)) is None


def test_the_reading_records_the_zone_labels():
    from types import SimpleNamespace

    from wenart.ingest.generic import reading as RD
    from wenart.ingest.model import LevelExtraction, TextItem

    def label(eid, value, x, y):
        return TextItem(text=value, start=(x, y), box=[x - 50, y - 20, x + 50, y + 20], rotation_deg=0.0, entity=eid,
                        height=40.0, role="room_label", evidence={"layer": "MAHAL", "method": "vector"})

    own, zone = label("TEXT:30", "SALON", 4500, 2000), label("TEXT:31", "YEMEK BÖLÜMÜ", 1500, 2000)
    ex = LevelExtraction(file="plan.dxf", page=1, level_id="L0", units="mm",
                         transform_to_building=[0.001, 0.0, 0.0, 0.0, 0.001, 0.0], texts=[own, zone],
                         labels=[own, zone])
    work = SimpleNamespace(record=SimpleNamespace(level_id="L0", file="plan.dxf", page=1, format="dxf"), extraction=ex)
    b = M.building(room_type="living", w=6.0, h=4.0)
    rows = RD.zone_labels(SimpleNamespace(building=b, generic=[]), {"k": work})
    assert [(z["id"], z["kind"], z["anchors"], z["file"]) for z in rows] == [
        ("TEXT:31", "dining", ["table_dining"], "plan.dxf")]
    from shapely.geometry import Polygon
    cell = Polygon(rows[0]["zone"])
    assert abs(cell.area - 3.0 * 4.0) < 1e-6          # the half of the room nearer the dining label (x < 3 m)


# --------------------------------------------------------------------------
# real06 (L1 of the reading with the answers of run 20261026-170020-full, before this rule)
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real06():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_real06_name_texts_type_correct_and_add(real06):
    b = copy.deepcopy(real06)
    by_id = {f["id"]: f for f in b["furniture"]}
    assert [t["id"] for t in b["furniture_texts"]] == ["TEXT:2772EB", "TEXT:29ABD3", "TEXT:29AC0C", "TEXT:29AC25"]
    # rule 1 in the reading: f_L1_007 (untyped before the tie-break) is the dresser its text stands on
    first = copy.deepcopy(b)
    f7 = next(f for f in first["furniture"] if f["id"] == "f_L1_007")
    f7.update(type="unknown", type_method="none")
    assert INF.type_by_code(first, f7)["type"] == "dresser"
    # f_L1_019: the text names it, but the reading made its room a living room
    assert INF.type_by_code(b, by_id["f_L1_019"]) is None
    assert "holds no dresser" in INF.name_text_note(b, by_id["f_L1_019"])
    # rule 1b: the tie-break's desk f_L1_007 and the AI's washbasin f_L1_021 are corrected
    props = INF.infer_types(b)
    named = sorted((p["piece_id"], p["type"]) for p in props if p.get("type_method") == INF.NAME_RETYPE_METHOD)
    assert named == [("f_L1_007", "dresser"), ("f_L1_021", "washing_machine")]
    b["furniture"] = INF.apply_inferences(b, props)["furniture"]
    f21 = next(f for f in b["furniture"] if f["id"] == "f_L1_021")
    assert (f21["type"], f21["drawn_type"], f21["adjusted_by_ai"]["by"]) == ("washing_machine", "washbasin", "code")
    # rule 2: the master bedroom's dresser text stands in front of the 1.55 m doorless opening o_L1_007 the reading
    # made of the east window: no valid place within 1 m, listed for review (never forced)
    as_read = copy.deepcopy(b)
    out = NM.add_named_pieces(as_read)
    assert out["added"] == [] and [n["id"] for n in out["review"]] == ["TEXT:29AC25"]
    assert "more than 1 m" in out["review"][0]["reason"]
    # with the drawn windows read as windows, the dresser is added at its text, back on the east wall
    for o in b["openings"]:
        if o["id"] in ("o_L1_006", "o_L1_007"):
            o.update(type="window", sill_height=0.9)
    out = NM.add_named_pieces(b)
    assert len(out["added"]) == 1 and not out["review"]
    p = next(f for f in b["furniture"] if f["id"] == out["added"][0])
    assert (p["type"], p["room_id"], p["named_by"], p["source"]) == \
        ("dresser", "r_L1_ebeveyn_y_odasi", "TEXT:29AC25", "from_documents")
    assert p["footprint"]["center"][0] > 8.0 and abs(p["front_deg"] - 180.0) < 1e-6
    # the ledger: only f_L1_019's text is left (its piece is listed with the reason); as read, the unplaced one too
    items = {"pages": [{"id": "p4", "level_id": "L1", "read": True, "class": "floor_plan"}],
             "texts": [{"id": t["id"], "page": "p4", "text": t["text"], "pos": t["pos"], "role": "other"}
                       for t in b["furniture_texts"]]}
    a6 = sorted(f["target"] for f in L.ledger(b, items)["findings"] if f["check"] == "A6")
    assert a6 == ["TEXT:29ABD3"]
    a6 = sorted(f["target"] for f in L.ledger(as_read, items)["findings"] if f["check"] == "A6")
    assert a6 == ["TEXT:29ABD3", "TEXT:29AC25"]


def test_real06_dining_zone_and_corner_baths(real06):
    b = copy.deepcopy(real06)
    zone = b["zone_labels"]
    assert [(z["id"], z["room_id"], z["kind"], z["anchors"]) for z in zone] == [
        ("TEXT:295858", "r_L0_salon", "dining", ["table_dining"])]
    # the first reading: the round table drawn with its chairs under "YEMEK BÖLÜMÜ" and its four split chairs untyped
    for f in b["furniture"]:
        if f["id"] in ("f_L0_011", "f_L0_027", "f_L0_028", "f_L0_029", "f_L0_030"):
            f.update(type="unknown", type_method="none")
    coded = {p["piece_id"]: p for p in INF.code_types(b)}
    assert (coded["f_L0_011"]["type"], coded["f_L0_011"]["type_method"]) == ("table_dining", "zone_label")
    assert coded["f_L0_011"]["evidence"]["entity"] == "TEXT:295858"
    no_zone = copy.deepcopy(b)
    no_zone["zone_labels"] = []
    assert {p["piece_id"]: p["type"] for p in INF.code_types(no_zone)}.get("f_L0_011") == "sofa_corner"   # before
    # the corner baths of both bathrooms (pass 1: "likely a bathtub or shower", pass 2: bunk_bed)
    props = INF.ai_named_members(copy.deepcopy(real06))
    assert sorted((p["piece_id"], p["type"], tuple(p["footprint"]["size"])) for p in props) == [
        ("f_L0_010", "bathtub", (1.8, 0.8)), ("f_L1_011", "bathtub", (1.8, 0.8))]
    # the dressing room's two drawn runs (2.27 x 0.85 m, "unknown" / "stair" by the passes) are its wardrobes
    runs = {p["piece_id"]: p for p in INF.code_types(copy.deepcopy(real06))
            if p["piece_id"] in ("f_L1_014", "f_L1_015")}
    assert {k: (p["type"], p["footprint"]["size"]) for k, p in runs.items()} == {
        "f_L1_014": ("wardrobe", [2.2745, 0.6]), "f_L1_015": ("wardrobe", [2.2745, 0.6])}


def test_the_conflict_of_a_piece_typed_by_these_rules_is_resolved():
    from types import SimpleNamespace

    from wenart.ingest.generic import reading as RD

    piece = M.fp("f_L0_007", "dresser", (0.3, 2.0), (1.2, 0.55), 90.0, type_method="name_text",
                 inferred_reason="dresser: the documents name it")
    other = M.fp("f_L0_008", "desk", (2.3, 2.0), (1.2, 0.55), 90.0, type_method="inferred")
    raw = [{"kind": "symbol_type_disagreement", "element_ids": [pid], "description": "x",
            "resolution": "unresolved: the drawn footprint is kept as unknown, unverified"}
           for pid in ("f_L0_007", "f_L0_008")]
    build = SimpleNamespace(building=M.building(furniture=[piece, other]), raw_conflicts=raw)
    assert RD.resolve_named_conflicts(build) == 1
    assert raw[0]["resolution"].startswith("typed dresser by code (name_text)")
    assert raw[1]["resolution"].startswith("unresolved")
