"""The deterministic group solver (docs/milestone12.md §4.4, contract §13.2; owner: track G).

Contract (frozen 10 Oct 2026); deterministic (same input, same output: no random, no wall clock), pure:

- ``solve_room(building: dict, room_id: str, program: dict | None = None, *, k: int = 3,
  fixed_ids: list[str] | None = None) -> list[Candidate]`` (best first, at most ``k``). ``program`` defaults to
  ``program.room_program(building, room_id)``; ``fixed_ids``: pieces that must not move (drawn pieces always are).
  ``Candidate = {"rank": int, "score": float, "terms": {name: float}, "pieces": [furniture dicts, added_by_ai],
  "groups": [{"group_id", "group", "anchor_id", "member_ids"}], "hard_failures": [], "group_violations":
  [Violation]}``.
- ``apply_candidate(building: dict, room_id: str, candidate: dict) -> dict``: a new building with the room's
  ``added_by_ai`` pieces replaced by the candidate's pieces (drawn pieces untouched), each piece carrying
  ``group = {"group_id", "group", "role": "anchor" | "partner"}``.

Extra candidate keys: ``options`` ({group_id: option}), ``placed`` / ``not_placed`` (group ids, the latter with the
reason), ``kept_ids`` (the fixed added pieces ``apply_candidate`` keeps), ``nodes`` (search effort). Each piece's
``group`` also names the group's ``anchor_id`` (a drawn anchor's id for the partners of a completed group).

What and why: the layout and the completion placed single pieces from model coordinates and repaired them one by
one (§1.2). Here whole groups (``groups.yaml``) are placed by code; the vision model only picks among the top
candidates (``layout.py``).

How (one room):

1. **Free space** (``Space``): the room on a 5 cm raster in its own axis frame (``group_checks.RoomRaster``), minus
   the fixed pieces (drawn pieces, built or not, unless recorded as not furniture or untyped and unbuilt;
   ``fixed_ids``), the door approach
   strips and swings, and, per piece height, the window bands (sill + 0.05 m; a TV unit counts with its TV, a hob
   never stands in a window band). Use zones may cover door swings but never fixed pieces or the outside. Pieces and
   zones are boxes in their own frame; their raster cells come from arithmetic (no geometry objects) and are tested
   with integral images in O(1); the exact shapely tests run once per kept group candidate.
2. **Group candidates**: wall anchors on every outline segment every 0.10 m from both ends (both chaise sides of a
   corner sofa); free anchors on a 0.10 m grid turned to the room's axes; anchors are tried best pre-score first,
   one per 0.5 m first, until ``PER_LEVEL`` x 3 candidates are found. Partners stand at their template places
   (``groups.yaml`` ``place``: a TV unit on the wall the sofa faces, centred on its axis within 0.30 m, ≥ 1.50 m
   away; the coffee table at the recommended gap first; armchairs beside the coffee table facing it; nightstands at
   the head; chairs around the table by its length, a long side without chairs only where the table touches a wall;
   ...); a required partner that does not fit drops the candidate, an optional one is left out. Sets (bathroom, WC,
   entrance) place each member on a wall as its own search level; kitchen runs lay fridge - sink - hob along an I,
   L or U path or a galley with the NKBA landings and work-triangle legs as hard limits. Drawn anchors are not moved:
   their group gets only its missing partners.
3. **Soft terms** per candidate (0..1, weights in ``groups.yaml``; names after Merrell et al. 2011 and Yu et al.
   2011): wall_use, sight_tv, bed_sees_door, desk_side_light, daylight, related_near, recommended, partners,
   drawn_distance, sink_window; per full layout circulation, seating_crossed and balance.
4. **Beam search** (``BEAM_WIDTH`` 32) over the groups in priority order (drawn anchors first); per node every kept
   candidate of the level is tried (overlap and use zones against the node's pieces on the raster, exact shapely
   tests where two pieces come within 5 cm), then the walkways are checked on the raster (every door reaches every
   door at ≥ 0.60 m and the entrance door every door at ≥ 0.80 m where the room with its fixed pieces allows it;
   every use zone reached at ≥ 0.60 m). A group that fits nowhere may be skipped (a placed required group scores
   ``REQUIRED_BONUS``, an optional one ``OPTIONAL_BONUS``). At most ``PER_PARENT`` children per node in a first pass
   (the beam keeps different earlier choices); ties break by score, then the rounded positions; near-duplicates
   (same option and turn, anchor within 0.5 m) are merged; ``NODE_BUDGET`` caps the work.
5. **Top k**: the final nodes are scored with the layout terms, verified exactly (``verify``: the placer's geometry
   and the group checks G1–G14 on the room with the new pieces; only violations the fixed pieces alone do not cause
   count as ``hard_failures``) and returned best first, diverse (the main group differs first, then any group: another
   option or turn, or an anchor ≥ 1 m away).

Milestone 13 (docs/milestone13.md §1.4, §3.0 K3, §13.2; track T3; user decision D5 of 12 Oct 2026):

- ``solve_room(..., drawn_group=None)``: a drawn group (``groups.drawn_groups`` entry or its anchor id) that is
  re-solved as one unit, besides the groups the program marks ``resolve`` itself (an anchor that is missing, misread
  or fails the checks). The group's drawn pieces are **not** obstacles (``_fixed_items`` leaves them out): the
  anchor is placed anew within ``groups.GROUP_MEMBER_MOVE_MAX_M`` (0.5 m) of its drawn centre at its drawn size (or
  the nearest real product, ``sizes.snap_size``, when the drawn size is outside the product grid), the template
  partners are laid out around it and the drawn members take the partner places nearest their drawn centres (at
  most 0.5 m away; a member no place reaches stays where it is drawn). Every moved piece is returned in the
  candidate's ``pieces`` as the drawn dict with the new footprint, ``adjusted_by_ai`` (the reason, ``moved_m``),
  ``drawn_footprint`` / ``drawn_front_deg`` / ``drawn_height`` / ``drawn_type`` kept and ``drawn_group`` =
  ``{anchor_id, members, moved_m}``; ``candidate["resolved"]`` lists their ids; ``apply_candidate`` replaces them
  in place. An unbuilt drawn anchor (``asset.method`` none) never blocks its own group and never suppresses it.
- The designer terms of ``groups.yaml`` (R3 ``conversation``, R6 ``rug``, R12 ``anchored``, R13 ``alignment``) score
  the candidates; the rug is a decor member of the seating and sleeping templates (place ``under`` the coffee table,
  ``beside`` the bed; never an obstacle; ``candidate["rugs"]``, written to ``building["decor"]`` by
  ``apply_candidate``); the tiered minimums (``groups.rule_for``: a soft aisle in a small kitchen, soft NKBA terms for
  a fridge beside a drawn run) and the room-size variants (``groups.small_room``: one bed side on the wall in a small
  bedroom) replace the fixed numbers.
- Build round 3 (K2, docs/milestone13.md §14.4 T1/T3): a drawn piece with a uniformly scaled library model is
  planned with the box the scene builder makes (``placer.planned_piece``: the fitted depth ``asset.bbox_m[1]``, the
  back edge kept for a wall-backed type), in the fixed obstacles (``Space``), as a drawn anchor the partners gather
  round (``_spot_from``: the coffee table sits ``coffee_gap`` in front of the model's real front), in the overlap
  test of ``verify`` and in its group checks (``placer.planned_building``: the clearances G1-G14 are measured on
  the fitted boxes); a re-solved drawn piece at its drawn size is planned with the fitted box too (``_planned_of``,
  ``Spot.record``) and recorded at its drawn size where the builder makes that box (``Spot.record_box``: a sofa's
  back stays on the wall). The drawn footprint stays the record everywhere.

Fix round after P4a (17 Oct 2026):

- a drawn anchor that is ``unverified`` only because code typed it (vector-drawn, ``infer.CODE_TYPE_METHODS``) is
  used as drawn and gets its partners (``program.unsure_anchor``). Why: real02's code-typed beds f_L0_019-022 got no
  candidate at all, so four bedrooms had no nightstands;
- in a re-solved drawn group the partner places of a role are searched at the drawn members' own boxes first
  (``_member_boxes``), then at the template's sizes. Why: the members take a matched place at their own box
  (``_match_members``), so a 0.45 m deep drawn nightstand on a place made for a 0.40 m one reached 2.5 cm into the
  headboard wall, failed the exact test and the whole group got no candidate (real02's YATAK beds with their drawn
  nightstands, ``infer.nightstand_symbols``: the misread 2.55 m bed then stayed as drawn).

Fix round after P4b (17 Oct 2026; pod P4b, real03). What: a drawn appliance of ``ACCESS_ZONE_TYPES`` (a washing
machine) whose drawn front opens out of the room (less than ``ACCESS_INSIDE_SHARE`` of its use zone in front lies in
the room: the drawing turned it towards a wall) keeps a use zone free on the one other side that opens into the room
(``access_zone``: at least that share inside, off every other drawn piece; the part inside the room, named
``access``). No added piece stands there and the walkways keep reaching it. With no such side, or more than one,
nothing is reserved (the side is unclear). The drawn piece is not changed (fixed equipment, CLAUDE.md). Why: real03's
4 entrance halls each end in a 0.45 m strip with a drawn washer whose block faces the strip's wall; its only open
side is the strip, and the completion put a 0.9 m console there, 0.11-0.26 m in front of the door of the machine
(the agent later turned the washers to face the strip, onto the console). A front clearance in the clearance table
would not have stopped it: the drawn front looks at the wall.

Fix round after P6a (22 Oct 2026; pod P6a, real04). What: under the roof the solver keeps headroom. ``Space`` reads
the level's sloped ceiling (``decor.ceiling_planes``: the layout and fit buildings carry no
``level["ceiling_planes"]``, only the scene builder's prepared building does) and computes the ceiling height over
every raster cell. A piece the solver places needs ``group_checks.effective_height`` of its type plus
``HEADROOM_MARGIN_M`` (0.05 m) under the ceiling over its whole footprint: the raster layer of its type blocks the
lower cells (``layer_for``) and the exact test reads the ceiling at the footprint's corners (``exact_ok``; the
planes are linear, so the lowest point of a footprint is a corner). A re-solved drawn piece is never asked for more
than its drawn place gives (less ``DRAWN_HEADROOM_TOL_M``): it may stay where it is drawn and is not moved lower.
Under a flat ceiling (no roof over the level) nothing changes. The same need is checked for the added pieces a twin
room copies (``complete.copy_added``: ``headroom_short``). Why: the completion put two 1.8 m bookshelves
(f_L1_048, f_L1_056) and a 0.8 m console table (f_L1_049) where the slope is 0.82 m high; the built models went
through the roof (critical X2 in every agent round, also in P5) and the agent could fix only one of the twins.

Fix round after P6b (23 Oct 2026), review (the integration's ask). What: a front partner (``place: front``: the
coffee table) takes the first of its (size, gap) options, sizes first and then the gaps (groups.yaml: 1.2 x 0.7,
1.0 x 0.6, 0.8 x 0.5 at 0.40, 0.35 and 0.30 m, the ``coffee_gap`` rule), that fits locally, as before. When no
candidate of the room passes the final check (``verify``'s hard failures, or nothing placed), ``solve_room`` searches
again with the front partners starting at the option after the one they took (``Space.front_from``,
``Space.front_chosen``), until a candidate passes or no option is left; a solve with a passing candidate is not
searched again, so its placements do not change, and when no option passes the first search's candidates are
returned (with their refusal). The candidates of a repeated search carry ``front_from``. Why: on P4a's real02 (the
data P6c replays) complete_group of the drawn sofa f_L-1b_041 took a 1.2 x 0.7 table at the 0.40 m gap, which cut
the kitchen island's walkway (G11), and the group got no candidate; a smaller table at a smaller gap clears its F3
and G2 with no new finding.

Fix round of 26 Oct 2026 (user: "a kitchen must never be empty"; "fix should be general, it is not a fix for real06").
What: (1) an untyped drawn piece the reading left unbuilt (``untyped_unbuilt``: ``type`` unknown, ``build: false``)
is no fixed obstacle (``_fixed_items``): it is in no render; (2) the kitchen legs stand on the outline with its jogs
under ``JOG_M`` (0.15 m) merged onto the inner wall line (``run_outline``), so a plaster step no longer splits a wall
or breaks a real corner; (3) when no option of the program fits, ``run_candidates`` tries the compact fallback runs of
``groups.yaml`` (``fallback: true``: an I from 2.1 m, an L with 0.9 m legs, a galley of 1.35 + 0.6 m; a 0.60 m tall
fridge unit, a 0.60 or 0.45 m sink and hob, 0.30 m base units between; the run's ``compact`` limits,
``run_limits``; the work triangle and the NKBA landings are scored and reported as minor by the ``compact_run``
tier), and ``solve_room`` searches once more with only those runs when the program's run was generated but no
passing candidate places it (``run_left_out``; the candidates carry ``compact_fallback``). A room that holds a full
run keeps it: the compact runs are never tried beside one. A kitchen that still gets no run is a critical finding of
the layout (``layout.empty_kitchens``) and G9 is critical for a kitchen without any run piece. Why: real06's 24.8 m²
kitchen (a stair, an untyped 3.99 x 2.40 m unbuilt drawn piece over two walls, a 4.6 cm jog in its back wall, free
stretches of 2.2, 2.0 and 1.75 m) got "no candidate position fits the room" and rendered empty.

Bathroom sense of 26 Oct 2026 (``groups`` module docstring): a set member whose type a kept piece of the room holds
(``groups.held_types`` of the fixed pieces: drawn ones, the added ones the solver keeps) is that member, whatever the
entry lists: never placed a second time. A fixture hung at its working top is a fixed obstacle and a floor piece of the
checks (``schemas.off_floor``); the entrance of the walkways is no bare gap the drawing blocks with fixed equipment
(``group_checks.blocked_gaps``). Why: real06's upper bathroom got a third washbasin beside its two drawn ones.
"""
from __future__ import annotations

import copy
import math
import re
from dataclasses import dataclass, field
from typing import Iterable, Optional

import numpy as np
from shapely.geometry import LineString, Point, Polygon

from wenart import geometry as G
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import placer, schemas
from wenart.furniture import program as PR

BEAM_WIDTH = 32
PER_LEVEL = 40                 # group candidates of one level kept after the free-space checks
PER_PARENT = 4                 # children per beam node in the first pass
ANCHOR_TRIES = 900             # anchor positions tried per group (best pre-score first)
OPTION_GENERATE_MIN = 300      # 23 Oct 2026: the least anchor positions an option is generated at (group options 10x)
NODE_BUDGET = 60000            # anchor positions generated / candidate expansions per room
# 23 Oct 2026 (group options 10x): the anchor positions generated per room (2.5 x NODE_BUDGET: ten times the
# options; each group and option gets its share, ``anchored_candidates``); the expansions stay at NODE_BUDGET.
GENERATE_BUDGET = 150000
GRID_M = 0.10
REQUIRED_BONUS = 10.0
OPTIONAL_BONUS = 3.0
MERGE_M = 0.5                  # same option and turn, anchor within this: one candidate (the better one)
DIVERSE_M = 1.0                # the top k differ by an option, a turn or an anchor this far apart
ZONE_INFLATE_M = 0.02          # use zones are tested 2 cm larger on the raster (sub-cell safety)
FIXED_ZONE_INFLATE_M = -0.03   # a drawn piece's zone is tested 3 cm smaller: it touches the piece's own cells
# Fix round after P4b (module docstring): drawn appliances whose use zone is kept free on their open side when the
# drawn front opens out of the room.
ACCESS_ZONE_TYPES: tuple[str, ...] = ("washing_machine",)
ACCESS_INSIDE_SHARE = 0.5      # a use zone with less than this share inside the room opens out of it
CLOSE_M = 0.05                 # pieces closer than this get an exact shapely overlap test
HEADROOM_MARGIN_M = 0.05       # fix round after P6a: a placed piece's height stays this far under a sloped ceiling
DRAWN_HEADROOM_TOL_M = 0.05    # ... a re-solved drawn piece: at most this lower than its drawn place (box shifts)
GAP = placer.SNAP_GAP_M        # back edge to wall face
EVIDENCE_FILE = "building.json"
SINK_WINDOW_M = 0.4


# --------------------------------------------------------------------------
# Pieces and boxes
# --------------------------------------------------------------------------

