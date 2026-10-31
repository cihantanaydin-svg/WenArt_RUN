"""Building shell: walls with boolean-cut openings, door and window geometry,
floors and ceilings (docs/milestone3.md §3, shell.py).

Walls: one object per wall element (named by its id, so every object stays
traceable and the per-kind counts match the JSON), an extruded rectangle from
the centre line, thickness and height, grouped in one collection per level.
Faces get material slots by what they face: interior (style walls), exterior
(``plaster_exterior`` for the outward faces of exterior walls that look into
no indoor room: a merged exterior run can face a room along part of its
length, ``wall_face_slot``) or wet-room (``wet_walls`` for faces looking into
a bathroom / wc / kitchen).

Openings: a boolean difference per opening with a cutter box of
width x (thickness + 2 cm) x height centred on the wall centre line; doors
start at the floor, windows at the sill. The JSON centre is projected onto
the wall centre line first (a door block inserted on the wall face is the
normal CAD convention and the ingest accepts it); the shift is recorded as
``center_shift`` in the manifest, as ``assumed`` when it exceeds 1 mm and as a
warning when it exceeds half the wall thickness. The cutters are temporary
objects, the modifiers are applied through the depsgraph
(``common.evaluated_mesh``), then the cutters are deleted. The EXACT solver
is the default in Blender 5.2 (solver items: FLOAT, EXACT, MANIFOLD); a wall
built from touching pieces (``wall_pieces``: parapet stretches) is cut with
``use_self``. Every cut wall is then checked against its solid
(``wall_cut_problems``): one that lost anything outside its cutters stops the
build (``WallLost``), never a silently missing wall.

Every door and plain opening gets a threshold face (``<id>_threshold``, kind
``floor``, the material of the adjacent room floor) because the room floors
stop at the wall faces and the cutter removes the wall bottom. A plain
opening without a height is cut through the full wall height; on a level
with nothing above it a soffit face (``<id>_soffit``, kind ``ceiling``)
closes the wall top over the opening.

The outward side of an exterior wall is found by probing both sides of the
wall against the room polygons of the level (the side that lies in no room
is outside); when both or neither side is in a room the bounding-box centre
of the level decides and a warning is recorded.

Defaults for ``null`` values are recorded as ``assumed`` in the manifest:
door height 2.10 m, window sill 0.90 m, window height 1.20 m (1.40 m when the
opening is wider than 1.5 m), plain opening full height, wall height = level
ceiling height, slab thickness 0.30 m (walls of a level with a level above
it run up to the next floor so the slab zone is closed).

Milestone 6 (docs/milestone6.md §5 rows 3 and 9):

- before the per-face material probe, every wall mesh is cut with vertical
  planes across the wall (``bmesh.ops.bisect_plane``) at every room corner
  that lies along the wall (``wall_split_positions``), so a wall shared by a
  bathroom and a bedroom gets tiles on the bathroom span only (one face
  used to take the material of its centre);
- wood door leaves take the veneer of their wood (``vocabulary.veneer_for``,
  grain along the box UV v = world Z: vertical) and get a pair of steel
  lever handles at 1.02 m on both faces (``door_handle_parts``; the door's
  wenart id and pass index, so ``--hide`` hides them with the door);
- dry rooms get a painted skirting board 8 cm x 12 mm along their walls,
  interrupted at doors, plain openings and floor-level windows
  (``skirting_spans``), pass index 0;
- handles and skirting are design details: status ``assumed``, a scene
  manifest ``assumed`` entry with ``parent`` (door or room id), ``kind`` and
  ``reason``; nothing is added to the building JSON.

Milestone 7 (docs/milestone7.md §6.4):

- doorless openings (type ``opening``) are cut to their ``height`` (the
  recognition core writes 2.10 m and lists it in the opening's ``assumed``;
  every field listed there is recorded as assumed here too), with the
  threshold face and no frame or leaf; without a height they still run to
  the wall top (Milestone 3);
- virtual separators (``virtual: true``, ``wall_id: null``) have no
  geometry: a manifest entry (``has_geometry: false``, ``virtual``,
  ``line``) and nothing else; the room floors and ceilings meet at the line;
  the skirting stops along it. An opening without a wall that is not
  virtual is a warning, never a crash;
- stairs (``furniture`` of type ``stair``) are fixed equipment built here,
  not by furniture.py: ``plan_stairs`` (pure: rise = ceiling + the assumed
  0.15 m slab, or floor to floor when a level lies above) and
  ``build_stairs`` (steps, landing, rails as ``furn_<id>``: kind
  ``furniture``, the piece's pass index; the shaft and cap that close the
  ceiling opening as ``<id>_void``: kind ``ceiling``, status ``assumed``);
  ``build_floors_ceilings(..., stairs=)`` cuts the opening out of every
  ceiling it crosses (``geom2d.polygon_faces``); pieces with ``build:
  false`` are not built and listed;
- dining and prayer rooms take the living-room slots (``slot_room_type``):
  dry floor, plain walls, skirting.

Milestone 10 (docs/milestone10.md §3.2, §1.6b rows 12, 13, 20), the whole building (``whole`` arguments; None
keeps the M3-M9 shell): slabs (``slab_plan`` / ``build_slabs``), walls to the next floor or cut by the roof
underside and the terrace parapets, closed L-joins, the facade look and the drawn facade parts on the outward
faces, sills and balcony railings (``build_outside_details``, kind ``railing``), floors and ceilings with the
stair voids and the sloped attic ceilings. A stair on the top level (no level above) never rises to a floor that is
not there or through the roof (``top_level_stair``): over a stair of the level below it is that stair's drawn upper
end (``stair_arrival``: not built again, ``not_built`` with ``arrives_from`` and the slab opening, which the floor
keeps; no ceiling opening), any other stops under the roof underside (assumed, a warning; no opening, no shaft).
The inside and opening looks go through track F's functions
(``wall_face_material``, ``wet_wall_look``, ``accent_walls``, ``door_look``, ``window_frame_look``,
``facade_look`` of ``wenart/blender/looks.py``; thin wrappers with the M9 looks as the fallback) and the outside
materials through ``exterior_material`` / ``look_material``.

Milestone 10 doors and windows (docs/milestone10.md §4.7, track F): a door or window with Milestone 10 values
(``door_geometry_m10`` / ``window_geometry_m10``: a style door style, handle or colour, a drawn non-swing
operation; a Milestone 10 frame material or colour, drawn mullions or transoms) is built from
``parametric.door_parts`` / ``window_parts`` (``build_door_m10`` / ``build_window_m10``): the drawn operation
wins (sliding and barn doors hang on the face of the room they open into, ``opening_room_side``; pocket, double,
folding and fixed doors as drawn, a fixed one without handles), the frame material's profile with the drawn
mullions and transoms, an inside sill on the room side (assumed), the outside sill from the frame's outer edge;
the ``door`` / ``window`` records in the manifest. The others keep the Milestone 6-9 door and window. The floor,
ceiling, trim, skirting, stair and slab slots take their colour name and ``params`` (``slot_material``).

Fix round after P3 (16-17 Oct 2026): door stops. What: every door in a frame has jamb and head stops on the leaf
face away from the room it opens into (``door_m6_parts`` for the Milestone 6 door, ``parametric.door_parts`` for
the Milestone 10 styles; ``parametric.door_stop_boxes``), in the ``<id>_frame`` object. Why: the closed leaf is
5 mm smaller than its frame on every side, so a slit ran straight through the wall; pod P3's corridor view
cam_r_L1_koridor_2_2 saw the sunlit roof terrace through it (a glowing line round the leaf, depth 196 m against the
60 m interior bound). How: the stops overlap the leaf by 10 mm (5 mm under a Milestone 10 head), stay inside the
wall depth and leave the leaf, its material and the door rays as they were.

Fix round after P4b (17 Oct 2026; pod P4b, real03's fire stair, yangin_merdiveni_3): stairs meet their walls and
their structure is smooth. What: ``build_stairs`` builds every plan through ``stair_build_plan``
(``stair_wall_joints`` on the level's walls; ``plan_stairs`` and ``parametric.stair_plan`` keep their plans): a
flight side or landing edge within ``STAIR_JOINT_SNAP_M`` of a parallel wall face is built ``STAIR_JOINT_EMBED_M``
into the wall (``plan["wall_joints"]``, an assumed ``stair_wall_joint`` entry, the stair record's ``wall_joints``);
the stair's
structure slot (stringer sides, soffit, landing edge) is the wall colour as a smooth paint (``stair_structure_slot``:
no wall texture set). Why: the drawn U-stair is exactly as wide as its stairwell but its centre was read 0.9 mm off,
so the right flight and the landing stopped 0.9 mm short of the wall and the rig light came through as a slit down
the wall; the wall set's bump, at wall scale, read as coarse plaster on the 0.6 m stringer seen up close. How: the
drawn footprint stays in the building JSON (fixed equipment as drawn); only the mesh widens, by at most 6 cm.

Pass before P5 (17 Oct 2026; the review of the fix round after P4b). What: a walls slug whose bare request gets a
shell slot's texture set back (``shell_stand_in``: ``plaster_white``, the ceiling slot's white_plaster_02) gives the
stair structure ``STAIR_STRUCTURE_PAINT`` in the walls' colour (``stair_structure_slot``). Why: every "white walls"
style (synthetic-01/02/05/06/07, real01, the profile fallback) is ``plaster_white`` + white_plaster_02; dropping the
asset left a bare ``plaster_white``, which ``materials.MaterialLibrary.get`` with the shell lever on maps to the
ceiling slot and gives white_plaster_02 back, so the stringer kept the wall's plaster photo and normal map (material
``plaster_white__white_plaster_02__ceiling``) while its record said "smooth paint". How: the paint takes the walls'
colour phrase when it colours the walls, else the slug's own flat colour as a ``tint`` over the paint's, so the
colour stays the walls' (0.85, 0.84, 0.80 for ``plaster_white``) and the paint's ``plaster`` slot gives its layers
(corner AO, 4 mm bevel) with no set. real02/03/04 (``paint`` + plastered_wall in warm greige) keep
``paint`` in warm greige, as before.
"""
from __future__ import annotations

import math

from wenart import geometry as G
from wenart.blender import details as D
from wenart.blender import geom2d
from wenart.blender import parametric as P

DEFAULTS = {
    "door_height": 2.10,
    "window_sill": 0.90,
    "window_height": 1.20,
    "window_height_wide": 1.40,
    "window_wide_threshold": 1.5,
    "slab_thickness": 0.30,
    "frame_width": 0.05,
    "leaf_thickness": 0.04,
    "glass_thickness": 0.006,
    "cutter_extra": 0.02,
    "face_probe": 0.05,          # distance beyond a wall face for the room probes
    "threshold_lift": 0.001,     # thresholds above a stacked wall top (no coplanar faces)
    "shift_assumed": 0.001,      # centre shift recorded as assumed above this
}
# The guard after the opening booleans (``wall_cut_problems``): a wall may lose up to its cutters' volume, and its
# extent only on a side a cutter reaches; these tolerances (m, m³) cover the float mesh of the evaluated result.
WALL_CUT_TOL_M = 1e-3
WALL_CUT_TOL_M3 = 1e-3
WET_ROOM_TYPES = {"bathroom", "wc", "kitchen"}
# Milestone 11 (docs/milestone11.md §1.3 M2): a kitchen is no wet room for its walls (it had full-height tiles): its
# walls take the style's walls and a tiled splashback band behind the counter runs (``splashback_plan``); its floor
# is the brief's floor when that is wet-safe, else the wet floor (``floor_style``).
WET_WALL_ROOM_TYPES = {"bathroom", "wc"}
KITCHEN_TYPES = {"kitchen"}
# Rooms without skirting: wet rooms keep their tiles to the floor, a balcony is outside.
NO_SKIRTING_TYPES = WET_WALL_ROOM_TYPES | {"balcony"}
# The splashback (M2): a tile band this high from the counter top, on the wall behind the counter run.
SPLASHBACK = {"height": 0.60, "thickness": 0.008, "gap": 0.002, "counter_top": 0.90, "wall_reach": 0.20,
              "types": ("kitchen_counter", "sink_kitchen", "stove", "hob", "dishwasher", "oven")}
# 26 Oct 2026 (Argus on real06: the splashback behind the counter f_L0_032 covered the 2.9 m pass-through o_L0_001
# between the kitchen and the living room): a finish or built-in along a wall never covers an opening of that wall
# (``wall_face_openings``, ``split_band``): it is cut at every door, window, plain opening and virtual separator with
# the opening's width and height range, and the opening is always cut.
WALL_FINISH_OPENING_CLEAR = 0.01  # m: a band stops this far from an opening's edges (no face shared with the reveal)
WALL_FINISH_MIN_PIECE = 0.05      # m: a band piece narrower or lower than this is left out
WALL_FACE_REACH = 0.10            # m: a wall face lies within half the wall's thickness + this of its centre line
# Milestone 7 room types that take another type's material slots (docs/milestone7.md §6.4).
ROOM_SLOT_TYPES = {"dining": "living", "prayer": "living", "stair": "hall", "shaft": "hall"}
SKIRTING_H = 0.08
SKIRTING_T = 0.012
SKIRTING_MIN_SPAN = 0.02
# A room corner splits a wall when it lies within half the wall thickness + this of the centre line
# and this far from the wall's ends.
SPLIT_REACH_EXTRA = 0.1
SPLIT_END_MARGIN = 0.01
# Lever handles (docs/milestone6.md §5 row 9): lever axis this high above the floor, this far
# from the latch-side edge of the leaf; the furthest point stands HANDLE_DEPTH proud of the leaf face.
HANDLE_HEIGHT = 1.02
HANDLE_EDGE_INSET = 0.075
HANDLE_DEPTH = 0.055


class WallLost(RuntimeError):
    """The opening booleans took (part of) a wall outside its cutters (``wall_cut_problems``): the build stops
    with the wall ids (CLAUDE.md: nothing is removed silently)."""


def slot_room_type(room_type: str | None) -> str | None:
    """The room type whose material slots a room uses: dining and prayer rooms the living room's."""
    return ROOM_SLOT_TYPES.get(room_type, room_type)


def is_virtual(opening: dict) -> bool:
    """A virtual separator (docs/milestone7.md §2.7.1): ``virtual: true`` with no wall; it has no geometry."""
    return bool(opening.get("virtual")) and opening.get("wall_id") is None


# --------------------------------------------------------------------------
# Opening sizes (pure Python, used by shell and the tests)
# --------------------------------------------------------------------------

def opening_vertical(opening: dict, level: dict, levels_above: bool) -> tuple[float, float, dict]:
    """``(bottom_z, top_z, assumed)`` of an opening in world Z.

    ``assumed`` lists the defaults that filled ``null`` fields of the JSON
    and the values the JSON itself lists as assumed (Milestone 7: the
    opening's ``assumed`` list, e.g. a doorless gap's 2.10 m height)."""
    floor_z = float(level["elevation"])
    ceiling = float(level["ceiling_height"])
    assumed = {}
    kind = opening["type"]
    height = opening.get("height")
    sill = opening.get("sill_height")
    listed = opening.get("assumed") or ()
    for field, value in (("height", height), ("sill_height", sill)):
        if field in listed and value is not None:
            assumed[field] = float(value)
    if kind == "door":
        if sill is None:
            sill = 0.0
        if height is None:
            height = DEFAULTS["door_height"]
            assumed["height"] = height
    elif kind == "window":
        if sill is None:
            sill = DEFAULTS["window_sill"]
            assumed["sill_height"] = sill
        if height is None:
            wide = float(opening["width"]) > DEFAULTS["window_wide_threshold"]
            height = DEFAULTS["window_height_wide"] if wide else DEFAULTS["window_height"]
            assumed["height"] = height
    else:  # plain opening: full height unless the JSON says otherwise
        if sill is None:
            sill = 0.0
        if height is None:
            height = ceiling - float(sill)
            assumed["height"] = height
    bottom = floor_z + float(sill)
    if kind in ("door", "opening") and opening.get("threshold_z") is not None:
        # Milestone 12 (track L): a door's frame starts at its threshold (the higher room floor beside it).
        bottom = float(opening["threshold_z"]) + float(sill)
    if kind == "opening":
        # Runs up to the ceiling; build_walls cuts through the wall top when the
        # opening reaches it and build_openings closes it with a soffit face.
        top = min(bottom + float(height), floor_z + ceiling)
    else:
        # A door or window taller than the ceiling stops 1 mm below it so the
        # cutter never shares a face with the wall top.
        top = min(bottom + float(height), floor_z + ceiling - 0.001)
    return bottom, top, assumed


def piece_built(piece: dict) -> bool:
    """Milestone 12 (lead note of 10 Oct 2026): a furniture piece is in the scene unless ``build: false``, its type is
    ``unknown`` (no untyped piece is built, CLAUDE.md) or its fitted asset says ``method: none`` (no model fitted)."""
    asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
    return piece.get("build", True) is not False and piece.get("type") != "unknown" and asset.get("method") != "none"


def room_floor_z(room: dict, level: dict) -> float:
    """Milestone 12 (docs/milestone12.md §3.2, track L): a room's finished floor: its level's elevation + its
    ``floor_offset_m`` (0 when not marked)."""
    return float(level["elevation"]) + float(room.get("floor_offset_m") or 0.0)


def wall_base_drop(wall: dict, rooms: list[dict], reach_extra: float = 0.05) -> float:
    """Milestone 12 (pure): how far (<= 0) a wall starts below its level's floor: the lowest negative
    ``floor_offset_m`` of the rooms whose outline runs along it (within half its thickness + ``reach_extra``)."""
    low = 0.0
    reach = float(wall["thickness"]) / 2.0 + reach_extra
    a, b = wall["start"], wall["end"]
    for r in rooms:
        off = float(r.get("floor_offset_m") or 0.0)
        poly = r.get("polygon") or []
        if off >= low or len(poly) < 3:
            continue
        for i in range(len(poly)):
            p, q = poly[i], poly[(i + 1) % len(poly)]
            mid = G.segment_midpoint(p, q)
            if G.point_segment_distance(mid, a, b) <= reach and G.distance(p, q) > 1e-6:
                low = off
                break
    return low


def inner_step(opening: dict, wall: dict, rooms: list[dict], level: dict) -> dict | None:
    """Milestone 12 (pure): the step block under a door or doorless opening between two rooms whose floors differ
    by more than 5 mm: ``{"polygon", "z0", "z1", "rise", "low_room", "high_room"}`` (the opening width x the wall
    thickness, from the lower floor up to the threshold), else None."""
    cx, cy, _ = opening_centre_on_wall(opening, wall)
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + 0.05
    sides = []
    for s in (1.0, -1.0):
        p = (cx + s * nx * reach, cy + s * ny * reach)
        sides.append(next((r for r in rooms if len(r.get("polygon") or []) >= 3 and G.point_in_polygon(p, r["polygon"])),
                          None))
    if None in sides:
        return None
    za, zb = room_floor_z(sides[0], level), room_floor_z(sides[1], level)
    if abs(za - zb) <= 0.005:
        return None
    low, high = (sides[0], sides[1]) if za < zb else (sides[1], sides[0])
    top = float(opening["threshold_z"]) if opening.get("threshold_z") is not None else max(za, zb)
    poly = G.rotated_rectangle((cx, cy), (float(opening["width"]), float(wall["thickness"])),
                               G.segment_angle_deg(wall["start"], wall["end"]))
    return {"polygon": [tuple(p) for p in poly], "z0": min(za, zb), "z1": top, "rise": round(abs(za - zb), 4),
            "low_room": low["id"], "high_room": high["id"]}


def wall_height(wall: dict, level: dict, has_level_above: bool) -> tuple[float, dict]:
    """Wall height and the assumptions used."""
    assumed = {}
    h = wall.get("height")
    if h is None:
        h = float(level["ceiling_height"])
        assumed["height"] = h
    h = float(h)
    if has_level_above:
        h += DEFAULTS["slab_thickness"]
        assumed["slab_thickness"] = DEFAULTS["slab_thickness"]
    return h, assumed


def opening_centre_on_wall(opening: dict, wall: dict) -> tuple[float, float, float]:
    """``(cx, cy, shift)``: the opening centre projected onto the wall centre
    line and the distance it moved. A door block drawn on the wall face sits
    half a thickness off the centre line; the cutter and the frame must still
    be centred in the wall."""
    ax, ay = float(wall["start"][0]), float(wall["start"][1])
    bx, by = float(wall["end"][0]), float(wall["end"][1])
    px, py = float(opening["center"][0]), float(opening["center"][1])
    dx, dy = bx - ax, by - ay
    length_sq = dx * dx + dy * dy
    if length_sq < 1e-12:
        return px, py, 0.0
    t = ((px - ax) * dx + (py - ay) * dy) / length_sq
    cx, cy = ax + t * dx, ay + t * dy
    return cx, cy, math.hypot(px - cx, py - cy)


def foreign_cuts(wall: dict, walls_by_id: dict, openings: list[dict], tol_deg: float = 3.0,
                 min_overlap_m: float = 0.05) -> list[tuple[dict, tuple[float, float], float]]:
    """Openings of OTHER walls that this wall overlaps (pure; pod P5, 11 Oct 2026): real03's facade line
    ``w_L0_002`` (0.15 m) runs along the outer face of ``w_L0_005`` (0.45 m), so the window ``win_L0_002`` cut only
    its own wall and stayed closed: a dark bedroom and a sill without glass. Returns ``[(opening, (cx, cy),
    depth)]``: the cutter centre (on the host wall's normal, midway over both walls) and its depth across both,
    for every opening whose host wall is parallel to this one (within ``tol_deg``) and whose rectangle overlaps this
    wall's footprint along the wall by at least ``min_overlap_m``. Only windows and doors cut through (pod P8, 11 Oct
    2026): a plain ``opening`` is a gap in its own line, e.g. real03's 0.25 m gap ``o_L0_001`` in the facade line
    ``w_L0_001`` where the column ``w_L0_003`` stands; cut through the column it opened a full-height slit to the
    outside. Where another layer is solid the wall is closed."""
    out = []
    wx0, wy0 = float(wall["start"][0]), float(wall["start"][1])
    wx1, wy1 = float(wall["end"][0]), float(wall["end"][1])
    wlen = math.hypot(wx1 - wx0, wy1 - wy0)
    if wlen < 1e-9:
        return out
    wu = ((wx1 - wx0) / wlen, (wy1 - wy0) / wlen)
    wt = float(wall["thickness"])
    for o in openings:
        host = walls_by_id.get(o.get("wall_id"))
        if host is None or host["id"] == wall["id"] or is_virtual(o) or o.get("type") not in ("window", "door"):
            continue
        hx0, hy0 = float(host["start"][0]), float(host["start"][1])
        hx1, hy1 = float(host["end"][0]), float(host["end"][1])
        hlen = math.hypot(hx1 - hx0, hy1 - hy0)
        if hlen < 1e-9:
            continue
        hu = ((hx1 - hx0) / hlen, (hy1 - hy0) / hlen)
        if abs(hu[0] * wu[1] - hu[1] * wu[0]) > math.sin(math.radians(tol_deg)):
            continue                                    # not parallel
        n = (-hu[1], hu[0])
        cx, cy, _ = opening_centre_on_wall(o, host)
        ht = float(host["thickness"])
        d = (wx0 - cx) * n[0] + (wy0 - cy) * n[1]       # this wall's centre line, across the host's
        if abs(d) >= (ht + wt) / 2.0 - 1e-6:
            continue                                    # side by side, not overlapping in depth
        half = float(o["width"]) / 2.0
        a = ((cx - wx0) * wu[0] + (cy - wy0) * wu[1])   # the opening centre along this wall
        overlap = min(a + half, wlen) - max(a - half, 0.0)
        if overlap < min_overlap_m:
            continue
        lo, hi = min(-ht / 2.0, d - wt / 2.0), max(ht / 2.0, d + wt / 2.0)
        mid = (lo + hi) / 2.0
        out.append((o, (cx + n[0] * mid, cy + n[1] * mid), hi - lo))
    return out


def along_wall(wall: dict, point) -> float:
    """Distance of ``point`` along the wall from its start (pure; the point projected on the centre line)."""
    ax, ay = float(wall["start"][0]), float(wall["start"][1])
    dx, dy = float(wall["end"][0]) - ax, float(wall["end"][1]) - ay
    length = math.hypot(dx, dy)
    if length < 1e-12:
        return 0.0
    return ((float(point[0]) - ax) * dx + (float(point[1]) - ay) * dy) / length


def span_covered(span: tuple, spans: list[tuple], tol: float = 0.02) -> bool:
    """True when the cut ``span`` ``(a0, a1, z0, z1)`` (along the wall, height) lies inside one of ``spans`` (within
    ``tol``): a cut there removes nothing more (pure; pod P8, 11 Oct 2026: real03 draws a window on three or four
    stacked wall layers; every copy cut every layer, about 100 boolean cuts, and the scene build took twice as
    long)."""
    a0, a1, z0, z1 = span
    return any(b0 - tol <= a0 and a1 <= b1 + tol and c0 - tol <= z0 and z1 <= c1 + tol for b0, b1, c0, c1 in spans)


def cut_full_height(top: float, floor_z: float, wall_h: float) -> bool:
    """True when an opening reaches the top of its wall (plain opening on a
    level with nothing above): the cutter then runs through the wall top."""
    return top >= floor_z + wall_h - 1e-6


def wall_outward_normal(wall: dict, rooms: list[dict], level_centre) -> tuple[tuple[float, float], bool]:
    """``((nx, ny), ambiguous)``: unit normal pointing to the outside of a wall.

    Three points along the wall are probed ``face_probe`` beyond each face
    against the room polygons; the side with fewer room hits is outside. When
    both sides score the same (no rooms, or rooms on both sides) the side away
    from ``level_centre`` is used and ``ambiguous`` is True."""
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + DEFAULTS["face_probe"]
    polys = [r["polygon"] for r in rooms if len(r["polygon"]) >= 3]
    hits = {1: 0, -1: 0}
    for t in (0.25, 0.5, 0.75):
        px, py = G.point_along_segment(wall["start"], wall["end"], t)
        for side in (1, -1):
            probe = (px + side * nx * reach, py + side * ny * reach)
            if any(G.point_in_polygon(probe, poly) for poly in polys):
                hits[side] += 1
    if hits[1] != hits[-1]:
        side = 1 if hits[1] < hits[-1] else -1
        return (side * nx, side * ny), False
    mid = G.segment_midpoint(wall["start"], wall["end"])
    side = -1 if (level_centre[0] - mid[0]) * nx + (level_centre[1] - mid[1]) * ny > 0 else 1
    return (side * nx, side * ny), True


def adjacent_room(centre, wall: dict, rooms: list[dict]) -> dict | None:
    """The room next to an opening: the left side of the wall direction is
    probed first, then the right. None when no room polygon is there."""
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + DEFAULTS["face_probe"]
    for side in (1, -1):
        probe = (centre[0] + side * nx * reach, centre[1] + side * ny * reach)
        for room in rooms:
            if len(room["polygon"]) >= 3 and G.point_in_polygon(probe, room["polygon"]):
                return room
    return None


def door_sides(centre, wall: dict, rooms: list[dict]) -> list:
    """The room types on the two sides of an opening (None for no room: outside), the left side of the wall direction
    first (28 Oct 2026: ``looks.role_door_style``)."""
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + DEFAULTS["face_probe"]
    out = []
    for side in (1, -1):
        probe = (centre[0] + side * nx * reach, centre[1] + side * ny * reach)
        room = next((r for r in rooms if len(r["polygon"]) >= 3 and G.point_in_polygon(probe, r["polygon"])), None)
        out.append(room.get("room_type") if room else None)
    return out


# = opening_models.OPEN_AIR_TYPES: no architrave on the face of an open-air room (a facade face)
ARCHITRAVE_OUTSIDE_TYPES = ("balcony", "terrace", "roof_terrace", "loggia", "veranda", "patio", "porch", "garden")


def architrave_faces(centre, wall: dict, rooms: list[dict]) -> tuple:
    """The y sides of a door's opening frame (+1: the left of the wall direction) where an indoor room lies (pure;
    29 Oct 2026, UL89): the parametric door's architrave goes on those faces; both when neither side finds a room."""
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + DEFAULTS["face_probe"]
    out = []
    for side in (1.0, -1.0):
        probe = (centre[0] + side * nx * reach, centre[1] + side * ny * reach)
        room = next((r for r in rooms if len(r.get("polygon") or []) >= 3 and G.point_in_polygon(probe, r["polygon"])),
                    None)
        if room is not None and str(room.get("room_type") or "").lower() not in ARCHITRAVE_OUTSIDE_TYPES:
            out.append(side)
    return tuple(out) or (1.0, -1.0)


# --------------------------------------------------------------------------
# Milestone 6 design details and wall splits (pure Python)
# --------------------------------------------------------------------------

