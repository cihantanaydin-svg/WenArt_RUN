"""The media wall: a TV in every living room and in the master bedroom (29 Oct 2026, user on real06 run
20261028-154514-full: "There is no TV in the house", lesson UL99).

What the run had: no living room or bedroom held a television. The seating group's TV unit (``groups.yaml``
``seating``: a ``tv_unit`` on the wall the sofa faces, centred on its axis within 0.30 m) was placed by the solver
only for a sofa it laid itself; a drawn sofa whose facing wall the solver found taken kept ``missing: tv_unit``
(real06's salon, three real04 living rooms), and a TV unit, where one was built, carried no TV: the library holds 72
TV-unit models and no television.

What (pure; the layout stage calls ``add_media_walls`` after the completion, the decor stage ``tv_items``, the model
review M21 and Argus U19 call ``review``):

1. **Media rooms** (``media_rooms``): every living room (``program.room_kind`` living) with a sofa, and the master
   bedroom with its double bed: a bedroom whose label names it (``MASTER_WORDS``: ebeveyn, master, parents, suite,
   ...), else the largest non-child bedroom with a double bed of at least ``MASTER_MIN_M2``. Brief keys:
   ``media_wall`` (default true; false: no TV anywhere) and ``tv_in_bedroom`` (``master`` by default, ``all``: every
   bedroom with a double bed but a child's room, ``none``). A child's room never gets one by default.
2. **The seat** (``main_seat``): the largest sofa (a corner sofa by its long leg), else the double bed; the other
   sofas of the room are tried after it.
3. **The TV wall** (``tv_spots``): a ``tv_unit`` (``UNIT_SIZES``) with its back on a wall that faces the seat
   (``WALL_FACE_DEG``), its front ``VIEW_MIN_M``-``VIEW_MAX_M`` from the seat's front, the TV centre seen from the seat
   within ``VIEW_ANGLE_MAX_DEG`` of its axis (best on it, at ``VIEW_BEST_M``); never in front of a window or a door,
   never in a door swing or a walkway, nothing taller than ``SIGHT_HEIGHT_M`` between the seat and the TV, every
   placement checked by the solver's code checks (``solver.verify``: inside, no overlap, doors and windows free, the
   walkways). A drawn TV unit is kept wherever it is drawn; a drawn low chest on the TV wall of a bedroom (a dresser, a
   sideboard, a console) is the TV's host instead of a new unit. A room where no place passes is reported (``notes``,
   the review), never forced.
4. **The TV** (``tv_items``, decor type ``tv``): on every TV unit (and the bedroom's host chest), its size by the
   viewing distance (SMPTE / THX: the distance is 1.2-1.6 times the screen diagonal; ``inches_for``) no wider than its
   host, at most ``MAX_INCHES`` (65 inches in a living room, 55 in a bedroom), its stand at the back of the host's top,
   facing the host's front; built procedurally (``wenart.blender.parametric.tv_parts``: a thin black panel with a slim
   bezel and a dark glossy screen with a faint reflection, a pedestal stand), ``added_by_ai``, ``method: rule``, the
   reason naming the seat and the distance.

Why: a living room is planned around its seating and the screen it faces; the user expects the TV a real house has.
"""
from __future__ import annotations

import math
import re
from typing import Callable, Optional

from wenart import geometry as G
from wenart.furniture import placer

RULE = "media_wall"
LESSON = "UL99"
REVIEW_CHECK = "M21"
LIVING_SEATS: tuple[str, ...] = ("sofa_corner", "sofa")
BED_SEATS: tuple[str, ...] = ("bed_double",)
HOST_TYPES: tuple[str, ...] = ("tv_unit",)                                  # a TV always stands on these
BEDROOM_HOSTS: tuple[str, ...] = ("dresser", "sideboard", "console_table")  # a bedroom's TV may stand on a low chest
LIVING_HOSTS: tuple[str, ...] = ("sideboard", "console_table")              # ... and a living room's on a sideboard
HOST_MAX_TOP_M = 0.95             # a host this low or lower (a chest taller than this hides the screen's lower edge)
UNIT_SIZES: dict[str, tuple[tuple[float, float], ...]] = {
    # real TV units (wenart/furniture/catalog_library.json tv_unit boxes: 1.0-1.9 m wide, 0.40-0.48 m deep)
    "living": ((1.8, 0.45), (1.6, 0.45), (1.4, 0.42), (1.2, 0.40)),
    "bedroom": ((1.2, 0.40), (1.4, 0.42), (1.0, 0.40)),
}
VIEW_MIN_M = 1.5                  # = groups.yaml tv_distance min (seat front to the TV unit front)
VIEW_MAX_M = 4.0
VIEW_BEST_M = 2.6                 # 55-65 inch at 1.2-1.6 x the diagonal
VIEW_ANGLE_MAX_DEG = 15.0         # the TV centre seen from the seat's centre, off its axis (the seat faces the screen)
WALL_FACE_DEG = 15.0              # the TV wall's inward normal against the seat's front direction
OPENING_MARGIN_M = 0.15           # a unit (and its TV) keeps this along the wall from a window or a door
SIGHT_HEIGHT_M = 0.60             # = group_checks.SIGHT_HEIGHT_M: taller pieces between the seat and the TV block it
SIGHT_FREE_TYPES: tuple[str, ...] = ("table_coffee", "ottoman", "side_table", "rug", "unknown")
STEP_M = 0.05                     # positions along a wall
GAP_M = 0.02                      # the unit's back off the wall
# Step 3b: a seat that faces the open floor of an open-plan living room (no wall within VIEW_MAX_M) gets a low media
# console standing free on its axis, its back to the rest of the room (the room divider of the user's target picture
# for real06's salon, lesson UL107); the walkways and doors decide by code (solver.verify).
OPEN_PLAN_MIN_M2 = 25.0
FREE_DISTANCES_M: tuple[float, ...] = (2.6, 2.4, 2.8, 2.2, 3.0, 2.0, 3.2)
FREE_OFFSETS_M: tuple[float, ...] = (0.0, 0.1, -0.1, 0.2, -0.2)
FREE_BACK_M = 1.0                 # open floor behind a free console (else it stands against something)
SPOTS_TRIED = 60                  # the best places checked by the solver per seat (each check is a room check)
MASTER_WORDS: tuple[str, ...] = ("ebeveyn", "master", "parent", "parents", "suite", "principal", "eltern",
                                 "matrimonial", "matrimoniale", "hoofdslaapkamer", "e yatak")
