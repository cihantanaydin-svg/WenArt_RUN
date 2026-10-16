"""The agent's group tools and fixture fixes (docs/milestone12.md §5.2, §5.3, §4.1 U1; wenart/furniture/edit_ops.py,
wenart/furniture/locked.py): one passing and one failing case per tool, the numbers in every refusal, ``dry_run``,
``allowed_edits`` and the locked check after each accepted edit."""
import copy
import json

import _m11_room as M
from wenart.furniture import edit_ops as E
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import locked as LK
from wenart.furniture import placer as P
from wenart.furniture import solver as SV

META = {"reason": "test", "round": 2, "log_seq": 3, "model": "mock"}
ROOM = M.ROOM_ID


def edit(op, **args):
    return dict({"op": op}, **META, **args)


def bed(**kw):
    """A 1.6 x 2.0 double bed, headboard on the west wall, facing east."""
    return M.fp("b1", "bed_double", (1.02, 2.0), (1.6, 2.0), rotation=90.0, front=0.0, **kw)


def piece(b, pid):
    return next(f for f in b["furniture"] if f["id"] == pid)


def added(b):
    return [f for f in b["furniture"] if f["source"] == "added_by_ai"]


# --------------------------------------------------------------------------
# complete_group, place_group, add
# --------------------------------------------------------------------------

def test_complete_group_adds_the_nightstands_of_a_drawn_bed():
    b = M.building(furniture=[bed()])
    gid = f"{ROOM}.sleeping_double"
    assert [g["group_id"] for g in GR.group_members(b, ROOM)] == [gid]
    res = E.apply_edit(b, edit("complete_group", group_id=gid))
    assert res["accepted"], res["failed_checks"]
    stands = [f for f in added(res["building"]) if f["type"] == "nightstand"]
    assert len(stands) == 2 and all(f["group"]["anchor_id"] == "b1" and f["completes_room"] for f in stands)
    sides = {GC.nightstand_place(P.drawn_piece(bed()), P.drawn_piece(f))["side"] for f in stands}
    assert sides == {"left", "right"}
    assert LK.check(b, res["building"], "complete") == []
    again = E.apply_edit(res["building"], edit("complete_group", group_id=gid))
    assert not again["accepted"] and "nothing missing" in again["failed_checks"][0]
    missing = E.apply_edit(b, edit("complete_group", group_id=f"{ROOM}.dining"))
    assert not missing["accepted"] and f"groups: {gid}" in missing["failed_checks"][0]


def test_add_of_a_missing_partner_goes_through_the_solver():
    """Fails on Milestone 11: the placer put the nightstand 0.78 m from the bed, facing away (G4)."""
    b = M.building(furniture=[bed()])
    res = E.apply_edit(b, edit("add", room_id=ROOM, type="nightstand"))
    assert res["accepted"], res["failed_checks"]
    new = added(res["building"])
    assert [f["type"] for f in new] == ["nightstand"] and new[0]["group"]["anchor_id"] == "b1"
    place = GC.nightstand_place(P.drawn_piece(bed()), P.drawn_piece(new[0]))
    assert place["side_gap_m"] <= 0.10 and place["head_offset_m"] <= 0.10


def test_place_group_never_a_second_anchor_and_only_where_it_belongs():
    b = M.building(furniture=[bed()])
    # Milestone 13 (B3): the room has a drawn sleeping group (the drawn bed): place_group re-solves it as one unit
    # around the drawn anchor instead of a second bed; the bed keeps its drawn values and moves at most 0.5 m
    second = E.apply_edit(b, edit("place_group", room_id=ROOM, group="sleeping_double"))
    assert second["accepted"], second["failed_checks"]
    beds = [f for f in second["building"]["furniture"] if f["type"] == "bed_double"]
    assert [f["id"] for f in beds] == ["b1"] and beds[0]["source"] == "from_documents"
    assert beds[0]["drawn_group"]["anchor_id"] == "b1" and beds[0]["drawn_group"]["moved_m"] <= 0.5
    assert beds[0]["drawn_footprint"]["center"] == [1.02, 2.0] and beds[0]["adjusted_by_ai"]["reason"]
    assert "b1" in second["changed_ids"] and LK.check(b, second["building"], "complete") == []
    kitchen = E.apply_edit(b, edit("place_group", room_id=ROOM, group="kitchen_run"))
    assert not kitchen["accepted"] and "does not belong in a bedroom room" in kitchen["failed_checks"][0]
    option = E.apply_edit(b, edit("place_group", room_id=ROOM, group="storage", option="seats_4"))
    assert not option["accepted"] and "is not an option of storage" in option["failed_checks"][0]
    res = E.apply_edit(b, edit("place_group", room_id=ROOM, group="storage"))
    assert res["accepted"], res["failed_checks"]
    assert [f["type"] for f in added(res["building"])] == ["wardrobe"]
    assert added(res["building"])[0]["group"]["role"] == "anchor"
    assert LK.check(b, res["building"], "complete") == []


