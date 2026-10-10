"""The room brief of the M12 planner (docs/milestone12.md §5.2 D17, §1.4; bug B5).

Checked on the two-room fixture with a misread drawn toilet (fixed equipment), an unbuilt cluster and the other
tracks' functions faked: every built piece has a front (an inferred one flagged), its lock state and the tools it
allows with the move allowance left; an unbuilt piece is only listed as not built; groups carry their missing
partners and G-check numbers; free wall spans leave out door frames and pieces against the wall and mark window
parts; candidates come with scores and an image; findings are split into fixable (with the tools that fix them) and
"not yours" (not built, locked, no tool); track G's ``allowed_edits`` replaces the fallback rules when it answers
(the fallback is injected where a test is about it: ``fakes``), with the agent's stricter rule on top (a drawn piece
is removed only as "not furniture"); the brief's wall spans are track G's ``free_spans`` (``move_group`` takes their
ids)."""
from __future__ import annotations

import copy

from test_agent_helpers import building, piece
from wenart.agent import brief as BR
from wenart.agent import memory as MEM
from wenart.agent import topdown as TD


def toy() -> dict:
    b = building()
    b["furniture"].append(piece("f4", "r1", "toilet", (3.5, 1.0), (0.4, 1.1), 0.0, None))
    b["furniture"].append(dict(piece("f5", "r1", "unknown", (1.0, 1.0), (3.0, 2.0), 0.0, None), build=False))
    return b


FINDINGS = [{"id": "c:F3:f1", "check": "F3", "severity": "critical", "target": "f1", "room_id": "r1", "message": "x"},
            {"id": "c:F7:f4", "check": "F7", "severity": "critical", "target": "f4", "room_id": "r1", "message": "y"},
            {"id": "c:F9:f5", "check": "F9", "severity": "major", "target": "f5", "room_id": "r1", "message": "z"},
            {"id": "c:R5:r1", "check": "R5", "severity": "major", "target": "r1", "room_id": "r1",
             "message": "dark"},
            {"id": "c:S5:f1", "check": "S5", "severity": "major", "target": "f1", "room_id": "r1",
             "message": "cushion 4 cm above the mattress"},
            {"id": "c:G4:f2", "check": "G4", "severity": "major", "target": "f2", "room_id": "r1",
             "message": "one nightstand only"}]


def fakes(**kw):
    members = [{"group_id": "g_sleep", "group": "sleeping_double", "anchor_id": "f1", "member_ids": ["f1", "f2"],
                "missing": ["nightstand"]}]
    viol = [{"check": "G4", "severity": "major", "target": "g_sleep", "room_id": "r1",
             "message": "nightstand on one side only: the left side is free 0.9 m", "metrics": {}}]
    cands = [{"rank": 1, "score": 0.82, "terms": {"walls": 0.9}, "pieces": [{}], "hard_failures": [],
              "groups": [{"group": "sleeping_double", "anchor_id": "f1", "member_ids": ["f1", "f2", "n2"]}],
              "group_violations": []},
             {"rank": 2, "score": 0.61, "terms": {"walls": 0.7}, "pieces": [], "groups": [],
              "group_violations": [{"check": "G5", "severity": "major"}]}]
    out = dict(members_fn=lambda b, r: members, group_checks_fn=lambda b, r: viol, allowed_fn=lambda b, pid: {},
               program_fn=lambda b, r: {"groups": [{"group_id": "g_sleep", "group": "sleeping_double",
                                                    "anchor_id": "f1", "required": True, "options": ["double"],
                                                    "chosen": "double", "drawn": True}], "reason": "bedroom 14 m2"},
               solver_fn=lambda b, r, k=3: cands)
    out.update(kw)
    return out


