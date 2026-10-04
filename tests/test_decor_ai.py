"""Milestone 9 AI decor (docs/milestone9.md §4; wenart/furniture/decor_ai.py): slots built from the building (every
kind, window and ceiling limits, unusable hosts and prayer rooms left out), the question and its strict per-room
schema (xgrammar-safe), the answers store (asked once by key, transport errors not stored), agreement of the two
passes (same slot and type; colour rule; single-pass items and wrong types never built), the checks (scaled down
never up, wall overlap, a second floor plant), the rule fallback per room with its reason, the building schema of
AI decor, the CLI with a fake client, and the builder's pure helpers for surface decor and the parametric mirror.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import jsonschema
import pytest

from wenart import building as B
from wenart.blender import furniture as F
from wenart.blender import parametric as P
from wenart.furniture import decor as D
from wenart.furniture import decor_ai as DA
from wenart.recognition.schemas import grammar_problems

from fakes.fake_vlm import unsupported_keys
from test_decor_m8 import RID, room_building

STYLE = "scandinavian, light oak, white walls"
LIVING = [("sofa", (3.0, 4.5), 0.0, (2.2, 0.9)),               # back to the north wall
          ("table_coffee", (3.0, 3.0), 0.0, (1.0, 0.6)),
          ("side_table", (1.5, 4.6), 0.0, (0.45, 0.45)),
          ("dresser", (5.75, 2.5), 270.0, (1.2, 0.5))]           # back to the east wall (+X)


def living(**kw):
    return room_building(furniture=LIVING, **kw)


def slots_of(building):
    room = building["rooms"][0]
    pieces = [f for f in building["furniture"] if f["room_id"] == room["id"]]
    return DA.room_slots(room, pieces, building)


def by_id(slots):
    return {s.id: s for s in slots}


# --------------------------------------------------------------------------
# Slots
# --------------------------------------------------------------------------

def test_living_room_slots_cover_every_kind():
    slots, notes = slots_of(living())
    ids = by_id(slots)
    assert ids["f_L0_001.cushions"].kind == "soft" and ids["f_L0_001.cushions"].types == ("cushion",)
    assert ids["f_L0_001.wall"].kind == "wall" and ids["f_L0_001.wall"].types == ("wall_art",)
    top = ids["f_L0_002.centre"]
    assert top.kind == "top" and top.types == ("vase", "bowl", "plant_small", "book_set")
    assert top.max_size[0] == pytest.approx(1.0 - 2 * DA.TOP_MARGIN_M) and top.max_size[1] == pytest.approx(0.54)
    assert ids["f_L0_003.centre"].types == ("table_lamp", "vase", "plant_small", "book_set")
    assert {"f_L0_004.left", "f_L0_004.right"} <= set(ids)
    assert ids["f_L0_004.wall"].types == ("wall_art", "mirror")       # a dresser takes a picture or a mirror
    assert any(s.kind == "rug" for s in slots) and any(s.kind == "floor" for s in slots)
    assert len([s for s in slots if s.kind == "floor"]) <= DA.FLOOR_CORNERS_MAX
    # Every slot of a top has its centre on the host and the host's rotation.
    left = ids["f_L0_004.left"]
    assert left.rotation_deg == 270.0 and left.center[0] == pytest.approx(5.75)


def test_top_height_is_limited_by_the_ceiling_and_a_window_sill():
    # A nightstand right under a window (sill 0.9 m): the height above its top is limited by the sill.
    b = room_building(room_type="bedroom", furniture=[("bed_double", (3.0, 3.9), 0.0, (1.6, 2.0)),
                                                      ("nightstand", (1.8, 4.75), 0.0, (0.5, 0.4))],
                      windows=[("win_1", "n", 1.8, 1.0)])
    ids = by_id(slots_of(b)[0])
    top = ids["f_L0_002.centre"]
    assert "under a window" in top.note
    assert top.max_size[2] == pytest.approx(0.9 - D.placer_bbox_height(b["furniture"][1]), abs=1e-6)
    # A low ceiling: no room above a dresser for anything.
    low = room_building(room_type="hall", furniture=[("dresser", (3.0, 4.75), 0.0, (1.2, 0.5))], ceiling=0.85)
    slots, notes = slots_of(low)
    assert not [s for s in slots if s.kind == "top"] and any("no decor fits" in n for n in notes)


def test_unverified_or_not_built_hosts_and_prayer_rooms_get_no_slot():
    b = room_building(furniture=[("sofa", (3.0, 4.5), 0.0, (2.2, 0.9), "unverified"),
                                 ("table_coffee", (3.0, 3.0), 0.0, (1.0, 0.6))])
    b["furniture"][1]["build"] = False
    slots, _ = slots_of(b)
    assert not [s for s in slots if s.host_id in ("f_L0_001", "f_L0_002")]
    prayer = room_building(room_type="prayer", furniture=LIVING)
    assert slots_of(prayer) == ([], [])
    assert DA.room_questions(prayer, STYLE) == []


def test_room_types_limit_the_decor():
    bath = room_building(room_type="bathroom", furniture=[("washbasin", (3.0, 4.75), 0.0, (0.6, 0.45)),
                                                          ("toilet", (1.0, 4.65), 0.0, (0.4, 0.7))])
    slots, _ = slots_of(bath)
    assert [(s.id, s.types) for s in slots] == [("f_L0_001.wall", ("mirror",))]
    mirror = slots[0].items["mirror"]
    assert mirror["type"] == "mirror" and mirror["gap_m"] == DA.MIRROR_GAP_M
    kitchen = room_building(room_type="kitchen", furniture=[("table_dining", (3.0, 2.5), 0.0, (1.2, 0.8))])
    slots, _ = slots_of(kitchen)
    assert {t for s in slots for t in s.types} <= set(DA.ROOM_TYPES["kitchen"]) | {"rug"} - {"rug"}


# --------------------------------------------------------------------------
# Question, schema, answers
# --------------------------------------------------------------------------

@pytest.mark.parametrize("project", ["real01", "synthetic-01", "synthetic-04"])
def test_the_committed_projects_questions(project):
    """The rooms of the M8 F1 projects the AI decor asks about: every schema passes the grammar backend's keyword
    check (recognition/schemas.py, found on the prep pod) and validates an empty answer."""
    root = Path(__file__).resolve().parents[1] / "results" / "furniture" / project
    if not (root / "building_furnished.json").is_file():
        pytest.skip("committed building not present")
    b = json.loads((root / "building_furnished.json").read_text(encoding="utf-8"))
    qs = DA.room_questions(b, STYLE)
    assert qs, project
    for q in qs:
        assert grammar_problems(q.schema) == [], q.room["id"]
        assert DA.schema_errors({"items": []}, q.schema) == []
        assert all(s.types for s in q.slots), q.room["id"]

def test_question_and_schema_name_only_the_rooms_slots():
    b = living()
    q = DA.room_questions(b, STYLE)[0]
    schema = q.schema
    assert unsupported_keys(schema) == [] and grammar_problems(schema) == []
    item = schema["properties"]["items"]["items"]
    assert item["properties"]["slot"]["enum"] == [s.id for s in q.slots]
    assert set(item["properties"]["type"]["enum"]) == {t for s in q.slots for t in s.types}
    assert item["properties"]["colour"]["enum"] == list(DA.COLOURS) and item["additionalProperties"] is False
    for n in DA.PASSES:
        text = q.prompts[n]
        assert STYLE in text and "never moved" in text and all(s.id in text for s in q.slots)
    assert q.prompts[1] != q.prompts[2]                                 # another block order
    good = {"items": [{"slot": q.slots[0].id, "type": q.slots[0].types[0], "colour": "cream", "reason": "x"}]}
    assert DA.schema_errors(good, schema) == []
    assert DA.schema_errors({"items": [dict(good["items"][0], slot="elsewhere")]}, schema)
    assert DA.COLOURS is P.DECOR_COLOURS


class FakeClient:
    def __init__(self, answers, model="fake/qwen", transport=()):
        self.answers, self.model, self.transport, self.calls = answers, model, set(transport), []

    def ask(self, prompt, schema, pass_no):
        self.calls.append(pass_no)
        if pass_no in self.transport:
            return {"data": None, "error": "connection refused", "transport": True, "latency_s": 0.0}
        return {"data": self.answers(prompt, schema, pass_no), "error": None, "transport": False, "latency_s": 0.1,
                "raw_text": "{}"}


def choose(*picks):
    """An answer function: ``picks`` = (slot suffix, type, colour) for both passes."""
    def answer(prompt, schema, pass_no):
        slots = schema["properties"]["items"]["items"]["properties"]["slot"]["enum"]
        items = []
        for suffix, dtype, colour in picks:
            slot = next(s for s in slots if s.endswith(suffix))
            items.append({"slot": slot, "type": dtype, "colour": colour, "reason": f"pass {pass_no}"})
        return {"items": items}
    return answer


def test_ask_stores_answers_by_key_and_never_asks_twice(tmp_path):
    b = living()
    path = tmp_path / "answers.json"
    client = FakeClient(choose(("f_L0_002.centre", "vase", "terracotta")))
    doc, failed = DA.ask(b, STYLE, client, path, client.model, log=lambda *a: None)
    rooms = len(DA.room_questions(b, STYLE))
    assert failed == 0 and len(doc["answers"]) == 2 * rooms and client.calls == [1, 2] * rooms
    again = FakeClient(choose())
    DA.ask(b, STYLE, again, path, client.model, log=lambda *a: None)
    assert again.calls == []                                            # same keys: nothing asked
    # A transport error is not an answer: not stored, counted.
    path2 = tmp_path / "answers2.json"
    dead = FakeClient(choose(), transport={2})
    doc, failed = DA.ask(b, STYLE, dead, path2, dead.model, log=lambda *a: None)
    assert failed == rooms and all(v["pass"] == 1 for v in doc["answers"].values())


# --------------------------------------------------------------------------
# Apply: agreement, checks, fallback
# --------------------------------------------------------------------------

def applied(b, answer, **kw):
    import tempfile
    from pathlib import Path
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "answers.json"
        client = FakeClient(answer, **kw)
        DA.ask(b, STYLE, client, path, client.model, log=lambda *a: None)
        answers = DA.read_answers(path)
    return DA.apply(b, STYLE, answers)


def test_agreed_items_are_built_with_both_passes_as_evidence():
    b = living()
    out, records = applied(b, choose(("f_L0_002.centre", "vase", "terracotta"), ("f_L0_001.cushions", "cushion", "sage green"),
                                     ("f_L0_003.centre", "table_lamp", "brass"), ("f_L0_001.wall", "wall_art", "navy")))
    B.validate(out)
    assert json.dumps(b["furniture"]) == json.dumps(out["furniture"])     # furniture untouched
    ai = [d for d in out["decor"] if d["method"] == "ai"]
    assert {d["type"] for d in ai} == {"vase", "cushion", "table_lamp", "wall_art"}
    assert len([d for d in ai if d["type"] == "cushion"]) == 2              # the sofa's two cushion places
    vase = next(d for d in ai if d["type"] == "vase")
    assert vase["host_id"] == "f_L0_002" and vase["colour"] == "terracotta" and vase["status"] == "verified"
    assert vase["size"] == [0.18, 0.18, 0.40] and vase["slot"] == "f_L0_002.centre"
    assert [e["pass"] for e in vase["evidence"]] == [1, 2] and all(e["method"] == "ai" for e in vase["evidence"])
    art = next(d for d in ai if d["type"] == "wall_art")
    assert art["host_id"] is None and art["anchor_ids"] == ["f_L0_001"] and "wall_point" in art
    rec = records[0]
    assert rec.fallback is None and len(rec.agreed) == 4 and not rec.not_agreed


def test_only_items_both_passes_chose_are_kept():
    def answer(prompt, schema, pass_no):
        slots = schema["properties"]["items"]["items"]["properties"]["slot"]["enum"]
        table = next(s for s in slots if s.endswith("f_L0_002.centre"))
        side = next(s for s in slots if s.endswith("f_L0_003.centre"))
        items = [{"slot": table, "type": "vase", "colour": "cream" if pass_no == 1 else "white", "reason": "r"}]
        if pass_no == 1:
            items.append({"slot": side, "type": "table_lamp", "colour": "brass", "reason": "only pass 1"})
        else:
            items.append({"slot": side, "type": "vase", "colour": "brass", "reason": "only pass 2"})
        return {"items": items}
    out, records = applied(living(), answer)
    rec = records[0]
    assert [(a["slot"], a["type"]) for a in rec.agreed] == [("f_L0_002.centre", "vase")]
    assert rec.agreed[0]["colour"] == "cream" and rec.agreed[0]["colour_agreed"] is False      # pass 1's colour
    assert sorted((x["type"], x["passes"][0]) for x in rec.not_agreed) == [("table_lamp", 1), ("vase", 2)]
    assert [d["type"] for d in out["decor"] if d["method"] == "ai"] == ["vase"]


def test_wrong_types_and_second_items_for_a_slot_are_rejected():
    items, rejected, error = DA.pass_items({"data": {"items": [
        {"slot": "a", "type": "vase", "colour": "white", "reason": ""},
        {"slot": "a", "type": "bowl", "colour": "white", "reason": ""},
        {"slot": "b", "type": "rug", "colour": "white", "reason": ""},
        {"slot": "nope", "type": "vase", "colour": "white", "reason": ""}]}},
        [DA.Slot("a", "top", ("vase", "bowl")), DA.Slot("b", "top", ("vase",))])
    assert [i["slot"] for i in items] == ["a"] and error is None
    assert [r["why"] for r in rejected] == ["a second item for the same slot", "the slot does not take this type",
                                           "unknown slot"]
    assert DA.pass_items(None, []) == ([], [], "not asked")
    assert DA.pass_items({"data": None, "error": "schema: x"}, []) == ([], [], "schema: x")


def test_surface_items_are_scaled_down_never_up_and_refused_when_too_small():
    slot = DA.Slot("s", "top", ("vase",), "f", "nightstand", (1.0, 1.0), 0.0, (0.5, 0.5, 2.0))
    box, _ = DA._surface_item(slot, "vase")
    assert box["size"] == [0.18, 0.18, 0.40]                             # the default, never larger
    small = DA.Slot("s", "top", ("vase",), "f", "nightstand", (1.0, 1.0), 0.0, (0.12, 0.30, 0.20))
    box, _ = DA._surface_item(small, "vase")
    assert box["size"] == [0.09, 0.09, 0.2]                             # uniform: the height limits it
    tiny = DA.Slot("s", "top", ("table_lamp",), "f", "nightstand", (1.0, 1.0), 0.0, (0.10, 0.10, 0.20))
    assert DA._surface_item(tiny, "table_lamp")[0] is None


def test_two_wall_items_never_overlap_on_one_wall():
    a = {"id": "a", "type": "wall_art", "wall_point": [3.0, 5.0], "rotation_deg": 0.0, "size": [1.0, 0.04]}
    near = {"id": "b", "type": "mirror", "wall_point": [3.6, 5.0], "rotation_deg": 0.0, "size": [0.6, 0.04]}
    far = {"id": "c", "type": "mirror", "wall_point": [5.0, 5.0], "rotation_deg": 0.0, "size": [0.6, 0.04]}
    other_wall = {"id": "d", "type": "mirror", "wall_point": [3.0, 5.0], "rotation_deg": 90.0, "size": [0.6, 0.04]}
    assert "overlaps wall_art a" in DA._wall_overlap(near, [a])
    assert DA._wall_overlap(far, [a]) is None and DA._wall_overlap(other_wall, [a]) is None


def test_rooms_without_agreement_or_answers_get_the_rules_with_the_reason():
    b = living()
    out, records = applied(b, choose())                                 # both passes answer nothing
    rec = records[0]
    assert rec.fallback == "the two passes agreed on no item"
    rule = [d for d in out["decor"] if d["method"] == "rule"]
    expected, _row = D.rule_decor_room(b, b["rooms"][0], b["furniture"], lambda lv: "x")
    assert sorted(d["type"] for d in rule) == sorted(d["type"] for d in expected) and rule
    # No answers at all (the server never answered): the rules, each pass named.
    out, records = DA.apply(b, STYLE, {"answers": {}})
    assert records[0].fallback == "pass 1: not asked; pass 2: not asked"
    # A pass that failed its schema: its error is the reason.
    out, records = applied(b, choose(), transport={1, 2})
    assert records[0].fallback.startswith("pass 1: not asked")


def test_brief_switches_decor_off_or_to_the_rules():
    off = living(brief={"decor": False})
    assert DA.decor_mode(off) == "off" and DA.apply(off, STYLE, {"answers": {}})[0]["decor"] == []
    rules = living(brief={"decor": "rules"})
    assert DA.decor_mode(rules) == "rules"
    out, records = DA.apply(rules, STYLE, {"answers": {}})
    assert out["decor"] and all(d["method"] == "rule" for d in out["decor"])
    assert records[0].fallback == "brief.decor is 'rules'"
    assert DA.decor_mode(living()) == "ai"


def test_schema_takes_ai_decor_and_refuses_broken_items():
    out, _ = applied(living(), choose(("f_L0_002.centre", "bowl", "black")))
    B.validate(out)
    for mutate in (lambda o: o["decor"][0].update(method="guess"), lambda o: o["decor"][0].update(type="candle"),
                   lambda o: o["decor"][0]["evidence"][0].update(method="dream")):
        broken = copy.deepcopy(out)
        mutate(broken)
        with pytest.raises(jsonschema.ValidationError):
            B.validate(broken)


def test_cli_ask_then_apply(tmp_path):
    b = living()
    src = tmp_path / "building_furnished.json"
    B.save(b, src)
    answers = tmp_path / "decor_ai_answers.json"
    client = FakeClient(choose(("f_L0_002.centre", "plant_small", "sage green")))
    assert DA.main(["ask", str(src), "--answers", str(answers), "--model", "fake/qwen"],
                   client_factory=lambda: client) == DA.EXIT_OK
    out = tmp_path / "building_decor.json"
    assert DA.main(["apply", str(src), "--answers", str(answers), "--out", str(out), "--debug",
                    str(tmp_path / "decor_debug")]) == DA.EXIT_OK
    doc = B.load(out)
    assert [d["type"] for d in doc["decor"] if d["method"] == "ai"] == ["plant_small"]
    summary = json.loads((tmp_path / "decor_ai.json").read_text())
    assert summary["items_ai"] == 1 and summary["rooms_ai"] == 1
    report = (tmp_path / "decor_report.md").read_text()
    assert "AI decor" in report and "| Room (r_L0_room) |" in report
    assert (tmp_path / "decor_debug" / f"{RID}.json").is_file()
    dead = FakeClient(choose(), transport={1, 2})
    assert DA.main(["ask", str(src), "--answers", str(tmp_path / "a2.json"), "--model", "fake/qwen"],
                   client_factory=lambda: dead) == DA.EXIT_SERVER


# --------------------------------------------------------------------------
# Builder helpers (pure)
# --------------------------------------------------------------------------

def test_surface_points_walk_towards_the_host_centre():
    pts = F.surface_points((1.0, 1.0), (2.0, 3.0))
    assert pts[0] == (1.0, 1.0) and pts[-1] == (2.0, 3.0) and len(pts) == F.SURFACE_RAY_STEPS + 1
    host = {"type": "nightstand"}
    assert F.on_surface({"type": "vase"}, host) and F.on_surface({"type": "table_lamp"}, host)
    assert F.on_surface({"type": "book_set", "method": "ai"}, {"type": "desk"})
    assert not F.on_surface({"type": "book_set", "method": "ai"}, {"type": "bookshelf"})
    assert not F.on_surface({"type": "book_set"}, {"type": "desk"})            # the M4 books: type height
    assert not F.on_surface({"type": "vase"}, None) and not F.on_surface({"type": "cushion"}, host)


def test_parametric_mirror_and_tabletop_decor_stay_in_their_boxes():
    for dtype in ("vase", "bowl", "plant_small", "table_lamp", "mirror"):
        parts = P.decor_parts(dtype, 0.4, 0.3, 0.5)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x1 - x0 <= 0.4 + 1e-9 and y1 - y0 <= 0.3 + 1e-9 and z1 - z0 <= 0.5 + 1e-9 and z0 == 0.0
        assert any(p["key"].startswith(P.ACCENT_PREFIX) for p in parts)     # the part the AI's colour tints
    glass = [p for p in P.decor_parts("mirror", 0.6, 0.03, 0.8) if p["key"] == "mirror"]
    assert len(glass) == 1 and min(v[1] for v in glass[0]["verts"]) == pytest.approx(-0.015)   # on the front face
    assert F.mirror_box({"size": [0.6, 0.04], "max_height_m": 0.5}) == [0.6, P.MIRROR_FRAME_M, 0.5]
    assert F.mirror_box({"size": [0.6, 0.04]})[2] == pytest.approx(0.75)
    assert P.decor_rest_height("dresser", 0.8, "mirror") == 0.0


# --------------------------------------------------------------------------
# Library models of the new decor (wenart/furniture/fit.py)
# --------------------------------------------------------------------------

def _decor_entry(eid, dtype, bbox, name, styles=("neutral",), kind="decor", source="abo"):
    out = {"id": eid, "type": f"decor_{dtype}" if kind == "decor" else dtype, "source": source, "licence": "CC-BY-4.0",
           "bbox_m": list(bbox), "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [0, 0, 0],
           "front_axis_confidence": "low", "glb": f"models/{source}/{eid}.glb", "sha256_glb": "0" * 64,
           "styles": list(styles), "name": name, "kind": kind}
    if kind == "decor":
        out["decor_type"] = dtype
    return out


class _Cat:
    def __init__(self, decor=(), entries=()):
        self.decor, self.entries = list(decor), list(entries)

    def decor_candidates(self, dtype):
        return [e for e in self.decor if e.get("decor_type") == dtype]


def test_tabletop_decor_keeps_its_real_size_and_prefers_the_colour():
    from wenart.furniture import fit as FIT
    cat = _Cat(decor=[_decor_entry("v_white", "vase", (0.15, 0.15, 0.30), "Ceramic Vase, White"),
                      _decor_entry("v_teal", "vase", (0.12, 0.12, 0.25), "Stoneware Flower Vase - 7 Inch, Teal"),
                      _decor_entry("v_big", "vase", (0.30, 0.30, 0.60), "Floor Vase, Teal")])
    item = {"type": "vase", "size": [0.18, 0.18, 0.40], "host_id": "f1", "colour": "teal"}
    asset = FIT.fit_decor_item(item, cat, "scandinavian")
    assert asset["asset_id"] in ("v_teal", "v_big") and asset["pick"]["colour_matches"] == 2
    assert asset["target"] == "within" and asset["fit_scale"][0] == asset["fit_scale"][1] == asset["fit_scale"][2]
    by = {e["id"]: FIT._decor_fit(e, item, "vase") for e in cat.decor}
    assert by["v_teal"]["bbox_m"] == [0.12, 0.12, 0.25] and by["v_teal"]["fit_scale"] == [1.0, 1.0, 1.0]  # never up
    assert by["v_big"]["fit_scale"][0] == pytest.approx(0.6) and by["v_big"]["bbox_m"][2] == pytest.approx(0.36)
    # No colour match: every fitting model stays in the pick.
    plain = FIT.fit_decor_item(dict(item, colour="burgundy"), cat, "scandinavian")
    assert plain["pick"]["colour_matches"] == 0 and plain["pick"]["of"] == 3


def test_a_floor_plant_may_be_a_potted_plant_model():
    from wenart.furniture import fit as FIT
    plant = _decor_entry("gen_pp", "potted_plant", (0.5, 0.5, 1.1), "generated potted plant", kind="furniture",
                         source="generated")
    asset = FIT.fit_decor_item({"type": "plant", "size": [0.4, 0.4], "id": "dec_1"}, _Cat(entries=[plant]),
                               "japandi")
    assert asset is not None and asset["asset_id"] == "gen_pp" and asset["decor_type"] == "plant"
    assert FIT.fit_decor_item({"type": "plant", "size": [0.4, 0.4]}, _Cat(), "japandi") is None
