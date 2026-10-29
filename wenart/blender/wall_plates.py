"""Wall plates: a light switch beside every room's door and power sockets where they are used (29 Oct 2026, lesson
UL112; user on real06 run 20261029-100801-full: "Also includes some power sockets and light on offs": the renders
showed rooms with no socket and no switch anywhere).

What (pure Python, deterministic; the building JSON's walls, openings, pieces and wall decor only, no ray casts):

- ``wall_lines(room, walls)``: the room's wall faces (its polygon edges that lie on a wall), grouped into lines with
  their covered stretches; a plate sits on a line, never on an open side.
- ``plan_level(building, level, style)``: the plates of a level's indoor rooms (``plan``: of every level):
  - a light switch (``HEIGHTS["switch"]``, a common European height) beside each door into the room (an outside door
    too, never a terrace door: glazed, sliding, a French window or wider than ``OUTSIDE_DOOR_MAX_M``; a doorless
    opening only when the room has no door), on the latch side: the side away from the hinge when the door's record
    gives one (``hinge`` / ``hinges`` points, or ``hinge_side`` seen from its ``swing_side`` room), else the side with
    more free wall; its centre ``CLEAR["switch_from_frame"]`` from the frame's outer edge; the hinge side only when the
    latch side is blocked and no drawn leaf opens over it. Rooms with two doors get one at each; a door right beside
    one of the room's switches shares it (``CLEAR["share"]``: a hall's doors within 2 m), an outside door never.
  - power sockets (``HEIGHTS["socket"]``) where they are used: one beside each bed's nightstand (each side of a double
    bed; above the nightstand when its side is blocked; over the bed end of a dresser or another low piece standing in
    for one), one at each desk (under its top, beside its legs), a pair
    (a double frame) beside the TV unit, one per free wall stretch of the living rooms and bedrooms
    (``FREE_WALL_MAX``), a row of double frames on the kitchen's splashback ``HEIGHTS["worktop_over"]`` over the
    worktop (clear of the hob and the sink, ``CLEAR["hob"]``, ``CLEAR["sink"]``), one beside the bathroom mirror (else
    the basin) at ``HEIGHTS["bathroom"]`` outside the bath and shower zone (``CLEAR["wet_zone"]``), one in each hall.
  - every spot is checked by code: on a wall face of the room, clear of its corners, never inside an opening (no plate
    on glass), never behind a piece standing against that wall whose height range reaches the plate's
    (``CLEAR["against"]``), never under a picture, mirror or curtain, never on another plate. A plate on the kitchen's
    splashback or a feature panel stands off it by the finish's depth.
  - every plate is ``inferred`` with its reason (the build's ``assumed`` rows and manifest records carry it); what found
    no place is listed in ``skipped`` with the reason.
- ``plate_mesh(kind, finish)``: a plate as vertex / face lists (pure): a square plate ``PLATE["size_m"]`` (about 82 mm,
  ``PLATE["depth_m"]`` proud of the wall, a chamfered front), a switch's tilted rocker, a socket's round well with its
  two pin holes; a double frame ``PLATE["double_w_m"]`` wide with two wells.
- ``FAMILY_FINISH``: the plates' finish by style family (one table): white satin for most families, brushed steel for
  industrial homes, matte black for modern minimal ones.
- ``review(building, plates)``: the problems model review M25 and Argus U29 report (a room with doors and no switch, a
  plate on glass or inside an opening, a plate behind a tall piece, a bed without a socket beside it, a kitchen
  without a socket over its worktop).
- ``build_wall_plates(...)`` (bpy): all plates of a level as ONE mesh object (``wall_plates_<level id>``) made from
  the vertex / face lists in one ``from_pydata`` (no operator, no modifier, no boolean per plate), kind ``wall_plate``
  (a finish on the walls, never a wall of the JSON), two material slots (the plate finish, the dark insert); its
  manifest record (detail ``wall_plates``) lists every plate.

Why: a room without switches and sockets does not look lived in; a professional render shows them where a builder
puts them. The build's furniture step already takes most of the build time (18 min on real06), so the plates cost one
object per level and a pure plan.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart import geometry as G

CHECK = "UL112"
RULE = "blender.wall_plates.plan"

# The plate (designer values of real European ranges: square plates 80-86 mm, 8-10 mm proud of the wall; a double
# frame holds two 71 mm modules; a socket's well about 38 mm across with two 4.8 mm pin holes 19 mm apart).
PLATE: dict = {"size_m": 0.082, "double_w_m": 0.153, "module_m": 0.071, "depth_m": 0.009, "back_gap_m": 0.0005,
               "chamfer_m": 0.0015, "rocker_m": 0.056, "rocker_proud_m": (0.002, 0.004), "well_r_m": 0.019,
               "well_depth_m": 0.007, "pin_r_m": 0.0024, "pin_pitch_m": 0.019, "segments": 16, "pin_segments": 8}
# Plate centres over the room's finished floor: common European heights (designer values, not a cited norm).
HEIGHTS: dict = {"switch": 1.05,          # a light switch beside the door
                 "socket": 0.30,          # a power socket over the floor
                 "worktop_over": 0.18,    # a kitchen socket's centre over the worktop (about 1.08 m over a 0.90 m one)
                 "bathroom": 1.20,        # the socket beside the bathroom mirror
                 "bedside_over_top": 0.20}  # a bedside socket over its nightstand's top (when beside it is blocked)
CLEAR: dict = {"switch_from_frame": (0.12, 0.10, 0.15),   # a switch's centre from the door frame's outer edge
               "frame_overhang": 0.023,  # the door's frame and architrave beyond the opening's edge on the wall face
               "window_trim": 0.02,      # a window's trim beyond its opening
               "corner": 0.03,           # a plate's edge from the room corner or the wall's end
               "opening": 0.03,          # ... from another opening's frame
               "piece": 0.02,            # ... from a piece standing against the wall
               "decor": 0.03,            # ... from a picture, a mirror, a curtain
               "plate": 0.03,            # ... from another plate
               "z": 0.02,                # the same above and below
               "against": 0.15,          # a piece whose footprint comes this close to the wall face stands against it
               "beside": 0.06,           # a plate's edge this far beyond the piece it serves
               "hob": 0.30, "sink": 0.30,  # a worktop socket's edge this far from a hob's and a sink's edge
               "worktop_end": 0.05,      # ... and inside the worktop's ends
               "wet_zone": 0.60,         # a bathroom socket's centre this far (plan) from a bath or a shower
               "spacing": 1.50,          # a free-wall socket this far from the room's other sockets on its wall
               "free_min": 1.00,         # a free wall stretch at least this long gets a socket ...
               "free_corner": 0.35,      # ... this far from its corner end
               "hall_min": 0.40,         # a hall's socket needs this much free wall
               # an inside door shares one of the room's switches lying this much beyond where its own would go
               # (doors side by side; a hall's doors share more); an outside door always gets its own (``outside``)
               "share": {"hall": 2.0, "stair": 2.0, "default": 0.5, "outside": 0.0},
               "pitch": 1.20,            # the kitchen row's pairs about this far apart
               "kitchen_max": 4,         # double frames over a kitchen's worktops at most
               "head_reach": 0.30}       # a bed's head, a desk's or a TV unit's back this close to a wall is on it
FACE_REACH_M = 0.06            # a room edge lies within half a wall's thickness + this of its centre line
MIN_FACE_M = 0.10              # room edges shorter than this carry no plate
PARALLEL_SIN = math.sin(math.radians(3.0))
LINE_TOL_M = 0.01              # two faces on one line
JOG_M = 0.12                   # a spot off its line's wall may sit on a parallel face of the room this far off it
OUTSIDE_DOOR_MAX_M = 1.20      # an outside door wider than this (two leaves) is a terrace door: no switch beside it
BEDSIDE_MAX_H = 1.20           # a low piece beside a bed's head (``BEDSIDE_TYPES``) serves as its nightstand ...
BEDSIDE_NARROW_M = 0.65        # ... this narrow its socket beside it, a wider one (a dresser) over its end by the bed
BED_NEAR_M = 0.60              # a bed side whose wall is blocked: the nearest free wall spot this close to its head
BED_SOCKET_REACH_M = 1.0       # a socket this close (plan) to a bed's head corner serves that side (M25, U29)
BATH_NEAR_M = 0.80             # a mirror or basin whose sides are blocked: the nearest free wall spot this close
TV_OVER_TOP_M = 0.15           # a TV unit with both sides blocked: its pair this far over its top, behind the TV
# room type -> the plate rules it follows (dining and prayer rooms the living room's; balconies and shafts none)
ROOM_KIND: dict = {"living": "living", "dining": "living", "prayer": "living", "bedroom": "bedroom",
                   "kitchen": "kitchen", "bathroom": "bathroom", "wc": "wc", "hall": "hall", "stair": "stair",
                   "storage": "storage", "other": "other", "unknown": "other"}
OUTDOOR_TYPES: tuple = ("balcony", "terrace", "veranda", "porch", "loggia", "deck", "patio", "garden")
SOCKET_USES: dict = {"living": ("tv", "desk", "wall"), "bedroom": ("bed", "desk", "tv", "wall"),
                     "kitchen": ("worktop", "desk"), "bathroom": ("mirror",), "hall": ("hall",)}
FREE_WALL_MAX: dict = {"living": 3, "bedroom": 2}
BEDS: tuple = ("bed_double", "bed_single", "bunk_bed")
DOUBLE_BEDS: tuple = ("bed_double",)
NIGHTSTANDS: tuple = ("nightstand",)
BEDSIDE_TYPES: tuple = ("nightstand", "side_table", "dresser", "chest", "desk", "console_table", "bookshelf")
DESKS: tuple = ("desk",)
TV_UNITS: tuple = ("tv_unit",)
WORKTOP_TYPES: tuple = ("kitchen_counter", "sink_kitchen", "stove", "hob", "cooktop", "dishwasher", "oven")
HOBS: tuple = ("stove", "hob", "cooktop")
SINKS: tuple = ("sink_kitchen",)
BASINS: tuple = ("washbasin", "vanity", "bathroom_vanity")
WET: tuple = ("bathtub", "shower")
MIRRORS: tuple = ("mirror",)
SOCKET_KINDS: tuple = ("socket", "socket_double")
OPT_OUT: tuple = (False, "none", "off", "no")
# The finish of the plates by style family (one table; designer values): white satin plastic for most homes, brushed
# steel for industrial ones, matte black for modern minimal ones. ``well``: the socket's well in the plate's finish
# (``plate``) or in the dark insert (``dark``).
FAMILY_FINISH: dict = {
    "default": {"plate": "painted_wood_white", "colour": "white", "well": "plate", "name": "white satin"},
    "industrial": {"plate": "steel_brushed", "colour": None, "well": "dark", "name": "brushed steel"},
    "modern minimal": {"plate": "lacquer_dark", "colour": None, "well": "dark", "name": "matte black"},
}
INSERT_MATERIAL = "lacquer_dark"   # the pin holes (and a metal or black plate's well)


# --------------------------------------------------------------------------
# small geometry
# --------------------------------------------------------------------------

def _unit(dx: float, dy: float) -> tuple[float, float]:
    n = math.hypot(dx, dy)
    return (dx / n, dy / n) if n > 1e-12 else (0.0, 0.0)


def _st(line: dict, p) -> tuple[float, float]:
    """``(s along the line, distance into the room)`` of a plan point."""
    dx, dy = float(p[0]) - line["a"][0], float(p[1]) - line["a"][1]
    return dx * line["u"][0] + dy * line["u"][1], dx * line["n"][0] + dy * line["n"][1]


def _xy(line: dict, s: float, d: float = 0.0) -> tuple[float, float]:
    (ax, ay), (ux, uy), (nx, ny) = line["a"], line["u"], line["n"]
    return ax + ux * s + nx * d, ay + uy * s + ny * d


def _corners(fp: dict) -> list[tuple[float, float]]:
    return [tuple(c) for c in G.rotated_rectangle(fp["center"], fp["size"][:2], float(fp.get("rotation_deg") or 0.0))]


def _union(spans) -> list[tuple[float, float]]:
    out: list[list[float]] = []
    for a, b in sorted((float(a), float(b)) for a, b in spans):
        if out and a <= out[-1][1] + LINE_TOL_M:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return [(a, b) for a, b in out]


def _point_rect_distance(p, fp: dict) -> float:
    """Plan distance of a point to a footprint rectangle (0 inside)."""
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    dx, dy = float(p[0]) - cx, float(p[1]) - cy
    lx, ly = dx * math.cos(rot) + dy * math.sin(rot), -dx * math.sin(rot) + dy * math.cos(rot)
    hx, hy = float(fp["size"][0]) / 2.0, float(fp["size"][1]) / 2.0
    return math.hypot(max(0.0, abs(lx) - hx), max(0.0, abs(ly) - hy))


def _front(piece: dict) -> Optional[tuple[float, float]]:
    f = piece.get("front_deg")
    if f is None:
        return None
    return math.cos(math.radians(float(f))), math.sin(math.radians(float(f)))


def _num(v) -> Optional[float]:
    return float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def piece_height(piece: dict) -> float:
    """The built height of a piece (its fitted box, ``parametric.piece_bbox``; else its own ``height``)."""
    try:
        from wenart.blender import parametric as P
        h = float(P.piece_bbox(piece)[2])
        if h > 0:
            return h
    except Exception:  # noqa: BLE001 - an unknown piece: its own height, else a 0.8 m box
        pass
    return _num(piece.get("height")) or 0.8


def piece_built(piece: dict) -> bool:
    from wenart.blender.shell import piece_built as built
    return built(piece) and bool((piece.get("footprint") or {}).get("center"))


def room_kind(room: dict) -> Optional[str]:
    """The plate rules a room follows (``ROOM_KIND``); None for an outdoor room, a balcony or a shaft."""
    rt = str(room.get("room_type") or "unknown")
    if rt in OUTDOOR_TYPES or str(room.get("room_subtype") or "") in OUTDOOR_TYPES or room.get("open_air") \
            or room.get("outdoor_space"):
        return None
    return ROOM_KIND.get(rt)


def finish_of(style: Optional[dict]) -> dict:
    """The plates' finish of a style (``FAMILY_FINISH``: its family's row, else the default)."""
    fam = str((style or {}).get("family") or "").lower()
    row = FAMILY_FINISH.get(fam) or FAMILY_FINISH["default"]
    return dict(row, family=fam or None)


# --------------------------------------------------------------------------
# where: the room's wall faces and what stands on them
# --------------------------------------------------------------------------

def wall_lines(room: dict, walls: Sequence[dict]) -> list[dict]:
    """The room's wall faces as lines (pure): ``[{"a" (origin), "u" (along), "n" (into the room), "spans": [{"s0",
    "s1", "wall_id", "offset" (the built wall face along n from the room edge), "thickness", "exterior"}], "union":
    [(s0, s1)]}]``: every polygon edge that lies on a wall (parallel within 3 degrees, within half its thickness +
    ``FACE_REACH_M``), the edges of one straight face on one line."""
    from wenart.blender import geom2d

    poly = geom2d.ccw([tuple(p[:2]) for p in room.get("polygon") or []])
    if len(poly) < 3:
        return []
    lines: list[dict] = []
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        length = G.distance(a, b)
        if length < MIN_FACE_M:
            continue
        u = _unit(b[0] - a[0], b[1] - a[1])
        n = (-u[1], u[0])                                   # the polygon is counter-clockwise: the room on the left
        spans = []
        for w in walls:
            ws, we = w["start"][:2], w["end"][:2]
            if G.distance(ws, we) < 1e-6:
                continue
            wu = _unit(float(we[0]) - float(ws[0]), float(we[1]) - float(ws[1]))
            if abs(u[0] * wu[1] - u[1] * wu[0]) > PARALLEL_SIN:
                continue
            t = float(w.get("thickness") or 0.1)
            off = (float(ws[0]) - a[0]) * n[0] + (float(ws[1]) - a[1]) * n[1] + t / 2.0
            if abs(off) > FACE_REACH_M:
                continue
            ss = sorted((float(p[0]) - a[0]) * u[0] + (float(p[1]) - a[1]) * u[1] for p in (ws, we))
            s0, s1 = max(ss[0], 0.0), min(ss[1], length)
            if s1 - s0 <= 0.02:
                continue
            spans.append({"s0": s0, "s1": s1, "wall_id": w.get("id"), "offset": round(off, 4), "thickness": t,
                          "exterior": bool(w.get("exterior"))})
        if not spans:
            continue
        line = next((ln for ln in lines if ln["u"][0] * u[0] + ln["u"][1] * u[1] > 0.9995
                     and abs(_st(ln, a)[1]) <= LINE_TOL_M), None)
        if line is None:
            line = {"a": (float(a[0]), float(a[1])), "u": u, "n": n, "spans": []}
            lines.append(line)
        base = _st(line, a)[0]
        for sp in spans:
            line["spans"].append(dict(sp, s0=round(base + sp["s0"], 4), s1=round(base + sp["s1"], 4)))
    for line in lines:
        line["spans"].sort(key=lambda sp: (sp["s0"], sp["s1"]))
        line["union"] = _union((sp["s0"], sp["s1"]) for sp in line["spans"])
        line["wall_id"] = max(line["spans"], key=lambda sp: sp["s1"] - sp["s0"])["wall_id"]
    return lines


def _span_at(line: dict, s: float) -> Optional[dict]:
    return next((sp for sp in line["spans"] if sp["s0"] - 1e-6 <= s <= sp["s1"] + 1e-6), None)


def _level_ctx(building: dict, level: dict, decor: Optional[list] = None) -> dict:
    """What every room of the level reads: its walls, openings, built pieces, wall decor, splashback bands."""
    from wenart.blender import shell

    lid = level["id"]
    walls = [w for w in building.get("walls") or [] if w.get("level_id") == lid]
    rooms = [r for r in building.get("rooms") or [] if r.get("level_id") == lid and len(r.get("polygon") or []) >= 3]
    room_level = {r["id"]: r.get("level_id") for r in building.get("rooms") or [] if r.get("id")}
    items = decor if decor is not None else building.get("decor") or []
    try:
        bands = shell.splashback_bands(building, level)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        bands = []
    return {"level": level, "walls": walls, "walls_by_id": {w["id"]: w for w in walls if w.get("id")},
            "rooms": rooms,
            "openings": [o for o in building.get("openings") or [] if o.get("level_id") == lid],
            "pieces": [f for f in building.get("furniture") or [] if f.get("level_id") == lid and piece_built(f)],
            "boxes": {},
            "decor": [d for d in items if (d.get("level_id") or room_level.get(d.get("room_id"))) == lid],
            "bands": bands}


def _openings_on(line: dict, ctx: dict, floor_z: float) -> list[dict]:
    from wenart.blender import shell

    out = []
    for o in ctx["openings"]:
        if shell.is_virtual(o) or not o.get("center") or o.get("type") not in ("door", "window", "opening"):
            continue
        w = ctx["walls_by_id"].get(o.get("wall_id"))
        if w is None or G.distance(w["start"], w["end"]) < 1e-6:
            continue
        wu = _unit(float(w["end"][0]) - float(w["start"][0]), float(w["end"][1]) - float(w["start"][1]))
        if abs(line["u"][0] * wu[1] - line["u"][1] * wu[0]) > PARALLEL_SIN:
            continue
        t = float(w.get("thickness") or 0.1)
        cx, cy, _shift = shell.opening_centre_on_wall(o, w)
        s, d = _st(line, (cx, cy))
        if not -(t + 0.10) <= d <= 0.10:
            continue
        half = float(o.get("width") or 0.0) / 2.0
        grow = CLEAR["window_trim"] if o["type"] == "window" else CLEAR["frame_overhang"]
        try:
            z0, z1, _ = shell.opening_vertical(o, ctx["level"], False)
        except (KeyError, TypeError, ValueError):
            z0, z1 = floor_z, floor_z + 2.1
        out.append({"id": o.get("id"), "type": o["type"], "s": s, "half": half, "s0": s - half - grow,
                    "s1": s + half + grow, "z0": float(z0) - floor_z, "z1": float(z1) - floor_z, "glass": _glass(o),
                    "thickness": t, "o": o})
    return out


def _glass(o: dict) -> bool:
    """A window, a glazed or sliding door, an interior glazing: glass a plate never sits on."""
    if o.get("type") == "window" or o.get("glazed") or o.get("interior_glazing") or o.get("guard"):
        return True                     # (an outside door with a guard is a French window)
    style = str(o.get("door_type") or o.get("door_style") or "")
    return style.startswith("glazed") or o.get("operation") in ("sliding", "folding")


def piece_boxes(piece: dict) -> list[tuple[dict, float, float]]:
    """``[(footprint, z0, z1)]`` of a built piece over the floor: a module-built piece (a kitchen run, a wardrobe run:
    ``asset.module_plan``) one box per module (its base units, worktop, hood, tall units at their own heights), a
    piece built into another one's run (``module_plan.built_into``: the run holds it) none, any other piece its
    footprint from its bottom (``mount_bottom_m``) to its built height."""
    asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
    mp = asset.get("module_plan") if isinstance(asset.get("module_plan"), dict) else None
    if mp and mp.get("built_into"):
        return []
    fp = piece["footprint"]
    if mp and asset.get("method") == "module" and mp.get("modules"):
        rot = float(fp.get("rotation_deg") or 0.0)
        cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        cx, cy = float(fp["center"][0]), float(fp["center"][1])
        out = []
        for m in mp["modules"]:
            size, pos = m.get("size_m") or [], m.get("pos_m") or [0.0, 0.0]
            if len(size) < 3 or len(pos) < 2:
                continue
            x, y = float(pos[0]), float(pos[1])
            z0 = _num(m.get("z_m")) or 0.0
            box = {"center": [cx + cr * x - sr * y, cy + sr * x + cr * y], "size": [float(size[0]), float(size[1])],
                   "rotation_deg": rot + float(m.get("rot_deg") or 0.0)}
            out.append((box, z0, z0 + float(size[2])))
        if out:
            return out
    bottom = _num(piece.get("mount_bottom_m")) or 0.0
    return [(fp, bottom, bottom + piece_height(piece))]


def _pieces_on(line: dict, ctx: dict) -> list[dict]:
    """The pieces standing against the line's wall (``CLEAR["against"]``; in front of it, never across it), one
    entry per box of ``piece_boxes``."""
    out = []
    lo = min((a for a, _b in line["union"]), default=0.0) - 0.5
    hi = max((b for _a, b in line["union"]), default=0.0) + 0.5
    for f in ctx["pieces"]:
        key = id(f)
        if key not in ctx["boxes"]:
            ctx["boxes"][key] = piece_boxes(f)
        for fp, z0, z1 in ctx["boxes"][key]:
            pts = [_st(line, c) for c in _corners(fp)]
            dmin = min(d for _s, d in pts)
            s0, s1 = min(s for s, _d in pts), max(s for s, _d in pts)
            if not -0.10 <= dmin <= CLEAR["against"] or s1 < lo or s0 > hi:
                continue
            out.append({"id": f.get("id"), "type": f.get("type"), "s0": s0, "s1": s1, "z0": z0, "z1": z1,
                        "d": dmin, "piece": f})
    return out


def _decor_on(line: dict, ctx: dict, room: dict) -> list[dict]:
    """The wall items of the room on the line (pictures, mirrors, clocks, curtains, blinds: anything with a wall
    point), their width and height range over the floor (``parametric.decor_size``)."""
    from wenart.blender import parametric as P

    out = []
    for item in ctx["decor"]:
        wp = item.get("wall_point")
        if not wp or (item.get("room_id") and item.get("room_id") != room.get("id")):
            continue
        s, d = _st(line, wp)
        if abs(d) > 0.12:
            continue
        try:
            w, _dd, h = P.decor_size(str(item.get("type")), item.get("size") or [0.4, 0.05])
        except (TypeError, ValueError, IndexError):
            continue
        c = item.get("center") or []
        if item.get("type") in ("curtain", "blind"):
            z0 = float(c[2]) if len(c) > 2 and c[2] is not None else 0.0
        else:
            z0 = _num(item.get("bottom_m"))
            z0 = 1.0 if z0 is None else z0
        out.append({"id": item.get("id"), "type": item.get("type"), "s0": s - w / 2.0, "s1": s + w / 2.0, "z0": z0,
                    "z1": z0 + h, "s": s, "item": item})
    return out


def _room_ctx(ctx: dict, room: dict) -> dict:
    from wenart.blender import shell

    lv = ctx["level"]
    floor_z = float(shell.room_floor_z(room, lv))
    lines = wall_lines(room, ctx["walls"])
    for line in lines:
        line["openings"] = _openings_on(line, ctx, floor_z)
        line["pieces"] = _pieces_on(line, ctx)
        line["decor"] = _decor_on(line, ctx, room)
        line["plates"] = []
    return {"room": room, "floor_z": floor_z, "lines": lines, "level": lv, "ctx": ctx, "plates": []}


def _overlap(a0, a1, b0, b1) -> bool:
    return a0 < b1 and b0 < a1


def fit(line: dict, s: float, hw: float, z: float, hh: float, ignore=()) -> Optional[str]:
    """None when a plate ``2 hw`` wide and ``2 hh`` high centred at ``s`` / ``z`` (over the floor) fits on the line,
    else what is in the way (module docstring: the wall face, the openings, the pieces against it, the wall items,
    the other plates)."""
    lo, hi, z0, z1 = s - hw, s + hw, z - hh - CLEAR["z"], z + hh + CLEAR["z"]
    if not any(a + CLEAR["corner"] <= lo + 1e-9 and hi <= b - CLEAR["corner"] + 1e-9 for a, b in line["union"]):
        return "the wall ends there (a corner or an open side)"
    for op in line["openings"]:
        if _overlap(lo, hi, op["s0"] - CLEAR["opening"], op["s1"] + CLEAR["opening"]) and \
                _overlap(z0, z1, op["z0"], op["z1"]):
            return f"the {'glass of the ' if op['glass'] else ''}{op['type']} {op['id']}"
    for pc in line["pieces"]:
        if pc["id"] in ignore:
            continue
        if _overlap(lo, hi, pc["s0"] - CLEAR["piece"], pc["s1"] + CLEAR["piece"]) and \
                _overlap(z0, z1, pc["z0"], pc["z1"]):
            return f"the {pc['type']} {pc['id']} against the wall"
    for dc in line["decor"]:
        if _overlap(lo, hi, dc["s0"] - CLEAR["decor"], dc["s1"] + CLEAR["decor"]) and \
                _overlap(z0, z1, dc["z0"], dc["z1"]):
            return f"the {dc['type']} {dc['id']}"
    for pl in line["plates"]:
        if _overlap(lo, hi, pl["s0"] - CLEAR["plate"], pl["s1"] + CLEAR["plate"]) and \
                _overlap(z0, z1, pl["z0"], pl["z1"]):
            return f"the {pl['kind']} {pl['id']}"
    return None


def _blockers(line: dict, z: float, hh: float, ignore=()) -> list[tuple[float, float]]:
    z0, z1 = z - hh - CLEAR["z"], z + hh + CLEAR["z"]
    out = []
    for key, clear in (("openings", CLEAR["opening"]), ("pieces", CLEAR["piece"]), ("decor", CLEAR["decor"]),
                       ("plates", CLEAR["plate"])):
        for x in line[key]:
            if x.get("id") in ignore and key == "pieces":
                continue
            if _overlap(z0, z1, x["z0"], x["z1"]):
                out.append((x["s0"] - clear, x["s1"] + clear))
    return out


def free_spans(line: dict, z: float, hh: float, ignore=()) -> list[tuple[float, float, bool, bool]]:
    """``[(s0, s1, starts at a corner, ends at a corner)]``: the stretches of the line's wall at a plate's height
    range that nothing blocks (corners kept clear)."""
    out = []
    blocks = sorted(_blockers(line, z, hh, ignore))
    for a, b in line["union"]:
        lo, hi = a + CLEAR["corner"], b - CLEAR["corner"]
        cur, cur_corner = lo, True
        for x0, x1 in blocks:
            if x1 <= cur or x0 >= hi:
                continue
            if x0 > cur:
                out.append((cur, x0, cur_corner, False))
            cur, cur_corner = max(cur, x1), False
        if cur < hi:
            out.append((cur, hi, cur_corner, True))
    return [x for x in out if x[1] - x[0] > 1e-6]


def free_run(line: dict, s: float, sign: int, z: float, hh: float) -> float:
    """How far the wall runs free from station ``s`` in direction ``sign`` at a plate's height (0 when ``s`` is not on
    a free stretch)."""
    for a, b, _c0, _c1 in free_spans(line, z, hh):
        if a - 1e-6 <= s <= b + 1e-6:
            return (b - s) if sign > 0 else (s - a)
    return 0.0


def _standoff(rctx: dict, line: dict, s: float, z_world: float) -> float:
    """How far a plate at station ``s`` stands off the wall face: the kitchen splashback's tiles or a feature panel
    under it (``shell.SPLASHBACK``; ``feature_walls.finish_depth_at``)."""
    from wenart.blender import feature_walls as FW
    from wenart.blender import shell

    sp = _span_at(line, s)
    off = float(sp["offset"]) if sp else 0.0
    p = _xy(line, s, off)
    depth = 0.0
    for band in rctx["ctx"]["bands"]:
        if band.get("room_id") != rctx["room"]["id"]:
            continue
        (px, py), (qx, qy), (nx, ny) = band["p"], band["q"], band["normal"]
        length = math.hypot(qx - px, qy - py)
        if length < 1e-9 or abs((p[0] - px) * nx + (p[1] - py) * ny) > 0.03:
            continue
        t = ((p[0] - px) * (qx - px) + (p[1] - py) * (qy - py)) / length
        if any(t0 <= t <= t1 and z0 <= z_world <= z1 for t0, t1, z0, z1 in band.get("pieces") or []):
            depth = max(depth, shell.SPLASHBACK["gap"] + shell.SPLASHBACK["thickness"])
    try:
        depth = max(depth, float(FW.finish_depth_at(rctx["room"], p, z_world)))
    except (KeyError, TypeError, ValueError):
        pass
    return depth


def _add(rctx: dict, line: dict, kind: str, use: str, s: float, z: float, reason: str, target=None, **extra) -> dict:
    """Record a plate on the line (its world centre on the wall face, standing off a finish under it)."""
    hw = (PLATE["double_w_m"] if kind == "socket_double" else PLATE["size_m"]) / 2.0
    hh = PLATE["size_m"] / 2.0
    room = rctx["room"]
    sp = _span_at(line, s)
    off = float(sp["offset"]) if sp else 0.0
    z_world = rctx["floor_z"] + z
    stand = _standoff(rctx, line, s, z_world)
    x, y = _xy(line, s, off + stand)
    pid = f"plate_{room['id']}_{len(rctx['plates']) + 1:02d}"
    rec = {"id": pid, "kind": kind, "use": use, "for": target, "room_id": room["id"], "level_id": rctx["level"]["id"],
           "wall_id": (sp or {}).get("wall_id") or line.get("wall_id"),
           "center": [round(x, 4), round(y, 4), round(z_world, 4)], "u": [round(line["u"][0], 6),
                                                                          round(line["u"][1], 6)],
           "n": [round(line["n"][0], 6), round(line["n"][1], 6)], "z_m": round(z, 3),
           "width_m": round(2 * hw, 3), "height_m": round(2 * hh, 3), "depth_m": PLATE["depth_m"],
           "standoff_m": round(stand, 4), "source": "inferred", "inferred": True, "rule": RULE, "reason": reason}
    rec.update({k: v for k, v in extra.items() if v is not None})
    rctx["plates"].append(rec)
    line["plates"].append({"id": pid, "kind": kind, "s0": s - hw, "s1": s + hw, "z0": z - hh, "z1": z + hh, "s": s})
    return rec


def _try(rctx: dict, line: dict, kind: str, spots, z: float, ignore=()) -> tuple[Optional[tuple], Optional[str]]:
    """``((line, s), None)`` of the first of the stations ``spots`` (on ``line``) where the plate fits: on the line,
    else on a parallel face of the room within ``JOG_M`` of it (the jog of a thicker wall beside a door); else
    ``(None, what blocked the first)``."""
    hw = (PLATE["double_w_m"] if kind == "socket_double" else PLATE["size_m"]) / 2.0
    first = None
    jogs = _jogs(rctx, line)
    for s in spots:
        why = fit(line, s, hw, z, PLATE["size_m"] / 2.0, ignore)
        if why is None:
            return (line, s), None
        first = first or why
        p = _xy(line, s)
        for ln in jogs:
            s2 = _st(ln, p)[0]
            if fit(ln, s2, hw, z, PLATE["size_m"] / 2.0, ignore) is None:
                return (ln, s2), None
    return None, first


def near_spots(rctx: dict, p, kind: str, z: float, reach: float, ignore=()) -> list[tuple[float, dict, float]]:
    """``[(plan distance, line, s)]`` of the room's wall spots nearest the point ``p`` (one per line, within
    ``reach``) where the plate fits, nearest first."""
    hw = (PLATE["double_w_m"] if kind == "socket_double" else PLATE["size_m"]) / 2.0
    out = []
    for line in rctx["lines"]:
        s0 = _st(line, p)[0]
        best = None
        for a, b, _c0, _c1 in free_spans(line, z, PLATE["size_m"] / 2.0, ignore):
            if b - a < 2 * hw:
                continue
            s = min(max(s0, a + hw), b - hw)
            dist = G.distance(p, _xy(line, s))
            if dist <= reach and (best is None or dist < best[0]) and \
                    fit(line, s, hw, z, PLATE["size_m"] / 2.0, ignore) is None:
                best = (dist, line, s)
        if best:
            out.append(best)
    return sorted(out, key=lambda x: x[0])


def _line_of(rctx: dict, p, normal=None, reach: float = CLEAR["head_reach"]) -> Optional[dict]:
    """The room line a point lies on (within ``reach`` into the room), facing ``normal`` when given."""
    best = None
    for line in rctx["lines"]:
        if normal is not None and line["n"][0] * normal[0] + line["n"][1] * normal[1] < 0.95:
            continue
        s, d = _st(line, p)
        if not -0.05 <= d <= reach or not any(a - 0.05 <= s <= b + 0.05 for a, b in line["union"]):
            continue
        if best is None or d < best[0]:
            best = (d, line)
    return best[1] if best else None


def _piece_span(line: dict, piece: dict) -> tuple[float, float]:
    ss = [_st(line, c)[0] for c in _corners(piece["footprint"])]
    return min(ss), max(ss)


def _back_line(rctx: dict, piece: dict) -> Optional[dict]:
    """The wall line a piece's back stands on (its front faces into the room), None for a free-standing piece."""
    f = _front(piece)
    corners = _corners(piece["footprint"])
    if f is None:
        return None
    back = min(corners, key=lambda c: c[0] * f[0] + c[1] * f[1])
    back_d = back[0] * f[0] + back[1] * f[1]
    pts = [c for c in corners if c[0] * f[0] + c[1] * f[1] <= back_d + 0.02] or [back]
    mid = (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))
    return _line_of(rctx, mid, normal=f)


