"""The ground floor of a block whose ground floor is not drawn (13 Nov 2026; the coordinator after the stage-1 review:
"what a viewer of the pod's plans and renders sees first"; the verified audit's amended R10 (4) and R43, review findings
S1-21a, S1-20b, S1-21c).

What: ``apply(build, ground, rec, texts, drawn, side)`` runs in ``completion._ground_floor`` when the storey rule read
the ground floor from the typical plan (``ground_from_typical``) and the area table's footprint (OTURUM) is smaller than
the typical floor (``cantilevers``). It changes the building in place and returns the record written to
``level_inference.storeys.ground_floor``:

1. **The footprint** (``footprint``): a closed outline drawn in the plan's region, one stroke or a chain of strokes with
   gaps of at most ``CHAIN_GAP_M``, on a building-outline layer (BİNA, OTURUM, İZDÜŞÜM, TABAN, KAT İZİ) or with a
   dashed linetype, whose area is the OTURUM text's within ``FOOT_MATCH`` (or 1 m2), inside the plan's outline with no
   corner more than ``FOOT_IN_M`` in, and holding the core (amended R10 (3)). None: nothing is cut (the conflict of
   ``completion._ground_floor`` stays).
2. **The cut** (``cut``): the ground storey keeps to the footprint. Its walls are clipped to it (a wall wholly outside
   goes), new exterior walls stand on the footprint's edges where no wall does (their outer face on the line), its
   rooms are clipped (a room left with under ``ROOM_MIN_M2`` or a fifth of itself goes, its furniture too), the
   openings on what went go (a window of a room that stays moves to the new facade when the plan draws windows), the
   ground slab follows the footprint, the balconies outside it are left off, a door that now opens onto nothing is a
   window. The upper storeys keep their outline: the parts past the footprint are cantilevers (amended R10 (4)).
3. **The entrance hall** (``entrance_hall``, the amended R43): when no way leads from outside to the core without
   crossing a flat, and the street side is known (a street text facing a facade that is no party wall), the rooms
   between the core and the street facade (the shortest chain of rooms, never a wet room, a shaft, a lift or a light
   well) become the building's entrance hall ('Bina Giriş Holü', a common area), joined to the core and to each other
   by inferred openings, with an inferred entrance door on the street facade and its ``site.entrances`` record (steps
   from the ground the reading knows). The street unknown, or no chain: no geometry, a question.

Everything is ``inferred`` / ``adjusted_by_ai`` (by code) with its reason and evidence, listed in ``needs_review`` and
asked as the architect's N1 answers (``questions``: ``wenart.blender.architect_storeys``). A drawn ground floor is never
touched (the rule runs only on a storey the storey rule inferred). Each change passes ``rule_guards.blocked``
(``ground_cut``, ``entrance_hall``).

Why: real21 and real20 draw one typical floor; the reading built their ground floors as that floor (the typical
outline standing past the drawn footprint, balconies at the ground, six flats wall to wall around the core and no way
in from the street).

How: shapely on the building dict; no AI.
"""
from __future__ import annotations

import math
import re
import statistics
from typing import Optional

from shapely.geometry import LineString, MultiPoint, Point, Polygon
from shapely.ops import unary_union

from wenart import building as B
from wenart import geometry as G
from wenart.ingest import completion as CP
from wenart.ingest import rule_guards as RG

OUTLINE_LAYER_RE = re.compile(r"bina|oturum|izdusum|taban|kat\s*izi|zemin\s*izi|footprint|outline")
DASHED_RE = re.compile(r"hidden|dash|gizli|kesik")
NOT_OUTLINE_RE = re.compile(r"merd|stair|treppe|kapi|door|penc|window|mobil|furn|dim|olcu|tarama|hatch|aks|axis|grid")
CHAIN_GAP_M = 0.15              # the strokes of one outline meet within this (amended R10 (3))
FOOT_MATCH = 0.03               # a footprint's area is the OTURUM text's within this share (or 1 m2) ...
FOOT_IN_M = 2.0                 # ... inside the plan's outline, no corner further in than this
ROOM_MIN_M2 = 1.0               # a room cut to less than this (or a fifth of itself) goes
WALL_MIN_M = 0.10
COVER_M = 0.25                  # a footprint edge this close to a kept parallel wall's face is that wall's
JAMB_M = 0.10                   # a moved window keeps this much wall beside it (R20-04)
PIT_WIDTH_M = 0.30              # a piece of the footprint past the slab above wider than this ... (R20-02)
PIT_MIN_M2 = 0.5                # ... and larger than this: the slab above covers it
LOBBY_LABEL = "Bina Giriş Holü"
LOBBY_WIDTH_M = 1.50            # the entrance hall's passages (R43: at least 1.5 m wide where the walls allow)
NO_LOBBY_TYPES = ("bathroom", "wc", "shower", "toilet", "shaft", "stair", "balcony", "terrace", "garage", "technical")


