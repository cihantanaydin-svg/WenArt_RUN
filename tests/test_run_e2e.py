"""Smoke end to end of the one-command full run on the CPU (docs/milestone6.md §2.5).

What: ``python -m wenart.run pod --profile smoke`` with the fake VLM server
(``tests/fakes/fake_vlm.py``) on synthetic-04 + synthetic-02 + a private copy
of synthetic-02 (alias ``selftest-02``, ``--private-selftest``) + the realism
A/B on synthetic-01 (2 cameras, controls on synthetic-01), every output in
temp folders outside the repo (paths are then absolute, §1.1); then
``python -m wenart.run copy``. Checks the run manifests, the stage records,
the reports, the private allow-list and that nothing private reaches
``$RESULTS``.

Needs the other M6 areas (synthetic-04 of area S, the build's
``--camera-policy`` of areas L/C, the realism commands of area V, intake and
``gate validate`` of area IE): skipped until ``projects/synthetic-04`` and the
build flag exist (the integrator makes it run). Marked ``slow`` (Blender
renders on the CPU, several minutes); skipped without Blender.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from fakes.fake_vlm import FakeVLM
from wenart.blender import cli as blender_cli
from wenart.run import state as ST

ROOT = Path(__file__).resolve().parents[1]
BLENDER = blender_cli.find_blender()
HAS_POLICY = "--camera-policy" in (ROOT / "wenart" / "blender" / "cli.py").read_text(encoding="utf-8")
pytestmark = [
    pytest.mark.slow,
    pytest.mark.skipif(BLENDER is None, reason="no Blender binary"),
    pytest.mark.skipif(not (ROOT / "projects" / "synthetic-04").is_dir(), reason="projects/synthetic-04 missing (area S)"),
    pytest.mark.skipif(not HAS_POLICY, reason="build --camera-policy missing (areas L/C)"),
]
ALIAS = "selftest-02"
ALLOWED = ("ok", "reused", "warning", "skipped")
PRIVATE_ALLOWED = re.compile(r"^(final/(final_report\.md|final_manifest\.json|[^/]+_final_preview\.jpg|contact_[^/]+\.jpg)"
                             r"|run/[^/]+\.json)$")


@pytest.fixture(scope="module")
def smoke(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("smoke")
    paths = {k: tmp / k for k in ("results", "outputs", "pp", "po", "pr", "job")}
    assets = Path(os.environ["WENART_ASSETS"]) if os.environ.get("WENART_ASSETS") else (
        ROOT / "assets" if (ROOT / "assets").is_dir() else tmp / "assets")
    env = {k: v for k, v in os.environ.items() if k not in ("WENART_DEADLINE", "WENART_JOB_DIR", "WENART_OUTPUTS")}
    env.update(CHECK_MODELS="qwen glm", JOB_ID="smoke")
    common = ["--outputs", str(paths["outputs"]), "--private-root", str(paths["pp"]), "--private-outputs",
              str(paths["po"]), "--private-results", str(paths["pr"])]
    with FakeVLM() as url:
        pod = subprocess.run(
            [sys.executable, "-m", "wenart.run", "pod", "--projects", "synthetic-04 synthetic-02", "--private-selftest",
             "--ab", "synthetic-01", "--ab-controls", "synthetic-01", "--results", str(paths["results"]),
             "--profile", "smoke", "--vlm-url", url, "--job-dir", str(paths["job"]), "--assets", str(assets)] + common,
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=5400)
    copy = subprocess.run(
        [sys.executable, "-m", "wenart.run", "copy", "--projects", "synthetic-04 synthetic-02", "--private-selftest",
         "--ab", "synthetic-01", "--results", str(paths["results"])] + common,
        cwd=ROOT, env=env, capture_output=True, text=True, timeout=600)
    return {"pod": pod, "copy": copy, **paths}


def _manifest(smoke) -> dict:
    return json.loads((smoke["results"] / "run_manifest.json").read_text(encoding="utf-8"))


def _records(out: Path, run_id: str) -> dict:
    found = {}
    for path in sorted((out / "run").glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("run_id") == run_id:
            found[data["stage"]] = data
    return found


def test_the_run_ends_ok(smoke):
    pod = smoke["pod"]
    assert pod.returncode == 0, pod.stdout[-6000:] + pod.stderr[-3000:]
    m = _manifest(smoke)
    assert m["kind"] == "run_manifest" and m["profile"] == "smoke" and m["final"] and m["exit_code"] == 0
    states = {p["name"]: p for p in m["projects"]}
    assert states["synthetic-04"]["state"] == "ok"
    assert states["synthetic-02"]["state"] == "needs_review"
    assert states[ALIAS] == {"name": ALIAS, "private": True, "state": "needs_review"}
    assert m["tests"] == []                                  # no GPU tests in the smoke profile
    assert [ph["phase"] for ph in m["phases"]] == list(range(1, 12))


def test_stage_records_of_the_ok_project(smoke):
    m = _manifest(smoke)
    out = smoke["outputs"] / "synthetic-04"
    records = _records(out, m["run_id"])
    for stage in ("pipeline", "fit", "style", "assets", "layout", "decor", "refit", "build", "render", "controls",
                  "expected", "check", "combine", "report"):
        assert stage in records, stage
        assert records[stage]["status"] in ALLOWED, (stage, records[stage]["status"], records[stage]["note"])
    for stage in ("gate", "polish"):
        assert records[stage]["status"] == "skipped" and records[stage]["note"] == "smoke profile"
    assert records["photos"]["note"] == "no style photos" and records["intake"]["note"] == "private only"
    for rec in records.values():
        if rec["status"] == "skipped":
            assert rec["note"] in ST.SKIP_REASONS
    # Paths outside the repo are recorded absolute.
    assert all(Path(p).is_absolute() for p in records["pipeline"]["inputs"])
    scene = json.loads((out / "scene" / "scene_manifest.json").read_text(encoding="utf-8"))
    assert scene["cameras"] and {c.get("policy") for c in scene["cameras"]} == {"search"}
    final = json.loads((out / "final" / "final_manifest.json").read_text(encoding="utf-8"))
    render = json.loads((out / "renders" / "render_manifest.json").read_text(encoding="utf-8"))
    assert final["summary"]["views"] == len(render["renders"])
    assert (out / "final" / "final_report.md").is_file()


def test_needs_review_projects(smoke):
    m = _manifest(smoke)
    out = smoke["outputs"] / "synthetic-02"
    records = _records(out, m["run_id"])
    assert records["pipeline"]["status"] == "needs_review"
    assert "build" not in records and "layout" not in records
    assert (out / "final" / "final_report.md").is_file()
    final = json.loads((out / "final" / "final_manifest.json").read_text(encoding="utf-8"))
    assert final["status"] == "needs_review"
    private = _records(smoke["po"] / ALIAS, m["run_id"])
    assert private["intake"]["status"] == "ok" and private["pipeline"]["status"] == "needs_review"
    assert "build" not in private and (smoke["pp"] / ALIAS).is_dir()      # the self-test upload (synthetic-02)
    assert (smoke["po"] / ALIAS / "intake_manifest.json").is_file()


def test_private_files_stay_private(smoke):
    pr = smoke["pr"] / ALIAS
    files = [p.relative_to(pr).as_posix() for p in pr.rglob("*") if p.is_file()]
    assert "final/final_report.md" in files and any(f.startswith("run/") for f in files)
    bad = [f for f in files if not PRIVATE_ALLOWED.match(f)]
    assert not bad, bad
    for f in files:
        if f.startswith("run/"):
            assert "inputs" not in json.loads((pr / f).read_text(encoding="utf-8"))
    link = smoke["job"] / "results-private" / ALIAS
    assert link.is_symlink() and link.resolve() == pr.resolve()
    private_manifest = json.loads((smoke["job"] / "results-private" / "_run_manifest.json").read_text())
    assert [p["name"] for p in private_manifest["projects"]] == [ALIAS]
    # Nothing private in $RESULTS: no alias folder, no private path in any file.
    results = smoke["results"]
    for path in results.rglob("*"):
        assert ALIAS not in path.relative_to(results).parts, path
        if path.is_file():
            text = path.read_bytes()
            assert str(smoke["po"]).encode() not in text and str(smoke["pp"]).encode() not in text, path
    # The orchestrator printed only "<alias> <stage> <status> <seconds>s" for the private project.
    for line in smoke["pod"].stdout.splitlines():
        if line.startswith(ALIAS + " "):
            assert re.fullmatch(rf"{ALIAS} \w+ \w+ [0-9.]+s", line), line


def test_copy_layout_and_count_only_output(smoke):
    copy = smoke["copy"]
    assert copy.returncode == 0, copy.stderr
    assert re.fullmatch(r"copy: \d+ public file\(s\), \d+ private file\(s\) \(full copy\)\n", copy.stdout)
    results = smoke["results"]
    for rel in ("furniture/synthetic-04/building_final.json", "renders/synthetic-04/render_manifest.json",
                "renders/synthetic-04/scene_manifest.json", "check/synthetic-04/check_manifest.json",
                "final/synthetic-04/final_report.md", "run/synthetic-04/pipeline.json",
                "final/synthetic-02/final_report.md", "realism/synthetic-01/cameras_check.json",
                "realism/synthetic-01/pairs.json"):
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
    assert (smoke["results"] / "realism" / "realism_summary.json").is_file()
