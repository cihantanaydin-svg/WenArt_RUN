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
import re
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
    # real10: a room named by its mirror (``mirror_labels``) lies within the mirror-label tolerance of its twin.
    mirrored = any((r.get("label_inferred") or {}).get("method") == "mirror" for r in (a, b))
    if not moved.is_valid or moved.hausdorff_distance(pb) > (MIRROR_LABEL_TOL if mirrored else TOL):
        return False
    if not _match(_room_openings(a, openings), _room_openings(b, openings), lambda o: o["center"], _opening_same,
                  transform):
        return False
    if mirrored:
        # The drafter drew the furniture in the named half only (real10's left flats): the pieces are not compared.
        return True
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


MIRROR_LABEL_IOU = 0.95     # 3 Nov 2026: ... or overlapping it by 95 % (intersection over union)
MIRROR_LABEL_TOL = 0.10      # real10: an unlabelled face within 10 cm (Hausdorff) of a labelled room's mirror


def _wall_axis(walls: list, level_id: str):
    """The level's mirror axis from its walls (``generic.facade.mirror_axis``), or None."""
    from types import SimpleNamespace

    from wenart.ingest.generic import facade as FC

    items = [SimpleNamespace(start=tuple(w["start"]), end=tuple(w["end"]), thickness=float(w.get("thickness") or 0.2))
             for w in walls or [] if w.get("level_id") == level_id and w.get("start") and w.get("end")]
    return FC.mirror_axis(items) if len(items) >= 4 else None


def mirror_labels(rooms: list[dict], walls: Optional[list] = None) -> list[str]:
    """real10 (1 Nov 2026): a plan that labels only one of two mirrored halves (the two flats of an apartment floor,
    a semi-detached pair: the drafter wrote the names in one). Per level, the mirror axis is the one most pairs of a
    labelled room and an unlabelled face of the same area (2 %) on one line agree on (within ``TOL``); an unlabelled
    face whose polygon lies within ``MIRROR_LABEL_TOL`` of a labelled room's mirror takes its label and room type,
    ``inferred`` (``label_raw`` stays null: no text names it). Returns one line per labelled face."""
    notes: list[str] = []
    by_level: dict[str, list[dict]] = {}
    for r in rooms:
        if len(r.get("polygon") or []) >= 3:
            by_level.setdefault(r["level_id"], []).append(r)
    for level_id, level_rooms in by_level.items():
        named = [r for r in level_rooms if r.get("label_raw")]
        blank = [r for r in level_rooms if not r.get("label_raw")]
        if not named or not blank:
            continue
        votes: list[tuple[str, float]] = []
        for a in named:
            pa = _poly(a)
            for b in blank:
                pb = _poly(b)
                if abs(pa.area - pb.area) > 0.02 * max(pa.area, 1e-9):
                    continue
                ca, cb = pa.centroid, pb.centroid
                if abs(ca.y - cb.y) <= TOL and abs(ca.x - cb.x) > TOL:
                    votes.append(("x", (ca.x + cb.x) / 2.0))
                if abs(ca.x - cb.x) <= TOL and abs(ca.y - cb.y) > TOL:
                    votes.append(("y", (ca.y + cb.y) / 2.0))
        groups: list[list[tuple[str, float]]] = []
        for v in sorted(votes):
            if groups and groups[-1][0][0] == v[0] and v[1] - groups[-1][-1][1] <= TOL:
                groups[-1].append(v)
            else:
                groups.append([v])
        best = max(groups, key=len) if groups else []
        if len(best) >= 2:
            axis = (best[0][0], sorted(v[1] for v in best)[len(best) // 2])
        else:
            # 3 Nov 2026 (real09's attic: one pair of equal areas only, the living rooms differ by 4 % by a door
            # notch): the walls' own mirror axis (``generic.facade.mirror_axis``)
            axis = _wall_axis(walls, level_id)
            if axis is None:
                continue
        taken: set = set()
        for a in named:
            mirrored = _mirror_poly(_poly(a), axis)
            cands = [(mirrored.hausdorff_distance(_poly(b)), b["id"], b) for b in blank if b["id"] not in taken]
            # 3 Nov 2026 (real09: the left flat's entrance hall and living room overlap their twins' mirrors by 99 %,
            # a door notch puts one point 0.24-0.27 m off): an overlap of ``MIRROR_LABEL_IOU`` is a twin too
            cands = [c for c in cands if c[0] <= MIRROR_LABEL_TOL or _iou(mirrored, _poly(c[2])) >= MIRROR_LABEL_IOU]
            if not cands:
                continue
            dist, _, b = min(cands, key=lambda c: (c[0], c[1]))
            taken.add(b["id"])
            b["label"], b["room_type"] = a["label"], a["room_type"]
            if a.get("room_subtype") is not None:
                b["room_subtype"] = a["room_subtype"]
            b["inferred"] = True
            b["label_inferred"] = {"method": "mirror", "of": a["id"], "axis": [axis[0], round(axis[1], 4)],
                                   "hausdorff_m": round(float(dist), 4)}
            notes.append(f"{level_id}: unlabelled room {b['id']} takes the label '{a['label']}' of {a['id']}, its "
                         f"mirror about {axis[0]} = {axis[1]:.3f} (within {dist:.3f} m): the plan names one of the "
                         f"two mirrored halves only (inferred)")
    return notes


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


def _iou(a: Polygon, b: Polygon) -> float:
    u = a.union(b).area
    return float(a.intersection(b).area / u) if u > 0 else 0.0


CORE_LEVELS = 3               # 3 Nov 2026: a stair at one spot on this many levels is the building's stair core
CORE_REACH_M = 0.6
GENERIC_LABELS = {"oda", "room", "hol", "hall"}


def _holds_most(poly, fp: dict) -> bool:
    """The room polygon holds at least half of a piece's footprint rectangle."""
    from shapely.geometry import Polygon

    try:
        cx, cy = fp["center"][:2]
        w, d = fp["size"][:2]
        a = math.radians(float(fp.get("rotation_deg") or 0.0))
    except (KeyError, TypeError, ValueError):
        return False
    ca, sa = math.cos(a), math.sin(a)
    rect = Polygon([(cx + ca * u - sa * v, cy + sa * u + ca * v)
                    for u, v in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))])
    return rect.area > 0 and poly.intersection(rect).area >= 0.5 * rect.area


def stair_cores(rooms: list[dict], furniture: list[dict]) -> list[str]:
    """3 Nov 2026 (real09, user: "This section is wrong it s the main shaft with the stairs you should be able to
    understand it"): a room no text names (or named only by a placeholder) that holds a drawn stair standing at the same
    spot (within ``CORE_REACH_M``) on at least ``CORE_LEVELS`` levels is the building's stair core: it is named
    'Merdiven' ('Stair' on an English page), type ``stair``, ``label_inferred`` (method ``stair_core``). A family
    house's hall with its stair (two levels) stays a hall. Returns one line per room."""
    stairs = [f for f in furniture if f.get("type") == "stair" and (f.get("footprint") or {}).get("center")]
    notes = []
    for r in rooms:
        if r.get("label_raw") or len(r.get("polygon") or []) < 3:
            continue
        if str(r.get("label") or "").strip().lower() not in GENERIC_LABELS and r.get("room_type") not in ("hall",
                                                                                                           "unknown"):
            continue
        poly = _poly(r)
        # 3 Nov 2026 (real10: the core stair's centre stood in the hall in front of the stair room): the room holding
        # the stair's centre, or at least half of its footprint
        mine = [f for f in stairs if f.get("level_id") == r["level_id"]
                and (poly.contains(Point(f["footprint"]["center"])) or _holds_most(poly, f["footprint"])
                     or f.get("room_id") == r.get("id"))]         # 13 Nov 2026 (review BLD-04): its flights' room
        if not mine:
            continue
        c = mine[0]["footprint"]["center"]
        levels = sorted({f["level_id"] for f in stairs
                         if math.dist(f["footprint"]["center"][:2], c[:2]) <= CORE_REACH_M})
        if len(levels) < CORE_LEVELS:
            continue
        # the drawing's language: the placeholder, else the labels the level's plan writes (real10: the core room had
        # no placeholder and came out 'Stair' on a Turkish plan)
        from wenart import building as B
        turkish = str(r.get("label") or "").strip().lower() in ("oda", "hol") or any(
            B.is_turkish_label(str(x.get("label_raw") or "")) for x in rooms
            if x.get("level_id") == r["level_id"] and x.get("label_raw"))
        old = r.get("label")
        r["label"] = "Merdiven" if turkish else "Stair"
        r["room_type"] = "stair"
        r["inferred"] = True
        r["label_inferred"] = {"method": "stair_core", "levels": levels}
        notes.append(f"{r['level_id']}: room {r['id']} ('{old}') holds the stair that stands at the same spot on "
                     f"{len(levels)} levels ({', '.join(levels)}): the building's stair core, '{r['label']}' (inferred)")
    return notes


SUB_SPACE_REACH_M = 0.30         # 12 Nov 2026: a pending sub-space's label anchor this close to a part stands in it
STACK_IOU = 0.5                  # a part overlapping a lift of another level this much stacks on it (the same shaft)


def _lift_label(room: dict) -> bool:
    from wenart.sheets import register as RG
    from wenart.sheets import titles as TI

    return room.get("room_type") == "shaft" and bool(RG.LIFT_RE.search(TI.fold(str(room.get("label_raw") or
                                                                                    room.get("label") or "")))) \
        and not _machine(room)


LIFT_SIDE_M = (0.9, 2.6)        # 12 Nov 2026: a lift shaft's sides (labels.AREA_RANGES 'lift': up to a 2.6 x 3.0 m car) ...
LIFT_LONG_MAX_M = 3.0           # ... its long side at most this
SMALL_ROOM_DOORS_MAX = 1        # a lift, shaft, WC or closet has one door at most (a landing has the flats' doors)


def fits_small_room(part: Polygon, kind: str, openings: Optional[list] = None) -> bool:
    """12 Nov 2026 (round-2 review, CODE-A2 / G5: a stair-core remainder holding the lift and the landing became one
    6 m2 'Asansör' and sealed the stair off): whether a part can be the small room ``kind``: a lift's oriented box fits a
    shaft (``LIFT_SIDE_M``, ``LIFT_LONG_MAX_M``), and no small room has more than ``SMALL_ROOM_DOORS_MAX`` drawn door
    on its edges (``openings``: the level's, dicts)."""
    if kind == "lift":
        box = part.minimum_rotated_rectangle
        if box.geom_type != "Polygon":
            return False
        c = list(box.exterior.coords)
        sides = sorted((math.dist(c[0], c[1]), math.dist(c[1], c[2])))
        if sides[0] < LIFT_SIDE_M[0] or sides[0] > LIFT_SIDE_M[1] or sides[1] > LIFT_LONG_MAX_M:
            return False
    doors = [o for o in openings or [] if o.get("type") == "door" and not o.get("virtual") and o.get("center")
             and part.exterior.distance(Point(o["center"][:2])) <= 0.3]
    return len(doors) <= SMALL_ROOM_DOORS_MAX


def sub_space_of(part: Polygon, room: dict, rooms: list[dict], openings: Optional[list] = None) -> Optional[dict]:
    """12 Nov 2026 (review of the reader targets, real11 A2 / A-L1 / F5: the lift shaft beside the core stair became
    'Kat Holü' on 8 levels): what a part split off a room (or an unnamed room) is when it is a small room of its own:
    the room's pending sub-space (``rooms.derive_rooms`` ``sub_spaces``: a lift, shaft, WC or closet label that gave up
    the larger face) whose anchor stands in the part (within ``SUB_SPACE_REACH_M``) and whose type's area range
    (``labels.AREA_RANGES``) the part fits; else a lift of another level the part stacks on (``STACK_IOU``) when it fits
    a lift's range. ``{"label", "label_raw", "type", "how", "sub"}`` or None."""
    from wenart.ingest.generic import labels as LB

    a = part.area
    for sp in room.get("sub_spaces") or []:
        at = sp.get("anchor")
        lo, hi = float(sp.get("min_m2") or 0.0), float(sp.get("max_m2") or 0.0)
        if at and part.distance(Point(at[:2])) <= SUB_SPACE_REACH_M and lo <= a <= hi \
                and fits_small_room(part, sp["type"], openings):
            return {"label_raw": sp["label"], "type": sp["type"], "how": f"its label '{sp['label']}' stands in it",
                    "sub": sp}
    lo, hi = LB.AREA_RANGES["lift"][:2]
    if lo <= a <= hi and fits_small_room(part, "lift", openings):
        for x in rooms:
            if x.get("level_id") != room.get("level_id") and _lift_label(x) and len(x.get("polygon") or []) >= 3 \
                    and _iou(part, _poly(x)) >= STACK_IOU:
                return {"label_raw": x.get("label_raw") or x.get("label"), "type": "lift",
                        "how": f"it stacks on the lift {x['id']} of {x['level_id']}", "sub": None}
    return None


def _as_sub_space(room: dict, what: dict) -> None:
    """Names a room the small room ``what`` says (``sub_space_of``; mutated): the label from its text, type ``shaft``
    for a lift or a shaft (the schema's type), ``label_inferred`` method ``sub_space``."""
    from wenart import building as B

    label, rtype, _ = B.normalise_room_label(str(what["label_raw"]))
    room["label"] = label
    room["label_raw"] = what["label_raw"]
    room["room_type"] = "shaft" if what["type"] in ("lift", "shaft") else rtype
    room["inferred"] = True
    room["has_documented_furniture"] = False
    room["label_inferred"] = {"method": "sub_space", "reason": what["how"]}
    room.pop("sub_spaces", None)


