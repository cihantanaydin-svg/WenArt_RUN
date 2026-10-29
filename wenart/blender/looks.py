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
# = wenart.style.objects.FAMILY_ACCENTS / FAMILY_ACCENT_DEFAULT (28 Oct 2026; Blender loads this module on its own)
FAMILY_ACCENTS: dict[str, tuple[str, str]] = {
    "scandinavian": ("paint", "pale muted sage"), "japandi": ("paint", "pale taupe"), "modern minimal": ("paint", "greige"),
    "minimal": ("paint", "greige"), "modern": ("paint", "pale dusty blue"), "contemporary": ("paint", "pale taupe"),
    "industrial": ("paint", "light charcoal"), "mediterranean": ("paint", "pale terracotta"), "classic": ("paint", "pale dusty blue"),
    "rustic": ("paint", "pale taupe")}
FAMILY_ACCENT_DEFAULT: tuple[str, str] = ("paint", "greige")
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


# 29 Oct 2026 (lesson UL119, docs/reference_details_20261029.md R25, R34; ``wenart.furniture.room_schemes``): a room
# whose scheme paints it all round: a deep colour (paint, white skirting and ceiling) or a limewash texture
SCHEME_WALLS: dict[str, str] = {"deep_colour": "paint", "limewash": "lime_plaster"}


def scheme_walls(room: Optional[dict], style: Optional[dict] = None) -> Optional[dict]:
    """The wall look a room's scheme gives every wall of the room (``SCHEME_WALLS``), None for a room whose scheme
    keeps the house's walls (or a style that turns the schemes off: ``room_schemes`` false)."""
    sc = (room or {}).get("scheme") if isinstance((room or {}).get("scheme"), dict) else None
    if not sc or (style or {}).get("room_schemes") in (False, "off", "none"):
        return None
    slug = SCHEME_WALLS.get(str(sc.get("walls")))
    if slug is None or not sc.get("wall_colour"):
        return None
    what = "a deep colour all round (R25)" if sc["walls"] == "deep_colour" else "a limewash texture all round (R34)"
    return _look(slug, None, sc["wall_colour"], "scheme", f"the room's scheme {sc.get('key')}: {what}")


def wall_face_material(style: dict, room: Optional[dict] = None) -> dict:
    """The look of the inside wall faces of ``room`` (None: the level's default): the style's ``walls`` slot (its
    material, asset and colour name; a Milestone 3 slug such as ``plaster_cream`` carries no colour). Milestone 11
    (docs/milestone11.md §1.3 M2, §3.2 ``set_material``): a kitchen takes the ``kitchen_walls`` slot when the agent
    set one, else the walls like any other room. 29 Oct 2026 (UL119): a room whose scheme paints it all round takes
    that look (``scheme_walls``)."""
    own = scheme_walls(room, style)
    if own is not None:
        return {"material": own["material"], "asset": None, "tint": None, "colour": own["colour"],
                "scheme": own["reason"]}
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
    accent = _slot(style, "wall_accent") or family_accent(style)
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
        # 29 Oct 2026 (UL119): a room painted all round by its scheme keeps its own look on that wall too (the wall is
        # still the room's anchor wall: the feature panel goes there); an accent scheme names its own pale colour
        # unless the brief names the accent
        own = scheme_walls(room, style)
        sc = room.get("scheme") if isinstance(room.get("scheme"), dict) else {}
        if own is not None:
            out.setdefault(wall_id, {})[room["id"]] = _look(own["material"], None, own["colour"], "scheme",
                                                            f"accent wall of {room['id']}: {why} ({own['reason']})",
                                                            accent=True)
            continue
        colour = accent.get("colour")
        if sc.get("walls") == "accent" and sc.get("wall_colour") and not _slot(style, "wall_accent") \
                and (style or {}).get("room_schemes") not in (False, "off", "none"):
            colour = sc["wall_colour"]
            why += f"; the room's scheme {sc.get('key')}"
        out.setdefault(wall_id, {})[room["id"]] = _look(
            material, accent.get("asset"), colour, "style",
            f"accent wall of {room['id']}: {why} (" + (accent.get("why") or "style wall_accent") + ")", accent=True)
    return out


