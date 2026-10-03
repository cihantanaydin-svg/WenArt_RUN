"""``python -m wenart.run``: the subcommands' dispatch (docs/milestone6.md §2.1, docs/milestone7.md §9.2)."""
from __future__ import annotations

import sys
import types

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