MASTER_MIN_M2 = 12.0
BRIEF_KEYS = ("media_wall", "tv_in_bedroom")
# The TVs (16:9 panels): width = 0.8716 x the diagonal, panel height = 0.4903 x the diagonal, a 1 cm bezel each side,
# a pedestal stand 6 cm high (real 43-75 inch sets: 0.96-1.68 m wide, stands 0.20-0.33 m deep).
TV_INCHES: tuple[int, ...] = (43, 50, 55, 65, 75)
MAX_INCHES: dict[str, int] = {"living": 65, "bedroom": 55}
DISTANCE_FACTOR = (1.2, 1.6)      # SMPTE (30 degrees: 1.6 x the diagonal) to THX (40 degrees: 1.2 x)
TV_BEZEL_M = 0.01
TV_STAND_H_M = 0.06
TV_BACK_GAP_M = 0.05              # the stand's back this far in from the host's back edge
TV_DEFAULT_INCHES = 50            # a TV unit with no seat facing it
TOP_MARGIN_M = 0.03               # = tabletop.TOP_MARGIN_M: the TV's box this far in from its host's edges


def tv_box(inches: int) -> tuple[float, float, float]:
    """``(width, stand depth, height)`` in metres of an ``inches`` TV on its stand (pure)."""
    diag = float(inches) * 0.0254
    w = diag * 0.8716 + 2 * TV_BEZEL_M
    h = diag * 0.4903 + 2 * TV_BEZEL_M + TV_STAND_H_M
    d = 0.12 + float(inches) * 0.0024
    return round(w, 3), round(d, 3), round(h, 3)


def inches_for(distance_m: Optional[float], max_width: float, kind: str = "living") -> Optional[int]:
    """The TV for a viewing distance (pure; module docstring, step 4): the largest set whose diagonal is at most
    ``distance / 1.2`` (and ``MAX_INCHES`` of the room kind) and whose width fits ``max_width``; the diagonal nearest
    ``distance / 1.4`` among those wins; None when not even the smallest fits."""
    top = MAX_INCHES.get(kind, MAX_INCHES["living"])
    fits = [n for n in TV_INCHES if n <= top and tv_box(n)[0] <= max_width + 1e-9]
    if not fits:
        return None
    if distance_m is None:
        return max(n for n in fits if n <= TV_DEFAULT_INCHES) if any(n <= TV_DEFAULT_INCHES for n in fits) \
            else min(fits)
    big = [n for n in fits if n * 0.0254 <= float(distance_m) / DISTANCE_FACTOR[0] + 1e-9] or [min(fits)]
    want = float(distance_m) / 1.4 / 0.0254
    return min(big, key=lambda n: (abs(n - want), -n))


# --------------------------------------------------------------------------
# Rooms and seats
# --------------------------------------------------------------------------

def brief_values(project_dir, settings=None) -> dict:
    """The brief keys of the media wall (``BRIEF_KEYS``, defaults in ``wenart/defaults.yaml``) and the furnished-room
    keys of ``settings`` (a ``complete.Settings``): the rooms kept as drawn get no TV unit."""
    from wenart import brief as BR

    try:
        loaded = BR.load_brief(project_dir)
    except Exception:  # noqa: BLE001 - a broken brief: the layout already reported it; the defaults apply here
        loaded = {}
    out = {"media_wall": BR.value(loaded, "media_wall", True), "tv_in_bedroom": BR.value(loaded, "tv_in_bedroom",
                                                                                          "master"),
           "room_fill": BR.value(loaded, "room_fill", True)}          # wenart.furniture.room_fill (UL98)
    if settings is not None:
        out.update(settings.brief_values())
    return out


