"""Balcony and terrace edges are guards, never storey walls (26 Nov 2026, audit rule R04).

Why: real17 (run 20261126-110510-full) drew the open edges of its corner balconies as a 5 cm band on the wall layer.
The reader kept the band as exterior walls with the ceiling height, the build ran every wall to the slab above, and the
balconies of L1 and L2 became dark 3 m boxes with the balcony door opening into them. Only the top floor's edges were
low, because the roof-terrace path (``roof.parapet_cuts``) lowered them.

Rule (every project, every level above the ground floor): once the rooms and the outdoor spaces exist, a wall with an
outdoor space on one side (a room of type balcony, terrace, roof_terrace or loggia, a room an outdoor word names, or an
outdoor space of the site, os_*) and the outside on the other (no room of the level, outside the level's indoor
footprint, and not a party wall) is a guard:

- ``parapet: true``, ``guard: {top_m, kind, source}``, ``guard_of`` (the space), ``guard_drawn_thickness``,
  ``drawn_height`` kept, an ``inferred`` evidence item with the reason;
- kind ``solid`` when the drawn band is ``SOLID_MIN_T_M`` (0.10 m) or thicker: a ``GUARD_TOP_M`` (1.10 m) parapet;
  kind ``railing`` when it is thinner (a 5-6 cm line): a ``RAIL_KERB_M`` kerb with the house's balustrade on it up to
  ``GUARD_TOP_M`` (``shell`` builds it, ``wall.guard``).

The outside is open air over a drop: no room of the floor below lies under it either (a setback storey's roof, or a
room the reading missed, is no fall edge). It stays a full wall when: a room or a party wall lies beyond any part of it (a loggia's side walls, the privacy wall
between neighbouring balconies), an outdoor space lies on both sides, a door or window sits in it, it is thicker than
``MAX_T_M`` or shorter than ``BLOCK_RATIO`` times its thickness (a wall's end, a pier), less than ``OUTDOOR_SHARE_MIN`` of its length runs along the space, or a full wall of the level above stands
on it (that wall carries the slab; the levels are taken from the top down, so a guard above carries nothing). The
ground floor's terraces are left alone: a garden or privacy wall at grade is no fall guard. A roof terrace cut into the
roof (a roof opening names its room) keeps the roof's own parapet (``roof.parapet_cuts``, a drawn height wins); its
edge walls carry nothing for the floor below either.

The build keeps a parapet wall's own height (``shell.wall_height`` adds no slab, the wall loop neither runs it to the
slab above nor to the roof); ``shell.railing_edges`` sees the parapet wall as the edge's guard, so no second rail.
"""
from __future__ import annotations

import re
from typing import Optional

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from wenart import building as B

GUARD_TOP_M = 1.10                 # the guard's top over the balcony floor
SOLID_MIN_T_M = 0.10               # a drawn band this thick or more: a solid parapet
RAIL_KERB_M = 0.15                 # a thinner band: a kerb this high with a balustrade on it
MAX_T_M = 0.30                     # a thicker wall is a structural wall, never a guard
BLOCK_RATIO = 2.0                  # a piece shorter than this times its thickness is a block (a wall end, a pier)
DROP_MIN_M = 1.0                   # a level this high or more over the ground floor: its open edges are fall edges
PROBE_M = 0.15                     # the sides are probed this far beyond the wall's faces ...
SAMPLE_M = 0.10                    # ... every this along it
OUTDOOR_SHARE_MIN = 0.5            # at least this share of the wall runs along the outdoor space
FOOTPRINT_CLOSE_M = 0.30           # the indoor rooms closed over walls up to twice this thick (the indoor footprint)
STAND_GAP_M = 0.05                 # an upper wall within half the thicker wall + this of the line stands on it ...
STAND_OVERLAP_M = 0.30             # ... over at least this length (or STAND_SHARE of the wall)
STAND_SHARE = 0.30
OUTDOOR_TYPES = ("balcony", "terrace", "roof_terrace", "loggia")
OUTDOOR_KINDS = ("balcony", "terrace", "roof_terrace", "loggia")
UNTYPED = ("", "none", "unknown", "other")
OUTDOOR_WORDS = re.compile(r"(?<![a-z])(?:balkon|teras|terrace|loggia|lodjia|balcony)")
RULE = "edge_guard"


