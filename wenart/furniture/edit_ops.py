"""Validated furniture and room edits of the agent (docs/milestone11.md §3.2, §5, contract §17.2).

What: ``apply_edit(building, edit)`` applies one edit (move, rotate, resize, change_type, swap_model, add,
add_group, remove, relayout_room, set_room_type) to a COPY of the building and accepts it only when the code checks
pass (inside the room, no overlap, clearances, door swing, window band, walkway, drawn-piece rules of CLAUDE.md)
and the room's plausibility score does not drop.

Contract (frozen; owner: track B):

- ``EDIT_SCHEMAS``: op -> JSON schema of the edit's arguments (the agent's tool parameters). Every edit also
  carries ``reason`` (str), ``round`` (int), ``log_seq`` (int), ``model`` (str).
- ``apply_edit(building, edit, *, catalog=None) -> {"accepted": bool, "failed_checks": [str],
  "score_before": float, "score_after": float, "building": <new building> | None, "changed_ids": [str],
  "rerun_from": "refit" | "layout", "message": str}``; pure: the input is never changed.
- Labels: a changed drawn piece keeps ``drawn_type``, ``drawn_footprint``, ``drawn_front_deg``, ``drawn_height``
  and gets ``adjusted_by_ai = {reason, round, log_seq, model, changed}``; an added piece is ``added_by_ai``;
  an inferred value sets ``inferred: true``.

The edit dict: ``{"op": <EDIT_OPS name or its §3.2 tool name, e.g. move_piece>, <arguments>}`` or
``{"op", "args": {...}}``; ``reason``, ``round``, ``log_seq`` and ``model`` may stand beside ``args``.

How each edit is checked (§5, CLAUDE.md furniture rules):

- every edit: its arguments match ``EDIT_SCHEMAS[op]`` (strict); the placer checks of every floor piece of the room
  before and after (``placer.check_all``; pieces in the frame of their fronts): a check the edit makes fail (on the
  edited piece or on another one) rejects it, a failure the room already had is not counted; then the room's
  ``plausibility.score_room`` must not drop;
- drawn fixed equipment (``schemas.FIXED_TYPES``: stairs, kitchen runs and appliances, sanitary ware): only
  ``rotate``, and only for a clear error (its back is not on a wall, its front faces a wall or, 29 Oct 2026, lesson
  UL92, the door of a washer, cooker or fridge is blocked: ``fixture_use.access_problem``; and the new front fixes
  that and leaves the door free); never moved, resized, retyped or removed;
- drawn furniture: ``move`` / wall snap by at most ``SNAP_MAX_M`` (0.3 m), ``rotate``, ``resize`` to a size within the
  type's product sizes, ``change_type`` within the room type's types (an ``unknown`` piece: any type of the room,
  marked ``inferred``), ``remove`` only with a reason (the piece stays in the JSON with ``build: false``); in a kept
  room (``furnished_rooms: keep`` / ``furnished_rooms_keep`` / ``furnished_rooms_keep_size``) only the orientation
  and clear errors (an unknown piece's type, removal);
- ``added_by_ai`` pieces: free, always through the checks; a removed one leaves the JSON with the decor on it;
- ``add`` / ``add_group``: never a second anchor piece (``schemas.anchor_types``); ``swap_model``: the asset is a
  catalogue model of the piece's type (``catalog.load``), pinned as ``asset_pin`` for the fit;
- ``set_room_type``: the new type passes R1 (area and fixtures) and no piece check gets worse.

``rerun_from``: ``layout`` for ``relayout_room`` and ``set_room_type``, else ``refit``.

Milestone 12 (docs/milestone12.md §5.2, §5.3, §4.1 U1; owner: track G), tools that work on groups:

- ``place_group(room_id, group, option?)``: the solver places a missing group (``groups.yaml``) with the room's other
  pieces fixed; never a second anchor of the room; ``complete_group(group_id)``: the group's missing partners (a
  drawn anchor gets what fits); ``move_group(group_id, span_id, offset?)``: a group of added pieces solved again on a
  free wall span (``free_spans``), partners follow; ``relayout_room(room_id, candidate?, choices?)``: the room solved
  again (its added pieces replaced) with the program's ``choices`` (group id -> option), candidate k (1 = the best).
  These four are accepted when the placer checks hold and no critical or major finding is new (``GROUP_OPS``);
- ``add`` of a type a group misses (a nightstand by a bed) goes through the solver too;
- ``retype_piece(piece_id, type)``: only a type of the room / zone at the piece that fits its footprint (size table,
  not turned 90° against a drawn front); the ``change_type`` locks hold;
- ``mark_not_furniture(piece_id, kind, evidence)``: a drawn piece read from a symbol is not built (``build: false``)
  and recorded in ``symbols[]`` (``former_piece_id``, the crop as evidence); the solver and the checks ignore it; it
  leaves ``needs_review`` (pre-flight of 16 Oct 2026). Round 4 of Milestone 13: drawn fixed equipment
  (``schemas.FIXED_TYPES``) is treated like walls and is never marked (``fix_fixture`` fixes a misread size or
  place); only fixed equipment in a room that never holds it (``schemas.misplaced_fixed``, a reading error that
  ``remove_piece`` and ``retype_piece`` may already fix) may be. The CPU pre-flight's scripted round marked 5 real03
  toilets as not furniture and left 5 bathrooms without a toilet (G10 major);
- ``fix_fixture(piece_id, size?, center?)`` (U1): drawn fixed equipment more than 30 % outside its type's real range
  takes the nearest real size (or the given one); a fixed piece through a wall or in a door swing moves at most 0.5 m
  (to ``center``, or the nearest valid spot); ``locked.check`` accepts exactly that;
- ``set_front(piece_id, front_deg)``: a drawn piece without a front gets one along a side of its footprint (± 1°);
- ``dry_run(edit)``: the answer without the building; ``allowed_edits(building, piece_id)``: per tool ``{allowed, why,
  move_left_m}`` from the locks (the room brief). Every refusal names its numbers.

Milestone 13 (docs/milestone13.md §1.5, §1.8 B2 / B3, §13.2; owner: track T4):

- ``retype_piece`` BUILDS the piece: after the type change it is fitted again through ``fit.fit_piece`` (track T1)
  in the project's licence mode (``building.project.licence_mode``, else the catalogue's default) with the fallback
  ladder (library model, module builder, parametric family), so a retyped drawn piece is never an unbuilt box; it
  becomes ``verified``, ``build`` true, leaves ``needs_review`` and keeps ``drawn_type`` with ``adjusted_by_ai``
  (``retype``: the fit's method and licence mode). ``apply_edit(..., catalog=...)`` takes the catalogue for it (the
  tools and the replay pass it; without one ``catalog.load()`` is used);
- ``place_group`` reuses the drawn group: when the room has a drawn group of the template (``groups.drawn_groups``:
  a drawn anchor with its drawn partners, built or not) the solver re-solves it as one unit around the drawn anchor
  (``solve_room(..., drawn_group=...)``, track T3: every member within 0.5 m of its drawn centre, ``adjusted_by_ai``)
  instead of adding a second group (real04: six duplicate washbasins);
- ``swap_model`` refuses an S2 cut below ``S2_SWAP_MIN_M`` (0.03 m, ``scene_checks.TOLERANCES["overlap_fixture"]``)
  with the reason "within tolerance" (the edit's ``target_finding`` carries the finding's metrics; real04: 40 toilet
  swaps for 1.2-1.3 cm cuts changed nothing) and the model the piece already has (``no_change``);
- every edit may carry ``target_finding`` (``{check, target, severity, message, metrics, cause}``, set by the
  loop, never by the model): the finding the edit addresses.

Round 2 of the build (15 Oct 2026, the integration's asks): ``_solve_apply`` applies a candidate through
``layout.apply_choice`` (the one place that applies a solver candidate): the re-solved drawn pieces of
``candidate["resolved"]`` change in place (the same dict objects, every field the solver wrote: ``drawn_group``,
``group``, ``adjusted_by_ai``), the rug members of ``candidate["rugs"]`` come with the decor; ``complete_group``
passes the drawn group (``groups.drawn_groups``) to ``solve_room`` when the room's program marks it for a re-solve
(a misread, unbuilt or failing anchor: ``_resolve_group``), else the drawn anchor stays and only the partners are
placed, as in Milestone 12.

Fix round after P4a (17 Oct 2026; pod P4a, real02). What: ``mark_not_furniture`` is a reading-error tool. A built
drawn piece that code typed from the drawing (``type_method`` in ``MARK_LOCK_METHODS``: a block name, a reading
rule, a twin, another level or a group member, with vector evidence) and that has a real size (drawn within its
type's range with the size table's 15 %, or snapped by the fit into ``plausibility.size_range``) is refused
(``drawn_lock``, ``mark_lock_refusal``) unless a reading reason holds: the edit targets an ``NR`` / ``RC`` finding,
the piece waits for review (``needs_review``) or a ``type_disagreement`` conflict names it, or it is a duplicate
outline (at least ``DUPLICATE_SHARE`` of it lies in another built drawn piece of its type: real04's wardrobe
f_L0_038 inside the storage run f_L0_026). The evidence's
plan crop is the first image path anywhere in the text (before: only a text that ended with one). Why: P4a's agent
marked three drawn, typed pieces as not furniture to clear wall cuts and wrong-room findings: the vector chair
f_L1_022 (0.58 x 0.45 m, "half through the wall"), the coffee table f_L1_021 and the dolap01 wardrobe anchor
f_L-1_024 (a 0.020 m cut, within tolerance; its twin f_L-1_023 stayed built), all with crop null. CLAUDE.md: a drawn
piece is removed only when it is clearly not furniture; a cut is fixed by the snap or a move. Untyped pieces, pieces
outside their range, AI-typed pieces (a rug outline or a cushion read as a piece) and misplaced fixed equipment keep
the old rule. No twin rule: refusing the first of two mirrored misreads while its twin is built would lock both.

Fix round after P4b (17 Oct 2026; the review of the P4a fix round, pod P4b, real03). What:

- the duplicate outline of the mark lock also counts a larger built drawn piece of the same family
  (``DUPLICATE_FAMILIES``: sofa / corner sofa / armchair / chaise; the storage types; the beds) whose footprint box
  holds at least ``DUPLICATE_SHARE`` of the piece (``family_host_of``). Tucked pairs (a chair under its table) and a
  bed block's nightstand are of other families. Why: real02's 1.30 m "sofa" f_L-1_061 is drawn 84 % inside the
  corner sofa f_L-1_053 (the seat segment of its block, typed by the group-member rule); the lock refused its mark in
  every case, the agent spent about 12 rejected moves on its F9 overlap and finally moved the drawn corner sofa;
- the lock is lifted when the edit's evidence names a plan crop (``plan_crop_of``: ``recognition/crops/<key>_ctx`` or
  ``_iso.png``, a camera's ``check/<cam>_plan`` crop): the verifier's second way out of the P4a fix, which the P4a
  fix round left out. A text-only evidence or a top-down render still leaves the lock on (P4a's 0.020 m wardrobe cut
  and the chair and coffee table marked from top-down renders stay refused);
- ``crop_of`` records only a plan crop (or another image that is not one of the agent's own renders,
  ``AGENT_IMAGE``) as the crop of a not-furniture symbol; a top-down render (P4a seq 264: "top-down image
  r1_044_topdown_r_L-1_salon_2.png: ...") gives ``crop: null`` and its text stays in the evidence. CLAUDE.md asks for
  the plan crop as evidence of a removal and the AI never judges a bare top-down image;
- ``complete_group`` (and ``allowed_edits``) refuses at once (``no_completion``, ``program_refusal``) a group whose
  row in the room's program completes nothing: a group that does not belong in the room ("no completion: a
  bathroom_set group does not belong in a hall room") or a duplicate outline (``program.duplicate_anchor``). Why:
  real03's agent sent ``complete_group`` for the bathroom set of the drawn washers in 3 entrance halls; each ran the
  solver and was refused with "no place passes the checks" (and the brief still offered the tool).

Pass before P5 (17 Oct 2026; the review of the fix round after P4b). What: the plan-crop way out of the mark lock
(the bullet above) takes only a crop of the piece itself (``own_crop_named``): the reading's crop of its own question
(an evidence entry ``recognition:<key>``: ``<key>_ctx.png``, ``<key>_iso.png`` or ``<key>.png`` in a ``crops/``
folder) or a recognition crop recorded for its id in ``needs_review`` or ``conflicts``. A room's or camera's plan crop
(``check/<cam>_plan.jpg``, what the ``plan_crop`` and ``view`` tools return) and the crop of another symbol leave the
lock on, and the refusal no longer hands out a crop path pattern. The symbol of a marked piece records its own crop
when the evidence names it, else ``crop_of`` as before. Why: any crop-like path lifted the lock, and the agent cites
the room's camera crop as removal evidence for placement findings (P3 real04 seq 3282, 3689, 3692: "plan crop
check/cam_r_L1_koridor_2_1_plan.jpg: ... not a built table; it pokes through wall w_L1_006" for an F9 / S2 finding on
the coffee table f_L1_024, which a ``type_disagreement`` conflict leaves outside the lock). On P4a's real02 buildings
such a crop let the coffee table f_L1_021 through, and the crop of the unrelated symbol sym_L-1_009 the wardrobe
f_L-1_024: a drawn piece removed as not furniture for a placement finding, which the P4a fix round's lock was built
to stop. On P3's real04 buildings 72 drawn pieces are under the lock; a room crop or another symbol's crop lifts it
for none of them now, and 2 have a crop of their own (the round coffee tables f_L1_015 / f_L1_016: sym_L1_001 /
sym_L1_002). No accepted mark of the P3, P4a or P4b logs changes.

Fix round after P5 (22 Oct 2026; pod P5, real04; the P5 verifier's better fix and the user decisions of 22 Oct
2026). What:

- **The mark lock holds when the AI passes typed the piece as furniture too** (``ai_furniture_dispute``): a
  ``type_disagreement`` conflict the drawing won ("<id>: the AI passes typed it bench; ...", ``reading.log_overrides``)
  whose AI type is a furniture type means the doubt is which piece it is, so ``retype_piece`` fixes it: neither the
  conflict nor an edit that targets its ``RC`` finding lifts the lock then; the piece's own recognition crop still
  does, and an ``NR`` target keeps its way out. A conflict that names no AI type keeps the old rule. No twin rule (a
  coat closet is furniture: marking the twin would remove it too). Why: P5 seq 5021 marked the drawn coffee table
  f_L1_021 (really a coat closet: ``symbols.hanging_rail``) as "a stair" with a camera plan crop for an F1 finding,
  because its conflict c_047 lifted the lock; the twin f_L1_024 stayed built.
- **An untyped piece is marked only with its plan crop**: when the evidence names no image and no recognition crop is
  recorded for the piece (``recorded_crop``: ``needs_review`` / ``conflicts``), ``mark_not_furniture`` on an untyped
  piece is refused (``no_crop``); a recorded crop is the symbol's crop when the evidence names none. Why: P5 seq 5388
  marked the 5.14 x 2.37 m cluster f_L-1b_001 with "plan crop of r_L-1b_salon_2" and no image (symbol crop null);
  CLAUDE.md removes a drawn piece only with its plan crop as evidence.
- **fix_fixture shrinks a bath or shower a few cm longer than its bay** (user decision (3) of 22 Oct 2026): without
  ``center`` (and with no ``size`` or the same one) it takes ``reading.bay_fit``'s nearest real product that fits the
  clear bay (``adjusted_by_ai.fix_fixture.bay``); the code's search for a spot could never fit such a tub (P4b real03:
  21 centres in 5 cm steps). The refusal of a centre still in a wall or a door swing now says that without ``center``
  the code searches every spot within 0.50 m and that no centre will do when that search found none.

Fix round after P6a (22-23 Oct 2026; pod P6a, real04; the asks of the agent and decor tracks). What:

- **swap_model refuses a generated model the refit refuses** (``generated_pin_refusal``): a pin to a ``source:
  generated`` model is fitted at once (``fit.fit_piece`` with the pin, the building's licence mode and style family,
  the piece's ``fit.piece_ceiling``); a ``pin_refused`` of that pin (a real product of the type fits, or the caps, the
  height or the sloped ceiling) is the refusal "pin_refused: <piece>: <reason>: the real model stays". Other models
  keep the old checks (the stage-12 refit and the loop's acceptance, ``agent.loop.refused_pin``, judge them). Why:
  P6a seq 6069 / 6075 / 6076 pinned gen_fridge / gen_washbasin / gen_toilet models; the refit refused each pin and
  built the same real models, while the edits were accepted and their vision findings counted as removed;
- **mark_not_furniture marks an untyped piece only with its own crop**: the crop of its own question
  (``own_crop_named``) or the recognition crop its review entry records (``recorded_crop``); never ``crop_of``'s first
  image (a whole sheet ``final/debug/...``, a room's or camera's plan crop, another symbol's crop): else
  ``no_crop``. Typed pieces keep the old crop rule (and the mark lock). Why: P6a seq 5968 marked the 5.14 x 2.37 m
  cluster f_L-1b_002 (no question, no crop) with the whole sheet ``final/debug/deneme1_dwg_s1.jpg``; decision 8 keeps
  such a cluster listed for review;
- **change_type / retype_piece read the room's types with their aliases** (``room_allowed``: the union of the rows of
  ``plausibility.room_types``, the alias kind of an ``other`` room included, as F1 and G14 read the room); the
  fixed-type, ``unknown`` and old-type exclusions stay. Why: P6a seq 6008 / 6014: retype_piece offered console_table /
  sideboard for f_L1_035 in r_L1_oyun_aktivite_ve_dinlenme_odasi (room type ``other``, alias living;
  ``group_checks.allowed_types_at``) and change_type refused it "not a piece a other room may hold";
- **the retype refit keeps headroom** (``_build_retyped``): ``fit.fit_piece`` gets the piece's ``fit.piece_ceiling``
  under a sloped ceiling, as ``fit.fit_building`` (the decor track's ask, verify:agent:4 part 2).

Fix round after P6b (23 Oct 2026; pod P6b, real03; verify:library:0 and verify:agent:0's better fix). What:

- **a cut through the room outline that is new or grows is refused** (``outline_cuts``, ``outline_growth``): after the
  placer checks, every op but ``mark_not_furniture`` compares the F9 cuts through the REAL room outline that the
  room's plausibility score measures (``plausibility._f9``: ``outside_m2``, ``depth_m``) before and after the edit; a
  piece past ``PL.OUTSIDE_MIN_M2`` (0.05 m²) that was not before, or whose cut grew by more than that area or by more
  than ``OUTLINE_DEPTH_GROWTH_M`` (0.05 m) in depth, fails "inside_room (outline: ...)", whatever the score nets. Why:
  P6b seq 2588 moved the drawn wardrobe f_L0_098 0.28 m through the front outer wall (0.168 m² outside; visible on the
  facade of ext_6 / ext_7, which it made non-commercial): it failed inside_room against the 2 cm shrunk room by 4.5 mm
  before, so the placer's pass/fail flags saw no new failure, and the score rose 70 -> 80 (G13 and the bed's G5 gone,
  one F9 major new). Measured against the real outline, not the shrunk room: the corner washing machines f_L0_074 /
  076 / 077 turned 90 degrees for "front faces a wall" (P6b seq 1969 / 1971 / 2637, P4b seq 434 / 437) deepen a cut
  they already had by 0.025 m and stay accepted; on the accepted footprint edits of P4a, P4b, P5 and P6a only P4a's
  coffee table f_L1_024 (0.07 m², 0.059 m through w_L1_006 after its move and resize; the vision critic said "rendered
  intersecting the wall") would be refused.
- **complete_group takes a drawn anchor typed by code** (``unsure_group_anchor``): the "retype_piece first" refusal
  holds only for an ``unverified`` anchor the reading could not agree on (``program.unsure_anchor``), not for a
  vector-drawn one the reading typed by code (``infer.CODE_TYPE_METHODS``), which the program, the solver and the decor
  (``decor.trusted_host``) already complete like a verified one. Why: the review of the fix round after P6a gave the
  F3 of the drawn basement sofas f_L-1b_041 / 042 (P6a real04, P4a real02; group_member / twin) the cause
  missing_member, while complete_group refused their groups as unverified and the acceptance refuses a same-type
  confirm (it changes nothing in the render): a deadlock (place_group has no such lock);
- **a sofa's front clearance counts its coffee table as the score does** (``room_checks``, ``seat_front_free``): the
  placer's ``clearance_ok`` (0.6 m in front of a sofa, no exemption for a coffee table) is excused when only
  ``plausibility.EXTRA_EXEMPT`` partners (coffee table, ottoman) and the placer's own exemptions stand in the zone,
  the rule of the score's F6. Why: the solver places the coffee table at the designer gap (groups.yaml ``coffee_gap``
  0.30-0.45 m), and the validator refused every such group edit "<sofa>: clearance_ok" (P6a seq 6308 / 6309 / 6312 /
  6600 / 6645 / 6649; a completion of f_L-1b_041 / 042); an armchair or chair in the zone still fails (seq 5081);
- **a group edit's new findings are counted by finding, not by message** (``finding_identity``): an F4 "does not face
  its group (...)" whose list grew by the new piece is the finding the piece had (P6a's chair f_L-1b_053 with the new
  coffee table f_L-1b_087); every other message is compared whole, as before;
- **an F4 of another group's anchor is reported, not held against a group edit** (``other_group_front``): a new F4
  "does not face its group" on a piece that anchors its own group, naming only pieces this edit added to a group with
  another anchor, goes into the accepted message ("noted: ... kept for the next round"). Why: the coffee table
  completing f_L-1b_041 stands 1.7 m from the second drawn sofa f_L-1b_045 (its own seating group), within the
  score's 4.5 m sofa reach; CLAUDE.md asks fronts to face their group.

Bathroom sense of 26 Oct 2026 (``groups`` module docstring): ``place_group`` of a set or run the room already holds
(a bathroom set, a WC set, a kitchen run, an entrance set) completes that one (``complete_group``: only its missing
members, the pieces the room has are adopted) or is refused "nothing missing, never a second set"; the floor filters
(``_floor_items``, ``_ai_floor_ids``) count a fixture hung at its working top (``schemas.off_floor``), so a relayout
replaces an added basin the fit hung instead of keeping it beside a new one; the refit of a retyped piece knows a
child's room (``fit.use_context``).
"""
from __future__ import annotations

