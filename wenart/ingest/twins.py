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
                and (poly.contains(Point(f["footprint"]["center"])) or _holds_most(poly, f["footprint"]))]
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


SHARED_HALL_REACH_M = 0.55       # an opening joins two rooms when its centre lies this close to both (core walls run 0.4-0.8 m thick)
LANDING_MIN_M2 = 2.0             # 3 Nov 2026: a stair core room this much larger than its stair holds the shared hall ...
LANDING_MIN_WIDTH_M = 0.9        # ... when the rest is this wide (a walkable hall, not a strip beside the flight)


def _stair_box(f: dict) -> Polygon:
    """The rectangle of a stair's footprint (centre, size, rotation)."""
    fp = f["footprint"]
    (cx, cy), (w, d) = fp["center"][:2], fp["size"][:2]
    a = math.radians(float(fp.get("rotation_deg") or 0.0))
    c, s = math.cos(a), math.sin(a)
    return Polygon([(cx + x * c - y * s, cy + x * s + y * c)
                    for x, y in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))])


def split_core_landings(rooms: list[dict], openings: list[dict], furniture: list[dict]) -> list[str]:
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
    for r in list(rooms):
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
        parts = sorted(getattr(rest, "geoms", [rest]), key=lambda g: -g.area)
        hall = parts[0]
        if hall.geom_type != "Polygon" or hall.interiors or hall.area < LANDING_MIN_M2 \
                or hall.buffer(-LANDING_MIN_WIDTH_M / 2.0).is_empty:
            # (a hole: a stair standing free inside the room, no landing in front of a core stair)
            continue
        lifts = [_poly(x) for x in rooms if x.get("level_id") == r["level_id"] and x.get("room_type") == "shaft"
                 and RG.LIFT_RE.search(TI.fold(str(x.get("label_raw") or x.get("label") or "")))]
        if lifts and not any(hall.distance(lp) <= SHARED_HALL_REACH_M for lp in lifts):
            continue
        # the stair keeps the footprint's part and the small leftovers (strips beside the flights)
        stair_poly = unary_union([stair_part] + parts[1:]).buffer(0)
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
        rooms.append(dict(r, id=hall_id, label="Kat Holü" if turkish else "Landing", room_type="hall",
                          polygon=[[round(x, 4), round(y, 4)] for x, y in list(hall.exterior.coords)[:-1]],
                          area_computed=round(hall.area, 2), has_documented_furniture=False,
                          label_inferred={"method": "shared_hall", "core": r["id"], "split_from": r["id"]}))
        (ax, ay), (bx, by) = cut.coords[0], cut.coords[-1]
        openings.append({"id": f"o_{hall_id}", "type": "opening", "level_id": r["level_id"], "wall_id": None,
                         "virtual": True, "line": [[round(ax, 4), round(ay, 4)], [round(bx, 4), round(by, 4)]],
                         "center": [round((ax + bx) / 2, 4), round((ay + by) / 2, 4)], "width": round(cut.length, 4),
                         "height": None, "sill_height": None, "swing_side": None, "status": "verified",
                         "evidence": [{"file": (r.get("evidence") or [{}])[0].get("file"), "method": "inferred",
                                       "confidence": 0.8, "entity": f"split:{r['id']}",
                                       "note": f"virtual separator ({cut.length:.2f} m): the stair core's stair and "
                                               f"the shared hall in front of it, open (no wall drawn)",
                                       "region_id": (r.get("evidence") or [{}])[0].get("region_id")}]})
        notes.append(f"{r['level_id']}: the stair core {r['id']} ({poly.area:.1f} m2) holds its stair "
                     f"({stair_poly.area:.1f} m2) and the shared hall in front of it: {hall_id} '{rooms[-1]['label']}' "
                     f"({hall.area:.1f} m2, inferred), joined open along {cut.length:.2f} m")
    return notes


def shared_halls(rooms: list[dict], openings: list[dict]) -> list[str]:
    """3 Nov 2026 (real10, user: "green marking is outside shared hall", "core stairs and elevators and that section is
    shaft usually"): an unnamed room the building's stair core (``stair_cores``) opens into (an opening or door whose
    centre lies within ``SHARED_HALL_REACH_M`` of both) is the floor's shared hall in front of the core: 'Kat Holü'
    ('Landing' on an English plan), type ``hall``, ``label_inferred`` (method ``shared_hall``); where the floor has a
    lift (a shaft labelled lift, asansör ...), the shared hall touches it too. The flats' own halls beside the core,
    behind a wall, are not joined to it. Returns one line per room."""
    from shapely.geometry import Point

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
            cp = _poly(core)
            for r in level_rooms:
                if r is core or r.get("label_raw") or str(r.get("label") or "").strip().lower() not in GENERIC_LABELS:
                    continue
                rp = _poly(r)
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


