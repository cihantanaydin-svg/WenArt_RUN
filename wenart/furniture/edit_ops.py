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

Milestone 12 (docs/milestone12.md §5.2, §5.3, §4.1 U1; owner: track G), tools that work on groups:

- ``place_group(room_id, group, option?)``: the solver places a missing group (``groups.yaml``) with the room's other
  pieces fixed; never a second anchor of the room; ``complete_group(group_id)``: the group's missing partners (a
  drawn anchor gets what fits); ``move_group(group_id, span_id, offset?)``: a group of added pieces solved again on a
  free wall span (``free_spans``), partners follow; ``relayout_room(room_id, candidate?, choices?)``: the room solved
  again (its added pieces replaced) with the program's ``choices`` (group id -> option), candidate k (1 = the best).
  These four are accepted when the placer checks hold and no critical or major finding is new (``GROUP_OPS``);
- ``add`` of a type a group misses (a nightstand by a bed) goes through the solver too;
- ``retype_piece(piece_id, type)``: only a type of the room / zone at the piece that fits its footprint (size table,
  not turned 90° against a drawn front); the ``change_type`` locks hold;
- ``mark_not_furniture(piece_id, kind, evidence)``: a drawn piece read from a symbol is not built (``build: false``)
  and recorded in ``symbols[]`` (``former_piece_id``, the crop as evidence); the solver and the checks ignore it;
- ``fix_fixture(piece_id, size?, center?)`` (U1): drawn fixed equipment more than 30 % outside its type's real range
  takes the nearest real size (or the given one); a fixed piece through a wall or in a door swing moves at most 0.5 m
  (to ``center``, or the nearest valid spot); ``locked.check`` accepts exactly that;
- ``set_front(piece_id, front_deg)``: a drawn piece without a front gets one along a side of its footprint (± 1°);
- ``dry_run(edit)``: the answer without the building; ``allowed_edits(building, piece_id)``: per tool ``{allowed, why,
  move_left_m}`` from the locks (the room brief). Every refusal names its numbers.
