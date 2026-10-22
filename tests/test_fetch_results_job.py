"""scripts/jobs/fetch_results.sh (22 Oct 2026): copy an earlier job's results from the volume into this job's
results, so the runner collects them when the earlier pod stopped itself with no runner attached (pod P6b)."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

JOB = Path(__file__).resolve().parents[1] / "scripts" / "jobs" / "fetch_results.sh"


def _run(ws: Path, **env_extra):
    env = dict(os.environ, WENART_WS=str(ws), JOB_ID="fetchjob", WENART_RESULTS=str(ws / "jobs" / "fetchjob" / "results"))
    env.update(env_extra)
    return subprocess.run(["bash", str(JOB)], env=env, capture_output=True, text=True, timeout=60)


def _old_job(ws: Path) -> None:
    res = ws / "jobs" / "old" / "results"
    (res / "final" / "real03" / "3d").mkdir(parents=True)
    (res / "final" / "real03" / "cam_1_final_preview.jpg").write_bytes(b"jpg")
    (res / "final" / "real03" / "3d" / "real03.glb").write_bytes(b"glb")
    (res / "run_manifest.json").write_text("{}")
    (ws / "jobs" / "old" / "status.json").write_text('{"state": "done", "exit_code": 1}')
    (ws / "logs").mkdir(parents=True)
    (ws / "logs" / "old.log").write_text("pod entry log")


def test_fetch_results_job_contract():
    subprocess.run(["bash", "-n", str(JOB)], check=True)
    text = JOB.read_text(encoding="utf-8")
    assert text.startswith("#!/usr/bin/env bash") and "set -Eeuo pipefail" in text and os.access(JOB, os.X_OK)
    assert "LOGS=$WS/logs" in text and "trap " in text and "ERR" in text
    assert " rm " not in text and " mv " not in text                 # nothing is moved or deleted on the volume


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_fetch_results_copies_the_earlier_jobs_results(tmp_path):
    _old_job(tmp_path)
    proc = _run(tmp_path, FETCH_JOB="old")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    out = tmp_path / "jobs" / "fetchjob" / "results"
    assert (out / "final" / "real03" / "cam_1_final_preview.jpg").read_bytes() == b"jpg"
    assert (out / "final" / "real03" / "3d" / "real03.glb").is_file()
    assert (out / "fetched_status.json").read_text().startswith('{"state": "done"')
    assert (out / "fetched_pod_entry.log").read_text() == "pod entry log"
    assert (tmp_path / "jobs" / "old" / "results" / "run_manifest.json").is_file()      # the source stays
    # without the 3D files
    proc = _run(tmp_path, FETCH_JOB="old", FETCH_SKIP_3D="1", WENART_RESULTS=str(tmp_path / "r2"))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert (tmp_path / "r2" / "run_manifest.json").is_file() and not (tmp_path / "r2" / "final" / "real03" / "3d").exists()


@pytest.mark.skipif(not Path("/bin/bash").exists(), reason="bash needed")
def test_fetch_results_refuses_a_missing_or_bad_job(tmp_path):
    assert _run(tmp_path).returncode == 2
    assert _run(tmp_path, FETCH_JOB="../etc").returncode == 2
    assert _run(tmp_path, FETCH_JOB="nojob").returncode == 3
