"""C1's walk from the entrance (31 Oct 2026, real06 run 20261030-224530-full: the architect question C1 "cannot be
reached from the entrance" fired for 11 of 12 rooms, and the AI then retyped them as store rooms one by one, although
its own reasons named their doors to the hall).

Root cause: an answer of the AI architect (``AI.pass_through:o_L0_001``) made the only passage between the living room
(the entrance room) and the kitchen a serving hatch; the kitchen holds the stair and the doors to the bathroom and the
store, so the whole house behind it was cut off. The rules pinned here, for every project:

- no answer that is not the user's takes away the only way between two rooms (a door or passage made a window or a
  hatch, closed or merged away, a stair left out): code checks the room graph after it and undoes it whole, with the
  reason (``architect_actions.walk_cut``);
- more than half of the rooms unreached, or every room of a level, is a reading problem of the room graph, never a
  house of shafts: C1 logs one point (``C1:room_graph``) with no retype to choose, and C1's retype answers are not
  carried out for it (``architect.circulation``, ``architect_actions.c1_refusal``);
- a room no door reaches is offered the window between it and a reached room as its door.

Pure tests (no Blender) on a small synthetic house; the real06 replay reads the committed latest baseline and skips
without it."""
import copy
import json
from pathlib import Path

import pytest

from wenart.agent import architect_ai as AI
from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "results" / "baseline" / "latest" / "furniture" / "real06" / "building_final.json"


def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _house(second_way: bool = False) -> dict:
    """Ground floor: the living room l (the entrance d0 in its south wall), the kitchen k north of it behind the only
    passage o1 (2.9 m, no leaf), the bathroom w and the store s off the kitchen, the stair room st0 off the kitchen.
    Upper floor (over it all): the hall h (the stair room st1 opens onto it) and the bedrooms b1, b2 off the hall.
    ``second_way``: a door d9 joins the living room and the kitchen as well."""
    levels = [{"id": "L0", "elevation": 0.0, "height": 3.0, "ceiling_height": 2.8},
              {"id": "L1", "elevation": 3.0, "height": 3.0, "ceiling_height": 2.8}]

    def room(rid, lid, rtype, poly, **kw):
        return dict({"id": rid, "level_id": lid, "room_type": rtype, "polygon": poly}, **kw)

    def wall(wid, lid, a, b):
        return {"id": wid, "level_id": lid, "start": a, "end": b, "thickness": 0.2}

    def op(oid, kind, lid, wid, c, width=0.9, **kw):
        return dict({"id": oid, "type": kind, "level_id": lid, "wall_id": wid, "center": c, "width": width,
                     "height": 2.1}, **kw)

    rooms = [room("l", "L0", "living", _rect(0, 0, 10, 5)), room("k", "L0", "kitchen", _rect(0, 5, 6, 9)),
             room("w", "L0", "bathroom", _rect(6, 5, 8, 9)), room("s", "L0", "storage", _rect(8, 5, 10, 7)),
             room("st0", "L0", "hall", _rect(8, 7, 10, 9), label="MERDIVEN"),
             room("h", "L1", "hall", _rect(6, 5, 10, 9)), room("b1", "L1", "bedroom", _rect(0, 0, 10, 5)),
             room("b2", "L1", "bedroom", _rect(0, 5, 6, 9)), room("st1", "L1", "hall", _rect(8, 7, 10, 9),
                                                                  label="MERDIVEN")]
    walls = [wall("ws", "L0", [0, 0], [10, 0]), wall("wlk", "L0", [0, 5], [6, 5]), wall("wkw", "L0", [6, 5], [6, 9]),
             wall("wks", "L0", [8, 7], [10, 7]), wall("wws", "L0", [8, 5], [8, 9]),
             wall("wh1", "L1", [0, 5], [10, 5]), wall("wh2", "L1", [6, 5], [6, 9])]
    openings = [op("d0", "door", "L0", "ws", [5, 0]), op("o1", "opening", "L0", "wlk", [2, 5], 2.9),
                op("d2", "door", "L0", "wkw", [6, 6]), op("d3", "door", "L0", "wws", [8, 6]),
                op("d4", "door", "L0", "wks", [9, 7]),
                op("d5", "door", "L1", "wh1", [8, 5]), op("d6", "door", "L1", "wh2", [6, 7])]
    if second_way:
        openings.append(op("d9", "door", "L0", "wlk", [5, 5]))
    return {"levels": levels, "rooms": rooms, "walls": walls, "openings": openings, "furniture": [],
            "site": {"entrances": [{"door_id": "d0", "level_id": "L0", "main": True}]}}


