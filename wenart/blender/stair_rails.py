"""Stair handrails, balustrades and structure as one designed stair (pure; 28 Oct 2026).

User on real04's stairs (28 Oct 2026): "There should have been better indoor stair solutions should be there I did not
like this one". The corridor view (cam_r_L0_koridor_1): oak treads, a glass balustrade with a steel top rail and other
steel rails at different angles crossing each other near the well. Measured: every flight side not against a wall got
its own straight rail 0.90 m over its nosings (``parametric.stair_plan`` "rails"), so at a U stair the rails stopped
at odd heights on both sides of the well, nothing guarded the winders or the half landing at the well, the rail of
the last flight ran up beside the floor guard of the level above (two guards 8 cm apart at different slopes), and the
steps stood on a 0.15 m waist slab even where the stair stands free over a void.

What (every stair: straight, L, U, with winders, a landing or an apron at the top):

- ``side_paths(plan, wall_rects)``: per climbing side (the climber's left and right) the stair's edge as one path: the
  first flight's side, the edge of the landing or the winders on that side (the well side: the short way round, the
  outer side: the long way), the next flight's side; every leg is open or against a wall (the probe of
  ``parametric.STAIR_WALL_PROBE``).
- ``stair_design(style, kind)``: the stair's look from the house's style family (``wenart.style.vocabulary``) and
  balustrade kind (``details.balustrade_kind``, one language with the stairwell guards and the balconies): the
  structure (``solid``: the waist slab; ``plate``: a thin folded-plate soffit with steel plate strings, modern and
  minimal; ``stringer``: slim closed strings with a soffit flush with them, scandinavian, japandi, industrial), the
  infill (frameless glass with a steel or timber cap, glass between slim posts, slim steel bars, timber slats, turned
  or square timber balusters, wrought bars) and the handrail (round steel, rounded timber).
- ``plan_guards(plan, ceiling_voids=, upper_guards=)``: one continuous balustrade on every open stretch of a side:
  the handrail ``parametric.STAIR_RAIL_HEIGHT`` over the nosing line (``LEVEL_GUARD_M`` along a level edge: a landing,
  an apron), a newel post at every turn and at both ends (the rails die into it, no rail crosses another), the infill
  under it with no gap of ``GAP_MAX_M`` or more, on the string where the stair has one; a wall handrail on brackets
  with returns into the wall along the wall side where a flight is wider than ``TWO_RAILS_WIDTH_M`` or a flight would
  have no handrail; nothing through a tread, a wall or the floor above: under the slab every part stays under it,
  beside the floor guard of the level above (``upper_guards``) the stair's handrail stops at that floor and its infill
  closes up to it (the floor guard takes over, ``TAKEOVER_M``), in a capped shaft everything stays under the cap.
- ``guard_parts(guards)`` / ``string_parts(guards)``: the meshes ``parametric.stair_parts`` adds.
- ``review(guards, plan, ...)``: the checks of the model review's M15 (rails that cross, stop short, stand at the wrong
  height, run through a tread, a wall or the floor above, sit beside a floor guard; infill gaps); ``legacy_guards``
  reads the rails of a scene built before this module (one straight rail per open flight side) for the same review.

Why: a stair is the one piece of a house a visitor holds on to; a designer draws its balustrade as one line that
follows the flights and turns at newels, never as separate bars. Every rule here is general (every stair of every
project); real04's U stairs with winders are the test case.

How: plain Python on the plan dicts of ``parametric.stair_plan`` (no shapely: the module runs inside Blender too).
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G
from wenart.blender import geom2d

# --------------------------------------------------------------------------
# Dimensions (metres)
# --------------------------------------------------------------------------
NEWEL_M = 0.07                  # a newel post, square (the balustrade's line runs through its centre)
NEWEL_CAP_M = 0.04              # a newel rises this far over the highest rail that dies into it
LINE_IN_M = NEWEL_M / 2.0       # the balustrade's line this far inside the stair's edge: posts stay on the stair
FOOT_POST_M = 0.065             # the starting newel's centre this far up the first tread (all of it on the tread)
TOP_POST_M = 0.045              # the top newel's centre this far back from the last nosing (on the last tread)
TURN_DEG = 1.0                  # a joint of two legs that turns more than this is a corner (a newel there)
REVERSAL_DEG = 150.0            # ... more than this is a reversal (a dog-leg stair: one newel on the divider)
SHORT_LEG_M = 0.6               # a leg between two newels shorter than this has a level rail (the well of a U stair)
LEVEL_GUARD_M = 1.00            # a balustrade along a level edge (a landing, an apron) is a guard: 1.0 m
RAIL_FLIGHT_RANGE = (0.85, 1.10)    # a handrail's top over the nosing line on a flight (the review's M15)
TWO_RAILS_WIDTH_M = 1.00        # a flight wider than this gets a handrail on both sides (a wall rail on brackets)
HELD_SHARE = 0.5                # a flight whose handrails cover less than this share of its run gets a wall rail
RAIL_MIN_M = 0.30               # a cut rail shorter than this is left out (the infill stays)
GAP_MAX_M = 0.11                # no gap of an infill lets a sphere of this size through
GAP_DESIGN_M = 0.10             # the clear gap the balusters are spaced for (under GAP_MAX_M)
GLASS_T = 0.012
GLASS_PANEL_MAX_M = 1.6         # longer legs get several panels
GLASS_END_GAP_M = 0.01          # glass to a newel's face and between two panels
GLASS_STRING_OVERLAP_M = 0.03   # glass fixed to the inner face of the string over this height
POST_EVERY_M = 1.2              # glass between posts (``glass_posts``): an intermediate slim post at most this apart
SLIM_POST_M = 0.042
TAKEOVER_M = 0.30               # a floor guard of the level above this near (in plan) and along the rail takes over
TAKEOVER_COS = 0.9
CLEAR_M = 0.03                  # rails and posts stay this far under a ceiling, a slab or a cap
INFILL_CLEAR_M = 0.003          # infill and strings stay this far under it (no coplanar faces)
EDGE_MARGIN_M = 0.02            # a part's line this far inside a floor opening of the level above is in it
WALL_RAIL_GAP_M = 0.06          # a wall handrail's clear gap to the wall
BRACKET_EVERY_M = 1.0
BRACKET_R = 0.008
STRING_UP_M = 0.05              # a string's top over the nosing line (a closed string: it hides the tread ends)
STRING_T = {"plate": 0.03, "stringer": 0.05, "solid": 0.05}
PLATE_M = 0.05                  # the plate structure under the steps, square to the pitch
STRINGER_DEPTH_M = 0.25         # a stringer's depth, square to the pitch
WINDER_PLATE_M = 0.06           # a winder of a light stair over a void: tread and plate together
WINDER_RISER_T = 0.02
SAMPLE_M = 0.02                 # rails are sampled this often for the caps and the review
APRON_LEG_MIN_M = 0.10          # an apron at the top at least this deep has its own guard along its open sides

# --------------------------------------------------------------------------
# The look per style family (wenart.style.vocabulary.STYLE_FAMILIES; details.STYLE_KINDS for the language)
# --------------------------------------------------------------------------
STRUCTURES = ("solid", "plate", "stringer")
# family -> structure, string slot ("steel", "structure": the wall paint, "timber"), the balusters a "bars" house
# gets, the handrail
FAMILY_DESIGN = {
    "modern": {"structure": "plate", "string": "steel", "bars": "bars", "rail": "steel"},
    "minimal": {"structure": "plate", "string": "steel", "bars": "bars", "rail": "steel"},
    "modern minimal": {"structure": "plate", "string": "steel", "bars": "bars", "rail": "steel"},
    "contemporary": {"structure": "plate", "string": "steel", "bars": "bars", "rail": "timber"},
    "scandinavian": {"structure": "stringer", "string": "structure", "bars": "bars", "rail": "timber"},
    "japandi": {"structure": "stringer", "string": "timber", "bars": "slats", "rail": "timber"},
    "industrial": {"structure": "stringer", "string": "steel", "bars": "bars", "rail": "steel"},
    "classic": {"structure": "solid", "string": "structure", "bars": "turned", "rail": "timber"},
    "rustic": {"structure": "solid", "string": "timber", "bars": "square_timber", "rail": "timber"},
    "mediterranean": {"structure": "solid", "string": "structure", "bars": "wrought", "rail": "steel"},
}
DEFAULT_DESIGN = {"structure": "solid", "string": "structure", "bars": "bars", "rail": "steel"}
RAILS = {"steel": {"r": 0.022, "sides": 12, "key": "steel"}, "timber": {"r": 0.028, "sides": 8, "key": "timber"}}
# baluster kinds: width along the run, depth across, key, shape
BALUSTERS = {"bars": {"w": 0.016, "d": 0.016, "key": "steel", "shape": "square"},
             "slats": {"w": 0.04, "d": 0.022, "key": "timber", "shape": "square", "gap": 0.06},
             "square_timber": {"w": 0.035, "d": 0.035, "key": "timber", "shape": "square"},
             "turned": {"w": 0.042, "d": 0.042, "key": "timber", "shape": "turned"},
             "wrought": {"w": 0.014, "d": 0.014, "key": "steel", "shape": "wrought"}}
STRING_KEYS = {"steel": "steel", "structure": "worktop", "timber": "timber"}
GLASS_KINDS = ("glass_channel", "glass_posts")


def stair_design(style: Optional[dict] = None, kind: Optional[str] = None) -> dict:
    """The stair's look (module docstring): ``{"family", "kind", "structure", "infill", "posts_every", "rail",
    "newel_key", "string", "string_t", "string_key", "why"}``. ``kind`` (a ``details.KINDS`` balustrade) defaults to
    the house's (``details.balustrade_kind(style)``), without a style to ``parametric.STAIR_BALUSTRADE_DEFAULT``."""
    from wenart.blender import details as D
    from wenart.blender import parametric as P

    family = str((style or {}).get("family") or "").lower() or None
    if kind is None:
        kind = D.balustrade_kind(style) if style else P.STAIR_BALUSTRADE_DEFAULT
    fam = FAMILY_DESIGN.get(family or "", DEFAULT_DESIGN)
    glass = kind in GLASS_KINDS
    infill = "glass" if glass else fam["bars"]
    rail = dict(RAILS[fam["rail"]])
    structure = fam["structure"]
    string = structure != "solid" or glass
    newel_key = "steel" if glass or fam["rail"] == "steel" else "timber"
    why = (f"{family or 'no style family'}: {structure} structure, {infill.replace('_', ' ')} "
           f"{'panels' if glass else 'balusters'} under a {fam['rail']} handrail"
           + (f", {fam['string']} strings" if string else "") + f" ({kind.replace('_', ' ')} language of the house)")
    return {"family": family, "kind": kind, "structure": structure, "infill": infill,
            "posts_every": POST_EVERY_M if kind == "glass_posts" else None, "rail": rail, "newel_key": newel_key,
            "string": string, "string_t": STRING_T[structure], "string_key": STRING_KEYS[fam["string"]], "why": why}


def plan_design(plan: dict) -> dict:
    """The design a plan is built with: ``plan["design"]`` (``shell.build_stairs``: the house's style), else the
    plain design of its ``balustrade`` kind."""
    d = plan.get("design")
    if isinstance(d, dict) and d.get("structure") in STRUCTURES:
        return d
    return stair_design(None, plan.get("balustrade"))