def wall_split_positions(wall: dict, rooms: list[dict], reach_extra: float = SPLIT_REACH_EXTRA,
                         end_margin: float = SPLIT_END_MARGIN) -> list[float]:
    """Distances along the wall (from ``wall["start"]``, metres, sorted, 0.1 mm
    rounded) of the room corners that lie along it: within ``thickness / 2 +
    reach_extra`` of the centre line and more than ``end_margin`` inside its
    ends. The wall mesh is cut across at each (docs/milestone6.md §5 row 3)."""
    a, b = wall["start"], wall["end"]
    length = G.distance(a, b)
    if length < 1e-6:
        return []
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    reach = float(wall["thickness"]) / 2.0 + reach_extra
    cuts = set()
    for room in rooms:
        for p in room["polygon"]:
            along = (p[0] - a[0]) * ux + (p[1] - a[1]) * uy
            across = abs((p[0] - a[0]) * -uy + (p[1] - a[1]) * ux)
            if end_margin < along < length - end_margin and across <= reach:
                cuts.add(round(along, 4))
    return sorted(cuts)


PAIR_HANDLE_X = 0.08              # a pair's levers this far either side of the middle (29 Oct 2026)


def door_handle_parts(width: float, height: float, sill: float = 0.0,
                      leaf_thickness: float = DEFAULTS["leaf_thickness"],
                      frame_width: float = DEFAULTS["frame_width"], pair: bool = False) -> list[tuple[list, list]]:
    """Boxes of a pair of lever handles in the opening's local frame (X along
    the wall, Y across, Z up from the opening bottom; ``geom2d.box`` tuples):
    on both leaf faces a rose plate, a neck and a 13 cm lever whose axis is
    ``HANDLE_HEIGHT`` above the floor (``sill`` = opening bottom above the
    floor), ``HANDLE_EDGE_INSET`` from the latch-side (+X) edge of the leaf.
    The lever's far side stands ``HANDLE_DEPTH`` proud of the leaf face. A
    door lower than 1.3 m gets its handles at half height."""
    lt = float(leaf_thickness)
    hx = width / 2.0 - frame_width - HANDLE_EDGE_INSET
    lever_z = HANDLE_HEIGHT - float(sill) if height >= 1.3 else height / 2.0
    parts = []
    # 29 Oct 2026: a pair of leaves (``opening_models`` ``pair``) has a lever pair on each leaf at the meeting stiles,
    # each lever pointing to its own hinge side
    spots = [(hx, -1.0)] if not pair else [(-PAIR_HANDLE_X, -1.0), (PAIR_HANDLE_X, 1.0)]
    for x, point in spots:
        for sgn in (1.0, -1.0):
            parts.append(geom2d.box((x, sgn * (lt / 2.0 + 0.004), lever_z - 0.04), (0.05, 0.008, 0.16)))   # rose
            parts.append(geom2d.box((x, sgn * (lt / 2.0 + 0.026), lever_z), (0.018, 0.044, 0.018)))        # neck
            parts.append(geom2d.box((x + point * 0.055, sgn * (lt / 2.0 + HANDLE_DEPTH - 0.009), lever_z),
                                    (0.13, 0.018, 0.018)))                                                # lever
    return parts


# The roles of ``parametric.door_parts`` that go into a Milestone 10 door's ``<id>_frame`` object (``build_door_m10``);
# fix round after P3: the door stops too.
FRAME_ROLES: tuple[str, ...] = ("frame", "rail", "stop", "architrave", "plinth", "moulding")   # + the architrave
# (29 Oct 2026), its plinth blocks and fillet (30 Oct 2026, UL179)
# The Milestone 6 leaf is this much smaller than the frame opening on every side (5 mm per side).
M6_LEAF_CLEARANCE = 0.01


def door_m6_parts(width: float, height: float, thickness: float, swing_side: float = -1.0,
                  frame_width: float = DEFAULTS["frame_width"],
                  leaf_thickness: float = DEFAULTS["leaf_thickness"]) -> dict[str, list[tuple[list, list]]]:
    """The boxes of a Milestone 6 door in the opening's local frame (pure; ``geom2d.box`` tuples; X along the wall,
    Y across, Z up from the opening bottom): ``{"frame": jambs and head as deep as the wall, then the stops, "leaf":
    the closed leaf, "stops": the stops alone}``.

    What (fix round after P3, 16-17 Oct 2026): the jamb and head stops of ``parametric.door_stop_boxes`` on the leaf
    face away from ``swing_side`` (+1 / -1: the y side of the room the door opens into, ``opening_room_side``), so on
    ``-swing_side``; no threshold stop (light under a door is real; a camera at 1.25 m cannot see through 5 mm).
    Why: the leaf is ``M6_LEAF_CLEARANCE`` smaller than the frame opening, so a 5 mm slit ran straight through the
    wall round every closed door; pod P3's cam_r_L1_koridor_2_2 saw the sunlit terrace through it (depth 196 m, a
    glowing line round the leaf).
    How: the frame and leaf boxes are the Milestone 6 ones, unchanged (they moved here from ``build_openings`` so the
    CPU tests guard this path); the stops go into the frame object (its material and pass index)."""
    fw = float(frame_width)
    lt = float(leaf_thickness)
    w, h, t = float(width), float(height), float(thickness)
    frame = [
        geom2d.box((-(w / 2.0 - fw / 2.0), 0.0, h / 2.0), (fw, t, h)),
        geom2d.box((w / 2.0 - fw / 2.0, 0.0, h / 2.0), (fw, t, h)),
        geom2d.box((0.0, 0.0, h - fw / 2.0), (w - 2 * fw, t, fw)),
    ]
    stops = [geom2d.box((cx, cy, z0 + bh / 2.0), (bw, bd, bh))
             for cx, cy, z0, bw, bd, bh in P.door_stop_boxes(w, h, fw, lt / 2.0, t, -float(swing_side))]
    # Leaf: closed (0 deg), slightly smaller than the frame opening.
    leaf = [geom2d.box((0.0, 0.0, (h - fw) / 2.0), (w - 2 * fw - M6_LEAF_CLEARANCE, lt, h - fw - M6_LEAF_CLEARANCE))]
    return {"frame": frame + stops, "leaf": leaf, "stops": stops}


def skirting_spans(polygon, gaps, min_span: float = SKIRTING_MIN_SPAN) -> list[tuple[int, float, float]]:
    """Where a skirting board runs along a room polygon: ``[(edge index, s0, s1)]``
    with ``s0 < s1`` in metres from the edge's first corner. ``gaps`` are
    ``(centre, width)`` of the doors and openings of the room; each is cut
    from the edge nearest to its centre (centre projected onto the edge,
    +- width / 2). Spans shorter than ``min_span`` are dropped."""
    poly = [tuple(p[:2]) for p in polygon]
    if len(poly) > 1 and G.distance(poly[0], poly[-1]) < 1e-9:
        poly = poly[:-1]
    n = len(poly)
    cuts: dict[int, list[tuple[float, float]]] = {i: [] for i in range(n)}
    for centre, width in gaps:
        dists = [G.point_segment_distance(centre[:2], poly[i], poly[(i + 1) % n]) for i in range(n)]
        i = min(range(n), key=lambda k: (dists[k], k))
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        if length < 1e-9:
            continue
        along = ((centre[0] - a[0]) * (b[0] - a[0]) + (centre[1] - a[1]) * (b[1] - a[1])) / length
        cuts[i].append((along - float(width) / 2.0, along + float(width) / 2.0))
    spans = []
    for i in range(n):
        length = G.distance(poly[i], poly[(i + 1) % n])
        start = 0.0
        for c0, c1 in sorted(cuts[i]):
            if c0 - start >= min_span:
                spans.append((i, round(start, 6), round(min(c0, length), 6)))
            start = max(start, c1)
        if length - start >= min_span:
            spans.append((i, round(start, 6), round(length, 6)))
    return spans


def skirting_gaps(openings: list[dict], level: dict, levels_above: bool) -> list[tuple[list, float]]:
    """``(centre, width)`` of the openings that interrupt a room's skirting:
    doors, plain openings and windows reaching below the board; a virtual
    separator by its whole ``line`` (no wall there, so no board along it)."""
    floor_z = float(level["elevation"])
    gaps = []
    for o in openings:
        line = o.get("line")
        if is_virtual(o) and isinstance(line, (list, tuple)) and len(line) == 2:
            (ax, ay), (bx, by) = line[0][:2], line[1][:2]
            gaps.append(([(ax + bx) / 2.0, (ay + by) / 2.0], G.distance((ax, ay), (bx, by))))
            continue
        bottom, _top, _ = opening_vertical(o, level, levels_above)
        if o["type"] in ("door", "opening") or bottom - floor_z < SKIRTING_H:
            gaps.append((o["center"], float(o["width"])))
    return gaps


def skirting_reflex_corners(poly) -> set:
    """The indices of a room polygon's outside corners (reflex, seen from the room: the walls turn away from it)."""
    n = len(poly)
    if n < 3:
        return set()
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    sign = 1.0 if area > 0 else -1.0
    out = set()
    for i in range(n):
        p0, p1, p2 = poly[i - 1], poly[i], poly[(i + 1) % n]
        cross = (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p1[1] - p0[1]) * (p2[0] - p1[0])
        if cross * sign < -1e-9:
            out.add(i)
    return out


def skirting_boxes(polygon, spans, floor_z: float, height: float = SKIRTING_H,
                   thickness: float = SKIRTING_T) -> tuple[list, list]:
    """``(verts, faces)`` of the skirting boards of ``spans`` (``skirting_spans``):
    one box per span, ``thickness`` deep into the room from the polygon edge,
    ``height`` tall from ``floor_z``."""
    poly = [tuple(p[:2]) for p in polygon]
    if len(poly) > 1 and G.distance(poly[0], poly[-1]) < 1e-9:
        poly = poly[:-1]
    n = len(poly)
    reflex = skirting_reflex_corners(poly)
    parts = []
    for i, s0, s1 in spans:
        a, b = poly[i], poly[(i + 1) % n]
        length = G.distance(a, b)
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = geom2d.inward_normal(a, b, poly)
        # 28 Oct 2026 (user: "baseboard needs to be all around"): at an outside corner of the room (a wall nib, a
        # pilaster, a wall end) the boards of its two walls each run on by their thickness, so they meet around it
        # instead of leaving a notch
        if s0 <= 1e-6 and i in reflex:
            s0 = -thickness
        if s1 >= length - 1e-6 and (i + 1) % n in reflex:
            s1 = length + thickness
        mid = (s0 + s1) / 2.0
        centre = (a[0] + ux * mid + nx * thickness / 2.0, a[1] + uy * mid + ny * thickness / 2.0,
                  floor_z + height / 2.0)
        parts.append(geom2d.box(centre, (s1 - s0, thickness, height), math.degrees(math.atan2(uy, ux))))
    return geom2d.merge(parts)


# --------------------------------------------------------------------------
# Walls
# --------------------------------------------------------------------------

def trim_wall_overlaps(walls: list[dict]) -> dict[str, dict]:
    """Shorten wall centre lines where two wall rectangles overlap in volume
    (L-corners of exterior walls drawn as two full-length rectangles).

    Coincident faces of overlapping boxes self-shadow and z-fight in Cycles.
    Where an end edge of wall B lies entirely inside wall A's rectangle, B's
    centre line is cut back to the point where it enters A, so the union of
    the two boxes is unchanged while no faces coincide. At an L-corner both
    ends lie inside each other; the wall with the larger id is trimmed.
    Returns ``{wall_id: {"start": [..], "end": [..], "trimmed": [notes]}}``
    for every wall (untouched walls keep their JSON points).
    """
    out = {w["id"]: {"start": list(w["start"]), "end": list(w["end"]), "trimmed": []} for w in walls}
    ordered = sorted(walls, key=lambda w: w["id"])
    for b in ordered:
        for a in ordered:
            if a["id"] == b["id"]:
                continue
            if a["id"] > b["id"] and _end_inside(a, b):
                continue  # the pair is handled when the roles are swapped
            rect_a = G.centerline_to_rectangle(a["start"], a["end"], a["thickness"])
            cur = out[b["id"]]
            for which in ("start", "end"):
                other = "end" if which == "start" else "start"
                p, q = cur[which], cur[other]
                corners = _end_edge(p, q, b["thickness"])
                if not all(_in_rect(c, rect_a) for c in corners):
                    continue
                t = _exit_parameter(p, q, rect_a)
                if t is None or t <= 1e-6 or t >= 0.999:
                    continue
                new_p = G.point_along_segment(p, q, t)
                cut = G.distance(p, new_p)
                cur[which] = [G.snap(new_p[0]), G.snap(new_p[1])]
                cur["trimmed"].append(f"{which} cut back {cut:.3f} m at the overlap with {a['id']} (union unchanged)")
    return out


def _end_inside(a: dict, b: dict) -> bool:
    """True when an end edge of wall A lies inside wall B's rectangle."""
    rect_b = G.centerline_to_rectangle(b["start"], b["end"], b["thickness"])
    for p, q in ((a["start"], a["end"]), (a["end"], a["start"])):
        if all(_in_rect(c, rect_b) for c in _end_edge(p, q, a["thickness"])):
            return True
    return False


def _end_edge(p, q, thickness: float) -> list[tuple[float, float]]:
    nx, ny = G.unit_normal_left(p, q)
    h = thickness / 2.0
    return [(p[0] + nx * h, p[1] + ny * h), (p[0] - nx * h, p[1] - ny * h)]


def _in_rect(point, rect, tol: float = 1e-6) -> bool:
    """Point inside a convex quadrilateral (or on its boundary within tol)."""
    sign = None
    for i in range(4):
        a, b = rect[i], rect[(i + 1) % 4]
        cross = (b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])
        if abs(cross) <= tol:
            continue
        s = cross > 0
        if sign is None:
            sign = s
        elif s != sign:
            return False
    return True


def _exit_parameter(p, q, rect) -> float | None:
    """Parameter t along p->q where the segment leaves the convex rect (p inside)."""
    best = None
    for i in range(4):
        a, b = rect[i], rect[(i + 1) % 4]
        t = _segment_intersection_t(p, q, a, b)
        if t is not None and t > 1e-9 and (best is None or t < best):
            best = t
    return best


def _segment_intersection_t(p, q, a, b) -> float | None:
    dx, dy = q[0] - p[0], q[1] - p[1]
    ex, ey = b[0] - a[0], b[1] - a[1]
    den = dx * ey - dy * ex
    if abs(den) < 1e-12:
        return None
    t = ((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den
    u = ((a[0] - p[0]) * dy - (a[1] - p[1]) * dx) / den
    if -1e-9 <= u <= 1 + 1e-9 and 0 <= t <= 1 + 1e-9:
        return t
    return None


def build_walls(building: dict, level: dict, collection, library, style: dict, manifest_objects: list,
                assumed: list, warnings: list, whole: dict | None = None) -> list:
    """Create the wall objects of a level with their openings cut.

    ``whole`` (Milestone 10, the whole building; None = the M3-M9 walls): ``{"slab_above": slab record or
    None, "roof_cut": {"planes", "top", "parapets"} or None (the level under the roof: ``roof.wall_cut`` and
    ``roof.parapet_cuts``), "looks": ``exterior.resolve_looks(...)``, "outline": the level's outline, "faces":
    {wall id: [drawn facade face with its side "direction"]}, "open_rooms"}``. Walls then run to the next
    floor (the slab above) instead of the ceiling + the assumed 0.30 m slab, walls under the roof are cut by
    its underside (knee walls, gable ends) and under a roof terrace at the parapet top, L-joins are closed
    (``corner_extensions``), the outward faces take the facade look and a drawn facade part (its side, its
    ``z_range``) its own material; end faces on the outline count as outside. The inside looks come from
    track F's functions (``wall_face_material``, ``wet_wall_look``, ``accent_walls``; today the style).

    After the opening booleans every cut wall is checked against the solid it came from (``wall_cut_problems``):
    its manifest entry gets ``after_cuts`` (``openings``, ``faces``, ``z_range`` and any ``problems``), and a wall
    that lost faces or volume outside its cutters is an ERROR in ``warnings`` and raises ``WallLost`` once the
    level's walls are done: the build fails with the wall ids (pod F2, synthetic-07's ``w_L1_006``)."""
    import bpy

    from wenart.blender import common

    level_id = level["id"]
    floor_z = float(level["elevation"])
    has_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
    walls = [w for w in building["walls"] if w["level_id"] == level_id]
    walls_by_id_level = {w["id"]: w for w in walls}
    openings = [o for o in building["openings"] if o["level_id"] == level_id]
    rooms = [r for r in building["rooms"] if r["level_id"] == level_id]

    # No walls.tint since Milestone 5 (§2.2): the flat albedo mode gives the wall colour;
    # build.load_style warns when an old style file still carries one. The looks come from track F's
    # functions (wall_face_material, wet_wall_look, accent_walls, facade_look; today the style slots).
    wall_mat = look_material(library, wall_face_material(style, None))
    ext_mat = look_material(library, facade_look(whole["looks"])) if whole else library.get("plaster_exterior")
    wet_mat = look_material(library, wet_wall_look(style, None))
    slots = [wall_mat, ext_mat, wet_mat]

    def slot_of(look) -> int:
        mat = look_material(library, look)
        if mat not in slots:
            slots.append(mat)
        return slots.index(mat)

    # Rooms whose inside or wet look differs from the level's: [(polygon, inside slot, wet slot)].
    room_slots = []
    for r in rooms:
        if len(r["polygon"]) >= 3:
            inside_slot, wet_slot = slot_of(wall_face_material(style, r)), slot_of(wet_wall_look(style, r))
            if (inside_slot, wet_slot) != (0, 2):
                room_slots.append((r["polygon"], inside_slot, wet_slot))
    rooms_by_id = {r["id"]: r for r in rooms}
    accents: dict[str, list] = {}
    accent_rooms: dict[str, list] = {}      # Milestone 10: the manifest marks accent faces (accent, room_ids)
    for wid, per_room in accent_walls(building, level, style).items():
        for rid, look in (per_room or {}).items():
            if rid in rooms_by_id and len(rooms_by_id[rid]["polygon"]) >= 3:
                accents.setdefault(wid, []).append((rooms_by_id[rid]["polygon"], slot_of(look)))
                accent_rooms.setdefault(wid, []).append((rid, look))
    face_slots: dict[str, list[tuple]] = {}
    if whole:
        # Drawn facade parts (prepared per wall by build.prepare: side direction, optional z band).
        for wid, faces in (whole.get("faces") or {}).items():
            for face in faces:
                slot = slot_of({"material": face["material"], "colour": face.get("colour")})
                zr = face.get("z_range") or [-1e9, 1e9]
                face_slots.setdefault(wid, []).append((float(zr[0]), float(zr[1]), slot, face.get("direction"),
                                                       face.get("span")))
    roof_cut = whole.get("roof_cut") if whole else None
    cut_planes = roof_cut["planes"] if roof_cut else None
    slab_above = whole.get("slab_above") if whole else None
    open_ids = set((whole or {}).get("open_rooms") or ())
    open_polys = [r["polygon"] for r in rooms if r["id"] in open_ids and len(r["polygon"]) >= 3]

    footprint_centre = _level_centre(walls)
    extended = corner_extensions(walls) if whole else {}
    trims = trim_wall_overlaps([dict(w, **extended.get(w["id"], {})) for w in walls])
    objects = []
    pairs = []  # (object, wall) for the face classification after the booleans
    cutters = []
    solids: dict[str, tuple] = {}         # wall id: (verts, faces) handed to the booleans
    wall_cuts: dict[str, list] = {}       # wall id: [(opening id, (verts, faces) of its cutter)]
    entries: dict[str, dict] = {}         # wall id: its manifest entry
    for wall in walls:
        height, wall_assumed = wall_height(wall, level, has_above)
        if slab_above is not None:
            # 31 Oct 2026 (user on real04 run 181158, the attic play room: "Something wrong within cyan outline": the
            # tops of the walls below showed through the attic floor and its rug as a grey band and white lines): a
            # wall stops WALL_UNDER_FLOOR_GAP under the floor above, inside the slab, never in the floor's plane
            height, wall_assumed = float(slab_above["z_top"]) - floor_z - WALL_UNDER_FLOOR_GAP, {}
        start, end = trims[wall["id"]]["start"], trims[wall["id"]]["end"]
        length = G.distance(start, end)
        if length < 1e-6:
            warnings.append(f"{wall['id']}: zero-length wall skipped")
            continue
        mid = G.segment_midpoint(start, end)
        angle = G.segment_angle_deg(start, end)
        parapets = []
        # 27 Oct 2026: under a stepped hip roof each wall is cut by the part of the roof over it (roof.wall_cut's
        # wall_planes), stretch by stretch where the part over it changes along it (wall_spans); under any other roof
        # by the roof's underside
        wall_planes = ((roof_cut.get("wall_planes") or {}).get(wall["id"]) or cut_planes) if roof_cut else None
        part_spans = plane_spans(wall, start, end, (roof_cut.get("wall_spans") or {}).get(wall["id"]) or []) \
            if roof_cut else []
        if cut_planes is not None:
            # Under the roof: a box up past the ridge, cut by the roof underside (knee wall, gable end);
            # under a roof terrace the parapet height instead (roof.parapet_cuts).
            height, wall_assumed = float(roof_cut["top"]) + 0.5 - floor_z, {}
            parapets = trimmed_spans(wall, start, end, (roof_cut.get("parapets") or {}).get(wall["id"]) or [])
        # Milestone 12 (track L): a wall beside a sunken room floor starts at that floor (no gap under the wall).
        drop = wall_base_drop(wall, rooms)
        wz = floor_z + drop
        height -= drop
        if parapets or part_spans:
            verts, faces = wall_pieces(start, end, float(wall["thickness"]), wz, height, wall_planes, parapets,
                                       part_spans)
        else:
            verts, faces = geom2d.box((mid[0], mid[1], wz + height / 2.0),
                                      (length, float(wall["thickness"]), height), angle)
            if cut_planes is not None:
                verts, faces = geom2d.clip_solid_below(verts, faces, wall_planes)
        if not verts:
            # Review #23: the roof underside lies below the floor along the whole wall (eaves at or below the
            # attic floor): nothing of the wall stands; listed, never a crash.
            on_it = [o["id"] for o in openings if o.get("wall_id") == wall["id"]]
            reason = (f"the roof underside lies below the floor of {level_id} along the whole wall (eaves at or "
                      f"below the attic floor): no wall built" + (f"; its openings {', '.join(on_it)} have no wall"
                                                                   if on_it else ""))
            warnings.append(f"{wall['id']}: {reason}")
            assumed.append({"object": wall["id"], "field": "not_built", "value": True, "reason": reason})
            continue
        if cut_planes is not None:
            height = max(v[2] for v in verts) - wz
        ob = common.new_mesh_object(wall["id"], verts, faces, collection=collection, wenart_id=wall["id"],
                                    kind="wall", status=wall.get("status", "verified"), materials=slots)
        objects.append(ob)
        pairs.append((ob, wall))
        solids[wall["id"]] = (verts, faces)

        # Cutters for the openings of this wall (a virtual separator has no wall: never cut).
        spans = []                                       # (a0, a1, z0, z1) of every cut of this wall
        for opening in openings:
            if opening.get("wall_id") != wall["id"]:
                continue
            bottom, top, _ = opening_vertical(opening, level, has_above)
            extra = DEFAULTS["cutter_extra"]
            # Door cutters start a little below the floor so no coplanar faces
            # remain; an opening that reaches the wall top also runs above it.
            cut_bottom = bottom if opening["type"] == "window" else bottom - extra
            cut_top = top + extra if cut_full_height(top, wz, height) else top
            cx, cy, _shift = opening_centre_on_wall(opening, wall)  # shift recorded in build_openings
            a = along_wall(wall, (cx, cy))
            spans.append((a - float(opening["width"]) / 2.0, a + float(opening["width"]) / 2.0, cut_bottom, cut_top))
            cv, cf = geom2d.box((cx, cy, (cut_bottom + cut_top) / 2.0),
                                (float(opening["width"]), float(wall["thickness"]) + extra, cut_top - cut_bottom),
                                angle)
            cutter = common.new_mesh_object(f"cut_{opening['id']}", cv, cf, collection=collection,
                                            wenart_id=opening["id"], kind="opening", status="assumed")
            cutter.hide_render = True
            cutters.append(cutter)
            wall_cuts.setdefault(wall["id"], []).append((opening["id"], (cv, cf)))
            mod = ob.modifiers.new(name=f"cut_{opening['id']}", type="BOOLEAN")
            mod.operation = "DIFFERENCE"
            mod.solver = "EXACT"
            # A wall with parapet stretches is several closed pieces side by side (wall_pieces) whose end faces
            # touch, coincident and opposite: the exact solver reads that only with self-intersection on; without
            # it, it returned synthetic-07's w_L1_006 (parapet, gable and window) as an empty mesh (pod F2). Every
            # other wall is one closed solid and keeps the default.
            mod.use_self = bool(parapets or part_spans)
            mod.object = cutter

        # Openings of another wall that this one overlaps (a facade line drawn over a thick wall): cut through
        # both, else the opening stays closed (pod P5, foreign_cuts).
        # The widest first; one that an earlier cut of this wall already covers adds no cutter (span_covered).
        cut_through, covered = [], []
        foreign = sorted(foreign_cuts(wall, walls_by_id_level, openings), key=lambda c: -float(c[0]["width"]))
        for opening, (fx, fy), depth in foreign:
            host = walls_by_id_level[opening["wall_id"]]
            bottom, top, _ = opening_vertical(opening, level, has_above)
            extra = DEFAULTS["cutter_extra"]
            cut_bottom = bottom if opening["type"] == "window" else bottom - extra
            cut_top = top + extra if cut_full_height(top, wz, height) else top
            a = along_wall(wall, (fx, fy))
            span = (a - float(opening["width"]) / 2.0, a + float(opening["width"]) / 2.0, cut_bottom, cut_top)
            if span_covered(span, spans):
                covered.append(opening["id"])
                continue
            spans.append(span)
            h_angle = math.atan2(float(host["end"][1]) - float(host["start"][1]),
                                 float(host["end"][0]) - float(host["start"][0]))
            cv, cf = geom2d.box((fx, fy, (cut_bottom + cut_top) / 2.0),
                                (float(opening["width"]), depth + extra, cut_top - cut_bottom), h_angle)
            cutter = common.new_mesh_object(f"cut_{opening['id']}_{wall['id']}", cv, cf, collection=collection,
                                            wenart_id=opening["id"], kind="opening", status="assumed")
            cutter.hide_render = True
            cutters.append(cutter)
            wall_cuts.setdefault(wall["id"], []).append((opening["id"], (cv, cf)))
            mod = ob.modifiers.new(name=f"cut_{opening['id']}", type="BOOLEAN")
            mod.operation = "DIFFERENCE"
            mod.solver = "EXACT"
            mod.use_self = bool(parapets or part_spans)
            mod.object = cutter
            cut_through.append(opening["id"])
            warnings.append(f"{wall['id']}: overlaps {host['id']} at {opening['id']}: the opening is cut through "
                            "both walls")
            assumed.append({"object": wall["id"], "field": "cut_through", "value": opening["id"],
                            "reason": f"the wall overlaps {host['id']} at its opening {opening['id']}: cut through "
                                      "both (a facade line drawn over a thicker wall)"})

        manifest_objects.append({
            "name": wall["id"], "wenart_id": wall["id"], "kind": "wall",
            "status": wall.get("status", "verified"), "level_id": level_id, "element_id": wall["id"],
            "evidence": wall.get("evidence", []), "material": wall_mat.name,
            "textured": library.textured(wall_mat),
            "pass_index": None, "assumed": wall_assumed,
            "trimmed": trims[wall["id"]]["trimmed"],
            "start": trims[wall["id"]]["start"], "end": trims[wall["id"]]["end"],
            "thickness": wall["thickness"], "height": height,
        })
        entry = entries[wall["id"]] = manifest_objects[-1]
        if wall["id"] in accent_rooms:
            # The gate (wenart/gate/colour.py) finds a room's accent wall by these keys (track H).
            marked = accent_rooms[wall["id"]]
            entry.update(accent=True, room_ids=sorted(rid for rid, _look in marked),
                         accent_material=slots[accents[wall["id"]][0][1]].name,
                         accent_reason="; ".join(str(look.get("reason") or "") for _rid, look in marked))
        if wall["id"] in extended:
            entry["corner_join"] = {k: [round(c, 4) for c in v] for k, v in extended[wall["id"]].items()}
        if slab_above is not None:
            entry["runs_to"] = f"the next floor (slab {slab_above['id']} top {float(slab_above['z_top']):.3f} m)"
        if cut_planes is not None:
            entry["runs_to"] = "the roof underside (knee wall / gable end)"
            entry["z_range"] = [round(wz, 4), round(wz + height, 4)]
        if drop < 0:
            entry["base_drop"] = round(drop, 4)          # Milestone 12: down to a sunken room floor beside it
        if cut_through:
            entry["cut_through"] = cut_through           # openings of an overlapped wall (foreign_cuts)
        if covered:
            entry["cut_through_covered"] = covered       # ... whose span an earlier cut of this wall already opened
        if parapets:
            entry["parapet"] = [{"s": [round(a, 4), round(b, 4)], "z_top": round(z, 4)} for a, b, z in parapets]
            entry["runs_to"] += "; a parapet under the roof terrace"
        for field, value in wall_assumed.items():
            assumed.append({"object": wall["id"], "field": field, "value": value,
                            "reason": "wall height from the level ceiling height" if field == "height"
                            else "slab between levels"})

    # Apply the booleans through the depsgraph, split at the room corners and classify faces.
    bpy.context.view_layer.update()
    lost = []
    for ob, wall in pairs:
        changed = False
        if ob.modifiers:
            mesh = common.evaluated_mesh(ob)
            # Pod F2: the exact solver returned a wall empty without a word. The cuts may only remove what lies
            # inside their cutters; a wall that lost more stops the build (CLAUDE.md: nothing removed silently).
            mw = ob.matrix_world
            after = ([tuple(mw @ v.co) for v in mesh.vertices], [list(p.vertices) for p in mesh.polygons])
            own = wall_cuts.get(wall["id"]) or []
            problems = wall_cut_problems(solids[wall["id"]], after, [c for _oid, c in own])
            zs = [v[2] for v in after[0]]
            record = {"openings": [oid for oid, _c in own], "faces": len(after[1]),
                      "z_range": [round(min(zs), 4), round(max(zs), 4)] if zs else None}
            if problems:
                record["problems"] = problems
                lost.append(f"{wall['id']} ({'; '.join(problems)})")
                warnings.append(f"{wall['id']}: ERROR the opening cuts ({', '.join(record['openings'])}) lost part of "
                                f"the wall: {'; '.join(problems)}")
            if wall["id"] in entries:
                entries[wall["id"]]["after_cuts"] = record
            common.replace_mesh(ob, mesh)
            # The boolean appends the cutter's (empty) material slot; drop it.
            while len(mesh.materials) > len(slots) or any(m is None for m in mesh.materials):
                idx = next((i for i, m in enumerate(mesh.materials) if m is None), len(mesh.materials) - 1)
                mesh.materials.pop(index=idx)
            changed = True
        cuts = split_wall_at_room_corners(ob, wall, rooms)
        if cuts:
            changed = True
            for entry in manifest_objects:
                if entry.get("kind") == "wall" and entry.get("wenart_id") == wall["id"]:
                    entry["split_at_m"] = cuts
        if face_slots.get(wall["id"]):
            changed = split_wall_at_heights(ob, sorted({z for z0, z1, *_ in face_slots[wall["id"]]
                                                         for z in (z0, z1) if abs(z) < 1e8})) or changed
            spans = [part[4] for part in face_slots[wall["id"]] if len(part) > 4 and part[4]]
            if spans:
                changed = split_wall_at_points(ob, wall["start"], wall["end"], [p for sp in spans for p in sp]) \
                    or changed
        if changed:
            common.assign_box_uvs(ob.data)
        outward, ambiguous = wall_outward_normal(wall, rooms, footprint_centre)
        if ambiguous and wall.get("exterior"):
            warnings.append(f"{wall['id']}: exterior wall with rooms on both sides or on neither; "
                            f"outward side taken from the level centre")
        _assign_wall_face_materials(ob, wall, rooms, outward, outline=whole.get("outline") if whole else None,
                                    face_slots=face_slots.get(wall["id"]), open_polys=open_polys,
                                    room_slots=room_slots, accents=accents.get(wall["id"]))
    for cutter in cutters:
        common.delete_object(cutter)
    bpy.context.view_layer.update()
    if lost:
        raise WallLost(f"level {level_id}: the opening booleans lost walls (no render may show them missing): "
                       + "; ".join(lost))
    return objects


def mesh_volume(verts, faces) -> float:
    """Signed volume (m³) of a closed mesh with outward faces (pure): the divergence theorem over a triangle fan
    of each face. Closed pieces that only touch (``wall_pieces``) add up."""
    total = 0.0
    for face in faces:
        a = verts[face[0]]
        for i in range(1, len(face) - 1):
            b, c = verts[face[i]], verts[face[i + 1]]
            total += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                      + a[2] * (b[0] * c[1] - b[1] * c[0]))
    return total / 6.0


def _extent(verts) -> list[tuple[float, float]]:
    return [(min(float(v[k]) for v in verts), max(float(v[k]) for v in verts)) for k in range(3)]


def wall_cut_problems(before, after, cutters, tol_m: float = WALL_CUT_TOL_M,
                      tol_m3: float = WALL_CUT_TOL_M3) -> list[str]:
    """What a wall lost to its opening booleans outside the cutters (pure; ``[]``: nothing).

    ``before``: the ``(verts, faces)`` handed to the booleans, ``after``: the evaluated mesh, ``cutters``: the
    ``(verts, faces)`` of each cutter (world metres, closed solids with outward faces). A boolean DIFFERENCE removes
    only what lies inside its cutters, so the wall was lost (pod F2: the exact solver returned synthetic-07's
    ``w_L1_006``, parapet and gable, as an empty mesh without a word) when it has no faces left, when it lost more
    volume than its cutters hold or gained volume, or when its x, y or z extent shrank on a side no cutter
    reaches (a lost end piece: a parapet stretch, a gable). A wall wholly inside its cutters may go."""
    if not before[0] or not before[1]:
        return []
    held = sum(abs(mesh_volume(*c)) for c in cutters if c[0])
    reach = [_extent(c[0]) for c in cutters if c[0]]
    vb = mesh_volume(*before)
    eb = _extent(before[0])
    empty = not after[0] or not after[1]
    va = 0.0 if empty else mesh_volume(*after)
    problems = []
    if vb - va > held + tol_m3:
        problems.append(f"lost {vb - va:.4f} m³ of {vb:.4f} m³, more than its cutters hold ({held:.4f} m³)")
    elif va - vb > tol_m3:
        problems.append(f"gained {va - vb:.4f} m³ ({vb:.4f} -> {va:.4f} m³)")
    for k, axis in enumerate("xyz"):
        (b0, b1) = eb[k]
        (a0, a1) = (b1, b0) if empty else _extent(after[0])[k]
        if a0 < b0 - tol_m or a1 > b1 + tol_m:
            problems.append(f"its {axis} extent grew from [{b0:.3f}, {b1:.3f}] to [{a0:.3f}, {a1:.3f}]")
            continue
        low = a0 > b0 + tol_m and not any(e[k][0] <= b0 + tol_m for e in reach)
        high = a1 < b1 - tol_m and not any(e[k][1] >= b1 - tol_m for e in reach)
        if low or high:
            problems.append(f"its {axis} extent shrank from [{b0:.3f}, {b1:.3f}] to "
                            + ("nothing" if empty else f"[{a0:.3f}, {a1:.3f}]") + " where no cutter reaches")
    if empty and problems:
        problems.insert(0, f"no faces left after the cuts (had {len(before[1])})")
    return problems


def trimmed_spans(wall: dict, start, end, cuts: list[dict]) -> list[tuple[float, float, float]]:
    """``[(s0, s1, z_top)]``: parapet stretches (``roof.parapet_cuts``, parameters along the drawn centre line)
    in metres along the built (trimmed or corner-joined) centre line ``start``-``end`` (pure)."""
    length = G.distance(start, end)
    if length < 1e-9:
        return []
    ux, uy = (end[0] - start[0]) / length, (end[1] - start[1]) / length
    out = []
    for c in cuts:
        pts = [G.point_along_segment(wall["start"], wall["end"], float(c[k])) for k in ("t0", "t1")]
        s = sorted((p[0] - start[0]) * ux + (p[1] - start[1]) * uy for p in pts)
        # a stretch that reaches a drawn wall end runs to the built end (the joined corner)
        s0 = 0.0 if float(c["t0"]) <= 1e-6 or s[0] <= 1e-6 else min(max(s[0], 0.0), length)
        s1 = length if float(c["t1"]) >= 1 - 1e-6 or s[1] >= length - 1e-6 else min(max(s[1], 0.0), length)
        if s1 - s0 > 1e-4:
            out.append((s0, s1, float(c["z_top"])))
    return sorted(out)


def plane_spans(wall: dict, start, end, spans: list[dict]) -> list[tuple[float, float, list]]:
    """``[(s0, s1, planes)]``: a wall's stretches under the parts of a stepped hip roof (``roof.wall_cut``'s
    ``wall_spans``: parameters along the drawn centre line) in metres along the built centre line (pure; the
    mapping of ``trimmed_spans``)."""
    if not spans:
        return []
    marked = [dict(s, z_top=float(i)) for i, s in enumerate(spans)]
    return [(s0, s1, spans[int(round(i))]["planes"]) for s0, s1, i in trimmed_spans(wall, start, end, marked)]


def wall_pieces(start, end, thickness: float, floor_z: float, height: float, planes, parapets,
                part_spans=()) -> tuple[list, list]:
    """``(verts, faces)`` of a wall under the roof with parapet stretches (pure): convex boxes along the
    centre line, each cut by the roof underside ``planes`` or, under a terrace, at its parapet top (never lowered
    by the roof planes: no roof is over a parapet). The pieces stand side by side in one mesh and touch: the end
    faces at each mark lie on each other, coincident and opposite, so the mesh is not one closed manifold and any
    boolean on it needs ``use_self`` (``build_walls``; without it the exact solver returned synthetic-07's
    ``w_L1_006`` empty, pod F2). 27 Oct 2026: ``part_spans`` (``plane_spans``) cut each stretch under a stepped hip
    roof by the planes of the part over it."""
    length = G.distance(start, end)
    angle = G.segment_angle_deg(start, end)
    marks = sorted({0.0, length} | {s for a, b, _ in parapets for s in (a, b)}
                   | {s for a, b, _ in part_spans for s in (a, b) if 0.0 < s < length})
    parts = []
    for s0, s1 in zip(marks, marks[1:]):
        if s1 - s0 < 1e-6:
            continue
        sm = (s0 + s1) / 2.0
        top = next((z for a, b, z in parapets if a - 1e-9 <= sm <= b + 1e-9), None)
        own = next((p for a, b, p in part_spans if a - 1e-9 <= sm <= b + 1e-9), planes)
        c = G.point_along_segment(start, end, sm / length)
        verts, faces = geom2d.box((c[0], c[1], floor_z + height / 2.0), (s1 - s0, thickness, height), angle)
        cut = [(0.0, 0.0, top)] if top is not None else own
        parts.append(geom2d.clip_solid_below(verts, faces, cut))
    return geom2d.merge(parts)


def split_wall_at_room_corners(ob, wall: dict, rooms: list[dict]) -> list[float]:
    """Cut the wall mesh with a vertical plane across the wall at every
    ``wall_split_positions`` distance (``bmesh.ops.bisect_plane``, nothing
    removed), so each face lies along one room and takes that room's material.
    Returns the distances cut (empty when none)."""
    import bmesh
    from mathutils import Vector

    cuts = wall_split_positions(wall, rooms)
    if not cuts:
        return []
    a, b = wall["start"], wall["end"]
    length = G.distance(a, b)
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for along in cuts:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=Vector((a[0] + ux * along, a[1] + uy * along, 0.0)),
                               plane_no=Vector((ux, uy, 0.0)))
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return cuts


