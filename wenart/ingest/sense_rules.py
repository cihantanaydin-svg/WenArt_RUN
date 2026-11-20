"""A building that makes sense, second series (12 Nov 2026; the architect's audit of 8 buildings, user: "Make sense of
the building", "This is for all the projects").

What: ``apply(build, texts_by_level)`` runs in ``completion.complete`` after the core rules and the windows; it changes
the building in place and returns the record written to ``level_inference.sense_rules``:

1. **Exterior flags from the outline** (``exterior``; the staged rule ``exterior_spans`` replaces it when switched
   on): a wall is exterior where a room lies on one side and the open air (beyond the level's filled outline, a
   balcony out there, or a light well: one definition with the windows, the amended R14) on the other, interior where
   rooms lie on both sides. An open-air room inside the outline (a terrace, a loggia) is unknown, never a room: a drawn
   flag stays (review MF8). The flag changes only when one of the two holds along at least ``CLEAR_SHARE`` of all the
   wall's stations (stations with no room on either side count too); else the drawn flag stays. Each change keeps
   ``drawn_exterior`` (``adjusted_by_ai`` by code).
2. **A stair rises only into a storey over it** (``stairs``): a stair whose storey above exists and covers less than
   ``STAIR_COVER`` of its footprint (outside the storey's outline: an open roof), or whose storey above is an open roof
   terrace that draws no stair or stair head over it (S1-10c), is the arriving flight drawn on its storey: it is not
   built upward (``build: false``) and its void in the slab above is removed. It stays (a review record, nothing
   changed) when the storey above draws a stair of about its size near it (also misregistered, within
   ``STAIR_NEAR_M``), a riser tag on it climbs the full storey, the storey above is read too thinly to tell, or it
   arrives on a terrace drawn over it (review MF1, REG-07). The variants follow their base level. The top storey's
   stairs are the builder's (``shell.plan_stairs``: an arrival or capped under the roof).
3. **Shafts are voids** (``shafts``): a face named or holding a shaft word (``SHAFT_RE``: ŞAFT, Ş., TESİSAT, BACA,
   HAVALANDIRMA, duct, riser) that no door reaches and at most ``SHAFT_MAX_M2`` is a shaft (room type ``shaft``, never
   furnished), with its void in the slab of every storey above where the storey below has the shaft too.
4. **Balconies have a door** (``balconies``): a balcony (outdoor space) deeper than ``SERVICE_DEPTH_M`` that no door
   touches (any door within its wall's half thickness and ``DOOR_TOUCH_M`` of it, from any room or none, or an
   entrance onto it) gets one: an opening between it and a habitable room (its probe in this balcony, on any face)
   becomes its door only when a door's swing is drawn at it (an arc of about its width at one of its jambs, sweeping
   at least ``SWING_SWEEP_DEG``: the coordinator's decision of 12 Nov 2026) and it carries no drawn window evidence (a
   W/H tag under 1.8 m high, a window layer or block); a doorless gap there becomes its door; else nothing is changed
   and a review record is written (never a door through a solid drawn wall, never a tagged window retyped: review
   POD-01, REG-06, CS1-03, MF2). A level read with low confidence is left as it is. A shallower balcony is a service
   balcony (an AC ledge reached through its window): its window stays (audit real03-14).

Why: the audit's real21-4 and real20-9 (interior walls flagged exterior, where inferred windows would go), real10-5 (a
stair copied onto the top normal floor rising onto the open roof), real20-11, real03-4 and real06-10 (shafts read as
rooms or lost), real20-10 (balconies with no door). Each is a general rule.

How: pure geometry on the building dict (``completion.Level`` probes); no AI. Every change passes
``rule_guards.blocked`` first (rule keys ``exterior_flag``, ``stair_over_nothing``, ``shaft``, ``balcony_door``): a
guard or a rule switched off stops it, logged in ``level_inference.guarded``.
"""
from __future__ import annotations

import re
from typing import Optional

from shapely.geometry import Point

from wenart import building as B
from wenart import geometry as G
from wenart.ingest import completion as CP
from wenart.ingest import rule_guards as RG