# --------------------------------------------------------------------------
# the doors of a room and their switches
# --------------------------------------------------------------------------

def _hinge_world(o: dict, rooms: list, walls_by_id: dict) -> tuple[Optional[tuple], Optional[str]]:
    """The hinge jamb of a door from its record (a ``hinge`` / ``hinge_point`` / ``hinges`` point, else ``hinge_side``
    left / right seen from its ``swing_side`` room facing the door), None when the record gives none."""
    for key in ("hinge", "hinge_point", "hinges"):
        v = o.get(key)
        if isinstance(v, (list, tuple)) and v and isinstance(v[0], (list, tuple)):
            v = v[0]
        if isinstance(v, (list, tuple)) and len(v) >= 2 and all(_num(x) is not None for x in v[:2]):
            return (float(v[0]), float(v[1])), f"the drawn hinge ({key})"
    side = str(o.get("hinge_side") or "").strip().lower()
    swing = o.get("swing_side")
    w = walls_by_id.get(o.get("wall_id"))
    room = next((r for r in rooms if r.get("id") == swing), None)
    if side not in ("left", "right") or room is None or w is None or not o.get("center"):
        return None, None
    for line in wall_lines(room, [w]):
        s, d = _st(line, o["center"])
        if -(float(w.get("thickness") or 0.1) + 0.1) <= d <= 0.1:
            half = float(o.get("width") or 0.0) / 2.0
            # standing in the room facing the wall, +u is on the left (the room lies left of u)
            return _xy(line, s + (half if side == "left" else -half), d), \
                f"the drawn hinge side ({side}, seen from {swing})"
    return None, None