def _level_centre(walls: list[dict]) -> tuple[float, float]:
    pts = [w["start"] for w in walls] + [w["end"] for w in walls]
    if not pts:
        return (0.0, 0.0)
    box = G.bbox(pts)
    return G.box_center(box)


def wall_face_slot(wall: dict, centre, normal, outward, indoor_polys, wet_polys,
                   probe: float = DEFAULTS["face_probe"]) -> int:
    """Material slot of one wall face (pure): 0 interior, 1 exterior, 2 wet room.

    ``centre`` / ``normal``: the face centre (x, y[, z]) and its unit normal
    (x, y, z). Top, bottom, jamb and end faces are 0. A side face is probed
    ``probe`` metres beyond its centre: the exterior slot needs an exterior
    wall, a normal along ``outward`` AND a probe in no indoor room polygon
    (``indoor_polys``: the level's rooms without balconies, which are
    outside). The ingest flags a merged axis run exterior when part of it
    touches the outer loop (review ingest-3: real01's ``w_L0_011`` runs from
    the parking past the pooja and kitchen), so ``exterior`` alone does not
    say what one face looks into; the faces are split at the room corners
    first (``split_wall_at_room_corners``), so this decides per room stretch.
    A face looking into a wet room (``wet_polys``) is 2, any other 0."""
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    fx, fy, fz = float(normal[0]), float(normal[1]), float(normal[2])
    if abs(fz) > 0.5 or abs(fx * nx + fy * ny) < 0.5:
        return 0  # top, bottom, jambs, end faces
    p = (float(centre[0]) + fx * probe, float(centre[1]) + fy * probe)
    if wall.get("exterior") and (fx * outward[0] + fy * outward[1]) > 0.5 \
            and not any(G.point_in_polygon(p, poly) for poly in indoor_polys):
        return 1
    return 2 if any(G.point_in_polygon(p, poly) for poly in wet_polys) else 0


# Rooms that are outside: an exterior face looking into one keeps the exterior material.
OUTDOOR_ROOM_TYPES = {"balcony"}
# 30 Oct 2026 (UL159): rooms whose floor is the outdoor floor (``build.prepare``'s ``terrace_floor``) when it is given
OUTDOOR_FLOOR_ROOMS = ("balcony", "terrace", "loggia", "veranda", "porch", "deck", "patio")


def _assign_wall_face_materials(ob, wall: dict, rooms: list[dict], outward, outline=None, face_slots=None,
                                open_polys=(), room_slots=(), accents=None) -> None:
    """Slot 0 interior, 1 exterior (faces of exterior walls whose normal
    points ``outward``, see ``wall_outward_normal``, and that look into no
    indoor room), 2 wet-room faces: ``wall_face_slot`` per face.

    Milestone 10 (``outline``: the building outline): a vertical face whose probe lies outside the outline
    is outside too (the end faces of a closed L-join at the building corner), and so is one looking into a
    room open to the sky (``open_polys``: roof terraces); ``face_slots``: drawn facade parts ``[(z0, z1,
    slot, direction)]`` replace the exterior slot of the faces whose centre lies in their z range and whose
    normal lies within 45 degrees of the part's side (``direction``; None = every side). The looks of track F
    (``room_slots``: ``[(room polygon, inside slot, wet slot)]``; ``accents``: ``[(room polygon, slot)]`` of this
    wall) replace slots 0 and 2 of the faces looking into those rooms."""
    mesh = ob.data
    polys = [r for r in rooms if len(r["polygon"]) >= 3]
    indoor = [r["polygon"] for r in polys if r.get("room_type") not in OUTDOOR_ROOM_TYPES]
    wet_polys = [r["polygon"] for r in polys if slot_room_type(r.get("room_type")) in WET_WALL_ROOM_TYPES]
    probe = DEFAULTS["face_probe"]
    for poly in mesh.polygons:
        c = poly.center  # wall meshes are built in world coordinates (identity transform)
        normal = tuple(poly.normal)
        slot = wall_face_slot(wall, (c.x, c.y), normal, outward, indoor, wet_polys)
        if outline and slot == 0 and (outside_face(c, normal, outline) or open_face(c, normal, open_polys)):
            slot = 1
        if slot in (0, 2) and (room_slots or accents) and abs(normal[2]) <= 0.5:
            p = (c.x + normal[0] * probe, c.y + normal[1] * probe)
            accent = next((s for pg, s in accents or () if slot == 0 and G.point_in_polygon(p, pg)), None)
            if accent is not None:
                slot = accent
            else:
                slot = next((i if slot == 0 else w for pg, i, w in room_slots if G.point_in_polygon(p, pg)), slot)
        if face_slots and slot == 1:
            slot = facade_face_slot(c.z, face_slots, slot, normal, centre=(c.x, c.y))
        poly.material_index = slot


def outside_face(centre, normal, outline, probe: float = DEFAULTS["face_probe"]) -> bool:
    """A vertical face whose probe point (``probe`` beyond its centre along the normal) lies outside the
    building outline (pure; Milestone 10)."""
    if abs(float(normal[2])) > 0.5:
        return False
    p = (float(centre[0]) + float(normal[0]) * probe, float(centre[1]) + float(normal[1]) * probe)
    return not G.point_in_polygon(p, outline) and geom2d.distance_to_polygon_edges(p, outline) > 1e-6


def open_face(centre, normal, open_polys, probe: float = DEFAULTS["face_probe"]) -> bool:
    """A vertical face looking into a room open to the sky (a roof terrace; pure, Milestone 10)."""
    if not open_polys or abs(float(normal[2])) > 0.5:
        return False
    p = (float(centre[0]) + float(normal[0]) * probe, float(centre[1]) + float(normal[1]) * probe)
    return any(G.point_in_polygon(p, poly) for poly in open_polys)


def facade_face_slot(z: float, face_slots, default: int, normal=None, centre=None) -> int:
    """The slot of a drawn facade part (``[(z0, z1, slot[, direction[, span]]])]``) whose z range holds ``z`` and, when
    the part has a side ``direction`` (a unit vector in the building frame) and ``normal`` is given, whose
    side the face normal lies within 45 degrees of, and, when it has a ``span`` (two plan points on the wall) and
    ``centre`` is given, onto whose span the face centre projects; else ``default``."""
    from wenart.blender.facade import on_span

    for part in face_slots:
        z0, z1, slot = part[0], part[1], part[2]
        direction = part[3] if len(part) > 3 else None
        span = part[4] if len(part) > 4 else None
        if not z0 - 1e-6 <= float(z) <= z1 + 1e-6:
            continue
        if span and centre is not None and not on_span(centre, span):
            continue
        if direction is not None and normal is not None:
            if float(normal[0]) * direction[0] + float(normal[1]) * direction[1] < math.cos(math.radians(45.0)) - 1e-9:
                continue
        return slot
    return default


def split_wall_at_points(ob, start, end, points) -> bool:
    """Cut a wall mesh with vertical planes across the wall at the plan ``points`` (the ends of facade parts with a
    ``span``) so each face lies on one side of them. True when it cut."""
    import bmesh
    from mathutils import Vector

    (x0, y0), (x1, y1) = start[:2], end[:2]
    length = math.hypot(x1 - x0, y1 - y0)
    if length <= 1e-9 or not points:
        return False
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    ts = [(v.co.x - x0) * ux + (v.co.y - y0) * uy for v in ob.data.vertices]
    cuts = []
    for p in points:
        t = (float(p[0]) - x0) * ux + (float(p[1]) - y0) * uy
        if ts and min(ts) + 1e-4 < t < max(ts) - 1e-4 and all(abs(t - c) > 1e-4 for c in cuts):
            cuts.append(t)
    if not cuts:
        return False
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for t in cuts:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=Vector((x0 + ux * t, y0 + uy * t, 0.0)),
                               plane_no=Vector((ux, uy, 0.0)))
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return True


def split_wall_at_heights(ob, heights: list[float]) -> bool:
    """Cut a wall mesh with horizontal planes at ``heights`` (the edges of drawn facade parts) so each face
    lies in one part. True when it cut."""
    import bmesh
    from mathutils import Vector

    zs = [v.co.z for v in ob.data.vertices]
    cuts = [z for z in heights if zs and min(zs) + 1e-6 < z < max(zs) - 1e-6]
    if not cuts:
        return False
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    for z in cuts:
        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)
        bmesh.ops.bisect_plane(bm, geom=geom, plane_co=Vector((0.0, 0.0, z)), plane_no=Vector((0.0, 0.0, 1.0)))
    bm.to_mesh(ob.data)
    bm.free()
    ob.data.update()
    return True


# --------------------------------------------------------------------------
# Doors and windows
# --------------------------------------------------------------------------