STAIR_COVER = 0.3
STAIR_SIZE_TOL_M = 0.2          # a stair the storey above draws is the same one when each side is this close ...
STAIR_NEAR_M = 4.0              # ... and it lies this near (a misregistered storey: about 3 m off; REG-07)
STAIR_REG_M = 1.0               # ... farther than this: the storeys do not register (a finding)
RISE_TOL_M = 0.10               # a riser tag climbing the storey height within this keeps the stair
STATION_M = 0.25
CLEAR_SHARE = 0.75              # the share of a wall's stations one side must hold before its flag changes
DOOR_TOUCH_M = 0.30             # a door this far beyond its wall's half thickness from a balcony opens onto it
SWING_SWEEP_DEG = 75.0          # a door's swing sweeps at least this (a quarter); a tick or a sill arc less
TAG_RE = re.compile(r"^\s*[a-z]?\s*(\d{2,3})\s*/\s*(\d{2,3})\s*$")
WINDOW_LAYER_RE = re.compile(r"pencere|penc|window|glass|glazing|(?<![a-z])cam(?![a-z])|fenster|fenetre|ventana")
TERRACE_RE = re.compile(r"(?<![a-z])(?:teras|terasi|terrace|dachterrasse|roof\s+terrace)(?![a-z])")
SHAFT_RE = re.compile(r"(?<![a-z])(?:saft|s\.|tesisat|baca|havalandirma|hava\s+bacasi|duct|riser|vent\s+shaft)"
                      r"(?![a-z])")
SHAFT_MAX_M2 = 3.0
SWING_RADIUS = (0.3, 1.3)       # a door's swing: an arc whose radius is this share of the opening's width ...
SWING_REACH_M = 0.30            # ... with its centre or one of its ends this close to one of its jambs
SERVICE_DEPTH_M = 1.0           # a balcony this shallow or less is a service balcony (an AC ledge): its window stays
HABITABLE = ("bedroom", "living", "kitchen", "office", "study", "dining")


def _fold(t) -> str:
    return CP._fold(t)


# --------------------------------------------------------------------------------------------- 1. exterior flags
def exterior_flags(b: dict) -> list:
    """Rule 1 (the module docstring); returns the changes ``[{wall, level_id, exterior, reason}]``."""
    from shapely.prepared import prep

    from wenart.ingest import ground_floor as GF

    out = []
    for lv in b.get("levels") or []:
        level = CP.Level(b, lv["id"])
        if level.outline is None:
            continue
        bands = {wid: GF._band(ww) for wid, ww in level.walls.items() if CP._axis(ww)[2] >= 0.05}
        for w in level.walls.values():
            a, u, length = CP._axis(w)
            if length < 0.3:
                continue
            n = (-u[1], u[0])
            reach = float(w.get("thickness") or 0.15) / 2.0 + CP.PROBE_M
            ext = inner = other = 0
            steps = max(1, int(length / STATION_M))
            # (20 Nov 2026, pre-pod review R03-07: short wall stubs at the corridor ends kept walls between rooms below
            # the share) a station whose probe falls inside another wall's solid is not counted
            solid = [prep(p) for wid, p in bands.items() if wid != w["id"] and p.distance(
                Point((a[0] + u[0] * length / 2.0, a[1] + u[1] * length / 2.0))) <= length / 2.0 + reach + 0.5]
            for k in range(steps + 1):
                t = length * (k + 0.5) / (steps + 1)
                c = (a[0] + u[0] * t, a[1] + u[1] * t)
                qs = [(c[0] + s * n[0] * reach, c[1] + s * n[1] * reach) for s in (1, -1)]
                if any(s.contains(Point(q)) for s in solid for q in qs):
                    continue
                kinds = [level.kind_at(q, "") for q in qs]
                # an open-air room inside the outline (a terrace, a loggia) is unknown: never a room (MF8)
                kinds = ["unknown" if x == "balcony" and level._inside is not None and level._inside.contains(Point(q))
                         else x for x, q in zip(kinds, qs)]
                inside = [x == "room" for x in kinds]
                # a light well is open air, as for the windows (the amended R14; POD-07)
                outside = [x in ("outside", "balcony", "light_well") for x in kinds]
                if any(inside) and any(outside):
                    ext += 1
                elif all(inside):
                    inner += 1
                else:
                    other += 1
            total = ext + inner + other
            if ext + inner < 3:
                continue
            if ext >= CLEAR_SHARE * total:
                flag = True
            elif inner >= CLEAR_SHARE * total:
                flag = False
            else:
                continue                                    # partly on the outline or unknown: the drawn flag stays
            if bool(w.get("exterior")) == flag or RG.blocked(
                    "exterior_flag", b, {"level_id": lv["id"], "wall": w["id"], "exterior": flag,
                                         "stations": [ext, inner, other]}):
                continue
            reason = (f"{w['id']}: {'the open air' if flag else 'rooms'} on {'one side' if flag else 'both sides'} along "
                      f"{max(ext, inner)} of {total} stations: {'exterior' if flag else 'interior'} by the building "
                      f"outline (drawn flag {bool(w.get('exterior'))})")
            for ww in b.get("walls") or []:
                if ww["id"] == w["id"]:
                    ww["drawn_exterior"] = bool(ww.get("exterior"))
                    ww["exterior"] = flag
                    ww["adjusted_by_ai"] = {"by": "code", "rule": "exterior_from_outline", "reason": reason,
                                            "changed": {"exterior": ww["drawn_exterior"]}}
            out.append({"wall": w["id"], "level_id": lv["id"], "exterior": flag, "reason": reason})
    return out