import copy
import dataclasses
import math
import re
from typing import Any, Optional

import jsonschema

from shapely.geometry import Point

from wenart import geometry as G
from wenart.furniture import fixture_use as FU
from wenart.furniture import group_checks as GC
from wenart.furniture import groups as GR
from wenart.furniture import locked as LK
from wenart.furniture import placer, plausibility as PL, schemas

EDIT_OPS = ("move", "rotate", "resize", "change_type", "swap_model", "add", "add_group", "remove",
            "relayout_room", "set_room_type",
            # Milestone 12 (docs/milestone12.md §5.3)
            "place_group", "complete_group", "move_group", "retype_piece", "mark_not_furniture", "fix_fixture",
            "set_front")
# The tool names of docs/milestone11.md §3.2 and milestone12.md §5.3 -> the ops.
TOOL_OPS: dict[str, str] = {"move_piece": "move", "rotate_piece": "rotate", "resize_piece": "resize",
                            "change_type": "change_type", "swap_model": "swap_model", "add_piece": "add",
                            "add_group": "add_group", "remove_piece": "remove", "relayout_room": "relayout_room",
                            "set_room_type": "set_room_type", "place_group": "place_group",
                            "complete_group": "complete_group", "move_group": "move_group",
                            "retype_piece": "retype_piece", "mark_not_furniture": "mark_not_furniture",
                            "fix_fixture": "fix_fixture", "set_front": "set_front"}
# Ops that place whole groups with the solver: accepted when no critical or major finding is new (a minor one, an
# armchair not quite facing, may come with a group) and the placer checks hold.
GROUP_OPS = ("place_group", "complete_group", "move_group", "relayout_room")
# Reading corrections: a misread symbol left out may leave the room without a piece it needs; the new findings are
# reported in the message, not held against the edit (the placer checks still hold). Round 4: drawn fixed equipment
# is never marked (``_mark_not_furniture``), and the agent's acceptance (``wenart.agent.causes.accept_edit``) refuses
# an edit whose dry re-check shows a new room-set finding (G9 / G10) for a fixture it removed.
CORRECTION_OPS = ("mark_not_furniture",)
SNAP_MAX_M = 0.3                 # §5: a drawn piece may move (snap to a wall) by at most this
MOVE_CLAMP_FACTOR = 2.0          # 28 Oct 2026: a drawn move up to this times the limit is clamped to it, not refused
LAYOUT_OPS = ("relayout_room", "set_room_type")
ROOM_TYPES = ("living", "dining", "bedroom", "kitchen", "bathroom", "wc", "hall", "balcony", "storage", "prayer",
              "stair", "shaft", "other", "unknown")
EVIDENCE_FILE = "building.json"

_META: dict[str, Any] = {
    "reason": {"type": "string", "minLength": 1, "maxLength": 500, "description": "why (logged, shown in the report)"},
    "round": {"type": "integer", "minimum": 0},
    "log_seq": {"type": "integer", "minimum": 0},
    "model": {"type": "string", "maxLength": 200},
    # Milestone 13: the finding the edit addresses (set by the loop: check, target, severity, message, metrics, cause)
    "target_finding": {"type": "object"},
}
META_KEYS = ("reason", "round", "log_seq", "model", "target_finding")
S2_SWAP_MIN_M = 0.03             # Milestone 13: swap_model never for an S2 cut below this (within tolerance)
_POINT = {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}
_ID = {"type": "string", "minLength": 1, "maxLength": 80}
_FTYPES = sorted(t for t in schemas.SIZE_OPTIONS)


def _schema(props: dict, required: list[str], **extra) -> dict:
    out = {"type": "object", "additionalProperties": False, "properties": dict(props, **_META),
           "required": list(required) + ["reason"]}
    out.update(extra)
    return out


# op -> JSON schema of the arguments (strict: additionalProperties false, required fields).
EDIT_SCHEMAS: dict[str, dict] = {
    "move": _schema({"piece_id": _ID, "center": dict(_POINT, description="new footprint centre [x, y], metres"),
                     "snap_wall_id": dict(_ID, description="snap the back edge onto this wall of the room"),
                     "offset": {"type": "number", "description": "with snap_wall_id: shift along the wall (metres, "
                                                                 "positive towards the wall's end point)"}},
                    ["piece_id"], oneOf=[{"required": ["center"], "not": {"required": ["snap_wall_id"]}},
                                         {"required": ["snap_wall_id"], "not": {"required": ["center"]}}],
                    dependentRequired={"offset": ["snap_wall_id"]}),
    "rotate": _schema({"piece_id": _ID, "front_deg": {"type": "number", "minimum": 0, "maximum": 360,
                                                      "description": "direction the front faces, degrees "
                                                                     "counter-clockwise from +X"}},
                      ["piece_id", "front_deg"]),
    "resize": _schema({"piece_id": _ID, "size": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                                                 "minItems": 2, "maxItems": 2,
                                                 "description": "[width along the front, depth], metres"}},
                      ["piece_id", "size"]),
    "change_type": _schema({"piece_id": _ID, "type": {"enum": _FTYPES}}, ["piece_id", "type"]),
    "swap_model": _schema({"piece_id": _ID, "asset_id": _ID}, ["piece_id", "asset_id"]),
    "add": _schema({"room_id": _ID, "type": {"enum": sorted(schemas.LAYOUT_TYPES)}, "center": _POINT,
                    "front_deg": {"type": "number", "minimum": 0, "maximum": 360}}, ["room_id", "type"],
                   dependentRequired={"front_deg": ["center"]}),
    "add_group": _schema({"room_id": _ID, "group": {"enum": list(GR.GROUPS)},
                          "anchor": {"type": "object", "additionalProperties": False,
                                     "properties": {"piece_id": _ID, "center": _POINT,
                                                    "front_deg": {"type": "number", "minimum": 0, "maximum": 360}}}},
                         ["room_id", "group"]),
    "remove": _schema({"piece_id": _ID}, ["piece_id"]),
    "relayout_room": _schema({"room_id": _ID,
                              "candidate": {"type": "integer", "minimum": 1, "maximum": 5,
                                            "description": "the solver's candidate k (1 = its best)"},
                              "choices": {"type": "object", "additionalProperties": {"type": "string"},
                                          "description": "group id -> option of the room's program"}}, ["room_id"]),
    "set_room_type": _schema({"room_id": _ID, "room_type": {"enum": list(ROOM_TYPES)}}, ["room_id", "room_type"]),
    # 23 Oct 2026 (group options 10x): the option is a name checked by code (``_place_group``: not an option of the
    # group -> rejected with the group's options), not an enum of all 263 names in every agent prompt
    "place_group": _schema({"room_id": _ID, "group": {"enum": sorted(GR.load_groups())},
                            "option": {"type": "string", "pattern": "^[A-Za-z0-9_]{1,48}$",
                                       "description": "an option of the group (the room's program lists them)"}},
                           ["room_id", "group"]),
    "complete_group": _schema({"group_id": _ID}, ["group_id"]),
    "move_group": _schema({"group_id": _ID, "span_id": dict(_ID, description="a free wall span (free_spans)"),
                           "offset": {"type": "number", "minimum": 0,
                                      "description": "the anchor's centre, metres from the span's start"}},
                          ["group_id", "span_id"]),
    "retype_piece": _schema({"piece_id": _ID, "type": {"enum": _FTYPES}}, ["piece_id", "type"]),
    "mark_not_furniture": _schema({"piece_id": _ID, "kind": {"enum": ["level_mark", "room_number", "north_arrow",
                                                                     "axis_bubble", "section_mark", "door_arc",
                                                                     "dimension_outline", "text_frame", "other"]},
                                   "evidence": {"type": "string", "minLength": 1, "maxLength": 500,
                                                "description": "the plan crop path or what shows it"}},
                                  ["piece_id", "kind", "evidence"]),
    "fix_fixture": _schema({"piece_id": _ID, "size": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                                                      "minItems": 2, "maxItems": 2,
                                                      "description": "a real product size [width, depth]"},
                            "center": dict(_POINT, description="new centre, at most 0.5 m from the drawn one")},
                           ["piece_id"]),
    "set_front": _schema({"piece_id": _ID, "front_deg": {"type": "number", "minimum": 0, "maximum": 360}},
                         ["piece_id", "front_deg"]),
}


class EditRejected(Exception):
    """An edit that breaks a rule before any check runs (unknown piece, a locked drawn piece, ...)."""

    def __init__(self, check: str, message: str):
        super().__init__(message)
        self.check = check
        self.message = message


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def normalise_edit(edit: dict) -> tuple[Optional[str], dict]:
    """``(op, arguments)`` of an edit dict (op or tool name; flat or nested ``args``; meta keys beside ``args``)."""
    name = edit.get("op") or edit.get("tool")
    op = TOOL_OPS.get(name, name)
    if isinstance(edit.get("args"), dict):
        args = {k: v for k, v in edit.items() if k in META_KEYS}
        args.update(edit["args"])
    else:
        args = {k: v for k, v in edit.items() if k not in ("op", "tool")}
    return op, args


def schema_errors(op: str, args: dict) -> list[str]:
    validator = jsonschema.Draft202012Validator(EDIT_SCHEMAS[op])
    errors = sorted(validator.iter_errors(args), key=lambda e: list(e.absolute_path))
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<args>'}: {e.message}" for e in errors]


def _piece(b: dict, pid: str) -> dict:
    found = next((f for f in b.get("furniture") or [] if f.get("id") == pid), None)
    if found is None:
        raise EditRejected("piece_exists", f"no piece {pid!r}")
    return found


def _room(b: dict, rid: Optional[str]) -> dict:
    found = next((r for r in b.get("rooms") or [] if r.get("id") == rid), None)
    if found is None:
        raise EditRejected("room_exists", f"no room {rid!r}")
    return found


def _drawn(item: dict) -> bool:
    return item.get("source") == "from_documents"


def _fixed(item: dict) -> bool:
    return _drawn(item) and item.get("type") in schemas.FIXED_TYPES


def kept_room(building: dict, room: dict) -> bool:
    """The room keeps its drawn pieces (the brief's ``furnished_rooms: keep``, ``furnished_rooms_keep`` (ids or
    labels) or ``furnished_rooms_keep_size``): only orientation and clear errors may change there."""
    brief = (building.get("project") or {}).get("brief") or {}
    if brief.get("furnished_rooms") == "keep" or brief.get("furnished_rooms_keep_size"):
        return True
    keep = [str(v).strip().lower() for v in brief.get("furnished_rooms_keep") or []]
    return room["id"].lower() in keep or str(room.get("label", "")).strip().lower() in keep


def _anchor_roles(room: dict) -> set:
    return set(schemas.ANCHOR_TYPES.get(room.get("room_type") or "", ())) | set(
        schemas.anchor_types(room.get("room_type"), room.get("room_subtype")))


def _next_id(b: dict, level_id: str) -> str:
    pattern = re.compile(rf"^f_{re.escape(level_id)}_(\d+)$")
    numbers = [int(m.group(1)) for f in b.get("furniture") or [] for m in [pattern.match(f["id"])] if m]
    return f"f_{level_id}_{max(numbers, default=0) + 1:03d}"


def _set_footprint(item: dict, center, rotation: float, size, front: Optional[float]) -> None:
    item["footprint"] = {"center": [round(float(center[0]), 4), round(float(center[1]), 4)],
                         "size": [round(float(size[0]), 4), round(float(size[1]), 4)],
                         "rotation_deg": round(G.normalise_angle(rotation), 3)}
    item["front_deg"] = round(G.normalise_angle(front), 3) if front is not None else None


def _label(item: dict, before: dict, args: dict, fields: list[str]) -> None:
    """``adjusted_by_ai`` (first old values kept over several edits; the earlier records under ``previous``) and, on a
    drawn piece, the drawn values."""
    if _drawn(item):
        item.setdefault("drawn_type", before.get("type"))
        item.setdefault("drawn_footprint", copy.deepcopy(before.get("footprint")))
        item.setdefault("drawn_front_deg", before.get("front_deg"))
        item.setdefault("drawn_height", before.get("height"))
    old = item.get("adjusted_by_ai") or {}
    changed = dict(old.get("changed") or {})
    for f in fields:
        changed.setdefault(f, copy.deepcopy(before.get(f)))
    label = {"reason": str(args.get("reason") or "")}
    for k in ("round", "log_seq", "model"):
        if args.get(k) is not None:
            label[k] = args[k]
    label["changed"] = changed
    # A later edit keeps the allowances of the earlier ones that ``locked.check`` reads: the snap's wider move (M11),
    # a fix_fixture's move and real size (M12 U1) and a drawn-group re-solve's move (M13). Without them a second edit
    # of the same piece (fix_fixture, then mark_not_furniture or set_front) made the refit's locked check refuse the
    # first one: "fixed equipment moved or resized" (CPU pre-flight of 16 Oct 2026, real03: five toilets).
    for key in ("snapped_wall", "fix_fixture", "drawn_group"):
        if old.get(key):
            label[key] = old[key]
    # Integration of the fix round after P5 (P_report's ask): the earlier records stay under ``previous`` (oldest
    # first), so an agent edit no longer replaces the code's own record (P5: the nightstand retypes of
    # f_L0_032/034/036/038, rule nightstand_symbol with their plan crops, were overwritten by the agent's moves)
    previous = [copy.deepcopy(r) for r in old.get("previous") or [] if isinstance(r, dict)]
    if old:
        previous.append({k: copy.deepcopy(v) for k, v in old.items() if k != "previous"})
    if previous:
        label["previous"] = previous
    item["adjusted_by_ai"] = label


def _ai_evidence(args: dict, text: str) -> list[dict]:
    ev = {"file": EVIDENCE_FILE, "method": "ai", "confidence": 0.8, "text": text}
    if args.get("model"):
        ev["model"] = args["model"]
    return [ev]


