"""The looks of walls, wet walls, accent walls, doors, window frames, the facade and furniture designs
(docs/milestone10.md §1.6b rows 14, 15, 17, 20; §4.1, §4.3, §4.4, §4.7; track F).

What: pure functions (no ``bpy``) that ``wenart.blender.shell`` calls through its wrappers of the same names
(``wall_face_material``, ``wet_wall_look``, ``accent_walls``, ``door_look``, ``window_frame_look``,
``facade_look``) and that ``wenart.blender.furniture`` calls for the pieces (``design_for``). A look is a dict
``{"material": slug, "asset", "colour", "params", "source", "reason", ...}`` (only ``material`` is required);
``shell.look_material`` turns it into a Blender material through ``materials.MaterialLibrary.get`` (the colour a
``wenart/style/colours.py`` phrase, ``params`` the procedural look's overrides).

Why here: the style profile (``style.json``, track C) says what the brief asks for; the drawn building decides
where it applies (the wall behind the sofa, the drawn door operation) and the drawn values always win: a sliding
door stays sliding whatever door style the brief names (§4.7), a drawn washbasin keeps its type and only takes
the vanity look (§4.4). Every value no drawing or brief gives is a default, said in ``reason`` / ``assumed``.

How: wall looks are the style slots as they are (a Milestone 3 wall slug without a colour is unchanged); the
accent wall (§4.1: "the wall behind the sofa or the bed head, else the longest wall without a window" in each
living room and bedroom) is found from the room's anchor piece (its back edge within ``ACCENT_REACH_M`` of a wall
parallel to it) or the room's walls (those along the room outline, without a window, the longest overlap); door
looks take the drawn ``operation`` first (``OPERATION_STYLES``), then the style's door style where it fits the
operation (``door_geometry_m10`` / ``window_geometry_m10`` say which openings the shell builds from
``parametric.door_parts`` / ``window_parts``: those with Milestone 10 values; the others keep the Milestone 6-9
door and window); designs come from ``furniture.design`` (written by the layout stage, track B) and, for a piece
without one (a project whose layout stage did not run), from ``style.json`` ``cabinets`` / ``furniture`` and
the rules (vanity: a washbasin at least ``VANITY_MIN_DEPTH_M`` deep; built-in: a wardrobe whose two ends touch
walls).
Imports only the pure style tables and ``wenart.geometry`` (Blender's Python runs it).
"""
from __future__ import annotations

import math
from typing import Optional

from wenart import geometry as G

# --- walls -----------------------------------------------------------------------------------------------------

ACCENT_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom")       # = wenart.style.objects.ACCENT_ROOM_TYPES
ACCENT_ANCHORS: dict[str, tuple[str, ...]] = {"living": ("sofa", "sofa_corner"),
                                              "bedroom": ("bed_double", "bed_single", "bunk_bed")}
ACCENT_REACH_M = 0.3             # the anchor's back edge within this of the wall face
ACCENT_PARALLEL_DEG = 10.0
WALL_ON_OUTLINE_M = 0.06         # a wall bounds a room edge when its face lies within this of the edge


def _slot(style: dict, name: str) -> dict:
    entry = (style or {}).get(name)
    return entry if isinstance(entry, dict) else {}


def _look(material: Optional[str], asset=None, colour=None, source: str = "style", reason: str = "", **extra) -> dict:
    out = {"material": material, "asset": asset, "colour": colour, "source": source, "reason": reason}
    out.update({k: v for k, v in extra.items() if v is not None})
    return out


def wall_face_material(style: dict, room: Optional[dict] = None) -> dict:
    """The look of the inside wall faces of ``room`` (None: the level's default): the style's ``walls`` slot (its
    material, asset and colour name; a Milestone 3 slug such as ``plaster_cream`` carries no colour). Milestone 11
    (docs/milestone11.md §1.3 M2, §3.2 ``set_material``): a kitchen takes the ``kitchen_walls`` slot when the agent
    set one, else the walls like any other room."""
    walls = _slot(style, "walls")
    if room is not None and room.get("room_type") == "kitchen" and _slot(style, "kitchen_walls"):
        walls = _slot(style, "kitchen_walls")
    look = {"material": walls.get("material") or "plaster_white", "asset": walls.get("asset"), "tint": None}
    if walls.get("colour"):                      # the Milestone 9 look stays the same dict without a colour
        look["colour"] = walls["colour"]
    return look


