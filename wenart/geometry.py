"""Small 2D geometry helpers shared by the synthetic generator, the ingest
pipeline and the recognition metrics.

Conventions (see docs/milestone2.md):
- A point is ``(x, y)`` or ``[x, y]``; any sequence of two numbers works.
  Functions return plain tuples/lists so results can go straight into JSON.
- A box is axis-aligned ``[x0, y0, x1, y1]`` with ``x0 <= x1`` and ``y0 <= y1``.
- Angles are degrees, counter-clockwise around +Z (``0`` = +X direction).
- An affine transform is a list of six numbers ``[a, b, c, d, e, f]`` meaning
  ``x' = a*x + b*y + c`` and ``y' = d*x + e*y + f`` (the first two rows of the
  3x3 matrix, row-major). This is the layout used by
  ``transform_to_building`` in the building schema.
- A homography is a 3x3 matrix given either as nested lists ``[[..],[..],[..]]``
  or as nine numbers row-major. ``apply_homography`` accepts both.

Pure Python on purpose: no numpy or shapely needed to import this module, so
the helpers can be used in tests and small scripts without extra cost.
"""
from __future__ import annotations

import math
from typing import Iterable, Sequence

Point = Sequence[float]


# --------------------------------------------------------------------------
# Points and segments
# --------------------------------------------------------------------------

def distance(a: Point, b: Point) -> float:
    """Euclidean distance between two points."""
    return math.hypot(b[0] - a[0], b[1] - a[1])


def segment_length(a: Point, b: Point) -> float:
    """Length of the segment a-b (alias of distance, reads better in wall code)."""
    return distance(a, b)


def segment_midpoint(a: Point, b: Point) -> tuple[float, float]:
    """Midpoint of the segment a-b."""
    return ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)


def segment_angle_deg(a: Point, b: Point) -> float:
    """Direction of the segment a->b in degrees, counter-clockwise from +X, in [0, 360)."""
    ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
    return normalise_angle(ang)


def normalise_angle(deg: float) -> float:
    """Bring an angle into [0, 360). -0.0 becomes 0.0."""
    value = deg % 360.0
    return 0.0 if value == 0 else value


def angle_difference_deg(a: float, b: float) -> float:
    """Smallest absolute difference between two angles in degrees (0..180)."""
    diff = abs(normalise_angle(a) - normalise_angle(b))
    return min(diff, 360.0 - diff)


def point_along_segment(a: Point, b: Point, t: float) -> tuple[float, float]:
    """Point at parameter ``t`` (0 = a, 1 = b) along the segment a-b."""
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def point_at_distance(a: Point, b: Point, d: float) -> tuple[float, float]:
    """Point ``d`` units away from ``a`` in the direction of ``b``."""
    length = distance(a, b)
    if length == 0:
        return (a[0], a[1])
    return point_along_segment(a, b, d / length)


def point_segment_distance(p: Point, a: Point, b: Point) -> float:
    """Shortest distance from point p to the segment a-b."""
    ax, ay = a[0], a[1]
    bx, by = b[0], b[1]
    px, py = p[0], p[1]
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / length_sq
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


