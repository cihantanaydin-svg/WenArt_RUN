"""Coffee mugs around the house (30 Oct 2026; lesson UL213, user on real06 run 20261029-100801-full: "coffee mugs
around the house also is a good decor item book and on top of a book coffee mug").

What (pure, deterministic; ``place_mugs`` runs in the decor stage, ``decor_ai.apply``, after the rooms' tops, the
details, the beds and the bathrooms are dressed): a few mugs per house, at most one place per kind (``KINDS``, in
this order) and per room, ``MUGS_MAX`` places in all (``MUGS_MAX_SPARSE`` when most rooms are sparse):

- ``kitchen``: a pair of mugs (``mug_pair``: side by side, on a small tray in the families with one,
  ``MUG_TRAY_FAMILIES``; one behind the other, ``PAIR_DEEP``, in a narrow place) at the free spot nearest the coffee
  machine, on its run first, within ``PAIR_REACH_M`` of it, that passes ``decor.worktop_item_ok`` (on the worktop
  inside the run's front box, off the hob, the sink and the tall pieces, under a wall cabinet and a window's sill,
  never on another item);
- ``seat``: on the coffee table of a seating group (else a side table by a seat, ``SIDE_REACH_M``) a mug of coffee on
  books: the books already there take the mug on their top cover (the item becomes ``mug_on_books``, its stack kept;
  ``mug.was``), else a small stack of two books with the mug goes to the top's free spot;
- ``desk``: a mug of coffee by the laptop (or the keyboard) of a desk, at the user's right, else the left, at the front
  or half-way back;
- ``bedside``: on a nightstand, a mug beside its books (either side, else in front).

Every mug stands on its support's top inside it (``tabletop.inside_top``, ``TOP_MARGIN_M`` in from its edges; the build
rests it on the real top with the whole footprint supported, UL165), ``ITEM_GAP_M`` clear of what stands there, under
the height the top leaves (its ceiling, a window's sill: ``decor_ai.top_room``). A mug on books stands on the top
book's cover (``mug_parts.on_cover``). The glaze follows the style family's accents (``FAMILY_GLAZE``); the mugs by a
seat and at a desk hold coffee, the one by the bed and one of the pair do not. Items are ``source: added_by_ai``,
``method: rule`` with the reason (``REASON_TAG``) and the record ``mug`` (the kind, the glaze, the coffee, the books, the
handle's turn). A twin room (a copy target) gets none: a few mugs per house, not one per copy.

Why: the rooms showed books, vases and candles but nothing that says someone lives there.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from wenart import geometry as G

LESSON = "UL213"
REASON_TAG = ("30 Oct 2026, user: \"coffee mugs around the house also is a good decor item book and on top of a book "
              "coffee mug\"")
KINDS: tuple[str, ...] = ("kitchen", "seat", "desk", "bedside")
MUGS_MAX = 4
MUGS_MAX_SPARSE = 2
MUG_SIZE = (0.12, 0.088, 0.096)            # = mug_parts.MUG with its handle (8.2 cm across, 9.6 cm high)
MUG_TURN_DEG = -35.0                       # the handle out to the front right (towards the user or the room)
BOOKS_SIZE = (0.24, 0.17)                  # two books under a mug (UL154's books, a little smaller than a stack of 3)
BOOKS_H_M = 0.07
BOOKS_MIN = (0.20, 0.14)                   # books this big at least take a mug on their cover
PAIR_SIZE = {True: (0.27, 0.15, 0.104), False: (0.25, 0.10, 0.096)}      # on a tray / without
PAIR_DEEP = (0.13, 0.21, 0.096)            # one mug behind the other: the place beside a machine at a run's end
PAIR_REACH_M = 1.0                         # the pair stands this near the machine (its run first, else another)
BEDSIDE_BOOK = (0.20, 0.14)                # one book with the mug on it, on a nightstand without books
BEDSIDE_BOOK_H_M = 0.035
CHILD_SUBTYPES: tuple[str, ...] = ("child",)   # ``rooms[].room_subtype``: a child's room gets no coffee mug
ROUND_TOL_M = 0.002                        # books placed inside the top's margin, their centre rounded to 1 mm
MUG_GAP_M = 0.04                           # a mug this far beside the laptop or the books
SIDE_REACH_M = 0.6                         # a side table this near a seat is by it
SEAT_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise")
COFFEE_TYPES: tuple[str, ...] = ("coffee_machine", "coffee_station")
BOOK_TYPES: tuple[str, ...] = ("books",)
# the family's glazes (``parametric.DECOR_COLOURS`` names): the first the mugs', the second the pair's other mug is
# white; after the family's accent walls (``looks.FAMILY_ACCENTS``) and its ceramics
FAMILY_GLAZE: dict[str, str] = {"scandinavian": "sage green", "japandi": "charcoal", "modern": "dusty blue",
                                "contemporary": "sand", "minimal": "white", "modern minimal": "white",
                                "industrial": "charcoal", "mediterranean": "terracotta", "classic": "navy",
                                "traditional": "navy", "rustic": "rust"}
GLAZE_DEFAULT = "dusty blue"
MUG_TRAY_FAMILIES: tuple[str, ...] = ("scandinavian", "japandi", "rustic", "mediterranean", "classic", "traditional")
TRAY_KEYS: dict[str, str] = {"japandi": "dark"}                # a dark lacquer tray; the others oak ("wood")


def glaze(family: Optional[str]) -> str:
    return FAMILY_GLAZE.get(str(family or "").casefold(), GLAZE_DEFAULT)


def record(kind: str, family: Optional[str], **extra) -> dict:
    """The item's ``mug`` record (read by ``mug_parts``)."""
    return dict({"lesson": LESSON, "kind": kind, "family": family, "glaze": glaze(family)}, **extra)


