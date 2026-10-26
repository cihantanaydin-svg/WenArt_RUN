"""The roof of the whole building (docs/milestone10.md §3.2 items 2-3, §1.6a).

What:

- ``planes_for(roof, building)`` derives the roof planes (3D polygons of the outer roof surface, the
  ``roof.planes`` format of the building schema) from the roof type, the eaves outline, the eaves and
  ridge heights, the pitches, the ridge lines and (mansard, gambrel) the closed break line. The pipeline
  leaves ``roof.planes`` empty; the builder records what it used in the scene manifest.
- ``roof_model(roof, building)`` decides what the scene builds: the drawn planes when the building has
  them, else the derived ones, the thickness, the roof terraces (``roof.openings``) and every value no
  drawing gives (``assumed``, with the reason).
- The mesh helpers turn the model into the roof solid (``roof_solid``: covering on top, soffit under it,
  fascia on the edges, terraces cut out), the walls under the roof into knee walls and gable ends
  (``clip_solid_below``: a wall box cut by the roof underside) and the ceilings of the rooms under it into
  sloped faces (``ceiling_faces``).
- ``build_roof`` (bpy) makes the roof object.

Why: Milestone 10 builds the whole building: real02 has a mansard roof (two pitches, about 40 and 13
degrees, eaves 0.50 m above the attic floor and 0.50 m outside the wall, a closed break line on the attic
plan) with roof terraces cut into it; the example building a gable roof with a terrace.

How: every roof plane is ``z = a x + b y + c`` (``plane_from_points``). The roof types derived here are
convex, so the outer roof surface is the lowest plane at every point (``surface_z``) and the region where
one plane is the lowest is convex: clipping a convex piece of the outline by the half-planes ``plane_i <=
plane_j`` gives that plane's face, and the same for the underside (each plane lowered by
``thickness / cos(slope)``) and for the attic ceilings (the underside 1 mm lower, and the flat ceiling of
the level where the section shows one: ``level.ceiling_height``). Rectangular roofs are derived on the
outline's smallest enclosing rectangle (``geom2d.oriented_rectangle``); another outline is simplified to that
rectangle and the simplification is listed as assumed. Plane names follow the downhill direction in the
building frame (+Y = north): ``rp_south`` slopes down to -Y. Pure Python (Blender's Python has no shapely or
numpy needs here), tested on the CPU (tests/test_blender_roof.py).

Conventions of the contract (building.schema.json ``roof``, docs/milestone10.md §1.6b rows 1 and 13): planes,
``eaves_height`` and ``ridge_height`` are the top surface in building z; ``thickness`` is measured square to the
slope; ``overhang`` is used only without a drawn outline; ``knee_wall`` (the top surface at the outer wall face
minus the attic floor; the example: eaves 3.65 + 0.5 m x tan 35 = 4.00 = floor 3.00 + 1.00) is a cross-check
(``knee_wall_check``), and only fills the eaves when no eaves height is given; ``aspect_deg`` is the downhill
direction in degrees counter-clockwise from +X (downhill -Y = 270), not a compass bearing; roof terrace
openings reach over the outer walls to the outline, and their ``parapet_wall_ids`` (else the outer walls under
the opening) end at the parapet height there (``parapet_cuts``). Without any roof evidence the pipeline writes
``roof: null`` and the build makes an assumed flat roof over the top level (``flat_roof``).

The drawn section (``roof.profile``, review #22): when it peaks inside, the ridge runs across the cut through
its peak (``section_profile``; assumed ``ridge_direction``: one section), and a mansard or gambrel takes its tiers
from it (``_profile_tiers``: the drawn slopes, break and ridge heights; a mansard's two uncut sides take the lower
pitch and run up to the ridge, assumed ``mansard_ends``); the plan's break line, pitches and eaves are
cross-checks (warnings), and every derived roof is compared with its section (``profile_check``). Without
ridge line or section the long-axis ridge of a gable or gambrel is assumed (``ridge_direction``).

The roof follows its drawn section (26 Oct 2026, ``follow_section``; CLAUDE.md evidence rules: source geometry
outranks a pitch text, a default and an un-drawn ridge direction): when the built roof's ridge (the highest point of its
planes) or, for a reliable profile (``section_reliability``: one-to-one with the plan, one roof surface), its silhouette
(``profile_diffs``) differs from the drawing by more than ``SECTION_TOL``, an un-drawn ridge direction is turned or the
pitch is solved so the ridge meets the drawn height; the eaves and the outline stay. The record is ``section_fit``.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d

Plane = tuple[float, float, float]           # z = a x + b y + c

ROOF_TYPES = ("flat", "gable", "hip", "mansard", "gambrel", "shed", "other")
DEFAULTS = {
    "pitch_deg": 30.0,           # no pitch and no ridge height drawn
    "shed_pitch_deg": 10.0,
    "overhang": 0.50,            # only used when the outline is not drawn, or for the knee-wall eaves
    "thickness": 0.25,           # the roof is one line in most sections
    "knee_wall": 1.00,           # an attic without eaves height and knee wall
    "parapet": 1.00,             # a roof terrace without a drawn parapet
    "terrace_parapet_min": 0.30,  # a pitched roof's terrace wall stops at the eaves line when that is this high or more
    "flat_thickness": 0.30,      # a flat roof slab
    "flat_cut_parapet": 0.30,    # Milestone 12: the parapet of a flat_cut roof (a single drawn ground floor)
    "parapet_thickness": 0.20,
}
EAVES_JOG_MAX_M = 0.60           # 26 Oct 2026: facade jogs shallower than this run under one straight eaves line
EAVES_MIN_COVER_M = 0.15         # ... and every wall face keeps at least this much roof over it
# 26 Oct 2026 (Argus on real06; CLAUDE.md evidence rules: a drawn section is source geometry and outranks a pitch text
# or a default): the built roof follows the drawn section's heights within SECTION_TOL (``follow_section``).
SECTION_TOL = 0.25               # m: the built ridge / the section's points may differ this much from the drawing
SECTION_LIST_TOL = 0.05          # m: a smaller difference is not listed (a warning above it, within SECTION_TOL too)
SECTION_SPAN_TOL = 0.30          # m: a profile whose ends lie further from the outline is not compared point by point
SECTION_PITCH_DEG = (5.0, 60.0)  # the pitch that meets the drawn heights must lie in this range, else the roof is kept
SILHOUETTE_STEP = 0.05           # m: the roof's silhouette across the outline (what a section draws) is sampled so
CEILING_GAP = 0.001              # attic ceilings stay this far under the roof underside (no coplanar faces)
CONVEX_TOL = 0.01                # drawn planes: a plane more than this above another at its own corners -> not convex
SAME_TOL = 0.02                  # equivalent planes: corners within 2 cm
MIN_PIECE_AREA = geom2d.MIN_PIECE_AREA


# --------------------------------------------------------------------------
# Planes
# --------------------------------------------------------------------------

def plane_from_points(points: Sequence[Sequence[float]]) -> Optional[Plane]:
    """``(a, b, c)`` of ``z = a x + b y + c`` through a planar 3D polygon (Newell normal); None for a vertical
    or degenerate one."""
    pts = [(float(p[0]), float(p[1]), float(p[2])) for p in points]
    if len(pts) < 3:
        return None
    nx, ny, nz = geom2d.face_normal(pts, list(range(len(pts))))
    if abs(nz) < 1e-9:
        return None
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    cz = sum(p[2] for p in pts) / len(pts)
    a, b = -nx / nz, -ny / nz
    return (a, b, cz - a * cx - b * cy)


plane_z = geom2d.plane_z
surface_z = geom2d.surface_z
plane_regions = geom2d.plane_regions


def slope_aspect(plane: Plane) -> tuple[float, Optional[float]]:
    """``(slope_deg, aspect_deg)``: the slope and the downhill direction, degrees counter-clockwise from +X
    (downhill -Y = 270; None for a flat plane)."""
    a, b = plane[0], plane[1]
    g = math.hypot(a, b)
    slope = math.degrees(math.atan(g))
    if g < 1e-9:
        return round(slope, 4), None
    return round(slope, 4), round(math.degrees(math.atan2(-b, -a)) % 360.0, 4)


def lowered(plane: Plane, thickness: float) -> Plane:
    """The plane ``thickness`` metres (measured square to it) below: ``c - t / cos(slope)``."""
    a, b, c = plane
    return (a, b, c - float(thickness) * math.sqrt(1.0 + a * a + b * b))


def _ramp(base: Sequence[float], inward: Sequence[float], z0: float, tan_pitch: float) -> Plane:
    """The plane that is ``z0`` on the line through ``base`` square to ``inward`` and rises along ``inward``
    by ``tan_pitch`` per metre."""
    ix, iy = float(inward[0]), float(inward[1])
    a, b = tan_pitch * ix, tan_pitch * iy
    return (a, b, z0 - a * float(base[0]) - b * float(base[1]))


def side_name(aspect: Optional[float]) -> str:
    """The plane name's word for a downhill direction (counter-clockwise from +X) in the building frame,
    +Y read as north: ``south`` = down to -Y (270), ``east`` = +X (0)."""
    if aspect is None:
        return "flat"
    return ("east", "north", "west", "south")[int(((aspect + 45.0) % 360.0) // 90.0)]


def _region_polygons(planes: Sequence[Plane], outline: Sequence[Sequence[float]]) -> list[list]:
    """Per plane its face polygon on the outline (the outline clipped by its half-planes; a concave outline
    clipped the Sutherland-Hodgman way keeps its area)."""
    out = []
    for i, pi in enumerate(planes):
        poly = geom2d.ccw(outline)
        for j, pj in enumerate(planes):
            if j == i or not poly:
                continue
            poly = geom2d.clip_half_plane(poly, pi[0] - pj[0], pi[1] - pj[1], pi[2] - pj[2] - (1e-9 if j < i else 0.0))
        # clipping through a corner can repeat it: drop repeated points (closing one included)
        poly = [p for k, p in enumerate(poly) if G.distance(p, poly[k - 1]) > 1e-6] if len(poly) > 1 else poly
        poly = geom2d._drop_collinear(poly, 1e-7) if len(poly) > 3 else poly
        out.append(poly if len(poly) >= 3 and G.polygon_area(poly) > MIN_PIECE_AREA else [])
    return out


def planes_from_equations(planes: Sequence[Plane], outline: Sequence[Sequence[float]], names: Sequence[str],
                          source: str = "derived") -> list[dict]:
    """``roof.planes`` entries of plane equations on an outline (planes with no face there are left out)."""
    out = []
    used: dict[str, int] = {}
    for plane, poly, name in zip(planes, _region_polygons(planes, outline), names):
        if not poly:
            continue
        slope, aspect = slope_aspect(plane)
        pid = name
        if pid in used:
            used[pid] += 1
            pid = f"{name}_{used[name]}"
        else:
            used[pid] = 1
        out.append({"id": pid, "points": [[round(x, 4), round(y, 4), round(plane_z(plane, x, y), 4)] for x, y in poly],
                    "slope_deg": round(slope, 3), "aspect_deg": None if aspect is None else round(aspect, 3),
                    "source": source})
    return out


def equivalent_planes(a: Sequence[dict], b: Sequence[dict], tol: float = SAME_TOL) -> tuple[bool, str]:
    """``(same, why not)``: two plane lists describe the same roof surface: one-to-one, the same slope
    (0.5 degree) and downhill direction (1 degree) and every corner of each polygon within ``tol`` of a corner
    of the other (vertex order and start do not matter)."""
    if len(a) != len(b):
        return False, f"{len(a)} planes vs {len(b)}"
    free = list(b)

    def near(p, q):
        return math.dist([float(v) for v in p[:3]], [float(v) for v in q[:3]]) <= tol

    for pa in a:
        sa, aa = slope_aspect(plane_from_points(pa["points"]) or (0.0, 0.0, 0.0))
        hit = None
        for pb in free:
            sb, ab = slope_aspect(plane_from_points(pb["points"]) or (0.0, 0.0, 0.0))
            if abs(sa - sb) > 0.5 or (aa is None) != (ab is None):
                continue
            if aa is not None and abs((aa - ab + 180.0) % 360.0 - 180.0) > 1.0:
                continue
            pts_a, pts_b = pa["points"], pb["points"]
            if all(any(near(p, q) for q in pts_b) for p in pts_a) and all(any(near(q, p) for p in pts_a) for q in pts_b):
                hit = pb
                break
        if hit is None:
            return False, f"no plane like {pa.get('id')} (slope {sa}, aspect {aa})"
        free.remove(hit)
    return True, ""


# --------------------------------------------------------------------------
# Deriving the planes (planes_for)
# --------------------------------------------------------------------------

def _value(entry) -> Optional[float]:
    if isinstance(entry, dict):
        v = entry.get("value")
        return None if v is None else float(v)
    if isinstance(entry, (int, float)) and not isinstance(entry, bool):
        return float(entry)
    return None


def _is_assumed(entry) -> bool:
    return isinstance(entry, dict) and entry.get("method") == "assumed"


def over_level(roof: dict, building: dict) -> Optional[dict]:
    """The level the roof covers: ``over_level_id``, else the highest level."""
    levels = building.get("levels") or []
    lid = roof.get("over_level_id")
    found = next((lv for lv in levels if lv["id"] == lid), None) if lid else None
    if found is None and levels:
        found = max(levels, key=lambda lv: float(lv.get("elevation") or 0.0))
    return found


def section_profile(roof: dict, rect: dict) -> Optional[dict]:
    """The drawn section of the roof (``roof.profile``, §1.6b row 13: ``cut_axis`` and the top surface as ``[s,
    z]`` points, ``s`` the building coordinate along the cut) read for its ridge and tiers (pure), or None
    when it gives no single ridge: fewer than 3 points, a cut not along an axis of the outline rectangle, the
    highest point at an end, or a flat top. Returns ``{"cut": unit vector of the cut, "ridge_dir": the
    ridge direction (across the cut), "eaves": [(s, z) of both ends], "peak": (s, z), "sides": [[(s, z), ...]
    from each eaves point to the peak], "cut_at"}``."""
    prof = roof.get("profile") if isinstance(roof.get("profile"), dict) else None
    if not prof or prof.get("cut_axis") not in ("x", "y"):
        return None
    pts = sorted((float(p[0]), float(p[1])) for p in prof.get("points") or []
                 if isinstance(p, (list, tuple)) and len(p) >= 2)
    if len(pts) < 3:
        return None
    cut = (1.0, 0.0) if prof["cut_axis"] == "x" else (0.0, 1.0)
    if max(abs(rect["u"][0] * cut[0] + rect["u"][1] * cut[1]), abs(rect["v"][0] * cut[0] + rect["v"][1] * cut[1])) < 0.999:
        return None
    k = max(range(len(pts)), key=lambda i: pts[i][1])
    if k in (0, len(pts) - 1) or any(abs(p[1] - pts[k][1]) < 1e-3 for i, p in enumerate(pts) if i != k):
        return None
    return {"cut": cut, "ridge_dir": (-cut[1], cut[0]), "eaves": [pts[0], pts[-1]], "peak": pts[k],
            "sides": [pts[:k + 1], pts[k:][::-1]], "cut_at": prof.get("cut_at")}


def _ridge_axis(rect: dict, roof: dict) -> tuple[tuple[float, float], tuple[float, float], float, float,
                                                  Optional[float], str]:
    """``(r, across, half_along, half_across, ridge_half_length, source)`` of a rectangle: the ridge
    direction from the longest drawn ridge line (snapped to the nearer rectangle axis), else across the cut of
    the drawn section when it peaks inside (``section_profile``: source ``profile``), else the long axis."""
    u, v = rect["u"], rect["v"]
    a, b = rect["half"]
    lines = [ln for ln in roof.get("ridge_lines") or [] if isinstance(ln, (list, tuple)) and len(ln) == 2]
    if lines:
        p, q = max(lines, key=lambda ln: G.distance(ln[0], ln[1]))
        length = G.distance(p, q)
        if length > 1e-6:
            d = ((q[0] - p[0]) / length, (q[1] - p[1]) / length)
            if abs(d[0] * u[0] + d[1] * u[1]) >= abs(d[0] * v[0] + d[1] * v[1]):
                return u, v, a, b, length / 2.0, "ridge_lines"
            return v, (-v[1], v[0]), b, a, length / 2.0, "ridge_lines"
        return u, v, a, b, 0.0, "ridge_lines"
    prof = section_profile(roof, rect)
    if prof is not None:
        d = prof["ridge_dir"]
        if abs(d[0] * u[0] + d[1] * u[1]) >= abs(d[0] * v[0] + d[1] * v[1]):
            return u, v, a, b, None, "profile"
        return v, (-v[1], v[0]), b, a, None, "profile"
    return u, v, a, b, None, "long axis"


def _profile_tiers(prof: dict, outline: Sequence[Sequence[float]], rtype: str, eaves: Optional[float],
                   break_line: Optional[Sequence[Sequence[float]]] = None) -> tuple[list[Plane], list[str], dict]:
    """The mansard or gambrel tiers of a drawn section (``section_profile``; pure): on both sides of the cut the
    lower plane from the eaves point to the break point and the upper plane from the break point to the peak,
    their slopes as drawn; the upper planes meet in the ridge across the cut at the peak. A mansard also gets
    planes on the two sides the section does not cut (``eaves`` at the outline edges; assumed). Milestone 11
    (docs/milestone11.md §1.1 E7): with the plan's closed ``break_line`` the lower plane there rises from the
    eaves to the break line, at the section's break height (the mean of its two breaks), and an upper plane rises
    from the break line at the section's upper pitch, steeper when that cannot reach the section's ridge height
    (the hip then meets the ridge, so the roof still matches its section); without a break line the M10 rule:
    the mean drawn lower slope up to the ridge. Returns ``(planes, tier names, info)`` with ``info`` =
    ``{"breaks": [(s, z) per side], "lower_deg", "upper_deg", "notes", "ends"}`` (``ends``: how the uncut sides
    were made, None for a gambrel)."""
    cut, ridge_dir = prof["cut"], prof["ridge_dir"]
    s_p, z_p = prof["peak"]
    planes, names, notes, breaks, lower_deg, upper_deg = [], [], [], [], [], []
    for side, pts in zip((1.0, -1.0), prof["sides"]):
        (s_e, z_e), (s_b, z_b) = pts[0], pts[1] if len(pts) > 2 else pts[-1]
        if len(pts) > 3:
            notes.append(f"the section has {len(pts) - 2} slope breaks on one side: the lower slope to the first, the "
                         f"upper slope from the last")
        inward = (cut[0] * side, cut[1] * side)
        base = (cut[0] * s_e, cut[1] * s_e)
        tan_low = (z_b - z_e) / abs(s_b - s_e) if abs(s_b - s_e) > 1e-6 else 0.0
        planes.append(_ramp(base, inward, z_e, tan_low))
        names.append("lower")
        lower_deg.append(math.degrees(math.atan(tan_low)))
        if len(pts) > 2:
            s_u, z_u = pts[-2]
            tan_up = (z_p - z_u) / abs(s_p - s_u) if abs(s_p - s_u) > 1e-6 else 0.0
            planes.append(_ramp((cut[0] * s_u, cut[1] * s_u), inward, z_u, tan_up))
            names.append("upper")
            upper_deg.append(math.degrees(math.atan(tan_up)))
        breaks.append((s_b, z_b))
    ends = None
    if rtype == "mansard":
        t_side = math.tan(math.radians(sum(lower_deg) / len(lower_deg)))
        z0 = eaves if eaves is not None else sum(e[1] for e in prof["eaves"]) / 2.0
        proj = [x * ridge_dir[0] + y * ridge_dir[1] for x, y in outline]
        brk = geom2d.ccw(break_line or [])
        bproj = [x * ridge_dir[0] + y * ridge_dir[1] for x, y in brk]
        inside = len(brk) >= 3 and min(proj) + 1e-3 < min(bproj) < max(bproj) < max(proj) - 1e-3
        if inside:
            # E7: the plan's break line on the uncut sides (a four-sided mansard as the attic plan draws it).
            z_b = sum(b[1] for b in breaks) / len(breaks)
            half = (max(bproj) - min(bproj)) / 2.0
            tan_up = math.tan(math.radians(sum(upper_deg) / len(upper_deg))) if upper_deg else 0.0
            tan_end = max(tan_up, (z_p - z_b) / half) if half > 1e-6 else tan_up
            lows = []
            for side, w, wb in ((1.0, min(proj), min(bproj)), (-1.0, max(proj), max(bproj))):
                inward = (ridge_dir[0] * side, ridge_dir[1] * side)
                tan_low = (z_b - z0) / abs(wb - w)
                planes.append(_ramp((ridge_dir[0] * w, ridge_dir[1] * w), inward, z0, tan_low))
                names.append("lower")
                planes.append(_ramp((ridge_dir[0] * wb, ridge_dir[1] * wb), inward, z_b, tan_end))
                names.append("upper")
                lows.append(math.degrees(math.atan(tan_low)))
            ends = {"source": "break_line", "lower_deg": [round(d, 2) for d in lows],
                    "upper_deg": round(math.degrees(math.atan(tan_end)), 2), "break_z": round(z_b, 4),
                    "steepened": tan_end > tan_up + 1e-9}
        else:
            for side, w in ((1.0, min(proj)), (-1.0, max(proj))):
                planes.append(_ramp((ridge_dir[0] * w, ridge_dir[1] * w), (ridge_dir[0] * side, ridge_dir[1] * side),
                                    z0, t_side))
                names.append("lower")
            ends = {"source": "section lower pitch", "lower_deg": [round(math.degrees(math.atan(t_side)), 2)] * 2,
                    "upper_deg": None, "break_z": None, "steepened": False}
    return planes, names, {"breaks": breaks, "lower_deg": lower_deg, "upper_deg": upper_deg, "notes": notes,
                           "ends": ends}


def profile_points(prof: dict) -> list[tuple[float, float]]:
    """The ``[(s, z)]`` points of a ``section_profile`` from one eaves end to the other."""
    return list(prof["sides"][0]) + list(prof["sides"][1][::-1][1:])


def roof_silhouette(planes: Sequence[Plane], outline: Sequence[Sequence[float]], cut: Sequence[float],
                    ridge_dir: Sequence[float], s: float, step: float = SILHOUETTE_STEP) -> Optional[float]:
    """The highest point of the roof surface over the outline on the line across the cut at ``s`` (pure): what a
    section's roof line draws (the cut and the roof seen beyond it; the middle line for a symmetric roof). ``s``
    within ``SECTION_SPAN_TOL`` outside the outline is read at its edge (a longer drawn overhang); None further out."""
    along = [x * cut[0] + y * cut[1] for x, y in outline]
    proj = [x * ridge_dir[0] + y * ridge_dir[1] for x, y in outline]
    lo, hi = min(along), max(along)
    if s < lo - SECTION_SPAN_TOL or s > hi + SECTION_SPAN_TOL:
        return None
    s = min(max(s, lo), hi)
    t0, t1 = min(proj), max(proj)
    n = max(1, int(math.ceil((t1 - t0) / step)))
    best = None
    for k in range(n + 1):
        t = t0 + (t1 - t0) * k / n
        x, y = cut[0] * s + ridge_dir[0] * t, cut[1] * s + ridge_dir[1] * t
        if G.point_in_polygon((x, y), outline):
            z = surface_z(planes, x, y)
            best = z if best is None or z > best else best
    return best


def profile_diffs(planes: Sequence[Plane], prof: dict,
                  outline: Sequence[Sequence[float]]) -> list[tuple[float, float, float]]:
    """``[(s, built z, drawn z)]`` of every profile point of a drawn section (pure): the roof's silhouette across the
    outline at the point's ``s`` (``roof_silhouette``) against the drawn height; points with no roof under them are
    left out (``section_reliability`` names them)."""
    out = []
    for s, z in profile_points(prof):
        got = roof_silhouette(planes, outline, prof["cut"], prof["ridge_dir"], s)
        if got is not None:
            out.append((s, got, z))
    return out


def profile_check(planes: Sequence[Plane], prof: dict, outline: Sequence[Sequence[float]],
                  tol: float = SECTION_LIST_TOL) -> list[str]:
    """Where the roof surface of ``planes`` differs from the drawn section by more than ``tol`` (pure;
    ``profile_diffs``). Returns warnings (empty when the roof matches its section)."""
    return [f"roof vs the drawn section at s {s:.2f} m: {got:.3f} m built, {z:.3f} m drawn ({(got - z) * 100:+.0f} cm)"
            for s, got, z in profile_diffs(planes, prof, outline) if abs(got - z) > tol]


def section_reliability(prof: dict, outline: Sequence[Sequence[float]],
                        axis: Optional[str] = None) -> tuple[bool, list[str]]:
    """Whether a drawn section's profile (``section_profile``) can be compared with the roof point by point (pure;
    26 Oct 2026, real06): its two eaves ends lie within ``SECTION_SPAN_TOL`` of the roof outline's ends along the cut
    (else the section and the plan do not run one-to-one: a porch, a wider cut), and it is one roof surface: from each
    eaves end up to its highest point it never drops more than ``SECTION_TOL`` (else other lines are drawn with the
    roof: trusses, trims, a dormer or a chimney). Returns ``(ok, reasons)``. An unreliable profile still gives its eaves
    and ridge heights (the highest roof line); only its shape is not followed."""
    pts = profile_points(prof)
    cut = prof["cut"]
    along = [x * cut[0] + y * cut[1] for x, y in outline]
    lo, hi = min(along), max(along)
    reasons = []
    off = max(abs(pts[0][0] - lo), abs(pts[-1][0] - hi))
    if off > SECTION_SPAN_TOL:
        reasons.append(f"its ends at s {pts[0][0]:.2f} / {pts[-1][0]:.2f} m and the roof outline's at {lo:.2f} / "
                       f"{hi:.2f} m along {axis or 'the cut'} are up to {off:.2f} m apart (over {SECTION_SPAN_TOL:.2f} "
                       f"m: the section does not run one-to-one with the plan)")
    dip, at = 0.0, None
    for side in prof["sides"]:                       # each from its eaves point up to the peak
        top = None
        for s, z in side:
            if top is not None and top - z > dip:
                dip, at = top - z, s
            top = z if top is None else max(top, z)
    if dip > SECTION_TOL:
        reasons.append(f"its roof line drops {dip:.2f} m at s {at:.2f} m on the way up to its highest point (trusses, "
                       f"trims or another roof drawn with it: not one roof surface)")
    return not reasons, reasons


def _rect_planes(centre, r, across, half_along: float, half_across: float, z0: float, tan_side: float,
                 ends: str, ridge_half: Optional[float], base: str) -> tuple[list[Plane], list[str], list[str]]:
    """Planes over a rectangle (``centre``, ridge direction ``r``, ``across`` = ``r`` turned 90 degrees):
    two sides rising from the long edges at ``tan_side`` to the ridge, and ``ends``: ``gable`` (none: the
    gable walls close the ends) or ``hip`` (rising from the short edges; with ``ridge_half`` the drawn ridge
    half-length sets their pitch, else the side pitch). Returns ``(planes, names, notes)``."""
    cx, cy = centre
    planes, names, notes = [], [], []
    for sgn in (1.0, -1.0):
        edge = (cx + across[0] * half_across * sgn, cy + across[1] * half_across * sgn)
        planes.append(_ramp(edge, (-across[0] * sgn, -across[1] * sgn), z0, tan_side))
        names.append(base)
    if ends == "hip":
        rise = half_across * tan_side
        if ridge_half is not None and ridge_half < half_along - 1e-3:
            inset = half_along - max(0.0, ridge_half)
            tan_end = rise / inset
            notes.append(f"hip ends from the drawn ridge length {2 * ridge_half:.2f} m "
                         f"({math.degrees(math.atan(tan_end)):.1f} degrees)")
        elif ridge_half is not None:
            tan_end = None
            notes.append("the drawn ridge runs the full length: gable ends")
        else:
            tan_end = tan_side
        if tan_end is not None:
            for sgn in (1.0, -1.0):
                edge = (cx + r[0] * half_along * sgn, cy + r[1] * half_along * sgn)
                planes.append(_ramp(edge, (-r[0] * sgn, -r[1] * sgn), z0, tan_end))
                names.append(base)
    return planes, names, notes


def _named(planes: Sequence[Plane], names: Sequence[str]) -> list[str]:
    return [f"rp_{side_name(slope_aspect(p)[1])}" + (f"_{n}" if n else "") for p, n in zip(planes, names)]


def _turned(axis: tuple) -> tuple:
    """A ``_ridge_axis`` result with the ridge turned 90 degrees (the other axis of the rectangle)."""
    r, across, half_along, half_across, ridge_half, source = axis
    return across, (-across[1], across[0]), half_across, half_along, None, source


def derive(roof: dict, building: dict) -> dict:
    """The derivation behind ``planes_for``: ``{"planes": [...], "equations": [(a, b, c)], "outline",
    "eaves_z", "ridge_z", "pitches", "assumed": [{"field", "value", "reason"}], "warnings", "notes",
    "section_fit", "follows_section"}``. ``ridge_z`` is the highest point of the built planes. The derived roof
    then follows its drawn section (``follow_section``, 26 Oct 2026)."""
    return follow_section(roof, building, _derive(roof, building))


def _derive(roof: dict, building: dict, pitch: Optional[float] = None, turn: bool = False) -> dict:
    """One derivation of the roof (``derive``). ``pitch`` replaces the pitch the drawn section may set (the pitch of a
    gable, hip or shed, the upper pitch of a mansard or gambrel without section tiers); ``turn`` turns a ridge
    direction no ridge line draws by 90 degrees. The private ``_ctx`` says what ``follow_section`` may change."""
    rtype = str(roof.get("type") or "other")
    assumed: list[dict] = []
    warnings: list[str] = []
    notes: list[str] = []
    level = over_level(roof, building)
    floor_z = float(level["elevation"]) if level else 0.0
    if not roof.get("over_level_id"):
        assumed.append({"field": "over_level_id", "value": level["id"] if level else None,
                        "reason": "not given: the roof covers the highest level"})

    overhang = _value(roof.get("overhang"))
    overhang_assumed = overhang is None or _is_assumed(roof.get("overhang"))
    if overhang is None:
        overhang = 0.0 if rtype == "flat" else DEFAULTS["overhang"]

    outline = geom2d.ccw(roof.get("outline") or [])
    if len(outline) < 3:
        walls = [w for w in building.get("walls") or [] if level and w.get("level_id") == level["id"]]
        wall_line, method = geom2d.wall_outline(walls)
        if len(wall_line) < 3:
            return {"planes": [], "equations": [], "outline": [], "eaves_z": None, "ridge_z": None, "pitches": [],
                    "assumed": assumed, "warnings": ["no roof outline and no walls under the roof: no roof"],
                    "notes": notes, "_ctx": {"fit": None}}
        # The walls' own outline grown by the overhang (review #26: an L-shaped level keeps its notch open; the
        # planes are derived on the enclosing rectangle and cut to it, listed as outline_rectangle below).
        # 26 Oct 2026 (user: "why there is that many rain gutters in real06"): a pitched roof's eaves run straight
        # past the shallow jogs of the facade (piers, pilasters, shallow recesses): they are closed first, so the
        # gutter is one line per facade, not one per pier (real06: 70 outline points, 27 gutters, 20 downpipes)
        closed = 0
        if rtype != "flat":
            wall_line, closed = geom2d.close_jogs(wall_line, EAVES_JOG_MAX_M,
                                                  inward_max=max(0.0, overhang - EAVES_MIN_COVER_M))
        outline = geom2d.ccw(geom2d.offset_polygon(wall_line, -overhang) if overhang > 0 else wall_line)
        assumed.append({"field": "outline", "value": [[round(x, 4), round(y, 4)] for x, y in outline],
                        "reason": f"no roof outline drawn: the walls' outline ({method}) grown by the "
                                  f"{'assumed ' if overhang_assumed else ''}overhang {overhang:.2f} m"
                                  + (f"; {closed} facade jog(s) shallower than {EAVES_JOG_MAX_M:.2f} m closed "
                                     f"under the eaves (one eaves line per facade)" if closed else "")})
        overhang_used = True
    else:
        overhang_used = False
    rect = geom2d.oriented_rectangle(outline)
    if rtype not in ("flat",) and rect["fill"] < 0.98:
        assumed.append({"field": "outline_rectangle", "value": round(rect["fill"], 3),
                        "reason": f"the {len(outline)}-point outline is not a rectangle: the {rtype} planes are "
                                  f"derived on its smallest enclosing rectangle and cut to the outline"})

    pitches = [_value(p) for p in roof.get("pitches_deg") or []]
    pitches = [p for p in pitches if p is not None]
    eaves = _value(roof.get("eaves_height"))
    ridge = _value(roof.get("ridge_height"))
    knee = _value(roof.get("knee_wall"))
    axis0 = _ridge_axis(rect, roof)
    turn = turn and axis0[5] != "ridge_lines"          # a drawn ridge line is never turned
    r, across, half_along, half_across, ridge_half, ridge_source = _turned(axis0) if turn else axis0
    fit = "pitch" if rtype in ("gable", "hip", "other", "shed") else None

    def first_pitch() -> float:
        if pitch is not None and fit == "pitch":
            notes.append(f"pitch {pitch:.2f} degrees: the roof follows the drawn section's heights")
            return float(pitch)
        if pitches:
            return pitches[0]
        if ridge is not None and eaves is not None and rtype in ("gable", "hip") and half_across > 0:
            p = math.degrees(math.atan2(ridge - eaves, half_across))
            notes.append(f"pitch {p:.2f} degrees from the eaves and ridge heights")
            return p
        p = DEFAULTS["shed_pitch_deg"] if rtype == "shed" else DEFAULTS["pitch_deg"]
        assumed.append({"field": "pitch", "value": p, "reason": "no pitch and no ridge height drawn"})
        return p

    if rtype == "flat":
        z = eaves if eaves is not None else ridge
        if z is None:
            top = floor_z + float(level["ceiling_height"]) if level else 0.0
            z = top + DEFAULTS["flat_thickness"]
            assumed.append({"field": "eaves_height", "value": round(z, 4),
                            "reason": "flat roof without a height: the top level's ceiling + an assumed "
                                      f"{DEFAULTS['flat_thickness']} m roof slab"})
        eq = [(0.0, 0.0, z)]
        planes = planes_from_equations(eq, outline, ["rp_flat"])
        return {"planes": planes, "equations": eq, "outline": outline, "eaves_z": z, "ridge_z": z, "pitches": [0.0],
                "assumed": assumed, "warnings": warnings, "notes": notes,
                "_ctx": {"fit": None, "rect": rect, "rtype": rtype, "why_fixed": "a flat roof has no pitch"}}

    p1 = first_pitch()
    t1 = math.tan(math.radians(p1))
    if eaves is None:
        if knee is not None:
            eaves = floor_z + knee - overhang * t1      # the eaves edge is `overhang` outside the wall face
            notes.append(f"eaves {eaves:.3f} m from the knee wall {knee:.2f} m at the outer wall face and the "
                         f"overhang {overhang:.2f} m")
            if overhang_assumed and not overhang_used:
                assumed.append({"field": "overhang", "value": overhang,
                                "reason": "not drawn: used to bring the knee wall to the eaves"})
        elif ridge is not None and rtype in ("gable", "hip"):
            eaves = ridge - half_across * t1
            notes.append(f"eaves {eaves:.3f} m from the ridge height and the pitch")
        else:
            knee_a = DEFAULTS["knee_wall"]
            eaves = floor_z + knee_a - overhang * t1
            assumed.append({"field": "eaves_height", "value": round(eaves, 4),
                            "reason": f"no eaves height, knee wall or ridge height drawn: an assumed knee wall of "
                                      f"{knee_a} m at the outer wall face"})

    eqs: list[Plane] = []
    tiers: list[str] = []
    if rtype in ("gable", "hip", "other"):
        if rtype == "other":
            assumed.append({"field": "type", "value": "gable",
                            "reason": "roof type 'other': built as a gable roof along the ridge"})
        ends = "hip" if rtype == "hip" else "gable"
        eqs, tiers, more = _rect_planes(rect["center"], r, across, half_along, half_across, eaves, t1, ends,
                                        ridge_half, "")
        notes += more
        if turn:
            from_ = "the section peak" if ridge_source == "profile" else "the long side"
            assumed.append({"field": "ridge_direction",
                            "value": "along the section cut" if ridge_source == "profile" else "along the short side",
                            "reason": f"no ridge line drawn ({from_} gave the other direction): turned so the drawn "
                                      f"pitch and the drawn section's heights meet (follow_section)"})
        elif ridge_source == "long axis" and rtype != "hip":
            assumed.append({"field": "ridge_direction", "value": "along the long side",
                            "reason": "no ridge line and no section peak drawn: the ridge along the long side of the "
                                      "outline"})
        elif ridge_source == "profile" and rtype != "hip":
            assumed.append({"field": "ridge_direction", "value": "across the section cut",
                            "reason": f"read from one section profile (cut along {roof['profile']['cut_axis']}): the "
                                      f"ridge runs across the cut"})
        top = eaves + half_across * t1
    elif rtype == "shed":
        lines = [ln for ln in roof.get("ridge_lines") or [] if isinstance(ln, (list, tuple)) and len(ln) == 2]
        cx, cy = rect["center"]
        if lines:
            mid = G.segment_midpoint(*max(lines, key=lambda ln: G.distance(ln[0], ln[1])))
            side = 1.0 if (mid[0] - cx) * across[0] + (mid[1] - cy) * across[1] >= 0 else -1.0
        else:
            side = 1.0
            assumed.append({"field": "shed_direction", "value": "high edge on the +across side",
                            "reason": "no ridge line drawn for the shed roof"})
        low = (cx - across[0] * half_across * side, cy - across[1] * half_across * side)
        eqs, tiers = [_ramp(low, (across[0] * side, across[1] * side), eaves, t1)], [""]
        top = eaves + 2.0 * half_across * t1
    elif rtype in ("mansard", "gambrel") and section_profile(roof, rect) is not None:
        # The drawn section gives the tiers along its cut (slopes, break and ridge heights, the ridge across the
        # cut at its peak: real02's party wall); the plan's break line is a cross-check (§1.6b row 13).
        prof = section_profile(roof, rect)
        fit = None                                   # the tiers are the section's own slopes and heights
        eaves_drawn = sum(z for _s, z in prof["eaves"]) / 2.0
        if any(abs(z - eaves) > 0.05 for _s, z in prof["eaves"]):
            warnings.append(f"eaves height {eaves:.3f} m vs the section's "
                            f"{', '.join(f'{z:.3f}' for _s, z in prof['eaves'])} m: the section is kept")
        eaves = eaves_drawn
        eqs, tiers, info = _profile_tiers(prof, outline, rtype, eaves, roof.get("break_line"))
        notes += info["notes"]
        top = prof["peak"][1]
        notes.append(f"tiers from the drawn section ({rtype}): lower "
                     f"{', '.join(f'{d:.1f}' for d in info['lower_deg'])} degrees, upper "
                     f"{', '.join(f'{d:.1f}' for d in info['upper_deg'])} degrees, break at z "
                     f"{', '.join(f'{z:.3f}' for _s, z in info['breaks'])} m, ridge {top:.3f} m across the cut at "
                     f"s {prof['peak'][0]:.3f} m")
        assumed.append({"field": "ridge_direction", "value": "across the section cut",
                        "reason": f"read from one section profile (cut along {roof['profile']['cut_axis']}): the ridge "
                                  f"runs across the cut through its highest point"})
        ends = info.get("ends") or {}
        if rtype == "mansard" and ends.get("source") == "break_line":
            assumed.append({"field": "mansard_ends", "value": {"lower_deg": ends["lower_deg"],
                                                               "upper_deg": ends["upper_deg"]},
                            "reason": f"the section does not cut the two other sides: their lower slopes rise from "
                                      f"the eaves to the plan's break line at the section's break height "
                                      f"{ends['break_z']:.3f} m, the upper slopes from there "
                                      + ("at the pitch that reaches the section's ridge height (its upper pitch "
                                         "would stay under it)" if ends["steepened"]
                                         else "at the section's upper pitch")
                                      + " (docs/milestone11.md §1.1 E7)"})
        elif rtype == "mansard":
            assumed.append({"field": "mansard_ends", "value": round(sum(info["lower_deg"]) / len(info["lower_deg"]), 2),
                            "reason": "the section does not cut the two other sides: their lower slopes take the "
                                      "section's lower pitch from the eaves height and, with no upper slope drawn "
                                      "there (and no closed break line on the plan), run up to the ridge"})
        for drawn, got, what in ((pitches[0] if pitches else None, info["lower_deg"], "lower"),
                                 (pitches[1] if len(pitches) > 1 else None, info["upper_deg"], "upper")):
            if drawn is not None and got and max(abs(g - drawn) for g in got) > 0.5:
                warnings.append(f"{what} pitch {drawn:.1f} degrees vs the section's "
                                f"{', '.join(f'{g:.1f}' for g in got)}: the section is kept")
        brk = geom2d.ccw(roof.get("break_line") or [])
        if len(brk) >= 3:
            proj = [x * prof["cut"][0] + y * prof["cut"][1] for x, y in brk]
            for (s_b, _z), s_d in zip(info["breaks"], (min(proj), max(proj))):
                if abs(s_b - s_d) > 0.05:
                    warnings.append(f"break line: the section breaks at s {s_b:.2f} m, the plan's break line at "
                                    f"{s_d:.2f} m ({(s_b - s_d) * 100:+.0f} cm): the section is kept")
        pitches = pitches or [info["lower_deg"][0], *info["upper_deg"][:1]]
    elif rtype in ("mansard", "gambrel"):
        brk = geom2d.ccw(roof.get("break_line") or [])
        fit = "upper_pitch"
        p2 = float(pitch) if pitch is not None else pitches[1] if len(pitches) > 1 else None
        if pitch is not None:
            notes.append(f"upper pitch {p2:.2f} degrees: the roof follows the drawn section's heights")
        if rtype == "gambrel" and ridge_source == "long axis" and not turn:
            assumed.append({"field": "ridge_direction", "value": "along the long side",
                            "reason": "no ridge line and no section peak drawn: the gambrel's ridge along the long "
                                      "side of the outline"})
        if len(brk) < 3:
            inset = min(half_across, half_along) * 0.3
            brk = geom2d.rectangle_corners(rect, -inset)
            assumed.append({"field": "break_line", "value": [[round(x, 4), round(y, 4)] for x, y in brk],
                            "reason": f"no break line drawn: the outline rectangle {inset:.2f} m in"})
        brect = geom2d.oriented_rectangle(brk)
        # Offsets of the break line from the outline, per side of the outline rectangle.
        offs = []
        cx, cy = rect["center"]
        for axis, half in ((r, half_along), (across, half_across)):
            proj = [(x - cx) * axis[0] + (y - cy) * axis[1] for x, y in brk]
            offs.append((half - max(proj), half + min(proj)))
        across_offs = offs[1]
        along_offs = offs[0]
        sides = list(across_offs) + ([] if rtype == "gambrel" else list(along_offs))
        mean_off = sum(sides) / len(sides)
        z_break = eaves + mean_off * t1
        lower: list[Plane] = []
        for (axis, half), (o_pos, o_neg) in zip(((r, half_along), (across, half_across)), (along_offs, across_offs)):
            if rtype == "gambrel" and axis is r:
                continue
            for sgn, off in ((1.0, o_pos), (-1.0, o_neg)):
                edge = (cx + axis[0] * half * sgn, cy + axis[1] * half * sgn)
                tan_i = (z_break - eaves) / off if off > 1e-6 else t1
                if abs(math.degrees(math.atan(tan_i)) - p1) > 0.5:
                    notes.append(f"lower slope {math.degrees(math.atan(tan_i)):.1f} degrees on one side: the break "
                                 f"line is {off:.2f} m in there (level break line at {z_break:.3f} m)")
                lower.append(_ramp(edge, (-axis[0] * sgn, -axis[1] * sgn), eaves, tan_i))
        # Upper tier over the break line: across the ridge at p2 (else from the ridge height, else assumed).
        b_axis = _ridge_axis(brect, roof)
        b_r, b_across, b_half_along, b_half_across, b_ridge_half, _ = _turned(b_axis) if turn else b_axis
        if turn:
            assumed.append({"field": "ridge_direction", "value": "turned 90 degrees",
                            "reason": "no ridge line drawn: turned so the drawn pitches and the drawn section's "
                                      "heights meet (follow_section)"})
        if p2 is None:
            if ridge is not None and b_half_across > 0:
                p2 = math.degrees(math.atan2(max(0.0, ridge - z_break), b_half_across))
                notes.append(f"upper pitch {p2:.2f} degrees from the ridge height")
            else:
                p2 = 15.0
                assumed.append({"field": "upper_pitch", "value": p2, "reason": "no second pitch and no ridge "
                                                                             "height drawn"})
        t2 = math.tan(math.radians(p2))
        upper, _names, more = _rect_planes(brect["center"], b_r, b_across, b_half_along, b_half_across, z_break, t2,
                                           "gable" if rtype == "gambrel" else "hip", b_ridge_half, "")
        notes += more
        eqs = lower + upper
        tiers = ["lower"] * len(lower) + ["upper"] * len(upper)
        top = z_break + b_half_across * t2
        notes.append(f"break line at z {z_break:.3f} m")
    else:
        return {"planes": [], "equations": [], "outline": outline, "eaves_z": eaves, "ridge_z": ridge, "pitches": pitches,
                "assumed": assumed, "warnings": [f"unknown roof type {rtype!r}: no roof"], "notes": notes,
                "_ctx": {"fit": None}}

    planes = planes_from_equations(eqs, outline, _named(eqs, tiers))
    # 26 Oct 2026 (real06): the ridge is the highest point of the planes as built. ``eaves + half_across x tan`` is that
    # only when the ridge runs along the long side; a hip whose axis came from the section's peak reported 8.53 m for
    # a roof built 7.61 m high (its four equal slopes meet over the short half-width whatever the axis).
    top = max((plane_z(eq, x, y) for eq, poly in zip(eqs, _region_polygons(eqs, outline)) for x, y in poly),
              default=top)
    if pitch is not None and fit == "pitch":
        pitches = [float(pitch)] + pitches[1:]
    elif pitch is not None and fit == "upper_pitch":
        pitches = (pitches[:1] or [p1]) + [float(pitch)] + pitches[2:]
    return {"planes": planes, "equations": eqs, "outline": outline, "eaves_z": eaves, "ridge_z": top,
            "pitches": pitches or [p1], "assumed": assumed, "warnings": warnings, "notes": notes,
            "_ctx": {"fit": fit, "rect": rect, "rtype": rtype, "ridge_source": axis0[5], "turned": turn,
                     "pitch": p2 if fit == "upper_pitch" else p1 if fit == "pitch" else None,
                     "why_fixed": None if fit else
                     "the mansard / gambrel tiers are the section's own slopes and heights"}}


def _pitch_for_ridge(roof: dict, building: dict, target: float, turn: bool) -> tuple[Optional[dict], Optional[str]]:
    """The derivation whose ridge meets ``target`` by its pitch (pure; bisection: the ridge rises or falls steadily
    with the pitch while the eaves stay). ``(derivation, None)`` or ``(None, why not)`` when no pitch in
    ``SECTION_PITCH_DEG`` reaches it."""
    lo, hi = SECTION_PITCH_DEG
    d_lo, d_hi = _derive(roof, building, pitch=lo, turn=turn), _derive(roof, building, pitch=hi, turn=turn)
    f_lo, f_hi = d_lo["ridge_z"] - target, d_hi["ridge_z"] - target
    if abs(f_hi - f_lo) < 1e-6:
        return None, "the ridge does not move with the pitch (the eaves are taken from the drawn ridge height)"
    if f_lo * f_hi > 0:
        return None, (f"no pitch from {lo:g} to {hi:g} degrees reaches the drawn ridge {target:.3f} m (the ridge would "
                      f"run from {d_lo['ridge_z']:.3f} to {d_hi['ridge_z']:.3f} m)")
    best = d_lo if abs(f_lo) <= abs(f_hi) else d_hi
    for _ in range(40):
        mid = (lo + hi) / 2.0
        d = _derive(roof, building, pitch=mid, turn=turn)
        f = d["ridge_z"] - target
        if abs(f) < abs(best["ridge_z"] - target):
            best = d
        if abs(f) < 1e-4:
            break
        if (f > 0) == (f_hi > 0):
            hi, f_hi = mid, f
        else:
            lo = mid
    return best, None


def _section_evidence(roof: dict) -> list[dict]:
    """Where the drawn section's heights come from: the profile's region and the ridge height's evidence."""
    out = []
    prof = roof.get("profile") if isinstance(roof.get("profile"), dict) else {}
    if prof.get("region_id"):
        out.append({"region_id": prof["region_id"], "rule": "section_profile", "cut_axis": prof.get("cut_axis"),
                    "points": len(prof.get("points") or []), "method": prof.get("method") or "vector"})
    ridge = roof.get("ridge_height")
    for e in (ridge.get("evidence") or [])[:3] if isinstance(ridge, dict) else []:
        out.append({k: e.get(k) for k in ("file", "region_id", "entity", "rule", "method") if e.get(k) is not None})
    return out


