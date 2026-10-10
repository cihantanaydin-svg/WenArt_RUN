"""The locked check of drawn furniture (docs/milestone10.md §1.7, §2.2, §2.7).

What: ``check(source, final, mode)`` compares every drawn piece
(``source: from_documents``) of the source building JSON with the final one
and returns one readable line per violation (an empty list = pass);
``anchor_of(piece, building)`` gives a drawn piece's locked location.

Why: with ``furnished_rooms: complete`` the AI may change a drawn piece's
type, size, height and look, but its location and position are locked
(CLAUDE.md furniture rules). This check is the guard after ``layout`` and
after ``refit``: a violation fails the stage, nothing is silently moved.

How, mode ``complete`` (per drawn piece):

- present in the final building (never removed), same ``level_id`` and
  ``room_id``, ``source: from_documents`` kept; no final piece claims
  ``from_documents`` without being in the source;
- fixed equipment (``schemas.FIXED_TYPES``), pieces that are not built
  (``build: false``) and the other types that never change
  (``schemas.UNCHANGEABLE_TYPES``): type and footprint byte-equal;
- an unverified drawn piece stays ``unverified`` with its drawn footprint;
  only an agreed type proposal may change its type (and the type's height):
  ``type_proposal: true`` with ``drawn_type`` = the source type, no
  ``modified_by_ai`` (§1.6b row 15);
- every other piece: the anchor within ``ANCHOR_TOL_M`` (5 cm: the footprint
  centre of a free piece, the back-edge midpoint of a piece against a wall),
  the same wall, ``front_deg`` within ``FRONT_TOL_DEG`` (1 degree); a changed
  type, footprint or height needs ``modified_by_ai: true`` and the drawn
  values (``drawn_type``, ``drawn_footprint``, ``drawn_height``) equal to the
  source's;
- walls, openings and rooms byte-equal.

Milestone 11 (docs/milestone11.md §5): a drawn piece the agent changed through ``edit_ops.apply_edit`` carries
``adjusted_by_ai`` (with its reason) and is checked by ``_agent_problems`` instead: the drawn values kept for what
changed (``drawn_type``, ``drawn_footprint``, ``drawn_front_deg``); fixed equipment and kept rooms only turned (and
in a kept room an unknown piece typed, a piece not built); other drawn furniture moved at most 0.3 m.

Mode ``keep`` (and every room in ``keep_rooms``): the old byte rule, the
fit's ``FROZEN_KEYS`` (``KEEP_KEYS``) equal for every drawn piece. Anchors: a piece whose
back edge (the edge opposite its ``front_deg``; its three points: both ends
and the middle) each lie within ``placer.WALL_TOUCH_M`` (5 cm) of the
level's walls or the room outline has a ``back_edge`` anchor at the edge's
midpoint; its ``wall_id`` is the wall within 5 cm of that midpoint (null when
no wall is drawn there), so an end over an unwalled stretch never changes it
(code review #19); every other piece, and any piece without a front, has a
``centre`` anchor.
"""
from __future__ import annotations

import json
from typing import Iterable, Optional

from shapely.geometry import Point, Polygon

from wenart import geometry as G
from wenart.furniture import placer, schemas

ANCHOR_TOL_M = 0.05
FRONT_TOL_DEG = 1.0
MODES = ("complete", "keep")
BYTE_EQUAL_BLOCKS = ("walls", "openings", "rooms")


def _dump(value) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


def _back_edge(piece: dict) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    """(left end, midpoint, right end) of the back edge in the frame of the piece's front."""
    rot, size = placer.front_frame(piece["footprint"], piece.get("front_deg"))
    c = (float(piece["footprint"]["center"][0]), float(piece["footprint"]["center"][1]))
    w, d = size[0] / 2.0, size[1] / 2.0
    a = G.rotate_point((c[0] - w, c[1] + d), rot, c)
    b = G.rotate_point((c[0] + w, c[1] + d), rot, c)
    return a, placer.back_edge_midpoint(c, rot, size), b


def _wall_shapes(building: dict, level_id: str) -> list[tuple[str, Polygon]]:
    out = []
    for w in building.get("walls", []):
        if w.get("level_id") != level_id:
            continue
        if G.distance(w["start"], w["end"]) < 1e-6:
            continue
        thickness = float(w.get("thickness") or placer.DEFAULT_WALL_THICKNESS_M)
        out.append((w["id"], Polygon(G.centerline_to_rectangle(w["start"], w["end"], thickness))))
    return out


