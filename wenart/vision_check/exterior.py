"""Exterior views of the vision check (docs/milestone10.md §3.3 item 4, §1.6b row 11).

What: the pure helpers that let ``expected.expected_view`` and the vision check treat a camera of kind
``exterior`` (the scene manifest's ``ext_<n>``: no room, no level) like an interior one:

- ``scope``: which building an exterior view shows. The variant of the camera (``variant_building``: only
  its levels), the outer openings of that variant (doors and windows on exterior walls, with the compass side
  of each) and the north (``site.north_deg``, else +Y, assumed). Only these openings are expected elements of
  an exterior view; furniture and decor seen through a window are ``ignore``.
- ``roles_for``: the thresholds of an exterior view (``check.yaml: roles_exterior``): a window of a whole house
  fills 0.1-0.7 % of the frame, so the interior thresholds (2 %) would ignore all of them.
- ``block``: the ``exterior`` record of an expected view: per visible facade the openings expected in view
  (counts for the advisory VLM window count, the facade's pixel box = the projected outer wall faces turned
  to the camera), and the roof check.
- ``roof_check``: the roof of the building JSON (its planes, else ``wenart.blender.roof.planes_for``) sampled on a
  grid, projected and compared with the rendered depth: a sample is *present* when the rendered surface lies
  within ``roof_tol_m`` of it, *sky* when nothing was rendered there, *behind* when the render shows a surface
  farther away (the roof is not where the JSON puts it), *occluded* when something nearer hides it. A roof in
  view whose visible samples are mostly sky or behind is ``missing``: a mismatch of the Cycles render, never
  fixed (like ``in_json_not_rendered``).

Why: the gate and the vision check run on the exterior views too (docs/milestone10.md §3.3 item 4); the
expected facade openings and the roof are what such a view can be judged on.

How: numpy and the projection of ``wenart.vision_check.expected`` only; the Blender helpers
(``wenart.blender.site``, ``geom2d``, ``roof``, ``shell``: all pure Python, no ``bpy``) are imported inside the
functions, so importing this module stays as light as ``expected``.
"""
from __future__ import annotations

import math
from typing import Optional

import numpy as np

EXTERIOR = "exterior"
SIDE_ANGLE_DEG = 45.0               # an outer wall belongs to the side it faces within 45 degrees
_SCOPES: dict = {}                  # (id(building), variant) -> scope (the module is used per run, the dict stays small)


def is_exterior(camera: Optional[dict], view=None) -> bool:
    """True for a camera of kind ``exterior`` (scene manifest); a camera without a kind is exterior only when
    it has no room and is named ``ext_<n>``."""
    if camera is not None and camera.get("kind"):
        return camera.get("kind") == EXTERIOR
    name = str(getattr(view, "camera", "") or (camera or {}).get("name") or "")
    room = getattr(view, "room_id", None) or (camera or {}).get("room_id")
    return not room and name.startswith("ext_")


def variant_of(scene_manifest: dict, camera: Optional[dict]) -> str:
    """The variant id an exterior camera belongs to: the camera's, else the scene manifest's, else ``base``."""
    return str((camera or {}).get("variant") or (scene_manifest.get("variant") or {}).get("id") or "base")


def roles_for(cfg: dict, exterior: bool) -> dict:
    """The role thresholds of a view kind (``roles`` or ``roles_exterior`` of ``check.yaml``)."""
    if exterior and isinstance(cfg.get("roles_exterior"), dict):
        return {**cfg["roles"], **cfg["roles_exterior"]}
    return cfg["roles"]


def variant_building_of(building: dict, variant: str) -> tuple[dict, list[str]]:
    """``(building of one variant, warnings)``: ``wenart.views.variant_building`` for a building with
    ``variants``, the building itself otherwise (the M3-M9 buildings)."""
    from wenart import views

    try:
        return views.variant_building(building, variant), []
    except KeyError as exc:
        return building, [f"variant {variant!r}: {exc}; the whole building is used"]


