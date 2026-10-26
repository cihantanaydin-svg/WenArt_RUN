"""Milestone 13, track T3 (docs/milestone13.md §1.4, §3.0 K3, §13.1-§13.3): code-first typing of untyped drawn
footprints (twin / level / block / group member), drawn groups re-solved as one unit (0.5 m per member), an
unbuilt drawn anchor that never blocks its own group, room-type aliases, tiered minimums, the designer terms as
data, the rug as a group member, S2 tolerances by class, F8 naming the missing anchor and F2 on every drawn piece.
Every test here fails on the Milestone 12 code."""
from __future__ import annotations

import copy
import inspect
import json
from pathlib import Path

import pytest
from shapely.geometry import Point

import _m11_room as M
from test_scene_checks import LIB, building as scene_building, checks_of, parametric_mesh, piece as scene_piece
from wenart.blender import scene_checks as SC
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import infer as INF
from wenart.furniture import locked as LK
from wenart.furniture import placer as P
from wenart.furniture import plausibility as PL
from wenart.furniture import program as PR
from wenart.furniture import solver as SV

ROOT = Path(__file__).resolve().parents[1]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_final.json"
ROOM = M.ROOM_ID


def fp(pid, ftype, center, size, front, **kw):
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def unknown(pid, center, size, rotation=0.0, **kw):
    return M.fp(pid, "unknown", center, size, rotation=rotation, front=None, status="unverified", **kw)


def unbuilt(item: dict) -> dict:
    """A drawn piece the fit left unbuilt (a library gap: ``asset.method`` none)."""
    return dict(item, asset={"method": "none", "asset_id": None, "fallback_reason": "no model within the caps"},
                library_gap="none")


def two_rooms(twin=True) -> dict:
    """Two 4 x 4 bedrooms side by side (the second mirrors the first about x = 4.5): twins when ``twin``, else two
    rooms on two levels at the same plan position."""
    b = M.building(w=4.0, h=4.0, room_type="bedroom", window=None)
    a = b["rooms"][0]
    second = copy.deepcopy(a)
    if twin:
        second.update(id="r_L0_oda_2", polygon=[[5.0, 0.0], [9.0, 0.0], [9.0, 4.0], [5.0, 4.0]], twin_of=a["id"],
                      twin_transform=[-1.0, 0.0, 9.0, 0.0, 1.0, 0.0])
    else:
        second.update(id="r_L1_oda", level_id="L1")
        b["levels"].append({"id": "L1", "label": "1. Kat", "elevation": 3.0, "ceiling_height": 2.7})
    b["rooms"].append(second)
    return b


# --------------------------------------------------------------------------
# 1. Code-first typing
# --------------------------------------------------------------------------

def test_type_by_code_contract():
    assert list(inspect.signature(INF.type_by_code).parameters) == ["building", "piece"]
    # 26 Oct 2026: same_block (one block drawn again elsewhere in the project gets one type)
    assert set(INF.CODE_TYPE_METHODS) == {"twin", "level", "same_block", "block", "group_member"}
    assert list(inspect.signature(GR.drawn_groups).parameters) == ["building", "room_id"]
    assert GR.GROUP_MEMBER_MOVE_MAX_M == 0.5


def test_twin_room_types_the_same_footprint_mirrored():
    b = two_rooms(twin=True)
    bed = fp("b1", "bed_double", (1.02, 2.0), (1.6, 2.0), 0.0)                    # headboard on the west wall
    box = unknown("u1", (7.98, 2.0), (2.0, 1.6), rotation=0.0)                     # its mirror image, untyped
    box["room_id"] = "r_L0_oda_2"
    b["furniture"] = [bed, box]
    got = INF.type_by_code(b, box)
    assert got and got["type"] == "bed_double" and got["method"] == "twin" and got["confidence"] == INF.CONF_TWIN
    assert got["evidence"]["method"] == "inferred" and got["evidence"]["source_id"] == "b1"
    assert got["front_deg"] == pytest.approx(180.0)                                # the mirrored front
    out, props = INF.apply_code_types(b)
    u1 = next(f for f in out["furniture"] if f["id"] == "u1")
    assert u1["type"] == "bed_double" and u1["type_method"] == "twin" and u1["inferred"] is True
    assert [p["piece_id"] for p in props] == ["u1"]


def test_another_level_types_the_same_plan_position():
    b = two_rooms(twin=False)
    tub = fp("t1", "bathtub", (2.0, 0.4), (1.7, 0.75), 90.0)
    box = unknown("u1", (2.0, 0.4), (0.75, 1.7), rotation=90.0)                   # the same rectangle, turned
    box.update(room_id="r_L1_oda", level_id="L1")
    b["furniture"] = [tub, box]
    got = INF.type_by_code(b, box)
    assert got and (got["type"], got["method"]) == ("bathtub", "level") and got["evidence"]["source_id"] == "t1"
    far = copy.deepcopy(box)
    far["footprint"]["center"] = [2.3, 0.4]                                        # 0.3 m off: not the same drawing
    b["furniture"] = [tub, far]
    got = INF.type_by_code(b, far)
    assert got is None or got["method"] != "level"


def test_a_block_name_types_a_footprint_that_fits():
    b = M.building(w=4.5, h=4.0, room_type="bedroom")
    box = unknown("u1", (1.3, 2.0), (2.55, 2.0), rotation=90.0)                   # the real04 YATAK block, 27 % wide
    box["evidence"] = [{"file": "plan.dwg", "method": "vector", "confidence": 0.9, "entity": "INSERT:1", "block": "YATAK"}]
    b["furniture"] = [box]
    got = INF.type_by_code(b, box)
    assert got and (got["type"], got["method"]) == ("bed_double", "block") and got["evidence"]["block"] == "YATAK"
    assert "yatak" in got["reason"] and got["confidence"] == INF.CONF_BLOCK
    box["evidence"][0]["block"] = "xref_1+1_B_PLAN"                                 # no furniture word: no block type
    got = INF.type_by_code(b, box)
    assert got is None or got["method"] != "block"