# ------------------------------------------------------------------------------------------------- 1. footprint
def _chains(drawn) -> list:
    """``[(Polygon, [stroke ids], layer, linetype)]``: the closed outlines of the outline-like strokes of a page, a
    closed stroke or a chain of strokes meeting within ``CHAIN_GAP_M`` (building metres)."""
    pieces = []
    for st in getattr(drawn, "strokes", None) or []:
        layer = B.fold_ascii(str(getattr(st, "layer", "") or "")).lower()
        lt = str(getattr(st, "linetype", "") or "").lower()
        if getattr(st, "arc", None) or len(st.pts) < 2 or NOT_OUTLINE_RE.search(layer) or \
                not (OUTLINE_LAYER_RE.search(layer) or DASHED_RE.search(lt)):
            continue
        pts = [G.apply_affine(drawn.m6, p) for p in st.pts]
        if getattr(st, "closed", False) and len(pts) >= 3:
            pts = pts + [pts[0]]
        pieces.append({"pts": pts, "ids": [st.id], "layer": getattr(st, "layer", None), "lt": getattr(st, "linetype", None)})
    if len(pieces) > 400:
        return []
    out = []
    used = [False] * len(pieces)
    for i, p in enumerate(pieces):
        if used[i]:
            continue
        used[i] = True
        line, ids = list(p["pts"]), list(p["ids"])
        grew = True
        while grew and math.dist(line[0], line[-1]) > CHAIN_GAP_M:
            grew = False
            for j, q in enumerate(pieces):
                if used[j]:
                    continue
                a, z = q["pts"][0], q["pts"][-1]
                if math.dist(line[-1], a) <= CHAIN_GAP_M:
                    line += q["pts"][1:]
                elif math.dist(line[-1], z) <= CHAIN_GAP_M:
                    line += list(reversed(q["pts"]))[1:]
                elif math.dist(line[0], z) <= CHAIN_GAP_M:
                    line = q["pts"][:-1] + line
                elif math.dist(line[0], a) <= CHAIN_GAP_M:
                    line = list(reversed(q["pts"]))[:-1] + line
                else:
                    continue
                used[j], grew = True, True
                ids += q["ids"]
        if len(line) >= 4 and math.dist(line[0], line[-1]) <= CHAIN_GAP_M:
            poly = Polygon(line[:-1] if math.dist(line[0], line[-1]) < 1e-9 else line).buffer(0)
            if poly.geom_type == "Polygon" and poly.area > 1.0:
                out.append((poly, ids, p["layer"], p["lt"]))
    return out


def footprint(b: dict, lid: str, drawn, oturum: float) -> Optional[dict]:
    """The footprint outline of the module docstring (1), or None (pure but for the drawing's query)."""
    from wenart.ingest import core_rules as CR

    if drawn is None or not oturum:
        return None
    level = CP.Level(b, lid)
    plan = level.outline
    if plan is None:
        return None
    core = [level.polys[i] for i in CR.core_rooms(b, level) if i in level.polys]
    # inside the plan: its filled outline or, where the reading lost a facade, the hull of its walls
    hull = MultiPoint([tuple(p[:2]) for w in level.walls.values() for p in (w["start"], w["end"])]).convex_hull
    area = unary_union([plan, hull]) if hull.geom_type == "Polygon" else plan
    best = None
    for poly, ids, layer, lt in _chains(drawn):
        if abs(poly.area - oturum) > max(FOOT_MATCH * oturum, 1.0):
            continue
        if poly.difference(area.buffer(0.3)).area > 0.02 * poly.area:
            continue
        rings = [plan.exterior] + ([hull.exterior] if hull.geom_type == "Polygon" else [])
        if any(min(r.distance(Point(c)) for r in rings) > FOOT_IN_M for c in list(poly.exterior.coords)[:-1]):
            continue
        if core and not all(poly.buffer(0.05).contains(c.representative_point()) for c in core):
            continue
        key = abs(poly.area - oturum)
        if best is None or key < best[0]:
            best = (key, poly, ids, layer, lt)
    if best is None:
        return None
    _k, poly, ids, layer, lt = best
    return {"polygon": poly, "entities": ids, "layer": layer, "linetype": lt, "area_m2": round(poly.area, 1)}


# ------------------------------------------------------------------------------------------------------- 2. cut
def _ev(b: dict, lid: str, rule: str, text: str, foot: dict) -> dict:
    return {"file": CP._ev_file(b, lid), "method": "inferred", "confidence": 0.5, "rule": rule, "text": text,
            "entity": ",".join(foot.get("entities") or [])[:200] or None, "layer": foot.get("layer")}


def _clip_wall(w: dict, area) -> Optional[tuple]:
    """``(start, end)`` of the longest part of a wall's axis inside ``area``, ``()`` when wholly inside, None when
    nothing is left."""
    axis = LineString([w["start"], w["end"]])
    if axis.length < 1e-9:
        return None
    inside = axis.intersection(area)
    if inside.is_empty:
        return None
    if inside.length >= axis.length - 0.01:
        return ()
    parts = [g for g in getattr(inside, "geoms", [inside]) if g.geom_type == "LineString"]
    if not parts:
        return None
    best = max(parts, key=lambda g: g.length)
    if best.length < WALL_MIN_M:
        return None
    (x0, y0), (x1, y1) = best.coords[0], best.coords[-1]
    # keep the wall's direction
    a = w["start"]
    if math.dist((x1, y1), a) < math.dist((x0, y0), a):
        (x0, y0), (x1, y1) = (x1, y1), (x0, y0)
    return [round(x0, 4), round(y0, 4)], [round(x1, 4), round(y1, 4)]


