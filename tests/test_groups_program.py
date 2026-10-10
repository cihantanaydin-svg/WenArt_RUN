"""Groups as data and the room program (docs/milestone12.md §4.2, §4.3; wenart/furniture/groups.yaml, groups.py,
program.py): the YAML is validated, every number has a source, the rule table per room type, drawn pieces matched to
their groups first, a drawn anchor's group only completed, and never a second anchor."""
import copy

import pytest

import _m11_room as M
from wenart.furniture import groups as GR
from wenart.furniture import program as PR

ROOM = M.ROOM_ID


def fp(pid, ftype, center, size, front, **kw):
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def test_groups_yaml_is_valid_and_every_rule_has_a_source():
    cfg = GR.config()
    assert GR.validate_config(cfg) == []
    groups = GR.load_groups()
    assert {"seating", "dining", "sleeping_double", "sleeping_single", "storage", "work", "kitchen_run",
            "bathroom_set", "wc_set", "entrance", "balcony"} <= set(groups)
    for name, r in cfg["rules"].items():
        assert r["source"], name
    assert GR.rule_rec("walkway_main") == pytest.approx(0.91) and GR.rule_min("tv_distance") == 1.50
    assert GR.use_zone("bed_double")["sides"] == pytest.approx(GR.rule_min("bed_side"))
    assert GR.sizes_for(groups["sleeping_double"], "bed_double", 9.0)[0][0] <= \
        GR.sizes_for(groups["sleeping_double"], "bed_double", 25.0)[0][0]


@pytest.mark.parametrize("break_it, word", [
    (lambda c: c["rules"]["walkway"].update(source=["nowhere"]), "unknown source"),
    (lambda c: c["groups"]["seating"]["partners"][0].update(type="spaceship"), "not a furniture type"),
    (lambda c: c["groups"]["kitchen_run"]["run"]["order"].pop(), "order must name every module"),
    (lambda c: c["use_zones"]["bed_double"].update(sides="no_rule"), "unknown rule"),
])
def test_a_broken_groups_yaml_is_refused_with_the_place(break_it, word):
    cfg = copy.deepcopy(GR.config())
    break_it(cfg)
    problems = GR.validate_config(cfg)
    assert problems and any(word in p for p in problems), problems


@pytest.mark.parametrize("rtype, w, h, want", [
    ("bedroom", 4.0, 4.5, {"sleeping_double", "storage"}),
    ("living", 5.0, 4.5, {"seating"}),
    ("kitchen", 3.5, 4.0, {"kitchen_run"}),
    ("bathroom", 2.5, 2.4, {"bathroom_set"}),
    ("dining", 4.0, 4.0, {"dining"}),
])
def test_the_rule_table_per_room_type(rtype, w, h, want):
    prog = PR.room_program(M.building(w=w, h=h, room_type=rtype), ROOM)
    names = {g["group"] for g in prog["groups"]}
    assert want <= names, (rtype, names)
    assert all(g["group_id"] == f"{ROOM}.{g['group']}" and g["options"] for g in prog["groups"])
    assert [g["priority"] for g in prog["groups"]] == sorted((g["priority"] for g in prog["groups"]), reverse=True)


def test_rooms_that_get_no_groups():
    for rtype in ("prayer", "stair", "storage"):
        prog = PR.room_program(M.building(room_type=rtype), ROOM)
        assert prog["groups"] == [] and rtype in prog["reason"]


def test_drawn_pieces_are_matched_first_and_their_group_is_only_completed():
    bed = fp("b1", "bed_double", (1.02, 2.5), (1.6, 2.0), 0.0)
    ns = fp("n1", "nightstand", (0.22, 1.47), (0.4, 0.4), 0.0)
    prog = PR.room_program(M.building(w=4.5, h=5.0, furniture=[bed, ns]), ROOM)
    sleep = [g for g in prog["groups"] if g["group"].startswith("sleeping")]
    assert len(sleep) == 1                                              # never a second bed group
    g = sleep[0]
    assert g["drawn"] and g["anchor_id"] == "b1" and g["members"] == ["n1"] and g["missing"] == ["nightstand"]
    assert g["priority"] >= 100                                         # drawn groups first
    assert prog["groups"][0] is g


def test_an_unverified_drawn_anchor_gets_nothing():
    table = M.fp("t1", "table_dining", (2.0, 2.0), (1.6, 0.9), rotation=0.0, front=None, status="unverified")
    prog = PR.room_program(M.building(room_type="dining", furniture=[table]), ROOM)
    g = next(g for g in prog["groups"] if g["group"] == "dining")
    assert g["note"] == "unverified anchor: nothing added" and g["missing"] == []


def test_an_unknown_box_of_anchor_size_blocks_a_second_anchor():
    box = M.fp("u1", "unknown", (1.02, 2.5), (2.0, 1.6), rotation=0.0, front=None, status="unverified")
    prog = PR.room_program(M.building(w=4.5, h=5.0, furniture=[box]), ROOM)
    sleep = next(g for g in prog["groups"] if g["group"] == "sleeping_double")
    assert sleep["drawn"] and sleep["anchor_id"] == "u1" and sleep["note"].startswith("unverified anchor")
    small = M.fp("u1", "unknown", (1.0, 1.0), (0.3, 0.3), rotation=0.0, front=None, status="unverified")
    other = PR.room_program(M.building(w=4.5, h=5.0, furniture=[small]), ROOM)
    assert not next(g for g in other["groups"] if g["group"] == "sleeping_double")["drawn"]


def test_a_group_of_another_room_type_is_never_completed():
    wm = fp("wm", "washing_machine", (2.0, 3.68), (0.6, 0.6), 270.0)
    prog = PR.room_program(M.building(room_type="hall", furniture=[wm]), ROOM)
    bath = next(g for g in prog["groups"] if g["group"] == "bathroom_set")
    assert bath["note"] == "no completion: a bathroom_set group does not belong in a hall room" and not bath["missing"]


def test_program_choices_pick_an_option():
    prog = PR.room_program(M.building(w=5.0, h=4.5, room_type="living"), ROOM,
                           choices={f"{ROOM}.seating": "sofa", f"{ROOM}.nope": "x"})
    seat = next(g for g in prog["groups"] if g["group"] == "seating")
    assert seat["chosen"] == "sofa"
    bad = PR.room_program(M.building(w=5.0, h=4.5, room_type="living"), ROOM, choices={f"{ROOM}.seating": "piano"})
    assert next(g for g in bad["groups"] if g["group"] == "seating")["chosen"] is None
