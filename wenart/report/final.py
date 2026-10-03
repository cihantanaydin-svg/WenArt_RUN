"""Final report of Milestone 5 (docs/milestone5.md §7): which image is final for every view, and why.

What: ``python -m wenart.report final --project-out outputs/<p>`` reads the
manifests of every stage and writes ``outputs/<p>/final/``:

- ``final_manifest.json``: per view the camera, room, level, the final image
  (path relative to ``final/``), ``polished|cycles`` and the reason
  (``gate|brief|room|vision_check|check_incomplete|error``, plus
  ``deadline`` from the polish and ``not_run`` when the polish did not run
  for the view), the chosen polish attempt's settings and gate summary, the
  vision-check verdicts of both images, the JSON cross-check, the realism
  preference, the exposure, the element ids per source and the unverified
  pieces in view, and every mismatch with its source and evidence;
- ``<cam>_final_preview.jpg`` (<= 300 KB) of the final image;
- ``<cam>_plan.jpg``: copies of the source-plan crops of ``check/``;
- ``contact_<level>.jpg`` (<= 300 KB): 480 px tiles labelled with the camera,
  ``P`` (polished) or ``C`` (Cycles) and ``U<n>`` (unverified pieces in view);
- ``final_report.md``: summary, per-view table, every mismatch (never
  auto-fixed), the unverified items and conflicts of the building JSON, rooms
  mixing polished and Cycles views, models and licences. It links only to
  files in ``final/``.

Inputs (each may be missing; the report then says "not run"):
``renders/render_manifest.json``, ``scene/scene_manifest.json``, the building
and the brief (``wenart.views.project_paths``), ``polish/polish_manifest.json``,
``check/check_manifest.json``, ``check/check_calibration.json``,
``check/expected_views.json``, ``check/answers_*.json`` (seconds),
``gate/gate_calibration.json``.

Final decision (§5.5, §7), ``decide``: the final image is the polished one
iff the brief allows the polish, the project's gate validation allows it
(Milestone 6 §7.3: ``polish_disabled`` and ``not_validated`` mean Cycles for
every view, reason ``gate_validation``), the polish says ``final: polished``
with an existing PNG made from the current render, and the vision check
checked that very image without rejecting it. The check rejects
(``vision_check``) when its manifest says so or when an element
ok/unverified on the Cycles render is confirmed missing/changed on the
polished one (recomputed here as a second look); it is ``check_incomplete``
when the check did not run, did not see this polished image or the Cycles
image (the check manifest's ``image_sha256`` must hold the current file's
sha256: a re-polish writes new pixels under the same file name), or a pass
was not computed or unreliable. Everything else stays Cycles with the
polish's own reason. Nothing is auto-fixed: mismatches are listed with their
evidence.

Milestone 6 (docs/milestone6.md §7.4):

- ``status`` in ``final_manifest.json``: ``ok`` (a report of rendered views),
  ``not_rendered`` (no render manifest; ``status_note: "no renders in this
  run"``, the report names this run's ``incomplete``/``failed`` stages; exit 1)
  or ``needs_review``;
- a ``needs_review`` project (``intake_manifest.json``, ``building.json`` or a
  stage record ``run/<stage>.json`` of this run says so; stale renders are
  ignored) gets the needs-review report: status, every reason, the page table of
  ``building.json`` (or the documents table of ``report.md``), the debug
  images of the pipeline as JPEG <= 300 KB under ``final/debug/``, and the
  stage table; exit 0;
- the gate validation (``gate/gate_validation.json``) with its decision, rates,
  limits and effect (a validation older than the calibration it names counts as
  ``not_validated``); with ``polish_disabled`` or ``not_validated`` a
  ``polish/polish_manifest.json`` on the volume is from an earlier run and is
  not used (``stages.polish: not_run``);
- the views are the render manifest's: a camera that only the polish manifest
  has (an earlier run's camera) is a warning, never a view;
- per view the camera policy and score, the window pull and the EV; views per
  room as rendered (1-3, rooms without a view listed); a stage table from
  ``run/*.json`` (status, seconds, note; the report's own record is written
  after the report). This run is the ``run_id`` of the newest record; records
  of other runs (stages this run did not reach) are listed apart as
  ``earlier run <run_id>`` (``earlier_run_stages``) and never decide the status;
- a private project (``--private``, an ``intake_manifest.json`` in the project
  output, a folder under ``/workspace/outputs-private`` or an alias name) never
  gets plan crops or debug images copied into ``final/``: they are named (paths
  relative to the project output) and stay on the volume; the intake is
  summarised by counts and by its fixed note texts only (``notes_by_kind``: a
  misnamed or nested brief, a DWG; never a file name), and a brief that was not
  read is an advisory flag;
- the brief's own warnings (``wenart.brief.load_brief``: no ``brief.yaml``, a
  value of the wrong type) are report warnings (a private project's brief values
  are left out of them);
- ``final_manifest.json`` is written last, so a manifest newer than the report
  call means the report finished (exit 1 is then ``not_rendered``, not a crash);
- every repo-relative path (the scene manifest's ``building``) is resolved with
  ``wenart.views._resolve_repo_path``.
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from wenart.report import common as C

FINAL_DIR = "final"
MANIFEST_NAME = "final_manifest.json"
REPORT_NAME = "final_report.md"
TILE_WIDTH = 480
CONTACT_COLUMNS = 4
LABEL_HEIGHT = 24

REASONS = ("gate", "brief", "room", "vision_check", "check_incomplete", "error", "deadline", "not_run",
           "gate_validation")
# Gate validation decisions (wenart/gate/validate.py) that switch the polish off for the project.
NO_POLISH_DECISIONS = ("polish_disabled", "not_validated")
GATE_EFFECT = {
    "ok": "polish allowed",
    "flagged": "polish ran; flagged: the gate also rejects some harmless edits, so more views may stay Cycles",
    "polish_disabled": "no polish for this project: every final image is the Cycles render",
    "not_validated": "no polish for this project: every final image is the Cycles render",
}
DEBUG_DIR = "debug"
# status_note of a report without a render manifest (the orchestrator records the report stage of a project
# that a deadline or a failure stopped before its first render as a warning with the same words).
NO_RENDERS = "no renders in this run"
# Stage statuses that stop a project before its renders (wenart.run.state.TERMINAL without needs_review).
STOPPED_STATUSES = ("incomplete", "failed")
# An intake note whose text is not one of the fixed texts of wenart/intake.py is only counted (it could name a file).
OTHER_INTAKE_NOTE = "other note (its text is in intake_manifest.json on the volume)"
# Brief warnings of a private project: the user's value after "got <type>" is left out (wenart/brief.py texts).
_BRIEF_LIST_VALUE = re.compile(r"(: expected a list of file names), got .*(; default )", re.S)
_BRIEF_GOT_VALUE = re.compile(r"(: expected [^,;]+, got \w+) .*(; default )", re.S)
NEEDS_REVIEW_HINTS = (
    ("not uploaded", "upload the project folder (docs/intake.md, step 5) and run again"),
    ("collision", "rename one of the files that map to the same name (see intake_manifest.json)"),
    ("cap", "split or shrink the file(s) over the size limit"),
    ("dwg", "export DXF (or a vector PDF) from the CAD program; DWG is not read"),
    ("no vector floor plan", "add a DXF or vector PDF floor plan; scans and photos need the recognition path"),
    ("no scale", "add a scale (ÖLÇEK 1/50, 1/100 or DXF $INSUNITS) to the plan"),
    ("level title", "add the level title (e.g. ZEMİN KAT PLANI) to the floor plan"),
    ("closed loop", "close the outer walls of the level in the drawing"),
    ("do not close", "close the walls around every labelled room in the drawing"),
    ("no document", "upload at least one plan (.dxf, .pdf or an image)"),
)
MISMATCH_RESULTS = ("missing", "changed", "missing_or_changed")
NON_DECOR_CLASSES = ("door", "window", "furniture", "fixture")
CROSSCHECK_KEYS = ("in_json_not_rendered", "rendered_not_in_json", "misplaced")
# Keys of a check-manifest camera entry that are not image kinds (§5.7).
CHECK_VIEW_KEYS = {"room_id", "json_crosscheck", "polished_rejected", "polished_reason", "polished_reasons",
                   "needs_review", "needs_review_reasons", "preference"}
ADDED_BY_AI_NOTE = "added_by_ai: render/polish issue, not a document conflict"

NUM = {"type": ["number", "null"]}
STR = {"type": ["string", "null"]}
FINAL_VIEW = {
    "type": "object",
    "required": ["camera", "room_id", "level_id", "final", "reason", "image", "preview", "plan", "attempt",
                 "gate", "vision_check", "json_crosscheck", "preference", "exposure", "ids_by_source",
                 "unverified", "mismatches", "needs_review"],
    "properties": {
        "camera": {"type": "string"},
        "final": {"enum": ["polished", "cycles"]},
        "reason": {"enum": [None, *REASONS]},
        "image": STR, "preview": STR, "plan": STR,
        "attempt": {"type": ["object", "null"]},
        "gate": {"type": ["object", "null"]},
        "vision_check": {"type": ["object", "null"]},
        "ids_by_source": {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string"}}},
        "unverified": {"type": "array", "items": {"type": "string"}},
        "mismatches": {"type": "array", "items": {"type": "object", "required": ["image", "what", "result"]}},
        "needs_review": {"type": "boolean"},
    },
}
FINAL_MANIFEST = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["schema_version", "kind", "project", "status", "private", "inputs", "stages", "polish_allowed",
                 "advisory", "advisory_flags", "summary", "views", "rooms", "rooms_mixed", "models",
                 "contact_sheets", "building", "gate_validation", "run_stages", "warnings"],
    "properties": {
        "schema_version": {"const": "0.1"},
        "kind": {"const": "final"},
        "project": {"type": "string"},
        "status": {"enum": ["ok", "not_rendered"]},
        "status_note": STR,
        "private": {"type": "boolean"},
        "gate_validation": {"type": ["object", "null"]},
        "run_id": STR,
        "run_stages": {"type": "array", "items": {"type": "object", "required": ["stage", "status"]}},
        "earlier_run_stages": {"type": "array", "items": {"type": "object", "required": ["stage", "status"]}},
        "stopped_stages": {"type": "array", "items": {"type": "object", "required": ["stage", "status"]}},
        "stages": {"type": "object", "required": ["render", "polish", "check"]},
        "polish_allowed": {"type": "boolean"},
        "advisory": {"type": "boolean"},
        "advisory_flags": {"type": "array", "items": {"type": "string"}},
        "summary": {"type": "object", "required": ["views", "polished", "cycles", "cycles_by_reason"]},
        "views": {"type": "array", "items": FINAL_VIEW},
        "rooms_mixed": {"type": "array", "items": {"type": "string"}},
        "models": {"type": "array"},
        "contact_sheets": {"type": "object", "additionalProperties": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}},
    },
}


NEEDS_REVIEW_MANIFEST = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["schema_version", "kind", "project", "status", "private", "reasons", "documents", "debug_images",
                 "building", "intake", "run_stages", "summary", "views", "advisory_flags", "warnings"],
    "properties": {
        "schema_version": {"const": "0.1"},
        "kind": {"const": "final"},
        "project": {"type": "string"},
        "status": {"const": "needs_review"},
        "private": {"type": "boolean"},
        "reasons": {"type": "array", "minItems": 1, "items": {"type": "string"}},
        "documents": {"type": "array", "items": {"type": "object", "required": ["file", "page"]}},
        "debug_images": {"type": "array", "items": {"type": "object", "required": ["source", "preview"]}},
        "building": {"type": ["object", "null"]},
        "intake": {"type": ["object", "null"]},
        "run_id": STR,
        "run_stages": {"type": "array"},
        "earlier_run_stages": {"type": "array"},
        "summary": {"type": "object", "required": ["views", "polished", "cycles", "cycles_by_reason"]},
        "views": {"type": "array", "maxItems": 0},
        "advisory_flags": {"type": "array", "items": {"type": "string"}},
        "warnings": {"type": "array", "items": {"type": "string"}},
    },
}


def validate_final_manifest(manifest: dict) -> list[str]:
    """Schema errors of a ``final_manifest.json`` dict (empty list = valid); a needs-review manifest has its own."""
    import jsonschema
    schema = NEEDS_REVIEW_MANIFEST if manifest.get("status") == "needs_review" else FINAL_MANIFEST
    validator = jsonschema.Draft202012Validator(schema)
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in sorted(validator.iter_errors(manifest), key=lambda e: list(e.absolute_path))]


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------

@dataclass
class Inputs:
    """Everything the final report reads; a missing file is None / empty and noted in ``warnings``."""
    project_out: Path
    out_dir: Path
    project: str
    warnings: list = field(default_factory=list)
    render_manifest: Optional[dict] = None
    entries: dict = field(default_factory=dict)          # camera -> render entry (manifest order)
    scene: Optional[dict] = None
    table: dict = field(default_factory=dict)            # pass index -> element (wenart.views.index_table)
    building: Optional[dict] = None
    building_path: Optional[Path] = None
    brief: Optional[dict] = None
    polish: Optional[dict] = None
    polish_views: dict = field(default_factory=dict)
    check: Optional[dict] = None
    check_calibration: Optional[dict] = None
    expected: dict = field(default_factory=dict)         # camera -> expected_view (check/expected_views.json)
    answers: list = field(default_factory=list)
    gate_calibration: Optional[dict] = None
    gate_validation: Optional[dict] = None
    private: bool = False
    stage_records: list = field(default_factory=list)    # run/*.json of this run (split_runs), in run order
    earlier_records: list = field(default_factory=list)  # run/*.json of earlier runs (stages this run did not reach)
    run_id: Optional[str] = None                         # this run (the newest record's run_id)
    intake: Optional[dict] = None                        # intake_manifest.json (private projects)
    cameras: dict = field(default_factory=dict)          # camera name -> scene-manifest camera plan
    gate: Optional[dict] = None                          # gate_validation_summary (effective decision)

    @property
    def render_dir(self) -> Path:
        return self.project_out / "renders"

    @property
    def polish_dir(self) -> Path:
        return self.project_out / "polish"

    @property
    def check_dir(self) -> Path:
        return self.project_out / "check"


def _building_path(scene: dict, project_out: Path) -> Optional[Path]:
    """The building file of a scene manifest when ``project_paths`` could not run: the manifest's
    ``building`` (absolute, or relative to the repo root: ``views._resolve_repo_path``, §1.1), else
    ``building_final.json`` in the project output."""
    from wenart import views as VW

    p = VW._resolve_repo_path(scene.get("building"), project_out)
    if p is not None and p.is_file():
        return p
    fallback = project_out / "building_final.json"
    return fallback if fallback.is_file() else None


def is_private(project_out: Path, explicit: bool = False) -> bool:
    """True for a private project (§7.1): asked for, staged by ``wenart.intake`` (its
    ``intake_manifest.json``), under the private outputs root, or named like a private alias.
    Any one of these is enough (a private project must never be treated as public)."""
    from wenart.run.projects import ALIAS_RE, PRIVATE_OUTPUTS, RESERVED_ALIASES

    out = Path(project_out).resolve()
    if explicit or (out / "intake_manifest.json").is_file():
        return True
    try:
        out.relative_to(PRIVATE_OUTPUTS.resolve())
        return True
    except ValueError:
        pass
    return bool(ALIAS_RE.match(out.name)) or out.name in RESERVED_ALIASES


def load_stage_records(project_out: Path, warnings: Optional[list] = None) -> list[dict]:
    """``run/*.json`` stage records (§1.2) as ``{stage, status, seconds, note, rc, started_utc, run_id}``, in run
    order (``started_utc``, then name), of every run (``split_runs`` keeps this run's). The report's own record
    is left out: it describes an earlier report."""
    folder = Path(project_out) / "run"
    out = []
    for path in sorted(folder.glob("*.json")) if folder.is_dir() else []:
        data = C.read_json(path, warnings)
        if not isinstance(data, dict) or not data.get("status"):
            continue
        if data.get("kind") not in (None, "stage_record"):
            continue
        stage = str(data.get("stage") or path.stem)
        if stage == "report":
            continue
        out.append({"stage": stage, "status": data.get("status"), "seconds": data.get("seconds"),
                    "note": data.get("note"), "rc": data.get("rc"), "started_utc": data.get("started_utc"),
                    "run_id": data.get("run_id")})
    out.sort(key=lambda r: (str(r.get("started_utc") or "~"), r["stage"]))
    return out


def split_runs(records: list[dict]) -> tuple[list[dict], list[dict], Optional[str]]:
    """``(this run's records, earlier runs' records, this run_id)``.

    A record of an older run stays on the volume when this run did not reach its stage (wenart/run/state.py);
    the run manifest lists only this run's records, and so does the report. This run is the ``run_id`` of the
    newest record (largest ``started_utc``: the orchestrator writes the intake and pipeline records first and
    runs the report last). Without a ``run_id`` on the newest record (records of a hand-run project) every
    record counts as this run's.
    """
    dated = [r for r in records if r.get("started_utc")]
    run_id = max(dated, key=lambda r: str(r["started_utc"])).get("run_id") if dated else None
    if not run_id:
        return list(records), [], None
    return ([r for r in records if r.get("run_id") == run_id], [r for r in records if r.get("run_id") != run_id],
            str(run_id))


def stopped_stages(records: list[dict]) -> list[dict]:
    """``[{stage, status, note}]`` of this run's stages that ended ``incomplete`` or ``failed``."""
    return [{"stage": r["stage"], "status": r["status"], "note": r.get("note")} for r in records
            if r.get("status") in STOPPED_STATUSES]


def brief_warnings(brief: Optional[dict], private: bool = False) -> list[str]:
    """The warnings of ``wenart.brief.load_brief`` (no ``brief.yaml``, a value of the wrong type, ...). For a
    private project the user's value is left out (``got str 'no'`` -> ``got str``); the keys and the defaults
    come from ``wenart/defaults.yaml``."""
    out = []
    for text in (brief or {}).get("warnings") or []:
        text = str(text)
        if private:
            text = _BRIEF_GOT_VALUE.sub(r"\1\2", _BRIEF_LIST_VALUE.sub(r"\1\2", text))
        out.append(text)
    return out


def load_inputs(project_out, out_dir=None, private: bool = False) -> Inputs:
    """Read every manifest of a project output folder (see module docstring); never raises for a missing file."""
    from wenart import views as VW

    out = Path(project_out).resolve()
    inp = Inputs(project_out=out, out_dir=Path(out_dir).resolve() if out_dir else out / FINAL_DIR,
                 project=out.name, private=is_private(out, private))
    w = inp.warnings
    try:
        paths = VW.project_paths(out)
    except Exception as exc:  # noqa: BLE001 - missing/broken scene manifest or brief.yaml: report what is there
        w.append(f"project inputs not fully readable ({type(exc).__name__}: {exc}); brief not loaded, polish "
                 f"permission taken as the default (true)")
        paths = None
    if paths is not None:
        inp.scene = paths["scene_manifest"]
        inp.project = str(paths["project"] or out.name)
        inp.building_path = paths["building_path"]
        inp.brief = paths["brief"]
        w.extend(paths["warnings"])
        w.extend(brief_warnings(inp.brief, inp.private))
    else:
        inp.scene = C.read_json(out / "scene" / "scene_manifest.json", w)
        if inp.scene is None:
            w.append("scene/scene_manifest.json not readable: no element table or building")
        else:
            inp.project = str(inp.scene.get("project") or out.name)
            inp.building_path = _building_path(inp.scene, out)
    if inp.scene is not None:
        inp.table = VW.index_table(inp.scene)
        inp.cameras = {c["name"]: c for c in inp.scene.get("cameras") or [] if isinstance(c, dict) and c.get("name")}
    inp.building = C.read_json(inp.building_path, w) if inp.building_path else None
    inp.render_manifest = C.read_json(inp.render_dir / "render_manifest.json", w)
    if inp.render_manifest is None:
        w.append("renders/render_manifest.json not found: no rendered views")
    for e in (inp.render_manifest or {}).get("renders") or []:
        if isinstance(e, dict) and e.get("camera"):
            inp.entries[e["camera"]] = e
    inp.gate_calibration = C.read_json(inp.project_out / "gate" / "gate_calibration.json", w)
    inp.gate_validation = C.read_json(inp.project_out / "gate" / "gate_validation.json", w)
    inp.gate = gate_validation_summary(inp)
    inp.polish = C.read_json(inp.polish_dir / "polish_manifest.json", w)
    if inp.polish is not None and inp.polish.get("kind") not in (None, "run"):
        w.append(f"polish/polish_manifest.json is a {inp.polish.get('kind')!r} manifest, not a final run: "
                 f"treated as polish not run")
        inp.polish = None
    if inp.polish is not None and inp.gate is not None and inp.gate["decision"] in NO_POLISH_DECISIONS:
        # §7.3: no polish for this project, so the orchestrator skipped the polish; the manifest is an earlier
        # run's (its views, models and seconds are not this report's).
        w.append(f"polish/polish_manifest.json not used: the gate validation says {inp.gate['decision']} (no "
                 f"polish for this project; the manifest is from an earlier polish run)")
        inp.polish = None
    for v in (inp.polish or {}).get("views") or []:
        if isinstance(v, dict) and v.get("camera"):
            inp.polish_views[v["camera"]] = v
    inp.check = C.read_json(inp.check_dir / "check_manifest.json", w)
    inp.check_calibration = C.read_json(inp.check_dir / "check_calibration.json", w)
    expected = C.read_json(inp.check_dir / "expected_views.json", w)
    if isinstance(expected, dict):
        inp.expected = expected["views"] if isinstance(expected.get("views"), dict) else expected
    for path in sorted(inp.check_dir.glob("answers_*.json")) if inp.check_dir.is_dir() else []:
        data = C.read_json(path, w)
        if isinstance(data, dict):
            inp.answers.append(data)
    inp.stage_records, inp.earlier_records, inp.run_id = split_runs(load_stage_records(out, w))
    inp.intake = C.read_json(out / "intake_manifest.json", w)
    return inp


def gate_validation_summary(inp: Inputs) -> Optional[dict]:
    """The project's gate validation (§7.3) with its effect on the finals; None when none is recorded.

    A validation whose recorded calibration hash differs from the current ``gate_calibration.json``
    (re-calibrated without validating again), or with an unknown decision, counts as ``not_validated``.
    """
    v = inp.gate_validation
    if not isinstance(v, dict):
        return None
    recorded = v.get("decision")
    decision = recorded if recorded in GATE_EFFECT else "not_validated"
    reasons = [str(r) for r in v.get("reasons") or []]
    if recorded not in GATE_EFFECT:
        reasons.append(f"unknown gate validation decision {recorded!r}")
    sha = (v.get("calibration") or {}).get("sha256")
    if sha:
        from wenart.canonical import canonical_sha256
        if canonical_sha256(inp.project_out / "gate" / "gate_calibration.json") != sha:
            decision = "not_validated"
            reasons.append("gate_calibration.json changed after the validation (run gate validate again)")
    return {"decision": decision, "recorded_decision": recorded, "benign_accept": v.get("benign_accept"),
            "negative_reject": v.get("negative_reject"), "n_benign": v.get("n_benign"),
            "n_negative": v.get("n_negative"), "limits": v.get("limits") or {}, "reasons": reasons,
            "effect": GATE_EFFECT[decision], "polish_allowed": decision not in NO_POLISH_DECISIONS}


# --------------------------------------------------------------------------
# Small lookups
# --------------------------------------------------------------------------

def polish_allowed(brief: Optional[dict]) -> bool:
    """The brief's ``polish`` value (default true when there is no brief)."""
    values = (brief or {}).get("values") or {}
    return values.get("polish", True) is not False


def level_of(inp: Inputs, camera: str) -> str:
    entry = inp.entries.get(camera) or {}
    if entry.get("level_id"):
        return str(entry["level_id"])
    for cam in (inp.scene or {}).get("cameras") or []:
        if cam.get("name") == camera and cam.get("level_id"):
            return str(cam["level_id"])
    exp = inp.expected.get(camera) or {}
    lvl = (exp.get("json_crosscheck") or {}).get("level_id")
    return str(lvl) if lvl else "unknown"


def room_of(inp: Inputs, camera: str) -> Optional[str]:
    for src in (inp.entries.get(camera), inp.polish_views.get(camera), inp.expected.get(camera)):
        if src and src.get("room_id"):
            return src["room_id"]
    for cam in (inp.scene or {}).get("cameras") or []:
        if cam.get("name") == camera:
            return cam.get("room_id")
    return None


def room_types(building: Optional[dict]) -> dict:
    return {r.get("id"): r.get("room_type") for r in (building or {}).get("rooms") or []}


def building_elements(building: Optional[dict]) -> dict:
    """``{id: element}`` of every wall, opening, room, furniture piece and decor item of the building."""
    out: dict = {}
    for key in ("walls", "openings", "rooms", "furniture", "decor"):
        for el in (building or {}).get(key) or []:
            if isinstance(el, dict) and el.get("id"):
                out[el["id"]] = {**el, "_collection": key}
    return out


def evidence_text(evidence: Any, limit: int = 2) -> str:
    """``file p<page> layer entity method confidence`` of the first ``limit`` evidence records."""
    parts = []
    for ev in (evidence or [])[:limit]:
        if not isinstance(ev, dict):
            continue
        bits = [str(ev.get("file") or "?")]
        if ev.get("page") is not None:
            bits.append(f"p{ev['page']}")
        for key in ("layer", "entity", "block"):
            if ev.get(key):
                bits.append(str(ev[key]))
        if ev.get("box"):
            bits.append(f"box {ev['box']}")
        if ev.get("method"):
            bits.append(str(ev["method"]))
        if isinstance(ev.get("confidence"), (int, float)):
            bits.append(f"{float(ev['confidence']):.2f}")
        parts.append(" ".join(bits))
    more = len(evidence or []) - limit
    if more > 0:
        parts.append(f"+{more} more")
    return "; ".join(parts) or "-"


def element_info(inp: Inputs, elements: dict, wid: Optional[str]) -> dict:
    """``{type, kind, source, status, evidence}`` of an element id from the building, else the index table."""
    if not wid:
        return {}
    el = elements.get(wid)
    if el is not None:
        coll = el.get("_collection")
        source = el.get("source") or ("from_documents" if coll in ("walls", "openings", "rooms") else None)
        ev = el.get("evidence") or []
        if ev:
            text = evidence_text(ev)
        else:                               # decor and AI pieces carry method + reason instead of evidence
            text = ": ".join(str(x) for x in (el.get("method"), el.get("reason")) if x) or "-"
        return {"type": el.get("type") or el.get("room_type"), "kind": coll, "source": source,
                "status": el.get("status"), "evidence": text}
    for t in inp.table.values():
        if t.get("wenart_id") == wid:
            return {"type": t.get("type"), "kind": t.get("kind"), "source": t.get("source"),
                    "status": t.get("status"), "evidence": evidence_text(t.get("evidence"))}
    return {}


def view_elements(inp: Inputs, camera: str) -> list[dict]:
    """The elements in a view: ``check/expected_views.json`` when present, else the render's index statistics."""
    exp = inp.expected.get(camera)
    if isinstance(exp, dict) and isinstance(exp.get("elements"), list):
        return [{"id": e.get("wenart_id"), "kind": e.get("kind"), "type": e.get("type"), "source": e.get("source"),
                 "status": e.get("status"), "role": e.get("role"), "pixels": e.get("pixels")}
                for e in exp["elements"] if isinstance(e, dict) and e.get("wenart_id")]
    entry = inp.entries.get(camera) or {}
    stats = entry.get("index_stats")
    if stats is None:
        stats = {str(v): {} for v in entry.get("index_values") or []}
    out = []
    for idx in sorted(stats, key=lambda s: int(s)):
        t = inp.table.get(int(idx))
        if t is None:
            out.append({"id": f"index:{idx}", "kind": "unknown", "type": None, "source": None, "status": None,
                        "role": None, "pixels": (stats[idx] or {}).get("pixels")})
            continue
        out.append({"id": t["wenart_id"], "kind": t.get("kind"), "type": t.get("type"), "source": t.get("source"),
                    "status": t.get("status"), "role": None, "pixels": (stats[idx] or {}).get("pixels")})
    return out


def ids_by_source(elements: list[dict]) -> dict:
    out: dict[str, list] = {}
    for e in elements:
        if e.get("role") == "ignore":
            continue
        src = e.get("source") or "unknown"
        if e["id"] not in out.setdefault(src, []):
            out[src].append(e["id"])
    return {k: sorted(v) for k, v in sorted(out.items())}


def unverified_in_view(elements: list[dict]) -> list[str]:
    """Pieces in view whose status is unverified or whose type is unknown (ignored slivers left out)."""
    return sorted({e["id"] for e in elements if e.get("role") != "ignore"
                   and (e.get("status") == "unverified" or e.get("type") == "unknown")})


# --------------------------------------------------------------------------
# Vision check entries
# --------------------------------------------------------------------------

def image_entries(cview: Optional[dict]) -> dict:
    """``{image kind: entry}`` of one camera of ``check_manifest.json`` (non-image keys left out)."""
    return {k: v for k, v in (cview or {}).items() if k not in CHECK_VIEW_KEYS and isinstance(v, dict)}


def checked(entry: Optional[dict]) -> bool:
    """An element check that ran (not only a preference entry)."""
    return isinstance(entry, dict) and not entry.get("preference_only") and "verdict" in entry


def incomplete_detail(entry: Optional[dict], name: str) -> Optional[str]:
    """Why a check entry cannot support a decision (None when it can)."""
    if not checked(entry):
        return f"{name} image not checked"
    if entry.get("verdict") == "not_computed" or entry.get("not_computed"):
        keys = ", ".join(entry.get("not_computed") or []) or "a pass"
        return f"{name} image: not computed ({keys})"
    if entry.get("unreliable"):
        return f"{name} image: unreliable pass ({', '.join(entry['unreliable'])} saw the decoy)"
    return None


def differential_losses(cycles: Optional[dict], polished: Optional[dict]) -> list[dict]:
    """Elements ok/unverified on the Cycles render and confirmed missing/changed on the polished one (§5.5)."""
    if not checked(cycles) or not checked(polished):
        return []
    out = []
    for eid, e in (polished.get("elements") or {}).items():
        before = ((cycles.get("elements") or {}).get(eid) or {}).get("result")
        if e.get("result") in MISMATCH_RESULTS and before in ("ok", "unverified"):
            out.append({"reason": "vision_check", "what": "element", "id": eid, "type": e.get("type"),
                        "source": e.get("source"), "cycles": before, "polished": e.get("result")})
    return out


def check_summary(entry: Optional[dict]) -> Optional[dict]:
    """Verdict and counts of one image's check entry."""
    if not isinstance(entry, dict):
        return None
    elements = entry.get("elements") or {}
    results: dict[str, int] = {}
    for e in elements.values():
        results[str(e.get("result"))] = results.get(str(e.get("result")), 0) + 1
    extras = entry.get("extras") or []
    return {"verdict": entry.get("verdict"), "results": dict(sorted(results.items())),
            "mismatches": len(confirmed_items(check_items(entry, ""))),
            "extras_confirmed": sum(1 for x in extras if x.get("confirmed")),
            "counts": {k: (c or {}).get("result") for k, c in (entry.get("counts") or {}).items()},
            "not_computed": list(entry.get("not_computed") or []), "unreliable": list(entry.get("unreliable") or []),
            "preference_only": bool(entry.get("preference_only"))}


def check_items(entry: Optional[dict], image: str) -> list[dict]:
    """Mismatch items of one image's check entry: elements confirmed missing/changed or disputed,
    confirmed non-decor extras, door/window counts out of range."""
    items: list[dict] = []
    if not checked(entry):
        return items
    for eid, e in (entry.get("elements") or {}).items():
        res = e.get("result")
        if res in MISMATCH_RESULTS or res == "disputed":
            items.append({"image": image, "what": "element", "id": eid, "type": e.get("type"),
                          "kind": e.get("kind"), "role": e.get("role"), "source": e.get("source"), "result": res,
                          "confirmed": res in MISMATCH_RESULTS, "notes": list(e.get("notes") or [])})
    for x in entry.get("extras") or []:
        if x.get("confirmed") and x.get("class") in NON_DECOR_CLASSES:
            cats = x.get("categories") or {}
            items.append({"image": image, "what": "extra", "id": None, "type": ", ".join(sorted(set(cats.values())))
                          or x.get("category"), "kind": x.get("class"), "role": None, "source": None,
                          "result": "extra", "confirmed": True, "box_px": x.get("box_px"), "notes": []})
    for kind, c in (entry.get("counts") or {}).items():
        if (c or {}).get("result") in ("fewer", "more"):
            items.append({"image": image, "what": "count", "id": None, "type": kind, "kind": kind, "role": None,
                          "source": None, "result": f"{kind} count {c['result']}", "confirmed": True,
                          "expected": c.get("expected"), "passes": c.get("passes"), "notes": []})
    return items


def confirmed_items(items: list[dict]) -> list[dict]:
    """Items that count as mismatches: confirmed, and for elements only required ones (optional ones are info)."""
    return [i for i in items if i.get("confirmed") and (i["what"] != "element" or i.get("role") == "required")]


def crosscheck_items(cc: Optional[dict]) -> list[dict]:
    """The JSON cross-check findings of the Cycles render (§5.1) as mismatch items."""
    items = []
    for key in CROSSCHECK_KEYS:
        for it in (cc or {}).get(key) or []:
            if not isinstance(it, dict):
                continue
            detail = []
            if it.get("visible_share") is not None:
                detail.append(f"visible {float(it['visible_share']):.2f}")
            if it.get("area_frac") is not None:
                detail.append(f"area {float(it['area_frac']):.3f}")
            if it.get("offset_frac_w") is not None:            # check manifests before the containment test
                detail.append(f"offset {float(it['offset_frac_w']):.3f} W")
            if it.get("outside_share") is not None:
                detail.append(f"{float(it['outside_share']) * 100:.0f} % of its pixels > "
                              f"{float(it.get('margin_m') or 0.1):.2f} m outside the drawing")
            if it.get("pixels") is not None:
                detail.append(f"{it['pixels']} px")
            items.append({"image": "cycles", "what": "crosscheck", "id": it.get("id"), "type": it.get("type"),
                          "kind": it.get("kind"), "role": None, "source": it.get("source"), "result": key,
                          "confirmed": True, "detail": ", ".join(detail), "notes": []})
    return items


# --------------------------------------------------------------------------
# The decision
# --------------------------------------------------------------------------

def other_pixels(entry: dict, sha256: Optional[str], what: str) -> Optional[str]:
    """Why a check entry is not about the image with ``sha256`` (None when it is).

    The check manifest records the sha256 of every image it checked
    (``image_sha256``); a file name is not enough, because a re-run of the
    polish writes new pixels under the same ``<cam>_a<k>.png``. ``sha256``
    None = the current file is unknown (no PNG in a results copy): not
    compared. A manifest without hashes cannot vouch for any image.
    """
    if sha256 is None:
        return None
    shas = entry.get("image_sha256")
    if not shas:
        return (f"the check manifest records no sha256 of the {what} it checked "
                "(re-run vision_check combine on the current images)")
    if sha256 not in shas:
        return (f"the vision check saw other pixels than the current {what} (image sha256 differs; "
                "re-run the vision check)")
    return None


def _cycles(reason: Optional[str], detail: Optional[str], candidate: Optional[dict] = None) -> dict:
    return {"final": "cycles", "reason": reason, "detail": detail, "candidate": candidate}


def decide(pview: Optional[dict], cview: Optional[dict], *, polish_ran: bool, check_ran: bool,
           allowed: bool = True, polish_dir: Optional[Path] = None, source_sha256: Optional[str] = None,
           gate_decision: Optional[str] = None) -> dict:
    """``{"final", "reason", "detail", "candidate"}`` of one view (see the module docstring; pure but for file checks).

    ``pview``: the view's polish-manifest entry; ``cview``: its
    check-manifest camera entry; ``polish_dir``: where the attempt PNGs are
    (None skips the file check); ``source_sha256``: the current render PNG's
    hash (None skips the staleness check); ``gate_decision``: the project's
    effective gate validation decision (None = not recorded, M5 outputs).
    """
    if not allowed:
        return _cycles("brief", "brief.yaml polish: false")
    if gate_decision in NO_POLISH_DECISIONS:
        return _cycles("gate_validation", f"gate validation {gate_decision}: no polish for this project")
    if not polish_ran:
        return _cycles("not_run", "polish not run")
    if pview is None:
        return _cycles("not_run", "view not in the polish manifest")
    if pview.get("final") != "polished":
        reason = pview.get("reason")
        if reason not in REASONS:
            detail = f"polish final {pview.get('final')!r}, reason {reason!r}"
            reason = "not_run" if pview.get("final") is None and reason is None else "error"
            return _cycles(reason, detail)
        if reason == "gate":
            tried = [f"a{a.get('k')} " + _short_gate(gate_summary(a)) for a in pview.get("attempts") or []]
            return _cycles(reason, "no ladder attempt passed the gate" + (f": {'; '.join(tried)}" if tried else ""))
        return _cycles(reason, f"polish: {reason}")
    k = pview.get("final_attempt")
    candidate = next((a for a in pview.get("attempts") or [] if a.get("k") == k), None)
    if candidate is None or not candidate.get("png"):
        return _cycles("error", f"polish final attempt {k} has no image in the manifest")
    polished_sha256 = candidate.get("sha256")
    if polish_dir is not None:
        if not (Path(polish_dir) / candidate["png"]).is_file():
            return _cycles("error", f"polished image {candidate['png']} not found", candidate)
        polished_sha256 = C.sha256_file(Path(polish_dir) / candidate["png"])      # the file that would ship
    if source_sha256 and pview.get("source_sha256") and pview["source_sha256"] != source_sha256:
        return _cycles("error", "polished from another render (source sha256 differs from the current render)",
                       candidate)
    if not check_ran:
        return _cycles("check_incomplete", "vision check not run", candidate)
    if cview is None:
        return _cycles("check_incomplete", "view not in the check manifest", candidate)
    polished, cycles = cview.get("polished"), cview.get("cycles")
    for entry, name in ((polished, "polished"), (cycles, "Cycles")):
        why = incomplete_detail(entry, name)
        if why:
            return _cycles("check_incomplete", why, candidate)
    seen = [Path(str(p)).name for p in polished.get("images") or []]
    if seen and Path(candidate["png"]).name not in seen:
        return _cycles("check_incomplete", f"the check saw {', '.join(seen)}, not {candidate['png']}", candidate)
    for entry, sha, what in ((polished, polished_sha256, f"polished image {candidate['png']}"),
                             (cycles, source_sha256, "Cycles render")):
        why = other_pixels(entry, sha, what)
        if why:
            return _cycles("check_incomplete", why, candidate)
    if cview.get("polished_rejected"):
        reasons = cview.get("polished_reasons") or []
        reason = cview.get("polished_reason")
        if reason not in ("vision_check", "check_incomplete"):
            incomplete = any(isinstance(r, dict) and r.get("reason") == "check_incomplete" for r in reasons)
            reason = "check_incomplete" if incomplete else "vision_check"
        return _cycles(reason, "; ".join(_reason_text(r) for r in reasons) or "rejected by the vision check",
                       candidate)
    losses = differential_losses(cycles, polished)
    if losses:
        return _cycles("vision_check", "; ".join(_reason_text(r) for r in losses)
                       + " (recomputed here; the check manifest did not flag it)", candidate)
    return {"final": "polished", "reason": None, "detail": None, "candidate": candidate}


def _reason_text(r: Any) -> str:
    if not isinstance(r, dict):
        return str(r)
    if r.get("what") == "element":
        return f"{r.get('id')} ({r.get('type')}, {r.get('source')}): {r.get('cycles')} -> {r.get('polished')}"
    if r.get("what") == "added_by_polish":
        return f"added_by_polish {r.get('class')} at {r.get('box_px')}"
    return ", ".join(f"{k} {v}" for k, v in r.items() if k != "reason") or str(r.get("reason"))


# --------------------------------------------------------------------------
# Per view
# --------------------------------------------------------------------------

def attempt_settings(a: Optional[dict]) -> Optional[dict]:
    if not a:
        return None
    keys = ("k", "role", "strength", "control", "scale", "size", "mode", "seed", "steps", "seconds", "png",
            "sha256", "attempt_key", "panes_restored")
    return {k: a.get(k) for k in keys}


def gate_summary(a: Optional[dict]) -> Optional[dict]:
    gate = (a or {}).get("gate")
    if not isinstance(gate, dict):
        return None
    metrics = gate.get("metrics") or {}
    globals_ = {k: v.get("global") for k, v in metrics.items()
                if isinstance(v, dict) and "global" in v and k not in ("regions", "seconds")}
    return {"decision": gate.get("decision"), "reasons": list(gate.get("reasons") or []),
            "notes": len(gate.get("notes") or []), "global": globals_, "gate_key": gate.get("gate_key")}


def _short_gate(g: Optional[dict]) -> str:
    if not g:
        return "-"
    if g["decision"] == "accept":
        return "accept"
    checks = sorted({str(r.get("check")) for r in g["reasons"] if isinstance(r, dict)})
    return "reject" + (f" ({', '.join(checks)})" if checks else "")


def camera_plan(cam: Optional[dict]) -> Optional[dict]:
    """``{policy, score, score_total, warning, placement, shift_y}`` of a scene-manifest camera (§1.3).

    Manifests written before Milestone 6 carry no ``policy``: their cameras come from the M5 rules.
    """
    if not isinstance(cam, dict):
        return None
    score = cam.get("score") if isinstance(cam.get("score"), dict) else None
    total = (score or {}).get("total")
    return {"policy": cam.get("policy") or "m5", "policy_recorded": cam.get("policy") is not None,
            "score": score, "score_total": float(total) if isinstance(total, (int, float)) else None,
            "warning": cam.get("warning"), "placement": cam.get("placement"), "shift_y": cam.get("shift_y")}


def build_views(inp: Inputs) -> list[dict]:
    """One final-manifest entry per rendered view (the render manifest's cameras, in its order).

    A camera that only the polish manifest has is an earlier run's camera (the polish rebuilds its views from
    the current renders): a warning, never a view of this report.
    """
    elements_by_id = building_elements(inp.building)
    rtypes = room_types(inp.building)
    allowed = polish_allowed(inp.brief)
    cams = list(inp.entries)
    for cam in inp.polish_views:
        if cam not in inp.entries:
            inp.warnings.append(f"{cam}: in the polish manifest but not in the render manifest (an earlier run's "
                                f"camera; not a view of this report)")
    check_views = (inp.check or {}).get("views") or {}
    out = []
    for cam in cams:
        entry = inp.entries.get(cam) or {}
        pview = inp.polish_views.get(cam)
        cview = check_views.get(cam)
        src_png = inp.render_dir / entry["png"] if entry.get("png") else None
        src_sha = C.sha256_file(src_png) if src_png is not None and src_png.is_file() else None
        dec = decide(pview, cview, polish_ran=inp.polish is not None, check_ran=inp.check is not None,
                     allowed=allowed, polish_dir=inp.polish_dir, source_sha256=src_sha,
                     gate_decision=(inp.gate or {}).get("decision"))
        cand = dec["candidate"]
        if dec["final"] == "polished":
            image = inp.polish_dir / cand["png"]
        else:
            image = src_png
        elements = view_elements(inp, cam)
        kinds = image_entries(cview)
        cc = (cview or {}).get("json_crosscheck")
        if cc is None:
            cc = (inp.expected.get(cam) or {}).get("json_crosscheck")
        if isinstance(cc, dict) and cc.get("error"):
            inp.warnings.append(f"{cam}: JSON cross-check not computed ({cc['error']})")
        items = check_items(kinds.get("cycles"), "cycles") + check_items(kinds.get("polished"), "polished")
        items += crosscheck_items(cc)
        for it in items:
            info = element_info(inp, elements_by_id, it.get("id"))
            it["evidence"] = info.get("evidence", "-")
            it["source"] = it.get("source") or info.get("source")
            it["type"] = it.get("type") or info.get("type")
            if it.get("source") == "added_by_ai" and it["what"] in ("element", "crosscheck") \
                    and ADDED_BY_AI_NOTE not in it["notes"]:
                it["notes"].append(ADDED_BY_AI_NOTE)
        final_image = "polished" if dec["final"] == "polished" else "cycles"
        final_items = [i for i in items if i["image"] == final_image and i["what"] != "crosscheck"]
        pol_entry = kinds.get("polished") or {}
        vc = None
        if cview is not None:
            vc = {"cycles": check_summary(kinds.get("cycles")), "polished": check_summary(kinds.get("polished")),
                  "other": sorted(k for k in kinds if k not in ("cycles", "polished")),
                  "polished_rejected": bool(cview.get("polished_rejected")),
                  "polished_reason": cview.get("polished_reason"),
                  "polished_reasons": list(cview.get("polished_reasons") or []),
                  "needs_review": bool(cview.get("needs_review")),
                  "needs_review_reasons": list(cview.get("needs_review_reasons") or [])}
        needs_review = bool((cview or {}).get("needs_review")) or bool(confirmed_items(
            [i for i in items if i["image"] == "cycles"]))
        out.append({
            "camera": cam,
            "room_id": room_of(inp, cam),
            "room_type": rtypes.get(room_of(inp, cam)),
            "level_id": level_of(inp, cam),
            "final": dec["final"],
            "reason": dec["reason"],
            "detail": dec["detail"],
            "image": C.rel(image, inp.out_dir) if image is not None else None,
            "image_sha256": C.sha256_file(image) if image is not None and image.is_file() else None,
            "preview": None,
            "plan": None,
            "polish": None if pview is None else {"final": pview.get("final"), "reason": pview.get("reason"),
                                                  "final_attempt": pview.get("final_attempt"),
                                                  "attempts": len(pview.get("attempts") or []),
                                                  "prompt": pview.get("prompt")},
            "attempt": attempt_settings(cand),
            "gate": gate_summary(cand),
            "vision_check": vc,
            "json_crosscheck": cc,
            "preference": pol_entry.get("preference") if isinstance(pol_entry, dict) else None,
            "exposure": entry.get("exposure"),
            "window_pull": entry.get("window_pull"),
            "camera_plan": camera_plan(inp.cameras.get(cam)),
            "plan_kept": None,
            "ids_by_source": ids_by_source(elements),
            "unverified": unverified_in_view(elements),
            "mismatches": items,
            "final_mismatches": len(confirmed_items(final_items)),
            "needs_review": needs_review,
        })
    return out


# --------------------------------------------------------------------------
# Images: previews, plan copies, contact sheets
# --------------------------------------------------------------------------

def _load_rgb(path: Optional[Path]):
    if path is None or not Path(path).is_file():
        return None
    from wenart import views as VW
    try:
        return VW.read_rgb(path)
    except (OSError, ValueError):
        return None


def _final_source(inp: Inputs, view: dict) -> Optional[Path]:
    """The final image file, else a preview JPEG of the same image (results copies have no PNGs)."""
    candidates = []
    if view["final"] == "polished" and view["attempt"]:
        a = view["attempt"]
        candidates.append(inp.polish_dir / a["png"])
        pv = inp.polish_views.get(view["camera"]) or {}
        rec = next((x for x in pv.get("attempts") or [] if x.get("k") == a["k"]), {})
        if rec.get("preview"):
            candidates.append(inp.polish_dir / rec["preview"])
        candidates.append(inp.polish_dir / f"{view['camera']}_a{a['k']}_preview.jpg")
    else:
        entry = inp.entries.get(view["camera"]) or {}
        if entry.get("png"):
            candidates.append(inp.render_dir / entry["png"])
        if entry.get("preview"):
            candidates.append(inp.render_dir / entry["preview"])
    return next((c for c in candidates if c.is_file()), None)


def _font(size: int = 16):
    from PIL import ImageFont
    try:
        return ImageFont.load_default(size=size)
    except TypeError:                       # Pillow < 10.1: fixed bitmap font
        return ImageFont.load_default()


def tile_label(view: dict) -> str:
    return f"{view['camera']}  {'P' if view['final'] == 'polished' else 'C'}  U{len(view['unverified'])}"


def contact_sheet(tiles: list, columns: int = CONTACT_COLUMNS, tile_width: int = TILE_WIDTH):
    """One image of ``(label, PIL image)`` tiles, ``tile_width`` px wide, a label strip under each."""
    from PIL import Image, ImageDraw

    resized = []
    for label, img in tiles:
        h = max(1, round(img.height * tile_width / img.width))
        resized.append((label, img.resize((tile_width, h), Image.Resampling.LANCZOS)))
    cell_h = max(t.height for _, t in resized) + LABEL_HEIGHT
    cols = max(1, min(columns, len(resized)))
    rows = (len(resized) + cols - 1) // cols
    gap = 4
    sheet = Image.new("RGB", (cols * tile_width + (cols + 1) * gap, rows * cell_h + (rows + 1) * gap), (32, 32, 32))
    draw = ImageDraw.Draw(sheet)
    font = _font(16)
    for i, (label, t) in enumerate(resized):
        x = gap + (i % cols) * (tile_width + gap)
        y = gap + (i // cols) * (cell_h + gap)
        sheet.paste(t, (x, y))
        draw.rectangle([x, y + t.height, x + tile_width - 1, y + t.height + LABEL_HEIGHT - 1], fill=(0, 0, 0))
        draw.text((x + 6, y + t.height + 3), label, fill=(255, 255, 255), font=font)
    return sheet


def write_images(inp: Inputs, views: list[dict]) -> dict:
    """Final previews, plan copies and contact sheets into ``inp.out_dir``; returns ``{level: sheet name}``."""
    from PIL import Image

    out = inp.out_dir
    out.mkdir(parents=True, exist_ok=True)
    tiles: dict[str, list] = {}
    for view in views:
        cam = view["camera"]
        src = _final_source(inp, view)
        rgb = _load_rgb(src)
        if rgb is None:
            inp.warnings.append(f"{cam}: final image not found; no preview or contact tile")
        else:
            if src is not None and src.suffix.lower() in (".jpg", ".jpeg") and view["image"] \
                    and not (inp.out_dir / view["image"]).is_file():
                inp.warnings.append(f"{cam}: final PNG not here; preview made from {src.name}")
            name = f"{cam}_final_preview.jpg"
            C.save_jpeg_under(rgb, out / name)
            view["preview"] = name
            img = Image.fromarray(rgb)
            img.thumbnail((TILE_WIDTH * 2, TILE_WIDTH * 2))
            tiles.setdefault(view["level_id"], []).append((tile_label(view), img))
        plan = inp.check_dir / f"{cam}_plan.jpg"
        if plan.is_file() and inp.private:
            # A crop of the user's plan: named, never copied into final/ (§7.4); it stays on the volume.
            view["plan_kept"] = C.rel(plan, inp.project_out)
        elif plan.is_file():
            name = f"{cam}_plan.jpg"
            if plan.stat().st_size <= C.MAX_IMAGE_BYTES:
                shutil.copyfile(plan, out / name)
            else:
                C.save_jpeg_under(_load_rgb(plan), out / name)
                inp.warnings.append(f"{cam}: plan crop above 300 KB; re-encoded")
            view["plan"] = name
    sheets = {}
    for level in sorted(tiles):
        name = f"contact_{level}.jpg"
        C.save_jpeg_under(contact_sheet(tiles[level]), out / name)
        sheets[level] = name
    # Files of an earlier run that this run did not write are listed, not deleted.
    written = {v["preview"] for v in views} | {v["plan"] for v in views} | set(sheets.values())
    for pattern in ("*_final_preview.jpg", "*_plan.jpg", "contact_*.jpg"):
        for f in sorted(out.glob(pattern)):
            if f.name not in written:
                inp.warnings.append(f"final/{f.name} is from an earlier run (not part of this report)")
    return sheets


# --------------------------------------------------------------------------
# Project-level summaries
# --------------------------------------------------------------------------

def stage_seconds(inp: Inputs) -> dict:
    """Seconds per stage from the manifests (None when the stage left no numbers)."""
    def total(values) -> Optional[float]:
        vals = [float(v) for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
        return round(sum(vals), 1) if vals else None

    entries = list(inp.entries.values())
    attempts = [a for v in inp.polish_views.values() for a in v.get("attempts") or []]
    gate = []
    for a in attempts:
        if isinstance(a.get("gate_seconds"), (int, float)):
            gate.append(a["gate_seconds"])
        else:
            secs = ((a.get("gate") or {}).get("metrics") or {}).get("seconds") or {}
            gate.extend(v for v in secs.values() if isinstance(v, (int, float)))
    polish = total([a.get("seconds") for a in attempts])
    load = (inp.polish or {}).get("load_seconds")
    if polish is not None and isinstance(load, (int, float)):
        polish = round(polish + float(load), 1)
    calls = [c for ans in inp.answers for c in ((ans.get("calls") or {}).values()
                                                 if isinstance(ans.get("calls"), dict) else ans.get("calls") or [])]
    return {"build": total([(inp.scene or {}).get("seconds")]),
            "render": total([e.get("seconds") for e in entries]),
            "meter": total([(e.get("exposure") or {}).get("meter_seconds") for e in entries]),
            "polish": polish,
            "gate": total(gate),
            "check": total([c.get("latency_s") for c in calls if isinstance(c, dict)])}


def exposure_summary(inp: Inputs) -> dict:
    evs, modes, at_limit = [], set(), 0
    for e in inp.entries.values():
        exp = e.get("exposure") or {}
        if isinstance(exp.get("ev"), (int, float)):
            evs.append(float(exp["ev"]))
        if exp.get("mode"):
            modes.add(str(exp["mode"]))
        at_limit += bool(exp.get("at_limit"))
    pulls = [float(p["ev"]) for p in (e.get("window_pull") for e in inp.entries.values())
             if isinstance(p, dict) and isinstance(p.get("ev"), (int, float))]
    return {"min": min(evs) if evs else None, "max": max(evs) if evs else None, "views": len(evs),
            "at_limit": at_limit, "modes": sorted(modes),
            "window_pull": {"views": len(pulls), "min": min(pulls) if pulls else None,
                            "max": max(pulls) if pulls else None}}


def camera_summary(views: list[dict]) -> dict:
    """Views per camera policy, score range and the camera warnings (e.g. ``blocked unavoidable``)."""
    policies: dict[str, int] = {}
    scores, warnings = [], []
    for v in views:
        cp = v.get("camera_plan")
        if not cp:
            policies["unknown"] = policies.get("unknown", 0) + 1
            continue
        policies[cp["policy"]] = policies.get(cp["policy"], 0) + 1
        if cp["score_total"] is not None:
            scores.append(cp["score_total"])
        if cp.get("warning"):
            warnings.append(f"{v['camera']}: {cp['warning']}")
    return {"policies": dict(sorted(policies.items())), "scored": len(scores),
            "score_min": round(min(scores), 3) if scores else None,
            "score_mean": round(sum(scores) / len(scores), 3) if scores else None,
            "score_max": round(max(scores), 3) if scores else None, "warnings": warnings}


def rooms_summary(inp: Inputs, views: list[dict]) -> dict:
    """Per room: rendered views (1-3 per room in M6), polished/Cycles, polish room rule; building rooms
    without any rendered view are listed with ``views: []``."""
    rooms: dict[str, dict] = {}
    for v in views:
        r = rooms.setdefault(v["room_id"] or "-", {"views": [], "polished": [], "cycles": []})
        r["views"].append(v["camera"])
        r["polished" if v["final"] == "polished" else "cycles"].append(v["camera"])
    building_rooms = {r.get("id"): r for r in (inp.building or {}).get("rooms") or [] if isinstance(r, dict)}
    for rid in building_rooms:
        if rid and rid not in rooms:
            rooms[rid] = {"views": [], "polished": [], "cycles": []}
    rules = (inp.polish or {}).get("rooms") or {}
    for rid, r in rooms.items():
        r["mixed"] = bool(r["polished"]) and bool(r["cycles"])
        rule = rules.get(rid) or {}
        r["polish_rule"] = rule.get("rule")
        r["polish_rung"] = rule.get("rung")
        b = building_rooms.get(rid) or {}
        r["room_type"] = b.get("room_type")
        r["level_id"] = b.get("level_id")
    return dict(sorted(rooms.items()))


def model_rows(inp: Inputs) -> list[dict]:
    """``[{role, repo, revision, licence, source}]`` of every AI model named in the manifests."""
    rows = []
    models = (inp.polish or {}).get("models") or {}
    for role in ("base", "controlnet"):
        m = models.get(role)
        if isinstance(m, dict):
            rows.append({"role": f"polish {role}", "repo": m.get("repo"), "revision": m.get("revision"),
                         "licence": m.get("licence"), "source": "polish_manifest.json"})
    for key, m in (models.get("gate") or {}).items():
        if isinstance(m, dict):
            rows.append({"role": f"gate {key}", "repo": m.get("repo"), "revision": m.get("revision"),
                         "licence": m.get("licence"), "source": "polish_manifest.json"})
    check_models = (inp.check or {}).get("models") or {}
    cfg_models: dict = {}
    if check_models and any(not (m or {}).get("licence") for m in check_models.values()):
        try:
            from wenart.vision_check.config import load_config
            cfg_models = load_config().get("models") or {}
        except Exception:  # noqa: BLE001 - the licence then shows as unknown
            cfg_models = {}
    for key, m in check_models.items():
        m = m or {}
        rows.append({"role": f"check {key}", "repo": m.get("id") or m.get("repo"), "revision": m.get("revision"),
                     "licence": m.get("licence") or (cfg_models.get(key) or {}).get("licence"),
                     "source": "check_manifest.json"})
    return rows


def asset_licences(inp: Inputs) -> dict:
    """Licence counts of the texture assets (scene manifest) and the furniture/decor models (building)."""
    textures: dict[str, int] = {}
    for m in ((inp.scene or {}).get("materials") or {}).values():
        if isinstance(m, dict) and m.get("textured") and m.get("asset"):
            lic = str(m.get("licence") or "unknown")
            textures[lic] = textures.get(lic, 0) + 1
    models: dict[str, int] = {}
    for piece in list((inp.building or {}).get("furniture") or []) + list((inp.building or {}).get("decor") or []):
        asset = piece.get("asset") if isinstance(piece, dict) else None
        if isinstance(asset, dict) and asset.get("method") == "library":
            lic = str(asset.get("licence") or "unknown")
            models[lic] = models.get(lic, 0) + 1
    return {"textures": dict(sorted(textures.items())), "models": dict(sorted(models.items()))}


def advisory_flags(inp: Inputs, views: list[dict]) -> list[str]:
    """Open items the user must see: advisory check, missed targets, single pass, stages not run, uncalibrated gate."""
    flags = []
    if inp.polish is None:
        flags.append("polish not run (every view is the Cycles render)")
    elif inp.polish.get("incomplete"):
        flags.append("polish incomplete (deadline): some views did not finish their ladder")
    if inp.check is None:
        if any(v.get("polish") and v["polish"].get("final") == "polished" for v in views):
            flags.append("vision check not run: polished candidates kept as Cycles (check_incomplete)")
        else:
            flags.append("vision check not run")
    else:
        if inp.check.get("single_pass"):
            flags.append("vision check single pass: every result unverified (advisory)")
        if inp.check.get("advisory"):
            flags.append("vision check advisory" + (f": {inp.check['advisory_reason']}"
                                                    if inp.check.get("advisory_reason") else ""))
    if inp.check is not None and inp.check_calibration is None:
        flags.append("vision check calibration not run (check_calibration.json missing)")
    for m in (inp.check_calibration or {}).get("missed") or []:
        if isinstance(m, dict):
            flags.append(f"check target missed: {m.get('metric')} {C.cell(m.get('value'), 3)} "
                         f"(needs {m.get('op')} {m.get('threshold')})"
                         + (f", {m['reason']}" if m.get("reason") else ""))
    th = (inp.polish or {}).get("thresholds") or {}
    cal = th.get("calibration") if isinstance(th, dict) else None
    if inp.polish is not None and isinstance(cal, dict):
        if not cal.get("source"):
            flags.append("gate thresholds not calibrated yet (thresholds.yaml calibration.source is null)")
        if cal.get("accepted_shortfall"):
            flags.append(f"gate calibration accepted shortfall: {cal['accepted_shortfall']}")
    if not polish_allowed(inp.brief):
        flags.append("brief polish: false (no AI polish by request)")
    g = inp.gate
    if g is not None and g["decision"] != "ok":
        why = "; ".join(g["reasons"]) or "no reason recorded"
        flags.append(f"gate validation {g['decision']}: {g['effect']} ({why})")
    elif g is None and inp.polish is not None and polish_allowed(inp.brief):
        flags.append("gate validation not recorded: the polish of this project was not validated "
                     "(gate/gate_validation.json missing; Milestone 5 run)")
    for w in camera_summary(views)["warnings"]:
        flags.append(f"camera {w}")
    flags.extend(intake_flags(intake_summary(inp.intake)))
    return flags


# --------------------------------------------------------------------------
# Manifest and report
# --------------------------------------------------------------------------

def build_manifest(inp: Inputs, views: list[dict], sheets: dict) -> dict:
    by_reason: dict[str, int] = {}
    for v in views:
        if v["final"] == "cycles":
            by_reason[str(v["reason"])] = by_reason.get(str(v["reason"]), 0) + 1
    rooms = rooms_summary(inp, views)
    b = inp.building or {}
    flags = advisory_flags(inp, views)
    stages = {
        "render": "run" if inp.render_manifest is not None else "not_run",
        "polish": ("not_run" if inp.polish is None else "incomplete" if inp.polish.get("incomplete") else "run"),
        "check": "not_run" if inp.check is None else ("single_pass" if inp.check.get("single_pass") else "run"),
        "check_calibration": "not_run" if inp.check_calibration is None else "run",
        "gate_calibration": "not_run" if inp.gate_calibration is None else "run",
        "gate_validation": "not_run" if inp.gate is None else inp.gate["decision"],
        "expected": "run" if inp.expected else "not_run",
    }
    files = {"render_manifest": inp.render_dir / "render_manifest.json",
             "scene_manifest": inp.project_out / "scene" / "scene_manifest.json",
             "polish_manifest": inp.polish_dir / "polish_manifest.json",
             "check_manifest": inp.check_dir / "check_manifest.json",
             "check_calibration": inp.check_dir / "check_calibration.json",
             "expected_views": inp.check_dir / "expected_views.json",
             "gate_calibration": inp.project_out / "gate" / "gate_calibration.json",
             "gate_validation": inp.project_out / "gate" / "gate_validation.json"}
    inputs = {k: (C.rel(p, inp.out_dir) if p.is_file() else None) for k, p in files.items()}
    inputs["building"] = C.rel(inp.building_path, inp.out_dir) if inp.building_path and inp.building_path.is_file() \
        else None
    rendered = inp.render_manifest is not None
    return {
        "schema_version": "0.1",
        "kind": "final",
        "project": inp.project,
        "status": "ok" if rendered else "not_rendered",
        "status_note": None if rendered else NO_RENDERS,
        "private": inp.private,
        "inputs": inputs,
        "stages": stages,
        "run_id": inp.run_id,
        "run_stages": list(inp.stage_records),
        "earlier_run_stages": list(inp.earlier_records),
        "stopped_stages": stopped_stages(inp.stage_records),
        "gate_validation": inp.gate,
        "polish_allowed": polish_allowed(inp.brief),
        "brief_assumed": list((inp.brief or {}).get("assumed") or []),
        "advisory": bool((inp.check or {}).get("advisory")) or inp.check is None
        or bool((inp.check_calibration or {}).get("missed")),
        "advisory_flags": flags,
        "summary": {
            "views": len(views),
            "polished": sum(v["final"] == "polished" for v in views),
            "cycles": sum(v["final"] == "cycles" for v in views),
            "cycles_by_reason": dict(sorted(by_reason.items())),
            "final_mismatches": sum(v["final_mismatches"] for v in views),
            "views_with_final_mismatch": sum(v["final_mismatches"] > 0 for v in views),
            "crosscheck_findings": sum(1 for v in views for i in v["mismatches"] if i["what"] == "crosscheck"),
            "needs_review": sum(v["needs_review"] for v in views),
            "unverified_in_view": sum(len(v["unverified"]) for v in views),
            "exposure": exposure_summary(inp),
            "cameras": camera_summary(views),
            "views_per_room": views_per_room(rooms),
            "seconds": stage_seconds(inp),
            "rooms_mixed": sum(r["mixed"] for r in rooms.values()),
        },
        "views": views,
        "rooms": rooms,
        "rooms_mixed": [rid for rid, r in rooms.items() if r["mixed"]],
        "models": model_rows(inp),
        "assets": asset_licences(inp),
        "contact_sheets": sheets,
        "building": {"status": b.get("status"), "unverified": list(b.get("unverified") or []),
                     "conflicts": list(b.get("conflicts") or [])},
        "intake": intake_summary(inp.intake),
        "kept_on_volume": kept_on_volume(views) if inp.private else [],
        "warnings": list(inp.warnings),
    }


def views_per_room(rooms: dict) -> dict:
    """``{"<n> views": rooms}`` over the rooms of the report (0 = a building room without a rendered view)."""
    out: dict[str, int] = {}
    for rid, r in rooms.items():
        if rid == "-":
            continue
        key = str(len(r["views"]))
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: int(kv[0])))


def intake_note_texts() -> dict:
    """The fixed note texts of ``wenart/intake.py`` -> their kind (``brief``, ``dwg``, ``collision``)."""
    from wenart import intake as I

    return {f"not read: the brief must be {I.BRIEF_NAME} at the top level of the folder": "brief",
            I.DWG_NOTE: "dwg", "name collision": "collision"}


def intake_notes_by_kind(intake: dict) -> dict:
    """``{fixed note text: files}`` over the files of ``intake_manifest.json``. A note joins its texts with
    ``"; "`` (a DWG note plus ``name collision``); a text that is not one of ``intake_note_texts`` counts as
    ``OTHER_INTAKE_NOTE``, so no file name is ever copied."""
    known = sorted(intake_note_texts(), key=len, reverse=True)
    out: dict[str, int] = {}
    for f in intake.get("files") or []:
        note = f.get("note") if isinstance(f, dict) else None
        if not note:
            continue
        rest = str(note)
        for text in known:
            if text in rest:
                out[text] = out.get(text, 0) + 1
                rest = rest.replace(text, "", 1)
        if rest.replace(";", "").strip():
            out[OTHER_INTAKE_NOTE] = out.get(OTHER_INTAKE_NOTE, 0) + 1
    return dict(sorted(out.items()))


def intake_summary(intake: Optional[dict]) -> Optional[dict]:
    """Counts, reasons and fixed note texts of ``intake_manifest.json`` (private projects); never a file name.

    ``brief_staged``: a ``brief.yaml`` at the top level of the upload was kept (the pipeline reads it).
    """
    if not isinstance(intake, dict):
        return None
    from wenart.intake import BRIEF_NAME

    staged = [(f.get("staged") or f.get("would_stage_as")) for f in intake.get("files") or []
              if isinstance(f, dict) and f.get("kept")]
    return {"status": intake.get("status"), "reasons": list(intake.get("reasons") or []),
            "totals": dict(intake.get("totals") or {}),
            "skipped_by_reason": dict(intake.get("skipped_by_reason") or {}),
            "notes_by_kind": intake_notes_by_kind(intake),
            "brief_staged": BRIEF_NAME in staged}


def intake_flags(summary: Optional[dict]) -> list[str]:
    """Advisory flags from the intake notes: a brief that was not read, DWG files, other notes (counts only)."""
    if not summary:
        return []
    kinds = intake_note_texts()
    flags = []
    for text, n in (summary.get("notes_by_kind") or {}).items():
        if kinds.get(text) == "brief":
            if summary.get("brief_staged"):
                flags.append(f"{n} other brief file(s) not read (another name or in a subfolder): only brief.yaml "
                             f"at the top level of the folder is read")
            else:
                flags.append(f"brief.yaml not read: {n} brief file(s) with another name or in a subfolder (e.g. "
                             f"Brief.yaml, brief.yml); it must be named exactly brief.yaml at the top level of the "
                             f"folder, so every brief value is a default")
        else:
            flags.append(f"intake note on {n} file(s): {text}")
    return flags


def kept_on_volume(views: list[dict]) -> list[str]:
    """Files of a private project that the report names but never copies (paths relative to the project output)."""
    return sorted(v["plan_kept"] for v in views if v.get("plan_kept"))


def _attempt_text(a: Optional[dict]) -> str:
    if not a:
        return "-"
    bits = [f"a{a.get('k')}", f"s {a.get('strength')}", str(a.get("control") or "no control")]
    if a.get("scale") is not None:
        bits.append(f"x{a['scale']}")
    if a.get("size") and a.get("size") != "native":
        bits.append(str(a["size"]))
    if a.get("mode") and a.get("mode") != "plain":
        bits.append(str(a["mode"]))
    return " ".join(bits)


def _pref_text(p: Optional[dict]) -> str:
    if not isinstance(p, dict):
        return "-"
    word = "preferred" if p.get("preferred") else "not preferred"
    return f"{word} {p.get('votes')}/{p.get('answers', p.get('asked'))}"


def _verdict(vc: Optional[dict], image: str) -> str:
    if vc is None:
        return "not run"
    s = vc.get(image)
    if not s:
        return "-"
    if s.get("preference_only"):
        return "pref only"
    v = str(s.get("verdict"))
    return v + (f" ({s['mismatches']})" if s.get("mismatches") else "")


def _sources_text(ids: dict) -> str:
    short = {"from_documents": "D", "added_by_ai": "A", "rule": "R"}
    order = [k for k in short if k in ids] + sorted(k for k in ids if k not in short)
    return " ".join(f"{short.get(k, k)}{len(ids[k])}" for k in order) or "-"


def _ev_text(exp: Optional[dict]) -> str:
    if not isinstance(exp, dict) or exp.get("ev") is None:
        return "-"
    return f"{float(exp['ev']):+.2f}" + (" (limit)" if exp.get("at_limit") else "")


def _camera_text(cp: Optional[dict]) -> str:
    if not cp:
        return "-"
    text = cp["policy"] + (f" {cp['score_total']:.2f}" if cp.get("score_total") is not None else "")
    if (cp.get("score") or {}).get("blocked"):
        text += " blocked"
    return text


def _pull_text(wp: Optional[dict]) -> str:
    if not isinstance(wp, dict) or wp.get("ev") is None:
        return "-"
    return f"{float(wp['ev']):g}"


def gate_validation_lines(g: Optional[dict], polish_ok: bool, polish_ran: bool) -> list[str]:
    """The "Gate validation" section (§7.3, §7.4)."""
    lines = ["", "## Gate validation", ""]
    if g is None:
        if not polish_ok:
            lines.append("Not needed: brief polish: false (every view is the Cycles render).")
        elif polish_ran:
            lines.append("Not recorded (`gate/gate_validation.json` missing): this polish was not validated for "
                         "the project (Milestone 5 run).")
        else:
            lines.append("Not recorded: the gate calibration and validation did not run.")
        return lines
    lim = g.get("limits") or {}

    def rate(value, limit) -> str:
        if value is None:
            return "-"
        return f"{100.0 * float(value):.1f} %" + (f" (limit {100.0 * float(limit):.0f} %)" if limit is not None else "")

    rows = [["decision", g["decision"] + (f" (recorded {g['recorded_decision']})"
                                          if g.get("recorded_decision") != g["decision"] else "")],
            ["benign controls accepted", f"{rate(g.get('benign_accept'), lim.get('benign_accept_min'))}, "
                                         f"{g.get('n_benign') or 0} comparisons"],
            ["negative controls rejected", f"{rate(g.get('negative_reject'), lim.get('negative_reject_min'))}, "
                                           f"{g.get('n_negative') or 0} comparisons"],
            ["effect", g["effect"]]]
    lines += C.table(["item", "value"], rows)
    if g["reasons"]:
        lines += ["", "Reasons:", ""] + C.bullets(g["reasons"])
    return lines


def stage_table_lines(records: list[dict], earlier: Optional[list] = None, run_id: Optional[str] = None) -> list[str]:
    """The "Stages" section from ``run/*.json`` (status, seconds, note): this run's records, then the records
    of earlier runs (stages this run did not reach), each labelled ``earlier run <run_id>``."""
    lines = ["", "## Stages", ""]
    earlier = list(earlier or [])
    if not records and not earlier:
        lines.append("No stage records (`run/*.json`): the project was not run by `wenart.run`.")
        return lines
    if run_id:
        lines += [f"This run (`{run_id}`):", ""]
    lines += C.table(["stage", "status", "seconds", "note"],
                     [[r["stage"], r["status"], C.seconds_text(r.get("seconds")), r.get("note")] for r in records])
    lines += ["", "The report stage itself is recorded after this report."]
    if earlier:
        lines += ["", "Earlier runs: records of stages this run did not reach. They stay on the volume and are not "
                      "part of this run's state or of this report's status:", ""]
        lines += C.table(["stage", "status", "seconds", "note", "run"],
                         [[r["stage"], r["status"], C.seconds_text(r.get("seconds")), r.get("note"),
                           f"earlier run {r.get('run_id') or '(no run id)'}"] for r in earlier])
    return lines


def intake_lines(intake: Optional[dict]) -> list[str]:
    """The "Intake" section of a private project: counts and reasons only (file names stay on the volume)."""
    if not intake:
        return []
    t = intake.get("totals") or {}
    lines = ["", "## Intake (private upload)", ""]
    lines.append(f"Status {intake.get('status') or '-'}: {t.get('kept', 0)} files kept ({t.get('documents', 0)} "
                 f"documents, {t.get('style_photos', 0)} style photos), {t.get('skipped', 0)} skipped, "
                 f"{t.get('notes', 0)} with notes. File names are in `intake_manifest.json` on the volume.")
    if intake.get("reasons"):
        lines += ["", "Reasons:", ""] + C.bullets(intake["reasons"])
    if intake.get("skipped_by_reason"):
        lines += ["", "Skipped files by reason:", ""]
        lines += C.table(["reason", "files"], [[k, n] for k, n in intake["skipped_by_reason"].items()])
    if intake.get("notes_by_kind"):
        lines += ["", "Kept files with a note (the files are named in `intake_manifest.json` on the volume):", ""]
        lines += C.table(["note", "files"], [[k, n] for k, n in intake["notes_by_kind"].items()])
        lines += ["", "Open items from the intake:", ""] + C.bullets(intake_flags(intake))
    return lines


def report_markdown(manifest: dict) -> str:
    """``final_report.md`` from the final manifest (links only to files in ``final/``)."""
    s = manifest["summary"]
    views = manifest["views"]
    st = manifest["stages"]
    lines = [f"# Final report: {manifest['project']}", ""]
    if manifest["status"] == "not_rendered":
        lines.append(f"Status: **not_rendered**: {NO_RENDERS}. `renders/render_manifest.json` was not found, so "
                     f"this report has no view to show.")
        stopped = manifest.get("stopped_stages") or []
        if stopped:
            lines.append("")
            text = ("This run stopped the project before its renders: "
                    + "; ".join(f"{r['stage']} {r['status']}" + (f" ({r['note']})" if r.get("note") else "")
                                for r in stopped) + ".")
            if any(r["status"] == "incomplete" for r in stopped):
                text += " A project cut by the deadline (`incomplete`) is resumed with the same command."
            if any(r["status"] == "failed" for r in stopped):
                text += " A `failed` stage has its log in `run/logs/<stage>.log` on the volume."
            lines.append(text)
        lines.append("")
    reasons = ", ".join(f"{k} {n}" for k, n in s["cycles_by_reason"].items()) or "none"
    lines.append(f"{s['views']} views: {s['polished']} polished, {s['cycles']} Cycles ({reasons}). "
                 f"Stages: render {st['render']}, gate validation {st.get('gate_validation', 'not_run')}, "
                 f"polish {st['polish']}, vision check {st['check']} "
                 f"(calibration {st['check_calibration']}). A polished image is final only when the gate accepted "
                 f"it and the vision check checked it without finding a lost or added element (§5.5). Mismatches "
                 f"are listed with their evidence and never auto-fixed.")
    lines += ["", "## Summary", ""]
    exp = s["exposure"]
    sec = s["seconds"]
    ev_range = ("-" if exp["min"] is None
                else f"{exp['min']:+.2f} .. {exp['max']:+.2f} EV ({exp['at_limit']} at a limit)")
    rows = [
        ["views", s["views"]],
        ["polished", s["polished"]],
        ["Cycles", f"{s['cycles']} ({reasons})"],
        ["confirmed mismatches on the final image", f"{s['final_mismatches']} in {s['views_with_final_mismatch']} "
                                                    f"view(s)"],
        ["JSON cross-check findings (Cycles render)", s["crosscheck_findings"]],
        ["needs_review views", s["needs_review"]],
        ["unverified pieces in view (sum over views)", s["unverified_in_view"]],
        ["rooms mixing polished and Cycles", s["rooms_mixed"]],
        ["advisory", "yes" if manifest["advisory"] else "no"],
        ["advisory flags", len(manifest["advisory_flags"])],
        ["exposure", ev_range + (f", modes {', '.join(exp['modes'])}" if exp["modes"] else "")],
        ["window pull", "-" if not exp.get("window_pull", {}).get("views") else
         f"{exp['window_pull']['views']} view(s), {exp['window_pull']['min']:g} .. {exp['window_pull']['max']:g} EV"],
        ["camera policy", ", ".join(f"{k} {n}" for k, n in s["cameras"]["policies"].items()) or "-"],
        ["camera score (min / mean / max)", "-" if s["cameras"]["score_mean"] is None else
         f"{s['cameras']['score_min']:.2f} / {s['cameras']['score_mean']:.2f} / {s['cameras']['score_max']:.2f}"],
        ["rooms by number of views", ", ".join(f"{n} with {k}" for k, n in s["views_per_room"].items()) or "-"],
        ["gate validation", (manifest["gate_validation"] or {}).get("decision") or "not recorded"],
        ["seconds: build / render / metering",
         " / ".join(C.seconds_text(sec[k]) for k in ("build", "render", "meter"))],
        ["seconds: polish / gate / check", " / ".join(C.seconds_text(sec[k]) for k in ("polish", "gate", "check"))],
        ["brief polish", ("yes" if manifest["polish_allowed"] else "no")
         + (" (default, not in brief.yaml)" if "polish" in manifest.get("brief_assumed", []) else "")],
    ]
    lines += C.table(["item", "value"], rows)
    lines += ["", "## Advisory flags and open items", ""]
    lines += C.bullets(manifest["advisory_flags"])
    lines += gate_validation_lines(manifest["gate_validation"], manifest["polish_allowed"],
                                   manifest["stages"]["polish"] != "not_run")
    if manifest["contact_sheets"]:
        lines += ["", "## Contact sheets", ""]
        lines.append("Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.")
        for level, name in manifest["contact_sheets"].items():
            lines += ["", f"Level {level}: [{name}]({name})"]
    lines += ["", "## Views", ""]
    rows = []
    for v in views:
        files = []
        if v["preview"]:
            files.append(f"[preview]({v['preview']})")
        if v["plan"]:
            files.append(f"[plan]({v['plan']})")
        rows.append([v["camera"], v["room_id"], v["level_id"], v["final"], v["reason"], _attempt_text(v["attempt"]),
                     _short_gate(v["gate"]), _verdict(v["vision_check"], "cycles"),
                     _verdict(v["vision_check"], "polished"), _pref_text(v["preference"]), _ev_text(v["exposure"]),
                     _pull_text(v.get("window_pull")), _camera_text(v.get("camera_plan")),
                     _sources_text(v["ids_by_source"]), len(v["unverified"]), v["needs_review"],
                     " ".join(files) or "-"])
    lines += C.table(["view", "room", "level", "final", "reason", "polish attempt", "gate", "check Cycles",
                      "check polished", "preference", "EV", "pull EV", "camera", "ids D/A/R", "U", "review", "files"],
                     rows)
    lines.append("")
    lines.append("polish attempt: the polish candidate (used only when final is polished). pull EV: the window "
                 "pull of the render (window panes darkened by that many EV, §5). camera: policy (`search` = "
                 "ray-cast camera search, `m5` = the fixed rules) and score. ids: D from_documents, A added_by_ai, "
                 "R rule (elements in view). check: verdict (confirmed mismatches). U: unverified pieces in view.")
    lines += ["", "## Views per room", ""]
    room_rows = []
    for rid, r in manifest["rooms"].items():
        room_rows.append([rid, r.get("room_type"), r.get("level_id"), len(r["views"]), len(r["polished"]),
                          len(r["cycles"]), r["views"]])
    if room_rows:
        lines += C.table(["room", "type", "level", "views", "polished", "Cycles", "cameras"], room_rows)
        empty = [rid for rid, r in manifest["rooms"].items() if not r["views"] and rid != "-"]
        if empty:
            lines += ["", "Rooms without a rendered view: " + ", ".join(empty) + "."]
    else:
        lines.append("None.")
    details = [v for v in views if v["detail"] and v["final"] == "cycles" and v["reason"] not in ("brief",)]
    if details:
        lines += ["", "### Why Cycles", ""]
        lines += [f"- {v['camera']}: {v['reason']}: {v['detail']}" for v in details]
    lines += ["", "## Mismatches (never auto-fixed)", ""]
    rows = []
    for v in views:
        for it in v["mismatches"]:
            what = it["result"] if it["what"] != "crosscheck" else f"cross-check {it['result']}"
            extra = it.get("detail") or (f"box {[round(x) for x in it['box_px']]}" if it.get("box_px") else "")
            if it.get("expected") is not None:
                extra = f"expected {it['expected']}, passes {it.get('passes')}"
            counted = "yes" if it in confirmed_items([it]) else "info"
            rows.append([v["camera"], it["image"], what, it.get("id") or it.get("kind"), it.get("type"),
                         it.get("role"), it.get("source"), it.get("evidence"), counted,
                         "; ".join(x for x in [extra] + it.get("notes", []) if x)])
    if rows:
        lines += C.table(["view", "image", "result", "id", "type", "role", "source", "evidence", "counted",
                          "notes"], rows)
    else:
        lines.append("None." if manifest["stages"]["check"] != "not_run" or manifest["stages"]["expected"] == "run"
                     else "Not computed: the vision check and the expected lists did not run.")
    review = [v for v in views if v["needs_review"]]
    lines += ["", "## Needs review", ""]
    lines += C.bullets(f"{v['camera']}: " + ("; ".join((v["vision_check"] or {}).get("needs_review_reasons") or [])
                                             or "confirmed mismatch or cross-check finding on the Cycles render")
                       for v in review)
    b = manifest["building"]
    lines += ["", "## Building JSON: unverified items and conflicts", ""]
    lines.append(f"Status: {b['status'] or '-'}.")
    lines += ["", "Unverified items:", ""]
    lines += C.bullets(b["unverified"])
    unv_views = [(v["camera"], v["unverified"]) for v in views if v["unverified"]]
    if unv_views:
        lines += ["", "Unverified pieces in view:", ""]
        lines += [f"- {cam}: {', '.join(ids)}" for cam, ids in unv_views]
    lines += ["", "Conflicts:", ""]
    if b["conflicts"]:
        lines += C.table(["id", "kind", "elements", "description", "resolution"],
                         [[c.get("id"), c.get("kind"), c.get("element_ids"), c.get("description"), c.get("resolution")]
                          for c in b["conflicts"]])
    else:
        lines.append("None.")
    lines += ["", "## Rooms mixing polished and Cycles views", ""]
    mixed = [(rid, r) for rid, r in manifest["rooms"].items() if r["mixed"]]
    if mixed:
        reason_of = {v["camera"]: v["reason"] for v in views}
        lines += C.table(["room", "polished", "Cycles (reason)", "polish room rule"],
                         [[rid, r["polished"], [f"{c} ({reason_of.get(c)})" for c in r["cycles"]],
                           (r["polish_rule"] + (f" (rung {r['polish_rung']})" if r["polish_rung"] is not None else ""))
                           if r["polish_rule"] else "-"]
                          for rid, r in mixed])
    else:
        lines.append("None.")
    down = [(rid, r) for rid, r in manifest["rooms"].items() if r.get("polish_rule") == "downgraded"]
    if down:
        lines += ["", "Polish room rule (wall colour within ΔE 5 per room) downgraded: "
                  + ", ".join(f"{rid} (rung {r['polish_rung']})" for rid, r in down) + "."]
    lines += ["", "## Models and licences", ""]
    if manifest["models"]:
        lines += C.table(["role", "model", "revision", "licence", "from"],
                         [[m["role"], m["repo"], m["revision"], m["licence"], m["source"]] for m in manifest["models"]])
    else:
        lines.append("No AI model ran for this report (polish and vision check not run).")
    assets = manifest.get("assets") or {}
    if assets.get("textures") or assets.get("models"):
        lines += ["", "Assets: textures " + (", ".join(f"{k} x {n}" for k, n in assets["textures"].items()) or "-")
                  + "; furniture/decor models " + (", ".join(f"{k} x {n}" for k, n in assets["models"].items()) or "-")
                  + " (parametric meshes need no licence)."]
    lines += stage_table_lines(manifest["run_stages"], manifest.get("earlier_run_stages"), manifest.get("run_id"))
    if manifest["private"]:
        lines += intake_lines(manifest.get("intake"))
        lines += ["", "## Kept on the volume (private project)", ""]
        lines.append("Plan crops and debug images of a private project are never copied into `final/`. They "
                     "stay in the project output on the volume (paths relative to it; see docs/intake.md):")
        lines += [""] + C.bullets(manifest.get("kept_on_volume") or [], empty="No plan crop was made.")
    lines += ["", "## Warnings", ""]
    lines += C.bullets(manifest["warnings"])
    return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------
# Needs-review report (§7.4)
# --------------------------------------------------------------------------

REVIEW_PREFIX = "needs review: "


@dataclass
class ReviewInputs:
    """What the needs-review report reads (see ``review_inputs``)."""
    project_out: Path
    out_dir: Path
    project: str
    private: bool
    reasons: list
    building: Optional[dict]
    report_md: Optional[str]
    intake: Optional[dict]
    records: list
    warnings: list
    earlier: list = field(default_factory=list)
    run_id: Optional[str] = None


def review_inputs(project_out, out_dir=None, private: bool = False) -> Optional[ReviewInputs]:
    """The inputs of the needs-review report, or None when the project does not need review.

    Sources, in order: ``intake_manifest.json`` (status ``needs_review``: its reasons; the pipeline did not
    run, so an older ``building.json`` is ignored), ``building.json`` (status ``needs_review``: its
    ``needs review: ...`` warnings, plus a failed schema validation), then this run's stage records with status
    ``needs_review`` of stages no manifest covers (their note). Records of earlier runs (``split_runs``) are
    only listed.
    """
    out = Path(project_out).resolve()
    w: list = []
    records, earlier, run_id = split_runs(load_stage_records(out, w))
    intake = C.read_json(out / "intake_manifest.json", w)
    building = C.read_json(out / "building.json", w)
    reasons: list[str] = []
    covered = set()
    if isinstance(intake, dict):
        covered.add("intake")
        if intake.get("status") == "needs_review":
            reasons += [f"intake: {r}" for r in intake.get("reasons") or []] or ["intake: needs review"]
            if building is not None:
                w.append("building.json is from an earlier run (the pipeline did not run after the intake); "
                         "ignored")
            building = None
            covered.update(r["stage"] for r in records)
    if isinstance(building, dict):
        covered.add("pipeline")
        if building.get("status") == "needs_review":
            bw = [x for x in building.get("warnings") or [] if isinstance(x, str)]
            found = [x[len(REVIEW_PREFIX):] for x in bw if x.startswith(REVIEW_PREFIX)]
            if any(x.startswith("schema: ") for x in bw):
                found.append("building JSON failed schema validation")
            reasons += found or ["building.json says needs_review (no reason recorded)"]
    for r in records:
        if r["status"] == "needs_review" and r["stage"] not in covered:
            reasons.append(f"{r['stage']}: {r.get('note') or 'needs review'}")
    if not reasons:
        return None
    report_md = None
    if (out / "report.md").is_file() and building is not None:
        report_md = (out / "report.md").read_text(encoding="utf-8", errors="replace")
    project = (building or {}).get("project")
    name = project.get("id") if isinstance(project, dict) else None
    return ReviewInputs(project_out=out, out_dir=Path(out_dir).resolve() if out_dir else out / FINAL_DIR,
                        project=str(name or out.name), private=is_private(out, private), reasons=reasons,
                        building=building, report_md=report_md, intake=intake if isinstance(intake, dict) else None,
                        records=records, warnings=w, earlier=earlier, run_id=run_id)


def review_hints(reasons: list[str]) -> list[str]:
    """What the user can do, from the reason texts (``NEEDS_REVIEW_HINTS``); no hint is invented."""
    hints: list[str] = []
    for reason in reasons:
        low = reason.lower()
        for key, hint in NEEDS_REVIEW_HINTS:
            if key in low and hint not in hints:
                hints.append(hint)
    return hints


def document_rows(building: Optional[dict]) -> list[dict]:
    """One row per document page of ``building.json`` (the page table of the pipeline's report.md)."""
    rows = []
    for doc in (building or {}).get("documents") or []:
        for page in doc.get("pages") or []:
            scale = page.get("scale")
            scale_text = (f"{scale['metres_per_unit']:.6g} m/unit ({scale.get('method')})"
                          if isinstance(scale, dict) and isinstance(scale.get("metres_per_unit"), (int, float))
                          else None)
            rows.append({"file": doc.get("file"), "page": page.get("page"), "format": doc.get("format"),
                         "class": page.get("class"), "kind": page.get("kind"), "level_id": page.get("level_id"),
                         "scale": scale_text, "confidence": page.get("confidence"),
                         "skip_reason": page.get("skip_reason"), "debug_image": page.get("debug_image"),
                         "debug_preview": None})
    return rows


def report_md_documents(text: Optional[str]) -> list[str]:
    """The "## Documents" table of the pipeline's report.md (used when building.json has no documents)."""
    if not text:
        return []
    lines, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            if inside:
                break
            inside = line.strip() == "## Documents"
            continue
        if inside and line.startswith("|"):
            lines.append(line)
    return lines


def write_review_images(ri: ReviewInputs, docs: list[dict]) -> list[dict]:
    """Debug images of the pages as JPEG <= 300 KB under ``final/debug/`` (public projects); a private
    project's debug images are only named (paths relative to the project output)."""
    out = []
    seen = set()
    for row in docs:
        rel_src = row.get("debug_image")
        if not rel_src or rel_src in seen:
            continue
        seen.add(rel_src)
        src = ri.project_out / rel_src
        entry = {"source": rel_src, "preview": None, "bytes": None}
        if ri.private:
            entry["kept_on_volume"] = True
        elif not src.is_file():
            ri.warnings.append(f"debug image {rel_src} not found")
        else:
            rgb = _load_rgb(src)
            if rgb is None:
                ri.warnings.append(f"debug image {rel_src} unreadable")
            else:
                name = f"{DEBUG_DIR}/{Path(rel_src).stem}.jpg"
                info = C.save_jpeg_under(rgb, ri.out_dir / name)
                entry.update(preview=name, bytes=info["bytes"])
        out.append(entry)
        for r in docs:
            if r.get("debug_image") == rel_src:
                r["debug_preview"] = entry["preview"]
    written = {e["preview"] for e in out if e["preview"]}
    for pattern in (f"{DEBUG_DIR}/*.jpg", "*_final_preview.jpg", "*_plan.jpg", "contact_*.jpg"):
        for f in sorted(ri.out_dir.glob(pattern)):
            rel = f.relative_to(ri.out_dir).as_posix()
            if rel not in written:
                ri.warnings.append(f"final/{rel} is from an earlier run (not part of this report)")
    return out


def building_summary(building: Optional[dict]) -> Optional[dict]:
    if not isinstance(building, dict):
        return None
    counts = {key: len(building.get(key) or []) for key in ("levels", "walls", "openings", "rooms", "furniture")}
    return {"status": building.get("status"), **counts, "conflicts": list(building.get("conflicts") or []),
            "unverified": list(building.get("unverified") or []),
            "warnings": [w for w in building.get("warnings") or [] if isinstance(w, str)]}


def build_review_manifest(ri: ReviewInputs, docs: list[dict], images: list[dict]) -> dict:
    stale = ri.project_out / "renders" / "render_manifest.json"
    if stale.is_file():
        ri.warnings.append("renders/ holds an earlier run's renders: ignored (the project needs review)")
    intake = intake_summary(ri.intake)
    return {
        "schema_version": "0.1",
        "kind": "final",
        "project": ri.project,
        "status": "needs_review",
        "private": ri.private,
        "reasons": list(ri.reasons),
        "hints": review_hints(ri.reasons),
        "documents": docs,
        "debug_images": images,
        "building": building_summary(ri.building),
        "intake": intake,
        "run_id": ri.run_id,
        "run_stages": list(ri.records),
        "earlier_run_stages": list(ri.earlier),
        "summary": {"views": 0, "polished": 0, "cycles": 0, "cycles_by_reason": {}, "needs_review": 0},
        "views": [],
        "advisory_flags": [f"needs review: {r}" for r in ri.reasons] + intake_flags(intake),
        "warnings": list(ri.warnings),
    }


def review_markdown(manifest: dict, report_md_table: list[str]) -> str:
    """``final_report.md`` of a needs-review project (links only to files in ``final/``)."""
    lines = [f"# Final report: {manifest['project']} (needs review)", ""]
    lines.append("Status: **needs_review**. The project stopped before the 3D stages: nothing was built, rendered "
                 "or polished in this run, and nothing was guessed or filled in. Every reason is listed below; after "
                 "fixing them, run the project again.")
    lines += ["", "## Reasons", ""] + C.bullets(manifest["reasons"])
    if manifest["hints"]:
        lines += ["", "## What to do", ""] + C.bullets(manifest["hints"])
    lines += ["", "## Documents and pages", ""]
    docs = manifest["documents"]
    if docs:
        rows = []
        for d in docs:
            if d["debug_preview"]:
                debug = f"[{d['debug_preview']}]({d['debug_preview']})"
            elif d["debug_image"] and manifest["private"]:
                debug = f"{d['debug_image']} (on the volume, not copied)"
            else:
                debug = d["debug_image"] or "-"
            rows.append([d["file"], d["page"], d["class"], d["kind"], d["level_id"], d["scale"],
                         C.cell(d["confidence"]), d["skip_reason"], debug])
        lines += C.table(["file", "page", "class", "kind", "level", "scale", "confidence", "skip reason",
                          "debug image"], rows)
    elif report_md_table:
        lines += ["From the pipeline's report.md:", ""] + report_md_table
    else:
        lines.append("No document page was classified (the pipeline did not run or found no document).")
    if manifest["private"] and manifest["debug_images"]:
        lines += ["", "Debug images of a private project stay on the volume (paths relative to the project "
                      "output; see docs/intake.md)."]
    b = manifest["building"]
    if b is not None:
        lines += ["", "## Building JSON", ""]
        lines += C.table(["status", "levels", "walls", "openings", "rooms", "furniture", "conflicts", "unverified"],
                         [[b["status"], b["levels"], b["walls"], b["openings"], b["rooms"], b["furniture"],
                           len(b["conflicts"]), len(b["unverified"])]])
        if b["conflicts"]:
            lines += ["", "Conflicts:", ""]
            lines += C.table(["id", "kind", "elements", "description", "resolution"],
                             [[c.get("id"), c.get("kind"), c.get("element_ids"), c.get("description"),
                               c.get("resolution")] for c in b["conflicts"]])
        if b["unverified"]:
            lines += ["", "Unverified items:", ""] + C.bullets(b["unverified"])
        lines += ["", "Pipeline warnings:", ""] + C.bullets(b["warnings"])
    if manifest["private"]:
        lines += intake_lines(manifest.get("intake"))
    lines += stage_table_lines(manifest["run_stages"], manifest.get("earlier_run_stages"), manifest.get("run_id"))
    lines += ["", "## Warnings", ""] + C.bullets(manifest["warnings"])
    return "\n".join(lines) + "\n"


def write_needs_review(ri: ReviewInputs) -> dict:
    """Write the needs-review ``final_report.md``, then ``final_manifest.json`` (last); returns the manifest."""
    ri.out_dir.mkdir(parents=True, exist_ok=True)
    docs = document_rows(ri.building)
    images = write_review_images(ri, docs)
    manifest = build_review_manifest(ri, docs, images)
    errors = validate_final_manifest(manifest)
    if errors:
        manifest["warnings"].extend(f"final manifest schema: {e}" for e in errors[:20])
    table = [] if docs else report_md_documents(ri.report_md)
    (ri.out_dir / REPORT_NAME).write_text(review_markdown(manifest, table), encoding="utf-8")
    C.write_json(ri.out_dir / MANIFEST_NAME, manifest)
    return manifest


def write_final(project_out, out_dir=None, private: bool = False) -> dict:
    """Build and write everything of ``final/`` (see module docstring); returns the manifest.

    ``private``: treat the project as private even when nothing else says so (``is_private``).
    ``final_manifest.json`` is written last: a manifest newer than the call means the report finished (the
    orchestrator tells a ``not_rendered`` exit 1 from a crash this way).
    """
    ri = review_inputs(project_out, out_dir, private)
    if ri is not None:
        return write_needs_review(ri)
    inp = load_inputs(project_out, out_dir, private)
    views = build_views(inp)
    sheets = write_images(inp, views)
    manifest = build_manifest(inp, views, sheets)
    errors = validate_final_manifest(manifest)
    if errors:
        manifest["warnings"].extend(f"final manifest schema: {e}" for e in errors[:20])
    inp.out_dir.mkdir(parents=True, exist_ok=True)
    (inp.out_dir / REPORT_NAME).write_text(report_markdown(manifest), encoding="utf-8")
    C.write_json(inp.out_dir / MANIFEST_NAME, manifest)
    return manifest