def straight_runs(line) -> list:
    """The straight runs (shapely lines) of a line or a multi-line: one wall each (a common edge turns at a shaft's
    corners); runs under 0.3 m are left out."""
    from shapely.geometry import LineString

    if line is None or line.is_empty:
        return []
    out = []
    for g in getattr(line, "geoms", [line]):
        if g.geom_type != "LineString":
            continue
        pts = list(g.simplify(1e-4).coords)
        out += [LineString([a, b]) for a, b in zip(pts, pts[1:]) if math.dist(a, b) >= 0.3]
    return out


CARVE_SLIT_M = 0.002            # the slit that opens a room around a free-standing shaft to its edge


def _open_hole(poly: Polygon) -> Optional[Polygon]:
    """A polygon with holes cut open to its outer ring along the shortest line from each hole (a ``CARVE_SLIT_M``
    slit): one simple polygon, or None when that fails."""
    from shapely.geometry import LineString
    from shapely.ops import nearest_points

    out = poly
    for ring in list(poly.interiors):
        hole = Polygon(ring)
        a, b = nearest_points(hole.exterior, Polygon(out.exterior).exterior)
        if a.distance(b) <= 0:
            continue
        slit = LineString([(a.x, a.y), (b.x, b.y)]).buffer(CARVE_SLIT_M / 2.0, cap_style=2)
        out = out.difference(slit).buffer(0)
        if out.geom_type != "Polygon":
            out = max(getattr(out, "geoms", [out]), key=lambda g: g.area)
    return out if out.geom_type == "Polygon" and not out.interiors else None


SUB_SPACE_INSIDE = 0.8           # an untyped drawn piece this much inside a room can be its pending small room


def carve_sub_spaces(rooms: list[dict], furniture: list[dict], walls: Optional[list] = None) -> list[str]:
    """12 Nov 2026 (review of the reader targets, real20 A-L2: the lift's label gave up the 16 m2 core and the lift was
    never built; its shaft outline was read as the untyped piece f_L0_002, 1.73 x 1.70 m): a room's pending sub-space
    (``sub_spaces``) whose label anchor stands on an untyped drawn piece (``SUB_SPACE_INSIDE`` of it in the room) of
    that type's area range is that small room: the piece's rectangle becomes a room of its own (``sub_space_of``
    naming), the room keeps the rest (one polygon of at least 1 m2), the piece is not furniture (not built) and the
    side of the shaft towards the rest gets an inferred wall where none was read. Mutates; returns one line each."""
    from shapely.ops import unary_union

    from wenart.ingest.generic import labels as LB

    notes = []
    for r in list(rooms):
        pend = [s for s in r.get("sub_spaces") or [] if s.get("anchor")]
        if not pend or len(r.get("polygon") or []) < 3:
            continue
        poly = _poly(r)
        for sp in pend:
            at = Point(sp["anchor"][:2])
            lo, hi = LB.AREA_RANGES[sp["type"]][:2]
            for f in furniture:
                if f.get("level_id") != r["level_id"] or f.get("type") not in (None, "unknown") \
                        or not (f.get("footprint") or {}).get("size"):
                    continue
                box = _stair_box(f)
                if not (lo <= box.area <= hi) or box.distance(at) > SUB_SPACE_REACH_M \
                        or poly.intersection(box).area < SUB_SPACE_INSIDE * box.area:
                    continue
                part = poly.intersection(box)
                rest = poly.difference(box).buffer(0)
                if part.geom_type != "Polygon" or rest.geom_type != "Polygon" or rest.area < 1.0:
                    continue
                if rest.interiors:
                    # 12 Nov 2026 (round-2 review, A2-FC6 / CODE-A1: real20's lift stood free inside the hall, which
                    # kept its whole polygon over it): the rest is cut open along the shortest line from the shaft to
                    # the room's edge (a CARVE_SLIT_M slit), so it is one simple polygon whose area is its own
                    rest = _open_hole(rest)
                    if rest is None:
                        continue
                new = dict(r, id=f"{r['id']}_{'lift' if sp['type'] == 'lift' else 'sub'}",
                           polygon=[[round(x, 4), round(y, 4)] for x, y in list(part.exterior.coords)[:-1]],
                           area_computed=round(part.area, 2))
                new.pop("sub_spaces", None)
                _as_sub_space(new, {"label_raw": sp["label"], "type": sp["type"],
                                    "how": f"its label '{sp['label']}' stands on the drawn outline {f.get('id')}"})
                rooms.append(new)
                r["polygon"] = [[round(x, 4), round(y, 4)] for x, y in list(rest.exterior.coords)[:-1]]
                r["area_computed"] = round(rest.area, 2)
                r["sub_spaces"] = [s for s in r.get("sub_spaces") or [] if s is not sp]
                if not r["sub_spaces"]:
                    r.pop("sub_spaces")
                f["build"] = False
                f.setdefault("details", {})["not_furniture"] = {
                    "as": sp["type"], "by": "sub_space", "room_id": new["id"],
                    "reason": f"the outline of {new['id']} '{new['label']}' (its label stands on it)"}
                edge = part.boundary.intersection(rest.boundary)
                lines = [g for g in getattr(edge, "geoms", [edge]) if g.geom_type == "LineString"]
                from shapely.ops import linemerge
                merged = linemerge(unary_union(lines)) if lines else None
                for k, ln in enumerate(straight_runs(merged)):
                    shaft_wall(new, ln, walls, f"the side of {new['id']} '{new['label']}' towards {r['id']}: not read, "
                                               f"inferred", wall_id=f"w_{new['id']}_{k + 1}")
                notes.append(f"{r['level_id']}: {new['id']} '{new['label']}' ({part.area:.1f} m2) carved out of "
                             f"{r['id']} on the drawn outline {f.get('id')} its label '{sp['label']}' stands on "
                             f"(inferred; {f.get('id')} is not furniture)")
                poly = rest
                break
    return notes


STACK_INSIDE = 0.8               # 19 Nov 2026 (review A3, OA3-02): a lift of another storey this much inside a room ...
STACK_LABEL_REACH_M = 0.6        # ... with the room's pending lift label this close to it is that lift on this storey


def carve_stacked_lifts(rooms: list[dict], walls: Optional[list] = None) -> list[str]:
    """19 Nov 2026 (review A3, OA3-02: real11's lift was built on one storey; on the others the landing strip and the
    lift box stayed one 1.60 x 4.72 m part, too long for a lift, and the ASANSOR label gave up): a room holding a pending
    lift sub-space (``sub_spaces``, type lift) whose label stands within ``STACK_LABEL_REACH_M`` of a lift shaft of
    another storey lying at least ``STACK_INSIDE`` inside the room is cut there: the lift's outline (its intersection
    with the room) becomes the lift on this storey, the room keeps the rest (one polygon of at least 1 m2, cut open when
    the lift stands free in it), an inferred shaft wall stands on the side towards the rest, and ``lift_doors`` gives it
    its landing door. The shaft must fit a lift (``fits_small_room``). Else, the room's own arm under the label: the room
    cut on a line through one of its inner corners, the piece holding the label fitting a lift (``_lift_arm``: real11
    L1-L6, the lift box beside the landing strip of one L-shaped part). Mutates; returns one line each."""
    from shapely.ops import linemerge, unary_union

    from wenart.ingest.generic import labels as LB

    lo, hi = LB.AREA_RANGES["lift"][:2]
    notes = []
    for r in list(rooms):
        pend = [s for s in r.get("sub_spaces") or [] if s.get("anchor") and s.get("type") == "lift"]
        if not pend or len(r.get("polygon") or []) < 3:
            continue
        poly = _poly(r)
        for sp in pend:
            at = Point(sp["anchor"][:2])
            best = None
            for x in rooms:
                if x.get("level_id") == r.get("level_id") or not _lift_label(x) or len(x.get("polygon") or []) < 3:
                    continue
                lp = _poly(x)
                share = poly.intersection(lp).area / lp.area if lp.area > 0 else 0.0
                if share >= STACK_INSIDE and lp.distance(at) <= STACK_LABEL_REACH_M and (best is None or share > best[0]):
                    best = (share, x, lp)
            # the stacked shaft's outline, or the room's own arm under the label: the smaller (the arm of a part can
            # hold the landing strip too)
            part = rest = x = None
            share = 0.0
            if best is not None:
                share, x, lp = best
                part = poly.intersection(lp)
                rest = poly.difference(lp).buffer(0)
                if part.geom_type != "Polygon" or rest.geom_type != "Polygon" or rest.area < 1.0 \
                        or not lo <= part.area <= hi or not fits_small_room(part, "lift"):
                    part = rest = x = None
            arm = _lift_arm(poly, at, lo, hi)
            if arm is not None and (part is None or arm[0].area < part.area - 0.05):
                part, rest = arm
                x = None
            if part is None:
                continue
            if rest.interiors:
                rest = _open_hole(rest)
                if rest is None:
                    continue
            new = dict(r, id=f"{r['id']}_lift", polygon=[[round(px, 4), round(py, 4)]
                                                         for px, py in list(part.exterior.coords)[:-1]],
                       area_computed=round(part.area, 2))
            new.pop("sub_spaces", None)
            if x is not None:
                how = (f"its label '{sp['label']}' stands by the lift {x['id']} of {x['level_id']}, which lies {share:.0%} "
                       f"inside {r['id']}: the stacked shaft")
                why = (f"the lift {x['id']} of {x['level_id']} stacks here (a lift shaft stands on every storey it "
                       f"serves); its outline cut out of {r['id']}")
            else:
                how = (f"its label '{sp['label']}' stands in the arm of {r['id']} beyond its inner corner, the size of a "
                       f"lift shaft")
                why = f"the arm of {r['id']} that holds the lift label is cut off at the room's inner corner"
            _as_sub_space(new, {"label_raw": sp["label"], "type": "lift", "how": how})
            new["adjusted_by_ai"] = {"by": "code", "rule": "stacked_lift" if x is not None else "lift_arm",
                                     "evidence": [x["id"]] if x is not None else [], "reason": why}
            rooms.append(new)
            r["polygon"] = [[round(px, 4), round(py, 4)] for px, py in list(rest.exterior.coords)[:-1]]
            r["area_computed"] = round(rest.area, 2)
            r["sub_spaces"] = [s for s in r.get("sub_spaces") or [] if s is not sp]
            if not r["sub_spaces"]:
                r.pop("sub_spaces")
            edge = part.boundary.intersection(rest.boundary)
            lines = [g for g in getattr(edge, "geoms", [edge]) if g.geom_type == "LineString"]
            joined = unary_union(lines) if lines else None
            merged = joined if joined is None or joined.geom_type == "LineString" else linemerge(joined)
            for k, ln in enumerate(straight_runs(merged)):
                shaft_wall(new, ln, walls, f"the side of {new['id']} '{new['label']}' towards {r['id']}: not read, "
                                           f"inferred ({how})", wall_id=f"w_{new['id']}_{k + 1}")
            notes.append(f"{r['level_id']}: {new['id']} '{new['label']}' ({part.area:.1f} m2) cut out of {r['id']}: "
                         f"{how} (inferred)")
            poly = rest
            break
    return notes


def _lift_arm(poly, at, lo: float, hi: float):
    """19 Nov 2026 (review A3, OA3-02): the arm of a room that holds a lift's label: the room cut along a line through
    one of its inner (reflex) corners, on one of the corner's two edge directions, into two polygons; the piece holding
    the label (within ``SUB_SPACE_REACH_M``) of a lift's area (``lo``-``hi``) that fits a shaft (``fits_small_room``),
    the rest one polygon of at least 1 m2. The smallest such piece; ``(part, rest)`` or None (pure)."""
    from shapely.geometry import LineString
    from shapely.ops import split

    pts = list(poly.exterior.coords)[:-1]
    n = len(pts)
    if n < 5:
        return None
    ccw = poly.exterior.is_ccw
    best = None
    for i in range(n):
        a, b, c = pts[i - 1], pts[i], pts[(i + 1) % n]
        cross = (b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])
        if (cross > 0) == ccw or abs(cross) < 1e-9:
            continue                                             # a convex corner (or none)
        for d in ((b[0] - a[0], b[1] - a[1]), (c[0] - b[0], c[1] - b[1])):
            L = math.hypot(*d)
            if L <= 1e-9:
                continue
            ux, uy = d[0] / L * 50.0, d[1] / L * 50.0
            try:
                pieces = list(split(poly, LineString([(b[0] - ux, b[1] - uy), (b[0] + ux, b[1] + uy)])).geoms)
            except (ValueError, TypeError):
                continue
            if len(pieces) != 2:
                continue
            for k in (0, 1):
                part, rest = pieces[k], pieces[1 - k]
                if part.distance(at) > SUB_SPACE_REACH_M or not lo <= part.area <= hi or rest.area < 1.0 \
                        or not fits_small_room(part, "lift"):
                    continue
                if best is None or part.area < best[0].area:
                    best = (part, rest)
    return best