def structure_of(plan: dict) -> str:
    """The structure a plan is built with: ``plan["structure"]`` when set (the scene manifest's record, read back by
    the model review), else its design's (``solid`` without a style)."""
    if plan.get("structure") in STRUCTURES:
        return plan["structure"]
    return plan_design(plan)["structure"]


def flight_waist(plan: dict, f: dict) -> tuple[float, float]:
    """``(k, t_v)`` of a planned flight (pure): the soffit's rise per metre of going and the depth of the structure
    under the root line (the inner corners of the steps), measured vertically: ``solid`` the
    ``parametric.STAIR_WAIST_M`` waist square to the soffit, ``plate`` ``PLATE_M``, ``stringer`` down to the
    stringers' bottom (``STRINGER_DEPTH_M`` square to the pitch from ``STRING_UP_M`` over the nosings). The steps,
    the strings and the spandrel panels under the stair (``stair_access.under_parts``) use it."""
    from wenart.blender import parametric as P

    riser = float(plan["riser_m"])
    k = riser / max(float(f["going"]), 1e-6)
    sq = math.sqrt(1.0 + k * k)
    structure = structure_of(plan)
    if structure == "plate":
        return k, PLATE_M * sq
    if structure == "stringer":
        return k, max(PLATE_M * sq, STRINGER_DEPTH_M * sq - riser - STRING_UP_M)
    return k, P.STAIR_WAIST_M * sq


# --------------------------------------------------------------------------
# Small geometry
# --------------------------------------------------------------------------

def _sub(a, b):
    return (float(a[0]) - float(b[0]), float(a[1]) - float(b[1]))


def _add(a, b, s: float = 1.0):
    return (float(a[0]) + float(b[0]) * s, float(a[1]) + float(b[1]) * s)


def _dot(a, b) -> float:
    return float(a[0]) * float(b[0]) + float(a[1]) * float(b[1])


def _cross(a, b) -> float:
    return float(a[0]) * float(b[1]) - float(a[1]) * float(b[0])


def _unit(v):
    n = math.hypot(float(v[0]), float(v[1]))
    return (0.0, 0.0) if n < 1e-12 else (float(v[0]) / n, float(v[1]) / n)


def _lerp(a, b, t: float):
    return tuple(float(a[i]) + (float(b[i]) - float(a[i])) * t for i in range(len(a)))


def _r(v, nd: int = 4):
    return [round(float(c), nd) for c in v]


def seg_dist3(p1, q1, p2, q2) -> float:
    """The shortest distance between the 3D segments ``p1``-``q1`` and ``p2``-``q2``."""
    d1 = [q1[i] - p1[i] for i in range(3)]
    d2 = [q2[i] - p2[i] for i in range(3)]
    r = [p1[i] - p2[i] for i in range(3)]
    a = sum(c * c for c in d1)
    e = sum(c * c for c in d2)
    f = sum(d2[i] * r[i] for i in range(3))
    if a < 1e-12 and e < 1e-12:
        return math.dist(p1, p2)
    if a < 1e-12:
        s, t = 0.0, min(max(f / e, 0.0), 1.0)
    else:
        c = sum(d1[i] * r[i] for i in range(3))
        if e < 1e-12:
            s, t = min(max(-c / a, 0.0), 1.0), 0.0
        else:
            b = sum(d1[i] * d2[i] for i in range(3))
            den = a * e - b * b
            s = min(max((b * f - c * e) / den, 0.0), 1.0) if den > 1e-12 else 0.0
            t = (b * s + f) / e
            if t < 0.0:
                t, s = 0.0, min(max(-c / a, 0.0), 1.0)
            elif t > 1.0:
                t, s = 1.0, min(max((b - c) / a, 0.0), 1.0)
    c1 = [p1[i] + d1[i] * s for i in range(3)]
    c2 = [p2[i] + d2[i] * t for i in range(3)]
    return math.dist(c1, c2)


def _in_poly(p, poly, margin: float = 0.0) -> bool:
    return G.point_in_polygon(p, poly) and (margin <= 0.0 or geom2d.distance_to_polygon_edges(p, poly) >= margin)


def _boundary_pos(poly, p) -> tuple[float, int]:
    """``(arc-length position, edge)`` of the boundary point of the counter-clockwise ``poly`` nearest ``p``."""
    best, pos, run = None, 0.0, 0.0
    n = len(poly)
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        t = 0.0 if length < 1e-12 else min(max(_dot(_sub(p, a), _sub(b, a)) / (length * length), 0.0), 1.0)
        d = G.distance(p, _lerp(a, b, t))
        if best is None or d < best[0] - 1e-12:
            best = (d, run + t * length, i)
        run += length
    return best[1], best[2]


def _point_at(poly, cum, pos: float):
    per = cum[-1]
    pos = pos % per if per > 0 else 0.0
    for i in range(len(poly)):
        if pos <= cum[i + 1] + 1e-12:
            length = cum[i + 1] - cum[i]
            t = 0.0 if length < 1e-12 else (pos - cum[i]) / length
            return _lerp(poly[i], poly[(i + 1) % len(poly)], t)
    return tuple(poly[0])


def boundary_arc(poly, p, q, short: bool) -> list:
    """The points from ``p`` to ``q`` along the boundary of the convex counter-clockwise ``poly`` (both projected on
    it), the shorter way round (``short``) or the longer; with the corners passed."""
    n = len(poly)
    cum = [0.0]
    for i in range(n):
        cum.append(cum[-1] + G.distance(poly[i], poly[(i + 1) % n]))
    per = cum[-1]
    sp, _ = _boundary_pos(poly, p)
    sq, _ = _boundary_pos(poly, q)
    fwd = (sq - sp) % per
    go_fwd = (fwd <= per - fwd) if short else (fwd > per - fwd)
    span = fwd if go_fwd else per - fwd
    pts = [_point_at(poly, cum, sp)]
    corners = sorted(((c - sp) % per if go_fwd else (sp - c) % per, c) for c in cum[:-1])
    for d, c in corners:
        if 1e-6 < d < span - 1e-6:
            pts.append(_point_at(poly, cum, c))
    pts.append(_point_at(poly, cum, sq))
    return pts


def _edge_normal(poly, a, b):
    """The outward normal of the edge of the counter-clockwise ``poly`` that holds the segment ``a``-``b``."""
    mid = G.segment_midpoint(a, b)
    _pos, i = _boundary_pos(poly, mid)
    p, q = poly[i], poly[(i + 1) % len(poly)]
    d = _unit(_sub(q, p))
    return (d[1], -d[0])


# --------------------------------------------------------------------------
# The flights, the treads under a point
# --------------------------------------------------------------------------

def flight_frame(f: dict, riser: float) -> dict:
    """The frame of a planned flight: ``o`` (its first nosing's centre), ``r`` (the rise), ``pl`` (left of it),
    ``hw``, ``L`` (first to last nosing), ``g``, ``n``, ``k``, ``base``, ``top``, ``index``."""
    r = (float(f["rise_dir"][0]), float(f["rise_dir"][1]))
    n, g = int(f["lines"]), float(f["going"])
    return {"o": (float(f["nosings"][0][0]), float(f["nosings"][0][1])), "r": r, "pl": (-r[1], r[0]),
            "hw": float(f["width"]) / 2.0, "L": (n - 1) * g, "g": g, "n": n, "k": riser / max(g, 1e-9),
            "base": float(f["base_z"]), "top": float(f["top_z"]), "index": f["index"], "riser": riser}


def _edge_point(fr: dict, s: float, sign: float, q: float = 0.0):
    off = sign * (fr["hw"] - q)
    return (fr["o"][0] + fr["r"][0] * s + fr["pl"][0] * off, fr["o"][1] + fr["r"][1] * s + fr["pl"][1] * off)


def nose(fr: dict, s: float) -> float:
    """The nosing line of a flight over its run ``s`` (clamped to its first and last nosing)."""
    return fr["base"] + fr["riser"] + min(max(s, 0.0), fr["L"]) * fr["k"]


def tread_top(fr: dict, s: float) -> float:
    """The top of the tread (or the landing) a point ``s`` along the flight stands on."""
    if s < 0.0:
        return fr["base"]
    i = min(fr["n"] - 1, int(s / fr["g"] + 1e-9)) + 1
    return fr["base"] + i * fr["riser"]


def _s_of(fr: dict, p) -> float:
    return _dot(_sub(p, fr["o"]), fr["r"])


def _q_of(fr: dict, p) -> float:
    return _dot(_sub(p, fr["o"]), fr["pl"])


def surface_z(plan: dict, p, frames: Optional[list] = None) -> Optional[float]:
    """The top of the stair under plan point ``p`` (a tread, a winder, the landing, the apron), None over none."""
    frames = frames if frames is not None else [flight_frame(f, float(plan["riser_m"])) for f in plan["flights"]]
    land = plan.get("landing") or {}
    for w in land.get("winders") or []:
        if G.point_in_polygon(p, w["polygon"]):
            return float(w["top"])
    if land.get("role") in ("mid", "top") and G.point_in_polygon(p, land["polygon"]):
        return float(land["z"])
    for fr in frames:
        s, q = _s_of(fr, p), _q_of(fr, p)
        if abs(q) <= fr["hw"] + 1e-3 and -0.03 <= s <= fr["L"] + 1e-6:
            return tread_top(fr, s)
    apron = float(plan.get("top_apron") or 0.0)
    if apron > 0 and frames:
        fr = frames[-1]
        s, q = _s_of(fr, p), _q_of(fr, p)
        if abs(q) <= fr["hw"] + 1e-3 and fr["L"] - 1e-6 <= s <= fr["L"] + apron + 1e-6:
            return float(plan["rise_m"])
    return None


def _winder_top(plan: dict, p) -> float:
    land = plan.get("landing") or {}
    best = None
    for w in land.get("winders") or []:
        if G.point_in_polygon(p, w["polygon"]):
            return float(w["top"])
        d = geom2d.distance_to_polygon_edges(p, w["polygon"])
        if best is None or d < best[0]:
            best = (d, float(w["top"]))
    return best[1] if best else float(land.get("z") or 0.0)


# --------------------------------------------------------------------------
# The side paths
# --------------------------------------------------------------------------

def wall_rects_near(plan_or_points, walls: Sequence[dict], reach: float = 1.5) -> list[list]:
    """The rectangles of the ``walls`` within ``reach`` of the stair (its flights' nosings and its landing)."""
    pts = list(plan_or_points)
    if not pts:
        return []
    x0, y0 = min(p[0] for p in pts) - reach, min(p[1] for p in pts) - reach
    x1, y1 = max(p[0] for p in pts) + reach, max(p[1] for p in pts) + reach
    out = []
    for w in walls or ():
        if G.distance(w["start"], w["end"]) <= 1e-9:
            continue
        rect = G.centerline_to_rectangle(w["start"], w["end"], float(w["thickness"]))
        if max(p[0] for p in rect) < x0 or min(p[0] for p in rect) > x1 or max(p[1] for p in rect) < y0 \
                or min(p[1] for p in rect) > y1:
            continue
        out.append([[round(float(p[0]), 5), round(float(p[1]), 5)] for p in rect])
    return out


