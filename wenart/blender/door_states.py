"""Doors as a designer shows them: open by default, sized by role, framed (29 Oct 2026; lessons UL116, UL117, UL122;
docs/reference_details_20261029.md D1, D5).

The user (29 Oct 2026): "Also we need better doors, not all the doors needs to be closed in default", "Not every
single one of them with the same dimension we can change the dimentions", "Doors looks without frames they need
frames" and "Sometimes maybe not needed frames but mostly yes it does". Every rule here is general (CLAUDE.md); the
house that showed it (real06: 13 doors, all closed, all 2.10 m) is the test case.

What (pure, no ``bpy``; ``build.py`` applies both steps to the building before any geometry is made, so the walls'
cuts, the library door plan, the cameras, the build and the checks read one record):

- ``apply_sizes(building, style)`` (D5): the door sizes by role and family. The entrance is taller
  (``ENTRANCE_HEIGHT_M``; a pivot door ``PIVOT_HEIGHT_M`` in the modern families, ``MODERN_FAMILIES``) and at least an
  entrance product wide (``ENTRANCE_WIDTHS_M``, ``PIVOT_WIDTHS_M``) where its wall allows; a door between day rooms
  (``DAY_TYPES``) in the modern families runs to the ceiling; every other door stays ``STANDARD_HEIGHT_M``. A drawn
  width stays unless it is no real product size (``PRODUCT_WIDTHS_M`` within ``WIDTH_TOL_M``): then the nearest one
  that fits its wall. Only a height the documents do not give changes (the opening's ``assumed`` lists ``height``);
  every change keeps ``drawn_width`` / ``drawn_height``, is ``adjusted_by_ai`` (by code) and is recorded in
  ``door_size`` with the reason. A width grows only where the wall has room (``WALL_END_CLEAR_M`` from its ends,
  ``OPENING_GAP_M`` from the other openings of the wall) and no piece stands in the new strip; a height grows only on a
  level without a sloped ceiling and under every opening above it on the wall.
- ``apply_states(building, style, cameras)`` (D1; UL127, user: "Leaving all the doors open in default could be a
  good approach"): the leaf of every door: ``open`` (every interior door, whatever room it leads to: a swing leaf at
  ``OPEN_DEG`` into the room it opens into, its hinge at the jamb nearer the room's corner so the leaf stands by the
  wall beside it, or the drawn ``hinge_side``, or the side a camera's view needs, ``camera_hinge``; a sliding leaf slid
  along its wall face, a pocket leaf into the wall, the moving panels of a glazed sliding door behind the fixed ones;
  both leaves of a pair), ``ajar`` (a leaf a piece, a wall or another door's leaf stops: at its widest free angle,
  ``AJAR_STEPS``) or ``closed`` (the entrance and the outside and terrace doors, garage, sectional, folding and fixed
  doors, a leaf that cannot open 15 degrees). The documents or an answer (the architect's D9) may fix a state
  (``open_state``: open, ajar, closed), the brief close them all (``doors_open: false``). Every choice is recorded in
  ``leaf_state`` (``state``, ``angle_deg``, ``slide_m``, ``hinge``, ``hinge_side``, ``side``, ``into``, the open
  leaf's plan outline ``leaf_polys``, ``reason``, ``by``) and listed as assumed, so the checks and the vision checks
  know a leaf is open.
- Only a style with a family gets either step (a Milestone 3-9 style keeps its closed doors of drawn sizes, as the
  parametric product door of ``looks.door_product``).

Checks (pure; the model review's M29 and Argus' U33, lessons UL116, UL117, UL120, UL122):
``state_problems(building)``: every inside door closed in a house whose doors could open (``all_closed``), all doors
one size or an entrance no bigger than the inside doors (``one_size``), an open leaf in a piece (``leaf_in_piece``),
a dressing room with closed wardrobe fronts only (``dressing_closed_fronts``, ``wardrobe_fronts.is_see_through``), a
view showing only closed doors though one leads to a room worth showing (``view_closed_doors``, UL126);
``frame_problems(manifest)``: a door built without a frame and without a recorded frameless reason (``no_frame``),
an indoor face without its architrave and no reason (``no_architrave``).

30 Oct 2026 (lessons UL128, UL132; the user on real04 run 20261029-201533-full: "Some frames coming out of the roof it
needs fixing", "Door frame needs fixing"): D5 put d_L1_001 / 002 back to 2.10 m under a 1.84 m slope ("a sloped
ceiling over the level: 2.10 m kept", after the roof clip had made them 1.80 m) and the bathroom doors d_L1_004 / 005 to
2.10 m under 1.03 m: their frames, architraves and open leaves stood through the roof, and inside the jamb ran up into
the slope with its head hidden above it. Now one height serves the opening, the leaf, the jamb lining, the head and the
architrave (they are all built from the opening's height) and it fits under the ceiling at the door:

- ``head_room(o, wall, level)``: the lowest sloped ceiling over the door's frame (its architrave on both faces)
  less ``ROOF_HEAD_GAP_M``; D5's ``_door_height`` never goes over it.
- ``apply_under_roof(building)`` (after D5, every style): a door reaching over its head room is lowered to it when that
  leaves ``MIN_CLEAR_M``; else it slides along its wall (at most ``ROOF_SLIDE_MAX_M``, the same rooms at its centre
  and both jambs) to the nearest spot that does; else it is lowered all the same with a warning (``under_roof.fits``
  False: the model review's M31 asks for a dormer). A drawn height over the wall at the door is a clear reading error
  (a door cannot be taller than its wall there) and is lowered too; every change keeps ``drawn_height`` /
  ``drawn_center``, is ``adjusted_by_ai`` by code, recorded in ``under_roof`` and assumed.
- An open leaf is tried under the ceiling over it (``leaf_frame``'s ``head``, ``leaf_under_ceiling``): a leaf the slope
  stops stands ajar at a smaller angle or on the other jamb, swings into the other room when no swing side is drawn
  (``swing_turned``, the build's ``swing_side``), else stays closed with the reason.
- ``census_problems`` (M29, Argus U33; the frame's ``census``, ``parametric.frame_census``): a frame part over its
  opening's head by more than the architrave's ``HEAD_RISE_M`` (``frame_taller``), a lining or an architrave face with
  jambs and no head (``jamb_without_head``) or one jamb only (``one_jamb``).
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Optional, Sequence

from wenart import geometry as G

# --- D5: sizes -----------------------------------------------------------------------------------------------------
# Typical joinery sizes (assumed: no drawing gives them): EU inside door sets 60-100 cm, entrance sets 90-120 cm.
PRODUCT_WIDTHS_M: tuple[float, ...] = (0.60, 0.70, 0.75, 0.80, 0.85, 0.90, 1.00)
ENTRANCE_WIDTHS_M: tuple[float, ...] = (0.90, 1.00, 1.10, 1.20)
PIVOT_WIDTHS_M: tuple[float, ...] = (1.00, 1.10, 1.20)
WIDE_PRODUCT_M = 1.20             # a door this wide or wider is a pair or a sliding door: its width stays as drawn
WIDTH_TOL_M = 0.015               # a drawn width within this of a product width is that product
STANDARD_HEIGHT_M = 2.10
ENTRANCE_HEIGHT_M = 2.30
PIVOT_HEIGHT_M = 2.40
HEIGHT_TOL_M = 0.005
MODERN_FAMILIES: tuple[str, ...] = ("modern", "modern minimal", "minimal", "contemporary")
DAY_TYPES: tuple[str, ...] = ("living", "dining", "kitchen", "hall")
WALL_END_CLEAR_M = 0.10           # a widened door keeps this much wall at the wall's ends ...
OPENING_GAP_M = 0.10              # ... and between its frame and another opening of the wall (= door_spacing.PAIR_GAP_M)
STRIP_M = 0.60                    # the floor strip in front of a widened door that must stay free of pieces

# --- D1: states ----------------------------------------------------------------------------------------------------
OPEN_DEG = 90.0                   # an open leaf stands square to its wall, by the wall beside it
AJAR_DEG = 20.0                   # a door set ajar (the documents', an answer's) stands this far open
AJAR_STEPS: tuple[float, ...] = (80.0, 70.0, 60.0, 50.0, 40.0, 30.0, 20.0, 15.0)   # UL127: the widest free angle
STATES: tuple[str, ...] = ("open", "ajar", "closed")
WET_TYPES: tuple[str, ...] = ("bathroom", "wc", "toilet", "shower")
STORAGE_TYPES: tuple[str, ...] = ("storage", "closet", "pantry", "utility", "technical", "shaft", "laundry")
DRESSING_TYPES: tuple[str, ...] = ("dressing",)
OPEN_AIR_TYPES: tuple[str, ...] = ("balcony", "terrace", "roof_terrace", "loggia", "veranda", "patio", "porch",
                                   "garden")
# = groups.yaml room_aliases.dressing (used when the furniture package cannot be imported, inside Blender without it)
DRESSING_WORDS: tuple[str, ...] = ("dressing", "walk in", "walkin", "closet", "wardrobe room", "soyunma", "giyinme",
                                   "gardirop", "vestiaire", "ankleide", "vestidor", "guardarropa", "garderobe")
HIT_M2 = 0.003                    # an overlap of a leaf (or its sweep) with a piece this big is a hit
SWEEP_STEPS = 6                   # the sweep's arc as this many chords (a convex fan)
FLOOR_DECOR: tuple[str, ...] = ("plant", "plant_large", "potted_plant", "floor_vase", "vase_floor", "floor_lamp",
                                "basket", "laundry_basket", "pouf", "bean_bag", "umbrella_stand", "magazine_rack")
SIGHT_M = 12.0                    # a camera looks through a door its centre line crosses within this distance
FRAME_W_M = 0.05                  # = parametric.DOOR_FRAME_W
LEAF_CLEAR_M = 0.01               # the leaf is this much narrower than the frame's clear width
LEAF_T_M = 0.04                   # = parametric.DOOR_LEAF_T
SLIDE_OVERLAP_M = 0.05            # = parametric.SLIDING_OVERLAP_M
SLIDE_STANDOFF_M = 0.012          # = parametric.SLIDING_STANDOFF_M
SWING_OPERATIONS: tuple[str, ...] = ("swing", "unknown", "double", "")
# --- UL128 / UL132 (30 Oct 2026): doors under the roof ---------------------------------------------------------------
ROOF_HEAD_GAP_M = 0.05            # = roof.OPENING_ROOF_GAP: a door's opening stops this far under the sloped ceiling
HEAD_RISE_M = 0.023               # the architrave's head over the opening (parametric.architrave_boxes: W + reveal - frame)
FRAME_ALONG_M = 0.023             # the architrave's outer edge past each side of the opening (the same sum)
MIN_CLEAR_M = 1.60                # = roof.MIN_OPENING_HEIGHT["door"]: a door lower than this does not fit (a finding)
ROOF_SLIDE_MAX_M = 0.50           # a door that does not fit slides at most this far along its wall (as a piece's fix)
ROOF_SLIDE_STEP_M = 0.05
LEAF_HEAD_GAP_M = 0.01            # an open leaf stays this far under the sloped ceiling over it
SLIDE_OPERATIONS: tuple[str, ...] = ("sliding", "pocket")


def family_of(style) -> str:
    if isinstance(style, str):
        return style.strip().lower()
    return str((style or {}).get("family") or "").strip().lower()


def active(style) -> bool:
    """Only a style with a family gets the door states and the role sizes (module docstring)."""
    return bool(family_of(style))


# --------------------------------------------------------------------------------------------------- the plan model

def _walls(building: dict) -> dict:
    return {w["id"]: w for w in building.get("walls") or [] if w.get("id")}


def _levels(building: dict) -> dict:
    return {lv["id"]: lv for lv in building.get("levels") or [] if lv.get("id")}


def _rooms(building: dict, level_id) -> list[dict]:
    return [r for r in building.get("rooms") or [] if r.get("level_id") == level_id
            and len(r.get("polygon") or []) >= 3]


def _rtype(room: Optional[dict]) -> str:
    return str((room or {}).get("room_type") or "").strip().lower()


def _axis(wall: dict) -> tuple[tuple[float, float], tuple[float, float], float]:
    (ax, ay), (bx, by) = wall["start"][:2], wall["end"][:2]
    length = math.hypot(bx - ax, by - ay)
    if length < 1e-9:
        return (float(ax), float(ay)), (1.0, 0.0), 0.0
    return (float(ax), float(ay)), ((bx - ax) / length, (by - ay) / length), length


def centre_on_wall(o: dict, wall: dict) -> tuple[float, float, float]:
    """``(cx, cy, t)``: the opening's centre on its wall's centre line and its distance from the wall's start."""
    a, u, _length = _axis(wall)
    px, py = float(o["center"][0]), float(o["center"][1])
    t = (px - a[0]) * u[0] + (py - a[1]) * u[1]
    return a[0] + u[0] * t, a[1] + u[1] * t, t


