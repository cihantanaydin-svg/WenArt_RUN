"""Code checks of the exterior and of the views, and validation of the agent's camera, exterior and material
overrides (docs/milestone11.md §4.1, §4.4, §7, contract §17.2). Pure Python (no bpy); owner: track C.

``Violation`` as in ``wenart.furniture.plausibility`` (checks X1–X8, V1, V3):
``{"check", "severity": critical | major | minor, "target", "room_id", "message", "metrics"}``.

What:

- ``check_exterior(building, scene_manifest=None, render_manifest=None)``: X1–X8 measured on the building JSON
  through the build's own pure planning (``build.prepare``: the outlines, the roof model, the site plan, the
  clipped openings), and, when given, on the scene manifest (the built objects, the exterior cameras, the sun,
  the outside looks) and the render manifest (its cameras). An item the inputs cannot measure is not reported
  (no guess): without a scene manifest X6–X8 are skipped.
- ``check_views(building, render_manifest)``: V1 (the camera inside its room, not inside a piece, at least
  ``DOOR_CLEARANCE_M`` from a door, eye height ``EYE_RANGE_M``) and V3 (no unverified stripes in a final image,
  decision D3) per view. ``render_manifest`` may be a render manifest (``renders``), a scene manifest
  (``cameras``) or a dict with both (``{"cameras": [...], "renders": [...], "markers_in_final": ...}``): a camera
  needs its position for V1.
- ``validate_camera_override`` / ``validate_exterior_override`` / ``validate_material_override``: the edit
  validator of the agent's ``set_camera`` / ``add_camera`` / ``remove_camera``, ``set_exterior`` and
  ``set_material`` tools (§3.2): the JSON schema first (``CAMERA_OVERRIDE_SCHEMA``, ``EXTERIOR_OVERRIDE_SCHEMA``,
  ``MATERIAL_OVERRIDE_SCHEMA``: strict, no extra keys), then the code checks. ``{"ok", "failed": [reasons]}``.

Why: the agent's code critic and edit validator (track A) need what can be measured, in milliseconds, with the
same rules the build uses (``build.prepare``, ``site``, ``roof``, ``exterior``), so a check and the build never
disagree.

How: every check is a small function adding Violations; the score is 100 minus ``SEVERITY_WEIGHT`` per
violation (at least 0).

Fix round after P3, part 2 (17 Oct 2026, docs/milestone13.md §14.9): X6 counts the true aerial views per camera set.
P4 builds with ``--cameras-from`` (the replayed M11 set: ext_5) and ``--cameras-extra`` (the searched set, renamed
with ``_s`` and marked ``extra``: ext_5_s); each set may have one, so the two sets together no longer give a minor X6.

Fix round after P4a (17 Oct 2026; pod P4a, real02): two X2 findings say where they come from in their metrics.
The critical "pokes through the roof" measured on the scene manifest's object boxes carries ``source:
scene_manifest`` (``SCENE_MANIFEST_SOURCE``): the box is the round's built scene, so the agent's dry re-check of an
edit that moved or removed the piece must not read it as still there (``wenart.agent.loop.after_findings``; P4a: the
bookshelf f_L1_058 kept a stale 5.17 m top through 3 rounds and every remove or move was rejected). A door or window
the build clipped under the roof below a usable height carries ``kind: opening_clip`` (``OPENING_CLIP_KIND``): the
agent reports it ("needs a dormer: review", ``causes.opening_under_roof``) instead of offering ``set_exterior``.

Fix round after P4b (17 Oct 2026; pod P4b, real03; integration of the agent track's asks):

- **The entrance view has its own X6 rule.** The planner frames an entrance door at 6-12 m with a fixed frame
  (``exterior.entrance_views``), so the whole-building rules (``FILL_RANGE``, "does not fit") always fired on a long
  building (real03's ext_7), and the agent moved the entrance view away from its door. An ``entrance`` view is now
  judged by ``entrance_view_problem`` instead: its door (``entrance``, else the main entrance of ``site.entrances``)
  is in ``visible_openings`` and in the horizontal field of view, and the camera stands at most
  ``ENTRANCE_VIEW_MAX_M`` from the door face and within ``ENTRANCE_VIEW_MAX_DEG`` of the door's axis (the agent's
  ``tools.entrance_problem`` and the build's ``agent_exterior_view`` use the same function). The bearing is taken
  from the door: the planner's own entrance view then looked 42 degrees off the axis, because ``frame_fixed`` turned
  it to the building's middle. Fix round after P6b (23 Oct 2026; docstring only): the planner's entrance view now
  looks straight at its door from 20 degrees off the door's axis (``exterior.entrance_frame``, ``_try_entrance``: a
  level frame, no yaw re-centring; a place is kept only with its door and the sky in the frame), and the
  bearing-from-door rule stays as it is (an agent's entrance view may still look along another line).
- **The sun override follows the X7 rule.** ``validate_exterior_override`` takes the sun elevation only within
  ``SUN_ELEVATION_RANGE`` (25-50 degrees, was 5-89), and an ``azimuth_deg`` only when, turned to the building frame
  with ``site.north_deg``, it lights the main facade (P4b's sun at 55 degrees was accepted, then X7 reported it).
  Lead decision 4 (17 Oct 2026): real02's assumed north stays; a view into the sun is only listed.

Fix round after P5 (22 Oct 2026; user decision (2) of 22 Oct 2026: wider or tilted framing for long, low buildings):
the planner frames the corner and frontal views of a long, low building to ``exterior.LONG_LOW_FILL`` (0.9) of the
frame width and records ``long_low`` in the plan (``exterior.long_low``). X6 takes ``exterior.LONG_LOW_FILL_RANGE``
(60-90 %) for those views (``fill_range``); every other view keeps ``FILL_RANGE``. Without it, each of real03's five
closer views would get a minor X6 ("fills 89 % of the frame width (wanted 60%-80%)") and the agent would move them
back out.

Fix round after P6a (22 Oct 2026; pod P6a, real04; docs/milestone13.md §14.13 decision 16):

- **X6's frontal view frames the building with the sky.** An ``elevation`` or ``agent`` view square to the main
  facade (``_faces``) counted as the frontal view by its pose alone, and nothing measured what its frame holds: P6a's
  agent camera ext_front_entrance, 5 m from real04's 15.4 m entrance facade at 26 mm, was counted (metrics 12 and 13)
  while it shows a blank wall, both doors cut, no sky (0 of 576 rays; the building spans 2.34 frame widths). Now such a
  view is the frontal view only when it frames the building (``frame_fixed``'s ``fits`` at its lens from its place,
  and that re-centred frame still square to the facade) and shows the sky (``exterior.sky_share`` >=
  ``exterior.SKY_MIN_SHARE``) (``x6_frontal``, the one rule of ``_x6`` and ``wenart.agent.critic_vision.x6_frontal``);
  otherwise "no frontal view" stays and the camera gets its own major X6 (``frame_problem``: "frames only part of the
  building", "no sky in the frame"). Every eye-level agent view gets the sky part of that finding. The measures are
  the camera record's ``fill`` / ``fits`` / ``sky_share`` / ``frame_target`` (the build records them on the agent's
  plans, ``build.finish_agent_exterior_plans``), else measured on the build's exterior model (``exterior_model``,
  ``camera_frame``); without either (a test's toy plan) the pose rule stays. An agent view's ``fill`` gets no
  fill-range finding (real03's agent frontal view ext_6 fills 0.94 of the frame and frames the building: a minor
  there would only move it).
- **The agent's eye-level exterior camera** (``validate_camera_override``, below the high-view line) is refused when
  its ray grid has no sky (``exterior.sky_share`` under ``exterior.SKY_MIN_SHARE``; only when the cheap checks
  passed: a camera inside a building sees no sky either) and when its lens lies outside ``exterior.EYE_LENS_RANGE_MM``
  (24-28 mm, Milestone 11 E14) on a building that is not long and low (``exterior.long_low``; CLAUDE.md, user OK of
  22 Oct 2026: "exterior views of long, low buildings may use a wider or tilted framing"). Measured: P6a's
  ext_front_entrance 0 % sky (refused); every accepted agent pose of P4a real02, P4b real03 and P6a real04 and every
  planner view 17-44 % (all pass).

Fix round after P6a (23 Oct 2026), review: ``x6_frontal`` judges two more agent poses by their frame. (1) A pose at
least ``HIGH_VIEW_ABOVE_RIDGE_M`` over the ridge kept the pose rule, and ``_x6`` measured no frame for it: P6a's strip
pose 1.2 m over real04's ridge, (8.5, 17.5, 7.2) -> (8.5, 6.0, 0.0), passes the validator (no eye-level rule up there)
and the build records fill 2.34, fits False, 0 % sky on it, yet "no frontal view" went and the critic was told it is
the frontal view. Now its frame is read or measured (``_x6`` passes its model) like an eye-level pose's; it still gets
no eye-level finding of its own (``frame_problem``). (2) An agent ``set`` of the planner's ``frontal`` view keeps that
label on any square pose (``build.agent_exterior_view``), and a ``frontal`` view counted at once: P6b's real03 ext_6
(searched, not frozen) set 8 m from its 33 m facade (fill 2.95, fits False) would have cleared "no frontal view" and
had no finding. Now only the planner's ``frontal`` view counts by its label; an agent plan (``_agent_camera``)
labelled ``frontal`` is a frontal pose (``_frontal_pose``) judged by its frame, with ``frame_problem``'s major on the
camera. Measured on P4a, P4b, P5, P6a and P6b: X6 unchanged (no high ``agent`` / ``elevation`` view there; the
``frontal`` views of real02 (P4a, replayed) and real03 (P6b) are the planner's).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G

SEVERITY_WEIGHT = {"critical": 25, "major": 10, "minor": 3}
STOREY_RANGE_M = (2.6, 3.3)
DOOR_HEIGHT_RANGE_M = (2.0, 2.2)
SILL_RANGE_M = (0.8, 1.1)
OVERHANG_RANGE_M = (0.3, 0.8)
EYE_LEVEL_RANGE_M = (1.5, 1.7)          # exterior eye-level cameras above the ground
EYE_RANGE_M = (1.2, 1.6)                # interior cameras above their floor
DOOR_CLEARANCE_M = 0.6
AGENT_WALL_CLEARANCE_M = 0.15           # pod P8: an agent camera may stand closer to a wall than a search point
                                        # (0.3 m); P5's accepted cam_r_L0_ebeveyn_odasi_4_1 stood 0.20 m from one
SUN_ELEVATION_RANGE = (25.0, 50.0)
FILL_RANGE = (0.6, 0.8)
BLANK_FACADE_M = 3.0                    # a habitable room's outer wall this long with no opening is a blank facade
HABITABLE = ("bedroom", "living", "dining", "kitchen", "study", "office", "kids", "children", "play", "guest")
CAMERA_ACTIONS = ("set", "add", "remove")
ROOF_TYPES = ("flat", "gable", "hip", "mansard", "gambrel", "shed")
FENCES = ("hedge", "fence", "none")
# Fix round after P4a (module docstring): the X2 metrics that tell where a finding comes from.
SCENE_MANIFEST_SOURCE = "scene_manifest"     # metrics.source of an X2 measured on the scene manifest's boxes
OPENING_CLIP_KIND = "opening_clip"           # metrics.kind of an opening clipped under the roof (= causes)
COURTS = ("auto", "yes", "no")
# Fix round after P4b (module docstring): an entrance view's rule (= the agent's tools.ENTRANCE_VIEW_MAX_M / _DEG).
ENTRANCE_VIEW = "entrance"
ENTRANCE_VIEW_MAX_M = 14.0              # the planner's farthest entrance view (exterior.ENTRANCE_VIEW_M, 12 m) + 2 m
ENTRANCE_VIEW_MAX_DEG = 30.0            # the planner looks 20 degrees off the door's axis
HIGH_VIEW_ABOVE_RIDGE_M = 1.0           # a camera this far over the ridge is a high view (X6, the validator)
FRONTAL_POSE_VIEWS = ("elevation", "agent")         # X6: the frontal view when square to the main facade and framed
FRAME_KEYS = ("fill", "fits", "sky_share")          # fix round after P6a: an agent plan's frame (the build records it)
_NUM = {"type": "number"}
_VEC3 = {"type": "array", "items": _NUM, "minItems": 3, "maxItems": 3}

# The agent's tool parameters (§17.3 entry shapes). Strict: no extra keys; the conditional rules (a set / add needs
# a position, a target and a kind; an interior camera its room) are code checks of validate_camera_override.
CAMERA_OVERRIDE_SCHEMA: dict = {
    "type": "object", "additionalProperties": False,
    "required": ["action", "view_id", "reason"],
    "properties": {
        "action": {"enum": list(CAMERA_ACTIONS)},
        "view_id": {"type": "string", "minLength": 1, "maxLength": 80, "pattern": "^[A-Za-z0-9_.-]+$"},
        "kind": {"enum": ["interior", "exterior"]},
        "room_id": {"type": ["string", "null"]},
        "position": _VEC3,
        "target": _VEC3,
        "lens_mm": {"type": "number", "minimum": 14.0, "maximum": 50.0},
        "reason": {"type": "string", "minLength": 1, "maxLength": 600},
    },
}
EXTERIOR_OVERRIDE_SCHEMA: dict = {
    "type": "object", "additionalProperties": False, "minProperties": 1,
    "properties": {
        "roof": {"type": "object", "additionalProperties": False, "minProperties": 1, "properties": {
            "type": {"enum": list(ROOF_TYPES)},
            "pitch_deg": {"type": "number", "minimum": 0.0, "maximum": 70.0},
            "overhang_m": {"type": "number", "minimum": 0.0, "maximum": 1.5}}},
        "ground": {"type": "string", "minLength": 1},
        "site": {"type": "object", "additionalProperties": False, "minProperties": 1, "properties": {
            "path": {"type": "boolean"},
            "fence": {"enum": list(FENCES)},
            "trees": {"type": "integer", "minimum": 0, "maximum": 12},
            "front_court": {"enum": list(COURTS)}}},
        "sun": {"type": "object", "additionalProperties": False, "minProperties": 1, "properties": {
            "azimuth_deg": {"type": "number", "minimum": 0.0, "maximum": 360.0},
            "elevation_deg": {"type": "number", "minimum": 0.0, "maximum": 90.0}}},
    },
}
# Material slots (set_material, §3.2) -> the vocabulary kinds a look of that slot may have.
SLOT_KINDS = {
    "walls": ("plaster", "painted", "wallpaper", "brick", "stone", "wood", "hard"),
    "kitchen_walls": ("plaster", "painted", "wallpaper", "brick", "stone", "wood", "hard"),
    "ceiling": ("plaster", "painted", "wood"),
    "floor": ("wood", "hard", "soft", "stone"),
    "wet_floor": ("hard", "stone"),
    "wet_walls": ("hard", "stone", "plaster"),
    "splashback": ("hard", "stone", "metal"),
    "trim": ("painted", "wood", "plaster", "metal"),
    "door": ("wood", "painted", "metal", "plastic"),
    "window_frame": ("metal", "plastic", "wood", "painted"),
    "facade": ("plaster", "brick", "stone", "wood", "painted", "metal", "hard"),
    "roof": ("roof", "metal"),
    "ground": ("ground",),
    "garden": ("ground",),
    "paving": ("ground", "hard", "stone"),
    "path": ("ground", "hard", "stone"),
    "plot_wall": ("plaster", "brick", "stone", "wood", "metal", "painted"),
    "plinth": ("stone", "brick", "hard", "plaster"),
    "cornice": ("plaster", "stone", "painted", "hard"),
    "surround": ("stone", "plaster", "hard", "painted"),
    "hedge": ("organic", "ground"),
}
SLOT_ALIASES = {"frames": "window_frame", "window_frames": "window_frame", "kitchen_splashback": "splashback",
                "wet_room_walls": "wet_walls", "wet_room_floor": "wet_floor"}
MATERIAL_OVERRIDE_SCHEMA: dict = {
    "type": "object", "additionalProperties": False, "minProperties": 1,
    "properties": {slot: {"type": "string", "minLength": 1, "maxLength": 64}
                   for slot in list(SLOT_KINDS) + list(SLOT_ALIASES)},
}


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def _v(check: str, severity: str, target, message: str, room_id=None, **metrics) -> dict:
    return {"check": check, "severity": severity, "target": target, "room_id": room_id, "message": message,
            "metrics": {k: (round(v, 4) if isinstance(v, float) else v) for k, v in metrics.items()}}


def _score(violations: Sequence[dict]) -> int:
    return max(0, 100 - sum(SEVERITY_WEIGHT.get(v["severity"], 0) for v in violations))


def _schema_errors(schema: dict, value) -> list[str]:
    import jsonschema

    v = jsonschema.Draft202012Validator(schema)
    return [f"schema: {'/'.join(str(p) for p in e.path) or '(root)'}: {e.message}"
            for e in sorted(v.iter_errors(value), key=lambda e: list(e.path))]


def _prep(building: dict) -> Optional[dict]:
    """The build's pure plan of the base variant (``build.prepare``), None when it cannot be made."""
    from wenart.blender import build as B

    try:
        return B.prepare(building, "base", None)
    except (KeyError, ValueError, TypeError, IndexError):
        return None


