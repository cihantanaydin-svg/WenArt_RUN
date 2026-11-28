"""Drawn fixed equipment read in the context of its room (27 Nov 2026, audit fix round 5a, rule R18).

What: ``kitchen_context(b)`` runs after the furniture types are inferred and judges each room's kitchen kit as a whole
(28 Nov 2026, round 5a fix-up FIX-1/FIX-2/GENERAL-8): kitchen kit (a counter run, a hob, a kitchen sink, a hood, a
dishwasher) belongs to a kitchen, a kitchen-living room, a living room with a kitchen part or a utility room. A room is
read again only when it is typed bedroom, or labelled a hall or a dressing room by a drawn text (never a face that got
the hall type from its door count, never a role name), carries no kitchen word ('MUTFAK', 'MUTFAĞI', 'MUTF.', 'MTF',
'KITCHEN', 'AÇIK MUTFAK') and holds no kitchen sink, no hob and no kitchen zone a text names: a counter run with a sink
or a hob on it is a kitchen, never a wardrobe. In such a room a piece the reading typed as kitchen kit by its shape or a
vision pass (never by its block or name text) is read again: a run ``WARDROBE_DEPTH_M`` deep along a wall is a wardrobe
(``adjusted_by_ai`` by code merged into any earlier record, ``drawn_*`` kept, an evidence entry, ``type_method``
inferred); any other kitchen piece there is not built (``not_built_reason``, ``needs_review`` with its plan crop: FIX-3).
The room's kitchen zone the reading made from those pieces is dropped, or keeps the pieces left (FIX-1: a bedroom never
plans a kitchen run for a counter that became a wardrobe).

Why: real10's bedrooms and halls got kitchen counters and hoods from wardrobe runs drawn 0.6 m deep along a wall.

How: pure on the building JSON; the room's type, its label words, its pieces and the piece's footprint against the
room's outline.
"""
from __future__ import annotations

import copy
import math
import re
from typing import Optional

KITCHEN_KIT = ("kitchen_counter", "stove", "sink_kitchen", "hood", "dishwasher", "kitchen_island")
KITCHEN_PROOF = ("sink_kitchen", "stove", "oven", "cooktop")    # a run with one of these is a kitchen (any method)
NOT_KITCHEN_TYPES = ("bedroom",)
LABELLED_TYPES = ("hall",)      # ... and these only when a drawn label names them (never a door count's hall)
STRONG_METHODS = ("block_name", "name_text", "zone_label", "block")
WARDROBE_DEPTH_M = (0.50, 0.70)
WALL_REACH_M = 0.15             # a run's back this close to the room's outline stands on a wall
KITCHEN_WORD_RE = re.compile(r"(?<![a-z])(?:mutfa[kg]\w*|mutf\.?|mtf\.?|kitchen\w*|kuche|cuisine|cocina|"
                             r"camasir\w*|utility|laundry|kiler\w*|pantry)(?![a-z])")
DRESSING_RE = re.compile(r"(?<![a-z])(?:soyunma|giyinme|dressing|walk\s*-?\s*in\s+(?:closet|wardrobe))(?![a-z])")
RULE = "kitchen_context"


def _fold(text) -> str:
    from wenart.textfold import fold_ascii
    return " ".join(fold_ascii(str(text or "")).lower().split())


def not_a_kitchen(room: Optional[dict]) -> Optional[str]:
    """Why the room holds no kitchen kit by its type and words (a bedroom; a hall or a dressing room a drawn label
    names; no kitchen word), or None (pure)."""
    if not room:
        return None
    drawn = "" if room.get("label_role") else str(room.get("label_raw") or "")
    words = _fold(f"{drawn} {'' if room.get('label_role') else room.get('label') or ''}")
    if KITCHEN_WORD_RE.search(words):
        return None
    if drawn and DRESSING_RE.search(words):
        return "a dressing room"
    if room.get("room_type") in NOT_KITCHEN_TYPES:
        return f"a {room.get('room_type')}"
    if room.get("room_type") in LABELLED_TYPES and drawn.strip():
        return f"a {room.get('room_type')} its label names"
    return None


