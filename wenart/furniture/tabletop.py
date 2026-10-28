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
    nx = max(0, int(((w - 2 * TOP_MARGIN_M - bw) / 2.0) / GRID_STEP_M))
    ny = max(0, int(((d - 2 * TOP_MARGIN_M - bd) / 2.0) / GRID_STEP_M))
    best, best_key = None, None
    for i in range(-nx, nx + 1):
        for j in range(-ny, ny + 1):
            box = (i * GRID_STEP_M, j * GRID_STEP_M, bw, bd)
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


def _item(room: dict, host: dict, dtype: str, centre, size, slot: str, reason: str, **extra) -> dict:
    return dict({"kind": "decor", "type": dtype, "level_id": room["level_id"], "room_id": room["id"], "asset": None,
                 "source": "added_by_ai", "method": "rule", "slot": slot, "colour": None, "confidence": 0.7,
                 "status": "verified", "host_id": host["id"], "center": list(centre),
                 "rotation_deg": float(host["footprint"]["rotation_deg"]), "size": [float(v) for v in size],
                 "reason": f"{reason} ({REASON_TAG})"}, **extra)


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
    out = []
    for dtype in picks:
        if len(taken) >= most:
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


def dress_tops(room: dict, pieces: list[dict], building: dict, items: list[dict], new_id: Callable,
               slots: Optional[list] = None, density: str = "balanced") -> list[dict]:
    """The new items of one room's tops (module docstring): its dining tables set, its other tops and shelves styled;
    ``items``: the room's decor so far (never moved); ``slots``: the room's decor slots (``decor_ai.room_slots``,
    made here when not given): only a host with a top slot is dressed, under that slot's height; ``density``: the
    style's decor density (``decor_ai.room_minimum``: a sparse room gets smaller groups, no shelf pieces and no centre
    bowl on its set table)."""
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
    out: list[dict] = []
    for hid in sorted(set(max_h) | shelf_hosts):
        host = by_id.get(hid)
        if host is None:
            continue
        on_host = [it for it in items + out if it.get("host_id") == hid and it.get("center")]
        if host["type"] in DINING_TYPES:
            made = table_setting(room, host, pieces, on_host, DA.SURFACE_SIZES, max_h.get(hid),
                                 centre=density != "sparse")
        elif host["type"] in GROUPS and hid in max_h:
            made = top_group(room, host, on_host, DA.SURFACE_SIZES, max_h.get(hid), density)
        elif host["type"] in SHELF_HOSTS and density != "sparse":
            made = shelf_group(room, host, on_host, DA.SURFACE_SIZES)
        else:
            made = []
        for it in made:
            it["id"] = new_id(room["level_id"])
        out += made
    return out