# ------------------------------------------------------------------------------------------------------ 2. stairs
def _same_stair_above(b: dict, f: dict, above: str) -> Optional[tuple]:
    """``(stair, distance)``: a stair the storey above draws of about ``f``'s size (``STAIR_SIZE_TOL_M``) within
    ``STAIR_NEAR_M`` (pure)."""
    fp = f["footprint"]
    mine = sorted(float(v) for v in fp["size"])
    best = None
    for g in b.get("furniture") or []:
        gp = g.get("footprint") or {}
        if g.get("level_id") != above or g.get("type") != "stair" or not gp.get("size"):
            continue
        other = sorted(float(v) for v in gp["size"])
        d = G.distance(fp["center"][:2], gp["center"][:2])
        if all(abs(x - y) <= STAIR_SIZE_TOL_M for x, y in zip(mine, other)) and d <= STAIR_NEAR_M and \
                (best is None or d < best[1]):
            best = (g, d)
    return best


def _thin(b: dict, lv: dict) -> Optional[str]:
    """Why the storey ``lv`` is read too thinly to say what is over a stair (pure): most of its room labels lie in no
    room, or it has 3 rooms or fewer while its plan has 10 or more room labels; None otherwise."""
    rooms = sum(1 for r in b.get("rooms") or [] if r.get("level_id") == lv["id"])
    lost = sum(1 for p in lv.get("reading_places") or [] if p.get("kind") == "unplaced_label")
    if rooms == 0:
        return f"{lv['id']} has no room read"
    if lost > rooms:
        return f"{lv['id']} has {lost} room labels in no room against {rooms} rooms read"
    if rooms <= 3 and rooms + lost >= 10:
        return f"{lv['id']} has {rooms} rooms read for {rooms + lost} room labels"
    return None


def _terrace_over(b: dict, above: dict, poly, texts: list) -> Optional[str]:
    """A terrace drawn over the stair on the storey above (a terrace space or room, or a TERAS word over it), or None."""
    for s in (b.get("site") or {}).get("outdoor_spaces") or []:
        p = CP._poly(s.get("polygon"))
        if s.get("level_id") == above["id"] and p is not None and str(s.get("kind") or "") in CP.OPEN_AIR and \
                p.intersects(poly):
            return f"the {s.get('kind')} {s['id']}"
    for r in b.get("rooms") or []:
        p = CP._poly(r.get("polygon"))
        if r.get("level_id") == above["id"] and p is not None and str(r.get("room_type") or "") in CP.OPEN_AIR and \
                p.intersects(poly):
            return f"the {r.get('room_type')} {r['id']}"
    for t in texts or []:
        if TERRACE_RE.search(_fold(t.get("text"))) and poly.buffer(1.0).contains(Point(t["x"], t["y"])):
            return f"the word '{t['text']}'"
    return None


