"""Fuller rooms (29 Oct 2026, user on real06 run 20261028-154514-full): the furniture a designer adds once a room's
groups stand.

The user's words (lessons): "This scene I like it but a bit more furniture would be nice" (UL98, cam_r_L0_salon_1:
the open living and dining room, 55.6 m², 18 % of its floor furnished, wide empty floor between the seating and the
table); the user's improved picture of that view (UL107: a sideboard on the wall beside the dining table, a low
shelving unit between living and dining, an accent armchair with a side table, plants, books on shelves); "There
are no library and books in the house lets put some library and books" (UL103); "bath is too empty there should be
some dolaps" (UL102, r_L1_dus: a wall basin, a toilet and a shower, nothing else).

What (pure; the layout stage calls ``fill_building`` after the completion and the media wall, the model review M21
and Argus U19 call ``review``):

1. **Density** (``furniture_share``, ``under_density``): the share of a room's floor its floor-standing furniture
   covers (rugs and decor aside), measured; a living or dining room of at least ``DENSITY_MIN_M2`` under
   ``DENSITY_TARGET`` of its kind is under-furnished. The program then keeps the groups that only have extra options
   (a reading corner, a bedroom chest) as optional rows of a furnished room (``program.room_program``), and this
   module adds the pieces below while the room stays under its target.
2. **A sideboard by the dining table** (living and dining rooms with a dining table and no sideboard, console or
   display cabinet): on the wall nearest the table (``wall_spots``, ``near``), ``SIDEBOARD_SIZES``.
3. **Bookshelves** (UL103): a living room, a study (a room with a desk read as ``other``) and a child's room without a
   bookshelf get one on a free wall (a child's room a low one, ``LOW_SHELF``); the decor stage fills every bookshelf's
   boards with books (``tabletop.shelf_books``).
4. **Bathroom storage** (UL102): a bathroom without storage gets a tall storage column (``BATH_COLUMN_SIZES``) on a
   free wall stretch; never a fixture moved.

Every piece stands with its back on a wall (``wall_spots``: never in front of a window or a door, off the door swings),
passes the solver's code checks (``solver.verify``: inside, no overlap, the use zones of the fixtures and the
walkways), is ``added_by_ai`` with ``method: rule``, ``rule: room_fill.<what>`` and its reason naming the lesson, and
joins its group (``group`` tag). Off with ``furnished_rooms: keep`` and in the rooms kept as drawn; the brief's
``room_fill: false`` turns the step off.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G
from wenart.furniture import placer

RULE = "room_fill"
REVIEW_CHECK = "M21"
DENSITY_TARGET: dict[str, float] = {"living": 0.25, "dining": 0.25}
# Measured on the committed runs (real06 run 154514 and real04 run 183611, 29 Oct 2026): real04's 50.9-51.8 m² living
# rooms 0.30-0.31 (not called empty), its 40.5 m² play rooms 0.21, real06's 55.6 m² living room 0.18 ("a bit more
# furniture would be nice"); the target sits between (assumed, flagged).
DENSITY_MIN_M2: dict[str, float] = {"living": 16.0, "dining": 12.0}
FLOOR_FREE_TYPES: tuple[str, ...] = ("rug", "unknown", "wall_cabinet")
SIDEBOARD_SIZES: tuple[tuple[float, float], ...] = ((1.6, 0.45), (1.4, 0.42), (1.2, 0.42))
SIDEBOARD_NEAR_M = 3.0            # the sideboard's front within this of the dining table's edge (it serves the table)
STORAGE_TYPES: tuple[str, ...] = ("sideboard", "console_table", "display_cabinet", "dresser")
SHELF_SIZES: tuple[tuple[float, float], ...] = ((1.0, 0.35), (1.2, 0.35), (0.8, 0.3))
LOW_SHELF: dict = {"sizes": ((0.8, 0.3), (1.0, 0.35), (0.6, 0.3)), "height": 0.9}
BATH_COLUMN_SIZES: tuple[tuple[float, float], ...] = ((0.4, 0.35), (0.6, 0.35), (0.3, 0.3))
BATH_COLUMN_HEIGHT_M = 1.6        # a bathroom storage column (ABO B07RMJPJMX 0.30 x 0.27 x 1.40 m; 1.6-1.9 m units)
BATH_STORAGE_TYPES: tuple[str, ...] = ("tall_cabinet", "wall_cabinet", "dresser", "sideboard", "bookshelf",
                                       "shoe_cabinet", "display_cabinet")
STEP_M = 0.05
GAP_M = 0.02
OPENING_MARGIN_M = 0.10
SPOTS_TRIED = 40
# the free floor in front of a new piece (groups.yaml use_zones: storage_front 0.80 m; a bookshelf the walkway's 0.60 m),
# tested cheaply before the solver's checks
FRONT_FREE_M: dict[str, float] = {"sideboard": 0.8, "tall_cabinet": 0.8, "bookshelf": 0.6}
LESSONS = {"sideboard": "UL107", "bookshelf": "UL103", "low_shelf": "UL103", "bath_column": "UL102",
           "density": "UL98"}


def _area(room: dict) -> float:
    pts = room.get("polygon") or []
    return abs(G.polygon_area([tuple(p[:2]) for p in pts])) if len(pts) >= 3 else 0.0


def _built(f: dict) -> bool:
    return f.get("build") is not False and bool(f.get("footprint")) and f.get("type") not in (None, "unknown")


def _pieces(building: dict, room_id: str) -> list[dict]:
    return [f for f in building.get("furniture") or [] if f.get("room_id") == room_id and _built(f)]


def furniture_share(building: dict, room: dict) -> float:
    """The share of the room's floor its floor-standing furniture covers (pure; module docstring, step 1)."""
    from shapely.geometry import Polygon
    from shapely.ops import unary_union

    from wenart.furniture import schemas

    if len(room.get("polygon") or []) < 3:
        return 0.0
    poly = Polygon([tuple(p[:2]) for p in room["polygon"]]).buffer(0)
    shapes = []
    for f in _pieces(building, room["id"]):
        if f.get("type") in FLOOR_FREE_TYPES or schemas.off_floor(f):
            continue
        try:
            shapes.append(placer.piece_from_furniture(f).polygon())
        except (KeyError, TypeError, ValueError):
            continue
    if not shapes or poly.area <= 0:
        return 0.0
    return round(unary_union(shapes).intersection(poly).area / poly.area, 4)


