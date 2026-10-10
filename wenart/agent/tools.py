"""The tool API of the agent (docs/milestone11.md §3).

What: ``build_registry()`` returns the ``Registry`` of every tool: name, description, JSON schema of the input,
handler -> JSON output, and the stage an edit touches. Read tools (§3.1) have no side effects; edit tools (§3.2)
are validated by code before they are accepted and every accepted edit becomes one entry of ``overrides.json``.

| kind | tools |
|---|---|
| read | building_summary, room, room_topdown, plan_crop, plausibility, view, exterior_summary, catalog, stage_status |
| furniture edit (``edit_ops.apply_edit``) | move_piece, rotate_piece, resize_piece, change_type, swap_model, add_piece, add_group, remove_piece, relayout_room, set_room_type |
| override edit (``blender.exterior_checks`` validators) | set_camera, add_camera, remove_camera, set_material, set_exterior |
| record-only edit | correct_geometry (``geometry_fix``), rerun_stage (white list) |
| control | finish |

Why: the model writes no code and runs no command; it can only call these tools. A call whose arguments do not
match the schema is refused with the schema error (and counted against the round's budget, §3).

How: the furniture tools take ``EDIT_SCHEMAS[op]`` of track B as their parameters (+ ``reason``), the camera and
exterior tools ``CAMERA_/EXTERIOR_OVERRIDE_SCHEMA`` of track C; while a track's table is still empty (its stub)
the fallback schemas below (from §3.2) are used, so the registry is complete either way. Every edit result is
``{accepted, failed_checks, score_before, score_after, overrides_id, rerun_from, message, changed_ids}`` (§3.2).
A validator that is not built yet (``NotImplementedError``) rejects the edit with ``validator_unavailable``. The
same target is edited at most ``MAX_TRIES`` = 3 times per round (§3.2, §14). Images a read tool makes or finds
are put in ``ctx.pending_images``; the loop shows them to the model in the next message.

Milestone 12 (docs/milestone12.md §5.2–§5.4, D17–D19):

| kind | new tools |
|---|---|
| read | ``room_brief`` (``brief.room_brief``: replaces ``room`` + ``plausibility`` for the planner), ``levels`` (marks, floors, thresholds, ground, terrain, entrances, L-findings) |
| group edit (``edit_ops.apply_edit``, track G) | ``relayout_room`` (with a solver ``candidate``), ``place_group``, ``complete_group``, ``move_group``, ``retype_piece``, ``mark_not_furniture``, ``fix_fixture``, ``set_front`` |
| level edit (``levels.edits.apply_level_edit``, track L) | ``set_mark_kind``, ``set_room_floor``, ``set_ground_point``, ``set_entrance``, ``set_terrain`` |
| record-only | ``report_library_gap`` (into ``agent_overrides.library_gaps``) |
| free | ``dry_run`` (the validator's answer without applying it; no try is counted, nothing is stored) |

Every accepted building edit is followed by ``decor.sync_to_hosts`` (track S: the decor follows its host, B3) and
its result carries the room's group checks after the edit (with their numbers). An edit identical to one rejected
earlier in the same room (``memory.Memory``, any round) is refused before any validator call (``failed_checks``
``memory: ...``). Track G's ops validate every edit; with a validator that lacks them (an older one, a test fake),
``set_front`` / ``retype_piece`` / ``mark_not_furniture`` are
validated as their M11 ops (``overrides.resolve_edit``). The planner is offered ``PLANNER_TOOLS`` (the M12 set);
the M11 tools stay callable for replay and old scripts. The context is shared by the parallel room sessions of one
round: building changes, tries, overrides and the log are guarded by ``ctx.lock``; the images a read tool returns
and ``finish`` belong to the calling session (thread-local).
"""
from __future__ import annotations

import copy
import itertools
import json
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from wenart.agent import brief as BR
from wenart.agent import geometry_fix as GF
from wenart.agent import log as LG
from wenart.agent import overrides as OV
from wenart.agent import topdown as TD
from wenart.agent.model import tool_spec

MAX_TRIES = 3
PREVIEW_DIR = "agent/previews"         # the round previews (960x540, 32 samples)
FINAL_RENDER_DIR = "renders"
EDIT_META = ("op", "round", "log_seq", "model")
# rerun_stage white list (§3.2): stage -> {setting: JSON schema of its value}. The scheduler honours
# polish.enabled (false: the project's views keep Cycles); the other stages are re-run as they are.
RERUN_WHITELIST: dict = {"refit": {}, "build": {}, "polish": {"enabled": {"type": "boolean"}}}

REASON = {"type": "string", "minLength": 3, "description": "why (one sentence, logged and shown in the report)"}
ID = {"type": "string", "minLength": 1}
XY = {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}
XYZ = {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}


def _obj(props: dict, required: list) -> dict:
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


# §3.2 inputs, used while track B's EDIT_SCHEMAS has no entry for an op.
FALLBACK_EDIT_SCHEMAS: dict = {
    "move": _obj({"piece_id": ID, "center": XY, "snap_wall_id": ID,
                  "offset": {"type": "number", "description": "metres along the wall from its start"}}, ["piece_id"]),
    "rotate": _obj({"piece_id": ID, "front_deg": {"type": "number", "description": "the direction the front faces, "
                                                  "degrees counter-clockwise from +x"}}, ["piece_id", "front_deg"]),
    "resize": _obj({"piece_id": ID, "size": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                                             "minItems": 2, "maxItems": 3}}, ["piece_id", "size"]),
    "change_type": _obj({"piece_id": ID, "type": ID}, ["piece_id", "type"]),
    "swap_model": _obj({"piece_id": ID, "asset_id": ID}, ["piece_id", "asset_id"]),
    "add": _obj({"room_id": ID, "type": ID, "anchor": {"type": "object"}}, ["room_id", "type"]),
    "add_group": _obj({"room_id": ID, "group": {"enum": ["dining_set", "bed_set", "living_set", "desk_set",
                                                         "kitchen_run"]},
                       "anchor": {"type": "object"}}, ["room_id", "group"]),
    "remove": _obj({"piece_id": ID, "evidence": {"type": "string"}}, ["piece_id"]),
    "relayout_room": _obj({"room_id": ID, "candidate": {"type": "integer", "minimum": 1, "maximum": 3,
                                                        "description": "the rank of the solver candidate to take "
                                                                       "(see the room brief)"}}, ["room_id"]),
    "set_room_type": _obj({"room_id": ID, "type": ID}, ["room_id", "type"]),
    # Milestone 12 (§5.3), used while track G's EDIT_SCHEMAS has no entry for these ops.
    "place_group": _obj({"room_id": ID, "group": {"type": "string", "description": "a group of the room's program "
                                                                                  "(groups.yaml name)"},
                         "option": {"type": "string", "description": "one of the group's program options"}},
                        ["room_id", "group"]),
    "complete_group": _obj({"group_id": ID}, ["group_id"]),
    "move_group": _obj({"group_id": ID, "span_id": {"type": "string", "description": "a free wall span id of the "
                                                                                     "room brief"},
                        "offset": {"type": "number", "description": "metres along the span from its start"}},
                       ["group_id", "span_id"]),
    "retype_piece": _obj({"piece_id": ID, "type": ID}, ["piece_id", "type"]),
    "mark_not_furniture": _obj({"piece_id": ID, "kind": {"enum": ["level_mark", "room_number", "north_arrow",
                                                                  "axis_bubble", "section_mark", "door_arc",
                                                                  "dimension", "text_frame", "line", "other"]},
                                "evidence": {"type": "string", "minLength": 3}}, ["piece_id", "kind", "evidence"]),
    "fix_fixture": _obj({"piece_id": ID, "size": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                                                  "minItems": 2, "maxItems": 2,
                                                  "description": "a real product size [w, d] of its type"},
                         "center": dict(XY, description="a new centre at most 0.5 m away")}, ["piece_id"]),
    "set_front": _obj({"piece_id": ID, "front_deg": {"type": "number", "minimum": 0, "maximum": 360}},
                      ["piece_id", "front_deg"]),
}
LIBRARY_GAP_SCHEMA = _obj({"type": ID, "style": {"type": "string"}, "piece_id": ID}, ["type"])
FALLBACK_CAMERA_SCHEMA = _obj({"view_id": ID, "kind": {"enum": ["interior", "exterior"]}, "room_id": ID,
                               "position": XYZ, "target": XYZ, "lens_mm": {"type": "number", "minimum": 10,
                                                                           "maximum": 85}},
                              ["view_id", "kind", "position", "target", "lens_mm"])