def stairs_over_nothing(b: dict, texts_by_level: Optional[dict] = None) -> list:
    """Rule 2 (the module docstring); returns the records ``[{stair, level_id, reason}]`` (``kept`` True for a stair
    left as it is with a review reason)."""
    from shapely.geometry import Polygon

    storeys = sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                     key=lambda lv: (lv.get("order") or 0, lv["id"]))
    ids = [lv["id"] for lv in storeys]
    by_id = {lv["id"]: lv for lv in storeys}
    out, stopped = [], []
    for f in b.get("furniture") or []:
        if f.get("type") != "stair" or f.get("build") is False or f.get("level_id") not in ids or \
                not (f.get("footprint") or {}).get("size"):
            continue
        k = ids.index(f["level_id"])
        if k + 1 >= len(ids):
            continue
        above = by_id[ids[k + 1]]
        if not any(r.get("level_id") == above["id"] for r in b.get("rooms") or []):
            continue
        outline = CP.Level(b, above["id"]).outline
        if outline is None:
            continue
        fp = f["footprint"]
        poly = Polygon(G.rotated_rectangle(fp["center"], fp["size"], fp["rotation_deg"]))
        if poly.area <= 0:
            continue
        cover = outline.intersection(poly).area / poly.area
        texts = (texts_by_level or {}).get(above["id"]) or []
        over_roof = cover < STAIR_COVER
        # S1-10c: an open roof terrace storey that draws no stair or stair head over it (a stair head: any enclosed
        # room of that storey over at least half of the stair, whatever its label: real10's 'Oda' over its core stair)
        heads = [r for r in b.get("rooms") or [] if r.get("level_id") == above["id"]
                 and str(r.get("room_type") or "") not in CP.OPEN_AIR
                 and (CP._poly(r.get("polygon")) or Polygon()).intersection(poly).area >= 0.5 * poly.area]
        open_top = bool(above.get("roof_terrace")) and k + 2 >= len(ids) and not heads
        if not over_roof and not open_top:
            continue
        # what keeps it (review MF1, REG-07): the same stair drawn above, a riser tag for the full storey, a storey read
        # too thinly, a terrace it arrives on
        keep = None
        same = _same_stair_above(b, f, above["id"])
        if same is not None:
            keep = (f"{above['id']} draws the stair {same[0]['id']} of its size {same[1]:.1f} m away"
                    + (" (the storeys do not register: a finding)" if same[1] > STAIR_REG_M else ""))
        rise = None
        if isinstance(above.get("elevation"), (int, float)) and isinstance(by_id[f["level_id"]].get("elevation"),
                                                                           (int, float)):
            rise = float(above["elevation"]) - float(by_id[f["level_id"]]["elevation"])
        if keep is None and rise and f.get("risers") and f.get("riser_m") and \
                abs(float(f["risers"]) * float(f["riser_m"]) - rise) <= RISE_TOL_M:
            keep = f"its riser tag climbs {float(f['risers']) * float(f['riser_m']):.2f} m, the storey height"
        if keep is None:
            keep = _thin(b, above)
        if keep is None and over_roof:
            ter = _terrace_over(b, above, poly, texts)
            keep = f"it arrives on {ter} drawn over it on {above['id']}" if ter else None
        if keep is not None:
            out.append({"stair": f["id"], "level_id": f["level_id"], "kept": True,
                        "reason": f"the stair {f['id']} of {f['level_id']} is "
                                  + (f"{cover * 100:.0f} % under {above['id']}" if over_roof else
                                     f"under the open roof terrace {above['id']}")
                                  + f", but {keep}: kept (to review)"})
            continue
        if RG.blocked("stair_over_nothing", b, {"level_id": f["level_id"], "stair": f["id"], "above": above["id"]}):
            continue
        what = (f"has no storey over it ({above['id']} covers {cover * 100:.0f} % of it)" if over_roof else
                f"rises into the open roof terrace {above['id']}, which draws no stair or stair head over it")
        reason = (f"the stair {f['id']} of {f['level_id']} {what}: the arriving flight drawn on {f['level_id']}, not "
                  f"built upward; its void in the slab above is removed")
        stopped.append((f, reason))
    for f, reason in stopped:
        _stop(b, f, reason)
        out.append({"stair": f["id"], "level_id": f["level_id"], "reason": reason})
        # the variants of its level follow it (a variant's copy of the same stair)
        for g in b.get("furniture") or []:
            lv = next((x for x in b.get("levels") or [] if x["id"] == g.get("level_id")), {})
            gp = g.get("footprint") or {}
            if g is not f and g.get("type") == "stair" and lv.get("base_level_id") == f["level_id"] and \
                    gp.get("center") and g.get("build") is not False and \
                    G.distance(gp["center"][:2], f["footprint"]["center"][:2]) <= 0.5:
                _stop(b, g, reason + f" (the variant {lv['id']} follows {f['level_id']})")
                out.append({"stair": g["id"], "level_id": g["level_id"], "reason": reason + " (variant)"})
    return out


