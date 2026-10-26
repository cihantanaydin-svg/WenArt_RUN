"""Argus's inputs: every record a run leaves, read once, for both layouts (26 Oct 2026).

What: ``Inputs`` holds the stages' buildings (``conservation.STAGE_FILES``), the scene manifest, the architect's and
the model review's records, the inspector's, the big loop's and the judge's, the recognition questions and answers,
the per-stage run records, the run manifest and the test reports, and the paths of the source plans and the model's
top-down images. ``pod(project_out, results)`` reads a project's output folder on the pod (``outputs/<p>``, the scene
under ``scene/``, the orchestrator under ``orchestrator/``); ``collected(results, project)`` reads a collected run
(``runs/<job>/results``: ``furniture/<p>``, ``renders/<p>``, ``agent/<p>``, ``recognition/<p>``, ``run/<p>``).

Why: the lines read the same facts in both places: on the pod while the run can still act on them, here when a run is
reviewed. A file that is missing is ``None`` (the line that needs it says so in the report: nothing is skipped
silently).
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from wenart.audit import conservation as CV


def read_json(path) -> Optional[dict]:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


@dataclass
class Inputs:
    project: str
    layout: str                                   # pod | collected
    root: Path                                    # the project's output folder, or the collected results
    stages: list = field(default_factory=list)    # [(stage, building)] in order
    manifest: Optional[dict] = None               # the scene manifest
    architect: Optional[dict] = None
    model_review: Optional[dict] = None
    inspector: Optional[dict] = None
    agent_log: Optional[dict] = None              # the orchestrator's decision log (orchestrator/log.json)
    big_loop: Optional[dict] = None
    architect_look: Optional[dict] = None
    rubric: Optional[list] = None
    check: Optional[dict] = None                  # the final vision check (check/check_manifest.json)
    requests: Optional[dict] = None               # the recognition questions
    answers: dict = field(default_factory=dict)   # model slug -> the recognition answers
    records: dict = field(default_factory=dict)   # stage -> its run record
    run_manifest: Optional[dict] = None
    junit: list = field(default_factory=list)     # test report paths
    top_plans: list = field(default_factory=list)  # the model's top-down images (top_<level>_plan.jpg)
    images: list = field(default_factory=list)    # the final renders' previews
    missing: list = field(default_factory=list)   # the records that were looked for and not found

    @property
    def final(self) -> Optional[dict]:
        """The last stage's building (the one built)."""
        return self.stages[-1][1] if self.stages else None

    def stage(self, name: str) -> Optional[dict]:
        return next((b for n, b in self.stages if n == name), None)


def _first(*paths) -> Optional[Path]:
    return next((Path(p) for p in paths if p and Path(p).is_file()), None)


def _fill(inp: Inputs, scene: Path, orch: Path, recog: Path, run: Path, final: Path, results: Optional[Path],
          check: Optional[Path] = None) -> Inputs:
    def get(name, *paths):
        p = _first(*paths)
        if p is None:
            inp.missing.append(name)
            return None
        return read_json(p)

    inp.manifest = get("scene_manifest", scene / "scene_manifest.json")
    inp.architect = get("architect", scene / "architect.json")
    inp.model_review = get("model_review", scene / "model_review.json")
    inp.inspector = get("inspector", orch / "inspector.json")
    inp.big_loop = read_json(orch / "big_loop.json") if (orch / "big_loop.json").is_file() else None
    inp.agent_log = read_json(orch / "log.json") if (orch / "log.json").is_file() else None
    inp.architect_look = read_json(orch / "architect_look.json") if (orch / "architect_look.json").is_file() else None
    rubric = read_json(final / "rubric_per_view.json") if (final / "rubric_per_view.json").is_file() else None
    inp.rubric = rubric if isinstance(rubric, list) else \
        (rubric or {}).get("views") if isinstance(rubric, dict) else None
    inp.requests = read_json(recog / "requests.json") if (recog / "requests.json").is_file() else None
    if check is not None and (check / "check_manifest.json").is_file():
        inp.check = read_json(check / "check_manifest.json")
    for p in sorted(recog.glob("answers_*.json")) if recog.is_dir() else ():
        inp.answers[p.stem[len("answers_"):]] = read_json(p)
    for p in sorted(run.glob("*.json")) if run.is_dir() else ():
        inp.records[p.stem] = read_json(p)
    if results is not None:
        rm = results / "run_manifest.json"
        inp.run_manifest = read_json(rm) if rm.is_file() else None
        inp.junit = sorted(results.glob("junit-*.xml"))
    tops = {p.name: p for d in (scene, scene.parent / "renders") if d.is_dir()
            for p in sorted(d.glob("top_*_plan*.jpg"))}
    inp.top_plans = [tops[k] for k in sorted(tops)]          # the pod keeps them in renders/, a collected run in scene
    inp.images = sorted(final.glob("*_final_preview.jpg")) if final.is_dir() else []
    return inp


def pod(project_out, results=None) -> Inputs:
    """A project's output folder on the pod (``outputs/<p>``); ``results`` the job's results folder (run manifest,
    test reports) when known."""
    out = Path(project_out)
    inp = Inputs(project=out.name, layout="pod", root=out, stages=CV.load(out))
    return _fill(inp, out / "scene", out / "orchestrator", out / "recognition", out / "run", out / "final",
                 Path(results) if results else None, out / "check")


def collected(results, project: str) -> Inputs:
    """A collected run (``runs/<job>/results``)."""
    res = Path(results)
    stages, _manifest = CV.from_results(res, project)
    inp = Inputs(project=project, layout="collected", root=res, stages=stages)
    return _fill(inp, res / "renders" / project, res / "agent" / project, res / "recognition" / project,
                 res / "run" / project, res / "final" / project, res, res / "check" / project)
