"""Twin rooms of a semi-detached pair and rooms an alternative level shares with its base (docs/milestone10.md §1.1,
§3.2 items 6-7).

What: ``mirror_twins(rooms, openings, furniture) -> {room id: twin id}`` finds, per level, the rooms that mirror an
other room of the same level about one axis (the party wall of a semi-detached pair); ``twin_transforms`` gives the
same pairs with the mirror as an affine ``[a, b, c, d, e, f]`` (first twin -> this room, ``rooms[].twin_transform``)
and the Hausdorff distance it leaves (``twin_residual_m``, docs/milestone10.md §1.6b row 18); ``same_as(alt_rooms,
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

Milestone 11 (docs/milestone11.md §1.2 M7, U16): a drawn piece still ``unknown`` in one twin matches the mirrored
piece of the same footprint size in the other (real02's L1 corridor and open kitchen were not paired: one twin's
bench / island was typed, the other's not), unlabelled faces pair too (the stair cores); ``twin_copies`` /
``apply_twin_copies`` then give the untyped (or frontless) twin piece the agreed twin's type, size and mirrored
front, ``inferred: true``.
"""
from __future__ import annotations

import math
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


def _sorted_size(f: dict) -> list[float]:
    return sorted(float(v) for v in f["footprint"]["size"])


def _piece_same(a: dict, b: dict) -> bool:
    """The same drawn piece in both twins: the same type, or (Milestone 11, M7: real02's L1 corridor and open kitchen
    were not paired because one twin's piece was typed and the other's not) the same footprint size within 2 cm when
    one of them is still ``unknown`` (the agreed twin's type is copied over, ``twin_copies``)."""
    if a["type"] == b["type"]:
        return True
    if "unknown" not in (a["type"], b["type"]):
        return False
    return all(abs(x - y) <= TOL for x, y in zip(_sorted_size(a), _sorted_size(b)))


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


def mirror_affine(axis: tuple[str, float]) -> list[float]:
    """The mirror about a vertical (``x = c``) or horizontal (``y = c``) axis as ``[a, b, c, d, e, f]``."""
    kind, c = axis
    m = round(2.0 * c, 6) + 0.0
    return [-1.0, 0.0, m, 0.0, 1.0, 0.0] if kind == "x" else [1.0, 0.0, 0.0, 0.0, -1.0, m]


def mirror_twins(rooms: list[dict], openings: list[dict], furniture: list[dict]) -> dict[str, str]:
    return {second: info["twin_of"] for second, info in twin_transforms(rooms, openings, furniture).items()}


