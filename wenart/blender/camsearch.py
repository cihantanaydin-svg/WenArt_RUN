"""Camera search: score candidate cameras with a coarse ray caster and pick
the best diverse views per room (docs/milestone6.md §1.3, §4).

What: ``plan_level(building, level_id)`` returns the camera plans of every
room of a level for the camera policy ``search`` (``cameras.plan_cameras``
calls it); the plans have the same fields as the M5 plans plus ``shift_x``,
``shift_y``, ``policy``, ``score`` and ``search_seconds``.

Why: the M5 rules (three fixed cameras per room at 1.4 m looking 0.1 m down)
framed bare walls in 17 of 87 views, were blocked in 12 and showed less than
1 % floor in 52. A score computed from what a camera would see picks views
that show the furniture, some floor and a door or window, with straight
verticals (pitch 0, lens shift instead of tilt).

How:

- Model of a room (``RoomModel``): the room prism (floor at the level
  elevation, ceiling at the level's ceiling height, every polygon edge a
  vertical wall), the door and window rectangles on its edges
  (``cameras.room_openings`` and ``shell.opening_vertical``; a plain
  opening is labelled ``opening``, it is neither wall nor element) and the
  room's furniture boxes (``parametric.piece_bbox`` turned by the footprint
  rotation, standing on the floor; decor is ignored). Pure numpy, no
  Blender, no shapely: build.py runs it inside Blender's Python.
- Rays: a 64 x 36 grid over the 1920 x 1080 frame of a 24 mm lens on a
  36 mm sensor (horizontal sensor fit) with the lens shift of §1.3
  (``a = (col + 0.5 - W/2 + shift_x W) / f``, ``b = -(row + 0.5 - H/2 -
  shift_y W) / f``, direction ``forward + a right + b up``). The ray
  parameter is the planar depth along the view axis, the quantity Cycles
  writes into its Z pass and the GPU test reads from ``depth_mm`` (the
  research prototype used the ray length, up to 1.34 x larger in the
  corners of the frame).
- Per candidate: the share of rays of every label (each piece, each door or
  window, floor, ceiling, wall), whether a piece touches the frame border,
  the share of rays nearer than 0.9 m and the median depth of the wall rays.
  ``score_terms`` turns them into the §4.1 score; every constant is in
  ``SCORE``.
- Candidates: free points (``geom2d.point_is_free`` with the wall 0.3 m /
  obstacle 0.2 m clearances of the M5 cameras) on a 0.5 m grid plus two
  points per convex polygon corner (0.45 m and 0.6 m in along the bisector),
  12 yaws (every 30 degrees, 0 = +X, counter-clockwise), height 1.25 m,
  pitch 0, ``shift_y = -0.10``. A room without a free point gets the M5
  fallback point with a warning, anchored at the room's inner point
  (``lighting.polylabel``, always inside the polygon; the centroid of an
  L-shaped room can lie in the notch): that point, or the nearest point
  clear of the tall boxes, or that point inside a box.
- Pick (``select_views``): views per room by the room area (3 from 6 m2,
  2 from 3 m2, else 1); a candidate is blocked when its near share is over
  0.30 or one element covers over 0.50 of the rays; greedy by score among
  the unblocked candidates (ties: score, then x, y, yaw), a later pick must
  differ from every earlier one by at least 50 degrees of yaw or 1.0 m, and a
  pick below 0.5 x the room's best score is dropped (at least one view per
  room). A room with only blocked candidates gets its best one with the
  warning ``blocked unavoidable``. Deterministic: scores are rounded to
  1e-6 before sorting, so float noise never decides a tie.
- Output per plan: ``score`` = ``{total, furniture, openings, floor, depth,
  penalties, blocked, yaw_deg, shares}`` (the terms as they enter the total;
  ``shares`` are the model's ray shares), ``placement`` = the same as text,
  ``visible_openings``/``visible_furniture`` = the room's openings and
  pieces whose centre is inside the shifted frustum (as the M5 lists),
  ``search_seconds`` = the wall time of the level's search (the same value
  on every plan of the level; ``level_search_seconds`` collects it).

CLI (inspection only; the build calls ``plan_level``): ``python -m
wenart.blender.camsearch outputs/<p>/building_final.json --out cameras.json
[--report cameras.md] [--level L0]``.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from wenart import geometry as G
from wenart.blender import cameras, geom2d
from wenart.blender.parametric import obstacle_rect, piece_bbox
from wenart.blender.shell import opening_vertical

POLICY = "search"

# Every constant of the score (docs/milestone6.md §4.1) in one table.
SCORE = {
    "grid": (64, 36),                 # rays across, rays down
    "furniture_factor": 4.0,          # 4 * furn
    "piece_cap": 0.25,                # min(c_k, 0.25) / 0.25
    "border_factor": 0.6,             # a piece touching the frame border counts 0.6
    "openings_cap": 0.12,             # min(open, 0.12) / 0.12
    "floor_cap": 0.25,                # min(floor, 0.25) / 0.25
    "depth_ref_m": 3.0,               # min(d_wall / 3 m, 1)
    "near_m": 0.9,                    # near = share of rays with depth < 0.9 m
    # name: (factor, allowed share): score -= factor * max(0, share - allowed)
    "penalties": {
        "near": (3.0, 0.08),
        "max_single": (3.0, 0.40),
        "wall": (2.0, 0.55),
        "window": (2.0, 0.20),
        "ceiling": (1.0, 0.15),
    },
    "blocked_near": 0.30,             # blocked: near > 0.30 ...
    "blocked_single": 0.50,           # ... or one piece / opening > 0.50
    "type_weight": {
        "bed": 3.0, "bed_double": 3.0, "bed_single": 3.0, "sofa": 3.0, "kitchen_counter": 3.0,
        "kitchen_island": 3.0,
        "bathtub": 2.5,
        "table_dining": 2.0, "desk": 2.0, "toilet": 2.0, "washbasin": 2.0, "shower": 2.0, "sink_kitchen": 2.0,
        "wardrobe": 1.5, "armchair": 1.5, "stove": 1.5, "tv_unit": 1.5, "table_coffee": 1.5,
        "chair": 0.8,
    },
    "default_type_weight": 1.0,
}

# Candidates and the pick (§4.1).
CAMERA_HEIGHT = 1.25
SHIFT_X = 0.0
SHIFT_Y = -0.10
LENS_MM = cameras.LENS_MM            # 24 mm
SENSOR_MM = cameras.SENSOR_MM        # 36 mm
RESOLUTION = cameras.RESOLUTION      # 1920 x 1080
GRID_STEP = 0.5
CORNER_INSETS = (0.45, 0.6)
YAW_STEP_DEG = 30
TARGET_DISTANCE = 1.0
WALL_CLEARANCE = cameras.CAMERA_WALL_CLEARANCE          # 0.3 m
OBSTACLE_CLEARANCE = cameras.CAMERA_OBSTACLE_CLEARANCE  # 0.2 m
MIN_YAW_DIFF_DEG = 50.0
MIN_DISTANCE_M = 1.0
DROP_BELOW_BEST = 0.5
VIEW_AREAS = ((6.0, 3), (3.0, 2))    # (minimum area m2, views); smaller rooms get 1 view
BLOCKED_WARNING = "blocked unavoidable"
SCORE_DECIMALS = 6                   # scores are rounded before sorting (deterministic ties)

# Ray labels; elements (doors, windows, pieces) follow from FIRST_ELEMENT.
NOTHING, FLOOR, CEILING, WALL, OPENING = 0, 1, 2, 3, 4
FIRST_ELEMENT = 5
_EPS_T = 1e-4
_EPS_S = 1e-6


# --------------------------------------------------------------------------
# View count, weights, the score formula
# --------------------------------------------------------------------------

def views_for_area(area_m2: float) -> int:
    """Views of a room by its area: 3 from 6 m2, 2 from 3 m2, else 1."""
    for minimum, n in VIEW_AREAS:
        if area_m2 >= minimum:
            return n
    return 1


def room_polygon(room: dict) -> list[tuple[float, float]]:
    poly = [(float(p[0]), float(p[1])) for p in room["polygon"]]
    if len(poly) > 1 and G.distance(poly[0], poly[-1]) < 1e-9:
        poly = poly[:-1]
    return poly


def room_view_count(room: dict) -> int:
    """Views of ``room`` by the area of its polygon (§4.1; also used by ``wenart.run plan``)."""
    return views_for_area(G.polygon_area(room_polygon(room)))


def type_weight(piece_type: Optional[str]) -> float:
    return float(SCORE["type_weight"].get(piece_type or "", SCORE["default_type_weight"]))


def furniture_share(shares: Sequence[float], touches_border: Sequence[bool], weights: Sequence[float]) -> float:
    """``furn`` of §4.1: ``sum_k w_k min(c_k, cap)/cap (0.6 if k touches the border) / sum_k w_k``
    over the room's pieces (0 for a room without pieces)."""
    total = float(sum(weights))
    if total <= 0:
        return 0.0
    cap = SCORE["piece_cap"]
    acc = 0.0
    for c, border, w in zip(shares, touches_border, weights):
        acc += float(w) * min(float(c), cap) / cap * (SCORE["border_factor"] if border else 1.0)
    return acc / total