def under_density(building: dict, room: dict, kind: Optional[str] = None) -> tuple[bool, float, Optional[float]]:
    """``(under, share, target)`` of a room (module docstring, step 1); ``target`` None for a kind without one."""
    from wenart.furniture import program as PR

    kind = kind or PR.room_kind(building, room)
    target = DENSITY_TARGET.get(kind)
    if target is None or _area(room) < DENSITY_MIN_M2.get(kind, math.inf) - 1e-9:
        return False, furniture_share(building, room), target
    share = furniture_share(building, room)
    return share < target - 1e-9, share, target


# --------------------------------------------------------------------------
# A piece on a free wall
# --------------------------------------------------------------------------

def _opening_spans(ctx, k: int) -> list[tuple[float, float]]:
    a, b = ctx.segments[k]
    length = G.distance(a, b)
    u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
    out = []
    for z in list(ctx.doors) + list(ctx.windows):
        p = z.inner_point
        if G.point_segment_distance(p, a, b) > 0.35:
            continue
        t = (p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1]
        out.append((t - float(z.width) / 2.0, t + float(z.width) / 2.0))
    return out


def wall_spots(building: dict, room: dict, sizes, near=None, near_max: Optional[float] = None) -> list[dict]:
    """Places for a piece with its back on a wall (pure): every ``STEP_M`` along every wall segment long enough, its
    span along the wall clear of the doors and windows on it (``OPENING_MARGIN_M``); ``[{"center", "rotation_deg",
    "size", "segment", "near_m"}]``, nearest ``near`` (a point; within ``near_max`` of it) first, else the middle of
    the longest free stretch first. The solver's checks judge each (``place``)."""
    from shapely.geometry import Point

    ctx = placer.room_context(building, room)
    out = []
    for k, (a, b) in enumerate(ctx.segments):
        length = G.distance(a, b)
        n = ctx.segment_normal(k)
        u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        rot = placer._rotation_for_normal(n)
        spans = _opening_spans(ctx, k)
        for w, d in sizes:
            if length < w + 2 * GAP_M:
                continue
            t = w / 2.0 + GAP_M
            while t <= length - w / 2.0 - GAP_M + 1e-9:
                lo, hi = t - w / 2.0 - OPENING_MARGIN_M, t + w / 2.0 + OPENING_MARGIN_M
                if not any(s0 < hi and s1 > lo for s0, s1 in spans):
                    c = (a[0] + u[0] * t + n[0] * (d / 2.0 + GAP_M), a[1] + u[1] * t + n[1] * (d / 2.0 + GAP_M))
                    dist = Point(c).distance(near) if near is not None else None
                    if near_max is None or dist is None or dist <= near_max + 1e-9:
                        key = (round(dist, 3) if dist is not None else round(abs(t - length / 2.0) - length, 3),
                               -w, k, round(t, 3))
                        out.append({"center": (round(c[0], 4), round(c[1], 4)), "rotation_deg": rot, "size": (w, d),
                                    "segment": k, "near_m": dist, "_key": key})
                t += STEP_M
    out.sort(key=lambda s: s["_key"])
    return out