def sides(o: dict, wall: dict, rooms: Sequence[dict]) -> list[Optional[dict]]:
    """The rooms on the two sides of a door (the left of the wall direction first; None: no room, outside)."""
    cx, cy, _t = centre_on_wall(o, wall)
    nx, ny = G.unit_normal_left(wall["start"], wall["end"])
    reach = float(wall.get("thickness") or 0.2) / 2.0 + 0.05
    out = []
    for s in (1.0, -1.0):
        p = (cx + s * nx * reach, cy + s * ny * reach)
        out.append(next((r for r in rooms if G.point_in_polygon(p, r["polygon"])), None))
    return out


def swing_side(o: dict, wall: dict, rooms: Sequence[dict]) -> tuple[int, Optional[str], bool]:
    """``(side, room id, assumed)``: the side the door opens into, as the build hangs it
    (``shell.opening_room_side``: its ``swing_side``, else the only room, else the wall's right side, assumed)."""
    from wenart.blender import shell as SH

    cx, cy, _t = centre_on_wall(o, wall)
    return SH.opening_room_side((cx, cy), wall, list(rooms), o.get("swing_side"))


def main_entrance(building: dict) -> Optional[str]:
    """The id of the main entrance door: ``site.entrances`` (its ``main`` record, else the first), else a door the
    architect made the entrance (``door_type`` / ``door_decision.kind`` ``entrance``)."""
    recs = [r for r in ((building.get("site") or {}).get("entrances") or []) if isinstance(r, dict)
            and not r.get("into_air") and not r.get("below_ground")]
    main = next((r.get("door_id") for r in recs if r.get("main")), None)
    if main is None and recs:
        main = recs[0].get("door_id")
    if main is not None:
        return main
    for o in building.get("openings") or []:
        dec = o.get("door_decision") if isinstance(o.get("door_decision"), dict) else {}
        if o.get("type") == "door" and (o.get("door_type") or dec.get("kind")) == "entrance":
            return o.get("id")
    return None


def _label_words(room: dict) -> list[str]:
    import re

    from wenart import textfold as B          # fold_ascii without jsonschema (Blender's Python)

    text = " ".join(str(room.get(k) or "") for k in ("label", "label_raw"))
    return [w for w in re.split(r"[^a-z0-9]+", B.fold_ascii(text).lower()) if w]


_ALIAS_WORDS: list = []
GROUPS_YAML = Path(__file__).resolve().parents[1] / "furniture" / "groups.yaml"     # = furniture.groups.GROUPS_YAML


def dressing_words() -> tuple[str, ...]:
    """``DRESSING_WORDS`` and the furniture program's ``groups.yaml`` ``room_aliases.dressing`` words (read once; the
    constant alone inside Blender without the furniture package's shapely)."""
    if not _ALIAS_WORDS:
        words = list(DRESSING_WORDS)
        try:
            # the file itself, not wenart.furniture.groups (its import closure is the whole furniture program: the
            # gate's code fingerprint would follow every furniture change; tests/test_run_stages.py)
            import yaml

            data = yaml.safe_load(GROUPS_YAML.read_text(encoding="utf-8")) or {}
            words += [str(w) for w in ((data.get("room_aliases") or {}).get("dressing") or {}).get("words") or []]
        except Exception:  # noqa: BLE001 - the constant stands
            pass
        _ALIAS_WORDS.append(tuple(dict.fromkeys(w.lower() for w in words)))
    return _ALIAS_WORDS[0]


def is_dressing(building: dict, room: Optional[dict]) -> bool:
    """A dressing room or walk-in closet (pure, cheap: no walkway geometry): its type, else a word of its label
    (``dressing_words``: a Turkish keyword at the start of a word, an English or a two-word keyword as whole words, as
    the furniture program reads labels). The program's other rule (a small room whose every door opens into a
    bedroom) is ``wardrobe_fronts.walk_in``'s facing runs here."""
    if room is None:
        return False
    if _rtype(room) in DRESSING_TYPES:
        return True
    if _rtype(room) not in ("storage", "other", "unknown", "", "closet", "hall"):
        return False
    words = _label_words(room)
    text = " " + " ".join(words) + " "
    return any((f" {w} " in text) if " " in w else any(x.startswith(w) for x in words) for w in dressing_words())


def door_role(building: dict, o: dict, wall: Optional[dict], room_sides: Sequence[Optional[dict]],
              entrance: Optional[str]) -> str:
    """``entrance`` | ``outside`` | ``wet`` | ``storage`` | ``dressing`` | ``day`` | ``inside`` of a door."""
    if o.get("id") == entrance:
        return "entrance"
    if wall is None or None in room_sides or o.get("outside_door") \
            or any(_rtype(r) in OPEN_AIR_TYPES for r in room_sides):
        return "outside"
    types = {_rtype(r) for r in room_sides}
    if types & set(WET_TYPES):
        return "wet"
    if any(is_dressing(building, r) for r in room_sides):
        return "dressing"
    if types & set(STORAGE_TYPES):
        return "storage"
    if types <= set(DAY_TYPES):
        return "day"
    return "inside"


# --------------------------------------------------------------------------------------------------------- D5 sizes

def nearest_product(width: float, sizes: Sequence[float]) -> float:
    """The product width nearest ``width`` (ties: the narrower one, which always fits its wall)."""
    return min(sizes, key=lambda s: (abs(s - width), s))


def is_product(width: float, sizes: Sequence[float] = PRODUCT_WIDTHS_M) -> bool:
    return any(abs(width - s) <= WIDTH_TOL_M + 1e-9 for s in sizes)


def width_room(o: dict, wall: dict, openings: Sequence[dict]) -> tuple[float, float]:
    """``(room before, room after)``: how far the door's edges may move along its wall (pure): to ``WALL_END_CLEAR_M``
    from the wall's ends and ``OPENING_GAP_M`` from the other openings of the wall."""
    _a, _u, length = _axis(wall)
    _cx, _cy, t = centre_on_wall(o, wall)
    w = float(o.get("width") or 0.0)
    lo, hi = t - w / 2.0, t + w / 2.0
    before, after = lo - WALL_END_CLEAR_M, length - WALL_END_CLEAR_M - hi
    for x in openings:
        if x is o or x.get("id") == o.get("id") or x.get("wall_id") != o.get("wall_id") or not x.get("center"):
            continue
        _x, _y, tx = centre_on_wall(x, wall)
        wx = float(x.get("width") or 0.0)
        if tx + wx / 2.0 <= lo + 1e-9:
            before = min(before, lo - (tx + wx / 2.0) - OPENING_GAP_M)
        elif tx - wx / 2.0 >= hi - 1e-9:
            after = min(after, (tx - wx / 2.0) - hi - OPENING_GAP_M)
        else:
            before = after = min(before, after, 0.0)
    return max(0.0, before), max(0.0, after)


def piece_polys(building: dict, level_id) -> list[tuple[str, str, list]]:
    """``[(id, type, polygon)]`` of the built pieces of a level (``shell.piece_built``) and its free-standing floor
    decor (``FLOOR_DECOR``): what a leaf or its swing must not hit."""
    out = []
    for f in building.get("furniture") or []:
        if f.get("level_id") != level_id or f.get("build", True) is False or f.get("type") == "unknown":
            continue
        asset = f.get("asset") if isinstance(f.get("asset"), dict) else {}
        fp = f.get("footprint") or {}
        if asset.get("method") == "none" or not fp.get("center") or not fp.get("size"):
            continue
        if str(f.get("type")) in ("stair",):
            continue                                       # the stair is fixed equipment: the walls' checks own it
        poly = G.rotated_rectangle(fp["center"][:2], fp["size"][:2], float(fp.get("rotation_deg") or 0.0))
        out.append((str(f.get("id")), str(f.get("type")), [tuple(p) for p in poly]))
    for d in building.get("decor") or []:
        if d.get("level_id") != level_id or d.get("host_id") or str(d.get("type")) not in FLOOR_DECOR:
            continue
        c, s = d.get("center"), d.get("size")
        if not c or not s or len(s) < 2:
            continue
        poly = G.rotated_rectangle(c[:2], s[:2], float(d.get("rotation_deg") or 0.0))
        out.append((str(d.get("id")), str(d.get("type")), [tuple(p) for p in poly]))
    return out + wall_hung_polys(building, level_id)          # UL190: a leaf never rests over a mirror or a picture


# 30 Oct 2026 (lesson UL190, user on real04 run 20261030-112241-full: "mirror staying behind the door in this case door can
# be closed"): a wall-hung item (a mirror, a picture) is in the way of an open leaf that would rest against it: the
# strip of wall it hangs on, this deep into the room, counts as a piece the leaf may not cover (the door opens less or
# stays closed)
WALL_HUNG_TYPES: tuple[str, ...] = ("mirror", "wall_art", "wall_discs", "clock", "desk_wall_unit", "wall_shelf")
WALL_HUNG_DEPTH_M = 0.15


