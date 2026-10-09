"""Plausibility of rooms and furniture (docs/milestone11.md §4.2, §4.3, §6, contract §17.2).

What: ``score_room(building, room_id)`` and ``score_building(building)`` measure the checklist items F1–F9 and
R1–R4 that code can measure (back to the wall, fronts facing their group, groups complete, real sizes,
clearances, blocked doors and windows, floating pieces, room type vs size and fixtures). The agent's code critic,
the edit validator (``edit_ops.apply_edit``) and the tests use the same functions.

Contract (frozen; owner: track B): pure functions, no I/O, the building is never changed; under 50 ms per room.

``Violation = {"check": "F3", "severity": "critical" | "major" | "minor", "target": <piece/room/opening id>,
"room_id": <id>, "message": <one sentence>, "metrics": {<numbers that prove it>}}``

Why: no stage could see its own result (§1.4): a bed with its headboard in the room, chairs facing away from their
table, an armchair behind a sofa's back all passed every stage. One measured score per room lets the agent's critic
find them and lets the edit validator refuse an edit that makes a room worse.

How (per room; pieces with ``build: false`` are not built and are skipped; decor is a separate list):

- the orientation of a piece is its drawn front (``front_deg``); without one, the side the builder faces it
  (``(270 + rotation) mod 360``, the footprint's local -Y), reported as ``front_assumed`` in the metrics;
- F1 the type is in the room type's row (``schemas.allowed_types``; stairs, lamps, plants and side tables anywhere);
- F2 the footprint fits the type's product size range (``wenart/recognition/size_table.yaml``, +15 %, either way);
- F3 types whose back belongs on a wall (``schemas.ORIENTATION_RULES`` back ``wall``): >= 60 % of the back edge within
  ``BACK_WALL_M`` (5 cm) of the room outline and parallel to the nearest wall within 5 degrees; a sofa
  (``wall_or_group``) may stand free when its front faces its group (TV unit, coffee table);
- F4 the front does not face a wall closer than 0.3 m; and, when one of the type's ``front_to`` types stands within
  ``reach_m``, the front faces one of them (within 45 degrees) from the target's front side (not behind its back);
- F5 groups: a dining table has chairs (by its length, ``CHAIRS_BY_TABLE_LENGTH``; none = major), a bed its
  nightstands, a sofa a coffee table (rooms that may hold one), a desk a chair; an unverified host is skipped;
- F6 front clearances (``placer`` zones; a coffee table, pouf or side table may stand in front of a seat) and the
  0.9 m walkways between doors and to the windows (``placer.walkway_blame``);
- F7 a door's approach strip is blocked (critical; not by a stair, entered through its opening); a piece taller than
  the sill stands in a window band (major);
- F8 a free-standing piece (back ``free``) that touches no wall and has no group partner within ``partner_m``;
- F9 what code can see of "odd": two pieces overlapping (a chair under its table is fine), a piece through the room
  outline (not a stair: it runs into the storey opening), an unexplained ``unknown`` box that is built;
- R1 the room type fits its area and fixtures (a bathtub makes a bathroom; a 3 m² room is no bedroom);
- R2 the level's ceiling height is plausible (2.2–4.0 m); R3 every door swing into the room is free;
- R4 (finishes) is the build's business (track C): listed, not measured here.

Score = 100 − (30 per critical, 10 per major, 3 per minor), floored at 0.
"""
from __future__ import annotations

import functools
import re
import math
from typing import Optional

from shapely.geometry import LineString, Point, Polygon


from wenart import geometry as G
from wenart.furniture import placer, schemas

SEVERITIES = ("critical", "major", "minor")
WEIGHTS: dict[str, int] = {"critical": 30, "major": 10, "minor": 3}