def score_terms(m: dict) -> dict:
    """The §4.1 score from the model shares of one camera.

    ``m``: ``furn`` (``furniture_share``), ``open``, ``floor``, ``wall``,
    ``window``, ``ceiling``, ``near``, ``max_single`` (ray shares) and
    ``d_wall`` (metres). Returns the terms as they enter the total:
    ``{"total", "furniture", "openings", "floor", "depth", "penalties", "blocked"}``.
    """
    furniture = SCORE["furniture_factor"] * float(m["furn"])
    openings = min(float(m["open"]), SCORE["openings_cap"]) / SCORE["openings_cap"]
    floor = min(float(m["floor"]), SCORE["floor_cap"]) / SCORE["floor_cap"]
    depth = min(float(m["d_wall"]) / SCORE["depth_ref_m"], 1.0)
    penalties = 0.0
    for name, (factor, allowed) in SCORE["penalties"].items():
        penalties += factor * max(0.0, float(m[name]) - allowed)
    total = furniture + openings + floor + depth - penalties
    return {"total": total, "furniture": furniture, "openings": openings, "floor": floor, "depth": depth,
            "penalties": penalties, "blocked": is_blocked(m)}


def is_blocked(m: dict) -> bool:
    """Blocked: the model's near share is over 0.30 or one element covers over 0.50 of the rays."""
    return bool(float(m["near"]) > SCORE["blocked_near"] or float(m["max_single"]) > SCORE["blocked_single"])


