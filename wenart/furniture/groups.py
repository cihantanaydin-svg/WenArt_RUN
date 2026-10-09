"""Functional furniture groups (docs/milestone11.md §6, contract §17.2): dining set, bed set, living set,
desk set, kitchen run. ``place_group`` places a whole group as one unit (anchor piece + members with their relative
offsets and facing) and checks it with the placer. Pure; owner: track B.

What: ``place_group(building, room_id, group, anchor=None) -> {"ok", "pieces", "failed", "reason"}``. ``pieces``
are new furniture dicts (``source: added_by_ai``, ``method: rule``, ids after the level's last one); the building is
never changed. ``anchor`` (optional): ``{"piece_id"}`` builds the members around an existing piece of the room (the
chairs of a drawn table); ``{"center": [x, y], "front_deg"?, "type"?, "size"?}`` asks for the anchor near that point.

Why: the agent's ``add_group`` edit and the layout need whole groups that make sense together (chairs facing their
table, nightstands beside the headboard, a coffee table in front of the sofa, a TV unit across from it, the office
chair at the desk), not single pieces the placer pushes apart (U7, U13, U14 of §1.2).

How: the anchor's candidate positions (wall types: every boundary segment, nearest to the asked point or longest
first, slid along it in 10 cm steps by ``placer._snap_to_segment``; free types: a 10 cm grid nearest to the asked
point or the room centre, turned with the room's main wall); at each the members are laid out in the anchor's
frame (``_layout``); the first position where the anchor and every member pass all placer checks (inside the room,
no overlap, clearances, doors, windows, wall contact, walkways; the room's pieces are locked obstacles whose own
drawn-layout failures are excused, ``placer.obstacle_checks``) wins; else the first position where the anchor passes
and the members that fail are left out (``failed``). No anchor position -> ``ok: false`` with the reason. An
existing anchor (``piece_id``) is never moved: only members that pass are returned; an unverified anchor gets no
members (U10: no chairs for an unverified table).
"""
from __future__ import annotations

import dataclasses
import math
import re
from typing import Optional

from wenart import geometry as G
from wenart.furniture import placer, schemas

GROUPS = ("dining_set", "bed_set", "living_set", "desk_set", "kitchen_run")

GRID_M = 0.1
GRID_MAX_M = 3.0
SLIDE_STEP_M = 0.1
MAX_CANDIDATES = 400
CHAIR_SIZE = (0.45, 0.45)
CHAIR_PITCH_M = 0.55            # one chair per 0.55 m of a table side (assumed typical seat width)
CHAIR_GAP_M = 0.02              # a chair stands this far off the table edge (the placer allows no overlap)
COFFEE_GAP_M = 0.62             # sofa front to coffee table: the placer keeps 0.6 m free in front of a sofa
DESK_CHAIR_GAP_M = 0.25         # desk front to the office chair's centre line, past its half depth
NIGHTSTAND_GAP_M = 0.02
TV_REACH_M = 5.0                # the TV unit stands on the wall the sofa faces within this distance
EVIDENCE_FILE = "building.json"


@dataclasses.dataclass
class Member:
    """One piece of a group in the anchor's frame: centre ``(x, y)`` (local, front = -Y), its own size and the
    turn of its front relative to the anchor's front (degrees)."""
    type: str
    local: tuple[float, float]
    size: tuple[float, float]
    turn: float = 0.0
    against_wall: bool = False


# --------------------------------------------------------------------------
# Group layouts (anchor frame: x along the front edge, front towards -Y)
# --------------------------------------------------------------------------

def _anchor_type(group: str, room: dict, anchor: Optional[dict]) -> str:
    if anchor and anchor.get("type"):
        return anchor["type"]
    if group == "bed_set":
        if room.get("room_subtype") == "child":
            return "bed_single"
        return "bed_double" if float(room.get("area_computed") or 0.0) >= 9.0 else "bed_single"
    return schemas.GROUP_TYPES[group]["anchor"][0]


def _anchor_sizes(atype: str, anchor: Optional[dict]) -> list[tuple[float, float]]:
    """The sizes tried for the anchor: the asked size, else the type's options from the default down."""
    if anchor and anchor.get("size"):
        return [(float(anchor["size"][0]), float(anchor["size"][1]))]
    options = schemas.SIZE_OPTIONS[atype]
    if atype == "kitchen_counter":
        return [(2.4, 0.6), (1.8, 0.6), (1.2, 0.6)]
    return [options[schemas.DEFAULT_SIZE_INDEX]] + [o for o in reversed(options[:schemas.DEFAULT_SIZE_INDEX])]