def room_doors(rctx: dict) -> list[dict]:
    """The room's doors and doorless openings on its wall faces: ``[{"id", "line", "s", "half", "other" (the room on
    the other side or None), "outside", "counted" (it gets a switch), "why", "op"}]``. Counted: a door into another
    indoor room; an outside door that is no terrace door (not glazed, sliding, a French window or wider than
    ``OUTSIDE_DOOR_MAX_M``); the room's only way in when nothing else is counted."""
    room, ctx = rctx["room"], rctx["ctx"]
    out = []
    for line in rctx["lines"]:
        for op in line["openings"]:
            if op["type"] not in ("door", "opening"):
                continue
            if not any(a - op["half"] <= op["s"] <= b + op["half"] for a, b in line["union"]):
                continue
            probe = _xy(line, op["s"], 0.20)
            if not G.point_in_polygon(probe, room["polygon"]):
                continue
            back = _xy(line, op["s"], -(op["thickness"] + 0.20))
            other = next((r for r in ctx["rooms"] if r["id"] != room["id"] and
                          G.point_in_polygon(back, r["polygon"])), None)
            outside = other is None or room_kind(other) is None
            out.append({"id": op["id"], "line": line, "s": op["s"], "half": op["half"],
                        "other": other["id"] if other else None, "outside": outside, "op": op, "type": op["type"]})
    seen, uniq = set(), []
    for d in sorted(out, key=lambda d: (d["type"] != "door", not d["outside"], str(d["id"]))):
        if d["id"] in seen:
            continue
        seen.add(d["id"])
        uniq.append(d)
    for d in uniq:
        o = d["op"]["o"]
        if d["type"] == "door" and not d["outside"]:
            d["counted"], d["why"] = True, f"the door {d['id']} into {room['id']}"
        elif d["type"] == "door" and not d["op"]["glass"] and 2.0 * d["half"] <= OUTSIDE_DOOR_MAX_M:
            d["counted"], d["why"] = True, f"the outside door {d['id']} ({o.get('door_type') or 'solid'})"
        elif d["type"] == "door":
            what = "French window" if o.get("guard") else "glazed, sliding or wide outside door"
            d["counted"], d["why"] = False, (f"the {what} {d['id']}: a terrace door, the room's other doors carry its "
                                             "switch")
        else:
            d["counted"], d["why"] = False, f"the doorless opening {d['id']}"
    if not any(d["counted"] for d in uniq):
        for d in uniq:                       # the room's only ways in: a terrace door, a doorless opening
            if d["type"] == "door" or (d["type"] == "opening" and not d["outside"]):
                d["counted"], d["why"] = True, f"{d['why'].split(':')[0]}, the room's only way in"
    return uniq


