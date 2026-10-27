"""Camera search: score candidate cameras with a coarse ray caster and pick
the best diverse views per room (docs/milestone6.md §1.3, §4).

What: ``plan_level(building, level_id)`` returns the camera plans of every
room of a level for the camera policy ``search`` (``cameras.plan_cameras``
calls it); the plans have the same fields as the M5 plans plus ``shift_x``,
``shift_y``, ``policy``, ``score`` and ``search_seconds``.

Why: the M5 rules (three fixed cameras per room at 1.4 m looking 0.1 m down)
framed bare walls in 17 of 87 views, were blocked in 12 and showed less than
1 % floor in 52. A score computed from what a camera would see picks views
that show the furniture, some floor and a door or window, with straight
verticals (pitch 0, lens shift instead of tilt).

How:

- Model of a room (``RoomModel``): the room prism (floor at the level
  elevation, ceiling at the level's ceiling height, every polygon edge a
  vertical wall; fix round after P3, 16-17 Oct 2026: also every wall of the
  level standing inside the outline, ``inner_walls``, with both faces, its
  end faces and its openings, and as an obstacle of the camera points,
  ``inner_wall_rects``), the door and window rectangles on its edges
  (``cameras.room_openings`` and ``shell.opening_vertical``; a plain
  opening is labelled ``opening``, it is neither wall nor element) and the
  room's furniture boxes (``parametric.piece_bbox`` turned by the footprint
  rotation, standing on the floor; decor is ignored (but free-standing floor decor keeps the camera points
  away: ``floor_decor_rects``, pod P5), and so are pieces with
  ``build: false``: drawn symbols the scene does not build, ``shown_pieces``).
  A stair (fixed equipment, ``parametric.SHELL_TYPES``) is not its box but
  the convex parts ``shell.build_stairs`` builds (``shell.plan_stairs`` /
  ``parametric.stair_parts``: step prisms on the sloped waist, riser plates,
  landing slab, rails), so the space under the upper flight and the landing
  is open as in the scene (review dwgblender-2: the 3.17 m box hid the
  walls behind the flights and the search picked hall views without the
  stair). The ceiling opening over the stair stays closed in the model.
  A piece with a back (beds, chairs, sofas, armchairs, toilets:
  ``PROFILES``) is not one box at its full height but its height profile
  (``piece_profile``): the low part (mattress, seat, bowl), the sofa arms
  and the back slab (headboard, chair or sofa back, cistern) on the rear
  edge, read from the parts ``parametric.build_parts`` builds for the
  piece (back = local +Y, the side opposite the front, as the scene builds
  both parametric meshes and library assets); the back rises to the piece's
  ``piece_bbox`` height (a library asset's fitted box). The full-height box
  over the whole footprint loomed into the frame where the real piece is a
  0.5 m mattress or a 0.45 m seat (pod run 20261003-205431: a bed beside
  the camera at 0.35 of the frame, chairs at the frame edge whose seat was
  below the frame and back outside it, a toilet whose cistern was behind
  the camera; none of them in the render). The soft bedding of a
  parametric bed (duvet, pillows: up to 0.15 m above the mattress) is left
  out: for a parametric bed the model errs towards seeing less, not more.
  A library asset's real seat or mattress is not known beyond its fitted
  box; the builder's height stands for it, except for a library toilet:
  its bowl is the type's 0.4 m (``proxies.PROXY_HEIGHTS``), because an
  added toilet's JSON height is its 0.8 m cistern top
  (``furniture.schemas.HEIGHTS``), which the builder would read as the
  bowl (pod F2, synthetic-03: a 0.8 m phantom bowl beside two cameras
  whose renders show no toilet).
  Door leaves need no part of their own: the scene builder builds every
  leaf closed inside its frame (``shell.build_openings``, checked by
  tests/test_blender_build.py), which the door rectangle on the wall is.
  Pure numpy, no Blender, no shapely: build.py runs it inside Blender's
  Python.
- Rays: a 64 x 36 grid over the 1920 x 1080 frame of the room's lens on a
  36 mm sensor (horizontal sensor fit) with the lens shift of §1.3
  (``a = (col + 0.5 - W/2 + shift_x W) / f``, ``b = -(row + 0.5 - H/2 -
  shift_y W) / f``, direction ``forward + a right + b up``). The ray
  parameter is the planar depth along the view axis, the quantity Cycles
  writes into its Z pass and the GPU test reads from ``depth_mm`` (the
  research prototype used the ray length, up to 1.34 x larger in the
  corners of the frame).
- Per candidate: the share of rays of every label (each piece, each door or
  window, floor, ceiling, wall), whether a piece touches the frame border,
  the share of rays nearer than 0.9 m, the median depth of the wall rays and
  the nearest depth.
  ``score_terms`` turns them into the §4.1 score; every constant is in
  ``SCORE``.
- Candidates: free points (``geom2d.point_is_free`` with the wall 0.3 m /
  obstacle 0.2 m clearances of the M5 cameras) on a 0.5 m grid plus two
  points per convex polygon corner (0.45 m and 0.6 m in along the bisector),
  12 yaws (every 30 degrees, 0 = +X, counter-clockwise), height 1.25 m,
  pitch 0, ``shift_y = -0.10``. A room without a free point gets the M5
  fallback point with a warning, anchored at the room's inner point
  (``lighting.polylabel``, always inside the polygon; the centroid of an
  L-shaped room can lie in the notch): that point, or the nearest point
  clear of the tall boxes, or that point inside a box.
- Pick (``select_views``): views per room by the room area (3 from 6 m2,
  2 from 3 m2, else 1; Milestone 7: a room with nothing to show gets one
  view, and none below 2.5 m2, see below); a candidate is blocked when its
  near share is over 0.30, one element covers over 0.50 of the rays or its
  nearest surface is nearer than 0.12 m (planar; pod run F1: a camera at the
  fallback point in a stair well, a step side 0.08 m from the lens, under
  both share limits; ``is_blocked``); greedy by score among
  the unblocked candidates (ties: score, then x, y, yaw), a later pick must
  differ from every earlier one by at least 50 degrees of yaw or 1.0 m, and a
  pick below 0.5 x the room's best score is dropped (at least one view per
  room; 0.7 and the room's set since the fix round after the real06 run,
  below). A room with only blocked candidates gets its best one with the
  warning ``blocked unavoidable``. Deterministic: scores are rounded to
  1e-6 before sorting, so float noise never decides a tie.
- Output per plan: ``score`` = ``{total, furniture, openings, floor, depth,
  penalties, blocked, yaw_deg, shares}`` (the terms as they enter the total;
  ``shares`` are the model's ray shares), ``placement`` = the same as text,
  ``visible_openings``/``visible_furniture`` = the room's openings and
  pieces whose centre is inside the shifted frustum (as the M5 lists); a
  piece the view's model rays see is listed too (a long piece seen from the
  side can have its centre outside the frame),
  ``search_seconds`` = the wall time of the level's search (the same value
  on every plan of the level; ``level_search_seconds`` collects it).

Milestone 7 (docs/milestone7.md §6.2, user decision 8): a room whose
``RoomModel.pieces`` is empty (no furniture after layout and decor, decor
and ``build: false`` pieces not counted) gets ``EMPTY_ROOM_VIEWS`` = 1 view
whatever its area; such a room below ``MIN_EMPTY_ROOM_AREA_M2`` = 2.5 m2
gets none: ``plan_room`` returns no plan and ``rooms_without_view`` lists it
with the reason (the scene manifest's ``rooms_without_view``). The room
still gets its walls, floor, ceiling and openings; only the camera is left
out. ``room_view_count(room)`` without the building is the area rule alone
(the pre-layout estimate).

Milestone 8 (docs/milestone8.md §5, user decision 6): each room is searched
with its own lens (``cameras.room_lens``: 18 mm, 16 mm in a room narrower
than 2.2 m, or the brief's ``render.lens_mm``, the ``lens_mm`` argument of
``plan_level``): the ray grid, the frustum lists and the plan's
``lens_mm``/``lens_rule`` all use it. The score weights, caps, penalties,
candidate distances and ``shift_y`` are unchanged (the shift is a fraction
of the image width, so the horizon stays at the same image row, 32 % from
the top, whatever the lens; pitch 0 keeps the verticals straight). One
constant follows the lens: the near distance (``near_distance``: 0.9 m at
the 24 mm lens it was set with, times lens / 24: 0.675 m at 18 mm, 0.6 m
at 16 mm), because a surface d metres away through lens L is as large in
the frame as at d x 24 / L through 24 mm. Measured on the committed
buildings of real01 and synthetic-01..06 (159 views): with 0.9 m at every
lens the side walls of narrow rooms seen through 16 mm made 2 views
``blocked unavoidable`` (synthetic-02 bathroom, synthetic-05 hall) and cost
2 views (157 instead of the area rule's 159), the mean near share tripled
(0.03 -> 0.07); with the scaled distance no view is blocked and every room
gets its area-rule views.

Milestone 10 (docs/milestone10.md §3.2 item 2, §1.6b row 15): a room under the roof has the sloped ceiling of
its level's ``ceiling_planes`` in the ray model and keeps ``HEADROOM_M`` above its camera points
(``headroom_ok``); a wall-hung piece (``mount_bottom_m``, wall cabinets at 1.45 m; ``mount_bottom``) is no floor
obstacle for the camera points (one hung above the lens only since the fix round after the real06 run,
``floor_obstacle``) and its boxes hang from that height in the model and the frustum lists. A roof
terrace open to the sky (the level's ``open_rooms``: ``build.prepare``'s decided roof openings, where the shell
builds no ceiling) has no sloped ceiling in the model and no headroom filter (fix round after P5, below).

Fix round after P5 (22 Oct 2026; pod P5, real04):
- Roof terraces (the verifier's better fix of the look finding "terrace views regressed: 2 left of 6"). What: a room
  ``build.prepare`` decided open to the sky (``level["open_rooms"]``, ``sloped_level``) has no sloped ceiling in the
  ray model and no headroom filter; only those rooms, never by room type or by ``roof.openings`` (a terrace the brief
  keeps closed still has its sloped ceiling, which the shell builds). Scores and labels are unchanged. Why: the
  level's roof ``ceiling_planes`` were in the model and the headroom filter of every L1 room, the open terraces too;
  under P5's drawn 32.5 degree roof that fake ceiling stood 1.13 m above the terrace floor, only the inner corner
  passed ``headroom_ok`` and both terraces got one view framed on the parapet corner (scores 0.23 and 0.25, P3 had
  2.18-2.67). Simulated on P5's building: 3 views per terrace, 2.22-2.70, each terrace's table in frame. On P4a's
  real02 building the terrace views go from 1.20-1.77 (two views without furniture) to 2.19-2.79, every view with
  the terrace furniture; in a replay run only ``r_L1_teras_2`` is searched (2.19-2.72): ``r_L1_teras`` keeps its
  replayed ``cam_r_L1_teras_1`` (frozen set).
- The fallback camera (the verifier's better fix of "the camera blocked check never sees the built scene"). What: the
  free-standing and hanging decor under camera height + 0.2 m (``floor_decor_rects``) is a tall obstacle of the
  fallback as it already was of the free points, and under a sloped ceiling the fallback point must pass
  ``headroom_ok``: else the point clear of the walls, the tall pieces and that decor nearest the room's inner point
  that passes it, else the clear point with the most ceiling over it (``fallback_position``; the warning says so).
  Rooms with a flat ceiling keep their fallback point. Why: P5's ``cam_r_L1_banyo_1`` stood at the inner point
  (7.05, 10.87) with 0.15 m of ceiling over the lens, 1.5 cm above the decor ceiling light ``dec_L1_011`` (56 % of the
  frame, depth 0.05 m), which the fallback did not avoid. With that light no longer placed or built (the 2.0 m rule,
  ``wenart.furniture.decor.MIN_LIGHT_BOTTOM_M``) the camera moves to (7.02, 10.63), 1.55 m of ceiling, best view
  1.64; with the light still listed it moves to (7.02, 10.43).
- ``lens_clearance`` (warning only; the verifier's form of the analyst's check against the built scene): the build
  lists the searched interior cameras whose lens is nearer than ``SCORE["blocked_min_depth"]`` to a built box
  (``box3d`` of the scene manifest: furniture, decor, the rig's fixture meshes), naming the object; no camera is
  moved, replayed cameras are not checked.

Fix round after P6b (23 Oct 2026; pod P6b, real03 with the Milestone 11 cameras replayed; docs/milestone13.md §7: "A
frozen camera that ends up inside a newly built piece is moved by the free-floor rule and marked"):
``move_blocked_replayed(plans, building)`` (pure) moves a replayed interior camera that a piece of this build blocks
or contains. What: a replayed interior plan with a target is moved when, on ``building`` (the build passes
``build.camera_building``, the building the search sees), the model's one-element share of its frame is over
``SCORE["blocked_single"]`` or its lens stands inside a built piece's box (``piece_bbox`` on the footprint, a stair
excepted) at eye height. A piece the lens stands inside but looks out of (the box centre behind the lens and the side
of the box the view leaves through at most ``REPLAY_LOOKS_OUT_M`` ahead, ``lens_inside_pieces``) is left out of the
frame first: its face lies inside the fitted box, and the camera's near clip must hide it (P6b's yasama_4_3 stands
inside fridge f_L0_194's box, looks away from it, leaves the box 0.057 m ahead on its central ray and renders without
a fridge pixel; a lens deeper inside a piece, or beside a side it looks along, is moved). Fix round after P6b (23 Oct
2026), review: the clip is the one really used. ``looks_out_depth`` is the largest planar depth at which a frame ray
leaves the piece's box (the fitted box centred or back-aligned, ``furniture.fit_vertices``); when that depth plus
``REPLAY_CLIP_MARGIN_M`` passes the plan's clip (``cameras.CLIP_START_M``, 0.05 m, without its own) and the camera
stays, the plan gets ``clip_start`` just past it (``create_cameras`` honours it) and its warning says so; when the rest
of the view (the model without the piece) comes as near as that clip plus the margin, the clip would cut it too and
the lens counts as inside the piece (moved). Before, the camera stayed on the 0.05 m clip whatever the depth: the face
of P6b's fridge box lies 0.036-0.117 m ahead over yasama_4_3's frame (its render was clean only because the fit
pushed the shallower mesh 0.028 m back), and a lens 0.07 m behind a box face the mesh fills would render the inside of
the piece. yasama_4_3 now stays with ``clip_start`` 0.128 m (the rest of its view is 1.03 m away). The near share and
the nearest-depth rules of
``is_blocked`` never trigger a move (they flag yasama_4_2 and 6_2 over the 1.18 m counter run, whose renders are
good). The camera goes to the nearest free point of its room (``candidate_positions``) within
``REPLAY_MOVE_MAX_M`` whose view through the same frame (yaw, pitch, height, lens, shift, sensor) is not blocked
(``is_blocked``), a point distinct from the room's other cameras first (``select_views``: 50 degrees of yaw or 1 m);
the target moves with it, the name stays, ``source`` stays ``replayed`` (frozen for the agent) and ``replay`` says
``{"status": "moved", "position_old", "target_old", "moved_m", "trigger", "blocked_by", "blocked_by_type",
"share_old", "share", "reason"}``; the plan's warning says so. Without such a point the pose stays and the warning
gets ``BLOCKED_WARNING`` with the reason. Why: P6b typed the boxes at the end of real03's kitchen runs as 2.02 m
fridges (P4b had 0.9 m chairs there); four replayed views stood inside or against them (single share 0.54-1.0 in the
index pass, three black finals). On P6b's building yasama_2_2, 3_2, 5_2 and 6_1 move 0.88, 0.72, 0.68 and 0.66 m
(single share 0.11-0.15 after); nothing moves on P4b real03, P4a real02 or P6a real04 (no replayed camera).

Fix round after the real06 run (26 Oct 2026; pod run 20261026-183115-full, the AI judge's scores of real06): a view
shows the room's set, not its walls. Why: the judge scored real06's bathroom views 1-2 of 5 for framing a blank tiled
wall, a door or a corner while the toilet, shower and basins were out of the frame (``cam_r_L1_banyo_3`` 1/5,
``cam_r_L0_banyo_1``/``_2``, ``cam_r_L1_dus_2`` 2/5), a living room view whose centre was a bare column
(``cam_r_L0_salon_1``) and a bedroom view with its bed cropped. Causes, all general: openings, floor and depth gave up
to 3 points to any view, while a room's furniture term divided what one view shows by all its pieces (a bathroom view
of one fixture: 1.3 points); a door counted as an opening whatever its size; nothing looked at what stands in the
middle of the frame; edge_near treated the room's own shower 0.9 m away as a looming wardrobe side (-1.3); later views
were kept down to half the best score; and wall-hung pieces were no obstacles, so a camera stood over a basin. What:
- The room's anchors and set (``view_set``): the pieces of the room type's ``VIEW_ANCHOR_TYPES`` (bathroom: toilet,
  basin, shower, bathtub; living: sofas and armchairs; bedroom: beds; kitchen: counter runs, island, sink, stove,
  fridge; ...) and the group anchors (``group.role: anchor``), else the pieces of the room's highest type weight; the
  set adds the other members of their groups. Only pieces the model holds count (a stair's top end on the floor above is
  nothing in it); a room whose model holds no piece gets ``EMPTY_ROOM_VIEWS``. ``sofa_corner`` and ``bunk_bed`` weigh 3.
- A piece in the frame (``box_in_frame``, pure numpy): the fraction of its box's projected rectangle inside the frame
  (the box cut at 0.05 m ahead of the lens, so a piece beside the camera is outside), the frame share of that part and
  whether it reaches the frame's middle third. A piece is in the frame (``anchors_in``, ``set_in``) when that
  fraction is at least ``anchor_inside`` (0.6), its rays fill at least ``anchor_seen`` of ``anchor_fill`` x its
  in-frame box (not hidden) and it covers ``anchor_min_share`` (1 %); a piece no camera point of the room frames whole
  (``RoomModel.set_big``: a stair in a narrow hall, a basin in a 1.2 m WC) is in the frame when its in-frame part
  covers ``anchor_big_share`` (15 %) and reaches the middle third.
- Score: ``anchors`` = ``anchor_factor`` (3) x the set's weighted share shown (``set_cover``; a piece counts its
  in-frame fraction x its fill x min(1, share / ``anchor_full_share``), so a far, small piece counts less); penalties
  ``door`` (the door leaves' share over 0.10, x 4) and ``centre`` (``bare_centre``: the share of the frame's middle
  third of columns whose lowest surface above the floor is a wall or door leaf nearer than ``centre_near_m``, 4 m,
  over 0.30, x 3; in rooms with a set only); edge_near counts only the outside part of a set piece in the frame.
- Pick (``select_views``): no view without an anchor in the frame while one shows it (none at all: the best view only,
  with ``NO_ANCHOR_NOTE``: fewer views beat views of a wall); a later view is the one with the highest score + 3 x
  what it adds to the set (``cover_gain``), kept from ``DROP_BELOW_BEST`` = 0.7 x the best score (was 0.5); in a room
  under ``SMALL_ROOM_M2`` (8 m2) a later view must show a piece of the set no earlier view shows.
- Camera points (``floor_obstacle``): a piece hung below the lens (a wall-hung basin or toilet) keeps them away; one
  hung at or above it (a wall cabinet at 1.45 m) does not.
Plans carry ``score.anchors``, ``score.shares.anchors/door/centre``, ``anchors_in_frame`` and ``set_in_frame``.
Measured on real06's built building (all 12 rooms, both levels; the old pick reproduced exactly): 28 -> 24 views;
views of a room with anchors but none in the frame 5 -> 1 (the 3.1 m2 entrance: no view holds its shoe cabinet);
views with a bare centre (>= 0.9) 6 -> 0; door share over 0.10: 7 -> 1; set pieces in frame per view 1.04 -> 1.54;
rooms whose views together show their whole set 4 -> 7; search 8.3 -> 8.4 s (best of 3; within 6 %). The tests replay
real06's three bathrooms (tests/test_camsearch_views.py, tests/fixtures/camsearch_real06_bathrooms_20261026.json).
On the committed synthetic-01 / synthetic-03 buildings: 29 -> 20 and 43 -> 39 views, views without an anchor in the
frame 10 -> 0 and 16 -> 0, with a bare centre 3 -> 0 and 2 -> 0.

CLI (inspection only; the build calls ``plan_level``): ``python -m
wenart.blender.camsearch outputs/<p>/building_final.json --out cameras.json
[--report cameras.md] [--level L0] [--lens-mm 18]``.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path
from typing import Optional, Sequence

import numpy as np

from wenart import geometry as G
from wenart.blender import cameras, geom2d
from wenart.blender import parametric as P
from wenart.blender.parametric import obstacle_rect, piece_bbox
from wenart.blender.proxies import proxy_height
from wenart.blender.shell import opening_vertical, plan_stairs

POLICY = "search"

# Every constant of the score (docs/milestone6.md §4.1) in one table.
SCORE = {
    "grid": (64, 36),                 # rays across, rays down
    "furniture_factor": 4.0,          # 4 * furn
    "piece_cap": 0.25,                # min(c_k, 0.25) / 0.25
    "border_factor": 0.6,             # a piece touching the frame border counts 0.6
    "openings_cap": 0.12,             # min(open, 0.12) / 0.12
    "floor_cap": 0.25,                # min(floor, 0.25) / 0.25
    "depth_ref_m": 3.0,               # min(d_wall / 3 m, 1)
    "near_m": 0.9,                    # near = share of rays with depth < 0.9 m (at the 24 mm reference lens)
    "near_lens_mm": 24.0,             # Milestone 8: near_m scales with the lens (near_distance)
    # name: (factor, allowed share): score -= factor * max(0, share - allowed)
    "penalties": {
        "near": (3.0, 0.08),
        "max_single": (3.0, 0.40),
        "wall": (2.0, 0.55),
        "window": (2.0, 0.20),
        "ceiling": (1.0, 0.15),
        # Milestone 11 (docs/milestone11.md §1.3 M6): one element close to the lens at the frame edge (a door leaf
        # filling a quarter of the frame, a wardrobe side): its share of the rays nearer than edge_near_factor x the
        # near distance, for an element that touches the frame border
        "edge_near": (4.0, 0.05),
        # fix round after the real06 run (26 Oct 2026): the door leaves' share of the frame (a door filling half of
        # it), and the bare wall or door in the frame's centre below eye level (``centre``: a column, a blank wall)
        "door": (4.0, 0.10),
        "centre": (3.0, 0.30),
    },
    "edge_near_factor": 2.0,
    "blocked_near": 0.30,             # blocked: near > 0.30 ...
    "blocked_single": 0.50,           # ... or one piece / opening > 0.50 ...
    "blocked_min_depth": 0.12,        # ... or the nearest surface < 0.12 m (planar; pod run F1)
    "type_weight": {
        "bed": 3.0, "bed_double": 3.0, "bed_single": 3.0, "sofa": 3.0, "kitchen_counter": 3.0,
        "kitchen_island": 3.0,
        "sofa_corner": 3.0, "bunk_bed": 3.0,          # fix round after the real06 run: a corner sofa is a sofa
        "bathtub": 2.5,
        "table_dining": 2.0, "desk": 2.0, "toilet": 2.0, "washbasin": 2.0, "shower": 2.0, "sink_kitchen": 2.0,
        "wardrobe": 1.5, "armchair": 1.5, "stove": 1.5, "tv_unit": 1.5, "table_coffee": 1.5,
        "chair": 0.8,
    },
    "default_type_weight": 1.0,
    # fix round after the real06 run (26 Oct 2026): the room's set in the frame (``set_cover``): anchor_factor x
    # the weighted share of the set shown, a piece counting its in-frame box fraction times its visible fill
    "anchor_factor": 3.0,
    "anchor_fill": 0.5,               # a piece whose rays fill half of its in-frame box is not hidden (seen = 1)
    "anchor_full_share": 0.08,        # ... and it counts fully from this frame share on (less when far and small)
    "anchor_inside": 0.6,             # an anchor is in the frame when this much of its box is inside it ...
    "anchor_seen": 0.5,               # ... it is not hidden behind a wall or piece (seen >= 0.5) ...
    "anchor_min_share": 0.01,         # ... and it covers at least 1 % of the frame
    "anchor_big_share": 0.15,         # a piece no camera point frames whole (RoomModel.set_big: a stair in a narrow
                                      # hall) is in the frame when its part there covers this much, in the middle
    "centre_columns": (1.0 / 3.0, 2.0 / 3.0),   # the frame's centre: its middle third of columns ...
    "centre_near_m": 4.0,             # ... bare where a wall or door nearer than this stands on the floor (bare_centre)
}

# Candidates and the pick (§4.1).
CAMERA_HEIGHT = 1.25
SHIFT_X = 0.0
SHIFT_Y = -0.10
LENS_MM = cameras.LENS_MM            # 18 mm (Milestone 8; 16 mm in narrow rooms: cameras.room_lens)
SENSOR_MM = cameras.SENSOR_MM        # 36 mm
RESOLUTION = cameras.RESOLUTION      # 1920 x 1080
GRID_STEP = 0.5
CORNER_INSETS = (0.45, 0.6)
YAW_STEP_DEG = 30
TARGET_DISTANCE = 1.0
WALL_CLEARANCE = cameras.CAMERA_WALL_CLEARANCE          # 0.3 m
OBSTACLE_CLEARANCE = cameras.CAMERA_OBSTACLE_CLEARANCE  # 0.2 m
MIN_YAW_DIFF_DEG = 50.0
MIN_DISTANCE_M = 1.0
DROP_BELOW_BEST = 0.7                # fix round after the real06 run: 0.5 kept views of a wall next to a good one
VIEW_AREAS = ((6.0, 3), (3.0, 2))    # (minimum area m2, views); smaller rooms get 1 view
# Milestone 7 (§6.2): a room with nothing to show gets one view, none below this area (listed).
EMPTY_ROOM_VIEWS = 1
MIN_EMPTY_ROOM_AREA_M2 = 2.5
# Milestone 11 (docs/milestone11.md §1.3 M6): a piece at least this tall (a wardrobe) looms at the frame edge.
EDGE_TALL_M = 1.4
BLOCKED_WARNING = "blocked unavoidable"
SCORE_DECIMALS = 6                   # scores are rounded before sorting (deterministic ties)

# Fix round after the real06 run (26 Oct 2026; module docstring): the room's anchors by room type (the pieces a view
# of that room is about); a room without one of its type's anchors takes its group anchors, else its pieces of the
# highest type weight. The room's set is its anchors and the other members of their groups.
VIEW_ANCHOR_TYPES: dict[str, tuple[str, ...]] = {
    "bathroom": ("toilet", "washbasin", "shower", "bathtub"),
    "wc": ("toilet", "washbasin"),
    "kitchen": ("kitchen_counter", "kitchen_island", "sink_kitchen", "stove", "fridge"),
    "living": ("sofa", "sofa_corner", "armchair", "chaise"),
    "bedroom": ("bed", "bed_double", "bed_single", "bunk_bed", "crib"),
    "dining": ("table_dining",),
    "storage": ("wardrobe", "tall_cabinet"),
    "balcony": ("table_dining", "sofa", "armchair", "bench"),
}
SMALL_ROOM_M2 = 8.0                  # under this area a later view must show a piece of the set no earlier one does
NO_ANCHOR_NOTE = "no candidate view shows one of the room's anchors inside the frame; the best view is kept"

# Height profiles of the pieces with a back (``piece_profile``): per type, the roles of the parametric parts
# (``parametric.build_parts``) whose box is the low part (frame and mattress, seat, bowl and seat ring) and the
# roles kept as one box per part (the sofa arms); the parts of role ``PROFILE_BACK_ROLE`` (headboard, chair and
# sofa back, cistern) make the back slab on the rear edge. Every other type stays one box (``piece_bbox``).
PROFILE_BACK_ROLE = "back"
PROFILES: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    # Milestone 13 (T2 bed v2): the frame (role body) is a low box over the whole footprint and the mattress a
    # box of its own inside the frame's ledge, so a close-up of the foot corner sees the ledge the mesh shows.
    "bed": (("body",), ("mattress",)), "bed_single": (("body",), ("mattress",)),
    "bed_double": (("body",), ("mattress",)),
    "chair": (("top",), ()),
    "sofa": (("body", "cushion"), ("arm",)), "armchair": (("body", "cushion"), ("arm",)),
    "toilet": (("bowl", "seat"), ()),
}

# Ray labels; elements (doors, windows, pieces) follow from FIRST_ELEMENT.
NOTHING, FLOOR, CEILING, WALL, OPENING = 0, 1, 2, 3, 4
FIRST_ELEMENT = 5
_EPS_T = 1e-4
_EPS_S = 1e-6


# --------------------------------------------------------------------------
# View count, weights, the score formula
# --------------------------------------------------------------------------

def views_for_area(area_m2: float) -> int:
    """Views of a room by its area: 3 from 6 m2, 2 from 3 m2, else 1."""
    for minimum, n in VIEW_AREAS:
        if area_m2 >= minimum:
            return n
    return 1


def room_polygon(room: dict) -> list[tuple[float, float]]:
    poly = [(float(p[0]), float(p[1])) for p in room["polygon"]]
    if len(poly) > 1 and G.distance(poly[0], poly[-1]) < 1e-9:
        poly = poly[:-1]
    return poly


def shown_pieces(room: dict, building: dict) -> list[dict]:
    """The furniture a camera of ``room`` can show: the room's pieces after layout and decor, without
    decor (``kind: decor``) and without ``build: false`` pieces (drawn symbols both recognition passes
    called ``not_furniture``: kept in the building as obstacles, never built, docs/milestone7.md §3.3)."""
    from wenart.blender.shell import piece_built     # M12: unknown / no-model pieces are not built either

    return [f for f in building.get("furniture") or []
            if f.get("room_id") == room["id"] and f.get("kind") != "decor" and piece_built(f)]


# Fix round after P3 (16-17 Oct 2026): walls of the level standing inside a room outline.
INNER_WALL_MIN_M = 0.10      # metres of a wall's centre line inside the outline: the wall stands in the room
INNER_WALL_EDGE_M = 0.01     # a centre line this close to the outline runs along it (a bounding wall), not inside


def _segment_params(p, q, a, b) -> Optional[float]:
    """Parameter ``t`` (0..1) along ``p -> q`` where it crosses the segment ``a -> b``; None when parallel or apart."""
    dx, dy = q[0] - p[0], q[1] - p[1]
    ex, ey = b[0] - a[0], b[1] - a[1]
    den = dx * ey - dy * ex
    if abs(den) < 1e-12:
        return None
    t = ((a[0] - p[0]) * ey - (a[1] - p[1]) * ex) / den
    u = ((a[0] - p[0]) * dy - (a[1] - p[1]) * dx) / den
    if -1e-9 <= u <= 1.0 + 1e-9 and -1e-9 <= t <= 1.0 + 1e-9:
        return min(max(t, 0.0), 1.0)
    return None


_TRIM_CACHE: dict = {}


def _trimmed_walls(level_walls: list[dict]) -> dict:
    """``shell.trim_wall_overlaps`` of a level's walls, computed once per wall set (the search builds a room model per
    room and per scored camera: the trim is quadratic in the level's walls)."""
    from wenart.blender.shell import trim_wall_overlaps

    key = tuple((w["id"], tuple(float(v) for v in w["start"][:2]), tuple(float(v) for v in w["end"][:2]),
                 float(w["thickness"])) for w in level_walls)
    hit = _TRIM_CACHE.get(key)
    if hit is None:
        if len(_TRIM_CACHE) > 64:
            _TRIM_CACHE.clear()
        hit = _TRIM_CACHE[key] = trim_wall_overlaps(level_walls)
    return hit