def _stop(b: dict, f: dict, reason: str) -> None:
    f["build"] = False
    f["adjusted_by_ai"] = {"by": "code", "rule": "stair_over_nothing", "reason": reason}
    for s in b.get("slabs") or []:
        if s.get("below_level_id") == f["level_id"]:
            s["openings"] = [o for o in s.get("openings") or [] if o.get("furniture_id") != f["id"]]



# ------------------------------------------------------------------------------------------------------ 3. shafts
def shaft_word(room: dict, texts: Optional[list]) -> Optional[str]:
    for key in ("label_raw", "label"):
        if SHAFT_RE.search(_fold(room.get(key)).lower()):
            return str(room.get(key))
    p = CP._poly(room.get("polygon"))
    if p is None or not texts:
        return None
    for t in texts:
        if SHAFT_RE.search(_fold(t["text"]).lower()) and p.buffer(0.05).contains(Point(t["x"], t["y"])):
            return str(t["text"]).strip()
    return None


def shafts(b: dict, texts_by_level: dict) -> list:
    """Rule 3 (the module docstring); returns the records ``[{room, level_id, reason}]``."""
    out, by_level = [], {}
    for lv in b.get("levels") or []:
        lid = lv["id"]
        doors = [o for o in b.get("openings") or [] if o.get("level_id") == lid and o.get("type") == "door"
                 and o.get("center")]
        for r in b.get("rooms") or []:
            if r.get("level_id") != lid or r.get("room_subtype") == "light_well" or CP.is_lift(r):
                continue
            p = CP._poly(r.get("polygon"))
            if p is None or p.area > SHAFT_MAX_M2:
                continue
            word = shaft_word(r, texts_by_level.get(lid))
            if word is None or any(p.distance(Point(o["center"][:2])) <= 0.25 for o in doors):
                continue
            # every shaft, retyped or already one, passes the guard before it gets slab voids (review CS1-09)
            if RG.blocked("shaft", b, {"level_id": lid, "room": r["id"], "why": word}):
                continue
            by_level.setdefault(lid, []).append(r)
            if r.get("room_type") == "shaft":
                continue
            reason = (f"'{word}' names a shaft (a duct or riser through the storeys, never a room); read as "
                      f"'{r.get('label')}' ({r.get('room_type')})")
            r["adjusted_by_ai"] = {"by": "code", "rule": "shaft_word", "reason": reason,
                                   "changed": {"room_type": r.get("room_type"), "label": r.get("label")}}
            r["room_type"] = "shaft"
            out.append({"room": r["id"], "level_id": lid, "reason": reason})
    for s in b.get("slabs") or []:
        above, below = s.get("above_level_id"), s.get("below_level_id")
        if not above or not below or above not in by_level or below not in by_level:
            continue
        under = [CP._poly(r["polygon"]) for r in by_level[below]]
        for r in by_level[above]:
            p = CP._poly(r["polygon"])
            if p is None or not any(q is not None and q.intersection(p).area >= 0.5 * p.area for q in under):
                continue
            if any(o.get("room_id") == r["id"] for o in s.get("openings") or []):
                continue
            s.setdefault("openings", []).append(
                {"id": f"so_{above}_sh_{len(s['openings']) + 1:02d}", "kind": "void", "room_id": r["id"],
                 "furniture_id": None, "polygon": [[round(float(x), 4), round(float(y), 4)] for x, y in r["polygon"]],
                 "source": "derived", "reason": f"the shaft {r['id']} runs through {below} and {above} (inferred)",
                 "entity": None})
    return out