def _jogs(rctx: dict, line: dict) -> list[dict]:
    return [ln for ln in rctx["lines"] if ln is not line and ln["u"][0] * line["u"][0] + ln["u"][1] * line["u"][1]
            > 0.9995 and abs(_st(ln, line["a"])[1]) <= JOG_M]


def _side_run(rctx: dict, line: dict, s_edge: float, sign: int, z: float, hh: float) -> float:
    """The free wall beside a door's frame edge ``s_edge`` in direction ``sign`` (on its line, else on a parallel face
    a jog off it)."""
    start = s_edge + sign * (CLEAR["opening"] + 0.01)
    run = free_run(line, start, sign, z, hh)
    if run > 0.0:
        return run
    p = _xy(line, start)
    return max([free_run(ln, _st(ln, p)[0], sign, z, hh) for ln in _jogs(rctx, line)] + [0.0])


def _plan_switches(rctx: dict, kind: str, skipped: list) -> None:
    room, ctx = rctx["room"], rctx["ctx"]
    share = CLEAR["share"].get(kind, CLEAR["share"]["default"])
    hw = hh = PLATE["size_m"] / 2.0
    z = HEIGHTS["switch"]
    for door in room_doors(rctx):
        if not door["counted"]:
            continue
        line, s_c, half = door["line"], door["s"], door["half"]
        edge = half + CLEAR["frame_overhang"]
        c = _xy(line, s_c)
        reach = edge + max(CLEAR["switch_from_frame"]) + hw + (CLEAR["share"]["outside"] if door["outside"] else share)
        near = [p for p in rctx["plates"] if p["kind"] == "switch" and G.distance(p["center"][:2], c) <= reach]
        if near:                                  # a door beside one of the room's switches shares it
            near[0].setdefault("serves", [near[0]["for"]]).append(door["id"])
            continue
        hinge, hinge_why = _hinge_world(door["op"]["o"], ctx["rooms"], ctx["walls_by_id"])
        swing_in = door["op"]["o"].get("swing_side") == room["id"]
        if hinge is not None:
            latch = 1 if _st(line, hinge)[0] < s_c else -1
            latch_why = f"on the latch side, away from {hinge_why}"
        else:
            run_p = _side_run(rctx, line, s_c + edge, 1, z, hh)
            run_m = _side_run(rctx, line, s_c - edge, -1, z, hh)
            latch = 1 if run_p >= run_m else -1
            latch_why = (f"on the latch side, assumed on the side with more free wall ({max(run_p, run_m):.2f} m "
                         f"against {min(run_p, run_m):.2f} m; the documents give no hinge side)")
        # the hinge side only when the leaf does not open over it into this room (a drawn hinge and swing)
        sides = [latch] + ([-latch] if hinge is None or not swing_in else [])
        first = None
        for sign in sides:
            spots = [s_c + sign * (edge + off) for off in CLEAR["switch_from_frame"]]
            got, why = _try(rctx, line, "switch", spots, z)
            if got is None:
                first = first or why
                continue
            ln, s = got
            gap = abs(_st(line, _xy(ln, s))[0] - s_c) - edge
            side_why = latch_why if sign == latch else f"on the hinge side: the latch side is blocked by {first}"
            _add(rctx, ln, "switch", "door", s, z,
                 f"inferred: a light switch beside {door['why']}, {side_why}, its centre {gap:.2f} m from the frame, "
                 f"{z:.2f} m over the floor (a common European height)", target=door["id"],
                 side="latch" if sign == latch else "hinge")
            break
        else:
            skipped.append({"room_id": room["id"], "use": "door", "for": door["id"],
                            "reason": f"no switch beside {door['why']}: {first}"})


