"""Completion of rooms with drawn furniture through the group solver (docs/milestone12.md §4.3-§4.5; Milestone 10
§2 before), with a fake vision client that picks among the solver's candidates.

Fixtures: the M10 example building with the AI-made pieces stripped (``test_locked.drawn_building``: a drawn
sofa in the basement living room, a counter run in the kitchen, stairs in the halls, a double bed in the
bedroom, sanitary ware in the bathroom; the alternative level's hall is ``same_as`` the base hall) and a
semi-detached pair of bedrooms mirrored about a party wall at x = 4.1 (``twin_building``).
"""
import copy
import json
import math
from pathlib import Path

import pytest

from wenart import building as B
from wenart.furniture import complete as C
from wenart.furniture import group_checks as GC
from wenart.furniture import layout as L
from wenart.furniture import locked as LK
from wenart.furniture import placer as P
from wenart.furniture import schemas

from test_locked import drawn_building, example

MODEL = "fake/vision-model"


def room_of(images) -> str:
    """The room id from the candidate image names (``<room>_c<rank>.png``)."""
    return Path(images[0]).name.rsplit("_c", 1)[0]


class FakeChooser:
    """``choose`` answers ``{"candidate": picks.get(room, pick)}``; ``transport``: rooms whose call fails like a dead
    server; ``invalid``: rooms answered with a candidate number that does not exist."""
    model = MODEL
    _model = MODEL

    def __init__(self, pick=2, picks=None, transport=(), invalid=()):
        self.pick, self.picks = pick, dict(picks or {})
        self.transport, self.invalid = set(transport), set(invalid)
        self.calls, self.prompts, self.schemas, self.images = [], {}, {}, {}
        self.down = None

    def choose(self, prompt, images, labels, schema):
        rid = room_of(images)
        self.calls.append(rid)
        self.prompts[rid], self.schemas[rid], self.images[rid] = prompt, schema, [Path(p).name for p in images]
        assert labels == [f"Candidate {k}:" for k in range(1, len(images) + 1)]
        if rid in self.transport:
            self.down = "cannot reach http://127.0.0.1:1/v1"
            return L.Proposal(1, None, error=self.down, prompt=prompt, model=MODEL, transport_error=True)
        n = 99 if rid in self.invalid else min(self.picks.get(rid, self.pick), len(images))
        answer = {"candidate": n, "reason": f"candidate {n} reads best"}
        return L.Proposal(1, answer, raw_text=json.dumps(answer), latency_s=0.5, prompt=prompt, model=MODEL)


SALON, KITCHEN, HALL, HALL_ALT, BEDROOM, BATH = ("r_L-1_salon", "r_L-1_mutfak", "r_L-1_hol", "r_L-1b_hol",
                                                 "r_L0_yatak_odasi", "r_L0_banyo")
HALL_L0 = "r_L0_hol"
OPEN_KITCHEN = "r_L-1b_salon_acik_mutfak"
# style.json slots the looks are read from (absent slots give no design keys).
STYLE = {"family": "modern", "cabinets": {"front_style": "shaker", "colour": "sage", "handle": "brass", "worktop": "stone"},
         "furniture": {"by_type": {"table_coffee": {"material_tags": ["glass", "chrome"]},
                                   "sofa_corner": {"material_tags": ["fabric"]}}}}


@pytest.fixture(scope="module")
def completed():
    source = drawn_building(example())
    client = FakeChooser()
    out, records = C.complete_building(source, "Modern natural", client, C.Settings(), style=STYLE)
    return source, out, {r.room_id: r for r in records}, client