def wall_hung_polys(building: dict, level_id) -> list[tuple[str, str, list]]:
    """``[(id, type, polygon)]`` of the level's wall-hung items (``WALL_HUNG_TYPES`` with a ``wall_point``): their width
    along the wall, ``WALL_HUNG_DEPTH_M`` into the room from the wall face (UL190)."""
    out = []
    for d in building.get("decor") or []:
        if d.get("level_id") != level_id or str(d.get("type")) not in WALL_HUNG_TYPES or d.get("build") is False:
            continue
        wp, c, size = d.get("wall_point"), d.get("center"), d.get("size")
        if not wp or not c or not size:
            continue
        nx, ny = float(c[0]) - float(wp[0]), float(c[1]) - float(wp[1])
        n = math.hypot(nx, ny)
        if n < 1e-6:
            a = math.radians(float(d.get("rotation_deg") or 0.0))
            nx, ny, n = -math.sin(a), math.cos(a), 1.0
        nx, ny = nx / n, ny / n
        ux, uy = -ny, nx
        half, depth = float(size[0]) / 2.0, WALL_HUNG_DEPTH_M
        x0, y0 = float(wp[0]), float(wp[1])
        poly = [(x0 + ux * half, y0 + uy * half), (x0 - ux * half, y0 - uy * half),
                (x0 - ux * half + nx * depth, y0 - uy * half + ny * depth),
                (x0 + ux * half + nx * depth, y0 + uy * half + ny * depth)]
        out.append((str(d.get("id")), str(d.get("type")), poly))
    return out


def overlap(a, b) -> float:
    from wenart.blender import door_spacing as DS
    return DS.overlap_area(a, b)


def _hits(poly, pieces) -> list[str]:
    return [pid for pid, _t, pp in pieces if overlap(poly, pp) > HIT_M2]


def _strip(cx: float, cy: float, u, n, half: float, depth: float, s: float, base: float) -> list:
    """The rectangle ``2 half`` along the wall by ``depth`` into side ``s`` from ``base`` off the centre line."""
    out = []
    for a, b in ((-half, base), (half, base), (half, base + depth), (-half, base + depth)):
        out.append((cx + u[0] * a + n[0] * s * b, cy + u[1] * a + n[1] * s * b))
    return out


def plan_sizes(building: dict, style) -> list[dict]:
    """The D5 size changes of the doors (module docstring): ``[{"id", "role", "width", "height", "drawn_width",
    "drawn_height", "reason"}]`` for the doors whose width or height changes, in building order (pure)."""
    if not active(style):
        return []
    fam = family_of(style)
    modern = fam in MODERN_FAMILIES
    walls, levels = _walls(building), _levels(building)
    entrance = main_entrance(building)
    openings = list(building.get("openings") or [])
    out = []
    for o in openings:
        if o.get("type") != "door" or not o.get("center") or o.get("virtual"):
            continue
        wall, level = walls.get(o.get("wall_id")), levels.get(o.get("level_id"))
        if wall is None or level is None:
            continue
        rooms = _rooms(building, level["id"])
        rs = sides(o, wall, rooms)
        role = door_role(building, o, wall, rs, entrance)
        if role == "outside":
            continue                                       # the facade's doors keep the drawn sizes
        w = float(o.get("width") or 0.0)
        if w <= 0:
            continue
        notes = []
        new_w = w
        pivot = modern and role == "entrance"
        if role == "entrance":
            sizes = PIVOT_WIDTHS_M if pivot else ENTRANCE_WIDTHS_M
            if w < sizes[0] - WIDTH_TOL_M:
                new_w = sizes[0]
                notes.append(f"an entrance at least an entrance door set wide ({new_w:.2f} m"
                             + (", a pivot door" if pivot else "") + f"; drawn {w:.2f} m)")
            elif w < WIDE_PRODUCT_M and not is_product(w, sizes):
                new_w = nearest_product(w, sizes)
                notes.append(f"the nearest entrance door set width {new_w:.2f} m (drawn {w:.2f} m: no product size)")
        elif w < WIDE_PRODUCT_M - 1e-9 and not is_product(w):
            new_w = nearest_product(w, PRODUCT_WIDTHS_M)
            notes.append(f"the nearest door set width {new_w:.2f} m (drawn {w:.2f} m: no product size)")
        if new_w > w + 1e-9:
            # the door widens about its drawn centre: each side grows by half
            before, after = width_room(o, wall, openings)
            room = 2.0 * min(before, after)
            if room + 1e-9 < new_w - w:
                fit = [s for s in (PIVOT_WIDTHS_M if pivot else ENTRANCE_WIDTHS_M if role == "entrance"
                                   else PRODUCT_WIDTHS_M) if w < s <= w + room + 1e-9]
                if role != "entrance" and not fit:
                    fit = [s for s in PRODUCT_WIDTHS_M if s <= w + room + 1e-9]
                new_w = max(fit) if fit else w
                notes.append(f"its wall leaves {room / 2.0:.2f} m on its tighter side: {new_w:.2f} m")
            if new_w > w + 1e-9 and _widened_blocked(building, o, wall, level["id"], new_w):
                notes.append(f"a piece stands in front of the wider door: {w:.2f} m kept")
                new_w = w
        height = o.get("height")
        h = float(height) if isinstance(height, (int, float)) and not isinstance(height, bool) else STANDARD_HEIGHT_M
        listed = set(o.get("assumed") or ()) if isinstance(o.get("assumed"), (list, tuple)) else set()
        new_h = h
        height_why = None
        if "height" in listed or height is None:
            target, what = STANDARD_HEIGHT_M, "a standard door"
            if role == "entrance":
                target, what = (PIVOT_HEIGHT_M, "a pivot entrance door") if pivot else (ENTRANCE_HEIGHT_M,
                                                                                        "a taller entrance door")
            elif role == "day" and modern:
                target, what = None, f"a full-height door to the ceiling between day rooms ({fam} style)"
            new_h, height_why = _door_height(building, o, wall, level, target, what)
        else:
            height_why = f"the documents give its height {h:.2f} m: kept"
        if abs(new_h - h) > HEIGHT_TOL_M and height_why:
            notes.append(height_why)
        if abs(new_w - w) <= 1e-6 and abs(new_h - h) <= HEIGHT_TOL_M:
            continue
        out.append({"id": o["id"], "role": role, "width": round(new_w, 4), "height": round(new_h, 4),
                    "drawn_width": round(w, 4), "drawn_height": round(h, 4), "pivot": pivot or None,
                    "reason": f"D5 door sizes by role and family ({role} door, {fam} style): " + "; ".join(notes)})
    return out


def _widened_blocked(building: dict, o: dict, wall: dict, level_id, new_w: float) -> bool:
    """A piece in the floor strip in front of the widened door that was not in front of it before."""
    cx, cy, _t = centre_on_wall(o, wall)
    _a, u, _l = _axis(wall)
    n = G.unit_normal_left(wall["start"], wall["end"])
    half_t = float(wall.get("thickness") or 0.2) / 2.0
    pieces = piece_polys(building, level_id)
    w = float(o.get("width") or 0.0)
    for s in (1.0, -1.0):
        new = _strip(cx, cy, u, n, new_w / 2.0, STRIP_M, s, half_t)
        old = _strip(cx, cy, u, n, w / 2.0, STRIP_M, s, half_t)
        if set(_hits(new, pieces)) - set(_hits(old, pieces)):
            return True
    return False


def _door_height(building: dict, o: dict, wall: dict, level: dict, target: Optional[float], what: str
                 ) -> tuple[float, str]:
    """``(height, why)`` of a door whose height the documents do not give: ``target`` (None: to the ceiling) where its
    level has no sloped ceiling and no opening of its wall stands over it; else the standard height."""
    from wenart.blender import shell as SH

    above = any(float(x.get("elevation") or 0.0) > float(level.get("elevation") or 0.0)
                for x in building.get("levels") or [])
    bottom, _top, _a = SH.opening_vertical(dict(o, height=STANDARD_HEIGHT_M), level, above)
    ceiling = float(level["elevation"]) + float(level["ceiling_height"])
    room = ceiling - bottom
    if level.get("ceiling_planes"):
        # 30 Oct 2026 (UL128, UL132; real04 run 20261029-201533: "a sloped ceiling over the level: 2.10 m kept" put
        # d_L1_001 / 002 back to 2.10 m under a 1.84 m slope, their frames and open leaves through the roof): under a
        # sloped ceiling a door runs to its head room at its wall, never over it (``head_room``)
        limit = head_room(o, wall, level)
        want = STANDARD_HEIGHT_M if target is None else float(target)
        if limit is not None and want > limit and limit >= MIN_CLEAR_M - 1e-9:
            return round(limit, 4), f"{what}: {limit:.2f} m, its head room under the sloped ceiling at its wall"
        if limit is not None and want > limit:
            # too low a head room for a usable door: ``apply_under_roof`` slides it along its wall or lowers it with
            # a finding (never a role height through the roof)
            return round(want, 4), f"{what}: {want:.2f} m; its head room at its wall is {limit:.2f} m (the roof rule)"
        return round(want, 4), f"{what} under the sloped ceiling: {want:.2f} m"
    want = room if target is None else min(float(target), room)
    _cx, _cy, t = centre_on_wall(o, wall)
    w = float(o.get("width") or 0.0)
    for x in building.get("openings") or []:
        if x is o or x.get("wall_id") != o.get("wall_id") or not x.get("center") or x.get("type") == "door":
            continue
        _x, _y, tx = centre_on_wall(x, wall)
        wx = float(x.get("width") or 0.0)
        if abs(tx - t) < (w + wx) / 2.0:
            xb, _xt, _xa = SH.opening_vertical(x, level, above)
            want = min(want, xb - bottom - OPENING_GAP_M)
    want = max(STANDARD_HEIGHT_M, want)
    return round(want, 4), f"{what}: {want:.2f} m high"


