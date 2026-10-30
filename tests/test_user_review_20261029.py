"""The user's review of real06 run 20261028-154514-full (29 Oct 2026): the TV (UL99), fuller rooms (UL98, UL107),
books (UL103), bathroom storage (UL102), the lights of one room (UL91) and the rejected floor lamp (UL94); the model
review's M21 and Argus U19 (CPU only).

The real06 fixture (``tests/fixtures/real06_rooms_20261029.json``) is the run's building as built, trimmed to the
living room, the three first-floor bedrooms and two bathrooms."""
from __future__ import annotations

import copy
import json
import math
from pathlib import Path

import pytest

from wenart.agent import causes as CS
from wenart.audit import kinds as K
from wenart.audit import lessons as LS
from wenart.blender import furniture as BF
from wenart.blender import model_review as MR
from wenart.blender import parametric as P
from wenart.furniture import catalog as C
from wenart.furniture import ceiling_lights as CL
from wenart.furniture import decor as D
from wenart.furniture import fit as F
from wenart.furniture import media_wall as MW
from wenart.furniture import placer
from wenart.furniture import program as PR
from wenart.furniture import room_fill as RF
from wenart.furniture import room_use as RU
from wenart.furniture import sizes as SZ
from wenart.furniture import solver as SV
from wenart.furniture import tabletop as TT

from test_decor_m8 import RID, room_building

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "real06_rooms_20261029.json"
REAL04 = ROOT / "results" / "furniture" / "real04"


@pytest.fixture(scope="module")
def real06() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def _room(b: dict, rid: str) -> dict:
    return next(r for r in b["rooms"] if r["id"] == rid)


def _new_ids(prefix: str = "dec"):
    counter = iter(range(900, 9999))
    return lambda lv: f"{prefix}_{lv}_{next(counter)}"


# --------------------------------------------------------------------------
# UL91: two lights together (the ceiling lights of one room)
# --------------------------------------------------------------------------

def test_real06_child_room_pendant_and_flush_lights_are_found_too_close(real06):
    got, _n = CL.review(real06)
    pairs = [f for f in got if f["room_id"] == "r_L1_cocuk_odasi" and f["metrics"].get("rule") == "spacing"]
    assert {f["target"] for f in pairs} >= {"dec_L1_047", "dec_L1_048"}          # 2.04 / 2.07 m from the pendant
    assert all(f["severity"] == "major" and f["metrics"]["ids"][0] == "dec_L1_015" for f in pairs)
    assert all(f["metrics"]["lesson"] == "UL91" and "two lights together" in f["message"] for f in pairs)


def test_the_lighting_rule_spaces_the_lights_of_a_room(real06):
    b = copy.deepcopy(real06)
    b["decor"] = [d for d in b["decor"] if not (d.get("type") in CL.LIGHT_TYPES and d.get("rule") == CL.RULE)]
    made, _notes = CL.add_lights(b, _new_ids())
    for room in b["rooms"]:
        lights = CL.room_lights(b, room["id"])
        for i, a in enumerate(lights):
            for c in lights[i + 1:]:
                dist = math.dist(a["center"][:2], c["center"][:2])
                assert dist >= CL.LIGHT_SPACING_M - 1e-6, (a["id"], c["id"], dist)
                kinds = {a["type"], c["type"]}
                if kinds == {"pendant_light", "ceiling_light"}:
                    pend = a if a["type"] == "pendant_light" else c
                    if not CL.task_pendant(pend, [f for f in b["furniture"] if f["room_id"] == room["id"]]):
                        assert dist >= CL.MIXED_SPACING_M - 1e-6, (a["id"], c["id"], dist)
    # the child's room keeps the AI's pendant as its light: no flush light beside it
    child = CL.room_lights(b, "r_L1_cocuk_odasi")
    assert [d["id"] for d in child if d["type"] == "pendant_light"] == ["dec_L1_015"]
    assert all(math.dist(d["center"][:2], child[0]["center"][:2]) >= CL.MIXED_SPACING_M - 1e-6 for d in child[1:])
    assert not [f for f in CL.review(b)[0] if f["metrics"].get("rule") == "spacing"]