def test_the_missing_group_member_of_that_size_is_typed():
    bath = M.building(w=2.7, h=1.9, room_type="bathroom", window=None, door_x=0.6)
    toilet = fp("to", "toilet", (2.3, 1.55), (0.4, 0.7), 270.0)
    basin = fp("wb", "washbasin", (1.3, 1.675), (0.6, 0.45), 270.0)
    tub = unknown("u1", (2.3, 0.6), (1.83, 0.8), rotation=90.0)                   # real04's ARC cluster: the tub
    bath["furniture"] = [toilet, basin, tub]
    got = INF.type_by_code(bath, tub)
    assert got and (got["type"], got["method"]) == ("bathtub", "group_member") and "shower|bathtub" in got["reason"]
    assert got["confidence"] == INF.CONF_GROUP
    # infer_types runs it first: the proposal carries the method, apply_inferences writes it with the evidence.
    props = INF.infer_types(bath)
    assert [(p["piece_id"], p["type"], p["type_method"]) for p in props] == [("u1", "bathtub", "group_member")]
    out = INF.apply_inferences(bath, props)
    u1 = next(f for f in out["furniture"] if f["id"] == "u1")
    assert u1["type"] == "bathtub" and u1["type_method"] == "group_member" and u1["inferred"] is True
    assert u1["evidence"][-1]["rule"].endswith("group_member") and u1.get("build") is not False


def test_an_untyped_piece_left_unbuilt_for_being_untyped_is_typed_and_built():
    b = M.building(w=4.5, h=5.0, room_type="bedroom")
    bed = fp("b1", "bed_double", (1.02, 2.5), (1.6, 2.0), 0.0)
    box = unknown("u2", (0.22, 1.47), (0.4, 0.45), build=False,
                  not_built_reason="untyped (CLAUDE.md: no untyped piece is built)")
    b["furniture"] = [bed, box]
    assert INF.untyped_drawn(box)
    out, props = INF.apply_code_types(b)
    u2 = next(f for f in out["furniture"] if f["id"] == "u2")
    assert u2["type"] == "nightstand" and u2["build"] is True and "not_built_reason" not in u2
    # The completion path: a type proposal that keeps the drawn footprint and status (the locked check).
    out2, _p = INF.apply_code_types(b, proposal=True)
    u2 = next(f for f in out2["furniture"] if f["id"] == "u2")
    assert u2["type_proposal"] is True and u2["drawn_type"] == "unknown" and u2["status"] == "unverified"
    assert u2["footprint"] == box["footprint"] and u2["adjusted_by_ai"]["typed_by_code"] == "group_member"
    assert not LK.check(b, out2, "complete")


@pytest.mark.skipif(not REAL04.exists(), reason="the committed real04 building is not here")
def test_real04_untyped_pieces_are_typed_by_code():
    b = json.loads(REAL04.read_text(encoding="utf-8"))
    untyped = [f for f in b["furniture"] if INF.untyped_drawn(f)]
    props = INF.code_types(b)
    by_id = {p["piece_id"]: p for p in props}
    # 20 untyped drawn pieces; code types the ones it can prove (3 on 15 Oct 2026), the rest wait for the plan crop
    # (two AI passes disagreed on a type that fits, or no required group misses a member of that size).
    assert len(untyped) >= 15 and len(props) >= 3
    # The drawn bathtub of r_L0_banyo (an ARC cluster, 1.83 x 0.80 m): the same drawing as the typed tub one level
    # down (f_L-1_056); its mirror image in the twin bathroom follows by the twin rule.
    assert (by_id["f_L0_043"]["type"], by_id["f_L0_043"]["type_method"]) == ("bathtub", "level")
    assert by_id["f_L0_043"]["evidence"]["source_id"] == "f_L-1_056"
    assert by_id["f_L0_044"]["type"] == "bathtub" and by_id["f_L0_044"]["type_method"] in ("level", "twin")
    # The twin villas: a piece typed in one villa types its mirror image in the other.
    assert any(p["type_method"] == "twin" for p in props)
    # The play rooms' drawn sofas miss their coffee tables: the 1.03 x 0.69 m footprint beside them is one.
    assert by_id["f_L1_015"]["type"] == "table_coffee" and by_id["f_L1_015"]["type_method"] == "group_member"
    assert all(p["type_method"] in INF.CODE_TYPE_METHODS and p["evidence"]["method"] == "inferred" for p in props)


# --------------------------------------------------------------------------
# 2. Drawn groups as one unit
# --------------------------------------------------------------------------

def dining_room():
    """A 6 x 5 dining room with a misread 3.6 x 1.0 m table (the product grid ends at 3.4 m) and six drawn chairs."""
    table = M.fp("t1", "table_dining", (3.0, 2.6), (3.6, 1.0), rotation=0.0, front=None)
    chairs = []
    for k, x in enumerate((2.0, 3.0, 4.0)):
        chairs.append(fp(f"c{k}", "chair", (x, 2.6 - 0.75), (0.45, 0.45), 90.0))
        chairs.append(fp(f"c{k + 3}", "chair", (x, 2.6 + 0.75), (0.45, 0.45), 270.0))
    return M.building(w=6.0, h=5.0, room_type="dining", window=(3.0, 1.2), furniture=[table] + chairs)


def test_drawn_groups_are_read_from_the_drawn_pieces_built_or_not():
    b = dining_room()
    (g,) = GR.drawn_groups(b, ROOM)
    assert g["anchor_id"] == "t1" and g["template"] == "dining" and sorted(g["members"]) == [f"c{k}" for k in range(6)]
    assert g["centre"] == [3.0, 2.6] and all(g["roles"][m] == "chair" for m in g["members"])
    b["furniture"][0] = unbuilt(b["furniture"][0])
    (g2,) = GR.drawn_groups(b, ROOM)
    assert g2["anchor_id"] == "t1" and g2["built"]["t1"] is False           # an unbuilt anchor still heads its group