def apply_sizes(building: dict, style) -> tuple[list[dict], list[dict]]:
    """Carry out ``plan_sizes`` on ``building`` (in place): ``(changes, assumed entries)``."""
    changes = plan_sizes(building, style)
    by_id = {o.get("id"): o for o in building.get("openings") or []}
    assumed = []
    for c in changes:
        o = by_id[c["id"]]
        if abs(c["width"] - c["drawn_width"]) > 1e-6:
            o.setdefault("drawn_width", c["drawn_width"])
            o["width"] = c["width"]
        if abs(c["height"] - c["drawn_height"]) > HEIGHT_TOL_M:
            o.setdefault("drawn_height", c["drawn_height"] if o.get("height") is not None else None)
            o["height"] = c["height"]
        o["door_size"] = {k: c[k] for k in ("role", "width", "height", "drawn_width", "drawn_height", "pivot",
                                            "reason") if c.get(k) is not None}
        rec = {"by": "code", "rule": "D5 door sizes", "reason": c["reason"]}
        if isinstance(o.get("adjusted_by_ai"), dict):
            ev = o.setdefault("evidence", [])
            if isinstance(ev, list):
                ev.append({"file": "door_states", "method": "inferred", "confidence": 0.6, "rule": "D5 door sizes",
                           "text": c["reason"]})
        else:
            o["adjusted_by_ai"] = rec
        assumed.append({"object": c["id"], "field": "door_size", "value": {"width": c["width"], "height": c["height"]},
                        "reason": c["reason"], "parent": c["id"], "kind": "door_size"})
    return changes, assumed


# ---------------------------------------------------------------------------------- UL128 / UL132: under the roof

def head_room(o: dict, wall: dict, level: dict, t: Optional[float] = None) -> Optional[float]:
    """How tall a door's opening may be over its own bottom where it stands under a sloped ceiling (pure; 30 Oct 2026,
    lessons UL128, UL132): the lowest of the level's ``ceiling_planes`` over its frame (the opening and its architrave,
    ``FRAME_ALONG_M`` past each jamb, on both wall faces) less ``ROOF_HEAD_GAP_M`` (the architrave's head stands
    ``HEAD_RISE_M`` over the opening) and its sill; None on a level without a sloped ceiling. ``t``: the door's centre
    along its wall (default: where it stands). One height serves the opening, the leaf, the jamb lining, the head and
    the architrave: they are all built from the opening's height."""
    planes = level.get("ceiling_planes") if isinstance(level, dict) else None
    if not planes or not o.get("center"):
        return None
    from wenart.blender import geom2d

    a, u, _length = _axis(wall)
    n = G.unit_normal_left(wall["start"], wall["end"])
    if t is None:
        _cx, _cy, t = centre_on_wall(o, wall)
    cx, cy = a[0] + u[0] * t, a[1] + u[1] * t
    half = float(o.get("width") or 0.0) / 2.0 + FRAME_ALONG_M
    depth = float(wall.get("thickness") or 0.2) / 2.0
    pts = [(cx + u[0] * s * half + n[0] * k * depth, cy + u[1] * s * half + n[1] * k * depth)
           for s in (-1.0, 1.0) for k in (-1.0, 1.0)]
    low = min(geom2d.surface_z(planes, x, y) for x, y in pts)
    sill = float(o.get("sill_height") or 0.0)
    return round(low - float(level.get("elevation") or 0.0) - sill - ROOF_HEAD_GAP_M, 4)


def door_height_of(o: dict) -> float:
    """The door's built height (``shell.opening_vertical``'s default for none)."""
    h = o.get("height")
    return float(h) if isinstance(h, (int, float)) and not isinstance(h, bool) else STANDARD_HEIGHT_M


def _slide_spots(o: dict, wall: dict, openings: Sequence[dict]) -> list[float]:
    """The centres along its wall a door may slide to (pure; UL128): ``ROOF_SLIDE_STEP_M`` steps up to
    ``ROOF_SLIDE_MAX_M`` either way, nearest first, within ``width_room`` (the wall's ends and the other openings)."""
    _cx, _cy, t = centre_on_wall(o, wall)
    before, after = width_room(o, wall, openings)
    out = []
    k = 1
    while k * ROOF_SLIDE_STEP_M <= ROOF_SLIDE_MAX_M + 1e-9:
        d = k * ROOF_SLIDE_STEP_M
        if d <= after + 1e-9:
            out.append(t + d)
        if d <= before + 1e-9:
            out.append(t - d)
        k += 1
    return out


def plan_under_roof(building: dict) -> list[dict]:
    """Every door of a level under a sloped ceiling whose opening reaches over its head room (pure; UL128, UL132,
    user: "Some frames coming out of the roof it needs fixing", "Door frame needs fixing"): ``[{"id", "height", "was",
    "head_room", "center", "moved_m", "fits", "drawn", "reason"}]``. A door is lowered to its head room when that
    leaves ``MIN_CLEAR_M``; else it slides along its wall (``_slide_spots``: at most ``ROOF_SLIDE_MAX_M``, the same
    rooms on both sides) to the nearest spot that does; else it is lowered to its head room all the same (``fits``
    False: a finding, it needs a dormer or a raised roof). A drawn height over the wall at the door is a clear
    reading error (a door cannot be taller than its wall there): it is lowered too, ``drawn`` True."""
    walls, levels = _walls(building), _levels(building)
    openings = list(building.get("openings") or [])
    out = []
    for o in openings:
        if o.get("type") != "door" or not o.get("center") or o.get("virtual"):
            continue
        wall, level = walls.get(o.get("wall_id")), levels.get(o.get("level_id"))
        if wall is None or level is None:
            continue
        room = head_room(o, wall, level)
        h = door_height_of(o)
        if room is None or h <= room + HEIGHT_TOL_M:
            continue
        listed = set(o.get("assumed") or ()) if isinstance(o.get("assumed"), (list, tuple)) else set()
        drawn = o.get("height") is not None and "height" not in listed
        rec = {"id": o["id"], "was": round(h, 4), "head_room": room, "center": None, "moved_m": 0.0, "drawn": drawn}
        if room >= MIN_CLEAR_M - 1e-9:
            rec.update(height=round(room, 4), fits=True,
                       reason=f"its {h:.2f} m would reach over the sloped ceiling at its wall: lowered to its head "
                              f"room {room:.2f} m (UL128)")
        else:
            rooms = _rooms(building, level["id"])
            ids = [r.get("id") if r else None for r in sides(o, wall, rooms)]
            a, u, _l = _axis(wall)
            spot = None
            half = max(0.0, float(o.get("width") or 0.0) / 2.0 - FRAME_W_M)
            for t in _slide_spots(o, wall, openings):
                there = dict(o, center=[a[0] + u[0] * t, a[1] + u[1] * t])
                r2 = head_room(there, wall, level)
                if r2 is None or r2 < MIN_CLEAR_M - 1e-9:
                    continue
                # the same two rooms at its centre and at both jambs (no slide past a wall meeting this one)
                probes = [dict(o, center=[a[0] + u[0] * x, a[1] + u[1] * x]) for x in (t - half, t, t + half)]
                if all([r.get("id") if r else None for r in sides(p, wall, rooms)] == ids for p in probes):
                    spot = (t, r2, there["center"])
                    break
            if spot is not None:
                _cx, _cy, t0 = centre_on_wall(o, wall)
                new_h = min(h, spot[1])
                rec.update(height=round(new_h, 4), fits=True, head_room=spot[1],
                           center=[round(spot[2][0], 4), round(spot[2][1], 4)], moved_m=round(spot[0] - t0, 4),
                           reason=f"its head room at its wall is only {room:.2f} m (under {MIN_CLEAR_M:.2f} m): slid "
                                  f"{spot[0] - t0:+.2f} m along its wall to where the sloped ceiling leaves "
                                  f"{spot[1]:.2f} m, {new_h:.2f} m high (UL128)")
            else:
                rec.update(height=round(max(room, 0.05), 4), fits=False,
                           reason=f"its head room under the sloped ceiling is only {room:.2f} m (under "
                                  f"{MIN_CLEAR_M:.2f} m) and no spot within {ROOF_SLIDE_MAX_M:.1f} m along its wall "
                                  f"leaves more: lowered to {max(room, 0.05):.2f} m so nothing crosses the roof; it "
                                  f"needs a dormer or a raised roof (review)")
        out.append(rec)
    return out


def apply_under_roof(building: dict) -> tuple[list[dict], list[dict], list[str]]:
    """Carry out ``plan_under_roof`` on ``building`` (in place): ``(changes, assumed entries, warnings)``. Every
    change keeps ``drawn_height`` (and ``drawn_center`` for a slid door), is recorded in ``under_roof`` and as
    ``adjusted_by_ai`` (by code), and in ``assumed``; a door that does not fit is a warning (its finding)."""
    changes = plan_under_roof(building)
    by_id = {o.get("id"): o for o in building.get("openings") or []}
    assumed, warnings = [], []
    for c in changes:
        o = by_id[c["id"]]
        o.setdefault("drawn_height", o.get("height"))
        o["height"] = c["height"]
        listed = list(o.get("assumed") or []) if isinstance(o.get("assumed"), (list, tuple)) else []
        if "height" not in listed and not c["drawn"]:
            o["assumed"] = listed + ["height"]
        if c["center"] is not None:
            o.setdefault("drawn_center", list(o["center"]))
            o["center"] = list(c["center"])
        o["under_roof"] = {k: c[k] for k in ("height", "was", "head_room", "moved_m", "fits", "drawn", "reason")}
        if isinstance(o.get("adjusted_by_ai"), dict):          # as D5 does: the first record stays, the rule is evidence
            ev = o.setdefault("evidence", [])
            if isinstance(ev, list):
                ev.append({"file": "door_states", "method": "inferred", "confidence": 0.8,
                           "rule": "UL128 doors under the roof", "text": c["reason"]})
        else:
            o["adjusted_by_ai"] = {"by": "code", "rule": "UL128 doors under the roof", "reason": c["reason"]}
        if isinstance(o.get("door_size"), dict):
            o["door_size"] = dict(o["door_size"], height=c["height"], reason=f"{o['door_size'].get('reason')}; "
                                                                             f"{c['reason']}")
        assumed.append({"object": c["id"], "field": "under_roof", "value": {"height": c["height"],
                                                                           "moved_m": c["moved_m"]},
                        "reason": c["reason"], "parent": c["id"], "kind": "door_under_roof"})
        if not c["fits"]:
            warnings.append(f"{c['id']}: {c['reason']}")
    return changes, assumed, warnings


def leaf_head(o: dict, level: Optional[dict]) -> Optional[dict]:
    """``{"planes", "top"}`` for a door on a level under a sloped ceiling (its leaf's top in world z: the floor + the
    sill + the opening's height), None elsewhere (pure; UL128: an open leaf reaches into the room, where the slope
    may be lower than over its wall)."""
    planes = (level or {}).get("ceiling_planes")
    if not planes:
        return None
    top = float(level.get("elevation") or 0.0) + float(o.get("sill_height") or 0.0) + door_height_of(o)
    return {"planes": planes, "top": top}


def leaf_under_ceiling(poly, head: Optional[dict]) -> Optional[float]:
    """How far a leaf's outline (plan) reaches over the sloped ceiling over it (pure; positive: it crosses, by that
    much plus ``LEAF_HEAD_GAP_M``), None when it stays under it or on a flat level."""
    if not head or not poly:
        return None
    from wenart.blender import geom2d

    low = min(geom2d.surface_z(head["planes"], float(p[0]), float(p[1])) for p in poly)
    over = float(head["top"]) + LEAF_HEAD_GAP_M - low
    return round(over, 4) if over > 1e-6 else None


