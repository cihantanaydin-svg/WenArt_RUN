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
  or ``reused`` in this run (or ``warning`` for second-round questions it
  left unanswered with ``--no-ai``, wenart/run/stages.py
  ``SECOND_ROUND_NOTE``), whose building has no pending question; the
  ``sheets`` stage may be ``pending`` too (Milestone 10: it wrote
  sheet_region questions; fix round after P3, 16-17 Oct 2026) only with a
  ``pipeline_final`` that ended ``ok``, ``reused`` or ``warning`` (``sheet
  answers missing``, printed) and recorded the ``sheets.json`` the outputs
  hold, i.e. it applied the sheet answers; the
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
from wenart.run.stages import SECOND_ROUND_NOTE
from wenart.run.state import SKIP_REASONS

pytestmark = pytest.mark.gpu
RESULTS = Path(os.environ.get("WENART_RESULTS", "/workspace/jobs/run/results"))
OUTPUTS = Path(os.environ.get("WENART_OUTPUTS", "/workspace/repo/outputs"))
PRIVATE_RESULTS = Path(os.environ.get("WENART_PRIVATE_RESULTS", "/workspace/results-private"))
RUN = [p for p in os.environ.get("RUN_TEST_PROJECTS", "").split() if p]
NEEDS_REVIEW = [p for p in os.environ.get("NEEDS_REVIEW_TEST_PROJECTS", "").split() if p]
SELFTEST = os.environ.get("SELFTEST_TEST_ALIAS", "").strip()
ALLOWED = ("ok", "reused", "warning", "skipped")
# wenart/run/scheduler.py stage_pipeline_final: the note of a pipeline_final that ran without the sheet answers
SHEETS_MISSING = "sheet answers missing"
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
        if stage["stage"] in ("pipeline", "sheets") and stage["status"] == "pending":
            continue                                   # checked by test_pending_pipeline_has_its_final_building
                                                       # (M10: sheet_region questions; P3 real04: 8 of them)
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
    and a pipeline_final that ended ok or reused; that building is the one the later stages used. A pipeline_final
    whose answers opened second-round questions ran once more with --no-ai and is a warning with exactly
    SECOND_ROUND_NOTE (the new pieces stay unknown/unverified, listed in its report): allowed, printed.

    Fix round after P3: a ``sheets`` stage left ``pending`` (its sheet_region questions, Milestone 10) is answered by
    pipeline_final: it must end ok, reused or warning (a warning with "sheet answers missing" is allowed and
    printed, as scheduler.stage_pipeline_final writes it) and its record's ``sheets.json`` must be the file the
    outputs hold (P3 real04: 8 questions, both models' answers, sheets.json 484c08e6...)."""
    stages = {s["stage"]: s for s in _entry(manifest, project)["stages"]}
    sheets_missing = False
    if stages.get("sheets", {}).get("status") == "pending":
        final = stages.get("pipeline_final", {})
        assert final.get("status") in ("ok", "reused", "warning"), final
        record = _load(project, "run/pipeline_final.json")
        assert record["written"].get("sheets.json") == canonical_sha256(OUTPUTS / project / "sheets.json"), \
            record["written"]
        sheets_missing = final.get("status") == "warning" and SHEETS_MISSING in str(final.get("note") or "")
        if final.get("status") == "warning":
            print(f"{project} warning pipeline_final: {final.get('note')}")
    if stages.get("pipeline", {}).get("status") != "pending":
        assert stages.get("pipeline_final", {}).get("note") == "no questions", stages.get("pipeline_final")
        return
    assert "recognize" in stages and stages["recognize"]["status"] in ("ok", "reused", "warning"), stages
    final = stages.get("pipeline_final", {})
    second_round = final.get("status") == "warning" and final.get("note") == SECOND_ROUND_NOTE
    assert final.get("status") in ("ok", "reused") or second_round or sheets_missing, final
    record = _load(project, "run/pipeline_final.json")
    building = OUTPUTS / project / "building.json"
    assert record["written"]["building.json"] == canonical_sha256(building)
    assert json.loads(building.read_text(encoding="utf-8"))["status"] == "ok"
    if stages["recognize"]["status"] == "warning":
        print(f"{project} warning recognize: {stages['recognize']['note']}")
    if second_round:
        print(f"{project} warning pipeline_final: {final['note']}")


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


@pytest.mark.parametrize("project", RUN)
def test_the_model_as_built_has_no_critical_finding(project):
    """26 Oct 2026 (user: "I need ai models to see understand and fix everything before even I look at it";
    "reviewing the 3d model itself could be better"): the review of the final scene's model as built
    (``scene/model_review.json``, ``wenart.blender.model_review``) leaves no critical finding: no door off its floor,
    no basin at knee height, no opening to fall out of, no door into the air, no room that is not what it is called.
    A failure names every element and its number."""
    rec = _load(project, "scene/model_review.json")
    crit = [f"{f['check']} {f['target']}: {f['message']}" for f in rec.get("findings") or []
            if f.get("severity") == "critical"]
    for f in rec.get("findings") or []:
        if f.get("severity") == "major":
            print(f"{project} model review major {f['check']} {f['target']}: {f['message']}")
    assert not crit, crit


@pytest.mark.parametrize("project", RUN)
def test_every_planned_library_door_is_built(project):
    """29 Oct 2026 (user: "Better door models needed"; lesson UL89; real06 run 20261028-154514-full: the build refused
    every HSSD door the plan chose, "CC BY 4.0 without source_url, via (no credit line)"): no door of the final scene
    is the parametric door in place of the library model the plan chose (model review M20, kind
    ``library_door_not_built``), and at most a third of the doors are parametric (Argus U18)."""
    from wenart.blender import opening_models as OM

    scene = _load(project, "scene/scene_manifest.json")
    rows = OM.built_doors(scene)
    lost = [p["message"] for p in OM.door_product_problems(scene) if p["kind"] == "library_door_not_built"]
    para = [r["id"] for r in rows if not r["library"]]
    print(f"{project}: {len(rows) - len(para)} of {len(rows)} doors library models; parametric {para}")
    assert not lost, lost
    assert not [p for p in OM.door_model_problems(scene) if p["kind"] == "parametric_doors"], para