def wet_wall_look(style: dict, room: Optional[dict] = None) -> dict:
    """The look of the wall faces of a wet room: the style's ``wet_walls`` slot (tile kind; the brief's tile size,
    pattern and grout colour go to the procedural tiles as ``params``), else ``walls``."""
    wet = _slot(style, "wet_walls") or _slot(style, "walls")
    params = {k: wet.get(k) for k in ("tile_size_m", "pattern", "grout_colour") if wet.get(k) is not None}
    return _look(wet.get("material") or "tiles_light", wet.get("asset"), wet.get("colour"), "style",
                 "style wet_walls" + (f" ({', '.join(f'{k} {v}' for k, v in params.items())})" if params else ""),
                 params=params or None)


def _unit(dx: float, dy: float) -> tuple[float, float]:
    n = math.hypot(dx, dy)
    return (dx / n, dy / n) if n > 1e-12 else (0.0, 0.0)


def piece_back_mid(piece: dict) -> Optional[tuple[tuple[float, float], tuple[float, float]]]:
    """``(midpoint of the back edge, back direction)`` of a piece with a ``front_deg`` (pure; the depth is the
    footprint side along the front direction), None without a front."""
    front = piece.get("front_deg")
    if front is None:
        return None
    fp = piece["footprint"]
    rot = float(fp.get("rotation_deg") or 0.0)
    local = G.normalise_angle(float(front) - rot)            # the front in the piece frame
    depth = float(fp["size"][1]) if min(abs(local - 270.0), abs(local - 90.0)) < 45.0 else float(fp["size"][0])
    back = math.radians(float(front) + 180.0)
    bx, by = math.cos(back), math.sin(back)
    c = fp["center"]
    return (float(c[0]) + bx * depth / 2.0, float(c[1]) + by * depth / 2.0), (bx, by)


def _wall_dir(wall: dict) -> tuple[float, float]:
    return _unit(float(wall["end"][0]) - float(wall["start"][0]), float(wall["end"][1]) - float(wall["start"][1]))


def wall_behind(piece: dict, walls: list[dict]) -> Optional[str]:
    """The id of the wall the piece's back stands against: parallel within ``ACCENT_PARALLEL_DEG``, the back
    edge's midpoint within half the wall's thickness + ``ACCENT_REACH_M`` of its centre line and between its
    ends; the nearest. None when there is none."""
    found = piece_back_mid(piece)
    if found is None:
        return None
    mid, back = found
    best = None
    for w in walls:
        if G.distance(w["start"], w["end"]) < 1e-6:
            continue
        ux, uy = _wall_dir(w)
        if abs(ux * back[1] - uy * back[0]) < math.cos(math.radians(ACCENT_PARALLEL_DEG)):
            continue                                          # the wall must run across the back direction
        dist = G.point_segment_distance(mid, w["start"], w["end"])
        along = (mid[0] - float(w["start"][0])) * ux + (mid[1] - float(w["start"][1])) * uy
        if not -0.05 <= along <= G.distance(w["start"], w["end"]) + 0.05:
            continue
        if dist <= float(w.get("thickness") or 0.1) / 2.0 + ACCENT_REACH_M and (best is None or dist < best[0]):
            best = (dist, w["id"])
    return best[1] if best else None


