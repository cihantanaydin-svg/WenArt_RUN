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
    second = E.apply_edit(b, edit("place_group", room_id=ROOM, group="sleeping_double"))
    assert not second["accepted"] and second["failed_checks"][0].startswith("second_anchor")
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
    toilet = M.fp("t1", "toilet", (4.6, 3.6), (0.4, 0.7), front=270.0)
    b = M.building(room_type="bathroom", furniture=[toilet])
    res = E.apply_edit(b, edit("mark_not_furniture", piece_id="t1", kind="room_number", evidence="crops/t1.png"))
    assert res["accepted"], res["failed_checks"]
    assert "new findings: G10" in res["message"]                       # reported, not held against the fix
    t = piece(res["building"], "t1")
    assert t["build"] is False and t["adjusted_by_ai"]["not_furniture"] == "room_number"
    sym = res["building"]["symbols"][0]
    assert sym["former_piece_id"] == "t1" and sym["crop"] == "crops/t1.png" and sym["kind"] == "room_number"
    assert sym["id"] == "sym_L0_001" and sym["evidence"][0]["method"] == "ai"
    assert LK.check(b, res["building"], "complete") == []
    assert not [f for f in SV._fixed_items(res["building"], ROOM, set()) if f["id"] == "t1"]
    removed = copy.deepcopy(b)
    removed["furniture"][0].update(build=False, adjusted_by_ai={"reason": "x", "changed": {"build": None}})
    assert any("fixed equipment removed" in v for v in LK.check(b, removed, "complete"))   # no symbol: refused
    twice = E.apply_edit(res["building"], edit("mark_not_furniture", piece_id="t1", kind="other", evidence="x"))
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
    no = E.dry_run(b, edit("place_group", room_id=ROOM, group="sleeping_double"))
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
    assert not t["remove_piece"]["allowed"] and t["mark_not_furniture"]["allowed"]
    s = E.allowed_edits(b, "s1")
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