FALLBACK_EXTERIOR_SCHEMA = _obj({
    "roof": _obj({"type": {"type": "string"}, "pitch_deg": {"type": "number"}, "overhang_m": {"type": "number"}}, []),
    "ground": {"type": "string", "description": "look id of the ground"},
    "site": _obj({"path": {"type": "boolean"}, "fence": {"type": "boolean"}, "trees": {"type": "integer"},
                  "front_court": {"enum": ["auto", "yes", "no"]}}, []),
    "sun": _obj({"azimuth_deg": {"type": "number"}, "elevation_deg": {"type": "number"}}, [])}, [])
LIGHTING_FACTOR = (0.5, 3.0)      # set_lighting: the room light power times this (real03: a black floor hall)
LIGHTING_SCHEMA = _obj({"room_id": ID,
                        "factor": {"type": "number", "minimum": LIGHTING_FACTOR[0], "maximum": LIGHTING_FACTOR[1],
                                   "description": "room light power x factor (1 = as assumed); a room with a factor "
                                                  "gets ceiling lights even when it has daylight"}},
                       ["room_id", "factor"])
MATERIAL_SCHEMA = _obj({"slot": {"type": "string", "description": "walls, floor, wet_walls, kitchen_walls, facade, "
                                                                  "roof, ground, frames, ..."},
                        "look_id": ID}, ["slot", "look_id"])

DESCRIPTIONS = {
    "building_summary": "Levels, rooms (type, name, area, status, ceiling), counts and open conflicts.",
    "room": "One room: polygon, walls with ids, doors (width, swing), windows (sill, head), pieces (id, type, "
            "footprint, front_deg, source, labels, failed checks).",
    "room_topdown": "A top-down image of the room: pieces with front arrows and ids, door swings, window bands, "
                    "failed checks in red.",
    "plan_crop": "The source plan crop of a room or of the room of a piece (what the drawing shows).",
    "plausibility": "Plausibility score 0-100 and the violations of the checklist, for a room or the building.",
    "view": "One camera view: its preview image, camera position, target and lens, the visible elements.",
    "exterior_summary": "Outline, levels, roof, openings, site, sun and the exterior cameras.",
    "catalog": "Library models of a furniture type with their real sizes and style tags.",
    "stage_status": "Status, seconds and notes of the pipeline stages.",
    "move_piece": "Move a piece to a new centre, or snap its back to a wall (snap_wall_id, offset).",
    "rotate_piece": "Turn a piece so its front faces front_deg.",
    "resize_piece": "Resize a piece to a real product size.",
    "change_type": "Change a piece's type (within the types of the room type).",
    "swap_model": "Use another library model for a piece.",
    "add_piece": "Add one piece to a room (placed by the layout engine).",
    "add_group": "Add a functional group (dining_set, bed_set, living_set, desk_set, kitchen_run) to a room.",
    "remove_piece": "Remove a piece. A drawn piece only when it is clearly not furniture (give the evidence).",
    "relayout_room": "Re-place the AI pieces of a room (drawn pieces stay locked).",
    "set_room_type": "Change a room's type when it does not fit its area, fixtures and doors.",
    "set_camera": "Move an existing camera (position, target, lens).",
    "add_camera": "Add a camera view.",
    "remove_camera": "Remove a camera view (e.g. a view of a bare wall).",
    "set_material": "Set the look of a material slot (walls, floor, wet walls, kitchen walls, facade, roof, ground, "
                    "frames ...).",
    "set_exterior": "Change the roof (type, pitch, overhang), ground, site items or the sun.",
    "set_lighting": "Make a room's ceiling lights stronger or weaker (factor 0.5-3; a dark or windowless room, a long "
                    "corridor). Long rooms already get one light per 3 m of length.",
    "correct_geometry": "Record a clear geometry error: close a gap <= 0.15 m, merge a duplicate wall within 0.02 m, "
                        "put an opening <= 0.10 m off its wall back on it.",
    "rerun_stage": "Re-run a stage with white-listed settings (e.g. polish enabled false).",
    "finish": "End this round: your verdict and the findings that stay open.",
    # Milestone 12 (§5.2, §5.3, §3.6)
    "room_brief": "The room brief: built pieces with lock state and allowed tools, groups, free wall spans, fixable "
                  "and not-yours findings, memory, solver candidates.",
    "levels": "Level marks, room floor levels, door thresholds, ground points, terrain, entrances and the level "
              "findings.",
    "place_group": "Add a missing functional group of the room's program; the solver places it.",
    "complete_group": "Add the missing partners of a group (e.g. the second nightstand); the solver places them.",
    "move_group": "Move a whole group to a free wall span (partners follow).",
    "retype_piece": "Change a piece's type to a type that fits its size and its room (zone).",
    "mark_not_furniture": "Record a drawn symbol, mark or line that was read as furniture (not built), with the "
                          "evidence.",
    "fix_fixture": "Misread fixed equipment: a real product size and/or a move of at most 0.5 m (through a wall, in "
                   "a door swing).",
    "set_front": "Give a drawn piece without a front (front_inferred) the direction its front faces (degrees "
                 "counter-clockwise from +x, along a side of its footprint); to turn a piece use rotate_piece.",
    "set_mark_kind": "Correct the kind of a level mark (with the reason).",
    "set_room_floor": "Set a room's floor level from a mark or a drawn step line.",
    "set_ground_point": "Add or correct a ground point (x, y, z) with its evidence.",
    "set_entrance": "Choose the solution at an outside door: none, steps, ramp, steps and ramp.",
    "set_terrain": "Choose the terrain model: flat, planar or tin.",
    "report_library_gap": "Record that no audited library model of a type and style exists (a library gap).",
    "dry_run": "Ask the validator about an edit WITHOUT applying it (free: no try is counted): accepted or the failed "
               "checks with their numbers.",
}
STAGE_OF = {"set_camera": "build", "add_camera": "build", "remove_camera": "build", "set_material": "build",
            "set_exterior": "build", "set_lighting": "build", "correct_geometry": "pipeline_final"}
# The tools offered to the M12 planner (§5.3): the M11 piece tools that the group tools replace (add_piece,
# add_group, change_type) and the M11 reads that the brief replaces (room, plausibility) stay callable for replay but
# are not offered. rotate_piece turns a piece (track G: set_front only gives a front to a piece without one).
PLANNER_READS = ("room_brief", "room_topdown", "plan_crop", "view", "levels", "catalog")
PLANNER_ROOM_EDITS = ("relayout_room", "place_group", "complete_group", "move_group", "move_piece", "rotate_piece",
                      "set_front", "resize_piece", "retype_piece", "mark_not_furniture", "fix_fixture", "remove_piece",
                      "swap_model", "set_room_type", "set_lighting", "report_library_gap")
PLANNER_BUILDING = ("building_summary", "exterior_summary", "set_exterior", "set_material", "set_camera",
                    "add_camera", "remove_camera", "correct_geometry", "rerun_stage", *OV.LEVEL_TOOLS)
PLANNER_CONTROL = ("dry_run", "finish")
PLANNER_TOOLS = PLANNER_READS + PLANNER_ROOM_EDITS + PLANNER_BUILDING + PLANNER_CONTROL


# --------------------------------------------------------------------------
# Context
# --------------------------------------------------------------------------

def read_json(path) -> Optional[dict]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def working_building_path(project_out) -> Optional[Path]:
    """The building the edits apply to: ``building_agent.json`` (decor + the accepted edits) when it exists, else
    ``building_decor.json``, else ``building_final.json`` (a project without the decor stage)."""
    out = Path(project_out)
    for name in (OV.AGENT_BUILDING, OV.DECOR_BUILDING, "building_final.json"):
        if (out / name).is_file():
            return out / name
    return None