def family_accent(style: dict) -> dict:
    """The style family's default accent wall (``objects.FAMILY_ACCENTS``) for a style whose brief names none; {} when
    the brief turns accents off (``wall_accent`` ``False`` or ``"none"``)."""
    if (style or {}).get("wall_accent") in (False, "none", "off"):
        return {}
    fam = str((style or {}).get("family") or "").lower()
    material, colour = FAMILY_ACCENTS.get(fam, FAMILY_ACCENT_DEFAULT)
    return {"material": material, "asset": None, "colour": colour, "room_types": list(ACCENT_ROOM_TYPES),
            "why": f"assumed: the {fam or 'house'} style's accent colour {colour} (the brief names no accent wall)"}


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
# 26 Oct 2026 (architect D5, ``architect_actions.act_door_type``): the door styles a decided door names in its
# ``door_style`` (= parametric.DOOR_STYLES), and the glazed style of a ``glazed`` door's operation without one (a gap
# the architect made a glazed door, ``gap_to_door``); both win over the style's swing look.
DECIDED_STYLES: tuple[str, ...] = ("flush", "shaker_panel", "glazed", "pocket", "sliding", "barn", "double",
                                   "entrance", "folding", "glazed_sliding", "sectional")
GLAZED_OPERATION_STYLES: dict[str, str] = {"sliding": "glazed_sliding", "double": "double", "folding": "folding",
                                           "swing": "glazed", "unknown": "glazed"}
FACADE_FINISH_STYLES: tuple[str, ...] = ("sectional",)       # outside doors in the windows' finish without glass


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
        else:
            role, why = role_door_style((opening or {}).get("joins"), style)
            if role is not None:
                door_style = role
                notes.append(why)
    colour = door.get("colour")
    decided, extra = _decided(opening, op, door_style)
    if decided is not None:
        door_style = decided
        notes.append(extra.pop("note"))
        if extra.pop("frame", False):                       # the leaves in the windows' frame finish
            frame = window_frame_look(style, opening)
            slug, asset, colour = frame.get("material") or slug, frame.get("asset"), frame.get("colour")
            notes.append(f"an outside door: its leaves in the windows' frame finish ({slug})")
    family = str((style or {}).get("family") or "").strip().lower()
    # 29 Oct 2026 (D2, docs/reference_details_20261029.md): the family's hardware where the style names none
    handle = door.get("handle") if door.get("handle") in HANDLE_SLUGS else FAMILY_HANDLES.get(family, DEFAULT_HANDLE)
    # 29 Oct 2026 (D3): a wide door between day rooms is a glazed divided-lite door in the family's accent colour
    lite = divided_lite(opening, style, door_style) \
        if decided is None or (decided in ("double", "sliding", "folding") and not extra.get("glazed")) else None
    if lite is not None:
        door_style = lite["door_style"]
        slug, asset, colour = "painted_wood_white", None, lite["colour"]
        extra.update(glazed=True, lites=lite["lites"])
        notes.append(lite["why"])
    product = door_product(style, door_style, veneered=veneer is not None)
    if product:
        kind = product["leaf_detail"]["kind"]
        notes.append(("" if kind == "plain" else f"a {kind} leaf, ") + f"an architrave and hinges where it is framed "
                     f"({product['why']})")
    if family in BLACK_FAMILIES and str(slug).startswith("painted") and not colour and lite is None \
            and door_style in DETAIL_STYLES + ("shaker_panel",) and not (opening or {}).get("outside_door"):
        # 29 Oct 2026 (D2): a painted flush leaf of the modern, industrial and minimal families is black
        colour = "black"
        notes.append(f"a black flush leaf ({family} style, D2)")
    pivot = bool(((opening or {}).get("door_size") or {}).get("pivot")) and door_style == "entrance"
    if pivot:
        notes.append("a pivot entrance door (D5)")
    frameless = frameless_reason(style, opening, door_style)
    reason = (f"door {door_style} (drawn operation {op}{', assumed' if op_assumed else ''}"
              f"{'; ' + '; '.join(notes) if notes else ''}), style door {door.get('material') or 'default'}")
    out = _look(slug, asset, colour, "style", reason, door_style=door_style, handle=handle,
                handle_material=HANDLE_SLUGS[handle], handle_assumed=door.get("handle") not in HANDLE_SLUGS,
                operation=op, operation_assumed=op_assumed, leaf_detail=product.get("leaf_detail"),
                architrave=product.get("architrave"), hinges=product.get("hinges"),
                lock_rose=product.get("lock_rose"), **extra)
    if pivot:
        out["pivot"] = True
    if frameless:
        out["frameless"] = frameless
    if product:
        out["frame_look"] = door_frame_look(style)
    return out