# -------------------------------------------------------------------------------------------------------- D1 states

def leaf_frame(o: dict, wall: dict, level: Optional[dict] = None) -> dict:
    """The door's frame in plan: centre, wall axis ``u``, left normal ``n``, wall thickness, the leaf's clear width
    ``lw`` and thickness ``t`` (the parametric door's sizes); ``head`` (30 Oct 2026, UL128: ``leaf_head``) on a level
    under a sloped ceiling, so an open leaf is tried under the ceiling over it."""
    cx, cy, _t = centre_on_wall(o, wall)
    _a, u, _l = _axis(wall)
    n = G.unit_normal_left(wall["start"], wall["end"])
    w = float(o.get("width") or 0.0)
    return {"c": (cx, cy), "u": u, "n": n, "T": float(wall.get("thickness") or 0.2), "w": w,
            "lw": max(0.1, w - 2 * FRAME_W_M - LEAF_CLEAR_M), "t": LEAF_T_M, "head": leaf_head(o, level)}


def _to_world(fr: dict, x: float, y: float) -> tuple[float, float]:
    (cx, cy), u, n = fr["c"], fr["u"], fr["n"]
    return (round(cx + u[0] * x + n[0] * y, 5), round(cy + u[1] * x + n[1] * y, 5))


def swing_leaf(fr: dict, side: int, hinge: str, angle_deg: float, lw: Optional[float] = None,
               hx: Optional[float] = None) -> dict:
    """The open leaf of a swing door in plan (pure): ``{"poly": its outline, "sweep": the floor it sweeps from closed
    to ``angle_deg``, "pivot", "free_end"}``. The leaf (``lw`` long, ``t`` thick) turns about its hinge edge on the
    face of the room it opens into (``side``: +1 the wall's left), ``hinge`` the jamb at the wall's ``start`` or
    ``end`` (= ``parametric.pose_door_parts``)."""
    lw = fr["lw"] if lw is None else lw
    t, s = fr["t"], (1.0 if side > 0 else -1.0)
    k = -1.0 if hinge == "start" else 1.0
    hx = k * fr["lw"] / 2.0 if hx is None else hx
    py = s * t / 2.0
    ang = math.radians(angle_deg)
    # the leaf's direction from its hinge when closed: along -k x; open: turned towards +s y
    d0 = (-k, 0.0)
    d1 = (-k * math.cos(ang), s * math.sin(ang))
    # the leaf's body lies behind its swing face (towards -s when closed): that side turned with the leaf
    nrm = (-d1[1], d1[0]) if k == s else (d1[1], -d1[0])
    corners = [(hx, py), (hx + d1[0] * lw, py + d1[1] * lw), (hx + d1[0] * lw + nrm[0] * t, py + d1[1] * lw + nrm[1] * t),
               (hx + nrm[0] * t, py + nrm[1] * t)]
    fan = [(hx, py)]
    for i in range(SWEEP_STEPS + 1):
        a = ang * i / SWEEP_STEPS
        d = (-k * math.cos(a), s * math.sin(a))
        fan.append((hx + d[0] * lw, py + d[1] * lw))
    return {"poly": [_to_world(fr, x, y) for x, y in corners], "sweep": [_to_world(fr, x, y) for x, y in fan],
            "pivot": _to_world(fr, hx, py), "free_end": _to_world(fr, hx + d1[0] * lw, py + d1[1] * lw),
            "closed_dir": d0}


def slide_leaf(fr: dict, side: int, direction: int, surface: bool) -> dict:
    """The slid-open leaf of a sliding door in plan (pure): on the face of ``side`` (``surface``: hung on the wall
    face, else a pocket leaf inside the wall), moved ``direction`` (+1: towards the wall's end) by the opening's
    width."""
    s = 1.0 if side > 0 else -1.0
    w, t = fr["w"], fr["t"]
    if surface:
        sw = w + 2 * SLIDE_OVERLAP_M
        y0 = s * (fr["T"] / 2.0 + SLIDE_STANDOFF_M)
        x0 = direction * w - sw / 2.0
        corners = [(x0, y0), (x0 + sw, y0), (x0 + sw, y0 + s * t), (x0, y0 + s * t)]
    else:
        x0 = direction * (fr["lw"] - 0.05) - fr["lw"] / 2.0
        corners = [(x0, -t / 2.0), (x0 + fr["lw"], -t / 2.0), (x0 + fr["lw"], t / 2.0), (x0, t / 2.0)]
    return {"poly": [_to_world(fr, x, y) for x, y in corners], "slide_m": round(direction * (w if surface else
                                                                                           fr["lw"] - 0.05), 4)}


def _ray_exit(p, d, polygon) -> float:
    """How far a ray from ``p`` along ``d`` runs before it leaves ``polygon`` (its nearest edge crossing)."""
    best = float("inf")
    n = len(polygon)
    for i in range(n):
        a, b = polygon[i], polygon[(i + 1) % n]
        ex, ey = b[0] - a[0], b[1] - a[1]
        den = d[0] * ey - d[1] * ex
        if abs(den) < 1e-12:
            continue
        rx, ry = a[0] - p[0], a[1] - p[1]
        t = (rx * ey - ry * ex) / den
        s = (rx * d[1] - ry * d[0]) / den
        if t > 1e-6 and -1e-9 <= s <= 1.0 + 1e-9:
            best = min(best, t)
    return best


def _corner_distance(fr: dict, side: int, hinge: str, room: dict) -> float:
    """How far the hinge jamb stands from the room's wall beside it (along the door's wall, on the room's face)."""
    k = -1.0 if hinge == "start" else 1.0
    s = 1.0 if side > 0 else -1.0
    p = _to_world(fr, k * fr["w"] / 2.0, s * (fr["T"] / 2.0 + 0.02))
    return _ray_exit(p, (fr["u"][0] * k, fr["u"][1] * k), room["polygon"])


def _inside(poly_pts, room: dict, fr: dict, side: int) -> bool:
    """The parts of an open leaf beyond the wall face lie in the room it opens into."""
    s = 1.0 if side > 0 else -1.0
    face = fr["T"] / 2.0 + 0.01
    (cx, cy), n = fr["c"], fr["n"]
    for x, y in poly_pts:
        off = (x - cx) * n[0] * s + (y - cy) * n[1] * s
        if off > face and not G.point_in_polygon((x, y), room["polygon"]):
            return False
    return True


def hinge_end(o: dict, side: int) -> tuple[Optional[str], bool]:
    """``(start | end, drawn)`` of the drawn ``hinge_side`` (left / right seen from the room the door opens into,
    ``side`` its side of the wall), ``(None, False)`` without one. Seen from the left side (+1) of a wall the viewer's
    right hand is the wall's start."""
    hs = str(o.get("hinge_side") or "").strip().lower()
    if hs not in ("left", "right"):
        return None, False
    end = (hs == "left") == (side > 0)
    return ("end" if end else "start"), True


def hinge_side_of(hinge: str, side: int) -> str:
    """The inverse of ``hinge_end``: the hinge side seen from the room the door opens into."""
    return "left" if (hinge == "end") == (side > 0) else "right"


def operation_of(o: dict) -> str:
    """The door's operation as the build makes it: the architect's door kind first (``door_style``), else the drawn
    ``operation``."""
    style = str(o.get("door_style") or "")
    if style in ("glazed_sliding",):
        return "glazed_sliding"
    if style in ("sliding", "barn"):
        return "sliding"
    if style == "pocket":
        return "pocket"
    if style in ("double",) or str(o.get("door_type") or "") in ("double", "french"):
        return "double"
    if style in ("folding", "sectional"):
        return style
    op = str(o.get("operation") or "swing").lower()
    if op == "unknown":
        op = "swing"
    if op == "double" or (op == "swing" and isinstance(o.get("leaves"), int) and o.get("leaves") == 2):
        return "double"
    return op


def _swing_try(fr, side, hinge, angle, room, pieces, others, lw=None, hx=None):
    """``(leaf, why)`` of one swing leaf at ``angle``; ``why`` None when nothing stops it."""
    leaf = swing_leaf(fr, side, hinge, angle, lw=lw, hx=hx)
    if room is not None and not _inside(leaf["poly"] + leaf["sweep"][1:], room, fr, side):
        return leaf, "its leaf would run into the wall of the room it opens into"
    over = leaf_under_ceiling(leaf["poly"], fr.get("head"))
    if over is not None:                  # 30 Oct 2026 (UL128): the slope over the open leaf is lower than its top
        return leaf, f"its open leaf would reach {over:.2f} m into the sloped ceiling over it"
    hit = sorted(set(_hits(leaf["poly"], pieces)) | set(_hits(leaf["sweep"], pieces)))
    if hit:
        return leaf, f"its {'swing' if not set(_hits(leaf['poly'], pieces)) else 'open leaf'} would hit " \
                     f"{', '.join(hit[:3])}"
    for oid, poly in others:
        if overlap(leaf["poly"], poly) > HIT_M2 or overlap(leaf["sweep"], poly) > HIT_M2:
            return leaf, f"its leaf would meet the leaf or the doorway of {oid}"
    return leaf, None


def camera_hinge(fr: dict, side: int, cam) -> str:
    """The hinge jamb whose open leaf stays out of a camera's view of the doorway (pure; UL126): a camera in the room
    the door opens into sees past a leaf at the jamb across from it, a camera on the other side past a leaf at the
    jamb on its own side (the doorway's rays run away from it)."""
    (cx, cy), u, n = fr["c"], fr["u"], fr["n"]
    dx, dy = float(cam[0]) - cx, float(cam[1]) - cy
    x_cam = dx * u[0] + dy * u[1]
    in_swing = (dx * n[0] + dy * n[1]) * (1.0 if side > 0 else -1.0) > 0
    if in_swing:
        return "end" if x_cam < 0 else "start"
    return "start" if x_cam < 0 else "end"


def _segment_hits(p, q, poly) -> bool:
    """The segment ``p`` -> ``q`` crosses the convex polygon ``poly`` (an edge crossing, or ``q`` inside it)."""
    if G.point_in_polygon(q, poly):
        return True
    d = (q[0] - p[0], q[1] - p[1])
    length = math.hypot(*d)
    if length < 1e-9:
        return False
    t = _ray_exit(p, (d[0] / length, d[1] / length), poly)
    return t < length - 1e-6


def leaf_hides(cam, leaf_poly, fr: dict) -> bool:
    """The open leaf ``leaf_poly`` stands between a camera and at least two of three points across the doorway (pure;
    UL126: the leaf must not hide the opening from the view that shows it)."""
    pts = [_to_world(fr, k * fr["w"] * 0.3, 0.0) for k in (-1.0, 0.0, 1.0)]
    cam2 = (float(cam[0]), float(cam[1]))
    return sum(1 for q in pts if _segment_hits(cam2, q, leaf_poly)) >= 2


