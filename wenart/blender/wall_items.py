"""Wall-hung items keep clear of the openings, the other wall items and the pieces in front of their wall (30 Oct 2026,
lessons UL134 and UL139; user on real04 run 20261029-201533-full: "These things in front of a window needs fixing"
(cam_r_L0_yatak_odasi_3_1/2/3) and "need to move the picture, TV hiding the picture not making sense"
(cam_r_L-1_salon_1)).

What the run had:

- r_L0_yatak_odasi_3 (and its twin r_L0_yatak_odasi_4): the desk's wall unit (room_details R27: wall cabinets and a
  floating shelf with books and a plant) and the large framed picture over the bed hung in front of a 2.68 m window.
  The decor stage placed both on a blank outer wall; the build then carried out the architect's answer
  ``enlarge_windows`` (``architect_actions``: the habitable bedroom had no outside glass) and cut
  ``win_arch_r_L0_yatak_odasi_3_1`` into that wall, behind them. The desk unit's own rule ("where no window is
  behind") ran at plan time only, the picture had none, and nothing in the build looked again.
- r_L-1_salon: a 1.5 m picture (dec_L-1_007, bottom 1.20 m) over the TV unit f_L-1_101, whose TV (dec_L-1_010, 0.89 m
  on the unit's top) covered the picture's lower part: the decor stage checked the wall, never what stands in front.

What (pure, deterministic; one rule for every item placed on a wall):

- ``wall items`` (``is_wall_item``): decor with a wall point or a wall support (wall art and art pairs, mirrors, wall
  TVs, clocks, the desk's wall unit, niches, intercoms, towel rails and shelves, paper holders, feature panels, leaning
  art, any other item on a wall), each with its extent on its wall face (``extent``: the span along the face, from its
  bottom to its top over the floor), and the wall-hung furniture boxes (``hung_boxes``: wall cabinets, floating
  nightstands, a hung TV or shelf: a box at least ``HUNG_MIN_M`` off the floor against a wall). Curtains and blinds
  (``EXEMPT_TYPES``) hang at a window by design; the wall plates come after the decor in the build and keep off it
  and off the openings by their own rule (``wall_plates``: model review M25, Argus U29).
- ``openings_on``: every door, window and plain opening of the face's line, found by geometry (the opening's wall
  parallel to the face, its centre within the wall's thickness: the face's own wall and its twin face, a second wall
  id on the same line), with its frame and architrave (``FRAME_M``) on the face.
- ``stacks``: the pieces standing in front of the face (their footprint within ``AGAINST_M`` of it), each with its top
  over the floor including what stands on it (``STACK_DECOR``: a TV on its unit with its screen, a lamp, a tall vase:
  decor ``STACK_MIN_H_M`` or taller): a TV on its unit, a tall cabinet, a bed's headboard, a sofa's back.
- ``conflicts``: what an item's extent, widened by ``MARGIN_M`` each side and ``Z_MARGIN_M`` up and down, overlaps:
  an opening of its line (``opening``: critical over a door, major over a window or an opening), another wall item or a
  hung box (``overlap``), a stack whose top reaches into it (``covered``). A feature panel is a wall finish
  (``FINISH_TYPES``): pieces stand in front of it by design. ``clashes(building)``: every conflict of every room.
- ``resolve(building)`` (in place; the decor stage after its details, ``decor_ai.apply``, and the build after the
  architect's answers, ``build.build``), the user's order (UL139): (1) raise the item to ``RAISE_GAP_M`` (0.20 m, in
  0.15-0.25 m) over what stands below it when its top stays ``CEILING_GAP_M`` under the ceiling (the slope over it
  too) and its centre at most ``EYE_MAX_CENTRE_M`` over the floor; (2) move it along its wall to the nearest free
  stretch (a tied item, ``TIED_TYPES``: the desk's wall unit over its desk, a TV over its unit, a mirror over its
  basin, the bathroom's rails and holders, an intercom by its door, only within its piece's span), a free item
  (``FREE_TYPES``: art, a clock, a mirror) else to another free wall of the room at eye height (``FREE_CENTRE_M``);
  (3) leave it out (``decor_dropped`` with the reason; a wall with a TV simply takes no art). Every change records
  ``wall_clear`` on the item (how, from, to, why); drawn furniture never moves (``clashes`` reports it).
- ``review(building)``: the findings of the model review's M31 and Argus' U35 (``clashes``).

Why: an item on a wall is planned on the wall the decor stage sees; the build may still cut a window into it (the
architect's answers come after the decor stage), and what stands in front of a wall decides where on it a picture can
hang, so the decor stage and the build both check the walls as they are.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G

CHECK = "UL134"
LESSONS: tuple[str, ...] = ("UL134", "UL139")
RULE = "blender.wall_items"
MARGIN_M = 0.10                 # the item's width plus this on each side stays clear of an opening's frame ...
SMALL_MARGIN_M = 0.05           # ... a small fitting's (an intercom, a paper holder, a sconce) this
SMALL_TYPES: tuple[str, ...] = ("intercom", "toilet_paper_holder", "sconce", "wall_light", "key_rack", "coat_hooks")
Z_MARGIN_M = 0.05               # ... and this above and below
# the frame and architrave beyond the opening's edge on the wall face (a door's architrave: parametric.ARCHITRAVE_W_M
# 0.065 less its 0.008 reveal; a window's trim 2-5 cm; a plain opening's lining)
FRAME_M = {"door": 0.06, "window": 0.05, "opening": 0.03}
LINE_REACH_M = 0.15             # a wall point this close to a wall face lies on it
HUNG_MIN_M = 0.25               # a furniture box this high off the floor against a wall hangs on it
AGAINST_M = 0.15                # a footprint this close to a wall face stands in front of it
CORNER_M = 0.05                 # an item's edge stays this far from the end of its wall face
STEP_M = 0.05                   # the slide along the wall in these steps
ITEM_GAP_M = 0.05               # an item moved keeps this far from the other wall items
OVERLAP_TOL_M = 0.01            # two wall items overlap when they share more than this (an art pair's prints touch)
COVER_TOL_M = 0.02              # a piece whose top reaches this far into an item covers it
RAISE_GAP_M = 0.20              # UL139: an item raised over what stands below it, this far over its top (0.15-0.25)
CEILING_GAP_M = 0.10            # = furniture.WALL_ART_CEILING_M: an item's top this far under the ceiling at least
EYE_MAX_CENTRE_M = 2.0          # ... and its centre at most this high over the floor (over a tall TV, a gallery hang)
FREE_CENTRE_M = 1.55            # a free picture, clock or mirror on another wall: its centre at eye height
STACK_MIN_H_M = 0.45            # decor on a piece this tall or taller adds to the piece's top (a TV, a lamp)
EXEMPT_TYPES: tuple[str, ...] = ("curtain", "blind", "curtain_rod", "roller_blind", "venetian_blind")
WALL_TYPES: tuple[str, ...] = ("wall_art", "art_pair", "mirror", "clock", "tv", "intercom", "desk_wall_unit",
                               "wall_niche", "art_leaning", "towel_rail", "towel_shelf", "towel_bar",
                               "toilet_paper_holder", "feature_panel", "wall_shelf", "shelf", "coat_hooks",
                               "wall_light", "sconce", "key_rack")
FREE_TYPES: tuple[str, ...] = ("wall_art", "art_pair", "clock", "mirror", "art_leaning")   # may go to another wall
TIED_TYPES: tuple[str, ...] = ("desk_wall_unit", "tv", "towel_rail", "towel_shelf", "towel_bar",
                               "toilet_paper_holder", "intercom", "feature_panel", "wall_niche")
RAISE_TYPES: tuple[str, ...] = ("wall_art", "art_pair", "clock", "mirror", "wall_shelf", "shelf")
# a wall finish (the terrazzo panel behind a vanity): its mirror, its cove light and the vanity stand on or in front of
# it by design; only the openings count for it
FINISH_TYPES: tuple[str, ...] = ("feature_panel",)
STACK_DECOR: tuple[str, ...] = ("tv",)                          # always on top of their piece's top
BASIN_TYPES: tuple[str, ...] = ("washbasin", "vanity", "bathroom_vanity", "sink_kitchen")
TIED_REACH_M = 0.60             # a tied item without a host piece on its wall slides at most this far
FLOOR_ITEMS: tuple[str, ...] = ("art_leaning", "wall_niche")    # standing on the floor against the wall


def _num(v) -> Optional[float]:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def _overlap(a0: float, a1: float, b0: float, b1: float) -> bool:
    return a0 < b1 - 1e-9 and b0 < a1 - 1e-9


def _level(building: dict, level_id) -> Optional[dict]:
    return next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), None)


def _st(line: dict, p) -> tuple[float, float]:
    dx, dy = float(p[0]) - line["a"][0], float(p[1]) - line["a"][1]
    return dx * line["u"][0] + dy * line["u"][1], dx * line["n"][0] + dy * line["n"][1]


def _xy(line: dict, s: float, d: float = 0.0) -> tuple[float, float]:
    return (line["a"][0] + line["u"][0] * s + line["n"][0] * d, line["a"][1] + line["u"][1] * s + line["n"][1] * d)


def _rect(fp: dict) -> list[tuple[float, float]]:
    return [tuple(c) for c in G.rotated_rectangle(fp["center"], fp["size"][:2], float(fp.get("rotation_deg") or 0.0))]


def room_lines(building: dict, room: dict) -> list[dict]:
    """The room's wall faces (``wall_plates.wall_lines``: the polygon edges on a wall, one straight face per line)."""
    from wenart.blender import wall_plates as WP

    walls = [w for w in building.get("walls") or [] if w.get("level_id") == room.get("level_id")]
    return WP.wall_lines(room, walls)