# 29 Oct 2026 (D2, docs/reference_details_20261029.md; H3: "dark (black) door frames and architraves"): the door
# hardware and frames of a family where the style names none. Black frames, architraves and levers in the modern,
# industrial and minimal families (``BLACK_FAMILIES``); black levers in the light wood families too.
FAMILY_HANDLES: dict[str, str] = {"modern": "black", "modern minimal": "black", "minimal": "black",
                                  "industrial": "black", "contemporary": "black", "scandinavian": "black",
                                  "japandi": "black", "rustic": "black", "classic": "brass", "mediterranean": "brass",
                                  "traditional": "brass"}
BLACK_FAMILIES: tuple[str, ...] = ("modern", "modern minimal", "minimal", "industrial")
MODERN_FAMILIES: tuple[str, ...] = ("modern", "modern minimal", "minimal", "contemporary")   # = door_states'
VENEER_GROOVE_FAMILIES: tuple[str, ...] = ("contemporary", "modern minimal", "minimal")      # R28's product leaf


def door_frame_look(style: Optional[dict]) -> dict:
    """The look of a door's frame and architrave (29 Oct 2026, D2 / H3): black in ``BLACK_FAMILIES`` (painted black;
    blackened steel in the industrial family), else the style's trim."""
    family = str((style or {}).get("family") or "").strip().lower()
    if family == "industrial":
        return _look("metal_black", None, None, "style", "black steel door frames (industrial family, D2)")
    if family in BLACK_FAMILIES:
        return _look("painted_wood_white", None, "black", "style", f"black door frames and architraves ({family} "
                                                                   "family, D2)")
    trim = _slot(style or {}, "trim")
    return _look(trim.get("material") or "painted_wood_white", trim.get("asset"), trim.get("colour"), "style",
                 "door frames in the style's trim")


# 29 Oct 2026 (D3): a glazed divided-lite door (sliding or double) for a wide opening between day rooms, in the
# family's accent colour (``objects.FAMILY_ACCENTS``' colour without its "pale" / "muted" / "light"; black where the
# accent is a greige).
DIVIDED_LITE_MIN_M = 1.2
DIVIDED_LITE_ROOMS: tuple[str, ...] = ("living", "dining", "kitchen", "hall")
DIVIDED_LITE_STYLES: tuple[str, ...] = ("double", "sliding", "glazed_sliding", "folding")


def joinery_accent(style: Optional[dict]) -> str:
    fam = str((style or {}).get("family") or "").lower()
    _m, colour = FAMILY_ACCENTS.get(fam, FAMILY_ACCENT_DEFAULT)
    words = [w for w in str(colour).split() if w not in ("pale", "muted", "light", "soft", "warm")]
    name = " ".join(words) or "black"
    try:
        from wenart.style import colours as C
        if name not in C.COLOURS:
            name = words[-1] if words and words[-1] in C.COLOURS else "black"
    except Exception:  # noqa: BLE001 - without the colour table: black
        name = "black"
    return "black" if name in ("greige", "white", "off white") else name