# id -> {"severity": default severity, "what": one line, "measured": code measures it here}.
CHECKS: dict[str, dict] = {
    "F1": {"severity": "major", "what": "the piece's type is allowed in the room type (schemas.allowed_types)",
           "measured": True},
    "F2": {"severity": "major", "what": "the footprint fits the type's product size range (size table, +15 %)",
           "measured": True},
    "F3": {"severity": "major", "what": "the back stands on a wall where the type needs it (bed: critical; a sofa "
                                        "may stand free facing its group)", "measured": True},
    "F4": {"severity": "major", "what": "the front faces its group (sofa -> TV unit / coffee table, chairs -> table, "
                                        "armchairs -> coffee table / sofa) and never a wall closer than 0.3 m",
           "measured": True},
    "F5": {"severity": "minor", "what": "groups complete: dining table + chairs (none: major), bed + nightstands, "
                                        "sofa + coffee table, desk + chair", "measured": True},
    "F6": {"severity": "major", "what": "front clearances (0.6 m; armchairs 0.45 m) and the 0.9 m walkways",
           "measured": True},
    "F7": {"severity": "critical", "what": "no door approach blocked (critical); nothing taller than the sill in a "
                                           "window band (major)", "measured": True},
    "F8": {"severity": "major", "what": "no floating piece: a free-standing piece touches a wall or belongs to a "
                                        "group", "measured": True},
    "F9": {"severity": "major", "what": "nothing odd: overlapping pieces, a piece through the room outline, an "
                                        "unexplained unknown box", "measured": True},
    "R1": {"severity": "major", "what": "the room type fits the area and the fixtures", "measured": True},
    "R2": {"severity": "minor", "what": "the ceiling height is plausible (2.2-4.0 m)", "measured": True},
    "R3": {"severity": "critical", "what": "every door into the room swings into free space", "measured": True},
    "R4": {"severity": "minor", "what": "finishes fit the room (tiles in wet rooms, a splashback in kitchens): "
                                        "measured by the build (track C), not here", "measured": False},
}

AREA_MIN_M2 = 0.01               # intersections below this are touching (drawn pieces meet at their edges)
OVERLAP_MIN_M2 = 0.05            # F9: two pieces overlap
OUTSIDE_MIN_M2 = 0.05            # F9: a piece reaches through the room outline
BACK_SHARE = 0.6                 # F3: share of the back edge that must lie on the wall
SIDE_WALL_M = 0.10               # F8: a side this close to the outline touches a wall
UNKNOWN_LARGE_M2 = 1.0           # F9: an unknown box this large is a major oddity
ALWAYS_ALLOWED = ("stair", "floor_lamp", "potted_plant", "side_table", "unknown")
SEAT_TYPES = ("chair", "bar_stool", "office_chair", "bench")
UNDER_TYPES = ("table_dining", "desk", "kitchen_island", "table_coffee", "kitchen_counter")
TUCKED_TYPES = SEAT_TYPES + ("ottoman", "side_table")
# F6: what may stand in front of a seat besides the placer's CLEARANCE_EXEMPT (a coffee table before a sofa).
EXTRA_EXEMPT: dict[str, tuple[str, ...]] = {"sofa": ("table_coffee", "ottoman"),
                                            "sofa_corner": ("table_coffee", "ottoman")}
# R1: what a fixture says about its room.
FIXTURE_ROOMS: dict[str, tuple[str, ...]] = {
    "bathtub": ("bathroom",), "shower": ("bathroom", "wc"), "toilet": ("bathroom", "wc"),
    "stove": ("kitchen", "living", "dining", "other"), "sink_kitchen": ("kitchen", "living", "dining", "other"),
    "bed_double": ("bedroom", "other", "living"), "bed_single": ("bedroom", "other", "living"),
}
ROOM_MIN_M2: dict[str, tuple[float, str]] = {"bedroom": (6.0, "major"), "living": (8.0, "minor"),
                                             "kitchen": (3.0, "minor"), "dining": (5.0, "minor")}
CEILING_RANGE_M = (2.2, 4.0)
NIGHTSTAND_REACH_M = 0.5
COFFEE_REACH_M = 2.0
CHAIR_REACH_M = 0.8
DESK_CHAIR_REACH_M = 1.0


@functools.lru_cache(maxsize=1)
def _size_table() -> dict:
    from wenart.recognition import symbols   # the M7 size table and its fit rule (lazy: PyYAML)

    return symbols.load_size_table()


def _fits(ftype: str, size) -> bool:
    from wenart.recognition import symbols

    return symbols.fits(_size_table(), ftype, size)


def _violation(check: str, target: str, room_id: str, message: str, metrics: Optional[dict] = None,
               severity: Optional[str] = None) -> dict:
    return {"check": check, "severity": severity or CHECKS[check]["severity"], "target": target, "room_id": room_id,
            "message": message, "metrics": dict(metrics or {})}