def openings_on(line: dict, building: dict, room: dict) -> list[dict]:
    """The doors, windows and plain openings on a wall face (pure; module docstring): ``[{"id", "type", "s0", "s1",
    "z0", "z1"}]`` over the room's floor, widened by the opening's frame (``FRAME_M``) on the face, its head too (a
    window's sill as well); found by geometry: the face's own wall and its twin face."""
    from wenart.blender import shell

    level = _level(building, room.get("level_id"))
    if level is None:
        return []
    floor_z = float(shell.room_floor_z(room, level))
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("id")}
    levels_above = any(float(lv.get("elevation") or 0.0) > float(level["elevation"])
                       for lv in building.get("levels") or [])
    out = []
    for o in building.get("openings") or []:
        if o.get("level_id") != room.get("level_id") or shell.is_virtual(o) or not o.get("center") \
                or o.get("type") not in ("door", "window", "opening"):
            continue
        w = walls.get(o.get("wall_id"))
        if w is None or G.distance(w["start"][:2], w["end"][:2]) < 1e-6:
            continue
        wx, wy = float(w["end"][0]) - float(w["start"][0]), float(w["end"][1]) - float(w["start"][1])
        wl = math.hypot(wx, wy)
        if abs(line["u"][0] * wy / wl - line["u"][1] * wx / wl) > math.sin(math.radians(3.0)):
            continue
        t = float(w.get("thickness") or 0.1)
        cx, cy, _shift = shell.opening_centre_on_wall(o, w)
        s, d = _st(line, (cx, cy))
        if not -(t + 0.10) <= d <= 0.10:
            continue
        frame = FRAME_M.get(o["type"], 0.03)
        half = float(o.get("width") or 0.0) / 2.0
        try:
            z0, z1, _ = shell.opening_vertical(o, level, levels_above)
        except (KeyError, TypeError, ValueError):
            z0, z1 = floor_z, floor_z + 2.1
        out.append({"id": o.get("id"), "type": o["type"], "s0": s - half - frame, "s1": s + half + frame,
                    "z0": float(z0) - floor_z - (frame if o["type"] == "window" else 0.0),
                    "z1": float(z1) - floor_z + frame})
    return out


