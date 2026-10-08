"""Feature 1: AI completes rooms with drawn furniture (docs/milestone10.md §2), with a fake client.

Fixtures: the M10 example building with the AI-made pieces stripped (``test_locked.drawn_building``: a drawn
sofa in the basement living room, a counter run in the kitchen, stairs in the halls, a double bed in the
bedroom, sanitary ware in the bathroom; the alternative level's hall is ``same_as`` the base hall) and a
semi-detached pair of bedrooms mirrored about a party wall at x = 4.1 (``twin_building``).
"""
import copy
import json
import math

import pytest
from shapely.geometry import Polygon

from wenart import building as B
from wenart.furniture import complete as C
from wenart.furniture import layout as L
from wenart.furniture import locked as LK
from wenart.furniture import placer as P
from wenart.furniture import schemas
from wenart.recognition.schemas import grammar_problems

from test_locked import drawn_building, example

MODEL = "fake/completion-model"


def room_of(prompt: str) -> str:
    return json.loads(prompt.split("Room (metres, X right, Y up):\n", 1)[1].split("\n\n", 1)[0])["room_id"]


class FakeClient:
    """``complete`` answers from ``table[(room id, pass)]`` (default: nothing), checking every answer against the
    room's schema as vLLM's grammar would; ``propose`` (Milestone 4 empty rooms) from ``m4[(room id, pass)]``."""
    model = MODEL
    _model = MODEL

    def __init__(self, table=None, m4=None, transport=()):
        self.table = table or {}
        self.m4 = m4 or {}
        self.transport = set(transport)
        self.calls, self.m4_calls, self.schemas, self.prompts = [], [], {}, {}

    def complete(self, prompt, schema, pass_no):
        rid = room_of(prompt)
        self.calls.append((rid, pass_no))
        self.schemas[rid], self.prompts[(rid, pass_no)] = schema, prompt
        if rid in self.transport:
            return L.Proposal(pass_no, None, error="cannot reach http://127.0.0.1:1/v1", prompt=prompt, model=MODEL,
                              transport_error=True)
        answer = self.table.get((rid, pass_no), {"changes": [], "added": []})
        if isinstance(answer, str):
            return L.Proposal(pass_no, None, error=answer, latency_s=0.5, prompt=prompt, model=MODEL)
        assert C.schema_errors(answer, schema) == [], (rid, C.schema_errors(answer, schema))
        return L.Proposal(pass_no, copy.deepcopy(answer), raw_text=json.dumps(answer), latency_s=1.25, prompt=prompt,
                          model=MODEL)

    def propose(self, prompt, pass_no):
        rid = room_of(prompt)
        self.m4_calls.append((rid, pass_no))
        answer = self.m4.get((rid, pass_no), {"pieces": []})
        return L.Proposal(pass_no, copy.deepcopy(answer), raw_text=json.dumps(answer), latency_s=1.0, prompt=prompt,
                          model=MODEL)


def pc(ftype, center, rotation, size, wall=True, reason="test"):
    return {"type": ftype, "center": list(center), "rotation_deg": rotation, "size": list(size), "against_wall": wall,
            "reason": reason}


def ch(pid, ftype, size, style="modern", colour="light grey", reason="test"):
    return {"id": pid, "type": ftype, "size": list(size), "style": style, "colour": colour, "reason": reason}


SALON, KITCHEN, HALL, HALL_ALT, BEDROOM, BATH = ("r_L-1_salon", "r_L-1_mutfak", "r_L-1_hol", "r_L-1b_hol",
                                                 "r_L0_yatak_odasi", "r_L0_banyo")
HALL_L0 = "r_L0_hol"
EXAMPLE_ANSWERS = {
    # The drawn sofa becomes a corner sofa (both passes; sizes 2.6 / 3.0: the smaller is kept; colours differ:
    # the project's); pass 1 adds a coffee table and a TV unit, pass 2 only the coffee table (agreed: 0.9).
    (SALON, 1): {"changes": [ch("f_L-1_002", "sofa_corner", (2.6, 1.6), colour="light grey", reason="fills the wall")],
                 "added": [pc("table_coffee", (2.725, 6.025), 0, (1.0, 0.6), False, "in front of the sofa"),
                           pc("tv_unit", (4.625, 0.5), 180, (1.6, 0.45), True, "facing the sofa")]},
    (SALON, 2): {"changes": [ch("f_L-1_002", "sofa_corner", (3.0, 1.7), colour="beige", reason="corner sofa")],
                 "added": [pc("table_coffee", (2.825, 5.925), 0, (1.0, 0.6), False, "coffee table")]},
    # The bedroom misses its nightstands and a wardrobe; pass 2 also proposes a bed (never a second one).
    (BEDROOM, 1): {"changes": [], "added": [pc("nightstand", (2.025, 7.775), 0, (0.5, 0.4)),
                                            pc("nightstand", (4.225, 7.775), 0, (0.5, 0.4)),
                                            pc("wardrobe", (0.571, 2.625), 90, (1.8, 0.6))]},
    (BEDROOM, 2): {"changes": [ch("f_L0_002", "bed_double", (1.8, 2.0))],
                   "added": [pc("nightstand", (2.025, 7.725), 0, (0.5, 0.4)),
                             pc("wardrobe", (0.571, 2.725), 90, (1.8, 0.6))]},
    # The base hall gets a console table; the alternative level's hall (same_as) is never asked.
    (HALL, 1): {"changes": [], "added": [pc("console_table", (6.525, 6.125), 90, (1.2, 0.35), True, "slim console")]},
    (HALL, 2): {"changes": [], "added": [pc("console_table", (6.525, 6.225), 90, (1.2, 0.35), True, "console")]},
    # The ground-floor hall's unverified drawn piece (unknown): both passes propose a console table (§1.6b row 15).
    (HALL_L0, 1): {"changes": [ch("f_L0_009", "console_table", (1.2, 0.35), reason="a narrow table: console")],
                   "added": []},
    (HALL_L0, 2): {"changes": [ch("f_L0_009", "console_table", (0.9, 0.3), reason="console table")], "added": []},
}
# style.json slots the looks are read from (track C adds them; absent slots give no design keys).
STYLE = {"family": "modern", "cabinets": {"front_style": "shaker", "colour": "sage", "handle": "brass", "worktop": "stone"},
         "furniture": {"by_type": {"table_coffee": {"material_tags": ["glass", "chrome"]},
                                   "sofa_corner": {"material_tags": ["fabric"]}}}}


@pytest.fixture(scope="module")
def completed():
    source = drawn_building(example())
    client = FakeClient(EXAMPLE_ANSWERS)
    out, records = C.complete_building(source, "Modern natural", client, C.Settings(), style=STYLE)
    return source, out, {r.room_id: r for r in records}, client