def piece(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


def added_in(b, room_id):
    return [f for f in b["furniture"] if f["room_id"] == room_id and f["source"] == "added_by_ai"]


def floor_added(b, room_id):
    return [f for f in added_in(b, room_id) if f["type"] not in schemas.MOUNTED_TYPES]


# --------------------------------------------------------------------------
# Per room type: anchors, expected (missing) and what may be added (schemas, kept from Milestone 10)
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
    ("dining", None, [("table_dining", (1.2, 0.8))], {"chair": 4}, {"sideboard", "bench"}, {"table_dining"}),
    ("kitchen", None, [("kitchen_counter", (3.0, 0.6))], {}, {"table_dining", "tall_cabinet"}, {"bar_stool"}),
    ("bathroom", None, [("toilet", (0.4, 0.7))], {}, set(), {"washbasin", "shower", "bathtub", "washing_machine"}),
    ("hall", None, [("stair", (1.0, 3.0))], {}, {"console_table", "shoe_cabinet", "bench"}, {"dresser", "stair"}),
])
def test_completion_plan_per_room_type(rtype, subtype, present, missing, may, never):
    plan = schemas.completion_plan(rtype, subtype, present)
    assert plan["missing"] == missing
    assert may <= set(plan["addable"]), (may - set(plan["addable"]), plan["addable"])
    assert not never & set(plan["addable"]), never & set(plan["addable"])


def test_change_types_and_fixed_equipment():
    assert schemas.FIXED_TYPES == ("stair", "kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge",
                                   "washing_machine", "toilet", "washbasin", "shower", "bathtub")
    assert "prayer" not in schemas.ALLOWED_TYPES                                 # prayer rooms: never furnished
    assert schemas.ALLOWED_TYPES["balcony"] == ("table_dining", "chair", "bench")   # Milestone 12: balcony group


# --------------------------------------------------------------------------
# The example end to end
# --------------------------------------------------------------------------

def test_every_furnished_room_is_handled_once(completed):
    source, out, records, client = completed
    assert set(records) == {r["id"] for r in source["rooms"] if r["has_documented_furniture"]}
    assert HALL_ALT not in client.calls and BATH not in client.calls     # same_as copy; nothing missing in the bath
    assert len(client.calls) == len(set(client.calls))                   # one question per room at most
    assert records[HALL_ALT].state == "copied" and records[HALL_ALT].partner["id"] == HALL
    assert records[BATH].state == "completed" and records[BATH].reason == "nothing missing: the drawn groups are complete"
    B.validate(out)
    assert LK.check(source, out, "complete") == []


def test_drawn_pieces_never_change(completed):
    source, out, _r, _c = completed
    for f in source["furniture"]:
        after = piece(out, f["id"])
        for key in ("type", "footprint", "front_deg", "height", "status", "source", "room_id"):
            assert after.get(key) == f.get(key), (f["id"], key)
        assert "modified_by_ai" not in after and "type_proposal" not in after


def test_completion_adds_only_the_missing_partners_and_groups(completed):
    _s, out, records, _c = completed
    salon = floor_added(out, SALON)
    assert not {"sofa", "sofa_corner"} & {f["type"] for f in salon}       # never a second anchor
    assert piece(out, "f_L-1_002")["group"] == {"group_id": f"{SALON}.seating", "group": "seating", "role": "anchor",
                                                "anchor_id": "f_L-1_002"}      # the drawn anchor is tagged too
    assert piece(out, "f_L0_008")["group"]["group"] == "bathroom_set"
    coffee = next(f for f in salon if f["type"] == "table_coffee")
    assert coffee["group"] == {"group_id": f"{SALON}.seating", "group": "seating", "role": "partner",
                               "anchor_id": "f_L-1_002"}                    # a partner of the drawn sofa
    bedroom = floor_added(out, BEDROOM)
    stands = [f for f in bedroom if f["type"] == "nightstand"]
    assert len(stands) == 2 and all(f["group"]["anchor_id"] == "f_L0_002" for f in stands)
    assert not {"bed_double", "bed_single"} & {f["type"] for f in bedroom}
    assert "wardrobe" in {f["type"] for f in bedroom}                     # the group the room type misses whole
    bed = P.drawn_piece(piece(out, "f_L0_002"))
    assert sorted(GC.nightstand_place(bed, P.drawn_piece(f))["side"] for f in stands) == ["left", "right"]
    for rid, rec in records.items():
        for f in rec.added:
            assert f["source"] == "added_by_ai" and f["completes_room"] is True and f["method"] == "rule", f["id"]
            assert f["status"] == "verified" and set(f["checks"]) == set(P.CHECKS) and all(f["checks"].values())
            assert f["group"]["group_id"].startswith(rid + ".") and f["group"]["group"] in f["group"]["group_id"]
            if rec.state == "completed":
                assert f["evidence"][0]["method"] == "derived" and "group solver" in f["evidence"][0]["text"]
    ids = [f["id"] for f in out["furniture"]]
    assert len(ids) == len(set(ids))


