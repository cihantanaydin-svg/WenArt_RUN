"""Type inference for drawn pieces the documents leave unclear (docs/milestone11.md §6, CLAUDE.md furniture rules,
contract §17.2): an unknown footprint that holds other pieces is a rug or a group outline; one that matches a
type's size table, room and position rule gets that type, marked ``inferred``. Pure; owner: track B.

What: ``infer_types(building) -> [proposal]`` looks at every built drawn piece of type ``unknown``;
``apply_inferences(building, proposals) -> building`` returns a copy with them applied. A proposal is
``{"piece_id", "type", "reason", "confidence", "evidence": {...}, "front_deg"?: float, "build"?: false}``.

Why: CLAUDE.md (9 Oct 2026): "Footprint clear but type unclear -> the AI infers the type from size, room and
neighbours, marks it inferred and lists it in the report. It never stays an unexplained box." real02 had 56 built
unknown boxes (U17): rug and zone outlines read as one 13 m² piece (U9), pieces the two AI passes disagreed on.

How (deterministic; the agent may confirm or change the type later on the plan crop):

1. **Outline**: an unknown footprint whose polygon holds the centre of at least one other piece of its room is a rug
   or zone outline drawn around a group. The furniture schema has no rug type, so it is not built (``build:
   false``, proposal type ``rug``); the decor rules lay rugs under the groups (``decor.rugs_for_room``).
1b. **Detail**: an unknown footprint drawn >= 60 % inside a larger typed piece (a sink bowl in a counter leg) is a
   detail of that piece: not built (proposal type ``detail``).
2. **One type**: the types the footprint can be are those whose product size range fits it (size table, +15 %,
   either way), that the room type allows (``schemas.allowed_types``, plus stand-alone lamps, plants and side
   tables) and whose position rule holds (``schemas.ORIENTATION_RULES``: a back-to-wall type has a side on a wall;
   a free piece has a side on a wall or a group partner near). Exactly one -> that type (confidence 0.6).
1c. **Mark** (real03): an unknown footprint that fits no type and is smaller than ``MARK_SIDE_M`` both ways or
   thinner than ``MARK_THIN_M`` is a drawn mark (a tap, a valve, a threshold line): not built (type ``detail``).
3. **One named**: several fit, but exactly one of them was named by an AI pass (``type_candidates``) -> that type
   (confidence 0.55).
4. The front of an inferred type with a front: the side opposite the only side on a wall; a seat faces its nearest
   partner; else none (the builder's side, listed as assumed).

Nothing else is guessed: an unknown piece with no single answer stays unknown and is listed.
"""
from __future__ import annotations

import copy
import math
from typing import Optional

from shapely.geometry import Point

from wenart import geometry as G
from wenart.furniture import placer, plausibility as PL, schemas

OUTLINE_TYPE = "rug"              # what an outline holding other pieces is (a decor type, not a furniture type)
WALL_SIDE_M = 0.10                # a side this close to the room outline stands on a wall
CONF_ONE = 0.6
CONF_NAMED = 0.55
CONF_OUTLINE = 0.7
SKIP_TYPES = ("stair", "unknown", "wall_cabinet")


OUTLINE_MIN_M2 = 1.0              # an outline (rug, zone) is at least this large ...
HELD_INSIDE = 0.5                 # ... and holds >= half of each smaller piece it is drawn around


def outline_holds(poly, mates: list[dict]) -> list[str]:
    """Ids of the pieces an outline ``poly`` is drawn around: smaller pieces whose centre lies in it with at least
    ``HELD_INSIDE`` of their area (none when the outline is smaller than ``OUTLINE_MIN_M2``)."""
    if poly.area < OUTLINE_MIN_M2:
        return []
    out = []
    for f in mates:
        try:
            other = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if other.area >= poly.area or not poly.contains(Point(f["footprint"]["center"])):
            continue
        if other.intersection(poly).area >= HELD_INSIDE * other.area:
            out.append(f["id"])
    return sorted(out)