def follow_section(roof: dict, building: dict, base: dict) -> dict:
    """The derived roof made to follow its drawn section (pure; 26 Oct 2026, Argus on real06; CLAUDE.md evidence rules:
    a drawn section is source geometry, it outranks a pitch text, a default and a ridge direction no line draws).

    Targets: the drawn ridge height (``ridge_height`` read from a drawing: vector, OCR or a dimension, from a section or
    an elevation), else the peak of a reliable section profile; and the profile's points when ``section_reliability``
    says the profile runs one-to-one with the plan as one roof surface. When the built roof (``ridge_z``: the highest
    point of its planes; the profile's silhouette, ``profile_diffs``) differs from a target by more than
    ``SECTION_TOL``, the roof follows the section, trying in this order and taking the first that brings every target
    within ``SECTION_TOL`` without making the profile fit worse: (1) the ridge turned when no ridge line draws its
    direction (every drawn value kept), (2) the pitch that meets the drawn ridge (``_pitch_for_ridge``; the upper pitch
    of a mansard or gambrel without section tiers), (3) both. Else the candidate closest to the section (it must meet
    the ridge, not worsen the profile and be better than the derived roof); else the derived roof is kept and the log
    says why (no pitch in ``SECTION_PITCH_DEG`` reaches the ridge, the tiers already are the section's, a flat roof). The
    eaves height and the outline never change: the roof still closes over every wall and the knee walls follow from
    the same eaves line. Every difference over ``SECTION_LIST_TOL`` stays listed; the record is ``section_fit``:
    ``{"status": within_tolerance | followed | followed_closest | kept_derived | not_compared, "follows_section",
    "region_id", "tolerance_m", "derived", "drawn", "used", "change", "misfit_m", "points_compared", "reasons",
    "evidence"}``."""
    ctx = base.pop("_ctx", None) or {}
    out = dict(base, section_fit=None, follows_section=False)
    if not base.get("planes") or not ctx.get("rect"):
        return out
    prof_raw = roof.get("profile") if isinstance(roof.get("profile"), dict) else {}
    axis = prof_raw.get("cut_axis")
    rid = prof_raw.get("region_id")
    if rid is None and isinstance(roof.get("ridge_height"), dict):
        rid = next((e["region_id"] for e in roof["ridge_height"].get("evidence") or []
                    if isinstance(e, dict) and e.get("region_id")), None)
    where = f"the drawn section {rid}" if rid else "the drawn section"
    prof = section_profile(roof, ctx["rect"])
    points_ok, reasons = section_reliability(prof, base["outline"], axis) if prof is not None else (False, [])
    ridge_drawn = _value(roof.get("ridge_height")) if _drawn(roof.get("ridge_height")) else None
    target = ridge_drawn if ridge_drawn is not None else prof["peak"][1] if prof is not None and points_ok else None
    if target is None and not points_ok:
        if prof is not None:
            out["section_fit"] = {"status": "not_compared", "follows_section": False, "region_id": rid,
                                  "tolerance_m": SECTION_TOL, "points_compared": False, "reasons": reasons,
                                  "evidence": _section_evidence(roof)}
            out["warnings"] = list(base["warnings"]) + [f"{where} is not checked against the roof: "
                                                        f"{'; '.join(reasons)}; it draws no ridge height either"]
        return out

    def misfit(d: dict) -> tuple[float, float, list]:
        diffs = profile_diffs(d["equations"], prof, d["outline"]) if points_ok else []
        return abs(d["ridge_z"] - target), max((abs(b - z) for _s, b, z in diffs), default=0.0), diffs

    def summary(d: dict, c: dict) -> dict:
        return {"ridge_z": round(d["ridge_z"], 4),
                "pitch_deg": None if c.get("pitch") is None else round(c["pitch"], 3),
                "ridge_turned": bool(c.get("turned"))}

    r0, p0, _ = misfit(base)
    chosen, chosen_ctx, change, why = base, ctx, None, None
    if r0 <= SECTION_TOL and p0 <= SECTION_TOL:
        status = "within_tolerance"
    elif ctx.get("fit") is None:
        status, why = "kept_derived", ctx.get("why_fixed") or "the roof type has no pitch to follow the section with"
    else:
        tried, why_not = [], []
        if ctx.get("ridge_source") != "ridge_lines":
            tried.append(("ridge_direction", _derive(roof, building, turn=True)))
        for turn, name in ((False, "pitch"), (True, "pitch+ridge_direction")):
            if turn and ctx.get("ridge_source") == "ridge_lines":
                continue
            d, no = _pitch_for_ridge(roof, building, target, turn)
            if d is None:
                why_not.append(f"with the ridge turned: {no}" if turn else no)
            else:
                tried.append((name, d))
        scored = [(name, d, *misfit(d)[:2]) for name, d in tried]
        ok = [s for s in scored if s[2] <= SECTION_TOL and s[3] <= SECTION_TOL]
        closest = sorted((s for s in scored if s[2] <= SECTION_TOL and s[3] <= p0 + 1e-6
                          and max(s[2], s[3]) < max(r0, p0) - 1e-6), key=lambda s: max(s[2], s[3]))
        pick = ok[0] if ok else closest[0] if closest else None
        if pick is None:
            status = "kept_derived"
            why = "; ".join(why_not) or (f"no ridge direction or pitch brings the roof within {SECTION_TOL:.2f} m of "
                                         f"the section without making its fit worse")
        else:
            change, chosen = pick[0], pick[1]
            chosen_ctx = chosen.pop("_ctx", None) or {}
            status = "followed" if ok else "followed_closest"
    r1, p1, diffs = misfit(chosen)
    warnings = list(chosen["warnings"])
    if prof is not None and not points_ok:
        warnings.append(f"{where} is not checked point by point against the roof: "
                        f"{'; '.join(reasons)}; only its ridge height {target:.3f} m is followed")
    warnings += [f"roof vs the drawn section at s {s:.2f} m: {b:.3f} m built, {z:.3f} m drawn "
                 f"({(b - z) * 100:+.0f} cm)" for s, b, z in diffs if abs(b - z) > SECTION_LIST_TOL]
    if change is not None:
        what = []
        if "pitch" in change:
            word = "upper pitch" if chosen_ctx.get("fit") == "upper_pitch" else "pitch"
            what.append(f"{word} {ctx['pitch']:.1f} -> {chosen_ctx['pitch']:.1f} degrees")
        if "ridge_direction" in change:
            what.append("the ridge turned 90 degrees (no ridge line drawn)")
        rest = "" if status == "followed" else f"; the section's shape still differs by up to {p1:.2f} m"
        warnings.append(f"roof adjusted to follow {where}: {', '.join(what)}; ridge {chosen['ridge_z']:.3f} m (drawn "
                        f"{target:.3f} m; derived {base['ridge_z']:.3f} m, {(base['ridge_z'] - target) * 100:+.0f} cm)"
                        + rest)
    if abs(chosen["ridge_z"] - target) > SECTION_LIST_TOL:
        d_cm = (chosen["ridge_z"] - target) * 100
        kept = "" if change and "pitch" in change else ", the pitches are kept"
        tail = (f"within the {SECTION_TOL:.2f} m tolerance{kept}" if r1 <= SECTION_TOL
                else f"the pitches are kept: {why}")
        warnings.append(f"roof ridge {chosen['ridge_z']:.3f} m built vs the drawn ridge height {target:.3f} m "
                        f"({d_cm:+.0f} cm): {tail}")
    fit = {"status": status, "follows_section": status in ("within_tolerance", "followed"), "region_id": rid,
           "tolerance_m": SECTION_TOL,
           "derived": summary(base, ctx),
           "drawn": {"ridge_z": round(target, 4),
                     "ridge_source": "ridge_height" if ridge_drawn is not None else "profile peak",
                     "eaves_z": _value(roof.get("eaves_height")),
                     "profile_points": len(profile_points(prof)) if prof is not None else 0},
           "used": summary(chosen, chosen_ctx), "change": change,
           "misfit_m": {"before": round(max(r0, p0), 4), "after": round(max(r1, p1), 4)},
           "points_compared": bool(points_ok), "reasons": ([why] if why else []) + ([] if points_ok else reasons),
           "evidence": _section_evidence(roof)}
    out = dict(chosen, warnings=warnings, section_fit=fit, follows_section=fit["follows_section"])
    out.pop("_ctx", None)
    if change is not None:
        out["notes"] = list(chosen["notes"]) + [f"adjusted to follow {where} ({change}): see section_fit"]
    return out


