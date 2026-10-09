"""The CPU parts of the pod G1 model check (wenart/agent/podcheck.py, scripts/jobs/agent_check.sh;
docs/milestone11.md §11, §12): the repetition measure, the planted errors, the job script's conventions, and the
scheduler's sleep rule for the agent server (sleep below 80 GB of VRAM, WENART_AGENT_SLEEP on / off)."""
from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path

import pytest

from wenart.agent import podcheck as PC
from wenart.run import scheduler as SC

ROOT = Path(__file__).resolve().parents[1]
JOB = ROOT / "scripts" / "jobs" / "agent_check.sh"


def test_repetition():
    loop = " ".join(["the sofa faces the TV unit and the coffee table"] * 6)
    assert PC.repetition(loop)["looped"] is True
    text = " ".join(f"word{i}" for i in range(200))
    assert PC.repetition(text) == {"ngram": PC.repetition(text)["ngram"], "count": 1, "looped": False, "words": 200}
    assert PC.repetition("")["count"] == 0


def test_plant_errors_on_the_committed_real02_building():
    b = json.loads((ROOT / "results" / "furniture" / "real02" / "building_final.json").read_text())
    planted_b, planted = PC.plant_errors(b)
    assert [p["what"].split()[0] for p in planted] == ["bed", "sofa"]
    for item in planted:
        old = next(f for f in b["furniture"] if f["id"] == item["piece_id"])
        new = next(f for f in planted_b["furniture"] if f["id"] == item["piece_id"])
        assert (new["footprint"]["rotation_deg"] - old["footprint"]["rotation_deg"]) % 360 == 180
    assert b["furniture"] != planted_b["furniture"]


def test_the_job_script_follows_the_conventions():
    text = JOB.read_text()
    assert text.startswith("#!/usr/bin/env bash\n") and "\nset -Eeuo pipefail\n" in text
    assert re.search(r"^trap 'on_error \$LINENO \"\$BASH_COMMAND\"' ERR$", text, re.M)
    assert re.search(r"^trap 'on_exit' EXIT$", text, re.M) and os.access(JOB, os.X_OK)
    assert "LOGS=$WS/logs" in text and 'exec > >(tee -a "$LOG") 2>&1' in text
    assert subprocess.run(["bash", "-n", str(JOB)]).returncode == 0
    for step in ("podcheck --key", "--mtp", "--planted real02", "tests/gpu/test_agent.py", "pod_setup_polish.sh",
                 "export HF_HUB_OFFLINE=1"):
        assert step in text, step
    assert text.index("run_step setup") < text.index("export HF_HUB_OFFLINE=1") \
        < text.index('-m wenart.agent.podcheck') < text.index("-m pytest -m gpu")
    # scripts/gpu_run.py accepts the job path
    import importlib.util
    spec = importlib.util.spec_from_file_location("gpu_run_for_test", ROOT / "scripts" / "gpu_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.JOB_RE.match("scripts/jobs/agent_check.sh")


@pytest.mark.parametrize("mem,env,want", [(97887, None, False), (49140, None, True), (0, None, False),
                                          (97887, "on", True), (49140, "off", False)])
def test_the_agent_server_sleeps_below_80_gb(tmp_path, monkeypatch, mem, env, want):
    if env is None:
        monkeypatch.delenv("WENART_AGENT_SLEEP", raising=False)
    else:
        monkeypatch.setenv("WENART_AGENT_SLEEP", env)
    orch = SC.Orchestrator(SC.RunOptions(results=tmp_path, orchestrator=True), gpu_mem=lambda: mem,
                           check_models={}, out=lambda s: None)
    assert orch.agent_sleep_mode() is want
