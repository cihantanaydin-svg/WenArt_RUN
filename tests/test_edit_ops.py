"""Validated agent edits (docs/milestone11.md §3.2, §5, §10 "edit validators"; wenart/furniture/edit_ops.py): the
schemas, one passing and one failing case per edit type, the drawn-piece rules of CLAUDE.md, the labels, purity, and
the M10 locked check accepting the agent's validated changes (wenart/furniture/locked.py)."""
import copy
import json

import jsonschema
import pytest

import _m11_room as M
from wenart.furniture import edit_ops as E
from wenart.furniture import locked as LK
from wenart.furniture import plausibility as PL

META = {"reason": "test", "round": 1, "log_seq": 7, "model": "mock"}


def edit(op, **args):
    return dict({"op": op}, **META, **args)


def bedroom(*extra):
    """A bedroom with a reversed drawn bed (headboard in the room), a drawn wardrobe and a drawn washbasin."""
    return M.building(furniture=[
        M.fp("f_L0_001", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=270.0, front=180.0),
        M.fp("f_L0_002", "wardrobe", (3.5, 3.68), (1.8, 0.6), rotation=0.0, front=270.0),
        *extra])


def test_schemas_are_strict_json_schemas_with_a_reason():
    assert set(E.EDIT_SCHEMAS) == set(E.EDIT_OPS)
    for op, schema in E.EDIT_SCHEMAS.items():
        jsonschema.Draft202012Validator.check_schema(schema)
        assert schema["additionalProperties"] is False and "reason" in schema["required"], op
        assert {"reason", "round", "log_seq", "model"} <= set(schema["properties"]), op
    res = E.apply_edit(bedroom(), {"op": "move_piece", "piece_id": "f_L0_002", "reason": "x", "colour": "red"})
    assert not res["accepted"] and res["failed_checks"][0].startswith("schema:")
    res = E.apply_edit(bedroom(), {"op": "move", "piece_id": "f_L0_002", "center": [1, 1], "snap_wall_id": "w_n",
                                   "reason": "both"})
    assert not res["accepted"]
    assert not E.apply_edit(bedroom(), {"op": "teleport", "reason": "x"})["accepted"]


def test_rotate_a_reversed_drawn_bed_is_accepted_and_labelled():
    b = bedroom()
    before = json.dumps(b, sort_keys=True)
    res = E.apply_edit(b, edit("rotate_piece", piece_id="f_L0_001", front_deg=0))
    assert json.dumps(b, sort_keys=True) == before                      # pure
    assert res["accepted"] and res["rerun_from"] == "refit" and res["changed_ids"] == ["f_L0_001"]
    assert res["penalty_after"] < res["penalty_before"] and res["score_after"] > res["score_before"]
    bed = next(f for f in res["building"]["furniture"] if f["id"] == "f_L0_001")
    assert bed["front_deg"] == 0.0 and bed["footprint"]["rotation_deg"] == 90.0
    assert bed["drawn_front_deg"] == 180.0 and bed["drawn_type"] == "bed_double"
    assert bed["drawn_footprint"]["rotation_deg"] == 270.0
    adj = bed["adjusted_by_ai"]
    assert adj["reason"] == "test" and adj["round"] == 1 and adj["log_seq"] == 7 and adj["model"] == "mock"
    assert adj["changed"]["front_deg"] == 180.0
    # The M10 guard after refit accepts the agent's validated change.
    assert LK.check(b, res["building"], "complete") == []


def test_an_edit_that_lowers_the_score_is_rejected():
    good = E.apply_edit(bedroom(), edit("rotate", piece_id="f_L0_001", front_deg=0))["building"]
    res = E.apply_edit(good, edit("rotate", piece_id="f_L0_001", front_deg=180))
    assert not res["accepted"] and any(c.startswith("score:") for c in res["failed_checks"])
    assert res["building"] is None


