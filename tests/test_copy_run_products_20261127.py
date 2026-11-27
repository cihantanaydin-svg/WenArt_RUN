"""The run-product folders carry only this run's files (27 Nov 2026, check pod 2smyy0ktv63y40).

A structure run (no agent, no polish, no gate) took 154 MB of real06's agent round images of 30 Oct from the
project's output folder on the volume, and the pack hit the runner's size cap. The agent's images and before/after
sheets, its previews and the polish, gate, detect and export folders now copy only files written at or after this
run's start, unless a stage that owns the folder was reused; the other folders and hand runs copy as before.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from wenart.run import copy as CP
from wenart.run.projects import REPO_ROOT, public_project

DAY = 86400


def iso(t: float) -> str:
    return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def put(path: Path, data, age: float = 0.0) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, (dict, list)):
        path.write_text(json.dumps(data), encoding="utf-8")
    else:
        path.write_bytes(data)
    t = time.time() - age
    os.utime(path, (t, t))
    return path


def record(out: Path, stage: str, run_id, started, status: str = "ok") -> None:
    rec = {"kind": "stage_record", "project": out.name, "stage": stage, "status": status, "run_id": run_id}
    if started is not None:
        rec["started_utc"] = started
    put(out / "run" / f"{stage}.json", rec)


def project(tmp_path):
    results = tmp_path / "results"
    ref = replace(public_project("synthetic-01", results, REPO_ROOT), name="p", out_dir=tmp_path / "out" / "p")
    out = ref.out_dir
    # an earlier run's agent images, polish and gate files, and the orchestrator's own records
    put(out / "orchestrator" / "images" / "r1_cam_a_before.jpg", b"old", age=28 * DAY)
    put(out / "orchestrator" / "compare" / "cam_a.jpg", b"old", age=28 * DAY)
    put(out / "agent" / "previews" / "cam_a_preview.jpg", b"old", age=28 * DAY)
    put(out / "polish" / "polish_manifest.json", {"old": True}, age=28 * DAY)
    put(out / "gate" / "gate_validation.json", {"old": True}, age=28 * DAY)
    put(out / "orchestrator" / "architect_answers.json", {"answers": []}, age=28 * DAY)
    return results, ref, out


def test_an_earlier_runs_agent_polish_and_gate_files_stay_on_the_volume(tmp_path, capsys):
    results, ref, out = project(tmp_path)
    now = time.time()
    record(out, "agent", "run-old", iso(now - 28 * DAY))             # the agent of 30 Oct, not of this run
    record(out, "pipeline_final", "run-new", iso(now - 3600))
    record(out, "build", "run-new", iso(now - 600))
    put(out / "orchestrator" / "images" / "r1_cam_b_before.jpg", b"new")   # one image this run made
    CP.copy_project(ref)
    agent = results / "agent" / "p"
    assert (agent / "images" / "r1_cam_b_before.jpg").is_file()
    assert not (agent / "images" / "r1_cam_a_before.jpg").exists()
    assert not (agent / "compare").exists() and not (agent / "previews").exists()
    assert not (results / "polish" / "p").exists() and not (results / "gate" / "p").exists()
    # a folder that is no run product (the architect's answers live beside the agent's records) is copied as before
    assert (agent / "architect_answers.json").is_file()
    err = capsys.readouterr().err
    assert "earlier run in orchestrator/images/ left out" in err and "polish/" in err
    assert all(p.is_file() for p in (out / "orchestrator" / "images").iterdir())       # nothing deleted


def test_a_reused_stage_keeps_its_earlier_files(tmp_path):
    results, ref, out = project(tmp_path)
    now = time.time()
    record(out, "pipeline_final", "run-new", iso(now - 3600))
    record(out, "polish", "run-new", iso(now - 600), status="reused")
    CP.copy_project(ref)
    assert (results / "polish" / "p" / "polish_manifest.json").is_file()
    assert not (results / "gate" / "p").exists()


def test_a_hand_run_without_run_ids_copies_everything(tmp_path):
    results, ref, out = project(tmp_path)
    record(out, "pipeline", None, None)
    CP.copy_project(ref)
    assert (results / "agent" / "p" / "images" / "r1_cam_a_before.jpg").is_file()
    assert (results / "polish" / "p" / "polish_manifest.json").is_file()
    assert (results / "gate" / "p" / "gate_validation.json").is_file()


def test_the_window_is_this_runs_earliest_record_and_the_margin_covers_clock_skew(tmp_path):
    out = tmp_path / "p"
    now = time.time()
    record(out, "intake", "run-new", iso(now - 7200), status="skipped")
    record(out, "build", "run-new", iso(now - 600))
    record(out, "agent", "run-old", iso(now - 9 * DAY))
    start, reused = CP.run_window(out)
    assert abs(start - (now - 7200)) < 2 and reused == frozenset()
    young = put(tmp_path / "x.jpg", b"x", age=7200 + CP.RUN_START_MARGIN_S - 60)    # within the margin
    old = put(tmp_path / "y.jpg", b"x", age=7200 + CP.RUN_START_MARGIN_S + 60)
    assert not CP.earlier_run_file("orchestrator/images", young, (start, reused))
    assert CP.earlier_run_file("orchestrator/images", old, (start, reused))
    assert not CP.earlier_run_file("orchestrator", old, (start, reused))          # not a run-product folder
    assert not CP.earlier_run_file("polish", old, (start, frozenset({"polish"})))
    assert CP.run_window(tmp_path / "none") == (None, frozenset())
