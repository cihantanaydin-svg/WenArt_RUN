"""Rule-based decor: cushions on sofas and beds, books on shelves and desks, one
potted plant per living room or bedroom (docs/milestone4.md section 4).

Only when ``brief.decor`` is not false (default true, ``wenart/defaults.yaml``),
and never in a prayer room (``NO_DECOR_ROOM_TYPES``, docs/milestone7.md §0:
a pooja room gets no decor, not even on a drawn piece; the report says so).
Pieces with ``build: false`` (drawn symbols that are not built) never host
decor but stay obstacles for the plant.
Decor is ``added_by_ai`` with ``method: "rule"``, never larger than 0.6 m, and
never on a walkway: a plant goes into a free room corner that passes the
placer checks (inside the room, no overlap with furniture, not on a door
approach or swing, and the 0.9 m walkways of the room stay intact; a corner
within 0.3 m of a window is skipped because the plant is taller than the
sill). Cushions and books sit on their host piece (``host_id``), expressed in
building coordinates so the Blender build can drop them on the host's top.

Output on the building: a top-level list ``decor`` of
``{"id", "kind": "decor", "type": "cushion"|"book_set"|"plant", "level_id",
"room_id", "center": [x, y], "rotation_deg", "size": [w, d], "asset": null,
"host_id": <furniture id or null>, "source": "added_by_ai", "method": "rule",
"reason"}`` plus a short markdown report.

CLI: ``python -m wenart.furniture.decor outputs/<p>/building_furnished.json
--out outputs/<p>/building_decor.json`` (``decor_report.md`` next to it).

Milestone 8 (docs/milestone8.md §4), two more decor types, same brief switch
and prayer-room rule, only around verified, built pieces of a verified room:

- ``rug`` (``rugs``): under the sofa + coffee table group of a living room
  (the widest sofa with a coffee table in front of it within
  ``COFFEE_TABLE_REACH_M``), under the lower (foot) two thirds of every double
  bed of a bedroom, under every dining table grown by ``DINING_CHAIR_M``
  (0.6 m) on each side for the chairs. Rug = that group box (in the frame of
  the sofa / bed / table) grown by ``RUG_MARGIN_M`` (0.3 m) on every side,
  then cut down side by side (``fit_rug``) until it lies inside the room
  shrunk by ``RUG_ROOM_INSET_M`` (0.3 m) and touches no door swing (the
  placer's swing geometry), no fixed or tall piece (``RUG_BLOCKER_TYPES``)
  and no earlier rug, keeping the key piece's centre (coffee table, bed,
  dining table) on it; smaller than ``RUG_MIN_SIDE_M`` on a side -> no rug.
  A rug lies on the floor, ``host_id`` None (its own decor element and pass
  index in the scene), ``anchor_ids`` = the group.
- ``wall_art`` (``wall_art_for_room``): one per living room, bedroom or
  dining room, centred above the first of a sofa, a double bed, a single bed
  (its headboard) or a dresser whose back stands within ``WALL_MAX_GAP_M``
  of a room wall parallel to it; width <= ``WALL_ART_WIDTH_SHARE`` (0.6) x
  the piece width (at most ``WALL_ART_MAX_W``), narrowed (centred) to keep
  ``OPENING_MARGIN_M`` off every door, window or opening of that wall and
  inside the wall segment, refused below ``WALL_ART_MIN_W``; bottom edge
  ``WALL_ART_GAP_M`` (0.25 m) above the piece top (``bottom_m`` from
  ``parametric.piece_bbox``; the scene builder re-hangs it over the built
  top), ``max_height_m`` up to ``WALL_ART_CEILING_M`` under the ceiling.
  Fields: ``wall_point`` (the art's centre on the wall face), ``wall_id``
  (the nearest wall of the building, when there is one), ``gap_m``,
  ``bottom_m``, ``max_height_m``; ``center`` = ``wall_point`` + half the
  nominal depth into the room, ``rotation_deg`` turns local -Y into the room.
  Wall art is built only from a library decor model (``fit.fit_decor_item``).
- Rugs and wall art may be larger than ``MAX_DECOR_M`` (``LARGE_DECOR_TYPES``).

28 Oct 2026 (user: "More decor pieces needed ... kettle in the kitchen, microwave in the kitchen etc"; real06's kitchen:
nothing on the counter): ``kitchen_worktop_decor`` dresses every kitchen's worktop modestly by rule (in the rules and
in the AI decorator's rooms): a microwave, a coffee machine or a toaster, a kettle, a utensil pot, a chopping board, a
fruit bowl (``KITCHEN_DECOR_TYPES``, real sizes, parametric until audited library models exist), each where it belongs
and passing ``worktop_item_ok`` (on the worktop, off the hob and its side gap, off the sink and tall units, never in
front of a window or a pass-through it would reach), hosted on the counter, ``added_by_ai`` by rule with the reason.

Milestone 10 (docs/milestone10.md §4.6, §1.6b rows 18, 20; track F):

- The 12 new decor types are in ``DECOR_TYPES`` (the AI decorator places them, ``decor_ai``); curtains, blinds,
  throws, large plants, floor sculptures and pendants may pass the 0.6 m cap.
- Host tables of the new furniture types: a corner sofa takes cushions along its back like a sofa
  (``host_decor``), wall art above it, and its rug lies in the inner corner (in front of the main seat beside the
  chaise, with the coffee table); tall, wall, shoe and display cabinets and sideboards are rug blockers.
- Partners (``partner_rooms``, ``copy_partner_decor``): a room with ``same_as`` (an alternative level's room equal
  to a base room) and, with ``render.twin_rooms: one`` (the default), the second twin of a mirrored pair
  (``twin_of``) are not decorated themselves: the partner's decor is copied onto them (mirrored for twins, through
  ``wenart.furniture.complete.partner_transform``) with ``mirrored_from``; host pieces, rug and wall-art anchors and
  curtain windows are mapped to the room's own (an item whose piece or window has no counterpart is dropped and
  listed). A partner that cannot be verified leaves the room to be decorated itself (listed).
- Partner chains (pod F1, real02: r_L-1b_banyo_2 is ``same_as`` r_L-1_banyo_2, the twin of r_L-1_banyo): a room
  whose partner takes a copy itself copies after it, from that copy (``_copy_order``); a loop of partners has no
  room to copy from, so its first room in building order is decorated itself (listed, ``copy_targets``).

Milestone 11 (docs/milestone11.md §1.1 E2): under the sloped attic ceiling (``ceiling_planes``: the roof as the build
makes it) a corner whose ceiling is lower than the plant (+ 10 cm) gets no plant (``ceiling_over``); the AI
decorator's floor corners and tabletop heights use the same ceiling. A drawn rug outline (``infer.py``) is no rug
blocker.

Milestone 12 (docs/milestone12.md §4.7 D13, contract §13.2; track S): every decor item carries a ``host_frame``
(``support`` seat | mattress | back | headboard | top | shelf | floor | wall | ceiling, ``u`` / ``v`` as shares of
its host's footprint, ``turn_deg``, ``lean_deg``, ``shelf``; an anchored rug, picture or pendant: ``anchor_id``) next
to its world ``center`` (``attach_host_frames``, called by ``add_decor`` and the AI decorator); ``sync_to_hosts``
recomputes the world position from the host after any edit (move, turn, resize, swap) and drops decor whose host is
gone, not built or retyped (``decor_dropped``, fixes B3). Heights are not stored: the scene builder finds the real
support on the built mesh (``wenart.blender.rest``). Cushions are real-size standing cushions (``CUSHION_SIZE``,
``PILLOW_SIZE``: width, thickness, height) and none go on a seat or bed whose model already has its own
(``takes_cushions``); untyped pieces and library gaps host nothing (``piece_is_built``).

Milestone 13 (docs/milestone13.md §3.0 K3, groups.yaml R6; track T3 -> the decor stage): the group solver lays the
rug as a member of the seating and sleeping groups (``solver.apply_candidate`` writes it to ``building["decor"]``
with ``group.role == "rug"``; ``layout.apply_choice`` and the agent's ``edit_ops`` carry it). ``add_decor`` keeps
those rugs (``solver_rugs``) instead of resetting the decor: the rule rugs are laid only under groups the solver
left without one, off the kept rugs (``rugs_for_room``), the new ids count on after the kept ones
(``decor_counters``), a partner copy never doubles a room's own solver rug, and the report row counts the kept
rugs. With ``brief.decor`` false the solver's rugs are left out too (listed): no decor means no rug.

Fix round after P4a (17 Oct 2026; the furniture track's ask, applied at integration): a vector-drawn piece the
reading typed by code (``type_method`` in ``infer.CODE_TYPE_METHODS``; it stays ``unverified`` until two passes agree)
hosts decor like a verified one (``trusted_host``: ``program.unsure_anchor`` is False for it), as the completion
completes it. P4a's r_L0_yatak_odasi kept only a curtain (2 decor slots against 10 in M11) because its code-typed bed
hosted nothing. A piece the reading could not agree on still hosts nothing.

Fix round after P5 (22 Oct 2026; pod P5, real04): ``MIN_LIGHT_BOTTOM_M`` (2.0 m, Milestone 11 pod G2b) is the one
rule for every decor light that hangs from a sloped ceiling: the AI decorator offers no flush ceiling light under the
slope whose bottom would be lower (``decor_ai.ceiling_items``; its pendants already keep their bottom at
``decor_ai.PENDANT_MIN_BOTTOM_M``, a dining pendant 0.75 m over the table), and the builder does not build one
(``build.decor_under_roof``, now also for a light already placed flush under the slope). P5 hung ``dec_L1_011`` flush
under the 1.27 m slope of the L1 bathroom, 1.155 m above the floor and 1.5 cm under the lens of ``cam_r_L1_banyo_1``
(56 % of the frame). The Blender side (``build.py``) keeps a copy of the constant (this module imports shapely, which
Blender's Python does not have); tests/test_m13_p5_fixround.py pins them equal. The light rig's own ceiling fixtures
keep a lower bound, the camera height plus headroom (``lighting.RIG_CEILING_MIN_BOTTOM_M``, 1.55 m; why there).

Fix round after P6a (22 Oct 2026; pod P6a, real04): window decor under the roof. ``roof_clips`` gives the windows and
doors of the level under the roof as the build makes them (``roof.clip_openings_to_roof`` on ``roof.roof_model``, as
``build.prepare``: a window whose height is not drawn stops ``roof.OPENING_ROOF_GAP`` under the roof underside at its
wall); the AI decorator hangs curtains and blinds at that window and under the sloped ceiling over their own
footprint (``decor_ai.window_items``). A partner room's copy of a curtain or blind is not copied where the ceiling
over the copy is lower than its top plus ``WINDOW_DECOR_CEILING_CLEAR_M`` (``copy_partner_decor``, a note; a
mirrored roof gives the twin the same heights). Why: P6a hung the curtains dec_L1_005 / dec_L1_014 of the L1 oyun
rooms 2.25 m high at windows drawn 1.2 m tall; the build clipped those windows to 0.81 m (top 1.71 m) and the slope
over the curtains is 1.83 m, so both poked 0.4 m through the mansard roof in four exterior views (critical X2 in
every agent round; no agent tool edits decor).
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import re
import sys
from pathlib import Path
from typing import Optional

from shapely import affinity
from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from wenart import building as B
from wenart import geometry as G
from wenart.furniture import placer

DECOR_TYPES: tuple[str, ...] = ("cushion", "book_set", "plant", "rug", "wall_art",
                                 # Milestone 9 (docs/milestone9.md §3): tabletop decor and the wall mirror; the AI
                                 # decorator (wenart/furniture/decor_ai.py) places them, the rules never do.
                                 "vase", "bowl", "plant_small", "table_lamp", "mirror",
                                 # Milestone 10 (docs/milestone10.md §4.6): the AI decorator's slots place them.
                                 "curtain", "blind", "throw", "books", "candle", "basket", "tray", "clock",
                                 "sculpture", "plant_large", "pendant_light", "ceiling_light",
                                 # 28 Oct 2026: the kitchen worktop's small appliances and decor (kitchen_worktop_decor)
                                 "microwave", "kettle", "coffee_machine", "toaster", "chopping_board", "utensil_pot",
                                 "fruit_bowl")
# Not held to MAX_DECOR_M (Milestone 8, 9; Milestone 10: window dressings, throws, large plants and floor
# sculptures, pendants on their cord).
LARGE_DECOR_TYPES: tuple[str, ...] = ("rug", "wall_art", "mirror", "curtain", "blind", "throw", "plant_large",
                                      "sculpture", "pendant_light")
MAX_DECOR_M = 0.6
# Milestone 12 (§4.7, B7): real sizes (width, thickness, height): a 45 cm square cushion standing against a sofa
# back, a 50 cm one leaning at a bed's head (in front of the sleeping pillows); never stretched by a model fit.
CUSHION_SIZE = (0.45, 0.15, 0.45)  # standing against a sofa back
PILLOW_SIZE = (0.5, 0.15, 0.5)     # leaning at the head of a bed
BOOK_SIZE = (0.3, 0.22)
PLANT_SIZE = (0.4, 0.4)
PLANT_HEIGHT_M = 1.0
PLANT_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom")
NO_DECOR_ROOM_TYPES: tuple[str, ...] = ("prayer", "stair", "shaft")   # Milestone 7: no decor at all in these rooms
# 25 Oct 2026 (user: "there are not enough decor around"): a room the reading left unverified (an inferred scale or
# label; real06's living room and kitchen, 14 of real04's 38 rooms) is furnished, so it is dressed too; only these
# statuses take decor
DECOR_ROOM_STATUSES: tuple[str, ...] = ("verified", "unverified")


def room_takes_decor(room: dict) -> bool:
    """A room decor may dress (pure): a status of ``DECOR_ROOM_STATUSES`` and not a ``NO_DECOR_ROOM_TYPES`` room."""
    return room.get("status") in DECOR_ROOM_STATUSES and room.get("room_type") not in NO_DECOR_ROOM_TYPES
CORNER_INSET_M = 0.25             # plant centre from each wall of the corner
HOST_TYPES: dict[str, str] = {    # host type -> decor type
    "sofa": "cushion", "bed_double": "cushion", "bed_single": "cushion",
    "bookshelf": "book_set", "desk": "book_set",
    "sofa_corner": "cushion",     # Milestone 10: cushions along the L's back, as a sofa
}
CORNER_SOFA_CUSHION_PITCH_M = 0.6  # Milestone 10: one cushion per this much of a corner sofa's back
# Milestone 8 rugs (docs/milestone8.md §4).
RUG_MARGIN_M = 0.3                # the group box grows by this on every side
RUG_ROOM_INSET_M = 0.3            # ... and is clipped to the room shrunk by this
DINING_CHAIR_M = 0.6              # a dining table's group: the table plus this on every side (the chairs)
BED_RUG_SHARE = 2.0 / 3.0         # a double bed's group: the lower (foot) two thirds of the bed
COFFEE_TABLE_REACH_M = 1.5        # a coffee table in front of a sofa within this belongs to its group
SEATING_RUG_DEPTH_M = 1.4         # 27 Oct 2026: a sofa without a coffee table: the rug reaches this far in front ...
SEATING_RUG_UNDER_M = 0.25        # ... and this far under the sofa (its front legs on it)
SINGLE_BED_RUG_OUT_M = 0.6        # a single bed's rug reaches this far out on its sides (the wall side is cut)
RUG_MIN_SIDE_M = 0.8              # a rug cut smaller than this on a side is left out
RUG_GRID_M = 0.02                 # the cutting grid of fit_rug
LIVING_RUG_ROOM_TYPES: tuple[str, ...] = ("living",)
BED_RUG_ROOM_TYPES: tuple[str, ...] = ("bedroom",)
# Pieces a rug never runs under (fixed equipment, tall storage, bathroom and kitchen pieces, unknown symbols).
RUG_BLOCKER_TYPES: tuple[str, ...] = (
    "stair", "kitchen_counter", "kitchen_island", "fridge", "stove", "sink_kitchen", "washing_machine", "wardrobe",
    "bookshelf", "bathtub", "shower", "toilet", "washbasin", "unknown",
    # Milestone 10: storage standing on the floor (and wall cabinets, over the counter run anyway)
    "tall_cabinet", "wall_cabinet", "shoe_cabinet", "display_cabinet", "sideboard")
LIVING_RUG_SOFAS: tuple[str, ...] = ("sofa", "sofa_corner")      # Milestone 10: a corner sofa groups like a sofa
# Milestone 8 wall art.
WALL_ART_ROOM_TYPES: tuple[str, ...] = ("living", "bedroom", "dining")
WALL_ART_HOST_TYPES: tuple[str, ...] = ("sofa", "sofa_corner", "bed_double", "bed_single", "dresser")   # in order
WALL_ART_GAP_M = 0.25             # bottom edge above the piece top
WALL_ART_WIDTH_SHARE = 0.6        # width <= this x the piece width
WALL_ART_MAX_W = 1.5
WALL_ART_MIN_W = 0.4
WALL_ART_DEPTH_M = 0.04           # nominal depth (the library model's own depth is used when built)
WALL_ART_NOMINAL_ASPECT = 0.75    # nominal height / width for the ceiling check
WALL_ART_CEILING_M = 0.10         # top at least this far below the ceiling
WALL_ART_MIN_H = 0.25             # less room than this under the ceiling: no wall art
WALL_MAX_GAP_M = 0.3              # the piece's back edge within this of the wall
WALL_PARALLEL_DEG = 10.0
WALL_END_MARGIN_M = 0.05          # art this far inside the wall segment's ends
OPENING_MARGIN_M = 0.1            # and this far off every door, window or opening of its wall


def decor_allowed(building: dict) -> bool:
    brief = (building.get("project") or {}).get("brief") or {}
    return brief.get("decor", True) is not False


def _local_to_building(host: dict, local_x: float, local_y: float) -> list[float]:
    fp = host["footprint"]
    p = G.rotate_point((fp["center"][0] + local_x, fp["center"][1] + local_y), fp["rotation_deg"], tuple(fp["center"]))
    return [round(p[0], 3), round(p[1], 3)]


def host_decor(host: dict) -> list[dict]:
    """Cushions / books for one furniture piece, in building coordinates (without ids)."""
    w, d = host["footprint"]["size"]
    rot = host["footprint"]["rotation_deg"]
    kind = HOST_TYPES.get(host["type"])
    items = []
    if kind == "cushion" and host["type"] == "sofa_corner":
        n = max(2, int(w / CORNER_SOFA_CUSHION_PITCH_M))
        for i in range(n):
            x = -w / 2.0 + w * (i + 0.5) / n
            centre = _local_to_building(host, x, d / 2.0 - CUSHION_SIZE[1] / 2.0 - 0.1)
            items.append({"type": "cushion", "center": centre, "rotation_deg": rot, "size": list(CUSHION_SIZE),
                          "reason": "cushion against the corner sofa's back"})
    elif kind == "cushion" and host["type"] == "sofa":
        for x in (-w / 4.0, w / 4.0):
            items.append({"type": "cushion", "center": _local_to_building(host, x, d / 2.0 - CUSHION_SIZE[1] / 2.0 - 0.1),
                          "rotation_deg": rot, "size": list(CUSHION_SIZE), "reason": "cushion against the sofa back"})
    elif kind == "cushion":
        xs = (-w / 4.0, w / 4.0) if host["type"] == "bed_double" else (0.0,)
        for x in xs:
            items.append({"type": "cushion", "center": _local_to_building(host, x, d / 2.0 - PILLOW_SIZE[1] / 2.0 - 0.1),
                          "rotation_deg": rot, "size": list(PILLOW_SIZE), "reason": "cushion at the head of the bed"})
    elif kind == "book_set" and host["type"] == "bookshelf":
        items.append({"type": "book_set", "center": _local_to_building(host, 0.0, 0.0), "rotation_deg": rot,
                      "size": list(BOOK_SIZE), "reason": "books on the shelf"})
    elif kind == "book_set":
        items.append({"type": "book_set", "center": _local_to_building(host, w / 2.0 - BOOK_SIZE[0] / 2.0 - 0.05,
                                                                         d / 2.0 - BOOK_SIZE[1] / 2.0 - 0.05),
                      "rotation_deg": rot, "size": list(BOOK_SIZE), "reason": "books on the back corner of the desk"})
    return items


def _corner_candidates(ctx: placer.RoomContext, inset: float = CORNER_INSET_M) -> list[tuple[float, float]]:
    """Plant centres inset (``inset`` from each wall; Milestone 10: a larger item insets more) from every convex
    corner of the room, in boundary order."""
    segs = ctx.segments
    out = []
    for i in range(len(segs)):
        a, b = segs[i - 1]          # previous segment ends at the corner
        _b2, c = segs[i]            # next segment starts at the corner
        corner = b
        u_prev = placer._unit((a[0] - corner[0], a[1] - corner[1]))
        u_next = placer._unit((c[0] - corner[0], c[1] - corner[1]))
        cross = u_prev[0] * u_next[1] - u_prev[1] * u_next[0]
        if cross >= -1e-9:          # reflex or straight corner (CCW ring): not a corner to stand in
            continue
        out.append((round(corner[0] + (u_prev[0] + u_next[0]) * inset, 3),
                    round(corner[1] + (u_prev[1] + u_next[1]) * inset, 3)))
    return out


CEILING_CLEAR_M = 0.10           # Milestone 11 (E2): a floor item's top stays this far under the (sloped) ceiling
MIN_LIGHT_BOTTOM_M = 2.0         # M11, fix round after P5: a decor light's bottom under a slope, at least this
WINDOW_DECOR_TYPES = ("curtain", "blind")
WINDOW_DECOR_CEILING_CLEAR_M = 0.02   # fix round after P6a: a curtain rod / blind roller this far under a slope
COPY_HEIGHT_TOL_M = 0.005        # ... a twin's copy may reach this much higher (rounding of the mirrored centre)


def ceiling_planes(building: dict, level_id: str) -> list:
    """Milestone 11 (docs/milestone11.md §1.1 E2): the sloped ceiling of the level under the roof, as the build makes
    it (``wenart.blender.build.prepare``: ``roof.roof_model`` + ``roof.ceiling_planes``, pure Python, no Blender), or
    [] when the level has a flat ceiling (no roof, a non-convex roof, another level)."""
    roof = building.get("roof")
    if not isinstance(roof, dict):
        return []
    from wenart.blender import roof as R

    try:
        model = R.roof_model(roof, building)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return []
    if not model or not model.get("convex") or not model.get("equations") or model.get("over_level_id") != level_id:
        return []
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), None)
    if level is None or level.get("ceiling_height") is None:
        return []
    return [list(p) for p in R.ceiling_planes(model, level)]


def roof_clips(building: dict, level_id: str) -> dict[str, dict]:
    """Fix round after P6a (module docstring): ``{opening id: clip}`` of the doors and windows of ``level_id`` that
    the build clips under the roof (``roof.clip_openings_to_roof`` on ``roof.roof_model``, as ``build.prepare``;
    ``clip`` = ``{"height", "sill_height", "was", "underside_z", "reason", "fits"}``), {} for another level or no
    roof."""
    roof = building.get("roof")
    if not isinstance(roof, dict):
        return {}
    from wenart.blender import roof as R

    try:
        model = R.roof_model(roof, building)
        if not model or model.get("over_level_id") != level_id:
            return {}
        level = next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), None)
        if level is None:
            return {}
        return {c["opening_id"]: c for c in R.clip_openings_to_roof(building, level, model)}
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return {}


def ceiling_over(building: dict, level_id: str, center, size, rotation_deg: float = 0.0,
                 planes: Optional[list] = None) -> float:
    """The ceiling height above the floor over a footprint: the level's ``ceiling_height``; under the roof the lowest
    ceiling plane over its corners and centre (as ``wenart.blender.furniture.ceiling_above``)."""
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == level_id), {})
    flat = float(level.get("ceiling_height") or 2.7)
    planes = ceiling_planes(building, level_id) if planes is None else planes
    if not planes:
        return flat
    from wenart.blender import geom2d

    floor_z = float(level.get("elevation") or 0.0)
    pts = list(G.rotated_rectangle((float(center[0]), float(center[1])), (float(size[0]), float(size[1])),
                                   float(rotation_deg))) + [(float(center[0]), float(center[1]))]
    return round(min(geom2d.surface_z(planes, x, y) for x, y in pts) - floor_z, 4)


def plant_position(room: dict, furniture: list[dict], building: dict) -> tuple[Optional[tuple[float, float]], str]:
    """A free corner for the plant, or (None, reason). Milestone 11 (E2): under a sloped attic ceiling a corner where
    the ceiling over the plant is lower than its height (+ ``CEILING_CLEAR_M``) is no place for it."""
    ctx = placer.room_context(building, room)
    pieces = [placer.piece_from_furniture(f, i) for i, f in enumerate(furniture)]
    candidates = _corner_candidates(ctx)
    if not candidates:
        return None, "no convex corner"
    planes = ceiling_planes(building, room["level_id"])
    reasons = []
    for center in candidates:
        if planes:
            ceiling = ceiling_over(building, room["level_id"], center, PLANT_SIZE, planes=planes)
            if ceiling < PLANT_HEIGHT_M + CEILING_CLEAR_M:
                reasons.append(f"{center}: sloped ceiling {ceiling:.2f} m")
                continue
        plant = placer.Piece("plant", center, 0.0, PLANT_SIZE, False, index=len(pieces))
        checks = placer.check_piece(plant, pieces, ctx)
        failed = placer.failed_checks(checks)
        if not failed and any(p.type in placer.schemas.CLEARANCE_TYPES
                              and plant.polygon().intersection(p.front_zone()).area > placer.AREA_EPS
                              for p in pieces):
            failed = ["clearance of another piece"]
        # 27 Oct 2026 (run 160846): only a walkway the plant blocks itself (one blocked before stays a layout finding)
        if not failed and set(placer.walkway_failures(pieces + [plant], ctx)) - set(placer.walkway_failures(pieces, ctx)):
            failed = ["walkway"]
        if not failed:
            return center, "free corner"
        reasons.append(f"{center}: {', '.join(failed)}")
    return None, "no free corner (" + "; ".join(reasons) + ")"


def trusted_host(piece: dict) -> bool:
    """Fix round after P4a (module docstring): a piece whose type and place decor may trust: verified, or a
    vector-drawn piece the reading typed by code (``program.unsure_anchor`` False for an ``unverified`` piece)."""
    if piece.get("status") == "verified":
        return True
    if piece.get("status") != "unverified":
        return False
    from wenart.furniture import program as PR     # lazy: program reads the groups

    return not PR.unsure_anchor(piece)


def _usable_anchor(piece: dict) -> bool:
    """A piece decor may be placed around: verified (type and place trusted; fix round after P4a: or typed by code
    from the drawing, ``trusted_host``) and built (Milestone 12: ``piece_is_built``: no untyped piece, no library
    gap)."""
    return trusted_host(piece) and piece_is_built(piece)


def _to_local(geom, center, rotation_deg: float):
    """A world geometry in the frame of a piece (origin at its centre, axes turned by its rotation)."""
    return affinity.rotate(affinity.translate(geom, -center[0], -center[1]), -rotation_deg, origin=(0.0, 0.0))


def _to_world(point, center, rotation_deg: float) -> tuple[float, float]:
    p = G.rotate_point((center[0] + point[0], center[1] + point[1]), rotation_deg, (center[0], center[1]))
    return (p[0], p[1])


def _local_bounds(pieces: list[dict], center, rotation_deg: float) -> tuple[float, float, float, float]:
    """Bounds of the footprints of ``pieces`` in the frame (``center``, ``rotation_deg``)."""
    geoms = [_to_local(placer.piece_from_furniture(p).polygon(), center, rotation_deg) for p in pieces]
    return unary_union(geoms).bounds


def fit_rug(rect: tuple[float, float, float, float], allowed_local, key_point: tuple[float, float],
            min_side: float = RUG_MIN_SIDE_M, step: float = RUG_GRID_M
            ) -> tuple[Optional[tuple[float, float, float, float]], str]:
    """The largest rectangle inside the local rectangle ``rect`` = (x0, y0, x1, y1) that lies inside
    ``allowed_local`` and keeps ``key_point`` on it (pure; the rug is cut, never moved or turned).

    Exact on a grid of about ``step`` (the cells divide ``rect`` evenly, so an unobstructed rectangle comes
    back whole): a cell is free when the allowed area covers it; for every top row and every bottom row
    around the key cell the free run of columns through the key column gives the widest rectangle; the
    largest area wins (ties: the first found). Returns the rectangle, or None and why (the key point not on
    free floor, a side below ``min_side``)."""
    import numpy as np
    import shapely

    x0, y0, x1, y1 = (float(v) for v in rect)
    kx, ky = (float(v) for v in key_point)
    if not (x0 <= kx <= x1 and y0 <= ky <= y1):
        return None, "the group's key piece is outside the rug box"
    nx = max(1, int(round((x1 - x0) / step)))
    ny = max(1, int(round((y1 - y0) / step)))
    sx, sy = (x1 - x0) / nx, (y1 - y0) / ny
    if allowed_local.is_empty:
        return None, "no free floor around the group"
    allowed = allowed_local.buffer(1e-7)                      # cells on its edge are in it
    shapely.prepare(allowed)
    gx, gy = np.meshgrid(x0 + np.arange(nx) * sx, y0 + np.arange(ny) * sy)
    free = shapely.covers(allowed, shapely.box(gx, gy, gx + sx, gy + sy))     # [row = y, column = x]
    kc, kr = min(nx - 1, int((kx - x0) / sx)), min(ny - 1, int((ky - y0) / sy))
    if not free[kr, kc]:
        return None, "the group's key piece does not stand on free floor (wall, door swing or fixed piece)"
    if free.all():
        return (x0, y0, x1, y1), "ok"
    prefix = np.zeros((ny + 1, nx), dtype=np.int32)
    prefix[1:] = np.cumsum(free, axis=0)
    bottoms = np.arange(kr, ny)
    best = (0, None)
    for top in range(kr + 1):
        heights = bottoms - top + 1
        ok = (prefix[bottoms + 1, :] - prefix[top, :]) == heights[:, None]     # rows top..b all free
        left = np.cumprod(ok[:, kc::-1], axis=1).sum(axis=1)
        right = np.cumprod(ok[:, kc:], axis=1).sum(axis=1)
        width = np.where(ok[:, kc], left + right - 1, 0)
        area = width * heights
        i = int(np.argmax(area))
        if area[i] > best[0]:
            best = (int(area[i]), (kc - int(left[i]) + 1, top, kc + int(right[i]) - 1, int(bottoms[i])))
    if best[1] is None:
        return None, "no free floor around the group"
    c0, r0, c1, r1 = best[1]
    got = (x0 + c0 * sx, y0 + r0 * sy, x0 + (c1 + 1) * sx, y0 + (r1 + 1) * sy)
    if got[2] - got[0] < min_side - 1e-9 or got[3] - got[1] < min_side - 1e-9:
        return None, f"cut to {got[2] - got[0]:.2f} x {got[3] - got[1]:.2f} m, below {min_side} m"
    return got, "ok"


def _rug_forbidden(ctx: placer.RoomContext, furniture: list[dict], rugs: list[Polygon]):
    """The floor a rug never covers: door swings, blocker pieces (``RUG_BLOCKER_TYPES`` and not-built symbols; not a
    drawn rug outline, Milestone 11 ``infer.py``) and the rugs placed before."""
    zones = [d.swing for d in ctx.doors if d.swing is not None and not d.swing.is_empty]
    zones += [placer.piece_from_furniture(f).polygon() for f in furniture
              if (f["type"] in RUG_BLOCKER_TYPES or f.get("build", True) is False)
              and f.get("inferred_as") != "rug"]
    zones += list(rugs)
    return unary_union(zones) if zones else None


def _rug_item(ctx: placer.RoomContext, frame_piece: dict, group: list[dict], region, key_point, furniture: list[dict],
              rugs: list[Polygon], reason: str) -> tuple[Optional[dict], str]:
    """A rug under ``group`` in the frame of ``frame_piece`` (``region`` = local (x0, y0, x1, y1) of the group
    before the margin), or (None, why)."""
    fp = frame_piece["footprint"]
    center, rot = (float(fp["center"][0]), float(fp["center"][1])), float(fp["rotation_deg"])
    x0, y0, x1, y1 = region
    rect = (x0 - RUG_MARGIN_M, y0 - RUG_MARGIN_M, x1 + RUG_MARGIN_M, y1 + RUG_MARGIN_M)
    allowed = ctx.polygon.buffer(-RUG_ROOM_INSET_M, join_style="mitre")
    forbidden = _rug_forbidden(ctx, furniture, rugs)
    if forbidden is not None:
        allowed = allowed.difference(forbidden)
    got, why = fit_rug(rect, _to_local(allowed, center, rot), key_point)
    if got is None:
        return None, why
    gx0, gy0, gx1, gy1 = got
    w = math.floor((gx1 - gx0) * 1000.0 + 1e-6) / 1000.0
    d = math.floor((gy1 - gy0) * 1000.0 + 1e-6) / 1000.0
    c = _to_world(((gx0 + gx1) / 2.0, (gy0 + gy1) / 2.0), center, rot)
    cut = "" if got == rect else f"; cut from {rect[2] - rect[0]:.2f} x {rect[3] - rect[1]:.2f} m to stay off walls, door swings and fixed pieces"
    return {"type": "rug", "center": [round(c[0], 3), round(c[1], 3)], "rotation_deg": round(rot, 3),
            "size": [w, d], "anchor_ids": [p["id"] for p in group], "reason": reason + cut}, "ok"


def inner_corner_region(sofa: dict, table: dict) -> tuple[float, float, float, float]:
    """Milestone 10: the rug region of a corner sofa group in the sofa's frame (pure): from the chaise's inner edge
    (``schemas.l_parts``) across the free inner corner in front of the main seat, down to the coffee table's far
    edge; the table's own box is always inside."""
    from wenart.blender import parametric as P

    fp = sofa["footprint"]
    side = sofa.get("chaise_side") if sofa.get("chaise_side") in ("left", "right") else "right"
    main, chaise = P.l_parts(fp["size"], side, sofa.get("chaise_depth"), sofa.get("seat_depth"),
                             sofa.get("chaise_width"))
    tx0, ty0, tx1, ty1 = _local_bounds([table], fp["center"], float(fp["rotation_deg"]))
    if side == "right":
        x0, x1 = main[0], chaise[0]
    else:
        x0, x1 = chaise[1], main[1]
    return (min(x0, tx0), min(chaise[2], ty0), max(x1, tx1), main[2])