def _brief(building: dict, brief: Optional[dict] = None) -> dict:
    values = dict(((building.get("project") or {}).get("brief") or {}))
    values.update({k: v for k, v in (brief or {}).items() if k in BRIEF_KEYS})
    return values


def _off(value) -> bool:
    return value is False or str(value).strip().lower() in ("false", "off", "no", "none", "0")


def _area(room: dict) -> float:
    pts = room.get("polygon") or []
    return abs(G.polygon_area([tuple(p[:2]) for p in pts])) if len(pts) >= 3 else 0.0


def _built(f: dict) -> bool:
    return f.get("build") is not False and bool(f.get("footprint")) and f.get("type") not in (None, "unknown")


def _pieces(building: dict, room_id: str) -> list[dict]:
    return [f for f in building.get("furniture") or [] if f.get("room_id") == room_id and _built(f)]


def _fold(text: str) -> str:
    table = str.maketrans("çğıöşüâîûÇĞİÖŞÜ", "cgiosuaiuCGIOSU")
    return re.sub(r"[^a-z0-9]+", " ", str(text or "").translate(table).lower()).strip()


def master_named(room: dict) -> bool:
    """A bedroom whose label names the master or parents' bedroom (``MASTER_WORDS``; Turkish folded to ASCII:
    "Ebeveyn Y. Odası", "E. Yatak Odası")."""
    words = f" {_fold(room.get('label') or room.get('id') or '')} "
    return any(f" {w} " in words or words.strip().startswith(w) for w in MASTER_WORDS)


def media_rooms(building: dict, brief: Optional[dict] = None) -> list[tuple[dict, str]]:
    """``[(room, kind)]`` of the rooms that get a TV (module docstring, step 1), ``kind`` ``living`` or ``bedroom``."""
    from wenart.furniture import program as PR

    values = _brief(building, brief)
    if _off(values.get("media_wall", True)):
        return []
    bedrooms = str(values.get("tv_in_bedroom", "master") or "master").strip().lower()
    out: list[tuple[dict, str]] = []
    beds: list[dict] = []
    for room in building.get("rooms") or []:
        if len(room.get("polygon") or []) < 3:
            continue
        kind = PR.room_kind(building, room)
        pieces = _pieces(building, room["id"])
        if kind == "living" and any(f["type"] in LIVING_SEATS for f in pieces):
            out.append((room, "living"))
        elif kind == "bedroom" and room.get("room_subtype") != "child" and any(f["type"] in BED_SEATS
                                                                               for f in pieces):
            beds.append(room)
    if bedrooms in ("all", "every"):
        out += [(r, "bedroom") for r in beds]
    elif bedrooms in ("master", "main", "true", "yes"):
        named = [r for r in beds if master_named(r)]
        if not named:
            big = sorted((r for r in beds if _area(r) >= MASTER_MIN_M2 - 1e-9), key=lambda r: (-_area(r), r["id"]))
            named = big[:1]
        out += [(r, "bedroom") for r in named]
    return out


def seat_width(f: dict) -> float:
    w, d = (float(v) for v in f["footprint"]["size"][:2])
    return max(w, d) if f.get("type") == "sofa_corner" else w


def seats(pieces: list[dict], kind: str) -> list[dict]:
    """The room's seats that may face a TV, the main one first (module docstring, step 2)."""
    types = LIVING_SEATS if kind == "living" else BED_SEATS
    return sorted((f for f in pieces if f.get("type") in types),
                  key=lambda f: (-round(seat_width(f), 2), f["type"] != "sofa_corner", str(f["id"])))


def main_seat(pieces: list[dict], kind: str) -> Optional[dict]:
    got = seats(pieces, kind)
    return got[0] if got else None


def _seat_frame(seat: dict) -> tuple[tuple[float, float], tuple[float, float], float]:
    """``(seat front centre, front unit vector, seat width)`` of a sofa or bed (a corner sofa: its long leg's seat)."""
    from wenart.furniture import group_checks as GC
    from wenart.furniture import schemas

    p = placer.piece_from_furniture(seat)
    fx, fy = GC.front_vec(p)
    x0, x1, yf = -p.size[0] / 2.0, p.size[0] / 2.0, -p.size[1] / 2.0
    if p.shape == "L":
        x0, x1, yf = schemas.l_seat_front(p.size, p.chaise_side, p.chaise_depth, p.seat_depth, p.chaise_width)
    front = GC.to_world(p, ((x0 + x1) / 2.0, yf))
    return (float(front[0]), float(front[1])), (fx, fy), float(x1 - x0)