def planes_for(roof: dict, building: dict) -> list:
    """The roof planes derived from the roof's type, outline, heights, pitches, ridge lines and break line
    (pure; docs/milestone10.md §1.6a): ``[{"id", "points": [[x, y, z], ...], "slope_deg", "aspect_deg",
    "source": "derived"}]`` on the outer roof surface, counter-clockwise seen from above. Used when the
    pipeline leaves ``roof.planes`` empty; ``derive`` gives the assumptions behind them."""
    return derive(roof, building)["planes"]


# --------------------------------------------------------------------------
# The model the scene builds
# --------------------------------------------------------------------------

def is_convex(planes: Sequence[dict], tol: float = CONVEX_TOL) -> bool:
    """True when every plane is the lowest one at its own corners (the roof surface is the lowest plane
    everywhere: what the mesh, wall and ceiling helpers need)."""
    eqs = [plane_from_points(p["points"]) for p in planes]
    if any(e is None for e in eqs):
        return False
    for i, p in enumerate(planes):
        for x, y, *_ in p["points"]:
            zi = plane_z(eqs[i], x, y)
            if any(plane_z(e, x, y) < zi - tol for j, e in enumerate(eqs) if j != i):
                return False
    return True


def roof_model(roof: Optional[dict], building: dict) -> Optional[dict]:
    """What the scene builds for ``building.roof`` (None without a roof).

    ``{"type", "over_level_id", "planes", "planes_source": "building" | "derived", "equations", "outline",
    "openings": [{"id", "kind", "room_id", "polygon", "parapet_height", "parapet_source"}], "thickness",
    "eaves_z", "ridge_z", "convex", "covering", "assumed": [{"field", "value", "reason"}], "warnings", "notes",
    "derived_check"}``. Drawn planes are used as they are and compared with the derivation (a difference is a
    note, not a change); the roof's own ``assumed`` list is carried over."""
    if not isinstance(roof, dict):
        return None
    der = derive(roof, building)
    level = over_level(roof, building)
    drawn = [p for p in roof.get("planes") or [] if isinstance(p, dict) and len(p.get("points") or []) >= 3]
    assumed = [{"field": "roof", "value": a, "reason": "listed as assumed in the building JSON"}
               for a in roof.get("assumed") or []]
    notes = list(der["notes"])
    if drawn:
        planes, source = drawn, "building"
        same, why = equivalent_planes(drawn, der["planes"]) if der["planes"] else (False, "nothing derived")
        check = {"equivalent": same, "why": why}
        outline = geom2d.ccw(roof.get("outline") or []) or geom2d.convex_hull(
            [(p[0], p[1]) for pl in drawn for p in pl["points"]])
        eaves = _value(roof.get("eaves_height"))
        if eaves is None:
            eaves = min(float(p[2]) for pl in drawn for p in pl["points"])
        ridge = max(float(p[2]) for pl in drawn for p in pl["points"])
    else:
        planes, source = der["planes"], "derived"
        check = None
        outline, eaves, ridge = der["outline"], der["eaves_z"], der["ridge_z"]
        assumed += der["assumed"]
    eqs = [plane_from_points(p["points"]) for p in planes]
    eqs = [e for e in eqs if e is not None]
    thickness = _value(roof.get("thickness"))
    if thickness is None or thickness <= 0:
        thickness = DEFAULTS["thickness"]
        assumed.append({"field": "thickness", "value": thickness, "reason": "roof thickness not drawn"})
    elif _is_assumed(roof.get("thickness")):
        assumed.append({"field": "thickness", "value": thickness,
                        "reason": (roof.get("thickness") or {}).get("note") or "assumed in the building JSON"})
    openings = []
    for o in roof.get("openings") or []:
        poly = geom2d.ccw(o.get("polygon") or [])
        if len(poly) < 3:
            continue
        ph = o.get("parapet_height")
        height = _value(ph)
        psource = "drawn" if height is not None and not _is_assumed(ph) else "assumed"
        if height is None:
            height = DEFAULTS["parapet"]
        guard = None
        knee = (float(eaves) - float(level["elevation"])) if level is not None and eaves is not None else None
        if psource == "assumed" and roof.get("type") not in ("flat", None) and knee is not None \
                and DEFAULTS["terrace_parapet_min"] <= knee < height - 0.05:
            # 24 Oct 2026 (real04): a 1.0 m parapet rose 0.4 m over the eaves and the terrace ends read as white boxes
            # stuck on the roof; the wall stops at the eaves line and a railing makes the guard height
            guard, height = height, round(knee, 3)
        if psource == "assumed":
            assumed.append({"field": f"parapet_height:{o.get('id')}", "value": height,
                            "reason": ((ph or {}).get("note") if isinstance(ph, dict) and ph.get("note")
                                       else "parapet height not drawn")
                            + (f"; the wall stops at the eaves line ({height:.2f} m over the terrace floor) and a "
                               f"railing reaches the {guard:.2f} m guard height" if guard else "")})
        openings.append({"id": o.get("id"), "kind": o.get("kind") or "other", "room_id": o.get("room_id"),
                         "polygon": poly, "parapet_height": height, "parapet_source": psource,
                         "parapet_wall_ids": list(o.get("parapet_wall_ids") or []), "guard_height": guard})
    convex = is_convex(planes)
    warnings = list(der["warnings"])
    if not convex:
        warnings.append("the roof planes are not convex (a valley or a raised part): walls keep their level "
                        "height and attic ceilings stay flat under this roof")
    model = {"type": roof.get("type"), "over_level_id": level["id"] if level else None, "planes": planes,
             "planes_source": source, "equations": eqs, "outline": outline, "openings": openings,
             "thickness": thickness, "eaves_z": eaves, "ridge_z": ridge, "convex": convex,
             "covering": roof.get("covering"), "covering_colour": roof.get("covering_colour"),
             "covering_source": roof.get("covering_source"), "assumed": assumed, "warnings": warnings,
             "notes": notes, "derived_check": check, "profile": roof.get("profile"),
             "kind": roof.get("kind"), "parapet": 0.0,
             # 26 Oct 2026: how the derived roof follows its drawn section (follow_section; drawn planes stay as drawn)
             "section_fit": der.get("section_fit") if source == "derived" else None,
             "follows_section": bool(der.get("follows_section")) if source == "derived" else False}
    if roof.get("kind") == "flat_cut":
        # Milestone 12 (docs/milestone12.md §3.4, U2): a single drawn ground floor ends with a flat roof slab and a
        # low parapet on its outer walls (inferred, "upper floors not drawn").
        ph = _value(roof.get("parapet_height"))
        model["parapet"] = DEFAULTS["flat_cut_parapet"] if ph is None else max(0.0, ph)
        assumed.append({"field": "flat_cut", "value": model["parapet"],
                        "reason": roof.get("note") or "upper floors not drawn: a flat roof slab with a parapet"})
    model["knee_wall_check"] = knee_wall_check(model, roof, building)
    if model["knee_wall_check"] and abs(model["knee_wall_check"]["difference"]) > 0.05:
        warnings.append(f"knee wall {model['knee_wall_check']['drawn']:.2f} m drawn, "
                        f"{model['knee_wall_check']['derived']:.2f} m from the roof planes at the outer wall face: "
                        f"the planes are kept")
    return model


