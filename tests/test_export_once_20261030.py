"""UL173 (30 Oct 2026, the user on the step times of real04 run 20261030-112241-full: "Do the 3D export only once, at
the end rest stays the same"). The 3D export ran four times (after the phase-5 build and again after the big loop's
rebuild, for the house and its variant). Every export of the final chain waits for its end: one per scene."""
import inspect
from types import SimpleNamespace

from wenart.run import scheduler as SC


def _fake(runs, built=("ok",)):
    calls = []
    fake = SimpleNamespace(runs=runs, opts=SimpleNamespace(smoke=False), defer_export=True, export_wanted=None,
                           out=lambda s: calls.append(("out", s)),
                           status_of=lambda pr, stage: "ok" if pr.name in built or "ok" in built else "failed",
                           can_start=lambda s: True, tools=None,
                           run_step=lambda pr, stage, step, cmd: calls.append(("export", pr.label)) or 0,
                           finish=lambda pr, stage, status, *a, **k: calls.append(("finish", pr.label, status)))
    fake.stage_export = lambda pr: SC.Orchestrator.stage_export(fake, pr)
    return fake, calls


def test_the_chain_asks_for_exports_and_runs_each_once_at_its_end(monkeypatch):
    monkeypatch.setattr(SC.S, "export", lambda tools, ref, variant=None: ["export", ref])
    base = SimpleNamespace(name="p", label="p", ref="p", variant=None, active=True, base=None)
    var = SimpleNamespace(name="p", label="p/v", ref="p/v", variant="v", active=True, base=base)
    fake, calls = _fake([base, var])
    for pr in (base, var, base, var):                        # phase 5, then the big loop's final stages again
        fake.stage_export(pr)
    assert not [c for c in calls if c[0] == "export"] and fake.export_wanted == [base, var]
    fake.defer_export = False
    SC.Orchestrator.exports_at_end(fake)
    assert [c for c in calls if c[0] == "export"] == [("export", "p"), ("export", "p/v")]
    assert ("finish", "p", "ok") in calls and ("finish", "p/v", "ok") in calls and fake.export_wanted == []


def test_an_inactive_or_unbuilt_scene_is_not_exported(monkeypatch):
    monkeypatch.setattr(SC.S, "export", lambda tools, ref, variant=None: ["export", ref])
    gone = SimpleNamespace(name="q", label="q", ref="q", variant=None, active=False, base=None)
    fake, calls = _fake([gone])
    fake.stage_export(gone)
    fake.defer_export = False
    SC.Orchestrator.exports_at_end(fake)
    assert not [c for c in calls if c[0] == "export"]


def test_the_final_chain_defers_and_exports_at_its_end_whatever_happens():
    src = inspect.getsource(SC.Orchestrator.final_chain)
    assert src.index("self.defer_export = True") < src.index("self.phase5()")
    # 30 Oct 2026 (real04 run 20261030-181158-full: the deadline cut the export waiting behind Argus AI's last pass):
    # the exports run after the big loop and the variants, before argus_final, and again (a no-op) in the finally
    assert src.index("self.variants_again(url)") < src.index("self.exports_at_end()") < src.index("self.argus_final")
    assert src.index("finally:") < src.rindex("self.exports_at_end()")
