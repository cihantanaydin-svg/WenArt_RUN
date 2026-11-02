"""One doorway measure for the code critic and the architect (2 Nov 2026, house score item 6b, rule B).

What: ``door_measures(building, room)``: every door and doorless opening of a room (``placer.room_context``'s doors) as
the code critic's F7 and R3 judge it: the floor pieces on the door's ``placer.DOOR_APPROACH_M`` approach strip over
``AREA_MIN_M2`` (F7), in the leaf's half disc and in each hinge's quarter disc (R3), the blockers. The critic
(``plausibility``), the architect's F2 (``architect_rules``) and its ``move_piece`` (``architect_actions``) all read it,
so the two never disagree (real04 run 20261101-093151: F2's 25 % of a 0.8 m box let a 0.05 m move pass while F7 still
found the piece on the strip, and the audit's Y2 raised a critical).

Why a module of its own: the Blender build imports the architect's rules; ``plausibility`` reaches the drawing
readers and the furniture fit through its lazy imports, which do not belong in the build. This module needs the
geometry, the placer and the schemas only (all in the build's fingerprint, ``build.FINGERPRINT_CODE``).
"""
from __future__ import annotations

from wenart.furniture import placer, schemas

AREA_MIN_M2 = 0.01               # = plausibility.AREA_MIN_M2: intersections below this are touching
NOT_BUILT_ASSET_METHODS: tuple[str, ...] = ("none",)   # = groups.NOT_BUILT_ASSET_METHODS: a library gap, not built


def door_pieces(building: dict, room: dict) -> tuple[list[str], list, list, set]:
    """``(ids, pieces, polys, hosted)`` of a room's floor pieces as F6 / F7 / R3 judge them (= ``plausibility._Room``'s
    floor): built (not ``build: false``, not a library gap), typed, standing on the floor; ``hosted``: a module built
    into a counter of the room (its host's finding covers the door)."""
    items = [f for f in building.get("furniture") or [] if f.get("room_id") == room["id"]]
    built = [f for f in items if f.get("build") is not False and (
        not isinstance(f.get("asset"), dict) or f["asset"].get("method") not in NOT_BUILT_ASSET_METHODS)]
    pieces: dict = {}
    for i, f in enumerate(built):
        try:
            pieces[f["id"]] = placer.drawn_piece(f, i)
        except (KeyError, TypeError, ValueError):
            continue
    floor = [f for f in built if f["id"] in pieces and f["type"] != "unknown" and not schemas.off_floor(f)]
    ids = [f["id"] for f in floor]
    hosted = {f["id"] for f in floor if f.get("built_into") in set(ids)}
    return ids, [pieces[pid] for pid in ids], [pieces[pid].polygon() for pid in ids], hosted


def door_measure(door, ids: list[str], pieces: list, polys: list, hosted: set) -> dict:
    """One doorway (the module docstring). ``approach``: ``{piece id: area m2}`` on the approach strip over
    ``AREA_MIN_M2`` (F7, critical); ``swing``: the pieces in the leaf's half disc (R3); ``per_hinge``: the pieces in
    each hinge's quarter disc (only when the swing is hit); ``free_hinge``: a hinge side the leaf can use, None when
    none is free (R3 critical); ``blockers``: the pieces F7 or a critical R3 name, the largest approach area first;
    ``blocked``: any. A stair (entered through its opening) and a hosted module are never judged."""
    judged = [(pid, poly) for pid, p, poly in zip(ids, pieces, polys) if p.type != "stair" and pid not in hosted]
    approach = {}
    for pid, poly in judged:
        area = poly.intersection(door.zone).area
        if area > AREA_MIN_M2:
            approach[pid] = area
    swing, per_hinge = [], []
    if door.swing is not None and not door.swing.is_empty:
        swing = [pid for pid, poly in judged if poly.intersection(door.swing).area > AREA_MIN_M2]
        if swing:
            # M11 (pod G1, synthetic-01): no drawing gives the hinge side, and the half disc covers both
            per_hinge = [[pid for pid, poly in judged if poly.intersection(q).area > AREA_MIN_M2]
                         for q in door.hinge_swings()]
    free = [i for i, h in enumerate(per_hinge) if not h]
    free_hinge = free[0] if per_hinge and free else None
    swing_blocked = bool(swing) and free_hinge is None
    blockers = sorted(approach, key=lambda k: (-approach[k], str(k)))
    blockers += [pid for pid in swing if swing_blocked and pid not in approach]
    return {"door": door.id, "approach": approach, "approach_m": placer.DOOR_APPROACH_M, "area_min_m2": AREA_MIN_M2,
            "swing": swing, "per_hinge": per_hinge, "free_hinge": free_hinge, "swing_blocked": swing_blocked,
            "blockers": blockers, "blocked": bool(blockers)}


def door_measures(building: dict, room: dict) -> list[dict]:
    """``door_measure`` of every door and doorless opening of ``room``, in ``placer.room_context``'s order."""
    ctx = placer.room_context(building, room, walkways=False)      # the door zones only: the walkways are G11's
    ids, pieces, polys, hosted = door_pieces(building, room)
    return [door_measure(door, ids, pieces, polys, hosted) for door in ctx.doors]
