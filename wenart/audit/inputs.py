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
    stale: list = field(default_factory=list)     # 30 Oct 2026: records an earlier run left ({"record", "why"})

    @property
    def final(self) -> Optional[dict]:
        """The last stage's building (the one built)."""
        return self.stages[-1][1] if self.stages else None

    def stage(self, name: str) -> Optional[dict]:
        return next((b for n, b in self.stages if n == name), None)


def inspector_of_run(rec: Optional[dict], run_manifest: Optional[dict]) -> tuple[Optional[dict], Optional[str]]:
    """``(record, None)`` when the inspector's record belongs to this run, ``(None, why)`` when an earlier run left it
    (pure; 30 Oct 2026): written (``written_utc``) before the run started (the run manifest's ``started_utc``), or
    with no time stamp at all (a record from before 30 Oct 2026) in a run that has one. Why: real04 runs
    20261028-183611 to 20261029-201533 never rewrote ``orchestrator/inspector.json`` (the report raised on a camera
    edit), and Argus read the 28 Oct record's criticals (the cushions dec_L0_011 / 012 4.9 cm in a bed that run had
    dressed, the mirror dec_L1_013 through the roof) as each run's own. Without a run start the record is read."""
    if not isinstance(rec, dict):
        return rec, None
    started = (run_manifest or {}).get("started_utc") if isinstance(run_manifest, dict) else None
    if not started:
        return rec, None
    written = rec.get("written_utc")
    if not written:
        return None, f"stale: no time stamp, written before the run started {started}"
    if str(written) < str(started):
        return None, f"stale: written {written}, before the run started {started}"
    return rec, None


# 27 Nov 2026 (check pod 2smyy0ktv63y40, a structure run with no agent stage: the agent stage's building of a full run
# of 2 Nov stayed in the project's output folder on the volume, and C1 called 799 rooms, walls and openings of the run
# lost between "layout" and "agent"): a stage's building counts only when the run manifest says its stage ran in this
# run. stage (conservation.STAGE_FILES) -> the run's stage names that write its file (wenart/run/stages.py)
STAGE_RUN_NAMES = {"reading": ("pipeline_final", "pipeline"), "fit": ("fit",), "layout": ("layout",),
                   "decor": ("decor",), "agent": ("agent_apply", "agent"), "final": ("refit",), "build": ("build",)}
RAN = ("ok", "warning", "reused", "incomplete")


def stages_of_run(stages: list, run_manifest: Optional[dict], project: str) -> tuple[list, list]:
    """``(stages this run wrote, [{"record", "why"}] of the ones an earlier run left)`` (pure). Without a run manifest,
    or one that does not list the project's stages, every stage is kept (the old behaviour). A stage counts when one
    of its run stages ended ``ok``, ``warning``, ``reused`` or ``incomplete``; a stage the manifest lists as skipped,
    pending or failed, or does not list at all, wrote nothing in this run, so its file is an earlier run's."""
    if not isinstance(run_manifest, dict):
        return list(stages), []
    rec = next((p for p in run_manifest.get("projects") or []
                if isinstance(p, dict) and p.get("name") == project), None)
    if not isinstance(rec, dict) or not isinstance(rec.get("stages"), list):
        return list(stages), []
    status = {s.get("stage"): s.get("status") for s in rec["stages"] if isinstance(s, dict)}
    kept, stale = [], []
    for name, building in stages:
        names = STAGE_RUN_NAMES.get(name)
        if names is None or any(status.get(n) in RAN for n in names):
            kept.append((name, building))
            continue
        said = ", ".join(f"{n} {status[n]}" for n in names if n in status) or "not run"
        stale.append({"record": f"stage {name}", "why": f"stale: its stage did not run in this run ({said}); the "
                                                         f"file an earlier run left is not compared"})
    return kept, stale


# 27 Nov 2026: the records only the agent phase writes (its judge's rubric, the big loop, its decision log with the
# room critic's findings, the AI architect's look) and the final vision check belong to a run only when that phase ran
AGENT_RUN_NAMES = ("agent_apply", "agent_previews", "agent")
AGENT_RECORDS = ("rubric", "big_loop", "agent_log", "architect_look")


def bare_run(run_manifest: Optional[dict]) -> bool:
    """Whether the run built the bare building of a structure check (the run manifest's ``profile``; pure)."""
    return isinstance(run_manifest, dict) and run_manifest.get("profile") == "structure"


def agent_ran(run_manifest: Optional[dict], project: str) -> Optional[bool]:
    """Whether the agent phase ran for the project in this run (pure): None when the manifest does not say."""
    if not isinstance(run_manifest, dict):
        return None
    rec = next((p for p in run_manifest.get("projects") or []
                if isinstance(p, dict) and p.get("name") == project), None)
    if not isinstance(rec, dict) or not isinstance(rec.get("stages"), list):
        return None
    return any(isinstance(s, dict) and s.get("stage") in AGENT_RUN_NAMES and s.get("status") in RAN
               for s in rec["stages"])


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
    inp.inspector, stale = inspector_of_run(inp.inspector, inp.run_manifest)
    if stale:
        inp.missing.append(f"inspector ({stale})")
        inp.stale.append({"record": "inspector", "why": stale})
    if agent_ran(inp.run_manifest, inp.project) is False:
        for name in AGENT_RECORDS + (("check",) if bare_run(inp.run_manifest) else ()):
            if getattr(inp, name) is not None:
                setattr(inp, name, None)
                why = "stale: the agent phase did not run in this run" if name != "check" else \
                    "stale: a structure run makes no final vision check"
                inp.missing.append(f"{name} ({why})")
                inp.stale.append({"record": name, "why": why})
    inp.stages, old_stages = stages_of_run(inp.stages, inp.run_manifest, inp.project)
    for rec in old_stages:
        inp.missing.append(f"{rec['record']} ({rec['why']})")
        inp.stale.append(rec)
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