def knee_wall_check(model: dict, roof: dict, building: dict) -> Optional[dict]:
    """The knee wall cross-check (§1.6b row 13): the roof's top surface at the outer face of the outer walls
    of the level under it, minus its floor, the lowest along those faces (sampled at the wall midpoints),
    against the drawn ``knee_wall``. None without a drawn knee wall or planes."""
    drawn = _value(roof.get("knee_wall"))
    level = over_level(roof, building)
    if drawn is None or level is None or not model["equations"] or not model["convex"]:
        return None
    walls = [w for w in building.get("walls") or [] if w.get("level_id") == level["id"] and w.get("exterior")]
    outline, _ = geom2d.wall_outline([w for w in building.get("walls") or [] if w.get("level_id") == level["id"]])
    heights = []
    for w in walls:
        mid = G.segment_midpoint(w["start"], w["end"])
        nx, ny = G.unit_normal_left(w["start"], w["end"])
        half = float(w["thickness"]) / 2.0
        for s in (1.0, -1.0):
            p = (mid[0] + s * nx * half, mid[1] + s * ny * half)
            q = (mid[0] + s * nx * (half + 0.05), mid[1] + s * ny * (half + 0.05))
            if outline and not G.point_in_polygon(q, outline):
                heights.append(surface_z(model["equations"], *p) - float(level["elevation"]))
    if not heights:
        return None
    derived = min(heights)
    return {"drawn": drawn, "derived": round(derived, 4), "difference": round(derived - drawn, 4)}