def _against_wall(a, b, out, wall_rects, probe: float) -> bool:
    pts = [_add(_lerp(a, b, t), out, probe) for t in (0.25, 0.5, 0.75)]
    return sum(1 for q in pts if any(G.point_in_polygon(q, rect) for rect in wall_rects)) >= 2


def turn_sign(plan: dict) -> float:
    """+1 when the stair turns left from its first flight to its second, -1 right, 0 without a second flight."""
    fl = plan.get("flights") or []
    if len(fl) < 2:
        return 0.0
    riser = float(plan["riser_m"])
    a, b = flight_frame(fl[0], riser), flight_frame(fl[1], riser)
    c1 = _add(a["o"], a["r"], a["L"])
    d = _dot(a["pl"], _sub(b["o"], c1))
    if abs(d) < 1e-6:
        d = _cross(a["r"], b["r"])
    return 1.0 if d > 0 else -1.0


def side_paths(plan: dict, wall_rects: Sequence = ()) -> list[dict]:
    """The two climbing sides of a planned stair (module docstring): ``[{"side": "left" | "right", "sign": +1 | -1,
    "inner": True on the well side of a turning stair, "legs": [{"what": "flight" | "landing" | "winders" | "apron" |
    "top", "flight", "a", "b" (the edge, climbing order), "out" (the outward normal), "z" (a level leg), "wall"}]}]``.
    The apron at the top (``top_apron``) and the edges of a top landing are legs of the last flight's sides."""
    from wenart.blender import parametric as P

    flights = plan.get("flights") or []
    riser = float(plan["riser_m"])
    frames = [flight_frame(f, riser) for f in flights]
    land = plan.get("landing") or None
    turn = None
    if land and land.get("role") in ("mid", "winders") and len(frames) >= 2 and len(land.get("polygon") or []) >= 3:
        turn = geom2d.ccw([(float(p[0]), float(p[1])) for p in land["polygon"]])
    tau = turn_sign(plan)
    out = []
    for sign, name in ((1.0, "left"), (-1.0, "right")):
        legs: list[dict] = []
        for i, fr in enumerate(frames):
            a, b = _edge_point(fr, 0.0, sign), _edge_point(fr, fr["L"], sign)
            legs.append({"what": "flight", "flight": fr["index"], "a": a, "b": b,
                         "out": (fr["pl"][0] * sign, fr["pl"][1] * sign)})
            if i == 0 and turn is not None:
                what = "winders" if land["role"] == "winders" else "landing"
                nxt = _edge_point(frames[1], 0.0, sign)
                pts = boundary_arc(turn, b, nxt, short=(sign == tau))
                # the path joins the flights' corners exactly (a drawn line may stand a little off the landing's edge)
                pts[0], pts[-1] = b, nxt
                for u, w in zip(pts, pts[1:]):
                    if G.distance(u, w) > 1e-4:
                        legs.append({"what": what, "flight": None, "a": u, "b": w, "out": _edge_normal(turn, u, w),
                                     "z": float(land["z"])})
        if frames:
            fr = frames[-1]
            apron = float(plan.get("top_apron") or 0.0)
            end = _edge_point(fr, fr["L"], sign)
            if apron >= APRON_LEG_MIN_M:                     # a shorter apron is the top newel's place
                legs.append({"what": "apron", "flight": None, "a": end, "b": _add(end, fr["r"], apron),
                             "out": (fr["pl"][0] * sign, fr["pl"][1] * sign), "z": float(plan["rise_m"])})
            elif land and land.get("role") == "top" and len(land.get("polygon") or []) >= 3:
                legs += _top_legs(geom2d.ccw(land["polygon"]), end, fr, sign, float(land["z"]))
        for leg in legs:
            leg["wall"] = bool(wall_rects) and _against_wall(leg["a"], leg["b"], leg["out"], wall_rects,
                                                             P.STAIR_WALL_PROBE)
        out.append({"side": name, "sign": sign, "inner": (sign == tau) if turn is not None else None, "legs": legs})
    return out


def _top_legs(poly, start, fr: dict, sign: float, z: float) -> list[dict]:
    """The edges of a top landing on one side of the climber: from the last nosing's corner along the landing's
    boundary on that side to its far end."""
    side = (fr["pl"][0] * sign, fr["pl"][1] * sign)
    far = max(_dot(p, fr["r"]) for p in poly)
    n = len(poly)
    cum = [0.0]
    for i in range(n):
        cum.append(cum[-1] + G.distance(poly[i], poly[(i + 1) % n]))
    sp, _ = _boundary_pos(poly, start)
    best = None
    for direction in (1.0, -1.0):
        nxt = _point_at(poly, cum, sp + direction * 0.05)
        score = _dot(_unit(_sub(nxt, start)), side) + _dot(_unit(_sub(nxt, start)), fr["r"])
        if best is None or score > best[0]:
            best = (score, direction)
    direction = best[1]
    pts = [_point_at(poly, cum, sp)]
    corners = sorted(((c - sp) % cum[-1] if direction > 0 else (sp - c) % cum[-1], c) for c in cum[:-1])
    for d, c in corners:
        if d <= 1e-6:
            continue
        p = _point_at(poly, cum, c)
        pts.append(p)
        if _dot(p, fr["r"]) >= far - 0.01:
            break
    legs = []
    for u, w in zip(pts, pts[1:]):
        if G.distance(u, w) > 1e-4:
            legs.append({"what": "top", "flight": None, "a": u, "b": w, "out": _edge_normal(poly, u, w), "z": z})
    return legs


# --------------------------------------------------------------------------
# Insets: the balustrade's line and the wall rail's line
# --------------------------------------------------------------------------

def _interior(leg: dict, sign: float):
    d = _unit(_sub(leg["b"], leg["a"]))
    return d, (d[1] * sign, -d[0] * sign)


def _turn_deg(d1, d2) -> float:
    return abs(math.degrees(math.atan2(_cross(d1, d2), _dot(d1, d2))))


def inset_legs(legs: list[dict], sign: float, q: float) -> list[dict]:
    """Every leg's line ``q`` inside the stair (``A``, ``B``), consecutive legs meeting at their corner (a miter);
    ``joint`` after each leg: ``None`` (no next leg or not joined), ``"straight"``, ``"corner"`` or ``"reversal"``
    (a dog-leg's turn: the two lines end ``q`` either side of the divider)."""
    out = []
    for leg in legs:
        d, n = _interior(leg, sign)
        out.append({"A": _add(leg["a"], n, q), "B": _add(leg["b"], n, q), "d": d, "n": n, "joint": None})
    for i in range(len(legs) - 1):
        if G.distance(legs[i]["b"], legs[i + 1]["a"]) > 1e-3:
            continue
        a, b = out[i], out[i + 1]
        turn = _turn_deg(a["d"], b["d"])
        if turn > REVERSAL_DEG:
            a["joint"] = "reversal"
            continue
        if turn < TURN_DEG:
            a["joint"] = "straight"
            continue
        den = _cross(a["d"], b["d"])
        t = _cross(_sub(b["A"], a["A"]), b["d"]) / den
        m = _add(a["A"], a["d"], t)
        a["B"], b["A"], a["joint"] = m, m, "corner"
    return out


# --------------------------------------------------------------------------
# Caps: the slab, the floor guard of the level above, the shaft's cap
# --------------------------------------------------------------------------

def _context(plan: dict, ceiling_voids=None, upper_guards=(), upper_walls=None) -> dict:
    """What limits the parts from above (module docstring); ``upper_walls``: the wall rectangles of the level above
    (default ``plan["upper_wall_rects"]``: a wall handrail goes on up where its wall does)."""
    riser = float(plan["riser_m"])
    if ceiling_voids is not None:
        openings = [geom2d.ccw([(float(p[0]), float(p[1])) for p in v]) for v in ceiling_voids if len(v) >= 3]
    else:
        openings = [geom2d.ccw([(float(p[0]), float(p[1])) for p in v]) for v in plan.get("void") or [] if len(v) >= 3]
    if plan.get("rail_limit") is not None:           # the stair comes up through the floor above: its guard height
        top_open = max(float(plan["rail_limit"]), float(plan["rise_m"]) + LEVEL_GUARD_M) + CLEAR_M
    else:
        top_open = float(plan["cap_z"])
    return {"openings": openings, "ceiling": float(plan["ceiling_z"]), "top_open": top_open,
            "rise": float(plan["rise_m"]), "cap": float(plan["cap_z"]),
            "guards": [((float(p[0]), float(p[1])), (float(q[0]), float(q[1]))) for p, q in upper_guards or ()
                       if G.distance(p, q) > 1e-6],
            "upper_walls": list(plan.get("upper_wall_rects") or []) if upper_walls is None else list(upper_walls),
            "frames": [flight_frame(f, riser) for f in plan.get("flights") or []]}


def taken_over(ctx: dict, p, d) -> bool:
    """True where a floor guard of the level above runs within ``TAKEOVER_M`` of plan point ``p`` along ``d``."""
    for a, b in ctx["guards"]:
        u = _unit(_sub(b, a))
        if abs(_dot(u, d)) >= TAKEOVER_COS and G.point_segment_distance(p, a, b) <= TAKEOVER_M:
            return True
    return False


def cap_at(ctx: dict, p, d, part: str = "rail", out=None) -> tuple[float, str]:
    """``(z, why)``: how high a part (``rail``, ``post``, ``infill``, ``wall``) at plan point ``p`` (running along
    ``d``) may reach: under the slab of the level above its underside, inside its floor opening the top (the stair
    that arrives through it, or the shaft's cap), beside its floor guard that floor's level; less the clearance (the
    infill closes up to a slab or a floor: ``INFILL_CLEAR_M`` there). A wall rail (``out``: towards its wall) stops
    under the cap unless its wall goes on up on the level above."""
    close = INFILL_CLEAR_M if part == "infill" else CLEAR_M
    inside = any(_in_poly(p, poly, EDGE_MARGIN_M) for poly in ctx["openings"])
    if not inside:
        return ctx["ceiling"] - close, "under the slab of the level above"
    if part == "wall":
        if out is not None and ctx.get("upper_walls"):
            probe = _add(p, out, WALL_RAIL_GAP_M + 0.022 + 0.05)
            if any(G.point_in_polygon(probe, rect) for rect in ctx["upper_walls"]):
                return ctx["top_open"] - CLEAR_M, "the wall goes on up on the level above"
        return ctx["cap"] - CLEAR_M, "a wall rail stops under the cap (the wall may end at the floor above)"
    if d is not None and taken_over(ctx, p, d):
        return ctx["rise"] - close, "the floor guard of the level above takes over over that floor"
    return ctx["top_open"] - CLEAR_M, "in the floor opening"


def _intervals(ok, n: int) -> list[tuple[float, float]]:
    """The parts of [0, 1] where ``ok(t)`` holds (``n`` samples, the ends refined by bisection)."""
    ts = [i / n for i in range(n + 1)]
    flags = [ok(t) for t in ts]
    out, start = [], None

    def edge(t_in, t_out):
        for _ in range(48):
            m = (t_in + t_out) / 2.0
            if ok(m):
                t_in = m
            else:
                t_out = m
        return t_in

    for i, f in enumerate(flags):
        if f and start is None:
            start = ts[i] if i == 0 else edge(ts[i], ts[i - 1])
        if not f and start is not None:
            out.append((start, edge(ts[i - 1], ts[i])))
            start = None
    if start is not None:
        out.append((start, 1.0))
    return out