def kitchen_proof(b: dict, room: dict) -> Optional[str]:
    """What in the room says kitchen whatever its type (pure): a kitchen sink or a hob (any method), or a kitchen zone a
    text names (not the one the reading makes from the pieces themselves)."""
    from wenart.ingest.generic import reading as RDG

    for f in b.get("furniture") or []:
        if f.get("room_id") == room.get("id") and f.get("type") in KITCHEN_PROOF and f.get("build") is not False:
            return f"its {f['type'].replace('_', ' ')} {f['id']}"
    for z in room.get("zones") or []:
        if z.get("kind") != "kitchen":
            continue
        rules = {str((e or {}).get("rule") or "") for e in z.get("evidence") or [] if isinstance(e, dict)}
        if rules - {RDG.ZONE_RULE, ""}:
            return f"its kitchen zone {z.get('zone_id')}"
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


def _label(f: dict, reason: str, changed: dict) -> None:
    from wenart.furniture import infer as IF

    crop = IF._crop_of(f)
    lab = {"by": "code", "rule": RULE, "reason": reason, "changed": changed}
    if crop:
        lab["crop"] = crop
    IF.merge_code_label(f, lab)
    ev = f.setdefault("evidence", [])
    if isinstance(ev, list):
        ev.append({"file": "building.json", "method": "inferred", "confidence": 0.7, "rule": RULE, "note": reason})


def kitchen_context(b: dict) -> list[dict]:
    """The kitchen kit out of its context (module docstring), in place; one record per piece changed or not built and
    per kitchen zone dropped."""
    out = []
    by_room: dict = {}
    for f in b.get("furniture") or []:
        if f.get("type") in KITCHEN_KIT and f.get("source") == "from_documents" and f.get("build") is not False:
            by_room.setdefault(f.get("room_id"), []).append(f)
    rooms = {r.get("id"): r for r in b.get("rooms") or []}
    for rid, kit in sorted(by_room.items(), key=lambda x: str(x[0])):
        room = rooms.get(rid)
        why_not = not_a_kitchen(room)
        if why_not is None or kitchen_proof(b, room) is not None:
            continue                              # a kitchen word, a sink or a hob: the run is a kitchen (GENERAL-8)
        gone = set()
        for f in kit:
            if str(f.get("type_method") or "") in STRONG_METHODS:
                continue                          # a block or a name says kitchen: the drawing's word stands
            fp = f.get("footprint") or {}
            size = sorted(float(v) for v in fp.get("size") or [0, 0])
            drawn = f.get("type")
            f.setdefault("drawn_type", drawn)
            f.setdefault("drawn_footprint", copy.deepcopy(fp))
            f.setdefault("drawn_front_deg", f.get("front_deg"))
            f.setdefault("drawn_height", f.get("height"))
            if drawn == "kitchen_counter" and WARDROBE_DEPTH_M[0] <= size[0] <= WARDROBE_DEPTH_M[1] \
                    and size[1] >= 0.8 and _against_wall(f, room):
                reason = (f"{f['id']}: a {size[1]:.2f} x {size[0]:.2f} m run along a wall of {room['id']} "
                          f"'{room.get('label')}' ({why_not}, no kitchen word, no sink or hob there): a wardrobe, not a "
                          f"kitchen counter (R18)")
                method = f.get("type_method")
                f["type"] = "wardrobe"
                f["type_method"] = "inferred"             # FIX-4: code retyped it (the label names the rule)
                _label(f, reason, {"type": drawn, "type_method": method})
                out.append({"piece": f["id"], "room": room["id"], "type": "wardrobe", "reason": reason})
            else:
                reason = (f"{f['id']}: typed {drawn} in {room['id']} '{room.get('label')}' ({why_not}, no kitchen word, "
                          f"no sink or hob there): kitchen kit only in a kitchen; not built, listed for review (R18)")
                f.update(build=False, not_built_reason=reason)
                _label(f, reason, {"build": True})
                from wenart.furniture import infer as IF
                b.setdefault("needs_review", []).append({"id": f["id"], "reason": reason, "kind": "kitchen_context",
                                                         "crop": IF._crop_of(f)})
                out.append({"piece": f["id"], "room": room["id"], "type": drawn, "reason": reason, "review": True})
            gone.add(f["id"])
        if gone:
            out += _zone_left(b, room, gone)
    return out


