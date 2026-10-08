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

Milestone 7 (docs/milestone7.md §9.4), all read from the building JSON, the
scene manifest and the check manifest (nothing is recomputed):

- ``units``: the project's unit system (``project.unit_system``) and every
  document's; lengths of an imperial project are written in feet and inches
  with metres in brackets (``length_text``), metric ones in metres;
- side-by-side sheets ``contact_sbs_<room>.jpg`` (<= 300 KB; named like the
  contact sheets so the results copy takes them) for every project with the
  polish on (brief ``polish`` true and a polish manifest of this run): per view
  of the room the Cycles render on the left and the polish candidate (the
  chosen attempt, else the last attempt the gate saw) on the right, labelled
  with the gate decision, both check verdicts, the detector and the final
  decision (``side_by_side``);
- ``recognition``: the AI-typed furniture pieces with both passes' answers
  (``type_candidates``), the composites the core could not split ("possible
  group of N pieces"), the raster pages and, per room of a raster page, how
  its label was accepted (two passes agree, one pass equal to Tesseract,
  Tesseract only or not accepted; from the evidence the pipeline recorded);
- ``site`` (plot walls, exterior areas, site decor; recorded, not built),
  ``separators`` (virtual openings), ``assumed`` (brief defaults, assumed
  level titles, ceiling heights, opening heights and sills, stair direction,
  turn and void, the scene manifest's assumed values grouped);
- ``attribution``: the credit line of every CC BY / CC0 Objaverse model of
  the building (``furniture[].asset.attribution``) and the ODC-By 1.0 notice;
- ``detector``: the OWLv2 added-object detector of the check manifest (status,
  thresholds, model, views where it confirmed an added object:
  ``added_by_polish``); ``CHECK_VIEW_KEYS`` knows its per-view keys;
- ``NEEDS_REVIEW_HINTS`` for DWG (LibreDWG 0.14), raster pages (no page
  quadrilateral, no dimension readable, photo aspect unknown), text drawn as
  geometry, untitled plan pages and an uncorroborated scale.

Milestone 10 (docs/milestone10.md §3.3 item 6; the sections are built by ``wenart/report/m10.py``):

- a project that stopped at the ``sheets`` stage (``sheets.json`` lists ``needs_review[]``, no ``building.json``,
  no ``report.md``) gets the needs-review report too: the sheets reasons, a Sheets section (regions, strays, unit
  check, conflicts, debug images as JPEG under ``final/debug/``) and ``sheets_report.md`` copied next to it (a
  private project's stays on the volume);
- a rendered project gets a ``Sheets`` section (``sheets.json``), a ``Building`` section (levels, variants, every
  height drawn or assumed, slabs, roof, facade, site, levels left out), the Feature 1 section per room (drawn
  type and size -> new type and size, added pieces, refused proposals; ``completion.json``) with the drawn-piece
  check against the source plan, an ``Exterior views`` section (outside looks, views, dropped cameras, the
  elevation check, roof and advisory facade counts, the exterior gate) and a ``Variants`` section that reads
  ``variants/<id>/final/final_manifest.json`` of each alternative; every assumed value is listed under
  ``Assumed values``;
- an exterior view (``view_kind: exterior``, a camera without a room) is held to the exterior gate decision
  (``wenart.gate.calibrate.exterior_polish``, next to the project's own): one that does not allow the polish
  makes the view Cycles with reason ``gate_validation`` and leaves the rooms alone;
- contact sheets: ``contact_<level>.jpg`` for the rooms as before, ``contact_exterior_<variant>.jpg`` for the
  exterior views of a variant, ``contact_variant_<id>.jpg`` for the interior views of an alternative (tiles from
  its own ``final/``); an alternative whose outside is unchanged lists the base exterior views instead;
- a drawn piece the AI changed (``modified_by_ai``) carries the note ``modified_by_ai (drawn <type>)`` next to a
  mismatch, as an added piece carries ``added_by_ai``: a render issue, never a conflict between documents;
- an alternative's sub-output ``outputs/<p>/variants/<id>`` reads the base project's gate calibration, sheets and
  ``completion.json`` and is private when its project is.
"""
from __future__ import annotations

import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from wenart.report import common as C
from wenart.report import m10 as M

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
# (lower-case text in a reason, hint): every hint whose text occurs in a reason is shown once; no hint is invented.
DWG_HINT = "DWG is read with LibreDWG 0.14 (beta); if it fails, export DXF"        # = wenart.intake.DWG_NOTE (§5.1)
NEEDS_REVIEW_HINTS = (
    ("not uploaded", "upload the project folder (docs/intake.md, step 5) and run again"),
    ("collision", "rename one of the files that map to the same name (see intake_manifest.json)"),
    ("cap", "split or shrink the file(s) over the size limit"),
    ("dwg", DWG_HINT),
    ("no vector floor plan", "add a floor plan the pipeline can read: DXF/DWG, a vector PDF, or a sharp scan or photo "
                             "with readable dimension texts"),
    ("no scale", "add a scale (ÖLÇEK 1/50, 1/100 or DXF $INSUNITS) to the plan"),
    ("scale not corroborated", "check the plan's dimension texts and room-size labels (two dimensions need two room "
                               "sizes that agree within 5 %), or add more dimensions or a scale note"),
    ("level title", "add the level title (e.g. ZEMİN KAT PLANI) to the floor plan"),
    ("untitled plan pages", "add a level title to every plan page (e.g. GROUND FLOOR PLAN, FIRST FLOOR PLAN)"),
    ("closed loop", "close the outer walls of the level in the drawing"),
    ("do not close", "close the walls around every labelled room in the drawing"),
    ("no document", "upload at least one plan (.dxf, .pdf or an image)"),
    # Raster pages (docs/milestone7.md §4, §9.4).
    ("no page quadrilateral", "photograph the whole sheet with its four corners visible (flat, on a darker "
                              "background), or upload a scan or the CAD file"),
    ("no dimension readable", "a scan or photo needs dimension texts that OCR can read: upload a sharper scan "
                              "(300 dpi), or the CAD file or a vector PDF"),
    ("photo aspect unknown", "photograph the sheet straight on with all four corners in view (its sheet size could "
                             "not be told), or upload a scan or the CAD file"),
    ("text drawn as geometry", "export the PDF with real text (or upload the DWG/DXF): the texts of this page are "
                               "drawn as lines"),
    # The sheets stage (docs/milestone10.md §3.1).
    ("no readable plan region", "add a floor plan the sheets stage can read: a DXF/DWG or vector PDF with closed "
                                "walls and room labels, or a sharp scan"),
    ("missing scale", "set the drawing unit of the CAD file (or add a scale note such as ÖLÇEK 1/50 to the plan)"),
    ("unit check", "check the drawing unit of the CAD file ($INSUNITS) against the room-area labels, the level "
                   "marks and the door widths"),
)
MISMATCH_RESULTS = ("missing", "changed", "missing_or_changed")
NON_DECOR_CLASSES = ("door", "window", "furniture", "fixture")
CROSSCHECK_KEYS = ("in_json_not_rendered", "rendered_not_in_json", "misplaced", "roof_not_rendered")
# Keys of a check-manifest camera entry that are not image kinds (§5.7; M7 §8.1: the detector's per-view record and
# its added_by_polish flag).
CHECK_VIEW_KEYS = {"room_id", "json_crosscheck", "polished_rejected", "polished_reason", "polished_reasons",
                   "needs_review", "needs_review_reasons", "preference", "added_by_polish", "detector",
                   # Milestone 10: the exterior view's roof check, the advisory facade counts and the view kind
                   "facades", "exterior", "view_kind"}
ADDED_BY_AI_NOTE = "added_by_ai: render/polish issue, not a document conflict"
# Milestone 10, Feature 1: a drawn piece the AI changed (= wenart.vision_check.combine.MODIFIED_NOTE).
MODIFIED_NOTE = "modified_by_ai (drawn {drawn}): render/polish issue, not a document conflict"
# Milestone 7 (§9.4).
SBS_PREFIX = "contact_sbs_"          # side-by-side sheets (the copy rule takes contact_*.jpg up to 300 KB)
SBS_LABEL_HEIGHT = 44                # two label lines under each tile
COMPOSITE_NOTE = "possible group of"  # wenart.ingest.generic.symbols: a cluster that could not be split
RASTER_KINDS = ("scan", "photo")
# The room-label evidence confidences of wenart.recognition.room_labels (AGREE_CONFIDENCE, TESSERACT_CONFIDENCE),
# which record how a raster room label was accepted (§3.4). Mirrored: the report imports no recognition code
# (tests/test_report.py pins them equal).
LABEL_TWO_PASS_CONFIDENCE = 0.85
LABEL_TESSERACT_CONFIDENCE = 0.8
LABEL_PATHS = {"two_pass": "two passes agree", "tesseract": "one pass equals the Tesseract text",
               "tesseract_only": "Tesseract only (not confirmed by the passes)",
               "not_accepted": "not accepted (the passes disagree)", "none": "no label read"}

NUM = {"type": ["number", "null"]}
STR = {"type": ["string", "null"]}
FINAL_VIEW = {
    "type": "object",
    "required": ["camera", "room_id", "level_id", "final", "reason", "image", "preview", "plan", "attempt",
                 "gate", "vision_check", "json_crosscheck", "preference", "exposure", "ids_by_source",
                 "unverified", "mismatches", "needs_review"],
    "properties": {
        "camera": {"type": "string"},
        "view_kind": {"enum": ["interior", "exterior"]},
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
        # Milestone 7 (§9.4)
        "units": {"type": ["object", "null"], "properties": {"system": {"enum": ["metric", "imperial"]}}},
        "side_by_side": {"type": "object", "required": ["sheets"],
                         "properties": {"sheets": {"type": "object", "additionalProperties": {"type": "string"}}}},
        "recognition": {"type": ["object", "null"]},
        "site": {"type": ["object", "null"]},
        "separators": {"type": "array"},
        "assumed": {"type": ["object", "null"]},
        "attribution": {"type": ["object", "null"],
                        "properties": {"credits": {"type": "array", "items": {"type": "object",
                                                                              "required": ["asset_id", "credit"]}}}},
        "detector": {"type": ["object", "null"]},
        # Milestone 9 (docs/milestone9.md §4, user request of 4 Oct 2026)
        "decor_ai": {"type": ["object", "null"]},
        "files_3d": {"type": ["object", "null"]},
        # Milestone 10 (docs/milestone10.md §3.3 item 6; wenart/report/m10.py)
        "variant": {"type": "string"},
        "sheets": {"type": ["object", "null"]},
        "building_detail": {"type": ["object", "null"]},
        "completion": {"type": ["object", "null"]},
        "drawn_check": {"type": ["object", "null"]},
        "exterior": {"type": ["object", "null"]},
        "exterior_sheets": {"type": "object", "additionalProperties": {"type": "string"}},
        "variants": {"type": ["object", "null"]},
        "variant_sheets": {"type": "object", "additionalProperties": {"type": "object"}},
        "base_exterior_views": {"type": "array"},
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
    side_by_side: dict = field(default_factory=dict)     # room id -> side-by-side sheet (M7 §9.4)
    side_by_side_note: Optional[str] = None              # why there is none
    style: Optional[dict] = None                         # style.json of the style stage (assumed default style)
    # Milestone 10
    sheets: Optional[dict] = None                        # sheets.json (the project's, for a variant sub-output the base's)
    completion: Optional[dict] = None                    # completion.json of the layout stage (Feature 1)
    exterior_gate: Optional[dict] = None                 # the exterior polish decision (gate.calibrate.exterior_polish)
    variant: str = "base"                                # the variant of this output (outputs/<p>/variants/<id>: <id>)
    root: Optional[Path] = None                          # the project output (= project_out; a variant's: its base)
    variant_manifests: dict = field(default_factory=dict)    # variant id -> its final/final_manifest.json
    base_manifest: Optional[dict] = None                 # a variant sub-output: the base project's final manifest
    exterior_sheets: dict = field(default_factory=dict)  # variant -> contact_exterior_<variant>.jpg (write_images)
    variant_sheets: dict = field(default_factory=dict)   # variant id -> {"interior": name, "exterior": name}
    sheets_block: Optional[dict] = None                  # the Sheets block of the report (m10.sheets_block)

    @property
    def gate_dir(self) -> Path:
        """``gate/`` of this output, else of its base project (an alternative reuses the base calibration)."""
        own = self.project_out / "gate"
        if (own / "gate_calibration.json").is_file() or (own / "gate_validation.json").is_file() or self.root is None:
            return own
        return self.root / "gate"

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


def variant_root(project_out: Path) -> tuple[Path, str]:
    """``(project output, variant id)`` of an output folder: an alternative's sub-output
    ``outputs/<p>/variants/<id>`` is ``(outputs/<p>, <id>)``, any other folder ``(itself, "base")``
    (docs/milestone10.md §1.6b row 9)."""
    out = Path(project_out).resolve()
    if out.parent.name == "variants" and out.parent.parent != out:
        return out.parent.parent, out.name
    return out, "base"


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
    if bool(ALIAS_RE.match(out.name)) or out.name in RESERVED_ALIASES:
        return True
    # Milestone 10: an alternative's sub-output ``outputs/<p>/variants/<id>`` is as private as its project.
    if out.parent.name == "variants" and out.parent.parent != out:
        return is_private(out.parent.parent)
    return False


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
    style_path = out / "style.json"
    if style_path.is_file():
        inp.style = C.read_json(style_path, w)
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
    inp.root, inp.variant = variant_root(out)
    inp.gate_calibration = C.read_json(inp.gate_dir / "gate_calibration.json", w)
    inp.gate_validation = C.read_json(inp.gate_dir / "gate_validation.json", w)
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
    load_m10_inputs(inp)
    return inp


def load_m10_inputs(inp: Inputs) -> None:
    """The Milestone 10 inputs: ``sheets.json``, ``completion.json``, the exterior polish decision and the final
    manifests of the variants (each may be missing)."""
    w = inp.warnings
    root = inp.root or inp.project_out
    sheets = C.read_json(root / "sheets.json", w)
    inp.sheets = sheets if isinstance(sheets, dict) and sheets.get("kind") in (None, "sheets") else None
    folders = [inp.building_path.parent] if inp.building_path else []
    for folder in folders + [inp.project_out, root]:
        completion = C.read_json(folder / "completion.json") if (folder / "completion.json").is_file() else None
        if isinstance(completion, dict):
            inp.completion = completion
            break
    if any(isinstance(c, dict) and c.get("kind") == "exterior" for c in (inp.scene or {}).get("cameras") or []):
        try:
            from wenart.gate.calibrate import exterior_polish
            inp.exterior_gate = exterior_polish(inp.project_out)
        except Exception as exc:  # noqa: BLE001 - an unreadable decision never allows the exterior polish
            inp.exterior_gate = {"decision": "not_validated", "polish_allowed": False,
                                 "reasons": [f"the exterior validation could not be read ({type(exc).__name__}: {exc})"]}
            w.append(f"exterior gate decision not readable ({type(exc).__name__}: {exc}); exterior views stay Cycles")
    if inp.variant == "base":
        for v in (inp.building or {}).get("variants") or []:
            vid = v.get("id") if isinstance(v, dict) else None
            if vid and vid != "base":
                m = C.read_json(root / "variants" / vid / FINAL_DIR / MANIFEST_NAME)
                if isinstance(m, dict) and m.get("kind") == "final":
                    inp.variant_manifests[vid] = m
    else:
        base = C.read_json(root / FINAL_DIR / MANIFEST_NAME)
        inp.base_manifest = base if isinstance(base, dict) and base.get("kind") == "final" else None


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
        if canonical_sha256(inp.gate_dir / "gate_calibration.json") != sha:
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


def view_kind_of(inp: Inputs, camera: str, cview: Optional[dict] = None) -> str:
    """``interior`` or ``exterior``: the scene manifest's camera ``kind``, else the check manifest's ``view_kind``,
    else a camera named ``ext_<n>`` that has no room (Milestone 10)."""
    for kind in ((inp.cameras.get(camera) or {}).get("kind"), (cview or {}).get("view_kind")):
        if kind in ("interior", "exterior"):
            return kind
    return "exterior" if camera.startswith("ext_") and not room_of(inp, camera) else "interior"


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
                "status": el.get("status"), "evidence": text, "modified_by_ai": bool(el.get("modified_by_ai")),
                "drawn_type": el.get("drawn_type"), "completes_room": bool(el.get("completes_room"))}
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
           gate_decision: Optional[str] = None, exterior_gate: Optional[dict] = None) -> dict:
    """``{"final", "reason", "detail", "candidate"}`` of one view (see the module docstring; pure but for file checks).

    ``pview``: the view's polish-manifest entry; ``cview``: its
    check-manifest camera entry; ``polish_dir``: where the attempt PNGs are
    (None skips the file check); ``source_sha256``: the current render PNG's
    hash (None skips the staleness check); ``gate_decision``: the project's
    effective gate validation decision (None = not recorded, M5 outputs);
    ``exterior_gate``: for an exterior view (Milestone 10) the exterior polish decision
    (``wenart.gate.calibrate.exterior_polish``); one that does not allow the polish keeps the view Cycles
    (``gate_validation``), whatever the rooms' decision is.
    """
    if not allowed:
        return _cycles("brief", "brief.yaml polish: false")
    if gate_decision in NO_POLISH_DECISIONS:
        return _cycles("gate_validation", f"gate validation {gate_decision}: no polish for this project")
    if exterior_gate is not None and not exterior_gate.get("polish_allowed"):
        why = "; ".join(str(r) for r in (exterior_gate.get("reasons") or [])[:2])
        return _cycles("gate_validation", f"exterior gate validation {exterior_gate.get('decision')}: the exterior "
                       f"views stay the Cycles render" + (f" ({why})" if why else ""))
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
        view_kind = view_kind_of(inp, cam, cview)
        dec = decide(pview, cview, polish_ran=inp.polish is not None, check_ran=inp.check is not None,
                     allowed=allowed, polish_dir=inp.polish_dir, source_sha256=src_sha,
                     gate_decision=(inp.gate or {}).get("decision"),
                     exterior_gate=inp.exterior_gate if view_kind == "exterior" else None)
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
            elif info.get("modified_by_ai") and it["what"] in ("element", "crosscheck") \
                    and not any(str(n).startswith("modified_by_ai") for n in it["notes"]):
                it["notes"].append(MODIFIED_NOTE.format(drawn=info.get("drawn_type") or "?"))
            if info.get("modified_by_ai") or info.get("completes_room"):
                it["modified_by_ai"] = bool(info.get("modified_by_ai"))
                it["completes_room"] = bool(info.get("completes_room"))
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
            if view_kind == "exterior":
                # Milestone 10: the roof check and the advisory facade counts of an exterior view.
                vc["exterior"] = cview.get("exterior")
                vc["facades"] = cview.get("facades")
        needs_review = bool((cview or {}).get("needs_review")) or bool(confirmed_items(
            [i for i in items if i["image"] == "cycles"]))
        camera = inp.cameras.get(cam) or {}
        out.append({
            "camera": cam,
            "view_kind": view_kind,
            "variant": camera.get("variant") if view_kind == "exterior" else None,
            "exterior_view": camera.get("view") if view_kind == "exterior" else None,
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
            "added_by_polish": bool((cview or {}).get("added_by_polish")),
            "detector": detector_view((cview or {}).get("detector")),
        })
    return out


def detector_view(d: Optional[dict]) -> Optional[dict]:
    """``{status, computed, added, unmatched, boxes}`` of a check-manifest camera's detector record (M7 §8.1)."""
    if not isinstance(d, dict):
        return None
    added = [c for c in d.get("added") or [] if isinstance(c, dict)]
    return {"status": d.get("status"), "computed": bool(d.get("computed")), "added": len(added),
            "unmatched": len(d.get("unmatched") or []),
            "boxes": [{"class": c.get("class"), "group": c.get("group"), "box_px": c.get("box_px"),
                       "score": c.get("score"), "confirmed_by": list(c.get("confirmed_by") or [])} for c in added]}


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


def _polish_tile_source(inp: Inputs, view: dict) -> tuple[Optional[Path], Optional[dict]]:
    """The polished image of a side-by-side row and its attempt record: the view's candidate (the chosen attempt,
    also when the check rejected it), else the last attempt the gate saw (a view no attempt passed); the PNG, else
    its preview JPEG (results copies). ``(None, None)`` when the polish made no image for the view."""
    pv = inp.polish_views.get(view["camera"]) or {}
    attempts = [a for a in pv.get("attempts") or [] if isinstance(a, dict) and a.get("png")]
    k = (view.get("attempt") or {}).get("k")
    rec = next((a for a in attempts if a.get("k") == k), None) if k is not None else None
    if rec is None and attempts:
        rec = attempts[-1]
    if rec is None:
        return None, None
    candidates = [inp.polish_dir / rec["png"]]
    if rec.get("preview"):
        candidates.append(inp.polish_dir / rec["preview"])
    candidates.append(inp.polish_dir / f"{view['camera']}_a{rec.get('k')}_preview.jpg")
    return next((c for c in candidates if c.is_file()), None), rec


def _cycles_tile_source(inp: Inputs, camera: str) -> Optional[Path]:
    entry = inp.entries.get(camera) or {}
    candidates = [inp.render_dir / entry[k] for k in ("png", "preview") if entry.get(k)]
    return next((c for c in candidates if c.is_file()), None)


def side_by_side_labels(view: dict, rec: Optional[dict]) -> tuple[list[str], list[str]]:
    """The two label lines under the Cycles tile and under the polished tile of one view."""
    vc = view.get("vision_check")
    final = "polished" if view["final"] == "polished" else f"Cycles ({view['reason']})"
    left = [f"{view['camera']}  Cycles", f"check {_verdict(vc, 'cycles')}"]
    if rec is None:
        right = ["no polished image", f"final {final}"]
    else:
        detector = "  added_by_polish" if view.get("added_by_polish") else ""
        right = [f"a{rec.get('k')}  gate {_short_gate(gate_summary(rec))}{detector}",
                 f"check {_verdict(vc, 'polished')}  ->  final {final}"]
    return left, right


def side_by_side_sheet(rows: list, tile_width: int = TILE_WIDTH):
    """One image of ``(cycles image | None, left lines, polished image | None, right lines)`` rows: Cycles left,
    polished right, ``tile_width`` px per tile, two label lines under each; a missing image is a grey tile."""
    from PIL import Image, ImageDraw

    def fit(img):
        return img.resize((tile_width, max(1, round(img.height * tile_width / img.width))),
                          Image.Resampling.LANCZOS)

    sized = [(fit(a) if a is not None else None, la, fit(b) if b is not None else None, lb) for a, la, b, lb in rows]
    heights = [t.height for r in sized for t in (r[0], r[2]) if t is not None]
    tile_h = max(heights) if heights else round(tile_width * 9 / 16)
    gap = 4
    cell_h = tile_h + SBS_LABEL_HEIGHT
    sheet = Image.new("RGB", (2 * tile_width + 3 * gap, len(sized) * cell_h + (len(sized) + 1) * gap), (32, 32, 32))
    draw = ImageDraw.Draw(sheet)
    font = _font(15)
    for i, row in enumerate(sized):
        y = gap + i * (cell_h + gap)
        for col, (img, lines) in enumerate(((row[0], row[1]), (row[2], row[3]))):
            x = gap + col * (tile_width + gap)
            if img is None:
                draw.rectangle([x, y, x + tile_width - 1, y + tile_h - 1], fill=(90, 90, 90))
                draw.text((x + 8, y + tile_h // 2 - 8), "no image", fill=(230, 230, 230), font=font)
            else:
                sheet.paste(img, (x, y))
            draw.rectangle([x, y + tile_h, x + tile_width - 1, y + cell_h - 1], fill=(0, 0, 0))
            for n, text in enumerate(lines[:2]):
                draw.text((x + 6, y + tile_h + 3 + 20 * n), text, fill=(255, 255, 255), font=font)
    return sheet


def polish_on(inp: Inputs) -> tuple[bool, Optional[str]]:
    """Whether the project has its polish on (side-by-side sheets, §9.4) and, if not, why."""
    if not polish_allowed(inp.brief):
        return False, "brief polish: false"
    if inp.gate is not None and inp.gate["decision"] in NO_POLISH_DECISIONS:
        return False, f"gate validation {inp.gate['decision']}: no polish for this project"
    if inp.polish is None:
        return False, "the polish did not run in this run"
    return True, None


def sbs_group(view: dict, variant: str = "base") -> str:
    """The side-by-side sheet of a view: its room, or ``exterior_<variant>`` for an exterior view (no room), else
    ``-``."""
    if view.get("room_id"):
        return view["room_id"]
    return f"exterior_{view.get('variant') or variant}" if view.get("view_kind") == "exterior" else "-"


def write_side_by_side(inp: Inputs, views: list[dict]) -> dict:
    """``contact_sbs_<room>.jpg`` per room with rendered views when the polish is on (§9.4); ``{room: name}``."""
    on, why = polish_on(inp)
    if not on:
        inp.side_by_side_note = why
        return {}
    by_room: dict[str, list] = {}
    for view in views:
        by_room.setdefault(sbs_group(view, inp.variant), []).append(view)
    sheets = {}
    for room, room_views in sorted(by_room.items()):
        rows = []
        for view in room_views:
            pol_src, rec = _polish_tile_source(inp, view)
            left, right = side_by_side_labels(view, rec)
            cyc = _load_rgb(_cycles_tile_source(inp, view["camera"]))
            pol = _load_rgb(pol_src)
            if rec is not None and pol is None:
                inp.warnings.append(f"{view['camera']}: polish attempt a{rec.get('k')} image not found for the "
                                    f"side-by-side sheet")
            rows.append((_pil(cyc), left, _pil(pol), right))
        name = f"{SBS_PREFIX}{re.sub(r'[^A-Za-z0-9_.-]+', '_', room)}.jpg"
        C.save_jpeg_under(side_by_side_sheet(rows), inp.out_dir / name)
        sheets[room] = name
    return sheets


def _pil(rgb):
    if rgb is None:
        return None
    from PIL import Image
    return Image.fromarray(rgb)


def write_images(inp: Inputs, views: list[dict]) -> dict:
    """Final previews, plan copies and contact sheets into ``inp.out_dir``; returns ``{level: sheet name}``."""
    from PIL import Image

    out = inp.out_dir
    out.mkdir(parents=True, exist_ok=True)
    tiles: dict[str, list] = {}
    exterior_tiles: dict[str, list] = {}
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
            if view.get("view_kind") == "exterior":
                exterior_tiles.setdefault(view.get("variant") or inp.variant, []).append((tile_label(view), img))
            else:
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
    inp.exterior_sheets = {}
    for variant in sorted(exterior_tiles):
        name = f"contact_exterior_{re.sub(r'[^A-Za-z0-9_.-]+', '_', variant)}.jpg"
        C.save_jpeg_under(contact_sheet(exterior_tiles[variant], columns=3), out / name)
        inp.exterior_sheets[variant] = name
    inp.variant_sheets = write_variant_sheets(inp)
    inp.side_by_side = write_side_by_side(inp, views)
    # Files of an earlier run that this run did not write are listed, not deleted.
    written = ({v["preview"] for v in views} | {v["plan"] for v in views} | set(sheets.values())
               | set(inp.side_by_side.values()) | set(inp.exterior_sheets.values())
               | {n for sheet in inp.variant_sheets.values() for n in sheet.values()})
    for pattern in ("*_final_preview.jpg", "*_plan.jpg", "contact_*.jpg"):
        for f in sorted(out.glob(pattern)):
            if f.name not in written:
                inp.warnings.append(f"final/{f.name} is from an earlier run (not part of this report)")
    inp.sheets_block = write_sheets_block(inp)
    return sheets


def _safe_name(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text)


def write_variant_sheets(inp: Inputs) -> dict:
    """Per alternative with its own final manifest: ``contact_variant_<id>.jpg`` (its interior views) and, when it
    rendered exterior views of its own (its outside changed), ``contact_exterior_<id>.jpg``. The tiles are the
    previews of the alternative's own ``variants/<id>/final/``. ``{variant id: {"interior": name, "exterior":
    name}}``; an alternative with an unchanged outside has no exterior sheet (the report lists the base views)."""
    from PIL import Image

    out: dict = {}
    for vid, manifest in sorted(inp.variant_manifests.items()):
        folder = (inp.root or inp.project_out) / "variants" / vid / FINAL_DIR
        tiles: dict[str, list] = {"interior": [], "exterior": []}
        for v in manifest.get("views") or []:
            if not isinstance(v, dict):
                continue
            kind = "exterior" if v.get("view_kind") == "exterior" else "interior"
            rgb = _load_rgb(folder / v["preview"]) if v.get("preview") else None
            if rgb is None:
                inp.warnings.append(f"variant {vid}: {v.get('camera')}: final preview not found; no tile")
                continue
            img = Image.fromarray(rgb)
            img.thumbnail((TILE_WIDTH * 2, TILE_WIDTH * 2))
            label = tile_label(v) if "final" in v and "unverified" in v else str(v.get("camera"))
            tiles[kind].append((label, img))
        names = {}
        for kind, prefix, columns in (("interior", "contact_variant_", CONTACT_COLUMNS),
                                      ("exterior", "contact_exterior_", 3)):
            if tiles[kind]:
                names[kind] = f"{prefix}{_safe_name(vid)}.jpg"
                C.save_jpeg_under(contact_sheet(tiles[kind], columns=columns), inp.out_dir / names[kind])
        if names:
            out[vid] = names
    return out


def write_sheets_block(inp: Inputs) -> Optional[dict]:
    """The Sheets block of the report (``m10.sheets_block``) with the debug images as JPEG <= 300 KB under
    ``final/debug/`` (a private project's are named only) and ``sheets_report.md`` copied (a private project's
    stays on the volume). None without ``sheets.json`` and for an alternative's sub-output (the base report has it)."""
    sh = inp.sheets
    if not isinstance(sh, dict) or inp.variant != "base":
        return None
    root = inp.root or inp.project_out
    rows = sheet_image_rows(sh, inp.private)
    write_debug_previews(root, inp.out_dir, inp.private, inp.warnings, rows)
    block = M.sheets_block(sh, inp.private, sheet_names(sh, inp.private),
                           {r["debug_image"]: r.get("debug_preview") for r in rows})
    report = root / SHEETS_REPORT
    if report.is_file():
        if inp.private:
            block["report_kept_on_volume"] = SHEETS_REPORT
        else:
            shutil.copyfile(report, inp.out_dir / SHEETS_REPORT)
            block["report"] = SHEETS_REPORT
    return block


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
    det_model = ((inp.check or {}).get("detector") or {}).get("model")
    if isinstance(det_model, dict) and det_model.get("repo"):
        rows.append({"role": "detector", "repo": det_model.get("repo"), "revision": det_model.get("revision"),
                     "licence": det_model.get("licence"), "source": "check_manifest.json"})
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
# Milestone 7 summaries (§9.4): units, recognition, site, separators, assumed values, attribution, detector
# --------------------------------------------------------------------------

def unit_system(building: Optional[dict]) -> str:
    """``project.unit_system`` of the building (``metric`` when not recorded: every pre-M7 building is metric)."""
    system = (((building or {}).get("project") or {}) if isinstance(building, dict) else {}).get("unit_system")
    return system if system in ("metric", "imperial") else "metric"


def length_text(metres: Any, system: str) -> str:
    """A length in the project's system: imperial ``11' 3" (3.43 m)``, metric ``3,43 m`` (``wenart.units``)."""
    if not isinstance(metres, (int, float)) or isinstance(metres, bool):
        return "-"
    from wenart import units as U
    if system == "imperial":
        return f"{U.format_length(float(metres), 'imperial')} ({float(metres):.2f} m)"
    return U.format_length(float(metres), "metric")


def _doc_name(file: Any, index: int, private: bool) -> Any:
    """A document's file name, or ``document <n>`` for a private project (file names stay on the volume)."""
    return f"document {index}" if private else file


def units_summary(building: Optional[dict], private: bool = False) -> Optional[dict]:
    """``{system, recorded, documents: [{file, unit_system, source_kind}]}`` of the building (None without one; a
    private project's documents are numbered, never named)."""
    if not isinstance(building, dict):
        return None
    docs = [{"file": _doc_name(d.get("file"), i, private), "unit_system": d.get("unit_system"),
             "source_kind": d.get("source_kind")}
            for i, d in enumerate((d for d in building.get("documents") or [] if isinstance(d, dict)), start=1)]
    return {"system": unit_system(building), "recorded": bool((building.get("project") or {}).get("unit_system")),
            "documents": docs}


def _evidence_list(el: dict) -> list[dict]:
    ev = el.get("evidence")
    if isinstance(ev, dict):
        return [ev]
    return [e for e in ev or [] if isinstance(e, dict)]


def raster_files(building: Optional[dict]) -> set:
    """Files with a scan or photo page (docs/milestone7.md §4)."""
    return {d.get("file") for d in (building or {}).get("documents") or [] if isinstance(d, dict)
            for pg in d.get("pages") or [] if isinstance(pg, dict) and pg.get("kind") in RASTER_KINDS}


def label_path(room: dict) -> str:
    """How a raster room label was accepted (§3.4), from the evidence the pipeline recorded: the passes' ``ai``
    evidence (``entity recognition:<key>``) carries the acceptance path as its confidence (room_labels:
    0.85 two passes agree, 0.8 one pass equals Tesseract, 0.3 not accepted); ``ocr`` evidence alone = Tesseract
    only (no answers, or ``--no-ai``)."""
    ev = _evidence_list(room)
    ai = [e for e in ev if e.get("method") == "ai" and str(e.get("entity") or "").startswith("recognition:")]
    confs = {round(float(e["confidence"]), 3) for e in ai if isinstance(e.get("confidence"), (int, float))}
    if LABEL_TWO_PASS_CONFIDENCE in confs:
        return "two_pass"
    if LABEL_TESSERACT_CONFIDENCE in confs:
        return "tesseract"
    if ai:
        return "not_accepted"
    if any(e.get("method") == "ocr" for e in ev):
        return "tesseract_only"
    return "none"


def recognition_summary(inp: Inputs) -> Optional[dict]:
    """The AI typing and the raster labels of the building (§3, §4, §9.4): type methods, AI-typed pieces with both
    passes' answers, composites, raster pages and, per room labelled from a raster page, its acceptance path."""
    b = inp.building
    if not isinstance(b, dict):
        return None
    furniture = [f for f in b.get("furniture") or [] if isinstance(f, dict)]
    methods: dict[str, int] = {}
    ai, composites, unanswered = [], [], []
    for f in furniture:
        notes = [str(e.get("note")) for e in _evidence_list(f) if str(e.get("note") or "").startswith(COMPOSITE_NOTE)]
        if (f.get("type_method") == "none" and not f.get("type_candidates") and f.get("build", True) is not False
                and (f.get("type") or "unknown") == "unknown" and not notes):
            unanswered.append(f.get("id"))      # asked (or to be asked) but no AI answer was applied (review cross-5)
        if f.get("type_method"):
            methods[str(f["type_method"])] = methods.get(str(f["type_method"]), 0) + 1
        cands = sorted((c for c in f.get("type_candidates") or [] if isinstance(c, dict)),
                       key=lambda c: (str(c.get("pass") or ""), str(c.get("model") or "")))
        if f.get("type_method") == "ai_two_pass" or cands:
            ai.append({"id": f.get("id"), "room_id": f.get("room_id"), "type": f.get("type"),
                       "type_method": f.get("type_method"), "status": f.get("status"),
                       "build": f.get("build", True) is not False, "agreed": f.get("type_method") == "ai_two_pass",
                       "answers": [{"pass": c.get("pass"), "model": c.get("model") or c.get("model_key"),
                                    "type": c.get("type"), "front": c.get("front"), "confidence": c.get("confidence"),
                                    "reason": c.get("reason")} for c in cands]})
        if notes:
            composites.append({"id": f.get("id"), "room_id": f.get("room_id"), "type": f.get("type"),
                               "status": f.get("status"), "size": (f.get("footprint") or {}).get("size"),
                               "note": notes[0]})
    files = raster_files(b)
    docs = [d for d in b.get("documents") or [] if isinstance(d, dict)]
    names = {d.get("file"): _doc_name(d.get("file"), i, inp.private) for i, d in enumerate(docs, start=1)}
    pages = [{"file": names.get(d.get("file")), "page": pg.get("page"), "kind": pg.get("kind"),
              "class": pg.get("class"), "level_id": pg.get("level_id"), "classifier": pg.get("classifier"),
              "source_kind": d.get("source_kind"),
              "rectified_image": None if inp.private else pg.get("rectified_image"),
              "skip_reason": None if inp.private else pg.get("skip_reason")}
             for d in docs for pg in d.get("pages") or [] if isinstance(pg, dict) and pg.get("kind") in RASTER_KINDS]
    rooms = []
    for r in b.get("rooms") or []:
        if not isinstance(r, dict):
            continue
        primary = next((e for e in _evidence_list(r) if e.get("method") != "derived"), None)
        if primary is None or primary.get("file") not in files:
            continue
        rooms.append({"id": r.get("id"), "label": r.get("label"), "label_raw": r.get("label_raw"),
                      "room_type": r.get("room_type"), "status": r.get("status"), "path": label_path(r),
                      "file": names.get(primary.get("file")), "page": primary.get("page")})
    requests = C.read_json(inp.project_out / "recognition" / "requests.json")
    folder = inp.project_out / "recognition"
    return {"type_methods": dict(sorted(methods.items())), "ai_typed": ai, "composites": composites,
            "no_answer": unanswered, "raster_pages": pages, "raster_rooms": rooms,
            "questions": len(requests.get("items") or []) if isinstance(requests, dict) else None,
            "answer_files": sorted(p.name for p in folder.glob("answers_*.json")) if folder.is_dir() else []}


def site_summary(building: Optional[dict]) -> Optional[dict]:
    """The site of the building (§2.5): plot and other boundary walls, exterior areas, decor, openings, with the
    ``build`` flag of each (Milestone 10: a drawn plot, paving, grass, parking and boundary wall is built; a
    label-only area is recorded, not built). None when the building has no site block."""
    site = (building or {}).get("site") if isinstance(building, dict) else None
    if not isinstance(site, dict) or not any(site.get(k) for k in ("boundary_walls", "areas", "decor", "openings")):
        return None
    from wenart import geometry as G

    walls = [{"id": w.get("id"), "kind": w.get("kind"), "level_id": w.get("level_id"),
              "length_m": round(G.distance(w["start"], w["end"]), 3) if w.get("start") and w.get("end") else None,
              "thickness_m": w.get("thickness"), "build": w.get("build")}
             for w in site.get("boundary_walls") or [] if isinstance(w, dict)]
    areas = []
    for a in site.get("areas") or []:
        if not isinstance(a, dict):
            continue
        ls = a.get("label_size") if isinstance(a.get("label_size"), dict) else {}
        areas.append({"id": a.get("id"), "label": a.get("label"), "label_size": ls.get("text"),
                      "measured": ls.get("measured"), "status": ls.get("status"),
                      "closed": a.get("polygon") is not None, "kind": a.get("kind"), "build": a.get("build")})
    decor: dict[str, int] = {}
    for d in site.get("decor") or []:
        if isinstance(d, dict):
            decor[str(d.get("kind") or "other")] = decor.get(str(d.get("kind") or "other"), 0) + 1
    openings = [{"id": o.get("id"), "type": o.get("type"), "width_m": o.get("width"),
                 "boundary_wall_id": o.get("boundary_wall_id")}
                for o in site.get("openings") or [] if isinstance(o, dict)]
    built_known = any(x.get("build") is not None for x in walls + areas)
    return {"boundary_walls": walls, "areas": areas, "decor": dict(sorted(decor.items())), "openings": openings,
            "built_known": built_known}


def separators_summary(building: Optional[dict]) -> list[dict]:
    """The virtual separators of the building (§2.7.1): openings with ``virtual`` true (no geometry is built)."""
    from wenart import geometry as G

    out = []
    for o in (building or {}).get("openings") or []:
        if not isinstance(o, dict) or not o.get("virtual"):
            continue
        line = o.get("line")
        notes = [str(e.get("note")) for e in _evidence_list(o) if e.get("note")]
        out.append({"id": o.get("id"), "level_id": o.get("level_id"), "status": o.get("status"),
                    "length_m": round(G.distance(line[0], line[1]), 3) if line and len(line) == 2 else o.get("width"),
                    "note": notes[0] if notes else None})
    return out


def assumed_summary(inp: Inputs) -> dict:
    """Every assumed value the report can see (§2.9, §6.4, §9.4): brief defaults, assumed level titles, ceiling
    heights, opening heights and sills, stair direction/turn/void, and the scene manifest's assumed values grouped by
    field and reason."""
    b = inp.building if isinstance(inp.building, dict) else {}
    system = unit_system(b)
    values = (inp.brief or {}).get("values") or {}
    brief = [{"key": k, "value": _dotted(values, k)} for k in (inp.brief or {}).get("assumed") or []]
    style = style_assumptions(inp.style)
    building: list[str] = []
    for lv in b.get("levels") or []:
        if not isinstance(lv, dict):
            continue
        if lv.get("label_source") == "assumed":
            building.append(f"{lv.get('id')}: level '{lv.get('label')}' assumed (no level title on the page)")
        if lv.get("ceiling_height_source") == "assumed_default":   # (else measured: section, elevation_drawing)
            building.append(f"{lv.get('id')}: ceiling height {length_text(lv.get('ceiling_height'), system)} "
                            f"({lv.get('ceiling_height_source')})")
    for doc in b.get("documents") or []:
        for page in (doc.get("pages") or []) if isinstance(doc, dict) else []:
            a = page.get("aspect") if isinstance(page, dict) else None
            if isinstance(a, dict) and a.get("assumed"):
                name = doc.get("file") if not inp.private else "a raster page"
                building.append(f"{name} p{page.get('page')}: photo aspect assumed: snapped to the {a.get('name')} "
                                f"sheet ratio {a.get('snapped')} (measured {a.get('measured')}, {a.get('off_pct')} % off)")
    fronts = [str(f.get("id")) for f in b.get("furniture") or []
              if isinstance(f, dict) and "front_deg" in (f.get("assumed") or [])]
    if fronts:
        building.append(f"front kept from the drawing although both AI passes answered 'none': {len(fronts)} "
                        f"piece(s) ({', '.join(fronts[:6])}{' ...' if len(fronts) > 6 else ''})")
    groups: dict[tuple, list] = {}
    for o in b.get("openings") or []:
        if not isinstance(o, dict):
            continue
        for key in o.get("assumed") or []:
            groups.setdefault((str(o.get("type")), str(key), o.get(key)), []).append(str(o.get("id")))
    for (otype, key, value), ids in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1], str(kv[0][2]))):
        building.append(f"{otype} {key.replace('_', ' ')} {length_text(value, system)}: {len(ids)} opening(s) "
                        f"({', '.join(ids[:6])}{' ...' if len(ids) > 6 else ''})")
    for f in b.get("furniture") or []:
        stair = f.get("stair") if isinstance(f, dict) else None
        if not isinstance(stair, dict):
            continue
        what = [k[:-len("_assumed")] for k in ("direction_assumed", "turn_assumed", "void_assumed") if stair.get(k)]
        if what:
            building.append(f"{f.get('id')} (stair): {', '.join(what)} assumed"
                            + (f" ({stair['reason']})" if stair.get("reason") else ""))
        if stair.get("riser_source"):
            building.append(f"{f.get('id')} (stair): riser {length_text(stair.get('riser_m'), system)} "
                            f"({stair['riser_source']})")
    scene: dict[tuple, list] = {}
    for a in (inp.scene or {}).get("assumed") or []:
        if isinstance(a, dict):
            scene.setdefault((str(a.get("field")), str(a.get("reason") or "-")), []).append(str(a.get("object")))
    scene_rows = [{"field": f, "reason": r, "count": len(objs), "examples": objs[:3]}
                  for (f, r), objs in sorted(scene.items())]
    m10 = M.assumed_lines(b, inp.scene, lambda v: length_text(v, system))
    return {"brief": brief, "style": style, "building": building, "scene": scene_rows, "m10": m10}


def _dotted(values: dict, key: str):
    """``render.samples`` -> ``values["render"]["samples"]`` (wenart.brief lists nested defaults as dotted paths)."""
    cur = values
    for part in str(key).split("."):
        cur = cur.get(part) if isinstance(cur, dict) else None
    return cur


def style_assumptions(style: Optional[dict]) -> list[str]:
    """The assumed parts of the project's style (M7 §0, §13): the default style text when the brief has none, and
    every other ``assumed:`` warning of the style stage (slot fills from the defaults)."""
    if not isinstance(style, dict):
        return []
    out = []
    for w in style.get("warnings") or []:
        text = str(w)
        if not text.startswith("assumed:"):
            continue
        if "no style in the brief" in text:
            out.append(f"style: default text \"{style.get('source_text') or '?'}\" (no style in brief.yaml; "
                       f"wenart/defaults.yaml)")
        else:
            out.append("style " + text[len("assumed:"):].strip())
    return out


def attribution_summary(building: Optional[dict]) -> dict:
    """Credits of the Objaverse models of the building (§7.3): one entry per model with its §7.3 line
    (``asset.attribution``) and the pieces that use it, plus the ODC-By 1.0 notice when there is any."""
    found: dict[str, dict] = {}
    b = building if isinstance(building, dict) else {}
    for piece in list(b.get("furniture") or []) + list(b.get("decor") or []):
        asset = piece.get("asset") if isinstance(piece, dict) else None
        if not isinstance(asset, dict) or asset.get("library") != "objaverse" or asset.get("method") == "parametric":
            continue
        key = str(asset.get("asset_id") or asset.get("uid") or "?")
        entry = found.setdefault(key, {"asset_id": key, "licence": asset.get("licence"),
                                       "credit": asset.get("attribution") or None, "pieces": []})
        entry["pieces"].append(str(piece.get("id") or "?"))
    notice = None
    if found:
        from wenart.assets import objaverse as OBJ   # stdlib-only at import; the yaml is read here
        try:
            cfg = OBJ.load_config()
        except Exception:  # noqa: BLE001 - the notice has built-in defaults (allenai/objaverse @ 21e4e14)
            cfg = None
        notice = OBJ.odc_by_notice(cfg)
    return {"credits": [found[k] for k in sorted(found)], "notice": notice,
            "missing": sorted(k for k, e in found.items() if not e["credit"])}


def detector_summary(inp: Inputs, views: list[dict]) -> Optional[dict]:
    """The added-object detector of the check manifest (§8.1); None when the check did not run."""
    if inp.check is None:
        return None
    det = inp.check.get("detector")
    if not isinstance(det, dict):
        return {"status": "not_recorded", "advisory": True, "thresholds": None, "model": None, "not_computed": [],
                "views_added": []}
    return {"status": det.get("status") or "not_run", "advisory": bool(det.get("advisory", True)),
            "reason": det.get("reason"), "thresholds": det.get("thresholds"), "model": det.get("model"),
            "not_computed": list(det.get("not_computed") or []),
            "views_added": [v["camera"] for v in views if v.get("added_by_polish")]}


# --------------------------------------------------------------------------
# Manifest and report
# --------------------------------------------------------------------------

def m10_blocks(inp: Inputs, views: list[dict]) -> dict:
    """The Milestone 10 blocks of the final manifest (``wenart/report/m10.py``): sheets, whole building, Feature 1
    (completion and drawn-piece check), exterior views and the variants."""
    own_exterior = [v["camera"] for v in views if v.get("view_kind") == "exterior"]
    if inp.variant == "base":
        manifests = dict(inp.variant_manifests)
        manifests["base"] = {"status": "ok", "views": views}
        variants = M.variants_block(inp.building, manifests, own_exterior, "base")
    else:
        variants = None
    return {
        "variant": inp.variant,
        "sheets": inp.sheets_block,
        "building_detail": M.building_block(inp.building),
        "completion": M.completion_block(inp.completion),
        "drawn_check": M.drawn_block(inp.check),
        "exterior": M.exterior_block(inp.scene, inp.check, views, inp.exterior_gate, inp.variant),
        "exterior_sheets": dict(inp.exterior_sheets),
        "variants": variants,
        "variant_sheets": {vid: dict(names) for vid, names in inp.variant_sheets.items()},
        "base_exterior_views": own_exterior if inp.variant == "base" else [
            v.get("camera") for v in (inp.base_manifest or {}).get("views") or []
            if isinstance(v, dict) and v.get("view_kind") == "exterior"],
    }


def m10_flags(blocks: dict) -> list[str]:
    """Open items of Milestone 10: levels left out, exterior views that were dropped or held back, a mismatch of
    the elevation check, a roof the render does not show, drawn pieces that moved, refused proposals."""
    flags = []
    left_out = ((blocks.get("building_detail") or {}).get("levels_left_out")) or []
    if left_out:
        flags.append(f"{len(left_out)} level(s) left out of the building: "
                     + "; ".join(f"{x['label']} ({x['reason']})" for x in left_out[:4]))
    ext = blocks.get("exterior") or {}
    if ext.get("dropped"):
        flags.append(f"{len(ext['dropped'])} exterior view(s) dropped, no camera place worked: "
                     + ", ".join(str(d["name"]) for d in ext["dropped"][:6]))
    gate = ext.get("gate")
    if ext.get("views") and gate is not None and not gate.get("polish_allowed"):
        flags.append(f"exterior gate {gate.get('decision')}: the exterior views are the Cycles render "
                     f"({'; '.join(str(r) for r in (gate.get('reasons') or [])[:2]) or 'no reason recorded'})")
    elev = ext.get("elevation") or {}
    summary = elev.get("summary") or {}
    if summary.get("mismatch") or summary.get("roof") == "mismatch":
        flags.append(f"elevation check: {summary.get('mismatch', 0)} facade(s) differ from the drawn elevation; "
                     f"roof heights {summary.get('roof')}")
    missing_roof = [v["camera"] for v in ext.get("views") or [] if v.get("roof") == "missing"]
    if missing_roof:
        flags.append("the roof of the building JSON is not in the render: " + ", ".join(missing_roof))
    drawn = blocks.get("drawn_check") or {}
    if drawn.get("failed") or drawn.get("violations"):
        flags.append(f"drawn-piece check: {len(drawn.get('failed') or [])} piece(s) moved beyond the tolerance, "
                     f"{len(drawn.get('violations') or [])} locked-rule violation(s)")
    comp = blocks.get("completion") or {}
    refused = sum(len(r["refused"]) + len(r["dropped"]) for r in comp.get("rooms") or [])
    if refused:
        flags.append(f"AI completion: {refused} proposal(s) refused, reverted or not placed (listed per room)")
    return flags


def build_manifest(inp: Inputs, views: list[dict], sheets: dict) -> dict:
    by_reason: dict[str, int] = {}
    for v in views:
        if v["final"] == "cycles":
            by_reason[str(v["reason"])] = by_reason.get(str(v["reason"]), 0) + 1
    rooms = rooms_summary(inp, views)
    b = inp.building or {}
    flags = advisory_flags(inp, views)
    recognition = recognition_summary(inp)
    attribution = attribution_summary(inp.building)
    detector = detector_summary(inp, views)
    flags.extend(m7_flags(recognition, attribution, detector))
    blocks = m10_blocks(inp, views)
    flags.extend(m10_flags(blocks))
    stages = {
        "render": "run" if inp.render_manifest is not None else "not_run",
        "polish": ("not_run" if inp.polish is None else "incomplete" if inp.polish.get("incomplete") else "run"),
        "check": "not_run" if inp.check is None else ("single_pass" if inp.check.get("single_pass") else "run"),
        "check_calibration": "not_run" if inp.check_calibration is None else "run",
        "gate_calibration": "not_run" if inp.gate_calibration is None else "run",
        "gate_validation": "not_run" if inp.gate is None else inp.gate["decision"],
        "exterior_gate": "not_applicable" if inp.exterior_gate is None else inp.exterior_gate.get("decision"),
        "expected": "run" if inp.expected else "not_run",
    }
    files = {"render_manifest": inp.render_dir / "render_manifest.json",
             "scene_manifest": inp.project_out / "scene" / "scene_manifest.json",
             "polish_manifest": inp.polish_dir / "polish_manifest.json",
             "check_manifest": inp.check_dir / "check_manifest.json",
             "check_calibration": inp.check_dir / "check_calibration.json",
             "expected_views": inp.check_dir / "expected_views.json",
             "gate_calibration": inp.gate_dir / "gate_calibration.json",
             "gate_validation": inp.gate_dir / "gate_validation.json",
             "sheets": (inp.root or inp.project_out) / "sheets.json",
             "completion": (inp.root or inp.project_out) / "completion.json"}
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
            "interior_views": sum(v.get("view_kind") != "exterior" for v in views),
            "exterior_views": sum(v.get("view_kind") == "exterior" for v in views),
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
        # Milestone 7 (§9.4)
        "units": units_summary(inp.building, inp.private),
        "side_by_side": {"sheets": dict(inp.side_by_side), "note": inp.side_by_side_note},
        "recognition": recognition,
        "site": site_summary(inp.building),
        "separators": separators_summary(inp.building),
        "assumed": assumed_summary(inp),
        "attribution": attribution,
        "detector": detector,
        # Milestone 9
        "decor_ai": decor_ai_summary(inp.project_out),
        "files_3d": None if inp.private else files_3d_summary(inp.project_out),
        # Milestone 10
        **blocks,
        "warnings": list(inp.warnings),
    }


def decor_ai_summary(project_out: Path) -> Optional[dict]:
    """The AI decor of ``decor_ai.json`` (Milestone 9): items by method, the rooms with AI decor and the rooms that
    fell back to the rules with the reason; None without the file."""
    doc = C.read_json(Path(project_out) / "decor_ai.json")
    if not isinstance(doc, dict):
        return None
    return {"model": doc.get("model"), "items_ai": doc.get("items_ai", 0), "items_rule": doc.get("items_rule", 0),
            "rooms_ai": doc.get("rooms_ai", 0),
            "fallbacks": [{"room_id": r.get("room_id"), "reason": r.get("fallback")} for r in doc.get("rooms") or []
                          if r.get("fallback")]}


def files_3d_summary(project_out: Path) -> Optional[dict]:
    """The 3D files of ``export/export_manifest.json`` (Milestone 9): name and size per file; the results copy them
    to ``final/<p>/3d/``."""
    doc = C.read_json(Path(project_out) / "export" / "export_manifest.json")
    if not isinstance(doc, dict):
        return None
    files = {k: {"file": v.get("file"), "bytes": v.get("bytes")} for k, v in (doc.get("files") or {}).items()
             if isinstance(v, dict) and not v.get("missing")}
    return {"files": files, "max_texture": doc.get("max_texture"), "images_scaled": doc.get("images_scaled"),
            "cameras": len(doc.get("cameras") or {}), "warnings": list(doc.get("warnings") or [])}


def m9_lines(manifest: dict) -> list[str]:
    """The report's Milestone 9 sections: the 3D files, the AI decor."""
    lines = []
    files = manifest.get("files_3d")
    if files and files.get("files"):
        lines += ["", "## 3D files", "",
                  "Open in Blender: the `.blend` directly (textures packed, cameras with their metered exposure in "
                  "the custom property `wenart_exposure_ev`, render settings as these images); the `.glb` with "
                  "File > Import > glTF 2.0 (also other 3D tools). In the results: `final/<project>/3d/`.", ""]
        lines += C.table(["file", "size"], [[f"[{f['file']}](3d/{f['file']})",
                                             f"{(f.get('bytes') or 0) / 2 ** 20:.1f} MB"]
                                            for f in files["files"].values()])
        lines.append("")
        lines.append(f"{files['cameras']} cameras; textures scaled to at most {files.get('max_texture')} px "
                     f"({files.get('images_scaled') or 0} scaled) for the download.")
    decor = manifest.get("decor_ai")
    if decor:
        lines += ["", "## AI decor", "",
                  f"{decor['items_ai']} decor items chosen by the AI ({decor.get('model') or '-'}; both passes "
                  f"agreeing) in {decor['rooms_ai']} rooms; {decor['items_rule']} items by the rules. The decor "
                  "stage places decor only: it moves, adds and removes no furniture (the AI completion of furnished "
                  "rooms has its own section, `AI completion of furnished rooms`; "
                  "`furniture/<project>/decor_report.md` has every room)."]
        if decor["fallbacks"]:
            lines += [""] + C.bullets([f"{f['room_id']}: rules ({f['reason']})" for f in decor["fallbacks"]])
    return lines


def m7_flags(recognition: Optional[dict], attribution: dict, detector: Optional[dict]) -> list[str]:
    """Open items of Milestone 7: AI typing left open, raster labels not confirmed, CC BY models without a credit
    line, an advisory or uncomputed detector, views the detector rejected."""
    flags = []
    rec = recognition or {}
    open_types = [p["id"] for p in rec.get("ai_typed") or [] if not p["agreed"] and p["build"]]
    if open_types:
        flags.append(f"{len(open_types)} drawn piece(s) not typed: the two AI passes disagree or did not answer "
                     f"(unknown, unverified; footprint kept): {', '.join(str(x) for x in open_types[:8])}")
    if rec.get("no_answer"):
        flags.append(f"{len(rec['no_answer'])} drawn piece(s) without an AI answer (not asked, or the answers were "
                     f"not applied; unknown, unverified; footprint kept): "
                     + ", ".join(str(x) for x in rec["no_answer"][:8]))
    if rec.get("composites"):
        flags.append(f"{len(rec['composites'])} drawn group(s) not split into pieces (unknown, unverified): "
                     + ", ".join(str(c["id"]) for c in rec["composites"][:8]))
    unconfirmed = [r["id"] for r in rec.get("raster_rooms") or [] if r["path"] not in ("two_pass", "tesseract")]
    if unconfirmed:
        flags.append(f"{len(unconfirmed)} raster room label(s) not confirmed (§3.4): "
                     + ", ".join(str(x) for x in unconfirmed[:8]))
    if attribution.get("missing"):
        flags.append("Objaverse model(s) without a credit line (check the catalogue entry before sharing images): "
                     + ", ".join(attribution["missing"]))
    det = detector or {}
    if det.get("status") == "advisory":
        flags.append("added-object detector advisory (not calibrated): it lists boxes and never rejects a polish")
    if det.get("not_computed"):
        flags.append(f"added-object detector: no current detection for {', '.join(det['not_computed'])} "
                     f"(those polished images stay Cycles)")
    if det.get("views_added"):
        flags.append(f"the polish added an object in {', '.join(det['views_added'])}: the Cycles render is final")
    return flags


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


def exterior_gate_lines(manifest: dict) -> list[str]:
    """The exterior part of the "Gate validation" section (Milestone 10): the exterior views are calibrated with
    their own negatives and validated apart; a failed exterior validation keeps them Cycles only and leaves the
    rooms alone. Nothing for a project without exterior views."""
    ext = manifest.get("exterior") or {}
    g = ext.get("gate")
    if g is None or not ext.get("views"):
        return []
    lim = g.get("limits") or {}

    def rate(value, limit) -> str:
        if value is None:
            return "-"
        return f"{100.0 * float(value):.1f} %" + (f" (limit {100.0 * float(limit):.0f} %)" if limit is not None else "")

    lines = ["", "### Exterior views", "",
             f"Exterior decision: **{g.get('decision')}**. "
             + ("The exterior views may be polished (the same gate, per view)." if g.get("polish_allowed") else
                "The exterior views are the Cycles render; the rooms are not affected.")]
    rows = [["benign exterior comparisons accepted", f"{rate(g.get('benign_accept'), lim.get('benign_accept_min'))}, "
                                                     f"{g.get('n_benign') or 0} comparisons"],
            ["negative exterior comparisons rejected",
             f"{rate(g.get('negative_reject'), lim.get('negative_reject_min'))}, {g.get('n_negative') or 0} comparisons"]]
    lines += [""] + C.table(["item", "value"], rows)
    if g.get("reasons"):
        lines += ["", "Reasons:", ""] + C.bullets([str(r) for r in g["reasons"]])
    return lines


def side_by_side_lines(manifest: dict) -> list[str]:
    """The "Side-by-side sheets" section (§9.4): per room the sheet and the decisions of each view."""
    sbs = manifest.get("side_by_side") or {}
    sheets = sbs.get("sheets") or {}
    lines = ["", "## Side-by-side sheets (Cycles | polished)", ""]
    if not sheets:
        lines.append(f"None: {sbs.get('note') or 'no rendered view'}.")
        return lines
    lines.append("Per room: the Cycles render (left) and the polish candidate (right; the chosen attempt, else the "
                 "last attempt the gate saw) with the gate decision, both check verdicts and the final decision.")
    by_room: dict = {}
    for v in manifest["views"]:
        by_room.setdefault(sbs_group(v, manifest.get("variant") or "base"), []).append(v)
    rows = []
    for room, name in sheets.items():
        lines += ["", f"- {room}: [{name}]({name})"]
        for v in by_room.get(room, []):
            det = "added_by_polish" if v.get("added_by_polish") else (
                (v.get("detector") or {}).get("status") or "-")
            rows.append([room, v["camera"], _attempt_text(v["attempt"]), _short_gate(v["gate"]),
                         _verdict(v["vision_check"], "cycles"), _verdict(v["vision_check"], "polished"), det,
                         v["final"] + (f" ({v['reason']})" if v["reason"] else "")])
    lines += [""] + C.table(["room", "view", "polish attempt", "gate", "check Cycles", "check polished", "detector",
                             "final"], rows)
    return lines


def _answer_text(a: dict) -> str:
    conf = f" {float(a['confidence']):.2f}" if isinstance(a.get("confidence"), (int, float)) else ""
    front = f", front {a['front']}" if a.get("front") not in (None, "none") else ""
    return f"pass {a.get('pass')} {a.get('model') or '?'}: {a.get('type')}{front}{conf}"


def _built_text(build: Any) -> str:
    """``, built`` / ``, recorded only (not built)`` for a site element's ``build`` flag (nothing when unknown)."""
    return "" if build is None else (", built" if build else ", recorded only (not built)")


def m7_building_lines(manifest: dict) -> list[str]:
    """Units, recognition, site, separators and assumed values (§9.4)."""
    units = manifest.get("units")
    system = (units or {}).get("system") or "metric"
    lines = ["", "## Units", ""]
    if units is None:
        lines.append("No building JSON: unknown.")
    else:
        imperial = " (lengths in feet and inches, metres in brackets)" if system == "imperial" else ""
        lines.append(f"Project unit system: **{system}**{imperial}"
                     + ("" if units.get("recorded") else " (not recorded in the building JSON: metric)") + ".")
        if units.get("documents"):
            lines += [""] + C.table(["document", "unit system", "source kind"],
                                    [[d["file"], d.get("unit_system"), d.get("source_kind")]
                                     for d in units["documents"]])
    rec = manifest.get("recognition")
    lines += ["", "## Recognition (AI typing and raster labels)", ""]
    if rec is None:
        lines.append("No building JSON.")
    else:
        methods = ", ".join(f"{k} {n}" for k, n in (rec.get("type_methods") or {}).items()) or "-"
        q = rec.get("questions")
        lines.append(f"Furniture type methods: {methods}. Recognition questions: "
                     f"{'-' if q is None else q}; answer files: {', '.join(rec.get('answer_files') or []) or 'none'}. "
                     "A type counts only when both passes agree and the drawn footprint fits the type's size range; "
                     "otherwise the piece stays `unknown` and `unverified` with both answers.")
        if rec.get("ai_typed"):
            lines += ["", "AI-typed pieces:", ""]
            lines += C.table(["piece", "room", "type", "agreed", "status", "built", "answers"],
                             [[p["id"], p["room_id"], p["type"], "yes" if p["agreed"] else "no", p["status"],
                               "yes" if p["build"] else "no (drawn symbol, not built)",
                               "; ".join(_answer_text(a) for a in p["answers"]) or "no answer"]
                              for p in rec["ai_typed"]])
        if rec.get("composites"):
            lines += ["", "Drawn groups not split into pieces:", ""]
            lines += C.table(["piece", "room", "size", "status", "note"],
                             [[c["id"], c["room_id"], " x ".join(length_text(x, system) for x in c.get("size") or [])
                               or "-", c["status"], c["note"]] for c in rec["composites"]])
        if rec.get("raster_pages"):
            lines += ["", "Raster pages (scans and photos):", ""]
            lines += C.table(["file", "page", "kind", "class", "level", "rectified image", "skip reason"],
                             [[pg["file"], pg["page"], pg["kind"], pg["class"], pg["level_id"],
                               pg.get("rectified_image"), pg.get("skip_reason")] for pg in rec["raster_pages"]])
            if rec.get("raster_rooms"):
                lines += ["", "Room labels of the raster pages and how they were accepted (§3.4):", ""]
                lines += C.table(["room", "label", "as read", "type", "status", "accepted by"],
                                 [[r["id"], r["label"], r["label_raw"] or "—", r["room_type"], r["status"],
                                   LABEL_PATHS.get(r["path"], r["path"])] for r in rec["raster_rooms"]])
    site = manifest.get("site")
    built_text = ("The plot, paving, grass, parking and boundary walls marked built are built in the 3D scene and "
                  "show in the exterior views; an area that is only a label (not built) is recorded, not built."
                  if (site or {}).get("built_known") else "Recorded, not built.")
    lines += ["", "## Site", "", built_text]
    if site:
        rows = [[w["id"], f"boundary wall ({w['kind']})", f"{length_text(w['length_m'], system)} long, "
                 f"{length_text(w['thickness_m'], system)} thick" + _built_text(w.get("build"))]
                for w in site["boundary_walls"]]
        for a in site["areas"]:
            measured = " x ".join(length_text(x, system) for x in a.get("measured") or []) or "-"
            rows.append([a["id"], f"area '{a['label']}'" + (f" ({a['kind']})" if a.get("kind") else ""),
                         f"label size {a.get('label_size') or '-'}, measured "
                         f"{measured} ({a.get('status') or '-'})" + ("" if a["closed"] else ", no closed outline")
                         + _built_text(a.get("build"))])
        rows += [[o["id"], f"{o['type']} in {o.get('boundary_wall_id') or '-'}", f"{length_text(o['width_m'], system)} "
                  "wide"] for o in site["openings"]]
        if site["decor"]:
            rows.append(["-", "decor", ", ".join(f"{k} x {n}" for k, n in site["decor"].items())])
        lines += [""] + C.table(["id", "what", "detail"], rows)
    else:
        lines += ["", "None."]
    seps = manifest.get("separators") or []
    lines += ["", "## Separators", ""]
    if seps:
        lines.append("Virtual lines that split an open-plan face where two room names share it (no geometry is "
                     "built; the pipeline's report.md lists the candidates it dropped):")
        lines += [""] + C.table(["id", "level", "length", "status", "reason"],
                                [[s["id"], s["level_id"], length_text(s["length_m"], system), s["status"], s["note"]]
                                 for s in seps])
    else:
        lines.append("None.")
    assumed = manifest.get("assumed") or {}
    lines += ["", "## Assumed values", ""]
    items = list(assumed.get("style") or [])
    items += [f"brief {a['key']}: {a['value']} (default, not in brief.yaml)" for a in assumed.get("brief") or []]
    items += list(assumed.get("building") or [])
    items += list(assumed.get("m10") or [])
    lines += C.bullets(items)
    if assumed.get("scene"):
        lines += ["", "Scene (build) assumptions:", ""]
        lines += C.table(["field", "objects", "reason", "e.g."],
                         [[s["field"], s["count"], s["reason"], ", ".join(s["examples"])] for s in assumed["scene"]])
    return lines


def m7_model_lines(manifest: dict) -> list[str]:
    """Attribution (§7.3) and the added-object detector (§8.1)."""
    att = manifest.get("attribution") or {}
    lines = ["", "## Attribution", ""]
    if att.get("credits"):
        lines.append("3D models from Objaverse 1.0 used in these images (§7.3):")
        lines += [""] + [f"- {c['credit'] or c['asset_id'] + ': no attribution recorded (check the catalogue entry)'}"
                         f" (used for {', '.join(c['pieces'])})" for c in att["credits"]]
        if att.get("notice"):
            lines += ["", att["notice"]]
    else:
        lines.append("No CC BY or Objaverse model in this project (Poly Haven CC0 models and parametric meshes need "
                     "no credit).")
    det = manifest.get("detector")
    lines += ["", "## Added-object detector", ""]
    if det is None:
        lines.append("Not run: the vision check did not run.")
        return lines
    status = det.get("status")
    if status in ("not_run", "not_recorded"):
        lines.append("Not run for this project (no `detect/` results in the check manifest).")
        return lines
    th = det.get("thresholds") or {}
    if det.get("advisory"):
        lines.append(f"Advisory ({det.get('reason') or 'no thresholds'}): unmatched polished boxes are listed in the "
                     "check report, nothing is rejected.")
    else:
        lines.append(f"Calibrated: t_det {th.get('t_det')}, t_strong {th.get('t_strong')}; a confirmed added non-decor "
                     "object rejects the polished image (the Cycles render is final).")
    model = det.get("model") or {}
    if model:
        lines.append(f"Model: {model.get('repo')} @ {str(model.get('revision') or '-')[:12]} ({model.get('licence')}).")
    rows = []
    for v in manifest["views"]:
        d = v.get("detector")
        if not d:
            continue
        boxes = "; ".join(f"{b.get('class')} {b.get('box_px')} ({', '.join(b.get('confirmed_by') or [])})"
                          for b in d.get("boxes") or [])
        rows.append([v["camera"], d.get("status"), "yes" if d.get("computed") else "no",
                     "yes" if v.get("added_by_polish") else "no", boxes or "-"])
    if rows:
        lines += [""] + C.table(["view", "detector", "computed", "added_by_polish", "confirmed boxes"], rows)
    return lines


def m10_lines(manifest: dict) -> list[str]:
    """The Milestone 10 sections: Sheets, Building, AI completion of furnished rooms (Feature 1), Exterior views and
    Variants (``wenart/report/m10.py``). A block that was not recorded leaves its section out."""
    system = (manifest.get("units") or {}).get("system") or "metric"

    def fmt(value: Any) -> str:
        return length_text(value, system)

    lines: list[str] = []
    variant = manifest.get("variant") or "base"
    if variant != "base":
        lines += ["", f"## This report: variant `{variant}`", "",
                  "An alternative's sub-output: it renders the rooms its plan changes, and its exterior views only "
                  "when its outside differs from the base. The sheets, the whole building and the other variants "
                  "are in the base project's report (`../../final/final_report.md`). The list of base exterior "
                  "views: " + (", ".join(manifest.get("base_exterior_views") or []) or "none") + "."]
    if manifest.get("sheets"):
        lines += M.sheets_lines(manifest["sheets"], manifest["private"], stopped=False)
    detail = manifest.get("building_detail")
    if detail:
        lines += M.building_lines(detail, fmt)
    comp, drawn = manifest.get("completion"), manifest.get("drawn_check")
    if comp:
        lines += M.completion_lines(comp, fmt)
    elif drawn:
        lines += ["", "## AI completion of furnished rooms (Feature 1)", "",
                  "No `completion.json`: the layout stage did not run the completion for this project."]
    if drawn:
        lines += M.drawn_lines(drawn)
    ext = manifest.get("exterior")
    if ext:
        sheets_map = dict(manifest.get("exterior_sheets") or {})
        for vid, names in (manifest.get("variant_sheets") or {}).items():
            if names.get("exterior"):
                sheets_map[vid] = names["exterior"]
        lines += M.exterior_lines(ext, sheets_map, fmt)
        if variant == "base":
            base = manifest.get("base_exterior_views") or []
            unchanged = [v["id"] for v in (manifest.get("variants") or {}).get("variants") or []
                         if not v["base"] and not v["exterior_changed"]]
            if unchanged and base:
                lines += ["", "Alternatives with an unchanged outside (" + ", ".join(unchanged) + ") use the base "
                          "views above: " + ", ".join(base) + "."]
    elif detail:
        lines += ["", "## Exterior views", "", "None rendered: the scene has no exterior camera (brief "
                  "`render.exterior_views: false`, or no place worked for any view)."]
    if manifest.get("variants"):
        vsheets = {}
        for vid, names in (manifest.get("variant_sheets") or {}).items():
            if names.get("interior"):
                vsheets[f"{vid}: interior views"] = names["interior"]
        lines += M.variants_lines(manifest["variants"], vsheets)
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
        ["interior / exterior views", f"{s.get('interior_views', s['views'])} / {s.get('exterior_views', 0)}"],
        ["variant", manifest.get("variant") or "base"],
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
        ["unit system", (manifest.get("units") or {}).get("system") or "-"],
        ["side-by-side sheets", len((manifest.get("side_by_side") or {}).get("sheets") or {})],
    ]
    lines += C.table(["item", "value"], rows)
    lines += m9_lines(manifest)
    lines += ["", "## Advisory flags and open items", ""]
    lines += C.bullets(manifest["advisory_flags"])
    lines += gate_validation_lines(manifest["gate_validation"], manifest["polish_allowed"],
                                   manifest["stages"]["polish"] != "not_run")
    lines += exterior_gate_lines(manifest)
    if manifest["contact_sheets"]:
        lines += ["", "## Contact sheets", ""]
        lines.append("Tiles: camera, `P` polished / `C` Cycles, `U<n>` unverified pieces in view.")
        for level, name in manifest["contact_sheets"].items():
            lines += ["", f"Level {level}: [{name}]({name})"]
    lines += side_by_side_lines(manifest)
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
    lines += m10_lines(manifest)
    lines += m7_building_lines(manifest)
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
    lines += m7_model_lines(manifest)
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
    sheets: Optional[dict] = None            # sheets.json of a project that stopped at the sheets stage (M10)


def review_inputs(project_out, out_dir=None, private: bool = False) -> Optional[ReviewInputs]:
    """The inputs of the needs-review report, or None when the project does not need review.

    Sources, in order: ``intake_manifest.json`` (status ``needs_review``: its reasons; the pipeline did not
    run, so an older ``building.json`` is ignored), ``sheets.json`` (Milestone 10: the sheets stage stopped the
    project, ``wenart.sheets`` exit 1: its ``needs_review[]`` reasons; no ``building.json`` was written, an
    older one is ignored), ``building.json`` (status ``needs_review``: its ``needs review: ...`` warnings, plus
    a failed schema validation), then this run's stage records with status ``needs_review`` of stages no
    manifest covers (their note). Records of earlier runs (``split_runs``) are only listed.

    The sheets stage stopped the project when this run's ``sheets`` record says ``needs_review``, or, without
    stage records (a hand run), when there is no ``building.json`` and ``sheets.json`` lists reasons. A
    ``sheets.json`` with reasons next to a ``building.json`` of this run (a level left out with
    ``failed_levels: leave_out``) is not a stop.
    """
    out = Path(project_out).resolve()
    w: list = []
    records, earlier, run_id = split_runs(load_stage_records(out, w))
    intake = C.read_json(out / "intake_manifest.json", w)
    building = C.read_json(out / "building.json", w)
    sheets = C.read_json(out / "sheets.json", w)
    sheets = sheets if isinstance(sheets, dict) and sheets.get("kind") in (None, "sheets") else None
    reasons: list[str] = []
    covered = set()
    sheets_stopped = False
    if isinstance(intake, dict):
        covered.add("intake")
        if intake.get("status") == "needs_review":
            reasons += [f"intake: {r}" for r in intake.get("reasons") or []] or ["intake: needs review"]
            if building is not None:
                w.append("building.json is from an earlier run (the pipeline did not run after the intake); "
                         "ignored")
            building = None
            sheets = None
            covered.update(r["stage"] for r in records)
    if sheets is not None:
        listed = [n for n in sheets.get("needs_review") or [] if isinstance(n, dict) and n.get("reason")]
        record = next((r for r in records if r["stage"] == "sheets"), None)
        stopped = (record is not None and record["status"] == "needs_review") or \
            (record is None and building is None and bool(listed))
        if stopped:
            sheets_stopped = True
            covered.add("sheets")
            reasons += [f"sheets: {n['reason']}" for n in listed] or \
                [f"sheets: {(record or {}).get('note') or 'the sheets stage needs review'}"]
            if building is not None:
                w.append("building.json is from an earlier run (the sheets stage stopped the project); ignored")
            building = None
    if not sheets_stopped:
        sheets = None
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
                        project=str(name or (sheets or {}).get("project") or out.name),
                        private=is_private(out, private), reasons=reasons,
                        building=building, report_md=report_md, intake=intake if isinstance(intake, dict) else None,
                        records=records, warnings=w, earlier=earlier, run_id=run_id, sheets=sheets)


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