def view_of(seat: dict, point) -> dict:
    """``{"distance_m", "offset_m", "angle_deg", "in_front"}`` of a point (a TV's front centre) seen from a seat
    (pure): the distance along the seat's axis from its front, the offset off its axis, the angle off its axis."""
    (sx, sy), (fx, fy), _w = _seat_frame(seat)
    dx, dy = float(point[0]) - sx, float(point[1]) - sy
    along = dx * fx + dy * fy
    off = abs(-dx * fy + dy * fx)
    return {"distance_m": round(along, 3), "offset_m": round(off, 3),
            "angle_deg": round(math.degrees(math.atan2(off, max(along, 1e-6))), 2), "in_front": along > 0.0}


# --------------------------------------------------------------------------
# The TV wall
# --------------------------------------------------------------------------

def _opening_spans(ctx, k: int) -> list[tuple[float, float]]:
    """The spans along segment ``k`` (from its start) of the doors and windows on it (their width)."""
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


def _sight_blocked(seat: dict, unit_front, tv_w: float, pieces: list[dict], skip: set) -> list[str]:
    """The pieces taller than ``SIGHT_HEIGHT_M`` in the corridor from the seat's front to the TV (the TV's width)."""
    from shapely.geometry import LineString

    (sx, sy), _f, _w = _seat_frame(seat)
    line = LineString([(sx, sy), (float(unit_front[0]), float(unit_front[1]))])
    if line.length < 0.2:
        return []
    corridor = line.buffer(tv_w / 2.0, cap_style=2)
    out = []
    for f in pieces:
        if f["id"] in skip or f.get("type") in SIGHT_FREE_TYPES:
            continue
        try:
            poly = placer.piece_from_furniture(f).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if _top(f) > SIGHT_HEIGHT_M and poly.intersection(corridor).area > 0.02:
            out.append(f["id"])
    return out


def _unit_piece(room: dict, center, rotation: float, size, seat: dict, kind: str, view: dict, pid: str,
                free: bool = False) -> dict:
    group = "seating" if kind == "living" else "sleeping_double"
    own = seat.get("group") if isinstance(seat.get("group"), dict) else {}
    # the seat's own group (the unit is its TV, G1 judges it against this seat); a seat that anchors none gets its own
    group_id = (own.get("group_id") if own.get("group") == group and own.get("anchor_id") == seat["id"]
                else f"{room['id']}.{group}.{seat['id']}")
    where = ("a low media console standing free on its axis, its back to the open floor (a room divider)" if free
             else "on the wall it faces")
    return {"id": pid, "level_id": room["level_id"], "room_id": room["id"], "type": "tv_unit",
            "source": "added_by_ai", "method": "rule", "completes_room": True, "status": "verified",
            "footprint": {"center": [round(float(center[0]), 4), round(float(center[1]), 4)],
                          "size": [float(size[0]), float(size[1])], "rotation_deg": round(float(rotation), 3)},
            "front_deg": round(G.front_direction_deg(float(rotation)), 3), "height": None, "asset": None,
            "group": {"group_id": group_id, "group": group, "role": "partner", "anchor_id": seat["id"]},
            "rule": {"name": RULE, "seat": seat["id"], "free": bool(free), "view": dict(view)},
            "reason": (f"media wall: a TV unit for the TV facing the {seat['type'].replace('_', ' ')} {seat['id']}, "
                       f"{where}, {view['distance_m']:.2f} m from its front, {view['angle_deg']:.0f}° off its axis, "
                       f"off every window, door and walkway (user, 29 Oct 2026: \"There is no TV in the "
                       f"house\", {LESSON})"),
            "evidence": [{"file": "rule", "method": "inferred", "confidence": 0.7,
                          "note": f"{RULE}: the TV wall the seat {seat['id']} faces"}]}


def tv_spots(building: dict, room: dict, seat: dict, kind: str, pieces: Optional[list[dict]] = None,
             sizes=None) -> list[dict]:
    """The TV-unit places facing ``seat`` (pure; module docstring, step 3), best first: ``[{"center", "rotation_deg",
    "size", "view", "score", "segment"}]`` (geometry only; ``plan_room`` checks each with the solver)."""
    ctx = placer.room_context(building, room)
    pieces = pieces if pieces is not None else _pieces(building, room["id"])
    (sx, sy), (fx, fy), _w = _seat_frame(seat)
    out = []
    for k, (a, b) in enumerate(ctx.segments):
        length = G.distance(a, b)
        if length < 0.8:
            continue
        n = ctx.segment_normal(k)
        if G.angle_difference_deg(math.degrees(math.atan2(-n[1], -n[0])), math.degrees(math.atan2(fy, fx))) \
                > WALL_FACE_DEG + 1e-9:
            continue
        u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        rot = placer._rotation_for_normal(n)
        spans = _opening_spans(ctx, k)
        for w, d in sizes or UNIT_SIZES[kind]:
            t = w / 2.0 + GAP_M
            while t <= length - w / 2.0 - GAP_M + 1e-9:
                lo, hi = t - w / 2.0 - OPENING_MARGIN_M, t + w / 2.0 + OPENING_MARGIN_M
                if not any(s0 < hi and s1 > lo for s0, s1 in spans):
                    c = (a[0] + u[0] * t + n[0] * (d / 2.0 + GAP_M), a[1] + u[1] * t + n[1] * (d / 2.0 + GAP_M))
                    front = (c[0] + n[0] * d / 2.0, c[1] + n[1] * d / 2.0)
                    view = view_of(seat, front)
                    if (view["in_front"] and VIEW_MIN_M - 1e-9 <= view["distance_m"] <= VIEW_MAX_M + 1e-9
                            and view["angle_deg"] <= VIEW_ANGLE_MAX_DEG + 1e-9):
                        score = (view["angle_deg"] / VIEW_ANGLE_MAX_DEG + abs(view["distance_m"] - VIEW_BEST_M)
                                 / VIEW_BEST_M - 0.1 * w)
                        out.append({"center": (round(c[0], 4), round(c[1], 4)), "rotation_deg": rot,
                                    "size": (w, d), "view": view, "score": round(score, 4), "segment": k,
                                    "front": front})
                t += STEP_M
    out.sort(key=lambda s: (s["score"], s["segment"], s["center"]))
    return out