def outer_openings(building: dict) -> dict[str, dict]:
    """``{opening id: {"wall_id", "level_id", "type", "outward": (nx, ny), "centre": (x, y)}}`` of the doors and
    windows on the outer walls of ``building`` (its levels only).

    A wall is outer when it says ``exterior: true``; a building whose walls do not carry the flag gets the
    walls whose one side lies outside the level's wall outline (``wenart.blender.shell.outward_side``)."""
    from wenart.blender import geom2d
    from wenart.blender.shell import opening_centre_on_wall, outward_side

    walls_by_level: dict[str, list] = {}
    for w in building.get("walls") or []:
        walls_by_level.setdefault(w.get("level_id"), []).append(w)
    flagged = any("exterior" in w for w in building.get("walls") or [])
    outlines = {lid: geom2d.wall_outline(ws)[0] for lid, ws in walls_by_level.items()}
    walls = {w["id"]: w for w in building.get("walls") or []}
    out: dict[str, dict] = {}
    for o in building.get("openings") or []:
        if o.get("type") not in ("door", "window"):
            continue
        wall = walls.get(o.get("wall_id"))
        if wall is None:
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        outline = outlines.get(wall.get("level_id")) or []
        outward = outward_side(wall, outline, (cx, cy)) if len(outline) >= 3 else None
        if flagged and not wall.get("exterior"):
            continue
        if not flagged and outward is None:
            continue
        if outward is None:                  # flagged outer wall, outline unusable: use the left normal
            from wenart import geometry as G
            outward = G.unit_normal_left(wall["start"], wall["end"])
        out[o["id"]] = {"wall_id": wall["id"], "level_id": wall.get("level_id"), "type": o["type"],
                        "outward": (float(outward[0]), float(outward[1])), "centre": (cx, cy)}
    return out


def side_name(outward, north: float, north_known: bool) -> str:
    from wenart.blender import site

    return site.side_of(outward, north, north_known)


def scope(camera: Optional[dict], scene_manifest: dict, building: dict) -> dict:
    """What an exterior view shows (see the module docstring): ``{"variant", "building", "level_ids",
    "openings": {id: info + "side"}, "north", "north_known", "warnings"}``."""
    from wenart.blender import site

    variant = variant_of(scene_manifest, camera)
    key = (id(building), variant)
    if key in _SCOPES and _SCOPES[key]["building_ref"] is building:
        return _SCOPES[key]
    vb, warnings = variant_building_of(building, variant)
    north, src = site.north_deg(vb)
    known = not src.startswith("assumed")
    openings = outer_openings(vb)
    for info in openings.values():
        info["side"] = side_name(info["outward"], north, known)
    result = {"variant": variant, "building": vb, "building_ref": building,
              "level_ids": [lv["id"] for lv in vb.get("levels") or []], "openings": openings,
              "north": north, "north_source": src, "north_known": known, "warnings": warnings}
    if len(_SCOPES) > 16:
        _SCOPES.clear()
    _SCOPES[key] = result
    return result


# --------------------------------------------------------------------------
# Facades
# --------------------------------------------------------------------------

def _wall_face(wall: dict, level: dict, outward, ceiling_to: Optional[float] = None) -> np.ndarray:
    """The 4 corners (3D) of the outer face of a wall: floor to ceiling (or ``ceiling_to``)."""
    half = float(wall.get("thickness") or 0.2) / 2.0
    z0 = float(level["elevation"])
    z1 = float(ceiling_to if ceiling_to is not None else z0 + float(level.get("ceiling_height") or 2.7))
    a = (float(wall["start"][0]) + outward[0] * half, float(wall["start"][1]) + outward[1] * half)
    b = (float(wall["end"][0]) + outward[0] * half, float(wall["end"][1]) + outward[1] * half)
    return np.array([[a[0], a[1], z0], [b[0], b[1], z0], [b[0], b[1], z1], [a[0], a[1], z1]], dtype=np.float64)