def _value(v) -> Optional[float]:
    if isinstance(v, dict):
        v = v.get("value")
    if isinstance(v, (int, float)) and not isinstance(v, bool):
        return float(v)
    return None


def _base_levels(building: dict) -> list[dict]:
    return sorted((lv for lv in building.get("levels") or [] if not lv.get("base_level_id")),
                  key=lambda lv: float(lv["elevation"]))


def _ground_z(prep: Optional[dict], x: float, y: float) -> float:
    from wenart.blender import site as S

    site = (prep or {}).get("site")
    return S.ground_z(site["terrain"], x, y) if site else 0.0


def _exterior_cameras(scene_manifest: Optional[dict], render_manifest: Optional[dict]) -> list[dict]:
    cams = []
    for m in (scene_manifest, render_manifest):
        for c in (m or {}).get("cameras") or []:
            if isinstance(c, dict) and c.get("kind") == "exterior" and c.get("position") \
                    and all(c.get("name") != x.get("name") for x in cams):
                cams.append(c)
    return cams


def entrance_record(building: dict, camera: dict) -> Optional[dict]:
    """Fix round after P4b (module docstring): the ``site.entrances`` record an entrance view frames: the camera's
    own ``entrance`` door, else the main entrance, else the one nearest the camera's target; None without one."""
    recs = [r for r in ((building.get("site") or {}).get("entrances") or [])
            if isinstance(r, dict) and r.get("outward") and (r.get("face") or r.get("centre"))]
    if not recs:
        return None
    door = camera.get("entrance") or camera.get("door_id")
    rec = next((r for r in recs if door and r.get("door_id") == door), None) or \
        next((r for r in recs if r.get("main")), None)
    if rec is None:
        aim = camera.get("target") or camera.get("position") or [0.0, 0.0]
        rec = min(recs, key=lambda r: math.dist([float(v) for v in (r.get("face") or r["centre"])[:2]],
                                                [float(v) for v in aim[:2]]))
    return rec