def test_no_new_group_check_failure_in_completed_rooms(completed):
    source, out, records, _c = completed
    for rid, rec in records.items():
        before = {(v["check"], v["target"], v["message"]) for v in GC.check_room(source, rid)}
        new = [v for v in GC.check_room(out, rid) if (v["check"], v["target"], v["message"]) not in before
               and v["severity"] in ("critical", "major") and v["check"] not in ("G14",)]
        assert not new, (rid, new)


def test_the_vision_model_picks_among_the_candidates(completed):
    _s, out, records, client = completed
    rec = records[SALON]
    assert rec.choice["by"] == "vlm" and rec.choice["rank"] == 2 and rec.chosen == 2
    assert client.images[SALON] == [f"{SALON}_c{c['rank']}.png" for c in rec.candidates if not c["hard_failures"]]
    assert client.schemas[SALON]["properties"]["candidate"]["enum"] == [1, 2, 3]
    assert "The documents draw some furniture in it" in client.prompts[SALON]
    ev = rec.added[0]["evidence"][-1]
    assert ev["method"] == "ai" and ev["model"] == MODEL and "chosen by the vision model" in ev["text"]
    assert all(f["layout"]["candidate"] == 2 for f in rec.added)


def test_a_failed_or_invalid_choice_takes_the_solvers_best():
    source = drawn_building(example())
    client = FakeChooser(invalid=[SALON], transport=[BEDROOM])
    out, records = C.complete_building(source, "x", client, C.Settings())
    rec = {r.room_id: r for r in records}
    assert rec[SALON].choice["by"] == "default" and rec[SALON].chosen == 1
    assert "no valid answer" in rec[SALON].choice["reason"]
    assert rec[BEDROOM].choice["by"] == "default" and rec[BEDROOM].choice["transport_error"] is True
    assert rec[BEDROOM].added and LK.check(source, out, "complete") == []
    no_model = C.complete_building(source, "x", object(), C.Settings())[1]
    assert all(r.choice is None or r.choice["by"] == "default" for r in no_model)


def test_completion_is_deterministic():
    source = drawn_building(example())
    a = C.complete_building(source, "x", FakeChooser(), C.Settings())[0]
    b = C.complete_building(source, "x", FakeChooser(), C.Settings())[0]
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_a_drawn_kitchen_run_gets_its_wall_cabinets_and_no_fridge_without_a_landing(completed):
    _s, out, records, _c = completed
    cabinets = [f for f in out["furniture"] if f["type"] == "wall_cabinet"]
    kitchen = [f for f in cabinets if f["room_id"] == KITCHEN]
    assert len(kitchen) == 1 and records[KITCHEN].wall_cabinets == kitchen
    cab = kitchen[0]
    assert cab["source"] == "added_by_ai" and cab["method"] == "rule" and cab["completes_room"] is True
    assert cab["evidence"][0]["method"] == "derived" and "f_L-1_004" in cab["evidence"][0]["text"]
    assert cab["rule"]["z"] == [1.45, 2.15] and cab["mount_bottom_m"] == 1.45 and cab["height"] == pytest.approx(0.7)
    assert cab["footprint"]["size"] == [3.0, 0.35] and cab["footprint"]["center"] == pytest.approx([9.825, 2.125])
    assert cab["design"] == {"front_style": "shaker", "colour": "sage", "handle": "brass"}     # style.json cabinets
    assert len([f for f in cabinets if f["room_id"] == OPEN_KITCHEN]) == 1   # an open kitchen of a living room too
    # The drawn run fills its wall: a fridge beside it finds no landing (G8), so it is left out, not forced in.
    assert "fridge" not in {f["type"] for f in floor_added(out, KITCHEN)}


