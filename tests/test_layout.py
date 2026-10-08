"""Layout end to end with a fake client on synthetic-01 (L1: five rooms without
documented furniture), prompt/schema consistency and the CLI."""
import json

import pytest
from shapely.geometry import Polygon

from wenart import building as B
from wenart.furniture import layout as L
from wenart.furniture import placer as P
from wenart.furniture import prompts, schemas
from wenart.synthetic.blocks import BLOCKS

from conftest import load_truth

L1_EMPTY = {"r_L1_ebeveyn_yatak_odasi", "r_L1_hol", "r_L1_yatak_odasi", "r_L1_banyo", "r_L1_cocuk_odasi"}


def pc(ftype, center, rotation=0.0, size=None, wall=True, reason="test"):
    return {"type": ftype, "center": list(center), "rotation_deg": rotation,
            "size": list(size or schemas.default_size(ftype)), "against_wall": wall, "reason": reason}


# (room id, pass) -> answer dict, or an error string. Rooms not listed answer no pieces.
FIXED = {
    # Master bedroom: both passes agree on the bed (0.9); the nightstands and the wardrobe only in pass 1 (0.6).
    ("r_L1_ebeveyn_yatak_odasi", 1): {"pieces": [
        pc("bed_double", (2.0, 3.15), reason="headboard on the north wall"),
        pc("nightstand", (0.95, 3.95)), pc("nightstand", (3.05, 3.95)),
        pc("wardrobe", (0.55, 1.0), 90.0, size=(1.2, 0.6))]},
    ("r_L1_ebeveyn_yatak_odasi", 2): {"pieces": [
        pc("bed_double", (2.1, 3.1)), pc("wardrobe", (3.93, 0.95), 270.0, size=(1.2, 0.6))]},
    # Children's room: a chair on the door strip in pass 1, pass 2 fails -> pass 1 wins, all 0.6.
    ("r_L1_cocuk_odasi", 1): {"pieces": [
        pc("bed_single", (1.0, 5.9)), pc("desk", (3.0, 6.5)), pc("chair", (4.0, 5.5), wall=False)]},
    ("r_L1_cocuk_odasi", 2): "error: cannot reach the server",
    # Bedroom: identical answers.
    ("r_L1_yatak_odasi", 1): {"pieces": [pc("bed_double", (7.7, 2.95))]},
    ("r_L1_yatak_odasi", 2): {"pieces": [pc("bed_double", (7.7, 2.95))]},
    # Bathroom: three pieces, pass 2 proposes one that cannot be placed -> pass 1 (fewest dropped).
    ("r_L1_banyo", 1): {"pieces": [pc("washbasin", (7.0, 6.7)), pc("toilet", (8.5, 6.6)), pc("shower", (8.9, 4.5))]},
    ("r_L1_banyo", 2): {"pieces": [pc("washbasin", (7.0, 6.7)), pc("toilet", (8.5, 6.6)), pc("shower", (8.9, 4.5)),
                                   pc("bathtub", (7.7, 5.5), wall=False)]},
    # Hall: nothing usable in either pass.
    ("r_L1_hol", 1): {"pieces": []},
    ("r_L1_hol", 2): {"pieces": []},
}


