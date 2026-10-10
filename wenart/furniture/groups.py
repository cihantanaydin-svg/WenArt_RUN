"""Functional furniture groups: the Milestone 12 group data (docs/milestone12.md §4.2, contract §13.2) and the
Milestone 11 ``place_group`` (docs/milestone11.md §6, kept for the agent's ``add_group``). Pure; owner: track G.

Milestone 12 (contract, frozen 10 Oct 2026):

- ``load_groups() -> {name: template}``: ``groups.yaml`` (next to this file) read and validated (``validate_config``:
  a JSON schema of the file, then the cross references: every type is a furniture type of ``schemas.SIZE_OPTIONS``,
  every rule and source named exists, every option names an anchor type or members of its group). ``config()``
  gives the whole file (``rules``, ``weights``, ``use_zones``, ``sources``, ``groups``); ``rule(name)`` one rule;
  ``use_zone(ftype)`` the use zone of a type with its rule names resolved to metres.
- ``group_members(building, room_id) -> [{"group_id", "group", "anchor_id", "member_ids", "missing", "roles"}]``:
  the groups of one room. Pieces that carry ``group`` (the solver writes ``{group_id, group, role, anchor_id}``) are
  grouped by it; the other built pieces are matched by the templates (``match_groups``): every anchor-type piece
  opens a group, partners join the anchor they belong to (a TV unit the sofa it faces best, nightstands, chairs,
  benches and office chairs the nearest anchor within the role's reach), the sanitary ware of a bath is one set,
  the kitchen pieces of a room one run. ``missing``: the partner types the template expects and the room lacks
  (a TV unit and a coffee table for a sofa where the room may hold them, a nightstand per bed side, chairs by the
  table length, a desk chair, a sink / hob / fridge in a kitchen, a toilet and a washbasin in a bath).

Why: the five hard-coded Milestone 11 templates were used by no stage (§1.2); the layout, the completion, the checks
and the agent's tools now share one description of what belongs together.

Milestone 11 (kept): dining set, bed set, living set, desk set, kitchen run. ``place_group`` places a whole group as
one unit (anchor piece + members with their relative offsets and facing) and checks it with the placer.

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
from functools import lru_cache
from pathlib import Path
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


# --------------------------------------------------------------------------
# Milestone 12: groups.yaml (docs/milestone12.md §4.2, §13.2)
# --------------------------------------------------------------------------

GROUPS_YAML = Path(__file__).with_name("groups.yaml")
LAYOUTS = ("anchored", "set", "run")
ANCHOR_PLACES = ("wall", "free")
PARTNER_PLACES = ("facing_wall", "front", "flank", "beside_head", "foot", "around", "chair", "stools", "pair")
ALIGNS = ("centre", "corner", "any")
ZONE_KINDS = ("living", "dining", "sleeping", "work", "kitchen", "bath", "hall", "balcony")
RUN_SHAPES = ("I", "L", "galley", "U")

_NUM = {"type": "number"}
_SIZE = {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0}, "minItems": 2, "maxItems": 2}
_SIZES = {"type": "array", "items": _SIZE, "minItems": 1}
_SIZE_ROW = {"type": "object", "properties": {"max_area": _NUM}, "additionalProperties": _SIZES}
_PARTNER = {"type": "object", "additionalProperties": False, "required": ["role", "type", "required", "place", "sizes"],
            "properties": {"role": {"type": "string"}, "type": {"type": "string"}, "alt_type": {"type": "string"},
                           "required": {"type": "boolean"}, "max": {"type": "integer", "minimum": 1},
                           "place": {"enum": list(PARTNER_PLACES) + ["wall"]}, "of": {"type": "string"},
                           "gap": {"anyOf": [_NUM, {"type": "string"}]}, "facing": {"enum": ["anchor", "same", "of"]},
                           "align": {"enum": list(ALIGNS)}, "option": {"type": "string"},
                           "option_any": {"type": "array", "items": {"type": "string"}}, "sizes": _SIZES}}
_GROUP = {
    "type": "object", "additionalProperties": False,
    "required": ["what", "layout", "zone", "room_types", "priority", "options", "partners"],
    "properties": {
        "what": {"type": "string"}, "layout": {"enum": list(LAYOUTS)}, "zone": {"enum": list(ZONE_KINDS)},
        "room_types": {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "priority": {"type": "integer"},
        "anchor": {"type": "object", "additionalProperties": False, "required": ["types", "place", "sizes"],
                   "properties": {"types": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                                  "place": {"enum": list(ANCHOR_PLACES)}, "align": {"enum": list(ALIGNS)},
                                  "sizes": {"type": "array", "items": _SIZE_ROW, "minItems": 1}}},
        "options": {"type": "object", "minProperties": 1, "additionalProperties": {"type": "object"}},
        "partners": {"type": "array", "items": _PARTNER},
        "members": {"type": "array", "items": _PARTNER},
        "run": {"type": "object", "required": ["depth", "max_leg", "step", "order", "modules"]},
    },
}
CONFIG_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["version", "sources", "rules", "weights", "use_zones", "groups"],
    "properties": {
        "version": {"const": 1},
        "sources": {"type": "object", "additionalProperties": {"type": "string"}},
        "rules": {"type": "object", "additionalProperties": {
            "type": "object", "required": ["source"],
            "properties": {"min": _NUM, "rec": _NUM, "max": _NUM, "source": {"type": "array", "items": {"type": "string"}},
                           "flagged": {"type": "boolean"}, "what": {"type": "string"}}}},
        "weights": {"type": "object", "additionalProperties": {"type": "number", "minimum": 0}},
        "use_zones": {"type": "object", "additionalProperties": {"type": "object"}},
        "groups": {"type": "object", "minProperties": 1, "additionalProperties": _GROUP},
    },
}


class GroupsError(ValueError):
    """``groups.yaml`` does not follow its schema or names something that does not exist."""


def validate_config(data: dict) -> list[str]:
    """Every problem of a parsed ``groups.yaml`` as a readable line (empty = valid)."""
    import jsonschema

    problems = [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
                for e in sorted(jsonschema.Draft202012Validator(CONFIG_SCHEMA).iter_errors(data),
                                key=lambda e: list(e.absolute_path))]
    if problems:
        return problems
    types = set(schemas.SIZE_OPTIONS)
    rules = data["rules"]
    for name, r in rules.items():
        problems += [f"rules/{name}: unknown source {s!r}" for s in r["source"] if s not in data["sources"]]
    for ftype, spec in data["use_zones"].items():
        if ftype not in types:
            problems.append(f"use_zones/{ftype}: not a furniture type")
        for key, value in spec.items():
            if isinstance(value, str) and value not in rules:
                problems.append(f"use_zones/{ftype}/{key}: unknown rule {value!r}")
    for gname, g in data["groups"].items():
        where = f"groups/{gname}"
        pieces = list(g.get("partners") or []) + list(g.get("members") or [])
        anchor_types = (g.get("anchor") or {}).get("types", [])
        for t in anchor_types + [p["type"] for p in pieces] + [p["alt_type"] for p in pieces if p.get("alt_type")]:
            if t not in types:
                problems.append(f"{where}: {t!r} is not a furniture type")
        for row in (g.get("anchor") or {}).get("sizes", []):
            problems += [f"{where}/anchor/sizes: {k!r} is not an anchor type" for k in row
                         if k != "max_area" and k not in anchor_types]
        for p in pieces:
            gap = p.get("gap")
            if isinstance(gap, str) and gap not in rules:
                problems.append(f"{where}/{p['role']}: unknown rule {gap!r}")
        if g["layout"] in ("anchored", "run") and not g.get("anchor"):
            problems.append(f"{where}: an {g['layout']} group needs an anchor")
        if g["layout"] == "set" and not g.get("members"):
            problems.append(f"{where}: a set group needs members")
        if g["layout"] == "run":
            run = g.get("run") or {}
            for key, mod in (run.get("modules") or {}).items():
                if mod.get("type") not in types:
                    problems.append(f"{where}/run/{key}: {mod.get('type')!r} is not a furniture type")
                if mod.get("landing") not in rules:
                    problems.append(f"{where}/run/{key}: unknown landing rule {mod.get('landing')!r}")
            if sorted(run.get("order") or []) != sorted(run.get("modules") or {}):
                problems.append(f"{where}/run: order must name every module")
        roles = {p["role"] for p in pieces}
        for oname, opt in g["options"].items():
            if g["layout"] == "anchored" and opt.get("anchor") not in anchor_types:
                problems.append(f"{where}/options/{oname}: anchor {opt.get('anchor')!r} is not an anchor type")
            for t in opt.get("counts", {}):
                if t not in {p["type"] for p in pieces}:
                    problems.append(f"{where}/options/{oname}: {t!r} is no partner type")
            for role in opt.get("members", []):
                if role not in roles:
                    problems.append(f"{where}/options/{oname}: unknown member role {role!r}")
            if g["layout"] == "run" and opt.get("shape") not in RUN_SHAPES:
                problems.append(f"{where}/options/{oname}: shape must be one of {RUN_SHAPES}")
    return problems


@lru_cache(maxsize=4)
def _load(path: str) -> dict:
    import yaml

    data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    problems = validate_config(data)
    if problems:
        raise GroupsError(f"{path}: " + "; ".join(problems[:8]))
    return data


def config() -> dict:
    """The whole validated ``groups.yaml`` (cached; do not change the returned dict)."""
    return _load(str(GROUPS_YAML))


def load_groups() -> dict:
    """``groups.yaml`` parsed and validated: ``{group name: template}``."""
    return config()["groups"]


def rule(name: str) -> dict:
    """One rule of ``groups.yaml`` (``{min, rec, ..., source, flagged}``); KeyError when unknown."""
    return config()["rules"][name]


def rule_min(name_or_value) -> float:
    """A rule's minimum (a number is returned as it is)."""
    if isinstance(name_or_value, (int, float)):
        return float(name_or_value)
    r = rule(name_or_value)
    return float(r.get("min", r.get("rec", 0.0)))