def facade_boxes(camera: dict, size, sc: dict) -> dict[str, dict]:
    """``{side: {"box_px", "area_frac", "walls": [ids]}}``: the union box (clipped to the frame) of the projected
    outer wall faces of each side that turn towards the camera."""
    from wenart.vision_check import expected as X

    vb = sc["building"]
    levels = {lv["id"]: lv for lv in vb.get("levels") or []}
    walls = {w["id"]: w for w in vb.get("walls") or []}
    by_wall: dict[str, tuple] = {}
    for info in sc["openings"].values():
        by_wall.setdefault(info["wall_id"], (info["outward"], info["side"]))
    # An outer wall without an opening still shows its face: the sides come from the openings' walls and from
    # every outer wall whose outward normal could be told (``outer_wall_sides``).
    for wid, (outward, side) in outer_wall_sides(vb, sc).items():
        by_wall.setdefault(wid, (outward, side))
    W, H = int(size[0]), int(size[1])
    pos = np.asarray(camera["position"], dtype=np.float64)
    found: dict[str, dict] = {}
    for wid, (outward, side) in by_wall.items():
        wall, level = walls.get(wid), levels.get(walls.get(wid, {}).get("level_id"))
        if wall is None or level is None:
            continue
        face = _wall_face(wall, level, outward)
        mid = face[:2].mean(axis=0)
        if (pos[0] - mid[0]) * outward[0] + (pos[1] - mid[1]) * outward[1] <= 0.0:
            continue                                  # a back face
        hull = X.projected_hull(face, camera, (W, H), edges=((0, 1), (1, 2), (2, 3), (3, 0)))
        if hull is None:
            continue
        clipped = X.clip_to_rect(hull, W, H)
        if len(clipped) < 3 or X.polygon_area(clipped) <= 0:
            continue
        x0, y0 = clipped.min(axis=0)
        x1, y1 = clipped.max(axis=0)
        e = found.setdefault(side, {"box": [x0, y0, x1, y1], "walls": []})
        e["box"] = [min(e["box"][0], x0), min(e["box"][1], y0), max(e["box"][2], x1), max(e["box"][3], y1)]
        e["walls"].append(wid)
    out = {}
    for side, e in sorted(found.items()):
        box = [int(math.floor(e["box"][0])), int(math.floor(e["box"][1])), int(math.ceil(e["box"][2])),
               int(math.ceil(e["box"][3]))]
        out[side] = {"box_px": box, "area_frac": round(((box[2] - box[0]) * (box[3] - box[1])) / float(W * H), 5),
                     "walls": sorted(e["walls"])}
    return out


def outer_wall_sides(vb: dict, sc: dict) -> dict[str, tuple]:
    """``{wall id: (outward, side)}`` of every outer wall of the variant (``exterior: true`` or, without the
    flag, a wall one side of which lies outside its level's outline)."""
    from wenart.blender import geom2d
    from wenart.blender.shell import outward_side

    by_level: dict[str, list] = {}
    for w in vb.get("walls") or []:
        by_level.setdefault(w.get("level_id"), []).append(w)
    flagged = any("exterior" in w for w in vb.get("walls") or [])
    out: dict[str, tuple] = {}
    for lid, ws in by_level.items():
        outline = geom2d.wall_outline(ws)[0]
        if len(outline) < 3:
            continue
        for w in ws:
            if flagged and not w.get("exterior"):
                continue
            mid = ((w["start"][0] + w["end"][0]) / 2.0, (w["start"][1] + w["end"][1]) / 2.0)
            outward = outward_side(w, outline, mid)
            if outward is None:
                continue
            out[w["id"]] = (outward, side_name(outward, sc["north"], sc["north_known"]))
    return out


def facade_records(camera: dict, size, sc: dict, projected: dict, min_visible: float) -> list[dict]:
    """The facades in view: ``[{"side", "box_px", "area_frac", "walls", "windows", "doors", "partial_windows",
    "partial_doors", "ids"}]``.

    ``projected``: the cross-check's ``projected`` record per opening id (visible share, in view). An opening
    counts as expected in full when its visible share is at least ``min_visible``, as partial when it is seen
    at all; the VLM count of the facade crop is judged against ``[windows, windows + partial_windows]``."""
    boxes = facade_boxes(camera, size, sc)
    out = []
    for side, b in boxes.items():
        rec = {"side": side, **b, "windows": 0, "doors": 0, "partial_windows": 0, "partial_doors": 0, "ids": []}
        for oid, info in sorted(sc["openings"].items()):
            if info["side"] != side:
                continue
            p = projected.get(oid)
            if not p or not p.get("visible_share"):
                continue
            kind = info["type"]
            if p["visible_share"] >= min_visible:
                rec["windows" if kind == "window" else "doors"] += 1
            else:
                rec["partial_windows" if kind == "window" else "partial_doors"] += 1
            rec["ids"].append(oid)
        out.append(rec)
    return out


