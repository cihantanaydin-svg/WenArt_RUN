"""Pure-Python geometry for the Blender scene: boxes, wedges, polygon faces,
box-projected UVs, free-area search and camera frustum tests.

No ``bpy``, no shapely, no numpy: this module runs inside Blender (whose
Python has no shapely) and in the CPU tests outside Blender. Vertices are
``(x, y, z)`` tuples in world metres; faces are index lists wound
counter-clockwise seen from outside, which is what Blender expects for
outward normals.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

from wenart import geometry as G

Vec3 = tuple[float, float, float]


# --------------------------------------------------------------------------
# Solid primitives
# --------------------------------------------------------------------------

def box(center: Sequence[float], size: Sequence[float], rotation_deg: float = 0.0
        ) -> tuple[list[Vec3], list[list[int]]]:
    """Axis box of ``size = (w, d, h)`` centred at ``center = (x, y, z)``,
    rotated by ``rotation_deg`` around +Z through its centre.

    Faces are wound so the normals point outwards (checked in the tests).
    """
    w, d, h = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
    local = [(-w, -d, -h), (w, -d, -h), (w, d, -h), (-w, d, -h),
             (-w, -d, h), (w, -d, h), (w, d, h), (-w, d, h)]
    verts = [_place(p, center, rotation_deg) for p in local]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return verts, faces


def wedge(center: Sequence[float], width: float, depth: float, height: float,
          rotation_deg: float = 0.0) -> tuple[list[Vec3], list[list[int]]]:
    """Triangular prism whose base edge (``width`` long) lies on the local
    y = 0 line and whose apex points to local -Y by ``depth``; ``height`` along
    Z. Used as the "front" marker on furniture proxies.
    """
    hw, hh = width / 2.0, height / 2.0
    local = [(-hw, 0.0, -hh), (hw, 0.0, -hh), (0.0, -depth, -hh),
             (-hw, 0.0, hh), (hw, 0.0, hh), (0.0, -depth, hh)]
    verts = [_place(p, center, rotation_deg) for p in local]
    faces = [[0, 1, 2], [3, 5, 4], [0, 3, 4, 1], [1, 4, 5, 2], [2, 5, 3, 0]]
    return verts, faces


def _place(p: Vec3, center: Sequence[float], rotation_deg: float) -> Vec3:
    x, y = G.rotate_point((p[0], p[1]), rotation_deg)
    return (x + center[0], y + center[1], p[2] + center[2])


def merge(parts: Iterable[tuple[list[Vec3], list[list[int]]]]) -> tuple[list[Vec3], list[list[int]]]:
    """Concatenate several (verts, faces) pieces into one mesh description."""
    verts: list[Vec3] = []
    faces: list[list[int]] = []
    for pv, pf in parts:
        offset = len(verts)
        verts.extend(pv)
        faces.extend([[i + offset for i in f] for f in pf])
    return verts, faces


def oriented_box(points: Iterable[Sequence[float]], rotation_deg: float = 0.0) -> dict:
    """The box of world points in a frame turned by ``rotation_deg`` about +Z.

    Returns ``{"center": [x, y, z], "size": [w, d, h], "rotation_deg": r}``:
    the points are turned by ``-r`` into the piece frame, boxed there
    (w along the piece X, d along the piece Y) and the box centre is turned
    back into the world. This is the ``box3d`` convention of the scene
    manifest (docs/milestone5.md §2.7): a box with these fields, drawn with
    ``box(center, size, rotation_deg)``, encloses the points."""
    pts = [(float(p[0]), float(p[1]), float(p[2])) for p in points]
    if not pts:
        raise ValueError("oriented_box needs at least one point")
    rot = float(rotation_deg)
    local = [(*G.rotate_point((x, y), -rot), z) for x, y, z in pts]
    xs = [p[0] for p in local]
    ys = [p[1] for p in local]
    zs = [p[2] for p in local]
    lx, ly = (min(xs) + max(xs)) / 2.0, (min(ys) + max(ys)) / 2.0
    cx, cy = G.rotate_point((lx, ly), rot)
    return {"center": [round(cx, 4), round(cy, 4), round((min(zs) + max(zs)) / 2.0, 4)],
            "size": [round(max(xs) - min(xs), 4), round(max(ys) - min(ys), 4), round(max(zs) - min(zs), 4)],
            "rotation_deg": rot}


def polygon_face(polygon: Sequence[Sequence[float]], z: float, facing_up: bool = True
                 ) -> tuple[list[Vec3], list[list[int]]]:
    """One n-gon face from a 2D polygon at height ``z``. Counter-clockwise
    vertex order gives an upward normal; reversed for ceilings."""
    pts = [tuple(p[:2]) for p in polygon]
    if len(pts) > 1 and G.distance(pts[0], pts[-1]) < 1e-9:
        pts = pts[:-1]
    if G.polygon_signed_area(pts) < 0:
        pts = pts[::-1]
    if not facing_up:
        pts = pts[::-1]
    verts = [(float(x), float(y), float(z)) for x, y in pts]
    return verts, [list(range(len(verts)))]


def face_normal(verts: Sequence[Vec3], face: Sequence[int]) -> Vec3:
    """Unit normal of a planar face (Newell's method, works for n-gons)."""
    nx = ny = nz = 0.0
    n = len(face)
    for i in range(n):
        x0, y0, z0 = verts[face[i]]
        x1, y1, z1 = verts[face[(i + 1) % n]]
        nx += (y0 - y1) * (z0 + z1)
        ny += (z0 - z1) * (x0 + x1)
        nz += (x0 - x1) * (y0 + y1)
    length = math.sqrt(nx * nx + ny * ny + nz * nz)
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (nx / length, ny / length, nz / length)


def face_center(verts: Sequence[Vec3], face: Sequence[int]) -> Vec3:
    xs = [verts[i] for i in face]
    n = float(len(xs))
    return (sum(p[0] for p in xs) / n, sum(p[1] for p in xs) / n, sum(p[2] for p in xs) / n)


# --------------------------------------------------------------------------
# Box projection UVs (metres)
# --------------------------------------------------------------------------

def box_uv(point: Vec3, normal: Vec3) -> tuple[float, float]:
    """UV in metres for a point on a face with the given normal: the two world
    axes that are not the dominant normal axis. A texture with a real-world
    size of ``size_m`` then tiles correctly after dividing by that size."""
    ax, ay, az = abs(normal[0]), abs(normal[1]), abs(normal[2])
    x, y, z = point
    if az >= ax and az >= ay:
        return (x, y)
    if ax >= ay:
        return (y, z)
    return (x, z)


# --------------------------------------------------------------------------
# 2D helpers for placement (rooms, proxies, free area)
# --------------------------------------------------------------------------

def distance_to_polygon_edges(p: Sequence[float], polygon: Sequence[Sequence[float]]) -> float:
    """Shortest distance from a point to any edge of a polygon."""
    n = len(polygon)
    return min(G.point_segment_distance(p, polygon[i], polygon[(i + 1) % n]) for i in range(n))


def distance_to_rect(p: Sequence[float], center: Sequence[float], size: Sequence[float],
                     rotation_deg: float) -> float:
    """Distance from a point to a rotated rectangle (0 when inside)."""
    lx, ly = G.rotate_point(p, -rotation_deg, center)
    dx = max(abs(lx - center[0]) - size[0] / 2.0, 0.0)
    dy = max(abs(ly - center[1]) - size[1] / 2.0, 0.0)
    return math.hypot(dx, dy)


def point_is_free(p: Sequence[float], polygon: Sequence[Sequence[float]], obstacles: Sequence[dict],
                  wall_clearance: float = 0.5, obstacle_clearance: float = 0.3) -> bool:
    """True when ``p`` lies inside the room polygon shrunk by ``wall_clearance``
    and outside every obstacle footprint grown by ``obstacle_clearance``.

    ``obstacles`` are dicts with ``center``, ``size`` and ``rotation_deg`` (the
    furniture footprint shape of the building JSON).
    """
    if not G.point_in_polygon(p, polygon):
        return False
    if distance_to_polygon_edges(p, polygon) < wall_clearance - 1e-9:
        return False
    for ob in obstacles:
        if distance_to_rect(p, ob["center"], ob["size"], ob["rotation_deg"]) < obstacle_clearance - 1e-9:
            return False
    return True


def free_points(polygon: Sequence[Sequence[float]], obstacles: Sequence[dict], step: float = 0.1,
                wall_clearance: float = 0.5, obstacle_clearance: float = 0.3) -> list[tuple[float, float]]:
    """Grid sample of the free area of a room (see ``point_is_free``)."""
    x0, y0, x1, y1 = G.bbox(polygon)
    out = []
    nx = int((x1 - x0) / step) + 1
    ny = int((y1 - y0) / step) + 1
    for i in range(nx):
        for j in range(ny):
            p = (x0 + i * step, y0 + j * step)
            if point_is_free(p, polygon, obstacles, wall_clearance, obstacle_clearance):
                out.append(p)
    return out


def inward_normal(a: Sequence[float], b: Sequence[float], polygon: Sequence[Sequence[float]]) -> tuple[float, float]:
    """Unit normal of the edge a-b that points into the polygon."""
    nx, ny = G.unit_normal_left(a, b)
    mid = G.segment_midpoint(a, b)
    probe = (mid[0] + nx * 0.05, mid[1] + ny * 0.05)
    if G.point_in_polygon(probe, polygon):
        return (nx, ny)
    return (-nx, -ny)


def longest_edge(polygon: Sequence[Sequence[float]]) -> tuple[tuple[float, float], tuple[float, float]]:
    """End points of the longest edge of a polygon."""
    n = len(polygon)
    best = None
    for i in range(n):
        a, b = polygon[i], polygon[(i + 1) % n]
        length = G.distance(a, b)
        if best is None or length > best[0]:
            best = (length, (tuple(a[:2]), tuple(b[:2])))
    return best[1]


def nearest_edge(p: Sequence[float], polygon: Sequence[Sequence[float]]
                 ) -> tuple[float, tuple[tuple[float, float], tuple[float, float]]]:
    """Distance and end points of the polygon edge closest to ``p``."""
    n = len(polygon)
    best = None
    for i in range(n):
        a, b = polygon[i], polygon[(i + 1) % n]
        d = G.point_segment_distance(p, a, b)
        if best is None or d < best[0]:
            best = (d, (tuple(a[:2]), tuple(b[:2])))
    return best


# --------------------------------------------------------------------------
# Camera frustum (24 mm on a 36 mm sensor, landscape)
# --------------------------------------------------------------------------

def frustum_tangents(lens_mm: float, sensor_mm: float, resolution: Sequence[int]) -> tuple[float, float]:
    """``(tan(h_fov/2), tan(v_fov/2))`` for a landscape camera with the sensor
    width mapped to the image width (Blender sensor_fit AUTO / HORIZONTAL).
    The lens shift does not change them; it moves the frustum (see
    ``point_in_frustum``)."""
    th = (sensor_mm / 2.0) / lens_mm
    tv = th * resolution[1] / resolution[0]
    return th, tv


def camera_basis(position: Sequence[float], target: Sequence[float]) -> tuple[Vec3, Vec3, Vec3]:
    """Forward, right and up unit vectors of a camera looking from
    ``position`` at ``target`` with world +Z up."""
    f = _normalise((target[0] - position[0], target[1] - position[1], target[2] - position[2]))
    r = _normalise(_cross(f, (0.0, 0.0, 1.0)))
    if r == (0.0, 0.0, 0.0):  # looking straight down: pick +X as right
        r = (1.0, 0.0, 0.0)
    u = _cross(r, f)
    return f, r, u


def point_in_frustum(point: Sequence[float], position: Sequence[float], target: Sequence[float],
                     tangents: tuple[float, float], near: float = 0.05, shift_x: float = 0.0,
                     shift_y: float = 0.0) -> bool:
    """True when the 3D point is in front of the camera and inside its field of view.

    ``shift_x``/``shift_y``: Blender's lens shift in units of the image
    width (docs/milestone6.md §1.3). With slopes ``a = (v.r)/(v.f)`` and
    ``b = (v.u)/(v.f)`` the frame is ``|a - 2 th shift_x| <= th`` and
    ``|b - 2 th shift_y| <= tv`` (``th, tv = tangents``; ``2 th`` = W / f):
    a negative ``shift_y`` moves the frame down, a positive ``shift_x`` to the
    right. Shift 0 is the plain frustum."""
    f, r, u = camera_basis(position, target)
    v = (point[0] - position[0], point[1] - position[1], point[2] - position[2])
    z = _dot(v, f)
    if z <= near:
        return False
    ca = 2.0 * tangents[0] * float(shift_x)
    cb = 2.0 * tangents[0] * float(shift_y)
    return abs(_dot(v, r) - ca * z) <= tangents[0] * z and abs(_dot(v, u) - cb * z) <= tangents[1] * z


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _normalise(v: Vec3) -> Vec3:
    length = math.sqrt(_dot(v, v))
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (v[0] / length, v[1] / length, v[2] / length)