def _host_top(item: dict, pieces: dict) -> Optional[float]:
    """The built top of the piece a picture or mirror hangs over (its first anchor), None without one."""
    from wenart.blender import wall_plates as WP

    for a in item.get("anchor_ids") or []:
        p = pieces.get(a)
        if p is not None and (p.get("footprint") or {}).get("center") and WP.piece_built(p):
            return (_num(p.get("mount_bottom_m")) or 0.0) + WP.piece_height(p)
    return None


def _decor_h(item: dict) -> Optional[float]:
    from wenart.blender import parametric as P

    try:
        return float(P.decor_size(str(item.get("type")), list(item.get("size") or [0.3, 0.3]))[2])
    except (TypeError, ValueError, IndexError):
        return None


def extent(item: dict, building: dict, room: dict, lines: list[dict], pieces: Optional[dict] = None) \
        -> Optional[dict]:
    """A wall item's extent on its wall face (pure): ``{"line" (index), "s", "s0", "s1", "z0", "z1", "d", "w", "h"}``
    over the room's floor, None when the item is on no wall face of the room. The face: the line its ``wall_point``
    (else its centre) lies on within ``LINE_REACH_M`` (the item's depth more for a centre). Height: a centre with a
    third value is the bottom (the rule items, ``room_details._item``); a picture or mirror hangs ``gap_m`` (0.25 m)
    over its anchor's top, at least ``min_bottom_m`` (the build's ``furniture.wall_art_placement``), else at its
    ``bottom_m``; its height is ``size[2]``, else the type's (``parametric.decor_size``) at most ``max_height_m`` (the
    room the decor stage left over it)."""
    from wenart.blender import parametric as P

    pieces = pieces if pieces is not None else {p.get("id"): p for p in building.get("furniture") or []}
    size = list(item.get("size") or [])
    if len(size) < 2 or not item.get("center"):
        return None
    try:
        w, dd, h = P.decor_size(str(item.get("type")), size)
    except (TypeError, ValueError, IndexError):
        return None
    if len(size) < 3 and _num(item.get("max_height_m")):
        h = min(h, float(item["max_height_m"]))       # the room the decor stage left over it, not its height
    ref = item.get("wall_point") or item["center"]
    reach = LINE_REACH_M if item.get("wall_point") else LINE_REACH_M + dd
    best = None
    for i, line in enumerate(lines):
        s, d = _st(line, ref)
        if abs(d) > reach or not any(a - 0.05 <= s <= b + 0.05 for a, b in line["union"]):
            continue
        if best is None or abs(d) < abs(best[2]):
            best = (i, s, d)
    if best is None:
        return None
    i, s, d = best
    c = item["center"]
    if len(c) > 2 and _num(c[2]) is not None:
        z0 = float(c[2])
    else:
        top = _host_top(item, pieces)
        z0 = top + float(item.get("gap_m", 0.25)) if top is not None else (_num(item.get("bottom_m")) or 1.0)
        if _num(item.get("min_bottom_m")) is not None:
            z0 = max(z0, float(item["min_bottom_m"]))
    return {"line": i, "s": s, "s0": s - w / 2.0, "s1": s + w / 2.0, "z0": z0, "z1": z0 + h, "d": d, "w": w, "h": h}


def is_wall_item(item: dict) -> bool:
    """A decor item placed on a wall (module docstring): not a curtain or blind; a wall point, a wall support or a
    wall type, never an item on a piece's top, seat, mattress or shelf, on the floor (but leaning art and a niche) or
    on the ceiling."""
    if item.get("type") in EXEMPT_TYPES or item.get("kind") not in (None, "decor"):
        return False
    support = (item.get("host_frame") or {}).get("support") if isinstance(item.get("host_frame"), dict) else None
    if item.get("host_id") or support in ("top", "seat", "mattress", "ceiling", "shelf"):
        return False
    if support == "floor" and not item.get("wall_point") and item.get("type") not in FLOOR_ITEMS:
        return False                     # a floor item (a plant, a basket); one with a wall point stands at its wall
    return bool(item.get("wall_point")) or support == "wall" or item.get("type") in WALL_TYPES