def _ai(option, **params):
    return {"option": option, "params": params, "by": "ai", "answer": "a test answer"}


def test_the_synthetic_house_is_walked_through_from_the_entrance():
    b = _house()
    walk = AR.circulation(b)
    assert walk["starts"] == ["l"] and walk["unreached"] == [] and not walk["reading_problem"]
    assert ("st0", "st0", "h") in AR.stair_links(b) or ("st0", "st0", "st1") in AR.stair_links(b)
    c1 = AR.review_circulation(b, AR.opening_sides(b))
    assert not [a for a in c1["answers"] if a.get("open")]


def test_an_answer_never_makes_the_only_passage_between_two_rooms_a_hatch():
    b = _house()
    o1 = next(o for o in b["openings"] if o["id"] == "o1")
    res = AA.apply_answers(b, {"AI.pass_through:o1": _ai("pass_through")})
    rec = res[0]
    assert not rec["ok"] and "undone" in rec["change"]
    assert "o1 was the only way between k and l" in rec["change"]
    assert "no longer be reached from the entrance" in rec["change"] and "b1" in rec["change"]
    assert next(o for o in b["openings"] if o["id"] == "o1") is o1              # undone in place
    assert o1["type"] == "opening" and "corrected_by_ai" not in o1 and "interior_glazing" not in o1
    assert AR.circulation(b)["unreached"] == []
    # the plan's lookups see the restored openings (a later answer on o1 acts on the passage as it stands)
    res = AA.apply_answers(b, {"AI.pass_through:o1": _ai("pass_through"), "D1:o1": _ai("widen_door")})
    assert next(r for r in res if r["key"] == "D1:o1")["change"] == "o1 is 2.90 m wide"


def test_a_passage_with_a_second_way_beside_it_may_become_a_hatch():
    b = _house(second_way=True)
    res = AA.apply_answers(b, {"AI.pass_through:o1": _ai("pass_through")})
    assert res[0]["ok"], res[0]["change"]
    assert next(o for o in b["openings"] if o["id"] == "o1")["type"] == "window"
    assert AR.circulation(b)["unreached"] == []


def test_the_users_answer_is_carried_out_and_the_cut_shows_as_one_reading_problem():
    """The user may close a passage (the user's answers win); then 8 of 9 rooms are unreached: C1 logs one reading
    problem with no retype, never one point per room, and the AI architect is not asked to close it."""
    b = _house()
    res = AA.apply_answers(b, {"AI.pass_through:o1": dict(_ai("pass_through"), by="user")})
    assert res[0]["ok"]
    walk = AR.circulation(b)
    assert walk["reading_problem"] and len(walk["unreached"]) == 8
    c1 = AR.review_circulation(b, AR.opening_sides(b))
    opened = [a for a in c1["answers"] if a.get("open")]
    assert [a["element"] for a in opened] == [AR.READING_ELEMENT]
    point = opened[0]
    assert point["reading_problem"] and point["rooms"] == walk["unreached"] and "reading problem" in point["found"]
    assert [o["id"] for o in point["options"]] == ["keep"]
    rec = AR.summary([c1])
    assert not [q for q in AI.open_questions(rec, set()) if q["rule"] == "C1"]


def test_c1_retypes_are_not_carried_out_for_a_reading_problem_or_a_reached_room():
    b = _house()
    AA.apply_answers(b, {"AI.pass_through:o1": dict(_ai("pass_through"), by="user")})
    res = AA.apply_answers(b, {"C1:b1": _ai("retype_room", room_type="storage")})
    assert not res[0]["ok"] and "reading problem" in res[0]["change"]
    assert next(r for r in b["rooms"] if r["id"] == "b1")["room_type"] == "bedroom"
    ok = _house()
    res = AA.apply_answers(ok, {"C1:k": _ai("retype_room", room_type="storage")})
    assert not res[0]["ok"] and "is reached from the entrance" in res[0]["change"]
    assert next(r for r in ok["rooms"] if r["id"] == "k")["room_type"] == "kitchen"