def rug_polygon(item: dict) -> Polygon:
    return placer.Piece("rug", tuple(item["center"]), item["rotation_deg"], tuple(item["size"]), False).polygon()


SOLVER_RUG_ROLE = "rug"           # Milestone 13: the group role of a rug the solver laid (solver._rug_dicts)


def solver_rugs(building: dict, room_id: Optional[str] = None) -> list[dict]:
    """Milestone 13 (R6): the rugs the group solver laid as group members (decor items with ``group.role == "rug"``,
    written by ``solver.apply_candidate``), of one room or of the whole building, in building order. The decor
    stages keep them (``add_decor``; the AI decorator seeds its decor with them the same way). A rug whose pieces
    are all gone or not built (``piece_is_built``: the agent removed the sofa, the fit left the bed unbuilt) is no
    solver rug any more (the ``sync_to_hosts`` rule): it is left out (``stale_solver_rugs`` lists it)."""
    return [d for d in _solver_rug_items(building, room_id) if _rug_alive(building, d)]


def stale_solver_rugs(building: dict, room_id: Optional[str] = None) -> list[dict]:
    """The solver's rug members ``solver_rugs`` leaves out: their pieces are all gone or not built."""
    return [d for d in _solver_rug_items(building, room_id) if not _rug_alive(building, d)]