def cut(build, b: dict, lid: str, foot: dict, why: str) -> dict:
    """The cut of the module docstring (2); the record."""
    poly = foot["polygon"]
    rec = {"rooms_dropped": [], "rooms_cut": [], "walls_removed": [], "walls_cut": [], "walls_added": [],
           "openings_removed": [], "windows_moved": [], "doors_to_windows": [], "furniture_removed": [],
           "spaces_left_off": []}
    level0 = CP.Level(b, lid)
    rooms_before = {r["id"]: level0.polys[r["id"]] for r in level0.rooms}
    walls = [w for w in b.get("walls") or [] if w.get("level_id") == lid and w.get("start") and w.get("end")]
    outer = [float(w.get("thickness") or 0.0) for w in walls if w.get("exterior") and w.get("thickness")]
    t_ext = round(statistics.median(outer), 3) if outer else 0.20
    height = next((w.get("height") for w in walls if w.get("exterior") and w.get("height")), None)
    draws_windows = any(o.get("type") == "window" and not o.get("inferred") for o in level0.openings)
    # walls
    gone_walls, kept = set(), []
    edges = [LineString([p, q]) for p, q in zip(list(poly.exterior.coords), list(poly.exterior.coords)[1:])]
    for w in walls:
        res = _clip_wall(w, poly.buffer(float(w.get("thickness") or 0.15) / 2.0 + 0.02, join_style=2))
        if res is not None and not _along_edge(w, edges):
            # 20 Nov 2026 (pre-pod review R21-01: cut walls stood 0.07-0.12 m out of the new facade, thin fins on the
            # street): a wall that crosses the footprint line stops at the line (inside the new facade wall's body);
            # a wall along an edge keeps the half-thickness margin
            tight = _clip_wall(w, poly.buffer(0.005, join_style=2))
            if tight:
                res = tight
        if res is None:
            gone_walls.add(w["id"])
            rec["walls_removed"].append(w["id"])
            continue
        if res:
            w.setdefault("drawn_start", list(w["start"]))
            w.setdefault("drawn_end", list(w["end"]))
            w["start"], w["end"] = res
            w["adjusted_by_ai"] = {"by": "code", "rule": "ground_cut", "reason": why + f": {w['id']} cut at the "
                                   f"footprint line", "changed": {"start": w["drawn_start"], "end": w["drawn_end"]}}
            rec["walls_cut"].append(w["id"])
        kept.append(w)
    b["walls"] = [w for w in b.get("walls") or [] if w["id"] not in gone_walls]
    # new facade walls on the footprint's edges no kept wall stands on
    ring = list(poly.exterior.coords)
    if Polygon(ring).exterior.is_ccw is False:
        ring = list(reversed(ring))
    new_walls = []
    for p, q in zip(ring, ring[1:]):
        el = math.dist(p, q)
        if el < 0.3:
            continue
        u = ((q[0] - p[0]) / el, (q[1] - p[1]) / el)
        n_in = (-u[1], u[0])                                   # ccw ring: the inside is on the left
        covered = []
        for w in kept:
            a, wu, wl = CP._axis(w)
            if wl < 0.1 or abs(u[0] * wu[1] - u[1] * wu[0]) > CP.PARALLEL_SIN:
                continue
            off = (a[0] - p[0]) * n_in[0] + (a[1] - p[1]) * n_in[1]
            if abs(off) > float(w.get("thickness") or 0.15) / 2.0 + COVER_M:
                continue
            ts = sorted(((c[0] - p[0]) * u[0] + (c[1] - p[1]) * u[1]) for c in (w["start"], w["end"]))
            covered.append((ts[0] - 0.05, ts[1] + 0.05))
        free, t = [], 0.0
        for c0, c1 in sorted(covered):
            if c0 > t + 0.5:
                free.append((t, min(c0, el)))
            t = max(t, c1)
        if el - t > 0.5:
            free.append((t, el))
        for t0, t1 in free:
            t0, t1 = max(0.0, t0), min(el, t1)
            if t1 - t0 < 0.5:
                continue
            s = (p[0] + u[0] * t0 + n_in[0] * t_ext / 2.0, p[1] + u[1] * t0 + n_in[1] * t_ext / 2.0)
            e = (p[0] + u[0] * t1 + n_in[0] * t_ext / 2.0, p[1] + u[1] * t1 + n_in[1] * t_ext / 2.0)
            wid = build.ids.next("wall", lid)
            text = why + ": a new facade wall on the drawn footprint line (inferred)"
            w = {"id": wid, "level_id": lid, "start": [round(s[0], 4), round(s[1], 4)],
                 "end": [round(e[0], 4), round(e[1], 4)], "thickness": t_ext, "height": height, "exterior": True,
                 "status": "unverified", "inferred": True, "evidence": [_ev(b, lid, "ground_footprint_wall", text, foot)]}
            new_walls.append(w)
            rec["walls_added"].append(wid)
    stopped = _stop_at_party(new_walls, kept, poly)
    if stopped:
        rec["walls_stopped_at_party"] = sorted(set(stopped))
    b["walls"].extend(new_walls)
    # rooms: what lies past the footprint or in a new wall goes
    bands = [_band(w) for w in new_walls]
    keep_area = poly.difference(unary_union(bands)) if bands else poly
    gone_rooms = set()
    for r in [r for r in b.get("rooms") or [] if r.get("level_id") == lid]:
        p0 = rooms_before.get(r["id"])
        if p0 is None:
            continue
        p1 = p0.intersection(keep_area)
        if p1.geom_type != "Polygon":
            parts = [g for g in getattr(p1, "geoms", []) if g.geom_type == "Polygon"]
            p1 = max(parts, key=lambda g: g.area) if parts else Polygon()
        if p1.area >= p0.area - 0.05:
            continue
        if p1.is_empty or p1.area < max(ROOM_MIN_M2, 0.2 * p0.area):
            gone_rooms.add(r["id"])
            rec["rooms_dropped"].append(r["id"])
            continue
        r.setdefault("drawn_polygon", [list(c) for c in r["polygon"]])
        r["polygon"] = [[round(x, 4), round(y, 4)] for x, y in list(p1.exterior.coords)[:-1]]
        r["area_computed"] = round(p1.area, 3)
        r["adjusted_by_ai"] = {"by": "code", "rule": "ground_cut", "reason": why + f": {r['id']} cut at the "
                               f"footprint line ({p0.area:.1f} -> {p1.area:.1f} m2)", "changed": {"area": round(p0.area, 2)}}
        rec["rooms_cut"].append(r["id"])
    b["rooms"] = [r for r in b.get("rooms") or [] if r["id"] not in gone_rooms]
    _repoint_same_as(b, gone_rooms | set(rec["rooms_cut"]))
    # openings
    level = CP.Level(b, lid)
    keep_ops, moved = [], []
    for o in b.get("openings") or []:
        if o.get("level_id") != lid or o.get("virtual"):
            keep_ops.append(o)
            continue
        w = level.walls.get(o.get("wall_id"))
        gone = w is None or not o.get("center")
        if not gone:
            a, u, length = CP._axis(w)
            t = (o["center"][0] - a[0]) * u[0] + (o["center"][1] - a[1]) * u[1]
            gone = not (-0.05 <= t <= length + 0.05) or not poly.buffer(0.3).contains(Point(o["center"][:2]))
        if not gone:
            keep_ops.append(o)
            continue
        rec["openings_removed"].append(o["id"])
        if o.get("type") == "window" and draws_windows and o.get("center"):
            moved.append(o)
    b["openings"] = keep_ops
    level = CP.Level(b, lid)
    for o in moved:
        new = _move_window(build, b, level, o, new_walls, rooms_before, why, foot)
        if new is not None:
            b["openings"].append(new)
            level.openings.append(new)
            rec["windows_moved"].append({"from": o["id"], "to": new["id"]})
    # furniture of the rooms that went or past the footprint
    keep_f = []
    for f in b.get("furniture") or []:
        fp = f.get("footprint") or {}
        if f.get("level_id") == lid and (f.get("room_id") in gone_rooms or (fp.get("center") and not
                                         keep_area.buffer(0.05).contains(Point(fp["center"][:2])))):
            rec["furniture_removed"].append(f["id"])
            continue
        keep_f.append(f)
    b["furniture"] = keep_f
    # the ground slab follows the footprint
    for s in b.get("slabs") or []:
        if s.get("above_level_id") == lid and not s.get("below_level_id") and s.get("outline"):
            s.setdefault("drawn_outline", s["outline"])
            s["outline"] = [[round(x, 4), round(y, 4)] for x, y in list(poly.exterior.coords)[:-1]]
            s["outline_source"] = "ground_footprint"
    # 20 Nov 2026 (pre-pod review R20-02: 21.8 m2 of the cut ground floor's closed rooms had no ceiling up to the roof,
    # the slab over it kept the open typical outline): the slab over the cut storey covers the footprint too (the
    # pieces past it become floor of the storey above), adjusted_by_ai with the reason
    for s in b.get("slabs") or []:
        if s.get("below_level_id") != lid or s.get("variants") or not s.get("outline") or len(s["outline"]) < 3:
            continue
        sp = Polygon(s["outline"])
        sp = sp if sp.is_valid else sp.buffer(0)
        past = poly.difference(sp)
        pieces = [g for g in getattr(past, "geoms", [past]) if g.geom_type == "Polygon" and g.area >= PIT_MIN_M2
                  and not g.buffer(-PIT_WIDTH_M / 2.0).is_empty]
        if not pieces:
            continue
        grown = unary_union([sp] + pieces)
        if grown.geom_type != "Polygon":
            grown = max(grown.geoms, key=lambda g: g.area)
        text = (why + f": {sum(g.area for g in pieces):.1f} m2 of the footprint lay past the slab over {lid} "
                f"({len(pieces)} piece(s)); the slab covers them (floor of the storey above)")
        s.setdefault("drawn_outline", s["outline"])
        s["outline"] = [[round(x, 4), round(y, 4)] for x, y in list(grown.exterior.coords)[:-1]]
        s["adjusted_by_ai"] = {"by": "code", "rule": "ground_cut", "reason": text,
                               "changed": {"area": round(sp.area, 2)}}
        rec["slab_above_extended"] = {"slab": s["id"], "pieces_m2": [round(g.area, 2) for g in pieces],
                                      "reason": text}
    # the balconies past the footprint are left off
    site = b.get("site") if isinstance(b.get("site"), dict) else {}
    keep_s = []
    for s in site.get("outdoor_spaces") or []:
        p = CP._poly(s.get("polygon"))
        if s.get("level_id") == lid and p is not None and p.difference(poly).area >= 0.5 * p.area and \
                str(s.get("kind")) in CP.OPEN_AIR:
            rec["spaces_left_off"].append(s["id"])
            continue
        keep_s.append(s)
    if rec["spaces_left_off"]:
        site["outdoor_spaces"] = keep_s
    # a door that now opens onto nothing is a window (its balcony left off, its room cut)
    level = CP.Level(b, lid)
    from wenart.ingest import core_rules as CR
    for o in level.openings:
        if o.get("type") != "door" or o.get("virtual") or o.get("lift_door"):
            continue
        sides = CR._sides(level, o)
        if "outside" not in [s[0] for s in sides] or not any(s[1] is not None for s in sides):
            continue
        head = float(o.get("height") or 2.1)
        text = why + f": {o['id']} would open onto nothing on the ground floor (its balcony or room is past the " \
                     f"footprint): a window"
        o.update(drawn_type=o.get("drawn_type") or "door", type="window", sill_height=0.9,
                 height=round(max(0.6, head - 0.9), 3), operation=None, operation_source=None, swing_side=None,
                 adjusted_by_ai={"by": "code", "rule": "ground_cut_window", "reason": text,
                                 "changed": {"type": "door", "height": head}})
        rec["doors_to_windows"].append(o["id"])
    ops = {o["id"]: o for o in b.get("openings") or []}
    if isinstance(site, dict) and site.get("entrances"):
        site["entrances"] = [e for e in site["entrances"] if (ops.get(e.get("door_id")) or {}).get("type") == "door"]
    return rec