class SessionState:
    """What belongs to one planner session (one thread): the images its tools returned, its ``finish``."""

    def __init__(self, room_id: Optional[str] = None):
        self.room_id = room_id
        self.pending_images: list = []
        self.finished: Optional[dict] = None


@dataclass
class ToolContext:
    """What the tools of one round see and change (one per round, shared by its parallel room sessions)."""
    project_out: Path
    building: dict
    round: int = 1
    model_id: str = ""
    log: Optional[LG.AgentLog] = None
    overrides: Optional[OV.Overrides] = None
    scene: dict = field(default_factory=dict)
    style: dict = field(default_factory=dict)
    preview_dir: str = PREVIEW_DIR
    violations: list = field(default_factory=list)       # code findings of the round (red in the top-down images)
    apply_edit: Optional[Callable] = None                # wenart.furniture.edit_ops.apply_edit (injectable)
    validators: Any = None                               # wenart.blender.exterior_checks (injectable)
    plausibility: Any = None                             # wenart.furniture.plausibility (injectable)
    catalog_loader: Optional[Callable] = None
    tries: dict = field(default_factory=dict)
    accepted: list = field(default_factory=list)          # [{tool, args, result}] of the round
    rejected: list = field(default_factory=list)
    schema_errors: int = 0
    max_tries: int = MAX_TRIES
    image_n: int = 0
    _catalog: Any = None
    # Milestone 12 (§5.2-§5.4)
    memory: Any = None                                   # wenart.agent.memory.Memory
    findings: list = field(default_factory=list)          # the round's findings (code + kept vision) for the briefs
    level_edit: Optional[Callable] = None                # wenart.levels.edits.apply_level_edit (injectable)
    level_checks: Optional[Callable] = None              # wenart.levels.checks.check_levels (injectable)
    sync: Optional[Callable] = None                      # wenart.furniture.decor.sync_to_hosts (injectable)
    brief_fns: dict = field(default_factory=dict)         # room_brief's *_fn arguments (tests inject fakes)
    dry_runs: int = 0
    refused_repeats: int = 0
    _default_session: Any = None
    _local: Any = None
    _lock: Any = None
    _counter: Any = None

    def __post_init__(self):
        self._default_session = SessionState()
        self._local = threading.local()
        self._lock = threading.RLock()
        self._counter = itertools.count(self.image_n + 1)

    # ----- the calling session (thread-local) --------------------------------------------------------------

    @property
    def lock(self):
        return self._lock

    def session(self) -> SessionState:
        return getattr(self._local, "session", None) or self._default_session

    def begin_session(self, room_id: Optional[str]) -> SessionState:
        state = SessionState(room_id)
        self._local.session = state
        return state

    def end_session(self) -> None:
        self._local.session = None

    @property
    def pending_images(self) -> list:
        return self.session().pending_images

    @property
    def finished(self) -> Optional[dict]:
        return self.session().finished

    @finished.setter
    def finished(self, value: Optional[dict]) -> None:
        self.session().finished = value

    @classmethod
    def load(cls, project_out, **kwargs) -> "ToolContext":
        out = Path(project_out)
        path = working_building_path(out)
        building = read_json(path) if path is not None else None
        if building is None:
            raise FileNotFoundError(f"no building JSON in {out}")
        scene = read_json(out / "scene" / "scene_manifest.json") or {}
        style = read_json(out / "style.json") or {}
        return cls(project_out=out, building=building, scene=scene, style=style, **kwargs)

    # ----- lazy modules (the other tracks' functions; tests inject fakes) ---------------------------------

    def edit_fn(self) -> Callable:
        if self.apply_edit is None:
            from wenart.furniture import edit_ops
            self.apply_edit = edit_ops.apply_edit
        return self.apply_edit

    def checks(self):
        if self.validators is None:
            from wenart.blender import exterior_checks
            self.validators = exterior_checks
        return self.validators

    def plaus(self):
        if self.plausibility is None:
            from wenart.furniture import plausibility
            self.plausibility = plausibility
        return self.plausibility

    def catalog(self):
        if self._catalog is None:
            if self.catalog_loader is not None:
                self._catalog = self.catalog_loader()
            else:
                from wenart.furniture import catalog as CAT
                self._catalog = CAT.load()
        return self._catalog

    def level_fn(self) -> Callable:
        if self.level_edit is None:
            from wenart.levels import edits
            self.level_edit = edits.apply_level_edit
        return self.level_edit

    def level_check_fn(self) -> Callable:
        if self.level_checks is None:
            from wenart.levels import checks
            self.level_checks = checks.check_levels
        return self.level_checks

    def sync_fn(self) -> Callable:
        return self.sync or OV.sync_decor

    def known_ops(self) -> tuple:
        """The ops the edit validator knows: every op when a validator is injected (tests), else track G's."""
        return tuple(OV.FURNITURE_TOOLS.values()) if self.apply_edit is not None else OV.known_ops()

    def group_checks_of(self, room_id: Optional[str]) -> list[str]:
        """The room's group checks now, as lines with their numbers (the edit results show them)."""
        if not room_id:
            return []
        fn = self.brief_fns.get("group_checks_fn")
        try:
            if fn is None:
                from wenart.furniture import group_checks
                fn = group_checks.check_room
            return [f"{v.get('check')} {v.get('severity')} {v.get('target')}: {v.get('message')}"
                    for v in fn(self.building, room_id) or []][:12]
        except Exception:  # noqa: BLE001 - the checks are information here, never a reason to fail the edit
            return []

    # ----- lookups -------------------------------------------------------------------

    def room(self, room_id: str) -> Optional[dict]:
        return next((r for r in self.building.get("rooms") or [] if r.get("id") == room_id), None)

    def piece(self, piece_id: str) -> Optional[dict]:
        return next((f for f in self.building.get("furniture") or [] if f.get("id") == piece_id), None)

    def cameras(self) -> list[dict]:
        return [c for c in self.scene.get("cameras") or [] if isinstance(c, dict)]

    def camera(self, view_id: str) -> Optional[dict]:
        return next((c for c in self.cameras() if c.get("name") == view_id), None)

    def images_dir(self) -> Path:
        if self.log is not None:
            return self.log.images_dir
        path = LG.orchestrator_dir(self.project_out) / LG.IMAGES_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    def rel(self, path) -> Optional[str]:
        return self.log.rel(path) if self.log is not None else (str(path) if path is not None else None)

    def image_name(self, what: str) -> Path:
        n = next(self._counter)
        self.image_n = max(self.image_n, n)
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in what)
        return self.images_dir() / f"r{self.round}_{n:03d}_{safe}.png"

    def candidate_image(self, room_id: str, rank: int, candidate: dict) -> Optional[str]:
        """The top-down image of solver candidate ``rank`` (``topdown.draw_candidate``), its log-relative id."""
        try:
            apply_fn = self.brief_fns.get("apply_candidate_fn")
            path = TD.draw_candidate(self.building, room_id, candidate, self.image_name(f"cand{rank}_{room_id}"),
                                     apply_fn=apply_fn)
        except Exception:  # noqa: BLE001 - a candidate without an image is still listed
            return None
        return self.rel(path)

    def brief(self, room_id: str) -> dict:
        """The room brief (``brief.room_brief``) with this round's findings of the room and the memory."""
        from wenart.agent import brief as BRF
        fns = {k: v for k, v in self.brief_fns.items() if k.endswith("_fn") and k != "apply_candidate_fn"}
        return BRF.room_brief(self.building, room_id, findings=BRF.findings_of_room(self.findings, self.building,
                                                                                   room_id),
                              memory=self.memory, image_of=lambda rank, c: self.candidate_image(room_id, rank, c),
                              **fns)

    def topdown(self, room_id: str, building: Optional[dict] = None, what: str = "topdown",
                annotate: bool = True) -> Optional[Path]:
        try:
            room_violations = [v for v in self.violations if v.get("room_id") == room_id or v.get("target") == room_id]
            return TD.draw_room(building or self.building, room_id, self.image_name(f"{what}_{room_id}"),
                                room_violations, annotate=annotate)
        except Exception:  # noqa: BLE001 - an image that cannot be drawn is no reason to fail the edit
            return None

    def preview_path(self, view_id: str) -> Optional[Path]:
        for folder in (self.preview_dir, FINAL_RENDER_DIR):
            p = self.project_out / folder / f"{view_id}_preview.jpg"
            if p.is_file():
                return p
        return None

    def plan_crop_path(self, room_id: str) -> Optional[Path]:
        """An existing plan crop of the room (M11 step 3: take what exists): ``check/<cam>_plan.jpg``, then
        ``final/<cam>_plan.jpg`` of the room's cameras, then a debug image of the room's level."""
        cams = [c.get("name") for c in self.cameras() if c.get("room_id") == room_id]
        for folder in ("check", "final"):
            for cam in cams:
                p = self.project_out / folder / f"{cam}_plan.jpg"
                if p.is_file():
                    return p
        room = self.room(room_id) or {}
        for folder in ("debug", "final/debug"):
            found = sorted((self.project_out / folder).glob("*.jpg")) if (self.project_out / folder).is_dir() else []
            level = str(room.get("level_id") or "")
            pick = [p for p in found if level and level.lower() in p.name.lower()] or found
            if pick:
                return pick[0]
        return None

    def room_of(self, target: Optional[str]) -> Optional[str]:
        if not target:
            return None
        if self.room(target) is not None:
            return target
        piece = self.piece(target)
        if piece is not None:
            return piece.get("room_id")
        cam = self.camera(target)
        if cam is not None:
            return cam.get("room_id")
        return None


