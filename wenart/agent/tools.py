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
"""
from __future__ import annotations

import copy
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

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
    "relayout_room": _obj({"room_id": ID, "constraints": {"type": "object"}}, ["room_id"]),
    "set_room_type": _obj({"room_id": ID, "type": ID}, ["room_id", "type"]),
}
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
}
STAGE_OF = {"set_camera": "build", "add_camera": "build", "remove_camera": "build", "set_material": "build",
            "set_exterior": "build", "set_lighting": "build", "correct_geometry": "pipeline_final"}


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


@dataclass
class ToolContext:
    """What the tools of one round see and change (one per round)."""
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
    pending_images: list = field(default_factory=list)
    tries: dict = field(default_factory=dict)
    accepted: list = field(default_factory=list)          # [{tool, args, result}] of the round
    rejected: list = field(default_factory=list)
    schema_errors: int = 0
    finished: Optional[dict] = None
    max_tries: int = MAX_TRIES
    image_n: int = 0
    _catalog: Any = None

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
        self.image_n += 1
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in what)
        return self.images_dir() / f"r{self.round}_{self.image_n:03d}_{safe}.png"

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

    def specs(self) -> list[dict]:
        return [t.spec() for t in self.tools.values()]

    def call(self, ctx: ToolContext, name: str, args: Optional[dict], parse_error: Optional[str] = None) -> dict:
        """Run one tool call; a bad call returns ``{"error", "schema_error": true}`` and counts in
        ``ctx.schema_errors``."""
        from wenart.recognition.vlm_client import schema_errors
        tool = self.tools.get(name)
        if tool is None:
            ctx.schema_errors += 1
            return {"error": f"unknown tool {name!r}; the tools are: {', '.join(self.tools)}", "schema_error": True}
        if parse_error:
            ctx.schema_errors += 1
            return {"error": f"bad arguments for {name}: {parse_error}", "schema_error": True}
        errors = schema_errors(tool.parameters, args if args is not None else {})
        if errors:
            ctx.schema_errors += 1
            return {"error": f"the arguments of {name} do not match its schema: " + "; ".join(errors[:5]),
                    "schema_error": True}
        try:
            return tool.handler(ctx, dict(args or {}))
        except Exception as exc:  # noqa: BLE001 - the model sees the error and may try another way
            return {"error": f"{name} failed: {type(exc).__name__}: {exc}"}


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
    path = ctx.topdown(args["room_id"], annotate=args.get("annotate", True))
    if path is None:
        return {"error": "the top-down image could not be drawn"}
    ctx.pending_images.append(path)
    return {"room_id": args["room_id"], "image": ctx.rel(path), "shown": True}


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
    ctx.tries[target] = ctx.tries.get(target, 0) + 1
    if ctx.tries[target] > ctx.max_tries:
        return _result(False, [f"max_tries: {target} was edited {ctx.max_tries} times in this round"], tool=tool)
    return None


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
    ctx.accepted.append({"tool": tool, "args": copy.deepcopy(args), "result": result})
    return result


def _next_log_seq(ctx: ToolContext) -> int:
    return ctx.log.next_seq() if ctx.log is not None else 0


def furniture_handler(tool: str) -> Callable[[ToolContext, dict], dict]:
    op = OV.FURNITURE_TOOLS[tool]

    def handler(ctx: ToolContext, args: dict) -> dict:
        refused = _too_many(ctx, tool, args)
        if refused is not None:
            ctx.rejected.append({"tool": tool, "args": args, "result": refused})
            return refused
        edit = {"op": op, **copy.deepcopy(args), "round": ctx.round, "log_seq": _next_log_seq(ctx),
                "model": ctx.model_id}
        room_id = args.get("room_id") or ctx.room_of(args.get("piece_id"))
        before_png = ctx.topdown(room_id, what=f"{tool}_before") if room_id else None
        try:
            catalog = ctx.catalog() if op == "swap_model" else None
            res = ctx.edit_fn()(ctx.building, edit, catalog=catalog)
        except NotImplementedError as exc:
            out = _result(False, ["validator_unavailable"], message=f"the edit validator is not built yet ({exc})",
                          tool=tool)
            ctx.rejected.append({"tool": tool, "args": args, "result": out})
            return out
        accepted = bool(res.get("accepted")) and isinstance(res.get("building"), dict)
        out = _result(accepted, res.get("failed_checks") or ([] if accepted else ["rejected"]),
                      before=res.get("score_before"), after=res.get("score_after"),
                      rerun_from=res.get("rerun_from") or "refit", message=str(res.get("message") or ""),
                      changed_ids=res.get("changed_ids"), log_seq=edit["log_seq"],
                      # track B: acceptance is decided on the unfloored penalty (a score floored at 0 hides gains)
                      penalty_before=res.get("penalty_before"), penalty_after=res.get("penalty_after"))
        if before_png is not None:
            out["before_image"] = ctx.rel(before_png)
        if not accepted:
            ctx.rejected.append({"tool": tool, "args": args, "result": out})
            return out
        ctx.building = res["building"]
        after_png = ctx.topdown(room_id, what=f"{tool}_after") if room_id and ctx.room(room_id) else None
        if after_png is not None:
            out["after_image"] = ctx.rel(after_png)
        return _accept(ctx, tool, args, out)

    return handler


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
}
READ_HANDLERS = {"building_summary": t_building_summary, "room": t_room, "room_topdown": t_room_topdown,
                 "plan_crop": t_plan_crop, "plausibility": t_plausibility, "view": t_view,
                 "exterior_summary": t_exterior_summary, "catalog": t_catalog, "stage_status": t_stage_status}


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
    finish = _obj({"verdict": {"enum": ["done", "partly", "gave_up"]},
                   "open_findings": {"type": "array", "items": {"type": "string"}}}, ["verdict"])
    tools.append(Tool("finish", "control", DESCRIPTIONS["finish"], finish, t_finish))
    return Registry(tools)


EDIT_KINDS = ("furniture", "override", "record")


def label_for(tool: str, ctx: ToolContext, args: dict) -> Optional[str]:
    """The label of an edit in the log (§9): added_by_ai, adjusted_by_ai, corrected_by_ai or agent_override."""
    if tool in ("add_piece", "add_group"):
        return "added_by_ai"
    if tool == "correct_geometry":
        return "corrected_by_ai"
    if tool in OV.FURNITURE_TOOLS:
        piece = ctx.piece(args.get("piece_id") or "")
        if piece is not None and piece.get("source") == "added_by_ai":
            return "added_by_ai"
        return "adjusted_by_ai"
    if tool == "rerun_stage":
        return "agent_rerun"
    return "agent_override"