def _solver_rug_items(building: dict, room_id: Optional[str]) -> list[dict]:
    return [d for d in building.get("decor") or []
            if isinstance(d, dict) and (d.get("group") or {}).get("role") == SOLVER_RUG_ROLE
            and (room_id is None or d.get("room_id") == room_id)]


def _rug_alive(building: dict, rug: dict) -> bool:
    pieces = {p.get("id"): p for p in building.get("furniture") or []}
    anchors = [a for a in rug.get("anchor_ids") or [] if a]
    return any(piece_is_built(pieces.get(a)) for a in anchors)


def decor_counters(items: list[dict]) -> dict[str, int]:
    """``{level id: highest n}`` of the ids ``dec_<level>_<n>`` among ``items``, so a decor stage that keeps items
    numbers its new ones after them (Milestone 13: the solver's rugs keep their ids)."""
    out: dict[str, int] = {}
    for d in items or []:
        m = re.match(r"^dec_(.+)_(\d+)$", str(d.get("id") or ""))
        if m:
            out[m.group(1)] = max(out.get(m.group(1), 0), int(m.group(2)))
    return out


def rugs_for_room(room: dict, furniture: list[dict], building: dict) -> tuple[list[dict], list[str]]:
    """The rugs of one room (without ids) and the notes for the report (docs/milestone8.md §4). Milestone 13: the
    solver's rugs already in ``building["decor"]`` (``solver_rugs``) are kept: a group one of them belongs to gets
    no rule rug (listed), and the rule rugs stay off them."""
    ctx = placer.room_context(building, room)
    usable = [f for f in furniture if _usable_anchor(f)]
    rugs: list[dict] = []
    notes: list[str] = []
    kept = solver_rugs(building, room["id"])
    placed: list[Polygon] = [rug_polygon(k) for k in kept]
    covered: dict[str, str] = {a: k["id"] for k in kept for a in k.get("anchor_ids") or []}

    def add(item, why, what):
        if item is None:
            notes.append(f"no rug {what}: {why}")
        else:
            rugs.append(item)
            placed.append(rug_polygon(item))

    def solver_laid(what: str, *pieces) -> bool:
        hit = next((covered[p["id"]] for p in pieces if p["id"] in covered), None)
        if hit is not None:
            notes.append(f"rug {what}: {hit} laid by the group solver (kept)")
        return hit is not None

    if room.get("room_type") in LIVING_RUG_ROOM_TYPES:
        tables = [f for f in usable if f["type"] == "table_coffee"]
        group = None
        for sofa in sorted((f for f in usable if f["type"] in LIVING_RUG_SOFAS),
                           key=lambda f: (-float(f["footprint"]["size"][0]), f["id"])):
            fp = sofa["footprint"]
            sw, sd = (float(v) for v in fp["size"])
            near = []
            for t in tables:
                lx, ly = _to_local(Point(t["footprint"]["center"]), fp["center"], float(fp["rotation_deg"])).coords[0]
                if ly < -sd / 2.0 and -ly - sd / 2.0 <= COFFEE_TABLE_REACH_M and abs(lx) <= sw / 2.0 + 0.3:
                    near.append((-ly, t["id"], t, (lx, ly)))
            if near:
                _d, _id, table, key = min(near, key=lambda n: (n[0], n[1]))
                group = (sofa, [sofa, table], key)
                break
        if group is not None:
            sofa, members, key = group
            if not solver_laid(f"under {sofa['id']} + {members[1]['id']}", sofa, members[1]):
                fp = sofa["footprint"]
                region = _local_bounds(members, fp["center"], float(fp["rotation_deg"]))
                if sofa["type"] == "sofa_corner":
                    region = inner_corner_region(sofa, members[1])
                item, why = _rug_item(ctx, sofa, members, region, key, furniture, placed,
                                      "rug under the sofa and coffee table group")
                add(item, why, f"under {sofa['id']} + {members[1]['id']}")
        elif any(f["type"] in LIVING_RUG_SOFAS for f in usable):
            if not any(f["id"] in covered for f in usable if f["type"] in LIVING_RUG_SOFAS):
                # 27 Oct 2026 (lesson UL42: real06's 55 m2 salon had no rug, "no coffee table in front of a sofa";
                # every reference photo of a living room shows one): the rug lies in front of the largest sofa, its
                # front legs on it, over the seating area
                sofa = max((f for f in usable if f["type"] in LIVING_RUG_SOFAS),
                           key=lambda f: (float(f["footprint"]["size"][0]), f["id"]))
                fp = sofa["footprint"]
                sw, sd = (float(v) for v in fp["size"])
                region = (-sw / 2.0, -sd / 2.0 - SEATING_RUG_DEPTH_M, sw / 2.0, -sd / 2.0 + SEATING_RUG_UNDER_M)
                item, why = _rug_item(ctx, sofa, [sofa], region, (0.0, -sd / 2.0 - SEATING_RUG_DEPTH_M / 2.0),
                                      furniture, placed, "rug in front of the sofa, its front legs on it (no coffee "
                                      "table: the seating area)")
                add(item, why, f"in front of {sofa['id']}")
    if room.get("room_type") in BED_RUG_ROOM_TYPES:
        for bed in sorted((f for f in usable if f["type"] == "bed_single"), key=lambda f: f["id"]):
            if solver_laid(f"beside {bed['id']}", bed):
                continue
            # 27 Oct 2026 (UL42): a single bed's rug lies under its lower two thirds and out on its free side (the
            # side away from the wall; both sides when it stands free)
            bw, bd = (float(v) for v in bed["footprint"]["size"])
            region = (-bw / 2.0 - SINGLE_BED_RUG_OUT_M, -bd / 2.0, bw / 2.0 + SINGLE_BED_RUG_OUT_M,
                      -bd / 2.0 + BED_RUG_SHARE * bd)
            item, why = _rug_item(ctx, bed, [bed], region, (0.0, -bd / 2.0 + BED_RUG_SHARE * bd / 2.0), furniture,
                                  placed, "rug under the lower two thirds of the single bed and beside it")
            add(item, why, f"beside {bed['id']}")
        for bed in sorted((f for f in usable if f["type"] == "bed_double"), key=lambda f: f["id"]):
            if solver_laid(f"under {bed['id']}", bed):
                continue
            bw, bd = (float(v) for v in bed["footprint"]["size"])
            region = (-bw / 2.0, -bd / 2.0, bw / 2.0, -bd / 2.0 + BED_RUG_SHARE * bd)
            item, why = _rug_item(ctx, bed, [bed], region, (0.0, -bd / 2.0 + BED_RUG_SHARE * bd / 2.0), furniture,
                                  placed, "rug under the lower two thirds of the double bed")
            add(item, why, f"under {bed['id']}")
    for table in sorted((f for f in usable if f["type"] == "table_dining"), key=lambda f: f["id"]):
        if solver_laid(f"under {table['id']}", table):
            continue
        tw, td = (float(v) for v in table["footprint"]["size"])
        region = (-tw / 2.0 - DINING_CHAIR_M, -td / 2.0 - DINING_CHAIR_M, tw / 2.0 + DINING_CHAIR_M,
                  td / 2.0 + DINING_CHAIR_M)
        item, why = _rug_item(ctx, table, [table], region, (0.0, 0.0), furniture, placed,
                              f"rug under the dining table (+ {DINING_CHAIR_M} m each side for the chairs)")
        add(item, why, f"under {table['id']}")
    return rugs, notes


