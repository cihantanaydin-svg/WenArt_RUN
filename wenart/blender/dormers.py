"""Dormers over drawn doors and windows the roof leaves too low (31 Oct 2026).

The user on real04 run 20261030-181158-full (the attic bathroom render ``cam_r_L1_banyo_1``): "There is something
seriously wrong here, investigate what happened and fix it, the door the toilet not making sense at all". The two attic
bathroom doors ``d_L1_004`` / ``d_L1_005`` (0.82 x 2.10 m in walls square to the eaves) stand under our inferred
mansard with 1.00 m of head room; ``door_states.apply_under_roof`` lowered both to 1.00 m ("it needs a dormer or a
raised roof (review)"): 1 m hatch doors with their frames under the slope. The rule here is general (CLAUDE.md);
real04 is the test case.

Rule: a drawn door is source evidence that a full-height door fits there (CLAUDE.md trust order: source geometry
outranks an inferred part such as the roof). When the roof leaves a door less head room than ``door_states.MIN_CLEAR_M``
and no spot within ``door_states.ROOF_SLIDE_MAX_M`` along its wall leaves more (``door_states.slide_spot``), the build
raises a shed DORMER over it instead of lowering it; the door keeps its drawn (or standard) height. A door that fits by
lowering to its head room (at least ``MIN_CLEAR_M``) or by such a slide keeps that behaviour (``door_states``). A drawn
window that crosses the roof gets the same: one whose height is drawn and whose top stands over the roof underside at
its wall, and one of assumed height that the roof clip (``roof.clip_openings_to_roof``) could not keep usable ("needs a
dormer: review").

What (pure, no ``bpy`` but ``build_dormers``):

- ``needs(building, level, model)``: the doors and windows of the level under a convex roof that need a dormer.
- ``plan(building, level, model)``: one dormer per opening, or one shared by openings on the same roof plane whose
  boxes overlap or nearly touch (``DORMER["merge_gap_m"]``). The box is aligned with the roof plane over the opening
  (its downhill direction ``d``, its contour ``e``): it covers the opening's NEED, the plan rectangle that must stand
  under a full-height ceiling (a door: its frame ``DORMER["margin_m"]`` past each jamb and ``DORMER["approach_m"]`` past
  each wall face, for the open leaf and the step through; a window: ``DORMER["window_depth_m"]`` past each face),
  clipped to the level's outline, with a cheek wall ``DORMER["cheek_t_m"]`` on each side. Its front stands on the
  facade (the outer face of the wall under the eaves) when the need ends within ``DORMER["flush_max_m"]`` of it (the
  facade wall rises to the dormer: the dormer's front face; the overhang in front of it is cut to the eaves), else on
  the roof ``DORMER["front_margin_m"]`` past the need (its own clad front face). Its roof is a shed (``pitches_deg``:
  the steepest that fits, flat last) falling to the front; its ceiling stands ``head_clear_m`` over the opening's top
  (the preferred clearance, else the least one: the head gap and the architrave); its back is where its roof meets the
  main roof (``base_top_z``), straight across the dormer within ``DORMER["junction_tol_m"]`` (no dormer at a hip or a
  valley). Its slab has the main roof's vertical thickness at that junction, so the dormer's underside meets the main
  underside there and the ceilings join. A dormer that would cut into a roof terrace, leave the roof, reach over the
  level's flat ceiling, find no junction, or not give the opening its height (the code check: ``door_states.head_room``
  with the dormer, ``roof.opening_head_limit``) is refused with the reason; the door then keeps the old behaviour (its
  finding names why). Every dormer is ``inferred``, by the architect, with the reason and the openings it serves.
- ``apply(...)`` / ``raise_dormers(...)``: the roof model gets ``dormers`` (``roof.roof_solid`` cuts them out,
  ``roof.top_z`` / ``underside_z`` read them, ``roof.wall_cut`` cuts the walls under a dormer at its underside:
  ``wall_spans``), the level gets ``ceiling_dormers`` (the raised ceiling: ``geom2d.raised_surface_z``,
  ``geom2d.level_ceiling_z``; the door's head room and open leaf, the furniture and decor caps, the stairs, the lights
  and the checks under the roof read it), every served opening a ``dormer`` record and an evidence line; ``assumed``
  rows (kind ``dormer``, by architect) and warnings for the refused ones (``dormer_refused`` on the opening).
- ``room_ceiling(polygon, holes, planes, raises)``: a room's ceiling under the roof with the dormer ceilings in it (the
  shell's ``build_floors_ceilings``); the step from the slope up to the dormer's ceiling is the cheek's inner face.
- ``meshes(dormer, model)``: the dormer's roof slab (covering, soffit, fascia), its cheeks (and a set-back front face)
  from the main roof's underside up to its own (the facade look outside, the ceiling plaster inside and under), the
  flashings along its cheeks, behind it and (set back) in front of it.
- ``build_dormers`` (bpy): one object per dormer (kind ``roof``, detail ``dormer``: hidden in the top-down views with
  the roof, never read as poking through it), its manifest record and its looks (``assumed``).

Why this way: the dormer is planned in ``build.prepare`` after the roof and the architect's answers and before the roof
clip of the openings, so the clip, the door rules (D5, UL128), the walls, the ceilings and the checks all read one
record. The furniture stage before the build does not know the dormers (its caps stay under the old slope there: lower,
never through anything); the camera search's ray model keeps the old slope too (a camera there is refused, never put
inside the roof).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d

# Building rules of thumb (not a cited norm), metres and degrees.
DORMER = {
    "approach_m": 0.75,          # a door's need past each wall face: the open leaf (a 0.70 m leaf) and the step through
    "margin_m": 0.10,            # past each side of the door's frame (along its wall) or of a window
    "window_depth_m": 0.15,      # a window's need past each wall face (its reveal and sill)
    "head_clear_m": (0.15, 0.07),  # the ceiling over the opening's top: preferred, else the least (gap + architrave)
    "pitches_deg": (5.0, 3.0, 2.0, 1.0, 0.0),   # the shed roof: the steepest that fits (a membrane or metal roof)
    "cheek_t_m": 0.12,           # the cheek walls (studs and cladding)
    "front_t_m": 0.15,           # a set-back front face
    "overhang_front_m": 0.20,    # the dormer roof past its front face ...
    "overhang_side_m": 0.04,     # ... and past its cheeks
    "flush_max_m": 0.80,         # its front on the facade when the need ends this near the facade's outer face
    "front_margin_m": 0.10,      # a set-back front this far past the need
    "junction_tol_m": 0.03,      # the back line (dormer roof meets main roof) straight across the dormer within this
    "merge_gap_m": 0.60,         # openings on one roof plane whose needs are this close share a dormer
    "eave_reach_m": 0.05,        # a dormer on the facade cuts the overhang this far past the eaves (a clean cut)
    "march_step_m": 0.05,        # the back line is searched in these steps up the roof, then to a tenth of a mm
    "max_depth_m": 12.0,         # no back line within this of the front: refused
    "min_slope": 0.05,           # a main plane flatter than this (tan, about 3 degrees) gets no dormer
    "flashing_w_m": 0.15, "flashing_t_m": 0.006, "upstand_m": 0.12,
    "tile_min_pitch_deg": 15.0,  # a dormer roof flatter than this is metal-clad (tiles need more fall)
    "window_cross_m": 0.02,      # a drawn window this far over the roof underside crosses the roof
}
WINDOW_MIN_H_M = 0.4             # = roof.MIN_OPENING_HEIGHT["window"]
RULE = "blender.dormers"
SLOT_COVER, SLOT_SOFFIT, SLOT_FASCIA, SLOT_CLAD, SLOT_FLASHING = 0, 1, 2, 3, 4
DORMER_LOOKS = {
    "cover_metal": ("standing_seam", "dark grey", "a low-pitched or flat dormer roof clad in standing-seam metal "
                                                  "(tiles need a steeper fall; not drawn)"),
    "flashing": ("aluminium_anthracite", None, "the dormer's flashings along its cheeks and its back (not drawn)"),
}


# --------------------------------------------------------------------------------------------------- the frame (pure)

def _pt(o, ev, dv, ee: float, dd: float) -> tuple[float, float]:
    return (o[0] + ev[0] * ee + dv[0] * dd, o[1] + ev[1] * ee + dv[1] * dd)


def _coords(o, ev, dv, p) -> tuple[float, float]:
    x, y = float(p[0]) - o[0], float(p[1]) - o[1]
    return (x * ev[0] + y * ev[1], x * dv[0] + y * dv[1])


def _rect(o, ev, dv, e_lo: float, e_hi: float, d_lo: float, d_hi: float) -> list[tuple[float, float]]:
    """The rectangle ``e_lo..e_hi`` x ``d_lo..d_hi`` of the frame, counter-clockwise in the plan."""
    return geom2d.ccw([_pt(o, ev, dv, a, b) for a, b in ((e_lo, d_lo), (e_hi, d_lo), (e_hi, d_hi), (e_lo, d_hi))])


def _plane(o, dv, z_ref: float, d_ref: float, s: float) -> tuple[float, float, float]:
    """``z = z_ref + s (d_ref - d)`` with ``d`` the frame's downhill coordinate, as ``(a, b, c)``."""
    a, b = -s * dv[0], -s * dv[1]
    return (a, b, z_ref + s * d_ref + s * (dv[0] * o[0] + dv[1] * o[1]))