def test_relayout_room_takes_candidate_k_and_program_choices():
    b = M.building(room_type="bedroom")
    one = E.apply_edit(b, edit("relayout_room", room_id=ROOM))
    two = E.apply_edit(b, edit("relayout_room", room_id=ROOM, candidate=2))
    assert one["accepted"] and two["accepted"] and one["rerun_from"] == "layout"
    layouts = [sorted((f["type"], f["footprint"]["center"]) for f in added(r["building"])) for r in (one, two)]
    assert layouts[0] != layouts[1]
    cands = SV.solve_room(b, ROOM, k=3)
    assert layouts[0] == sorted((p["type"], p["footprint"]["center"]) for p in cands[0]["pieces"])
    again = E.apply_edit(one["building"], edit("relayout_room", room_id=ROOM, candidate=2))
    assert again["accepted"] and not set(f["id"] for f in added(one["building"])) & set(
        f["id"] for f in added(again["building"])) - set(again["changed_ids"])
    assert len([f for f in again["building"]["furniture"] if f["type"] == "bed_double"]) == 1   # replaced, not added
    bad = E.apply_edit(b, edit("relayout_room", room_id=ROOM, choices={f"{ROOM}.sleeping_double": "sofa"}))
    assert not bad["accepted"] and "is not an option of the room's program" in bad["failed_checks"][0]
    assert not E.apply_edit(b, edit("relayout_room", room_id=ROOM, candidate=9))["accepted"]     # schema: 1-5


def test_move_group_moves_an_added_group_to_another_span():
    b = E.apply_edit(M.building(room_type="bedroom", w=6.0, h=5.0),
                     edit("relayout_room", room_id=ROOM))["building"]
    gid = next(f["group"]["group_id"] for f in added(b) if f["type"] == "bed_double")
    bed_now = P.drawn_piece(next(f for f in added(b) if f["type"] == "bed_double"))
    spans = E.free_spans(b, ROOM)
    assert spans and all(s["span_id"].startswith(ROOM + ".s") and s["length"] >= 0.3 for s in spans)
    ctx = P.room_context(b, b["rooms"][0])

    def edge_of(p):
        mid = P.back_edge_midpoint(p.center, p.rotation_deg, p.size)
        return min(range(len(ctx.segments)), key=lambda i: P.G.point_segment_distance(mid, *ctx.segments[i]))

    before = edge_of(bed_now)
    others = [s for s in spans if s["edge"] != before and s["length"] >= 2.0]
    assert others
    moved = None
    for s in others:
        res = E.apply_edit(b, edit("move_group", group_id=gid, span_id=s["span_id"]))
        if res["accepted"]:
            moved = (s, res)
            break
    assert moved is not None, [E.apply_edit(b, edit("move_group", group_id=gid, span_id=s["span_id"]))["failed_checks"]
                               for s in others]
    s, res = moved
    new_bed = P.drawn_piece(next(f for f in added(res["building"]) if f["type"] == "bed_double"))
    assert edge_of(new_bed) == s["edge"]
    stands = [f for f in added(res["building"]) if f["type"] == "nightstand"]
    assert stands and all(f["group"]["anchor_id"] == next(x["id"] for x in added(res["building"])
                                                          if x["type"] == "bed_double") for f in stands)
    drawn = M.building(furniture=[bed()])
    refused = E.apply_edit(drawn, edit("move_group", group_id=f"{ROOM}.sleeping_double", span_id=f"{ROOM}.s0"))
    assert not refused["accepted"] and "stay where they are drawn" in refused["failed_checks"][0]
    nospan = E.apply_edit(b, edit("move_group", group_id=gid, span_id=f"{ROOM}.s99"))
    assert not nospan["accepted"] and "no free span" in nospan["failed_checks"][0]


# --------------------------------------------------------------------------
# retype_piece, mark_not_furniture, set_front
# --------------------------------------------------------------------------