def _wall_behind(piece: dict, ctx: placer.RoomContext) -> Optional[tuple[int, float]]:
    """``(segment index, gap)`` of the room wall the piece's back stands against: parallel within
    ``WALL_PARALLEL_DEG``, facing the piece's back, the back edge within ``WALL_MAX_GAP_M``, the piece's
    centre between the segment's ends; the nearest."""
    fp = piece["footprint"]
    rad = math.radians(float(fp["rotation_deg"]))
    back = (-math.sin(rad), math.cos(rad))                    # local +Y
    d = float(fp["size"][1])
    back_mid = (float(fp["center"][0]) + back[0] * d / 2.0, float(fp["center"][1]) + back[1] * d / 2.0)
    cos_tol = math.cos(math.radians(WALL_PARALLEL_DEG))
    best = None
    for i, (a, b) in enumerate(ctx.segments):
        n = ctx.segment_normal(i)                             # inward
        if n[0] * back[0] + n[1] * back[1] > -cos_tol:        # the wall must face the piece's back
            continue
        length = G.distance(a, b)
        along = ((back_mid[0] - a[0]) * (b[0] - a[0]) + (back_mid[1] - a[1]) * (b[1] - a[1])) / length
        if not 0.0 <= along <= length:
            continue
        gap = (back_mid[0] - a[0]) * n[0] + (back_mid[1] - a[1]) * n[1]
        if -0.05 <= gap <= WALL_MAX_GAP_M and (best is None or gap < best[1] - 1e-9):
            best = (i, gap)
    return best


def _nearest_wall_id(building: dict, level_id: str, point) -> Optional[str]:
    best = None
    for w in building.get("walls") or []:
        if w.get("level_id") != level_id:
            continue
        dist = G.point_segment_distance(point, tuple(w["start"]), tuple(w["end"]))
        limit = float(w.get("thickness") or placer.DEFAULT_WALL_THICKNESS_M) / 2.0 + 0.05
        if dist <= limit and (best is None or dist < best[0]):
            best = (dist, w["id"])
    return best[1] if best else None


def wall_art_for_host(host: dict, ctx: placer.RoomContext, building: dict, level: dict, dtype: str = "wall_art",
                      width_share: float = WALL_ART_WIDTH_SHARE, max_w: float = WALL_ART_MAX_W,
                      gap: float = WALL_ART_GAP_M, min_w: float = WALL_ART_MIN_W) -> tuple[Optional[dict], str]:
    """Wall art above ``host`` (without id), or (None, why). Milestone 9: the same geometry hangs a ``mirror``
    (``dtype``) with its own width share, maximum width, gap and minimum width (``decor_ai.MIRROR_*``)."""
    found = _wall_behind(host, ctx)
    if found is None:
        return None, f"{host['id']} has no wall behind it"
    i, _gap = found
    a, b = ctx.segments[i]
    seg_len = G.distance(a, b)
    u = ((b[0] - a[0]) / seg_len, (b[1] - a[1]) / seg_len)
    n = ctx.segment_normal(i)
    c = host["footprint"]["center"]
    s_c = (c[0] - a[0]) * u[0] + (c[1] - a[1]) * u[1]
    width = min(width_share * float(host["footprint"]["size"][0]), max_w)
    half = min(width / 2.0, s_c - WALL_END_MARGIN_M, seg_len - WALL_END_MARGIN_M - s_c)
    narrowed = []
    if half < width / 2.0 - 1e-9:
        narrowed.append("wall end")
    doors, windows = placer.room_openings(building, ctx.room)
    walls = {w["id"]: w for w in building.get("walls") or []}
    for op in doors + windows:
        oc = (float(op["center"][0]), float(op["center"][1]))
        wall = walls.get(op.get("wall_id") or "")
        t = float(wall["thickness"]) if wall and wall.get("thickness") else placer.DEFAULT_WALL_THICKNESS_M
        if G.point_segment_distance(oc, a, b) > t / 2.0 + 0.06:
            continue                                          # not on this wall (the placer's opening rule)
        s_o = (oc[0] - a[0]) * u[0] + (oc[1] - a[1]) * u[1]
        free = abs(s_o - s_c) - float(op["width"]) / 2.0 - OPENING_MARGIN_M
        if free < half - 1e-9:
            half = free
            narrowed.append(f"{op['type']} {op['id']}")
    width_out = math.floor(2.0 * half * 1000.0 + 1e-6) / 1000.0
    what_item = "the picture" if dtype == "wall_art" else f"the {dtype.replace('_', ' ')}"
    if width_out < min_w - 1e-9:
        return None, (f"above {host['id']}: {', '.join(narrowed) or 'the wall ends'} on the wall behind it "
                      f"leave {max(0.0, width_out):.2f} m for {what_item} (min {min_w} m)")
    top = float(placer_bbox_height(host))
    bottom = round(top + gap, 3)
    wall_point = (a[0] + u[0] * s_c, a[1] + u[1] * s_c)
    center = (wall_point[0] + n[0] * WALL_ART_DEPTH_M / 2.0, wall_point[1] + n[1] * WALL_ART_DEPTH_M / 2.0)
    rotation = G.normalise_angle(math.degrees(math.atan2(n[0], -n[1])))    # local +Y = out of the room
    ceiling = flat = float(level.get("ceiling_height") or 2.7)
    # Fix round after P3 (16-17 Oct 2026). What: under a sloped roof the art's top stays WALL_ART_CEILING_M under the
    # sloped ceiling at its own wall position (``ceiling_over`` over its footprint on the wall), not the level's flat
    # ceiling height; it is made lower, or left out below WALL_ART_MIN_H. Why: P3's dec_L1_009, a mirror above a
    # console in r_L1_koridor, hung up to 2.35 m where the slope over the wall is 0.80 m high: it poked through the
    # L1 roof (X2 critical in all 4 agent rounds). How: the decor stage's own ceiling (``ceiling_planes``, the roof as
    # the build makes it); a level with a flat ceiling keeps the old rule.
    level_id = level.get("id") or host.get("level_id")
    planes = ceiling_planes(building, level_id) if level_id else []
    sloped = None
    if planes:
        sloped = ceiling_over(building, level_id, center, (width_out, WALL_ART_DEPTH_M), rotation, planes=planes)
        ceiling = min(ceiling, sloped)
    max_h = round(ceiling - WALL_ART_CEILING_M - bottom, 3)
    if max_h < WALL_ART_MIN_H - 1e-9:
        where = "the ceiling" if sloped is None or sloped >= flat else \
            f"the sloped ceiling ({sloped:.2f} m high over the wall)"
        return None, f"above {host['id']}: {max(0.0, max_h):.2f} m left under {where} (min {WALL_ART_MIN_H} m)"
    what = {"sofa": "a sofa", "bed_double": "a bed's headboard", "bed_single": "a bed's headboard",
            "dresser": "a dresser"}.get(host["type"], "a " + host["type"].replace("_", " "))
    reason = f"{dtype.replace('_', ' ')} centred above {what} on the wall behind it"
    if narrowed:
        reason += f" (narrowed for {', '.join(narrowed)})"
    if sloped is not None and sloped < flat:
        reason += f" (kept under the sloped ceiling, {sloped:.2f} m high over the wall)"
    return {"type": dtype, "center": [round(center[0], 3), round(center[1], 3)], "rotation_deg": round(rotation, 3),
            "size": [width_out, WALL_ART_DEPTH_M], "anchor_ids": [host["id"]],
            "wall_point": [round(wall_point[0], 3), round(wall_point[1], 3)],
            "wall_id": _nearest_wall_id(building, host["level_id"], wall_point), "gap_m": gap,
            "bottom_m": bottom, "max_height_m": max_h, "reason": reason}, "ok"


# 27 Oct 2026 (run 160846, real06's 55 m2 salon: the recipe's wall art and plants were musts, yet the only art slot was
# above the sofa, where a window left 0.00 m, and no corner was free for a plant): a designer hangs art on any free
# wall and stands a plant beside the sofa or a window. ``free_wall_art``: the longest free stretches of the room's
# walls (no door, window or opening within OPENING_MARGIN_M, no piece taller than FREE_WALL_TALL_M in front of it
# within FREE_WALL_FRONT_M), at least FREE_WALL_MIN_M long; the picture is FREE_WALL_ART_SHARE of the stretch (at
# most WALL_ART_MAX_W), centred, its bottom at FREE_WALL_ART_BOTTOM_M or WALL_ART_GAP_M over the low pieces in
# front. ``wall_candidates``: plant places along the walls, every WALL_STEP_M, inset like a corner plant.
FREE_WALL_MIN_M = 1.0
FREE_WALL_TALL_M = 1.3
FREE_WALL_FRONT_M = 0.8
FREE_WALL_ART_SHARE = 0.55
FREE_WALL_ART_BOTTOM_M = 1.2
FREE_WALL_ART_MAX = 2
WALL_STEP_M = 0.5


def _free_intervals(lo: float, hi: float, blocked: list[tuple[float, float]]) -> list[tuple[float, float]]:
    """The parts of ``[lo, hi]`` outside every ``blocked`` interval (pure)."""
    out, cur = [], lo
    for a, b in sorted(blocked):
        if b <= cur:
            continue
        if a > cur:
            out.append((cur, min(a, hi)))
        cur = max(cur, b)
        if cur >= hi:
            break
    if cur < hi:
        out.append((cur, hi))
    return [(a, b) for a, b in out if b - a > 1e-6]


