"""The layout stage end to end (docs/milestone12.md §4.3-§4.5): synthetic-01's empty rooms (L1: five rooms without
documented furniture, L0: hall and kitchen) solved in functional groups, the vision model's choice among the
solver's candidates (a fake client), the request, the prompt and the CLI. The Milestone 4 text schema and prompt
stay tested here (``LayoutClient.propose``, the fake-server run)."""
import json

import pytest
from shapely.geometry import Polygon

from wenart import building as B
from wenart.furniture import group_checks as GC
from wenart.furniture import layout as L
from wenart.furniture import placer as P
from wenart.furniture import prompts, schemas
from wenart.recognition.schemas import grammar_problems
from wenart.synthetic.blocks import BLOCKS

from conftest import load_truth
from test_complete import MODEL, FakeChooser

L1_EMPTY = {"r_L1_ebeveyn_yatak_odasi", "r_L1_hol", "r_L1_yatak_odasi", "r_L1_banyo", "r_L1_cocuk_odasi"}


def pc(ftype, center, rotation=0.0, size=None, wall=True, reason="test"):
    return {"type": ftype, "center": list(center), "rotation_deg": rotation,
            "size": list(size or schemas.default_size(ftype)), "against_wall": wall, "reason": reason}


@pytest.fixture(scope="module")
def furnished():
    building = load_truth("synthetic-01")
    client = FakeChooser(picks={"r_L1_yatak_odasi": 1})
    out, layouts = L.furnish_building(building, "Scandinavian, light oak floor", client, passes=2)
    return building, out, layouts, client


def by_room(out):
    rooms = {}
    for f in out["furniture"]:
        if f["source"] == "added_by_ai":
            rooms.setdefault(f["room_id"], []).append(f)
    return rooms


def test_every_empty_room_is_solved_and_asked_once(furnished):
    building, out, layouts, client = furnished
    assert L1_EMPTY <= {l.room_id for l in layouts}
    assert L1_EMPTY <= set(client.calls) and len(client.calls) == len(set(client.calls))
    assert not any(r["id"] in client.calls for r in building["rooms"] if r["has_documented_furniture"])
    for l in layouts:
        assert l.program["groups"] and l.candidates and not l.skipped, l.room_id
        assert [c["rank"] for c in l.candidates] == list(range(1, len(l.candidates) + 1))


def test_furnished_building_is_valid_and_documents_untouched(furnished):
    building, out, layouts, client = furnished
    B.validate(out)
    kept = [f for f in out["furniture"] if f["source"] == "from_documents"]
    assert json.dumps(building["furniture"], sort_keys=True) == json.dumps(kept, sort_keys=True)
    assert json.dumps(building["rooms"], sort_keys=True) == json.dumps(out["rooms"], sort_keys=True)


def test_added_pieces_carry_their_group_evidence_and_checks(furnished):
    _b, out, layouts, _c = furnished
    added = [f for f in out["furniture"] if f["source"] == "added_by_ai"]
    ids = [f["id"] for f in added]
    assert added and len(ids) == len(set(ids))
    chosen = {l.room_id: l.chosen for l in layouts}
    for f in added:
        assert f["status"] == "verified" and f["type_raw"] is None and f["asset"] is None and f["method"] == "rule"
        assert f["evidence"][0]["method"] == "derived" and "group solver" in f["evidence"][0]["text"]
        choice = f["evidence"][-1]
        assert choice["method"] == "ai" and choice["model"] == MODEL and "chosen by the vision model" in choice["text"]
        assert set(f["checks"]) == set(P.CHECKS) and all(f["checks"].values())
        assert f["height"] == schemas.HEIGHTS[f["type"]]
        assert f["front_deg"] == pytest.approx((270 + f["footprint"]["rotation_deg"]) % 360)
        assert f["group"]["group_id"].startswith(f["room_id"] + ".") and f["group"]["role"] in ("anchor", "partner")
        assert f["layout"]["candidate"] == chosen[f["room_id"]] and "completes_room" not in f
    assert chosen["r_L1_yatak_odasi"] == 1 and chosen["r_L1_ebeveyn_yatak_odasi"] == 2