def test_a_misread_dining_group_is_re_solved_with_every_member_within_half_a_metre():
    b = dining_room()
    prog = PR.room_program(b, ROOM)
    dining = next(g for g in prog["groups"] if g["group"] == "dining")
    assert dining["drawn"] and dining["resolve"]["anchor_id"] == "t1" and "misread" in dining["resolve"]["reason"]
    assert sorted(dining["resolve"]["members"]) == [f"c{k}" for k in range(6)]
    cands = SV.solve_room(b, ROOM, prog, k=3)
    best = cands[0]
    assert not best["hard_failures"] and sorted(best["resolved"]) == ["c0", "c1", "c2", "c3", "c4", "c5", "t1"]
    moved = {p["id"]: p for p in best["pieces"] if p["source"] == "from_documents"}
    table = moved["t1"]
    assert table["footprint"]["size"] == [3.0, 1.0]                         # the nearest real product
    assert table["drawn_footprint"] == b["furniture"][0]["footprint"] and table["drawn_type"] == "table_dining"
    assert table["adjusted_by_ai"]["by"] == "solver" and "misread" in table["adjusted_by_ai"]["reason"]
    assert table["asset"] is None                                            # resized: fitted again
    for pid, p in moved.items():
        d = P.drawn_piece(p).center
        drawn = next(f for f in b["furniture"] if f["id"] == pid)["footprint"]["center"]
        assert ((d[0] - drawn[0]) ** 2 + (d[1] - drawn[1]) ** 2) ** 0.5 <= GR.GROUP_MEMBER_MOVE_MAX_M + 1e-6
        assert p["drawn_group"]["anchor_id"] == "t1" and p["group"]["group"] == "dining"
        assert p["drawn_group"]["moved_m"] <= GR.GROUP_MEMBER_MOVE_MAX_M
    assert all(p["adjusted_by_ai"]["moved_m"] <= 0.5 for p in moved.values() if p.get("adjusted_by_ai"))
    (dg,) = best["drawn_groups"]
    assert dg["anchor_id"] == "t1" and set(dg["moved"]) == set(moved)
    after = SV.apply_candidate(b, ROOM, best)
    ids = [f["id"] for f in after["furniture"]]
    assert ids[:7] == [f["id"] for f in b["furniture"]] and len(ids) == len(set(ids))      # replaced in place
    assert next(f for f in after["furniture"] if f["id"] == "t1")["footprint"]["size"] == [3.0, 1.0]
    assert not LK.check(b, after, "complete")                                # the locked rules allow the 0.5 m
    assert not [v for v in GC.check_room(after, ROOM) if v["severity"] != "minor"]


def test_solve_room_takes_a_drawn_group_on_request_and_the_keep_switches_turn_it_off():
    b = dining_room()
    b["furniture"][0]["footprint"]["size"] = [2.0, 1.0]                        # a sound table: no reason by itself
    prog = PR.room_program(b, ROOM)
    assert not any(g.get("resolve") for g in prog["groups"])
    (g,) = GR.drawn_groups(b, ROOM)
    best = SV.solve_room(b, ROOM, k=1, drawn_group=g)[0]
    assert "t1" in best["resolved"]
    assert "t1" in SV.solve_room(b, ROOM, k=1, drawn_group="t1")[0]["resolved"]
    bad = dining_room()                                                         # the misread table again
    assert any(g.get("resolve") for g in PR.room_program(bad, ROOM)["groups"])
    for brief in ({"furnished_rooms": "keep"}, {"furnished_rooms_keep_size": True},
                  {"furnished_rooms_keep": [ROOM]}, {"furnished_rooms_keep": ["Oda"]}):
        prog = PR.room_program(bad, ROOM, brief=brief)
        assert not any(g.get("resolve") for g in prog["groups"]), brief
        assert "not re-solved" in prog["reason"]


def test_an_unbuilt_drawn_anchor_never_blocks_its_group_and_never_suppresses_it():
    bed = unbuilt(fp("b1", "bed_double", (1.3, 2.5), (2.55, 2.0), 0.0))        # real04's YATAK block: 2.55 m, unbuilt
    lamp = fp("l1", "floor_lamp", (0.4, 4.2), (0.3, 0.3), 0.0)
    b = M.building(w=4.5, h=5.0, room_type="bedroom", furniture=[bed, lamp])
    prog = PR.room_program(b, ROOM)
    sleep = next(g for g in prog["groups"] if g["group"] == "sleeping_double")
    assert sleep["drawn"] and sleep["resolve"] and "not built" in sleep["resolve"]["reason"]
    assert "left out" not in prog["reason"]
    # The solver's free space: the unbuilt bed is not an obstacle (its cells are free), the lamp is.
    fixed = SV._fixed_items(b, ROOM, set(), exclude={"b1"})
    assert [f["id"] for f in fixed] == ["l1"]
    best = SV.solve_room(b, ROOM, prog, k=1)[0]
    assert not best["hard_failures"] and "b1" in best["resolved"]
    new_bed = next(p for p in best["pieces"] if p["id"] == "b1")
    assert new_bed["footprint"]["size"][0] <= 2.0 and new_bed["asset"] is None and new_bed["build"] is True
    assert new_bed["adjusted_by_ai"]["resized"] is True and new_bed["drawn_footprint"]["size"] == [2.55, 2.0]
    assert {p["type"] for p in best["pieces"]} >= {"bed_double", "nightstand"}
    after = SV.apply_candidate(b, ROOM, best)
    assert not LK.check(b, after, "complete")


def test_a_drawn_group_no_place_takes_stays_as_drawn_and_blocks_the_others():
    """A wardrobe drawn from wall to wall across the door: nowhere to put a 3.9 m run within 0.5 m, so it stays as
    drawn (kept as an obstacle for the other groups, not dropped)."""
    wardrobe = fp("w1", "wardrobe", (2.25, 0.4), (3.9, 0.6), 90.0)              # on the south wall, over the door
    b = M.building(w=4.5, h=5.0, room_type="bedroom", door_x=1.0, furniture=[wardrobe])
    prog = PR.room_program(b, ROOM)
    storage = next(g for g in prog["groups"] if g["group"] == "storage")
    assert storage["resolve"] and "door" in storage["resolve"]["reason"]
    best = SV.solve_room(b, ROOM, prog, k=1)[0]
    assert "w1" not in best["resolved"]
    kept = next(p for p in best["pieces"] if p["id"] == "w1")
    assert kept["footprint"] == wardrobe["footprint"] and "adjusted_by_ai" not in kept
    for p in best["pieces"]:
        if p["id"] != "w1":
            assert P.drawn_piece(p).polygon().intersection(P.drawn_piece(wardrobe).polygon()).area < 1e-4


# --------------------------------------------------------------------------
# 3. F8 names the missing anchor; F2 on every drawn piece
# --------------------------------------------------------------------------