def entrance_view_problem(rec: Optional[dict], position, target, lens_mm: Optional[float] = None) -> Optional[str]:
    """Fix round after P4b (module docstring; pure): why the pose ``position`` -> ``target`` is no entrance view of
    the door ``rec``: the camera stands farther than ``ENTRANCE_VIEW_MAX_M`` from the door face, or more than
    ``ENTRANCE_VIEW_MAX_DEG`` off the door's outward axis (seen from the door), or the door lies outside the
    horizontal field of view of ``lens_mm`` (default ``exterior.EYE_LENS_MM``); None when it is one, or without a
    record. The bearing is measured from the door, not along the look: the planner's entrance view stands 20 degrees
    off the axis. Until the fix round after P6b ``exterior.frame_fixed`` turned its yaw to the building's middle (P4b
    real03's ext_7 looked 42 degrees off the axis with the door in the frame); since then (23 Oct 2026) it looks
    straight at its door (``exterior.entrance_frame``, ``_try_entrance``). An agent's entrance view may still look
    along another line, so the bearing stays measured from the door."""
    from wenart.blender import exterior as E

    if not rec or target is None:
        return None
    face = [float(v) for v in (rec.get("face") or rec["centre"])[:2]]
    o = [float(v) for v in rec["outward"][:2]]
    n = math.hypot(*o)
    if n < 1e-9:
        return None
    o = [o[0] / n, o[1] / n]
    px, py = float(position[0]) - face[0], float(position[1]) - face[1]
    dist = math.hypot(px, py)
    door = rec.get("door_id")
    if dist > ENTRANCE_VIEW_MAX_M + 1e-6:
        return (f"{dist:.1f} m from the door {door} (an entrance view stands at most {ENTRANCE_VIEW_MAX_M:g} m in "
                f"front of it)")
    bearing = 0.0 if dist < 1e-9 else math.degrees(math.acos(max(-1.0, min(1.0, (px * o[0] + py * o[1]) / dist))))
    if bearing > ENTRANCE_VIEW_MAX_DEG + 1e-6:
        return (f"standing {bearing:.0f} degrees off the door {door}'s axis (an entrance view stands within "
                f"{ENTRANCE_VIEW_MAX_DEG:g} degrees of it, in front of the door)")
    dx, dy = float(target[0]) - float(position[0]), float(target[1]) - float(position[1])
    look = math.hypot(dx, dy)
    if look > 1e-9 and dist > 1e-9:
        half = math.degrees(math.atan(E.SENSOR_MM / 2.0 / float(lens_mm or E.EYE_LENS_MM)))
        off = math.degrees(math.acos(max(-1.0, min(1.0, -(dx * px + dy * py) / (look * dist)))))
        if off > half + 1e-6:
            return (f"the door {door} is {off:.0f} degrees off the view direction (outside the {half:.0f} degree "
                    f"half width of the frame)")
    return None


def _entrance_x6(building: dict, c: dict, name, out: list) -> None:
    """Fix round after P4b (module docstring): the X6 of an ``entrance`` view: its door in the frame, the camera
    close to the door and looking along its axis (no whole-building fill or fit rule)."""
    rec = entrance_record(building, c)
    door = c.get("entrance") or (rec or {}).get("door_id")
    vis = c.get("visible_openings")
    if door and isinstance(vis, list) and (vis or c.get("source") == "searched") and door not in vis:
        out.append(_v("X6", "major", name, f"{name}: the entrance view does not show its door {door}", door=door))
    why = entrance_view_problem(rec, c["position"], c.get("target"), c.get("lens_mm"))
    if why is not None:
        out.append(_v("X6", "major", name, f"{name}: not an entrance view any more: {why}", door=door))


# --------------------------------------------------------------------------
# X1-X8
# --------------------------------------------------------------------------

def _x1(building: dict, prep: dict, out: list) -> None:
    from wenart.blender import geom2d

    levels = [lv for lv in _base_levels(building) if lv["id"] in (prep.get("outlines") or {})]
    for lv in levels:
        walls = [w for w in prep["building"].get("walls") or [] if w.get("level_id") == lv["id"]]
        outline, method = geom2d.wall_outline(walls)
        if len(outline) < 3:
            out.append(_v("X1", "critical", lv["id"], f"level {lv['id']}: no outer wall loop", level=lv["id"]))
        elif method == "convex_hull":
            out.append(_v("X1", "major", lv["id"], f"level {lv['id']}: the outer walls do not close (the outline is "
                                                   f"their convex hull)", level=lv["id"], method=method))
    for below, above in zip(levels, levels[1:]):
        a, b = prep["outlines"].get(above["id"]) or [], prep["outlines"].get(below["id"]) or []
        if len(a) < 3 or len(b) < 3:
            continue
        inside = sum(1 for p in a if G.point_in_polygon(p, b) or geom2d.distance_to_polygon_edges(p, b) < 0.3)
        share = inside / len(a)
        if share < 0.5:
            out.append(_v("X1", "critical", above["id"], f"level {above['id']} is not stacked on {below['id']}: "
                                                         f"{share:.0%} of its outline corners stand on it",
                          level=above["id"], share=share))


def _x2(building: dict, prep: dict, scene_manifest: Optional[dict], out: list) -> None:
    from wenart.blender import build as B
    from wenart.blender import geom2d
    from wenart.blender import roof as R

    roof = prep.get("roof")
    if not roof or not roof.get("equations"):
        out.append(_v("X2", "critical", "roof", "no roof over the top level"))
        return
    over = next((lv for lv in prep["building"]["levels"] if lv["id"] == roof.get("over_level_id")), None)
    outline = (prep.get("outlines") or {}).get(roof.get("over_level_id")) or []
    if len(outline) >= 3:
        uncovered = [p for p in outline if not G.point_in_polygon(p, roof["outline"])
                     and geom2d.distance_to_polygon_edges(p, roof["outline"]) > 1e-3 and not R.in_opening(roof, *p)]
        if uncovered:
            out.append(_v("X2", "critical", "roof", f"the roof leaves {len(uncovered)} outline corners of "
                                                    f"{roof['over_level_id']} uncovered", corners=len(uncovered)))
        if roof.get("type") != "flat":
            d = [geom2d.distance_to_polygon_edges(p, roof["outline"]) for p in outline
                 if G.point_in_polygon(p, roof["outline"]) and not R.in_opening(roof, *p)]
            if d:
                lo, hi = min(d), max(d)
                if lo < OVERHANG_RANGE_M[0] - 1e-3 or hi > OVERHANG_RANGE_M[1] + 0.25:
                    out.append(_v("X2", "major" if lo < 0.05 else "minor", "roof",
                                  f"roof overhang {lo:.2f}-{hi:.2f} m (believable: {OVERHANG_RANGE_M[0]:g}-"
                                  f"{OVERHANG_RANGE_M[1]:g} m)", overhang_min=lo, overhang_max=hi))
    for d in prep.get("terraces") or []:
        if d.get("conflict"):
            out.append(_v("X2", "minor", d["opening_id"], d["conflict"], room_id=d.get("room_id"),
                          decision=d["decision"]))
    for c in prep.get("clips") or []:
        if not c["fits"]:
            # fix round after P4a: the kind lets the agent report it (a dormer, review) instead of a roof edit
            out.append(_v("X2", "major", c["opening_id"], c["reason"], height=c["height"], kind=OPENING_CLIP_KIND))
    if over is not None:
        cut = R.wall_cut(roof)
        for w in B.openings_through_roof(prep["building"], over, cut):
            out.append(_v("X2", "major", w.split(":")[0], w))
        for w in B.pieces_above_ceiling(prep["building"], over):
            out.append(_v("X2", "major", w.split(":")[0], w))
    for o in (scene_manifest or {}).get("objects") or []:
        box = o.get("box3d")
        if not isinstance(box, dict) or o.get("kind") in ("roof", "terrain", "camera", "light"):
            continue
        cx, cy, cz = (float(v) for v in box["center"])
        top = cz + float(box["size"][2]) / 2.0
        if R.covers(roof, cx, cy) and top > R.surface_z(roof["equations"], cx, cy) + 0.02:
            # fix round after P4a: the box is the round's built scene, not the building checked (``source``)
            out.append(_v("X2", "critical", o.get("wenart_id") or o.get("name"),
                          f"{o.get('name')} pokes through the roof (top {top:.2f} m)", top=top,
                          source=SCENE_MANIFEST_SOURCE))