def test_move_into_a_wall_or_onto_the_door_is_rejected():
    chair = M.fp("f_L0_003", "chair", (2.5, 2.0), (0.45, 0.45), front=270.0, source="added_by_ai")
    b = bedroom(chair)
    wall = E.apply_edit(b, edit("move", piece_id="f_L0_003", center=[4.9, 2.0]))
    assert not wall["accepted"] and "f_L0_003: inside_room" in wall["failed_checks"]
    door = E.apply_edit(b, edit("move", piece_id="f_L0_003", center=[1.0, 0.3]))
    assert not door["accepted"] and "f_L0_003: doors_free" in door["failed_checks"]


def test_drawn_furniture_snaps_at_most_0_3_m_and_fixed_equipment_never_moves():
    shifted = M.fp("f_L0_002", "wardrobe", (4.0, 3.48), (1.8, 0.6), rotation=0.0, front=270.0)    # 0.2 m off
    b = M.building(furniture=[shifted])
    res = E.apply_edit(b, edit("move", piece_id="f_L0_002", snap_wall_id="w_n"))
    assert res["accepted"], res["failed_checks"]
    moved = res["building"]["furniture"][0]
    assert moved["footprint"]["center"][1] == pytest.approx(3.679, abs=1e-3)
    assert moved["drawn_footprint"]["center"] == [4.0, 3.48]
    assert LK.check(b, res["building"], "complete") == []
    far = E.apply_edit(b, edit("move", piece_id="f_L0_002", center=[4.0, 2.5]))
    assert not far["accepted"] and far["failed_checks"][0].startswith("drawn_lock")
    basin = M.fp("f_L0_009", "washbasin", (2.5, 3.78), (0.6, 0.45), front=270.0)
    res = E.apply_edit(M.building(room_type="bathroom", furniture=[basin]),
                       edit("move", piece_id="f_L0_009", center=[2.4, 3.78]))
    assert not res["accepted"] and "fixed equipment" in res["message"]


def test_fixed_equipment_turns_only_for_a_clear_error():
    wrong = M.fp("f_L0_009", "washbasin", (2.5, 3.78), (0.6, 0.45), rotation=180.0, front=90.0)   # faces the wall
    res = E.apply_edit(M.building(room_type="bathroom", furniture=[wrong]),
                       edit("rotate", piece_id="f_L0_009", front_deg=270))
    assert res["accepted"], res["failed_checks"]
    right = res["building"]
    again = E.apply_edit(right, edit("rotate", piece_id="f_L0_009", front_deg=0))
    assert not again["accepted"] and "clear error" in again["message"]
    # The locked check: fixed equipment changed only its orientation, with the reason.
    assert LK.check(M.building(room_type="bathroom", furniture=[wrong]), right, "complete") == []


def test_resize_to_a_product_size_only():
    b = bedroom()
    bad = E.apply_edit(b, edit("resize", piece_id="f_L0_002", size=[3.6, 0.6]))
    assert not bad["accepted"] and "product_size" in bad["failed_checks"][0]
    ok = E.apply_edit(b, edit("resize", piece_id="f_L0_002", size=[1.2, 0.6]))
    assert ok["accepted"], ok["failed_checks"]
    w = next(f for f in ok["building"]["furniture"] if f["id"] == "f_L0_002")
    assert w["footprint"]["size"] == [1.2, 0.6] and w["footprint"]["center"][1] == pytest.approx(3.68, abs=1e-3)


def test_change_type_of_an_unknown_piece_is_inferred_and_room_rules_hold():
    box = M.fp("f_L0_005", "unknown", (4.7, 1.5), (0.4, 0.5), front=None, status="unverified")
    b = bedroom(box)
    res = E.apply_edit(b, edit("change_type", piece_id="f_L0_005", type="nightstand"))
    assert res["accepted"], res["failed_checks"]
    piece = next(f for f in res["building"]["furniture"] if f["id"] == "f_L0_005")
    assert piece["type"] == "nightstand" and piece["inferred"] is True and piece["drawn_type"] == "unknown"
    assert piece["evidence"][-1]["method"] == "inferred" and piece["status"] == "unverified"
    bad = E.apply_edit(b, edit("change_type", piece_id="f_L0_005", type="toilet"))
    assert not bad["accepted"] and bad["failed_checks"][0].startswith("room_type")
    second = E.apply_edit(b, edit("change_type", piece_id="f_L0_002", type="bed_single"))
    assert not second["accepted"]


