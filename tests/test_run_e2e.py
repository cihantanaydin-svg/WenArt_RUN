"""Smoke end to end of the one-command full run on the CPU (docs/milestone6.md §2.5).

What: ``python -m wenart.run pod --profile smoke`` with the fake VLM server
(``tests/fakes/fake_vlm.py``) on synthetic-04 + synthetic-02 + two private
projects + the realism A/B on synthetic-01 (2 cameras, controls on
synthetic-01), every output in temp folders outside the repo (paths are then
absolute, §1.1); then ``python -m wenart.run copy``. The private projects:

- ``selftest-02`` (``--private-selftest``): a private copy of synthetic-02,
  expected ``needs_review``;
- ``real-01``: a copy of synthetic-04 uploaded into the temp private root,
  expected ``ok``: the private path through intake, build, render, check and
  report with absolute paths and the allow-list (no gate/polish in smoke).

Checks the run manifests, the stage records, the reports, the private
allow-list and that nothing private reaches ``$RESULTS`` or the job log.

Marked ``slow`` (Blender renders on the CPU, several minutes); skipped without
Blender.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from fakes.fake_vlm import FakeVLM
from wenart.blender import cli as blender_cli
from wenart.run import state as ST

ROOT = Path(__file__).resolve().parents[1]
BLENDER = blender_cli.find_blender()
pytestmark = [pytest.mark.slow, pytest.mark.skipif(BLENDER is None, reason="no Blender binary")]
ALIAS = "selftest-02"
REAL = "real-01"                       # a copy of synthetic-04 in the temp private root (never committed)
PRIVATE = (REAL, ALIAS)
ALLOWED = ("ok", "reused", "warning", "skipped")
PRIVATE_ALLOWED = re.compile(r"^(final/(final_report\.md|final_manifest\.json|[^/]+_final_preview\.jpg|contact_[^/]+\.jpg)"
                             r"|run/[^/]+\.json)$")


@pytest.fixture(scope="module")
def smoke(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("smoke")
    paths = {k: tmp / k for k in ("results", "outputs", "pp", "po", "pr", "job")}
    # The user's upload of real-01 (docs/intake.md): here the synthetic-04 folder, truth/ included (the intake
    # never stages truth/).
    shutil.copytree(ROOT / "projects" / "synthetic-04", paths["pp"] / REAL)
    assets = Path(os.environ["WENART_ASSETS"]) if os.environ.get("WENART_ASSETS") else (
        ROOT / "assets" if (ROOT / "assets").is_dir() else tmp / "assets")
    env = {k: v for k, v in os.environ.items()
           if k not in ("WENART_DEADLINE", "WENART_JOB_DIR", "WENART_OUTPUTS", "WENART_COPY_LOCK")}
    env.update(CHECK_MODELS="qwen glm", JOB_ID="smoke")
    common = ["--outputs", str(paths["outputs"]), "--private", REAL, "--private-selftest", "--private-root",
              str(paths["pp"]), "--private-outputs", str(paths["po"]), "--private-results", str(paths["pr"])]
    with FakeVLM() as url:
        pod = subprocess.run(
            [sys.executable, "-m", "wenart.run", "pod", "--projects", "synthetic-04 synthetic-02",
             "--ab", "synthetic-01", "--ab-controls", "synthetic-01", "--results", str(paths["results"]),
             "--profile", "smoke", "--vlm-url", url, "--job-dir", str(paths["job"]), "--assets", str(assets)] + common,
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=5400)
    copy = subprocess.run(
        [sys.executable, "-m", "wenart.run", "copy", "--projects", "synthetic-04 synthetic-02", "--ab", "synthetic-01",
         "--results", str(paths["results"])] + common,
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    return {"pod": pod, "copy": copy, **paths}


def _manifest(smoke) -> dict:
    return json.loads((smoke["results"] / "run_manifest.json").read_text(encoding="utf-8"))


def _private_manifest(smoke) -> dict:
    return json.loads((smoke["job"] / "results-private" / "_run_manifest.json").read_text(encoding="utf-8"))


def _records(out: Path, run_id: str) -> dict:
    found = {}
    for path in sorted((out / "run").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("run_id") == run_id:
            found[data["stage"]] = data
    return found


def _check_ok_project(out: Path, records: dict) -> None:
    """The stage records and outputs of a project that ended ok in the smoke profile."""
    for stage in ("pipeline", "fit", "style", "assets", "layout", "decor", "refit", "build", "render", "controls",
                  "expected", "check", "combine", "report"):
        assert stage in records, stage
        assert records[stage]["status"] in ALLOWED, (stage, records[stage]["status"], records[stage]["note"])
    for stage in ("gate", "polish"):
        assert records[stage]["status"] == "skipped" and records[stage]["note"] == "smoke profile"
    assert records["photos"]["note"] == "no style photos"
    for rec in records.values():
        if rec["status"] == "skipped":
            assert rec["note"] in ST.SKIP_REASONS
    # Paths outside the repo are recorded absolute (§1.1): the outputs are in a temp folder.
    fit_inputs = list(records["fit"]["inputs"])
    assert str(out / "building.json") in fit_inputs and "wenart/furniture/catalog.json" in fit_inputs
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    assert scene["cameras"] and {c.get("policy") for c in scene["cameras"]} == {"search"}
    assert scene["camera_policy"] == "search" and isinstance(scene["search_seconds"], (int, float))
    assert Path(scene["building"]).is_absolute() and Path(scene["building"]).parent == out
    final = json.loads((out / "final" / "final_manifest.json").read_text(encoding="utf-8"))
    render = json.loads((out / "renders" / "render_manifest.json").read_text(encoding="utf-8"))
    assert final["status"] == "ok" and final["summary"]["views"] == len(render["renders"]) == len(scene["cameras"])
    assert (out / "final" / "final_report.md").is_file()


def test_the_run_ends_ok(smoke):
    pod = smoke["pod"]
    assert pod.returncode == 0, pod.stdout[-6000:] + pod.stderr[-3000:]
    m = _manifest(smoke)
    assert m["kind"] == "run_manifest" and m["profile"] == "smoke" and m["final"] and m["exit_code"] == 0
    states = {p["name"]: p for p in m["projects"]}
    assert states["synthetic-04"]["state"] == "ok"
    assert states["synthetic-02"]["state"] == "needs_review"
    # Private aliases: their state only in the public manifest (§2.3).
    assert states[REAL] == {"name": REAL, "private": True, "state": "ok"}
    assert states[ALIAS] == {"name": ALIAS, "private": True, "state": "needs_review"}
    assert m["totals"] == {"ok": 2, "needs_review": 2, "failed": 0, "incomplete": 0}
    assert m["tests"] == []                                  # no GPU tests in the smoke profile
    assert [ph["phase"] for ph in m["phases"]] == list(range(1, 12))
    assert m["test_lists"]["SELFTEST_TEST_ALIAS"] == ALIAS and REAL not in " ".join(m["test_lists"].values())


def test_stage_records_of_the_ok_project(smoke):
    m = _manifest(smoke)
    out = smoke["outputs"] / "synthetic-04"
    records = _records(out, m["run_id"])
    _check_ok_project(out, records)
    assert records["intake"]["note"] == "private only"
    # A project folder inside the repo stays repo-relative (§1.1).
    assert list(records["pipeline"]["inputs"]) == ["projects/synthetic-04"]
    final = json.loads((out / "final" / "final_manifest.json").read_text(encoding="utf-8"))
    assert final["private"] is False and list((out / "final").glob("*_plan.jpg"))


def test_private_project_runs_through_build_render_and_report(smoke):
    m = _manifest(smoke)
    out = smoke["po"] / REAL
    records = _records(out, m["run_id"])
    _check_ok_project(out, records)
    assert records["intake"]["status"] == "ok"
    # The staged copy is the project folder: absolute, under the private outputs (§7.1).
    staged = out / "input" / REAL
    assert list(records["pipeline"]["inputs"]) == [str(staged)] and (staged / "3_kat_plani.dxf").is_file()
    assert not (staged / "truth").exists()
    intake = json.loads((out / "intake_manifest.json").read_text(encoding="utf-8"))
    assert intake["status"] == "ok" and intake["alias"] == REAL
    building = json.loads((out / "building.json").read_text(encoding="utf-8"))
    assert building["status"] == "ok" and building["project"]["id"] == REAL
    # The report of a private project names plan crops and debug images, never copies them (§7.4).
    final = json.loads((out / "final" / "final_manifest.json").read_text(encoding="utf-8"))
    assert final["private"] is True
    assert not list((out / "final").glob("*_plan.jpg")) and not (out / "final" / "debug").exists()
    assert list((out / "final").glob("*_final_preview.jpg"))
    # The private run manifest holds the details; the stages there are this run's.
    pm = _private_manifest(smoke)
    assert pm["kind"] == "private_run_manifest" and [p["name"] for p in pm["projects"]] == [REAL, ALIAS]
    entry = pm["projects"][0]
    assert entry["state"] == "ok" and entry["out_dir"] == str(out)
    assert {s["stage"] for s in entry["stages"]} >= {"intake", "pipeline", "build", "render", "check", "report"}


def test_needs_review_projects(smoke):
    m = _manifest(smoke)
    out = smoke["outputs"] / "synthetic-02"
    records = _records(out, m["run_id"])
    assert records["pipeline"]["status"] == "needs_review"
    assert "build" not in records and "layout" not in records
    assert (out / "final" / "final_report.md").is_file()
    final = json.loads((out / "final" / "final_manifest.json").read_text(encoding="utf-8"))
    assert final["status"] == "needs_review" and final["reasons"]
    private = _records(smoke["po"] / ALIAS, m["run_id"])
    assert private["intake"]["status"] == "ok" and private["pipeline"]["status"] == "needs_review"
    assert "build" not in private and (smoke["pp"] / ALIAS).is_dir()      # the self-test upload (synthetic-02)
    assert (smoke["po"] / ALIAS / "intake_manifest.json").is_file()
    final = json.loads((smoke["po"] / ALIAS / "final" / "final_manifest.json").read_text(encoding="utf-8"))
    assert final["status"] == "needs_review" and final["private"] is True


@pytest.mark.parametrize("alias", PRIVATE)
def test_private_files_stay_private(smoke, alias):
    pr = smoke["pr"] / alias
    files = [p.relative_to(pr).as_posix() for p in pr.rglob("*") if p.is_file()]
    assert "final/final_report.md" in files and "final/final_manifest.json" in files
    assert any(f.startswith("run/") for f in files)
    if alias == REAL:
        assert any(f.endswith("_final_preview.jpg") for f in files)
    bad = [f for f in files if not PRIVATE_ALLOWED.match(f)]
    assert not bad, bad
    for f in files:
        if f.startswith("run/"):
            assert "inputs" not in json.loads((pr / f).read_text(encoding="utf-8"))
    link = smoke["job"] / "results-private" / alias
    assert link.is_symlink() and link.resolve() == pr.resolve()


def test_nothing_private_reaches_results_or_the_job_log(smoke):
    results = smoke["results"]
    private_roots = [str(smoke[k]).encode() for k in ("pp", "po", "pr")]
    for path in results.rglob("*"):
        parts = path.relative_to(results).parts
        assert not set(PRIVATE) & set(parts), path
        if path.is_file():
            text = path.read_bytes()
            assert not any(root in text for root in private_roots), path
    # The orchestrator printed only "<alias> <stage> <status> <seconds>s" for a private project, and no
    # private path at all (§1.1); the copy printed counts only.
    stdout = smoke["pod"].stdout
    for line in stdout.splitlines():
        if line.startswith(PRIVATE):
            assert re.fullmatch(rf"({REAL}|{ALIAS}) \w+ \w+ [0-9.]+s", line), line
    assert not any(root.decode() in stdout + smoke["pod"].stderr for root in private_roots)
    assert re.search(r"^copy: \d+ public file\(s\), \d+ private file\(s\) \(full copy\)$", stdout, re.M)


def test_copy_layout_and_count_only_output(smoke):
    copy = smoke["copy"]
    assert copy.returncode == 0, copy.stderr
    assert re.fullmatch(r"copy: \d+ public file\(s\), \d+ private file\(s\) \(full copy\)\n", copy.stdout)
    results = smoke["results"]
    for rel in ("furniture/synthetic-04/building_final.json", "renders/synthetic-04/render_manifest.json",
                "renders/synthetic-04/scene_manifest.json", "check/synthetic-04/check_manifest.json",
                "final/synthetic-04/final_report.md", "run/synthetic-04/pipeline.json",
                "final/synthetic-02/final_report.md", "realism/synthetic-01/cameras_check.json",
                "realism/synthetic-01/pairs.json", "realism/synthetic-01/realism_ab.json",
                "realism/realism_summary.json"):
        assert (results / rel).is_file(), rel


def test_ab_on_synthetic_01(smoke):
    m = _manifest(smoke)
    ab = {a["name"]: a for a in m["ab"]}["synthetic-01"]
    stages = {s["stage"]: s["status"] for s in ab["stages"]}
    for stage in ("ab_prepare", "ab_m5", "ab_render", "ab_controls", "ab_pairs", "ab_realism", "ab_combine"):
        assert stages.get(stage) == "ok", (stage, stages)
    assert m["realism_summary"]["status"] == "ok"
    out = smoke["outputs"] / "synthetic-01" / "ab"
    check = json.loads((out / "cameras_check.json").read_text(encoding="utf-8"))
    assert len(check["kept"]) == 2
    assert all(d["reason"] == "not rendered in the A/B render" for d in check["dropped"])   # smoke: 2 cameras
    pairs = json.loads((out / "pairs.json").read_text(encoding="utf-8"))
    sets = {p["set"] for p in pairs["pairs"]}
    assert {"m5_vs_m6", "look_alt", "ctl_flat", "ctl_proxy", "ctl_direct", "ctl_lowspp", "null_identical",
            "null_reencode", "nuisance_ev"} <= sets
    summary = json.loads((smoke["results"] / "realism" / "realism_summary.json").read_text(encoding="utf-8"))
    assert summary["controls_project"] == "synthetic-01" and "m5_vs_m6" in summary["sets"]
