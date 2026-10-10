"""The group checks G1-G14 (docs/milestone12.md §4.5, §4.6; wenart/furniture/group_checks.py): per check one room
that passes and one with a planted error, the numbers in the messages, the use zones and the walkway raster."""
import copy

import _m11_room as M
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import placer as P

W, H = 4.5, 5.0


def fp(pid, ftype, center, size, front, **kw):
    """A piece facing ``front`` (degrees) with its footprint in that frame."""
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def found(b, check=None):
    return [(v["check"], v["severity"], v["target"]) for v in GC.check_room(b, M.ROOM_ID)
            if check is None or v["check"] == check]


def message(b, check):
    return next(v["message"] for v in GC.check_room(b, M.ROOM_ID) if v["check"] == check)


def living(*pieces):
    return M.building(w=W, h=H, room_type="living", window=(2.25, 1.2), furniture=list(pieces))


SOFA = fp("s1", "sofa", (0.47, 2.5), (2.2, 0.9), 0.0)                    # back on the west wall, facing east
TV = fp("tv", "tv_unit", (W - 0.245, 2.5), (1.6, 0.45), 180.0)           # on the east wall, facing the sofa
COFFEE = M.fp("c1", "table_coffee", (1.52, 2.5), (1.0, 0.6), rotation=90.0, front=None)
BED = fp("b1", "bed_double", (1.02, 2.5), (1.6, 2.0), 0.0)
NS1, NS2 = fp("n1", "nightstand", (0.22, 1.47), (0.4, 0.4), 0.0), fp("n2", "nightstand", (0.22, 3.53), (0.4, 0.4), 0.0)


def test_the_check_list_and_the_rules_have_sources():
    assert GC.CHECKS == tuple(f"G{k}" for k in range(1, 15)) and set(GC.WHAT) == set(GC.CHECKS)
    cfg = GR.config()
    for name, rule in cfg["rules"].items():
        assert rule["source"] and set(rule["source"]) <= set(cfg["sources"]), name
    assert GR.rule_min("walkway") == 0.60 and GR.rule_min("walkway_main") == 0.80
    assert GR.rule_min("diner_pullout") == 0.81 and GR.rule_min("fixture_front") == 0.53


def test_g1_tv_opposite_the_sofa():
    assert found(living(SOFA, TV, COFFEE)) == []
    off = living(SOFA, fp("tv", "tv_unit", (W - 0.245, 4.0), (1.6, 0.45), 180.0), COFFEE)
    assert found(off) == [("G1", "major", "tv")] and "1.50 m off the sofa axis, needs ≤ 0.30 m" in message(off, "G1")
    away = living(SOFA, fp("tv", "tv_unit", (2.5, 2.5), (1.6, 0.45), 0.0), COFFEE)
    msg = message(away, "G1")
    assert "180° off the line to the sofa, needs ≤ 10°" in msg and "1.35 m from the sofa front, needs ≥ 1.50 m" in msg


def test_g2_coffee_table_off_the_sofa_front():
    near = living(SOFA, TV, M.fp("c1", "table_coffee", (1.07, 2.5), (1.0, 0.6), rotation=90.0, front=None))
    assert found(near) == [("G2", "major", "c1")] and "0.00 m from the sofa front, needs ≥ 0.30 m" in message(near, "G2")


def test_g3_armchairs_face_the_group():
    assert found(living(SOFA, TV, COFFEE, fp("a1", "armchair", (1.52, 3.85), (0.8, 0.8), 270.0))) == []
    away = living(SOFA, TV, COFFEE, fp("a1", "armchair", (1.52, 3.85), (0.8, 0.8), 90.0))
    assert found(away) == [("G3", "major", "a1")] and "113° off the sofa s1 (needs ≤ 30°)" in message(away, "G3")


