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
    "flat_thickness": 0.30,      # a flat roof slab
}
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


def _ridge_axis(rect: dict, roof: dict) -> tuple[tuple[float, float], tuple[float, float], float, float,
                                                  Optional[float], str]:
    """``(r, across, half_along, half_across, ridge_half_length, source)`` of a rectangle: the ridge
    direction from the longest drawn ridge line (snapped to the nearer rectangle axis), else the long axis."""
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
    return u, v, a, b, None, "long axis"


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


def _offset_outline(rect: dict, grow: float) -> list[tuple[float, float]]:
    return geom2d.rectangle_corners(rect, grow)


def derive(roof: dict, building: dict) -> dict:
    """The derivation behind ``planes_for``: ``{"planes": [...], "equations": [(a, b, c)], "outline",
    "eaves_z", "ridge_z", "pitches", "assumed": [{"field", "value", "reason"}], "warnings", "notes"}``."""
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
                    "notes": notes}
        rect = geom2d.oriented_rectangle(wall_line)
        outline = _offset_outline(rect, overhang) if rtype != "flat" or overhang > 0 else geom2d.ccw(wall_line)
        assumed.append({"field": "outline", "value": [[round(x, 4), round(y, 4)] for x, y in outline],
                        "reason": f"no roof outline drawn: the walls' outline ({method}) grown by the "
                                  f"{'assumed ' if overhang_assumed else ''}overhang {overhang:.2f} m"})
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
    r, across, half_along, half_across, ridge_half, ridge_source = _ridge_axis(rect, roof)

    def first_pitch() -> float:
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
                "assumed": assumed, "warnings": warnings, "notes": notes}

    p1 = first_pitch()
    t1 = math.tan(math.radians(p1))
    if eaves is None:
        if knee is not None:
            eaves = floor_z + knee - (0.0 if overhang_used else overhang) * t1
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
            eaves = floor_z + knee_a - (0.0 if overhang_used else overhang) * t1
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
        if ridge_source == "long axis" and rtype != "hip":
            notes.append("ridge along the long side of the outline (no ridge line drawn)")
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
    elif rtype in ("mansard", "gambrel"):
        brk = geom2d.ccw(roof.get("break_line") or [])
        p2 = pitches[1] if len(pitches) > 1 else None
        if len(brk) < 3:
            inset = min(half_across, half_along) * 0.3
            brk = geom2d.rectangle_corners(rect, -inset)
            assumed.append({"field": "break_line", "value": [[round(x, 4), round(y, 4)] for x, y in brk],
                            "reason": f"no break line drawn: the outline rectangle {inset:.2f} m in"})
        brect = geom2d.oriented_rectangle(brk)
        # Offsets of the break line from the outline, per side of the outline rectangle.
        offs = []
        cx, cy = rect["center"]
        bx, by = brect["center"]
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
        b_r, b_across, b_half_along, b_half_across, b_ridge_half, _ = _ridge_axis(brect, roof)
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
                "assumed": assumed, "warnings": [f"unknown roof type {rtype!r}: no roof"], "notes": notes}

    planes = planes_from_equations(eqs, outline, _named(eqs, tiers))
    if ridge is not None and abs(top - ridge) > 0.05:
        warnings.append(f"derived ridge {top:.3f} m vs the drawn ridge height {ridge:.3f} m "
                        f"({(top - ridge) * 100:+.0f} cm): the pitches are kept")
    return {"planes": planes, "equations": eqs, "outline": outline, "eaves_z": eaves, "ridge_z": top,
            "pitches": pitches or [p1], "assumed": assumed, "warnings": warnings, "notes": notes}


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
        if psource == "assumed":
            assumed.append({"field": f"parapet_height:{o.get('id')}", "value": height,
                            "reason": (ph or {}).get("note") if isinstance(ph, dict) and ph.get("note")
                            else "parapet height not drawn"})
        openings.append({"id": o.get("id"), "kind": o.get("kind") or "other", "room_id": o.get("room_id"),
                         "polygon": poly, "parapet_height": height, "parapet_source": psource,
                         "parapet_wall_ids": list(o.get("parapet_wall_ids") or [])})
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
             "notes": notes, "derived_check": check, "profile": roof.get("profile")}
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
    return _mesh(faces)


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
    return ob