@dataclass
class Tool:
    name: str
    kind: str                    # read | furniture | override | record | control
    description: str
    parameters: dict
    handler: Callable[[ToolContext, dict], dict]
    stage: Optional[str] = None  # the stage an accepted edit re-runs from (furniture: from the result)

    def spec(self) -> dict:
        return tool_spec(self.name, self.description, self.parameters)


class Registry:
    def __init__(self, tools: list[Tool]):
        self.tools = {t.name: t for t in tools}

    def names(self) -> list[str]:
        return list(self.tools)

    def specs(self, names=None) -> list[dict]:
        """The tool specs (all, or ``names`` in that order: the M12 planner gets ``PLANNER_TOOLS`` or a subset)."""
        if names is None:
            return [t.spec() for t in self.tools.values()]
        return [self.tools[n].spec() for n in names if n in self.tools]

    def call(self, ctx: ToolContext, name: str, args: Optional[dict], parse_error: Optional[str] = None) -> dict:
        """Run one tool call; a bad call returns ``{"error", "schema_error": true}`` and counts in
        ``ctx.schema_errors``. Milestone 12: an edit identical to one rejected earlier in the same room (the memory)
        is refused without running it; every validated edit is recorded in the memory."""
        from wenart.recognition.vlm_client import schema_errors
        tool = self.tools.get(name)
        if tool is None:
            with ctx.lock:
                ctx.schema_errors += 1
            return {"error": f"unknown tool {name!r}; the tools are: {', '.join(self.tools)}", "schema_error": True}
        if parse_error:
            with ctx.lock:
                ctx.schema_errors += 1
            return {"error": f"bad arguments for {name}: {parse_error}", "schema_error": True}
        errors = schema_errors(tool.parameters, args if args is not None else {})
        if errors:
            with ctx.lock:
                ctx.schema_errors += 1
            return {"error": f"the arguments of {name} do not match its schema: " + "; ".join(errors[:5]),
                    "schema_error": True}
        args = dict(args or {})
        remember = tool.kind in EDIT_KINDS and ctx.memory is not None
        room = edit_room(ctx, args) if remember else None
        if remember:
            prev = ctx.memory.repeat_of(room, name, args)
            if prev is not None:
                ctx.memory.refused()
                with ctx.lock:
                    ctx.refused_repeats += 1
                out = _result(False, [f"memory: the same edit was rejected in round {prev.get('round')}: "
                                      + "; ".join(prev.get("reasons") or ["rejected"])[:300]],
                              message="refused without validation: this exact edit was rejected before; try "
                                      "something else", refused_by_memory=True)
                return _reject(ctx, name, args, out)
        try:
            res = tool.handler(ctx, args)
        except Exception as exc:  # noqa: BLE001 - the model sees the error and may try another way
            return {"error": f"{name} failed: {type(exc).__name__}: {exc}"}
        failed = list(res.get("failed_checks") or [])
        if remember and "accepted" in res and not (failed and (failed[0].startswith("max_tries")
                                                              or failed[0] == "validator_unavailable")):
            ctx.memory.record(room, ctx.round, name, args, res)
        return res


# --------------------------------------------------------------------------
# Read tools (§3.1)
# --------------------------------------------------------------------------

def _round(v, n=3):
    try:
        return round(float(v), n)
    except (TypeError, ValueError):
        return v


def t_building_summary(ctx: ToolContext, args: dict) -> dict:
    b = ctx.building
    level = args.get("level")
    levels = [{"id": lv.get("id"), "label": lv.get("label"), "elevation": lv.get("elevation"),
               "ceiling_height": lv.get("ceiling_height")} for lv in b.get("levels") or []]
    furniture = b.get("furniture") or []
    rooms = []
    for r in b.get("rooms") or []:
        if level and r.get("level_id") != level:
            continue
        rooms.append({"id": r.get("id"), "label": r.get("label"), "type": r.get("room_type"),
                      "level_id": r.get("level_id"), "area": _round(r.get("area_computed"), 2),
                      "status": r.get("status"), "ceiling": r.get("ceiling_height"),
                      "pieces": sum(1 for f in furniture if f.get("room_id") == r.get("id"))})
    by_source: dict = {}
    for f in furniture:
        by_source[str(f.get("source"))] = by_source.get(str(f.get("source")), 0) + 1
    return {"levels": levels, "rooms": rooms,
            "counts": {"rooms": len(b.get("rooms") or []), "walls": len(b.get("walls") or []),
                       "openings": len(b.get("openings") or []), "furniture": by_source},
            "conflicts": list(b.get("conflicts") or [])[:20], "unverified": len(b.get("unverified") or [])}


def _room_walls(ctx: ToolContext, room: dict) -> list[dict]:
    from shapely.geometry import LineString, Polygon
    ring = Polygon(room["polygon"]).exterior
    out = []
    for w in ctx.building.get("walls") or []:
        if w.get("level_id") != room.get("level_id"):
            continue
        line = LineString([w["start"], w["end"]])
        if line.length < 1e-6:
            continue
        near = float(w.get("thickness") or 0.2) / 2.0 + 0.08
        if ring.distance(line.interpolate(0.5, normalized=True)) <= near:
            out.append({"id": w.get("id"), "start": w.get("start"), "end": w.get("end"),
                        "thickness": w.get("thickness"), "exterior": w.get("exterior")})
    return out


def t_room(ctx: ToolContext, args: dict) -> dict:
    room = ctx.room(args["room_id"])
    if room is None:
        return {"error": f"no room {args['room_id']}"}
    from wenart.furniture import placer
    doors, windows = placer.room_openings(ctx.building, room)
    swings: dict = {}
    try:
        rc = placer.room_context(ctx.building, room)
        swings = {d.id: [[_round(x), _round(y)] for x, y in d.swing.exterior.coords]
                  for d in rc.doors if d.swing is not None and not d.swing.is_empty and d.swing.geom_type == "Polygon"}
    except Exception:  # noqa: BLE001 - a room without a usable context still lists its openings
        pass
    fails: dict = {}
    for v in ctx.violations:
        fails.setdefault(v.get("target"), []).append(f"{v.get('check')} {v.get('severity')}: {v.get('message')}")
    pieces = []
    for f in TD.room_pieces(ctx.building, room["id"]):
        labels = [k for k in ("adjusted_by_ai", "inferred", "modified_by_ai", "completes_room") if f.get(k)]
        pieces.append({"id": f.get("id"), "type": f.get("type"), "source": f.get("source"),
                       "footprint": f.get("footprint"), "front_deg": f.get("front_deg"), "height": f.get("height"),
                       "status": f.get("status"), "labels": labels, "checks": fails.get(f.get("id"), [])})
    return {"id": room["id"], "label": room.get("label"), "type": room.get("room_type"),
            "level_id": room.get("level_id"), "area": _round(room.get("area_computed"), 2),
            "polygon": room.get("polygon"), "walls": _room_walls(ctx, room),
            "doors": [{"id": d.get("id"), "width": d.get("width"), "wall_id": d.get("wall_id"),
                       "center": d.get("center"), "swing_side": d.get("swing_side"),
                       "swing_polygon": swings.get(d.get("id"))} for d in doors],
            "windows": [{"id": w.get("id"), "width": w.get("width"), "wall_id": w.get("wall_id"),
                         "center": w.get("center"), "sill": w.get("sill_height"), "head": w.get("height")}
                        for w in windows],
            "pieces": pieces, "checks": fails.get(room["id"], [])}


