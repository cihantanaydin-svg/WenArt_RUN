"""A building that makes sense, second series (12 Nov 2026; the architect's audit of 8 buildings, user: "Make sense of
the building", "This is for all the projects").

What: ``apply(build, texts_by_level)`` runs in ``completion.complete`` after the core rules and the windows; it changes
the building in place and returns the record written to ``level_inference.sense_rules``:

1. **Exterior flags from the outline** (``exterior``): a wall is exterior where a room lies on one side and the outside
   (beyond the level's filled outline) or an open-air space on the other, along at least half of the stretches where
   rooms meet it; interior where rooms (or a light well) lie on both sides. Walls with no room on either side keep their
   flag. Each change keeps ``drawn_exterior`` (``adjusted_by_ai`` by code).
2. **A stair rises only into a storey over it** (``stairs``): a stair whose storey above exists and covers less than
   ``STAIR_COVER`` of its footprint (outside the storey's outline: an open roof) is the arriving flight drawn on its
   storey: it is not built upward (``build: false``) and its void in the slab above is removed. The top storey's
   stairs are the builder's (``shell.plan_stairs``: an arrival or capped under the roof).
3. **Shafts are voids** (``shafts``): a face named or holding a shaft word (``SHAFT_RE``: ŞAFT, Ş., TESİSAT, BACA,
   HAVALANDIRMA, duct, riser) that no door reaches and at most ``SHAFT_MAX_M2`` is a shaft (room type ``shaft``, never
   furnished), with its void in the slab of every storey above where the storey below has the shaft too.
4. **Balconies have a door** (``balconies``): a balcony (outdoor space) that no door opens onto gets one: the widest
   window between it and a habitable room becomes its door (``adjusted_by_ai``), else a door is inferred on the wall
   between them (``completion`` balcony door).

Why: the audit's real21-4 and real20-9 (interior walls flagged exterior, where inferred windows would go), real10-5 (a
stair copied onto the top normal floor rising onto the open roof), real20-11, real03-4 and real06-10 (shafts read as
rooms or lost), real03-14 and real20-10 (balconies reached only through a window). Each is a general rule.

How: pure geometry on the building dict (``completion.Level`` probes); no AI.
"""
from __future__ import annotations

import re
from typing import Optional

from shapely.geometry import Point

from wenart import geometry as G
from wenart.ingest import completion as CP

STATION_M = 0.25
EXTERIOR_SHARE = 0.5
STAIR_COVER = 0.3
SHAFT_RE = re.compile(r"(?<![a-z])(?:saft|s\.|tesisat|baca|havalandirma|hava\s+bacasi|duct|riser|vent\s+shaft)"
                      r"(?![a-z])")
SHAFT_MAX_M2 = 3.0
HABITABLE = ("bedroom", "living", "kitchen", "office", "study", "dining")


def _fold(t) -> str:
    return CP._fold(t)


# --------------------------------------------------------------------------------------------- 1. exterior flags
def exterior_flags(b: dict) -> list:
    """Rule 1 (the module docstring); returns the changes ``[{wall, level_id, exterior, reason}]``."""
    out = []
    for lv in b.get("levels") or []:
        level = CP.Level(b, lv["id"])
        if level.outline is None:
            continue
        for w in level.walls.values():
            a, u, length = CP._axis(w)
            if length < 0.3:
                continue
            n = (-u[1], u[0])
            reach = float(w.get("thickness") or 0.15) / 2.0 + CP.PROBE_M
            ext = inner = 0
            steps = max(1, int(length / STATION_M))
            for k in range(steps + 1):
                t = length * (k + 0.5) / (steps + 1)
                c = (a[0] + u[0] * t, a[1] + u[1] * t)
                kinds = [level.kind_at((c[0] + s * n[0] * reach, c[1] + s * n[1] * reach), "") for s in (1, -1)]
                inside = [x in ("room", "light_well") for x in kinds]
                outside = [x in ("outside", "balcony") for x in kinds]
                if any(inside) and any(outside):
                    ext += 1
                elif all(inside):
                    inner += 1
            if ext + inner < 3:
                continue
            flag = ext / (ext + inner) >= EXTERIOR_SHARE
            if bool(w.get("exterior")) == flag:
                continue
            reason = (f"{w['id']}: {'the outside' if flag else 'rooms'} on {'one side' if flag else 'both sides'} along "
                      f"{max(ext, inner)} of {ext + inner} stations: {'exterior' if flag else 'interior'} by the "
                      f"building outline (drawn flag {bool(w.get('exterior'))})")
            for ww in b.get("walls") or []:
                if ww["id"] == w["id"]:
                    ww["drawn_exterior"] = bool(ww.get("exterior"))
                    ww["exterior"] = flag
                    ww["adjusted_by_ai"] = {"by": "code", "rule": "exterior_from_outline", "reason": reason,
                                            "changed": {"exterior": ww["drawn_exterior"]}}
            out.append({"wall": w["id"], "level_id": lv["id"], "exterior": flag, "reason": reason})
    return out