class FakeClient:
    """Answers from FIXED; records the prompts and the passes it was asked for."""
    model = "fake/layout-model"
    _model = "fake/layout-model"

    def __init__(self, table=None):
        self.table = FIXED if table is None else table
        self.calls = []
        self.completion_calls = []

    def complete(self, prompt, schema, pass_no):
        """Milestone 10: the furnished rooms' completion question; this fake changes and adds nothing."""
        room_id = json.loads(prompt.split("Room (metres, X right, Y up):\n", 1)[1].split("\n\n", 1)[0])["room_id"]
        self.completion_calls.append((room_id, pass_no))
        answer = {"changes": [], "added": []}
        return L.Proposal(pass_no, answer, raw_text=json.dumps(answer), latency_s=1.0, prompt=prompt, model=self.model)

    def propose(self, prompt, pass_no):
        room_id = json.loads(prompt.split("Room (metres, X right, Y up):\n", 1)[1].split("\n\n", 1)[0])["room_id"]
        self.calls.append((room_id, pass_no))
        answer = self.table.get((room_id, pass_no), {"pieces": []})
        if isinstance(answer, str):
            return L.Proposal(pass_no, None, error=answer, latency_s=0.5, prompt=prompt, model=self.model)
        assert not schemas.validation_errors(answer), schemas.validation_errors(answer)
        return L.Proposal(pass_no, answer, raw_text=json.dumps(answer), latency_s=1.5, prompt=prompt, model=self.model)


@pytest.fixture(scope="module")
def furnished():
    building = load_truth("synthetic-01")
    client = FakeClient()
    out, layouts = L.furnish_building(building, "Scandinavian, light oak floor", client, passes=2)
    return building, out, layouts, client


def by_room(out):
    rooms = {}
    for f in out["furniture"]:
        if f["source"] == "added_by_ai":
            rooms.setdefault(f["room_id"], []).append(f)
    return rooms


def test_every_empty_room_was_asked_twice(furnished):
    building, out, layouts, client = furnished
    asked = {r for r, _ in client.calls}
    assert L1_EMPTY <= asked
    assert all(len([c for c in client.calls if c[0] == r]) == 2 for r in L1_EMPTY)
    assert {l.room_id for l in layouts} == asked
    assert not any(r["id"] in asked for r in building["rooms"] if r["has_documented_furniture"])


def test_furnished_building_is_valid_and_documents_untouched(furnished):
    building, out, layouts, client = furnished
    B.validate(out)
    original = [f for f in building["furniture"]]
    kept = [f for f in out["furniture"] if f["source"] == "from_documents"]
    assert json.dumps(original, sort_keys=True) == json.dumps(kept, sort_keys=True)
    assert json.dumps(building["rooms"], sort_keys=True) == json.dumps(out["rooms"], sort_keys=True)


def test_added_pieces_carry_evidence_and_checks(furnished):
    _b, out, _l, _c = furnished
    added = [f for f in out["furniture"] if f["source"] == "added_by_ai"]
    assert added
    ids = [f["id"] for f in added]
    assert len(ids) == len(set(ids)) and all(i.startswith("f_L1_") for i in ids)
    for f in added:
        assert f["status"] == "verified" and f["type_raw"] is None and f["asset"] is None
        ev = f["evidence"][0]
        assert ev["method"] == "ai" and ev["model"] == "fake/layout-model" and ev["pass"] in (1, 2) and ev["text"]
        assert set(f["checks"]) == set(P.CHECKS) and all(f["checks"].values())
        assert f["height"] == schemas.HEIGHTS[f["type"]]
        assert f["front_deg"] == pytest.approx((270 + f["footprint"]["rotation_deg"]) % 360)
        assert f["layout"]["proposed"]["center"] and isinstance(f["layout"]["repairs"], list)


def test_agreement_confidences(furnished):
    _b, out, layouts, _c = furnished
    rooms = by_room(out)
    master = {f["type"]: f["evidence"][0]["confidence"] for f in rooms["r_L1_ebeveyn_yatak_odasi"]}
    assert master["bed_double"] == 0.9 and master["nightstand"] == 0.6 and master["wardrobe"] == 0.6
    assert {f["evidence"][0]["confidence"] for f in rooms["r_L1_yatak_odasi"]} == {0.9}
    # Pass 2 of the children's room failed: nothing to agree with.
    assert {f["evidence"][0]["confidence"] for f in rooms["r_L1_cocuk_odasi"]} == {0.6}
    chosen = {l.room_id: l.chosen_pass for l in layouts}
    assert chosen["r_L1_ebeveyn_yatak_odasi"] == 1 and chosen["r_L1_cocuk_odasi"] == 1
    assert chosen["r_L1_banyo"] == 1 and chosen["r_L1_hol"] is None


