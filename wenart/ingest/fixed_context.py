"""Drawn fixed equipment read in the context of its room (27 Nov 2026, audit fix round 5a, rule R18).

What: ``kitchen_context(b)`` runs after the furniture types are inferred: kitchen kit (a counter run, a hob, a kitchen
sink, a hood, a dishwasher) belongs to a kitchen, a kitchen-living room, a living room with a kitchen part or a utility
room. A piece the reading typed so (by its shape or a vision pass, never by its block or name text) in a bedroom, a
hall or a dressing room is read again: a run ``WARDROBE_DEPTH_M`` deep along a wall is a wardrobe (``adjusted_by_ai``
by code, ``drawn_type`` and the drawn footprint kept); any other kitchen piece there is listed for review
(``needs_review``), never built as kitchen kit in a bedroom.

Why: real10's bedrooms and halls got kitchen counters and hoods from wardrobe runs drawn 0.6 m deep along a wall.

How: pure on the building JSON; the room's type, its label words ('MUTFAK', 'KITCHEN', 'AÇIK MUTFAK') and the piece's
footprint against the room's outline.
"""
from __future__ import annotations

import copy
import math
import re
from typing import Optional

KITCHEN_KIT = ("kitchen_counter", "stove", "sink_kitchen", "hood", "dishwasher", "kitchen_island")
NOT_KITCHEN_TYPES = ("bedroom", "hall")
STRONG_METHODS = ("block_name", "name_text", "zone_label", "block")
WARDROBE_DEPTH_M = (0.50, 0.70)
WALL_REACH_M = 0.15             # a run's back this close to the room's outline stands on a wall
KITCHEN_WORD_RE = re.compile(r"(?<![a-z])(?:mutfak|kitchen|kitchenette|kuche|cuisine|cocina|aksam\s+mutfagi|"
                             r"camasir|utility|laundry|kiler|pantry)")
DRESSING_RE = re.compile(r"(?<![a-z])(?:soyunma|giyinme|dressing|walk\s*-?\s*in|vestiyer)(?![a-z])")


def _fold(text) -> str:
    from wenart import building as B
    return " ".join(B.fold_ascii(str(text or "")).lower().split())


def not_a_kitchen(room: Optional[dict]) -> Optional[str]:
    """Why the room holds no kitchen kit (a bedroom, a hall, a dressing room with no kitchen word), or None (pure)."""
    if not room:
        return None
    words = _fold(f"{room.get('label_raw') or ''} {room.get('label') or ''}")
    if KITCHEN_WORD_RE.search(words):
        return None
    if DRESSING_RE.search(words):
        return "a dressing room"
    if room.get("room_type") in NOT_KITCHEN_TYPES:
        return f"a {room.get('room_type')}"
    return None


def _against_wall(piece: dict, room: dict) -> bool:
    from wenart.ingest import completion as CP

    p = CP._poly(room.get("polygon"))
    fp = piece.get("footprint") or {}
    if p is None or not fp.get("center") or not fp.get("size"):
        return False
    w, d = float(fp["size"][0]), float(fp["size"][1])
    r = math.radians(float(fp.get("rotation_deg") or 0.0))
    ux, uy = math.cos(r), math.sin(r)
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    long_ = (ux, uy) if w >= d else (-uy, ux)
    short = (-long_[1], long_[0])
    half_d = min(w, d) / 2.0
    from shapely.geometry import Point
    ring = p.exterior
    return any(ring.distance(Point(cx + s * short[0] * half_d, cy + s * short[1] * half_d)) <= WALL_REACH_M
               for s in (1, -1))


def kitchen_context(b: dict) -> list[dict]:
    """The kitchen kit out of its context (module docstring), in place; one record per piece changed or listed."""
    rooms = {r.get("id"): r for r in b.get("rooms") or []}
    out = []
    for f in b.get("furniture") or []:
        if f.get("type") not in KITCHEN_KIT or f.get("source") != "from_documents" or f.get("build") is False:
            continue
        if str(f.get("type_method") or "") in STRONG_METHODS:
            continue                              # a block or a name says kitchen: the drawing's word stands
        room = rooms.get(f.get("room_id"))
        why_not = not_a_kitchen(room)
        if why_not is None:
            continue
        fp = f.get("footprint") or {}
        size = sorted(float(v) for v in fp.get("size") or [0, 0])
        if f.get("type") == "kitchen_counter" and WARDROBE_DEPTH_M[0] <= size[0] <= WARDROBE_DEPTH_M[1] \
                and size[1] >= 0.8 and _against_wall(f, room):
            reason = (f"{f['id']}: a {size[1]:.2f} x {size[0]:.2f} m run along a wall of {room['id']} "
                      f"'{room.get('label')}' ({why_not}, no kitchen there): a wardrobe, not a kitchen counter (R18)")
            f.setdefault("drawn_type", f.get("type"))
            f.setdefault("drawn_footprint", copy.deepcopy(fp))
            f.setdefault("drawn_front_deg", f.get("front_deg"))
            f["type"] = "wardrobe"
            f["adjusted_by_ai"] = {"by": "code", "rule": "kitchen_context", "reason": reason,
                                   "changed": {"type": f["drawn_type"]}}
            out.append({"piece": f["id"], "room": room["id"], "type": "wardrobe", "reason": reason})
        else:
            reason = (f"{f['id']}: typed {f.get('type')} in {room['id']} '{room.get('label')}' ({why_not}): kitchen "
                      f"kit only in a kitchen; listed for review (R18)")
            f["needs_review_reason"] = reason
            b.setdefault("needs_review", []).append({"id": f["id"], "reason": reason, "kind": "kitchen_context"})
            out.append({"piece": f["id"], "room": room["id"], "type": f.get("type"), "reason": reason,
                        "review": True})
    return out
