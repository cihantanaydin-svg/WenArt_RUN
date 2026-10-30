"""Table settings and styled tops (28 Oct 2026, user on real04 run 20261028-005318-full: "More decor pieces needed,
plates on tables for example").

What (pure, deterministic; ``dress_tops`` runs in the decor stage after the AI's and the rules' items,
``decor_ai.apply``, and only when the brief's decor switch is on):

- ``table_setting``: every chair (or stool; a bench by its length) that sits at a dining table gets a place setting on
  the table in front of it: a ``plate`` (``PLATE_SIZE``) ``SETTING_INSET_M`` in from the edge on the chair's side and
  a ``glass`` (``GLASS_SIZE``) at the diner's right, further in (``GLASS_OFFSET_M``); the table's centre gets a bowl
  (``CENTRE_PICKS``) when nothing stands there.
- ``top_group``: the other tops get a small group (``GROUPS``: a coffee table, a sideboard, a console, a dresser or a
  TV unit up to three pieces, books, a tray, a vase, a bowl; a nightstand, a side table or a desk up to two small
  ones; a bookshelf a vase and a candle on its boards, ``SHELF_GROUP``), each at the free spot of the top farthest
  from what stands there.
- Every new item keeps ``ITEM_GAP_M`` from every other item on its top and stays inside the top (``TOP_MARGIN_M``),
  under the height the room's top slot allows (the ceiling, a window's sill); it is ``source: added_by_ai``,
  ``method: rule`` with its reason. The scene builder rests it on the real top by rays (``rest.place_on_top`` /
  ``place_on_shelf``) and checks it (S5): nothing floats.

Why: the rooms held one item per top part (the AI's slot), dining tables bare: the user asked for "more decor pieces
... plates on tables". Kitchen appliances (a kettle, a microwave) are the kitchen's, not decor.

29 Oct 2026 (user on real06 run 20261028-154514-full, lesson UL93: "Computer on the table would have been nice or a
laptop"; a bedroom desk with its office chair had nothing on it). What: ``work_set`` gives every desk, in any room
type, and every writing table (``work_hosts``: a table with an office chair at it, or the table of a home office
without a desk) one work set before its other tops are styled: an open laptop (``LAPTOP_BASES``: a 14-15 inch base,
the smaller one when the larger does not fit; parametric, ``parametric.work_set_parts``) on the side its seat stands
at (``seat_at``; the desk's front without a seat), ``WORK_EDGE_M`` in from that edge, at the seat (along the edge, the
nearest free place to it), its screen facing the seat (``rotation_deg``: the host's turned to that side); a home
office desk (``home_office``) gets a monitor on its stand at the back (at most ``MONITOR_REACH_M`` from the user's
edge), a keyboard in front of it and a mouse at the user's right (``work_layouts``) when they fit, else the laptop.
Every piece stays inside the top (``TOP_MARGIN_M``),
``ITEM_GAP_M`` clear of what stands there; where nothing is free a piece of decor on the top moves to the top's free
spot farthest from the set (``free_spot``; recorded in the item's ``moved_for``) and only when none is free it is left
out (``decor_dropped`` with the reason). Heights: under the ceiling, and under a window's sill behind the desk by at
most ``WORK_SILL_OVER_M`` (a laptop's screen rises over the sill as on any desk at a window; a monitor does not, so
such a desk gets the laptop). Items are ``source: added_by_ai``, ``method: rule``, ``slot: <host>.work`` with the
reason (``WORK_REASON_TAG``) and ``work_set`` (the set, the user's side, the seat). The other tops' group counts the
set as one piece. Why: decor slots only offered lamps, books and plants on a desk, the AI never a computer, and the
library holds no laptop, monitor or keyboard the audit keeps.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from wenart import geometry as G

SETTING_TYPES: tuple[str, ...] = ("plate", "glass")
PLATE_SIZE = (0.27, 0.27, 0.025)          # a dinner plate
GLASS_SIZE = (0.075, 0.075, 0.14)         # a water glass
SETTING_INSET_M = 0.04                    # a plate's rim this far in from the table's edge
GLASS_OFFSET_M = (0.21, 0.06)             # the glass from the plate's centre: to the diner's right, a little further
#                                           in (beside the plate's box: the plan boxes keep ITEM_GAP_M apart)
CHAIR_TYPES: tuple[str, ...] = ("chair", "dining_chair", "stool", "bar_stool")
BENCH_TYPES: tuple[str, ...] = ("bench",)
BENCH_SEAT_M = 0.6                        # a bench at a dining table seats one diner per this much of its length
CHAIR_REACH_M = 0.6                       # a chair whose centre is at most this far out of the table's edge sits at it
CHAIR_TUCK_M = 0.3                        # ... or at most this far under it (pushed in)
DINING_TYPES: tuple[str, ...] = ("table_dining",)
CENTRE_PICKS: tuple[str, ...] = ("bowl", "vase", "candle")
ITEM_GAP_M = 0.03                         # items on one top keep this apart
TOP_MARGIN_M = 0.03                       # = decor_ai.TOP_MARGIN_M: and this far in from its edge
GRID_STEP_M = 0.05                        # the free spots of a top are searched on this grid
# host type -> (the most items its top holds, the types a stylist adds, in order)
GROUPS: dict[str, tuple[int, tuple[str, ...]]] = {
    "table_coffee": (3, ("books", "tray", "bowl", "vase", "candle")),
    "sideboard": (3, ("vase", "books", "bowl", "candle")),
    "console_table": (3, ("vase", "books", "bowl", "candle")),
    "dresser": (3, ("vase", "books", "tray", "candle")),
    "tv_unit": (3, ("books", "vase", "candle")),
    "nightstand": (2, ("books", "candle", "plant_small")),
    "side_table": (2, ("books", "candle", "plant_small")),
    "desk": (2, ("books", "plant_small")),
}
# the style's decor density (``style.density.decor_density``: a japandi or minimal room is sparse) -> pieces more or
# fewer per top group (never under one); a sparse set table gets no centre piece
GROUP_EXTRA: dict[str, int] = {"sparse": -1, "balanced": 0, "layered": 1}
SHELF_HOSTS: tuple[str, ...] = ("bookshelf",)
SHELF_GROUP: tuple[tuple[str, int, float], ...] = (("vase", 2, -0.25), ("candle", 3, 0.25))   # type, board, x share
SHELF_ITEM_TYPES: tuple[str, ...] = ("vase", "candle", "bowl", "plant_small", "sculpture")
REASON_TAG = "28 Oct 2026, user: \"More decor pieces needed, plates on tables for example\""

# 29 Oct 2026 (lesson UL93): the work set of a desk or a writing table (module docstring)
WORK_TYPES: tuple[str, ...] = ("laptop", "monitor", "keyboard", "computer_mouse")     # = decor.WORK_DECOR_TYPES
WORK_HOST_TYPES: tuple[str, ...] = ("desk",)
WRITING_TABLE_TYPES: tuple[str, ...] = ("table_dining", "console_table")
WORK_SEAT_TYPES: tuple[str, ...] = ("office_chair",) + CHAIR_TYPES
WRITING_TABLE_MAX_SEATS = 2       # a home office's table with more seats than this is a meeting table, not a desk
# a study or a home office by its label (groups.yaml room_aliases ``other`` without the utility words), folded ASCII
WORK_ROOM_WORDS: tuple[str, ...] = ("calisma", "ofis", "buro", "study", "office", "home office")
HOME_OFFICE_ROOM_TYPES: tuple[str, ...] = ("other", "unknown")     # with a desk and no bed or sofa: a home office
# 14-15 inch laptops: base width x depth (real products 0.32-0.36 x 0.22-0.24 m, 15-18 mm), the larger first
LAPTOP_BASES: tuple[tuple[float, float], ...] = ((0.34, 0.235), (0.32, 0.22))
WORK_EDGE_M = 0.06                # the laptop's or keyboard's front edge this far in from the edge the user sits at
WORK_SILL_OVER_M = 0.15           # a laptop's screen may rise this far over the sill of a window behind the desk (a
#                                   0.22-0.24 m screen on a 0.72-0.80 m desk under a 0.90 m sill: designer value)
MONITOR_SIZE = (0.54, 0.20, 0.45)           # a 24 inch monitor on its stand (panel 0.54 x 0.32 m, 0.10 m up)
KEYBOARD_SIZE = (0.43, 0.13, 0.025)         # a full-size keyboard
MOUSE_SIZE = (0.065, 0.11, 0.038)           # a computer mouse
MOUSE_GAP_M = 0.07                # the mouse this far right of the keyboard's edge
MONITOR_BACK_M = 0.03             # the monitor's foot this far in from the back edge ...
MONITOR_REACH_M = 0.50            # ... its centre at most this far from the user's edge (a screen read at 0.5-0.7 m)
WORK_REASON_TAG = "29 Oct 2026, user: \"Computer on the table would have been nice or a laptop\""
SIDE_TURN: dict[str, float] = {"-y": 0.0, "+x": 90.0, "+y": 180.0, "-x": 270.0}   # the item's -Y towards the user


def _local(host: dict, x: float, y: float) -> tuple[float, float]:
    fp = host["footprint"]
    p = G.rotate_point((float(x), float(y)), -float(fp["rotation_deg"]), tuple(float(v) for v in fp["center"][:2]))
    return p[0] - float(fp["center"][0]), p[1] - float(fp["center"][1])


def _world(host: dict, lx: float, ly: float) -> list[float]:
    fp = host["footprint"]
    c = (float(fp["center"][0]), float(fp["center"][1]))
    p = G.rotate_point((c[0] + lx, c[1] + ly), float(fp["rotation_deg"]), c)
    return [round(p[0], 3), round(p[1], 3)]


def local_box(host: dict, item: dict) -> tuple[float, float, float, float]:
    """``(x, y, w, d)`` of an item's plan box in its host's frame (pure): its centre turned into the frame; its sides
    swapped when it is turned a quarter, its larger side both ways when it is turned otherwise (never smaller than it
    is)."""
    lx, ly = _local(host, float(item["center"][0]), float(item["center"][1]))
    size = list(item.get("size") or [0.2, 0.2])
    w, d = float(size[0]), float(size[1] if len(size) > 1 else size[0])
    host_rot = float(host["footprint"]["rotation_deg"])
    rot = float(item["rotation_deg"]) if item.get("rotation_deg") is not None else host_rot
    turn = abs(G.normalise_angle(rot - host_rot))
    turn = min(turn, 180.0 - turn)
    if abs(turn - 90.0) < 1.0:
        w, d = d, w
    elif turn > 1.0:
        w = d = max(w, d)
    return lx, ly, w, d


def boxes_clear(a, b, gap: float = ITEM_GAP_M) -> bool:
    """Two local boxes ``(x, y, w, d)`` keep ``gap`` apart on one axis at least."""
    return (abs(a[0] - b[0]) >= (a[2] + b[2]) / 2.0 + gap - 1e-9
            or abs(a[1] - b[1]) >= (a[3] + b[3]) / 2.0 + gap - 1e-9)


def inside_top(host: dict, box, margin: float = TOP_MARGIN_M) -> bool:
    w, d = (float(v) for v in host["footprint"]["size"][:2])
    return (abs(box[0]) + box[2] / 2.0 <= w / 2.0 - margin + 1e-9
            and abs(box[1]) + box[3] / 2.0 <= d / 2.0 - margin + 1e-9)


def diners(table: dict, pieces: list[dict]) -> list[tuple[str, float, float]]:
    """``(seat id, local x, local y)`` of the places at a dining table (pure): every chair or stool whose centre is at
    most ``CHAIR_REACH_M`` out of the table's edge (or ``CHAIR_TUCK_M`` under it), a bench one place per
    ``BENCH_SEAT_M`` of its length along the side it stands at."""
    w, d = (float(v) for v in table["footprint"]["size"][:2])
    out = []
    for p in sorted(pieces, key=lambda q: q["id"]):
        if p.get("id") == table.get("id") or p.get("type") not in CHAIR_TYPES + BENCH_TYPES:
            continue
        lx, ly = _local(table, *p["footprint"]["center"][:2])
        out_x, out_y = abs(lx) - w / 2.0, abs(ly) - d / 2.0
        if not -CHAIR_TUCK_M <= max(out_x, out_y) <= CHAIR_REACH_M:
            continue                                     # too far from the table, or deep under it
        if p["type"] in BENCH_TYPES:
            bw = max(float(v) for v in p["footprint"]["size"][:2])
            n = max(1, int(bw / BENCH_SEAT_M))
            for k in range(n):
                off = -bw / 2.0 + bw * (k + 0.5) / n
                if out_y >= out_x:
                    out.append((f"{p['id']}#{k + 1}", lx + off, ly))
                else:
                    out.append((f"{p['id']}#{k + 1}", lx, ly + off))
            continue
        out.append((p["id"], lx, ly))
    return out


def setting_boxes(table: dict, lx: float, ly: float) -> tuple[Optional[tuple], Optional[tuple]]:
    """The plate's and the glass's local boxes for a diner at local ``(lx, ly)`` (pure): the side of the table the
    diner sits at, the plate ``SETTING_INSET_M`` in from that edge in front of them (along the side as far as the
    table goes), the glass at their right, further in; None for a piece that leaves the top."""
    w, d = (float(v) for v in table["footprint"]["size"][:2])
    r = PLATE_SIZE[0] / 2.0
    if abs(ly) - d / 2.0 >= abs(lx) - w / 2.0:              # a long side (local +-Y)
        s = 1.0 if ly >= 0 else -1.0
        px = max(-w / 2.0 + r + SETTING_INSET_M, min(w / 2.0 - r - SETTING_INSET_M, lx))
        py = s * (d / 2.0 - SETTING_INSET_M - r)
        face = (0.0, -s)
    else:                                                    # an end (local +-X)
        s = 1.0 if lx >= 0 else -1.0
        px = s * (w / 2.0 - SETTING_INSET_M - r)
        py = max(-d / 2.0 + r + SETTING_INSET_M, min(d / 2.0 - r - SETTING_INSET_M, ly))
        face = (-s, 0.0)
    right = (face[1], -face[0])
    plate = (px, py, PLATE_SIZE[0], PLATE_SIZE[1])
    gx = px + right[0] * GLASS_OFFSET_M[0] + face[0] * GLASS_OFFSET_M[1]
    gy = py + right[1] * GLASS_OFFSET_M[0] + face[1] * GLASS_OFFSET_M[1]
    glass = (gx, gy, GLASS_SIZE[0], GLASS_SIZE[1])
    return (plate if inside_top(table, plate, 0.0) else None), (glass if inside_top(table, glass) else None)


def free_spot(host: dict, size: tuple[float, float], taken: list[tuple]) -> Optional[tuple[float, float]]:
    """The free spot of a host's top for a ``size`` box (pure): on a ``GRID_STEP_M`` grid inside the top
    (``TOP_MARGIN_M``), ``ITEM_GAP_M`` clear of every taken box; the one farthest from them (the top's edge counts),
    the back half and the middle first on a tie; None when none is free."""
    w, d = (float(v) for v in host["footprint"]["size"][:2])
    bw, bd = (float(v) for v in size)
    ex, ey = (w - 2 * TOP_MARGIN_M - bw) / 2.0, (d - 2 * TOP_MARGIN_M - bd) / 2.0
    nx = max(0, int(ex / GRID_STEP_M))
    ny = max(0, int(ey / GRID_STEP_M))
    # 29 Oct 2026: the grid and the places against the top's margins (a strip beside a laptop is rarely on the grid)
    xs = sorted({i * GRID_STEP_M for i in range(-nx, nx + 1)} | ({-ex, ex} if ex > 0 else set()))
    ys = sorted({j * GRID_STEP_M for j in range(-ny, ny + 1)} | ({-ey, ey} if ey > 0 else set()))
    best, best_key = None, None
    for x in xs:
        for y in ys:
            i, j = x / GRID_STEP_M, y / GRID_STEP_M
            box = (x, y, bw, bd)
            if not inside_top(host, box) or not all(boxes_clear(box, t) for t in taken):
                continue
            room = min([math.hypot(box[0] - t[0], box[1] - t[1]) - (max(bw, bd) + max(t[2], t[3])) / 2.0
                        for t in taken] or [10.0])
            key = (round(room, 3), j, -abs(i), -i)
            if best_key is None or key > best_key:
                best, best_key = (box[0], box[1]), key
    return best


def _sized(dtype: str, sizes: dict, max_h: Optional[float], max_wd: Optional[tuple] = None) -> Optional[list]:
    """The default box of a surface type (``sizes``: ``decor_ai.SURFACE_SIZES``), scaled down (never up) to the
    height and plan room there is; None under its smallest box."""
    default, lowest = sizes[dtype]
    s = 1.0
    if max_h is not None:
        s = min(s, float(max_h) / default[2])
    if max_wd is not None:
        s = min(s, float(max_wd[0]) / default[0], float(max_wd[1]) / default[1])
    box = [round(default[k] * s, 3) for k in range(3)]
    if any(box[k] < lowest[k] - 1e-9 for k in range(3)):
        return None
    return box


def _item(room: dict, host: dict, dtype: str, centre, size, slot: str, reason: str, tag: str = REASON_TAG,
          **extra) -> dict:
    return dict({"kind": "decor", "type": dtype, "level_id": room["level_id"], "room_id": room["id"], "asset": None,
                 "source": "added_by_ai", "method": "rule", "slot": slot, "colour": None, "confidence": 0.7,
                 "status": "verified", "host_id": host["id"], "center": list(centre),
                 "rotation_deg": float(host["footprint"]["rotation_deg"]), "size": [float(v) for v in size],
                 "reason": f"{reason} ({tag})"}, **extra)


def table_setting(room: dict, table: dict, pieces: list[dict], on_top: list[dict], sizes: dict,
                  max_h: Optional[float] = None, centre: bool = True) -> list[dict]:
    """The place settings of a dining table and (``centre``) its centre piece (module docstring; items without
    ids)."""
    taken = [local_box(table, it) for it in on_top]
    out = []
    for seat, lx, ly in diners(table, pieces):
        plate, glass = setting_boxes(table, lx, ly)
        if plate is None or not all(boxes_clear(plate, t) for t in taken):
            continue
        taken.append(plate)
        out.append(_item(room, table, "plate", _world(table, plate[0], plate[1]), PLATE_SIZE,
                         f"{table['id']}.setting.{seat}", f"a place setting at {seat}: a plate on the table in front "
                                                          "of it"))
        if glass is not None and (max_h is None or GLASS_SIZE[2] <= max_h) and all(boxes_clear(glass, t)
                                                                                    for t in taken):
            taken.append(glass)
            out.append(_item(room, table, "glass", _world(table, glass[0], glass[1]), GLASS_SIZE,
                             f"{table['id']}.setting.{seat}", f"a place setting at {seat}: a glass at the diner's "
                                                              "right"))
    if centre and out and not any(abs(t[0]) < 0.15 and abs(t[1]) < 0.15
                                  for t in [local_box(table, it) for it in on_top]):
        for dtype in CENTRE_PICKS:
            size = _sized(dtype, sizes, max_h)
            if size is None:
                continue
            box = (0.0, 0.0, size[0], size[1])
            if inside_top(table, box) and all(boxes_clear(box, t) for t in taken):
                out.append(_item(room, table, dtype, _world(table, 0.0, 0.0), size, f"{table['id']}.centre_piece",
                                 f"a {dtype} in the middle of the set table"))
                break
    return out


def top_group(room: dict, host: dict, on_top: list[dict], sizes: dict, max_h: Optional[float] = None,
              density: str = "balanced") -> list[dict]:
    """A host's top up to its group (``GROUPS``, one piece fewer or more by the style's ``density``,
    ``GROUP_EXTRA``; module docstring; items without ids)."""
    most, picks = GROUPS[host["type"]]
    most = max(1, most + GROUP_EXTRA.get(str(density), 0))
    taken = [local_box(host, it) for it in on_top]
    have_types = {it.get("type") for it in on_top}
    # 29 Oct 2026: a desk's work set (a monitor, its keyboard and mouse) counts as one piece of the group
    count = len(taken) - max(0, sum(1 for it in on_top if it.get("type") in WORK_TYPES) - 1)
    out = []
    for dtype in picks:
        if count >= most:
            break
        if dtype in have_types:
            continue
        w, d = (float(v) for v in host["footprint"]["size"][:2])
        size = _sized(dtype, sizes, max_h, (w - 2 * TOP_MARGIN_M, d - 2 * TOP_MARGIN_M))
        if size is None:
            continue
        spot = free_spot(host, (size[0], size[1]), taken)
        if spot is None:
            continue
        taken.append((spot[0], spot[1], size[0], size[1]))
        count += 1
        have_types.add(dtype)
        out.append(_item(room, host, dtype, _world(host, *spot), size, f"{host['id']}.group",
                         f"a styled {host['type'].replace('_', ' ')}: a {dtype} beside what stands on it"))
    return out


def shelf_group(room: dict, host: dict, on_host: list[dict], sizes: dict) -> list[dict]:
    """Small pieces on a bookshelf's boards (``SHELF_GROUP``; items without ids); the scene builder finds the board
    and its clearance by rays (``rest.place_on_shelf``)."""
    have = {it.get("type") for it in on_host}
    w, d = (float(v) for v in host["footprint"]["size"][:2])
    out = []
    for dtype, board, share in SHELF_GROUP:
        if dtype in have:
            continue
        size = _sized(dtype, sizes, 0.25, (w / 3.0, max(0.05, d - 2 * TOP_MARGIN_M)))
        if size is None:
            continue
        out.append(_item(room, host, dtype, _world(host, share * w, 0.0), size, f"{host['id']}.shelf{board}",
                         f"a small {dtype} on board {board} of the shelf",
                         host_frame={"support": "shelf", "u": share, "v": 0.0, "turn_deg": 0.0, "lean_deg": 0.0,
                                     "shelf": board}))
    return out


# ------------------------------------------------------------------------------- 29 Oct 2026: the work set (UL93)
def seat_at(host: dict, pieces: list[dict]) -> Optional[tuple[dict, str]]:
    """``(seat, side)``: the seat a person works from at a desk or a table (pure): an office chair first, else the
    nearest chair or stool whose centre is at most ``CHAIR_REACH_M`` out of the host's edge (or ``CHAIR_TUCK_M`` under
    it); ``side`` is the host's side it stands at (local ``-y`` = the front, ``+y``, ``-x``, ``+x``). None without
    one."""
    w, d = (float(v) for v in host["footprint"]["size"][:2])
    best = None
    for p in pieces:
        if p.get("id") == host.get("id") or p.get("type") not in WORK_SEAT_TYPES or not p.get("footprint") \
                or p.get("build") is False:
            continue
        lx, ly = _local(host, *p["footprint"]["center"][:2])
        out_x, out_y = abs(lx) - w / 2.0, abs(ly) - d / 2.0
        if not -CHAIR_TUCK_M <= max(out_x, out_y) <= CHAIR_REACH_M:
            continue
        side = ("+y" if ly >= 0 else "-y") if out_y >= out_x else ("+x" if lx >= 0 else "-x")
        key = (p["type"] != "office_chair", round(math.hypot(lx, ly), 3), str(p.get("id")))
        if best is None or key < best[0]:
            best = (key, p, side)
    return (best[1], best[2]) if best else None


def home_office(room: dict, pieces: list[dict]) -> bool:
    """A study or a home office (pure): its label names one (``WORK_ROOM_WORDS``), or a room of
    ``HOME_OFFICE_ROOM_TYPES`` that holds a desk and no bed or sofa."""
    from wenart.furniture import program as PR     # lazy: program reads the groups

    if PR._alias_hit(PR._label_words(room), list(WORK_ROOM_WORDS)) is not None:
        return True
    types = {p.get("type") for p in pieces if p.get("build") is not False}
    return (str(room.get("room_type") or "unknown") in HOME_OFFICE_ROOM_TYPES and "desk" in types
            and not types & {"bed_double", "bed_single", "bunk_bed", "sofa", "sofa_corner"})


def work_hosts(room: dict, pieces: list[dict], usable: Optional[Callable] = None) -> list[dict]:
    """The desks and writing tables of a room that take a work set (pure; module docstring), in id order: every desk,
    a table (``WRITING_TABLE_TYPES``) with an office chair at it, and in a home office without a desk its table with at
    most ``WRITING_TABLE_MAX_SEATS`` seats. ``usable`` (the decor stage's ``decor_ai.usable_host``) filters the hosts,
    else a host is any built piece; none in an open-air room (an indoor piece outside is Argus U9's)."""
    from wenart.blender import outdoor as OD

    if OD.open_air_room(room):
        return []
    ok = [p for p in pieces if p.get("footprint") and p.get("build") is not False and (usable is None or usable(p))]
    desks = [p for p in ok if p.get("type") in WORK_HOST_TYPES]
    out = list(desks)
    office = None
    for p in ok:
        if p.get("type") not in WRITING_TABLE_TYPES:
            continue
        seat = seat_at(p, pieces)
        if seat is not None and seat[0].get("type") == "office_chair":
            out.append(p)
            continue
        if not desks:
            office = home_office(room, pieces) if office is None else office
            if office and len(diners(p, pieces)) <= WRITING_TABLE_MAX_SEATS:
                out.append(p)
    return sorted(out, key=lambda p: str(p["id"]))


def _side_dims(host: dict, side: str) -> tuple[float, float]:
    """The top's ``(width along the user's edge, depth away from the user)``."""
    w, d = (float(v) for v in host["footprint"]["size"][:2])
    return (w, d) if side in ("-y", "+y") else (d, w)


def _side_box(u: float, v: float, size, turn: float) -> tuple[float, float, float, float]:
    """A piece at ``(u, v)`` of the user's frame (the user at -v, their right at +u) as a local box of the host."""
    lx, ly = G.rotate_point((u, v), turn, (0.0, 0.0))
    w, d = float(size[0]), float(size[1])
    if abs(G.normalise_angle(turn)) % 180.0 > 1.0:
        w, d = d, w
    return (lx, ly, w, d)


def _laptop(base) -> tuple[float, float, float]:
    from wenart.blender import parametric as P   # pure Python (no bpy)

    return P.laptop_box(*base)


def work_layouts(office: bool) -> list[tuple[str, list[tuple[str, tuple, str, float]]]]:
    """The work sets to try, in order (pure): ``(set, [(type, size, edge, along)])``; ``edge`` front (its front edge
    ``WORK_EDGE_M`` in from the user's edge) or back (``MONITOR_BACK_M`` in from the far edge), ``along`` its offset
    to the user's right. A home office first tries the monitor set, then the laptops; any other desk the laptops."""
    sets = [(f"laptop {b[0]:.2f} x {b[1]:.2f} m", [("laptop", _laptop(b), "front", 0.0)]) for b in LAPTOP_BASES]
    if office:
        mouse_at = KEYBOARD_SIZE[0] / 2.0 + MOUSE_GAP_M + MOUSE_SIZE[0] / 2.0
        sets.insert(0, ("monitor, keyboard and mouse", [("monitor", MONITOR_SIZE, "back", 0.0),
                                                        ("keyboard", KEYBOARD_SIZE, "front", 0.0),
                                                        ("computer_mouse", MOUSE_SIZE, "front", mouse_at)]))
    return sets


def _set_boxes(host: dict, side: str, members, u: float, back: float) -> list[tuple]:
    W, D = _side_dims(host, side)
    turn = SIDE_TURN[side]
    out = []
    for _dtype, size, edge, along in members:
        if edge == "front":
            v = -D / 2.0 + WORK_EDGE_M + float(size[1]) / 2.0 + back
        else:                                   # at the back, never further than a screen is read from
            v = min(D / 2.0 - MONITOR_BACK_M - float(size[1]) / 2.0, -D / 2.0 + MONITOR_REACH_M)
        out.append(_side_box(u + along, v, size, turn))
    return out


def _fits_top(host: dict, boxes: list[tuple]) -> bool:
    return all(inside_top(host, b) for b in boxes) and all(boxes_clear(a, c) for k, a in enumerate(boxes)
                                                           for c in boxes[k + 1:])


# 30 Oct 2026 (lesson UL164; user on real04 run 20261030-043021-full: "A laptop on this table could have even nice, also
# some stationary", "Same stationary and laptop here also": four bedroom desks, library models read unverified from the
# drawing, had bare tops: the work set asked for a trusted host, ``decor_ai.usable_host``): every built desk gets its
# work set (what is built is what the render shows), and with it the desk's stationery (``desk_parts``: notebooks and a
# pen pot) beside the laptop and a desk lamp at a back corner when no lamp lights the desk (a table lamp on it, a floor
# lamp within ``DESK_LAMP_REACH_M``, a pendant hung over it); each inside the top, clear of the set and of what stands
# there, under the ceiling and a window's sill (``WORK_SILL_OVER_M``), else left out with the reason.
STATIONERY_SIZE = (0.30, 0.22, 0.17)          # = desk_parts.STATIONERY_SIZE
DESK_LAMP_SIZE = (0.24, 0.24, 0.46)           # a desk lamp: a 20-24 cm foot or shade, 42-50 cm high
DESK_LAMP_REACH_M = 1.2                       # a floor lamp this near the desk's centre lights it
DESK_REASON_TAG = "30 Oct 2026, user: \"A laptop on this table could have even nice, also some stationary\""
DESK_EXTRA_GAP_M = 0.04                       # the stationery this far beside the laptop or the keyboard


def desk_lit(host: dict, pieces: list[dict], room_items: list[dict]) -> Optional[str]:
    """What lights a desk already (pure; UL164): a table or desk lamp on it, a floor lamp within ``DESK_LAMP_REACH_M``,
    a pendant hung over it; None when nothing does."""
    hc = host["footprint"]["center"]
    for it in room_items or []:
        if it.get("type") == "table_lamp" and it.get("host_id") == host["id"]:
            return f"the table lamp {it.get('id')} on it"
        if it.get("type") == "pendant_light" and str(it.get("slot") or "").endswith(f"over_{host['id']}"):
            return f"the pendant {it.get('id')} over it"
        if it.get("type") == "desk_wall_unit" and it.get("desk_id") == host["id"]:
            return f"the LED strip of the wall unit {it.get('id')} over it"
    for p in list(pieces or []) + [it for it in room_items or [] if it.get("type") == "floor_lamp"]:
        c = (p.get("footprint") or {}).get("center") or p.get("center")
        if p.get("type") == "floor_lamp" and c and math.dist(c[:2], hc[:2]) <= DESK_LAMP_REACH_M:
            return f"the floor lamp {p.get('id')} beside it"
    return None


def desk_extras(room: dict, host: dict, pieces: list[dict], on_top: list[dict], set_items: list[dict],
                ceiling_room: Optional[float], sill_room: Optional[float], room_items: Optional[list] = None
                ) -> tuple[list[dict], list[str]]:
    """``(items, notes)``: the stationery and, when nothing lights the desk (``desk_lit``), a desk lamp (pure; UL164,
    note above). ``on_top``: what stands on the top after the work set's moves; ``set_items``: the work set."""
    seat = seat_at(host, pieces)
    side = seat[1] if seat else "-y"
    turn = SIDE_TURN[side]
    W, D = _side_dims(host, side)
    taken = [local_box(host, it) for it in list(on_top) + list(set_items)]
    over_ceiling = math.inf if ceiling_room is None else float(ceiling_room)
    limit = over_ceiling if sill_room is None else min(over_ceiling, float(sill_room) + WORK_SILL_OVER_M)
    set_u = []
    for it in set_items:
        lx, ly = _local(host, *it["center"][:2])
        u = G.rotate_point((lx, ly), -turn, (0.0, 0.0))[0]
        half = float(it["size"][0]) / 2.0
        set_u.append((u - half, u + half))
    lo = min((a for a, _b in set_u), default=0.0)
    hi = max((b for _a, b in set_u), default=0.0)
    out, notes = [], []
    who = f"{host.get('type')} {host['id']}"

    def place(dtype, size, spots, slot, reason):
        if float(size[2]) > limit + 1e-9:
            notes.append(f"{host['id']}: no {dtype} ({float(size[2]):.2f} m high, the top leaves {max(0.0, limit):.2f} m"
                         + (" under the sill of the window behind it)" if sill_room is not None else ")"))
            return None
        for u, v in spots:
            box = _side_box(u, v, size, turn)
            if inside_top(host, box) and all(boxes_clear(box, t) for t in taken):
                taken.append(box)
                it = _item(room, host, dtype, _world(host, box[0], box[1]), size, slot, reason, tag=DESK_REASON_TAG)
                it["rotation_deg"] = round(G.normalise_angle(float(host["footprint"]["rotation_deg"]) + turn), 3)
                out.append(it)
                return it
        notes.append(f"{host['id']}: no free place for its {dtype} on the {W:.2f} x {D:.2f} m top")
        return None

    sw, sd = STATIONERY_SIZE[0], STATIONERY_SIZE[1]
    front = -D / 2.0 + WORK_EDGE_M + sd / 2.0
    back = D / 2.0 - TOP_MARGIN_M - sd / 2.0
    right, left = hi + DESK_EXTRA_GAP_M + sw / 2.0, lo - DESK_EXTRA_GAP_M - sw / 2.0
    place("stationery", STATIONERY_SIZE, [(right, front), (left, front), (right, back), (left, back)],
          f"{host['id']}.stationery", f"the stationery of {who}: notebooks and a pen pot beside its "
                                      f"{set_items[0]['type'] if set_items else 'work set'}")
    lit = desk_lit(host, pieces, room_items or [])
    if lit:
        notes.append(f"{host['id']}: no desk lamp ({lit} lights it)")
    else:
        lw, ld = DESK_LAMP_SIZE[0], DESK_LAMP_SIZE[1]
        bv = D / 2.0 - TOP_MARGIN_M - ld / 2.0
        corner_l, corner_r = -W / 2.0 + TOP_MARGIN_M + lw / 2.0, W / 2.0 - TOP_MARGIN_M - lw / 2.0
        lamp = place("table_lamp", DESK_LAMP_SIZE, [(corner_l, bv), (corner_r, bv)], f"{host['id']}.lamp",
                     f"a desk lamp at a back corner of {who}: nothing lights it")
        if lamp is not None:
            lamp["desk_lamp"] = True
    return out, notes


def work_set(room: dict, host: dict, pieces: list[dict], on_top: list[dict], ceiling_room: Optional[float] = None,
             sill_room: Optional[float] = None, office: bool = False, room_items: Optional[list] = None) -> dict:
    """The work set of one desk or writing table (pure; module docstring): ``{"items"`` (without ids), ``"moved"``
    (``[(item, new centre)]``: decor on the top that makes room), ``"dropped"`` (``[(item, reason)]``), ``"note"``}``.
    ``on_top``: the decor on the host so far; ``ceiling_room`` / ``sill_room``: the height over the top under the
    ceiling and under a window's sill behind it (``decor_ai.top_room``); a host that already holds a work piece gets
    nothing. 30 Oct 2026 (UL164): with the set, the desk's stationery and its lamp (``desk_extras``; ``room_items``:
    the room's decor, for the lamps that light it already; ``notes`` says what was left out)."""
    res = _work_set(room, host, pieces, on_top, ceiling_room, sill_room, office)
    if res["items"]:
        moved = {id(it): c for it, c in res["moved"]}
        gone = {id(it) for it, _why in res["dropped"]}
        stays = [dict(it, center=list(moved[id(it)]) + list(it["center"][2:])) if id(it) in moved else it
                 for it in on_top if id(it) not in gone]
        if not any(it.get("type") in DESK_EXTRA_TYPES for it in on_top):
            extra, notes = desk_extras(room, host, pieces, stays, res["items"], ceiling_room, sill_room, room_items)
            res["items"] += extra
            res["notes"] = notes
    return res


DESK_EXTRA_TYPES: tuple[str, ...] = ("stationery",)


def _work_set(room: dict, host: dict, pieces: list[dict], on_top: list[dict], ceiling_room: Optional[float] = None,
              sill_room: Optional[float] = None, office: bool = False) -> dict:
    """``work_set`` without the stationery and the lamp (the laptop or the monitor set; 29 Oct 2026)."""
    res: dict = {"items": [], "moved": [], "dropped": [], "note": None}
    if any(it.get("type") in WORK_TYPES for it in on_top):
        res["note"] = f"{host['id']}: its work set is there already"
        return res
    seat = seat_at(host, pieces)
    side = seat[1] if seat else "-y"
    turn = SIDE_TURN[side]
    W, D = _side_dims(host, side)
    u0 = 0.0
    if seat is not None:
        lx, ly = _local(host, *seat[0]["footprint"]["center"][:2])
        u0 = G.rotate_point((lx, ly), -turn, (0.0, 0.0))[0]
    over_ceiling = math.inf if ceiling_room is None else float(ceiling_room)
    taken = [(it, local_box(host, it)) for it in on_top]
    steps = int(W / GRID_STEP_M) + 1
    why = []
    for mode in ("free", "move", "drop"):
        for name, members in work_layouts(office):
            tall = max(float(m[1][2]) for m in members)
            limit = over_ceiling
            if sill_room is not None:
                low = any(m[0] == "monitor" for m in members)       # a monitor never rises over a sill
                limit = min(limit, float(sill_room) + (0.0 if low else WORK_SILL_OVER_M))
            if tall > limit + 1e-9:
                if mode == "free":
                    why.append(f"{name}: {tall:.2f} m high, the top leaves {max(0.0, limit):.2f} m"
                               + (" (a window behind it)" if sill_room is not None else ""))
                continue
            cands = []
            for k in range(steps):
                for du in ((0.0,) if k == 0 else (k * GRID_STEP_M, -k * GRID_STEP_M)):
                    for j in range(int(D / GRID_STEP_M) + 1):
                        back = j * GRID_STEP_M
                        boxes = _set_boxes(host, side, members, u0 + du, back)
                        if _fits_top(host, boxes):
                            cands.append((round(abs(du) + back, 4), abs(du), back, boxes))
            # the seat's place first; a centre that leaves the top is pulled in along the edge
            cands.sort(key=lambda c: c[:3])
            if not cands:
                if mode == "free":
                    why.append(f"{name}: does not fit the {W:.2f} x {D:.2f} m top")
                continue
            if mode == "free":
                hit = next((c for c in cands if all(boxes_clear(b, t) for b in c[3] for _it, t in taken)), None)
                if hit is None:
                    continue
                return _made(res, room, host, members, hit[3], side, seat, name, sill_room, [], [])
            boxes = cands[0][3]
            blockers = [(it, t) for it, t in taken if not all(boxes_clear(b, t) for b in boxes)]
            blocked = {id(it) for it, _t in blockers}
            keep = [t for it, t in taken if id(it) not in blocked]
            moved, dropped = [], []
            for it, t in sorted(blockers, key=lambda x: -x[1][2] * x[1][3]):
                spot = free_spot(host, (t[2], t[3]), keep + list(boxes))
                if spot is None:
                    if mode == "move":
                        break
                    dropped.append((it, f"no free place on {host['id']} beside its work set"))
                    continue
                keep.append((spot[0], spot[1], t[2], t[3]))
                moved.append((it, _world(host, *spot)))
            else:
                return _made(res, room, host, members, boxes, side, seat, name, sill_room, moved, dropped)
    res["note"] = f"{host['id']}: no work set fits (" + "; ".join(why or ["the top is taken"]) + ")"
    return res


def _made(res: dict, room: dict, host: dict, members, boxes, side: str, seat, name: str, sill_room, moved,
          dropped) -> dict:
    rot = round(G.normalise_angle(float(host["footprint"]["rotation_deg"]) + SIDE_TURN[side]), 3)
    who = f"facing {seat[0]['id']} ({seat[0].get('type')})" if seat else "facing the desk's front (no seat at it)"
    for (dtype, size, _edge, _along), box in zip(members, boxes):
        what = {"laptop": "an open laptop", "monitor": "a monitor on its stand at the back",
                "keyboard": "a keyboard in front of the monitor",
                "computer_mouse": "a mouse at the keyboard's right"}[dtype]
        reason = f"the work set of {host.get('type')} {host['id']}: {what}, {who}"
        if dtype == "laptop" and sill_room is not None and float(size[2]) > float(sill_room):
            reason += (f"; its screen rises {float(size[2]) - float(sill_room):.2f} m over the sill of the window "
                       f"behind it (at most {WORK_SILL_OVER_M:g} m)")
        it = _item(room, host, dtype, _world(host, box[0], box[1]), size, f"{host['id']}.work", reason,
                   tag=WORK_REASON_TAG, work_set={"set": name, "user_side": side,
                                                  "seat_id": seat[0]["id"] if seat else None})
        it["rotation_deg"] = rot
        res["items"].append(it)
    res["moved"], res["dropped"] = moved, dropped
    return res


# 29 Oct 2026 (user on real06: "There are no library and books in the house lets put some library and books", UL103):
# a bookshelf carries books on its boards. The library's bookshelf models are empty (their titles and the judges name
# no books), so every bookshelf gets a row of books (``book_set``) on each board the decor's rest finds by rays
# (``rest.place_on_shelf``), two rows on a wide shelf, around the vase and the candle of ``SHELF_GROUP``.
BOOK_BOARD_PITCH_M = 0.35         # one board per this much of the shelf's height (over its plinth)
BOOK_MAX_BOARDS = 4
WIDE_SHELF_M = 0.9                # a shelf this wide holds two rows of books per board
BOOK_SHARES: tuple[float, ...] = (-0.25, 0.22)
NO_BOOK_ROOM_TYPES: tuple[str, ...] = ("bathroom", "wc", "kitchen")


def shelf_boards(host: dict) -> int:
    """The boards a bookshelf is assumed to hold for its books (pure): by its fitted or drawn height."""
    h = None
    asset = host.get("asset") if isinstance(host.get("asset"), dict) else {}
    if len(asset.get("bbox_m") or []) > 2:
        h = float(asset["bbox_m"][2])
    elif isinstance(host.get("height"), (int, float)) and not isinstance(host.get("height"), bool):
        h = float(host["height"])
    h = h if h else 1.85
    return max(1, min(BOOK_MAX_BOARDS, int((h - 0.25) / BOOK_BOARD_PITCH_M)))


def shelf_books(room: dict, host: dict, on_host: list[dict], sizes: dict) -> list[dict]:
    """Books on every board of a bookshelf (note above; items without ids): a ``book_set`` per board (two on a
    shelf at least ``WIDE_SHELF_M`` wide) at ``BOOK_SHARES`` of its width, where nothing of the host stands on that
    board's side already."""
    if room.get("room_type") in NO_BOOK_ROOM_TYPES:
        return []
    w, d = (float(v) for v in host["footprint"]["size"][:2])
    taken = set()
    for it in on_host:
        frame = it.get("host_frame") if isinstance(it.get("host_frame"), dict) else {}
        board = int(frame.get("shelf", 1)) if frame.get("support", "shelf") == "shelf" else None
        u = float(frame.get("u", 0.0))
        if board is not None:
            taken |= {(board, s) for s in BOOK_SHARES if abs(s - u) < 0.3 or abs(u) < 0.1}
    shares = BOOK_SHARES if w >= WIDE_SHELF_M - 1e-9 else (0.0,)
    out = []
    size = _sized("book_set", sizes, 0.25, ((w - 2 * TOP_MARGIN_M) / len(shares) - 0.05,
                                            max(0.05, d - 2 * TOP_MARGIN_M)))
    if size is None:
        return []
    for board in range(shelf_boards(host)):
        for k, share in enumerate(shares):
            if (board, share) in taken or (len(shares) == 1 and any(b == board for b, _s in taken)):
                continue
            u = share if len(shares) > 1 else (0.15 if board % 2 else -0.15)
            it = _item(room, host, "book_set", _world(host, u * w, 0.0), size, f"{host['id']}.shelf{board}",
                       "", host_frame={"support": "shelf", "u": u, "v": 0.0, "turn_deg": 0.0, "lean_deg": 0.0,
                                       "shelf": board})
            it["reason"] = (f"a row of books on board {board} of the bookshelf (29 Oct 2026, user: \"There are no "
                            "library and books in the house\", UL103)")
            out.append(it)
    return out


def bare_hosts(room: dict, pieces: list[dict], building: dict, items: list[dict], new_id: Callable) -> list[dict]:
    """29 Oct 2026 (UL99, UL103): the TVs of the room's bare TV units and the books of its bookshelves without books
    (items with ids), for a room whose decor came as a twin's copy (``decor_ai.apply``): the rest of its decor stays
    the copy."""
    from wenart.furniture import decor_ai as DA
    from wenart.furniture import media_wall as MW

    out: list[dict] = MW.tv_items(room, pieces, building, items, new_id)
    booked = {it.get("host_id") for it in items + out if it.get("type") in ("book_set", "books")}
    for host in pieces:
        if host.get("type") in SHELF_HOSTS and host.get("build") is not False and host["id"] not in booked:
            on_host = [it for it in items if it.get("host_id") == host["id"] and it.get("center")]
            made = shelf_books(room, host, on_host, DA.SURFACE_SIZES)
            for it in made:
                it["id"] = new_id(room["level_id"])
            out += made
    # 30 Oct 2026 (UL164: "Same stationary and laptop here also"): a twin's copy without a work set on its desk (its twin
    # had none) gets the desk's own set, stationery and lamp
    from wenart.furniture import decor as D

    worked = {it.get("host_id") for it in items + out if it.get("type") in WORK_TYPES}
    hosts = [h for h in work_hosts(room, pieces, D.piece_is_built) if h["id"] not in worked] \
        if D.room_takes_decor(room) else []
    office = home_office(room, pieces) if hosts else False
    for host in hosts:
        on_host = [it for it in items + out if it.get("host_id") == host["id"] and it.get("center")]
        ceiling_room, sill_room = DA.top_room(host, room, building)
        got = work_set(room, host, pieces, on_host, ceiling_room, sill_room, office, room_items=items + out)
        for it, centre in got["moved"]:
            it["moved_for"] = {"from": list(it["center"][:2]), "slot": f"{host['id']}.work",
                               "reason": f"made room for the work set of {host['id']} ({WORK_REASON_TAG})"}
            it["center"] = list(centre) + list(it["center"][2:])
            it.pop("host_frame", None)
        for it, why in got["dropped"]:
            if it in (building.get("decor") or []):
                building["decor"].remove(it)
            building.setdefault("decor_dropped", []).append(
                {"id": it.get("id"), "type": it.get("type"), "host_id": host["id"], "anchor_ids": [],
                 "room_id": room["id"], "reason": f"{why} ({WORK_REASON_TAG})"})
        for it in got["items"]:
            it["id"] = new_id(room["level_id"])
        out += got["items"]
    return out


def dress_tops(room: dict, pieces: list[dict], building: dict, items: list[dict], new_id: Callable,
               slots: Optional[list] = None, density: str = "balanced", notes: Optional[list] = None) -> list[dict]:
    """The new items of one room's tops (module docstring): its desks and writing tables get their work set first
    (29 Oct 2026, ``work_set``), its dining tables set, its other tops and shelves styled; ``items``: the room's decor
    so far (never moved, except a piece on a desk that makes room for its work set: its centre changes in place, its
    ``moved_for`` says why; one with no free place left is taken out of ``items`` and listed in the building's
    ``decor_dropped``); ``slots``: the room's decor slots (``decor_ai.room_slots``, made here when not given): only a
    host with a top slot is dressed, under that slot's height (a work set under its own heights, ``decor_ai.top_room``);
    ``density``: the style's decor density (``decor_ai.room_minimum``: a sparse room gets smaller groups, no shelf
    pieces and no centre bowl on its set table); ``notes``: the room's decor notes (a desk whose set does not fit)."""
    from wenart.furniture import decor as D
    from wenart.furniture import decor_ai as DA

    if slots is None:
        slots, _notes = DA.room_slots(room, pieces, building)
    max_h: dict[str, float] = {}
    shelf_hosts: set = set()
    for s in slots:
        if s.kind == "top" and s.host_id and s.max_size:
            max_h[s.host_id] = min(max_h.get(s.host_id, math.inf), float(s.max_size[2]))
        if s.kind == "shelf" and s.host_id:
            shelf_hosts.add(s.host_id)
    by_id = {p["id"]: p for p in pieces}
    # 30 Oct 2026 (UL164): every built desk (an unverified drawn desk is built and rendered as a desk all the same)
    work = ({p["id"]: p for p in work_hosts(room, pieces, D.piece_is_built)} if D.room_takes_decor(room) else {})
    office = home_office(room, pieces) if work else False
    ctx = placer_context(building, room) if work else None
    shelf_hosts |= {p["id"] for p in pieces if p.get("type") in SHELF_HOSTS and p.get("build") is not False}   # UL103
    # 29 Oct 2026 (user on real06: "There is no TV in the house", UL99): the TV first, on every TV unit (and a media
    # room's TV chest; wenart.furniture.media_wall): a styled group then stands beside it, never before its screen
    from wenart.furniture import media_wall as MW

    out: list[dict] = MW.tv_items(room, pieces, building, items, new_id)
    gone = {i for tv in out for i in tv.get("clears") or ()}
    if gone:                                   # the TV's place on its unit: the items in its way leave (in place)
        items[:] = [it for it in items if it.get("id") not in gone]
    for hid in sorted(set(max_h) | shelf_hosts | set(work)):
        host = by_id.get(hid)
        if host is None:
            continue
        on_host = [it for it in items + out if it.get("host_id") == hid and it.get("center")]
        if hid in work:
            ceiling_room, sill_room = DA.top_room(host, room, building, ctx)
            got = work_set(room, host, pieces, on_host, ceiling_room, sill_room, office, room_items=items + out)
            if notes is not None:
                notes += got.get("notes") or []
            for it, centre in got["moved"]:
                it["moved_for"] = {"from": list(it["center"][:2]), "slot": f"{hid}.work",
                                   "reason": f"made room for the work set of {hid} ({WORK_REASON_TAG})"}
                it["center"] = list(centre) + list(it["center"][2:])
                it.pop("host_frame", None)                # its frame follows its new place (attach_host_frames)
            for it, why in got["dropped"]:
                if it in items:
                    items.remove(it)
                building.setdefault("decor_dropped", []).append(
                    {"id": it.get("id"), "type": it.get("type"), "host_id": hid, "anchor_ids": [],
                     "room_id": room["id"], "reason": f"{why} ({WORK_REASON_TAG})"})
            if got["note"] and notes is not None and not got["items"]:
                notes.append(got["note"])
            for it in got["items"]:
                it["id"] = new_id(room["level_id"])
            out += got["items"]
            on_host = [it for it in items + out if it.get("host_id") == hid and it.get("center")]
        if host["type"] in DINING_TYPES and hid not in work and hid in max_h:
            made = table_setting(room, host, pieces, on_host, DA.SURFACE_SIZES, max_h.get(hid),
                                 centre=density != "sparse")
        elif host["type"] in GROUPS and hid in max_h:
            made = top_group(room, host, on_host, DA.SURFACE_SIZES, max_h.get(hid), density)
        elif host["type"] in SHELF_HOSTS:
            made = shelf_group(room, host, on_host, DA.SURFACE_SIZES) if density != "sparse" else []
            made += shelf_books(room, host, on_host + made, DA.SURFACE_SIZES)     # 29 Oct 2026 (UL103)
        else:
            made = []
        for it in made:
            it["id"] = new_id(room["level_id"])
        out += made
    return out


def placer_context(building: dict, room: dict):
    """The room's placer context (``placer.room_context``: its windows' bands), once per room."""
    from wenart.furniture import placer

    return placer.room_context(building, room)