def room_walls(room: dict, walls: list[dict]) -> list[tuple[str, float]]:
    """``[(wall id, length along the room outline)]``: the walls whose face runs along an edge of the room polygon
    (parallel, the edge within half the thickness + ``WALL_ON_OUTLINE_M`` of the centre line), with the length of
    the overlap, longest first (then by id)."""
    poly = room.get("polygon") or []
    out: dict[str, float] = {}
    for i in range(len(poly)):
        a, b = poly[i], poly[(i + 1) % len(poly)]
        elen = G.distance(a, b)
        if elen < 1e-6:
            continue
        ex, ey = _unit(float(b[0]) - float(a[0]), float(b[1]) - float(a[1]))
        for w in walls:
            wlen = G.distance(w["start"], w["end"])
            if wlen < 1e-6:
                continue
            ux, uy = _wall_dir(w)
            if abs(ux * ey - uy * ex) > math.sin(math.radians(ACCENT_PARALLEL_DEG)):
                continue
            reach = float(w.get("thickness") or 0.1) / 2.0 + WALL_ON_OUTLINE_M
            mid = G.segment_midpoint(a, b)
            if G.point_segment_distance(mid, w["start"], w["end"]) > reach and \
                    G.point_segment_distance(G.segment_midpoint(w["start"], w["end"]), a, b) > reach:
                continue
            s0 = (float(a[0]) - float(w["start"][0])) * ux + (float(a[1]) - float(w["start"][1])) * uy
            s1 = (float(b[0]) - float(w["start"][0])) * ux + (float(b[1]) - float(w["start"][1])) * uy
            overlap = min(max(s0, s1), wlen) - max(min(s0, s1), 0.0)
            if overlap > 0.05:
                out[w["id"]] = out.get(w["id"], 0.0) + overlap
    return sorted(out.items(), key=lambda kv: (-round(kv[1], 6), kv[0]))


def accent_walls(building: dict, level: dict, style: dict) -> dict:
    """``{wall id: {room id: look}}``: one accent wall per living room and bedroom of ``level`` when the style has a
    ``wall_accent`` (§4.1): the wall behind the room's sofa (corner sofa) or bed head, else the longest wall
    along the room without a window; the look's ``reason`` says which rule chose it. Rooms with neither get none
    (listed in no look; the style's ``wall_accent.rule`` is the report's text)."""
    accent = _slot(style, "wall_accent")
    if not accent or not (accent.get("material") or accent.get("colour")):
        return {}
    types = tuple(accent.get("room_types") or ACCENT_ROOM_TYPES)
    material = accent.get("material") or _slot(style, "walls").get("material") or "paint"
    walls = [w for w in building.get("walls") or [] if w.get("level_id") == level["id"]]
    windows = {o.get("wall_id") for o in building.get("openings") or []
               if o.get("level_id") == level["id"] and o.get("type") == "window"}
    out: dict[str, dict] = {}
    for room in building.get("rooms") or []:
        if (room.get("level_id") != level["id"] or room.get("room_type") not in types
                or len(room.get("polygon") or []) < 3):
            continue
        along = dict(room_walls(room, walls))
        wall_id, why = None, ""
        anchors = ACCENT_ANCHORS.get(room["room_type"], ())
        pieces = sorted((f for f in building.get("furniture") or [] if f.get("room_id") == room["id"]
                         and f.get("type") in anchors and f.get("build", True) is not False),
                        key=lambda f: (anchors.index(f["type"]), f["id"]))
        for piece in pieces:
            wid = wall_behind(piece, walls)
            if wid is not None and wid in along:
                wall_id, why = wid, f"the wall behind the {piece['type'].replace('_', ' ')} {piece['id']}"
                break
        if wall_id is None:
            free = [(wid, length) for wid, length in along.items() if wid not in windows]
            if free:
                wall_id = sorted(free, key=lambda kv: (-round(kv[1], 6), kv[0]))[0][0]
                why = f"the longest wall without a window ({along[wall_id]:.2f} m along the room)"
        if wall_id is None:
            continue
        out.setdefault(wall_id, {})[room["id"]] = _look(
            material, accent.get("asset"), accent.get("colour"), "style",
            f"accent wall of {room['id']}: {why} (style wall_accent)", accent=True)
    return out


