"""Expected elements per view (docs/milestone5.md §1.4, §5.1).

What: for every rendered view, the doors, windows, furniture and decor the
Cycles render shows (from the object-index pass through ``wenart.views``),
each with its role (required / optional / ignore), pixel boxes, visibility and
evidence, plus a non-circular cross-check against the building JSON projected
with a depth test. The polish prompt (area B), the gate's CPU negatives
(area C), select-controls and the vision check all read this, so the role
logic lives only here.

How:

- Elements: one per pass index of ``view.index_stats`` (``views.index_table``
  maps it to the wenart id, kind, type, room, source, status, evidence and
  ``box3d``). ``own_room``: furniture/decor whose ``room_id`` is the camera's
  room; openings whose ``room_ids`` hold it. Scene manifests made before M5
  have no ``room_ids`` on openings: then the rooms come from the building
  JSON (the room polygon edge that carries the opening's wall,
  ``wenart.blender.cameras.room_openings``).
- Visibility (furniture/decor): the ``box3d`` corners projected with the
  pinhole formula of ``wenart/blender/cameras.py`` (24 mm lens on a 36 mm
  sensor, horizontal sensor fit, look-at with world up +Z; the box is clipped
  at the camera's near plane first): in-frame share of the projected hull x
  ``min(1, pixels / in-frame hull area)``. Openings: None.
- Roles (thresholds in ``check.yaml: roles``): ``ignore`` below 0.2 % of the
  frame; ``required`` for own-room doors, windows and furniture with
  area_frac >= 0.03, or >= 0.01 when the visibility is unknown or >= 0.35;
  everything else (decor, other rooms) ``optional``. Unverified pieces and
  type ``unknown`` are flagged ``type_unverified`` (asked as "furniture piece
  (type unverified)"; only present/absent counts for them).
- JSON cross-check: every door, window and furniture piece of the camera's
  level in the building JSON becomes an oriented 3D shape: a piece is its
  drawn footprint box with the height the scene built (the scene manifest's
  ``box3d`` height of that id, else ``wenart.blender.parametric.piece_bbox``:
  a library asset whose file is missing is built as a lower parametric
  piece); a door or window is the
  rectangle on the wall centre line (wall + centre + sill/height defaults of
  ``wenart.blender.shell.opening_vertical``: door 2.10 m, window sill 0.90 m,
  height 1.20 m or 1.40 m above 1.5 m width). Samples on its camera-facing
  faces (4 cm grid) are projected and depth-tested against ``depth_mm``: a
  sample is visible when nothing was rendered more than 5 cm in front of it
  (``z <= rendered + tolerance``, background counts as far), so a missing
  element (rendered surface behind it) and a present one both pass while an
  occluded one does not. ``in_json_not_rendered``: visible share >= 0.35 and
  projected in-frame area >= 0.01 of the frame while its index is absent;
  ``rendered_not_in_json``: an index id with no building element;
  ``misplaced``: the element's own index pixels, put back into the world
  with their depth, lie more than ``misplaced_margin_m`` (0.10 m) outside
  its drawn shape (a piece's footprint, any height; an opening's rectangle as
  deep as its wall) for more than ``misplaced_max_outside`` (10 %) of them.
  (Comparing the index-box centre with the centre of the projected box
  flagged correctly placed beds and armchairs: the box holds air above a
  mattress or a seat, and a library height the scene did not build.)
  These are mismatches of the Cycles render, never fixed.

Imports only stdlib, numpy, yaml (lazily), ``wenart.views`` and
``wenart.geometry`` at import time; the pure Blender helpers named above are
imported lazily inside the functions that need them (no ``bpy``).
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

import numpy as np

from wenart import geometry, views

CONFIG_PATH = Path(__file__).resolve().parent / "check.yaml"

REQUIRED_KINDS = ("door", "window", "furniture")
TYPE_UNVERIFIED_TEXT = "furniture piece (type unverified)"
NEAR_M = 0.05                 # camera clip_start of wenart/blender/cameras.py
DEFAULT_LENS_MM = 24.0
DEFAULT_SENSOR_MM = 36.0
SAMPLE_SPACING_M = 0.04       # grid of the cross-check samples on each face
MAX_SAMPLES_PER_AXIS = 60

# The 8 corners of a box are ordered by (sx, sy, sz) in {-0.5, 0.5}^3: index 4*ix + 2*iy + iz.
_BOX_EDGES = tuple((a, b) for a in range(8) for b in range(a + 1, 8) if bin(a ^ b).count("1") == 1)


_DEFAULT_CFG: Optional[dict] = None


def load_cfg(cfg: Optional[dict] = None) -> dict:
    """``cfg`` or this package's ``check.yaml`` (resolved relative to the package, §1.1; read once)."""
    global _DEFAULT_CFG
    if cfg is not None:
        return cfg
    if _DEFAULT_CFG is None:
        import yaml
        with open(CONFIG_PATH, encoding="utf-8") as fh:
            _DEFAULT_CFG = yaml.safe_load(fh)
    return _DEFAULT_CFG