def test_f8_names_the_unbuilt_anchor_and_f2_sees_unbuilt_drawn_pieces():
    sofa = unbuilt(fp("s1", "sofa", (0.47, 2.5), (2.2, 0.9), 0.0))
    chair = fp("a1", "armchair", (2.0, 2.5), (0.8, 0.8), 180.0)               # 1.1 m from the (unbuilt) sofa
    b = M.building(w=4.5, h=5.0, room_type="living", furniture=[sofa, chair])
    f8 = [v for v in PL.score_room(b, ROOM)["violations"] if v["check"] == "F8"]
    assert len(f8) == 1 and f8[0]["target"] == "a1"
    assert f8[0]["metrics"]["missing_anchor"] == "s1" and f8[0]["metrics"]["cause"] == "anchor_not_built"
    assert "which is not built" in f8[0]["message"] and "s1" in f8[0]["message"]
    bed = unbuilt(fp("b1", "bed_double", (1.3, 2.5), (2.55, 2.0), 0.0))
    b2 = M.building(w=4.5, h=5.0, room_type="bedroom", furniture=[bed])
    f2 = [v for v in PL.score_room(b2, ROOM)["violations"] if v["check"] == "F2"]
    assert len(f2) == 1 and f2[0]["target"] == "b1" and f2[0]["metrics"]["built"] is False
    assert "not built" in f2[0]["message"]


# --------------------------------------------------------------------------
# 4. Room-type aliases, the stair landing, room-size variants
# --------------------------------------------------------------------------

def test_room_kind_reads_labels_and_drawn_content():
    b = M.building(w=6.0, h=6.5, room_type="other")
    room = b["rooms"][0]
    room.update(label="Oyun Aktivite Ve Dinlenme Odası", label_raw="OYUN AKTİVİTE VE DİNLENME ODASI")
    assert PR.room_kind(b, room) == "living"
    room.update(label="Oda", label_raw=None, room_type="unknown")
    assert PR.room_kind(b, room) == "bedroom"                                 # a plain room of 39 m² is a bedroom
    room["area_computed"] = 0.3
    assert PR.room_kind(b, room) == "other"                                   # a 0.3 m² "Oda" is a shaft
    room.update(label="Çalışma", label_raw="ÇALIŞMA", area_computed=12.0)
    assert PR.room_kind(b, room) == "other"
    room.update(label="X", label_raw="X", room_type="other")
    b["furniture"] = [fp("s1", "sofa", (0.47, 3.0), (2.2, 0.9), 0.0)]
    assert PR.room_kind(b, room) == "living"                                  # drawn sofas make a living room
    room["room_type"] = "bedroom"
    assert PR.room_kind(b, room) == "bedroom"                                 # a typed room keeps its type


def test_an_other_room_with_drawn_sofas_gets_a_seating_group_and_no_wrong_type_finding():
    sofa = fp("s1", "sofa", (0.47, 3.0), (2.2, 0.9), 0.0)
    b = M.building(w=6.0, h=6.5, room_type="other", furniture=[sofa])
    b["rooms"][0].update(label="Oyun Aktivite Ve Dinlenme Odası")
    prog = PR.room_program(b, ROOM)
    seat = next(g for g in prog["groups"] if g["group"] == "seating")
    assert seat["drawn"] and seat["anchor_id"] == "s1" and not seat["note"].startswith("no completion")
    assert prog["kind"] == "living" and "read as living" in prog["reason"]
    assert not [v for v in GC.check_room(b, ROOM) if v["check"] == "G14"]
    assert not [v for v in PL.score_room(b, ROOM)["violations"] if v["check"] == "F1"]
    assert "living" in PL.room_types(b, b["rooms"][0])
    best = SV.solve_room(b, ROOM, prog, k=1)[0]
    assert {"tv_unit", "table_coffee"} & {p["type"] for p in best["pieces"]}


def test_a_stair_landing_gets_no_program():
    stair = fp("st", "stair", (1.2, 1.2), (2.4, 2.2), 0.0)
    b = M.building(w=2.4, h=2.4, room_type="hall", window=None, furniture=[stair])
    b["rooms"][0].update(label="Merdiven")
    assert PR.stair_cover(b, b["rooms"][0]) > 0.6
    assert PR.room_program(b, ROOM)["groups"] == []
    assert PR.room_program(M.building(w=2.4, h=2.4, room_type="hall", window=None), ROOM)["groups"]


def test_small_room_variants_are_data():
    small = GR.small_room("living", 11.0)
    assert small and small["options"] == ["sofa"] and "turkish_imar" in small["source"] and small["flagged"]
    assert GR.small_room("living", 12.0) is None and GR.small_room("bedroom", 9.5)["sides_needed"] == 1
    prog = PR.room_program(M.building(w=3.0, h=3.6, room_type="living"), ROOM)
    assert next(g for g in prog["groups"] if g["group"] == "seating")["options"] == ["sofa"]
    # G5 in a 9 m² bedroom: one free side is enough (R14).
    bed = fp("b1", "bed_double", (0.82, 2.0), (1.6, 2.0), 0.0)
    ok = M.building(w=3.0, h=3.0, room_type="bedroom", furniture=[bed], window=None)
    assert not [v for v in GC.check_room(ok, ROOM) if v["check"] == "G5" and "side" in v["message"]]


# --------------------------------------------------------------------------
# 5. Tiered minimums
# --------------------------------------------------------------------------

def test_tiers_make_minimums_soft_by_room_class():
    small = GR.rule_for("kitchen_aisle", room_type="kitchen", area=6.0)
    assert (small["min"], small["hard"], small["tier"]) == (0.9, False, "small_kitchen")
    assert GR.rule_for("kitchen_aisle", room_type="kitchen", area=13.0)["hard"] is True
    assert GR.rule_for("walkway_main", room_type="kitchen", area=6.0)["min"] == 0.6
    assert GR.rule_for("walkway_main", room_type="living", area=6.0)["min"] == 0.8
    drawn = GR.rule_for("triangle_leg", room_type="kitchen", area=13.6, drawn_run=True)
    assert drawn["hard"] is False and drawn["tier"] == "drawn_run" and drawn["max"] == 2.7
    assert GR.rule_for("triangle_leg", room_type="kitchen", area=13.6)["hard"] is True
    # 26 Oct 2026 (real06's 24.8 m² kitchen kept no fridge): a drawn run in any kitchen scores the triangle
    assert GR.rule_for("triangle_leg", room_type="kitchen", area=15.0, drawn_run=True)["hard"] is False
    assert GR.rule_for("triangle_leg", room_type="kitchen", area=15.0)["hard"] is True
    cfg = GR.config()
    for name, tier in cfg["tiers"].items():
        assert tier["flagged"] and all(s in cfg["sources"] for s in tier["source"]) and tier["what"], name
    over = GR.tier_overrides("kitchen", 6.0)
    assert over["kitchen_aisle"] == {"min": 0.6, "rec": 0.9} and over["walkway"]["min"] == 0.6
    assert GR.use_zone("kitchen_counter", over)["front"] == 0.6 and GR.use_zone("kitchen_counter")["front"] == 0.9