def test_pieces_fronts_locks_and_the_unbuilt_cluster():
    b = toy()
    out = BR.room_brief(b, "r1", findings=FINDINGS, **fakes())
    pieces = {p["id"]: p for p in out["pieces"]}
    assert set(pieces) == {"f1", "f2", "f4"}                    # B5: the unbuilt f5 is no piece of the brief
    assert out["not_built"] == [{"id": "f5", "type": "unknown", "size": [3.0, 2.0]}]
    assert all(p["front_deg"] is not None for p in pieces.values())
    assert pieces["f4"]["front_inferred"] is True and "front_inferred" not in pieces["f1"]
    # drawn furniture: 0.3 m move allowance, no removal (only "not furniture" with evidence)
    assert pieces["f1"]["allowed"]["move_piece"] is True and pieces["f1"]["move_left_m"] == 0.3
    assert "mark_not_furniture" in pieces["f1"]["allowed"]["remove_piece"]
    # drawn fixed equipment: only a front fix, the U1 fixture fix, another model
    assert {t for t, v in pieces["f4"]["allowed"].items() if v is True} == {"rotate_piece", "set_front", "fix_fixture",
                                                                           "swap_model"}
    assert pieces["f4"]["lock"].startswith("may: rotate_piece, set_front, fix_fixture")
    assert pieces["f1"]["group"] == {"group_id": "g_sleep"} and out["allowed_source"] == ["fallback"]
    # a drawn piece already moved 0.25 m has 0.05 m left
    moved = copy.deepcopy(b)
    f2 = next(f for f in moved["furniture"] if f["id"] == "f2")
    f2["drawn_footprint"] = {"center": [0.9, 3.0]}
    assert BR.room_brief(moved, "r1", **fakes())["pieces"][1]["move_left_m"] == 0.05


def test_groups_program_candidates_and_memory(tmp_path):
    mem = MEM.Memory(tmp_path)
    mem.record("r1", 1, "move_piece", {"piece_id": "f1", "center": [2, 2], "reason": "x"},
               {"accepted": False, "failed_checks": ["drawn_lock: moved 0.45 m, limit 0.3 m"]})
    seen = []
    out = BR.room_brief(toy(), "r1", findings=FINDINGS, memory=mem,
                        image_of=lambda rank, c: seen.append(rank) or f"images/cand{rank}.png", **fakes())
    g = out["groups"][0]
    assert g["missing"] == ["nightstand"] and g["checks"] == [
        "G4 major: nightstand on one side only: the left side is free 0.9 m"]
    assert out["program"]["groups"][0]["options"] == ["double"]
    assert [c["candidate"] for c in out["candidates"]] == [1, 2] and seen == [1, 2]
    assert out["candidates"][0]["image"] == "images/cand1.png" and out["candidates"][1]["group_findings"] == [
        "G5 major"]
    assert out["memory"]["rejected"][0]["why_rejected"] == ["drawn_lock: moved 0.45 m, limit 0.3 m"]
    assert "reason" not in out["memory"]["rejected"][0]["args"]


def test_fixable_and_not_yours():
    out = BR.room_brief(toy(), "r1", findings=FINDINGS, **fakes())
    fixable = {f["id"]: f["tools"] for f in out["findings"]["fixable"]}
    not_yours = {f["id"]: f["why"] for f in out["findings"]["not_yours"]}
    # a re-layout never moves a drawn bed
    assert fixable["c:F3:f1"] == ["move_piece", "move_group", "rotate_piece", "set_front"]
    assert fixable["c:F7:f4"] == ["fix_fixture"]                    # U1: the misread toilet may be fixed
    assert fixable["c:R5:r1"] == ["set_lighting"] and fixable["c:G4:f2"][0] == "complete_group"
    assert "not built" in not_yours["c:F9:f5"] and "decor stage" in not_yours["c:S5:f1"]
    # a finding whose only tools the target refuses is "not yours" with the reason
    locked = [{"id": "c:F2:f4", "check": "F2", "severity": "major", "target": "f4", "room_id": "r1",
               "message": "1.1 m long"}]
    out2 = BR.room_brief(toy(), "r1", findings=locked, **fakes(
        allowed_fn=lambda b, pid: {"fix_fixture": {"allowed": False, "why": "the size is a real one"}}
        if pid == "f4" else {}))
    assert out2["findings"]["fixable"] == [] and "the size is a real one" in out2["findings"]["not_yours"][0]["why"]
    assert out2["allowed_source"] == ["edit_ops", "fallback"]


def test_track_g_allowed_edits_replace_the_fallback_and_op_names_are_mapped():
    answer = {"move": {"allowed": True, "why": "", "move_left_m": 0.12}, "set_front": {"allowed": False,
                                                                                         "why": "front fixed"}}
    a, src = BR.allowed_of(toy(), {"id": "f1"}, lambda b, pid: answer)
    assert src == "edit_ops" and a["move_piece"] == {"allowed": True, "why": "", "move_left_m": 0.12}
    assert a["set_front"]["allowed"] is False
    a2, src2 = BR.allowed_of(toy(), next(f for f in toy()["furniture"] if f["id"] == "f3"), lambda b, pid: {})
    assert src2 == "fallback" and a2["remove_piece"]["allowed"] and not a2["mark_not_furniture"]["allowed"]


