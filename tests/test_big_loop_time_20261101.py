"""1 Nov 2026 (real04 run 20261101-093151-full): the big loop's cycle took 41 min where its start test counted about 14
(the round's full re-build, its planner calls and the cycle's looks left out); the open-kitchen variant's build after the
loop then left no time for its render and the 3D exports (exit 1). A cycle now starts only when its measured need and
the work after the loop (the variants again, the 3D exports) fit before the deadline; a variant builds again only when
its render fits too; an export starts only when its measured seconds fit. CPU only."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))

from wenart.run import scheduler as SC  # noqa: E402


class Clock:
    def __init__(self, t=0.0):
        self.t = t

    def __call__(self):
        return self.t


def _run(name, parts=None, base=None, views=10, no_views=False, active=True):
    return SimpleNamespace(name=name, label=name, parts=dict(parts or {}), previous={}, records={}, base=base,
                           views=views, no_views=no_views, active=active, agent_loop=None, out=Path("/nonexistent"))


def _orch(runs, deadline, now=0.0):
    o = SC.Orchestrator.__new__(SC.Orchestrator)
    o.runs = runs
    o.deadline = deadline
    o.now = Clock(now)
    o._speed = {"speed": 1.0}
    o.previous = lambda pr, stage: None
    o.final_estimate = lambda pr: 1000.0
    o.lines = []
    o.out = o.lines.append
    return o


def test_after_loop_counts_every_variant_build_render_stages_and_every_export():
    base = _run("p", {"export": [{"name": "export", "rc": 0, "seconds": 209.0}]})
    var = _run("p/v", {"build": [{"name": "build", "rc": 0, "seconds": 570.0}],
                       "render": [{"name": "render", "rc": 0, "seconds": 349.0}]}, base=base)
    o = _orch([base, var], deadline=None)
    after = o.after_loop_s(base)
    assert after == 209.0 + 570.0 + 349.0 + o.VARIANT_STAGES_S + o.EXPORT_DEFAULT_S
    assert o.after_loop_s(var) == o.EXPORT_DEFAULT_S        # a variant has no variants of its own


def test_a_failed_export_step_is_no_measurement_and_the_run_before_is_used():
    base = _run("p", {"export": [{"name": "export", "rc": 124, "seconds": 91.0}]})
    o = _orch([base], deadline=None)
    assert o.export_estimate(base) == o.EXPORT_DEFAULT_S
    o.previous = lambda pr, stage: SimpleNamespace(steps=[{"name": "export", "rc": 0, "seconds": 209.0}])
    assert o.export_estimate(base) == 209.0


def test_the_cycle_counts_the_mean_round_the_look_and_the_changed_views():
    from wenart.agent.loop import FINAL_ROUND_SHARE
    from wenart.audit import argus_ai as AX
    base = _run("p")
    base.agent_loop = SimpleNamespace(rounds=[{"seconds": 1600.0}, {"seconds": 1700.0}])
    o = _orch([base], deadline=None)
    need = o.big_loop_cycle_s(base)
    assert need == AX.CYCLE_BUDGET_S + 1650.0 + FINAL_ROUND_SHARE * (1000.0 + o.BIG_LOOP_MEASURE_S)
    assert need > 2400.0                                       # the real04 cycle took 2456 s


def test_the_real04_timeline_starts_no_cycle_and_leaves_the_variant_and_exports_their_time():
    """real04 run 093151: the loop's first measure ended about 52 min before the scheduler's deadline; the cycle took
    41 min and the variant's build 10 min, so its render and the exports got no time."""
    base = _run("p", {"export": [{"name": "export", "rc": 0, "seconds": 209.0}]})
    base.agent_loop = SimpleNamespace(rounds=[{"seconds": 1654.0}] * 3)
    var = _run("p/v", {"build": [{"name": "build", "rc": 0, "seconds": 570.0}],
                       "render": [{"name": "render", "rc": 0, "seconds": 349.0}]}, base=base)
    o = _orch([base, var], deadline=3150.0, now=0.0)
    fits, need, after = o.big_loop_cycle_fits(base)
    assert not fits and need + after > 3150.0
    assert after < 3150.0                                      # without the cycle the work after the loop fits
    o.now.t = -3000.0                                          # an hour more: the cycle fits
    assert o.big_loop_cycle_fits(base)[0]


def test_the_loop_stops_before_a_cycle_that_would_pass_the_deadline(tmp_path):
    from wenart.agent import judge as JD  # noqa: F401  - the loop writes through it

    class FakeLoop:
        stop = {"round": 3}
        rounds = []

        def __init__(self):
            self.final_rounds = 0

        def measure(self, k, only=None):
            return {"score": {"score": 30.0, "rubric": 2.4, "counts": {}}, "rows": [{"view": "v",
                                                                                    "client_ready_score": 2}],
                    "findings": []}

        def final_round(self, k):
            self.final_rounds += 1
            return {"accepted": 1, "rerun_from": "refit", "views": ["v"], "stop": None, "stage_note": "n"}

    calls = []
    pr = SimpleNamespace(agent_loop=FakeLoop(), active=True, name="p", out=tmp_path)
    fake = SimpleNamespace(runs=[pr], out=lambda s: calls.append(s), BIG_LOOP_CYCLES=4,
                           big_loop_topdown=lambda p: None,
                           big_loop_cycle_fits=lambda p: (False, 2800.0, 1700.0),
                           argus_cycle=lambda p, url, cycle: calls.append(f"argus {cycle}"),
                           agent_note_after_final=lambda p, n: None,
                           final_stages_again=lambda p, url: calls.append("final stages"),
                           rollback_round=lambda p, k, why: 0,
                           agent_rerun=lambda p, stage, views, k, final: {"status": "ok"})
    SC.Orchestrator.final_critical_rounds(fake, "url")
    rec = json.loads((tmp_path / "orchestrator" / "big_loop.json").read_text())
    assert rec["stop"].startswith("cycle 1: time:") and "47 min" in rec["stop"] and "28 min" in rec["stop"]
    assert pr.agent_loop.final_rounds == 0 and not [c for c in calls if str(c).startswith("argus")]


def test_a_variant_is_not_built_again_when_its_render_would_not_fit():
    base = _run("p")
    var = _run("p/v", {"build": [{"name": "build", "rc": 0, "seconds": 570.0}],
                       "render": [{"name": "render", "rc": 0, "seconds": 349.0}]}, base=base)
    var.records["build"] = SimpleNamespace(status="ok")
    o = _orch([base, var], deadline=600.0, now=0.0)
    built = []
    o.stage_build = lambda vr: built.append(vr.name)
    SC.Orchestrator.variants_again(o, "url")
    assert built == [] and any("not built again" in line for line in o.lines)


def test_an_export_is_not_started_when_its_measured_seconds_do_not_fit():
    base = _run("p", {"export": [{"name": "export", "rc": 0, "seconds": 209.0}]})
    o = _orch([base], deadline=150.0, now=0.0)
    o.opts = SimpleNamespace(smoke=False)
    o.defer_export = False
    started, finished = [], []
    o.run_step = lambda *a, **k: started.append(a) or 0
    o.not_started = lambda pr, stage, what="": finished.append(stage)
    SC.Orchestrator.stage_export(o, base)
    assert started == [] and finished == ["export"]