def test_swap_model_checks_the_catalogue():
    class Cat:
        def entry(self, asset_id):
            return {"wardrobe_01": {"id": "wardrobe_01", "type": "wardrobe"},
                    "sofa_01": {"id": "sofa_01", "type": "sofa"}}.get(asset_id)

    b = bedroom()
    res = E.apply_edit(b, edit("swap_model", piece_id="f_L0_002", asset_id="wardrobe_01"), catalog=Cat())
    assert res["accepted"] and res["building"]["furniture"][1]["asset_pin"] == "wardrobe_01"
    assert not E.apply_edit(b, edit("swap_model", piece_id="f_L0_002", asset_id="sofa_01"), catalog=Cat())["accepted"]
    assert not E.apply_edit(b, edit("swap_model", piece_id="f_L0_002", asset_id="nope"), catalog=Cat())["accepted"]


def test_add_piece_and_group_never_a_second_anchor():
    b = E.apply_edit(bedroom(), edit("rotate", piece_id="f_L0_001", front_deg=0))["building"]
    res = E.apply_edit(b, edit("add", room_id=M.ROOM_ID, type="nightstand"))
    assert res["accepted"], res["failed_checks"]
    new = res["building"]["furniture"][-1]
    assert new["source"] == "added_by_ai" and new["type"] == "nightstand" and new["id"] == "f_L0_003"
    assert not E.apply_edit(b, edit("add", room_id=M.ROOM_ID, type="bed_single"))["accepted"]
    assert not E.apply_edit(b, edit("add_group", room_id=M.ROOM_ID, group="bed_set"))["accepted"]
    desk = E.apply_edit(b, edit("add_group", room_id=M.ROOM_ID, group="desk_set"))
    assert desk["accepted"] and len(desk["changed_ids"]) == 2


def test_remove_added_piece_and_drawn_piece_rules():
    chair = M.fp("f_L0_003", "chair", (4.5, 1.0), (0.45, 0.45), front=270.0, source="added_by_ai")
    b = bedroom(chair)
    b["decor"] = [{"id": "dec_L0_001", "kind": "decor", "type": "cushion", "level_id": "L0", "room_id": M.ROOM_ID,
                   "center": [4.5, 1.0], "size": [0.4, 0.15], "source": "added_by_ai", "host_id": "f_L0_003"}]
    res = E.apply_edit(b, edit("remove_piece", piece_id="f_L0_003"))
    assert res["accepted"] and not [f for f in res["building"]["furniture"] if f["id"] == "f_L0_003"]
    assert res["building"]["decor"] == []
    drawn = E.apply_edit(b, edit("remove", piece_id="f_L0_002"))
    assert drawn["accepted"]
    w = next(f for f in drawn["building"]["furniture"] if f["id"] == "f_L0_002")
    assert w["build"] is False and w["adjusted_by_ai"]["changed"] == {"build": None}
    basin = M.fp("f_L0_009", "washbasin", (2.5, 3.78), (0.6, 0.45), front=270.0)
    res = E.apply_edit(M.building(room_type="bathroom", furniture=[basin]), edit("remove", piece_id="f_L0_009"))
    assert not res["accepted"]


def test_kept_rooms_change_only_orientation_and_clear_errors():
    b = bedroom()
    b["project"]["brief"] = {"furnished_rooms": "keep"}
    assert not E.apply_edit(b, edit("move", piece_id="f_L0_002", center=[3.4, 3.68]))["accepted"]
    res = E.apply_edit(b, edit("rotate", piece_id="f_L0_001", front_deg=0))
    assert res["accepted"]
    assert LK.check(b, res["building"], "keep") == []