def test_one_light_per_zone_and_the_spacing_rules():
    # a bedroom: a pendant at the room's centre lights the bed 0.8 m off its edge (the bed's zone reach)
    b = room_building(4.0, 5.0, "bedroom", furniture=[("bed_double", (2.0, 4.0), 0.0, (1.6, 2.0))])
    b["decor"] = [{"id": "dec_L0_001", "kind": "decor", "type": "pendant_light", "level_id": "L0", "room_id": RID,
                   "center": [2.0, 2.2, 2.0], "size": [0.45, 0.45, 0.7], "rotation_deg": 0.0, "method": "ai"}]
    rec = CL.plan_room(b, b["rooms"][0], b["furniture"], CL.room_lights(b, RID))
    assert not [a for a in rec["add"] if a.get("anchor_ids") == ["f_L0_001"]]       # no second light over the bed
    assert all(math.dist(a["center"][:2], (2.0, 2.2)) >= CL.MIXED_SPACING_M - 1e-6 for a in rec["add"])
    # two lights 1.0 m apart: the rule's own light goes, the AI's stays
    b["decor"].append({"id": "dec_L0_002", "kind": "decor", "type": "ceiling_light", "level_id": "L0", "room_id": RID,
                       "center": [3.0, 2.2, 2.58], "size": [0.4, 0.4, 0.12], "rotation_deg": 0.0,
                       "rule": CL.RULE})
    rec = CL.plan_room(b, b["rooms"][0], b["furniture"], CL.room_lights(b, RID))
    assert rec["remove"] == ["dec_L0_002"] and rec["too_close"][0]["ids"] == ["dec_L0_001", "dec_L0_002"]
    assert CL.clash((0, 0), "ceiling_light", False, (1.0, 0), "ceiling_light", False)
    assert CL.clash((0, 0), "ceiling_light", False, (2.0, 0), "pendant_light", True)
    assert not CL.clash((0, 0), "ceiling_light", False, (2.0, 0), "pendant_light", False)   # a task pendant
    assert not CL.clash((0, 0), "ceiling_light", False, (2.0, 0), "pendant_light", True, task_p=True)  # a run light


@pytest.mark.skipif(not (REAL04 / "building_decor.json").is_file(), reason="no committed real04 decor")
def test_real04_lights_keep_their_spacing_after_the_rule():
    b = json.loads((REAL04 / "building_decor.json").read_text(encoding="utf-8"))
    CL.add_lights(b, _new_ids())
    assert not [f for f in CL.review(b)[0] if f["metrics"].get("rule") == "spacing"]


# --------------------------------------------------------------------------
# UL94: the rejected floor lamp
# --------------------------------------------------------------------------

def test_a_model_the_user_rejected_is_never_used_again():
    rec = C.user_rejection({"id": "abo_B07JNRNTYJ"})
    assert rec and rec["lesson"] == "UL94" and rec["user"] == "I did not like this light" and rec["date"]
    entry = C.load().entry("abo_B07JNRNTYJ")
    for mode in C.LICENCE_MODES:
        assert not C.usable(entry, mode)
        assert "the user rejected this model" in C.unusable_reason(entry, mode)
    assert not C.usable({"asset_id": "abo_B07JNRNTYJ", "licence": "CC-BY-4.0", "licence_flag": "none"}, "relaxed")
    assert C.usable({"asset_id": "abo_B07B4ZK8BR", "licence": "CC-BY-4.0", "licence_flag": "none"}, "relaxed")
    rows = json.loads(C.USER_REJECTED_PATH.read_text(encoding="utf-8"))["rejected"]
    assert all({"id", "type", "date", "lesson", "user", "where"} <= set(r) for r in rows)