def free_spots(building: dict, room: dict, seat: dict, kind: str, sizes=None) -> list[dict]:
    """A media console standing free in an open-plan living room (module docstring, step 3b; pure): on the seat's
    axis (``FREE_OFFSETS_M``) at ``FREE_DISTANCES_M`` from its front, facing it, its back to at least ``FREE_BACK_M``
    of open floor (a low room divider between the living and the dining part); only in a living room of at least
    ``OPEN_PLAN_MIN_M2``. Same records as ``tv_spots``; ``plan_room`` checks each with the solver."""
    from shapely.geometry import Point

    if kind != "living" or _area(room) < OPEN_PLAN_MIN_M2 - 1e-9:
        return []
    ctx = placer.room_context(building, room)
    (sx, sy), (fx, fy), _w = _seat_frame(seat)
    rot = placer._rotation_for_normal((-fx, -fy))
    others = []
    for f in _pieces(building, room["id"]):
        try:
            others.append(placer.piece_from_furniture(f).polygon())
        except (KeyError, TypeError, ValueError):
            continue
    out = []
    for w, d in sizes or UNIT_SIZES[kind]:
        for dist in FREE_DISTANCES_M:
            for off in FREE_OFFSETS_M:
                fpt = (sx + fx * dist - fy * off, sy + fy * dist + fx * off)
                c = (fpt[0] + fx * d / 2.0, fpt[1] + fy * d / 2.0)
                back = Point(c[0] + fx * (d / 2.0 + FREE_BACK_M), c[1] + fy * (d / 2.0 + FREE_BACK_M))
                if not ctx.polygon.contains(back) or not ctx.polygon.contains(Point(c)):
                    continue
                # the open floor behind it (its width, FREE_BACK_M deep) holds no piece: it closes the seating
                # group, it does not stand inside it (real04's L-1b salon: its armchairs face each other behind it)
                strip = placer._local_box(c, rot, -w / 2.0, w / 2.0, d / 2.0, d / 2.0 + FREE_BACK_M)
                if not ctx.polygon.buffer(1e-3).contains(strip) or any(strip.intersection(q).area > 0.01
                                                                       for q in others):
                    continue
                view = view_of(seat, fpt)
                score = 1.0 + abs(dist - VIEW_BEST_M) / VIEW_BEST_M + abs(off) - 0.1 * w
                out.append({"center": (round(c[0], 4), round(c[1], 4)), "rotation_deg": rot, "size": (w, d),
                            "view": view, "score": round(score, 4), "segment": None, "front": fpt, "free": True})
    out.sort(key=lambda s: (s["score"], s["center"]))
    return out


def _host_on_wall(seat: dict, pieces: list[dict], kind: str) -> Optional[tuple[dict, dict]]:
    """A low piece the seat faces that may hold the TV (a drawn chest on a bedroom's TV wall, a sideboard on a living
    room's): ``(piece, view)`` or None."""
    from wenart.furniture import group_checks as GC

    types = BEDROOM_HOSTS if kind == "bedroom" else LIVING_HOSTS
    best = None
    for f in pieces:
        if f.get("type") not in types or _top(f) > HOST_MAX_TOP_M + 1e-9:
            continue
        p = placer.piece_from_furniture(f)
        hf = GC.front_vec(p)
        front = GC.to_world(p, (0.0, -p.size[1] / 2.0))
        view = view_of(seat, front)
        (_s, (fx, fy), _w) = _seat_frame(seat)
        faces = G.angle_difference_deg(math.degrees(math.atan2(hf[1], hf[0])), math.degrees(math.atan2(-fy, -fx)))
        if (view["in_front"] and VIEW_MIN_M - 1e-9 <= view["distance_m"] <= VIEW_MAX_M + 1e-9
                and view["angle_deg"] <= VIEW_ANGLE_MAX_DEG + 1e-9 and faces <= WALL_FACE_DEG + 1e-9):
            key = (view["angle_deg"], abs(view["distance_m"] - VIEW_BEST_M), f["id"])
            if best is None or key < best[0]:
                best = (key, f, view)
    return (best[1], best[2]) if best else None