def rule_rec(name_or_value) -> float:
    """A rule's recommended value (its minimum when it has none)."""
    if isinstance(name_or_value, (int, float)):
        return float(name_or_value)
    r = rule(name_or_value)
    return float(r.get("rec", r.get("min", 0.0)))


def weights() -> dict:
    return dict(config()["weights"])


def use_zone(ftype: str) -> dict:
    """The use zone of a type with rule names resolved: ``{"front": m, "front_rec": m, "sides": m, "foot": m,
    "head_skip": m, "sides_needed": n, "side_half": m, "chairs": m, "back": m}`` (only the keys the type has)."""
    spec = config()["use_zones"].get(ftype) or {}
    out: dict = {}
    for key, value in spec.items():
        if key in ("head_skip", "sides_needed"):
            out[key] = value
        else:
            out[key] = rule_min(value)
            out[key + "_rec"] = rule_rec(value)
            if isinstance(value, str):
                out[key + "_rule"] = value
    return out


def sizes_for(template: dict, ftype: str, area: float) -> list[tuple[float, float]]:
    """The anchor sizes of ``ftype`` for a room (zone) of ``area`` m²: the first size row whose ``max_area`` is above
    the area (the last row has none)."""
    for row in template["anchor"]["sizes"]:
        if row.get("max_area") is None or area < float(row["max_area"]) - 1e-9:
            if ftype in row:
                return [(float(w), float(d)) for w, d in row[ftype]]
    return [schemas.default_size(ftype)]