def books_height(item: dict) -> float:
    """The built height of a ``mug_on_books`` item (its stack and the mug on it), from the builder."""
    from wenart.blender import mug_parts as MG
    from wenart.blender import parametric as P

    w, d = (float(v) for v in item["size"][:2])
    parts = MG.parts("mug_on_books", w, d, 1.0, item)
    return round(P.parts_bbox(parts)[5] + 0.002, 3)


def _limit(host: dict, room: dict, building: dict) -> float:
    from wenart.furniture import decor_ai as DA

    ceiling, sill = DA.top_room(host, room, building)
    return min(ceiling, sill) if sill is not None else ceiling


def _on(host: dict, decor: list[dict]) -> list[dict]:
    return [d for d in decor if d.get("host_id") == host.get("id") and d.get("center")]


def _square(turn_deg: float) -> tuple[float, float]:
    """A mug's plan box in its host's frame: turned off the host's axes, its larger side both ways
    (``tabletop.local_box``)."""
    s = max(MUG_SIZE[0], MUG_SIZE[1])
    return (s, s) if abs(turn_deg) % 90.0 > 1.0 else (MUG_SIZE[0], MUG_SIZE[1])


# --------------------------------------------------------------------------
# the places
# --------------------------------------------------------------------------

def kitchen_pair(building: dict, room: dict, pieces: list[dict], decor: list[dict], family: Optional[str]
                 ) -> Optional[dict]:
    """The pair of mugs by the room's coffee machine (module docstring; an item without id), None without a place."""
    from wenart.furniture import decor as D

    machines = [d for d in decor if d.get("room_id") == room["id"] and d.get("type") in COFFEE_TYPES
                and d.get("host_id") and d.get("center")]
    if not machines:
        return None
    ctx = D._worktop_context(building, room, pieces)
    if ctx is None:
        return None
    tray_family = str(family or "").casefold() in MUG_TRAY_FAMILIES
    # side by side (on the family's tray, else without), else one behind the other in a narrow place
    layouts = ([(True, PAIR_SIZE[True])] if tray_family else []) + [(False, PAIR_SIZE[False]), (False, PAIR_DEEP)]
    placed = [d for d in decor if d.get("room_id") == room["id"] and d.get("host_id") and d.get("center")]
    best, tray = None, False
    for machine in sorted(machines, key=lambda m: str(m.get("id"))):
        for tray, size in layouts:
            # the machine's own run first, else another run of the room within PAIR_REACH_M of it
            cands = [c for c in D._worktop_candidates(ctx, "mug_pair", placed, size=size)
                     if G.distance(c[3]["center"], machine["center"]) <= PAIR_REACH_M + 1e-9]
            if cands:
                best = min(cands, key=lambda c: (c[1] != str(machine["host_id"]),
                                                 round(G.distance(c[3]["center"], machine["center"]), 4), c[2]))
                break
        if best is None:
            continue
        item = dict(best[3])
        item["mug"] = record("kitchen", family, coffee=True, tray=tray,
                             tray_key=TRAY_KEYS.get(str(family or "").casefold(), "wood"), on="worktop",
                             beside=machine.get("id"))
        item["reason"] = (f"a pair of mugs by the {str(machine['type']).replace('_', ' ')} {machine.get('id')} on "
                          f"{machine['host_id']}" + (", on a small tray" if tray else ""))
        return item
    return None


