"""Audit fix round 3b (27 Nov 2026): the defects an independent review found in round 3 (R02 stale answers, R17 drawn
evidence the architect keeps), each built from the reviewer's repro (scratchpad rev/exp1-exp9), and the rules the user
added (a fallback default for a stale answer's point, unsigned machine answers retired, answers of a rule that did not
run, a gate per prepare, a door's own size tag).

1. The replay gate gives the same verdict whether or not the plan is seeded with the architect's defaults (the
   answer-free default chain decides it; the report never says "not raised" next to an open point).
2. An answer re-targeted by place acts on its target; the other elements it names are found again or it is stale.
3. R17 d holds on every path: clear_basin, and move_piece / clear_front away from a window, never move drawn fixed
   equipment (unless the user says so).
4. Each retype rule checks its own premise (the daylight premise only for a no-daylight claim; R4 the area).
5. The AI's override of a major default carries its element's signature.
Then: the fallback default (7), unsigned machine answers (8), a rule that did not run (9), the chain's cache key (10),
a gate per prepare (11), a glass hatch as window evidence (12), the same-key replacement in the AI's own plans (13), a
door's own size tag and H2's words (14).

Pure tests on small synthetic buildings and the real06 fixture of 25 Oct (about 3 s a plan)."""
import copy
import json
from pathlib import Path

import pytest

from wenart.agent import architect_ai as AI
from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RU
from wenart.blender import build as BB
from wenart.blender import door_states as DS

ROOT = Path(__file__).resolve().parents[1]
REAL06_FIXTURE = ROOT / "tests" / "fixtures" / "real06_building_20261025.json"
ARC = [{"file": "t.dwg", "method": "vector", "confidence": 0.95, "entity": "ARC:1"}]


def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _wall(wid, lid, a, b, t=0.2, **kw):
    return dict({"id": wid, "level_id": lid, "start": list(a), "end": list(b), "thickness": t}, **kw)