# --- doors and windows -------------------------------------------------------------------------------------------

# The drawn operation -> the door style it forces (§4.7: the drawn opening type always wins); None = the style's look.
OPERATION_STYLES: dict[str, Optional[str]] = {"sliding": "sliding", "pocket": "pocket", "double": "double",
                                              "folding": "folding", "fixed": "flush", "swing": None, "unknown": None}
# Door styles that only fit one drawn operation; the others (looks) fit any swing door.
OPERATION_BOUND: dict[str, tuple[str, ...]] = {"sliding": ("sliding",), "barn": ("sliding",), "pocket": ("pocket",),
                                               "double": ("double",)}
SWING_LOOKS: tuple[str, ...] = ("flush", "shaker_panel", "glazed", "entrance")
HANDLE_SLUGS: dict[str, str] = {"brushed_steel": "steel_brushed", "black": "metal_black", "brass": "metal_brass"}
DEFAULT_HANDLE = "brushed_steel"


def _veneer(slug: Optional[str]) -> tuple[Optional[str], Optional[str]]:
    """``(veneer slug, its asset)`` of a wood slug (``vocabulary.veneer_for``), ``(None, None)`` otherwise."""
    try:
        from wenart.style import vocabulary as V
        veneer = V.veneer_for(slug)
        if veneer is not None:
            return veneer, (V.FURNITURE_MATERIALS.get(veneer) or {}).get("asset")
    except Exception:  # noqa: BLE001 - without the vocabulary the style slug stays
        pass
    return None, None


def door_look(style: dict, opening: Optional[dict] = None) -> dict:
    """The look of a door leaf: the style's ``door`` slot (a wood door's veneer, its colour name) with
    ``door_style`` decided by the drawn ``operation`` first (sliding, pocket, double, folding; ``fixed``: a flush
    leaf; null: swing, assumed), then the style's door style where it fits that operation (a barn door only for a
    drawn sliding door), else ``flush``; ``handle`` from the style (``brushed_steel`` assumed)."""
    door = _slot(style, "door")
    slug = door.get("material") or "wood_oak_light"
    asset = door.get("asset")
    veneer, veneer_asset = _veneer(slug)
    if veneer is not None:
        slug, asset = veneer, veneer_asset
    op = (opening or {}).get("operation")
    op_assumed = op is None
    op = op or "swing"
    wanted = door.get("style")
    forced = OPERATION_STYLES.get(op)
    notes = []
    if forced is not None:
        door_style = forced
        if wanted in OPERATION_BOUND and op in OPERATION_BOUND[wanted]:
            door_style = wanted                              # barn for a drawn sliding door
        elif wanted and wanted != forced:
            notes.append(f"the style's {wanted} door does not fit the drawn {op} door")
    elif wanted in SWING_LOOKS:
        door_style = wanted
    else:
        door_style = "flush"
        if wanted:
            notes.append(f"the style's {wanted} door does not fit a drawn swing door")
    handle = door.get("handle") if door.get("handle") in HANDLE_SLUGS else DEFAULT_HANDLE
    reason = (f"door {door_style} (drawn operation {op}{', assumed' if op_assumed else ''}"
              f"{'; ' + '; '.join(notes) if notes else ''}), style door {door.get('material') or 'default'}")
    return _look(slug, asset, door.get("colour"), "style", reason, door_style=door_style, handle=handle,
                 handle_material=HANDLE_SLUGS[handle], handle_assumed=door.get("handle") not in HANDLE_SLUGS,
                 operation=op, operation_assumed=op_assumed)


