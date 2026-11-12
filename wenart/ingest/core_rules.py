"""The common core of a building, completed (12 Nov 2026; the architect's audit of 8 buildings, user: "Make sense of
the building", "This is for all the projects").

What: ``apply(build, texts_by_level, party_by_level)`` runs in ``completion.complete`` after the storeys and the light
wells and before the windows; it changes the building in place and returns the record written to
``level_inference.core_rules``. Every change carries ``inferred`` or ``adjusted_by_ai`` (by code) with its reason.

1. **A stair the reading missed** (``stairs``): a building with a lift, several flats on a storey (two kitchens) or
   several storeys has a stair rising from every storey with a storey above. When a storey has none, a stroke box the
   reading set aside as notation (``symbols`` of kind ``dimension_outline`` or ``unknown``, at least ``STAIR_BOX_M``)
   standing in a hall or a stair room, or touching a lift, is that stair (``from_documents``, typed by this rule);
   else, in a building with a lift or several flats, a dog-leg stair is inferred in the core hall when it has room for
   one (``added_by_ai``). Each stair gets its void in the slab above.
2. **Lift landing doors** (``lift_doors``): a lift's openings onto a flat's room, onto a stair flight or narrower than
   ``LIFT_DOOR_MIN_M`` are removed; a lift left without an opening onto the common hall gets one inferred landing door
   on the face to the hall.
3. **Between a flat and the core** (``core_gaps``): an unclassified gap (type ``opening``) between a flat's room and
   the common core (the lifts, the stairs and the halls joined to them by doorless openings) is closed: the only way
   from a flat into the core is its entrance door.
4. **Entrances** (``entrances``): an entrance (``site.entrances``) whose far side holds a room label the reading lost
   is no entrance (the room behind it is missing); in a building of several flats an entrance from a flat's room or
   hall is refused (the building's entrance leads into the common hall); a building of several flats without an
   entrance into the core gets an inferred one where the core hall reaches a facade that is no party wall, else an open
   point (the passage from the street to the core is not drawn).

Why: real21's core held two lifts and a stair box the reader set aside as a dimension outline; its lifts opened into
bedrooms, a bedroom opened onto the stair hall, and no door led in from the street. real20's six "entrances" were inner
doors of rooms the reading lost; real10's lift opened into a WC and onto its stair. Every one is a general rule.

How: pure geometry on the building dict (``completion.Level`` probes, shapely); no AI.
"""
from __future__ import annotations

import math
from typing import Optional

from shapely.geometry import Point, Polygon

from wenart import geometry as G
from wenart.ingest import completion as CP

PRIVATE = ("bedroom", "living", "kitchen", "bathroom", "wc", "shower", "toilet", "storage", "dining", "office",
           "study", "laundry")
WET = ("bathroom", "wc", "shower", "toilet")
STAIR_BOX_M = (1.0, 2.5)        # a stroke box at least this small side by this long side can hold a stair
STAIR_SYMBOL_KINDS = ("dimension_outline", "unknown", "untyped", "outline")
LIFT_DOOR_MIN_M = 0.60
LIFT_DOOR_M = (0.90, 2.10)      # an inferred lift landing door
ENTRANCE_DOOR_M = (1.20, 2.20)
DOGLEG_M = (2.30, 4.20)         # an inferred dog-leg stair's footprint (two 1.1 m flights and a 1.2 m landing)
TREAD_M = 0.27
LABEL_REACH_M = 1.5             # a lost room label this close beyond an entrance is the room behind it


def _storey_below(b: dict, lid: str) -> Optional[str]:
    st = _storeys(b)
    ids = [lv["id"] for lv in st]
    return ids[ids.index(lid) - 1] if lid in ids and ids.index(lid) > 0 else None


def _rect(fp: dict) -> Polygon:
    return Polygon(G.rotated_rectangle(fp["center"], fp["size"], fp["rotation_deg"]))