def twin_transforms(rooms: list[dict], openings: list[dict], furniture: list[dict]) -> dict[str, dict]:
    """``{second twin id: {twin_of, transform, residual_m}}``."""
    out: dict[str, dict] = {}
    by_level: dict[str, list[dict]] = {}
    for r in rooms:
        # Milestone 11 (M7): unlabelled faces too (real02's two stair cores "Oda"): the label must still be the same
        # and the polygon, openings and pieces must mirror.
        if (r.get("label_raw") or r.get("label")) and len(r.get("polygon") or []) >= 3:
            by_level.setdefault(r["level_id"], []).append(r)
    for level_rooms in by_level.values():
        found: list[tuple[str, float, dict, dict]] = []
        level_rooms = sorted(level_rooms, key=lambda r: r["id"])
        for i, a in enumerate(level_rooms):
            ca = _poly(a).centroid
            for b in level_rooms[i + 1:]:
                if a["label"] != b["label"]:
                    continue
                cb = _poly(b).centroid
                if abs(_poly(a).area - _poly(b).area) > 0.02 * max(_poly(a).area, 1e-9):
                    continue
                if abs(ca.y - cb.y) <= TOL and abs(ca.x - cb.x) > TOL:
                    found.append(("x", (ca.x + cb.x) / 2.0, a, b))
                if abs(ca.x - cb.x) <= TOL and abs(ca.y - cb.y) > TOL:
                    found.append(("y", (ca.y + cb.y) / 2.0, a, b))
        if not found:
            continue
        # Candidate axes within 2 cm of each other are one axis (its median); the axis of the most pairs wins.
        groups: list[list[tuple]] = []
        for item in sorted(found, key=lambda f: (f[0], f[1])):
            if groups and groups[-1][0][0] == item[0] and item[1] - groups[-1][-1][1] <= TOL:
                groups[-1].append(item)
            else:
                groups.append([item])
        best = max(groups, key=lambda g: (len(g), -g[0][1]))
        values = sorted(f[1] for f in best)
        axis = (best[0][0], values[len(values) // 2])
        for _, _, a, b in best:
            if a["id"] in out or b["id"] in out:
                continue
            if not _equal(a, b, openings, furniture, lambda p: _mirror_pt(p, axis)):
                continue
            ca, cb = _poly(a).centroid, _poly(b).centroid
            first, second = (a, b) if (ca.x if axis[0] == "x" else ca.y) < (cb.x if axis[0] == "x" else cb.y) \
                else (b, a)
            residual = _mirror_poly(_poly(first), axis).hausdorff_distance(_poly(second))
            out[second["id"]] = {"twin_of": first["id"], "transform": mirror_affine(axis),
                                 "residual_m": round(float(residual), 4) + 0.0}
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


# --------------------------------------------------------------------------
# Milestone 11 (docs/milestone11.md §1.2 U16): twins take the agreed twin's type and front
# --------------------------------------------------------------------------

AGREED_METHODS = ("block_name", "rule", "ai_two_pass")


def _agreed(f: dict) -> bool:
    """A piece whose type the documents or both AI passes decided (not ``unknown``)."""
    return f["type"] != "unknown" and (f.get("type_method") in AGREED_METHODS or f.get("type_method") is None)


def _mirror_dir(deg: float, transform: list[float]) -> float:
    a, b, _c, d, e, _f = transform
    vx, vy = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return round(math.degrees(math.atan2(d * vx + e * vy, a * vx + b * vy)) % 360.0, 3)


def _apply(t: list[float], p) -> tuple[float, float]:
    a, b, c, d, e, f = t
    return a * p[0] + b * p[1] + c, d * p[0] + e * p[1] + f


def _mirror_footprint(src: dict, dst: dict, transform: list[float]) -> tuple[dict, Optional[float]]:
    """The footprint and front ``dst`` takes from its twin ``src``: ``dst``'s own drawn centre, ``src``'s size and
    its rotation and front mirrored (a front keeps ``rotation = front + 90``)."""
    from wenart.furniture import placer

    if src.get("front_deg") is not None:
        _rot, size = placer.front_frame(src["footprint"], src["front_deg"])
        front = _mirror_dir(float(src["front_deg"]), transform)
        rotation = (front + 90.0) % 360.0
    else:
        size = (float(src["footprint"]["size"][0]), float(src["footprint"]["size"][1]))
        front = None
        rotation = _mirror_dir(float(src["footprint"]["rotation_deg"]), transform) % 180.0
    fp = {"center": list(dst["footprint"]["center"]), "size": [round(float(size[0]), 4), round(float(size[1]), 4)],
          "rotation_deg": round(rotation, 3)}
    return fp, front


def twin_copies(rooms: list[dict], furniture: list[dict]) -> list[dict]:
    """``[{"piece_id", "from_id", "type", "footprint", "front_deg", "reason"}]``: for every pair of twin rooms
    (``rooms[].twin_of`` / ``twin_transform``), the drawn pieces that mirror each other (centre within 2 cm, same
    footprint size) where one twin's piece has an agreed type (block name, rule, both AI passes) and the other's is
    ``unknown``, or both have the type and only the agreed one a front: the other takes the agreed type, size and
    the mirrored front. Both typed differently: nothing is copied."""
    by_id = {r["id"]: r for r in rooms}
    out: list[dict] = []
    for second in rooms:
        first = by_id.get(second.get("twin_of") or "")
        t = second.get("twin_transform")
        if first is None or not t:
            continue
        left = list(_room_pieces(second, furniture))
        for a in _room_pieces(first, furniture):
            p = _apply(t, a["footprint"]["center"])
            b = next((x for x in left if Point(x["footprint"]["center"]).distance(Point(p)) <= TOL
                      and all(abs(u - v) <= TOL for u, v in zip(_sorted_size(a), _sorted_size(x)))), None)
            if b is None:
                continue
            left.remove(b)
            for src, dst, src_room in ((a, b, first), (b, a, second)):
                if not _agreed(src):
                    continue
                unknown = dst["type"] == "unknown"
                if unknown or (dst["type"] == src["type"] and dst.get("front_deg") is None
                               and src.get("front_deg") is not None):
                    fp, front = _mirror_footprint(src, dst, t)
                    what = "type and front" if unknown else "front"
                    out.append({"piece_id": dst["id"], "from_id": src["id"], "type": src["type"], "footprint": fp,
                                "front_deg": front, "reason": f"{what} of {src['id']}, its mirror twin in "
                                                              f"{src_room['id']} (U16)"})
                    break
    return out


def apply_twin_copies(furniture: list[dict], copies: list[dict]) -> list[str]:
    """Apply ``twin_copies`` in place (the pipeline's building): type, footprint frame and front, ``inferred: true``
    and an ``inferred`` evidence entry naming the twin. Returns one line per copy for the warnings."""
    by_id = {f["id"]: f for f in furniture}
    lines = []
    for c in copies:
        f = by_id.get(c["piece_id"])
        if f is None:
            continue
        old = f["type"]
        f["type"] = c["type"]
        f["footprint"] = dict(c["footprint"])
        f["front_deg"] = c["front_deg"]
        f["inferred"] = True
        f["inferred_reason"] = c["reason"]
        src = (f.get("evidence") or [{}])[0]
        ev = {"file": src.get("file") or "building.json", "method": "inferred", "confidence": 0.8,
              "rule": "ingest.twins", "text": c["reason"]}
        for k in ("page", "entity", "region_id"):
            if src.get(k) is not None:
                ev[k] = src[k]
        f.setdefault("evidence", []).append(ev)
        lines.append(f"{f['id']}: {old} -> {c['type']}"
                     + (f", front {c['front_deg']:g} deg" if c["front_deg"] is not None else "")
                     + f" ({c['reason']}; inferred)")
    return lines