# ------------------------------------------------------------------------------------------------------ 2. stairs
def stairs_over_nothing(b: dict) -> list:
    """Rule 2 (the module docstring); returns the records ``[{stair, level_id, reason}]``."""
    storeys = sorted((lv for lv in b.get("levels") or [] if not lv.get("base_level_id")),
                     key=lambda lv: (lv.get("order") or 0, lv["id"]))
    ids = [lv["id"] for lv in storeys]
    out = []
    for f in b.get("furniture") or []:
        if f.get("type") != "stair" or f.get("build") is False or f.get("level_id") not in ids or \
                not (f.get("footprint") or {}).get("size"):
            continue
        k = ids.index(f["level_id"])
        if k + 1 >= len(ids):
            continue
        above = ids[k + 1]
        if not any(r.get("level_id") == above for r in b.get("rooms") or []):
            continue
        outline = CP.Level(b, above).outline
        if outline is None:
            continue
        fp = f["footprint"]
        from shapely.geometry import Polygon
        poly = Polygon(G.rotated_rectangle(fp["center"], fp["size"], fp["rotation_deg"]))
        if poly.area <= 0 or outline.intersection(poly).area >= STAIR_COVER * poly.area:
            continue
        reason = (f"the stair {f['id']} of {f['level_id']} has no storey over it ({above} covers "
                  f"{outline.intersection(poly).area / poly.area * 100:.0f} % of it): the arriving flight drawn on "
                  f"{f['level_id']}, not built upward; its void in the slab above is removed")
        f["build"] = False
        f["adjusted_by_ai"] = {"by": "code", "rule": "stair_over_nothing", "reason": reason}
        for s in b.get("slabs") or []:
            if s.get("below_level_id") == f["level_id"]:
                s["openings"] = [o for o in s.get("openings") or [] if o.get("furniture_id") != f["id"]]
        out.append({"stair": f["id"], "level_id": f["level_id"], "reason": reason})
    return out


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
def balcony_doors(b: dict, next_id) -> list:
    """Rule 4 (the module docstring); returns the records ``[{space, opening, how, reason}]``."""
    out = []
    spaces = [s for s in (b.get("site") or {}).get("outdoor_spaces") or [] if str(s.get("kind")) == "balcony"]
    for s in spaces:
        lid = s.get("level_id")
        p = CP._poly(s.get("polygon"))
        if p is None or not lid:
            continue
        level = CP.Level(b, lid)
        best_win, best_face = None, None
        has_door = False
        for room in level.rooms:
            if room.get("room_type") not in HABITABLE:
                continue
            for f in level.faces(room):
                if f["kind"] != "balcony":
                    continue
                a, u, _ = CP._axis(level.walls[f["wall_id"]])
                for o in level.openings:
                    if o.get("wall_id") != f["wall_id"] or not o.get("center"):
                        continue
                    t = (o["center"][0] - a[0]) * u[0] + (o["center"][1] - a[1]) * u[1]
                    if not f["t0"] - 0.2 <= t <= f["t1"] + 0.2:
                        continue
                    q = level.at(f["wall_id"], t)
                    if p.distance(Point(q)) > 1.0:
                        continue
                    if o.get("type") == "door":
                        has_door = True
                    elif o.get("type") == "window" and float(o.get("width") or 0) >= 0.6 and \
                            (best_win is None or float(o["width"]) > float(best_win[0]["width"])):
                        best_win = (o, room)
                if best_face is None or f["t1"] - f["t0"] > best_face[0]["t1"] - best_face[0]["t0"]:
                    best_face = (f, room)
        if has_door or (best_win is None and best_face is None):
            continue
        if best_win is not None:
            o, room = best_win
            reason = (f"the balcony {s['id']} has no door: the window {o['id']} of {room['id']} '{room.get('label')}' "
                      f"onto it becomes its door (adjusted_by_ai)")
            o.update(drawn_type="window", type="door", sill_height=None, height=max(float(o.get("height") or 0), 2.1),
                     operation="double" if float(o["width"]) >= 1.2 else "swing", operation_source="assumed",
                     adjusted_by_ai={"by": "code", "rule": "balcony_door", "reason": reason})
            out.append({"space": s["id"], "opening": o["id"], "how": "window to door", "reason": reason})
            continue
        f, room = best_face
        pieces = sorted(level.free(f), key=lambda x: -(x[1] - x[0]))
        if not pieces or pieces[0][1] - pieces[0][0] < CP.BALCONY_DOOR[0]:
            continue
        p0, p1 = pieces[0]
        reason = (f"the balcony {s['id']} has no door and no window onto it: a door inferred from {room['id']} "
                  f"'{room.get('label')}' on {f['wall_id']}")
        o = CP._new_opening("door", next_id("door", lid), level, f["wall_id"], (p0 + p1) / 2.0, CP.BALCONY_DOOR[0],
                            CP.BALCONY_DOOR[1], None, reason, room, f, CP._ev_file(b, lid), None, "default balcony door")
        o["inference"]["rule"] = "balcony_door"
        b["openings"].append(o)
        out.append({"space": s["id"], "opening": o["id"], "how": "inferred door", "reason": reason + " (inferred)"})
    return out


def apply(build, texts_by_level: dict) -> dict:
    """The four rules (the module docstring); the record for ``level_inference.sense_rules``."""
    b = build.building
    rec = {"shafts": shafts(b, texts_by_level), "stairs": stairs_over_nothing(b),
           "balconies": balcony_doors(b, build.ids.next), "exterior": exterior_flags(b)}
    for k, word in (("shafts", "shaft"), ("stairs", "stair"), ("balconies", "balcony")):
        for x in rec[k]:
            build.warn(f"{word}: {x['reason']}")
    if rec["exterior"]:
        build.warn(f"exterior flags: {len(rec['exterior'])} wall(s) set from the building outline "
                   f"({sum(1 for x in rec['exterior'] if not x['exterior'])} interior, "
                   f"{sum(1 for x in rec['exterior'] if x['exterior'])} exterior)")
    return rec