def _room_outer_length(room: dict, outline) -> float:
    from wenart.blender import geom2d

    poly = [tuple(p[:2]) for p in room.get("polygon") or []]
    total = 0.0
    for i in range(len(poly)):
        p, q = poly[i], poly[(i + 1) % len(poly)]
        mid = ((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0)
        if geom2d.distance_to_polygon_edges(mid, outline) < 0.45:
            total += G.distance(p, q)
    return total


def _x3(building: dict, prep: dict, out: list) -> None:
    from wenart.blender import cameras
    from wenart.blender import site as S

    vb = prep["building"]
    levels = _base_levels(vb)
    outer = S.outer_openings(vb, levels, prep.get("ground_outline") or [], prep.get("outlines"))
    by_axis: dict[str, int] = {}
    for rec in outer:
        by_axis[rec["axis"]] = by_axis.get(rec["axis"], 0) + 1
    for room in vb.get("rooms") or []:
        rtype = str(room.get("room_type") or "")
        outline = (prep.get("outlines") or {}).get(room.get("level_id")) or []
        if not any(rtype.startswith(h) for h in HABITABLE) or len(outline) < 3 or len(room.get("polygon") or []) < 3:
            continue
        length = _room_outer_length(room, outline)
        if length < BLANK_FACADE_M:
            continue
        ops = cameras.room_openings(room, [tuple(p[:2]) for p in room["polygon"]], vb)
        ids = {r["opening"]["id"] for r in outer}
        if not any(o["id"] in ids for o in ops):
            out.append(_v("X3", "major", room["id"], f"{room['id']} ({rtype}): {length:.1f} m of outer wall with no "
                                                     f"window or door: a blank facade", room_id=room["id"],
                          outer_wall_m=length))
    site = prep.get("site")
    if site is None:
        return
    ents = S.entrances(vb, levels, site["terrain"], prep.get("ground_outline") or [], prep.get("outlines"))
    if not ents and any(r["opening"].get("type") == "door" for r in outer):
        out.append(_v("X3", "minor", "entrance", "no outside door at or near the ground (entrance)"))
    inferred = site.get("inferred") or {}
    # 26 Oct 2026: a shared platform (site.entrance_layout) carries the steps of all its doors
    stepped = {i for s in inferred.get("steps") or [] for i in [s["opening_id"]] + list(s.get("members") or [])}
    records = (vb.get("site") or {}).get("entrances") if isinstance(vb.get("site"), dict) else None
    if isinstance(records, list):
        # Milestone 12 (docs/milestone12.md §3.5, track L): every outside door of site.entrances, every rise (a door
        # more than 1.5 m up is no longer left out: it is a door into the air).
        for r in records:
            if not isinstance(r, dict):
                continue
            rise = float(r.get("threshold_z") or 0.0) - float(r.get("ground_z") or 0.0)
            if r.get("into_air") or rise > 1.5:
                out.append(_v("X3", "critical", r.get("door_id"), f"door {r.get('door_id')} is {rise:.2f} m above the "
                                                                  f"ground with nothing to reach it (a door into the "
                                                                  f"air)", rise=rise))
            elif rise > 0.05 and (r.get("solution") in (None, "none") or r.get("door_id") not in stepped):
                out.append(_v("X3", "major", r.get("door_id"), f"entrance {r.get('door_id')} is {rise:.2f} m above "
                                                               f"the ground with no steps or ramp", rise=rise))
        return
    for e in ents:
        if e["rise"] > 0.05 and e["opening_id"] not in stepped:
            out.append(_v("X3", "major", e["opening_id"], f"entrance {e['opening_id']} is {e['rise']:.2f} m above the "
                                                          f"ground with no steps or ramp", rise=e["rise"]))


def _x4(building: dict, prep: dict, scene_manifest: Optional[dict], out: list) -> None:
    from wenart.blender import site as S

    site = prep.get("site")
    if site is None:
        out.append(_v("X4", "critical", "ground", "no ground around the building"))
        return
    if scene_manifest is not None:
        objs = scene_manifest.get("objects") or []
        ground = next((o for o in objs if o.get("kind") == "terrain"), None)
        if ground is None:
            out.append(_v("X4", "critical", "ground", "the scene has no ground"))
        else:
            rec = (scene_manifest.get("materials") or {}).get(ground.get("material")) or {}
            if not rec.get("textured") and not rec.get("procedural"):
                out.append(_v("X4", "minor", "ground", f"the ground ({ground.get('material')}) is a flat colour, not "
                                                       f"textured", material=ground.get("material")))
    if site.get("mode") != "full":
        return
    inferred = site.get("inferred") or {}
    ents = S.entrances(prep["building"], _base_levels(prep["building"]), site["terrain"],
                       prep.get("ground_outline") or [], prep.get("outlines"))
    pathed = {i for p in inferred.get("paths") or [] for i in p["opening_ids"]}
    drawn = [a["polygon"] for a in site.get("areas") or [] if a.get("kind") in ("paving", "parking")]
    for e in ents:
        probe = (e["centre"][0] + e["outward"][0] * (e["half_t"] + 0.5), e["centre"][1] + e["outward"][1] * (e["half_t"] + 0.5))
        if e["opening_id"] not in pathed and not any(G.point_in_polygon(probe, a) for a in drawn):
            out.append(_v("X4", "major", e["opening_id"], f"no path to the entrance {e['opening_id']}"))
    if not site.get("plot") and not inferred.get("boundary") and not site.get("plot_walls"):
        out.append(_v("X4", "minor", "plot", "no plot boundary (no plot drawn, no hedge or fence)"))


def _x5(building: dict, prep: dict, out: list) -> None:
    from wenart.blender import shell

    vb = prep["building"]
    levels = _base_levels(vb)
    for a, b in zip(levels, levels[1:]):
        h = float(b["elevation"]) - float(a["elevation"])
        if not STOREY_RANGE_M[0] - 1e-6 <= h <= STOREY_RANGE_M[1] + 1e-6:
            sev = "major" if h < 2.3 or h > 4.0 else "minor"
            out.append(_v("X5", sev, a["id"], f"storey {a['id']} -> {b['id']} is {h:.2f} m (believable "
                                              f"{STOREY_RANGE_M[0]:g}-{STOREY_RANGE_M[1]:g} m)", storey_m=h))
    from wenart.blender import cameras

    clipped = {c["opening_id"] for c in prep.get("clips") or []}
    types = {r["id"]: str(r.get("room_type") or "") for r in vb.get("rooms") or []}
    rooms_of: dict[str, list[str]] = {}
    for lv in levels:
        rooms_of.update(cameras.opening_rooms(vb, lv["id"]))
    for o in vb.get("openings") or []:
        lv = next((x for x in levels if x["id"] == o.get("level_id")), None)
        if lv is None or o.get("type") not in ("door", "window") or o["id"] in clipped:
            continue
        above = any(float(x["elevation"]) > float(lv["elevation"]) for x in levels)
        bottom, top, _ = shell.opening_vertical(o, lv, above)
        if o["type"] == "door":
            h = top - bottom
            if not DOOR_HEIGHT_RANGE_M[0] - 1e-6 <= h <= DOOR_HEIGHT_RANGE_M[1] + 0.3:
                out.append(_v("X5", "minor", o["id"], f"door {o['id']} is {h:.2f} m high (believable "
                                                      f"{DOOR_HEIGHT_RANGE_M[0]:g}-{DOOR_HEIGHT_RANGE_M[1]:g} m)",
                              height=h))
        else:
            sill = bottom - float(lv["elevation"])
            if not any(types.get(rid, "").startswith(HABITABLE) for rid in rooms_of.get(o["id"]) or []):
                continue                                 # bathrooms, stairs, halls: high or low sills are normal
            if 0.15 < sill < SILL_RANGE_M[0] - 0.1 or sill > SILL_RANGE_M[1] + 0.3:
                out.append(_v("X5", "minor", o["id"], f"window {o['id']} sill {sill:.2f} m (believable "
                                                      f"{SILL_RANGE_M[0]:g}-{SILL_RANGE_M[1]:g} m, or a French "
                                                      f"window at the floor)", sill=sill))


def _x6(building: dict, prep: dict, scene_manifest, render_manifest, out: list) -> None:
    from wenart.blender import geom2d
    from wenart.blender import site as S

    cams = _exterior_cameras(scene_manifest, render_manifest)
    if not cams:
        if scene_manifest is not None and (scene_manifest.get("whole_building") or {}).get("exterior_cameras"):
            out.append(_v("X6", "major", "exterior", "no exterior view was planned"))
        return
    outlines = [o for o in (prep.get("outlines") or {}).values() if len(o) >= 3]
    roof = prep.get("roof") or {}
    ridge = float(roof.get("ridge_z") or 0.0)
    main = prep.get("main_facade") or {}
    frontal = False
    built: list = []

    def model():
        """The build's exterior model of ``prep``, made once and only when a camera record lacks its frame."""
        if not built:
            built.append(exterior_model(prep))
        return built[0]

    for c in cams:
        x, y, z = (float(v) for v in c["position"])
        name = c.get("name")
        if any(G.point_in_polygon((x, y), o) or geom2d.distance_to_polygon_edges((x, y), o) < 0.3 for o in outlines):
            out.append(_v("X6", "critical", name, f"{name} stands inside the building", position=[x, y, z]))
        high = c.get("view") == "aerial" or z >= ridge + HIGH_VIEW_ABOVE_RIDGE_M
        if not high:
            h = z - _ground_z(prep, x, y)
            if not EYE_LEVEL_RANGE_M[0] - 1e-3 <= h <= EYE_LEVEL_RANGE_M[1] + 1e-3:
                out.append(_v("X6", "major", name, f"{name}: eye height {h:.2f} m above the ground (wanted "
                                                   f"{EYE_LEVEL_RANGE_M[0]:g}-{EYE_LEVEL_RANGE_M[1]:g} m)", eye_m=h))
            tgt = c.get("target") or c["position"]
            pitch = math.degrees(math.atan2(float(tgt[2]) - z, math.hypot(float(tgt[0]) - x, float(tgt[1]) - y)))
            if abs(pitch) > 0.5:
                out.append(_v("X6", "minor", name, f"{name}: pitched {pitch:.1f} degrees (verticals not straight; "
                                                   f"use the lens shift)", pitch_deg=pitch))
        if c.get("view") == "corner" and len(c.get("sides") or []) != 2:
            out.append(_v("X6", "major", name, f"{name}: a corner view that shows {len(c.get('sides') or [])} "
                                               f"facades", sides=c.get("sides")))
        if c.get("view") == ENTRANCE_VIEW:
            # fix round after P4b (module docstring): an entrance view frames its door, not the whole building
            _entrance_x6(building, c, name, out)
            continue
        fill = c.get("fill")
        lo, hi = fill_range(c)
        # fix round after P6a (module docstring): an agent plan's recorded fill is judged by frame_problem only
        if isinstance(fill, (int, float)) and not isinstance(fill, bool) and not _agent_camera(c) \
                and not lo - 0.05 <= fill <= hi + 0.05:
            out.append(_v("X6", "minor", name, f"{name}: the building fills {fill:.0%} of the frame width (wanted "
                                               f"{lo:.0%}-{hi:.0%})", fill=float(fill)))
        if "does not fit" in str(c.get("warning") or ""):
            out.append(_v("X6", "major", name, f"{name}: the whole building is not in the frame"))
        # fix round after P6a (module docstring): the frontal view frames the building with the sky; an eye-level
        # agent view shows the sky
        candidate = not high and _frontal_pose(c, main)
        frame = camera_frame(c, model) if not high and (candidate or _agent_camera(c)) else None
        why = frame_problem(c, frame, candidate)
        if why is not None:
            out.append(_v("X6", "major", name, f"{name}: {why}", fill=frame["fill"], fits=frame["fits"],
                          sky_share=frame["sky_share"]))
        # fix round after P6a (23 Oct 2026), review: a high pose's frame is measured too (``x6_frontal``)
        if x6_frontal(c, main, frame=frame, model=model):
            frontal = True
    if main and not frontal:
        out.append(_v("X6", "major", "exterior", f"no frontal view of the entrance ({main.get('axis')}) facade",
                      main_facade=main.get("axis")))
    # Milestone 13 (D8): one true aerial view is allowed (and the site view of the copies); a second one is noted.
    # Fix round after P3, part 2 (17 Oct 2026): counted per camera set. With --cameras-from and --cameras-extra (P4)
    # the replayed set (ext_5) and the searched set (``extra``: ext_5_s) each carry their own aerial; one per set.
    for extra in (False, True):
        aerials = [c.get("name") for c in cams if c.get("view") == "aerial" and not c.get("site_view")
                   and bool(c.get("extra")) == extra]
        if len(aerials) > 1:
            out.append(_v("X6", "minor", "exterior",
                          f"{len(aerials)} aerial views ({', '.join(str(a) for a in aerials)}): one true aerial view "
                          f"is the policy" + (" (the searched set of --cameras-extra)" if extra else ""),
                          aerials=aerials))


def fill_range(camera: dict) -> tuple[float, float]:
    """The share of the frame width X6 wants the building to fill in ``camera`` (pure): ``FILL_RANGE``, or
    ``exterior.LONG_LOW_FILL_RANGE`` for a corner or frontal view the planner framed closer for a long, low building
    (fix round after P5, 22 Oct 2026, user decision (2): the plan records ``long_low``, ``exterior.long_low``)."""
    if camera.get("view") in ("corner", "frontal") and isinstance(camera.get("long_low"), dict):
        from wenart.blender import exterior as E
        return E.LONG_LOW_FILL_RANGE
    return FILL_RANGE


def _faces(cam: dict, direction) -> bool:
    """True when ``cam`` looks square (within 30 degrees) at the facade whose outward normal is ``direction``."""
    p, t = cam["position"], cam.get("target") or cam["position"]
    dx, dy = float(t[0]) - float(p[0]), float(t[1]) - float(p[1])
    n = math.hypot(dx, dy)
    return n > 1e-9 and -(dx * direction[0] + dy * direction[1]) / n > math.cos(math.radians(30.0))


def _agent_camera(cam: dict) -> bool:
    """A camera the agent placed: its plan's ``policy`` is ``agent`` or the build labelled its pose ``agent``."""
    return cam.get("policy") == "agent" or cam.get("view") == "agent"


def _frontal_pose(cam: dict, main: Optional[dict]) -> bool:
    """An ``elevation`` / ``agent`` view whose pose looks square (``_faces``) at the main facade ``main``. Fix round
    after P6a (23 Oct 2026), review: and an agent plan (``_agent_camera``) labelled ``frontal``, the label the build
    keeps on the agent's square pose of the planner's frontal view (``x6_frontal``)."""
    try:
        view = cam.get("view")
        return (view in FRONTAL_POSE_VIEWS or (view == "frontal" and _agent_camera(cam))) \
            and bool(cam.get("position")) and bool((main or {}).get("direction")) and _faces(cam, main["direction"])
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def exterior_model(prep: Optional[dict]):
    """Fix round after P6a (module docstring): the build's ``exterior.ExteriorModel`` of ``prep`` (``build.prepare``:
    ``exterior.build_model`` on its building, levels, roof and site, as the build makes it); None when it cannot be
    made."""
    if not isinstance(prep, dict) or not isinstance(prep.get("building"), dict):
        return None
    from wenart.blender import exterior as E

    try:
        b = prep["building"]
        return E.build_model(b, list(b.get("levels") or []), prep.get("roof"), prep.get("site"))
    except (KeyError, ValueError, TypeError, IndexError, AttributeError):
        return None


def camera_frame(camera: dict, model=None) -> Optional[dict]:
    """Fix round after P6a (module docstring): ``{"fill", "fits", "sky_share"}`` (and ``frame_target`` when known) of
    an exterior camera: the record's own (``FRAME_KEYS`` and ``frame_target``, recorded by
    ``build.finish_agent_exterior_plans``), else ``exterior.frame_check`` of its pose, lens and lens shift on ``model``
    (an ``ExteriorModel``, or a function returning one or None); None without either."""
    if all(isinstance(camera.get(k), (int, float)) for k in FRAME_KEYS):
        out = {"fill": float(camera["fill"]), "fits": bool(camera["fits"]), "sky_share": float(camera["sky_share"])}
        if isinstance(camera.get("frame_target"), (list, tuple)) and len(camera["frame_target"]) >= 2:
            out["frame_target"] = [float(v) for v in camera["frame_target"]]
        return out
    if not camera.get("position") or not camera.get("target"):
        return None
    m = model() if callable(model) else model
    if m is None:
        return None
    from wenart.blender import exterior as E

    try:
        return E.frame_check(m, [float(v) for v in camera["position"]], [float(v) for v in camera["target"]],
                             float(camera.get("lens_mm") or E.EYE_LENS_MM), shift_y=float(camera.get("shift_y") or 0.0))
    except (TypeError, ValueError, IndexError, ZeroDivisionError, FloatingPointError):
        return None


def frames_building(frame: Optional[dict]) -> bool:
    """Fix round after P6a: the frame ``frame`` (``camera_frame``) holds the whole building and the sky."""
    from wenart.blender import exterior as E

    return bool(frame) and bool(frame["fits"]) and float(frame["sky_share"]) >= E.SKY_MIN_SHARE - 1e-9


def frame_problem(camera: dict, frame: Optional[dict], frontal_pose: bool) -> Optional[str]:
    """Fix round after P6a (module docstring): why an eye-level camera's frame breaks the rules, None when it does
    not (or without a frame): a pose square to the main facade (``frontal_pose``) that does not frame the whole
    building, and any such camera without sky in its frame (CLAUDE.md: the sky, the sun and the horizon are always in
    the image)."""
    if not frame:
        return None
    from wenart.blender import exterior as E

    parts = []
    if frontal_pose and not frame["fits"]:
        parts.append(f"frames only part of the building (it spans {float(frame['fill']):.2f} of the frame width at "
                     f"{float(camera.get('lens_mm') or E.EYE_LENS_MM):g} mm from this view line), so it is no "
                     f"frontal view")
    if float(frame["sky_share"]) < E.SKY_MIN_SHARE - 1e-9:
        parts.append(f"no sky in the frame ({float(frame['sky_share']):.0%} of its rays look up into the sky, at "
                     f"least {E.SKY_MIN_SHARE:.0%}: the sky, the sun and the horizon are always in the image)")
    return "; ".join(parts) or None


def x6_frontal(camera: Optional[dict], main: Optional[dict], frame: Optional[dict] = None, model=None) -> bool:
    """X6's frontal view (one rule for ``_x6`` and ``wenart.agent.critic_vision.x6_frontal``): the planner's
    ``frontal`` view, or an ``elevation`` / ``agent`` view (or an agent plan labelled ``frontal``, ``_frontal_pose``)
    whose pose looks square at the main facade ``main`` (``_faces``, within 30 degrees) and, fix round after P6a
    (module docstring), frames the whole building with the sky (``frames_building`` of ``frame``, else of
    ``camera_frame(camera, model)``), the frame that holds the building (its ``frame_target``, the yaw re-centred)
    still looking square at that facade: from real04's strip a pose 29.8 degrees off square at (22, 18.2) fits the
    building only when turned 43.8 degrees off square, a corner view. A pose whose frame cannot be measured keeps the
    pose rule.

    Fix round after P6a (23 Oct 2026), review: a high pose (at least ``HIGH_VIEW_ABOVE_RIDGE_M`` over the ridge) is
    judged by its frame like an eye-level one (it kept the pose rule: P6a's strip pose 1.2 m over real04's ridge,
    fill 2.34, fits False, 0 % sky, cleared "no frontal view"), and only the planner's ``frontal`` view counts by its
    label: an agent plan keeps the label ``frontal`` on any square pose (``build.agent_exterior_view``), so a set of
    real03's ext_6 8 m from its 33 m facade (fill 2.95, fits False) counted as the frontal view. Without a main facade
    (``main`` has no direction: X6 asks for no frontal view then) an agent plan's ``frontal`` label stands as before."""
    if not isinstance(camera, dict):
        return False
    if camera.get("view") == "frontal" and (not _agent_camera(camera) or not (main or {}).get("direction")):
        return True
    if not _frontal_pose(camera, main):
        return False
    got = frame if frame is not None else camera_frame(camera, model)
    if got is None:
        return True
    if got.get("frame_target") is not None and not _faces(dict(camera, target=got["frame_target"]), main["direction"]):
        return False                    # the frame that holds the building looks at it from a corner, not square
    return frames_building(got)


def eye_level_problems(prep: Optional[dict], position, target, lens_mm: Optional[float], sky: bool = True,
                       model=None) -> list[str]:
    """Fix round after P6a (module docstring): why an eye-level exterior pose of the agent is refused: its lens
    (``lens_mm``; None = the build's default, not judged) outside ``exterior.EYE_LENS_RANGE_MM`` on a building that is
    not long and low (``exterior.long_low``), and (``sky``) no sky in its ray grid (``exterior.sky_share`` under
    ``exterior.SKY_MIN_SHARE``, at ``lens_mm`` or ``exterior.EYE_LENS_MM``). The model (``model``, else
    ``exterior_model(prep)``) is made only when a rule needs it; nothing is refused without it."""
    from wenart.blender import exterior as E

    lens = None if lens_mm is None else float(lens_mm)
    off = lens is not None and not E.EYE_LENS_RANGE_MM[0] - 1e-6 <= lens <= E.EYE_LENS_RANGE_MM[1] + 1e-6
    if not off and not sky:
        return []
    m = model if model is not None else exterior_model(prep)
    if m is None:
        return []
    out = []
    if off and E.long_low(m) is None:
        out.append(f"lens {lens:g} mm outside the eye-level range {E.EYE_LENS_RANGE_MM[0]:g}-"
                   f"{E.EYE_LENS_RANGE_MM[1]:g} mm (Milestone 11 E14; a wider framing is for a long, low building "
                   f"only, decision of 22 Oct 2026)")
    if sky:
        share = E.sky_share(m, position, target, lens if lens is not None else E.EYE_LENS_MM)
        if share < E.SKY_MIN_SHARE - 1e-9:
            out.append(f"no sky in the frame: {share:.0%} of its rays look up into the sky (at least "
                       f"{E.SKY_MIN_SHARE:.0%}; CLAUDE.md: the sky, the sun and the horizon are always in the image); "
                       f"stand where the facade's roof line and the sky above it are in the frame")
    return out


def _x7(prep: dict, scene_manifest: Optional[dict], out: list) -> None:
    sun = ((scene_manifest or {}).get("lighting") or {}).get("sun")
    if not sun:
        return
    el = float(sun.get("elevation_deg", 0.0))
    if not SUN_ELEVATION_RANGE[0] - 1e-6 <= el <= SUN_ELEVATION_RANGE[1] + 1e-6:
        out.append(_v("X7", "major", "sun", f"sun {el:.0f} degrees above the horizon (wanted "
                                            f"{SUN_ELEVATION_RANGE[0]:g}-{SUN_ELEVATION_RANGE[1]:g})", elevation=el))
    main = prep.get("main_facade")
    az = sun.get("azimuth_building_deg", sun.get("azimuth_deg"))
    if main and az is not None:
        a = math.radians(float(az))                     # clockwise from the building's +Y
        sx, sy = math.sin(a), math.cos(a)
        dot = sx * main["direction"][0] + sy * main["direction"][1]
        if dot <= 0.0:
            out.append(_v("X7", "major", "sun", f"the sun ({float(az):.0f} degrees) lights the back: the main "
                                                f"({main['axis']}) facade is in shadow", azimuth=float(az), dot=dot))
    world = (scene_manifest.get("lighting") or {}).get("world_exterior")
    if _exterior_cameras(scene_manifest, None) and not world:
        out.append(_v("X7", "minor", "sky", "the exterior views use the interior HDRI (its own sun and ground), not a "
                                            "sky matched to the sun"))


def _x8(building: dict, scene_manifest: Optional[dict], out: list) -> None:
    if not scene_manifest:
        return
    looks = scene_manifest.get("exterior_looks") or {}
    style = scene_manifest.get("style_profile") or {}
    text = str(style.get("source_text") or "").lower()
    frame = (style.get("window_frame") or {})
    want = (frame.get("outside") or {}).get("material") or frame.get("material")
    got = (looks.get("window_frame") or {}).get("material")
    if "frame" in text and want and got and want != got and (looks.get("window_frame") or {}).get("source") != "agent":
        out.append(_v("X8", "major", "window_frame", f"window frames {got} outside, the brief says {want}",
                      wanted=want, built=got))
    brief = scene_manifest.get("brief") or {}
    words = ((brief.get("exterior") or {}).get("value")) or {}
    for slot, phrase in (words.items() if isinstance(words, dict) else []):
        look = looks.get(slot) or {}
        if str(phrase or "").strip() and look.get("source") in ("fallback", "build"):
            out.append(_v("X8", "major", slot, f"brief exterior.{slot} {phrase!r} is not used ({look.get('material')} "
                                               f"from the fallback)", phrase=phrase, built=look.get("material")))
    roof = building.get("roof") if isinstance(building.get("roof"), dict) else {}
    if roof.get("covering") and (looks.get("roof") or {}).get("material") != roof["covering"] \
            and (looks.get("roof") or {}).get("source") != "agent":
        out.append(_v("X8", "major", "roof", f"roof covering {roof['covering']} drawn, "
                                             f"{(looks.get('roof') or {}).get('material')} built"))


def check_exterior(building: dict, scene_manifest: dict | None = None, render_manifest: dict | None = None) -> dict:
    """``{"score": 0..100, "violations": [Violation]}`` (X1–X8; module docstring)."""
    from wenart.blender import build as B

    out: list[dict] = []
    if not B.is_whole_building(building):
        return {"score": 100, "violations": [], "skipped": "not a whole building (no slabs, roof or variants)"}
    prep = _prep(building)
    if prep is None:
        out.append(_v("X1", "critical", "building", "the build cannot plan this building"))
        return {"score": _score(out), "violations": out}
    _x1(building, prep, out)
    _x2(building, prep, scene_manifest, out)
    _x3(building, prep, out)
    _x4(building, prep, scene_manifest, out)
    _x5(building, prep, out)
    if scene_manifest is not None or render_manifest is not None:
        _x6(building, prep, scene_manifest, render_manifest, out)
    _x7(prep, scene_manifest, out)
    _x8(building, scene_manifest, out)
    return {"score": _score(out), "violations": out}


# --------------------------------------------------------------------------
# V1, V3
# --------------------------------------------------------------------------

def _door_segments(building: dict, room: dict) -> list[tuple[str, tuple, tuple]]:
    from wenart.blender import cameras

    return cameras.door_segments(room, building)


def camera_problems(building: dict, cam: dict) -> list[dict]:
    """V1 of one interior camera (pure): ``[Violation]``."""
    from wenart.blender.parametric import piece_bbox

    name = cam.get("name") or cam.get("view_id") or cam.get("camera")
    rid = cam.get("room_id")
    room = next((r for r in building.get("rooms") or [] if r["id"] == rid), None)
    if room is None or len(room.get("polygon") or []) < 3:
        return [_v("V1", "critical", name, f"{name}: its room {rid} is not in the building", room_id=rid)]
    level = next((lv for lv in building.get("levels") or [] if lv["id"] == room.get("level_id")), None)
    x, y, z = (float(v) for v in cam["position"])
    out = []
    poly = [tuple(p[:2]) for p in room["polygon"]]
    if not G.point_in_polygon((x, y), poly):
        out.append(_v("V1", "critical", name, f"{name} stands outside its room {rid}", room_id=rid, position=[x, y]))
    floor = float(level["elevation"]) if level else 0.0
    from wenart.blender.shell import piece_built     # M12: unknown / no-model pieces are not built either

    for f in building.get("furniture") or []:
        if f.get("room_id") != rid or not piece_built(f) or f.get("kind") == "decor":
            continue
        fp = f["footprint"]
        rect = G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0))
        bottom = floor + float(f.get("mount_bottom_m") or 0.0)
        if G.point_in_polygon((x, y), rect) and bottom - 0.05 <= z <= bottom + float(piece_bbox(f)[2]) + 0.05:
            out.append(_v("V1", "critical", name, f"{name} stands inside {f['id']} ({f.get('type')})", room_id=rid,
                          piece=f["id"]))
    for oid, a, b in _door_segments(building, room):
        d = G.point_segment_distance((x, y), a, b)
        if d < DOOR_CLEARANCE_M:
            out.append(_v("V1", "major", name, f"{name} is {d:.2f} m from the door {oid} (at least "
                                               f"{DOOR_CLEARANCE_M:g} m)", room_id=rid, door=oid, distance=d))
    h = z - floor
    if not EYE_RANGE_M[0] - 1e-3 <= h <= EYE_RANGE_M[1] + 1e-3:
        out.append(_v("V1", "major" if h < 1.0 or h > 1.8 else "minor", name,
                      f"{name}: eye height {h:.2f} m (wanted {EYE_RANGE_M[0]:g}-{EYE_RANGE_M[1]:g} m)", room_id=rid,
                      eye_m=h))
    return out