def group_of_type(ftype: str, room_type: Optional[str]) -> Optional[str]:
    """The group a piece of ``ftype`` anchors (or, for a set or run, belongs to) in a room of ``room_type``."""
    if ftype in ("bed_double",):
        return "sleeping_double"
    if ftype in ("bed_single", "bunk_bed", "crib"):
        return "sleeping_single"
    if ftype in ("sofa", "sofa_corner"):
        return "seating"
    if ftype == "table_dining":
        return "balcony" if room_type == "balcony" else "dining"
    if ftype == "desk":
        return "work"
    if ftype == "wardrobe":
        return "storage"
    if ftype in ("sideboard", "bookshelf") and room_type in ("living", "dining"):
        return "living_storage"
    if ftype in KITCHEN_RUN_TYPES:
        return "kitchen_run"
    if ftype == "kitchen_island":
        return "island"
    if ftype in BATH_TYPES:
        return "wc_set" if room_type == "wc" else "bathroom_set"
    if ftype in ("shoe_cabinet", "console_table") and room_type == "hall":
        return "entrance"
    return None


KITCHEN_RUN_TYPES = ("kitchen_counter", "sink_kitchen", "stove", "fridge", "tall_cabinet")
BATH_TYPES = ("toilet", "washbasin", "shower", "bathtub", "washing_machine")
# role -> (partner types, reach in metres from the anchor's footprint: a partner farther away belongs to no group).
PARTNER_REACH: dict[str, tuple[tuple[str, ...], float]] = {
    "tv": (("tv_unit",), 6.0), "coffee": (("table_coffee", "ottoman"), 2.5), "armchair": (("armchair",), 3.0),
    "nightstand": (("nightstand",), 1.0), "bench": (("bench",), 1.0), "chair": (("chair", "office_chair"), 1.0),
    "stool": (("bar_stool",), 1.0),
}
ROLES_OF_GROUP: dict[str, tuple[str, ...]] = {
    "seating": ("tv", "coffee", "armchair"), "sleeping_double": ("nightstand", "bench"),
    "sleeping_single": ("nightstand", "bench"), "dining": ("chair",), "balcony": ("chair",), "work": ("chair",),
    "island": ("stool",),
}