def test_retype_piece_takes_only_types_that_fit_the_footprint_and_the_room():
    box = M.fp("u1", "unknown", (0.221, 0.93), (0.4, 0.4), rotation=90.0, front=0.0, status="unverified")
    b = M.building(furniture=[bed(), box])
    res = E.apply_edit(b, edit("retype_piece", piece_id="u1", type="nightstand"))
    assert res["accepted"], res["failed_checks"]
    assert piece(res["building"], "u1")["type"] == "nightstand" and piece(res["building"], "u1")["inferred"] is True
    wrong = E.apply_edit(b, edit("retype_piece", piece_id="u1", type="wardrobe"))
    msg = wrong["failed_checks"][0]
    assert not wrong["accepted"] and "0.40 x 0.40 m" in msg and "nightstand" in msg.split("give ")[1]
    toilet = E.apply_edit(b, edit("retype_piece", piece_id="u1", type="toilet"))
    assert not toilet["accepted"]                                     # a bedroom holds no toilet


def test_mark_not_furniture_leaves_a_misread_symbol_out():
    # Round 4: a drawn armchair outline that is really the room-number circle (fixed equipment is never marked, see
    # test_mark_not_furniture_refuses_drawn_fixed_equipment)
    toilet = M.fp("t1", "toilet", (4.6, 3.6), (0.4, 0.7), front=270.0)
    circle = M.fp("c1", "armchair", (2.5, 2.0), (0.8, 0.8), front=270.0)
    b = M.building(room_type="living", furniture=[circle, toilet])
    res = E.apply_edit(b, edit("mark_not_furniture", piece_id="c1", kind="room_number", evidence="crops/c1.png"))
    assert res["accepted"], res["failed_checks"]
    t = piece(res["building"], "c1")
    assert t["build"] is False and t["adjusted_by_ai"]["not_furniture"] == "room_number"
    sym = res["building"]["symbols"][0]
    assert sym["former_piece_id"] == "c1" and sym["crop"] == "crops/c1.png" and sym["kind"] == "room_number"
    assert sym["id"] == "sym_L0_001" and sym["evidence"][0]["method"] == "ai"
    assert LK.check(b, res["building"], "complete") == []
    assert not [f for f in SV._fixed_items(res["building"], ROOM, set()) if f["id"] == "c1"]
    removed = copy.deepcopy(b)
    removed["furniture"][1].update(build=False, adjusted_by_ai={"reason": "x", "changed": {"build": None}})
    assert any("fixed equipment removed" in v for v in LK.check(b, removed, "complete"))   # no symbol: refused
    twice = E.apply_edit(res["building"], edit("mark_not_furniture", piece_id="c1", kind="other", evidence="x"))
    assert not twice["accepted"]
    ai = M.fp("a1", "chair", (2.5, 2.0), (0.45, 0.45), source="added_by_ai")
    assert not E.apply_edit(M.building(furniture=[ai]), edit("mark_not_furniture", piece_id="a1", kind="other",
                                                             evidence="x"))["accepted"]


def test_set_front_gives_a_drawn_piece_without_a_front_one_side():
    sofa = M.fp("s1", "sofa", (2.5, 0.47), (2.2, 0.9), rotation=0.0, front=None)
    b = M.building(room_type="living", furniture=[sofa])
    res = E.apply_edit(b, edit("set_front", piece_id="s1", front_deg=90.4))
    assert res["accepted"], res["failed_checks"]
    s = piece(res["building"], "s1")
    assert s["front_deg"] == 90.0 and s["drawn_front_deg"] is None
    poly_a, poly_b = P.drawn_piece(sofa).polygon(), P.drawn_piece(s).polygon()
    assert poly_a.symmetric_difference(poly_b).area < 1e-9                  # the same rectangle
    assert LK.check(b, res["building"], "complete") == []
    off = E.apply_edit(b, edit("set_front", piece_id="s1", front_deg=37))
    assert not off["accepted"] and "37.0° off the nearest side" in off["failed_checks"][0]
    again = E.apply_edit(res["building"], edit("set_front", piece_id="s1", front_deg=270))
    assert not again["accepted"] and "faces 90° already" in again["failed_checks"][0]


# --------------------------------------------------------------------------
# fix_fixture (U1) and the locked check
# --------------------------------------------------------------------------