def _top(f: dict) -> float:
    """A piece's top over its floor as the scene builds it (``parametric.piece_bbox``; = decor.placer_bbox_height)."""
    from wenart.blender import parametric as P

    return float(P.piece_bbox(f)[2])


def _next_id(building: dict, level_id: str) -> str:
    from wenart.furniture import solver as SV

    return f"f_{level_id}_{SV._next_number(building, level_id):03d}"


def plan_room(building: dict, room: dict, kind: str) -> dict:
    """The media wall of one room (pure): ``{"room_id", "kind", "seat_id", "host_id", "unit" (a new tv_unit piece or
    None), "view", "why", "notes"}``. A room that has a TV unit keeps it (``host_id``, ``why`` "kept"); else the first
    seat (``seats``) with a place that passes the code checks gets a new unit, or a low chest on its TV wall hosts the
    TV; else ``why`` says what stood in the way."""
    from wenart.furniture import solver as SV

    pieces = _pieces(building, room["id"])
    rec = {"room_id": room["id"], "kind": kind, "seat_id": None, "host_id": None, "unit": None, "view": None,
           "why": "", "notes": []}
    units = [f for f in pieces if f["type"] in HOST_TYPES]
    order = seats(pieces, kind)
    if units:
        unit = sorted(units, key=lambda f: (f.get("source") != "from_documents", f["id"]))[0]
        rec.update(host_id=unit["id"], why=f"the room's TV unit {unit['id']} holds the TV (kept where it is)")
        if order:
            p = placer.piece_from_furniture(unit)
            from wenart.furniture import group_checks as GC

            seat = min(order, key=lambda s: view_of(s, GC.to_world(p, (0.0, -p.size[1] / 2.0)))["angle_deg"])
            rec["seat_id"] = seat["id"]
            rec["view"] = view_of(seat, GC.to_world(p, (0.0, -p.size[1] / 2.0)))
        return rec
    if not order:
        rec["why"] = "no sofa or double bed to face a TV"
        return rec
    tried = []
    pid = _next_id(building, room["level_id"])

    polys = []
    for f in pieces:
        try:
            polys.append((f["id"], placer.piece_from_furniture(f).polygon()))
        except (KeyError, TypeError, ValueError):
            continue

    def first_passing(seat: dict, spots: list[dict]) -> tuple[Optional[dict], int, list[str]]:
        refused, why, checked = 0, [], 0
        for s in spots:
            if checked >= SPOTS_TRIED:
                break
            piece = _unit_piece(room, s["center"], s["rotation_deg"], s["size"], seat, kind, s["view"], pid,
                                free=bool(s.get("free")))
            inches = inches_for(s["view"]["distance_m"], s["size"][0], kind) or TV_INCHES[0]
            blocked = _sight_blocked(seat, s["front"], tv_box(inches)[0], pieces, {seat["id"]})
            if blocked:
                refused += 1
                why.append(f"the view is blocked by {', '.join(blocked)}")
                continue
            mine = placer.piece_from_furniture(piece).polygon()
            hit = next((pid_ for pid_, q in polys if mine.intersection(q).area > placer.AREA_EPS), None)
            if hit is not None:                      # the cheap test first: the solver's check is a room check
                refused += 1
                why.append(f"{pid}: no_overlap with {hit}")
                continue
            checked += 1
            hard, _after = SV.verify(building, room["id"], [piece])
            if hard:
                refused += 1
                why.append(hard[0])
                continue
            return dict(piece, _view=s["view"]), refused, why
        return None, refused, why

    for seat in order:
        spots = tv_spots(building, room, seat, kind, pieces)
        piece, refused, why = first_passing(seat, spots)
        if piece is not None:
            view = piece.pop("_view")
            rec.update(seat_id=seat["id"], unit=piece, view=view,
                       why=f"a new TV unit {pid} on the wall the {seat['type'].replace('_', ' ')} {seat['id']} faces")
            return rec
        host = _host_on_wall(seat, pieces, kind)
        if host is not None:
            f, view = host
            rec.update(seat_id=seat["id"], host_id=f["id"], view=view,
                       why=f"the {f['type'].replace('_', ' ')} {f['id']} on the wall the {seat['id']} faces holds the "
                           "TV")
            return rec
        tried.append(f"{seat['id']}: {len(spots)} place(s) on the wall it faces, "
                     f"{refused} refused by the code checks (e.g. {why[0][:90] if why else '-'})" if spots else
                     f"{seat['id']}: no wall faces it {VIEW_MIN_M:g}-{VIEW_MAX_M:g} m away within "
                     f"{VIEW_ANGLE_MAX_DEG:g}° off its axis clear of windows and doors")
    # 3b. an open-plan living room: a low media console standing free on a seat's axis (a room divider)
    for seat in order:
        spots = free_spots(building, room, seat, kind)
        if not spots:
            continue
        piece, refused, why = first_passing(seat, spots)
        if piece is not None:
            view = piece.pop("_view")
            rec.update(seat_id=seat["id"], unit=piece, view=view,
                       why=(f"a new TV unit {pid} standing free on the axis of the {seat['type'].replace('_', ' ')} "
                            f"{seat['id']} (a low room divider; " + "; ".join(tried) + ")"))
            return rec
        tried.append(f"{seat['id']}: {len(spots)} free-standing place(s), {refused} refused by the code checks (e.g. "
                     f"{why[0][:90] if why else '-'})")
    rec["seat_id"] = order[0]["id"]
    rec["why"] = "no TV place: " + "; ".join(tried)
    return rec


