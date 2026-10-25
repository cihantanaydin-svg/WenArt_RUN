"""The group options grown 10x (23 Oct 2026, user: "increase the group furniture options 10x (sofa set etc)"):
extra options carry an area window and are offered beside the core options; drawn groups keep the core options;
new partners default to 0 (the core options build what they built before); per-option partner sizes, seat counts,
kitchen module sizes and set member sizes reach the solver; the reading corner and the bedroom chest are offered
only in large rooms; options with ``auto: false`` only on request; the solver never drops a required group for an
optional one."""
import copy

import pytest

import _m11_room as M
from wenart.furniture import groups as GR
from wenart.furniture import program as PR
from wenart.furniture import solver as SV

ROOM = M.ROOM_ID
CORE = {"seating": 4, "dining": 3, "sleeping_double": 2, "sleeping_single": 1, "storage": 1, "work": 1,
        "living_storage": 2, "kitchen_run": 4, "island": 1, "bathroom_set": 3, "wc_set": 1, "entrance": 2,
        "balcony": 1}


def fp(pid, ftype, center, size, front, **kw):
    return M.fp(pid, ftype, center, size, rotation=(front + 90.0) % 360.0, front=front, **kw)


def test_ten_times_the_options_and_the_core_ones_unchanged():
    counts = GR.option_count()
    assert counts["total"] >= 10 * sum(CORE.values())                       # 26 before
    for group, n in CORE.items():
        assert len(GR.core_options(group)) == n, group
        assert counts[group] > n, group
    assert counts["seating"] >= 40 and {"reading_corner", "bedroom_chest"} <= set(counts)
    groups = GR.load_groups()
    for name, g in groups.items():
        for oname, opt in g["options"].items():
            assert opt.get("what") or GR.is_core(opt), (name, oname)     # every extra says what it builds


def test_new_partners_default_to_zero_so_core_options_build_what_they_did():
    for name in ("seating", "sleeping_double", "sleeping_single", "work", "living_storage", "balcony"):
        g = GR.load_groups()[name]
        new = [p for p in g["partners"] if "default" in p]
        assert new and all(p["default"] == 0 and not p["required"] for p in new), name
        for oname in GR.core_options(name):
            counts = g["options"][oname].get("counts") or {}
            assert not any(counts.get(p["type"]) for p in new), (name, oname)


@pytest.mark.parametrize("break_it, word", [
    (lambda g: g["seating"]["options"]["sofa2_pouf"].update(colour="red"), "unknown key 'colour'"),
    (lambda g: g["seating"]["options"]["sofa2_pouf"].update(partner_sizes={"piano": [[1.0, 1.0]]}),
     "is no partner role"),
    (lambda g: g["seating"]["options"]["sofa2_pouf"].update(min_area=20.0, max_area=10.0), "below max_area"),
    (lambda g: g["seating"]["options"]["sofa"].update(max_area=10.0), "needs min_area"),
    (lambda g: g["kitchen_run"]["options"]["I_fridge70"].update(modules={"oven": {"sizes": [[0.6, 0.6]]}}),
     "is no run module"),
    (lambda g: g["bathroom_set"]["options"]["walk_in_shower"].update(partner_sizes={"sauna": [[2.0, 2.0]]}),
     "is no member type"),
])
def test_a_broken_option_is_refused(break_it, word):
    cfg = copy.deepcopy(GR.config())
    break_it(cfg["groups"])
    problems = GR.validate_config(cfg)
    assert any(word in p for p in problems), problems


def test_extras_are_offered_by_the_room_area_and_walls():
    small = GR.extra_options("seating", 10.0)
    big = GR.extra_options("seating", 30.0)
    assert "sofa2_pouf" in small and "sofa4_2_armchairs" not in small and "sofa_compact_tv" in small
    assert "sofa4_2_armchairs" in big and "sofa_compact_tv" not in big            # max_area 14
    assert "bathtub_long" not in GR.extra_options("bathroom_set", 6.0, longest=1.70)
    assert "bathtub_long" in GR.extra_options("bathroom_set", 6.0, longest=2.0)
    assert "galley_fridge70" not in GR.extra_options("kitchen_run", 8.0, width=1.8)
    assert "galley_fridge70" in GR.extra_options("kitchen_run", 8.0, width=2.4)
    assert "bunk_bed" not in GR.extra_options("sleeping_single", 12.0, subtype="child")   # auto: false