SHARED_HALL_REACH_M = 0.55       # an opening joins two rooms when its centre lies this close to both (core walls run 0.4-0.8 m thick)
LANDING_MIN_M2 = 2.0             # 3 Nov 2026: a stair core room this much larger than its stair holds the shared hall ...
LANDING_MIN_WIDTH_M = 0.9        # ... when the rest is this wide (a walkable hall, not a strip beside the flight)
LANDING_NARROW_MIN_M = 0.60      # 13 Nov 2026: a narrower rest a drawn way in opens into, at least this wide (a person
#                                  passes), is still the landing: its own room, flagged ``narrow_landing``


def _width(g) -> float:
    """The width of a polygon: twice the radius of the largest circle inside it, to 5 mm (pure)."""
    lo, hi = 0.0, 20.0
    if g.is_empty:
        return 0.0
    while hi - lo > 0.005:
        mid = (lo + hi) / 2.0
        if g.buffer(-mid / 2.0).is_empty:
            hi = mid
        else:
            lo = mid
    return round(lo, 3)


def _stair_box(f: dict) -> Polygon:
    """The rectangle of a stair's footprint (centre, size, rotation)."""
    fp = f["footprint"]
    (cx, cy), (w, d) = fp["center"][:2], fp["size"][:2]
    a = math.radians(float(fp.get("rotation_deg") or 0.0))
    c, s = math.cos(a), math.sin(a)
    return Polygon([(cx + x * c - y * s, cy + x * s + y * c)
                    for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))])


SHAFT_WALL_T_M = 0.10            # 12 Nov 2026: the inferred shaft wall between a stair and its lift (a thin core wall)


def shaft_wall(room: dict, line, walls: Optional[list], why: str, wall_id: Optional[str] = None) -> Optional[dict]:
    """An inferred wall along ``line`` (a shapely line) closing a small room split off a face where no wall was read
    (a lift's shaft wall): ``SHAFT_WALL_T_M`` thick, ``inferred``, unverified, appended to ``walls`` (when given)."""
    if walls is None or line is None or line.length < 0.3:
        return None
    (ax, ay), (bx, by) = line.coords[0], line.coords[-1]
    ev = (room.get("evidence") or [{}])[0]
    w = {"id": wall_id or f"w_{room['id']}", "level_id": room["level_id"], "start": [round(ax, 4), round(ay, 4)],
         "end": [round(bx, 4), round(by, 4)], "thickness": SHAFT_WALL_T_M, "height": None, "exterior": False,
         "status": "unverified", "inferred": True,
         "evidence": [{"file": ev.get("file"), "method": "inferred", "confidence": 0.6, "entity": f"split:{room['id']}",
                       "rule": "sub_space_wall", "note": why, "region_id": ev.get("region_id")}]}
    walls.append(w)
    return w


def split_core_landings(rooms: list[dict], openings: list[dict], furniture: list[dict],
                        walls: Optional[list] = None) -> list[str]:
    """3 Nov 2026 (real10, user: "Understanding the building starts with the stairs in the shaft", "green marking is
    outside shared hall"; the plan draws no wall between the core stair and the landing in front of it and the lifts,
    so once the stair's middle wall and rails were no longer read as a wall across the stair, stair and landing were one
    face): a stair core room (``stair_cores``) whose part outside its stair's footprint is at least ``LANDING_MIN_M2``
    and ``LANDING_MIN_WIDTH_M`` wide (and touches the floor's lift, where the floor has one) is two rooms: the stair
    ('Merdiven', the footprint's part) and the shared hall in front of it ('Kat Holü' / 'Landing', type ``hall``,
    ``label_inferred`` method ``shared_hall``), joined by a virtual opening along their common edge (open: no wall is
    drawn there). Mutates ``rooms`` and ``openings``; returns one line per split."""
    from shapely.geometry import MultiLineString
    from shapely.ops import linemerge, unary_union

    from wenart.sheets import register as RG
    from wenart.sheets import titles as TI

    stairs = [f for f in furniture if f.get("type") == "stair" and (f.get("footprint") or {}).get("size")]
    notes = []
    # 12 Nov 2026: the cores holding a pending small room first, so the lift they give is there for the others to stack on
    for r in sorted(rooms, key=lambda x: not x.get("sub_spaces")):
        if (r.get("label_inferred") or {}).get("method") != "stair_core" or len(r.get("polygon") or []) < 3:
            continue
        poly = _poly(r)
        mine = [f for f in stairs if f.get("level_id") == r["level_id"] and _stair_box(f).intersects(poly)]
        if not mine:
            continue
        box = unary_union([_stair_box(f) for f in mine])
        stair_part = poly.intersection(box)
        rest = poly.difference(box)
        if stair_part.is_empty or rest.is_empty:
            continue
        # 12 Nov 2026 (review B-r10-L7-hall: real10's hall ran round the stair box in 3-6 cm slivers, its opening
        # 10 m 'wide' on a 0.15 m line): the parts of the room beside the stair thinner than ``HALL_SLIVER_M`` are the
        # stair's
        opened = rest.buffer(-HALL_SLIVER_M / 2.0, join_style=2).buffer(HALL_SLIVER_M / 2.0, join_style=2)
        opened = opened.intersection(rest)
        if not opened.is_empty:
            rest = opened
        parts = sorted(getattr(rest, "geoms", [rest]), key=lambda g: -g.area)
        hall = parts[0]
        if hall.geom_type != "Polygon" or hall.interiors or hall.area < LANDING_MIN_M2:
            # (a hole: a stair standing free inside the room, no landing in front of a core stair)
            continue
        narrow = None
        if hall.buffer(-LANDING_MIN_WIDTH_M / 2.0).is_empty:
            # 13 Nov 2026 (coordinator on real09: "a drawn room label never vanishes"; the hall in front of the core
            # stair came out 0.79 m wide and was merged into the stair room): the width threshold is for strips
            # beside a flight; a rest that a drawn door or opening of the floor opens into (its centre within
            # SHARED_HALL_REACH_M of the rest and nearer to it than to the stair) is the landing people arrive in, kept
            # as its own room when at least LANDING_NARROW_MIN_M wide, flagged ``narrow_landing`` (RC14 reports it)
            width = _width(hall)
            ways_in = [o for o in openings if o.get("level_id") == r["level_id"] and not o.get("virtual")
                       and o.get("center") and hall.distance(Point(o["center"][:2])) <= SHARED_HALL_REACH_M
                       and hall.distance(Point(o["center"][:2])) < box.distance(Point(o["center"][:2]))]
            if width < LANDING_NARROW_MIN_M or not ways_in:
                continue
            narrow = {"width_m": width, "min_m": LANDING_MIN_WIDTH_M, "ways_in": sorted(o["id"] for o in ways_in)}
        lvl_open = [o for o in openings if o.get("level_id") == r["level_id"]]
        small = sub_space_of(hall, r, rooms, lvl_open)
        if small is not None and not any(
                o.get("center") and not o.get("virtual") and stair_part.exterior.distance(Point(o["center"][:2])) <= 0.3
                and hall.exterior.distance(Point(o["center"][:2])) > 0.3 for o in lvl_open):
            small = None            # sealing the part off would leave the stair with no way to the floor
        lifts = [_poly(x) for x in rooms if x.get("level_id") == r["level_id"] and x.get("room_type") == "shaft"
                 and RG.LIFT_RE.search(TI.fold(str(x.get("label_raw") or x.get("label") or "")))]
        if small is None and lifts and not any(hall.distance(lp) <= SHARED_HALL_REACH_M for lp in lifts):
            continue
        # the stair keeps the footprint's part and the small leftovers (strips beside the flights, slivers)
        stair_poly = poly.difference(hall).buffer(0)
        if stair_poly.geom_type != "Polygon":
            stair_poly = max(stair_poly.geoms, key=lambda g: g.area)
        edge = stair_poly.boundary.intersection(hall.boundary)
        lines = [g for g in getattr(edge, "geoms", [edge]) if g.geom_type in ("LineString", "MultiLineString")]
        merged = linemerge(MultiLineString([c for g in lines for c in getattr(g, "geoms", [g])])) if lines else None
        if merged is None or merged.is_empty:
            continue
        cut = max(getattr(merged, "geoms", [merged]), key=lambda g: g.length)
        if cut.length < 0.6:
            continue
        turkish = str(r.get("label") or "") == "Merdiven"
        hall_id = f"{r['id']}_hall"
        r["polygon"] = [[round(x, 4), round(y, 4)] for x, y in list(stair_poly.exterior.coords)[:-1]]
        r["area_computed"] = round(stair_poly.area, 2)
        part = dict(r, id=hall_id, label="Kat Holü" if turkish else "Landing", room_type="hall",
                    polygon=[[round(x, 4), round(y, 4)] for x, y in list(hall.exterior.coords)[:-1]],
                    area_computed=round(hall.area, 2), has_documented_furniture=False,
                    label_inferred={"method": "shared_hall", "core": r["id"], "split_from": r["id"]})
        part.pop("sub_spaces", None)
        if narrow and small is None:
            part["narrow_landing"] = narrow
        # 12 Nov 2026 (round-2 review, CODE-A2): a pending sub-space whose label stands in the hall part goes with it,
        # so carve_sub_spaces can find its drawn outline (else RC14 names it)
        moved = [sp for sp in r.get("sub_spaces") or [] if sp.get("anchor")
                 and hall.distance(Point(sp["anchor"][:2])) <= SUB_SPACE_REACH_M
                 and (small is None or sp is not small.get("sub"))]
        if moved:
            part["sub_spaces"] = moved
            r["sub_spaces"] = [sp for sp in r.get("sub_spaces") or [] if all(sp is not m for m in moved)]
            if not r["sub_spaces"]:
                r.pop("sub_spaces")
        rooms.append(part)
        if small is not None:
            # 12 Nov 2026 (review, real11): the part is the small room its label (or the lift below) says, behind its
            # drawn shaft wall: no open joint, never a hall (``lift_doors`` gives a lift its landing door)
            _as_sub_space(part, small)
            part["id"] = f"{r['id']}_{'lift' if small['type'] == 'lift' else 'sub'}"
            part["label_inferred"].update(split_from=r["id"])
            for k, run in enumerate(straight_runs(merged)):
                shaft_wall(part, run, walls, f"the wall of {part['id']} '{part['label']}' towards the stair: not read "
                                             f"({small['how']}), inferred", wall_id=f"w_{part['id']}_{k + 1}")
            if small.get("sub") is not None:
                r["sub_spaces"] = [s for s in r.get("sub_spaces") or [] if s is not small["sub"]]
                if not r["sub_spaces"]:
                    r.pop("sub_spaces")
            notes.append(f"{r['level_id']}: the stair core {r['id']} ({poly.area:.1f} m2) holds its stair "
                         f"({stair_poly.area:.1f} m2) and {part['id']} '{part['label']}' ({hall.area:.1f} m2): "
                         f"{small['how']} (inferred); no open joint")
            continue
        (ax, ay), (bx, by) = cut.coords[0], cut.coords[-1]
        openings.append({"id": f"o_{hall_id}", "type": "opening", "level_id": r["level_id"], "wall_id": None,
                         "virtual": True, "line": [[round(ax, 4), round(ay, 4)], [round(bx, 4), round(by, 4)]],
                         "center": [round((ax + bx) / 2, 4), round((ay + by) / 2, 4)],
                         "width": round(math.dist((ax, ay), (bx, by)), 4),           # the line's length (review)
                         "height": None, "sill_height": None, "swing_side": None, "status": "verified",
                         "evidence": [{"file": (r.get("evidence") or [{}])[0].get("file"), "method": "inferred",
                                       "confidence": 0.8, "entity": f"split:{r['id']}",
                                       "note": f"virtual separator ({cut.length:.2f} m): the stair core's stair and "
                                               f"the shared hall in front of it, open (no wall drawn)",
                                       "region_id": (r.get("evidence") or [{}])[0].get("region_id")}]})
        notes.append(f"{r['level_id']}: the stair core {r['id']} ({poly.area:.1f} m2) holds its stair "
                     f"({stair_poly.area:.1f} m2) and the shared hall in front of it: {hall_id} '{rooms[-1]['label']}' "
                     f"({hall.area:.1f} m2, inferred), joined open along {cut.length:.2f} m"
                     + (f"; a narrow landing {narrow['width_m']:.2f} m (under {LANDING_MIN_WIDTH_M} m), kept: "
                        f"{', '.join(narrow['ways_in'])} open into it" if narrow else ""))
    return notes