def piece_boxes(piece: dict) -> list[tuple[dict, float, float, bool]]:
    """``[(footprint, z0, z1, hung)]`` of a built piece (``wall_plates.piece_boxes``: a kitchen run's modules one by
    one): a box is hung when it starts ``HUNG_MIN_M`` or more off the floor and rests on no standing box of the piece
    (a worktop on its base units stands; a wall cabinet over them hangs)."""
    from shapely.geometry import Polygon

    from wenart.blender import wall_plates as WP

    boxes = sorted(WP.piece_boxes(piece), key=lambda b: b[1])
    out: list[tuple[dict, float, float, bool]] = []
    for fp, z0, z1 in boxes:
        hung = z0 >= HUNG_MIN_M
        if hung:
            poly = Polygon(_rect(fp))
            for ofp, _o0, o1, ohung in out:
                if not ohung and abs(o1 - z0) <= 0.03 and poly.intersection(Polygon(_rect(ofp))).area > 1e-4:
                    hung = False
                    break
        out.append((fp, float(z0), float(z1), hung))
    return out


def hung_boxes(building: dict, room: dict, lines: list[dict]) -> list[dict]:
    """The wall-hung furniture boxes of the room (pure): each box of a built piece (``wall_plates.piece_boxes``: a
    kitchen run's modules one by one) at least ``HUNG_MIN_M`` off the floor whose footprint comes within
    ``AGAINST_M`` of a wall face: ``[{"piece", "type", "line", "s0", "s1", "z0", "z1"}]``."""
    from wenart.blender import wall_plates as WP

    out = []
    for f in building.get("furniture") or []:
        if f.get("room_id") != room.get("id") or not WP.piece_built(f):
            continue
        for fp, z0, z1, hung in piece_boxes(f):
            if not hung:
                continue
            pts = _rect(fp)
            for i, line in enumerate(lines):
                st = [_st(line, p) for p in pts]
                if not -0.10 <= min(d for _s, d in st) <= AGAINST_M:
                    continue
                out.append({"piece": f.get("id"), "type": f.get("type"), "line": i, "s0": min(s for s, _d in st),
                            "s1": max(s for s, _d in st), "z0": z0, "z1": z1})
                break
    return out


def stacks(building: dict, room: dict, lines: list[dict]) -> list[dict]:
    """The pieces standing in front of the room's wall faces (pure; UL139): each box of a built piece standing on the
    floor (under ``HUNG_MIN_M``) whose footprint comes within ``AGAINST_M`` of a face, its top the box's top or what
    stands on the piece (decor hosted on it, ``STACK_DECOR`` or ``STACK_MIN_H_M`` tall: a TV with its screen on its
    unit, a lamp): ``[{"piece", "type", "line", "s0", "s1", "top", "by"}]``."""
    from wenart.blender import wall_plates as WP

    on_top: dict = {}
    for d in building.get("decor") or []:
        hid = d.get("host_id")
        support = (d.get("host_frame") or {}).get("support") if isinstance(d.get("host_frame"), dict) else None
        if not hid or support not in (None, "top"):
            continue
        h = _decor_h(d)
        # an item without its host frame yet counts only when it stands on the top by its type (a TV)
        if h is not None and (d.get("type") in STACK_DECOR or (support == "top" and h >= STACK_MIN_H_M - 1e-9)):
            on_top.setdefault(hid, []).append((h, d))
    out = []
    for f in building.get("furniture") or []:
        if f.get("room_id") != room.get("id") or not WP.piece_built(f):
            continue
        top_of_piece = (_num(f.get("mount_bottom_m")) or 0.0) + WP.piece_height(f)
        extra = max(on_top.get(f.get("id")) or [], key=lambda hd: hd[0], default=None)
        for fp, z0, z1, hung in piece_boxes(f):
            if hung:
                continue
            pts = _rect(fp)
            for i, line in enumerate(lines):
                st = [_st(line, p) for p in pts]
                if not -0.10 <= min(d for _s, d in st) <= AGAINST_M:
                    continue
                top, by = z1, f.get("id")
                if extra is not None and z1 >= top_of_piece - 0.02:      # the piece's top box carries its decor
                    top, by = z1 + extra[0], extra[1].get("id")
                out.append({"piece": f.get("id"), "type": f.get("type"), "line": i, "s0": min(s for s, _d in st),
                            "s1": max(s for s, _d in st), "top": top, "by": by})
                break
    return out


def _roofed(building: dict) -> dict:
    """The building with its roof's sloped ceiling (``camsearch.with_roof_ceilings``: the ceiling over an item)."""
    from wenart.blender import camsearch as CSR

    return CSR.with_roof_ceilings(building)