def check_views(building: dict, render_manifest: dict) -> dict:
    """``{"views": {view_id: [Violation]}}`` (V1, V3; module docstring)."""
    rm = render_manifest or {}
    cams = {c.get("name"): c for c in rm.get("cameras") or [] if isinstance(c, dict) and c.get("name")}
    for c in ((rm.get("scene") or {}).get("cameras") or []) if isinstance(rm.get("scene"), dict) else []:
        cams.setdefault(c.get("name"), c)
    names = list(cams)
    for e in rm.get("renders") or []:
        if isinstance(e, dict) and e.get("camera") and e["camera"] not in cams:
            cams[e["camera"]] = {"name": e["camera"], "room_id": e.get("room_id"), "position": e.get("position"),
                                 "kind": "interior" if e.get("room_id") else "exterior"}
            names.append(e["camera"])
    markers = bool(rm.get("markers_in_final")) or any(
        (r or {}).get("unverified") for r in (rm.get("materials") or {}).values())
    out: dict[str, list] = {}
    for name in names:
        c = cams[name]
        v = []
        if c.get("kind") != "exterior" and c.get("room_id") and c.get("position"):
            v += camera_problems(building, c)
        if markers:
            v.append(_v("V3", "major", name, f"{name}: the unverified stripes are in the final image "
                                             f"(markers_in_final: false is the default, decision D3)",
                        room_id=c.get("room_id")))
        out[name] = v
    return {"views": out}