def anchor_of(piece: dict, building: dict) -> dict:
    """``{"kind": "centre" | "back_edge", "point": [x, y], "wall_id": str | None}`` (see the module docstring)."""
    fp = piece["footprint"]
    centre = {"kind": "centre", "point": [round(float(fp["center"][0]), 4), round(float(fp["center"][1]), 4)],
              "wall_id": None}
    if piece.get("front_deg") is None:
        return centre
    a, mid, b = _back_edge(piece)
    points = [Point(a), Point(mid), Point(b)]
    tol = placer.WALL_TOUCH_M + 1e-9
    walls = _wall_shapes(building, piece.get("level_id"))
    shapes = [shape for _id, shape in walls]
    room = next((r for r in building.get("rooms", []) if r["id"] == piece.get("room_id")), None)
    if room is not None and len(room.get("polygon") or []) >= 3:
        shapes.append(Polygon(room["polygon"]).exterior)
    if not shapes or not all(min(sh.distance(p) for sh in shapes) <= tol for p in points):
        return centre
    # Against a wall or the room outline at all three points; the wall is the one at the back edge's midpoint
    # (code review #19: an end over an unwalled stretch does not change it while the midpoint stays put).
    wall_id = None
    if walls:
        near_id, near = min(walls, key=lambda ws: (round(ws[1].distance(points[1]), 6), ws[0]))
        wall_id = near_id if near.distance(points[1]) <= tol else None
    return {"kind": "back_edge", "point": [round(mid[0], 4), round(mid[1], 4)], "wall_id": wall_id}


# keep mode: the fit's own guard keys (``wenart.furniture.fit.FROZEN_KEYS``; a copy, so the layout stage does not
# import the fit, the catalogue and the asset code; tests/test_locked.py checks that both stay equal).
KEEP_KEYS: tuple[str, ...] = ("id", "level_id", "room_id", "type", "type_raw", "source", "footprint", "front_deg",
                              "height", "status", "evidence", "build")


def _front_ok(a: Optional[float], b: Optional[float]) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return G.angle_difference_deg(float(a), float(b)) <= FRONT_TOL_DEG + 1e-9


# Milestone 11 (pod G2b): the agent's set_room_type changes a room's type with a reason (``adjusted_by_ai``);
# the room's geometry and every other field stay as drawn.
AGENT_ROOM_KEYS = ("room_type", "adjusted_by_ai", "inferred")


def _agent_retyped(room: Optional[dict]) -> bool:
    """True when the agent changed only the room's type, with a reason (``adjusted_by_ai.changed`` names only
    ``AGENT_ROOM_KEYS``)."""
    adj = (room or {}).get("adjusted_by_ai")
    return (isinstance(adj, dict) and bool(str(adj.get("reason") or "").strip())
            and not set(adj.get("changed") or {}) - set(AGENT_ROOM_KEYS))


def _without_agent_keys(room: dict) -> dict:
    return {k: v for k, v in room.items() if k not in AGENT_ROOM_KEYS}


def _block_problems(source: dict, final: dict) -> list[str]:
    out = []
    for key in BYTE_EQUAL_BLOCKS:
        before = {e.get("id"): _dump(e) for e in source.get(key) or []}
        after = {e.get("id"): _dump(e) for e in final.get(key) or []}
        if key == "rooms":                     # a reasoned room type change of the agent (set_room_type)
            src_rooms = {e.get("id"): e for e in source.get(key) or []}
            for e in final.get(key) or []:
                if _agent_retyped(e) and e.get("id") in src_rooms:
                    before[e["id"]] = _dump(_without_agent_keys(src_rooms[e["id"]]))
                    after[e["id"]] = _dump(_without_agent_keys(e))
        if before == after:
            continue
        changed = sorted(i for i in before.keys() & after.keys() if before[i] != after[i])
        gone = sorted(set(before) - set(after))
        new = sorted(set(after) - set(before))
        parts = [f"changed {', '.join(map(str, changed))}" if changed else "",
                 f"removed {', '.join(map(str, gone))}" if gone else "",
                 f"added {', '.join(map(str, new))}" if new else ""]
        out.append(f"{key}: must stay as drawn (byte-equal): " + "; ".join(p for p in parts if p))
    return out