# --------------------------------------------------------------------------
# The guard plan
# --------------------------------------------------------------------------

def _leg_req(plan: dict, ctx: dict, leg: dict, p, level_h: float) -> float:
    """The lowest top a handrail over plan point ``p`` of ``leg`` may have (on a flight the nosing line, kept at its
    pitch past the first and last nosing into the newels there)."""
    from wenart.blender import parametric as P
    if leg["what"] == "flight":
        fr = next(f for f in ctx["frames"] if f["index"] == leg["flight"])
        return fr["base"] + fr["riser"] + _s_of(fr, p) * fr["k"] + P.STAIR_RAIL_HEIGHT
    if leg["what"] == "winders":
        return _winder_top(plan, p) + P.STAIR_RAIL_HEIGHT
    return float(leg["z"]) + level_h


def _rail_line(plan: dict, ctx: dict, leg: dict, A, B, level_h: float) -> tuple[float, float]:
    """``(h_A, h_B)``: the handrail's top at the ends of a straight leg between two newels: on a flight its nosing
    line plus the rail height, on a level edge level, over winders a line over every tread (level when short). The
    treads under the newels at its ends do not count: winders meet at a newel, the newel takes their climb."""
    if leg["what"] == "flight":
        return _leg_req(plan, ctx, leg, A, level_h), _leg_req(plan, ctx, leg, B, level_h)
    length = G.distance(A, B)
    n = max(2, int(math.ceil(length / 0.005)))
    e = min(0.45, (NEWEL_M / 2.0 + 0.02) / max(length, 1e-9))
    ts = [e + (1.0 - 2.0 * e) * i / n for i in range(n + 1)]
    req = [_leg_req(plan, ctx, leg, _lerp(A, B, t), level_h) for t in ts]
    if leg["what"] != "winders" or length < SHORT_LEG_M:
        top = max(req)
        return top, top
    h0, h1 = req[0], req[-1]
    lift = max(r - (h0 + (h1 - h0) * t) for t, r in zip(ts, req))
    return h0 + max(0.0, lift), h1 + max(0.0, lift)


def _post(posts: list, at, z0: float, key: str, size=(NEWEL_M, NEWEL_M), angle: float = 0.0, role: str = "newel"
          ) -> dict:
    for p in posts:
        if G.distance(p["at"], at) < 0.01 and p["role"] == role:
            p["z0"] = min(p["z0"], z0)
            return p
    rec = {"id": f"n{len(posts) + 1}", "at": (float(at[0]), float(at[1])), "z0": float(z0), "z1": None,
           "tops": [], "size": [float(size[0]), float(size[1])], "angle": float(angle), "key": key, "role": role}
    posts.append(rec)
    return rec


def _foot_z(plan: dict, ctx: dict, at, half: float) -> float:
    """The lowest stair surface under a post's footprint (the post stands on it, through the higher parts)."""
    zs = []
    for dx in (-half, 0.0, half):
        for dy in (-half, 0.0, half):
            z = surface_z(plan, (at[0] + dx, at[1] + dy), ctx["frames"])
            if z is not None:
                zs.append(z)
    return min(zs) if zs else 0.0


def plan_guards(plan: dict, ceiling_voids=None, upper_guards=(), upper_walls=None) -> dict:
    """The handrails, newels, infill and strings of a planned stair (module docstring). ``ceiling_voids``: the floor
    openings of the level above (None: the stair's own ``void``); ``upper_guards``: the runs ``(p, q)`` of that
    level's floor guards (``shell.floor_void_guards``); ``upper_walls``: that level's wall rectangles (default
    ``plan["upper_wall_rects"]``)."""
    design = plan_design(plan)
    sides = plan.get("sides")
    if not sides:
        sides = side_paths(plan, plan.get("wall_rects") or ())
    elif plan.get("top_apron") and not any(leg["what"] == "apron" for s in sides for leg in s["legs"]):
        sides = side_paths(plan, plan.get("wall_rects") or ())       # the apron came after the plan: legs for it
    ctx = _context(plan, ceiling_voids, upper_guards, upper_walls)
    rail = design["rail"]
    r = rail["r"]
    posts: list[dict] = []
    rails: list[dict] = []
    infill: list[dict] = []
    strings: list[dict] = []
    cuts: list[dict] = []
    notes: list[str] = []
    widths = [float(f["width"]) for f in plan.get("flights") or []]
    for side in sides:
        sign = side["sign"]
        legs = side["legs"]
        lines = inset_legs(legs, sign, LINE_IN_M)
        i = 0
        while i < len(legs):
            if legs[i]["wall"]:
                i += 1
                continue
            j = i
            while j + 1 < len(legs) and not legs[j + 1]["wall"] and lines[j]["joint"] is not None:
                j += 1
            _balustrade(plan, ctx, design, side, legs, lines, i, j, posts, rails, infill, cuts)
            if design["string"]:
                for m in range(i, j + 1):
                    strings += _string(plan, ctx, design, legs[m], sign)
            i = j + 1
    # the wall rails: two rails on a wide stair, and one where a flight would have no handrail
    held = _held(plan, ctx, rails)
    want: dict = {}
    for fr in ctx["frames"]:
        wide = fr["hw"] * 2.0 > TWO_RAILS_WIDTH_M + 1e-9
        short = held.get(fr["index"], 0.0) < HELD_SHARE * railable(ctx, fr)
        wall_sides = [s for s in sides for leg in s["legs"] if leg["flight"] == fr["index"] and leg["wall"]]
        if not wall_sides or not (wide or short):
            continue
        for s in (wall_sides if wide else [min(wall_sides, key=lambda s: s["sign"])]):
            want.setdefault(s["side"], []).append(fr["index"])
            if short and not wide:
                notes.append(f"flight {fr['index'] + 1}: its open side holds no handrail over most of its run: a "
                             f"wall handrail on its {s['side']} side")
    for side in sides:
        if side["side"] in want:
            rails += _wall_rails(plan, ctx, design, side, len(rails))
    used = {pid for rl in rails for pid in rl["posts"] if pid}
    posts = [p for p in posts if p["id"] in used or p.get("infill")]
    for p in posts:
        top = max(p["tops"]) + NEWEL_CAP_M if p["tops"] else p["z0"] + 0.9
        cap, _why = cap_at(ctx, p["at"], None, "post")
        p["z1"] = max(min(top, cap), p["z0"] + 0.05)
        p.pop("tops", None)
        p.pop("infill", None)
    gap = _max_gap(infill, design)
    return {"design": design, "sides": [{"side": s["side"], "sign": s["sign"], "inner": s["inner"],
                                         "legs": [{k: v for k, v in leg.items()} for leg in s["legs"]]}
                                        for s in sides],
            "rails": rails, "posts": posts, "infill": infill, "strings": strings, "cuts": cuts, "notes": notes,
            "max_gap_m": round(gap, 4), "widths": widths}


def _balustrade(plan, ctx, design, side, legs, lines, i: int, j: int, posts, rails, infill, cuts) -> None:
    """One balustrade over the open legs ``i``..``j`` of a side: newels at its ends and corners, one straight rail
    per leg (cut where a cap says so), the infill under it."""
    rail = design["rail"]
    r = rail["r"]
    sign = side["sign"]
    # the newels' places: the run's ends nudged onto the stair, the joints between its legs
    starts, ends = [], []
    for m in range(i, j + 1):
        A, B = lines[m]["A"], lines[m]["B"]
        d = lines[m]["d"]
        if m == i:
            if legs[m]["what"] == "flight":
                fr = next(f for f in ctx["frames"] if f["index"] == legs[m]["flight"])
                s = _s_of(fr, A)
                if s < FOOT_POST_M:
                    A = _add(A, d, FOOT_POST_M - s)
        if m == j:
            last_flight = legs[m]["what"] == "flight" and (m == len(legs) - 1 or lines[m]["joint"] is None
                                                           or legs[m + 1]["wall"])
            if last_flight:
                fr = next(f for f in ctx["frames"] if f["index"] == legs[m]["flight"])
                s = _s_of(fr, B)
                if s > fr["L"] - TOP_POST_M:
                    B = _add(B, d, (fr["L"] - TOP_POST_M) - s)
            elif legs[m]["what"] in ("apron", "top"):
                B = _add(B, d, -TOP_POST_M)
        if m > i and lines[m - 1]["joint"] == "reversal":
            A = lines[m]["A"]
        starts.append(A)
        ends.append(B)
    across = 2.0 * (LINE_IN_M + r) + 0.01               # a dog-leg's newel takes both flights' rails
    for m in range(i, j + 1):
        k = m - i
        leg, line = legs[m], lines[m]
        A, B = starts[k], ends[k]
        length = G.distance(A, B)
        if length < 1e-3:
            continue
        d = line["d"]
        angle = math.degrees(math.atan2(d[1], d[0]))
        h_a, h_b = _rail_line(plan, ctx, leg, A, B, LEVEL_GUARD_M)
        # newels: at the start and the end (a reversal's on the divider)
        if k > 0 and lines[m - 1]["joint"] == "reversal":
            p0 = _post(posts, leg["a"], _foot_z(plan, ctx, leg["a"], across / 2.0), design["newel_key"],
                       (NEWEL_M, across), angle)
        else:
            p0 = _post(posts, A, _foot_z(plan, ctx, A, NEWEL_M / 2.0), design["newel_key"], angle=angle)
        if line["joint"] == "reversal" and m < j:
            p1 = _post(posts, leg["b"], _foot_z(plan, ctx, leg["b"], across / 2.0), design["newel_key"],
                       (NEWEL_M, across), angle)
        else:
            p1 = _post(posts, B, _foot_z(plan, ctx, B, NEWEL_M / 2.0), design["newel_key"], angle=angle)

        def top_at(t, h_a=h_a, h_b=h_b):
            return h_a + (h_b - h_a) * t

        def ok(t, A=A, B=B, d=d, top_at=top_at):
            return top_at(t) <= cap_at(ctx, _lerp(A, B, t), d, "rail")[0] + 1e-9

        # the rail, cut where it would pass a cap (the infill goes on under the cap)
        keep = _intervals(ok, max(4, int(math.ceil(length / SAMPLE_M))))
        if keep != [(0.0, 1.0)]:
            keep = [(t0, t1) for t0, t1 in keep if (t1 - t0) * length >= min(RAIL_MIN_M, 0.9 * length)]
            for t0, t1 in _complement(keep):
                cuts.append({"side": side["side"], "leg": m, "what": leg["what"], "flight": leg.get("flight"),
                             "from": _r(_lerp(A, B, t0)), "to": _r(_lerp(A, B, t1)),
                             "why": cap_at(ctx, _lerp(A, B, (t0 + t1) / 2.0), d, "rail")[1]})
        for t0, t1 in keep:
            P0, P1 = _lerp(A, B, t0), _lerp(A, B, t1)
            z0, z1 = top_at(t0), top_at(t1)
            start = p0 if t0 < 1e-6 else _post(posts, P0, _foot_z(plan, ctx, P0, NEWEL_M / 2.0),
                                                design["newel_key"], angle=angle)
            end = p1 if t1 > 1 - 1e-6 else _post(posts, P1, _foot_z(plan, ctx, P1, NEWEL_M / 2.0),
                                                  design["newel_key"], angle=angle)
            start["tops"].append(z0)
            end["tops"].append(z1)
            rails.append({"id": f"r{len(rails) + 1}", "side": side["side"], "type": "balustrade", "leg": m,
                          "what": leg["what"], "flight": leg.get("flight"),
                          "path": [(P0[0], P0[1], z0), (P1[0], P1[1], z1)], "r": r, "key": rail["key"],
                          "sides": rail["sides"], "posts": [start["id"], end["id"]], "returns": []})
        built = _infill(plan, ctx, design, side, leg, m, A, B, d, top_at, keep, infill)
        # a newel no rail reaches but the infill does ends that infill: its top over the infill, under the cap; one
        # that neither reaches is no newel (under a shaft's cap the balustrade ends at the rail's last newel)
        face = (NEWEL_M / 2.0 + 0.02) / length
        for post, t, pt in ((p0, 0.0, A), (p1, 1.0, B)):
            if any(t0 - 1e-6 <= t <= t1 + 1e-6 for t0, t1 in keep):
                continue
            if any(u0 <= t + face and u1 >= t - face for u0, u1 in built):
                post["tops"].append(min(top_at(t), cap_at(ctx, pt, d, "post")[0] - NEWEL_CAP_M))
                post["infill"] = True