def _room_state(building: dict, room: dict, roofed: Optional[dict] = None) -> dict:
    lines = room_lines(building, room)
    pieces = {p.get("id"): p for p in building.get("furniture") or []}
    ops = [openings_on(line, building, room) for line in lines]
    items = []
    for d in building.get("decor") or []:
        if d.get("room_id") != room.get("id") or not is_wall_item(d):
            continue
        ext = extent(d, building, room, lines, pieces)
        if ext is not None:
            items.append((d, ext))
    return {"room": room, "lines": lines, "ops": ops, "items": items, "pieces": pieces,
            "boxes": hung_boxes(building, room, lines), "stacks": stacks(building, room, lines),
            "building": building, "roofed": roofed if roofed is not None else _roofed(building)}


def margin_of(item) -> float:
    """The clear margin each side of an item to an opening's frame: ``SMALL_MARGIN_M`` for a small fitting."""
    return SMALL_MARGIN_M if isinstance(item, dict) and item.get("type") in SMALL_TYPES else MARGIN_M


def conflicts(st: dict, item, ext: dict) -> list[dict]:
    """What a wall item's extent overlaps (module docstring): ``[{"kind": opening | overlap | covered, "id", "type",
    "s0", "s1", "z0", "z1"}]`` (``item`` the decor item, or a hung box's piece id)."""
    line_i = ext["line"]
    out = []
    m = margin_of(item)
    for o in st["ops"][line_i]:
        if _overlap(ext["s0"] - m, ext["s1"] + m, o["s0"], o["s1"]) \
                and _overlap(ext["z0"] - Z_MARGIN_M, ext["z1"] + Z_MARGIN_M, o["z0"], o["z1"]):
            out.append(dict(o, kind="opening"))
    if isinstance(item, dict) and item.get("type") in FINISH_TYPES:
        return out                                     # a wall finish: only the openings count
    tol = OVERLAP_TOL_M
    for d, e in st["items"]:
        if d is item or e["line"] != line_i or d.get("type") in FINISH_TYPES:
            continue
        if _overlap(ext["s0"] + tol, ext["s1"] - tol, e["s0"], e["s1"]) \
                and _overlap(ext["z0"] + tol, ext["z1"] - tol, e["z0"], e["z1"]):
            out.append({"kind": "overlap", "id": d.get("id"), "type": d.get("type"), "s0": e["s0"], "s1": e["s1"],
                        "z0": e["z0"], "z1": e["z1"]})
    for b in st["boxes"]:
        if b["line"] != line_i or b["piece"] == item:
            continue
        if _overlap(ext["s0"] + tol, ext["s1"] - tol, b["s0"], b["s1"]) \
                and _overlap(ext["z0"] + tol, ext["z1"] - tol, b["z0"], b["z1"]):
            out.append({"kind": "overlap", "id": b["piece"], "type": b["type"], "s0": b["s0"], "s1": b["s1"],
                        "z0": b["z0"], "z1": b["z1"]})
    for s in st["stacks"]:
        if s["line"] != line_i or (isinstance(item, dict) and item.get("desk_id") == s["piece"]):
            continue
        if _overlap(ext["s0"], ext["s1"], s["s0"], s["s1"]) and s["top"] > ext["z0"] + COVER_TOL_M \
                and ext["z0"] >= 0.05:                     # an item standing on the floor is not covered from below
            out.append({"kind": "covered", "id": s["by"], "piece": s["piece"], "type": s["type"], "s0": s["s0"],
                        "s1": s["s1"], "z0": 0.0, "z1": s["top"]})
    return out


def _finding(st: dict, target, what: str, ext: dict, c: dict) -> dict:
    room = st["room"]
    where = (f"(its extent {ext['s0']:.2f}-{ext['s1']:.2f} m along the wall, {ext['z0']:.2f}-{ext['z1']:.2f} m up")
    if c["kind"] == "opening":
        severity = "critical" if c["type"] == "door" else "major"
        msg = (f"{what} hangs over the {c['type']} {c['id']} of its wall in {room['id']} {where}, with {MARGIN_M:g} m "
               f"each side; the {c['type']} with its frame {c['s0']:.2f}-{c['s1']:.2f} m, {c['z0']:.2f}-"
               f"{c['z1']:.2f} m)")
        lesson = "UL134"
    elif c["kind"] == "overlap":
        severity, lesson = "major", "UL139"
        msg = f"{what} overlaps the wall item {c['type']} {c['id']} in {room['id']} {where})"
    else:
        severity, lesson = "major", "UL139"
        hid = "" if c["id"] == c.get("piece") else f" ({c['id']} on it)"
        msg = (f"{what} is covered by the {c['type']} {c.get('piece')}{hid} standing in front of its wall in "
               f"{room['id']}: its top {c['z1']:.2f} m reaches over the item's bottom {ext['z0']:.2f} m {where})")
    return {"kind": c["kind"], "target": target, "room_id": room["id"], "other": c["id"], "other_type": c.get("type"),
            "opening": c["id"] if c["kind"] == "opening" else None,
            "opening_type": c.get("type") if c["kind"] == "opening" else None, "severity": severity, "message": msg,
            "lesson": lesson, "s0": round(ext["s0"], 3), "s1": round(ext["s1"], 3), "z0": round(ext["z0"], 3),
            "z1": round(ext["z1"], 3)}