def t_room_topdown(ctx: ToolContext, args: dict) -> dict:
    if ctx.room(args["room_id"]) is None:
        return {"error": f"no room {args['room_id']}"}
    if args.get("candidate"):
        # Milestone 12: the top-down image of solver candidate k (the brief lists their ranks and scores)
        fn = ctx.brief_fns.get("solver_fn")
        if fn is None:
            from wenart.furniture import solver
            fn = solver.solve_room
        cands = fn(ctx.building, args["room_id"], k=3) or []
        cand = next((c for c in cands if int(c.get("rank") or 0) == int(args["candidate"])), None)
        if cand is None:
            return {"error": f"no solver candidate {args['candidate']} for {args['room_id']} ({len(cands)} found)"}
        image = ctx.candidate_image(args["room_id"], int(args["candidate"]), cand)
        if image is None:
            return {"error": "the candidate image could not be drawn"}
        ctx.pending_images.append(ctx.images_dir().parent / image if not Path(image).is_absolute() else Path(image))
        return {"room_id": args["room_id"], "candidate": int(args["candidate"]), "image": image, "shown": True}
    path = ctx.topdown(args["room_id"], annotate=args.get("annotate", True))
    if path is None:
        return {"error": "the top-down image could not be drawn"}
    ctx.pending_images.append(path)
    return {"room_id": args["room_id"], "image": ctx.rel(path), "shown": True}


def t_room_brief(ctx: ToolContext, args: dict) -> dict:
    if ctx.room(args["room_id"]) is None:
        return {"error": f"no room {args['room_id']}"}
    return ctx.brief(args["room_id"])


# What the ``levels`` tool shows of a level mark and of an entrance (track L's fields, schema ``level_marks[]``,
# ``site.entrances[]``; docs/m12_tracks/L.md): its kind and its use, the AI labels.
LEVEL_MARK_FIELDS = ("id", "value", "relative", "absolute", "z", "kind", "point", "level_id", "room_id", "side",
                     "used_for", "status", "placement", "door_id", "corrected_by_ai", "inferred", "adjusted_by_ai",
                     "note")
ENTRANCE_FIELDS = ("door_id", "level_id", "room_id", "side", "main", "drawn", "solution", "rise", "into_air",
                   "below_ground", "terrain_lowered", "ground_source", "reason", "adjusted_by_ai")


def t_levels(ctx: ToolContext, args: dict) -> dict:
    """Milestone 12 (§3.6): the building's level data and the L-findings (``levels.checks.check_levels``)."""
    b = ctx.building
    site = b.get("site") or {}
    try:
        findings = [{"check": v.get("check"), "severity": v.get("severity"), "target": v.get("target"),
                     "message": v.get("message"), "metrics": v.get("metrics") or {}}
                    for v in ctx.level_check_fn()(b, ctx.scene, None) or []]
    except Exception as exc:  # noqa: BLE001 - the level data is still shown
        findings = [{"error": f"{type(exc).__name__}: {exc}"}]
    marks = [{k: m.get(k) for k in LEVEL_MARK_FIELDS if m.get(k) is not None} for m in b.get("level_marks") or []]
    ground = site.get("ground") or {}
    inference = b.get("level_inference") or {}
    return {"datum": (b.get("project") or {}).get("datum"),
            "levels": [{"id": lv.get("id"), "elevation": lv.get("elevation"),
                        "elevation_source": lv.get("elevation_source"), "ceiling_height": lv.get("ceiling_height")}
                       for lv in b.get("levels") or []],
            "marks": marks[:80], "marks_total": len(marks),
            "room_floors": [{"room_id": r.get("id"), "floor_offset_m": r.get("floor_offset_m"),
                             "floor_source": r.get("floor_source"), "floor_evidence": r.get("floor_evidence")}
                            for r in b.get("rooms") or [] if r.get("floor_offset_m") not in (None, 0, 0.0)
                            or r.get("floor_source")],
            "thresholds": [{"opening_id": o.get("id"), "threshold_z": o.get("threshold_z")}
                           for o in b.get("openings") or [] if o.get("threshold_z") is not None],
            "ground": {"points": list(ground.get("points") or [])[:60], "surface": ground.get("surface"),
                       "source": ground.get("source"), "terrain_override": ground.get("terrain_override"),
                       "light_wells": list(ground.get("light_wells") or [])[:10]},
            "terrain": site.get("terrain") or ground.get("surface"),
            "entrances": [{k: e.get(k) for k in ENTRANCE_FIELDS if e.get(k) is not None}
                          for e in site.get("entrances") or [] if isinstance(e, dict)],
            "plinth": site.get("plinth"),
            "level_inference": {k: (v[:20] if isinstance(v, list) else v) for k, v in inference.items()},
            "conflicts": [c for c in b.get("conflicts") or [] if "level" in json.dumps(c).lower()][:20],
            "findings": findings}


def t_plan_crop(ctx: ToolContext, args: dict) -> dict:
    room_id = args.get("room_id") or ctx.room_of(args.get("piece_id"))
    if not room_id or ctx.room(room_id) is None:
        return {"error": "give a room_id or a piece_id of this building"}
    path = ctx.plan_crop_path(room_id)
    if path is None:
        return {"room_id": room_id, "image": None, "note": "no plan crop on disk for this room"}
    ctx.pending_images.append(path)
    return {"room_id": room_id, "image": str(path.relative_to(ctx.project_out)), "shown": True}


def t_plausibility(ctx: ToolContext, args: dict) -> dict:
    try:
        if args.get("room_id"):
            if ctx.room(args["room_id"]) is None:
                return {"error": f"no room {args['room_id']}"}
            return ctx.plaus().score_room(ctx.building, args["room_id"])
        res = ctx.plaus().score_building(ctx.building)
        return {"mean": res.get("mean"), "counts": res.get("counts"),
                "rooms": {rid: r.get("score") for rid, r in (res.get("rooms") or {}).items()}}
    except NotImplementedError:
        return {"error": "the plausibility score is not available in this build (wenart.furniture.plausibility)"}


def t_view(ctx: ToolContext, args: dict) -> dict:
    cam = ctx.camera(args["view_id"])
    if cam is None:
        return {"error": f"no view {args['view_id']}; views: {', '.join(c.get('name') for c in ctx.cameras())}"}
    preview = ctx.preview_path(cam["name"])
    if preview is not None:
        ctx.pending_images.append(preview)
    plan = ctx.plan_crop_path(cam.get("room_id")) if cam.get("room_id") else None
    return {"view_id": cam["name"], "kind": cam.get("kind") or ("exterior" if not cam.get("room_id") else "interior"),
            "room_id": cam.get("room_id"), "position": cam.get("position"), "target": cam.get("target"),
            "lens_mm": cam.get("lens_mm"), "visible_furniture": cam.get("visible_furniture"),
            "visible_openings": cam.get("visible_openings"),
            "image": str(preview.relative_to(ctx.project_out)) if preview else None,
            "plan_crop": str(plan.relative_to(ctx.project_out)) if plan else None, "shown": preview is not None}