def _along_edge(w: dict, edges: list) -> bool:
    """True when the wall runs along an edge of the footprint (parallel, its axis within half its thickness plus
    ``COVER_M`` of the edge over a part of its length; pure)."""
    a, u, length = CP._axis(w)
    if length < 1e-6:
        return False
    axis = LineString([w["start"][:2], w["end"][:2]])
    reach = float(w.get("thickness") or 0.15) / 2.0 + COVER_M
    for e in edges:
        (x0, y0), (x1, y1) = e.coords[0], e.coords[-1]
        el = math.dist((x0, y0), (x1, y1))
        if el < 1e-6 or abs(u[0] * (y1 - y0) / el - u[1] * (x1 - x0) / el) > CP.PARALLEL_SIN:
            continue
        if axis.intersection(e.buffer(reach)).length >= min(0.5, 0.5 * length):
            return True
    return False


def _stop_at_party(new_walls: list, kept: list, poly) -> list:
    """20 Nov 2026 (pre-pod review R21-01: the cadastral footprint followed a slanted party wall the reader had
    straightened, and the new facade wall ran 0.155 m past the party wall's outer face): a new facade wall's end past
    the outer face of a kept party or exterior wall it crosses stops at that face. Returns the ids moved (in place)."""
    moved = []
    centre = poly.centroid
    for w in new_walls:
        for k in kept:
            if not (k.get("exterior") or k.get("party_wall")):
                continue
            ka, ku, kl = CP._axis(k)
            wa, wu, wl = CP._axis(w)
            if kl < 0.3 or abs(ku[0] * wu[1] - ku[1] * wu[0]) < 0.7:
                continue                                        # only a wall the new one meets at an angle
            kn = (-ku[1], ku[0])
            inside = (centre.x - ka[0]) * kn[0] + (centre.y - ka[1]) * kn[1]
            sgn = 1.0 if inside >= 0 else -1.0
            half = float(k.get("thickness") or 0.15) / 2.0
            for key in ("start", "end"):
                p = w[key]
                d = ((p[0] - ka[0]) * kn[0] + (p[1] - ka[1]) * kn[1]) * sgn       # > 0: on the building's side
                t = (p[0] - ka[0]) * ku[0] + (p[1] - ka[1]) * ku[1]
                if d >= -half - 1e-3 or d < -half - 0.5 or not (-0.3 <= t <= kl + 0.3):
                    continue
                other = w["end" if key == "start" else "start"]
                od = ((other[0] - ka[0]) * kn[0] + (other[1] - ka[1]) * kn[1]) * sgn
                if od <= 0:
                    continue
                # slide p along the new wall until it stands on the outer face (d = -half)
                f = (od + half) / (od - d)
                w[key] = [round(other[0] + (p[0] - other[0]) * f, 4), round(other[1] + (p[1] - other[1]) * f, 4)]
                moved.append(w["id"])
    return moved