def inner_walls(room: dict, building: dict, polygon=None) -> list[dict]:
    """Fix round after P3 (16-17 Oct 2026): the walls of the room's level whose centre line, after the shell's overlap
    trim (``shell.trim_wall_overlaps``, as the scene builds them), runs through the inside of the room outline for
    at least ``INNER_WALL_MIN_M``: ``[{"id", "thickness", "parts": [(start, end)], "faces": [(a, b)]}]`` with the
    inside parts of the centre line and their wall faces (both sides, and the end face where the wall itself ends).

    Why: the room model had one wall per outline edge only; a wall the shell builds inside the outline (real04: the
    unverified extra wall of the second plan region across a bedroom bay, real03: a 0.74 m stub in the living
    room) was absent, so the search planned and scored a view of a desk the wall hides (model share 0.088, nothing
    in the render). How: pure Python (build.py runs this inside Blender's Python): the crossings of the centre line
    with the outline split it, a part whose middle lies inside (more than ``INNER_WALL_EDGE_M`` from the outline)
    is inside."""
    polygon = list(polygon) if polygon is not None else room_polygon(room)
    n = len(polygon)
    level_walls = [w for w in building.get("walls") or [] if w.get("level_id") == room.get("level_id")
                   and w.get("start") is not None and w.get("end") is not None]
    if n < 3 or not level_walls:
        return []
    trimmed = _trimmed_walls(level_walls)
    xs, ys = [p[0] for p in polygon], [p[1] for p in polygon]
    box = (min(xs) - 1e-6, min(ys) - 1e-6, max(xs) + 1e-6, max(ys) + 1e-6)
    out = []
    for w in level_walls:
        t = trimmed.get(w["id"]) or w
        p, q = (float(t["start"][0]), float(t["start"][1])), (float(t["end"][0]), float(t["end"][1]))
        length = G.distance(p, q)
        if length < 1e-9 or max(p[0], q[0]) < box[0] or min(p[0], q[0]) > box[2] or max(p[1], q[1]) < box[1] \
                or min(p[1], q[1]) > box[3]:
            continue                                    # nowhere near the room
        cuts = {0.0, 1.0}
        for i in range(n):
            s = _segment_params(p, q, polygon[i], polygon[(i + 1) % n])
            if s is not None:
                cuts.add(s)
        cuts = sorted(cuts)
        inside: list[list[float]] = []
        for t0, t1 in zip(cuts, cuts[1:]):
            if t1 - t0 < 1e-9:
                continue
            mid = G.point_along_segment(p, q, (t0 + t1) / 2.0)
            edge = min(G.point_segment_distance(mid, polygon[i], polygon[(i + 1) % n]) for i in range(n))
            if edge <= INNER_WALL_EDGE_M or not G.point_in_polygon(mid, polygon):
                continue
            if inside and abs(inside[-1][1] - t0) < 1e-9:
                inside[-1][1] = t1                      # a crossing at a touching vertex: one part
            else:
                inside.append([t0, t1])
        parts = [(t0, t1) for t0, t1 in inside if (t1 - t0) * length >= INNER_WALL_MIN_M]
        if not parts:
            continue
        h = float(w["thickness"]) / 2.0
        nx, ny = G.unit_normal_left(p, q)
        faces, segs = [], []
        for t0, t1 in parts:
            a, b = G.point_along_segment(p, q, t0), G.point_along_segment(p, q, t1)
            segs.append((a, b))
            for side in (1.0, -1.0):
                faces.append(((a[0] + side * nx * h, a[1] + side * ny * h),
                              (b[0] + side * nx * h, b[1] + side * ny * h)))
            for end, at in ((t0, a), (t1, b)):
                if end <= 1e-9 or end >= 1.0 - 1e-9:     # the wall itself ends here: its end face is seen too
                    faces.append(((at[0] - nx * h, at[1] - ny * h), (at[0] + nx * h, at[1] + ny * h)))
        out.append({"id": w["id"], "thickness": float(w["thickness"]), "parts": segs, "faces": faces})
    return out