def test_bedrooms_got_beds_and_nothing_blocks_a_door(furnished):
    building, out, _l, _c = furnished
    rooms = by_room(out)
    for rid in ("r_L1_ebeveyn_yatak_odasi", "r_L1_yatak_odasi", "r_L1_cocuk_odasi"):
        assert any(f["type"] in schemas.ANCHOR_TYPES["bedroom"] for f in rooms[rid]), rid
    for rid, pieces in rooms.items():
        room = next(r for r in out["rooms"] if r["id"] == rid)
        ctx = P.room_context(out, room)
        placed = [P.piece_from_furniture(f, i) for i, f in enumerate(pieces)]
        for p in placed:
            assert Polygon(room["polygon"]).buffer(-0.019).contains(p.polygon()), (rid, p.type)
            for door in ctx.doors:
                assert p.polygon().intersection(door.zone).area < P.AREA_EPS, (rid, p.type, door.id)
        assert not P.walkway_failures(placed, ctx), rid
        for c in P.check_all(placed, ctx):
            assert not P.failed_checks(c), (rid, c)


def test_chair_on_the_door_was_repaired_or_dropped(furnished):
    _b, out, layouts, _c = furnished
    layout = next(l for l in layouts if l.room_id == "r_L1_cocuk_odasi")
    placement = layout.placements[1]
    chair_steps = [e for e in placement.log if e["type"] == "chair"]
    assert chair_steps and chair_steps[0]["failed"]
    chairs = [f for f in by_room(out)["r_L1_cocuk_odasi"] if f["type"] == "chair"]
    if chairs:
        assert chairs[0]["layout"]["repairs"]
    else:
        assert any(d["type"] == "chair" for d in placement.dropped)


def test_empty_answer_leaves_the_room_empty_and_is_reported(furnished):
    _b, out, layouts, _c = furnished
    hol = next(l for l in layouts if l.room_id == "r_L1_hol")
    assert hol.pieces == [] and hol.skipped and "nothing usable" in hol.skipped
    assert "r_L1_hol" not in by_room(out)
    assert any(w.startswith("r_L1_hol: no AI furniture") for w in out["warnings"])
    report = L.layout_report(layouts, out)
    assert "r_L1_hol" in report and "room stays empty" in report
    assert "bed_double (0.9)" in report and "nightstand (0.6)" in report
    summary = L.layout_summary(layouts, out, "http://x/v1", "fake/layout-model")
    hol_entry = next(r for r in summary["rooms"] if r["room_id"] == "r_L1_hol")
    assert hol_entry["chosen_pass"] is None and hol_entry["latency_s"] == pytest.approx(3.0)
    assert summary["pieces_added"] == len(by_room(out).get("r_L1_ebeveyn_yatak_odasi", [])) + sum(
        len(v) for k, v in by_room(out).items() if k != "r_L1_ebeveyn_yatak_odasi")


def test_brief_can_switch_ai_furnishing_off():
    building = load_truth("synthetic-01")
    building["project"]["brief"] = {"empty_rooms": "none"}
    client = FakeClient()
    out, layouts = L.furnish_building(building, "x", client)
    assert client.calls == [] and not by_room(out)
    assert all(l.skipped and "empty_rooms" in l.skipped for l in layouts)


# --------------------------------------------------------------------------
# Prompt, schema, request
# --------------------------------------------------------------------------