def divided_lite(opening: Optional[dict], style: Optional[dict], door_style: Optional[str]) -> Optional[dict]:
    """``{"door_style", "lites", "colour", "why"}`` of a D3 door (module comment), None for any other door: an inside
    door at least ``DIVIDED_LITE_MIN_M`` wide whose rooms are all day rooms, in a style with a family; a drawn sliding
    door becomes a glazed sliding door, any other a pair of glazed leaves (French doors)."""
    o = opening or {}
    if not str((style or {}).get("family") or "").strip() or o.get("outside_door"):
        return None
    joins = [str(t) for t in o.get("joins") or []]
    if len(joins) != 2 or any(t not in DIVIDED_LITE_ROOMS for t in joins):
        return None
    try:
        w = float(o.get("width") or 0.0)
    except (TypeError, ValueError):
        return None
    if w < DIVIDED_LITE_MIN_M - 1e-9 or (door_style not in DIVIDED_LITE_STYLES and door_style not in SWING_LOOKS):
        return None
    sliding = str(o.get("operation") or "") == "sliding" or door_style in ("sliding", "glazed_sliding")
    colour = joinery_accent(style)
    leaf = w / (2.0 if not sliding else max(2.0, math.ceil(w / 1.2)))
    lites = [1 if leaf < 0.55 else 2, 4]
    return {"door_style": "glazed_sliding" if sliding else "double", "lites": lites, "colour": colour,
            "why": (f"a {w:.2f} m door between day rooms: a glazed divided-lite "
                    f"{'sliding door' if sliding else 'pair of French doors'} in the family's accent colour "
                    f"{colour} (D3)")}


# 29 Oct 2026 (UL122: "Doors looks without frames they need frames", "Sometimes maybe not needed frames but mostly yes
# it does"): every door is framed by default; frameless only where it makes sense, decided in code and recorded.
FRAMELESS_FAMILIES: tuple[str, ...] = ("minimal", "modern minimal", "modern")


def frameless_reason(style: Optional[dict], opening: Optional[dict], door_style: Optional[str]) -> Optional[str]:
    """Why a door has no architrave (a concealed, flush-to-wall door), None for a framed door (pure): the answer of
    the architect's D7 (``opening["frame_decision"]``: the AI's or the user's answer wins, the architect's default
    stays framed), else the style's ``door.frameless`` key in a ``FRAMELESS_FAMILIES`` style, on a flush leaf only."""
    o = opening or {}
    fam = str((style or {}).get("family") or "").strip().lower()
    dec = o.get("frame_decision") if isinstance(o.get("frame_decision"), dict) else {}
    if dec and dec.get("by") not in (None, "architect"):
        return (f"a concealed frameless door ({dec.get('by')}'s answer {dec.get('key') or ''}: "
                f"{dec.get('reason') or ''})") if dec.get("frameless") else None
    if door_style not in ("flush", "pocket") or fam not in FRAMELESS_FAMILIES:
        return None
    if dec.get("frameless"):
        return f"a concealed frameless door (the architect's {dec.get('key') or 'D7'})"
    if _slot(style or {}, "door").get("frameless") is True:
        return f"a concealed frameless flush door (the {fam} style's door.frameless)"
    return None


