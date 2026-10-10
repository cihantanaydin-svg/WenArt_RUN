"""Validated furniture and room edits of the agent (docs/milestone11.md §3.2, §5, contract §17.2).

What: ``apply_edit(building, edit)`` applies one edit (move, rotate, resize, change_type, swap_model, add,
add_group, remove, relayout_room, set_room_type) to a COPY of the building and accepts it only when the code checks
pass (inside the room, no overlap, clearances, door swing, window band, walkway, drawn-piece rules of CLAUDE.md)
and the room's plausibility score does not drop.

Contract (frozen; owner: track B):

- ``EDIT_SCHEMAS``: op -> JSON schema of the edit's arguments (the agent's tool parameters). Every edit also
  carries ``reason`` (str), ``round`` (int), ``log_seq`` (int), ``model`` (str).
- ``apply_edit(building, edit, *, catalog=None) -> {"accepted": bool, "failed_checks": [str],
  "score_before": float, "score_after": float, "building": <new building> | None, "changed_ids": [str],
  "rerun_from": "refit" | "layout", "message": str}``; pure: the input is never changed.
- Labels: a changed drawn piece keeps ``drawn_type``, ``drawn_footprint``, ``drawn_front_deg``, ``drawn_height``
  and gets ``adjusted_by_ai = {reason, round, log_seq, model, changed}``; an added piece is ``added_by_ai``;
  an inferred value sets ``inferred: true``.

The edit dict: ``{"op": <EDIT_OPS name or its §3.2 tool name, e.g. move_piece>, <arguments>}`` or
``{"op", "args": {...}}``; ``reason``, ``round``, ``log_seq`` and ``model`` may stand beside ``args``.

How each edit is checked (§5, CLAUDE.md furniture rules):

- every edit: its arguments match ``EDIT_SCHEMAS[op]`` (strict); the placer checks of every floor piece of the room
  before and after (``placer.check_all``; pieces in the frame of their fronts): a check the edit makes fail (on the
  edited piece or on another one) rejects it, a failure the room already had is not counted; then the room's
  ``plausibility.score_room`` must not drop;
- drawn fixed equipment (``schemas.FIXED_TYPES``: stairs, kitchen runs and appliances, sanitary ware): only
  ``rotate``, and only for a clear error (its back is not on a wall or its front faces a wall, and the new front
  fixes that); never moved, resized, retyped or removed;
- drawn furniture: ``move`` / wall snap by at most ``SNAP_MAX_M`` (0.3 m), ``rotate``, ``resize`` to a size within the
  type's product sizes, ``change_type`` within the room type's types (an ``unknown`` piece: any type of the room,
  marked ``inferred``), ``remove`` only with a reason (the piece stays in the JSON with ``build: false``); in a kept
  room (``furnished_rooms: keep`` / ``furnished_rooms_keep`` / ``furnished_rooms_keep_size``) only the orientation
  and clear errors (an unknown piece's type, removal);
- ``added_by_ai`` pieces: free, always through the checks; a removed one leaves the JSON with the decor on it;
- ``add`` / ``add_group``: never a second anchor piece (``schemas.anchor_types``); ``swap_model``: the asset is a
  catalogue model of the piece's type (``catalog.load``), pinned as ``asset_pin`` for the fit;
- ``set_room_type``: the new type passes R1 (area and fixtures) and no piece check gets worse.

``rerun_from``: ``layout`` for ``relayout_room`` and ``set_room_type``, else ``refit``.
"""
from __future__ import annotations

import copy
import dataclasses
import math
import re
from typing import Any, Optional

import jsonschema

from wenart import geometry as G
from wenart.furniture import groups as GR
from wenart.furniture import placer, plausibility as PL, schemas

EDIT_OPS = ("move", "rotate", "resize", "change_type", "swap_model", "add", "add_group", "remove",
            "relayout_room", "set_room_type")
# The tool names of docs/milestone11.md §3.2 -> the ops.
TOOL_OPS: dict[str, str] = {"move_piece": "move", "rotate_piece": "rotate", "resize_piece": "resize",
                            "change_type": "change_type", "swap_model": "swap_model", "add_piece": "add",
                            "add_group": "add_group", "remove_piece": "remove", "relayout_room": "relayout_room",
                            "set_room_type": "set_room_type"}
SNAP_MAX_M = 0.3                 # §5: a drawn piece may move (snap to a wall) by at most this
LAYOUT_OPS = ("relayout_room", "set_room_type")
META_KEYS = ("reason", "round", "log_seq", "model")
ROOM_TYPES = ("living", "dining", "bedroom", "kitchen", "bathroom", "wc", "hall", "balcony", "storage", "prayer",
              "stair", "shaft", "other", "unknown")