class _Room:
    """The measured facts of one room: its outline, context (doors, windows, walkways) and its built pieces in
    the frame of their fronts. Read-only views of the building."""

    def __init__(self, building: dict, room: dict):
        self.building = building
        self.room = room
        self.id = room["id"]
        self.type = room.get("room_type") or "unknown"
        self.ctx = placer.room_context(building, room)
        self.polygon: Polygon = self.ctx.polygon
        self.ring = self.polygon.exterior
        self.items = [f for f in building.get("furniture") or [] if f.get("room_id") == self.id]
        self.built = [f for f in self.items if f.get("build") is not False]
        self.pieces: dict[str, placer.Piece] = {}
        for i, f in enumerate(self.built):
            try:
                self.pieces[f["id"]] = placer.drawn_piece(f, i)
            except (KeyError, TypeError, ValueError):
                continue
        self.polys = {pid: p.polygon() for pid, p in self.pieces.items()}
        # Floor pieces the placer checks: built, typed, standing on the floor.
        self.floor = [f for f in self.built if f["id"] in self.pieces and f["type"] != "unknown"
                      and f["type"] not in schemas.MOUNTED_TYPES and f.get("mount_bottom_m") is None]

    def item(self, pid: str) -> dict:
        return next(f for f in self.built if f["id"] == pid)

    def front_dir(self, pid: str) -> tuple[float, float]:
        a = math.radians(G.front_direction_deg(self.pieces[pid].rotation_deg))
        return math.cos(a), math.sin(a)


def _assumed(item: dict) -> dict:
    return {"front_assumed": True} if item.get("front_deg") is None else {}


def _front_deg(piece: placer.Piece) -> float:
    return round(G.front_direction_deg(piece.rotation_deg), 2)


# --------------------------------------------------------------------------
# F1, F2: type and size
# --------------------------------------------------------------------------

_MULTI_LABEL = re.compile(r"one face holds the room names (.+)$")


def room_types(building: dict, room: dict) -> list[str]:
    """The room's type, plus the types of the other room names its face holds (the pipeline's conflict "one face
    holds the room names 'Açık Mutfak' and 'SALON'": real02's open kitchen is a kitchen and a living room)."""
    from wenart import building as B

    out = [room.get("room_type") or "unknown"]
    for c in building.get("conflicts") or []:
        if room["id"] not in (c.get("element_ids") or []):
            continue
        m = _MULTI_LABEL.search(c.get("description") or "")
        if not m:
            continue
        for name in re.findall(r"'([^']+)'", m.group(1)):
            t = B.room_type_for(name)
            if t and t not in out:
                out.append(t)
    return out


def allowed_in(building: dict, room: dict) -> set:
    """Every type the room's types allow (``room_types``), plus stand-alone lamps, plants and side tables."""
    out = set(ALWAYS_ALLOWED)
    for t in room_types(building, room):
        out |= set(schemas.allowed_types(t, room.get("room_subtype")))
    return out


def _f1(r: _Room) -> list[dict]:
    if not any(t in schemas.ALLOWED_TYPES for t in room_types(r.building, r.room)):
        return []
    allowed = allowed_in(r.building, r.room)
    out = []
    for f in r.built:
        if f["type"] not in allowed:
            # A drawn piece says what the room holds (its row may be narrow, e.g. a sofa in an "other" room): minor,
            # unless it is fixed equipment in the wrong room (a kitchen counter read in a bedroom wardrobe, U12).
            drawn = f.get("source") == "from_documents"
            out.append(_violation("F1", f["id"], r.id, f"{f['type']} is not a piece of a {r.type} room",
                                  {"type": f["type"], "room_type": r.type, "drawn": drawn},
                                  severity="minor" if drawn and f["type"] not in schemas.FIXED_TYPES else None))
    return out


def _f2(r: _Room) -> list[dict]:
    out = []
    for f in r.built:
        if f["type"] in ("unknown", "stair") or f["type"] in schemas.MOUNTED_TYPES:
            continue
        size = [round(float(v), 3) for v in f["footprint"]["size"]]
        if f["type"] in _size_table() and not _fits(f["type"], size):
            out.append(_violation("F2", f["id"], r.id, f"{f['type']} {size[0]:.2f} x {size[1]:.2f} m is outside the "
                                  f"type's product sizes", {"size": size, "type": f["type"]}))
    return out