def test_g4_g5_bed_nightstands_and_clearances():
    assert found(M.building(w=W, h=H, furniture=[BED, NS1, NS2])) == []
    single = M.building(w=W, h=H, furniture=[BED, NS1])
    assert found(single) == [("G4", "minor", "b1")] and "free right side" in message(single, "G4") or \
        "free left side" in message(single, "G4")
    far = M.building(w=W, h=H, furniture=[BED, NS1, fp("n2", "nightstand", (0.22, 4.0), (0.4, 0.4), 0.0)])
    assert ("G4", "major", "n2") in found(far)
    n2 = next(v["message"] for v in GC.check_room(far, M.ROOM_ID) if v["target"] == "n2")
    assert "0.50 m from the bed side (needs ≤ 0.30 m)" in n2
    off = M.building(w=W, h=H, furniture=[fp("b1", "bed_double", (1.6, 2.5), (1.6, 2.0), 0.0)])
    assert ("G5", "critical", "b1") in found(off) and "0.60 m off the wall" in message(off, "G5")
    tight = M.building(w=3.0, h=4.0, door_x=0.6, furniture=[fp("b1", "bed_double", (1.5, 2.98), (1.6, 2.0), 270.0),
                                                             fp("w1", "wardrobe", (1.5, 1.2), (2.9, 0.6), 270.0)])
    assert ("G5", "major", "b1") in found(tight) and "0.48 m free at the foot, needs ≥ 0.60 m" in message(tight, "G5")


def dining(h=H, chairs=None, table_y=2.5):
    table = M.fp("t1", "table_dining", (2.25, table_y), (1.6, 0.9), rotation=0.0, front=None)
    seats = chairs if chairs is not None else [
        (1.85, table_y - 0.75, 90.0), (2.65, table_y - 0.75, 90.0), (1.85, table_y + 0.75, 270.0),
        (2.65, table_y + 0.75, 270.0)]
    return M.building(w=W, h=h, room_type="dining", window=(2.25, 1.2), furniture=[table] + [
        fp(f"c{i}", "chair", (x, y), (0.45, 0.45), f) for i, (x, y, f) in enumerate(seats)])


def test_g6_dining_chairs_count_facing_and_pull_out():
    good = dining()
    assert found(good) == [("G6", "minor", "t1")] and "has 4 of 6 chairs" in message(good, "G6")
    away = dining(chairs=[(1.85, 1.75, 270.0), (2.65, 1.75, 90.0), (1.85, 3.25, 270.0), (2.65, 3.25, 270.0)])
    assert ("G6", "major", "c0") in found(away) and "180° off the table t1 (needs ≤ 45°)" in str(GC.check_room(away, M.ROOM_ID))
    wall = dining(table_y=1.15)                                        # the table edge 0.70 m from the south wall
    pulls = [v for v in GC.check_room(wall, M.ROOM_ID) if v["check"] == "G6" and "pullout_m" in v["metrics"]]
    assert {v["target"] for v in pulls} == {"c0", "c1"} and "0.70 m from the table edge" in pulls[0]["message"]
    bare = dining(chairs=[])
    assert found(bare, "G6") == [("G6", "major", "t1")] and "has no chairs (needs 6)" in message(bare, "G6")


def test_g7_desk_chair_and_room_behind():
    desk = fp("d1", "desk", (3.5, 4.68), (1.2, 0.6), 270.0)
    chair = fp("oc", "office_chair", (3.5, 4.03), (0.6, 0.6), 90.0)
    assert found(M.building(w=W, h=H, furniture=[desk, chair]), "G7") == []
    alone = M.building(w=W, h=H, furniture=[desk])
    assert found(alone, "G7") == [("G7", "minor", "d1")] and message(alone, "G7") == "desk d1 has no chair"
    blocked = M.building(w=W, h=H, furniture=[desk, chair, fp("dr", "dresser", (3.5, 3.4), (1.2, 0.5), 90.0)])
    assert ("G7", "major", "d1") in found(blocked) and "needs ≥ 0.80 m" in message(blocked, "G7")


def kitchen(*extra, run=None):
    pieces = run if run is not None else [
        fp("k1", "kitchen_counter", (2.3, 4.68), (3.0, 0.6), 270.0), fp("fr", "fridge", (0.45, 4.63), (0.7, 0.7), 270.0),
        fp("sk", "sink_kitchen", (1.7, 4.68), (0.8, 0.6), 270.0), fp("st", "stove", (3.0, 4.68), (0.6, 0.6), 270.0)]
    return M.building(w=W, h=H, room_type="kitchen", window=(1.7, 1.0), sill=1.0, furniture=pieces + list(extra))