def test_fix_fixture_gives_a_misread_toilet_a_real_size():
    """real03 U1: toilets read 1.145 x 0.356 m get the nearest real toilet size, back on the wall."""
    big = M.fp("t1", "toilet", (2.5, 3.802), (1.145, 0.356), front=270.0)
    b = M.building(room_type="bathroom", furniture=[big])
    res = E.apply_edit(b, edit("fix_fixture", piece_id="t1"))
    assert res["accepted"], res["failed_checks"]
    t = piece(res["building"], "t1")
    assert t["footprint"]["size"] == [0.5, 0.55] and t["drawn_footprint"]["size"] == [1.145, 0.356]
    fix = t["adjusted_by_ai"]["fix_fixture"]
    assert fix["resized"] is True and fix["size"]["off"] > 0.3
    assert LK.anchor_of(t, res["building"])["kind"] == "back_edge"       # grown from its wall line
    assert LK.check(b, res["building"], "complete") == []
    normal = M.building(room_type="bathroom", furniture=[M.fp("t2", "toilet", (2.5, 3.63), (0.4, 0.7), front=270.0)])
    refused = E.apply_edit(normal, edit("fix_fixture", piece_id="t2", size=[0.45, 0.6]))
    assert not refused["accepted"] and "within 30 % of the real toilet range" in refused["failed_checks"][0]
    sofa = M.building(room_type="living", furniture=[M.fp("s1", "sofa", (2.5, 0.47), (2.2, 0.9), rotation=180.0,
                                                          front=90.0)])
    not_fixed = E.apply_edit(sofa, edit("fix_fixture", piece_id="s1"))
    assert not not_fixed["accepted"] and "is for drawn fixed equipment" in not_fixed["failed_checks"][0]


def test_fix_fixture_moves_a_washbasin_out_of_the_wall_at_most_0_5_m():
    through = M.fp("w1", "washbasin", (4.9, 2.0), (0.6, 0.45), rotation=270.0, front=180.0)   # 0.125 m in the wall
    b = M.building(room_type="bathroom", furniture=[through])
    res = E.apply_edit(b, edit("fix_fixture", piece_id="w1"))
    assert res["accepted"], res["failed_checks"]
    w = piece(res["building"], "w1")
    moved = P.G.distance(w["footprint"]["center"], through["footprint"]["center"])
    assert 0.1 <= moved <= 0.5 and w["adjusted_by_ai"]["fix_fixture"]["moved_m"] == round(moved, 3)
    assert LK.check(b, res["building"], "complete") == []
    far = E.apply_edit(b, edit("fix_fixture", piece_id="w1", center=[4.2, 2.0]))
    assert not far["accepted"] and "the move is 0.70 m, at most 0.50 m" in far["failed_checks"][0]
    hand = copy.deepcopy(res["building"])
    piece(hand, "w1")["footprint"]["center"] = [4.2, 2.0]                  # a 0.7 m move under the same label
    assert any("by fix_fixture (> 0.5 m)" in v for v in LK.check(b, hand, "complete"))


def test_resize_never_turns_a_bed():
    """Fails on Milestone 11: the size table accepted either orientation, so a bed resized to 2.0 m along its front
    and 1.6 m deep (turned 90°, as real02 f_L0_007) passed."""
    b = M.building(furniture=[bed()])
    turned = E.apply_edit(b, edit("resize", piece_id="b1", size=[2.0, 1.6]))
    assert not turned["accepted"] and "turned 90°" in turned["failed_checks"][0]
    assert E.apply_edit(b, edit("resize", piece_id="b1", size=[1.8, 2.0]))["accepted"]


# --------------------------------------------------------------------------
# dry_run and allowed_edits
# --------------------------------------------------------------------------

def test_dry_run_answers_without_the_building():
    b = M.building(furniture=[bed()])
    before = json.dumps(b, sort_keys=True)
    dry = E.dry_run(b, edit("complete_group", group_id=f"{ROOM}.sleeping_double"))
    real = E.apply_edit(b, edit("complete_group", group_id=f"{ROOM}.sleeping_double"))
    assert dry["building"] is None and dry["dry_run"] is True and dry["accepted"] == real["accepted"] is True
    assert dry["changed_ids"] == real["changed_ids"] and json.dumps(b, sort_keys=True) == before
    no = E.dry_run(b, edit("place_group", room_id=ROOM, group="kitchen_run"))
    assert not no["accepted"] and no["building"] is None and no["failed_checks"]