def test_the_program_adds_extras_to_the_core_rows():
    prog = PR.room_program(M.building(w=5.0, h=4.5, room_type="living"), ROOM)
    seat = next(g for g in prog["groups"] if g["group"] == "seating")
    assert seat["options"][:3] == ["sofa_2_armchairs", "sofa_armchair", "sofa"]            # the core rows first
    assert {"sofa3_side_tables", "corner_sofa_pouf", "sofa_2_armchairs_side_tables"} <= set(seat["options"])
    assert any(g["group"] == "reading_corner" and not g["required"] for g in prog["groups"])
    # A living room under 12 m²: the small-room rule narrows the seating to the sofa (no extras).
    small = PR.room_program(M.building(w=3.2, h=3.4, room_type="living"), ROOM)
    assert next(g for g in small["groups"] if g["group"] == "seating")["options"] == ["sofa"]
    assert not any(g["group"] == "reading_corner" for g in small["groups"])


def test_new_groups_only_in_large_rooms_of_their_types():
    big = {g["group"] for g in PR.room_program(M.building(w=4.5, h=4.5, room_type="bedroom"), ROOM)["groups"]}
    small = {g["group"] for g in PR.room_program(M.building(w=3.0, h=3.5, room_type="bedroom"), ROOM)["groups"]}
    kitchen = {g["group"] for g in PR.room_program(M.building(w=4.5, h=4.5, room_type="kitchen"), ROOM)["groups"]}
    assert {"reading_corner", "bedroom_chest"} <= big
    assert not ({"reading_corner", "bedroom_chest"} & small) and not ({"reading_corner", "bedroom_chest"} & kitchen)


def test_a_drawn_group_keeps_the_core_options():
    sofa = fp("s1", "sofa", (2.5, 0.5), (2.2, 0.9), 90.0)
    prog = PR.room_program(M.building(w=5.0, h=4.5, room_type="living", furniture=[sofa]), ROOM)
    (g,) = [g for g in prog["groups"] if g["anchor_id"] == "s1"]
    # 25 Oct 2026 (user: "furniture groups are not sufficient"): the core options and the accessory extras (end
    # tables, a lamp, a plant: PR.ACCESSORY_TYPES) that keep the drawn sofa's size
    opts = GR.load_groups()["seating"]["options"]
    assert g["drawn"] and g["options"] and all(GR.is_core(opts[o]) or PR._accessory_option("seating", opts[o])
                                                for o in g["options"])
    assert not any(opts[o].get("sizes") for o in g["options"])
    # a group re-solved as one unit (this sofa stands on a door strip) is put right with the core options only
    assert g.get("resolve") and all(GR.is_core(opts[o]) for o in g["options"])
    assert any(not GR.is_core(opts[o]) for o in PR.drawn_options("seating", list(opts)))


def test_an_on_request_option_can_be_chosen():
    b = M.building(w=3.2, h=3.5, room_type="bedroom")
    b["rooms"][0]["room_subtype"] = "child"
    prog = PR.room_program(b, ROOM, choices={f"{ROOM}.sleeping_single": "bunk_bed"})
    g = next(g for g in prog["groups"] if g["group"] == "sleeping_single")
    assert g["chosen"] == "bunk_bed" and "bunk_bed" in g["options"]
    assert "bunk_bed" not in PR.room_program(b, ROOM)["groups"][0]["options"]


def _only(b, group, option):
    prog = PR.room_program(b, ROOM)
    prog["groups"] = [g for g in prog["groups"] if g["group"] == group]
    prog["groups"][0]["options"] = [option]
    best = SV.solve_room(b, ROOM, program=prog, k=1)[0]
    return best, sorted((p["type"], tuple(p["footprint"]["size"])) for p in best["pieces"])


def test_option_counts_and_sizes_reach_the_solver():
    living = M.building(w=5.0, h=4.5, room_type="living")
    best, pieces = _only(living, "seating", "sofa3_side_tables")
    types = [t for t, _ in pieces]
    assert not best["hard_failures"] and types.count("side_table") == 2 and "armchair" not in types
    assert ("sofa", (2.2, 0.9)) in pieces
    best, pieces = _only(living, "seating", "sofa2_pouf")
    types = [t for t, _ in pieces]
    assert not best["hard_failures"] and "ottoman" in types and "table_coffee" not in types
    dining = M.building(w=4.0, h=4.0, room_type="dining")
    best, pieces = _only(dining, "dining", "seats_4_round")
    assert not best["hard_failures"] and [t for t, _ in pieces].count("chair") == 4
    assert any(t == "table_dining" and s[0] == s[1] for t, s in pieces)