def add_media_walls(building: dict, brief: Optional[dict] = None) -> tuple[dict, list[dict]]:
    """In place: every media room (``media_rooms``) without a TV unit or a TV host gets its TV unit (``plan_room``);
    returns ``(building, records)``. Off with the brief's ``media_wall: false``; rooms the brief keeps as drawn
    (``furnished_rooms: keep``, ``furnished_rooms_keep``) are left alone."""
    from wenart.furniture import complete as C

    values = dict(brief or {})
    settings = C.Settings(mode=str(values.get("furnished_rooms", "complete")),
                          keep=tuple(str(v) for v in values.get("furnished_rooms_keep") or ()))
    records = []
    for room, kind in media_rooms(building, brief):
        if settings.mode == "keep" or C.is_kept(room, settings):
            records.append({"room_id": room["id"], "kind": kind, "why": "kept as drawn (brief)", "unit": None,
                            "host_id": None, "seat_id": None, "view": None, "notes": []})
            continue
        rec = plan_room(building, room, kind)
        if rec["unit"] is not None:
            building.setdefault("furniture", []).append(rec["unit"])
        records.append(rec)
    if records:
        building["warnings"] = list(building.get("warnings") or []) + [
            f"{r['room_id']}: media wall: {r['why']}" for r in records if r["unit"] is None and not r["host_id"]
            and r["why"] and not r["why"].startswith("kept")]
    return building, records


# --------------------------------------------------------------------------
# The TV (decor)
# --------------------------------------------------------------------------

def tv_hosts(building: dict, room: dict, pieces: list[dict], brief: Optional[dict] = None) -> list[tuple[dict, dict]]:
    """``[(host, plan)]`` of the room: every TV unit, and the chest a media room's plan names as the TV's host."""
    out = [(f, {}) for f in pieces if f.get("type") in HOST_TYPES and _built(f)]
    kinds = {r["id"]: k for r, k in media_rooms(building, brief)}
    if room["id"] in kinds and not out:
        for seat in seats(pieces, kinds[room["id"]]):
            host = _host_on_wall(seat, pieces, kinds[room["id"]])
            if host is not None:
                out.append((host[0], {"seat_id": seat["id"], "host_id": host[0]["id"]}))
                break
    return out


def tv_item(room: dict, host: dict, seat: Optional[dict], kind: str,
            max_width: Optional[float] = None) -> Optional[dict]:
    """The TV on ``host`` (pure; module docstring, step 4), an item without an id, or None when not even the smallest
    set fits the host's width (or ``max_width``: the free span between what stands on its top)."""
    from wenart.furniture import group_checks as GC

    w, d = (float(v) for v in host["footprint"]["size"][:2])
    p = placer.piece_from_furniture(host)
    view = view_of(seat, GC.to_world(p, (0.0, -p.size[1] / 2.0))) if seat is not None else None
    dist = view["distance_m"] if view and view["in_front"] else None
    span = w - 2 * TOP_MARGIN_M if max_width is None else min(w - 2 * TOP_MARGIN_M, float(max_width))
    inches = inches_for(dist, span, kind)
    if inches is None:
        return None
    tw, td, th = tv_box(inches)
    depth = max(td, d - 2 * TOP_MARGIN_M)             # the box reaches the host's front: nothing stands before it
    ly = d / 2.0 - TOP_MARGIN_M - depth / 2.0
    centre = [round(v, 3) for v in GC.to_world(p, (0.0, ly))]
    facing = (f", facing the {seat['type'].replace('_', ' ')} {seat['id']} {dist:.2f} m away" if dist is not None
              else "")
    return {"kind": "decor", "type": "tv", "level_id": room["level_id"], "room_id": room["id"], "asset": None,
            "source": "added_by_ai", "method": "rule", "rule": RULE, "slot": f"{host['id']}.tv", "colour": None,
            "confidence": 0.7, "status": "verified", "host_id": host["id"], "center": list(centre),
            "rotation_deg": float(host["footprint"]["rotation_deg"]), "size": [tw, round(depth, 3), th],
            "tv": {"inches": inches, "panel_m": [tw, round(th - TV_STAND_H_M, 3)], "stand_depth_m": td,
                   "mount": "stand", "back_gap_m": TV_BACK_GAP_M},
            "reason": (f"media wall: a {inches}-inch TV on the {host['type'].replace('_', ' ')} {host['id']}{facing} "
                       f"(viewing distance 1.2-1.6 x the diagonal; user, 29 Oct 2026: \"There is no TV in "
                       f"the house\", {LESSON})")}