def _zone_left(b: dict, room: dict, gone: set) -> list[dict]:
    """FIX-1: the room's kitchen zones keep only the kitchen pieces left; a zone with none left is dropped (logged)."""
    from wenart.ingest.generic import reading as RDG

    left = {f["id"] for f in b.get("furniture") or [] if f.get("room_id") == room.get("id")
            and f.get("type") in RDG.KITCHEN_ZONE_TYPES and f.get("build") is not False}
    out, zones = [], []
    for z in room.get("zones") or []:
        if z.get("kind") != "kitchen" or not set(z.get("piece_ids") or ()) & gone:
            zones.append(z)
            continue
        ids = [i for i in z.get("piece_ids") or [] if i in left]
        if ids:
            zones.append(dict(z, piece_ids=ids))
            continue
        reason = (f"{room['id']}: its kitchen zone {z.get('zone_id')} held only {', '.join(sorted(gone))}, read again "
                  f"(no kitchen kit left): the zone is dropped (R18)")
        out.append({"zone": z.get("zone_id"), "room": room["id"], "reason": reason, "dropped": copy.deepcopy(z)})
    room["zones"] = zones
    return out


CELL_MAX_M2 = 3.5               # ``topology.CLOSET_M2``: a cell this small is read by its words, then by its fixtures
CELL_FIXTURES = {"shower": "bathroom", "bathtub": "bathroom", "shower_tray": "bathroom", "toilet": "wc"}


def wet_cells(b: dict) -> list[dict]:
    """28 Nov 2026 (round 5a fix-up, WET-1): a small cell no text names (no ``label_raw``) that the reader typed by its
    size or its words as storage, technical or other, holding a drawn shower or bath (a bathroom) or toilet (a WC) after
    the furniture is read, is that wet cell (``adjusted_by_ai`` by code, its role name 'Duş' / 'WC' with ``label_role``):
    real15's shower cell with its tray and 'E.ŞOFBEN' is a shower cell, a boiler closet with nothing drawn stays
    technical. In place; one record per room."""
    from wenart.ingest import completion as CP

    out = []
    for room in b.get("rooms") or []:
        if room.get("label_raw") or str(room.get("room_type") or "") not in ("storage", "technical", "other", "unknown"):
            continue
        p = CP._poly(room.get("polygon"))
        if p is None or p.area > CELL_MAX_M2:
            continue
        held = [f for f in b.get("furniture") or [] if f.get("room_id") == room.get("id")
                and f.get("build") is not False and f.get("source") == "from_documents" and f.get("type") in CELL_FIXTURES]
        if not held:
            continue
        rtype = "bathroom" if any(CELL_FIXTURES[f["type"]] == "bathroom" for f in held) else "wc"
        before = {"room_type": room.get("room_type"), "label": room.get("label")}
        why = (f"{room['id']} ({p.area:.2f} m², no text names it) holds the drawn "
               f"{', '.join(sorted({f['type'] for f in held}))} {', '.join(f['id'] for f in held[:3])}: a "
               f"{'shower cell' if rtype == 'bathroom' else 'WC'} (R21)")
        room["room_type"] = rtype
        room["label"] = "Duş" if rtype == "bathroom" else "WC"
        room["label_role"] = True
        room.setdefault("label_placeholder", before["label"])
        room["adjusted_by_ai"] = {"by": "code", "rule": "wet_cell_fixtures", "reason": why, "changed": before}
        out.append({"room": room["id"], "room_type": rtype, "reason": why})
    return out