def test_allowed_edits_per_tool_from_the_locks():
    toilet = M.fp("t1", "toilet", (4.9, 3.6), (0.4, 0.7), rotation=90.0, front=0.0)          # through the wall
    sofa = M.fp("s1", "sofa", (2.5, 0.47), (2.2, 0.9), rotation=180.0, front=None)
    chair = M.fp("c1", "chair", (2.5, 2.0), (0.45, 0.45), source="added_by_ai")
    b = M.building(room_type="living", furniture=[toilet, sofa, chair])
    t = E.allowed_edits(b, "t1")
    tools = {"move_piece", "rotate_piece", "resize_piece", "retype_piece", "change_type", "swap_model", "remove_piece",
             "mark_not_furniture", "fix_fixture", "set_front", "complete_group", "move_group"}
    assert set(t) == tools and all(set(v) == {"allowed", "why", "move_left_m"} for v in t.values())
    assert not t["move_piece"]["allowed"] and "fix_fixture moves it up to 0.5 m" in t["move_piece"]["why"]
    assert t["fix_fixture"]["allowed"] and t["fix_fixture"]["move_left_m"] == 0.5 and "through a wall" in \
        t["fix_fixture"]["why"]
    # round 4: drawn fixed equipment is treated like walls: never removed, never marked as not furniture
    assert not t["remove_piece"]["allowed"] and not t["mark_not_furniture"]["allowed"]
    assert "treated like walls" in t["mark_not_furniture"]["why"] and "fix_fixture" in t["mark_not_furniture"]["why"]
    s = E.allowed_edits(b, "s1")
    assert s["mark_not_furniture"]["allowed"]
    assert s["move_piece"]["allowed"] and s["move_piece"]["move_left_m"] == 0.3
    assert s["set_front"]["allowed"] and not s["fix_fixture"]["allowed"]
    c = E.allowed_edits(b, "c1")
    assert c["move_piece"]["allowed"] and c["move_piece"]["move_left_m"] is None
    assert not c["mark_not_furniture"]["allowed"] and not c["set_front"]["allowed"]
    kept = copy.deepcopy(b)
    kept["project"]["brief"] = {"furnished_rooms": "keep"}
    k = E.allowed_edits(kept, "s1")
    assert not k["move_piece"]["allowed"] and not k["resize_piece"]["allowed"] and k["rotate_piece"]["allowed"]
    assert E.allowed_edits(b, "nope") == {}


# --------------------------------------------------------------------------
# Milestone 13, round 2: the candidate applied like layout.apply_choice; complete_group with the drawn group; refit
# --------------------------------------------------------------------------

def test_a_re_solved_drawn_group_is_applied_in_place_with_its_kept_members_and_rug():
    """``_solve_apply`` applies the candidate through ``layout.apply_choice``: the drawn pieces of
    ``candidate["resolved"]`` change in place (the same dict objects; a kept member carries its ``drawn_group`` and
    ``group`` too) and the solver's rug member comes with the decor. Before round 2 a kept member lost those keys
    and the re-solved dicts were replaced."""
    stand = M.fp("n1", "nightstand", (0.22, 3.7), (0.4, 0.4), rotation=90.0, front=0.0)
    b = M.building(w=4.5, h=5.0, furniture=[bed(), stand])
    source = copy.deepcopy(b)
    room = b["rooms"][0]
    drawn = GR.drawn_groups(b, ROOM)[0]
    assert drawn["anchor_id"] == "b1" and drawn["members"] == ["n1"]
    bed_obj, stand_obj = piece(b, "b1"), piece(b, "n1")
    changed = E._solve_apply(b, room, E._program(b, room, []), dict(META), "test", fixed=[], drawn_group=drawn)
    assert piece(b, "b1") is bed_obj and piece(b, "n1") is stand_obj                 # changed in place
    assert changed[:2] == ["b1", "n1"] or changed[:1] == ["b1"]
    for pid in ("b1", "n1"):
        f = piece(b, pid)
        assert f["drawn_group"]["anchor_id"] == "b1" and f["drawn_group"]["moved_m"] <= GR.GROUP_MEMBER_MOVE_MAX_M
        assert f["group"]["group"] == "sleeping_double" and f["group"]["anchor_id"] == "b1"
    assert piece(b, "b1")["adjusted_by_ai"]["by"] == "solver" and piece(b, "b1")["adjusted_by_ai"]["round"] == 2
    rugs = [d for d in b["decor"] if d["type"] == "rug"]
    assert len(rugs) == 1 and rugs[0]["group"]["role"] == "rug" and "b1" in rugs[0]["anchor_ids"]
    new = added(b)
    assert new and all(f["completes_room"] and f["checks"] and f["layout"]["candidate"] == 1 for f in new)
    assert all([e["method"] for e in f["evidence"]][-2:] == ["derived", "ai"] for f in new)
    assert LK.check(source, b, "complete") == []
    # through apply_edit (a copy): the same, and the changed ids name the re-placed drawn pieces first
    res = E.apply_edit(source, edit("place_group", room_id=ROOM, group="sleeping_double"))
    assert res["accepted"], res["failed_checks"]
    assert res["changed_ids"][0] == "b1" and [d["type"] for d in res["building"]["decor"]] == ["rug"]
    assert piece(res["building"], "n1")["drawn_group"]["members"] == ["n1"]
    assert LK.check(source, res["building"], "complete") == []