def _storeys(b: dict) -> list:
    return sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                  key=lambda lv: (lv.get("order") or 0, lv["id"]))


def several_flats(b: dict) -> bool:
    """A building of several flats (pure): a lift, or two kitchens on one storey."""
    if any(CP.is_lift(r) for r in b.get("rooms") or []):
        return True
    for lv in _storeys(b):
        if sum(1 for r in b.get("rooms") or [] if r.get("level_id") == lv["id"] and r.get("room_type") == "kitchen") >= 2:
            return True
    return False


def needs_stair(b: dict) -> bool:
    """A building that needs a stair (pure): several flats (``several_flats``) or several storeys."""
    return several_flats(b) or len(_storeys(b)) >= 2


def stairs_on(b: dict, lid: str) -> list:
    return ([f for f in b.get("furniture") or [] if f.get("level_id") == lid and f.get("type") == "stair"]
            + [r for r in b.get("rooms") or [] if r.get("level_id") == lid and r.get("room_type") == "stair"])


# ------------------------------------------------------------------------------------------------------- 1. stairs
def stair_dict(fp: dict, reason: str) -> dict:
    """A dog-leg (U) stair in the footprint ``fp`` (pure): two flights side by side along its long side, a half
    landing at the far end; the direction and the turn assumed (the shape the stair rule writes)."""
    (cx, cy), (w, d), rot = fp["center"], fp["size"], math.radians(fp["rotation_deg"])
    # the long side along the footprint's own axis
    if d >= w:
        u, n, length, width = (-math.sin(rot), math.cos(rot)), (math.cos(rot), math.sin(rot)), d, w
    else:
        u, n, length, width = (math.cos(rot), math.sin(rot)), (-math.sin(rot), math.cos(rot)), w, d
    fw = width / 2.0
    ld = max(min(fw, 1.4), 1.0)
    lines = max(3, min(10, int((length - ld - 0.3) / TREAD_M)))
    fl = lines * TREAD_M

    def at(s, t):
        return [round(cx + u[0] * s + n[0] * t, 4), round(cy + u[1] * s + n[1] * t, 4)]

    s0 = -length / 2.0 + 0.3
    flights = [{"start": at(s0, -fw / 2.0), "end": at(s0 + fl, -fw / 2.0), "width": round(fw, 3), "lines": lines,
                "spacing": TREAD_M},
               {"start": at(length / 2.0 - ld, fw / 2.0), "end": at(length / 2.0 - ld - fl, fw / 2.0),
                "width": round(fw, 3), "lines": lines, "spacing": TREAD_M}]
    landing = [at(length / 2.0 - ld, -width / 2.0), at(length / 2.0, -width / 2.0), at(length / 2.0, width / 2.0),
               at(length / 2.0 - ld, width / 2.0)]
    return {"flights": flights, "landing": {"polygon": landing, "depth": round(ld, 3)},
            "direction": [round(u[0], 4), round(u[1], 4)], "direction_assumed": True, "turn": "U",
            "turn_assumed": True, "void_assumed": True, "riser_m": None, "riser_source": None, "reason": reason}


def _stair_box(b: dict, level: "CP.Level") -> Optional[dict]:
    """The stroke box of a storey that holds its stair (the module docstring), or None."""
    lifts = [level.polys[r["id"]] for r in level.rooms if CP.is_lift(r)]
    seen = set()
    for s in b.get("symbols") or []:
        fp = s.get("footprint") or {}
        if s.get("level_id") != level.lid or str(s.get("kind")) not in STAIR_SYMBOL_KINDS or not fp.get("size"):
            continue
        key = (round(fp["center"][0], 2), round(fp["center"][1], 2))
        if key in seen:
            continue
        seen.add(key)
        small, long_ = sorted(float(v) for v in fp["size"])
        if small < STAIR_BOX_M[0] or long_ < STAIR_BOX_M[1]:
            continue
        p = _rect(fp)
        room = level.room_at((p.centroid.x, p.centroid.y))
        in_core = room is not None and room.get("room_type") in ("hall", "stair")
        if in_core or any(p.distance(q) <= 0.4 for q in lifts):
            return {"symbol": s, "footprint": fp, "room": room}
    return None