def test_a_drawn_floor_lamp_is_fitted_at_a_real_product_size(real06):
    snap = SZ.symbol_snap("floor_lamp", (0.58, 0.58))
    assert snap["changed"] and snap["footprint"] == (0.4, 0.4)
    assert not SZ.symbol_snap("floor_lamp", (0.40, 0.40))["changed"] and not SZ.symbol_snap("sofa", (3, 1))["changed"]
    lamp = copy.deepcopy(next(f for f in real06["furniture"] if f["id"] == "f_L1_020"))
    for k in ("size_snap", "adjusted_by_ai", "drawn_footprint", "drawn_type", "drawn_front_deg", "drawn_height"):
        lamp.pop(k, None)
    centre = list(lamp["footprint"]["center"])
    rec = F.apply_size_snap(lamp)
    assert rec["symbol"] and lamp["footprint"]["size"] == [0.4, 0.4] and lamp["footprint"]["center"] == centre
    assert lamp["drawn_footprint"]["size"] == [0.5801, 0.5801] and lamp["adjusted_by_ai"]["rule"] == F.SNAP_RULE
    assert "UL94" in lamp["adjusted_by_ai"]["reason"]
    asset = F.fit_piece(lamp, C.load(), style_family="scandinavian", mode="relaxed")
    assert asset["asset_id"] != "abo_B07JNRNTYJ" and max(asset["bbox_m"][:2]) <= SZ.SYMBOL_MAX_M["floor_lamp"] + 0.05
    # M21 finds the run's lamp: the rejected model and its symbol size
    found = {f["metrics"]["rule"] for f in RU.review(real06)[0] if f["target"] == "f_L1_020"}
    assert found == {"user_rejected", "symbol_size"}


# --------------------------------------------------------------------------
# UL99: the TV
# --------------------------------------------------------------------------

def test_a_living_room_gets_a_tv_unit_on_the_wall_its_sofa_faces():
    # sofa on the north wall facing south, a coffee table, a window on the south wall off the sofa's axis
    b = room_building(6.0, 5.0, "living", furniture=[("sofa", (3.0, 4.53), 0.0, (2.2, 0.9)),
                                                      ("table_coffee", (3.0, 3.38), 0.0, (1.2, 0.6))],
                      windows=[("win1", "s", 1.0, 1.2)], doors=[("d1", "e", 4.0, 0.9, True)])
    rooms = MW.media_rooms(b)
    assert [(r["id"], k) for r, k in rooms] == [(RID, "living")]
    rec = MW.plan_room(b, b["rooms"][0], "living")
    unit = rec["unit"]
    assert unit and unit["type"] == "tv_unit" and unit["source"] == "added_by_ai" and unit["rule"]["name"] == MW.RULE
    assert unit["group"]["group"] == "seating" and unit["group"]["anchor_id"] == "f_L0_001"
    view = rec["view"]
    assert MW.VIEW_MIN_M <= view["distance_m"] <= MW.VIEW_MAX_M and view["angle_deg"] <= MW.VIEW_ANGLE_MAX_DEG
    poly = placer.piece_from_furniture(unit).polygon()
    assert poly.bounds[1] < 0.6                                           # its back on the south wall
    assert poly.bounds[0] > 1.0 + 0.6 + MW.OPENING_MARGIN_M - 1e-6        # never in front of the window
    assert SV.verify(b, RID, [unit])[0] == []
    # the TV on it: its size by the viewing distance, its box on the unit, nothing before its screen
    b["furniture"].append(unit)
    tvs = MW.tv_items(b["rooms"][0], b["furniture"], b, [], _new_ids())
    assert len(tvs) == 1
    tv = tvs[0]
    assert tv["type"] == "tv" and tv["host_id"] == unit["id"] and tv["source"] == "added_by_ai"
    assert tv["tv"]["inches"] == MW.inches_for(view["distance_m"], unit["footprint"]["size"][0] - 0.06)
    assert tv["size"][0] <= unit["footprint"]["size"][0] and tv["rotation_deg"] == unit["footprint"]["rotation_deg"]
    made = TT.dress_tops(b["rooms"][0], b["furniture"], b, [], _new_ids())
    on_unit = [m for m in made if m.get("host_id") == unit["id"]]
    assert [m["type"] for m in on_unit].count("tv") == 1
    tv_box = TT.local_box(unit, next(m for m in on_unit if m["type"] == "tv"))
    for m in on_unit:
        if m["type"] != "tv":
            assert TT.boxes_clear(TT.local_box(unit, m), tv_box)           # beside the TV, never before its screen
    got, n = MW.review(dict(b, decor=made))
    assert n == 1 and got == []
    assert MW.review(b)[0][0]["severity"] == "minor"                       # a TV unit without its TV