def test_same_as_room_takes_the_base_rooms_pieces(completed):
    _s, out, records, _c = completed
    base, alt = floor_added(out, HALL), floor_added(out, HALL_ALT)
    assert [f["type"] for f in base] == [f["type"] for f in alt] and base
    for fb, fa in zip(base, alt):
        assert fa["footprint"]["center"] == fb["footprint"]["center"] and fa["mirrored_from"] == fb["id"]
        assert fa["level_id"] == "L-1b" and fa["id"].startswith("f_L-1b_") and all(fa["checks"].values())
        assert fa["group"]["group_id"] == fb["group"]["group_id"].replace(HALL, HALL_ALT, 1)
        assert fa["layout"]["copied_from"] == fb["id"]


def test_outputs_summary_report_and_debug(completed, tmp_path):
    _s, out, records, _c = completed
    recs = list(records.values())
    summary = C.summary(recs, out, C.Settings(), "http://x/v1", MODEL, [])
    assert summary["kind"] == "completion" and summary["changes_applied"] == 0 and summary["rooms_copied"] == 1
    assert summary["pieces_added"] == sum(len(r.added) for r in recs) and summary["wall_cabinets"] == 2
    rooms = {r["room_id"]: r for r in summary["rooms"]}
    assert rooms[SALON]["chosen"] == 2 and rooms[SALON]["candidates"][0]["rank"] == 1
    assert {"group_id": f"{SALON}.seating", "group": "seating", "options": rooms[SALON]["program"][0]["options"],
            "drawn": True, "required": True, "missing": ["tv_unit", "table_coffee"], "note": ""} \
        in rooms[SALON]["program"]
    json.dumps(summary)
    report = C.report(recs, out, C.Settings(), [])
    assert report.startswith("# AI completion of furnished rooms") and "## Locked check: pass" in report
    assert f"| Salon ({SALON}) | living | completed | seating |" in report
    assert "seating (partner, anchor f_L-1_002)" in report
    for rec in recs:
        C.write_room_debug(rec, out, tmp_path)
    assert (tmp_path / f"{SALON}.png").exists() and (tmp_path / f"{HALL_ALT}.png").exists()
    record = json.loads((tmp_path / f"{SALON}.json").read_text())
    assert record["candidates_full"][0]["pieces"] and record["program_full"]["room_id"] == SALON


# --------------------------------------------------------------------------
# Unverified and unknown anchors
# --------------------------------------------------------------------------

def test_an_unverified_drawn_bed_gets_no_partners_and_no_second_bed():
    source = drawn_building(example())
    piece(source, "f_L0_002")["status"] = "unverified"
    out, records = C.complete_building(source, "x", FakeChooser(), C.Settings())
    rec = next(r for r in records if r.room_id == BEDROOM)
    types = {f["type"] for f in floor_added(out, BEDROOM)}
    assert not types & {"nightstand", "bed_double", "bed_single"} and "wardrobe" in types
    assert any(g["note"] == "unverified anchor: nothing added" for g in rec.program["groups"])


def test_an_unknown_piece_of_bed_size_is_never_joined_by_a_second_bed():
    """Fails on the Milestone 12 draft: the program added a whole bed group beside an unknown 1.6 x 2.0 box."""
    source = drawn_building(example())
    piece(source, "f_L0_002").update(type="unknown", status="unverified")
    out, records = C.complete_building(source, "x", FakeChooser(), C.Settings())
    types = {f["type"] for f in floor_added(out, BEDROOM)}
    assert not types & {"bed_double", "bed_single", "nightstand"}
    rec = next(r for r in records if r.room_id == BEDROOM)
    note = next(g["note"] for g in rec.program["groups"] if g["group"] == "sleeping_double")
    assert note.startswith("unverified anchor: nothing added (unknown f_L0_002")


# --------------------------------------------------------------------------
# Modes: keep (M9), keep size, keep list
# --------------------------------------------------------------------------