# --------------------------------------------------------------------------
# Rays
# --------------------------------------------------------------------------

def ray_grid(grid=None, lens_mm: float = LENS_MM, sensor_mm: float = SENSOR_MM, resolution=RESOLUTION,
             shift_x: float = 0.0, shift_y: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """``(a, b)`` (each ``rows x cols`` flattened row-major) of the ray grid over the frame.

    A grid cell's centre is the image point ``((i + 0.5) W / cols, (j + 0.5) H / rows)``; ``a``/``b``
    are its horizontal and vertical slopes by the §1.3 inverse projection with shift.
    """
    cols, rows = grid or SCORE["grid"]
    W, H = float(resolution[0]), float(resolution[1])
    fpx = float(lens_mm) / float(sensor_mm) * W
    col = (np.arange(cols) + 0.5) * W / cols
    row = (np.arange(rows) + 0.5) * H / rows
    a = (col - W / 2.0 + float(shift_x) * W) / fpx
    b = -(row - H / 2.0 - float(shift_y) * W) / fpx
    A, B = np.meshgrid(a, b)
    return A.ravel(), B.ravel()


def border_mask(grid=None) -> np.ndarray:
    """Flattened mask of the grid cells on the frame border."""
    cols, rows = grid or SCORE["grid"]
    m = np.zeros((rows, cols), dtype=bool)
    m[0, :] = m[-1, :] = m[:, 0] = m[:, -1] = True
    return m.ravel()


def yaw_directions(yaws_deg: Sequence[float], a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Ray directions (n_yaw x P x 3) of pitch-0 cameras: ``forward + a right + b up``
    with forward = (cos yaw, sin yaw, 0), right = (sin yaw, -cos yaw, 0), up = +Z."""
    yaw = np.radians(np.asarray(yaws_deg, dtype=np.float64))[:, None]
    c, s = np.cos(yaw), np.sin(yaw)
    out = np.empty((yaw.shape[0], a.shape[0], 3))
    out[..., 0] = c + a[None, :] * s
    out[..., 1] = s - a[None, :] * c
    out[..., 2] = b[None, :]
    return out


def camera_directions(position, target, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Ray directions (P x 3) of a look-at camera with world up +Z (any pitch), planar-depth scaled."""
    pos = np.asarray(position, dtype=np.float64)
    f = np.asarray(target, dtype=np.float64) - pos
    f = f / np.linalg.norm(f)
    r = np.cross(f, [0.0, 0.0, 1.0])
    n = np.linalg.norm(r)
    r = np.array([1.0, 0.0, 0.0]) if n < 1e-9 else r / n
    u = np.cross(r, f)
    return f[None, :] + a[:, None] * r[None, :] + b[:, None] * u[None, :]


# --------------------------------------------------------------------------
# The room model
# --------------------------------------------------------------------------

class RoomModel:
    """Ray-cast model of one room (see the module docstring).

    ``elements``: one dict per label from ``FIRST_ELEMENT`` on (``id``,
    ``kind`` door/window/furniture, ``type``, ``weight``), doors and windows
    first (in ``room_openings`` order), then the pieces in building order.
    """

    def __init__(self, room: dict, building: dict, level: Optional[dict] = None):
        self.room = room
        self.level = level or next(lv for lv in building["levels"] if lv["id"] == room["level_id"])
        self.floor_z = float(self.level["elevation"])
        self.ceil_z = self.floor_z + float(self.level["ceiling_height"])
        levels_above = any(float(lv["elevation"]) > self.floor_z for lv in building["levels"])
        self.polygon = room_polygon(room)
        self.pieces = [f for f in building.get("furniture") or []
                       if f.get("room_id") == room["id"] and f.get("kind") != "decor"]
        self.openings = cameras.room_openings(room, self.polygon, building)
        walls = {w["id"]: w for w in building.get("walls", []) if w["level_id"] == room["level_id"]}

        self.elements: list[dict] = []
        codes: dict[str, int] = {}
        for o in self.openings:
            if o["type"] in ("door", "window"):
                codes[o["id"]] = FIRST_ELEMENT + len(self.elements)
                self.elements.append({"id": o["id"], "kind": o["type"], "type": o["type"], "weight": 0.0})
        for f in self.pieces:
            self.elements.append({"id": f["id"], "kind": "furniture", "type": f.get("type"),
                                  "weight": type_weight(f.get("type"))})
        self.n_labels = FIRST_ELEMENT + len(self.elements)
        idx = np.arange(FIRST_ELEMENT, self.n_labels)
        kinds = [e["kind"] for e in self.elements]
        self.piece_codes = idx[[k == "furniture" for k in kinds]] if kinds else idx
        self.opening_codes = idx[[k in ("door", "window") for k in kinds]] if kinds else idx
        self.window_codes = idx[[k == "window" for k in kinds]] if kinds else idx
        self.piece_weights = np.array([e["weight"] for e in self.elements if e["kind"] == "furniture"])

        # Walls: one per polygon edge, with the openings whose centre lies on it.
        self.edges = []
        n = len(self.polygon)
        for i in range(n):
            a, b = self.polygon[i], self.polygon[(i + 1) % n]
            length = G.distance(a, b)
            if length < 1e-9:
                continue
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            spans = []
            for o in self.openings:
                tol = cameras.opening_edge_tolerance(o, walls)
                c = o["center"]
                along = (c[0] - a[0]) * ux + (c[1] - a[1]) * uy
                across = abs((c[0] - a[0]) * -uy + (c[1] - a[1]) * ux)
                if across > tol or along < -cameras.OPENING_EDGE_SLACK or along > length + cameras.OPENING_EDGE_SLACK:
                    continue
                bottom, top, _ = opening_vertical(o, self.level, levels_above)
                code = codes.get(o["id"], OPENING)
                spans.append((along, float(o["width"]) / 2.0, bottom, top, code))
            self.edges.append((a[0], a[1], b[0] - a[0], b[1] - a[1], length, spans))

        # Furniture boxes: piece_bbox in the footprint frame, standing on the floor.
        self.boxes = []
        for k, f in enumerate(self.pieces):
            w, d, h, _ = piece_bbox(f)
            fp = f["footprint"]
            rot = math.radians(float(fp.get("rotation_deg") or 0.0))
            self.boxes.append((FIRST_ELEMENT + len(self.elements) - len(self.pieces) + k,
                               float(fp["center"][0]), float(fp["center"][1]), self.floor_z + h / 2.0,
                               w / 2.0, d / 2.0, h / 2.0, math.cos(rot), math.sin(rot)))

    # ------------------------------------------------------------------
    def cast(self, origin, dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """``(labels int32, depth float)`` of rays from ``origin`` along ``dirs`` (N x 3 or ... x 3).

        ``depth`` is the ray parameter (planar depth for the planar-scaled
        directions of this module); ``inf`` with label ``NOTHING`` where no
        surface was hit."""
        shape = dirs.shape[:-1]
        d = dirs.reshape(-1, 3)
        ox, oy, oz = (float(v) for v in origin)
        dx, dy, dz = d[:, 0], d[:, 1], d[:, 2]
        with np.errstate(divide="ignore", invalid="ignore"):
            tf = np.where(dz < 0, (self.floor_z - oz) / dz, np.inf)
            tc = np.where(dz > 0, (self.ceil_z - oz) / dz, np.inf)
        tf = np.where(tf > _EPS_T, tf, np.inf)
        tc = np.where(tc > _EPS_T, tc, np.inf)
        depth = np.minimum(tf, tc)
        labels = np.where(tf <= tc, FLOOR, CEILING).astype(np.int32)
        labels[~np.isfinite(depth)] = NOTHING

        for ax, ay, ex, ey, length, spans in self.edges:
            den = dx * ey - dy * ex
            rx, ry = ax - ox, ay - oy
            with np.errstate(divide="ignore", invalid="ignore"):
                t = (rx * ey - ry * ex) / den
                s = (rx * dy - ry * dx) / den
            ok = (np.abs(den) > 1e-12) & (t > _EPS_T) & (s >= -_EPS_S) & (s <= 1.0 + _EPS_S) & (t < depth)
            if not ok.any():
                continue
            z = oz + t * dz
            ok &= (z >= self.floor_z - 1e-9) & (z <= self.ceil_z + 1e-9)
            lab = np.full(d.shape[0], WALL, dtype=np.int32)
            along = s * length
            for centre, half, bottom, top, code in spans:
                inside = ok & (np.abs(along - centre) <= half) & (z >= bottom) & (z <= top)
                lab[inside] = code
            depth = np.where(ok, t, depth)
            labels = np.where(ok, lab, labels)

        for code, cx, cy, cz, hw, hd, hh, c, s in self.boxes:
            # World -> box frame: turn by -rotation about the box centre.
            px, py, pz = ox - cx, oy - cy, oz - cz
            lox, loy = c * px + s * py, -s * px + c * py
            ldx, ldy = c * dx + s * dy, -s * dx + c * dy
            with np.errstate(divide="ignore", invalid="ignore"):
                t1x, t2x = (-hw - lox) / ldx, (hw - lox) / ldx
                t1y, t2y = (-hd - loy) / ldy, (hd - loy) / ldy
                t1z, t2z = (-hh - pz) / dz, (hh - pz) / dz
                tmin = np.fmax(np.fmax(np.fmin(t1x, t2x), np.fmin(t1y, t2y)), np.fmin(t1z, t2z))
                tmax = np.fmin(np.fmin(np.fmax(t1x, t2x), np.fmax(t1y, t2y)), np.fmax(t1z, t2z))
            hit = tmax >= np.maximum(tmin, _EPS_T)
            t = np.where(tmin > _EPS_T, tmin, tmax)
            closer = hit & (t < depth)
            depth = np.where(closer, t, depth)
            labels = np.where(closer, code, labels)
        return labels.reshape(shape), depth.reshape(shape)

    # ------------------------------------------------------------------
    def measure(self, labels: np.ndarray, depth: np.ndarray, border: np.ndarray) -> list[dict]:
        """Model shares (the ``score_terms`` input) of each row of ``labels``/``depth`` (C x P)."""
        labels = np.asarray(labels).reshape(-1, labels.shape[-1])
        depth = np.asarray(depth).reshape(-1, depth.shape[-1])
        C, P = labels.shape
        L = self.n_labels
        offsets = (np.arange(C) * L)[:, None]
        counts = np.bincount((labels + offsets).ravel(), minlength=C * L).reshape(C, L)
        bl = labels[:, border]
        bcounts = np.bincount((bl + offsets).ravel(), minlength=C * L).reshape(C, L)
        shares = counts / float(P)
        elements = np.concatenate([self.piece_codes, self.opening_codes]).astype(int)
        max_single = shares[:, elements].max(axis=1) if len(elements) else np.zeros(C)
        near = (depth < SCORE["near_m"]).mean(axis=1)
        wall = labels == WALL
        d_wall = np.zeros(C)
        has_wall = wall.any(axis=1)
        if has_wall.any():
            with np.errstate(invalid="ignore"):
                d_wall[has_wall] = np.nanmedian(np.where(wall[has_wall], depth[has_wall], np.nan), axis=1)
        for i in np.nonzero(~has_wall)[0]:
            finite = depth[i][np.isfinite(depth[i])]
            d_wall[i] = float(np.median(finite)) if finite.size else 0.0
        out = []
        for i in range(C):
            pc = self.piece_codes
            furn = furniture_share(shares[i, pc], bcounts[i, pc] > 0, self.piece_weights) if len(pc) else 0.0
            out.append({
                "furn": furn,
                "open": float(shares[i, self.opening_codes].sum()) if len(self.opening_codes) else 0.0,
                "window": float(shares[i, self.window_codes].sum()) if len(self.window_codes) else 0.0,
                "floor": float(shares[i, FLOOR]), "ceiling": float(shares[i, CEILING]),
                "wall": float(shares[i, WALL]), "near": float(near[i]), "max_single": float(max_single[i]),
                "d_wall": float(d_wall[i]),
                "elements": {self.elements[c - FIRST_ELEMENT]["id"]: float(shares[i, c])
                           for c in range(FIRST_ELEMENT, L) if counts[i, c]},
                "cut": sorted(self.elements[c - FIRST_ELEMENT]["id"] for c in range(FIRST_ELEMENT, L) if bcounts[i, c]),
            })
        return out


# --------------------------------------------------------------------------
# Candidates and the pick
# --------------------------------------------------------------------------

def convex_corner_points(polygon: Sequence[Sequence[float]], insets=CORNER_INSETS) -> list[tuple[float, float]]:
    """Two points per convex corner, ``insets`` metres in along the bisector (not yet checked for room)."""
    n = len(polygon)
    orient = 1.0 if G.polygon_signed_area(polygon) >= 0 else -1.0
    out = []
    for i in range(n):
        pv, p, nx = polygon[i - 1], polygon[i], polygon[(i + 1) % n]
        cross = (p[0] - pv[0]) * (nx[1] - p[1]) - (p[1] - pv[1]) * (nx[0] - p[0])
        if cross * orient <= 1e-12:
            continue                          # reflex or straight
        l1, l2 = G.distance(pv, p), G.distance(nx, p)
        if l1 < 1e-9 or l2 < 1e-9:
            continue
        bx = (pv[0] - p[0]) / l1 + (nx[0] - p[0]) / l2
        by = (pv[1] - p[1]) / l1 + (nx[1] - p[1]) / l2
        lb = math.hypot(bx, by)
        if lb < 1e-9:
            continue
        for k in insets:
            out.append((p[0] + bx / lb * k, p[1] + by / lb * k))
    return out


def candidate_positions(room: dict, building: dict) -> tuple[list[tuple[float, float]], Optional[str]]:
    """Camera points of a room and a warning: the free convex-corner points and the free 0.5 m grid
    points (sorted by x, y); without any, the M5 fallback point with its warning."""
    polygon = room_polygon(room)
    pieces = [f for f in building.get("furniture") or [] if f.get("room_id") == room["id"] and f.get("kind") != "decor"]
    obstacles = [obstacle_rect(f) for f in pieces]
    corners = [p for p in convex_corner_points(polygon)
               if geom2d.point_is_free(p, polygon, obstacles, WALL_CLEARANCE, OBSTACLE_CLEARANCE)]
    grid = geom2d.free_points(polygon, obstacles, step=GRID_STEP, wall_clearance=WALL_CLEARANCE,
                              obstacle_clearance=OBSTACLE_CLEARANCE)
    points = sorted({(round(p[0], 9), round(p[1], 9)) for p in corners + grid})
    if points:
        return points, None
    tall = [obstacle_rect(f) for f in pieces if piece_bbox(f)[2] >= CAMERA_HEIGHT]
    p, warning = fallback_position(polygon, obstacles, tall)
    return [(round(float(p[0]), 9), round(float(p[1]), 9))], warning


def fallback_position(polygon, obstacles, tall) -> tuple[tuple[float, float], str]:
    """The M5 fallback (``cameras._Search.fallback``, unchanged) anchored at the room's inner point.

    The anchor is ``lighting.polylabel`` (the point farthest from the walls), not the centroid: the
    centroid of an L-shaped room can lie outside it, in the notch, and a camera there renders the wall
    mass or the neighbouring room under this room's name (review C1). The inner point is always inside
    the polygon, so a cramped view stays in the room and the model flags it ``blocked unavoidable``.
    The warning says what happened: the anchor is the room's inner point, and the last resort is said
    to be inside a proxy only when it is."""
    from wenart.blender import lighting

    x, y, distance = lighting.polylabel(polygon)
    anchor = (x, y)
    search = cameras._Search(polygon, obstacles, tall, [], anchor)
    p, warning = search.fallback(anchor, "no free camera point in the room")
    if warning.endswith("INSIDE a proxy"):
        inside = any(geom2d.distance_to_rect(p, ob["center"], ob["size"], ob["rotation_deg"]) <= 1e-9 for ob in tall)
        where = "INSIDE a proxy" if inside else f"{distance:.2f} m from the nearest wall"
        warning = (f"no free camera point in the room; no point clear of the walls and the tall proxies, "
                   f"camera at the room's inner point {where}")
    else:
        warning = warning.replace("centroid", "room's inner point")
    return p, warning


def yaw_difference(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def sort_key(c: dict) -> tuple:
    """Ties: score (higher first), then x, y, yaw."""
    return (-round(c["total"], SCORE_DECIMALS), c["x"], c["y"], c["yaw"])


def select_views(candidates: Sequence[dict], n: int) -> tuple[list[dict], Optional[str]]:
    """The §4.1 greedy pick: ``(picks, warning)`` from candidate dicts with ``total``, ``x``, ``y``,
    ``yaw`` and ``blocked``; at most ``n`` and at least one pick (none for no candidate)."""
    ordered = sorted(candidates, key=sort_key)
    free = [c for c in ordered if not c["blocked"]]
    if not free:
        return (ordered[:1], BLOCKED_WARNING) if ordered else ([], None)
    best = round(free[0]["total"], SCORE_DECIMALS)
    picks = [free[0]]
    for c in free[1:]:
        if len(picks) >= n:
            break
        if round(c["total"], SCORE_DECIMALS) < DROP_BELOW_BEST * best:
            break                               # sorted: every later one is lower still
        if all(yaw_difference(c["yaw"], p["yaw"]) >= MIN_YAW_DIFF_DEG - 1e-9
               or math.hypot(c["x"] - p["x"], c["y"] - p["y"]) >= MIN_DISTANCE_M - 1e-9 for p in picks):
            picks.append(c)
    return picks, None


def score_candidates(model: RoomModel, positions, height: float = CAMERA_HEIGHT, yaws=None,
                     shift_x: float = SHIFT_X, shift_y: float = SHIFT_Y, grid=None) -> list[dict]:
    """Every (position, yaw) candidate of a room with its model shares and score terms."""
    grid = grid or SCORE["grid"]
    yaws = list(range(0, 360, YAW_STEP_DEG)) if yaws is None else list(yaws)
    a, b = ray_grid(grid, shift_x=shift_x, shift_y=shift_y)
    dirs = yaw_directions(yaws, a, b)
    border = border_mask(grid)
    z = model.floor_z + float(height)
    out = []
    for x, y in positions:
        labels, depth = model.cast((x, y, z), dirs)
        for yaw, m in zip(yaws, model.measure(labels, depth, border)):
            terms = score_terms(m)
            out.append({"x": float(x), "y": float(y), "yaw": float(yaw), "total": terms["total"], "terms": terms,
                        "blocked": terms["blocked"], "shares": m})
    return out


def score_camera(building: dict, camera: dict, grid=None) -> dict:
    """Model shares and score terms of any camera plan (M5 or searched; pitch and shift as recorded)."""
    room = next(r for r in building["rooms"] if r["id"] == camera["room_id"])
    model = RoomModel(room, building)
    grid = grid or SCORE["grid"]
    a, b = ray_grid(grid, camera.get("lens_mm") or LENS_MM, camera.get("sensor_mm") or SENSOR_MM,
                    camera.get("resolution") or RESOLUTION, float(camera.get("shift_x") or 0.0),
                    float(camera.get("shift_y") or 0.0))
    labels, depth = model.cast(camera["position"], camera_directions(camera["position"], camera["target"], a, b))
    m = model.measure(labels[None, :], depth[None, :], border_mask(grid))[0]
    return {"shares": m, "terms": score_terms(m)}


# --------------------------------------------------------------------------
# Plans
# --------------------------------------------------------------------------

def _round(v: float, nd: int = 4) -> float:
    r = round(float(v), nd)
    return 0.0 if r == 0 else r


def _frustum_lists(model: RoomModel, position, target) -> tuple[list[str], list[str]]:
    """The room's openings and pieces whose centre is inside the shifted frustum (as the M5 lists)."""
    tangents = geom2d.frustum_tangents(LENS_MM, SENSOR_MM, RESOLUTION)
    fz = model.floor_z
    opens = [o["id"] for o in model.openings
             if geom2d.point_in_frustum((o["center"][0], o["center"][1], fz + 1.0), position, target, tangents,
                                        shift_x=SHIFT_X, shift_y=SHIFT_Y)]
    pieces = [f["id"] for f in model.pieces
              if geom2d.point_in_frustum((f["footprint"]["center"][0], f["footprint"]["center"][1],
                                          fz + piece_bbox(f)[2] / 2.0), position, target, tangents,
                                         shift_x=SHIFT_X, shift_y=SHIFT_Y)]
    return opens, pieces


def _plan(model: RoomModel, index: int, pick: dict, warning: Optional[str]) -> dict:
    room = model.room
    z = model.floor_z + CAMERA_HEIGHT
    yaw = math.radians(pick["yaw"])
    position = [_round(pick["x"], 6), _round(pick["y"], 6), _round(z, 6)]
    target = [_round(pick["x"] + TARGET_DISTANCE * math.cos(yaw), 6),
              _round(pick["y"] + TARGET_DISTANCE * math.sin(yaw), 6), _round(z, 6)]
    t, m = pick["terms"], pick["shares"]
    score = {"total": _round(t["total"]), "furniture": _round(t["furniture"]), "openings": _round(t["openings"]),
             "floor": _round(t["floor"]), "depth": _round(t["depth"]), "penalties": _round(t["penalties"]),
             "blocked": bool(t["blocked"]), "yaw_deg": float(pick["yaw"]),
             "shares": {k: _round(m[k]) for k in ("furn", "open", "window", "floor", "ceiling", "wall", "near",
                                                  "max_single", "d_wall")}}
    placement = (f"search: score {score['total']:.3f} = furniture {score['furniture']:.3f} + openings "
                 f"{score['openings']:.3f} + floor {score['floor']:.3f} + depth {score['depth']:.3f} - penalties "
                 f"{score['penalties']:.3f}; yaw {pick['yaw']:.0f} deg")
    opens, pieces = _frustum_lists(model, position, target)
    return {
        "name": f"cam_{room['id']}_{index}",
        "room_id": room["id"], "level_id": room["level_id"], "index": index,
        "position": position, "target": target,
        "lens_mm": LENS_MM, "sensor_mm": SENSOR_MM, "resolution": list(RESOLUTION),
        "shift_x": SHIFT_X, "shift_y": SHIFT_Y, "policy": POLICY, "score": score,
        "placement": placement, "anchor": None, "warning": warning,
        "visible_openings": opens, "visible_furniture": pieces,
    }


def plan_room(room: dict, building: dict, level: Optional[dict] = None) -> tuple[list[dict], int]:
    """``(plans, candidates scored)`` of one room."""
    model = RoomModel(room, building, level)
    if len(model.polygon) < 3:
        raise ValueError(f"room {room['id']}: polygon with fewer than 3 vertices, no camera can be placed")
    positions, fallback = candidate_positions(room, building)
    cands = score_candidates(model, positions)
    picks, blocked = select_views(cands, room_view_count(room))
    warning = "; ".join(w for w in (fallback, blocked) if w) or None
    return [_plan(model, i, p, warning) for i, p in enumerate(picks, start=1)], len(cands)


def plan_level(building: dict, level_id: str) -> list[dict]:
    """Searched camera plans of every room of ``level_id`` (``cameras.plan_cameras(policy="search")``).

    Every plan carries ``search_seconds``: the wall time of this level's search."""
    level = next(lv for lv in building["levels"] if lv["id"] == level_id)
    t0 = time.perf_counter()
    plans: list[dict] = []
    for room in building["rooms"]:
        if room["level_id"] != level_id:
            continue
        plans.extend(plan_room(room, building, level)[0])
    seconds = round(time.perf_counter() - t0, 3)
    for plan in plans:
        plan["search_seconds"] = seconds
    return plans


def level_search_seconds(plans: Sequence[dict]) -> dict[str, float]:
    """``{level_id: search seconds}`` of searched plans (what the scene manifest records)."""
    out: dict[str, float] = {}
    for p in plans:
        if p.get("policy") == POLICY and p.get("search_seconds") is not None:
            out[p["level_id"]] = float(p["search_seconds"])
    return out


def model_shares(building: dict, camera: dict, grid=(192, 108)) -> dict[str, float]:
    """``{element id: ray share}`` the model sees from ``camera`` on a finer grid (GPU test helper)."""
    return score_camera(building, camera, grid=grid)["shares"]["elements"]


# --------------------------------------------------------------------------
# CLI (inspection)
# --------------------------------------------------------------------------

def report_md(building: dict, plans: Sequence[dict]) -> str:
    rooms = {r["id"]: r for r in building["rooms"]}
    lines = [f"# Camera search: {building.get('project', {}).get('id', '?')}", "",
             f"Policy `search`: height {CAMERA_HEIGHT} m, pitch 0, shift_y {SHIFT_Y}, lens {LENS_MM:.0f} mm; "
             f"{len(plans)} views in {len({p['room_id'] for p in plans})} rooms; search "
             + ", ".join(f"{k} {v:.1f} s" for k, v in level_search_seconds(plans).items()) + ".", "",
             "| Camera | Room | Area m2 | Score | Furniture | Openings | Floor | Depth | Penalties | Floor share | "
             "Near | Warning |", "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for p in plans:
        s = p["score"]
        area = G.polygon_area(room_polygon(rooms[p["room_id"]]))
        lines.append(f"| {p['name']} | {p['room_id']} | {area:.2f} | {s['total']:.3f} | {s['furniture']:.3f} | "
                     f"{s['openings']:.3f} | {s['floor']:.3f} | {s['depth']:.3f} | {s['penalties']:.3f} | "
                     f"{s['shares']['floor']:.3f} | {s['shares']['near']:.3f} | {p['warning'] or ''} |")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.blender.camsearch", description=__doc__.split("\n\n")[0])
    ap.add_argument("building", help="building JSON (status ok)")
    ap.add_argument("--level", default=None, help="one level id (default: every level)")
    ap.add_argument("--out", required=True, help="JSON with the plans")
    ap.add_argument("--report", default=None, help="optional markdown table of the views")
    args = ap.parse_args(argv)
    building = json.loads(Path(args.building).read_text(encoding="utf-8"))
    levels = [lv["id"] for lv in building["levels"] if args.level is None or lv["id"] == args.level]
    if not levels:
        print(f"no level {args.level!r} in {args.building}", file=sys.stderr)
        return 2
    plans: list[dict] = []
    for level_id in levels:
        plans.extend(plan_level(building, level_id))
    out = {"schema_version": "0.1", "kind": "camera_search", "building": args.building, "policy": POLICY,
           "search_seconds": level_search_seconds(plans), "cameras": plans}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if args.report:
        Path(args.report).write_text(report_md(building, plans), encoding="utf-8")
    blocked = [p["name"] for p in plans if p["warning"] and BLOCKED_WARNING in p["warning"]]
    print(f"{len(plans)} views, search {sum(out['search_seconds'].values()):.1f} s, blocked unavoidable: "
          f"{blocked or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