def _core_hall(level: "CP.Level") -> Optional[dict]:
    """The hall that touches a lift (the largest), or None."""
    lifts = [level.polys[r["id"]] for r in level.rooms if CP.is_lift(r)]
    halls = [r for r in level.rooms if r.get("room_type") == "hall"
             and any(level.polys[r["id"]].distance(q) <= 0.4 for q in lifts)]
    return max(halls, key=lambda r: level.polys[r["id"]].area, default=None)


def _dogleg_in(level: "CP.Level", hall: dict) -> Optional[dict]:
    """A dog-leg footprint in the hall's minimum rotated rectangle when the hall holds one (pure), else None."""
    p = level.polys[hall["id"]]
    mrr = p.minimum_rotated_rectangle
    pts = list(mrr.exterior.coords)[:4]
    e1, e2 = math.dist(pts[0], pts[1]), math.dist(pts[1], pts[2])
    long_, short = max(e1, e2), min(e1, e2)
    if short < DOGLEG_M[0] or long_ < DOGLEG_M[1] + 1.2:
        return None
    a, bpt = (pts[0], pts[1]) if e1 >= e2 else (pts[1], pts[2])
    ang = math.degrees(math.atan2(bpt[1] - a[1], bpt[0] - a[0]))
    ux, uy = (bpt[0] - a[0]) / long_, (bpt[1] - a[1]) / long_
    vx, vy = -uy, ux
    along, across = (long_ - DOGLEG_M[1]) / 2.0, (short - DOGLEG_M[0]) / 2.0
    # at either end of the hall, against either side or in the middle: the first place the hall holds
    for s in (along, -along):
        for t in (-across, across, 0.0):
            c = (mrr.centroid.x + ux * s + vx * t, mrr.centroid.y + uy * s + vy * t)
            fp = {"center": [round(c[0], 4), round(c[1], 4)], "size": [DOGLEG_M[1], DOGLEG_M[0]],
                  "rotation_deg": round(ang, 3)}
            if p.buffer(0.02).contains(_rect(fp)):
                return fp
    return None