# --------------------------------------------------------------------------
# Override validators
# --------------------------------------------------------------------------

def free_floor_problems(building: dict, camera: dict) -> list[str]:
    """An agent camera stands on the free floor the camera search uses (pure; pod P8, 11 Oct 2026): at least
    ``camsearch.OBSTACLE_CLEARANCE`` from every floor piece and free-standing decor, ``AGENT_WALL_CLEARANCE_M`` from
    the walls. real03's ``cam_r_L0_banyo_2_1`` was moved 0.05 m beside the shower glass: half the frame was the
    glass (depth 0.05 m at the lens). In a room with no free point (the search's fallback camera) only the pieces
    reaching camera height count, plus the floor decor (fix round after P5: the search's fallback avoids it too).
    The search's own points always pass; the message names the nearest one."""
    from wenart.blender import camsearch as CS, geom2d
    from wenart.blender.parametric import piece_bbox

    room = next((r for r in building.get("rooms") or [] if r["id"] == camera.get("room_id")), None)
    if room is None or len(room.get("polygon") or []) < 3:
        return []                                       # camera_problems names the missing room
    points, warning = CS.candidate_positions(room, building)
    if not points:
        return []
    x, y = (float(v) for v in camera["position"][:2])
    if any(math.dist(q, (x, y)) < 1e-6 for q in points):
        return []
    polygon = CS.room_polygon(room)
    pieces = [f for f in CS.shown_pieces(room, building) if CS.mount_bottom(f) <= 0.0]
    obstacles = [(f["id"], CS.obstacle_rect(f)) for f in pieces]
    if warning:                                         # no free point: only what stands at camera height counts
        obstacles = [(f["id"], CS.obstacle_rect(f)) for f in pieces if piece_bbox(f)[2] >= CS.CAMERA_HEIGHT]
    # fix round after P5: the floor decor counts in a room without a free point too, as in the search's fallback
    obstacles += [("floor decor", r) for r in CS.floor_decor_rects(room, building)]
    if geom2d.point_is_free((x, y), polygon, [r for _i, r in obstacles], AGENT_WALL_CLEARANCE_M,
                            CS.OBSTACLE_CLEARANCE):
        return []
    near = [(geom2d.distance_to_rect((x, y), r["center"], r["size"], r["rotation_deg"]), i) for i, r in obstacles]
    near = [(d, i) for d, i in near if d < CS.OBSTACLE_CLEARANCE - 1e-9]
    what = (f"{min(near)[0]:.2f} m from {min(near)[1]}" if near
            else f"{geom2d.distance_to_polygon_edges((x, y), polygon):.2f} m from a wall")
    best = min(points, key=lambda q: math.dist(q, (x, y)))
    return [f"the camera stands {what} (free floor: {CS.OBSTACLE_CLEARANCE:g} m from pieces, {AGENT_WALL_CLEARANCE_M:g} m "
            f"from walls); the nearest free point is [{best[0]:.2f}, {best[1]:.2f}]"]