def test_tv_sizes_and_the_parametric_tv():
    assert MW.inches_for(2.6, 1.8) == 65 and MW.inches_for(2.0, 1.8) == 55 and MW.inches_for(1.8, 1.8) == 50
    assert MW.inches_for(2.6, 1.8, "bedroom") == 55 and MW.inches_for(2.6, 1.0) == 43
    assert MW.inches_for(2.6, 0.8) is None
    w, d, h = MW.tv_box(55)
    assert 1.22 <= w <= 1.26 and 0.76 <= h <= 0.80
    assert "tv" in P.DECOR_TYPES and "tv" in P.LARGE_DECOR_TYPES and "tv" in P.SURFACE_DECOR_TYPES
    assert "tv" not in P.KITCHEN_DECOR_TYPES and "tv" in D.DECOR_TYPES and "screen" in P.MATERIAL_KEYS
    parts = P.decor_parts("tv", w, 0.39, h, {"tv": {"stand_depth_m": d}})
    xs = [v[0] for p in parts for v in p["verts"]]
    ys = [v[1] for p in parts for v in p["verts"]]
    zs = [v[2] for p in parts for v in p["verts"]]
    assert min(xs) >= -w / 2 - 1e-6 and max(xs) <= w / 2 + 1e-6 and min(zs) == 0.0 and max(zs) <= h + 1e-6
    assert max(ys) <= 0.39 / 2 + 1e-6 and min(ys) >= -0.39 / 2 - 1e-6
    assert {p["key"] for p in parts} <= set(P.MATERIAL_KEYS) and "screen" in {p["key"] for p in parts}
    screen = next(p for p in parts if p["key"] == "screen")
    panel = next(p for p in parts if p["role"] == "panel")
    assert min(v[1] for v in screen["verts"]) < min(v[1] for v in panel["verts"])    # the screen on the panel's front
    assert min(v[2] for v in screen["verts"]) > min(v[2] for v in panel["verts"])    # inside its bezel
    keys, _assumed = BF.style_material_keys({"floor": {"material": "wood_oak_light"}})
    from wenart.style import vocabulary as V
    assert keys["screen"][0] == "screen_black" and V.ROUGHNESS["screen_black"] < 0.15
    from wenart import building as B
    assert "tv" in B.load_schema()["$defs"]["decor"]["properties"]["type"]["enum"]


def test_real06_salon_gets_a_free_media_console_and_the_master_bedroom_is_reported(real06):
    rooms = dict((r["id"], k) for r, k in MW.media_rooms(real06))
    assert rooms == {"r_L0_salon": "living", "r_L1_ebeveyn_y_odasi": "bedroom"}     # never the child's room
    assert MW.master_named(_room(real06, "r_L1_ebeveyn_y_odasi"))
    rec = MW.plan_room(real06, _room(real06, "r_L0_salon"), "living")
    unit = rec["unit"]
    assert unit is not None and rec["seat_id"] == "f_L0_014" and unit["rule"]["free"]
    assert rec["view"]["angle_deg"] < 1.0 and abs(rec["view"]["distance_m"] - MW.VIEW_BEST_M) < 0.45
    assert SV.verify(real06, "r_L0_salon", [unit])[0] == []
    assert "f_L0_006" in rec["why"]                                       # why the main sofa got none
    bed = MW.plan_room(real06, _room(real06, "r_L1_ebeveyn_y_odasi"), "bedroom")
    assert bed["unit"] is None and "windows" in bed["why"]               # two windows face the bed: no TV there
    sev = {f["room_id"]: f["severity"] for f in MW.review(real06)[0]}
    assert sev == {"r_L0_salon": "major", "r_L1_ebeveyn_y_odasi": "minor"}
    off = copy.deepcopy(real06)
    off["project"]["brief"] = {"media_wall": False}
    assert MW.media_rooms(off) == [] and MW.review(off) == ([], 0)