def test_default_sizes_are_the_drawing_block_sizes():
    blocks = schemas.block_sizes()
    for ftype, options in schemas.SIZE_OPTIONS.items():
        assert len(options) == 3 and all(w > 0 and d > 0 for w, d in options)
        areas = [w * d for w, d in options]
        assert areas[0] <= areas[1] <= areas[2]
        if ftype in blocks:
            assert schemas.default_size(ftype) in blocks[ftype], ftype
        assert ftype in schemas.HEIGHTS
    assert {t for t, _w, _d in BLOCKS.values()} <= set(schemas.SIZE_OPTIONS)
    schema_types = set(B.load_schema()["$defs"]["furniture"]["properties"]["type"]["enum"]) - {"unknown"}
    assert set(schemas.SIZE_OPTIONS) == schema_types                    # the fit and the placer know every type
    # docs/milestone7.md §6.5: every schema type except the documented-only ones can be proposed by the layout;
    # Milestone 10: nor the rule-only wall cabinet, the change-only corner sofa or the island-only bar stool.
    assert schemas.DOCUMENTED_ONLY_TYPES == ("stair", "side_table", "floor_lamp", "potted_plant")
    never = (schemas.DOCUMENTED_ONLY_TYPES + schemas.RULE_ONLY_TYPES + schemas.CHANGE_ONLY_TYPES
             + schemas.ISLAND_ONLY_TYPES)
    assert set(schemas.LAYOUT_TYPES) == schema_types - set(never)
    assert set(never) - set(schemas.DOCUMENTED_ONLY_TYPES) == {"wall_cabinet", "sofa_corner", "bar_stool"}
    assert set(schemas.LAYOUT["properties"]["pieces"]["items"]["properties"]["type"]["enum"]) == set(schemas.LAYOUT_TYPES)
    assert not set(schemas.DOCUMENTED_ONLY_TYPES) & {t for types in schemas.ALLOWED_TYPES.values() for t in types}
    assert schemas.smaller_size("wardrobe", (1.8, 0.6)) == (1.2, 0.6)
    assert schemas.smaller_size("wardrobe", (1.2, 0.6)) is None
    assert schemas.smaller_size("sofa", (2.0, 0.9)) == (1.6, 0.9)      # not an option: next option below


def test_documented_only_types_are_never_proposed():
    for ftype in schemas.DOCUMENTED_ONLY_TYPES:
        assert not schemas.is_valid({"pieces": [pc(ftype, (1, 1))]}), ftype
        assert ftype in schemas.HEIGHTS and len(schemas.SIZE_OPTIONS[ftype]) == 3


DINING_TABLE = {
    ("r_L1_yatak_odasi", 1): {"pieces": [pc("table_dining", (7.7, 2.1), size=(1.2, 0.8), wall=False),
                                         pc("chair", (7.7, 1.4), wall=False)]},
    ("r_L1_yatak_odasi", 2): {"pieces": [pc("table_dining", (7.7, 2.1), size=(1.2, 0.8), wall=False)]},
}


