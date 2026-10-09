"""Plausibility of rooms and furniture (docs/milestone11.md §4.2, §4.3, §10 "plausibility"; wenart/furniture/
plausibility.py): hand-made rooms with one planted error each, the score formula, purity and speed."""
import copy
import json
import time

import pytest

import _m11_room as M
from wenart.furniture import plausibility as PL
from wenart.furniture import schemas


def checks(building, check=None):
    vs = PL.score_room(building, M.ROOM_ID)["violations"]
    return [v for v in vs if check is None or v["check"] == check]


def bed(front=90.0, center=(0.4 + 1.0, 2.0), pid="b1", **kw):
    """A 1.6 x 2.0 double bed whose headboard is on the west wall (x = 0) when it faces east (90 degrees... front 0)."""
    return M.fp(pid, "bed_double", center, (1.6, 2.0), rotation=(front + 90.0) % 360.0, front=front, **kw)


def test_checks_table_names_every_item_with_a_severity():
    assert set(PL.CHECKS) == {"F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "R1", "R2", "R3", "R4"}
    assert all(c["severity"] in PL.SEVERITIES and c["what"] for c in PL.CHECKS.values())
    assert PL.CHECKS["R4"]["measured"] is False


def test_bed_with_its_headboard_on_a_wall_is_fine_and_in_the_middle_is_critical():
    # Headboard on the west wall: the bed faces east (front 0), its back edge at x = 0.02.
    good = M.building(furniture=[M.fp("b1", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=90.0, front=0.0),
                                 M.fp("n1", "nightstand", (0.22, 0.75), (0.4, 0.4), rotation=90.0, front=0.0),
                                 M.fp("n2", "nightstand", (0.22, 3.25), (0.4, 0.4), rotation=90.0, front=0.0)])
    assert not checks(good, "F3") and not checks(good, "F4")
    assert PL.score_room(good, M.ROOM_ID)["score"] == 100.0
    middle = M.building(furniture=[M.fp("b1", "bed_double", (2.5, 2.0), (1.6, 2.0), rotation=90.0, front=0.0)])
    f3 = checks(middle, "F3")
    assert [(v["target"], v["severity"]) for v in f3] == [("b1", "critical")]
    assert f3[0]["metrics"]["back_wall_m"] > 1.0


def test_a_reversed_bed_faces_the_wall_and_has_its_headboard_in_the_room():
    # real02 U3: headboard in the room, the foot against the wall.
    rev = M.building(furniture=[M.fp("b1", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=270.0, front=180.0)])
    got = {(v["check"], v["severity"]) for v in checks(rev)}
    assert ("F3", "critical") in got and ("F4", "major") in got


def test_a_piece_without_a_front_is_judged_by_the_side_the_builder_faces_it():
    item = M.fp("b1", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=270.0, front=None)
    f3 = checks(M.building(furniture=[item]), "F3")
    assert f3 and f3[0]["metrics"]["front_assumed"] is True


def test_sofa_facing_a_wall_and_sofa_facing_its_tv_unit():
    near_wall = M.building(room_type="living", furniture=[
        M.fp("s1", "sofa", (2.5, 3.4), (2.2, 0.9), rotation=180.0, front=90.0)])        # front 0.15 m from the north wall
    f4 = checks(near_wall, "F4")
    assert f4 and f4[0]["target"] == "s1" and f4[0]["metrics"]["front_wall_m"] < 0.3
    group = M.building(room_type="living", furniture=[
        M.fp("s1", "sofa", (2.5, 0.47), (2.2, 0.9), rotation=180.0, front=90.0),        # back on the south wall
        M.fp("t1", "table_coffee", (2.5, 1.8), (1.0, 0.6), rotation=180.0, front=None),
        M.fp("tv", "tv_unit", (2.5, 3.75), (1.6, 0.45), rotation=0.0, front=270.0)])    # back on the north wall
    assert not checks(group, "F3") and not checks(group, "F4") and not checks(group, "F5")


def test_a_free_standing_sofa_facing_its_group_needs_no_wall():
    free = M.building(room_type="living", w=7.0, h=6.0, furniture=[
        M.fp("s1", "sofa", (3.5, 2.0), (2.2, 0.9), rotation=180.0, front=90.0),
        M.fp("t1", "table_coffee", (3.5, 3.2), (1.0, 0.6), rotation=0.0, front=None)])
    assert not checks(free, "F3")
    alone = M.building(room_type="living", w=7.0, h=6.0, furniture=[
        M.fp("s1", "sofa", (3.5, 2.0), (2.2, 0.9), rotation=180.0, front=90.0)])
    assert [v["target"] for v in checks(alone, "F3")] == ["s1"]


def test_dining_chairs_facing_away_and_a_table_without_chairs():
    # real02 U7: the added chairs had rotation 0 (front -Y) beside the table.
    table = M.fp("t1", "table_dining", (2.5, 2.0), (1.6, 0.9), rotation=0.0, front=None)
    away = M.building(room_type="dining", furniture=[
        table, M.fp("c1", "chair", (2.0, 2.8), (0.45, 0.45), rotation=180.0, front=90.0, source="added_by_ai"),
        M.fp("c2", "chair", (3.0, 2.8), (0.45, 0.45), rotation=0.0, front=270.0, source="added_by_ai")])
    assert [v["target"] for v in checks(away, "F4")] == ["c1"]
    bare = M.building(room_type="dining", furniture=[table])
    f5 = checks(bare, "F5")
    assert [(v["target"], v["severity"]) for v in f5] == [("t1", "major")]


def test_an_unverified_table_asks_for_no_chairs():
    t = M.fp("t1", "table_dining", (2.5, 2.0), (1.6, 0.9), rotation=0.0, front=None, status="unverified")
    assert not checks(M.building(room_type="dining", furniture=[t]), "F5")


def test_an_armchair_behind_the_sofa_back_does_not_face_its_group():
    # real02 U13 / f_L1_029: an added armchair 1 cm behind a sofa back, facing it.
    b = M.building(room_type="living", w=7.0, h=6.0, furniture=[
        M.fp("s1", "sofa", (3.5, 3.0), (2.2, 0.9), rotation=180.0, front=90.0),
        M.fp("t1", "table_coffee", (3.5, 4.2), (1.0, 0.6), rotation=0.0, front=None),
        M.fp("a1", "armchair", (3.5, 2.09), (0.9, 0.9), rotation=180.0, front=90.0, source="added_by_ai")])
    targets = {v["target"] for v in checks(b, "F4")}
    assert "a1" in targets


def test_room_type_and_size_checks():
    counter = M.fp("k1", "kitchen_counter", (2.5, 3.68), (2.4, 0.6), rotation=0.0, front=270.0, source="added_by_ai")
    f1 = checks(M.building(furniture=[counter]), "F1")
    assert [(v["target"], v["severity"]) for v in f1] == [("k1", "major")]
    sofa = M.fp("s1", "sofa", (2.5, 3.5), (2.2, 0.9), rotation=0.0, front=270.0)
    assert [v["severity"] for v in checks(M.building(room_type="other", furniture=[sofa]), "F1")] == ["minor"]
    giant = M.fp("t1", "table_dining", (2.5, 2.0), (3.35, 1.57), rotation=0.0, front=None)
    assert [v["target"] for v in checks(M.building(room_type="dining", furniture=[giant]), "F2")] == ["t1"]
    tiny = M.building(w=2.0, h=1.5)
    assert [(v["check"], v["severity"]) for v in checks(tiny, "R1")] == [("R1", "major")]
    bath = M.building(room_type="bedroom", furniture=[M.fp("x", "bathtub", (1.0, 3.6), (1.7, 0.75), front=270.0)])
    assert any("bathtub" in v["message"] for v in checks(bath, "R1"))


def test_blocked_door_swing_and_window():
    # The door d1 at x = 1.0 on the south wall opens into the room.
    wardrobe = M.fp("w1", "wardrobe", (1.0, 0.32), (1.8, 0.6), rotation=180.0, front=90.0)
    vs = checks(M.building(furniture=[wardrobe]))
    assert any(v["check"] == "F7" and v["severity"] == "critical" for v in vs)
    assert any(v["check"] == "R3" and v["target"] == "d1" for v in vs)
    shelf = M.fp("b1", "bookshelf", (2.5, 3.83), (1.0, 0.35), rotation=0.0, front=270.0)   # in front of win1
    f7 = checks(M.building(furniture=[shelf]), "F7")
    assert [(v["target"], v["severity"]) for v in f7] == [("b1", "major")]


def test_floating_piece_overlap_and_unknown_box():
    lonely = M.fp("a1", "armchair", (2.5, 2.0), (0.9, 0.9), rotation=0.0, front=270.0)
    assert [v["target"] for v in checks(M.building(furniture=[lonely]), "F8")] == ["a1"]
    over = [M.fp("w1", "wardrobe", (3.0, 3.68), (1.8, 0.6), rotation=0.0, front=270.0),
            M.fp("d1", "dresser", (3.5, 3.68), (1.2, 0.5), rotation=0.0, front=270.0)]
    assert any(v["check"] == "F9" and "overlaps" in v["message"] for v in checks(M.building(furniture=over)))
    tucked = [M.fp("t1", "table_dining", (2.5, 2.0), (1.6, 0.9), front=None),
              M.fp("c1", "chair", (2.5, 2.5), (0.45, 0.45), rotation=0.0, front=270.0)]
    assert not [v for v in checks(M.building(room_type="dining", furniture=tucked), "F9")]
    box = M.fp("u1", "unknown", (2.5, 2.0), (1.5, 1.0), front=None, status="unverified")
    assert [(v["target"], v["severity"]) for v in checks(M.building(furniture=[box]), "F9")] == [("u1", "major")]
    hidden = dict(box, build=False)
    assert not checks(M.building(furniture=[hidden]), "F9")


def test_score_formula_and_building_summary():
    b = M.building(furniture=[M.fp("b1", "bed_double", (2.5, 2.0), (1.6, 2.0), rotation=90.0, front=0.0)])
    res = PL.score_room(b, M.ROOM_ID)
    assert res["penalty"] == sum(PL.WEIGHTS[v["severity"]] for v in res["violations"])
    assert res["score"] == max(0.0, 100.0 - res["penalty"])
    total = PL.score_building(b)
    assert total["rooms"][M.ROOM_ID]["score"] == res["score"] and total["mean"] == res["score"]
    assert sum(total["counts"].values()) == len(res["violations"])
    assert PL.summary_lines(total)[0].startswith("mean score")


def test_pure_and_fast():
    furniture = [M.fp(f"c{k}", "chair", (0.5 + 0.6 * k, 1.5), (0.45, 0.45), rotation=0.0, front=270.0)
                 for k in range(7)]
    furniture += [M.fp("t1", "table_dining", (2.5, 2.2), (2.0, 1.0), front=None),
                  M.fp("w1", "wardrobe", (3.5, 3.68), (1.8, 0.6), front=270.0),
                  M.fp("b1", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=90.0, front=0.0)]
    b = M.building(furniture=furniture)
    before = json.dumps(b, sort_keys=True)
    t0 = time.perf_counter()
    for _ in range(5):
        PL.score_room(b, M.ROOM_ID)
    per_room = (time.perf_counter() - t0) / 5
    assert json.dumps(b, sort_keys=True) == before
    assert per_room < 0.05, per_room


def test_orientation_rules_cover_every_type():
    assert set(schemas.SIZE_OPTIONS) <= set(schemas.ORIENTATION_RULES)
    for t, rule in schemas.ORIENTATION_RULES.items():
        assert rule["back"] in ("wall", "wall_or_group", "free", "skip"), t
        assert set(rule["front_to"]) <= set(schemas.SIZE_OPTIONS), t
        assert set(rule["partners"]) <= set(schemas.SIZE_OPTIONS), t