def clashes(building: dict) -> list[dict]:
    """Every conflict of every wall item (module docstring): decor (``source: decor``) and the wall-hung furniture
    boxes (``source: furniture``), in room order; a pair of wall items once (pure)."""
    out = []
    roofed = _roofed(building)
    for room in building.get("rooms") or []:
        if len(room.get("polygon") or []) < 3:
            continue
        st = _room_state(building, room, roofed)
        seen = set()
        for d, ext in st["items"]:
            for c in conflicts(st, d, ext):
                if c["kind"] == "overlap":
                    key = tuple(sorted((str(d.get("id")), str(c["id"]))))
                    if key in seen:
                        continue
                    seen.add(key)
                out.append(dict(_finding(st, d.get("id"), f"the {d.get('type')} {d.get('id')}", ext, c),
                                source="decor"))
        for b in st["boxes"]:
            ext = dict(b, w=b["s1"] - b["s0"], h=b["z1"] - b["z0"], s=(b["s0"] + b["s1"]) / 2.0)
            for c in conflicts(st, b["piece"], ext):
                if c["kind"] != "opening":
                    continue                                    # pieces against each other: the placer's checks
                out.append(dict(_finding(st, b["piece"], f"the hung {b['type']} {b['piece']}", ext, c),
                                source="furniture"))
    return out


def _tied_span(item: dict, ext: dict, st: dict) -> tuple[float, float]:
    """The centre range a tied item may slide in on its wall (module docstring): its host piece's span on the face
    (the desk under the wall unit, the unit under a TV, the basin under a mirror), else ``TIED_REACH_M`` around it."""
    line = st["lines"][ext["line"]]
    host_id = item.get("desk_id") or item.get("host_id") or next(iter(item.get("anchor_ids") or []), None)
    host = st["pieces"].get(host_id) if host_id else None
    if host is not None and (host.get("footprint") or {}).get("center"):
        ss = [_st(line, c)[0] for c in _rect(host["footprint"])]
        lo, hi = min(ss) + ext["w"] / 2.0, max(ss) - ext["w"] / 2.0
        if lo > hi:                                       # an item wider than its piece stays centred on it
            lo = hi = (min(ss) + max(ss)) / 2.0
        return lo, hi
    return ext["s"] - TIED_REACH_M, ext["s"] + TIED_REACH_M


def _ceiling_over(st: dict, line_i: int, s: float, w: float) -> float:
    """The ceiling over the floor above a stretch of a face (the level's; under the roof the slope over it)."""
    room = st["room"]
    level = _level(st["roofed"], room.get("level_id")) or {}
    flat = float(level.get("ceiling_height") or 2.7)
    planes = level.get("ceiling_planes") or []
    if not planes or room.get("id") in set(level.get("open_rooms") or ()):
        return flat
    line = st["lines"][line_i]
    elev = float(level.get("elevation") or 0.0)
    pts = [_xy(line, s + k * w / 2.0, 0.05) for k in (-1, 0, 1)]
    return min(flat, min(min(float(a) * x + float(b) * y + float(c) for a, b, c in planes) - elev for x, y in pts))


def _clear_at(st: dict, item, ext: dict) -> bool:
    return not conflicts(st, item, ext)


def _raise(st: dict, item: dict, ext: dict) -> Optional[float]:
    """UL139 (1): the bottom that clears what the item overlaps from below (a covering piece's top, a wall item or an
    opening under it) by ``RAISE_GAP_M``, when its top stays ``CEILING_GAP_M`` under the ceiling and its centre at most
    ``EYE_MAX_CENTRE_M`` up and nothing else is in the way there; None otherwise."""
    if item.get("type") not in RAISE_TYPES:
        return None
    below = [c["z1"] for c in conflicts(st, item, ext) if c["z0"] < ext["z0"] + 0.5 * ext["h"]]
    if not below:
        return None
    z0 = max(below) + RAISE_GAP_M
    if z0 + ext["h"] / 2.0 > EYE_MAX_CENTRE_M + 1e-9 or \
            z0 + ext["h"] > _ceiling_over(st, ext["line"], ext["s"], ext["w"]) - CEILING_GAP_M + 1e-9:
        return None
    trial = dict(ext, z0=z0, z1=z0 + ext["h"])
    return z0 if _clear_at(st, item, trial) else None


def _blocked(st: dict, line_i: int, z0: float, z1: float, item) -> list[tuple[float, float]]:
    """The stretches of a face an item at ``z0``-``z1`` may not cover: the openings (with the margin), the other wall
    items and the hung boxes at its height, the pieces in front whose top reaches its bottom (``stacks``)."""
    m = margin_of(item)
    out = [(o["s0"] - m, o["s1"] + m) for o in st["ops"][line_i]
           if _overlap(z0 - Z_MARGIN_M, z1 + Z_MARGIN_M, o["z0"], o["z1"])]
    if item.get("type") in FINISH_TYPES:
        return out
    out += [(e["s0"] - ITEM_GAP_M, e["s1"] + ITEM_GAP_M) for d, e in st["items"]
            if d is not item and e["line"] == line_i and d.get("type") not in FINISH_TYPES
            and _overlap(z0, z1, e["z0"], e["z1"])]
    out += [(b["s0"] - ITEM_GAP_M, b["s1"] + ITEM_GAP_M) for b in st["boxes"]
            if b["line"] == line_i and _overlap(z0, z1, b["z0"], b["z1"])]
    if z0 >= 0.05:
        out += [(s["s0"], s["s1"]) for s in st["stacks"] if s["line"] == line_i and s["top"] > z0 + COVER_TOL_M
                and item.get("desk_id") != s["piece"]]
    return out