def test_a_floor_nobody_reaches_is_a_reading_problem_too():
    """The stair not read (st0 and st1 plain halls): the 4 rooms of the upper floor are fewer than half of the 9, but
    a whole floor of shafts does not exist: one reading problem naming the level, no retype."""
    b = _house()
    for r in b["rooms"]:
        if r["id"] in ("st0", "st1"):
            r["label"] = "HOL"
    walk = AR.circulation(b)
    assert sorted(walk["unreached"]) == ["b1", "b2", "h", "st1"] and walk["levels_cut"] == ["L1"]
    assert walk["reading_problem"]
    c1 = AR.review_circulation(b, AR.opening_sides(b))
    opened = [a for a in c1["answers"] if a.get("open")]
    assert [a["element"] for a in opened] == [AR.READING_ELEMENT]
    assert opened[0]["levels"] == ["L1"] and "every room of L1" in opened[0]["found"]
    res = AA.apply_answers(b, {"C1:b1": _ai("retype_room", room_type="storage")})
    assert not res[0]["ok"] and "reading problem" in res[0]["change"]


def test_a_shaft_in_a_house_that_is_walked_through_is_still_asked_about():
    """One room with no door (fewer than half unreached): the point per room stays, with its retype; a room joined to
    a reached room by a window only is offered that window as its door first."""
    b = _house()
    b["rooms"].append({"id": "x", "level_id": "L0", "room_type": "other", "polygon": _rect(10, 0, 12, 2)})
    b["rooms"].append({"id": "y", "level_id": "L1", "room_type": "other", "polygon": _rect(10, 0, 12, 5)})
    b["walls"].append({"id": "wy", "level_id": "L1", "start": [10, 0], "end": [10, 5], "thickness": 0.2})
    b["openings"].append({"id": "wn", "type": "window", "level_id": "L1", "wall_id": "wy", "center": [10, 3],
                          "width": 0.9, "height": 1.2, "sill_height": 0.9})
    walk = AR.circulation(b)
    assert walk["unreached"] == ["x", "y"] and not walk["reading_problem"]
    c1 = AR.review_circulation(b, AR.opening_sides(b))
    by = {a["element"]: a for a in c1["answers"] if a.get("open")}
    assert set(by) == {"x", "y"}
    assert [o["id"] for o in by["x"]["options"]] == ["retype_room", "keep"]
    assert [o["id"] for o in by["y"]["options"]] == ["window_to_door", "retype_room", "keep"]
    assert by["y"]["options"][0]["params"] == {"window_id": "wn"} and "the window wn" in by["y"]["found"]
    res = AA.apply_answers(b, {"C1:x": _ai("retype_room", room_type="storage"),
                               "C1:y": dict(_ai("window_to_door"), params={"window_id": "wn"})})
    assert all(r["ok"] for r in res), res
    assert AR.circulation(b)["unreached"] == ["x"]


def test_cut_links_names_the_way_and_ignores_a_stair_read_again():
    b = _house()
    after = copy.deepcopy(b)
    next(o for o in after["openings"] if o["id"] == "o1")["type"] = "window"
    cuts = AR.cut_links(b, after)
    assert [c["link"] for c in cuts] == ["o1"] and cuts[0]["rooms"] == ["k", "l"]
    assert set(cuts[0]["lost"]) == {"k", "w", "s", "st0", "st1", "h", "b1", "b2"}
    assert AR.cut_links(b, copy.deepcopy(b)) == []
    # a door taken away beside another way between the same rooms cuts nothing
    two = _house(second_way=True)
    after = copy.deepcopy(two)
    after["openings"] = [o for o in after["openings"] if o["id"] != "o1"]
    assert AR.cut_links(two, after) == []