def seat_tops(room: dict, pieces: list[dict]) -> list[dict]:
    """The tops by a seat: the coffee tables of the room (a seat in the room), then its side tables within
    ``SIDE_REACH_M`` of a seat (pure)."""
    seats = [p for p in pieces if p.get("type") in SEAT_TYPES and p.get("footprint") and p.get("build") is not False]
    if not seats:
        return []
    ok = [p for p in pieces if p.get("footprint") and p.get("build") is not False]
    tables = sorted((p for p in ok if p.get("type") == "table_coffee"), key=lambda p: str(p["id"]))
    sides = []
    for p in ok:
        if p.get("type") != "side_table":
            continue
        gap = min(G.distance(p["footprint"]["center"], s["footprint"]["center"])
                  - (max(s["footprint"]["size"][:2]) + max(p["footprint"]["size"][:2])) / 2.0 for s in seats)
        if gap <= SIDE_REACH_M:
            sides.append((round(gap, 3), str(p["id"]), p))
    return tables + [p for _g, _i, p in sorted(sides, key=lambda t: (t[0], t[1]))]


def on_books(building: dict, room: dict, host: dict, decor: list[dict], family: Optional[str], new: bool = True
             ) -> Optional[tuple[dict, bool]]:
    """``(item, converted)``: the mug on the books of a top by a seat (module docstring): the books there (the
    returned item is that item, changed: ``converted``), else a new stack with its mug at the top's free spot; None
    when neither fits (the height the top leaves, its free room)."""
    from wenart.furniture import tabletop as TT

    limit = _limit(host, room, building)
    on_top = _on(host, decor)
    for books in sorted((d for d in on_top if d.get("type") in BOOK_TYPES), key=lambda d: str(d.get("id"))):
        w, d = (float(v) for v in books["size"][:2])
        if w < BOOKS_MIN[0] - 1e-9 or d < BOOKS_MIN[1] - 1e-9 \
                or not TT.inside_top(host, TT.local_box(host, books), TT.TOP_MARGIN_M - ROUND_TOL_M):
            continue
        hb = float(books["size"][2]) if len(books["size"]) > 2 and books["size"][2] else 0.12
        trial = dict(books, type="mug_on_books",
                     mug=record("seat", family, coffee=True, on="books", books=3, books_h=hb, seed=3,
                                handle_deg=MUG_TURN_DEG, was={"type": books["type"], "size": list(books["size"])}))
        trial["size"] = [w, d, books_height(trial)]
        if trial["size"][2] > limit + 1e-9:
            continue
        return trial, True
    if not new:
        return None
    item = {"size": [BOOKS_SIZE[0], BOOKS_SIZE[1], 0.0],
            "mug": record("seat", family, coffee=True, on="books", books=2, books_h=BOOKS_H_M, seed=5,
                          handle_deg=MUG_TURN_DEG)}
    h = books_height(item)
    if h > limit + 1e-9:
        return None
    taken = [TT.local_box(host, it) for it in on_top]
    spot = TT.free_spot(host, BOOKS_SIZE, taken)
    if spot is None:
        return None
    made = TT._item(room, host, "mug_on_books", TT._world(host, *spot), [BOOKS_SIZE[0], BOOKS_SIZE[1], h],
                    f"{host['id']}.mug", f"a mug of coffee on a small stack of books on {host['type'].replace('_', ' ')}"
                                         f" {host['id']}, by the seat", tag=REASON_TAG, mug=item["mug"])
    return made, False