def free_wall_art(room: dict, furniture: list[dict], building: dict, ctx: Optional[placer.RoomContext] = None,
                  level: Optional[dict] = None, dtype: str = "wall_art",
                  most: int = FREE_WALL_ART_MAX) -> list[dict]:
    """Wall art on the room's free walls (the comment above), the longest stretches first, at most ``most`` (one per
    wall); each item as ``wall_art_for_host`` makes it, without ``anchor_ids`` (no host), ``free_wall`` True."""
    ctx = ctx or placer.room_context(building, room)
    level = level or next((lv for lv in building.get("levels") or [] if lv.get("id") == room["level_id"]), {})
    doors, windows = placer.room_openings(building, room)
    walls = {w["id"]: w for w in building.get("walls") or []}
    floor_pieces = [f for f in furniture if f.get("footprint") and f.get("build", True) is not False]
    ceiling_flat = float(level.get("ceiling_height") or 2.7)
    planes = ceiling_planes(building, room["level_id"])
    found = []
    for i, (a, b) in enumerate(ctx.segments):
        seg_len = G.distance(a, b)
        if seg_len < FREE_WALL_MIN_M:
            continue
        u = ((b[0] - a[0]) / seg_len, (b[1] - a[1]) / seg_len)
        n = ctx.segment_normal(i)
        blocked = []
        for op in doors + windows:
            oc = (float(op["center"][0]), float(op["center"][1]))
            wall = walls.get(op.get("wall_id") or "")
            t = float(wall["thickness"]) if wall and wall.get("thickness") else placer.DEFAULT_WALL_THICKNESS_M
            if G.point_segment_distance(oc, a, b) > t / 2.0 + 0.06:
                continue
            s_o = (oc[0] - a[0]) * u[0] + (oc[1] - a[1]) * u[1]
            half = float(op["width"]) / 2.0 + OPENING_MARGIN_M
            blocked.append((s_o - half, s_o + half))
        low_tops = []                                         # (s0, s1, top) of the low pieces in front
        for f in floor_pieces:
            poly = placer.piece_from_furniture(f).polygon()
            pts = list(poly.exterior.coords)
            depth = [(x - a[0]) * n[0] + (y - a[1]) * n[1] for x, y in pts]
            if min(depth) > FREE_WALL_FRONT_M or max(depth) < -0.05:
                continue
            along = [(x - a[0]) * u[0] + (y - a[1]) * u[1] for x, y in pts]
            s0, s1 = min(along), max(along)
            if s1 < 0.0 or s0 > seg_len:
                continue
            hung = placer.schemas.off_floor(f)                 # a wall-hung piece takes its stretch of the wall
            top = 0.0 if hung else float(placer_bbox_height(f))
            if top > FREE_WALL_TALL_M or hung:
                blocked.append((s0 - 0.05, s1 + 0.05))
            else:
                low_tops.append((s0, s1, top))
        for s0, s1 in _free_intervals(WALL_END_MARGIN_M, seg_len - WALL_END_MARGIN_M, blocked):
            if s1 - s0 >= FREE_WALL_MIN_M:
                found.append((s1 - s0, i, s0, s1, u, n, a, low_tops))
    out: list[dict] = []
    used_walls = set()
    for length, i, s0, s1, u, n, a, low_tops in sorted(found, key=lambda x: (-x[0], x[1], x[2])):
        if len(out) >= most or i in used_walls:
            continue
        width = math.floor(min(WALL_ART_MAX_W, FREE_WALL_ART_SHARE * length) * 1000.0) / 1000.0
        if width < WALL_ART_MIN_W:
            continue
        s_c = (s0 + s1) / 2.0
        under = [top for p0, p1, top in low_tops if p1 > s_c - width / 2.0 and p0 < s_c + width / 2.0]
        bottom = round(max([FREE_WALL_ART_BOTTOM_M] + [t + WALL_ART_GAP_M for t in under]), 3)
        wall_point = (a[0] + u[0] * s_c, a[1] + u[1] * s_c)
        center = (wall_point[0] + n[0] * WALL_ART_DEPTH_M / 2.0, wall_point[1] + n[1] * WALL_ART_DEPTH_M / 2.0)
        rotation = G.normalise_angle(math.degrees(math.atan2(n[0], -n[1])))
        ceiling = ceiling_flat
        if planes:
            ceiling = min(ceiling, ceiling_over(building, room["level_id"], center, (width, WALL_ART_DEPTH_M),
                                                rotation, planes=planes))
        max_h = round(ceiling - WALL_ART_CEILING_M - bottom, 3)
        if max_h < WALL_ART_MIN_H - 1e-9:
            continue
        used_walls.add(i)
        out.append({"type": dtype, "center": [round(center[0], 3), round(center[1], 3)],
                    "rotation_deg": round(rotation, 3), "size": [width, WALL_ART_DEPTH_M],
                    "wall_point": [round(wall_point[0], 3), round(wall_point[1], 3)],
                    "wall_id": _nearest_wall_id(building, room["level_id"], wall_point), "gap_m": WALL_ART_GAP_M,
                    "bottom_m": bottom, "max_height_m": max_h, "free_wall": True,
                    "reason": f"{dtype.replace('_', ' ')} centred on a free wall stretch of {length:.2f} m (no door, "
                              f"window or tall piece in front)"})
    return out


def wall_candidates(ctx: placer.RoomContext, inset: float = CORNER_INSET_M,
                    step: float = WALL_STEP_M) -> list[tuple[float, float]]:
    """Floor places along the room's walls (pure but for the context): every ``step`` m along each wall segment,
    ``inset`` into the room, from ``inset`` + 0.2 m off its ends, in boundary order."""
    out = []
    for i, (a, b) in enumerate(ctx.segments):
        seg_len = G.distance(a, b)
        start = inset + 0.2
        if seg_len < 2.0 * start:
            continue
        u = ((b[0] - a[0]) / seg_len, (b[1] - a[1]) / seg_len)
        nrm = ctx.segment_normal(i)
        k = 0
        while start + k * step <= seg_len - inset - 0.2 + 1e-9:
            s = start + k * step
            out.append((round(a[0] + u[0] * s + nrm[0] * inset, 3), round(a[1] + u[1] * s + nrm[1] * inset, 3)))
            k += 1
    return out


def placer_bbox_height(piece: dict) -> float:
    """The top of a piece above its floor as the scene will build it (``parametric.piece_bbox``: the fitted
    library box or the parametric box, a headboard included)."""
    from wenart.blender import parametric as P   # pure Python (no bpy)

    return P.piece_bbox(piece)[2]


def wall_art_for_room(room: dict, furniture: list[dict], building: dict) -> tuple[Optional[dict], str]:
    """At most one wall art piece for ``room`` (without id): the first host of ``WALL_ART_HOST_TYPES`` order
    (then by id) that has a wall behind it with room for the picture; else (None, the reasons)."""
    if room.get("room_type") not in WALL_ART_ROOM_TYPES:
        return None, "-"
    hosts = sorted((f for f in furniture if _usable_anchor(f) and f["type"] in WALL_ART_HOST_TYPES),
                   key=lambda f: (WALL_ART_HOST_TYPES.index(f["type"]), f["id"]))
    if not hosts:
        return None, "no sofa, bed or dresser"
    ctx = placer.room_context(building, room)
    level = next((lv for lv in building.get("levels") or [] if lv.get("id") == room["level_id"]), {})
    reasons = []
    for host in hosts:
        item, why = wall_art_for_host(host, ctx, building, level)
        if item is not None:
            return item, "ok"
        reasons.append(why)
    return None, "; ".join(reasons)


def add_decor(building: dict) -> tuple[dict, list[dict]]:
    """Return (building with ``decor``, report rows). Idempotent: existing decor is replaced, except the rugs the
    group solver laid as group members (Milestone 13, ``solver_rugs``), which are kept with their ids."""
    out = json.loads(json.dumps(building))
    kept = solver_rugs(out)
    stale = stale_solver_rugs(out)                    # review (round 2): a solver rug under pieces gone or unbuilt
    out["decor"] = kept
    rows: list[dict] = []
    if not decor_allowed(out):
        out["decor"] = []
        rows.append({"room_id": "-", "label": "-", "note": "brief.decor is false: no decor"
                     + (f" (the group solver's {len(kept)} rug(s) left out too: "
                        f"{', '.join(k['id'] for k in kept)})" if kept else "")})
        return out, rows
    counters: dict[str, int] = decor_counters(kept)
    for d in stale:
        rows.append({"room_id": d.get("room_id") or "-", "label": "-",
                     "note": f"rug {d.get('id')} of the group solver not kept: its pieces "
                             f"{', '.join(a for a in d.get('anchor_ids') or [] if a) or 'none'} are gone or not "
                             f"built (the rule rugs decide again)"})

    def new_id(level_id: str) -> str:
        counters[level_id] = counters.get(level_id, 0) + 1
        return f"dec_{level_id}_{counters[level_id]:03d}"

    targets, notes = copy_targets(out)
    for room, pieces in rooms_with_pieces(out):
        if room["id"] in targets:
            continue
        items, row = rule_decor_room(out, room, pieces, new_id)
        out["decor"].extend(items)
        rows.append(row)
    copies, copy_notes = copy_partner_decor(out, out["decor"], targets, new_id)
    out["decor"].extend(copies)
    for rid, (pid, kind, _t) in sorted(targets.items()):
        room = next(r for r in out["rooms"] if r["id"] == rid)
        rows.append({"room_id": rid, "label": room["label"], "cushions": "-", "books": "-", "plant": "-", "rugs": "-",
                     "wall_art": "-", "note": f"decor copied from {pid} ({kind}): "
                                              f"{sum(1 for c in copies if c['room_id'] == rid)} item(s)"})
    for note in notes + copy_notes:
        rows.append({"room_id": "-", "label": "-", "note": note})
    attach_host_frames(out)                           # Milestone 12: every item in its host's frame
    return out, rows


def rooms_with_pieces(building: dict) -> list[tuple[dict, list[dict]]]:
    """``(room, its furniture)`` for every room of the building, in building order."""
    furniture_by_room: dict[str, list[dict]] = {}
    for f in building["furniture"]:
        if f.get("room_id"):
            furniture_by_room.setdefault(f["room_id"], []).append(f)
    return [(room, furniture_by_room.get(room["id"], [])) for room in building["rooms"]]


def rule_decor_room(building: dict, room: dict, pieces: list[dict], new_id) -> tuple[list[dict], dict]:
    """The rule decor of one room (the M4 cushions, books and plant, the M8 rugs and wall art) and its report row;
    ``new_id(level_id)`` numbers the items. Milestone 9: also the fallback of the AI decorator per room."""
    items: list[dict] = []
    row = {"room_id": room["id"], "label": room["label"], "cushions": 0, "books": 0, "plant": "-", "rugs": 0,
           "wall_art": "-", "note": ""}
    if room.get("room_type") in NO_DECOR_ROOM_TYPES:
        row["note"] = f"{room['room_type']} room: no decor (docs/milestone7.md §0)"
        return items, row
    for host in pieces:
        if not trusted_host(host) or host["type"] not in HOST_TYPES or not piece_is_built(host):
            continue
        if HOST_TYPES[host["type"]] == "cushion" and not takes_cushions(host):
            continue                                  # Milestone 12: the model has its own cushions or bedding
        for item in host_decor(host):
            assert max(item["size"]) <= MAX_DECOR_M
            items.append({"id": new_id(room["level_id"]), "kind": "decor", "type": item["type"],
                          "level_id": room["level_id"], "room_id": room["id"], "center": item["center"],
                          "rotation_deg": item["rotation_deg"], "size": item["size"], "asset": None,
                          "host_id": host["id"], "source": "added_by_ai", "method": "rule",
                          "reason": item["reason"]})
            row["cushions" if item["type"] == "cushion" else "books"] += 1
    if room.get("room_type") in PLANT_ROOM_TYPES and room_takes_decor(room):
        center, why = plant_position(room, pieces, building)
        if center is not None:
            items.append({"id": new_id(room["level_id"]), "kind": "decor", "type": "plant",
                          "level_id": room["level_id"], "room_id": room["id"], "center": list(center),
                          "rotation_deg": 0.0, "size": list(PLANT_SIZE), "asset": None, "host_id": None,
                          "source": "added_by_ai", "method": "rule", "reason": "potted plant in a free corner"})
            row["plant"] = f"{center[0]}, {center[1]}"
        else:
            row["plant"] = "none"
            row["note"] = why
    if room_takes_decor(room):
        notes = [row["note"]] if row["note"] else []
        rugs, rug_notes = rugs_for_room(room, pieces, building)
        for item in rugs:
            items.append(_large_item(new_id(room["level_id"]), room, item))
        kept = solver_rugs(building, room["id"])              # Milestone 13: the solver's rugs, kept as they are
        row["rugs"] = len(rugs) + len(kept)
        if kept:
            rug_notes.append(f"{len(kept)} rug(s) kept from the group solver ({', '.join(k['id'] for k in kept)})")
        art, why = wall_art_for_room(room, pieces, building)
        if art is not None:
            items.append(_large_item(new_id(room["level_id"]), room, art))
            row["wall_art"] = f"over {art['anchor_ids'][0]} ({art['size'][0]:.2f} m wide)"
        elif why != "-":
            row["wall_art"] = "none"
            rug_notes.append(f"no wall art: {why}")
        # 28 Oct 2026 (user: "kettle in the kitchen, microwave in the kitchen etc"): the worktop, dressed modestly
        worktop = kitchen_worktop_decor(building, room, pieces, new_id, existing=items)
        if worktop:
            items += worktop
            rug_notes.append(f"worktop: {', '.join(i['type'] for i in worktop)}")
        row["note"] = "; ".join(notes + rug_notes)
    return items, row