def _band(w: dict) -> Polygon:
    """The footprint of a wall: its axis grown by half its thickness to each side."""
    _a, u, _l = CP._axis(w)
    h = float(w.get("thickness") or 0.15) / 2.0
    n = (-u[1] * h, u[0] * h)
    (sx, sy), (ex, ey) = w["start"][:2], w["end"][:2]
    return Polygon([(sx - n[0], sy - n[1]), (ex - n[0], ey - n[1]), (ex + n[0], ey + n[1]), (sx + n[0], sy + n[1])])


def _repoint_same_as(b: dict, changed: set) -> None:
    """The rooms of the copies that took a changed ground-floor room as their model (``same_as``) take the lowest
    copy's room instead (that room is the model again: furnished once, copied to the others)."""
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    for rid in changed:
        copies = sorted((r for r in b.get("rooms") or [] if r.get("same_as") == rid),
                        key=lambda r: ((levels.get(r.get("level_id")) or {}).get("order") or 0, r["id"]))
        if not copies:
            continue
        model = copies[0]
        model.pop("same_as", None)
        for r in copies[1:]:
            r["same_as"] = model["id"]


def _move_window(build, b, level, o, new_walls, rooms_before, why, foot) -> Optional[dict]:
    """A window of a removed facade stretch moved onto the new facade wall in front of its room, at its place along
    the wall (inferred), or None."""
    c = o["center"][:2]
    room = next((rid for rid, p in rooms_before.items() if p.distance(Point(c)) <= 0.5
                 and any(r["id"] == rid for r in level.rooms)), None)
    if room is None:
        return None
    rp = level.polys.get(room)
    for w in new_walls:
        a, u, length = CP._axis(w)
        t = (c[0] - a[0]) * u[0] + (c[1] - a[1]) * u[1]
        half = float(o.get("width") or 0.9) / 2.0
        reach = float(w.get("thickness") or 0.2) / 2.0 + 0.2
        if rp is None:
            continue
        # 20 Nov 2026 (pre-pod review R20-04: a drawn 1.40 m bedroom window missed the new wall's end by 5.7 cm and
        # was dropped): the window slides along the wall into the room's stretch, a jamb from each end; dropped only
        # when the stretch is shorter than the window
        stretch = LineString([a, (a[0] + u[0] * length, a[1] + u[1] * length)]).intersection(rp.buffer(reach))
        parts = [g for g in getattr(stretch, "geoms", [stretch]) if g.geom_type == "LineString" and g.length > 0]
        best = None
        for g in parts:
            ts = sorted((p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1] for p in (g.coords[0], g.coords[-1]))
            lo = max(ts[0], 0.0) + half + JAMB_M
            hi = min(ts[1], length) - half - JAMB_M
            if lo > hi:
                continue
            t2 = min(max(t, lo), hi)
            if best is None or abs(t2 - t) < abs(best - t):
                best = t2
        if best is None:
            continue
        q = (a[0] + u[0] * best, a[1] + u[1] * best)
        if rp.distance(Point(q)) > reach:
            continue
        shift = f", moved {abs(best - t):.2f} m along {w['id']} to stay on the wall" if abs(best - t) > 0.005 else ""
        text = why + f": the window {o['id']} of {room} moved with the facade onto {w['id']}{shift} (inferred)"
        return {"id": build.ids.next("window", level.lid), "type": "window", "level_id": level.lid, "wall_id": w["id"],
                "center": [round(q[0], 4), round(q[1], 4)], "width": o.get("width"), "height": o.get("height"),
                "sill_height": o.get("sill_height"), "swing_side": None, "status": "unverified", "inferred": True,
                "inference": {"rule": "ground_window_moved", "room_id": room, "from": o["id"], "reason": text},
                "evidence": [_ev(b, level.lid, "ground_window_moved", text, foot)]}
    return None