def test_keep_mode_is_unchanged_from_m9():
    source = drawn_building(example())
    client = FakeChooser()
    out, records = C.complete_building(source, "x", client, C.Settings(mode="keep"))
    assert client.calls == [] and all(r.state == "kept" for r in records)
    no_look = [{k: v for k, v in f.items() if k not in ("design", "group")} for f in out["furniture"]]
    assert json.dumps(no_look, sort_keys=True) == json.dumps(source["furniture"], sort_keys=True)
    assert piece(out, "f_L0_007")["design"] == {"vanity": True}            # kept rooms get their looks (row 15)
    assert piece(out, "f_L0_002")["group"]["role"] == "anchor"              # and their groups (not a locked key)
    assert LK.check(source, out, "keep") == []


def test_keep_size_completes_and_changes_no_drawn_piece():
    source = drawn_building(example())
    out, records = C.complete_building(source, "x", FakeChooser(), C.Settings(keep_size=True))
    assert piece(out, "f_L-1_002")["footprint"] == piece(source, "f_L-1_002")["footprint"]
    assert "table_coffee" in {f["type"] for f in added_in(out, SALON)}


def test_furnished_rooms_keep_by_label_or_id():
    source = drawn_building(example())
    client = FakeChooser()
    out, records = C.complete_building(source, "x", client, C.Settings(keep=("salon", "r_L0_yatak_odasi")))
    states = {r.room_id: r.state for r in records}
    assert states[SALON] == "kept" and states[BEDROOM] == "kept"
    assert SALON not in client.calls and not added_in(out, SALON)
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
# Looks (furniture.design, §1.6b row 15)
# --------------------------------------------------------------------------

def test_looks_of_completed_rooms(completed):
    _s, out, _r, _c = completed
    assert piece(out, "f_L-1_004")["design"] == STYLE["cabinets"]                    # style.json cabinets
    assert piece(out, "f_L-1b_002")["design"] == STYLE["cabinets"]                   # the open kitchen's run too
    assert piece(out, "f_L0_007")["design"] == {"vanity": True}                      # washbasin 0.5 m deep
    coffee = next(f for f in added_in(out, SALON) if f["type"] == "table_coffee")
    assert coffee["design"] == {"material_tags": ["glass"]}                          # chrome is no schema tag
    assert "design" not in piece(out, "f_L0_008")                                    # a shower: nothing to say


def test_looks_without_style_slots_and_by_rule():
    source = drawn_building(example())
    out, _r = C.complete_building(source, "x", FakeChooser(), C.Settings(), style={"family": "modern"})
    assert "design" not in piece(out, "f_L-1_004")                                    # no cabinets slot: no keys
    style = {"cabinets": {"front": "slatted", "colour": 7, "handle": "gold", "worktop": "wood"}}
    out, _r = C.complete_building(source, "x", FakeChooser(), C.Settings(), style=style)
    assert piece(out, "f_L-1_004")["design"] == {"front_style": "slatted", "worktop": "wood"}   # bad values left out
    cab = next(f for f in out["furniture"] if f["type"] == "wall_cabinet")
    assert cab["design"] == {"front_style": "slatted"}                                # no worktop on a wall cabinet


@pytest.mark.parametrize("x0, x1, built_in", [(0.1, 4.0, True), (0.1, 3.0, False)])
def test_a_wardrobe_from_wall_to_wall_is_built_in(x0, x1, built_in):
    source = twin_building()
    w = round(x1 - x0, 3)
    source["furniture"].append({"id": "f_L0_003", "level_id": "L0", "room_id": TWIN_A, "type": "wardrobe",
                                "type_raw": None, "source": "from_documents", "status": "verified",
                                "evidence": [B.evidence("p.dxf", "vector", 1.0)],
                                "footprint": {"center": [(x0 + x1) / 2, 0.4], "size": [w, 0.6], "rotation_deg": 180.0},
                                "front_deg": 90.0, "height": 2.1})
    out, _r = C.complete_building(source, "x", FakeChooser(), C.Settings(twin_rooms="all"))
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