def test_dining_rooms_are_furnished_and_prayer_rooms_never():
    """docs/milestone7.md §0 and §6.5: a dining room gets the dining types (anchor: the dining table); a prayer room
    is never asked, it is listed as skipped with the reason and stays empty."""
    building = load_truth("synthetic-01")
    rooms = {r["id"]: r for r in building["rooms"]}
    rooms["r_L1_yatak_odasi"]["room_type"] = "dining"
    rooms["r_L1_banyo"]["room_type"] = "prayer"
    assert schemas.ALLOWED_TYPES["dining"][:4] == ("table_dining", "chair", "dresser", "bookshelf")
    assert schemas.layout_types("dining") == ("table_dining", "chair", "dresser", "bookshelf", "sideboard",
                                              "display_cabinet", "bench")             # Milestone 10
    assert schemas.ANCHOR_TYPES["dining"] == ("table_dining",) and "dining" in schemas.FURNISHABLE_ROOM_TYPES
    assert "prayer" not in schemas.FURNISHABLE_ROOM_TYPES and schemas.NOT_FURNISHED_ROOM_TYPES == ("prayer",)
    assert [r["id"] for r in L.not_furnished_rooms(building)] == ["r_L1_banyo"]
    assert "r_L1_banyo" not in {r["id"] for r in L.empty_rooms(building)}
    client = FakeClient(DINING_TABLE)
    out, layouts = L.furnish_building(building, "x", client)
    assert "r_L1_banyo" not in {r for r, _ in client.calls} and ("r_L1_yatak_odasi", 1) in client.calls
    prayer = next(l for l in layouts if l.room_id == "r_L1_banyo")
    assert prayer.pieces == [] and prayer.proposals == [] and "never furnished by AI" in prayer.skipped
    assert any(w.startswith("r_L1_banyo: no AI furniture, prayer room: never furnished by AI") for w in out["warnings"])
    dining = {f["type"]: f for f in by_room(out)["r_L1_yatak_odasi"]}
    assert set(dining) == {"table_dining", "chair"} and dining["table_dining"]["evidence"][0]["confidence"] == 0.9
    room = rooms["r_L1_yatak_odasi"]
    doors, windows = P.room_openings(building, room)
    prompt = prompts.layout_prompt(room, doors, windows, "Scandinavian", 1)
    assert "dining room (Turkish: YEMEK ODASI)" in prompt and "one dining table in the middle" in prompt
    assert "- table_dining: height 0.75 m" in prompt and "- sofa:" not in prompt
    assert set(prompts.ROOM_TYPE_TEXT) >= set(schemas.ALLOWED_TYPES) | {"prayer"}
    assert set(prompts.ROOM_GUIDE) == set(prompts.ROOM_TYPE_TEXT)


def test_schema_is_strict():
    good = {"pieces": [pc("sofa", (1, 1))]}
    assert schemas.is_valid(good)
    assert not schemas.is_valid({"pieces": [dict(pc("sofa", (1, 1)), extra=1)]})
    assert not schemas.is_valid({"pieces": [pc("unknown", (1, 1), size=(1.0, 1.0))]})
    assert not schemas.is_valid({"pieces": [pc("sofa", (1, 1))] * 13})
    assert not schemas.is_valid({"pieces": [], "note": "x"})
    missing = pc("sofa", (1, 1))
    del missing["reason"]
    assert not schemas.is_valid({"pieces": [missing]})
    assert "$schema" not in schemas.grammar_schema() and schemas.grammar_schema()["additionalProperties"] is False


def test_prompt_lists_types_sizes_room_and_differs_per_pass():
    building = load_truth("synthetic-01")
    room = next(r for r in building["rooms"] if r["id"] == "r_L1_ebeveyn_yatak_odasi")
    doors, windows = P.room_openings(building, room)
    p1 = prompts.layout_prompt(room, doors, windows, "Scandinavian", 1)
    p2 = prompts.layout_prompt(room, doors, windows, "Scandinavian", 2)
    assert p1 != p2 and p1.endswith("Answer only with JSON.") and p2.endswith("Answer only with JSON.")
    assert "Ebeveyn Yatak Odası" in p1 and "Scandinavian" in p1 and "YATAK ODASI" in p1
    for ftype in schemas.layout_types("bedroom"):
        assert f"- {ftype}: height {schemas.HEIGHTS[ftype]} m" in p1
        for w, d in schemas.SIZE_OPTIONS[ftype]:
            assert f"[{w}, {d}]" in p1
    # Milestone 10: cribs and bunk beds only in a child's room (room_subtype: child), no double bed there.
    assert "- crib:" not in p1 and "- bunk_bed:" not in p1 and "- bench:" in p1
    child = prompts.layout_prompt(dict(room, room_subtype="child"), doors, windows, "Scandinavian", 1)
    assert "- crib:" in child and "- bunk_bed:" in child and "- bed_double:" not in child
    assert "sofa" not in p1.split("Fields of the answer")[0].split("Allowed types")[1].split("\n\n")[0]
    block = json.loads(p1.split("Room (metres, X right, Y up):\n", 1)[1].split("\n\n", 1)[0])
    assert block["room_id"] == room["id"] and len(block["doors"]) == 1 and len(block["windows"]) == 2
    assert block["doors"][0]["opens_into_this_room"] is True and block["windows"][0]["sill_height"] is None
    assert "0.9 m assumed" in p1
    for key in ("type", "center", "rotation_deg", "size", "against_wall", "reason"):
        assert f"- {key}:" in p1