EVIDENCE_FILE = "building.json"

_META: dict[str, Any] = {
    "reason": {"type": "string", "minLength": 1, "maxLength": 500, "description": "why (logged, shown in the report)"},
    "round": {"type": "integer", "minimum": 0},
    "log_seq": {"type": "integer", "minimum": 0},
    "model": {"type": "string", "maxLength": 200},
}
_POINT = {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}
_ID = {"type": "string", "minLength": 1, "maxLength": 80}
_FTYPES = sorted(t for t in schemas.SIZE_OPTIONS)


def _schema(props: dict, required: list[str], **extra) -> dict:
    out = {"type": "object", "additionalProperties": False, "properties": dict(props, **_META),
           "required": list(required) + ["reason"]}
    out.update(extra)
    return out


# op -> JSON schema of the arguments (strict: additionalProperties false, required fields).
EDIT_SCHEMAS: dict[str, dict] = {
    "move": _schema({"piece_id": _ID, "center": dict(_POINT, description="new footprint centre [x, y], metres"),
                     "snap_wall_id": dict(_ID, description="snap the back edge onto this wall of the room"),
                     "offset": {"type": "number", "description": "with snap_wall_id: shift along the wall (metres, "
                                                                 "positive towards the wall's end point)"}},
                    ["piece_id"], oneOf=[{"required": ["center"], "not": {"required": ["snap_wall_id"]}},
                                         {"required": ["snap_wall_id"], "not": {"required": ["center"]}}],
                    dependentRequired={"offset": ["snap_wall_id"]}),
    "rotate": _schema({"piece_id": _ID, "front_deg": {"type": "number", "minimum": 0, "maximum": 360,
                                                      "description": "direction the front faces, degrees "
                                                                     "counter-clockwise from +X"}},
                      ["piece_id", "front_deg"]),
    "resize": _schema({"piece_id": _ID, "size": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                                                 "minItems": 2, "maxItems": 2,
                                                 "description": "[width along the front, depth], metres"}},
                      ["piece_id", "size"]),
    "change_type": _schema({"piece_id": _ID, "type": {"enum": _FTYPES}}, ["piece_id", "type"]),
    "swap_model": _schema({"piece_id": _ID, "asset_id": _ID}, ["piece_id", "asset_id"]),
    "add": _schema({"room_id": _ID, "type": {"enum": sorted(schemas.LAYOUT_TYPES)}, "center": _POINT,
                    "front_deg": {"type": "number", "minimum": 0, "maximum": 360}}, ["room_id", "type"],
                   dependentRequired={"front_deg": ["center"]}),
    "add_group": _schema({"room_id": _ID, "group": {"enum": list(GR.GROUPS)},
                          "anchor": {"type": "object", "additionalProperties": False,
                                     "properties": {"piece_id": _ID, "center": _POINT,
                                                    "front_deg": {"type": "number", "minimum": 0, "maximum": 360}}}},
                         ["room_id", "group"]),
    "remove": _schema({"piece_id": _ID}, ["piece_id"]),
    "relayout_room": _schema({"room_id": _ID}, ["room_id"]),
    "set_room_type": _schema({"room_id": _ID, "room_type": {"enum": list(ROOM_TYPES)}}, ["room_id", "room_type"]),
}


class EditRejected(Exception):
    """An edit that breaks a rule before any check runs (unknown piece, a locked drawn piece, ...)."""

    def __init__(self, check: str, message: str):
        super().__init__(message)
        self.check = check
        self.message = message


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def normalise_edit(edit: dict) -> tuple[Optional[str], dict]:
    """``(op, arguments)`` of an edit dict (op or tool name; flat or nested ``args``; meta keys beside ``args``)."""
    name = edit.get("op") or edit.get("tool")
    op = TOOL_OPS.get(name, name)
    if isinstance(edit.get("args"), dict):
        args = {k: v for k, v in edit.items() if k in META_KEYS}
        args.update(edit["args"])
    else:
        args = {k: v for k, v in edit.items() if k not in ("op", "tool")}
    return op, args