def _complement(keep: list[tuple[float, float]]) -> list[tuple[float, float]]:
    out, t = [], 0.0
    for t0, t1 in keep:
        if t0 > t + 1e-6:
            out.append((t, t0))
        t = t1
    if t < 1.0 - 1e-6:
        out.append((t, 1.0))
    return out


def _base_at(plan, ctx, design, leg, p) -> float:
    """The bottom of the infill at plan point ``p``: the string's top (glass a little lower, fixed to its inner
    face), else the tread, landing or apron under it."""
    lift = STRING_UP_M - (GLASS_STRING_OVERLAP_M if design["infill"] == "glass" else 0.0)
    if leg["what"] == "flight":
        fr = next(f for f in ctx["frames"] if f["index"] == leg["flight"])
        s = _s_of(fr, p)
        return nose(fr, s) + lift if design["string"] else tread_top(fr, s)
    if leg["what"] == "winders":
        z = _winder_top(plan, p)
        return z + lift if design["string"] else z
    z = float(leg["z"])
    return z + lift if design["string"] and leg["what"] == "landing" else z


CLOSING_CAPS = ("under the slab of the level above", "the floor guard of the level above takes over over that floor")


def _infill(plan, ctx, design, side, leg, m: int, A, B, d, top_at, keep, infill: list) -> list[tuple[float, float]]:
    """The infill of one leg between its newels: glass panels or balusters from the base to the rail; where the rail
    is cut by a slab or the floor guard above, up to that slab or floor (it closes the gap there); not under a
    shaft's cap, where the balustrade ends with the rail. Returns the stretches ``(t0, t1)`` it fills."""
    r = design["rail"]["r"]
    length = G.distance(A, B)
    face = NEWEL_M / 2.0
    if length <= 2 * face + 0.02:
        return []

    def railed(t):
        return any(t0 - 1e-9 <= t <= t1 + 1e-9 for t0, t1 in keep)

    def top(t, glass: bool):
        under_rail = top_at(t) - (r if glass else 2.0 * r - 0.004)
        if railed(t):
            return under_rail
        return min(under_rail, cap_at(ctx, _lerp(A, B, t), d, "infill")[0])

    def allowed(t):
        return railed(t) or cap_at(ctx, _lerp(A, B, t), d, "infill")[1] in CLOSING_CAPS

    a, b = face / length, 1.0 - face / length
    spans = [(a + (b - a) * u0, a + (b - a) * u1)
             for u0, u1 in _intervals(lambda u: allowed(a + (b - a) * u), max(4, int(math.ceil(length / SAMPLE_M))))]
    spans = [(t0, t1) for t0, t1 in spans if (t1 - t0) * length >= 0.06]
    glass = design["infill"] == "glass"
    bays = []
    for s0, s1 in spans:
        # under a cut rail a span ends at a newel (the rail's end): a newel's half width off it
        e0 = 0.0 if s0 <= a + 1e-6 else face / length
        e1 = 0.0 if s1 >= b - 1e-6 else face / length
        t0, t1 = s0 + e0, s1 - e1
        if (t1 - t0) * length < 0.06:
            continue
        if design.get("posts_every") and (t1 - t0) * length > design["posts_every"]:
            k = int(math.ceil((t1 - t0) * length / design["posts_every"]))
            cuts = [t0 + (t1 - t0) * i / k for i in range(k + 1)]
            for u0, u1 in zip(cuts, cuts[1:]):
                bays.append((u0 + (SLIM_POST_M / 2.0) / length if u0 > t0 else u0,
                             u1 - (SLIM_POST_M / 2.0) / length if u1 < t1 else u1))
            for t in cuts[1:-1]:
                p = _lerp(A, B, t)
                infill.append({"type": "slim_post", "side": side["side"], "leg": m, "at": _r(p, 5),
                               "z0": _base_at(plan, ctx, design, leg, p) - 0.03,
                               "z1": top(t, False) + 0.004, "w": SLIM_POST_M, "key": "steel"})
        else:
            bays.append((t0, t1))
    if glass:
        gap = GLASS_END_GAP_M / length
        for t0, t1 in bays:
            t0, t1 = t0 + gap, t1 - gap
            if (t1 - t0) * length < 0.08:
                continue
            k = max(1, int(math.ceil((t1 - t0) * length / GLASS_PANEL_MAX_M)))
            for q in range(k):
                u0 = t0 + (t1 - t0) * q / k + (gap / 2.0 if q else 0.0)
                u1 = t0 + (t1 - t0) * (q + 1) / k - (gap / 2.0 if q < k - 1 else 0.0)
                ts = [u0] + [t for kk in keep for t in kk if u0 < t < u1] + [u1]
                bottom = [(t, _base_at(plan, ctx, design, leg, _lerp(A, B, t))) for t in (u0, u1)]
                tops = [(t, top(t, True)) for t in ts]
                if min(tops[0][1] - bottom[0][1], tops[-1][1] - bottom[1][1]) < 0.05:
                    continue
                infill.append({"type": "glass", "side": side["side"], "leg": m, "o": _r(A, 5), "d": _r(d, 6),
                               "length": length, "bottom": [[round(t * length, 5), round(z, 5)] for t, z in bottom],
                               "top": [[round(t * length, 5), round(z, 5)] for t, z in tops], "t": GLASS_T})
        return spans
    spec = BALUSTERS[design["infill"]]
    w = spec["w"]
    gap = spec.get("gap", GAP_DESIGN_M)
    for t0, t1 in bays:
        clear = (t1 - t0) * length
        nb = max(0, int(math.ceil((clear - gap) / (gap + w) - 1e-9)))
        if nb <= 0:
            continue
        g = (clear - nb * w) / (nb + 1)
        for q in range(nb):
            t = t0 + (g * (q + 1) + w * (q + 0.5)) / length
            p = _lerp(A, B, t)
            z0, z1 = _base_at(plan, ctx, design, leg, p), top(t, False)
            if z1 - z0 < 0.05:
                continue
            infill.append({"type": "baluster", "side": side["side"], "leg": m, "at": _r(p, 5), "z0": round(z0, 5),
                           "z1": round(z1, 5), "w": w, "d": spec["d"],
                           "angle": round(math.degrees(math.atan2(d[1], d[0])), 3),
                           "key": spec["key"], "shape": spec["shape"], "gap": round(g, 5)})
    return spans


def _max_gap(infill: list, design: dict) -> float:
    """The largest clear gap of the infill: between two balusters (and a baluster and a newel), or the glass's end
    gaps to the newels and between panels."""
    gaps = [float(p["gap"]) for p in infill if p.get("type") == "baluster"]
    if design["infill"] == "glass" and infill:
        gaps.append(GLASS_END_GAP_M)
    return max(gaps) if gaps else 0.0


def _string(plan, ctx, design, leg, sign: float) -> list[dict]:
    """The string (a closed string, or the landing's fascia) along an open leg: its outer face on the edge, its top
    ``STRING_UP_M`` over the nosing line (over a level edge, over the landing), its bottom the stair's soffit."""
    if leg["what"] in ("apron", "top"):
        return []
    from wenart.blender import parametric as P
    d, n = _interior(leg, sign)
    t = design["string_t"]
    length = G.distance(leg["a"], leg["b"])
    if length < 0.02:
        return []
    o = _add(leg["a"], n, t / 2.0)
    key = design["string_key"]
    if leg["what"] == "flight":
        fr = next(f for f in ctx["frames"] if f["index"] == leg["flight"])
        f = next(x for x in plan["flights"] if x["index"] == leg["flight"])
        k, tv = flight_waist(plan, f)

        def top(s):
            return nose(fr, s) + STRING_UP_M

        def bot(s):
            return fr["base"] + s * k - tv
        s0, s1 = 0.0, fr["L"]
        b0, b1 = bot(s0), bot(s1)
        if b1 <= 0.0:
            return []
        if b0 < 0.0:
            sc = (tv - fr["base"]) / k
            prof = [(s0, 0.0), (sc, 0.0), (s1, b1), (s1, top(s1)), (s0, top(s0))]
        else:
            prof = [(s0, b0), (s1, b1), (s1, top(s1)), (s0, top(s0))]
        return [{"o": _r(o, 5), "d": _r(d, 6), "t": t, "profile": [_r(p, 5) for p in prof], "key": key,
                 "flight": leg["flight"]}]
    land = plan.get("landing") or {}
    z_b = float(land.get("z") or 0.0) - float(land.get("thickness") or P.STAIR_WAIST_M)
    if leg["what"] == "landing":
        z_t = float(leg["z"]) + STRING_UP_M
        return [{"o": _r(o, 5), "d": _r(d, 6), "t": t, "profile": [[0.0, z_b], [round(length, 5), z_b],
                                                                    [round(length, 5), z_t], [0.0, z_t]],
                 "key": key, "flight": None}]
    out = []                                                        # winders: one piece per tread along the edge
    n_s = max(2, int(math.ceil(length / 0.01)))
    zs = [_winder_top(plan, _add(_lerp(leg["a"], leg["b"], i / n_s), n, 0.03)) for i in range(n_s + 1)]
    start = 0
    for i in range(1, n_s + 2):
        if i == n_s + 1 or abs(zs[i] - zs[start]) > 1e-6:
            s0, s1 = length * start / n_s, length * min(i, n_s) / n_s
            if s1 - s0 > 0.005:
                z_t = zs[start] + STRING_UP_M
                out.append({"o": _r(o, 5), "d": _r(d, 6), "t": t,
                            "profile": [[round(s0, 5), z_b], [round(s1, 5), z_b], [round(s1, 5), z_t],
                                        [round(s0, 5), z_t]], "key": key, "flight": None})
            start = i
    return out


def railable(ctx: dict, fr: dict) -> float:
    """How much of a flight's run can hold a handrail at all: up to where its rail would pass a shaft's cap (a stair
    whose floor above is not built goes on out of sight under it)."""
    from wenart.blender import parametric as P
    top = ctx["top_open"] - CLEAR_M
    s = (top - P.STAIR_RAIL_HEIGHT - fr["base"] - fr["riser"]) / max(fr["k"], 1e-9)
    return max(1e-6, min(fr["L"], s))