def test_g8_reports_a_soft_aisle_as_minor_in_a_small_kitchen():
    def kitchen(w, h):
        run = [fp("k1", "kitchen_counter", (w / 2.0, h - 0.32), (2.4, 0.6), 270.0),
               fp("sk", "sink_kitchen", (w / 2.0 - 0.6, h - 0.32), (0.6, 0.6), 270.0),
               fp("st", "stove", (w / 2.0 + 0.6, h - 0.32), (0.6, 0.6), 270.0)]
        table = M.fp("t1", "table_dining", (w / 2.0, h - 0.62 - 0.7 - 0.4), (1.2, 0.8), rotation=0.0, front=None)
        return M.building(w=w, h=h, room_type="kitchen", window=None, furniture=run + [table])

    small = kitchen(2.6, 2.6)                                                  # 6.8 m²: the aisle is a soft term
    aisle = [v for v in GC.check_room(small, ROOM) if v["check"] == "G8" and "aisle" in v["message"]]
    assert aisle and aisle[0]["severity"] == "minor" and aisle[0]["metrics"]["tier"] == "small_kitchen"
    large = kitchen(3.2, 3.2)                                                  # 10.2 m²: hard
    aisle = [v for v in GC.check_room(large, ROOM) if v["check"] == "G8" and "aisle" in v["message"]]
    assert aisle and aisle[0]["severity"] == "major"


def test_a_fridge_beside_a_drawn_run_is_placed_with_soft_nkba_terms():
    """real04: the only fridge candidate beside the drawn run broke the hard work triangle (3.38 m > 2.70) and the
    landing; the kitchen stayed without a fridge for 7 rounds. With a drawn run they score instead (under 14 m² since
    Milestone 13; in every kitchen since 26 Oct 2026, real06)."""
    h = 4.2
    run = [fp("k1", "kitchen_counter", (1.5, h - 0.32), (3.0, 0.6), 270.0),
           fp("sk", "sink_kitchen", (0.5, h - 0.32), (0.8, 0.6), 270.0), fp("st", "stove", (2.6, h - 0.32), (0.6, 0.6), 270.0)]
    b = M.building(w=3.1, h=h, room_type="kitchen", window=(1.5, 1.0), sill=1.0, furniture=run)
    b["rooms"][0]["area_computed"] = 13.0
    prog = PR.room_program(b, ROOM)
    run_entry = next(g for g in prog["groups"] if g["group"] == "kitchen_run")
    assert run_entry["drawn"] and "fridge" in run_entry["missing"]
    best = SV.solve_room(b, ROOM, prog, k=1)[0]
    fridge = next((p for p in best["pieces"] if p["type"] == "fridge"), None)
    assert fridge is not None and not best["hard_failures"]
    after = SV.apply_candidate(b, ROOM, best)
    g8 = [v for v in GC.check_room(after, ROOM) if v["check"] == "G8" and v["target"] in (fridge["id"], "sk")]
    assert g8 and all(v["severity"] == "minor" and v["metrics"].get("tier") == "drawn_run" for v in g8)
    assert not [v for v in GC.check_room(after, ROOM) if v["check"] == "G9"]
    big = copy.deepcopy(b)
    big["rooms"][0]["area_computed"] = 15.0                     # over 14 m²: the fridge landing stays hard
    # 26 Oct 2026: the work triangle of a drawn run is scored in every kitchen (drawn_run_any), the landing is not:
    # no floor place has one here, the counter between the drawn sink and stove takes no under-counter fridge (the
    # sink would not stand between it and the hob), and the record says so (never a fridge without its landing)
    best = SV.solve_room(big, ROOM, k=1)[0]
    assert "fridge" not in {p["type"] for p in best["pieces"]}
    rec = next(r for r in best["built_ins"] if r["kind"] == "fridge")
    assert rec["placed"] is False and rec["how"] == "none" and rec["reason"].startswith("no floor place for a fridge")


# --------------------------------------------------------------------------
# 6. Designer terms as data, the rug as a group member
# --------------------------------------------------------------------------

def test_designer_terms_are_data_with_named_sources():
    cfg = GR.config()
    for rule in ("conversation_circle", "rug_seating", "rug_dining", "rug_bed", "floating", "alignment"):
        r = cfg["rules"][rule]
        assert r["flagged"] is True and r["source"] and all(s in cfg["sources"] for s in r["source"]), rule
    assert {"conversation", "rug", "anchored", "alignment"} <= set(cfg["weights"])
    assert cfg["sources"]["design_books"] and cfg["sources"]["merrell2011"] and cfg["sources"]["turkish_imar"]
    seating = GR.load_groups()["seating"]
    rug = next(p for p in seating["partners"] if p["role"] == "rug")
    assert rug["type"] == "rug" and rug["place"] == "under" and rug["gap"] == "rug_seating"
    assert next(p for p in GR.load_groups()["sleeping_double"]["partners"] if p["role"] == "rug")["place"] == "beside"
    assert "rug" in GR.DECOR_MEMBER_TYPES


def test_the_solver_scores_the_designer_terms_and_lays_the_rug_under_the_coffee_table():
    b = M.building(w=5.0, h=6.0, room_type="living", window=(2.5, 1.2))
    prog = PR.room_program(b, ROOM)
    prog["groups"] = [g for g in prog["groups"] if g["group"] == "seating"]
    prog["groups"][0]["chosen"] = "sofa_2_armchairs"
    best = SV.solve_room(b, ROOM, prog, k=1)[0]
    assert {"anchored", "alignment", "conversation", "rug"} <= set(best["terms"])
    assert 0.0 <= best["terms"]["conversation"] <= 1.0 and best["terms"]["rug"] == 1.0
    (rug,) = best["rugs"]
    assert rug["type"] == "rug" and rug["kind"] == "decor" and rug["source"] == "added_by_ai"
    sofa = next(p for p in best["pieces"] if p["type"] == "sofa")
    coffee = next(p for p in best["pieces"] if p["type"] == "table_coffee")
    assert sofa["id"] in rug["anchor_ids"] and rug["group"]["group"] == "seating"
    poly = P.Piece("rug", tuple(rug["center"]), rug["rotation_deg"], tuple(rug["size"]), False).polygon()
    assert poly.contains(Point(coffee["footprint"]["center"]))
    assert P.room_context(b, b["rooms"][0]).polygon.contains(poly)
    after = SV.apply_candidate(b, ROOM, best)
    (item,) = [d for d in after["decor"] if d["type"] == "rug"]
    assert item["id"].startswith("dec_L0_") and item["anchor_ids"] == rug["anchor_ids"] and item["host_id"] is None
    assert {"kind", "type", "level_id", "room_id", "center", "size", "source", "rotation_deg"} <= set(item)
    assert item["source"] == "added_by_ai" and item["method"] == "rule" and item["kind"] == "decor"