# --------------------------------------------------------------------------------------------------- 4. balconies
def swing_at(o: dict, wall: dict, drawn) -> Optional[dict]:
    """The door swing drawn at an opening (pure but for the drawing's query): an arc whose radius is ``SWING_RADIUS``
    of the opening's width (a leaf, or one of a pair of leaves), with its centre or one of its ends within
    ``SWING_REACH_M`` of one of its jambs (real09 draws the swing from its jamb), sweeping at least
    ``SWING_SWEEP_DEG`` (a quarter: a tick or a sill arc is far less); None without one or without the drawing."""
    if drawn is None or not o.get("center"):
        return None
    import math

    from shapely.geometry import Point as P
    a, u, _ = CP._axis(wall)
    width = float(o.get("width") or 0.0)
    c = o["center"][:2]
    jambs = [(c[0] + u[0] * k * width / 2.0, c[1] + u[1] * k * width / 2.0) for k in (-1, 1)]
    for arc in drawn.arcs(P(c).buffer(width / 2.0 + SWING_REACH_M + 0.05)):
        if not SWING_RADIUS[0] * width <= arc["radius"] <= SWING_RADIUS[1] * width:
            continue
        ends = list(arc.get("ends") or [])
        if len(ends) == 2:
            v1 = (ends[0][0] - arc["center"][0], ends[0][1] - arc["center"][1])
            v2 = (ends[1][0] - arc["center"][0], ends[1][1] - arc["center"][1])
            n1, n2 = math.hypot(*v1), math.hypot(*v2)
            if n1 > 1e-9 and n2 > 1e-9:
                sweep = math.degrees(math.acos(max(-1.0, min(1.0, (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2)))))
                if sweep < SWING_SWEEP_DEG:
                    continue
        if min(G.distance(q, j) for q in [arc["center"]] + ends for j in jambs) <= SWING_REACH_M:
            return arc
    return None


def window_evidence(o: dict, texts: list) -> Optional[str]:
    """The drawn evidence that an opening is a window (pure): a W/H size tag with a height under 1.8 m at it, an entity
    on a window layer, or a window block; None without one (review POD-01, MF2)."""
    for e in o.get("evidence") or []:
        layer = B.fold_ascii(str(e.get("layer") or "")).lower()
        block = B.fold_ascii(str(e.get("block") or e.get("block_name") or "")).lower()
        if WINDOW_LAYER_RE.search(layer):
            return f"its entity on the window layer '{e.get('layer')}'"
        if WINDOW_LAYER_RE.search(block):
            return f"the window block '{e.get('block') or e.get('block_name')}'"
        m = TAG_RE.match(B.fold_ascii(str(e.get("text") or "")).lower())
        if m and int(m.group(2)) < 180:
            return f"its size tag '{e.get('text')}'"
    c = o.get("center")
    if c:
        reach = float(o.get("width") or 0.0) / 2.0 + 0.6
        for t in texts or []:
            m = TAG_RE.match(B.fold_ascii(str(t.get("text") or "")).lower())
            if m and int(m.group(2)) < 180 and G.distance((t["x"], t["y"]), c[:2]) <= reach:
                return f"the size tag '{t['text']}' at it"
    return None