# --------------------------------------------------------------------------
# Roof
# --------------------------------------------------------------------------

def triangle_samples(a, b, c, spacing: float, cap: int = 4000) -> np.ndarray:
    """Cell-centre samples (N x 3) of the triangle ``a b c`` on a barycentric grid of about ``spacing`` metres."""
    a, b, c = (np.asarray(p, dtype=np.float64) for p in (a, b, c))
    n = int(min(60, max(1, math.ceil(max(np.linalg.norm(b - a), np.linalg.norm(c - a),
                                         np.linalg.norm(c - b)) / max(spacing, 1e-3)))))
    pts = []
    for i in range(n):
        for j in range(n - i):
            u, v = (i + 1.0 / 3.0) / n, (j + 1.0 / 3.0) / n
            pts.append(a + u * (b - a) + v * (c - a))
            if i + j + 1 < n:                          # the second triangle of the cell
                u, v = (i + 2.0 / 3.0) / n, (j + 2.0 / 3.0) / n
                pts.append(a + u * (b - a) + v * (c - a))
    arr = np.array(pts).reshape(-1, 3)
    if len(arr) > cap:
        arr = arr[np.linspace(0, len(arr) - 1, cap).astype(int)]
    return arr


def roof_planes(vb: dict) -> tuple[list[dict], str]:
    """``(planes, source)`` of the roof of a building JSON: its drawn planes, else the derived ones
    (``wenart.blender.roof.planes_for``), else ``([], reason)``."""
    roof = vb.get("roof")
    if not isinstance(roof, dict):
        return [], "no roof in the building JSON (the build makes a flat roof over the top level: assumed)"
    drawn = [p for p in roof.get("planes") or [] if isinstance(p, dict) and len(p.get("points") or []) >= 3]
    if drawn:
        return drawn, "building"
    try:
        from wenart.blender.roof import planes_for
        derived = [p for p in planes_for(roof, vb) or [] if len(p.get("points") or []) >= 3]
    except Exception as exc:  # noqa: BLE001 - the roof check then says it could not derive planes
        return [], f"roof planes could not be derived ({type(exc).__name__}: {exc})"
    return (derived, "derived") if derived else ([], "roof planes could not be derived")


def _in_polygon(point, polygon) -> bool:
    from wenart import geometry as G

    return G.point_in_polygon(point, [tuple(p[:2]) for p in polygon])