def _free_centre(st: dict, line_i: int, w: float, z0: float, z1: float, want: float, lo: float, hi: float,
                 item) -> Optional[float]:
    """The centre nearest ``want`` within ``lo``-``hi`` where an item ``w`` wide at ``z0``-``z1`` fits on the face:
    inside one of its wall stretches (``CORNER_M`` in from its ends) and clear of ``_blocked``; None without one."""
    line = st["lines"][line_i]
    blocked = _blocked(st, line_i, z0, z1, item)
    mid = (min(a for a, _b in line["union"]) + max(b for _a, b in line["union"])) / 2.0
    best = None
    for a, b in line["union"]:
        c_lo, c_hi = max(a + CORNER_M + w / 2.0, lo), min(b - CORNER_M - w / 2.0, hi)
        if c_lo > c_hi + 1e-9:
            continue
        # steps out from ``want`` both ways and the stretch's ends; ties go to the wall's middle (a mirrored twin
        # room resolves to the mirrored place: nothing here depends on the face's direction)
        start = min(max(want, c_lo), c_hi)
        n = int(math.ceil((c_hi - c_lo) / STEP_M)) + 1
        cands = {round(start, 4), round(c_lo, 4), round(c_hi, 4)}
        cands |= {round(start + sg * k * STEP_M, 4) for k in range(1, n + 1) for sg in (-1, 1)
                  if c_lo - 1e-9 <= start + sg * k * STEP_M <= c_hi + 1e-9}
        for c in sorted(cands, key=lambda c: (round(abs(c - want), 4), round(abs(c - mid), 4), c)):
            if all(not _overlap(c - w / 2.0, c + w / 2.0, b0, b1) for b0, b1 in blocked):
                if best is None or (round(abs(c - want), 4), round(abs(c - mid), 4)) < \
                        (round(abs(best - want), 4), round(abs(best - mid), 4)):
                    best = c
                break
    return best


def _rotation_into(n) -> float:
    return round(G.normalise_angle(math.degrees(math.atan2(float(n[0]), -float(n[1])))), 3)


def _set_bottom(item: dict, z0: float) -> None:
    c = list(item["center"])
    if len(c) > 2:
        c[2] = round(z0, 3)
        item["center"] = c
    else:
        item["bottom_m"] = round(z0, 3)
        item["min_bottom_m"] = round(z0, 3)          # the build hangs it over its piece's top + gap, at least here


def _record(item: dict, how: str, why: str, was: dict, moved_m: float) -> dict:
    rec = {"rule": RULE, "lessons": list(LESSONS), "how": how, "reason": why, "from": was,
           "to": {"wall_point": item.get("wall_point"), "center": item.get("center"),
                  "rotation_deg": item.get("rotation_deg"), "bottom_m": item.get("bottom_m")},
           "moved_m": round(moved_m, 3)}
    item["wall_clear"] = rec
    return rec


def _move(item: dict, ext: dict, st: dict, line_i: int, s: float, z0: Optional[float], why: str) -> dict:
    """In place: the item to centre ``s`` on face ``line_i`` (its offset from the face kept; on another face turned to
    face the room, its bottom ``z0``); returns the ``wall_clear`` record."""
    old_line = st["lines"][ext["line"]]
    line = st["lines"][line_i]
    was = {"wall_point": item.get("wall_point"), "center": item.get("center"),
           "rotation_deg": item.get("rotation_deg"), "wall_id": item.get("wall_id"), "bottom_m": item.get("bottom_m")}
    c = list(item["center"])
    _s_c, d_c = _st(old_line, c)
    wp_d = _st(old_line, item["wall_point"])[1] if item.get("wall_point") else 0.0
    if item.get("wall_point"):
        item["wall_point"] = [round(v, 3) for v in _xy(line, s, wp_d)]
    xy = _xy(line, s, d_c)
    item["center"] = [round(xy[0], 3), round(xy[1], 3)] + c[2:]
    if line_i != ext["line"]:
        item["rotation_deg"] = _rotation_into(line["n"])
        item.pop("anchor_ids", None)                  # off its piece's wall: no longer hung over it
        item.pop("gap_m", None)
        item.pop("min_bottom_m", None)
        if z0 is not None:
            _set_bottom(item, z0)
        item["wall_id"] = line.get("wall_id")
    item.pop("host_frame", None)                      # re-made from the new place (decor.attach_host_frames)
    return _record(item, "moved", why, was, G.distance(_xy(old_line, ext["s"]), _xy(line, s)))


def _why(c: dict, stage: str) -> str:
    if c["kind"] == "opening":
        return (f"over the {c['type']} {c['id']} of its wall ({stage}): a wall item keeps its width + {MARGIN_M:g} m "
                f"each side and its height clear of every door, window and frame (UL134)")
    if c["kind"] == "overlap":
        return f"over the wall item {c['type']} {c['id']} ({stage}): wall items never overlap (UL139)"
    return (f"covered by the {c['type']} {c.get('piece')} in front of its wall, its top {c['z1']:.2f} m ({stage}): "
            f"a wall item stays clear of what stands in front of it (UL139)")