def test_text_request_has_no_image_and_pass_seed():
    body = L.build_text_request("m", "hello", schemas.grammar_schema(), seed=2)
    assert body["temperature"] == 0.0 and body["seed"] == 2 and body["model"] == "m"
    assert body["messages"][1] == {"role": "user", "content": "hello"}
    assert body["structured_outputs"] == {"json": schemas.grammar_schema()}
    assert body["chat_template_kwargs"] == {"enable_thinking": False}


def test_style_text_fallbacks():
    building = load_truth("synthetic-01")
    assert L.style_text_of({"source_text": "Minimal"}, building) == "Minimal"
    assert L.style_text_of(None, building) == building["project"]["brief"]["style"]
    building["project"].pop("brief")
    assert "Scandinavian" in L.style_text_of(None, building)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def test_cli_writes_building_report_and_debug(tmp_path):
    src = tmp_path / "building.json"
    B.save(load_truth("synthetic-01"), src)
    out = tmp_path / "out" / "building_furnished.json"
    client = FakeClient()
    rc = L.main([str(src), "--out", str(out), "--debug", str(tmp_path / "dbg"), "--server", "http://127.0.0.1:1/v1"],
                client_factory=lambda: client)
    assert rc == 0
    furnished = B.load(out)
    assert any(f["source"] == "added_by_ai" for f in furnished["furniture"])
    summary = json.loads((out.parent / "layout.json").read_text())
    assert summary["model"] == "fake/layout-model" and summary["server"] == "http://127.0.0.1:1/v1"
    assert {r["room_id"] for r in summary["rooms"]} >= L1_EMPTY
    assert all(p["latency_s"] > 0 for r in summary["rooms"] for p in r["passes"])
    assert (out.parent / "layout_report.md").read_text().startswith("# AI layout: synthetic-01")
    for rid in L1_EMPTY:
        assert (tmp_path / "dbg" / f"{rid}.json").exists() and (tmp_path / "dbg" / f"{rid}.png").exists()
    record = json.loads((tmp_path / "dbg" / "r_L1_cocuk_odasi.json").read_text())
    assert record["passes"][1]["error"] and record["passes"][0]["placement"]["log"]


def test_cli_refuses_a_needs_review_building(tmp_path):
    building = load_truth("synthetic-01")
    building["status"] = "needs_review"
    src = tmp_path / "building.json"
    B.save(building, src)
    rc = L.main([str(src), "--out", str(tmp_path / "x.json")], client_factory=FakeClient)
    assert rc == 2 and not (tmp_path / "x.json").exists()


def test_types_the_room_does_not_allow_are_rejected_before_placement():
    """AI proposes, checks decide: a toilet in a bedroom never becomes added_by_ai."""
    building = load_truth("synthetic-01")
    room = next(r for r in building["rooms"] if r["room_type"] == "bedroom" and not r["has_documented_furniture"])
    cx, cy = Polygon(room["polygon"]).centroid.coords[0]
    answer = {"pieces": [
        {"type": "toilet", "center": [cx, cy], "rotation_deg": 0, "size": [0.4, 0.7], "against_wall": False,
         "reason": "wrong room"},
        {"type": "bed_double", "center": [cx, cy], "rotation_deg": 0, "size": [1.6, 2.0], "against_wall": True,
         "reason": "bed"},
    ]}
    client = FakeClient({(room["id"], 1): answer, (room["id"], 2): answer})
    layout = L.propose_layouts(room, building, "test style", client, passes=2)
    assert {p["type"] for p in layout.pieces} == {"bed_double"}
    assert all(p.rejected_types == ["toilet"] for p in layout.proposals)
    record = layout.to_dict()
    assert record["passes"][0]["rejected_types"] == ["toilet"] and "anchor_first" in record["passes"][0]