# --------------------------------------------------------------------------
# the sockets where they are used
# --------------------------------------------------------------------------

def _room_pieces(rctx: dict, types) -> list[dict]:
    return sorted((f for f in rctx["ctx"]["pieces"] if f.get("room_id") == rctx["room"]["id"]
                   and f.get("type") in types), key=lambda f: str(f.get("id")))


def _beside(span: tuple[float, float], sign: int, hw: float) -> float:
    return (span[1] + CLEAR["beside"] + hw) if sign > 0 else (span[0] - CLEAR["beside"] - hw)


def _top(piece: dict) -> float:
    boxes = piece_boxes(piece)
    return max(z1 for _fp, _z0, z1 in boxes) if boxes else piece_height(piece)


def _bedside(rctx: dict, line: dict, bed: dict, edge: float, sign: int) -> Optional[tuple[dict, tuple]]:
    """The low piece beside a bed's head on one side (a nightstand first, else a side table, a dresser, a desk ...
    standing in for it): its back on the head wall, its near edge within 0.40 m of the bed's side."""
    best = None
    for n in _room_pieces(rctx, BEDSIDE_TYPES):
        if n.get("id") == bed.get("id") or _top(n) > BEDSIDE_MAX_H or \
                min(_st(line, c)[1] for c in _corners(n["footprint"])) > CLEAR["head_reach"]:
            continue
        sp = _piece_span(line, n)
        gap = (sp[0] - edge) if sign > 0 else (edge - sp[1])
        if not -0.10 <= gap <= 0.40:
            continue
        key = (n.get("type") not in NIGHTSTANDS, abs(gap), str(n.get("id")))
        if best is None or key < best[0]:
            best = (key, n, sp)
    return (best[1], best[2]) if best else None


def _bed_sockets(rctx: dict, skipped: list) -> None:
    hw = hh = PLATE["size_m"] / 2.0
    z = HEIGHTS["socket"]
    for bed in _room_pieces(rctx, BEDS):
        line = _back_line(rctx, bed)
        if line is None:
            skipped.append({"room_id": rctx["room"]["id"], "use": "bed", "for": bed["id"],
                            "reason": f"the {bed['type']} {bed['id']} stands free (no head wall within "
                                      f"{CLEAR['head_reach']} m): a floor box, not built"})
            continue
        b0, b1 = _piece_span(line, bed)
        sides = [(sg, _bedside(rctx, line, bed, b1 if sg > 0 else b0, sg)) for sg in (-1, 1)]
        if bed["type"] not in DOUBLE_BEDS:        # one socket: on its nightstand's side, else its freer side
            with_stand = [x for x in sides if x[1] is not None]
            sides = with_stand[:1] or sorted(
                sides, key=lambda x: -free_run(line, _beside((b0, b1), x[0], hw), x[0], z, hh))[:1]
        for sign, stand in sides:
            where = "right" if sign > 0 else "left"           # seen lying in the bed (the line runs to its right)
            if stand is not None:
                n, sp = stand
                what = "nightstand" if n.get("type") in NIGHTSTANDS else str(n.get("type")).replace("_", " ")
                near_end = (sp[0] + 0.10 + hw) if sign > 0 else (sp[1] - 0.10 - hw)
                beside = ([_beside(sp, sign, hw)], z, f"beside its {what} {n['id']}", ())
                over = ([(sp[0] + sp[1]) / 2.0, near_end] if sp[1] - sp[0] <= BEDSIDE_NARROW_M else [near_end],
                        _top(n) + HEIGHTS["bedside_over_top"], f"over its {what} {n['id']} at the bed's side",
                        (n["id"],))
                # a nightstand: beside it, else over it; a wider piece standing in for one: over its end by the bed
                tries = [beside, over] if sp[1] - sp[0] <= BEDSIDE_NARROW_M else [over, beside]
            else:
                s = _beside((b0, b1), sign, hw)
                tries = [([s, s + sign * 0.15], z, "beside its head (no nightstand on that side)", ())]
            first = None
            for spots, zz, what, ign in tries:
                got, why = _try(rctx, line, "socket", spots, zz, ign)
                if got is None:
                    first = first or why
                    continue
                _add(rctx, got[0], "socket", "bed", got[1], zz,
                     f"inferred: a power socket for the {bed['type']} {bed['id']} ({where} side) {what}, "
                     f"{zz:.2f} m over the floor", target=bed["id"], side=where, over=ign[0] if ign else None)
                break
            else:
                corner = _xy(line, b1 if sign > 0 else b0)
                cand = near_spots(rctx, corner, "socket", z, BED_NEAR_M)
                if cand:
                    _dist, ln, s = cand[0]
                    _add(rctx, ln, "socket", "bed", s, z,
                         f"inferred: a power socket for the {bed['type']} {bed['id']} ({where} side) on the wall "
                         f"nearest its head, as beside it {first}, {z:.2f} m over the floor", target=bed["id"],
                         side=where)
                    continue
                skipped.append({"room_id": rctx["room"]["id"], "use": "bed", "for": bed["id"],
                                "reason": f"no socket on the {where} side of {bed['id']}: {first}"})


def _desk_sockets(rctx: dict, skipped: list) -> None:
    hw = PLATE["size_m"] / 2.0
    z = HEIGHTS["socket"]
    for desk in _room_pieces(rctx, DESKS):
        line = _back_line(rctx, desk)
        if line is None:
            skipped.append({"room_id": rctx["room"]["id"], "use": "desk", "for": desk["id"],
                            "reason": f"the desk {desk['id']} stands free: a floor box, not built"})
            continue
        d0, d1 = _piece_span(line, desk)
        inset = 0.10 + hw
        ends = sorted((1, -1), key=lambda sg: -free_run(line, _beside((d0, d1), sg, hw), sg, z, hw))
        got, why = _try(rctx, line, "socket", [(d1 - inset) if sg > 0 else (d0 + inset) for sg in ends], z,
                        (desk["id"],))
        what = "under its top, beside its legs"
        if got is None:
            got, _why = _try(rctx, line, "socket", [_beside((d0, d1), sg, hw) for sg in ends], z)
            what = "beside it (under its top is blocked)"
        if got is None:
            skipped.append({"room_id": rctx["room"]["id"], "use": "desk", "for": desk["id"],
                            "reason": f"no socket at the desk {desk['id']}: {why}"})
            continue
        _add(rctx, got[0], "socket", "desk", got[1], z, f"inferred: a power socket at the desk {desk['id']} {what}, "
                                                        f"{z:.2f} m over the floor", target=desk["id"])


def _tv_sockets(rctx: dict, skipped: list) -> None:
    hw = PLATE["double_w_m"] / 2.0
    z = HEIGHTS["socket"]
    for unit in _room_pieces(rctx, TV_UNITS):
        line = _back_line(rctx, unit)
        if line is None:
            skipped.append({"room_id": rctx["room"]["id"], "use": "tv", "for": unit["id"],
                            "reason": f"the TV unit {unit['id']} stands free (no wall behind it): a floor box, not "
                                      "built"})
            continue
        u0, u1 = _piece_span(line, unit)
        order = sorted((1, -1), key=lambda sg: -free_run(line, _beside((u0, u1), sg, hw), sg, z, PLATE["size_m"] / 2))
        got, why = _try(rctx, line, "socket_double", [_beside((u0, u1), sg, hw) for sg in order], z)
        zz, what, over = z, "beside it", None
        if got is None:
            zz, over = _top(unit) + TV_OVER_TOP_M, unit["id"]
            what = "behind the TV over the unit (beside it is blocked)"
            got, _w = _try(rctx, line, "socket_double", [(u0 + u1) / 2.0 + sg * (u1 - u0) / 4.0 for sg in order],
                           zz, (unit["id"],))
        if got is None:
            skipped.append({"room_id": rctx["room"]["id"], "use": "tv", "for": unit["id"],
                            "reason": f"no socket pair at the TV unit {unit['id']}: {why}"})
            continue
        _add(rctx, got[0], "socket_double", "tv", got[1], zz,
             f"inferred: a socket pair (a double frame) for the TV unit {unit['id']} {what}, {zz:.2f} m over the "
             "floor", target=unit["id"], over=over)


def _local_span(line: dict, piece: dict, x_m: float, w_m: float) -> tuple[float, float]:
    """The stations on ``line`` of a stretch ``x_m +- w_m / 2`` along a piece's own x axis (a module run's built-in)."""
    fp = piece["footprint"]
    rot = math.radians(float(fp.get("rotation_deg") or 0.0))
    cx, cy = float(fp["center"][0]), float(fp["center"][1])
    ss = sorted(_st(line, (cx + math.cos(rot) * x, cy + math.sin(rot) * x))[0]
                for x in (float(x_m) - float(w_m) / 2.0, float(x_m) + float(w_m) / 2.0))
    return ss[0], ss[1]


