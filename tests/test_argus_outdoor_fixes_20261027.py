"""27 Oct 2026 (user: "make argus fix these by itself"): the outdoor spaces' findings (model review M10) become
architect decisions with no model (``argus_ai.outdoor_decisions``): a guard on every open edge of a space
(``guard_edge``), a light roof over a covered kind left open (``cover_space``), the widest window onto a space
nobody can reach made its door; the build carries them out (``architect_actions.apply_answers``, ``site.platforms``)
and the dry re-check matches the exact rule (``argus_ai.target_gone``)."""
from __future__ import annotations

import json

import pytest

from wenart.agent import architect_ai as AIA
from wenart.audit import argus_ai as AI
from wenart.blender import architect_actions as AA
from wenart.blender import site as S
from wenart.levels import model as M

from test_outdoor_spaces_20261026 import _area, _box_building


def _terrace(label="TERAS", texts=("9,00m²",)):
    b = _box_building()
    b["site"]["areas"] = [_area(label, (8.0, -1.6), texts=texts)]          # 1.5 m in front of the south face
    n = M.infer_levels(b)
    return n, n["site"]["outdoor_spaces"][0]


def _answer(action, element, params=None):
    return {f"{AIA.AI_RULE}.{action}:{element}": {"option": action, "params": params or {}, "by": "ai",
                                                   "answer": "test", "where": None}}


def _front(space):
    ys = [p[1] for p in space["polygon"]]
    xs = [p[0] for p in space["polygon"]]
    return [[min(xs), min(ys)], [max(xs), min(ys)]]


def test_guard_segments_take_one_edge_or_a_list():
    one = [[0, 0], [2, 0]]
    assert AA.guard_segments(one) == [[[0.0, 0.0], [2.0, 0.0]]]
    assert AA.guard_segments([one, [[2, 0], [2, 3]]]) == [[[0.0, 0.0], [2.0, 0.0]], [[2.0, 0.0], [2.0, 3.0]]]
    assert AA.guard_segments([[0, 0], [0, 0]]) == [] and AA.guard_segments("x") == [] and AA.guard_segments([]) == []


def _sides(space):
    ys = [p[1] for p in space["polygon"]]
    xs = [p[0] for p in space["polygon"]]
    return [[[min(xs), min(ys)], [min(xs), max(ys)]], [[max(xs), min(ys)], [max(xs), max(ys)]]]


def test_an_asked_guard_lands_on_the_platform_edges_it_names_and_never_on_the_steps():
    n, t = _terrace()
    plain = next(p for p in AIA.prep_of(n, None, {})["site"]["platforms"] if p["id"] == t["id"])
    asked = _sides(t) + [_front(t)]
    prep = AIA.prep_of(n, None, _answer("guard_edge", t["id"], {"edges": asked}))
    applied = {r["key"]: r for r in prep["architect"]["applied"]}
    rec = applied[f"{AIA.AI_RULE}.guard_edge:{t['id']}"]
    assert rec["ok"] and "a guard on" in rec["change"]
    pf = next(p for p in prep["site"]["platforms"] if p["id"] == t["id"])
    n_e = len(pf["polygon"])
    on = {i for i in range(n_e) if S.on_guard_edge(pf["polygon"][i], pf["polygon"][(i + 1) % n_e], asked)}
    assert len(on) >= 3 and on - {pf.get("steps_edge")} <= set(pf["railing_edges"])
    assert len(pf["railing_edges"]) > len(plain.get("railing_edges") or [])
    added = set(pf["railing_edges"]) - set(plain.get("railing_edges") or [])
    assert pf.get("steps_edge") not in added                           # an asked guard never closes the way down
    assert pf.get("steps_edge") == plain.get("steps_edge")             # the edge treatment is unchanged


def test_drawn_steps_and_asked_guards_both_hold_on_one_platform():
    # the asked guards come after the elevated / drawn-steps branches: a raised terrace keeps its drawn flight
    from wenart.levels import model as LM

    n, t = _terrace()
    for s in n["site"]["outdoor_spaces"]:
        s["z"] = 0.6
        s["steps"] = {"edge": _front(t), "width_m": 1.2, "treads": 3, "tread_m": 0.3}
        s["guard_edges"] = _sides(t)
    pfs = S.platforms(n["site"], None, keep_out=[LM.outlines_of(n)["L0"]], outlines=LM.outlines_of(n))
    pf = next(p for p in pfs if p["id"] == t["id"])
    assert pf["drop_m"] > S.PLATFORM["level_tol"] and pf["edge"] == "steps"
    assert pf["steps_at"]["source"] == "drawn" and pf["steps_at"]["treads"] == 3
    n_e = len(pf["polygon"])
    sides = {i for i in range(n_e) if S.on_guard_edge(pf["polygon"][i], pf["polygon"][(i + 1) % n_e], _sides(t))}
    assert sides and sides <= set(pf["railing_edges"])