def _top_items(host: dict, items: list[dict]) -> list[tuple[dict, float, float]]:
    """``(item, local x, half width)`` of the items standing on a host's top (its frame; the larger side as width)."""
    from wenart.furniture import group_checks as GC

    p = placer.piece_from_furniture(host)
    out = []
    for it in items:
        if it.get("host_id") != host["id"] or not it.get("center") or not it.get("size"):
            continue
        frame = it.get("host_frame") if isinstance(it.get("host_frame"), dict) else {}
        if frame.get("support") not in (None, "top"):
            continue
        lx, _ly = GC.to_local(p, it["center"][:2])
        out.append((it, float(lx), max(float(it["size"][0]), float(it["size"][1])) / 2.0))
    return out


def tv_items(room: dict, pieces: list[dict], building: dict, items: list[dict], new_id: Callable,
             brief: Optional[dict] = None) -> list[dict]:
    """The decor stage's TVs of one room (module docstring, step 4): every TV host without a TV gets one; ``items``:
    the room's decor so far (never moved). The TV takes the free span between what stands on its host's top (the
    largest set that fits there); when not even the smallest set fits, the TV wins: it lists the items in its way in
    ``clears`` (the caller takes them out; a TV unit holds its TV)."""
    values = _brief(building, brief)
    if _off(values.get("media_wall", True)):
        return []
    kinds = {r["id"]: k for r, k in media_rooms(building, brief)}
    kind = kinds.get(room["id"], "bedroom" if room.get("room_type") == "bedroom" else "living")
    has = {it.get("host_id") for it in items if it.get("type") == "tv"}
    out = []
    for host, rec in tv_hosts(building, room, pieces, brief):
        if host["id"] in has:
            continue
        order = seats(pieces, kind)
        seat = next((f for f in pieces if f["id"] == rec.get("seat_id")), None) if rec else None
        if seat is None and order:
            p = placer.piece_from_furniture(host)
            from wenart.furniture import group_checks as GC

            seat = min(order, key=lambda s: view_of(s, GC.to_world(p, (0.0, -p.size[1] / 2.0)))["angle_deg"])
        on_top = _top_items(host, items)
        free = (2.0 * min(abs(x) - half for _i, x, half in on_top) - 2 * TOP_MARGIN_M) if on_top else None
        it = tv_item(room, host, seat, kind, max_width=free) if free is None or free > 0 else None
        if it is None and on_top:
            it = tv_item(room, host, seat, kind)
            if it is not None:
                hw = float(it["size"][0]) / 2.0 + TOP_MARGIN_M
                it["clears"] = sorted(i["id"] for i, x, half in on_top if abs(x) - half < hw and i.get("id"))
                if it["clears"]:
                    it["reason"] += f"; in place of {', '.join(it['clears'])} on its top (a TV unit holds its TV)"
        if it is None:
            continue
        it["id"] = new_id(room["level_id"])
        out.append(it)
    return out


# --------------------------------------------------------------------------
# The review
# --------------------------------------------------------------------------

def review(building: dict, brief: Optional[dict] = None) -> tuple[list[dict], int]:
    """M21 / U19 (pure): ``(findings, checked)``: a media room without a TV (major in a living room, minor in the
    master bedroom), a TV unit without its TV (minor), each with the plan's reason."""
    tvs = {d.get("host_id") for d in building.get("decor") or [] if d.get("type") == "tv"}
    out, n = [], 0
    rooms = media_rooms(building, brief)
    for room, kind in rooms:
        n += 1
        pieces = _pieces(building, room["id"])
        hosts = [f for f in pieces if f["id"] in tvs]
        if hosts:
            continue
        units = [f for f in pieces if f["type"] in HOST_TYPES]
        if units:
            out.append({"check": REVIEW_CHECK, "severity": "minor", "target": units[0]["id"], "room_id": room["id"],
                        "message": f"{room['id']}: the TV unit {units[0]['id']} holds no TV",
                        "metrics": {"model_review": True, "rule": RULE, "lesson": LESSON, "kind": kind}})
            continue
        rec = plan_room(building, room, kind)
        sev = "major" if kind == "living" else "minor"
        out.append({"check": REVIEW_CHECK, "severity": sev, "target": room["id"], "room_id": room["id"],
                    "message": f"{room['id']} ({kind}) has no TV: {rec['why']}",
                    "metrics": {"model_review": True, "rule": RULE, "lesson": LESSON, "kind": kind,
                                "seat": rec.get("seat_id"), "placeable": rec["unit"] is not None
                                or bool(rec["host_id"])}})
    return out, n