LIFT_DOOR_W_M = 0.90             # 4 Nov 2026 (UL306): a lift's landing door (a car door of 0.80-0.90 m) ...
LIFT_DOOR_H_M = 2.10             # ... this high, sliding
LIFT_WALL_REACH_M = 0.60         # a room, an opening or a wall this close to the shaft is beside it (core walls 0.2-0.5 m)
MACHINE_RE_WORDS = ("MAHAL", "MAKINE", "MACHINE", "MOTOR", "MASCHINEN")   # a lift's machine room is no shaft


def lift_doors(rooms: list[dict], openings: list[dict], walls: list[dict]) -> list[str]:
    """4 Nov 2026 (lesson UL306, user on real10: "here is for the elevator (asansor) there should be a door for the
    elevator like sliding door again this is a general rule"): every lift shaft (a ``shaft`` room labelled lift,
    asansör ...; not its machine room) has its landing door on each floor: a door or opening drawn in its wall is that
    door, made sliding; else a sliding door ``LIFT_DOOR_W_M`` wide is inferred in the wall towards the room beside it
    (a common area first, then a hall or corridor, the longest common edge). Mutates ``openings``; returns one line
    per shaft."""
    from shapely.geometry import LineString

    from wenart import common_areas as CA
    from wenart.sheets import register as RG
    from wenart.sheets import titles as TI

    notes = []
    for s in rooms:
        label = TI.fold(str(s.get("label_raw") or s.get("label") or ""))
        if s.get("room_type") != "shaft" or not RG.LIFT_RE.search(label) or any(w in label for w in MACHINE_RE_WORDS) \
                or len(s.get("polygon") or []) < 3:
            continue
        sp, lv = _poly(s), s["level_id"]
        drawn = [o for o in openings if o.get("level_id") == lv and not o.get("virtual") and o.get("center")
                 and o.get("type") in ("door", "opening") and sp.exterior.distance(Point(o["center"])) <= LIFT_WALL_REACH_M]
        if drawn:
            o = max(drawn, key=lambda o: float(o.get("width") or 0))
            if o.get("operation") != "sliding" or o.get("type") != "door":
                o["type"], o["operation"], o["operation_source"], o["lift_door"] = "door", "sliding", "assumed", True
                o["swing_side"] = None
                o.setdefault("evidence", []).append({"file": (s.get("evidence") or [{}])[0].get("file") or "building.json",
                                                     "method": "inferred", "confidence": 0.8, "rule": "lift_door",
                                                     "note": f"the door of lift shaft {s['id']}: a sliding landing door"})
                notes.append(f"{lv}: {o['id']} in the wall of lift shaft {s['id']} is its sliding landing door")
            continue
        cands = []
        for r in rooms:
            if r is s or r.get("level_id") != lv or r.get("room_type") == "shaft" or len(r.get("polygon") or []) < 3:
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
            rank = (CA.is_common_room(r), str(r.get("room_type") or "") in ("hall", "corridor"), piece.length)
            cands.append((rank, r, piece))
        if not cands:
            notes.append(f"{lv}: lift shaft {s['id']}: no hall beside it, no landing door inferred")
            continue
        _rank, room, piece = max(cands, key=lambda c: c[0])
        mid = piece.interpolate(0.5, normalized=True)
        near = [(LineString([w["start"], w["end"]]).distance(mid), w) for w in walls
                if w.get("level_id") == lv and w["start"] != w["end"]]
        near = [(d, w) for d, w in near if d <= LIFT_WALL_REACH_M]
        if not near:
            notes.append(f"{lv}: lift shaft {s['id']}: no wall between it and {room['id']}, no landing door inferred")
            continue
        wall = min(near, key=lambda x: x[0])[1]
        axis = LineString([wall["start"], wall["end"]])
        c = axis.interpolate(axis.project(mid))
        width = round(min(LIFT_DOOR_W_M, piece.length - 0.1), 3)
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
                     f"({'common area' if CA.is_common_room(room) else room.get('room_type')}) in {wall['id']}")
    return notes


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
        o["operation"], o["operation_source"] = "sectional", "assumed"
        o["sill_height"] = 0.0
        if not o.get("height") or float(o.get("height") or 0.0) < 2.0:
            o["height"] = GARAGE_DOOR_H_M
        o["door_decision"] = {"kind": "garage_sectional", "rule": "garage_door (UL320)",
                              "reason": f"the widest outer opening ({float(o['width']):.2f} m) of the garage {r['id']}: "
                                        f"its sectional garage door, so a car can drive in and out"}
        notes.append(f"{r.get('level_id')}: {o['id']} ({was}, {float(o['width']):.2f} m) in the outer wall of the garage "
                     f"{r['id']} is its sectional garage door")
    return notes