@pytest.fixture(scope="module")
def real06():
    if not REAL06_FIXTURE.is_file():
        pytest.skip("the real06 fixture is not here")
    b = json.loads(REAL06_FIXTURE.read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"
    return b


@pytest.fixture(scope="module")
def real06_plain(real06):
    """The real06 fixture planned with no answer (its open points carry their signatures; its defaults)."""
    return BB.prepare(copy.deepcopy(real06), "base", None)


def _point(prep, key):
    rule, _, el = key.partition(":")
    return next((a for q in prep["architect"]["questions"] if q["id"] == rule for a in q["answers"]
                 if a["element"] == el), None)


def _answer_to(point: dict, by: str = "ai", **extra) -> dict:
    """An answer to an open point as the AI architect gives it (its first change, the point's signature)."""
    opt = next((o for o in point["options"] if o["id"] != "keep"), point["options"][0])
    return dict({"option": opt["id"], "params": dict(opt.get("params") or {}), "choice": opt["choice"], "by": by,
                 "answer": "a test answer", "where": point.get("where"), "signature": point.get("signature"),
                 "date": "2026-11-27"}, **extra)


# ------------------------------------------------------------------------------------- defect 1: seeded or not

def test_defect1_the_gate_gives_the_same_verdict_whether_or_not_the_plan_is_seeded(real06, real06_plain):
    """exp2: F2:d_L1_011 and F3:o_L1_005 open only after a default ran; the AI's answers with their own signatures
    were stale on a plan not seeded with the defaults (the build on the pod) and admitted on a seeded one."""
    keys = ("F2:d_L1_011", "F3:o_L1_005")
    for k in keys:
        assert _point(real06_plain, k)["open"], k
    # the answer-free review alone does not raise them: the answer-free default chain does
    chain = BB.raised_review(real06, "base", None, None)
    assert set(keys) <= set(chain["open"])
    answers = {k: _answer_to(_point(real06_plain, k)) for k in keys}
    verdicts = {}
    for seeded in (False, True):
        b = copy.deepcopy(real06)
        b["agent_overrides"] = {"architect": copy.deepcopy(answers)}
        if seeded:
            b["architect_defaults"] = copy.deepcopy(real06_plain["architect_defaults"])
            b["architect_refused_defaults"] = copy.deepcopy(real06_plain["architect_refused_defaults"])
        prep = BB.prepare(b, "base", None)
        app = {r["key"]: r for r in prep["architect_applied"] if r["key"] in answers}
        assert set(app) == set(keys)
        verdicts[seeded] = {k: (bool(r.get("stale")), r["element"]) for k, r in app.items()}
        assert not any(r.get("stale") for r in app.values()), app
        assert set(keys) <= set(prep["architect_replay"]["admitted"])
        for k in keys:                          # the AI's answer stands: no default, no point left for the AI
            assert k not in prep["architect_defaults"] and not (_point(prep, k) or {}).get("for_ai")
    assert verdicts[False] == verdicts[True]


def test_defect1_the_build_brief_with_the_merged_answers_keeps_the_accepted_ai_answers(real06, real06_plain):
    """On the pod the Blender build's brief carries the merged answers (cli.py), so its seed key differs from the AI
    architect's and it runs unseeded: an answer the AI architect's own plan accepted is carried out in it too."""
    key = "F2:d_L1_011"
    ans = _answer_to(_point(real06_plain, key))
    b = copy.deepcopy(real06)
    ai_prep = AI.prep_of(b, None, {key: ans})
    ai_rec = next(r for r in ai_prep["architect_applied"] if r["key"] == key)
    build = BB.prepare(copy.deepcopy(real06), "base", {"architect_answers": {key: ans}})
    rec = next(r for r in build["architect_applied"] if r["key"] == key)
    assert BB.seed_key(real06, {"architect_answers": {key: ans}}) != BB.seed_key(real06, None)
    assert not ai_rec.get("stale") and not rec.get("stale") and ai_rec["element"] == rec["element"]


def test_defect1_the_report_never_says_not_raised_next_to_an_open_point():
    """A stale answer whose question waits for the AI architect is shown with why it is stale, never as 'not raised'."""
    rec = {"questions": [{"id": "F2", "answers": [{"element": "d1", "open": True, "for_ai": True,
                                                   "stale_answers": [{"id": "x1", "key": "F2:d1"}]}]}],
           "applied": [{"key": "F2:d1", "rule": "F2", "option": "move_piece", "by": "ai", "stale": True,
                        "not_raised": True, "element": "d1",
                        "old": {"id": "x1", "choice": "move_piece", "why": BB.not_raised_text("F2:d1", "d1")}}]}
    row = AR.stale_rows(rec)[0]
    assert row["new"].startswith("open: the AI architect decides again") and "not raised" not in row["why"]


# --------------------------------------------------------------------------- defect 2: re-targeted acts on target

def _two_bedrooms(swapped: bool = False) -> dict:
    """exp6: the hall h and the bedrooms b1 (west) and b2 (east), each reached by its drawn door (d1 into b1 at x 2,
    d2 into b2 at x 8); ``swapped``: a later reading that gave the two doors each other's ids."""
    lv = [{"id": "L0", "elevation": 0.0, "height": 3.0, "ceiling_height": 2.8}]
    rooms = [{"id": "h", "level_id": "L0", "room_type": "hall", "label": "HOL", "polygon": _rect(0, 0, 10, 3)},
             {"id": "b1", "level_id": "L0", "room_type": "bedroom", "label": "YATAK 1", "polygon": _rect(0, 3, 5, 7)},
             {"id": "b2", "level_id": "L0", "room_type": "bedroom", "label": "YATAK 2", "polygon": _rect(5, 3, 10, 7)}]
    walls = [_wall("w", "L0", (0, 3), (10, 3), 0.1)]

    def door(i, x):
        return {"id": i, "type": "door", "level_id": "L0", "wall_id": "w", "center": [x, 3], "width": 0.8,
                "height": 2.1, "evidence": copy.deepcopy(ARC)}
    ids = ("d2", "d1") if swapped else ("d1", "d2")
    return {"levels": lv, "rooms": rooms, "walls": walls, "openings": [door(ids[0], 2.0), door(ids[1], 8.0)],
            "furniture": []}


def test_defect2_an_answer_retargeted_by_place_acts_on_its_target():
    a = _two_bedrooms()
    sig = AA.element_signature(AA.Plan(a), "D9", "d1", "D9:d1")
    ans = {"option": "door_state", "params": {"door_id": "d1", "state": "closed"}, "by": "ai", "answer": "closed",
           "where": {"kind": "door", "level_id": "L0", "centre": [2.0, 3.0]}, "signature": sig}
    b = _two_bedrooms(swapped=True)
    chk = AA.replay_check(AA.Plan(b), "D9:d1", ans)
    assert chk["target"] == "d2" and chk["how"] == "place" and chk["stale"] is None
    assert chk["params"]["door_id"] == "d2"
    res = AA.apply_answers(b, {"D9:d1": ans})
    assert res[0]["ok"] and res[0]["element"] == "d2" and res[0]["change"].startswith("d2")
    doors = {o["id"]: o for o in b["openings"]}
    assert doors["d2"].get("open_state") == "closed" and doors["d2"]["center"] == [2.0, 3]   # the door into b1
    assert doors["d1"].get("open_state") is None                                            # the door into b2: untouched


def test_defect2_the_other_elements_an_answer_names_are_found_again_or_it_is_stale():
    a = _two_bedrooms()
    plan = AA.Plan(a)
    # a move away from d2 (another element) answered for d1, with d2's signature kept (``refs``)
    sig = AA.element_signature(plan, "F2", "d1", "F2:d1")
    sig["refs"] = AA.option_refs(plan, "F2", "d1", [{"params": {"piece_id": "d1", "away_from": "d2"}}])
    assert set(sig["refs"]) == {"d2"} and sig["refs"]["d2"]["centre"] == [8.0, 3.0]
    ans = {"option": "door_state", "params": {"door_id": "d1", "away_from": "d2"}, "by": "ai", "signature": sig,
           "where": {"kind": "door", "level_id": "L0", "centre": [2.0, 3.0]}}
    b = _two_bedrooms(swapped=True)
    chk = AA.replay_check(AA.Plan(b), "F2:d1", ans)
    assert chk["stale"] is None and chk["params"] == {"door_id": "d2", "away_from": "d1"}   # both found again by place
    # the other element gone: stale, with the reason
    gone = copy.deepcopy(b)
    gone["openings"] = [o for o in gone["openings"] if o["center"][0] < 5]
    chk = AA.replay_check(AA.Plan(gone), "F2:d1", ans)
    assert chk["stale"] and "away_from d2 is not found again" in chk["stale"]
    # no kept signature of the other element: an answer found by place cannot confirm it
    bare = dict(ans, signature={k: v for k, v in sig.items() if k != "refs"})
    chk = AA.replay_check(AA.Plan(b), "F2:d1", bare)
    assert chk["stale"] and "cannot be confirmed" in chk["stale"]
    # an answer found by its own id keeps the ids that are still in the plan
    chk = AA.replay_check(AA.Plan(a), "F2:d1", bare)
    assert chk["stale"] is None and chk["params"] == {"door_id": "d1", "away_from": "d2"}


def test_defect2_every_open_point_keeps_the_signatures_of_the_elements_its_options_name(real06_plain):
    point = _point(real06_plain, "F2:d_L1_011")
    piece = point["options"][0]["params"]["piece_id"]
    assert point["signature"]["refs"][piece]["kind"] == "piece" and "centre" in point["signature"]["refs"][piece]


# ------------------------------------------------------------------------------- defect 3: R17 d on every path

def _bathroom(drawn: bool = True) -> dict:
    levels = [{"id": "L0", "elevation": 0.0, "height": 3.0, "ceiling_height": 2.7}]
    rooms = [{"id": "w", "level_id": "L0", "room_type": "bathroom", "polygon": _rect(0, 0, 3, 2.5)}]
    walls = [_wall("ws", "L0", (0, 0), (3, 0), exterior=True), _wall("wn", "L0", (0, 2.5), (3, 2.5)),
             _wall("ww", "L0", (0, 0), (0, 2.5), exterior=True)]
    win = {"id": "o", "type": "window", "level_id": "L0", "wall_id": "ws", "center": [1.5, 0], "width": 0.8,
           "height": 1.5, "sill_height": 0.7, "evidence": [{"method": "vector", "entity": "LINE:1,LINE:2"}]}
    door = {"id": "d", "type": "door", "level_id": "L0", "wall_id": "wn", "center": [2.4, 2.5], "width": 0.8,
            "height": 2.1, "evidence": copy.deepcopy(ARC)}
    basin = {"id": "f_basin", "type": "washbasin", "level_id": "L0", "room_id": "w",
             "source": "from_documents" if drawn else "added_by_ai",
             "footprint": {"center": [1.5, 0.35], "size": [0.6, 0.45], "rotation_deg": 0.0}, "front_deg": 90.0,
             "height": 0.85}
    return {"levels": levels, "rooms": rooms, "walls": walls, "openings": [win, door], "furniture": [basin],
            "site": {}}


def test_defect3_clear_basin_never_moves_a_drawn_basin_on_any_path():
    """exp9: H2 keeps the drawn basin under its window, but the AI's own clear_basin moved it 0.46 m."""
    b = _bathroom()
    key, ans, why = AI._decision({"action": "clear_basin", "element": "f_basin", "value": "", "reason": "a window"},
                                 AA.Plan(b), b, "L0")
    assert key is None and "drawn sanitary ware is never moved" in why
    res = AA.apply_answers(b, {"AI.clear_basin:f_basin": {"option": "clear_basin", "params": {}, "by": "ai"}})
    assert res[0]["premise"] and not res[0]["ok"] and b["furniture"][0]["footprint"]["center"] == [1.5, 0.35]
    # the user's own answer still moves it (CLAUDE.md: the user decides), an added basin may move
    assert AA.premise_refusal(AA.Plan(b), "H2", "clear_basin", "f_basin", {}, {"by": "user"}) is None
    added = _bathroom(drawn=False)
    assert AA.premise_refusal(AA.Plan(added), "H2", "clear_basin", "f_basin", {}, {"by": "ai"}) is None


def test_defect3_drawn_fixed_equipment_is_never_moved_away_from_a_window():
    """exp8: a legacy move_piece away from what is now a window re-seated real06's drawn kitchen sink."""
    b = _bathroom()
    b["furniture"][0].update(type="sink_kitchen", id="f_sink")
    plan = AA.Plan(b)
    for opt in ("move_piece", "clear_front"):
        why = AA.premise_refusal(plan, "AI." + opt, opt, "f_sink", {"away_from": "o"}, {"by": "argus"})
        assert why and "never moved because of a window" in why and "(o;" in why
    # away from a door it may still move (at most 0.5 m, CLAUDE.md), and a piece that is not fixed equipment too
    assert AA.premise_refusal(plan, "F2", "move_piece", "f_sink", {"away_from": "d"}, {"by": "ai"}) is None
    b["furniture"][0]["type"] = "dresser"
    assert AA.premise_refusal(AA.Plan(b), "F3", "move_piece", "f_sink", {"away_from": "o"}, {"by": "ai"}) is None


# --------------------------------------------------------------------------- defect 4: each rule's own premise

def _small_room(area_side: float = 2.0, window: bool = True) -> dict:
    """exp7: a 'bedroom' s of 2 x ``area_side`` m with a 1.0 x 1.2 m window to the outside."""
    b = {"levels": [{"id": "L0", "elevation": 0.0, "height": 3.0, "ceiling_height": 2.8}],
         "rooms": [{"id": "h", "level_id": "L0", "room_type": "hall", "label": "HOL", "polygon": _rect(0, 0, 6, 3)},
                   {"id": "s", "level_id": "L0", "room_type": "bedroom", "label": "ODA",
                    "polygon": _rect(0, 3, area_side, 5)}],
         "walls": [_wall("wm", "L0", (0, 3), (6, 3), 0.1), _wall("wn", "L0", (0, 5), (6, 5), exterior=True)],
         "openings": [{"id": "d", "type": "door", "level_id": "L0", "wall_id": "wm", "center": [1, 3], "width": 0.8,
                       "height": 2.1, "evidence": copy.deepcopy(ARC)}],
         "furniture": []}
    if window:
        b["openings"].append({"id": "w", "type": "window", "level_id": "L0", "wall_id": "wn", "center": [1, 5],
                              "width": 1.0, "height": 1.2, "sill_height": 0.9,
                              "evidence": [{"method": "vector", "entity": "LINE:1"}]})
    return b


def test_defect4_r4_checks_the_area_not_the_daylight():
    b = _small_room()
    r4 = next(q for q in RU.rooms_rules(AA.Plan(b)) if q["id"] == "R4")
    assert next(a for a in r4["answers"] if a["element"] == "s")["open"]
    res = AA.apply_answers(b, {"R4:s": {"option": "retype_room", "params": {"room_type": "storage"}, "by": "ai",
                                        "answer": "too small for a bedroom"}})
    assert res[0]["ok"] and b["rooms"][1]["room_type"] == "storage"
    # its own premise: a bedroom of 8 m2 is not too small
    big = _small_room(area_side=4.0)
    res = AA.apply_answers(big, {"R4:s": {"option": "retype_room", "params": {"room_type": "storage"}, "by": "ai"}})
    assert res[0]["premise"] and "too small for its type is not true" in res[0]["change"]


def test_defect4_the_daylight_premise_is_only_for_a_no_daylight_claim():
    lit = _small_room(area_side=4.0)                               # 8 m2, 1.2 m2 of glass: lit
    for key, ans in (("L1:s", {}), ("AI.retype_room:s", {}),
                     ("R4:s", {"answer": "it has no window, so it is a store room"})):
        b = copy.deepcopy(lit)
        why = AA.premise_refusal(AA.Plan(b), key.partition(":")[0], "retype_room", "s", {"room_type": "storage"},
                                 dict({"by": "ai"}, **ans))
        assert why and "without daylight is not true" in why, key
    # the same storage retype of a dark room holds
    dark = _small_room(area_side=4.0, window=False)
    assert AA.premise_refusal(AA.Plan(dark), "L1", "retype_room", "s", {"room_type": "storage"}, {"by": "ai"}) is None


def test_defect4_r1_r2_r5_check_their_own_premise():
    b = _small_room(area_side=4.0)                                 # 4 x 2 m: a bedroom 2.0 m wide (R1 holds)
    plan = AA.Plan(b)
    assert AA.premise_refusal(plan, "R1", "retype_room", "s", {"room_type": "study"}, {"by": "ai"}) is None
    b["rooms"][1]["polygon"] = _rect(0, 3, 4, 5.6)                  # 2.6 m wide: R1's premise is gone
    assert "narrower than" in AA.premise_refusal(AA.Plan(b), "R1", "retype_room", "s", {"room_type": "study"},
                                                 {"by": "ai"})
    b["furniture"] = [{"id": "f_bed", "type": "bed_double", "room_id": "s", "level_id": "L0",
                       "source": "from_documents", "footprint": {"center": [2, 4.3], "size": [1.6, 2.0],
                                                                 "rotation_deg": 0.0}}]
    assert "anchor piece" in AA.premise_refusal(AA.Plan(b), "R2", "retype_room", "s", {"room_type": "study"},
                                                {"by": "ai"})
    assert "no type and no name" in AA.premise_refusal(AA.Plan(b), "R5", "retype_room", "s",
                                                       {"room_type": "office"}, {"by": "ai"})


# ------------------------------------------------------------------- defect 5: the AI's override carries the sig

def test_defect5_the_ai_override_of_a_major_default_carries_its_signature(real06):
    b = copy.deepcopy(real06)
    raw = AI.raw_review(b, None, {})
    prep = AI.prep_of(b, None, {})
    decided = AI._decided(raw, prep["architect_defaults"], set())
    assert decided and all(d.get("signature", {}).get("v") == AA.SIG_VERSION for d in decided)
    d = decided[0]
    other = next(o for o in d["options"] if o["choice"] != d["decided"])
    pick = AI._answer(other, "the AI overrides the default", "mock", d.get("where"), d)
    assert pick["signature"] == d["signature"] and pick["signature"]["key"] == d["key"]


# --------------------------------------------------------------------------------- item 7: the fallback default

def test_item7_a_stale_answers_point_gets_its_safe_default_as_the_fallback(real06):
    """A stale answer of another element (found at its old place) leaves its point to the AI architect; when no AI
    answer comes (the build after the AI session: off, out of time, ask_user) the point's safe default is carried out,
    logged as the fallback; in the AI architect's own plan the AI decides first."""
    b = copy.deepcopy(real06)
    win = next(o for o in b["openings"] if o["id"] == "win_L1_004")
    old = {"option": "interior_glazing", "by": "ai", "date": "2026-10-26", "answer": "an old decision",
           "where": {"kind": "window", "level_id": "L1", "centre": list(win["center"])}}
    prep = BB.prepare(copy.deepcopy(b), "base", {"architect_answers": {"W2:win_L1_099": old}})
    rec = next(r for r in prep["architect_applied"] if r["key"] == "W2:win_L1_099")
    assert rec["stale"] and rec["element"] == "win_L1_004" and rec["how"] == "place"
    fb = prep["architect_defaults"]["W2:win_L1_004"]
    assert fb["fallback"] and "as the fallback" in fb["answer"] and fb["fallback_for"] == [rec["old"]["id"]]
    done = next(r for r in prep["architect_applied"] if r["key"] == "W2:win_L1_004")
    assert done["ok"] and done["fallback"]
    row = next(r for r in AR.stale_rows(prep["architect"]) if r["key"] == "W2:win_L1_099")
    assert row["new"].startswith("the safe default") and "as the fallback" in row["new"]
    assert "the safe default" in AR.report_md(prep["architect"], "real06")
    # the AI architect's own plan: the point waits for the AI, the fallback it would get is recorded
    ai = AI.prep_of(copy.deepcopy(b), {"architect_answers": {"W2:win_L1_099": old}}, {})
    point = _point(ai, "W2:win_L1_004")
    assert point["open"] and point["for_ai"] and point["fallback_chain"]
    assert set(point["fallback_chain"]) <= {o["choice"] for o in point["options"]} and "default" not in point
    assert "W2:win_L1_004" not in ai["architect_defaults"]
    assert "W2:win_L1_004" in {q["key"] for q in AI.open_questions(ai["architect"], set())}


def test_item7_no_fallback_for_the_change_a_stale_answer_of_this_element_decided_against(real06, real06_plain):
    """The exception: a stale answer that named this very element (by its id) and chose otherwise than the safe
    default decided against that change; neither is carried out, the point waits (with the reason)."""
    sig = dict(_point(real06_plain, "W2:win_L1_004").get("signature") or {}, width=9.99)     # the element changed
    old = {"option": "keep", "by": "ai", "date": "2026-10-26", "signature": sig}
    prep = BB.prepare(copy.deepcopy(real06), "base", {"architect_answers": {"W2:win_L1_004": old}})
    rec = next(r for r in prep["architect_applied"] if r["key"] == "W2:win_L1_004")
    assert rec["stale"] and rec["how"] == "id" and "width" in rec["change"]
    point = _point(prep, "W2:win_L1_004")
    assert point["open"] and point["for_ai"] and "decided against" in point["fallback_withheld"]
    assert "W2:win_L1_004" not in prep["architect_defaults"]
    assert "no fallback default" in next(r for r in AR.stale_rows(prep["architect"]) if r["key"] == "W2:win_L1_004")["new"]
    # the same stale answer with the default's own choice: no contradiction, the fallback is carried out
    same = dict(old, option="move_window_to_outer_wall", choice="move_window_to_outer_wall")
    prep = BB.prepare(copy.deepcopy(real06), "base", {"architect_answers": {"W2:win_L1_004": same}})
    assert prep["architect_defaults"]["W2:win_L1_004"]["fallback"]


# ---------------------------------------------------------------------- item 8: unsigned machine answers retired

def test_item8_an_unsigned_machine_answer_is_not_replayed_by_id(real06, real06_plain):
    key = "F2:d_L1_011"
    signed = _answer_to(_point(real06_plain, key))
    unsigned = {k: v for k, v in signed.items() if k != "signature"}
    for by in ("ai", "argus", "architect"):
        prep = BB.prepare(copy.deepcopy(real06), "base", {"architect_answers": {key: dict(unsigned, by=by)}})
        rec = next(r for r in prep["architect_applied"] if r["key"] == key)
        assert rec["stale"] and rec.get("unsigned") and "carries no signature" in rec["change"], by
        assert key in prep["architect_replay"]["why"]["unsigned"]
    # the user's own answer keeps its path (no signature, no premise check)
    prep = BB.prepare(copy.deepcopy(real06), "base", {"architect_answers": {key: dict(unsigned, by="user")}})
    rec = next(r for r in prep["architect_applied"] if r["key"] == key)
    assert not rec.get("stale") and key in prep["architect_replay"]["admitted"]
    # signed, the machine answer is admitted
    prep = BB.prepare(copy.deepcopy(real06), "base", {"architect_answers": {key: signed}})
    assert key in prep["architect_replay"]["admitted"]


# --------------------------------------------------------------------------- item 9: a rule that did not run

def test_item9_an_answer_of_a_rule_that_did_not_run_is_not_carried_out_unless_it_is_the_users(real06):
    key = "A1:downpipes"                      # A1 follows with the facade kit: no question of the review
    sig = {"v": AA.SIG_VERSION, "rule": "A1", "key": key, "kind": None}
    prep = BB.prepare(copy.deepcopy(real06), "base",
                      {"architect_answers": {key: {"option": "keep", "by": "ai", "signature": sig}}})
    rec = next(r for r in prep["architect_applied"] if r["key"] == key)
    assert rec["stale"] and rec["unchecked"] and rec["change"].startswith("not applied: not checked: its rule A1")
    assert "not checked: its rule did not run" in next(r for r in AR.stale_rows(prep["architect"])
                                                         if r["key"] == key)["new"]
    prep = BB.prepare(copy.deepcopy(real06), "base", {"architect_answers": {key: {"option": "keep", "by": "user"}}})
    rec = next(r for r in prep["architect_applied"] if r["key"] == key)
    assert rec["ok"] and not rec.get("stale")


# ------------------------------------------------------------------------------ item 10: the chain's cache key

def test_item10_the_chain_key_drops_only_the_architect_answers_of_the_agent_overrides():
    base = {"levels": [], "agent_overrides": {"architect": {"W2:x": {"option": "keep"}}}}
    same = dict(base, agent_overrides={"architect": {"W2:y": {"option": "keep"}}})
    roof = dict(base, agent_overrides={"architect": {}, "roof": {"pitch_deg": 30}})
    assert BB.raised_key(base, None, "base", None) == BB.raised_key(same, None, "base", None)
    assert BB.raised_key(base, None, "base", None) != BB.raised_key(roof, None, "base", None)


# ---------------------------------------------------------------------------------- item 11: a gate per prepare

def test_item11_a_planned_building_never_hands_its_old_gate_to_a_later_prepare(real06, real06_plain):
    key = "F2:d_L1_011"
    first = BB.prepare(copy.deepcopy(real06), "base", {"architect_answers": {key: _answer_to(_point(real06_plain,
                                                                                                    key))}})
    assert "architect_replay" not in first["building"] and first["architect_replay"]["admitted"]
    # a building that still carries a gate (an older building_built.json): a new answer is gated, not carried out
    built = dict(copy.deepcopy(real06), architect_replay=first["architect_replay"])
    new = {"option": "interior_glazing", "by": "ai", "where": None}
    prep = BB.prepare(built, "base", {"architect_answers": {"W2:win_L1_004": new}})
    rec = next(r for r in prep["architect_applied"] if r["key"] == "W2:win_L1_004")
    assert rec["stale"] and rec.get("unsigned") and "W2:win_L1_004" in prep["architect_replay"]["keys"]
    # and apply_answers given a gate that never saw an answer does not carry it out
    b = _two_bedrooms()
    res = AA.apply_answers(b, {"D9:d1": {"option": "door_state", "params": {"state": "closed"}, "by": "ai"}},
                           replay={"admitted": {}, "stale": {}})
    assert res[0]["stale"] and "not checked by this plan's replay gate" in res[0]["change"]


# ------------------------------------------------------------------------------ item 12: a glass hatch is evidence

def test_item12_a_glass_hatch_is_window_evidence():
    hatch = {"type": "window", "evidence": [{"method": "vector", "entity": "HATCH:5C", "layer": "0",
                                             "note": "glass hatch in the gap"}]}
    assert AA.window_evidence(hatch)
    assert AA.window_evidence({"type": "window", "evidence": [{"method": "vector", "entity": "gap:HATCH:5C",
                                                               "note": "unclassified gap content: HATCH:5C"}]}) is None


# --------------------------------------------------------------- item 13: the same-key replacement, AI session too

def test_item13_the_ai_replacement_of_a_stale_user_answer_wins_in_the_ai_architects_plan_too():
    user = {"option": "keep", "answer": "keep it", "by": "user", "date": "2026-10-25"}
    old = AA.stale_summary("W2:w", AA.normalise("W2:w", user), "moved", "w")
    ai = {"option": "interior_glazing", "by": "ai", "replaces": [old]}
    b = {"agent_overrides": {"architect": {"W2:w": ai}}}
    assert AA.answers_of(b, {"W2:w": user})["W2:w"]["by"] == "ai"
    assert AA.answers_of(b, {"W2:w": dict(user, answer="another answer")})["W2:w"]["by"] == "user"
    assert AA.merge_user_answers({"W2:w": ai}, {"W2:w": user})["W2:w"]["by"] == "ai"


# -------------------------------------------------------------------- item 14: a door's own tag, H2's words

def test_item14_a_door_is_built_at_its_own_tags_height():
    b = {"openings": [{"id": "d1", "type": "door", "width": 0.8, "height": 2.1, "assumed": ["height"],
                       "door_tags": ["K1-80/230"], "evidence": []},
                      {"id": "d2", "type": "door", "width": 0.9, "height": 2.2, "door_tags": ["K2-90/210"],
                       "evidence": []},
                      {"id": "d3", "type": "door", "width": 0.8, "height": 2.1, "assumed": ["height"],
                       "door_tags": ["K1-80/210"], "evidence": []}]}
    got = DS.tag_heights(b)
    d1, d2, d3 = b["openings"]
    assert [g["object"] for g in got] == ["d1"] and d1["height"] == pytest.approx(2.3)
    assert d1["drawn_height"] == pytest.approx(2.1) and "height" not in d1["assumed"] and "K1-80/230" in d1["height_source"]
    assert d2["height"] == pytest.approx(2.2) and d3["height"] == pytest.approx(2.1)        # drawn / the same: kept
    assert DS.tag_heights(b) == []                                                          # once


def test_item14_h2_never_says_drawn_heights_for_an_assumed_sill():
    b = _bathroom()
    o = b["openings"][0]
    o.update(assumed=["sill_height", "height"], sill_height=0.9, height=0.6)        # too short to raise to 1.2 m
    q = next(q for q in RU.furniture_rules(AA.Plan(b), AR.opening_sides(b)) if q["id"] == "H2")
    found = next(a for a in q["answers"] if a["element"] == "f_basin")["found"]
    assert "drawn" not in found.split("stays under")[1] and "too short to raise" in found
    drawn = _bathroom()
    q = next(q for q in RU.furniture_rules(AA.Plan(drawn), AR.opening_sides(drawn)) if q["id"] == "H2")
    assert "the documents give its heights" in next(a for a in q["answers"] if a["element"] == "f_basin")["found"]