def resolve(building: dict, stage: str = "decor") -> dict:
    """In place (module docstring): every decor item in conflict is (1) raised, (2) moved along its wall or to another
    free wall, (3) left out (``decor_dropped``). Returns ``{"raised": [...], "moved": [...], "dropped": [...],
    "furniture": [the hung furniture over an opening, reported only]}``; each row ``{id, type, room_id, kind, other,
    ...}``."""
    raised, moved, dropped = [], [], []
    gone: set = set()
    roofed = _roofed(building)
    for room in building.get("rooms") or []:
        if len(room.get("polygon") or []) < 3:
            continue
        st = _room_state(building, room, roofed)
        for item, ext in list(st["items"]):
            found = conflicts(st, item, ext)
            if not found:
                continue
            c = found[0]
            why = _why(c, stage)
            dtype = item.get("type")
            row = {"id": item.get("id"), "type": dtype, "room_id": room["id"], "kind": c["kind"], "other": c["id"]}
            z0 = _raise(st, item, ext)
            if z0 is not None:
                was = {"bottom_m": item.get("bottom_m"), "center": item.get("center")}
                old = ext["z0"]
                _set_bottom(item, z0)
                ext.update(z0=z0, z1=z0 + ext["h"])
                _record(item, "raised", why + f"; raised from {old:.2f} m to {z0:.2f} m ({RAISE_GAP_M:g} m over it)",
                        was, 0.0)
                raised.append(dict(row, bottom_m=round(z0, 3)))
                continue
            tied = dtype in TIED_TYPES or (dtype == "mirror" and any(
                (st["pieces"].get(a) or {}).get("type") in BASIN_TYPES for a in item.get("anchor_ids") or []))
            lo, hi = _tied_span(item, ext, st) if tied else (-math.inf, math.inf)
            s = _free_centre(st, ext["line"], ext["w"], ext["z0"], ext["z1"], ext["s"], lo, hi, item)
            if s is not None:
                rec = _move(item, ext, st, ext["line"], s, None, why)
                ext.update(s=s, s0=s - ext["w"] / 2.0, s1=s + ext["w"] / 2.0)
                moved.append(dict(row, moved_m=rec["moved_m"], to="along its wall"))
                continue
            placed = False
            if dtype in FREE_TYPES and not tied:
                z0 = ext["z0"] if dtype in FLOOR_ITEMS else FREE_CENTRE_M - ext["h"] / 2.0
                here = _xy(st["lines"][ext["line"]], ext["s"])

                def wall_mid(i):
                    union = st["lines"][i]["union"]
                    return (min(a for a, _b in union) + max(b for _a, b in union)) / 2.0
                # the longest free wall first, then the one nearest to where the item was (no face direction: a
                # mirrored twin room picks the mirrored wall)
                order = sorted((i for i in range(len(st["lines"])) if i != ext["line"]),
                               key=lambda i: (-round(sum(b - a for a, b in st["lines"][i]["union"]), 3),
                                              round(G.distance(_xy(st["lines"][i], wall_mid(i)), here), 3), i))
                for i in order:
                    mid = wall_mid(i)
                    if z0 + ext["h"] > _ceiling_over(st, i, mid, ext["w"]) - CEILING_GAP_M:
                        continue
                    s = _free_centre(st, i, ext["w"], z0, z0 + ext["h"], mid, -math.inf, math.inf, item)
                    if s is None:
                        continue
                    rec = _move(item, ext, st, i, s, z0, why + "; moved to another free wall of the room")
                    ext.update(line=i, s=s, s0=s - ext["w"] / 2.0, s1=s + ext["w"] / 2.0, z0=z0, z1=z0 + ext["h"])
                    moved.append(dict(row, moved_m=rec["moved_m"], to="another wall"))
                    placed = True
                    break
            if placed:
                continue
            reason = why + "; not raised (ceiling or eye height) and no free stretch of " + \
                ("its piece's span" if tied else "the room's walls") + " takes it: left out"
            dropped.append(dict(row, host_id=item.get("host_id"), anchor_ids=list(item.get("anchor_ids") or []),
                                reason=reason, rule=RULE, lessons=list(LESSONS)))
            gone.add(id(item))
            st["items"] = [(d, e) for d, e in st["items"] if d is not item]
    if gone:
        building["decor"] = [d for d in building.get("decor") or [] if id(d) not in gone]
        building.setdefault("decor_dropped", []).extend(dropped)
    furniture = [c for c in clashes(building) if c["source"] == "furniture"]
    return {"raised": raised, "moved": moved, "dropped": dropped, "furniture": furniture}


def review(building: dict, check: str = "M31") -> tuple[list[dict], int]:
    """``(findings, items checked)`` of the model review's M31 and Argus' U35 (``clashes``; pure)."""
    n = 0
    roofed = _roofed(building)
    for room in building.get("rooms") or []:
        if len(room.get("polygon") or []) < 3:
            continue
        st = _room_state(building, room, roofed)
        n += len(st["items"]) + len(st["boxes"])
    return [dict(c, check=check) for c in clashes(building)], n