def build_openings(building: dict, level: dict, collection, library, style: dict, pass_indices: dict,
                   manifest_objects: list, assumed: list, warnings: list, library_openings: dict | None = None,
                   assets_dir: str | None = None, geo_cache: dict | None = None) -> list:
    """Door frame + leaf and window frame + glass per opening (plain openings
    are only the hole in the wall and get no object). 24 Oct 2026: an outer opening in ``library_openings``
    (``opening_models.plan``) is the library model (``opening_build``), the parametric one when it cannot load.
    28 Oct 2026: an inside door in it too (``opening_models.plan_inside``), its leaf in the role's door look."""
    from wenart.blender import common

    level_id = level["id"]
    floor_z = float(level["elevation"])
    has_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
    has_below = any(float(lv["elevation"]) < floor_z for lv in building["levels"])
    walls = {w["id"]: w for w in building["walls"] if w["level_id"] == level_id}
    rooms = [r for r in building["rooms"] if r["level_id"] == level_id]
    trim = style.get("trim") or {"material": "painted_wood_white"}
    frame_mat = slot_material(library, trim)
    glass_mat = library.glass()
    steel_mat = library.get("steel_brushed")

    created = []
    for opening in building["openings"]:
        if opening["level_id"] != level_id:
            continue
        if is_virtual(opening):
            # A separator line between two rooms where no wall exists: no geometry at all.
            manifest_objects.append(separator_entry(opening, level_id))
            continue
        wall = walls.get(opening.get("wall_id"))
        if wall is None:
            warnings.append(f"{opening['id']}: wall {opening.get('wall_id')} not found on {level_id}; "
                            f"opening not built")
            continue
        bottom, top, op_assumed = opening_vertical(opening, level, has_above)
        listed = opening.get("assumed") or ()
        for field, value in op_assumed.items():
            assumed.append({"object": opening["id"], "field": field, "value": value,
                            "reason": f"{opening['type']} {field} listed as assumed in the building JSON"
                            if field in listed else f"{opening['type']} {field} not in the JSON; default"})
        angle = G.segment_angle_deg(wall["start"], wall["end"])
        width = float(opening["width"])
        thickness = float(wall["thickness"])
        status = opening.get("status", "verified")
        # The centre is used on the wall centre line; an off-centre JSON centre
        # (block on the wall face) is recorded, never silently moved.
        cx, cy, shift = opening_centre_on_wall(opening, wall)
        if shift > DEFAULTS["shift_assumed"]:
            op_assumed["center_shift"] = round(shift, 4)
            assumed.append({"object": opening["id"], "field": "center_shift", "value": round(shift, 4),
                            "reason": f"opening centre {shift * 1000:.0f} mm off the centre line of "
                                      f"{wall['id']}; projected onto it"})
            if shift > thickness / 2.0:
                warnings.append(f"{opening['id']}: centre {shift:.3f} m off the centre line of {wall['id']}, "
                                f"more than half its thickness ({thickness:.3f} m); projected onto the wall")

        if opening["type"] in ("door", "opening"):
            # Threshold: the room floors stop at the wall faces and the cutter
            # removes the wall bottom, so the footprint needs its own floor face.
            created.append(_threshold(opening, wall, (cx, cy), angle, floor_z, has_below, rooms, style, library,
                                      collection, manifest_objects, warnings, op_assumed, shift))
        hatch = opening["type"] == "window" and (opening.get("interior_glazing") or {}).get("kind") == "pass_through"
        if hatch:
            # 27 Oct 2026 (user: "Not every opening inside the house requires a door or a window"): a serving hatch
            # over a drawn counter (door_spacing.open_hatch) is open above the counter: no glass, no frame
            op_assumed["open_hatch"] = "a serving hatch over the drawn counter: open, no glass or frame"
        if opening["type"] == "opening" or hatch:
            wall_h, _ = wall_height(wall, level, has_above)
            full = cut_full_height(top, floor_z, wall_h)
            if full:
                # Nothing above the wall: close the wall top over the opening.
                created.append(_soffit(opening, wall, (cx, cy), angle, floor_z + wall_h, style, library,
                                       collection, manifest_objects, op_assumed, shift))
            manifest_objects.append(_opening_entry(opening, None, level_id, None, False, None, op_assumed, shift))
            if not hatch and door_product(style) and float(opening.get("sill_height") or 0.0) <= PASSAGE_SILL_M:
                # 29 Oct 2026 (UL122): an open passage gets a lined reveal (jambs and head lining), no architrave
                created.append(_passage_lining(opening, (cx, cy), width, top - bottom, thickness, angle, bottom,
                                               not full, frame_mat, collection, manifest_objects, assumed, level_id,
                                               shift))
            continue
        fw = DEFAULTS["frame_width"]
        height = top - bottom
        index = len(pass_indices) + 1
        pass_indices[opening["id"]] = index
        # The door leaf and window frame looks (looks.door_look / window_frame_look: the style slots, the door
        # style decided by the drawn operation first).
        # 28 Oct 2026: the rooms a door joins pick an inside door's role look (looks.role_door_style)
        dlook = door_look(style, dict(opening, joins=door_sides((cx, cy), wall, rooms))) \
            if opening["type"] == "door" else None
        if dlook is not None and opening.get("outside_door") and dlook.get("door_style") in ("flush", "shaker_panel"):
            # 25 Oct 2026 (architect A3): a door to a terrace or balcony is glazed, never the inside's flush leaf
            dlook = dict(dlook, door_style="glazed",
                         reason=dlook.get("reason", "") + "; glazed: " + opening["outside_door"]["reason"])
        wlook = window_frame_look(style, opening) if opening["type"] != "door" else None
        if dlook is not None and opening.get("outside_door") and dlook.get("door_style") == "glazed":
            # 25 Oct 2026 (user: "is the door to the terrace ok?"): a glazed terrace door is joinery of the facade:
            # its frame takes the windows' frame finish, not the inside doors' wood
            frame = window_frame_look(style, opening)
            if isinstance(frame, dict) and frame.get("material"):
                dlook = dict(dlook, **{k: frame[k] for k in ("material", "colour", "asset") if k in frame},
                             reason=dlook.get("reason", "") + "; frame in the windows' finish")
        leaf_mat = look_material(library, dlook) if dlook is not None else None
        win_mat = look_material(library, wlook) if wlook is not None else None
        # 29 Oct 2026 (D2, UL122): the door's frame and architrave in the family's finish (black in the modern,
        # industrial and minimal families, else the trim); an outside door's frame in its leaves' facade finish
        door_frame_mat = frame_mat
        if dlook is not None and opening.get("outside_door") and leaf_mat is not None:
            door_frame_mat = leaf_mat
        elif dlook is not None and isinstance(dlook.get("frame_look"), dict):
            door_frame_mat = look_material(library, dlook["frame_look"])
        framing = opening["type"] == "door" and bool(door_product(style))
        geo = {"centre": (cx, cy), "bottom": bottom, "width": width, "height": height, "thickness": thickness,
               "angle": angle, "index": index, "status": status, "level_id": level_id,
               "floor_z": floor_z}                 # 28 Oct 2026: a library door's added handles (opening_build)
        ctx = {"library": library, "collection": collection, "manifest_objects": manifest_objects,
               "assumed": assumed, "rooms": rooms}

        lib = (library_openings or {}).get(opening["id"])
        planned, k0 = None, len(manifest_objects)
        if lib is not None:
            from wenart.blender import opening_build as OB

            n0 = len(warnings)
            made = OB.build_library_opening(opening, wall, lib, geo, dict(ctx, warnings=warnings, assets_dir=assets_dir,
                                                                          geo_cache=geo_cache if geo_cache is not None
                                                                          else {}),
                                            {"glass": glass_mat, "frame": win_mat, "leaf": leaf_mat,
                                             "door_frame": door_frame_mat, "framing": framing}, op_assumed, shift)
            if made:
                created += made
                continue
            # 29 Oct 2026 (UL89: the HSSD doors the plan chose were refused by the build and nothing said so where the
            # door is): the parametric opening records the model it stands in for and why (model review M20)
            planned = library_planned_record(lib, warnings[n0:])
            k0 = len(manifest_objects)
        if opening["type"] == "door" and door_geometry_m10(style, opening):
            # Milestone 10: the door style of the look (the drawn operation first) from parametric.door_parts.
            created += build_door_m10(opening, wall, dlook, geo, ctx, {"frame": door_frame_mat, "leaf": leaf_mat,
                                                                       "glass": glass_mat}, op_assumed, shift)
        elif opening["type"] == "door":
            # Frame: two jambs and a head, as deep as the wall, and (fix round after P3) the jamb and head stops on
            # the leaf face away from the room the door opens into (door_m6_parts).
            swing, _swing_room, _swing_assumed = opening_room_side((cx, cy), wall, rooms, opening.get("swing_side"))
            m6 = door_m6_parts(width, height, thickness, swing)
            frame = _local_to_world(m6["frame"], (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_frame", *frame, collection=collection,
                                        wenart_id=opening["id"], kind="door", status=status, materials=[frame_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(dict(_opening_entry(opening, ob.name, level_id, frame_mat.name,
                                                        _textured(library, frame_mat), index, op_assumed, shift),
                                         frame={"lining": True, "head": True, "architrave": [], "indoor_faces": [],
                                                "source": "the Milestone 6 frame", "frameless": None,
                                                "architrave_why": None}))
            # Leaf: closed (0 deg), slightly smaller than the frame opening.
            leaf = _local_to_world(m6["leaf"], (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_leaf", *leaf, collection=collection,
                                        wenart_id=opening["id"], kind="door", status=status, materials=[leaf_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, leaf_mat.name,
                                                   _textured(library, leaf_mat), index, op_assumed, shift))
            # Lever handles on both faces: a design detail of the door (its id and pass index).
            handles = _local_to_world(door_handle_parts(width, height, bottom - floor_z), (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_handle", *handles, collection=collection,
                                        wenart_id=opening["id"], kind="door", status="assumed",
                                        materials=[steel_mat])
            ob.pass_index = index
            created.append(ob)
            reason = "design detail of the documented door (lever handles on both faces); not in the documents"
            entry = _opening_entry(opening, ob.name, level_id, steel_mat.name, False, index, {}, shift)
            entry.update(status="assumed", evidence=[], parent=opening["id"],
                         assumed={"detail": "door_handles", "lever_height_m": HANDLE_HEIGHT, "reason": reason})
            manifest_objects.append(entry)
            assumed.append({"object": ob.name, "field": "door_handles",
                            "value": f"steel lever pair at {HANDLE_HEIGHT} m", "reason": reason,
                            "parent": opening["id"], "kind": "door_handles"})
        elif window_geometry_m10(style, opening):
            # Milestone 10: the frame material's profile, mullions / transoms, the inside sill (window_parts).
            created += build_window_m10(opening, wall, wlook, geo, ctx, {"frame": win_mat, "glass": glass_mat,
                                                                         "sill": frame_mat}, op_assumed, shift)
        else:
            depth = min(thickness, 0.08)
            parts = [
                geom2d.box((-(width / 2.0 - fw / 2.0), 0.0, height / 2.0), (fw, depth, height)),
                geom2d.box((width / 2.0 - fw / 2.0, 0.0, height / 2.0), (fw, depth, height)),
                geom2d.box((0.0, 0.0, height - fw / 2.0), (width - 2 * fw, depth, fw)),
                geom2d.box((0.0, 0.0, fw / 2.0), (width - 2 * fw, depth, fw)),
            ]
            frame = _local_to_world(parts, (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_frame", *frame, collection=collection,
                                        wenart_id=opening["id"], kind="window", status=status, materials=[win_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, win_mat.name,
                                                   _textured(library, win_mat), index, op_assumed, shift))
            pane = _local_to_world([geom2d.box((0.0, 0.0, height / 2.0),
                                               (width - 2 * fw, DEFAULTS["glass_thickness"], height - 2 * fw))],
                                   (cx, cy, bottom), angle)
            ob = common.new_mesh_object(f"{opening['id']}_glass", *pane, collection=collection,
                                        wenart_id=opening["id"], kind="window", status=status, materials=[glass_mat])
            ob.pass_index = index
            created.append(ob)
            manifest_objects.append(_opening_entry(opening, ob.name, level_id, glass_mat.name, False, index, op_assumed, shift))
        if planned is not None:
            tag_library_planned(manifest_objects[k0:], opening["id"], planned)
    return created


PASSAGE_SILL_M = 0.20            # = door_spacing.DOORWAY_SILL_M: a doorless opening this low is a passage


def passage_lining_parts(width: float, height: float, thickness: float, head: bool) -> list:
    """The lined reveal of an open passage in the opening's frame (pure; 29 Oct 2026, UL122): a board
    ``parametric.LINING_T_M`` thick on each jamb (as deep as the wall less 2 mm, so no face lies in the wall's face
    plane) and, under a wall that goes on over it (``head``), one under its head; ``geom2d.box`` tuples."""
    lt = P.LINING_T_M
    d = max(0.01, float(thickness) - 0.002)
    w, h = float(width), float(height)
    parts = [geom2d.box((-(w / 2.0 - lt / 2.0), 0.0, h / 2.0), (lt, d, h)),
             geom2d.box((w / 2.0 - lt / 2.0, 0.0, h / 2.0), (lt, d, h))]
    if head:
        parts.append(geom2d.box((0.0, 0.0, h - lt / 2.0), (w - 2 * lt, d, lt)))
    return parts


def _passage_lining(opening, centre, width, height, thickness, angle, bottom, head, mat, collection,
                    manifest_objects, assumed, level_id, shift):
    """The ``<id>_lining`` object of an open passage (a design detail, assumed; its parent the opening)."""
    from wenart.blender import common

    verts, faces = _local_to_world(passage_lining_parts(width, height, thickness, head), (*centre, bottom), angle)
    ob = common.new_mesh_object(f"{opening['id']}_lining", verts, faces, collection=collection,
                                wenart_id=opening["id"], kind="opening", status="assumed", materials=[mat])
    reason = ("design detail of the documented passage: a lined reveal (jambs" + (" and head" if head else "")
              + " lining in the trim), no architrave (UL122); not in the documents")
    entry = _opening_entry(opening, ob.name, level_id, mat.name, False, None, {}, shift)
    entry.update(status="assumed", evidence=[], parent=opening["id"], has_geometry=True,
                 assumed={"detail": "passage_lining", "reason": reason},
                 frame={"lining": True, "head": bool(head), "architrave": [], "indoor_faces": [],
                        "source": "passage lining", "frameless": None,
                        "architrave_why": "an open passage: a lined reveal, no architrave"})
    manifest_objects.append(entry)
    assumed.append({"object": ob.name, "field": "passage_lining", "value": "lined reveal", "reason": reason,
                    "parent": opening["id"], "kind": "passage_lining"})
    return ob


def library_planned_record(lib: dict, warnings: list) -> dict:
    """The library model a parametric opening stands in for (pure; 29 Oct 2026, UL89): its asset, category, role and
    the build's reason (the warnings ``opening_build.build_library_opening`` wrote)."""
    asset = lib.get("asset") or {}
    return {"asset_id": asset.get("asset_id") or asset.get("id"), "title": asset.get("title"),
            "category": lib.get("category"), "role": lib.get("role"),
            "why": "; ".join(str(w) for w in warnings) or "the library model could not be built"}


def tag_library_planned(entries: list, opening_id: str, planned: dict) -> int:
    """``library_planned`` on the manifest entries of ``opening_id`` among ``entries`` (in place; pure)."""
    n = 0
    for entry in entries:
        if entry.get("element_id") == opening_id or entry.get("wenart_id") == opening_id:
            entry["library_planned"] = dict(planned)
            n += 1
    return n


def opening_room_side(centre, wall: dict, rooms: list[dict], room_id: str | None = None
                      ) -> tuple[int, str | None, bool]:
    """``(side, room id, assumed)`` of an opening (pure): the side of its wall where the room lies, +1 for the left
    of the wall direction (the opening frame's +y, ``_local_to_world``), -1 for the right. ``room_id`` (a door's
    ``swing_side``) is taken when it lies on a side; else the only side with a room; rooms on both sides or none:
    -1, assumed."""
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + DEFAULTS["face_probe"]
    found: dict[int, str] = {}
    for side in (1, -1):
        probe = (centre[0] + side * nx * reach, centre[1] + side * ny * reach)
        for room in rooms:
            if len(room.get("polygon") or []) >= 3 and G.point_in_polygon(probe, room["polygon"]):
                found[side] = room["id"]
                break
    for side, rid in found.items():
        if room_id is not None and rid == room_id:
            return side, rid, False
    if len(found) == 1:
        side, rid = next(iter(found.items()))
        return side, rid, False
    return -1, found.get(-1), True


def opening_parts_mesh(parts: list[dict], materials_by: dict, origin, angle: float) -> tuple[list, list, list, list]:
    """``(verts, faces, materials, face material indices)`` of parametric parts in an opening's frame
    (``parametric.door_parts`` / ``window_parts``), each part's material by its role, else by its key."""
    mats: list = []
    names: list[str] = []
    indices: list[int] = []
    pieces = []
    for part in parts:
        if part["role"] == "glass" and part["key"] != "glass" and part["key"] in materials_by:
            mat = materials_by[part["key"]]               # UL210: a pane of its own glass (satin in a wet room)
        else:
            mat = materials_by.get(part["role"]) or materials_by[part["key"]]
        if mat.name not in names:
            mats.append(mat)
            names.append(mat.name)
        indices += [names.index(mat.name)] * len(part["faces"])
        pieces.append((part["verts"], part["faces"]))
    verts, faces = _local_to_world(pieces, origin, angle)
    return verts, faces, mats, indices


def _opening_object(opening: dict, suffix: str, parts: list[dict], materials_by: dict, geo: dict, ctx: dict,
                    status: str):
    """A mesh object ``<opening id>_<suffix>`` of ``parts`` (kind door / window, the opening's pass index)."""
    from wenart.blender import common

    verts, faces, mats, indices = opening_parts_mesh(parts, materials_by, (*geo["centre"], geo["bottom"]),
                                                     geo["angle"])
    ob = common.new_mesh_object(f"{opening['id']}_{suffix}", verts, faces, collection=ctx["collection"],
                                wenart_id=opening["id"], kind=opening["type"], status=status, materials=mats,
                                face_material_indices=indices)
    ob.pass_index = geo["index"]
    return ob, mats


def _detail_entry(opening: dict, ob, mats: list, geo: dict, ctx: dict, detail: dict, value: str, field: str,
                  shift: float) -> None:
    """Manifest and ``assumed`` entries of a design detail of an opening (handles, an inside sill): status
    assumed, its parent the opening."""
    library = ctx["library"]
    entry = _opening_entry(opening, ob.name, geo["level_id"], mats[0].name, library.textured(mats[0]), geo["index"],
                           {}, shift)
    entry.update(status="assumed", evidence=[], parent=opening["id"], assumed=detail,
                 materials=[m.name for m in mats])
    ctx["manifest_objects"].append(entry)
    ctx["assumed"].append({"object": ob.name, "field": field, "value": value, "reason": detail["reason"],
                           "parent": opening["id"], "kind": field})


def build_door_m10(opening: dict, wall: dict, look: dict, geo: dict, ctx: dict, mats: dict, op_assumed: dict,
                   shift: float) -> list:
    """A Milestone 10 door (docs/milestone10.md §4.7): ``parametric.door_parts`` for the door look
    (``looks.door_look``: the drawn operation first, so sliding, pocket, double, folding and fixed doors are built
    as drawn; else the style's door style), in three objects as in Milestone 6: ``<id>_frame`` (the frame, or a
    sliding / barn door's rail), ``<id>_leaf`` (leaves, panels, glass, ledges; the manifest entry carries the
    ``door`` record) and ``<id>_handle`` (the handles in the look's handle metal: a design detail, assumed; none
    on a fixed door). A sliding or barn door hangs on the face of the room it opens into (``swing_side``), else
    of the only room next to it (``opening_room_side``)."""
    library = ctx["library"]
    look = dict(look or {})
    side, side_room, side_assumed = opening_room_side(geo["centre"], wall, ctx["rooms"], opening.get("swing_side"))
    look["side"] = side
    if look.get("architrave"):
        # 29 Oct 2026 (UL89): the product door's architrave on the faces of its indoor rooms (never on the facade)
        look["architrave_faces"] = architrave_faces(geo["centre"], wall, ctx["rooms"])
    state = opening.get("leaf_state") if isinstance(opening.get("leaf_state"), dict) else None
    if state is not None:
        look["leaf_state"] = state                  # 29 Oct 2026 (D1, UL116): open, ajar or slid open
    parts, record = P.door_parts(look, geo["width"], geo["height"], geo["thickness"], DEFAULTS["frame_width"])
    if state is not None and state.get("state") in ("open", "ajar") and not record.get("pose"):
        # the style cannot take the pose (a folding or a sectional door): built closed, the record says why
        opening["leaf_state"] = dict(state, state="closed", built=False, leaf_polys=[],
                                     reason=str(state.get("reason") or "") + f"; built closed: a "
                                                                             f"{record['door_style']} leaf")
    handle_mat = library.get(look.get("handle_material") or "steel_brushed")
    by = {"frame": mats["frame"], "rail": handle_mat, "groove": handle_mat, "leaf": mats["leaf"],
          "glass": mats["glass"], "handle": handle_mat}
    # fix round after P3 (16-17 Oct 2026): the stops (role ``stop``) belong to the frame object, so the leaf object
    # and its manifest material stay as they were
    groups = {"frame": [p for p in parts if p["role"] in FRAME_ROLES],
              "leaf": [p for p in parts if p["role"] not in FRAME_ROLES and p["key"] != "handle"],
              "handle": [p for p in parts if p["key"] == "handle"]}
    record = dict(record, operation=look.get("operation"), operation_assumed=bool(look.get("operation_assumed")),
                  handle=look.get("handle"), handle_material=handle_mat.name if groups["handle"] else None,
                  side_room=side_room if record["surface_mounted"] else None,
                  side_assumed=side_assumed if record["surface_mounted"] else None, reason=look.get("reason"))
    created = []
    for key in ("frame", "leaf"):
        if not groups[key]:
            continue
        ob, used = _opening_object(opening, key, groups[key], by, geo, ctx, geo["status"])
        created.append(ob)
        entry = _opening_entry(opening, ob.name, geo["level_id"], used[0].name, library.textured(used[0]),
                               geo["index"], op_assumed, shift)
        entry["materials"] = [m.name for m in used]
        if key == "leaf":
            entry["door"] = record
            # 29 Oct 2026 (UL122): what frames it (a door of a style without a family: its jambs and head)
            entry["frame"] = record.get("frame") or {
                "lining": not record["surface_mounted"], "head": not record["surface_mounted"], "architrave": [],
                "indoor_faces": [], "source": "parametric (no style family)", "frameless": None,
                "architrave_why": "a style without a family keeps its Milestone 10 door"}
            if not record["surface_mounted"]:
                # 30 Oct 2026 (UL132): the built frame parts and the opening's one height (M29: frame_problems)
                entry["frame"] = dict(entry["frame"], census=P.frame_census(groups["frame"], geo["height"]))
            if record.get("pose"):
                entry["pose"] = record["pose"]
        ctx["manifest_objects"].append(entry)
    if record["surface_mounted"] and side_assumed:
        ctx["assumed"].append({"object": opening["id"], "field": "door_side", "value": side,
                               "reason": f"{record['door_style']} door: rooms on both sides or none and no "
                                         f"swing_side; hung on the wall's {'left' if side > 0 else 'right'} face"})
    if record.get("architrave") or record.get("leaf_detail"):
        # 29 Oct 2026 (UL89): the product door's design details, not in the documents
        ctx["assumed"].append({"object": opening["id"], "field": "door_product",
                               "value": {"architrave": record.get("architrave"),
                                         "leaf_detail": record.get("leaf_detail"), "hinges": record.get("hinges")},
                               "reason": "design detail of the documented door (the style family's door: "
                                         f"{look.get('reason') or 'assumed'}); not in the documents"})
    if groups["handle"]:
        ob, used = _opening_object(opening, "handle", groups["handle"], by, geo, ctx, "assumed")
        created.append(ob)
        what = "rail and handle" if record["surface_mounted"] else "handles on both faces"
        if record.get("hinges"):
            what += f" and {record['hinges']} hinges"
        reason = (f"design detail of the documented {record['door_style']} door ({look.get('handle') or 'steel'} "
                  f"{what}); not in the documents")
        _detail_entry(opening, ob, used, geo, ctx, {"detail": "door_handles", "lever_height_m": P.LEVER_HEIGHT_M,
                                                    "reason": reason},
                      f"{used[0].name} handles", "door_handles", shift)
    return created


def build_window_m10(opening: dict, wall: dict, look: dict, geo: dict, ctx: dict, mats: dict, op_assumed: dict,
                     shift: float) -> list:
    """A Milestone 10 window (docs/milestone10.md §4.7): ``parametric.window_parts`` for the window frame look
    (the frame material's profile, the opening's ``mullions`` / ``transoms``), in ``<id>_frame`` (frame and bars;
    the manifest entry carries the ``window`` record, which ``build_outside_details`` reads for the outside sill),
    ``<id>_glass`` and ``<id>_inside_sill`` (the trim look on the room side's reveal: a design detail, assumed)."""
    library = ctx["library"]
    look = look or {}
    side, room_id, side_assumed = opening_room_side(geo["centre"], wall, ctx["rooms"])
    # 30 Oct 2026 (lessons UL197, UL181): the window as a real product (parametric.window_product_parts: the stepped
    # frame, sashes or glazing beads, gaskets, handles, a wide glazing divided into real panes)
    # 30 Oct 2026 (lesson UL210, window_order): a window of a facade group keeps the group's lines; a fixed lower light
    # below its transom (``lower_light``) where it needs a higher sill, satin glass in a wet room (``glass``)
    lower = opening.get("lower_light") if isinstance(opening.get("lower_light"), dict) else {}
    glass_key = "satin" if opening.get("glass") == "satin" else "glass"
    transom_at = None
    if lower.get("at_m") is not None and opening.get("sill_height") is not None:
        transom_at = float(lower["at_m"]) - float(opening["sill_height"])
    parts, record = P.window_product_parts(look, geo["width"], geo["height"], geo["thickness"], look.get("mullions", 0),
                                           look.get("transoms", 0), side, sill=opening.get("sill_height"),
                                           transom_at=transom_at,
                                           glass_keys=("satin" if lower.get("glass") == "satin" else glass_key,
                                                       glass_key))
    by = {"frame": mats["frame"], "glass": mats["glass"], "sill": mats["sill"],
          "gasket": library.get(WINDOW_GASKET_MATERIAL), "handle": mats.get("handle") or mats["frame"]}
    if any(p.get("key") == "satin" for p in parts):
        by["satin"] = library.satin_glass()
    record = dict(record, inside_side=side, room_id=room_id, inside_assumed=side_assumed, reason=look.get("reason"))
    created = []
    for key, roles in (("frame", WINDOW_FRAME_ROLES), ("glass", ("glass",))):
        group = [p for p in parts if p["role"] in roles]
        ob, used = _opening_object(opening, key, group, by, geo, ctx, geo["status"])
        created.append(ob)
        entry = _opening_entry(opening, ob.name, geo["level_id"], used[0].name,
                               library.textured(used[0]) if key == "frame" else False, geo["index"], op_assumed,
                               shift)
        if key == "frame":
            entry["window"] = record
        ctx["manifest_objects"].append(entry)
    sill = [p for p in parts if p["role"] == "sill"]
    if sill:
        ob, used = _opening_object(opening, "inside_sill", sill, by, geo, ctx, "assumed")
        created.append(ob)
        info = record["inside_sill"]
        reason = (f"design detail of the documented window: an inside sill {info['depth']} m deep, "
                  f"{info['proud']} m proud of the wall face, in the trim look"
                  + ("; rooms on both sides or none: the sill on the wall's right face" if side_assumed else "")
                  + "; not in the documents")
        _detail_entry(opening, ob, used, geo, ctx, {"detail": "inside_sill", **info, "reason": reason},
                      f"{used[0].name} sill", "inside_sill", shift)
    handles = [p for p in parts if p["role"] == "handle"]
    if handles:
        ob, used = _opening_object(opening, "handle", handles, by, geo, ctx, "assumed")
        created.append(ob)
        product = record.get("product") or {}
        reason = (f"design detail of the documented window: a {product.get('kind')} window of "
                  f"{product.get('panes')} pane(s), handles on the opening one(s) {product.get('opening')} "
                  f"({product.get('why')}); not in the documents")
        _detail_entry(opening, ob, used, geo, ctx, {"detail": "window_handles", "product": product, "reason": reason},
                      f"{used[0].name} handles", "window_handles", shift)
    return created


WINDOW_FRAME_ROLES: tuple[str, ...] = ("frame", "mullion", "transom", "sash", "bead", "gasket", "track")
WINDOW_GASKET_MATERIAL = "steel_black"     # 30 Oct 2026 (UL197): the dark gasket line at the glass


def _textured(library, mat) -> bool:
    return library.textured(mat)


def door_leaf_material(door_style: dict) -> tuple[str, str | None]:
    """``(slug, asset id)`` of the door leaves: the veneer of a wood door slug
    (``vocabulary.veneer_for``: the floor planks were on the doors before
    Milestone 6; the veneer's grain runs along the box UV v, world Z on the
    leaf: vertical), else the style's door slug and asset (painted doors)."""
    slug = door_style.get("material") or "wood_oak_light"
    try:
        from wenart.style import vocabulary as V
        veneer = V.veneer_for(slug)
        if veneer is not None:
            return veneer, V.FURNITURE_MATERIALS[veneer].get("asset")
    except Exception:  # noqa: BLE001 - without the vocabulary the style slug stays
        pass
    return slug, door_style.get("asset")


def _opening_entry(opening, name, level_id, material, textured, index, op_assumed, shift) -> dict:
    return {
        "name": name or opening["id"], "wenart_id": opening["id"], "kind": opening["type"],
        "status": opening.get("status", "verified"), "level_id": level_id, "element_id": opening["id"],
        "evidence": opening.get("evidence", []), "material": material, "textured": textured,
        "pass_index": index, "assumed": dict(op_assumed), "wall_id": opening.get("wall_id"),
        "has_geometry": name is not None, "center_shift": round(shift, 4),
    }


def separator_entry(opening: dict, level_id: str) -> dict:
    """Manifest entry of a virtual separator (pure): kind ``opening``, no
    geometry, no wall, its ``line``; floors and ceilings meet there."""
    entry = _opening_entry(opening, None, level_id, None, False, None, {}, 0.0)
    entry.update({"virtual": True, "line": opening.get("line"),
                  "note": "virtual separator: no geometry; the room floors and ceilings meet at the line"})
    return entry


def floor_style(room: dict, style: dict, outdoor: dict | None = None) -> tuple[dict, bool]:
    """``(style slot, wet)`` of a room floor: the wet-room floor for bathroom /
    wc / kitchen, the style floor otherwise (dining and prayer rooms as living
    rooms, ``slot_room_type``). Milestone 10: ``outdoor`` (the exterior ``paving``
    look) is the floor of a room open to the sky (a roof terrace), not the
    interior floor (real02's terraces showed oak parquet in the rain). Milestone 11 (docs/milestone11.md §1.3
    M2): a kitchen takes the style's floor when it is wet-safe (``profile.is_wet_safe``: tiles, stone,
    terracotta, polished concrete ...), else the wet floor."""
    if outdoor and (outdoor.get("material") or outdoor.get("slug")):
        return dict(outdoor, material=outdoor.get("material") or outdoor.get("slug")), False
    kind = slot_room_type(room.get("room_type"))
    if kind in KITCHEN_TYPES and isinstance(style.get("floor"), dict) and _wet_safe(style["floor"].get("material")):
        return style["floor"], True
    # 29 Oct 2026 (K11, wenart.blender.kitchen_details.floor_look): a kitchen of the modern families takes large glossy
    # porcelain tiles where the style names no wet-safe floor (before: the wet rooms' floor)
    if kind in KITCHEN_TYPES:
        try:
            from wenart.blender import kitchen_details as KD
            tile = KD.floor_look(style.get("family"))
        except ImportError:
            tile = None
        if tile is not None:
            return {"material": tile["material"], "colour": tile["colour"], "reason": tile["reason"]}, True
    wet = kind in WET_ROOM_TYPES
    slot = (style.get("wet_floor") if wet else None) or style["floor"]
    if wet and kind not in KITCHEN_TYPES and slot is style.get("wet_floor"):
        # 29 Oct 2026 (UL114 B8): a bathroom's or WC's floor in the family's large stone-look tile (the brief's wins)
        try:
            from wenart.blender import bath_parts as BT
            tile = BT.wet_tile_look(style, "floor")
        except ImportError:
            tile = None
        if tile is not None:
            slot = {k: v for k, v in tile.items() if k in ("material", "asset", "colour")}   # its own 60 x 120 grid
    # 29 Oct 2026 (UL106): the style's plank floor laid in the room's pattern (herringbone / chevron; the build writes
    # ``room["floor_pattern"]``, wenart.blender.parquet.annotate)
    if not wet and slot is style.get("floor") and isinstance(slot, dict):
        try:
            from wenart.blender import parquet as PQ
            extra = PQ.floor_params(room)
        except ImportError:
            extra = None
        if extra:
            slot = dict(slot, params=dict(slot.get("params") or {}, **extra))
    return slot, wet


def _wet_safe(slug) -> bool:
    try:
        from wenart.style.profile import is_wet_safe
    except ImportError:          # Blender without the style package: the M10 rule (the wet floor)
        return False
    return bool(is_wet_safe(slug))


def kitchen_counter_back(piece: dict, room: dict, reach: float = SPLASHBACK["wall_reach"]
                         ) -> tuple[tuple, tuple, float] | None:
    """The wall stretch behind a kitchen piece (pure; M11 M2): ``(p, q, distance)``, the piece's back edge
    projected onto the nearest room-polygon edge within ``reach`` that runs parallel to it (the back edge of
    ``front_deg`` when the piece has one, else its longest edge nearest a wall), None when it stands free (an
    island)."""
    fp = piece["footprint"]
    corners = G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0))
    edges = [(corners[i], corners[(i + 1) % 4]) for i in range(4)]
    poly = [tuple(p[:2]) for p in room["polygon"]]
    front = piece.get("front_deg")
    if front is not None:
        back = (math.cos(math.radians(float(front) + 180.0)), math.sin(math.radians(float(front) + 180.0)))
        cx, cy = fp["center"]
        edges.sort(key=lambda e: -((e[0][0] + e[1][0]) / 2.0 - cx) * back[0] - ((e[0][1] + e[1][1]) / 2.0 - cy) * back[1])
        edges = edges[:1]
    else:
        edges.sort(key=lambda e: -G.distance(*e))
    best = None
    for a, b in edges:
        length = G.distance(a, b)
        if length < 0.3:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        for i in range(len(poly)):
            p, q = poly[i], poly[(i + 1) % len(poly)]
            el = G.distance(p, q)
            if el < 1e-6:
                continue
            ex, ey = (q[0] - p[0]) / el, (q[1] - p[1]) / el
            if abs(ux * ex + uy * ey) < 0.98:
                continue
            d = abs((mid[0] - p[0]) * -ey + (mid[1] - p[1]) * ex)
            t = (mid[0] - p[0]) * ex + (mid[1] - p[1]) * ey
            if d > reach or t < -0.05 or t > el + 0.05:
                continue
            if best is None or d < best[2]:
                ta = (a[0] - p[0]) * ex + (a[1] - p[1]) * ey
                tb = (b[0] - p[0]) * ex + (b[1] - p[1]) * ey
                lo, hi = max(0.0, min(ta, tb)), min(el, max(ta, tb))
                best = ((p[0] + ex * lo, p[1] + ey * lo), (p[0] + ex * hi, p[1] + ey * hi), d)
    return best


def wall_face_openings(building: dict, level: dict, p, q, reach: float = WALL_FACE_REACH) -> list[dict]:
    """The openings of the wall a face segment ``p -> q`` lies on (pure; 26 Oct 2026): every door, window and plain
    opening of the level whose wall runs parallel to ``p -> q`` (within about 8 degrees) with the segment within half
    the wall's thickness + ``reach`` of its centre line, and every virtual separator whose line runs along the segment
    (no wall there at all), when they overlap the segment. ``[{"id", "type", "t0", "t1", "z0", "z1"}]``: ``t`` in
    metres from ``p`` along ``p -> q`` (the opening's width around its centre on the wall), ``z`` in building z
    (``opening_vertical``; a virtual separator from the floor to the ceiling)."""
    length = G.distance(p, q)
    if length < 1e-9:
        return []
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    mid = ((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0)
    walls = {w["id"]: w for w in building.get("walls") or [] if w.get("level_id") == level["id"]}
    floor_z = float(level["elevation"])
    out = []
    for o in building.get("openings") or []:
        if o.get("level_id") != level["id"]:
            continue
        line = o.get("line")
        if is_virtual(o):
            if not (isinstance(line, (list, tuple)) and len(line) == 2):
                continue
            (ax, ay), (bx, by) = line[0][:2], line[1][:2]
            half, centre = 0.0, None
            z0, z1 = floor_z, floor_z + float(level["ceiling_height"])
        else:
            wall = walls.get(o.get("wall_id"))
            if wall is None or o.get("type") not in ("door", "window", "opening"):
                continue
            (ax, ay), (bx, by) = wall["start"][:2], wall["end"][:2]
            half = float(wall["thickness"]) / 2.0
            centre = opening_centre_on_wall(o, wall)[:2]
            z0, z1, _ = opening_vertical(o, level, False)
        wl = math.hypot(bx - ax, by - ay)
        if wl < 1e-9 or abs((bx - ax) / wl * ux + (by - ay) / wl * uy) < 0.99:
            continue
        nx, ny = -(by - ay) / wl, (bx - ax) / wl
        if abs((mid[0] - ax) * nx + (mid[1] - ay) * ny) > half + reach:
            continue
        if centre is None:                                    # a virtual separator: its line's ends
            ts = sorted(((x - p[0]) * ux + (y - p[1]) * uy) for x, y in ((ax, ay), (bx, by)))
        else:
            tc = (centre[0] - p[0]) * ux + (centre[1] - p[1]) * uy
            ts = [tc - float(o["width"]) / 2.0, tc + float(o["width"]) / 2.0]
        if ts[1] <= 0.0 or ts[0] >= length:
            continue
        out.append({"id": o["id"], "type": "virtual" if centre is None else o["type"], "t0": ts[0], "t1": ts[1],
                    "z0": z0, "z1": z1})
    return out


def split_band(t0: float, t1: float, z0: float, z1: float, holes, clear: float = WALL_FINISH_OPENING_CLEAR,
               min_piece: float = WALL_FINISH_MIN_PIECE) -> list[tuple[float, float, float, float]]:
    """A band on a wall face (``t0 .. t1`` along the wall, ``z0 .. z1`` high) with every opening of ``holes``
    (``(t0, t1, z0, z1)``, grown by ``clear`` all round) taken out (pure; 26 Oct 2026): beside an opening the band
    keeps its full height, under or over it (a window sill above the counter) only the strip the opening leaves. Pieces
    narrower or lower than ``min_piece`` are left out. Returns the pieces ``[(t0, t1, z0, z1)]`` in order; ``[]`` when
    the openings cover the whole band."""
    pieces = [(float(t0), float(t1), float(z0), float(z1))]
    for h in holes:
        h0, h1, hz0, hz1 = float(h[0]) - clear, float(h[1]) + clear, float(h[2]) - clear, float(h[3]) + clear
        nxt = []
        for a, b, c, d in pieces:
            if h1 <= a or h0 >= b or hz1 <= c or hz0 >= d:
                nxt.append((a, b, c, d))
                continue
            m0, m1 = max(a, h0), min(b, h1)
            if h0 > a:
                nxt.append((a, h0, c, d))                     # beside the opening, full height
            if h1 < b:
                nxt.append((h1, b, c, d))
            if hz0 > c:
                nxt.append((m0, m1, c, hz0))                  # under it (a sill above the band's foot)
            if hz1 < d:
                nxt.append((m0, m1, hz1, d))                  # over it
        pieces = nxt
    return sorted(pc for pc in pieces if pc[1] - pc[0] >= min_piece and pc[3] - pc[2] >= min_piece)


SPLASHBACK_CORNER = {"touch_m": 0.05, "reach_m": 0.75, "depth_m": 0.70, "square": 0.30}


def splashback_corner_ends(piece: dict, pieces: list, room: dict, p, q, normal) -> tuple[tuple, tuple, list]:
    """30 Oct 2026 (lesson UL149, user on real04 run 20261029-201533-full: "this wall seems like missing the texture":
    a bare painted patch behind the microwave where two counter runs meet): ``(p, q, ids)``, the splashback band
    ``p -> q`` of a counter run (on its wall face, ``normal`` into the room) carried on at either end over the corner
    square of another counter run of the room that butts against the same wall at right angles (its end within
    ``touch_m`` of the band's end, within ``depth_m`` of the wall, at most ``reach_m`` on: the other run's depth), up to
    the room's wall; ``ids`` names those runs (pure). A run standing on along the same wall keeps its own band."""
    poly = [tuple(v[:2]) for v in room.get("polygon") or []]
    length = G.distance(p, q)
    if length < 1e-6 or len(poly) < 3:
        return p, q, []
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    nx, ny = normal
    rot = math.radians(float(piece["footprint"].get("rotation_deg") or 0.0))
    lo, hi, ids = 0.0, length, []
    for other in pieces:
        if other is piece or other.get("id") == piece.get("id") or other.get("room_id") != piece.get("room_id") \
                or other.get("type") != "kitchen_counter" or not piece_built(other) \
                or not isinstance(other.get("footprint"), dict):
            continue
        orot = math.radians(float(other["footprint"].get("rotation_deg") or 0.0))
        if abs(math.cos(orot - rot)) > SPLASHBACK_CORNER["square"]:
            continue                                     # not at right angles: a run on along the same wall
        pts = G.rotated_rectangle(other["footprint"]["center"], other["footprint"]["size"],
                                  math.degrees(orot))
        ts = [(x - p[0]) * ux + (y - p[1]) * uy for x, y in pts]
        ds = [(x - p[0]) * nx + (y - p[1]) * ny for x, y in pts]
        if min(ds) > SPLASHBACK_CORNER["depth_m"] or max(ds) < 0.0:
            continue                                     # it does not reach this wall
        if abs(min(ts) - length) <= SPLASHBACK_CORNER["touch_m"] or (min(ts) > length - 0.05 and min(ts) < length):
            new = min(max(ts), length + SPLASHBACK_CORNER["reach_m"])
            if new > hi + 1e-6:
                hi, ids = new, ids + [other["id"]]
        elif abs(max(ts)) <= SPLASHBACK_CORNER["touch_m"]:
            new = max(min(ts), -SPLASHBACK_CORNER["reach_m"])
            if new < lo - 1e-6:
                lo, ids = new, ids + [other["id"]]
    if not ids:
        return p, q, []
    # never past the room's wall: clip to the room edge the band lies on
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        el = G.distance(a, b)
        if el < 1e-6:
            continue
        ex, ey = (b[0] - a[0]) / el, (b[1] - a[1]) / el
        if abs(ex * ux + ey * uy) < 0.98 or abs((p[0] - a[0]) * -ey + (p[1] - a[1]) * ex) > 0.02:
            continue
        t_a = (a[0] - p[0]) * ux + (a[1] - p[1]) * uy
        t_b = (b[0] - p[0]) * ux + (b[1] - p[1]) * uy
        e0, e1 = min(t_a, t_b), max(t_a, t_b)
        if e0 - 0.02 <= 0.0 and length <= e1 + 0.02:
            lo, hi = max(lo, e0), min(hi, e1)
            break
    else:
        lo, hi = max(lo, 0.0), min(hi, length)          # no room edge under the band: keep it as it was
    if hi - lo <= length + 1e-6:
        return p, q, []
    return (p[0] + ux * lo, p[1] + uy * lo), (p[0] + ux * hi, p[1] + uy * hi), ids


def splashback_bands(building: dict, level: dict) -> list[dict]:
    """The splashback bands of a level's kitchens before they become boxes (pure; docs/milestone11.md §1.3 M2): behind
    every kitchen counter run, sink, hob or stove (``SPLASHBACK["types"]``) of a kitchen that stands against a wall
    (``kitchen_counter_back``), a band from its counter top (its height, else ``counter_top``) ``height`` high on the
    wall face ``p -> q``, cut at every opening of that wall (``wall_face_openings``, ``split_band``; 26 Oct 2026: a
    finish never covers an opening). ``[{"piece_id", "room_id", "p", "q", "normal", "z0", "z1", "openings": [ids that
    cut it], "pieces": [(t0, t1, z0, z1)]}]``; neighbouring pieces on one wall each get their own band."""
    rooms = {r["id"]: r for r in building.get("rooms") or [] if r.get("level_id") == level["id"]}
    out = []
    floor_z = float(level["elevation"])
    for piece in building.get("furniture") or []:
        room = rooms.get(piece.get("room_id"))
        if room is None or slot_room_type(room.get("room_type")) not in KITCHEN_TYPES \
                or piece.get("type") not in SPLASHBACK["types"] or not piece_built(piece) \
                or len(room.get("polygon") or []) < 3:
            continue
        back = kitchen_counter_back(piece, room)
        if back is None:
            continue
        p, q, _d = back
        length = G.distance(p, q)
        if length < 0.2:
            continue
        ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
        nx, ny = -uy, ux                                    # towards the piece (into the room)
        cx, cy = piece["footprint"]["center"]
        mid = ((p[0] + q[0]) / 2.0, (p[1] + q[1]) / 2.0)
        if (cx - mid[0]) * nx + (cy - mid[1]) * ny < 0:
            nx, ny = -nx, -ny
        # 30 Oct 2026 (lesson UL149): the band runs on into the inside corner the next run's end fills
        p, q, corners = splashback_corner_ends(piece, building.get("furniture") or [], room, p, q, (nx, ny))
        length = G.distance(p, q)
        top = float(piece.get("height") or SPLASHBACK["counter_top"])
        top = SPLASHBACK["counter_top"] if top > 1.2 else top       # a tall unit (fridge column): the counter top
        z0, z1 = floor_z + top, floor_z + top + SPLASHBACK["height"]
        holes = [h for h in wall_face_openings(building, level, p, q)
                 if h["t1"] > 0.0 and h["t0"] < length and h["z1"] > z0 and h["z0"] < z1]
        out.append({"piece_id": piece["id"], "room_id": room["id"], "p": [p[0], p[1]], "q": [q[0], q[1]],
                    "normal": [nx, ny], "z0": z0, "z1": z1, "openings": [h["id"] for h in holes],
                    **({"into_corner": corners} if corners else {}),
                    "pieces": split_band(0.0, length, z0, z1, [(h["t0"], h["t1"], h["z0"], h["z1"]) for h in holes]
                                         ) if holes else [(0.0, length, z0, z1)]})
    return out


def splashback_plan(building: dict, level: dict) -> list[dict]:
    """The splashback boxes of a level's kitchens (pure; ``splashback_bands``): one box per band piece left between
    the openings of its wall, ``thickness`` thick on the wall face (``gap`` off it, into the room). ``[{"piece_id",
    "room_id", "center", "size", "rotation_deg", "cut_at": [opening ids]}]``; a band the openings cover entirely gives
    no box (``splashback_bands`` keeps its record)."""
    out = []
    off = SPLASHBACK["gap"] + SPLASHBACK["thickness"] / 2.0
    for band in splashback_bands(building, level):
        (px, py), (qx, qy), (nx, ny) = band["p"], band["q"], band["normal"]
        length = math.hypot(qx - px, qy - py)
        ux, uy = (qx - px) / length, (qy - py) / length
        for t0, t1, z0, z1 in band["pieces"]:
            tm = (t0 + t1) / 2.0
            out.append({"piece_id": band["piece_id"], "room_id": band["room_id"],
                        "center": [px + ux * tm + nx * off, py + uy * tm + ny * off, (z0 + z1) / 2.0],
                        "size": [t1 - t0, SPLASHBACK["thickness"], z1 - z0],
                        "rotation_deg": math.degrees(math.atan2(uy, ux)), "cut_at": list(band["openings"])})
    return out


def splashback_family_look(building: dict, level: dict, style: dict) -> dict | None:
    """29 Oct 2026 (K5, G3): the splashback look of the style's family (``kitchen_details.splashback_look``: the
    worktop's stone, a white marble slab or white subway tiles; None keeps the wet walls' tiles) with the designs of
    the level's kitchen runs (their worktop); pure."""
    try:
        from wenart.blender import kitchen_details as KD
    except ImportError:
        return None
    designs = []
    for p in building.get("furniture") or []:
        if p.get("level_id") != level.get("id") or p.get("type") not in ("kitchen_counter", "kitchen_island"):
            continue
        plan = ((p.get("asset") or {}).get("module_plan") or {}) if isinstance(p.get("asset"), dict) else {}
        designs.append(plan.get("design") or p.get("design") or {})
    return KD.splashback_look((style or {}).get("family"), designs)


def build_splashbacks(building: dict, level: dict, collection, library, style: dict, manifest_objects: list,
                      assumed: list) -> int:
    """The splashback objects of ``splashback_plan``: one object ``splashback_<room>`` per kitchen (kind
    ``splashback``, status assumed, the room as parent, pass index 0: a finish on the wall, not an element of the
    JSON). Its look: the style's ``splashback`` slot (agent override), else the wet walls' tiles. 26 Oct 2026: every
    band cut at an opening of its wall is listed in ``assumed`` (field ``splashback_cut``), also when nothing is
    left."""
    from wenart.blender import common

    for band in splashback_bands(building, level):
        if band["openings"]:
            left = len(band["pieces"])
            assumed.append({"object": f"splashback_{band['room_id']}", "field": "splashback_cut",
                            "value": band["openings"],
                            "reason": f"the splashback behind {band['piece_id']} is cut at the opening(s) "
                                      f"{', '.join(band['openings'])} of its wall (a wall finish never covers an "
                                      f"opening): " + (f"{left} piece(s) left" if left
                                                       else "nothing left, the openings cover it"),
                            "parent": band["room_id"], "kind": "splashback"})
    plan = splashback_plan(building, level)
    if not plan:
        return 0
    slot = style.get("splashback") if isinstance(style.get("splashback"), dict) else None
    if slot is None and "wet_walls_brief" in style:
        # 29 Oct 2026 (UL114 B8): the bathrooms' family tiles are no kitchen's; the splashback keeps the brief's wet walls
        style = dict(style, wet_walls=style["wet_walls_brief"])
    look = dict(_slot_look(slot, "tiles_light"), colour=slot.get("colour")) if slot else wet_wall_look(style, None)
    family_look = None if slot else splashback_family_look(building, level, style)
    if family_look is not None:
        # 29 Oct 2026 (K5, G3; wenart.blender.kitchen_details.splashback_look): the family's stone or subway tiles
        look = {"material": family_look["material"], "asset": None, "tint": None, "colour": family_look.get("colour")}
        for rid in sorted({b["room_id"] for b in plan}):     # one record per kitchen, its room the parent
            assumed.append({"object": f"splashback_{rid}", "field": "splashback_look",
                            "value": family_look["material"], "reason": family_look["reason"], "parent": rid,
                            "kind": "splashback"})
    mat = look_material(library, look)
    by_room: dict[str, list] = {}
    for b in plan:
        by_room.setdefault(b["room_id"], []).append(b)
    for rid, boxes in sorted(by_room.items()):
        verts, faces = geom2d.merge([geom2d.box(b["center"], b["size"], b["rotation_deg"]) for b in boxes])
        name = f"splashback_{rid}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="splashback",
                                    status="assumed", materials=[mat])
        ob.pass_index = 0
        cuts = sorted({o for b in boxes for o in b.get("cut_at") or []})
        reason = (f"kitchen splashback: tiles {SPLASHBACK['height']:g} m high from the counter top behind "
                  f"{', '.join(dict.fromkeys(b['piece_id'] for b in boxes))} (docs/milestone11.md §1.3 M2; not drawn)"
                  + (f"; cut at the opening(s) {', '.join(cuts)}" if cuts else ""))
        manifest_objects.append({
            "name": ob.name, "wenart_id": name, "kind": "splashback", "status": "assumed", "level_id": level["id"],
            "element_id": rid, "evidence": [], "material": mat.name, "textured": library.textured(mat),
            "pass_index": None, "detail": "splashback", "pieces": list(dict.fromkeys(b["piece_id"] for b in boxes)),
            "cut_at": cuts, "assumed": {"reason": reason}})
        assumed.append({"object": name, "field": "splashback", "value": SPLASHBACK["height"], "reason": reason,
                        "parent": rid, "kind": "splashback"})
    return len(plan)


def slot_material(library, slot: dict, unverified: bool = False):
    """The material of a style slot (floor, ceiling, trim, ...): its slug, asset and tint and, Milestone 10, its
    colour name and procedural ``params`` (``materials.MaterialLibrary.get``; a slot without them is the M9
    material)."""
    return library.get(slot["material"], slot.get("asset"), slot.get("tint"), unverified=unverified,
                       colour=slot.get("colour"), params=slot.get("params"))


def floor_material(room: dict, style: dict, library, outdoor: dict | None = None):
    """``(material, wet)`` of a room floor: the style floor, the wet-room floor
    for bathroom / wc / kitchen (``outdoor``: a roof terrace's paving,
    ``floor_style``), the dashed-red overlay for unverified rooms."""
    slot, wet = floor_style(room, style, outdoor)
    mat = slot_material(library, slot, unverified=room.get("status") == "unverified")
    return mat, wet


def _threshold(opening, wall, centre, angle, floor_z, has_below, rooms, style, library, collection,
               manifest_objects, warnings, op_assumed, shift):
    """Floor face of opening width x wall thickness under a door or plain
    opening, with the material of the adjacent room floor. Lifted 1 mm when a
    level lies below so it never shares a face with a stacked wall top."""
    from wenart.blender import common

    room = adjacent_room(centre, wall, rooms)
    if room is None:
        warnings.append(f"{opening['id']}: no room on either side; threshold gets the style floor material")
    mat, wet = floor_material(room or {}, style, library)
    # Milestone 12 (track L): the threshold at the door's threshold_z; between two rooms whose floors differ, a
    # step block from the lower floor up to it (inner_step).
    base = float(opening["threshold_z"]) if opening.get("threshold_z") is not None else floor_z
    z = base + (DEFAULTS["threshold_lift"] if has_below else 0.0)
    level = {"elevation": floor_z}
    step = inner_step(opening, wall, rooms, level)
    if step is not None:
        verts, faces = geom2d.prism(step["polygon"], step["z0"], z)
    else:
        verts, faces = geom2d.polygon_face(
            G.rotated_rectangle(centre, (float(opening["width"]), float(wall["thickness"])), angle), z,
            facing_up=True)
    ob = common.new_mesh_object(f"{opening['id']}_threshold", verts, faces, collection=collection,
                                wenart_id=opening["id"], kind="floor", status=opening.get("status", "verified"),
                                materials=[mat])
    manifest_objects.append({
        "name": ob.name, "wenart_id": opening["id"], "kind": "floor", "status": opening.get("status", "verified"),
        "level_id": opening["level_id"], "element_id": opening["id"], "evidence": opening.get("evidence", []),
        "material": mat.name, "textured": library.textured(mat), "pass_index": None, "assumed": dict(op_assumed),
        "wall_id": opening.get("wall_id"), "room_id": room["id"] if room else None,
        "room_type": room.get("room_type") if room else None, "wet": wet, "center_shift": round(shift, 4),
        "lifted": z - floor_z,
    })
    if step is not None:
        manifest_objects[-1]["step"] = {"rise": step["rise"], "low_room": step["low_room"],
                                        "high_room": step["high_room"]}
    return ob


def _soffit(opening, wall, centre, angle, z, style, library, collection, manifest_objects, op_assumed, shift):
    """Downward face closing the wall top over a plain opening that was cut
    through the full wall height (a level with nothing above it)."""
    from wenart.blender import common

    ceiling_style = style.get("ceiling") or {"material": "plaster_white"}
    mat = slot_material(library, ceiling_style)
    verts, faces = geom2d.polygon_face(
        G.rotated_rectangle(centre, (float(opening["width"]), float(wall["thickness"])), angle), z, facing_up=False)
    ob = common.new_mesh_object(f"{opening['id']}_soffit", verts, faces, collection=collection,
                                wenart_id=opening["id"], kind="ceiling", status=opening.get("status", "verified"),
                                materials=[mat])
    manifest_objects.append({
        "name": ob.name, "wenart_id": opening["id"], "kind": "ceiling", "status": opening.get("status", "verified"),
        "level_id": opening["level_id"], "element_id": opening["id"], "evidence": opening.get("evidence", []),
        "material": mat.name, "textured": library.textured(mat), "pass_index": None, "assumed": dict(op_assumed),
        "wall_id": opening.get("wall_id"), "room_type": None, "wet": False, "center_shift": round(shift, 4),
    })
    return ob


def _local_to_world(parts, origin, angle_deg):
    """Rotate box parts given in the opening's local frame (X along the wall,
    Y across, Z up from the opening bottom) into world space."""
    verts, faces = geom2d.merge(parts)
    rad = math.radians(angle_deg)
    c, s = math.cos(rad), math.sin(rad)
    world = [(origin[0] + c * x - s * y, origin[1] + s * x + c * y, origin[2] + z) for x, y, z in verts]
    return world, faces


# --------------------------------------------------------------------------
# Floors and ceilings
# --------------------------------------------------------------------------

def ceiling_faces(polygon, voids, ceil_z: float) -> tuple[list, list, list[int]]:
    """``(verts, faces, cut)`` of a room ceiling (pure): one n-gon facing down
    as before, or, when stair openings (``voids``: lists of polygons, one
    list per stair) cross the room, the room minus the openings
    (``geom2d.polygon_faces``); ``cut`` = the indices of the stairs whose
    opening took area from the room."""
    verts, faces = geom2d.polygon_face(polygon, ceil_z, facing_up=False)
    area = G.polygon_area([v[:2] for v in verts])
    holes, cut = [], []
    for i, loops in enumerate(voids):
        rest_v, rest_f = geom2d.polygon_faces(polygon, list(loops), ceil_z, facing_up=False)
        if geom2d.faces_area(rest_v, rest_f) < area - 1e-6:
            holes.extend(loops)
            cut.append(i)
    if not cut:
        return verts, faces, []
    verts, faces = geom2d.polygon_faces(polygon, holes, ceil_z, facing_up=False)
    return verts, faces, cut


def build_floors_ceilings(building: dict, level: dict, collection, library, style: dict,
                          manifest_objects: list, warnings: list, stairs: list | None = None,
                          whole: dict | None = None, assumed: list | None = None) -> list:
    """One floor face and one ceiling face per room, material per style and
    wet-room rule; unverified rooms get the dashed-red overlay on the floor.
    ``stairs`` (``plan_stairs``): their ceiling openings are cut out of the
    ceilings they cross (the shaft and cap come with ``build_stairs``).

    ``whole`` (Milestone 10): ``{"floor_voids": [polygons] (the openings of the slab under the level: cut out
    of its floors), "ceiling_voids": [polygons] or None (the openings of the slab above: cut out of the
    ceilings instead of the stairs' own openings), "ceiling_planes": [(a, b, c)] or None (the rooms under the
    roof: ceilings on the lowest of these planes, ``roof.ceiling_planes``), "open_rooms": {room ids} (roof
    terraces: no ceiling), "terrace_floor": the exterior ``paving`` look (the floor of the open rooms)}``.

    26 Oct 2026: the free edges of the floor openings get a guard (``build_void_guards``; ``assumed``, when given,
    gets its entries)."""
    from wenart.blender import common

    level_id = level["id"]
    floor_z = float(level["elevation"])
    ceil_z = floor_z + float(level["ceiling_height"])
    planned = [s for s in (stairs or []) if s.get("plan") is not None and s["plan"]["void"]]
    voids = [s["plan"]["void"] for s in planned]
    whole = whole or {}
    floor_voids = [v for v in whole.get("floor_voids") or [] if len(v) >= 3]
    slab_voids = whole.get("ceiling_voids")
    planes = whole.get("ceiling_planes")
    open_rooms = set(whole.get("open_rooms") or ())
    created = []
    for room in building["rooms"]:
        if room["level_id"] != level_id:
            continue
        # 30 Oct 2026 (UL159): a roof terrace and an outdoor room (balcony, loggia, ...) take the outdoor floor
        outside = room["id"] in open_rooms or str(room.get("room_type") or "") in OUTDOOR_FLOOR_ROOMS
        floor_mat, wet = floor_material(room, style, library, whole.get("terrace_floor") if outside else None)
        ceiling_style = style.get("ceiling") or {"material": "plaster_white"}
        ceil_mat = slot_material(library, ceiling_style)
        if len(room["polygon"]) < 3:
            warnings.append(f"{room['id']}: polygon with fewer than 3 points, no floor")
            continue
        rz = room_floor_z(room, level)           # Milestone 12: the room's own floor (floor_offset_m)
        fv, ff, fcut = ceiling_faces(room["polygon"], [[v] for v in floor_voids], rz)
        fv, ff = geom2d.polygon_face(room["polygon"], rz, facing_up=True) if not fcut else \
            geom2d.polygon_faces(room["polygon"], [floor_voids[i] for i in fcut], rz, facing_up=True)
        if not ff:
            warnings.append(f"{room['id']}: the stair opening covers the whole floor; no floor face")
            continue
        ob = common.new_mesh_object(f"{room['id']}_floor", fv, ff, collection=collection, wenart_id=room["id"],
                                    kind="floor", status=room.get("status", "verified"), materials=[floor_mat])
        created.append(ob)
        manifest_objects.append({
            "name": ob.name, "wenart_id": room["id"], "kind": "floor", "status": room.get("status", "verified"),
            "level_id": level_id, "element_id": room["id"], "evidence": room.get("evidence", []),
            "material": floor_mat.name, "textured": _textured(library, floor_mat),
            "pass_index": None, "assumed": {}, "room_type": room.get("room_type"), "wet": wet,
        })
        # 29 Oct 2026 (K11): a floor the family's kitchen rule chose is recorded with its reason
        k11 = floor_style(room, style)[0] if room["id"] not in open_rooms else {}
        if isinstance(k11, dict) and k11.get("reason"):
            manifest_objects[-1]["assumed"] = {"floor": k11["material"], "reason": k11["reason"]}
            if assumed is not None:
                assumed.append({"object": ob.name, "field": "floor", "value": k11["material"],
                                "reason": k11["reason"], "parent": room["id"], "kind": "floor"})
        if fcut:
            manifest_objects[-1]["stair_void"] = f"{len(fcut)} opening(s) of the slab under the level cut out"
        if abs(rz - floor_z) > 1e-9:
            manifest_objects[-1].update(floor_z=round(rz, 4), floor_offset_m=room.get("floor_offset_m"),
                                        floor_source=room.get("floor_source"))
        if room["id"] in open_rooms:
            manifest_objects[-1]["open_to_sky"] = True
            continue                          # a roof terrace: no ceiling
        room_voids = voids if slab_voids is None else [[v] for v in slab_voids if len(v) >= 3]
        if planes:
            holes = []
            for i, loops in enumerate(room_voids):
                _rv, _rf, c = ceiling_faces(room["polygon"], [loops], ceil_z)
                if c:
                    holes.extend(loops)
            # 31 Oct 2026 (user on real04 run 20261030-181158-full: "the door the toilet not making sense at all"): a
            # dormer's ceiling over a drawn door stands in the room's sloped ceiling (dormers.room_ceiling; the step
            # up to it is the dormer cheek's inner face)
            from wenart.blender import dormers as DM
            cv, cf = DM.room_ceiling(room["polygon"], holes, planes, whole.get("ceiling_dormers"))
            cut = [0] if holes else []
        else:
            cv, cf, cut = ceiling_faces(room["polygon"], room_voids, ceil_z)
        if not cf:
            warnings.append(f"{room['id']}: the stair opening covers the whole ceiling; no ceiling face")
            continue
        ob = common.new_mesh_object(f"{room['id']}_ceiling", cv, cf, collection=collection, wenart_id=room["id"],
                                    kind="ceiling", status=room.get("status", "verified"), materials=[ceil_mat])
        created.append(ob)
        entry = {
            "name": ob.name, "wenart_id": room["id"], "kind": "ceiling", "status": room.get("status", "verified"),
            "level_id": level_id, "element_id": room["id"], "evidence": room.get("evidence", []),
            "material": ceil_mat.name, "textured": _textured(library, ceil_mat),
            "pass_index": None, "assumed": {}, "room_type": room.get("room_type"), "wet": wet,
        }
        if planes:
            entry["sloped"] = "under the roof: the roof underside and the level's flat ceiling, the lower one"
            raised = [r["id"] for r in whole.get("ceiling_dormers") or []
                      if G.polygon_area(geom2d.clip_convex(room["polygon"], r["polygon"]) or [(0, 0)] * 3) > 1e-4]
            if raised:
                entry["dormers"] = raised
        if cut and slab_voids is None and not planes:
            ids = [planned[i]["piece"]["id"] for i in cut]
            entry["stair_void"] = ids
            entry["assumed"]["stair_void"] = f"ceiling opening of {', '.join(ids)} cut out (assumed)"
        elif cut:
            entry["stair_void"] = "the opening(s) of the slab above cut out" if slab_voids is not None \
                else "the stairs' openings cut out"
        manifest_objects.append(entry)
    if floor_voids:
        # 26 Oct 2026 (user on real06: "an unguarded stair void at the upper landing"): a guard on the free edges
        created += build_void_guards(building, level, collection, library, style, manifest_objects, floor_voids,
                                     assumed)
    return created


# --------------------------------------------------------------------------
# Guards around the floor openings (26 Oct 2026, user on real06: "an unguarded stair void at the upper landing";
# "The house needs to make sense and needs to look very stylish")
# --------------------------------------------------------------------------

VOID_ARRIVAL_NEAR_M = 0.30        # a stair's top line this near a floor opening comes up through it


def level_below(building: dict, level: dict) -> dict | None:
    """The level directly under ``level`` (the highest elevation below it), None for the lowest."""
    z = float(level["elevation"])
    under = [lv for lv in building.get("levels") or [] if float(lv["elevation"]) < z - 1e-6]
    return max(under, key=lambda lv: float(lv["elevation"])) if under else None


def stair_arrival_edges(building: dict, level: dict) -> list[dict]:
    """Where the stairs of the level below come up through the floor of ``level`` (pure): per stair planned there
    (``plan_stairs`` with the slab's opening), the top line of its last flight across its drawn width (its last
    nosing: the last riser rises to this floor; past its apron, ``top_apron``, when it has one), and, for a landing
    at the top (at this floor's height), every edge of that landing. ``[{"stair": piece id, "p", "q"}]``."""
    below = level_below(building, level)
    if below is None:
        return []
    out = []
    try:
        items = plan_stairs(building, below, slab_void=True)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return []
    for item in items:
        plan = item.get("plan")
        if not plan or not plan.get("flights"):
            continue
        sid = item["piece"]["id"]
        f = plan["flights"][-1]
        r = f["rise_dir"]
        apron = float(plan.get("top_apron") or 0.0)
        c = (f["nosings"][-1][0] + r[0] * apron, f["nosings"][-1][1] + r[1] * apron)
        hw = float(f["width"]) / 2.0
        p = (-r[1], r[0])
        out.append({"stair": sid, "p": (c[0] - p[0] * hw, c[1] - p[1] * hw), "q": (c[0] + p[0] * hw, c[1] + p[1] * hw)})
        landing = plan.get("landing")
        if landing is not None and landing.get("role") == "top":
            poly = geom2d.ccw(landing["polygon"])
            out += [{"stair": sid, "p": poly[k], "q": poly[(k + 1) % len(poly)]} for k in range(len(poly))]
    return out


# 30 Oct 2026 (lesson UL192): a floor opening's guard keeps this far out of the footprint of a stair of its own level
OWN_STAIR_MARGIN_M = 0.05


def own_stair_footprints(building: dict, level: dict) -> list[list[tuple[float, float]]]:
    """The footprints of the stairs the level builds (``plan_stairs`` items with a plan; pure; UL192), each grown by
    ``OWN_STAIR_MARGIN_M``: a floor opening's guard runs nowhere inside them (the stair's own balustrades guard its
    flights and its well). The drawn upper end of the stair below (no plan) is not one: its opening keeps its guard."""
    out = []
    for item in plan_stairs(building, level):
        fp = item["piece"].get("footprint") or {}
        if item.get("plan") is None or len(fp.get("size") or ()) < 2:
            continue
        grown = dict(fp, size=[float(s) + 2.0 * OWN_STAIR_MARGIN_M for s in fp["size"][:2]])
        rect = _footprint_polygon({"footprint": grown})
        if rect:
            out.append(rect)
    return out


def floor_void_guards(building: dict, level: dict, voids: list) -> list[dict]:
    """The guards around the openings of the floor of ``level`` (pure; the plan ``build_void_guards`` builds and the
    architect's K2 / K3 can count): per opening with a free edge ``{"void": its index, "polygon", "runs": [(p, q)]
    (``details.void_guard_runs`` with the level's walls and the arrival lines of the stairs that come up through it,
    ``stair_arrival_edges``), "arrivals": [(p, q)], "arrives_from": [stair ids], "length_m", "keep_out"}``; 30 Oct
    2026 (UL192): no run inside the footprint of a stair of the level (``own_stair_footprints``)."""
    walls = [w for w in building.get("walls") or [] if w.get("level_id") == level["id"]]
    arrivals = stair_arrival_edges(building, level)
    keep_out = own_stair_footprints(building, level)
    out = []
    for i, void in enumerate(voids or []):
        if len(void or []) < 3:
            continue
        poly = geom2d.ccw(void)
        mine = [a for a in arrivals
                if G.point_in_polygon(G.segment_midpoint(a["p"], a["q"]), poly)
                or geom2d.distance_to_polygon_edges(G.segment_midpoint(a["p"], a["q"]), poly) <= VOID_ARRIVAL_NEAR_M]
        lines = [(a["p"], a["q"]) for a in mine]
        runs = D.void_guard_runs(poly, walls, lines, keep_out=keep_out)
        if not runs:
            continue
        out.append({"void": i, "polygon": [tuple(p) for p in poly], "runs": runs, "arrivals": lines,
                    "arrives_from": sorted({a["stair"] for a in mine}),
                    "length_m": round(sum(G.distance(p, q) for p, q in runs), 3), "keep_out": keep_out})
    return out


def build_void_guards(building: dict, level: dict, collection, library, style: dict, manifest_objects: list,
                      voids: list, assumed: list | None = None) -> list:
    """One balustrade object per floor opening with free edges (``floor_void_guards``): ``void_guard_<level>_<i>``,
    kind ``railing``, status ``assumed``, the stair's materials (steel, thin glass) and the house's balustrade kind
    (``details.balustrade_kind``: K3, one language with the stairs, balconies and terraces), ``details.GUARD``
    height on the floor around the opening. The manifest entry records ``assumed.detail`` ``void_guard``, the height,
    the kind, the runs and the stairs that arrive; the stair of the level below gets ``stair.void_guard``."""
    from wenart.blender import common

    plans = floor_void_guards(building, level, voids)
    if not plans:
        return []
    kind = D.balustrade_kind(style)
    steel = library.get("steel_brushed")
    glass = library.thin_glass()
    walls = [w for w in building.get("walls") or [] if w.get("level_id") == level["id"]]
    rooms = [r for r in building["rooms"] if r["level_id"] == level["id"] and len(r.get("polygon") or []) >= 3]
    created = []
    for g in plans:
        p, q = g["runs"][0]
        mid = G.segment_midpoint(p, q)
        room = next((r for r in rooms if G.point_in_polygon(mid, r["polygon"])), None)
        z = room_floor_z(room, level) if room is not None else float(level["elevation"])
        metal, panes, _runs = D.void_guards(g["polygon"], walls, g["arrivals"], z, kind, keep_out=g["keep_out"])
        verts, faces = geom2d.merge(metal + panes)
        if not faces:
            continue
        slots = [0] * sum(len(f) for _v, f in metal) + [1] * sum(len(f) for _v, f in panes)
        name = f"void_guard_{level['id']}_{g['void']}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="railing",
                                    status="assumed", materials=[steel, glass], face_material_indices=slots)
        ob.pass_index = 0
        created.append(ob)
        stairs = ", ".join(g["arrives_from"]) or "no stair"
        parent = room["id"] if room is not None else level["id"]
        reason = (f"floor opening {g['void']} of {level['id']} ({stairs} comes up through it): a "
                  f"{D.GUARD['height']:.2f} m {kind.replace('_', ' ')} balustrade on its {len(g['runs'])} free "
                  f"edge(s), {g['length_m']:.2f} m (not drawn: assumed; the kind follows the style, as the stair's)")
        manifest_objects.append({
            "name": ob.name, "wenart_id": name, "kind": "railing", "status": "assumed", "level_id": level["id"],
            "element_id": name, "parent": parent, "evidence": [], "material": steel.name, "textured": False,
            "pass_index": 0,
            "assumed": {"detail": "void_guard", "height_m": D.GUARD["height"], "balustrade": kind,
                        "edges": len(g["runs"]), "length_m": g["length_m"], "arrives_from": g["arrives_from"],
                        "runs": [[[round(x, 4), round(y, 4)] for x, y in run] for run in g["runs"]],
                        "reason": reason},
        })
        if assumed is not None:
            assumed.append({"object": ob.name, "field": "void_guard", "value": D.GUARD["height"], "reason": reason,
                            "parent": parent, "kind": "railing"})
        for e in manifest_objects:
            if isinstance(e.get("stair"), dict) and e.get("wenart_id") in g["arrives_from"]:
                e["stair"]["void_guard"] = name
    return created


def build_skirting(building: dict, level: dict, collection, library, style: dict, manifest_objects: list,
                   assumed: list) -> list:
    """A painted skirting board (``SKIRTING_H`` x ``SKIRTING_T``, the trim
    material) along the walls of every dry room of the level (not bathroom,
    WC, kitchen or balcony), interrupted at its doors, plain openings and
    windows that reach below the board (``skirting_spans``). One object per
    room (``skirting_<room id>``, kind wall, pass index 0, status assumed)
    and one ``assumed`` entry with the room as ``parent``."""
    from wenart.blender import common
    from wenart.blender.cameras import room_openings

    floor_z = float(level["elevation"])
    has_above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
    trim = style.get("trim") or {"material": "painted_wood_white"}
    mat = slot_material(library, trim)
    reason = "design detail of the room's documented walls (painted skirting board); not in the documents"
    created = []
    for room in building["rooms"]:
        if room["level_id"] != level["id"] or slot_room_type(room.get("room_type")) in NO_SKIRTING_TYPES:
            continue
        polygon = [tuple(p[:2]) for p in room["polygon"]]
        if len(polygon) > 1 and G.distance(polygon[0], polygon[-1]) < 1e-9:
            polygon = polygon[:-1]
        if len(polygon) < 3:
            continue
        gaps = skirting_gaps(room_openings(room, polygon, building), level, has_above)
        spans = skirting_spans(polygon, gaps)
        if not spans:
            continue
        verts, faces = skirting_boxes(polygon, spans, room_floor_z(room, level))   # M12: the room floor
        name = f"skirting_{room['id']}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="wall",
                                    status="assumed", materials=[mat])
        ob.pass_index = 0
        created.append(ob)
        length = round(sum(s1 - s0 for _, s0, s1 in spans), 3)
        manifest_objects.append({
            "name": ob.name, "wenart_id": name, "kind": "wall", "status": "assumed", "level_id": level["id"],
            "element_id": room["id"], "parent": room["id"], "evidence": [], "material": mat.name,
            "textured": library.textured(mat), "pass_index": 0,
            "assumed": {"detail": "skirting", "size_m": [SKIRTING_H, SKIRTING_T], "length_m": length,
                        "runs": len(spans), "reason": reason},
        })
        assumed.append({"object": ob.name, "field": "skirting",
                        "value": f"{SKIRTING_H * 100:g} cm x {SKIRTING_T * 1000:g} mm, {length} m in {len(spans)} runs",
                        "reason": reason, "parent": room["id"], "kind": "skirting"})
    return created


# --------------------------------------------------------------------------
# Stairs (Milestone 7, docs/milestone7.md §6.4): fixed equipment, built with the shell
# --------------------------------------------------------------------------

STAIR_NOT_BUILT_REASON = "build false: kept in the building, not built"
STAIR_METHOD = "parametric (fixed equipment: the drawn flights and landing)"
STAIR_METHOD_GENERIC = "parametric (fixed equipment: one assumed flight, no drawn flights)"
# Above the level the shaft cap stays this far under the next floor (no coplanar faces with it); a stair on the
# top level of a whole building stops this far under the roof underside (Milestone 10).
STAIR_UPPER_FLOOR_GAP = 0.005
# Milestone 10: a stair on the top level whose footprint covers at least this share of the smaller of its own and
# a stair footprint of the level below is the drawn upper end of that stair (``stair_arrival``).
STAIR_ARRIVAL_SHARE = 0.5
# Milestone 10: a stair on the top level with less room than this under the roof (two of the lowest risers) is
# not built (a warning, needs review).
STAIR_MIN_RISE_M = 2 * P.STAIR_RISER_RANGE[0]


def stair_rise(building: dict, level: dict) -> tuple[float, float, str, str | None]:
    """``(rise, cap_height, riser_source, warning)`` of the stairs of a level
    (pure, metres above its floor): with nothing above, the ceiling height +
    the assumed ``STAIR_SLAB_M`` and the cap ``STAIR_SHAFT_CAP_M`` above the
    ceiling; with a level above, floor to floor and the cap just under its
    floor (whose own floor is not cut: a warning says so). The top level of a
    whole building (Milestone 10) does not use this rise: ``plan_stairs``
    reads its stairs as the upper end of the stair below or stops them under
    the roof (``top_level_stair``)."""
    floor_z = float(level["elevation"])
    ceiling = float(level["ceiling_height"])
    above = sorted(float(lv["elevation"]) for lv in building["levels"] if float(lv["elevation"]) > floor_z + 1e-6)
    if above:
        rise = above[0] - floor_z
        cap = min(ceiling + P.STAIR_SHAFT_CAP_M, rise - STAIR_UPPER_FLOOR_GAP)
        return rise, cap, "derived from the level elevations (floor to floor)", \
            "the floor of the level above is not cut; the stair opening is capped under it"
    if level.get("ceiling_height_source") == "assumed_default":
        source = P.STAIR_RISER_SOURCE
    else:
        source = "derived from the documented ceiling and assumed slab"
    return ceiling + P.STAIR_SLAB_M, ceiling + P.STAIR_SHAFT_CAP_M, source, None


def plan_stairs(building: dict, level: dict, slab_void: bool = False) -> list[dict]:
    """The stairs of a level (pure): ``[{"piece", "plan", "reason"}]`` with
    ``plan = parametric.stair_plan(...)`` (rise from ``stair_rise``, the
    level's walls for the handrail sides), or ``plan: None`` and the reason
    for a piece with ``build: false``. Site elements are never read.
    ``slab_void`` (Milestone 10): the slab above carries the opening and the
    floor above is cut, so the stair arrives there (no capped-shaft warning).

    Milestone 10, the top level of a whole building (no level above it,
    ``build.is_whole_building``): ``top_level_stair`` instead. A stair over a
    stair of the level below is that stair's drawn upper end (``plan: None``,
    ``arrival``: ``stair_arrival``; no second flight, no ceiling opening, no
    shaft; the floor keeps the slab's opening); any other stops under the roof
    underside (rise = ceiling = cap: no opening, no shaft through the roof;
    assumed and a warning). Items may carry ``arrival`` and ``warnings``
    (for ``build_stairs``). Pre-M10 buildings keep the M7 rise."""
    walls = [w for w in building["walls"] if w["level_id"] == level["id"]]
    rise, cap, source, warning = stair_rise(building, level)
    if slab_void:
        warning = None
    top_of_whole = whole_building(building) and is_top_level(building, level)
    out = []
    for piece in building.get("furniture") or []:
        if piece.get("level_id") != level["id"] or piece.get("type") not in P.SHELL_TYPES:
            continue
        if piece.get("build", True) is False:
            out.append({"piece": piece, "plan": None, "reason": STAIR_NOT_BUILT_REASON})
            continue
        if top_of_whole:
            out.append(top_level_stair(building, level, piece, walls))
            continue
        plan = P.stair_plan(piece, rise, float(level["ceiling_height"]), cap, walls, source)
        if warning:
            plan["warnings"].append(warning)
        if slab_void:
            # 26 Oct 2026 (user on real06: "an unguarded stair void"): the stair comes up through the opening of the
            # floor above, so its balustrade runs to the top (``parametric.stair_parts``), not cut under the slab,
            # and a drawn opening that goes on past its top step gets an apron there (``parametric.arrival_apron``)
            plan["rail_limit"] = rise + P.STAIR_RAIL_HEIGHT + P.STAIR_CAP_CLEARANCE
            apron = P.arrival_apron(plan, slab_openings_above(building, level))
            if apron > 0.0:
                plan["top_apron"] = round(apron, 4)
                plan["assumed"].append({"field": "top_apron", "kind": "stair_apron", "value": round(apron, 4),
                                        "reason": f"the floor's drawn opening goes on {apron:.2f} m past the top "
                                                  f"step: an apron in the tread finish meets the floor's edge (not "
                                                  f"drawn: assumed)"})
        out.append({"piece": piece, "plan": plan, "reason": None})
    return out


def slab_openings_above(building: dict, level: dict) -> list:
    """The drawn openings of the slab directly above ``level`` (the building's ``slabs`` entry of the next level up;
    pure; 26 Oct 2026), counter-clockwise polygons; [] when none is drawn (the slab plan then cuts the stair's own
    opening, which ends at the top step)."""
    z = float(level["elevation"])
    above = [lv for lv in building.get("levels") or [] if float(lv["elevation"]) > z + 1e-6]
    if not above:
        return []
    up = min(above, key=lambda lv: float(lv["elevation"]))
    slab = next((s for s in building.get("slabs") or [] if isinstance(s, dict) and s.get("above_level_id") == up["id"]),
                None)
    return [geom2d.ccw(o["polygon"]) for o in (slab or {}).get("openings") or []
            if isinstance(o, dict) and len(o.get("polygon") or []) >= 3]


def whole_building(building: dict) -> bool:
    """``build.is_whole_building`` (pure; build imports this module): Milestone 10, a building with slabs, a roof
    or variants."""
    return bool(building.get("slabs") or isinstance(building.get("roof"), dict) or building.get("variants"))


def is_top_level(building: dict, level: dict) -> bool:
    """True when no level of ``building`` lies above ``level`` (pure; the test of ``stair_rise``)."""
    z = float(level["elevation"])
    return not any(float(lv["elevation"]) > z + 1e-6 for lv in building.get("levels") or [])


def _footprint_polygon(piece: dict) -> list[tuple[float, float]]:
    """The footprint rectangle of a piece, counter-clockwise ([] without a usable footprint)."""
    fp = piece.get("footprint") or {}
    try:
        rect = G.rotated_rectangle(fp["center"], fp["size"], float(fp.get("rotation_deg") or 0.0))
    except (KeyError, TypeError, ValueError, IndexError):
        return []
    rect = geom2d.ccw(rect)
    return rect if len(rect) >= 3 and G.polygon_area(rect) > 1e-9 else []


def stair_arrival(building: dict, level: dict, piece: dict) -> dict | None:
    """The stair of the level below whose drawn upper end ``piece`` is (pure; Milestone 10), or None.

    Only in a whole building (``whole_building``) on a level with no level above it: a plan cut above a stair
    shows its flights from above, the same block at the same place as on the plan below (real02's attic,
    synthetic-07's MERDIVEN on every plan; ``sheets_report.md``: "stairs aligned"). It is when the piece's
    footprint covers at least ``STAIR_ARRIVAL_SHARE`` of the smaller of its own and the footprint of a built
    stair (``parametric.SHELL_TYPES``) of the level(s) directly below (the highest elevation under it); the
    largest share wins. ``{"from": that stair's id, "from_level", "share", "opening": the id of the opening of
    the building's slab under ``level`` drawn for it (``furniture_id``, else the first one over its footprint)
    or None, "slabs": True when the building has slabs (``slab_plan`` then cuts an opening over it)}``."""
    levels = building.get("levels") or []
    if not whole_building(building) or not is_top_level(building, level):
        return None
    z = float(level["elevation"])
    under = [float(lv["elevation"]) for lv in levels if float(lv["elevation"]) < z - 1e-6]
    mine = _footprint_polygon(piece)
    if not under or not mine:
        return None
    zb = max(under)
    below = {lv["id"] for lv in levels if abs(float(lv["elevation"]) - zb) <= 1e-6}
    best = None
    for q in building.get("furniture") or []:
        if q.get("type") not in P.SHELL_TYPES or q.get("level_id") not in below or q.get("build", True) is False:
            continue
        theirs = _footprint_polygon(q)
        if not theirs:
            continue
        share = _shared_area(mine, theirs) / min(G.polygon_area(mine), G.polygon_area(theirs))
        if share >= STAIR_ARRIVAL_SHARE - 1e-9 and (best is None or share > best[0] + 1e-9):
            best = (min(1.0, share), q, theirs)
    if best is None:
        return None
    share, q, theirs = best
    slab = next((s for s in building.get("slabs") or []
                 if isinstance(s, dict) and s.get("above_level_id") == level["id"]), None)
    openings = [o for o in (slab or {}).get("openings") or [] if isinstance(o, dict)]
    opening = next((o.get("id") for o in openings if o.get("furniture_id") == q["id"]), None)
    if opening is None:
        opening = next((o.get("id") for o in openings if len(o.get("polygon") or []) >= 3
                        and _overlap(theirs, geom2d.ccw(o["polygon"]))), None)
    return {"from": q["id"], "from_level": q["level_id"], "share": round(share, 3), "opening": opening,
            "slabs": bool(building.get("slabs"))}


def top_level_stair(building: dict, level: dict, piece: dict, walls: list[dict]) -> dict:
    """The ``plan_stairs`` item of a stair on the top level of a whole building (pure; Milestone 10). Nothing
    lies above it, so it never rises to a floor above or through the roof:

    - over a stair of the level below (``stair_arrival``): that stair's drawn upper end. ``plan: None``,
      ``arrival``; not built (the stair below arrives through the slab opening, which the floor keeps); a
      warning when the building has no slabs (the floor is not cut);
    - else (a stair that goes up, the access to the roof space is not drawn): it stops ``STAIR_UPPER_FLOOR_GAP``
      under the lowest roof underside over its footprint (``level["ceiling_planes"]``, set by
      ``build.prepare``; without them the level's ceiling): rise = ceiling = cap, so no ceiling opening and no
      shaft; the top is assumed (kind ``stair_top``) and a warning says so. With less than
      ``STAIR_MIN_RISE_M`` of room it is not built (a warning)."""
    arr = stair_arrival(building, level, piece)
    if arr is not None:
        warnings = [] if arr["slabs"] else [
            f"arrives from {arr['from']}, but the building has no slabs: the floor of {level['id']} is not cut over it"]
        return {"piece": piece, "plan": None, "arrival": arr, "warnings": warnings,
                "reason": f"arrives from {arr['from']} ({arr['from_level']} -> {level['id']}): the drawn upper end "
                          f"of that stair; no level above, not built again"}
    floor_z = float(level["elevation"])
    planes = level.get("ceiling_planes")
    mine = _footprint_polygon(piece)
    if planes:
        corners = mine or [tuple(piece["footprint"]["center"])]
        # 31 Oct 2026: a dormer over it raises the ceiling (level ``ceiling_dormers``, dormers.py)
        under, what = min(geom2d.level_ceiling_z(level, x, y) for x, y in corners) - floor_z, "the roof underside"
    else:
        under, what = float(level["ceiling_height"]), "the ceiling"
    top = under - STAIR_UPPER_FLOOR_GAP
    why = "on the top level with no level above and not over a stair of the level below"
    roof = building.get("roof") if isinstance(building.get("roof"), dict) else {}
    terraces = [str(o.get("id") or o.get("room_id")) for o in roof.get("openings") or []
                if isinstance(o, dict) and len(o.get("polygon") or []) >= 3 and mine
                and _overlap(mine, geom2d.ccw(o["polygon"]))]
    extra = [f"it reaches into the roof opening {', '.join(terraces)}: it may lead out onto the roof (needs review)"] \
        if terraces else []
    if top < STAIR_MIN_RISE_M:
        headroom = (f"{why}: {what} lies {under:.2f} m above the floor over its footprint, no room for a flight; "
                    f"not built (needs review)")
        return {"piece": piece, "plan": None, "arrival": None,
                "reason": f"{why}: no headroom under {what} over its footprint (needs review)",
                "warnings": [headroom, *extra]}
    plan = P.stair_plan(piece, top, top, top, walls, f"limited by {what} (no level above, assumed)")
    plan["notes"] = [n.replace("under the shaft cap", f"under {what}") for n in plan["notes"]]
    plan["assumed"].append({"field": "rise_m", "kind": "stair_top", "value": round(top, 4),
                            "reason": f"{why}: the stair stops under {what}; no roof opening is drawn, none is cut"})
    plan["warnings"].append(f"{why}: stops {top:.2f} m above the floor under {what}; the roof access is not drawn "
                            f"(needs review)")
    plan["warnings"].extend(extra)
    return {"piece": piece, "plan": plan, "arrival": None, "reason": None}


# Fix round after P4b (17 Oct 2026; pod P4b, real03's fire stair yangin_merdiveni_3): the drawn U-stair is exactly
# as wide as its 2.6 m stairwell, but its centre was read 0.9 mm off (8.403 vs 8.4039), so the right flight and the
# landing stopped 0.9 mm short of the wall face and the rig light above came through as a vertical slit down the wall.
# A flight side or a landing edge within STAIR_JOINT_SNAP_M of a parallel wall face (the wall beside it over at least
# STAIR_JOINT_OVERLAP of its length) now meets the wall, STAIR_JOINT_EMBED_M into it, as two walls meet at a joint.
# The drawn footprint stays in the building JSON; the mesh widens by at most SNAP + EMBED and the build lists it.
STAIR_JOINT_SNAP_M = 0.05
STAIR_JOINT_EMBED_M = 0.01
STAIR_JOINT_OVERLAP = 0.5
STAIR_JOINT_PARALLEL_DEG = 2.0
# The stair's structure (the stringer sides, the soffit and the landing edge): the wall colour as a smooth paint, not
# the wall's texture set. P4b: the plastered_wall set's bump, at wall scale, showed as large bumps on the 0.6 m stringer
# face seen up close under the flight (M11's flat paint was smooth).
STAIR_STRUCTURE_REASON = "stair structure: the wall colour as a smooth paint (no wall texture set: its bump at wall " \
                         "scale reads as coarse plaster on the stringer seen up close)"
# pass before P5 (module docstring): the slug of the structure when the walls' slug has a shell stand-in set
STAIR_STRUCTURE_PAINT = "paint"


def _wall_gap(a, b, normal, walls) -> list[tuple[float, dict]]:
    """``[(gap, wall)]``: the walls parallel to the segment ``a``-``b`` on the side of the unit ``normal`` whose
    near face lies ``gap`` metres out from the segment (negative: the segment is inside the wall), with their axis
    beside at least ``STAIR_JOINT_OVERLAP`` of the segment's length (pure)."""
    length = G.distance(a, b)
    if length < 1e-9:
        return []
    u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
    out = []
    for w in walls:
        ws, we = w["start"], w["end"]
        wl = G.distance(ws, we)
        if wl < 1e-9:
            continue
        wu = ((we[0] - ws[0]) / wl, (we[1] - ws[1]) / wl)
        if abs(u[0] * wu[1] - u[1] * wu[0]) > math.sin(math.radians(STAIR_JOINT_PARALLEL_DEG)):
            continue
        q = ((ws[0] - a[0]) * normal[0] + (ws[1] - a[1]) * normal[1]
             + (we[0] - a[0]) * normal[0] + (we[1] - a[1]) * normal[1]) / 2.0
        if q <= 0.0:
            continue                                              # the wall's axis lies on the other side
        t0 = (ws[0] - a[0]) * u[0] + (ws[1] - a[1]) * u[1]
        t1 = (we[0] - a[0]) * u[0] + (we[1] - a[1]) * u[1]
        overlap = min(max(t0, t1), length) - max(min(t0, t1), 0.0)
        if overlap < STAIR_JOINT_OVERLAP * length:
            continue
        out.append((q - float(w["thickness"]) / 2.0, w))
    return out


def stair_wall_joints(plan: dict, walls: list[dict]) -> list[dict]:
    """Close the gaps between a planned stair and the walls beside it (pure; fix round after P4b, 17 Oct 2026, see
    ``STAIR_JOINT_SNAP_M``). Every flight side (left / right of its rise direction, along its steps) and every edge
    of a ``mid`` / ``top`` landing whose nearest parallel wall face lies between ``-STAIR_JOINT_EMBED_M`` and
    ``STAIR_JOINT_SNAP_M`` out gets ``extend_m`` = that gap + ``STAIR_JOINT_EMBED_M`` (it ends ``EMBED`` inside the
    wall). Sets ``plan["wall_joints"]``: ``[{"part": "flight" | "landing", "flight" | "edge", "side", "wall_id",
    "gap_m", "extend_m"}]`` (``parametric.stair_parts`` widens the steps, the riser plates and the landing by it) and,
    when there is one, appends a ``stair_wall_joint`` assumed entry. Returns the joints."""
    joints = []
    for f in plan.get("flights") or []:
        r = f["rise_dir"]
        p = (-r[1], r[0])
        hw = float(f["width"]) / 2.0
        o = f["nosings"][0]
        sn = (int(f["lines"]) - 1) * float(f["going"])
        if sn <= 1e-6:
            continue
        for side, sgn in (("left", 1.0), ("right", -1.0)):
            nrm = (p[0] * sgn, p[1] * sgn)
            a = (o[0] + nrm[0] * hw, o[1] + nrm[1] * hw)
            b = (a[0] + r[0] * sn, a[1] + r[1] * sn)
            gaps = [(g, w) for g, w in _wall_gap(a, b, nrm, walls) if -STAIR_JOINT_EMBED_M < g <= STAIR_JOINT_SNAP_M]
            if gaps:
                g, w = min(gaps, key=lambda x: x[0])
                joints.append({"part": "flight", "flight": f["index"], "side": side, "wall_id": w.get("id"),
                               "gap_m": round(g, 4), "extend_m": round(g + STAIR_JOINT_EMBED_M, 4)})
    landing = plan.get("landing")
    if landing is not None and landing.get("role") in ("mid", "top"):
        poly = geom2d.ccw(landing["polygon"])
        n = len(poly)
        for k in range(n):
            a, b = poly[k], poly[(k + 1) % n]
            length = G.distance(a, b)
            if length < 1e-9:
                continue
            nrm = ((b[1] - a[1]) / length, -(b[0] - a[0]) / length)       # outward of a counter-clockwise polygon
            gaps = [(g, w) for g, w in _wall_gap(a, b, nrm, walls) if -STAIR_JOINT_EMBED_M < g <= STAIR_JOINT_SNAP_M]
            if gaps:
                g, w = min(gaps, key=lambda x: x[0])
                joints.append({"part": "landing", "edge": k, "side": "edge", "wall_id": w.get("id"),
                               "gap_m": round(g, 4), "extend_m": round(g + STAIR_JOINT_EMBED_M, 4)})
    plan["wall_joints"] = joints
    if joints:
        what = "; ".join(f"{'flight ' + str(j['flight'] + 1) + ' ' + j['side'] if j['part'] == 'flight' else 'landing'}"
                         f" to {j['wall_id']} (gap {j['gap_m'] * 1000:.1f} mm)" for j in joints)
        plan["assumed"].append({"field": "wall_joint", "kind": "stair_wall_joint",
                                "value": f"{len(joints)} side(s) meet the wall {STAIR_JOINT_EMBED_M * 100:.0f} cm "
                                         f"into it: {what}",
                                "reason": f"a flight side or landing edge within {STAIR_JOINT_SNAP_M * 100:.0f} cm of "
                                          f"a wall face meets it (a gap lets the light through as a slit); the drawn "
                                          f"footprint is kept"})
    return joints


def stair_build_plan(plan: dict, walls: list[dict]) -> dict:
    """The plan ``build_stairs`` builds (pure; fix round after P4b): a copy of ``plan`` (its ``assumed`` list copied
    too) with ``stair_wall_joints`` on the level's ``walls``. ``plan_stairs`` and ``parametric.stair_plan`` keep their
    plan as it was (the camera search, the slab voids and the lights read it)."""
    out = dict(plan, assumed=list(plan.get("assumed") or []))
    stair_wall_joints(out, walls)
    return out


def stair_under_plan(plan: dict, walls: list[dict], voids=()) -> dict:
    """The space under a planned stair closed where it is low and its landing carried (pure; 27 Oct 2026, user on
    real06's ground floor: "This stairs not making any sense": loose slabs seen from below): ``plan["under"]`` =
    ``stair_access.under_stair`` on the level's ``walls`` (the spandrel panels and the posts ``parametric.stair_parts``
    builds) and, when there is something to build, one ``stair_under`` assumed entry. Returns the record. 28 Oct
    2026: ``voids`` (the floor openings of the level) carry no panel and no post (the stair stands free there)."""
    from wenart.blender import stair_access as SA
    try:
        under = SA.under_stair(plan, walls, voids)
    except ImportError:                     # 27 Oct 2026: no shapely in this Python (Blender before pod_setup's step)
        return None
    plan["under"] = under
    if under["panels"] or under["posts"]:
        plan["assumed"] = list(plan.get("assumed") or []) + [
            {"field": "under", "kind": "stair_under", "value": f"{len(under['panels'])} spandrel panel(s), "
                                                               f"{len(under['posts'])} post(s)",
             "reason": under["reason"]}]
    return under


# 29 Oct 2026 (lessons UL113, UL115; docs/reference_details_20261029.md H8: "a stair with oak treads, white risers and a
# black wall-mounted handrail"): the stair's finishes follow the family: the steel of its rails and strings black in the
# modern families (powder-coated), oak treads where the room's floor is not wood in the families that build timber
# treads (the risers keep the walls' paint)
STAIR_BLACK_METAL_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "industrial")
STAIR_WOOD_TREAD_FAMILIES: tuple[str, ...] = ("modern", "contemporary", "modern minimal", "minimal", "scandinavian",
                                              "japandi", "rustic", "classic")


def stair_finishes(style: dict | None, tread_slot: dict | None) -> tuple[dict | None, str, str]:
    """``(tread slot or None to keep the floor's, metal slug, why)`` of a stair by the house's family (pure; H8)."""
    fam = str((style or {}).get("family") or "").lower()
    metal = "metal_black" if fam in STAIR_BLACK_METAL_FAMILIES else "steel_brushed"
    why = [f"{'black' if metal == 'metal_black' else 'brushed steel'} rails and strings ({fam or 'house'} family)"]
    tread = None
    slug = str((tread_slot or {}).get("material") or "")
    if fam in STAIR_WOOD_TREAD_FAMILIES and slug and not slug.startswith("wood") and "parquet" not in slug:
        tread = stair_timber_slot(style)
        why.append(f"timber treads over the {slug.replace('_', ' ')} floor (H8)")
    return tread, metal, "; ".join(why)


def stair_timber_slot(style: dict | None) -> dict:
    """The timber of a stair (pure; 28 Oct 2026): the style's door slot when it is a wood (``wood_*``: the house's
    joinery), else ``wood_oak_light``."""
    door = (style or {}).get("door") if isinstance((style or {}).get("door"), dict) else {}
    if str(door.get("material") or "").startswith("wood"):
        return {k: v for k, v in door.items() if k in ("material", "asset", "colour", "tint", "params")}
    return {"material": "wood_oak_light"}


def level_above(building: dict, level: dict) -> dict | None:
    """The level directly over ``level`` (the lowest elevation above it), None for the highest."""
    z = float(level["elevation"])
    over = [lv for lv in building.get("levels") or [] if float(lv["elevation"]) > z + 1e-6]
    return min(over, key=lambda lv: float(lv["elevation"])) if over else None


def upper_wall_rects(building: dict, up: dict | None, plan: dict) -> list:
    """The wall rectangles of the level ``up`` near a planned stair (pure; 28 Oct 2026: a wall handrail goes on up
    where its wall goes on, ``stair_rails.cap_at``); [] without a level above."""
    from wenart.blender import stair_rails as SR
    if up is None:
        return []
    near = [p for f in plan.get("flights") or [] for p in f["nosings"]] + \
        list((plan.get("landing") or {}).get("polygon") or [])
    return SR.wall_rects_near(near, [w for w in building.get("walls") or [] if w.get("level_id") == up["id"]])


def stair_guard_plan(building: dict, level: dict, plan: dict, style: dict | None, floor_voids=None,
                     ceiling_voids=None) -> dict:
    """The stair's design and its guards (pure; 28 Oct 2026, ``stair_rails``; user on real04's stairs: "There should
    have been better indoor stair solutions should be there I did not like this one"): ``plan["design"]`` from the
    house's style (``stair_rails.stair_design``: the structure, the infill and the handrail of its family in the
    house's balustrade language), ``plan["floor_voids"]`` (the floor openings of the level: the winders of a light
    stair over one are thin, no spandrel panel stands there), ``plan["ceiling_voids"]`` (the openings of the slab
    above when the stair comes up through it) with ``plan["upper_guards"]`` (the runs of that floor's guards,
    ``floor_void_guards``: the stair's handrail does not run up beside them) and ``plan["guards"]``
    (``stair_rails.plan_guards``); a ``stair_structure`` assumed entry for a light structure and a
    ``stair_balustrade`` one. Returns the guards."""
    from wenart.blender import stair_rails as SR

    design = SR.stair_design(style)
    plan["design"] = design
    plan["balustrade"] = design["kind"]
    plan["floor_voids"] = [[(float(p[0]), float(p[1])) for p in v] for v in floor_voids or [] if len(v) >= 3]
    upper: list = []
    up = level_above(building, level)
    plan["upper_wall_rects"] = upper_wall_rects(building, up, plan)
    if ceiling_voids:
        plan["ceiling_voids"] = [[(float(p[0]), float(p[1])) for p in v] for v in ceiling_voids if len(v) >= 3]
        if up is not None:
            try:
                upper = [run for g in floor_void_guards(building, up, plan["ceiling_voids"]) for run in g["runs"]]
            except (KeyError, TypeError, ValueError, ZeroDivisionError):
                upper = []
    plan["upper_guards"] = upper
    guards = SR.plan_guards(plan, plan.get("ceiling_voids"), upper)
    plan["guards"] = guards
    assumed = list(plan.get("assumed") or [])
    if design["structure"] != "solid":
        assumed = [a for a in assumed if a.get("field") != "waist"]
        f = (plan.get("flights") or [{}])[0]
        _k, tv = SR.flight_waist(plan, f) if f else (0.0, 0.0)
        what = ("a thin folded-plate soffit with steel plate strings on the open sides"
                if design["structure"] == "plate"
                else "slim closed strings on the open sides, the soffit flush with them")
        assumed.append({"field": "waist", "kind": "stair_structure",
                        "value": f"{what} ({tv:.3f} m under the steps' inner corners); the landing slab "
                                 f"{P.STAIR_WAIST_M:.2f} m"
                                 + ("; thin winders with riser plates over the floor opening"
                                    if SR.light_winders(plan, plan["floor_voids"]) else ""),
                        "reason": f"the house's style ({design['why']}); the documents show the stair in plan only"})
    n_rails = sum(1 for r in guards["rails"] if r["type"] == "balustrade")
    n_wall = sum(1 for r in guards["rails"] if r["type"] == "wall")
    assumed.append({"field": "balustrade", "kind": "stair_balustrade",
                    "value": f"{design['infill'].replace('_', ' ')} under a {design['rail']['key']} handrail: "
                             f"{n_rails} rail(s) between {len(guards['posts'])} newel(s), {n_wall} wall rail(s); "
                             f"largest gap {guards['max_gap_m']:.3f} m"
                             + (f"; {len(guards['cuts'])} stretch(es) without a handrail: "
                                + "; ".join(sorted({c['why'] for c in guards['cuts']})) if guards["cuts"] else ""),
                    "reason": f"one continuous balustrade per open side with newels at its turns (not drawn: "
                              f"assumed; {design['why']})"})
    plan["assumed"] = assumed
    return guards


def shell_stand_in(slug: str) -> str | None:
    """The texture set a bare request of ``slug`` gets from its shell slot (pure; pass before P5, module docstring):
    the set of the slot ``materials.shell_slot_of(slug)`` names when that set stands in for the slug (the rule of
    ``materials.MaterialLibrary.get``: the slot's ``asset_for``, else its ``slugs``), else None. In the table:
    ``plaster_white`` (the ceiling slot, white_plaster_02), ``stone_worktop`` (Marble012), ``steel_brushed``
    (Metal032)."""
    from wenart.blender import materials as M

    slot = M.shell_slot_of(slug, None)
    spec = M.SHELL_SLOTS.get(slot) if slot else None
    if not spec or not spec.get("asset"):
        return None
    return spec["asset"] if slug in (spec.get("asset_for") or spec.get("slugs") or (slug,)) else None


# 30 Oct 2026 (UL192): the walls' look kinds a stair's structure may take as they are (a smooth plaster or a paint)
STAIR_STRUCTURE_KINDS: tuple[str, ...] = ("plaster", "painted")


def stair_feature_finish(slug: str) -> bool:
    """True when the walls' look ``slug`` is a feature finish (wood slats or panels, stone, brick, wallpaper, tiles: a
    vocabulary kind outside ``STAIR_STRUCTURE_KINDS``); an unknown slug or a plain paint is not (pure)."""
    from wenart.style.profile import _entry

    entry = _entry(slug)
    return bool(entry) and entry.get("kind") not in (None,) + STAIR_STRUCTURE_KINDS


def stair_structure_slot(walls_style: dict) -> dict:
    """The material slot of a stair's structure (pure; fix round after P4b, ``STAIR_STRUCTURE_REASON``): the walls'
    material and colour (and procedural params) without their texture set and tint.

    Pass before P5 (module docstring): a walls slug with a ``shell_stand_in`` set is ``STAIR_STRUCTURE_PAINT``
    instead, in the walls' colour phrase when that phrase colours the walls (``materials.colour_linear``,
    ``materials.takes_colour``), else with ``tint`` = the slug's flat colour over the paint's, so no set comes back
    and the colour stays the walls'."""
    from wenart.blender import materials as M

    walls = dict(walls_style or {"material": "plaster_white"})
    out = {k: v for k, v in walls.items() if k not in ("asset", "tint")}
    slug = str(out.get("material") or "plaster_white")
    if stair_feature_finish(slug):
        # 30 Oct 2026 (lesson UL192, user on real04 run 20261030-112241-full: "Something wrong with the stairs": the
        # walls' wood_slat finish, procedural with no texture set, was copied onto the risers, the soffit and the
        # spandrels): a feature finish is never the stair's structure; the smooth paint of a plain white plaster wall,
        # in the walls' colour phrase when they give one
        plain = {"material": "plaster_white"}
        if M.colour_linear(out.get("colour")) is not None:
            plain["colour"] = out["colour"]
        return stair_structure_slot(plain)
    if shell_stand_in(slug) is None:
        return out
    out["material"] = STAIR_STRUCTURE_PAINT
    if M.colour_linear(out.get("colour")) is None or not M.takes_colour(slug, bool(walls.get("asset"))):
        out.pop("colour", None)
        own, paint = M.flat_colour(slug), M.flat_colour(STAIR_STRUCTURE_PAINT)
        out["tint"] = [round(float(o) / float(p), 4) for o, p in zip(own, paint)]
    return out


def stair_mesh(plan: dict, floor_z: float) -> tuple[list, list, list[int], list[dict]]:
    """``(verts, faces, slots, parts)`` of a planned stair in world metres
    (pure): ``parametric.stair_parts`` lifted to the floor, one material slot
    per face (``parametric.STAIR_SLOTS``)."""
    parts = P.stair_parts(plan)
    verts, faces = geom2d.merge([(p["verts"], p["faces"]) for p in parts])
    return [(x, y, z + floor_z) for x, y, z in verts], faces, P.stair_face_slots(parts), parts


def stair_room(piece: dict, rooms: list[dict]) -> dict | None:
    """The room of a stair: its ``room_id``, else the room holding its footprint centre."""
    by_id = {r["id"]: r for r in rooms}
    if piece.get("room_id") in by_id:
        return by_id[piece["room_id"]]
    centre = piece["footprint"]["center"]
    return next((r for r in rooms if len(r["polygon"]) >= 3 and G.point_in_polygon(centre, r["polygon"])), None)


def build_stairs(building: dict, level: dict, collection, library, style: dict, pass_indices: dict,
                 manifest_objects: list, assumed: list, warnings: list, plans: list | None = None,
                 shaft: bool = True, floor_voids: list | None = None, ceiling_voids: list | None = None) -> dict:
    """Build the stairs of a level (``plan_stairs``): one ``furn_<id>``
    object (kind ``furniture``, the piece's pass index; treads in the room's
    floor finish, structure in the wall finish, steel rails) and one
    ``<id>_void`` object closing the ceiling opening (kind ``ceiling``,
    status ``assumed``, the ceiling finish). Every assumption of the plan
    becomes a scene-manifest ``assumed`` entry (parent = the piece). Returns
    ``{"pieces", "ids", "not_built"}``. ``shaft`` False (Milestone 10: the
    slab above has the opening and the floor above is cut): no capped shaft,
    the stair arrives on the level above. An item without a plan is listed
    under ``not_built`` (``stair_not_built``: Milestone 10's upper end of the
    stair below carries ``arrives_from`` and ``slab_opening``, and that
    stair's ``stair`` record gets ``upper_end``).

    28 Oct 2026 (``stair_guard_plan``): ``floor_voids`` (the openings of this level's floor) and ``ceiling_voids``
    (those of the slab above, when the stair comes up through it) shape the stair's guards and structure; a fifth
    material, the house's wood (``stair_timber_slot``), takes the timber handrails, slats, balusters and strings."""
    from wenart.blender import common

    floor_z = float(level["elevation"])
    plans = plan_stairs(building, level) if plans is None else plans
    rooms = [r for r in building["rooms"] if r["level_id"] == level["id"]]
    level_walls = [w for w in building.get("walls") or [] if w.get("level_id") == level["id"]]
    summary = {"pieces": 0, "ids": [], "not_built": []}
    walls_style = style.get("walls") or {"material": "plaster_white"}
    ceiling_style = style.get("ceiling") or {"material": "plaster_white"}
    _t, metal_slug, _why = stair_finishes(style, None)
    steel = library.get(metal_slug)              # 29 Oct 2026 (H8): black in the modern families
    foreign = level_guard_segments(building, level, floor_voids)     # 30 Oct 2026 (UL192): the stair's envelope
    for item in plans:
        piece, plan = item["piece"], item["plan"]
        for w in item.get("warnings") or []:
            warnings.append(f"{piece['id']}: stair {w}")
        if plan is None:
            record, notes = stair_not_built(item, level)
            summary["not_built"].append(record)
            assumed.extend(notes)
            if record.get("arrives_from"):
                below = next((e for e in manifest_objects if e.get("name") == f"furn_{record['arrives_from']}"
                              and isinstance(e.get("stair"), dict)), None)
                if below is not None:
                    below["stair"]["upper_end"] = piece["id"]
            continue
        status = piece.get("status", "verified")
        unverified = status == "unverified"
        room = stair_room(piece, rooms)
        slot, _wet = floor_style(room or {}, style)
        tread_slot, _metal, finish_why = stair_finishes(style, slot)     # 29 Oct 2026 (H8): the family's finishes
        tread = slot_material(library, tread_slot or slot, unverified=unverified)
        # fix round after P4b (17 Oct 2026): a smooth paint of the wall colour (STAIR_STRUCTURE_REASON)
        structure = slot_material(library, stair_structure_slot(walls_style), unverified=unverified)
        plan = stair_build_plan(plan, level_walls)          # fix round after P4b: the stair meets its walls
        # 25 Oct 2026: the balustrade follows the style; 28 Oct 2026: the whole stair's design, one continuous
        # balustrade per open side (stair_guard_plan), and no spandrel panel over a floor opening
        stair_guard_plan(building, level, plan, style, floor_voids, None if shaft else ceiling_voids)
        stair_under_plan(plan, level_walls, plan.get("floor_voids") or ())   # 27 Oct 2026: closed where low
        verts, faces, slots, parts = stair_mesh(plan, floor_z)
        name = f"furn_{piece['id']}"
        glass = library.thin_glass()
        timber = slot_material(library, stair_timber_slot(style), unverified=unverified)
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=piece["id"],
                                    kind="furniture", status=status,
                                    materials=[tread, structure, steel, glass, timber],
                                    face_material_indices=slots)
        index = len(pass_indices) + 1
        pass_indices[piece["id"]] = index
        ob.pass_index = index
        ob["wenart_type"] = piece["type"]
        ob["wenart_room"] = piece.get("room_id") or (room["id"] if room else "")
        ob["wenart_source"] = piece.get("source") or "from_documents"
        ob["wenart_asset"] = "parametric"
        fp = piece["footprint"]
        rot = float(fp["rotation_deg"])
        x0, y0, z0, x1, y1, z1 = P.local_bbox_of_world_points(verts, fp["center"], rot)
        entry = {
            "name": name, "wenart_id": piece["id"], "kind": "furniture", "status": status, "level_id": level["id"],
            "element_id": piece["id"], "room_id": piece.get("room_id"), "type": piece["type"],
            "source": piece.get("source"), "evidence": piece.get("evidence", []), "pass_index": index,
            "assumed": {}, "decor": [],
            "center": [float(fp["center"][0]), float(fp["center"][1]), floor_z + plan["rise_m"] / 2.0],
            "size": [float(fp["size"][0]), float(fp["size"][1]), round(plan["rise_m"], 4)], "rotation_deg": rot,
            "front_deg": None if piece.get("front_deg") is None else float(piece["front_deg"]),
            "asset": piece.get("asset"), "fit_scale": [1.0, 1.0, 1.0],
            "method": STAIR_METHOD_GENERIC if plan["generic"] else STAIR_METHOD,
            "bbox_m": [round(x1 - x0, 4), round(y1 - y0, 4), round(z1 - z0, 4)], "fallback_reason": None,
            "materials": [m.name for m in (tread, structure, steel, glass, timber)], "material": tread.name,
            "textured": any(library.textured(m) for m in (tread, structure)),
            "stair": stair_record(plan, parts, foreign),
        }
        shaft_name = f"{piece['id']}_void"
        for a in plan["assumed"]:
            if not shaft and a["kind"] == "stair_void":
                continue                    # the opening is the slab's (building JSON), not assumed here
            owner = shaft_name if a["kind"] == "stair_void" else name
            if owner == name:
                entry["assumed"][a["field"]] = a["value"]
            assumed.append({"object": owner, "field": a["field"], "value": a["value"], "reason": a["reason"],
                            "parent": piece["id"], "kind": a["kind"]})
        for w in plan["warnings"]:
            warnings.append(f"{piece['id']}: stair {w}")
        entry["stair"]["finishes"] = finish_why
        assumed.append({"object": name, "field": "stair_finishes", "value": finish_why, "parent": piece["id"],
                        "kind": "stair_finishes", "reason": "the house's style family (H8); the documents show the "
                                                           "stair in plan only"})
        manifest_objects.append(entry)
        summary["pieces"] += 1
        summary["ids"].append(piece["id"])
        if not shaft:
            entry["stair"]["arrives"] = "through the opening of the slab above (no shaft)"
            continue
        sv, sf = P.void_shaft(plan)
        if sf:
            cap_mat = slot_material(library, ceiling_style)
            shaft = common.new_mesh_object(shaft_name, [(x, y, z + floor_z) for x, y, z in sv], sf,
                                           collection=collection, wenart_id=shaft_name, kind="ceiling",
                                           status="assumed", materials=[cap_mat])
            void = next((a for a in plan["assumed"] if a["kind"] == "stair_void"), {})
            manifest_objects.append({
                "name": shaft.name, "wenart_id": shaft_name, "kind": "ceiling", "status": "assumed",
                "level_id": level["id"], "element_id": piece["id"], "parent": piece["id"], "evidence": [],
                "material": cap_mat.name, "textured": library.textured(cap_mat), "pass_index": None,
                "room_type": None, "wet": False,
                "assumed": {"detail": "stair_void", "cap_z": round(floor_z + plan["cap_z"], 4),
                            "void": [[[round(x, 4), round(y, 4)] for x, y in loop] for loop in plan["void"]],
                            "reason": void.get("reason", "assumed ceiling opening")},
            })
    return summary