def shared_halls(rooms: list[dict], openings: list[dict]) -> list[str]:
    """3 Nov 2026 (real10, user: "green marking is outside shared hall", "core stairs and elevators and that section is
    shaft usually"): an unnamed room the building's stair core (``stair_cores``) opens into (an opening or door whose
    centre lies within ``SHARED_HALL_REACH_M`` of both) is the floor's shared hall in front of the core: 'Kat Holü'
    ('Landing' on an English plan), type ``hall``, ``label_inferred`` (method ``shared_hall``); where the floor has a
    lift (a shaft labelled lift, asansör ...), the shared hall touches it too. The flats' own halls beside the core,
    behind a wall, are not joined to it. Returns one line per room."""
    from shapely.geometry import Point
    from shapely.ops import unary_union

    from wenart import building as B

    notes = []
    by_level: dict = {}
    for r in rooms:
        if len(r.get("polygon") or []) >= 3:
            by_level.setdefault(r["level_id"], []).append(r)
    for lid, level_rooms in by_level.items():
        cores = [r for r in level_rooms if (r.get("label_inferred") or {}).get("method") == "stair_core"]
        if not cores:
            continue
        turkish = any(B.is_turkish_label(str(x.get("label_raw") or "")) for x in level_rooms if x.get("label_raw"))
        level_openings = [o for o in openings if o.get("level_id") == lid and o.get("center")]
        # the core is the stair with the lifts (user: "core stairs and elevators and that section is shaft usually"):
        # where the floor has a lift, the shared hall touches it too (a flat's own hall beside the stair does not)
        from wenart.sheets import register as RG
        from wenart.sheets import titles as TI
        lifts = [_poly(x) for x in level_rooms if x.get("room_type") == "shaft"
                 and RG.LIFT_RE.search(TI.fold(str(x.get("label_raw") or x.get("label") or "")))]
        for core in cores:
            # 13 Nov 2026 (real09 L-1: once the core's landing was split off, the vestibule its 1.5 m opening joins lost
            # its 'Kat Holü'): the core is its stair with the landing split off it (``split_core_landings``)
            split = [_poly(x).buffer(0) for x in level_rooms
                     if (x.get("label_inferred") or {}).get("split_from") == core["id"]]
            cp = unary_union([_poly(core).buffer(0)] + split) if split else _poly(core)
            for r in level_rooms:
                if r is core or r.get("label_raw") or str(r.get("label") or "").strip().lower() not in GENERIC_LABELS:
                    continue
                rp = _poly(r)
                small = sub_space_of(rp, r, rooms, level_openings)
                if small is not None:
                    # 12 Nov 2026 (review, real11 / real10 L-2: a lift shaft named 'Kat Holü'): it is that small room
                    old = r.get("label")
                    _as_sub_space(r, small)
                    notes.append(f"{lid}: room {r['id']} ('{old}') beside the stair core {core['id']} is "
                                 f"'{r['label']}' ({rp.area:.1f} m2): {small['how']} (inferred), not the shared hall")
                    continue
                joined = [o for o in level_openings if cp.distance(Point(o["center"][:2])) <= SHARED_HALL_REACH_M
                          and rp.distance(Point(o["center"][:2])) <= SHARED_HALL_REACH_M]
                if not joined:
                    continue
                if lifts and not any(rp.distance(lp) <= SHARED_HALL_REACH_M for lp in lifts):
                    continue
                old = r.get("label")
                r["label"] = "Kat Holü" if turkish else "Landing"
                r["room_type"] = "hall"
                r["inferred"] = True
                r["label_inferred"] = {"method": "shared_hall", "core": core["id"]}
                notes.append(f"{lid}: room {r['id']} ('{old}') is the shared hall the stair core {core['id']} opens "
                             f"into ({len(joined)} opening(s)): '{r['label']}' (inferred)")
    return notes


HALL_SLIVER_M = 0.10             # 12 Nov 2026: a part of a stair core this thin beside the stair is the stair's
LIFT_DOOR_W_M = 0.90             # 4 Nov 2026 (UL306): a lift's landing door (a car door of 0.80-0.90 m) ...
LIFT_DOOR_H_M = 2.10             # ... this high, sliding
LIFT_WALL_REACH_M = 0.60         # a room, an opening or a wall this close to the shaft is beside it (core walls 0.2-0.5 m)
LIFT_DOOR_MIN_W_M = 0.60         # 12 Nov 2026 (review B-r21-lift: real21's 0.25 m gap between two shafts was taken): a
#                                  drawn opening is the landing door only when it is door-wide ...
LIFT_DOOR_MAX_W_M = 1.40         # ... and no wider than a lift door product (a single panel about 1.1 m, a wide automatic
#                                  door 1.4 m; review B2 FC-07: real21's second shaft took a 2.22 m gap)
# a machine room is no shaft: ``wenart.ingest.lift_words.machine_room`` (one test everywhere; review CODE-05)


def _machine(room: dict) -> bool:
    """19 Nov 2026 (review A3, OA3-03): a lift's machine room by the one test of the reader (``building.machine_room``:
    MAKİNA, MAK.DAİR., MAKN.DAİRESİ ...) or by the old words: never a lift shaft, it keeps its drawn door."""
    from wenart.ingest import lift_words as LW

    # 19 Nov 2026 (merge of reader A and the building-sense branch: one machine-room test): ``building.machine_room``
    # with the lift-named label's old words (MAHAL, MAKİNE, MOTOR ...) and the 'without a machine room' forms exempt
    # (makinesiz, makine dairesiz, MRL: review CODE-05), in ``lift_words.machine_room``
    return LW.machine_room(room.get("label_raw") or room.get("label") or "")


LIFT_LANDING_DEPTH_M = 1.20       # 19 Nov 2026 (review A3, POD-A3-02): the clear depth a landing door needs in front
LIFT_LANDING_TOL_M = 0.05         # ... less this drawing tolerance (real20's 1.20 m landing strip)
LIFT_DEPTH_MAX_M = 3.0            # ... measured up to this (deeper counts as this deep); a stretch of the room under
LIFT_DEPTH_SLIVER_M = 0.05        # this is a sliver of its outline (real20's 0.4 mm along the carved shaft), no depth
LIFT_DOOR_END_M = 0.05            # an inferred door keeps this far from its wall's ends


def _landing_sides(sp, rp, edge, blocks) -> list:
    """19 Nov 2026 (review A3, POD-A3-02): the straight sides of a lift shaft ``sp`` along its common ``edge`` with a room
    ``rp``, each with the clear depth in front of it: along three rays square to the side (its middle and a door's half
    width either way), the length of the first stretch inside the room that starts within ``LIFT_WALL_REACH_M`` of the
    shaft's face (the wall between), up to where it leaves the room or meets one of ``blocks`` (a stair's box, another
    shaft); the shortest of the three. A side with no room in front is left out. Returns ``[(depth, side)]`` (pure)."""
    from shapely.geometry import LineString
    from shapely.ops import unary_union

    blocked = unary_union(blocks) if blocks else None
    out = []
    for run in straight_runs(edge):
        if run.length < LIFT_DOOR_W_M + 0.1:
            continue
        (ax, ay), (bx, by) = run.coords[0], run.coords[-1]
        L = run.length
        ux, uy = (bx - ax) / L, (by - ay) / L
        mx, my = (ax + bx) / 2.0, (ay + by) / 2.0
        nx, ny = -uy, ux
        if sp.contains(Point(mx + nx * 0.05, my + ny * 0.05)):
            nx, ny = -nx, -ny
        hw = min(LIFT_DOOR_W_M, L - 0.1) / 2.0
        reach = LIFT_WALL_REACH_M + LIFT_DEPTH_MAX_M
        depths = []
        for k in (-1.0, 0.0, 1.0):
            px, py = mx + ux * k * hw, my + uy * k * hw
            ray = LineString([(px, py), (px + nx * reach, py + ny * reach)])
            inside = ray.intersection(rp)
            if blocked is not None and not inside.is_empty:
                inside = inside.difference(blocked)
            parts = sorted((g for g in getattr(inside, "geoms", [inside]) if g.geom_type == "LineString"
                            and g.length > LIFT_DEPTH_SLIVER_M), key=lambda g: Point(px, py).distance(g))
            if not parts or Point(px, py).distance(parts[0]) > LIFT_WALL_REACH_M + 0.01:
                depths = []
                break
            depths.append(min(parts[0].length, LIFT_DEPTH_MAX_M))
        if depths:
            out.append((round(min(depths), 3), run))
    return out


def _middle_side(edge, sides: list):
    """19 Nov 2026 (review A3, POD-A3-02): of ``sides`` (``_landing_sides``), the one the middle of the common ``edge``
    stands on, when the edge is no closed ring and its middle lies at least half a door from that side's ends (no
    corner); else None (pure)."""
    if edge is None or edge.is_empty or edge.geom_type != "LineString" or edge.is_ring or not sides:
        return None
    mid = edge.interpolate(0.5, normalized=True)
    for depth, run in sides:
        if run.distance(mid) <= 0.01:
            t = run.project(mid)
            if LIFT_DOOR_W_M / 2.0 <= t <= run.length - LIFT_DOOR_W_M / 2.0:
                return depth, run
    return None


def _clamped(axis, c, width: float):
    """19 Nov 2026 (POD-A3-02): the point of ``axis`` nearest ``c`` that keeps a door ``width`` wide inside the axis,
    ``LIFT_DOOR_END_M`` from each end (the axis' middle when it is shorter than that)."""
    lo, hi = width / 2.0 + LIFT_DOOR_END_M, axis.length - width / 2.0 - LIFT_DOOR_END_M
    d = (lo + hi) / 2.0 if lo > hi else min(max(axis.project(Point(c.x, c.y)), lo), hi)
    return axis.interpolate(d)


def _room_beyond(opening: dict, shaft: dict, rooms: list[dict]) -> Optional[dict]:
    """12 Nov 2026 (round-2 review, F2): the room on the other side of an opening in a shaft's wall: the nearest room of
    its level, no shaft, within ``LIFT_WALL_REACH_M`` of its centre (None when there is none)."""
    c = Point(opening["center"])
    best = None
    for r in rooms:
        if r is shaft or r.get("level_id") != shaft.get("level_id") or r.get("room_type") == "shaft" \
                or len(r.get("polygon") or []) < 3:
            continue
        d = _poly(r).distance(c)
        if d <= LIFT_WALL_REACH_M and (best is None or d < best[0]):
            best = (d, r)
    return best[1] if best else None


