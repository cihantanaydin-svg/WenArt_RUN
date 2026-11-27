"""Names of the rooms no text names (27 Nov 2026, audit fix round 5a, rule R28).

What: ``name_faces(b)`` runs at the end of the reading: a room the drawing gives no label (``label_raw`` empty, its name
the reader's placeholder 'Oda' / 'Room') takes

1. the label of the labelled room of the same kind (a hall, or its own type) it opens onto without a door (a doorless
   gap, ``type`` opening or a virtual separator, between them: real06's L1 corridor is part of HOL), else
2. a role name from its type (``ROLE_NAMES``: Hol, Koridor, Giriş, Merdiven, Depo ...), never the bare 'Oda' that
   collides with real ODA rooms (real06's bedroom became r_L1_oda_2 beside an unlabelled 'Oda' corridor).

The new name is ``label_inferred`` (method ``open_neighbour`` or ``role``) and ``label_role: true``; ``label_raw`` stays
empty (no text names it), so every check that asks whether a room is labelled sees it unlabelled as before. A room
whose label names a dressing room ('SOYUNMA ODASI', 'GİYİNME BÖL.', 'dressing', 'walk-in') keeps its name and gets
``room_use: dressing`` with ``dressing_of``: the bedroom it opens into (never storage).

Why: names feed the cameras, the room programs and the reports; two 'Oda' rooms beside a real ODA confused all three.

How: pure on the building JSON; no AI.
"""
from __future__ import annotations

import math
import re
from typing import Optional

from shapely.geometry import Point

ROLE_NAMES = {
    "tr": {"hall": "Hol", "corridor": "Koridor", "porch": "Giriş", "stair": "Merdiven", "storage": "Depo",
           "shaft": "Şaft", "wc": "WC", "bathroom": "Banyo", "kitchen": "Mutfak", "balcony": "Balkon",
           "garage": "Garaj", "technical": "Teknik Hacim", "living": "Oturma Odası", "bedroom": "Yatak Odası",
           "dining": "Yemek Alanı", "prayer": "Mescit", "other": "Alan", "unknown": "Alan"},
    "en": {"hall": "Hall", "corridor": "Corridor", "porch": "Porch", "stair": "Stair", "storage": "Storage",
           "shaft": "Shaft", "wc": "WC", "bathroom": "Bathroom", "kitchen": "Kitchen", "balcony": "Balcony",
           "garage": "Garage", "technical": "Technical room", "living": "Living room", "bedroom": "Bedroom",
           "dining": "Dining area", "prayer": "Prayer room", "other": "Space", "unknown": "Space"},
}
PLACEHOLDERS = ("oda", "room")
CORRIDOR_ASPECT = 3.0           # a hall face this many times longer than wide is a corridor
DRESSING_RE = re.compile(r"(?<![a-z])(?:soyunma|giyinme|giyinme\s+bol\w*|dressing|walk\s*-?\s*in|vestiyer)(?![a-z])")
OPEN_LINK_M = 0.35              # a doorless gap this close to two rooms' outlines joins them
OPEN_JOIN_TYPES = ("hall",)     # an unnamed face takes the label of an open neighbour of these types (or of its own)


def _fold(text) -> str:
    from wenart import building as B
    return " ".join(B.fold_ascii(str(text or "")).lower().split())


def _poly(room: dict):
    from wenart.ingest import completion as CP
    return CP._poly(room.get("polygon"))


def unnamed(room: dict) -> bool:
    """No text names the room: no ``label_raw``, its name the placeholder (or none), no label inferred elsewhere."""
    if room.get("label_raw") or room.get("label_inferred"):
        return False
    return _fold(room.get("label")) in PLACEHOLDERS + ("",)


def _lang(room: dict) -> str:
    return "en" if _fold(room.get("label")) == "room" else "tr"