def infer_stairs(b: dict, next_id, texts_by_level: dict) -> list:
    """Rule 1 (the module docstring); returns the records ``[{level_id, stair, how, reason}]``."""
    out = []
    if not needs_stair(b):
        return out
    storeys = _storeys(b)
    flats = several_flats(b)
    for k, lv in enumerate(storeys[:-1]):
        lid = lv["id"]
        if stairs_on(b, lid) or not any(r.get("level_id") == lid for r in b.get("rooms") or []):
            continue
        level = CP.Level(b, lid, texts_by_level.get(lid))
        box = _stair_box(b, level)
        fp, how, room = None, None, None
        base = [f for f in b.get("furniture") or [] if lv.get("typical_of") and f.get("type") == "stair"
                and f.get("level_id") == lv["typical_of"]]
        if base and box is None:
            # a copy of a typical floor takes its floor's stair (drawn or inferred), at the same place
            fp = dict(base[0]["footprint"])
            room = level.room_at(tuple(fp["center"]))
            how = f"{lid} copies the typical floor {lv['typical_of']}: its stair {base[0]['id']} stands here too"
            box = {"symbol": {"id": base[0]["id"], "kind": "typical copy",
                              "evidence": base[0].get("evidence") or []}, "footprint": fp, "room": room}
        elif box is not None:
            fp, room = box["footprint"], box["room"]
            how = (f"the stroke box {box['symbol']['id']} ({fp['size'][0]:.2f} x {fp['size'][1]:.2f} m, set aside as "
                   f"'{box['symbol'].get('kind')}') in {room['id'] if room else 'the core'}: the building needs a stair "
                   f"and the reading has none on {lid}")
        elif flats:
            hall = _core_hall(level)
            fp = _dogleg_in(level, hall) if hall is not None else None
            room = hall
            if fp is not None:
                how = (f"no stair is drawn or read on {lid} of a building with several flats: a dog-leg stair is "
                       f"inferred in the core hall {hall['id']}")
        if fp is None:
            continue
        reason = how + " (inferred; needs review)"
        piece = {"id": next_id("furniture", lid), "level_id": lid, "room_id": (room or {}).get("id"), "type": "stair",
                 "type_raw": None,
                 "source": (base[0].get("source") or "added_by_ai") if box is not None and
                 box["symbol"].get("kind") == "typical copy" else "from_documents" if box is not None else "added_by_ai",
                 "footprint": {"center": list(fp["center"]), "size": list(fp["size"]),
                               "rotation_deg": fp["rotation_deg"]},
                 "front_deg": None, "height": None, "asset": None, "status": "unverified", "type_method": "inferred",
                 "type_candidates": [], "build": True, "inferred": True,
                 "adjusted_by_ai": {"by": "code", "rule": "stair_missing", "reason": reason},
                 "stair": stair_dict(fp, reason),
                 "evidence": (list((box or {}).get("symbol", {}).get("evidence") or [])[:1]
                              + [{"file": CP._ev_file(b, lid), "method": "inferred", "confidence": 0.4,
                                  "rule": "stair_missing", "text": reason}])}
        b.setdefault("furniture", []).append(piece)
        above = storeys[k + 1]["id"]
        for s in b.get("slabs") or []:
            if s.get("below_level_id") == lid and s.get("above_level_id") == above:
                s.setdefault("openings", []).append(
                    {"id": f"sv_{above}_st_{len(s['openings']) + 1:02d}", "kind": "stair_void", "furniture_id": piece["id"],
                     "polygon": [[round(x, 4), round(y, 4)] for x, y in G.rotated_rectangle(
                         fp["center"], fp["size"], fp["rotation_deg"])], "source": "derived"})
        out.append({"level_id": lid, "stair": piece["id"], "reason": reason,
                    "how": ("typical copy" if box is not None and box["symbol"].get("kind") == "typical copy" else
                            "stroke box" if box is not None else "dog-leg")})
    return out


# ------------------------------------------------------------------------------------- the core and the openings
def _sides(level: "CP.Level", o: dict) -> list:
    """The two things on either side of an opening: ``(kind, room or None)`` per side (``Level.kind_at``)."""
    w = level.walls.get(o.get("wall_id"))
    if w is None or not o.get("center"):
        return []
    a, u, _ = CP._axis(w)
    n = (-u[1], u[0])
    reach = float(w.get("thickness") or 0.15) / 2.0 + CP.PROBE_M
    c = o["center"]
    out = []
    for k in (1, -1):
        q = (c[0] + k * n[0] * reach, c[1] + k * n[1] * reach)
        out.append((level.kind_at(q, ""), level.room_at(q), q))
    return out


