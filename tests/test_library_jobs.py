"""Milestone 12 track B: the two audit pods' job scripts (docs/milestone12.md §8 P2, P3) follow the job conventions
(CLAUDE.md engineering conventions; scripts/jobs/agent_check.sh): bash strict mode with an error trap, logs in
/workspace/logs, results copied after every step and from the EXIT trap, the deadline passed on, resumable steps,
the vLLM server stopped by the EXIT trap, and P3 never writes the session's catalogues (copies only)."""
import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
JOBS = ("scripts/jobs/library_audit_render.sh", "scripts/jobs/library_audit_judge.sh")


def gpu_run():
    spec = importlib.util.spec_from_file_location("gpu_run", REPO / "scripts" / "gpu_run.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("job", JOBS)
def test_conventions(job):
    text = (REPO / job).read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash\n")
    assert "set -Eeuo pipefail" in text and "trap 'on_error $LINENO" in text and "trap 'on_exit' EXIT" in text
    assert "LOGS=$WS/logs" in text and "tee -a" in text
    assert "copy_results\n  return 0" in text                     # after every step
    assert 'WENART_DEADLINE' in text and "--deadline" in text
    assert f"--job {job}" in text and "--max-minutes" in text     # the command line for the lead is in the header
    assert os.access(REPO / job, os.X_OK)
    subprocess.run(["bash", "-n", str(REPO / job)], check=True)
    assert gpu_run().validate_job_path(job) == job


def test_p2_renders_with_the_audit_cli_and_resumes():
    text = (REPO / JOBS[0]).read_text(encoding="utf-8")
    assert "-m wenart.assets audit render" in text and "-m wenart.assets audit code" in text
    assert "--work \"$WORK\"" in text and "AUDIT_ROOT:-$WS/library-audit" in text
    assert "-k audit_render" in text


def test_p3_writes_copies_of_the_catalogues_only():
    text = (REPO / JOBS[1]).read_text(encoding="utf-8")
    assert "--serve" in text and "--pass both" in text and "kill_vllm" in text
    write = text[text.index("run_step write"):text.index("run_step gpu-tests")]
    assert "--catalog \"$AUDIT/catalogue/catalog_library.json\"" in write
    assert "--polyhaven \"$AUDIT/catalogue/catalog.json\"" in write
    assert "measure.json" in text and "run pod P2" in text


def test_p3_stops_without_the_render_of_p2(tmp_path):
    env = dict(os.environ, WENART_WS=str(tmp_path), WENART_RESULTS=str(tmp_path / "res"), JOB_ID="t",
               AUDIT_MODEL_KEY="agent", WENART_PY="python3")
    (tmp_path / "repo").symlink_to(REPO)
    proc = subprocess.run(["bash", str(REPO / JOBS[1])], env=env, capture_output=True, text=True, timeout=120)
    assert proc.returncode == 1
    assert "run pod P2" in proc.stdout
    assert (tmp_path / "res" / "library_audit_judge-t.log").is_file()     # the EXIT trap copied the log
