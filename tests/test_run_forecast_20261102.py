"""2 Nov 2026 (user: "is there a way to predict the total required run time?" ... "yes, build the forecast and the render
reserve"; real10 runs 20261101-233829-full and 20261102-063705-full ended without a render): the scheduler keeps a
render reserve (the builds, the previews, the final stages and a margin) before the AI architect's answers, its floor
look and Argus; ``wenart.run.forecast`` predicts every part of a run before the pod. CPU only."""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

from wenart.run import forecast as FC
from wenart.run import scheduler as SC


class Clock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t


def _run(parts=None, views=70, out=Path("/nonexistent")):
    return SimpleNamespace(name="p", label="p", parts=dict(parts or {}), previous={}, records={}, base=None,
                           views=views, no_views=False, active=True, agent_loop=None, out=out, agent_model=None)


def _orch(deadline, now=0.0, final=1500.0):
    o = SC.Orchestrator.__new__(SC.Orchestrator)
    o.runs = []
    o.deadline = deadline
    o.now = Clock(now)
    o._speed = {"speed": 1.0}
    o.previous = lambda pr, stage: None
    o.final_estimate = lambda pr: final
    o.opts = SimpleNamespace(agent_key="qwen")
    o.seqs = lambda key="qwen": 4
    o.polish_on = lambda pr: False
    o.lines = []
    o.out = o.lines.append
    return o


def test_the_reserve_counts_the_builds_previews_final_stages_and_margin():
    pr = _run({"build": [{"name": "build", "rc": 0, "seconds": 1075.0}],
               "agent_previews": [{"name": "agent_previews", "rc": 0, "seconds": 240.0}]})
    o = _orch(deadline=None)
    need = o.render_reserve_s(pr, builds=1)
    final = 1500.0 + (1075.0 - SC.S.EST_BUILD_S)          # the final build counted at the measured length
    assert need == 1075.0 + 240.0 + final + o.RESERVE_MARGIN_S
    assert o.render_reserve_s(pr, builds=0) == need - 1075.0


def test_an_ai_step_starts_only_while_the_render_reserve_fits():
    pr = _run({"build": [{"name": "build", "rc": 0, "seconds": 1075.0}]})
    o = _orch(deadline=10_000.0, now=0.0)
    need = o.render_reserve_s(pr, 1)
    assert o.reserve_ok(pr, 1)
    o.now.t = 10_000.0 - need + 1.0
    assert not o.reserve_ok(pr, 1, "architect look", say=True)
    assert "architect look: skipped: the render reserve needs" in o.lines[-1]
    o.deadline = None
    assert o.reserve_ok(pr, 1)


def test_an_unmeasured_build_takes_the_forecast_rate(tmp_path):
    b = {"levels": [{"id": "L0"}], "walls": [{"id": f"w{k}", "level_id": "L0"} for k in range(100)],
         "furniture": [{"id": f"f{k}", "level_id": "L0"} for k in range(40)], "decor": [], "rooms": []}
    (tmp_path / "building_final.json").write_text(json.dumps(b))
    pr = _run(out=tmp_path)
    o = _orch(deadline=None)
    est = o.build_estimate(pr)
    assert est == FC.build_seconds_of(b) and est > SC.S.EST_BUILD_S * 4         # 296 s, not 60 s