def roof_check(view, camera: dict, vb: dict, depth_m: np.ndarray, cfg: dict) -> dict:
    """The roof check of one exterior view (module docstring): ``{"planes", "planes_source", "samples",
    "in_frame", "area_frac", "expected", "present", "sky", "behind", "occluded", "present_share", "result",
    "note"}``; ``result`` is ``ok`` / ``partial`` / ``missing`` for a roof in view, ``not_in_view`` / ``not_checked``
    otherwise."""
    from wenart.vision_check import expected as X

    rc = cfg.get("roof") or {}
    spacing = float(rc.get("sample_m", 0.4))
    tol = float(rc.get("tolerance_m", 0.25))
    W, H = int(view.size[0]), int(view.size[1])
    planes, source = roof_planes(vb)
    out = {"planes": len(planes), "planes_source": source if planes else None, "samples": 0, "in_frame": 0,
           "area_frac": 0.0, "expected": False, "present": 0, "sky": 0, "behind": 0, "occluded": 0,
           "present_share": None, "result": "not_checked", "note": None}
    if not planes:
        out["note"] = source
        return out
    holes = [o.get("polygon") for o in (vb.get("roof") or {}).get("openings") or [] if o.get("polygon")]
    pts = []
    for pl in planes:
        p = [tuple(float(c) for c in q) for q in pl["points"]]
        for k in range(1, len(p) - 1):
            pts.append(triangle_samples(p[0], p[k], p[k + 1], spacing))
    samples = np.concatenate(pts) if pts else np.zeros((0, 3))
    if holes:
        keep = np.array([not any(_in_polygon((s[0], s[1]), h) for h in holes) for s in samples], dtype=bool)
        samples = samples[keep]
    out["samples"] = int(len(samples))
    if not len(samples):
        out["note"] = "no roof sample outside the roof openings"
        return out
    uv, z = X.project_points(samples, camera, (W, H))
    front = z > X.NEAR_M
    with np.errstate(invalid="ignore"):
        inside = front & (uv[:, 0] >= 0) & (uv[:, 0] < W) & (uv[:, 1] >= 0) & (uv[:, 1] < H)
    out["in_frame"] = int(inside.sum())
    hull = X.convex_hull(uv[front]) if front.any() else None
    out["area_frac"] = (round(X.polygon_area(X.clip_to_rect(hull, W, H)) / float(W * H), 5)
                        if hull is not None and len(hull) >= 3 else 0.0)
    if not inside.any():
        out["result"] = "not_in_view"
        out["note"] = "the roof is not in the frame"
        return out
    ui = np.clip(np.floor(uv[inside, 0]).astype(int), 0, W - 1)
    vi = np.clip(np.floor(uv[inside, 1]).astype(int), 0, H - 1)
    rendered = depth_m[vi, ui]
    zin = z[inside]
    sky = rendered <= 0
    present = ~sky & (np.abs(zin - rendered) <= tol)
    occluded = ~sky & (rendered < zin - tol)
    behind = ~sky & (rendered > zin + tol)
    out.update(present=int(present.sum()), sky=int(sky.sum()), behind=int(behind.sum()), occluded=int(occluded.sum()))
    seen = out["present"] + out["sky"] + out["behind"]
    min_samples = int(rc.get("min_samples", 25))
    out["expected"] = bool(seen >= min_samples and out["area_frac"] >= float(rc.get("min_area_frac", 0.01)))
    if seen:
        out["present_share"] = round(out["present"] / float(seen), 4)
    if not out["expected"]:
        out["result"] = "not_in_view"
        out["note"] = "too little of the roof is in the frame and unhidden to judge it"
        return out
    if out["present_share"] >= float(rc.get("ok_share", 0.6)):
        out["result"] = "ok"
    elif out["present_share"] >= float(rc.get("missing_share", 0.2)):
        out["result"] = "partial"
    else:
        out["result"] = "missing"
    return out


# --------------------------------------------------------------------------
# The record of an expected view
# --------------------------------------------------------------------------

def block(view, camera: dict, sc: dict, crosscheck: dict, cfg: dict) -> dict:
    """The ``exterior`` record of an expected exterior view: variant, view kind and sides of the camera, the
    outer openings the camera plan expected to see, the facades in view (counts and boxes for the advisory
    VLM count) and the roof check."""
    ecfg = cfg.get("exterior") or {}
    cc = cfg["crosscheck"]
    size = (int(view.size[0]), int(view.size[1]))
    facades = facade_records(camera, size, sc, crosscheck.get("projected") or {},
                             float(ecfg.get("min_visible_share", cc["min_visible_share"])))
    keep = [f for f in facades if f["area_frac"] >= float(ecfg.get("facade_min_area_frac", 0.02))
            and (f["windows"] + f["doors"] + f["partial_windows"] + f["partial_doors"]) > 0]
    roof = {"result": "not_checked", "note": "depth map not readable"}
    try:
        depth_m = view.read_depth_mm().astype(np.float64) / 1000.0
        if depth_m.shape == (size[1], size[0]):
            roof = roof_check(view, camera, sc["building"], depth_m, cfg)
        else:
            roof["note"] = f"depth_mm is {depth_m.shape[1]}x{depth_m.shape[0]}, the view is {size[0]}x{size[1]}"
    except (OSError, ValueError) as exc:
        roof["note"] = f"depth_mm unreadable: {exc}"
    planned = [str(i) for i in camera.get("visible_openings") or []]
    seen = sorted(oid for oid, p in (crosscheck.get("projected") or {}).items()
                  if oid in sc["openings"] and (p.get("visible_share") or 0) >= float(cc["min_visible_share"]))
    return {"variant": sc["variant"], "view": camera.get("view"), "sides": list(camera.get("sides") or []),
            "region_id": camera.get("region_id"), "north": sc["north"], "north_source": sc["north_source"],
            "levels": list(sc["level_ids"]), "outer_openings": len(sc["openings"]),
            "planned_openings": planned, "seen_openings": seen,
            "planned_not_seen": sorted(set(planned) - set(seen)), "seen_not_planned": sorted(set(seen) - set(planned)),
            "facades": keep, "roof": roof, "warnings": list(sc["warnings"])}
