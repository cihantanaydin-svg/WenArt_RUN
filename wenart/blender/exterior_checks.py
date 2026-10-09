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
SUN_ELEVATION_RANGE = (25.0, 50.0)
FILL_RANGE = (0.6, 0.8)
BLANK_FACADE_M = 3.0                    # a habitable room's outer wall this long with no opening is a blank facade
HABITABLE = ("bedroom", "living", "dining", "kitchen", "study", "office", "kids", "children", "play", "guest")
CAMERA_ACTIONS = ("set", "add", "remove")
ROOF_TYPES = ("flat", "gable", "hip", "mansard", "gambrel", "shed")
FENCES = ("hedge", "fence", "none")
COURTS = ("auto", "yes", "no")
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
            out.append(_v("X2", "major", c["opening_id"], c["reason"], height=c["height"]))
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
            out.append(_v("X2", "critical", o.get("wenart_id") or o.get("name"),
                          f"{o.get('name')} pokes through the roof (top {top:.2f} m)", top=top))


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
    stepped = {s["opening_id"] for s in inferred.get("steps") or []}
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
    for c in cams:
        x, y, z = (float(v) for v in c["position"])
        name = c.get("name")
        if any(G.point_in_polygon((x, y), o) or geom2d.distance_to_polygon_edges((x, y), o) < 0.3 for o in outlines):
            out.append(_v("X6", "critical", name, f"{name} stands inside the building", position=[x, y, z]))
        high = c.get("view") == "aerial" or z >= ridge + 1.0
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
        fill = c.get("fill")
        if isinstance(fill, (int, float)) and not FILL_RANGE[0] - 0.05 <= fill <= FILL_RANGE[1] + 0.05:
            out.append(_v("X6", "minor", name, f"{name}: the building fills {fill:.0%} of the frame width (wanted "
                                               f"{FILL_RANGE[0]:.0%}-{FILL_RANGE[1]:.0%})", fill=float(fill)))
        if "does not fit" in str(c.get("warning") or ""):
            out.append(_v("X6", "major", name, f"{name}: the whole building is not in the frame"))
        if c.get("view") == "frontal" or (c.get("view") in ("elevation", "agent") and main.get("direction")
                                          and _faces(c, main["direction"])):
            frontal = True
    if main and not frontal:
        out.append(_v("X6", "major", "exterior", f"no frontal view of the entrance ({main.get('axis')}) facade",
                      main_facade=main.get("axis")))


def _faces(cam: dict, direction) -> bool:
    """True when ``cam`` looks square (within 30 degrees) at the facade whose outward normal is ``direction``."""
    p, t = cam["position"], cam.get("target") or cam["position"]
    dx, dy = float(t[0]) - float(p[0]), float(t[1]) - float(p[1])
    n = math.hypot(dx, dy)
    return n > 1e-9 and -(dx * direction[0] + dy * direction[1]) / n > math.cos(math.radians(30.0))


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
    for f in building.get("furniture") or []:
        if f.get("room_id") != rid or f.get("build", True) is False or f.get("kind") == "decor":
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

def validate_camera_override(building: dict, camera: dict) -> dict:
    """``{"ok": bool, "failed": [str]}``: the schema, then for ``set`` / ``add``: an interior camera stands in its
    room, not inside a piece, at least ``DOOR_CLEARANCE_M`` from a door, ``EYE_RANGE_M`` above its floor; an
    exterior one outside the building (and its roof) at ``EYE_LEVEL_RANGE_M`` above the ground, or a high view
    above the ridge; the target differs from the position."""
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
        return {"ok": not failed, "failed": failed}
    from wenart.blender import geom2d

    prep = _prep(building) or {}
    x, y, z = pos
    for lid, o in (prep.get("outlines") or {}).items():
        if len(o) >= 3 and (G.point_in_polygon((x, y), o) or geom2d.distance_to_polygon_edges((x, y), o) < 0.3):
            failed.append(f"the camera stands inside the building (level {lid})")
            break
    roof = prep.get("roof") or {}
    ridge = float(roof.get("ridge_z") or 0.0)
    if roof.get("outline") and G.point_in_polygon((x, y), roof["outline"]) and z <= ridge + 1.0:
        failed.append("the camera stands under the roof")
    if z < ridge + 1.0:
        h = z - _ground_z(prep, x, y)
        if not EYE_LEVEL_RANGE_M[0] - 1e-3 <= h <= EYE_LEVEL_RANGE_M[1] + 1e-3:
            failed.append(f"eye height {h:.2f} m above the ground (an exterior view: {EYE_LEVEL_RANGE_M[0]:g}-"
                          f"{EYE_LEVEL_RANGE_M[1]:g} m, or a high view above the ridge {ridge:.2f} m)")
    return {"ok": not failed, "failed": failed}


def validate_exterior_override(building: dict, override: dict) -> dict:
    """``{"ok", "failed"}``: the schema, then: the roof with the override still covers the top level's outline
    (``roof.apply_override`` + ``roof_model``), a pitched roof at 5-60 degrees, the ground look is a ground of the
    vocabulary, the sun above the horizon (5-89 degrees)."""
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
    sun = override.get("sun") or {}
    if sun.get("elevation_deg") is not None and not 5.0 <= float(sun["elevation_deg"]) <= 89.0:
        failed.append(f"sun {sun['elevation_deg']} degrees: not above the horizon (5-89)")
    return {"ok": not failed, "failed": failed}


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