def test_relayout_and_set_room_type_rerun_the_layout():
    chair = M.fp("f_L0_003", "chair", (2.6, 2.0), (0.45, 0.45), front=270.0, source="added_by_ai")
    b = E.apply_edit(bedroom(chair), edit("rotate", piece_id="f_L0_001", front_deg=0))["building"]
    res = E.apply_edit(b, edit("relayout_room", room_id=M.ROOM_ID))
    assert res["rerun_from"] == "layout"
    bath = E.apply_edit(b, edit("set_room_type", room_id=M.ROOM_ID, room_type="bathroom"))
    assert not bath["accepted"] and bath["failed_checks"][0].startswith("R1")
    other = E.apply_edit(b, edit("set_room_type", room_id=M.ROOM_ID, room_type="other"))
    assert other["rerun_from"] == "layout"
    if other["accepted"]:
        room = other["building"]["rooms"][0]
        assert room["room_type"] == "other" and room["adjusted_by_ai"]["changed"] == {"room_type": "bedroom"}


def test_locked_check_refuses_an_unlabelled_or_out_of_rule_change():
    b = M.building(room_type="bathroom", furniture=[
        M.fp("f_L0_009", "washbasin", (2.5, 3.78), (0.6, 0.45), front=270.0)])
    moved = copy.deepcopy(b)
    moved["furniture"][0]["footprint"]["center"] = [2.0, 3.78]
    moved["furniture"][0]["adjusted_by_ai"] = {"reason": "x", "changed": {}}
    moved["furniture"][0]["drawn_footprint"] = copy.deepcopy(b["furniture"][0]["footprint"])
    assert any("fixed equipment moved" in v for v in LK.check(b, moved, "complete"))


def test_the_refit_locked_check_accepts_every_validated_edit_of_drawn_pieces():
    """Lead note (M11): the refit guard compares drawn pieces with adjusted_by_ai against the CLAUDE.md
    allowances (snap <= 0.3 m, turn, product resize, retype of an unknown), not against the drawn place."""
    source = M.building(furniture=[
        M.fp("f_L0_001", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=270.0, front=180.0),
        M.fp("f_L0_002", "wardrobe", (4.0, 3.48), (1.8, 0.6), rotation=0.0, front=270.0),
        M.fp("f_L0_005", "unknown", (4.7, 1.5), (0.4, 0.5), front=None, status="unverified")])
    b = source
    for e in (edit("rotate_piece", piece_id="f_L0_001", front_deg=0),
              edit("move_piece", piece_id="f_L0_002", snap_wall_id="w_n"),
              edit("resize_piece", piece_id="f_L0_002", size=[1.2, 0.6]),
              edit("change_type", piece_id="f_L0_005", type="nightstand")):
        res = E.apply_edit(b, e)
        assert res["accepted"], (e["op"], res["failed_checks"])
        assert {"rerun_from", "changed_ids", "building"} <= set(res)
        assert res["rerun_from"] == "refit" and res["changed_ids"]
        b = res["building"]
        assert LK.check(source, b, "complete") == [], e["op"]
    by_id = {f["id"]: f for f in b["furniture"]}
    assert all(by_id[i].get("adjusted_by_ai") for i in ("f_L0_001", "f_L0_002", "f_L0_005"))
    # A move beyond the snap distance that did not pass apply_edit is still refused by the guard.
    far = copy.deepcopy(b)
    next(f for f in far["furniture"] if f["id"] == "f_L0_002")["footprint"]["center"] = [3.0, 2.0]
    assert any("moved" in v for v in LK.check(source, far, "complete"))