def _links(b: dict, room: dict, rooms: list) -> list:
    """The rooms ``room`` opens onto through a doorless gap (``type`` opening or virtual), nearest first."""
    p = _poly(room)
    if p is None:
        return []
    out = []
    for o in b.get("openings") or []:
        if o.get("level_id") != room.get("level_id") or not o.get("center"):
            continue
        if not (o.get("virtual") or o.get("type") == "opening"):
            continue
        c = Point(o["center"][:2])
        if p.exterior.distance(c) > OPEN_LINK_M:
            continue
        for r in rooms:
            if r is room:
                continue
            q = _poly(r)
            if q is not None and q.exterior.distance(c) <= OPEN_LINK_M:
                out.append((q.exterior.distance(c), r))
    return [r for _d, r in sorted(out, key=lambda x: x[0])]


def _aspect(room: dict) -> float:
    p = _poly(room)
    if p is None or p.area <= 0:
        return 1.0
    mrr = p.minimum_rotated_rectangle
    xs = list(mrr.exterior.coords)
    a, c = math.dist(xs[0], xs[1]), math.dist(xs[1], xs[2])
    return max(a, c) / max(min(a, c), 1e-6)


def name_faces(b: dict) -> list[dict]:
    """The names of the unnamed rooms and the dressing rooms (module docstring), in place; one record per change."""
    out: list[dict] = []
    by_level: dict = {}
    for r in b.get("rooms") or []:
        by_level.setdefault(r.get("level_id"), []).append(r)
    for lid, rooms in sorted(by_level.items(), key=lambda kv: str(kv[0])):
        for r in rooms:
            if not unnamed(r):
                continue
            lang = _lang(r)
            # the open neighbour's label when it is the same kind of space (a corridor that is part of the HOL), never
            # a room of another use beside an open hall (a hall holding the stair beside the drawing room)
            named = [x for x in _links(b, r, rooms) if x.get("label_raw") and not unnamed(x)
                     and (x.get("room_type") in OPEN_JOIN_TYPES or x.get("room_type") == r.get("room_type"))]
            if named:
                src = named[0]
                r["label"] = src.get("label")
                r["label_inferred"] = {"method": "open_neighbour", "of": src["id"],
                                       "reason": f"no text names it; it opens onto {src['id']} "
                                                 f"'{src.get('label')}' without a door: part of that room (R28)"}
            else:
                rtype = str(r.get("room_type") or "unknown")
                if rtype == "hall" and _aspect(r) >= CORRIDOR_ASPECT:
                    rtype = "corridor"
                name = ROLE_NAMES[lang].get(rtype, ROLE_NAMES[lang]["unknown"])
                r["label"] = name
                r["label_inferred"] = {"method": "role", "role": rtype,
                                       "reason": f"no text names it: the role name of a {rtype} (never the "
                                                 f"placeholder 'Oda', R28)"}
            r["label_role"] = True
            out.append({"room": r["id"], "level_id": lid, "label": r["label"],
                        "method": r["label_inferred"]["method"]})
        for r in rooms:
            f = _fold(f"{r.get('label_raw') or ''} {r.get('label') or ''}")
            if not DRESSING_RE.search(f) or r.get("room_use") == "dressing":
                continue
            r["room_use"] = "dressing"
            bed = next((x for x in _door_links(b, r, rooms) if x.get("room_type") == "bedroom"), None)
            if bed is not None:
                r["dressing_of"] = bed["id"]
            out.append({"room": r["id"], "level_id": lid, "room_use": "dressing",
                        "dressing_of": bed["id"] if bed else None})
    return out


def _door_links(b: dict, room: dict, rooms: list) -> list:
    """The rooms ``room`` opens onto through a door or a doorless gap."""
    p = _poly(room)
    if p is None:
        return []
    out = []
    for o in b.get("openings") or []:
        if o.get("level_id") != room.get("level_id") or not o.get("center") or o.get("type") == "window":
            continue
        c = Point(o["center"][:2])
        if p.exterior.distance(c) > OPEN_LINK_M:
            continue
        for r in rooms:
            q = _poly(r)
            if r is not room and q is not None and q.exterior.distance(c) <= OPEN_LINK_M:
                out.append(r)
    return out


def label_of(room: Optional[dict]) -> str:
    """The room's label as a check reads it: empty for a role name (``label_role``; no text names the room)."""
    if not room or room.get("label_role"):
        return ""
    return str(room.get("label") or room.get("label_raw") or "")