def piece(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


def added_in(b, room_id):
    return [f for f in b["furniture"] if f["room_id"] == room_id and f["source"] == "added_by_ai"]


# --------------------------------------------------------------------------
# Per room type: anchors, expected (missing) and what may be added
# --------------------------------------------------------------------------

@pytest.mark.parametrize("rtype, subtype, present, missing, may, never", [
    ("bedroom", None, [("bed_double", (1.6, 2.0))], {"nightstand": 2, "wardrobe": 1},
     {"desk", "office_chair", "bench", "ottoman", "armchair", "dresser", "bookshelf"}, {"bed_single", "crib", "chair"}),
    ("bedroom", None, [("bed_single", (0.9, 2.0)), ("nightstand", (0.5, 0.4))], {"wardrobe": 1}, {"desk"},
     {"nightstand"}),
    ("bedroom", "child", [("crib", (1.36, 0.7))], {"wardrobe": 1}, {"desk"}, {"nightstand", "bed_single", "bunk_bed"}),
    ("bedroom", None, [("wardrobe", (1.8, 0.6))], {"nightstand": 2}, {"bed_double", "bed_single"}, {"wardrobe"}),
    ("living", None, [("sofa", (2.2, 0.9)), ("armchair", (0.9, 0.9)), ("armchair", (0.9, 0.9))],
     {"table_coffee": 1, "tv_unit": 1}, {"chaise", "sideboard", "console_table", "display_cabinet"},
     {"armchair", "sofa", "sofa_corner"}),
    ("living", None, [("table_dining", (1.6, 0.9))], {"table_coffee": 1, "tv_unit": 1, "chair": 6}, {"sofa"},
     {"sofa_corner"}),
    ("dining", None, [("table_dining", (1.2, 0.8))], {"chair": 4}, {"sideboard", "bench"}, {"table_dining"}),
    ("dining", None, [("table_dining", (1.6, 0.9)), ("chair", (0.45, 0.45)), ("chair", (0.45, 0.45))], {"chair": 4},
     {"display_cabinet"}, {"table_dining"}),
    ("dining", None, [("table_dining", (1.0, 2.0))], {"chair": 8}, set(), set()),
    ("kitchen", None, [("kitchen_counter", (3.0, 0.6)), ("kitchen_island", (1.6, 0.9))], {},
     {"bar_stool", "table_dining", "chair", "tall_cabinet"}, {"kitchen_counter", "stove", "fridge", "wall_cabinet"}),
    ("kitchen", None, [("kitchen_counter", (3.0, 0.6))], {}, {"table_dining", "tall_cabinet"}, {"bar_stool"}),
    ("bathroom", None, [("toilet", (0.4, 0.7))], {}, set(), {"washbasin", "shower", "bathtub", "washing_machine"}),
    ("wc", None, [("toilet", (0.4, 0.7))], {}, set(), {"washbasin"}),
    ("hall", None, [("stair", (1.0, 3.0))], {}, {"console_table", "shoe_cabinet", "bench"}, {"dresser", "stair"}),
    ("other", None, [("desk", (1.4, 0.7))], {}, {"armchair", "chair", "bookshelf", "table_dining"}, {"desk"}),
])
def test_completion_plan_per_room_type(rtype, subtype, present, missing, may, never):
    plan = schemas.completion_plan(rtype, subtype, present)
    assert plan["missing"] == missing
    assert may <= set(plan["addable"]), (may - set(plan["addable"]), plan["addable"])
    assert not never & set(plan["addable"]), never & set(plan["addable"])


def test_counts_of_the_plan():
    plan = schemas.completion_plan("kitchen", None, [("kitchen_island", (1.6, 0.9))])
    assert plan["addable"]["bar_stool"] == 3                                     # 2-4 by the island's length
    assert schemas.completion_plan("kitchen", None, [("kitchen_island", (1.2, 0.8))])["addable"]["bar_stool"] == 2
    assert schemas.completion_plan("kitchen", None, [("kitchen_island", (2.0, 1.0))])["addable"]["bar_stool"] == 4
    living = schemas.completion_plan("living", None, [("sofa", (2.2, 0.9)), ("armchair", (0.9, 0.9))])
    assert living["addable"]["armchair"] == 1 and living["maxima"]["armchair"] == 2
    assert living["has_anchor"] and not living["anchor_missing"] and living["maxima"]["sofa"] == 0
    no_sofa = schemas.completion_plan("living", None, [("tv_unit", (1.6, 0.45))])
    assert no_sofa["anchor_missing"] and no_sofa["addable"]["sofa"] == 1 and "sofa_corner" not in no_sofa["addable"]
    child = schemas.completion_plan("bedroom", "child", [("wardrobe", (1.8, 0.6))])
    assert set(child["anchors"]) == {"bed_single", "bunk_bed", "crib"} and "bed_double" not in child["addable"]
    assert {"bed_single", "bunk_bed", "crib"} <= set(child["addable"])


def test_change_types_and_fixed_equipment():
    assert schemas.FIXED_TYPES == ("stair", "kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge",
                                   "washing_machine", "toilet", "washbasin", "shower", "bathtub")
    assert "sofa_corner" in schemas.change_types("living") and "sofa_corner" not in schemas.layout_types("living")
    assert not set(schemas.FIXED_TYPES) & set(schemas.change_types("kitchen"))
    assert "wall_cabinet" not in schemas.change_types("kitchen") and "bar_stool" in schemas.change_types("kitchen")
    assert schemas.change_types("bathroom") == () and schemas.change_types("wc") == ()
    assert {"bunk_bed", "crib"} <= set(schemas.change_types("bedroom", "child"))
    assert not {"bunk_bed", "crib"} & set(schemas.change_types("bedroom"))
    for rtype in schemas.ALLOWED_TYPES:
        assert not set(schemas.DOCUMENTED_ONLY_TYPES) & set(schemas.change_types(rtype))
    assert "prayer" not in schemas.ALLOWED_TYPES                                 # prayer rooms: never furnished
    for ftype in schemas.SIZE_OPTIONS:
        assert len(schemas.SIZE_OPTIONS[ftype]) == 3 and ftype in schemas.HEIGHTS


# --------------------------------------------------------------------------
# Agreement (§2.4) and the change rules
# --------------------------------------------------------------------------

def test_agreement_of_changes():
    order = ["a", "b", "c", "d"]
    p1 = {"changes": [ch("a", "sofa", (2.6, 0.95), colour="sage"), ch("b", "armchair", (0.9, 0.9)),
                      ch("c", "ottoman", (0.6, 0.6)), ch("a", "sofa", (1.6, 0.9))], "added": []}
    p2 = {"changes": [ch("a", "sofa", (2.17, 0.92), colour="sage", style="classic"), ch("c", "chaise", (0.75, 1.7))],
          "added": []}
    agreed, other = C.agree_changes({1: p1, 2: p2}, order)
    assert [a["id"] for a in agreed] == ["a"]
    a = agreed[0]
    assert a["type"] == "sofa" and a["size"] == (2.2, 0.9)                       # the smaller option of 2.6 / 2.2
    assert a["colour"] == "sage" and a["style"] is None                          # style differs: the project's
    reasons = {o["id"]: o["reason"] for o in other}
    assert "only pass 1 changes it" in reasons["b"]
    assert "disagree on the type (ottoman / chaise)" in reasons["c"]
    assert any(o["id"] == "a" and "listed twice" in o["reason"] for o in other)
    assert C.agree_changes({1: p1, 2: None}, order)[0] == []                    # a drawn piece needs both passes


def _drawn(items, room_type="living", subtype=None):
    building = {"walls": [], "openings": [], "rooms": [], "furniture": items}
    out = []
    for i, f in enumerate(items):
        out.append(C.Drawn(f, "changeable", LK.anchor_of(f, building), P.drawn_piece(f, i),
                           unverified=f.get("status") == "unverified"))
    return out


def _item(pid, ftype, size, status="verified"):
    return {"id": pid, "type": ftype, "source": "from_documents", "level_id": "L0", "room_id": "r",
            "footprint": {"center": [0, 0], "size": list(size), "rotation_deg": 0}, "front_deg": 270.0,
            "status": status}


def test_change_rules_main_piece_and_counts():
    drawn = _drawn([_item("bed", "bed_double", (1.6, 2.0)), _item("ch", "chair", (0.45, 0.45)),
                    _item("ns", "nightstand", (0.5, 0.4)), _item("dr", "dresser", (1.2, 0.5))], "bedroom")
    plan = schemas.completion_plan("bedroom", None, C._present(drawn))
    agreed = [{"id": "bed", "type": "desk", "size": (1.4, 0.7)},          # the main piece stays a main piece type
              {"id": "ch", "type": "bed_single", "size": (0.9, 2.0)},     # never a second main piece
              {"id": "dr", "type": "wardrobe", "size": (1.8, 0.6)},       # fine: 0 of 1 wardrobe
              {"id": "ns", "type": "wardrobe", "size": (1.2, 0.6)}]       # a second wardrobe: over the count
    kept, refused = C.check_change_rules(agreed, drawn, plan)
    assert [k["id"] for k in kept] == ["dr"]
    why = {r["id"]: r["reason"] for r in refused}
    assert "main piece (bed_double) may only become another main piece" in why["bed"]
    assert "never a second main piece" in why["ch"]
    assert "already holds 1 wardrobe" in why["ns"]
    kept, _ = C.check_change_rules([{"id": "bed", "type": "bed_single", "size": (0.9, 2.0)}], drawn, plan)
    assert kept                                                           # a bed may become another bed type


def test_filter_added_counts_and_one_main_piece():
    plan = schemas.completion_plan("bedroom", None, [("wardrobe", (1.8, 0.6))])
    items = [pc("bed_double", (1, 1), 0, (1.6, 2.0)), pc("bed_single", (3, 1), 0, (0.9, 2.0)),
             pc("nightstand", (1, 2), 0, (0.5, 0.4)), pc("nightstand", (2, 2), 0, (0.5, 0.4)),
             pc("nightstand", (3, 2), 0, (0.5, 0.4)), pc("wardrobe", (4, 2), 0, (1.8, 0.6))]
    kept, refused = C.filter_added(items, plan, "bedroom")
    assert [k["type"] for k in kept] == ["bed_double", "nightstand", "nightstand"]
    reasons = [r["reason"] for r in refused]
    assert reasons == ["never a second main piece (bed_single)", "covered: at most 2 nightstand",
                       "covered: the room holds its maximum of wardrobe"]


# --------------------------------------------------------------------------
# Question and schema
# --------------------------------------------------------------------------

def test_schema_is_strict_and_grammar_safe(completed):
    _s, _o, records, client = completed
    salon = client.schemas[SALON]
    assert grammar_problems(salon) == []
    changes = salon["properties"]["changes"]["items"]["properties"]
    assert changes["id"]["enum"] == ["f_L-1_002"]                       # only the changeable drawn piece
    assert "sofa_corner" in changes["type"]["enum"] and "kitchen_counter" not in changes["type"]["enum"]
    assert changes["colour"]["enum"] == C.colour_names() and changes["style"]["enum"] == C.style_families()
    added = salon["properties"]["added"]
    assert set(added["items"]["properties"]["type"]["enum"]) == set(records[SALON].question["add"])
    assert "sofa" not in added["items"]["properties"]["type"]["enum"]    # the room has its main piece
    assert C.schema_errors({"changes": [ch("f_L-1_001", "sofa", (2.2, 0.9))], "added": []}, salon)  # a stair id
    assert C.schema_errors({"changes": [], "added": [], "x": 1}, salon)
    assert C.schema_errors({"changes": [], "added": [pc("toilet", (1, 1), 0, (0.4, 0.7))]}, salon)
    kitchen = client.schemas[KITCHEN]                                    # no changeable piece: changes always []
    assert kitchen["properties"]["changes"] == {"type": "array", "maxItems": 0} and grammar_problems(kitchen) == []
    assert C.schema_errors({"changes": [ch("f_L-1_004", "sofa", (2.2, 0.9))], "added": []}, kitchen)


def test_prompt_lists_the_room_the_drawn_pieces_and_what_is_missing(completed):
    _s, _o, _r, client = completed
    p1, p2 = client.prompts[(SALON, 1)], client.prompts[(SALON, 2)]
    assert p1 != p2 and p1.endswith("Answer only with JSON.") and p2.endswith("Answer only with JSON.")
    assert "living room (Turkish: SALON)" in p1 and "Modern natural" in p1
    drawn = json.loads(p1.split("of a piece against a wall):\n", 1)[1].split("\n\n", 1)[0])
    assert [d["id"] for d in drawn] == ["f_L-1_002"]
    sofa = drawn[0]
    assert sofa["kind"] == "changeable" and sofa["anchor"]["kind"] == "back_edge"
    assert sofa["anchor"]["point"] == pytest.approx([3.125, 7.975], abs=0.006)                # 2 decimals
    assert sofa["against_wall"] == "w_L-1_003" and sofa["front_deg"] == 270.0
    assert "expected for this room type and missing: table_coffee (1), tv_unit (1)" in p1
    assert "- sofa_corner: height 0.85 m, size options [2.2, 1.5], [2.6, 1.6], [3.0, 1.7]" in p1
    assert "never a second main piece" in p1 and "light grey" in p1
    room = json.loads(p1.split("Room (metres, X right, Y up):\n", 1)[1].split("\n\n", 1)[0])
    assert room["doors"][0]["approach"] and room["windows"][0]["sill_height"] == 0.9
    kitchen = client.prompts[(KITCHEN, 1)]
    assert "no drawn piece may change its type or size" in kitchen and '"kind": "fixed"' in kitchen
    assert "changes: always an empty list []" in kitchen


# --------------------------------------------------------------------------
# The example end to end
# --------------------------------------------------------------------------

def test_every_furnished_room_is_handled_once(completed):
    source, out, records, client = completed
    assert set(records) == {r["id"] for r in source["rooms"] if r["has_documented_furniture"]}
    asked = {r for r, _ in client.calls}
    assert HALL_ALT not in asked and BATH not in asked                  # same_as copy; nothing to ask in a bathroom
    assert all(sorted(k for r, k in client.calls if r == room) == [1, 2] for room in asked)
    assert records[HALL_ALT].state == "copied" and records[HALL_ALT].partner["id"] == HALL
    assert records[BATH].state == "completed" and "nothing to ask" in records[BATH].reason
    B.validate(out)
    assert LK.check(source, out, "complete") == []


def test_a_changed_drawn_piece_keeps_its_anchor_and_label(completed):
    source, out, records, _c = completed
    sofa, drawn = piece(out, "f_L-1_002"), piece(source, "f_L-1_002")
    assert sofa["source"] == "from_documents" and sofa["modified_by_ai"] is True and sofa["status"] == "verified"
    assert sofa["type"] == "sofa_corner" and sofa["drawn_type"] == "sofa" and sofa["drawn_height"] == drawn["height"]
    assert sofa["drawn_footprint"] == drawn["footprint"]
    assert sofa["footprint"]["size"] == [2.6, 1.6] and sofa["footprint"]["center"] == [3.125, 7.175]  # the example's
    assert sofa["seat_depth"] == 0.9 and sofa["chaise_width"] == 0.9
    assert sofa["shape"] == "L" and sofa["chaise_side"] == "right" and sofa["chaise_depth"] == 1.6
    assert sofa["front_deg"] == drawn["front_deg"] and sofa["height"] == schemas.HEIGHTS["sofa_corner"]
    assert sofa["anchor"] == {"kind": "back_edge", "point": [3.125, 7.975], "wall_id": "w_L-1_003"}
    ai = [e for e in sofa["evidence"] if e["method"] == "ai"]
    assert [e["pass"] for e in ai] == [1, 2] and all(e["model"] == MODEL and e["confidence"] == 0.9 for e in ai)
    assert [e["text"] for e in ai] == ["fills the wall", "corner sofa"]
    assert sofa["evidence"][:len(drawn["evidence"])] == drawn["evidence"]
    assert sofa["design"] == {"style_family": "modern", "material_tags": ["fabric"]}   # colours differed: none
    change = next(c for c in records[SALON].changes if c["id"] == "f_L-1_002")
    assert change["status"] == "applied" and change["drawn_size"] == [2.2, 0.9] and change["size"] == [2.6, 1.6]


def test_added_pieces_complete_the_room_with_evidence_and_checks(completed):
    _s, out, records, _c = completed
    salon = {f["type"]: f for f in added_in(out, SALON)}
    assert set(salon) == {"table_coffee", "tv_unit"}
    for f in salon.values():
        assert f["completes_room"] is True and f["method"] == "ai" and f["status"] == "verified"
        assert set(f["checks"]) == set(P.CHECKS) and all(f["checks"].values())
        assert f["evidence"][0]["method"] == "ai" and f["evidence"][0]["model"] == MODEL
    assert salon["table_coffee"]["evidence"][0]["confidence"] == 0.9 and len(salon["table_coffee"]["evidence"]) == 2
    assert salon["tv_unit"]["evidence"][0]["confidence"] == 0.6 and len(salon["tv_unit"]["evidence"]) == 1
    assert records[SALON].chosen_pass == 1
    bedroom = sorted(f["type"] for f in added_in(out, BEDROOM))
    assert bedroom == ["nightstand", "nightstand", "wardrobe"]
    # Pass 2's bed change has no partner in pass 1: listed, not applied; the drawn bed stays as drawn.
    assert piece(out, "f_L0_002")["type"] == "bed_double" and "modified_by_ai" not in piece(out, "f_L0_002")
    bed = next(c for c in records[BEDROOM].changes if c["id"] == "f_L0_002")
    assert bed["status"] == "not_agreed" and "only pass 2" in bed["reason"]
    ids = [f["id"] for f in out["furniture"]]
    assert len(ids) == len(set(ids))


def test_every_added_and_changed_piece_passes_the_checks_in_its_room(completed):
    _s, out, records, _c = completed
    for rid, rec in records.items():
        room = next(r for r in out["rooms"] if r["id"] == rid)
        items = [f for f in out["furniture"] if f["room_id"] == rid and f["type"] not in schemas.MOUNTED_TYPES]
        ctx = P.room_context(out, room)
        pieces = [P.drawn_piece(f, i, against_wall=(f.get("layout") or {}).get("against_wall", False))
                  for i, f in enumerate(items)]
        drawn_fails = rec.drawn_layout.get("pieces", {})
        for f, c in zip(items, P.check_all(pieces, ctx)):
            failed = set(P.failed_checks(c)) - {"wall_contact"}
            if f["source"] == "added_by_ai":
                assert not failed, (rid, f["id"], failed)
            elif f.get("modified_by_ai"):
                assert failed <= set(drawn_fails.get(f["id"], [])), (rid, f["id"], failed)


def test_wall_cabinets_follow_the_counter_run(completed):
    _s, out, records, _c = completed
    cabinets = [f for f in out["furniture"] if f["type"] == "wall_cabinet"]
    kitchen = [f for f in cabinets if f["room_id"] == KITCHEN]
    assert len(kitchen) == 1 and records[KITCHEN].wall_cabinets == kitchen
    cab = kitchen[0]
    assert cab["source"] == "added_by_ai" and cab["method"] == "rule" and cab["completes_room"] is True
    assert cab["evidence"][0]["method"] == "derived" and "f_L-1_004" in cab["evidence"][0]["text"]
    assert cab["rule"]["z"] == [1.45, 2.15] and cab["mount_bottom_m"] == 1.45 and cab["height"] == pytest.approx(0.7)
    # Counter y 0.625..3.625 on the east wall w_L-1_002 (back edge x 9.98, wall face x 10.0): no window, door or
    # stove along it: one 3.0 m run, its back on the wall face, facing west like the counter.
    assert cab["footprint"]["size"] == [3.0, 0.35] and cab["footprint"]["center"] == pytest.approx([9.825, 2.125])
    assert cab["footprint"]["rotation_deg"] == 270.0 and cab["front_deg"] == 180.0 and cab["rule"]["excluded"] == []
    assert cab["design"] == {"front_style": "shaker", "colour": "sage", "handle": "brass"}     # style.json cabinets
    open_kitchen = [f for f in cabinets if f["room_id"] == "r_L-1b_salon_acik_mutfak"]
    assert len(open_kitchen) == 1                                        # an open kitchen of a living room too


def test_same_as_room_takes_the_base_rooms_decisions(completed):
    _s, out, records, _c = completed
    base, alt = added_in(out, HALL), added_in(out, HALL_ALT)
    assert [f["type"] for f in base] == [f["type"] for f in alt] == ["console_table"]
    assert alt[0]["footprint"]["center"] == base[0]["footprint"]["center"]
    assert alt[0]["footprint"]["rotation_deg"] == base[0]["footprint"]["rotation_deg"]
    assert alt[0]["mirrored_from"] == base[0]["id"] and alt[0]["level_id"] == "L-1b"
    assert alt[0]["id"].startswith("f_L-1b_") and alt[0]["evidence"] == base[0]["evidence"]
    assert all(alt[0]["checks"].values())


def test_outputs_summary_report_and_debug(completed, tmp_path):
    _s, out, records, _c = completed
    recs = list(records.values())
    summary = C.summary(recs, out, C.Settings(), "http://x/v1", MODEL, [])
    assert summary["kind"] == "completion" and summary["changes_applied"] == 2          # the sofa, the proposal
    assert summary["pieces_added"] == 7 and summary["wall_cabinets"] == 2 and summary["rooms_copied"] == 1
    json.dumps(summary)
    report = C.report(recs, out, C.Settings(), [])
    assert "| r_L-1_salon | f_L-1_002 | sofa / 2.20 x 0.90 | sofa_corner / 2.60 x 1.60 | applied |" in report
    assert "## Locked check: pass" in report and "f_L0_009 fails doors_free as drawn" in report
    assert "| r_L0_hol | f_L0_009 | unknown / 0.90 x 0.35 | console_table / 0.90 x 0.35 | applied (type_proposal) |" \
        in report
    assert "pass 2 bed_double" not in report or "never a second" in report
    for rec in recs:
        C.write_room_debug(rec, out, tmp_path)
    assert (tmp_path / f"{SALON}.png").exists() and json.loads((tmp_path / f"{SALON}.json").read_text())["question"]


@pytest.mark.parametrize("with_desk", [True, False])
def test_an_office_chair_needs_its_desk(with_desk):
    """§2.3 "desk + office_chair": the chair may stand in the desk's front clearance; without a desk it is dropped."""
    desk = [pc("desk", (0.5, 2.0), 90, (1.4, 0.7), True, "under the window")] if with_desk else []
    added = desk + [pc("office_chair", (1.2, 2.0) if with_desk else (3.0, 3.0), 270, (0.6, 0.6), False)]
    answers = {(BEDROOM, k): {"changes": [], "added": added} for k in (1, 2)}
    out, records = C.complete_building(drawn_building(example()), "x", FakeClient(answers), C.Settings())
    rec = next(r for r in records if r.room_id == BEDROOM)
    types = sorted(f["type"] for f in added_in(out, BEDROOM))
    if with_desk:
        assert types == ["desk", "office_chair"] and all(f["evidence"][0]["confidence"] == 0.9 for f in rec.added)
    else:
        assert types == [] and any("no desk in the room" in d["reason"] for d in rec.dropped)


# --------------------------------------------------------------------------
# Modes: keep (M9), keep size, keep list
# --------------------------------------------------------------------------

def test_keep_mode_is_unchanged_from_m9():
    source = drawn_building(example())
    client = FakeClient(EXAMPLE_ANSWERS)
    out, records = C.complete_building(source, "x", client, C.Settings(mode="keep"))
    assert client.calls == [] and all(r.state == "kept" for r in records)
    no_look = [{k: v for k, v in f.items() if k != "design"} for f in out["furniture"]]
    assert json.dumps(no_look, sort_keys=True) == json.dumps(source["furniture"], sort_keys=True)
    assert piece(out, "f_L0_007")["design"] == {"vanity": True}            # kept rooms get their looks (row 15)
    assert LK.check(source, out, "keep") == []


def test_keep_size_asks_no_change_but_completes():
    source = drawn_building(example())
    client = FakeClient({(SALON, k): {"changes": [], "added": EXAMPLE_ANSWERS[(SALON, k)]["added"]} for k in (1, 2)})
    out, records = C.complete_building(source, "x", client, C.Settings(keep_size=True))
    salon = client.schemas[SALON]
    assert salon["properties"]["changes"] == {"type": "array", "maxItems": 0}
    assert "always an empty list" in client.prompts[(SALON, 1)]
    assert piece(out, "f_L-1_002") == {**piece(source, "f_L-1_002"), "anchor": piece(out, "f_L-1_002")["anchor"]}
    assert {f["type"] for f in added_in(out, SALON)} == {"table_coffee", "tv_unit"}


def test_furnished_rooms_keep_by_label_or_id():
    source = drawn_building(example())
    client = FakeClient(EXAMPLE_ANSWERS)
    out, records = C.complete_building(source, "x", client, C.Settings(keep=("salon", "r_L0_yatak_odasi")))
    states = {r.room_id: r.state for r in records}
    assert states[SALON] == "kept" and states[BEDROOM] == "kept"
    assert SALON not in {r for r, _ in client.calls} and not added_in(out, SALON)
    assert LK.check(source, out, "complete", keep_rooms=[SALON, BEDROOM]) == []


def test_settings_from_the_brief(tmp_path):
    (tmp_path / "brief.yaml").write_text("furnished_rooms: keep\nfurnished_rooms_keep: [Salon]\n"
                                         "render:\n  twin_rooms: all\n", encoding="utf-8")
    s = C.load_settings(tmp_path)
    assert (s.mode, s.keep, s.keep_size, s.twin_rooms) == ("keep", ("Salon",), False, "all")
    assert "furnished_rooms_keep_size" in s.assumed and "furnished_rooms" not in s.assumed
    d = C.load_settings(tmp_path / "missing")
    assert d.mode == "complete" and d.twin_rooms == "one" and set(d.assumed) == set(C.Settings.KEYS)


# --------------------------------------------------------------------------
# Unverified drawn pieces: type proposals
# --------------------------------------------------------------------------

def test_an_unverified_piece_gets_a_type_proposal_as_the_example(completed):
    """§1.6b row 15: the example's f_L0_009 (drawn unknown, unverified): the agreed type, type_proposal, drawn_type,
    its drawn footprint, front and status, no modified_by_ai; listed with the unverified items."""
    source, out, records, _c = completed
    after, drawn, want = piece(out, "f_L0_009"), piece(source, "f_L0_009"), piece(example(), "f_L0_009")
    for key in ("type", "type_proposal", "drawn_type", "status", "footprint", "front_deg", "height", "source"):
        assert after.get(key) == want.get(key), key
    assert "modified_by_ai" not in after and "drawn_footprint" not in after
    ai = [e for e in after["evidence"] if e["method"] == "ai"]
    assert [e["pass"] for e in ai] == [1, 2] and all(e["confidence"] == 0.6 for e in ai)
    assert after["evidence"][:len(drawn["evidence"])] == drawn["evidence"]
    assert "f_L0_009" in out["unverified"] and any("AI type proposal console_table" in w for w in out["warnings"])
    change = next(c for c in records[HALL_L0].changes if c["id"] == "f_L0_009")
    assert change["type_proposal"] is True and change["status"] == "applied"


def test_unverified_bed_proposal_never_adds_a_second_bed():
    source = drawn_building(example())
    bed = piece(source, "f_L0_002")
    bed.update(type="unknown", status="unverified", type_raw="BLOK_A")
    source["unverified"] = ["f_L0_002"]
    answers = {(BEDROOM, k): {"changes": [ch("f_L0_002", "bed_double", (1.8, 2.0))], "added": []} for k in (1, 2)}
    out, records = C.complete_building(source, "x", FakeClient(answers), C.Settings())
    after = piece(out, "f_L0_002")
    assert after["type"] == "bed_double" and after["type_proposal"] is True and after["status"] == "unverified"
    assert after["footprint"] == bed["footprint"] and after["drawn_type"] == "unknown"
    assert "modified_by_ai" not in after and out["unverified"] == ["f_L0_002"]
    assert LK.check(source, out, "complete") == []


# --------------------------------------------------------------------------
# Looks (furniture.design, §1.6b row 15)
# --------------------------------------------------------------------------

def test_looks_of_completed_rooms(completed):
    _s, out, _r, _c = completed
    counter = piece(out, "f_L-1_004")
    assert counter["design"] == STYLE["cabinets"]                                     # style.json cabinets
    assert piece(out, "f_L-1b_002")["design"] == STYLE["cabinets"]                    # the open kitchen's run too
    assert piece(out, "f_L0_007")["design"] == {"vanity": True}                       # washbasin 0.5 m deep
    coffee = next(f for f in added_in(out, SALON) if f["type"] == "table_coffee")
    assert coffee["design"] == {"material_tags": ["glass"]}                           # chrome is no schema tag
    assert "design" not in piece(out, "f_L0_008")                                     # a shower: nothing to say


def test_looks_without_style_slots_and_by_rule():
    source = drawn_building(example())
    out, _r = C.complete_building(source, "x", FakeClient(), C.Settings(), style={"family": "modern"})
    assert "design" not in piece(out, "f_L-1_004")                                    # no cabinets slot: no keys
    style = {"cabinets": {"front": "slatted", "colour": 7, "handle": "gold", "worktop": "wood"}}
    out, _r = C.complete_building(source, "x", FakeClient(), C.Settings(), style=style)
    assert piece(out, "f_L-1_004")["design"] == {"front_style": "slatted", "worktop": "wood"}   # bad values left out
    cab = next(f for f in out["furniture"] if f["type"] == "wall_cabinet")
    assert cab["design"] == {"front_style": "slatted"}                                # no worktop on a wall cabinet


def test_agreed_colour_is_the_fabric_colour_of_upholstered_types():
    answers = {(HALL_L0, k): {"changes": [ch("f_L0_009", "bench", (1.0, 0.4), colour="mustard")], "added": []}
               for k in (1, 2)}
    out, _r = C.complete_building(drawn_building(example()), "x", FakeClient(answers), C.Settings())
    assert piece(out, "f_L0_009")["design"] == {"style_family": "modern", "fabric_colour": "mustard"}
    answers = {(HALL_L0, k): {"changes": [ch("f_L0_009", "console_table", (0.9, 0.3), colour="mustard")],
                              "added": []} for k in (1, 2)}
    out, _r = C.complete_building(drawn_building(example()), "x", FakeClient(answers), C.Settings())
    assert piece(out, "f_L0_009")["design"]["colour"] == "mustard"


@pytest.mark.parametrize("x0, x1, built_in", [(0.1, 4.0, True), (0.1, 3.0, False)])
def test_a_wardrobe_from_wall_to_wall_is_built_in(x0, x1, built_in):
    source = twin_building()
    w = round(x1 - x0, 3)
    source["furniture"].append({"id": "f_L0_003", "level_id": "L0", "room_id": TWIN_A, "type": "wardrobe",
                                "type_raw": None, "source": "from_documents", "status": "verified",
                                "evidence": [B.evidence("p.dxf", "vector", 1.0)],
                                "footprint": {"center": [(x0 + x1) / 2, 0.4], "size": [w, 0.6], "rotation_deg": 180.0},
                                "front_deg": 90.0, "height": 2.1})
    out, _r = C.complete_building(source, "x", FakeClient(), C.Settings(twin_rooms="all"))
    assert piece(out, "f_L0_003").get("design", {}).get("built_in", False) is built_in


# --------------------------------------------------------------------------
# Twins (semi-detached pair) mirrored, asked once
# --------------------------------------------------------------------------

def twin_building(furnished=True, shift=0.0):
    b = B.empty_building("twins", "projects/twins", "abc1234", created_utc="2026-10-08T12:00:00Z")
    b["levels"] = [{"id": "L0", "label": "Zemin Kat", "order": 0, "elevation": 0.0, "ceiling_height": 2.7,
                    "ceiling_height_source": "assumed_default", "evidence": [B.evidence("p.dxf", "vector", 1.0)]}]
    ev = [B.evidence("p.dxf", "vector", 1.0)]
    for n, (a, z) in enumerate([((0, 0), (8.2, 0)), ((8.2, 0), (8.2, 3.7)), ((8.2, 3.7), (0, 3.7)), ((0, 3.7), (0, 0)),
                                ((4.1, 0), (4.1, 3.7))], 1):
        b["walls"].append({"id": f"w_L0_{n:03d}", "level_id": "L0", "start": list(a), "end": list(z), "thickness": 0.2,
                           "status": "verified", "evidence": ev})
    ra, rb = "r_L0_yatak_odasi", "r_L0_yatak_odasi_2"
    for rid, poly, twin in ((ra, [[0.1, 0.1], [4.0, 0.1], [4.0, 3.6], [0.1, 3.6]], None),
                            (rb, [[4.2, 0.1], [8.1, 0.1], [8.1, 3.6], [4.2, 3.6]], ra)):
        b["rooms"].append({"id": rid, "level_id": "L0", "label": "Yatak Odası", "room_type": "bedroom", "polygon": poly,
                           "area_computed": 13.65, "has_documented_furniture": furnished, "twin_of": twin,
                           "status": "verified", "evidence": ev})
    for oid, kind, wall, c, w, swing in (("d_L0_001", "door", "w_L0_001", [3.2, 0.0], 0.9, ra),
                                         ("d_L0_002", "door", "w_L0_001", [5.0, 0.0], 0.9, rb),
                                         ("win_L0_001", "window", "w_L0_003", [1.5, 3.7], 1.2, None),
                                         ("win_L0_002", "window", "w_L0_003", [6.7, 3.7], 1.2, None)):
        b["openings"].append({"id": oid, "type": kind, "level_id": "L0", "wall_id": wall, "center": c, "width": w,
                              "sill_height": 0.9 if kind == "window" else None, "swing_side": swing,
                              "status": "verified", "evidence": ev})
    if furnished:
        for pid, rid, x in (("f_L0_001", ra, 2.0), ("f_L0_002", rb, 6.2 + shift)):
            b["furniture"].append({"id": pid, "level_id": "L0", "room_id": rid, "type": "bed_double", "type_raw": None,
                                   "source": "from_documents", "status": "verified", "evidence": ev,
                                   "footprint": {"center": [x, 2.6], "size": [1.6, 2.0], "rotation_deg": 0.0},
                                   "front_deg": 270.0, "height": 0.5})
    B.validate(b)
    return b


TWIN_A, TWIN_B = "r_L0_yatak_odasi", "r_L0_yatak_odasi_2"
TWIN_ANSWERS = {(TWIN_A, k): {"changes": [ch("f_L0_001", "bed_double", (1.8, 2.0), colour="sage green")],
                              "added": [pc("nightstand", (0.8, 3.38), 0, (0.5, 0.4)),
                                        pc("nightstand", (3.2, 3.38), 0, (0.5, 0.4)),
                                        pc("wardrobe", (0.42, 0.8), 90, (1.2, 0.6))]} for k in (1, 2)}


def test_twin_room_takes_the_mirrored_decisions():
    source = twin_building()
    client = FakeClient(TWIN_ANSWERS)
    out, records = C.complete_building(source, "x", client, C.Settings(twin_rooms="one"))
    assert {r for r, _ in client.calls} == {TWIN_A}                       # asked once
    rec = {r.room_id: r for r in records}
    assert rec[TWIN_B].state == "mirrored" and rec[TWIN_B].partner["transform"]["axis_deg"] == pytest.approx(90.0)
    bed_a, bed_b = piece(out, "f_L0_001"), piece(out, "f_L0_002")
    assert bed_a["footprint"]["size"] == bed_b["footprint"]["size"] == [1.8, 2.0]
    assert bed_b["footprint"]["center"] == pytest.approx([8.2 - bed_a["footprint"]["center"][0], 2.6])
    assert bed_b["mirrored_from"] == "f_L0_001" and bed_b["modified_by_ai"] is True
    assert bed_b["design"] == bed_a["design"] and bed_b["design"]["fabric_colour"] == "sage green"
    a = sorted(added_in(out, TWIN_A), key=lambda f: f["id"])
    b = sorted(added_in(out, TWIN_B), key=lambda f: f["id"])
    assert len(a) == len(b) == 3
    for fa, fb in zip(a, b):
        assert fb["type"] == fa["type"] and fb["mirrored_from"] == fa["id"] and fb["room_id"] == TWIN_B
        assert fb["footprint"]["center"] == pytest.approx([8.2 - fa["footprint"]["center"][0],
                                                           fa["footprint"]["center"][1]], abs=1e-3)
        assert math.isclose(G_front(fb), (180.0 - G_front(fa)) % 360.0, abs_tol=1e-6)
        assert all(fb["checks"].values())
    assert LK.check(source, out, "complete") == []
    B.validate(out)


def G_front(f):
    return f["front_deg"] % 360.0


def test_a_mirrored_corner_sofa_takes_the_other_side():
    source = twin_building()
    for r in source["rooms"]:
        r["room_type"], r["label"] = "living", "Salon"
    for f in source["furniture"]:
        f.update(type="sofa", height=0.85)
        f["footprint"].update(center=[f["footprint"]["center"][0], 3.15], size=[2.2, 0.9])
    answers = {(TWIN_A, k): {"changes": [ch("f_L0_001", "sofa_corner", (2.6, 1.6))], "added": []} for k in (1, 2)}
    client = FakeClient(answers)
    out, records = C.complete_building(source, "x", client, C.Settings())
    assert {r for r, _ in client.calls} == {TWIN_A}
    a, b = piece(out, "f_L0_001"), piece(out, "f_L0_002")
    assert (a["type"], a["chaise_side"], b["type"], b["chaise_side"]) == ("sofa_corner", "right", "sofa_corner", "left")
    pa, pb = P.drawn_piece(a).polygon(), P.drawn_piece(b).polygon()
    mirrored = Polygon([(8.2 - x, y) for x, y in pa.exterior.coords])
    assert pb.symmetric_difference(mirrored).area < 1e-6
    assert LK.check(source, out, "complete") == []


def test_the_pipelines_twin_transform_is_used():
    """§1.6b row 18: ``rooms[].twin_transform`` (first twin -> this room) wins over the derived mirror."""
    source = twin_building()
    room_b = next(r for r in source["rooms"] if r["id"] == TWIN_B)
    room_b["twin_transform"] = [-1.0, 0.0, 8.2, 0.0, 1.0, 0.0]                  # x' = 8.2 - x
    client = FakeClient(TWIN_ANSWERS)
    out, records = C.complete_building(source, "x", client, C.Settings())
    rec = {r.room_id: r for r in records}
    assert rec[TWIN_B].state == "mirrored" and rec[TWIN_B].partner["transform"]["kind"] == "given"
    assert rec[TWIN_B].partner["transform"]["affine"] == [-1.0, 0.0, 8.2, 0.0, 1.0, 0.0]
    b = sorted(added_in(out, TWIN_B), key=lambda f: f["type"])
    a = sorted(added_in(out, TWIN_A), key=lambda f: f["type"])
    assert [f["footprint"]["center"][0] for f in b] == pytest.approx([8.2 - f["footprint"]["center"][0] for f in a])
    room_b["twin_transform"] = [1.0, 0.0, 4.1, 0.0, 1.0, 0.0]                   # a shift: does not map the bed
    out, records = C.complete_building(source, "x", FakeClient(TWIN_ANSWERS), C.Settings())
    rec = {r.room_id: r for r in records}
    assert rec[TWIN_B].state == "completed" and "does not map" in rec[TWIN_B].reason


def test_mirror_transform_maps_points_fronts_and_sides():
    t = C.Transform.mirror((4.1, 0.0), 90.0)
    assert t.point((3.0, 1.0)) == pytest.approx((5.2, 1.0)) and t.flips
    assert t.direction(0.0) == pytest.approx(180.0) and t.direction(270.0) == pytest.approx(270.0)
    assert t.rotation(90.0) == pytest.approx(270.0) and t.side("right") == "left"
    given = C.given_transform({"twin_transform": [-1.0, 0.0, 8.2, 0.0, 1.0, 0.0]})
    assert given.point((3.0, 1.0)) == pytest.approx((5.2, 1.0)) and given.side("left") == "right"
    assert C.given_transform({"twin_transform": None}) is None and C.given_transform({}) is None


def test_twin_rooms_all_asks_both():
    client = FakeClient(TWIN_ANSWERS)
    C.complete_building(twin_building(), "x", client, C.Settings(twin_rooms="all"))
    assert {r for r, _ in client.calls} == {TWIN_A, TWIN_B}


def test_a_twin_that_does_not_mirror_is_asked_itself():
    client = FakeClient(TWIN_ANSWERS)
    out, records = C.complete_building(twin_building(shift=0.3), "x", client, C.Settings())
    rec = {r.room_id: r for r in records}
    assert {r for r, _ in client.calls} == {TWIN_A, TWIN_B}
    assert rec[TWIN_B].state == "completed" and "has no counterpart here" in rec[TWIN_B].reason


def test_empty_twin_rooms_copy_the_milestone_4_layout():
    source = twin_building(furnished=False)
    m4 = {(TWIN_A, k): {"pieces": [pc("bed_double", (2.0, 2.579), 0, (1.6, 2.0)),
                                   pc("wardrobe", (0.42, 0.8), 90, (1.2, 0.6))]} for k in (1, 2)}
    client = FakeClient(m4=m4)
    settings = C.Settings()
    partners = {r["id"]: p for r in source["rooms"] for p in [C.partner_of(r, settings)] if p}
    out, layouts = L.furnish_building(source, "x", client, partners=partners)
    assert {r for r, _ in client.m4_calls} == {TWIN_A}
    by_room = {l.room_id: l for l in layouts}
    assert by_room[TWIN_B].copied_from["room"] == TWIN_A and by_room[TWIN_B].proposals == []
    b = sorted(added_in(out, TWIN_B), key=lambda f: f["type"])
    a = sorted(added_in(out, TWIN_A), key=lambda f: f["type"])
    assert [f["type"] for f in b] == [f["type"] for f in a] == ["bed_double", "wardrobe"]
    for fa, fb in zip(a, b):
        assert fb["footprint"]["center"] == pytest.approx([8.2 - fa["footprint"]["center"][0],
                                                           fa["footprint"]["center"][1]], abs=1e-3)
        assert fb["mirrored_from"] == fa["id"] and all(fb["checks"].values())
    assert "copied from r_L0_yatak_odasi (twin)" in L.layout_report(layouts, out)
    B.validate(out)


# --------------------------------------------------------------------------
# Wall cabinets rule (§4.4)
# --------------------------------------------------------------------------

def kitchen_building(window=True, door=False):
    b = twin_building(furnished=False)
    b["rooms"] = [dict(b["rooms"][0], id="r_L0_mutfak", label="Mutfak", room_type="kitchen",
                       has_documented_furniture=True, twin_of=None)]
    b["openings"] = [o for o in b["openings"] if o["id"] == "d_L0_001"]
    b["openings"][0]["swing_side"] = "r_L0_mutfak"
    ev = [B.evidence("p.dxf", "vector", 1.0)]
    if window:
        b["openings"].append({"id": "win_L0_001", "type": "window", "level_id": "L0", "wall_id": "w_L0_003",
                              "center": [2.0, 3.7], "width": 0.8, "sill_height": 1.0, "status": "verified",
                              "evidence": ev})
    if door:
        b["openings"].append({"id": "d_L0_009", "type": "door", "level_id": "L0", "wall_id": "w_L0_003",
                              "center": [0.6, 3.7], "width": 0.8, "swing_side": None, "status": "verified",
                              "evidence": ev})
    for pid, ftype, c, size, h in (("f_L0_001", "kitchen_counter", [2.0, 3.3], [3.0, 0.6], 0.9),
                                   ("f_L0_002", "stove", [3.0, 3.3], [0.6, 0.6], 0.9),
                                   ("f_L0_003", "fridge", [3.75, 3.25], [0.5, 0.7], 1.8)):
        b["furniture"].append({"id": pid, "level_id": "L0", "room_id": "r_L0_mutfak", "type": ftype, "type_raw": None,
                               "source": "from_documents", "status": "verified", "evidence": ev,
                               "footprint": {"center": c, "size": size, "rotation_deg": 0.0}, "front_deg": 270.0,
                               "height": h})
    B.validate(b)
    return b


def _cabinets(b, mode="complete"):
    out, records = C.complete_building(b, "x", FakeClient(), C.Settings(mode=mode))
    return [f for f in out["furniture"] if f["type"] == "wall_cabinet"], out


def spans(cabinets):
    return [(round(f["footprint"]["center"][0] - f["footprint"]["size"][0] / 2, 3),
             round(f["footprint"]["center"][0] + f["footprint"]["size"][0] / 2, 3)) for f in cabinets]


def test_wall_cabinets_keep_off_windows_and_the_stove():
    """Counter x 0.5..3.5 on the north wall (face y 3.6); window x 1.6..2.4 (0.3 m kept free along the wall: 1.3..2.7);
    stove x 2.7..3.3; the rest 3.3..3.5 is shorter than 0.3 m."""
    cabinets, out = _cabinets(kitchen_building())
    assert spans(cabinets) == [(0.5, 1.3)]
    cab = cabinets[0]
    assert cab["footprint"]["center"][1] == pytest.approx(3.6 - 0.175) and cab["front_deg"] == 270.0
    assert set(cab["rule"]["excluded"]) == {"window win_L0_001", "stove f_L0_002"}
    no_window, _ = _cabinets(kitchen_building(window=False))
    assert spans(no_window) == [(0.5, 2.7)]                               # never over the stove
    assert LK.check(kitchen_building(), out, "complete") == []


def test_wall_cabinets_never_over_a_door_nor_in_keep_mode():
    cabinets, _ = _cabinets(kitchen_building(door=True))
    assert spans(cabinets) == []                              # door x 0.2..1.0 + 0.3 m, then the window: nothing
    cabinets, _ = _cabinets(kitchen_building(window=False, door=True))
    assert spans(cabinets) == [(1.3, 2.7)]                    # 0.3 m from the door (§1.6b row 15), not over the stove
    assert all(f["mount_bottom_m"] == 1.45 for f in cabinets)
    assert _cabinets(kitchen_building(), mode="keep")[0] == []


# --------------------------------------------------------------------------
# CLI (one run: empty rooms and furnished rooms, the locked check)
# --------------------------------------------------------------------------

def _write(tmp_path, building, brief="furnished_rooms: complete\n"):
    src = tmp_path / "building_fitted.json"
    B.save(building, src)
    project = tmp_path / "project"
    project.mkdir()
    (project / "brief.yaml").write_text(brief, encoding="utf-8")
    return src, project


def test_cli_furnishes_empty_rooms_and_completes_furnished_ones(tmp_path):
    source = drawn_building(example())
    src, project = _write(tmp_path, source)
    out = tmp_path / "out" / "building_furnished.json"
    m4 = {("r_L1_oyun_odasi", k): {"pieces": [pc("armchair", (1.0, 1.0), 0, (0.9, 0.9), False)]} for k in (1, 2)}
    client = FakeClient(EXAMPLE_ANSWERS, m4=m4)
    rc = L.main([str(src), "--out", str(out), "--debug", str(tmp_path / "dbg"), "--project-dir", str(project),
                 "--server", "http://127.0.0.1:1/v1"], client_factory=lambda: client)
    assert rc == 0
    final = B.load(out)
    assert piece(final, "f_L-1_002")["type"] == "sofa_corner"
    assert [f["type"] for f in added_in(final, "r_L1_oyun_odasi")] == ["armchair"]   # the M4 empty room
    completion = json.loads((out.parent / "completion.json").read_text())
    assert completion["locked_violations"] == [] and completion["changes_applied"] == 2
    assert completion["settings"]["furnished_rooms"] == "complete" and completion["model"] == MODEL
    assert LK.mode_of(completion) == "complete" and LK.keep_rooms_of(completion) == []   # what refit passes on
    assert LK.check(source, final, LK.mode_of(completion), LK.keep_rooms_of(completion)) == []
    layout = json.loads((out.parent / "layout.json").read_text())
    assert layout["completion"]["pieces_added"] == completion["pieces_added"] == 7
    assert (out.parent / "completion_report.md").read_text().startswith("# AI completion of furnished rooms")
    assert (tmp_path / "dbg" / f"{SALON}.png").exists() and (tmp_path / "dbg" / "r_L1_oyun_odasi.png").exists()
    assert LK.check(source, final, "complete") == []


def test_cli_keep_brief_changes_nothing_drawn(tmp_path):
    source = drawn_building(example())
    src, project = _write(tmp_path, source, "furnished_rooms: keep\n")
    out = tmp_path / "out.json"
    client = FakeClient(EXAMPLE_ANSWERS)
    assert L.main([str(src), "--out", str(out), "--project-dir", str(project)], client_factory=lambda: client) == 0
    final = B.load(out)
    assert client.calls == [] and LK.check(source, final, "keep") == []
    completion = json.loads((tmp_path / "completion.json").read_text())
    assert completion["rooms_completed"] == 0 and LK.mode_of(completion) == "keep"
    assert set(LK.keep_rooms_of(completion)) == {r["id"] for r in source["rooms"] if r["has_documented_furniture"]}


def test_cli_exits_3_when_the_completion_cannot_reach_the_server(tmp_path, capsys):
    src, project = _write(tmp_path, drawn_building(example()))
    out = tmp_path / "out" / "building_furnished.json"
    client = FakeClient(EXAMPLE_ANSWERS, transport=[SALON])
    rc = L.main([str(src), "--out", str(out), "--project-dir", str(project)], client_factory=lambda: client)
    assert rc == 3 and not out.exists() and not (out.parent / "completion.json").exists()
    assert f"{SALON} pass 1: server not reachable" in capsys.readouterr().err


def test_cli_exits_1_on_a_locked_violation(tmp_path, monkeypatch, capsys):
    src, project = _write(tmp_path, drawn_building(example()))
    out = tmp_path / "out" / "building_furnished.json"
    real = C.complete_building

    def moving(building, *args, **kwargs):           # a bug that moves a drawn piece 10 cm
        done, records = real(building, *args, **kwargs)
        piece(done, "f_L0_002")["footprint"]["center"][0] += 0.1
        return done, records

    monkeypatch.setattr(C, "complete_building", moving)
    rc = L.main([str(src), "--out", str(out), "--project-dir", str(project)],
                client_factory=lambda: FakeClient(EXAMPLE_ANSWERS))
    assert rc == 1 and not out.exists()
    completion = json.loads((out.parent / "completion.json").read_text())
    assert completion["locked_violations"] and "f_L0_002" in completion["locked_violations"][0]
    assert "locked violation" in capsys.readouterr().err
    assert "## Locked check: 2 violation(s)" in (out.parent / "completion_report.md").read_text()