def stair_not_built(item: dict, level: dict) -> tuple[dict, list[dict]]:
    """``(record, assumed)`` of a ``plan_stairs`` item without a plan (pure): the furniture summary's
    ``not_built`` record ``{"id", "type", "reason"}`` and the scene-manifest ``assumed`` entries. The upper end
    of a stair of the level below (Milestone 10, ``stair_arrival``) adds ``arrives_from`` and ``slab_opening``
    (the opening id of the slab under the level, or None) to the record and one ``stair_arrival`` entry."""
    piece = item["piece"]
    record = {"id": piece["id"], "type": piece["type"], "reason": item["reason"]}
    arr = item.get("arrival")
    if not arr:
        return record, []
    record["arrives_from"] = arr["from"]
    record["slab_opening"] = arr.get("opening")
    if arr.get("opening"):
        through = f"slab opening {arr['opening']}"
    elif arr.get("slabs"):
        through = "the opening the slab plan cuts over it"
    else:
        through = "no slab opening: the building has no slabs"
    entry = {"object": piece["id"], "field": "stair", "value": f"arrives from {arr['from']}",
             "reason": f"no level above {level['id']}: the drawn stair lies over {arr['from']} "
                       f"({arr['share']:.0%} of the smaller footprint; {through}); read as its upper end, "
                       f"not built as a second flight",
             "parent": piece["id"], "kind": "stair_arrival"}
    return record, [entry]