def test_complete_group_re_solves_a_misread_drawn_anchor_as_one_unit_and_keeps_a_sound_one():
    """A drawn bed outside the product grid (1.6 x 1.5 m) is marked for a re-solve by the program: complete_group
    passes the drawn group to the solver, the bed takes a real size within 0.5 m of its drawn centre (drawn values
    kept) and the nightstands come with it; a sound drawn bed stays exactly as drawn (Milestone 12)."""
    short = M.fp("b1", "bed_double", (1.02, 2.5), (1.6, 1.5), rotation=90.0, front=0.0)
    b = M.building(w=4.5, h=5.0, furniture=[short])
    room = b["rooms"][0]
    assert E._resolve_group(b, room, "b1") is not None and E._resolve_group(b, room, None) is None
    gid = f"{ROOM}.sleeping_double"
    res = E.apply_edit(b, edit("complete_group", group_id=gid))
    assert res["accepted"], res["failed_checks"]
    b1 = piece(res["building"], "b1")
    assert b1["drawn_footprint"]["size"] == [1.6, 1.5] and b1["adjusted_by_ai"]["resized"] is True
    assert sorted(b1["footprint"]["size"]) != [1.5, 1.6] and b1["drawn_group"]["moved_m"] <= 0.5
    assert b1["asset"] is None and b1.get("build", True) is True              # the refit builds it again
    assert "re-solved with its sleeping_double group as one unit" in b1["adjusted_by_ai"]["reason"]
    assert "b1" in res["changed_ids"]
    stands = [f for f in added(res["building"]) if f["type"] == "nightstand"]
    assert len(stands) == 2 and all(f["group"]["anchor_id"] == "b1" for f in stands)
    assert LK.check(b, res["building"], "complete") == []
    sound = M.building(furniture=[bed()])
    assert E._resolve_group(sound, sound["rooms"][0], "b1") is None
    ok = E.apply_edit(sound, edit("complete_group", group_id=gid))
    assert ok["accepted"] and piece(ok["building"], "b1") == bed() and "drawn_group" not in piece(ok["building"], "b1")


def test_the_refit_builds_the_re_solved_pieces_and_the_locked_check_accepts_the_group_move():
    """Item 4 of round 2: after a drawn group re-solve (``asset`` None on a resized member, ``drawn_group``,
    ``adjusted_by_ai`` by the solver) the refit (``fit.fit_building``, the stage behind ``python -m wenart.furniture
    fit``) fits the piece again (never ``none``) and the locked check of the refit (``fit.locked_check`` ->
    ``locked.check``) accepts the member's move within ``groups.GROUP_MEMBER_MOVE_MAX_M`` and refuses a longer one."""
    from wenart.furniture import catalog as C
    from wenart.furniture import fit as F

    short = M.fp("b1", "bed_double", (1.02, 2.5), (1.6, 1.5), rotation=90.0, front=0.0)
    b = M.building(w=4.5, h=5.0, furniture=[short])
    b["project"] = {"id": "t", "name": "t", "licence_mode": "commercial"}
    res = E.apply_edit(b, edit("complete_group", group_id=f"{ROOM}.sleeping_double"))
    assert res["accepted"] and piece(res["building"], "b1")["asset"] is None
    fitted = F.fit_building(res["building"], C.load(), snap=False)
    b1 = piece(fitted, "b1")
    assert b1["asset"]["method"] in ("library", "module", "parametric") and GR.piece_is_built(b1)
    assert b1["footprint"] == piece(res["building"], "b1")["footprint"] and b1["drawn_group"]["anchor_id"] == "b1"
    assert all(f["asset"]["method"] != "none" for f in fitted["furniture"])
    assert LK.check(b, fitted, "complete") == []
    far = copy.deepcopy(fitted)
    moved = piece(far, "b1")
    moved["footprint"]["center"] = [moved["footprint"]["center"][0] + 0.6, moved["footprint"]["center"][1]]
    problems = LK.check(b, far, "complete")
    assert len(problems) == 1 and "by the solver (drawn group)" in problems[0] and "> 0.5 m" in problems[0]