def t_exterior_summary(ctx: ToolContext, args: dict) -> dict:
    b = ctx.building
    ext = [w for w in b.get("walls") or [] if w.get("exterior")]
    xs = [float(p[0]) for w in ext for p in (w["start"], w["end"])]
    ys = [float(p[1]) for w in ext for p in (w["start"], w["end"])]
    per_level: dict = {}
    for o in b.get("openings") or []:
        lv = per_level.setdefault(str(o.get("level_id")), {})
        lv[str(o.get("type"))] = lv.get(str(o.get("type")), 0) + 1
    return {"outline_bbox": [min(xs), min(ys), max(xs), max(ys)] if xs else None, "outer_walls": len(ext),
            "levels": [{"id": lv.get("id"), "elevation": lv.get("elevation"),
                        "ceiling_height": lv.get("ceiling_height")} for lv in b.get("levels") or []],
            "roof": b.get("roof"), "site": {k: v for k, v in (b.get("site") or {}).items() if k in
                                            ("plot", "ground", "paving", "front_court", "grade")},
            "facade": b.get("facade"), "openings_per_level": per_level,
            "lighting": ctx.scene.get("lighting"), "exterior_cameras": [
                {"view_id": c.get("name"), "position": c.get("position"), "target": c.get("target"),
                 "lens_mm": c.get("lens_mm")} for c in ctx.cameras() if c.get("kind") == "exterior"],
            "agent_overrides": (b.get("agent_overrides") or {}).get("exterior")}


def t_catalog(ctx: ToolContext, args: dict) -> dict:
    entries = list(ctx.catalog().candidates(args["type"]))
    if args.get("style"):
        styled = [e for e in entries if args["style"] in (e.get("styles") or [])
                  or e.get("style_family") == args["style"]]
        entries = styled or entries
    size = args.get("size")
    if size:
        def dist(e):
            bb = e.get("bbox_m") or [0, 0, 0]
            return abs(float(bb[0]) - float(size[0])) + abs(float(bb[1]) - float(size[1]))
        entries = sorted(entries, key=dist)
    keep = ("id", "type", "source", "licence", "bbox_m", "styles", "style_family", "name")
    return {"type": args["type"], "count": len(entries), "models": [{k: e.get(k) for k in keep} for e in entries[:10]]}


def t_stage_status(ctx: ToolContext, args: dict) -> dict:
    run_dir = ctx.project_out / "run"
    out = {}
    names = [args["stage"]] if args.get("stage") else sorted(p.stem for p in run_dir.glob("*.json"))
    for name in names:
        rec = read_json(run_dir / f"{name}.json")
        if rec is not None:
            out[name] = {"status": rec.get("status"), "seconds": rec.get("seconds"), "note": rec.get("note")}
    return {"stages": out}


# --------------------------------------------------------------------------
# Edit tools (§3.2)
# --------------------------------------------------------------------------

def _target(tool: str, args: dict) -> str:
    for key in ("piece_id", "room_id", "view_id", "opening_id", "stage", "slot"):
        if args.get(key):
            return str(args[key])
    return tool


def _too_many(ctx: ToolContext, tool: str, args: dict) -> Optional[dict]:
    target = _target(tool, args)
    with ctx.lock:
        ctx.tries[target] = ctx.tries.get(target, 0) + 1
        if ctx.tries[target] > ctx.max_tries:
            return _result(False, [f"max_tries: {target} was edited {ctx.max_tries} times in this round"], tool=tool)
    return None


def edit_room(ctx: ToolContext, args: dict) -> str:
    """The room an edit belongs to (memory key): its room, its piece's room, its group's room, its view's room, else
    ``building``."""
    if args.get("room_id"):
        return str(args["room_id"])
    for key in ("piece_id", "view_id"):
        room = ctx.room_of(args.get(key))
        if room:
            return room
    gid = args.get("group_id")
    if gid:
        for f in ctx.building.get("furniture") or []:
            if (f.get("group") or {}).get("group_id") == gid:
                return str(f.get("room_id"))
    return "building"


def _result(accepted: bool, failed: list, *, before=None, after=None, overrides_id=None, rerun_from=None,
            message: str = "", changed_ids=None, tool: str = "", **extra) -> dict:
    out = {"accepted": bool(accepted), "failed_checks": [str(f) for f in failed or []],
           "score_before": before, "score_after": after, "overrides_id": overrides_id,
           "rerun_from": rerun_from if accepted else None, "message": message,
           "changed_ids": list(changed_ids or [])}
    out.update(extra)
    return out


def _accept(ctx: ToolContext, tool: str, args: dict, result: dict) -> dict:
    if ctx.overrides is not None:
        result["overrides_id"] = ctx.overrides.add(ctx.round, tool, args, result, ctx.model_id)
    with ctx.lock:
        ctx.accepted.append({"tool": tool, "args": copy.deepcopy(args), "result": result})
    return result


def _reject(ctx: ToolContext, tool: str, args: dict, result: dict) -> dict:
    with ctx.lock:
        ctx.rejected.append({"tool": tool, "args": args, "result": result})
    return result


def _next_log_seq(ctx: ToolContext) -> int:
    return ctx.log.next_seq() if ctx.log is not None else 0


def _building_edit(ctx: ToolContext, tool: str, args: dict, edit: dict, run: Callable[[dict], dict],
                   default_rerun: str) -> dict:
    """The shared part of a furniture or level edit: before image, validation (``run(building) -> apply_edit
    result``) and, when accepted, the new building with its decor synced (B3), the after image and the room's group
    checks now (§5.3: failed checks with numbers)."""
    room_id = edit_room(ctx, args)
    room_id = room_id if ctx.room(room_id) is not None else None
    before_png = ctx.topdown(room_id, what=f"{tool}_before") if room_id else None
    with ctx.lock:
        try:
            res = run(ctx.building)
        except NotImplementedError as exc:
            out = _result(False, ["validator_unavailable"], message=f"the edit validator is not built yet ({exc})",
                          tool=tool)
            return _reject(ctx, tool, args, out)
        accepted = bool(res.get("accepted")) and isinstance(res.get("building"), dict)
        if accepted:
            ctx.building = ctx.sync_fn()(res["building"])
    out = _result(accepted, res.get("failed_checks") or ([] if accepted else ["rejected"]),
                  before=res.get("score_before"), after=res.get("score_after"),
                  rerun_from=res.get("rerun_from") or default_rerun, message=str(res.get("message") or ""),
                  changed_ids=res.get("changed_ids"), log_seq=edit["log_seq"],
                  # acceptance is decided on the unfloored penalty (a score floored at 0 hides gains)
                  penalty_before=res.get("penalty_before"), penalty_after=res.get("penalty_after"))
    if before_png is not None:
        out["before_image"] = ctx.rel(before_png)
    if room_id:
        out["room_checks_now"] = ctx.group_checks_of(room_id)
    if not accepted:
        return _reject(ctx, tool, args, out)
    after_png = ctx.topdown(room_id, what=f"{tool}_after") if room_id else None
    if after_png is not None:
        out["after_image"] = ctx.rel(after_png)
    if tool == "relayout_room" and args.get("candidate") and ctx.memory is not None and room_id:
        ctx.memory.tried(room_id, int(args["candidate"]))
    return _accept(ctx, tool, args, out)


def furniture_handler(tool: str) -> Callable[[ToolContext, dict], dict]:
    op = OV.FURNITURE_TOOLS[tool]

    def handler(ctx: ToolContext, args: dict) -> dict:
        refused = _too_many(ctx, tool, args)
        if refused is not None:
            return _reject(ctx, tool, args, refused)
        edit = {"op": op, **copy.deepcopy(args), "round": ctx.round, "log_seq": _next_log_seq(ctx),
                "model": ctx.model_id}
        edit = OV.resolve_edit(edit, ctx.known_ops())

        def run(building):
            catalog = ctx.catalog() if edit["op"] == "swap_model" else None
            return ctx.edit_fn()(building, edit, catalog=catalog)
        return _building_edit(ctx, tool, args, edit, run, "refit")

    return handler


def level_handler(tool: str) -> Callable[[ToolContext, dict], dict]:
    """Milestone 12 (§3.6): a level edit through ``levels.edits.apply_level_edit`` (track L); re-run from build."""
    def handler(ctx: ToolContext, args: dict) -> dict:
        refused = _too_many(ctx, tool, args)
        if refused is not None:
            return _reject(ctx, tool, args, refused)
        edit = {"op": tool, **copy.deepcopy(args), "round": ctx.round, "log_seq": _next_log_seq(ctx),
                "model": ctx.model_id}
        return _building_edit(ctx, tool, args, edit, lambda b: ctx.level_fn()(b, edit), "build")
    return handler