def test_a_runner_lies_beside_the_bed():
    b = M.building(w=4.5, h=5.0, room_type="bedroom")
    best = SV.solve_room(b, ROOM, k=1)[0]
    rugs = [r for r in best["rugs"] if r["group"]["group"] == "sleeping_double"]
    assert rugs and all(r["size"][0] < r["size"][1] or r["size"][1] < r["size"][0] for r in rugs)
    bed = P.drawn_piece(next(p for p in best["pieces"] if p["type"] == "bed_double"))
    for r in rugs:
        poly = P.Piece("rug", tuple(r["center"]), r["rotation_deg"], tuple(r["size"]), False).polygon()
        assert poly.distance(bed.polygon()) < 0.05 and poly.intersection(bed.polygon()).area < 1e-3


# --------------------------------------------------------------------------
# 7. S2 tolerances by class
# --------------------------------------------------------------------------

def test_s2_tolerances_by_class():
    assert SC.TOLERANCES["overlap_fixture"] == 0.03 and SC.TOLERANCES["overlap_soft"] == 0.05
    assert SC.TOLERANCES["overlap_m"] == 0.010
    assert SC.overlap_tolerance("toilet") == 0.03 and SC.overlap_tolerance("armchair", "ottoman") == 0.05
    assert SC.overlap_tolerance("chair", "table_dining") == 0.010 and SC.overlap_tolerance("chair", "sofa") == 0.05
    a = scene_piece("a", "armchair", (2.0, 3.0), (0.9, 0.9), asset=LIB)
    b = scene_piece("b", "armchair", (2.87, 3.0), (0.9, 0.9), asset=LIB)              # 3 cm into each other
    report = SC.measure_pure({k: parametric_mesh(p) for k, p in (("a", a), ("b", b))}, scene_building([a, b]))
    assert not checks_of(report, "S2")
    c = scene_piece("c", "chair", (2.0, 5.0), (0.45, 0.45), asset=LIB)
    d = scene_piece("d", "chair", (2.42, 5.0), (0.45, 0.45), asset=LIB)               # 3 cm: a hard piece pair
    report = SC.measure_pure({k: parametric_mesh(p) for k, p in (("c", c), ("d", d))}, scene_building([c, d]))
    (v,) = checks_of(report, "S2")
    assert v["metrics"]["tolerance_m"] == 0.010 and v["metrics"]["depth_m"] > 0.02
    toilet = scene_piece("t", "toilet", (3.0, 0.437), (0.4, 0.7), asset=LIB)        # its back 0.013 m into wall w1
    report = SC.measure_pure({"t": parametric_mesh(toilet)}, scene_building([toilet]))
    depth = report["measured"]["t"]["wall_depth_m"]
    assert 0.010 < depth <= 0.03 and report["measured"]["t"]["s2_tolerance_m"] == 0.03   # real04's toilets: 1.2-1.3 cm
    assert not checks_of(report, "S2")


# --------------------------------------------------------------------------
# 8. Review fixes (15 Oct 2026)
# --------------------------------------------------------------------------

def test_a_drawn_piece_the_fit_snapped_and_the_solver_keeps_is_not_a_new_piece():
    """A drawn piece that comes back as drawn (a skipped re-solve, a kept member) carries the fit's size-snap
    ``adjusted_by_ai`` (T1) after the fit stage; the verification counted it as the candidate's own piece and every
    candidate of the room failed on its drawn faults (the wardrobe over the door: doors_free, G11)."""
    wardrobe = fp("w1", "wardrobe", (2.25, 0.4), (3.9, 0.6), 90.0)
    wardrobe.update(adjusted_by_ai={"by": "fit", "stage": "fit", "reason": "size snap: depth 0.65 -> 0.60 m"},
                    size_snap={"drawn": [3.9, 0.65, 2.1], "snapped": [3.9, 0.6, 2.1], "product": "wardrobe 0.60 m",
                               "reason": "depth outside the product range"},
                    drawn_footprint={"center": [2.25, 0.425], "size": [3.9, 0.65], "rotation_deg": 180.0})
    b = M.building(w=4.5, h=5.0, room_type="bedroom", door_x=1.0, furniture=[wardrobe])
    best = SV.solve_room(b, ROOM, k=1)[0]
    assert not best["hard_failures"] and "w1" not in best["resolved"]
    kept = next(p for p in best["pieces"] if p["id"] == "w1")
    assert kept["footprint"] == wardrobe["footprint"] and kept["adjusted_by_ai"] == wardrobe["adjusted_by_ai"]
    # The same without the snap: the kept wardrobe's own G11 finding is not the candidate's either.
    plain = M.building(w=4.5, h=5.0, room_type="bedroom", door_x=1.0,
                       furniture=[fp("w1", "wardrobe", (2.25, 0.4), (3.9, 0.6), 90.0)])
    assert not SV.solve_room(plain, ROOM, k=1)[0]["hard_failures"]
    # The 0.5 m bound counts from where the piece was drawn (drawn_footprint), not from where the snap put it.
    (g,) = GR.drawn_groups(b, ROOM)
    assert g["centre"] == [2.25, 0.425] and GR.drawn_centre(wardrobe) == [2.25, 0.425]
    assert GR.drawn_centre(fp("x", "wardrobe", (1.0, 2.0), (1.2, 0.6), 90.0)) == [1.0, 2.0]


def test_a_generic_room_word_yields_to_a_specific_one():
    """"oda" (room) names a bedroom only when no other kind's word is in the label: a study or a laundry room is
    not a bedroom (``room_aliases.generic``)."""
    assert "oda" in GR.room_aliases()["generic"]
    b = M.building(w=4.0, h=3.0, room_type="other")
    room = b["rooms"][0]
    for label, kind in (("Çalışma Odası", "other"), ("Çamaşır Odası", "other"), ("Yatak Odası", "bedroom"),
                        ("Oda", "bedroom"), ("Oyun Odası", "living"), ("Hizmetli Odası", "bedroom")):
        room.update(label=label, label_raw=label.upper())
        assert PR.room_kind(b, room) == kind, label
    bad = copy.deepcopy(GR.config())
    bad["room_aliases"]["generic"] = ["kiler"]
    assert any("generic" in p for p in GR.validate_config(bad))