def _held(plan, ctx, rails: list) -> dict:
    """Per flight the length of its run its balustrade handrails cover."""
    out: dict = {}
    for rl in rails:
        if rl.get("what") != "flight" or rl.get("flight") is None:
            continue
        fr = next(f for f in ctx["frames"] if f["index"] == rl["flight"])
        a, b = rl["path"][0], rl["path"][-1]
        out[rl["flight"]] = out.get(rl["flight"], 0.0) + abs(_s_of(fr, b[:2]) - _s_of(fr, a[:2]))
    return out


def _wall_rails(plan, ctx, design, side, start_id: int) -> list[dict]:
    """The wall handrails of one side: along every run of consecutive wall legs, ``WALL_RAIL_GAP_M`` off the wall,
    the rail height over the nosing line (rising smoothly round a landing: the heights between two nosings are
    interpolated along the rail), a return into the wall at both ends, brackets at most ``BRACKET_EVERY_M`` apart;
    it ends where it would pass the cap."""
    from wenart.blender import parametric as P
    r = P.STAIR_HANDRAIL_R
    q = WALL_RAIL_GAP_M + r
    legs = side["legs"]
    lines = inset_legs(legs, side["sign"], q)
    out = []
    i = 0
    while i < len(legs):
        if not legs[i]["wall"]:
            i += 1
            continue
        j = i
        while j + 1 < len(legs) and legs[j + 1]["wall"] and lines[j]["joint"] in ("corner", "straight"):
            j += 1
        pts, anchors = [], []
        for m in range(i, j + 1):
            A, B = lines[m]["A"], lines[m]["B"]
            leg = legs[m]
            if leg["what"] == "flight":
                fr = next(f for f in ctx["frames"] if f["index"] == leg["flight"])
                if m == i:
                    A = _add(A, lines[m]["d"], max(0.0, 0.05 - _s_of(fr, A)))
                if m == j:
                    B = _add(B, lines[m]["d"], min(0.0, fr["L"] - 0.05 - _s_of(fr, B)))
                for p in (A, B):
                    pts.append(p)
                    anchors.append(nose(fr, _s_of(fr, p)) + P.STAIR_RAIL_HEIGHT)
            elif leg["what"] == "winders":
                n_s = max(2, int(math.ceil(G.distance(A, B) / 0.005)))
                last = None
                for k in range(n_s + 1):
                    p = _lerp(A, B, k / n_s)
                    z = _winder_top(plan, p) + P.STAIR_RAIL_HEIGHT
                    if last is None or z > last + 1e-6 or k == n_s:
                        pts.append(p)
                        anchors.append(z)
                        last = z if last is None else max(last, z)
            else:
                pts += [A, B]
                anchors += [None, None]
        # one height per point: joined points share the higher; the level legs in between are interpolated
        clean, hs = [], []
        for p, h in zip(pts, anchors):
            if clean and G.distance(clean[-1], p) < 1e-4:
                if h is not None:
                    hs[-1] = h if hs[-1] is None else max(hs[-1], h)
                continue
            clean.append(p)
            hs.append(h)
        hs = _fill(clean, hs, float((plan.get("landing") or {}).get("z") or 0.0) + P.STAIR_RAIL_HEIGHT)
        full = [(p[0], p[1], h) for p, h in zip(clean, hs)]
        path = _cut_wall_path(ctx, full, _outs_along(full, legs[i:j + 1], lines[i:j + 1]))
        if len(path) >= 2 and sum(math.dist(a, b) for a, b in zip(path, path[1:])) >= RAIL_MIN_M:
            outs = _outs_along(path, legs[i:j + 1], lines[i:j + 1])
            first_out, last_out = outs[0], outs[-1]
            rets = [[path[0], (path[0][0] + first_out[0] * q, path[0][1] + first_out[1] * q, path[0][2])],
                    [path[-1], (path[-1][0] + last_out[0] * q, path[-1][1] + last_out[1] * q, path[-1][2])]]
            out.append({"id": f"r{start_id + len(out) + 1}", "side": side["side"], "type": "wall", "leg": i,
                        "what": "wall", "flight": legs[i].get("flight"), "path": path, "r": r, "key": "steel",
                        "sides": 12, "posts": [None, None], "returns": rets, "outs": outs})
        i = j + 1
    return out


def _fill(pts, hs, default: float) -> list[float]:
    """The missing heights ``None`` interpolated along the path between the known ones (held flat at the ends)."""
    if all(h is None for h in hs):
        return [default] * len(hs)
    cum = [0.0]
    for a, b in zip(pts, pts[1:]):
        cum.append(cum[-1] + G.distance(a, b))
    known = [(c, h) for c, h in zip(cum, hs) if h is not None]
    out = []
    for c, h in zip(cum, hs):
        if h is not None:
            out.append(h)
            continue
        before = [k for k in known if k[0] <= c]
        after = [k for k in known if k[0] >= c]
        if not before:
            out.append(after[0][1])
        elif not after:
            out.append(before[-1][1])
        else:
            (c0, h0), (c1, h1) = before[-1], after[0]
            out.append(h0 if c1 - c0 < 1e-9 else h0 + (h1 - h0) * (c - c0) / (c1 - c0))
    # never down: a handrail climbs with the stair
    for k in range(1, len(out)):
        out[k] = max(out[k], out[k - 1])
    return out


def _cut_wall_path(ctx, path: list, outs: list) -> list:
    """A wall rail's path (its top line) up to where it would pass the cap or a slab (``outs``: its wall side per
    segment)."""
    out = [path[0]]
    for k, (a, b) in enumerate(zip(path, path[1:])):
        d = _unit((b[0] - a[0], b[1] - a[1]))
        wall = outs[k] if k < len(outs) else None

        def ok(t, a=a, b=b, d=d, wall=wall):
            p = _lerp(a, b, t)
            return p[2] <= cap_at(ctx, p[:2], d, "wall", wall)[0] + 1e-9

        if ok(1.0) and ok(0.5):
            out.append(b)
            continue
        keep = _intervals(ok, max(4, int(math.dist(a, b) / SAMPLE_M)))
        if keep and keep[0][0] < 1e-6:
            out.append(_lerp(a, b, keep[0][1]))
        break
    return out


def _outs_along(path, legs, lines) -> list:
    """The wall's side (outward normal) for every segment of a wall rail's path: the leg nearest its middle."""
    outs = []
    for a, b in zip(path, path[1:]):
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        best = min(range(len(legs)), key=lambda k: G.point_segment_distance(mid, lines[k]["A"], lines[k]["B"]))
        outs.append(_r(legs[best]["out"], 6))
    return outs


# --------------------------------------------------------------------------
# Meshes
# --------------------------------------------------------------------------

def _part(mesh, key: str, role: str, **extra) -> dict:
    verts, faces = mesh
    return dict({"verts": verts, "faces": faces, "key": key, "role": role}, **extra)


def guard_parts(guards: dict) -> list[dict]:
    """The meshes of a guard plan (pure): every handrail a round (steel) or rounded (timber) bar with its returns
    and, on a wall, its brackets; the newels; the infill; role ``rail``, ``bracket``, ``post``, ``baluster`` or
    ``glass``; key ``steel``, ``timber`` or ``glass`` (``parametric.stair_face_slots``)."""
    from wenart.blender import details as D
    parts: list[dict] = []
    for rl in guards.get("rails") or []:
        path = [tuple(float(c) for c in p) for p in rl["path"]]
        sides = int(rl.get("sides") or 12)
        phase = 0.0 if sides % 4 == 0 else 0.5             # a vertex on the top: the rail's top is its path exactly
        r = float(rl["r"])
        for a, b in zip(path, path[1:]):
            mesh = D.tube(*_axis(a, b, r), r, sides, phase)
            if mesh[0]:
                parts.append(_part(mesh, rl["key"], "rail", flight=rl.get("flight"), rail=rl["id"]))
        for a, b in rl.get("returns") or []:
            mesh = D.tube(*_axis(tuple(a), tuple(b), r), r, sides, phase)
            if mesh[0]:
                parts.append(_part(mesh, rl["key"], "rail", flight=rl.get("flight"), rail=rl["id"], end_return=True))
        if rl.get("type") == "wall":
            parts += _brackets(rl)
    for p in guards.get("posts") or []:
        x, y = p["at"]
        h = float(p["z1"]) - float(p["z0"])
        parts.append(_part(geom2d.box((x, y, float(p["z0"]) + h / 2.0), (p["size"][0], p["size"][1], h),
                                      float(p.get("angle") or 0.0)), p["key"], "post", flight=None, newel=True))
    for piece in guards.get("infill") or []:
        parts += _infill_parts(piece)
    return parts


def _axis(a, b, r: float):
    """The axis of a round bar whose top runs from ``a`` to ``b``: lowered by ``r`` times the cosine of its slope
    (the top of a sloped bar's section lies that far over its axis)."""
    run = math.hypot(b[0] - a[0], b[1] - a[1])
    length = math.dist(a, b)
    c = r * (run / length if length > 1e-12 else 1.0)
    return (a[0], a[1], a[2] - c), (b[0], b[1], b[2] - c)


def _brackets(rl: dict) -> list[dict]:
    from wenart.blender import details as D
    out = []
    r = float(rl["r"])
    path = [(float(p[0]), float(p[1]), float(p[2]) - r) for p in rl["path"]]
    q = WALL_RAIL_GAP_M + r
    outs = rl.get("outs") or []
    for k, (a, b) in enumerate(zip(path, path[1:])):
        wall = outs[k] if k < len(outs) else (0.0, 0.0)
        length = math.dist(a, b)
        n = max(1, int(math.ceil(length / BRACKET_EVERY_M - 1e-9)))
        for m in range(n + 1):
            if m == 0 and k > 0:
                continue
            t = min(max(m / n, 0.08), 0.92)
            c = tuple(a[j] + (b[j] - a[j]) * t for j in range(3))
            stem = (c[0], c[1], c[2] - r - 0.03)
            to = (stem[0] + wall[0] * q, stem[1] + wall[1] * q, stem[2])
            for mesh in (D.tube(c, stem, BRACKET_R, 6), D.tube(stem, to, BRACKET_R, 6)):
                if mesh[0]:
                    out.append(_part(mesh, "steel", "bracket", flight=rl.get("flight"), rail=rl["id"]))
    return out