@pytest.mark.skipif(not (REAL04 / "building_final.json").is_file(), reason="no committed real04 building")
def test_real04_living_rooms_get_their_tv_units():
    b = json.loads((REAL04 / "building_final.json").read_text(encoding="utf-8"))
    out, recs = MW.add_media_walls(copy.deepcopy(b))
    units = [r["unit"] for r in recs if r["unit"]]
    assert len(units) >= 2
    for u in units:
        assert SV.verify(b, u["room_id"], [u])[0] == []
    assert not any(r["kind"] == "bedroom" and r["room_id"].endswith("cocuk") for r in recs)


# --------------------------------------------------------------------------
# UL98 / UL107 / UL103 / UL102: fuller rooms
# --------------------------------------------------------------------------

def test_density_keeps_the_reading_corner_of_an_under_furnished_living_room(real06):
    salon = _room(real06, "r_L0_salon")
    under, share, target = RF.under_density(real06, salon)
    assert under and 0.15 < share < target == RF.DENSITY_TARGET["living"]
    prog = PR.room_program(real06, "r_L0_salon")
    rows = [g for g in prog["groups"] if g["group"] == "reading_corner"]
    assert rows and not rows[0]["required"] and "density" in rows[0]["note"]
    # a furnished room at its density, or one too small for the rule, keeps the old rule: only completed
    furniture = [("sofa", (2.5, 3.53), 0.0, (2.2, 0.9)), ("table_coffee", (2.5, 2.4), 0.0, (1.2, 0.6)),
                 ("armchair", (0.6, 2.4), 90.0, (0.8, 0.8)), ("armchair", (4.4, 2.4), 270.0, (0.8, 0.8)),
                 ("tv_unit", (2.5, 0.25), 180.0, (1.8, 0.45)), ("bookshelf", (0.5, 0.2), 180.0, (1.0, 0.35)),
                 ("sideboard", (4.2, 0.25), 180.0, (1.4, 0.45))]
    dense = room_building(5.0, 4.0, "living", furniture=furniture)
    assert RF.furniture_share(dense, dense["rooms"][0]) >= RF.DENSITY_TARGET["living"]
    small = room_building(4.0, 3.5, "living", furniture=furniture[:2])
    for b in (dense, small):
        assert not RF.under_density(b, b["rooms"][0])[0]
        assert not [g for g in PR.room_program(b, RID)["groups"] if g["group"] == "reading_corner"]


def test_the_room_fill_adds_a_sideboard_a_bookshelf_and_bathroom_storage():
    # a 7 x 5 living room with a sofa, a coffee table and a dining table: under its density
    b = room_building(7.0, 5.0, "living", furniture=[("sofa", (2.0, 4.53), 0.0, (2.2, 0.9)),
                                                      ("table_coffee", (2.0, 3.38), 0.0, (1.0, 0.6)),
                                                      ("table_dining", (5.5, 2.5), 0.0, (1.2, 0.8))],
                      doors=[("d1", "s", 1.0, 0.9, True)])
    assert RF.under_density(b, b["rooms"][0])[0]
    out, recs = RF.fill_building(copy.deepcopy(b))
    added = {r["what"]: r["piece"] for r in recs if r["piece"]}
    assert set(added) == {"sideboard", "bookshelf"}
    side = added["sideboard"]
    table = next(f for f in out["furniture"] if f["type"] == "table_dining")
    assert placer.piece_from_furniture(side).polygon().distance(placer.piece_from_furniture(table).polygon()) \
        <= RF.SIDEBOARD_NEAR_M + 1e-6
    for p in added.values():
        assert p["source"] == "added_by_ai" and p["method"] == "rule" and p["rule"]["name"].startswith("room_fill.")
        assert SV.verify(b, RID, [p])[0] == []
    assert "UL107" in side["reason"] and "UL103" in added["bookshelf"]["reason"]
    # a bathroom: a storage column off the fixtures' use zones, the door swing and the window
    bath = room_building(2.4, 2.2, "bathroom", furniture=[("toilet", (0.5, 1.85), 0.0, (0.4, 0.7)),
                                                          ("washbasin", (1.5, 1.98), 0.0, (0.5, 0.4)),
                                                          ("shower", (1.95, 0.45), 90.0, (0.9, 0.9))],
                         doors=[("d1", "s", 0.6, 0.8, True)], windows=[("w1", "n", 2.0, 0.6)])
    out, recs = RF.fill_building(copy.deepcopy(bath))
    col = next(r["piece"] for r in recs if r["what"] == "bath_column")
    assert col and col["type"] == "tall_cabinet" and SV.verify(bath, RID, [col])[0] == [] and "UL102" in col["reason"]
    assert RF.review(out)[0] == [] or all(f["metrics"]["rule"] != "room_fill.bath_column" for f in RF.review(out)[0])
    off = copy.deepcopy(bath)
    off["project"]["brief"] = {"room_fill": False}
    assert RF.fill_building(off)[1] == []