TERRACE_MODES = ("auto", "cut", "closed")


def terrace_decisions(roof: dict, building: dict, mode: str = "auto") -> tuple[dict, list[dict], list[str]]:
    """Which roof terraces are cut into the roof (pure; docs/milestone11.md §1.1 E6, decision D5, brief
    ``roof_terraces``): ``cut`` keeps every terrace opening, ``closed`` drops them (the roof runs over the terrace
    rooms; their outer walls become knee walls), ``auto`` cuts a terrace when the plan of its level draws it as a
    room with a door to it (``cameras.room_openings``: a door on the room's edge), else keeps the roof closed.
    The section is vector geometry and the terrace a label (trust order): when the roof has a drawn section
    (``profile``) that runs over the terrace, the conflict is listed either way. Returns ``(roof, decisions,
    warnings)``: a copy of the roof with the kept openings, ``[{"opening_id", "room_id", "decision": cut |
    closed, "reason", "doors", "conflict"}]`` and one warning per conflict."""
    from wenart.blender import cameras

    mode = mode if mode in TERRACE_MODES else "auto"
    rooms = {r["id"]: r for r in building.get("rooms") or []}
    kept, decisions, warnings = [], [], []
    prof = roof.get("profile") if isinstance(roof.get("profile"), dict) else None
    for o in roof.get("openings") or []:
        room = rooms.get(o.get("room_id"))
        doors = []
        if room is not None and len(room.get("polygon") or []) >= 3:
            doors = [x["id"] for x in cameras.room_openings(room, [tuple(p[:2]) for p in room["polygon"]], building)
                     if x.get("type") == "door"]
        if mode == "cut":
            cut, why = True, "brief roof_terraces: cut"
        elif mode == "closed":
            cut, why = False, "brief roof_terraces: closed"
        elif doors:
            cut, why = True, (f"brief roof_terraces: auto: the plan draws {o.get('room_id')} as a room with a door to "
                              f"it ({', '.join(doors)})")
        else:
            cut, why = False, (f"brief roof_terraces: auto: {o.get('room_id') or 'the terrace'} has no door on the "
                               f"plan: the roof stays closed")
        conflict = None
        if prof is not None:
            conflict = (f"roof terrace {o.get('id')} ({o.get('room_id')}): the plan labels a terrace, the section "
                        f"{prof.get('region_id') or ''} draws the roof closed over it; "
                        + ("cut into the roof" if cut else "the roof is kept closed") + f" ({why})")
            warnings.append(conflict)
        decisions.append({"opening_id": o.get("id"), "room_id": o.get("room_id"), "decision": "cut" if cut else "closed",
                          "reason": why, "doors": doors, "conflict": conflict})
        if cut:
            kept.append(o)
    out = dict(roof, openings=kept)
    return out, decisions, warnings