def test_twin_room_takes_the_mirrored_pieces():
    source = twin_building()
    client = FakeChooser()
    out, records = C.complete_building(source, "x", client, C.Settings(twin_rooms="one"))
    assert client.calls == [TWIN_A]                                        # asked once
    rec = {r.room_id: r for r in records}
    assert rec[TWIN_B].state == "mirrored" and rec[TWIN_B].partner["transform"]["axis_deg"] == pytest.approx(90.0)
    a = sorted(added_in(out, TWIN_A), key=lambda f: f["id"])
    b = sorted(added_in(out, TWIN_B), key=lambda f: f["id"])
    assert len(a) == len(b) and {f["type"] for f in a} >= {"nightstand", "wardrobe"}
    for fa, fb in zip(a, b):
        assert fb["type"] == fa["type"] and fb["mirrored_from"] == fa["id"] and fb["room_id"] == TWIN_B
        assert fb["footprint"]["center"] == pytest.approx([8.2 - fa["footprint"]["center"][0],
                                                           fa["footprint"]["center"][1]], abs=1e-3)
        assert math.isclose(fb["front_deg"] % 360.0, (180.0 - fa["front_deg"]) % 360.0, abs_tol=1e-6)
        assert all(fb["checks"].values()) and fb["group"]["group_id"].startswith(TWIN_B + ".")
        if fa["type"] == "nightstand":                                     # the group anchor is this room's bed
            assert fa["group"]["anchor_id"] == "f_L0_001" and fb["group"]["anchor_id"] == "f_L0_002"
        elif fa["group"]["role"] == "anchor":                              # a new anchor: its own copy
            assert fb["group"]["anchor_id"] == fb["id"]
    assert LK.check(source, out, "complete") == []
    B.validate(out)


def test_mirror_transform_maps_points_fronts_and_sides():
    t = C.Transform.mirror((4.1, 0.0), 90.0)
    assert t.point((3.0, 1.0)) == pytest.approx((5.2, 1.0)) and t.flips
    assert t.direction(0.0) == pytest.approx(180.0) and t.direction(270.0) == pytest.approx(270.0)
    assert t.rotation(90.0) == pytest.approx(270.0) and t.side("right") == "left"
    given = C.given_transform({"twin_transform": [-1.0, 0.0, 8.2, 0.0, 1.0, 0.0]})
    assert given.point((3.0, 1.0)) == pytest.approx((5.2, 1.0)) and given.side("left") == "right"
    assert C.given_transform({"twin_transform": None}) is None and C.given_transform({}) is None


def test_the_pipelines_twin_transform_is_used():
    """§1.6b row 18: ``rooms[].twin_transform`` (first twin -> this room) wins over the derived mirror."""
    source = twin_building()
    room_b = next(r for r in source["rooms"] if r["id"] == TWIN_B)
    room_b["twin_transform"] = [-1.0, 0.0, 8.2, 0.0, 1.0, 0.0]                  # x' = 8.2 - x
    out, records = C.complete_building(source, "x", FakeChooser(), C.Settings())
    rec = {r.room_id: r for r in records}
    assert rec[TWIN_B].state == "mirrored" and rec[TWIN_B].partner["transform"]["kind"] == "given"
    assert rec[TWIN_B].partner["transform"]["affine"] == [-1.0, 0.0, 8.2, 0.0, 1.0, 0.0]
    room_b["twin_transform"] = [1.0, 0.0, 4.1, 0.0, 1.0, 0.0]                   # a shift: does not map the bed
    out, records = C.complete_building(source, "x", FakeChooser(), C.Settings())
    rec = {r.room_id: r for r in records}
    assert rec[TWIN_B].state == "completed" and "does not map" in rec[TWIN_B].reason


def test_twin_rooms_all_solves_both():
    client = FakeChooser()
    C.complete_building(twin_building(), "x", client, C.Settings(twin_rooms="all"))
    assert client.calls == [TWIN_A, TWIN_B]