def test_g8_g9_kitchen_order_landings_triangle_aisle():
    good = kitchen()
    assert found(good) == []
    bad_order = kitchen(run=[fp("k1", "kitchen_counter", (1.5, 4.68), (3.0, 0.6), 270.0),
                             fp("sk", "sink_kitchen", (1.5, 4.68), (0.8, 0.6), 270.0),
                             fp("st", "stove", (2.6, 4.68), (0.6, 0.6), 270.0),
                             fp("fr", "fridge", (3.4, 4.63), (0.7, 0.7), 270.0)])
    msgs = [v["message"] for v in GC.check_room(bad_order, M.ROOM_ID) if v["check"] == "G8"]
    assert "the sink is not between the fridge and the hob along the run" in msgs
    assert any(m.startswith("work triangle: sink-hob 1.10 m, hob-fridge 0.81 m") for m in msgs)
    aisle = kitchen(M.fp("t1", "table_dining", (1.5, 3.6), (1.2, 0.8), rotation=0.0, front=None))
    assert any("kitchen aisle 0.38 m in front of kitchen_counter k1, needs ≥ 0.90 m" in v["message"]
               for v in GC.check_room(aisle, M.ROOM_ID))
    no_hob = kitchen(run=[fp("k1", "kitchen_counter", (2.3, 4.68), (3.0, 0.6), 270.0),
                          fp("sk", "sink_kitchen", (1.7, 4.68), (0.8, 0.6), 270.0)])
    assert {(c, t) for c, _s, t in found(no_hob, "G9")} == {("G9", M.ROOM_ID)}
    assert {v["message"] for v in GC.check_room(no_hob, M.ROOM_ID) if v["check"] == "G9"} == {
        f"kitchen {M.ROOM_ID} has no hob (stove)", f"kitchen {M.ROOM_ID} has no fridge (fridge)"}


def test_g8_fridge_landing_across():
    """NKBA: a fridge landing may be a counter or island at most 1.22 m across from it (fails before Milestone 12's
    last G8 change: only a counter beside the fridge on its run counted)."""
    run = [fp("k1", "kitchen_counter", (2.6, 4.68), (2.4, 0.6), 270.0), fp("sk", "sink_kitchen", (2.0, 4.68), (0.8, 0.6),
                                                                          270.0),
           fp("st", "stove", (3.4, 4.68), (0.6, 0.6), 270.0), fp("fr", "fridge", (0.37, 3.0), (0.7, 0.7), 0.0)]
    alone = kitchen(run=list(run))
    assert any(v["message"].startswith("fridge fr: 0.00 m of counter beside it, needs ≥ 0.38 m") for v in
               GC.check_room(alone, M.ROOM_ID))
    across = kitchen(fp("is", "kitchen_island", (2.07, 3.0), (1.2, 0.8), 180.0), run=list(run))
    assert not [v for v in GC.check_room(across, M.ROOM_ID) if v["message"].startswith("fridge fr")]
    assert GC.fridge_landing_elsewhere(GC.RoomView(across, across["rooms"][0]), "fr") == "across"


BATH = [fp("to", "toilet", (3.8, 4.63), (0.4, 0.7), 270.0), fp("wb", "washbasin", (2.5, 4.755), (0.6, 0.45), 270.0),
        fp("sh", "shower", (4.03, 0.47), (0.9, 0.9), 90.0)]


def test_g10_bathroom_fixtures_and_clearances():
    assert found(M.building(w=W, h=H, room_type="bathroom", window=None, furniture=BATH)) == []
    no_toilet = M.building(w=W, h=H, room_type="bathroom", window=None, furniture=BATH[1:])
    assert found(no_toilet) == [("G10", "major", M.ROOM_ID)] and message(no_toilet, "G10") == "bathroom without a toilet"
    tight = M.building(w=W, h=H, room_type="bathroom", window=None, furniture=BATH + [
        fp("wm", "washing_machine", (3.8, 3.7), (0.6, 0.6), 90.0)])
    assert ("G10", "major", "to") in found(tight) and "0.28 m clear in front, needs ≥ 0.53 m" in message(tight, "G10")


def test_g11_walkways_reach_doors_and_use_zones():
    b = M.building(w=3.0, h=4.0, door_x=0.6, furniture=[fp("w1", "wardrobe", (1.5, 2.0), (2.9, 0.6), 270.0)])
    b["openings"].append({"id": "d2", "type": "door", "level_id": "L0", "wall_id": "w_n", "center": [1.5, 4.05],
                          "width": 0.9, "swing_side": M.ROOM_ID, "status": "verified", "evidence": []})
    cut = [v for v in GC.check_room(b, M.ROOM_ID) if v["check"] == "G11"]
    assert cut and cut[0]["severity"] == "critical" and "d2" in cut[0]["message"]
    ok = M.building(w=3.0, h=4.0, door_x=0.6, furniture=[fp("w1", "wardrobe", (0.32, 2.0), (1.8, 0.6), 0.0)])
    ok["openings"] = copy.deepcopy(b["openings"])                     # the same two doors, the wardrobe on a side
    assert not found(ok, "G11")
    unreachable = M.building(w=3.0, h=4.0, door_x=0.6, furniture=[
        fp("b1", "bed_double", (1.5, 2.98), (1.6, 2.0), 270.0), fp("w1", "wardrobe", (1.5, 1.2), (2.9, 0.6), 270.0)])
    zones = [v["message"] for v in GC.check_room(unreachable, M.ROOM_ID) if v["check"] == "G11"]
    assert "bed_double b1: its foot use zone is not reached by a 0.60 m walkway from door d1" in zones