def lift_doors(rooms: list[dict], openings: list[dict], walls: list[dict], furniture: list[dict] = (),
               merged: Optional[list] = None, review: Optional[list] = None) -> list[str]:
    """4 Nov 2026 (lesson UL306, user on real10: "here is for the elevator (asansor) there should be a door for the
    elevator like sliding door again this is a general rule"): every lift shaft (a ``shaft`` room labelled lift,
    asansör ...; not its machine room) has its landing door on each floor: a door or opening drawn in its wall is that
    door, made sliding; else a sliding door ``LIFT_DOOR_W_M`` wide is inferred in the wall towards the room beside it
    (a common area first, then a hall or corridor, the longest common edge). Mutates ``openings``; returns one line
    per shaft.

    12 Nov 2026 (round-2 review, F2: real10's basement lift took a 1.26 m gap in the shear wall towards the stair as
    its landing door): of the drawn openings the one towards a common area first, then a hall or corridor, then the
    widest; never one whose room beyond is a stair (the landing is reached from the hall, not from a flight).


    13 Nov 2026 (review B3C-02, B3-FC07-SIDE / B3-REG-04 / BLD-08: real21's second shaft got its door on the corridor
    side by 5 cm of edge length while both drawn door frames face the stair hall; a gap the rule does not take stayed
    an open hole into the shaft, and a gap wider than a lift door got a second, inferred door on the same spot): the
    inferred door goes to the room that holds the stair (or that a neighbouring shaft's door faces), then to the room
    beside the most lift shafts (the lobby the lifts share), before a longer edge, edges within ``LIFT_EDGE_TIE_M``
    count as equal; it stands in a drawn gap towards that room when there is
    one (the gap narrowed to the door, the rest closed); every other drawn gap into the shaft is closed (the shaft is
    entered by its landing door only), each with a note.

    19 Nov 2026 (review A3, POD-A3-02 / M2: real20's inferred door was centred on the carved shaft's corner, half past
    its wall's end, facing the 0.40 m slot beside the stair, because the hall wraps the shaft and the common edge was
    the whole ring): the inferred door stands on one straight side of the shaft towards the chosen room with a landing's
    clear depth in front of it (``_landing_sides``: at least ``LIFT_LANDING_DEPTH_M``, a stair's flights or another
    shaft end it; the next room in the ranking is tried when no side of the first has that depth): the side the middle
    of the common edge stands on when that is no corner and the edge no ring (``_middle_side``), else the deepest;
    centred on that side and never past its wall's ends (``_clamped``). M3: never a flat's room (a bathroom beside the
    shaft is no landing); a stair room only after every hall, and only on a side with a landing in front of it clear of
    its flights (the F2 rule of the drawn gaps: never into a flight). M4: every gap merged into or closed by a landing
    door goes to ``merged`` (the building's
    ``openings_merged``) with ``corrected_by_ai``; a gap that opens onto nothing is never closed, it goes to ``review``
    (the building's ``needs_review``)."""
    from shapely.geometry import LineString

    from wenart import common_areas as CA
    from wenart.sheets import register as RG
    from wenart.sheets import titles as TI

    notes = []
    deferred: list = []                       # shafts with no hall beside them (FC-02)
    faced: dict = {}                          # level -> the rooms a shaft's landing door faces
    stair_rooms = {r["id"] for r in rooms if len(r.get("polygon") or []) >= 3 and any(
        f.get("type") == "stair" and f.get("level_id") == r.get("level_id") and (f.get("footprint") or {}).get("center")
        and _poly(r).contains(Point(f["footprint"]["center"][:2])) for f in furniture or ())}
    # the rooms beside several lift shafts: the lobby the core's lifts share (real21: both shafts' drawn door frames face
    # the stair hall west of them, each shaft also touching one flat-entrance strip)
    shafts = [x for x in rooms if x.get("room_type") == "shaft" and len(x.get("polygon") or []) >= 3
              and RG.LIFT_RE.search(TI.fold(str(x.get("label_raw") or x.get("label") or "")))
              and not _machine(x)]
    served = {r["id"]: sum(1 for x in shafts if x.get("level_id") == r.get("level_id")
                           and _poly(x).distance(_poly(r)) <= LIFT_WALL_REACH_M)
              for r in rooms if r.get("room_type") != "shaft" and len(r.get("polygon") or []) >= 3}
    for s in rooms:
        label = TI.fold(str(s.get("label_raw") or s.get("label") or ""))
        if s.get("room_type") != "shaft" or not RG.LIFT_RE.search(label) or _machine(s) \
                or len(s.get("polygon") or []) < 3:
            continue
        sp, lv = _poly(s), s["level_id"]
        # (19 Nov 2026, merge: the building-sense branch's MF6 / FC-02 case, real17's gap between a shop and the hall
        # beside the lift) a drawn opening is the shaft's only when it stands in the shaft's own wall
        drawn = [o for o in openings if o.get("level_id") == lv and not o.get("virtual") and o.get("center")
                 and o.get("type") in ("door", "opening") and sp.exterior.distance(Point(o["center"])) <= LIFT_WALL_REACH_M
                 and LIFT_DOOR_MIN_W_M <= float(o.get("width") or 0) <= LIFT_DOOR_MAX_W_M
                 and _in_shaft_wall(o, sp, walls)]
        # 12 Nov 2026 (review B2 FC-07, real21: the second shaft took a gap towards a flat's bedroom; real10 C0034, the
        # user: "a sliding lift door on each floor onto the shared hall"): a drawn opening is the landing door only
        # towards the landing: the room beyond it a common area, a hall or a corridor, never only a flat's room; the
        # landing side first, then the width nearest a lift door's
        ranked = []
        for o in drawn:
            nearest = _room_beyond(o, s, rooms)
            if nearest is not None and nearest.get("room_type") == "stair":
                # 12 Nov 2026 (round-2 review, F2): never a gap into the stair (the shear wall between lift and flight)
                notes.append(f"{lv}: {o['id']} in the wall of lift shaft {s['id']} opens into the stair {nearest['id']}: "
                             f"not its landing door")
                continue
            beyond = [r for r in rooms if r is not s and r.get("level_id") == lv and r.get("room_type") != "shaft"
                      and len(r.get("polygon") or []) >= 3
                      and _poly(r).distance(Point(o["center"])) <= LIFT_WALL_REACH_M]
            landing = any(CA.is_common_room(r) or str(r.get("room_type") or "") in ("hall", "corridor") for r in beyond)
            if beyond and not landing and all(str(r.get("room_type") or "") in FLAT_ROOM_TYPES for r in beyond):
                continue                     # it opens into a flat's room only: no landing door
            ranked.append(((landing, -abs(float(o.get("width") or 0) - LIFT_DOOR_W_M)), o))
        drawn = [o for _r, o in sorted(ranked, key=lambda x: x[0], reverse=True)]
        if drawn:
            o = drawn[0]
            # (12 Nov 2026, real10 C0034: the shaft's landing gap was read four times on stacked wall runs, 0.68-0.90 m;
            # one became the door and the others stayed openings in its place): a gap whose centre lies in the landing
            # door's span is the same opening read again, merged into the door
            again = [x for x in openings if x is not o and x.get("level_id") == lv and x.get("type") == "opening"
                     and not x.get("virtual") and x.get("center")
                     and Point(x["center"]).distance(Point(o["center"])) <= float(o.get("width") or 0) / 2.0]
            for x in again:
                openings.remove(x)
                if merged is not None:
                    merged.append(dict(x, merged_into=o["id"], corrected_by_ai={
                        "by": "code", "rule": "lift_door", "evidence": [s["id"], o["id"]],
                        "reason": f"the landing gap of lift shaft {s['id']} read again on stacked wall runs: one "
                                  f"opening, merged into its landing door {o['id']}"}))
            if again:
                o.setdefault("evidence", []).append({"file": (s.get("evidence") or [{}])[0].get("file") or "building.json",
                                                     "method": "derived", "confidence": 0.8, "rule": "lift_door",
                                                     "note": "the same landing gap read again on stacked wall runs, "
                                                             "merged into it: " + ", ".join(x["id"] for x in again)})
                notes.append(f"{lv}: {', '.join(x['id'] for x in again)} merged into the landing door {o['id']} (the "
                             f"same gap read again)")
            if o.get("operation") != "sliding" or o.get("type") != "door":
                if o.get("type") == "door":
                    # 13 Nov 2026 (review MF6, S1-20a): the drawn operation is kept, so a mark undone gives it back
                    o.setdefault("drawn_operation", o.get("operation"))
                    o.setdefault("drawn_operation_source", o.get("operation_source"))
                    o.setdefault("drawn_swing_side", o.get("swing_side"))
                o["type"], o["operation"], o["operation_source"], o["lift_door"] = "door", "sliding", "assumed", True
                o["swing_side"] = None
                o.setdefault("evidence", []).append({"file": (s.get("evidence") or [{}])[0].get("file") or "building.json",
                                                     "method": "inferred", "confidence": 0.8, "rule": "lift_door",
                                                     "note": f"the door of lift shaft {s['id']}: a sliding landing door"})
                notes.append(f"{lv}: {o['id']} in the wall of lift shaft {s['id']} is its sliding landing door")
            notes += _close_shaft_gaps(s, o, openings, rooms, merged, review)
            continue
        cands = []
        for r in rooms:
            # 19 Nov 2026 (review A3, M3): never a flat's room; a stair room only after every hall, and only on a side
            # with a landing's clear depth in front, clear of its flights (real14: the core's landing is the 'Merdiven'
            # room's; real10 L-2's gap into the flight beside the lift is no landing)
            # 19 Nov 2026 (merge, the building-sense branch's FC-01: real19's stair hall took the label of a small
            # shaft drawn in its corner, 'Şaft'): a room read as a shaft that holds the stair and is no lift is the
            # stair hall: a hall here
            stair_hall = r.get("room_type") == "shaft" and r["id"] in stair_rooms and not RG.LIFT_RE.search(
                TI.fold(str(r.get("label_raw") or r.get("label") or "")))
            # (merge, MF3 / REG-01 of the building-sense branch) never a unit's own use either: a shop's stair and door
            # are the shop's (real17's shops beside the lift)
            if r is s or r.get("level_id") != lv or (r.get("room_type") == "shaft" and not stair_hall) \
                    or str(r.get("room_type") or "") in FLAT_ROOM_TYPES or len(r.get("polygon") or []) < 3 \
                    or UNIT_USE_WORDS.search(TI.fold(str(r.get("label_raw") or r.get("label") or "")).lower()):
                continue
            rp = _poly(r)
            if sp.distance(rp) > LIFT_WALL_REACH_M:
                continue
            edge = sp.exterior.intersection(rp.buffer(LIFT_WALL_REACH_M))
            pieces = [g for g in getattr(edge, "geoms", [edge]) if g.geom_type == "LineString"]
            if not pieces:
                continue
            piece = max(pieces, key=lambda g: g.length)
            if piece.length < LIFT_DOOR_W_M + 0.1:
                continue
            rank = (r.get("room_type") != "stair", CA.is_common_room(r),
                    str(r.get("room_type") or "") in ("hall", "corridor") or stair_hall,
                    r["id"] in stair_rooms or r["id"] in faced.get(lv, ()), served.get(r["id"], 0),
                    round(piece.length / LIFT_EDGE_TIE_M))
            cands.append((rank, r, piece, edge))
        if not cands:
            deferred.append(s)           # (FC-02) the face the storey above or below uses, once every shaft is done
            continue
        cands.sort(key=lambda c: c[0], reverse=True)
        # 19 Nov 2026 (review A3, POD-A3-02): one straight side of the shaft, the one with the most clear depth in front
        blocks = [_stair_box(f) for f in furniture or () if f.get("type") == "stair" and f.get("level_id") == lv
                  and (f.get("footprint") or {}).get("center") and (f.get("footprint") or {}).get("size")]
        blocks += [_poly(x) for x in rooms if x is not s and x.get("level_id") == lv and x.get("room_type") == "shaft"
                   and len(x.get("polygon") or []) >= 3
                   and not (x["id"] in stair_rooms and not RG_LIFT(x))]     # (FC-01) a stair hall read as a shaft
        pick = None
        for _rank, rc, pc, ec in cands:
            sides = _landing_sides(sp, _poly(rc), ec, blocks)   # every piece of the common edge
            deep = [x for x in sides if x[0] >= LIFT_LANDING_DEPTH_M - LIFT_LANDING_TOL_M]
            if deep:
                # the side the common edge's middle stands on when that is no corner and the edge no ring (the shaft
                # beside its landing: real17's door towards the stair landing, not the flat's hall the edge also
                # touches), else the deepest
                mine = _middle_side(pc, deep)
                pick = (rc, mine if mine is not None else max(deep, key=lambda x: (x[0], x[1].length)))
                break
            if pick is None and sides and rc.get("room_type") != "stair":
                pick = (rc, max(sides, key=lambda x: (x[0], x[1].length)))
        if pick is None and all(c[1].get("room_type") == "stair" for c in cands):
            notes.append(f"{lv}: lift shaft {s['id']}: only a stair beside it, no landing in front of a side, no landing "
                         f"door inferred")
            continue
        if pick is None:
            _rank, room, piece, _e = next(c for c in cands if c[1].get("room_type") != "stair")
            runs = straight_runs(piece)
            side, depth = (max(runs, key=lambda g: g.length) if runs else piece), None
        else:
            room, (depth, side) = pick
        mid = side.interpolate(0.5, normalized=True)
        (ax0, ay0), (bx0, by0) = side.coords[0], side.coords[-1]
        ang = math.atan2(by0 - ay0, bx0 - ax0)
        near = [(LineString([w["start"], w["end"]]).distance(mid), w) for w in walls
                if w.get("level_id") == lv and w["start"] != w["end"]
                and abs(math.sin(math.atan2(w["end"][1] - w["start"][1], w["end"][0] - w["start"][0]) - ang)) <= 0.17]
        near = [(d, w) for d, w in near if d <= LIFT_WALL_REACH_M]
        if not near:
            notes.append(f"{lv}: lift shaft {s['id']}: no wall between it and {room['id']}, no landing door inferred")
            continue
        wall = min(near, key=lambda x: x[0])[1]
        axis = LineString([wall["start"], wall["end"]])
        c = axis.interpolate(axis.project(mid))
        piece = side
        # a drawn gap towards that room (too wide for a lift door, or once taken for something else) holds the door
        rp = _poly(room)
        gaps = [o for o in openings if o.get("level_id") == lv and o.get("type") == "opening" and not o.get("virtual")
                and o.get("center") and sp.exterior.distance(Point(o["center"])) <= LIFT_WALL_REACH_M
                and rp.distance(Point(o["center"])) <= LIFT_WALL_REACH_M
                and float(o.get("width") or 0.0) >= LIFT_DOOR_MIN_W_M]
        if gaps:
            g = max(gaps, key=lambda o: float(o.get("width") or 0.0))
            gw = next((w for w in walls if w.get("id") == g.get("wall_id")), None)
            if gw is not None and gw["start"] != gw["end"]:
                wall, axis = gw, LineString([gw["start"], gw["end"]])
            c = axis.interpolate(axis.project(Point(g["center"][:2])))
        width = round(min(LIFT_DOOR_W_M, piece.length - 0.1), 3)
        c = _clamped(axis, c, width)                 # 19 Nov 2026 (POD-A3-02): never past its wall's ends
        oid = f"d_{s['id']}_lift"
        openings.append({"id": oid, "type": "door", "level_id": lv, "wall_id": wall["id"],
                         "center": [round(c.x, 4), round(c.y, 4)], "width": width, "height": LIFT_DOOR_H_M,
                         "sill_height": 0.0, "swing_side": None, "operation": "sliding", "operation_source": "assumed",
                         "lift_door": True, "status": "unverified",
                         "evidence": [{"file": (s.get("evidence") or [{}])[0].get("file") or "building.json",
                                       "method": "inferred", "confidence": 0.6, "rule": "lift_door",
                                       "note": f"lift shaft {s['id']} has no door drawn: a {width:.2f} m sliding landing "
                                               f"door towards {room['id']} (UL306)"}]})
        notes.append(f"{lv}: lift shaft {s['id']}: a {width:.2f} m sliding landing door inferred towards {room['id']} "
                     f"({'common area' if CA.is_common_room(room) else room.get('room_type')}) in {wall['id']}"
                     + (f", on the shaft's side with {depth:.2f} m clear in front" if depth is not None else "")
                     + (f" (less than {LIFT_LANDING_DEPTH_M:.1f} m)" if depth is not None
                        and depth < LIFT_LANDING_DEPTH_M - LIFT_LANDING_TOL_M else ""))
        faced.setdefault(lv, set()).add(room["id"])
        notes += _close_shaft_gaps(s, openings[-1], openings, rooms, merged, review)
    for s in deferred:
        notes += _stacked_landing_door(s, shafts, rooms, openings, walls, merged, review)
    return notes


UNIT_USE_WORDS = re.compile(r"(?<![a-z])(?:dukkan\w*|magaza\w*|ofis\w*|buro\w*|isyeri|atolye|shop|office)(?![a-z])")


