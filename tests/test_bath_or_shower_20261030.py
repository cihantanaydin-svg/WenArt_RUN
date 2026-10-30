"""UL200 (30 Oct 2026, real04 run 20261030-112241-full): "Not all the bathrooms requires a bath sometimes a shower solution
could be better solution". A bath-sized drawn footprint typed by code keeps its bath only in the main bathrooms (on the
level with the most bedrooms); the others become walk-in showers; a bath the drawing names stays. Pure tests."""
from wenart.furniture import infer as I


def _room(rid, lv, rtype):
    return {"id": rid, "level_id": lv, "room_type": rtype, "polygon": [[0, 0], [3, 0], [3, 2], [0, 2]]}


def _tub(fid, rid, lv, **kw):
    return dict({"id": fid, "type": "bathtub", "room_id": rid, "level_id": lv, "source": "from_documents",
                 "type_method": "group_member", "footprint": {"center": [1.0, 0.5], "size": [1.83, 0.8],
                                                               "rotation_deg": 0.0}, "front_deg": 90.0}, **kw)


def _house():
    rooms = [_room("r_L0_bed_1", "L0", "bedroom"), _room("r_L0_bed_2", "L0", "bedroom"), _room("r_L0_bath", "L0",
             "bathroom"), _room("r_L1_bath", "L1", "bathroom"), _room("r_L1_play", "L1", "living"),
             _room("r_L-1_bath", "L-1", "bathroom")]
    furniture = [_tub("t0", "r_L0_bath", "L0"), _tub("t1", "r_L1_bath", "L1"), _tub("tb", "r_L-1_bath", "L-1")]
    return {"project": {"brief": {}}, "rooms": rooms, "furniture": furniture}


def test_only_the_main_bathroom_keeps_its_bath():
    b = _house()
    reasons = I.bath_or_shower(b)
    by = {f["id"]: f for f in b["furniture"]}
    assert by["t0"]["type"] == "bathtub"
    for fid in ("t1", "tb"):
        f = by[fid]
        assert f["type"] == "shower" and f["shower_kind"] == "walk_in" and f["drawn_type"] == "bathtub"
        assert f["adjusted_by_ai"]["rule"] == I.BATH_OR_SHOWER_RULE and f["drawn_footprint"]["size"] == [1.83, 0.8]
    assert len(reasons) == 2 and all("UL200" in r for r in reasons)


def test_a_named_bath_one_bathroom_and_the_brief_keep_the_baths():
    b = _house()
    b["furniture"][1]["type_raw"] = "KÜVET"                           # the drawing names it a bath
    b["furniture"][2]["type_method"] = "block"
    assert I.bath_or_shower(b) == [] and all(f["type"] == "bathtub" for f in b["furniture"])
    one = _house()
    one["furniture"] = one["furniture"][1:2]
    assert I.bath_or_shower(one) == []                               # the house's only bath stays
    kept = _house()
    kept["project"]["brief"]["bath_or_shower"] = "keep"
    assert I.bath_or_shower(kept) == []


def test_the_locked_check_accepts_the_code_swap_of_an_inferred_bath_only():
    """The replay of real04 run 112241: the layout's locked check refused the six showers ("fixed equipment changed
    its type") and wrote no building; a code swap of an inferred bathing member passes, nothing else does."""
    import copy
    from wenart.furniture import locked as L
    b = _house()
    for f in b["furniture"]:
        f["inferred"] = True
    src = copy.deepcopy(b)
    I.bath_or_shower(b)
    fin = {f["id"]: f for f in b["furniture"]}
    for f in src["furniture"]:
        probs = L._agent_problems(f, fin[f["id"]], False, "bathroom") if fin[f["id"]] != f else []
        assert not [p for p in probs if "changed its type" in p], probs
    named = copy.deepcopy(src["furniture"][1])
    named.pop("inferred")                                            # typed by the drawing: stays a bathtub
    retyped = dict(fin["t1"])
    assert any("changed its type" in p for p in L._agent_problems(named, retyped, False, "bathroom"))
    agent = dict(fin["t1"], adjusted_by_ai={"by": "agent", "model": "m", "reason": "r", "changed": {"type": "bathtub"}})
    assert any("changed its type" in p for p in L._agent_problems(src["furniture"][1], agent, False, "bathroom"))
    toilet = dict(fin["t1"], type="toilet")                         # not the same member
    assert any("changed its type" in p for p in L._agent_problems(src["furniture"][1], toilet, False, "bathroom"))