def unit_normal_left(a: Point, b: Point) -> tuple[float, float]:
    """Unit vector pointing to the left of the direction a->b (rotation by +90 deg)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return (0.0, 0.0)
    return (-dy / length, dx / length)


def rotate_point(p: Point, deg: float, origin: Point = (0.0, 0.0)) -> tuple[float, float]:
    """Rotate p counter-clockwise by ``deg`` degrees around ``origin``."""
    rad = math.radians(deg)
    c, s = math.cos(rad), math.sin(rad)
    x, y = p[0] - origin[0], p[1] - origin[1]
    return (origin[0] + c * x - s * y, origin[1] + s * x + c * y)


def snap(value: float, decimals: int = 6) -> float:
    """Round to a fixed number of decimals so touching edges share exact floats."""
    rounded = round(value, decimals)
    return 0.0 if rounded == 0 else rounded


def snap_point(p: Point, decimals: int = 6) -> tuple[float, float]:
    """Round both coordinates of a point (see ``snap``)."""
    return (snap(p[0], decimals), snap(p[1], decimals))


# --------------------------------------------------------------------------
# Polygons and boxes
# --------------------------------------------------------------------------

def polygon_signed_area(polygon: Sequence[Point]) -> float:
    """Shoelace area; positive for counter-clockwise polygons."""
    n = len(polygon)
    if n < 3:
        return 0.0
    total = 0.0
    for i in range(n):
        x0, y0 = polygon[i][0], polygon[i][1]
        x1, y1 = polygon[(i + 1) % n][0], polygon[(i + 1) % n][1]
        total += x0 * y1 - x1 * y0
    return total / 2.0


def polygon_area(polygon: Sequence[Point]) -> float:
    """Absolute area of a simple polygon (closing vertex optional)."""
    return abs(polygon_signed_area(polygon))


def polygon_centroid(polygon: Sequence[Point]) -> tuple[float, float]:
    """Area centroid of a simple polygon. Falls back to the vertex mean for zero area."""
    area2 = polygon_signed_area(polygon) * 2.0
    n = len(polygon)
    if n == 0:
        return (0.0, 0.0)
    if abs(area2) < 1e-12:
        return (sum(p[0] for p in polygon) / n, sum(p[1] for p in polygon) / n)
    cx = cy = 0.0
    for i in range(n):
        x0, y0 = polygon[i][0], polygon[i][1]
        x1, y1 = polygon[(i + 1) % n][0], polygon[(i + 1) % n][1]
        cross = x0 * y1 - x1 * y0
        cx += (x0 + x1) * cross
        cy += (y0 + y1) * cross
    return (cx / (3.0 * area2), cy / (3.0 * area2))


def point_in_polygon(p: Point, polygon: Sequence[Point]) -> bool:
    """Ray-casting point-in-polygon test. Points exactly on an edge count as inside."""
    x, y = p[0], p[1]
    inside = False
    n = len(polygon)
    for i in range(n):
        x0, y0 = polygon[i][0], polygon[i][1]
        x1, y1 = polygon[(i + 1) % n][0], polygon[(i + 1) % n][1]
        if point_segment_distance(p, (x0, y0), (x1, y1)) < 1e-9:
            return True
        if (y0 > y) != (y1 > y):
            x_cross = x0 + (y - y0) * (x1 - x0) / (y1 - y0)
            if x < x_cross:
                inside = not inside
    return inside


def bbox(points: Iterable[Point]) -> list[float]:
    """Axis-aligned bounding box [x0, y0, x1, y1] of a set of points."""
    pts = list(points)
    if not pts:
        raise ValueError("bbox of no points")
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    return [min(xs), min(ys), max(xs), max(ys)]


def box_center(box: Sequence[float]) -> tuple[float, float]:
    """Centre of an axis-aligned box."""
    return ((box[0] + box[2]) / 2.0, (box[1] + box[3]) / 2.0)


def box_area(box: Sequence[float]) -> float:
    """Area of an axis-aligned box (0 for degenerate boxes)."""
    return max(0.0, box[2] - box[0]) * max(0.0, box[3] - box[1])


def box_iou(a: Sequence[float], b: Sequence[float]) -> float:
    """Intersection over union of two axis-aligned boxes; 0 when they do not overlap."""
    ix0, iy0 = max(a[0], b[0]), max(a[1], b[1])
    ix1, iy1 = min(a[2], b[2]), min(a[3], b[3])
    inter = max(0.0, ix1 - ix0) * max(0.0, iy1 - iy0)
    if inter == 0:
        return 0.0
    union = box_area(a) + box_area(b) - inter
    return inter / union if union > 0 else 0.0


def box_corners(box: Sequence[float]) -> list[tuple[float, float]]:
    """The four corners of an axis-aligned box, counter-clockwise from (x0, y0)."""
    x0, y0, x1, y1 = box
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


# --------------------------------------------------------------------------
# Rectangles <-> centre lines (walls) and rotated footprints (furniture)
# --------------------------------------------------------------------------

def rectangle_to_centerline(corners: Sequence[Point]) -> tuple[tuple[float, float], tuple[float, float], float]:
    """Turn a drawn wall rectangle (4 corners, in drawing order, closing point
    optional) into ``(start, end, thickness)``.

    The long axis is the centre line, the short side the thickness. ``start``
    is the end with the smaller (x, y) so the result does not depend on the
    corner order in the file. Raises ValueError for anything but 4 corners.
    """
    pts = [tuple(p[:2]) for p in corners]
    if len(pts) == 5 and distance(pts[0], pts[-1]) < 1e-9:
        pts = pts[:4]
    if len(pts) != 4:
        raise ValueError(f"wall rectangle needs 4 corners, got {len(pts)}")
    edges = [(pts[i], pts[(i + 1) % 4]) for i in range(4)]
    lengths = [distance(a, b) for a, b in edges]
    # Edges 0 and 2 are parallel, as are 1 and 3. The shorter pair gives the
    # thickness and its midpoints are the centre-line end points.
    if (lengths[0] + lengths[2]) >= (lengths[1] + lengths[3]):
        short_a, short_b = edges[1], edges[3]
        thickness = (lengths[1] + lengths[3]) / 2.0
    else:
        short_a, short_b = edges[0], edges[2]
        thickness = (lengths[0] + lengths[2]) / 2.0
    p = segment_midpoint(*short_a)
    q = segment_midpoint(*short_b)
    start, end = sorted([p, q])
    return (start, end, thickness)


def centerline_to_rectangle(start: Point, end: Point, thickness: float) -> list[tuple[float, float]]:
    """Four corners (counter-clockwise) of the wall rectangle around a centre line."""
    nx, ny = unit_normal_left(start, end)
    h = thickness / 2.0
    return [
        (start[0] - nx * h, start[1] - ny * h),
        (end[0] - nx * h, end[1] - ny * h),
        (end[0] + nx * h, end[1] + ny * h),
        (start[0] + nx * h, start[1] + ny * h),
    ]


def rotated_rectangle(center: Point, size: Sequence[float], rotation_deg: float) -> list[tuple[float, float]]:
    """Corners of a footprint rectangle ``size = [width (X), depth (Y)]`` centred
    at ``center`` and rotated counter-clockwise by ``rotation_deg``.

    Order: local (-w/2,-d/2), (+w/2,-d/2), (+w/2,+d/2), (-w/2,+d/2), i.e. the
    first edge is the front edge (front side = -Y in the local frame).
    """
    w, d = size[0] / 2.0, size[1] / 2.0
    local = [(-w, -d), (w, -d), (w, d), (-w, d)]
    return [rotate_point((center[0] + x, center[1] + y), rotation_deg, center) for x, y in local]


def front_direction_deg(rotation_deg: float) -> float:
    """Direction a piece faces for a footprint rotation (front side = local -Y)."""
    return normalise_angle(270.0 + rotation_deg)


# --------------------------------------------------------------------------
# Affine transforms and homographies
# --------------------------------------------------------------------------

def affine_identity() -> list[float]:
    return [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]


def affine_from_scale_translate(sx: float, sy: float, tx: float, ty: float) -> list[float]:
    """Affine ``x' = sx*x + tx``, ``y' = sy*y + ty``."""
    return [sx, 0.0, tx, 0.0, sy, ty]


def affine_to_matrix(m6: Sequence[float]) -> list[list[float]]:
    """6-number affine -> 3x3 homography matrix."""
    a, b, c, d, e, f = m6
    return [[a, b, c], [d, e, f], [0.0, 0.0, 1.0]]


def matrix_to_affine(matrix: Sequence[Sequence[float]]) -> list[float]:
    """3x3 matrix with last row [0,0,1] -> 6-number affine. Raises if it is projective."""
    m = _as_matrix(matrix)
    if abs(m[2][0]) > 1e-12 or abs(m[2][1]) > 1e-12 or abs(m[2][2] - 1.0) > 1e-9:
        raise ValueError("matrix is not affine")
    return [m[0][0], m[0][1], m[0][2], m[1][0], m[1][1], m[1][2]]


def apply_affine(m6: Sequence[float], p: Point) -> tuple[float, float]:
    """Apply a 6-number affine to a point."""
    a, b, c, d, e, f = m6
    x, y = p[0], p[1]
    return (a * x + b * y + c, d * x + e * y + f)


def compose_affine(outer: Sequence[float], inner: Sequence[float]) -> list[float]:
    """Affine that applies ``inner`` first, then ``outer``."""
    return matrix_to_affine(matmul(affine_to_matrix(outer), affine_to_matrix(inner)))


def invert_affine(m6: Sequence[float]) -> list[float]:
    """Inverse of a 6-number affine. Raises ZeroDivisionError for singular transforms."""
    a, b, c, d, e, f = m6
    det = a * e - b * d
    if det == 0:
        raise ZeroDivisionError("singular affine")
    ia, ib, id_, ie = e / det, -b / det, -d / det, a / det
    return [ia, ib, -(ia * c + ib * f), id_, ie, -(id_ * c + ie * f)]


def _as_matrix(h) -> list[list[float]]:
    """Accept a 3x3 nested list or nine row-major numbers."""
    if len(h) == 9 and not isinstance(h[0], (list, tuple)):
        return [[float(h[0]), float(h[1]), float(h[2])],
                [float(h[3]), float(h[4]), float(h[5])],
                [float(h[6]), float(h[7]), float(h[8])]]
    if len(h) == 3 and len(h[0]) == 3:
        return [[float(v) for v in row] for row in h]
    raise ValueError("homography must be 3x3 or nine numbers")


def matmul(a: Sequence[Sequence[float]], b: Sequence[Sequence[float]]) -> list[list[float]]:
    """3x3 matrix product a @ b."""
    a, b = _as_matrix(a), _as_matrix(b)
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def apply_homography(h, p: Point) -> tuple[float, float]:
    """Apply a 3x3 homography (nested list or nine numbers) to a point."""
    m = _as_matrix(h)
    x, y = p[0], p[1]
    w = m[2][0] * x + m[2][1] * y + m[2][2]
    return ((m[0][0] * x + m[0][1] * y + m[0][2]) / w,
            (m[1][0] * x + m[1][1] * y + m[1][2]) / w)


def invert_homography(h) -> list[list[float]]:
    """Inverse of a 3x3 matrix by cofactors."""
    m = _as_matrix(h)
    (a, b, c), (d, e, f), (g, hh, i) = m
    det = a * (e * i - f * hh) - b * (d * i - f * g) + c * (d * hh - e * g)
    if det == 0:
        raise ZeroDivisionError("singular homography")
    adj = [
        [e * i - f * hh, c * hh - b * i, b * f - c * e],
        [f * g - d * i, a * i - c * g, c * d - a * f],
        [d * hh - e * g, b * g - a * hh, a * e - b * d],
    ]
    return [[v / det for v in row] for row in adj]


def apply_transform(t, p: Point) -> tuple[float, float]:
    """Apply a transform of either kind: 6-number affine, 3x3 matrix or nine numbers."""
    if len(t) == 6 and not isinstance(t[0], (list, tuple)):
        return apply_affine(t, p)
    return apply_homography(t, p)


def transform_points(t, points: Iterable[Point]) -> list[tuple[float, float]]:
    """Apply a transform (see ``apply_transform``) to many points."""
    return [apply_transform(t, p) for p in points]


def transform_box(t, box: Sequence[float]) -> list[float]:
    """Map a box through a transform and return the axis-aligned box of the result."""
    return bbox(transform_points(t, box_corners(box)))