# --------------------------------------------------------------------------
# 28 Oct 2026: the kitchen worktop, dressed modestly (user: "More decor pieces needed ... kettle in the kitchen,
# microwave in the kitchen etc"; real06's kitchen: "nothing on the counter")
# --------------------------------------------------------------------------

KITCHEN_DECOR_TYPES: tuple[str, ...] = ("microwave", "kettle", "coffee_machine", "toaster", "chopping_board",
                                        "utensil_pot", "fruit_bowl")
# Real products (width, depth, height): a 20 l countertop microwave 45-49 x 33-40 x 26-30 cm, a 1.7 l kettle, a
# bean-to-cup coffee machine 24 x 43 x 35 cm, a 2-slice toaster, a 40 x 25 cm board, a utensil pot with its tools,
# a 28 cm fruit bowl (= parametric.DECOR_DEFAULT_HEIGHT for the heights).
KITCHEN_DECOR_SIZES: dict[str, tuple[float, float, float]] = {
    "microwave": (0.46, 0.36, 0.27), "kettle": (0.22, 0.16, 0.25), "coffee_machine": (0.24, 0.38, 0.35),
    "toaster": (0.28, 0.17, 0.19), "chopping_board": (0.40, 0.25, 0.02), "utensil_pot": (0.12, 0.12, 0.30),
    "fruit_bowl": (0.28, 0.28, 0.12)}
# The order they are placed in, and what each stands near: the microwave at a run end against a wall or a corner,
# the coffee machine (or, with no room for it, the toaster) at another end, the kettle by the sink, the utensil pot
# and the board beside the hob (outside its side gap), the fruit bowl on an island or in the middle of a free stretch.
KITCHEN_DECOR_ORDER: tuple[str, ...] = ("microwave", "coffee_machine", "kettle", "utensil_pot", "chopping_board",
                                        "fruit_bowl")
WORKTOP_HOB_CLEAR_M = 0.25        # nothing within this of a hob's sides (pans slide off onto the landing)
WORKTOP_SINK_CLEAR_M = 0.10       # nor this close to the sink's sides
WORKTOP_ITEM_GAP_M = 0.10         # between two items
WORKTOP_END_M = 0.05              # off the run's open ends
WORKTOP_BACK_M = 0.04             # an item's back this far off the wall (the splashback)
WORKTOP_WINDOW_CLEAR_M = 0.02     # an item lower than a window's sill over the worktop by this may stand in front of it
WORKTOP_PER_M = 0.5               # modest: at most one item per this much free worktop ...
KITCHEN_DECOR_MAX = 5             # ... and this many per kitchen
WORKTOP_TOP_RANGE_M = (0.80, 1.20)


def _worktop_z(counter: dict) -> float:
    h = counter.get("height")
    if isinstance(h, (int, float)) and not isinstance(h, bool) and WORKTOP_TOP_RANGE_M[0] <= h <= WORKTOP_TOP_RANGE_M[1]:
        return float(h)
    return 0.90


def _front_box(piece: dict):
    rot, size = placer.front_frame(piece["footprint"], piece.get("front_deg"))
    c = (float(piece["footprint"]["center"][0]), float(piece["footprint"]["center"][1]))
    return c, rot, float(size[0]), float(size[1])


def _x_extent_of(c, rot: float, geom) -> Optional[tuple[float, float]]:
    if geom is None or geom.is_empty or geom.area <= placer.AREA_EPS:
        return None
    r = math.radians(rot)
    xs = [(pt[0] - c[0]) * math.cos(r) + (pt[1] - c[1]) * math.sin(r)
          for g in getattr(geom, "geoms", [geom]) if hasattr(g, "exterior") for pt in g.exterior.coords]
    return (min(xs), max(xs)) if xs else None


def worktop_blocks(counter: dict, pieces: list[dict]) -> list[tuple[float, float, str]]:
    """The spans of a counter's worktop (its front frame's x) no item may take: every hob ``WORKTOP_HOB_CLEAR_M``
    wider on both sides, every sink ``WORKTOP_SINK_CLEAR_M`` wider, every piece standing in it taller than the
    worktop (a fridge column, a tall unit); an under-counter appliance's top is worktop."""
    c, rot, w, d = _front_box(counter)
    box = placer._local_box(c, rot, -w / 2.0, w / 2.0, -d / 2.0, d / 2.0)
    top = _worktop_z(counter)
    out = []
    for p in pieces:
        if p.get("id") == counter.get("id") or not p.get("footprint") or p.get("build") is False:
            continue
        try:
            inside = placer.drawn_piece(p).polygon().intersection(box)
        except (KeyError, TypeError, ValueError):
            continue
        if inside.is_empty or inside.area < 0.02:
            continue
        ext = _x_extent_of(c, rot, inside)
        if ext is None:
            continue
        if p.get("type") == "stove":
            out.append((ext[0] - WORKTOP_HOB_CLEAR_M, ext[1] + WORKTOP_HOB_CLEAR_M, "hob"))
        elif p.get("type") == "sink_kitchen":
            out.append((ext[0] - WORKTOP_SINK_CLEAR_M, ext[1] + WORKTOP_SINK_CLEAR_M, "sink"))
        elif p.get("type") not in ("kitchen_counter", "kitchen_island") and not schemas_off_floor(p) \
                and float(p.get("height") or 0.0) > top + 0.05:
            out.append((ext[0], ext[1], "tall"))
    return out


def schemas_off_floor(piece: dict) -> bool:
    from wenart.furniture import schemas
    return schemas.off_floor(piece)


def worktop_windows(counter: dict, building: dict, room: dict) -> list[tuple[float, float, float]]:
    """``(x0, x1, sill over the worktop)`` of the windows in the wall behind a counter (its front frame), whose
    width meets the counter's; a doorless opening (a pass-through over the counter) counts as a window with its sill
    (none: the floor)."""
    c, rot, w, d = _front_box(counter)
    doors, windows = placer.room_openings(building, room)
    windows = list(windows) + [o for o in doors if o.get("type") == "opening"]
    top = _worktop_z(counter)
    walls = {x.get("id"): x for x in building.get("walls") or []}
    out = []
    r = math.radians(rot)
    for o in windows:
        wall = walls.get(o.get("wall_id"))
        if wall is None or not o.get("center"):
            continue
        (x0, y0), (x1, y1) = wall["start"][:2], wall["end"][:2]
        length = math.hypot(x1 - x0, y1 - y0)
        if length < 1e-6:
            continue
        ux, uy = (x1 - x0) / length, (y1 - y0) / length
        half = float(o.get("width") or 0.9) / 2.0
        pts = [(float(o["center"][0]) + s * ux * half, float(o["center"][1]) + s * uy * half) for s in (-1, 1)]
        loc = [((px - c[0]) * math.cos(r) + (py - c[1]) * math.sin(r),
                -(px - c[0]) * math.sin(r) + (py - c[1]) * math.cos(r)) for px, py in pts]
        if any(ly < d / 2.0 - 0.05 or ly > d / 2.0 + 0.60 for _lx, ly in loc):
            continue                                       # not in the wall behind the counter
        lo, hi = sorted(lx for lx, _ly in loc)
        if hi <= -w / 2.0 or lo >= w / 2.0:
            continue
        out.append((lo, hi, float(o.get("sill_height") or 0.0) - top))
    return out


def worktop_item_ok(item: dict, counter: dict, pieces: list[dict], windows: list, others: list = ()) -> Optional[str]:
    """Why a worktop item fails the code checks, None when it passes (28 Oct 2026): on the counter's top (its box
    inside the counter's footprint: it rests on the worktop, never over its edge), off the hob and its side gap, off
    the sink, off the tall pieces in the run, never in front of a window whose sill it would reach, never on another
    item (``WORKTOP_ITEM_GAP_M`` apart)."""
    c, rot, w, d = _front_box(counter)
    r = math.radians(rot)
    px, py = float(item["center"][0]) - c[0], float(item["center"][1]) - c[1]
    lx, ly = math.cos(r) * px + math.sin(r) * py, -math.sin(r) * px + math.cos(r) * py
    iw, idp, ih = (float(v) for v in item["size"][:3])
    if abs(lx) + iw / 2.0 > w / 2.0 + 1e-6 or abs(ly) + idp / 2.0 > d / 2.0 + 1e-6:
        return "it would stand over the worktop's edge"
    x0, x1 = lx - iw / 2.0, lx + iw / 2.0
    for b0, b1, kind in worktop_blocks(counter, pieces):
        if x0 < b1 - 1e-6 and x1 > b0 + 1e-6:
            return {"hob": "on the hob or in its side gap", "sink": "on the sink or at its edge",
                    "tall": "against a tall piece of the run"}[kind]
    for w0, w1, sill in windows:
        if x0 < w1 + 0.05 and x1 > w0 - 0.05 and ih > sill - WORKTOP_WINDOW_CLEAR_M:
            return "in front of a window it would reach (its sill over the worktop)"
    for o in others:
        if o is item or o.get("host_id") != counter.get("id"):
            continue
        ox = math.cos(r) * (float(o["center"][0]) - c[0]) + math.sin(r) * (float(o["center"][1]) - c[1])
        if abs(ox - lx) < (float(o["size"][0]) + iw) / 2.0 + WORKTOP_ITEM_GAP_M - 1e-6:
            return f"on or against {o.get('type')} {o.get('id')}"
    return None


def kitchen_worktop_decor(building: dict, room: dict, pieces: list[dict], new_id, existing: list = ()) -> list[dict]:
    """The worktop dressing of a kitchen (any room with a kitchen run), modest (28 Oct 2026; module note above): the
    items of ``KITCHEN_DECOR_ORDER`` placed on the built counter runs of the room (no outline drawn inside another
    run: ``fit.nested_counters``) at their real sizes, each where it belongs (``KITCHEN_DECOR_ORDER``), every one
    passing ``worktop_item_ok``; at most one per ``WORKTOP_PER_M`` of free worktop and ``KITCHEN_DECOR_MAX`` in all.
    Hosted on the counter (``host_id``: the build rests them on the built worktop), ``added_by_ai`` by rule with the
    reason. None when the room takes no decor or already holds worktop items."""
    if room.get("room_type") in NO_DECOR_ROOM_TYPES or not room_takes_decor(room):
        return []
    have = [d for d in list(building.get("decor") or []) + list(existing) if d.get("room_id") == room["id"]
            and d.get("type") in KITCHEN_DECOR_TYPES]
    if have:
        return []
    from wenart.furniture import fit as FT
    nested = FT.nested_counters(dict(building, furniture=pieces))
    # a built counter run is a worktop whatever the reading's doubt (real06's drawn runs are unverified and built)
    counters = [p for p in pieces if p.get("type") in ("kitchen_counter", "kitchen_island") and piece_is_built(p)
                and p.get("footprint") and p.get("front_deg") is not None and p.get("id") not in nested]
    if not counters:
        return []
    windows = {p["id"]: worktop_windows(p, building, room) for p in counters}
    free_total = 0.0
    stretches = []
    for p in counters:
        c, rot, w, d = _front_box(p)
        spans = sorted(worktop_blocks(p, pieces))
        x, lo, hi = -w / 2.0 + WORKTOP_END_M, -w / 2.0 + WORKTOP_END_M, w / 2.0 - WORKTOP_END_M
        for b0, b1, _k in spans:
            if b0 > x:
                stretches.append((p, max(lo, x), min(hi, b0)))
            x = max(x, b1)
        if hi > x:
            stretches.append((p, x, hi))
    stretches = [s for s in stretches if s[2] - s[1] > 0.10]
    free_total = sum(s[2] - s[1] for s in stretches)
    budget = min(KITCHEN_DECOR_MAX, int(free_total / WORKTOP_PER_M))
    placed: list[dict] = []

    def anchors(p, kind):
        c, rot, w, d = _front_box(p)
        return [((b0 + b1) / 2.0) for b0, b1, k in worktop_blocks(p, pieces) if k == kind]

    def candidates(dtype):
        iw, idp, ih = KITCHEN_DECOR_SIZES[dtype]
        out = []
        for p, a, b in stretches:
            c, rot, w, d = _front_box(p)
            if b - a < iw - 1e-6 or d < idp + 0.06:
                continue
            island = p.get("type") == "kitchen_island"
            y = 0.0 if island else d / 2.0 - idp / 2.0 - WORKTOP_BACK_M
            if dtype == "fruit_bowl" and not island:
                y = d / 2.0 - idp / 2.0 - 0.08
            steps = max(1, int((b - a - iw) / 0.05))
            xs = sorted({round(a + iw / 2.0, 4), round(b - iw / 2.0, 4)}
                        | {round(a + iw / 2.0 + k * 0.05, 4) for k in range(steps + 1)})
            for x in xs:
                if x - iw / 2.0 < a - 1e-6 or x + iw / 2.0 > b + 1e-6:
                    continue
                world = G.rotate_point((c[0] + x, c[1] + y), rot, c)
                item = {"type": dtype, "center": [round(world[0], 4), round(world[1], 4)], "rotation_deg": round(rot, 3),
                        "size": [iw, idp, ih], "host_id": p["id"]}
                if worktop_item_ok(item, p, pieces, windows[p["id"]], placed) is not None:
                    continue
                hob, sink = anchors(p, "hob"), anchors(p, "sink")
                end = min(abs(x - iw / 2.0 - a), abs(b - x - iw / 2.0))
                run_end = abs(x - iw / 2.0 - (-w / 2.0 + WORKTOP_END_M)) < 1e-3 or \
                    abs(x + iw / 2.0 - (w / 2.0 - WORKTOP_END_M)) < 1e-3
                rank = 0 if run_end else (1 if end < 1e-3 else 2)
                if dtype in ("microwave", "coffee_machine", "toaster"):
                    score = (rank, -min([abs(x - h) for h in hob] or [9.0]))
                elif dtype == "kettle":
                    score = (min([abs(x - s) for s in sink] or [5.0 + abs(x)]), 0)
                elif dtype in ("utensil_pot", "chopping_board"):
                    score = (min([abs(x - h) for h in hob] or [5.0 + abs(x)]), 0)
                else:
                    score = (0 if island else 1, -min(x - iw / 2.0 - a, b - x - iw / 2.0))
                out.append((score, str(p["id"]), x, item))
        out.sort(key=lambda t: (t[0], t[1], t[2]))
        return out

    reasons = {"microwave": "a countertop microwave at the end of the run, against the wall or the corner",
               "coffee_machine": "a coffee machine at the end of the run", "toaster": "a toaster at the end of the run",
               "kettle": "a kettle by the sink", "utensil_pot": "a utensil pot beside the hob, off its side gap",
               "chopping_board": "a chopping board beside the hob, off its side gap",
               "fruit_bowl": "a fruit bowl on a free stretch of the worktop"}
    order = list(KITCHEN_DECOR_ORDER)
    for dtype in order:
        if len(placed) >= budget:
            break
        got = candidates(dtype)
        if not got and dtype == "coffee_machine":
            got = candidates("toaster")
            dtype = "toaster" if got else dtype
        if not got:
            continue
        _s, _pid, _x, item = got[0]
        item.update({"id": new_id(room["level_id"]), "kind": "decor", "level_id": room["level_id"],
                     "room_id": room["id"], "asset": None, "source": "added_by_ai", "method": "rule",
                     "reason": f"kitchen worktop dressing (28 Oct 2026): {reasons[dtype]}; on the worktop of "
                               f"{item['host_id']}, off the hob, the sink and the windows (code checks)"})
        placed.append(item)
    return placed