# The roof keys the agent may change (docs/milestone11.md §17.3 ``agent_overrides.exterior.roof``).
OVERRIDE_TYPES = ("flat", "gable", "hip", "mansard", "gambrel", "shed")


def override_of(building: dict) -> Optional[dict]:
    """The agent's roof override of a building (``agent_overrides.exterior.roof``, §17.3), None without one. Here
    (not only in ``overrides``) so the gate's import closure stays roof.py (wenart/run/stages.py GATE_CODE)."""
    ov = building.get("agent_overrides") if isinstance(building, dict) else None
    ext = ov.get("exterior") if isinstance(ov, dict) and isinstance(ov.get("exterior"), dict) else {}
    r = ext.get("roof")
    return r if isinstance(r, dict) and r else None


def apply_override(roof: Optional[dict], override: Optional[dict]) -> tuple[Optional[dict], list[dict]]:
    """The roof with the agent's ``exterior.roof`` override on top (pure; §17.3: ``{type, pitch_deg, overhang_m}``,
    every key optional): ``type`` replaces the type; ``pitch_deg`` the first pitch; ``overhang_m`` the overhang,
    and the roof outline is then grown from the walls (a drawn outline fixes the overhang). Each change is
    ``{"field", "value", "was", "reason"}`` (method ``ai`` on the value). No override: the roof unchanged. A key
    whose value the drawing gives (``_drawn``, ``_drawn_type``, ``_drawn_outline``) is refused: the roof lists it in
    ``override_refused`` (24 Oct 2026)."""
    if not isinstance(override, dict) or not override or roof is None:
        return roof, []
    out = dict(roof)
    changes = []
    note = "agent override (docs/milestone11.md §17.3)"
    # 24 Oct 2026 (real04: the agent's 45 degree, 0.8 m override replaced the drawn 32.5 / 11.3 degree mansard, its
    # outline and its 5.8 m ridge: the roof stood 1.35 m too high). CLAUDE.md evidence rules: the drawn geometry is
    # the anchor; an override of a drawn value is refused and listed (``override_refused``), the rest applies.
    refused = []
    override = dict(override)
    for key, drawn in (("type", _drawn_type(roof)), ("pitch_deg", _drawn((roof.get("pitches_deg") or [None])[0])),
                       ("overhang_m", _drawn(roof.get("overhang")) or _drawn_outline(roof))):
        if key in override and drawn and not (key == "type" and override[key] == roof.get("type")):
            refused.append({"field": key, "value": override.pop(key), "kept": drawn,
                            "reason": f"{note}: refused, the drawing gives {key} ({drawn}); the drawn geometry is "
                                      f"the anchor (CLAUDE.md evidence rules)"})
    if refused:
        out["override_refused"] = refused
    if override.get("type") in OVERRIDE_TYPES:
        changes.append({"field": "type", "value": override["type"], "was": roof.get("type"), "reason": note})
        out["type"], out["type_source"] = override["type"], "agent"
    if isinstance(override.get("pitch_deg"), (int, float)) and not isinstance(override.get("pitch_deg"), bool):
        p = float(override["pitch_deg"])
        old = [dict(x) if isinstance(x, dict) else x for x in roof.get("pitches_deg") or []]
        new = {"value": p, "method": "ai", "confidence": 1.0, "evidence": [], "note": note}
        out["pitches_deg"] = [new] + old[1:]
        changes.append({"field": "pitch_deg", "value": p, "was": _value(old[0]) if old else None, "reason": note})
        if out.get("profile"):        # the section's own pitch would win over the plan's pitch: the agent's wins
            out["profile"] = None
            changes.append({"field": "profile", "value": None, "was": "section profile",
                            "reason": note + ": the agent's pitch replaces the section's tiers"})
        out["ridge_height"] = None
    if isinstance(override.get("overhang_m"), (int, float)) and not isinstance(override.get("overhang_m"), bool):
        h = float(override["overhang_m"])
        changes.append({"field": "overhang_m", "value": h, "was": _value(roof.get("overhang")), "reason": note})
        out["overhang"] = {"value": h, "method": "ai", "confidence": 1.0, "evidence": [], "note": note}
        out["outline"] = None
        out["openings"] = [dict(o) for o in roof.get("openings") or []]
    return out, changes