def write_debug_previews(project_out: Path, out_dir: Path, private: bool, warnings: list, docs: list[dict]) -> list[dict]:
    """Debug images of the rows in ``docs`` (``debug_image`` = path relative to the project output) as JPEG
    <= 300 KB under ``out_dir/debug/`` (public projects); a private project's debug images are only named. Sets
    ``debug_preview`` on every row; returns ``[{source, preview, bytes}]``."""
    out = []
    seen = set()
    for row in docs:
        rel_src = row.get("debug_image")
        if not rel_src or rel_src in seen:
            continue
        seen.add(rel_src)
        src = Path(project_out) / rel_src
        entry = {"source": rel_src, "preview": None, "bytes": None}
        if private:
            entry["kept_on_volume"] = True
        elif not src.is_file():
            warnings.append(f"debug image {rel_src} not found")
        else:
            rgb = _load_rgb(src)
            if rgb is None:
                warnings.append(f"debug image {rel_src} unreadable")
            else:
                name = f"{DEBUG_DIR}/{Path(rel_src).stem}.jpg"
                info = C.save_jpeg_under(rgb, Path(out_dir) / name)
                entry.update(preview=name, bytes=info["bytes"])
        out.append(entry)
        for r in docs:
            if r.get("debug_image") == rel_src:
                r["debug_preview"] = entry["preview"]
    return out