def test_bedrooms_get_beds_with_nightstands_and_nothing_blocks_a_door(furnished):
    building, out, _l, _c = furnished
    rooms = by_room(out)
    for rid in ("r_L1_ebeveyn_yatak_odasi", "r_L1_yatak_odasi", "r_L1_cocuk_odasi"):
        bed = next(f for f in rooms[rid] if f["type"] in schemas.ANCHOR_TYPES["bedroom"])
        stands = [f for f in rooms[rid] if f["type"] == "nightstand"]
        assert stands and all(f["group"]["anchor_id"] == bed["id"] for f in stands), rid
        sides = {GC.nightstand_place(P.drawn_piece(bed), P.drawn_piece(f))["side"] for f in stands}
        assert len(sides) == len(stands), rid                             # one per side, at the head
    for rid, pieces in rooms.items():
        room = next(r for r in out["rooms"] if r["id"] == rid)
        ctx = P.room_context(out, room)
        placed = [P.piece_from_furniture(f, i) for i, f in enumerate(pieces)]
        for p in placed:
            assert Polygon(room["polygon"]).buffer(-0.019).contains(p.polygon()), (rid, p.type)
            for door in ctx.doors:
                assert p.polygon().intersection(door.zone).area < P.AREA_EPS, (rid, p.type, door.id)


def test_no_group_check_fails_in_a_furnished_room(furnished):
    building, out, layouts, _c = furnished
    for l in layouts:
        found = [v for v in GC.check_room(out, l.room_id) if v["severity"] in ("critical", "major")]
        assert not found, (l.room_id, found)


def test_report_summary_and_warnings(furnished):
    _b, out, layouts, _c = furnished
    report = L.layout_report(layouts, out)
    assert report.startswith("# AI layout: synthetic-01") and "| Yatak Odası (r_L1_yatak_odasi) | bedroom |" in report
    assert "Choices of the vision model:" in report
    summary = L.layout_summary(layouts, out, "http://x/v1", MODEL)
    assert summary["pieces_added"] == sum(len(v) for v in by_room(out).values())
    entry = next(r for r in summary["rooms"] if r["room_id"] == "r_L1_banyo")
    assert entry["chosen"] == 2 and entry["choice"]["by"] == "vlm" and entry["candidates"][0]["terms"]
    json.dumps(summary)


def test_a_room_without_a_usable_candidate_stays_empty_and_is_reported():
    building = load_truth("synthetic-01")
    hall = next(r for r in building["rooms"] if r["id"] == "r_L1_hol")
    x0, y0 = hall["polygon"][0]
    hall["polygon"] = [[x0, y0], [x0 + 1.0, y0], [x0 + 1.0, y0 + 1.0], [x0, y0 + 1.0]]    # 1 m²: no entrance group
    hall["area_computed"] = 1.0
    out, layouts = L.furnish_building(building, "x", FakeChooser())
    layout = next(l for l in layouts if l.room_id == "r_L1_hol")
    assert layout.pieces == [] and layout.skipped and "r_L1_hol" not in by_room(out)
    assert any(w.startswith("r_L1_hol: no AI furniture") for w in out["warnings"])
    assert "room stays empty" in L.layout_report(layouts, out)


def test_brief_can_switch_ai_furnishing_off():
    building = load_truth("synthetic-01")
    building["project"]["brief"] = {"empty_rooms": "none"}
    client = FakeChooser()
    out, layouts = L.furnish_building(building, "x", client)
    assert client.calls == [] and not by_room(out)
    assert all(l.skipped and "empty_rooms" in l.skipped for l in layouts)