NOT_BUILT_ASSET_METHODS: tuple[str, ...] = ("none",)   # the fit's library gap: no usable model, not built


def piece_is_built(piece: Optional[dict]) -> bool:
    """A piece the scene builds: ``build`` not false, typed (an ``unknown`` piece is never built) and not a library
    gap the fit left unbuilt (``asset.method == "none"``). The same rule as track S's
    ``wenart.furniture.decor.piece_is_built`` (kept here so the group modules do not import the decor code)."""
    if not piece or piece.get("build", True) is False or piece.get("type") == "unknown":
        return False
    asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
    return asset.get("method") not in NOT_BUILT_ASSET_METHODS


def _room_of(building: dict, room_id: str) -> Optional[dict]:
    return next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)


def _built_floor(building: dict, room_id: str) -> list[dict]:
    return [f for f in building.get("furniture") or [] if f.get("room_id") == room_id and piece_is_built(f)
            and f.get("type") not in schemas.MOUNTED_TYPES and f.get("mount_bottom_m") is None
            and f.get("footprint")]


def _expected_missing(group: str, anchor: Optional[dict], members: list[dict], room: dict) -> list[str]:
    """Partner types the group expects and lacks (see the module docstring)."""
    allowed = set(schemas.allowed_types(room.get("room_type"), room.get("room_subtype")))
    have = [m["type"] for m in members]
    out: list[str] = []
    if group == "seating":
        if "tv_unit" in allowed and "tv_unit" not in have:
            out.append("tv_unit")
        if "table_coffee" in allowed and not ({"table_coffee", "ottoman"} & set(have)):
            out.append("table_coffee")
    elif group in ("sleeping_double", "sleeping_single") and anchor is not None:
        want = schemas.NIGHTSTANDS_PER_BED.get(anchor["type"], 1)
        out += ["nightstand"] * max(0, want - have.count("nightstand"))
    elif group in ("dining",) and anchor is not None and anchor.get("status") != "unverified":
        want = schemas.count_by_length(max(float(v) for v in anchor["footprint"]["size"]),
                                       schemas.CHAIRS_BY_TABLE_LENGTH)
        chairs = sum(1 for t in have if t in ("chair", "bench", "bar_stool"))
        out += ["chair"] * max(0, want - chairs)
    elif group == "work":
        if not any(t in ("office_chair", "chair") for t in have):
            out.append("office_chair")
    elif group == "kitchen_run":
        types = set(have) | ({anchor["type"]} if anchor else set())
        out += [t for t in ("sink_kitchen", "stove", "fridge") if t not in types]
    elif group in ("bathroom_set", "wc_set"):
        types = set(have) | ({anchor["type"]} if anchor else set())
        need = ["toilet", "washbasin"] + (["shower|bathtub"] if group == "bathroom_set" else [])
        for t in need:
            if not any(x in types for x in t.split("|")):
                out.append(t)
    return out