# 29 Oct 2026 (user: "Better door models needed"; real06 run 20261028-154514-full, real04 run 20261028-183611-full:
# the parametric door was a plain slab in a flat frame flush with the wall): where no library model fits, the
# parametric door is a real product of the house's style family (``parametric.door_parts``): its leaf face detail
# (``LEAF_DETAILS``: routed lines, horizontal or vertical grooves, panels in the period families; on a flush leaf and
# the solid leaves of a pair), an architrave on the room faces and three hinges on the hinge side, with the lever
# pair. ``kind``: ``lined`` (one routed line round each face), ``horizontal`` / ``vertical`` (``count`` V-grooves),
# ``panelled`` (raised stiles and rails), ``plain`` (none: a style whose door slot names it).
LEAF_DETAILS: dict[str, dict] = {
    "scandinavian": {"kind": "lined"}, "japandi": {"kind": "vertical", "count": 4},
    "modern": {"kind": "horizontal", "count": 4}, "contemporary": {"kind": "horizontal", "count": 4},
    "minimal": {"kind": "horizontal", "count": 2}, "modern minimal": {"kind": "horizontal", "count": 2},
    "industrial": {"kind": "horizontal", "count": 3},
    "classic": {"kind": "panelled"}, "rustic": {"kind": "panelled"}, "mediterranean": {"kind": "panelled"},
    "traditional": {"kind": "panelled"},
}
DEFAULT_LEAF_DETAIL: dict = {"kind": "lined"}
LEAF_DETAIL_KINDS: tuple[str, ...] = ("lined", "horizontal", "vertical", "fine_vertical", "panelled", "plain")
DETAIL_STYLES: tuple[str, ...] = ("flush", "double", "folding")     # door styles whose solid leaves take the detail


def door_product(style: Optional[dict], door_style: Optional[str] = None, veneered: bool = False) -> dict:
    """``{"leaf_detail", "architrave", "hinges", "lock_rose", "why"}`` of a parametric door in a style with a family
    (pure; see ``LEAF_DETAILS``), {} for a style without one (a Milestone 3-9 style keeps its door). The style's
    ``door`` slot may name ``leaf_detail`` (a kind of ``LEAF_DETAIL_KINDS``, or a dict with its ``kind`` and
    ``count``); a leaf style other than ``DETAIL_STYLES`` (glazed, shaker panel, entrance, sliding ...) keeps its own
    face. 29 Oct 2026 (R28, D2): a lock rose under the lever; a wood-veneer leaf (``veneered``) of the
    ``VENEER_GROOVE_FAMILIES`` is the flush leaf with fine vertical grooves (one product)."""
    family = str((style or {}).get("family") or "").strip().lower()
    if not family:
        return {}
    named = _slot(style, "door").get("leaf_detail")
    if isinstance(named, str) and named in LEAF_DETAIL_KINDS:
        detail, why = {"kind": named}, "the style's door names it"
    elif isinstance(named, dict) and named.get("kind") in LEAF_DETAIL_KINDS:
        detail, why = dict(named), "the style's door names it"
    elif veneered and family in VENEER_GROOVE_FAMILIES:
        detail, why = {"kind": "fine_vertical"}, f"a wood-veneer leaf with fine vertical grooves ({family} family, R28)"
    else:
        detail = dict(LEAF_DETAILS.get(family, DEFAULT_LEAF_DETAIL))
        why = f"the {family} family's door, assumed" if family in LEAF_DETAILS else f"a {family} door, assumed"
    if door_style is not None and door_style not in DETAIL_STYLES:
        detail = {"kind": "plain"}
    return {"leaf_detail": detail, "architrave": True, "hinges": True, "lock_rose": True, "why": why}


# 28 Oct 2026 (user: "I want better doors inside the house and the outside ... some variation is needed"): with no door
# style in the brief, an inside swing door takes the style of its role: a door into the living rooms (living, dining,
# kitchen) is glazed (daylight into the hall), a door to a private room (bedroom, bathroom, wc, storage) is solid:
# flush in the light families, panelled in the period ones (classic, rustic, mediterranean, traditional).
LIVING_ROOM_TYPES: tuple[str, ...] = ("living", "dining", "kitchen")
PRIVATE_ROOM_TYPES: tuple[str, ...] = ("bedroom", "bathroom", "wc", "storage")
PERIOD_FAMILIES: tuple[str, ...] = ("classic", "rustic", "mediterranean", "traditional")