def core_rooms(b: dict, level: "CP.Level") -> set:
    """The common core of a storey (pure): its lifts, its stair rooms and the rooms holding a stair, and the halls joined
    to them by doorless openings or virtual separators (a landing in front of the lifts; never a flat's hall behind its
    door)."""
    core = {r["id"] for r in level.rooms if CP.is_lift(r) or r.get("room_type") == "stair"}
    below = _storey_below(b, level.lid)
    for f in b.get("furniture") or []:
        # the room holding a stair, and the room a stair of the storey below arrives in
        if f.get("level_id") in (level.lid, below) and f.get("type") == "stair" and f.get("footprint"):
            r = level.room_at(tuple(f["footprint"]["center"]))
            if r is not None and (f.get("level_id") == level.lid or r.get("room_type") == "hall"):
                core.add(r["id"])
    # a lift's lobby: the hall the lift touches along the longest stretch
    for lift in [r for r in level.rooms if CP.is_lift(r)]:
        lp = level.polys[lift["id"]].buffer(0.4)
        touch = [(lp.intersection(level.polys[r["id"]].exterior.buffer(0.05)).area, r) for r in level.rooms
                 if r.get("room_type") == "hall" and r["id"] != lift["id"]]
        touch = [t for t in touch if t[0] > 0.05]
        if touch:
            core.add(max(touch, key=lambda t: t[0])[1]["id"])
    rooms = {r["id"]: r for r in level.rooms}
    links = []
    for o in level.openings:
        if o.get("type") != "opening" and not o.get("virtual"):
            continue
        if o.get("virtual"):
            line = o.get("line") or []
            if len(line) != 2:
                continue
            mid = ((line[0][0] + line[1][0]) / 2.0, (line[0][1] + line[1][1]) / 2.0)
            near = [r["id"] for r in level.rooms if level.polys[r["id"]].distance(Point(mid)) <= 0.15]
        else:
            near = [s[1]["id"] for s in _sides(level, o) if s[1] is not None]
        if len(near) == 2:
            links.append(tuple(near))
    grew = True
    while grew:
        grew = False
        for a, c in links:
            for x, y in ((a, c), (c, a)):
                if x in core and y not in core and rooms.get(y, {}).get("room_type") == "hall":
                    core.add(y)
                    grew = True
    return core