def validate_camera_override(building: dict, camera: dict) -> dict:
    """``{"ok": bool, "failed": [str]}``: the schema, then for ``set`` / ``add``: an interior camera stands in its
    room, not inside a piece, on the free floor (``free_floor_problems``), at least ``DOOR_CLEARANCE_M`` from a door,
    ``EYE_RANGE_M`` above its floor; an
    exterior one outside the building (and its roof) at ``EYE_LEVEL_RANGE_M`` above the ground, or a high view
    above the ridge; the target differs from the position. Fix round after P6a (module docstring): an eye-level
    exterior one keeps the eye-level lens range unless the building is long and low, and has sky in its frame
    (``eye_level_problems``)."""
    failed = _schema_errors(CAMERA_OVERRIDE_SCHEMA, camera)
    if failed:
        return {"ok": False, "failed": failed}
    if camera["action"] == "remove":
        return {"ok": True, "failed": []}
    for key in ("kind", "position", "target"):
        if camera.get(key) is None:
            failed.append(f"{camera['action']}: {key} is required")
    if failed:
        return {"ok": False, "failed": failed}
    pos, tgt = [float(v) for v in camera["position"]], [float(v) for v in camera["target"]]
    if math.dist(pos, tgt) < 0.1:
        failed.append("the target is the position")
    prefix = "cam_" if camera["kind"] == "interior" else "ext_"
    if not str(camera["view_id"]).startswith(prefix):
        failed.append(f"an {camera['kind']} view_id starts with {prefix} (the render and report readers)")
    if camera["kind"] == "interior":
        if not camera.get("room_id"):
            return {"ok": False, "failed": failed + ["an interior camera needs its room_id"]}
        if camera.get("lens_mm") is not None and not 14.0 <= float(camera["lens_mm"]) <= 35.0:
            failed.append(f"lens {camera['lens_mm']} mm outside 14-35 mm (interior)")
        failed += [v["message"] for v in camera_problems(building, dict(camera, name=camera["view_id"]))]
        failed += free_floor_problems(building, camera)
        return {"ok": not failed, "failed": failed}
    from wenart.blender import geom2d

    prep = _prep(building) or {}
    x, y, z = pos
    for lid, o in (prep.get("outlines") or {}).items():
        if len(o) >= 3 and (G.point_in_polygon((x, y), o) or geom2d.distance_to_polygon_edges((x, y), o) < 0.3):
            failed.append(f"the camera stands inside the building (level {lid})")
            break
    from wenart.blender import copies as CP          # 11 Oct 2026 (real04): the other buildings on the plot
    for c, fp in zip(CP.copies_of(building), CP.footprints(building)):
        if G.point_in_polygon((x, y), fp) or geom2d.distance_to_polygon_edges((x, y), fp) < 0.3:
            failed.append(f"the camera stands inside the building {c['id']} (another building on the plot)")
            break
    roof = prep.get("roof") or {}
    ridge = float(roof.get("ridge_z") or 0.0)
    if roof.get("outline") and G.point_in_polygon((x, y), roof["outline"]) and z <= ridge + 1.0:
        failed.append("the camera stands under the roof")
    if z < ridge + HIGH_VIEW_ABOVE_RIDGE_M:
        h = z - _ground_z(prep, x, y)
        if not EYE_LEVEL_RANGE_M[0] - 1e-3 <= h <= EYE_LEVEL_RANGE_M[1] + 1e-3:
            failed.append(f"eye height {h:.2f} m above the ground (an exterior view: {EYE_LEVEL_RANGE_M[0]:g}-"
                          f"{EYE_LEVEL_RANGE_M[1]:g} m, or a high view above the ridge {ridge:.2f} m)")
        # fix round after P6a (module docstring): the eye-level lens and the sky (rays only for an otherwise valid pose)
        failed += eye_level_problems(prep, pos, tgt, camera.get("lens_mm"), sky=not failed)
    return {"ok": not failed, "failed": failed}


