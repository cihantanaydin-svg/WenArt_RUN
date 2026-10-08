"""Pure-Python geometry for the Blender scene: boxes, wedges, polygon faces,
box-projected UVs, free-area search and camera frustum tests.

No ``bpy``, no shapely, no numpy: this module runs inside Blender (whose
Python has no shapely) and in the CPU tests outside Blender. Vertices are
``(x, y, z)`` tuples in world metres; faces are index lists wound
counter-clockwise seen from outside, which is what Blender expects for
outward normals.

Milestone 7 (docs/milestone7.md §6.4): ``extrude_profile`` and
``convex_solid`` (the steps of a stair: a convex (s, z) profile pushed across
the flight width), ``rect_union_outline`` (the stair void = the last flight
plus the landing, an L-shaped outline) and ``polygon_faces`` (a ceiling with
the void cut out: trapezoids of "inside the outer polygon and outside every
hole", since a Blender n-gon has no holes).
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
# Milestone 7: convex solids, rectangle unions, polygons with holes
# --------------------------------------------------------------------------

def convex_solid(verts: Sequence[Vec3], faces: Sequence[Sequence[int]]) -> tuple[list[Vec3], list[list[int]]]:
    """The faces of a convex solid wound outwards: a face whose normal points
    towards the centroid of the vertices is reversed (valid only for convex
    solids, where every face sees the centroid on its inner side)."""
    verts = [tuple(float(c) for c in v) for v in verts]
    n = float(len(verts))
    centre = (sum(v[0] for v in verts) / n, sum(v[1] for v in verts) / n, sum(v[2] for v in verts) / n)
    out = []
    for f in faces:
        nrm = face_normal(verts, f)
        c = face_center(verts, f)
        if _dot(nrm, (c[0] - centre[0], c[1] - centre[1], c[2] - centre[2])) < 0:
            f = list(reversed(f))
        out.append(list(f))
    return verts, out


def extrude_profile(profile: Sequence[Sequence[float]], origin: Sequence[float], along: Sequence[float],
                    width: float) -> tuple[list[Vec3], list[list[int]]]:
    """A convex profile ``[(s, z), ...]`` (in the vertical plane through
    ``origin`` along the horizontal unit vector ``along``) pushed sideways
    by ``width`` (centred on the plane): two end caps and one quad per
    profile edge, wound outwards. ``origin`` = ``(x, y)``; z is absolute."""
    ux, uy = float(along[0]), float(along[1])
    px, py = -uy, ux                                   # left of ``along``
    h = float(width) / 2.0
    ox, oy = float(origin[0]), float(origin[1])
    k = len(profile)
    verts = []
    for q in (-h, h):
        for s, z in profile:
            verts.append((ox + ux * s + px * q, oy + uy * s + py * q, float(z)))
    faces = [list(range(k)), list(range(k, 2 * k))]
    for j in range(k):
        a, b = j, (j + 1) % k
        faces.append([a, b, k + b, k + a])
    return convex_solid(verts, faces)


def prism(polygon: Sequence[Sequence[float]], z0: float, z1: float) -> tuple[list[Vec3], list[list[int]]]:
    """Vertical prism of a convex 2D polygon from ``z0`` to ``z1``, wound outwards."""
    pts = [tuple(p[:2]) for p in polygon]
    if len(pts) > 1 and G.distance(pts[0], pts[-1]) < 1e-9:
        pts = pts[:-1]
    k = len(pts)
    verts = [(float(x), float(y), float(z0)) for x, y in pts] + [(float(x), float(y), float(z1)) for x, y in pts]
    faces = [list(range(k)), list(range(k, 2 * k))]
    for j in range(k):
        a, b = j, (j + 1) % k
        faces.append([a, b, k + b, k + a])
    return convex_solid(verts, faces)


def rect_union_outline(rects: Sequence[Sequence[float]], tol: float = 1e-7) -> list[list[tuple[float, float]]]:
    """Outline loops of the union of axis-aligned rectangles ``(x0, y0, x1,
    y1)``: counter-clockwise outer loops, clockwise holes, collinear points
    removed. Grid method: the cells between the distinct edge coordinates
    are covered or not; the boundary is every cell side with an uncovered
    neighbour, chained into loops (covered cell on the left)."""
    boxes = [(min(r[0], r[2]), min(r[1], r[3]), max(r[0], r[2]), max(r[1], r[3])) for r in rects]
    boxes = [b for b in boxes if b[2] - b[0] > tol and b[3] - b[1] > tol]
    if not boxes:
        return []

    def uniq(values):
        out = []
        for v in sorted(values):
            if not out or v - out[-1] > tol:
                out.append(v)
        return out

    xs = uniq([b[0] for b in boxes] + [b[2] for b in boxes])
    ys = uniq([b[1] for b in boxes] + [b[3] for b in boxes])
    nx, ny = len(xs) - 1, len(ys) - 1

    def covered(i: int, j: int) -> bool:
        if not (0 <= i < nx and 0 <= j < ny):
            return False
        cx, cy = (xs[i] + xs[i + 1]) / 2.0, (ys[j] + ys[j + 1]) / 2.0
        return any(b[0] < cx < b[2] and b[1] < cy < b[3] for b in boxes)

    cells = {(i, j) for i in range(nx) for j in range(ny) if covered(i, j)}
    edges: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for i, j in sorted(cells):
        if (i, j - 1) not in cells:
            edges.setdefault((i, j), []).append((i + 1, j))          # bottom, left to right
        if (i + 1, j) not in cells:
            edges.setdefault((i + 1, j), []).append((i + 1, j + 1))  # right, upwards
        if (i, j + 1) not in cells:
            edges.setdefault((i + 1, j + 1), []).append((i, j + 1))  # top, right to left
        if (i - 1, j) not in cells:
            edges.setdefault((i, j + 1), []).append((i, j))          # left, downwards
    loops = []
    while edges:
        start = min(edges)
        loop = [start]
        cur = start
        while True:
            nxt = edges[cur].pop(0)
            if not edges[cur]:
                del edges[cur]
            if nxt == start:
                break
            loop.append(nxt)
            cur = nxt
            if cur not in edges:      # broken chain (cannot happen for a cell boundary); stop safely
                break
        pts = [(xs[i], ys[j]) for i, j in loop]
        loops.append(_drop_collinear(pts))
    return [lp for lp in loops if len(lp) >= 3]


def _drop_collinear(pts: list[tuple[float, float]], tol: float = 1e-9) -> list[tuple[float, float]]:
    out = list(pts)
    changed = True
    while changed and len(out) > 3:
        changed = False
        for k in range(len(out)):
            a, b, c = out[k - 1], out[k], out[(k + 1) % len(out)]
            if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) <= tol:
                del out[k]
                changed = True
                break
    return out


def polygon_faces(outer: Sequence[Sequence[float]], holes: Sequence[Sequence[Sequence[float]]], z: float,
                  facing_up: bool = True, tol: float = 1e-9) -> tuple[list[Vec3], list[list[int]]]:
    """Faces covering the region inside ``outer`` and outside every polygon
    of ``holes`` (holes may reach beyond ``outer``), at height ``z``.

    Trapezoidal decomposition in horizontal bands: the band edges are every
    vertex y and every y where an edge of one polygon crosses an edge of
    another, so no two edges cross inside a band; in each band the edges
    are sorted along x and the even-odd parity of the outer polygon and of
    the holes says which intervals are inside the region; each interval is a
    trapezoid (or a triangle) between its two bounding edges. Faces are
    counter-clockwise seen from above (``facing_up``) or reversed; vertices
    on the band lines are shared."""
    def clean(poly):
        pts = [(float(p[0]), float(p[1])) for p in poly]
        if len(pts) > 1 and G.distance(pts[0], pts[-1]) < tol:
            pts = pts[:-1]
        return pts

    polys = [clean(outer)] + [clean(h) for h in holes if len(h) >= 3]
    edges = []                                    # (x0, y0, x1, y1, polygon index); non-horizontal only
    for k, poly in enumerate(polys):
        n = len(poly)
        for i in range(n):
            (ax, ay), (bx, by) = poly[i], poly[(i + 1) % n]
            if abs(ay - by) > tol:
                edges.append((ax, ay, bx, by, k))
    ys = {p[1] for poly in polys for p in poly}
    for i, e in enumerate(edges):
        for f in edges[i + 1:]:
            if e[4] == f[4]:
                continue
            y = _edge_crossing_y(e, f, tol)
            if y is not None:
                ys.add(y)
    bands = []
    for y in sorted(ys):
        if not bands or y - bands[-1] > tol:
            bands.append(y)
    verts: list[Vec3] = []
    index: dict[tuple[float, float], int] = {}

    def vid(x: float, y: float) -> int:
        key = (round(x, 9), round(y, 9))
        if key not in index:
            index[key] = len(verts)
            verts.append((x, y, float(z)))
        return index[key]

    faces: list[list[int]] = []
    for y0, y1 in zip(bands, bands[1:]):
        ym = (y0 + y1) / 2.0
        hits = []
        for ax, ay, bx, by, k in edges:
            if min(ay, by) < ym < max(ay, by):
                def x_at(y, ax=ax, ay=ay, bx=bx, by=by):
                    return ax + (bx - ax) * (y - ay) / (by - ay)
                hits.append((x_at(ym), x_at(y0), x_at(y1), k))
        hits.sort(key=lambda h: h[0])
        parity = [False] * len(polys)
        left = None
        for xm, x0, x1, k in hits:
            was = parity[0] and not any(parity[1:])
            parity[k] = not parity[k]
            now = parity[0] and not any(parity[1:])
            if now and not was:
                left = (x0, x1)
            elif was and not now and left is not None:
                lx0, lx1 = left
                bottom = x0 - lx0 > tol
                top = x1 - lx1 > tol
                if bottom and top:
                    face = [vid(lx0, y0), vid(x0, y0), vid(x1, y1), vid(lx1, y1)]
                elif bottom:
                    face = [vid(lx0, y0), vid(x0, y0), vid(lx1, y1)]
                elif top:
                    face = [vid(lx0, y0), vid(x1, y1), vid(lx1, y1)]
                else:
                    face = None
                if face is not None:
                    faces.append(face if facing_up else list(reversed(face)))
                left = None
    return verts, faces


def _edge_crossing_y(e, f, tol: float) -> float | None:
    """y of the proper crossing of two segments (None when parallel or not crossing)."""
    ax, ay, bx, by = e[:4]
    cx, cy, dx, dy = f[:4]
    rx, ry = bx - ax, by - ay
    sx, sy = dx - cx, dy - cy
    den = rx * sy - ry * sx
    if abs(den) < 1e-15:
        return None
    t = ((cx - ax) * sy - (cy - ay) * sx) / den
    u = ((cx - ax) * ry - (cy - ay) * rx) / den
    if -tol <= t <= 1 + tol and -tol <= u <= 1 + tol:
        return ay + t * ry
    return None


def faces_area(verts: Sequence[Vec3], faces: Sequence[Sequence[int]]) -> float:
    """Total area of planar faces projected on the XY plane (absolute)."""
    total = 0.0
    for f in faces:
        total += abs(G.polygon_signed_area([verts[i][:2] for i in f]))
    return total


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
# Camera frustum (the camera's lens on a 36 mm sensor, landscape)
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


# --------------------------------------------------------------------------
# Milestone 10 (docs/milestone10.md §3.2): outlines, half-plane clipping, convex pieces
# --------------------------------------------------------------------------

def clean_polygon(polygon: Sequence[Sequence[float]], tol: float = 1e-9) -> list[tuple[float, float]]:
    """``(x, y)`` points without the closing duplicate and without repeated points."""
    out: list[tuple[float, float]] = []
    for p in polygon:
        q = (float(p[0]), float(p[1]))
        if not out or G.distance(out[-1], q) > tol:
            out.append(q)
    if len(out) > 1 and G.distance(out[0], out[-1]) <= tol:
        out.pop()
    return out


def ccw(polygon: Sequence[Sequence[float]]) -> list[tuple[float, float]]:
    """The polygon counter-clockwise (positive signed area)."""
    pts = clean_polygon(polygon)
    return pts if G.polygon_signed_area(pts) >= 0 else pts[::-1]


def convex_hull(points: Iterable[Sequence[float]]) -> list[tuple[float, float]]:
    """Counter-clockwise convex hull (Andrew's monotone chain), collinear points dropped."""
    pts = sorted({(float(p[0]), float(p[1])) for p in points})
    if len(pts) <= 2:
        return pts

    def half(seq):
        out: list[tuple[float, float]] = []
        for p in seq:
            while len(out) >= 2 and ((out[-1][0] - out[-2][0]) * (p[1] - out[-2][1])
                                     - (out[-1][1] - out[-2][1]) * (p[0] - out[-2][0])) <= 1e-12:
                out.pop()
            out.append(p)
        return out

    lower, upper = half(pts), half(reversed(pts))
    return lower[:-1] + upper[:-1]


def clip_half_plane(polygon: Sequence[Sequence[float]], a: float, b: float, c: float,
                    tol: float = 1e-12) -> list[tuple[float, float]]:
    """The part of a polygon where ``a x + b y + c <= 0`` (Sutherland-Hodgman against one half-plane;
    exact for convex polygons, area-correct for concave ones)."""
    pts = [(float(p[0]), float(p[1])) for p in polygon]
    if not pts:
        return []
    out: list[tuple[float, float]] = []
    n = len(pts)
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        dp, dq = a * p[0] + b * p[1] + c, a * q[0] + b * q[1] + c
        if dp <= tol:
            out.append(p)
        if (dp < -tol and dq > tol) or (dp > tol and dq < -tol):
            t = dp / (dp - dq)
            out.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return clean_polygon(out, 1e-9) if len(out) >= 3 else []


def convex_pieces(outer: Sequence[Sequence[float]], holes: Sequence[Sequence[Sequence[float]]] = ()
                  ) -> list[list[tuple[float, float]]]:
    """The region inside ``outer`` and outside every hole as convex pieces (the trapezoids of
    ``polygon_faces``), each counter-clockwise."""
    verts, faces = polygon_faces(outer, [h for h in holes if len(h) >= 3], 0.0, facing_up=True)
    return [[(verts[i][0], verts[i][1]) for i in f] for f in faces]


def wall_outline(walls: Sequence[dict], tol_deg: float = 0.5) -> tuple[list[tuple[float, float]], str]:
    """``(outline, method)``: the outer outline of the union of the wall rectangles (centre line,
    thickness), counter-clockwise: the outer face of the outer walls. Axis-parallel walls (within
    ``tol_deg``) give the exact union (``rect_union_outline``, method ``wall_union``); otherwise the convex
    hull of every wall corner (method ``convex_hull``, an approximation the callers record as assumed)."""
    rects, corners, axis = [], [], True
    for w in walls:
        length = G.distance(w["start"], w["end"])
        if length < 1e-9:
            continue
        # Square end caps (half the thickness past each end): two walls meeting at their centre-line
        # corner leave the outer corner square open otherwise.
        half = float(w["thickness"]) / 2.0
        s = G.point_at_distance(w["start"], w["end"], -half)
        e = G.point_at_distance(w["start"], w["end"], length + half)
        quad = G.centerline_to_rectangle(s, e, float(w["thickness"]))
        corners.extend(quad)
        ang = G.segment_angle_deg(w["start"], w["end"]) % 90.0
        if min(ang, 90.0 - ang) > tol_deg:
            axis = False
        xs, ys = [p[0] for p in quad], [p[1] for p in quad]
        rects.append((min(xs), min(ys), max(xs), max(ys)))
    if not rects:
        return [], "none"
    if axis:
        loops = rect_union_outline(rects)
        outer = [lp for lp in loops if G.polygon_signed_area(lp) > 0]
        if outer:
            return max(outer, key=G.polygon_area), "wall_union"
    return convex_hull(corners), "convex_hull"


def oriented_rectangle(polygon: Sequence[Sequence[float]]) -> dict:
    """The smallest rectangle around a polygon (rotating the convex hull's edge directions):
    ``{"center", "u", "v", "half": (A, B), "fill"}`` with ``u`` along the longer side (A >= B), ``v`` = ``u``
    turned 90 degrees counter-clockwise, and ``fill`` = polygon area / rectangle area (1 for a rectangle)."""
    hull = convex_hull(polygon)
    best = None
    n = len(hull)
    for i in range(n):
        p, q = hull[i], hull[(i + 1) % n]
        length = G.distance(p, q)
        if length < 1e-9:
            continue
        u = ((q[0] - p[0]) / length, (q[1] - p[1]) / length)
        v = (-u[1], u[0])
        s = [x * u[0] + y * u[1] for x, y in hull]
        t = [x * v[0] + y * v[1] for x, y in hull]
        area = (max(s) - min(s)) * (max(t) - min(t))
        if best is None or area < best[0] - 1e-9:
            best = (area, u, v, (min(s), max(s)), (min(t), max(t)))
    if best is None:
        raise ValueError("oriented_rectangle needs a polygon with area")
    area, u, v, (s0, s1), (t0, t1) = best
    sc, tc = (s0 + s1) / 2.0, (t0 + t1) / 2.0
    centre = (u[0] * sc + v[0] * tc, u[1] * sc + v[1] * tc)
    a, b = (s1 - s0) / 2.0, (t1 - t0) / 2.0
    if a < b - 1e-9:
        u, a, b = v, b, a
    u = _axis_tidy(u)
    v = (-u[1], u[0])
    fill = G.polygon_area(clean_polygon(polygon)) / area if area > 0 else 0.0
    return {"center": centre, "u": u, "v": v, "half": (a, b), "fill": fill}


def _axis_tidy(u: tuple[float, float]) -> tuple[float, float]:
    """A direction within 1e-9 of an axis snapped onto it, pointing to +X (or +Y for a vertical one)."""
    x, y = u
    if abs(x) < 1e-9:
        x = 0.0
    if abs(y) < 1e-9:
        y = 0.0
    if x < 0 or (x == 0 and y < 0):
        x, y = -x, -y
    n = math.hypot(x, y)
    return (x / n, y / n)


def offset_polygon(polygon: Sequence[Sequence[float]], inset: float) -> list[tuple[float, float]]:
    """The polygon moved ``inset`` metres inwards (negative: outwards): every edge line moved square to
    itself, consecutive lines intersected (collinear neighbours keep the moved corner). For the small
    insets of the scene (1-2 cm) on building outlines; a corner where the moved lines are parallel keeps the
    moved point."""
    pts = ccw(polygon)
    n = len(pts)
    if n < 3:
        return pts
    lines = []
    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        nx, ny = G.unit_normal_left(p, q)                 # counter-clockwise: left is inside
        lines.append(((p[0] + nx * inset, p[1] + ny * inset), (q[0] + nx * inset, q[1] + ny * inset)))
    out = []
    for i in range(n):
        (a, b), (c, d) = lines[i - 1], lines[i]
        rx, ry, sx, sy = b[0] - a[0], b[1] - a[1], d[0] - c[0], d[1] - c[1]
        den = rx * sy - ry * sx
        if abs(den) < 1e-12:
            out.append(c)
            continue
        t = ((c[0] - a[0]) * sy - (c[1] - a[1]) * sx) / den
        out.append((a[0] + t * rx, a[1] + t * ry))
    return out


def rectangle_corners(rect: dict, grow: float = 0.0) -> list[tuple[float, float]]:
    """The counter-clockwise corners of an ``oriented_rectangle`` grown by ``grow`` on every side."""
    (cx, cy), (ux, uy), (vx, vy) = rect["center"], rect["u"], rect["v"]
    a, b = rect["half"][0] + grow, rect["half"][1] + grow
    return [(cx - ux * a - vx * b, cy - uy * a - vy * b), (cx + ux * a - vx * b, cy + uy * a - vy * b),
            (cx + ux * a + vx * b, cy + uy * a + vy * b), (cx - ux * a + vx * b, cy - uy * a + vy * b)]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a: Sequence[float], b: Sequence[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _normalise(v: Vec3) -> Vec3:
    length = math.sqrt(_dot(v, v))
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (v[0] / length, v[1] / length, v[2] / length)