def window_frame_look(style: dict, opening: Optional[dict] = None) -> dict:
    """The look of a window frame seen from inside: the style's ``window_frame`` slot (``pvc_white``,
    ``aluminium_anthracite``, ``steel_black``, ``dark_bronze``, ``oak``, ``painted_metal_white`` in a colour) and the
    frame profile of that material (``parametric.window_profile``, assumed sizes); the mullions and transoms the
    opening gives (``mullions`` / ``transoms`` counts when the building has them, else none)."""
    frame = _slot(style, "window_frame")
    material = frame.get("material") or "painted_metal_white"
    out = _look(material, frame.get("asset"), frame.get("colour"), "style",
                f"style window_frame {material}" + (f" in {frame['colour']}" if frame.get("colour") else ""))
    for key in ("mullions", "transoms"):
        value = (opening or {}).get(key)
        if isinstance(value, int) and not isinstance(value, bool) and value > 0:
            out[key] = value
    return out


# Which doors and windows get the Milestone 10 geometry (``parametric.door_parts`` / ``window_parts``, built by
# ``shell.build_openings``): those the style or the drawing gives Milestone 10 values; a project without them keeps
# the Milestone 6-9 door (frame, leaf, lever pair) and window (frame, glass), so the M3-M9 scenes stay as they were.
DRAWN_DOOR_OPERATIONS: tuple[str, ...] = ("double", "sliding", "pocket", "folding", "fixed")
M10_FRAME_MATERIALS: tuple[str, ...] = ("pvc_white", "aluminium_anthracite", "steel_black", "dark_bronze", "oak")


def _count(opening: Optional[dict], key: str) -> int:
    value = (opening or {}).get(key)
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else 0


def door_geometry_m10(style: dict, opening: Optional[dict] = None) -> bool:
    """True when a door is built from ``parametric.door_parts``: the style's ``door`` slot names a door style, a
    handle or a colour, or the drawing a non-swing operation (``DRAWN_DOOR_OPERATIONS``: the drawn type wins)."""
    door = _slot(style, "door")
    if door.get("style") or door.get("handle") or door.get("colour"):
        return True
    return (opening or {}).get("operation") in DRAWN_DOOR_OPERATIONS


def window_geometry_m10(style: dict, opening: Optional[dict] = None) -> bool:
    """True when a window is built from ``parametric.window_parts`` (the frame material's profile, mullions,
    transoms, an inside sill): the style's ``window_frame`` is a Milestone 10 frame material
    (``M10_FRAME_MATERIALS``) or has a colour, or the opening gives mullions or transoms."""
    frame = _slot(style, "window_frame")
    if frame.get("colour") or frame.get("material") in M10_FRAME_MATERIALS:
        return True
    return _count(opening, "mullions") > 0 or _count(opening, "transoms") > 0


def facade_look(looks: dict, wall: Optional[dict] = None) -> dict:
    """The outside look of an outer wall: the resolved facade look (``exterior.resolve_looks``: documents > brief >
    style > fallback; the same dict for every wall); a drawn facade part of one wall is the shell's own face slot."""
    return looks["facade"]


# --- furniture designs (§1.6b row 15; §4.4) -------------------------------------------------------------------------

# wenart.furniture.schemas (track B) tables, repeated: that module needs jsonschema, which Blender's Python lacks
# (tests/test_cabinets.py keeps the copies equal).
CABINET_TYPES: tuple[str, ...] = ("kitchen_counter", "kitchen_island", "wall_cabinet", "tall_cabinet")
STORAGE_TYPES: tuple[str, ...] = ("sideboard", "shoe_cabinet", "display_cabinet")
FABRIC_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "armchair", "chaise", "ottoman", "bench", "bed_single",
                                 "bed_double")
VANITY_MIN_DEPTH_M = 0.45
BUILT_IN_REACH_M = 0.05          # a wardrobe end within this of a wall face counts as touching it
DESIGN_KEYS = ("front_style", "colour", "fabric_colour", "wood", "handle", "worktop", "material_tags", "built_in",
               "vanity", "style_family")


def _front_depth(piece: dict) -> float:
    found = piece_back_mid(piece)
    fp = piece["footprint"]
    if found is None:
        return float(fp["size"][1])
    mid, _back = found
    return 2.0 * G.distance(mid, fp["center"])