# --------------------------------------------------------------------------
# CPU pre-flight of 16 Oct 2026 (real04, the P3 inputs)
# --------------------------------------------------------------------------

def _open_kitchen(zone_id):
    """A living room with an open kitchen: a counter run tagged with the group of its kitchen zone (the reading names
    the zone ``<room>_kitchen``, without a dot; real04 ``r_L-1b_salon_kitchen.kitchen_run``), the fridge missing."""
    gid = f"{zone_id}.kitchen_run"

    def tag(role):
        return {"group_id": gid, "group": "kitchen_run", "role": role, "anchor_id": "k1"}
    run = [M.fp("k1", "kitchen_counter", (3.0, 0.3), (2.4, 0.6), front=90.0, group=tag("anchor")),
           M.fp("s1", "sink_kitchen", (2.5, 0.3), (0.6, 0.5), front=90.0, group=tag("partner")),
           M.fp("h1", "stove", (3.6, 0.3), (0.6, 0.55), front=90.0, group=tag("partner"))]
    b = M.building(w=8.0, h=5.0, room_type="living", door_x=6.5, furniture=run)
    b["rooms"][0]["zones"] = [{"zone_id": zone_id, "kind": "kitchen", "piece_ids": ["k1", "s1", "h1"],
                               "polygon": [[0.0, 0.0], [5.5, 0.0], [5.5, 2.0], [0.0, 2.0]]}]
    return b, gid


def test_complete_group_finds_the_group_of_an_open_kitchen_zone():
    """Fails on the old code: the room of a group was the text before the first dot of its id, so the group of a
    kitchen zone (``r_L0_oda_kitchen.kitchen_run``) was refused as "exists: no group ... (its room
    'r_L0_oda_kitchen')" and a G9 (the open kitchen misses its fridge) could never be completed."""
    b, gid = _open_kitchen(f"{ROOM}_kitchen")
    assert [g["group_id"] for g in GR.group_members(b, ROOM)] == [gid]
    assert E.group_room_id(b, gid) == ROOM
    assert E.group_room_id(b, f"{ROOM}.sleeping_double") == ROOM          # a room's own group: unchanged
    for res in (E.apply_edit(b, edit("complete_group", group_id=gid)), E.dry_run(b, edit("complete_group",
                                                                                           group_id=gid))):
        assert not any(c.startswith(("exists", "group_exists")) for c in res["failed_checks"]), res["failed_checks"]
        assert res["accepted"] or "missing fridge" in res["failed_checks"][0]   # the solver decides, not the lookup


def test_mark_not_furniture_takes_the_piece_off_the_review_list():
    """Fails on the old code: an untyped drawn piece marked as not furniture stayed in ``needs_review``, so the code
    critic's NR finding stayed and the agent's dry re-check refused every such edit (real04: 20 NR findings)."""
    blob = M.fp("u1", "unknown", (2.5, 2.0), (1.2, 0.8), front=None, status="unverified", build=False)
    b = M.building(furniture=[blob])
    b["needs_review"] = [{"id": "u1", "kind": "untyped_piece", "reason": "no type", "room_id": ROOM,
                          "level_id": "L0"}, {"id": "u2", "kind": "untyped_piece", "reason": "other", "room_id": ROOM,
                                              "level_id": "L0"}]
    res = E.apply_edit(b, edit("mark_not_furniture", piece_id="u1", kind="other", evidence="crops/u1.png"))
    assert res["accepted"], res["failed_checks"]
    assert [n["id"] for n in res["building"]["needs_review"]] == ["u2"]
    assert res["building"]["symbols"][0]["former_piece_id"] == "u1"
    from wenart.agent import critic_code as CC
    assert [v["target"] for v in CC.reading_items(res["building"]) if v["check"] == "NR"] == ["u2"]