def _front_problem(r: "PL._Room", pid: str) -> Optional[str]:
    """The clear orientation error of a piece (F3 back not on a wall, or F4 front into a wall), else None. 29 Oct 2026
    (lesson UL92): or the door or drawers of a door-fronted piece (``fixture_use.ACCESS_M``: a washer, a dishwasher, a
    cooker, a fridge, a nightstand) blocked by a neighbour (``fixture_use.access_problem``): real06's washer f_L1_019 was
    turned from the wall onto the toilet 0.11 m away, and this rule called the new front free."""
    item = r.item(pid)
    rule = schemas.orientation_rule(item["type"])
    p = r.pieces[pid]
    if rule["back"] in ("wall", "wall_or_group") and not PL.back_on_wall(p, r)[0]:
        return "its back is not on a wall"
    if item["type"] not in schemas.FRONTLESS_TYPES and PL.front_wall_distance(p, r, r.front_dir(pid)) is not None:
        return "its front faces a wall"
    if item["type"] in FU.ACCESS_M and not FU.in_run(item, r.built):
        obstacles = [(oid, r.item(oid)["type"], [tuple(c) for c in list(op.exterior.coords)[:-1]])
                     for oid, op in r.polys.items() if oid != pid and getattr(op, "exterior", None) is not None]
        prob = FU.access_problem(item["type"], p.center, p.rotation_deg, p.size, list(r.ring.coords), obstacles)
        if prob is not None:
            return (f"its front is blocked ({', '.join(prob['blockers'][:3] + (['the wall'] if prob['wall'] else []))}"
                    f"; {prob['free_m']:.2f} m free, its door needs {prob['open_m']:.2f} m to open and "
                    f"{prob['use_m']:.2f} m to use)")
    return None


# --------------------------------------------------------------------------
# Placer checks of a room before / after
# --------------------------------------------------------------------------

def _floor_items(b: dict, room_id: str) -> list[dict]:
    return [f for f in b.get("furniture") or [] if f.get("room_id") == room_id and f.get("build") is not False
            and f.get("type") != "unknown" and not schemas.off_floor(f)]


def room_checks(b: dict, room_id: str) -> dict[str, set]:
    """piece id -> the placer checks it fails among the room's floor pieces (fronts as drawn). Milestone 12: the
    walkways are the group check G11's (in the score), not the placer's 0.9 m erosion. Fix round after P6b (module
    docstring): a seat's ``clearance_ok`` counts what may stand in front of it as the score's F6 does
    (``seat_front_free``: a coffee table or ottoman before a sofa)."""
    room = _room(b, room_id)
    items = _floor_items(b, room_id)
    if not items:
        return {}
    ctx = placer.room_context(b, room)
    pieces = [placer.drawn_piece(f, i) for i, f in enumerate(items)]
    out: dict[str, set] = {}
    for f, p, c in zip(items, pieces, placer.check_all(pieces, ctx, walkways=False)):
        failed = set(placer.failed_checks(c))
        if "clearance_ok" in failed and seat_front_free(p, [o for o in pieces if o is not p], ctx):
            failed.discard("clearance_ok")
        out[f["id"]] = failed
    return out


def seat_front_free(p: placer.Piece, others: list[placer.Piece], ctx: placer.RoomContext) -> bool:
    """Fix round after P6b (module docstring): True for a seat with extra front partners (``plausibility.EXTRA_EXEMPT``:
    a sofa or corner sofa) whose front clearance (``placer.Piece.front_zone``, 0.6 m) lies in the room and holds no
    piece but those partners and the placer's own exemptions (``schemas.CLEARANCE_EXEMPT``): the placer's
    ``clearance_ok`` without the score's F6 exemption refused every coffee table the solver places at the designer gap
    (groups.yaml ``coffee_gap`` 0.30-0.45 m). False for any other type (the placer's verdict stands)."""
    extra = PL.EXTRA_EXEMPT.get(p.type)
    if not extra:
        return False
    exempt = set(schemas.CLEARANCE_EXEMPT.get(p.type, ())) | set(extra)
    zone = p.front_zone()
    if zone.difference(ctx.polygon.buffer(0.01, join_style="mitre")).area >= placer.AREA_EPS:
        return False
    return all(zone.intersection(o.polygon()).area < placer.AREA_EPS for o in others if o.type not in exempt)


def _new_failures(before: dict[str, set], after: dict[str, set]) -> list[str]:
    out = []
    for pid, failed in sorted(after.items()):
        for name in sorted(failed - before.get(pid, set())):
            out.append(f"{pid}: {name}")
    return out


# Fix round after P6b (module docstring): how much deeper an outline cut a piece already had may get (a corner washing
# machine turned 90 degrees to fix "front faces a wall" deepens its cut by 0.025 m).
OUTLINE_DEPTH_GROWTH_M = 0.05


def outline_cuts(score: dict) -> dict[str, tuple[float, float, str]]:
    """Fix round after P6b: ``{piece id: (outside_m2, depth_m, message)}`` of the F9 cuts through the room outline in a
    ``plausibility.score_room`` result (``_f9``: more than ``PL.OUTSIDE_MIN_M2`` outside the real room outline, not
    the placer's 2 cm shrunk room)."""
    out: dict[str, tuple[float, float, str]] = {}
    for v in (score or {}).get("violations") or []:
        m = v.get("metrics") if isinstance(v.get("metrics"), dict) else {}
        if v.get("check") != "F9" or m.get("outside_m2") is None:
            continue
        try:
            out[str(v.get("target"))] = (float(m["outside_m2"]), float(m.get("depth_m") or 0.0),
                                         str(v.get("message") or ""))
        except (TypeError, ValueError):
            continue
    return out


def outline_growth(before: dict, after: dict) -> list[str]:
    """Fix round after P6b (module docstring): the failed checks ``"<id>: inside_room (outline: ...)"`` of the pieces
    whose cut through the room outline (``outline_cuts``) is new after the edit (none past ``PL.OUTSIDE_MIN_M2``
    before), or grew by more than ``PL.OUTSIDE_MIN_M2`` in area or ``OUTLINE_DEPTH_GROWTH_M`` in depth; [] otherwise."""
    bad = []
    for pid, (area, depth, message) in sorted(after.items()):
        was = before.get(pid)
        a0, d0 = (was[0], was[1]) if was is not None else (0.0, 0.0)
        if was is None or area - a0 > PL.OUTSIDE_MIN_M2 + 1e-9 or depth - d0 > OUTLINE_DEPTH_GROWTH_M + 1e-9:
            bad.append(f"{pid}: inside_room (outline: {message}; {a0:.2f} m² up to {d0:.3f} m deep before)")
    return bad


# --------------------------------------------------------------------------
# The edits (each changes ``b`` in place: the caller's copy)
# --------------------------------------------------------------------------

def _wall_segment(b: dict, ctx: placer.RoomContext, wall_id: str, near) -> tuple[int, float]:
    """(index of the room outline segment on wall ``wall_id`` nearest ``near``, +1/-1: the segment runs with or
    against the wall's start -> end)."""
    wall = next((w for w in b.get("walls") or [] if w.get("id") == wall_id), None)
    if wall is None:
        raise EditRejected("wall_exists", f"no wall {wall_id!r}")
    t = float(wall.get("thickness") or placer.DEFAULT_WALL_THICKNESS_M)
    wdir = math.degrees(math.atan2(wall["end"][1] - wall["start"][1], wall["end"][0] - wall["start"][0]))
    best = None
    for i, (a, c) in enumerate(ctx.segments):
        mid = ((a[0] + c[0]) / 2.0, (a[1] + c[1]) / 2.0)
        diff = G.angle_difference_deg(G.segment_angle_deg(a, c) % 180.0, wdir % 180.0)
        if min(diff, 180.0 - diff) > 5.0:
            continue
        if G.point_segment_distance(mid, wall["start"], wall["end"]) > t / 2.0 + 0.05:
            continue
        key = G.point_segment_distance(near, a, c)
        if best is None or key < best[0]:
            same = G.angle_difference_deg(G.segment_angle_deg(a, c), wdir) < 90.0
            best = (key, i, 1.0 if same else -1.0)
    if best is None:
        raise EditRejected("wall_in_room", f"wall {wall_id} does not bound the piece's room")
    return best[1], best[2]