def _poly(points) -> Optional[Polygon]:
    if not points or len(points) < 3:
        return None
    try:
        p = Polygon([(float(x), float(y)) for x, y, *_ in points]).buffer(0)
    except (TypeError, ValueError):
        return None
    return p if not p.is_empty else None


def outdoor_room(room: dict) -> bool:
    """A room that is an outdoor floor (pure): an outdoor type, or an untyped room an outdoor word names."""
    t = str(room.get("room_type") or "").lower()
    if t in OUTDOOR_TYPES:
        return True
    return t in UNTYPED and bool(OUTDOOR_WORDS.search(B.fold_ascii(str(room.get("label") or "")).lower()))


def _levels_top_down(b: dict) -> list[dict]:
    base = [lv for lv in b.get("levels") or [] if not lv.get("base_level_id")]
    return sorted(base, key=lambda lv: -float(lv.get("elevation") or 0.0))


def _ground_floor_z(b: dict) -> Optional[float]:
    base = sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                  key=lambda lv: float(lv.get("elevation") or 0.0))
    if not base:
        return None
    zero = [lv for lv in base if lv.get("order") == 0]
    up = [lv for lv in base if float(lv.get("elevation") or 0.0) >= -0.5]
    return float((zero or up or base)[0].get("elevation") or 0.0)


def _axis(w: dict):
    (ax, ay), (bx, by) = w["start"][:2], w["end"][:2]
    length = ((bx - ax) ** 2 + (by - ay) ** 2) ** 0.5
    if length < 1e-9:
        return None
    return (float(ax), float(ay)), ((bx - ax) / length, (by - ay) / length), length


def stands_on(upper: dict, w: dict) -> bool:
    """Whether wall ``upper`` (of the level above) stands on wall ``w`` (pure): parallel, on its line within half the
    thicker wall + ``STAND_GAP_M``, overlapping it over ``STAND_OVERLAP_M`` or ``STAND_SHARE`` of its length."""
    a = _axis(w)
    b = _axis(upper)
    if a is None or b is None:
        return False
    (ax, ay), (ux, uy), length = a
    (bx, by), (vx, vy), blen = b
    if abs(ux * vx + uy * vy) < 0.996:                    # within about 5 degrees
        return False
    tol = max(float(w.get("thickness") or 0.0), float(upper.get("thickness") or 0.0)) / 2.0 + STAND_GAP_M
    n = (-uy, ux)
    ends = [(bx, by), (bx + vx * blen, by + vy * blen)]
    if any(abs((px - ax) * n[0] + (py - ay) * n[1]) > tol for px, py in ends):
        return False
    t = sorted((px - ax) * ux + (py - ay) * uy for px, py in ends)
    overlap = min(length, t[1]) - max(0.0, t[0])
    return overlap >= min(STAND_OVERLAP_M, STAND_SHARE * length) and overlap > 0.0


def _classify(pt, outdoor: list, indoor: list, footprint, below=None) -> str:
    p = Point(pt)
    for _sid, poly in outdoor:
        if poly.covers(p):
            return "out"
    for poly in indoor:
        if poly.covers(p):
            return "room"
    if footprint is not None and footprint.covers(p):
        return "room"                       # an interior gap of the floor (no room drawn there): never the outside
    if below is not None and below.covers(p):
        return "room"                       # the floor below's rooms under it: a roof or a room not read, no drop
    return "none"