DETAIL_TYPE = "detail"            # a drawn part inside a typed piece (not a furniture type: not built)
# real03 (10 Oct 2026): a symbol smaller than this both ways (a tap, a valve) or thinner than MARK_THIN_M (a
# threshold, a shelf line) that fits no type is a drawn mark, not a piece: not built (rule 1c).
MARK_SIDE_M = 0.30
MARK_THIN_M = 0.20
DETAIL_INSIDE = 0.6


def _host_of(poly, mates: list[dict]) -> Optional[dict]:
    """The built, typed (larger) piece that holds >= ``DETAIL_INSIDE`` of ``poly`` (real02: the sink bowls inside
    the counter legs, typed bar stools by one AI pass), else None."""
    for f in mates:
        if f.get("type") in ("unknown", "stair") or f.get("build") is False:
            continue
        try:
            other = placer.drawn_piece(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if other.area > poly.area and poly.intersection(other).area >= DETAIL_INSIDE * poly.area:
            return f
    return None


def _rooms(building: dict) -> dict[str, dict]:
    return {r["id"]: r for r in building.get("rooms") or [] if len(r.get("polygon") or []) >= 3}


def _sides(poly) -> list[tuple[tuple[float, float], tuple[float, float]]]:
    c = list(poly.exterior.coords)
    return [(c[i], c[i + 1]) for i in range(len(c) - 1)]


def _wall_sides(piece: placer.Piece, ring) -> list[int]:
    """Indices of the footprint's sides (local order: front, right, back, left) within ``WALL_SIDE_M`` of the room
    outline along most of their length."""
    out = []
    for k, (a, b) in enumerate(_sides(piece.polygon())):
        pts = [((a[0] * (1 - t) + b[0] * t), (a[1] * (1 - t) + b[1] * t)) for t in (0.2, 0.5, 0.8)]
        if all(ring.distance(Point(p)) <= WALL_SIDE_M for p in pts):
            out.append(k)
    return out


def _outward_deg(piece: placer.Piece, side: tuple) -> float:
    mid = ((side[0][0] + side[1][0]) / 2.0, (side[0][1] + side[1][1]) / 2.0)
    return math.degrees(math.atan2(mid[1] - piece.center[1], mid[0] - piece.center[0]))


def _snap_quarter(deg: float, rotation: float) -> float:
    """``deg`` snapped to the nearest of the footprint's four side normals."""
    base = G.front_direction_deg(rotation)
    k = round(G.normalise_angle(deg - base) / 90.0) % 4
    return round(G.normalise_angle(base + 90.0 * k), 3)


def _front_for(ftype: str, piece: placer.Piece, ring, partners: list[placer.Piece]) -> Optional[float]:
    if ftype in schemas.FRONTLESS_TYPES:
        return None
    rule = schemas.orientation_rule(ftype)
    if rule["back"] == "free" and partners:
        host = min(partners, key=lambda h: (round(h.polygon().distance(piece.polygon()), 6), h.index))
        target = host.polygon().centroid
        return _snap_quarter(math.degrees(math.atan2(target.y - piece.center[1], target.x - piece.center[0])),
                             piece.rotation_deg)
    sides = _sides(piece.polygon())
    near = _wall_sides(piece, ring)
    if len(near) == 1:
        return _snap_quarter(_outward_deg(piece, sides[near[0]]) + 180.0, piece.rotation_deg)
    return None


SQUARE_TYPES = ("potted_plant", "side_table", "floor_lamp", "bar_stool", "chair", "office_chair")
PARTNER_ONLY = ("chair", "bar_stool", "office_chair")   # a seat is placed by its table, never by a wall alone
SQUARE_ASPECT = 1.3               # these are about as wide as deep (a 1.03 x 0.69 m outline is no plant)


def _shape_ok(ftype: str, size) -> bool:
    a, b = sorted(float(v) for v in size)
    return ftype not in SQUARE_TYPES or b <= SQUARE_ASPECT * a + 1e-9


def _position_ok(ftype: str, piece: placer.Piece, on_wall: bool, others: list[tuple[str, placer.Piece]]) -> bool:
    rule = schemas.orientation_rule(ftype)
    if rule["back"] in ("wall", "wall_or_group"):
        return on_wall
    if rule["back"] == "free" and rule["partners"]:
        poly = piece.polygon()
        near = any(t in rule["partners"] and o.polygon().distance(poly) <= rule["partner_m"] for t, o in others)
        return near if ftype in PARTNER_ONLY else (on_wall or near)
    return True


def _evidence(item: dict, reason: str, confidence: float) -> dict:
    src = (item.get("evidence") or [{}])[0]
    ev = {"file": src.get("file") or "building.json", "method": "inferred", "confidence": confidence,
          "rule": "furniture.infer", "text": reason}
    for k in ("page", "entity", "region_id"):
        if src.get(k) is not None:
            ev[k] = src[k]
    return ev


def infer_types(building: dict) -> list[dict]:
    """``[{"piece_id", "type", "reason", "confidence", "evidence": {...}}]`` (proposals; the building is unchanged)."""
    rooms = _rooms(building)
    furniture = building.get("furniture") or []
    out = []
    for item in furniture:
        if item.get("type") != "unknown" or item.get("source") != "from_documents" or item.get("build") is False:
            continue
        room = rooms.get(item.get("room_id"))
        if room is None:
            continue
        piece = placer.drawn_piece(item)
        poly = piece.polygon()
        mates = [f for f in furniture if f.get("room_id") == room["id"] and f["id"] != item["id"]]
        held = outline_holds(poly, mates)
        if held and not any(f["type"] in schemas.FIXED_TYPES for f in mates if f["id"] in held):
            reason = (f"outline {piece.size[0]:.2f} x {piece.size[1]:.2f} m around {len(held)} other piece(s) "
                      f"({', '.join(held[:6])}): a rug or zone outline, not a piece (not built; the decor rules lay "
                      f"rugs under the groups)")
            out.append({"piece_id": item["id"], "type": OUTLINE_TYPE, "build": False, "reason": reason,
                        "confidence": CONF_OUTLINE, "evidence": _evidence(item, reason, CONF_OUTLINE)})
            continue
        ring = _room_ring(room)
        on_wall = bool(_wall_sides(piece, ring))
        others = [(f["type"], placer.drawn_piece(f, k)) for k, f in enumerate(mates)
                  if f.get("type") != "unknown" and f.get("build") is not False]
        if held:
            continue                       # an outline around fixed equipment: a counter run (split at ingest)
        host = _host_of(poly, mates)
        if host is not None:
            reason = (f"drawn inside {host['type']} {host['id']} ({DETAIL_INSIDE:.0%} or more of it): a detail of that "
                      f"piece (a sink bowl, an appliance front), not a piece of its own (not built)")
            out.append({"piece_id": item["id"], "type": DETAIL_TYPE, "build": False, "reason": reason,
                        "confidence": CONF_OUTLINE, "evidence": _evidence(item, reason, CONF_OUTLINE)})
            continue
        size_now = sorted(float(v) for v in item["footprint"]["size"])
        if (size_now[1] < MARK_SIDE_M or size_now[0] < MARK_THIN_M) and not any(
                PL._fits(t, size_now) for t in PL._size_table() if t not in SKIP_TYPES):
            reason = (f"{size_now[1]:.2f} x {size_now[0]:.2f} m fits no type and is "
                      + (f"smaller than {MARK_SIDE_M} m both ways" if size_now[1] < MARK_SIDE_M
                         else f"thinner than {MARK_THIN_M} m")
                      + ": a drawn mark (a tap, a valve, a threshold or shelf line), not a piece (not built)")
            out.append({"piece_id": item["id"], "type": DETAIL_TYPE, "build": False, "reason": reason,
                        "confidence": CONF_OUTLINE, "evidence": _evidence(item, reason, CONF_OUTLINE)})
            continue
        types = PL.room_types(building, room)
        rtype = " + ".join(types)
        if any(t in ("other", "unknown") for t in types):
            # A room of no known purpose (real02's play and rest room is "other") says nothing about its pieces: the
            # room rule does not narrow the types there.
            allowed = {t for t in schemas.SIZE_OPTIONS if t not in schemas.CHILD_ONLY_TYPES}
        else:
            allowed = PL.allowed_in(building, room)
        size = [float(v) for v in item["footprint"]["size"]]
        sized = [t for t in allowed if t not in SKIP_TYPES and t in PL._size_table() and PL._fits(t, size)
                 and _shape_ok(t, size)]
        fits = sorted(t for t in sized if _position_ok(t, piece, on_wall, others))
        answers = {c.get("type") for c in item.get("type_candidates") or []}
        named = sorted(answers & set(fits))
        # An AI pass named another type that fits the size and the room: the piece is ambiguous (real02's sofas in
        # the open kitchen: kitchen_island / sofa); the agent decides on the plan crop, nothing is inferred.
        rivals = sorted((answers & set(sized)) - set(fits[:1] if len(fits) == 1 else named[:1]))
        if rivals:
            continue
        if len(fits) == 1:
            ftype, conf = fits[0], CONF_ONE
            reason = (f"{ftype}: the only type whose size range fits {size[0]:.2f} x {size[1]:.2f} m, that a "
                      f"{rtype} room holds and whose position rule holds here")
        elif len(named) == 1:
            ftype, conf = named[0], CONF_NAMED
            reason = (f"{ftype}: named by an AI pass and the only named type that fits the size ({size[0]:.2f} x "
                      f"{size[1]:.2f} m), the {rtype} room and the position (others fitting: "
                      f"{', '.join(t for t in fits if t != ftype)})")
        else:
            continue
        partners = [o for t, o in others if t in schemas.orientation_rule(ftype)["partners"]]
        prop = {"piece_id": item["id"], "type": ftype, "reason": reason, "confidence": conf,
                "evidence": _evidence(item, reason, conf)}
        if item.get("front_deg") is None:
            front = _front_for(ftype, piece, ring, partners)
            if front is not None:
                prop["front_deg"] = front
        out.append(prop)
    return out


def _room_ring(room: dict):
    """The room outline as a shapely ring (CCW)."""
    from shapely.geometry import Polygon
    from shapely.geometry.polygon import orient

    poly = orient(Polygon(room["polygon"]), 1.0)
    return (poly if poly.is_valid else poly.buffer(0)).exterior


def set_front(item: dict, front_deg: float) -> None:
    """Give a piece a front: the footprint turned by whole quarter turns so its local -Y faces ``front_deg``
    (``placer.front_frame``: same rectangle, size swapped on an odd turn)."""
    rot, size = placer.front_frame(item["footprint"], front_deg)
    item["footprint"] = dict(item["footprint"], rotation_deg=round(rot, 3), size=[round(size[0], 4),
                                                                                   round(size[1], 4)])
    item["front_deg"] = round(G.normalise_angle(front_deg), 3)


def apply_inferences(building: dict, proposals: list[dict]) -> dict:
    """A copy of the building with the proposals applied (``inferred: true``, evidence method ``inferred``)."""
    b = copy.deepcopy(building)
    by_id = {f["id"]: f for f in b.get("furniture") or []}
    for prop in proposals:
        item = by_id.get(prop["piece_id"])
        if item is None:
            continue
        ev = dict(prop.get("evidence") or _evidence(item, prop["reason"], float(prop.get("confidence", 0.5))))
        item.setdefault("evidence", []).append(ev)
        item["inferred"] = True
        item["inferred_reason"] = prop["reason"]
        if prop.get("build") is False or prop["type"] not in schemas.SIZE_OPTIONS:
            item["build"] = False
            item["inferred_as"] = prop["type"]
            continue
        item["type"] = prop["type"]
        if prop.get("front_deg") is not None and item.get("front_deg") is None:
            set_front(item, float(prop["front_deg"]))
    return b