def _ray(p, direction, polygon) -> Optional[float]:
    """The nearest ``t >= 0`` where ``p + t direction`` meets an edge of ``polygon`` (None when it meets none)."""
    best = None
    n = len(polygon)
    for i in range(n):
        a, b = polygon[i], polygon[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = direction[0] * ey - direction[1] * ex
        if abs(den) < 1e-12:
            continue
        rx, ry = a[0] - p[0], a[1] - p[1]
        t = (rx * ey - ry * ex) / den
        s = (rx * direction[1] - ry * direction[0]) / den
        if t >= -1e-6 and -1e-9 <= s <= 1.0 + 1e-9:
            best = t if best is None else min(best, t)
    return None if best is None else max(0.0, best)


def _overlap(a, b) -> float:
    """The area shared by the convex polygon ``b`` and the polygon ``a``."""
    part = geom2d.clip_convex(a, b)
    return G.polygon_area(part) if len(part) >= 3 else 0.0


# ------------------------------------------------------------------------------------------------- what needs one

def _level_walls(building: dict, level: dict) -> dict:
    return {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level["id"] and w.get("id")}


def needs(building: dict, level: dict, model: Optional[dict]) -> list[dict]:
    """The doors and windows of ``level`` under ``model`` (a convex roof over this level, its ceiling planes set) that
    need a dormer (module docstring): ``[{"opening", "wall", "type", "head_room", "why"}]`` (pure)."""
    from wenart.blender import door_states as DS
    from wenart.blender import roof as R
    from wenart.blender import shell as SH

    if not model or not model.get("equations") or not model.get("convex") or model.get("parts") \
            or model.get("over_level_id") != level.get("id") or not level.get("ceiling_planes"):
        return []
    walls = _level_walls(building, level)
    openings = [o for o in building.get("openings") or [] if o.get("level_id") == level["id"]]
    floor = float(level.get("elevation") or 0.0)
    out = []
    for o in openings:
        wall = walls.get(o.get("wall_id"))
        if wall is None or not o.get("center") or o.get("virtual"):
            continue
        if o.get("type") == "door":
            room = DS.head_room(o, wall, level)
            h = DS.door_height_of(o)
            if room is None or h <= room + DS.HEIGHT_TOL_M or room >= DS.MIN_CLEAR_M - 1e-9:
                continue                                  # it fits, or lowering to its head room keeps it usable
            if DS.slide_spot(building, o, wall, level, openings) is not None:
                continue                                  # a slide along its wall fixes it (door_states)
            out.append({"opening": o, "wall": wall, "type": "door", "head_room": room,
                        "why": f"the roof leaves it {room:.2f} m of head room (a door needs {DS.MIN_CLEAR_M:.2f} m "
                               f"at least) and no spot within {DS.ROOF_SLIDE_MAX_M:.1f} m along its wall leaves more"})
        elif o.get("type") == "window":
            limit = R.opening_head_limit(model, level, wall, o)
            if limit is None:
                continue
            bottom, top, _a = SH.opening_vertical(o, level, False)
            listed = o.get("assumed") or ()
            if o.get("height") is not None and "height" not in listed:
                if top - floor <= limit + R.OPENING_ROOF_GAP + DORMER["window_cross_m"]:
                    continue
                why = (f"its drawn top {top - floor:.2f} m over the floor stands over the roof underside at its wall "
                       f"({limit + R.OPENING_ROOF_GAP:.2f} m)")
            else:
                if top - floor <= limit + 1e-6:
                    continue
                sill = bottom - floor
                height = limit - sill
                if height < WINDOW_MIN_H_M and (o.get("sill_height") is None or "sill_height" in listed):
                    sill = max(0.0, limit - WINDOW_MIN_H_M)
                    height = limit - sill
                if height >= WINDOW_MIN_H_M - 1e-6:
                    continue                              # the roof clip keeps it usable (roof.clip_openings_to_roof)
                why = (f"the roof leaves it {max(height, 0.0):.2f} m (a window needs {WINDOW_MIN_H_M:.2f} m at least) "
                       f"under the roof underside at its wall")
            out.append({"opening": o, "wall": wall, "type": "window", "head_room": round(limit, 4), "why": why})
    return out


def need_of(item: dict, level: dict, outline: Sequence = ()) -> dict:
    """The plan region an opening needs a full-height ceiling over and the height (module docstring; pure):
    ``{"id", "type", "poly", "top_z"}`` (``top_z``: the opening's top, world z)."""
    from wenart.blender import door_states as DS
    from wenart.blender import shell as SH

    o, wall = item["opening"], item["wall"]
    cx, cy, _t = DS.centre_on_wall(o, wall)
    _a, u, _l = DS._axis(wall)
    n = G.unit_normal_left(wall["start"], wall["end"])
    half_t = float(wall.get("thickness") or 0.2) / 2.0
    w = float(o.get("width") or 0.0)
    floor = float(level.get("elevation") or 0.0)
    if item["type"] == "door":
        along, across = w / 2.0 + DS.FRAME_ALONG_M + DORMER["margin_m"], half_t + DORMER["approach_m"]
        top = floor + float(o.get("sill_height") or 0.0) + DS.door_height_of(o)
    else:
        along, across = w / 2.0 + DORMER["margin_m"], half_t + DORMER["window_depth_m"]
        top = SH.opening_vertical(o, level, False)[1]
    rect = [(cx + u[0] * s * along + n[0] * k * across, cy + u[1] * s * along + n[1] * k * across)
            for s, k in ((-1.0, -1.0), (1.0, -1.0), (1.0, 1.0), (-1.0, 1.0))]
    poly = geom2d.clip_convex(outline, rect) if len(outline or ()) >= 3 else []
    return {"id": o["id"], "type": item["type"], "poly": poly or geom2d.ccw(rect), "top_z": round(top, 4)}


# ------------------------------------------------------------------------------------------------------ one dormer

def _frame_of(model: dict, needs_: Sequence[dict]):
    """``(plane index, d, e)`` of the main plane over the lowest need corner, None on a flat part."""
    from wenart.blender import roof as R

    pts = [p for nd in needs_ for p in nd["poly"]]
    low = min(pts, key=lambda p: R.base_top_z(model, float(p[0]), float(p[1])))
    eqs = model["equations"]
    j = min(range(len(eqs)), key=lambda i: geom2d.plane_z(eqs[i], float(low[0]), float(low[1])))
    a, b = float(eqs[j][0]), float(eqs[j][1])
    g = math.hypot(a, b)
    if g < DORMER["min_slope"]:
        return None
    dv = (-a / g, -b / g)
    return j, dv, (-dv[1], dv[0])


def _v_of(model: dict, j: int) -> float:
    e = model["equations"][j]
    return float(model["thickness"]) * math.sqrt(1.0 + float(e[0]) ** 2 + float(e[1]) ** 2)


def _junction(model: dict, o, ev, dv, ee: float, d_start: float, top_at) -> Optional[float]:
    """The downhill coordinate where the dormer roof (``top_at(d)``) meets the main roof walking up from ``d_start``
    at the contour coordinate ``ee`` (pure); None when it does not, within the roof and ``max_depth_m``."""
    from wenart.blender import roof as R

    def gap(dd: float) -> float:
        x, y = _pt(o, ev, dv, ee, dd)
        return top_at(dd) - R.base_top_z(model, x, y)

    if gap(d_start) <= 0.0:
        return None
    step, dd = DORMER["march_step_m"], d_start
    outline = model["outline"]
    while dd > d_start - DORMER["max_depth_m"]:
        nd = dd - step
        if not G.point_in_polygon(_pt(o, ev, dv, ee, nd), outline):
            return None
        if gap(nd) <= 0.0:
            lo, hi = nd, dd
            while hi - lo > 1e-4:
                mid = (lo + hi) / 2.0
                if gap(mid) <= 0.0:
                    lo = mid
                else:
                    hi = mid
            return (lo + hi) / 2.0
        dd = nd
    return None


def fit(model: dict, level: dict, outline: Sequence, needs_: Sequence[dict], clear: float, pitch_deg: float
        ) -> tuple[Optional[dict], str]:
    """The dormer over ``needs_`` with the ceiling ``clear`` over their tops and a ``pitch_deg`` shed roof (pure):
    ``(record, "")`` or ``(None, reason)``. The record's polygons are plan polygons (counter-clockwise), its planes
    ``(a, b, c)`` of ``z = a x + b y + c``: ``top`` (its covering), ``under`` (its underside) and ``ceiling``."""
    from wenart.blender import roof as R

    fr = _frame_of(model, needs_)
    if fr is None:
        return None, "the roof over it is flat there"
    j0, dv, ev = fr
    pts = [(p, nd["top_z"] + clear) for nd in needs_ for p in nd["poly"]]
    o = (sum(float(p[0]) for p, _z in pts) / len(pts), sum(float(p[1]) for p, _z in pts) / len(pts))
    cs = [(_coords(o, ev, dv, p), z) for p, z in pts]
    emin, emax = min(c[0][0] for c in cs), max(c[0][0] for c in cs)
    d_need = max(c[0][1] for c in cs)
    flat = float(level["elevation"]) + float(level["ceiling_height"])
    if max(z for _c, z in cs) > flat + 1e-6:
        return None, (f"the level's flat ceiling ({flat - float(level['elevation']):.2f} m over the floor) is lower "
                      f"than the opening needs")
    s = math.tan(math.radians(pitch_deg))
    zc_ref = max(z - s * (d_need - c[1]) for c, z in cs)     # the dormer's ceiling at the need's front
    t_c = DORMER["cheek_t_m"]
    e0, e1 = emin - t_c, emax + t_c
    samples = (e0, (e0 + e1) / 2.0, e1)
    # the front: on the facade when the need ends near it (the same facade across the dormer), else set back
    hits = [_ray(_pt(o, ev, dv, ee, d_need), dv, outline) for ee in samples] if len(outline or ()) >= 3 else [None]
    flush = all(h is not None for h in hits) and max(hits) - min(hits) <= 0.05 \
        and min(hits) <= DORMER["flush_max_m"] + 1e-9
    d_front = d_need + min(hits) if flush else d_need + DORMER["front_margin_m"]
    v = _v_of(model, j0)
    gap = R.CEILING_GAP
    d_back = None
    for _round in range(3):
        top_ref = zc_ref + gap + v

        def top_at(dd: float, top_ref=top_ref) -> float:
            return top_ref + s * (d_need - dd)
        got = [_junction(model, o, ev, dv, ee, d_front, top_at) for ee in samples]
        if any(g is None for g in got):
            return None, (f"its roof ({pitch_deg:g} degrees) finds no clean junction with the main roof (the roof "
                          f"never rises to it within the roof's outline)")
        if max(got) - min(got) > DORMER["junction_tol_m"]:
            return None, (f"its back line would not be straight ({max(got) - min(got):.2f} m out across it: a hip or "
                          f"another roof plane)")
        d_back = max(got)
        jx, jy = _pt(o, ev, dv, samples[1], d_back - 0.01)
        eqs = model["equations"]
        jj = min(range(len(eqs)), key=lambda i: geom2d.plane_z(eqs[i], jx, jy))
        v_new = _v_of(model, jj)
        if abs(v_new - v) < 1e-6:
            break
        v = v_new
    if d_back >= d_need - 1e-3:
        return None, "the main roof already reaches the needed height over the opening"
    top = _plane(o, dv, zc_ref + gap + v, d_need, s)
    under = (top[0], top[1], top[2] - v)
    ceiling = (under[0], under[1], under[2] - gap)
    front_t = 0.0 if flush else DORMER["front_t_m"]
    d_hole = d_front
    if flush:
        eaves = [_ray(_pt(o, ev, dv, ee, d_front), dv, model["outline"]) for ee in samples]
        if any(h is None for h in eaves):
            return None, "its front on the facade finds no eaves in front of it"
        d_hole = d_front + max(eaves) + DORMER["eave_reach_m"]
    footprint = _rect(o, ev, dv, e0, e1, d_back, d_front)
    for p in footprint:
        if not G.point_in_polygon(p, model["outline"]):
            return None, "it would stand out of the roof's outline"
    hole = _rect(o, ev, dv, e0, e1, d_back, d_hole)
    for op in model.get("openings") or []:
        if len(op.get("polygon") or []) >= 3 and _overlap(op["polygon"], hole) > 1e-4:
            return None, f"it would cut into the roof terrace or opening {op.get('id')}"
    floor = float(level["elevation"])
    front_top = geom2d.plane_z(top, *_pt(o, ev, dv, (e0 + e1) / 2.0, d_front))
    rec = {
        "level_id": level["id"], "plane": j0, "d": [round(dv[0], 9), round(dv[1], 9)],
        "e": [round(ev[0], 9), round(ev[1], 9)], "origin": [round(o[0], 6), round(o[1], 6)],
        "e0": round(e0, 6), "e1": round(e1, 6), "d_back": round(d_back, 6), "d_front": round(d_front, 6),
        "d_need": round(d_need, 6), "flush": flush, "pitch_deg": float(pitch_deg), "head_clear_m": float(clear),
        "thickness_v": round(v, 6), "cheek_t": t_c, "front_t": front_t,
        "top": [round(x, 9) for x in top], "under": [round(x, 9) for x in under],
        "ceiling": [round(x, 9) for x in ceiling], "flat_z": round(flat, 6),
        "footprint": [list(p) for p in footprint],
        "inner": [list(p) for p in _rect(o, ev, dv, e0 + t_c, e1 - t_c, d_back, d_front - front_t)],
        "hole": [list(p) for p in hole],
        "roof_poly": [list(p) for p in _rect(o, ev, dv, e0 - DORMER["overhang_side_m"], e1 + DORMER["overhang_side_m"],
                                              d_back, d_front + DORMER["overhang_front_m"])],
        "cheeks": [[list(p) for p in _rect(o, ev, dv, e0, e0 + t_c, d_back, d_front - front_t)],
                   [list(p) for p in _rect(o, ev, dv, e1 - t_c, e1, d_back, d_front - front_t)]],
        "front": None if flush else [list(p) for p in _rect(o, ev, dv, e0, e1, d_front - front_t, d_front)],
        "width_m": round(e1 - e0, 3), "depth_m": round(d_front - d_back, 3),
        "front_top_z": round(front_top, 4), "ceiling_m": round(zc_ref - floor, 4),
        "needs": [{"id": nd["id"], "type": nd["type"], "poly": [list(p) for p in nd["poly"]], "top_z": nd["top_z"]}
                  for nd in needs_],
    }
    return rec, ""


def ceiling_raise(d: dict) -> dict:
    """A dormer's record for its level's ``ceiling_dormers`` (``geom2d.raised_surface_z``): its inner plan region and
    its ceiling planes (its own, and the level's flat ceiling)."""
    return {"id": d["id"], "polygon": [list(p) for p in d["inner"]],
            "planes": [list(d["ceiling"]), [0.0, 0.0, float(d["flat_z"])]]}


def _verified(building: dict, level: dict, model: dict, rec: dict, items: Sequence[dict], others: Sequence[dict]
              ) -> Optional[str]:
    """The code check of a candidate dormer: with it (and the dormers accepted before), every door it serves gets
    its height under the ceiling at its frame (``door_states.head_room``) and every window its top under the roof at
    its wall (``roof.opening_head_limit``). None when it does, else what fails."""
    from wenart.blender import door_states as DS
    from wenart.blender import roof as R
    from wenart.blender import shell as SH

    trial = dict(rec, id=rec.get("id") or "trial")
    lv = dict(level, ceiling_dormers=[ceiling_raise(x) for x in list(others) + [trial]])
    m = dict(model, dormers=list(others) + [trial])
    for it in items:
        o, wall = it["opening"], it["wall"]
        if it["type"] == "door":
            room = DS.head_room(o, wall, lv)
            if room is None or DS.door_height_of(o) > room + DS.HEIGHT_TOL_M:
                return f"{o['id']} would still have only {room if room is not None else 0.0:.2f} m of head room"
        else:
            limit = R.opening_head_limit(m, lv, wall, o)
            top = SH.opening_vertical(o, lv, False)[1] - float(lv["elevation"])
            if limit is None or top > limit + 1e-3:
                return f"{o['id']} would still cross the roof"
    return None


def _try(building: dict, level: dict, model: dict, outline, items: Sequence[dict], others: Sequence[dict]
         ) -> tuple[Optional[dict], str]:
    needs_ = [it["need"] for it in items]
    why = "no candidate"
    for clear in DORMER["head_clear_m"]:
        for pitch in DORMER["pitches_deg"]:
            rec, why_fit = fit(model, level, outline, needs_, clear, pitch)
            if rec is None:
                why = why_fit
                continue
            fail = _verified(building, level, model, rec, items, others)
            if fail is None:
                return rec, ""
            why = fail
    return None, why


def _groups(model: dict, items: list[dict]) -> list[list[dict]]:
    """Openings on the same main plane whose needs overlap or nearly touch along the plane's contour share a dormer."""
    keyed = []
    for it in items:
        fr = _frame_of(model, [it["need"]])
        if fr is None:
            keyed.append((None, None, [it]))
            continue
        j, _dv, ev = fr
        es = [float(p[0]) * ev[0] + float(p[1]) * ev[1] for p in it["need"]["poly"]]
        keyed.append((j, (min(es), max(es)), [it]))
    merged = True
    while merged:
        merged = False
        for a in range(len(keyed)):
            for b in range(a + 1, len(keyed)):
                ja, ra, ia = keyed[a]
                jb, rb, ib = keyed[b]
                if ja is None or ja != jb or ra[0] > rb[1] + DORMER["merge_gap_m"] or rb[0] > ra[1] + DORMER[
                        "merge_gap_m"]:
                    continue
                keyed[a] = (ja, (min(ra[0], rb[0]), max(ra[1], rb[1])), ia + ib)
                del keyed[b]
                merged = True
                break
            if merged:
                break
    return [g for _j, _r, g in keyed]


def _reason(rec: dict, items: Sequence[dict], level: dict) -> str:
    what = " and ".join(f"{it['type']} {it['opening']['id']}" for it in items)
    whys = "; ".join(f"{it['opening']['id']}: {it['why']}" for it in items)
    roof = "flat" if rec["pitch_deg"] <= 0.0 else f"{rec['pitch_deg']:g} degree"
    front = "its front on the facade (the facade wall rises to it)" if rec["flush"] else \
        "its front face set back on the roof"
    return (f"a shed dormer over the drawn {what} ({whys}): the drawn opening is source evidence that it fits at its "
            f"full height, the roof is inferred; {rec['width_m']:.2f} m wide, {rec['depth_m']:.2f} m deep, a {roof} "
            f"roof, {front}, its ceiling {rec['ceiling_m']:.2f} m over the floor at the opening (rule of 31 Oct 2026: "
            f"a drawn door under the roof gets a dormer, never a hatch)")


def plan(building: dict, level: dict, model: Optional[dict]) -> dict:
    """The dormers of ``level`` under ``model`` (module docstring; pure): ``{"dormers": [record], "refused": [{"id",
    "reason"}]}``; each record also has ``id``, ``serves`` (opening ids), ``kinds``, ``reason``, ``by`` (architect),
    ``source`` (inferred) and ``rule``. Planned on the roof without dormers (the level's ``ceiling_dormers`` and the
    model's ``dormers`` are left out)."""
    if not model:
        return {"dormers": [], "refused": []}
    base_level = {k: v for k, v in level.items() if k != "ceiling_dormers"}
    base_model = {k: v for k, v in model.items() if k != "dormers"}
    items = needs(building, base_level, base_model)
    if not items:
        return {"dormers": [], "refused": []}
    outline, _how = geom2d.wall_outline(list(_level_walls(building, level).values()))
    for it in items:
        it["need"] = need_of(it, base_level, outline)
    dormers, refused = [], []
    for group in _groups(base_model, items):
        tries = [group] if len(group) == 1 else [group] + [[it] for it in group]
        done = set()
        for g in tries:
            if any(it["opening"]["id"] in done for it in g):
                continue
            rec, why = _try(building, base_level, base_model, outline, g, dormers)
            if rec is not None and any(_overlap(x["hole"], rec["hole"]) > 1e-4
                                       or _overlap(x["footprint"], rec["footprint"]) > 1e-4 for x in dormers):
                rec, why = None, "it would overlap another dormer"
            if rec is None:
                if len(g) == 1 or len(tries) == 1:
                    for it in g:
                        refused.append({"id": it["opening"]["id"], "reason": why})
                continue
            ids = [it["opening"]["id"] for it in g]
            rec.update(id=f"dormer_{ids[0]}", serves=ids, kinds=sorted({it["type"] for it in g}),
                       reason=_reason(rec, g, base_level), by="architect", source="inferred", inferred=True,
                       rule=RULE)
            dormers.append(rec)
            done.update(ids)
            if g is group:
                break
    return {"dormers": dormers, "refused": refused}


def apply(building: dict, level: dict, model: dict, planned: dict) -> tuple[list[dict], list[str]]:
    """Carry out ``plan`` (in place): the model's ``dormers``, the level's ``ceiling_dormers`` (none: the key is
    removed), each served opening's ``dormer`` record and evidence line, a refused one's ``dormer_refused``.
    ``(assumed rows, warnings)``."""
    model["dormers"] = list(planned.get("dormers") or [])
    level.pop("ceiling_dormers", None)
    if model["dormers"]:
        level["ceiling_dormers"] = [ceiling_raise(d) for d in model["dormers"]]
    by_id = {o.get("id"): o for o in building.get("openings") or []}
    assumed, warnings = [], []
    for d in model["dormers"]:
        for oid in d["serves"]:
            o = by_id.get(oid)
            if o is None:
                continue
            o.pop("dormer_refused", None)
            o["dormer"] = {"id": d["id"], "by": "architect", "source": "inferred", "reason": d["reason"]}
            ev = o.setdefault("evidence", [])
            if isinstance(ev, list):
                ev.append({"file": "dormers", "method": "inferred", "confidence": 0.7, "rule": RULE,
                           "text": d["reason"]})
        assumed.append({"object": d["id"], "field": "dormer", "kind": "dormer", "parent": d["serves"][0],
                        "by": "architect", "inferred": True, "reason": d["reason"],
                        "value": {"serves": d["serves"], "width_m": d["width_m"], "depth_m": d["depth_m"],
                                  "pitch_deg": d["pitch_deg"], "flush": d["flush"], "ceiling_m": d["ceiling_m"]}})
    for r in planned.get("refused") or []:
        o = by_id.get(r["id"])
        if o is not None:
            o["dormer_refused"] = {"reason": r["reason"], "rule": RULE}
        warnings.append(f"{r['id']}: no dormer could be raised over it: {r['reason']}")
    return assumed, warnings


def raise_dormers(building: dict, level: Optional[dict], model: Optional[dict]) -> dict:
    """``plan`` + ``apply`` for the level under the roof (the build's ``prepare``): ``{"dormers", "refused",
    "assumed", "warnings"}``. Idempotent: a level or model planned before is planned again from the bare roof."""
    out = {"dormers": [], "refused": [], "assumed": [], "warnings": []}
    if level is None or not model:
        return out
    level.pop("ceiling_dormers", None)
    model.pop("dormers", None)
    for o in building.get("openings") or []:            # a building planned before (building_built.json as input)
        if o.get("level_id") == level.get("id"):
            o.pop("dormer", None)
            o.pop("dormer_refused", None)
    planned = plan(building, level, model)
    out["assumed"], out["warnings"] = apply(building, level, model, planned)
    out["dormers"], out["refused"] = planned["dormers"], planned["refused"]
    # the building's roof record keeps them (roof.roof_model carries them over: the checks that rebuild the roof
    # from building_built.json see the dormers); a new dict, the caller's roof record is never changed
    if isinstance(building.get("roof"), dict):
        roof = {k: v for k, v in building["roof"].items() if k != "dormers"}
        if planned["dormers"]:
            roof["dormers"] = [dict(d) for d in planned["dormers"]]
        building["roof"] = roof
    return out


# ------------------------------------------------------------------------------------- the walls and the ceilings

def wall_spans(walls: Sequence[dict], dormers: Sequence[dict], main_planes: Sequence) -> dict:
    """``{wall id: [{"t0", "t1", "planes"}]}`` (``roof.wall_cut``'s ``wall_spans``: parameters 0..1 along the drawn
    centre line) for the walls whose centre line runs into a dormer's inner region: that stretch is cut by the dormer's
    underside, the rest by the main roof's (pure)."""
    from wenart.blender import roof as R

    out: dict = {}
    for w in walls:
        if not w.get("id") or not w.get("start") or not w.get("end"):
            continue
        inside = []
        for d in dormers:
            if len(d.get("inner") or []) < 3:
                continue
            for t0, t1 in R.segment_inside(w["start"][:2], w["end"][:2], d["inner"]):
                inside.append((t0, t1, [tuple(d["under"])]))
        if not inside:
            continue
        inside.sort(key=lambda s: s[0])
        spans, t = [], 0.0
        for t0, t1, planes in inside:
            if t0 > t + 1e-9:
                spans.append({"t0": round(t, 9), "t1": round(t0, 9), "planes": [tuple(p) for p in main_planes]})
            if t1 > max(t0, t) + 1e-9:
                spans.append({"t0": round(max(t0, t), 9), "t1": round(t1, 9), "planes": planes})
            t = max(t, t1)
        if t < 1.0 - 1e-9:
            spans.append({"t0": round(t, 9), "t1": 1.0, "planes": [tuple(p) for p in main_planes]})
        out[w["id"]] = spans
    return out


def room_ceiling(polygon, holes, planes, raises=()) -> tuple[list, list]:
    """``(verts, faces)`` of a room's ceiling under the roof (facing down; pure): the room minus ``holes`` on the lowest
    of ``planes`` (the sloped ceiling), with every ``raises`` region (a dormer's inner region, ``ceiling_raise``) on its
    own planes instead. Without raises: ``geom2d.sloped_faces``."""
    raises = [r for r in raises or () if isinstance(r, dict) and len(r.get("polygon") or []) >= 3 and r.get("planes")]
    holes = [h for h in holes or () if len(h) >= 3]
    if not raises:
        return geom2d.sloped_faces(polygon, holes, planes, facing_up=False)
    faces = [(geom2d.lift(poly, planes[i], False), 0)
             for i, poly in geom2d.surface_pieces(polygon, holes + [r["polygon"] for r in raises], planes)]
    pieces = geom2d.convex_pieces(polygon, holes)
    for r in raises:
        own = [tuple(p) for p in r["planes"]]
        for piece in pieces:
            part = geom2d.clip_convex(piece, r["polygon"])
            if len(part) < 3 or G.polygon_area(part) <= geom2d.MIN_PIECE_AREA:
                continue
            faces += [(geom2d.lift(poly, own[i], False), 0) for i, poly in geom2d.plane_regions(own, part)]
    verts, faces_out, _slots = geom2d.mesh_from_faces(faces)
    return verts, faces_out


# ------------------------------------------------------------------------------------------------ meshes (pure)

def _frame(d: dict):
    return tuple(d["origin"]), tuple(d["e"]), tuple(d["d"])


def meshes(d: dict, model: dict) -> tuple[list, list, list[int]]:
    """``(verts, faces, slots)`` of one dormer (module docstring; slots ``SLOT_COVER`` .. ``SLOT_FLASHING``; pure)."""
    from wenart.blender import roof as R

    top, under = [tuple(d["top"])], [tuple(d["under"])]
    gap = R.CEILING_GAP
    main_top = [tuple(e) for e in model["equations"]]
    # the cheeks and the front stand on the main roof's underside, a hair under the room's ceiling there
    bottom = [(a, b, c - 2.0 * gap) for a, b, c in R.underside(model)] + [(0.0, 0.0, float(d["flat_z"]) - gap)]
    faces: list = []
    rp = geom2d.ccw(d["roof_poly"])
    faces.append((geom2d.lift(rp, top[0], True), SLOT_COVER))
    faces.append((geom2d.lift(rp, under[0], False), SLOT_SOFFIT))
    faces += [(f, SLOT_FASCIA) for f in geom2d.side_faces(rp, top, under)]
    inner = d["inner"]
    for poly in list(d.get("cheeks") or []) + ([d["front"]] if d.get("front") else []):
        loop = geom2d.ccw(poly)
        faces += [(geom2d.lift(pc, bottom[i], False), SLOT_SOFFIT) for i, pc in geom2d.surface_pieces(loop, [], bottom)]
        faces.append((geom2d.lift(loop, under[0], True), SLOT_CLAD))
        n = len(loop)
        for i in range(n):
            p, q = loop[i], loop[(i + 1) % n]
            length = G.distance(p, q)
            if length < 1e-9:
                continue
            nx, ny = (q[1] - p[1]) / length, -(q[0] - p[0]) / length         # the right normal: out of the solid
            m = ((p[0] + q[0]) / 2.0 + nx * 0.01, (p[1] + q[1]) / 2.0 + ny * 0.01)
            slot = SLOT_SOFFIT if G.point_in_polygon(m, inner) else SLOT_CLAD
            faces += [(f, slot) for f in geom2d.segment_side_faces(p, q, under, bottom)]
    faces += [(f, SLOT_FLASHING) for f in flashing_faces(d, main_top)]
    return geom2d.mesh_from_faces(faces)


def flashing_faces(d: dict, main_top: Sequence) -> list:
    """The flashing faces (pure): strips on the main roof along both cheeks and behind the dormer (and in front of a
    set-back front), ``flashing_t_m`` over the covering, with an upstand ``upstand_m`` high against each cheek."""
    o, ev, dv = _frame(d)
    fw, ft, up = DORMER["flashing_w_m"], DORMER["flashing_t_m"], DORMER["upstand_m"]
    raised = [(a, b, c + ft) for a, b, c in main_top]
    raised_up = [(a, b, c + ft + up) for a, b, c in main_top]
    e0, e1, db, df = float(d["e0"]), float(d["e1"]), float(d["d_back"]), float(d["d_front"])
    strips = [_rect(o, ev, dv, e0 - fw, e0, db, df), _rect(o, ev, dv, e1, e1 + fw, db, df),
              _rect(o, ev, dv, e0 - fw, e1 + fw, db - fw, db)]
    if not d.get("flush"):
        strips.append(_rect(o, ev, dv, e0 - fw, e1 + fw, df, df + fw))
    out = []
    for s in strips:
        out += [geom2d.lift(pc, raised[i], True) for i, pc in geom2d.surface_pieces(s, [], raised)]
    eps = 0.003
    out += geom2d.segment_side_faces(_pt(o, ev, dv, e0 - eps, db), _pt(o, ev, dv, e0 - eps, df), raised_up, raised)
    out += geom2d.segment_side_faces(_pt(o, ev, dv, e1 + eps, df), _pt(o, ev, dv, e1 + eps, db), raised_up, raised)
    return out


# ---------------------------------------------------------------------------------------------- looks and records

def looks_of(d: dict, looks: Optional[dict] = None) -> dict:
    """The looks of a dormer's parts (pure): ``cover`` (standing-seam metal under ``tile_min_pitch_deg``, else the
    roof's covering), ``clad`` (the facade's look: the cheeks and a set-back front), ``flashing``. Every look a
    vocabulary slug, ``inferred`` with its reason."""
    looks = looks or {}
    base = {"source": "build", "assumed": True, "inferred": True}
    if d.get("pitch_deg", 0.0) < DORMER["tile_min_pitch_deg"] or not isinstance(looks.get("roof"), dict):
        m, c, why = DORMER_LOOKS["cover_metal"]
        cover = dict(base, material=m, colour=c, reason=why)
    else:
        cover = dict(base, **{k: looks["roof"].get(k) for k in ("material", "colour", "rgb", "asset", "params")
                              if looks["roof"].get(k)}, reason="the dormer roof in the main roof's covering")
    facade = looks.get("facade") if isinstance(looks.get("facade"), dict) else {"material": "render",
                                                                                "colour": "white"}
    clad = dict(base, **{k: facade.get(k) for k in ("material", "colour", "rgb", "asset", "params") if facade.get(k)},
                reason="the dormer's cheeks and front in the house's facade look")
    m, c, why = DORMER_LOOKS["flashing"]
    return {"cover": cover, "clad": clad, "flashing": dict(base, material=m, colour=c, reason=why)}


def manifest_record(d: dict) -> dict:
    """The dormer's record in the scene manifest (pure)."""
    keys = ("id", "serves", "kinds", "level_id", "flush", "pitch_deg", "head_clear_m", "width_m", "depth_m",
            "front_top_z", "ceiling_m", "footprint", "hole", "inner", "top", "under", "reason", "by", "source", "rule")
    return {k: d.get(k) for k in keys if d.get(k) is not None}


def summary(model: Optional[dict], refused: Sequence[dict] = ()) -> Optional[dict]:
    """The dormers for the scene manifest's ``whole_building.dormers`` (pure); None without any (and none refused)."""
    ds = list((model or {}).get("dormers") or [])
    if not ds and not refused:
        return None
    return {"dormers": [{k: d.get(k) for k in ("id", "serves", "flush", "pitch_deg", "width_m", "depth_m",
                                                "ceiling_m", "reason")} for d in ds],
            "refused": list(refused)}


def build_dormers(model: dict, collection, looks: Optional[dict], make_material, roof_materials: Sequence,
                  manifest_objects: list, assumed: list, refused: Sequence[dict] = ()) -> Optional[dict]:
    """One object per dormer of ``model`` (kind ``roof``, detail ``dormer``, status ``assumed``) with five material
    slots (cover, the roof's soffit, the roof's fascia, the facade cladding, the flashing); its manifest record and its
    looks' ``assumed`` row (the dormer itself is listed by ``raise_dormers``). Returns ``summary`` (bpy)."""
    from wenart.blender import common

    for d in model.get("dormers") or []:
        lk = looks_of(d, looks)
        soffit = roof_materials[1] if len(roof_materials) > 1 else None
        fascia = roof_materials[2] if len(roof_materials) > 2 else None
        mats = [make_material(lk["cover"]), soffit, fascia, make_material(lk["clad"]), make_material(lk["flashing"])]
        mats = [m if m is not None else mats[0] for m in mats]
        verts, faces, slots = meshes(d, model)
        ob = common.new_mesh_object(d["id"], verts, faces, collection=collection, wenart_id=d["id"], kind="roof",
                                    status="assumed", materials=mats, face_material_indices=slots)
        manifest_objects.append({
            "name": ob.name, "wenart_id": d["id"], "kind": "roof", "status": "assumed", "level_id": d.get("level_id"),
            "element_id": d["id"], "evidence": [], "material": mats[0].name if mats[0] is not None else None,
            "textured": False, "pass_index": None, "detail": "dormer", "source": "inferred", "inferred": True,
            "serves": list(d["serves"]),
            "assumed": {"detail": "dormer", "reason": d["reason"], "inferred": True, "by": "architect"},
            "looks": {k: {"material": v.get("material"), "colour": v.get("colour")} for k, v in lk.items()},
            "dormer": manifest_record(d)})
        assumed.append({"object": d["id"], "field": "dormer_looks", "kind": "dormer", "parent": d["id"],
                        "value": {k: v.get("material") for k, v in lk.items()},
                        "reason": "; ".join(v["reason"] for v in lk.values())})
    return summary(model, refused)