def _in_shaft_wall(o: dict, sp, walls: list[dict]) -> bool:
    """Whether opening ``o`` stands in the wall of the shaft polygon ``sp`` (pure): a probe across its wall, on one side,
    lands in the shaft (a wall's half thickness and 0.25 m out); with no wall, its centre within 0.35 m of the shaft."""
    w = next((x for x in walls if x.get("id") == o.get("wall_id")), None)
    c = o["center"][:2]
    if w is None or w["start"] == w["end"]:
        return sp.exterior.distance(Point(c)) <= 0.35
    (ax, ay), (bx, by) = w["start"][:2], w["end"][:2]
    ln = math.hypot(bx - ax, by - ay)
    nx, ny = -(by - ay) / ln, (bx - ax) / ln
    reach = float(w.get("thickness") or 0.15) / 2.0 + 0.25
    return any(sp.buffer(0.05).contains(Point(c[0] + k * nx * reach, c[1] + k * ny * reach)) for k in (1, -1))


def _stacked_landing_door(s: dict, shafts: list[dict], rooms: list[dict], openings: list[dict], walls: list[dict],
                          merged: Optional[list] = None, review: Optional[list] = None) -> list[str]:
    """19 Nov 2026 (merge of reader A and the building-sense branch, FC-02: real17's L0 lift had no hall beside it, the
    entrance hall in front of it read as a shaft, while the storeys above have the landing door on that face): a lift
    shaft with no hall beside it takes its landing door where a stacked shaft of another storey (centroids within
    ``LIFT_STACK_M``) has its landing door, when the room beyond that face is no flat's room and no unit's own use; the
    door is ``landing_stacked`` and a review record names the room it opens into. Mutates ``openings``; the notes."""
    from shapely.geometry import LineString

    from wenart.sheets import titles as TI

    sp, lv = _poly(s), s["level_id"]
    above = [o for o in openings if o.get("lift_door") and o.get("level_id") != lv and o.get("center")
             and any(x.get("level_id") == o.get("level_id") and _poly(x).centroid.distance(sp.centroid) <= LIFT_STACK_M
                     and _poly(x).exterior.distance(Point(o["center"][:2])) <= LIFT_WALL_REACH_M for x in shafts)]
    for o in sorted(above, key=lambda x: (str(x.get("level_id")), x["id"])):
        c = Point(o["center"][:2])
        if sp.exterior.distance(c) > LIFT_WALL_REACH_M:
            continue
        near = sorted((LineString([w["start"], w["end"]]).distance(c), w) for w in walls
                      if w.get("level_id") == lv and w["start"] != w["end"]
                      and LineString([w["start"], w["end"]]).distance(c) <= LIFT_WALL_REACH_M
                      and sp.distance(LineString([w["start"], w["end"]])) <= LIFT_WALL_REACH_M)
        if not near:
            continue
        wall = near[0][1]
        axis = LineString([wall["start"], wall["end"]])
        at = axis.interpolate(axis.project(c))
        room = next((r for r in rooms if r is not s and r.get("level_id") == lv and len(r.get("polygon") or []) >= 3
                     and (r.get("room_type") != "shaft" or not RG_LIFT(r))
                     and _poly(r).distance(at) <= LIFT_WALL_REACH_M and not _poly(r).equals(sp)), None)
        label = TI.fold(str((room or {}).get("label_raw") or (room or {}).get("label") or "")).lower()
        if room is None or str(room.get("room_type") or "") in FLAT_ROOM_TYPES or UNIT_USE_WORDS.search(label):
            continue
        width = round(min(LIFT_DOOR_W_M, axis.length - 0.1), 3)
        at = _clamped(axis, at, width)
        oid = f"d_{s['id']}_lift"
        door = {"id": oid, "type": "door", "level_id": lv, "wall_id": wall["id"],
                "center": [round(at.x, 4), round(at.y, 4)], "width": width, "height": LIFT_DOOR_H_M,
                "sill_height": 0.0, "swing_side": None, "operation": "sliding", "operation_source": "assumed",
                "lift_door": True, "landing_stacked": True, "status": "unverified",
                "evidence": [{"file": (s.get("evidence") or [{}])[0].get("file") or "building.json",
                              "method": "inferred", "confidence": 0.5, "rule": "lift_door",
                              "note": f"lift shaft {s['id']} has no hall beside it: its landing door stands where the "
                                      f"storey {o.get('level_id')} has it ({o['id']}), towards {room['id']} "
                                      f"'{room.get('label')}' ({room.get('room_type')})"}]}
        openings.append(door)
        why = (f"the lift shaft {s['id']}'s landing door {oid} stands where the storey {o.get('level_id')} has it, "
               f"onto {room['id']} '{room.get('label')}' ({room.get('room_type')}), a room not read as a hall: review "
               f"its type")
        if review is not None:
            review.append({"id": oid, "kind": "lift_landing_stacked", "reason": why, "room_id": room["id"],
                           "level_id": lv})
        return [f"{lv}: {why}"] + _close_shaft_gaps(s, door, openings, rooms, merged, review)
    return [f"{lv}: lift shaft {s['id']}: no hall beside it and no landing door of a stacked shaft to follow, no "
            f"landing door inferred"]


def RG_LIFT(r: dict) -> bool:
    """A room named a lift (the reader's lift word)."""
    from wenart.sheets import register as RG
    from wenart.sheets import titles as TI

    return bool(RG.LIFT_RE.search(TI.fold(str(r.get("label_raw") or r.get("label") or ""))))


LIFT_CAR_SIDES_M = ((0.9, 2.2), (1.1, 2.8))    # 13 Nov 2026: a lift car's outline (short side, long side) ...
LIFT_CAR_FILL = 0.4                 # ... the cars filling this share of the face at least ...
LIFT_CAR_MAX_M2 = 8.0               # ... the face at most this much a car (``labels.AREA_RANGES`` lift)
LIFT_CAR_GAP_ALIGN = 0.5            # a landing gap whose centre lies within this share of a car's width of the car's


LIFT_STACK_M = 0.30                 # 19 Nov 2026 (review A3, POD-A3-01): a shaft stacks when a shaft, a car or a lift word
#                                     stands this close to it on the storey above or below
DOOR_SIZE_TAG_RE = re.compile(r"^\s*(?:[KD]\s*\d{0,2}\s*[:\-.]?\s*)?(\d{2,3})\s*/\s*(\d{2,3})\s*$", re.IGNORECASE)
DOOR_SIZE_TAG_MIN_H_CM = 180        # ... a size tag this high (``core.DOOR_TAG_LOW_H_CM``, 'K:100/210') names a door
CAR_DOOR_LAYER_ROLES = ("door", "window", "glass")


def _door_made(x: dict) -> Optional[str]:
    """19 Nov 2026 (review A3, POD-A3-01: real09's 'car' f_L-1_013 was the box of an unequal double door's swing,
    ARC:48B1 and ARC:48C3 on 'kapı-pencere'): why an outline is a door's drawing and no lift car: it holds arcs (a
    door's swing; a car is drawn with straight lines), or its strokes are on a door, window or glass layer. None when
    neither."""
    from wenart.ingest.generic import layer_names as LN

    for e in x.get("evidence") or []:
        if not isinstance(e, dict):
            continue
        arcs = [i.strip() for i in str(e.get("entity") or "").split(",") if i.strip().upper().startswith("ARC:")]
        if arcs:
            return f"it holds the arc(s) {', '.join(arcs[:3])} (a door's swing)"
        role = LN.layer_role(e.get("layer"))
        if role in CAR_DOOR_LAYER_ROLES:
            return f"it is drawn on the {role} layer '{e.get('layer')}'"
    return None


def _level_order(levels) -> dict:
    """Level id -> storey order (by elevation where every level has one, else by the id's storey number)."""
    def num(lid: str) -> float:
        m = re.match(r"^L(-?\d+)", str(lid))
        return float(m.group(1)) if m else 0.0

    lv = [x for x in levels or () if isinstance(x, dict) and x.get("id")]
    if lv and all(isinstance(x.get("elevation"), (int, float)) for x in lv):
        keys = sorted({float(x["elevation"]) for x in lv})
        return {x["id"]: keys.index(float(x["elevation"])) for x in lv}
    keys = sorted({num(x["id"]) for x in lv})
    return {x["id"]: keys.index(num(x["id"])) for x in lv}


def _car_size(fp: dict) -> bool:
    sides = sorted(float(v) for v in (fp.get("size") or (0, 0)))
    return (LIFT_CAR_SIDES_M[0][0] <= sides[0] <= LIFT_CAR_SIDES_M[0][1]
            and LIFT_CAR_SIDES_M[1][0] <= sides[1] <= LIFT_CAR_SIDES_M[1][1])


def _stacks(cars: list, lv: str, rooms: list[dict], outlines: list[dict], levels) -> tuple[Optional[bool], str]:
    """19 Nov 2026 (review A3, POD-A3-01: real09's one-storey 'shaft' under two bedrooms): whether drawn lift cars stack:
    True when the storey above or below has a lift shaft, a room labelled lift or a car-size outline within
    ``LIFT_STACK_M`` of them; False when those storeys read rooms of another kind there and none of that; None when no
    storey above or below reads that place (a single drawing: real03's typical floor). Returns (verdict, why)."""
    from wenart.sheets import register as RG
    from wenart.sheets import titles as TI

    order = _level_order(levels)
    if lv not in order:
        return None, "no storey order"
    k = order[lv]
    near = [x for x, o in order.items() if abs(o - k) == 1]
    centres = [cp.centroid for _x, cp in cars]
    covered = []
    for al in near:
        for r in rooms:
            if r.get("level_id") != al or len(r.get("polygon") or []) < 3:
                continue
            rp = _poly(r)
            if not any(rp.distance(c) <= LIFT_STACK_M for c in centres):
                continue
            label = TI.fold(str(r.get("label_raw") or r.get("label") or ""))
            if (r.get("room_type") == "shaft" or RG.LIFT_RE.search(label)) and not _machine(r):
                return True, f"{al}: {r['id']} ({r.get('label') or r.get('room_type')})"
            if any(rp.contains(c) for c in centres):
                covered.append(f"{al}: {r['id']} ({r.get('label') or r.get('room_type')})")
        for x in outlines:
            if x.get("level_id") != al or not _car_size(x["footprint"]) or _door_made(x):
                continue
            if any(Point(x["footprint"]["center"][:2]).distance(c) <= LIFT_STACK_M for c in centres):
                return True, f"{al}: the car outline {x.get('id')}"
    if covered:
        return False, ", ".join(covered[:3])
    return None, "no storey above or below reads that place"


def _towards_nothing(o: dict, face: dict, rooms: list[dict]) -> bool:
    """19 Nov 2026 (review A3, M1): an opening with no room but ``face`` within ``LIFT_WALL_REACH_M`` of its centre opens
    to the outside (or onto nothing read)."""
    c = Point(o["center"][:2])
    return not any(r is not face and r.get("level_id") == face.get("level_id") and len(r.get("polygon") or []) >= 3
                   and _poly(r).distance(c) <= LIFT_WALL_REACH_M for r in rooms)


def _fp_poly(fp: dict):
    w, d = float(fp["size"][0]), float(fp["size"][1])
    a = math.radians(float(fp.get("rotation_deg") or 0.0))
    ux, uy, vx, vy = math.cos(a), math.sin(a), -math.sin(a), math.cos(a)
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    return Polygon([(cx + sx * w / 2.0 * ux + sy * d / 2.0 * vx, cy + sx * w / 2.0 * uy + sy * d / 2.0 * vy)
                    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])


