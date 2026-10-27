"""Doors side by side and open passages (27 Oct 2026). User on real06's dressing room: "doors next to each other not
making sense" (the AI architect made the two windows beside the door between the shower room and the dressing room
doors: three doors 2.5 cm apart); user: "Not every opening inside the house requires a door or a window" (the AI made
the open passage between the two upper halls a glazed door with a glass guard).

General rules under test: a window is the door of a room no door reaches, never a second door beside the door of two
rooms, never a door whose frame touches another (``act_window_to_door``); the model review's M12 finds doors that
crowd each other (overlapping openings, touching frames, two doors of one passage, leaves that sweep over each other)
and openings that got a leaf, glass or a guard they do not need, naming the decision that made them (Argus revokes
the AI's); two drawn doors of one passage are merged by the architect's O1; an inside gap drawn with no leaf stays an
open passage, a door only into a room that needs privacy (D6, ``act_gap_to_door``); no inside door or passage becomes
a window; no guard without a drop. CPU only; synthetic buildings, real06's trimmed fixture as the test case."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from wenart.agent import architect_ai as AIA
from wenart.agent import causes as CA
from wenart.audit import argus_ai as AX
from wenart.audit import kinds as K
from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RR
from wenart.blender import door_spacing as DS
from wenart.blender import model_review as MR

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "tests" / "fixtures" / "real06_building_20261025.json"
ANS = {"by": "ai", "answer": "test"}


def _room(rid, x0, y0, x1, y1, rtype, **kw):
    return dict({"id": rid, "level_id": "L0", "room_type": rtype,
                 "polygon": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]}, **kw)


def _wall(wid, a, b, t=0.2):
    return {"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t, "height": 2.7}


def _door(oid, wall, c, width=0.8, **kw):
    return dict({"id": oid, "type": "door", "level_id": "L0", "wall_id": wall, "center": list(c), "width": width,
                 "height": 2.1, "sill_height": None, "operation": "swing", "status": "verified",
                 "evidence": [{"file": "t.dwg", "method": "vector", "confidence": 0.95}]}, **kw)


def _window(oid, wall, c, width=0.8, **kw):
    return dict({"id": oid, "type": "window", "level_id": "L0", "wall_id": wall, "center": list(c), "width": width,
                 "height": 1.2, "sill_height": 0.9, "status": "verified",
                 "evidence": [{"file": "t.dwg", "method": "vector", "confidence": 0.9}]}, **kw)


def _gap(oid, wall, c, width=1.6, unclear=False):
    ev = {"file": "t.dwg", "method": "derived", "confidence": 0.5}
    o = {"id": oid, "type": "opening", "level_id": "L0", "wall_id": wall, "center": list(c), "width": width,
         "height": 2.1, "sill_height": None, "status": "unverified", "evidence": [ev]}
    if unclear:
        ev["note"] = "unclassified gap content: LINE:1,LINE:2"
        o["type_raw"] = "unclassified gap content"
    return o


def _building(rooms, walls, openings):
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "rooms": rooms, "walls": walls,
            "openings": openings, "furniture": []}


def dressing_and_shower():
    """A dressing room under a shower room; between them a door with a window on each side, 2.5 cm off its jambs (the
    drawing of real06's upper floor)."""
    return _building([_room("ra", 0, 0, 4, 3, "dressing"), _room("rb", 0, 3.2, 4, 6, "bathroom")],
                     [_wall("wm", (0, 3.1), (4, 3.1))],
                     [_door("d1", "wm", (2.0, 3.1), swing_side="rb"), _window("w1", "wm", (1.175, 3.1)),
                      _window("w2", "wm", (2.825, 3.1))])


def made_door(o: dict, key: str) -> dict:
    """``o`` as a decision made it a door from a window (the record ``act_window_to_door`` leaves)."""
    o.update(drawn_type=o["type"], type="door", sill_height=None, height=2.1, operation="swing",
             corrected_by_ai={"by": "architect", "answer_key": key, "answer_by": "ai", "reason": "test"})
    return o


# --------------------------------------------------------------------------------------- window_to_door refuses

def test_a_window_beside_the_door_of_two_rooms_is_never_made_a_second_door():
    b = dressing_and_shower()
    plan = AA.Plan(b)
    before = copy.deepcopy(plan.openings["w1"])
    ok, why = AA.act_window_to_door(plan, "AI.window_to_door:w1", ANS, "w1")
    assert not ok and "joined by d1 already" in why
    assert plan.openings["w1"] == before                                   # nothing changed, nothing marked


def test_a_window_whose_frame_would_touch_another_door_stays_a_window():
    b = _building([_room("ra", 0, 0, 4, 3, "hall"), _room("rb", 0, 3.2, 2.0, 6, "bathroom"),
                   _room("rc", 2.2, 3.2, 4, 6, "bedroom")],
                  [_wall("wm", (0, 3.1), (4, 3.1))],
                  [_door("d2", "wm", (2.6, 3.1), swing_side="rc"), _window("w1", "wm", (1.775, 3.1))])
    plan = AA.Plan(b)
    before = copy.deepcopy(plan.openings["w1"])
    ok, why = AA.act_window_to_door(plan, "AI.window_to_door:w1", ANS, "w1")
    assert not ok and "frames touch" in why
    assert plan.openings["w1"] == before
    # the same window a metre from that door is the bathroom's door (no door reaches it)
    b["openings"][1]["center"] = [0.8, 3.1]
    plan = AA.Plan(b)
    ok, why = AA.act_window_to_door(plan, "AI.window_to_door:w1", ANS, "w1")
    o = plan.openings["w1"]
    assert ok and o["type"] == "door" and o["drawn_type"] == "window" and o["corrected_by_ai"]["answer_key"]


# --------------------------------------------------------------------------------------- M12: doors side by side

def test_m12_finds_three_doors_side_by_side_and_names_the_decisions():
    b = dressing_and_shower()
    assert DS.conflicts(b)[0] == []                       # as drawn: one door and two windows
    for o in b["openings"]:
        if o["id"] in ("w1", "w2"):
            made_door(o, f"AI.window_to_door:{o['id']}")
    found, n = MR.doors_side_by_side(b)
    assert n == 6 and "M12" in MR.CHECKS                  # 3 doors against each other, 3 openings between rooms
    frames = {f["target"]: f for f in found if f["metrics"]["rule"] == "frames"}
    assert set(frames) == {"w1", "w2"} and all(f["severity"] == "critical" for f in frames.values())
    assert frames["w1"]["metrics"]["other"] == "d1" and frames["w1"]["metrics"]["same_rooms"]
    assert frames["w1"]["metrics"]["made_by"] == {"w1": "AI.window_to_door:w1"}
    assert "frames touch" in frames["w1"]["message"] and "0.02 m apart" in frames["w1"]["message"]
    # w1 and w2 are 0.85 m apart: more than a leaf, so no second finding for that pair (the frames name both)
    assert not any(f["metrics"]["rule"] == "same_passage" for f in found)
    assert CA.CHECK_CAUSE["M12"] == "opening_sense" and K.kind_of({"check": "M12"}) == "no_sense"


def test_doors_to_different_rooms_need_two_frames_of_wall_between_them():
    def corridor(gap):
        x = 0.4 + 0.8 + gap + 0.4
        return _building([_room("rh", 0, 0, 4, 3, "hall"), _room("r1", 0, 3.2, 1.25, 6, "bathroom"),
                          _room("r2", 1.25, 3.2, 4, 6, "wc")],
                         [_wall("wm", (0, 3.1), (4, 3.1))],
                         [_door("da", "wm", (0.8, 3.1)), _door("db", "wm", (x, 3.1))])
    assert DS.conflicts(corridor(0.15))[0] == []                  # a partition between two doors: two doors
    recs = DS.conflicts(corridor(0.05))[0]
    assert [(r["kind"], r["severity"]) for r in recs] == [("frames", "major")]
    recs = DS.conflicts(corridor(-0.10))[0]
    assert recs and recs[0]["kind"] == "overlap" and recs[0]["severity"] == "critical"


def test_two_doors_of_one_passage_closer_than_a_leaf():
    b = _building([_room("ra", 0, 0, 4, 3, "hall"), _room("rb", 0, 3.2, 4, 6, "living")],
                  [_wall("wm", (0, 3.1), (4, 3.1))],
                  [_door("da", "wm", (1.0, 3.1)), _door("db", "wm", (2.1, 3.1))])          # 0.30 m apart
    recs = DS.conflicts(b)[0]
    assert [(r["kind"], r["severity"], r["same_rooms"]) for r in recs] == [("same_passage", "major", True)]


def corner(dn_c, de_c, de_side="rh"):
    """A hall with a bathroom north and a bedroom east; a door in each wall near the inner corner."""
    return _building([_room("rh", 0, 0, 3, 3, "hall"), _room("rn", 0, 3.2, 3, 6, "bathroom"),
                      _room("re", 3.2, 0, 6, 3, "bedroom")],
                     [_wall("wn", (0, 3.1), (3.2, 3.1)), _wall("we", (3.1, 0), (3.1, 3.2))],
                     [_door("dn", "wn", (dn_c, 3.1), swing_side="rh"),
                      _door("de", "we", (3.1, de_c), swing_side=de_side)])


def test_doors_at_an_inner_corner_frames_and_leaves():
    recs = DS.conflicts(corner(2.6, 2.65))[0]                     # the frames run into each other in the corner
    assert [r["kind"] for r in recs] == ["frames"] and "corner" in recs[0]["message"]
    recs = DS.conflicts(corner(2.3, 2.3))[0]                      # clear frames, both leaves sweep the same floor
    assert [(r["kind"], r["severity"]) for r in recs] == [("swing", "major")] and recs[0]["share"] >= DS.SWING_SHARE
    assert DS.conflicts(corner(2.3, 2.3, de_side="re"))[0] == []  # one swings into the bedroom: no clash
    assert DS.conflicts(corner(1.0, 1.0))[0] == []                # far from the corner


# --------------------------------------------------------------------------------------- the fixes

def test_the_architect_merges_two_drawn_doors_of_one_passage_whose_frames_touch():
    b = _building([_room("ra", 0, 0, 4, 3, "hall"), _room("rb", 0, 3.2, 4, 6, "living")],
                  [_wall("wm", (0, 3.1), (4, 3.1))],
                  [_door("da", "wm", (1.2, 3.1)), _door("db", "wm", (2.02, 3.1))])         # 0.02 m apart
    plan = AA.Plan(b)
    o1 = next(q for q in RR.openings_rules(plan, AR.opening_sides(b)) if q["id"] == "O1")
    a = next(x for x in o1["answers"] if x["element"] == "da")
    assert a.get("open") and "one passage drawn or read twice" in a["found"]
    opt = next(x for x in a["options"] if x["choice"] == a["default"])
    assert opt["id"] == "merge_openings" and opt["params"] == {"other_id": "db"}
    ok, _why = AA.act_merge_openings(plan, "O1:da", {"by": "architect"}, "da", "db")
    assert ok and [o["id"] for o in plan.b["openings"]] == ["da"] and DS.conflicts(plan.b)[0] == []
    # a door a decision made beside a door is not merged: the decision is undone where it was made (Argus)
    b2 = dressing_and_shower()
    made_door(b2["openings"][1], "AI.window_to_door:w1")
    o1 = next(q for q in RR.openings_rules(AA.Plan(b2), AR.opening_sides(b2)) if q["id"] == "O1")
    assert not any(x.get("default", "").startswith("merge_openings") for x in o1["answers"])


def test_argus_revokes_the_ai_decision_that_made_a_door_beside_a_door(tmp_path):
    from wenart.agent import log as LG
    b = dressing_and_shower()
    made_door(b["openings"][1], "AI.window_to_door:w1")
    found, _n = MR.doors_side_by_side(b)
    rep = {"findings": [K.finding("model", f["check"], f["severity"], f["target"], f["message"],
                                  evidence={"metrics": f["metrics"]}) for f in found]}
    why = AX.door_revokes(rep)
    assert list(why) == ["AI.window_to_door:w1"] and "beside another door" in why["AI.window_to_door:w1"]
    odir = LG.orchestrator_dir(tmp_path)
    AIA._save_answers(odir, {"AI.window_to_door:w1": {"by": "ai"}, "W2:w2": {"by": "user"}})
    res = AX.revoke_decisions(tmp_path, list(why) + ["W2:w2"], why)
    assert [r["done"] for r in res] == [True, False] and "beside another door" in res[0]["why"]
    assert set(AIA._saved_answers(odir)) == {"W2:w2"}


# --------------------------------------------------------------------------------------- open passages (D6)

def hall_and(rtype, unclear=False):
    return _building([_room("rh", 0, 0, 4, 3, "hall"), _room("rx", 0, 3.2, 4, 6, rtype)],
                     [_wall("wm", (0, 3.1), (4, 3.1))], [_gap("g1", "wm", (2.0, 3.1), unclear=unclear)])


def test_an_inside_gap_stays_an_open_passage_and_never_becomes_a_window():
    for rtype in ("living", "kitchen", "hall", "dressing"):
        plan = AA.Plan(hall_and(rtype, unclear=True))
        before = copy.deepcopy(plan.openings["g1"])
        ok, why = AA.act_gap_to_door(plan, "AI.gap_to_door:g1", ANS, "g1")
        assert not ok and "stays open" in why and plan.openings["g1"] == before
        ok, why = AA.act_door_to_window(plan, "AI.door_to_window:g1", ANS, "g1")
        assert not ok and "never made a window" in why and plan.openings["g1"] == before
        ok, why = AA.act_french_window(plan, "AI.french_window:g1", ANS, "g1")
        assert not ok and "no drop" in why and "guard" not in plan.openings["g1"]


def test_a_guard_between_rooms_only_over_a_drop():
    b = hall_and("living")
    b["rooms"][1]["floor_offset_m"] = 0.6                         # a split level: 0.60 m drop at the passage
    plan = AA.Plan(b)
    ok, _why = AA.act_french_window(plan, "AI.french_window:g1", ANS, "g1")
    assert ok and plan.openings["g1"]["guard"]["top_m"] == AA.GUARD_TOP_M


def test_d6_a_door_only_where_a_room_needs_privacy_and_the_drawing_is_unclear():
    def d6_of(b):
        plan = AA.Plan(b)
        q = next(q for q in RR.passages_rule(plan, AR.opening_sides(b)))
        return q["answers"][0]
    a = d6_of(hall_and("living", unclear=True))
    assert not a.get("open") and "open passage" in a["found"] and "no room needs privacy" in a["found"]
    a = d6_of(hall_and("bedroom", unclear=False))                 # a clear empty gap: open, as drawn
    assert not a.get("open") and "empty gap" in a["found"]
    a = d6_of(hall_and("bathroom", unclear=True))                 # unclear lines into a bathroom: its door
    assert a.get("open") and a["default"] == "gap_to_door"
    b = hall_and("bathroom", unclear=True)
    plan = AA.Plan(b)
    ok, why = AA.act_gap_to_door(plan, "D6:g1", {"by": "architect"}, "g1")
    o = plan.openings["g1"]
    assert ok and o["type"] == "door" and o["operation"] == "swing" and not o.get("glazed")
    assert o["drawn_type"] == "opening" and o["privacy_door"]["rooms"] == ["rx"] and "privacy" in why
    assert DS.needless(plan.b)[0] == []                           # a door the bathroom needs


def test_m12_reports_a_leaf_glass_or_guard_a_passage_does_not_need():
    b = hall_and("living", unclear=True)
    g = b["openings"][0]
    g.update(drawn_type="opening", type="door", operation="sliding", glazed=True,
             corrected_by_ai={"by": "architect", "answer_key": "AI.gap_to_door:g1", "answer_by": "ai"},
             guard={"top_m": 1.1, "kind": "glass", "reason": "the answer to AI.french_window:g1: a French window"})
    found, _n = MR.doors_side_by_side(b)
    rules = {f["metrics"]["rule"]: f for f in found}
    assert set(rules) == {"needless_leaf", "needless_guard"}
    assert rules["needless_leaf"]["metrics"]["made_by"] == {"g1": "AI.gap_to_door:g1"}
    assert rules["needless_guard"]["metrics"]["made_by"] == {"g1": "AI.french_window:g1"}
    rep = {"findings": [K.finding("model", f["check"], f["severity"], f["target"], f["message"],
                                  evidence={"metrics": f["metrics"]}) for f in found]}
    assert set(AX.door_revokes(rep)) == {"AI.gap_to_door:g1", "AI.french_window:g1"}
    # a passage a decision made a window: glass it does not need; a serving hatch over a drawn counter is open
    b = hall_and("kitchen")
    b["openings"][0].update(drawn_type="opening", type="window", sill_height=0.9, height=1.2,
                            corrected_by_ai={"answer_key": "AI.door_to_window:g1", "by": "architect"})
    assert [r["kind"] for r in DS.needless(b)[0]] == ["needless_glass"]
    b["openings"][0]["interior_glazing"] = {"kind": "pass_through", "rooms": ["rh", "rx"]}
    assert DS.needless(b)[0] == [] and DS.open_hatch(b["openings"][0])


# --------------------------------------------------------------------------------------- real06, the test case

@pytest.fixture(scope="module")
def real06():
    b = json.loads(REAL06.read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"          # no user answers
    return b


def test_real06_the_ai_decisions_of_run_180412_are_refused_by_code(real06):
    """The decisions the AI architect took in run 20261027-180412 on the upper floor (the windows beside the shower
    room's and the bedroom's doors made doors, the halls' passage made a glazed door, glass guards between rooms) are
    refused with their reasons; the model review finds no door beside a door and no needless leaf or guard."""
    def ans(option, centre):
        return {"option": option, "params": {}, "choice": option, "by": "ai", "answer": "test",
                "where": {"kind": "opening", "level_id": "L1", "centre": centre}}
    ids = {"win_L1_004": [6.376, 9.275], "win_L1_005": [7.988, 9.275], "win_L1_008": [3.427, 10.813],
           "o_L1_002": [4.85, 9.275]}
    answers = {f"AI.window_to_door:{i}": ans("window_to_door", c) for i, c in ids.items() if i.startswith("win")}
    answers.update({f"AI.french_window:{i}": ans("french_window", c) for i, c in ids.items()})
    answers["AI.gap_to_door:o_L1_002"] = ans("gap_to_door", ids["o_L1_002"])
    prep = AIA.prep_of(copy.deepcopy(real06), None, answers)
    applied = {r["key"]: r for r in prep["architect"].get("applied") or []}
    for key in answers:
        assert applied[key]["ok"] is False, key
    assert "joined by d_L1_003 already" in applied["AI.window_to_door:win_L1_004"]["change"]
    assert "stays open" in applied["AI.gap_to_door:o_L1_002"]["change"]
    built = {o["id"]: o for o in prep["building"]["openings"]}
    assert built["win_L1_004"]["type"] == "window" and built["o_L1_002"]["type"] == "opening"
    assert not any(isinstance(built[i].get("guard"), dict) for i in ids)
    rec = MR.review(prep["building"], None, prep)
    assert rec["checks"]["M12"]["status"] == "ok" and rec["checks"]["M12"]["failed"] == 0
    d6 = next(q for q in prep["architect"]["questions"] if q["id"] == "D6")
    assert any(a["element"] == "o_L1_002" and "open passage" in a["found"] for a in d6["answers"])