def balcony_doors(b: dict, next_id, drawn_by_level: Optional[dict] = None,
                  texts_by_level: Optional[dict] = None) -> list:
    """Rule 4 (the module docstring); returns the records ``[{space, opening, how, reason}]``."""
    from wenart.ingest import core_rules as CR

    out = []
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    spaces = [s for s in (b.get("site") or {}).get("outdoor_spaces") or [] if str(s.get("kind")) == "balcony"]
    onto = {e.get("onto") for e in (b.get("site") or {}).get("entrances") or [] if e.get("onto")}
    for s in spaces:
        lid = s.get("level_id")
        p = CP._poly(s.get("polygon"))
        if p is None or not lid or s["id"] in onto:
            continue
        level = CP.Level(b, lid)
        inside = p.buffer(1e-6)
        # a door on the balcony's edge, whatever room is behind it (one the reading lost, a WC, a hall, none)
        touching = []
        for o in level.openings:
            w = level.walls.get(o.get("wall_id"))
            if o.get("type") == "door" and o.get("center") and not o.get("virtual") and \
                    p.distance(Point(o["center"][:2])) <= (float(w.get("thickness") or 0.15) / 2.0 if w else 0.1) \
                    + DOOR_TOUCH_M:
                touching.append(o)
        if touching:
            continue
        if RG.switched_off("balcony_door", b):
            RG.blocked("balcony_door", b, {"level_id": lid, "space": s["id"]})
            continue
        # the openings between this balcony and a habitable room, on any face
        cands = []
        for o in level.openings:
            if o.get("virtual") or o.get("type") not in ("window", "opening") or o.get("wall_id") not in level.walls:
                continue
            sides = CR._sides(level, o)
            ins = [k for k, x in enumerate(sides) if inside.contains(Point(x[2]))]
            if len(ins) != 1:
                continue
            room = sides[1 - ins[0]][1]
            if room is not None and room.get("room_type") in HABITABLE:
                cands.append((o, room))
        mrr = p.minimum_rotated_rectangle
        edges = sorted({round(G.distance(a, c), 3) for a, c in zip(list(mrr.exterior.coords)[:-1],
                                                                    list(mrr.exterior.coords)[1:])})
        depth = edges[0] if edges else 0.0
        if depth <= SERVICE_DEPTH_M:
            # a service balcony (an AC ledge) reached through its window keeps the window: no door (audit real03-14)
            out.append({"space": s["id"], "opening": None, "how": "service balcony",
                        "reason": f"the balcony {s['id']} is {depth:.2f} m deep: a service balcony, its window stays "
                                  f"(a guard on upper floors, no door)"})
            continue
        lv = levels.get(lid) or {}
        base = levels.get(lv.get("typical_of")) if lv.get("typical_of") else None
        if (base or lv).get("reading_confidence") == "low":
            out.append({"space": s["id"], "opening": None, "how": "review",
                        "reason": f"the balcony {s['id']} has no door, but {lid} is read with low confidence: nothing "
                                  f"is changed (review)"})
            continue
        drawn = (drawn_by_level or {}).get(lid)
        texts = (texts_by_level or {}).get(lid) or []
        choice, notes = None, []
        for o, room in sorted(cands, key=lambda c: -float(c[0].get("width") or 0)):
            ev = window_evidence(o, texts) if o.get("type") == "window" else None
            if ev:
                notes.append(f"{o['id']} is a window ({ev})")
                continue
            if o.get("type") == "opening":
                choice = (o, room, None)
                break
            swing = swing_at(o, level.walls[o["wall_id"]], drawn)
            if swing is not None:
                choice = (o, room, swing)
                break
            notes.append(f"{o['id']} has no door's swing drawn")
        if choice is None:
            out.append({"space": s["id"], "opening": None, "how": "review",
                        "reason": f"the balcony {s['id']} has no door: "
                                  + ("; ".join(notes) if notes else "no opening joins it to a room")
                                  + ": nothing is changed, a door is never cut through a drawn wall nor a drawn "
                                    "window made a door (review)"})
            continue
        o, room, swing = choice
        if RG.blocked("balcony_door", b, {"level_id": lid, "space": s["id"], "opening": o["id"]}):
            continue
        what = (f"has a door's swing drawn at its jamb ({swing['id']}, {swing['radius']:.2f} m)" if swing else
                "is a doorless gap")
        reason = (f"the balcony {s['id']} has no door: the {o.get('type')} {o['id']} of {room['id']} "
                  f"'{room.get('label')}' onto it {what}: it is the balcony door (adjusted_by_ai)")
        o.update(drawn_type=o.get("type"), type="door", sill_height=None, height=max(float(o.get("height") or 0), 2.1),
                 operation="double" if float(o.get("width") or 0) >= 1.2 else "swing", operation_source="assumed",
                 adjusted_by_ai={"by": "code", "rule": "balcony_door", "reason": reason})
        out.append({"space": s["id"], "opening": o["id"], "how": f"{o['drawn_type']} to door", "reason": reason})
    return out



def apply(build, texts_by_level: dict, drawn_by_level: Optional[dict] = None) -> dict:
    """The four rules (the module docstring); the record for ``level_inference.sense_rules``."""
    b = build.building
    rec = {"shafts": shafts(b, texts_by_level), "stairs": stairs_over_nothing(b, texts_by_level),
           "balconies": balcony_doors(b, build.ids.next, drawn_by_level, texts_by_level),
           # the staged per-stretch rule (exterior.apply, before the windows) replaces this one when switched on
           "exterior": [] if RG.active("exterior_spans", b) else exterior_flags(b)}
    for k, word in (("shafts", "shaft"), ("stairs", "stair"), ("balconies", "balcony")):
        for x in rec[k]:
            build.warn(f"{word}: {x['reason']}")
    if rec["exterior"]:
        build.warn(f"exterior flags: {len(rec['exterior'])} wall(s) set from the building outline "
                   f"({sum(1 for x in rec['exterior'] if not x['exterior'])} interior, "
                   f"{sum(1 for x in rec['exterior'] if x['exterior'])} exterior)")
    return rec