def schema_errors(op: str, args: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(EDIT_SCHEMAS[op])
    errors = sorted(validator.iter_errors(args), key=lambda e: list(e.absolute_path))
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<args>'}: {e.message}" for e in errors]


def _piece(b: dict, pid: str) -> dict:
    found = next((f for f in b.get("furniture") or [] if f.get("id") == pid), None)
    if found is None:
        raise EditRejected("piece_exists", f"no piece {pid!r}")
    return found


def _room(b: dict, rid: Optional[str]) -> dict:
    found = next((r for r in b.get("rooms") or [] if r.get("id") == rid), None)
    if found is None:
        raise EditRejected("room_exists", f"no room {rid!r}")
    return found


def _drawn(item: dict) -> bool:
    return item.get("source") == "from_documents"


def _fixed(item: dict) -> bool:
    return _drawn(item) and item.get("type") in schemas.FIXED_TYPES


def kept_room(building: dict, room: dict) -> bool:
    """The room keeps its drawn pieces (the brief's ``furnished_rooms: keep``, ``furnished_rooms_keep`` (ids or
    labels) or ``furnished_rooms_keep_size``): only orientation and clear errors may change there."""
    brief = (building.get("project") or {}).get("brief") or {}
    if brief.get("furnished_rooms") == "keep" or brief.get("furnished_rooms_keep_size"):
        return True
    keep = [str(v).strip().lower() for v in brief.get("furnished_rooms_keep") or []]
    return room["id"].lower() in keep or str(room.get("label", "")).strip().lower() in keep


def _anchor_roles(room: dict) -> set:
    return set(schemas.ANCHOR_TYPES.get(room.get("room_type") or "", ())) | set(
        schemas.anchor_types(room.get("room_type"), room.get("room_subtype")))


def _next_id(b: dict, level_id: str) -> str:
    pattern = re.compile(rf"^f_{re.escape(level_id)}_(\d+)$")
    numbers = [int(m.group(1)) for f in b.get("furniture") or [] for m in [pattern.match(f["id"])] if m]
    return f"f_{level_id}_{max(numbers, default=0) + 1:03d}"


def _set_footprint(item: dict, center, rotation: float, size, front: Optional[float]) -> None:
    item["footprint"] = {"center": [round(float(center[0]), 4), round(float(center[1]), 4)],
                         "size": [round(float(size[0]), 4), round(float(size[1]), 4)],
                         "rotation_deg": round(G.normalise_angle(rotation), 3)}
    item["front_deg"] = round(G.normalise_angle(front), 3) if front is not None else None


def _label(item: dict, before: dict, args: dict, fields: list[str]) -> None:
    """``adjusted_by_ai`` (first old values kept over several edits) and, on a drawn piece, the drawn values."""
    if _drawn(item):
        item.setdefault("drawn_type", before.get("type"))
        item.setdefault("drawn_footprint", copy.deepcopy(before.get("footprint")))
        item.setdefault("drawn_front_deg", before.get("front_deg"))
        item.setdefault("drawn_height", before.get("height"))
    old = item.get("adjusted_by_ai") or {}
    changed = dict(old.get("changed") or {})
    for f in fields:
        changed.setdefault(f, copy.deepcopy(before.get(f)))
    label = {"reason": str(args.get("reason") or "")}
    for k in ("round", "log_seq", "model"):
        if args.get(k) is not None:
            label[k] = args[k]
    label["changed"] = changed
    if old.get("snapped_wall"):                    # M11: a later edit keeps the snap's wider move allowance
        label["snapped_wall"] = old["snapped_wall"]
    item["adjusted_by_ai"] = label


def _ai_evidence(args: dict, text: str) -> list[dict]:
    ev = {"file": EVIDENCE_FILE, "method": "ai", "confidence": 0.8, "text": text}
    if args.get("model"):
        ev["model"] = args["model"]
    return [ev]


def _front_problem(r: "PL._Room", pid: str) -> Optional[str]:
    """The clear orientation error of a piece (F3 back not on a wall, or F4 front into a wall), else None."""
    item = r.item(pid)
    rule = schemas.orientation_rule(item["type"])
    p = r.pieces[pid]
    if rule["back"] in ("wall", "wall_or_group") and not PL.back_on_wall(p, r)[0]:
        return "its back is not on a wall"
    if item["type"] not in schemas.FRONTLESS_TYPES and PL.front_wall_distance(p, r, r.front_dir(pid)) is not None:
        return "its front faces a wall"
    return None


# --------------------------------------------------------------------------
# Placer checks of a room before / after
# --------------------------------------------------------------------------

def _floor_items(b: dict, room_id: str) -> list[dict]:
    return [f for f in b.get("furniture") or [] if f.get("room_id") == room_id and f.get("build") is not False
            and f.get("type") != "unknown" and f.get("type") not in schemas.MOUNTED_TYPES
            and f.get("mount_bottom_m") is None]


def room_checks(b: dict, room_id: str) -> dict[str, set]:
    """piece id -> the placer checks it fails among the room's floor pieces (fronts as drawn)."""
    room = _room(b, room_id)
    items = _floor_items(b, room_id)
    if not items:
        return {}
    ctx = placer.room_context(b, room)
    pieces = [placer.drawn_piece(f, i) for i, f in enumerate(items)]
    return {f["id"]: set(placer.failed_checks(c)) for f, c in zip(items, placer.check_all(pieces, ctx))}


def _new_failures(before: dict[str, set], after: dict[str, set]) -> list[str]:
    out = []
    for pid, failed in sorted(after.items()):
        for name in sorted(failed - before.get(pid, set())):
            out.append(f"{pid}: {name}")
    return out


# --------------------------------------------------------------------------
# The edits (each changes ``b`` in place: the caller's copy)
# --------------------------------------------------------------------------

def _wall_segment(b: dict, ctx: placer.RoomContext, wall_id: str, near) -> tuple[int, float]:
    """(index of the room outline segment on wall ``wall_id`` nearest ``near``, +1/-1: the segment runs with or
    against the wall's start -> end)."""
    wall = next((w for w in b.get("walls") or [] if w.get("id") == wall_id), None)
    if wall is None:
        raise EditRejected("wall_exists", f"no wall {wall_id!r}")
    t = float(wall.get("thickness") or placer.DEFAULT_WALL_THICKNESS_M)
    wdir = math.degrees(math.atan2(wall["end"][1] - wall["start"][1], wall["end"][0] - wall["start"][0]))
    best = None
    for i, (a, c) in enumerate(ctx.segments):
        mid = ((a[0] + c[0]) / 2.0, (a[1] + c[1]) / 2.0)
        diff = G.angle_difference_deg(G.segment_angle_deg(a, c) % 180.0, wdir % 180.0)
        if min(diff, 180.0 - diff) > 5.0:
            continue
        if G.point_segment_distance(mid, wall["start"], wall["end"]) > t / 2.0 + 0.05:
            continue
        key = G.point_segment_distance(near, a, c)
        if best is None or key < best[0]:
            same = G.angle_difference_deg(G.segment_angle_deg(a, c), wdir) < 90.0
            best = (key, i, 1.0 if same else -1.0)
    if best is None:
        raise EditRejected("wall_in_room", f"wall {wall_id} does not bound the piece's room")
    return best[1], best[2]


def _move(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    if _fixed(item):
        raise EditRejected("drawn_lock", f"{item['id']}: drawn fixed equipment ({item['type']}) is never moved")
    if _drawn(item) and kept_room(b, room):
        raise EditRejected("drawn_lock", f"{item['id']}: the room keeps its drawn pieces: only orientation and clear "
                                         f"errors may change")
    before = copy.deepcopy(item)
    p = placer.drawn_piece(item)
    if args.get("center") is not None:
        center, rotation = (float(args["center"][0]), float(args["center"][1])), p.rotation_deg
    else:
        ctx = placer.room_context(b, room)
        seg, sign = _wall_segment(b, ctx, args["snap_wall_id"], p.center)
        others = [placer.drawn_piece(f) for f in _floor_items(b, room["id"]) if f["id"] != item["id"]]
        found = placer.snap_to_wall(p, ctx, seg_index=seg, offset=sign * float(args.get("offset") or 0.0),
                                    max_shift=schemas.WALL_SNAP_MAX_M if _drawn(item) else None, others=others)
        if found is None:
            raise EditRejected("snap", f"{item['id']}: no free place on wall {args['snap_wall_id']} (doors, windows"
                                       + (f", at most {schemas.WALL_SNAP_MAX_M} m from the drawn place"
                                          if _drawn(item) else "") + ")")
        center, rotation = found[0], found[1]
    limit = schemas.WALL_SNAP_MAX_M if args.get("snap_wall_id") else SNAP_MAX_M
    if _drawn(item):
        drawn_center = (item.get("drawn_footprint") or item["footprint"])["center"]
        if G.distance(center, drawn_center) > limit + 1e-6:
            raise EditRejected("drawn_lock", f"{item['id']}: a drawn piece moves at most {SNAP_MAX_M} m, or "
                                             f"{schemas.WALL_SNAP_MAX_M} m when its back snaps onto a wall (this move: "
                                             f"{G.distance(center, drawn_center):.2f} m)")
    front = G.front_direction_deg(rotation) if (item.get("front_deg") is not None or args.get("snap_wall_id")) \
        else None
    _set_footprint(item, center, rotation, p.size, front)
    _label(item, before, args, ["footprint", "front_deg"])
    if args.get("snap_wall_id"):
        item["adjusted_by_ai"]["snapped_wall"] = str(args["snap_wall_id"])
    return [item["id"]]


def _rotate(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    before = copy.deepcopy(item)
    front = float(args["front_deg"]) % 360.0
    _rot, size = placer.front_frame(item["footprint"], item.get("front_deg"))
    if item["type"] in schemas.FRONTLESS_TYPES:
        raise EditRejected("frontless", f"{item['id']}: a {item['type']} has no front to turn")
    if _fixed(item):
        r = PL._Room(b, room)
        problem = _front_problem(r, item["id"]) if item["id"] in r.pieces else None
        if problem is None:
            raise EditRejected("drawn_lock", f"{item['id']}: drawn fixed equipment turns only for a clear error (its "
                                             f"back off the wall or its front into a wall); none here")
        trial = copy.deepcopy(b)
        _set_footprint(_piece(trial, item["id"]), item["footprint"]["center"], front + 90.0, size, front)
        r2 = PL._Room(trial, room)
        if _front_problem(r2, item["id"]) is not None:
            raise EditRejected("drawn_lock", f"{item['id']}: the new front does not fix the error ({problem})")
    _set_footprint(item, item["footprint"]["center"], front + 90.0, size, front)
    _label(item, before, args, ["footprint", "front_deg"])
    return [item["id"]]


def _resize(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    if _fixed(item):
        raise EditRejected("drawn_lock", f"{item['id']}: drawn fixed equipment keeps its drawn size")
    if _drawn(item) and kept_room(b, room):
        raise EditRejected("drawn_lock", f"{item['id']}: the room keeps its drawn pieces' sizes")
    size = (float(args["size"][0]), float(args["size"][1]))
    if item["type"] == "unknown" or not PL._fits(item["type"], size):
        raise EditRejected("product_size", f"{item['id']}: {size[0]:.2f} x {size[1]:.2f} m is not a real "
                                           f"{item['type']} size (size table)")
    before = copy.deepcopy(item)
    r = PL._Room(b, room)
    p = r.pieces.get(item["id"]) or placer.drawn_piece(item)
    center = p.center
    if item["id"] in r.pieces and PL.back_on_wall(p, r)[0]:
        # The back stays on its wall: the piece grows or shrinks from the wall line.
        mid = placer.back_edge_midpoint(p.center, p.rotation_deg, p.size)
        center = placer.anchored_center({"kind": "back_edge", "point": list(mid)}, p.rotation_deg, size)
    front = item.get("front_deg")
    _set_footprint(item, center, p.rotation_deg, size, front)
    if item.get("source") == "added_by_ai":
        item["height"] = schemas.HEIGHTS.get(item["type"], item.get("height"))
    _label(item, before, args, ["footprint"])
    return [item["id"]]


def _change_type(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    new = args["type"]
    old = item["type"]
    if new == old:
        raise EditRejected("no_change", f"{item['id']} is already a {new}")
    rtype, sub = room.get("room_type"), room.get("room_subtype")
    if _drawn(item) and old == "unknown":
        allowed = set(schemas.allowed_types(rtype, sub)) | set(PL.ALWAYS_ALLOWED) - {"unknown"}
    elif _fixed(item) and schemas.misplaced_fixed(old, rtype):
        # real03: fixed equipment in a room that never holds it is a reading error (CLAUDE.md: a clear error).
        allowed = (set(schemas.allowed_types(rtype, sub)) | set(PL.ALWAYS_ALLOWED)) - {"unknown", old}
    elif _fixed(item):
        raise EditRejected("drawn_lock", f"{item['id']}: drawn fixed equipment keeps its type ({old})")
    elif _drawn(item):
        if kept_room(b, room):
            raise EditRejected("drawn_lock", f"{item['id']}: the room keeps its drawn pieces' types")
        allowed = set(schemas.change_types(rtype, sub))
    else:
        allowed = set(schemas.allowed_types(rtype, sub)) - set(schemas.FIXED_TYPES)
    if new not in allowed:
        raise EditRejected("room_type", f"{new} is not a piece a {rtype} room may hold here")
    size = item["footprint"]["size"]
    if not PL._fits(new, size):
        raise EditRejected("product_size", f"{item['id']}: {float(size[0]):.2f} x {float(size[1]):.2f} m does not fit "
                                           f"a {new} (size table)")
    roles = _anchor_roles(room)
    if new in roles and any(f["type"] in roles and f["id"] != item["id"] and f.get("build") is not False
                            for f in b["furniture"] if f.get("room_id") == room["id"]):
        raise EditRejected("second_anchor", f"the room already has its {' / '.join(sorted(roles))}: never a second "
                                            f"anchor piece")
    before = copy.deepcopy(item)
    item["type"] = new
    if item.get("source") == "added_by_ai":
        item["height"] = schemas.HEIGHTS.get(new)
    if old == "unknown":
        item["inferred"] = True
        item.setdefault("evidence", []).append({"file": EVIDENCE_FILE, "method": "inferred", "confidence": 0.7,
                                                "text": f"type {new} inferred by the agent: {args.get('reason')}"})
    _label(item, before, args, ["type", "height"])
    return [item["id"]]


def _swap_model(b: dict, args: dict, catalog) -> list[str]:
    item = _piece(b, args["piece_id"])
    if catalog is None:
        from wenart.furniture import catalog as C
        catalog = C.load()
    entry = catalog.entry(args["asset_id"])
    if entry is None:
        raise EditRejected("asset_exists", f"no catalogue model {args['asset_id']!r}")
    if entry.get("type") != item["type"]:
        raise EditRejected("asset_type", f"{args['asset_id']} is a {entry.get('type')} model, not a {item['type']}")
    before = copy.deepcopy(item)
    item["asset_pin"] = args["asset_id"]
    _label(item, before, args, ["asset_pin"])
    return [item["id"]]


def _new_piece(b: dict, room: dict, piece: placer.Piece, args: dict, text: str) -> dict:
    rot = round(piece.rotation_deg, 2)
    return {"id": _next_id(b, room["level_id"]), "level_id": room["level_id"], "room_id": room["id"],
            "type": piece.type, "type_raw": None, "source": "added_by_ai",
            "footprint": {"center": [round(piece.center[0], 3), round(piece.center[1], 3)],
                          "size": [piece.size[0], piece.size[1]], "rotation_deg": rot},
            "front_deg": round(G.front_direction_deg(rot), 2), "height": schemas.HEIGHTS.get(piece.type),
            "asset": None, "status": "verified", "evidence": _ai_evidence(args, text),
            "adjusted_by_ai": None}


def _check_anchor(b: dict, room: dict, ftype: str) -> None:
    roles = _anchor_roles(room)
    if ftype in roles and any(f["type"] in roles and f.get("build") is not False
                              for f in b["furniture"] if f.get("room_id") == room["id"]):
        raise EditRejected("second_anchor", f"the room already has its {' / '.join(sorted(roles))}: never a second "
                                            f"anchor piece")


def _add(b: dict, args: dict) -> list[str]:
    room = _room(b, args["room_id"])
    ftype = args["type"]
    if ftype not in schemas.allowed_types(room.get("room_type"), room.get("room_subtype")):
        raise EditRejected("room_type", f"a {ftype} is not a piece of a {room.get('room_type')} room")
    _check_anchor(b, room, ftype)
    ctx = placer.room_context(b, room)
    size = schemas.default_size(ftype)
    rule = schemas.orientation_rule(ftype)
    wall = rule["back"] in ("wall", "wall_or_group")
    if args.get("center") is not None:
        center = (float(args["center"][0]), float(args["center"][1]))
        if args.get("front_deg") is not None:
            piece = placer.Piece(ftype, center, G.normalise_angle(float(args["front_deg"]) + 90.0), size, wall)
        else:
            piece = placer.Piece(ftype, center, 0.0, size, wall)
            if wall:
                found = placer.snap_to_wall(piece, ctx)
                if found is None:
                    raise EditRejected("snap", f"no free wall for the {ftype} near {list(center)}")
                piece.center, piece.rotation_deg = found[0], found[1]
    else:
        obstacles = [placer.drawn_piece(f, i) for i, f in enumerate(_floor_items(b, room["id"]))]
        proposal = [{"type": ftype, "center": [ctx.polygon.centroid.x, ctx.polygon.centroid.y], "rotation_deg": 0.0,
                     "size": list(size), "against_wall": wall, "reason": args.get("reason") or "agent"}]
        result = placer.place(proposal, ctx, obstacles=obstacles)
        if not result.pieces:
            why = result.dropped[0]["failed"] if result.dropped else []
            raise EditRejected("no_place", f"no place for a {ftype} in {room['id']} ({', '.join(why)})")
        piece = result.pieces[0]
        if ftype in schemas.COMPANIONS:
            hosts = [o for o in obstacles if o.type in schemas.COMPANIONS[ftype]]
            placer.face_host(piece, hosts)
    item = _new_piece(b, room, piece, args, args.get("reason") or f"{ftype} added by the agent")
    b["furniture"].append(item)
    return [item["id"]]


def _add_group(b: dict, args: dict) -> list[str]:
    room = _room(b, args["room_id"])
    res = GR.place_group(b, room["id"], args["group"], args.get("anchor"))
    if not res["ok"]:
        raise EditRejected("group", f"{args['group']}: {res['reason']}")
    ids = []
    for item in res["pieces"]:
        item = dict(item)
        if args.get("model"):
            item["evidence"] = list(item["evidence"]) + _ai_evidence(args, args.get("reason") or "")
        b["furniture"].append(item)
        ids.append(item["id"])
    return ids


def _remove(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    if item.get("source") == "added_by_ai":
        b["furniture"] = [f for f in b["furniture"] if f["id"] != item["id"]]
        b["decor"] = [d for d in b.get("decor") or [] if d.get("host_id") != item["id"]]
        return [item["id"]]
    room = _room(b, item.get("room_id")) if item.get("room_id") else {}
    if _fixed(item) and not schemas.misplaced_fixed(item["type"], room.get("room_type")):
        raise EditRejected("drawn_lock", f"{item['id']}: drawn fixed equipment ({item['type']}) is never removed")
    if not str(args.get("reason") or "").strip():
        raise EditRejected("reason", f"{item['id']}: a drawn piece is removed only with a reason")
    if item.get("build") is False:
        raise EditRejected("no_change", f"{item['id']} is not built already")
    before = copy.deepcopy(item)
    item["build"] = False
    _label(item, before, args, ["build"])
    return [item["id"]]


def _relayout(b: dict, args: dict) -> list[str]:
    room = _room(b, args["room_id"])
    ai = [f for f in b["furniture"] if f.get("room_id") == room["id"] and f.get("source") == "added_by_ai"
          and f.get("type") not in schemas.MOUNTED_TYPES]
    if not ai:
        raise EditRejected("no_change", f"{room['id']} has no AI pieces to place again")
    drawn = [f for f in _floor_items(b, room["id"]) if f.get("source") == "from_documents"]
    ctx = placer.room_context(b, room)
    obstacles = [placer.drawn_piece(f, i) for i, f in enumerate(drawn)]
    anchors = _anchor_roles(room)
    order = sorted(ai, key=lambda f: (0 if f["type"] in anchors else 1, f["id"]))
    proposal = []
    for f in order:
        p = placer.drawn_piece(f)
        rule = schemas.orientation_rule(f["type"])
        proposal.append({"type": f["type"], "center": list(p.center), "rotation_deg": p.rotation_deg,
                         "size": list(p.size), "against_wall": rule["back"] in ("wall", "wall_or_group"),
                         "reason": "relayout"})
    result = placer.place(proposal, ctx, obstacles=obstacles)
    by_index = {p.proposal_index: p for p in result.pieces}
    hosts = obstacles + list(result.pieces)
    changed = []
    keep_ids = set()
    for k, f in enumerate(order):
        p = by_index.get(k)
        if p is None:
            continue
        targets = schemas.COMPANIONS.get(f["type"]) or tuple(schemas.orientation_rule(f["type"])["front_to"])
        if targets and schemas.orientation_rule(f["type"])["back"] == "free":
            # Seats face their group (a chair its table, an armchair the coffee table or the sofa): turns that keep
            # the footprint (placer.face_host).
            placer.face_host(p, [h for h in hosts if h.type in targets and h is not p])
        before = copy.deepcopy(f)
        _set_footprint(f, p.center, p.rotation_deg, p.size, G.front_direction_deg(p.rotation_deg))
        _label(f, before, args, ["footprint", "front_deg"])
        keep_ids.add(f["id"])
        changed.append(f["id"])
    dropped = [f["id"] for f in order if f["id"] not in keep_ids]
    if dropped:
        b["furniture"] = [f for f in b["furniture"] if f["id"] not in dropped]
        b["decor"] = [d for d in b.get("decor") or [] if d.get("host_id") not in dropped]
    return changed + dropped


def _set_room_type(b: dict, args: dict) -> list[str]:
    room = _room(b, args["room_id"])
    new = args["room_type"]
    if room.get("room_type") == new:
        raise EditRejected("no_change", f"{room['id']} is already a {new}")
    trial = copy.deepcopy(room)
    trial["room_type"] = new
    r = PL._Room(b, trial)
    bad = [v for v in PL._r1(r) if v["severity"] in ("critical", "major")]
    if bad:
        raise EditRejected("R1", "; ".join(v["message"] for v in bad))
    old = room.get("room_type")
    room["room_type"] = new
    label = {"reason": str(args.get("reason") or "")}
    for k in ("round", "log_seq", "model"):
        if args.get(k) is not None:
            label[k] = args[k]
    label["changed"] = dict(((room.get("adjusted_by_ai") or {}).get("changed") or {}))
    label["changed"].setdefault("room_type", old)
    room["adjusted_by_ai"] = label
    return [room["id"]]


# --------------------------------------------------------------------------
# apply_edit
# --------------------------------------------------------------------------

def _result(accepted: bool, failed: list[str], before: float, after: float, building, changed: list[str],
            rerun: str, message: str) -> dict:
    return {"accepted": accepted, "failed_checks": list(failed), "score_before": float(before),
            "score_after": float(after), "building": building, "changed_ids": list(changed), "rerun_from": rerun,
            "message": message}


def _room_id_of(b: dict, op: str, args: dict) -> Optional[str]:
    if "room_id" in args:
        return args["room_id"]
    item = next((f for f in b.get("furniture") or [] if f.get("id") == args.get("piece_id")), None)
    return item.get("room_id") if item else None


def apply_edit(building: dict, edit: dict, *, catalog=None) -> dict:
    """Apply one edit to a copy of ``building`` (see the module docstring); the input is never changed."""
    op, args = normalise_edit(edit if isinstance(edit, dict) else {})
    rerun = "layout" if op in LAYOUT_OPS else "refit"
    if op not in EDIT_SCHEMAS:
        return _result(False, [f"op: unknown edit {op!r} (one of {', '.join(EDIT_OPS)})"], 0.0, 0.0, None, [],
                       rerun, "unknown edit")
    errors = schema_errors(op, args)
    if errors:
        return _result(False, [f"schema: {e}" for e in errors], 0.0, 0.0, None, [], rerun,
                       "the arguments do not match the edit's schema")
    room_id = _room_id_of(building, op, args)
    if room_id is None or not any(r.get("id") == room_id for r in building.get("rooms") or []):
        what = f"piece {args.get('piece_id')!r}" if "piece_id" in args else f"room {args.get('room_id')!r}"
        return _result(False, [f"exists: no {what} in a room of the building"], 0.0, 0.0, None, [], rerun,
                       "nothing to edit")
    before_score = PL.score_room(building, room_id)
    before_checks = room_checks(building, room_id)
    b = copy.deepcopy(building)
    try:
        if op == "move":
            changed = _move(b, args)
        elif op == "rotate":
            changed = _rotate(b, args)
        elif op == "resize":
            changed = _resize(b, args)
        elif op == "change_type":
            changed = _change_type(b, args)
        elif op == "swap_model":
            changed = _swap_model(b, args, catalog)
        elif op == "add":
            changed = _add(b, args)
        elif op == "add_group":
            changed = _add_group(b, args)
        elif op == "remove":
            changed = _remove(b, args)
        elif op == "relayout_room":
            changed = _relayout(b, args)
        else:
            changed = _set_room_type(b, args)
    except EditRejected as exc:
        return _result(False, [f"{exc.check}: {exc.message}"], before_score["score"], before_score["score"], None, [],
                       rerun, exc.message)
    failed = _new_failures(before_checks, room_checks(b, room_id))
    after_score = PL.score_room(b, room_id)
    # The score must not drop; it is compared before the floor at 0 (``penalty``), so a room far below 0 neither
    # hides a worse edit nor an improvement.
    if after_score["penalty"] > before_score["penalty"]:
        new = [v for v in after_score["violations"]
               if (v["check"], v["target"], v["message"]) not in
               {(w["check"], w["target"], w["message"]) for w in before_score["violations"]}]
        failed.append(f"score: plausibility {100 - before_score['penalty']} -> {100 - after_score['penalty']} ("
                      + "; ".join(f"{v['check']} {v['target']}: {v['message']}" for v in new[:4]) + ")")
    out = _result(not failed, failed, before_score["score"], after_score["score"], None if failed else b, changed,
                  rerun, (f"{op} rejected: " + "; ".join(failed[:3])) if failed else
                  f"{op} accepted: score {100 - before_score['penalty']} -> {100 - after_score['penalty']}")
    out["penalty_before"], out["penalty_after"] = before_score["penalty"], after_score["penalty"]
    return out