DRAWN_METHODS = ("vector", "ocr", "dimension")


def _drawn(entry) -> Optional[str]:
    """``"<method> <value>"`` when a roof value is drawn (method vector / ocr / dimension, confidence 0.9 or more),
    else None."""
    if isinstance(entry, dict) and entry.get("method") in DRAWN_METHODS and entry.get("value") is not None \
            and float(entry.get("confidence") or 0.0) >= 0.9:
        return f"{entry['method']} {entry['value']}"
    return None


def _drawn_type(roof: dict) -> Optional[str]:
    """The roof type when the drawing gives it (``type_source`` a drawing rule, not assumed / agent / default)."""
    src = str(roof.get("type_source") or "")
    if roof.get("type") in (None, "other") or src in ("", "assumed", "agent", "default", "inferred", "brief"):
        return None
    return f"{src} {roof['type']}"


def _drawn_outline(roof: dict) -> Optional[str]:
    if len(roof.get("outline") or []) >= 3 and any(isinstance(e, dict) and e.get("rule") == "roof_outline"
                                                   for e in roof.get("evidence") or []):
        return "drawn roof outline"
    return None


OPENING_ROOF_GAP = 0.05          # an opening with an assumed height stops this far under the roof underside
MIN_OPENING_HEIGHT = {"window": 0.4, "door": 1.6}


def clip_openings_to_roof(building: dict, level: dict, model: Optional[dict]) -> list[dict]:
    """E8 (docs/milestone11.md §1.1): the doors and windows of the level under the roof whose height is not drawn
    (assumed: ``null`` or listed in the opening's ``assumed``) and whose top would reach over the roof underside
    at their wall are clipped ``OPENING_ROOF_GAP`` under it (pure). The underside is sampled at both ends of the
    opening on both wall faces (the lowest counts). A window whose clipped height is under
    ``MIN_OPENING_HEIGHT`` also lowers an assumed sill. Returns ``[{"opening_id", "height", "sill_height",
    "was", "underside_z", "reason", "fits"}]``; ``apply_clips`` writes them into a building copy. A drawn
    height is never changed (``build.openings_through_roof`` warns about it)."""
    from wenart.blender import shell

    cut = wall_cut(model) if model else None
    if not cut or level is None or model.get("over_level_id") != level["id"]:
        return []
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level["id"]}
    out = []
    floor_z = float(level["elevation"])
    for o in building.get("openings") or []:
        wall = walls.get(o.get("wall_id"))
        if o.get("level_id") != level["id"] or wall is None or o.get("type") not in ("door", "window"):
            continue
        listed = o.get("assumed") or ()
        height_assumed = o.get("height") is None or "height" in listed
        if not height_assumed:
            continue
        bottom, top, _ = shell.opening_vertical(o, level, False)
        cx, cy, _ = shell.opening_centre_on_wall(o, wall)
        ux, uy = _unit(wall)
        nx, ny = -uy, ux
        half_w, half_t = float(o["width"]) / 2.0, float(wall["thickness"]) / 2.0
        under = min(surface_z(cut["planes"], cx + ux * a + nx * b, cy + uy * a + ny * b)
                    for a in (-half_w, half_w) for b in (-half_t, half_t))
        limit = under - OPENING_ROOF_GAP
        if top <= limit + 1e-6:
            continue
        sill = bottom - floor_z
        height = limit - bottom
        sill_assumed = o["type"] == "window" and (o.get("sill_height") is None or "sill_height" in listed)
        minimum = MIN_OPENING_HEIGHT[o["type"]]
        if height < minimum and sill_assumed:
            sill = max(0.0, limit - floor_z - minimum)
            height = limit - floor_z - sill
        fits = height >= minimum - 1e-6
        reason = (f"{o['type']} height not drawn: its top {top - floor_z:.2f} m above the floor would reach over the "
                  f"roof underside ({under - floor_z:.2f} m) at its wall; clipped {OPENING_ROOF_GAP:.2f} m under it "
                  f"(docs/milestone11.md §1.1 E8)" + ("" if fits else "; still lower than a usable "
                                                        f"{o['type']} (needs a dormer: review)"))
        out.append({"opening_id": o["id"], "height": round(max(height, 0.05), 4), "sill_height": round(sill, 4),
                    "was": {"height": round(top - bottom, 4), "sill_height": round(bottom - floor_z, 4)},
                    "underside_z": round(under, 4), "reason": reason, "fits": fits})
    return out


def opening_head_limit(model: Optional[dict], level: Optional[dict], wall: dict, opening: dict) -> Optional[float]:
    """How high over the floor an opening's head may reach under the roof at its wall (the lowest roof underside at
    its two ends on both wall faces, ``OPENING_ROOF_GAP`` under it, as ``clip_openings_to_roof`` clips); None when
    the roof is not over this level (pure). The architect's answers size windows with it (25 Oct 2026)."""
    from wenart.blender import shell

    cut = wall_cut(model) if model else None
    if not cut or level is None or model.get("over_level_id") != level["id"]:
        return None
    cx, cy, _ = shell.opening_centre_on_wall(opening, wall)
    ux, uy = _unit(wall)
    nx, ny = -uy, ux
    half_w, half_t = float(opening["width"]) / 2.0, float(wall.get("thickness") or 0.2) / 2.0
    under = min(surface_z(cut["planes"], cx + ux * a + nx * b, cy + uy * a + ny * b)
                for a in (-half_w, half_w) for b in (-half_t, half_t))
    return under - OPENING_ROOF_GAP - float(level["elevation"])


def _unit(wall: dict) -> tuple[float, float]:
    (x0, y0), (x1, y1) = wall["start"][:2], wall["end"][:2]
    n = math.hypot(x1 - x0, y1 - y0) or 1.0
    return (x1 - x0) / n, (y1 - y0) / n


def apply_clips(building: dict, clips: Sequence[dict]) -> dict:
    """A copy of ``building`` with the clipped openings of ``clip_openings_to_roof`` (height, and a lowered sill,
    both listed in the opening's ``assumed``)."""
    if not clips:
        return building
    by_id = {c["opening_id"]: c for c in clips}
    openings = []
    for o in building.get("openings") or []:
        c = by_id.get(o.get("id"))
        if c is None:
            openings.append(o)
            continue
        listed = list(o.get("assumed") or [])
        new = dict(o, height=c["height"], clipped_by_roof=c["reason"])
        if "height" not in listed:
            listed.append("height")
        if o.get("type") == "window" and abs(c["sill_height"] - c["was"]["sill_height"]) > 1e-6:
            new["sill_height"] = c["sill_height"]
            if "sill_height" not in listed:
                listed.append("sill_height")
        new["assumed"] = listed
        openings.append(new)
    return dict(building, openings=openings)


def flat_roof(building: dict) -> dict:
    """The roof of a building whose pipeline found no roof (``roof: null``, §1.6b row 13): a flat roof over
    the top level on its walls' outline, its height and thickness assumed (``derive``)."""
    levels = building.get("levels") or []
    top = max(levels, key=lambda lv: float(lv.get("elevation") or 0.0)) if levels else None
    return {"type": "flat", "type_source": "assumed", "over_level_id": top["id"] if top else None, "outline": None,
            "planes": [], "openings": [], "evidence": [],
            "assumed": ["no roof evidence: a flat roof over the top level (height, outline and thickness assumed)"]}


def underside(model: dict) -> list[Plane]:
    """The roof underside planes (each plane lowered by the roof thickness, square to it)."""
    return [lowered(e, model["thickness"]) for e in model["equations"]]


def ceiling_planes(model: dict, level: dict) -> list[Plane]:
    """The ceiling of the rooms under the roof: the underside ``CEILING_GAP`` lower, and the level's flat
    ceiling (``elevation + ceiling_height``, where the section shows a flat part; an attic whose ceiling
    height reaches the roof keeps the sloped faces only)."""
    flat = float(level["elevation"]) + float(level["ceiling_height"])
    return [(a, b, c - CEILING_GAP) for a, b, c in underside(model)] + [(0.0, 0.0, flat)]


def in_opening(model: dict, x: float, y: float) -> bool:
    return any(G.point_in_polygon((x, y), o["polygon"]) for o in model.get("openings") or [])


def covers(model: dict, x: float, y: float) -> bool:
    """True when the roof is over ``(x, y)``: inside the outline and in no roof opening."""
    return G.point_in_polygon((x, y), model["outline"]) and not in_opening(model, x, y)


# --------------------------------------------------------------------------
# Meshes (pure)
# --------------------------------------------------------------------------

# The plane-surface helpers live in geom2d (shell.py uses them for slabs, sloped ceilings and knee walls).
surface_pieces = geom2d.surface_pieces
lift = geom2d.lift
edge_breaks = geom2d.edge_breaks
side_faces = geom2d.side_faces
_mesh = geom2d.mesh_from_faces
clip_solid_below = geom2d.clip_solid_below

SLOT_COVERING, SLOT_SOFFIT, SLOT_FASCIA = 0, 1, 2


def roof_solid(model: dict) -> tuple[list, list, list[int]]:
    """``(verts, faces, slots)`` of the roof: the covering on top (slot 0), the soffit under it (slot 1)
    and the edges (slot 2: eaves fascia and the sides of the roof terraces cut into it)."""
    top = list(model["equations"])
    bottom = underside(model)
    holes = [o["polygon"] for o in model.get("openings") or []]
    outer = geom2d.ccw(model["outline"])
    faces = [(lift(poly, top[i], True), SLOT_COVERING) for i, poly in surface_pieces(outer, holes, top)]
    faces += [(lift(poly, bottom[i], False), SLOT_SOFFIT) for i, poly in surface_pieces(outer, holes, bottom)]
    # Terrace openings reach over the eaves (§1.6b row 13): only the edges of what is left get a fascia.
    for p, q in geom2d.region_boundary(outer, holes):
        faces += [(f, SLOT_FASCIA) for f in geom2d.segment_side_faces(p, q, top, bottom)]
    for verts, idx in parapet_ring(model):           # Milestone 12: flat_cut
        faces += [([verts[i] for i in f], SLOT_FASCIA) for f in idx]
    return _mesh(faces)