def worktop_runs(rctx: dict) -> list[dict]:
    """The kitchen's worktops against its walls (``shell.kitchen_counter_back``): ``[{"line", "s0", "s1", "top",
    "members": [(id, type, s0, s1)], "holes": [(sink | hob, s0, s1, id)]}]``, the pieces of one run on one line
    merged; the holes are the sinks and hobs in it (a module run's built-ins, ``module_plan.built_ins``, and the
    sinks and hobs standing in front of it)."""
    from wenart.blender import shell

    room = rctx["room"]
    runs: list[dict] = []
    for f in _room_pieces(rctx, WORKTOP_TYPES):
        if not piece_boxes(f):                    # built into another piece's run: that run holds it
            continue
        try:
            back = shell.kitchen_counter_back(f, room)
        except (KeyError, TypeError, ValueError, ZeroDivisionError):
            back = None
        if back is None:
            continue
        p, q, _d = back
        dirn = _unit(q[0] - p[0], q[1] - p[1])
        line = next((ln for ln in rctx["lines"] if abs(ln["u"][0] * dirn[1] - ln["u"][1] * dirn[0]) <= PARALLEL_SIN
                     and abs(_st(ln, p)[1]) <= 0.03 and abs(_st(ln, q)[1]) <= 0.03), None)
        if line is None:
            continue
        mp = (f.get("asset") or {}).get("module_plan") if isinstance((f.get("asset") or {}).get("module_plan"),
                                                                     dict) else {}
        top = _num(mp.get("worktop_m")) or _num(f.get("height")) or 0.90
        top = 0.90 if top > 1.2 else top
        s0, s1 = sorted((_st(line, p)[0], _st(line, q)[0]))
        run = next((r for r in runs if r["line"] is line and s0 <= r["s1"] + 0.05 and s1 >= r["s0"] - 0.05), None)
        if run is None:
            run = {"line": line, "s0": s0, "s1": s1, "top": top, "members": [], "holes": []}
            runs.append(run)
        run["s0"], run["s1"] = min(run["s0"], s0), max(run["s1"], s1)
        if f.get("type") == "kitchen_counter":
            run["top"] = top
        run["members"].append((f["id"], f["type"], s0, s1))
        if f.get("type") in HOBS + SINKS:
            run["holes"].append(("hob" if f["type"] in HOBS else "sink", s0, s1, f["id"]))
        for bi in mp.get("built_ins") or []:
            if isinstance(bi, dict) and bi.get("kind") in ("sink", "hob") and _num(bi.get("x_m")) is not None \
                    and _num(bi.get("w_m")):
                a, b = _local_span(line, f, bi["x_m"], bi["w_m"])
                run["holes"].append((bi["kind"], a, b, bi.get("id")))
    for f in _room_pieces(rctx, HOBS + SINKS):     # a sink or hob standing in front of a run, a little off it
        if not piece_boxes(f):
            continue
        for run in runs:
            if any(m[0] == f["id"] for m in run["members"]):
                continue
            pts = [_st(run["line"], c) for c in _corners(f["footprint"])]
            a, b = min(s for s, _d in pts), max(s for s, _d in pts)
            if min(d for _s, d in pts) <= 1.0 and _overlap(a, b, run["s0"], run["s1"]):
                run["holes"].append(("hob" if f["type"] in HOBS else "sink", a, b, f["id"]))
    return runs