def desk_mug(building: dict, room: dict, host: dict, pieces: list[dict], decor: list[dict], family: Optional[str]
             ) -> Optional[dict]:
    """A mug of coffee by the laptop of a desk (module docstring), None without a work set or a free place."""
    from wenart.furniture import tabletop as TT

    on_top = _on(host, decor)
    work = [it for it in on_top if it.get("type") in TT.WORK_TYPES]
    if not work or MUG_SIZE[2] > _limit(host, room, building) + 1e-9:
        return None
    seat = TT.seat_at(host, pieces)
    side = seat[1] if seat else "-y"
    turn = TT.SIDE_TURN[side]
    W, Dp = TT._side_dims(host, side)
    us = []
    for it in work:
        lx, ly = TT._local(host, *it["center"][:2])
        u = G.rotate_point((lx, ly), -turn, (0.0, 0.0))[0]
        us += [u - float(it["size"][0]) / 2.0, u + float(it["size"][0]) / 2.0]
    lo, hi = min(us), max(us)
    sq = _square(MUG_TURN_DEG)
    front = -Dp / 2.0 + TT.WORK_EDGE_M + sq[1] / 2.0
    right, left = hi + MUG_GAP_M + sq[0] / 2.0, lo - MUG_GAP_M - sq[0] / 2.0
    taken = [TT.local_box(host, it) for it in on_top]
    for u, v in ((right, front), (right, 0.0), (left, front), (left, 0.0)):
        box = TT._side_box(u, v, sq, turn)
        if TT.inside_top(host, box) and all(TT.boxes_clear(box, t) for t in taken):
            where = "at the user's right" if u > 0 else "at the user's left"
            it = TT._item(room, host, "mug", TT._world(host, box[0], box[1]), MUG_SIZE, f"{host['id']}.mug",
                          f"a mug of coffee by the {work[0]['type'].replace('_', ' ')} on {host['type']} {host['id']}"
                          f" ({where})", tag=REASON_TAG, mug=record("desk", family, coffee=True, on="top",
                                                                     handle_deg=0.0))
            it["rotation_deg"] = round(G.normalise_angle(float(host["footprint"]["rotation_deg"]) + turn
                                                         + MUG_TURN_DEG), 3)
            return it
    return None


def bedside_mug(building: dict, room: dict, host: dict, decor: list[dict], family: Optional[str]) -> Optional[dict]:
    """A mug beside the books of a nightstand (module docstring), None without books or a free place."""
    from wenart.furniture import tabletop as TT

    on_top = _on(host, decor)
    books = sorted((d for d in on_top if d.get("type") in BOOK_TYPES + ("book_set",)), key=lambda d: str(d.get("id")))
    limit = _limit(host, room, building)
    if MUG_SIZE[2] > limit + 1e-9:
        return None
    sq = _square(MUG_TURN_DEG)
    taken = [TT.local_box(host, it) for it in on_top]
    if not books:                                 # no book there: the mug on a book of its own
        rec = record("bedside", family, coffee=False, on="books", books=1, books_h=BEDSIDE_BOOK_H_M, seed=7,
                     handle_deg=MUG_TURN_DEG)
        h = books_height({"size": [BEDSIDE_BOOK[0], BEDSIDE_BOOK[1], 0.0], "mug": rec})
        spot = TT.free_spot(host, BEDSIDE_BOOK, taken) if h <= limit + 1e-9 else None
        if spot is None:
            return None
        return TT._item(room, host, "mug_on_books", TT._world(host, *spot), [BEDSIDE_BOOK[0], BEDSIDE_BOOK[1], h],
                        f"{host['id']}.mug", f"a mug on a book on nightstand {host['id']}", tag=REASON_TAG, mug=rec)
    for b in books:
        bx, by, bw, bd = TT.local_box(host, b)
        dx, dy = (bw + sq[0]) / 2.0 + MUG_GAP_M, (bd + sq[1]) / 2.0 + MUG_GAP_M
        for x, y in ((bx + dx, by), (bx - dx, by), (bx, by - dy)):
            box = (x, y, sq[0], sq[1])
            if TT.inside_top(host, box) and all(TT.boxes_clear(box, t) for t in taken):
                it = TT._item(room, host, "mug", TT._world(host, x, y), MUG_SIZE, f"{host['id']}.mug",
                              f"a mug beside the books {b.get('id')} on nightstand {host['id']}", tag=REASON_TAG,
                              mug=record("bedside", family, coffee=False, on="top", handle_deg=0.0,
                                         beside=b.get("id")))
                it["rotation_deg"] = round(G.normalise_angle(float(host["footprint"]["rotation_deg"]) + MUG_TURN_DEG), 3)
                return it
    return None