def lift_cars(rooms: list[dict], symbols: list[dict], furniture: list[dict], openings: list[dict],
              walls: list[dict], texts: list[dict] = (), levels: list[dict] = ()) -> list[str]:
    """13 Nov 2026 (building-sense review S1-03b, real03: twin lift shafts drawn with their cars, guide rails,
    counterweights and telescopic doors but no ASANSÖR word, read as one 'Oda'): a face with no room word of its own
    (unlabelled or a generic 'Oda', of no type or a hall's) that holds drawn lift cars (untyped outlines, symbols or
    unknown pieces, of ``LIFT_CAR_SIDES_M``, together at least ``LIFT_CAR_FILL`` of the face, the face at most
    ``LIFT_CAR_MAX_M2`` a car), has no window and no hinged door, and whose doorless gaps each line up with a car and open
    onto a hall, is that many lift shafts: one 'Asansör' per car, split midway between the cars (an inferred shaft
    wall between them), each ``inferred`` with the cars and the gaps as evidence. ``lift_doors`` then makes each gap its
    shaft's sliding landing door. Mutates ``rooms`` and ``walls``; one line per face.

    19 Nov 2026 (review A3, POD-A3-01 / M1: real09's street-entrance vestibule became a one-storey lift shaft and its
    only street door was walled up; the 'car' was the box of an unequal double door's swing): an outline holding arcs or
    drawn on a door, window or glass layer is no car (``_door_made``); a face with a door size tag inside it
    (``texts``: ``{"text", "point", "level_id"}`` in the building frame), or with a gap or door that opens onto nothing
    (the outside), is no shaft; and the cars must stack (``_stacks``: a shaft, a lift word or a car within
    ``LIFT_STACK_M`` on the storey above or below; a storey that reads other rooms there refuses it). A refused face keeps
    its class, with a review line."""
    from shapely.geometry import LineString
    from shapely.ops import split

    from wenart import building as B
    from wenart import common_areas as CA

    notes = []
    outlines_all = [x for x in list(symbols or []) + list(furniture or []) if isinstance(x.get("footprint"), dict)
                    and (x.get("kind") in ("other", "unknown") if "kind" in x else x.get("type") == "unknown")]
    for r in list(rooms):
        label = r.get("label")
        if r.get("room_type") not in (None, "unknown", "hall", "other") or len(r.get("polygon") or []) < 3:
            continue
        if label and not B.generic_room_label(label) and not r.get("label_inferred"):
            continue
        if r.get("label_raw") and not B.generic_room_label(r.get("label_raw")):
            continue
        poly, lv = _poly(r), r["level_id"]
        outlines = [x for x in outlines_all if x.get("level_id") == lv]
        cars, refused = [], []
        for x in outlines:
            fp = x["footprint"]
            if not _car_size(fp):
                continue
            cp = _fp_poly(fp)
            if poly.buffer(0.05).contains(cp) and not any(cp.intersects(c[1]) for c in cars):
                why = _door_made(x)
                if why:
                    refused.append(f"{x.get('id')}: {why}")
                    continue
                cars.append((x, cp))
        for line in refused:
            notes.append(f"{lv}: {r['id']}: the car-size outline {line}: no lift car")
        n = len(cars)
        if not n or poly.area > n * LIFT_CAR_MAX_M2 or sum(c[1].area for c in cars) < LIFT_CAR_FILL * poly.area:
            continue
        near = [o for o in openings if o.get("level_id") == lv and o.get("center") and not o.get("virtual")
                and poly.exterior.distance(Point(o["center"])) <= LIFT_WALL_REACH_M]
        if any(o.get("type") == "window" or (o.get("type") == "door" and o.get("operation") in ("swing", "double"))
               for o in near):
            continue
        keep = f"{r['id']} keeps its class ({r.get('label') or r.get('room_type') or 'unlabelled'}), listed for review"
        tag = next((t for t in texts or () if t.get("level_id") == lv and t.get("point") is not None
                    and (m := DOOR_SIZE_TAG_RE.match(str(t.get("text") or "")))
                    and int(m.group(2)) >= DOOR_SIZE_TAG_MIN_H_CM and poly.contains(Point(t["point"][:2]))), None)
        if tag is not None:
            notes.append(f"{lv}: review: {r['id']} holds car-size outline(s) but the door size tag '{tag['text']}' "
                         f"stands inside it: no lift shaft; {keep}")
            continue
        out = [o for o in near if o.get("type") in ("opening", "door") and _towards_nothing(o, r, rooms)]
        if out:
            notes.append(f"{lv}: review: {r['id']} holds car-size outline(s) but its "
                         f"{', '.join(o['id'] for o in out)} opens onto nothing read (the outside): a lift never opens "
                         f"to the outside, no lift shaft; {keep}")
            continue
        stacked, why = _stacks(cars, lv, rooms, outlines_all, levels)
        if stacked is False:
            notes.append(f"{lv}: review: {r['id']} holds car-size outline(s) but the storey above or below reads "
                         f"other rooms there ({why}) and no shaft, lift word or car: a lift shaft stacks, no lift "
                         f"shaft; {keep}")
            continue
        gaps = []
        for x, cp in cars:
            c = cp.centroid
            hw = min(float(v) for v in x["footprint"]["size"]) / 2.0
            hit = [o for o in near if o.get("type") in ("opening", "door") and Point(o["center"]).distance(c)
                   <= max(float(v) for v in x["footprint"]["size"]) / 2.0 + LIFT_WALL_REACH_M
                   and min(abs(o["center"][0] - c.x), abs(o["center"][1] - c.y)) <= LIFT_CAR_GAP_ALIGN * 2 * hw]
            beyond = [_room_beyond(o, r, rooms) for o in hit]
            ok = [o for o, b in zip(hit, beyond) if b is not None and (str(b.get("room_type") or "") in ("hall", "corridor")
                                                                      or CA.is_common_room(b))]
            if not ok:
                break
            gaps.append(ok[0])
        if len(gaps) != n:
            continue
        cars.sort(key=lambda t: (round(t[1].centroid.x, 1), round(t[1].centroid.y, 1)))
        parts = [poly]
        cuts = []
        for (_x1, a), (_x2, b) in zip(cars, cars[1:]):
            ca, cb = a.centroid, b.centroid
            mx, my = (ca.x + cb.x) / 2.0, (ca.y + cb.y) / 2.0
            dx, dy = cb.x - ca.x, cb.y - ca.y
            L = math.hypot(dx, dy) or 1.0
            px, py = -dy / L * 20.0, dx / L * 20.0
            cut = LineString([(mx - px, my - py), (mx + px, my + py)])
            cuts.append(cut)
            nxt = []
            for p in parts:
                nxt.extend(g for g in split(p, cut).geoms if g.area > 0.5)
            parts = nxt
        if len(parts) != n:
            continue
        evid = [x.get("id") for x, _cp in cars] + [g.get("id") for g in gaps]
        made = []
        for k, part in enumerate(sorted(parts, key=lambda p: (round(p.centroid.x, 1), round(p.centroid.y, 1)))):
            room = r if k == 0 else dict(r, id=f"{r['id']}_lift{k + 1}")
            room["polygon"] = [[round(x, 4), round(y, 4)] for x, y in list(part.exterior.coords)[:-1]]
            room["area_computed"] = round(part.area, 2)
            _as_sub_space(room, {"label_raw": "Asansör", "type": "lift",
                                 "how": f"a drawn lift car ({', '.join(str(e) for e in evid[:n])}) with its landing gap "
                                        f"onto the hall ({', '.join(str(e) for e in evid[n:])}); no lift word drawn"})
            room["adjusted_by_ai"] = {"by": "code", "rule": "lift_cars", "evidence": evid,
                                      "reason": f"{n} drawn lift car(s) in one face: one lift shaft each"}
            if k:
                rooms.append(room)
            made.append(room["id"])
        for k, cut in enumerate(cuts):
            seg = cut.intersection(poly)
            for j, ln in enumerate(straight_runs(seg)):
                shaft_wall(r, ln, walls, f"between the lift shafts {', '.join(made)}: not read, inferred",
                           wall_id=f"w_{r['id']}_cars{k + 1}_{j + 1}")
        notes.append(f"{lv}: {r['id']} ({poly.area:.1f} m2, no room word) holds {n} drawn lift car(s) with landing "
                     f"gaps onto the hall: {n} lift shaft(s) {', '.join(made)} (inferred)")
    return notes


SHAFT_SLIVER_M = 0.50            # 13 Nov 2026 (S1-10b): a 'door' this narrow beside a lift's landing door is part of it ...
SHAFT_SLIVER_REACH_M = 0.30      # ... standing this close to it (the stacked faces of a core wall: one wall band)


def _shaft_extra(o: dict, sp, door: dict) -> bool:
    """13 Nov 2026 (building-sense review S1-10b, real10's 2nd basement: a 1.26 m 'window' to the stair on a buried
    storey and a 0.33 m sliver beside the landing door): besides the gaps, a window read from the gap's lines standing
    in the shaft's own wall band (its centre within ``SHAFT_WINDOW_REACH_M`` of the shaft), and a door narrower than
    ``SHAFT_SLIVER_M`` within ``SHAFT_SLIVER_REACH_M`` of the landing door, are no openings of the shaft; a door drawn
    as a door stays."""
    c, w = o["center"][:2], float(o.get("width") or 0.0)
    if o.get("type") == "door":
        return w < SHAFT_SLIVER_M and Point(c).distance(Point(door["center"][:2])) <= \
            float(door.get("width") or 0.0) / 2.0 + w / 2.0 + SHAFT_SLIVER_REACH_M
    if o.get("type") != "window":
        return False
    ev = o.get("evidence") or []
    derived = o.get("status") == "unverified" or any(isinstance(e, dict) and (
        e.get("method") in ("derived", "inferred") or e.get("rule") in ("gap_behind_furniture", "no_glass")) for e in ev)
    return derived and sp.exterior.distance(Point(c)) <= SHAFT_WINDOW_REACH_M


SHAFT_WINDOW_REACH_M = 0.40      # ... a window this close to the shaft stands in its wall band (core walls 0.2-0.5 m)


LIFT_EDGE_TIE_M = 0.5            # 13 Nov 2026: two rooms' edges along a lift shaft this close in length are equal


def _close_shaft_gaps(shaft: dict, door: dict, openings: list[dict], rooms: list[dict],
                      merged: Optional[list] = None, review: Optional[list] = None) -> list[str]:
    """13 Nov 2026 (review B3C-02): the drawn gaps (type opening) into a lift shaft other than its landing ``door``
    are closed: removed from ``openings``, one note each; a gap the door stands in is the door's (narrowed to it).
    Returns the notes.

    19 Nov 2026 (review A3, M1 / M4): a gap that opens onto nothing (no room but the shaft beside it: the outside) is
    never closed: it stays and goes to ``review`` (a lift never opens to the outside: the shaft or the gap is misread);
    every closed gap goes to ``merged`` with ``corrected_by_ai`` (rule, reason, the shaft; ``merged_into`` the door when
    the door stands in it)."""
    sp, lv = _poly(shaft), shaft["level_id"]
    out = []
    for o in [x for x in openings if x is not door and x.get("level_id") == lv and not x.get("virtual")
              and x.get("center") and sp.exterior.distance(Point(x["center"][:2])) <= LIFT_WALL_REACH_M
              and (x.get("type") == "opening" or _shaft_extra(x, sp, door))]:
        beyond = [r["id"] for r in rooms if r is not shaft and r.get("level_id") == lv
                  and len(r.get("polygon") or []) >= 3 and _poly(r).distance(Point(o["center"][:2])) <= LIFT_WALL_REACH_M]
        mine = math.dist(o["center"][:2], door["center"][:2]) <= float(o.get("width") or 0.0) / 2.0 + 0.05
        w = float(o.get("width") or 0)
        if not beyond and not mine:
            why = (f"the {o.get('type')} {o['id']} ({w:.2f} m) in the wall of lift shaft {shaft['id']} opens onto nothing "
                   f"read (the outside): a lift never opens to the outside; kept, the shaft or the opening is misread")
            out.append(f"{lv}: review: {why}")
            if review is not None:
                review.append({"id": o["id"], "kind": "lift_shaft_gap", "reason": why, "room_id": shaft["id"],
                               "level_id": lv})
            continue
        openings.remove(o)
        src = (shaft.get("evidence") or [{}])[0].get("file") or "building.json"
        what = ("holds this landing door: narrowed to it, the rest closed" if mine else
                "into the shaft closed: a lift shaft is entered by its landing door only")
        door.setdefault("evidence", []).append({"file": src, "method": "inferred", "confidence": 0.7,
                                                "rule": "lift_shaft_gap",
                                                "note": f"the drawn gap {o['id']} ({w:.2f} m) {what}"})
        if merged is not None:
            merged.append(dict(o, merged_into=door["id"] if mine else None, corrected_by_ai={
                "by": "code", "rule": "lift_shaft_gap", "evidence": [shaft["id"], door["id"]],
                "reason": (f"the landing door {door['id']} of lift shaft {shaft['id']} stands in it: narrowed to the "
                           f"door, the rest closed" if mine else
                           f"towards {', '.join(beyond)}: a lift shaft is entered by its landing door {door['id']} "
                           f"only, the wall runs on")}))
        out.append(f"{lv}: the gap {o['id']} ({w:.2f} m) into lift shaft {shaft['id']} "
                   + (f"holds its landing door {door['id']}: narrowed to it" if mine else
                      f"closed (towards {', '.join(beyond)}; the shaft is entered by its landing door "
                      f"{door['id']} only)"))
    return out


FIRE_WORDS = ("YANGIN", "FIRE ESCAPE", "FIRE STAIR", "KACIS", "ACIL CIKIS", "EMERGENCY", "NOTTREPPE", "FLUCHT",
              "SECOURS")
FLAT_ROOM_TYPES = ("bedroom", "living", "kitchen", "dining", "bathroom", "wc", "study", "dressing")
FIRE_DOOR_REACH_M = 0.35         # an opening this close to the stair room's wall joins it to the room beyond ...
PASSAGE_MIN_M = 0.75             # ... when it is a door or a gap at least this wide (a 0.64 m gap is a window's)