def test_kitchen_module_sizes_and_bath_member_sizes():
    kitchen = M.building(w=3.5, h=4.0, room_type="kitchen", window=(1.75, 1.0), sill=1.0)
    best, pieces = _only(kitchen, "kitchen_run", "I_fridge70")
    assert not best["hard_failures"] and any(t == "fridge" and s[0] == pytest.approx(0.7) for t, s in pieces)
    bath = M.building(w=2.6, h=2.6, room_type="bathroom")
    best, pieces = _only(bath, "bathroom_set", "walk_in_shower")
    shower = [s for t, s in pieces if t == "shower"]
    assert shower and not best["hard_failures"]
    assert SV._option_run(GR.load_groups()["kitchen_run"], "I_double_sink")["modules"]["sink"]["sizes"][0] == [1.0, 0.6]


def test_a_large_bedroom_keeps_its_bed_with_the_extra_groups():
    # Found while growing the options: the full layout failed the final check by the bed's foot, and the fallback
    # dropped the bed (required) instead of the optional reading corner.
    best = SV.solve_room(M.building(w=4.0, h=4.5, room_type="bedroom"), ROOM, k=1)[0]
    types = sorted(p["type"] for p in best["pieces"])
    assert not best["hard_failures"] and types.count("bed_double") == 1 and "wardrobe" in types
    assert not [g for g in best["not_placed"] if g["required"]]


def test_an_l_run_corner_is_no_aisle_obstacle():
    from wenart.furniture import group_checks as GC

    kitchen = M.building(w=3.5, h=4.0, room_type="kitchen", window=(1.75, 1.0), sill=1.0)
    best, _ = _only(kitchen, "kitchen_run", "L")
    after = SV.apply_candidate(kitchen, ROOM, best)
    assert not best["hard_failures"]
    assert not [v for v in GC.check_room(after, ROOM) if v["check"] == "G8" and "aisle" in v["message"]]


def test_a_room_with_drawn_furniture_gets_no_extra_only_group():
    bed = fp("b1", "bed_double", (1.02, 2.25), (1.6, 2.0), 0.0)
    prog = PR.room_program(M.building(w=4.5, h=4.5, room_type="bedroom", furniture=[bed]), ROOM)
    names = {g["group"] for g in prog["groups"]}
    assert not ({"reading_corner", "bedroom_chest"} & names)
    assert "no reading_corner, bedroom_chest (drawn furniture: completed only)" in prog["reason"]


def test_set_extras_add_sizes_not_members_unless_chosen():
    hall = M.building(w=2.4, h=4.0, room_type="hall")
    best = SV.solve_room(hall, ROOM, k=1)[0]
    types = sorted(p["type"] for p in best["pieces"])
    assert types and set(types) <= {"shoe_cabinet", "console_table"}          # no bench, plant or bookshelf unasked
    prog = PR.room_program(hall, ROOM, choices={f"{ROOM}.entrance": "shoe_cabinet_bench_plant"})
    chosen = SV.solve_room(hall, ROOM, program=prog, k=1)[0]
    assert "bench" in {p["type"] for p in chosen["pieces"]} or "potted_plant" in {p["type"] for p in chosen["pieces"]}


def test_the_dining_options_leave_budget_for_the_groups_after_them():
    # real04's play room (found while growing the options): 26 dining options used up the generation budget and the
    # living storage after them got no candidate; each group and option now has its share.
    b = M.building(w=7.0, h=6.0, room_type="living")
    prog = PR.room_program(b, ROOM)
    assert {"seating", "dining", "living_storage"} <= {g["group"] for g in prog["groups"]}
    best = SV.solve_room(b, ROOM, program=prog, k=1)[0]
    placed = {g.split(".")[-1] for g in best["placed"]}
    assert {"seating", "dining", "living_storage"} <= placed and not best["hard_failures"]


def test_the_agent_brief_lists_some_options_and_the_plan_may_name_the_others():
    from wenart.agent import brief as BR
    from wenart.agent import loop as LP

    assert BR.BRIEF_OPTIONS == 5
    shown = GR.core_options("seating") + GR.extra_options("seating", 30.0)[:1]
    brief = {"room": {"id": ROOM}, "findings": {}, "pieces": [], "groups": [], "free_wall_spans": [],
             "program": {"groups": [{"group_id": f"{ROOM}.seating", "group": "seating", "options": shown,
                                     "more_options": 30}]}}
    plan = {"room_id": ROOM, "steps": [], "program": {"choices": [
        {"group_id": f"{ROOM}.seating", "option": "sofa4_2_armchairs"},          # not shown, but of the group
        {"group_id": f"{ROOM}.seating", "option": "piano"}]}}
    _steps, problems = LP.check_plan(plan, brief, [])
    assert not any("sofa4_2_armchairs" in p for p in problems)
    assert any("'piano' is not one of" in p for p in problems)