def doors_seen(cameras: Sequence[dict], building: dict) -> dict:
    """``{door id: camera}``: the doors a camera looks through (pure): its centre line (position to target,
    ``SIGHT_M`` long) crosses the door's opening on its wall."""
    walls = _walls(building)
    out: dict = {}
    for cam in cameras or []:
        pos = cam.get("position")
        tgt = cam.get("target")
        if not pos or not tgt:
            continue
        dx, dy = float(tgt[0]) - float(pos[0]), float(tgt[1]) - float(pos[1])
        n = math.hypot(dx, dy)
        if n < 1e-9:
            continue
        d = (dx / n, dy / n)
        for o in building.get("openings") or []:
            wall = walls.get(o.get("wall_id"))
            if o.get("type") != "door" or wall is None or not o.get("center") or (
                    cam.get("level_id") and o.get("level_id") != cam.get("level_id")):
                continue
            fr = leaf_frame(o, wall)
            a = _to_world(fr, -fr["w"] / 2.0, 0.0)
            b = _to_world(fr, fr["w"] / 2.0, 0.0)
            t = _ray_exit((float(pos[0]), float(pos[1])), d, [a, b])
            if t <= SIGHT_M:
                out.setdefault(o["id"], cam)
    return out


def worth_showing(building: dict, from_room: Optional[dict], beyond: Optional[dict]) -> Optional[str]:
    """Why the room ``beyond`` a door is worth showing from ``from_room`` (pure; UL126: "You can leave the right door
    open and show the dressing room"): a dressing room or walk-in (``wardrobe_fronts.walk_in``: see-through now), an
    en-suite (a wet room whose every door opens into ``from_room``, a bedroom), a hall or a living space; None for a
    private room (a WC or a bathroom seen from anywhere else, a storage room) or no room."""
    from wenart.blender import wardrobe_fronts as WF

    if beyond is None or from_room is None:
        return None
    t, f = _rtype(beyond), _rtype(from_room)
    if WF.walk_in(building, beyond):
        return "the dressing room beyond"
    if t in WET_TYPES:
        if f != "bedroom":
            return None
        doors = [o for o in building.get("openings") or [] if o.get("type") in ("door", "opening")
                 and o.get("level_id") == beyond.get("level_id") and beyond.get("id") in (
                     (o.get("leaf_state") or {}).get("rooms") or [])]
        if doors and all(from_room.get("id") in ((o.get("leaf_state") or {}).get("rooms") or []) for o in doors):
            return "the en-suite beyond"
        return None
    if t in ("hall", "living", "dining", "kitchen"):
        return f"the {t} beyond"
    return None


def plan_states(building: dict, style, cameras: Sequence[dict] = ()) -> dict:
    """``{door id: leaf_state}`` of every door (module docstring; pure). The doors are decided in building order; a
    leaf already open is an obstacle of the next door's leaf."""
    if not active(style):
        return {}
    walls, levels = _walls(building), _levels(building)
    entrance = main_entrance(building)
    seen = doors_seen(cameras, building)
    brief_open = doors_open_brief(building)
    out: dict = {}
    taken: dict = {}                                     # level id -> [(door id, open leaf outline)]
    pieces_of: dict = {}
    for o in building.get("openings") or []:
        if o.get("type") != "door" or not o.get("center") or o.get("virtual"):
            continue
        wall, level = walls.get(o.get("wall_id")), levels.get(o.get("level_id"))
        if wall is None or level is None:
            continue
        lid = level["id"]
        rooms = _rooms(building, lid)
        rs = sides(o, wall, rooms)
        role = door_role(building, o, wall, rs, entrance)
        side, into, side_assumed = swing_side(o, wall, rooms)
        room = next((r for r in rooms if r.get("id") == into), None)
        op = operation_of(o)
        fr = leaf_frame(o, wall, level)
        rec = {"state": "closed", "operation": op, "role": role, "side": side, "into": into,
               "rooms": [r.get("id") if r else None for r in rs], "angle_deg": 0.0, "slide_m": None, "hinge": None,
               "hinge_side": None, "hinge_assumed": None, "leaf_polys": [], "by": "rule", "assumed": True}
        if lid not in pieces_of:
            pieces_of[lid] = piece_polys(building, lid)
        pieces = pieces_of[lid]
        others = list(taken.get(lid) or [])
        # the doorways of the other doors of the level: a leaf never swings into another doorway
        for x in building.get("openings") or []:
            wx = walls.get(x.get("wall_id"))
            if x is o or x.get("level_id") != lid or wx is None or x.get("type") not in ("door", "opening") \
                    or not x.get("center"):
                continue
            fx = leaf_frame(x, wx)
            others.append((x["id"], [_to_world(fx, a * fx["w"] / 2.0, b * fx["T"] / 2.0)
                                     for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]))
        asked = str(o.get("open_state") or "").strip().lower()
        cam = seen.get(o["id"])
        camera = (cam.get("name") or "camera") if cam else None
        want, why = _wanted(role, op, asked, camera, o, brief_open)
        rec["by"] = "documents" if asked in STATES else ("brief" if not brief_open and want == "closed" and
                                                         role not in ("entrance", "outside") else
                                                         "camera" if camera and want == "open" else "rule")
        if camera and want == "open":
            rec["camera"] = camera
        if want == "closed":
            rec["reason"] = why
            out[o["id"]] = rec
            continue
        prefer = camera_hinge(fr, side, cam["position"]) if cam and cam.get("position") else None
        _decide(rec, o, fr, side, room, op, want, why, pieces, others, prefer)
        if rec["state"] == "closed" and side_assumed and "sloped ceiling" in str(rec.get("blocked") or ""):
            # 30 Oct 2026 (UL128): the slope over its own side is too low for the open leaf and no swing side is
            # drawn: it swings into the room on the other side when its leaf is free there
            other = next((r for r in rs if r is not None and r.get("id") != into), None)
            if other is not None:
                trial = dict(rec)
                _decide(trial, o, fr, -side, other, op, want, why, pieces, others, prefer)
                if trial["state"] != "closed":
                    trial.update(side=-side, into=other.get("id"), swing_turned=True,
                                 reason=trial["reason"] + f"; its swing turned into {other.get('id')}: the slope over "
                                                          f"{into} is too low for its open leaf (UL128)")
                    rec, side_assumed = trial, False
        if rec["state"] != "closed" and rec.get("leaf_polys"):
            taken.setdefault(lid, []).extend((o["id"], p) for p in rec["leaf_polys"])
        if side_assumed and rec["state"] != "closed":
            rec["reason"] += "; the side it opens to is assumed (no swing side drawn)"
        out[o["id"]] = rec
    return out


def _decide(rec: dict, o: dict, fr: dict, side: int, room: Optional[dict], op: str, want: str, why: str, pieces,
            others, prefer: Optional[str] = None) -> dict:
    """Open (or set ajar) a door's leaf in ``rec`` where its leaf, its swing or its slid leaf hit nothing (pure, in
    place): a swing leaf hinged at the drawn ``hinge_side``, else at ``prefer`` (a camera's ``camera_hinge``), else at
    the jamb nearer the room's wall beside it; both leaves of a pair; a sliding leaf along its wall face either way, a
    pocket leaf into its pocket, a glazed sliding door's moving panels. Else closed with the reason."""
    angle = AJAR_DEG if want == "ajar" else OPEN_DEG
    rec.update(state="closed", angle_deg=0.0, slide_m=None, leaf_polys=[], sweeps=[])
    if op in ("swing", "double"):
        drawn, is_drawn = hinge_end(o, side)
        leaves = []
        steps = [angle] + [a for a in AJAR_STEPS if a < angle - 1e-9]
        first_stop = None
        if op == "double":
            half = fr["lw"] / 2.0 - 0.002
            got = []
            for hinge, hx in (("start", -fr["lw"] / 2.0), ("end", fr["lw"] / 2.0)):
                found = None
                for a in steps:
                    leaf, stop = _swing_try(fr, side, hinge, a, room, pieces, others, lw=half, hx=hx)
                    if stop is None:
                        found = (a, leaf)
                        break
                    first_stop = first_stop or stop
                got.append(found)
            stop = first_stop if any(g is None for g in got) else None
            best = min(a for a, _l in got) if stop is None else None
            leaves = [lf for _a, lf in got] if stop is None else []
            if stop is None and best < angle - 1e-9:
                # both leaves of a pair open alike: the narrower free angle for both
                leaves = [_swing_try(fr, side, h, best, room, pieces, others, lw=half, hx=hx)[0]
                          for h, hx in (("start", -fr["lw"] / 2.0), ("end", fr["lw"] / 2.0))]
        else:
            if is_drawn:
                order = [drawn]
            else:
                order = sorted(("start", "end"), key=lambda h: (_corner_distance(fr, side, h, room) if room else 0.0,
                                                                h != "start"))
                if prefer in ("start", "end"):
                    order = [prefer] + [h for h in order if h != prefer]
            choice = None                                   # (angle, hinge, leaf): the widest free angle
            for h in order:
                for a in steps:
                    leaf, stop = _swing_try(fr, side, h, a, room, pieces, others)
                    if stop is None:
                        if choice is None or a > choice[0] + 1e-9:
                            choice = (a, h, leaf)
                        break
                    first_stop = first_stop or stop
                if choice is not None and choice[0] >= angle - 1e-9:
                    break
            stop = None if choice is not None else first_stop
            best = choice[0] if choice is not None else None
            hinge = choice[1] if choice is not None else order[0]
            leaves = [choice[2]] if choice is not None else []
            rec.update(hinge=hinge, hinge_side=hinge_side_of(hinge, side) if hinge else None,
                       hinge_assumed=not is_drawn)
        if stop is not None:
            rec.update(reason=f"{why}; closed: {stop}", blocked=stop)
            return rec
        rec.pop("blocked", None)
        where = ""
        if rec.get("hinge_assumed"):
            where = (f"; hinged so the open leaf stays out of the view ({rec['hinge_side']} seen from "
                     f"{rec.get('into')})" if prefer and rec.get("hinge") == prefer else
                     f"; hinged at the jamb by the wall beside it ({rec['hinge_side']} seen from {rec.get('into')})")
        state = want
        if best < angle - 1e-9:
            # 29 Oct 2026 (UL127): a piece or a wall stops the leaf: it stands ajar at its widest free angle
            state = "ajar"
            where += f"; ajar at {best:.0f} deg, the widest its leaf and swing are free ({first_stop})"
            rec["stopped_by"] = first_stop
        rec.update(state=state, angle_deg=best, leaf_polys=[lf["poly"] for lf in leaves],
                   sweeps=[lf["sweep"] for lf in leaves], reason=why + where)
    elif op in SLIDE_OPERATIONS:
        surface = op == "sliding"
        stop = None
        for direction in (1, -1) if surface else (1,):
            leaf = slide_leaf(fr, side, direction, surface)
            hit = _hits(leaf["poly"], pieces) if surface else []
            meet = [oid for oid, poly in others if overlap(leaf["poly"], poly) > HIT_M2] if surface else []
            room_ok = room is None or not surface or all(
                G.point_in_polygon(p, room["polygon"]) for p in leaf["poly"][2:])
            over = leaf_under_ceiling(leaf["poly"], fr.get("head"))     # 30 Oct 2026 (UL128)
            stop = (f"its slid leaf would hit {', '.join(hit[:3])}" if hit else
                    f"its slid leaf would cover {meet[0]}" if meet else
                    f"its slid leaf would reach {over:.2f} m into the sloped ceiling over it" if over is not None else
                    None if room_ok else "the wall beside it is too short for its slid leaf")
            if stop is None:
                rec.update(state="open", slide_m=leaf["slide_m"], leaf_polys=[leaf["poly"]],
                           reason=why + ("; slid along its wall face" if surface else "; slid into its pocket"))
                break
        if stop is not None:
            rec.update(reason=f"{why}; closed: {stop}", blocked=stop)
    elif op == "glazed_sliding":
        rec.update(state="open", slide_m=None, reason=why + "; its moving panels slid behind the fixed ones")
    else:
        rec["reason"] = f"a {op} door is shown closed"
    return rec