def _next_id(building: dict, level_id: str) -> str:
    from wenart.furniture import solver as SV

    return f"f_{level_id}_{SV._next_number(building, level_id):03d}"


def _piece(room: dict, ftype: str, spot: dict, pid: str, what: str, reason: str, group: Optional[dict] = None,
           height: Optional[float] = None) -> dict:
    out = {"id": pid, "level_id": room["level_id"], "room_id": room["id"], "type": ftype, "source": "added_by_ai",
           "method": "rule", "completes_room": True, "status": "verified",
           "footprint": {"center": [float(spot["center"][0]), float(spot["center"][1])],
                         "size": [float(spot["size"][0]), float(spot["size"][1])],
                         "rotation_deg": round(float(spot["rotation_deg"]), 3)},
           "front_deg": round(G.front_direction_deg(float(spot["rotation_deg"])), 3), "height": height, "asset": None,
           "rule": {"name": f"{RULE}.{what}", "lesson": LESSONS.get(what, "UL98")},
           "reason": f"{reason} ({LESSONS.get(what, 'UL98')})",
           "evidence": [{"file": "rule", "method": "inferred", "confidence": 0.7, "note": f"{RULE}.{what}"}]}
    if group:
        out["group"] = group
    return out


def place(building: dict, room: dict, ftype: str, sizes, what: str, reason: str, near=None,
          near_max: Optional[float] = None, group: Optional[dict] = None,
          height: Optional[float] = None) -> tuple[Optional[dict], str]:
    """The first wall place (``wall_spots``) of a new ``ftype`` piece that passes the code checks (a cheap overlap
    test, then ``solver.verify``); ``(piece, why)``, the piece None with the reason when none passes."""
    from wenart.furniture import solver as SV

    spots = wall_spots(building, room, sizes, near, near_max)
    if not spots:
        return None, "no free wall stretch clear of the windows and doors"
    pid = _next_id(building, room["level_id"])
    polys = []
    for f in _pieces(building, room["id"]):
        try:
            polys.append((f["id"], placer.piece_from_furniture(f).polygon()))
        except (KeyError, TypeError, ValueError):
            continue
    front_m = FRONT_FREE_M.get(ftype, 0.6)
    checked, why = 0, []
    for s in spots:
        if checked >= SPOTS_TRIED:
            break
        piece = _piece(room, ftype, s, pid, what, reason, group, height)
        pp = placer.piece_from_furniture(piece)
        mine, front = pp.polygon(), pp.front_zone(front_m)
        hit = next((i for i, q in polys if mine.intersection(q).area > placer.AREA_EPS
                    or front.intersection(q).area > placer.AREA_EPS), None)
        if hit is not None:                     # the cheap tests first (the box, its front's free floor)
            continue
        checked += 1
        hard, _after = SV.verify(building, room["id"], [piece])
        if hard:
            why.append(hard[0])
            continue
        return piece, "ok"
    return None, (f"{checked} free place(s) refused by the code checks (e.g. {why[0][:120]})" if why
                  else "every wall place is taken")