# ------------------------------------------------------------------------------------------------ 3. entrance hall
def street_edge(level: "CP.Level", side: list) -> Optional[tuple]:
    """``(edge, text)``: the outline edge a street text faces (its outward side towards the text, the text's foot
    within the edge extent with 2 m to spare, the nearest), never a party wall's side; None without one."""
    if level.outline is None:
        return None
    ring = list(level.outline.exterior.coords)
    if not Polygon(ring).exterior.is_ccw:
        ring = list(reversed(ring))
    best = None
    for sp in side or []:
        if sp.get("kind") != "street" or not sp.get("at"):
            continue
        x, y = sp["at"][:2]
        for p, q in zip(ring, ring[1:]):
            el = math.dist(p, q)
            if el < 1.0:
                continue
            u = ((q[0] - p[0]) / el, (q[1] - p[1]) / el)
            n_out = (u[1], -u[0])
            t = (x - p[0]) * u[0] + (y - p[1]) * u[1]
            d = (x - p[0]) * n_out[0] + (y - p[1]) * n_out[1]
            if d <= 0 or not -2.0 <= t <= el + 2.0:
                continue
            party = [w for w in level.walls.values() if isinstance(w.get("party_wall"), dict) and CP._on_side(w, (p, q))]
            if party:
                continue
            if best is None or d < best[0]:
                best = (d, (p, q), sp.get("text"))
    if best is None:
        return None
    # the whole facade: the outline edges on that line end to end (CS1-06's run)
    return CP._run(list(zip(ring, ring[1:])), best[1]), best[2]


def _shared(level: "CP.Level", ra: str, rb: str) -> Optional[tuple]:
    """``(wall, t0, t1)``: the longest stretch of a wall with room ``ra`` on one side and ``rb`` on the other."""
    best = None
    for w in level.walls.values():
        a, u, length = CP._axis(w)
        if length < 0.5:
            continue
        n = (-u[1], u[0])
        reach = float(w.get("thickness") or 0.15) / 2.0 + CP.PROBE_M
        steps = max(1, int(length / CP.SAMPLE_M))
        cur = None
        for k in range(steps + 1):
            t = length * k / steps
            c = (a[0] + u[0] * t, a[1] + u[1] * t)
            ids = {(level.room_at((c[0] + s * n[0] * reach, c[1] + s * n[1] * reach)) or {}).get("id") for s in (1, -1)}
            if ids == {ra, rb}:
                cur = (w, cur[1] if cur else t, t)
                if best is None or cur[2] - cur[1] > best[2] - best[1]:
                    best = cur
            else:
                cur = None
    return best


def _adjacent(level: "CP.Level", rooms: dict) -> dict:
    out = {rid: set() for rid in rooms}
    ids = sorted(rooms)
    for i, a in enumerate(ids):
        pa = level.polys[a].buffer(0.35)
        for bb in ids[i + 1:]:
            inter = pa.intersection(level.polys[bb].buffer(0.35))
            if not inter.is_empty and inter.area >= 0.35:
                out[a].add(bb)
                out[bb].add(a)
    return out