def level_guard_segments(building: dict, level: dict, floor_voids: list | None) -> list[dict]:
    """The guards of the openings of ``level``'s floor (``floor_void_guards``) as ``stair_rails.envelope_review``'s
    foreign parts (pure; 30 Oct 2026, lesson UL192): ``{"id": void_guard_<level>_<i>, "segments"}`` relative to the
    floor, ``details.GUARD`` high."""
    from wenart.blender import stair_rails as SR
    return [{"id": f"void_guard_{level['id']}_{g['void']}",
             "segments": SR.guard_run_segments(g["runs"], D.GUARD["height"])}
            for g in floor_void_guards(building, level, floor_voids or [])]


def stair_record(plan: dict, parts: list[dict], foreign: list[dict] | None = None) -> dict:
    """The scene manifest's ``stair`` record of a built stair (pure); 30 Oct 2026 (lesson UL192): ``envelope``, the
    findings of ``stair_rails.envelope_review`` (its parts against its envelope, ``foreign`` parts in its walking
    zone), read by the model review's M18."""
    from wenart.blender import stair_rails as SR
    return {
        "risers": plan["risers"], "riser_m": round(plan["riser_m"], 4), "riser_source": plan["riser_source"],
        "rise_m": round(plan["rise_m"], 4), "direction": plan["direction"], "turn": plan["turn"],
        "generic": plan["generic"],
        "flights": [{"index": f["index"], "lines": f["lines"], "width": round(f["width"], 4),
                     "going": round(f["going"], 4), "rise_dir": [round(f["rise_dir"][0], 4), round(f["rise_dir"][1], 4)],
                     "base_z": round(f["base_z"], 4), "top_z": round(f["top_z"], 4),
                     "treads": sum(1 for p in parts if p["role"] == "step" and p.get("flight") == f["index"])}
                    for f in plan["flights"]],
        "landing": None if plan["landing"] is None else {"role": plan["landing"]["role"],
                                                         "z": round(plan["landing"]["z"], 4)},
        "rails": plan["rails"], "notes": plan["notes"],
        # fix round after P4b (17 Oct 2026): the sides that meet a wall (stair_wall_joints) and the structure finish
        "wall_joints": list(plan.get("wall_joints") or []), "structure_finish": STAIR_STRUCTURE_REASON,
        # 27 Oct 2026: the space under the stair as built (stair_under_plan): the model review's M9 reads it
        "under": {"panels": sum(1 for p in parts if p.get("role") == "spandrel"),
                  "posts": sum(1 for p in parts if p.get("role") == "landing_post"),
                  "low_m2": (plan.get("under") or {}).get("low_m2")},
        # 28 Oct 2026: the structure and the guards as built (stair_guard_plan): the model review's M18 reads them
        "structure": SR.structure_of(plan),
        "guards": SR.summary(plan["guards"]) if plan.get("guards") else None,
        "envelope": SR.envelope_review(plan, parts, foreign or ()),
    }