def role_door_style(joins, style: Optional[dict] = None) -> tuple[Optional[str], str]:
    """``(door style, why)`` of an inside swing door from the room types it joins (``joins``, the shell's
    ``door_sides``), or ``(None, "")`` (a door with no known rooms keeps the flush leaf)."""
    types = {str(t) for t in joins or [] if t}
    family = str((style or {}).get("family") or "").lower()
    if types & set(PRIVATE_ROOM_TYPES):
        if family in PERIOD_FAMILIES:
            return "shaker_panel", f"a private room's door: a panelled leaf in the {family} style"
        return None, ""
    if types & set(LIVING_ROOM_TYPES):
        return "glazed", "a door into the living rooms: a glazed leaf brings daylight into the hall"
    return None, ""


def _decided(opening: Optional[dict], op: str, door_style: str) -> tuple[Optional[str], dict]:
    """``(door style, look fields)`` of a door whose kind the architect decided (D5: ``door_style``, ``glazed``,
    ``leaves``, ``sidelights``, ``door_decision``) or that is ``glazed`` (the glazed style of its operation);
    ``(None, {})`` for any other door, whose look stays as it was. The fields: ``glazed``, ``leaves``,
    ``sidelights``, ``door_type``, ``note`` (for the reason) and ``frame`` (True: an outside door whose glazed or
    sectional leaves take the windows' frame finish)."""
    o = opening or {}
    named = o.get("door_style") if o.get("door_style") in DECIDED_STYLES else None
    glazed = bool(o.get("glazed"))
    if named is None and not glazed:
        return None, {}
    style = named or GLAZED_OPERATION_STYLES.get(op, door_style)
    glass = glazed or style in ("glazed", "glazed_sliding")
    dec = o.get("door_decision") if isinstance(o.get("door_decision"), dict) else {}
    kind = o.get("door_type") or dec.get("kind")
    leaves = o.get("leaves")
    out = {"glazed": glass, "door_type": kind, "sidelights": bool(o.get("sidelights")) or None,
           "leaves": int(leaves) if isinstance(leaves, int) and not isinstance(leaves, bool) and leaves > 0 else None,
           "note": f"the architect's {kind or ('glazed ' + style)} door" + (f" ({dec.get('rule')})" if dec else "")}
    if (glass or style in FACADE_FINISH_STYLES) and (o.get("outside_door") or dec.get("outer")):
        out["frame"] = True
    return style, out


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
    handle or a colour, or the drawing a non-swing operation (``DRAWN_DOOR_OPERATIONS``: the drawn type wins), or
    (26 Oct 2026) the architect decided its kind or made it glazed (``door_style`` / ``glazed``: D5, ``gap_to_door``;
    the Milestone 6 door has one plain leaf)."""
    door = _slot(style, "door")
    if door.get("style") or door.get("handle") or door.get("colour"):
        return True
    if door_product(style):
        # 29 Oct 2026 (UL89): a style with a family builds its parametric doors as products (``door_product``)
        return True
    o = opening or {}
    return o.get("operation") in DRAWN_DOOR_OPERATIONS or o.get("door_style") in DECIDED_STYLES or bool(o.get("glazed"))


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
# 28 Oct 2026 (user on real04's kitchen: the fronts and handles "look plain"; its style.json named no cabinet look):
# the kitchen look of a style family where ``style.json`` ``cabinets`` is silent (assumed, noted): front style, handle
# metal (the hood's metal too: modules.hood_module) and worktop, as kitchens of the family are made (slab fronts with
# slim black bars and a stone top in a modern kitchen, shaker fronts with brass in a classic one, oak tops in the
# Nordic and rustic ones). Kitchen cabinet types only (``CABINET_TYPES``); the other storage keeps its look.
KITCHEN_FAMILY_LOOKS: dict[str, dict[str, str]] = {
    "modern": {"front_style": "flat", "handle": "black", "worktop": "stone"},
    "modern minimal": {"front_style": "flat", "handle": "brushed_steel", "worktop": "stone"},
    "minimal": {"front_style": "flat", "handle": "brushed_steel", "worktop": "stone"},
    "scandinavian": {"front_style": "flat", "handle": "black", "worktop": "wood"},
    "japandi": {"front_style": "flat", "handle": "black", "worktop": "wood"},
    "industrial": {"front_style": "flat", "handle": "black", "worktop": "wood"},
    "mediterranean": {"front_style": "shaker", "handle": "brass", "worktop": "terrazzo"},
    "classic": {"front_style": "shaker", "handle": "brass", "worktop": "stone"},
    "rustic": {"front_style": "shaker", "handle": "black", "worktop": "wood"},
    # 29 Oct 2026 (UL118, K2: "framed fronts for the families that use them"; wenart.blender.kitchen_details)
    "contemporary": {"front_style": "flat", "handle": "black", "worktop": "stone"},
    "modern classic": {"front_style": "shaker", "handle": "black", "worktop": "stone"},
    "transitional": {"front_style": "shaker", "handle": "brushed_steel", "worktop": "stone"},
    "farmhouse": {"front_style": "shaker", "handle": "black", "worktop": "wood"},
}


def kitchen_family_look(ftype: str, style: Optional[dict], have: dict) -> tuple[dict, list[str]]:
    """28 Oct 2026: the keys of ``KITCHEN_FAMILY_LOOKS`` for the style's family a kitchen cabinet piece has no value
    for yet (``have``), with the notes; nothing for another type or an unknown family."""
    if ftype not in CABINET_TYPES:
        return {}, []
    family = str((style or {}).get("family") or "").lower()
    look = KITCHEN_FAMILY_LOOKS.get(family) or {}
    out, notes = {}, []
    for key, value in look.items():
        if have.get(key) is None and (key != "worktop" or ftype in ("kitchen_counter", "kitchen_island")):
            out[key] = value
            notes.append(f"{key} {value}: the {family} family's kitchen look (style.json cabinets names none; assumed)")
    return out, notes
DESIGN_KEYS = ("front_style", "colour", "fabric_colour", "wood", "handle", "worktop", "material_tags", "built_in",
               "vanity", "style_family",
               "towel_colour")       # 29 Oct 2026 (UL124 B26): the bathroom's towels in the room's accent colour


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


def fabric_colour_for(piece: dict, style: Optional[dict]) -> tuple[Optional[str], Optional[str]]:
    """``(fabric colour, source)`` of an upholstered piece (pure; Milestone 13, bug B1 of docs/milestone13.md §1.8:
    the completion stage wrote ``design.material_tags`` only, so the brief's "light grey sofa" reached no sofa):
    ``design.fabric_colour`` (the layout stage), else the fit's ``asset.fabric_colour`` (track T1 writes it from
    the same style keys), else the style's ``furniture.by_type[type].fabric_colour``, else
    ``furniture.fabric_colour``; ``(None, None)`` for other types or without a colour. The same order as
    ``wenart.furniture.fit.fabric_colour_of``."""
    if piece.get("type") not in FABRIC_TYPES:
        return None, None
    design = piece.get("design") if isinstance(piece.get("design"), dict) else {}
    if design.get("fabric_colour"):
        return str(design["fabric_colour"]), "furniture.design (layout stage)"
    asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
    if asset.get("fabric_colour"):
        return str(asset["fabric_colour"]), "asset.fabric_colour (fit stage)"
    furniture = _slot(style, "furniture")
    by_type = (furniture.get("by_type") or {}).get(piece.get("type")) or {}
    if isinstance(by_type, dict) and by_type.get("fabric_colour"):
        return str(by_type["fabric_colour"]), f"style.json furniture.by_type.{piece.get('type')}"
    if furniture.get("fabric_colour"):
        return str(furniture["fabric_colour"]), "style.json furniture.fabric_colour"
    return None, None


def outdoor_design(piece: dict, design: dict, notes: list[str]) -> tuple[dict, list[str]]:
    """28 Oct 2026 (user on real04's roof terrace: "makes no sense to have that table with the carpet outside"): the
    design a module or parametric piece of an open-air room is built in (pure): the fit's ``asset.outdoor_build``
    (``wenart.blender.outdoor.outdoor_asset``: a steel frame with teak) over the piece's design, a painted colour left
    out (teak stays teak); ``(design, notes)`` unchanged for every other piece. Why: without a library model made for
    outside the parametric family built the terrace's table and chairs in the style's indoor wood and fabric."""
    asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
    build = asset.get("outdoor_build") if isinstance(asset.get("outdoor_build"), dict) else None
    if build is None or asset.get("method") not in ("module", "parametric"):
        return design, notes
    out = {k: v for k, v in design.items() if k != "colour"}
    for key in ("material_tags", "wood"):
        if build.get(key):
            out[key] = list(build[key]) if isinstance(build[key], list) else build[key]
    return out, list(notes) + [f"outdoor build: {build.get('why') or 'weather-proof materials'} (asset.outdoor_build)"]


def design_for(piece: dict, style: dict, building: Optional[dict] = None) -> tuple[dict, list[str]]:
    """``(design, notes)`` of a piece for the builders: its ``furniture.design`` as written by the layout stage
    (track B) when it has one; else (the layout stage did not run) from ``style.json``: ``cabinets`` (front style,
    colour, handle, worktop, wood) for counters, islands, wall and tall cabinets, storage, vanities and built-in
    wardrobes, ``furniture.by_type[type]`` (fabric colour, colour, material tags), ``furniture.fabric_colour`` for
    upholstered types and ``furniture.wood``, and the rules: ``vanity`` for a washbasin at least
    ``VANITY_MIN_DEPTH_M`` deep, ``built_in`` for a wardrobe touching walls at both ends (``building`` needed).
    ``notes`` say where each value came from.

    Milestone 13 (bug B1): a given design of an upholstered piece without ``fabric_colour`` takes the style's
    (``fabric_colour_for``), so the brief's fabric colour reaches the parametric and module fabrics; the note says
    where it came from."""
    given = piece.get("design")
    if isinstance(given, dict):
        design = {k: given[k] for k in DESIGN_KEYS if k in given}
        notes = ["furniture.design (layout stage)"]
        if "fabric_colour" not in design:
            colour, source = fabric_colour_for(piece, style)
            if colour:
                design["fabric_colour"] = colour
                notes.append(f"fabric_colour {colour} from {source} (M13 B1: the design had none)")
        return bath_design(piece, design, notes)
    design, notes = _design_from_style(piece, style, building)
    return bath_design(piece, design, notes)


def bath_design(piece: dict, design: dict, notes: list[str]) -> tuple[dict, list[str]]:
    """29 Oct 2026 (lessons UL114, UL124; ``bath_parts``): a bathroom piece's design takes its family's fixture finish
    as its handle (the flush plate, the mixers, the shower fittings) and the room's towel colour, unless the design
    names them (pure)."""
    look = piece.get("bath_look") if isinstance(piece.get("bath_look"), dict) else {}
    if not look:
        return design, notes
    from wenart.blender import bath_parts as BT

    handle = BT.finish_handle(piece)
    if handle and "handle" not in design:
        design = dict(design, handle=handle)
        notes = list(notes) + [f"handle {handle}: the bathroom's {look.get('finish')} finish (UL114)"]
    if look.get("towel_colour") and "towel_colour" not in design:
        design = dict(design, towel_colour=look["towel_colour"])
        notes = list(notes) + [f"towels {look['towel_colour']}: the room's accent (UL124 B26)"]
    return design, notes


def _design_from_style(piece: dict, style: dict, building: Optional[dict] = None) -> tuple[dict, list[str]]:
    """``design_for`` without a layout-stage design: the style's fallback looks (``design_for``'s docstring)."""
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
    extra, extra_notes = kitchen_family_look(ftype, style, design)     # 28 Oct 2026: the family's kitchen look
    design.update(extra)
    notes += extra_notes
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