def fire_stairs(rooms: list[dict], openings: list[dict], furniture: list[dict]) -> list[str]:
    """4 Nov 2026 (lessons UL307, UL312, user on real10: "There should have been fire escape ladders here, and a door to
    reach there via Hall halls the common use area", "Fire stairs should be like fire stairs not like regular stairs"):
    the fire escape stairs of a building: a stair named for it (``FIRE_WORDS`` in its room's or a room's label beside
    it), or, on a floor with a common area, a stair other than the core stair (``stair_core``, or the one beside the
    lift) whose room opens into no flat's room. Its piece gets ``details.stair.fire_escape`` (the build gives it
    hard-wearing treads and steel rails) and its room is a common area. Mutates the pieces and rooms; one line each."""
    from wenart import common_areas as CA
    from wenart.sheets import register as RG
    from wenart.sheets import titles as TI

    notes = []
    by_level: dict = {}
    for f in furniture:
        if f.get("type") == "stair" and (f.get("footprint") or {}).get("center"):
            by_level.setdefault(f.get("level_id"), []).append(f)
    for lv, stairs in by_level.items():
        lrooms = [r for r in rooms if r.get("level_id") == lv and len(r.get("polygon") or []) >= 3]
        polys = {r["id"]: _poly(r) for r in lrooms}

        def room_of(f):
            c = Point(f["footprint"]["center"][:2])
            return next((r for r in lrooms if polys[r["id"]].contains(c)), None)

        lifts = [polys[r["id"]] for r in lrooms if r.get("room_type") == "shaft"
                 and RG.LIFT_RE.search(TI.fold(str(r.get("label_raw") or r.get("label") or "")))]
        common = any(CA.is_common_room(r) for r in lrooms)
        for f in stairs:
            room = room_of(f)
            if room is None:
                continue
            words = TI.fold(" ".join(str(room.get(k) or "") for k in ("label", "label_raw")))
            named = any(w in words for w in FIRE_WORDS)
            # with a lift on the floor the core stair is the one beside it (real10: the fire stair spans the floors too
            # and was read as a stair core); without one, the stair core
            core = any(polys[room["id"]].distance(lp) <= 1.0 for lp in lifts) if lifts else \
                (room.get("label_inferred") or {}).get("method") == "stair_core" and len(stairs) < 2
            if not named and (len(stairs) < 2 or not common or core):
                continue
            # a stair opening into a flat's rooms is the flat's own stair (a duplex), never the building's fire stair
            flat = []
            for o in openings:
                if o.get("level_id") != lv or not o.get("center") or o.get("virtual"):
                    continue
                c = Point(o["center"])
                if polys[room["id"]].exterior.distance(c) > FIRE_DOOR_REACH_M:
                    continue
                for r in lrooms:
                    if r is not room and polys[r["id"]].exterior.distance(c) <= FIRE_DOOR_REACH_M \
                            and str(r.get("room_type") or "") in FLAT_ROOM_TYPES \
                            and (o.get("type") == "door" or (o.get("type") == "opening"
                                                             and float(o.get("width") or 0) >= PASSAGE_MIN_M)):
                        flat.append(r["id"])
            if flat and not named:
                continue
            st = f.setdefault("details", {}).setdefault("stair", {})
            st["fire_escape"] = True
            st["fire_escape_reason"] = ("named a fire stair" if named else
                                        "a stair beside the core stair, off the common area, into no flat's room")
            room["room_subtype"] = CA.COMMON_SUBTYPE
            notes.append(f"{lv}: {f['id']} in {room['id']} is a fire escape stair ({st['fire_escape_reason']}): "
                         f"hard-wearing treads, steel rails; its room a common area")
    return notes


ENTRANCE_DOOR_REACH_M = 0.35     # 4 Nov 2026 (UL316): a door this close to the walls of a common hall and of a flat's room
# the rooms a flat's entrance door opens into (a basement's shelter or store from the common hall is no flat)
DWELLING_TYPES = ("hall", "corridor", "living", "kitchen", "dining", "bedroom", "study")


def flat_entrance_doors(rooms: list[dict], openings: list[dict]) -> list[str]:
    """4 Nov 2026 (real10, user: "the Doors to this place from the actual living areas needs to be outside doors, kinda
    doors you can use to enter to the flat"; lesson UL316): a door between a common area (``common_areas``) and a flat's
    room (``DWELLING_TYPES``, no common area) is that flat's entrance door: ``door_style`` ``entrance``
    (the thick panelled entrance door with its frame, never an inside door model), ``flat_entrance: true``. A door
    whose style the documents or the architect named keeps it. Returns a note per door."""
    from wenart import common_areas as CA

    notes = []
    by_level: dict = {}
    for r in rooms:
        if len(r.get("polygon") or []) >= 3:
            by_level.setdefault(r.get("level_id"), []).append(r)
    for o in openings:
        if o.get("type") != "door" or o.get("virtual") or not o.get("center"):
            continue
        lrooms = by_level.get(o.get("level_id")) or []
        c = Point(o["center"][:2])
        near = [r for r in lrooms if Polygon(r["polygon"]).exterior.distance(c) <= ENTRANCE_DOOR_REACH_M]
        common = [r for r in near if CA.is_common_room(r)]
        flat = [r for r in near if not CA.is_common_room(r) and str(r.get("room_type") or "") in DWELLING_TYPES]
        if not common or not flat:
            continue
        if o.get("door_style") and o.get("door_style") != "entrance":
            continue
        o["door_style"] = "entrance"
        o["flat_entrance"] = True
        o.setdefault("door_decision", {"kind": "entrance", "rule": "flat_entrance (UL316)",
                                       "reason": f"the door from the common area {common[0]['id']} into "
                                                 f"{flat[0]['id']}: the flat's entrance door"})
        notes.append(f"{o.get('level_id')}: {o['id']} from the common area {common[0]['id']} into {flat[0]['id']} is "
                     f"the flat's entrance door (a thick panelled entrance door with its frame)")
    return notes


GARAGE_DOOR_MIN_M = 2.2          # 4 Nov 2026 (UL320): a car passes an opening this wide (a car is 1.8-1.9 m)
GARAGE_DOOR_H_M = 2.25           # a sectional garage door's clear height when the drawing gives none
GARAGE_DOOR_REACH_M = 0.35       # the opening's centre this close to the garage's outline


def garage_doors(rooms: list[dict], openings: list[dict], walls: list[dict]) -> list[str]:
    """4 Nov 2026 (real07, user: "If this is a garage (garaj) there will be a car inside and that car should be able to
    enter and exit, it requires a different kind of a door it requires a garage door"; lesson UL320): the widest
    opening of at least ``GARAGE_DOOR_MIN_M`` in a garage's outer walls (a window, a gap or a door the reading typed) is
    its sectional garage door: ``type`` door, ``door_type`` garage_sectional, from the floor, ``GARAGE_DOOR_H_M`` high
    unless drawn. Returns a note per garage."""
    notes = []
    outer = {w["id"] for w in walls if w.get("exterior")}
    for r in rooms:
        if r.get("room_type") != "garage" or len(r.get("polygon") or []) < 3:
            continue
        ring = Polygon(r["polygon"]).exterior
        cands = [o for o in openings if o.get("level_id") == r.get("level_id") and o.get("center")
                 and not o.get("virtual") and float(o.get("width") or 0.0) >= GARAGE_DOOR_MIN_M
                 and (o.get("wall_id") in outer or not o.get("wall_id"))
                 and ring.distance(Point(o["center"][:2])) <= GARAGE_DOOR_REACH_M]
        if not cands or any(o.get("door_type") == "garage_sectional" for o in cands):
            continue
        o = max(cands, key=lambda x: float(x.get("width") or 0.0))
        was = o.get("type")
        o["type"] = "door"
        o["door_type"] = "garage_sectional"
        o["operation"], o["operation_source"] = "unknown", "assumed"     # the schema's ways; door_type says sectional
        o["sill_height"] = 0.0
        if not o.get("height") or float(o.get("height") or 0.0) < 2.0:
            o["height"] = GARAGE_DOOR_H_M
        o["door_decision"] = {"kind": "garage_sectional", "rule": "garage_door (UL320)",
                              "reason": f"the widest outer opening ({float(o['width']):.2f} m) of the garage {r['id']}: "
                                        f"its sectional garage door, so a car can drive in and out"}
        notes.append(f"{r.get('level_id')}: {o['id']} ({was}, {float(o['width']):.2f} m) in the outer wall of the garage "
                     f"{r['id']} is its sectional garage door")
    return notes


CHAMFER_DEG = (20.0, 70.0)        # 4 Nov 2026 (UL328): a boundary this far off the walls' directions is a chamfer ...
CHAMFER_LEN_M = (1.0, 2.5)        # ... this long
CHAMFER_T_M = 0.10                # the frame's wall
CHAMFER_SIDES = {"hall"}, {"living", "dining", "kitchen", "other"}


def chamfer_frames(rooms: list[dict], openings: list[dict], walls: list[dict]) -> list[str]:
    """4 Nov 2026 (real10, user: "This door frame must be angled and same needs to be on the other mirror side";
    lesson UL328): a room boundary the drawing leaves open on a chamfer (a virtual separator ``CHAMFER_DEG`` off the
    walls' directions, ``CHAMFER_LEN_M`` long) between a hall and a living room is a glazed double door in its frame along
    the chamfer: a thin inferred wall on the line holding the door. Every such chamfer gets it (the mirrored flat too).
    Returns a note per frame."""
    import math as _m

    notes = []
    by_level: dict = {}
    for r in rooms:
        if len(r.get("polygon") or []) >= 3:
            by_level.setdefault(r.get("level_id"), []).append(r)
    dirs: dict = {}
    for w in walls:
        dx, dy = w["end"][0] - w["start"][0], w["end"][1] - w["start"][1]
        if dx or dy:
            dirs.setdefault(w.get("level_id"), []).append(_m.degrees(_m.atan2(dy, dx)) % 90.0)
    n = 0
    for o in openings:
        if not o.get("virtual") or not o.get("line") or o.get("chamfer_frame"):
            continue
        (x0, y0), (x1, y1) = o["line"]
        length = _m.hypot(x1 - x0, y1 - y0)
        if not CHAMFER_LEN_M[0] <= length <= CHAMFER_LEN_M[1]:
            continue
        ang = _m.degrees(_m.atan2(y1 - y0, x1 - x0)) % 90.0
        main = sorted(dirs.get(o.get("level_id")) or [0.0])[len(dirs.get(o.get("level_id")) or [0.0]) // 2]
        off = min(abs(ang - main) % 90.0, 90.0 - abs(ang - main) % 90.0)
        if not CHAMFER_DEG[0] <= off <= CHAMFER_DEG[1]:
            continue
        mid = ((x0 + x1) / 2.0, (y0 + y1) / 2.0)
        nx, ny = -(y1 - y0) / length, (x1 - x0) / length
        sides = []
        for sgn in (1, -1):
            q = Point(mid[0] + sgn * nx * 0.3, mid[1] + sgn * ny * 0.3)
            sides.append(next((r for r in by_level.get(o.get("level_id")) or [] if Polygon(r["polygon"]).contains(q)),
                              None))
        types = {str((r or {}).get("room_type") or "") for r in sides}
        if not (types & CHAMFER_SIDES[0] and types & CHAMFER_SIDES[1]):
            continue
        n += 1
        lv = o.get("level_id")
        wid = f"w_{lv}_chamfer_{n:02d}"
        walls.append({"id": wid, "level_id": lv, "start": [x0, y0], "end": [x1, y1], "thickness": CHAMFER_T_M,
                      "exterior": False, "status": "unverified", "inferred": True,
                      "evidence": [{"file": "building.json", "method": "inferred", "confidence": 0.6,
                                    "rule": "chamfer_frame", "text": "the frame of the glazed door on the chamfer (UL328)"}]})
        o.update({"virtual": False, "type": "door", "wall_id": wid, "width": round(length - 0.04, 3),
                  "center": [round(mid[0], 4), round(mid[1], 4)],
                  "rotation_deg": round(_m.degrees(_m.atan2(y1 - y0, x1 - x0)), 3), "glazed": True,
                  "door_type": "french", "door_style": "glazed", "leaves": 2, "chamfer_frame": True,
                  "door_decision": {"kind": "french", "rule": "chamfer_frame (UL328)",
                                    "reason": "the open chamfer between the hall and the living room: a glazed double "
                                              "door in its frame along the chamfer"}})
        o.pop("line", None)
        notes.append(f"{lv}: {o['id']} on the chamfer between {sides[0]['id']} and {sides[1]['id']} "
                     f"({length:.2f} m): a glazed double door in its frame along it")
    return notes


DRESSING_WORDS = ("GIYINME", "SOYUNMA", "DRESSING", "WALK-IN", "WALK IN", "GARDEROBE", "ANKLEIDE", "VESTIDOR")
PASSAGE_REACH_M = 0.35


def open_passages(rooms: list[dict], openings: list[dict], levels: list[dict]) -> list[str]:
    """4 Nov 2026 (real07 L1, user: "there is no wall here and the section on the left of that none existing wall is
    giyinme soyunma, a place for dressing"; lesson UL327): a doorless opening between a dressing room and the room it
    belongs to is an open passage up to the ceiling (no wall over it): its height is the level's ceiling height.
    Returns a note per passage."""
    from wenart.sheets import titles as TI

    ceil = {lv["id"]: float(lv.get("ceiling_height") or 2.7) for lv in levels or []}
    notes = []
    for o in openings:
        if o.get("type") != "opening" or o.get("virtual") or not o.get("center"):
            continue
        c = Point(o["center"][:2])
        near = [r for r in rooms if r.get("level_id") == o.get("level_id") and len(r.get("polygon") or []) >= 3
                and Polygon(r["polygon"]).exterior.distance(c) <= PASSAGE_REACH_M]
        dress = [r for r in near if any(w in TI.fold(" ".join(str(r.get(k) or "") for k in ("label", "label_raw")))
                                        for w in DRESSING_WORDS)]
        if not dress or len(near) < 2:
            continue
        h = ceil.get(o.get("level_id"), 2.7)
        o["height"] = round(h, 3)
        o["open_passage"] = True
        notes.append(f"{o.get('level_id')}: {o['id']} into the dressing room {dress[0]['id']}: an open passage up to the "
                     f"ceiling ({h:.2f} m), no wall over it")
    return notes