def _move(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    if _fixed(item):
        raise EditRejected("drawn_lock", f"{item['id']}: drawn fixed equipment ({item['type']}) is never moved")
    if _drawn(item) and kept_room(b, room):
        raise EditRejected("drawn_lock", f"{item['id']}: the room keeps its drawn pieces: only orientation and clear "
                                         f"errors may change")
    before = copy.deepcopy(item)
    p = placer.drawn_piece(item)
    if args.get("center") is not None:
        center, rotation = (float(args["center"][0]), float(args["center"][1])), p.rotation_deg
    else:
        ctx = placer.room_context(b, room)
        seg, sign = _wall_segment(b, ctx, args["snap_wall_id"], p.center)
        others = [placer.drawn_piece(f) for f in _floor_items(b, room["id"]) if f["id"] != item["id"]]
        found = placer.snap_to_wall(p, ctx, seg_index=seg, offset=sign * float(args.get("offset") or 0.0),
                                    max_shift=schemas.WALL_SNAP_MAX_M if _drawn(item) else None, others=others)
        if found is None:
            raise EditRejected("snap", f"{item['id']}: no free place on wall {args['snap_wall_id']} (doors, windows"
                                       + (f", at most {schemas.WALL_SNAP_MAX_M} m from the drawn place"
                                          if _drawn(item) else "") + ")")
        center, rotation = found[0], found[1]
    limit = schemas.WALL_SNAP_MAX_M if args.get("snap_wall_id") else SNAP_MAX_M
    clamped = None
    if _drawn(item):
        drawn_center = (item.get("drawn_footprint") or item["footprint"])["center"]
        dist = G.distance(center, drawn_center)
        if limit + 1e-6 < dist <= MOVE_CLAMP_FACTOR * limit and args.get("center") is not None:
            # 28 Oct 2026 (real04 run 005318: 9 moves refused, several at "0.30 m", the distance counts from the drawn
            # place, which the agent does not see): a move a little past the limit (up to MOVE_CLAMP_FACTOR times
            # it) goes as far as the limit allows in the asked direction (recorded); the checks then decide whether it
            # fixed its finding. A move farther than that is no small correction: refused as before
            k = (limit - 1e-6) / dist
            clamped = round(dist, 3)
            center = (float(drawn_center[0]) + (center[0] - float(drawn_center[0])) * k,
                      float(drawn_center[1]) + (center[1] - float(drawn_center[1])) * k)
        elif dist > limit + 1e-6:
            raise EditRejected("drawn_lock", f"{item['id']}: a drawn piece moves at most {SNAP_MAX_M} m, or "
                                             f"{schemas.WALL_SNAP_MAX_M} m when its back snaps onto a wall (this move: "
                                             f"{dist:.2f} m)")
    front = G.front_direction_deg(rotation) if (item.get("front_deg") is not None or args.get("snap_wall_id")) \
        else None
    _set_footprint(item, center, rotation, p.size, front)
    _label(item, before, args, ["footprint", "front_deg"])
    if args.get("snap_wall_id"):
        item["adjusted_by_ai"]["snapped_wall"] = str(args["snap_wall_id"])
    if clamped is not None:
        item["adjusted_by_ai"]["move_clamped"] = {"asked_m": clamped, "limit_m": limit,
                                                  "note": "moved as far as a drawn piece may, towards the asked place"}
    return [item["id"]]


def _rotate(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    before = copy.deepcopy(item)
    front = float(args["front_deg"]) % 360.0
    _rot, size = placer.front_frame(item["footprint"], item.get("front_deg"))
    if item["type"] in schemas.FRONTLESS_TYPES:
        raise EditRejected("frontless", f"{item['id']}: a {item['type']} has no front to turn")
    if _fixed(item):
        r = PL._Room(b, room)
        problem = _front_problem(r, item["id"]) if item["id"] in r.pieces else None
        if problem is None:
            raise EditRejected("drawn_lock", f"{item['id']}: drawn fixed equipment turns only for a clear error (its "
                                             f"back off the wall, its front into a wall or its door blocked); none "
                                             f"here")
        trial = copy.deepcopy(b)
        _set_footprint(_piece(trial, item["id"]), item["footprint"]["center"], front + 90.0, size, front)
        r2 = PL._Room(trial, room)
        still = _front_problem(r2, item["id"])
        if still is not None:
            raise EditRejected("drawn_lock", f"{item['id']}: the new front does not fix the error ({problem}); with "
                                             f"the front at {front:.0f} deg {still}")
    _set_footprint(item, item["footprint"]["center"], front + 90.0, size, front)
    _label(item, before, args, ["footprint", "front_deg"])
    return [item["id"]]


def _resize(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    if _fixed(item):
        raise EditRejected("drawn_lock", f"{item['id']}: drawn fixed equipment keeps its drawn size")
    if _drawn(item) and kept_room(b, room):
        raise EditRejected("drawn_lock", f"{item['id']}: the room keeps its drawn pieces' sizes")
    size = (float(args["size"][0]), float(args["size"][1]))
    if item["type"] == "unknown" or not PL._fits(item["type"], size):
        raise EditRejected("product_size", f"{item['id']}: {size[0]:.2f} x {size[1]:.2f} m is not a real "
                                           f"{item['type']} size (size table)")
    if item.get("front_deg") is not None and PL.oriented_fit(item["type"], size)["turned"]:
        raise EditRejected("product_size", f"{item['id']}: {size[0]:.2f} m along the front x {size[1]:.2f} m deep is "
                                           f"a {item['type']} turned 90° ({_fmt_range(PL.size_range(item['type']))})")
    before = copy.deepcopy(item)
    r = PL._Room(b, room)
    p = r.pieces.get(item["id"]) or placer.drawn_piece(item)
    center = p.center
    if item["id"] in r.pieces and PL.back_on_wall(p, r)[0]:
        # The back stays on its wall: the piece grows or shrinks from the wall line.
        mid = placer.back_edge_midpoint(p.center, p.rotation_deg, p.size)
        center = placer.anchored_center({"kind": "back_edge", "point": list(mid)}, p.rotation_deg, size)
    front = item.get("front_deg")
    _set_footprint(item, center, p.rotation_deg, size, front)
    if item.get("source") == "added_by_ai":
        item["height"] = schemas.HEIGHTS.get(item["type"], item.get("height"))
    _label(item, before, args, ["footprint"])
    return [item["id"]]


def _change_type(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    new = args["type"]
    old = item["type"]
    if new == old and item.get("status") == "unverified":
        return _confirm_type(b, item, room, args)
    if new == old:
        raise EditRejected("no_change", f"{item['id']} is already a {new}")
    rtype, sub = room.get("room_type"), room.get("room_subtype")
    # fix round after P6a (module docstring): the room's types with their aliases (plausibility.room_types)
    types = room_types_of(b, room)
    if _drawn(item) and old == "unknown":
        allowed = room_allowed(b, room) | set(PL.ALWAYS_ALLOWED) - {"unknown"}
    elif _fixed(item) and schemas.misplaced_fixed(old, rtype):
        # real03: fixed equipment in a room that never holds it is a reading error (CLAUDE.md: a clear error).
        allowed = (set(schemas.allowed_types(rtype, sub)) | set(PL.ALWAYS_ALLOWED)) - {"unknown", old}
    elif _fixed(item):
        raise EditRejected("drawn_lock", f"{item['id']}: drawn fixed equipment keeps its type ({old})")
    elif _drawn(item):
        if kept_room(b, room):
            raise EditRejected("drawn_lock", f"{item['id']}: the room keeps its drawn pieces' types")
        allowed = room_allowed(b, room, schemas.change_types)
    else:
        allowed = room_allowed(b, room) - set(schemas.FIXED_TYPES)
    if new not in allowed:
        kinds = rtype if types == [rtype] else f"{rtype} ({' / '.join(str(t) for t in types)})"
        raise EditRejected("room_type", f"{new} is not a piece a {kinds} room may hold here")
    size = item["footprint"]["size"]
    if not PL._fits(new, size):
        raise EditRejected("product_size", f"{item['id']}: {float(size[0]):.2f} x {float(size[1]):.2f} m does not fit "
                                           f"a {new} (size table)")
    roles = _anchor_roles(room)
    if new in roles and any(f["type"] in roles and f["id"] != item["id"] and f.get("build") is not False
                            for f in b["furniture"] if f.get("room_id") == room["id"]):
        raise EditRejected("second_anchor", f"the room already has its {' / '.join(sorted(roles))}: never a second "
                                            f"anchor piece")
    before = copy.deepcopy(item)
    item["type"] = new
    if item.get("source") == "added_by_ai":
        item["height"] = schemas.HEIGHTS.get(new)
    if old == "unknown":
        item["inferred"] = True
        item.setdefault("evidence", []).append({"file": EVIDENCE_FILE, "method": "inferred", "confidence": 0.7,
                                                "text": f"type {new} inferred by the agent: {args.get('reason')}"})
    _label(item, before, args, ["type", "height"])
    return [item["id"]]


def room_types_of(b: dict, room: dict) -> list[str]:
    """Fix round after P6a (module docstring): the room's types as the checks read them (``plausibility.room_types``:
    its ``room_type``, the other room names its face holds, the alias kind of an ``other`` / ``unknown`` room)."""
    try:
        return [str(t) for t in PL.room_types(b, room) if t]
    except (KeyError, TypeError, ValueError):
        return [str(room.get("room_type"))]


def room_allowed(b: dict, room: dict, row=schemas.allowed_types) -> set:
    """Fix round after P6a (module docstring): the union of ``row(room type, room_subtype)`` (``schemas.allowed_types``
    or ``schemas.change_types``) over the room's types with their aliases (``room_types_of``), as F1 and G14 read the
    room (``plausibility.allowed_in`` without the stand-alone lamps, plants and side tables)."""
    out: set = set()
    for t in room_types_of(b, room):
        out |= set(row(t, room.get("room_subtype")))
    return out


def _confirm_type(b: dict, item: dict, room: dict, args: dict) -> list[str]:
    """Integration of the fix round after P5 (A_agent's ask): ``retype_piece`` / ``change_type`` with the piece's own
    type confirms an unverified piece (``status`` verified, ``adjusted_by_ai`` with the reason, the AI passes'
    ``type_candidates`` kept, its ``needs_review`` entry closed) when its room may hold the type and its footprint fits
    it. Why: complete_group refuses a group whose anchor is unverified ("retype_piece first") and retype_piece refused
    the anchor's own type as no_change, a deadlock (P5 seq 4730/4732, 5111/5113: the desks f_L0_026 / f_L0_024)."""
    new = item["type"]
    rtype = room.get("room_type")
    # fix round after P6a: the room's types with their aliases, as _change_type reads them
    if new in (None, "unknown") or new not in room_allowed(b, room) | set(PL.ALWAYS_ALLOWED):
        raise EditRejected("room_type", f"{item['id']}: a {rtype} room does not hold a {new}: retype it instead")
    size = item["footprint"]["size"]
    if not PL._fits(new, size):
        raise EditRejected("product_size", f"{item['id']}: {float(size[0]):.2f} x {float(size[1]):.2f} m does not fit "
                                           f"a {new} (size table): retype it instead")
    before = copy.deepcopy(item)
    item["status"] = "verified"
    item.setdefault("evidence", []).extend(_ai_evidence(args, f"type {new} confirmed by the agent: "
                                                              f"{args.get('reason')}"))
    _label(item, before, args, ["status"])
    item["adjusted_by_ai"]["confirmed_type"] = new
    b["needs_review"] = [n for n in b.get("needs_review") or [] if n.get("id") != item["id"]]
    return [item["id"]]


def _s2_depth(args: dict) -> Optional[float]:
    """The S2 cut depth (metres) of the edit's ``target_finding``, None when the edit targets no S2 finding."""
    tf = args.get("target_finding") if isinstance(args.get("target_finding"), dict) else None
    if not tf or str(tf.get("check") or "") != "S2":
        return None
    metrics = tf.get("metrics") if isinstance(tf.get("metrics"), dict) else {}
    depth = metrics.get("depth_m", metrics.get("overlap_m"))
    try:
        return None if depth is None else float(depth)
    except (TypeError, ValueError):
        return None


def _swap_model(b: dict, args: dict, catalog) -> list[str]:
    item = _piece(b, args["piece_id"])
    depth = _s2_depth(args)
    if depth is not None and depth < S2_SWAP_MIN_M - 1e-9:
        # Milestone 13: a cut below the S2 class tolerance is not visible; no model swap fixes it
        raise EditRejected("within_tolerance", f"{item['id']}: the S2 cut of {depth:.3f} m is within tolerance "
                                               f"(below {S2_SWAP_MIN_M:.2f} m): no model swap is offered for it")
    if catalog is None:
        from wenart.furniture import catalog as C
        catalog = C.load()
    entry = catalog.entry(args["asset_id"])
    if entry is None:
        raise EditRejected("asset_exists", f"no catalogue model {args['asset_id']!r}")
    if entry.get("type") != item["type"]:
        raise EditRejected("asset_type", f"{args['asset_id']} is a {entry.get('type')} model, not a {item['type']}")
    # 28 Oct 2026 (real06: the agent pinned a freestanding stove and a tall fridge to the hob and the fridge built into
    # the counters; they stood as boxes in the run): a hob or fridge in a counter run is part of the run
    from wenart.furniture import fit as F
    if item["type"] in ("stove", "fridge") and item["id"] in F.kitchen_built_ins(b)["sinks"]:
        raise EditRejected("built_in", f"{item['id']}: the {item['type']} stands in a counter run and is built into "
                                       "it (a hob in the worktop, an integrated fridge in the run's fronts: kitchen "
                                       "design rule of 28 Oct 2026); no library model replaces it")
    from wenart.furniture import catalog as C
    status = str(C.audit_status(entry) or "").lower()
    why = (f"audit {status}" if status in C.REMOVED_STATUSES else None) or C.title_refusal(entry)
    if why:
        # 28 Oct 2026 (user on real04: a kitchen sink as a washbasin, a window on a wardrobe): no swap to a model the
        # audit or its own names refuse (the fit would refuse the pin)
        raise EditRejected("asset_unusable", f"{args['asset_id']} is not used: {why[:300]}")
    current = (item.get("asset") or {}).get("asset_id") if isinstance(item.get("asset"), dict) else None
    if args["asset_id"] in (current, item.get("asset_pin")):
        raise EditRejected("no_change", f"{item['id']} already uses the model {args['asset_id']}")
    off = off_style_refusal(b, entry)
    if off is not None:
        raise EditRejected("off_style", f"{item['id']}: {off}")
    low = lower_quality_refusal(catalog.entry(current) if current else None, entry)
    if low is not None:
        raise EditRejected("lower_quality", f"{item['id']}: {low}")
    refused = generated_pin_refusal(b, item, args["asset_id"], entry, catalog)
    if refused is not None:
        raise EditRejected("pin_refused", f"{item['id']}: {refused}: the real model stays; swap to a real model of "
                                          f"the type or use another tool")
    before = copy.deepcopy(item)
    item["asset_pin"] = args["asset_id"]
    _label(item, before, args, ["asset_pin"])
    return [item["id"]]


def off_style_refusal(b: dict, entry: dict) -> Optional[str]:
    """27 Oct 2026 (CLAUDE.md: the models fit together and carry the style; pod run 224516: the agent's swaps): why a
    model whose styles hold no family of the project's chain (``fit.style_chain`` of ``_style_family_of``: the family,
    then its fallbacks; ``neutral`` fits every family) may not be swapped in, else None. No family known: None."""
    from wenart.furniture import catalog as C
    from wenart.furniture import fit as F

    family = _style_family_of(b)
    if family is None:
        return None
    chain = F.style_chain(family)
    if any(C.styles_match(entry, fam) for fam in chain):
        return None
    return (f"{entry.get('id')} is of the styles {entry.get('styles') or []}, none of the project's chain "
            f"{' -> '.join(str(c) for c in chain)}: choose a model of the style")


SWAP_QUALITY_MARGIN = 0.25         # a swap may not take a model rated this much below the current one


def model_rating(entry: Optional[dict]) -> float:
    """The rating a swap compares (1-5): the mean of the judges' quality (``fit.quality_of``, when recorded) and the
    audit's vision quality (``fit.vision_quality_of``, when recorded), else ``fit.DEFAULT_QUALITY``."""
    from wenart.furniture import fit as F

    if not isinstance(entry, dict):
        return F.DEFAULT_QUALITY
    known = [F.quality_of(entry)] if entry.get("quality") is not None else []
    vq = F.vision_quality_of(entry)
    if vq is not None:
        known.append(vq)
    return sum(known) / len(known) if known else F.DEFAULT_QUALITY


def lower_quality_refusal(current: Optional[dict], entry: dict) -> Optional[str]:
    """27 Oct 2026 (pod run 091638, real06: Argus swapped the master bed, an ABO bed rated 4.5, for an unrated HSSD
    model that rendered as a glossy black slab, over a minor "plain styling" remark): why ``entry`` may not replace
    the current model ``current`` (rated more than ``SWAP_QUALITY_MARGIN`` lower, ``model_rating``), else None."""
    if not isinstance(current, dict):
        return None
    qc, qn = model_rating(current), model_rating(entry)
    if qn >= qc - SWAP_QUALITY_MARGIN - 1e-9:
        return None
    return (f"{entry.get('id')} is rated {qn:.1f} against {qc:.1f} of the current model {current.get('id')}: a swap "
            f"never takes a lower-rated model; choose one rated at least {qc - SWAP_QUALITY_MARGIN:.1f}, or fix the "
            f"view (camera, light) instead")


def generated_pin_refusal(b: dict, item: dict, asset_id: str, entry: dict, catalog) -> Optional[str]:
    """Fix round after P6a (module docstring): the fit's ``pin_refused`` reason when ``asset_id`` is a generated model
    (``entry["source"]`` ``fit.GENERATED``) that the refit refuses for ``item`` (``fit.fit_piece`` with the pin in the
    building's licence mode and style family and the piece's ``fit.piece_ceiling``: a real product of the type fits,
    or the pin fails the caps, the height or the sloped ceiling); None for any other model or a pin the fit takes.
    A fit error is a rejected edit (``refit``)."""
    from wenart.furniture import fit as F

    if entry.get("source") != F.GENERATED:
        return None
    try:
        asset = F.fit_piece(dict(item, build=True, asset_pin=asset_id), catalog, mode=licence_mode_of(b),
                            style_family=_style_family_of(b), ceiling=F.piece_ceiling(b, item))
    except Exception as exc:  # noqa: BLE001 - as _build_retyped: a refit error is a rejected edit, never a crash
        raise EditRejected("refit", f"{item['id']}: the refit with {asset_id} failed ({type(exc).__name__}: "
                                    f"{str(exc)[:160]}); the piece stays as it was") from exc
    why = asset.get("pin_refused")
    return str(why) if why and str(why).startswith(f"{asset_id}:") else None


def _new_piece(b: dict, room: dict, piece: placer.Piece, args: dict, text: str) -> dict:
    rot = round(piece.rotation_deg, 2)
    return {"id": _next_id(b, room["level_id"]), "level_id": room["level_id"], "room_id": room["id"],
            "type": piece.type, "type_raw": None, "source": "added_by_ai",
            "footprint": {"center": [round(piece.center[0], 3), round(piece.center[1], 3)],
                          "size": [piece.size[0], piece.size[1]], "rotation_deg": rot},
            "front_deg": round(G.front_direction_deg(rot), 2), "height": schemas.HEIGHTS.get(piece.type),
            "asset": None, "status": "verified", "evidence": _ai_evidence(args, text),
            "adjusted_by_ai": None}


def _check_anchor(b: dict, room: dict, ftype: str) -> None:
    roles = _anchor_roles(room)
    if ftype in roles and any(f["type"] in roles and f.get("build") is not False
                              for f in b["furniture"] if f.get("room_id") == room["id"]):
        raise EditRejected("second_anchor", f"the room already has its {' / '.join(sorted(roles))}: never a second "
                                            f"anchor piece")


def _add(b: dict, args: dict) -> list[str]:
    room = _room(b, args["room_id"])
    ftype = args["type"]
    if ftype not in schemas.allowed_types(room.get("room_type"), room.get("room_subtype")):
        raise EditRejected("room_type", f"a {ftype} is not a piece of a {room.get('room_type')} room")
    _check_anchor(b, room, ftype)
    ctx = placer.room_context(b, room)
    size = schemas.default_size(ftype)
    rule = schemas.orientation_rule(ftype)
    wall = rule["back"] in ("wall", "wall_or_group")
    if args.get("center") is not None:
        center = (float(args["center"][0]), float(args["center"][1]))
        if args.get("front_deg") is not None:
            piece = placer.Piece(ftype, center, G.normalise_angle(float(args["front_deg"]) + 90.0), size, wall)
        else:
            piece = placer.Piece(ftype, center, 0.0, size, wall)
            if wall:
                found = placer.snap_to_wall(piece, ctx)
                if found is None:
                    raise EditRejected("snap", f"no free wall for the {ftype} near {list(center)}")
                piece.center, piece.rotation_deg = found[0], found[1]
    else:
        # Milestone 12: a missing partner of a group in the room (a nightstand by a bed) is placed by the group
        # solver at its place in the group; anything else by the placer as before.
        ids = _add_partner(b, room, ftype, args)
        if ids:
            return ids
        obstacles = [placer.drawn_piece(f, i) for i, f in enumerate(_floor_items(b, room["id"]))]
        proposal = [{"type": ftype, "center": [ctx.polygon.centroid.x, ctx.polygon.centroid.y], "rotation_deg": 0.0,
                     "size": list(size), "against_wall": wall, "reason": args.get("reason") or "agent"}]
        result = placer.place(proposal, ctx, obstacles=obstacles)
        if not result.pieces:
            why = result.dropped[0]["failed"] if result.dropped else []
            raise EditRejected("no_place", f"no place for a {ftype} in {room['id']} ({', '.join(why)})")
        piece = result.pieces[0]
        if ftype in schemas.COMPANIONS:
            hosts = [o for o in obstacles if o.type in schemas.COMPANIONS[ftype]]
            placer.face_host(piece, hosts)
    item = _new_piece(b, room, piece, args, args.get("reason") or f"{ftype} added by the agent")
    b["furniture"].append(item)
    return [item["id"]]


def _add_partner(b: dict, room: dict, ftype: str, args: dict) -> list[str]:
    """One missing partner of ``ftype`` added to the first group of the room that misses it (the solver places the
    group's missing partners and only the first of this type is kept); [] when no group misses one or none fits."""
    for g in GR.group_members(b, room["id"]):
        template = GR.load_groups().get(g.get("group") or "")
        if not template or template["layout"] != "anchored" or ftype not in (g.get("missing") or []):
            continue
        try:
            return _solve_apply(b, room, _program(b, room, [_group_entry(room, g)]), args,
                                f"{ftype} of {g['group_id']}", fixed=_ai_floor_ids(b, room["id"]), only_type=ftype)
        except EditRejected:
            continue
    return []


def _add_group(b: dict, args: dict) -> list[str]:
    room = _room(b, args["room_id"])
    res = GR.place_group(b, room["id"], args["group"], args.get("anchor"))
    if not res["ok"]:
        raise EditRejected("group", f"{args['group']}: {res['reason']}")
    ids = []
    for item in res["pieces"]:
        item = dict(item)
        if args.get("model"):
            item["evidence"] = list(item["evidence"]) + _ai_evidence(args, args.get("reason") or "")
        b["furniture"].append(item)
        ids.append(item["id"])
    return ids


def _remove(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    if item.get("source") == "added_by_ai":
        b["furniture"] = [f for f in b["furniture"] if f["id"] != item["id"]]
        b["decor"] = [d for d in b.get("decor") or [] if d.get("host_id") != item["id"]]
        return [item["id"]]
    room = _room(b, item.get("room_id")) if item.get("room_id") else {}
    if _fixed(item) and not schemas.misplaced_fixed(item["type"], room.get("room_type")):
        raise EditRejected("drawn_lock", f"{item['id']}: drawn fixed equipment ({item['type']}) is never removed")
    if not _fixed(item):
        # Milestone 12 (CLAUDE.md: "A drawn piece is removed only when it is clearly not furniture (logged with the
        # plan crop as evidence)"): a drawn piece leaves the scene only through mark_not_furniture (kind + evidence);
        # misplaced fixed equipment (a kitchen piece read in a stair room) may still be removed with a reason.
        raise EditRejected("drawn_lock", f"{item['id']}: a drawn {item['type']} is removed only when it is clearly "
                                         f"not furniture: use mark_not_furniture with its kind and the plan-crop evidence")
    if not str(args.get("reason") or "").strip():
        raise EditRejected("reason", f"{item['id']}: a drawn piece is removed only with a reason")
    if item.get("build") is False:
        raise EditRejected("no_change", f"{item['id']} is not built already")
    before = copy.deepcopy(item)
    item["build"] = False
    _label(item, before, args, ["build"])
    return [item["id"]]


def _set_room_type(b: dict, args: dict) -> list[str]:
    room = _room(b, args["room_id"])
    new = args["room_type"]
    if room.get("room_type") == new:
        raise EditRejected("no_change", f"{room['id']} is already a {new}")
    trial = copy.deepcopy(room)
    trial["room_type"] = new
    r = PL._Room(b, trial)
    bad = [v for v in PL._r1(r) if v["severity"] in ("critical", "major")]
    if bad:
        raise EditRejected("R1", "; ".join(v["message"] for v in bad))
    old = room.get("room_type")
    room["room_type"] = new
    label = {"reason": str(args.get("reason") or "")}
    for k in ("round", "log_seq", "model"):
        if args.get(k) is not None:
            label[k] = args[k]
    label["changed"] = dict(((room.get("adjusted_by_ai") or {}).get("changed") or {}))
    label["changed"].setdefault("room_type", old)
    room["adjusted_by_ai"] = label
    return [room["id"]]


# --------------------------------------------------------------------------
# Milestone 12: group tools, fixture fixes, fronts (docs/milestone12.md §5.3; owner: track G)
# --------------------------------------------------------------------------

def _ai_floor_ids(b: dict, room_id: str, exclude=()) -> list[str]:
    """The room's added floor pieces the solver keeps where they are."""
    ex = set(exclude)
    return [f["id"] for f in b.get("furniture") or [] if f.get("room_id") == room_id and f.get("source") == "added_by_ai"
            and not schemas.off_floor(f) and f["id"] not in ex]


def _why_not(cands: list[dict]) -> str:
    """The numbers of the best failed candidate (hard failures first, then the groups not placed)."""
    if not cands:
        return "no candidate position fits the room"
    c = cands[0]
    parts = list(c.get("hard_failures") or [])[:3] or [f"{x['group']}: {x['reason']}" for x in c.get("not_placed") or []]
    return "; ".join(parts) or "no candidate adds a piece"


def _program(b: dict, room: dict, entries: list[dict], zones: Optional[list] = None) -> dict:
    from wenart.furniture import program as PR

    base = PR.room_program(b, room["id"])
    return {"room_id": room["id"], "zones": list(base.get("zones") or []) + list(zones or []), "groups": entries,
            "reason": "agent edit"}


def _solve_apply(b: dict, room: dict, prog: dict, args: dict, text: str, *, fixed: list[str], index: int = 1,
                 accept=None, only_type: Optional[str] = None, drawn_group=None) -> list[str]:
    """Solve ``prog`` with ``fixed`` pieces kept, take usable candidate ``index`` (1-based; ``accept`` filters) and
    add its pieces to ``b`` (``only_type``: only the first piece of that type). Returns the changed ids (the
    re-placed drawn members, then the new pieces). Milestone 13: ``drawn_group`` (a ``groups.drawn_groups`` entry)
    makes the solver re-solve that drawn group as one unit (``solve_room(..., drawn_group=...)``, track T3); the
    candidate is applied through ``layout.apply_choice`` (round 2): the drawn pieces of ``candidate["resolved"]``
    change in place with everything the solver wrote (a kept member gets its ``drawn_group`` and ``group`` too), the
    rugs of ``candidate["rugs"]`` come with the decor, the moved or resized members count as changed and are
    labelled."""
    from wenart.furniture import layout as LY
    from wenart.furniture import solver as SV

    cands = SV.solve_room(b, room["id"], prog, k=max(3, index), fixed_ids=fixed, drawn_group=drawn_group)
    passing = [c for c in cands if not c["hard_failures"] and c["pieces"]]
    usable = [c for c in passing if accept is None or accept(c)]
    if not usable and passing:
        raise EditRejected("no_place", f"{text}: the places that pass the checks are elsewhere ("
                                       + "; ".join(f"candidate {c['rank']}: {c['pieces'][0]['type']} at "
                                                   f"{c['pieces'][0]['footprint']['center']}" for c in passing[:3]) + ")")
    if not usable:
        raise EditRejected("no_place", f"{text}: no place passes the checks ({_why_not(cands)})")
    if index > len(usable):
        raise EditRejected("candidate", f"candidate {index} does not exist: {len(usable)} usable candidate(s)")
    cand = usable[index - 1]
    if only_type is not None:
        keep = next((p for p in cand["pieces"] if p["type"] == only_type), None)
        if keep is None:
            raise EditRejected("no_place", f"{text}: the solver places no {only_type} ({_why_not(cands)})")
        cand = dict(cand, pieces=[keep])
    in_cand = {p["id"] for p in cand.get("pieces") or []}
    resolved = [pid for pid in cand.get("resolved") or [] if pid in in_cand]
    cand = dict(cand, resolved=resolved)
    was = {pid: _piece(b, pid) for pid in resolved}
    before = {pid: {k: _dump(f.get(k)) for k in ("footprint", "front_deg", "build", "asset")}
              for pid, f in was.items()}
    choice = {"rank": cand["rank"], "by": "agent", "reason": args.get("reason") or text}
    added = LY.apply_choice(b, room, cand, choice, completes=bool(room.get("has_documented_furniture")))
    # a drawn member re-placed, resized or rebuilt as part of its drawn group counts as changed (the solver labels
    # it adjusted_by_ai); a member the solver kept only carries its drawn_group and group now
    moved = [pid for pid in resolved
             if any(_dump(was[pid].get(k)) != v for k, v in before[pid].items())]
    if not added and not moved:
        # a re-solve level the solver skipped hands the drawn pieces back as drawn: nothing placed, nothing moved
        raise EditRejected("no_place", f"{text}: the solver places nothing and leaves the drawn pieces as drawn "
                                       f"({_why_not(cands) if cands[0].get('not_placed') else 'no place within '
                                        + str(GR.GROUP_MEMBER_MOVE_MAX_M) + ' m of the drawn centre'})")
    for f in added:
        f["evidence"] = list(f.get("evidence") or []) + _ai_evidence(args, args.get("reason") or text)
    for pid in moved:
        item = _piece(b, pid)
        adj = item.get("adjusted_by_ai") if isinstance(item.get("adjusted_by_ai"), dict) else None
        if adj is None or not str(adj.get("reason") or "").strip():
            # the solver re-placed a drawn member: the label with this edit's reason and the drawn values
            src = next(f for f in b["furniture"] if f["id"] == pid)
            drawn_before = {"type": item.get("drawn_type", item.get("type")),
                            "footprint": item.get("drawn_footprint") or item.get("footprint"),
                            "front_deg": item.get("drawn_front_deg", item.get("front_deg")),
                            "height": item.get("drawn_height", item.get("height")), "source": "from_documents"}
            _label(src, drawn_before, args, ["footprint", "front_deg"])
        else:
            for k in ("round", "log_seq", "model"):
                if args.get(k) is not None:
                    adj.setdefault(k, args[k])
    return moved + [f["id"] for f in added]


def _dump(value) -> str:
    import json
    return json.dumps(value, sort_keys=True, default=str)


def group_room_id(b: dict, group_id) -> str:
    """The room of a group id. A group id is ``<room_id>.<group>[...]``, or ``<zone_id>.<group>`` for a group of a
    zone (``program._entry``). The reading names the kitchen zone of an open-plan room ``<room_id>_kitchen``, without
    a dot, so the text before the first dot is then a zone id, not a room id: the room is the one that holds that
    zone. CPU pre-flight of 16 Oct 2026 (real04, P3 inputs): ``complete_group`` on ``r_L-1b_salon_kitchen.kitchen_run``
    (the open kitchen misses its fridge, G9) was refused as "no group ... in a room of the building"."""
    head = str(group_id).split(".", 1)[0]
    rooms = b.get("rooms") or []
    if any(r.get("id") == head for r in rooms):
        return head
    for r in rooms:
        if any(isinstance(z, dict) and z.get("zone_id") == head for z in r.get("zones") or []):
            return str(r.get("id"))
    return head


def _find_group(b: dict, group_id: str) -> tuple[dict, dict]:
    room_id = group_room_id(b, group_id)
    room = _room(b, room_id)
    found = next((g for g in GR.group_members(b, room_id) if g["group_id"] == group_id), None)
    if found is None:
        have = ", ".join(g["group_id"] for g in GR.group_members(b, room_id)) or "none"
        raise EditRejected("group_exists", f"no group {group_id!r} in {room_id} (groups: {have})")
    return room, found


def _group_entry(room: dict, g: dict) -> dict:
    from wenart.furniture import program as PR

    template = GR.load_groups()[g["group"]]
    entry = PR._entry(room["id"], g["group"], True, PR.drawn_options(g["group"], list(template["options"])),
                      anchor_id=g.get("anchor_id"), drawn=True, members=list(g.get("member_ids") or []),
                      missing=list(g.get("missing") or []))
    entry["group_id"] = g["group_id"]
    return entry


# Bathroom sense of 26 Oct 2026: the sets of one kind (a bathroom's set and a WC's set are one sanitary set of a room).
SAME_SET: dict[str, tuple[str, ...]] = {"bathroom_set": ("bathroom_set", "wc_set"),
                                         "wc_set": ("bathroom_set", "wc_set")}


def _place_group(b: dict, args: dict) -> list[str]:
    from wenart.furniture import program as PR

    room = _room(b, args["room_id"])
    name = args["group"]
    template = GR.load_groups().get(name)
    if template is None:
        raise EditRejected("group", f"no group template {name!r} (groups.yaml)")
    allowed = GC.allowed_types_at(b, room, None)
    rtype = room.get("room_type")
    # 26 Oct 2026: the room's kinds too (``program.room_kinds``: a dressing room read from an ``other`` room's label)
    if not set(template["room_types"]) & ({rtype} | set(PR.room_kinds(b, room))
                                          | {z.get("kind") for z in room.get("zones") or []}):
        raise EditRejected("room_type", f"a {name} group does not belong in a {rtype} room (groups.yaml room types: "
                                        f"{', '.join(template['room_types'])})")
    option = args.get("option")
    if option is not None and option not in template["options"]:
        raise EditRejected("option", f"{option!r} is not an option of {name} ({', '.join(template['options'])})")
    if template["layout"] in ("set", "run"):
        # bathroom sense of 26 Oct 2026: a room holds one set or run of a kind (``groups.match_groups``); asked again,
        # its missing members are completed (the pieces it has are adopted), never a second set beside it
        have = next((g for g in GR.group_members(b, room["id"]) if g.get("group") in SAME_SET.get(name, (name,))),
                    None)
        if have is not None:
            if not have.get("missing"):
                raise EditRejected("no_change", f"{room['id']} already has its {have['group']} {have['group_id']} "
                                                f"(anchor {have.get('anchor_id')}, members "
                                                f"{', '.join(have.get('member_ids') or []) or 'none'}): nothing "
                                                f"missing, never a second set")
            return _complete_group(b, dict(args, group_id=have["group_id"]))
    # Milestone 13 (B3): a drawn group of this template (the drawn anchor with its drawn partners, built or not) is
    # re-solved as one unit around the drawn anchor instead of a second group beside it
    drawn = next((g for g in GR.drawn_groups(b, room["id"]) if g.get("template") == name), None)
    if drawn is not None:
        if option is not None:
            args = dict(args, option=option)
        return _solve_apply(b, room, _program(b, room, []), args,
                            f"{name} group re-solved around the drawn {drawn.get('anchor_type')} "
                            f"{drawn['anchor_id']}", fixed=_ai_floor_ids(b, room["id"]), drawn_group=drawn)
    if template["layout"] == "anchored":
        types = set(template["anchor"]["types"]) & allowed
        if not types:
            raise EditRejected("room_type", f"no anchor of the {name} group may stand in a {rtype} room")
        roles = _anchor_roles(room)
        if types & roles and any(f["type"] in roles and GR.piece_is_built(f) for f in b["furniture"]
                                 if f.get("room_id") == room["id"]):
            raise EditRejected("second_anchor", f"the room already has its {' / '.join(sorted(roles))}: never a "
                                                f"second anchor piece (complete_group adds the missing partners)")
    rows = [g for g in PR.room_program(b, room["id"])["groups"] if g["group"] == name and not g["drawn"]]
    entry = rows[0] if rows else PR._entry(room["id"], name, True, list(template["options"]))
    taken = {g["group_id"] for g in GR.group_members(b, room["id"])}
    while entry["group_id"] in taken:
        entry["group_id"] += "+"
    entry["required"] = True
    if option is not None:
        entry["chosen"] = option
    return _solve_apply(b, room, _program(b, room, [entry]), args, f"{name} group",
                        fixed=_ai_floor_ids(b, room["id"]))


def _resolve_group(b: dict, room: dict, anchor_id: Optional[str]) -> Optional[dict]:
    """Round 2 (Milestone 13, D5): the drawn group of ``anchor_id`` (``groups.drawn_groups``) when the room's program
    marks it for a re-solve as one unit (``program.room_program``: the anchor misread, not built or failing the
    checks), else None: the drawn anchor stays where it is and only its partners are placed."""
    from wenart.furniture import program as PR

    if not anchor_id:
        return None
    marked = any(r.get("drawn") and r.get("anchor_id") == anchor_id and r.get("resolve")
                 for r in PR.room_program(b, room["id"])["groups"])
    if not marked:
        return None
    return next((g for g in GR.drawn_groups(b, room["id"]) if g.get("anchor_id") == anchor_id), None)


NO_COMPLETION_NOTES: tuple[str, ...] = ("no completion", "duplicate outline")


def program_refusal(building: dict, room: dict, g: dict) -> Optional[str]:
    """Fix round after P4b (module docstring): why ``complete_group`` adds nothing to the group ``g`` (a
    ``groups.group_members`` entry) because the room's program completes nothing there (its row's note: a group that
    does not belong in the room, a duplicate outline), else None."""
    from wenart.furniture import program as PR

    rows = PR.room_program(building, room["id"])["groups"]
    row = next((r for r in rows if r.get("drawn") and r.get("anchor_id") == g.get("anchor_id")
                and r.get("group") == g.get("group")), None)
    note = str((row or {}).get("note") or "")
    if not note.startswith(NO_COMPLETION_NOTES):
        return None
    return f"{g['group_id']}: the room's program completes nothing here ({note})"


def unsure_group_anchor(anchor: Optional[dict]) -> bool:
    """Fix round after P6b (module docstring): True when ``complete_group`` refuses the group of ``anchor`` until
    ``retype_piece`` confirms it: an ``unverified`` anchor the reading could not agree on (``program.unsure_anchor``);
    False for a verified anchor and for a vector-drawn one the reading typed by code (``infer.CODE_TYPE_METHODS``),
    which the program, the solver and the decor (``decor.trusted_host``) already complete like a verified one."""
    from wenart.furniture import program as PR

    return anchor is not None and PR.unsure_anchor(anchor)


def _complete_group(b: dict, args: dict) -> list[str]:
    room, g = _find_group(b, args["group_id"])
    if g.get("missing"):
        refusal = program_refusal(b, room, g)        # fix round after P4b: before the solver runs
        if refusal is not None:
            raise EditRejected("no_completion", refusal)
    anchor = next((f for f in b["furniture"] if f["id"] == g.get("anchor_id")), None)
    if unsure_group_anchor(anchor):
        # fix round after P6b (module docstring): a drawn anchor typed by code from the drawing is completed like a
        # verified one; only a piece the reading could not agree on waits for retype_piece
        raise EditRejected("unverified", f"{g['group_id']}: the anchor {anchor['id']} is unverified and not typed by "
                                         f"code from the drawing (retype_piece first)")
    if not g.get("missing"):
        raise EditRejected("no_change", f"{g['group_id']}: nothing missing (members: "
                                        f"{', '.join(g.get('member_ids') or []) or 'none'})")
    # Milestone 13 (round 2): a drawn group the program marks for a re-solve (its anchor misread or failing the
    # checks) is completed as one unit around the drawn anchor (every member within 0.5 m, drawn values kept)
    drawn = _resolve_group(b, room, g.get("anchor_id")) if anchor is not None and _drawn(anchor) else None
    text = f"{g['group_id']} (missing {', '.join(g['missing'])})"
    if drawn is not None:
        text += f", re-solved as one unit around the drawn {anchor['type']} {anchor['id']}"
    return _solve_apply(b, room, _program(b, room, [_group_entry(room, g)]), args, text,
                        fixed=_ai_floor_ids(b, room["id"]), drawn_group=drawn)


def free_spans(building: dict, room_id: str, min_length: float = 0.3) -> list[dict]:
    """The free stretches of the room's walls: ``[{"span_id", "edge", "wall_id", "start", "end", "length"}]`` (the
    outline edges, counter-clockwise, minus door openings with 0.10 m each side and the built floor pieces whose back
    stands on the edge); ``span_id`` = ``<room>.s<k>``. ``move_group`` takes one; the room brief lists them."""
    room = _room(building, room_id)
    ctx = placer.room_context(building, room)
    out = []
    walls = LK._wall_shapes(building, room.get("level_id"))
    built = [placer.drawn_piece(f, i) for i, f in enumerate(_floor_items(building, room_id)) if GR.piece_is_built(f)]
    for e, (a, c) in enumerate(ctx.segments):
        length = G.distance(a, c)
        if length < min_length:
            continue
        ux, uy = (c[0] - a[0]) / length, (c[1] - a[1]) / length
        blocked = []
        for d in ctx.doors:
            if G.point_segment_distance(d.inner_point, a, c) <= 0.15:
                t = (d.inner_point[0] - a[0]) * ux + (d.inner_point[1] - a[1]) * uy
                blocked.append((t - d.width / 2.0 - 0.10, t + d.width / 2.0 + 0.10))
        for p in built:
            mid = placer.back_edge_midpoint(p.center, p.rotation_deg, p.size)
            if G.point_segment_distance(mid, a, c) <= 0.10:
                t = (mid[0] - a[0]) * ux + (mid[1] - a[1]) * uy
                blocked.append((t - p.size[0] / 2.0, t + p.size[0] / 2.0))
        mid = ((a[0] + c[0]) / 2.0, (a[1] + c[1]) / 2.0)
        wall_id = None
        if walls:
            wid, shape = min(walls, key=lambda ws: (round(ws[1].distance(Point(mid)), 6), ws[0]))
            wall_id = wid if shape.distance(Point(mid)) <= 0.15 else None
        t0 = 0.0
        for lo, hi in sorted(blocked) + [(length, length)]:
            if lo - t0 >= min_length:
                out.append({"edge": e, "wall_id": wall_id, "start": round(max(0.0, t0), 3),
                            "end": round(min(length, lo), 3)})
            t0 = max(t0, hi)
    for k, s in enumerate(out):
        a, c = ctx.segments[s["edge"]]
        length = G.distance(a, c)
        s["span_id"] = f"{room_id}.s{k}"
        s["length"] = round(s["end"] - s["start"], 3)
        s["from"] = [round(a[0] + (c[0] - a[0]) * s["start"] / length, 3), round(a[1] + (c[1] - a[1]) * s["start"] / length, 3)]
        s["to"] = [round(a[0] + (c[0] - a[0]) * s["end"] / length, 3), round(a[1] + (c[1] - a[1]) * s["end"] / length, 3)]
    return out


def _move_group(b: dict, args: dict) -> list[str]:
    room, g = _find_group(b, args["group_id"])
    ids = [g["anchor_id"]] + list(g.get("member_ids") or []) if g.get("anchor_id") else list(g.get("member_ids") or [])
    items = [f for f in b["furniture"] if f["id"] in ids]
    if any(f.get("source") != "added_by_ai" for f in items):
        drawn = [f["id"] for f in items if f.get("source") != "added_by_ai"]
        raise EditRejected("drawn_lock", f"{g['group_id']}: drawn pieces ({', '.join(drawn)}) stay where they are "
                                         f"drawn; complete_group adds partners, relayout_room re-solves the room")
    span = next((s for s in free_spans(b, room["id"]) if s["span_id"] == args["span_id"]), None)
    if span is None:
        raise EditRejected("span", f"no free span {args['span_id']!r} in {room['id']} (free_spans)")
    ctx = placer.room_context(b, room)
    a, c = ctx.segments[span["edge"]]
    length = G.distance(a, c)
    u = ((c[0] - a[0]) / length, (c[1] - a[1]) / length)
    n = (-u[1], u[0])                                   # inward normal (counter-clockwise outline)
    lo, hi = span["start"], span["end"]
    if args.get("offset") is not None:
        t = lo + float(args["offset"])
        if not lo - 1e-6 <= t <= hi + 1e-6:
            raise EditRejected("span", f"offset {float(args['offset']):.2f} m is outside span {span['span_id']} "
                                       f"({span['length']:.2f} m long)")
        lo, hi = max(span["start"], t - 0.25), min(span["end"], t + 0.25)
    depth = 2.2
    strip = [[a[0] + u[0] * s + n[0] * d, a[1] + u[1] * s + n[1] * d] for s, d in ((lo, 0.0), (hi, 0.0), (hi, depth),
                                                                                 (lo, depth))]
    zone_id = f"{room['id']}.span"
    template = GR.load_groups()[g["group"]]
    option = next(((f.get("layout") or {}).get("option") for f in items if (f.get("layout") or {}).get("option")),
                  None)
    from wenart.furniture import program as PR

    entry = PR._entry(room["id"], g["group"], True, [option] if option in template["options"]
                      else list(template["options"]), zone_id=zone_id)
    entry["group_id"] = g["group_id"]
    trial = copy.deepcopy(b)
    trial["furniture"] = [f for f in trial["furniture"] if f["id"] not in ids]

    def on_span(cand: dict) -> bool:
        first = cand["pieces"][0]
        p = placer.drawn_piece(first)
        mid = placer.back_edge_midpoint(p.center, p.rotation_deg, p.size)
        return G.point_segment_distance(mid, a, c) <= 0.10

    new_ids = _solve_apply(trial, room, _program(trial, room, [entry], [{"zone_id": zone_id, "kind": None,
                                                                         "polygon": strip}]),
                           args, f"{g['group_id']} on span {span['span_id']}", fixed=_ai_floor_ids(trial, room["id"]),
                           accept=on_span)
    b["furniture"] = trial["furniture"]
    # 29 Oct 2026 (real06 run 154514: a re-placed desk lost its decor): the group's decor goes to the re-placed
    # pieces (handover.hand_over: the same type nearest to each); the rest is dropped as before
    from wenart.furniture import handover as HO

    decor = list(b.get("decor") or [])
    handed = HO.hand_over(decor, [copy.deepcopy(f) for f in items],
                          [f for f in b["furniture"] if f["id"] in set(new_ids)])
    b["decor"] = [d for d in decor if d.get("host_id") not in ids or id(d) in handed]
    return ids + new_ids


def _retype(b: dict, args: dict, catalog=None) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    p = placer.drawn_piece(item)
    allowed = GC.allowed_types_at(b, room, p.center) - {"unknown"}
    size = (float(item["footprint"]["size"][0]), float(item["footprint"]["size"][1]))
    turned = item.get("front_deg") is not None
    candidates = sorted(t for t in allowed if t in PL._size_table() and PL._fits(t, size) and not (
        turned and PL.oriented_fit(t, p.size)["turned"]))
    if args["type"] not in candidates:
        raise EditRejected("retype", f"{args['type']} is no candidate for {item['id']} ({p.size[0]:.2f} x "
                                     f"{p.size[1]:.2f} m at [{p.center[0]:.2f}, {p.center[1]:.2f}]): the size table and "
                                     f"the room / zone give {', '.join(candidates) or 'none'}")
    confirm = item["type"] == args["type"] and item.get("status") == "unverified"
    changed = _change_type(b, args)
    if not confirm:                  # integration after P5: a confirmed piece keeps its fitted asset
        _build_retyped(b, _piece(b, item["id"]), args, catalog)
    return changed


def licence_mode_of(b: dict) -> str:
    """The licence mode of a building: ``project.licence_mode`` (written by the fit stage), else the catalogue's
    default (env ``WENART_LICENCE_MODE`` > ``commercial``)."""
    from wenart.furniture import catalog as C

    project = b.get("project") if isinstance(b.get("project"), dict) else {}
    mode = project.get("licence_mode")
    return str(mode) if mode in C.LICENCE_MODES else C.licence_mode()


def stamp_style_family(b: dict, style) -> Optional[str]:
    """27 Oct 2026 (pod run 091638, real06: the agent swapped a classic sofa into a scandinavian house because its
    working building, fitted before style.json existed, named no family, so ``off_style_refusal`` had none to check):
    writes ``project.style_family`` (and ``style_family_source``) of the project's ``style.json`` profile
    (``fit.style_family_of``) on a building that has none; returns the building's family (None: no profile family)."""
    project = b.get("project") if isinstance(b.get("project"), dict) else None
    if project is None:
        return None
    if project.get("style_family"):
        return str(project["style_family"])
    from wenart.furniture.fit import style_family_of
    try:
        family, how = style_family_of(style) if style else (None, "")
    except Exception:  # noqa: BLE001 - no family (no style filter), as before
        return None
    if family:
        project["style_family"] = str(family)
        project["style_family_source"] = f"style.json ({how})"
    return family


def _style_family_of(b: dict) -> Optional[str]:
    """The style family the fit used on this building: ``project.style_family`` (``stamp_style_family``, the
    project's style.json), else the most common ``asset.style_family`` of its fitted pieces, else the family of the
    brief's style text (``project.brief``; integration after P5); None without any (no style filter)."""
    project = b.get("project") if isinstance(b.get("project"), dict) else {}
    if project.get("style_family"):
        return str(project["style_family"])
    counts: dict = {}
    for f in b.get("furniture") or []:
        asset = f.get("asset") if isinstance(f.get("asset"), dict) else {}
        fam = asset.get("style_family")
        if fam:
            counts[str(fam)] = counts.get(str(fam), 0) + 1
    if counts:
        return max(sorted(counts), key=lambda k: counts[k])
    # Integration of the fix round after P5 (A_agent's ask): the working building's first fit has no style family
    # (P5: None, the refit used "modern" from style.json); the family of the brief's style text is the one the style
    # stage writes to style.json (real02 / real03 / real04: "modern" both ways)
    brief = project.get("brief") if isinstance(project.get("brief"), dict) else None
    try:
        from wenart.furniture.fit import style_family_of
        from wenart.style import profile as SPF
        if not SPF.style_texts(brief):
            return None
        return style_family_of(SPF.profiles_from_brief(brief))[0]
    except Exception:  # noqa: BLE001 - no family (no style filter), as before
        return None


def _build_retyped(b: dict, item: dict, args: dict, catalog=None) -> dict:
    """Milestone 13 (B2): the retyped piece is fitted again (``fit.fit_piece``, the ladder) in the project's licence
    mode and built: ``asset`` set, ``status`` verified, ``build`` true, no ``needs_review`` entry; the fit's method
    and mode are recorded under ``adjusted_by_ai.retype``. Returns the asset.

    Fix round after P3 (16-17 Oct 2026; G_geometry's ask). What: a kitchen counter or island is refitted with the
    hints of the drawn sink and stoves inside it (``fit.kitchen_built_ins``), as ``fit.fit_building`` fits it; a
    sink whose run's fitted plan already builds it (``fit.holds_built_in``) gets the built-in asset
    (``fit.built_in_fit``). Why: without the hints an agent refit of a run dropped its sink unit and stove gap until
    the stage-12 refit (the sink then stood buried in the run, S2). How: the hints go on a copy of the piece and into
    ``asset.module_hints``; the building piece never gets ``module_hints``."""
    from wenart.furniture import fit as F

    if catalog is None:
        from wenart.furniture import catalog as C
        catalog = C.load()
    mode = licence_mode_of(b)
    family = _style_family_of(b)
    trial = dict(item, build=True)
    trial.pop("asset_pin", None)
    kitchen = F.kitchen_built_ins(b)
    hints = kitchen["hints"].get(item["id"])
    host_id = kitchen["sinks"].get(item["id"])
    host = next((p for p in b.get("furniture") or [] if p.get("id") == host_id), None) if host_id else None
    try:
        if host is not None and F.holds_built_in(host, item["id"]):
            asset = F.built_in_fit(trial, host, mode, family)
        else:
            target = dict(trial, module_hints={**(trial.get("module_hints") or {}), **hints}) if hints else trial
            target = dict(target, **F.use_context(b, item))     # bathroom sense of 26 Oct 2026: a child's room
            # fix round after P6a: the piece's room under a sloped ceiling, as fit_building fits it
            asset = F.fit_piece(target, catalog, mode=mode, style_family=family, ceiling=F.piece_ceiling(b, item))
            if hints and asset.get("method") == F.MODULE_METHOD:
                asset["module_hints"] = copy.deepcopy(hints)
    except Exception as exc:  # noqa: BLE001 - review (T4): a refit error is a rejected edit with its reason, never a
        # crash of the session or of the replay (``apply_edit`` turns only EditRejected into a rejection)
        raise EditRejected("refit", f"{item['id']}: the refit as {item['type']} failed ({type(exc).__name__}: "
                                    f"{str(exc)[:160]}); the piece stays as it was") from exc
    if asset.get("method") in (None, F.NOT_BUILT_METHOD):
        # review (T4): the ladder builds a ``build: true`` piece (module or parametric at worst); a ``none`` answer
        # would leave the retyped piece as an unbuilt box, which a retype must never do
        raise EditRejected("refit", f"{item['id']}: the fit built nothing for {item['type']} "
                                    f"({(asset.get('library_gap') or {}).get('reason') or 'no model, no builder'})")
    item["asset"] = asset
    # round 2: a module plan with a split (a drawn table footprint that includes its chairs) labels the piece
    # ``adjusted_by_ai`` with the ``drawn_*`` keys, as ``fit_building`` does (``fit_piece`` is pure)
    F.apply_split_label(item, asset)
    if asset.get("library_gap"):
        item["library_gap"] = dict(asset["library_gap"])
    else:
        item.pop("library_gap", None)
    item["status"] = "verified"
    item.pop("build", None)                      # built (the default); a retype never leaves a box unbuilt
    if item.get("type_method") in (None, "none"):
        item["type_method"] = "inferred"
    b["needs_review"] = [n for n in b.get("needs_review") or [] if n.get("id") != item["id"]]
    adj = item.get("adjusted_by_ai") if isinstance(item.get("adjusted_by_ai"), dict) else {}
    adj["retype"] = {"to": item["type"], "built": True, "method": asset.get("method"), "asset_id": asset.get("asset_id"),
                     "licence_mode": mode, "ladder_step": (item.get("library_gap") or {}).get("step") or "library"}
    item["adjusted_by_ai"] = adj
    return asset


SYMBOL_KINDS = ("level_mark", "room_number", "north_arrow", "axis_bubble", "section_mark", "door_arc",
                "dimension_outline", "text_frame", "other")


def fixed_mark_refusal(building: dict, item: dict) -> Optional[str]:
    """Round 4: why a drawn piece of a fixed type may not be marked as not furniture (CLAUDE.md furniture rules:
    fixed equipment is treated like walls; the AI fixes only a clear drawing or reading error), else None. Fixed
    equipment in a room that never holds it (``schemas.misplaced_fixed``) is such an error and may be marked."""
    if not _fixed(item):
        return None
    room = next((r for r in building.get("rooms") or [] if r.get("id") == item.get("room_id")), None) or {}
    if schemas.misplaced_fixed(item["type"], room.get("room_type")):
        return None
    return (f"{item['id']}: drawn fixed equipment ({item['type']}) is treated like walls and is never marked as not "
            f"furniture (fix_fixture fixes a misread size or a piece through a wall or in a door swing)")


# Fix round after P4a (module docstring): mark_not_furniture is a reading-error tool.
MARK_LOCK_METHODS: tuple[str, ...] = ("block_name", "block", "rule", "twin", "level", "group_member",
                                      "same_block",       # 26 Oct 2026: a copy of a typed block (infer)
                                      "name_text",        # 26 Oct 2026: named by a text of the plan (names)
                                      "zone_label")       # 26 Oct 2026: the anchor a zone label names (infer)
READING_CHECKS: tuple[str, ...] = ("NR", "RC")       # the critic's reading findings (wenart.agent.critic_code)
NEEDS_REVIEW_CHECK_ID = "NR"                         # fix round after P5: NR keeps its way out of the lock
DUPLICATE_SHARE = 0.5            # a drawn piece this much inside a built drawn piece of its type is a duplicate outline
# Fix round after P4b (module docstring): a drawn piece this much inside a larger built drawn piece of the same family
# is a duplicate outline too (real02: the 1.30 m "sofa" f_L-1_061, 84 % inside the corner sofa f_L-1_053). The tucked
# pairs (a chair under its table) and the members of a bed block (a nightstand) are of other families.
DUPLICATE_FAMILIES: tuple[tuple[str, ...], ...] = (
    ("sofa", "sofa_corner", "armchair", "chaise"),
    ("wardrobe", "tall_cabinet", "display_cabinet", "dresser", "sideboard", "bookshelf", "shoe_cabinet"),
    ("bed_single", "bed_double", "bunk_bed", "crib"),
)
IMAGE_PATH = re.compile(r"[^\s'\"()\[\],;:]+\.(?:png|jpe?g|webp)\b", re.I)
# Fix round after P4b: a plan crop is the reading's crop of a drawn symbol (``recognition/crops/<key>_ctx.png`` or
# ``_iso.png``) or a camera's plan crop (``check/<cam>_plan.png``); the agent's own images (``r1_044_topdown_...``,
# ``r1_140_rotate_piece_before_...``) are renders of the 3D layout, never the plan.
PLAN_CROP = re.compile(r"(?:^|/)(?:crops/[^/]+_(?:ctx|iso)\.png|[^/]+_plan\.(?:png|jpe?g|webp))$", re.I)
AGENT_IMAGE = re.compile(r"(?:^r\d+_|topdown)", re.I)
# Pass before P5 (module docstring): a recognition crop of a question (recognition.crops: ``<key>_ctx.png``,
# ``<key>_iso.png``, or ``<key>.png`` for a single crop) in a ``crops/`` folder; group 1 is its file name.
RECOGNITION_CROP = re.compile(r"(?:^|/)crops/([^/]+\.png)$")
QUESTION_CROPS: tuple[str, ...] = ("{key}_ctx.png", "{key}_iso.png", "{key}.png")


def plan_crop_of(evidence: str) -> Optional[str]:
    """Fix round after P4b: the first plan crop (``PLAN_CROP``) named in an evidence text, else None."""
    return next((m.group(0) for m in IMAGE_PATH.finditer(str(evidence or "")) if PLAN_CROP.search(m.group(0))), None)


def own_crops(building: dict, item: dict) -> set[str]:
    """Pass before P5 (module docstring): the file names of the recognition crops of ``item`` itself: the crops of
    its own question (each evidence entry ``recognition:<key>``, ``QUESTION_CROPS``) and a recognition crop
    (``RECOGNITION_CROP``) recorded for its id in ``needs_review`` or ``conflicts``. Never a room's or camera's plan
    crop (``check/<cam>_plan.jpg``) and never another symbol's crop. Empty when the piece has none (real04: 70 of
    the 72 drawn pieces under the mark lock)."""
    names: set[str] = set()
    for e in item.get("evidence") or []:
        entity = str(e.get("entity") or "") if isinstance(e, dict) else ""
        key = entity.split(":", 1)[1].strip() if entity.startswith("recognition:") else ""
        if key and "/" not in key:
            names.update(pattern.format(key=key) for pattern in QUESTION_CROPS)
    pid = item.get("id")
    records = [n for n in building.get("needs_review") or [] if isinstance(n, dict) and n.get("id") == pid]
    records += [c for c in building.get("conflicts") or []
                if isinstance(c, dict) and pid in (c.get("element_ids") or [])]
    for rec in records:
        m = RECOGNITION_CROP.search(str(rec.get("crop") or ""))
        if m:
            names.add(m.group(1))
    return names


def own_crop_named(building: dict, item: dict, evidence: Optional[str]) -> Optional[str]:
    """Pass before P5 (module docstring): the first image path in ``evidence`` that is one of ``item``'s own
    recognition crops (``own_crops``: a ``crops/<file>`` path whose file name is the piece's), as written; else
    None (a room's or camera's plan crop, another symbol's crop, a top-down render, no image)."""
    names = own_crops(building, item)
    if not names:
        return None
    for m in IMAGE_PATH.finditer(str(evidence or "")):
        crop = RECOGNITION_CROP.search(m.group(0))
        if crop and crop.group(1) in names:
            return m.group(0)
    return None


def recorded_crop(building: dict, item: dict) -> Optional[str]:
    """Fix round after P5: the recognition crop path recorded for ``item`` in ``needs_review`` or ``conflicts``
    (``RECOGNITION_CROP``), else None."""
    pid = item.get("id")
    records = [n for n in building.get("needs_review") or [] if isinstance(n, dict) and n.get("id") == pid]
    records += [c for c in building.get("conflicts") or [] if isinstance(c, dict)
                and pid in (c.get("element_ids") or [])]
    for rec in records:
        crop = str(rec.get("crop") or "")
        if RECOGNITION_CROP.search(crop):
            return crop
    return None


def crop_of(evidence: str) -> Optional[str]:
    """Fix round after P4a: the image path an evidence text names as the plan crop (``recognition/crops/sym_L1_003_
    ctx.png: ...``), else None. Fix round after P4b: a plan crop first (``plan_crop_of``), else the first image that
    is not one of the agent's own renders (``AGENT_IMAGE``: a ``topdown`` image, a round-prefixed ``r1_...`` image);
    a top-down render is never recorded as the plan crop (its text stays in the evidence)."""
    found = plan_crop_of(evidence)
    if found is not None:
        return found
    for m in IMAGE_PATH.finditer(str(evidence or "")):
        if not AGENT_IMAGE.search(m.group(0).rsplit("/", 1)[-1]):
            return m.group(0)
    return None


def _in_range(ftype: str, size) -> bool:
    rng = PL.size_range(ftype)
    if rng is None:
        return False
    w, d = (float(v) for v in size)
    (w0, w1), (d0, d1) = rng
    return (w0 - 1e-9 <= w <= w1 + 1e-9 and d0 - 1e-9 <= d <= d1 + 1e-9) or \
        (w0 - 1e-9 <= d <= w1 + 1e-9 and d0 - 1e-9 <= w <= d1 + 1e-9)


def _family(ftype: Optional[str]) -> tuple[str, ...]:
    """The duplicate family of a type (``DUPLICATE_FAMILIES``), else the type alone."""
    return next((fam for fam in DUPLICATE_FAMILIES if ftype in fam), (str(ftype),))


def _host_share(building: dict, item: dict, same_type: bool) -> Optional[str]:
    """The id of the first built drawn piece of ``item``'s room that holds at least ``DUPLICATE_SHARE`` of its
    footprint: of the same type (``same_type``; the host's own outline, an L sofa's L) or of another type of its
    family (``DUPLICATE_FAMILIES``, at least as large; the host's footprint box), else None."""
    try:
        poly = placer.drawn_piece(item).polygon()
    except (KeyError, TypeError, ValueError):
        return None
    if poly.area <= 0:
        return None
    family = _family(item.get("type"))
    for other in building.get("furniture") or []:
        if other is item or other.get("id") == item.get("id"):
            continue
        if (other.get("type") == item.get("type")) != same_type or other.get("type") not in family:
            continue
        if other.get("room_id") != item.get("room_id") or not _drawn(other) or not GR.piece_is_built(other):
            continue
        try:
            hp = placer.drawn_piece(other)
            host = hp.polygon() if same_type else dataclasses.replace(hp, shape=None).polygon()
        except (KeyError, TypeError, ValueError):
            continue
        if not same_type and host.area < poly.area - 1e-9:
            continue                        # another type of the family: only the larger outline holds a duplicate
        if poly.intersection(host).area / poly.area >= DUPLICATE_SHARE - 1e-9:
            return str(other["id"])
    return None


def family_host_of(building: dict, item: dict) -> Optional[str]:
    """Fix round after P4b (module docstring): the id of a larger built drawn piece of another type of ``item``'s
    family (``DUPLICATE_FAMILIES``) whose footprint box holds at least ``DUPLICATE_SHARE`` of ``item``: real02's
    1.30 m "sofa" f_L-1_061 drawn 84 % inside the corner sofa f_L-1_053 (the seat segment of its block), and its twin
    f_L-1_062 in front of the twin L f_L-1_054, whose front the reading lost. Else None."""
    return _host_share(building, item, same_type=False)


def _duplicate_of(building: dict, item: dict) -> Optional[str]:
    """The id of a built drawn piece of the same type that holds at least ``DUPLICATE_SHARE`` of ``item``'s footprint
    (a duplicate outline: real04's wardrobe f_L0_038 inside the storage run f_L0_026) or, fix round after P4b, the
    family host of ``family_host_of``, else None."""
    return _host_share(building, item, same_type=True) or family_host_of(building, item)


def mark_lock_refusal(building: dict, item: dict, target: Optional[dict] = None,
                      evidence: Optional[str] = None) -> Optional[str]:
    """Fix round after P4a (module docstring): why a drawn piece may not be marked as not furniture although it is
    no fixed equipment (``fixed_mark_refusal`` covers that), else None. ``target``: the edit's ``target_finding``
    (a dict or a list of dicts with ``check``); ``evidence`` (fix round after P4b): the edit's evidence text, which
    lifts the lock when it names a plan crop; pass before P5: only a crop of the piece itself (``own_crop_named``),
    never a room's or camera's plan crop or another symbol's crop."""
    if not _drawn(item) or _fixed(item) or item.get("build") is False or item.get("type") in (None, "unknown"):
        return None
    method = item.get("type_method")
    if method not in MARK_LOCK_METHODS:
        return None
    if not any(isinstance(e, dict) and e.get("method") == "vector" for e in item.get("evidence") or []):
        return None
    drawn = (item.get("drawn_footprint") or item.get("footprint") or {}).get("size")
    size = (item.get("footprint") or {}).get("size")
    # a real size: as drawn (the size table, +15 %) or as the fit snapped it (P4a: the coffee table f_L1_021 drawn
    # 1.52 x 0.60 m, snapped to 1.20 x 0.70 m; the wardrobe f_L-1_024 drawn 0.74 m deep, snapped to 0.60 m)
    if not size or not drawn or not (PL._fits(item["type"], drawn) or _in_range(item["type"], size)):
        return None
    targets = target if isinstance(target, list) else [target] if isinstance(target, dict) else []
    checks = {t.get("check") for t in targets if isinstance(t, dict)}
    if NEEDS_REVIEW_CHECK_ID in checks:
        return None
    # Fix round after P5 (module docstring): when the AI passes typed it as furniture too, the doubt is which
    # furniture: an RC finding or the type_disagreement conflict no longer lifts the lock (retype_piece fixes it)
    dispute = ai_furniture_dispute(building, item)
    if dispute is None and checks & set(READING_CHECKS):
        return None
    if any(n.get("id") == item["id"] for n in building.get("needs_review") or [] if isinstance(n, dict)):
        return None
    if dispute is None and any(c.get("kind") == "type_disagreement" and item["id"] in (c.get("element_ids") or [])
                               for c in building.get("conflicts") or [] if isinstance(c, dict)):
        return None
    if _duplicate_of(building, item) is not None:
        return None
    if own_crop_named(building, item, evidence) is not None:
        return None                     # pass before P5: the piece's own plan crop is the evidence CLAUDE.md asks for
    w, d = (float(v) for v in size)
    if dispute is not None:
        return (f"{item['id']}: a drawn {item['type']} typed from the drawing ({method}, vector evidence) at a real "
                f"size ({w:.2f} x {d:.2f} m) that the AI passes typed {dispute}: both read it as furniture, so the doubt is "
                f"which piece it is: retype_piece fixes that; mark_not_furniture needs evidence that names its own "
                f"recognition crop, when it has one")
    return (f"{item['id']}: a drawn {item['type']} typed from the drawing ({method}, vector evidence) at a real size "
            f"({w:.2f} x {d:.2f} m) is furniture: mark_not_furniture is for reading errors (an NR or RC finding, a "
            f"duplicate outline, evidence that names its own recognition crop, when it has one); a wall cut is "
            f"fixed by move_piece / the wall snap, a wrong room type by retype_piece")


AI_TYPED_IT = re.compile(r"the AI passes typed it ([a-z_]+)")


def ai_furniture_dispute(building: dict, item: dict) -> Optional[str]:
    """Fix round after P5 (module docstring): the furniture type the AI passes named for ``item`` in a
    ``type_disagreement`` conflict the drawing won (``reading.log_overrides``: "<id>: the AI passes typed it bench;
    ..."), when it is a furniture type (``schemas.SIZE_OPTIONS``); else None (no conflict, or the passes said
    unknown or not furniture, or a conflict that names no AI type)."""
    for c in building.get("conflicts") or []:
        if not isinstance(c, dict) or c.get("kind") != "type_disagreement" or \
                item.get("id") not in (c.get("element_ids") or []):
            continue
        m = AI_TYPED_IT.search(str(c.get("description") or ""))
        if m and m.group(1) in schemas.SIZE_OPTIONS:
            return m.group(1)
    return None


def _mark_not_furniture(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    if not _drawn(item):
        raise EditRejected("drawn_only", f"{item['id']} is {item.get('source')}: only a drawn piece can be a misread "
                                         f"symbol (remove_piece removes an added one)")
    # Round 4 (CPU pre-flight of 16 Oct 2026: 5 real03 toilets marked, 5 bathrooms left without a toilet)
    refusal = fixed_mark_refusal(b, item)
    if refusal is not None:
        raise EditRejected("drawn_lock", refusal)
    # Fix round after P4a (module docstring): never a drawn, code-typed piece of a real size for a placement finding
    refusal = mark_lock_refusal(b, item, args.get("target_finding"), str(args.get("evidence") or ""))
    if refusal is not None:
        raise EditRejected("drawn_lock", refusal)
    if any(s.get("former_piece_id") == item["id"] for s in b.get("symbols") or []):
        raise EditRejected("no_change", f"{item['id']} is marked as not furniture already")
    evidence = str(args["evidence"])
    untyped = item.get("type") in (None, "unknown")
    # fix rounds after P4a / P4b: a plan crop anywhere, never a top-down render; pass before P5: the piece's own crop
    # first, when the evidence names it; fix round after P5: else the crop recorded for the piece; fix round after
    # P6a: an untyped piece only with its own crop (never crop_of's first image: a whole sheet, a room's or camera's
    # plan crop, another symbol's crop)
    if untyped:
        crop = own_crop_named(b, item, evidence) or recorded_crop(b, item)
    else:
        crop = own_crop_named(b, item, evidence) or crop_of(evidence) or recorded_crop(b, item)
    if crop is None and untyped:
        # Fix round after P5 (module docstring; P5 seq 5388: the 5.14 x 2.37 m cluster f_L-1b_001 marked with "plan
        # crop of r_L-1b_salon_2" and no image): CLAUDE.md removes a drawn piece only with the plan crop as evidence.
        # Fix round after P6a (P6a seq 5968: f_L-1b_002 marked with the whole sheet final/debug/deneme1_dwg_s1.jpg)
        named = crop_of(evidence)
        raise EditRejected("no_crop", f"{item['id']} is an untyped drawn piece: it is marked as not furniture only "
                                      f"with its own recognition crop (the crop of its own question, or the one its "
                                      f"review entry records)"
                                      + (f"; {named} is not its crop (a whole sheet, a room's or camera's plan crop "
                                         f"or another symbol's crop shows no reading of this piece)" if named else "")
                                      + ("; it has none, so it stays listed for review" if not own_crops(b, item)
                                         else "")
                                      + "; CLAUDE.md removes a drawn piece only with its plan crop")
    before = copy.deepcopy(item)
    item["build"] = False
    _label(item, before, args, ["build"])
    item["adjusted_by_ai"]["not_furniture"] = args["kind"]
    pattern = re.compile(rf"^sym_{re.escape(item['level_id'])}_(\d+)$")
    number = max((int(m.group(1)) for s in b.get("symbols") or [] for m in [pattern.match(str(s.get("id")))] if m),
                 default=0) + 1
    ev = {"file": crop or EVIDENCE_FILE, "method": "ai", "confidence": 0.8, "text": f"{args['kind']}: {evidence}"}
    if args.get("model"):
        ev["model"] = args["model"]
    b.setdefault("symbols", []).append({
        "id": f"sym_{item['level_id']}_{number:03d}", "kind": args["kind"], "level_id": item["level_id"],
        "room_id": item.get("room_id"), "footprint": copy.deepcopy(item["footprint"]), "former_piece_id": item["id"],
        "reason": str(args.get("reason") or ""), "crop": crop, "evidence": [ev]})
    b["decor"] = [d for d in b.get("decor") or [] if d.get("host_id") != item["id"]]
    # The piece is now recorded as not furniture (the symbol above, with its evidence), so it leaves the review list,
    # as a retyped piece does (``_retype``). Without this the critic's NR finding stayed after the edit and the dry
    # re-check refused every mark_not_furniture on an untyped piece (CPU pre-flight of 16 Oct 2026, real04: the 20
    # NR findings could not be closed this way).
    b["needs_review"] = [n for n in b.get("needs_review") or [] if n.get("id") != item["id"]]
    return [item["id"]]


FIXTURE_OFF_RANGE = 0.30         # U1: a fixed piece's drawn size more than 30 % outside its type's real range
FIXTURE_MOVE_M = 0.50            # U1: a fixed piece through a wall or in a door swing moves at most this far


def fixture_problems(building: dict, item: dict) -> dict:
    """U1 (docs/milestone12.md §4.1) of a drawn fixed piece: ``{"size": {...} | None, "place": {...} | None}``;
    size: ``{"drawn", "range", "off", "product"}`` when a side is more than ``FIXTURE_OFF_RANGE`` outside its real
    range (``product``: the nearest real size); place: ``{"outside_m2", "door"}`` when it stands through a wall
    (more than 0.01 m² outside the room) or in a door's approach or swing."""
    out: dict = {"size": None, "place": None}
    rng = PL.size_range(item["type"])
    p = placer.drawn_piece(item)
    if rng is not None:
        offs, product = [], []
        for v, (lo, hi) in zip(p.size, rng):
            off = (lo - v) / lo if v < lo else (v - hi) / hi if v > hi else 0.0
            offs.append(off)
            product.append(min(max(v, lo), hi))
        if max(offs) > FIXTURE_OFF_RANGE + 1e-9:
            out["size"] = {"drawn": [round(v, 3) for v in p.size], "range": [list(r) for r in rng],
                           "off": round(max(offs), 3), "product": [round(v, 3) for v in product]}
    room = next((r for r in building.get("rooms") or [] if r.get("id") == item.get("room_id")), None)
    if room is not None:
        out["place"] = _place_problem(building, room, p)
    return out


def _place_problem(building: dict, room: dict, p: placer.Piece) -> Optional[dict]:
    ctx = placer.room_context(building, room)
    poly = p.polygon()
    outside = poly.difference(ctx.polygon).area
    door = next((d.id for d in ctx.doors for z in (d.zone, d.swing) if z is not None and not z.is_empty
                 and poly.intersection(z).area > placer.AREA_EPS), None)
    if outside > 0.01 or door:
        return {"outside_m2": round(outside, 3), "door": door}
    return None


def _fix_fixture(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    room = _room(b, item.get("room_id"))
    if not _fixed(item):
        raise EditRejected("fixture", f"{item['id']} is a {item['type']} ({item.get('source')}): fix_fixture is for "
                                      f"drawn fixed equipment (stairs, kitchen runs, sanitary ware)")
    probs = fixture_problems(b, item)
    before = copy.deepcopy(item)
    p = placer.drawn_piece(item)
    size = p.size
    resized = False
    # Fix round after P5 (module docstring; user decision of 22 Oct 2026): a bath or shower a few cm longer than its
    # bay is a misread size: the nearest real product that fits the clear bay (reading.bay_fit)
    bay = _bay_fix(b, room, item) if probs["size"] is None else None
    if bay is not None and (args.get("size") is None or all(
            abs(float(u) - float(v)) <= 0.005 for u, v in zip(args["size"], bay["size"]))) \
            and args.get("center") is None:
        _set_footprint(item, bay["footprint"]["center"], float(bay["footprint"]["rotation_deg"]), bay["size"],
                       item.get("front_deg"))
        _label(item, before, args, ["footprint"])
        item["adjusted_by_ai"]["fix_fixture"] = {"resized": True, "moved_m": round(G.distance(
            tuple(bay["footprint"]["center"]), p.center), 3), "size": None, "place": probs["place"],
            "bay": {"overrun_m": bay["overrun"]["overrun_m"], "clear": list(bay["overrun"]["clear"]),
                    "reason": bay["reason"]}}
        return [item["id"]]
    if args.get("size") is not None or probs["size"]:
        if probs["size"] is None:
            rng = PL.size_range(item["type"])
            raise EditRejected("fixture_size", f"{item['id']}: the drawn {p.size[0]:.2f} x {p.size[1]:.2f} m is within "
                                               f"{int(FIXTURE_OFF_RANGE * 100)} % of the real {item['type']} range "
                                               f"({_fmt_range(rng)}): its size stays as drawn")
        size = tuple(float(v) for v in (args.get("size") or probs["size"]["product"]))
        rng = PL.size_range(item["type"])
        if any(not (lo / 1.05 - 1e-9 <= v <= hi * 1.05 + 1e-9) for v, (lo, hi) in zip(size, rng)):
            raise EditRejected("product_size", f"{item['id']}: {size[0]:.2f} x {size[1]:.2f} m is not a real "
                                               f"{item['type']} size ({_fmt_range(rng)})")
        resized = True
    center = p.center
    if resized:
        anchor = LK.anchor_of(item, b)
        if anchor["kind"] == "back_edge":            # grows or shrinks from its wall line
            center = placer.anchored_center(anchor, p.rotation_deg, size)
    moved = 0.0
    place = _place_problem(b, room, placer.Piece(p.type, center, p.rotation_deg, size, False))
    if args.get("center") is not None:
        target = (float(args["center"][0]), float(args["center"][1]))
        moved = G.distance(target, p.center)
        if place is None and probs["place"] is None:
            raise EditRejected("fixture_place", f"{item['id']} stands inside the room and off every door: it is "
                                                f"not moved")
        if moved > FIXTURE_MOVE_M + 1e-6:
            raise EditRejected("fixture_move", f"{item['id']}: the move is {moved:.2f} m, at most "
                                               f"{FIXTURE_MOVE_M:.2f} m")
        center = target
        if _place_problem(b, room, placer.Piece(p.type, center, p.rotation_deg, size, False)) is not None:
            # Fix round after P5 (the P4b finding's text): never send the model back to a search that found nothing
            raise EditRejected("fixture_place", f"{item['id']} at [{center[0]:.2f}, {center[1]:.2f}] is still through "
                                                f"a wall or in a door swing; without center the code searches every "
                                                f"spot within {FIXTURE_MOVE_M:.2f} m: when that search found no valid "
                                                f"spot, none exists, do not try centres; the finding stays for review")
    elif place is not None:
        spot = _nearest_valid(b, room, item, placer.Piece(p.type, center, p.rotation_deg, size, False))
        if spot is None:
            raise EditRejected("fixture_place", f"{item['id']}: no valid spot within {FIXTURE_MOVE_M:.2f} m (it "
                                                f"stands {place['outside_m2']:.2f} m² outside the room"
                                                + (f", in door {place['door']}" if place["door"] else "") + ")")
        center = spot
        moved = G.distance(center, p.center)
    if not resized and moved < 1e-6:
        raise EditRejected("no_change", f"{item['id']}: nothing to fix (size within the real range, inside the room "
                                        f"and off the doors)")
    _set_footprint(item, center, p.rotation_deg, size, item.get("front_deg"))
    _label(item, before, args, ["footprint"])
    item["adjusted_by_ai"]["fix_fixture"] = {"resized": resized, "moved_m": round(moved, 3),
                                             "size": probs["size"], "place": probs["place"] or place}
    return [item["id"]]


def _bay_fix(b: dict, room: dict, item: dict) -> Optional[dict]:
    """Fix round after P5: ``reading.bay_fit`` of a drawn bathtub or shower in its room's outline, else None."""
    from shapely.geometry import Polygon

    from wenart.ingest.generic import reading as RD

    if item.get("type") not in RD.BAY_TYPES or len(room.get("polygon") or []) < 3:
        return None
    poly = Polygon(room["polygon"])
    return RD.bay_fit(item, poly if poly.is_valid else poly.buffer(0))


def _fmt_range(rng) -> str:
    if rng is None:
        return "no size table entry"
    (w0, w1), (d0, d1) = rng
    return f"width {w0:.2f}-{w1:.2f} m, depth {d0:.2f}-{d1:.2f} m"


def _nearest_valid(b: dict, room: dict, item: dict, p: placer.Piece) -> Optional[tuple[float, float]]:
    """The nearest centre within ``FIXTURE_MOVE_M`` (0.05 m grid, nearest first) where the piece stands inside the
    room, off the doors and off the other built pieces."""
    others = [placer.drawn_piece(f).polygon() for f in _floor_items(b, room["id"]) if f["id"] != item["id"]
              and GR.piece_is_built(f)]
    step = 0.05
    n = int(FIXTURE_MOVE_M / step)
    offsets = sorted(((i * step, j * step) for i in range(-n, n + 1) for j in range(-n, n + 1)
                      if math.hypot(i * step, j * step) <= FIXTURE_MOVE_M + 1e-9 and (i or j)),
                     key=lambda o: (round(math.hypot(*o), 6), o))
    for dx, dy in offsets:
        c = (p.center[0] + dx, p.center[1] + dy)
        q = placer.Piece(p.type, c, p.rotation_deg, p.size, False)
        if _place_problem(b, room, q) is not None:
            continue
        poly = q.polygon()
        if any(poly.intersection(o).area > placer.AREA_EPS for o in others):
            continue
        return (round(c[0], 4), round(c[1], 4))
    return None


def _set_front(b: dict, args: dict) -> list[str]:
    item = _piece(b, args["piece_id"])
    if item.get("front_deg") is not None:
        raise EditRejected("has_front", f"{item['id']} faces {float(item['front_deg']):.0f}° already: rotate_piece "
                                        f"turns it")
    front = float(args["front_deg"]) % 360.0
    rot = float(item["footprint"]["rotation_deg"])
    sides = sorted({round(G.normalise_angle(rot + 270.0 + 90.0 * k), 3) for k in range(4)})
    near = min(sides, key=lambda s: G.angle_difference_deg(s, front))
    if G.angle_difference_deg(near, front) > 1.0 + 1e-9:
        raise EditRejected("front_side", f"front {front:.1f}° is {G.angle_difference_deg(near, front):.1f}° off the "
                                         f"nearest side of the footprint (needs ≤ 1°): fronts "
                                         f"{', '.join(f'{s:.0f}' for s in sides)}")
    before = copy.deepcopy(item)
    new_rot, size = placer.front_frame(item["footprint"], near)
    _set_footprint(item, item["footprint"]["center"], new_rot, size, near)
    _label(item, before, args, ["footprint", "front_deg"])
    return [item["id"]]


def _relayout_m12(b: dict, args: dict) -> list[str]:
    """``relayout_room``: the room solved again (its added pieces replaced; drawn pieces fixed): solver candidate
    ``candidate`` (1-based, default 1) of the program with the ``choices`` (group id -> option)."""
    from wenart.furniture import program as PR

    room = _room(b, args["room_id"])
    choices = dict(args.get("choices") or {})
    prog = PR.room_program(b, room["id"], choices=choices)
    known = {g["group_id"]: g["options"] for g in prog["groups"]}
    for gid, option in choices.items():
        if gid not in known or option not in known[gid]:
            raise EditRejected("choices", f"{gid}: {option!r} is not an option of the room's program ("
                                          + "; ".join(f"{k}: {'/'.join(v)}" for k, v in known.items()) + ")")
    if not prog["groups"]:
        raise EditRejected("no_change", f"{room['id']}: the program has no groups ({prog['reason']})")
    old = _ai_floor_ids(b, room["id"])
    new = _solve_apply(b, room, prog, args, f"{room['id']} relayout", fixed=[], index=int(args.get("candidate") or 1))
    return old + new


M12_EDITS = {"place_group": _place_group, "complete_group": _complete_group, "move_group": _move_group,
             "retype_piece": _retype, "mark_not_furniture": _mark_not_furniture, "fix_fixture": _fix_fixture,
             "set_front": _set_front}


# --------------------------------------------------------------------------
# apply_edit
# --------------------------------------------------------------------------

def _result(accepted: bool, failed: list[str], before: float, after: float, building, changed: list[str],
            rerun: str, message: str) -> dict:
    return {"accepted": accepted, "failed_checks": list(failed), "score_before": float(before),
            "score_after": float(after), "building": building, "changed_ids": list(changed), "rerun_from": rerun,
            "message": message}


def _room_id_of(b: dict, op: str, args: dict) -> Optional[str]:
    if "room_id" in args:
        return args["room_id"]
    if "group_id" in args:
        return group_room_id(b, args["group_id"])          # a zone's group: the room of the zone
    item = next((f for f in b.get("furniture") or [] if f.get("id") == args.get("piece_id")), None)
    return item.get("room_id") if item else None


def apply_edit(building: dict, edit: dict, *, catalog=None) -> dict:
    """Apply one edit to a copy of ``building`` (see the module docstring); the input is never changed."""
    op, args = normalise_edit(edit if isinstance(edit, dict) else {})
    rerun = "layout" if op in LAYOUT_OPS else "refit"
    if op not in EDIT_SCHEMAS:
        return _result(False, [f"op: unknown edit {op!r} (one of {', '.join(EDIT_OPS)})"], 0.0, 0.0, None, [],
                       rerun, "unknown edit")
    errors = schema_errors(op, args)
    if errors:
        return _result(False, [f"schema: {e}" for e in errors], 0.0, 0.0, None, [], rerun,
                       "the arguments do not match the edit's schema")
    room_id = _room_id_of(building, op, args)
    if room_id is None or not any(r.get("id") == room_id for r in building.get("rooms") or []):
        what = (f"piece {args.get('piece_id')!r}" if "piece_id" in args else
                f"group {args.get('group_id')!r} (its room {room_id!r})" if "group_id" in args else
                f"room {args.get('room_id')!r}")
        return _result(False, [f"exists: no {what} in a room of the building"], 0.0, 0.0, None, [], rerun,
                       "nothing to edit")
    before_score = PL.score_room(building, room_id)
    before_checks = room_checks(building, room_id)
    b = copy.deepcopy(building)
    try:
        if op == "move":
            changed = _move(b, args)
        elif op == "rotate":
            changed = _rotate(b, args)
        elif op == "resize":
            changed = _resize(b, args)
        elif op == "change_type":
            changed = _change_type(b, args)
        elif op == "swap_model":
            changed = _swap_model(b, args, catalog)
        elif op == "add":
            changed = _add(b, args)
        elif op == "add_group":
            changed = _add_group(b, args)
        elif op == "remove":
            changed = _remove(b, args)
        elif op == "relayout_room":
            changed = _relayout_m12(b, args)
        elif op == "set_room_type":
            changed = _set_room_type(b, args)
        elif op == "retype_piece":
            changed = _retype(b, args, catalog)          # Milestone 13: the refit needs the catalogue
        else:
            changed = M12_EDITS[op](b, args)
    except EditRejected as exc:
        return _result(False, [f"{exc.check}: {exc.message}"], before_score["score"], before_score["score"], None, [],
                       rerun, exc.message)
    failed = _new_failures(before_checks, room_checks(b, room_id))
    after_score = PL.score_room(b, room_id)
    if op not in CORRECTION_OPS:
        # fix round after P6b (module docstring): a cut through the room outline that is new or grows is refused,
        # whatever the score nets (P6b seq 2588: the drawn wardrobe 0.28 m through the front outer wall)
        failed += outline_growth(outline_cuts(before_score), outline_cuts(after_score))
    known = {finding_identity(w) for w in before_score["violations"]}
    new = [v for v in after_score["violations"] if finding_identity(v) not in known]
    notes = ""
    if op in GROUP_OPS:
        # A group placed by the solver: no new critical or major finding (the solver's own hard rule). Fix round
        # after P6b (module docstring): an F4 of another group's anchor that names only this edit's new members of
        # other groups is reported, not held against the edit.
        noted = {id(v): why for v in new if (why := other_group_front(b, room_id, v, changed)) is not None}
        bad = [v for v in new if v["severity"] in ("critical", "major") and id(v) not in noted]
        if bad:
            failed.append("group checks: " + "; ".join(f"{v['check']} {v['target']}: {v['message']}" for v in bad[:4]))
        if noted:
            notes = "; noted: " + "; ".join(list(noted.values())[:4])
    elif op in CORRECTION_OPS:
        notes = ("; new findings: " + "; ".join(f"{v['check']} {v['target']}: {v['message']}" for v in new[:4])
                 if new else "")
    # The score must not drop; it is compared before the floor at 0 (``penalty``), so a room far below 0 neither
    # hides a worse edit nor an improvement.
    elif after_score["penalty"] > before_score["penalty"]:
        failed.append(f"score: plausibility {100 - before_score['penalty']} -> {100 - after_score['penalty']} ("
                      + "; ".join(f"{v['check']} {v['target']}: {v['message']}" for v in new[:4]) + ")")
    out = _result(not failed, failed, before_score["score"], after_score["score"], None if failed else b, changed,
                  rerun, (f"{op} rejected: " + "; ".join(failed[:3])) if failed else
                  f"{op} accepted: score {100 - before_score['penalty']} -> {100 - after_score['penalty']}" + notes)
    out["penalty_before"], out["penalty_after"] = before_score["penalty"], after_score["penalty"]
    return out


# Fix round after P6b (module docstring): the F4 message whose trailing list names the pieces in reach
# (``plausibility._f3_f4``: "<type> does not face its group (<ids>)").
F4_GROUP_TEXT = " does not face its group ("


def finding_identity(v: dict) -> tuple[str, str, str]:
    """Fix round after P6b (module docstring): ``(check, target, message)`` of a score violation, the trailing list of
    an F4 "does not face its group (...)" left out: a piece that faced none of its group before and still faces none
    keeps the same finding when the edit adds a piece in its reach (P6a's chair f_L-1b_053 with the new coffee table
    f_L-1b_087 at the end of its list); every other message is compared whole, as before."""
    message = str(v.get("message") or "")
    if v.get("check") == "F4" and F4_GROUP_TEXT in message:
        message = message.split(F4_GROUP_TEXT, 1)[0] + F4_GROUP_TEXT.rstrip(" (")
    return (str(v.get("check")), str(v.get("target")), message)


def other_group_front(b: dict, room_id: str, v: dict, changed: list[str]) -> Optional[str]:
    """Fix round after P6b (module docstring): why a new F4 "does not face its group" after a group edit is reported
    but not held against it, else None. Only when its piece anchors a group of its own in the room
    (``groups.group_members``) and every piece it names (``metrics.targets``) is one this edit added
    (``added_by_ai``, in ``changed``) to a group with another anchor: the new piece is not in the piece's group, so
    the piece's front still faces its own group (CLAUDE.md: "fronts facing their group"); a critical one is held.
    P6a: the coffee table f_L-1b_087 completing the drawn sofa f_L-1b_041's seating group stands 1.7 m from the second
    drawn sofa f_L-1b_045 (inferred, its own group r_L-1b_salon_2.seating.2), within the score's 4.5 m sofa reach."""
    if v.get("check") != "F4" or F4_GROUP_TEXT not in str(v.get("message") or "") or v.get("severity") == "critical":
        return None
    metrics = v.get("metrics") if isinstance(v.get("metrics"), dict) else {}
    targets = [str(t) for t in metrics.get("targets") or []]
    pid = str(v.get("target"))
    if not targets:
        return None
    own = [g for g in GR.group_members(b, room_id) if g.get("anchor_id") == pid]
    if not own:
        return None
    by_id = {f.get("id"): f for f in b.get("furniture") or []}
    homes: list[str] = []
    for t in targets:
        f = by_id.get(t) or {}
        tag = f.get("group") if isinstance(f.get("group"), dict) else {}
        if t not in set(changed) or f.get("source") != "added_by_ai" or not tag.get("group_id") \
                or tag.get("anchor_id") in (None, pid):
            return None
        homes.append(str(tag["group_id"]))
    if {g.get("group_id") for g in own} & set(homes):
        return None
    return (f"F4 {pid} ({v.get('severity') or 'major'}, kept for the next round): it anchors {own[0]['group_id']}; "
            f"{', '.join(targets)} belong{'s' if len(targets) == 1 else ''} to {', '.join(sorted(set(homes)))}")


# Milestone 12 contract (docs/milestone12.md §5.2, §5.3, §13.2; owner: track G).
def dry_run(building: dict, edit: dict, *, catalog=None) -> dict:
    """The validator's answer for ``edit`` without applying it: the ``apply_edit`` result with ``building`` None and
    ``dry_run: true`` (the loop does not count it against the try budget)."""
    res = apply_edit(building, edit, catalog=catalog)
    return dict(res, building=None, dry_run=True)


def allowed_edits(building: dict, piece_id: str) -> dict:
    """Per tool name: ``{"allowed": bool, "why": str, "move_left_m": float | None}`` for one piece (the room brief,
    docs/milestone12.md §5.2): what the validator would allow by the CLAUDE.md locks before any geometry check (an
    allowed edit can still fail its checks; ``dry_run`` tells). ``move_left_m``: how far the piece may still move
    from its drawn place (None: no limit, an added piece; 0: it may not move)."""
    item = next((f for f in building.get("furniture") or [] if f.get("id") == piece_id), None)
    if item is None:
        return {}
    room = next((r for r in building.get("rooms") or [] if r.get("id") == item.get("room_id")), None) or {}
    drawn, fixed = _drawn(item), _fixed(item)
    kept = drawn and bool(room) and kept_room(building, room)
    built = GR.piece_is_built(item)
    misplaced = fixed and schemas.misplaced_fixed(item["type"], room.get("room_type"))
    drawn_center = (item.get("drawn_footprint") or item["footprint"])["center"]
    moved = G.distance(item["footprint"]["center"], drawn_center)
    out: dict = {}

    def put(tool: str, ok: bool, why: str, left: Optional[float] = 0.0) -> None:
        out[tool] = {"allowed": bool(ok), "why": why, "move_left_m": None if left is None else round(max(0.0, left), 3)}

    adj = item.get("adjusted_by_ai") or {}
    limit = schemas.WALL_SNAP_MAX_M if adj.get("snapped_wall") else SNAP_MAX_M
    if not drawn:
        put("move_piece", True, "an added piece moves freely (checks decide)", None)
    elif fixed:
        put("move_piece", False, f"drawn fixed equipment ({item['type']}) never moves; fix_fixture moves it up to "
                                 f"{FIXTURE_MOVE_M} m when it stands through a wall or in a door swing")
    elif kept:
        put("move_piece", False, "the room keeps its drawn pieces: only orientation and clear errors")
    else:
        put("move_piece", moved < limit, f"a drawn piece moves at most {SNAP_MAX_M} m ({schemas.WALL_SNAP_MAX_M} m "
                                         f"when its back snaps onto a wall); moved {moved:.2f} m so far",
            limit - moved)
    if item["type"] in schemas.FRONTLESS_TYPES:
        put("rotate_piece", False, f"a {item['type']} has no front to turn")
    elif fixed:
        r = PL._Room(building, room) if room else None
        problem = _front_problem(r, item["id"]) if r is not None and item["id"] in r.pieces else None
        put("rotate_piece", problem is not None, f"fixed equipment turns only for a clear error: "
                                                 f"{problem or 'none here (its back is on a wall, its front free)'}")
    else:
        put("rotate_piece", True, "orientation may change (checks decide)")
    if fixed:
        put("resize_piece", False, "fixed equipment keeps its drawn size; fix_fixture gives a real product size when the "
                                   "drawn one is more than 30 % off")
    elif kept:
        put("resize_piece", False, "the room keeps its drawn pieces' sizes")
    else:
        put("resize_piece", item["type"] != "unknown", "to a real size of its type (size table)"
            if item["type"] != "unknown" else "an unknown piece is typed first (retype_piece)")
    if fixed and not misplaced:
        retype = (False, f"drawn fixed equipment keeps its type ({item['type']})")
    elif kept and item["type"] != "unknown":
        retype = (False, "the room keeps its drawn pieces' types (an unknown piece may be typed)")
    else:
        retype = (True, "a type of the room / zone that fits the footprint (size table)")
    put("retype_piece", *retype)
    put("change_type", *retype)
    put("swap_model", built, "a catalogue model of its type" if built else "the piece is not built")
    if drawn and fixed and not misplaced:
        put("remove_piece", False, "drawn fixed equipment is never removed (treated like walls; fix_fixture for a "
                                   "misread size or place)")
    elif drawn:
        put("remove_piece", item.get("build") is not False, "a drawn piece is left out (build: false) only with a "
                                                            "reason" if item.get("build") is not False else
            "not built already")
    else:
        put("remove_piece", True, "an added piece may be removed")
    marked = any(s.get("former_piece_id") == item["id"] for s in building.get("symbols") or [])
    refusal = (fixed_mark_refusal(building, item) or mark_lock_refusal(building, item)) if drawn else None
    if refusal is not None:
        put("mark_not_furniture", False, refusal)
    else:
        put("mark_not_furniture", drawn and not marked, (
            "drawn fixed equipment in a room that never holds it (a reading error): it may be marked with its evidence"
            if misplaced else "a drawn piece read from a symbol, mark or line") if drawn and not marked else
            ("marked already" if marked else "only a drawn piece can be a misread symbol"))
    if fixed:
        probs = fixture_problems(building, item)
        fix = probs["size"] is not None or probs["place"] is not None
        why = "; ".join(x for x in (
            f"its size is {probs['size']['off'] * 100:.0f} % outside the real range" if probs["size"] else "",
            (f"it stands {probs['place']['outside_m2']:.2f} m² through a wall" if probs["place"]["outside_m2"] > 0.01
             else f"it stands in door {probs['place']['door']}") if probs["place"] else "") if x)
        put("fix_fixture", fix, why or "its size is real and it stands inside the room, off the doors",
            FIXTURE_MOVE_M - moved if probs["place"] else 0.0)
    else:
        put("fix_fixture", False, "only for drawn fixed equipment")
    put("set_front", item.get("front_deg") is None, "a drawn piece without a front gets one along a side of its "
        "footprint" if item.get("front_deg") is None else f"it faces {float(item['front_deg']):.0f}° already "
                                                          f"(rotate_piece)")
    group = next((g for g in GR.group_members(building, item["room_id"]) if item["id"] == g.get("anchor_id")
                  or item["id"] in (g.get("member_ids") or [])), None) if item.get("room_id") else None
    if group is None:
        put("complete_group", False, "the piece belongs to no group")
        put("move_group", False, "the piece belongs to no group")
    else:
        no_completion = program_refusal(building, _room(building, item["room_id"]), group) \
            if group.get("missing") else None        # fix round after P4b
        if no_completion is not None:
            put("complete_group", False, no_completion)
        else:
            put("complete_group", bool(group.get("missing")), f"{group['group_id']} misses "
                f"{', '.join(group['missing'])}" if group.get("missing") else f"{group['group_id']}: nothing missing")
        members = [f for f in building["furniture"] if f["id"] in [group.get("anchor_id")] + list(group["member_ids"])]
        ai = all(f.get("source") == "added_by_ai" for f in members)
        put("move_group", ai, f"{group['group_id']}: added pieces, moved as one" if ai else
            f"{group['group_id']} holds drawn pieces: they stay where they are drawn", None if ai else 0.0)
    return out