def validate_exterior_override(building: dict, override: dict) -> dict:
    """``{"ok", "failed"}``: the schema, then: the roof with the override still covers the top level's outline
    (``roof.apply_override`` + ``roof_model``), a pitched roof at 5-60 degrees, the ground look is a ground of the
    vocabulary, the sun by the X7 rule (fix round after P4b, module docstring: the elevation within
    ``SUN_ELEVATION_RANGE``, an azimuth on the side of the main facade in the building frame)."""
    failed = _schema_errors(EXTERIOR_OVERRIDE_SCHEMA, override)
    if failed:
        return {"ok": False, "failed": failed}
    roof_ov = override.get("roof")
    if roof_ov:
        from wenart.blender import roof as R

        t = roof_ov.get("type") or ((building.get("roof") or {}).get("type") if isinstance(building.get("roof"), dict)
                                    else "flat")
        if t != "flat" and roof_ov.get("pitch_deg") is not None and not 5.0 <= float(roof_ov["pitch_deg"]) <= 60.0:
            failed.append(f"a {t} roof at {roof_ov['pitch_deg']} degrees (5-60)")
        # 24 Oct 2026: a drawn roof value is the anchor (roof.apply_override refuses it): say so to the agent
        drawn_roof = building.get("roof") if isinstance(building.get("roof"), dict) else None
        refused = (R.apply_override(drawn_roof, roof_ov)[0] or {}).get("override_refused") if drawn_roof else None
        failed += [f"roof {c['field']} is drawn ({c['kept']}); the override would not apply" for c in refused or []]
        trial = dict(building, agent_overrides=dict(building.get("agent_overrides") or {},
                                                    exterior=dict(((building.get("agent_overrides") or {})
                                                                   .get("exterior") or {}), roof=roof_ov)))
        prep = _prep(trial)
        roof = (prep or {}).get("roof")
        if not roof or not roof.get("equations"):
            failed.append("the roof with this override has no planes")
        else:
            outline = (prep.get("outlines") or {}).get(roof.get("over_level_id")) or []
            from wenart.blender import geom2d
            bad = [p for p in outline if not G.point_in_polygon(p, roof["outline"])
                   and geom2d.distance_to_polygon_edges(p, roof["outline"]) > 1e-3 and not R.in_opening(roof, *p)]
            if bad:
                failed.append(f"the roof would leave {len(bad)} outline corners uncovered")
            if not roof.get("convex"):
                failed.append("the roof planes would not be convex")
    if override.get("ground") is not None:
        failed += _look_problems("ground", override["ground"])
    failed += sun_override_problems(building, override.get("sun") or {})
    return {"ok": not failed, "failed": failed}


def sun_override_problems(building: dict, sun: dict, main: Optional[dict] = None) -> list[str]:
    """Fix round after P4b (module docstring): a sun override against X7 (``_x7``): the elevation within
    ``SUN_ELEVATION_RANGE``; an ``azimuth_deg`` (compass, clockwise from north) turned to the building frame with
    ``site.north_deg`` must light the main facade (``main``, else ``build.prepare``'s ``main_facade``; dot > 0).
    Lead decision 4 (17 Oct 2026): an assumed north (real02) stays as it is."""
    from wenart.blender import site as S

    out = []
    el = sun.get("elevation_deg") if isinstance(sun, dict) else None
    lo, hi = SUN_ELEVATION_RANGE
    if el is not None and not lo - 1e-6 <= float(el) <= hi + 1e-6:
        out.append(f"sun {float(el):g} degrees above the horizon: outside the X7 range ({lo:g}-{hi:g} degrees)")
    az = sun.get("azimuth_deg") if isinstance(sun, dict) else None
    if az is not None:
        if main is None:
            main = (_prep(building) or {}).get("main_facade")
        if isinstance(main, dict) and main.get("direction"):
            north, src = S.north_deg(building)
            az_b = (float(az) - float(north)) % 360.0
            a = math.radians(az_b)
            dot = math.sin(a) * float(main["direction"][0]) + math.cos(a) * float(main["direction"][1])
            if dot <= 0.0:
                out.append(f"sun azimuth {float(az):g} degrees (compass; {az_b:g} in the building frame, north "
                           f"{float(north):g}, {src}) lights the back: X7 wants the sun on the side of the main "
                           f"({main.get('axis')}) facade")
    return out


def _look_problems(slot: str, look_id: str) -> list[str]:
    from wenart.style.profile import _entry

    entry = _entry(look_id)
    if not entry:
        return [f"{slot}: look {look_id!r} is not in the vocabulary"]
    kinds = SLOT_KINDS.get(slot)
    if kinds and entry.get("kind") not in kinds:
        return [f"{slot}: {look_id} is a {entry.get('kind')} look (the slot takes {', '.join(kinds)})"]
    if slot in ("wet_floor",):
        from wenart.style.profile import is_wet_safe
        if not is_wet_safe(look_id) and entry.get("kind") != "hard":
            return [f"{slot}: {look_id} is not wet-safe"]
    return []


def validate_material_override(style: dict, override: dict) -> dict:
    """``{"ok", "failed"}``: the schema (known slots only), then every look exists in the vocabulary and fits its
    slot (``SLOT_KINDS``: a floor look on the floor, a ground look on the ground, a wet-safe wet floor)."""
    failed = _schema_errors(MATERIAL_OVERRIDE_SCHEMA, override)
    if failed:
        return {"ok": False, "failed": failed}
    for slot, look_id in override.items():
        failed += _look_problems(SLOT_ALIASES.get(slot, slot), look_id)
    return {"ok": not failed, "failed": failed}