def _changed_piece_problems(src: dict, fin: dict, source: dict, final: dict) -> list[str]:
    pid = src["id"]
    out = []
    anchor = anchor_of(src, source)
    if anchor["kind"] == "back_edge":
        point = _back_edge(fin)[1]
    else:
        point = (float(fin["footprint"]["center"][0]), float(fin["footprint"]["center"][1]))
    moved = G.distance(point, anchor["point"])
    if moved > ANCHOR_TOL_M + 1e-6:
        out.append(f"{pid}: anchor ({anchor['kind']}) moved {moved:.3f} m (> {ANCHOR_TOL_M} m)")
    if anchor["kind"] == "back_edge":
        now = anchor_of(fin, final)
        if now["kind"] != "back_edge" or now["wall_id"] != anchor["wall_id"]:
            out.append(f"{pid}: no longer against wall {anchor['wall_id']} (now {now['kind']} "
                       f"{now.get('wall_id')})")
    if not _front_ok(src.get("front_deg"), fin.get("front_deg")):
        out.append(f"{pid}: front {src.get('front_deg')} -> {fin.get('front_deg')} (more than {FRONT_TOL_DEG} deg)")
    changed = (src["type"] != fin["type"] or _dump(src["footprint"]) != _dump(fin["footprint"])
               or src.get("height") != fin.get("height"))
    proposal = (fin.get("type_proposal") is True and src.get("status") == "unverified"
                and _dump(src["footprint"]) == _dump(fin["footprint"]))
    if changed and proposal and fin.get("modified_by_ai") is not True:
        if fin.get("drawn_type") != src["type"]:
            out.append(f"{pid}: type proposal without the drawn type ({fin.get('drawn_type')} != {src['type']})")
    elif changed:
        if fin.get("modified_by_ai") is not True:
            out.append(f"{pid}: type, footprint or height changed without modified_by_ai")
        elif (fin.get("drawn_type") != src["type"] or _dump(fin.get("drawn_footprint")) != _dump(src["footprint"])
              or fin.get("drawn_height") != src.get("height")):
            out.append(f"{pid}: drawn_type / drawn_footprint / drawn_height do not hold the drawn values")
    return out


AGENT_SNAP_M = 0.3               # Milestone 11 (§5): a drawn piece adjusted by the agent moves at most this far


def _agent_problems(src: dict, fin: dict, keep: bool) -> list[str]:
    """Milestone 11 (docs/milestone11.md §5, CLAUDE.md furniture rules): a drawn piece the agent changed
    (``adjusted_by_ai`` with its reason, ``wenart.furniture.edit_ops``). Fixed equipment and pieces that never change:
    only the orientation (type, centre and size as drawn). Kept rooms (``keep``): only the orientation, an unknown
    piece's type and ``build: false``. Other drawn furniture: the centre within ``AGENT_SNAP_M``. Always: the drawn
    values kept (``drawn_type``, ``drawn_footprint``, ``drawn_front_deg``) for what changed."""
    pid = src["id"]
    out = []
    adj = fin.get("adjusted_by_ai")
    if not isinstance(adj, dict) or not str(adj.get("reason") or "").strip():
        return [f"{pid}: adjusted_by_ai without a reason"]
    sfp, ffp = src["footprint"], fin["footprint"]
    moved = G.distance(sfp["center"], ffp["center"])
    same_box = sorted(round(float(v), 3) for v in sfp["size"]) == sorted(round(float(v), 3) for v in ffp["size"])
    if src["type"] != fin["type"] and fin.get("drawn_type") != src["type"]:
        out.append(f"{pid}: type changed without the drawn type ({fin.get('drawn_type')} != {src['type']})")
    if _dump(sfp) != _dump(ffp) and _dump(fin.get("drawn_footprint")) != _dump(sfp):
        out.append(f"{pid}: footprint changed without the drawn footprint")
    if not _front_ok(src.get("front_deg"), fin.get("front_deg")) and "drawn_front_deg" in fin \
            and not _front_ok(fin.get("drawn_front_deg"), src.get("front_deg")):
        out.append(f"{pid}: drawn_front_deg {fin.get('drawn_front_deg')} != the drawn front {src.get('front_deg')}")
    elif not _front_ok(src.get("front_deg"), fin.get("front_deg")) and "drawn_front_deg" not in fin:
        out.append(f"{pid}: front changed without drawn_front_deg")
    # Pod G2 (real02): the fixed equipment of CLAUDE.md is schemas.FIXED_TYPES, as in edit_ops; the other
    # UNCHANGEABLE_TYPES (documented-only and rule-only types, e.g. a floor lamp) keep their type but move like
    # other drawn furniture (the refit refused a validated 0.3 m floor lamp move and rolled the round back).
    # Pod G2c: a drawn ``unknown`` that was not built (a detail or an unclear symbol) may be typed by the agent (CLAUDE.md:
    # "never an unexplained box"), as edit_ops allows; other not-built pieces stay as they are.
    fixed = src["type"] in schemas.FIXED_TYPES or (src.get("build") is False and src["type"] != "unknown")
    if src["type"] in schemas.UNCHANGEABLE_TYPES and not fixed and src["type"] != fin["type"] and not keep:
        out.append(f"{pid}: {src['type']} changed its type (no room type lists a type to change it into)")
    if fixed or keep:
        if src["type"] != fin["type"] and not (keep and not fixed and src["type"] == "unknown"):
            out.append(f"{pid}: {'fixed equipment' if fixed else 'a kept drawn piece'} changed its type")
        if moved > 1e-3 or not same_box:
            out.append(f"{pid}: {'fixed equipment' if fixed else 'a kept drawn piece'} moved or resized (only the "
                       f"orientation may change)")
        if fixed and fin.get("build") is False and src.get("build") is not False:
            out.append(f"{pid}: fixed equipment removed")
    elif moved > (schemas.WALL_SNAP_MAX_M if adj.get("snapped_wall") else AGENT_SNAP_M) + 1e-6:
        limit = schemas.WALL_SNAP_MAX_M if adj.get("snapped_wall") else AGENT_SNAP_M
        out.append(f"{pid}: moved {moved:.3f} m by the agent (> {limit} m)")
    return out