# --------------------------------------------------------------------------
# F3, F4: back and front
# --------------------------------------------------------------------------

def back_on_wall(piece: placer.Piece, r: "_Room") -> tuple[bool, dict]:
    """(the back edge stands on a wall, metrics): >= ``BACK_SHARE`` of the edge within ``BACK_WALL_M`` of the
    room outline and the nearest outline segment parallel within ``BACK_PARALLEL_DEG``."""
    edge = piece.back_edge()
    samples = [edge.interpolate(t, normalized=True) for t in (0.05, 0.25, 0.5, 0.75, 0.95)]
    dists = [r.ring.distance(pt) for pt in samples]
    share = sum(1 for d in dists if d <= schemas.BACK_WALL_M + 0.005) / len(samples)
    mid = samples[2].coords[0]
    seg = r.ctx.segments[r.ctx.nearest_segment(mid)]
    (x0, y0), (x1, y1) = edge.coords[0], edge.coords[-1]
    edge_deg = math.degrees(math.atan2(y1 - y0, x1 - x0))
    wall_deg = G.segment_angle_deg(seg[0], seg[1])
    diff = G.angle_difference_deg(edge_deg % 180.0, wall_deg % 180.0)
    diff = min(diff, 180.0 - diff)
    ok = share >= BACK_SHARE - 1e-9 and diff <= schemas.BACK_PARALLEL_DEG + 1e-9
    return ok, {"back_wall_m": round(min(dists), 3), "back_on_wall_share": round(share, 2),
                "parallel_deg": round(diff, 1)}


def _front_mid(piece: placer.Piece, d: tuple[float, float]) -> tuple[float, float]:
    half = piece.size[1] / 2.0
    return piece.center[0] + d[0] * half, piece.center[1] + d[1] * half


def front_wall_distance(piece: placer.Piece, r: "_Room", d: tuple[float, float]) -> Optional[float]:
    """Distance from the front edge's midpoint to the room outline straight ahead (None: more than 0.3 m)."""
    m = _front_mid(piece, d)
    ray = LineString([(m[0] + d[0] * 0.005, m[1] + d[1] * 0.005),
                      (m[0] + d[0] * schemas.FRONT_WALL_MIN_M, m[1] + d[1] * schemas.FRONT_WALL_MIN_M)])
    if r.polygon.buffer(1e-4).contains(ray):
        return None
    hit = ray.intersection(r.ring)
    if hit.is_empty:
        return 0.0                                     # the front edge itself is outside the room
    return round(min(Point(m).distance(g) for g in getattr(hit, "geoms", [hit])), 3)


def behind_back(r: "_Room", pid: str, tid: str) -> bool:
    """Piece ``pid`` stands behind the back of piece ``tid`` (a target with a front) and looks at it."""
    titem = r.item(tid)
    if titem["type"] in schemas.FRONTLESS_TYPES:
        return False
    p, t = r.pieces[pid], r.pieces[tid]
    td = r.front_dir(tid)
    along = (p.center[0] - t.center[0]) * td[0] + (p.center[1] - t.center[1]) * td[1]
    if along >= -t.size[1] / 2.0 + 1e-6:
        return False
    pd = r.front_dir(pid)
    return pd[0] * td[0] + pd[1] * td[1] > 0.5           # looking the same way as the target: at its back


def faces(r: "_Room", pid: str, tid: str) -> tuple[bool, float]:
    """(piece ``pid`` faces piece ``tid``, the angle in degrees): the target's nearest point lies within
    ``FACING_DEG`` of the front, and the piece does not stand behind the target's back (a target with a front)."""
    p, t = r.pieces[pid], r.pieces[tid]
    tpoly = r.polys[tid]
    if tpoly.contains(Point(p.center)):
        goal = (tpoly.centroid.x, tpoly.centroid.y)
    else:
        from shapely.ops import nearest_points

        q = nearest_points(tpoly, Point(p.center))[0]
        goal = (q.x, q.y)
    dx, dy = goal[0] - p.center[0], goal[1] - p.center[1]
    if math.hypot(dx, dy) < 1e-6:
        return True, 0.0
    angle = G.angle_difference_deg(math.degrees(math.atan2(dy, dx)), G.front_direction_deg(p.rotation_deg))
    ok = angle <= schemas.FACING_DEG + 1e-9
    titem = r.item(tid)
    if ok and titem["type"] not in schemas.FRONTLESS_TYPES:
        td = r.front_dir(tid)
        along = (p.center[0] - t.center[0]) * td[0] + (p.center[1] - t.center[1]) * td[1]
        if along < -t.size[1] / 2.0 + 1e-6:
            ok = False                                 # behind the target's back
    return ok, round(angle, 1)