def _level_obstacles(building: dict, o: dict, lid, walls: dict) -> tuple[list, list]:
    """``(pieces, others)`` a door's leaf must not hit: the level's pieces (``piece_polys``) and the other doors'
    open leaves and doorways."""
    pieces = piece_polys(building, lid)
    others = []
    for x in building.get("openings") or []:
        wx = walls.get(x.get("wall_id"))
        if x is o or x.get("level_id") != lid or wx is None or x.get("type") not in ("door", "opening") \
                or not x.get("center"):
            continue
        fx = leaf_frame(x, wx)
        others.append((x["id"], [_to_world(fx, a * fx["w"] / 2.0, b * fx["T"] / 2.0)
                                 for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1))]))
        for poly in (x.get("leaf_state") or {}).get("leaf_polys") or []:
            others.append((x["id"], [tuple(p) for p in poly]))
    return pieces, others


OPENABLE = ("swing", "double", "sliding", "pocket", "glazed_sliding")


def seen_doors(plan: dict, building: dict) -> list[str]:
    """The doors a camera plan sees: its ``visible_openings`` that are doors, else the doors its centre line
    crosses (``doors_seen``)."""
    ids = {o.get("id") for o in building.get("openings") or [] if o.get("type") == "door"}
    vis = [v for v in plan.get("visible_openings") or [] if v in ids]
    return vis or list(doors_seen([plan], building))


def revise_for_cameras(building: dict, style, plans: Sequence[dict], level_id=None) -> list[dict]:
    """The doors as the views show them (pure, in place; 29 Oct 2026, lesson UL126, user on real06's master bedroom:
    "You can leave the right door open and show the dressing room, not all the doors should be closed"): a door an
    interior camera of the level sees (``seen_doors``) that leads to a room worth showing (``worth_showing``: a
    dressing room or walk-in, an en-suite, a hall or a living space) opens when the rules kept it closed or ajar (not
    the documents' ``open_state``, never the entrance or an outside door), its hinge chosen so its leaf stays out of
    that camera's view (``camera_hinge``), and an open leaf that hides the doorway from a camera turns to its other
    jamb; the leaf, its swing and the level's pieces and other leaves pass the same checks (``_decide``). A private
    door (a WC, a bathroom seen from a living space) keeps its state. Returns the ``assumed`` entries, each naming
    the camera and the reason."""
    if not active(style):
        return []
    walls, levels = _walls(building), _levels(building)
    rooms_by = {r.get("id"): r for r in building.get("rooms") or []}
    doors = {o.get("id"): o for o in building.get("openings") or [] if o.get("type") == "door"}
    out = []
    for plan in plans or []:
        pos, rid = plan.get("position"), plan.get("room_id")
        if not pos or (level_id is not None and plan.get("level_id") not in (None, level_id)):
            continue
        for oid in seen_doors(plan, building):
            o = doors.get(oid)
            ls = o.get("leaf_state") if o is not None and isinstance(o.get("leaf_state"), dict) else None
            wall = walls.get((o or {}).get("wall_id"))
            if ls is None or wall is None or o.get("level_id") not in levels or ls.get("by") in ("documents", "brief") \
                    or ls.get("role") in ("entrance", "outside") or ls.get("operation") not in OPENABLE:
                continue
            beyond = next((rooms_by.get(x) for x in ls.get("rooms") or [] if x and x != rid), None)
            worth = worth_showing(building, rooms_by.get(rid), beyond)
            fr = leaf_frame(o, wall, levels.get(o.get("level_id")))
            side = int(ls.get("side") or -1)
            room = rooms_by.get(ls.get("into"))
            prefer = camera_hinge(fr, side, pos)
            if ls.get("state") == "open":
                hides = [p for p in ls.get("leaf_polys") or [] if leaf_hides(pos, p, fr)]
                if not hides or ls.get("operation") != "swing" or not ls.get("hinge_assumed") \
                        or ls.get("hinge") == prefer:
                    continue
                trial = dict(ls)
                pieces, others = _level_obstacles(building, o, o["level_id"], walls)
                _decide(trial, dict(o, hinge_side=hinge_side_of(prefer, side)), fr, side, room, "swing", "open",
                        ls.get("reason") or "an inside door stands open", pieces, others)
                if trial["state"] == "open":
                    trial.update(hinge_assumed=True, camera=plan.get("name"), by="camera",
                                 reason=trial["reason"] + f"; turned to its other jamb: {plan.get('name')} sees the "
                                                          "doorway past it")
                    o["leaf_state"] = trial
                    out.append(_camera_assumed(oid, trial, plan))
                continue
            if worth is None:
                continue
            trial = dict(ls)
            pieces, others = _level_obstacles(building, o, o["level_id"], walls)
            why = f"{plan.get('name')} sees it and {worth} is worth showing (UL126)"
            _decide(trial, o, fr, side, room, ls["operation"], "open", why, pieces, others, prefer)
            if trial["state"] == "open":
                trial.update(by="camera", camera=plan.get("name"))
                o["leaf_state"] = trial
                out.append(_camera_assumed(oid, trial, plan))
            else:
                o["leaf_state"] = dict(ls, reason=str(ls.get("reason") or "") + f"; {why}, but " +
                                       trial["reason"].split("closed: ")[-1])
    return out


def _camera_assumed(oid: str, rec: dict, plan: dict) -> dict:
    return {"object": oid, "field": "leaf_state", "value": {k: rec.get(k) for k in ("state", "angle_deg", "hinge_side")},
            "reason": rec.get("reason") or "", "camera": plan.get("name"), "parent": oid, "kind": "door_state"}


def doors_open_brief(building: dict) -> bool:
    """The brief's ``doors_open`` (the project's stored brief; True when it names none)."""
    v = ((building.get("project") or {}).get("brief") or {}).get("doors_open", True)
    return not (v is False or str(v).strip().lower() in ("false", "off", "no", "closed", "0"))


def _wanted(role: str, op: str, asked: str, camera: Optional[str], o: dict, doors_open: bool = True
            ) -> tuple[str, str]:
    """``(open | ajar | closed, why)`` before the geometry is checked. 29 Oct 2026 (UL127, user: "Leaving all the
    doors open in default could be a good approach"): every interior door stands open by default, whatever room it
    leads to; the entrance and the outside (terrace) doors stay closed (an open front door reads as a mistake), so do
    garage, sectional, folding and fixed doors; the documents, an answer (the architect's D9, ``open_state``) or the
    brief (``doors_open: false``) close or set any door ajar."""
    if asked in STATES:
        return asked, f"the documents or an answer fix it {asked} (open_state)"
    if role == "entrance":
        return "closed", "the entrance door stays closed (an open front door reads as a mistake)"
    if role == "outside":
        return "closed", "an outside or terrace door stays closed (an open one reads as a mistake)"
    if op in ("folding", "sectional", "fixed"):
        return "closed", f"a {op} door is shown closed"
    if not doors_open:
        return "closed", "the brief closes the doors (doors_open: false)"
    what = {"dressing": "into the dressing room", "wet": "a bathroom or WC door", "storage": "a storage room's door",
            "day": "between day rooms"}.get(role, "an inside door")
    return "open", (f"every interior door stands open by default (UL127; {what})"
                    + (f"; {camera} looks through it" if camera else ""))


def apply_states(building: dict, style, cameras: Sequence[dict] = ()) -> tuple[dict, list[dict]]:
    """Write ``plan_states`` into the doors (``leaf_state``, in place): ``(states, assumed entries)``."""
    states = plan_states(building, style, cameras)
    by_id = {o.get("id"): o for o in building.get("openings") or []}
    assumed = []
    for oid, rec in states.items():
        by_id[oid]["leaf_state"] = rec
        if rec.get("swing_turned") and rec.get("into"):
            # 30 Oct 2026 (UL128): the build hangs the leaf on this side (``shell.opening_room_side``: swing_side)
            by_id[oid]["swing_side"] = rec["into"]
            assumed.append({"object": oid, "field": "swing_side", "value": rec["into"], "reason": rec.get("reason"),
                            "parent": oid, "kind": "door_swing_under_roof"})
        assumed.append({"object": oid, "field": "leaf_state",
                        "value": {k: rec.get(k) for k in ("state", "angle_deg", "slide_m", "hinge_side")},
                        "reason": rec.get("reason") or "", "parent": oid, "kind": "door_state"})
    return states, assumed


def state_of(o: dict) -> str:
    return str((o.get("leaf_state") or {}).get("state") or "closed")


def is_open(o: dict) -> bool:
    """A door whose leaf is open (a doorway a view sees through)."""
    return o.get("type") == "door" and state_of(o) == "open"


# ---------------------------------------------------------------------------------------------- M29 / U33 checks