def _infill_parts(piece: dict) -> list[dict]:
    from wenart.blender import details as D
    if piece["type"] == "glass":
        bottom = [tuple(p) for p in piece["bottom"]]
        top = [tuple(p) for p in piece["top"]]
        prof = geom2d.convex_hull(bottom + top)
        if len(prof) < 3:
            return []
        return [_part(geom2d.extrude_profile(prof, piece["o"], piece["d"], piece["t"]), "glass", "glass", flight=None)]
    if piece["type"] == "slim_post":
        x, y = piece["at"]
        return [_part(D.tube((x, y, piece["z0"]), (x, y, piece["z1"]), piece["w"] / 2.0, 12), piece["key"], "post",
                      flight=None)]
    x, y = piece["at"]
    z0, z1 = float(piece["z0"]), float(piece["z1"])
    w, dd, ang, key = float(piece["w"]), float(piece["d"]), float(piece["angle"]), piece["key"]
    shape = piece.get("shape") or "square"
    if shape == "turned" and z1 - z0 > 0.45:
        # a turned baluster: a square base and top block, a swelling shaft between (stacked round sections)
        blk = 0.12
        out = [_part(geom2d.box((x, y, z0 + blk / 2.0), (w, w, blk), ang), key, "baluster", flight=None),
               _part(geom2d.box((x, y, z1 - blk / 2.0), (w, w, blk), ang), key, "baluster", flight=None)]
        a, b = z0 + blk, z1 - blk
        radii = (0.4, 0.5, 0.42, 0.3, 0.36)
        for i, rr in enumerate(radii):
            s0, s1 = a + (b - a) * i / len(radii), a + (b - a) * (i + 1) / len(radii)
            out.append(_part(D.tube((x, y, s0), (x, y, s1), w * rr, 12), key, "baluster", flight=None))
        return out
    if shape == "wrought":
        out = [_part(D.tube((x, y, z0), (x, y, z1), w / 2.0, 8), key, "baluster", flight=None)]
        for zc in (z0 + (z1 - z0) * 0.33, z0 + (z1 - z0) * 0.66):
            out.append(_part(D.tube((x, y, zc - 0.015), (x, y, zc + 0.015), w, 8), key, "baluster", flight=None))
        return out
    return [_part(geom2d.box((x, y, (z0 + z1) / 2.0), (w, dd, z1 - z0), ang), key, "baluster", flight=None)]


def string_parts(guards: dict) -> list[dict]:
    """The strings of a guard plan (role ``string``; its key: ``steel``, ``worktop`` = the structure or ``timber``)."""
    out = []
    for s in guards.get("strings") or []:
        prof = geom2d.convex_hull([tuple(p) for p in s["profile"]])
        if len(prof) >= 3:
            out.append(_part(geom2d.extrude_profile(prof, s["o"], s["d"], s["t"]), s["key"], "string",
                             flight=s.get("flight"), rise_dir=None))
    return out


def light_winders(plan: dict, voids: Sequence = ()) -> bool:
    """True when the winders of a light stair (``plate``, ``stringer``) stand over a floor opening of their level
    (at least half the landing): they are built as thin treads with riser plates, their underside seen from below."""
    land = plan.get("landing") or {}
    if land.get("role") != "winders" or plan_design(plan)["structure"] == "solid" or not voids:
        return False
    poly = land["polygon"]
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    n, inside, over = 12, 0, 0
    for i in range(n):
        for j in range(n):
            p = (min(xs) + (max(xs) - min(xs)) * (i + 0.5) / n, min(ys) + (max(ys) - min(ys)) * (j + 0.5) / n)
            if not G.point_in_polygon(p, poly):
                continue
            inside += 1
            if any(len(v) >= 3 and G.point_in_polygon(p, v) for v in voids):
                over += 1
    return inside > 0 and over >= inside / 2.0


def winder_parts(plan: dict) -> list[dict]:
    """The winders of a light stair over a void (``light_winders``): each tread ``WINDER_PLATE_M`` thick under its
    top, a riser plate on the edge it shares with the next one, from under the lower tread to the upper (pure)."""
    land = plan.get("landing") or {}
    ws = land.get("winders") or []
    out = []
    for j, w in enumerate(ws):
        out.append(_part(geom2d.prism(w["polygon"], float(w["top"]) - WINDER_PLATE_M, float(w["top"])), "worktop",
                         "winder", flight=None, rise_dir=None, winder=j))
    for j in range(len(ws) - 1):
        seg = _shared_edge(ws[j]["polygon"], ws[j + 1]["polygon"])
        if seg is None:
            continue
        a, b = seg
        z0 = float(ws[j]["top"]) - WINDER_PLATE_M
        z1 = float(ws[j + 1]["top"]) - WINDER_PLATE_M + 0.002
        if z1 - z0 < 0.01 or G.distance(a, b) < 0.01:
            continue
        c = G.segment_midpoint(a, b)
        out.append(_part(geom2d.box((c[0], c[1], (z0 + z1) / 2.0), (G.distance(a, b), WINDER_RISER_T, z1 - z0),
                                    G.segment_angle_deg(a, b)), "worktop", "riser", flight=None, rise_dir=None,
                         winder=j))
    return out


def _shared_edge(pa, pb, tol: float = 1e-3):
    """The longest stretch the boundaries of two polygons share (two collinear overlapping edges), or None."""
    best = None
    for i in range(len(pa)):
        a0, a1 = pa[i], pa[(i + 1) % len(pa)]
        la = G.distance(a0, a1)
        if la < 1e-6:
            continue
        u = _unit(_sub(a1, a0))
        for k in range(len(pb)):
            b0, b1 = pb[k], pb[(k + 1) % len(pb)]
            if abs(_cross(u, _sub(b0, a0))) > tol or abs(_cross(u, _sub(b1, a0))) > tol:
                continue
            s0, s1 = sorted((_dot(_sub(b0, a0), u), _dot(_sub(b1, a0), u)))
            lo, hi = max(0.0, s0), min(la, s1)
            if hi - lo > 1e-3 and (best is None or hi - lo > best[0]):
                best = (hi - lo, _add(a0, u, lo), _add(a0, u, hi))
    return None if best is None else (best[1], best[2])


# --------------------------------------------------------------------------
# The review (model review M15)
# --------------------------------------------------------------------------
# The rules of the review, each a kind of what the user saw (cam_r_L0_koridor_1): rails that cross, a handrail that
# stops short of a turn or of its stair, one at the wrong height, one through a tread, a wall or the floor above, a
# stair rail beside the floor guard of the level above, an infill gap a child passes, a rail out over the room.
REVIEW_RULES = ("cross", "beside_guard", "stops_short", "no_handrail", "height", "through_tread", "through_wall",
                "through_floor_above", "gap", "outside")
OUTSIDE_M = 0.15                # a rail farther than this outside the stair (its flights, landing, apron, well)
UPPER_GUARD_R = 0.02            # the floor guard's top rail, a bar of this radius at its height


def _hull(plan: dict, frames: list) -> list:
    pts = []
    for fr in frames:
        for s in (-0.05, fr["L"] + 0.05):
            for q in (-1.0, 1.0):
                pts.append(_add(_add(fr["o"], fr["r"], s), fr["pl"], q * fr["hw"]))
    land = plan.get("landing") or {}
    pts += [tuple(p) for p in land.get("polygon") or []]
    apron = float(plan.get("top_apron") or 0.0)
    if apron > 0 and frames:
        fr = frames[-1]
        for q in (-1.0, 1.0):
            pts.append(_add(_add(fr["o"], fr["r"], fr["L"] + apron), fr["pl"], q * fr["hw"]))
    return geom2d.convex_hull(pts)


def _finding(rule: str, severity: str, message: str, **metrics) -> dict:
    return {"rule": rule, "severity": severity, "message": message, "metrics": metrics}