def _targets(r: "_Room", pid: str, types, reach: float) -> list[str]:
    poly = r.polys[pid]
    return sorted((tid for tid in r.pieces if tid != pid and r.item(tid)["type"] in types
                   and r.polys[tid].distance(poly) <= reach + 1e-9),
                  key=lambda tid: (round(r.polys[tid].distance(poly), 4), tid))


def _faced_group(r: "_Room", pid: str, rule: dict) -> tuple[Optional[bool], list[str]]:
    """(None when no ``front_to`` target stands within reach, else whether one is faced; the targets)."""
    if not rule["front_to"]:
        return None, []
    targets = _targets(r, pid, rule["front_to"], rule["reach_m"])
    if not targets:
        return None, []
    return any(faces(r, pid, tid)[0] for tid in targets), targets


def _f3_f4(r: _Room) -> list[dict]:
    out = []
    for f in r.built:
        pid = f["id"]
        if pid not in r.pieces or f["type"] in ("unknown", "stair") or f["type"] in schemas.MOUNTED_TYPES:
            continue
        rule = schemas.orientation_rule(f["type"])
        if rule["back"] == "skip":
            continue
        p = r.pieces[pid]
        assumed = _assumed(f)
        faced, targets = _faced_group(r, pid, rule)
        if rule["back"] in ("wall", "wall_or_group"):
            ok, metrics = back_on_wall(p, r)
            if not ok and not (rule["back"] == "wall_or_group" and faced):
                where = "the headboard stands in the room" if f["type"] in ("bed_double", "bed_single", "bunk_bed") \
                    else "its back is not on a wall"
                out.append(_violation("F3", pid, r.id, f"{f['type']}: {where} ({metrics['back_wall_m']:.2f} m off)",
                                      dict(metrics, front_deg=_front_deg(p), **assumed),
                                      severity=rule["back_severity"]))
        if f["type"] in schemas.FRONTLESS_TYPES:
            continue
        d = r.front_dir(pid)
        dist = front_wall_distance(p, r, d)
        if dist is not None:
            out.append(_violation("F4", pid, r.id, f"{f['type']} faces a wall {dist:.2f} m in front of it",
                                  dict({"front_deg": _front_deg(p), "front_wall_m": dist}, **assumed)))
            continue
        backs = [tid for tid in targets if behind_back(r, pid, tid)]
        if backs:
            # U13 (real02 f_L1_029): an armchair behind a sofa's back, looking at it, "faces" nothing it can use.
            out.append(_violation("F4", pid, r.id, f"{f['type']} stands behind the back of "
                                  f"{', '.join(backs)}, looking at it", dict({"front_deg": _front_deg(p),
                                                                              "behind": backs}, **assumed)))
        elif faced is False:
            angles = {tid: faces(r, pid, tid)[1] for tid in targets}
            out.append(_violation("F4", pid, r.id, f"{f['type']} does not face its group ({', '.join(targets)})",
                                  dict({"front_deg": _front_deg(p), "targets": targets, "angles_deg": angles},
                                       **assumed)))
    return out


# --------------------------------------------------------------------------
# F5: groups
# --------------------------------------------------------------------------

def _count_near(r: _Room, pid: str, types, reach: float) -> int:
    return len(_targets(r, pid, types, reach))