def test_layout_is_deterministic():
    building = load_truth("synthetic-01")
    a = L.furnish_building(building, "x", FakeChooser())[0]
    b = L.furnish_building(building, "x", FakeChooser())[0]
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_dining_rooms_are_furnished_and_prayer_rooms_never():
    """docs/milestone7.md §0 and §6.5: a dining room gets the dining group (anchor: the dining table, chairs around
    it); a prayer room is never asked, it is listed as skipped with the reason and stays empty."""
    building = load_truth("synthetic-01")
    rooms = {r["id"]: r for r in building["rooms"]}
    rooms["r_L1_yatak_odasi"]["room_type"] = "dining"
    rooms["r_L1_banyo"]["room_type"] = "prayer"
    assert schemas.ANCHOR_TYPES["dining"] == ("table_dining",) and "dining" in schemas.FURNISHABLE_ROOM_TYPES
    assert "prayer" not in schemas.FURNISHABLE_ROOM_TYPES and schemas.NOT_FURNISHED_ROOM_TYPES == ("prayer", "stair", "shaft")
    assert [r["id"] for r in L.not_furnished_rooms(building)] == ["r_L1_banyo"]
    client = FakeChooser()
    out, layouts = L.furnish_building(building, "x", client)
    assert "r_L1_banyo" not in client.calls and "r_L1_yatak_odasi" in client.calls
    prayer = next(l for l in layouts if l.room_id == "r_L1_banyo")
    assert prayer.pieces == [] and prayer.candidates == [] and "never furnished by AI" in prayer.skipped
    assert any(w.startswith("r_L1_banyo: no AI furniture, prayer room: never furnished by AI") for w in out["warnings"])
    dining = by_room(out)["r_L1_yatak_odasi"]
    table = next(f for f in dining if f["type"] == "table_dining")
    chairs = [f for f in dining if f["type"] == "chair"]
    assert len(chairs) >= 2 and all(f["group"]["anchor_id"] == table["id"] for f in chairs)
    assert set(prompts.ROOM_TYPE_TEXT) >= set(schemas.ALLOWED_TYPES) | {"prayer"}
    assert set(prompts.ROOM_GUIDE) == set(prompts.ROOM_TYPE_TEXT)


# --------------------------------------------------------------------------
# The choice: prompt, schema, request
# --------------------------------------------------------------------------

def test_choice_schema_and_prompt(furnished):
    _b, out, layouts, client = furnished
    schema = prompts.choice_schema(3)
    assert grammar_problems(schema) == [] and schema["additionalProperties"] is False
    assert schema["properties"]["candidate"]["enum"] == [1, 2, 3] and schema["required"] == ["candidate", "reason"]
    room = next(l for l in layouts if l.room_id == "r_L1_ebeveyn_yatak_odasi")
    prompt = client.prompts[room.room_id]
    assert prompt.endswith("Answer only with JSON.") and "Ebeveyn Yatak Odası" in prompt and "Scandinavian" in prompt
    for c in room.candidates:
        assert f"Candidate {c['rank']}: score {c['score']:.1f}" in prompt
    assert "sleeping_double (bed_nightstands" in prompt and "terms (0-1, higher is better)" in prompt
    assert "The documents draw some furniture" not in prompt                  # an empty room
    assert client.images[room.room_id] == [f"{room.room_id}_c{k}.png" for k in (1, 2, 3)]


def test_the_choice_request_carries_the_labelled_images(tmp_path, monkeypatch):
    from wenart.recognition import vlm_client

    seen = []

    def answer(url, body, timeout_s):
        seen.append(body)
        return {"choices": [{"message": {"content": json.dumps({"candidate": 2, "reason": "balanced"})}}]}

    monkeypatch.setattr(vlm_client, "post_json", answer)
    images = []
    for k in (1, 2):
        path = tmp_path / f"r_c{k}.png"
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(1, 1))
        fig.savefig(path)
        plt.close(fig)
        images.append(path)
    client = L.LayoutClient("http://127.0.0.1:1/v1", model="m", retries=1)
    p = client.choose("which?", images, ["Candidate 1:", "Candidate 2:"], prompts.choice_schema(2))
    assert p.data == {"candidate": 2, "reason": "balanced"} and not p.transport_error
    body = seen[0]
    assert body["temperature"] == 0.0 and body["structured_outputs"] == {"json": prompts.choice_schema(2)}
    parts = body["messages"][1]["content"]
    kinds = [x["type"] for x in parts]
    assert kinds == ["text", "image_url", "text", "image_url", "text"]
    assert parts[0]["text"] == "Candidate 1:" and parts[-1]["text"] == "which?"
    assert body["messages"][0]["content"] == prompts.CHOICE_SYSTEM_PROMPT