# --------------------------------------------------------------------------
# Checks
# --------------------------------------------------------------------------

RAY_IGNORED_KINDS = ("door", "window")


def door_ray_checks(building: dict, level: dict, scene) -> list[dict]:
    """Cast a ray through every door / plain opening centre (on the wall
    centre line) across its wall at 1 m height and record what it hits.
    Door and window objects (frame, leaf, glass) are stepped over so the ray
    tests the wall itself: after the booleans ``hit`` must be False and
    ``hit_kind`` None; the stepped-over objects are listed in ``passed``."""
    import bpy
    from mathutils import Vector

    level_id = level["id"]
    floor_z = float(level["elevation"])
    walls = {w["id"]: w for w in building["walls"] if w["level_id"] == level_id}
    depsgraph = bpy.context.evaluated_depsgraph_get()
    results = []
    for opening in building["openings"]:
        if opening["level_id"] != level_id or opening["type"] not in ("door", "opening"):
            continue
        wall = walls.get(opening.get("wall_id"))
        if wall is None:
            continue  # a virtual separator (no wall, no geometry) or a missing wall (warned in build_openings)
        nx, ny = G.unit_normal_left(wall["start"], wall["end"])
        cx, cy, _shift = opening_centre_on_wall(opening, wall)
        reach = float(wall["thickness"]) / 2.0 + 0.3
        origin = Vector((cx + nx * reach, cy + ny * reach, floor_z + 1.0))
        direction = Vector((-nx, -ny, 0.0))
        remaining = 2 * reach
        passed = []
        hit, ob = False, None
        for _ in range(16):  # at most a few door/window parts sit on the ray
            hit, loc, _normal, _index, ob, _matrix = scene.ray_cast(depsgraph, origin, direction, distance=remaining)
            if not hit or ob is None or ob.get("wenart_kind") not in RAY_IGNORED_KINDS:
                break
            passed.append(ob.name)
            # Continue just behind the door/window part that was hit.
            remaining -= (loc - origin).length + 0.002
            origin = loc + direction * 0.002
            if remaining <= 0:
                hit, ob = False, None
                break
        results.append({
            "opening_id": opening["id"], "hit": bool(hit),
            "hit_object": ob.name if hit and ob is not None else None,
            "hit_kind": ob.get("wenart_kind") if hit and ob is not None else None,
            "passed": passed,
        })
    return results


# --------------------------------------------------------------------------
# Milestone 10 (docs/milestone10.md §3.2 items 1, 4): slabs, corners, the outside looks, sills, railings
# --------------------------------------------------------------------------

SLAB_FACE_GAP = 0.001         # slab faces stay this far inside the floors, ceilings and wall faces around them
WALL_UNDER_FLOOR_GAP = 0.003  # a wall up to the next floor stops this far under it (31 Oct 2026: its top showed through)
SLAB_EDGE_INSET = 0.01        # ... and the slab edge this far inside the outer wall faces (no coplanar facade)
CORNER_JOIN_TOL = 0.01        # two wall ends within this meet in a corner
STAIR_ARRIVAL_TOL = 0.05      # a stair's top must lie within this of an opening of the slab above
SILL = {"depth": 0.30, "projection": 0.04, "thickness": 0.05, "rise": 0.02, "ears": 0.03, "material": "stone"}
RAILING = {"height": 1.00, "rail": 0.045, "panel": 0.012, "panel_bottom": 0.10, "wall_reach": 0.05,
           "post": 0.04, "post_every": 1.5}      # steel posts at the ends and at most 1.5 m apart (24 Oct 2026)


