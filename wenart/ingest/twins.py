"""Twin rooms of a semi-detached pair and rooms an alternative level shares with its base (docs/milestone10.md §1.1,
§3.2 items 6-7).

What: ``mirror_twins(rooms, openings, furniture) -> {room id: twin id}`` finds, per level, the rooms that mirror an
other room of the same level about one axis (the party wall of a semi-detached pair); ``same_as(alt_rooms,
base_rooms, openings, furniture) -> {alternative room id: base room id}`` finds the rooms of an alternative level
that equal a base room.

Why: real02 draws two mirrored dwellings on every plan; with ``render.twin_rooms: one`` only the first twin of each
pair is rendered and its AI furniture is mirrored onto the second, and an alternative level renders only the rooms
that differ from the base (``variants[].rooms_changed``).

How (tolerance 2 cm, deterministic):
- twins: two rooms of one level with the same label whose centroids lie on one horizontal (or vertical) line give a
  candidate axis halfway between them; the axis that explains the most pairs is the level's mirror axis. A pair is
  twins when the mirrored polygon of one lies within 2 cm of the other (Hausdorff distance), every opening on its
  boundary has a mirrored opening of the same type and width on the other's, and every drawn piece in it has a
  mirrored piece of the same type in the other. The room on the lower side of the axis is the first twin; the other
  gets ``twin_of``.
- same_as: an alternative room equals a base room when the polygons lie within 2 cm, the labels are the same and
  the openings on their boundaries and their drawn pieces match (type, width / centre within 2 cm).
"""
from __future__ import annotations

from typing import Optional

from shapely.geometry import Point, Polygon

TOL = 0.02
OPENING_REACH = 0.35          # an opening belongs to a room when its centre is this close to the room's boundary


def _poly(room: dict) -> Polygon:
    return Polygon(room["polygon"])


def _mirror_pt(p, axis: tuple[str, float]) -> tuple[float, float]:
    kind, c = axis
    return (2 * c - p[0], p[1]) if kind == "x" else (p[0], 2 * c - p[1])


def _mirror_poly(poly: Polygon, axis: tuple[str, float]) -> Polygon:
    return Polygon([_mirror_pt(p, axis) for p in poly.exterior.coords])


def _room_openings(room: dict, openings: list[dict]) -> list[dict]:
    boundary = _poly(room).exterior
    return [o for o in openings if o["level_id"] == room["level_id"]
            and boundary.distance(Point(o["center"])) <= OPENING_REACH]


def _room_pieces(room: dict, furniture: list[dict]) -> list[dict]:
    return [f for f in furniture if f.get("room_id") == room["id"] and f.get("source") == "from_documents"]


def _match(items_a: list[dict], items_b: list[dict], centre, same, transform) -> bool:
    if len(items_a) != len(items_b):
        return False
    left = list(items_b)
    for a in items_a:
        p = transform(centre(a))
        hit = next((b for b in left if same(a, b) and Point(centre(b)).distance(Point(p)) <= TOL), None)
        if hit is None:
            return False
        left.remove(hit)
    return True


def _opening_same(a: dict, b: dict) -> bool:
    return a["type"] == b["type"] and abs(float(a["width"]) - float(b["width"])) <= TOL


def _piece_same(a: dict, b: dict) -> bool:
    return a["type"] == b["type"]


def _equal(a: dict, b: dict, openings: list[dict], furniture: list[dict], transform) -> bool:
    pa, pb = _poly(a), _poly(b)
    moved = Polygon([transform(p) for p in pa.exterior.coords])
    if not moved.is_valid or moved.hausdorff_distance(pb) > TOL:
        return False
    if not _match(_room_openings(a, openings), _room_openings(b, openings), lambda o: o["center"], _opening_same,
                  transform):
        return False
    return _match(_room_pieces(a, furniture), _room_pieces(b, furniture), lambda f: f["footprint"]["center"],
                  _piece_same, transform)


def mirror_twins(rooms: list[dict], openings: list[dict], furniture: list[dict]) -> dict[str, str]:
    out: dict[str, str] = {}
    by_level: dict[str, list[dict]] = {}
    for r in rooms:
        if r.get("label_raw") and len(r.get("polygon") or []) >= 3:
            by_level.setdefault(r["level_id"], []).append(r)
    for level_rooms in by_level.values():
        cands: dict[tuple, list[tuple[dict, dict]]] = {}
        for i, a in enumerate(level_rooms):
            ca = _poly(a).centroid
            for b in level_rooms[i + 1:]:
                if a["label"] != b["label"]:
                    continue
                cb = _poly(b).centroid
                if abs(_poly(a).area - _poly(b).area) > 0.02 * max(_poly(a).area, 1e-9):
                    continue
                if abs(ca.y - cb.y) <= TOL and abs(ca.x - cb.x) > TOL:
                    cands.setdefault(("x", round((ca.x + cb.x) / 2.0, 2)), []).append((a, b))
                if abs(ca.x - cb.x) <= TOL and abs(ca.y - cb.y) > TOL:
                    cands.setdefault(("y", round((ca.y + cb.y) / 2.0, 2)), []).append((a, b))
        if not cands:
            continue
        axis = max(sorted(cands), key=lambda k: len(cands[k]))
        for a, b in cands[axis]:
            if a["id"] in out or b["id"] in out:
                continue
            if not _equal(a, b, openings, furniture, lambda p: _mirror_pt(p, axis)):
                continue
            ca, cb = _poly(a).centroid, _poly(b).centroid
            first, second = (a, b) if (ca.x if axis[0] == "x" else ca.y) < (cb.x if axis[0] == "x" else cb.y) \
                else (b, a)
            out[second["id"]] = first["id"]
    return out


def same_as(alt_rooms: list[dict], base_rooms: list[dict], openings: list[dict],
            furniture: list[dict]) -> dict[str, str]:
    out: dict[str, str] = {}
    taken: set[str] = set()
    for a in alt_rooms:
        if len(a.get("polygon") or []) < 3:
            continue
        best: Optional[dict] = None
        for b in base_rooms:
            if b["id"] in taken or b["label"] != a["label"] or len(b.get("polygon") or []) < 3:
                continue
            if _equal(a, b, openings, furniture, lambda p: (p[0], p[1])):
                best = b
                break
        if best is not None:
            out[a["id"]] = best["id"]
            taken.add(best["id"])
    return out
