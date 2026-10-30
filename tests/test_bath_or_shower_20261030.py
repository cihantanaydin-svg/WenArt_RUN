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
