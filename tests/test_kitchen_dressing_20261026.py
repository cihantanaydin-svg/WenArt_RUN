"""Kitchen runs take their missing hob and fridge into themselves, every counter run gets its wall cabinets, a dressing
room gets wardrobe runs (fix round of 26 Oct 2026, user: "fix should be general"; real06 is the test case).

real06 (pod run 20261026-183115): the AI judge scored the kitchen views 2/5 ("no hob, no oven, no cooktop, and no
upper cabinets above the worktop"), G9 said "no fridge", the agent's complete_group was refused 30+ times ("no place
passes the checks"); the 5.9 m² "Soyunma Odası" rendered as a bare shell ("no groups for this room").
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import _m11_room as M
from wenart.blender import modules as MOD
from wenart.furniture import complete as C
from wenart.furniture import fit as F
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import layout as L
from wenart.furniture import placer as P
from wenart.furniture import program as PR
from wenart.furniture import solver as SV

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "real06_kitchen_dressing_20261026.json"
ROOM = M.ROOM_ID


def fp(pid, ftype, center, size, front, **kw):
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def kitchen(w=4.0, h=3.0, counter_w=3.0, sink_x=0.9, window=None, door_x=3.4, extra=()) -> dict:
    """A kitchen with a drawn counter run on its north wall and a drawn sink in it: no hob, no fridge."""
    counter = fp("k1", "kitchen_counter", (counter_w / 2.0, h - 0.32), (counter_w, 0.6), 270.0)
    sink = fp("sk", "sink_kitchen", (sink_x, h - 0.32), (0.8, 0.6), 270.0)
    return M.building(w=w, h=h, room_type="kitchen", window=window, door_x=door_x,
                      furniture=[counter, sink] + list(extra))


def x_extent(piece: dict) -> tuple[float, float]:
    xs = [x for x, _y in P.drawn_piece(piece).polygon().exterior.coords]
    return min(xs), max(xs)


def by_id(b: dict) -> dict:
    return {f["id"]: f for f in b["furniture"]}


# --------------------------------------------------------------------------
# 1. The hob built into the run (no floor place)
# --------------------------------------------------------------------------

def test_a_drawn_run_without_its_hob_gets_one_built_into_its_counter():
    b = kitchen()
    prog = PR.room_program(b, ROOM)
    run = next(g for g in prog["groups"] if g["group"] == "kitchen_run")
    assert run["drawn"] and {"stove", "fridge"} <= set(run["missing"])
    best = SV.solve_room(b, ROOM, prog, k=1)[0]
    assert not best["hard_failures"]
    hob = next(p for p in best["pieces"] if p["type"] == "stove")
    assert hob["built_into"] == "k1" and hob["built_in"]["kind"] == "hob" and hob["built_in"]["oven"] is True
    assert hob["source"] == "added_by_ai" and hob["completes_room"] and hob["method"] == "rule"
    assert hob["group"]["group"] == "kitchen_run" and "misses its cooking piece" in hob["built_in"]["reason"]
    assert hob["footprint"]["size"] == [0.6, 0.6] and hob["front_deg"] == 270.0      # the counter's depth and front
    counter = by_id(b)["k1"]
    assert P.drawn_piece(counter).polygon().buffer(1e-6).contains(P.drawn_piece(hob).polygon())
    landing = GR.rule_min("hob_landing")
    x0, x1 = x_extent(hob)
    assert x0 >= 0.0 + landing - 1e-6 and x1 <= 3.0 - landing + 1e-6            # off both ends of the run
    s0, s1 = x_extent(by_id(b)["sk"])
    assert x0 >= s1 + landing - 1e-6 or x1 <= s0 - landing + 1e-6                 # off the sink, never over it
    rec = next(r for r in best["built_ins"] if r["kind"] == "hob")
    assert rec["placed"] and rec["host"] == "k1" and rec["id"] == hob["id"]
    after = SV.apply_candidate(b, ROOM, best)
    g9 = [v["message"] for v in GC.check_room(after, ROOM) if v["check"] == "G9"]
    assert not [m for m in g9 if "hob" in m]
    # the fridge: a floor place beside the run or, where none passes, one built into the counter; logged either way
    fridge = next(p for p in best["pieces"] if p["type"] == "fridge")
    frec = next(r for r in best["built_ins"] if r["kind"] == "fridge")
    assert frec["placed"] and frec["how"] in ("floor", "built_in") and frec["id"] == fridge["id"]
    assert not [m for m in g9 if "fridge" in m]


def test_the_hob_never_stands_under_a_window():
    b = kitchen(window=(2.5, 0.6))                         # the band covers x 2.2-2.8 over the counter
    best = SV.solve_room(b, ROOM, k=1)[0]
    hob = next(p for p in best["pieces"] if p["type"] == "stove")
    ctx = P.room_context(b, b["rooms"][0])
    poly = P.drawn_piece(hob).polygon()
    assert all(poly.intersection(w.band).area <= SV.BUILT_IN_WINDOW_M2 for w in ctx.windows)
    assert hob["built_into"] == "k1" and not best["hard_failures"]


def test_no_stretch_for_a_hob_is_logged_with_the_reason():
    b = kitchen(counter_w=1.2, sink_x=0.6)                 # a 1.20 m counter holding a 0.80 m sink: no stretch left
    piece, rec = SV.built_in_kitchen(b, b["rooms"][0], None, "hob", "f_L0_900")
    assert piece is None and rec["placed"] is False and "no place on the counters" in rec["reason"]
    best = SV.solve_room(b, ROOM, k=1)[0]
    assert not any(p["type"] == "stove" for p in best["pieces"])
    assert any(r["kind"] == "hob" and not r["placed"] for r in best["built_ins"])


def test_an_under_counter_fridge_is_built_in_where_no_floor_place_is_asked():
    b = kitchen()
    piece, rec = SV.built_in_kitchen(b, b["rooms"][0], None, "fridge", "f_L0_900", why="no floor place")
    assert piece is not None and rec["placed"] and piece["built_into"] == "k1" and piece["type"] == "fridge"
    assert piece["height"] <= 0.9 and piece["built_in"]["kind"] == "fridge"
    assert rec["reason"].startswith("no floor place: a 0.60 m under-counter fridge built into the drawn counter k1")
    s0, s1 = x_extent(by_id(b)["sk"])
    x0, x1 = x_extent(piece)
    assert x0 >= s1 - 1e-6 or x1 <= s0 + 1e-6                                     # never under the sink
    assert max(x0 - 0.0, 3.0 - x1) >= GR.rule_min("fridge_landing") - 1e-6       # counter beside it (its landing)


def test_the_built_in_specs_and_the_drawn_run_tier_come_from_groups_yaml():
    hob, fridge = SV.built_in_spec("hob"), SV.built_in_spec("fridge")
    assert hob["type"] == "stove" and hob["sizes"][0] == [0.6, 0.6] and hob["landing"] == "hob_landing"
    assert fridge["type"] == "fridge" and fridge["landing"] == "fridge_landing"
    # a drawn run in any kitchen: the work triangle is scored, never a refusal; the fridge landing only under 14 m²
    rule = GR.rule_for("triangle_leg", room_type="kitchen", area=24.8, drawn_run=True)
    assert rule["hard"] is False and rule["tier"] == "drawn_run_any"
    assert GR.rule_for("triangle_leg", room_type="kitchen", area=24.8)["hard"] is True
    assert GR.rule_for("fridge_landing", room_type="kitchen", area=24.8, drawn_run=True)["hard"] is True
    assert GR.rule_for("fridge_landing", room_type="kitchen", area=13.6, drawn_run=True)["tier"] == "drawn_run"


def test_a_new_work_triangle_finding_is_not_taken_for_an_old_landing_finding():
    old = {"check": "G8", "target": "sk", "room_id": "r", "message": "sink sk: 0.00 m of counter beside it",
           "metrics": {"landing_m": 0.0, "needs_m": 0.46}}
    new = {"check": "G8", "target": "sk", "room_id": "r", "message": "work triangle: fridge-sink 1.04 m",
           "metrics": {"legs_m": {"fridge-sink": 1.04}, "sum_m": 4.0}}
    assert SV._violation_key(old) != SV._violation_key(new)


def test_the_aisle_of_a_run_ignores_a_counter_outline_drawn_over_it():
    nested = fp("k2", "kitchen_counter", (1.5, 3.0 - 0.30), (0.9, 0.48), 270.0)   # real06's f_L0_002 in f_L0_031
    b = kitchen(extra=[nested])
    aisle = [v for v in GC.check_room(b, ROOM) if v["check"] == "G8" and "aisle" in v["message"]]
    assert not aisle


def test_a_twin_takes_the_built_in_hob_into_its_own_counter():
    b = kitchen()
    hob, _rec = SV.built_in_kitchen(b, b["rooms"][0], None, "hob", "f_L0_900")
    out = copy.deepcopy(b)
    ctx = P.room_context(b, b["rooms"][0])
    added, dropped = C.copy_added(out["rooms"][0], ROOM, [hob], C.Transform("identity"), [], out, ctx,
                                  ids={"k1": "k1", "sk": "sk"})
    assert dropped == [] and len(added) == 1 and added[0]["built_into"] == "k1" and added[0]["mirrored_from"] == hob["id"]
    # its counter missing in the twin: the copy is dropped with the reason (the room completes itself)
    added, dropped = C.copy_added(out["rooms"][0], ROOM, [hob], C.Transform("identity"), [], out, ctx, ids={})
    assert added == [] and "no counterpart here" in dropped[0]["reason"]


# --------------------------------------------------------------------------
# 2. The build: the module plan holds the hob (with its oven) and the fridge
# --------------------------------------------------------------------------

def test_the_fit_and_the_module_plan_build_the_modules_into_the_run():
    b = kitchen()
    best = SV.solve_room(b, ROOM, k=1)[0]
    hob = next(p for p in best["pieces"] if p["type"] == "stove")
    under, _rec = SV.built_in_kitchen(SV.apply_candidate(b, ROOM, best), b["rooms"][0], None, "fridge", "f_L0_901")
    after = SV.apply_candidate(b, ROOM, best)
    after["furniture"] = [f for f in after["furniture"] if f["type"] != "fridge"] + ([under] if under else [])
    kitchen_ = F.kitchen_built_ins(after)
    hints = kitchen_["hints"]["k1"]
    assert hints["hob_piece"] == hob["id"] and hints["oven"] is True and hints["hob_w_m"] == pytest.approx(0.6)
    assert kitchen_["sinks"][hob["id"]] == "k1" and kitchen_["sinks"]["sk"] == "k1"
    if under is not None:
        assert hints["fridge_piece"] == "f_L0_901" and kitchen_["sinks"]["f_L0_901"] == "k1"
    plan = MOD.plan_kitchen_run(dict(by_id(after)["k1"], module_hints=hints))
    kinds = {r["kind"]: r for r in plan["built_ins"]}
    assert kinds["hob"]["id"] == hob["id"] and kinds["hob"]["oven"] is True and kinds["sink"]["id"] == "sk"
    assert "fridge" not in plan["cutouts"] and "hob" in plan["cutouts"]
    oven = next(m for m in plan["modules"] if m.get("holds") == "hob")
    assert oven["front"] == "oven" and "oven" in oven["product"]
    parts = MOD.module_parts(plan)
    roles = {p["role"] for p in parts}
    keys = {p["key"] for p in parts}
    assert {"hob", "ring", "front", "handle"} <= roles and {"dark", "glass", "steel"} <= keys
    run = dict(by_id(after)["k1"], asset={"module_plan": plan})
    asset = F.built_in_fit(hob, run, "relaxed")
    assert asset["built_in"] == "k1" and asset["module_plan"]["kind"] == "hob" and "hob unit" in asset["fallback_reason"]


def test_an_under_counter_fridge_hint_builds_an_appliance_door():
    counter = fp("k1", "kitchen_counter", (1.5, 2.68), (3.0, 0.6), 270.0)
    plan = MOD.plan_kitchen_run(dict(counter, module_hints={"fridge_x_m": 1.0, "fridge_w_m": 0.6,
                                                            "fridge_piece": "f9"}))
    unit = next(m for m in plan["modules"] if m.get("holds") == "fridge")
    assert unit["front"] == "fridge" and unit["size_m"][0] == pytest.approx(0.6)
    assert plan["built_ins"] == [{"id": "f9", "kind": "fridge", "x_m": 1.0, "w_m": 0.6, "drawn_x_m": 1.0,
                                  "shift_m": 0.0}]
    parts = MOD._base_unit_parts(unit, {}, 0.6)
    assert any(p["key"] == "steel" and p["role"] == "front" for p in parts)


# --------------------------------------------------------------------------
# 3. Wall cabinets over every counter run, drawn or added
# --------------------------------------------------------------------------

def test_wall_cabinets_hang_over_an_added_run_and_never_over_its_hob():
    counter = fp("k1", "kitchen_counter", (1.5, 2.68), (3.0, 0.6), 270.0, source="added_by_ai")
    stove = fp("st", "stove", (2.2, 2.68), (0.6, 0.6), 270.0, source="added_by_ai")
    b = M.building(w=4.0, h=3.0, room_type="kitchen", window=None, door_x=3.4, furniture=[counter, stove])
    out = copy.deepcopy(b)
    added = C.hang_wall_cabinets(out["rooms"][0], b, out)
    assert added and all(f["type"] == "wall_cabinet" and f["rule"]["run"] == "k1" for f in added)
    hob = P.drawn_piece(stove).polygon()
    assert all(P.drawn_piece(f).polygon().intersection(hob).area < 1e-6 for f in added)
    assert C.hang_wall_cabinets(out["rooms"][0], b, out) == []                   # asked twice: hung already


# --------------------------------------------------------------------------
# 4. Dressing rooms
# --------------------------------------------------------------------------

def dressing(label="Soyunma Odası", room_type="other", w=2.4, h=2.45) -> dict:
    b = M.building(w=w, h=h, room_type=room_type, window=None, door_x=w / 2.0)
    b["rooms"][0].update(label=label, label_raw=label.upper())
    return b


def test_a_dressing_room_by_its_label_gets_wardrobe_runs_along_its_free_walls():
    for label, rtype in (("Soyunma Odası", "other"), ("Giyinme Odası", "other"), ("Walk-in closet", "storage"),
                         ("Dressing", "unknown"), ("Ankleidezimmer", "other"), ("Vestidor", "storage")):
        b = dressing(label, rtype)
        assert PR.room_kind(b, b["rooms"][0]) == "dressing", label
        prog = PR.room_program(b, ROOM)
        assert [g["group"] for g in prog["groups"]] == ["dressing"], label
    b = dressing()
    best = SV.solve_room(b, ROOM, k=1)[0]
    assert not best["hard_failures"]
    runs = [p for p in best["pieces"] if p["type"] == "wardrobe"]
    assert runs and all(p["footprint"]["size"][1] == pytest.approx(0.6) for p in runs)
    walls = [P.room_context(b, b["rooms"][0]).nearest_segment(P.back_edge_midpoint(
        P.drawn_piece(p).center, P.drawn_piece(p).rotation_deg, P.drawn_piece(p).size)) for p in runs]
    assert len(walls) == len(set(walls))                                           # one run per wall
    assert len(runs) >= 2 and min(p["footprint"]["size"][0] for p in runs) >= 1.6   # the runs fill their walls
    assert not [p for p in best["pieces"] if p["type"] in ("bench", "ottoman")]    # no bench at a run's cost
    door = P.room_context(b, b["rooms"][0]).doors[0]
    assert all(P.drawn_piece(p).polygon().intersection(door.zone).area < 1e-6 for p in best["pieces"])
    after = SV.apply_candidate(b, ROOM, best)
    assert not [v for v in GC.check_room(after, ROOM) if v["check"] in ("G13", "G14")]


def test_a_storage_room_read_as_a_dressing_room_is_furnished():
    b = dressing("Walk-in closet", "storage")
    assert [r["id"] for r in L.empty_rooms(b)] == [ROOM]
    assert [g["group"] for g in PR.room_program(b, ROOM)["groups"]] == ["dressing"]
    b2 = dressing("Depo", "storage")
    assert L.empty_rooms(b2) == [] and PR.room_program(b2, ROOM)["groups"] == []


def two_rooms(neighbour_type: str) -> dict:
    """A 4.0 x 3.0 m room and a 1.5 x 2.0 m room east of it, one door between them (the small room's only door)."""
    b = M.building(w=4.0, h=3.0, room_type=neighbour_type, window=None, door_x=1.0)
    b["rooms"][0]["label"] = "Ebeveyn Yatak Odası" if neighbour_type == "bedroom" else "Hol"
    b["walls"].append({"id": "w_x", "level_id": "L0", "start": [4.05, 0.0], "end": [4.05, 2.0], "thickness": 0.1,
                       "status": "verified", "evidence": []})
    b["openings"].append({"id": "d2", "type": "door", "level_id": "L0", "wall_id": "w_x", "center": [4.05, 1.0],
                          "width": 0.8, "swing_side": "r_small", "status": "verified", "evidence": []})
    b["rooms"].append({"id": "r_small", "level_id": "L0", "label": "", "label_raw": "", "room_type": "other",
                       "polygon": [[4.1, 0.0], [5.6, 0.0], [5.6, 2.0], [4.1, 2.0]], "area_computed": 3.0,
                       "has_documented_furniture": False, "status": "verified"})
    return b


def test_a_small_room_whose_only_door_opens_into_a_bedroom_is_a_dressing_room():
    b = two_rooms("bedroom")
    small = b["rooms"][1]
    assert PR.door_neighbours(b, small) == [ROOM]
    assert PR.dressing_room(b, small) and PR.room_kind(b, small) == "dressing"
    hall = two_rooms("hall")
    assert not PR.dressing_room(hall, hall["rooms"][1]) and PR.room_kind(hall, hall["rooms"][1]) == "other"


# --------------------------------------------------------------------------
# 5. real06 (the run of 26 Oct 2026, cut to the kitchen and the dressing room)
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real06() -> dict:
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_real06_kitchen_gets_its_hob_and_fridge(real06):
    prog = PR.room_program(real06, "r_L0_mutfak")
    run = next(g for g in prog["groups"] if g["group"] == "kitchen_run")
    assert run["drawn"] and {"stove", "fridge"} <= set(run["missing"])
    cands = SV.solve_room(real06, "r_L0_mutfak", prog, k=3)
    usable = [c for c in cands if not c["hard_failures"] and c["pieces"]]
    assert usable
    for cand in usable:
        types = [p["type"] for p in cand["pieces"]]
        assert "stove" in types and "fridge" in types, types
        hob = next(p for p in cand["pieces"] if p["type"] == "stove")
        assert hob["built_into"] == "f_L0_031"           # the free run on the wall, not the counter across the opening
        assert {r["kind"] for r in cand["built_ins"] if r["placed"]} >= {"hob", "fridge"}
    after = SV.apply_candidate(real06, "r_L0_mutfak", usable[0])
    assert not [v for v in GC.check_room(after, "r_L0_mutfak") if v["check"] == "G9"]


def test_real06_dressing_room_gets_wardrobes(real06):
    room = next(r for r in real06["rooms"] if r["id"] == "r_L1_soyunma_odasi")
    assert PR.room_kind(real06, room) == "dressing"
    assert C.completion_skip_reason(room, C.Settings(), real06) is None
    best = SV.solve_room(real06, "r_L1_soyunma_odasi", k=1)[0]
    assert not best["hard_failures"]
    assert sum(1 for p in best["pieces"] if p["type"] == "wardrobe") >= 2


def test_real06_completion_records_and_reports_the_built_ins(real06, tmp_path):
    out, records = C.complete_building(real06, "x", None, C.Settings())
    kitchen_rec = next(r for r in records if r.room_id == "r_L0_mutfak")
    assert {b["kind"] for b in kitchen_rec.built_ins if b.get("placed")} >= {"hob", "fridge"}
    assert any(f["type"] == "wall_cabinet" for f in kitchen_rec.wall_cabinets)
    hob = next(f for f in out["furniture"] if f["room_id"] == "r_L0_mutfak" and f["type"] == "stove")
    cabinets = [f for f in out["furniture"] if f["type"] == "wall_cabinet"]
    assert all(P.drawn_piece(f).polygon().intersection(P.drawn_piece(hob).polygon()).area < 1e-6 for f in cabinets)
    dressing_rec = next(r for r in records if r.room_id == "r_L1_soyunma_odasi")
    # 26 Oct 2026 (infer._wardrobe_run_type): the room's two drawn 2.27 m runs along its walls are its wardrobes (typed
    # by code), so the completion adds no second set of runs beside them
    assert {t["id"]: t["type"] for t in dressing_rec.typed_by_code} == {"f_L1_014": "wardrobe", "f_L1_015": "wardrobe"}
    assert not [f for f in dressing_rec.added if f["type"] == "wardrobe"]
    text = C.report(records, out, C.Settings(), [])
    assert "## Built into the kitchen runs" in text and "hob" in text


# --------------------------------------------------------------------------
# 5. The critics judge a built-in module and a cut-off area like the solver does
# --------------------------------------------------------------------------

def test_a_module_built_into_a_counter_is_not_a_second_door_finding():
    from wenart.furniture import plausibility as PL
    counter = fp("k1", "kitchen_counter", (1.5, 0.3), (3.0, 0.6), 90.0)        # drawn over the door d1 (x 0.55-1.45)
    fridge = fp("fz", "fridge", (1.0, 0.3), (0.6, 0.6), 90.0, source="added_by_ai", height=0.82, built_into="k1",
                built_in={"kind": "fridge", "host": "k1"})
    b = M.building(w=4.0, h=3.0, room_type="kitchen", window=None, door_x=1.0, furniture=[counter, fridge])
    found = PL.room_violations(b, b["rooms"][0])
    f7 = {v["target"] for v in found if v["check"] == "F7"}
    assert "k1" in f7 and "fz" not in f7                     # the counter's own finding covers the door
    r3 = [v for v in found if v["check"] == "R3"]
    assert r3 and all("fz" not in v["metrics"]["pieces"] for v in r3)
    loose = copy.deepcopy(b)                                 # the same fridge standing alone: its own finding
    for f in loose["furniture"]:
        f.pop("built_into", None)
        f.pop("built_in", None)
    assert "fz" in {v["target"] for v in PL.room_violations(loose, loose["rooms"][0]) if v["check"] == "F7"}


def _cut_off_room(barrier_source: str, north_door: bool = True) -> dict:
    """A 4 x 3 m room entered from the south (d1, 0.90 m); a 4 m wardrobe row across it at y 1.2-1.8 walls the north
    half off; an added armchair stands in that north half; a narrower second door d2 opens into the north half."""
    row = fp("row", "wardrobe", (2.0, 1.5), (4.0, 0.6), 270.0, source=barrier_source)
    chair = fp("ch", "armchair", (2.0, 2.55), (0.8, 0.8), 270.0, source="added_by_ai")
    b = M.building(w=4.0, h=3.0, room_type="bedroom", window=None, door_x=1.0, furniture=[row, chair])
    if north_door:
        b["openings"].append({"id": "d2", "type": "door", "level_id": "L0", "wall_id": "w_n", "center": [0.6, 3.05],
                              "width": 0.8, "swing_side": ROOM, "status": "verified", "evidence": []})
    return b


def _chair_g11(b: dict) -> list:
    return [v for v in GC.check_room(b, ROOM) if v["check"] == "G11" and v["target"] == "ch"]


def test_an_added_piece_in_an_area_the_drawn_pieces_cut_off_is_a_minor_walkway_finding():
    b = _cut_off_room("from_documents")
    assert GC.entrance_door(b, b["rooms"][0], P.room_context(b, b["rooms"][0])) == "d1"
    g11 = _chair_g11(b)
    assert g11 and all(v["severity"] == "minor" and v["metrics"]["cut_off_by_drawn"] for v in g11)
    assert "the drawn pieces alone already cut that area off" in g11[0]["message"]
    assert GC.zones_from_any_door(b, ROOM).get(("ch", g11[0]["metrics"]["zone"])) is True
    # no door reaches the north half: nobody reaches the chair, the finding stays major
    g11 = _chair_g11(_cut_off_room("from_documents", north_door=False))
    assert g11 and all(v["severity"] == "major" and "cut_off_by_drawn" not in v["metrics"] for v in g11)
    # the same row added by the AI: the added pieces cut the area off themselves, the finding stays major
    g11 = _chair_g11(_cut_off_room("added_by_ai"))
    assert g11 and all(v["severity"] == "major" and "cut_off_by_drawn" not in v["metrics"] for v in g11)


def test_real06_completed_kitchen_has_no_door_finding_for_its_built_in_modules(real06):
    from wenart.furniture import plausibility as PL
    out, _records = C.complete_building(real06, "x", None, C.Settings())
    room = next(r for r in out["rooms"] if r["id"] == "r_L0_mutfak")
    built = {f["id"] for f in out["furniture"] if f.get("room_id") == "r_L0_mutfak" and f.get("built_into")}
    assert built
    found = PL.room_violations(out, room)
    assert not [v for v in found if v["check"] in ("F7", "R3") and v["target"] in built]