def _large_item(item_id: str, room: dict, item: dict) -> dict:
    """A rug or wall art decor entry: hostless (``host_id`` None; its own element in the scene), the group in
    ``anchor_ids``, ``added_by_ai`` by rule."""
    out = {"id": item_id, "kind": "decor", "type": item["type"], "level_id": room["level_id"], "room_id": room["id"],
           "center": item["center"], "rotation_deg": item["rotation_deg"], "size": item["size"], "asset": None,
           "host_id": None, "anchor_ids": item["anchor_ids"], "source": "added_by_ai", "method": "rule",
           "reason": item["reason"]}
    for key in ("wall_point", "wall_id", "gap_m", "bottom_m", "max_height_m"):
        if key in item:
            out[key] = item[key]
    return out


# --------------------------------------------------------------------------
# Milestone 10: partners (same_as rooms, second twins) take a copy of their partner's decor
# --------------------------------------------------------------------------

PARTNER_WINDOW_TOL_M = 0.15       # a mapped window centre within this of the room's own window
PARTNER_PIECE_TOL_M = 0.10        # a mapped piece centre within this of the room's own piece of the same type


def partner_rooms(building: dict) -> dict[str, tuple[str, str]]:
    """``{room id: (partner room id, "same_as" | "twin")}`` of the rooms that take their partner's decor:
    ``same_as`` rooms always, second twins (``twin_of``) with ``render.twin_rooms: one`` (the building's stored
    brief or the default, ``wenart.views.brief_value``)."""
    from wenart import views as VW

    twin_rooms, _assumed = VW.brief_value(building, None, "render.twin_rooms")
    ids = {r["id"] for r in building.get("rooms") or []}
    out = {}
    for room in building.get("rooms") or []:
        if room.get("same_as") in ids:
            out[room["id"]] = (room["same_as"], "same_as")
        elif room.get("twin_of") in ids and str(twin_rooms or "one") == "one":
            out[room["id"]] = (room["twin_of"], "twin")
    return out


def copy_targets(building: dict) -> tuple[dict, list[str]]:
    """``({room id: (partner id, kind, transform)}, notes)``: the partner rooms whose map onto the room is verified
    (``complete.partner_transform``); a room whose partner does not map stays to be decorated itself (noted), and
    so does the first room of a loop of partners (noted)."""
    from wenart.furniture import complete as CP

    rooms = {r["id"]: r for r in building.get("rooms") or []}
    out, notes = {}, []
    for rid, (pid, kind) in sorted(partner_rooms(building).items()):
        t, why = CP.partner_transform(rooms[rid], rooms[pid], "same_as" if kind == "same_as" else "twin", building)
        if t is None:
            notes.append(f"{rid}: its {kind} partner {pid} cannot be mapped ({why}); decorated itself")
            continue
        out[rid] = (pid, kind, t)
    # A loop of partners (two rooms each the twin of the other) has no room to copy from: its first room in building
    # order is decorated itself, the others copy from it (as wenart.furniture.complete asks one room of a cycle).
    for room in building.get("rooms") or []:
        path = [room["id"]]
        while path[-1] in out and out[path[-1]][0] not in path:
            path.append(out[path[-1]][0])
        if path[-1] in out and out[path[-1]][0] == room["id"]:
            del out[room["id"]]
            notes.append(f"{room['id']}: its partners loop back to it ({' -> '.join(path + [room['id']])}); "
                         "decorated itself")
    return out, notes


def _piece_map(building: dict, room: dict, partner_id: str, t) -> dict[str, str]:
    """Partner piece id -> the room's piece id: a piece copied from it (``mirrored_from``), else the room's piece of the
    same type whose centre the map puts the partner's within ``PARTNER_PIECE_TOL_M``."""
    mine = [f for f in building.get("furniture") or [] if f.get("room_id") == room["id"]]
    out = {}
    for f in building.get("furniture") or []:
        if f.get("room_id") != partner_id:
            continue
        copied = next((m for m in mine if m.get("mirrored_from") == f["id"]), None)
        if copied is None:
            c = t.point(f["footprint"]["center"])
            near = [(G.distance(c, m["footprint"]["center"]), m["id"]) for m in mine if m["type"] == f["type"]]
            near = [x for x in near if x[0] <= PARTNER_PIECE_TOL_M]
            copied = {"id": min(near)[1]} if near else None
        if copied is not None:
            out[f["id"]] = copied["id"]
    return out


def _window_map(building: dict, room: dict, t) -> dict[str, str]:
    windows = [o for o in building.get("openings") or [] if o.get("level_id") == room["level_id"]
               and o.get("type") == "window"]
    out = {}
    for o in building.get("openings") or []:
        if o.get("type") != "window":
            continue
        c = t.point(o["center"])
        near = [(G.distance(c, w["center"]), w["id"]) for w in windows]
        near = [x for x in near if x[0] <= PARTNER_WINDOW_TOL_M]
        if near:
            out[o["id"]] = min(near)[1]
    return out


def _copy_order(targets: dict) -> list[str]:
    """The target rooms (``copy_targets``) in the order they copy, in rounds: a room whose partner is a target itself
    (a chain: real02's r_L-1b_banyo_2 is ``same_as`` r_L-1_banyo_2, the twin of r_L-1_banyo) after that partner, in
    id order per round. A loop left (``copy_targets`` breaks them) goes last as it is."""
    order, todo = [], sorted(targets)
    while todo:
        ready = [rid for rid in todo if targets[rid][0] not in todo] or todo
        order += ready
        todo = [rid for rid in todo if rid not in ready]
    return order


def copy_partner_decor(building: dict, items: list[dict], targets: dict, new_id) -> tuple[list[dict], list[str]]:
    """The decor of every target room (``copy_targets``) copied from its partner's ``items`` (``mirrored_from`` =
    the partner item's id; centre, wall point and rotation through the map; host, anchors and window mapped,
    ``wall_id`` the room's nearest wall) and the notes of the items that could not be copied. The rooms copy in
    ``_copy_order``: a room whose partner is a target itself copies the partner's copy.
    Fix round after P6a (22 Oct 2026): a curtain or blind whose top would reach closer than
    ``WINDOW_DECOR_CEILING_CLEAR_M`` to the sloped ceiling over the copy (``ceiling_over``; ``COPY_HEIGHT_TOL_M``
    for the rounding) is not copied (a note), so a roof that is not mirrored never takes window decor through it."""
    rooms = {r["id"]: r for r in building.get("rooms") or []}
    out, notes = [], []
    planes_of: dict[str, list] = {}
    for rid in _copy_order(targets):
        pid, kind, t = targets[rid]
        room = rooms[rid]
        pieces = _piece_map(building, room, pid, t)
        windows = _window_map(building, room, t)
        own = {tuple(sorted(d.get("anchor_ids") or [])) for d in items if d.get("room_id") == rid
               and (d.get("group") or {}).get("role") == SOLVER_RUG_ROLE}
        for item in items + out:                         # + the copies made so far (a chain's partner)
            if item.get("room_id") != pid:
                continue
            new = json.loads(json.dumps(item))
            missing = []
            if item.get("host_id") is not None:
                new["host_id"] = pieces.get(item["host_id"])
                if new["host_id"] is None:
                    missing.append(f"host {item['host_id']}")
            if item.get("anchor_ids"):
                new["anchor_ids"] = [pieces.get(a) for a in item["anchor_ids"]]
                if None in new["anchor_ids"]:
                    missing.append(f"anchors {item['anchor_ids']}")
            if item.get("window_id"):
                new["window_id"] = windows.get(item["window_id"])
                if new["window_id"] is None:
                    missing.append(f"window {item['window_id']}")
            if missing:
                notes.append(f"{rid}: {item['type']} {item['id']} of {pid} not copied (no counterpart for "
                             f"{', '.join(missing)})")
                continue
            if item.get("type") == "rug" and own and tuple(sorted(new.get("anchor_ids") or [])) in own:
                # Milestone 13: the room's own solver rug under those pieces stays; the partner's is not copied
                notes.append(f"{rid}: rug {item['id']} of {pid} not copied (the group solver laid the room's own "
                             f"rug under {', '.join(new['anchor_ids'])})")
                continue
            g = new.get("group")
            if isinstance(g, dict):
                # A solver rug's group is the room's own group, as for the copied furniture (complete._map_group):
                # the copy kept the partner's group id (review of the CPU pre-flight of 16 Oct 2026, real04: the rugs
                # of r_L-1b_oda_2 named r_L-1b_oda.sleeping_double while their bed is in r_L-1b_oda_2.sleeping_double).
                gid = str(g.get("group_id") or "")
                if gid.startswith(pid + "."):
                    g["group_id"] = rid + gid[len(pid):]
                if g.get("anchor_id") is not None:
                    g["anchor_id"] = pieces.get(g["anchor_id"])
            c = t.point(item["center"][:2])
            new["center"] = [round(c[0], 3), round(c[1], 3)] + list(item["center"][2:])
            new["rotation_deg"] = round(t.rotation(float(item.get("rotation_deg") or 0.0)), 3)
            if item.get("wall_point"):
                wp = t.point(item["wall_point"])
                new["wall_point"] = [round(wp[0], 3), round(wp[1], 3)]
                new["wall_id"] = _nearest_wall_id(building, room["level_id"], wp)
            if item.get("type") in WINDOW_DECOR_TYPES and len(new["center"]) > 2 and len(new.get("size") or []) > 2:
                lid = room["level_id"]           # fix round after P6a: window decor stays under a sloped ceiling
                if lid not in planes_of:
                    planes_of[lid] = ceiling_planes(building, lid)
                if planes_of[lid]:
                    top = float(new["center"][2]) + float(new["size"][2])
                    here = ceiling_over(building, lid, new["center"][:2], new["size"][:2], new["rotation_deg"],
                                        planes=planes_of[lid])
                    if top > here - WINDOW_DECOR_CEILING_CLEAR_M + COPY_HEIGHT_TOL_M:
                        notes.append(f"{rid}: {item['type']} {item['id']} of {pid} not copied (its top {top:.2f} m "
                                     f"reaches the sloped ceiling here, {here:.2f} m over it)")
                        continue
            new.update(id=new_id(room["level_id"]), level_id=room["level_id"], room_id=rid, mirrored_from=item["id"],
                       reason=f"copied from {item['id']} of {pid} ({'mirrored twin' if kind == 'twin' else 'same as'})")
            new.pop("host_frame", None)              # Milestone 12: re-attached in the room's own host's frame
            out.append(new)
    return out, notes