def _f5(r: _Room) -> list[dict]:
    out = []
    allowed = set(schemas.allowed_types(r.type, r.room.get("room_subtype"))) if r.type in schemas.ALLOWED_TYPES \
        else set()
    for f in r.built:
        pid, ftype = f["id"], f["type"]
        if pid not in r.pieces or f.get("status") == "unverified":
            continue
        if ftype == "table_dining":
            want = schemas.count_by_length(max(float(v) for v in f["footprint"]["size"]),
                                           schemas.CHAIRS_BY_TABLE_LENGTH)
            n = _count_near(r, pid, SEAT_TYPES, CHAIR_REACH_M)
            if n == 0:
                out.append(_violation("F5", pid, r.id, "dining table without chairs", {"chairs": 0, "expected": want},
                                      severity="major"))
            elif n < want:
                out.append(_violation("F5", pid, r.id, f"dining table with {n} of {want} chairs",
                                      {"chairs": n, "expected": want}))
        elif ftype in schemas.NIGHTSTANDS_PER_BED:
            want = schemas.NIGHTSTANDS_PER_BED[ftype]
            n = _count_near(r, pid, ("nightstand",), NIGHTSTAND_REACH_M)
            if n < want:
                out.append(_violation("F5", pid, r.id, f"{ftype} with {n} of {want} nightstands",
                                      {"nightstands": n, "expected": want}))
        elif ftype in ("sofa", "sofa_corner") and "table_coffee" in allowed:
            if not _count_near(r, pid, ("table_coffee",), COFFEE_REACH_M):
                out.append(_violation("F5", pid, r.id, f"{ftype} without a coffee table", {"coffee_tables": 0}))
        elif ftype == "desk":
            if not _count_near(r, pid, ("chair", "office_chair"), DESK_CHAIR_REACH_M):
                out.append(_violation("F5", pid, r.id, "desk without a chair", {"chairs": 0}))
    return out


# --------------------------------------------------------------------------
# F6, F7, R3: clearances, walkways, doors, windows (the placer's zones)
# --------------------------------------------------------------------------

def _f6_f7_r3(r: _Room) -> list[dict]:
    out = []
    ids = [f["id"] for f in r.floor]
    pieces = [r.pieces[pid] for pid in ids]
    for i, p in enumerate(pieces):
        p.index = i
    polys = [r.polys[pid] for pid in ids]
    room_area = r.polygon.buffer(0.01, join_style="mitre")
    for pid, p, poly in zip(ids, pieces, polys):
        item = r.item(pid)
        if p.type in schemas.CLEARANCE_TYPES:
            zone = p.front_zone()
            exempt = set(schemas.CLEARANCE_EXEMPT.get(p.type, ())) | set(EXTRA_EXEMPT.get(p.type, ()))
            outside = zone.difference(room_area).area
            blockers = [oid for oid, o, op in zip(ids, pieces, polys)
                        if oid != pid and o.type not in exempt and zone.intersection(op).area > AREA_MIN_M2]
            if outside > AREA_MIN_M2 or blockers:
                what = (f"blocked by {', '.join(blockers)}" if blockers else "reaches out of the room")
                out.append(_violation("F6", pid, r.id, f"{p.type}: the free zone in front of it is {what}",
                                      dict({"blockers": blockers, "outside_m2": round(outside, 3),
                                            "zone_m": schemas.CLEARANCE_DEPTH_M.get(p.type,
                                                                                    placer.CLEARANCE_FRONT_M)},
                                           **_assumed(item))))
        for door in (r.ctx.doors if p.type != "stair" else []):      # a stair is entered through its opening
            if poly.intersection(door.zone).area > AREA_MIN_M2:
                out.append(_violation("F7", pid, r.id, f"{p.type} blocks door {door.id}",
                                      {"door": door.id, "area_m2": round(poly.intersection(door.zone).area, 3)}))
        if p.type not in schemas.UNDER_WINDOW_TYPES:
            for win in r.ctx.windows:
                if p.height() > win.sill + 1e-9 and poly.intersection(win.band).area > AREA_MIN_M2:
                    out.append(_violation("F7", pid, r.id, f"{p.type} ({p.height():.2f} m) stands in front of "
                                          f"window {win.id} (sill {win.sill:.2f} m)",
                                          {"window": win.id, "height_m": p.height(), "sill_m": win.sill},
                                          severity="major"))
    for door in r.ctx.doors:
        if door.swing is None or door.swing.is_empty:
            continue
        hits = [pid for pid, p, poly in zip(ids, pieces, polys) if p.type != "stair"
                and poly.intersection(door.swing).area > AREA_MIN_M2]
        if hits:
            # M11 (pod G1, synthetic-01): no drawing gives the hinge side, and the half disc covers both. Critical
            # only when the leaf hits a piece on either hinge; else minor (the leaf is built closed and the door can hinge on
            # the free jamb).
            per_hinge = [[pid for pid, p, poly in zip(ids, pieces, polys) if p.type != "stair"
                          and poly.intersection(q).area > AREA_MIN_M2] for q in door.hinge_swings()]
            free = [i for i, h in enumerate(per_hinge) if not h]
            if per_hinge and free:
                out.append(_violation("R3", door.id, r.id, f"door {door.id} swings into {', '.join(hits)} on one "
                                      "hinge side; the other hinge side is free", {"pieces": hits,
                                      "free_hinge": free[0]}, severity="minor"))
            else:
                out.append(_violation("R3", door.id, r.id, f"door {door.id} swings into {', '.join(hits)}",
                                      {"pieces": hits}))
    if pieces and r.ctx.baseline_pairs:
        blamed, failures = placer.walkway_blame(pieces, r.ctx)
        for pair in failures:
            names = sorted(ids[i] for i in blamed)
            out.append(_violation("F6", names[0] if names else r.id, r.id,
                                  f"no 0.9 m walkway from {pair[1]} to {pair[3]}"
                                  + (f" (blocked by {', '.join(names)})" if names else ""),
                                  {"from": pair[1], "to": pair[3], "blocked_by": names}))
    return out