def fix_lift_doors(b: dict, next_id) -> dict:
    """Rule 2 (the module docstring); returns ``{"removed": [...], "added": [...]}``."""
    rec = {"removed": [], "added": []}
    for lv in b.get("levels") or []:
        lid = lv["id"]
        level = CP.Level(b, lid)
        lifts = [r for r in level.rooms if CP.is_lift(r)]
        if not lifts or level.outline is None:
            continue
        core = core_rooms(b, level)
        stairs = [_rect(f["footprint"]) for f in b.get("furniture") or []
                  if f.get("level_id") == lid and f.get("type") == "stair" and f.get("footprint")]
        drop = set()
        for o in level.openings:
            if o.get("virtual") or o.get("type") not in ("door", "opening", "window"):
                continue
            sides = _sides(level, o)
            ids = [s[1]["id"] if s[1] is not None else None for s in sides]
            lift = next((r for r in lifts if r["id"] in ids), None)
            if lift is None and sides and float(o.get("width") or 0.0) < LIFT_DOOR_MIN_M:
                # a sliver of a 'door' in the shaft wall between two lifts or at a lift's corner is the lift's
                near = [r for r in lifts if level.polys[r["id"]].distance(Point(o["center"][:2])) <= 0.45]
                lift = near[0] if near else None
                if lift is not None:
                    ids = [lift["id"] if s[1] is None else s[1]["id"] for s in sides]
            if lift is None:
                continue
            k = ids.index(lift["id"])
            kind, other, q = sides[1 - k]
            why = None
            if float(o.get("width") or 0.0) < LIFT_DOOR_MIN_M:
                why = f"{o['id']} ({float(o.get('width') or 0):.2f} m) is narrower than a lift door ({LIFT_DOOR_MIN_M} m)"
            elif other is not None and other.get("room_type") in PRIVATE and other["id"] not in core:
                why = (f"{o['id']} opens the lift {lift['id']} into {other['id']} '{other.get('label')}' "
                       f"({other.get('room_type')}), a flat's room: a lift opens only onto the common hall")
            elif any(s.contains(Point(q)) for s in stairs):
                why = f"{o['id']} opens the lift {lift['id']} onto a stair flight: a lift opens onto the common hall"
            elif o.get("type") == "window":
                why = f"{o['id']} is a window in the lift shaft {lift['id']}"
            if why:
                drop.add(o["id"])
                rec["removed"].append({"opening": o["id"], "level_id": lid, "reason": why + " (adjusted_by_ai)"})
        if drop:
            b["openings"] = [o for o in b["openings"] if o["id"] not in drop]
            level = CP.Level(b, lid)
            core = core_rooms(b, level)
        for lift in lifts:
            served = False
            for o in level.openings:
                sides = _sides(level, o) if o.get("type") in ("door", "opening") else []
                ids = [s[1]["id"] if s[1] is not None else None for s in sides]
                if lift["id"] in ids:
                    other = sides[1 - ids.index(lift["id"])][1]
                    if other is not None and (other["id"] in core or other.get("room_type") == "hall"):
                        served = True
                        break
            if served:
                continue
            faces = [f for f in _hall_faces(level, lift, core)]
            if not faces:
                continue
            # the landing door faces away from the counterweight when the drawing shows one (a narrow piece in the
            # shaft beside the car), else the longest stretch onto the hall
            cw = _counterweight(b, level, lift)
            lc = level.polys[lift["id"]].centroid

            def score(x, cw=cw, lc=lc):
                f, p0, p1 = x
                mid = level.at(f["wall_id"], (p0 + p1) / 2.0)
                if cw is None:
                    return (False, p1 - p0)
                v1, v2 = (mid[0] - lc.x, mid[1] - lc.y), (cw[0] - lc.x, cw[1] - lc.y)
                n1, n2 = math.hypot(*v1), math.hypot(*v2)
                cos = (v1[0] * v2[0] + v1[1] * v2[1]) / (n1 * n2) if n1 > 1e-9 and n2 > 1e-9 else 0.0
                return (cos < -0.5, p1 - p0)            # clearly on the far side from the counterweight

            f, p0, p1 = max(faces, key=score)
            width = min(LIFT_DOOR_M[0], p1 - p0)
            if width < LIFT_DOOR_MIN_M:
                continue
            reason = (f"the lift {lift['id']} has no landing door onto the common hall: one inferred on {f['wall_id']} "
                      f"facing {f['hall']}")
            o = CP._new_opening("door", next_id("door", lid), level, f["wall_id"], (p0 + p1) / 2.0, width,
                                LIFT_DOOR_M[1], None, reason, lift, {"kind": "hall"}, CP._ev_file(b, lid),
                                lv.get("region_id"), "default lift door")
            o["operation"] = "sliding"
            o["inference"]["rule"] = "lift_door"
            b["openings"].append(o)
            level.openings.append(o)
            rec["added"].append({"opening": o["id"], "level_id": lid, "reason": reason + " (inferred)"})
    return rec


def _counterweight(b: dict, level: "CP.Level", lift: dict) -> Optional[tuple]:
    """The centre of a lift's counterweight (a piece in the shaft at most 0.5 m wide and under 0.6 m2), or None."""
    p = level.polys[lift["id"]]
    for f in b.get("furniture") or []:
        fp = f.get("footprint") or {}
        if f.get("level_id") != level.lid or not fp.get("size") or f.get("type") == "stair":
            continue
        w, d = sorted(float(v) for v in fp["size"])
        if w <= 0.5 and w * d < 0.6 and p.contains(Point(fp["center"][:2])):
            return tuple(fp["center"][:2])
    return None