def test_g12_g13_window_band_and_storage_fronts():
    window = M.building(w=W, h=H, furniture=[fp("bs", "bookshelf", (2.25, 4.8), (1.0, 0.35), 270.0)])
    assert found(window) == [("G12", "major", "bs")]
    assert message(window, "G12") == "bookshelf bs (1.80 m) stands in front of window win1 (sill 0.90 m + 0.05)"
    low = M.building(w=W, h=H, furniture=[fp("ns", "nightstand", (2.25, 4.78), (0.5, 0.4), 270.0)])
    assert not found(low, "G12")                                           # below the sill
    fronts = M.building(w=W, h=H, window=(1.0, 1.0), furniture=[
        fp("w1", "wardrobe", (3.5, 4.68), (1.8, 0.6), 270.0), fp("dr", "dresser", (3.5, 3.9), (1.2, 0.5), 90.0)])
    assert ("G13", "major", "w1") in found(fronts) and "0.23 m free in front, needs ≥ 0.80 m" in message(fronts, "G13")
    assert not found(M.building(w=W, h=H, window=(1.0, 1.0), furniture=[
        fp("w1", "wardrobe", (3.5, 4.68), (1.8, 0.6), 270.0)]), "G13")


def test_g14_types_the_room_never_holds():
    b = M.building(w=W, h=H, furniture=[fp("to", "toilet", (3.8, 4.63), (0.4, 0.7), 270.0),
                                       fp("sb", "sideboard", (2.0, 0.27), (1.6, 0.45), 90.0)])
    assert sorted(found(b, "G14")) == [("G14", "major", "to"), ("G14", "minor", "sb")]
    zoned = M.building(w=W, h=H, room_type="living", window=(2.25, 1.2), furniture=[
        fp("st", "stove", (3.0, 4.68), (0.6, 0.6), 270.0)])
    assert found(zoned, "G14") == [("G14", "major", "st")]
    zoned["rooms"][0]["zones"] = [{"zone_id": "z1", "kind": "kitchen", "polygon": [[2.0, 3.5], [4.5, 3.5], [4.5, 5.0],
                                                                                  [2.0, 5.0]]}]
    assert not found(zoned, "G14")                                          # a kitchen zone of a living room


def test_unbuilt_pieces_are_not_judged():
    """Track S request: unknown pieces and library gaps (asset.method none) are not built, like build: false."""
    gap = copy.deepcopy(BATH[0])
    gap["asset"] = {"method": "none"}
    b = M.building(w=W, h=H, room_type="bathroom", window=None, furniture=[gap] + BATH[1:])
    assert found(b) == [("G10", "major", M.ROOM_ID)]
    unknown = M.building(w=W, h=H, furniture=[M.fp("u1", "unknown", (2.25, 4.8), (1.0, 0.35), front=270.0)])
    assert not found(unknown)
    assert not GR.piece_is_built({"type": "unknown"}) and GR.piece_is_built({"type": "sofa", "asset": None})
    from wenart.furniture import decor
    samples = [{"type": "sofa"}, {"type": "sofa", "build": False}, {"type": "unknown"}, {"type": "toilet", "asset":
               {"method": "none"}}, {"type": "toilet", "asset": {"method": "catalogue"}}, None, {}]
    assert [GR.piece_is_built(s) for s in samples] == [decor.piece_is_built(s) for s in samples]   # = track S's


def test_use_zones_follow_the_piece_frame():
    bed = P.drawn_piece(BED)
    zones = GC.use_zone_polys(bed, "bed_double")
    names = {name for name, _poly in zones}
    assert {"left", "right", "foot"} <= names
    foot = next(poly for name, poly in zones if name == "foot")
    assert foot.bounds[0] >= bed.polygon().bounds[2] - 1e-6               # in front of the bed (east)