# --------------------------------------------------------------------------
# Build round 3 (K2): the solver plans partners and collisions with the fitted depth
# --------------------------------------------------------------------------

def _deeper(item: dict, ratio: float = 1.12) -> dict:
    """The piece with a library model scaled uniformly to its width that came out ``ratio`` deeper."""
    w, d = (float(v) for v in item["footprint"]["size"])
    fd = round(d * ratio, 4)
    return dict(item, asset={"method": "library", "asset_id": "lib:sofa", "scaling": "uniform",
                             "bbox_m": [w, fd, 0.85], "depth_abs_m": round(fd - d, 4),
                             "fit_scale": [ratio, ratio, ratio], "library": "abo", "licence": "CC-BY-4.0"})


def test_a_drawn_sofa_fitted_deeper_gets_its_partners_in_front_of_the_fitted_front():
    """K2 (docs/milestone13.md §14.4 T1/T3, lead decision of round 3): the builder keeps a uniformly scaled
    wall-backed model's back edge on the wall and the extra depth goes to the front, so the solver plans the coffee
    table (and every collision) with the fitted depth: the table sits ``coffee_gap`` in front of the model's real
    front, 0.108 m further than for the drawn 0.9 m sofa; the drawn record is untouched. S2 on the built meshes is
    then not expected to flag the pair (P3 / P4 verify it on the renders)."""
    sofa = fp("s1", "sofa", (0.47, 2.5), (2.2, 0.9), 0.0)                    # back on the west wall, front east
    deeper = _deeper(sofa)
    rooms = {}
    for tag, item in (("drawn", sofa), ("fitted", deeper)):
        b = M.building(w=4.5, h=5.0, room_type="living", window=(2.25, 1.2), furniture=[item])
        prog = PR.room_program(b, ROOM)
        seat = next(g for g in prog["groups"] if g["group"] == "seating")
        assert seat["drawn"] and seat["anchor_id"] == "s1" and "table_coffee" in seat["missing"]
        prog["groups"] = [seat]
        seat["chosen"] = "sofa_2_armchairs"
        best = SV.solve_room(b, ROOM, prog, k=1)[0]
        assert not best["hard_failures"]
        rooms[tag] = (b, best)
    gap = GR.rule("coffee_gap")
    planned = P.planned_piece(deeper)
    assert planned.size == (2.2, 1.008) and planned.polygon().bounds[2] == pytest.approx(0.02 + 1.008)
    coffee = {tag: next(p for p in best["pieces"] if p["type"] == "table_coffee") for tag, (_b, best) in rooms.items()}
    front = {"drawn": 0.02 + 0.9, "fitted": 0.02 + 1.008}
    for tag in ("drawn", "fitted"):
        poly = P.piece_from_furniture(coffee[tag]).polygon()
        anchor = P.planned_piece(rooms[tag][0]["furniture"][0]).polygon()
        assert poly.intersection(anchor).area < P.AREA_EPS
        assert poly.bounds[0] == pytest.approx(front[tag] + gap["rec"], abs=0.06)   # coffee_gap off the real front
        assert poly.distance(anchor) >= gap["min"] - 1e-6
    # the same gap from the fitted front, so 0.108 m further into the room than for the drawn box
    dx = coffee["fitted"]["footprint"]["center"][0] - coffee["drawn"]["footprint"]["center"][0]
    assert dx == pytest.approx(0.108, abs=0.02)
    # every new piece keeps off the fitted box, and the drawn record is what the candidate writes back
    b, best = rooms["fitted"]
    for p in best["pieces"]:
        assert P.piece_from_furniture(p).polygon().intersection(planned.polygon()).area < P.AREA_EPS
    after = SV.apply_candidate(b, ROOM, best)
    assert next(f for f in after["furniture"] if f["id"] == "s1") == deeper
    assert not SV.verify(b, ROOM, best["pieces"])[0]


def test_a_fitted_drawn_piece_is_an_obstacle_with_its_fitted_box():
    """K2: a drawn wardrobe fitted deeper blocks the solver's cells with its fitted box (``Space.fixed_pieces``), and
    ``verify`` tests a candidate's overlaps against that box."""
    wardrobe = fp("w1", "wardrobe", (2.25, 4.7), (1.8, 0.6), 270.0)         # back on the north wall, front south
    deeper = _deeper(wardrobe, 1.15)
    b = M.building(w=4.5, h=5.0, room_type="bedroom", window=None, furniture=[deeper])
    space = SV.Space(b, b["rooms"][0], SV._fixed_items(b, ROOM, set()))
    (fixed,) = space.fixed_pieces
    assert fixed.size == (1.8, 0.69) and fixed.polygon().bounds == pytest.approx((1.35, 4.31, 3.15, 5.0))
    assert fixed.planned_size is None
    for c in SV.solve_room(b, ROOM, k=2):
        for p in c["pieces"]:
            assert P.piece_from_furniture(p).polygon().intersection(fixed.polygon()).area < P.AREA_EPS
    # a candidate piece inside the fitted front strip (free of the drawn box) is a hard overlap for verify
    intruder = fp("x1", "nightstand", (2.25, 4.15), (0.4, 0.4), 270.0)     # y 3.95-4.35: in the strip 4.31-4.40
    intruder["source"] = "added_by_ai"
    hard, _v = SV.verify(b, ROOM, [intruder])
    assert any("no_overlap with w1" in h for h in hard)
    drawn_only = M.building(w=4.5, h=5.0, room_type="bedroom", window=None, furniture=[wardrobe])
    assert not any("no_overlap" in h for h in SV.verify(drawn_only, ROOM, [intruder])[0])