RIDGE_CAP = {"radius": 0.13, "segments": 8, "sink": 0.04, "min_length": 0.4, "break_cos": 0.7}


def ridge_lines(model: dict) -> list[tuple[tuple, tuple]]:
    """The ridges and hips of a pitched roof (pure; 24 Oct 2026): the 3D edges two roof planes share on the covering
    (``surface_pieces`` of the top equations; the outer surface is the lowest plane, so every shared edge is a
    ridge, a hip or a break line) but the break lines (both planes falling the same way, ``break_cos``). [] for a
    flat roof."""
    if model.get("type") in ("flat", None) or model.get("kind") == "flat_cut" or not model.get("equations"):
        return []
    top = list(model["equations"])
    holes = [o["polygon"] for o in model.get("openings") or []]
    pieces = geom2d.surface_pieces(geom2d.ccw(model["outline"]), holes, top)

    segs = []                                            # (plane, a, b) of every piece edge
    for i, poly in pieces:
        n = len(poly)
        for k in range(n):
            a, b = poly[k], poly[(k + 1) % n]
            if G.distance(a, b) >= 1e-6:
                segs.append((i, (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))))
    tol = 1e-3
    found: dict = {}
    for x in range(len(segs)):
        i, a, b = segs[x]
        length = G.distance(a, b)
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        for y in range(x + 1, len(segs)):
            j, c, d = segs[y]
            if j == i:
                continue
            # collinear: c and d on the line through a, b; then the overlap of the two along it
            if abs((c[0] - a[0]) * uy - (c[1] - a[1]) * ux) > tol or abs((d[0] - a[0]) * uy - (d[1] - a[1]) * ux) > tol:
                continue
            tc = (c[0] - a[0]) * ux + (c[1] - a[1]) * uy
            td = (d[0] - a[0]) * ux + (d[1] - a[1]) * uy
            t0, t1 = max(0.0, min(tc, td)), min(length, max(tc, td))
            if t1 - t0 < RIDGE_CAP["min_length"]:
                continue
            p0 = (round(a[0] + ux * t0, 4), round(a[1] + uy * t0, 4))
            p1 = (round(a[0] + ux * t1, 4), round(a[1] + uy * t1, 4))
            found[tuple(sorted((p0, p1)))] = (min(i, j), max(i, j))
    out = []
    for (a, b), (i, j) in sorted(found.items()):
        grads = [(top[i][0], top[i][1]), (top[j][0], top[j][1])]
        norms = [math.hypot(*g) for g in grads]
        if min(norms) > 1e-6 and (grads[0][0] * grads[1][0] + grads[0][1] * grads[1][1]) / (norms[0] * norms[1]) \
                > RIDGE_CAP["break_cos"]:
            continue                                     # a break line (mansard, gambrel): both planes fall one way
        za = min(geom2d.plane_z(top[k], *a) for k in (i, j))
        zb = min(geom2d.plane_z(top[k], *b) for k in (i, j))
        out.append(((a[0], a[1], za), (b[0], b[1], zb)))
    return out


def ridge_caps(model: dict) -> tuple[list, list]:
    """``(verts, faces)`` of the ridge and hip caps (pure): a half-round tile line of ``RIDGE_CAP["radius"]`` along
    every ``ridge_lines`` edge, sunk ``sink`` into the covering, closed at both ends."""
    r, seg, sink = RIDGE_CAP["radius"], RIDGE_CAP["segments"], RIDGE_CAP["sink"]
    verts: list = []
    faces: list = []
    for a, b in ridge_lines(model):
        d = [b[i] - a[i] for i in range(3)]
        length = math.sqrt(sum(c * c for c in d))
        if length < 1e-6:
            continue
        u = [c / length for c in d]
        side = [u[1], -u[0], 0.0]                          # horizontal, square to the edge
        sl = math.hypot(side[0], side[1]) or 1.0
        side = [side[0] / sl, side[1] / sl, 0.0]
        up = [side[1] * u[2] - side[2] * u[1], side[2] * u[0] - side[0] * u[2], side[0] * u[1] - side[1] * u[0]]
        if up[2] < 0:
            up = [-c for c in up]
        base = len(verts)
        for end in (a, b):
            for k in range(seg + 1):
                t = math.pi * k / seg
                c, s_ = math.cos(t) * r, math.sin(t) * r - sink
                verts.append(tuple(end[i] + side[i] * c + up[i] * s_ for i in range(3)))
        m = seg + 1
        for k in range(seg):
            faces.append([base + k, base + k + 1, base + m + k + 1, base + m + k])
        faces.append([base + k for k in range(m)][::-1])
        faces.append([base + m + k for k in range(m)])
    return verts, faces


def parapet_ring(model: dict) -> list[tuple[list, list]]:
    """The parapet of a ``flat_cut`` roof (Milestone 12, pure): one box per outline edge, ``parapet_thickness``
    inside the outline, from the roof top up by ``model["parapet"]``; [] for any other roof."""
    h = float(model.get("parapet") or 0.0)
    if model.get("kind") != "flat_cut" or h <= 0 or not model.get("equations"):
        return []
    t = DEFAULTS["parapet_thickness"]
    pts = geom2d.ccw(model["outline"])
    out = []
    for i in range(len(pts)):
        p, q = pts[i], pts[(i + 1) % len(pts)]
        length = G.distance(p, q)
        if length < 1e-6:
            continue
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = -uy, ux                                     # counter-clockwise: left of the edge is inside
        mid = G.segment_midpoint(p, q)
        z0 = min(geom2d.plane_z(e, *mid) for e in model["equations"])
        out.append(geom2d.box((mid[0] + nx * t / 2.0, mid[1] + ny * t / 2.0, z0 + h / 2.0), (length, t, h),
                              math.degrees(math.atan2(uy, ux))))
    return out


def ceiling_faces(polygon, holes, planes: Sequence[Plane]) -> tuple[list, list]:
    """``(verts, faces)`` of a room ceiling under a roof: the room minus ``holes`` on the lowest of ``planes``
    (``ceiling_planes``), facing down."""
    return geom2d.sloped_faces(polygon, holes, planes, facing_up=False)


def wall_cut(model: dict) -> Optional[dict]:
    """What the walls under the roof are cut with (``shell.build_walls``): ``{"planes": the roof underside,
    "top": the ridge}``; None for a roof that is not convex (its walls keep their level height)."""
    if not model or not model.get("convex") or not model.get("equations"):
        return None
    return {"planes": underside(model), "top": max(float(p[2]) for pl in model["planes"] for p in pl["points"])}


# --------------------------------------------------------------------------
# Roof terraces: parapets
# --------------------------------------------------------------------------

def segment_inside(a, b, polygon) -> list[tuple[float, float]]:
    """``[(t0, t1)]``: the stretches of the segment ``a``-``b`` (parameters 0..1) inside ``polygon`` (its
    convex pieces clip the segment; touching stretches are joined)."""
    spans = []
    ax, ay, bx, by = float(a[0]), float(a[1]), float(b[0]), float(b[1])
    for piece in geom2d.convex_pieces(polygon):
        t0, t1 = 0.0, 1.0
        n = len(piece)
        for i in range(n):
            p, q = piece[i], piece[(i + 1) % n]
            nx, ny = G.unit_normal_left(p, q)                 # into the counter-clockwise piece
            da = (ax - p[0]) * nx + (ay - p[1]) * ny
            db = (bx - p[0]) * nx + (by - p[1]) * ny
            if da < -1e-9 and db < -1e-9:
                t0, t1 = 1.0, 0.0
                break
            if abs(da - db) > 1e-12:
                t = da / (da - db)
                if da < 0:
                    t0 = max(t0, t)
                elif db < 0:
                    t1 = min(t1, t)
        if t1 - t0 > 1e-6:
            spans.append((t0, t1))
    spans.sort()
    joined: list[list[float]] = []
    for t0, t1 in spans:
        if joined and t0 <= joined[-1][1] + 1e-6:
            joined[-1][1] = max(joined[-1][1], t1)
        else:
            joined.append([t0, t1])
    return [(round(a0, 9), round(a1, 9)) for a0, a1 in joined]


def parapet_cuts(model: dict, building: dict, level: dict) -> dict[str, list[dict]]:
    """Where the walls under a roof terrace end at the parapet (pure; §1.6b row 13): per wall id the
    stretches of its centre line under a roof opening, ``{"t0", "t1", "z_top", "opening_id", "source"}`` (t
    from the wall's start). The walls are the opening's ``parapet_wall_ids``, else the outer walls of the level
    whose centre line runs under the opening; their top there is the terrace floor + the parapet height
    (drawn or assumed): no roof is over them."""
    floor_z = float(level["elevation"])
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level["id"]}
    out: dict[str, list[dict]] = {}
    for o in model.get("openings") or []:
        ids = [i for i in o.get("parapet_wall_ids") or [] if i in walls]
        source = "parapet_wall_ids"
        if not ids:
            ids = [w["id"] for w in walls.values() if w.get("exterior")
                   and segment_inside(w["start"], w["end"], o["polygon"])]
            source = "outer walls under the opening"
        for wid in ids:
            w = walls[wid]
            for t0, t1 in segment_inside(w["start"], w["end"], o["polygon"]):
                out.setdefault(wid, []).append({"t0": t0, "t1": t1, "z_top": floor_z + float(o["parapet_height"]),
                                                "opening_id": o["id"], "source": source})
    return out


# --------------------------------------------------------------------------
# Blender
# --------------------------------------------------------------------------

def build_roof(model: dict, collection, materials: Sequence, manifest_objects: list, assumed: list) -> object:
    """The roof object (``roof``, kind ``roof``; status ``assumed`` when its planes were derived, else
    ``verified``) with the covering, soffit and fascia materials (``materials``, three slots). Its manifest
    entry lists the planes, their source and the z range; every assumption goes to ``assumed``."""
    from wenart.blender import common

    verts, faces, slots = roof_solid(model)
    status = "verified" if model["planes_source"] == "building" else "assumed"
    ob = common.new_mesh_object("roof", verts, faces, collection=collection, wenart_id="roof", kind="roof",
                                status=status, materials=list(materials), face_material_indices=slots)
    zs = [v[2] for v in verts] or [0.0]
    manifest_objects.append({
        "name": ob.name, "wenart_id": "roof", "kind": "roof", "status": status,
        "level_id": model.get("over_level_id"), "element_id": "roof", "evidence": [],
        "material": materials[0].name if materials else None, "textured": False, "pass_index": None,
        "assumed": {a["field"]: a["value"] for a in model["assumed"]},
        "roof_type": model.get("type"), "planes_source": model["planes_source"],
        "planes": model["planes"], "thickness": model["thickness"],
        "openings": [{"id": o["id"], "kind": o["kind"], "room_id": o["room_id"]} for o in model["openings"]],
        "z_range": [round(min(zs), 4), round(max(zs), 4)], "faces": len(faces),
    })
    for a in model["assumed"]:
        assumed.append({"object": "roof", "field": a["field"], "value": a["value"], "reason": a["reason"]})
    cv, cf = ridge_caps(model)
    if cf:                                       # 24 Oct 2026: the ridge and hip tiles (not drawn)
        caps = common.new_mesh_object("roof_ridges", cv, cf, collection=collection, wenart_id="roof_ridges",
                                      kind="roof", status="assumed", materials=[materials[0]] if materials else [])
        reason = "ridge and hip caps along the roof's ridges and hips (not drawn; a tiled roof has them)"
        manifest_objects.append({
            "name": caps.name, "wenart_id": "roof_ridges", "kind": "roof", "status": "assumed",
            "level_id": model.get("over_level_id"), "element_id": "roof", "evidence": [],
            "material": materials[0].name if materials else None, "textured": False, "pass_index": None,
            "assumed": {"detail": "ridge_caps", "reason": reason}, "ridges": len(ridge_lines(model))})
        assumed.append({"object": caps.name, "field": "ridge_caps", "value": len(ridge_lines(model)),
                        "reason": reason, "parent": "roof", "kind": "ridge_caps"})
    return ob