def decor_report(building: dict, rows: list[dict]) -> str:
    lines = [f"# Decor: {building['project']['id']}", "",
             f"{len(building.get('decor', []))} decor pieces (rule-based, `added_by_ai`, max {MAX_DECOR_M} m except "
             "rugs and wall art). "
             "Cushions on sofas and beds, books on shelves and desks, one plant per living room or bedroom in a "
             "free corner (never on a door approach, a swing or a 0.9 m walkway). Rugs under the sofa + coffee "
             "table group, the lower two thirds of a double bed and dining tables (+ 0.6 m for the chairs), group "
             f"+ {RUG_MARGIN_M} m, inside the room shrunk by {RUG_ROOM_INSET_M} m, never under a door swing; one wall "
             f"art piece per living room, bedroom or dining room above a sofa, bed or dresser ({WALL_ART_GAP_M} m "
             f"above its top, at most {WALL_ART_WIDTH_SHARE} x its width, never over a door or window; built only "
             "from a library model).", "",
             "| Room | Cushions | Books | Plant | Rugs | Wall art | Note |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['label']} ({r['room_id']}) | {r.get('cushions', '-')} | {r.get('books', '-')} | "
                     f"{r.get('plant', '-')} | {r.get('rugs', '-')} | {r.get('wall_art', '-')} | {r.get('note', '')} |")
    return "\n".join(lines) + "\n"


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="rule-based decor (cushions, books, plants, rugs, wall art) on a "
                                                 "building JSON")
    parser.add_argument("building", help="building JSON (furnished or not)")
    parser.add_argument("--out", required=True, help="building JSON with the decor list")
    parser.add_argument("--report", help="markdown report (default: decor_report.md next to --out)")
    args = parser.parse_args(argv)
    building = B.load(args.building)
    out, rows = add_decor(building)
    out_path = Path(args.out)
    B.save(out, out_path)
    report = Path(args.report) if args.report else out_path.parent / "decor_report.md"
    report.write_text(decor_report(out, rows), encoding="utf-8")
    print(f"decor: {len(out['decor'])} pieces -> {out_path} (report {report})")
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --------------------------------------------------------------------------
# Milestone 12 (docs/milestone12.md §4.7, D13; contract §13.2, §13.3; track S): decor in its host's frame
# --------------------------------------------------------------------------

# Where an item rests (``decor[].host_frame.support``): on a seat, a mattress, against a seat back or a headboard,
# on a top, a shelf board, the floor, a wall or the ceiling. The rules live in ``wenart.blender.rest`` (pure numpy:
# the scene builder and the scene checks read them inside Blender, whose Python has no shapely) and are the same here.
from wenart.blender.rest import (BED_HOSTS, CEILING_SUPPORT_TYPES, LYING_SEAT_HOSTS, SEAT_BACK_HOSTS,  # noqa: E402
                                 SHELF_HOSTS, SUPPORTS, TOP_HOST_TYPES, WALL_SUPPORT_TYPES, support_fits, support_of)

LEAN_DEG = 12.0                   # a cushion leans 10-15 degrees on its back (§4.7)
DEFAULT_SHELF = 1                 # books on the second board from the bottom (the Milestone 4 rest height)
WALL_FOLLOW_GAP_M = 0.35          # wall art follows its piece while the piece's back stays this close to the wall
THROW_BED_WIDTH_SHARE = 0.95      # = decor_ai: a throw across a bed's foot is this share of the bed's width
NOT_BUILT_ASSET_METHODS: tuple[str, ...] = ("none",)   # fit.py: a library gap (no audited model, not built)


def piece_is_built(piece: Optional[dict]) -> bool:
    """A piece the scene builds: ``build`` not false, typed (no ``unknown``: never a grey box, §4.1) and not a
    library gap left unbuilt by the fit (``asset.method == "none"``, §4.8)."""
    if not piece or piece.get("build", True) is False or piece.get("type") == "unknown":
        return False
    return (piece.get("asset") or {}).get("method") not in NOT_BUILT_ASSET_METHODS


def takes_cushions(host: dict) -> bool:
    """A seat or bed takes decor cushions unless its model already has them (the audit's ``has_cushions`` on a
    seat, ``has_pillows`` / ``has_cushions`` on a bed: §4.7, no duplicates)."""
    from wenart.blender.rest import own_cushions    # the build checks the final model with the same rule

    return not own_cushions(host)


def _frame_ref(item: dict, pieces: dict) -> tuple[Optional[dict], Optional[str]]:
    """``(the piece whose frame the item lives in, how)``: its host, else the first anchor (a rug under its group, a
    picture over its piece, a pendant over its table), else None (a plant in a corner, a curtain at its window)."""
    if item.get("host_id"):
        return pieces.get(item["host_id"]), "host"
    anchors = [a for a in item.get("anchor_ids") or [] if a]
    if anchors:
        return pieces.get(anchors[0]), "anchor"
    return None, None


def host_frame_of(item: dict, ref: Optional[dict], how: Optional[str] = "host") -> dict:
    """The host frame of a decor item in the frame of ``ref`` (its host or first anchor) from its world position:
    ``support``, ``u`` / ``v`` = its centre as shares of the host footprint (-0.5 .. +0.5 on the host; u along the
    width, v along the depth, +v = back), ``turn_deg`` = its rotation minus the host's, ``lean_deg`` (cushions
    against a back or a headboard), ``shelf`` (books on a shelf: the board index) and, for an anchor,
    ``anchor_id``. Wall items keep ``u`` along their wall (shares of the piece's width) and ``wall_offset`` (the
    centre in front of the wall point). An item without a frame piece has only its support (it stays where it is)."""
    dtype = item.get("type")
    support = support_of(dtype, ref.get("type") if (ref is not None and how == "host") else None)
    frame: dict = {"support": support}
    if ref is None:
        return frame
    fp = ref["footprint"]
    w, d = (float(v) for v in fp["size"][:2])
    rot = float(fp["rotation_deg"])
    if how == "anchor":
        frame["anchor_id"] = ref["id"]
    if support == "wall" and item.get("wall_point"):
        r = math.radians(float(item.get("rotation_deg") or 0.0))
        wx, wy = (float(v) for v in item["wall_point"][:2])
        along = (wx - float(fp["center"][0])) * math.cos(r) + (wy - float(fp["center"][1])) * math.sin(r)
        frame["u"] = round(along / w, 4) if w > 1e-9 else 0.0
        frame["wall_offset"] = [round(float(item["center"][0]) - wx, 4), round(float(item["center"][1]) - wy, 4)]
        return frame
    p = G.rotate_point((float(item["center"][0]), float(item["center"][1])), -rot,
                       (float(fp["center"][0]), float(fp["center"][1])))
    frame["u"] = round((p[0] - float(fp["center"][0])) / w, 4) if w > 1e-9 else 0.0
    frame["v"] = round((p[1] - float(fp["center"][1])) / d, 4) if d > 1e-9 else 0.0
    frame["turn_deg"] = round(G.normalise_angle(float(item.get("rotation_deg") or rot) - rot), 3)
    frame["lean_deg"] = LEAN_DEG if (dtype == "cushion" and support in ("back", "headboard")) else 0.0
    frame["shelf"] = DEFAULT_SHELF if support == "shelf" else None
    return frame


def attach_host_frames(building: dict) -> dict:
    """In place: a ``host_frame`` on every decor item that has none (from its current world position); returns
    the building. The decor stages call it once their items are placed."""
    pieces = {p["id"]: p for p in building.get("furniture") or []}
    for item in building.get("decor") or []:
        if isinstance(item.get("host_frame"), dict) and item["host_frame"].get("support"):
            continue
        ref, how = _frame_ref(item, pieces)
        item["host_frame"] = host_frame_of(item, ref, how)
    return building


def _world_of(frame: dict, ref: dict) -> tuple[tuple[float, float], float]:
    fp = ref["footprint"]
    w, d = (float(v) for v in fp["size"][:2])
    rot = float(fp["rotation_deg"])
    c = (float(fp["center"][0]), float(fp["center"][1]))
    p = G.rotate_point((c[0] + float(frame.get("u") or 0.0) * w, c[1] + float(frame.get("v") or 0.0) * d), rot, c)
    return (p[0], p[1]), G.normalise_angle(rot + float(frame.get("turn_deg") or 0.0))


def _follow_wall(item: dict, frame: dict, ref: dict) -> Optional[str]:
    """In place: a wall item slides along its wall with its piece (``u`` of the piece's width from the foot of the
    piece's centre on the wall line); returns why it cannot follow (the piece turned away from the wall or left
    it), None when it followed."""
    fp = ref["footprint"]
    r = math.radians(float(item.get("rotation_deg") or 0.0))
    ux, uy = math.cos(r), math.sin(r)                         # along the wall
    nx, ny = math.sin(r), -math.cos(r)                        # into the room (local -Y)
    wx, wy = (float(v) for v in item["wall_point"][:2])
    cx, cy = (float(v) for v in fp["center"][:2])
    if abs((G.normalise_angle(float(fp["rotation_deg"]) - math.degrees(r)) + 180.0) % 360.0 - 180.0) > 10.0:
        return "its piece no longer stands with its back to this wall"
    back = (float(fp["size"][1]) / 2.0)
    dist = (cx - wx) * nx + (cy - wy) * ny - back             # the piece's back edge in front of the wall face
    if not -0.05 <= dist <= WALL_FOLLOW_GAP_M:
        return f"its piece's back is {dist:.2f} m from the wall (more than {WALL_FOLLOW_GAP_M} m)"
    along_c = (cx - wx) * ux + (cy - wy) * uy
    shift = along_c + float(frame.get("u") or 0.0) * float(fp["size"][0])
    new_wp = (wx + ux * shift, wy + uy * shift)
    off = frame.get("wall_offset") or [float(item["center"][0]) - wx, float(item["center"][1]) - wy]
    item["wall_point"] = [round(new_wp[0], 3), round(new_wp[1], 3)]
    item["center"] = [round(new_wp[0] + float(off[0]), 3), round(new_wp[1] + float(off[1]), 3)] + \
        list(item.get("center", [])[2:])
    return None


def _drop(item: dict, reason: str) -> dict:
    return {"id": item.get("id"), "type": item.get("type"), "host_id": item.get("host_id"),
            "anchor_ids": list(item.get("anchor_ids") or []), "room_id": item.get("room_id"), "reason": reason}


def sync_to_hosts(building: dict) -> dict:
    """A new building whose decor follows its hosts: every decor item with ``host`` (host frame) gets its world
    ``center`` / ``rotation_deg`` recomputed from its host piece; decor whose host is gone or not built is dropped
    (listed in ``decor_dropped``). Called after every accepted agent edit and by ``agent apply``.

    Milestone 12 (§4.7, fixes B3): an item without a ``host_frame`` gets one from its current position first
    (``attach_host_frames``); hosted items take the host's room and level, and a throw across a bed's foot its
    width (``THROW_BED_WIDTH_SHARE``); items on a top, a seat or a mattress are never wider or deeper than the host.
    Anchored items follow their first anchor: a rug and a pendant in its frame, wall art along its wall while the
    piece keeps its back to it. Dropped (with the reason): the host gone, not built (``piece_is_built``) or retyped
    to a type without the item's support; every anchor of a rug, picture or pendant gone; wall art whose piece left
    its wall. Items without a frame piece (corner plants, curtains, room-centre lights) stay. Deterministic and
    idempotent (sync of a synced building changes nothing)."""
    out = copy.deepcopy(building)
    attach_host_frames(out)
    pieces = {p["id"]: p for p in out.get("furniture") or []}
    kept, dropped = [], []
    for item in out.get("decor") or []:
        frame = item["host_frame"]
        if item.get("host_id"):
            host = pieces.get(item["host_id"])
            if host is None:
                dropped.append(_drop(item, f"its host {item['host_id']} is gone"))
                continue
            if not piece_is_built(host):
                dropped.append(_drop(item, f"its host {host['id']} is not built"))
                continue
            if not support_fits(frame.get("support"), host.get("type")):
                dropped.append(_drop(item, f"its host {host['id']} is now a {host.get('type')} without a "
                                           f"{frame.get('support')}"))
                continue
            (x, y), rot = _world_of(frame, host)
            item["center"] = [round(x, 3), round(y, 3)] + list(item.get("center", [])[2:])
            item["rotation_deg"] = round(rot, 3)
            item["room_id"], item["level_id"] = host.get("room_id"), host.get("level_id")
            size = list(item.get("size") or [])
            hw, hd = (float(v) for v in host["footprint"]["size"][:2])
            if size and frame.get("support") == "mattress" and item.get("type") == "throw":
                size[0] = round(THROW_BED_WIDTH_SHARE * hw, 3)
            elif size and frame.get("support") in ("top", "seat", "mattress"):
                size[0] = round(min(float(size[0]), hw), 3)
                if len(size) > 1:
                    size[1] = round(min(float(size[1]), hd), 3)
            item["size"] = size
            kept.append(item)
            continue
        anchors = [a for a in item.get("anchor_ids") or [] if a]
        if anchors:
            live = [pieces[a] for a in anchors if a in pieces and piece_is_built(pieces[a])]
            if not live:
                dropped.append(_drop(item, f"its pieces {', '.join(anchors)} are gone or not built"))
                continue
            ref = pieces.get(frame.get("anchor_id") or anchors[0])
            if ref is None or not piece_is_built(ref):
                kept.append(item)                              # its first piece left: it stays where it is
                continue
            if frame.get("support") == "wall" and item.get("wall_point"):
                why = _follow_wall(item, frame, ref)
                if why is not None:
                    dropped.append(_drop(item, why))
                    continue
            elif frame.get("support") in ("floor", "ceiling") and "u" in frame:
                (x, y), rot = _world_of(frame, ref)
                item["center"] = [round(x, 3), round(y, 3)] + list(item.get("center", [])[2:])
                if frame.get("support") == "floor":
                    item["rotation_deg"] = round(rot, 3)
        kept.append(item)
    out["decor"] = kept
    if dropped or building.get("decor_dropped"):
        out["decor_dropped"] = list(building.get("decor_dropped") or []) + dropped
    return out