def write_review_images(ri: ReviewInputs, docs: list[dict]) -> list[dict]:
    """Debug images of the pages as JPEG <= 300 KB under ``final/debug/`` (public projects); a private
    project's debug images are only named (paths relative to the project output)."""
    out = write_debug_previews(ri.project_out, ri.out_dir, ri.private, ri.warnings, docs)
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


SHEETS_REPORT = "sheets_report.md"


def sheet_image_rows(sheets: Optional[dict], private: bool) -> list[dict]:
    """One row per sheet of ``sheets.json`` that has a debug image (``sheets_debug/<file>_<sheet>.png``, relative
    to the project output), shaped like ``document_rows`` so ``write_review_images`` handles both."""
    rows = []
    docs = [d for d in (sheets or {}).get("documents") or [] if isinstance(d, dict)]
    for i, d in enumerate(docs, start=1):
        for s in d.get("sheets") or []:
            if isinstance(s, dict) and s.get("debug_image"):
                rows.append({"file": _doc_name(d.get("file"), i, private), "page": s.get("id"), "class": "sheet",
                             "debug_image": s["debug_image"], "debug_preview": None})
    return rows


def sheet_names(sheets: Optional[dict], private: bool) -> dict:
    """``{file: shown name}`` of the documents of ``sheets.json`` (a private project's are numbered)."""
    docs = [d for d in (sheets or {}).get("documents") or [] if isinstance(d, dict)]
    return {d.get("file"): _doc_name(d.get("file"), i, private) for i, d in enumerate(docs, start=1)}