def corner_extensions(walls: list[dict], tol: float = CORNER_JOIN_TOL) -> dict[str, dict]:
    """``{wall id: {"start" | "end": [x, y]}}``: wall ends that meet another wall's end at an angle (an
    L-join or a corner) moved out by half the other wall's thickness, so the corner square between the two
    centre lines is closed (``trim_wall_overlaps`` then trims the overlap). Pure; the M3-M9 walls left the
    outer corner square open, which an exterior view shows."""
    out: dict[str, dict] = {}
    for w in walls:
        length = G.distance(w["start"], w["end"])
        if length < 1e-9:
            continue
        for which in ("start", "end"):
            p = w[which]
            reach = 0.0
            for o in walls:
                if o is w or G.distance(o["start"], o["end"]) < 1e-9:
                    continue
                if min(G.distance(p, o["start"]), G.distance(p, o["end"])) > tol:
                    continue
                turn = abs((G.segment_angle_deg(w["start"], w["end"]) - G.segment_angle_deg(o["start"], o["end"])
                            + 90.0) % 180.0 - 90.0)
                if turn > 10.0:
                    reach = max(reach, float(o["thickness"]) / 2.0)
            if reach > 0:
                d = -reach if which == "start" else length + reach
                out.setdefault(w["id"], {})[which] = list(G.point_at_distance(w["start"], w["end"], d))
    return out


# --- slabs ------------------------------------------------------------------

def slab_plan(building: dict, levels: list[dict], brief_thickness: float = 0.20,
              brief_assumed: bool = True) -> dict:
    """The slabs of a whole building (pure; §3.2 item 1): ``{"slabs": [record], "by_level": {level id:
    {"under": record | None, "above": record | None}}, "assumed", "warnings"}``.

    Per level (bottom up) the slab under it: the building's ``slabs[]`` entry whose ``above_level_id`` is
    the level (thickness null -> the brief's ``slab_thickness``, assumed), else one derived from the level's
    wall outline at its elevation with the brief's thickness (assumed). A record: ``{"id", "z_top",
    "thickness", "outline", "voids": [polygons], "above_level_id", "below_level_id", "source", "status",
    "evidence", "assumed": [notes], "stairs": [the stairs of the level below that pass it]}``. Every stair of
    the level below needs an opening of the slab: one that overlaps the stair's own opening
    (``plan_stairs``), else the stair's opening is added (assumed, a warning); a stair whose top lies outside
    every opening is a warning (``stair_arrivals``)."""
    order = sorted(levels, key=lambda lv: float(lv["elevation"]))
    given = {s.get("above_level_id"): s for s in building.get("slabs") or [] if isinstance(s, dict)}
    records, assumed, warnings = [], [], []
    by_level: dict[str, dict] = {lv["id"]: {"under": None, "above": None} for lv in order}
    for i, lv in enumerate(order):
        below = order[i - 1] if i > 0 else None
        s = given.get(lv["id"])
        notes = []
        if s is not None:
            thickness = s.get("thickness")
            if thickness is None or float(thickness) <= 0:
                thickness = brief_thickness
                notes.append(f"thickness {brief_thickness} m from the brief's slab_thickness"
                             + (" (default)" if brief_assumed else ""))
            elif s.get("thickness_source") == "assumed_default":
                notes.append(f"thickness {float(thickness)} m assumed in the building JSON")
            outline = geom2d.ccw(s.get("outline") or [])
            source = "building"
            if len(outline) < 3:
                outline, method = geom2d.wall_outline([w for w in building["walls"] if w["level_id"] == lv["id"]])
                notes.append(f"no outline: the level's wall outline ({method})")
            z_top = float(s.get("z_top", lv["elevation"]))
            if abs(z_top - float(lv["elevation"])) > 0.01:
                warnings.append(f"{s.get('id')}: top {z_top:.3f} m but level {lv['id']} stands at "
                                f"{float(lv['elevation']):.3f} m; the slab is built at its top, the floors at the level")
            voids = [geom2d.ccw(o["polygon"]) for o in s.get("openings") or []
                     if isinstance(o, dict) and len(o.get("polygon") or []) >= 3]
            rec = {"id": s.get("id") or f"sl_{lv['id']}", "z_top": z_top, "thickness": float(thickness),
                   "outline": outline, "voids": voids, "above_level_id": lv["id"],
                   "below_level_id": below["id"] if below else None, "source": source,
                   "status": s.get("status") or "verified", "evidence": s.get("evidence") or [], "assumed": notes}
        else:
            outline, method = geom2d.wall_outline([w for w in building["walls"] if w["level_id"] == lv["id"]])
            if len(outline) < 3:
                continue
            notes.append(f"no slab under {lv['id']} in the building: derived from the wall outline ({method}), "
                         f"thickness {brief_thickness} m from the brief")
            rec = {"id": f"sl_{lv['id']}", "z_top": float(lv["elevation"]), "thickness": float(brief_thickness),
                   "outline": outline, "voids": [], "above_level_id": lv["id"],
                   "below_level_id": below["id"] if below else None, "source": "derived", "status": "assumed",
                   "evidence": [], "assumed": notes}
        rec["stairs"] = []
        if below is not None:
            for item in plan_stairs(building, below, slab_void=True):
                if item["plan"] is None:
                    continue
                pid = item["piece"]["id"]
                rec["stairs"].append(pid)
                own = [loop for loop in item["plan"]["void"] if len(loop) >= 3]
                if own and not any(_overlap(loop, v) for loop in own for v in rec["voids"]):
                    rec["voids"].extend(geom2d.ccw(loop) for loop in own)
                    rec["assumed"].append(f"opening for stair {pid} added (the stair's own opening)")
                    warnings.append(f"{rec['id']}: no opening over stair {pid}; the stair's opening is cut (assumed)")
                for msg in stair_arrivals(item["plan"], rec["voids"]):
                    warnings.append(f"{pid}: {msg} of slab {rec['id']}")
        for note in rec["assumed"]:
            assumed.append({"object": rec["id"], "field": "slab", "value": rec["thickness"], "reason": note})
        records.append(rec)
        by_level[lv["id"]]["under"] = rec
        if below is not None:
            by_level[below["id"]]["above"] = rec
    return {"slabs": records, "by_level": by_level, "assumed": assumed, "warnings": warnings}


def _overlap(a, b) -> bool:
    """True when two polygons share area (``_shared_area``; enough for stair openings)."""
    return _shared_area(a, b) > 1e-4


def _shared_area(a, b) -> float:
    """The area two polygons share (a clipped by b's convex pieces; a convex, as stair openings and footprints)."""
    area = 0.0
    for piece in geom2d.convex_pieces(b):
        poly = list(a)
        n = len(piece)
        for i in range(n):
            p, q = piece[i], piece[(i + 1) % n]
            nx, ny = G.unit_normal_left(p, q)          # inside of a counter-clockwise piece
            poly = geom2d.clip_half_plane(poly, -nx, -ny, nx * p[0] + ny * p[1]) if poly else []
        if len(poly) >= 3:
            area += G.polygon_area(poly)
    return area


def stair_arrivals(plan: dict, voids: list, tol: float = STAIR_ARRIVAL_TOL) -> list[str]:
    """Where a stair arrives (the end of its last flight, pure): a message when it lies outside every
    opening of the slab above (more than ``tol`` away)."""
    flights = plan.get("flights") or []
    if not flights or not voids:
        return [] if flights else ["no flight to check"]
    last = flights[-1]
    end = last.get("end") or last.get("start")
    if end is None:
        return []
    p = (float(end[0]), float(end[1]))
    if any(G.point_in_polygon(p, v) or geom2d.distance_to_polygon_edges(p, v) <= tol for v in voids):
        return []
    return [f"arrives at ({p[0]:.2f}, {p[1]:.2f}), outside the openings"]


def slab_solid(rec: dict) -> tuple[list, list]:
    """``(verts, faces)`` of a slab: its outline ``SLAB_EDGE_INSET`` in, minus its openings, from
    ``SLAB_FACE_GAP`` over its bottom to ``SLAB_FACE_GAP`` under its top (the floors above and the ceilings
    below stay in front), closed by its edges and the sides of the openings."""
    outline = geom2d.offset_polygon(rec["outline"], SLAB_EDGE_INSET)
    top = [(0.0, 0.0, float(rec["z_top"]) - SLAB_FACE_GAP)]
    bottom = [(0.0, 0.0, float(rec["z_top"]) - float(rec["thickness"]) + SLAB_FACE_GAP)]
    holes = [geom2d.ccw(v) for v in rec["voids"]]
    faces = [(geom2d.lift(p, top[0], True), 0) for p in geom2d.convex_pieces(outline, holes)]
    faces += [(geom2d.lift(p, bottom[0], False), 0) for p in geom2d.convex_pieces(outline, holes)]
    for p, q in geom2d.region_boundary(outline, holes):
        faces += [(f, 0) for f in geom2d.segment_side_faces(p, q, top, bottom)]
    verts, fs, _ = geom2d.mesh_from_faces(faces)
    return verts, fs


def build_slabs(plan: dict, collections: dict, library, style: dict, manifest_objects: list, assumed: list) -> list:
    """One object per slab of ``slab_plan`` (``<slab id>``, kind ``slab``, in the collection of the level
    it carries; the wall finish: only its edges in the stair openings are seen)."""
    from wenart.blender import common

    walls_style = style.get("walls") or {"material": "plaster_white"}
    mat = slot_material(library, dict(walls_style, tint=None))
    created = []
    for rec in plan["slabs"]:
        col = collections.get(rec["above_level_id"])
        if col is None:
            continue
        verts, faces = slab_solid(rec)
        ob = common.new_mesh_object(rec["id"], verts, faces, collection=col, wenart_id=rec["id"], kind="slab",
                                    status="assumed" if rec["status"] == "assumed" else "verified", materials=[mat])
        created.append(ob)
        zs = [v[2] for v in verts] or [0.0]
        manifest_objects.append({
            "name": ob.name, "wenart_id": rec["id"], "kind": "slab", "status": ob["wenart_status"],
            "level_id": rec["above_level_id"], "element_id": rec["id"], "evidence": rec["evidence"],
            "material": mat.name, "textured": library.textured(mat), "pass_index": None,
            "assumed": {"notes": rec["assumed"]} if rec["assumed"] else {},
            "z_top": round(float(rec["z_top"]), 4), "thickness": round(float(rec["thickness"]), 4),
            "z_range": [round(min(zs), 4), round(max(zs), 4)], "openings": len(rec["voids"]),
            "below_level_id": rec["below_level_id"], "source": rec["source"], "stairs": rec["stairs"],
        })
    return created


# --- the looks: track F's functions and the outside materials ------------------
#
# docs/milestone10.md §1.6b row 20: track F owns ``wenart/blender/looks.py`` (pure functions this module calls:
# ``wall_face_material``, ``accent_walls``, ``wet_wall_look``, ``door_look``, ``window_frame_look``,
# ``facade_look``, ``door_geometry_m10``, ``window_geometry_m10``) and ``materials.exterior_material(library,
# slug, colour=None)``. The wrappers below hand over to F's function of the same name and signature (the
# Milestone 9 looks remain as the fallback when the module cannot be imported). A look is a dict
# ``{"material": slug, "asset", "tint", "colour", "rgb", "params", "source", "reason"}`` (only ``material``
# required); ``look_material`` makes its Blender material.

def _f_looks(name: str):
    """Track F's function ``name`` of ``wenart.blender.looks``, None while F's module or function is missing."""
    try:
        from wenart.blender import looks as F  # track F (Milestone 10)
    except ImportError:
        return None
    return getattr(F, name, None)


def _slot_look(entry, default: str) -> dict:
    entry = entry if isinstance(entry, dict) else {}
    return {"material": entry.get("material") or default, "asset": entry.get("asset"), "tint": entry.get("tint")}


def wall_face_material(style: dict, room: dict | None = None) -> dict:
    """The look of the inside wall faces of ``room`` (None = the level's default): ``looks.wall_face_material``
    (the style's ``walls`` slot with its colour name)."""
    f = _f_looks("wall_face_material")
    if f is not None:
        return f(style, room)
    return dict(_slot_look(style.get("walls"), "plaster_white"), tint=None)     # no walls.tint since M5


def wet_wall_look(style: dict, room: dict | None = None) -> dict:
    """The look of the wall faces of a wet room: ``looks.wet_wall_look`` (the style's ``wet_walls`` slot, its tile
    size, pattern and grout colour as procedural ``params``), else ``walls``."""
    f = _f_looks("wet_wall_look")
    if f is not None:
        return f(style, room)
    return dict(_slot_look(style.get("wet_walls") or style.get("walls"), "tiles_white"), tint=None)


def accent_walls(building: dict, level: dict, style: dict) -> dict:
    """``{wall id: {room id: look}}``: the inside faces of a wall towards a room that take the style's
    ``wall_accent`` look (``looks.accent_walls``: behind the sofa or the bed head, else the longest wall without a
    window, one per living room and bedroom)."""
    f = _f_looks("accent_walls")
    if f is not None:
        return f(building, level, style) or {}
    return {}


def door_look(style: dict, opening: dict | None = None) -> dict:
    """The look of a door leaf: ``looks.door_look`` (the style's ``door`` slot, a wood door's veneer, the door style
    decided by the drawn operation first)."""
    f = _f_looks("door_look")
    if f is not None:
        return f(style, opening)
    door_style = style.get("door") or {"material": "wood_oak_light"}
    slug, asset = door_leaf_material(door_style)
    return {"material": slug, "asset": asset, "tint": door_style.get("tint")}


def door_product(style: dict, door_style: str | None = None) -> dict:
    """``looks.door_product`` (29 Oct 2026, UL122: a style with a family frames every door and lines every passage);
    {} when the module cannot be imported."""
    f = _f_looks("door_product")
    return (f(style, door_style) or {}) if f is not None else {}


def window_frame_look(style: dict, opening: dict | None = None) -> dict:
    """The look of a window frame (seen from inside): ``looks.window_frame_look`` (the style's ``window_frame``
    slot)."""
    f = _f_looks("window_frame_look")
    if f is not None:
        return f(style, opening)
    return _slot_look(style.get("window_frame"), "painted_metal_white")


def door_geometry_m10(style: dict, opening: dict | None = None) -> bool:
    """True when a door gets the Milestone 10 geometry (``looks.door_geometry_m10``: a style door style, handle or
    colour, or a drawn non-swing operation); else the Milestone 6-9 door."""
    f = _f_looks("door_geometry_m10")
    return bool(f(style, opening)) if f is not None else False


def window_geometry_m10(style: dict, opening: dict | None = None) -> bool:
    """True when a window gets the Milestone 10 geometry (``looks.window_geometry_m10``: a Milestone 10 frame
    material or colour, or drawn mullions / transoms); else the Milestone 6-9 window."""
    f = _f_looks("window_geometry_m10")
    return bool(f(style, opening)) if f is not None else False


def facade_look(looks: dict, wall: dict | None = None) -> dict:
    """The outside look of an outer wall: ``looks.facade_look`` (the resolved facade look of
    ``exterior.resolve_looks``)."""
    f = _f_looks("facade_look")
    if f is not None:
        return f(looks, wall)
    return looks["facade"]


# Flat linear colours of the outside details no vocabulary slug covers (the build's own looks of
# ``exterior.BUILD_LOOKS`` and the site: sill stone, light-well concrete, soffit, trees, soil, the window glass of
# the exterior model); designer values (assumed). Every vocabulary slug takes ``vocabulary.MATERIALS[slug]["flat"]``
# through ``materials.exterior_material``, every colour name ``wenart/style/colours.py``.
LOOK_RGB = {"stone": (0.50, 0.48, 0.44), "concrete": (0.38, 0.38, 0.37), "bark": (0.10, 0.07, 0.05),
            "foliage": (0.04, 0.12, 0.02), "soil": (0.15, 0.11, 0.08), "soffit": (0.75, 0.74, 0.72),
            "glass": (0.60, 0.65, 0.65)}


def colour_rgb(name: str | None) -> tuple[float, float, float] | None:
    """Linear RGB of a colour phrase (``wenart.style.colours.linear_rgb``: names, aliases and modifiers); None
    for an unknown word."""
    if not name:
        return None
    word = str(name).strip().lower().replace("_", " ")
    try:
        from wenart.style import colours as C
        return tuple(round(float(v), 4) for v in C.linear_rgb(word))
    except (ImportError, KeyError, ValueError):
        return None


def exterior_material(library, slug: str, colour=None, rgb=None):
    """The Blender material of an outside slug in a colour: a vocabulary slug through track F's
    ``materials.exterior_material`` (its asset, procedural look and colour), else a flat material of ``rgb`` /
    the colour / ``LOOK_RGB`` (the slug keeps its name, so the manifest's material record names it)."""
    from wenart.blender import materials as M

    if slug in M.FLAT_COLOURS and rgb is None:
        return M.exterior_material(library, slug, colour)
    rgb = tuple(rgb) if rgb else colour_rgb(colour)
    if slug in M.FLAT_COLOURS:
        base = M.flat_colour(slug)
        return library.get(slug, None, [r / max(b, 1e-4) for r, b in zip(rgb, base)] if rgb else None)
    target = rgb or LOOK_RGB.get(slug) or M.flat_colour("unknown")
    grey = M.flat_colour("unknown")
    return library.get(slug, None, [t / max(g, 1e-4) for t, g in zip(target, grey)])


def look_material(library, look: dict):
    """The Blender material of a look (``exterior.resolve_looks`` entry or a slot look): a vocabulary slug through
    the library with its asset, colour name and procedural ``params``; an explicit ``rgb`` or a slug the
    vocabulary does not know through ``exterior_material``."""
    from wenart.blender import materials as M

    slug = str(look.get("material") or look.get("slug") or "unknown")
    if not look.get("rgb") and (look.get("asset") or slug in M.FLAT_COLOURS):
        return library.get(slug, look.get("asset") or (M.ENTRIES.get(slug) or {}).get("asset"), look.get("tint"),
                           colour=look.get("colour"), params=look.get("params"))
    return exterior_material(library, slug, look.get("colour"), look.get("rgb"))


# --- sills and railings ------------------------------------------------------

def outward_side(wall: dict, outline, centre) -> tuple[float, float] | None:
    """The unit normal of a wall pointing out of the building ``outline`` at ``centre`` (pure; None when both
    or neither side of the wall lie outside the outline: an inner wall)."""
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall["thickness"]) / 2.0 + 0.05
    out = []
    for s in (1.0, -1.0):
        p = (centre[0] + s * nx * reach, centre[1] + s * ny * reach)
        out.append(not G.point_in_polygon(p, outline))
    if out[0] == out[1]:
        return None
    return (nx, ny) if out[0] else (-nx, -ny)


def sill_box(opening: dict, wall: dict, level: dict, levels_above: bool, outward, cfg: dict | None = None
             ) -> tuple[list, list, dict]:
    """``(verts, faces, info)`` of the outside sill of a window (pure): from the frame's outer edge to
    ``projection`` past the outer wall face, ``ears`` wider than the opening on both sides, its top
    ``rise`` above the opening's bottom (the reveal floor) and ``thickness`` thick."""
    c = dict(SILL, **(cfg or {}))
    bottom, _top, _ = opening_vertical(opening, level, levels_above)
    cx, cy, _ = opening_centre_on_wall(opening, wall)
    half_t = float(wall["thickness"]) / 2.0
    frame_depth = c.get("frame_depth") or min(float(wall["thickness"]), 0.08)   # M10: the frame profile's
    inner = float(frame_depth) / 2.0 + 0.001                            # the window frame's outer edge
    outer = half_t + float(c["projection"])
    depth = outer - inner
    mid = (inner + outer) / 2.0
    ox, oy = outward
    centre = (cx + ox * mid, cy + oy * mid, bottom + float(c["rise"]) - float(c["thickness"]) / 2.0)
    width = float(opening["width"]) + 2.0 * float(c["ears"])
    angle = math.degrees(math.atan2(oy, ox)) - 90.0
    verts, faces = geom2d.box(centre, (width, depth, float(c["thickness"])), angle)
    return verts, faces, {"width": round(width, 4), "depth": round(depth, 4), "projection": c["projection"],
                          "top_z": round(bottom + float(c["rise"]), 4)}


def railing_edges(room: dict, walls: list[dict], reach: float = RAILING["wall_reach"]) -> list[tuple]:
    """Edges of a balcony polygon that no wall carries (pure): ``[(p, q)]`` sub-segments of each edge whose
    points lie farther than half a wall thickness + ``reach`` from every wall (sampled every 5 cm)."""
    poly = geom2d.ccw(room["polygon"])
    out = []
    n = len(poly)
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        length = G.distance(p, q)
        if length < 1e-6:
            continue
        k = max(2, int(length / 0.05))
        free = []
        for j in range(k + 1):
            x = G.point_along_segment(p, q, j / k)
            free.append(not any(G.point_segment_distance(x, w["start"], w["end"]) <= float(w["thickness"]) / 2.0 + reach
                                for w in walls))
        j = 0
        while j <= k:
            if not free[j]:
                j += 1
                continue
            j0 = j
            while j <= k and free[j]:
                j += 1
            t0, t1 = j0 / k, (j - 1) / k
            if (t1 - t0) * length >= 0.1:
                out.append((G.point_along_segment(p, q, t0), G.point_along_segment(p, q, t1)))
    return out


def railing_posts(p, q, floor_z: float, cfg: dict | None = None) -> list[tuple]:
    """``[(verts, faces)]``: the posts of a railing along ``p``-``q`` (at both ends and at most ``post_every``
    apart), from the floor up to the rail (24 Oct 2026: a rail and a panel alone read as a slab, real04's terrace
    'balcony')."""
    c = dict(RAILING, **(cfg or {}))
    length = G.distance(p, q)
    if length <= 1e-6:
        return []
    angle = G.segment_angle_deg(p, q)
    n = max(1, int(math.ceil(length / float(c["post_every"]) - 1e-9)))
    h = float(c["height"]) - float(c["rail"])
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    inset = float(c["post"]) / 2.0
    out = []
    for i in range(n + 1):
        t = min(max(length * i / n, inset), length - inset)
        out.append(geom2d.box((p[0] + ux * t, p[1] + uy * t, floor_z + h / 2.0), (c["post"], c["post"], h), angle))
    return out


def railing_parts(p, q, floor_z: float, cfg: dict | None = None) -> tuple[tuple, tuple]:
    """``((verts, faces) rail, (verts, faces) panel)`` of a railing along ``p``-``q`` standing on ``floor_z``."""
    c = dict(RAILING, **(cfg or {}))
    length = G.distance(p, q)
    mid = G.segment_midpoint(p, q)
    angle = G.segment_angle_deg(p, q)
    h = float(c["height"])
    rail = geom2d.box((mid[0], mid[1], floor_z + h - c["rail"] / 2.0), (length, c["rail"], c["rail"]), angle)
    z0, z1 = floor_z + c["panel_bottom"], floor_z + h - c["rail"]
    panel = geom2d.box((mid[0], mid[1], (z0 + z1) / 2.0), (length, c["panel"], z1 - z0), angle)
    return rail, panel


def recolour_outside(name: str, outward, material) -> bool:
    """Give the faces of object ``name`` that face ``outward`` (a window frame seen from outside) a second
    material slot. True when the object exists and has such faces."""
    import bpy

    ob = bpy.data.objects.get(name)
    if ob is None or ob.type != "MESH":
        return False
    mesh = ob.data
    if material.name not in [m.name for m in mesh.materials if m]:
        mesh.materials.append(material)
    slot = [m.name if m else None for m in mesh.materials].index(material.name)
    hit = False
    for poly in mesh.polygons:
        if poly.normal.x * outward[0] + poly.normal.y * outward[1] > 0.5:
            poly.material_index = slot
            hit = True
    return hit


def build_outside_details(building: dict, level: dict, collection, library, looks: dict, outline,
                          pass_indices: dict, manifest_objects: list, assumed: list,
                          style: dict | None = None) -> dict:
    """The outside details of a level (Milestone 10, §3.2 item 4): a sill under every window on an outer
    wall (``sill_box``; its window's id and pass index, status assumed), a railing (steel rail and glass
    panel) along the edges of every balcony that no wall carries (``railing_edges``; kind ``railing``, the
    room as parent, status assumed), and, when the documents, the brief or the style give the window frames
    another look outside (``looks["window_frame"]`` of ``exterior.resolve_looks`` with a source other than the
    fallback) than inside (``window_frame_look(style, window)``), that look on the frame faces turned outwards
    (``recolour_outside``). Returns ``{"sills": n, "railings": n, "frames_outside": n}``."""
    from wenart.blender import common

    floor_z = float(level["elevation"])
    above = any(float(lv["elevation"]) > floor_z for lv in building["levels"])
    walls = {w["id"]: w for w in building["walls"] if w["level_id"] == level["id"]}
    sill_mat = look_material(library, looks["sill"])
    facade = building.get("facade") if isinstance(building.get("facade"), dict) else {}
    cfg = {}
    sills_cfg = facade.get("sills") if isinstance(facade.get("sills"), dict) else {}
    for key in ("depth", "projection"):
        if isinstance(sills_cfg.get(key), (int, float)):
            cfg[key] = float(sills_cfg[key])
    counts = {"sills": 0, "railings": 0, "frames_outside": 0}
    frame_look = looks.get("window_frame") or {}
    own_outside = bool(frame_look.get("material")) and frame_look.get("source") in ("documents", "brief", "style")
    for o in building["openings"]:
        wall = walls.get(o.get("wall_id"))
        if o["level_id"] != level["id"] or o.get("type") != "window" or wall is None:
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        out = outward_side(wall, outline, (cx, cy))
        if out is None:
            continue
        inside = window_frame_look(style or {}, o)
        outside_frame = look_material(library, frame_look) if own_outside and (
            frame_look["material"] != inside.get("material") or frame_look.get("colour")) else None
        if outside_frame is not None and recolour_outside(f"{o['id']}_frame", out, outside_frame):
            counts["frames_outside"] += 1
            for entry in manifest_objects:
                if entry.get("name") == f"{o['id']}_frame":
                    entry["material_outside"] = outside_frame.name
                    entry["outside_source"] = frame_look.get("reason")
        frame_entry = next((e for e in manifest_objects if e.get("name") == f"{o['id']}_frame"), None)
        depth = ((frame_entry or {}).get("window") or {}).get("frame_depth")     # Milestone 10 window_parts
        verts, faces, info = sill_box(o, wall, level, above, out, dict(cfg, frame_depth=depth) if depth else cfg)
        name = f"{o['id']}_sill"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=o["id"], kind="window",
                                    status="assumed", materials=[sill_mat])
        ob.pass_index = pass_indices.get(o["id"], 0)
        reason = (f"outside sill {info['width']} x {info['depth']} m, {info['projection']} m proud of the facade "
                  f"({'facade.sills' if sills_cfg else 'not drawn'}; size assumed)")
        manifest_objects.append({
            "name": ob.name, "wenart_id": o["id"], "kind": "window", "status": "assumed", "level_id": level["id"],
            "element_id": o["id"], "parent": o["id"], "evidence": [], "material": sill_mat.name,
            "textured": library.textured(sill_mat), "pass_index": ob.pass_index or None,
            "assumed": {"detail": "sill", **info, "reason": reason}, "room_ids": [], "wall_id": o.get("wall_id"),
            "has_geometry": True,
        })
        assumed.append({"object": ob.name, "field": "sill", "value": info["width"], "reason": reason,
                        "parent": o["id"], "kind": "sill"})
        counts["sills"] += 1
    rail_mat = look_material(library, looks.get("railing") or {"material": "steel_brushed"})
    glass = library.guard_glass()           # 30 Oct 2026 (UL145): an outdoor guard's tinted glass
    for room in building["rooms"]:
        if room["level_id"] != level["id"] or room.get("room_type") != "balcony" or len(room["polygon"]) < 3:
            continue
        edges = railing_edges(room, list(walls.values()))
        if not edges:
            continue
        parts, slots = [], []
        kind = D.balustrade_kind(style)
        for p, q in edges:
            metal, panes = D.balustrade(p, q, floor_z, RAILING["height"], kind)   # 25 Oct 2026: real balustrades
            parts += metal + panes
            slots += [0] * sum(len(f) for _v, f in metal) + [1] * sum(len(f) for _v, f in panes)
        verts, faces = geom2d.merge(parts)
        name = f"railing_{room['id']}"
        ob = common.new_mesh_object(name, verts, faces, collection=collection, wenart_id=name, kind="railing",
                                    status="assumed", materials=[rail_mat, glass], face_material_indices=slots)
        ob.pass_index = 0
        reason = (f"balcony edge without a wall: a {RAILING['height']} m {kind.replace('_', ' ')} balustrade "
                  f"(height not drawn: assumed; the kind follows the style)")
        manifest_objects.append({
            "name": ob.name, "wenart_id": name, "kind": "railing", "status": "assumed", "level_id": level["id"],
            "element_id": room["id"], "parent": room["id"], "evidence": [], "material": rail_mat.name,
            "textured": False, "pass_index": 0,
            "assumed": {"detail": "railing", "height_m": RAILING["height"], "edges": len(edges), "reason": reason},
        })
        assumed.append({"object": ob.name, "field": "railing", "value": RAILING["height"], "reason": reason,
                        "parent": room["id"], "kind": "railing"})
        counts["railings"] += 1
    return counts
