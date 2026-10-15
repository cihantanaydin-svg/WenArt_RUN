"""``python -m wenart.run``: the subcommands' dispatch (docs/milestone6.md §2.1, docs/milestone7.md §9.2)."""
from __future__ import annotations

import sys
import types

import pytest

from wenart.run.__main__ import main as run_main


def test_prep_forwards_every_argument(monkeypatch):
    seen = {}

    def fake_main(argv):
        seen["argv"] = argv
        return 3

    monkeypatch.setitem(sys.modules, "wenart.run.prep", types.SimpleNamespace(main=fake_main))
    import wenart.run
    monkeypatch.setattr(wenart.run, "prep", sys.modules["wenart.run.prep"], raising=False)
    assert run_main(["prep", "--projects", "real01", "--help", "--phase", "all"]) == 3
    assert seen["argv"] == ["--projects", "real01", "--help", "--phase", "all"]


def test_prep_without_the_module_is_a_clean_error(monkeypatch, capsys):
    import wenart.run
    monkeypatch.setitem(sys.modules, "wenart.run.prep", None)          # import fails like a missing module
    monkeypatch.delattr(wenart.run, "prep", raising=False)
    assert run_main(["prep"]) == 2
    assert "wenart.run.prep cannot be imported" in capsys.readouterr().err


def test_pod_flags_for_the_camera_replay_the_white_balance_and_the_rounds(monkeypatch):
    """Milestone 13 (round 2): ``pod --cameras-from PATH --cameras-extra --white-balance project|kelvin:K`` reach
    RunOptions; the defaults leave the environment path (None / False) and the brief in charge; ``--agent-rounds``
    defaults to 3 (K4, the user's rule of 12 Oct 2026 = wenart.agent.loop.MAX_ROUNDS)."""
    from wenart.run import scheduler as SC
    seen = []
    monkeypatch.setattr(SC, "run_pod", lambda opts: seen.append(opts) or 0)
    assert run_main(["pod", "--projects", "synthetic-01", "--results", "/tmp/r"]) == 0
    o = seen[-1]
    assert o.cameras_from is None and o.cameras_extra is False and o.white_balance is None and o.agent_rounds == 3
    assert run_main(["pod", "--projects", "synthetic-01", "--results", "/tmp/r", "--cameras-from",
                     "results/renders/{name}/scene_manifest.json", "--cameras-extra", "--white-balance", "kelvin:5300",
                     "--agent-rounds", "2"]) == 0
    o = seen[-1]
    assert o.cameras_from == "results/renders/{name}/scene_manifest.json" and o.cameras_extra is True
    assert o.white_balance == "kelvin:5300" and o.agent_rounds == 2
    from wenart.agent import loop as LP
    assert SC.RunOptions().agent_rounds == LP.MAX_ROUNDS == 3
    # Round-2 review: a white balance that render.py would refuse is an argparse error (exit 2) at the pod CLI,
    # not a failed render stage hours later: only project | kelvin:K within stages.KELVIN_RANGE.
    assert run_main(["pod", "--projects", "synthetic-01", "--results", "/tmp/r", "--white-balance", "project"]) == 0
    assert seen[-1].white_balance == "project"
    assert run_main(["pod", "--projects", "synthetic-01", "--results", "/tmp/r", "--white-balance", "kelvin:4800.0"]) == 0
    assert seen[-1].white_balance == "kelvin:4800"
    for bad in ("auto", "kelvin:100", "kelvin:x", "fixed:1,1,1", ""):
        with pytest.raises(SystemExit) as err:
            run_main(["pod", "--projects", "synthetic-01", "--results", "/tmp/r", "--white-balance", bad])
        assert err.value.code == 2, bad