def entrance_hall(build, b: dict, lid: str, side: list, foot: Optional[dict], why: str) -> dict:
    """The entrance hall of the module docstring (3); the record (``open`` with the question when nothing is made)."""
    from wenart.ingest import core_rules as CR

    rec = {"rooms": [], "openings": [], "door": None, "street": None, "open": None, "flat_rooms_left": []}
    level = CP.Level(b, lid)
    core = CR.core_rooms(b, level)
    if not core or level.outline is None:
        rec["open"] = "no common core is read on the ground floor: no entrance hall is inferred"
        return rec
    lv = next((x for x in b.get("levels") or [] if x["id"] == lid), {})
    ents = [e for e in (b.get("site") or {}).get("entrances") or [] if e.get("level_id") == lid
            and not e.get("into_air") and not e.get("upper_floor") and CR.lost_behind(lv, e) is None]
    if any(CR._leads_to_core(b, e, core) for e in ents):
        return rec                                    # a way in reaches the core already (R43's guard)
    found = street_edge(level, side)
    if found is None:
        rec["open"] = ("the ground floor's core reaches no facade and the street side is not known (no street text "
                       "faces a free facade): which side is the street? (no entrance hall inferred)")
        return rec
    (p, q), street = found
    rec["street"] = street
    edge = LineString([p, q])
    rooms = {r["id"]: r for r in level.rooms}
    adj = _adjacent(level, rooms)

    def on_street(rid):
        return any(f["kind"] == "outside" and edge.distance(Point(level.at(f["wall_id"], (f["t0"] + f["t1"]) / 2.0)))
                   <= float(level.walls[f["wall_id"]].get("thickness") or 0.2) + 0.3 and f["t1"] - f["t0"] >= 1.3
                   for f in level.faces(rooms[rid]))

    def passable(rid):
        r = rooms[rid]
        mrr = level.polys[rid].minimum_rotated_rectangle
        pts = list(mrr.exterior.coords)[:3] if mrr.geom_type == "Polygon" else []
        short = min(math.dist(pts[0], pts[1]), math.dist(pts[1], pts[2])) if len(pts) == 3 else 0.0
        return r.get("room_type") not in NO_LOBBY_TYPES and not CP.is_lift(r) and rid not in level.wells and \
            short >= LOBBY_WIDTH_M - 0.05                 # R43: a hall at least 1.5 m wide
    starts = [rid for rid in core if rid in rooms and not CP.is_lift(rooms[rid])]
    # breadth first from the core: the fewest rooms, then the shortest walk
    best, todo, seen = None, [(0, 0.0, s, [s]) for s in starts], set(starts)
    while todo:
        todo.sort(key=lambda x: (x[0], x[1]))
        n, dist, rid, path = todo.pop(0)
        if n and on_street(rid):
            best = path
            break
        for nb in sorted(adj.get(rid) or ()):
            if nb in seen or nb in core or not passable(nb):
                continue
            seen.add(nb)
            c0, c1 = level.polys[rid].centroid, level.polys[nb].centroid
            todo.append((n + 1, dist + c0.distance(c1), nb, path + [nb]))
    if best is None:
        rec["open"] = (f"no chain of rooms leads from the core to the street facade ({street}) without a wet room, a "
                       f"shaft or a lift: no entrance hall inferred (which layout has the ground floor?)")
        return rec
    path = best
    if RG.blocked("entrance_hall", b, {"level_id": lid, "room": path[-1], "why": f"street {street}"}):
        return rec
    hall_rooms = path[1:]
    text = (f"{why}; no way leads from the street to the core: the rooms between the core and the street facade "
            f"({street}) become the building's entrance hall (one of several layouts: a corridor, a hall replacing "
            f"the front flat, shops on the street; inferred, to review)")
    for rid in hall_rooms:
        r = rooms[rid]
        r["adjusted_by_ai"] = {"by": "code", "rule": "entrance_hall", "reason": text,
                               "changed": {"label": r.get("label"), "room_type": r.get("room_type"),
                                           "room_subtype": r.get("room_subtype")}}
        r.update(label=LOBBY_LABEL, room_type="hall", room_subtype="common", inferred=True, entrance_hall=True,
                 has_documented_furniture=False)
        r.pop("same_as", None)
        rec["rooms"].append(rid)
    _repoint_same_as(b, set(hall_rooms))
    b["furniture"] = [f for f in b.get("furniture") or [] if f.get("room_id") not in set(hall_rooms)]
    # the passages: core -> hall -> hall ..., where no door or opening joins them yet
    level = CP.Level(b, lid)
    links = CR._links(level)
    for ra, rb in zip(path, path[1:]):
        if any({ra, rb} == {x, y} for x, y, _o in links):
            continue
        sh = _shared(level, ra, rb)
        if sh is None:
            continue
        w, t0, t1 = sh
        width = min(LOBBY_WIDTH_M, (t1 - t0) - 0.2)
        if width < 0.9:
            continue
        oid = build.ids.next("door", lid)
        o = {"id": oid, "type": "opening", "level_id": lid, "wall_id": w["id"],
             "center": level.at(w["id"], (t0 + t1) / 2.0), "width": round(width, 3), "height": 2.1,
             "sill_height": None, "swing_side": None, "status": "unverified", "inferred": True,
             "inference": {"rule": "entrance_hall", "reason": text},
             "evidence": [{"file": CP._ev_file(b, lid), "method": "inferred", "confidence": 0.3,
                           "rule": "entrance_hall", "text": f"the entrance hall's passage between {ra} and {rb}"}]}
        b["openings"].append(o)
        level.openings.append(o)
        rec["openings"].append(oid)
    # the entrance door on the street facade
    last = rooms[path[-1]]
    faces = [f for f in level.faces(last) if f["kind"] == "outside" and edge.distance(
        Point(level.at(f["wall_id"], (f["t0"] + f["t1"]) / 2.0))) <= float(level.walls[f["wall_id"]].get("thickness")
                                                                          or 0.2) + 0.3]
    cand = sorted(((f, p0, p1) for f in faces for p0, p1 in level.free(f)), key=lambda x: -(x[2] - x[1]))
    if not cand or cand[0][2] - cand[0][1] < CR.ENTRANCE_DOOR_M[0]:
        rec["open"] = f"the entrance hall reaches the street facade ({street}) but no free stretch takes a door"
        return rec
    f, p0, p1 = cand[0]
    lv = next(x for x in b["levels"] if x["id"] == lid)
    dtext = (f"the building entrance on the street facade ({street}) into the inferred entrance hall {last['id']} "
             f"(R43; inferred)")
    o = CP._new_opening("door", build.ids.next("door", lid), level, f["wall_id"], (p0 + p1) / 2.0,
                        CR.ENTRANCE_DOOR_M[0], CR.ENTRANCE_DOOR_M[1], None, dtext, last, f, CP._ev_file(b, lid),
                        lv.get("region_id"), "default entrance door")
    o["inference"]["rule"] = "inferred_entrance"
    o["operation"] = "double"
    b["openings"].append(o)
    ent = CR._entrance_record(b, o, level, lv, last, f, dtext)
    others = (b.get("site") or {}).get("entrances") or []
    levels = {x["id"]: x for x in b.get("levels") or []}
    if not any(e.get("main") and CR.lost_behind(levels.get(e.get("level_id")) or {}, e) is None for e in others):
        for e in others:
            e["main"] = False                         # a 'main' door with a lost room behind it is no way in
        ent["main"], ent["main_reason"] = True, "the inferred building entrance into the entrance hall (R43)"
    if isinstance(b.get("site"), dict):
        b["site"].setdefault("entrances", []).append(ent)
    rec["door"] = o["id"]
    # the flat whose rooms the hall took: its other rooms stay, listed
    rec["flat_rooms_left"] = sorted({nb for rid in hall_rooms for nb in adj.get(rid) or ()
                                    if nb not in core and nb not in hall_rooms and rooms[nb].get("room_type") in
                                    ("bedroom", "kitchen", "living", "dining", "bathroom", "wc", "hall")})
    # 20 Nov 2026 (pre-pod review R20-06: the hall took the left flat's kitchen and its kitchen door stayed a second
    # door from the flat's Antre into the common lobby): a door or opening between the hall and a flat's room is closed
    # when that room still reaches the core another way (removed into openings_merged, the wall kept); kept and named
    # the flat's entrance when it is its only way in; the rooms the flat lost are named by their drawn type
    rec["flat_rooms_lost"] = [{"room": rid, "drawn_type": (rooms[rid].get("adjusted_by_ai") or {}).get(
        "changed", {}).get("room_type"), "drawn_label": (rooms[rid].get("adjusted_by_ai") or {}).get(
        "changed", {}).get("label")} for rid in hall_rooms]
    level = CP.Level(b, lid)
    hall = set(hall_rooms)
    closed, why = [], {}
    for x, y, op in CR._links(level):
        if op.get("virtual") or op.get("inferred") or op["id"] == o["id"] or not ((x in hall) ^ (y in hall)):
            continue
        flat = y if x in hall else x
        if flat in core or flat in hall:
            continue
        reach = CR._reaches(level, set(core), flat, skip={op["id"]} | {d["id"] for d in closed})
        text = (f"{op['id']} joins the inferred entrance hall to {flat} '{rooms[flat].get('label')}'"
                + (", which reaches the core another way: closed (the wall kept; the drawn opening values kept in "
                   "openings_merged)" if reach else ", its flat's only way in: kept as the flat's entrance"))
        if reach and not RG.blocked("entrance_hall", b, {"level_id": lid, "opening": op["id"], "why": text}):
            closed.append(op)
            why[op["id"]] = why_ = text
            rec.setdefault("closed", []).append({"opening": op["id"], "room": flat, "reason": why_ + " (adjusted_by_ai)"})
        elif not reach:
            op["flat_entrance"] = {"by": "code", "rule": "entrance_hall", "reason": text}
            rec.setdefault("flat_entrances", []).append({"opening": op["id"], "room": flat, "reason": text})
    if closed:
        ids = {d["id"] for d in closed}
        CR._to_merged(b, closed, "entrance_hall", why)
        b["openings"] = [d for d in b.get("openings") or [] if d["id"] not in ids]
    lost = [f"{x['drawn_label'] or x['room']} ({x['drawn_type'] or 'room'})" for x in rec["flat_rooms_lost"]]
    if lost:
        b.setdefault("needs_review", []).append({
            "id": f"entrance_hall:{lid}", "kind": "entrance_hall_rooms", "crop": None, "room_id": hall_rooms[0],
            "level_id": lid, "reason": f"the inferred entrance hall on {lid} takes the flat's {', '.join(lost)}: to "
                                       f"review (the flat keeps {', '.join(rec['flat_rooms_left']) or 'no other room'})"})
    return rec