# --------------------------------------------------------------------------
# Transport errors (docs/milestone6.md §2.6)
# --------------------------------------------------------------------------

class TransportFailClient(FakeClient):
    """Every pass of one room could not reach the server (as LayoutClient reports it)."""

    def __init__(self, room_id):
        super().__init__()
        self.room_id = room_id

    def propose(self, prompt, pass_no):
        proposal = super().propose(prompt, pass_no)
        if self.calls[-1][0] == self.room_id:
            return L.Proposal(pass_no, None, error="cannot reach http://127.0.0.1:1/v1/chat/completions",
                              prompt=prompt, model=self.model, transport_error=True)
        return proposal


def test_cli_exits_3_and_writes_nothing_when_the_server_is_unreachable(tmp_path, capsys):
    src = tmp_path / "building.json"
    B.save(load_truth("synthetic-01"), src)
    out = tmp_path / "out" / "building_furnished.json"
    rc = L.main([str(src), "--out", str(out), "--server", "http://127.0.0.1:1/v1"],
                client_factory=lambda: TransportFailClient("r_L1_hol"))
    assert rc == 3
    assert not out.exists() and not (out.parent / "layout.json").exists()
    assert not (out.parent / "layout_report.md").exists()
    err = capsys.readouterr().err
    assert "r_L1_hol pass 1: server not reachable" in err and "exit 3" in err


def test_layout_client_flags_only_transport_errors(monkeypatch):
    """VLMError on the last attempt -> transport_error; a bad answer or a schema error is an answer."""
    from wenart.recognition import vlm_client

    def dead(url, body, timeout_s):
        raise vlm_client.VLMError(f"cannot reach {url}: Connection refused")

    monkeypatch.setattr(vlm_client, "post_json", dead)
    client = L.LayoutClient("http://127.0.0.1:1/v1", model="m", retries=1)
    p = client.propose("prompt", 1)
    assert p.transport_error and p.data is None and "cannot reach" in p.error

    def garbage(url, body, timeout_s):
        return {"choices": [{"message": {"content": "not json"}}]}

    monkeypatch.setattr(vlm_client, "post_json", garbage)
    p = client.propose("prompt", 1)
    assert not p.transport_error and p.error.startswith("bad answer")

    def wrong_schema(url, body, timeout_s):
        return {"choices": [{"message": {"content": json.dumps({"pieces": "x"})}}]}

    monkeypatch.setattr(vlm_client, "post_json", wrong_schema)
    p = client.propose("prompt", 1)
    assert not p.transport_error and p.error.startswith("schema:")

    # The first attempt fails, the retry answers: no transport error.
    calls = []

    def flaky(url, body, timeout_s):
        calls.append(1)
        if len(calls) == 1:
            raise vlm_client.VLMError("HTTP 503")
        return {"choices": [{"message": {"content": json.dumps({"pieces": []})}}]}

    monkeypatch.setattr(vlm_client, "post_json", flaky)
    monkeypatch.setattr(L.time, "sleep", lambda s: None)
    p = L.LayoutClient("http://127.0.0.1:1/v1", model="m", retries=2).propose("prompt", 1)
    assert not p.transport_error and p.error is None and p.data == {"pieces": []}


def test_layout_client_model_lookup_failure_is_a_transport_error(monkeypatch):
    from wenart.recognition import vlm_client

    monkeypatch.setattr(vlm_client, "served_models", lambda base_url: [])
    p = L.LayoutClient("http://127.0.0.1:1/v1", model=None, retries=1).propose("prompt", 2)
    assert p.transport_error and p.model == "?" and "no model served" in p.error