def t_report_library_gap(ctx: ToolContext, args: dict) -> dict:
    """Milestone 12 (§6.4): record-only; the gap goes to ``agent_overrides.library_gaps`` and the report."""
    out = _result(True, [], message=f"library gap recorded: {args['type']} {args.get('style') or ''}".strip(),
                  log_seq=_next_log_seq(ctx), applied=False)
    return _accept(ctx, "report_library_gap", args, out)


def _validator_result(ctx: ToolContext, tool: str, args: dict, check: Callable[[], dict], stage: str) -> dict:
    refused = _too_many(ctx, tool, args)
    if refused is not None:
        ctx.rejected.append({"tool": tool, "args": args, "result": refused})
        return refused
    try:
        verdict = check() or {}
    except NotImplementedError as exc:
        out = _result(False, ["validator_unavailable"], message=f"the validator is not built yet ({exc})", tool=tool)
        ctx.rejected.append({"tool": tool, "args": args, "result": out})
        return out
    ok = bool(verdict.get("ok"))
    out = _result(ok, verdict.get("failed") or ([] if ok else ["rejected"]), rerun_from=stage,
                  message=str(verdict.get("message") or ""), log_seq=_next_log_seq(ctx),
                  changed_ids=[args.get("view_id")] if args.get("view_id") else [])
    if not ok:
        ctx.rejected.append({"tool": tool, "args": args, "result": out})
        return out
    return _accept(ctx, tool, args, out)


def camera_handler(tool: str) -> Callable[[ToolContext, dict], dict]:
    action = OV.CAMERA_TOOLS[tool]

    def handler(ctx: ToolContext, args: dict) -> dict:
        entry = dict({k: v for k, v in args.items() if k != "reason"}, action=action, reason=args.get("reason"))
        if action != "add" and ctx.camera(args["view_id"]) is None:
            out = _result(False, [f"no view {args['view_id']}"], tool=tool)
            ctx.rejected.append({"tool": tool, "args": args, "result": out})
            return out
        if action == "remove":
            # The camera entry of §17.3 names its kind and room: taken from the scene manifest.
            cam = ctx.camera(args["view_id"]) or {}
            entry.setdefault("kind", cam.get("kind") or ("exterior" if not cam.get("room_id") else "interior"))
            entry.setdefault("room_id", cam.get("room_id"))
        stored = {k: v for k, v in entry.items() if k != "action"}
        return _validator_result(ctx, tool, stored,
                                 lambda: ctx.checks().validate_camera_override(ctx.building, entry), "build")
    return handler


def t_set_material(ctx: ToolContext, args: dict) -> dict:
    override = {args["slot"]: args["look_id"]}
    return _validator_result(ctx, "set_material", args,
                             lambda: ctx.checks().validate_material_override(ctx.style, override), "build")


def t_set_lighting(ctx: ToolContext, args: dict) -> dict:
    def check() -> dict:
        room = ctx.room(args["room_id"])
        if room is None:
            return {"ok": False, "failed": [f"no room {args['room_id']}"], "message": "unknown room"}
        factor = float(args["factor"])
        if not LIGHTING_FACTOR[0] <= factor <= LIGHTING_FACTOR[1]:
            return {"ok": False, "failed": ["factor"], "message": f"factor must lie in {LIGHTING_FACTOR}"}
        return {"ok": True, "message": f"{room['id']}: room lights x {factor:g} in the next build"}
    return _validator_result(ctx, "set_lighting", args, check, "build")


def t_set_exterior(ctx: ToolContext, args: dict) -> dict:
    override = {k: v for k, v in args.items() if k != "reason"}
    if not override:
        return _result(False, ["nothing to change"], tool="set_exterior")
    return _validator_result(ctx, "set_exterior", args,
                             lambda: ctx.checks().validate_exterior_override(ctx.building, override), "build")


def t_correct_geometry(ctx: ToolContext, args: dict) -> dict:
    refused = _too_many(ctx, "correct_geometry", args)
    if refused is not None:
        ctx.rejected.append({"tool": "correct_geometry", "args": args, "result": refused})
        return refused
    verdict = GF.check(ctx.building, args)
    out = _result(verdict["ok"], verdict["failed"], rerun_from="pipeline_final", log_seq=_next_log_seq(ctx),
                  message="recorded (record-only in M11: the geometry is not changed; listed for the next full run)"
                  if verdict["ok"] else "not a clear drawing error", applied=False, metrics=verdict["metrics"])
    if not verdict["ok"]:
        ctx.rejected.append({"tool": "correct_geometry", "args": args, "result": out})
        return out
    return _accept(ctx, "correct_geometry", args, out)


def t_rerun_stage(ctx: ToolContext, args: dict) -> dict:
    from wenart.recognition.vlm_client import schema_errors
    stage, settings = args["stage"], dict(args.get("settings") or {})
    allowed = RERUN_WHITELIST.get(stage)
    failed = []
    if allowed is None:
        failed.append(f"stage {stage} is not on the white list ({', '.join(RERUN_WHITELIST)})")
    else:
        for key, value in settings.items():
            if key not in allowed:
                failed.append(f"setting {key} of {stage} is not on the white list")
            else:
                failed += [f"{key}: {e}" for e in schema_errors(allowed[key], value)]
    out = _result(not failed, failed, rerun_from=stage, log_seq=_next_log_seq(ctx),
                  message="the stage runs again with these settings" if not failed else "refused")
    if failed:
        ctx.rejected.append({"tool": "rerun_stage", "args": args, "result": out})
        return out
    return _accept(ctx, "rerun_stage", args, out)


def t_finish(ctx: ToolContext, args: dict) -> dict:
    ctx.finished = {"verdict": args["verdict"], "open_findings": list(args.get("open_findings") or [])}
    return {"ok": True, "round_ends": True}


# --------------------------------------------------------------------------
# The registry
# --------------------------------------------------------------------------

def with_reason(schema: dict) -> dict:
    """A tool's parameters: the schema without the edit meta fields (``op``, ``round``, ``log_seq``, ``model``:
    the loop sets them), plus a required ``reason``."""
    out = copy.deepcopy(schema) if schema else {"type": "object", "properties": {}}
    out.pop("$schema", None)
    out.setdefault("type", "object")
    props = out.setdefault("properties", {})
    for key in EDIT_META + ("action",):
        props.pop(key, None)
    required = [r for r in out.get("required") or [] if r not in EDIT_META + ("action",)]
    props["reason"] = dict(REASON)
    if "reason" not in required:
        required.append("reason")
    out["required"] = required
    return out


def edit_schemas() -> dict:
    """``EDIT_SCHEMAS`` of track B where filled in, else the fallbacks (module docstring)."""
    try:
        from wenart.furniture import edit_ops
        given = dict(getattr(edit_ops, "EDIT_SCHEMAS", {}) or {})
    except ImportError:
        given = {}
    return {op: given.get(op) or FALLBACK_EDIT_SCHEMAS[op] for op in FALLBACK_EDIT_SCHEMAS}


def override_schemas() -> tuple[dict, dict]:
    try:
        from wenart.blender import exterior_checks as XC
        cam = dict(getattr(XC, "CAMERA_OVERRIDE_SCHEMA", {}) or {})
        ext = dict(getattr(XC, "EXTERIOR_OVERRIDE_SCHEMA", {}) or {})
    except ImportError:
        cam, ext = {}, {}
    return cam or FALLBACK_CAMERA_SCHEMA, ext or FALLBACK_EXTERIOR_SCHEMA