def review(guards: dict, plan: dict, wall_rects: Sequence = (), ceiling_voids=None, upper_guards=(),
           upper_guard_h: float = LEVEL_GUARD_M, upper_walls=None) -> list[dict]:
    """The findings of a stair's handrails as built (pure; model review M15): ``guards`` = ``plan_guards`` or the
    scene manifest's ``summary`` of it (or ``legacy_guards``), ``plan`` = the stair's plan (its treads),
    ``wall_rects`` the level's walls, ``ceiling_voids`` / ``upper_guards`` / ``upper_walls`` as for ``plan_guards``
    (the floor guards of the level above stand ``upper_guard_h`` high on that floor). ``[{"rule", "severity",
    "message", "metrics"}]`` with ``rule`` one of ``REVIEW_RULES``."""
    ctx = _context(plan, ceiling_voids, upper_guards, upper_walls)
    frames = ctx["frames"]
    rails = [dict(rl, path=[tuple(float(c) for c in p) for p in rl["path"]]) for rl in guards.get("rails") or []]
    posts = {p["id"]: p for p in guards.get("posts") or []}
    out: list[dict] = []
    hull = _hull(plan, frames)
    # 1. rails that cross another rail (not where they meet at a newel) or the floor guard of the level above
    segs = []
    for rl in rails:
        for k, (a, b) in enumerate(zip(rl["path"], rl["path"][1:])):
            segs.append((rl, k, a, b))
    for i, (ra, ka, a0, a1) in enumerate(segs):
        for rb, kb, b0, b1 in segs[i + 1:]:
            if ra["id"] == rb["id"]:
                continue
            shared = set(p for p in ra.get("posts") or [] if p) & set(p for p in rb.get("posts") or [] if p)
            ends = [math.dist(p, q) for p in (a0, a1) for q in (b0, b1)]
            if shared or min(ends) < NEWEL_M:
                continue
            d = seg_dist3(a0, a1, b0, b1)
            if d < float(ra["r"]) + float(rb["r"]) + 0.01:
                out.append(_finding("cross", "major", f"rail {ra['id']} ({ra['side']}, {ra['what']}) crosses rail "
                                    f"{rb['id']} ({rb['side']}, {rb['what']}) {d:.3f} m apart, not at a newel",
                                    rails=[ra["id"], rb["id"]], distance_m=round(d, 4)))
    rise = ctx["rise"]
    for rl in rails:
        for a, b in zip(rl["path"], rl["path"][1:]):
            d2 = _unit((b[0] - a[0], b[1] - a[1]))
            for g0, g1 in ctx["guards"]:
                p0, p1 = (g0[0], g0[1], rise + upper_guard_h), (g1[0], g1[1], rise + upper_guard_h)
                d = seg_dist3(a, b, p0, p1)
                if d < float(rl["r"]) + UPPER_GUARD_R + 0.01:
                    out.append(_finding("cross", "major", f"rail {rl['id']} ({rl['side']}) runs into the floor guard "
                                        f"of the level above ({d:.3f} m)", rails=[rl["id"]], distance_m=round(d, 4)))
                    break
            # 2. beside a floor guard over that floor (two guards side by side at different slopes)
            n = max(2, int(math.ceil(math.dist(a, b) / SAMPLE_M)))
            beside = 0.0
            for k in range(n):
                p = _lerp(a, b, (k + 0.5) / n)
                if p[2] > rise + 0.02 and taken_over(ctx, p[:2], d2):
                    beside += math.dist(a, b) / n
            if beside >= RAIL_MIN_M:
                out.append(_finding("beside_guard", "major", f"rail {rl['id']} ({rl['side']}) runs {beside:.2f} m "
                                    f"over the floor of the level above beside that floor's guard (two guards side "
                                    f"by side at different slopes)", rails=[rl["id"]], length_m=round(beside, 3)))
    # 3. a handrail that stops short: a balustrade rail end without its newel, an open leg without a rail
    for rl in rails:
        if rl["type"] != "balustrade":
            if rl["type"] == "wall" and int(rl.get("returns") if isinstance(rl.get("returns"), int)
                                            else len(rl.get("returns") or [])) < 2:
                out.append(_finding("stops_short", "minor", f"wall rail {rl['id']} ({rl['side']}) ends without a "
                                    f"return into the wall", rails=[rl["id"]]))
            continue
        for end, pid in zip((rl["path"][0], rl["path"][-1]), (rl.get("posts") or [None, None])):
            post = posts.get(pid) if pid else None
            reach = max(post.get("size") or [0.0]) / 2.0 + 0.005 if post else 0.0
            if post is None or G.distance(post["at"], end[:2]) > max(0.02, reach):
                out.append(_finding("stops_short", "major", f"rail {rl['id']} ({rl['side']}, {rl['what']}) ends in "
                                    f"the air at {_r(end, 3)}: no newel takes it", rails=[rl["id"]],
                                    at=_r(end, 3)))
    sides = guards.get("sides") or side_paths(plan, wall_rects)
    cuts = guards.get("cuts") or []
    for side in sides:
        lines = inset_legs(side["legs"], side["sign"], LINE_IN_M)
        for m, leg in enumerate(side["legs"]):
            if leg["wall"]:
                continue
            A, B = lines[m]["A"], lines[m]["B"]
            length = G.distance(A, B)
            if length < 0.05:
                continue
            covered = 0.0
            mine = [rl for rl in rails if rl["side"] == side["side"]]
            n = max(2, int(math.ceil(length / 0.05)))
            for k in range(n):
                p = _lerp(A, B, (k + 0.5) / n)
                near = any(G.point_segment_distance(p, a[:2], b[:2]) < 0.06
                           for rl in mine for a, b in zip(rl["path"], rl["path"][1:]))
                cut = any(G.point_segment_distance(p, c["from"], c["to"]) < 0.06 for c in cuts
                          if c.get("side") == side["side"])
                if near or cut:
                    covered += length / n
            if covered < length - max(0.12, 0.25 * length):
                what = {"winders": "the winders' edge at the turn", "landing": "the landing's edge at the turn",
                        "apron": "the apron's edge at the top", "top": "the top landing's edge"}.get(
                    leg["what"], f"flight {(leg.get('flight') or 0) + 1}")
                out.append(_finding("stops_short", "major", f"the {side['side']} handrail stops short: {what} "
                                    f"({length - covered:.2f} m of {length:.2f} m open) has no rail and no reason",
                                    side=side["side"], what=leg["what"], flight=leg.get("flight"),
                                    open_m=round(length - covered, 3)))
    # 4. every flight holds a handrail over most of its run
    for fr in frames:
        held = 0.0
        for rl in rails:
            for a, b in zip(rl["path"], rl["path"][1:]):
                if all(abs(_q_of(fr, p[:2])) <= fr["hw"] + 0.01 for p in (a, b)):
                    s0, s1 = sorted((_s_of(fr, a[:2]), _s_of(fr, b[:2])))
                    held = max(held, min(s1, fr["L"]) - max(s0, 0.0))
        run = railable(ctx, fr)
        if held < HELD_SHARE * run:
            out.append(_finding("no_handrail", "major", f"flight {fr['index'] + 1} has no handrail over "
                                f"{run - max(held, 0.0):.2f} m of its {run:.2f} m run",
                                flight=fr["index"], held_m=round(max(held, 0.0), 3)))
    # 5. heights, treads, walls, the floor above, outside the stair
    for rl in rails:
        bad = {}
        outs = rl.get("outs") or []
        for seg, (a, b) in enumerate(zip(rl["path"], rl["path"][1:])):
            length = math.dist(a, b)
            d2 = _unit((b[0] - a[0], b[1] - a[1]))
            wall_side = outs[seg] if seg < len(outs) else None
            n = max(2, int(math.ceil(length / SAMPLE_M)))
            for k in range(n + 1):
                t = k / n
                p = _lerp(a, b, t)
                if min(math.dist(p, a), math.dist(p, b)) < NEWEL_M / 2.0 + 0.01:
                    continue                                        # inside the newel it dies into
                xy = p[:2]
                z = surface_z(plan, xy, frames)
                if z is not None and p[2] - 2.0 * float(rl["r"]) < z - 0.005:
                    bad.setdefault("through_tread", (p, z))
                if any(_in_poly(xy, rect, 0.005) for rect in wall_rects):
                    bad.setdefault("through_wall", (p, None))
                cap, why = cap_at(ctx, xy, d2, "wall" if rl["type"] == "wall" else "rail", wall_side)
                if p[2] > cap + CLEAR_M - 0.005:
                    bad.setdefault("through_floor_above", (p, why))
                if hull and not G.point_in_polygon(xy, hull) and geom2d.distance_to_polygon_edges(xy, hull) > OUTSIDE_M:
                    bad.setdefault("outside", (p, None))
                for fr in frames:
                    if rl["what"] in ("flight", "wall") and abs(_q_of(fr, xy)) <= fr["hw"] + 1e-3 \
                            and 0.1 <= _s_of(fr, xy) <= fr["L"] - 0.1:
                        h = p[2] - nose(fr, _s_of(fr, xy))
                        lo, hi = RAIL_FLIGHT_RANGE
                        if not lo - 1e-6 <= h <= hi + 1e-6:
                            bad.setdefault("height", (p, round(h, 3)))
                if rl["what"] in ("landing", "apron", "top") and rl["type"] == "balustrade" and z is not None \
                        and p[2] - z < LEVEL_GUARD_M - 0.02:
                    bad.setdefault("height", (p, round(p[2] - z, 3)))
        for rule, (p, info) in bad.items():
            sev = "minor" if rule == "outside" else "major"
            text = {"through_tread": f"runs through a tread (its underside {p[2] - 2 * float(rl['r']):.2f} m, the "
                                     f"tread {info}" + " m)" if info is not None else "runs through a tread",
                    "through_wall": "runs through a wall", "through_floor_above": f"passes the limit above: {info}",
                    "outside": "stands out over the room, off the stair and its well",
                    "height": f"stands {info} m over its nosing line or level edge (not "
                              f"{RAIL_FLIGHT_RANGE[0]:.2f}-{RAIL_FLIGHT_RANGE[1]:.2f} m, {LEVEL_GUARD_M:.2f} m on a "
                              f"level edge)"}[rule]
            out.append(_finding(rule, sev, f"rail {rl['id']} ({rl['side']}, {rl['what']}) {text} at {_r(p, 3)}",
                                rails=[rl["id"]], at=_r(p, 3)))
    gap = float(guards.get("max_gap_m") or (guards.get("infill") or {}).get("max_gap_m") or 0.0)
    if gap >= GAP_MAX_M:
        out.append(_finding("gap", "major", f"the infill leaves a gap of {gap:.3f} m (a child passes "
                                            f"{GAP_MAX_M:.2f} m)", gap_m=round(gap, 4)))
    return out


def legacy_guards(plan: dict, rails: Sequence[dict], kind: Optional[str] = None) -> dict:
    """The rails of a scene built before this module (25-28 Oct 2026, ``plan["rails"]``: one straight rail per open
    flight side, 0.05 m in from its first and last nosing, a post at each end; a wall rail on the right of a flight
    with no open side), as a guard record for ``review``."""
    from wenart.blender import parametric as P
    riser = float(plan["riser_m"])
    cap = float(plan["rail_limit"]) if plan.get("rail_limit") is not None else float(plan["cap_z"]) - CLEAR_M
    glass = (kind or P.STAIR_BALUSTRADE_DEFAULT) in GLASS_KINDS
    out_rails, posts = [], []
    by_flight: dict = {}
    for rl in rails or []:
        by_flight.setdefault(rl["flight"], []).append(rl)
    for f in plan.get("flights") or []:
        fr = flight_frame(f, riser)
        mine = by_flight.get(f["index"]) or []
        specs = [(rl["side"], float(rl["offset"]), "balustrade") for rl in mine] or \
            [("right", -(fr["hw"] - P.STAIR_WALL_RAIL_GAP - P.STAIR_HANDRAIL_R), "wall")]
        for side, off, typ in specs:
            if glass and typ == "balustrade":
                sgn = 1.0 if off >= 0 else -1.0
                off = sgn * (abs(off) + P.STAIR_RAIL_INSET + P.STAIR_GLASS_T / 2.0 + 0.003)
            s_a, s_b = 0.05, fr["L"] - 0.05
            top_b = nose(fr, s_b) + P.STAIR_RAIL_HEIGHT
            lim = cap if typ == "balustrade" else float(plan["cap_z"]) - CLEAR_M
            if top_b > lim:
                s_b = (lim - P.STAIR_RAIL_HEIGHT - fr["base"] - riser) / fr["k"]
            if s_b - s_a < P.STAIR_RAIL_MIN_M:
                continue
            pa = _add(_add(fr["o"], fr["r"], s_a), fr["pl"], off)
            pb = _add(_add(fr["o"], fr["r"], s_b), fr["pl"], off)
            rid = f"r{len(out_rails) + 1}"
            ids = [None, None]
            if typ == "balustrade" and not glass:
                for k, (s, p) in enumerate(((s_a + P.STAIR_POST / 2.0, pa), (s_b - P.STAIR_POST / 2.0, pb))):
                    at = _add(_add(fr["o"], fr["r"], s), fr["pl"], off)
                    posts.append({"id": f"n{len(posts) + 1}", "at": at, "z0": tread_top(fr, s),
                                  "z1": nose(fr, s) + P.STAIR_RAIL_HEIGHT})
                    ids[k] = posts[-1]["id"]
            out_rails.append({"id": rid, "side": side, "type": typ, "what": "flight" if typ == "balustrade" else "wall",
                              "flight": f["index"], "r": P.STAIR_HANDRAIL_R,
                              "path": [(pa[0], pa[1], nose(fr, s_a) + P.STAIR_RAIL_HEIGHT),
                                       (pb[0], pb[1], nose(fr, s_b) + P.STAIR_RAIL_HEIGHT)],
                              "posts": ids, "returns": 0 if typ == "wall" else []})
    return {"design": {"infill": "glass" if glass else "bars", "kind": kind}, "rails": out_rails, "posts": posts,
            "cuts": [], "max_gap_m": 0.0 if glass else P.STAIR_BALUSTER_PITCH - P.STAIR_BALUSTER, "legacy": True}


# --------------------------------------------------------------------------
# The summary for the scene manifest
# --------------------------------------------------------------------------

def summary(guards: dict) -> dict:
    """The scene manifest's ``stair.guards`` record (model review M15 reads it): the design, the rails (paths,
    posts, returns), the newels, the infill (kind, count, the largest gap), the strings, the cuts and the notes."""
    return {"design": {k: guards["design"][k] for k in ("family", "kind", "structure", "infill", "string", "why")},
            "rails": [dict({"id": rl["id"], "side": rl["side"], "type": rl["type"], "what": rl["what"],
                            "flight": rl.get("flight"), "r": rl["r"], "path": [_r(p) for p in rl["path"]],
                            "posts": rl["posts"], "returns": len(rl.get("returns") or [])},
                           **({"outs": rl["outs"]} if rl.get("outs") else {})) for rl in guards["rails"]],
            "posts": [{"id": p["id"], "at": _r(p["at"]), "z0": round(p["z0"], 4), "z1": round(p["z1"], 4),
                       "size": _r(p["size"])} for p in guards["posts"]],
            "infill": {"kind": guards["design"]["infill"], "pieces": len(guards["infill"]),
                       "max_gap_m": guards["max_gap_m"]},
            "strings": len(guards["strings"]), "cuts": guards["cuts"], "notes": guards["notes"]}