# --------------------------------------------------------------------------
# the house
# --------------------------------------------------------------------------

def place_mugs(building: dict, new_id: Callable, skip_rooms=(), family: Optional[str] = None) -> list[str]:
    """In place: a few mugs on the house's tops (module docstring) added to ``building["decor"]`` (a top's books that
    take a mug change type in place); returns the notes (``"<room id>: ..."``)."""
    from wenart.furniture import decor as D
    from wenart.furniture import tabletop as TT

    decor = building.setdefault("decor", [])
    if any(d.get("type") in D.MUG_DECOR_TYPES for d in decor):
        return []                                  # dressed once
    family = family or D.kitchen_family(building, []) or None
    minimum = building.get("decor_minimum") or {}
    sparse = sum(1 for v in minimum.values() if isinstance(v, dict) and v.get("density") == "sparse")
    most = MUGS_MAX_SPARSE if minimum and sparse * 2 > len(minimum) else MUGS_MAX
    rooms = [(r, p) for r, p in D.rooms_with_pieces(building)
             if r["id"] not in set(skip_rooms) and D.room_takes_decor(r) and r.get("room_subtype") not in CHILD_SUBTYPES]
    # the adults' rooms first (a double bed), then by id
    rooms.sort(key=lambda rp: (not any(p.get("type") == "bed_double" for p in rp[1]), str(rp[0]["id"])))
    used: set = set()
    notes: list[str] = []
    for kind in KINDS:
        if len(used) >= most:
            break
        tried: list[str] = []
        for room, pieces in rooms:
            if room["id"] in used:
                continue
            item, converted = None, False
            if kind == "kitchen":
                if any(d.get("room_id") == room["id"] and d.get("type") in COFFEE_TYPES for d in decor):
                    tried.append(room["id"])
                item = kitchen_pair(building, room, pieces, decor, family)
                if item is not None:                   # the worktop's front turn (decor._front_box)
                    host = next(p for p in pieces if p["id"] == item["host_id"])
                    rot = item["rotation_deg"]
                    item = TT._item(room, host, "mug_pair", item["center"], item["size"], f"{host['id']}.mug",
                                    item["reason"], tag=REASON_TAG, mug=item["mug"])
                    item["rotation_deg"] = rot
            elif kind == "seat":
                for host in seat_tops(room, pieces):
                    tried.append(room["id"])
                    got = on_books(building, room, host, decor, family)
                    if got is not None:
                        item, converted = got
                        break
            elif kind == "desk":
                for host in TT.work_hosts(room, pieces, D.piece_is_built):
                    tried.append(room["id"])
                    item = desk_mug(building, room, host, pieces, decor, family)
                    if item is not None:
                        break
            elif kind == "bedside":
                if room.get("room_type") != "bedroom":
                    continue
                for host in sorted((p for p in pieces if p.get("type") == "nightstand" and p.get("footprint")
                                    and p.get("build") is not False), key=lambda p: str(p["id"])):
                    tried.append(room["id"])
                    item = bedside_mug(building, room, host, decor, family)
                    if item is not None:
                        break
            if item is None:
                continue
            tried = []
            item["colour"] = item["mug"]["glaze"]
            if converted:
                old = next(d for d in decor if d.get("id") == item.get("id"))
                old.clear()
                old.update(item)
                old["reason"] = (str(item.get("reason") or "") + f"; a mug of coffee on its top cover ({REASON_TAG})")
                old.pop("host_frame", None)
                notes.append(f"{room['id']}: books {old['id']} on {old['host_id']} take a mug on their cover (UL213)")
            else:
                item["id"] = new_id(room["level_id"])
                decor.append(item)
                notes.append(f"{room['id']}: {item['type']} {item['id']} on {item['host_id']} ({kind}, UL213)")
            used.add(room["id"])
            break
        for rid in sorted(set(tried)):              # a host there, no free place on it (the height, the room)
            notes.append(f"{rid}: no {kind} mug: {WHY_NOT[kind]} (UL213)")
    return notes


WHY_NOT: dict[str, str] = {"kitchen": f"no free worktop within {PAIR_REACH_M:.1f} m of the coffee machine",
                           "seat": "no books to stand on and no free place on the tops by the seats",
                           "desk": "no free place by the laptop",
                           "bedside": "no free place beside the books or the lamp on the nightstands"}