# --------------------------------------------------------------------------
# F8, F9
# --------------------------------------------------------------------------

def touches_wall(r: _Room, pid: str) -> bool:
    return r.polys[pid].exterior.distance(r.ring) <= SIDE_WALL_M + 1e-9


def _f8(r: _Room) -> list[dict]:
    out = []
    for f in r.built:
        pid = f["id"]
        if pid not in r.pieces:
            continue
        rule = schemas.orientation_rule(f["type"])
        if rule["back"] != "free" or not rule["partners"]:
            continue
        if touches_wall(r, pid) or _targets(r, pid, rule["partners"], rule["partner_m"]):
            continue
        out.append(_violation("F8", pid, r.id, f"{f['type']} stands alone in the room (no wall, no "
                              f"{' / '.join(rule['partners'][:3])} within {rule['partner_m']:.1f} m)",
                              {"partner_m": rule["partner_m"]}))
    return out


def _tucked(a: str, b: str) -> bool:
    return (a in TUCKED_TYPES and b in UNDER_TYPES) or (b in TUCKED_TYPES and a in UNDER_TYPES)


def _f9(r: _Room) -> list[dict]:
    out = []
    ids = [f["id"] for f in r.floor]
    for i, a in enumerate(ids):
        ta = r.item(a)["type"]
        for b in ids[i + 1:]:
            tb = r.item(b)["type"]
            if _tucked(ta, tb):
                continue
            area = r.polys[a].intersection(r.polys[b]).area
            if area > OVERLAP_MIN_M2:
                out.append(_violation("F9", b, r.id, f"{tb} {b} overlaps {ta} {a} by {area:.2f} m²",
                                      {"other": a, "overlap_m2": round(area, 3)}))
    for f in (x for x in r.floor if x["type"] != "stair"):         # a stair runs into the storey opening
        outside = r.polys[f["id"]].difference(r.polygon).area
        if outside > OUTSIDE_MIN_M2:
            out.append(_violation("F9", f["id"], r.id, f"{f['type']} reaches {outside:.2f} m² through the room "
                                  f"outline", {"outside_m2": round(outside, 3)}))
    for f in r.built:
        if f["type"] != "unknown" or f["id"] not in r.polys:
            continue
        area = r.polys[f["id"]].area
        out.append(_violation("F9", f["id"], r.id, f"an unexplained drawn box ({area:.2f} m², type unknown) is built",
                              {"area_m2": round(area, 3)}, severity="major" if area >= UNKNOWN_LARGE_M2 else "minor"))
    return out


# --------------------------------------------------------------------------
# R1, R2
# --------------------------------------------------------------------------