def test_a_twin_that_does_not_mirror_is_completed_itself():
    client = FakeChooser()
    out, records = C.complete_building(twin_building(shift=0.3), "x", client, C.Settings())
    rec = {r.room_id: r for r in records}
    assert client.calls == [TWIN_A, TWIN_B]
    assert rec[TWIN_B].state == "completed" and "has no counterpart here" in rec[TWIN_B].reason


def test_a_twin_copy_that_would_lose_a_piece_is_solved_itself():
    """Fails on the Milestone 10 copy: the copy that failed a check was dropped and the twin kept the rest."""
    source = twin_building()
    out, _r = C.complete_building(source, "x", FakeChooser(), C.Settings(twin_rooms="all"))
    mirrored = [f for f in added_in(out, TWIN_A) if f["type"] == "wardrobe"]
    assert mirrored
    x = 8.2 - mirrored[0]["footprint"]["center"][0]
    wall = "w_L0_001" if mirrored[0]["footprint"]["center"][1] < 1.85 else "w_L0_003"
    y = 0.0 if wall == "w_L0_001" else 3.7
    source["openings"].append({"id": "d_L0_009", "type": "door", "level_id": "L0", "wall_id": wall, "center": [x, y],
                               "width": 0.8, "swing_side": TWIN_B, "status": "verified",
                               "evidence": [B.evidence("p.dxf", "vector", 1.0)]})
    out, records = C.complete_building(source, "x", FakeChooser(), C.Settings())
    rec = {r.room_id: r for r in records}
    assert rec[TWIN_B].state == "completed" and "copied pieces fail a check here" in rec[TWIN_B].reason
    assert not [f for f in added_in(out, TWIN_B) if f.get("mirrored_from")]
    assert LK.check(source, out, "complete") == []


def test_empty_twin_rooms_copy_the_layout():
    source = twin_building(furnished=False)
    client = FakeChooser()
    settings = C.Settings()
    partners = {r["id"]: p for r in source["rooms"] for p in [C.partner_of(r, settings)] if p}
    out, layouts = L.furnish_building(source, "x", client, partners=partners)
    assert client.calls == [TWIN_A]
    by_room = {l.room_id: l for l in layouts}
    assert by_room[TWIN_B].copied_from["room"] == TWIN_A and by_room[TWIN_B].candidates == []
    b = sorted(added_in(out, TWIN_B), key=lambda f: f["id"])
    a = sorted(added_in(out, TWIN_A), key=lambda f: f["id"])
    assert [f["type"] for f in b] == [f["type"] for f in a] and "bed_double" in {f["type"] for f in a}
    for fa, fb in zip(a, b):
        assert fb["footprint"]["center"] == pytest.approx([8.2 - fa["footprint"]["center"][0],
                                                           fa["footprint"]["center"][1]], abs=1e-3)
        assert fb["mirrored_from"] == fa["id"] and all(fb["checks"].values())
        anchor = fb["group"]["anchor_id"]
        assert anchor is None or any(f["id"] == anchor for f in b)          # anchors mapped onto the copies
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
    out, records = C.complete_building(b, "x", FakeChooser(), C.Settings(mode=mode))
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
    client = FakeChooser()
    rc = L.main([str(src), "--out", str(out), "--debug", str(tmp_path / "dbg"), "--project-dir", str(project),
                 "--server", "http://127.0.0.1:1/v1"], client_factory=lambda: client)
    assert rc == 0
    final = B.load(out)
    assert added_in(final, "r_L1_oyun_odasi")                              # an empty room, furnished by the solver
    completion = json.loads((out.parent / "completion.json").read_text())
    assert completion["locked_violations"] == [] and completion["changes_applied"] == 0
    assert completion["settings"]["furnished_rooms"] == "complete" and completion["model"] == MODEL
    assert LK.mode_of(completion) == "complete" and LK.keep_rooms_of(completion) == []   # what refit passes on
    assert LK.check(source, final, LK.mode_of(completion), LK.keep_rooms_of(completion)) == []
    layout = json.loads((out.parent / "layout.json").read_text())
    assert layout["completion"]["pieces_added"] == completion["pieces_added"] > 0
    assert (out.parent / "completion_report.md").read_text().startswith("# AI completion of furnished rooms")
    assert (tmp_path / "dbg" / f"{SALON}.png").exists() and (tmp_path / "dbg" / "r_L1_oyun_odasi.png").exists()
    assert (tmp_path / "dbg" / f"{SALON}_c1.png").exists()                 # the images the model saw