def state_problems(building: dict, manifest: Optional[dict] = None, style=None) -> list[dict]:
    """The door checks of a house as built (module docstring): ``[{"target", "kind", "severity", "message"}]``."""
    if style is None and isinstance(manifest, dict):
        prof = manifest.get("style_profile") if isinstance(manifest.get("style_profile"), dict) else {}
        style = {"family": prof.get("family") or (manifest.get("style") if isinstance(manifest.get("style"), dict)
                                                  else {}).get("family")}
    out: list[dict] = []
    doors = [o for o in building.get("openings") or [] if o.get("type") == "door" and o.get("center")]
    if not doors:
        return dressing_problems(building, style if (style or {}).get("family") else None)
    walls = _walls(building)
    entrance = main_entrance(building)
    recorded = [o for o in doors if isinstance(o.get("leaf_state"), dict)]
    inside = []
    for o in doors:
        wall = walls.get(o.get("wall_id"))
        if wall is None:
            continue
        role = (o.get("leaf_state") or {}).get("role") or door_role(building, o, wall, sides(
            o, wall, _rooms(building, o.get("level_id"))), entrance)
        if role in ("day", "inside", "dressing"):
            inside.append(o)
    could = [o for o in inside if operation_of(o) in OPENABLE
             and (o.get("leaf_state") or {}).get("by") not in ("documents", "brief")
             and not (o.get("leaf_state") or {}).get("blocked")]
    if len(could) >= 2 and not any(state_of(o) in ("open", "ajar") for o in could):
        why = "; ".join(f"{o['id']}: {(o.get('leaf_state') or {}).get('reason') or 'no leaf state recorded'}"
                        for o in could[:4])
        out.append({"target": "doors", "kind": "all_closed", "severity": "major",
                    "message": f"every inside door of the house is closed ({len(could)} could open): {why[:400]} - "
                               "an inside door stands open by default (UL116)"})
    sized = [(round(float(o.get("width") or 0.0), 2), round(float(o.get("height") or STANDARD_HEIGHT_M), 2))
             for o in doors]
    if len(doors) >= 3 and len(set(sized)) == 1:
        out.append({"target": "doors", "kind": "one_size", "severity": "major",
                    "message": f"all {len(doors)} doors are one size ({sized[0][0]:.2f} x {sized[0][1]:.2f} m): door "
                               "sizes vary by role and family (UL117)"})
    ent = next((o for o in doors if o.get("id") == entrance), None)
    if ent is not None and inside:
        ew, eh = float(ent.get("width") or 0.0), float(ent.get("height") or STANDARD_HEIGHT_M)
        iw = max(float(o.get("width") or 0.0) for o in inside)
        ih = max(float(o.get("height") or STANDARD_HEIGHT_M) for o in inside)
        if ew <= iw + 1e-6 and eh <= ih + 1e-6 and recorded:
            out.append({"target": ent["id"], "kind": "one_size", "severity": "minor",
                        "message": f"the entrance {ent['id']} ({ew:.2f} x {eh:.2f} m) is no wider and no taller than "
                                   f"the inside doors ({iw:.2f} x {ih:.2f} m): a taller, wider entrance (UL117)"})
    for o in recorded:
        st = o["leaf_state"]
        if st.get("state") == "closed" or not st.get("leaf_polys"):
            continue
        pieces = piece_polys(building, o.get("level_id"))
        hit = sorted({pid for poly in st["leaf_polys"] for pid in _hits(poly, pieces)})
        if hit:
            out.append({"target": o["id"], "kind": "leaf_in_piece", "severity": "major",
                        "message": f"the open leaf of {o['id']} stands in {', '.join(hit[:4])}: the leaf closes or "
                                   "the piece moves (UL116)"})
    out += dressing_problems(building, style if (style or {}).get("family") else None)
    out += view_problems(building, (manifest or {}).get("cameras") or [])
    return out


def view_problems(building: dict, cameras: Sequence[dict]) -> list[dict]:
    """A view that shows only closed doors although one of them leads to a room worth showing (UL126; pure): one
    ``view_closed_doors`` finding per camera, naming the door, the room beyond and why the door stayed closed."""
    rooms_by = {r.get("id"): r for r in building.get("rooms") or []}
    by_id = {o.get("id"): o for o in building.get("openings") or [] if o.get("type") == "door"}
    walls = _walls(building)
    entrance = main_entrance(building)
    out = []
    for cam in cameras or []:
        if cam.get("kind") not in (None, "interior") or not cam.get("room_id"):
            continue
        seen = [by_id[i] for i in seen_doors(cam, building) if i in by_id]
        if not seen or any(is_open(o) for o in seen):
            continue
        for o in seen:
            wall = walls.get(o.get("wall_id"))
            if wall is None:
                continue
            ls = o.get("leaf_state") if isinstance(o.get("leaf_state"), dict) else {}
            rs = sides(o, wall, _rooms(building, o.get("level_id")))
            role = ls.get("role") or door_role(building, o, wall, rs, entrance)
            if role in ("entrance", "outside") or ls.get("by") in ("documents", "brief") or operation_of(o) not in OPENABLE:
                continue
            beyond = next((r for r in rs if r is not None and r.get("id") != cam.get("room_id")), None)
            worth = worth_showing(building, rooms_by.get(cam.get("room_id")), beyond)
            if worth:
                out.append({"target": o["id"], "kind": "view_closed_doors", "severity": "major",
                            "camera": cam.get("name"),
                            "message": f"{cam.get('name')} shows only closed doors, though {o['id']} leads to {worth} "
                                       f"({(beyond or {}).get('id')}): it stands open, its leaf out of the view "
                                       f"(UL126; {ls.get('reason') or 'no leaf state recorded'})"})
                break
    return out


def dressing_problems(building: dict, style=None) -> list[dict]:
    """A walk-in dressing room (``wardrobe_fronts.walk_in``: a dressing room, or wardrobe runs facing each other
    across an aisle) whose wardrobes all have closed fronts (UL120, UL125; ``wardrobe_fronts.is_see_through``): a
    design finding, the reference solution missed, with the architect's D8 answer that fixes it (``fix_choice``)."""
    from wenart.blender import wardrobe_fronts as WF

    out = []
    for room in building.get("rooms") or []:
        robes = [f for f in building.get("furniture") or [] if f.get("room_id") == room.get("id")
                 and str(f.get("type")) in WF.WARDROBE_TYPES and f.get("build", True) is not False]
        if not robes or any(WF.is_see_through(f) for f in robes):
            continue
        why = WF.walk_in(building, room)
        if why is None:
            continue
        ans = room.get("wardrobe_fronts") if isinstance(room.get("wardrobe_fronts"), dict) else {}
        if ans.get("kind") == "closed" and ans.get("by") not in (None, "architect"):
            continue                                     # the user's or the AI's answer: closed fronts on purpose
        # 31 Oct 2026 (user on real04 run 20261030-181158-full: "it needs to be wall to wall or from wall to middle"):
        # a walk-in none of whose runs can stand against a wall keeps its free-standing wardrobes (no fix exists)
        if not any(WF.built_in_fit(building, f, room)["ok"] for f in robes):
            continue
        kind = WF.WALK_IN_FRONTS.get(WF.family_of(style), WF.WALK_IN_DEFAULT) if style else "slats"
        out.append({"target": room["id"], "kind": "dressing_closed_fronts", "severity": "major",
                    "fix_choice": f"wardrobe_fronts:{kind}",
                    "message": f"the walk-in {room['id']} ({why}) has closed wardrobe fronts only "
                               f"({', '.join(str(f.get('id')) for f in robes[:4])}): a walk-in is see-through on "
                               f"every side, {WF.FRONT_WHAT[kind]} with real contents and a light inside "
                               "(UL120, UL125)"})
    return out


def frame_problems(manifest: Optional[dict]) -> list[dict]:
    """Doors without a frame (UL122): a door's ``frame`` record (``shell`` / ``opening_build``) with no lining and no
    recorded frameless reason (``no_frame``, major; a door with no record at all is one), an indoor face without its
    architrave and no reason (``no_architrave``, minor)."""
    objects = (manifest or {}).get("objects") if isinstance(manifest, dict) else manifest
    rows: dict = {}
    for ob in objects or []:
        if not isinstance(ob, dict) or ob.get("kind") != "door" or ob.get("parent"):
            continue
        oid = str(ob.get("element_id") or ob.get("wenart_id") or ob.get("name"))
        row = rows.setdefault(oid, {"frame": None})
        if isinstance(ob.get("frame"), dict):
            row["frame"] = ob["frame"]
    out = []
    for oid, row in rows.items():
        fr = row["frame"]
        if fr is None:
            out.append({"target": oid, "kind": "no_frame", "severity": "major",
                        "message": f"door {oid} has no frame record: it may stand in a raw hole in the wall (UL122)"})
            continue
        if fr.get("frameless"):
            continue
        if not fr.get("lining"):
            out.append({"target": oid, "kind": "no_frame", "severity": "major",
                        "message": f"door {oid} has no frame (no jamb lining, no head) and no frameless reason: every "
                                   "door gets a frame by default (UL122)"})
            continue
        missing = sorted(set(fr.get("indoor_faces") or []) - set(fr.get("architrave") or []))
        if missing and not fr.get("architrave_why"):
            out.append({"target": oid, "kind": "no_architrave", "severity": "minor",
                        "message": f"door {oid} has no architrave on its indoor face(s) {missing}: an architrave "
                                   "covers the joint of the frame and the plaster (UL122)"})
        out += census_problems(oid, fr.get("census"))
    return out


FRAME_TOP_TOL_M = 0.01            # a frame part may stand HEAD_RISE_M (+ this) over its opening's head, no more


def census_problems(oid: str, census: Optional[dict]) -> list[dict]:
    """30 Oct 2026 (lesson UL132, user on real04's d_L1_001: "Door frame needs fixing"; ``parametric.frame_census``):
    the opening, the leaf, the jamb lining, the head and the architrave share one height, and the frame is complete:
    a frame part reaching over its opening's head by more than the architrave's ``HEAD_RISE_M`` (``frame_taller``,
    major), a lining or an architrave face with jambs and no head (``jamb_without_head``, major), or with one jamb only
    (``one_jamb``, major). Pure; [] without a census (a frame built before the rule)."""
    if not isinstance(census, dict):
        return []
    out = []
    h, top = census.get("height_m"), census.get("top_m")
    if isinstance(h, (int, float)) and isinstance(top, (int, float)) and top > h + HEAD_RISE_M + FRAME_TOP_TOL_M:
        out.append({"target": oid, "kind": "frame_taller", "severity": "major",
                    "message": f"door {oid}'s frame reaches {top:.2f} m over its bottom, over its {h:.2f} m opening: "
                               "the opening, the leaf and the frame share one height (UL132)"})
    slots = [("its jamb lining", census.get("lining") or {})] + \
        [(f"its architrave on face {k}", v) for k, v in sorted((census.get("faces") or {}).items())]
    for what, slot in slots:
        jambs, heads = int(slot.get("jambs") or 0), int(slot.get("heads") or 0)
        if jambs and not heads:
            out.append({"target": oid, "kind": "jamb_without_head", "severity": "major",
                        "message": f"door {oid}: {what} has {jambs} jamb(s) and no head (UL132: both jambs and the "
                                   "head on each indoor face)"})
        elif jambs == 1:
            out.append({"target": oid, "kind": "one_jamb", "severity": "major",
                        "message": f"door {oid}: {what} has one jamb only (UL132: both jambs and the head)"})
    return out