# --------------------------------------------------------------------------
# The rules
# --------------------------------------------------------------------------

def fill_room(building: dict, room: dict, kind: str) -> list[dict]:
    """In place: the pieces the rules add to one room (module docstring, steps 2-4); returns the records ``{"what",
    "piece" | None, "why"}``."""
    out = []
    pieces = _pieces(building, room["id"])
    types = {f["type"] for f in pieces}
    under, share, target = under_density(building, room, kind)

    def add(piece: Optional[dict], what: str, why: str) -> None:
        if piece is not None:
            building.setdefault("furniture", []).append(piece)
        out.append({"what": what, "piece": piece, "why": why})

    if kind in ("living", "dining"):
        tables = [f for f in pieces if f["type"] == "table_dining"]
        if tables and not types & set(STORAGE_TYPES) and (under or kind == "dining"):
            t = max(tables, key=lambda f: float(f["footprint"]["size"][0]) * float(f["footprint"]["size"][1]))
            near = placer.piece_from_furniture(t).polygon()
            reason = (f"a sideboard on the wall beside the dining table {t['id']} (the room is "
                      f"{share * 100:.0f} % furnished, under {target * 100:.0f} %; user: \"a bit more furniture "
                      f"would be nice\", the improved picture's wooden sideboard by the table)" if target else
                      f"a sideboard on the wall beside the dining table {t['id']}")
            group = {"group_id": f"{room['id']}.living_storage.dining", "group": "living_storage", "role": "anchor"}
            piece, why = place(building, room, "sideboard", SIDEBOARD_SIZES, "sideboard", reason,
                               near=near, near_max=SIDEBOARD_NEAR_M, group=dict(group, anchor_id=None))
            if piece is not None:
                piece["group"]["anchor_id"] = piece["id"]
            add(piece, "sideboard", why)
    shelf_room = (kind == "living" or (kind == "bedroom" and room.get("room_subtype") == "child")
                  or (kind == "other" and "desk" in types))
    if shelf_room and "bookshelf" not in types:
        low = kind == "bedroom"
        reason = ("a low bookshelf with books and toys on a free wall of the child's room" if low else
                  "a bookshelf with books on a free wall" + (" of the study" if kind == "other" else ""))
        reason += " (user, 29 Oct 2026: \"There are no library and books in the house\")"
        group = ({"group_id": f"{room['id']}.living_storage.books", "group": "living_storage", "role": "anchor"}
                 if kind == "living" else None)
        piece, why = place(building, room, "bookshelf", LOW_SHELF["sizes"] if low else SHELF_SIZES,
                           "low_shelf" if low else "bookshelf", reason, group=group,
                           height=LOW_SHELF["height"] if low else None)
        if piece is not None and piece.get("group"):
            piece["group"]["anchor_id"] = piece["id"]
        add(piece, "low_shelf" if low else "bookshelf", why)
    if kind == "bathroom" and not types & set(BATH_STORAGE_TYPES):
        reason = ("a tall storage column on a free wall of the bathroom, off the fixtures' use zones, the shower entry "
                  "and the door swing (user, 29 Oct 2026: \"bath is too empty there should be some dolaps\")")
        # 29 Oct 2026 (UL114 B5: "a tall open niche column beside the vanity"): the free wall place nearest the basin
        basins = sorted((f for f in pieces if f["type"] == "washbasin"), key=lambda f: f["id"])
        near = placer.piece_from_furniture(basins[0]).polygon() if basins else None
        piece, why = place(building, room, "tall_cabinet", BATH_COLUMN_SIZES, "bath_column", reason, near=near,
                           height=BATH_COLUMN_HEIGHT_M)
        add(piece, "bath_column", why)
    return out