def test_track_g_answers_with_the_drawn_removal_rule_and_its_spans():
    """With track G's real ``allowed_edits`` and ``free_spans``: a drawn bed may turn (rotate_piece) but has a front
    already (no set_front) and is removed only as not furniture; an AI piece may be removed; the spans carry G's ids."""
    b = toy()
    out = BR.room_brief(b, "r1", findings=FINDINGS, **{k: v for k, v in fakes().items() if k != "allowed_fn"})
    pieces = {p["id"]: p for p in out["pieces"]}
    assert out["allowed_source"] == ["edit_ops"]
    f1 = pieces["f1"]["allowed"]
    assert f1["rotate_piece"] is True and f1["set_front"] is not True and "mark_not_furniture" in f1["remove_piece"]
    fixable = {f["id"]: f["tools"] for f in out["findings"]["fixable"]}
    assert "rotate_piece" in fixable["c:F3:f1"] and "set_front" not in fixable["c:F3:f1"]
    ai = copy.deepcopy(b)
    next(f for f in ai["furniture"] if f["id"] == "f1")["source"] = "added_by_ai"
    a, src = BR.allowed_of(ai, next(f for f in ai["furniture"] if f["id"] == "f1"))
    assert src == "edit_ops" and a["remove_piece"]["allowed"] is True
    from wenart.furniture import edit_ops
    ids = [s["span_id"] for s in edit_ops.free_spans(b, "r1")]
    spans = out["free_wall_spans"]
    assert [s["id"] for s in spans] == ids and all(s["id"].startswith("r1.s") for s in spans)
    assert all(s["into_room_deg"] is not None and s["fits"] for s in spans)

    def broken(building, room_id):
        raise ValueError("no spans")

    assert BR.wall_spans(b, "r1", spans_fn=broken) == BR.free_wall_spans(b, "r1")   # the brief's own spans then


def test_free_wall_spans():
    spans = {s["id"]: s for s in BR.free_wall_spans(toy(), "r1")}
    # wall w1 (y = 0) has door d1 at x 3.2 (0.9 wide): free 0 .. 2.65; the bed and the nightstand stand at w3
    assert spans["r1:s1.1"]["wall_id"] == "w1" and spans["r1:s1.1"]["end"] == [2.65, 0.0]
    assert spans["r1:s1.1"]["into_room_deg"] == 90.0 and spans["r1:s1.1"]["fits"] == "any piece"
    w3 = [s for s in spans.values() if s["wall_id"] == "w3"]
    assert [s["length_m"] for s in w3] == [1.2, 0.7]                  # minus the bed (1.2-2.8) and nightstand
    # without the bed the window part of w3 is listed for low pieces only
    b = toy()
    b["furniture"] = [f for f in b["furniture"] if f["id"] != "f1"]
    low = [s for s in BR.free_wall_spans(b, "r1") if "sill" in s["fits"]]
    assert low and low[0]["fits"].startswith("only below the sill 0.9 m (window win1)")


def test_unbuilt_pieces_are_never_drawn_or_shown_to_the_critic(tmp_path, monkeypatch):
    """B5 (real03 run 3: 6 critical "giant box" findings on two unbuilt clusters)."""
    import matplotlib.axes
    from wenart.agent import critic_vision as CV
    from wenart.agent import prompts as P
    b = toy()
    assert [p["id"] for p in TD.built_pieces(b, "r1")] == ["f1", "f2", "f4"]
    assert "f5" not in CV.room_ids(b, "r1", []) and "f1" in CV.room_ids(b, "r1", [])
    room = b["rooms"][0]
    prompt = P.room_look_prompt(room, TD.built_pieces(b, "r1"), [], [], [])
    assert "f5" not in prompt and "- f1: bed_double" in prompt
    drawn = []
    orig = matplotlib.axes.Axes.text

    def spy(self, x, y, s, *a, **k):
        drawn.append(str(s))
        return orig(self, x, y, s, *a, **k)

    monkeypatch.setattr(matplotlib.axes.Axes, "text", spy)
    TD.draw_room(b, "r1", tmp_path / "r1.png")
    assert any("f1" in t for t in drawn) and not any("f5" in t for t in drawn)


def test_fixable_weight_ranks_by_severity_times_area():
    fx = [{"severity": "critical"}, {"severity": "major"}, {"severity": "minor"}]
    assert BR.fixable_weight(fx, 10.0) == (9 + 3) * 10.0 and BR.fixable_weight([], 50.0) == 0.0