def test_a_stair_left_out_by_an_answer_is_put_back():
    """A stair drawn as a piece links its room with the room over it on the next floor; an answer that leaves the only
    stair out (not built) would cut the upper floor off: it is undone."""
    b = _house()
    b["rooms"] = [r for r in b["rooms"] if r["id"] not in ("st0", "st1")]
    b["openings"] = [o for o in b["openings"] if o["id"] != "d4"]
    b["furniture"].append({"id": "f_st", "type": "stair", "room_id": "k", "level_id": "L0", "source": "from_documents",
                           "build": True, "footprint": {"center": [5.0, 7.0], "size": [1.0, 3.0],
                                                        "rotation_deg": 0.0}})
    assert ("f_st", "k", "b2") in AR.stair_links(b)          # it starts in the kitchen, arrives in the room over it
    assert AR.circulation(b)["unreached"] == []
    res = AA.apply_answers(b, {"AI.remove_piece:f_st": _ai("remove_piece")})
    assert not res[0]["ok"] and "f_st was the only way between" in res[0]["change"]
    stair = next(f for f in b["furniture"] if f["id"] == "f_st")
    assert stair.get("build") is True and "adjusted_by_ai" not in stair
    assert AR.circulation(b)["unreached"] == []


def _real06() -> dict:
    if not REAL06.is_file():
        pytest.skip("the latest real06 baseline is not in this checkout")
    return json.loads(REAL06.read_text(encoding="utf-8"))


def test_real06_the_kitchen_passage_stays_and_every_room_is_reached():
    """real06 (latest baseline = run 20261030-224530-full): the AI's serving hatch in o_L0_001, the only passage from
    the living room r_L0_salon to the kitchen (its stair, bathroom and store, and the upper floor beyond), is undone;
    after the architect's defaults (the dressing room's window to the master bedroom is its door) all 12 rooms are
    reached and C1 has no open point."""
    from wenart.blender import build as B

    b = _real06()
    b["architect_answers"] = {"AI.pass_through:o_L0_001": _ai("pass_through")}
    prep = B.prepare(b)
    rec = next(r for r in prep["architect"]["applied"] if r["key"] == "AI.pass_through:o_L0_001")
    assert not rec["ok"] and "o_L0_001 was the only way between r_L0_mutfak and r_L0_salon" in rec["change"]
    assert next(o for o in prep["building"]["openings"] if o["id"] == "o_L0_001")["type"] == "opening"
    walk = AR.circulation(prep["building"])
    assert walk["starts"] == ["r_L0_salon"] and walk["unreached"] == [] and len(walk["rooms"]) == 12
    c1 = next(q for q in prep["architect"]["questions"] if q["id"] == "C1")
    assert not [a for a in c1["answers"] if a.get("open")]


def test_real06_the_cut_house_reads_as_one_reading_problem():
    """The run's state (the hatch carried out): 11 of 12 rooms unreached is one reading problem, not 11 shafts, and
    the run's C1 retypes to storage are refused (r_L1_hol, r_L1_oda_2 ...)."""
    b = _real06()
    ans = {"AI.pass_through:o_L0_001": dict(_ai("pass_through"), by="user")}
    ans.update({f"C1:{r}": _ai("retype_room", room_type="storage") for r in ("r_L1_hol", "r_L1_oda_2", "r_L1_banyo")})
    res = {r["key"]: r for r in AA.apply_answers(b, AA.answers_of(b, ans))}
    assert res["AI.pass_through:o_L0_001"]["ok"]
    walk = AR.circulation(b)
    assert walk["reading_problem"] and walk["reached"] == {"r_L0_salon"} and len(walk["unreached"]) == 11
    for k in ("C1:r_L1_hol", "C1:r_L1_oda_2", "C1:r_L1_banyo"):
        assert not res[k]["ok"] and "reading problem" in res[k]["change"]
    rooms = {r["id"]: r for r in b["rooms"]}
    assert rooms["r_L1_hol"]["room_type"] == "hall" and rooms["r_L1_oda_2"]["room_type"] == "bedroom"
    c1 = AR.review_circulation(b, AR.opening_sides(b))
    assert [a["element"] for a in c1["answers"] if a.get("open")] == [AR.READING_ELEMENT]