def sheets_summary(ri: ReviewInputs, sheet_rows: list[dict]) -> Optional[dict]:
    """The Sheets block of a needs-review report (None when the project did not stop at the sheets stage):
    regions with class, how it was decided, level, variant and use; strays; unit checks; the stop reasons;
    conflicts and warnings; the debug images. A private project's documents are numbered, never named."""
    sh = ri.sheets
    if not isinstance(sh, dict):
        return None
    return M.sheets_block(sh, ri.private, sheet_names(sh, ri.private),
                          {r["debug_image"]: r.get("debug_preview") for r in sheet_rows})


def build_review_manifest(ri: ReviewInputs, docs: list[dict], images: list[dict],
                          sheets: Optional[dict] = None) -> dict:
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
        "sheets": sheets,
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


def sheets_lines(sheets: dict, private: bool) -> list[str]:
    """The "Sheets" section of a needs-review report (a project the sheets stage stopped)."""
    return M.sheets_lines(sheets, private, stopped=True)


def review_markdown(manifest: dict, report_md_table: list[str]) -> str:
    """``final_report.md`` of a needs-review project (links only to files in ``final/``)."""
    lines = [f"# Final report: {manifest['project']} (needs review)", ""]
    lines.append("Status: **needs_review**. The project stopped before the 3D stages: nothing was built, rendered "
                 "or polished in this run, and nothing was guessed or filled in. Every reason is listed below; after "
                 "fixing them, run the project again.")
    lines += ["", "## Reasons", ""] + C.bullets(manifest["reasons"])
    if manifest["hints"]:
        lines += ["", "## What to do", ""] + C.bullets(manifest["hints"])
    sheets = manifest.get("sheets")
    if sheets:
        lines += sheets_lines(sheets, manifest["private"])
    lines += ["", "## Documents and pages", ""]
    docs = manifest["documents"]
    if sheets and not docs:
        lines.append("The project stopped at the sheets stage: no document page was read as a plan yet "
                     "(see Sheets above).")
    elif docs:
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
    sheet_rows = sheet_image_rows(ri.sheets, ri.private)
    images = write_review_images(ri, docs + sheet_rows)
    sheets = sheets_summary(ri, sheet_rows)
    if sheets is not None:
        report = ri.project_out / SHEETS_REPORT
        if not report.is_file():
            ri.warnings.append(f"{SHEETS_REPORT} not found next to sheets.json")
        elif ri.private:
            sheets["report_kept_on_volume"] = SHEETS_REPORT
        else:
            shutil.copyfile(report, ri.out_dir / SHEETS_REPORT)
            sheets["report"] = SHEETS_REPORT
    manifest = build_review_manifest(ri, docs, images, sheets)
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
