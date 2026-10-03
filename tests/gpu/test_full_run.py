"""GPU tests of the one-command full run (docs/milestone6.md §2.4, §9; docs/milestone7.md §11 GPU).

Run on the pod by ``python -m wenart.run pod`` (phase 11, after the last vLLM
server stopped) with ``pytest -m gpu tests/gpu/test_full_run.py ...``. They
read the run manifest the orchestrator wrote into ``$WENART_RESULTS`` just
before the tests (``final: false``; every stage of this run is in it), the
outputs under ``$WENART_OUTPUTS`` and, for the private self-test, the private
results root ``$WENART_PRIVATE_RESULTS``. Project lists (exported by the
orchestrator, empty when no project qualifies, so a test never falls back to
old outputs on the volume):

- ``RUN_TEST_PROJECTS``: every project ``ok``, every stage ``ok``,
  ``reused``, ``warning`` or ``skipped`` with an allowed reason (warnings are
  printed); the pipeline may be ``pending`` (recognition questions, M7 §1.4)
  only with a ``recognize`` stage and a ``pipeline_final`` that ended ``ok``
  or ``reused`` in this run, whose building has no pending question; the
  final report's view count equals the render manifest; a project whose
  gate decision is ``polish_disabled`` or ``not_validated`` has Cycles
  finals only;
- ``NEEDS_REVIEW_TEST_PROJECTS``: ``needs_review`` with at least one reason,
  no scene built in this run;
- ``SELFTEST_TEST_ALIAS`` (only with ``PRIVATE_SELFTEST=1``): its files only
  under ``results-private/<alias>/`` (the allow-list), none under
  ``$WENART_RESULTS``.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import pytest

from wenart.canonical import canonical_sha256
from wenart.run.state import SKIP_REASONS

pytestmark = pytest.mark.gpu
RESULTS = Path(os.environ.get("WENART_RESULTS", "/workspace/jobs/run/results"))
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PRIVATE_RESULTS = Path(os.environ.get("WENART_PRIVATE_RESULTS", "/workspace/results-private"))
RUN = [p for p in os.environ.get("RUN_TEST_PROJECTS", "").split() if p]
NEEDS_REVIEW = [p for p in os.environ.get("NEEDS_REVIEW_TEST_PROJECTS", "").split() if p]
SELFTEST = os.environ.get("SELFTEST_TEST_ALIAS", "").strip()
ALLOWED = ("ok", "reused", "warning", "skipped")
# final/ATTRIBUTION.md: the credits of the public library models a private project's images show (M7 §7.3).
PRIVATE_ALLOWED = re.compile(r"^(final/(final_report\.md|final_manifest\.json|[^/]+_final_preview\.jpg|contact_[^/]+\.jpg"
                             r"|ATTRIBUTION\.md)|run/[^/]+\.json)$")


@pytest.fixture(scope="module")
def manifest() -> dict:
    path = RESULTS / "run_manifest.json"
    assert path.is_file(), f"{path} missing: the orchestrator writes it before the GPU tests"
    return json.loads(path.read_text(encoding="utf-8"))


def _entry(manifest: dict, name: str) -> dict:
    entry = next((p for p in manifest["projects"] if p["name"] == name), None)
    assert entry is not None, f"{name} is not in the run manifest"
    return entry


def _load(project: str, rel: str) -> dict:
    path = OUTPUTS / project / rel
    assert path.is_file(), f"{path} missing"
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.skipif(not (RUN or NEEDS_REVIEW), reason="no public project in this run")
def test_every_public_project_ended_ok_or_needs_review(manifest):
    """A project that failed or was cut is in no test list: the manifest says it (M7 §11: real01 must be ok)."""
    public = {p["name"]: p["state"] for p in manifest["projects"] if not p["private"]}
    bad = {name: state for name, state in public.items() if state not in ("ok", "needs_review")}
    assert not bad, f"projects neither ok nor needs_review: {bad}"
    assert set(RUN) == {n for n, st in public.items() if st == "ok"}
    if "real01" in public:
        assert public["real01"] == "ok", "real01 (the user's first real project) must end ok"


@pytest.mark.parametrize("project", RUN)
def test_run_project_is_ok_with_allowed_stage_states(manifest, project):
    entry = _entry(manifest, project)
    assert entry["state"] == "ok", entry
    bad, warnings = [], []
    for stage in entry["stages"]:
        if stage["stage"] == "pipeline" and stage["status"] == "pending":
            continue                                   # checked by test_pending_pipeline_has_its_final_building
        if stage["status"] not in ALLOWED:
            bad.append(stage)
        elif stage["status"] == "skipped" and stage["note"] not in SKIP_REASONS:
            bad.append(stage)
        elif stage["status"] == "warning":
            warnings.append(f"{stage['stage']}: {stage['note']}")
    for w in warnings:
        print(f"{project} warning {w}")
    assert not bad, f"{project}: stages not ok: {bad}"
    names = [s["stage"] for s in entry["stages"]]
    for stage in ("pipeline", "build", "render", "check", "report"):
        assert stage in names, f"{project}: no {stage} stage in this run"


@pytest.mark.parametrize("project", RUN)
def test_pending_pipeline_has_its_final_building(manifest, project):
    """M7 §9.1: a pipeline that wrote recognition questions (pending) is ok only with this run's recognize stage
    and a pipeline_final that ended ok or reused; that building is the one the later stages used."""
    stages = {s["stage"]: s for s in _entry(manifest, project)["stages"]}
    if stages.get("pipeline", {}).get("status") != "pending":
        assert stages.get("pipeline_final", {}).get("note") == "no questions", stages.get("pipeline_final")
        return
    assert "recognize" in stages and stages["recognize"]["status"] in ("ok", "reused", "warning"), stages
    assert stages.get("pipeline_final", {}).get("status") in ("ok", "reused"), stages.get("pipeline_final")
    record = _load(project, "run/pipeline_final.json")
    building = OUTPUTS / project / "building.json"
    assert record["written"]["building.json"] == canonical_sha256(building)
    assert json.loads(building.read_text(encoding="utf-8"))["status"] == "ok"
    if stages["recognize"]["status"] == "warning":
        print(f"{project} warning recognize: {stages['recognize']['note']}")


@pytest.mark.parametrize("project", RUN)
def test_final_report_has_every_rendered_view(project):
    final = _load(project, "final/final_manifest.json")
    render = _load(project, "renders/render_manifest.json")
    assert final["summary"]["views"] == len(render["renders"]), (final["summary"], len(render["renders"]))


@pytest.mark.parametrize("project", RUN)
def test_unvalidated_gate_means_cycles_finals(project):
    path = OUTPUTS / project / "gate" / "gate_validation.json"
    if not path.is_file():
        pytest.skip(f"{project}: no gate validation (polish off)")
    decision = json.loads(path.read_text(encoding="utf-8")).get("decision")
    if decision not in ("polish_disabled", "not_validated"):
        pytest.skip(f"{project}: gate decision {decision}")
    final = _load(project, "final/final_manifest.json")
    assert final["summary"]["polished"] == 0, final["summary"]


def _review_reasons(project: str) -> list:
    final = _load(project, "final/final_manifest.json")
    reasons = [r for r in final.get("reasons") or final.get("review_reasons") or [] if r]
    if reasons:
        return reasons
    report = OUTPUTS / project / "report.md"
    if report.is_file():
        match = re.search(r"^Status: \*\*needs_review\*\* \((.+)\)$", report.read_text(encoding="utf-8"), re.M)
        if match:
            return [r.strip() for r in match.group(1).split(";") if r.strip()]
    return []


@pytest.mark.parametrize("project", NEEDS_REVIEW)
def test_needs_review_project(manifest, project):
    entry = _entry(manifest, project)
    assert entry["state"] == "needs_review", entry
    names = [s["stage"] for s in entry["stages"]]
    assert "build" not in names and "render" not in names, f"{project}: a scene was built in this run: {names}"
    final = _load(project, "final/final_manifest.json")
    assert final.get("status") == "needs_review", final.get("status")
    assert _review_reasons(project), f"{project}: needs_review without a reason"


@pytest.mark.skipif(not SELFTEST, reason="no private self-test in this run")
def test_selftest_files_stay_private(manifest):
    entry = _entry(manifest, SELFTEST)
    assert set(entry) == {"name", "private", "state"} and entry["private"] is True
    assert entry["state"] == "needs_review"
    folder = PRIVATE_RESULTS / SELFTEST
    files = [p.relative_to(folder).as_posix() for p in folder.rglob("*") if p.is_file()]
    assert "final/final_report.md" in files, files
    bad = [f for f in files if not PRIVATE_ALLOWED.match(f)]
    assert not bad, f"files outside the private allow-list: {bad}"
    for f in files:
        if f.startswith("run/"):
            assert "inputs" not in json.loads((folder / f).read_text(encoding="utf-8")), f
    leaked = [p for p in RESULTS.rglob("*") if SELFTEST in p.relative_to(RESULTS).parts]
    assert not leaked, f"private files under $WENART_RESULTS: {leaked}"