def fill_building(building: dict, brief: Optional[dict] = None) -> tuple[dict, list[dict]]:
    """In place: ``fill_room`` for every furnished room (module docstring); ``(building, records)`` with ``room_id``.
    Off with the brief's ``room_fill: false`` and ``furnished_rooms: keep``; the rooms kept as drawn are left alone."""
    from wenart.furniture import complete as C
    from wenart.furniture import program as PR

    values = dict(((building.get("project") or {}).get("brief") or {}))
    values.update(brief or {})
    v = values.get("room_fill", True)
    if v is False or str(v).strip().lower() in ("false", "off", "no", "none"):
        return building, []
    settings = C.Settings(mode=str(values.get("furnished_rooms", "complete")),
                          keep=tuple(str(x) for x in values.get("furnished_rooms_keep") or ()))
    if settings.mode == "keep":
        return building, []
    records = []
    for room in building.get("rooms") or []:
        if len(room.get("polygon") or []) < 3 or C.is_kept(room, settings):
            continue
        kind = PR.room_kind(building, room)
        if kind not in ("living", "dining", "bedroom", "other", "bathroom"):
            continue
        for r in fill_room(building, room, kind):
            records.append(dict(r, room_id=room["id"], kind=kind))
    return building, records


# --------------------------------------------------------------------------
# The review
# --------------------------------------------------------------------------

def review(building: dict) -> tuple[list[dict], int]:
    """M21 / U19 (pure): ``(findings, checked)``: a living or dining room under its furniture density (UL98, minor),
    a living room or a study without a bookshelf (UL103, minor), a bookshelf without books on it (UL103, minor; after
    the decor stage), a bathroom without storage (UL102, minor)."""
    from wenart.furniture import program as PR

    out, n = [], 0
    books = {d.get("host_id") for d in building.get("decor") or [] if d.get("type") in ("book_set", "books")}
    decor_done = bool(building.get("decor"))

    def f(sev, element, room, message, rule, lesson, **m):
        out.append({"check": REVIEW_CHECK, "severity": sev, "target": element, "room_id": room["id"],
                    "message": message, "metrics": dict(m, model_review=True, rule=rule, lesson=lesson)})

    for room in building.get("rooms") or []:
        if len(room.get("polygon") or []) < 3:
            continue
        kind = PR.room_kind(building, room)
        pieces = _pieces(building, room["id"])
        types = {p["type"] for p in pieces}
        if kind in DENSITY_TARGET:
            n += 1
            under, share, target = under_density(building, room, kind)
            if under:
                f("minor", room["id"], room, f"{room['id']} ({kind}, {_area(room):.1f} m²) is {share * 100:.0f} % "
                  f"furnished, under the {target * 100:.0f} % of a furnished {kind} room: wide empty floor",
                  f"{RULE}.density", "UL98", share=share, target=target)
        if kind == "living" or (kind == "other" and "desk" in types):
            n += 1
            if "bookshelf" not in types:
                f("minor", room["id"], room, f"{room['id']} ({kind}) has no bookshelf", f"{RULE}.bookshelf", "UL103")
        for p in pieces:
            if p["type"] == "bookshelf" and decor_done and p["id"] not in books:
                f("minor", p["id"], room, f"the bookshelf {p['id']} in {room['id']} holds no books",
                  f"{RULE}.books", "UL103")
        if kind == "bathroom":
            n += 1
            if not types & set(BATH_STORAGE_TYPES):
                f("minor", room["id"], room, f"{room['id']} (bathroom) has no storage: its fixtures stand alone",
                  f"{RULE}.bath_column", "UL102")
    return out, n