def test_real06_bathrooms_and_the_child_room_get_their_storage(real06):
    out, recs = RF.fill_building(copy.deepcopy(real06))
    by = {(r["room_id"], r["what"]): r for r in recs}
    for rid in ("r_L1_dus", "r_L1_banyo"):
        piece = by[(rid, "bath_column")]["piece"]
        assert piece is not None and SV.verify(real06, rid, [piece])[0] == []
    shelf = by[("r_L1_cocuk_odasi", "low_shelf")]["piece"]
    assert shelf is not None and shelf["height"] == RF.LOW_SHELF["height"]
    kinds = {f["metrics"]["rule"] for f in RF.review(out)[0]}
    assert "room_fill.bath_column" not in kinds


def test_every_bookshelf_carries_books_on_its_boards():
    b = room_building(5.0, 4.0, "living", furniture=[("bookshelf", (2.5, 3.8), 0.0, (1.0, 0.35))])
    host = b["furniture"][0]
    assert TT.shelf_boards(host) == 4 and TT.shelf_boards(dict(host, height=0.9)) == 1
    made = TT.dress_tops(b["rooms"][0], b["furniture"], b, [], _new_ids())
    books = [m for m in made if m["type"] == "book_set" and m["host_frame"]["support"] == "shelf"]
    assert len({m["host_frame"]["shelf"] for m in books}) == 4 and len(books) >= 6
    boxes = {}
    for m in made:
        frame = m.get("host_frame") or {}
        boxes.setdefault(frame.get("shelf"), []).append(TT.local_box(host, m))
    for board, bs in boxes.items():
        for i, a in enumerate(bs):
            for c in bs[i + 1:]:
                assert TT.boxes_clear(a, c, 0.0), board                   # nothing on a board overlaps
    assert all("UL103" in m["reason"] for m in books)
    assert TT.shelf_books(dict(b["rooms"][0], room_type="bathroom"), host, [], {}) == []


# --------------------------------------------------------------------------
# M21 / U19 and their registrations
# --------------------------------------------------------------------------

def test_m21_and_u19_find_what_the_user_pointed_at(real06):
    got, n = RU.review(real06)
    lessons = {f["metrics"]["lesson"] for f in got}
    assert {"UL99", "UL98", "UL102", "UL94"} <= lessons and n > 0
    assert all(f["check"] == "M21" for f in got)
    rec = MR.review(real06)
    assert "M21" in MR.CHECKS and rec["checks"]["M21"]["failed"] == len(got)
    assert K.kind_of({"check": "M21"}) == "taste" and K.kind_of({"check": "U19", "line": "lessons"}) == "taste"
    assert CS.CHECK_CAUSE["M21"] == "room_use" and CS.REPORT_TO["room_use"] == "layout"
    assert "room_use" in CS.NO_TOOL_REASON and CS.CAUSE_TOOLS["room_use"] == ()
    u19 = LS.rooms_for_use(real06)
    assert u19 and all(f["check"] == "U19" and f["evidence"]["lesson"] in ("UL91", "UL94", "UL98", "UL99", "UL102",
                                                                           "UL103", "UL107", "UL180") for f in u19)
    assert ("U19", LS.rooms_for_use) in LS.BUILDING_CHECKS and LS.CHECK_LESSONS["U19"] == ("UL94", "UL98", "UL99", "UL102", "UL103", "UL107", "UL180")
    res = LS.audit(real06)
    assert res["checked"]["U19"] == len(u19)