def _kitchen_sockets(rctx: dict, skipped: list) -> None:
    hw2, hw1 = PLATE["double_w_m"] / 2.0, PLATE["size_m"] / 2.0
    budget = CLEAR["kitchen_max"]
    runs = sorted(worktop_runs(rctx), key=lambda r: -(r["s1"] - r["s0"]))
    if not runs and _room_pieces(rctx, WORKTOP_TYPES):
        skipped.append({"room_id": rctx["room"]["id"], "use": "worktop", "for": None,
                        "reason": "no worktop stands against a wall (an island only): no row over it"})
    for run in runs:
        line, z = run["line"], run["top"] + HEIGHTS["worktop_over"]
        holes = [(a - CLEAR["hob" if k == "hob" else "sink"], b + CLEAR["hob" if k == "hob" else "sink"])
                 for k, a, b, _i in run["holes"]]
        free = [(run["s0"] + CLEAR["worktop_end"], run["s1"] - CLEAR["worktop_end"])]
        for h0, h1 in sorted(holes):
            nxt = []
            for a, b in free:
                if h1 <= a or h0 >= b:
                    nxt.append((a, b))
                    continue
                if h0 > a:
                    nxt.append((a, h0))
                if h1 < b:
                    nxt.append((h1, b))
            free = nxt
        # the stretches of the worktop's wall the windows, tall units and wall items leave (at the row's height)
        spans = []
        for a, b in free:
            for x0, x1, _c0, _c1 in free_spans(line, z, hw1):
                lo, hi = max(a, x0), min(b, x1)
                if hi - lo >= 2 * hw1:
                    spans.append((lo, hi))
        placed = 0
        for a, b in sorted(spans, key=lambda x: (-(x[1] - x[0]), x[0])):
            if budget <= 0:
                break
            length = b - a
            kind = "socket_double" if length >= 2 * hw2 else "socket"
            hw = hw2 if kind == "socket_double" else hw1
            count = max(1, min(budget, int((length - 2 * hw) // CLEAR["pitch"]) + 1))
            for k in range(count):
                s_mid = a + hw + (length - 2 * hw) * (k + 0.5) / count
                got, _why = _try(rctx, line, kind, [s_mid], z)
                if got is None or got[0] is not line:
                    continue
                _add(rctx, line, kind, "worktop", got[1], z,
                     f"inferred: {'a socket pair' if kind == 'socket_double' else 'a socket'} over the worktop "
                     f"{run['members'][0][0]} on the splashback, {HEIGHTS['worktop_over']:.2f} m over its top "
                     f"({z:.2f} m over the floor), clear of the hob and the sink", target=run["members"][0][0])
                placed += 1
                budget -= 1
                if budget <= 0:
                    break
        if not placed and budget > 0:
            skipped.append({"room_id": rctx["room"]["id"], "use": "worktop", "for": run["members"][0][0],
                            "reason": "no free stretch of the worktop's wall clear of the hob, the sink, the "
                                      "windows and the tall units"})


def _bath_sockets(rctx: dict, skipped: list) -> None:
    hw = PLATE["size_m"] / 2.0
    z = HEIGHTS["bathroom"]
    wet = _room_pieces(rctx, WET)
    room = rctx["room"]
    hosts = []
    for line in rctx["lines"]:
        for dc in line["decor"]:
            if dc["type"] in MIRRORS:
                hosts.append((line, (dc["s0"], dc["s1"]), f"the mirror {dc['id']}", dc["id"]))
    for basin in [] if hosts else _room_pieces(rctx, BASINS):
        line = _back_line(rctx, basin)
        if line is not None:
            hosts.append((line, _piece_span(line, basin), f"the basin {basin['id']} (no mirror hangs over it)",
                          basin["id"]))
    if not hosts:
        if _room_pieces(rctx, BASINS):
            skipped.append({"room_id": room["id"], "use": "mirror", "for": None,
                            "reason": "no mirror and no basin against a wall"})
        return
    line, span, what, target = hosts[0]

    def dry(p) -> float:
        return min([_point_rect_distance(p, f["footprint"]) for f in wet] + [9.0])

    first = None
    for sign in sorted((1, -1), key=lambda sg: -dry(_xy(line, _beside(span, sg, hw)))):
        s = _beside(span, sign, hw)
        got, why = _try(rctx, line, "socket", [s, s + sign * 0.10], z)
        if got is not None and dry(_xy(*got)) < CLEAR["wet_zone"]:
            got, why = None, f"the bath and shower zone ({dry(_xy(*got)):.2f} m from it)"
        if got is None:
            first = first or why
            continue
        _add(rctx, got[0], "socket", "mirror", got[1], z,
             f"inferred: a power socket beside {what}, {z:.2f} m over the floor, outside the bath and shower zone",
             target=target)
        return
    cand = [c for s_edge in span for c in near_spots(rctx, _xy(line, s_edge), "socket", z, BATH_NEAR_M)
            if dry(_xy(c[1], c[2])) >= CLEAR["wet_zone"]]
    if cand:
        _dist, ln, s = min(cand, key=lambda c: c[0])
        _add(rctx, ln, "socket", "mirror", s, z,
             f"inferred: a power socket on the wall nearest {what}, as beside it {first}, {z:.2f} m over the "
             "floor, outside the bath and shower zone", target=target)
        return
    skipped.append({"room_id": room["id"], "use": "mirror", "for": target,
                    "reason": f"no socket beside the mirror or the basin: {first}"})


def _spot_in(a: float, b: float, c0: bool, c1: bool, hw: float) -> float:
    if b - a > 2.0 * CLEAR["free_corner"] + 2 * hw:
        if c0:
            return a + CLEAR["free_corner"]
        if c1:
            return b - CLEAR["free_corner"]
    return (a + b) / 2.0


def _wall_sockets(rctx: dict, kind: str, skipped: list) -> None:
    hw = PLATE["size_m"] / 2.0
    z = HEIGHTS["socket"]
    cap = FREE_WALL_MAX.get(kind, 0)
    cands = []
    for i, line in enumerate(rctx["lines"]):
        taken = [_xy(ln, p["s"]) for ln in rctx["lines"] for p in ln["plates"] if p["kind"] in SOCKET_KINDS]
        for a, b, c0, c1 in free_spans(line, z, hw):
            if b - a < CLEAR["free_min"]:
                continue
            s = _spot_in(a, b, c0, c1, hw)
            if any(G.distance(_xy(line, s), t) < CLEAR["spacing"] for t in taken):
                continue
            cands.append((-(b - a), i, s, line, b - a))
    used = set()
    for _neg, i, s, line, length in sorted(cands, key=lambda c: (c[0], c[1])):
        if cap <= 0:
            break
        taken = [_xy(ln, p["s"]) for ln in rctx["lines"] for p in ln["plates"] if p["kind"] in SOCKET_KINDS]
        if i in used or any(G.distance(_xy(line, s), t) < CLEAR["spacing"] for t in taken):
            continue
        got, _why = _try(rctx, line, "socket", [s], z)
        if got is None:
            continue
        used.add(i)
        cap -= 1
        _add(rctx, got[0], "socket", "wall", got[1], z, f"inferred: a power socket on a free wall stretch of "
                                                        f"{length:.2f} m, {z:.2f} m over the floor",
             target=line.get("wall_id"))


def _hall_socket(rctx: dict, skipped: list) -> None:
    hw = PLATE["size_m"] / 2.0
    z = HEIGHTS["socket"]
    best = None
    for line in rctx["lines"]:
        for a, b, c0, c1 in free_spans(line, z, hw):
            if b - a >= CLEAR["hall_min"] and (best is None or b - a > best[0]):
                best = (b - a, line, _spot_in(a, b, c0, c1, hw))
    got = _try(rctx, best[1], "socket", [best[2]], z)[0] if best else None
    if got is None:
        skipped.append({"room_id": rctx["room"]["id"], "use": "hall", "for": None,
                        "reason": f"no free wall of {CLEAR['hall_min']} m in the hall"})
        return
    _add(rctx, got[0], "socket", "hall", got[1], z, f"inferred: a power socket in the hall on its longest free wall "
                                                    f"({best[0]:.2f} m), {z:.2f} m over the floor",
         target=best[1].get("wall_id"))


def plan_level(building: dict, level: dict, style: Optional[dict] = None, decor: Optional[list] = None) -> dict:
    """The wall plates of a level (module docstring): ``{"level_id", "plates", "skipped", "rooms": {room id:
    {"kind", "switches", "sockets", "outlets", "doors"}}, "finish"}``. ``decor``: the level's decor as built (else
    the building's)."""
    flag = (style or {}).get("wall_plates")
    out = {"level_id": level["id"], "plates": [], "skipped": [], "rooms": {}, "finish": finish_of(style)}
    if flag in OPT_OUT or (isinstance(flag, str) and flag.lower() in OPT_OUT):
        out["skipped"].append({"room_id": None, "use": "all", "for": None,
                               "reason": f"the brief turns the wall plates off ({flag!r})"})
        return out
    ctx = _level_ctx(building, level, decor)
    for room in sorted(ctx["rooms"], key=lambda r: str(r["id"])):
        kind = room_kind(room)
        if kind is None:
            continue
        rctx = _room_ctx(ctx, room)
        if not rctx["lines"]:
            out["skipped"].append({"room_id": room["id"], "use": "all", "for": None,
                                   "reason": "no room edge lies on a wall"})
            continue
        _plan_switches(rctx, kind, out["skipped"])
        uses = SOCKET_USES.get(kind, ())
        for use, fn in (("bed", _bed_sockets), ("desk", _desk_sockets), ("tv", _tv_sockets),
                        ("worktop", _kitchen_sockets), ("mirror", _bath_sockets)):
            if use in uses:
                fn(rctx, out["skipped"])
        if "wall" in uses:
            _wall_sockets(rctx, kind, out["skipped"])
        if "hall" in uses:
            _hall_socket(rctx, out["skipped"])
        plates = rctx["plates"]
        out["plates"] += plates
        out["rooms"][room["id"]] = {
            "kind": kind, "switches": sum(1 for p in plates if p["kind"] == "switch"),
            "sockets": sum(1 for p in plates if p["kind"] in SOCKET_KINDS),
            "outlets": sum(2 if p["kind"] == "socket_double" else 1 for p in plates if p["kind"] in SOCKET_KINDS),
            "doors": [d["id"] for d in room_doors(rctx) if d["counted"]]}
    return out


def plan(building: dict, style: Optional[dict] = None, levels: Optional[list] = None) -> dict:
    """``plan_level`` of every level, merged: ``{"plates", "skipped", "rooms", "finish", "levels"}``."""
    out = {"plates": [], "skipped": [], "rooms": {}, "finish": finish_of(style), "levels": []}
    for lv in levels if levels is not None else building.get("levels") or []:
        got = plan_level(building, lv, style)
        out["plates"] += got["plates"]
        out["skipped"] += got["skipped"]
        out["rooms"].update(got["rooms"])
        out["levels"].append(lv["id"])
    return out


def summary(level_plan: dict) -> dict:
    """The level's record for the scene manifest's ``wall_plates`` (counts per room, what found no place)."""
    return {"plates": len(level_plan.get("plates") or []), "rooms": level_plan.get("rooms") or {},
            "skipped": level_plan.get("skipped") or [], "finish": level_plan.get("finish"), "rule": RULE,
            "lesson": CHECK}


# --------------------------------------------------------------------------
# the model review's M25 and Argus U29
# --------------------------------------------------------------------------

def plates_of(manifest: Optional[dict]) -> list[dict]:
    """The plate records of a scene manifest (the objects of detail ``wall_plates``)."""
    return [p for o in (manifest or {}).get("objects") or [] if isinstance(o, dict) and o.get("detail") == "wall_plates"
            for p in o.get("plates") or [] if isinstance(p, dict)]


def _plate_line(rctx: dict, p: dict) -> Optional[dict]:
    u = p.get("u") or [1.0, 0.0]
    best = None
    for line in rctx["lines"]:
        if line["u"][0] * u[0] + line["u"][1] * u[1] < 0.995:
            continue
        s, d = _st(line, p["center"])
        sp = _span_at(line, s)
        off = float(sp["offset"]) if sp else 0.0
        gap = d - off - float(p.get("standoff_m") or 0.0)
        if abs(gap) <= 0.03 and (best is None or abs(gap) < best[0]):
            best = (abs(gap), line, s)
    return (best[1], best[2]) if best else None


def bed_sides(rctx: dict, bed: dict, sockets: Sequence[dict]) -> dict:
    """``{"open": [sides with free wall beside the bed's head], "served": [sides with a socket], "need"}`` of a bed
    (pure): a side is open when the head wall runs on 0.25 m past the bed (not a corner); served when a socket of the
    room lies within ``BED_SOCKET_REACH_M`` of that head corner or was planned for that side of the bed; a double
    bed needs both open sides, a single bed one."""
    line = _back_line(rctx, bed)
    if line is None:
        return {"open": [], "served": [], "need": 0}
    b0, b1 = _piece_span(line, bed)
    out = {"open": [], "served": []}
    for sign, where in ((-1, "left"), (1, "right")):
        e = b1 if sign > 0 else b0
        lo, hi = sorted((e, e + sign * 0.25))
        if any(a - 1e-6 <= lo and hi <= b + 1e-6 for a, b in line["union"]):
            out["open"].append(where)
        corner = _xy(line, e)
        if any(G.distance(p["center"][:2], corner) <= BED_SOCKET_REACH_M or
               (p.get("for") == bed.get("id") and p.get("side") == where) for p in sockets):
            out["served"].append(where)
    out["need"] = min(len(out["open"]), 2 if bed.get("type") in DOUBLE_BEDS else 1)
    return out


def review(building: dict, plates: Sequence[dict], levels: Optional[list] = None) -> tuple[list[dict], int]:
    """``(problems, checked)`` of the plates against the building as built (pure; model review M25, Argus U29):
    ``no_switch`` (a room with doors and no light switch at any of them, major; a room's other door without one,
    ``door_no_switch``, minor, never in a hall, whose doors share its switches), ``on_glass`` / ``in_opening`` (a
    plate over an opening, critical), ``behind_piece`` (a plate behind a piece standing against its wall, major),
    ``off_wall`` (a plate on no wall face of its room, major), ``bed_no_socket`` (a bed in a bedroom with no socket by
    its head, major; one free side of a double bed, minor: ``bed_sides``), ``worktop_no_socket`` (a kitchen whose
    worktops on its walls have no socket over them, major). Each problem: ``{"problem", "severity", "target",
    "room_id", "message", ...numbers}``."""
    plates = list(plates or [])
    by_room: dict[str, list] = {}
    for p in plates:
        by_room.setdefault(str(p.get("room_id")), []).append(p)
    out, checked = [], 0
    for lv in levels if levels is not None else building.get("levels") or []:
        ctx = _level_ctx(building, lv)
        for room in sorted(ctx["rooms"], key=lambda r: str(r["id"])):
            kind = room_kind(room)
            if kind is None:
                continue
            rctx = _room_ctx(ctx, room)
            if not rctx["lines"]:
                continue
            checked += 1
            mine = by_room.get(room["id"], [])
            switches = [p for p in mine if p.get("kind") == "switch"]
            sockets = [p for p in mine if p.get("kind") in SOCKET_KINDS]
            share = CLEAR["share"].get(kind, CLEAR["share"]["default"])
            doors = [d for d in room_doors(rctx) if d["counted"]]
            if doors and not switches:
                out.append({"problem": "no_switch", "severity": "major", "target": room["id"], "room_id": room["id"],
                            "doors": [d["id"] for d in doors],
                            "message": f"{room['id']} has no light switch at its door "
                                       f"({', '.join(str(d['id']) for d in doors)}; UL112: a switch on the latch "
                                       f"side, {HEIGHTS['switch']:.2f} m over the floor)"})
            for door in doors if switches and kind not in ("hall", "stair") else []:
                c = _xy(door["line"], door["s"])
                reach = door["half"] + CLEAR["frame_overhang"] + max(CLEAR["switch_from_frame"]) + \
                    PLATE["size_m"] / 2.0 + share + 0.05
                if not any(G.distance(p["center"][:2], c) <= reach for p in switches):
                    out.append({"problem": "door_no_switch", "severity": "minor", "target": door["id"],
                                "room_id": room["id"], "door": door["id"],
                                "message": f"{door['why']} has no light switch beside it (the room's other door has "
                                           "one)"})
            for p in mine:
                hit = _plate_line(rctx, p)
                if hit is None:
                    out.append({"problem": "off_wall", "severity": "major", "target": p.get("id"),
                                "room_id": room["id"], "message": f"the {p.get('kind')} {p.get('id')} is on no wall "
                                                                  f"face of {room['id']}"})
                    continue
                line, s = hit
                hw = float(p.get("width_m") or PLATE["size_m"]) / 2.0
                hh = float(p.get("height_m") or PLATE["size_m"]) / 2.0
                z = float(p["center"][2]) - rctx["floor_z"]
                for op in line["openings"]:
                    if _overlap(s - hw, s + hw, op["s0"], op["s1"]) and _overlap(z - hh, z + hh, op["z0"], op["z1"]):
                        out.append({"problem": "on_glass" if op["glass"] else "in_opening", "severity": "critical",
                                    "target": p.get("id"), "room_id": room["id"], "opening": op["id"],
                                    "message": f"the {p.get('kind')} {p.get('id')} sits on the "
                                               f"{'glass of the ' if op['glass'] else ''}{op['type']} {op['id']}"})
                        break
                # a desk's socket under its top, a socket over the nightstand or the TV unit it serves
                ignore = {p.get("over"), p.get("for") if p.get("use") == "desk" else None} - {None}
                for pc in line["pieces"]:
                    if pc["id"] in ignore:
                        continue
                    if _overlap(s - hw, s + hw, pc["s0"], pc["s1"]) and _overlap(z - hh, z + hh, pc["z0"], pc["z1"]):
                        out.append({"problem": "behind_piece", "severity": "major", "target": p.get("id"),
                                    "room_id": room["id"], "piece": pc["id"],
                                    "message": f"the {p.get('kind')} {p.get('id')} is behind the {pc['type']} "
                                               f"{pc['id']} standing against its wall ({pc['z1']:.2f} m high)"})
                        break
            for bed in _room_pieces(rctx, BEDS) if kind == "bedroom" else []:
                got = bed_sides(rctx, bed, sockets)
                if got["need"] and not got["served"]:
                    out.append({"problem": "bed_no_socket", "severity": "major", "target": bed["id"],
                                "room_id": room["id"], "open_sides": got["open"],
                                "message": f"the {bed['type']} {bed['id']} has no power socket beside it (UL112: "
                                           "one beside each nightstand)"})
                elif len(got["served"]) < got["need"]:
                    out.append({"problem": "bed_no_socket", "severity": "minor", "target": bed["id"],
                                "room_id": room["id"], "open_sides": got["open"],
                                "message": f"one free side of the {bed['type']} {bed['id']} has no power socket"})
            runs = worktop_runs(rctx) if kind == "kitchen" else []
            over = [p for r in runs for p in sockets
                    if G.point_segment_distance(p["center"][:2], _xy(r["line"], r["s0"]), _xy(r["line"], r["s1"]))
                    <= 0.1 and float(p["center"][2]) - rctx["floor_z"] > r["top"]]
            if runs and not over:
                out.append({"problem": "worktop_no_socket", "severity": "major", "target": runs[0]["members"][0][0],
                            "room_id": room["id"],
                            "message": f"the kitchen {room['id']} has no power socket over its worktop "
                                       f"({', '.join(r['members'][0][0] for r in runs)})"})
    return out, checked


# --------------------------------------------------------------------------
# the plate as vertex / face lists (pure)
# --------------------------------------------------------------------------

def _face(verts: list, idx: list[int], outward: Sequence[float]) -> list[int]:
    """``idx`` wound so its normal points along ``outward`` (Newell's normal)."""
    from wenart.blender import geom2d

    nrm = geom2d.face_normal(verts, idx)
    return idx if nrm[0] * outward[0] + nrm[1] * outward[1] + nrm[2] * outward[2] >= 0 else idx[::-1]


def _ray_rect(cx: float, cz: float, th: float, x0: float, x1: float, z0: float, z1: float) -> tuple[float, float]:
    dx, dz = math.cos(th), math.sin(th)
    ts = []
    if dx > 1e-12:
        ts.append((x1 - cx) / dx)
    if dx < -1e-12:
        ts.append((x0 - cx) / dx)
    if dz > 1e-12:
        ts.append((z1 - cz) / dz)
    if dz < -1e-12:
        ts.append((z0 - cz) / dz)
    t = min(ts)
    return cx + dx * t, cz + dz * t


def _well(verts: list, faces: list, slots: list, cell: tuple, cx: float, finish: dict) -> None:
    """A socket's front face around its round well (the cell ``(x0, x1, z0, z1)`` of the front), the well's wall and
    bottom, and the two pin holes (local frame: x along the wall, y out of it, z up)."""
    x0, x1, z0, z1 = cell
    D, r, wd = PLATE["depth_m"], PLATE["well_r_m"], PLATE["well_depth_m"]
    n = int(PLATE["segments"])
    a0 = math.pi / n
    angs = [a0 + 2 * math.pi * k / n for k in range(n)]
    corners = []
    for px, pz in ((x0, z0), (x1, z0), (x1, z1), (x0, z1)):
        a = math.atan2(pz, px - cx) % (2 * math.pi)
        corners.append((a if a >= a0 else a + 2 * math.pi, px, pz))
    well_slot = 0 if finish.get("well") == "plate" else 1
    base = len(verts)
    for th in angs:
        verts.append((cx + r * math.cos(th), D, r * math.sin(th)))          # the rim on the front
    for th in angs:
        rx, rz = _ray_rect(cx, 0.0, th, x0, x1, z0, z1)
        verts.append((rx, D, rz))                                             # the front's outline along the rays
    for th in angs:
        verts.append((cx + r * math.cos(th), D - wd, r * math.sin(th)))     # the rim at the well's bottom
    for k in range(n):
        k1 = (k + 1) % n
        lo, hi = angs[k], angs[k] + 2 * math.pi / n
        # rim k, rim k1, the outline at k1, the rect corners between (back towards k), the outline at k
        idx = [base + k, base + k1, base + n + k1]
        for a, px, pz in sorted(corners, reverse=True):
            if lo + 1e-9 < a < hi - 1e-9:
                verts.append((px, D, pz))
                idx.append(len(verts) - 1)
        idx.append(base + n + k)
        faces.append(_face(verts, idx, (0.0, 1.0, 0.0)))
        slots.append(0)
        wall = [base + k, base + 2 * n + k, base + 2 * n + k1, base + k1]
        mid = (cx + r * math.cos((lo + hi) / 2.0), 0.0, r * math.sin((lo + hi) / 2.0))
        faces.append(_face(verts, wall, (cx - mid[0], 0.0, -mid[2])))
        slots.append(well_slot)
    faces.append(_face(verts, [base + 2 * n + k for k in range(n)], (0.0, 1.0, 0.0)))
    slots.append(well_slot)
    m = int(PLATE["pin_segments"])
    for sx in (-PLATE["pin_pitch_m"] / 2.0, PLATE["pin_pitch_m"] / 2.0):
        b0 = len(verts)
        for k in range(m):
            th = 2 * math.pi * k / m
            verts.append((cx + sx + PLATE["pin_r_m"] * math.cos(th), D - wd + 0.0004, PLATE["pin_r_m"] * math.sin(th)))
        faces.append(_face(verts, list(range(b0, b0 + m)), (0.0, 1.0, 0.0)))
        slots.append(1)


def plate_mesh(kind: str, finish: Optional[dict] = None) -> tuple[list, list, list]:
    """``(verts, faces, material slots)`` of one plate in its own frame (x along the wall, y out of the wall face, z up
    from the plate's centre; module docstring). Slot 0: the plate's finish, slot 1: the dark insert. No back face (it
    lies 0.5 mm off the wall)."""
    finish = finish or FAMILY_FINISH["default"]
    W = PLATE["double_w_m"] if kind == "socket_double" else PLATE["size_m"]
    H, D, c, g = PLATE["size_m"], PLATE["depth_m"], PLATE["chamfer_m"], PLATE["back_gap_m"]
    fx, fz = W / 2.0 - c, H / 2.0 - c
    verts = [(-W / 2.0, g, -H / 2.0), (W / 2.0, g, -H / 2.0), (W / 2.0, g, H / 2.0), (-W / 2.0, g, H / 2.0),
             (-fx, D, -fz), (fx, D, -fz), (fx, D, fz), (-fx, D, fz)]
    faces, slots = [], []
    for (i, j), out in (((0, 1), (0, 0, -1)), ((1, 2), (1, 0, 0)), ((2, 3), (0, 0, 1)), ((3, 0), (-1, 0, 0))):
        faces.append(_face(verts, [i, j, j + 4, i + 4], out))
        slots.append(0)
    if kind == "switch":
        faces.append(_face(verts, [4, 5, 6, 7], (0, 1, 0)))
        slots.append(0)
        rw = PLATE["rocker_m"] / 2.0
        p0, p1 = PLATE["rocker_proud_m"]
        b = len(verts)
        verts += [(-rw, D, -rw), (rw, D, -rw), (rw, D, rw), (-rw, D, rw),
                  (-rw, D + p0, -rw), (rw, D + p0, -rw), (rw, D + p1, rw), (-rw, D + p1, rw)]
        faces.append(_face(verts, [b + 4, b + 5, b + 6, b + 7], (0, 1, 0)))
        slots.append(0)
        for (i, j), out in (((0, 1), (0, 0, -1)), ((1, 2), (1, 0, 0)), ((2, 3), (0, 0, 1)), ((3, 0), (-1, 0, 0))):
            faces.append(_face(verts, [b + i, b + j, b + j + 4, b + i + 4], out))
            slots.append(0)
        return verts, faces, slots
    if kind == "socket_double":
        m = PLATE["module_m"] / 2.0
        _well(verts, faces, slots, (-fx, 0.0, -fz, fz), -m, finish)
        _well(verts, faces, slots, (0.0, fx, -fz, fz), m, finish)
    else:
        _well(verts, faces, slots, (-fx, fx, -fz, fz), 0.0, finish)
    return verts, faces, slots


def level_mesh(plates: Sequence[dict], finish: Optional[dict] = None) -> tuple[list, list, list]:
    """All plates of a level as one mesh (world coordinates): each plate's ``plate_mesh`` placed at its ``center`` on
    its wall (``u`` along, ``n`` out of the wall)."""
    cache: dict = {}
    verts: list = []
    faces: list = []
    slots: list = []
    for p in plates:
        kind = p.get("kind") or "socket"
        if kind not in cache:
            cache[kind] = plate_mesh(kind, finish)
        pv, pf, ps = cache[kind]
        (ux, uy), (nx, ny) = p["u"][:2], p["n"][:2]
        ox, oy, oz = (float(v) for v in p["center"][:3])
        off = len(verts)
        verts += [(ox + ux * x + nx * y, oy + uy * x + ny * y, oz + z) for x, y, z in pv]
        faces += [[i + off for i in f] for f in pf]
        slots += ps
    return verts, faces, slots


# --------------------------------------------------------------------------
# bpy
# --------------------------------------------------------------------------

def build_wall_plates(level_plan: dict, level: dict, collection, library, manifest_objects: list,
                      assumed: list) -> Optional[str]:
    """The level's plates as one object (module docstring); its manifest record and one ``assumed`` row per plate.
    Returns the object's name, None when the level has no plate."""
    from wenart.blender import common

    plates = level_plan.get("plates") or []
    if not plates:
        return None
    finish = level_plan.get("finish") or finish_of(None)
    verts, faces, slots = level_mesh(plates, finish)
    mats = [library.get(finish["plate"], None, colour=finish.get("colour")), library.get(INSERT_MATERIAL)]
    name = f"wall_plates_{level['id']}"
    ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="wall_plate",
                                status="assumed", materials=mats, face_material_indices=slots)
    ob.pass_index = 0
    counts = {k: sum(1 for p in plates if p["kind"] == k) for k in ("switch", "socket", "socket_double")}
    reason = (f"inferred (UL112): {counts['switch']} light switches beside the doors, {counts['socket']} sockets and "
              f"{counts['socket_double']} socket pairs where they are used, {finish.get('name')} plates of the "
              f"{finish.get('family') or 'house'} style; not in the documents")
    manifest_objects.append({
        "name": ob.name, "wenart_id": name, "kind": "wall_plate", "status": "assumed", "level_id": level["id"],
        "element_id": level["id"], "evidence": [], "material": mats[0].name, "textured": library.textured(mats[0]),
        "pass_index": 0, "detail": "wall_plates", "source": "inferred", "inferred": True,
        "finish": {k: finish.get(k) for k in ("name", "plate", "colour", "well", "family")},
        "plates": [{k: p.get(k) for k in ("id", "kind", "use", "for", "room_id", "level_id", "wall_id", "center", "u",
                                          "n", "z_m", "width_m", "height_m", "depth_m", "standoff_m", "side", "serves",
                                          "reason") if p.get(k) is not None} for p in plates],
        "faces": len(faces), "assumed": {"detail": "wall_plates", "reason": reason, "inferred": True}})
    for p in plates:
        assumed.append({"object": p["id"], "field": "wall_plate", "value": f"{p['kind']} at {p['z_m']:.2f} m",
                        "reason": p["reason"], "parent": p["room_id"], "kind": "wall_plate"})
    return ob.name
