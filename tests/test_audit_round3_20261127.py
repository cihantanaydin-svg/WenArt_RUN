"""Audit fix round 3 (27 Nov 2026): two building-stage rules about the architect.

R02 (critical, lesson UL396): an architect answer from an earlier reading is carried out only while its question is
raised again for the element it resolves to and that element is the one it was given for (its signature). real06
replayed 112 answers of 25-30 Oct and real10 317 of 2 Nov on readings of 26 Nov, re-targeted by place: a guard across
the balcony doors, a balcony door made a window, rooms retyped as storage. A stale answer is not carried out, it is
logged and shown in the report with the new decision, and the AI architect decides again; the user is not asked again.
Premise checks guard door_to_window, french_window, move_window and retype_room; the walk check counts the loss of the
only door onto an outdoor space.

R17 (major): architect fixes never undo drawn evidence: a drawn door is never made a window or a hatch (the equipment
yields: a misread duplicate counter is not built, a counter run is trimmed), the walk check compares each floor on its
own, W2 moves no window without window evidence (it is read again as a passage), H2 raises an assumed sill before it
moves a basin and never moves drawn sanitary ware for a window, D5 keeps a tagged door's size, D6 makes no privacy door
into a room another door reaches.

Pure tests on small synthetic buildings; the real06 / real10 replays read the project afresh (CPU) and use the stored
answers of the latest runs (skipped without them)."""
import copy
import json
import os
from pathlib import Path

import pytest

from wenart.agent import architect_ai as AI
from wenart.blender import architect as AR
from wenart.blender import architect_actions as AA
from wenart.blender import architect_rules as RU
from wenart.blender import build as BB
from wenart.blender import door_states as DS

ROOT = Path(__file__).resolve().parents[1]
PROJECTS = ROOT / "projects"
RUNS = Path(os.environ.get("WENART_RUNS") or "/home/user/WenArt_RUN/runs")
REAL06_FIXTURE = ROOT / "tests" / "fixtures" / "real06_building_20261025.json"