def match_groups(building: dict, room_id: str) -> list[dict]:
    """The groups of one room by the templates (pieces without a ``group`` field are matched; see the module
    docstring). Deterministic: anchors in id order, partners nearest first (ties by id)."""
    room = _room_of(building, room_id)
    if room is None:
        return []
    rtype = room.get("room_type")
    items = _built_floor(building, room_id)
    by_id = {f["id"]: f for f in items}
    polys = {}
    for i, f in enumerate(items):
        try:
            polys[f["id"]] = placer.drawn_piece(f, i).polygon()
        except (KeyError, TypeError, ValueError):
            continue
    out: list[dict] = []
    used: set = set()
    counts: dict[str, int] = {}

    def gid(group: str) -> str:
        counts[group] = counts.get(group, 0) + 1
        return f"{room_id}.{group}" + (f".{counts[group]}" if counts[group] > 1 else "")

    # Sets and runs: one group per room.
    for group, types in (("kitchen_run", KITCHEN_RUN_TYPES), ("bathroom_set", BATH_TYPES)):
        members = sorted((f for f in items if f["type"] in types and f["id"] in polys), key=lambda f: f["id"])
        if group == "kitchen_run" and not any(f["type"] in ("kitchen_counter", "sink_kitchen", "stove")
                                              for f in members):
            members = []       # a lone fridge or tall cabinet is no run
        if group == "bathroom_set" and rtype == "wc":
            group = "wc_set"
        if not members:
            continue
        anchor = next((f for f in members if f["type"] in ("kitchen_counter", "bathtub", "shower", "toilet")),
                      members[0])
        rest = [f for f in members if f is not anchor]
        out.append({"group_id": gid(group), "group": group, "anchor_id": anchor["id"],
                    "member_ids": [f["id"] for f in rest], "roles": {f["id"]: "member" for f in rest},
                    "missing": _expected_missing(group, anchor, rest, room)})
        used |= {f["id"] for f in members}
    # Anchored groups: every anchor-type piece opens one.
    anchors = []
    for f in sorted(items, key=lambda f: f["id"]):
        group = group_of_type(f["type"], rtype)
        if group in (None, "kitchen_run", "bathroom_set", "wc_set", "entrance") or f["id"] not in polys:
            continue
        anchors.append((group, f))
    groups = {f["id"]: {"group_id": gid(group), "group": group, "anchor_id": f["id"], "member_ids": [], "roles": {}}
              for group, f in anchors}
    # Partners: per role, every free piece of the role's types joins the best anchor within reach.
    for role, (types, reach) in PARTNER_REACH.items():
        cands = [f for f in items if f["type"] in types and f["id"] not in used and f["id"] not in groups
                 and f["id"] in polys]
        for f in sorted(cands, key=lambda f: f["id"]):
            best = None
            for group, a in anchors:
                if role not in ROLES_OF_GROUP.get(group, ()):
                    continue
                if role == "chair" and group == "work" and f["type"] not in ("office_chair", "chair"):
                    continue
                d = polys[a["id"]].distance(polys[f["id"]])
                if d > reach + 1e-9:
                    continue
                cost = d
                if role == "tv":
                    cost = _tv_cost(a, f)
                key = (round(cost, 4), a["id"])
                if best is None or key < best[0]:
                    best = (key, a)
            if best is None:
                continue
            g = groups[best[1]["id"]]
            if role == "tv" and any(by_id[m]["type"] == "tv_unit" for m in g["member_ids"]):
                continue
            g["member_ids"].append(f["id"])
            g["roles"][f["id"]] = role
            used.add(f["id"])
    for _group, a in anchors:
        g = groups[a["id"]]
        g["missing"] = _expected_missing(g["group"], a, [by_id[m] for m in g["member_ids"]], room)
        out.append(g)
    return out


