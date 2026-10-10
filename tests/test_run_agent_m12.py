"""Milestone 12 changes of the orchestrated run (docs/milestone12.md §5.4, §13.3; bug B6), with the fakes of
tests/test_run_agent.py:

- the layout and the AI decor questions use the agent server and model (``--server`` / ``--model`` of
  ``python -m wenart.furniture.layout``), on ONE agent session that stays open until the final check;
- an agent server that does not start: the layout falls back to Qwen and the project keeps the M10 result;
- the final-stage estimate uses round 0 measured on this pod (real03 run 3: estimated 34.7 min, took 19.8-21.7);
- the loop gets the server's sequences as its parallel room sessions."""
from __future__ import annotations

import pytest

import test_run_agent as TRA
from test_run_scheduler import opt
from wenart.run import scheduler as SC
from wenart.run import stages as S

models = TRA.models             # the fixture (pytest finds it by name)


def test_the_layout_and_the_decor_questions_use_the_agent_session(tmp_path, models):
    r = TRA.orchestrated(tmp_path, [TRA.CHANGE, TRA.FINISH], [[TRA.F1], []])
    assert r.run(**r.kwargs) == 0
    assert r.servers.starts == ["agent"]
    layout = r.cli.find("layout")[0]["cmd"]
    assert opt(layout, "--model") == TRA.AGENT["id"] and opt(layout, "--server") == "http://fake-agent/v1"
    rec = r.record("p1", "layout")
    assert rec["status"] == "ok"
    # the layout's fingerprint names the agent model: a Qwen layout of an M11 run is not reused
    assert r.orch.layout_key() == "agent"
    assert opt(S.layout(r.orch.tools, r.orch.runs[0].ref, "U", "agent"), "--model") == TRA.AGENT["id"]
    assert opt(S.decor_ask(r.orch.tools, r.orch.runs[0].ref, True, "U", "agent"), "--model") == TRA.AGENT["id"]


def test_a_failed_agent_server_falls_back_to_qwen_for_the_layout(tmp_path, models):
    r = TRA.orchestrated(tmp_path, [TRA.CHANGE], [[TRA.F1]], fail={"agent": "early_exit"})
    assert r.run(**r.kwargs) == 1                                # the check cannot run without its server
    assert r.servers.starts == ["agent", "qwen"]                 # tried once, never twice
    layout = r.cli.find("layout")[0]["cmd"]
    assert opt(layout, "--model") == models["qwen"]["id"]
    assert r.record("p1", "layout")["status"] == "ok" and r.record("p1", "agent")["status"] == "warning"
    assert r.cli.find("render") and r.cli.find("previews") == []


def test_the_final_estimate_uses_round_0_measured_on_this_pod():
    """B6: real03 run 3 (83 views, polish off, RTX PRO 6000): the M11 estimate gave 34.4 min (34.7 with the old
    views); from the measured round-0 previews (≈ 290 s) the estimate is within 10 % of the measured final stages
    (render 663 + export 76 + controls 83 + expected 56 + check 309 + combine 55 + report ≈ 60 = 1,302 s)."""
    old = S.est_final(83, 4, False) / 1.634
    new = S.est_final_measured(83, 290.0, 83, seqs=4, polish=False, gpu_speed=1.634, critic_call_s=5.6)
    assert 2000 < old < 2150 and abs(new - 1302) / 1302 < 0.10
    # slower vision calls (a bigger model) and fewer sequences make the check longer; polish adds the M11 part
    assert S.est_final_measured(83, 290.0, 83, seqs=2, critic_call_s=11.2) > new + 900
    assert S.est_final_measured(83, 290.0, 83, polish=True) > S.est_final_measured(83, 290.0, 83)


def test_the_scheduler_estimate_takes_the_measurement_when_it_has_one(tmp_path, models):
    r = TRA.orchestrated(tmp_path, [TRA.CHANGE, TRA.FINISH], [[TRA.F1], []])
    assert r.run(**r.kwargs) == 0
    pr = r.orch.runs[0]
    assert pr.round0["previews_s"] >= 0 and pr.round0["views"] == pr.views
    measured = r.orch.final_estimate(pr)
    pr.round0 = {}
    assert r.orch.final_estimate(pr) == pytest.approx(
        S.est_final(pr.views, r.orch.seqs("agent"), r.orch.polish_on(pr)) / r.orch.gpu_speed())
    pr.round0 = {"previews_s": 30.0, "views": pr.views}
    assert r.orch.final_estimate(pr) == pytest.approx(S.est_final_measured(
        pr.views, 30.0, pr.views, seqs=r.orch.seqs("agent"), polish=r.orch.polish_on(pr),
        gpu_speed=r.orch.gpu_speed(), critic_call_s=SC.Orchestrator.critic_call_seconds(pr)))
    assert measured != r.orch.final_estimate(pr) or pr.round0["previews_s"] == 30.0


def test_the_loop_gets_the_servers_sequences_as_its_workers(tmp_path, models):
    seen = {}
    r = TRA.orchestrated(tmp_path, [TRA.CHANGE, TRA.FINISH], [[TRA.F1], []])
    orig = SC.Orchestrator.agent_project

    def spy(self, pr, url):
        orig(self, pr, url)
        seen["workers"] = pr.agent_loop.workers if pr.agent_loop else None

    SC.Orchestrator.agent_project = spy
    try:
        assert r.run(**r.kwargs) == 0
    finally:
        SC.Orchestrator.agent_project = orig
    assert seen["workers"] == r.orch.seqs("agent")