def edge_side(w: dict, outdoor: list, indoor: list, footprint, below=None) -> Optional[dict]:
    """``{"space", "share"}`` when wall ``w`` has an outdoor space on one side and the outside on the other over at
    least ``OUTDOOR_SHARE_MIN`` of its length and a room or a second outdoor space beyond no part of it; else None
    (pure). The outside is open air over a drop: no room of the floor (``indoor``, its closed ``footprint``) and none of
    the floor below (``below``: a setback's roof or a room the reading missed is no fall edge)."""
    ax = _axis(w)
    if ax is None:
        return None
    (x0, y0), (ux, uy), length = ax
    n = (-uy, ux)
    reach = float(w.get("thickness") or 0.0) / 2.0 + PROBE_M
    k = max(3, int(length / SAMPLE_M))
    hits: dict = {}
    good = 0
    for i in range(k):
        t = length * (0.05 + 0.9 * i / (k - 1))
        px, py = x0 + ux * t, y0 + uy * t
        sides = []
        for s in (1, -1):
            q = (px + n[0] * s * reach, py + n[1] * s * reach)
            kind = _classify(q, outdoor, indoor, footprint, below)
            sides.append(kind)
            if kind == "out":
                for sid, poly in outdoor:
                    if poly.covers(Point(q)):
                        hits[sid] = hits.get(sid, 0) + 1
                        break
        if "room" in sides or sides == ["out", "out"]:
            return None
        if "out" in sides:
            good += 1
    if good < OUTDOOR_SHARE_MIN * k or not hits:
        return None
    return {"space": max(hits, key=lambda s: hits[s]), "share": round(good / k, 3)}


