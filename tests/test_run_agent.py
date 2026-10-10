"""The orchestrated full run (docs/milestone11.md §2, §8, §10 "fallback", "loop"; D8): the scheduler with the fake
runner, clock and servers of tests/test_run_scheduler.py, the agent model faked by MockModel.

Checked: the phase order (1-4, the agent block with phases 5-8 inside, 10, 11), one agent server session (no Qwen
or GLM check sessions), round 0 = build + previews (960x540, 32 samples, agent/previews), a round's re-run =
agent_apply -> refit from building_agent.json -> build -> previews of the changed views only, the one-pass check with
the agent model and combine with CHECK_MODELS=agent, sleep/wake around the gate and the polish below 80 GB, a refit
that refuses the agent's edits is rolled back (the project stays ok), a failed agent server leaves the M10 result,
``--no-orchestrator`` is the default of RunOptions (the golden M10 tests stay as they are) and the CLI flags, and
the import closure of ``python -m wenart.agent`` is covered by the agent stages' code list."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import test_run_scheduler as TRS
from test_agent_helpers import FakeEdits, ScriptedCritic, fake_validators, violation
from test_run_scheduler import FakeCLI, Run, first, opt
from test_run_stages import import_closure
from wenart.agent import log as LG
from wenart.agent import model as M
from wenart.agent import overrides as OV
from wenart.run import scheduler as SC
from wenart.run import stages as S
from wenart.run import state as ST
from wenart.run.projects import REPO_ROOT

AGENT = {"id": "Qwen/Qwen3.8-27B-FP8", "revision": "rev-a", "slug": "qwen3.8-27b-fp8", "server_flags": ""}
START_S = {"qwen": 300.0, "glm": 150.0, "agent": 420.0}


class AgentCLI(FakeCLI):
    """FakeCLI + ``python -m wenart.agent apply`` (in process, with the fake edit validator) and room ids on the
    cameras (the agent's router maps rooms to views)."""

    edits = FakeEdits()

    @staticmethod
    def name_of(cmd) -> str:
        if len(cmd) > 3 and cmd[1] == "-m" and cmd[2] == "wenart.agent":
            return f"agent {cmd[3]}"
        if len(cmd) > 2 and cmd[2] == "wenart.blender.cli" and "agent/previews" in str(opt(cmd, "--out") or ""):
            return "previews"
        if len(cmd) > 3 and cmd[2] == "wenart.furniture.fit" and cmd[3].endswith(S.AGENT_BUILDING):
            return "refit"
        return FakeCLI.name_of(cmd)

    @staticmethod
    def project_of(cmd) -> str:
        if len(cmd) > 3 and cmd[2] == "wenart.agent":
            return Path(cmd[4]).name
        if len(cmd) > 2 and cmd[2] == "wenart.blender.cli" and "agent/previews" in str(opt(cmd, "--out") or ""):
            return Path(opt(cmd, "--out")).parent.parent.name
        return FakeCLI.project_of(cmd)

    def h_agent_apply(self, cmd, project, log):
        OV.apply(Path(cmd[4]), apply_edit=self.edits)

    def h_build(self, cmd, project, log):
        rc = super().h_build(cmd, project, log)
        path = Path(opt(cmd, "--out")) / "scene_manifest.json"
        if path.is_file():
            data = json.loads(path.read_text())
            for c in data["cameras"]:
                c["room_id"] = c["name"][4:].rsplit("_", 1)[0]
            path.write_text(json.dumps(data))
        return rc

    def h_previews(self, cmd, project, log):
        out = Path(opt(cmd, "--out"))
        scene = json.loads((Path(opt(cmd, "--scene")).parent / "scene_manifest.json").read_text())
        cams = [c["name"] for c in scene["cameras"]]
        if opt(cmd, "--cameras", "all") != "all":
            cams = opt(cmd, "--cameras").split(",")
        out.mkdir(parents=True, exist_ok=True)
        for c in cams:
            (out / f"{c}_preview.jpg").write_bytes(b"jpg")
        TRS.write(out / "render_manifest.json", {"renders": [{"camera": c} for c in cams], "incomplete": False})


@pytest.fixture
def models(monkeypatch):
    monkeypatch.setattr(TRS, "MODELS", dict(TRS.MODELS, agent=AGENT))
    monkeypatch.delenv("WENART_AGENT_SLEEP", raising=False)
    return TRS.MODELS


def orchestrated(tmp_path, chat, critic_rounds, *, buildings=None, rc=None, fail=None, **opts):
    r = Run(tmp_path, {"p1": {}}, buildings=buildings, start_s=START_S, fail=fail, projects=["p1"],
            orchestrator=True, **opts)
    r.cli = AgentCLI(r.clock, buildings, rc)
    r.controls = []
    r.mocks = []

    def factory(url, pr):
        m = M.MockModel(chat=list(chat), model=AGENT["id"], revision=AGENT["revision"])
        r.mocks.append((url, m))
        return m

    r.kwargs = dict(agent_model_factory=factory,
                    server_control=lambda url, action: r.controls.append((len(r.cli.calls), action)) or True,
                    agent_loop_kwargs={"code_critic": ScriptedCritic(critic_rounds), "vision": False,
                                       "apply_edit": FakeEdits(), "validators": fake_validators()})
    return r


CHANGE = {"tool_calls": [{"name": "change_type", "arguments": {"piece_id": "f_ai", "type": "armchair",
                                                                "reason": "a bed does not fit here"}}]}
FINISH = {"tool_calls": [{"name": "finish", "arguments": {"verdict": "done"}}]}
F1 = violation("F1", "critical", "f_ai", "r2", "wrong type for the room")


def test_the_orchestrated_run(tmp_path, models):
    r = orchestrated(tmp_path, [CHANGE, FINISH], [[F1], []])
    assert r.run(**r.kwargs) == 0
    names = r.cli.names()
    assert [ph["phase"] for ph in r.manifest()["phases"]] == [1, 2, 3, 4, 5, 6, 7, 8, SC.AGENT_PHASE, 10, 11]
    assert r.servers.starts == ["qwen", "agent"]                 # layout (Qwen), then one agent session
    order = ["layout", "decor", "refit", "build", "previews", "agent apply", "render", "select-controls",
             "gate calibrate", "polish", "expected", "check run", "combine", "report", "pytest"]
    idx = [first(names, n) for n in order]
    assert idx == sorted(idx), names
    # round 0: build + previews of every view; round 1: apply, refit from building_agent.json, build, changed views
    previews = r.cli.find("previews")
    assert len(previews) == 2
    p0 = previews[0]["cmd"]
    assert opt(p0, "--res") == "960x540" and opt(p0, "--samples") == "32" and opt(p0, "--cameras") == "all"
    assert opt(p0, "--out").endswith("outputs/p1/agent/previews")
    assert opt(previews[1]["cmd"], "--cameras") == "cam_r2_1,cam_r2_2,cam_r2_3"
    refits = r.cli.find("refit")
    assert refits[0]["cmd"][3].endswith("building_decor.json") and refits[1]["cmd"][3].endswith("building_agent.json")
    i_apply = r.cli.calls.index(r.cli.find("agent apply")[0])
    assert i_apply < r.cli.calls.index(refits[1]) < r.cli.calls.index(r.cli.find("build")[1]) \
        < r.cli.calls.index(previews[1])
    # the final renders are the full renders of every view (after the rounds)
    render = r.cli.find("render")[0]["cmd"]
    assert opt(render, "--cameras") == "all" and opt(render, "--res") == "1920x1080"
    assert r.cli.calls.index(previews[1]) < r.cli.calls.index(r.cli.find("render")[0])
    # D8: the check is one pass of the agent model; combine counts only it
    checks = r.cli.find("check run")
    assert [opt(c["cmd"], "--model-key") for c in checks] == ["agent"]
    assert opt(checks[0]["cmd"], "--server") == "http://fake-agent/v1" and opt(checks[0]["cmd"], "--workers") == "2"
    assert all(c["env"]["CHECK_MODELS"] == "agent" for c in r.cli.find("combine") + r.cli.find("calibrate"))
    # pod G3: the GPU tests check the answers of the models the run used (the agent alone)
    assert all(c["env"]["CHECK_MODELS"] == "agent" for c in r.cli.find("pytest"))
    # 32 GB: the agent server sleeps for the gate and the polish, then wakes for the check
    assert [a for _n, a in r.controls] == ["sleep", "wake"]
    (n_sleep, _), (n_wake, _) = r.controls
    calls = r.cli.calls
    assert calls.index(r.cli.find("control renders")[0]) < n_sleep <= calls.index(r.cli.find("gate calibrate")[0])
    assert calls.index(r.cli.find("polish")[0]) < n_wake <= calls.index(r.cli.find("check run")[0])
    # records, log, overrides, building_agent.json
    agent = r.record("p1", "agent")
    assert agent["status"] == "ok" and "1 edit(s) accepted" in agent["note"] and "no critical or major" in agent["note"]
    assert r.record("p1", "agent_apply")["status"] == "ok" and r.record("p1", "agent_previews")["status"] == "ok"
    out = tmp_path / "outputs" / "p1"
    log = json.loads((out / "orchestrator" / "log.json").read_text())
    assert LG.validate_log(log) == [] and log["model"] == AGENT["id"] and log["revision"] == "rev-a"
    edit = next(e for e in log["events"] if e["kind"] == "edit")
    assert edit["tool"] == "change_type" and edit["checklist"] == "F1" and edit["round"] == 1
    assert json.loads((out / S.AGENT_BUILDING).read_text())["agent_overrides"]["round"] == 1
    assert [f["type"] for f in json.loads((out / "building_final.json").read_text())["furniture"]] == ["armchair"]
    stages = r.stages("p1")
    assert {"agent", "agent_apply", "agent_previews"} <= set(stages) and r.manifest()["projects"][0]["state"] == "ok"
    assert r.mocks and r.mocks[0][0] == "http://fake-agent/v1"


def test_no_sleep_when_switched_off_and_a_resumed_run_replays_the_overrides(tmp_path, models, monkeypatch):
    r = orchestrated(tmp_path, [CHANGE, FINISH], [[F1], []])
    monkeypatch.setenv("WENART_AGENT_SLEEP", "off")          # (auto: only below 80 GB; Run fakes 32 GB)
    assert r.run(**r.kwargs) == 0
    assert r.controls == []
    monkeypatch.delenv("WENART_AGENT_SLEEP")
    # the same command again: phase 4 replays overrides.json (agent_apply reused) and refit reads building_agent.json
    r2 = orchestrated(tmp_path, [FINISH], [[]])
    assert r2.run(**r2.kwargs) == 0
    assert r2.record("p1", "agent_apply")["status"] == "reused"
    assert any(k.endswith("building_agent.json") for k in r2.record("p1", "refit")["inputs"])
    assert r2.cli.find("refit") == [] or r2.cli.find("refit")[0]["cmd"][3].endswith("building_agent.json")


def test_a_refused_refit_rolls_the_round_back(tmp_path, models):
    rc = {"refit": lambda cli: 1 if len(cli.find("refit")) == 2 else 0}
    r = orchestrated(tmp_path, [CHANGE, FINISH], [[F1]], rc=rc)
    assert r.run(**r.kwargs) == 0
    assert len(r.cli.find("refit")) == 3 and r.manifest()["projects"][0]["state"] == "ok"
    out = tmp_path / "outputs" / "p1"
    entry = json.loads(OV.overrides_path(out).read_text())["edits"][0]
    assert entry["result"]["accepted"] is False and "refit failed" in entry["result"]["rolled_back"]
    assert "rerun failed" in r.record("p1", "agent")["note"] or "re-run" in r.record("p1", "agent")["note"]
    assert r.record("p1", "refit")["status"] == "ok"
    assert [f.get("type") for f in json.loads((out / "building_final.json").read_text())["furniture"]] != ["armchair"]


def test_a_failed_agent_server_leaves_the_m10_result(tmp_path, models):
    r = orchestrated(tmp_path, [CHANGE], [[F1]], fail={"agent": "early_exit"})
    assert r.run(**r.kwargs) == 1                                # the check cannot run without its server
    assert r.record("p1", "agent")["status"] == "warning" and "early_exit" in r.record("p1", "agent")["note"]
    assert r.cli.find("render") and r.cli.find("previews") == [] and r.cli.find("check run") == []
    assert r.record("p1", "check")["status"] == "failed"


def test_without_the_orchestrator_nothing_changes(tmp_path, models):
    assert SC.RunOptions().orchestrator is False                  # the M6-M10 callers and golden tests
    r = Run(tmp_path, {"p1": {}}, start_s=START_S, projects=["p1"])
    r.cli = AgentCLI(r.clock, None, None)
    assert r.run() == 0
    assert r.cli.find("previews") == [] and r.cli.find("agent apply") == []
    assert r.servers.starts == ["qwen", "qwen", "glm"]
    assert all(s not in r.stages("p1") for s in S.AGENT_STAGES)
    # an overrides file on the volume is ignored by --no-orchestrator
    out = tmp_path / "outputs" / "p1"
    OV.Overrides(out).add(1, "rotate_piece", {"piece_id": "x", "front_deg": 0, "reason": "r"}, {"accepted": True})
    assert r.run() == 0 and all(c["cmd"][3].endswith("building_decor.json") for c in r.cli.find("refit"))


def test_cli_flags(monkeypatch):
    from wenart.run import __main__ as RM
    seen = []
    monkeypatch.setattr(SC, "run_pod", lambda opts: seen.append(opts) or 0)
    assert RM.main(["pod", "--projects", "synthetic-01", "--results", "/tmp/r"]) == 0
    assert seen[-1].orchestrator is True and seen[-1].agent_key == "agent" and seen[-1].agent_rounds == 4
    RM.main(["pod", "--projects", "synthetic-01", "--results", "/tmp/r", "--no-orchestrator"])
    assert seen[-1].orchestrator is False
    RM.main(["pod", "--projects", "synthetic-01", "--results", "/tmp/r", "--profile", "smoke", "--vlm-url", "u"])
    assert seen[-1].orchestrator is False                          # the smoke profile keeps the M10 chain
    RM.main(["pod", "--projects", "x", "--results", "/tmp/r", "--agent-model", "agent_fast", "--agent-rounds", "2"])
    assert seen[-1].agent_key == "agent_fast" and seen[-1].agent_rounds == 2


def test_the_agent_stages_and_their_code_list():
    assert S.AGENT_STAGES == ("agent_apply", "agent_previews", "agent")
    assert not set(S.AGENT_STAGES) & set(S.PROJECT_STAGES) and set(S.STAGE_VERSION) == set(S.STAGES)
    tools = S.Tools(py="PY", polish_py="P", assets=Path("/a"))
    from wenart.run.projects import public_project
    ref = public_project("synthetic-04", Path("/r"), REPO_ROOT)
    assert S.agent_apply(tools, ref) == ["PY", "-m", "wenart.agent", "apply", "outputs/synthetic-04"]
    assert S.agent_previews(tools, ref, ["a", "b"]) == [
        "PY", "-m", "wenart.blender.cli", "render", "--scene", "outputs/synthetic-04/scene/scene.blend", "--out",
        "outputs/synthetic-04/agent/previews", "--cameras", "a,b", "--samples", "32", "--res", "960x540",
        "--exposure", "auto", "--white-balance", "auto"]
    covered = {p.relative_to(REPO_ROOT).as_posix() for p in ST._code_files(S.STAGES["agent_apply"].code, REPO_ROOT)}
    missing = sorted(import_closure("wenart.agent") - covered)
    assert not missing, missing


def test_the_orchestrator_files_are_copied_for_public_projects_only(tmp_path):
    """wenart/run/copy.py (Milestone 11 rows): the log, overrides, log images, round previews and the report's
    before/after images reach $RESULTS/agent/<p>/ and final/<p>/agent/; a private project copies none of them."""
    from test_run_copy import refs
    from wenart.run import copy as CP
    results, pub, priv = refs(tmp_path)
    for ref in (pub, priv):
        o = ref.out_dir
        for rel, data in (("orchestrator/log.json", b"{}"), ("orchestrator/log.md", b"# log"),
                          ("orchestrator/overrides.json", b"{}"), ("orchestrator/images/r1_001_x.png", b"png"),
                          ("orchestrator/images/r1_cam_before.jpg", b"jpg"), ("agent/previews/cam_preview.jpg", b"j"),
                          ("agent/previews/render_manifest.json", b"{}"), ("final/agent/r1_001_x.png", b"png"),
                          ("agent/previews/cam.png", b"a full-size png: never copied")):
            (o / rel).parent.mkdir(parents=True, exist_ok=True)
            (o / rel).write_bytes(data)
    CP.copy_project(pub)
    got = {p.relative_to(results).as_posix() for p in results.rglob("*") if p.is_file()}
    assert {"agent/p/log.json", "agent/p/log.md", "agent/p/overrides.json", "agent/p/images/r1_001_x.png",
            "agent/p/images/r1_cam_before.jpg", "agent/p/previews/cam_preview.jpg",
            "agent/p/previews/render_manifest.json", "final/p/agent/r1_001_x.png"} <= got
    assert "agent/p/previews/cam.png" not in got
    CP.copy_project(priv)
    private = {p.relative_to(tmp_path / "pr").as_posix() for p in (tmp_path / "pr").rglob("*") if p.is_file()}
    assert not any("agent" in p or "orchestrator" in p for p in private), private
    assert S.est_final(10, 4) > S.est_final(10, 4, polish=False) > S.est_previews(10)


def test_run_polish_off_and_the_calibrated_final_estimate(monkeypatch, tmp_path):
    """Pod G2 (real02): the final stages took about twice their estimate and left no time for agent rounds; the job
    can turn the polish off (RUN_POLISH=off -> WENART_POLISH=off)."""
    from wenart.run import stages as S

    assert S.EST_FINAL_FACTOR == 2.2
    base = S.est_final(10, polish=False) / S.EST_FINAL_FACTOR
    assert S.est_final(10, polish=True) > S.est_final(10, polish=False) > base
    text = (Path(__file__).resolve().parents[1] / "scripts" / "jobs" / "full.sh").read_text()
    assert 'if [ "${RUN_POLISH:-on}" = "off" ]; then export WENART_POLISH=off; fi' in text


def test_only_the_edits_the_locked_check_refuses_are_rolled_back(tmp_path):
    """Pod G2b: one refused edit used to roll back the whole round; now only the edits the locked check names."""
    import json as _json
    import types
    from wenart.agent import overrides as OV
    from wenart.run import scheduler as SC

    out = tmp_path / "real02"
    (out / "orchestrator").mkdir(parents=True)
    room = {"id": "r1", "level_id": "L0", "room_type": "other", "polygon": [[0, 0], [5, 0], [5, 5], [0, 5]]}
    src = {"walls": [], "openings": [], "rooms": [room], "furniture": []}
    bad = dict(room, polygon=[[0, 0], [6, 0], [6, 5], [0, 5]])            # an outline change: refused
    (out / "building.json").write_text(_json.dumps(src))
    (out / "building_agent.json").write_text(_json.dumps(dict(src, rooms=[bad])))
    edits = [{"seq": 1, "round": 2, "tool": "set_room_type", "args": {"room_id": "r1"},
              "result": {"accepted": True, "changed_ids": ["r1"]}},
             {"seq": 2, "round": 2, "tool": "move_piece", "args": {"piece_id": "f9"},
              "result": {"accepted": True, "changed_ids": ["f9"]}}]
    (out / "orchestrator" / "overrides.json").write_text(_json.dumps({"project": "real02", "edits": edits}))
    pr = types.SimpleNamespace(out=out)
    assert SC.Orchestrator.rollback_locked(None, pr, 2) == 1
    kept = {e["seq"]: e["result"] for e in OV.Overrides(out).edits}
    assert kept[1]["accepted"] is False and "locked check" in kept[1]["rolled_back"] and kept[2]["accepted"] is True