def touches_walls_at_both_ends(piece: dict, walls: list[dict]) -> bool:
    """True when both ends of a piece (the midpoints of its sides left and right of its front) lie within
    ``BUILT_IN_REACH_M`` of a wall face (the built-in wardrobe rule, §4.4)."""
    fp = piece["footprint"]
    w, d = float(fp["size"][0]), float(fp["size"][1])
    rot = float(fp.get("rotation_deg") or 0.0)
    if piece_back_mid(piece) is not None and abs(_front_depth(piece) - w) < 1e-6 and abs(w - d) > 1e-6:
        w, rot = d, rot + 90.0                               # the front runs along the footprint's local X
    c = (float(fp["center"][0]), float(fp["center"][1]))
    ends = [G.rotate_point((c[0] + s * w / 2.0, c[1]), rot, c) for s in (-1, 1)]
    for p in ends:
        if not any(G.point_segment_distance(p, x["start"], x["end"]) <= float(x.get("thickness") or 0.1) / 2.0
                   + BUILT_IN_REACH_M for x in walls if G.distance(x["start"], x["end"]) > 1e-6):
            return False
    return True


def design_for(piece: dict, style: dict, building: Optional[dict] = None) -> tuple[dict, list[str]]:
    """``(design, notes)`` of a piece for the builders: its ``furniture.design`` as written by the layout stage
    (track B) when it has one; else (the layout stage did not run) from ``style.json``: ``cabinets`` (front style,
    colour, handle, worktop, wood) for counters, islands, wall and tall cabinets, storage, vanities and built-in
    wardrobes, ``furniture.by_type[type]`` (fabric colour, colour, material tags), ``furniture.fabric_colour`` for
    upholstered types and ``furniture.wood``, and the rules: ``vanity`` for a washbasin at least
    ``VANITY_MIN_DEPTH_M`` deep, ``built_in`` for a wardrobe touching walls at both ends (``building`` needed).
    ``notes`` say where each value came from."""
    given = piece.get("design")
    if isinstance(given, dict):
        return {k: given[k] for k in DESIGN_KEYS if k in given}, ["furniture.design (layout stage)"]
    ftype = piece.get("type")
    design: dict = {}
    notes: list[str] = []
    cab = _slot(style, "cabinets")
    furniture = _slot(style, "furniture")
    by_type = (furniture.get("by_type") or {}).get(ftype) or {}
    if ftype == "washbasin" and _front_depth(piece) >= VANITY_MIN_DEPTH_M - 1e-9:
        design["vanity"] = True
        notes.append(f"vanity: washbasin {_front_depth(piece):.2f} m deep (>= {VANITY_MIN_DEPTH_M} m, rule)")
    if ftype == "wardrobe" and building is not None:
        walls = [w for w in building.get("walls") or [] if w.get("level_id") == piece.get("level_id")]
        if touches_walls_at_both_ends(piece, walls):
            design["built_in"] = True
            notes.append("built_in: the wardrobe touches walls at both ends (rule)")
    if ftype in CABINET_TYPES + STORAGE_TYPES or design.get("vanity") or design.get("built_in"):
        for key in ("front_style", "colour", "handle", "worktop", "wood"):
            if cab.get(key) is not None and (key != "worktop" or ftype in ("kitchen_counter", "kitchen_island")):
                design[key] = cab[key]
                notes.append(f"{key} {cab[key]} from style.json cabinets")
    for key in ("fabric_colour", "colour", "material_tags"):
        if by_type.get(key) and key not in design:
            design[key] = by_type[key]
            notes.append(f"{key} {by_type[key]} from style.json furniture.by_type.{ftype}")
    if ftype in FABRIC_TYPES and "fabric_colour" not in design and furniture.get("fabric_colour"):
        design["fabric_colour"] = furniture["fabric_colour"]
        notes.append(f"fabric_colour {furniture['fabric_colour']} from style.json furniture")
    if furniture.get("wood") and "wood" not in design:
        design["wood"] = furniture["wood"]
        notes.append(f"wood {furniture['wood']} from style.json furniture")
    return design, notes