READ_SCHEMAS = {
    "building_summary": _obj({"level": ID}, []),
    "room": _obj({"room_id": ID}, ["room_id"]),
    "room_topdown": _obj({"room_id": ID, "annotate": {"type": "boolean"}}, ["room_id"]),
    "plan_crop": _obj({"room_id": ID, "piece_id": ID}, []),
    "plausibility": _obj({"room_id": ID, "building": {"type": "boolean"}}, []),
    "view": _obj({"view_id": ID}, ["view_id"]),
    "exterior_summary": _obj({}, []),
    "catalog": _obj({"type": ID, "style": {"type": "string"}, "size": XY}, ["type"]),
    "stage_status": _obj({"stage": ID}, []),
    "room_brief": _obj({"room_id": ID}, ["room_id"]),
    "levels": _obj({}, []),
}
READ_SCHEMAS["room_topdown"] = _obj({"room_id": ID, "annotate": {"type": "boolean"},
                                     "candidate": {"type": "integer", "minimum": 1, "maximum": 3,
                                                   "description": "show solver candidate k instead of the room"}},
                                    ["room_id"])
READ_HANDLERS = {"building_summary": t_building_summary, "room": t_room, "room_topdown": t_room_topdown,
                 "plan_crop": t_plan_crop, "plausibility": t_plausibility, "view": t_view,
                 "exterior_summary": t_exterior_summary, "catalog": t_catalog, "stage_status": t_stage_status,
                 "room_brief": t_room_brief, "levels": t_levels}


def build_registry() -> Registry:
    tools: list[Tool] = [Tool(n, "read", DESCRIPTIONS[n], READ_SCHEMAS[n], READ_HANDLERS[n]) for n in READ_SCHEMAS]
    schemas = edit_schemas()
    for tool, op in OV.FURNITURE_TOOLS.items():
        tools.append(Tool(tool, "furniture", DESCRIPTIONS[tool], with_reason(schemas[op]), furniture_handler(tool)))
    cam_schema, ext_schema = override_schemas()
    remove_schema = _obj({"view_id": ID}, ["view_id"])
    for tool in OV.CAMERA_TOOLS:
        params = with_reason(remove_schema if tool == "remove_camera" else cam_schema)
        tools.append(Tool(tool, "override", DESCRIPTIONS[tool], params, camera_handler(tool), "build"))
    tools.append(Tool("set_material", "override", DESCRIPTIONS["set_material"], with_reason(MATERIAL_SCHEMA),
                      t_set_material, "build"))
    tools.append(Tool("set_exterior", "override", DESCRIPTIONS["set_exterior"], with_reason(ext_schema),
                      t_set_exterior, "build"))
    tools.append(Tool("set_lighting", "override", DESCRIPTIONS["set_lighting"], with_reason(LIGHTING_SCHEMA),
                      t_set_lighting, "build"))
    geometry = _obj({"kind": {"enum": list(GF.KINDS)}, "wall_ids": {"type": "array", "items": ID, "maxItems": 2},
                     "opening_id": ID, "evidence": {"type": "string", "minLength": 3}}, ["kind", "evidence"])
    tools.append(Tool("correct_geometry", "record", DESCRIPTIONS["correct_geometry"], with_reason(geometry),
                      t_correct_geometry, "pipeline_final"))
    rerun = _obj({"stage": {"enum": list(RERUN_WHITELIST)}, "settings": {"type": "object"}}, ["stage"])
    tools.append(Tool("rerun_stage", "record", DESCRIPTIONS["rerun_stage"], with_reason(rerun), t_rerun_stage))
    # Milestone 12: level edits (track L), library gaps, the free dry run
    for tool, schema in level_schemas().items():
        tools.append(Tool(tool, "level", DESCRIPTIONS[tool], with_reason(schema), level_handler(tool), "build"))
    tools.append(Tool("report_library_gap", "record", DESCRIPTIONS["report_library_gap"],
                      with_reason(LIBRARY_GAP_SCHEMA), t_report_library_gap))
    table = {t.name: t for t in tools}
    dry = _obj({"tool": {"enum": [n for n in table if table[n].kind in ("furniture", "level")]},
                "args": {"type": "object", "description": "the arguments you would send to that tool"}},
               ["tool", "args"])
    tools.append(Tool("dry_run", "control", DESCRIPTIONS["dry_run"], dry, dry_run_handler(table)))
    finish = _obj({"verdict": {"enum": ["done", "partly", "gave_up"]},
                   "open_findings": {"type": "array", "items": {"type": "string"}}}, ["verdict"])
    tools.append(Tool("finish", "control", DESCRIPTIONS["finish"], finish, t_finish))
    return Registry(tools)


def level_schemas() -> dict:
    """``LEVEL_EDIT_SCHEMAS`` of track L (contract §13.2) for every level tool."""
    try:
        from wenart.levels import edits
        given = dict(getattr(edits, "LEVEL_EDIT_SCHEMAS", {}) or {})
    except ImportError:
        given = {}
    return {op: given.get(op) or {"type": "object"} for op in OV.LEVEL_TOOLS}


def dry_run_handler(table: dict) -> Callable[[ToolContext, dict], dict]:
    """Milestone 12 (§5.3): the validator's answer for an edit without applying it. Free: no try is counted, nothing
    goes to the overrides or the memory; logged as a ``dry_run`` event."""
    def handler(ctx: ToolContext, args: dict) -> dict:
        from wenart.recognition.vlm_client import schema_errors
        name, inner = args["tool"], dict(args.get("args") or {})
        inner.setdefault("reason", "dry run")
        tool = table[name]
        errors = schema_errors(tool.parameters, inner)
        with ctx.lock:
            ctx.dry_runs += 1
        if errors:
            out = {"would_accept": False, "failed_checks": [f"schema: {e}" for e in errors[:5]]}
        else:
            prev = ctx.memory.repeat_of(edit_room(ctx, inner), name, inner) if ctx.memory is not None else None
            if prev is not None:
                out = {"would_accept": False, "failed_checks": [f"memory: rejected in round {prev.get('round')}: "
                                                                 + "; ".join(prev.get("reasons") or [])[:300]]}
            else:
                edit = {"op": name if tool.kind == "level" else OV.FURNITURE_TOOLS[name], **inner,
                        "round": ctx.round, "log_seq": 0, "model": ctx.model_id}
                try:
                    with ctx.lock:
                        if tool.kind == "level":
                            res = ctx.level_fn()(ctx.building, edit)
                        else:
                            edit = OV.resolve_edit(edit, ctx.known_ops())
                            catalog = ctx.catalog() if edit["op"] == "swap_model" else None
                            if ctx.apply_edit is not None:
                                res = ctx.apply_edit(ctx.building, edit, catalog=catalog)
                            else:
                                from wenart.furniture import edit_ops
                                res = edit_ops.dry_run(ctx.building, edit, catalog=catalog)
                    out = {"would_accept": bool(res.get("accepted")),
                           "failed_checks": [str(f) for f in res.get("failed_checks") or []],
                           "score_before": res.get("score_before"), "score_after": res.get("score_after"),
                           "message": str(res.get("message") or "")}
                except NotImplementedError as exc:
                    out = {"would_accept": False, "failed_checks": ["validator_unavailable"], "message": str(exc)}
        out["note"] = "dry run: nothing was applied, no try was counted"
        if ctx.log is not None:
            ctx.log.event("dry_run", ctx.round, tool=name, args=inner, status="would_accept" if out["would_accept"]
                          else "would_reject", note="; ".join(out["failed_checks"])[:300] or None,
                          room_id=edit_room(ctx, inner))
        return out
    return handler


EDIT_KINDS = ("furniture", "override", "record", "level")


def label_for(tool: str, ctx: ToolContext, args: dict) -> Optional[str]:
    """The label of an edit in the log (§9): added_by_ai, adjusted_by_ai, corrected_by_ai or agent_override."""
    if tool in ("add_piece", "add_group", "place_group", "complete_group"):
        return "added_by_ai"
    if tool == "correct_geometry" or tool in OV.LEVEL_TOOLS:
        return "corrected_by_ai"
    if tool == "report_library_gap":
        return "library_gap"
    if tool in OV.FURNITURE_TOOLS:
        piece = ctx.piece(args.get("piece_id") or "")
        if piece is not None and piece.get("source") == "added_by_ai":
            return "added_by_ai"
        return "adjusted_by_ai"
    if tool == "rerun_stage":
        return "agent_rerun"
    return "agent_override"
