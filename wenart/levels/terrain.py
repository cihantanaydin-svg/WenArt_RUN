"""The terrain surface from ground points (docs/milestone12.md §3.3 "Terrain", §3.4; owner: track L).

What: ``fit_surface(points, ...) -> surface`` and ``surface_z(surface, x, y) -> z``:

- >= 3 points not on one line: a least-squares plane ``z = a x + b y + c``; when its largest residual is at most
  ``plane_residual`` (0.10 m) the surface is ``planar``, else a triangulated surface (``tin``, Delaunay) through the
  points;
- 1-2 points or none: ``flat`` (the mean of the points, or the given ``flat_z``); the per-side levels of the
  sections stay the build's ``terrain_model`` (``sides``), this module does not replace them;
- beyond the points (outside their convex hull, grown by ``margin``) the surface blends to flat (the mean of the
  points) over ``blend_m`` (20 m): "flat beyond the plot".

Why: real03's site note gives one finished grade, a site plan gives spot heights; the Blender ground mesh, the
entrances (ground in front of a door) and the checks must read one surface, the same way.

How: pure Python (math only): it runs in the pipeline, the checks and inside Blender (``wenart.blender.site``).
The surface is a plain dict, stored in the building JSON as ``site.ground.surface``: ``{"kind", "points": [[x, y,
z]], "plane": [a, b, c] | null, "triangles": [[i, j, k]], "hull": [[x, y]], "flat_z", "residual", "slope",
"blend_m", "margin"}``.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

PLANE_RESIDUAL_M = 0.10
BLEND_M = 20.0
MARGIN_M = 2.0


def _solve3(m: list[list[float]], v: list[float]) -> Optional[list[float]]:
    """Gauss elimination of a 3 x 3 system; None when it is singular."""
    a = [row[:] + [v[i]] for i, row in enumerate(m)]
    for c in range(3):
        p = max(range(c, 3), key=lambda r: abs(a[r][c]))
        if abs(a[p][c]) < 1e-12:
            return None
        a[c], a[p] = a[p], a[c]
        for r in range(3):
            if r != c:
                f = a[r][c] / a[c][c]
                for k in range(c, 4):
                    a[r][k] -= f * a[c][k]
    return [a[i][3] / a[i][i] for i in range(3)]


def fit_plane(points: Sequence[Sequence[float]]) -> Optional[tuple[float, float, float]]:
    """Least-squares ``z = a x + b y + c`` through ``points`` ([x, y, z]); None for fewer than 3 points or points on
    one line."""
    if len(points) < 3:
        return None
    cx = sum(p[0] for p in points) / len(points)
    cy = sum(p[1] for p in points) / len(points)
    sxx = sum((p[0] - cx) ** 2 for p in points)
    syy = sum((p[1] - cy) ** 2 for p in points)
    sxy = sum((p[0] - cx) * (p[1] - cy) for p in points)
    if sxx * syy - sxy * sxy <= 1e-9 * max(1.0, sxx * syy):
        return None                                   # collinear (or one point repeated)
    n = float(len(points))
    sx = sum(p[0] for p in points)
    sy = sum(p[1] for p in points)
    m = [[sum(p[0] * p[0] for p in points), sum(p[0] * p[1] for p in points), sx],
         [sum(p[0] * p[1] for p in points), sum(p[1] * p[1] for p in points), sy],
         [sx, sy, n]]
    v = [sum(p[0] * p[2] for p in points), sum(p[1] * p[2] for p in points), sum(p[2] for p in points)]
    sol = _solve3(m, v)
    return None if sol is None else (sol[0], sol[1], sol[2])


def convex_hull(points: Sequence[Sequence[float]]) -> list[tuple[float, float]]:
    """Counter-clockwise hull of the xy of ``points`` (monotone chain)."""
    pts = sorted({(round(float(p[0]), 9), round(float(p[1]), 9)) for p in points})
    if len(pts) <= 2:
        return pts

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
    return lower[:-1] + upper[:-1]


def delaunay(points: Sequence[Sequence[float]]) -> list[tuple[int, int, int]]:
    """Delaunay triangles (indices into ``points``) of the xy of ``points`` (Bowyer-Watson; deterministic: the
    points in their given order). Duplicate points (within 1 mm) take the first."""
    pts = [(float(p[0]), float(p[1])) for p in points]
    if len(pts) < 3:
        return []
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    span = max(max(xs) - min(xs), max(ys) - min(ys), 1.0) * 20.0
    mx, my = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0
    big = [(mx - span, my - span), (mx + span, my - span), (mx, my + span)]
    allp = pts + big
    n = len(pts)
    tris = [(n, n + 1, n + 2)]

    def circum(t):
        (ax, ay), (bx, by), (cx, cy) = allp[t[0]], allp[t[1]], allp[t[2]]
        d = 2.0 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
        if abs(d) < 1e-12:
            return (0.0, 0.0, float("inf"))
        ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
        uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
        return (ux, uy, (ax - ux) ** 2 + (ay - uy) ** 2)

    seen: list[tuple[float, float]] = []
    for i, p in enumerate(pts):
        if any(math.hypot(p[0] - q[0], p[1] - q[1]) < 1e-3 for q in seen):
            continue
        seen.append(p)
        bad = []
        for t in tris:
            ux, uy, r2 = circum(t)
            if (p[0] - ux) ** 2 + (p[1] - uy) ** 2 < r2 - 1e-12:
                bad.append(t)
        edges: dict[tuple[int, int], int] = {}
        for t in bad:
            for e in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                k = tuple(sorted(e))
                edges[k] = edges.get(k, 0) + 1
        tris = [t for t in tris if t not in bad]
        for (a, b), count in sorted(edges.items()):
            if count == 1:
                tris.append((a, b, i))
    out = []
    for t in tris:
        if max(t) >= n:
            continue
        (ax, ay), (bx, by), (cx, cy) = pts[t[0]], pts[t[1]], pts[t[2]]
        area = (bx - ax) * (cy - ay) - (cx - ax) * (by - ay)
        if abs(area) < 1e-9:
            continue
        out.append(t if area > 0 else (t[0], t[2], t[1]))
    return sorted(out)


def fit_surface(points: Sequence[Sequence[float]], flat_z: Optional[float] = None,
                plane_residual: float = PLANE_RESIDUAL_M, blend_m: float = BLEND_M, margin: float = MARGIN_M) -> dict:
    """The terrain surface through ground points ``[x, y, z]`` (module docstring)."""
    pts = [[float(p[0]), float(p[1]), float(p[2])] for p in points]
    mean = sum(p[2] for p in pts) / len(pts) if pts else (0.0 if flat_z is None else float(flat_z))
    base = {"points": [[round(v, 4) + 0.0 for v in p] for p in pts], "plane": None, "triangles": [], "hull": [],
            "flat_z": round(mean if flat_z is None or pts else float(flat_z), 4) + 0.0, "residual": 0.0,
            "slope": 0.0, "blend_m": float(blend_m), "margin": float(margin)}
    plane = fit_plane(pts)
    if plane is None:
        return dict(base, kind="flat")
    a, b, c = plane
    resid = max(abs(a * p[0] + b * p[1] + c - p[2]) for p in pts)
    hull = convex_hull(pts)
    out = dict(base, hull=[[round(x, 4) + 0.0, round(y, 4) + 0.0] for x, y in hull], residual=round(resid, 4) + 0.0,
               slope=round(math.hypot(a, b), 4) + 0.0)
    if resid <= plane_residual:
        return dict(out, kind="planar", plane=[round(a, 6) + 0.0, round(b, 6) + 0.0, round(c, 4) + 0.0])
    tris = delaunay(pts)
    if not tris:
        return dict(out, kind="planar", plane=[round(a, 6) + 0.0, round(b, 6) + 0.0, round(c, 4) + 0.0])
    steepest = 0.0
    for i, j, k in tris:
        pl = _tri_plane(pts[i], pts[j], pts[k])
        if pl is not None:
            steepest = max(steepest, math.hypot(pl[0], pl[1]))
    return dict(out, kind="tin", triangles=[list(t) for t in tris], slope=round(steepest, 4) + 0.0)


def _tri_plane(p, q, r) -> Optional[tuple[float, float, float]]:
    (x1, y1, z1), (x2, y2, z2), (x3, y3, z3) = p[:3], q[:3], r[:3]
    det = (x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)
    if abs(det) < 1e-12:
        return None
    a = ((z2 - z1) * (y3 - y1) - (z3 - z1) * (y2 - y1)) / det
    b = ((x2 - x1) * (z3 - z1) - (x3 - x1) * (z2 - z1)) / det
    return a, b, z1 - a * x1 - b * y1


def _in_tri(x: float, y: float, p, q, r, eps: float = 1e-9) -> bool:
    def s(a, b):
        return (b[0] - a[0]) * (y - a[1]) - (b[1] - a[1]) * (x - a[0])
    d1, d2, d3 = s(p, q), s(q, r), s(r, p)
    return (d1 >= -eps and d2 >= -eps and d3 >= -eps) or (d1 <= eps and d2 <= eps and d3 <= eps)


def _nearest_on_hull(x: float, y: float, hull) -> tuple[tuple[float, float], float]:
    best, best_d = (x, y), float("inf")
    n = len(hull)
    for i in range(n):
        a, b = hull[i], hull[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ll = dx * dx + dy * dy
        t = 0.0 if ll <= 0 else max(0.0, min(1.0, ((x - a[0]) * dx + (y - a[1]) * dy) / ll))
        p = (a[0] + t * dx, a[1] + t * dy)
        d = math.hypot(x - p[0], y - p[1])
        if d < best_d:
            best, best_d = p, d
    return best, best_d


def _inside(x: float, y: float, poly) -> bool:
    inside = False
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def _raw_z(surface: dict, x: float, y: float) -> float:
    kind = surface.get("kind")
    if kind == "planar" and surface.get("plane"):
        a, b, c = surface["plane"]
        return a * x + b * y + c
    if kind == "tin" and surface.get("triangles"):
        pts = surface["points"]
        best = None
        for i, j, k in surface["triangles"]:
            p, q, r = pts[i], pts[j], pts[k]
            if _in_tri(x, y, p, q, r):
                pl = _tri_plane(p, q, r)
                if pl is not None:
                    return pl[0] * x + pl[1] * y + pl[2]
            cx, cy = (p[0] + q[0] + r[0]) / 3.0, (p[1] + q[1] + r[1]) / 3.0
            d = math.hypot(x - cx, y - cy)
            if best is None or d < best[0]:
                best = (d, (p, q, r))
        if best is not None:                         # numerically outside every triangle: the nearest one's plane
            pl = _tri_plane(*best[1])
            if pl is not None:
                return pl[0] * x + pl[1] * y + pl[2]
    return float(surface.get("flat_z") or 0.0)


def surface_z(surface: Optional[dict], x: float, y: float) -> float:
    """The ground z of ``surface`` at ``(x, y)``: the plane or the triangles inside the points' hull (grown by
    ``margin``), blending to the flat ``flat_z`` over ``blend_m`` beyond it."""
    if not surface:
        return 0.0
    flat = float(surface.get("flat_z") or 0.0)
    if surface.get("kind") not in ("planar", "tin"):
        return flat
    hull = [tuple(p) for p in surface.get("hull") or []]
    if len(hull) < 3:
        return _raw_z(surface, x, y)
    if _inside(x, y, hull):
        return _raw_z(surface, x, y)
    edge, d = _nearest_on_hull(x, y, hull)
    margin = float(surface.get("margin") or 0.0)
    if d <= margin:
        return _raw_z(surface, x, y) if surface.get("kind") == "planar" else _raw_z(surface, *edge)
    at_edge = _raw_z(surface, x, y) if surface.get("kind") == "planar" else _raw_z(surface, *edge)
    if surface.get("kind") == "planar":                # the plane at the grown hull's edge
        ex, ey = edge
        ux, uy = (x - ex) / d, (y - ey) / d
        at_edge = _raw_z(surface, ex + ux * margin, ey + uy * margin)
    blend = max(float(surface.get("blend_m") or BLEND_M), 1e-6)
    w = min(1.0, (d - margin) / blend)
    return (1.0 - w) * at_edge + w * flat