def dining_members(size: tuple[float, float]) -> list[Member]:
    """Chairs around a table ``size`` = (length, width): ``CHAIRS_BY_TABLE_LENGTH`` chairs, as many per long side as
    fit at ``CHAIR_PITCH_M``, the rest at the ends; every chair faces the table."""
    w, d = size
    count = schemas.count_by_length(max(w, d), schemas.CHAIRS_BY_TABLE_LENGTH)
    per_side = max(1, min(count // 2, int((w + 0.05) // CHAIR_PITCH_M)))
    ends = max(0, min(2, count - 2 * per_side))
    off = d / 2.0 + CHAIR_SIZE[1] / 2.0 + CHAIR_GAP_M
    out = []
    for k in range(per_side):
        x = -w / 2.0 + w * (k + 0.5) / per_side
        out.append(Member("chair", (x, -off), CHAIR_SIZE, 180.0))      # front side, facing +Y (the table)
        out.append(Member("chair", (x, off), CHAIR_SIZE, 0.0))         # back side, facing -Y
    end_off = w / 2.0 + CHAIR_SIZE[1] / 2.0 + CHAIR_GAP_M
    for k in range(ends):
        side = -1.0 if k == 0 else 1.0
        out.append(Member("chair", (side * end_off, 0.0), CHAIR_SIZE, 90.0 if side < 0 else 270.0))
    return out


def _members(group: str, atype: str, size: tuple[float, float]) -> list[Member]:
    w, d = size
    if group == "dining_set":
        return dining_members(size)
    if group == "bed_set":
        ns = schemas.SIZE_OPTIONS["nightstand"][1]
        n = schemas.NIGHTSTANDS_PER_BED.get(atype, 1)
        y = d / 2.0 - ns[1] / 2.0                      # the nightstands' backs on the headboard wall
        x = w / 2.0 + ns[0] / 2.0 + NIGHTSTAND_GAP_M
        sides = (1.0, -1.0) if n >= 2 else (1.0,)
        return [Member("nightstand", (s * x, y), ns, 0.0, True) for s in sides]
    if group == "living_set":
        ct = schemas.SIZE_OPTIONS["table_coffee"][1]
        y = -(d / 2.0 + COFFEE_GAP_M + ct[1] / 2.0)
        return [Member("table_coffee", (0.0, y), ct, 0.0)]
    if group == "desk_set":
        ch = schemas.SIZE_OPTIONS["office_chair"][1]
        y = -(d / 2.0 + DESK_CHAIR_GAP_M + ch[1] / 2.0 - 0.15)
        return [Member("office_chair", (0.0, y), ch, 180.0)]
    if group == "kitchen_run":
        out = []
        sink, stove, fridge = (schemas.SIZE_OPTIONS["sink_kitchen"][1], schemas.SIZE_OPTIONS["stove"][1],
                               schemas.SIZE_OPTIONS["fridge"][1])
        # Along the wall: fridge | counter (anchor) | sink | stove; every back on the wall line of the counter.
        x = w / 2.0
        for ftype, s in (("sink_kitchen", sink), ("stove", stove)):
            out.append(Member(ftype, (x + s[0] / 2.0, d / 2.0 - s[1] / 2.0), s, 0.0, True))
            x += s[0]
        out.append(Member("fridge", (-w / 2.0 - fridge[0] / 2.0, d / 2.0 - fridge[1] / 2.0), fridge, 0.0, True))
        return out
    return []


# --------------------------------------------------------------------------
# Pieces and checks
# --------------------------------------------------------------------------

def _world(anchor: placer.Piece, m: Member, index: int) -> placer.Piece:
    c = G.rotate_point((anchor.center[0] + m.local[0], anchor.center[1] + m.local[1]), anchor.rotation_deg,
                       anchor.center)
    return placer.Piece(type=m.type, center=(round(c[0], 3), round(c[1], 3)),
                        rotation_deg=G.normalise_angle(anchor.rotation_deg + m.turn),
                        size=(float(m.size[0]), float(m.size[1])), against_wall=m.against_wall, index=index)


def _quick_fail(p: placer.Piece, others: list, ctx: placer.RoomContext) -> bool:
    """A cheap first test of the placer checks (inside the room, no overlap, doors, windows): most candidate
    positions fail here, before the walkway search of ``placer.obstacle_checks``."""
    poly = p.polygon()
    if not ctx.shrunk.buffer(1e-3, join_style="mitre").contains(poly):
        return True
    if any(poly.intersection(o).area >= placer.AREA_EPS for o in others):
        return True
    return placer._opening_blocked(p, ctx)


def _ok(pieces: list[placer.Piece], obstacles: list[placer.Piece], ctx: placer.RoomContext) -> list[bool]:
    """Per piece of ``pieces`` (the group): passes every placer check among the locked ``obstacles``."""
    obstacle_polys = [o.polygon() for o in obstacles]
    quick = []
    for k, p in enumerate(pieces):
        others = obstacle_polys + [q.polygon() for j, q in enumerate(pieces) if j != k]
        quick.append(not _quick_fail(p, others, ctx))
    if not quick[0]:
        return quick
    allp = list(obstacles) + list(pieces)
    if placer.walkway_failures(allp, ctx):
        # A walkway the room's own pieces leave open must stay open (the blame may fall on a drawn piece).
        return [False] * len(pieces)
    checks = placer.obstacle_checks(allp, ctx)
    return [q and not placer.failed_checks(c) for q, c in zip(quick, checks[len(obstacles):])]


def _wall_candidates(probe: placer.Piece, ctx: placer.RoomContext, near: Optional[tuple]) -> list[tuple]:
    """(center, rotation) with the back on a wall: segments nearest ``near`` (else longest) first, from the
    segment's middle (or the point nearest ``near``) outwards."""
    def seg_key(i: int):
        a, b = ctx.segments[i]
        if near is not None:
            return (round(G.point_segment_distance(near, a, b), 4), i)
        return (-round(G.distance(a, b), 4), i)

    out = []
    for i in sorted(range(len(ctx.segments)), key=seg_key):
        a, b = ctx.segments[i]
        length = G.distance(a, b)
        if length < probe.size[0] + 2 * placer.SNAP_GAP_M:
            continue
        start = near if near is not None else ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        base = dataclasses.replace(probe, center=(start[0], start[1]))
        steps = int(length / SLIDE_STEP_M) + 1
        offsets = [0.0] + [s * k * SLIDE_STEP_M for k in range(1, steps) for s in (1.0, -1.0)]
        seen = set()
        for off in offsets:
            center, rot = placer._snap_to_segment(base, ctx, i, off)
            key = (round(center[0], 2), round(center[1], 2))
            if key in seen:
                continue
            seen.add(key)
            out.append((center, rot))
    return out


def _free_candidates(ctx: placer.RoomContext, near: Optional[tuple], front_deg: Optional[float]) -> list[tuple]:
    """(center, rotation) on a 10 cm grid nearest ``near`` (else the room's centroid); the rotation follows the
    asked front, else the room's longest wall (both ways)."""
    c = near if near is not None else (ctx.polygon.centroid.x, ctx.polygon.centroid.y)
    if front_deg is not None:
        rotations = [G.normalise_angle(float(front_deg) + 90.0)]
    else:
        a, b = max(ctx.segments, key=lambda s: G.distance(*s))
        base = G.normalise_angle(G.segment_angle_deg(a, b))
        rotations = [base % 180.0, (base + 90.0) % 180.0]
    steps = int(GRID_MAX_M / GRID_M)
    offsets = sorted(((ix * GRID_M, iy * GRID_M) for ix in range(-steps, steps + 1) for iy in range(-steps, steps + 1)),
                     key=lambda o: (round(math.hypot(*o), 4), o))
    out = []
    for dx, dy in offsets:
        for rot in rotations:
            out.append(((round(c[0] + dx, 3), round(c[1] + dy, 3)), rot))
    return out


def _tv_member(anchor: placer.Piece, ctx: placer.RoomContext) -> Optional[placer.Piece]:
    """A TV unit on the wall the sofa faces (within ``TV_REACH_M``), centred on the sofa's axis, facing it."""
    a = math.radians(G.front_direction_deg(anchor.rotation_deg))
    d = (math.cos(a), math.sin(a))
    from shapely.geometry import LineString

    ray = LineString([anchor.center, (anchor.center[0] + d[0] * TV_REACH_M, anchor.center[1] + d[1] * TV_REACH_M)])
    hit = ray.intersection(ctx.ring)
    if hit.is_empty:
        return None
    pts = [g for g in getattr(hit, "geoms", [hit]) if g.geom_type == "Point"]
    if not pts:
        return None
    p = min(pts, key=lambda q: G.distance(anchor.center, (q.x, q.y)))
    size = schemas.SIZE_OPTIONS["tv_unit"][1]
    probe = placer.Piece("tv_unit", (p.x - d[0] * 0.3, p.y - d[1] * 0.3), 0.0, size, True)
    seg = ctx.nearest_segment((p.x, p.y))
    center, rot = placer._snap_to_segment(probe, ctx, seg)
    return placer.Piece("tv_unit", center, rot, size, True)


def _group_at(group: str, anchor: placer.Piece, ctx: placer.RoomContext) -> list[placer.Piece]:
    """The members of ``group`` around ``anchor``, only of types the room may hold (a room type without office
    chairs gets a desk alone: a plain chair may not stand in the desk's front clearance)."""
    allowed = set(schemas.allowed_types(ctx.room.get("room_type"), ctx.room.get("room_subtype")))
    members = []
    for i, m in enumerate(_members(group, anchor.type, anchor.size)):
        if m.type in allowed:
            members.append(_world(anchor, m, i + 1))
    if group == "living_set" and "tv_unit" in allowed:
        tv = _tv_member(anchor, ctx)
        if tv is not None:
            members.append(tv)
    return members


# --------------------------------------------------------------------------
# Building dicts
# --------------------------------------------------------------------------

def _next_number(building: dict, level_id: str) -> int:
    pattern = re.compile(rf"^f_{re.escape(level_id)}_(\d+)$")
    numbers = [int(m.group(1)) for f in building.get("furniture") or [] for m in [pattern.match(f["id"])] if m]
    return max(numbers, default=0) + 1


def piece_dict(piece: placer.Piece, room: dict, piece_id: str, group: str, reason: str, checks: dict) -> dict:
    """A placed group piece as a building furniture dict (``added_by_ai``, ``method: rule``)."""
    rotation = round(piece.rotation_deg, 2)
    return {"id": piece_id, "level_id": room["level_id"], "room_id": room["id"], "type": piece.type,
            "type_raw": None, "source": "added_by_ai",
            "footprint": {"center": [round(piece.center[0], 3), round(piece.center[1], 3)],
                          "size": [round(piece.size[0], 3), round(piece.size[1], 3)], "rotation_deg": rotation},
            "front_deg": round(G.front_direction_deg(rotation), 2), "height": schemas.HEIGHTS.get(piece.type),
            "asset": None, "status": "verified", "method": "rule",
            "evidence": [{"file": EVIDENCE_FILE, "method": "derived", "confidence": 0.9,
                          "rule": f"group {group}", "text": reason}],
            "checks": dict(checks), "rule": {"group": group}}


def _result(ok: bool, pieces: list, failed: list, reason: str) -> dict:
    return {"ok": ok, "pieces": pieces, "failed": failed, "reason": reason}


def place_group(building: dict, room_id: str, group: str, anchor: dict | None = None) -> dict:
    """``{"ok": bool, "pieces": [furniture dicts, added_by_ai], "failed": [str], "reason": str}``."""
    if group not in GROUPS:
        return _result(False, [], [], f"unknown group {group!r} (one of {', '.join(GROUPS)})")
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        return _result(False, [], [], f"no room {room_id!r}")
    ctx = placer.room_context(building, room)
    items = [f for f in building.get("furniture") or [] if f.get("room_id") == room_id and f.get("build") is not False
             and f.get("type") not in schemas.MOUNTED_TYPES and f.get("mount_bottom_m") is None]
    existing = [placer.drawn_piece(f, i) for i, f in enumerate(items)]
    obstacles = placer.obstacles_for(existing, ctx)
    ctx = placer.drawn_context(ctx, obstacles)
    number = _next_number(building, room["level_id"])
    anchor = dict(anchor or {})

    if anchor.get("piece_id"):
        host = next((f for f in items if f["id"] == anchor["piece_id"]), None)
        if host is None:
            return _result(False, [], [], f"anchor {anchor['piece_id']} is not a built piece of {room_id}")
        if host.get("status") == "unverified":
            return _result(False, [], [], f"anchor {host['id']} is unverified (its type or footprint is not sure): "
                                          f"no members added (U10)")
        if host["type"] not in schemas.GROUP_TYPES[group]["anchor"]:
            return _result(False, [], [], f"anchor {host['id']} is a {host['type']}, not a "
                                          f"{' / '.join(schemas.GROUP_TYPES[group]['anchor'])}")
        a = placer.drawn_piece(host)
        members = _group_at(group, a, ctx)
        out, failed = [], []
        placed: list[placer.Piece] = []
        for m in members:
            ok = _ok(placed + [m], obstacles, ctx)[-1]
            if ok:
                placed.append(m)
            else:
                failed.append(f"{m.type} at {list(m.center)}: "
                              + ", ".join(placer.failed_checks(placer.obstacle_checks(obstacles + placed + [m],
                                                                                      ctx)[-1])))
        checks = placer.obstacle_checks(obstacles + placed, ctx)[len(obstacles):]
        for k, (m, c) in enumerate(zip(placed, checks)):
            out.append(piece_dict(m, room, f"f_{room['level_id']}_{number + k:03d}", group,
                                  f"{m.type} of the {group} around {host['id']}", c))
        return _result(bool(out), out, failed, f"{len(out)} members around {host['id']}"
                       if out else "no member fits around the anchor")

    atype = _anchor_type(group, room, anchor)
    allowed = schemas.allowed_types(room.get("room_type"), room.get("room_subtype"))
    if atype not in allowed:
        return _result(False, [], [], f"a {atype} is not a piece of a {room.get('room_type')} room")
    roles = set(schemas.ANCHOR_TYPES.get(room.get("room_type") or "", ())) | set(
        schemas.anchor_types(room.get("room_type"), room.get("room_subtype")))
    if atype in roles and any(f["type"] in roles for f in items):
        return _result(False, [], [], f"the room already has its anchor piece ({', '.join(sorted(roles))}): never a "
                                      f"second one")
    near = tuple(float(v) for v in anchor["center"]) if anchor.get("center") else None
    rule = schemas.orientation_rule(atype)
    best_partial = None
    tried = 0
    for size in _anchor_sizes(atype, anchor):
        probe = placer.Piece(atype, near or (ctx.polygon.centroid.x, ctx.polygon.centroid.y), 0.0, size,
                             rule["back"] in ("wall", "wall_or_group"))
        if probe.against_wall:
            cands = _wall_candidates(probe, ctx, near)
        else:
            cands = _free_candidates(ctx, near, anchor.get("front_deg"))
        for center, rot in cands[:MAX_CANDIDATES]:
            tried += 1
            a = dataclasses.replace(probe, center=center, rotation_deg=rot)
            members = _group_at(group, a, ctx)
            oks = _ok([a] + members, obstacles, ctx)
            if not oks[0]:
                continue
            if all(oks):
                return _finish(room, group, a, members, oks, obstacles, ctx, number)
            if best_partial is None or sum(oks) > sum(best_partial[2]):
                best_partial = (a, members, oks)
    if best_partial is not None:
        a, members, oks = best_partial
        return _finish(room, group, a, members, oks, obstacles, ctx, number)
    return _result(False, [], [], f"no place for a {atype} in {room_id} ({tried} positions tried)")


def _finish(room: dict, group: str, a: placer.Piece, members: list[placer.Piece], oks: list[bool],
            obstacles: list[placer.Piece], ctx: placer.RoomContext, number: int) -> dict:
    keep = [a] + [m for m, ok in zip(members, oks[1:]) if ok]
    failed = []
    for m, ok in zip(members, oks[1:]):
        if not ok:
            c = placer.obstacle_checks(obstacles + [a, m], ctx)[-1]
            failed.append(f"{m.type} at {list(m.center)}: {', '.join(placer.failed_checks(c)) or 'with the others'}")
    # Members that pass alone but not together are dropped last to first until the group passes.
    while len(keep) > 1 and not all(_ok(keep, obstacles, ctx)):
        gone = keep.pop()
        failed.append(f"{gone.type} at {list(gone.center)}: does not fit with the other members")
    checks = placer.obstacle_checks(obstacles + keep, ctx)[len(obstacles):]
    pieces = [piece_dict(p, room, f"f_{room['level_id']}_{number + k:03d}", group,
                         f"{p.type} of the {group}" + (" (anchor)" if k == 0 else ""), c)
              for k, (p, c) in enumerate(zip(keep, checks))]
    reason = f"{group}: {a.type} at {list(a.center)} with {len(keep) - 1} of {len(members)} members"
    return _result(True, pieces, failed, reason)