def _r1(r: _Room) -> list[dict]:
    out = []
    area = float(r.room.get("area_computed") or r.polygon.area)
    floor = ROOM_MIN_M2.get(r.type)
    if floor is not None and area < floor[0]:
        out.append(_violation("R1", r.id, r.id, f"a {area:.1f} m² room is too small for a {r.type}",
                              {"area_m2": round(area, 2), "min_m2": floor[0]}, severity=floor[1]))
    if r.type in ("unknown",):
        return out
    seen = set()
    for f in r.built:
        rooms = FIXTURE_ROOMS.get(f["type"])
        if rooms is None or r.type in rooms or f["type"] in seen or f.get("source") != "from_documents":
            continue
        seen.add(f["type"])
        out.append(_violation("R1", r.id, r.id, f"a drawn {f['type']} ({f['id']}) says this is not a {r.type}",
                              {"fixture": f["id"], "room_types": list(rooms)}))
    return out


def _r2(r: _Room) -> list[dict]:
    level = next((lv for lv in r.building.get("levels") or [] if lv.get("id") == r.room.get("level_id")), None)
    if level is None or level.get("ceiling_height") is None:
        return []
    h = float(level["ceiling_height"])
    lo, hi = CEILING_RANGE_M
    if lo <= h <= hi:
        return []
    return [_violation("R2", r.id, r.id, f"ceiling height {h:.2f} m is outside {lo}-{hi} m", {"ceiling_m": h})]


# --------------------------------------------------------------------------
# Scores
# --------------------------------------------------------------------------

def penalty_of(violations: list[dict]) -> int:
    """The sum of the violations' weights (critical 30, major 10, minor 3)."""
    return sum(WEIGHTS[v["severity"]] for v in violations)


def score_of(violations: list[dict]) -> float:
    """100 minus the weights of the violations, floored at 0."""
    return float(max(0, 100 - penalty_of(violations)))


def room_violations(building: dict, room: dict) -> list[dict]:
    """Every violation of one room (see the module docstring), in check order."""
    if len(room.get("polygon") or []) < 3:
        return []
    r = _Room(building, room)
    out = []
    for fn in (_f1, _f2, _f3_f4, _f5, _f6_f7_r3, _f8, _f9, _r1, _r2):
        out.extend(fn(r))
    order = {k: i for i, k in enumerate(CHECKS)}
    return sorted(out, key=lambda v: (order.get(v["check"], 99), str(v["target"])))


def score_room(building: dict, room_id: str) -> dict:
    """``{"room_id", "score": 0..100, "violations": [Violation]}``; also ``penalty`` (the weights before the floor
    at 0: a room far below 0 still shows an edit that removes one violation)."""
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id!r}")
    violations = room_violations(building, room)
    return {"room_id": room_id, "score": score_of(violations), "violations": violations,
            "penalty": penalty_of(violations)}


def score_building(building: dict) -> dict:
    """``{"rooms": {room_id: score_room(...)}, "mean": float, "counts": {"critical": n, "major": n, "minor": n}}``."""
    rooms = {}
    counts = {s: 0 for s in SEVERITIES}
    for room in building.get("rooms") or []:
        res = score_room(building, room["id"])
        rooms[room["id"]] = res
        for v in res["violations"]:
            counts[v["severity"]] += 1
    mean = round(sum(r["score"] for r in rooms.values()) / len(rooms), 2) if rooms else 100.0
    return {"rooms": rooms, "mean": mean, "counts": counts}


def summary_lines(result: dict) -> list[str]:
    """A short text summary of ``score_building`` (rooms worst first, counts per check)."""
    by_check: dict[str, int] = {}
    for res in result["rooms"].values():
        for v in res["violations"]:
            by_check[v["check"]] = by_check.get(v["check"], 0) + 1
    lines = [f"mean score {result['mean']:.1f}; critical {result['counts']['critical']}, major "
             f"{result['counts']['major']}, minor {result['counts']['minor']}",
             "per check: " + ", ".join(f"{k} {by_check[k]}" for k in CHECKS if k in by_check)]
    for rid, res in sorted(result["rooms"].items(), key=lambda kv: (kv[1]["score"], kv[0])):
        lines.append(f"{rid}: {res['score']:.0f} ({len(res['violations'])} violations)")
    return lines