def _rect(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _wall(wid, lid, a, b, t=0.2, **kw):
    return dict({"id": wid, "level_id": lid, "start": list(a), "end": list(b), "thickness": t}, **kw)


def _op(oid, kind, lid, wid, c, width=0.9, **kw):
    out = {"id": oid, "type": kind, "level_id": lid, "wall_id": wid, "center": list(c), "width": width,
           "height": 2.1 if kind != "window" else 1.2}
    if kind == "window":
        out["sill_height"] = 0.9
    out.update(kw)
    return out


ARC = [{"file": "t.dwg", "method": "vector", "confidence": 0.95, "entity": "ARC:1,LINE:2"}]


def _ai(option, **params):
    return {"option": option, "params": params, "by": "ai", "answer": "a test answer"}


def _upper_flat(balcony: bool = True) -> dict:
    """L0 (the ground floor: the hall g with the entrance) and L1 3 m over it: the bedroom r (0-6 x 0-4) with its
    balcony door d_new (0.8 m, drawn swing) in the south wall onto the outdoor space os_bal (x 4-6, y -1.5-0) at its
    floor, a window w1 in the same wall, the hall h north of it (door d_h)."""
    levels = [{"id": "L0", "elevation": 0.0, "height": 3.0, "ceiling_height": 2.8},
              {"id": "L1", "elevation": 3.0, "height": 3.0, "ceiling_height": 2.8}]
    rooms = [{"id": "g", "level_id": "L0", "room_type": "hall", "label": "HOL", "polygon": _rect(0, 0, 6, 7)},
             {"id": "r", "level_id": "L1", "room_type": "bedroom", "label": "YATAK ODASI", "polygon": _rect(0, 0, 6, 4)},
             {"id": "h", "level_id": "L1", "room_type": "hall", "label": "HOL", "polygon": _rect(0, 4, 6, 7)}]
    walls = [_wall("ws0", "L0", (0, 0), (6, 0), exterior=True), _wall("ws1", "L1", (0, 0), (6, 0), exterior=True),
             _wall("wn1", "L1", (0, 4), (6, 4)), _wall("we1", "L1", (6, 0), (6, 7), exterior=True)]
    openings = [_op("d0", "door", "L0", "ws0", (3, 0), evidence=copy.deepcopy(ARC)),
                _op("d_new", "door", "L1", "ws1", (5, 0), 0.8, evidence=copy.deepcopy(ARC), operation="swing"),
                _op("w1", "window", "L1", "ws1", (1.5, 0), 1.2, evidence=[{"method": "vector", "entity": "LINE:9,LINE:10"}]),
                _op("d_h", "door", "L1", "wn1", (2, 4), evidence=copy.deepcopy(ARC))]
    site = {"entrances": [{"door_id": "d0", "level_id": "L0", "main": True}]}
    if balcony:
        site["outdoor_spaces"] = [{"id": "os_bal", "level_id": "L1", "kind": "balcony", "z": 3.0,
                                   "polygon": _rect(4, -1.5, 6, 0), "doors": ["d_new"]}]
    return {"levels": levels, "rooms": rooms, "walls": walls, "openings": openings, "furniture": [], "site": site}


def _by_id(b):
    return {o["id"]: o for o in b["openings"]}


# ------------------------------------------------------------------------------------------------ R02 signatures

def test_r02_the_signature_names_the_element_and_tells_another_one_apart():
    b = _upper_flat()
    plan = AA.Plan(b)
    sig = AA.element_signature(plan, "E1", "d_new")
    assert sig["kind"] == "door" and sig["level"] == "L1" and sig["width"] == pytest.approx(0.8)
    assert sig["wall_deg"] == pytest.approx(0.0) and sig["out_deg"] == pytest.approx(270.0)
    assert sig["sides"] == ["bedroom|yatak odasi", "outside"] and sig["outside"] == "balcony"
    assert AA.signature_diff(sig, AA.element_signature(plan, "E1", "d_new")) == []
    # the same rule on another element: width, rooms and what lies outside differ
    other = AA.element_signature(plan, "E1", "d_h")
    diff = AA.signature_diff(sig, other)
    assert any("width" in d for d in diff) or any("rooms on its sides" in d for d in diff)
    assert any("an outer opening -> an inside one" in d for d in diff)
    # a room: its drawn type, label and area
    room = AA.element_signature(plan, "L1", "r")
    assert room["room"] == "bedroom|yatak odasi" and room["area"] == pytest.approx(24.0)
    # drawn values: an answer that changed the door keeps its signature
    d = _by_id(b)["d_new"]
    AA._keep_drawn(d, "type", "width")
    d["type"], d["width"] = "window", 1.6
    assert AA.signature_diff(sig, AA.element_signature(AA.Plan(b), "E1", "d_new")) == []


def test_r02_an_element_found_again_by_place_is_by_id_when_it_is_the_named_one():
    b = _upper_flat()
    plan = AA.Plan(b)
    assert AA.resolve_how(plan, "d_new", {"kind": "door", "level_id": "L1", "centre": [5.2, 0.0]}) == ("d_new", "id")
    # the id moved between readings: the door at the old place is another element ("place")
    assert AA.resolve_how(plan, "d_old", {"kind": "door", "level_id": "L1", "centre": [5.2, 0.0]}) == \
        ("d_new", "place")
    # a room whose outline (and so its centre) changed is still found by id
    assert AA.resolve_how(plan, "r", {"kind": "room", "level_id": "L1", "centre": [1.0, 1.0]}) == ("r", "id")
    assert AA.resolve_how(plan, "nothing", {"kind": "window", "level_id": "L1", "centre": [9, 9]}) == (None, None)


def test_r02_a_door_to_window_answer_whose_place_now_holds_a_balcony_door_is_stale_and_the_door_stays():
    """The plan's unit test: a re-read with shifted ids, plus a stored door_to_window answer whose 'where' now lands
    on a door opening onto a balcony: not applied, reported stale, the door stays a door."""
    b = _upper_flat()
    old = dict(_ai("door_to_window"), date="2026-11-02",
               where={"kind": "door", "level_id": "L1", "centre": [5.0, 0.02]})
    res = AA.apply_answers(b, {"E1:d_L1_024": old})
    rec = res[0]
    assert rec["stale"] and not rec["ok"] and rec["element"] == "d_new"
    assert rec["change"].startswith("stale: not applied") and "no signature" in rec["change"]
    assert rec["old"]["choice"] == "door_to_window" and rec["old"]["date"] == "2026-11-02"
    assert _by_id(b)["d_new"]["type"] == "door"
    # an answer with a signature taken where nothing lay outside: the element now lands on the balcony: stale
    bare = _upper_flat(balcony=False)
    signed = dict(old, signature=AA.element_signature(AA.Plan(bare), "E1", "d_new", "E1:d_new"))
    res = AA.apply_answers(b, {"E1:d_new": signed})
    assert res[0]["stale"] and "outside air -> balcony" in res[0]["change"]
    # this reading's own answer (its signature matches): the premise check refuses it, the door stays a door
    fresh = dict(old, signature=AA.element_signature(AA.Plan(b), "E1", "d_new", "E1:d_new"))
    res = AA.apply_answers(b, {"E1:d_new": fresh})
    assert res[0]["premise"] and not res[0]["ok"] and _by_id(b)["d_new"]["type"] == "door"
    assert "drawn door" in res[0]["change"] or "balcony os_bal" in res[0]["change"]


def test_r02_a_french_window_answer_from_another_wall_or_width_is_stale():
    b = _upper_flat()
    plan = AA.Plan(b)
    sig = AA.element_signature(plan, "AI.french_window", "d_new")
    wide = dict(sig, width=1.98)
    turned = dict(sig, wall_deg=90.0)
    for s in (wide, turned):
        res = AA.apply_answers(copy.deepcopy(b), {"AI.french_window:d_new": dict(_ai("french_window"), signature=s)})
        assert res[0]["stale"], res[0]
        assert "width 1.98 -> 0.80" in res[0]["change"] or "host wall direction 90 -> 0" in res[0]["change"]
    # the right element, but a balcony at its floor: no drop, no guard (the premise)
    res = AA.apply_answers(b, {"AI.french_window:d_new": dict(_ai("french_window"), signature=sig)})
    assert res[0]["premise"] and "no drop, no guard" in res[0]["change"] and not _by_id(b)["d_new"].get("guard")


def test_r02_a_storage_retype_whose_no_window_premise_is_false_is_not_carried_out():
    b = _upper_flat()
    b["rooms"][1]["room_type"] = "living"
    w = _by_id(b)["w1"]
    w.update(width=2.10, height=1.30, sill_height=0.9)                  # 2.73 m2 of glass for a 24 m2 room
    for key in ("L1:r", "AI.retype_room:r"):
        res = AA.apply_answers(b, {key: _ai("retype_room", room_type="storage")})
        assert res[0]["premise"] and "glass to the outside" in res[0]["change"], res[0]
        assert b["rooms"][1]["room_type"] == "living"
    # without its window the premise holds: the retype is carried out
    dark = copy.deepcopy(b)
    dark["openings"] = [o for o in dark["openings"] if o["id"] != "w1"]
    res = AA.apply_answers(dark, {"L1:r": _ai("retype_room", room_type="storage")})
    assert res[0]["ok"] and dark["rooms"][1]["room_type"] == "storage"


def test_r02_a_bedroom_retype_needs_a_drawn_bed_where_the_room_holds_drawn_pieces():
    """real06: an old decision made the dressing room with its two drawn wardrobes a bedroom 'for its double bed'."""
    b = _upper_flat()
    b["rooms"][1].update(room_type="other", label="SOYUNMA ODASI")
    b["furniture"] = [{"id": "f_w1", "type": "wardrobe", "level_id": "L1", "room_id": "r", "source": "from_documents",
                       "footprint": {"center": [1, 3.5], "size": [1.2, 0.6], "rotation_deg": 0.0}}]
    res = AA.apply_answers(b, {"AI.retype_room:r": _ai("retype_room", room_type="bedroom")})
    assert res[0]["premise"] and "no bed" in res[0]["change"] and b["rooms"][1]["room_type"] == "other"
    # a room with no drawn piece may be retyped (it is furnished for its new type)
    b["furniture"] = []
    res = AA.apply_answers(b, {"AI.retype_room:r": _ai("retype_room", room_type="bedroom")})
    assert res[0]["ok"] and b["rooms"][1]["room_type"] == "bedroom"


def test_e1_a_door_with_an_assumed_sill_lands_on_the_balcony_at_its_threshold():
    """real11: twelve tagged 2.40 m balcony doors carried an assumed 0.90 m sill; E1 found nothing to step onto and the
    old default made them windows."""
    b = _upper_flat()
    d = _by_id(b)["d_new"]
    d.update(sill_height=0.9, assumed=["sill_height"], threshold_z=3.0)
    rect = _rect(0, 0, 6, 7)
    prep = {"ground_outline": rect, "outlines": {"L0": rect, "L1": rect}, "site": {"platforms": []}}
    lands = {g["rec"]["opening"]["id"]: g["lands"] for g in AR.outer_gaps(b, prep)}
    assert lands["d_new"] == "the balcony os_bal"
    d["assumed"] = []                                   # a sill the documents draw: 0.9 m over the balcony
    assert {g["rec"]["opening"]["id"]: g["lands"] for g in AR.outer_gaps(b, prep)}["d_new"] is None


def test_r02_losing_the_only_door_onto_an_outdoor_space_is_a_walk_cut():
    b = _upper_flat()
    assert AA.space_ways(b) == {"os_bal": ["d_new"]}
    snap = AA.walk_snapshot(b)
    d = _by_id(b)["d_new"]
    d["type"], d["sill_height"] = "window", 0.9
    why = AA.walk_cut(b, snap)
    assert why and "d_new was the only way onto the outdoor space os_bal" in why
    assert AA.lost_spaces(AA.walk_before(b, snap), b)


def test_r02_the_user_answer_replaced_by_the_ai_decision_gives_way_and_the_user_file_stays():
    user = {"W2:w9": {"option": "move_window_to_outer_wall", "answer": "outside", "by": "user", "date": "2026-10-25",
                      "where": {"kind": "window", "level_id": "L0", "centre": [1, 1]}}}
    old = AA.stale_summary("W2:w9", AA.normalise("W2:w9", user["W2:w9"]), "moved", "w3")
    ai = {"W2:w9": dict(_ai("interior_glazing"), replaces=[old])}
    assert AA.merge_user_answers(ai, user)["W2:w9"]["by"] == "ai"
    # any other user answer wins as before
    other = {"W2:w9": dict(user["W2:w9"], answer="something else")}
    assert AA.merge_user_answers(ai, other)["W2:w9"]["by"] == "user"


# ------------------------------------------------------------------------------- R02 the replay gate (build.prepare)

@pytest.fixture(scope="module")
def real06_fixture():
    if not REAL06_FIXTURE.is_file():
        pytest.skip("the real06 fixture is not here")
    b = json.loads(REAL06_FIXTURE.read_text(encoding="utf-8"))
    b["project"]["source_folder"] = "projects/no_such_project"
    return b


def test_r02_an_answer_is_carried_out_only_while_its_question_is_raised_and_a_stale_one_goes_to_the_ai(real06_fixture):
    b = copy.deepcopy(real06_fixture)
    first = BB.prepare(copy.deepcopy(b), "base", None)
    still = [a for q in first["architect"]["questions"] for a in q["answers"] if a.get("open")]
    assert still and all(a.get("signature", {}).get("v") == AA.SIG_VERSION for a in still)   # each carries its signature
    win = next(o for o in b["openings"] if o["id"] == "win_L1_004")
    plan = AA.Plan(b)
    answers = {
        # raised: the AI's keep (signed: round 3b, item 8) is carried out (the point closes, no default)
        "W2:win_L1_008": dict(_ai("keep"), where={"kind": "window", "level_id": "L1",
                                                   "centre": next(o for o in b["openings"]
                                                                  if o["id"] == "win_L1_008")["center"]},
                              signature=AA.element_signature(plan, "W2", "win_L1_008", "W2:win_L1_008")),
        # an answer for a question this reading does not raise for its room: stale
        "C1:r_L1_banyo": dict(_ai("retype_room", room_type="storage"), date="2026-10-30",
                              signature=AA.element_signature(plan, "C1", "r_L1_banyo", "C1:r_L1_banyo")),
        # an old id at win_L1_004's place, no signature: stale, the point goes to the AI architect
        "W2:win_L1_099": dict(_ai("interior_glazing"), date="2026-10-26",
                              where={"kind": "window", "level_id": "L1", "centre": list(win["center"])}),
    }
    prep = BB.prepare(copy.deepcopy(b), "base", {"architect_answers": answers})
    app = {r["key"]: r for r in prep["architect_applied"]}
    assert set(answers) <= set(app)                                        # 27 Nov 2026 (round 3b): presence first
    assert app["W2:win_L1_008"]["ok"] and not app["W2:win_L1_008"].get("stale")
    assert app["C1:r_L1_banyo"]["stale"] and "not raised" in app["C1:r_L1_banyo"]["change"]
    assert app["W2:win_L1_099"]["stale"] and app["W2:win_L1_099"]["element"] == "win_L1_004"
    assert prep["architect"]["stale"] == 2
    assert prep["architect_replay"]["admitted"].get("W2:win_L1_008") == "win_L1_008"
    # round 3b (item 7): the stale answer named another element (found at its old place): when no AI answer comes, the
    # build carries out the point's safe default as the fallback, logged as such (here W2's next safe fix closes it)
    fb = prep["architect_defaults"]["W2:win_L1_004"]
    assert fb["fallback"] and fb["fallback_for"] == [app["W2:win_L1_099"]["old"]["id"]]
    done = next(r for r in prep["architect_applied"] if r["key"] == "W2:win_L1_004")
    assert done["ok"] and done["fallback"] and done["option"] == fb["option"]
    assert "win_L1_004" not in {o["id"] for o in prep["building"]["openings"]} or fb["option"] != "close_window"
    md = AR.report_md(prep["architect"], "real06")
    assert "## Stale answers (not carried out)" in md and "`W2:win_L1_099`" in md
    assert "as the fallback (W2:win_L1_004" in md
    # in the AI architect's own plan the point waits for the AI (no fallback there), the user is not asked
    ai = AI.prep_of(copy.deepcopy(b), {"architect_answers": answers}, {})
    point = next(a for q in ai["architect"]["questions"] if q["id"] == "W2" for a in q["answers"]
                 if a["element"] == "win_L1_004")
    assert point["open"] and point["for_ai"] and point["stale_answers"][0]["key"] == "W2:win_L1_099"
    assert "W2:win_L1_004" not in ai["architect_defaults"]
    qs = AI.open_questions(ai["architect"], {"W2:win_L1_004"})
    q = next(x for x in qs if x["key"] == "W2:win_L1_004")
    assert q["stale_answers"] and q["signature"]["kind"] == "window"
    assert "earlier_answer_stale" in AI.prompt([q], ai["building"], AA.Plan(ai["building"]))
    md = AR.report_md(ai["architect"], "real06")
    assert "open: the AI architect decides again (W2:win_L1_004)" in md
    questions = md.split("## The architect's questions for you")[1].split("## ")[0] \
        if "## The architect's questions for you" in md else ""
    assert "W2:win_L1_004" not in questions
    prep = ai
    # the AI's new decision replaces it: carried out, old and new side by side in the report and the log
    pick = AI._answer(next(o for o in q["options"] if o["id"] != "keep"), "decided again", "mock", q.get("where"), q)
    assert pick["signature"] == q["signature"] and pick["replaces"][0]["key"] == "W2:win_L1_099"
    accepted = {"W2:win_L1_099": answers["W2:win_L1_099"], "W2:win_L1_004": pick}
    assert AI.drop_replaced(accepted, pick) == ["W2:win_L1_099"] and set(accepted) == {"W2:win_L1_004"}
    kept = {k: v for k, v in answers.items() if k != "W2:win_L1_099"}       # the replaced answer left the AI's file
    again = BB.prepare(copy.deepcopy(b), "base", {"architect_answers": dict(kept, **accepted)})
    rows = AR.stale_rows(again["architect"])
    row = next(r for r in rows if r["key"] == "W2:win_L1_099")
    assert row["old"] == "interior_glazing" and pick["option"] in row["new"] and "W2:win_L1_004" in row["new"]
    log = AI.stale_log(AI.stale_records(prep["architect"]), accepted, again["architect"])
    assert next(r for r in log if r["key"] == "W2:win_L1_099")["new_key"] == "W2:win_L1_004"
    assert "## Stale answers decided again" in "\n".join(AI.stale_md(log))


def test_r02_the_ai_own_decision_carries_its_signature_and_obeys_the_premise_checks():
    b = _upper_flat()
    plan = AA.Plan(b)
    key, ans, why = AI._decision({"action": "door_to_window", "element": "d_new", "value": "", "reason": "x"}, plan, b,
                                 "L1")
    assert key is None and ("drawn door" in why or "balcony" in why)
    key, ans, why = AI._decision({"action": "raise_sill", "element": "w1", "value": "", "reason": "x"}, plan, b, "L1")
    assert key == "AI.raise_sill:w1" and ans["signature"]["kind"] == "window"


# ------------------------------------------------------------------------------------- R17 a: drawn doors stay doors

def test_r17_what_makes_a_door_drawn():
    assert AA.drawn_door_evidence({"type": "door", "evidence": ARC}) == "its drawn swing arc"
    assert AA.drawn_door_evidence({"type": "door", "evidence": [{"method": "vector", "entity": "INSERT:19D/2"}]})
    leaves = {"type": "door", "evidence": [{"method": "vector", "entity": "LINE:1,LINE:2", "layer": "KAPI",
                                            "door_layer": True, "note": "6 leaf/leaves drawn parallel to the wall"}]}
    assert "door layer" in AA.drawn_door_evidence(leaves)
    tag = {"type": "door", "evidence": [{"rule": "size_tag", "text": "K1-80/210"}]}
    assert "K1-80/210" in AA.drawn_door_evidence(tag) and AA.door_tag(tag) == (0.8, 2.1, "K1-80/210")
    assert AA.drawn_door_evidence({"type": "door", "operation_source": "block_name", "evidence": []})
    for not_drawn in ({"type": "opening", "evidence": ARC},
                      # a swing side the reading set for a door read from lines is no drawn swing
                      {"type": "door", "swing_side": "r", "operation": "swing", "operation_source": "geometry",
                       "evidence": [{"entity": "LINE:3"}]},
                      {"type": "door", "lift_door": True, "evidence": ARC},
                      {"type": "door", "evidence": [{"rule": "inferred_door", "entity": "ARC:9"}]},
                      {"type": "door", "evidence": [{"note": "unclassified gap content: ARC:1", "entity": "ARC:1"}]},
                      {"type": "door", "operation": "sliding", "operation_source": "geometry",
                       "evidence": [{"entity": "LINE:1", "note": "2 leaf/leaves drawn parallel to the wall"}]}):
        assert AA.drawn_door_evidence(not_drawn) is None, not_drawn


def _kitchen(duplicate: bool = False) -> dict:
    """The kitchen k (0-5 x 0-4, the entrance d0 in its south wall) and north of it the stair hall s (0-5 x 4-7,
    'MERDIVEN'), joined only by the drawn door d (0.9 m, swing arc) at x 1.0 in the wall at y 4. A drawn counter run
    f_run (0.6 m deep) stands along that wall from x 0.2 with the drawn sink and stove in it; ``duplicate``: a second
    'counter' f_dup 0.34 m off the wall in front of the drawn appliances (read from the counter's front line)."""
    levels = [{"id": "L0", "elevation": 0.0, "height": 3.0, "ceiling_height": 2.8}]
    rooms = [{"id": "k", "level_id": "L0", "room_type": "kitchen", "label": "MUTFAK", "polygon": _rect(0, 0, 5, 4)},
             {"id": "s", "level_id": "L0", "room_type": "hall", "label": "MERDIVEN HOLU", "polygon": _rect(0, 4, 5, 7)}]
    walls = [_wall("wk", "L0", (0, 4), (5, 4)), _wall("ws", "L0", (0, 0), (5, 0), exterior=True)]
    openings = [_op("d0", "door", "L0", "ws", (4, 0), evidence=copy.deepcopy(ARC)),
                _op("d", "door", "L0", "wk", (1.0, 4), 0.9, evidence=copy.deepcopy(ARC), operation="swing",
                    swing_side="k")]

    def piece(fid, ftype, cx, cy, sx, sy, **kw):
        return dict({"id": fid, "type": ftype, "level_id": "L0", "room_id": "k", "source": "from_documents",
                     "footprint": {"center": [cx, cy], "size": [sx, sy], "rotation_deg": 0.0}, "height": 0.9,
                     "front_deg": 270.0}, **kw)
    furniture = [piece("f_sink", "sink_kitchen", 2.9, 3.6, 0.8, 0.6), piece("f_stove", "stove", 3.9, 3.6, 0.6, 0.6)]
    if duplicate:
        furniture.append(piece("f_dup", "kitchen_counter", 2.55, 3.32, 4.3, 0.48))
    else:
        furniture.append(piece("f_run", "kitchen_counter", 2.45, 3.6, 4.5, 0.6))
    return {"levels": levels, "rooms": rooms, "walls": walls, "openings": openings, "furniture": furniture,
            "site": {"entrances": [{"door_id": "d0", "level_id": "L0", "main": True}]}}


def _f2(b, element):
    q = next(q for q in RU.furniture_rules(AA.Plan(b), AR.opening_sides(b)) if q["id"] == "F2")
    return next((a for a in q["answers"] if a["element"] == element), None)


def test_r17_a_drawn_door_blocked_by_a_counter_run_stays_a_door_and_the_counter_is_trimmed():
    """The plan's unit test: a drawn door beside a kitchen run, the only link to a stair hall: the door stays, the
    counter is trimmed, every room stays reachable on its floor."""
    b = _kitchen()
    a = _f2(b, "d")
    assert a is not None and a.get("open"), a
    ids = [o["id"] for o in a["options"]]
    assert "pass_through" not in ids and ids[0] == "trim_piece" and a["default"] == "trim_piece"
    before = AR.circulation(b)["reached"]
    res = AA.apply_answers(b, {"F2:d": {"option": "trim_piece", "params": {"piece_id": "f_run", "door_id": "d"},
                                        "by": "architect", "answer": "the safe default"}})
    assert res[0]["ok"], res[0]
    run = next(f for f in b["furniture"] if f["id"] == "f_run")
    x0 = run["footprint"]["center"][0] - run["footprint"]["size"][0] / 2.0
    assert x0 >= 1.45 and run["footprint"]["size"][0] < 4.5 and run["drawn_footprint"]["size"][0] == 4.5
    assert run["footprint"]["center"][0] + run["footprint"]["size"][0] / 2.0 >= 4.2 - 1e-6   # the stove kept
    assert run["adjusted_by_ai"]["answer_key"] == "F2:d"
    assert _by_id(b)["d"]["type"] == "door" and AR.circulation(b)["reached"] == before
    # an AI answer that makes the drawn door a hatch is refused (the premise), whatever the walk check says
    res = AA.apply_answers(_kitchen(), {"AI.pass_through:d": _ai("pass_through")})
    assert res[0]["premise"] and "drawn door" in res[0]["change"]


def test_r17_a_misread_duplicate_counter_is_not_built():
    b = _kitchen(duplicate=True)
    dup = next(f for f in b["furniture"] if f["id"] == "f_dup")
    why = AA.counter_duplicate(AA.Plan(b), dup)
    assert why and "0.34 m off wk" in why and "f_stove (stove)" in why
    a = _f2(b, "d")
    assert a["options"][0]["id"] == "remove_piece" and a["options"][0]["params"]["why"] == why
    res = AA.apply_answers(b, {"F2:d": {"option": "remove_piece", "params": dict(a["options"][0]["params"]),
                                        "by": "architect"}})
    assert res[0]["ok"] and dup["build"] is False and "misread duplicate" in dup["not_built_reason"]
    # a counter on its wall with the sink in it is no duplicate
    run = next(f for f in _kitchen()["furniture"] if f["id"] == "f_run")
    assert AA.counter_duplicate(AA.Plan(_kitchen()), run) is None


def test_r17_b_a_way_lost_on_one_floor_is_a_cut_though_another_storey_still_joins_the_rooms():
    """Two stair rooms: A0 and B0 on L0 are joined by the door x and each by its own stair to A1 / B1 on L1, which a
    door joins: without x, A0 still reaches B0 through L1, but not on its own floor."""
    levels = [{"id": "L0", "elevation": 0.0, "height": 3.0, "ceiling_height": 2.8},
              {"id": "L1", "elevation": 3.0, "height": 3.0, "ceiling_height": 2.8}]
    rooms = [{"id": "A0", "level_id": "L0", "room_type": "hall", "label": "MERDIVEN", "polygon": _rect(0, 0, 4, 4)},
             {"id": "B0", "level_id": "L0", "room_type": "hall", "label": "MERDIVEN", "polygon": _rect(4, 0, 8, 4)},
             {"id": "A1", "level_id": "L1", "room_type": "hall", "label": "MERDIVEN", "polygon": _rect(0, 0, 4, 4)},
             {"id": "B1", "level_id": "L1", "room_type": "hall", "label": "MERDIVEN", "polygon": _rect(4, 0, 8, 4)}]
    walls = [_wall("w0", "L0", (4, 0), (4, 4)), _wall("w1", "L1", (4, 0), (4, 4)),
             _wall("ws", "L0", (0, 0), (4, 0), exterior=True)]
    openings = [_op("x", "door", "L0", "w0", (4, 2)), _op("y", "door", "L1", "w1", (4, 2)),
                _op("e", "door", "L0", "ws", (2, 0))]
    b = {"levels": levels, "rooms": rooms, "walls": walls, "openings": openings, "furniture": [],
         "site": {"entrances": [{"door_id": "e", "level_id": "L0", "main": True}]}}
    after = copy.deepcopy(b)
    next(o for o in after["openings"] if o["id"] == "x")["type"] = "window"
    cuts = AR.cut_links(b, after)
    assert cuts and cuts[0]["rooms"] == ["A0", "B0"] and cuts[0]["floor"] == "L0"
    assert "on their floor L0" in AR.cut_text(cuts)


# ------------------------------------------------------------------------------------------ R17 c: W2 window evidence

def _w2_house(evidence):
    """The hall h (0-4 x 0-4, the entrance) and the dark bedroom b (4-8 x 0-4, no window to the outside) with a
    1.0 m 'window' w in the wall between them."""
    levels = [{"id": "L0", "elevation": 0.0, "height": 3.0, "ceiling_height": 2.8}]
    rooms = [{"id": "h", "level_id": "L0", "room_type": "hall", "polygon": _rect(0, 0, 4, 4)},
             {"id": "b", "level_id": "L0", "room_type": "bedroom", "polygon": _rect(4, 0, 8, 4)}]
    walls = [_wall("wm", "L0", (4, 0), (4, 4)), _wall("ws", "L0", (0, 0), (8, 0), exterior=True),
             _wall("we", "L0", (8, 0), (8, 4), exterior=True)]
    openings = [_op("e", "door", "L0", "ws", (2, 0), evidence=copy.deepcopy(ARC)),
                _op("d", "door", "L0", "wm", (4, 3.4), 0.8, evidence=copy.deepcopy(ARC)),
                _op("w", "window", "L0", "wm", (4, 1.5), 1.0, evidence=evidence, type_raw=None)]
    return {"levels": levels, "rooms": rooms, "walls": walls, "openings": openings, "furniture": [],
            "site": {"entrances": [{"door_id": "e", "level_id": "L0", "main": True}]}}


def test_r17_c_w2_never_moves_a_window_without_window_evidence_it_reads_the_passage_again():
    dotted = [{"method": "vector", "entity": "gap:LINE:1,LINE:2", "note": "unclassified gap content: LINE:1,LINE:2"}]
    assert AA.window_evidence({"type": "window", "evidence": dotted}) is None
    assert AA.window_evidence({"type": "window", "type_raw": "window size tag 150/160",
                               "evidence": [{"rule": "size_tag", "text": "150/160"}]})
    assert AA.window_evidence({"type": "window", "evidence": [{"method": "vector", "entity": "LINE:4,LINE:5"}]})
    assert AA.window_evidence({"type": "window", "drawn_type": "door", "evidence": ARC}) is None
    b = _w2_house(dotted)
    sides = AR.opening_sides(b)
    w2 = next(q for q in RU.openings_rules(AA.Plan(b), sides) if q["id"] == "W2")
    a = next(x for x in w2["answers"] if x["element"] == "w")
    ids = [o["id"] for o in a["options"]]
    assert "move_window_to_outer_wall" not in ids and a["default"] == "window_to_passage"
    # an AI answer that moves it anyway is refused (the premise); the passage is read again
    res = AA.apply_answers(b, {"W2:w": _ai("move_window_to_outer_wall", room_id="b")})
    assert res[0]["premise"] and "no window evidence" in res[0]["change"]
    res = AA.apply_answers(b, {"W2:w": {"option": "window_to_passage", "by": "architect"}})
    assert res[0]["ok"] and _by_id(b)["w"]["type"] == "opening" and _by_id(b)["w"]["sill_height"] == 0.0
    assert _by_id(b)["w"]["drawn_type"] == "window" and _by_id(b)["w"]["corrected_by_ai"]["answer_key"] == "W2:w"
    # a window drawn as a window (its frame strokes) is still moved by default
    drawn = _w2_house([{"method": "vector", "entity": "LINE:4,LINE:5"}])
    w2 = next(q for q in RU.openings_rules(AA.Plan(drawn), AR.opening_sides(drawn)) if q["id"] == "W2")
    a = next(x for x in w2["answers"] if x["element"] == "w")
    assert a["default"] == "move_window_to_outer_wall"


# ----------------------------------------------------------------------------------- R17 d: basins stay, sills rise

def _bathroom(assumed_sill: bool = True) -> dict:
    levels = [{"id": "L0", "elevation": 0.0, "height": 3.0, "ceiling_height": 2.7}]
    rooms = [{"id": "w", "level_id": "L0", "room_type": "bathroom", "polygon": _rect(0, 0, 3, 2.5)}]
    walls = [_wall("ws", "L0", (0, 0), (3, 0), exterior=True), _wall("wn", "L0", (0, 2.5), (3, 2.5))]
    win = _op("o", "window", "L0", "ws", (1.5, 0), 0.8, sill_height=0.7, height=1.5,
              evidence=[{"method": "vector", "entity": "LINE:1,LINE:2"}])
    if assumed_sill:
        win["assumed"] = ["sill_height", "height"]
    basin = {"id": "f_basin", "type": "washbasin", "level_id": "L0", "room_id": "w", "source": "from_documents",
             "footprint": {"center": [1.5, 0.35], "size": [0.6, 0.45], "rotation_deg": 0.0}, "front_deg": 90.0,
             "height": 0.85}
    return {"levels": levels, "rooms": rooms, "walls": walls, "openings": [win], "furniture": [basin],
            "site": {}}


def test_r17_d_h2_raises_an_assumed_sill_first_and_never_moves_a_drawn_basin_for_a_window():
    b = _bathroom()
    q = next(q for q in RU.furniture_rules(AA.Plan(b), AR.opening_sides(b)) if q["id"] == "H2")
    a = next(x for x in q["answers"] if x["element"] == "f_basin")
    ids = [o["id"] for o in a["options"]]
    assert a["open"] and a["default"] == "basin_sill" and "clear_basin" not in ids, ids
    # F3 (free windows) never asks to move drawn sanitary ware either
    f3 = next(q for q in RU.furniture_rules(AA.Plan(b), AR.opening_sides(b)) if q["id"] == "F3")
    assert not any(x.get("open") for x in f3["answers"])
    # an added basin (not drawn) may still move, after the sill
    added = _bathroom()
    added["furniture"][0]["source"] = "added_by_ai"
    q = next(q for q in RU.furniture_rules(AA.Plan(added), AR.opening_sides(added)) if q["id"] == "H2")
    a = next(x for x in q["answers"] if x["element"] == "f_basin")
    assert a["options"][0]["id"] == "basin_sill"


# ---------------------------------------------------------------------------------- R17 e: D5 keeps a tagged size

def test_r17_e_d5_never_changes_the_size_of_a_door_the_documents_tag():
    scandi = {"family": "scandinavian", "door": {"material": "wood_oak_light"}}
    rooms = [{"id": "r_hall", "level_id": "L0", "room_type": "hall", "polygon": _rect(5, 0, 7, 7)},
             {"id": "r_liv", "level_id": "L0", "room_type": "living", "polygon": _rect(0, 0, 5, 7)}]
    walls = [_wall("ws", "L0", (0, 0), (11, 0), 0.3, exterior=True), _wall("w5", "L0", (5, 0), (5, 7), 0.1)]

    def house(tagged):
        ent = {"id": "d_ent", "type": "door", "level_id": "L0", "wall_id": "ws", "center": [6, 0], "width": 0.8,
               "height": 2.1, "assumed": ["height"], "evidence": []}
        if tagged:
            ent["evidence"] = [{"rule": "size_tag", "text": "K1-80/210", "method": "vector"}]
        return {"project": {"id": "t"}, "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
                "walls": walls, "rooms": rooms, "furniture": [], "decor": [],
                "openings": [ent, {"id": "d_liv", "type": "door", "level_id": "L0", "wall_id": "w5", "center": [5, 3],
                                   "width": 0.9, "height": 2.1, "assumed": ["height"]}],
                "site": {"entrances": [{"door_id": "d_ent", "main": True}]}}

    plain = {r["id"]: r for r in DS.plan_sizes(house(False), scandi)}
    assert plain["d_ent"]["height"] == pytest.approx(DS.ENTRANCE_HEIGHT_M)          # the entrance grows ...
    tagged = {r["id"]: r for r in DS.plan_sizes(house(True), scandi)}
    assert "d_ent" not in tagged                                                     # ... unless its size is tagged


def test_r17_e_the_reading_records_a_doors_own_size_tag_as_evidence_only():
    from wenart.ingest import core_rules as CR

    b = {"openings": [{"id": "d1", "type": "door", "level_id": "L0", "center": [4.475, 0.975], "width": 0.75,
                       "height": 2.1, "assumed": ["height"], "evidence": [{"file": "p.dwg", "method": "vector",
                                                                            "confidence": 0.95, "entity": "ARC:1"}]},
                      {"id": "d2", "type": "door", "level_id": "L0", "center": [9.0, 0.975], "width": 0.9,
                       "height": 2.1, "evidence": [{"file": "p.dwg", "method": "vector", "confidence": 0.9}]}]}
    texts = {"L0": [{"text": "K1-80/210", "x": 4.06, "y": 0.78, "entity": "ATTDEF:1"},
                    {"text": "P:120/150", "x": 9.0, "y": 1.2, "entity": "ATTDEF:2"},       # a window's tag
                    {"text": "K2-90/210", "x": 12.0, "y": 5.0, "entity": "ATTDEF:3"}]}     # too far from d2
    got = CR.own_door_tags(b, texts)
    assert got == [{"opening": "d1", "level_id": "L0", "tag": "K1-80/210"}]
    d1, d2 = b["openings"]
    assert d1["door_tags"] == ["K1-80/210"] and d1["evidence"][-1]["rule"] == "own_door_tag"
    assert d1["evidence"][-1]["file"] == "p.dwg" and d1["width"] == 0.75 and d1["assumed"] == ["height"]
    assert "door_tags" not in d2 and AA.door_tag(d1) == (0.8, 2.1, "K1-80/210")
    assert "K1-80/210" in AA.drawn_door_evidence(dict(d1, evidence=d1["evidence"][1:]))   # the tag alone: drawn


# --------------------------------------------------------------------------------- R17 f: D6 no second door

def test_r17_f_d6_makes_no_privacy_door_into_a_room_another_door_reaches():
    levels = [{"id": "L0", "elevation": 0.0, "height": 3.0, "ceiling_height": 2.8}]
    rooms = [{"id": "k", "level_id": "L0", "room_type": "kitchen", "polygon": _rect(0, 0, 4, 4)},
             {"id": "w", "level_id": "L0", "room_type": "bathroom", "polygon": _rect(4, 0, 7, 4)},
             {"id": "h", "level_id": "L0", "room_type": "hall", "polygon": _rect(0, 4, 7, 6)}]
    walls = [_wall("wkw", "L0", (4, 0), (4, 4), 0.1), _wall("wh", "L0", (0, 4), (7, 4), 0.1)]
    gap = _op("o", "opening", "L0", "wkw", (4, 1.5), 0.65, sill_height=0.0, type_raw="unclassified gap content",
              evidence=[{"entity": "gap:LINE:1", "note": "unclassified gap content: LINE:1"}])
    openings = [gap, _op("d_w", "door", "L0", "wh", (5.5, 4), 0.8, evidence=copy.deepcopy(ARC)),
                _op("d_k", "door", "L0", "wh", (2, 4), 0.8, evidence=copy.deepcopy(ARC))]
    b = {"levels": levels, "rooms": rooms, "walls": walls, "openings": openings, "furniture": [], "site": {}}
    d6 = RU.passages_rule(AA.Plan(b), AR.opening_sides(b))[0]
    a = next(x for x in d6["answers"] if x["element"] == "o")
    assert not a.get("open") and "reached by its door d_w" in a["found"]
    res = AA.apply_answers(b, {"D6:o": _ai("gap_to_door", door_id="o")})
    assert res[0]["premise"] and "no second (privacy) door" in res[0]["change"]
    assert _by_id(b)["o"]["type"] == "opening"
    # without the bathroom's own door the privacy door is still the default
    alone = copy.deepcopy(b)
    alone["openings"] = [o for o in alone["openings"] if o["id"] != "d_w"]
    d6 = RU.passages_rule(AA.Plan(alone), AR.opening_sides(alone))[0]
    assert next(x for x in d6["answers"] if x["element"] == "o")["default"] == "gap_to_door"


# ---------------------------------------------------------------------- W3: no guard over a landing, code-set sills

def test_w3_a_low_window_onto_an_outdoor_space_at_its_floor_is_over_no_drop():
    b = _upper_flat()
    w = _by_id(b)["w1"]
    w.update(center=[4.6, 0.0], width=0.6, sill_height=0.4)              # over the balcony os_bal
    w3 = next(q for q in RU.openings_rules(AA.Plan(b), AR.opening_sides(b)) if q["id"] == "W3")
    a = next(x for x in w3["answers"] if x["element"] == "w1")
    assert not a.get("open") and "no drop" in a["found"]
    bare = _upper_flat(balcony=False)
    _by_id(bare)["w1"].update(center=[4.6, 0.0], width=0.6, sill_height=0.4)
    w3 = next(q for q in RU.openings_rules(AA.Plan(bare), AR.opening_sides(bare)) if q["id"] == "W3")
    assert next(x for x in w3["answers"] if x["element"] == "w1")["open"]
    # a window code made from a door has a code-set sill: raised by default, never a guard
    made = _upper_flat(balcony=False)
    _by_id(made)["w1"].update(center=[4.6, 0.0], width=0.45, sill_height=0.0, height=2.1, drawn_type="door")
    w3 = next(q for q in RU.openings_rules(AA.Plan(made), AR.opening_sides(made)) if q["id"] == "W3")
    assert next(x for x in w3["answers"] if x["element"] == "w1")["default"] == "raise_sill"


# ------------------------------------------------------------------------------------ the real projects (CPU)

def _stored(project: str) -> dict:
    files = sorted(RUNS.glob(f"*/results/agent/{project}/architect_answers.json"))
    if not files:
        pytest.skip(f"no stored architect answers of {project} under {RUNS}")
    data = json.loads(files[-1].read_text(encoding="utf-8"))
    return data.get("answers", data)


@pytest.fixture(scope="module")
def real06_reading(tmp_path_factory):
    if not (PROJECTS / "real06").is_dir():
        pytest.skip("the real06 drawings are not here")
    from wenart.ingest import pipeline as PL
    return PL.run_project(PROJECTS / "real06", tmp_path_factory.mktemp("real06"), no_ai=True)[0]


def test_r02_real06_replay_stale_answers_put_no_guard_on_the_balcony_doors(real06_reading):
    answers = _stored("real06")
    b = copy.deepcopy(real06_reading)
    b["project"]["source_folder"] = "projects/no_such_project"
    prep = BB.prepare(b, "base", {"architect_answers": answers})
    app = [r for r in prep["architect_applied"] if r.get("by") != "architect"]
    stale = [r for r in app if r.get("stale")]
    assert len(stale) >= 40, len(stale)
    by_key = {r["key"]: r for r in app}
    # 27 Nov 2026 (round 3b, item 6): the keys are in the stored answers: their records must be there (presence first)
    for key in ("AI.french_window:d_L1_011", "AI.french_window:win_L1_005"):
        assert key in answers and key in by_key, key
        assert not by_key[key]["ok"], by_key[key]
    built = {o["id"]: o for o in prep["building"]["openings"]}
    # the balcony doors stay doors without a guard (they open onto os_L1_balkon)
    for oid in ("d_L1_002", "d_L1_007"):
        assert built[oid]["type"] == "door" and not built[oid].get("guard"), built[oid]
    # no drawn door turned into a window or a hatch
    drawn = {o["id"] for o in real06_reading["openings"] if o.get("type") == "door" and AA.drawn_door_evidence(o)}
    assert not [i for i in drawn if built.get(i, {}).get("type") not in (None, "door")]
    assert "## Stale answers (not carried out)" in AR.report_md(prep["architect"], "real06")
    # R17 e: the veranda door d_L0_004 keeps its tagged size K1-80/210 (D5 never makes it a 2.30 m entrance door)
    d4 = next(o for o in real06_reading["openings"] if o["id"] == "d_L0_004")
    assert d4.get("door_tags") == ["K1-80/210"]
    assert "d_L0_004" not in {r["id"] for r in DS.plan_sizes(prep["building"], {"family": "scandinavian"})}


@pytest.fixture(scope="module")
def real10_reading(tmp_path_factory):
    """A fresh CPU reading of real10 (no AI; about 6 minutes)."""
    if not (PROJECTS / "real10").is_dir():
        pytest.skip("the real10 drawings are not here")
    from wenart.ingest import pipeline as PL
    return PL.run_project(PROJECTS / "real10", tmp_path_factory.mktemp("real10"), no_ai=True)[0]


@pytest.mark.slow
def test_r02_real10_the_mirror_balcony_door_stays_a_door(real10_reading):
    """real10 F10: the stored E1:d_L0_024 door_to_window (2 Nov) re-targeted by place onto d_L0_025, the mirror
    flat's balcony door: stale, the door stays a door (and its balcony keeps its way in); the L1 storage retypes of
    the 'Günlük Oda' rooms (M2) are refused by their premise (the rooms have their daylight)."""
    answers = _stored("real10")
    b = copy.deepcopy(real10_reading)
    b["project"]["source_folder"] = "projects/no_such_project"
    keys = {k: v for k, v in answers.items() if k == "E1:d_L0_024" or (k.startswith("L1:")
                                                                        and v.get("option") == "retype_room")}
    # 27 Nov 2026 (round 3b, item 6): presence first, and through the replay gate as the build replays them
    gunluk = [k for k in keys if "gunluk" in k]
    assert "E1:d_L0_024" in keys and gunluk, sorted(keys)
    base, plan = BB.replay_gate(b, "base", {"architect_answers": keys})
    gate = base["architect_replay"]
    assert "E1:d_L0_024" in gate["keys"] and set(gunluk) <= set(gate["keys"])
    res = {r["key"]: r for r in plan["architect_applied"]}
    assert set(keys) <= set(res)
    assert not res["E1:d_L0_024"]["ok"] and not any(res[k]["ok"] for k in gunluk)
    assert next(o for o in plan["building"]["openings"] if o["id"] == "d_L0_025")["type"] == "door"
    rooms = {r["id"]: r for r in plan["building"]["rooms"]}
    read = {r["id"]: r for r in real10_reading["rooms"]}
    assert all(rooms[k.partition(":")[2]]["room_type"] == read[k.partition(":")[2]]["room_type"] != "storage"
               for k in gunluk if k.partition(":")[2] in read)
    # signed as given on this very reading, the premise refuses them where the room has its daylight
    plan0 = AA.Plan(copy.deepcopy(real10_reading))
    lit = [k for k in gunluk if k.partition(":")[2] in plan0.room
           and AA.retype_premise(plan0, "L1", plan0.room[k.partition(":")[2]], "storage", {})]
    assert lit, "the 'Günlük Oda' rooms have their daylight in this reading"