def test_a_second_edit_keeps_the_fix_fixture_allowance_for_the_locked_check():
    """Fails on the old code: every edit rebuilt ``adjusted_by_ai`` and kept only ``snapped_wall`` of the earlier
    labels, so a toilet fixed by ``fix_fixture`` and then edited again (marked as not furniture in the pre-flight,
    given a front here) lost its ``fix_fixture`` record and the refit's locked check refused it as "fixed equipment
    moved or resized" (CPU pre-flight of 16 Oct 2026, real03: five toilets 1.145 x 0.356 m; the scheduler then rolled
    back both edits). Round 4: marking the fixed toilet is refused now, so the second edit is ``set_front``."""
    big = M.fp("t1", "toilet", (2.5, 3.802), (1.145, 0.356), front=None)
    b = M.building(room_type="bathroom", furniture=[big])
    fixed = E.apply_edit(b, edit("fix_fixture", piece_id="t1"))
    assert fixed["accepted"], fixed["failed_checks"]
    fronted = E.apply_edit(fixed["building"], edit("set_front", piece_id="t1", front_deg=270.0))
    assert fronted["accepted"], fronted["failed_checks"]
    t = piece(fronted["building"], "t1")
    assert t["adjusted_by_ai"]["fix_fixture"] == piece(fixed["building"], "t1")["adjusted_by_ai"]["fix_fixture"]
    assert t["front_deg"] == 270.0
    assert LK.check(b, fronted["building"], "complete") == []
    # A forged larger move under the kept label is still refused: the allowance is the fix's, not a free pass.
    hand = copy.deepcopy(fronted["building"])
    piece(hand, "t1")["footprint"]["center"] = [2.5, 3.0]
    assert any("by fix_fixture (> 0.5 m)" in v for v in LK.check(b, hand, "complete"))
    # the pre-flight's second edit is refused now (round 4)
    marked = E.apply_edit(fixed["building"], edit("mark_not_furniture", piece_id="t1", kind="other",
                                                  evidence="crops/t1.png"))
    assert not marked["accepted"] and marked["failed_checks"][0].startswith("drawn_lock: t1: drawn fixed equipment")


def test_mark_not_furniture_refuses_drawn_fixed_equipment():
    """Round 4 of Milestone 13 (CLAUDE.md furniture rules: fixed equipment is treated like walls). Fails on the old
    code: the CPU pre-flight's scripted round marked 5 real03 toilets as not furniture and the edit was accepted,
    leaving 5 bathrooms without a toilet (G10 major). ``apply_edit``, ``dry_run`` and ``allowed_edits`` all refuse it
    with the reason; fixed equipment in a room that never holds it (a reading error, ``schemas.misplaced_fixed``) and
    an untyped drawn piece may still be marked."""
    toilet = M.fp("t1", "toilet", (4.6, 3.6), (0.4, 0.7), front=270.0)
    blob = M.fp("u1", "unknown", (2.0, 2.0), (0.5, 0.5), front=None, status="unverified")
    b = M.building(room_type="bathroom", furniture=[toilet, blob])
    for fn in (E.apply_edit, E.dry_run):
        res = fn(b, edit("mark_not_furniture", piece_id="t1", kind="other", evidence="crops/t1.png"))
        assert not res["accepted"] and res["building"] is None
        assert res["failed_checks"] == ["drawn_lock: t1: drawn fixed equipment (toilet) is treated like walls and is "
                                        "never marked as not furniture (fix_fixture fixes a misread size or a piece "
                                        "through a wall or in a door swing)"]
    allowed = E.allowed_edits(b, "t1")["mark_not_furniture"]
    assert allowed["allowed"] is False and "treated like walls" in allowed["why"]
    for ftype in ("stair", "kitchen_counter", "sink_kitchen", "stove", "fridge", "washbasin", "shower", "bathtub"):
        other = M.building(room_type="bathroom", furniture=[dict(toilet, type=ftype)])
        assert not E.apply_edit(other, edit("mark_not_furniture", piece_id="t1", kind="other",
                                            evidence="x"))["accepted"], ftype
    # an untyped drawn piece: still marked
    assert E.allowed_edits(b, "u1")["mark_not_furniture"]["allowed"]
    assert E.apply_edit(b, edit("mark_not_furniture", piece_id="u1", kind="room_number", evidence="crops/u1.png"))[
        "accepted"]
    # a toilet read in a stair room is a reading error: it may be marked (as remove_piece and retype_piece may act)
    stair = M.building(room_type="stair", furniture=[toilet])
    a = E.allowed_edits(stair, "t1")
    assert a["mark_not_furniture"]["allowed"] and "reading error" in a["mark_not_furniture"]["why"]
    res = E.apply_edit(stair, edit("mark_not_furniture", piece_id="t1", kind="other", evidence="crops/t1.png"))
    assert res["accepted"], res["failed_checks"]