def test_refit_accepts_a_validated_move_of_a_documented_only_piece():
    """Pod G2 (real02): the agent moved a drawn floor lamp 0.3 m away from a window (edit_ops accepted it), and the
    refit's locked check refused it as "fixed equipment" (it used UNCHANGEABLE_TYPES), rolling the round back."""
    import copy
    from wenart.furniture import locked, schemas

    assert "floor_lamp" in schemas.UNCHANGEABLE_TYPES and "floor_lamp" not in schemas.FIXED_TYPES
    src = {"id": "f1", "type": "floor_lamp", "source": "from_documents", "level_id": "L0", "room_id": "r1",
           "footprint": {"center": [1.28, 0.70], "size": [0.6, 0.6], "rotation_deg": 180.0}, "front_deg": 90.0}
    fin = copy.deepcopy(src)
    fin["footprint"]["center"] = [1.28, 0.99]
    fin["drawn_footprint"] = copy.deepcopy(src["footprint"])
    fin["adjusted_by_ai"] = {"reason": "away from the window", "round": 1, "log_seq": 1, "model": "m",
                             "changed": {"footprint": src["footprint"]}}
    assert locked._agent_problems(src, fin, keep=False) == []
    retyped = dict(fin, type="side_table", drawn_type="floor_lamp")
    assert any("changed its type" in p for p in locked._agent_problems(src, retyped, keep=False))
    far = copy.deepcopy(fin)
    far["footprint"]["center"] = [1.28, 1.40]
    assert any("moved" in p for p in locked._agent_problems(src, far, keep=False))
    stove = dict(copy.deepcopy(fin), type="stove")
    stove_src = dict(src, type="stove")
    assert any("fixed equipment moved" in p for p in locked._agent_problems(stove_src, stove, keep=False))


def test_refit_accepts_a_reasoned_room_type_change():
    """Pod G2b (real02): the agent retyped a 40 m² lounge from other to living (set_room_type, with a reason); the
    locked check wanted every room byte-equal and the round was rolled back. A reasoned type change passes; any other
    room change (or one without a reason) still fails."""
    import copy
    from wenart.furniture import locked

    room = {"id": "r1", "level_id": "L1", "room_type": "other", "polygon": [[0, 0], [5, 0], [5, 8], [0, 8]]}
    src = {"walls": [], "openings": [], "rooms": [room], "furniture": []}
    fin = copy.deepcopy(src)
    fin["rooms"][0].update(room_type="living", adjusted_by_ai={"reason": "two sofas and a coffee table", "round": 2,
                                                               "changed": {"room_type": "other"}})
    assert locked._block_problems(src, fin) == []
    no_reason = copy.deepcopy(fin)
    no_reason["rooms"][0]["adjusted_by_ai"]["reason"] = ""
    assert locked._block_problems(src, no_reason)
    moved = copy.deepcopy(fin)
    moved["rooms"][0]["polygon"][0] = [0.1, 0]
    assert locked._block_problems(src, moved)


def test_a_wall_snap_may_move_a_drawn_piece_up_to_1_2_m():
    """Pod G2b (real02): 45 of 99 agent edits were refused by the 0.3 m drawn-piece limit, among them wall snaps of
    sofas 0.8-1.1 m off the wall. CLAUDE.md lets the AI snap drawn furniture to a wall: a snap may move it up to
    WALL_SNAP_MAX_M; a free move stays within 0.3 m; the refit's locked check agrees."""
    import copy
    from wenart.furniture import locked, schemas

    assert schemas.WALL_SNAP_MAX_M == 1.2
    src = {"id": "f1", "type": "sofa", "source": "from_documents", "level_id": "L0", "room_id": "r1",
           "footprint": {"center": [2.0, 1.5], "size": [2.0, 0.9], "rotation_deg": 0.0}, "front_deg": 270.0}
    fin = copy.deepcopy(src)
    fin["footprint"]["center"] = [2.0, 0.45]                                   # 1.05 m onto the wall
    fin["drawn_footprint"] = copy.deepcopy(src["footprint"])
    fin["adjusted_by_ai"] = {"reason": "back onto the wall", "changed": {"footprint": src["footprint"]},
                             "snapped_wall": "w1"}
    assert locked._agent_problems(src, fin, keep=False) == []
    free = copy.deepcopy(fin)
    del free["adjusted_by_ai"]["snapped_wall"]
    assert any("moved 1.050 m" in p for p in locked._agent_problems(src, free, keep=False))