def _hall_faces(level: "CP.Level", lift: dict, core: set) -> list:
    """``[(face, t0, t1)]``: the stretches of the lift's walls with a common hall on the other side, free of openings."""
    p = level.polys[lift["id"]]
    x0, y0, x1, y1 = p.bounds
    out = []
    for w in level.walls.values():
        xs, ys = (w["start"][0], w["end"][0]), (w["start"][1], w["end"][1])
        if max(xs) < x0 - 0.5 or min(xs) > x1 + 0.5 or max(ys) < y0 - 0.5 or min(ys) > y1 + 0.5:
            continue
        a, u, length = CP._axis(w)
        if length < LIFT_DOOR_MIN_M:
            continue
        n = (-u[1], u[0])
        reach = float(w.get("thickness") or 0.15) / 2.0 + CP.PROBE_M
        steps = max(1, int(length / CP.SAMPLE_M))
        cur = None
        for k in range(steps + 1):
            t = length * k / steps
            c = (a[0] + u[0] * t, a[1] + u[1] * t)
            sides = [level.room_at((c[0] + s * n[0] * reach, c[1] + s * n[1] * reach)) for s in (1, -1)]
            ids = [r["id"] if r else None for r in sides]
            hall = None
            if lift["id"] in ids:
                other = sides[1 - ids.index(lift["id"])]
                if other is not None and other["id"] != lift["id"] and (other["id"] in core and not CP.is_lift(other)):
                    hall = other["id"]
            if hall and cur is not None and cur["hall"] == hall:
                cur["t1"] = t
            elif hall:
                cur = {"wall_id": w["id"], "t0": t, "t1": t, "hall": hall, "kind": "hall"}
                out.append(cur)
            else:
                cur = None
    res = []
    for f in out:
        if f["t1"] - f["t0"] < LIFT_DOOR_MIN_M:
            continue
        for p0, p1 in level.free(f):
            res.append((f, p0, p1))
    return res


def close_core_gaps(b: dict) -> list:
    """Rule 3 (the module docstring); returns the records of the closed gaps."""
    out = []
    for lv in b.get("levels") or []:
        level = CP.Level(b, lv["id"])
        core = core_rooms(b, level)
        if not core:
            continue
        drop = []
        for o in level.openings:
            if o.get("type") != "opening" or o.get("virtual"):
                continue
            sides = _sides(level, o)
            rooms = [s[1] for s in sides if s[1] is not None]
            if len(rooms) != 2:
                continue
            a, c = rooms
            if (a["id"] in core) == (c["id"] in core):
                continue
            flat = c if a["id"] in core else a
            if flat.get("room_type") not in PRIVATE:
                continue
            drop.append(o["id"])
            out.append({"opening": o["id"], "level_id": lv["id"],
                        "reason": f"the unclassified gap {o['id']} ({float(o.get('width') or 0):.2f} m) joins "
                                  f"{flat['id']} '{flat.get('label')}' ({flat.get('room_type')}) to the common core: a "
                                  f"flat meets the core only through its entrance door (adjusted_by_ai: closed)"})
        if drop:
            b["openings"] = [o for o in b["openings"] if o["id"] not in drop]
    return out