def inner_wall_rects(room: dict, building: dict, polygon=None) -> list[dict]:
    """Fix round after P3: the inside parts of ``inner_walls`` as obstacle rectangles (``center``, ``size``,
    ``rotation_deg``, as ``parametric.obstacle_rect``) for the camera points: no camera inside a wall band."""
    out = []
    for wall in inner_walls(room, building, polygon):
        for a, b in wall["parts"]:
            out.append({"center": [(a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0],
                        "size": [G.distance(a, b), wall["thickness"]], "rotation_deg": G.segment_angle_deg(a, b)})
    return out


def room_view_count(room: dict, building: Optional[dict] = None) -> int:
    """Views of ``room``: by the area of its polygon (§4.1; without ``building`` this area rule alone,
    the pre-layout estimate of ``wenart.run plan``); with ``building``, a room without ``shown_pieces``
    gets ``EMPTY_ROOM_VIEWS``, or 0 below ``MIN_EMPTY_ROOM_AREA_M2`` (docs/milestone7.md §6.2), and a stair
    core (``stair_core``, Milestone 11) gets 0."""
    area = G.polygon_area(room_polygon(room))
    if building is not None and not shown_pieces(room, building):
        return EMPTY_ROOM_VIEWS if area >= MIN_EMPTY_ROOM_AREA_M2 else 0
    if building is not None and stair_core(room, building):
        return 0
    return views_for_area(area)


STAIR_CORE_REASON = ("stair core: the stair fills the room, its only camera point is inside the stair; the hall "
                     "shows it (docs/milestone11.md §1.3 M5)")


def stair_core(room: dict, building: dict) -> bool:
    """True when ``room`` is a stair core (pure; Milestone 11, docs/milestone11.md §1.3 M5): it has no free camera
    point (``candidate_positions`` falls back) and the fallback point lies inside the footprint of one of its
    stairs. real02's unlabelled cores ("Oda") got two views from inside the stair: a bare wall and the steps."""
    stairs = [f for f in shown_pieces(room, building) if f.get("type") in P.SHELL_TYPES]
    if not stairs:
        return False
    points, fallback = candidate_positions(room, building)
    if fallback is None or not points:
        return False
    p = points[0]
    for f in stairs:
        r = obstacle_rect(f)
        if geom2d.distance_to_rect(p, r["center"], r["size"], r["rotation_deg"]) <= 1e-9:
            return True
    return False


def no_view_reason(room: dict, building: dict) -> Optional[str]:
    """Why ``room`` gets no camera (None when it gets at least one)."""
    if room_view_count(room, building) > 0:
        return None
    if shown_pieces(room, building) and stair_core(room, building):
        return STAIR_CORE_REASON
    area = G.polygon_area(room_polygon(room))
    return (f"no furniture after layout and decor and {area:.2f} m2 < {MIN_EMPTY_ROOM_AREA_M2:g} m2: "
            f"no view (docs/milestone7.md §6.2)")


def rooms_without_view(building: dict, level_id: Optional[str] = None) -> list[dict]:
    """The rooms (of ``level_id``, or of every level) the search gives no camera, in building order:
    ``[{"room_id", "level_id", "label", "area_m2", "reason"}]`` (the scene manifest's
    ``rooms_without_view``)."""
    out = []
    for room in building.get("rooms") or []:
        if level_id is not None and room["level_id"] != level_id:
            continue
        reason = no_view_reason(room, building)
        if reason is not None:
            out.append({"room_id": room["id"], "level_id": room["level_id"], "label": room.get("label"),
                        "area_m2": round(G.polygon_area(room_polygon(room)), 3), "reason": reason})
    return out


def type_weight(piece_type: Optional[str]) -> float:
    return float(SCORE["type_weight"].get(piece_type or "", SCORE["default_type_weight"]))


def _group_role(piece: dict) -> Optional[str]:
    g = piece.get("group")
    return g.get("role") if isinstance(g, dict) else None


def view_set(room: dict, pieces: Sequence[dict]) -> tuple[list[str], list[str]]:
    """``(anchors, set)``: the ids of the room's anchors and of its set among ``pieces`` (its ``shown_pieces``), in
    piece order (pure; fix round after the real06 run, 26 Oct 2026). The anchors are the pieces of the room type's
    ``VIEW_ANCHOR_TYPES`` and the group anchors (``group.role: anchor``); a room without any takes its pieces of the
    highest ``type_weight`` (a hall's stair, a dressing room's wardrobes). The set adds the other members of the
    anchors' groups (a sofa's armchairs and coffee table, a bed's nightstands). A stair counts only when it is the
    room's only kind of piece (a kitchen's stair is no view of the kitchen)."""
    if not pieces:
        return [], []
    types = set(VIEW_ANCHOR_TYPES.get(room.get("room_type") or "", ()))
    anchors = [f["id"] for f in pieces if f.get("type") in types or _group_role(f) == "anchor"]
    if not anchors:
        candidates = [f for f in pieces if f.get("type") not in P.SHELL_TYPES] or list(pieces)
        best = max(type_weight(f.get("type")) for f in candidates)
        anchors = [f["id"] for f in candidates if type_weight(f.get("type")) >= best - 1e-9]
    chosen = set(anchors)
    groups = {f["group"].get("group_id") for f in pieces if f["id"] in chosen and isinstance(f.get("group"), dict)}
    groups.discard(None)
    members = [f["id"] for f in pieces if f["id"] not in chosen and isinstance(f.get("group"), dict)
               and f["group"].get("group_id") in groups]
    chosen |= set(members)
    return anchors, [f["id"] for f in pieces if f["id"] in chosen]


def set_cover(shown: Sequence[float], weights: Sequence[float]) -> float:
    """The share of the room's set a view shows: ``sum_k w_k shown_k / sum_k w_k`` over the set (pure; 0 without a
    set); ``shown_k`` = the piece's in-frame box fraction x its visible fill x min(1, share / ``anchor_full_share``)
    (``RoomModel.measure``)."""
    total = float(sum(weights))
    if total <= 0:
        return 0.0
    return float(sum(float(w) * min(max(float(s), 0.0), 1.0) for s, w in zip(shown, weights))) / total


# The 12 edges of a box whose 8 corners are indexed by bits (x: 1, y: 2, z: 4).
_BOX_EDGES = tuple((i, i ^ bit) for i in range(8) for bit in (1, 2, 4) if not i & bit)


def box_corners(cx: float, cy: float, w: float, d: float, z0: float, z1: float,
                rotation_deg: float = 0.0) -> np.ndarray:
    """The 8 corners (8 x 3) of a box ``w`` x ``d`` on the plan point ``(cx, cy)``, turned by ``rotation_deg``, from
    ``z0`` to ``z1`` (corner ``i``: x side bit 1, y side bit 2, z side bit 4)."""
    r = math.radians(float(rotation_deg))
    c, s = math.cos(r), math.sin(r)
    out = np.empty((8, 3))
    for i in range(8):
        lx = (w / 2.0) * (1 if i & 1 else -1)
        ly = (d / 2.0) * (1 if i & 2 else -1)
        out[i] = (cx + c * lx - s * ly, cy + s * lx + c * ly, z1 if i & 4 else z0)
    return out


def frame_bounds(lens_mm: float = LENS_MM, shift_x: float = 0.0, shift_y: float = 0.0, sensor_mm: float = SENSOR_MM,
                 resolution=RESOLUTION) -> tuple[float, float, float, float]:
    """``(a0, a1, b0, b1)``: the frame's slopes (``ray_grid``'s ``a`` right, ``b`` up) at its left, right, bottom
    and top edges."""
    W, H = float(resolution[0]), float(resolution[1])
    f = float(lens_mm) / float(sensor_mm) * W
    return ((-W / 2.0 + float(shift_x) * W) / f, (W / 2.0 + float(shift_x) * W) / f,
            -(H / 2.0 - float(shift_y) * W) / f, (H / 2.0 + float(shift_y) * W) / f)


def box_in_frame(corners: np.ndarray, origin, forward: np.ndarray, right: np.ndarray, up: np.ndarray,
                 bounds, near: float = 0.05) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(inside, area, middle)`` of a box (``box_corners``, 8 x 3; each result C) or of K boxes (K x 8 x 3; each
    result C x K) seen by C cameras at ``origin`` with unit axes ``forward``/``right``/``up`` (C x 3; a ray is
    ``forward + a right + b up``) through the frame ``bounds`` (``frame_bounds``): the fraction of the box's projected
    bounding rectangle inside the frame, the frame share of that inside part (occlusion ignored) and whether that
    part reaches the frame's middle third of columns (``SCORE["centre_columns"]``). The box is cut at ``near`` metres
    ahead of the lens (the part behind projects far outside the frame), so a piece beside or behind the camera
    counts as outside."""
    pts = np.asarray(corners, dtype=np.float64)
    one = pts.ndim == 2
    rel = (pts[None] if one else pts) - np.asarray(origin, dtype=np.float64)        # K x 8 x 3
    z = np.einsum("kij,cj->kic", rel, forward)                                     # K x 8 x C
    x = np.einsum("kij,cj->kic", rel, right)
    y = np.einsum("kij,cj->kic", rel, up)
    front = z > near
    i, j = np.array(_BOX_EDGES).T
    cross = front[:, i] != front[:, j]                                             # K x 12 x C
    with np.errstate(divide="ignore", invalid="ignore"):
        t = (near - z[:, i]) / (z[:, j] - z[:, i])
        A = np.concatenate([np.where(front, x / z, np.nan),
                            np.where(cross, (x[:, i] + t * (x[:, j] - x[:, i])) / near, np.nan)], axis=1)
        B = np.concatenate([np.where(front, y / z, np.nan),
                            np.where(cross, (y[:, i] + t * (y[:, j] - y[:, i])) / near, np.nan)], axis=1)
    seen = ~np.isnan(A)                                                            # K x 20 x C
    ok = seen.any(axis=1)
    amin, amax = np.where(seen, A, np.inf).min(axis=1), np.where(seen, A, -np.inf).max(axis=1)
    bmin, bmax = np.where(seen, B, np.inf).min(axis=1), np.where(seen, B, -np.inf).max(axis=1)
    a0, a1, b0, b1 = bounds
    c0, c1 = SCORE["centre_columns"]
    with np.errstate(invalid="ignore"):
        left, right_ = np.maximum(amin, a0), np.minimum(amax, a1)
        inter = np.where(ok, np.clip(right_ - left, 0.0, None) * np.clip(np.minimum(bmax, b1) - np.maximum(bmin, b0),
                                                                          0.0, None), 0.0)
        area = np.where(ok, (amax - amin) * (bmax - bmin), 0.0)
        inside = np.where(area > 1e-12, inter / np.where(area > 1e-12, area, 1.0),
                          (ok & (amin >= a0) & (amax <= a1) & (bmin >= b0) & (bmax <= b1)).astype(float))
        middle = (inter > 0) & (right_ > a0 + c0 * (a1 - a0)) & (left < a0 + c1 * (a1 - a0))
    inside, share = np.clip(inside, 0.0, 1.0), inter / ((a1 - a0) * (b1 - b0))
    if one:
        return inside[0], share[0], middle[0]
    return inside.T, share.T, middle.T


def yaw_axes(yaws_deg: Sequence[float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(forward, right, up)`` (each n x 3) of pitch-0 cameras (``yaw_directions``' axes)."""
    yaw = np.radians(np.asarray(yaws_deg, dtype=np.float64))
    c, s = np.cos(yaw), np.sin(yaw)
    zero = np.zeros_like(c)
    return np.stack([c, s, zero], axis=1), np.stack([s, -c, zero], axis=1), np.stack([zero, zero, zero + 1.0], axis=1)


def look_axes(position, target) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """``(forward, right, up)`` (each 1 x 3) of a look-at camera with world up +Z (``camera_directions``' axes)."""
    pos = np.asarray(position, dtype=np.float64)
    f = np.asarray(target, dtype=np.float64) - pos
    f = f / np.linalg.norm(f)
    r = np.cross(f, [0.0, 0.0, 1.0])
    n = np.linalg.norm(r)
    r = np.array([1.0, 0.0, 0.0]) if n < 1e-9 else r / n
    return f[None, :], r[None, :], np.cross(r, f)[None, :]


def bare_centre(labels: np.ndarray, depth: np.ndarray, grid, blank_codes) -> np.ndarray:
    """``centre`` (C) of ray labels / depths (C x P, row-major over ``grid`` = (cols, rows)): the share of the frame's
    middle columns (``SCORE["centre_columns"]``) whose lowest surface above the floor is a wall or one of
    ``blank_codes`` (the door leaves) nearer than ``SCORE["centre_near_m"]`` (pure; fix round after the real06 run):
    nothing stands in front of that wall in the middle of the picture (a column, a blank tiled wall, a door). A
    piece in front of the wall, a window or opening down to the floor, or a wall farther away (the room's depth) is
    no bare column."""
    cols, rows = grid
    lo, hi = SCORE["centre_columns"]
    L = np.asarray(labels).reshape(-1, rows, cols)
    D = np.asarray(depth).reshape(-1, rows, cols)
    up = (L != FLOOR) & (L != NOTHING)
    has = up.any(axis=1)                                           # C x cols
    row = rows - 1 - np.argmax(up[:, ::-1, :], axis=1)            # the lowest such row of each column
    base = np.take_along_axis(L, row[:, None, :], axis=1)[:, 0, :]
    near = np.take_along_axis(D, row[:, None, :], axis=1)[:, 0, :] < SCORE["centre_near_m"]
    blank = (base == WALL) | np.isin(base, np.asarray(list(blank_codes), dtype=int))
    bare = has & blank & near
    middle = (np.arange(cols) >= lo * cols) & (np.arange(cols) < hi * cols)
    return bare[:, middle].mean(axis=1)


def furniture_share(shares: Sequence[float], touches_border: Sequence[bool], weights: Sequence[float]) -> float:
    """``furn`` of §4.1: ``sum_k w_k min(c_k, cap)/cap (0.6 if k touches the border) / sum_k w_k``
    over the room's pieces (0 for a room without pieces)."""
    total = float(sum(weights))
    if total <= 0:
        return 0.0
    cap = SCORE["piece_cap"]
    acc = 0.0
    for c, border, w in zip(shares, touches_border, weights):
        acc += float(w) * min(float(c), cap) / cap * (SCORE["border_factor"] if border else 1.0)
    return acc / total


def score_terms(m: dict) -> dict:
    """The §4.1 score from the model shares of one camera.

    ``m``: ``furn`` (``furniture_share``), ``open``, ``floor``, ``wall``,
    ``window``, ``ceiling``, ``near``, ``max_single`` (ray shares) and
    ``d_wall`` (metres); optional ``anchors`` (``set_cover``), ``edge_near``,
    ``door`` and ``centre`` (0 when absent). Returns the terms as they enter the total:
    ``{"total", "furniture", "anchors", "openings", "floor", "depth", "penalties", "blocked"}``.
    """
    furniture = SCORE["furniture_factor"] * float(m["furn"])
    anchors = SCORE["anchor_factor"] * float(m.get("anchors", 0.0))    # fix round after the real06 run
    openings = min(float(m["open"]), SCORE["openings_cap"]) / SCORE["openings_cap"]
    floor = min(float(m["floor"]), SCORE["floor_cap"]) / SCORE["floor_cap"]
    depth = min(float(m["d_wall"]) / SCORE["depth_ref_m"], 1.0)
    penalties = 0.0
    for name, (factor, allowed) in SCORE["penalties"].items():
        penalties += factor * max(0.0, float(m.get(name, 0.0)) - allowed)   # edge_near: Milestone 11
    total = furniture + anchors + openings + floor + depth - penalties
    return {"total": total, "furniture": furniture, "anchors": anchors, "openings": openings, "floor": floor,
            "depth": depth, "penalties": penalties, "blocked": is_blocked(m)}


def near_distance(lens_mm: float) -> float:
    """The near distance of a ``lens_mm`` camera (Milestone 8): ``SCORE["near_m"]`` (0.9 m, set with the
    24 mm lens of Milestone 6) times ``lens_mm / 24``: 0.675 m at 18 mm, 0.6 m at 16 mm. A surface at
    distance d through a lens L is as large in the frame as at d x 24 / L through the 24 mm lens, so the
    near share (and the blocked rule) means the same picture at every lens."""
    return SCORE["near_m"] * float(lens_mm) / SCORE["near_lens_mm"]


def is_blocked(m: dict) -> bool:
    """Blocked: the model's near share is over 0.30, one element covers over 0.50 of the rays, or the
    nearest surface (``min_depth``, planar metres) is nearer than 0.12 m. The last rule is for a camera at
    the fallback point inside a stair's box (pod run F1, real02's stair core): the stair is its open parts in
    the model, so a step side 0.08 m from the lens fills a few columns only, under both share limits. A
    camera at a free point (0.2 m from every floor piece, 0.3 m from the walls) sees nothing that near: at
    least 0.2 m x cos(atan(18 / 14)) = 0.123 m planar at the widest 14 mm lens. A share dict without
    ``min_depth`` has only the share rules."""
    return bool(float(m["near"]) > SCORE["blocked_near"] or float(m["max_single"]) > SCORE["blocked_single"]
                or float(m.get("min_depth", math.inf)) < SCORE["blocked_min_depth"])


# --------------------------------------------------------------------------
# Rays
# --------------------------------------------------------------------------

def ray_grid(grid=None, lens_mm: float = LENS_MM, sensor_mm: float = SENSOR_MM, resolution=RESOLUTION,
             shift_x: float = 0.0, shift_y: float = 0.0) -> tuple[np.ndarray, np.ndarray]:
    """``(a, b)`` (each ``rows x cols`` flattened row-major) of the ray grid over the frame.

    A grid cell's centre is the image point ``((i + 0.5) W / cols, (j + 0.5) H / rows)``; ``a``/``b``
    are its horizontal and vertical slopes by the §1.3 inverse projection with shift.
    """
    cols, rows = grid or SCORE["grid"]
    W, H = float(resolution[0]), float(resolution[1])
    fpx = float(lens_mm) / float(sensor_mm) * W
    col = (np.arange(cols) + 0.5) * W / cols
    row = (np.arange(rows) + 0.5) * H / rows
    a = (col - W / 2.0 + float(shift_x) * W) / fpx
    b = -(row - H / 2.0 - float(shift_y) * W) / fpx
    A, B = np.meshgrid(a, b)
    return A.ravel(), B.ravel()


def border_mask(grid=None) -> np.ndarray:
    """Flattened mask of the grid cells on the frame border."""
    cols, rows = grid or SCORE["grid"]
    m = np.zeros((rows, cols), dtype=bool)
    m[0, :] = m[-1, :] = m[:, 0] = m[:, -1] = True
    return m.ravel()


def yaw_directions(yaws_deg: Sequence[float], a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Ray directions (n_yaw x P x 3) of pitch-0 cameras: ``forward + a right + b up``
    with forward = (cos yaw, sin yaw, 0), right = (sin yaw, -cos yaw, 0), up = +Z."""
    yaw = np.radians(np.asarray(yaws_deg, dtype=np.float64))[:, None]
    c, s = np.cos(yaw), np.sin(yaw)
    out = np.empty((yaw.shape[0], a.shape[0], 3))
    out[..., 0] = c + a[None, :] * s
    out[..., 1] = s - a[None, :] * c
    out[..., 2] = b[None, :]
    return out


def camera_directions(position, target, a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Ray directions (P x 3) of a look-at camera with world up +Z (any pitch), planar-depth scaled."""
    pos = np.asarray(position, dtype=np.float64)
    f = np.asarray(target, dtype=np.float64) - pos
    f = f / np.linalg.norm(f)
    r = np.cross(f, [0.0, 0.0, 1.0])
    n = np.linalg.norm(r)
    r = np.array([1.0, 0.0, 0.0]) if n < 1e-9 else r / n
    u = np.cross(r, f)
    return f[None, :] + a[:, None] * r[None, :] + b[:, None] * u[None, :]


# --------------------------------------------------------------------------
# The room model
# --------------------------------------------------------------------------

mount_bottom = cameras.mount_bottom      # Milestone 10: how high a wall-hung piece hangs (0 on the floor)


def piece_profile(piece: dict) -> list[tuple[float, float, float, float, float]]:
    """Boxes ``(x0, y0, x1, y1, top)`` of a piece in its own frame (width X, depth Y, front -Y, back +Y,
    centred on the footprint centre), each standing on the floor up to ``top``.

    One box of ``piece_bbox`` for most types. A type of ``PROFILES`` (a piece with a back) gets the
    boxes of the parts the scene builder makes for it (``parametric.build_parts`` with the footprint
    and the type height, as ``furniture._parametric_object``): the low part, the side parts and the
    back slab, the back reaching the rear edge and the full ``piece_bbox`` height (a library asset's
    fitted box: its back or headboard top). A library asset is placed in the same frame (front -Y;
    ``furniture.fit_vertices``), so its profile is the parametric one stretched to its fitted box,
    every part clamped to that box's height; its seat or mattress height is the builder's at the piece's
    height, except a library toilet's bowl, which is the type's (``proxies.PROXY_HEIGHTS``, 0.4 m, as a
    drawn toilet without a height gets): an added toilet's JSON height is its cistern top
    (``furniture.schemas.HEIGHTS``, 0.8 m), which ``parametric._toilet`` reads as the bowl (pod F2: a 0.8 m
    phantom bowl beside the camera). When the low part is as tall as the box the profile is the box."""
    w, d, top, source = piece_bbox(piece)
    whole = [(-w / 2.0, -d / 2.0, w / 2.0, d / 2.0, top)]
    profile = PROFILES.get(piece.get("type"))
    if profile is None:
        return whole
    low_roles, side_roles = profile
    fp = piece["footprint"]
    fw, fd = float(fp["size"][0]), float(fp["size"][1])
    h, _ = proxy_height(piece["type"], piece.get("height"))
    if piece["type"] == "toilet" and source == "library":
        # An added toilet's JSON height (furniture.schemas.HEIGHTS 0.8) is its cistern top, while
        # parametric._toilet's h is the bowl; a library mesh has a real bowl, so it gets the type bowl, as drawn
        # toilets (no height) already do. The parametric toilet is built with that h and keeps it.
        h = proxy_height("toilet", None)[0]
    parts = P.build_parts(piece["type"], fw, fd, h, piece=piece)
    sx = w / fw if fw > 1e-9 else 1.0
    sy = d / fd if fd > 1e-9 else 1.0

    def box(group, back=False):
        x0, y0, _, x1, y1, z1 = P.parts_bbox(group)
        if back:                                       # to the rear edge, up to the piece's top
            return (x0 * sx, y0 * sy, x1 * sx, d / 2.0, top)
        return (x0 * sx, y0 * sy, x1 * sx, y1 * sy, min(z1, top))

    low = [p for p in parts if p["role"] in low_roles]
    sides = [p for p in parts if p["role"] in side_roles]
    if source == "library" and any(p["role"] == "mattress" for p in sides):
        # A library bed's mattress reaches its fitted box (its ledge, if any, is not known): the one low box of
        # Milestone 12 (frame and mattress together); the parametric bed v2 keeps its frame ledge and mattress box.
        low += [p for p in sides if p["role"] == "mattress"]
        sides = [p for p in sides if p["role"] != "mattress"]
    back = [p for p in parts if p["role"] == PROFILE_BACK_ROLE]
    if not low or not back:
        return whole
    boxes = [box(low)] + [box([p]) for p in sides]
    if max(b[4] for b in boxes) >= top - 1e-9:
        return whole
    return boxes + [box(back, back=True)]


def convex_parts_solid(parts, floor_z: float = 0.0):
    """``(lo, hi, planes)`` of convex parts (``parametric`` parts: ``verts``, ``faces`` wound outwards,
    z above the floor) for ``RoomModel``: the world bounding box (3-vectors, the floor added) and per part
    ``(normals k x 3, offsets k)`` with the inside ``normals . x <= offsets``. None without a part."""
    planes, pts = [], []
    for part in parts:
        verts = [(float(x), float(y), float(z) + float(floor_z)) for x, y, z in part["verts"]]
        normals, offsets = [], []
        for face in part["faces"]:
            n = geom2d.face_normal(verts, face)
            if n == (0.0, 0.0, 0.0):
                continue
            c = geom2d.face_center(verts, face)
            normals.append(n)
            offsets.append(n[0] * c[0] + n[1] * c[1] + n[2] * c[2])
        if len(normals) >= 4:
            planes.append((np.array(normals), np.array(offsets)))
            pts.extend(verts)
    if not planes:
        return None
    arr = np.array(pts)
    return arr.min(axis=0), arr.max(axis=0), planes


def _cast_convex_parts(origin, d: np.ndarray, lo, hi, parts, depth: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """``(t, hit)`` of rays ``origin + t d`` (N x 3) against convex parts (``convex_parts_solid``): ``hit``
    where a part lies nearer than ``depth``, ``t`` the entry parameter there (the exit one for an origin
    inside a part). Rays that miss the bounding box ``lo``-``hi`` skip the parts."""
    o = np.asarray(origin, dtype=np.float64)
    with np.errstate(divide="ignore", invalid="ignore"):
        t1, t2 = (lo[None, :] - o[None, :]) / d, (hi[None, :] - o[None, :]) / d
        tmin = np.fmax.reduce(np.fmin(t1, t2), axis=1)
        tmax = np.fmin.reduce(np.fmax(t1, t2), axis=1)
    sel = np.nonzero((tmax >= np.maximum(tmin, _EPS_T)) & (tmin < depth))[0]
    t_out = np.array(depth, dtype=np.float64, copy=True)
    hit_out = np.zeros(d.shape[0], dtype=bool)
    if sel.size == 0:
        return t_out, hit_out
    ds = d[sel]
    best = t_out[sel]
    hit = np.zeros(sel.size, dtype=bool)
    for normals, offsets in parts:
        den = ds @ normals.T                        # R x k
        num = offsets - normals @ o                 # k: >= 0 where the origin is inside that plane
        with np.errstate(divide="ignore", invalid="ignore"):
            t = num[None, :] / den
        enter = np.where(den < -1e-12, t, -np.inf).max(axis=1)
        leave = np.where(den > 1e-12, t, np.inf).min(axis=1)
        parallel_out = ((np.abs(den) <= 1e-12) & (num[None, :] < 0)).any(axis=1)
        ok = ~parallel_out & (leave >= np.maximum(enter, _EPS_T))
        th = np.where(enter > _EPS_T, enter, leave)
        closer = ok & (th < best)
        best = np.where(closer, th, best)
        hit |= closer
    t_out[sel] = best
    hit_out[sel] = hit
    return t_out, hit_out


class RoomModel:
    """Ray-cast model of one room (see the module docstring).

    ``elements``: one dict per label from ``FIRST_ELEMENT`` on (``id``,
    ``kind`` door/window/furniture, ``type``, ``weight``), doors and windows
    first (in ``room_openings`` order), then the pieces in building order.
    """

    def __init__(self, room: dict, building: dict, level: Optional[dict] = None):
        self.room = room
        self.level = level or next(lv for lv in building["levels"] if lv["id"] == room["level_id"])
        # Milestone 12 (track L): the room's own floor (floor_offset_m); the ceiling stays the level's.
        self.floor_z = float(self.level["elevation"]) + float(room.get("floor_offset_m") or 0.0)
        self.ceil_z = float(self.level["elevation"]) + float(self.level["ceiling_height"])
        # Milestone 10: a room under the roof has a sloped ceiling, the lowest of these planes (z = a x + b y
        # + c; roof.ceiling_planes, set on the level by the builder).
        self.ceiling_planes = [tuple(float(v) for v in p) for p in self.level.get("ceiling_planes") or []]
        if room.get("id") in set(self.level.get("open_rooms") or ()):
            self.ceiling_planes = []          # fix round after P5: a roof terrace open to the sky has no slope
        levels_above = any(float(lv["elevation"]) > float(self.level["elevation"]) for lv in building["levels"])
        self.polygon = room_polygon(room)
        self.pieces = shown_pieces(room, building)
        self.openings = cameras.room_openings(room, self.polygon, building)
        walls = {w["id"]: w for w in building.get("walls", []) if w["level_id"] == room["level_id"]}

        self.elements: list[dict] = []
        codes: dict[str, int] = {}
        for o in self.openings:
            if o["type"] in ("door", "window"):
                codes[o["id"]] = FIRST_ELEMENT + len(self.elements)
                self.elements.append({"id": o["id"], "kind": o["type"], "type": o["type"], "weight": 0.0})
        for f in self.pieces:
            self.elements.append({"id": f["id"], "kind": "furniture", "type": f.get("type"),
                                  "weight": type_weight(f.get("type"))})
        self.n_labels = FIRST_ELEMENT + len(self.elements)
        # fix round after the real06 run (26 Oct 2026): every piece's box for its in-frame fraction (``box_in_frame``;
        # set below with the ray boxes, None for a piece not in the model); the anchors and set after them
        self.piece_corners: list = [None] * len(self.pieces)
        idx = np.arange(FIRST_ELEMENT, self.n_labels)
        kinds = [e["kind"] for e in self.elements]
        self.piece_codes = idx[[k == "furniture" for k in kinds]] if kinds else idx
        self.opening_codes = idx[[k in ("door", "window") for k in kinds]] if kinds else idx
        self.window_codes = idx[[k == "window" for k in kinds]] if kinds else idx
        self.door_codes = idx[[k == "door" for k in kinds]] if kinds else idx
        self.piece_weights = np.array([e["weight"] for e in self.elements if e["kind"] == "furniture"])
        # Milestone 11 (§1.3 M6): the elements that loom at the frame edge when near the lens: door leaves and tall
        # pieces (a wardrobe side), not the low pieces a room view is about (a bed, a sofa)
        tall = {f["id"] for f in self.pieces if mount_bottom(f) + piece_bbox(f)[2] >= EDGE_TALL_M}
        self.edge_codes = np.array([FIRST_ELEMENT + k for k, e in enumerate(self.elements)
                                    if e["kind"] == "door" or (e["kind"] == "furniture" and e["id"] in tall)],
                                   dtype=int)

        # Walls: one per polygon edge, with the openings whose centre lies on it.
        self.edges = []
        n = len(self.polygon)
        for i in range(n):
            a, b = self.polygon[i], self.polygon[(i + 1) % n]
            length = G.distance(a, b)
            if length < 1e-9:
                continue
            ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
            spans = []
            for o in self.openings:
                tol = cameras.opening_edge_tolerance(o, walls)
                c = o["center"]
                along = (c[0] - a[0]) * ux + (c[1] - a[1]) * uy
                across = abs((c[0] - a[0]) * -uy + (c[1] - a[1]) * ux)
                if across > tol or along < -cameras.OPENING_EDGE_SLACK or along > length + cameras.OPENING_EDGE_SLACK:
                    continue
                bottom, top, _ = opening_vertical(o, self.level, levels_above)
                code = codes.get(o["id"], OPENING)
                spans.append((along, float(o["width"]) / 2.0, bottom, top, code))
            self.edges.append((a[0], a[1], b[0] - a[0], b[1] - a[1], length, spans))

        # Fix round after P3 (16-17 Oct 2026): a wall of the level standing inside the outline (``inner_walls``:
        # real04's bay wall, real03's stub) is a wall of the model too: both faces and its end faces, with that wall's
        # own openings on its faces (a door or window the room's outline does not carry is a plain opening label).
        self.inner_walls = inner_walls(room, building, self.polygon)
        for wall in self.inner_walls:
            mine = [o for o in building.get("openings") or [] if o.get("wall_id") == wall["id"]
                    and o.get("level_id") == room["level_id"] and o.get("center") is not None and not o.get("virtual")]
            for a, b in wall["faces"]:
                length = G.distance(a, b)
                if length < 1e-9:
                    continue
                ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
                spans = []
                for o in mine:
                    c = o["center"]
                    along = (c[0] - a[0]) * ux + (c[1] - a[1]) * uy
                    across = abs((c[0] - a[0]) * -uy + (c[1] - a[1]) * ux)
                    if across > wall["thickness"] + cameras.OPENING_EDGE_SLACK or \
                            along < -cameras.OPENING_EDGE_SLACK or along > length + cameras.OPENING_EDGE_SLACK:
                        continue
                    bottom, top, _ = opening_vertical(o, self.level, levels_above)
                    spans.append((along, float(o["width"]) / 2.0, bottom, top, codes.get(o["id"], OPENING)))
                self.edges.append((a[0], a[1], b[0] - a[0], b[1] - a[1], length, spans))

        # Furniture boxes: the piece's height profile (piece_profile: piece_bbox, or the low part, the
        # sides and the back slab of a piece with a back) in the footprint frame, standing on the floor;
        # the boxes of one piece share its label. A stair (fixed equipment, parametric.SHELL_TYPES) is its
        # built parts instead (review dwgblender-2): the step prisms on their sloped waist, the riser
        # plates, the landing slab and the rails, open under the upper flight and the landing as
        # shell.build_stairs builds it; its bounding box is a solid block taller than the room that hid
        # the walls behind the flights. A stair the builder leaves out on the top level of a whole building
        # (shell.top_level_stair, Milestone 10: the drawn upper end of the stair below, or no headroom under
        # the roof) is nothing in the model either.
        self.boxes = []
        self.solids = []
        stair_items = None
        for k, f in enumerate(self.pieces):
            code = FIRST_ELEMENT + len(self.elements) - len(self.pieces) + k
            if f.get("type") in P.SHELL_TYPES:
                if stair_items is None:
                    stair_items = {item["piece"]["id"]: item for item in plan_stairs(building, self.level)}
                item = stair_items.get(f["id"]) or {}
                plan = item.get("plan")
                if plan is not None:
                    solid = convex_parts_solid(P.stair_parts(plan), self.floor_z)
                    if solid is not None:
                        self.solids.append((code,) + solid)
                        lo, hi = solid[0], solid[1]
                        self.piece_corners[k] = box_corners((lo[0] + hi[0]) / 2.0, (lo[1] + hi[1]) / 2.0,
                                                            hi[0] - lo[0], hi[1] - lo[1], lo[2], hi[2])
                        continue
                elif "arrival" in item:
                    continue
            fp = f["footprint"]
            rot = math.radians(float(fp.get("rotation_deg") or 0.0))
            c, s = math.cos(rot), math.sin(rot)
            fx, fy = float(fp["center"][0]), float(fp["center"][1])
            base = self.floor_z + mount_bottom(f)                # a wall-hung piece hangs (Milestone 10)
            bw, bd, btop, _ = piece_bbox(f)
            self.piece_corners[k] = box_corners(fx, fy, bw, bd, base, base + btop, float(fp.get("rotation_deg") or 0.0))
            for x0, y0, x1, y1, top in piece_profile(f):
                lx, ly = (x0 + x1) / 2.0, (y0 + y1) / 2.0       # box centre in the piece frame -> world
                self.boxes.append((code, fx + c * lx - s * ly, fy + s * lx + c * ly, base + top / 2.0,
                                   (x1 - x0) / 2.0, (y1 - y0) / 2.0, top / 2.0, c, s))
        # fix round after the real06 run: the anchors and the set among the pieces the model holds (a stair's drawn
        # upper end on the top level is nothing in the model, so it is nothing a view can show); the pieces no camera
        # point of the room frames whole (``set_big``: none until it is called)
        self.anchor_ids, self.set_ids = view_set(room, [f for k, f in enumerate(self.pieces)
                                                        if self.piece_corners[k] is not None])
        self.piece_big = np.zeros(len(self.pieces), dtype=bool)
        self.big_known = False

    def set_big(self, frames: Sequence) -> None:
        """Mark the pieces too big for this room's frames (fix round after the real06 run): those whose in-frame
        fraction stays under ``anchor_inside`` in every one of ``frames`` (``piece_frames`` of the room's candidate
        points and yaws): a stair in a narrow hall, a counter run in a narrow kitchen. ``measure`` counts such a piece
        in the frame when its part there covers ``anchor_big_share`` of the frame and reaches the frame's middle
        third."""
        self.big_known = True
        if not self.pieces:
            return
        best = np.zeros(len(self.pieces))
        for inside, _area, _middle in frames:
            if len(inside):
                best = np.maximum(best, np.asarray(inside).max(axis=0))
        self.piece_big = np.array([c is not None for c in self.piece_corners]) & \
            (best < SCORE["anchor_inside"] - 1e-9)

    def room_frames(self, positions, height: float = None, yaws=None, lens_mm: float = LENS_MM,
                    shift_x: float = SHIFT_X, shift_y: float = SHIFT_Y) -> list:
        """``piece_frames`` of pitch-0 cameras at ``positions`` (``height`` over the room's floor, default
        ``CAMERA_HEIGHT``) for every yaw (default every ``YAW_STEP_DEG``) through ``lens_mm``."""
        z = self.floor_z + float(CAMERA_HEIGHT if height is None else height)
        yaws = list(range(0, 360, YAW_STEP_DEG)) if yaws is None else list(yaws)
        axes, bounds = yaw_axes(yaws), frame_bounds(lens_mm, shift_x, shift_y)
        return [self.piece_frames((x, y, z), *axes, bounds) for x, y in positions]

    # ------------------------------------------------------------------
    def cast(self, origin, dirs: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """``(labels int32, depth float)`` of rays from ``origin`` along ``dirs`` (N x 3 or ... x 3).

        ``depth`` is the ray parameter (planar depth for the planar-scaled
        directions of this module); ``inf`` with label ``NOTHING`` where no
        surface was hit."""
        shape = dirs.shape[:-1]
        d = dirs.reshape(-1, 3)
        ox, oy, oz = (float(v) for v in origin)
        dx, dy, dz = d[:, 0], d[:, 1], d[:, 2]
        with np.errstate(divide="ignore", invalid="ignore"):
            tf = np.where(dz < 0, (self.floor_z - oz) / dz, np.inf)
            tc = np.where(dz > 0, (self.ceil_z - oz) / dz, np.inf)
            for a, b, c in self.ceiling_planes:            # a sloped ceiling: the first plane the ray crosses
                den = dz - a * dx - b * dy
                tp = np.where(den > 1e-12, (a * ox + b * oy + c - oz) / den, np.inf)
                tc = np.minimum(tc, np.where(tp > _EPS_T, tp, np.inf))
        tf = np.where(tf > _EPS_T, tf, np.inf)
        tc = np.where(tc > _EPS_T, tc, np.inf)
        depth = np.minimum(tf, tc)
        labels = np.where(tf <= tc, FLOOR, CEILING).astype(np.int32)
        labels[~np.isfinite(depth)] = NOTHING

        for ax, ay, ex, ey, length, spans in self.edges:
            den = dx * ey - dy * ex
            rx, ry = ax - ox, ay - oy
            with np.errstate(divide="ignore", invalid="ignore"):
                t = (rx * ey - ry * ex) / den
                s = (rx * dy - ry * dx) / den
            ok = (np.abs(den) > 1e-12) & (t > _EPS_T) & (s >= -_EPS_S) & (s <= 1.0 + _EPS_S) & (t < depth)
            if not ok.any():
                continue
            z = oz + t * dz
            ok &= (z >= self.floor_z - 1e-9) & (z <= self.ceil_z + 1e-9)
            lab = np.full(d.shape[0], WALL, dtype=np.int32)
            along = s * length
            for centre, half, bottom, top, code in spans:
                inside = ok & (np.abs(along - centre) <= half) & (z >= bottom) & (z <= top)
                lab[inside] = code
            depth = np.where(ok, t, depth)
            labels = np.where(ok, lab, labels)

        for code, cx, cy, cz, hw, hd, hh, c, s in self.boxes:
            # World -> box frame: turn by -rotation about the box centre.
            px, py, pz = ox - cx, oy - cy, oz - cz
            lox, loy = c * px + s * py, -s * px + c * py
            ldx, ldy = c * dx + s * dy, -s * dx + c * dy
            with np.errstate(divide="ignore", invalid="ignore"):
                t1x, t2x = (-hw - lox) / ldx, (hw - lox) / ldx
                t1y, t2y = (-hd - loy) / ldy, (hd - loy) / ldy
                t1z, t2z = (-hh - pz) / dz, (hh - pz) / dz
                tmin = np.fmax(np.fmax(np.fmin(t1x, t2x), np.fmin(t1y, t2y)), np.fmin(t1z, t2z))
                tmax = np.fmin(np.fmin(np.fmax(t1x, t2x), np.fmax(t1y, t2y)), np.fmax(t1z, t2z))
            hit = tmax >= np.maximum(tmin, _EPS_T)
            t = np.where(tmin > _EPS_T, tmin, tmax)
            closer = hit & (t < depth)
            depth = np.where(closer, t, depth)
            labels = np.where(closer, code, labels)

        for code, lo, hi, parts in self.solids:
            t, hit = _cast_convex_parts((ox, oy, oz), d, lo, hi, parts, depth)
            depth = np.where(hit, t, depth)
            labels = np.where(hit, code, labels)
        return labels.reshape(shape), depth.reshape(shape)

    # ------------------------------------------------------------------
    def piece_frames(self, origin, forward: np.ndarray, right: np.ndarray, up: np.ndarray,
                     bounds) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """``(inside, area, middle)`` (each C x K, K = the room's pieces in ``pieces`` order) of ``box_in_frame`` for
        C cameras at ``origin``; 0 (False) for a piece not in the model."""
        C, K = forward.shape[0], len(self.pieces)
        inside, area, middle = np.zeros((C, K)), np.zeros((C, K)), np.zeros((C, K), dtype=bool)
        ks = [k for k, c in enumerate(self.piece_corners) if c is not None]
        if ks:
            got = box_in_frame(np.stack([self.piece_corners[k] for k in ks]), origin, forward, right, up, bounds)
            inside[:, ks], area[:, ks], middle[:, ks] = got
        return inside, area, middle

    def measure(self, labels: np.ndarray, depth: np.ndarray, border: np.ndarray,
                near_m: Optional[float] = None, frame=None, grid=None) -> list[dict]:
        """Model shares (the ``score_terms`` input) of each row of ``labels``/``depth`` (C x P) and the
        nearest depth ``min_depth`` (metres, inf when no ray hits anything; ``is_blocked``);
        ``near_m``: the near distance of the camera's lens (``near_distance``; default ``SCORE["near_m"]``,
        the 24 mm one).

        Fix round after the real06 run (26 Oct 2026): ``door`` (the door leaves' share, any depth); with ``frame``
        (``piece_frames`` of the C cameras) every piece's ``inside`` and ``shown`` (inside x seen, seen = its rays over
        ``anchor_fill`` of its in-frame box, at most 1), ``anchors`` (``set_cover`` of the room's set), ``anchors_in``
        and ``set_in`` (the anchors and set pieces in the frame: ``inside >= anchor_inside`` or a big piece's part
        there as ``set_big`` says, ``seen >= anchor_seen``, share ``>= anchor_min_share``), and an edge_near of a set
        piece counting its outside part only (x (1 - inside), for a set piece in the frame: the room's own shower or
        wardrobe is the subject, not a looming side);
        with ``grid`` (the rays' (cols, rows)) in a room with a set ``centre`` (``bare_centre``)."""
        near_m = SCORE["near_m"] if near_m is None else float(near_m)
        labels = np.asarray(labels).reshape(-1, labels.shape[-1])
        depth = np.asarray(depth).reshape(-1, depth.shape[-1])
        C, P = labels.shape
        # Milestone 11 (§1.3 M6): a door counts as an opening only beyond the near distance (a leaf beside the
        # lens is no view of a door), and one element near the lens at the frame edge is a penalty (edge_near)
        near_door = np.isin(labels, self.door_codes) & (depth < near_m) if len(self.door_codes) else \
            np.zeros(labels.shape, dtype=bool)
        edge_m = near_m * SCORE["edge_near_factor"]
        L = self.n_labels
        offsets = (np.arange(C) * L)[:, None]
        counts = np.bincount((labels + offsets).ravel(), minlength=C * L).reshape(C, L)
        bl = labels[:, border]
        bcounts = np.bincount((bl + offsets).ravel(), minlength=C * L).reshape(C, L)
        shares = counts / float(P)
        elements = np.concatenate([self.piece_codes, self.opening_codes]).astype(int)
        max_single = shares[:, elements].max(axis=1) if len(elements) else np.zeros(C)
        near = (depth < near_m).mean(axis=1)
        min_depth = np.where(np.isfinite(depth), depth, np.inf).min(axis=1)     # inf: nothing hit
        wall = labels == WALL
        d_wall = np.zeros(C)
        has_wall = wall.any(axis=1)
        if has_wall.any():
            with np.errstate(invalid="ignore"):
                d_wall[has_wall] = np.nanmedian(np.where(wall[has_wall], depth[has_wall], np.nan), axis=1)
        for i in np.nonzero(~has_wall)[0]:
            finite = depth[i][np.isfinite(depth[i])]
            d_wall[i] = float(np.median(finite)) if finite.size else 0.0
        close = depth < edge_m
        # the bare centre counts in a room with a set only (a hall without furniture has nothing to put there)
        centre = None if grid is None or not self.set_ids else bare_centre(labels, depth, grid, self.door_codes)
        set_ids, anchor_ids = set(self.set_ids), set(self.anchor_ids)
        ids = [f["id"] for f in self.pieces]
        set_k = [k for k, i in enumerate(ids) if i in set_ids]
        set_w = [type_weight(self.pieces[k].get("type")) for k in set_k]
        code_k = {int(c): k for k, c in enumerate(self.piece_codes)}
        out = []
        for i in range(C):
            pc = self.piece_codes
            furn = furniture_share(shares[i, pc], bcounts[i, pc] > 0, self.piece_weights) if len(pc) else 0.0
            inside = seen = None
            if frame is not None and len(pc):
                inside = np.asarray(frame[0][i], dtype=np.float64)
                area = np.asarray(frame[1][i], dtype=np.float64)
                with np.errstate(divide="ignore", invalid="ignore"):
                    seen = np.where(area > 1e-12, shares[i, pc] / (SCORE["anchor_fill"] * area), 0.0)
                seen = np.clip(np.nan_to_num(seen), 0.0, 1.0)
                # a piece no camera point of the room frames whole (set_big: a stair in a narrow hall) is in the
                # frame when its part there covers anchor_big_share of the frame and reaches the middle third
                big = self.piece_big & np.asarray(frame[2][i], dtype=bool) & (area >= SCORE["anchor_big_share"] - 1e-12)
                framed = np.where(big, 1.0, inside)
            edge = 0.0
            for c in self.edge_codes:
                if bcounts[i, c] and counts[i, c]:
                    e = float(((labels[i] == c) & close[i]).sum()) / float(P)
                    k = code_k.get(int(c))
                    if inside is not None and k is not None and ids[k] in set_ids \
                            and inside[k] >= SCORE["anchor_inside"] - 1e-9:
                        e *= 1.0 - float(inside[k])          # fix round after the real06 run: its outside part
                    edge = max(edge, e)
            opened = float(shares[i, self.opening_codes].sum()) if len(self.opening_codes) else 0.0
            row = {
                "furn": furn,
                "open": max(0.0, opened - float(near_door[i].sum()) / float(P)),
                "edge_near": edge,
                "window": float(shares[i, self.window_codes].sum()) if len(self.window_codes) else 0.0,
                "door": float(shares[i, self.door_codes].sum()) if len(self.door_codes) else 0.0,
                "floor": float(shares[i, FLOOR]), "ceiling": float(shares[i, CEILING]),
                "wall": float(shares[i, WALL]), "near": float(near[i]), "max_single": float(max_single[i]),
                "d_wall": float(d_wall[i]), "min_depth": float(min_depth[i]),
                "elements": {self.elements[c - FIRST_ELEMENT]["id"]: float(shares[i, c])
                           for c in range(FIRST_ELEMENT, L) if counts[i, c]},
                "cut": sorted(self.elements[c - FIRST_ELEMENT]["id"] for c in range(FIRST_ELEMENT, L) if bcounts[i, c]),
            }
            if centre is not None:
                row["centre"] = float(centre[i])
            if inside is not None:
                shown = framed * seen * np.clip(shares[i, pc] / SCORE["anchor_full_share"], 0.0, 1.0)
                well = (framed >= SCORE["anchor_inside"] - 1e-9) & (seen >= SCORE["anchor_seen"] - 1e-9) & \
                    (shares[i, pc] >= SCORE["anchor_min_share"] - 1e-12)
                row["inside"] = {ids[k]: round(float(inside[k]), 4) for k in range(len(ids)) if inside[k] > 0}
                row["shown"] = {ids[k]: round(float(shown[k]), 4) for k in range(len(ids)) if shown[k] > 0}
                row["anchors"] = set_cover([shown[k] for k in set_k], set_w)
                row["anchors_in"] = [ids[k] for k in range(len(ids)) if well[k] and ids[k] in anchor_ids]
                row["set_in"] = [ids[k] for k in range(len(ids)) if well[k] and ids[k] in set_ids]
            out.append(row)
        return out


# --------------------------------------------------------------------------
# Candidates and the pick
# --------------------------------------------------------------------------

def convex_corner_points(polygon: Sequence[Sequence[float]], insets=CORNER_INSETS) -> list[tuple[float, float]]:
    """Two points per convex corner, ``insets`` metres in along the bisector (not yet checked for room)."""
    n = len(polygon)
    orient = 1.0 if G.polygon_signed_area(polygon) >= 0 else -1.0
    out = []
    for i in range(n):
        pv, p, nx = polygon[i - 1], polygon[i], polygon[(i + 1) % n]
        cross = (p[0] - pv[0]) * (nx[1] - p[1]) - (p[1] - pv[1]) * (nx[0] - p[0])
        if cross * orient <= 1e-12:
            continue                          # reflex or straight
        l1, l2 = G.distance(pv, p), G.distance(nx, p)
        if l1 < 1e-9 or l2 < 1e-9:
            continue
        bx = (pv[0] - p[0]) / l1 + (nx[0] - p[0]) / l2
        by = (pv[1] - p[1]) / l1 + (nx[1] - p[1]) / l2
        lb = math.hypot(bx, by)
        if lb < 1e-9:
            continue
        for k in insets:
            out.append((p[0] + bx / lb * k, p[1] + by / lb * k))
    return out


def floor_decor_rects(room: dict, building: dict) -> list[dict]:
    """Obstacle rectangles of the room's decor that stands free on the floor up to camera height (no host: a large
    plant, a floor basket, a curtain at a window): pod P5 (11 Oct 2026) put real03's camera ``cam_r_L0_yasama_7_1``
    inside a 1.6 m plant (depth 0.05 m at the lens). Hosted decor and decor hanging above the camera are not
    obstacles."""
    out = []
    for d in building.get("decor") or []:
        if d.get("room_id") != room["id"] or d.get("host_id") or not d.get("center") or not d.get("size"):
            continue
        center, size = [float(v) for v in d["center"]], [float(v) for v in d["size"]]
        if len(size) < 2 or min(size[0], size[1]) <= 0.0:
            continue
        bottom = center[2] if len(center) > 2 else 0.0
        if bottom >= CAMERA_HEIGHT + 0.2:
            continue                                    # a pendant or a blind above the camera
        out.append({"center": center[:2], "size": size[:2], "rotation_deg": float(d.get("rotation_deg") or 0.0)})
    return out


def floor_obstacle(piece: dict) -> bool:
    """True when ``piece`` keeps the camera points away (pure): a piece standing on the floor, or one hung below the
    lens (``mount_bottom`` under ``CAMERA_HEIGHT``: a wall-hung basin or toilet, a vanity). Fix round after the real06
    run (26 Oct 2026): every wall-hung piece was exempt (Milestone 10, for the wall cabinets at 1.45 m), so real06's
    ``cam_r_L1_banyo_3`` stood over the washbasin f_L1_021 (hung at 0.15 m, top 0.85 m), the basin under the lens
    and out of the frame. A piece hung at or above the lens (a wall cabinet) stays no floor obstacle."""
    return mount_bottom(piece) < CAMERA_HEIGHT - 1e-9


def candidate_positions(room: dict, building: dict) -> tuple[list[tuple[float, float]], Optional[str]]:
    """Camera points of a room and a warning: the free convex-corner points and the free 0.5 m grid
    points (sorted by x, y); without any, the M5 fallback point with its warning."""
    polygon = room_polygon(room)
    # Wall-hung pieces (mount_bottom_m, docs/milestone10.md §1.6b row 15) hanging above the lens are not floor
    # obstacles (``floor_obstacle``); a basin hung below it is (fix round after the real06 run).
    pieces = [f for f in shown_pieces(room, building) if floor_obstacle(f)]
    # Fix round after P3: a wall standing inside the outline (``inner_wall_rects``) keeps the camera points away too.
    walls_in = inner_wall_rects(room, building, polygon)
    decor = floor_decor_rects(room, building)
    obstacles = [obstacle_rect(f) for f in pieces] + decor + walls_in
    corners = [p for p in convex_corner_points(polygon)
               if geom2d.point_is_free(p, polygon, obstacles, WALL_CLEARANCE, OBSTACLE_CLEARANCE)]
    grid = geom2d.free_points(polygon, obstacles, step=GRID_STEP, wall_clearance=WALL_CLEARANCE,
                              obstacle_clearance=OBSTACLE_CLEARANCE)
    points = sorted({(round(p[0], 9), round(p[1], 9)) for p in corners + grid})
    level = next((lv for lv in building.get("levels") or [] if lv["id"] == room.get("level_id")), None)
    sloped = sloped_level(level, room)
    if sloped is not None:
        points = [p for p in points if headroom_ok(sloped, p)]
    # Milestone 11 (docs/milestone11.md §1.3 M6, §4.4 V1): no camera pressed against a door leaf (the corner
    # points beside a door saw the leaf fill a quarter of the frame); a room with no other point keeps them.
    doors = cameras.door_segments(room, building)
    clear = [p for p in points if all(G.point_segment_distance(p, a, b) >= cameras.DOOR_CLEARANCE_M - 1e-9
                                      for _id, a, b in doors)]
    points = clear or points
    if points:
        return points, None
    # fix round after P5: the decor at camera height (P5's ceiling light 1.155 m above the floor) is a tall obstacle
    # of the fallback too, and under a slope the fallback point keeps its headroom
    tall = [obstacle_rect(f) for f in pieces if piece_bbox(f)[2] >= CAMERA_HEIGHT] + walls_in + decor
    p, warning = fallback_position(polygon, obstacles, tall, sloped)
    return [(round(float(p[0]), 9), round(float(p[1]), 9))], warning


HEADROOM_M = 0.30                    # Milestone 10: a camera stays this far under a sloped ceiling


def sloped_level(level: Optional[dict], room: dict) -> Optional[dict]:
    """``level`` when ``room`` stands under its sloped ceiling (``level["ceiling_planes"]``), else None (pure). Fix
    round after P5 (22 Oct 2026): a room ``build.prepare`` decided open to the sky (``level["open_rooms"]``, a roof
    terrace: the shell builds no ceiling there) is under no slope."""
    if level is None or not level.get("ceiling_planes"):
        return None
    if room.get("id") in set(level.get("open_rooms") or ()):
        return None
    return level


def ceiling_above_floor(level: dict, p) -> float:
    """The sloped ceiling's height above the level's floor at ``p`` (pure; ``math.inf`` without ceiling planes)."""
    planes = level.get("ceiling_planes") or []
    if not planes:
        return math.inf
    return min(float(a) * p[0] + float(b) * p[1] + float(c) for a, b, c in planes) - float(level["elevation"])


def headroom_ok(level: dict, p) -> bool:
    """True when the sloped ceiling of a room under the roof (``level["ceiling_planes"]``) is at least
    ``HEADROOM_M`` above a camera at ``CAMERA_HEIGHT`` at ``p``."""
    planes = level.get("ceiling_planes") or []
    if not planes:
        return True
    z = min(float(a) * p[0] + float(b) * p[1] + float(c) for a, b, c in planes)
    return z >= float(level["elevation"]) + CAMERA_HEIGHT + HEADROOM_M


def fallback_position(polygon, obstacles, tall, level: Optional[dict] = None) -> tuple[tuple[float, float], str]:
    """The M5 fallback (``cameras._Search.fallback``, unchanged) anchored at the room's inner point.

    The anchor is ``lighting.polylabel`` (the point farthest from the walls), not the centroid: the
    centroid of an L-shaped room can lie outside it, in the notch, and a camera there renders the wall
    mass or the neighbouring room under this room's name (review C1). The inner point is always inside
    the polygon, so a cramped view stays in the room and the model flags it ``blocked unavoidable``.
    The warning says what happened: the anchor is the room's inner point, and the last resort is said
    to be inside a proxy only when it is.

    Fix round after P5 (22 Oct 2026): ``level`` (``sloped_level``: the room is under the sloped ceiling) makes the
    point keep its headroom: a fallback point failing ``headroom_ok`` gives way to the point clear of the walls and
    of ``tall`` nearest the anchor that passes it, else to the clear point with the most ceiling over it (the
    warning says so). P5's real04 bathroom had 0.15 m of ceiling over the lens at its inner point."""
    from wenart.blender import lighting

    x, y, distance = lighting.polylabel(polygon)
    anchor = (x, y)
    search = cameras._Search(polygon, obstacles, tall, [], anchor)
    p, warning = search.fallback(anchor, "no free camera point in the room")
    if warning.endswith("INSIDE a proxy"):
        inside = any(geom2d.distance_to_rect(p, ob["center"], ob["size"], ob["rotation_deg"]) <= 1e-9 for ob in tall)
        where = "INSIDE a proxy" if inside else f"{distance:.2f} m from the nearest wall"
        warning = (f"no free camera point in the room; no point clear of the walls and the tall proxies, "
                   f"camera at the room's inner point {where}")
    else:
        warning = warning.replace("centroid", "room's inner point")
    if level is not None and level.get("ceiling_planes") and not headroom_ok(level, p):
        clear = geom2d.free_points(polygon, tall, wall_clearance=WALL_CLEARANCE, obstacle_clearance=OBSTACLE_CLEARANCE)
        ok = [q for q in clear if headroom_ok(level, q)]
        if ok:
            p = min(ok, key=lambda q: (G.distance(q, anchor), q))
            warning += (f"; moved to the nearest point with {HEADROOM_M:g} m of headroom under the sloped ceiling "
                        f"({ceiling_above_floor(level, p):.2f} m high there)")
        elif clear:
            p = max(clear, key=lambda q: (ceiling_above_floor(level, q), -G.distance(q, anchor)))
            warning += (f"; no point with {HEADROOM_M:g} m of headroom under the sloped ceiling, moved to the point "
                        f"with the most ({ceiling_above_floor(level, p):.2f} m high there)")
    return p, warning


def yaw_difference(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0)


def sort_key(c: dict) -> tuple:
    """Ties: score (higher first), then x, y, yaw."""
    return (-round(c["total"], SCORE_DECIMALS), c["x"], c["y"], c["yaw"])


def _distinct(c: dict, picks: Sequence[dict]) -> bool:
    return all(yaw_difference(c["yaw"], p["yaw"]) >= MIN_YAW_DIFF_DEG - 1e-9
               or math.hypot(c["x"] - p["x"], c["y"] - p["y"]) >= MIN_DISTANCE_M - 1e-9 for p in picks)


def cover_gain(c: dict, got: dict, weights: Optional[dict]) -> float:
    """What ``c`` adds to the room's set over the earlier picks (pure): ``sum_k w_k max(0, shown_k - got_k) / sum_k
    w_k`` over ``weights`` (``{set piece id: type weight}``; ``shown`` of the candidate's shares, ``got`` the best
    ``shown`` of the earlier picks); 0 without weights."""
    total = float(sum((weights or {}).values()))
    if total <= 0:
        return 0.0
    shown = (c.get("shares") or {}).get("shown") or {}
    return sum(float(w) * max(0.0, float(shown.get(k, 0.0)) - float(got.get(k, 0.0)))
               for k, w in weights.items()) / total


def select_views(candidates: Sequence[dict], n: int, small: bool = False,
                 weights: Optional[dict] = None) -> tuple[list[dict], Optional[str]]:
    """The §4.1 greedy pick: ``(picks, warning)`` from candidate dicts with ``total``, ``x``, ``y``,
    ``yaw`` and ``blocked``; at most ``n`` and at least one pick (none for no candidate).

    Fix round after the real06 run (26 Oct 2026): a candidate with ``anchored`` (``score_candidates``: True when it
    shows one of the room's anchors inside the frame, None in a room without anchors) False is never picked while one
    with True exists; when no unblocked candidate shows an anchor the room gets its best view only, with
    ``NO_ANCHOR_NOTE`` (fewer views beat views of a wall). A later pick is the eligible candidate with the highest
    value ``total + anchor_factor x cover_gain`` (``weights``: the set's type weights; what it shows of the set that
    the earlier picks do not); eligible: distinct from every earlier pick (50 degrees of yaw or 1 m), its value not
    below ``DROP_BELOW_BEST`` x the best score and, with ``small`` (a room under ``SMALL_ROOM_M2``), showing a piece of
    the room's set (``set_in``) that no earlier pick shows. Without ``weights`` the value is the score: the greedy
    pick in score order of §4.1."""
    ordered = sorted(candidates, key=sort_key)
    free = [c for c in ordered if not c["blocked"]]
    if not free:
        return (ordered[:1], BLOCKED_WARNING) if ordered else ([], None)
    if any(c.get("anchored") is not None for c in free):           # the room has anchors
        pool = [c for c in free if c.get("anchored")]
        if not pool:
            return [free[0]], NO_ANCHOR_NOTE
    else:
        pool = free
    best = round(pool[0]["total"], SCORE_DECIMALS)
    picks = [pool[0]]
    shown = set(pool[0].get("set_in") or ())
    got = dict((pool[0].get("shares") or {}).get("shown") or {})
    rest = list(pool[1:])
    while len(picks) < n:
        values = []
        for c in rest:
            if not _distinct(c, picks) or (small and c.get("set_in") is not None and not set(c["set_in"]) - shown):
                continue
            value = round(c["total"] + SCORE["anchor_factor"] * cover_gain(c, got, weights), SCORE_DECIMALS)
            if value >= DROP_BELOW_BEST * best:
                values.append(((-value,) + sort_key(c)[1:], c))
        if not values:
            break
        c = min(values, key=lambda v: v[0])[1]
        picks.append(c)
        rest = [r for r in rest if r is not c]
        shown |= set(c.get("set_in") or ())
        for k, v in ((c.get("shares") or {}).get("shown") or {}).items():
            got[k] = max(float(got.get(k, 0.0)), float(v))
    return picks, None


def score_candidates(model: RoomModel, positions, height: float = CAMERA_HEIGHT, yaws=None,
                     shift_x: float = SHIFT_X, shift_y: float = SHIFT_Y, grid=None,
                     lens_mm: float = LENS_MM) -> list[dict]:
    """Every (position, yaw) candidate of a room with its model shares and score terms, seen through
    ``lens_mm`` (the room's lens, ``cameras.room_lens``). Fix round after the real06 run: a model whose big pieces are
    not known yet (``RoomModel.set_big``) takes them from these candidates (``plan_room``: the room's camera points)."""
    grid = grid or SCORE["grid"]
    yaws = list(range(0, 360, YAW_STEP_DEG)) if yaws is None else list(yaws)
    a, b = ray_grid(grid, lens_mm, shift_x=shift_x, shift_y=shift_y)
    dirs = yaw_directions(yaws, a, b)
    border = border_mask(grid)
    axes = yaw_axes(yaws)                                # fix round after the real06 run: the pieces in the frame
    bounds = frame_bounds(lens_mm, shift_x, shift_y)
    z = model.floor_z + float(height)
    out = []
    near_m = near_distance(lens_mm)
    frames = [model.piece_frames((x, y, z), *axes, bounds) for x, y in positions]
    if not model.big_known:
        model.set_big(frames)                            # the pieces none of these frames holds whole
    for (x, y), frame in zip(positions, frames):
        labels, depth = model.cast((x, y, z), dirs)
        for yaw, m in zip(yaws, model.measure(labels, depth, border, near_m, frame, grid)):
            terms = score_terms(m)
            out.append({"x": float(x), "y": float(y), "yaw": float(yaw), "total": terms["total"], "terms": terms,
                        "blocked": terms["blocked"], "shares": m,
                        "anchored": bool(m.get("anchors_in")) if model.anchor_ids else None,
                        "set_in": list(m.get("set_in") or [])})
    return out


def score_camera(building: dict, camera: dict, grid=None) -> dict:
    """Model shares and score terms of any camera plan (M5 or searched; pitch, shift and lens as recorded, the
    near distance of its lens)."""
    room = next(r for r in building["rooms"] if r["id"] == camera["room_id"])
    model = RoomModel(room, building)
    grid = grid or SCORE["grid"]
    lens = float(camera.get("lens_mm") or cameras.M5_LENS_MM)    # no lens_mm: a pre-Milestone 8 camera (24 mm)
    a, b = ray_grid(grid, lens, camera.get("sensor_mm") or SENSOR_MM,
                    camera.get("resolution") or RESOLUTION, float(camera.get("shift_x") or 0.0),
                    float(camera.get("shift_y") or 0.0))
    dirs = camera_directions(camera["position"], camera["target"], a, b)
    labels, depth = model.cast(camera["position"], dirs)
    bounds = frame_bounds(lens, float(camera.get("shift_x") or 0.0), float(camera.get("shift_y") or 0.0),
                          camera.get("sensor_mm") or SENSOR_MM, camera.get("resolution") or RESOLUTION)
    frame = model.piece_frames(camera["position"], *look_axes(camera["position"], camera["target"]), bounds)
    if model.anchor_ids:                                 # fix round after the real06 run: the room's big pieces
        model.set_big(model.room_frames(candidate_positions(room, building)[0], lens_mm=lens,
                                        shift_x=float(camera.get("shift_x") or 0.0),
                                        shift_y=float(camera.get("shift_y") or 0.0)))
    m = model.measure(labels[None, :], depth[None, :], border_mask(grid), near_distance(lens), frame, grid)[0]
    return {"shares": m, "terms": score_terms(m)}


# --------------------------------------------------------------------------
# Plans
# --------------------------------------------------------------------------

def _round(v: float, nd: int = 4) -> float:
    r = round(float(v), nd)
    return 0.0 if r == 0 else r


def _frustum_lists(model: RoomModel, position, target, seen=None,
                   lens_mm: float = LENS_MM) -> tuple[list[str], list[str]]:
    """The room's openings whose centre is inside the shifted frustum of a ``lens_mm`` camera (as the
    M5 lists), and its pieces whose centre is inside it or that the model's rays see (``seen``:
    ``{element id: ray share}`` of this view, the ``elements`` of ``RoomModel.measure``). A long piece
    seen from the side (a 2.4 m stair filling half the frame) can have its centre outside the frame
    (review dwgblender-2)."""
    tangents = geom2d.frustum_tangents(lens_mm, SENSOR_MM, RESOLUTION)
    fz = model.floor_z
    seen = seen or {}
    opens = [o["id"] for o in model.openings
             if geom2d.point_in_frustum((o["center"][0], o["center"][1], fz + 1.0), position, target, tangents,
                                        shift_x=SHIFT_X, shift_y=SHIFT_Y)]
    pieces = [f["id"] for f in model.pieces
              if seen.get(f["id"], 0.0) > 0.0
              or geom2d.point_in_frustum((f["footprint"]["center"][0], f["footprint"]["center"][1],
                                          fz + mount_bottom(f) + piece_bbox(f)[2] / 2.0), position, target, tangents,
                                         shift_x=SHIFT_X, shift_y=SHIFT_Y)]
    return opens, pieces


def _plan(model: RoomModel, index: int, pick: dict, warning: Optional[str], lens_mm: float = LENS_MM,
          lens_rule: Optional[str] = None) -> dict:
    room = model.room
    z = model.floor_z + CAMERA_HEIGHT
    yaw = math.radians(pick["yaw"])
    position = [_round(pick["x"], 6), _round(pick["y"], 6), _round(z, 6)]
    target = [_round(pick["x"] + TARGET_DISTANCE * math.cos(yaw), 6),
              _round(pick["y"] + TARGET_DISTANCE * math.sin(yaw), 6), _round(z, 6)]
    t, m = pick["terms"], pick["shares"]
    score = {"total": _round(t["total"]), "furniture": _round(t["furniture"]),
             "anchors": _round(t.get("anchors", 0.0)), "openings": _round(t["openings"]),
             "floor": _round(t["floor"]), "depth": _round(t["depth"]), "penalties": _round(t["penalties"]),
             "blocked": bool(t["blocked"]), "yaw_deg": float(pick["yaw"]),
             "shares": {k: _round(m[k]) for k in ("furn", "anchors", "open", "window", "door", "centre", "floor",
                                                  "ceiling", "wall", "near", "max_single", "d_wall") if k in m}}
    placement = (f"search: score {score['total']:.3f} = furniture {score['furniture']:.3f} + anchors "
                 f"{score['anchors']:.3f} + openings {score['openings']:.3f} + floor {score['floor']:.3f} + depth "
                 f"{score['depth']:.3f} - penalties {score['penalties']:.3f}; yaw {pick['yaw']:.0f} deg")
    opens, pieces = _frustum_lists(model, position, target, m.get("elements"), lens_mm)
    return {
        "name": f"cam_{room['id']}_{index}",
        "room_id": room["id"], "level_id": room["level_id"], "index": index,
        "position": position, "target": target,
        "lens_mm": float(lens_mm), "lens_rule": lens_rule, "sensor_mm": SENSOR_MM, "resolution": list(RESOLUTION),
        "shift_x": SHIFT_X, "shift_y": SHIFT_Y, "policy": POLICY, "score": score,
        "placement": placement, "anchor": None, "warning": warning,
        "visible_openings": opens, "visible_furniture": pieces,
        # fix round after the real06 run (26 Oct 2026): the room's anchors and set pieces inside this frame
        "anchors_in_frame": list(m.get("anchors_in") or []), "set_in_frame": list(m.get("set_in") or []),
    }


def plan_room(room: dict, building: dict, level: Optional[dict] = None,
              lens_mm: Optional[float] = None) -> tuple[list[dict], int]:
    """``(plans, candidates scored)`` of one room; ``([], 0)`` for a room without a view
    (``no_view_reason``). The candidates are scored through the room's lens (``cameras.room_lens``:
    ``lens_mm`` = the brief's ``render.lens_mm``, or None for the 18 / 16 mm rule)."""
    model = RoomModel(room, building, level)
    if len(model.polygon) < 3:
        raise ValueError(f"room {room['id']}: polygon with fewer than 3 vertices, no camera can be placed")
    n = room_view_count(room, building)
    if n == 0:
        return [], 0
    lens, rule = cameras.room_lens(room, lens_mm)
    positions, fallback = candidate_positions(room, building)
    if fallback:                       # Milestone 11 (§1.3 M4): one cramped point gives one view, not three
        n = 1
    if model.pieces and all(c is None for c in model.piece_corners):
        n = min(n, EMPTY_ROOM_VIEWS)   # fix round after the real06 run: nothing in the model (a stair's top end)
    cands = score_candidates(model, positions, lens_mm=lens)
    # fix round after the real06 run: later views add what the earlier ones do not show of the room's set; a small
    # room's later views must show a piece of it the earlier ones do not
    weights = {f["id"]: type_weight(f.get("type")) for f in model.pieces if f["id"] in set(model.set_ids)}
    picks, blocked = select_views(cands, n, small=G.polygon_area(model.polygon) < SMALL_ROOM_M2, weights=weights)
    warning = "; ".join(w for w in (fallback, blocked) if w) or None
    return [_plan(model, i, p, warning, lens, rule) for i, p in enumerate(picks, start=1)], len(cands)


def plan_level(building: dict, level_id: str, lens_mm: Optional[float] = None) -> list[dict]:
    """Searched camera plans of every room of ``level_id`` (``cameras.plan_cameras(policy="search")``);
    ``lens_mm``: the brief's ``render.lens_mm`` for every room, None for the 18 / 16 mm rule.

    Every plan carries ``search_seconds``: the wall time of this level's search."""
    level = next(lv for lv in building["levels"] if lv["id"] == level_id)
    t0 = time.perf_counter()
    plans: list[dict] = []
    for room in building["rooms"]:
        if room["level_id"] != level_id:
            continue
        plans.extend(plan_room(room, building, level, lens_mm)[0])
    seconds = round(time.perf_counter() - t0, 3)
    for plan in plans:
        plan["search_seconds"] = seconds
    return plans


SHOW_MIN_SHARE = 0.003      # a piece is "shown" by a candidate when this share of its rays hits it
SHOW_POSES = 8              # poses_showing: the best poses returned (the camera validator picks the first that passes)


def poses_showing(room: dict, building: dict, show: Sequence[str], lens_mm: Optional[float] = None,
                  limit: int = SHOW_POSES) -> tuple[list[dict], list[str]]:
    """27 Oct 2026 (Argus on real06: 26 of 56 own edits were camera poses the model guessed, at the room's origin or
    outside it): ``(poses, not_here)``: the room's camera candidates (the build's search: its free points, its yaws,
    its lens) that show the elements ``show`` (pieces, doors, windows), most of them first, then the most of them
    whole in the frame, then the search score; ``not_here`` the ids of ``show`` that are no element of the room.
    Each pose: ``position``, ``target``, ``lens_mm``, ``shows``, ``misses``, ``score`` (blocked candidates left out).
    The AI names what a view must show; the code gives the coordinates."""
    model = RoomModel(room, building)
    known = {e["id"] for e in model.elements}
    want = [str(i) for i in dict.fromkeys(show) if str(i) in known]
    not_here = [str(i) for i in dict.fromkeys(show) if str(i) not in known]
    if not want or len(model.polygon) < 3:
        return [], not_here
    lens, _rule = cameras.room_lens(room, lens_mm)
    positions, _warning = candidate_positions(room, building)
    rows = []
    for c in score_candidates(model, positions, lens_mm=lens):
        if c["blocked"]:
            continue
        el = c["shares"].get("elements") or {}
        shows = [i for i in want if float(el.get(i) or 0.0) >= SHOW_MIN_SHARE]
        if not shows:
            continue
        whole = set(c["shares"].get("set_in") or ()) | set(c["shares"].get("anchors_in") or ())
        rows.append((-len(shows), -sum(1 for i in shows if i in whole), -round(float(c["total"]), SCORE_DECIMALS),
                     c["x"], c["y"], c["yaw"], c, shows))
    rows.sort(key=lambda r: r[:6])
    out = []
    for *_k, c, shows in rows[:max(1, int(limit))]:
        plan = _plan(model, 1, c, None, lens)
        out.append({"position": plan["position"], "target": plan["target"], "lens_mm": float(lens), "shows": shows,
                    "misses": [i for i in want if i not in shows], "score": plan["score"]["total"]})
    return out, not_here


LENS_CLEARANCE_KINDS = ("furniture", "furniture_proxy", "decor")   # the scene manifest entries with ``box3d``


def _nearest_on_box(p, box: dict) -> tuple[float, float, float]:
    """The point of a scene manifest ``box3d`` (``center``, ``size`` in the box frame turned by ``rotation_deg``
    about +Z, ``geom2d.oriented_box``) nearest to ``p`` (pure; ``p`` itself when inside)."""
    cx, cy, cz = (float(v) for v in box["center"])
    sx, sy, sz = (float(v) / 2.0 for v in box["size"])
    r = math.radians(float(box.get("rotation_deg") or 0.0))
    c, s = math.cos(r), math.sin(r)
    dx, dy = float(p[0]) - cx, float(p[1]) - cy
    lx, ly = dx * c + dy * s, -dx * s + dy * c
    lx, ly = min(max(lx, -sx), sx), min(max(ly, -sy), sy)
    z = min(max(float(p[2]), cz - sz), cz + sz)
    return cx + lx * c - ly * s, cy + lx * s + ly * c, z


def lens_clearance(plans: Sequence[dict], objects: Sequence[dict], min_m: Optional[float] = None) -> list[dict]:
    """The searched interior cameras whose lens is nearer than ``min_m`` (``SCORE["blocked_min_depth"]``, 0.12 m) to
    a built box (pure; fix round after P5, 22 Oct 2026; warning only, no camera is moved).

    What: for every plan with a ``room_id``, ``kind`` interior (or none), ``source`` searched (or none: a plan of
    the search; the agent's own cameras carry it too, ``build.merge_agent_cameras``) and a ``position``, the nearest
    ``box3d`` of the scene manifest ``objects`` of kind furniture,
    furniture_proxy or decor (the rig's fixture meshes are decor entries) that is not behind the lens (its nearest
    point is in front of, beside, above or under the lens, ``(q - p) . forward >= 0``, or the lens is inside it);
    ``[{"camera", "room_id", "object", "kind", "distance_m", "warning"}]``, sorted by camera. Why: the ray model of
    the search sees the walls, the openings and the furniture only (decor is a floor obstacle, ``floor_decor_rects``,
    and rig meshes are built after the search); P5's ``cam_r_L1_banyo_1`` stood 0.015 m over the decor light
    ``dec_L1_011`` (56 % of the frame, depth 0.05 m at the clip) with the model's view ``not blocked``, and only the
    GPU tests saw it. On P5's scene manifest this check lists that camera only (the next nearest lens is 0.22 m from
    a box). Replayed and exterior cameras are not checked (the replayed set is frozen)."""
    min_m = float(SCORE["blocked_min_depth"]) if min_m is None else float(min_m)
    boxes = [o for o in objects or () if o.get("kind") in LENS_CLEARANCE_KINDS and (o.get("box3d") or {}).get("size")]
    out: list[dict] = []
    for plan in plans or ():
        if not plan.get("room_id") or plan.get("kind") not in (None, "interior") \
                or (plan.get("source") or "searched") != "searched" or not plan.get("position"):
            continue
        p = [float(v) for v in plan["position"][:3]]
        target = plan.get("target")
        forward = None
        if target:
            f = [float(t) - v for t, v in zip(target[:3], p)]
            n = math.sqrt(sum(v * v for v in f))
            forward = [v / n for v in f] if n > 1e-9 else None
        best = None
        for o in boxes:
            q = _nearest_on_box(p, o["box3d"])
            d = math.dist(p, q)
            if d >= min_m - 1e-12:
                continue
            if forward is not None and d > 1e-9 and sum((a - b) * c for a, b, c in zip(q, p, forward)) < -1e-9:
                continue                                    # behind the lens: not in the frame
            if best is None or d < best[0]:
                best = (d, o)
        if best is None:
            continue
        d, o = best
        what = o.get("wenart_id") or o.get("name")
        out.append({"camera": plan.get("name"), "room_id": plan.get("room_id"), "object": what, "kind": o.get("kind"),
                    "distance_m": round(d, 4),
                    "warning": (f"{plan.get('name')}: the lens is {d:.3f} m from the {o.get('kind')} {what} (nearer "
                                f"than {min_m:g} m, the blocked distance of the camera search): the view may be "
                                f"blocked (lens clearance, warning only)")})
    return sorted(out, key=lambda h: str(h["camera"]))


# Fix round after P6b (23 Oct 2026): a replayed camera a newly built piece blocks or contains (module docstring).
REPLAY_MOVE_MAX_M = 1.5          # a frozen view moved farther is another view: it keeps its pose with the warning
REPLAY_LOOKS_OUT_M = 0.10        # a lens this near (along its view) the side of a box it looks out of sees past it
# fix round after P6b (23 Oct 2026), review: ... when the near clip hides that side over the whole frame: the clip is
# set this far past the box's exit depth, and the rest of the view must lie this far past the clip
REPLAY_CLIP_MARGIN_M = 0.01
REPLAY_CLIP_NOTE = ("replayed camera kept with its near clip at {clip:.3f} m (was {old:.3f} m): the lens stands "
                    "inside the {kind} {piece} and looks out of it, every frame ray leaves its box within {exit:.3f} m "
                    "(planar), the rest of the view lies {seen:.2f} m away or farther (docs/milestone13.md §7, fix "
                    "round after P6b)")
REPLAY_MOVED_REASON = ("the {kind} {piece} of this build {how} the replayed pose (single share {share:.2f}); moved by "
                       "the free-floor rule to the nearest free point whose view is not blocked, same yaw, pitch, "
                       "height and lens (docs/milestone13.md §7, fix round after P6b)")


def _forward_xy(position, target) -> Optional[tuple[float, float]]:
    dx, dy = float(target[0]) - float(position[0]), float(target[1]) - float(position[1])
    n = math.hypot(dx, dy)
    return (dx / n, dy / n) if n > 1e-9 else None


def lens_inside_pieces(room: dict, building: dict, position, floor_z: float,
                       forward=None) -> list[tuple[dict, float]]:
    """The built pieces of ``room`` whose box contains the lens point ``position`` (pure; fix round after P6b): the
    fitted box (``piece_bbox``) on the footprint centre, turned by the footprint rotation, from the piece's bottom
    (``mount_bottom`` over ``floor_z``) to its top; a stair (``parametric.SHELL_TYPES``) is its open parts in the model
    and never counts. ``[(piece, ahead)]`` in building order: ``ahead`` is the plan distance from the lens along
    ``forward`` (a unit plan direction, the view's) to the side of the box it leaves through (``math.inf`` without
    ``forward``)."""
    x, y, z = (float(v) for v in position[:3])
    out = []
    for f in shown_pieces(room, building):
        if f.get("type") in P.SHELL_TYPES:
            continue
        w, d, top, _ = piece_bbox(f)
        bottom = float(floor_z) + mount_bottom(f)
        if not bottom - 1e-9 <= z <= bottom + top + 1e-9:
            continue
        fp = f["footprint"]
        r = math.radians(float(fp.get("rotation_deg") or 0.0))
        c, s = math.cos(r), math.sin(r)
        dx, dy = x - float(fp["center"][0]), y - float(fp["center"][1])
        lx, ly = c * dx + s * dy, -s * dx + c * dy
        if abs(lx) > w / 2.0 + 1e-9 or abs(ly) > d / 2.0 + 1e-9:
            continue
        ahead = math.inf
        if forward is not None:
            fx, fy = c * forward[0] + s * forward[1], -s * forward[0] + c * forward[1]
            for at, half, k in ((lx, w / 2.0, fx), (ly, d / 2.0, fy)):
                if abs(k) > 1e-12:
                    ahead = min(ahead, max(0.0, (half - at) / k if k > 0 else (half + at) / -k))
        out.append((f, ahead))
    return out


def looks_out_depth(piece: dict, position, dirs: np.ndarray, floor_z: float) -> float:
    """The largest planar depth at which a ray of ``dirs`` (``_frame_rays``: planar-depth scaled, so the ray parameter
    is the planar depth) from the lens point ``position`` leaves the box of ``piece`` (pure; fix round after P6b, 23
    Oct 2026, review). The box is ``lens_inside_pieces``' (``piece_bbox`` on the footprint centre, turned by the
    footprint rotation, from ``mount_bottom`` over ``floor_z`` to its top), its depth widened to cover the fitted
    model centred or back-aligned (``furniture.fit_vertices(align="back")``: the back edge on the footprint's, so a
    model deeper than the footprint reaches further to the front). 0.0 without rays; a ray that starts outside the
    box counts from 0. The camera's near clip hides the piece over the whole frame when it is beyond this depth."""
    d = np.asarray(dirs, dtype=np.float64).reshape(-1, 3)
    if not d.size:
        return 0.0
    w, bd, top, _ = piece_bbox(piece)
    fp = piece["footprint"]
    d_fp = float(fp["size"][1]) if len(fp.get("size") or []) > 1 else bd
    y0, y1 = min(-bd / 2.0, d_fp / 2.0 - bd), max(bd / 2.0, d_fp / 2.0)
    z0 = float(floor_z) + mount_bottom(piece)
    r = math.radians(float(fp.get("rotation_deg") or 0.0))
    c, s = math.cos(r), math.sin(r)
    px, py = float(position[0]) - float(fp["center"][0]), float(position[1]) - float(fp["center"][1])
    lx, ly, lz = c * px + s * py, -s * px + c * py, float(position[2])
    ldx, ldy, ldz = c * d[:, 0] + s * d[:, 1], -s * d[:, 0] + c * d[:, 1], d[:, 2]

    def leave(o, k, lo, hi):
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.where(k > 1e-12, (hi - o) / k, np.where(k < -1e-12, (lo - o) / k, np.inf))
    t = np.minimum(np.minimum(leave(lx, ldx, -w / 2.0, w / 2.0), leave(ly, ldy, y0, y1)),
                   leave(lz, ldz, z0, z0 + top))
    t = np.where(np.isfinite(t), np.maximum(t, 0.0), 0.0)
    return float(t.max())


def _frame_rays(plan: dict, grid=None) -> tuple[np.ndarray, np.ndarray]:
    """``(directions P x 3, border mask)`` of a plan's frame (its lens, sensor, resolution and shift; any pitch)."""
    grid = grid or SCORE["grid"]
    lens = float(plan.get("lens_mm") or cameras.M5_LENS_MM)
    a, b = ray_grid(grid, lens, plan.get("sensor_mm") or SENSOR_MM, plan.get("resolution") or RESOLUTION,
                    float(plan.get("shift_x") or 0.0), float(plan.get("shift_y") or 0.0))
    return camera_directions(plan["position"], plan["target"], a, b), border_mask(grid)


def _measure_at(model: RoomModel, point, dirs: np.ndarray, border: np.ndarray, lens_mm: float) -> dict:
    labels, depth = model.cast(point, dirs)
    return model.measure(labels[None, :], depth[None, :], border, near_distance(lens_mm))[0]


def _top_element(m: dict) -> Optional[str]:
    elements = m.get("elements") or {}
    return max(sorted(elements), key=lambda k: elements[k]) if elements else None


def _keep_with_clip(plan: dict, room_id: str, clip: dict, single: float) -> dict:
    """Give a replayed plan that stays the near clip that hides the piece its lens looks out of (fix round after P6b,
    23 Oct 2026, review): ``plan["clip_start"]`` and a note in its warning; returns the ``clipped`` record."""
    piece = clip["piece"]
    note = REPLAY_CLIP_NOTE.format(clip=clip["clip_start"], old=clip["clip_start_old"], kind=piece.get("type"),
                                   piece=piece.get("id"), exit=clip["exit_m"], seen=clip["seen_m"])
    plan["clip_start"] = clip["clip_start"]
    plan["warning"] = "; ".join(w for w in (plan.get("warning"), note) if w)
    return {"name": plan.get("name"), "room_id": room_id, "status": "clipped", "trigger": "looks_out",
            "blocked_by": piece.get("id"), "blocked_by_type": piece.get("type"), "share_old": round(single, 4),
            "share": round(single, 4), "moved_m": 0.0, "clip_start": clip["clip_start"],
            "clip_start_old": clip["clip_start_old"], "exit_m": round(clip["exit_m"], 4), "warning": note}


def move_blocked_replayed(plans: Sequence[dict], building: dict) -> list[dict]:
    """Move the replayed interior cameras of ``plans`` that a piece of ``building`` blocks or contains (fix round after
    P6b, 23 Oct 2026; docs/milestone13.md §7; the rule is in the module docstring). Pure but for the plans it changes
    in place (``position``, ``target``, ``replay``, ``warning``), as ``build.repitch_replayed_aerials``. Returns one
    record per camera the rule fires on, in plan order: ``{"name", "room_id", "status": "moved" | "kept", "trigger":
    "single_share" | "inside", "blocked_by", "blocked_by_type", "share_old", "share", "moved_m", "warning"}``
    (``status: kept``: no free point within ``REPLAY_MOVE_MAX_M`` gives an unblocked view; the warning carries
    ``BLOCKED_WARNING``). Fix round after P6b (23 Oct 2026), review: a camera that stays while its lens looks out of a
    piece whose box the default clip does not hide over the frame (``looks_out_depth``) gets ``clip_start`` past it
    (``status: clipped``, ``trigger: looks_out``, with ``clip_start``, ``clip_start_old`` and ``exit_m``; a kept
    camera's record carries them too); a camera whose rest of view that clip would cut is moved as one inside the
    piece."""
    rooms = {r["id"]: r for r in building.get("rooms") or []}
    pieces = {f.get("id"): f for f in building.get("furniture") or []}
    models: dict = {}
    out: list[dict] = []
    for plan in plans or ():
        if plan.get("source") != "replayed" or plan.get("kind") not in (None, "interior") \
                or plan.get("room_id") not in rooms or plan.get("replay") or plan.get("target") is None \
                or plan.get("position") is None:
            continue
        forward = _forward_xy(plan["position"], plan["target"])
        if forward is None:
            continue                                    # a camera looking straight down has no yaw to keep
        room = rooms[plan["room_id"]]
        if len(room_polygon(room)) < 3:
            continue                                    # no room to stand in (plan_room refuses it too)
        if room["id"] not in models:
            models[room["id"]] = RoomModel(room, building)
        model = models[room["id"]]
        lens = float(plan.get("lens_mm") or cameras.M5_LENS_MM)
        pos = [float(v) for v in plan["position"][:3]]
        dirs, border = _frame_rays(plan)
        inside, looks_out = [], []
        for f, ahead in lens_inside_pieces(room, building, pos, model.floor_z, forward):
            c = f["footprint"]["center"]
            behind = (float(c[0]) - pos[0]) * forward[0] + (float(c[1]) - pos[1]) * forward[1] <= 0.0
            (looks_out if behind and ahead <= REPLAY_LOOKS_OUT_M + 1e-9 else inside).append(f)
        clip = None
        if looks_out:                                   # the frame without the pieces the lens looks out of
            gone = {f["id"] for f in looks_out}
            seen = RoomModel(room, dict(building, furniture=[f for f in building.get("furniture") or []
                                                             if f.get("id") not in gone]))
            m = _measure_at(seen, pos, dirs, border, lens)
            # fix round after P6b (23 Oct 2026), review: the near clip really used must hide those pieces over the
            # whole frame; a clip past them that would cut the rest of the view too means the lens is inside them
            old_clip = float(plan.get("clip_start") or cameras.CLIP_START_M)
            exit_m = max(looks_out_depth(f, pos, dirs, model.floor_z) for f in looks_out)
            if exit_m + REPLAY_CLIP_MARGIN_M > old_clip:
                need = math.ceil((exit_m + REPLAY_CLIP_MARGIN_M) * 1000.0 - 1e-6) / 1000.0
                if float(m["min_depth"]) > need + REPLAY_CLIP_MARGIN_M:
                    out_of = max(looks_out, key=lambda f: looks_out_depth(f, pos, dirs, model.floor_z))
                    clip = {"clip_start": need, "clip_start_old": old_clip, "exit_m": exit_m,
                            "seen_m": float(m["min_depth"]), "piece": out_of}
                else:
                    inside, looks_out, seen = inside + looks_out, [], model
                    m = _measure_at(model, pos, dirs, border, lens)
        else:
            seen = model
            m = _measure_at(seen, pos, dirs, border, lens)
        single = float(m["max_single"])
        shares = m.get("elements") or {}
        if inside:
            trigger, blocker = "inside", max(inside, key=lambda f: shares.get(f["id"], 0.0))["id"]
        elif single > SCORE["blocked_single"]:
            trigger, blocker = "single_share", _top_element(m)
        else:
            if clip is not None:                        # the pose stays: the clip that hides the piece goes with it
                out.append(_keep_with_clip(plan, room["id"], clip, single))
            continue
        piece = pieces.get(blocker) or {}
        kind = piece.get("type") or next((e["kind"] for e in seen.elements if e["id"] == blocker), "element")
        yaw = math.degrees(math.atan2(forward[1], forward[0]))
        others = []                                     # the room's other cameras: (yaw, x, y)
        for o in plans:
            fo = None if o is plan or o.get("room_id") != room["id"] or not o.get("position") \
                or o.get("target") is None else _forward_xy(o["position"], o["target"])
            if fo is not None:
                others.append((math.degrees(math.atan2(fo[1], fo[0])), float(o["position"][0]),
                               float(o["position"][1])))
        points, fallback = candidate_positions(room, building)
        best = None
        if not fallback:
            for x, y in points:
                dist = math.hypot(x - pos[0], y - pos[1])
                if dist > REPLAY_MOVE_MAX_M + 1e-9 or dist < 1e-6:
                    continue
                mm = _measure_at(model, (x, y, pos[2]), dirs, border, lens)
                if is_blocked(mm):
                    continue
                distinct = all(yaw_difference(yaw, oy) >= MIN_YAW_DIFF_DEG - 1e-9
                               or math.hypot(x - ox, y - oyy) >= MIN_DISTANCE_M - 1e-9 for oy, ox, oyy in others)
                key = (not distinct, round(dist, SCORE_DECIMALS), -round(score_terms(mm)["total"], SCORE_DECIMALS),
                       x, y)
                if best is None or key < best[0]:
                    best = (key, x, y, mm)
        how = "contains" if trigger == "inside" else "blocks"
        rec = {"name": plan.get("name"), "room_id": room["id"], "trigger": trigger, "blocked_by": blocker,
               "blocked_by_type": kind, "share_old": round(single, 4)}
        if best is None:
            why = (f"{BLOCKED_WARNING}: the {kind} {blocker} of this build {how} the replayed pose (single share "
                   f"{single:.2f}) and no free point within {REPLAY_MOVE_MAX_M:g} m of it gives an unblocked view "
                   f"(docs/milestone13.md §7, fix round after P6b)")
            plan["warning"] = "; ".join(w for w in (plan.get("warning"), why) if w)
            kept = dict(rec, status="kept", share=round(single, 4), moved_m=0.0, warning=why)
            if clip is not None:                        # fix round after P6b, review: the pose stays, so does the clip
                kept.update({k: v for k, v in _keep_with_clip(plan, room["id"], clip, single).items()
                             if k in ("clip_start", "clip_start_old", "exit_m")})
            out.append(kept)
            continue
        _key, x, y, mm = best
        dx, dy = x - pos[0], y - pos[1]
        moved = math.hypot(dx, dy)
        tgt = [float(v) for v in plan["target"][:3]]
        new_pos = [_round(x, 6), _round(y, 6), _round(pos[2], 6)]
        new_tgt = [_round(tgt[0] + dx, 6), _round(tgt[1] + dy, 6), _round(tgt[2], 6)]
        reason = REPLAY_MOVED_REASON.format(kind=kind, piece=blocker, how=how, share=single)
        plan["replay"] = {"status": "moved", "position_old": pos, "target_old": tgt, "moved_m": _round(moved),
                          "trigger": trigger, "blocked_by": blocker, "blocked_by_type": kind,
                          "share_old": _round(single), "share": _round(mm["max_single"]), "reason": reason}
        plan["position"], plan["target"] = new_pos, new_tgt
        note = (f"replayed camera moved {moved:.2f} m from ({pos[0]:.2f}, {pos[1]:.2f}) to ({x:.2f}, {y:.2f}): "
                f"{reason}")
        plan["warning"] = "; ".join(w for w in (plan.get("warning"), note) if w)
        out.append(dict(rec, status="moved", share=_round(mm["max_single"]), moved_m=_round(moved), warning=note))
    return out


def level_search_seconds(plans: Sequence[dict]) -> dict[str, float]:
    """``{level_id: search seconds}`` of searched plans (what the scene manifest records)."""
    out: dict[str, float] = {}
    for p in plans:
        if p.get("policy") == POLICY and p.get("search_seconds") is not None:
            out[p["level_id"]] = float(p["search_seconds"])
    return out


def model_shares(building: dict, camera: dict, grid=(192, 108)) -> dict[str, float]:
    """``{element id: ray share}`` the model sees from ``camera`` on a finer grid (GPU test helper)."""
    return score_camera(building, camera, grid=grid)["shares"]["elements"]


# --------------------------------------------------------------------------
# CLI (inspection)
# --------------------------------------------------------------------------

def report_md(building: dict, plans: Sequence[dict], without: Optional[Sequence[dict]] = None) -> str:
    """Markdown table of the views; ``without`` (``rooms_without_view`` rows) adds the rooms left without one."""
    rooms = {r["id"]: r for r in building["rooms"]}
    lenses = sorted({float(p.get("lens_mm") or LENS_MM) for p in plans})
    lines = [f"# Camera search: {building.get('project', {}).get('id', '?')}", "",
             f"Policy `search`: height {CAMERA_HEIGHT} m, pitch 0, shift_y {SHIFT_Y}, lens "
             f"{', '.join(f'{v:g}' for v in lenses) or f'{LENS_MM:g}'} mm; "
             f"{len(plans)} views in {len({p['room_id'] for p in plans})} rooms; search "
             + ", ".join(f"{k} {v:.1f} s" for k, v in level_search_seconds(plans).items()) + ".", "",
             "| Camera | Room | Area m2 | Lens mm | Score | Furniture | Openings | Floor | Depth | Penalties | "
             "Floor share | Near | Warning |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for p in plans:
        s = p["score"]
        area = G.polygon_area(room_polygon(rooms[p["room_id"]]))
        lines.append(f"| {p['name']} | {p['room_id']} | {area:.2f} | {float(p.get('lens_mm') or LENS_MM):g} | "
                     f"{s['total']:.3f} | {s['furniture']:.3f} | "
                     f"{s['openings']:.3f} | {s['floor']:.3f} | {s['depth']:.3f} | {s['penalties']:.3f} | "
                     f"{s['shares']['floor']:.3f} | {s['shares']['near']:.3f} | {p['warning'] or ''} |")
    if without:
        lines += ["", "Rooms without a view (docs/milestone7.md §6.2):", ""]
        lines += [f"- {r['room_id']} ({r.get('label') or '-'}, {r['area_m2']:.2f} m2): {r['reason']}" for r in without]
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m wenart.blender.camsearch", description=__doc__.split("\n\n")[0])
    ap.add_argument("building", help="building JSON (status ok)")
    ap.add_argument("--level", default=None, help="one level id (default: every level)")
    ap.add_argument("--out", required=True, help="JSON with the plans")
    ap.add_argument("--report", default=None, help="optional markdown table of the views")
    ap.add_argument("--lens-mm", type=float, default=None,
                    help="lens of every room (the brief's render.lens_mm, 14-35); default: 18 mm, 16 mm in rooms "
                         "narrower than 2.2 m")
    args = ap.parse_args(argv)
    if args.lens_mm is not None:
        try:
            cameras.check_lens(args.lens_mm)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
    building = json.loads(Path(args.building).read_text(encoding="utf-8"))
    levels = [lv["id"] for lv in building["levels"] if args.level is None or lv["id"] == args.level]
    if not levels:
        print(f"no level {args.level!r} in {args.building}", file=sys.stderr)
        return 2
    plans: list[dict] = []
    for level_id in levels:
        plans.extend(plan_level(building, level_id, args.lens_mm))
    out = {"schema_version": "0.1", "kind": "camera_search", "building": args.building, "policy": POLICY,
           "search_seconds": level_search_seconds(plans), "cameras": plans,
           "rooms_without_view": [r for level_id in levels for r in rooms_without_view(building, level_id)]}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if args.report:
        Path(args.report).write_text(report_md(building, plans, out["rooms_without_view"]), encoding="utf-8")
    blocked = [p["name"] for p in plans if p["warning"] and BLOCKED_WARNING in p["warning"]]
    print(f"{len(plans)} views, search {sum(out['search_seconds'].values()):.1f} s, blocked unavoidable: "
          f"{blocked or 'none'}, rooms without a view: {[r['room_id'] for r in out['rooms_without_view']] or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