def keep_rooms_of(completion: Optional[dict]) -> list[str]:
    """The rooms the layout kept as drawn (``completion.json`` rooms with ``state: kept``: ``furnished_rooms_keep``
    and partners of kept rooms), for ``check(..., keep_rooms=...)`` after a later stage (refit)."""
    return [r["room_id"] for r in (completion or {}).get("rooms", []) if r.get("state") == "kept"]


def mode_of(completion: Optional[dict]) -> str:
    """``keep`` or ``complete`` from ``completion.json`` (``complete`` when it is missing: the default)."""
    value = ((completion or {}).get("settings") or {}).get("furnished_rooms", "complete")
    return "keep" if value == "keep" else "complete"


def check(source: dict, final: dict, mode: str, keep_rooms: Optional[Iterable[str]] = None) -> list[str]:
    """Violations of the locked rules (see the module docstring); ``keep_rooms``: room ids that stay ``keep``
    in ``complete`` mode (``furnished_rooms_keep``)."""
    if mode not in MODES:
        raise ValueError(f"locked.check: mode must be one of {MODES}, got {mode!r}")
    keep = set(keep_rooms or ())
    out = _block_problems(source, final)
    source_ids = {f["id"] for f in source.get("furniture", [])}
    final_by_id = {f["id"]: f for f in final.get("furniture", [])}
    for f in final.get("furniture", []):
        if f.get("source") == "from_documents" and f["id"] not in source_ids:
            out.append(f"{f['id']}: labelled from_documents but not in the source building")
    frozen = KEEP_KEYS
    for src in source.get("furniture", []):
        if src.get("source") != "from_documents":
            continue
        pid = src["id"]
        fin = final_by_id.get(pid)
        if fin is None:
            out.append(f"{pid}: drawn {src['type']} removed")
            continue
        if fin.get("source") != "from_documents":
            out.append(f"{pid}: source changed to {fin.get('source')!r} (must stay from_documents)")
        for key in ("level_id", "room_id"):
            if fin.get(key) != src.get(key):
                out.append(f"{pid}: {key} {src.get(key)} -> {fin.get(key)}")
        if fin.get("adjusted_by_ai") is not None:
            # Milestone 11: the agent's validated edit (edit_ops) is checked by the M11 rules, not the M10 anchor.
            kept = mode == "keep" or src.get("room_id") in keep
            out.extend(_agent_problems(src, fin, kept))
            if kept:
                free = {"footprint", "front_deg", "build", "type", "evidence", "height"}
                bad = [k for k in frozen if k not in free and _dump(src.get(k)) != _dump(fin.get(k))]
                if bad:
                    out.append(f"{pid}: changed {', '.join(bad)} (keep: drawn pieces stay byte-equal)")
            continue
        if mode == "keep" or src.get("room_id") in keep:
            bad = [k for k in frozen if _dump(src.get(k)) != _dump(fin.get(k))]
            if bad:
                out.append(f"{pid}: changed {', '.join(bad)} (keep: drawn pieces stay byte-equal)")
            continue
        if (src["type"] in schemas.UNCHANGEABLE_TYPES or src.get("build") is False):
            bad = [k for k in ("type", "footprint") if _dump(src.get(k)) != _dump(fin.get(k))]
            if bad:
                what = "fixed equipment" if src["type"] in schemas.FIXED_TYPES else "drawn piece that never changes"
                out.append(f"{pid}: {what} changed {', '.join(bad)} (must stay byte-equal)")
            continue
        if src.get("status") == "unverified":
            if fin.get("status") != "unverified":
                out.append(f"{pid}: unverified drawn piece became {fin.get('status')}")
            if _dump(src["footprint"]) != _dump(fin["footprint"]):
                out.append(f"{pid}: unverified drawn piece changed its footprint")
        out.extend(_changed_piece_problems(src, fin, source, final))
    return out