def test_a_dead_server_is_asked_once(monkeypatch, tmp_path):
    from wenart.recognition import vlm_client

    calls = []

    def dead(url, body, timeout_s):
        calls.append(1)
        raise vlm_client.VLMError(f"cannot reach {url}: Connection refused")

    monkeypatch.setattr(vlm_client, "post_json", dead)
    client = L.LayoutClient("http://127.0.0.1:1/v1", model="m", retries=1)
    building = load_truth("synthetic-01")
    out, layouts = L.furnish_building(building, "x", client)
    assert len(calls) == 1 and client.down and "cannot reach" in client.down
    assert all(l.choice["by"] == "default" and l.chosen == 1 for l in layouts if l.choice)
    assert by_room(out)


# --------------------------------------------------------------------------
# Milestone 4 schema and prompt (kept for LayoutClient.propose and the fake-server run)
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
    assert schemas.DOCUMENTED_ONLY_TYPES == ("stair", "side_table", "floor_lamp", "potted_plant")
    never = (schemas.DOCUMENTED_ONLY_TYPES + schemas.RULE_ONLY_TYPES + schemas.CHANGE_ONLY_TYPES
             + schemas.ISLAND_ONLY_TYPES)
    assert set(schemas.LAYOUT_TYPES) == schema_types - set(never)
    assert not set(schemas.DOCUMENTED_ONLY_TYPES) & {t for types in schemas.ALLOWED_TYPES.values() for t in types}


def test_schema_is_strict():
    good = {"pieces": [pc("sofa", (1, 1))]}
    assert schemas.is_valid(good)
    assert not schemas.is_valid({"pieces": [dict(pc("sofa", (1, 1)), extra=1)]})
    assert not schemas.is_valid({"pieces": [pc("unknown", (1, 1), size=(1.0, 1.0))]})
    assert not schemas.is_valid({"pieces": [], "note": "x"})
    assert "$schema" not in schemas.grammar_schema() and schemas.grammar_schema()["additionalProperties"] is False


def test_layout_prompt_lists_types_sizes_and_the_room():
    building = load_truth("synthetic-01")
    room = next(r for r in building["rooms"] if r["id"] == "r_L1_ebeveyn_yatak_odasi")
    doors, windows = P.room_openings(building, room)
    p1 = prompts.layout_prompt(room, doors, windows, "Scandinavian", 1)
    assert p1.endswith("Answer only with JSON.") and "Ebeveyn Yatak Odası" in p1 and "YATAK ODASI" in p1
    for ftype in schemas.layout_types("bedroom"):
        assert f"- {ftype}: height {schemas.HEIGHTS[ftype]} m" in p1


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
    client = FakeChooser()
    rc = L.main([str(src), "--out", str(out), "--debug", str(tmp_path / "dbg"), "--server", "http://127.0.0.1:1/v1"],
                client_factory=lambda: client)
    assert rc == 0
    furnished = B.load(out)
    assert any(f["source"] == "added_by_ai" for f in furnished["furniture"])
    summary = json.loads((out.parent / "layout.json").read_text())
    assert summary["model"] == MODEL and summary["server"] == "http://127.0.0.1:1/v1"
    assert {r["room_id"] for r in summary["rooms"]} >= L1_EMPTY and summary["solve_s"] > 0
    assert summary["vision_model_down"] is None
    assert (out.parent / "layout_report.md").read_text().startswith("# AI layout: synthetic-01")
    for rid in L1_EMPTY:
        assert (tmp_path / "dbg" / f"{rid}.json").exists() and (tmp_path / "dbg" / f"{rid}.png").exists()
        assert (tmp_path / "dbg" / f"{rid}_c1.png").exists()
    record = json.loads((tmp_path / "dbg" / "r_L1_cocuk_odasi.json").read_text())
    assert record["candidates_full"][0]["pieces"] and record["program_full"]["groups"] and record["choice_full"]


def test_cli_refuses_a_needs_review_building(tmp_path):
    building = load_truth("synthetic-01")
    building["status"] = "needs_review"
    src = tmp_path / "building.json"
    B.save(building, src)
    rc = L.main([str(src), "--out", str(tmp_path / "x.json")], client_factory=FakeChooser)
    assert rc == 2 and not (tmp_path / "x.json").exists()


# --------------------------------------------------------------------------
# Transport errors (docs/milestone6.md §2.6)
# --------------------------------------------------------------------------

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