def test_cli_keep_brief_changes_nothing_drawn(tmp_path):
    source = drawn_building(example())
    src, project = _write(tmp_path, source, "furnished_rooms: keep\n")
    out = tmp_path / "out.json"
    client = FakeChooser()
    assert L.main([str(src), "--out", str(out), "--project-dir", str(project)], client_factory=lambda: client) == 0
    final = B.load(out)
    assert all(r not in client.calls for r in (SALON, BEDROOM)) and LK.check(source, final, "keep") == []
    completion = json.loads((tmp_path / "completion.json").read_text())
    assert completion["rooms_completed"] == 0 and LK.mode_of(completion) == "keep"
    assert set(LK.keep_rooms_of(completion)) == {r["id"] for r in source["rooms"] if r["has_documented_furniture"]}


def test_cli_takes_the_solvers_best_when_the_vision_model_is_down(tmp_path, capsys):
    """Milestone 12: a dead server no longer stops the stage (exit 3 before); every room takes candidate 1."""
    source = drawn_building(example())
    src, project = _write(tmp_path, source)
    out = tmp_path / "out" / "building_furnished.json"

    class Down(FakeChooser):
        def choose(self, prompt, images, labels, schema):
            self.calls.append(room_of(images))
            if self.down:
                return L.Proposal(1, None, error=f"not asked: {self.down}", prompt=prompt, transport_error=True)
            self.down = "cannot reach http://127.0.0.1:1/v1"
            return L.Proposal(1, None, error=self.down, prompt=prompt, model=MODEL, transport_error=True)

    client = Down()
    rc = L.main([str(src), "--out", str(out), "--project-dir", str(project)], client_factory=lambda: client)
    assert rc == 0 and out.exists()
    assert "the vision model could not be reached" in capsys.readouterr().err
    completion = json.loads((out.parent / "completion.json").read_text())
    assert all(r["chosen"] in (None, 1) for r in completion["rooms"])


def test_cli_exits_1_on_a_locked_violation(tmp_path, monkeypatch, capsys):
    src, project = _write(tmp_path, drawn_building(example()))
    out = tmp_path / "out" / "building_furnished.json"
    real = C.complete_building

    def moving(building, *args, **kwargs):           # a bug that moves a drawn piece 10 cm
        done, records = real(building, *args, **kwargs)
        piece(done, "f_L0_002")["footprint"]["center"][0] += 0.1
        return done, records

    monkeypatch.setattr(C, "complete_building", moving)
    rc = L.main([str(src), "--out", str(out), "--project-dir", str(project)], client_factory=lambda: FakeChooser())
    assert rc == 1 and not out.exists()
    completion = json.loads((out.parent / "completion.json").read_text())
    assert completion["locked_violations"] and "f_L0_002" in completion["locked_violations"][0]
    assert "locked violation" in capsys.readouterr().err
    assert "## Locked check: 2 violation(s)" in (out.parent / "completion_report.md").read_text()


def test_a_companion_turns_to_face_its_host():
    """M11 diagnosis (real02 r_L-1_salon): a chair beside a table turns to its nearest host when the turn keeps its
    footprint (square: 90 deg steps; else 180)."""
    table = P.Piece("table_dining", (6.0375, 4.2269), 90.0, (3.35, 1.566), False)      # x 5.25-6.82, y 2.55-5.90
    long_chair = P.Piece("chair", (6.0, 1.9), 0.0, (0.4, 0.6), False)                   # front 270, table above it
    assert P.face_host(long_chair, [table])["after"]["rotation_deg"] == pytest.approx(180.0)
    copy.deepcopy(table)