def _tv_cost(sofa: dict, tv: dict) -> float:
    """How badly a TV unit sits opposite a sofa: its offset from the sofa's axis plus the angle error (per 10 deg =
    0.3 m), so a TV unit belongs to the sofa it faces best."""
    s = placer.drawn_piece(sofa)
    t = placer.drawn_piece(tv)
    a = math.radians(G.front_direction_deg(s.rotation_deg))
    d = (math.cos(a), math.sin(a))
    rel = (t.center[0] - s.center[0], t.center[1] - s.center[1])
    along = rel[0] * d[0] + rel[1] * d[1]
    lateral = abs(-rel[0] * d[1] + rel[1] * d[0])
    if along <= 0:
        return 100.0 + lateral
    want = G.normalise_angle(G.front_direction_deg(s.rotation_deg) + 180.0)
    err = G.angle_difference_deg(G.front_direction_deg(t.rotation_deg), want)
    return lateral + err / 10.0 * 0.3


def group_members(building: dict, room_id: str) -> list[dict]:
    """``[{"group_id", "group", "anchor_id", "member_ids", "missing": [type], "roles"}]`` of one room (from the
    pieces' ``group`` fields, else matched by the templates)."""
    room = _room_of(building, room_id)
    if room is None:
        return []
    items = _built_floor(building, room_id)
    tagged: dict[str, dict] = {}
    for f in items:
        g = f.get("group")
        if not isinstance(g, dict) or not g.get("group_id"):
            continue
        entry = tagged.setdefault(g["group_id"], {"group_id": g["group_id"], "group": g.get("group"),
                                                 "anchor_id": g.get("anchor_id"), "member_ids": [], "roles": {}})
        if g.get("role") == "anchor":
            entry["anchor_id"] = f["id"]
        else:
            entry["member_ids"].append(f["id"])
            entry["roles"][f["id"]] = g.get("role") or "partner"
    if not tagged:
        return match_groups(building, room_id)
    # Tagged groups first; the untagged pieces are matched around them (a drawn anchor's added partners carry its id).
    matched = match_groups(building, room_id)
    by_id = {f["id"]: f for f in items}
    out = []
    claimed: set = set()
    for gid_, entry in sorted(tagged.items()):
        anchor = by_id.get(entry["anchor_id"]) if entry.get("anchor_id") else None
        same = next((m for m in matched if anchor is not None and m["anchor_id"] == anchor["id"]), None)
        if same is not None:      # the drawn anchor's own matched partners join the tagged ones
            for mid in same["member_ids"]:
                if mid not in entry["member_ids"] and mid not in claimed:
                    entry["member_ids"].append(mid)
                    entry["roles"][mid] = same["roles"].get(mid, "partner")
        entry["member_ids"] = sorted(set(entry["member_ids"]))
        entry["missing"] = _expected_missing(entry["group"] or "", anchor,
                                             [by_id[m] for m in entry["member_ids"] if m in by_id], _room_of(
                                                 building, room_id))
        claimed |= set(entry["member_ids"]) | ({entry["anchor_id"]} if entry.get("anchor_id") else set())
        out.append(entry)
    for m in matched:
        if m["anchor_id"] in claimed:
            continue
        m = dict(m, member_ids=[x for x in m["member_ids"] if x not in claimed])
        out.append(m)
    return out