# -------------------------------------------------------------------------------------------------------- apply
def apply(build, ground: dict, rec: dict, texts: Optional[list], drawn, side: Optional[list]) -> dict:
    """The module docstring; the record (``footprint``, ``cut``, ``entrance_hall``, ``questions``)."""
    b = build.building
    lid = ground["id"]
    cant = rec.get("cantilevers") or {}
    out: dict = {"footprint": None, "cut": None, "entrance_hall": None, "questions": []}
    foot = footprint(b, lid, drawn, float(cant.get("ground_m2") or 0.0)) if cant else None
    if foot is not None and not RG.blocked("ground_cut", b, {"level_id": lid, "why": "footprint",
                                                             "entities": foot["entities"][:6]}):
        why = (f"the ground floor is not drawn: read from the typical plan and cut to the drawn footprint "
               f"({foot['layer']}, {foot['area_m2']:.0f} m2 against {cant.get('ground_m2'):.0f} m2 of the area table, "
               f"{', '.join(foot['entities'][:6])})")
        out["footprint"] = {"area_m2": foot["area_m2"], "entities": foot["entities"], "layer": foot["layer"],
                            "linetype": foot["linetype"],
                            "polygon": [[round(x, 3), round(y, 3)] for x, y in list(foot["polygon"].exterior.coords)[:-1]]}
        out["cut"] = cut(build, b, lid, foot, why)
        c = out["cut"]
        build.warn(f"{lid}: {why}: {len(c['rooms_cut'])} room(s) cut, {len(c['rooms_dropped'])} left out, "
                   f"{len(c['walls_removed'])} wall(s) gone, {len(c['walls_added'])} new facade wall(s) (inferred)")
        out["questions"].append({
            "element": "ground_floor", "keep": "keep the inferred ground floor",
            "found": why + f"; {len(c['rooms_cut'])} room(s) cut, {len(c['rooms_dropped'])} left out, balconies left off "
                           f"({', '.join(c['spaces_left_off']) or 'none'}); its interior is the typical floor's "
                           f"(inferred)",
            "ask": "The ground floor is not drawn. Is it the typical floor cut to the footprint? A drawn ground floor "
                   "plan replaces the inference"})
        b.setdefault("needs_review", []).append({"id": f"ground_floor:{lid}", "kind": "ground_floor_inferred",
                                                 "reason": why, "crop": None, "room_id": None, "level_id": lid})
    why = "the ground floor is not drawn (read from the typical plan)"
    hall = entrance_hall(build, b, lid, side or [], foot, why)
    out["entrance_hall"] = hall
    if hall["rooms"] or hall["open"]:
        found = (f"the entrance hall from the street ({hall['street']}) into the core: {', '.join(hall['rooms'])} "
                 f"(door {hall['door']}); the flat's rooms left beside it: {', '.join(hall['flat_rooms_left']) or 'none'}"
                 if hall["rooms"] else hall["open"])
        out["questions"].append({
            "element": "entrance_hall", "keep": "keep the inferred entrance hall" if hall["rooms"] else "keep (none)",
            "found": found,
            "ask": "How does one enter the building from the street? A corridor to the core, an entrance hall in place "
                   "of the front flat, or shops on the street with a passage: all are plausible; the drawn ground "
                   "floor decides"})
        b.setdefault("needs_review", []).append({"id": f"entrance_hall:{lid}", "kind": "entrance_hall_inferred",
                                                 "reason": found, "crop": None, "room_id": None, "level_id": lid})
        if hall["rooms"]:
            build.warn(f"{lid}: entrance hall (inferred, R43): {found}")
    return out