@dataclass
class Spot:
    """One piece of a group candidate (world frame; the block frame of ``schemas``)."""
    type: str
    center: tuple
    rotation: float
    size: tuple
    role: str
    against_wall: bool = False
    shape: Optional[str] = None
    chaise_side: Optional[str] = None
    existing_id: Optional[str] = None          # a drawn (or fixed) piece used as the anchor: not new
    # Milestone 13: a re-solved drawn piece (``drawn``: its building dict) and how far it moved; ``kept``: a drawn
    # member no partner place reaches, left where it is drawn (its cells count, its own checks are not run again).
    drawn: Optional[dict] = None
    moved: float = 0.0
    kept: bool = False
    # Milestone 13 (K2, build round 3): a re-solved drawn piece with a uniform library fit is planned with the box the
    # scene builder makes (this spot's ``size`` / ``center``); ``record`` = (drawn size, offset of that box's centre
    # from the drawn centre in the piece frame) says what the building records (``record_box``). None: the spot's
    # box is the record.
    record: Optional[tuple] = None

    def record_box(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """``(centre, size)`` the building records for this spot: its own box, or for a planned re-solved piece
        (``record``) the drawn size at the place that gives this spot's box when the builder fits the model."""
        if self.record is None:
            return (float(self.center[0]), float(self.center[1])), (float(self.size[0]), float(self.size[1]))
        size, offset = self.record
        return _record_centre(self.center, self.rotation, offset), (float(size[0]), float(size[1]))

    def piece(self) -> placer.Piece:
        extra = {}
        if self.shape == "L":
            extra = {"shape": "L", "chaise_side": self.chaise_side, "chaise_depth": float(self.size[1]),
                     "seat_depth": schemas.L_SEAT_DEPTH_M, "chaise_width": schemas.L_CHAISE_WIDTH_M}
        return placer.Piece(self.type, (float(self.center[0]), float(self.center[1])), float(self.rotation),
                            (float(self.size[0]), float(self.size[1])), self.against_wall, **extra)

    def boxes(self) -> list[tuple]:
        """Its footprint as boxes ``(x0, x1, y0, y1)`` in its own frame (two for a corner sofa)."""
        if self.shape == "L":
            return [tuple(b) for b in schemas.l_parts(self.size, self.chaise_side, float(self.size[1]),
                                                      schemas.L_SEAT_DEPTH_M, schemas.L_CHAISE_WIDTH_M)]
        w, d = float(self.size[0]) / 2.0, float(self.size[1]) / 2.0
        return [(-w, w, -d, d)]

    def zones(self, rec: bool = False, overrides: Optional[dict] = None) -> list[tuple]:
        """Its use zones ``(name, centre, rotation, box)`` (``overrides``: the room's tier minimums, Milestone 13)."""
        return [(name, self.center, self.rotation, box) for name, box in GC.use_zone_boxes(
            self.size, self.type, self.shape, self.chaise_side, float(self.size[1]), rec, overrides)]

    def world(self, local) -> tuple[float, float]:
        r = math.radians(self.rotation)
        c, s = math.cos(r), math.sin(r)
        return (self.center[0] + local[0] * c - local[1] * s, self.center[1] + local[0] * s + local[1] * c)


def _spot_from(f: dict, role: str = "anchor") -> Spot:
    """A drawn piece as a spot that is not placed again (``existing_id``): a drawn anchor the partners gather round,
    a kept member, a skipped re-solve. Milestone 13 (K2, build round 3): its box is the one the scene builder makes
    (``placer.planned_piece``: a uniformly scaled library model keeps its back edge and is deeper or shallower at
    the front), so the partners and the clearances are planned where the model really ends; the drawn footprint
    stays the record (a kept member comes back as its drawn dict, ``_resolved_dict``)."""
    p = placer.planned_piece(f)
    return Spot(f["type"], p.center, p.rotation_deg, p.size, role, False, p.shape, p.chaise_side, existing_id=f["id"])


def _planned_of(drawn: dict) -> Optional[tuple[tuple, tuple, tuple]]:
    """Milestone 13 (K2, build round 3): ``(drawn size, planned size, offset)`` of a drawn piece whose uniform library
    fit is deeper or shallower than its drawing (``placer.drawn_piece`` carries the planned box), in the piece's
    front frame; ``offset`` is the planned centre minus the drawn centre in that frame (a wall-backed piece keeps
    its back edge, so its box centre moves towards the front). None for every other piece (it plans as drawn)."""
    try:
        p = placer.drawn_piece(drawn)
    except (KeyError, TypeError, ValueError):
        return None
    if p.planned_size is None or p.planned_center is None:
        return None
    dx, dy = p.planned_center[0] - p.center[0], p.planned_center[1] - p.center[1]
    r = math.radians(p.rotation_deg)
    c, s = math.cos(r), math.sin(r)
    return p.size, p.planned_size, (dx * c + dy * s, -dx * s + dy * c)


def _record_centre(center, rotation: float, offset) -> tuple[float, float]:
    """The recorded (drawn-size) centre of a planned box at ``center`` turned by ``rotation``: the box centre minus
    the fit's ``offset`` (``_planned_of``) turned with the piece."""
    r = math.radians(rotation)
    c, s = math.cos(r), math.sin(r)
    ox, oy = float(offset[0]), float(offset[1])
    return float(center[0]) - (ox * c - oy * s), float(center[1]) - (ox * s + oy * c)


def _planned_centre(center, rotation: float, offset) -> tuple[float, float]:
    """The inverse of ``_record_centre``: the planned box centre of a piece recorded at ``center``."""
    r = math.radians(rotation)
    c, s = math.cos(r), math.sin(r)
    ox, oy = float(offset[0]), float(offset[1])
    return float(center[0]) + (ox * c - oy * s), float(center[1]) + (ox * s + oy * c)


def _same_size(a, b, tol: float = 1e-4) -> bool:
    return abs(float(a[0]) - float(b[0])) <= tol and abs(float(a[1]) - float(b[1])) <= tol


def _local_spot(anchor: Spot, ftype: str, local, turn: float, size, role: str, wall: bool = False) -> Spot:
    c = anchor.world(local)
    return Spot(ftype, (round(c[0], 4), round(c[1], 4)), G.normalise_angle(anchor.rotation + turn),
                (float(size[0]), float(size[1])), role, wall)


@dataclass
class Cand:
    """A group candidate: its new spots, use zones (boxes that stay free), soft terms and raster footprints."""
    level: int
    group_id: str
    group: str
    option: str
    anchor: Spot
    spots: list                        # new spots (the anchor first when it is new)
    zones: list                        # [(name, centre, rotation, box)]
    terms: dict
    local: float = 0.0
    sig: tuple = ()
    fps: list = field(default_factory=list)
    zfps: list = field(default_factory=list)
    rfps: list = field(default_factory=list)       # the zones a person walks into (reached by a walkway)
    polys: list = field(default_factory=list)
    bboxes: list = field(default_factory=list)
    rugs: list = field(default_factory=list)       # Milestone 13: decor members (rug spots), never obstacles
    resolve: Optional[dict] = None                 # Milestone 13: {anchor_id, members, reason} of a re-solved group


def _reached(zone) -> bool:
    """A use zone a person walks into (a side clearance beside a toilet or washbasin, a sofa's view of its TV and a
    drawn table's pull-out room are kept free, not walked into)."""
    return not str(zone[0]).startswith(("side_", "sight", "pullout_drawn"))


# --------------------------------------------------------------------------
# Free space
# --------------------------------------------------------------------------

def _integral(mask: np.ndarray) -> np.ndarray:
    s = np.zeros((mask.shape[0] + 1, mask.shape[1] + 1), dtype=np.int32)
    s[1:, 1:] = mask.astype(np.int32).cumsum(0).cumsum(1)
    return s


class Layer:
    """A blocked-cell mask with its integral image."""

    def __init__(self, mask: np.ndarray):
        self.mask = mask
        self.s = _integral(mask)

    def hit(self, fp) -> bool:
        if fp[0] == "r":
            _k, j0, j1, i0, i1 = fp
            if j1 <= j0 or i1 <= i0:
                return True
            s = self.s
            return int(s[j1, i1] - s[j0, i1] - s[j1, i0] + s[j0, i0]) > 0
        idx = fp[1]
        return idx.size == 0 or bool(self.mask.ravel()[idx].any())


def paint(mask: np.ndarray, fp) -> None:
    if fp[0] == "r":
        _k, j0, j1, i0, i1 = fp
        if j1 > j0 and i1 > i0:
            mask[j0:j1, i0:i1] = True
    else:
        mask.ravel()[fp[1]] = True


def _close(a, b, m: float = CLOSE_M) -> bool:
    return not (a[2] + m < b[0] or b[2] + m < a[0] or a[3] + m < b[1] or b[3] + m < a[1])


# --------------------------------------------------------------------------
# Headroom under a sloped ceiling (fix round after P6a, module docstring)
# --------------------------------------------------------------------------

def headroom_planes(building: dict, level_id: str) -> list:
    """The level's sloped ceiling planes ``[a, b, c]`` (z = a x + b y + c, world), as the scene builder makes them
    (the rule of ``decor.ceiling_planes``), or [] under a flat ceiling.

    Integration of the fix round after P6a (23 Oct 2026): read through ``fit.ceiling_planes_of`` (the same
    ``roof.roof_model`` + ``roof.ceiling_planes`` calls; the planes are asserted equal in
    ``tests/test_m13_p6a_integration.py``), not ``decor``: the stages that reach the solver (sheets, pipeline) list
    ``fit.py`` in their code (``stages.GROUPS_CODE``) but not ``decor.py``, so a decor import would leave their
    fingerprints blind to it (``tests/test_run_stages.py::test_code_lists_cover_the_import_closure``)."""
    from wenart.furniture import fit as F             # lazy: fit reaches the solver through edit_ops

    return F.ceiling_planes_of(building, level_id)


def ceiling_over_polygon(planes: list, floor_z: float, poly) -> float:
    """The lowest ceiling height above the floor over a footprint polygon: the planes are linear, so their lowest
    point over the footprint is one of its corners."""
    pts = [(float(x), float(y)) for part in placer.polygon_parts(poly) for x, y in part.exterior.coords]
    return round(min(min(float(p[0]) * x + float(p[1]) * y + float(p[2]) for p in planes) for x, y in pts)
                 - float(floor_z), 4)


def headroom_short(building: dict, level_id: str, ftype: str, poly, planes: Optional[list] = None
                   ) -> Optional[str]:
    """Why a piece of ``ftype`` on ``poly`` lacks headroom under the level's sloped ceiling (its type's effective
    height plus ``HEADROOM_MARGIN_M`` over the ceiling at its lowest corner), or None (it fits, or the ceiling is
    flat). The check of ``Space`` for pieces placed outside the solver (``complete.copy_added``)."""
    planes = headroom_planes(building, level_id) if planes is None else planes
    if not planes:
        return None
    floor_z = float(next((lv.get("elevation") for lv in building.get("levels") or [] if lv.get("id") == level_id),
                         0.0) or 0.0)
    here = ceiling_over_polygon(planes, floor_z, poly)
    need = GC.effective_height({"type": ftype}) + HEADROOM_MARGIN_M
    if here < need - 1e-9:
        return (f"the sloped ceiling over it is {here:.2f} m high, a {ftype} needs {need:.2f} m "
                f"({GC.effective_height({'type': ftype}):.2f} m + {HEADROOM_MARGIN_M:g} m)")
    return None


class Space:
    """The room's free space for the solver (see the module docstring, step 1)."""

    def __init__(self, building: dict, room: dict, fixed: list[dict]):
        self.building, self.room = building, room
        self.ctx = placer.room_context(building, room)
        self.R = GC.RoomRaster(self.ctx.polygon)
        R = self.R
        self.fixed_items = fixed
        self.fixed_pieces = []
        for i, f in enumerate(fixed):
            try:
                # Milestone 13 (K2, build round 3): the box the scene builder makes (a uniformly scaled library
                # model is deeper or shallower at its front; ``placer.planned_piece``), so the collisions, the
                # fixed zones and the free cells are planned where the model really ends.
                self.fixed_pieces.append(placer.planned_piece(f, i))
            except (KeyError, TypeError, ValueError):
                continue
        self.fixed_polys = [p.polygon() for p in self.fixed_pieces]
        self.fixed_bounds = [p.bounds for p in self.fixed_polys]
        self.shrunk_tol = self.ctx.shrunk.buffer(1e-3, join_style="mitre")
        fixed_mask = np.zeros_like(R.inside)
        for poly in self.fixed_polys:
            fixed_mask |= R.polygon_mask(poly)
        self.fixed_mask = fixed_mask
        door_mask = np.zeros_like(R.inside)
        for door in self.ctx.doors:
            for geom in (door.zone, door.swing):
                if geom is not None and not geom.is_empty:
                    door_mask |= R.polygon_mask(geom)
        self.door_mask = door_mask
        self.inside_shrunk = R.polygon_mask(self.ctx.shrunk)
        self.windows = [(w, R.polygon_mask(w.band)) for w in self.ctx.windows]
        self.base = ~self.inside_shrunk | fixed_mask | door_mask
        self.zone_layer = Layer(~R.inside | fixed_mask)
        self._layers: dict = {}
        self.area = float(room.get("area_computed") or self.ctx.polygon.area)
        self.centroid = (self.ctx.polygon.centroid.x, self.ctx.polygon.centroid.y)
        self.doors_by_id = {d["id"]: d for d in placer.room_openings(building, room)[0]}
        self.kind = PR.room_kind(building, room)          # Milestone 13: the aliased room type
        # Milestone 13: the room's tier minimums (a small kitchen's soft aisle, a drawn run's soft NKBA terms).
        self.overrides = GC.tier_overrides_of(building, room, fixed)
        self._allowed_room = GC.allowed_types_at(building, dict(room, zones=[]), None)
        self._zones = [(Polygon(z["polygon"]).buffer(0.05), GC.allowed_types_at(building, dict(room, zones=[z]), None))
                       for z in room.get("zones") or [] if len(z.get("polygon") or []) >= 3]
        self.margin = GR.rule("window_band")["sill_margin"]
        # Fix round after P6a (module docstring): the sloped ceiling under the roof, as the scene builder makes it
        # (``decor.ceiling_planes``; [] under a flat ceiling), and its height above the floor over every raster cell.
        self.planes, self.headroom = headroom_planes(building, room["level_id"]), None
        self.floor_z = float(next((lv.get("elevation") for lv in building.get("levels") or []
                                   if lv.get("id") == room["level_id"]), 0.0) or 0.0)
        if self.planes:
            c, s = R._c, -R._s                     # RoomRaster.world, on the arrays of cell centres
            X = R.cx * c - R.cy * s + R.origin[0]
            Y = R.cx * s + R.cy * c + R.origin[1]
            self.headroom = np.min([float(p[0]) * X + float(p[1]) * Y + float(p[2]) for p in self.planes],
                                   axis=0) - self.floor_z
        self._drawn_here: dict = {}
        # Fix round after P6b (23 Oct 2026), review (module docstring): the first (size, gap) option a front partner
        # (the coffee table) may take this search, and the options the search took (``solve_room`` tries the next
        # ones when no candidate passes the final check).
        self.front_from = 0
        self.front_chosen: list[int] = []

    # ----- headroom under a sloped ceiling (fix round after P6a) ----------------------------------------------------

    def ceiling_over(self, poly) -> float:
        """The ceiling height above the floor over ``poly`` (its lowest corner; inf under a flat ceiling)."""
        if not self.planes:
            return math.inf
        return ceiling_over_polygon(self.planes, self.floor_z, poly)

    def need_height(self, spot: Spot) -> Optional[float]:
        """The ceiling height a spot needs over its footprint (None under a flat ceiling): its type's effective
        height plus ``HEADROOM_MARGIN_M``; a re-solved drawn piece at most what its drawn place gives (less
        ``DRAWN_HEADROOM_TOL_M``), so it may stay where it is drawn."""
        if self.headroom is None:
            return None
        need = GC.effective_height({"type": spot.type}) + HEADROOM_MARGIN_M
        if spot.drawn is not None:
            pid = spot.drawn.get("id")
            if pid not in self._drawn_here:
                try:
                    self._drawn_here[pid] = self.ceiling_over(placer.planned_piece(spot.drawn).polygon())
                except (KeyError, TypeError, ValueError):
                    self._drawn_here[pid] = math.inf
            need = min(need, self._drawn_here[pid] - DRAWN_HEADROOM_TOL_M)
        return round(need, 3)

    # ----- what may stand where -------------------------------------------------------------------------------------

    def allowed(self, ftype: str, point) -> bool:
        """``group_checks.allowed_types_at`` (cached): the room's types, plus a zone's types at a point inside it
        (anywhere in a zone when ``point`` is None)."""
        if ftype in self._allowed_room:
            return True
        for poly, types in self._zones:
            if ftype in types and (point is None or poly.contains(Point(point))):
                return True
        return False

    def layer_for(self, ftype: str, need: Optional[float] = None) -> Layer:
        """Blocked cells for a piece of ``ftype``: outside, fixed, doors, and the window bands its height reaches;
        fix round after P6a: under a sloped ceiling also the cells lower than ``need`` (default: the type's
        effective height plus ``HEADROOM_MARGIN_M``; ``need_height``)."""
        h = GC.effective_height({"type": ftype})
        if self.headroom is not None and need is None:
            need = round(h + HEADROOM_MARGIN_M, 3)
        key = (round(h, 3), ftype == "stove", None if self.headroom is None else round(float(need), 3))
        if key not in self._layers:
            mask = self.base.copy()
            for win, band in self.windows:
                if ftype == "stove" or h > win.sill + self.margin + 1e-9:
                    mask |= band
            if key[2] is not None:
                mask |= self.headroom < key[2] - 1e-9
            self._layers[key] = Layer(mask)
        return self._layers[key]

    def exact_ok(self, spot: Spot, poly: Polygon) -> bool:
        """The exact (shapely) tests the 5 cm raster may miss by less than a cell: inside the room shrunk by 2 cm, off
        every fixed piece, door strip and swing, and (for its height) off every window band."""
        if not self.shrunk_tol.contains(poly):
            return False
        b = poly.bounds
        for q, qb in zip(self.fixed_polys, self.fixed_bounds):
            if _close(b, qb, 0.0) and poly.intersection(q).area > placer.AREA_EPS:
                return False
        for door in self.ctx.doors:
            for geom in (door.zone, door.swing):
                if geom is not None and not geom.is_empty and poly.intersection(geom).area > placer.AREA_EPS:
                    return False
        h = GC.effective_height({"type": spot.type})
        for win, _band in self.windows:
            if (spot.type == "stove" or h > win.sill + self.margin + 1e-9) and \
                    poly.intersection(win.band).area > placer.AREA_EPS:
                return False
        need = self.need_height(spot)               # fix round after P6a: headroom under a sloped ceiling
        if need is not None and self.ceiling_over(poly) < need - 1e-9:
            return False
        return True

    # ----- raster footprints ---------------------------------------------------------------------------------------

    def _rect(self, X0: float, X1: float, Y0: float, Y1: float):
        R = self.R
        i0 = int(math.ceil((X0 - R.x0) / R.res - 0.5 - 1e-9))
        i1 = int(math.floor((X1 - R.x0) / R.res - 0.5 + 1e-9)) + 1
        j0 = int(math.ceil((Y0 - R.y0) / R.res - 0.5 - 1e-9))
        j1 = int(math.floor((Y1 - R.y0) / R.res - 0.5 + 1e-9)) + 1
        if i1 <= i0:                           # thinner than a cell: the cell under its centre line
            i0 = int(math.floor(((X0 + X1) / 2.0 - R.x0) / R.res))
            i1 = i0 + 1
        if j1 <= j0:
            j0 = int(math.floor(((Y0 + Y1) / 2.0 - R.y0) / R.res))
            j1 = j0 + 1
        if i0 < 0 or j0 < 0 or i1 > R.nx or j1 > R.ny:
            return ("r", 0, 0, 0, 0)           # leaves the raster: outside the room
        return ("r", j0, j1, i0, i1)

    def box_fp(self, center, rotation: float, box, inflate: float = 0.0):
        """Raster cells of a box ``(x0, x1, y0, y1)`` in the frame (``center``, ``rotation``): a rectangle of cells
        when it lies along the raster axes (arithmetic only), else the cells of its polygon."""
        x0, x1, y0, y1 = box[0] - inflate, box[1] + inflate, box[2] - inflate, box[3] + inflate
        R = self.R
        phi = (float(rotation) - R.angle) % 360.0
        q = int(round(phi / 90.0))
        if abs(phi - 90.0 * q) < 0.5:
            CX, CY = R.local(center)
            q %= 4
            if q == 0:
                return self._rect(CX + x0, CX + x1, CY + y0, CY + y1)
            if q == 1:
                return self._rect(CX - y1, CX - y0, CY + x0, CY + x1)
            if q == 2:
                return self._rect(CX - x1, CX - x0, CY - y1, CY - y0)
            return self._rect(CX + y0, CX + y1, CY - x1, CY - x0)
        poly = placer._local_box(center, rotation, x0, x1, y0, y1)
        return ("m", np.flatnonzero(R.polygon_mask(poly)))

    def spot_fps(self, spot: Spot) -> list:
        return [self.box_fp(spot.center, spot.rotation, b) for b in spot.boxes()]

    def zone_fp(self, zone, inflate: float = ZONE_INFLATE_M):
        _name, center, rotation, box = zone
        return self.box_fp(center, rotation, box, inflate)

    def rect_idx(self, fp) -> np.ndarray:
        _k, j0, j1, i0, i1 = fp
        if j1 <= j0 or i1 <= i0:
            return np.zeros(0, dtype=np.int64)
        jj, ii = np.meshgrid(np.arange(j0, j1), np.arange(i0, i1), indexing="ij")
        return (jj * self.R.nx + ii).ravel()

    def overlap(self, a, b) -> bool:
        if a[0] == "r" and b[0] == "r":
            return a[1] < b[2] and b[1] < a[2] and a[3] < b[4] and b[3] < a[4]
        ia = a[1] if a[0] == "m" else self.rect_idx(a)
        ib = b[1] if b[0] == "m" else self.rect_idx(b)
        return bool(np.intersect1d(ia, ib).size)

    def spot_free(self, spot: Spot, fps=None) -> bool:
        """The spot's cells are free for its type (raster only; under a sloped ceiling with its ``need_height``)."""
        layer = self.layer_for(spot.type, self.need_height(spot))
        return not any(layer.hit(fp) for fp in (fps or self.spot_fps(spot)))

    def zones_free(self, zones) -> bool:
        return not any(self.zone_layer.hit(self.zone_fp(z)) for z in zones)


# --------------------------------------------------------------------------
# Candidate checks against the free space
# --------------------------------------------------------------------------

def _finish(space: Space, cand: Cand) -> bool:
    """Footprints of the new spots and zones; True when every spot passes its layer and the exact tests, the spots
    do not overlap each other and every zone is inside the room and off the fixed pieces. A ``kept`` drawn member
    (Milestone 13) only counts as occupied and must not overlap the other spots; a rug member is dropped (not
    rejected) when it leaves the room or lies on a door strip or swing."""
    cand.fps, cand.zfps, cand.rfps, cand.polys, cand.bboxes = [], [], [], [], []
    for s in cand.spots:
        fps = space.spot_fps(s)
        poly = s.piece().polygon()
        if not s.kept:
            if not space.spot_free(s, fps):
                return False
            if not space.exact_ok(s, poly):
                return False
        cand.fps += fps
        cand.polys.append(poly)
        cand.bboxes.append(poly.bounds)
    cand.rugs = [r for r in cand.rugs if _rug_ok(space, r)]
    for i in range(len(cand.spots)):
        for j in range(i + 1, len(cand.spots)):
            if _close(cand.bboxes[i], cand.bboxes[j], 0.0) and \
                    cand.polys[i].intersection(cand.polys[j]).area > placer.AREA_EPS:
                return False
    for z in cand.zones:
        zfp = space.zone_fp(z)
        if space.zone_layer.hit(zfp):
            return False
        cand.zfps.append(zfp)
        if _reached(z):
            cand.rfps.append(zfp)
    return True


def _rug_ok(space: Space, rug: Spot) -> bool:
    """A rug lies inside the room (shrunk) and off every door strip and swing (it is never an obstacle)."""
    poly = rug.piece().polygon()
    if not space.shrunk_tol.contains(poly):
        return False
    for door in space.ctx.doors:
        for geom in (door.zone, door.swing):
            if geom is not None and not geom.is_empty and poly.intersection(geom).area > placer.AREA_EPS:
                return False
    return True


def _fits(space: Space, spot: Spot, others: list, zones=()) -> bool:
    """A partner spot on free cells for its type, off the group's other spots (raster), its zones free, its type
    allowed where it stands."""
    fps = space.spot_fps(spot)
    if not space.spot_free(spot, fps):
        return False
    if any(space.overlap(a, b) for a in fps for b in others):
        return False
    if zones and not space.zones_free(zones):
        return False
    return space.allowed(spot.type, spot.center)


# --------------------------------------------------------------------------
# Soft terms of one group candidate
# --------------------------------------------------------------------------

def _term_daylight(space: Space, p) -> float:
    if not space.ctx.windows:
        return 0.0
    d = min(G.distance(p, w.inner_point) for w in space.ctx.windows)
    return round(max(0.0, 1.0 - d / 4.0), 4)


def _term_desk_light(space: Space, desk: Spot) -> float:
    if not space.ctx.windows:
        return 0.3
    front = G.front_direction_deg(desk.rotation)
    best = 0.0
    for w in space.ctx.windows:
        pt = w.inner_point
        ang = G.angle_difference_deg(math.degrees(math.atan2(pt[1] - desk.center[1], pt[0] - desk.center[0])), front)
        best = max(best, 1.0 if 50.0 <= ang <= 130.0 else 0.6 if ang < 50.0 else 0.1)
    return best


def _term_bed_door(space: Space, bed: Spot, entrance: Optional[str]) -> float:
    doors = [d for d in space.ctx.doors if entrance is None or d.id == entrance] or space.ctx.doors
    if not doors:
        return 0.5
    p = bed.piece()
    w, d = p.size[0] / 2.0, p.size[1] / 2.0
    lx, ly = GC.to_local(p, doors[0].inner_point)
    if ly >= d - 0.3:
        return 0.2                                   # behind or beside the headboard: not seen from the bed
    if abs(lx) <= w and ly < -d:
        return 0.6                                   # straight beyond the foot
    return 1.0


def _term_sight(anchor: Spot, tv: Optional[Spot]) -> float:
    if tv is None:
        return 0.0
    geo = GC.tv_geometry(anchor.piece(), tv.piece())
    rule = GR.rule("tv_distance")
    lo, hi = (f * rule["screen_diagonal"] for f in rule["rec_factor"])
    dev = 0.0 if lo <= geo["distance_m"] <= hi else min(abs(geo["distance_m"] - lo), abs(geo["distance_m"] - hi))
    return round(max(0.0, 1.0 - dev) * (1.0 - geo["axis_offset_m"] / 0.6), 4)


def _term_recommended(space: Space, spot: Spot) -> Optional[float]:
    rec = spot.zones(rec=True, overrides=space.overrides)
    if not rec:
        return None
    ok = sum(1 for z in rec if not space.zone_layer.hit(space.zone_fp(z, 0.0)))
    return round(ok / len(rec), 4)


# Milestone 13 (T3): the designer terms R3, R12, R13 of groups.yaml (rules conversation_circle, floating, alignment).

def _seat_fronts(anchor: Spot, seats: list[Spot]) -> list[tuple[tuple[float, float], float]]:
    """``(front midpoint, front direction)`` of the sofa and every armchair of a seating group."""
    out = []
    for s in [anchor] + seats:
        p = s.piece()
        if p.shape == "L":
            x0, x1, yf = schemas.l_seat_front(p.size, p.chaise_side, p.chaise_depth, p.seat_depth, p.chaise_width)
            mid = s.world(((x0 + x1) / 2.0, yf))
        else:
            mid = s.world((0.0, -s.size[1] / 2.0))
        out.append((mid, G.front_direction_deg(s.rotation)))
    return out


def _term_conversation(anchor: Spot, armchairs: list[Spot]) -> Optional[float]:
    """R3: the seats form a conversation circle ``conversation_circle.min..max`` across (the widest seat-front
    distance; 1.0 inside the range, falling to 0 one metre outside it) and every seat faces the group's centre
    within ``facing_deg``. None without armchairs (a sofa alone is no circle)."""
    if not armchairs:
        return None
    rule = GR.rule("conversation_circle")
    fronts = _seat_fronts(anchor, armchairs)
    span = max(G.distance(a[0], b[0]) for i, (a) in enumerate(fronts) for b in fronts[i + 1:])
    lo, hi = float(rule["min"]), float(rule["max"])
    size = 1.0 if lo <= span <= hi else max(0.0, 1.0 - (lo - span if span < lo else span - hi))
    cx = sum(m[0] for m, _d in fronts) / len(fronts)
    cy = sum(m[1] for m, _d in fronts) / len(fronts)
    faced = 0
    for (mx, my), deg in fronts:
        want = math.degrees(math.atan2(cy - my, cx - mx))
        if G.angle_difference_deg(deg, want) <= float(rule.get("facing_deg", 45.0)) + 1e-9:
            faced += 1
    return round(0.5 * size + 0.5 * faced / len(fronts), 4)


def _term_alignment(space: Space, anchor: Spot, wall, by_role: dict) -> Optional[float]:
    """R13: a free anchor parallel to the room's axes (``alignment.axis_deg``); pairs (nightstands, armchairs)
    mirrored about the anchor's axis within ``alignment.pair_m``. None when nothing applies."""
    rule = GR.rule("alignment")
    parts = []
    if wall is None:
        off = G.normalise_angle(anchor.rotation - space.R.angle) % 90.0
        off = min(off, 90.0 - off)
        parts.append(1.0 if off <= float(rule.get("axis_deg", 5.0)) + 1e-9 else 0.0)
    for role in ("nightstand", "armchair"):
        pair = by_role.get(role) or []
        if len(pair) == 2:
            a, b = (GC.to_local(anchor.piece(), s.center) for s in pair)
            mirrored = abs(a[0] + b[0]) <= float(rule.get("pair_m", 0.10)) + 1e-9 and \
                abs(a[1] - b[1]) <= float(rule.get("pair_m", 0.10)) + 1e-9
            parts.append(1.0 if mirrored else 0.0)
        elif len(pair) == 1:
            parts.append(0.5)
    if not parts:
        return None
    return round(sum(parts) / len(parts), 4)


def _term_anchored(space: Space, spots: list[Spot]) -> Optional[float]:
    """R12: the share of the new free-standing spots that stand on a wall or within ``floating.max_m`` of another
    spot of the group or of a fixed piece (nothing floats in the middle of the room)."""
    free = [s for s in spots if not s.against_wall and s.type not in GR.DECOR_MEMBER_TYPES]
    if not free:
        return None
    reach = float(GR.rule("floating").get("max_m", 0.8))
    polys = [s.piece().polygon() for s in spots]
    ok = 0
    for s in free:
        poly = s.piece().polygon()
        if poly.distance(space.ctx.ring) <= reach + 1e-9:
            ok += 1
            continue
        if any(q is not poly and poly.distance(q) <= reach + 1e-9 for q in polys) or \
                any(poly.distance(q) <= reach + 1e-9 for q in space.fixed_polys):
            ok += 1
    return round(ok / len(free), 4)


def _kitchen_targets(space: Space) -> list:
    """Points the dining group likes to be near: the room's kitchen zones and the doors to kitchens."""
    out = []
    for z in space.room.get("zones") or []:
        if z.get("kind") == "kitchen" and len(z.get("polygon") or []) >= 3:
            c = Polygon(z["polygon"]).centroid
            out.append((c.x, c.y))
    for door in space.ctx.doors:
        op = space.doors_by_id.get(door.id)
        other = GC.other_room_of_door(space.building, space.room, op) if op else None
        if other is not None and other.get("room_type") == "kitchen":
            out.append(door.inner_point)
    if space.room.get("room_type") == "kitchen":
        out.append(space.centroid)
    return out


def _score(terms: dict) -> float:
    w = GR.weights()
    return round(sum(w.get(k, 0.0) * v for k, v in terms.items() if v is not None), 6)


def _align_term(t: float, lo: float, hi: float, align: str) -> float:
    half = max((hi - lo) / 2.0, 0.05)
    if align == "centre":
        return round(max(0.0, 1.0 - abs(t - (lo + hi) / 2.0) / half), 4)
    if align == "corner":
        return round(max(0.0, 1.0 - min(t - lo, hi - t) / half), 4)
    return 0.5


# --------------------------------------------------------------------------
# Anchor positions
# --------------------------------------------------------------------------

def _wall_positions(space: Space, size):
    """``(segment, t, centre, rotation, t_lo, t_hi)``: a back-to-wall footprint of ``size`` on every outline segment
    every 0.10 m from both ends (``t`` along the segment; ``t_lo..t_hi`` the stretch it may slide on)."""
    w, d = float(size[0]), float(size[1])
    for k, (a, b) in enumerate(space.ctx.segments):
        length = G.distance(a, b)
        if length < w + 2 * GAP - 1e-6:
            continue
        n = space.ctx.segment_normal(k)
        u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
        rot = placer._rotation_for_normal(n)
        t_min, t_max = w / 2.0 + GAP, length - w / 2.0 - GAP
        steps = int((t_max - t_min) / GRID_M + 1e-6)
        ts = sorted({round(t_min + i * GRID_M, 3) for i in range(steps + 1)} |
                    {round(t_max - i * GRID_M, 3) for i in range(steps + 1)})
        for t in ts:
            c = (a[0] + u[0] * t + n[0] * (d / 2.0 + GAP), a[1] + u[1] * t + n[1] * (d / 2.0 + GAP))
            yield k, t, (round(c[0], 4), round(c[1], 4)), rot, t_min, t_max


def _free_positions(space: Space, size, turns: tuple = (0.0, 90.0), step: float = GRID_M):
    """``(centre, rotation)`` on a 0.10 m grid (``step``) of the room's axis frame (only where the centre cell is
    free)."""
    R = space.R
    w, d = size
    reach = max(w, d) / 2.0
    xs = np.arange(R.x0 + reach, R.x0 + R.nx * R.res - reach + 1e-9, step)
    ys = np.arange(R.y0 + reach, R.y0 + R.ny * R.res - reach + 1e-9, step)
    for turn in turns:
        for y in ys:
            for x in xs:
                j, i = int(math.floor((float(y) - R.y0) / R.res)), int(math.floor((float(x) - R.x0) / R.res))
                if not (0 <= j < R.ny and 0 <= i < R.nx) or space.base[j, i]:
                    continue
                c = R.world((float(x), float(y)))
                yield (round(c[0], 4), round(c[1], 4)), G.normalise_angle(R.angle + turn)


def _ordered(items: list[tuple]) -> list[tuple]:
    """``(prescore, bucket, key, payload)`` best first, one per bucket first, then the rest (deterministic)."""
    items = sorted(items, key=lambda x: (-x[0], x[1], x[2]))
    first, rest, seen = [], [], set()
    for it in items:
        (rest if it[1] in seen else first).append(it)
        seen.add(it[1])
    return first + rest


# --------------------------------------------------------------------------
# Partners
# --------------------------------------------------------------------------

def _tv_spots(space: Space, anchor: Spot, sizes, offsets=(0.0, 0.1, -0.1, 0.2, -0.2, 0.3, -0.3)) -> list[Spot]:
    """TV units on the wall the sofa faces, centred on its axis (offsets along that wall), facing it; only where
    the TV front is ≥ the minimum viewing distance from the seat front and the wall is square to the axis."""
    a = anchor.piece()
    fx, fy = GC.front_vec(a)
    seat = anchor.world((0.0, -a.size[1] / 2.0))
    if a.shape == "L":
        x0, x1, yf = schemas.l_seat_front(a.size, a.chaise_side, a.chaise_depth, a.seat_depth, a.chaise_width)
        seat = anchor.world(((x0 + x1) / 2.0, yf))
    ray = LineString([seat, (seat[0] + fx * 12.0, seat[1] + fy * 12.0)])
    hit = ray.intersection(space.ctx.ring)
    if hit.is_empty:
        return []
    pts = [g for g in getattr(hit, "geoms", [hit]) if g.geom_type == "Point"]
    if not pts:
        return []
    p = min(pts, key=lambda q: Point(seat).distance(q))
    k = space.ctx.nearest_segment((p.x, p.y))
    n = space.ctx.segment_normal(k)
    if G.angle_difference_deg(math.degrees(math.atan2(-n[1], -n[0])), math.degrees(math.atan2(fy, fx))) > 2.0:
        return []                                      # the wall is not square to the sofa's axis
    sa, sb = space.ctx.segments[k]
    seg_len = G.distance(sa, sb)
    u = ((sb[0] - sa[0]) / seg_len, (sb[1] - sa[1]) / seg_len)
    t0 = (p.x - sa[0]) * u[0] + (p.y - sa[1]) * u[1]
    rot = placer._rotation_for_normal(n)
    tv_min = GR.rule_min("tv_distance")
    out = []
    for size in sizes:
        w, d = size
        dist = Point(seat).distance(p) - d - GAP
        if dist < tv_min - 1e-9:
            continue
        for off in offsets:
            t = t0 + off
            if t - w / 2.0 < GAP - 1e-6 or t + w / 2.0 > seg_len - GAP + 1e-6:
                continue
            c = (sa[0] + u[0] * t + n[0] * (d / 2.0 + GAP), sa[1] + u[1] * t + n[1] * (d / 2.0 + GAP))
            out.append(Spot("tv_unit", (round(c[0], 4), round(c[1], 4)), rot, (float(w), float(d)), "tv", True))
    return out


def chair_members(size, chair, count: Optional[int] = None) -> list[tuple[str, tuple, float]]:
    """``(side, local centre, turn)`` of the chairs around a table (``groups.dining_members``: as many per long side
    as fit at 0.55 m, the rest at the ends; each facing the table, 0.02 m off its edge; ``count``: Milestone 13, the
    drawn chairs of a re-solved group)."""
    out = []
    w, d = float(size[0]), float(size[1])
    for m in GR.dining_members((w, d), count):
        x, y = m.local
        if abs(y) > d / 2.0 - 1e-6 and abs(x) < w / 2.0:
            side = "front" if y < 0 else "back"
            y = (-1 if side == "front" else 1) * (d / 2.0 + chair[1] / 2.0 + GR.CHAIR_GAP_M)
        else:
            side = "left" if x < 0 else "right"
            x = (-1 if side == "left" else 1) * (w / 2.0 + chair[1] / 2.0 + GR.CHAIR_GAP_M)
        out.append((side, (x, y), m.turn))
    return out


def _pullout_zones(table: Spot, sides) -> dict[str, tuple]:
    """One pull-out zone (``diner_pullout`` deep from the table edge) per side that holds chairs."""
    w, d = table.size[0] / 2.0, table.size[1] / 2.0
    depth = GR.rule_min("diner_pullout")
    boxes = {"front": (-w, w, -d - depth, -d), "back": (-w, w, d, d + depth),
             "left": (-w - depth, -w, -d, d), "right": (w, w + depth, -d, d)}
    return {s: (f"pullout_{s}", table.center, table.rotation, boxes[s]) for s in sorted(set(sides))}


def _touches(space: Space, table: Spot, side: str) -> bool:
    """The table's side stands within 0.05 m of a wall or a fixed piece (a table against a wall)."""
    w, d = table.size[0] / 2.0, table.size[1] / 2.0
    strips = {"front": (-w, w, -d - 0.06, -d), "back": (-w, w, d, d + 0.06), "left": (-w - 0.06, -w, -d, d),
              "right": (w, w + 0.06, -d, d)}
    return space.zone_layer.hit(space.box_fp(table.center, table.rotation, strips[side], 0.0))


def _rug_under(anchor: Spot, seat_front: float, seat_x: float, seat_w: float, by_role: dict,
               spec: dict) -> Optional[Spot]:
    """R6: the seating rug in the anchor's frame: from ``rug_seating.inset`` behind the sofa's seat front over the
    coffee table and the armchairs (their far edges minus the inset: the front legs stay on), at least the
    template's smallest size; None without a coffee table."""
    coffee = (by_role.get("coffee") or [None])[0]
    if coffee is None:
        return None
    rule = GR.rule(spec["gap"]) if isinstance(spec.get("gap"), str) else {}
    inset = float(rule.get("inset", 0.30))
    xs, ys = [seat_x - seat_w / 2.0, seat_x + seat_w / 2.0], [seat_front + inset]
    for s in [coffee] + list(by_role.get("armchair") or []):
        lx, ly = GC.to_local(anchor.piece(), s.center)
        hw, hd = s.size[0] / 2.0, s.size[1] / 2.0
        if s.role == "armchair":           # its front faces the table: the far edge is its back, minus the inset
            reach = max(hw, hd) - inset
            xs += [lx - reach, lx + reach]
            ys += [ly - reach, ly + reach]
        else:
            xs += [lx - hw, lx + hw]
            ys += [ly - hd, ly + hd]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    mw, md = (float(v) for v in spec["sizes"][0])
    if x1 - x0 < mw:
        x0, x1 = (x0 + x1) / 2.0 - mw / 2.0, (x0 + x1) / 2.0 + mw / 2.0
    if y1 - y0 < md:
        y0 = y1 - md
    w, dd = round(x1 - x0, 2), round(y1 - y0, 2)
    return _local_spot(anchor, "rug", ((x0 + x1) / 2.0, (y0 + y1) / 2.0), 0.0, (w, dd), "rug")


def _rugs_beside(space: Space, anchor: Spot, spec: dict, want: int) -> list[Spot]:
    """R6: a runner ``rug_bed.width`` wide along each free long side of the bed, from the nightstand line
    (``head_skip``) to the foot; a side whose use zone is blocked gets none."""
    rule = GR.rule(spec["gap"]) if isinstance(spec.get("gap"), str) else {}
    width = float(rule.get("width", 0.8))
    w, d = float(anchor.size[0]), float(anchor.size[1])
    skip = float(GR.use_zone(anchor.type).get("head_skip", 0.45))
    length = round(d - skip, 2)
    out = []
    free = {z[0] for z in anchor.zones(overrides=space.overrides) if z[0] in ("left", "right")
            and not space.zone_layer.hit(space.zone_fp(z, FIXED_ZONE_INFLATE_M))}
    for side in ("right", "left"):
        if side not in free or len(out) >= want:
            continue
        sx = 1.0 if side == "right" else -1.0
        out.append(_local_spot(anchor, "rug", (sx * (w / 2.0 + width / 2.0), (d / 2.0 - skip - d / 2.0) / 2.0),
                               0.0, (width, length), "rug"))
    return out


def _resolve_count(resolve: Optional[dict], role: str) -> int:
    return sum(1 for _m, r in (resolve or {}).get("members", []) if r == role)


def _member_boxes(resolve: Optional[dict], role: str) -> list[tuple]:
    """Fix round after P4a: the front-frame boxes the drawn members of ``role`` take in a re-solve (their drawn size,
    or the planned box of a uniform library fit, as ``_match_members``), rounded, without repeats."""
    out = []
    for m, r in (resolve or {}).get("members", []):
        if r != role:
            continue
        try:
            p = placer.drawn_piece(m)
        except (KeyError, TypeError, ValueError):
            continue
        box = p.size if _planned_of(m) is None else p.planned_size
        out.append((round(float(box[0]), 4), round(float(box[1]), 4)))
    return list(dict.fromkeys(out))


def _match_members(space: Space, by_role: dict, resolve: dict) -> Optional[tuple[dict, list[Spot], list[float]]]:
    """Milestone 13: the drawn members of a re-solved group take the partner places of their role nearest their
    drawn centres (greedy, at most ``GROUP_MEMBER_MOVE_MAX_M`` away). Returns the spots by role with the matched
    spots replaced by the drawn pieces (their type and size, ``drawn`` / ``existing_id`` / ``moved`` set), the
    drawn members no place reaches (kept where drawn) and the moves."""
    limit = GR.GROUP_MEMBER_MOVE_MAX_M
    out = {role: list(spots) for role, spots in by_role.items()}
    kept: list[Spot] = []
    moves: list[float] = []
    for role in sorted({r for _m, r in resolve["members"]}):
        members = [m for m, r in resolve["members"] if r == role]
        spots = out.get(role) or []
        # Build round 3 (K2): a member with a uniform library fit takes the place with the box the builder makes
        # (centred on the place); what it records (and how far it moved) is its drawn size at the matching centre.
        records = []
        for m in members:
            plan = _planned_of(m)
            records.append(None if plan is None else (plan[0], plan[2]))
        # The drawn centre (``groups.drawn_centre``: drawn_footprint when the fit's size snap moved the piece).
        pairs = sorted((round(G.distance(tuple(GR.drawn_centre(m)), s.center if records[i] is None else
                                         _record_centre(s.center, s.rotation, records[i][1])), 4), i, j)
                       for i, m in enumerate(members) for j, s in enumerate(spots))
        taken_m: set = set()
        taken_s: set = set()
        for dist, i, j in pairs:
            if i in taken_m or j in taken_s or dist > limit + 1e-9:
                continue
            m, s = members[i], spots[j]
            p = placer.drawn_piece(m)
            box = p.size if records[i] is None else p.planned_size
            moved = Spot(m["type"], s.center, s.rotation, box, s.role, s.against_wall, p.shape, p.chaise_side,
                         existing_id=m["id"], drawn=m, moved=dist, record=records[i])
            spots[j] = moved
            taken_m.add(i)
            taken_s.add(j)
            moves.append(dist)
        for i, m in enumerate(members):
            if i not in taken_m:
                s = _spot_from(m, role)
                s.drawn, s.kept = m, True
                kept.append(s)
        out[role] = spots
    return out, kept, moves


def _partners(space: Space, template: dict, option: dict, anchor: Spot, filled: dict,
              resolve: Optional[dict] = None) -> Optional[tuple]:
    """(new partner spots, zones, terms, spots by role, rug spots) around ``anchor``, or None when a required
    partner does not fit. ``filled``: role -> count of drawn partners already there (``nightstand_sides``: the
    sides taken). ``resolve`` (Milestone 13): the drawn group re-solved as one unit (``{"members": [(piece, role)],
    ...}``): its members take the partner places nearest their drawn centres (``_match_members``)."""
    w, d = float(anchor.size[0]), float(anchor.size[1])
    new_anchor = anchor.existing_id is None      # a drawn anchor gets what fits; a new one needs its required partners
    placed: list[Spot] = []
    placed_fps: list = space.spot_fps(anchor)
    zones: list = []
    counts = option.get("counts") or {}
    optional_total, optional_placed = 0, 0
    by_role: dict[str, list[Spot]] = {}
    rugs: list[Spot] = []
    seat_front, seat_x, seat_w = -d / 2.0, 0.0, w
    if anchor.shape == "L":
        x0, x1, seat_front = schemas.l_seat_front(anchor.size, anchor.chaise_side, d)
        seat_x, seat_w = (x0 + x1) / 2.0, x1 - x0

    def with_found(found: list[Spot]) -> list:
        return placed_fps + [fp for f in found for fp in space.spot_fps(f)]

    for spec in template["partners"]:
        role, ftype = spec["role"], spec["type"]
        want = counts.get(ftype, spec.get("default", spec.get("max", 1)))
        if resolve is not None:
            want = max(want, _resolve_count(resolve, role))   # every drawn member of the role needs a place
        want = max(0, want - int(filled.get(role, 0)))
        if role == "nightstand":
            want = min(want, schemas.NIGHTSTANDS_PER_BED.get(anchor.type, 1) - len(filled.get("nightstand_sides", ())))
        if want <= 0:
            continue
        place = spec["place"]
        if ftype in GR.DECOR_MEMBER_TYPES:
            # Milestone 13 (R6): a rug member, laid after the pieces (it needs the coffee table / the free sides).
            if place == "under":
                rug = _rug_under(anchor, seat_front, seat_x, seat_w, by_role, spec)
                rugs += [rug] if rug is not None else []
            elif place == "beside":
                rugs += _rugs_beside(space, anchor, spec, want)
            continue
        if not spec["required"]:
            optional_total += want
        if not space.allowed(ftype, anchor.center):
            alt = spec.get("alt_type")
            if alt and space.allowed(alt, anchor.center):
                ftype = alt
            else:
                continue                       # the room cannot hold it: the group goes without it
        found: list[Spot] = []
        sizes = [tuple(s) for s in (option.get("partner_sizes") or {}).get(role, spec["sizes"])]
        if resolve is not None:
            # fix round after P4a: the drawn members of a re-solved group are placed at their own box (the box
            # _match_members gives them), so their places are searched at that size first (the template's after)
            sizes = list(dict.fromkeys(_member_boxes(resolve, role) + sizes))
        if place == "facing_wall":
            for s in _tv_spots(space, anchor, sizes):
                dist = GC.tv_geometry(anchor.piece(), s.piece())["distance_m"]
                half = min(s.size[0], seat_w) / 2.0
                sight = ("sight", anchor.center, anchor.rotation, (seat_x - half, seat_x + half, seat_front - dist,
                                                                    seat_front))
                if _fits(space, s, placed_fps) and space.zones_free([sight]):
                    found = [s]
                    zones.append(sight)
                    break
        elif place == "front":
            rule = GR.rule(spec["gap"]) if isinstance(spec.get("gap"), str) else {"min": float(spec.get("gap", 0.3))}
            rec_lo = rule.get("rec", rule["min"])
            gaps = list(dict.fromkeys([round((rec_lo + rule.get("rec_max", rec_lo)) / 2.0, 3), rec_lo, rule["min"]]))
            tv = (by_role.get("tv") or [None])[0]
            limit = GC.tv_geometry(anchor.piece(), tv.piece())["distance_m"] if tv is not None else None
            # fix round after P6b, review: the (size, gap) options in their order (sizes first, then gaps); the first
            # one that fits from ``space.front_from`` on (0: the first fit, as before) is taken and recorded
            for i, (size, g) in enumerate((size, g) for size in sizes for g in gaps):
                if i < space.front_from or size[0] > seat_w - 0.3:
                    continue
                if limit is not None and g + size[1] + 0.40 > limit:
                    continue
                s = _local_spot(anchor, ftype, (seat_x, seat_front - g - size[1] / 2.0), 0.0, size, role)
                if _fits(space, s, placed_fps):
                    found = [s]
                    space.front_chosen.append(i)
                    break
        elif place == "flank":
            of = (by_role.get(spec.get("of") or "") or [None])[0]
            if of is None:
                continue
            ol = GC.to_local(anchor.piece(), of.center)
            gap = float(spec.get("gap", 0.35))
            for size in sizes:
                found = []
                for side in (1.0, -1.0):
                    if len(found) >= want:
                        break
                    x = ol[0] + side * (of.size[0] / 2.0 + gap + size[1] / 2.0)
                    s = _local_spot(anchor, ftype, (x, ol[1]), 270.0 if side > 0 else 90.0, size, role)
                    if _fits(space, s, with_found(found), s.zones(overrides=space.overrides)):
                        found.append(s)
                if found:
                    break
        elif place == "beside_head":
            gap = float(spec.get("gap", 0.02))
            taken = set(filled.get("nightstand_sides", ()))
            sides = [s for s in ("right", "left") if s not in taken]
            for size in sizes:
                found = []
                for side in sides:
                    if len(found) >= want:
                        break
                    sx = 1.0 if side == "right" else -1.0
                    # Back on the anchor's back line; a drawn headboard flush on the wall line leaves no 2 cm gap, so
                    # the nightstand may step up to 5 cm forward (G4 allows 0.10 m).
                    for step in (0.0, 0.025, 0.05):
                        s = _local_spot(anchor, ftype, (sx * (w / 2.0 + gap + size[0] / 2.0),
                                                        d / 2.0 - size[1] / 2.0 - step), 0.0, size, role, True)
                        if _fits(space, s, with_found(found)) and space.exact_ok(s, s.piece().polygon()):
                            found.append(s)
                            break
                if len(found) >= want:
                    break
        elif place == "foot":
            gap = float(spec.get("gap", 0.05))
            for size in sizes:
                if size[0] > w + 1e-6:
                    continue
                s = _local_spot(anchor, ftype, (0.0, -d / 2.0 - gap - size[1] / 2.0), 0.0, size, role)
                if _fits(space, s, placed_fps):
                    found = [s]
                    break
        elif place == "chair":
            gap = float(spec.get("gap", 0.05))
            for size in sizes:
                s = _local_spot(anchor, ftype, (0.0, -d / 2.0 - gap - size[1] / 2.0), 180.0, size, role)
                if _fits(space, s, placed_fps):
                    found = [s]
                    break
        elif place == "around":
            if filled.get(role):
                continue                       # drawn chairs: none added
            count = counts.get(ftype)            # an option's seat count (else by the table length)
            if resolve is not None:            # Milestone 13: a place for every drawn chair (and the table's seats)
                count = max(_resolve_count(resolve, role),
                            schemas.count_by_length(max(w, d), schemas.CHAIRS_BY_TABLE_LENGTH))
            members = chair_members((w, d), sizes[0], count)
            pull = _pullout_zones(anchor, [m[0] for m in members])
            sides = set()
            for side, z in pull.items():
                if not space.zone_layer.hit(space.zone_fp(z)):
                    sides.add(side)
                elif new_anchor and not _touches(space, anchor, side):
                    return None                # a side without room behind its chairs that does not touch a wall
            zones += [pull[s] for s in sorted(sides)]
            for side, local, turn in members:
                if side not in sides:
                    continue
                s = _local_spot(anchor, ftype, local, turn, sizes[0], role)
                if _fits(space, s, with_found(found)):
                    found.append(s)
            if spec["required"] and members and len(found) < 2 and new_anchor:
                return None
        elif place == "stools":
            n = min(schemas.count_by_length(w, schemas.BAR_STOOLS_BY_ISLAND_LENGTH), want)
            size = sizes[0]
            gap = float(spec.get("gap", 0.05))
            for k in range(n):
                x = -w / 2.0 + w * (k + 0.5) / n
                s = _local_spot(anchor, ftype, (x, d / 2.0 + gap + size[1] / 2.0), 0.0, size, role)
                if _fits(space, s, with_found(found)):
                    found.append(s)
        elif place == "pair":
            size = sizes[0]
            for y, turn in ((-(d / 2.0 + 0.05 + size[1] / 2.0), 180.0), (d / 2.0 + 0.05 + size[1] / 2.0, 0.0)):
                s = _local_spot(anchor, ftype, (0.0, y), turn, size, role)
                if _fits(space, s, with_found(found)):
                    found.append(s)
            if spec["required"] and len(found) < 2 and new_anchor:
                return None
        if spec["required"] and not found and place != "around" and new_anchor:
            return None
        if place not in ("around", "pair"):
            found = found[:want]
        if not spec["required"]:
            optional_placed += len(found)
        for s in found:
            zones += s.zones(overrides=space.overrides)
        placed_fps = with_found(found)
        placed += found
        by_role.setdefault(role, []).extend(found)
    terms = {}
    if optional_total:
        terms["partners"] = round(optional_placed / optional_total, 4)
    if resolve is not None and resolve.get("members"):
        matched = _match_members(space, by_role, resolve)
        if matched is None:
            return None
        by_role, kept, moves = matched
        placed = [s for spots in by_role.values() for s in spots] + kept
        if moves:
            terms["member_moves"] = moves
    return placed, zones, terms, by_role, rugs


def _anchor_terms(space: Space, group: str, anchor: Spot, by_role: dict, info: dict, wall=None) -> dict:
    terms: dict = {}
    if group == "seating":
        terms["sight_tv"] = _term_sight(anchor, (by_role.get("tv") or [None])[0])
        conv = _term_conversation(anchor, list(by_role.get("armchair") or []))
        if conv is not None:
            terms["conversation"] = conv
    align = _term_alignment(space, anchor, wall, by_role)
    if align is not None:
        terms["alignment"] = align
    if group in ("sleeping_double", "sleeping_single"):
        terms["bed_sees_door"] = _term_bed_door(space, anchor, info["entrance"])
    if group == "work":
        terms["desk_side_light"] = _term_desk_light(space, anchor)
        terms["daylight"] = _term_daylight(space, anchor.center)
    if group in ("dining", "balcony"):
        terms["daylight"] = _term_daylight(space, anchor.center)
        if info["kitchen_points"] and group == "dining":
            dist = min(G.distance(anchor.center, p) for p in info["kitchen_points"])
            terms["related_near"] = round(max(0.0, 1.0 - dist / 6.0), 4)
    return terms


def _prescore(space: Space, group: str, spot: Spot, wall, align: str, info: dict) -> float:
    """A cheap score of an anchor alone (alignment, daylight, the bed's view of the door) to order the tries."""
    terms = {}
    if wall is not None:
        terms["wall_use"] = _align_term(wall[1], wall[2], wall[3], align)
    if group in ("dining", "work", "balcony"):
        terms["daylight"] = _term_daylight(space, spot.center)
    if group in ("sleeping_double", "sleeping_single"):
        terms["bed_sees_door"] = _term_bed_door(space, spot, info["entrance"])
    if group == "work":
        terms["desk_side_light"] = _term_desk_light(space, spot)
    return _score(terms)


# --------------------------------------------------------------------------
# Group candidates
# --------------------------------------------------------------------------

def _resolve_sizes(drawn: dict, template: dict, area: float) -> list[tuple[float, float]]:
    """Milestone 13: the sizes a re-solved drawn anchor is tried at: its drawn size (front frame) when it lies in
    the product grid, else the nearest real product (``sizes.snap_size``; CLAUDE.md "change its size to a real
    product size"), then the template's sizes for the room area nearest the drawn size."""
    from wenart.furniture import sizes as SZ

    p = placer.drawn_piece(drawn)
    size = (round(float(p.size[0]), 4), round(float(p.size[1]), 4))
    snap = SZ.snap_size(drawn["type"], size)
    first = size if not snap.get("changed") else tuple(round(float(v), 4) for v in snap["footprint"])
    if drawn["type"] in PR.RUN_LIKE_TYPES:
        # A storage run keeps its drawn length (modules, T2) and snaps only its depth; it is never shrunk to a
        # template size (a wall-to-wall wardrobe stays a run, or stays as drawn when no place takes it).
        return [(size[0], first[1])]
    out = [first]
    others = [tuple(s) for s in GR.sizes_for(template, drawn["type"], area)]
    others.sort(key=lambda s: (max(abs(math.log(s[0] / first[0])), abs(math.log(s[1] / first[1]))), s))
    for s in others:
        if all(abs(s[i] - o[i]) > 1e-6 for o in out for i in (0, 1)) or s not in out:
            if s not in out:
                out.append(s)
    return out[:3]


def _resolve_tries(space: Space, entry: dict, template: dict, options: list[str], info: dict,
                   align: str) -> list[tuple]:
    """Milestone 13: anchor tries of a re-solved drawn group: the drawn anchor at its drawn size (or the nearest
    product) on every wall position / free grid point within ``GROUP_MEMBER_MOVE_MAX_M`` of its drawn centre (the
    drawn place itself first), scored by the distance to the drawn centre on top of the usual pre-score."""
    res = info["resolve"][entry["group_id"]]
    drawn = res["anchor"]
    centre = tuple(float(v) for v in res["centre"])
    limit = GR.GROUP_MEMBER_MOVE_MAX_M
    anchor_spec = template["anchor"]
    budget = info["budget"]
    weight = GR.weights().get("drawn_distance", 1.0)
    dp = placer.drawn_piece(drawn)
    # Build round 3 (K2): at its drawn size a drawn anchor with a uniform library fit is planned with the box the
    # scene builder makes (deeper or shallower at the front, ``_planned_of``); the distance to the drawn centre and
    # the record are its drawn box (``Spot.record``). A snapped or template size drops the asset (refit): as given.
    plan = _planned_of(drawn)
    tries: list[tuple] = []
    for oname in options:
        opt = template["options"][oname]
        atype = opt["anchor"]
        if atype != drawn["type"]:
            continue
        for si, size in enumerate(_resolve_sizes(drawn, template, float(entry.get("area") or space.area))):
            box, record = size, None
            if plan is not None and _same_size(size, plan[0]):
                box, record = plan[1], (plan[0], plan[2])

            def moved_of(c, rot, record=record) -> float:
                """How far the recorded (drawn-size) box of a place lies from the drawn centre."""
                return G.distance(c if record is None else _record_centre(c, rot, record[1]), centre)

            if anchor_spec["place"] == "wall":
                sides = ((dp.chaise_side or "right"),) if atype == "sofa_corner" else (None,)
                for k, t, c, rot, lo, hi in _wall_positions(space, box):
                    dist = moved_of(c, rot)
                    if dist > limit + 1e-6:
                        continue
                    for side in sides:
                        budget["used"] += 1
                        s = Spot(atype, c, rot, box, "anchor", True, "L" if side else None, side,
                                 existing_id=drawn["id"], drawn=drawn, moved=dist, record=record)
                        if not space.spot_free(s):
                            continue
                        pre = (_prescore(space, entry["group"], s, (k, t, lo, hi), align, info) - 0.01 * si
                               + weight * (1.0 - dist / limit))
                        tries.append((pre, (oname, k, int(round(t / MERGE_M)), side or ""), (round(t, 3), si),
                                      (oname, s, (k, t, lo, hi))))
            else:
                turns = (0.0, 90.0) if atype in schemas.FRONTLESS_TYPES else (0.0, 90.0, 180.0, 270.0)
                places = []
                for turn in turns:
                    rot = G.normalise_angle(dp.rotation_deg + turn)
                    c = centre if record is None else _planned_centre(centre, rot, record[1])
                    places.append(((round(c[0], 4), round(c[1], 4)), rot))
                places += [(c, rot) for c, rot in _free_positions(space, box) if moved_of(c, rot) <= limit + 1e-6]
                for c, rot in places:
                    budget["used"] += 1
                    dist = moved_of(c, rot)
                    s = Spot(atype, c, rot, box, "anchor", False, existing_id=drawn["id"], drawn=drawn, moved=dist,
                             record=record)
                    if not space.spot_free(s):
                        continue
                    pre = _prescore(space, entry["group"], s, None, align, info) - 0.01 * si + weight * (1.0 - dist / limit)
                    tries.append((pre, (oname, round(rot) % 180, int(round(c[0] / MERGE_M)),
                                        int(round(c[1] / MERGE_M))), (c, si), (oname, s, None)))
    return tries


def anchored_candidates(space: Space, entry: dict, level: int, info: dict) -> list[Cand]:
    template = GR.load_groups()[entry["group"]]
    options = [entry["chosen"]] if entry.get("chosen") else list(entry["options"])
    anchor_spec = template["anchor"]
    align = anchor_spec.get("align", "any")
    zone_poly = info["zones"].get(entry.get("zone_id"))
    resolve = info.get("resolve", {}).get(entry["group_id"]) if entry.get("resolve") else None
    drawn = info["by_id"].get(entry.get("anchor_id")) if entry.get("drawn") and resolve is None else None
    filled = info["filled"].get(entry["group_id"], {})
    budget = info["budget"]
    out: list[Cand] = []
    tries: list[tuple] = []
    if resolve is not None:
        tries = _resolve_tries(space, entry, template, options, info, align)
    # 23 Oct 2026 (group options 10x): each group takes at most its share of the room's generation budget, its core
    # options half of it and its extra options the other half (each option an equal part of its half); an option whose
    # sizes have more positions than that is tried on a coarser grid (free anchors) or every n-th wall step (wall
    # anchors), so the 26 dining options never use up the budget of the living storage that comes after them.
    group_share = (budget["generate"] - budget["used"]) // max(1, info.get("groups_left", 1))
    core = [o for o in options if GR.is_core(template["options"][o])]
    halves = 2 if core and len(core) < len(options) else 1

    def share_of(oname: str) -> int:
        same = [o for o in options if (o in core) == (oname in core)] if halves == 2 else options
        return max(OPTION_GENERATE_MIN, group_share // halves // max(1, len(same)))

    for oname in (options if resolve is None else []):
        opt = template["options"][oname]
        atype = opt["anchor"]
        share = share_of(oname)
        if drawn is not None:
            # fix round after P4a: a code-typed (unverified) drawn anchor is used as drawn (program.unsure_anchor)
            if PR.unsure_anchor(drawn) or drawn.get("build") is False or drawn["type"] != atype:
                continue
            tries.append((1.0, ("drawn", oname), (oname,), (oname, _spot_from(drawn), None)))
            continue
        if not space.allowed(atype, None) and zone_poly is None:
            continue
        sizes = [tuple(s) for s in (opt.get("sizes") or {}).get(atype, [])] or \
            GR.sizes_for(template, atype, float(entry.get("area") or space.area))
        per_size = max(1, share // max(1, len(sizes)))
        for si, size in enumerate(sizes):
            if anchor_spec["place"] == "wall":
                sides = ("right", "left") if atype == "sofa_corner" else (None,)
                walls = list(_wall_positions(space, size))
                stride = max(1, math.ceil(len(walls) * len(sides) / per_size))
                for k, t, c, rot, lo, hi in walls[::stride]:
                    for side in sides:
                        if budget["used"] >= budget["generate"]:
                            break
                        budget["used"] += 1
                        s = Spot(atype, c, rot, size, "anchor", True, "L" if side else None, side)
                        if zone_poly is not None and not zone_poly.buffer(0.05).contains(Point(c)):
                            continue                   # outside the group's zone: not a try
                        if not space.spot_free(s):
                            continue
                        pre = _prescore(space, entry["group"], s, (k, t, lo, hi), align, info) - 0.01 * si
                        tries.append((pre, (oname, k, int(round(t / MERGE_M)), side or ""), (round(t, 3), si),
                                      (oname, s, (k, t, lo, hi))))
            else:
                # two turns per free 0.10 m cell (the raster's free cells, an upper bound)
                cells = 2.0 * float((space.base == 0).sum()) * (space.R.res / GRID_M) ** 2
                step = GRID_M * max(1, math.ceil(math.sqrt(cells / per_size)))
                for c, rot in _free_positions(space, size, step=step):
                    if budget["used"] >= budget["generate"]:
                        break
                    budget["used"] += 1
                    s = Spot(atype, c, rot, size, "anchor", False)
                    if zone_poly is not None and not zone_poly.buffer(0.05).contains(Point(c)):
                        continue
                    if not space.spot_free(s):
                        continue
                    pre = _prescore(space, entry["group"], s, None, align, info) - 0.01 * si
                    tries.append((pre, (oname, round(rot) % 180, int(round(c[0] / MERGE_M)),
                                        int(round(c[1] / MERGE_M))), (c, si), (oname, s, None)))
    valid = 0
    has_rug = any(p["type"] in GR.DECOR_MEMBER_TYPES for p in template["partners"])
    for n_try, (_pre, _bucket, _key, (oname, spot, wall)) in enumerate(_ordered(tries)):
        if n_try >= ANCHOR_TRIES or valid >= 3 * PER_LEVEL:
            break
        opt = template["options"][oname]
        new_anchor = spot.existing_id is None or spot.drawn is not None     # a re-solved anchor is placed anew
        if new_anchor:
            if zone_poly is not None and not zone_poly.buffer(0.05).contains(Point(spot.center)):
                continue
            zones = _one_side(space, spot, spot.zones(overrides=space.overrides))
            if zones is None or not space.zones_free(zones) or not space.allowed(spot.type, spot.center):
                continue
        else:
            zones = []                                 # a drawn anchor's zones are reserved at the root (fixed_zones)
        res = _partners(space, template, opt, spot, filled, resolve)
        if res is None:
            continue
        partners, pzones, terms, by_role, rugs = res
        if not new_anchor and not partners:
            continue                                   # a drawn group with nothing to add
        if new_anchor:
            rec = _term_recommended(space, spot)
            if rec is not None:
                terms["recommended"] = rec
            if wall is not None:
                terms["wall_use"] = _align_term(wall[1], wall[2], wall[3], align)
        else:
            ds = [G.distance(p.center, spot.center) for p in partners]
            terms["drawn_distance"] = round(max(0.0, 1.0 - (sum(ds) / len(ds)) / 4.0), 4) if ds else 1.0
        if resolve is not None:
            moves = [spot.moved] + list(terms.pop("member_moves", []))
            terms["drawn_distance"] = round(max(0.0, 1.0 - (sum(moves) / len(moves)) / GR.GROUP_MEMBER_MOVE_MAX_M), 4)
        terms.update(_anchor_terms(space, entry["group"], spot, by_role, info, wall))
        _previous_term(terms, partners if not new_anchor else [spot] + partners, info)
        new = ([spot] if new_anchor else []) + partners
        anchored = _term_anchored(space, new)
        if anchored is not None:
            terms["anchored"] = anchored
        cand = Cand(level, entry["group_id"], entry["group"], oname, spot, new, zones + pzones, terms, rugs=rugs)
        if resolve is not None:
            cand.resolve = {"anchor_id": resolve["anchor"]["id"], "members": [m["id"] for m, _r in resolve["members"]],
                            "reason": resolve.get("reason", "")}
        if not _finish(space, cand):
            continue
        if has_rug:
            terms["rug"] = 1.0 if cand.rugs else 0.0
        valid += 1
        cand.local = _score(terms)
        key = (wall[0], int(round(wall[1] / MERGE_M))) if wall else \
            (int(round(spot.center[0] / MERGE_M)), int(round(spot.center[1] / MERGE_M)))
        cand.sig = (oname, round(spot.rotation) % 360, key, spot.chaise_side or "", len(new))
        out.append(cand)
    # kinds: the anchor type and core / extra option (the extras' candidates never crowd out the core ones); a group
    # offered extra options keeps twice as many candidates
    keep = PER_LEVEL * (2 if len(core) < len(options) else 1)
    return _keep(out, keep, kind=lambda c: (c.anchor.type, GR.is_core(template["options"][c.option])))


def _one_side(space: Space, spot: Spot, zones: list, inflate: float = ZONE_INFLATE_M) -> Optional[list]:
    """A bed that needs one free long side (``sides_needed: 1``, a single bed; Milestone 13 R14: any bed in a
    bedroom under ``small_rooms.bedroom.max_area``) keeps the side zones that are free (the other side may touch a
    wall); None when neither is."""
    needed = int(GR.use_zone(spot.type).get("sides_needed", 2))
    small = GR.small_room("bedroom", space.area) if spot.type in GC.BED_TYPES else None
    if small and small.get("sides_needed"):
        needed = min(needed, int(small["sides_needed"]))
    if needed != 1:
        return zones
    sides = [z for z in zones if z[0] in ("left", "right")]
    free = [z for z in sides if not space.zone_layer.hit(space.zone_fp(z, inflate))]
    if sides and not free:
        return None
    return [z for z in zones if z[0] not in ("left", "right")] + free[:1]


def _previous_term(terms: dict, spots: list[Spot], info: dict) -> None:
    """``drawn_distance`` of a re-layout: new pieces near the room's earlier added pieces of their type."""
    prev = info.get("previous") or []
    if not prev or not spots:
        return
    ds = []
    for s in spots:
        same = [c for t, c in prev if t == s.type]
        if same:
            ds.append(min(G.distance(s.center, c) for c in same))
    if ds:
        terms["drawn_distance"] = round(max(0.0, 1.0 - (sum(ds) / len(ds)) / 3.0), 4)


def _keep(cands: list[Cand], n: int, kind=None) -> list[Cand]:
    """The best ``n`` candidates, one per signature (score, then position, deterministic). ``kind`` (23 Oct 2026,
    group options 10x): a candidate's kind (a run's shape, an anchor's type with core or extra option, a member's
    type); each kind first keeps
    its best ``max(2, n // (2 x kinds))``, then the best of the rest fill up, so twelve L and U variants never crowd
    the I runs out of the level (an L that fails the final aisle check would leave the kitchen without a run)."""
    cands = sorted(cands, key=lambda c: (-c.local, c.sig, _pos_key(c)))
    out, seen = [], set()
    if kind is not None:
        kinds = list(dict.fromkeys(kind(c) for c in cands))
        share, taken = max(2, n // (2 * max(1, len(kinds)))), {}
        for c in cands:
            k = kind(c)
            if c.sig in seen or taken.get(k, 0) >= share:
                continue
            seen.add(c.sig)
            taken[k] = taken.get(k, 0) + 1
            out.append(c)
            if len(out) >= n:
                break
    for c in cands:
        if len(out) >= n:
            break
        if c.sig in seen:
            continue
        seen.add(c.sig)
        out.append(c)
    return sorted(out, key=lambda c: (-c.local, c.sig, _pos_key(c)))


def _pos_key(c: Cand) -> tuple:
    return tuple((s.type, round(s.center[0], 2), round(s.center[1], 2), round(s.rotation, 1)) for s in c.spots)


def member_candidates(space: Space, entry: dict, members: list[dict], level: int, info: dict) -> list[Cand]:
    """Wall places of one member level of a set (or one missing piece of a drawn group): every member spec of the
    level (a bathtub or a shower for the ``bath`` role) at its sizes on every wall."""
    out = []
    budget = info["budget"]
    zone_poly = info["zones"].get(entry.get("zone_id"))
    near = info["near"].get(entry["group_id"])
    for member in members:
        ftype = member["type"]
        if not space.allowed(ftype, None) and zone_poly is None:
            continue
        align = member.get("align", "any")
        for size in [tuple(s) for s in member["sizes"]]:
            for k, t, c, rot, lo, hi in _wall_positions(space, size):
                if budget["used"] >= budget["generate"]:
                    break
                budget["used"] += 1
                spot = Spot(ftype, c, rot, size, member["role"], True)
                if not space.spot_free(spot):
                    continue
                if zone_poly is not None and not zone_poly.buffer(0.05).contains(Point(spot.center)):
                    continue
                zones = spot.zones(overrides=space.overrides)
                if not space.zones_free(zones):
                    continue
                terms = {"wall_use": _align_term(t, lo, hi, align)}
                rec = _term_recommended(space, spot)
                if rec is not None:
                    terms["recommended"] = rec
                if near:
                    dist = min(G.distance(spot.center, p) for p in near)
                    terms["drawn_distance"] = round(max(0.0, 1.0 - dist / 4.0), 4)
                _previous_term(terms, [spot], info)
                cand = Cand(level, entry["group_id"], entry["group"], ftype, spot, [spot], zones, terms)
                if not space.allowed(ftype, spot.center) or not _finish(space, cand):
                    continue
                cand.local = _score(terms)
                cand.sig = (member["role"], ftype, k, int(round(t / MERGE_M)))
                out.append(cand)
    return _keep(out, PER_LEVEL, kind=lambda c: c.anchor.type)


# --------------------------------------------------------------------------
# Kitchen runs
# --------------------------------------------------------------------------

BIN_M = 0.05
JOG_M = 0.15                   # 26 Oct 2026: outline jogs shorter than this are merged before the kitchen legs
STRAIGHT_DEG = 3.0             # ... and two outline segments within this angle are one wall
LEG_MIN_M = 1.2                # a wall shorter than this is no kitchen leg (the compact fallback: its own minimum)


def run_outline(segments: list) -> list[tuple]:
    """26 Oct 2026 (user: "a kitchen must never be empty"): the room outline the kitchen legs stand on, ``[(a, b)]``
    counter-clockwise like ``RoomContext.segments``. What: a jog shorter than ``JOG_M`` between two parallel walls
    (a plaster step, a 5 cm offset of two wall layers) is merged: the two walls become one leg on the inner of their
    two lines (the line further into the room, so the counters stay inside it; the back gap is at most the jog), and
    the walls before and after it are lengthened or shortened to meet that line; straight runs of segments become one
    segment. Why: real06's kitchen has a 4.6 cm jog in its back wall; it split the wall into a 2.0 m and a 0.5 m
    segment and broke the real corner with the side wall, so no I or L run fitted. Pure; the room is not changed."""
    pts = [(float(a[0]), float(a[1])) for a, _b in segments]

    def unit(p, q):
        d = G.distance(p, q)
        return ((q[0] - p[0]) / d, (q[1] - p[1]) / d) if d > 1e-9 else (0.0, 0.0)

    def straight(p, q, r) -> bool:
        u, v = unit(p, q), unit(q, r)
        return u[0] * v[0] + u[1] * v[1] > math.cos(math.radians(STRAIGHT_DEG))

    def meet(p, q, origin, u):
        """The point where the line p-q meets the line through ``origin`` along ``u`` (None when parallel)."""
        d = (q[0] - p[0], q[1] - p[1])
        den = d[0] * u[1] - d[1] * u[0]
        if abs(den) < 1e-9:
            return None
        s = ((origin[0] - p[0]) * u[1] - (origin[1] - p[1]) * u[0]) / den
        return (p[0] + d[0] * s, p[1] + d[1] * s), s

    changed = True
    while changed and len(pts) > 4:
        changed = False
        n = len(pts)
        for i in range(n):                                   # drop repeated and straight-through vertices
            p, q, r = pts[i - 1], pts[i], pts[(i + 1) % n]
            if G.distance(p, q) < 1e-6 or straight(p, q, r):
                del pts[i]
                changed = True
                break
        if changed:
            continue
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]                  # the jog a -> b
            if G.distance(a, b) >= JOG_M:
                continue
            p0, p1 = pts[i - 2], pts[i - 1]                  # the wall before p1 -> a
            q1, q2 = pts[(i + 2) % n], pts[(i + 3) % n]      # the wall after b -> q1
            u_prev, u_next = unit(p1, a), unit(b, q1)
            if u_prev[0] * u_next[0] + u_prev[1] * u_next[1] < math.cos(math.radians(STRAIGHT_DEG)):
                continue                                     # not two parallel walls of the same direction
            normal = G.unit_normal_left(p1, a)               # inward (counter-clockwise outline)
            depth_in = (b[0] - a[0]) * normal[0] + (b[1] - a[1]) * normal[1]
            if depth_in > 0:                                 # the next wall's line lies further in: move p1 onto it
                hit = meet(p0, p1, b, u_next)
                if hit is None or hit[1] <= 1e-3:
                    continue
                pts[i - 1] = hit[0]
            else:                                            # the wall before lies further in: move q1 onto its line
                hit = meet(q2, q1, a, u_prev)
                if hit is None or hit[1] <= 1e-3:
                    continue
                pts[(i + 2) % n] = hit[0]
            for j in sorted({i, (i + 1) % n}, reverse=True):
                del pts[j]
            changed = True
            break
    ring = Polygon(pts)
    if len(pts) < 3 or not ring.is_valid or ring.area <= 1e-6:
        return [tuple(s) for s in segments]               # a merge that breaks the outline: the outline as it is
    return [(pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts))]


class Leg:
    """One outline segment as a kitchen leg: 0.05 m bins along it saying what may stand there (a counter, the
    fridge, the hob), each with its aisle in front inside the room and off the fixed pieces. 26 Oct 2026: ``seg``
    is the segment ``(a, b)`` of the merged outline (``run_outline``); without it the room's segment ``k``."""

    def __init__(self, space: Space, k: int, depth: float, aisle: float, seg: Optional[tuple] = None):
        self.k = k
        a, b = seg if seg is not None else space.ctx.segments[k]
        self.a = a
        self.length = G.distance(a, b)
        self.u = ((b[0] - a[0]) / self.length, (b[1] - a[1]) / self.length)
        self.n = G.unit_normal_left(a, b)
        self.rot = placer._rotation_for_normal(self.n)
        self.depth = depth
        self.nb = max(0, int(self.length / BIN_M))
        ok: dict[str, list] = {"kitchen_counter": [], "fridge": [], "stove": []}
        for i in range(self.nb):
            t0, t1 = i * BIN_M, (i + 1) * BIN_M
            fp = self.fp(space, t0, t1, GAP, depth + GAP)
            aisle_ok = not space.zone_layer.hit(self.fp(space, t0, t1, depth + GAP, depth + GAP + aisle))
            for t in ok:
                ok[t].append(aisle_ok and not space.layer_for(t).hit(fp))
        self.flags = ok
        self.bad = {t: np.concatenate([[0], np.cumsum([0 if v else 1 for v in vals])]) for t, vals in ok.items()}

    def fp(self, space: Space, t0: float, t1: float, s0: float, s1: float):
        c = self.point((t0 + t1) / 2.0, (s0 + s1) / 2.0)
        hx, hy = (t1 - t0) / 2.0, (s1 - s0) / 2.0
        return space.box_fp(c, self.rot, (-hx, hx, -hy, hy))

    def ok(self, ftype: str, t0: float, t1: float) -> bool:
        if t0 < -1e-6 or t1 > self.length + 1e-6:
            return False
        i0 = max(0, int(math.floor(t0 / BIN_M + 1e-6)))
        i1 = min(self.nb, int(math.ceil(t1 / BIN_M - 1e-6)))
        if i1 <= i0:
            return False
        bad = self.bad[ftype]
        return int(bad[i1] - bad[i0]) == 0

    def intervals(self) -> list[tuple[float, float]]:
        """Maximal stretches (t) where a counter may stand, within the segment's ends."""
        out, start = [], None
        flags = self.flags["kitchen_counter"] + [False]
        for i, ok in enumerate(flags):
            if ok and start is None:
                start = i
            elif not ok and start is not None:
                t0, t1 = max(GAP, start * BIN_M), min(self.length - GAP, i * BIN_M)
                if t1 - t0 > 0.3:
                    out.append((round(t0, 3), round(t1, 3)))
                start = None
        return out

    def point(self, t: float, s: float) -> tuple[float, float]:
        return self.a[0] + self.u[0] * t + self.n[0] * s, self.a[1] + self.u[1] * t + self.n[1] * s

    def spot(self, ftype: str, t0: float, t1: float, role: str) -> Spot:
        c = self.point((t0 + t1) / 2.0, self.depth / 2.0 + GAP)
        return Spot(ftype, (round(c[0], 4), round(c[1], 4)), self.rot, (round(t1 - t0, 3), self.depth), role, True)


def _convex_turn(space: Space, k: int, segs: Optional[list] = None) -> bool:
    """The corner between segment k and the next turns left by about 90 degrees (an inner corner of the room).
    ``segs``: the outline (26 Oct 2026: the merged one of ``run_outline``; default the room's segments)."""
    segs = segs if segs is not None else space.ctx.segments
    a, b = segs[k]
    c, d = segs[(k + 1) % len(segs)]
    v1 = (b[0] - a[0], b[1] - a[1])
    v2 = (d[0] - c[0], d[1] - c[1])
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    ang = G.angle_difference_deg(math.degrees(math.atan2(v1[1], v1[0])), math.degrees(math.atan2(v2[1], v2[0])))
    return cross > 0 and abs(ang - 90.0) < 3.0


class Path:
    """A run along one or more legs, walked from its start (the fridge's end). ``parts``: ``[(leg, t0, t1)]`` in the
    outline's order; ``forward`` walks them in that order with t going up, else backwards with t going down. The
    corner square of an L or U (the dead corner) belongs to the leg that ends at the corner in the outline's order."""

    def __init__(self, legs: dict, parts: list, forward: bool, depth: float):
        self.L = legs
        self.parts = list(parts) if forward else list(reversed(parts))
        self.forward = forward
        self.offsets = []
        q = 0.0
        for k, t0, t1 in self.parts:
            self.offsets.append((q, q + (t1 - t0), k, t0, t1))
            q += t1 - t0
        self.total = q
        sq = depth + GAP
        self.corners = []
        for j in range(len(self.offsets) - 1):
            if forward:
                end = self.offsets[j][1]
                self.corners.append((end - sq, end))
            else:
                start = self.offsets[j + 1][0]
                self.corners.append((start, start + sq))

    def where(self, q0: float, q1: float) -> Optional[tuple[int, float, float]]:
        for s0, s1, k, t0, t1 in self.offsets:
            if s0 - 1e-6 <= q0 and q1 <= s1 + 1e-6:
                if self.forward:
                    return k, t0 + (q0 - s0), t0 + (q1 - s0)
                return k, t1 - (q1 - s0), t1 - (q0 - s0)
        return None

    def module_ok(self, ftype: str, q0: float, q1: float) -> Optional[tuple[int, float, float]]:
        w = self.where(q0, q1)
        if w is None or not all(q1 <= c0 + 1e-6 or q0 >= c1 - 1e-6 for c0, c1 in self.corners):
            return None
        if not self.L[w[0]].ok(ftype, w[1], w[2]):
            return None
        return w

    def front_mid(self, w: tuple[int, float, float]) -> tuple[float, float]:
        leg = self.L[w[0]]
        return leg.point((w[1] + w[2]) / 2.0, leg.depth + GAP)

    def spots(self, appliances: list[tuple[float, float, str, str]]) -> list[Spot]:
        """The appliances and one counter per free stretch of each leg."""
        out = []
        for s0, s1, k, _t0, _t1 in self.offsets:
            cuts = sorted((max(a0, s0), min(a1, s1), t, role) for a0, a1, t, role in appliances
                          if a0 < s1 - 1e-6 and a1 > s0 + 1e-6)
            cursor = s0
            for a0, a1, t, role in cuts:
                if a0 - cursor > 0.05:
                    w = self.where(cursor, a0)
                    out.append(self.L[k].spot("kitchen_counter", w[1], w[2], "counter"))
                w = self.where(a0, a1)
                out.append(self.L[k].spot(t, w[1], w[2], role))
                cursor = a1
            if s1 - cursor > 0.05:
                w = self.where(cursor, s1)
                out.append(self.L[k].spot("kitchen_counter", w[1], w[2], "counter"))
        return out


def _lengths(available: float, wanted: tuple) -> list[float]:
    return sorted({round(min(available, x), 3) for x in wanted if x <= available + 1e-6} | {round(available, 3)},
                  reverse=True)


# The run lengths the search tries (``_run_paths``, ``_galley_paths``) and the hard limits of the layouts
# (``_run_layouts``, ``_galley_layouts``). 26 Oct 2026: a kitchen-run option marked ``fallback`` (groups.yaml, the
# compact runs) takes the run's ``compact`` block over these: shorter runs and legs of real module sizes, a 0.30 m base
# unit as the least landing, the work triangle scored instead of hard (the ``compact_run`` tier reports it as minor).
RUN_LIMITS = {"i_min": 3.0, "i_lengths": (3.6, 3.0), "leg_min": 1.2, "leg_lengths": (2.4, 1.8), "galley_a_min": 1.8,
              "galley_a_lengths": (2.4, 1.8), "galley_b_min": 1.2, "galley_b_lengths": (1.2,), "landing_min": None,
              "triangle": "hard", "wall_min": LEG_MIN_M}


def run_limits(run: dict) -> dict:
    """``RUN_LIMITS`` with the run's ``compact`` block over them when the run is a compact fallback (``_option_run``
    sets ``compact_fallback``)."""
    out = dict(RUN_LIMITS)
    if run.get("compact_fallback"):
        out.update({k: (tuple(v) if isinstance(v, list) else v) for k, v in (run.get("compact") or {}).items()})
    return out


def _run_paths(space: Space, legs: dict, shape: str, depth: float, max_leg: float, segs: Optional[list] = None,
               limits: Optional[dict] = None) -> list[list[tuple]]:
    """The parts ``[(leg, t0, t1)]`` of every run of one shape (outline order). 26 Oct 2026: ``segs`` the outline the
    legs stand on (``run_outline``), ``limits`` the run lengths (``run_limits``)."""
    lim = limits or RUN_LIMITS
    segs = segs if segs is not None else space.ctx.segments
    n = len(segs)
    d2 = round(depth + 2 * GAP, 3)
    out = []
    if shape == "I":
        for k, leg in sorted(legs.items()):
            for i0, i1 in leg.intervals():
                for length in _lengths(min(i1 - i0, max_leg), tuple(lim["i_lengths"])):
                    if length < float(lim["i_min"]) - 0.01:
                        continue
                    for start in sorted({i0, round(i1 - length, 3)}):
                        out.append([(k, start, round(start + length, 3))])
    elif shape in ("L", "U"):
        for k in sorted(legs):
            chain = [k, (k + 1) % n] if shape == "L" else [k, (k + 1) % n, (k + 2) % n]
            if len(set(chain)) < len(chain) or any(c not in legs for c in chain) or \
                    not all(_convex_turn(space, c, segs) for c in chain[:-1]):
                continue
            first, last = legs[chain[0]], legs[chain[-1]]
            end_a = round(first.length - GAP, 3)
            ia = next(((i0, i1) for i0, i1 in first.intervals() if i1 >= end_a - 1e-6), None)
            ib = next(((i0, i1) for i0, i1 in last.intervals() if i0 <= d2 + 1e-6), None)
            if ia is None or ib is None:
                continue
            mids = []
            for mid in chain[1:-1]:
                m = legs[mid]
                if any(i0 <= d2 + 1e-6 and i1 >= m.length - GAP - 1e-6 for i0, i1 in m.intervals()):
                    mids.append((mid, d2, round(m.length - GAP, 3)))
            if len(mids) != len(chain) - 2:
                continue
            for la in _lengths(min(end_a - ia[0], max_leg), tuple(lim["leg_lengths"])):
                for lb in _lengths(min(ib[1] - d2, max_leg), tuple(lim["leg_lengths"])):
                    if la < float(lim["leg_min"]) or lb < float(lim["leg_min"]):
                        continue
                    out.append([(chain[0], round(end_a - la, 3), end_a)] + mids + [(chain[-1], d2, round(d2 + lb, 3))])
    return out


def _triangle_ok(legs_m: tuple) -> bool:
    """The NKBA work triangle: every leg within ``triangle_leg`` and the sum within ``triangle_sum``."""
    leg_rule, sum_rule = GR.rule("triangle_leg"), GR.rule("triangle_sum")
    return all(leg_rule["min"] - 1e-9 <= v <= leg_rule["max"] + 1e-9 for v in legs_m) and \
        sum(legs_m) <= sum_rule["max"] + 1e-9


def _run_layouts(path: Path, run: dict, space: Space) -> list[tuple]:
    """Module layouts of one path, best first: ``(spots, terms, key)``. The fridge stands at the path start, the sink
    and the hob after it; the minimum landings and the work-triangle legs are hard, the recommended landings, a
    compact triangle and the sink under a window score. 26 Oct 2026: a compact fallback run (``run_limits``) takes
    its own least landing (a 0.30 m base unit), every hob size of its modules, and scores the work triangle (a
    straight 2.4 m run cannot hold 1.20 m legs) instead of refusing it."""
    lim = run_limits(run)
    mods = run["modules"]
    fr_w = float(mods["fridge"]["sizes"][0][0])
    hob_ws = [float(s[0]) for s in mods["hob"]["sizes"]] if lim["landing_min"] is not None else \
        [float(mods["hob"]["sizes"][0][0])]
    land = {k: GR.rule_min(mods[k]["landing"]) for k in mods}
    c1_min, c2_min = max(land["fridge"], 0.40), max(land["sink"], 0.50)
    if lim["landing_min"] is not None:
        c1_min = c2_min = float(lim["landing_min"])
    soft_triangle = lim["triangle"] == "soft"
    total = path.total
    fr = path.module_ok("fridge", 0.0, fr_w)
    if fr is None:
        return []
    f_pt = path.front_mid(fr)
    wins = [w.inner_point for w in space.ctx.windows]
    results = []
    for hob_w in hob_ws:
        for sink_size in mods["sink"]["sizes"]:
            sw = float(sink_size[0])
            q_s = fr_w + c1_min
            while q_s + sw + c2_min + hob_w <= total + 1e-6:
                sk = path.module_ok("kitchen_counter", q_s, q_s + sw)
                if sk is not None:
                    s_pt = path.front_mid(sk)
                    hobs = {round(q_s + sw + c, 3) for c in (c2_min, 0.6, 0.9, 1.2)}
                    hobs |= {round(total - hob_w - c, 3) for c in (0.0, 0.3, 0.4, 0.6)}
                    for q_h in sorted(hobs):
                        c2, c3 = q_h - (q_s + sw), total - (q_h + hob_w)
                        if c2 < c2_min - 1e-6 or c3 < -1e-6 or (1e-6 < c3 < 0.30 - 1e-6):
                            continue
                        hb = path.module_ok("stove", q_h, q_h + hob_w)
                        if hb is None:
                            continue
                        h_pt = path.front_mid(hb)
                        legs_m = (G.distance(f_pt, s_pt), G.distance(s_pt, h_pt), G.distance(h_pt, f_pt))
                        tri = _triangle_ok(legs_m)
                        if not tri and not soft_triangle:
                            continue
                        c1 = q_s - fr_w
                        rec = (c1 >= GR.rule_rec("fridge_landing"),
                               c2 >= GR.rule_rec("sink_landing") + GR.rule_min("hob_landing"),
                               c3 >= GR.rule_rec("hob_landing"))
                        sink_c = path.L[sk[0]].point((sk[1] + sk[2]) / 2.0, 0.0)
                        share = (sum(rec) + int(tri)) / 4.0 if soft_triangle else sum(rec) / 3.0
                        terms = {"recommended": round(share, 4),
                                 "wall_use": round(max(0.0, 1.0 - abs(sum(legs_m) - 4.5) / 4.5), 4),
                                 "sink_window": 1.0 if any(G.distance(sink_c, w) <= SINK_WINDOW_M + sw / 2.0
                                                           for w in wins) else 0.0}
                        key = (round(q_s, 2), round(q_h, 2), sw) + ((hob_w,) if len(hob_ws) > 1 else ())
                        results.append((_score(terms), key, terms))
                q_s = round(q_s + 0.1, 3)
    results.sort(key=lambda r: (-r[0], r[1]))
    out = []
    for _sc, key, terms in results[:2]:
        q_s, q_h, sw = key[:3]
        hob_w = key[3] if len(key) > 3 else hob_ws[0]
        spots = path.spots([(0.0, fr_w, "fridge", "fridge"), (q_s, q_s + sw, "sink_kitchen", "sink"),
                            (q_h, q_h + hob_w, "stove", "hob")])
        out.append((spots, terms, key))
    return out


def _galley_paths(legs: dict, depth: float, aisle: float, limits: Optional[dict] = None) -> list:
    """Two opposite legs ``(leg A part, leg B part)``: fridge and sink on A, the hob on B, the aisle between.
    26 Oct 2026: ``limits`` the leg lengths (``run_limits``; the compact fallback takes shorter legs)."""
    lim = limits or RUN_LIMITS
    out = []
    keys = sorted(legs)
    for i, ka in enumerate(keys):
        for kb in keys[i + 1:]:
            A, B = legs[ka], legs[kb]
            if G.angle_difference_deg(math.degrees(math.atan2(A.n[1], A.n[0])),
                                      math.degrees(math.atan2(-B.n[1], -B.n[0]))) > 2.0:
                continue
            gap = abs((B.a[0] - A.a[0]) * A.n[0] + (B.a[1] - A.a[1]) * A.n[1])
            if gap < 2 * (depth + GAP) + aisle - 1e-6 or gap > 2 * (depth + GAP) + 1.8:
                continue
            for ia in A.intervals():
                for ib in B.intervals():
                    for la in _lengths(min(ia[1] - ia[0], 3.6), tuple(lim["galley_a_lengths"])):
                        for lb in _lengths(min(ib[1] - ib[0], 2.4), tuple(lim["galley_b_lengths"])):
                            if la < float(lim["galley_a_min"]) - 0.01 or lb < float(lim["galley_b_min"]) - 0.01:
                                continue
                            pa, pb = (ka, ia[0], round(ia[0] + la, 3)), (kb, ib[0], round(ib[0] + lb, 3))
                            out += [(pa, pb), (pb, pa)]
    return out


def _galley_layouts(legs: dict, parts: tuple, forward: bool, run: dict) -> list[tuple]:
    """Fridge and sink on the first leg (from its start in the walk direction), the hob on the second. 26 Oct 2026:
    a compact fallback run (``run_limits``) takes its own least landing, every hob size of its modules and scores the
    work triangle instead of refusing it (as ``_run_layouts``)."""
    lim = run_limits(run)
    mods = run["modules"]
    depth = float(run["depth"])
    fr_w = float(mods["fridge"]["sizes"][0][0])
    hob_ws = [float(s[0]) for s in mods["hob"]["sizes"]] if lim["landing_min"] is not None else \
        [float(mods["hob"]["sizes"][0][0])]
    land = {k: GR.rule_min(mods[k]["landing"]) for k in mods}
    c1_min, c2_min, c_hob = max(land["fridge"], 0.40), max(land["sink"], 0.5), max(land["hob"], 0.3)
    if lim["landing_min"] is not None:
        c1_min = c2_min = c_hob = float(lim["landing_min"])
    soft_triangle = lim["triangle"] == "soft"
    pa, pb = Path(legs, [parts[0]], forward, depth), Path(legs, [parts[1]], forward, depth)
    fr = pa.module_ok("fridge", 0.0, fr_w)
    if fr is None:
        return []
    f_pt = pa.front_mid(fr)
    results = []
    for hob_w in hob_ws:
        for sink_size in mods["sink"]["sizes"]:
            sw = float(sink_size[0])
            q_s = fr_w + c1_min
            while q_s + sw + c2_min <= pa.total + 1e-6:
                sk = pa.module_ok("kitchen_counter", q_s, q_s + sw)
                if sk is not None:
                    s_pt = pa.front_mid(sk)
                    q_h = c_hob
                    while q_h + hob_w <= pb.total + 1e-6:
                        c3 = pb.total - (q_h + hob_w)
                        hb = pb.module_ok("stove", q_h, q_h + hob_w)
                        if hb is not None and not (1e-6 < c3 < 0.30 - 1e-6):
                            h_pt = pb.front_mid(hb)
                            lm = (G.distance(f_pt, s_pt), G.distance(s_pt, h_pt), G.distance(h_pt, f_pt))
                            tri = _triangle_ok(lm)
                            if tri or soft_triangle:
                                good = 1.0 if (q_s - fr_w) >= 0.6 and c3 >= 0.38 else 0.5
                                terms = {"recommended": round((good + int(tri)) / 2.0, 4) if soft_triangle else good,
                                         "wall_use": round(max(0.0, 1.0 - abs(sum(lm) - 4.5) / 4.5), 4),
                                         "sink_window": 0.0}
                                key = (round(q_s, 2), round(q_h, 2), sw) + ((hob_w,) if len(hob_ws) > 1 else ())
                                results.append((_score(terms), key, terms))
                        q_h = round(q_h + 0.1, 3)
                q_s = round(q_s + 0.1, 3)
    results.sort(key=lambda r: (-r[0], r[1]))
    out = []
    for _sc, key, terms in results[:2]:
        q_s, q_h, sw = key[:3]
        hob_w = key[3] if len(key) > 3 else hob_ws[0]
        spots = pa.spots([(0.0, fr_w, "fridge", "fridge"), (q_s, q_s + sw, "sink_kitchen", "sink")])
        spots += pb.spots([(q_h, q_h + hob_w, "stove", "hob")])
        out.append((spots, terms, key))
    return out


def _option_run(template: dict, oname: str) -> dict:
    """The run of a kitchen-run option: the template's ``run`` with the option's module sizes (``modules``: a 0.70 m
    fridge, a 1.00 m double sink ...). 26 Oct 2026: a ``fallback`` option is marked ``compact_fallback`` (its limits
    are the run's ``compact`` block, ``run_limits``)."""
    run = template["run"]
    opt = template["options"][oname]
    over = opt.get("modules") or {}
    if not over and not opt.get("fallback"):
        return run
    modules = {k: (dict(m, sizes=over[k]["sizes"]) if k in over else m) for k, m in run["modules"].items()}
    out = dict(run, modules=modules)
    if opt.get("fallback"):
        out["compact_fallback"] = True
    return out


def fallback_options(group: str) -> list[str]:
    """26 Oct 2026: the options of a group the solver tries only when none of the program's options fits
    (``fallback: true`` in groups.yaml: the compact kitchen runs), in file order."""
    return [name for name, opt in GR.load_groups()[group]["options"].items() if opt.get("fallback")]


def run_candidates(space: Space, entry: dict, level: int, info: dict) -> list[Cand]:
    template = GR.load_groups()[entry["group"]]
    run = template["run"]
    depth = float(run["depth"])
    # Milestone 13: in a small kitchen the aisle minimum is a scored term (tier small_kitchen): the hard floor is
    # the tier's walkway, the 0.90 m aisle scores through ``recommended``.
    over = space.overrides.get("kitchen_aisle")
    aisle = float(over["min"]) if over else GR.rule_min("kitchen_aisle")
    zone_poly = info["zones"].get(entry.get("zone_id"))
    # 26 Oct 2026: the legs stand on the outline with its short jogs merged (``run_outline``); the compact fallback
    # takes shorter walls as legs (its ``wall_min``).
    segs = run_outline(space.ctx.segments)
    leg_cache: dict = {}

    def legs_of(wall_min: float) -> dict:
        out_legs = {}
        for k, (a, b) in enumerate(segs):
            if G.distance(a, b) >= wall_min - 1e-9:
                if k not in leg_cache:
                    leg_cache[k] = Leg(space, k, depth, aisle, (a, b))
                out_legs[k] = leg_cache[k]
        return out_legs

    options = [entry["chosen"]] if entry.get("chosen") else list(entry["options"])
    out = []
    budget = info["budget"]

    def search(onames: list[str]) -> None:
        for oname in onames:
            shape = template["options"][oname]["shape"]
            run = _option_run(template, oname)
            lim = run_limits(run)
            legs = legs_of(float(lim["wall_min"]))
            if shape == "galley":
                jobs = [(parts, fw) for parts in _galley_paths(legs, depth, aisle, lim) for fw in (True, False)]
            else:
                jobs = [(parts, fw) for parts in _run_paths(space, legs, shape, depth, float(run["max_leg"]), segs,
                                                            lim) for fw in (True, False)]
            for parts, forward in jobs:
                if budget["used"] >= budget["generate"]:
                    break
                budget["used"] += 1
                if shape == "galley":
                    layouts = _galley_layouts(legs, parts, forward, run)
                else:
                    layouts = _run_layouts(Path(legs, parts, forward, depth), run, space)
                for spots, terms, key in layouts:
                    if zone_poly is not None and not all(zone_poly.buffer(0.1).contains(Point(s.center))
                                                         for s in spots):
                        continue
                    anchor = next((s for s in spots if s.type == "kitchen_counter"), spots[0])
                    zones = [z for s in spots for z in s.zones(overrides=space.overrides)]
                    cand = Cand(level, entry["group_id"], entry["group"], oname, anchor, spots, zones, dict(terms))
                    if not all(space.allowed(s.type, s.center) for s in spots) or not _finish(space, cand):
                        continue
                    cand.local = _score(cand.terms)
                    cand.sig = (oname, tuple((p[0], int(round(p[1] / MERGE_M)), int(round(p[2] / MERGE_M)))
                                             for p in parts), forward, key)
                    out.append(cand)

    search(options)
    if not out:
        # 26 Oct 2026 (user: "a kitchen must never be empty"): no option of the program fits: the compact runs of
        # real module sizes (groups.yaml ``fallback``), tried only now so a room that holds a full run keeps it.
        search([o for o in fallback_options(entry["group"]) if o not in options])
    return _keep(out, PER_LEVEL, kind=lambda c: template["options"][c.option]["shape"])


# --------------------------------------------------------------------------
# The search
# --------------------------------------------------------------------------

@dataclass
class Node:
    cands: tuple
    occ: np.ndarray
    res: np.ndarray
    score: float
    sig: tuple
    polys: list = field(default_factory=list)
    zfps: list = field(default_factory=list)


class Walk:
    """Walkways on the raster for the beam's nodes (see the module docstring, step 4)."""

    def __init__(self, space: Space):
        self.space = space
        R = space.R
        self.seeds = {}
        for door in space.ctx.doors:
            if door.zone is not None and not door.zone.is_empty:
                m = R.polygon_mask(door.zone) & R.inside
                if m.any():
                    self.seeds[door.id] = m
        self.entrance = GC.entrance_door(space.building, space.room, space.ctx)
        over = space.overrides                        # Milestone 13: a small kitchen's walkway tier
        self.main = float(over["walkway_main"]["min"]) if "walkway_main" in over else GR.rule_min("walkway_main")
        self.sec = float(over["walkway"]["min"]) if "walkway" in over else GR.rule_min("walkway")
        self.base_cover = None
        base = self.state(space.fixed_mask)
        # Required: every door pair (at its width) the room with its fixed pieces connects.
        self.required = [(a, b, w) for a, b, w, ok in base["pairs"] if ok]
        self.base_cover = base["cover"]

    def state(self, occ: np.ndarray, zfps=()) -> dict:
        R = self.space.R
        free = R.inside & ~occ
        dist = R.clearance(free)
        labels = {w: R.components(dist >= w / 2.0 - 1e-6)[1] for w in (self.sec, self.main)}
        comps = {w: {d: set(int(v) for v in np.unique(labels[w][m]) if v > 0) for d, m in self.seeds.items()}
                 for w in labels}
        pairs = []
        ids = sorted(self.seeds)
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                w = self.main if self.entrance in (a, b) else self.sec
                pairs.append((a, b, w, bool(comps[w][a] & comps[w][b])))
                if w == self.main:
                    pairs.append((a, b, self.sec, bool(comps[self.sec][a] & comps[self.sec][b])))
        zones_ok = True
        cover = None
        if self.entrance in self.seeds and (zfps or self.base_cover is None):
            reach_ids = list(comps[self.sec][self.entrance])
            reach = np.isin(labels[self.sec], reach_ids) if reach_ids else np.zeros_like(free)
            cover = Layer(R.dilate(reach, self.sec / 2.0) & free)
            for zfp in zfps:
                sub = free[zfp[1]:zfp[2], zfp[3]:zfp[4]] if zfp[0] == "r" else free.ravel()[zfp[1]]
                if not sub.any():
                    continue
                if not cover.hit(zfp):
                    zones_ok = False             # a new piece's use zone no walkway reaches (G11)
                    break
        return {"pairs": pairs, "zones_ok": zones_ok, "cover": cover}

    def ok(self, occ: np.ndarray, zfps) -> bool:
        st = self.state(occ, zfps)
        have = {(a, b, w): ok for a, b, w, ok in st["pairs"]}
        if any(not have.get((a, b, w), False) for a, b, w in self.required):
            return False
        return st["zones_ok"]


def _expand(node: Node, cand: Cand, layers: tuple) -> bool:
    occres, occ = layers
    for fp in cand.fps:
        if occres.hit(fp):
            return False
    for zfp in cand.zfps:
        if occ.hit(zfp):
            return False
    for poly, bb in zip(cand.polys, cand.bboxes):
        for q in node.polys:
            if _close(bb, q.bounds) and poly.intersection(q).area > placer.AREA_EPS:
                return False
    return True


def _levels(space: Space, prog: dict, info: dict) -> list[tuple[dict, list[Cand], bool]]:
    """One search level per anchored group or run, one per set member; with their candidates."""
    levels = []
    for k, entry in enumerate(prog["groups"]):
        template = GR.load_groups()[entry["group"]]
        info["groups_left"] = len(prog["groups"]) - k     # 23 Oct 2026: each group's fair share of the budget
        if entry.get("note", "").startswith(("unverified", "no completion")):
            continue
        if template["layout"] == "anchored":
            if entry.get("resolve"):                   # Milestone 13: the drawn group re-solved as one unit
                levels.append((entry, anchored_candidates(space, entry, len(levels), info), entry["required"]))
                continue
            if entry.get("drawn") and (not template["partners"] or not entry.get("missing")):
                continue                               # a drawn wardrobe, a drawn table with its chairs: nothing to add
            levels.append((entry, anchored_candidates(space, entry, len(levels), info), entry["required"]))
        elif template["layout"] == "run":
            if entry.get("drawn"):
                if "fridge" not in (entry.get("missing") or []):
                    continue                           # a drawn run: only a missing fridge is added beside it
                member = {"role": "fridge", "type": "fridge", "sizes": [[0.6, 0.65], [0.7, 0.7]], "align": "any"}
                levels.append((entry, member_candidates(space, entry, [member], len(levels), info), False))
            else:
                levels.append((entry, run_candidates(space, entry, len(levels), info), entry["required"]))
        else:
            options = [entry["chosen"]] if entry.get("chosen") else list(entry["options"])
            # 23 Oct 2026 (group options 10x): unless chosen, a set's extra options add only their sizes (below), not
            # their members or member types (a hall keeps its shoe cabinet; no bench, plant or second washbasin
            # unasked, as every optional member that fits would be placed).
            sized = options
            if not entry.get("chosen"):
                options = [o for o in options if GR.is_core(template["options"][o])] or options
            have = {info["by_id"][m]["type"] for m in entry.get("members") or [] if m in info["by_id"]}
            if entry.get("drawn") and entry.get("anchor_id") in info["by_id"]:
                have.add(info["by_id"][entry["anchor_id"]]["type"])
            # bathroom sense of 26 Oct 2026: a piece the room keeps (drawn, or an added one the solver does not
            # re-place) of a member's type is that member, whether or not it is in the entry (a drawn washbasin the fit
            # hung on the wall, a set the agent's place_group asks for again): adopted, never added a second time
            have |= GR.held_types(space.fixed_items)
            roles = []
            for oname in options:
                for role in template["options"][oname].get("members", []):
                    if role not in roles:
                        roles.append(role)
            extra = {}                                 # 23 Oct 2026: the options' member sizes (by type)
            for oname in sized:
                for ftype, sizes in (template["options"][oname].get("partner_sizes") or {}).items():
                    extra.setdefault(ftype, []).extend(tuple(s) for s in sizes)
            for role in roles:
                types = [m for m in template["members"] if m["role"] == role and (
                    not m.get("option") or any(template["options"][o].get(role) == m["type"] for o in options))]
                if not types:
                    continue
                if entry.get("chosen"):                # the chosen option's sizes first
                    types = [dict(m, sizes=list(dict.fromkeys(extra.get(m["type"], []) +
                                                              [tuple(s) for s in m["sizes"]]))) for m in types]
                elif extra:
                    types = [dict(m, sizes=list(dict.fromkeys([tuple(s) for s in m["sizes"]] +
                                                              extra.get(m["type"], [])))) for m in types]
                if any(m["type"] in have for m in types) or (role == "bath" and have & {"shower", "bathtub"}):
                    continue                           # drawn already: only what is missing is added
                if entry.get("drawn") and not any(m.get("required") for m in types):
                    continue                           # a drawn set gets only its missing required members
                required = entry["required"] and any(m.get("required") for m in types)
                levels.append((entry, member_candidates(space, entry, types, len(levels), info), required))
    return levels


ROLE_OF_TYPE = {"tv_unit": "tv", "table_coffee": "coffee", "ottoman": "coffee", "armchair": "armchair",
                "nightstand": "nightstand", "bench": "bench", "chair": "chair", "office_chair": "chair",
                "bar_stool": "stool"}


def _info(space: Space, building: dict, room_id: str, prog: dict, budget: dict) -> dict:
    by_id = {f["id"]: f for f in building.get("furniture") or [] if f.get("room_id") == room_id}
    filled: dict = {}
    near: dict = {}
    resolve: dict = {}
    for entry in prog["groups"]:
        if not entry.get("drawn") or entry.get("anchor_id") not in by_id:
            continue
        if entry.get("resolve"):
            # Milestone 13: the group's drawn pieces are re-placed: nothing is filled, the drawn centres are kept.
            res = entry["resolve"]
            dg = next((g for g in GR.drawn_groups(building, room_id) if g["anchor_id"] == entry["anchor_id"]), None)
            roles_of = (dg or {}).get("roles") or {}
            members = [(by_id[m], roles_of.get(m) or ROLE_OF_TYPE.get(by_id[m]["type"], "partner"))
                       for m in res.get("members") or [] if m in by_id]
            centre = list(res.get("centre") or GR.drawn_centre(by_id[entry["anchor_id"]]))
            resolve[entry["group_id"]] = {"anchor": by_id[entry["anchor_id"]], "members": members, "centre": centre,
                                          "reason": res.get("reason", "")}
            near[entry["group_id"]] = [tuple(centre)]
            continue
        roles: dict = {}
        anchor = by_id[entry["anchor_id"]]
        members = [by_id[m] for m in entry.get("members") or [] if m in by_id]
        for m in members:
            role = ROLE_OF_TYPE.get(m["type"])
            if role:
                roles[role] = roles.get(role, 0) + 1
        if any(m["type"] == "nightstand" for m in members) and anchor.get("type") in GC.BED_TYPES:
            bed = placer.drawn_piece(anchor)
            roles["nightstand_sides"] = sorted({GC.nightstand_place(bed, placer.drawn_piece(m))["side"]
                                                for m in members if m["type"] == "nightstand"})
            roles.pop("nightstand", None)
        filled[entry["group_id"]] = roles
        near[entry["group_id"]] = [tuple(placer.drawn_piece(m).center) for m in [anchor] + members]
    zones = {z["zone_id"]: Polygon(z["polygon"]).buffer(0) for z in prog.get("zones") or []}
    previous = [(f["type"], tuple(placer.drawn_piece(f).center)) for f in by_id.values()
                if f.get("source") == "added_by_ai" and f.get("type") not in schemas.MOUNTED_TYPES
                and f.get("footprint")]
    drawn_run = any(f.get("source") == "from_documents" and f.get("type") in GR.KITCHEN_RUN_TYPES
                    and f.get("build") is not False for f in by_id.values())
    return {"by_id": by_id, "filled": filled, "near": near, "zones": zones, "budget": budget,
            "entrance": GC.entrance_door(building, space.room, space.ctx),
            "kitchen_points": _kitchen_targets(space), "previous": previous, "resolve": resolve,
            "drawn_run": drawn_run}


def _zone_poly(zone) -> Polygon:
    _name, center, rotation, box = zone
    return placer._local_box(center, rotation, *box)


def access_zone(space: Space, f: dict, p: placer.Piece) -> Optional[tuple]:
    """Fix round after P4b (module docstring): ``("access", centre, rotation, box)`` for a drawn ``ACCESS_ZONE_TYPES``
    piece whose drawn front zone lies mostly outside the room: its use zone on the one other side with at least
    ``ACCESS_INSIDE_SHARE`` inside the room and off every other drawn piece, cut to the room (the box of its part in
    the room); None when the drawn front opens into the room or no single side does."""
    if f.get("type") not in ACCESS_ZONE_TYPES or f.get("source") != "from_documents":
        return None
    room = space.ctx.polygon

    def front_of(rotation: float, size) -> Optional[tuple]:
        spot = Spot(f["type"], p.center, rotation, size, "fixed", False, existing_id=f["id"])
        return next((z for z in spot.zones(overrides=space.overrides) if z[0] == "front"), None)

    def share(zone) -> float:
        poly = _zone_poly(zone)
        return poly.intersection(room).area / poly.area if poly.area > 0 else 0.0

    drawn = front_of(p.rotation_deg, p.size)
    if drawn is None or share(drawn) >= ACCESS_INSIDE_SHARE - 1e-9:
        return None
    others = [q for g, q in zip(space.fixed_items, space.fixed_polys) if g.get("id") != f.get("id")
              and g.get("build") is not False and g.get("type") != "unknown"]
    open_sides = []
    for turn in (90.0, 180.0, 270.0):
        size = (p.size[1], p.size[0]) if turn != 180.0 else p.size
        zone = front_of(G.normalise_angle(p.rotation_deg + turn), size)
        if zone is None or share(zone) < ACCESS_INSIDE_SHARE - 1e-9:
            continue
        poly = _zone_poly(zone)
        if any(poly.intersection(q).area > placer.AREA_EPS for q in others):
            continue
        open_sides.append(zone)
    if len(open_sides) != 1:
        return None                              # no open side, or several: the access side is unclear
    _name, center, rotation, box = open_sides[0]
    inside = _zone_poly(open_sides[0]).intersection(room)
    r = math.radians(rotation)
    c, s_ = math.cos(r), math.sin(r)
    pts = [((x - center[0]) * c + (y - center[1]) * s_, -(x - center[0]) * s_ + (y - center[1]) * c)
           for geom in getattr(inside, "geoms", [inside]) for x, y in getattr(geom, "exterior", geom).coords]
    if not pts:
        return None
    xs, ys = [q[0] for q in pts], [q[1] for q in pts]
    cut = (max(box[0], min(xs)), min(box[1], max(xs)), max(box[2], min(ys)), min(box[3], max(ys)))
    if cut[1] - cut[0] <= 1e-6 or cut[3] - cut[2] <= 1e-6:
        return None
    return ("access", center, rotation, tuple(round(v, 4) for v in cut))


def fixed_zones(space: Space) -> list:
    """The use zones of the fixed (drawn) built pieces that are free with the fixed pieces alone: no new piece may
    stand there (a wardrobe in a drawn bed's side clearance), and the walkways must keep reaching them. Fix round after
    P4b: plus the ``access_zone`` of a drawn washer whose drawn front opens out of the room."""
    out = []
    chairs = [(f, p) for f, p in zip(space.fixed_items, space.fixed_pieces) if f.get("type") in GC.SEAT_TYPES
              and f.get("build") is not False]
    for f, p in zip(space.fixed_items, space.fixed_pieces):
        if f.get("build") is False or f.get("type") == "unknown":
            continue
        spot = Spot(f["type"], p.center, p.rotation_deg, p.size, "fixed", False, p.shape, p.chaise_side,
                    existing_id=f["id"])
        zones = _one_side(space, spot, spot.zones(overrides=space.overrides), FIXED_ZONE_INFLATE_M)
        if zones is None:
            zones = [z for z in spot.zones(overrides=space.overrides) if z[0] not in ("left", "right")]
        out += [z for z in zones if not space.zone_layer.hit(space.zone_fp(z, FIXED_ZONE_INFLATE_M))]
        access = access_zone(space, f, p)            # fix round after P4b (module docstring)
        if access is not None:
            out.append(access)
        if f["type"] == "table_dining":
            # A drawn table keeps the pull-out room behind its drawn chairs (they stand in it, so it is not tested).
            poly = p.polygon()
            sides = {GC._side_of(p, c.center) for _cf, c in chairs if c.polygon().distance(poly) <= 0.6}
            out += [(f"pullout_drawn_{s}",) + z[1:] for s, z in _pullout_zones(spot, sides).items()]
    return out


def resolve_skip_fps(space: Space, levels: list, info: dict) -> dict:
    """Milestone 13: per re-solved level, the raster footprints and polygons of its drawn pieces as drawn: when the
    level is skipped (no place within the bound) the pieces stay where they are drawn and the later levels must
    treat them as occupied again."""
    out = {}
    for i, (entry, _cands, _req) in enumerate(levels):
        res = entry.get("resolve")
        if not res:
            continue
        fps, polys = [], []
        for pid in [res["anchor_id"]] + list(res.get("members") or []):
            f = info["by_id"].get(pid)
            if f is None or not f.get("footprint"):
                continue
            try:
                s = _spot_from(f, "kept")
            except (KeyError, TypeError, ValueError):
                continue
            fps += space.spot_fps(s)
            polys.append(s.piece().polygon())
        out[i] = (fps, polys)
    return out


def _search(space: Space, levels: list, walk: Walk, budget: dict, skip_fps: Optional[dict] = None) -> list[Node]:
    res = np.zeros_like(space.fixed_mask)
    reach = []
    for z in fixed_zones(space):
        zfp = space.zone_fp(z)
        paint(res, zfp)
        if _reached(z) and (walk.base_cover is None or walk.base_cover.hit(zfp)):
            reach.append(zfp)                    # a drawn piece's zone the walkways reach now must stay reached
    root = Node((), space.fixed_mask.copy(), res, 0.0, (), [], reach)
    beam = [root]
    skip_fps = skip_fps or {}
    for level_index, (_entry, cands, required) in enumerate(levels):
        bonus = REQUIRED_BONUS if required else OPTIONAL_BONUS
        children = []
        for node in beam:
            layers = (Layer(node.occ | node.res), Layer(node.occ))
            for cand in cands:
                if budget["nodes"] >= budget["expand"]:
                    break
                budget["nodes"] += 1
                if _expand(node, cand, layers):
                    children.append((node, cand, node.score + bonus + cand.local))
            children.append((node, None, node.score))          # the level skipped
        children.sort(key=lambda c: (-round(c[2], 6), c[0].sig, c[1].sig if c[1] is not None else ()))
        nxt, seen, per_parent, rejected = [], set(), {}, set()
        # Two passes: first at most PER_PARENT children per parent (the beam keeps different earlier choices),
        # then the best of the rest.
        for cap in (PER_PARENT, BEAM_WIDTH):
            for node, cand, score in children:
                if len(nxt) >= BEAM_WIDTH:
                    break
                sig = node.sig + ((cand.sig if cand is not None else ("skip",)),)
                if sig in seen or sig in rejected or per_parent.get(node.sig, 0) >= cap:
                    continue
                if cand is None:
                    child = Node(node.cands + (None,), node.occ, node.res, score, sig, node.polys, node.zfps)
                    if level_index in skip_fps:              # Milestone 13: the drawn group stays as drawn
                        occ = node.occ.copy()
                        for fp in skip_fps[level_index][0]:
                            paint(occ, fp)
                        child = Node(node.cands + (None,), occ, node.res, score, sig,
                                     node.polys + skip_fps[level_index][1], node.zfps)
                else:
                    occ = node.occ.copy()
                    res = node.res.copy()
                    for fp in cand.fps:
                        paint(occ, fp)
                    for zfp in cand.zfps:
                        paint(res, zfp)
                    zfps = node.zfps + cand.rfps           # the zones the walkways must reach
                    budget["walks"] += 1
                    if not walk.ok(occ, zfps):
                        rejected.add(sig)
                        continue
                    child = Node(node.cands + (cand,), occ, res, score, sig, node.polys + cand.polys, zfps)
                seen.add(sig)
                per_parent[node.sig] = per_parent.get(node.sig, 0) + 1
                nxt.append(child)
        beam = sorted(nxt, key=lambda n: (-round(n.score, 6), n.sig)) or beam
    return beam


# --------------------------------------------------------------------------
# Final scoring, verification and the candidates
# --------------------------------------------------------------------------

def _balance(space: Space, node: Node) -> float:
    polys = space.fixed_polys + node.polys
    if not polys:
        return 1.0
    area = sum(p.area for p in polys)
    cx = sum(p.centroid.x * p.area for p in polys) / area
    cy = sum(p.centroid.y * p.area for p in polys) / area
    minx, miny, maxx, maxy = space.ctx.polygon.bounds
    diag = math.hypot(maxx - minx, maxy - miny)
    return round(max(0.0, 1.0 - G.distance((cx, cy), space.centroid) / (0.5 * diag)), 4)


def _seating_crossed(space: Space, node: Node, walk: Walk) -> Optional[float]:
    """1 when the doors stay connected without walking through a seating area (between the sofa's front and its
    TV), else 0; None without a seating group with a TV."""
    occ = None
    for cand in node.cands:
        if cand is None or cand.group != "seating":
            continue
        tv = next((s for s in cand.spots if s.type == "tv_unit"), None)
        if tv is None:
            continue
        a = cand.anchor
        geo = GC.tv_geometry(a.piece(), tv.piece())
        w, d = a.size[0] / 2.0, a.size[1] / 2.0
        if occ is None:
            occ = node.occ.copy()
        paint(occ, space.box_fp(a.center, a.rotation, (-w, w, -d - max(0.0, geo["distance_m"]), -d)))
    if occ is None:
        return None
    return 1.0 if walk.ok(occ, ()) else 0.0


def _circulation(space: Space, node: Node, walk: Walk) -> Optional[float]:
    """The open floor a 0.60 m walkway can use, against the room with its fixed pieces only (a stand-in for the
    circulation term of Merrell et al.: free floor between the doors)."""
    R = space.R
    base = int((R.clearance(R.inside & ~space.fixed_mask) >= walk.sec / 2.0).sum())
    if base == 0:
        return None
    now = int((R.clearance(R.inside & ~node.occ) >= walk.sec / 2.0).sum())
    return round(now / base, 4)


def _final_terms(space: Space, node: Node, walk: Walk) -> dict:
    sums: dict[str, list] = {}
    for cand in node.cands:
        if cand is None:
            continue
        for k, v in cand.terms.items():
            if v is not None:
                sums.setdefault(k, []).append(v)
    terms = {k: round(sum(v) / len(v), 4) for k, v in sorted(sums.items())}
    terms["balance"] = _balance(space, node)
    for name, fn in (("circulation", _circulation), ("seating_crossed", _seating_crossed)):
        value = fn(space, node, walk)
        if value is not None:
            terms[name] = value
    return terms


def _next_number(building: dict, level_id: str) -> int:
    pattern = re.compile(rf"^f_{re.escape(level_id)}_(\d+)$")
    numbers = [int(m.group(1)) for f in building.get("furniture") or [] for m in [pattern.match(f.get("id", ""))] if m]
    return max(numbers, default=0) + 1


def _spot_ids(room: dict, node: Node, start: int) -> list[tuple[int, Spot, str]]:
    """``(level index, spot, piece id)`` of every spot of a node: new pieces are numbered from ``start`` in level
    order, re-solved drawn pieces keep their ids (Milestone 13)."""
    out = []
    number = start
    for i, cand in enumerate(node.cands):
        if cand is None:
            continue
        for s in cand.spots:
            if s.drawn is not None:
                out.append((i, s, s.drawn["id"]))
                continue
            out.append((i, s, f"f_{room['level_id']}_{number:03d}"))
            number += 1
    return out


def _piece_dicts(room: dict, node: Node, start: int, levels: list, info: Optional[dict] = None
                 ) -> tuple[list[dict], list[dict]]:
    """The candidate's new pieces as furniture dicts (ids from ``start``) and its groups (one per group id: a set's
    members share theirs; a drawn anchor stays the group's anchor). Milestone 13: the re-solved drawn pieces of a
    group come back as their drawn dicts with the new place (``_resolved_dict``), the anchor first; the drawn pieces
    of a re-solved level the search skipped come back unchanged (they stay as drawn)."""
    pieces = []
    groups: dict[str, dict] = {}
    ids = iter(_spot_ids(room, node, start))
    for (entry, _cands, _req), cand in zip(levels, node.cands):
        if cand is None:
            res = entry.get("resolve")
            if res and info is not None:
                for pid in [res["anchor_id"]] + list(res.get("members") or []):
                    if pid in info["by_id"]:
                        pieces.append(copy.deepcopy(info["by_id"][pid]))
            continue
        g = groups.setdefault(cand.group_id, {"group_id": cand.group_id, "group": cand.group, "member_ids": [],
                                              "anchor_id": entry.get("anchor_id") if entry.get("drawn") else None,
                                              "option": cand.option})
        sets = GR.load_groups()[cand.group]["layout"] == "set"
        for s in cand.spots:
            _i, _s, pid = next(ids)
            if s.drawn is not None:
                role = "anchor" if s is cand.anchor else "partner"
                if role == "anchor":
                    g["anchor_id"] = pid
                else:
                    g["member_ids"].append(pid)
                pieces.append(_resolved_dict(s, room, cand, role))
                continue
            role = "anchor" if (s is cand.anchor and s.existing_id is None and not entry.get("drawn")
                                and not sets and g["anchor_id"] is None) else "partner"
            if role == "anchor":
                g["anchor_id"] = pid
            else:
                g["member_ids"].append(pid)
            pieces.append(_piece_dict(s, room, pid, cand, role))
    for p in pieces:
        g = p.get("group")
        if isinstance(g, dict) and g.get("group_id") in groups:
            g["anchor_id"] = groups[g["group_id"]]["anchor_id"]
    return pieces, list(groups.values())


def _resolved_dict(s: Spot, room: dict, cand: Cand, role: str) -> dict:
    """Milestone 13 (D5, CLAUDE.md furniture rules): a drawn piece of a re-solved group at its new place: the drawn
    dict with the new footprint and front, ``adjusted_by_ai`` (reason, ``moved_m``, the size change), the drawn
    values kept (``drawn_type``, ``drawn_footprint``, ``drawn_front_deg``, ``drawn_height``), ``drawn_group`` and
    ``group``; a resized or unbuilt piece loses its asset so the refit builds it again. A kept member (not moved)
    only gets ``drawn_group`` and ``group``."""
    f = copy.deepcopy(s.drawn)
    old_fp = dict(f["footprint"])
    rotation = round(G.normalise_angle(s.rotation), 3)
    # Build round 3 (K2): a spot planned with the fitted box records the drawn size where the builder makes that box
    centre, size = s.record_box()
    new_fp = {"center": [round(float(centre[0]), 4), round(float(centre[1]), 4)],
              "size": [round(float(size[0]), 4), round(float(size[1]), 4)], "rotation_deg": rotation}
    frontless = f["type"] in schemas.FRONTLESS_TYPES and f.get("front_deg") is None
    old_size = sorted(round(float(v), 3) for v in old_fp["size"])
    resized = old_size != sorted(round(float(v), 3) for v in new_fp["size"])
    moved = round(float(s.moved), 3)
    res = cand.resolve or {}
    f["group"] = {"group_id": cand.group_id, "group": cand.group, "role": role, "anchor_id": res.get("anchor_id")}
    f["drawn_group"] = {"anchor_id": res.get("anchor_id"), "members": list(res.get("members") or []),
                        "moved_m": moved}
    if s.kept or (moved <= 1e-3 and not resized and (frontless or abs(G.angle_difference_deg(
            G.front_direction_deg(rotation), float(f.get("front_deg") or G.front_direction_deg(
                float(old_fp["rotation_deg"]))))) < 0.5)):
        return f
    if f.get("drawn_type") is None:
        f["drawn_type"] = f["type"]
    if f.get("drawn_footprint") is None:
        f["drawn_footprint"] = old_fp
    if "drawn_front_deg" not in f or f.get("drawn_front_deg") is None:
        f["drawn_front_deg"] = f.get("front_deg")
    if "drawn_height" not in f or f.get("drawn_height") is None:
        f["drawn_height"] = f.get("height")
    f["footprint"] = new_fp
    f["front_deg"] = None if frontless else round(G.front_direction_deg(rotation), 3)
    what = f"moved {moved:.2f} m"
    if resized:
        what += (f", sized {old_fp['size'][0]:.2f} x {old_fp['size'][1]:.2f} m -> {new_fp['size'][0]:.2f} x "
                 f"{new_fp['size'][1]:.2f} m (a real product size)")
    reason = (f"{res.get('reason') or 'the drawn group is re-solved'}: re-solved with its {cand.group} group as one "
              f"unit around the drawn anchor ({role}); {what}")
    f["adjusted_by_ai"] = {"by": "solver", "stage": "layout", "reason": reason, "moved_m": moved,
                           "drawn_group": res.get("anchor_id"), "resized": resized}
    f.setdefault("evidence", []).append({"file": EVIDENCE_FILE, "method": "derived", "confidence": 0.9,
                                         "rule": f"group {cand.group}", "text": reason})
    asset = f.get("asset") if isinstance(f.get("asset"), dict) else None
    if resized or (asset is not None and asset.get("method") in GR.NOT_BUILT_ASSET_METHODS):
        f["asset"] = None
        f.pop("library_gap", None)
        f["build"] = True
    return f


def _rug_dicts(room: dict, node: Node, groups: list[dict]) -> list[dict]:
    """Milestone 13 (R6): the rug members of a node as decor items (``building["decor"]`` format of
    ``wenart.furniture.decor``: ``kind: decor``, ``type: rug``, ``source: added_by_ai``, ``method: rule``, ``host_id``
    None, ``anchor_ids`` the group's anchor and members; ids are given by ``apply_candidate``)."""
    by_group = {g["group_id"]: g for g in groups}
    out = []
    for cand in node.cands:
        if cand is None:
            continue
        g = by_group.get(cand.group_id) or {}
        anchors = [a for a in [g.get("anchor_id")] + list(g.get("member_ids") or []) if a]
        if not anchors:
            continue
        for r in cand.rugs:
            out.append({"kind": "decor", "type": "rug", "level_id": room["level_id"], "room_id": room["id"],
                        "center": [round(float(r.center[0]), 3), round(float(r.center[1]), 3)],
                        "rotation_deg": round(G.normalise_angle(r.rotation), 3),
                        "size": [round(float(r.size[0]), 3), round(float(r.size[1]), 3)], "asset": None,
                        "host_id": None, "anchor_ids": anchors, "source": "added_by_ai",
                        "method": "rule", "group": {"group_id": cand.group_id, "group": cand.group, "role": "rug"},
                        "reason": f"rug member of the {cand.group} group (groups.yaml rug_{'seating' if cand.group == 'seating' else 'bed'}: "
                                  f"{'under the coffee table, front legs on' if cand.group == 'seating' else 'a runner beside the bed'})"})
    return out


def _piece_dict(s: Spot, room: dict, pid: str, cand: Cand, role: str) -> dict:
    rotation = round(G.normalise_angle(s.rotation), 3)
    f = {"id": pid, "level_id": room["level_id"], "room_id": room["id"], "type": s.type, "type_raw": None,
         "source": "added_by_ai",
         "footprint": {"center": [round(s.center[0], 4), round(s.center[1], 4)],
                       "size": [round(float(s.size[0]), 4), round(float(s.size[1]), 4)], "rotation_deg": rotation},
         "front_deg": round(G.front_direction_deg(rotation), 3), "height": schemas.HEIGHTS.get(s.type), "asset": None,
         "status": "verified", "method": "rule",
         "evidence": [{"file": EVIDENCE_FILE, "method": "derived", "confidence": 0.9, "rule": f"group {cand.group}",
                       "text": f"{s.type} ({s.role}) of the {cand.group} group, option {cand.option}, placed by the "
                               f"group solver"}],
         "group": {"group_id": cand.group_id, "group": cand.group, "role": role, "anchor_id": None},
         "layout": {"against_wall": bool(s.against_wall), "solver_role": s.role, "option": cand.option}}
    if s.shape == "L":
        f.update({"shape": "L", "chaise_side": s.chaise_side, "chaise_depth": float(s.size[1]),
                  "seat_depth": schemas.L_SEAT_DEPTH_M, "chaise_width": schemas.L_CHAISE_WIDTH_M})
    return f


def _violation_key(v: dict) -> tuple:
    m = v.get("metrics") or {}
    return (v["check"], str(v["target"]), str(m.get("part") or m.get("zone") or m.get("side") or m.get("to") or ""),
            v["message"] if v["check"] in ("G9", "G10") and v["target"] == v["room_id"] else "")


def verify(base_building: dict, room_id: str, pieces: list[dict],
           unchanged: Iterable[str] = ()) -> tuple[list[str], list[dict]]:
    """(hard failures, group violations) of the room with ``pieces`` added: the placer's geometry (inside, overlap,
    doors, windows) of every new piece and every critical or major group-check violation (G14 aside: a drawn
    piece's type is not the solver's) the fixed pieces alone do not cause. ``unchanged`` (Milestone 13): the ids of
    the drawn pieces in ``pieces`` that come back as drawn (``_unchanged_ids``): they count as fixed, not as new."""
    trial = copy.deepcopy(base_building)
    trial["furniture"] = list(trial.get("furniture") or []) + pieces
    room = next(r for r in trial["rooms"] if r["id"] == room_id)
    ctx = placer.room_context(trial, room)
    # Milestone 13: a drawn piece that comes back unchanged (a kept member, a skipped re-solve) is not new: its own
    # drawn faults are not the candidate's. Review fix (15 Oct 2026): ``adjusted_by_ai`` alone does not tell (the
    # fit's size snap, T1, and earlier agent edits leave one on a piece that stays as drawn here), so the caller
    # names the unchanged ids and they join the base of the group checks below; before, every candidate of a room
    # with such a piece failed on its drawn faults (a wardrobe over the door: doors_free, G11).
    skip = set(unchanged)
    new_ids = {p["id"] for p in pieces if p["id"] not in skip and not (
        p.get("source") == "from_documents" and not isinstance(p.get("adjusted_by_ai"), dict))}
    floor = [f for f in trial["furniture"] if f.get("room_id") == room_id and f.get("build") is not False
             and not schemas.off_floor(f)
             and f.get("type") != "unknown" and f.get("footprint")]
    # Milestone 13 (K2, build round 3): the overlap test runs on the boxes the scene builder makes (a uniformly
    # scaled library model is deeper at its front: ``placer.planned_piece``), as the scene check S2 will see them.
    plist = [placer.planned_piece(f, i) for i, f in enumerate(floor)]
    hard = []
    shrunk = ctx.shrunk.buffer(1e-3, join_style="mitre")
    for f, p in zip(floor, plist):
        if f["id"] not in new_ids:
            continue
        poly = p.polygon()
        if not shrunk.contains(poly):
            hard.append(f"{f['id']}: inside_room ({poly.difference(shrunk).area:.3f} m² outside)")
        for g, q in zip(floor, plist):
            if g["id"] == f["id"] or (g["id"] in new_ids and g["id"] < f["id"]):
                continue
            area = poly.intersection(q.polygon()).area
            if area > placer.AREA_EPS:
                hard.append(f"{f['id']}: no_overlap with {g['id']} ({area:.3f} m²)")
        if placer._opening_blocked(p, ctx):
            hard.append(f"{f['id']}: doors_free / windows_free (on a door strip, a door swing or a window band)")
    base = base_building
    if skip:
        base = dict(base_building, furniture=list(base_building.get("furniture") or [])
                    + [copy.deepcopy(p) for p in pieces if p["id"] in skip])
    # Build round 3 (K2): the group checks (clearances G1-G14) measure the boxes the scene builder makes as well
    # (``placer.planned_building``: a uniformly scaled library model at its fitted depth; the records unchanged).
    base_v = {_violation_key(v) for v in GC.check_room(placer.planned_building(base, room_id), room_id)}
    after = GC.check_room(placer.planned_building(trial, room_id), room_id)
    hard += [f"{v['check']} {v['target']}: {v['message']}" for v in after
             if _violation_key(v) not in base_v and v["severity"] in ("critical", "major") and v["check"] != "G14"]
    return hard, after


def _unchanged_ids(pieces: list[dict], info: dict) -> set:
    """Milestone 13 (review fix of 15 Oct 2026): the drawn pieces a candidate brings back as drawn (a kept member, a
    skipped re-solve, a member matched to its own place): their dicts equal the room's (``group`` and
    ``drawn_group`` aside, which the candidate writes). ``verify`` counts them as fixed, not as new."""
    out = set()
    for p in pieces:
        src = info["by_id"].get(p["id"])
        if src is None or p.get("source") != "from_documents":
            continue
        if _without_group(p) == _without_group(src):
            out.add(p["id"])
    return out


def _without_group(piece: dict) -> dict:
    return {k: v for k, v in piece.items() if k not in ("group", "drawn_group")}


def untyped_unbuilt(f: dict) -> bool:
    """26 Oct 2026 (module docstring, fix round of 26 Oct): a drawn piece the reading left untyped and unbuilt
    (``type`` unknown or empty, ``build: false``). It is in no render (CLAUDE.md: no untyped piece is built), so it is
    no obstacle for the solver; the review list keeps it."""
    return f.get("build") is False and str(f.get("type") or "unknown") == "unknown"


def _fixed_items(building: dict, room_id: str, fixed_ids: set, exclude=()) -> list[dict]:
    """The pieces the solver never moves: drawn pieces (built or not; not a rug outline, not one recorded as not
    furniture, not an untyped unbuilt piece) and the ``fixed_ids``; wall-hung pieces stand above the floor.
    ``exclude`` (Milestone 13): the drawn pieces of a group re-solved as one unit: an unbuilt drawn anchor is never an
    obstacle for its own group. 26 Oct 2026: an untyped unbuilt drawn piece (``untyped_unbuilt``) is no obstacle
    either (real06's 3.99 x 2.40 m f_L0_002 covered the kitchen's walls, so no counter run fitted)."""
    out = []
    not_furniture = {s.get("former_piece_id") for s in building.get("symbols") or [] if s.get("former_piece_id")}
    skip = set(exclude or ())
    for f in building.get("furniture") or []:
        if f.get("room_id") != room_id or not f.get("footprint") or f["id"] in skip:
            continue
        if schemas.off_floor(f):
            continue
        if f["id"] in not_furniture or f.get("not_furniture") or f.get("inferred_as") == "rug":
            continue
        if f.get("source") == "from_documents" and untyped_unbuilt(f) and f["id"] not in fixed_ids:
            continue                                   # 26 Oct 2026: in no render, so no obstacle
        if f.get("source") == "from_documents" or f["id"] in fixed_ids:
            out.append(f)
    return out


def _with_drawn_group(building: dict, room: dict, prog: dict, drawn_group) -> dict:
    """Milestone 13: the program with ``drawn_group`` (a ``groups.drawn_groups`` entry or its anchor id) marked for
    the re-solve (``resolve``), whether or not the program found a reason itself."""
    if drawn_group is None:
        return prog
    groups = GR.drawn_groups(building, room["id"])
    if isinstance(drawn_group, str):
        g = next((x for x in groups if x["anchor_id"] == drawn_group), None)
        if g is None:
            raise KeyError(f"no drawn group with anchor {drawn_group!r} in {room['id']}")
    else:
        g = dict(drawn_group)
        g.setdefault("members", [])
        g.setdefault("template", GR.group_of_type(next((f["type"] for f in building.get("furniture") or []
                                                        if f["id"] == g["anchor_id"]), ""), room.get("room_type")))
        g.setdefault("centre", next((GR.drawn_centre(f) for f in building.get("furniture") or []
                                     if f["id"] == g["anchor_id"]), [0.0, 0.0]))
    by_id = {f["id"]: f for f in building.get("furniture") or []}
    anchor = by_id.get(g["anchor_id"])
    if anchor is None or not g.get("template"):
        raise KeyError(f"drawn group {g.get('anchor_id')!r}: no drawn anchor or template")
    rows = [dict(r) for r in prog["groups"]]
    entry = next((r for r in rows if r.get("drawn") and r.get("anchor_id") == anchor["id"]), None)
    reason = (entry or {}).get("resolve", {}).get("reason") if entry else None
    reason = reason or f"the drawn {anchor['type']} {anchor['id']} group is re-solved on request (drawn_group)"
    if entry is None:
        template = GR.load_groups()[g["template"]]
        same = next((r for r in rows if r["group"] == g["template"] and not r["drawn"]), None)
        options = PR._option_of_anchor(g["template"], anchor["type"], PR.drawn_options(
            g["template"], list((same or {}).get("options") or template["options"])))
        entry = PR._entry(room["id"], g["template"], True, options, zone_id=(same or {}).get("zone_id"),
                          area=(same or {}).get("area", PR._area(room)), anchor_id=anchor["id"], drawn=True,
                          members=list(g.get("members") or []))
        if same is not None:
            rows.remove(same)
        if any(r["group_id"] == entry["group_id"] for r in rows):
            entry["group_id"] = f"{entry['group_id']}.{anchor['id']}"
        rows.append(entry)
    entry["resolve"] = {"reason": reason, "anchor_id": anchor["id"], "members": list(g.get("members") or []),
                        "centre": list(g["centre"]), "template": g["template"]}
    entry["options"] = PR.core_only(g["template"], entry["options"])
    entry["members"] = sorted(set(entry.get("members") or []) | set(g.get("members") or []))
    entry["missing"] = GR._expected_missing(g["template"], anchor, [by_id[m] for m in entry["members"] if m in by_id],
                                            room, building)
    entry["note"] = f"re-solved as one unit around the drawn anchor: {reason}"
    rows.sort(key=lambda r: (-r["priority"], r["group_id"]))
    return dict(prog, groups=rows)


def solve_room(building: dict, room_id: str, program: Optional[dict] = None, *, k: int = 3,
               fixed_ids: Optional[list[str]] = None, drawn_group=None) -> list[dict]:
    room = next((r for r in building.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id!r}")
    if len(room.get("polygon") or []) < 3:
        return []
    fixed = set(fixed_ids or ())
    prog = program if program is not None else PR.room_program(building, room_id)
    if program is None and fixed:
        # Groups whose added pieces are kept (``fixed_ids``, tagged with their group) are present: not placed again.
        kept_groups = {(f.get("group") or {}).get("group") for f in building.get("furniture") or []
                       if f.get("id") in fixed and f.get("room_id") == room_id}
        prog = dict(prog, groups=[g for g in prog["groups"] if g.get("drawn") or g["group"] not in kept_groups])
    prog = _with_drawn_group(building, room, prog, drawn_group)
    if not prog.get("groups"):
        return []
    # Milestone 13: the drawn pieces of a re-solved group are placed anew, never obstacles for their own group.
    resolve_ids: set = set()
    for g in prog["groups"]:
        if g.get("resolve"):
            resolve_ids |= {g["resolve"]["anchor_id"]} | set(g["resolve"].get("members") or [])
    space = Space(building, room, _fixed_items(building, room_id, fixed, exclude=resolve_ids))
    # The base of the verification: the room without its replaceable added pieces (and without the re-solved drawn
    # pieces, which every candidate brings back at their new places).
    base = copy.deepcopy(building)
    kept = sorted(fid for fid in fixed if any(f["id"] == fid for f in base.get("furniture") or []))
    base["furniture"] = [f for f in base.get("furniture") or [] if f["id"] not in resolve_ids and not (
        f.get("room_id") == room_id and f.get("source") == "added_by_ai" and f["id"] not in fixed
        and not schemas.off_floor(f))]
    start = _next_number(building, room["level_id"])
    out = _solve_try(space, building, room, prog, k, base, kept, start)
    # Fix round after P6b (23 Oct 2026), review (module docstring): when no candidate passes the final check, the
    # front partners (the coffee table) take their next (size, gap) options in order, one search per option, until a
    # candidate passes; a solve with a passing candidate keeps it (nothing changes there)
    first = out
    while not any(_passes(c) for c in out) and space.front_chosen:
        space.front_from, space.front_chosen = min(space.front_chosen) + 1, []
        out = _solve_try(space, building, room, prog, k, base, kept, start)
        for c in out:
            c["front_from"] = space.front_from
    if not any(_passes(c) for c in out):
        out = first
    # 26 Oct 2026 (user: "a kitchen must never be empty"): a kitchen run of the program that no passing candidate
    # places (its full runs were generated but each failed the search or the final check) is searched again with the
    # compact fallback runs only; their candidates are used when one of them places the run and passes.
    missing = [g for g in prog["groups"] if run_left_out(g, out)]
    if missing:
        fb = dict(prog, groups=[dict(g, options=[o for o in fallback_options(g["group"]) if o not in g["options"]]
                                     or g["options"], chosen=None) if g in missing else g for g in prog["groups"]])
        space.front_from, space.front_chosen = 0, []
        retry = _solve_try(space, building, room, fb, k, base, kept, start)
        if any(_passes(c) and not any(run_left_out(g, [c]) for g in missing) for c in retry):
            for c in retry:
                c["compact_fallback"] = [g["group_id"] for g in missing]
            out = retry
    return out


def run_left_out(entry: dict, cands: list[dict]) -> bool:
    """26 Oct 2026: a kitchen run the room's program asks for (not drawn) that no passing candidate places."""
    if entry.get("group") != "kitchen_run" or entry.get("drawn") or not fallback_options("kitchen_run"):
        return False
    return not any(_passes(c) and entry["group_id"] in (c.get("placed") or []) for c in cands)


def _passes(cand: dict) -> bool:
    """Fix round after P6b, review: a candidate that passes the final check and places something (``edit_ops``'s
    usable candidate)."""
    return not cand["hard_failures"] and bool(cand["pieces"])


def _solve_try(space: Space, building: dict, room: dict, prog: dict, k: int, base: dict, kept: list,
               start: int) -> list[dict]:
    """One search and verification of ``solve_room`` on ``space`` (fix round after P6b, review: ``space.front_from``
    says from which option the front partners are tried; ``space.front_chosen`` gets the options they took)."""
    room_id = room["id"]
    budget = {"used": 0, "generate": GENERATE_BUDGET, "nodes": 0, "expand": NODE_BUDGET, "walks": 0}
    info = _info(space, building, room_id, prog, budget)
    levels = _levels(space, prog, info)
    if not levels:
        return []
    walk = Walk(space)
    skip_fps = resolve_skip_fps(space, levels, info)
    beam = _search(space, levels, walk, budget, skip_fps)
    weights = GR.weights()
    finals = []
    for node in beam:
        terms = _final_terms(space, node, walk)
        bonus = sum(REQUIRED_BONUS if req else OPTIONAL_BONUS for (_e, _c, req), c in zip(levels, node.cands)
                    if c is not None)
        score = round(bonus + sum(c.local for c in node.cands if c is not None)
                      + sum(weights.get(t, 0.0) * terms[t] for t in ("balance", "circulation", "seating_crossed")
                            if t in terms), 4)
        finals.append((score, node, terms))
    finals.sort(key=lambda x: (-x[0], x[1].sig))
    # A layout that leaves out a required group never stands beside one that places them all.
    req = [sum(1 for (_e, _c, r), c in zip(levels, node.cands) if r and c is not None) for _s, node, _t in finals]
    finals = [f for f, n in zip(finals, req) if n == max(req)]
    out: list[dict] = []
    failed: list[dict] = []
    picked: list = []
    verified: dict = {}
    limit = max(4 * k, 10)
    # Pass 1: the main group (the first placed level) differs; pass 2: any group differs.
    for primary in (True, False):
        for score, node, terms in finals:
            if len(out) >= k or len(verified) >= limit:
                break
            coarse = _coarse_sig(node)
            if any(_similar(coarse, s, primary) for s in picked):
                continue
            if node.sig not in verified:
                pieces, groups = _piece_dicts(room, node, start, levels, info)
                hard, violations = verify(base, room_id, pieces, _unchanged_ids(pieces, info))
                verified[node.sig] = _candidate(score, terms, pieces, groups, hard, violations, levels, node, kept,
                                                budget, _rug_dicts(room, node, groups))
                if hard:
                    failed.append(verified[node.sig])
            cand = verified[node.sig]
            if cand["hard_failures"] or any(c is cand for c in out):
                continue
            picked.append(coarse)
            out.append(cand)
    # Pass 3: a layout that fails only by some of its groups is tried without them (a fridge that finds no landing
    # beside a drawn run: the room still gets its other groups).
    for score, node, terms in finals:
        if len(out) >= k or len(verified) >= 3 * limit:
            break
        cand = verified.get(node.sig)
        if cand is None or not cand["hard_failures"]:
            continue
        drop = _failing_levels(cand, node, start)
        placed = sum(c is not None for c in node.cands)
        optional = [i for i, c in enumerate(node.cands) if c is not None and not levels[i][2]]
        if len(drop) >= placed or not (drop or optional):
            continue
        # 23 Oct 2026 (group options 10x): when a failure names a required group's piece (a bed whose foot an
        # optional armchair narrows) or only kept pieces (a drawn bed's side no walkway reaches once a desk and a
        # chest stand there), the optional groups go first: the failing optional ones, each optional one (the last
        # placed first), then all of them; the failing levels as named only after that (a required group is never
        # dropped for an optional one).
        tries = []
        required_drop = {i for i in drop if levels[i][2]}
        if required_drop or not drop:
            tries += [d for d in [drop - required_drop] + [{i} for i in reversed(optional)] + [set(optional)]
                      if d and len(d) < placed]
        if drop:
            tries.append(drop)
        for d in list(dict.fromkeys(frozenset(t) for t in tries)):
            reduced = _without(space, node, set(d), levels, skip_fps)
            if reduced.sig in verified:
                if not verified[reduced.sig]["hard_failures"]:
                    break
                continue
            rterms = _final_terms(space, reduced, walk)
            rscore = round(sum(REQUIRED_BONUS if req else OPTIONAL_BONUS
                               for (_e, _c, req), c in zip(levels, reduced.cands) if c is not None)
                           + sum(c.local for c in reduced.cands if c is not None)
                           + sum(weights.get(t, 0.0) * rterms[t] for t in ("balance", "circulation", "seating_crossed")
                                 if t in rterms), 4)
            pieces, groups = _piece_dicts(room, reduced, start, levels, info)
            hard, violations = verify(base, room_id, pieces, _unchanged_ids(pieces, info))
            verified[reduced.sig] = _candidate(rscore, rterms, pieces, groups, hard, violations, levels, reduced, kept,
                                               budget, _rug_dicts(room, reduced, groups))
            if hard:
                continue
            if not any(_similar(_coarse_sig(reduced), s) for s in picked):
                picked.append(_coarse_sig(reduced))
                out.append(verified[reduced.sig])
            break
    if len(out) < k:
        out += failed[:k - len(out)]
    for i, c in enumerate(out):
        c["rank"] = i + 1
    return out


def _failing_levels(cand: dict, node: Node, start: int) -> set:
    """The levels whose new pieces a hard failure names (pieces are numbered from ``start`` in level order; a
    re-solved drawn piece keeps its id, ``_spot_ids``)."""
    level_of = {pid: i for i, _s, pid in _spot_ids({"level_id": _level_of_ids(cand)}, node, start)}
    out = set()
    for text in cand["hard_failures"]:
        for pid, i in level_of.items():
            if re.search(rf"(?<![\w-]){re.escape(pid)}(?![\w-])", text):
                out.add(i)
    return out


def _level_of_ids(cand: dict) -> str:
    """The level id the candidate's piece ids carry (``f_<level>_<n>``)."""
    for p in cand["pieces"]:
        if p.get("level_id"):
            return p["level_id"]
    return ""


def _without(space: Space, node: Node, drop: set, levels: list, skip_fps: Optional[dict] = None) -> Node:
    """``node`` with the candidates of the ``drop`` levels left out (occupancy and reserved zones rebuilt; a dropped
    re-solved group's drawn pieces count as drawn again, ``skip_fps``)."""
    cands = tuple(None if i in drop else c for i, c in enumerate(node.cands))
    occ = space.fixed_mask.copy()
    res = np.zeros_like(space.fixed_mask)
    for z in fixed_zones(space):
        paint(res, space.zone_fp(z))
    polys, zfps = [], []
    for i, c in enumerate(cands):
        if c is None:
            for fp in (skip_fps or {}).get(i, ([], []))[0]:
                paint(occ, fp)
            polys += (skip_fps or {}).get(i, ([], []))[1]
            continue
        for fp in c.fps:
            paint(occ, fp)
        for zfp in c.zfps:
            paint(res, zfp)
    sig = tuple(c.sig if c is not None else ("skip",) for c in cands)
    return Node(cands, occ, res, 0.0, sig, polys, zfps)


def _coarse_sig(node: Node) -> tuple:
    out = []
    for c in node.cands:
        if c is None:
            out.append(None)
        else:
            a = c.anchor
            # Milestone 13: a frontless anchor (a table) turned 180° is the same layout; the re-solve tries the drawn
            # place at the drawn rotation and the free grid at 0° / 90°, which gave one table twice.
            turn = round(a.rotation) % (180 if a.type in schemas.FRONTLESS_TYPES else 360)
            out.append((c.option, turn, a.center, a.type))
    return tuple(out)


def _similar(a: tuple, b: tuple, primary: bool = False) -> bool:
    """Two layouts are alike when every group (``primary``: the first group placed in both) has the same option,
    turn and type and an anchor less than ``DIVERSE_M`` apart."""
    pairs = list(zip(a, b))
    if primary:
        pairs = [next(((x, y) for x, y in pairs if x is not None and y is not None), (None, None))]
    for x, y in pairs:
        if (x is None) != (y is None):
            return False
        if x is None:
            continue
        if x[0] != y[0] or x[1] != y[1] or x[3] != y[3] or G.distance(x[2], y[2]) >= DIVERSE_M:
            return False
    return True


def _candidate(score, terms, pieces, groups, hard, violations, levels, node, kept, budget, rugs=()) -> dict:
    not_placed = []
    for (entry, cands, required), c in zip(levels, node.cands):
        if c is None:
            why = "no place passes the checks" if cands else "no candidate position fits the room"
            not_placed.append({"group_id": entry["group_id"], "group": entry["group"], "required": required,
                               "reason": why})
    options = {}
    resolved = []
    for c in node.cands:
        if c is not None:
            options.setdefault(c.group_id, c.option)
            if c.resolve:
                resolved.append(dict(c.resolve, group_id=c.group_id,
                                     moved={s.drawn["id"]: round(float(s.moved), 3) for s in c.spots
                                            if s.drawn is not None}))
    return {"rank": 0, "score": score, "terms": terms, "pieces": pieces,
            "groups": [{k: g[k] for k in ("group_id", "group", "anchor_id", "member_ids")} for g in groups],
            "hard_failures": hard, "group_violations": violations, "options": options,
            "placed": [g["group_id"] for g in groups], "not_placed": not_placed, "kept_ids": list(kept),
            "nodes": {"generated": budget["used"], "expanded": budget["nodes"], "walkway_checks": budget["walks"]},
            # Milestone 13: the re-solved drawn pieces (ids) with their groups and moves, and the rug members.
            "resolved": sorted(p["id"] for p in pieces if p.get("source") == "from_documents"
                               and isinstance(p.get("drawn_group"), dict)),
            "drawn_groups": resolved, "rugs": list(rugs)}


def apply_candidate(building: dict, room_id: str, candidate: dict) -> dict:
    out = copy.deepcopy(building)
    room = next((r for r in out.get("rooms") or [] if r.get("id") == room_id), None)
    if room is None:
        raise KeyError(f"no room {room_id!r}")
    kept = set(candidate.get("kept_ids") or [])
    gone = {f["id"] for f in out.get("furniture") or [] if f.get("room_id") == room_id
            and f.get("source") == "added_by_ai" and f["id"] not in kept
            and not schemas.off_floor(f)}
    out["furniture"] = [f for f in out.get("furniture") or [] if f["id"] not in gone]
    if gone and out.get("decor"):
        out["decor"] = [d for d in out["decor"] if d.get("host_id") not in gone]
    number = _next_number(out, room["level_id"])
    taken = {f["id"] for f in out["furniture"]}
    drawn_ids = {f["id"] for f in out["furniture"] if f.get("source") == "from_documents"}
    ids = {}
    for p in candidate.get("pieces") or []:
        pid = p["id"]
        if p.get("source") == "from_documents" and pid in drawn_ids:
            ids[pid] = pid                   # Milestone 13: a re-solved drawn piece replaces itself in place
            continue
        if pid in taken:
            pid = f"f_{room['level_id']}_{number:03d}"
            number += 1
        ids[p["id"]] = pid
        taken.add(pid)
    index = {f["id"]: i for i, f in enumerate(out["furniture"])}
    for p in candidate.get("pieces") or []:
        q = copy.deepcopy(p)
        q["id"] = ids[p["id"]]
        g = dict(q.get("group") or {})
        if g.get("anchor_id") in ids:
            g["anchor_id"] = ids[g["anchor_id"]]
        g.setdefault("role", "partner")
        q["group"] = g
        if isinstance(q.get("drawn_group"), dict):
            dg = dict(q["drawn_group"])
            dg["anchor_id"] = ids.get(dg.get("anchor_id"), dg.get("anchor_id"))
            q["drawn_group"] = dg
        if q["id"] in index and p.get("source") == "from_documents":
            out["furniture"][index[q["id"]]] = q
        else:
            out["furniture"].append(q)
    rugs = candidate.get("rugs") or []
    if rugs or any(d.get("room_id") == room_id and (d.get("group") or {}).get("role") == "rug"
                   for d in out.get("decor") or []):
        decor = [d for d in out.get("decor") or [] if not (d.get("room_id") == room_id
                                                          and (d.get("group") or {}).get("role") == "rug")]
        numbers = [int(m.group(1)) for d in decor for m in [re.match(rf"^dec_{re.escape(room['level_id'])}_(\d+)$",
                                                                     str(d.get("id") or ""))] if m]
        n = max(numbers, default=0) + 1
        for r in rugs:
            item = copy.deepcopy(r)
            item["id"] = f"dec_{room['level_id']}_{n:03d}"
            n += 1
            item["anchor_ids"] = [ids.get(a, a) for a in item.get("anchor_ids") or []]
            decor.append(item)
        out["decor"] = decor
    return out