# --------------------------------------------------------------------------
# Camera maths (the pinhole of wenart/blender/cameras.py)
# --------------------------------------------------------------------------

def camera_basis(position, target) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(forward, right, up)`` unit vectors of a look-at camera with world up +Z.

    Same as ``(target - pos).to_track_quat('-Z', 'Y')`` in cameras.py: the
    camera's up is the world +Z made orthogonal to the view direction.
    """
    pos = np.asarray(position, dtype=np.float64)
    f = np.asarray(target, dtype=np.float64) - pos
    f = f / np.linalg.norm(f)
    r = np.cross(f, [0.0, 0.0, 1.0])
    n = np.linalg.norm(r)
    r = np.array([1.0, 0.0, 0.0]) if n < 1e-9 else r / n
    u = np.cross(r, f)
    return f, r, u


def focal_px(camera: dict, width: int) -> float:
    """Focal length in pixels (horizontal sensor fit: the sensor width spans the image width).

    The lens shift (``shift_x``/``shift_y``) moves the principal point, never
    the focal length (docs/milestone6.md §1.3)."""
    lens = float(camera.get("lens_mm") or DEFAULT_LENS_MM)
    sensor = float(camera.get("sensor_mm") or DEFAULT_SENSOR_MM)
    return lens / sensor * float(width)


def project_points(points, camera: dict, size) -> tuple[np.ndarray, np.ndarray]:
    """World points (N x 3) -> ``(uv N x 2 pixels, z N planar depths)``.

    ``u = W/2 - shift_x W + f * (d.r)/(d.f)``, ``v = H/2 + shift_y W - f *
    (d.u)/(d.f)`` with ``d = p - position`` (origin at the image's top-left
    corner; Blender's shift is in units of the larger image side W, the
    camera's ``shift_x``/``shift_y`` default to 0, docs/milestone6.md §1.3).
    ``uv`` is meaningless where ``z <= 0`` (behind the camera); callers mask it.
    """
    pts = np.asarray(points, dtype=np.float64).reshape(-1, 3)
    f, r, u = camera_basis(camera["position"], camera["target"])
    d = pts - np.asarray(camera["position"], dtype=np.float64)
    z = d @ f
    W, H = float(size[0]), float(size[1])
    fpx = focal_px(camera, W)
    cu = W / 2.0 - float(camera.get("shift_x") or 0.0) * W
    cv = H / 2.0 + float(camera.get("shift_y") or 0.0) * W
    with np.errstate(divide="ignore", invalid="ignore"):
        safe = np.where(np.abs(z) > 1e-12, z, 1e-12)
        uv = np.stack([cu + fpx * (d @ r) / safe, cv - fpx * (d @ u) / safe], axis=1)
    return uv, z


def box_corners(box3d: dict) -> np.ndarray:
    """The 8 world corners (8 x 3) of ``{center, size: [w, d, h], rotation_deg}`` (rotation about +Z)."""
    cx, cy, cz = (float(v) for v in box3d["center"])
    w, d, h = (float(v) for v in box3d["size"])
    a = math.radians(float(box3d.get("rotation_deg") or 0.0))
    ca, sa = math.cos(a), math.sin(a)
    out = []
    for sx in (-0.5, 0.5):
        for sy in (-0.5, 0.5):
            for sz in (-0.5, 0.5):
                x, y = sx * w, sy * d
                out.append((cx + ca * x - sa * y, cy + sa * x + ca * y, cz + sz * h))
    return np.array(out, dtype=np.float64)


def convex_hull(points) -> np.ndarray:
    """Convex hull (counter-clockwise in a y-down image, K x 2) by the monotone chain."""
    pts = sorted(set((float(p[0]), float(p[1])) for p in points))
    if len(pts) < 3:
        return np.array(pts, dtype=np.float64).reshape(-1, 2)

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower, upper = [], []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return np.array(lower[:-1] + upper[:-1], dtype=np.float64)


def polygon_area(poly) -> float:
    """Shoelace area of a polygon (K x 2), 0 for fewer than 3 points."""
    p = np.asarray(poly, dtype=np.float64).reshape(-1, 2)
    if len(p) < 3:
        return 0.0
    x, y = p[:, 0], p[:, 1]
    return float(0.5 * abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def clip_to_rect(poly, width: float, height: float) -> np.ndarray:
    """Sutherland-Hodgman clip of a convex polygon to ``[0, W] x [0, H]``."""
    pts = [tuple(p) for p in np.asarray(poly, dtype=np.float64).reshape(-1, 2)]
    for axis, limit, keep_ge in ((0, 0.0, True), (0, float(width), False), (1, 0.0, True), (1, float(height), False)):
        if not pts:
            break

        def inside(p, axis=axis, limit=limit, keep_ge=keep_ge):
            return p[axis] >= limit if keep_ge else p[axis] <= limit

        def cut(a, b, axis=axis, limit=limit):
            t = (limit - a[axis]) / (b[axis] - a[axis])
            return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))

        out = []
        for i in range(len(pts)):
            a, b = pts[i - 1], pts[i]
            if inside(b):
                if not inside(a):
                    out.append(cut(a, b))
                out.append(b)
            elif inside(a):
                out.append(cut(a, b))
        pts = out
    return np.array(pts, dtype=np.float64).reshape(-1, 2)


def projected_hull(corners, camera: dict, size, edges=_BOX_EDGES, near: float = NEAR_M) -> Optional[np.ndarray]:
    """Convex hull in pixels of a convex 3D shape given by its corners and edges, clipped at the near plane.

    Corners in front of the near plane are projected as they are; every edge
    that crosses the plane adds its crossing point, so a box partly behind
    the camera projects to a finite polygon. None when nothing is in front.
    """
    c = np.asarray(corners, dtype=np.float64)
    f, _, _ = camera_basis(camera["position"], camera["target"])
    z = (c - np.asarray(camera["position"], dtype=np.float64)) @ f
    pts = [c[i] for i in range(len(c)) if z[i] > near]
    for a, b in edges:
        if (z[a] > near) != (z[b] > near):
            t = (near - z[a]) / (z[b] - z[a])
            pts.append(c[a] + t * (c[b] - c[a]) + f * 1e-9)
    if len(pts) < 3:
        return None
    uv, _ = project_points(np.array(pts), camera, size)
    return convex_hull(uv)


def box_visibility(box3d: Optional[dict], camera: Optional[dict], size, pixels: int) -> Optional[dict]:
    """``{"in_frame", "unoccluded", "visibility", "hull_px"}`` of a box seen by the camera (§5.1), or None.

    ``in_frame`` = in-frame area of the projected hull / its full area;
    ``unoccluded`` = ``min(1, pixels / in-frame hull area)``; ``visibility``
    = their product. None without a box, a camera or a hull in front.
    """
    if not box3d or camera is None or not box3d.get("center") or not box3d.get("size"):
        return None
    hull = projected_hull(box_corners(box3d), camera, size)
    if hull is None:
        return None
    full = polygon_area(hull)
    if full <= 0:
        return None
    inside = polygon_area(clip_to_rect(hull, size[0], size[1]))
    in_frame = min(1.0, inside / full)
    unoccluded = min(1.0, pixels / inside) if inside > 0 else 0.0
    return {"in_frame": round(in_frame, 4), "unoccluded": round(unoccluded, 4),
            "visibility": round(in_frame * unoccluded, 4), "hull_px": round(inside, 1)}


# --------------------------------------------------------------------------
# Roles
# --------------------------------------------------------------------------

def role_of(kind: str, own_room: bool, area_frac: float, visibility: Optional[float], roles: dict,
            touches_border: bool = False) -> str:
    """``ignore`` / ``required`` / ``optional`` by the §5.1 rule (thresholds from ``check.yaml: roles``).

    Calibrated on run 1b (2 Oct 2026, 87 clean Cycles views, both models): 34 of the 36 required elements
    the models did not confirm touched the image border, mostly furniture whose visible share was below
    0.35 (a wardrobe side filling an edge) and doors at the frame edge. Furniture therefore needs
    ``furniture_min_visibility`` and openings that touch the border are optional unless
    ``border_openings_required``; optional elements are still asked and still count in the differential
    polish decision (§5.5)."""
    if area_frac < float(roles["ignore_area_frac"]):
        return "ignore"
    if kind not in REQUIRED_KINDS or not own_room:
        return "optional"
    if kind == "furniture":
        floor = roles.get("furniture_min_visibility")
        if floor is not None and visibility is not None and visibility < float(floor):
            return "optional"
    elif touches_border and not roles.get("border_openings_required", True):
        return "optional"
    if area_frac >= float(roles["required_area_frac"]):
        return "required"
    if area_frac >= float(roles["required_min_area_frac"]) and (
            visibility is None or visibility >= float(roles["required_min_visibility"])):
        return "required"
    return "optional"


def is_type_unverified(kind: str, element_type: Optional[str], status: Optional[str]) -> bool:
    """Furniture whose type cannot be trusted (status ``unverified`` or type ``unknown``), or an index
    the scene manifest does not know (kind ``unknown``)."""
    if kind == "unknown":
        return True
    return kind == "furniture" and (status == "unverified" or element_type in (None, "", "unknown"))


# --------------------------------------------------------------------------
# Building lookups
# --------------------------------------------------------------------------

def camera_of(view, scene_manifest: dict) -> Optional[dict]:
    """The scene manifest's camera plan of ``view`` (None when it is not listed)."""
    for cam in scene_manifest.get("cameras") or []:
        if cam.get("name") == view.camera:
            return cam
    return None


def _room_polygon(room: dict) -> list:
    poly = [tuple(p[:2]) for p in room.get("polygon") or []]
    if len(poly) > 1 and geometry.distance(poly[0], poly[-1]) < 1e-9:
        poly = poly[:-1]
    return poly


def opening_rooms(building: dict) -> dict[str, list[str]]:
    """``{opening_id: [room ids]}``: rooms whose polygon edge carries the opening (pre-M5 fallback).

    Uses ``wenart.blender.cameras.room_openings`` (pure Python), the rule the
    M5 build uses for the manifest's ``room_ids``.
    """
    from wenart.blender.cameras import room_openings

    out: dict[str, list[str]] = {o["id"]: [] for o in building.get("openings") or []}
    for room in building.get("rooms") or []:
        poly = _room_polygon(room)
        if len(poly) < 3:
            continue
        try:
            found = room_openings(room, poly, building)
        except (KeyError, TypeError, ValueError):
            continue
        for o in found:
            if room["id"] not in out.setdefault(o["id"], []):
                out[o["id"]].append(room["id"])
    return out


def building_ids(building: dict) -> set:
    """Every element id of the building JSON that can carry a pass index."""
    ids = set()
    for key in ("furniture", "openings", "decor"):
        for item in building.get(key) or []:
            if item.get("id"):
                ids.add(item["id"])
        if key == "furniture":
            for piece in building.get(key) or []:
                for d in piece.get("decor") or []:
                    if isinstance(d, dict) and d.get("id"):
                        ids.add(d["id"])
    return ids


# --------------------------------------------------------------------------
# Expected elements of one view
# --------------------------------------------------------------------------

def _touches_border(box, width: int, height: int) -> bool:
    return box[0] <= 0 or box[1] <= 0 or box[2] >= width or box[3] >= height


def expected_view(view: "views.View", scene_manifest: dict, building: dict, cfg: Optional[dict] = None) -> dict:
    """Expected elements of one view and its building-JSON cross-check (§5.1).

    Returns ``{"camera", "room_id", "room_type", "level_id", "size": [W, H],
    "elements": [...], "json_crosscheck": {...}, "warnings": [...]}``;
    elements sorted by descending pixels (then pass index). Element keys:
    ``index, wenart_id, kind, type, type_unverified, source, status,
    room_id, room_ids, own_room, pixels, area_frac, box_px, box_1000,
    touches_border, visibility, in_frame, unoccluded, evidence, host_decor,
    role``.
    """
    cfg = load_cfg(cfg)
    roles = cfg["roles"]
    W, H = int(view.size[0]), int(view.size[1])
    n_px = float(W * H)
    table = views.index_table(scene_manifest)
    camera = camera_of(view, scene_manifest)
    cam_room = view.room_id or (camera or {}).get("room_id")
    level_id = view.level_id or (camera or {}).get("level_id")
    rooms = {r["id"]: r for r in building.get("rooms") or []}
    room = rooms.get(cam_room) or {}
    warnings: list[str] = []
    if camera is None:
        warnings.append(f"{view.camera}: camera not in the scene manifest; no visibility and no cross-check")

    # Openings with explicit room_ids (M5 manifests); others fall back to the building JSON.
    explicit = {str(o.get("wenart_id")) for o in scene_manifest.get("objects") or []
                if o.get("kind") in ("door", "window", "opening") and "room_ids" in o}
    fallback_rooms: Optional[dict] = None

    elements = []
    for index, stats in sorted(view.index_stats.items()):
        pixels = int(stats["pixels"])
        box = [int(v) for v in stats["box"]]
        entry = table.get(int(index))
        if entry is None:
            warnings.append(f"{view.camera}: pass index {index} is not in the scene manifest")
            entry = {"wenart_id": f"index:{index}", "kind": "unknown", "type": "unknown", "room_id": None,
                     "room_ids": [], "host_decor": [], "evidence": [], "status": None, "source": None, "box3d": None}
        kind = entry["kind"]
        if kind in ("door", "window"):
            room_ids = list(entry.get("room_ids") or [])
            if entry["wenart_id"] not in explicit:
                if fallback_rooms is None:
                    fallback_rooms = opening_rooms(building)
                room_ids = fallback_rooms.get(entry["wenart_id"], [])
            own = cam_room is not None and cam_room in room_ids
        else:
            room_ids = list(entry.get("room_ids") or ([entry["room_id"]] if entry.get("room_id") else []))
            own = cam_room is not None and entry.get("room_id") == cam_room
        area_frac = pixels / n_px if n_px else 0.0
        vis = None
        if kind in ("furniture", "decor"):
            vis = box_visibility(entry.get("box3d"), camera, (W, H), pixels)
        visibility = None if vis is None else vis["visibility"]
        etype = entry.get("type") or kind
        elements.append({
            "index": int(index),
            "wenart_id": entry["wenart_id"],
            "kind": kind,
            "type": etype,
            "type_unverified": is_type_unverified(kind, etype, entry.get("status")),
            "source": entry.get("source"),
            "status": entry.get("status"),
            "room_id": entry.get("room_id"),
            "room_ids": room_ids,
            "own_room": bool(own),
            "pixels": pixels,
            "area_frac": round(area_frac, 6),
            "box_px": box,
            "box_1000": views.box_to_1000(box, W, H),
            "touches_border": _touches_border(box, W, H),
            "visibility": visibility,
            "in_frame": None if vis is None else vis["in_frame"],
            "unoccluded": None if vis is None else vis["unoccluded"],
            "evidence": entry.get("evidence") or [],
            "host_decor": list(entry.get("host_decor") or []),
            "role": role_of(kind, bool(own), area_frac, visibility, roles, touches_border=_touches_border(box, W, H)),
        })
    elements.sort(key=lambda e: (-e["pixels"], e["index"]))

    crosscheck = json_crosscheck(view, camera, building, table, cfg, level_id)
    return {
        "camera": view.camera,
        "room_id": cam_room,
        "room_type": room.get("room_type"),
        "room_label": room.get("label"),
        "level_id": level_id,
        "size": [W, H],
        "render_key": view.render_key,
        "hidden": list(view.hidden),
        "elements": elements,
        "json_crosscheck": crosscheck,
        "warnings": warnings,
    }


# --------------------------------------------------------------------------
# Building-JSON cross-check
# --------------------------------------------------------------------------

def _grid(n: int) -> np.ndarray:
    return (np.arange(n, dtype=np.float64) + 0.5) / n - 0.5


def _axis_count(length: float) -> int:
    return int(min(MAX_SAMPLES_PER_AXIS, max(2, math.ceil(abs(length) / SAMPLE_SPACING_M))))


def rect_samples(center, axis_a, axis_b, len_a: float, len_b: float) -> np.ndarray:
    """Cell-centre samples (N x 3) of a 3D rectangle spanned by two unit axes."""
    c = np.asarray(center, dtype=np.float64)
    a = np.asarray(axis_a, dtype=np.float64)
    b = np.asarray(axis_b, dtype=np.float64)
    ga = _grid(_axis_count(len_a)) * len_a
    gb = _grid(_axis_count(len_b)) * len_b
    A, B = np.meshgrid(ga, gb, indexing="ij")
    return c + A.reshape(-1, 1) * a + B.reshape(-1, 1) * b


def box_faces(box3d: dict) -> list[tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """``[(face centre, outward normal, samples)]`` for the 6 faces of an oriented box."""
    cx, cy, cz = (float(v) for v in box3d["center"])
    w, d, h = (float(v) for v in box3d["size"])
    a = math.radians(float(box3d.get("rotation_deg") or 0.0))
    ex = np.array([math.cos(a), math.sin(a), 0.0])
    ey = np.array([-math.sin(a), math.cos(a), 0.0])
    ez = np.array([0.0, 0.0, 1.0])
    c = np.array([cx, cy, cz])
    faces = []
    for normal, half, (u, lu), (v, lv) in ((ex, w, (ey, d), (ez, h)), (ey, d, (ex, w), (ez, h)),
                                           (ez, h, (ex, w), (ey, d))):
        for sign in (1.0, -1.0):
            centre = c + sign * normal * half / 2.0
            faces.append((centre, sign * normal, rect_samples(centre, u, v, lu, lv)))
    return faces


def opening_shape(opening: dict, building: dict, level: dict) -> Optional[dict]:
    """``{"corners" (4 x 3), "samples", "normal"}`` of a door/window: the rectangle on the wall centre line.

    Centre projected onto the wall centre line, bottom/top from the JSON or
    the build defaults (``wenart.blender.shell.opening_vertical``). None when
    the wall is unknown.
    """
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    walls = {w["id"]: w for w in building.get("walls") or []}
    wall = walls.get(opening.get("wall_id"))
    if wall is None:
        return None
    floor_z = float(level["elevation"])
    has_above = any(float(lv["elevation"]) > floor_z for lv in building.get("levels") or [])
    bottom, top, _ = opening_vertical(opening, level, has_above)
    cx, cy, _ = opening_centre_on_wall(opening, wall)
    ang = math.radians(geometry.segment_angle_deg(wall["start"], wall["end"]))
    along = np.array([math.cos(ang), math.sin(ang), 0.0])
    across = np.array([-math.sin(ang), math.cos(ang), 0.0])
    width = float(opening["width"])
    height = float(top - bottom)
    centre = np.array([cx, cy, (bottom + top) / 2.0])
    corners = np.array([centre + sa * along * width / 2.0 + np.array([0.0, 0.0, sz * height / 2.0])
                        for sa in (-1.0, 1.0) for sz in (-1.0, 1.0)])
    return {"corners": corners, "samples": rect_samples(centre, along, [0.0, 0.0, 1.0], width, height),
            "normal": across, "two_sided": True,
            "edges": ((0, 1), (0, 2), (1, 3), (2, 3)),
            # The drawn volume of the frame/leaf/glass: the opening rectangle as deep as the wall.
            "extent": {"center": centre, "axes": [(along, width / 2.0),
                                                  (across, float(wall.get("thickness") or 0.0) / 2.0),
                                                  (np.array([0.0, 0.0, 1.0]), height / 2.0)]}}


def furniture_box3d(piece: dict, level: dict, height: Optional[float] = None) -> dict:
    """The oriented box of a building piece: drawn footprint x the height the scene builds.

    ``height``: the height of the box the scene manifest records for that id
    (what was built: a library asset whose file is missing falls back to a
    lower parametric piece); None = ``piece_bbox`` from the building JSON.
    Footprint and position always come from the building JSON.
    """
    from wenart.blender.parametric import piece_bbox

    fp = piece["footprint"]
    h = float(height) if height else piece_bbox(piece)[2]
    floor_z = float(level["elevation"])
    return {"center": [float(fp["center"][0]), float(fp["center"][1]), floor_z + h / 2.0],
            "size": [float(fp["size"][0]), float(fp["size"][1]), float(h)],
            "rotation_deg": float(fp.get("rotation_deg") or 0.0)}


def _depth_visible(samples: np.ndarray, camera: dict, size, depth_m: np.ndarray, tol: float
                   ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(uv, in_frame mask, visible mask)`` of world samples against a rendered depth map (metres, 0 = far)."""
    W, H = int(size[0]), int(size[1])
    uv, z = project_points(samples, camera, (W, H))
    front = z > NEAR_M
    with np.errstate(invalid="ignore"):
        inside = front & (uv[:, 0] >= 0) & (uv[:, 0] < W) & (uv[:, 1] >= 0) & (uv[:, 1] < H)
    visible = np.zeros(len(samples), dtype=bool)
    if inside.any():
        ui = np.clip(np.floor(uv[inside, 0]).astype(int), 0, W - 1)
        vi = np.clip(np.floor(uv[inside, 1]).astype(int), 0, H - 1)
        rendered = depth_m[vi, ui]
        visible[inside] = (rendered <= 0) | (z[inside] <= rendered + tol)
    return uv, inside, visible


def project_element(shape_samples: np.ndarray, hull: Optional[np.ndarray], camera: dict, size,
                    depth_m: np.ndarray, tol: float) -> dict:
    """Visible share, in-frame area fraction and visible-sample box of one projected element."""
    W, H = int(size[0]), int(size[1])
    total = len(shape_samples)
    out = {"samples": int(total), "visible_share": 0.0, "area_frac": 0.0, "box_px": None, "centre_px": None,
           "visible_samples": 0}
    if total:
        uv, _, vis = _depth_visible(shape_samples, camera, (W, H), depth_m, tol)
        n_vis = int(vis.sum())
        out["visible_samples"] = n_vis
        out["visible_share"] = round(n_vis / total, 4)
        if n_vis:
            pts = uv[vis]
            box = [float(pts[:, 0].min()), float(pts[:, 1].min()), float(pts[:, 0].max()), float(pts[:, 1].max())]
            out["box_px"] = [round(v, 1) for v in box]
            out["centre_px"] = [round((box[0] + box[2]) / 2.0, 1), round((box[1] + box[3]) / 2.0, 1)]
    if hull is not None:
        out["area_frac"] = round(polygon_area(clip_to_rect(hull, W, H)) / float(W * H), 5)
    return out


def _front_samples(faces, camera: dict) -> np.ndarray:
    """Samples of the faces that look towards the camera (back faces culled)."""
    pos = np.asarray(camera["position"], dtype=np.float64)
    keep = [s for centre, normal, s in faces if float(np.dot(normal, pos - centre)) > 0.0]
    return np.concatenate(keep) if keep else np.zeros((0, 3))


def unproject_pixels(rows, cols, depth_m: np.ndarray, camera: dict, size) -> np.ndarray:
    """World points (N x 3) of pixel centres (``rows``, ``cols``) at their planar depth (metres).

    The inverse of ``project_points``: ``P = position + z * (f + a * r + b * u)``
    with ``a = (col + 0.5 - W/2 + shift_x W) / f_px`` and ``b = -(row + 0.5 -
    H/2 - shift_y W) / f_px`` (shift 0 when the camera has none).
    """
    W, H = int(size[0]), int(size[1])
    f, r, u = camera_basis(camera["position"], camera["target"])
    fpx = focal_px(camera, W)
    sx = float(camera.get("shift_x") or 0.0)
    sy = float(camera.get("shift_y") or 0.0)
    rows = np.asarray(rows)
    cols = np.asarray(cols)
    z = np.asarray(depth_m, dtype=np.float64)[rows, cols]
    a = (cols + 0.5 - W / 2.0 + sx * W) / fpx
    b = -(rows + 0.5 - H / 2.0 - sy * W) / fpx
    rays = f[None, :] + a[:, None] * r[None, :] + b[:, None] * u[None, :]
    return np.asarray(camera["position"], dtype=np.float64)[None, :] + z[:, None] * rays


def footprint_extent(box3d: dict) -> dict:
    """The drawn footprint of a piece as an extent (its two horizontal axes; the height is not tested)."""
    a = math.radians(float(box3d.get("rotation_deg") or 0.0))
    w, d = float(box3d["size"][0]), float(box3d["size"][1])
    return {"center": np.asarray(box3d["center"], dtype=np.float64),
            "axes": [(np.array([math.cos(a), math.sin(a), 0.0]), w / 2.0),
                     (np.array([-math.sin(a), math.cos(a), 0.0]), d / 2.0)]}


def outside_distance(points, extent: dict) -> np.ndarray:
    """Distance in metres of each world point outside an oriented extent (0 inside).

    ``extent``: ``{"center", "axes": [(unit axis, half length), ...]}``; a
    direction without an axis is unbounded (a piece's height).
    """
    d = np.asarray(points, dtype=np.float64).reshape(-1, 3) - np.asarray(extent["center"], dtype=np.float64)
    out = np.zeros(len(d))
    for axis, half in extent["axes"]:
        out += np.maximum(0.0, np.abs(d @ np.asarray(axis, dtype=np.float64)) - float(half)) ** 2
    return np.sqrt(out)


def placement(mask: np.ndarray, depth_m: np.ndarray, camera: dict, size, extent: dict, margin: float) -> dict:
    """How far an element's rendered pixels lie outside its drawn shape (§5.1 ``misplaced``).

    The element's index pixels with a depth are put back into the world
    (``unproject_pixels``) and measured against the drawn extent: a piece's
    footprint, an opening's rectangle as deep as its wall. Returns
    ``{"pixels", "outside_share" (share more than ``margin`` outside),
    "outside_p90_m"}``. Non-circular: only the drawing, the index pass and
    the depth pass are used, never the scene's own box of the element, so
    neither its shape nor its built height matters.
    """
    rows, cols = np.nonzero(mask & (depth_m > 0))
    out = {"pixels": int(len(rows)), "outside_share": None, "outside_p90_m": None}
    if len(rows):
        dist = outside_distance(unproject_pixels(rows, cols, depth_m, camera, size), extent)
        out["outside_share"] = round(float(np.mean(dist > margin)), 4)
        out["outside_p90_m"] = round(float(np.percentile(dist, 90)), 3)
    return out


def json_crosscheck(view, camera: Optional[dict], building: dict, table: dict, cfg: dict,
                    level_id: Optional[str] = None) -> dict:
    """The §5.1 building-JSON cross-check of one view (see the module docstring)."""
    cc = cfg["crosscheck"]
    tol = float(cc["depth_tolerance_m"])
    W, H = int(view.size[0]), int(view.size[1])
    result = {"level_id": level_id, "tested": 0, "in_json_not_rendered": [], "rendered_not_in_json": [],
              "misplaced": [], "projected": {}, "error": None}
    # Index ids present in the view (wenart id -> pass index) and ids without a building element.
    ids_in_view: dict[str, int] = {}
    known = building_ids(building)
    for index in sorted(view.index_stats):
        entry = table.get(int(index))
        wid = entry["wenart_id"] if entry else f"index:{index}"
        ids_in_view.setdefault(wid, int(index))
        if wid not in known:
            result["rendered_not_in_json"].append({"id": wid, "index": int(index),
                                                   "kind": entry["kind"] if entry else "unknown",
                                                   "pixels": int(view.index_stats[index]["pixels"])})
    if camera is None:
        result["error"] = "camera not in the scene manifest"
        return result
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), None)
    if level is None:
        result["error"] = f"level {level_id!r} not in the building JSON"
        return result
    try:
        depth_m = view.read_depth_mm().astype(np.float64) / 1000.0
    except (OSError, ValueError) as exc:
        result["error"] = f"depth_mm unreadable: {exc}"
        return result
    if depth_m.shape != (H, W):
        result["error"] = f"depth_mm is {depth_m.shape[1]}x{depth_m.shape[0]}, the view is {W}x{H}"
        return result
    try:
        index_map = view.read_index()
    except (OSError, ValueError) as exc:
        result["error"] = f"index unreadable: {exc}"
        return result
    if index_map.shape != (H, W):
        result["error"] = f"index is {index_map.shape[1]}x{index_map.shape[0]}, the view is {W}x{H}"
        return result

    # The height of each piece as the scene built it (the manifest's box3d); position and footprint
    # still come from the building JSON.
    built_height = {e["wenart_id"]: e["box3d"]["size"][2] for e in table.values()
                    if e.get("kind") == "furniture" and (e.get("box3d") or {}).get("size")}
    elements = []
    for o in building.get("openings") or []:
        if o.get("level_id") != level_id or o.get("type") not in ("door", "window"):
            continue
        shape = opening_shape(o, building, level)
        if shape is None:
            continue
        hull = projected_hull(shape["corners"], camera, (W, H), edges=shape["edges"])
        elements.append((o["id"], o["type"], o["type"], "from_documents", o.get("status"), shape["samples"], hull,
                         shape["extent"]))
    for piece in building.get("furniture") or []:
        if piece.get("level_id") != level_id or not piece.get("footprint"):
            continue
        if piece.get("build") is False:
            continue        # a drawn symbol both AI passes call not furniture: never built (docs/milestone7.md §3.3)
        try:
            box3d = furniture_box3d(piece, level, built_height.get(piece["id"]))
        except (KeyError, TypeError, ValueError):
            continue
        samples = _front_samples(box_faces(box3d), camera)
        hull = projected_hull(box_corners(box3d), camera, (W, H))
        elements.append((piece["id"], "furniture", piece.get("type"), piece.get("source"), piece.get("status"),
                         samples, hull, footprint_extent(box3d)))

    margin = float(cc["misplaced_margin_m"])
    hidden = set(getattr(view, "hidden", ()) or ())
    for eid, kind, etype, source, status, samples, hull, extent in elements:
        result["tested"] += 1
        proj = project_element(samples, hull, camera, (W, H), depth_m, tol)
        rendered = eid in ids_in_view
        if proj["visible_samples"] or rendered:
            result["projected"][eid] = {"kind": kind, "type": etype, "visible_share": proj["visible_share"],
                                        "area_frac": proj["area_frac"], "centre_px": proj["centre_px"],
                                        "in_view": rendered}
        if not rendered:
            if eid in hidden:
                continue                      # a control render: hidden on purpose
            if (proj["visible_share"] >= float(cc["min_visible_share"])
                    and proj["area_frac"] >= float(cc["min_area_frac"])):
                result["in_json_not_rendered"].append({
                    "id": eid, "kind": kind, "type": etype, "source": source, "status": status,
                    "visible_share": proj["visible_share"], "area_frac": proj["area_frac"],
                    "box_px": proj["box_px"]})
            continue
        # misplaced: the element's own rendered pixels, put back into the world, outside its drawn shape.
        place = placement(index_map == ids_in_view[eid], depth_m, camera, (W, H), extent, margin)
        result["projected"][eid].update(outside_share=place["outside_share"], rendered_pixels=place["pixels"])
        if place["outside_share"] is None or place["pixels"] < int(cc["misplaced_min_pixels"]):
            continue
        if place["outside_share"] > float(cc["misplaced_max_outside"]):
            result["misplaced"].append({"id": eid, "kind": kind, "type": etype, "source": source,
                                        "status": status, "outside_share": place["outside_share"],
                                        "outside_p90_m": place["outside_p90_m"], "pixels": place["pixels"],
                                        "margin_m": margin})
    return result


# --------------------------------------------------------------------------
# All views of a project
# --------------------------------------------------------------------------

def collect_expected(project_out, render_dir=None, cfg: Optional[dict] = None, cameras=None
                     ) -> tuple[dict, list[str]]:
    """``({camera: expected_view}, warnings)`` for every view of ``render_dir`` (default ``<out>/renders``).

    Stale render entries (made before M5) are skipped with a warning; nothing
    is written.
    """
    paths = views.project_paths(project_out)
    warnings = list(paths["warnings"])
    building: dict = {}
    if Path(paths["building_path"]).is_file():
        building = json.loads(Path(paths["building_path"]).read_text(encoding="utf-8"))
    rdir = Path(render_dir) if render_dir is not None else paths["render_dir"]
    vs = views.load_views(rdir, cameras, skip_stale=True, warnings=warnings)
    cfg = load_cfg(cfg)
    out = {}
    for cam, view in vs.items():
        out[cam] = expected_view(view, paths["scene_manifest"], building, cfg)
        warnings.extend(out[cam]["warnings"])
    return out, warnings


def expected_views(project_out, render_dir=None) -> dict:
    """``{camera: expected_view(...)}`` for every view of the project (pure, writes nothing)."""
    return collect_expected(project_out, render_dir)[0]


def required_count(expected: dict) -> int:
    return sum(1 for e in expected.get("elements") or [] if e.get("role") == "required")


def sweep_views(expected_views: dict, n: int) -> list:
    """Up to ``n`` cameras with the most required elements, at most one per room, ties by camera name."""
    order = sorted(expected_views, key=lambda cam: (-required_count(expected_views[cam]), cam))
    out, rooms = [], set()
    for cam in order:
        if len(out) >= int(n):
            break
        room = expected_views[cam].get("room_id") or f"camera:{cam}"
        if room in rooms:
            continue
        rooms.add(room)
        out.append(cam)
    return out


def largest_required(expected: dict) -> Optional[dict]:
    """The required element with the most pixels of one ``expected_view`` result, or None."""
    best = None
    for e in expected.get("elements") or []:
        if e.get("role") == "required" and (best is None or e["pixels"] > best["pixels"]):
            best = e
    return best