def apply(build) -> list[dict]:
    """The rule (module docstring) on ``build.building`` (mutated); returns the records ``[{wall, level_id, space,
    kind, height, top_m, thickness, reason}]`` and the kept walls' reasons in ``level_inference.edge_guards``."""
    b = build.building
    g = _ground_floor_z(b)
    if g is None:
        return []
    levels = _levels_top_down(b)
    openings_on = {o.get("wall_id") for o in b.get("openings") or [] if o.get("wall_id")}
    site = b.get("site") if isinstance(b.get("site"), dict) else {}
    roof = b.get("roof") if isinstance(b.get("roof"), dict) else {}
    # a roof terrace cut into the roof keeps its own parapet (roof.parapet_cuts: the drawn or assumed height); its edge
    # walls are no carriers of anything either (``roof_edge``)
    roof_spaces = {str(o["room_id"]) for o in roof.get("openings") or [] if isinstance(o, dict) and o.get("room_id")}
    roof_edge: set = set()
    out, kept = [], []
    for i, lv in enumerate(levels):
        lid = lv["id"]
        if float(lv.get("elevation") or 0.0) - g < DROP_MIN_M - 1e-6:
            continue
        rooms = [r for r in b.get("rooms") or [] if r.get("level_id") == lid]
        outdoor = [(r["id"], p) for r in rooms if outdoor_room(r) for p in [_poly(r.get("polygon"))] if p is not None]
        outdoor += [(s["id"], p) for s in site.get("outdoor_spaces") or [] if isinstance(s, dict)
                    and s.get("level_id") == lid and str(s.get("kind") or "") in OUTDOOR_KINDS
                    for p in [_poly(s.get("polygon"))] if p is not None]
        if not outdoor:
            continue
        indoor = [p for r in rooms if not outdoor_room(r) for p in [_poly(r.get("polygon"))] if p is not None]
        footprint = None
        if indoor:
            closed = unary_union([p.buffer(FOOTPRINT_CLOSE_M, join_style=2) for p in indoor]).buffer(
                -FOOTPRINT_CLOSE_M, join_style=2)
            footprint = unary_union([Polygon(x.exterior) for x in getattr(closed, "geoms", [closed])
                                     if x.geom_type == "Polygon" and not x.is_empty]) if not closed.is_empty else None
        above = next((x for x in reversed(levels[:i]) if float(x.get("elevation") or 0.0)
                      > float(lv.get("elevation") or 0.0) + 0.5), None)
        under = next((x for x in levels[i + 1:] if float(x.get("elevation") or 0.0)
                      < float(lv.get("elevation") or 0.0) - 0.5), None)
        below_rooms = [p for r in b.get("rooms") or [] if under is not None and r.get("level_id") == under["id"]
                       and not outdoor_room(r) for p in [_poly(r.get("polygon"))] if p is not None]
        below = unary_union(below_rooms).buffer(-0.05, join_style=2) if below_rooms else None
        upper_walls = [w for w in b.get("walls") or [] if above is not None and w.get("level_id") == above["id"]
                       and not w.get("parapet") and w["id"] not in roof_edge]
        for w in b.get("walls") or []:
            if w.get("level_id") != lid or w.get("parapet") or w["id"] in openings_on or w.get("party_wall"):
                continue
            t = float(w.get("thickness") or 0.0)
            ax = _axis(w)
            if t <= 0.0 or t > MAX_T_M or ax is None or ax[2] < BLOCK_RATIO * t:
                continue                    # a structural wall, or a block (a wall's end or a pier), never a band
            side = edge_side(w, outdoor, indoor, footprint, below)
            if side is None:
                continue
            if side["space"] in roof_spaces:
                roof_edge.add(w["id"])
                kept.append({"wall": w["id"], "level_id": lid, "space": side["space"],
                             "reason": "the edge of a roof terrace cut into the roof: its parapet is the roof's "
                                       "(roof.parapet_cuts)"})
                continue
            carrier = next((u["id"] for u in upper_walls if stands_on(u, w)), None)
            if carrier is not None:
                kept.append({"wall": w["id"], "level_id": lid, "space": side["space"],
                             "reason": f"{carrier} of {above['id']} stands on it (it carries the slab above): kept "
                                       f"a full wall"})
                continue
            solid = t >= SOLID_MIN_T_M - 1e-9
            kind = "solid" if solid else "railing"
            height = GUARD_TOP_M if solid else RAIL_KERB_M
            reason = (f"{w['id']} ({t:.2f} m) runs along the open edge of {side['space']} ({side['share']:.0%} of "
                      f"it) with the outside beyond and no room: a guard, never a storey wall: "
                      + (f"a solid parapet {GUARD_TOP_M:.2f} m high (the drawn band is {t:.2f} m)" if solid else
                         f"a railing on a {RAIL_KERB_M:.2f} m kerb up to {GUARD_TOP_M:.2f} m (the drawn line is "
                         f"{t:.2f} m thin)") + " (inferred)")
            w.setdefault("drawn_height", w.get("height"))
            w["height"] = round(height, 3)
            w["parapet"] = True
            w["guard"] = {"top_m": GUARD_TOP_M, "kind": kind, "source": f"drawn band {t:.2f} m ({RULE})"}
            w["guard_of"] = side["space"]
            w["guard_drawn_thickness"] = round(t, 3)
            ev = w.setdefault("evidence", [])
            if isinstance(ev, list):
                ev.append(B.evidence((ev[0].get("file") if ev and isinstance(ev[0], dict) else None)
                                     or "building.json", "inferred", 0.7, rule=RULE, text=reason))
            out.append({"wall": w["id"], "level_id": lid, "space": side["space"], "kind": kind,
                        "height": round(height, 3), "top_m": GUARD_TOP_M, "thickness": round(t, 3),
                        "reason": reason})
    if (out or kept) and isinstance(b.get("level_inference"), dict):
        b["level_inference"]["edge_guards"] = {"guards": out, "kept": kept}
    if out:
        spaces = sorted({x["space"] for x in out})
        build.warn(f"edge guards: {len(out)} wall(s) on the open edges of {len(spaces)} balcony / terrace space(s) "
                   f"are guards ({', '.join(x['wall'] for x in out[:8])}{' ...' if len(out) > 8 else ''}): parapets "
                   f"or railings {GUARD_TOP_M:.2f} m high, never storey walls (inferred)")
    return out