# --------------------------------------------------------------------------------------------------- 4. entrances
def fix_entrances(b: dict, next_id, party_by_level: dict) -> dict:
    """Rule 4 (the module docstring); returns ``{"refused": [...], "added": [...], "open": ...}``."""
    rec = {"refused": [], "added": [], "open": None}
    site = b.get("site") or {}
    rooms = {r["id"]: r for r in b.get("rooms") or []}
    flats = several_flats(b)
    levels = {lv["id"]: lv for lv in b.get("levels") or []}
    keep = []
    for e in site.get("entrances") or []:
        why = None
        lv = levels.get(e.get("level_id")) or {}
        lost = [p for p in lv.get("reading_places") or [] if p.get("kind") == "unplaced_label" and p.get("at")]
        face, out_ = e.get("face") or e.get("centre"), e.get("outward") or [0.0, 0.0]
        if face and lost:
            q = (face[0] + out_[0] * 0.6, face[1] + out_[1] * 0.6)
            near = [p for p in lost if math.dist(q, p["at"][:2]) <= LABEL_REACH_M + 1.0]
            if near:
                why = (f"the far side of {e.get('door_id')} holds the room label '{near[0].get('text')}' the reading "
                       f"lost: a room behind it, not the outside")
        room = rooms.get(e.get("room_id")) or {}
        if why is None and flats and e.get("level_id"):
            level = CP.Level(b, e["level_id"])
            core = core_rooms(b, level)
            if room.get("room_type") in PRIVATE or (room.get("room_type") == "hall" and room.get("id") not in core
                                                   and core):
                why = (f"{e.get('door_id')} opens from {room.get('id')} '{room.get('label')}' ({room.get('room_type')}): "
                       f"a building of several flats is entered into its common hall")
        if why:
            rec["refused"].append({"door": e.get("door_id"), "level_id": e.get("level_id"),
                                   "reason": why + " (adjusted_by_ai: no entrance, no steps)"})
            for o in b.get("openings") or []:
                if o["id"] == e.get("door_id"):
                    o["entrance_refused"] = why
            continue
        keep.append(e)
    if rec["refused"]:
        site["entrances"] = keep
    if not flats:
        return rec
    storeys = _storeys(b)
    ground = next((lv for lv in storeys if (lv.get("order") or 0) == 0), None)
    if ground is None:
        return rec
    level = CP.Level(b, ground["id"])
    core = core_rooms(b, level)
    if any(e.get("level_id") == ground["id"] and (e.get("room_id") in core) for e in keep):
        return rec
    if any(o.get("inference", {}).get("rule") == "inferred_entrance" for o in b.get("openings") or []):
        return rec
    party = party_by_level.get(ground["id"]) or {}
    halls = [rooms[i] for i in core if rooms.get(i, {}).get("room_type") in ("hall", "stair")]
    best = None
    for hall in halls:
        for f in level.faces(hall):
            if f["kind"] != "outside" or f["wall_id"] in party:
                continue
            for p0, p1 in level.free(f):
                if p1 - p0 >= ENTRANCE_DOOR_M[0] and (best is None or p1 - p0 > best[3] - best[2]):
                    best = (hall, f, p0, p1)
    if best is not None:
        hall, f, p0, p1 = best
        reason = (f"the building entrance: the common hall {hall['id']} '{hall.get('label')}' reaches the facade on "
                  f"{f['wall_id']}; no entrance into the core is drawn or read")
        o = CP._new_opening("door", next_id("door", ground["id"]), level, f["wall_id"], (p0 + p1) / 2.0,
                            ENTRANCE_DOOR_M[0], ENTRANCE_DOOR_M[1], None, reason, hall, f, CP._ev_file(b, ground["id"]),
                            ground.get("region_id"), "default entrance door")
        o["inference"]["rule"] = "inferred_entrance"
        b["openings"].append(o)
        rec["added"].append({"door": o["id"], "level_id": ground["id"], "reason": reason + " (inferred)"})
    else:
        names = ", ".join(sorted(core)) or "no core read"
        rec["open"] = (f"the common core ({names}) reaches no facade of {ground['id']}: the passage from the street to "
                       f"the core is not drawn (open point: a corridor through the street-side flat is a design "
                       f"decision)")
    return rec


def apply(build, texts_by_level: dict, party_by_level: dict) -> dict:
    """The four rules in order (the module docstring); the record for ``level_inference.core_rules``."""
    b = build.building
    rec = {"stairs": infer_stairs(b, build.ids.next, texts_by_level)}
    rec["lift_doors"] = fix_lift_doors(b, build.ids.next)
    rec["core_gaps"] = close_core_gaps(b)
    rec["entrances"] = fix_entrances(b, build.ids.next, party_by_level)
    for s in rec["stairs"]:
        build.warn(f"stair: {s['reason']}")
    for x in rec["lift_doors"]["removed"] + rec["lift_doors"]["added"] + rec["core_gaps"]:
        build.warn(f"core: {x['reason']}")
    for x in rec["entrances"]["refused"] + rec["entrances"]["added"]:
        build.warn(f"entrance: {x['reason']}")
    if rec["entrances"]["open"]:
        build.warn(f"entrance: {rec['entrances']['open']}")
    return rec