def test_a_re_solved_sofa_group_plans_the_fitted_box_and_records_the_drawn_one(monkeypatch):
    """K2 with a drawn group re-solved as one unit (``drawn_group``): the sofa (fitted 12 % deeper, back on the west
    wall) is placed anew with the box the builder makes (``Spot.record``) and recorded at its drawn size with its
    back on the wall (its asset kept: not resized); the drawn coffee table takes the coffee place as far from the
    fitted front as it stands from the front of the same sofa without the fit, so 0.108 m further into the room.
    The sizes are held at the drawn one (``_resolve_sizes``) so the two runs differ only by the fit."""
    monkeypatch.setattr(SV, "_resolve_sizes", lambda drawn, template, area: [tuple(P.drawn_piece(drawn).size)])
    fitted = _deeper(fp("s1", "sofa", (0.47, 2.5), (2.2, 0.9), 0.0))
    coffee = fp("c1", "table_coffee", (1.57, 2.5), (1.0, 0.6), 180.0)       # 0.35 m off the drawn front (x 0.92)
    plan = SV._planned_of(fitted)
    assert plan[0] == (2.2, 0.9) and plan[1] == (2.2, 1.008) and plan[2] == pytest.approx((0.0, -0.054))
    assert SV._planned_of(dict(fitted, asset=None)) is None
    runs = {}
    for tag, sofa in (("plain", dict(fitted, asset=None)), ("fitted", fitted)):
        b = M.building(w=4.5, h=5.0, room_type="living", window=(2.25, 1.2), furniture=[sofa, copy.deepcopy(coffee)])
        (g,) = GR.drawn_groups(b, ROOM)
        assert g["anchor_id"] == "s1" and g["members"] == ["c1"]
        best = SV.solve_room(b, ROOM, k=1, drawn_group="s1")[0]
        assert not best["hard_failures"] and sorted(best["resolved"]) == ["c1", "s1"]
        assert not SV.verify(b, ROOM, best["pieces"])[0]
        s = next(p for p in best["pieces"] if p["id"] == "s1")
        c = next(p for p in best["pieces"] if p["id"] == "c1")
        assert s["footprint"]["size"] == [2.2, 0.9] and s["asset"] == sofa["asset"]       # the drawn record
        assert P.drawn_piece(s).polygon().bounds[0] == pytest.approx(0.02, abs=0.005)      # its back on the wall
        for p in (s, c):
            if p.get("adjusted_by_ai"):
                assert p["adjusted_by_ai"]["moved_m"] <= GR.GROUP_MEMBER_MOVE_MAX_M
        built, table = P.planned_piece(s).polygon(), P.planned_piece(c).polygon()
        assert table.intersection(built).area < P.AREA_EPS
        runs[tag] = (built, table, c)
    built, table, c = runs["fitted"]
    assert built.bounds[0] == pytest.approx(0.02, abs=0.005) and built.bounds[2] - built.bounds[0] == pytest.approx(1.008)
    plain_gap = runs["plain"][1].distance(runs["plain"][0])
    assert plain_gap >= GR.rule("coffee_gap")["min"] - 1e-6
    assert table.distance(built) == pytest.approx(plain_gap, abs=0.06)                    # from the fitted front
    dx = c["footprint"]["center"][0] - runs["plain"][2]["footprint"]["center"][0]
    assert dx == pytest.approx(0.108, abs=0.06)


def test_the_group_checks_of_verify_measure_the_fitted_boxes():
    """K2: a drawn coffee table 0.35 m off a drawn sofa front passes G2 on the drawn boxes, but the sofa's model is
    0.108 m deeper at the front, so on the boxes the builder makes the gap is 0.24 m (< coffee_gap min 0.30): the
    solver's ``verify`` measures that (``placer.planned_building``); a candidate that brings a coffee table to such
    a gap from a fitted sofa fails, while the drawn pair alone is the room's own finding (not the candidate's)."""
    sofa = _deeper(fp("s1", "sofa", (0.47, 2.5), (2.2, 0.9), 0.0))
    coffee = fp("c1", "table_coffee", (1.57, 2.5), (1.0, 0.6), 180.0)
    b = M.building(w=4.5, h=5.0, room_type="living", window=(2.25, 1.2), furniture=[sofa, coffee])
    drawn = [v for v in GC.check_room(b, ROOM) if v["check"] == "G2"]
    planned = [v for v in GC.check_room(P.planned_building(b, ROOM), ROOM) if v["check"] == "G2"]
    assert not drawn and len(planned) == 1 and planned[0]["target"] == "c1" and "0.24 m" in planned[0]["message"]
    only_sofa = M.building(w=4.5, h=5.0, room_type="living", window=(2.25, 1.2), furniture=[sofa])
    new = dict(coffee, id="f_L0_009", source="added_by_ai")
    hard, _v = SV.verify(only_sofa, ROOM, [new])
    assert any(h.startswith("G2 f_L0_009") for h in hard)
    plain = M.building(w=4.5, h=5.0, room_type="living", window=(2.25, 1.2), furniture=[dict(sofa, asset=None)])
    assert not [h for h in SV.verify(plain, ROOM, [new])[0] if h.startswith("G2")]
    assert not [h for h in SV.verify(b, ROOM, [])[0] if h.startswith("G2")]          # the drawn pair: not new


def test_a_vanity_drawn_without_its_axis_line_is_typed_washbasin_by_its_bath_set():
    """Fix round after P4b (17 Oct 2026; pod P4b, real03, agent lens, refuted in part; a pin, no code change here):
    real03 draws six bathroom vanities (sym_L0_005/006/055-058) with a straight axis line through the drain that
    sticks out of the counter outline on both sides; the reading's footprint kept the line (0.85 x 0.80 m, outside
    the washbasin range), so code typing could not give the bath set its missing washbasin and the six stayed untyped.
    Once the ingest leaves the axis line out (the I_ingest ask: ``symbols.trim_axis_lines``) the true 0.80 x 0.50 m
    outline is the bath set's missing washbasin by the group-member rule, with no AI question."""
    bath = M.building(w=2.7, h=1.9, room_type="bathroom", window=None, door_x=0.6)
    toilet = fp("to", "toilet", (2.3, 1.55), (0.4, 0.7), 270.0)
    tub = fp("tb", "bathtub", (2.3, 0.4), (1.7, 0.75), 90.0)
    vanity = unknown("u1", (1.2, 1.65), (0.8, 0.5))                                  # back on the north wall
    bath["furniture"] = [toilet, tub, vanity]
    got = INF.type_by_code(bath, vanity)
    assert got and (got["type"], got["method"]) == ("washbasin", "group_member")
    assert "washbasin" in got["reason"] and got["confidence"] == INF.CONF_GROUP
    # the footprint with the axis line (P4b: 0.85 x 0.80 m) fits no washbasin: code leaves it to the reading
    inflated = unknown("u2", (1.2, 1.5), (0.85, 0.8))
    bath["furniture"] = [toilet, tub, inflated]
    got = INF.type_by_code(bath, inflated)
    assert got is None or got["type"] != "washbasin"