def test_cover_space_puts_a_light_roof_over_an_open_space():
    n, t = _terrace()
    assert t.get("roof") is None                                       # a terrace: an open kind
    prep = AIA.prep_of(n, None, _answer("cover_space", t["id"]))
    rec = next(r for r in prep["architect"]["applied"] if r["key"].startswith(f"{AIA.AI_RULE}.cover_space"))
    assert rec["ok"], rec["change"]
    pf = next(p for p in prep["site"]["platforms"] if p["id"] == t["id"])
    assert pf["roof"] and pf["roof"]["kind"] == "light_roof" and pf["posts"]
    assert pf["space"]["cover"] == "roof"


def test_m10_findings_become_decisions_with_every_open_edge_of_a_space_in_one():
    b = {"site": {"outdoor_spaces": [{"id": "os_b", "doors": ["win1", "win2"]}, {"id": "os_v", "doors": []}]},
         "openings": [{"id": "win1", "type": "window", "width": 1.2}, {"id": "win2", "type": "window", "width": 1.8}]}

    def f(rule, target, **m):
        return {"line": "model", "check": "M10", "target": target, "message": f"{rule} on {target}",
                "evidence": {"metrics": dict(m, rule=rule)}}

    rep = {"findings": [f("O1", "os_b"), f("O2", "os_b", edge_xy=[[0, 0], [2, 0]]),
                        f("O2", "os_b", edge_xy=[[2, 0], [2, 3]]), f("O5", "os_b", edge_xy=[[0, 0], [2, 0]]),
                        f("O4", "os_v"), f("O6", "os_v"), f("O2", "nope", edge_xy=[[0, 0], [1, 0]]),
                        {"check": "M3", "target": "os_b", "evidence": {"metrics": {"rule": "O2"}}}]}
    got = AI.outdoor_decisions(rep, b)
    by = {(d["action"], d["element"]): d for d in got}
    assert set(by) == {("window_to_door", "win2"), ("guard_edge", "os_b"), ("cover_space", "os_v")}
    edges = json.loads(by[("guard_edge", "os_b")]["value"])
    assert edges == [[[0, 0], [2, 0]], [[2, 0], [2, 3]]] and "2 open edges" in by[("guard_edge", "os_b")]["reason"]
    assert all(d["finding"]["check"] == "M10" for d in got)


def test_the_architect_takes_a_guard_decision_for_a_space_and_refuses_a_bad_edge():
    n, t = _terrace()
    plan = AA.Plan(n)
    lv = t["level_id"]
    key, ans, why = AIA._decision({"action": "guard_edge", "element": t["id"], "value": json.dumps([_front(t)])},
                                  plan, n, lv)
    assert key == f"{AIA.AI_RULE}.guard_edge:{t['id']}" and ans["opt"]["params"]["edges"] == [_front(t)]
    assert ans["where"]["kind"] == "space"
    key, _ans, why = AIA._decision({"action": "guard_edge", "element": t["id"], "value": "the front"}, plan, n, lv)
    assert key is None and "needs value" in why
    key, _ans, why = AIA._decision({"action": "move_piece", "element": t["id"], "value": ""}, plan, n, lv)
    assert key is None and "does not fit a space" in why


def test_the_dry_recheck_of_an_outdoor_finding_matches_its_rule(monkeypatch):
    from wenart.blender import model_review as MR

    left = [{"check": "M10", "target": "os_b", "metrics": {"rule": "O4"}}]
    monkeypatch.setattr(MR, "review", lambda b, s, prep: {"findings": left})
    o2 = {"line": "model", "check": "M10", "target": "os_b", "evidence": {"metrics": {"rule": "O2"}}}
    o4 = {"line": "model", "check": "M10", "target": "os_b", "evidence": {"metrics": {"rule": "O4"}}}
    assert AI.target_gone(o2, {"building": {}}) is True                # the guard fixed O2; O4 is another rule
    assert AI.target_gone(o4, {"building": {}}) is False


@pytest.mark.parametrize("value", [[[0, 0], [2, 0]], [[[0, 0], [2, 0]]]])
def test_act_guard_edge_adds_each_edge_once(value):
    plan = AA.Plan({"site": {"outdoor_spaces": [{"id": "os_b", "area_id": "sa_b"}]}})
    ok, text = AA.act_guard_edge(plan, "AI.guard_edge:os_b", {"by": "ai"}, "sa_b", value)
    assert ok and "the edge from" in text
    ok, _text = AA.act_guard_edge(plan, "AI.guard_edge:os_b", {"by": "ai"}, "os_b", value)
    sp = plan.b["site"]["outdoor_spaces"][0]
    assert ok and sp["guard_edges"] == [[[0.0, 0.0], [2.0, 0.0]]] and sp["adjusted_by_ai"]["answer_key"]
    assert AA.act_guard_edge(plan, "k", {}, "os_x", value)[0] is False
    assert AA.act_guard_edge(plan, "k", {}, "os_b", None)[0] is False