"""
from __future__ import annotations

import copy
import math
import re
from typing import Any, Optional

import jsonschema

from shapely.geometry import Point

from wenart import geometry as G
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import locked as LK
from wenart.furniture import placer, plausibility as PL, schemas

EDIT_OPS = ("move", "rotate", "resize", "change_type", "swap_model", "add", "add_group", "remove",
            "relayout_room", "set_room_type",
            # Milestone 12 (docs/milestone12.md §5.3)
            "place_group", "complete_group", "move_group", "retype_piece", "mark_not_furniture", "fix_fixture",
            "set_front")
# The tool names of docs/milestone11.md §3.2 and milestone12.md §5.3 -> the ops.
TOOL_OPS: dict[str, str] = {"move_piece": "move", "rotate_piece": "rotate", "resize_piece": "resize",
                            "change_type": "change_type", "swap_model": "swap_model", "add_piece": "add",
                            "add_group": "add_group", "remove_piece": "remove", "relayout_room": "relayout_room",
                            "set_room_type": "set_room_type", "place_group": "place_group",
                            "complete_group": "complete_group", "move_group": "move_group",
                            "retype_piece": "retype_piece", "mark_not_furniture": "mark_not_furniture",
                            "fix_fixture": "fix_fixture", "set_front": "set_front"}
# Ops that place whole groups with the solver: accepted when no critical or major finding is new (a minor one, an
# armchair not quite facing, may come with a group) and the placer checks hold.
GROUP_OPS = ("place_group", "complete_group", "move_group", "relayout_room")
# Reading corrections: a misread symbol left out may leave the room without a piece it needs (a bathroom without its
# toilet); the new findings are reported in the message, not held against the edit (the placer checks still hold).
CORRECTION_OPS = ("mark_not_furniture",)
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
    "relayout_room": _schema({"room_id": _ID,
                              "candidate": {"type": "integer", "minimum": 1, "maximum": 5,
                                            "description": "the solver's candidate k (1 = its best)"},
                              "choices": {"type": "object", "additionalProperties": {"type": "string"},
                                          "description": "group id -> option of the room's program"}}, ["room_id"]),
    "set_room_type": _schema({"room_id": _ID, "room_type": {"enum": list(ROOM_TYPES)}}, ["room_id", "room_type"]),
    "place_group": _schema({"room_id": _ID, "group": {"enum": sorted(GR.load_groups())},
                            "option": {"enum": sorted({o for t in GR.load_groups().values() for o in t["options"]})}},
                           ["room_id", "group"]),
    "complete_group": _schema({"group_id": _ID}, ["group_id"]),
    "move_group": _schema({"group_id": _ID, "span_id": dict(_ID, description="a free wall span (free_spans)"),
                           "offset": {"type": "number", "minimum": 0,
                                      "description": "the anchor's centre, metres from the span's start"}},
                          ["group_id", "span_id"]),
    "retype_piece": _schema({"piece_id": _ID, "type": {"enum": _FTYPES}}, ["piece_id", "type"]),
    "mark_not_furniture": _schema({"piece_id": _ID, "kind": {"enum": ["level_mark", "room_number", "north_arrow",
                                                                     "axis_bubble", "section_mark", "door_arc",
                                                                     "dimension_outline", "text_frame", "other"]},
                                   "evidence": {"type": "string", "minLength": 1, "maxLength": 500,
                                                "description": "the plan crop path or what shows it"}},
                                  ["piece_id", "kind", "evidence"]),
    "fix_fixture": _schema({"piece_id": _ID, "size": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                                                      "minItems": 2, "maxItems": 2,
                                                      "description": "a real product size [width, depth]"},
                            "center": dict(_POINT, description="new centre, at most 0.5 m from the drawn one")},
                           ["piece_id"]),
    "set_front": _schema({"piece_id": _ID, "front_deg": {"type": "number", "minimum": 0, "maximum": 360}},
                         ["piece_id", "front_deg"]),
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
    """piece id -> the placer checks it fails among the room's floor pieces (fronts as drawn). Milestone 12: the
    walkways are the group check G11's (in the score), not the placer's 0.9 m erosion."""
    room = _room(b, room_id)
    items = _floor_items(b, room_id)
    if not items:
        return {}
    ctx = placer.room_context(b, room)
    pieces = [placer.drawn_piece(f, i) for i, f in enumerate(items)]
    return {f["id"]: set(placer.failed_checks(c)) for f, c in zip(items, placer.check_all(pieces, ctx, walkways=False))}


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
    if item.get("front_deg") is not None and PL.oriented_fit(item["type"], size)["turned"]:
        raise EditRejected("product_size", f"{item['id']}: {size[0]:.2f} m along the front x {size[1]:.2f} m deep is "
                                           f"a {item['type']} turned 90° ({_fmt_range(PL.size_range(item['type']))})")
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
        # Milestone 12: a missing partner of a group in the room (a nightstand by a bed) is placed by the group
        # solver at its place in the group; anything else by the placer as before.
        ids = _add_partner(b, room, ftype, args)
        if ids:
            return ids
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


def _add_partner(b: dict, room: dict, ftype: str, args: dict) -> list[str]:
    """One missing partner of ``ftype`` added to the first group of the room that misses it (the solver places the
    group's missing partners and only the first of this type is kept); [] when no group misses one or none fits."""
    for g in GR.group_members(b, room["id"]):
        template = GR.load_groups().get(g.get("group") or "")
        if not template or template["layout"] != "anchored" or ftype not in (g.get("missing") or []):
            continue
        try:
            return _solve_apply(b, room, _program(b, room, [_group_entry(room, g)]), args,
                                f"{ftype} of {g['group_id']}", fixed=_ai_floor_ids(b, room["id"]), only_type=ftype)
        except EditRejected:
            continue
    return []


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
# Milestone 12: group tools, fixture fixes, fronts (docs/milestone12.md §5.3; owner: track G)
# --------------------------------------------------------------------------

def _ai_floor_ids(b: dict, room_id: str, exclude=()) -> list[str]:
    """The room's added floor pieces the solver keeps where they are."""
    ex = set(exclude)
    return [f["id"] for f in b.get("furniture") or [] if f.get("room_id") == room_id and f.get("source") == "added_by_ai"
            and f.get("type") not in schemas.MOUNTED_TYPES and f.get("mount_bottom_m") is None and f["id"] not in ex]


def _why_not(cands: list[dict]) -> str:
    """The numbers of the best failed candidate (hard failures first, then the groups not placed)."""
    if not cands:
        return "no candidate position fits the room"
    c = cands[0]
    parts = list(c.get("hard_failures") or [])[:3] or [f"{x['group']}: {x['reason']}" for x in c.get("not_placed") or []]
    return "; ".join(parts) or "no candidate adds a piece"


def _program(b: dict, room: dict, entries: list[dict], zones: Optional[list] = None) -> dict:
    from wenart.furniture import program as PR

    base = PR.room_program(b, room["id"])
    return {"room_id": room["id"], "zones": list(base.get("zones") or []) + list(zones or []), "groups": entries,
            "reason": "agent edit"}


def _solve_apply(b: dict, room: dict, prog: dict, args: dict, text: str, *, fixed: list[str], index: int = 1,
                 accept=None, only_type: Optional[str] = None) -> list[str]:
    """Solve ``prog`` with ``fixed`` pieces kept, take usable candidate ``index`` (1-based; ``accept`` filters) and
    add its pieces to ``b`` (``only_type``: only the first piece of that type). Returns the new ids."""
    from wenart.furniture import solver as SV

    cands = SV.solve_room(b, room["id"], prog, k=max(3, index), fixed_ids=fixed)
    passing = [c for c in cands if not c["hard_failures"] and c["pieces"]]
    usable = [c for c in passing if accept is None or accept(c)]
    if not usable and passing:
        raise EditRejected("no_place", f"{text}: the places that pass the checks are elsewhere ("
                                       + "; ".join(f"candidate {c['rank']}: {c['pieces'][0]['type']} at "
                                                   f"{c['pieces'][0]['footprint']['center']}" for c in passing[:3]) + ")")
    if not usable:
        raise EditRejected("no_place", f"{text}: no place passes the checks ({_why_not(cands)})")
    if index > len(usable):
        raise EditRejected("candidate", f"candidate {index} does not exist: {len(usable)} usable candidate(s)")
    cand = usable[index - 1]
    if only_type is not None:
        keep = next((p for p in cand["pieces"] if p["type"] == only_type), None)
        if keep is None:
            raise EditRejected("no_place", f"{text}: the solver places no {only_type} ({_why_not(cands)})")
        cand = dict(cand, pieces=[keep])
    new = SV.apply_candidate(b, room["id"], cand)
    before = {f["id"] for f in b["furniture"]}
    added = [f for f in new["furniture"] if f["id"] not in before]
    kept = {f["id"] for f in new["furniture"]}
    b["furniture"] = [f for f in b["furniture"] if f["id"] in kept] + added
    if "decor" in new:
        b["decor"] = new["decor"]
    for f in added:
        f["evidence"] = list(f.get("evidence") or []) + _ai_evidence(args, args.get("reason") or text)
        f["checks"] = {name: True for name in placer.CHECKS}
        f["layout"] = dict(f.get("layout") or {}, candidate=cand["rank"], score=cand["score"])
        if room.get("has_documented_furniture"):
            f["completes_room"] = True
    return [f["id"] for f in added]


def _find_group(b: dict, group_id: str) -> tuple[dict, dict]:
    room_id = str(group_id).split(".", 1)[0]
    room = _room(b, room_id)
    found = next((g for g in GR.group_members(b, room_id) if g["group_id"] == group_id), None)
    if found is None:
        have = ", ".join(g["group_id"] for g in GR.group_members(b, room_id)) or "none"
        raise EditRejected("group_exists", f"no group {group_id!r} in {room_id} (groups: {have})")
    return room, found


def _group_entry(room: dict, g: dict) -> dict:
    from wenart.furniture import program as PR

    template = GR.load_groups()[g["group"]]
    entry = PR._entry(room["id"], g["group"], True, list(template["options"]), anchor_id=g.get("anchor_id"),
                      drawn=True, members=list(g.get("member_ids") or []), missing=list(g.get("missing") or []))
    entry["group_id"] = g["group_id"]
    return entry


def _place_group(b: dict, args: dict) -> list[str]:
    from wenart.furniture import program as PR

    room = _room(b, args["room_id"])
    name = args["group"]
    template = GR.load_groups().get(name)
    if template is None:
        raise EditRejected("group", f"no group template {name!r} (groups.yaml)")
    allowed = GC.allowed_types_at(b, room, None)
    rtype = room.get("room_type")
    if not set(template["room_types"]) & ({rtype} | {z.get("kind") for z in room.get("zones") or []}):
        raise EditRejected("room_type", f"a {name} group does not belong in a {rtype} room (groups.yaml room types: "
                                        f"{', '.join(template['room_types'])})")
    if template["layout"] == "anchored":
        types = set(template["anchor"]["types"]) & allowed
        if not types:
            raise EditRejected("room_type", f"no anchor of the {name} group may stand in a {rtype} room")
        roles = _anchor_roles(room)
        if types & roles and any(f["type"] in roles and GR.piece_is_built(f) for f in b["furniture"]
                                 if f.get("room_id") == room["id"]):
            raise EditRejected("second_anchor", f"the room already has its {' / '.join(sorted(roles))}: never a "
                                                f"second anchor piece (complete_group adds the missing partners)")
    option = args.get("option")
    if option is not None and option not in template["options"]:
        raise EditRejected("option", f"{option!r} is not an option of {name} ({', '.join(template['options'])})")
    rows = [g for g in PR.room_program(b, room["id"])["groups"] if g["group"] == name and not g["drawn"]]
    entry = rows[0] if rows else PR._entry(room["id"], name, True, list(template["options"]))
    taken = {g["group_id"] for g in GR.group_members(b, room["id"])}
    while entry["group_id"] in taken:
        entry["group_id"] += "+"
    entry["required"] = True
    if option is not None:
        entry["chosen"] = option
    return _solve_apply(b, room, _program(b, room, [entry]), args, f"{name} group",
                        fixed=_ai_floor_ids(b, room["id"]))


def _complete_group(b: dict, args: dict) -> list[str]:
    room, g = _find_group(b, args["group_id"])
    anchor = next((f for f in b["furniture"] if f["id"] == g.get("anchor_id")), None)
    if anchor is not None and anchor.get("status") == "unverified":
        raise EditRejected("unverified", f"{g['group_id']}: the anchor {anchor['id']} is unverified (retype_piece "
                                         f"first)")
    if not g.get("missing"):
        raise EditRejected("no_change", f"{g['group_id']}: nothing missing (members: "
                                        f"{', '.join(g.get('member_ids') or []) or 'none'})")
    return _solve_apply(b, room, _program(b, room, [_group_entry(room, g)]), args,
                        f"{g['group_id']} (missing {', '.join(g['missing'])})", fixed=_ai_floor_ids(b, room["id"]))


def free_spans(building: dict, room_id: str, min_length: float = 0.3) -> list[dict]:
    """The free stretches of the room's walls: ``[{"span_id", "edge", "wall_id", "start", "end", "length"}]`` (the
    outline edges, counter-clockwise, minus door openings with 0.10 m each side and the built floor pieces whose back
    stands on the edge); ``span_id`` = ``<room>.s<k>``. ``move_group`` takes one; the room brief lists them."""
    room = _room(building, room_id)
    ctx = placer.room_context(building, room)
    out = []
    walls = LK._wall_shapes(building, room.get("level_id"))
    built = [placer.drawn_piece(f, i) for i, f in enumerate(_floor_items(building, room_id)) if GR.piece_is_built(f)]
    for e, (a, c) in enumerate(ctx.segments):
        length = G.distance(a, c)
        if length < min_length:
            continue
        ux, uy = (c[0] - a[0]) / length, (c[1] - a[1]) / length
        blocked = []
        for d in ctx.doors:
            if G.point_segment_distance(d.inner_point, a, c) <= 0.15:
                t = (d.inner_point[0] - a[0]) * ux + (d.inner_point[1] - a[1]) * uy
                blocked.append((t - d.width / 2.0 - 0.10, t + d.width / 2.0 + 0.10))
        for p in built:
            mid = placer.back_edge_midpoint(p.center, p.rotation_deg, p.size)
            if G.point_segment_distance(mid, a, c) <= 0.10:
                t = (mid[0] - a[0]) * ux + (mid[1] - a[1]) * uy
                blocked.append((t - p.size[0] / 2.0, t + p.size[0] / 2.0))
        mid = ((a[0] + c[0]) / 2.0, (a[1] + c[1]) / 2.0)
        wall_id = None
        if walls:
            wid, shape = min(walls, key=lambda ws: (round(ws[1].distance(Point(mid)), 6), ws[0]))
            wall_id = wid if shape.distance(Point(mid)) <= 0.15 else None
        t0 = 0.0
        for lo, hi in sorted(blocked) + [(length, length)]:
            if lo - t0 >= min_length:
                out.append({"edge": e, "wall_id": wall_id, "start": round(max(0.0, t0), 3),
                            "end": round(min(length, lo), 3)})
            t0 = max(t0, hi)
    for k, s in enumerate(out):
        a, c = ctx.segments[s["edge"]]
        length = G.distance(a, c)
        s["span_id"] = f"{room_id}.s{k}"
        s["length"] = round(s["end"] - s["start"], 3)
        s["from"] = [round(a[0] + (c[0] - a[0]) * s["start"] / length, 3), round(a[1] + (c[1] - a[1]) * s["start"] / length, 3)]
        s["to"] = [round(a[0] + (c[0] - a[0]) * s["end"] / length, 3), round(a[1] + (c[1] - a[1]) * s["end"] / length, 3)]
    return out


def _move_group(b: dict, args: dict) -> list[str]:
    room, g = _find_group(b, args["group_id"])
    ids = [g["anchor_id"]] + list(g.get("member_ids") or []) if g.get("anchor_id") else list(g.get("member_ids") or [])
    items = [f for f in b["furniture"] if f["id"] in ids]
    if any(f.get("source") != "added_by_ai" for f in items):
        drawn = [f["id"] for f in items if f.get("source") != "added_by_ai"]
        raise EditRejected("drawn_lock", f"{g['group_id']}: drawn pieces ({', '.join(drawn)}) stay where they are "
                                         f"drawn; complete_group adds partners, relayout_room re-solves the room")
    span = next((s for s in free_spans(b, room["id"]) if s["span_id"] == args["span_id"]), None)
    if span is None:
        raise EditRejected("span", f"no free span {args['span_id']!r} in {room['id']} (free_spans)")
    ctx = placer.room_context(b, room)
    a, c = ctx.segments[span["edge"]]
    length = G.distance(a, c)
    u = ((c[0] - a[0]) / length, (c[1] - a[1]) / length)
    n = (-u[1], u[0])                                   # inward normal (counter-clockwise outline)
    lo, hi = span["start"], span["end"]
    if args.get("offset") is not None:
        t = lo + float(args["offset"])
        if not lo - 1e-6 <= t <= hi + 1e-6:
            raise EditRejected("span", f"offset {float(args['offset']):.2f} m is outside span {span['span_id']} "
                                       f"({span['length']:.2f} m long)")
        lo, hi = max(span["start"], t - 0.25), min(span["end"], t + 0.25)
    depth = 2.2
    strip = [[a[0] + u[0] * s + n[0] * d, a[1] + u[1] * s + n[1] * d] for s, d in ((lo, 0.0), (hi, 0.0), (hi, depth),
                                                                                 (lo, depth))]
    zone_id = f"{room['id']}.span"
    template = GR.load_groups()[g["group"]]
    option = next(((f.get("layout") or {}).get("option") for f in items if (f.get("layout") or {}).get("option")),
                  None)
    from wenart.furniture import program as PR

    entry = PR._entry(room["id"], g["group"], True, [option] if option in template["options"]
                      else list(template["options"]), zone_id=zone_id)
    entry["group_id"] = g["group_id"]
    trial = copy.deepcopy(b)
    trial["furniture"] = [f for f in trial["furniture"] if f["id"] not in ids]

    def on_span(cand: dict) -> bool:
        first = cand["pieces"][0]
        p = placer.drawn_piece(first)
        mid = placer.back_edge_midpoint(p.center, p.rotation_deg, p.size)
        return G.point_segment_distance(mid, a, c) <= 0.10

    new_ids = _solve_apply(trial, room, _program(trial, room, [entry], [{"zone_id": zone_id, "kind": None,
                                                                         "polygon": strip}]),
                           args, f"{g['group_id']} on span {span['span_id']}", fixed=_ai_floor_ids(trial, room["id"]),
                           accept=on_span)
    b["furniture"] = trial["furniture"]
    b["decor"] = [d for d in b.get("decor") or [] if d.get("host_id") not in ids]
    return ids + new_ids


def _retype(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    p = placer.drawn_piece(item)
    allowed = GC.allowed_types_at(b, room, p.center) - {"unknown"}
    size = (float(item["footprint"]["size"][0]), float(item["footprint"]["size"][1]))
    turned = item.get("front_deg") is not None
    candidates = sorted(t for t in allowed if t in PL._size_table() and PL._fits(t, size) and not (
        turned and PL.oriented_fit(t, p.size)["turned"]))
    if args["type"] not in candidates:
        raise EditRejected("retype", f"{args['type']} is no candidate for {item['id']} ({p.size[0]:.2f} x "
                                     f"{p.size[1]:.2f} m at [{p.center[0]:.2f}, {p.center[1]:.2f}]): the size table and "
                                     f"the room / zone give {', '.join(candidates) or 'none'}")
    return _change_type(b, args)


SYMBOL_KINDS = ("level_mark", "room_number", "north_arrow", "axis_bubble", "section_mark", "door_arc",
                "dimension_outline", "text_frame", "other")


def _mark_not_furniture(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    if not _drawn(item):
        raise EditRejected("drawn_only", f"{item['id']} is {item.get('source')}: only a drawn piece can be a misread "
                                         f"symbol (remove_piece removes an added one)")
    if any(s.get("former_piece_id") == item["id"] for s in b.get("symbols") or []):
        raise EditRejected("no_change", f"{item['id']} is marked as not furniture already")
    before = copy.deepcopy(item)
    item["build"] = False
    _label(item, before, args, ["build"])
    item["adjusted_by_ai"]["not_furniture"] = args["kind"]
    evidence = str(args["evidence"])
    crop = evidence if re.search(r"\.(png|jpe?g|webp)$", evidence, re.I) else None
    pattern = re.compile(rf"^sym_{re.escape(item['level_id'])}_(\d+)$")
    number = max((int(m.group(1)) for s in b.get("symbols") or [] for m in [pattern.match(str(s.get("id")))] if m),
                 default=0) + 1
    ev = {"file": crop or EVIDENCE_FILE, "method": "ai", "confidence": 0.8, "text": f"{args['kind']}: {evidence}"}
    if args.get("model"):
        ev["model"] = args["model"]
    b.setdefault("symbols", []).append({
        "id": f"sym_{item['level_id']}_{number:03d}", "kind": args["kind"], "level_id": item["level_id"],
        "room_id": item.get("room_id"), "footprint": copy.deepcopy(item["footprint"]), "former_piece_id": item["id"],
        "reason": str(args.get("reason") or ""), "crop": crop, "evidence": [ev]})
    b["decor"] = [d for d in b.get("decor") or [] if d.get("host_id") != item["id"]]
    return [item["id"]]


FIXTURE_OFF_RANGE = 0.30         # U1: a fixed piece's drawn size more than 30 % outside its type's real range
FIXTURE_MOVE_M = 0.50            # U1: a fixed piece through a wall or in a door swing moves at most this far


def fixture_problems(building: dict, item: dict) -> dict:
    """U1 (docs/milestone12.md §4.1) of a drawn fixed piece: ``{"size": {...} | None, "place": {...} | None}``;
    size: ``{"drawn", "range", "off", "product"}`` when a side is more than ``FIXTURE_OFF_RANGE`` outside its real
    range (``product``: the nearest real size); place: ``{"outside_m2", "door"}`` when it stands through a wall
    (more than 0.01 m² outside the room) or in a door's approach or swing."""
    out: dict = {"size": None, "place": None}
    rng = PL.size_range(item["type"])
    p = placer.drawn_piece(item)
    if rng is not None:
        offs, product = [], []
        for v, (lo, hi) in zip(p.size, rng):
            off = (lo - v) / lo if v < lo else (v - hi) / hi if v > hi else 0.0
            offs.append(off)
            product.append(min(max(v, lo), hi))
        if max(offs) > FIXTURE_OFF_RANGE + 1e-9:
            out["size"] = {"drawn": [round(v, 3) for v in p.size], "range": [list(r) for r in rng],
                           "off": round(max(offs), 3), "product": [round(v, 3) for v in product]}
    room = next((r for r in building.get("rooms") or [] if r.get("id") == item.get("room_id")), None)
    if room is not None:
        out["place"] = _place_problem(building, room, p)
    return out


def _place_problem(building: dict, room: dict, p: placer.Piece) -> Optional[dict]:
    ctx = placer.room_context(building, room)
    poly = p.polygon()
    outside = poly.difference(ctx.polygon).area
    door = next((d.id for d in ctx.doors for z in (d.zone, d.swing) if z is not None and not z.is_empty
                 and poly.intersection(z).area > placer.AREA_EPS), None)
    if outside > 0.01 or door:
        return {"outside_m2": round(outside, 3), "door": door}
    return None


def _fix_fixture(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    if not _fixed(item):
        raise EditRejected("fixture", f"{item['id']} is a {item['type']} ({item.get('source')}): fix_fixture is for "
                                      f"drawn fixed equipment (stairs, kitchen runs, sanitary ware)")
    probs = fixture_problems(b, item)
    before = copy.deepcopy(item)
    p = placer.drawn_piece(item)
    size = p.size
    resized = False
    if args.get("size") is not None or probs["size"]:
        if probs["size"] is None:
            rng = PL.size_range(item["type"])
            raise EditRejected("fixture_size", f"{item['id']}: the drawn {p.size[0]:.2f} x {p.size[1]:.2f} m is within "
                                               f"{int(FIXTURE_OFF_RANGE * 100)} % of the real {item['type']} range "
                                               f"({_fmt_range(rng)}): its size stays as drawn")
        size = tuple(float(v) for v in (args.get("size") or probs["size"]["product"]))
        rng = PL.size_range(item["type"])
        if any(not (lo / 1.05 - 1e-9 <= v <= hi * 1.05 + 1e-9) for v, (lo, hi) in zip(size, rng)):
            raise EditRejected("product_size", f"{item['id']}: {size[0]:.2f} x {size[1]:.2f} m is not a real "
                                               f"{item['type']} size ({_fmt_range(rng)})")
        resized = True
    center = p.center
    if resized:
        anchor = LK.anchor_of(item, b)
        if anchor["kind"] == "back_edge":            # grows or shrinks from its wall line
            center = placer.anchored_center(anchor, p.rotation_deg, size)
    moved = 0.0
    place = _place_problem(b, room, placer.Piece(p.type, center, p.rotation_deg, size, False))
    if args.get("center") is not None:
        target = (float(args["center"][0]), float(args["center"][1]))
        moved = G.distance(target, p.center)
        if place is None and probs["place"] is None:
            raise EditRejected("fixture_place", f"{item['id']} stands inside the room and off every door: it is "
                                                f"not moved")
        if moved > FIXTURE_MOVE_M + 1e-6:
            raise EditRejected("fixture_move", f"{item['id']}: the move is {moved:.2f} m, at most "
                                               f"{FIXTURE_MOVE_M:.2f} m")
        center = target
        if _place_problem(b, room, placer.Piece(p.type, center, p.rotation_deg, size, False)) is not None:
            raise EditRejected("fixture_place", f"{item['id']} at [{center[0]:.2f}, {center[1]:.2f}] is still through "
                                                f"a wall or in a door swing")
    elif place is not None:
        spot = _nearest_valid(b, room, item, placer.Piece(p.type, center, p.rotation_deg, size, False))
        if spot is None:
            raise EditRejected("fixture_place", f"{item['id']}: no valid spot within {FIXTURE_MOVE_M:.2f} m (it "
                                                f"stands {place['outside_m2']:.2f} m² outside the room"
                                                + (f", in door {place['door']}" if place["door"] else "") + ")")
        center = spot
        moved = G.distance(center, p.center)
    if not resized and moved < 1e-6:
        raise EditRejected("no_change", f"{item['id']}: nothing to fix (size within the real range, inside the room "
                                        f"and off the doors)")
    _set_footprint(item, center, p.rotation_deg, size, item.get("front_deg"))
    _label(item, before, args, ["footprint"])
    item["adjusted_by_ai"]["fix_fixture"] = {"resized": resized, "moved_m": round(moved, 3),
                                             "size": probs["size"], "place": probs["place"] or place}
    return [item["id"]]


def _fmt_range(rng) -> str:
    if rng is None:
        return "no size table entry"
    (w0, w1), (d0, d1) = rng
    return f"width {w0:.2f}-{w1:.2f} m, depth {d0:.2f}-{d1:.2f} m"


def _nearest_valid(b: dict, room: dict, item: dict, p: placer.Piece) -> Optional[tuple[float, float]]:
    """The nearest centre within ``FIXTURE_MOVE_M`` (0.05 m grid, nearest first) where the piece stands inside the
    room, off the doors and off the other built pieces."""
    others = [placer.drawn_piece(f).polygon() for f in _floor_items(b, room["id"]) if f["id"] != item["id"]
              and GR.piece_is_built(f)]
    step = 0.05
    n = int(FIXTURE_MOVE_M / step)
    offsets = sorted(((i * step, j * step) for i in range(-n, n + 1) for j in range(-n, n + 1)
                      if math.hypot(i * step, j * step) <= FIXTURE_MOVE_M + 1e-9 and (i or j)),
                     key=lambda o: (round(math.hypot(*o), 6), o))
    for dx, dy in offsets:
        c = (p.center[0] + dx, p.center[1] + dy)
        q = placer.Piece(p.type, c, p.rotation_deg, p.size, False)
        if _place_problem(b, room, q) is not None:
            continue
        poly = q.polygon()
        if any(poly.intersection(o).area > placer.AREA_EPS for o in others):
            continue
        return (round(c[0], 4), round(c[1], 4))
    return None


def _set_front(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    if item.get("front_deg") is not None:
        raise EditRejected("has_front", f"{item['id']} faces {float(item['front_deg']):.0f}° already: rotate_piece "
                                        f"turns it")
    front = float(args["front_deg"]) % 360.0
    rot = float(item["footprint"]["rotation_deg"])
    sides = sorted({round(G.normalise_angle(rot + 270.0 + 90.0 * k), 3) for k in range(4)})
    near = min(sides, key=lambda s: G.angle_difference_deg(s, front))
    if G.angle_difference_deg(near, front) > 1.0 + 1e-9:
        raise EditRejected("front_side", f"front {front:.1f}° is {G.angle_difference_deg(near, front):.1f}° off the "
                                         f"nearest side of the footprint (needs ≤ 1°): fronts "
                                         f"{', '.join(f'{s:.0f}' for s in sides)}")
    before = copy.deepcopy(item)
    new_rot, size = placer.front_frame(item["footprint"], near)
    _set_footprint(item, item["footprint"]["center"], new_rot, size, near)
    _label(item, before, args, ["footprint", "front_deg"])
    return [item["id"]]


def _relayout_m12(b: dict, args: dict) -> list[str]:
    """``relayout_room``: the room solved again (its added pieces replaced; drawn pieces fixed): solver candidate
    ``candidate`` (1-based, default 1) of the program with the ``choices`` (group id -> option)."""
    from wenart.furniture import program as PR

    room = _room(b, args["room_id"])
    choices = dict(args.get("choices") or {})
    prog = PR.room_program(b, room["id"], choices=choices)
    known = {g["group_id"]: g["options"] for g in prog["groups"]}
    for gid, option in choices.items():
        if gid not in known or option not in known[gid]:
            raise EditRejected("choices", f"{gid}: {option!r} is not an option of the room's program ("
                                          + "; ".join(f"{k}: {'/'.join(v)}" for k, v in known.items()) + ")")
    if not prog["groups"]:
        raise EditRejected("no_change", f"{room['id']}: the program has no groups ({prog['reason']})")
    old = _ai_floor_ids(b, room["id"])
    new = _solve_apply(b, room, prog, args, f"{room['id']} relayout", fixed=[], index=int(args.get("candidate") or 1))
    return old + new


M12_EDITS = {"place_group": _place_group, "complete_group": _complete_group, "move_group": _move_group,
             "retype_piece": _retype, "mark_not_furniture": _mark_not_furniture, "fix_fixture": _fix_fixture,
             "set_front": _set_front}


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
    if "group_id" in args:
        return str(args["group_id"]).split(".", 1)[0]
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
            changed = _relayout_m12(b, args)
        elif op == "set_room_type":
            changed = _set_room_type(b, args)
        else:
            changed = M12_EDITS[op](b, args)
    except EditRejected as exc:
        return _result(False, [f"{exc.check}: {exc.message}"], before_score["score"], before_score["score"], None, [],
                       rerun, exc.message)
    failed = _new_failures(before_checks, room_checks(b, room_id))
    after_score = PL.score_room(b, room_id)
    known = {(w["check"], w["target"], w["message"]) for w in before_score["violations"]}
    new = [v for v in after_score["violations"] if (v["check"], v["target"], v["message"]) not in known]
    notes = ""
    if op in GROUP_OPS:
        # A group placed by the solver: no new critical or major finding (the solver's own hard rule).
        bad = [v for v in new if v["severity"] in ("critical", "major")]
        if bad:
            failed.append("group checks: " + "; ".join(f"{v['check']} {v['target']}: {v['message']}" for v in bad[:4]))
    elif op in CORRECTION_OPS:
        notes = ("; new findings: " + "; ".join(f"{v['check']} {v['target']}: {v['message']}" for v in new[:4])
                 if new else "")
    # The score must not drop; it is compared before the floor at 0 (``penalty``), so a room far below 0 neither
    # hides a worse edit nor an improvement.
    elif after_score["penalty"] > before_score["penalty"]:
        failed.append(f"score: plausibility {100 - before_score['penalty']} -> {100 - after_score['penalty']} ("
                      + "; ".join(f"{v['check']} {v['target']}: {v['message']}" for v in new[:4]) + ")")
    out = _result(not failed, failed, before_score["score"], after_score["score"], None if failed else b, changed,
                  rerun, (f"{op} rejected: " + "; ".join(failed[:3])) if failed else
                  f"{op} accepted: score {100 - before_score['penalty']} -> {100 - after_score['penalty']}" + notes)
    out["penalty_before"], out["penalty_after"] = before_score["penalty"], after_score["penalty"]
    return out


# Milestone 12 contract (docs/milestone12.md §5.2, §5.3, §13.2; owner: track G).
def dry_run(building: dict, edit: dict, *, catalog=None) -> dict:
    """The validator's answer for ``edit`` without applying it: the ``apply_edit`` result with ``building`` None and
    ``dry_run: true`` (the loop does not count it against the try budget)."""
    res = apply_edit(building, edit, catalog=catalog)
    return dict(res, building=None, dry_run=True)


def allowed_edits(building: dict, piece_id: str) -> dict:
    """Per tool name: ``{"allowed": bool, "why": str, "move_left_m": float | None}`` for one piece (the room brief,
    docs/milestone12.md §5.2): what the validator would allow by the CLAUDE.md locks before any geometry check (an
    allowed edit can still fail its checks; ``dry_run`` tells). ``move_left_m``: how far the piece may still move
    from its drawn place (None: no limit, an added piece; 0: it may not move)."""
    item = next((f for f in building.get("furniture") or [] if f.get("id") == piece_id), None)
    if item is None:
        return {}
    room = next((r for r in building.get("rooms") or [] if r.get("id") == item.get("room_id")), None) or {}
    drawn, fixed = _drawn(item), _fixed(item)
    kept = drawn and bool(room) and kept_room(building, room)
    built = GR.piece_is_built(item)
    misplaced = fixed and schemas.misplaced_fixed(item["type"], room.get("room_type"))
    drawn_center = (item.get("drawn_footprint") or item["footprint"])["center"]
    moved = G.distance(item["footprint"]["center"], drawn_center)
    out: dict = {}

    def put(tool: str, ok: bool, why: str, left: Optional[float] = 0.0) -> None:
        out[tool] = {"allowed": bool(ok), "why": why, "move_left_m": None if left is None else round(max(0.0, left), 3)}

    adj = item.get("adjusted_by_ai") or {}
    limit = schemas.WALL_SNAP_MAX_M if adj.get("snapped_wall") else SNAP_MAX_M
    if not drawn:
        put("move_piece", True, "an added piece moves freely (checks decide)", None)
    elif fixed:
        put("move_piece", False, f"drawn fixed equipment ({item['type']}) never moves; fix_fixture moves it up to "
                                 f"{FIXTURE_MOVE_M} m when it stands through a wall or in a door swing")
    elif kept:
        put("move_piece", False, "the room keeps its drawn pieces: only orientation and clear errors")
    else:
        put("move_piece", moved < limit, f"a drawn piece moves at most {SNAP_MAX_M} m ({schemas.WALL_SNAP_MAX_M} m "
                                         f"when its back snaps onto a wall); moved {moved:.2f} m so far",
            limit - moved)
    if item["type"] in schemas.FRONTLESS_TYPES:
        put("rotate_piece", False, f"a {item['type']} has no front to turn")
    elif fixed:
        r = PL._Room(building, room) if room else None
        problem = _front_problem(r, item["id"]) if r is not None and item["id"] in r.pieces else None
        put("rotate_piece", problem is not None, f"fixed equipment turns only for a clear error: "
                                                 f"{problem or 'none here (its back is on a wall, its front free)'}")
    else:
        put("rotate_piece", True, "orientation may change (checks decide)")
    if fixed:
        put("resize_piece", False, "fixed equipment keeps its drawn size; fix_fixture gives a real product size when the "
                                   "drawn one is more than 30 % off")
    elif kept:
        put("resize_piece", False, "the room keeps its drawn pieces' sizes")
    else:
        put("resize_piece", item["type"] != "unknown", "to a real size of its type (size table)"
            if item["type"] != "unknown" else "an unknown piece is typed first (retype_piece)")
    if fixed and not misplaced:
        retype = (False, f"drawn fixed equipment keeps its type ({item['type']})")
    elif kept and item["type"] != "unknown":
        retype = (False, "the room keeps its drawn pieces' types (an unknown piece may be typed)")
    else:
        retype = (True, "a type of the room / zone that fits the footprint (size table)")
    put("retype_piece", *retype)
    put("change_type", *retype)
    put("swap_model", built, "a catalogue model of its type" if built else "the piece is not built")
    if drawn and fixed and not misplaced:
        put("remove_piece", False, "drawn fixed equipment is never removed (mark_not_furniture for a misread symbol)")
    elif drawn:
        put("remove_piece", item.get("build") is not False, "a drawn piece is left out (build: false) only with a "
                                                            "reason" if item.get("build") is not False else
            "not built already")
    else:
        put("remove_piece", True, "an added piece may be removed")
    marked = any(s.get("former_piece_id") == item["id"] for s in building.get("symbols") or [])
    put("mark_not_furniture", drawn and not marked, "a drawn piece read from a symbol, mark or line" if drawn and not
        marked else ("marked already" if marked else "only a drawn piece can be a misread symbol"))
    if fixed:
        probs = fixture_problems(building, item)
        fix = probs["size"] is not None or probs["place"] is not None
        why = "; ".join(x for x in (
            f"its size is {probs['size']['off'] * 100:.0f} % outside the real range" if probs["size"] else "",
            (f"it stands {probs['place']['outside_m2']:.2f} m² through a wall" if probs["place"]["outside_m2"] > 0.01
             else f"it stands in door {probs['place']['door']}") if probs["place"] else "") if x)
        put("fix_fixture", fix, why or "its size is real and it stands inside the room, off the doors",
            FIXTURE_MOVE_M - moved if probs["place"] else 0.0)
    else:
        put("fix_fixture", False, "only for drawn fixed equipment")
    put("set_front", item.get("front_deg") is None, "a drawn piece without a front gets one along a side of its "
        "footprint" if item.get("front_deg") is None else f"it faces {float(item['front_deg']):.0f}° already "
                                                          f"(rotate_piece)")
    group = next((g for g in GR.group_members(building, item["room_id"]) if item["id"] == g.get("anchor_id")
                  or item["id"] in (g.get("member_ids") or [])), None) if item.get("room_id") else None
    if group is None:
        put("complete_group", False, "the piece belongs to no group")
        put("move_group", False, "the piece belongs to no group")
    else:
        put("complete_group", bool(group.get("missing")), f"{group['group_id']} misses "
            f"{', '.join(group['missing'])}" if group.get("missing") else f"{group['group_id']}: nothing missing")
        members = [f for f in building["furniture"] if f["id"] in [group.get("anchor_id")] + list(group["member_ids"])]
        ai = all(f.get("source") == "added_by_ai" for f in members)
        put("move_group", ai, f"{group['group_id']}: added pieces, moved as one" if ai else
            f"{group['group_id']} holds drawn pieces: they stay where they are drawn", None if ai else 0.0)
    return out