def test_forecast_rows_and_verdict():
    levels = [{"id": "L0", "elevation": 0.0}] + [{"id": f"L{k}", "elevation": 3.0 * k, "typical_of": "L0"}
                                                 for k in range(1, 7)]
    b = {"levels": levels, "walls": [{"id": f"w{k}", "level_id": "L0"} for k in range(200)],
         "furniture": [{"id": f"f_{lv['id']}_{k}", "level_id": lv["id"]} for lv in levels for k in range(10)],
         "decor": [], "rooms": []}
    assert FC.looked_levels(b) == ["L0"]
    assert FC.built_items(b) == 10                          # 7 identical floors: one example floor furnished
    hist = {"build": {"seconds": 1000.0, "source": "x"}}
    fc = FC.forecast("p", b, hist=hist, cpu={"questions": 24, "check_s": 30.0, "prepare_s": 200.0}, cameras=50)
    parts = [r["part"] for r in fc["rows"]]
    assert parts[0] == "boot and setup" and "first build" in parts and "second build (the decisions)" in parts
    first = next(r for r in fc["rows"] if r["part"] == "first build")
    assert first["seconds"] == 1000.0 and first["source"] == "measured"
    ai = next(r for r in fc["rows"] if r["part"] == "AI architect: open questions")
    assert ai["seconds"] == 2 * 1.5 * (FC.TASK_CALL_S + FC.CHECKS_PER_BATCH * 30.0) and ai["source"] == "cpu"
    assert fc["renders_fit"] and "agent round" in fc["verdict"]
    tight = FC.forecast("p", b, hist=hist, cpu={"questions": 80, "check_s": 600.0}, cameras=50, max_minutes=120)
    assert not tight["renders_fit"] and "render reserve" in tight["verdict"]
    assert "| **total** |" in FC.text(fc)


def test_history_takes_the_newest_record_and_the_longest_step(tmp_path):
    for job, when, steps in (("a", "2026-11-01T00:00:00Z", [500.0]), ("b", "2026-11-02T00:00:00Z", [300.0, 900.0])):
        d = tmp_path / job / "p"
        d.mkdir(parents=True)
        (d / "build.json").write_text(json.dumps({"status": "ok", "started_utc": when,
                                                  "steps": [{"rc": 0, "seconds": s} for s in steps]}))
    got = FC.history("p", roots=[tmp_path / "a", tmp_path / "b"])
    assert got["build"]["seconds"] == 900.0


def test_the_seed_file_keeps_a_buildings_default_search(tmp_path):
    """2 Nov 2026 (optimization 3): the default search of a building is kept beside it by content; the answers and the
    seed itself do not change the key; another building or brief does."""
    from wenart.blender import build as BD
    b = {"levels": [{"id": "L0"}], "walls": [{"id": "w1"}]}
    key = BD.seed_key(b, None)
    assert key == BD.seed_key(dict(b, agent_overrides={"architect": {"x": 1}}, architect_defaults={"a": 1}), None)
    assert key != BD.seed_key(dict(b, walls=[]), None) and key != BD.seed_key(b, {"style": "x"})
    path = tmp_path / BD.SEED_FILE
    assert BD.load_seed(path, key) is None
    BD.save_seed(path, key, {"E1:d_1": {"choice": "door_to_window"}}, {"O2:o_1": {"choice": "gap_to_door"}})
    got = BD.load_seed(path, key)
    assert got["defaults"] == {"E1:d_1": {"choice": "door_to_window"}} and got["refused"]["O2:o_1"]
    for k in range(BD.SEED_KEEP + 2):
        BD.save_seed(path, f"k{k}", {}, {})
    assert BD.load_seed(path, key) is None and BD.load_seed(path, f"k{BD.SEED_KEEP + 1}") is not None


def test_check_workers_follow_the_pods_cpu_budget(monkeypatch):
    from wenart.agent import architect_ai as A
    monkeypatch.delenv("WENART_CHECK_WORKERS", raising=False)
    monkeypatch.delenv("WENART_CPU_THREADS", raising=False)
    assert A.check_workers() == 1                          # this session and the tests: the halving
    monkeypatch.setenv("WENART_CPU_THREADS", "24")
    assert A.check_workers() == A.CHECK_WORKERS_MAX
    monkeypatch.setenv("WENART_CHECK_WORKERS", "3")
    assert A.check_workers() == 3


def test_big_loop_cycles_are_off_by_default():
    assert SC.Orchestrator.BIG_LOOP_CYCLES == 0 and SC.Orchestrator.BIG_LOOP_RESERVE_CYCLES == 0
