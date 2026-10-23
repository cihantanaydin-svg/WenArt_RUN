"""The tool API of the agent (docs/milestone11.md §3).

What: ``build_registry()`` returns the ``Registry`` of every tool: name, description, JSON schema of the input,
handler -> JSON output, and the stage an edit touches. Read tools (§3.1) have no side effects; edit tools (§3.2)
are validated by code before they are accepted and every accepted edit becomes one entry of ``overrides.json``.

| kind | tools |
|---|---|
| read | building_summary, room, room_topdown, plan_crop, plausibility, view, exterior_summary, catalog, stage_status |
| furniture edit (``edit_ops.apply_edit``) | move_piece, rotate_piece, resize_piece, change_type, swap_model, add_piece, add_group, remove_piece, relayout_room, set_room_type |
| override edit (``blender.exterior_checks`` validators) | set_camera, add_camera, remove_camera, set_material, set_exterior |
| record-only edit | correct_geometry (``geometry_fix``), rerun_stage (white list) |
| control | finish |

Why: the model writes no code and runs no command; it can only call these tools. A call whose arguments do not
match the schema is refused with the schema error (and counted against the round's budget, §3).

How: the furniture tools take ``EDIT_SCHEMAS[op]`` of track B as their parameters (+ ``reason``), the camera and
exterior tools ``CAMERA_/EXTERIOR_OVERRIDE_SCHEMA`` of track C; while a track's table is still empty (its stub)
the fallback schemas below (from §3.2) are used, so the registry is complete either way. Every edit result is
``{accepted, failed_checks, score_before, score_after, overrides_id, rerun_from, message, changed_ids}`` (§3.2).
A validator that is not built yet (``NotImplementedError``) rejects the edit with ``validator_unavailable``. The
same target is edited at most ``MAX_TRIES`` = 3 times per round (§3.2, §14). Images a read tool makes or finds
are put in ``ctx.pending_images``; the loop shows them to the model in the next message.

Milestone 12 (docs/milestone12.md §5.2–§5.4, D17–D19):

| kind | new tools |
|---|---|
| read | ``room_brief`` (``brief.room_brief``: replaces ``room`` + ``plausibility`` for the planner), ``levels`` (marks, floors, thresholds, ground, terrain, entrances, L-findings) |
| group edit (``edit_ops.apply_edit``, track G) | ``relayout_room`` (with a solver ``candidate``), ``place_group``, ``complete_group``, ``move_group``, ``retype_piece``, ``mark_not_furniture``, ``fix_fixture``, ``set_front`` |
| level edit (``levels.edits.apply_level_edit``, track L) | ``set_mark_kind``, ``set_room_floor``, ``set_ground_point``, ``set_entrance``, ``set_terrain`` |
| record-only | ``report_library_gap`` (into ``agent_overrides.library_gaps``) |
| free | ``dry_run`` (the validator's answer without applying it; no try is counted, nothing is stored) |

Every accepted building edit is followed by ``decor.sync_to_hosts`` (track S: the decor follows its host, B3) and
its result carries the room's group checks after the edit (with their numbers). An edit identical to one rejected
earlier in the same room (``memory.Memory``, any round) is refused before any validator call (``failed_checks``
``memory: ...``). Track G's ops validate every edit; with a validator that lacks them (an older one, a test fake),
``set_front`` / ``retype_piece`` / ``mark_not_furniture`` are
validated as their M11 ops (``overrides.resolve_edit``). The planner is offered ``PLANNER_TOOLS`` (the M12 set);
the M11 tools stay callable for replay and old scripts. The context is shared by the parallel room sessions of one
round: building changes, tries, overrides and the log are guarded by ``ctx.lock``; the images a read tool returns
and ``finish`` belong to the calling session (thread-local).

Milestone 13 (docs/milestone13.md §3.0 K4, §13.2; track T4):

- acceptance by finding removal: a validated edit goes through ``ctx.acceptance`` (the loop's ``AgentLoop.acceptance``:
  the dry re-check and ``causes.accept_edit``) before it is applied; its verdict (both finding lists, the reason)
  travels in the result as ``acceptance`` and in the log; ``target_findings`` names the findings an edit targets
  (the session's checklist step, else the finding on the edit's target), ``changed_targets`` what it changed;
- a building-wide tool (``causes.is_building_wide``: the roof, site, sun, materials, geometry, levels, terrain and
  the exterior cameras) is refused from a room session (``building_wide`` in ``failed_checks``); ``set_exterior`` is
  idempotent: an override that changes nothing against the building and the accepted overrides is a no-op with the
  reason (``no_change``), and its max-tries key names the keys it sets (``exterior:roof``), not the tool;
- ``retype_piece`` and ``swap_model`` get the catalogue (the retype refits the piece through ``fit.fit_piece``) and
  every furniture edit carries its ``target_finding`` (check, target, metrics) so ``swap_model`` can refuse an S2
  cut below 0.03 m; ``dry_run`` answers with the acceptance too.

Round 4 (before pod P3's second attempt): ``set_lighting`` is the tool of the render's ``lighting_dark`` findings
(``critic_code.lighting_items``); it changes every view of its room (``changed_targets``) and, like ``set_exterior``,
is a no-op with the reason when the room has that factor already (``lighting_state``: the building's
``agent_overrides.lighting`` under this run's accepted edits).

Fix round after P3 (16-17 Oct 2026): an edit's ``log_seq`` is the seq its log event gets (``_next_log_seq``
reserves it in the log, ``AgentLog.reserve``; the loop logs the edit with it), so ``overrides.json`` and
``adjusted_by_ai`` join the log exactly under parallel sessions.

Fix round after P4a (17 Oct 2026; pod P4a, real02):

- a memory refusal counts as a try of its target (``max_tries``), and the second refusal of the same edit in one
  session closes its checklist step: the result says ``step_closed`` and tells the model to go on (the loop ends the
  session when every step is done or closed). Why: P4a's session r1-s19 sent one refused move 7 times, 7 of its 12
  calls, and max_tries never fired;
- ``set_camera`` / ``add_camera`` are idempotent like ``set_exterior``: a pose the view already has (its last
  accepted override, else its scene camera; ``camera_pose_now``, ``same_pose``: 1 cm, 0.05 mm of lens) is a no-op
  with the reason (``no_change``), never an accepted edit. Why: P4a accepted the same set_camera ext_6 in rounds 2
  and 3; the dry re-check cannot measure X6 and counted it gone each time.

Fix round after P4b (17 Oct 2026; pod P4b, real03, the review of the P4a fix round and the lead's decisions of the
same day):

- decision 1: a camera replayed from the baseline (set 1; ``causes.frozen_camera``: ``source: replayed`` or a record
  that already replaced one) is frozen: ``set_camera``, ``remove_camera`` and an ``add_camera`` of its name are
  refused (``frozen``, counted as a try), with the reason; a new camera under a new view id may be added. Why: the
  P4a fix round's build merge made the agent's set really replace the replayed ext_6, so the frozen entrance view
  [7.59, 29.50] would have become a near-duplicate of ext_3 (docs/milestone13.md §7: set 1 keeps the old poses);
- decision 2: the role of an exterior camera stays: a ``frontal`` / ``elevation`` view is never turned into a pose
  that is no longer square to its facade (``build.agent_exterior_view``, the build's own rule: within 30 degrees),
  an ``entrance`` view keeps its door close and in front (``entrance_problem``: at most ``ENTRANCE_VIEW_MAX_M`` from
  the door face, within ``ENTRANCE_VIEW_MAX_DEG`` of the door's axis), and the only view of either
  role is not removed (``role_problem``). Why: P4b turned the frontal ext_6 and the entrance ext_7 into corner views
  for the vision critic's 3/4 rubric, then back to frontal for the code's X6 (8 accepted set_camera edits), and the
  final set had no entrance view; the far pose (40, -45) rendered blown out;
- an exterior camera refused for its eye height gets the ground under it and the z to use (``eye_height_hint``:
  "ground -0.15 m: use z 1.35-1.55"; P4b's 1.6 m tries were refused "eye height 1.75 m" without it);
- ``set_exterior``: the state it is compared with is the one the build makes (``exterior_state``: the site options'
  defaults and the brief's front court, the building's own site keys, the garden look the ground override writes,
  ``scene_manifest.exterior_looks.garden``), so P4b's ground 'grass' on a 'grass' garden is a no-op; a sun override
  is checked against the code's own X7 rule before the validator (``sun_problems``:
  ``exterior_checks.SUN_ELEVATION_RANGE``, 25-50 degrees, and the main facade's side, the compass azimuth turned to
  the building frame with ``site.north_deg``; decision 4: real02's assumed north stays). P4b set the sun to 55
  degrees for a vision X4 "no path". ``changed_targets`` adds a vision finding's target only when the override sets
  a slot of its cause (``causes.override_touches``);
- ``fix_fixture``: once the code's own search (no ``center``, no ``size``) found no valid spot for a piece, a later
  ``fix_fixture`` on that piece without a new size is refused (``no_spot``, counted as a try), in this session from
  its result and in later rounds from the memory (``memory.Memory.no_spot``). Why: P4b sent 21 centres in 5 cm steps
  after "no valid spot within 0.50 m" (and 13 max_tries);
- a ``dry_run`` repeated with the same arguments in a session, while no edit was accepted in between, is answered
  from the first one ("same as dry run #n"), counted as a try of its target and not validated again. Why: P4b sent
  one move of f_L0_141 nine times as a dry run, with the same answer;
- a ``swap_model`` result says that the footprint is kept (``footprint_kept``): the model is fitted to its width, so
  a swap does not change a wall cut across the width and changes one across the depth by a few cm at most
  (``loop.s2_wall_kept``, ``loop.swap_depth_slack``).

Integration of the fix round after P4b (17 Oct 2026; the site track's ask, the P4b verifier's better fix (c)):

- the entrance rule is ``exterior_checks.entrance_view_problem`` (one function for X6, the build's view check and
  this tool): the bearing is taken from the door (within 30 degrees of its axis, at most 14 m), and the door must be
  in the frame; the look-direction rule refused the planner's own entrance pose (real03's ext_7 looks 42 degrees off
  the axis, turned to the building's middle by ``exterior.frame_fixed``);
- an exterior ``set_camera`` / ``add_camera`` whose position lies within ``DUPLICATE_VIEW_M`` of another exterior
  camera (its pose the next build gives it: this session's accepted overrides first) and whose horizontal view
  direction is within ``DUPLICATE_VIEW_DEG`` of that camera's is refused (``duplicate_view_problem``, counted as a
  try; the camera of the same name, which the edit replaces, is left out). It compares geometry, not the ``sides``
  that ``overrides.fixed_plan`` copies. P4b's ext_6 and ext_7 stood 15-23 m apart when they showed the same facade;
  the role rules of decision 2 refuse those moves, this rule refuses a near copy of a view.

Pass before P5 (17 Oct 2026; the review of the fix round after P4b):

- decision 2 covers the frontal view by X6's own rule (``critic_vision.x6_frontal``: a ``frontal`` view, or an
  ``elevation`` / ``agent`` view square to the main facade, ``critic_vision.main_facade_of``): an ``agent`` view
  that is the frontal view (as the next build labels it, ``built_view``: an accepted set of a corner camera that no
  longer fits a corner is ``agent``) keeps a pose square to the main facade, and the only frontal view by that rule
  is not removed (the other views counted at the poses the next build gives them, ``exterior_poses``). Why:
  real04's planner drops ext_6 (P3: "inside the copy; 100% of the view blocked by trees") and code X6 "no frontal
  view of the entrance (+y) facade" fired in all 4 P3 rounds, so its frontal view is one the agent adds, labelled
  ``agent``; ``role_problem`` protected only the ``frontal`` / ``elevation`` labels, so the next set to a corner pose
  or a remove was accepted and the ping-pong of P4b could come back;
- the eye-height hint measures the ground as the validator does (``critic_vision.ground_z``: the building's site;
  the scene's terrain only without one) and names the z range with "to" ("use z -2.54 to -2.44"). Why: real04's
  ``tin`` terrain record in the scene manifest has no surface, so the hint said nothing on the project with the most
  sloped ground (its ground lies 0-4 m below zero, where "-2.54--2.44" is hard to read).

Pass before P5, round 2 (17 Oct 2026; the review of the pass before P5 and P3's real04 log):

- the frontal role follows the label the next build gives the pose, not only the pose's direction: ``next_view``
  starts from the planner's view and sides (``planner_view``: ``agent.view_was`` / ``agent.sides_was`` of a scene
  camera an earlier build relabelled, because the build plans the camera again and re-applies every override to it)
  and runs ``build.agent_exterior_view`` on the pose; a ``set`` / ``add`` of X6's frontal view (by label or by pose)
  is refused unless that label is still X6's frontal view or another camera stays one (``frontal_pose_problem``).
  Why: real04's corner ext_4 (left, back; back is the entrance +y facade) set square to the facade is ``agent``, X6's
  frontal view; a second set 25.8 degrees off the +y normal passed the direction check, but the build keeps that pose
  the corner of left, back (within 80 degrees of both normals), so code X6 "no frontal view" came back; in the round
  after, ``built_view`` took the scene's ``agent`` as the base, counted the corner pose as frontal and let the agent's
  added frontal view go;
- the aerial or site view the camera policy allows (``aerial_role``: ``aerial_allowed`` / ``site_view`` on an aerial
  or site label) is never brought down to eye level (``aerial_problem``: the next build would no longer label the
  pose aerial and would drop the flags); it may move to another aerial pose or be removed. Why: P3's critic called
  ext_5 and ext_7 "high angle, not at eye level" 9 times, and its round-6 ``set_camera`` brought ext_5 to z 2.46
  (accepted); the critic now drops those claims (``critic_vision.allowed_aerial``), this rule closes the tool path.

Pass before P5, round 2, review (17 Oct 2026):

- an aerial pose also stands on or above the high-view line of the camera validator and code X6
  (``critic_vision.high_view_line``: the roof's ``ridge_z`` + 1.0 m, 7.01 m on real04); ``aerial_problem`` refuses a
  pose below it as well as a pose that looks down less than 5 degrees, and its refusal states both rules. Why:
  real04's ext_5 set 1.60 m over the ground and aimed 6 degrees down passed the 5-degree rule, the validator passed
  its eye height, and the build kept it ``aerial`` with ``aerial_allowed`` (X6 skips the eye-level checks of an
  ``aerial`` view); the refusal of a level pose named only the 5 degrees and so invited that retry;
- an exterior camera added in this session is guarded like a scene camera (``added_camera``: the record
  ``role_problem`` judges when the scene manifest has no camera of that name but its last accepted entry is an
  exterior ``add``; ``next_view`` gives it the build's label of a new view, ``agent``). Why: ``role_problem``
  returned None for it, so the agent's own frontal view could be added again at a corner pose; with the "another
  camera stays X6's frontal view" exception (ext_4 set to a corner pose while the added ext_8 was frontal) that left
  real04 without a frontal view (code X6 "no frontal view of the entrance (+y) facade").

Pass before P5, integration (17 Oct 2026; track F's ask). What: ``plan_crop`` with a ``piece_id`` also shows the
piece's own recognition crop when one is on disk (``ToolContext.own_crop_path``: ``edit_ops.own_crops``, the crop a
review entry or conflict records for the piece first, else ``RECOGNITION_CROP_DIR``/<name>, the context crop before
the isolated one), as ``piece_crop`` with ``PIECE_CROP_NOTE``. Why: since the pass before P5 only that crop lifts the
mark lock of a drawn piece typed from the drawing (``edit_ops.own_crop_named``), but the tool returned only the room's
``check/<cam>_plan.jpg``, which never lifts it (P3 real04 seq 3282 / 3689 / 3692 cited that crop). On P3's real04
buildings 80 drawn pieces have their own crop in ``recognition/crops``; a piece without one gets the room crop only,
as before.

Fix round after P5 (22 Oct 2026; pod P5, real04, and the user's decisions of the same day):

- a ``max_tries`` refusal (``_too_many``) closes every checklist step on its target (``step_closed``,
  ``max_tries_target``) and says that every further edit of it is refused until the next round; an edit refused
  before any validator ran (``refused_unvalidated``: max tries, the memory, the code's fix_fixture search, a frozen
  camera) counts toward the loop's session end (``loop.REFUSALS_END_SESSION``). Why: P5's r2-s13 sent move_piece
  f_L1_024 six times after its max_tries refusal, 17-20k prompt tokens each;
- an accepted edit's verdict is applied by ``apply_verdict``: its finding list becomes the round's and the ids it
  changed join ``ctx.round_changed`` (the loop's dry re-check leaves the stale scene-manifest boxes of those targets
  out; P5 rejected 8 unrelated edits "new critical finding X2:f_L1_056" after the box's piece was removed);
- the memory refuses a repeat of a rejection about the round's finding list ("no target finding") in that round only
  (``_repeat_of`` passes ``ctx.round``; ``memory.Memory`` is scoped to the building and the code);
- ``dry_run`` of a level tool no longer carries ``target_finding`` (the level schemas have none: P5's dry_run
  set_terrain was refused "'target_finding' was unexpected"); a furniture dry run still carries it, as the real edit;
- an exterior camera refused for standing inside a building (the main one or another on the plot) gets the free
  stretch of its view line (``free_strip_hint``: P5's three add_camera ext_front_y stood inside b2 while 6 m in front
  of the entrance facade were free);
- the descriptions of ``retype_piece``, ``mark_not_furniture``, ``fix_fixture``, ``set_camera`` and ``add_camera`` name
  the user's decisions of 22 Oct 2026 where they change what a tool may do: a drawn piece typed from the drawing whose
  type does not fit its room is retyped, never removed, and a piece the code retyped from its size, room and
  neighbours keeps that type (the code's retype, not the agent's); a drawn bathtub or shower up to 5 cm longer than
  its bay is a misread size (``fix_fixture``); an exterior view of a long, low building may be framed wider or tilted.

Fix round after P5 (22 Oct 2026), review: ``remove_camera`` of an interior view is refused while it is the only view
of its room (``only_room_view_problem``, ``room_views``: the scene's cameras with this session's accepted adds and
removes), so a critical ``camera_blocked`` is fixed by ``set_camera``, never by dropping the room's render (P5's
cam_r_L1_banyo_1 is the bathroom's only view); ``free_strip_hint`` names the wider or tilted framing only for a long,
low building (``long_low_of``: ``exterior.long_low`` of the build's exterior model), else the eye-level lens.

Fix round after P6a (22 Oct 2026; pod P6a, real04): ``ToolContext.plan_crop_path`` gives a debug image only when its
file name names the room's level (``level_named``), never the first sheet of any level; ``plan_crop`` says
``NO_PLAN_CROP_NOTE`` then. Why: the basement rooms of real04 have no camera, so the tool fell back to the whole
sheet ``final/debug/deneme1_dwg_s1.jpg``; the agent cited it as the plan crop of the untyped 5.14 x 2.37 m piece
f_L-1b_002 (a rug outline under the salon seating) and marked it as not furniture (seq 5968), while its twin
f_L-1b_001 stayed under review.

Fix round after P6a, part 2 (23 Oct 2026; the exterior track's asks, docs/milestone13.md §14.13 decision 16):

- ``free_strip_hint`` names the free stretch of a refused exterior pose as a place to stand only when a level
  ``exterior.EYE_LENS_MM`` camera at its far end frames the building with the sky (``exterior.frame_check`` on the
  build's exterior model: ``fits`` and ``sky_share`` >= ``exterior.SKY_MIN_SHARE``) or the building is long and low
  (the wider or tilted framing); otherwise the hint says that no eye-level view fits there, how far from the target
  the facade needs a camera (``exterior.fill_distance``) and that the frontal view of that facade is a user decision.
  Why: P5's hint sent the agent into real04's 5.7 m strip between the entrance facade and b2; P6a's camera there
  (ext_front_entrance) showed a blank wall with no sky, both doors cut;
- the camera role guards (``x6_frontal_now``, ``frontal_pose_problem``, ``role_problem``) read X6's frontal view with
  its frame measured on ``ctx.building`` (``x6_frontal_of``: ``exterior_checks.x6_frontal`` on the build's exterior
  model, made once per context, ``exterior_of``), so a next-build plan without the build's recorded frame is judged
  as X6 judges the built camera: a pose square to the main facade that frames only part of the building or shows no
  sky is no frontal view, so its role no longer protects it.

Fix round after P6b (23 Oct 2026): an edit's ``acceptance`` record carries the dry re-check's fit record too
(``acceptance_record``: ``fitted`` ``{"overlaid", "refit"}``, at most 8 refit ids), so the log shows whether a piece
was fitted for the dry re-check (P6b's 219 edit events had no such record; ``loop.ACCEPTANCE_LOG_KEYS``).
"""
from __future__ import annotations

import copy
import itertools
import json
import math
import re
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from wenart.agent import causes as CS
from wenart.agent import geometry_fix as GF
from wenart.agent import log as LG
from wenart.agent import memory as MEM
from wenart.agent import overrides as OV
from wenart.agent import topdown as TD
from wenart.agent.model import tool_spec

MAX_TRIES = 3
MEMORY_REFUSALS_CLOSE = 2              # fix round after P4a: identical memory refusals in a session that close a step
POSE_TOLERANCE_M = 0.01                # fix round after P4a: two camera positions / targets this close are the same
LENS_TOLERANCE_MM = 0.05
# Fix round after P4b (module docstring): the camera roles the agent keeps, and the dry-run and no-spot refusals.
FRONTAL_VIEWS = ("frontal", "elevation")
ENTRANCE_VIEW = "entrance"
ENTRANCE_VIEW_MAX_M = 14.0             # the planner's farthest entrance view (exterior.ENTRANCE_VIEW_M, 12 m) + 2 m
ENTRANCE_VIEW_MAX_DEG = 30.0           # the planner's entrance view looks 20 degrees off the door's axis
DUPLICATE_VIEW_M = 6.0                 # integration after P4b: another exterior camera this close ...
DUPLICATE_VIEW_DEG = 15.0              # ... looking within this many degrees of it shows the same view
# Pass before P5, integration (module docstring): the folder of the reading's question crops (reading.CROP_DIR; a
# secondary page's crops are where its review entry records them) and what plan_crop says with a piece's own crop.
RECOGNITION_CROP_DIR = "recognition/crops"
PIECE_CROP_NOTE = ("piece_crop is the piece's own recognition crop (what the reading asked about it): the plan crop "
                   "mark_not_furniture accepts as evidence for a drawn piece typed from the drawing; the room's plan "
                   "crop (image) is no such evidence")
NO_PLAN_CROP_NOTE = ("no plan crop on disk for this room (a whole-sheet debug image is no plan crop: it never "
                     "counts as the crop of a piece)")


def level_named(file_name: str, level_id: str) -> bool:
    """Fix round after P6a: ``file_name`` names the level ``level_id`` as a word of its own (``plan_L0.jpg``,
    ``deneme1_L-1b_p1.jpg``; case-insensitive): not inside another level id (``L-1`` is not ``L-1b``) or word."""
    if not level_id:
        return False
    return re.search(rf"(?<![a-z0-9-]){re.escape(level_id.lower())}(?![a-z0-9])", file_name.lower()) is not None


FROZEN_CAMERA = ("frozen: {view} is a camera replayed from the baseline run (set 1): its pose is fixed for the "
                 "before/after comparison (docs/milestone13.md §7, decision of 17 Oct 2026); add_camera with a new "
                 "view id adds another view")
NO_SPOT_PREFIX = "no valid spot within"   # edit_ops._fix_fixture: the code's own search found no spot
PREVIEW_DIR = "agent/previews"         # the round previews (960x540, 32 samples)
FINAL_RENDER_DIR = "renders"
EDIT_META = ("op", "round", "log_seq", "model", "target_finding")      # set by the loop, never by the model
CATALOG_OPS = ("swap_model", "retype_piece")                           # edits that need the catalogue (M13: both)
BUILDING = "building"
# rerun_stage white list (§3.2): stage -> {setting: JSON schema of its value}. The scheduler honours
# polish.enabled (false: the project's views keep Cycles); the other stages are re-run as they are.
RERUN_WHITELIST: dict = {"refit": {}, "build": {}, "polish": {"enabled": {"type": "boolean"}}}

REASON = {"type": "string", "minLength": 3, "description": "why (one sentence, logged and shown in the report)"}
ID = {"type": "string", "minLength": 1}
XY = {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}
XYZ = {"type": "array", "items": {"type": "number"}, "minItems": 3, "maxItems": 3}


def _obj(props: dict, required: list) -> dict:
    return {"type": "object", "properties": props, "required": required, "additionalProperties": False}


# §3.2 inputs, used while track B's EDIT_SCHEMAS has no entry for an op.
FALLBACK_EDIT_SCHEMAS: dict = {
    "move": _obj({"piece_id": ID, "center": XY, "snap_wall_id": ID,
                  "offset": {"type": "number", "description": "metres along the wall from its start"}}, ["piece_id"]),
    "rotate": _obj({"piece_id": ID, "front_deg": {"type": "number", "description": "the direction the front faces, "
                                                  "degrees counter-clockwise from +x"}}, ["piece_id", "front_deg"]),
    "resize": _obj({"piece_id": ID, "size": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                                             "minItems": 2, "maxItems": 3}}, ["piece_id", "size"]),
    "change_type": _obj({"piece_id": ID, "type": ID}, ["piece_id", "type"]),
    "swap_model": _obj({"piece_id": ID, "asset_id": ID}, ["piece_id", "asset_id"]),
    "add": _obj({"room_id": ID, "type": ID, "anchor": {"type": "object"}}, ["room_id", "type"]),
    "add_group": _obj({"room_id": ID, "group": {"enum": ["dining_set", "bed_set", "living_set", "desk_set",
                                                         "kitchen_run"]},
                       "anchor": {"type": "object"}}, ["room_id", "group"]),
    "remove": _obj({"piece_id": ID, "evidence": {"type": "string"}}, ["piece_id"]),
    "relayout_room": _obj({"room_id": ID, "candidate": {"type": "integer", "minimum": 1, "maximum": 3,
                                                        "description": "the rank of the solver candidate to take "
                                                                       "(see the room brief)"}}, ["room_id"]),
    "set_room_type": _obj({"room_id": ID, "type": ID}, ["room_id", "type"]),
    # Milestone 12 (§5.3), used while track G's EDIT_SCHEMAS has no entry for these ops.
    "place_group": _obj({"room_id": ID, "group": {"type": "string", "description": "a group of the room's program "
                                                                                  "(groups.yaml name)"},
                         "option": {"type": "string", "description": "one of the group's program options"}},
                        ["room_id", "group"]),
    "complete_group": _obj({"group_id": ID}, ["group_id"]),
    "move_group": _obj({"group_id": ID, "span_id": {"type": "string", "description": "a free wall span id of the "
                                                                                     "room brief"},
                        "offset": {"type": "number", "description": "metres along the span from its start"}},
                       ["group_id", "span_id"]),
    "retype_piece": _obj({"piece_id": ID, "type": ID}, ["piece_id", "type"]),
    "mark_not_furniture": _obj({"piece_id": ID, "kind": {"enum": ["level_mark", "room_number", "north_arrow",
                                                                  "axis_bubble", "section_mark", "door_arc",
                                                                  "dimension", "text_frame", "line", "other"]},
                                "evidence": {"type": "string", "minLength": 3}}, ["piece_id", "kind", "evidence"]),
    "fix_fixture": _obj({"piece_id": ID, "size": {"type": "array", "items": {"type": "number", "exclusiveMinimum": 0},
                                                  "minItems": 2, "maxItems": 2,
                                                  "description": "a real product size [w, d] of its type"},
                         "center": dict(XY, description="only to choose a spot: a new centre at most 0.5 m away "
                                                        "(left out: the nearest valid spot)")}, ["piece_id"]),
    "set_front": _obj({"piece_id": ID, "front_deg": {"type": "number", "minimum": 0, "maximum": 360}},
                      ["piece_id", "front_deg"]),
}
LIBRARY_GAP_SCHEMA = _obj({"type": ID, "style": {"type": "string"}, "piece_id": ID}, ["type"])
FALLBACK_CAMERA_SCHEMA = _obj({"view_id": ID, "kind": {"enum": ["interior", "exterior"]}, "room_id": ID,
                               "position": XYZ, "target": XYZ, "lens_mm": {"type": "number", "minimum": 10,
                                                                           "maximum": 85}},
                              ["view_id", "kind", "position", "target", "lens_mm"])
FALLBACK_EXTERIOR_SCHEMA = _obj({
    "roof": _obj({"type": {"type": "string"}, "pitch_deg": {"type": "number"}, "overhang_m": {"type": "number"}}, []),
    "ground": {"type": "string", "description": "look id of the ground"},
    "site": _obj({"path": {"type": "boolean"}, "fence": {"type": "boolean"}, "trees": {"type": "integer"},
                  "front_court": {"enum": ["auto", "yes", "no"]}}, []),
    "sun": _obj({"azimuth_deg": {"type": "number"}, "elevation_deg": {"type": "number"}}, [])}, [])
LIGHTING_FACTOR = (0.5, 3.0)      # set_lighting: the room light power times this (real03: a black floor hall)
LIGHTING_SCHEMA = _obj({"room_id": ID,
                        "factor": {"type": "number", "minimum": LIGHTING_FACTOR[0], "maximum": LIGHTING_FACTOR[1],
                                   "description": "room light power x factor (1 = as assumed); a room with a factor "
                                                  "gets ceiling lights even when it has daylight"}},
                       ["room_id", "factor"])
MATERIAL_SCHEMA = _obj({"slot": {"type": "string", "description": "walls, floor, wet_walls, kitchen_walls, facade, "
                                                                  "roof, ground, frames, ..."},
                        "look_id": ID}, ["slot", "look_id"])

DESCRIPTIONS = {
    "building_summary": "Levels, rooms (type, name, area, status, ceiling), counts and open conflicts.",
    "room": "One room: polygon, walls with ids, doors (width, swing), windows (sill, head), pieces (id, type, "
            "footprint, front_deg, source, labels, failed checks).",
    "room_topdown": "A top-down image of the room: pieces with front arrows and ids, door swings, window bands, "
                    "failed checks in red.",
    "plan_crop": "The source plan crop of a room or of the room of a piece (what the drawing shows); with a "
                 "piece_id also the piece's own recognition crop when it has one (piece_crop).",
    "plausibility": "Plausibility score 0-100 and the violations of the checklist, for a room or the building.",
    "view": "One camera view: its preview image, camera position, target and lens, the visible elements.",
    "exterior_summary": "Outline, levels, roof, openings, site, sun and the exterior cameras.",
    "catalog": "Library models of a furniture type with their real sizes and style tags.",
    "stage_status": "Status, seconds and notes of the pipeline stages.",
    "move_piece": "Move a piece to a new centre, or snap its back to a wall (snap_wall_id, offset).",
    "rotate_piece": "Turn a piece so its front faces front_deg.",
    "resize_piece": "Resize a piece to a real product size.",
    "change_type": "Change a piece's type (within the types of the room type).",
    "swap_model": "Use another library model for a piece (never for a cut below 0.03 m: within tolerance; never "
                  "the model it has).",
    "add_piece": "Add one piece to a room (placed by the layout engine).",
    "add_group": "Add a functional group (dining_set, bed_set, living_set, desk_set, kitchen_run) to a room.",
    "remove_piece": "Remove a piece. A drawn piece only when it is clearly not furniture (give the evidence).",
    "relayout_room": "Re-place the AI pieces of a room (drawn pieces stay locked).",
    "set_room_type": "Change a room's type when it does not fit its area, fixtures and doors.",
    "set_camera": "Move an existing camera (position, target, lens). A camera replayed from the baseline (set 1) "
                  "is frozen and refused; a frontal view stays square to its facade, an entrance view stays "
                  "close in front of its door and the allowed aerial or site view stays an aerial view (never "
                  "brought to eye level). A camera_blocked interior view moves to a free point with headroom.",
    "add_camera": "Add a camera view under a new view id. An exterior view of a long, low building may be framed "
                  "wider or tilted; a refusal for standing inside a building names the free stretch of the view "
                  "line.",
    "remove_camera": "Remove a camera view (e.g. a view of a bare wall); never a replayed (set 1) camera, nor the "
                     "only frontal or entrance view, nor the only view of a room (set_camera moves it).",
    "set_material": "Set the look of a material slot (walls, floor, wet walls, kitchen walls, facade, roof, ground, "
                    "frames ...).",
    "set_exterior": "Change the roof (type, pitch, overhang), ground, site items or the sun (the building session "
                    "only; values the building already has are a no-op).",
    "set_lighting": "Make a room's ceiling lights stronger or weaker (factor 0.5-3; a dark or windowless room, a long "
                    "corridor, a lighting_dark view: the EV cap could not lift it, its finding names the factor the "
                    "room needs). Long rooms already get one light per 3 m of length.",
    "correct_geometry": "Record a clear geometry error: close a gap <= 0.15 m, merge a duplicate wall within 0.02 m, "
                        "put an opening <= 0.10 m off its wall back on it.",
    "rerun_stage": "Re-run a stage with white-listed settings (e.g. polish enabled false).",
    "finish": "End this round: your verdict and the findings that stay open.",
    # Milestone 12 (§5.2, §5.3, §3.6)
    "room_brief": "The room brief: built pieces with lock state and allowed tools, groups, free wall spans, fixable "
                  "and not-yours findings, memory, solver candidates.",
    "levels": "Level marks, room floor levels, door thresholds, ground points, terrain, entrances and the level "
              "findings.",
    "place_group": "Add a missing functional group of the room's program; the solver places it. When the room has a "
                   "drawn group of that kind (a drawn anchor with its drawn partners, built or not), the drawn group "
                   "is re-solved as one unit around its drawn anchor (every member within 0.5 m of its drawn "
                   "centre) instead of adding a second one.",
    "complete_group": "Add the missing partners of a group (e.g. the second nightstand); the solver places them.",
    "move_group": "Move a whole group to a free wall span (partners follow).",
    "retype_piece": "Change a piece's type to a type that fits its size and its room (zone); the piece is then "
                    "fitted and built (library model, module builder or parametric family in the project's licence "
                    "mode) and leaves the review list. The answer to a drawn piece typed from the drawing whose type "
                    "does not fit its room (F1, G14). A piece the code retyped from its size, room and neighbours "
                    "(adjusted_by_ai by code) keeps that type. With the piece's own type it confirms an unverified "
                    "piece (status verified, its model kept): complete_group needs a verified anchor.",
    "mark_not_furniture": "Record a drawn symbol, mark or line that was read as furniture (not built), with the "
                          "evidence (the piece's own recognition crop for a piece typed from the drawing; for an "
                          "untyped piece the image path of the plan crop you read, check/<view>_plan.jpg, else it is "
                          "refused: no_crop); never for a type that only does not fit the room (retype_piece).",
    "fix_fixture": "Misread fixed equipment: a real product size and/or a move of at most 0.5 m (through a wall, in "
                   "a door swing). Leave out center: the code moves it to the nearest valid spot (pod P5: 32 of 35 "
                   "guessed centres were still in a wall or a door swing). When the code answers 'no valid spot', no "
                   "centre will do: the finding stays for review. A drawn bathtub or shower up to 5 cm longer than its "
                   "bay is a misread size: without center and size it is shrunk to the nearest real product size that "
                   "fits the bay (drawn footprint kept).",
    "set_front": "Give a drawn piece without a front (front_inferred) the direction its front faces (degrees "
                 "counter-clockwise from +x, along a side of its footprint); to turn a piece use rotate_piece.",
    "set_mark_kind": "Correct the kind of a level mark (with the reason).",
    "set_room_floor": "Set a room's floor level from a mark or a drawn step line.",
    "set_ground_point": "Add or correct a ground point (x, y, z) with its evidence.",
    "set_entrance": "Choose the solution at an outside door: none, steps, ramp, steps and ramp.",
    "set_terrain": "Choose the terrain model: flat, planar or tin.",
    "report_library_gap": "Record that no audited library model of a type and style exists (a library gap).",
    "dry_run": "Ask the validator about an edit WITHOUT applying it (free: no try is counted): accepted or the failed "
               "checks with their numbers. The same dry run twice is answered from the first one and counts as a "
               "try.",
}
STAGE_OF = {"set_camera": "build", "add_camera": "build", "remove_camera": "build", "set_material": "build",
            "set_exterior": "build", "set_lighting": "build", "correct_geometry": "pipeline_final"}
# The tools offered to the M12 planner (§5.3): the M11 piece tools that the group tools replace (add_piece,
# add_group, change_type) and the M11 reads that the brief replaces (room, plausibility) stay callable for replay but
# are not offered. rotate_piece turns a piece (track G: set_front only gives a front to a piece without one).
PLANNER_READS = ("room_brief", "room_topdown", "plan_crop", "view", "levels", "catalog")
PLANNER_ROOM_EDITS = ("relayout_room", "place_group", "complete_group", "move_group", "move_piece", "rotate_piece",
                      "set_front", "resize_piece", "retype_piece", "mark_not_furniture", "fix_fixture", "remove_piece",
                      "swap_model", "set_room_type", "set_lighting", "report_library_gap")
PLANNER_BUILDING = ("building_summary", "exterior_summary", "set_exterior", "set_material", "set_camera",
                    "add_camera", "remove_camera", "correct_geometry", "rerun_stage", *OV.LEVEL_TOOLS)
PLANNER_CONTROL = ("dry_run", "finish")
PLANNER_TOOLS = PLANNER_READS + PLANNER_ROOM_EDITS + PLANNER_BUILDING + PLANNER_CONTROL


# --------------------------------------------------------------------------
# Context
# --------------------------------------------------------------------------

def read_json(path) -> Optional[dict]:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def working_building_path(project_out) -> Optional[Path]:
    """The building the edits apply to: ``building_agent.json`` (decor + the accepted edits) when it exists, else
    ``building_decor.json``, else ``building_final.json`` (a project without the decor stage)."""
    out = Path(project_out)
    for name in (OV.AGENT_BUILDING, OV.DECOR_BUILDING, "building_final.json"):
        if (out / name).is_file():
            return out / name
    return None


class SessionState:
    """What belongs to one planner session (one thread): the images its tools returned, its ``finish``, its checked
    checklist (Milestone 13: the steps name the findings an edit targets)."""

    def __init__(self, room_id: Optional[str] = None):
        self.room_id = room_id
        self.pending_images: list = []
        self.finished: Optional[dict] = None
        self.checklist: list = []
        self.refusals: dict = {}             # fix round after P4a: memory refusals per edit key in this session
        # fix round after P4b: the dry runs of the session (key -> {n, out, accepted}) and the pieces whose
        # fix_fixture search found no valid spot (piece id -> the refusal)
        self.dry_runs: dict = {}
        self.dry_n = 0
        self.no_spot: dict = {}


@dataclass
class ToolContext:
    """What the tools of one round see and change (one per round, shared by its parallel room sessions)."""
    project_out: Path
    building: dict
    round: int = 1
    model_id: str = ""
    log: Optional[LG.AgentLog] = None
    overrides: Optional[OV.Overrides] = None
    scene: dict = field(default_factory=dict)
    style: dict = field(default_factory=dict)
    preview_dir: str = PREVIEW_DIR
    violations: list = field(default_factory=list)       # code findings of the round (red in the top-down images)
    apply_edit: Optional[Callable] = None                # wenart.furniture.edit_ops.apply_edit (injectable)
    validators: Any = None                               # wenart.blender.exterior_checks (injectable)
    plausibility: Any = None                             # wenart.furniture.plausibility (injectable)
    catalog_loader: Optional[Callable] = None
    tries: dict = field(default_factory=dict)
    accepted: list = field(default_factory=list)          # [{tool, args, result}] of the round
    rejected: list = field(default_factory=list)
    schema_errors: int = 0
    max_tries: int = MAX_TRIES
    image_n: int = 0
    _catalog: Any = None
    # Milestone 12 (§5.2-§5.4)
    memory: Any = None                                   # wenart.agent.memory.Memory
    findings: list = field(default_factory=list)          # the round's findings (code + kept vision) for the briefs
    level_edit: Optional[Callable] = None                # wenart.levels.edits.apply_level_edit (injectable)
    level_checks: Optional[Callable] = None              # wenart.levels.checks.check_levels (injectable)
    sync: Optional[Callable] = None                      # wenart.furniture.decor.sync_to_hosts (injectable)
    brief_fns: dict = field(default_factory=dict)         # room_brief's *_fn arguments (tests inject fakes)
    dry_runs: int = 0
    refused_repeats: int = 0
    # Milestone 13: ``acceptance(ctx, tool, args, result, building_after) -> {"accepted", "reason", ...}`` (the
    # loop's dry re-check + ``causes.accept_edit``); None keeps the validator's verdict (replay, old tests).
    acceptance: Optional[Callable] = None
    # fix round after P5: the ids the round's accepted edits changed (``apply_verdict``; ``loop.after_findings`` leaves
    # the round's stale scene-manifest boxes of these targets out of every later dry re-check)
    round_changed: set = field(default_factory=set)
    # fix round after P6a, part 2: the build's plan and exterior model of ``building`` (``exterior_of``), made once
    _exterior: Any = None
    _default_session: Any = None
    _local: Any = None
    _lock: Any = None
    _counter: Any = None

    def __post_init__(self):
        self._default_session = SessionState()
        self._local = threading.local()
        self._lock = threading.RLock()
        self._counter = itertools.count(self.image_n + 1)

    # ----- the calling session (thread-local) --------------------------------------------------------------

    @property
    def lock(self):
        return self._lock

    def session(self) -> SessionState:
        return getattr(self._local, "session", None) or self._default_session

    def begin_session(self, room_id: Optional[str]) -> SessionState:
        state = SessionState(room_id)
        self._local.session = state
        return state

    def end_session(self) -> None:
        self._local.session = None

    @property
    def pending_images(self) -> list:
        return self.session().pending_images

    @property
    def finished(self) -> Optional[dict]:
        return self.session().finished

    @finished.setter
    def finished(self, value: Optional[dict]) -> None:
        self.session().finished = value

    @classmethod
    def load(cls, project_out, **kwargs) -> "ToolContext":
        out = Path(project_out)
        path = working_building_path(out)
        building = read_json(path) if path is not None else None
        if building is None:
            raise FileNotFoundError(f"no building JSON in {out}")
        scene = read_json(out / "scene" / "scene_manifest.json") or {}
        style = read_json(out / "style.json") or {}
        return cls(project_out=out, building=building, scene=scene, style=style, **kwargs)

    # ----- lazy modules (the other tracks' functions; tests inject fakes) ---------------------------------

    def edit_fn(self) -> Callable:
        if self.apply_edit is None:
            from wenart.furniture import edit_ops
            self.apply_edit = edit_ops.apply_edit
        return self.apply_edit

    def checks(self):
        if self.validators is None:
            from wenart.blender import exterior_checks
            self.validators = exterior_checks
        return self.validators

    def plaus(self):
        if self.plausibility is None:
            from wenart.furniture import plausibility
            self.plausibility = plausibility
        return self.plausibility

    def catalog(self):
        if self._catalog is None:
            if self.catalog_loader is not None:
                self._catalog = self.catalog_loader()
            else:
                from wenart.furniture import catalog as CAT
                self._catalog = CAT.load()
        return self._catalog

    def level_fn(self) -> Callable:
        if self.level_edit is None:
            from wenart.levels import edits
            self.level_edit = edits.apply_level_edit
        return self.level_edit

    def level_check_fn(self) -> Callable:
        if self.level_checks is None:
            from wenart.levels import checks
            self.level_checks = checks.check_levels
        return self.level_checks

    def sync_fn(self) -> Callable:
        return self.sync or OV.sync_decor

    def known_ops(self) -> tuple:
        """The ops the edit validator knows: every op when a validator is injected (tests), else track G's."""
        return tuple(OV.FURNITURE_TOOLS.values()) if self.apply_edit is not None else OV.known_ops()

    def group_checks_of(self, room_id: Optional[str]) -> list[str]:
        """The room's group checks now, as lines with their numbers (the edit results show them)."""
        if not room_id:
            return []
        fn = self.brief_fns.get("group_checks_fn")
        try:
            if fn is None:
                from wenart.furniture import group_checks
                fn = group_checks.check_room
            return [f"{v.get('check')} {v.get('severity')} {v.get('target')}: {v.get('message')}"
                    for v in fn(self.building, room_id) or []][:12]
        except Exception:  # noqa: BLE001 - the checks are information here, never a reason to fail the edit
            return []

    # ----- lookups -------------------------------------------------------------------

    def room(self, room_id: str) -> Optional[dict]:
        return next((r for r in self.building.get("rooms") or [] if r.get("id") == room_id), None)

    def piece(self, piece_id: str) -> Optional[dict]:
        return next((f for f in self.building.get("furniture") or [] if f.get("id") == piece_id), None)

    def cameras(self) -> list[dict]:
        return [c for c in self.scene.get("cameras") or [] if isinstance(c, dict)]

    def camera(self, view_id: str) -> Optional[dict]:
        return next((c for c in self.cameras() if c.get("name") == view_id), None)

    def images_dir(self) -> Path:
        if self.log is not None:
            return self.log.images_dir
        path = LG.orchestrator_dir(self.project_out) / LG.IMAGES_DIR
        path.mkdir(parents=True, exist_ok=True)
        return path

    def rel(self, path) -> Optional[str]:
        return self.log.rel(path) if self.log is not None else (str(path) if path is not None else None)

    def image_name(self, what: str) -> Path:
        n = next(self._counter)
        self.image_n = max(self.image_n, n)
        safe = "".join(ch if ch.isalnum() or ch in "-_." else "_" for ch in what)
        return self.images_dir() / f"r{self.round}_{n:03d}_{safe}.png"

    def candidate_image(self, room_id: str, rank: int, candidate: dict) -> Optional[str]:
        """The top-down image of solver candidate ``rank`` (``topdown.draw_candidate``), its log-relative id."""
        try:
            apply_fn = self.brief_fns.get("apply_candidate_fn")
            path = TD.draw_candidate(self.building, room_id, candidate, self.image_name(f"cand{rank}_{room_id}"),
                                     apply_fn=apply_fn)
        except Exception:  # noqa: BLE001 - a candidate without an image is still listed
            return None
        return self.rel(path)

    def brief(self, room_id: str) -> dict:
        """The room brief (``brief.room_brief``) with this round's findings of the room and the memory."""
        from wenart.agent import brief as BRF
        fns = {k: v for k, v in self.brief_fns.items() if k.endswith("_fn") and k != "apply_candidate_fn"}
        return BRF.room_brief(self.building, room_id, findings=BRF.findings_of_room(self.findings, self.building,
                                                                                   room_id),
                              memory=self.memory, image_of=lambda rank, c: self.candidate_image(room_id, rank, c),
                              **fns)

    def topdown(self, room_id: str, building: Optional[dict] = None, what: str = "topdown",
                annotate: bool = True) -> Optional[Path]:
        try:
            room_violations = [v for v in self.violations if v.get("room_id") == room_id or v.get("target") == room_id]
            return TD.draw_room(building or self.building, room_id, self.image_name(f"{what}_{room_id}"),
                                room_violations, annotate=annotate)
        except Exception:  # noqa: BLE001 - an image that cannot be drawn is no reason to fail the edit
            return None

    def preview_path(self, view_id: str) -> Optional[Path]:
        for folder in (self.preview_dir, FINAL_RENDER_DIR):
            p = self.project_out / folder / f"{view_id}_preview.jpg"
            if p.is_file():
                return p
        return None

    def plan_crop_path(self, room_id: str) -> Optional[Path]:
        """An existing plan crop of the room (M11 step 3: take what exists): ``check/<cam>_plan.jpg``, then
        ``final/<cam>_plan.jpg`` of the room's cameras, then a debug image named for the room's level. Fix round
        after P6a: never a debug image of no level (a whole sheet): P6a's room r_L-1b_salon has no camera, the tool
        gave ``final/debug/deneme1_dwg_s1.jpg`` and the agent cited the whole sheet as the plan crop of the untyped
        piece f_L-1b_002 it marked as not furniture; None then (the tool says no plan crop is on disk)."""
        cams = [c.get("name") for c in self.cameras() if c.get("room_id") == room_id]
        for folder in ("check", "final"):
            for cam in cams:
                p = self.project_out / folder / f"{cam}_plan.jpg"
                if p.is_file():
                    return p
        room = self.room(room_id) or {}
        level = str(room.get("level_id") or "")
        if not level:
            return None
        for folder in ("debug", "final/debug"):
            found = sorted((self.project_out / folder).glob("*.jpg")) if (self.project_out / folder).is_dir() else []
            pick = [p for p in found if level_named(p.name, level)]
            if pick:
                return pick[0]
        return None

    def own_crop_path(self, piece_id: Optional[str]) -> Optional[Path]:
        """Pass before P5, integration (module docstring): the piece's own recognition crop on disk
        (``edit_ops.own_crops``), else None: the crop path a ``needs_review`` entry or a conflict records for the
        piece, then ``RECOGNITION_CROP_DIR``/<name> (``_ctx`` before ``_iso`` before the single crop). Never the room's
        or a camera's plan crop."""
        item = self.piece(piece_id) if piece_id else None
        if item is None:
            return None
        from wenart.furniture import edit_ops as EO

        names = EO.own_crops(self.building, item)
        if not names:
            return None
        recorded = [str(n.get("crop") or "") for n in self.building.get("needs_review") or []
                    if isinstance(n, dict) and n.get("id") == item.get("id")]
        recorded += [str(c.get("crop") or "") for c in self.building.get("conflicts") or []
                     if isinstance(c, dict) and item.get("id") in (c.get("element_ids") or [])]
        order = sorted(names, key=lambda n: (0 if n.endswith("_ctx.png") else 1 if n.endswith("_iso.png") else 2, n))
        paths = [self.project_out / r for r in recorded if r and not Path(r).is_absolute() and Path(r).name in names]
        paths += [self.project_out / RECOGNITION_CROP_DIR / n for n in order]
        return next((p for p in paths if p.is_file()), None)

    def room_of(self, target: Optional[str]) -> Optional[str]:
        if not target:
            return None
        if self.room(target) is not None:
            return target
        piece = self.piece(target)
        if piece is not None:
            return piece.get("room_id")
        cam = self.camera(target)
        if cam is not None:
            return cam.get("room_id")
        return None


@dataclass
class Tool:
    name: str
    kind: str                    # read | furniture | override | record | control
    description: str
    parameters: dict
    handler: Callable[[ToolContext, dict], dict]
    stage: Optional[str] = None  # the stage an accepted edit re-runs from (furniture: from the result)

    def spec(self) -> dict:
        return tool_spec(self.name, self.description, self.parameters)


class Registry:
    def __init__(self, tools: list[Tool]):
        self.tools = {t.name: t for t in tools}

    def names(self) -> list[str]:
        return list(self.tools)

    def specs(self, names=None) -> list[dict]:
        """The tool specs (all, or ``names`` in that order: the M12 planner gets ``PLANNER_TOOLS`` or a subset)."""
        if names is None:
            return [t.spec() for t in self.tools.values()]
        return [self.tools[n].spec() for n in names if n in self.tools]

    def call(self, ctx: ToolContext, name: str, args: Optional[dict], parse_error: Optional[str] = None) -> dict:
        """Run one tool call; a bad call returns ``{"error", "schema_error": true}`` and counts in
        ``ctx.schema_errors``. Milestone 12: an edit identical to one rejected earlier in the same room (the memory)
        is refused without running it; every validated edit is recorded in the memory."""
        from wenart.recognition.vlm_client import schema_errors
        tool = self.tools.get(name)
        if tool is None:
            with ctx.lock:
                ctx.schema_errors += 1
            return {"error": f"unknown tool {name!r}; the tools are: {', '.join(self.tools)}", "schema_error": True}
        if parse_error:
            with ctx.lock:
                ctx.schema_errors += 1
            return {"error": f"bad arguments for {name}: {parse_error}", "schema_error": True}
        errors = schema_errors(tool.parameters, args if args is not None else {})
        if errors:
            with ctx.lock:
                ctx.schema_errors += 1
            return {"error": f"the arguments of {name} do not match its schema: " + "; ".join(errors[:5]),
                    "schema_error": True}
        args = dict(args or {})
        remember = tool.kind in EDIT_KINDS and ctx.memory is not None
        room = edit_room(ctx, args) if remember else None
        session_room = ctx.session().room_id
        if tool.kind in EDIT_KINDS and session_room not in (None, BUILDING) and CS.is_building_wide(name, args):
            # Milestone 13: building-wide edits come only from the building session (real04: a corridor session
            # flattened the roof; 10 roof edits from 6 room sessions, last writer wins)
            out = _result(False, [f"building_wide: {name} changes the whole building (roof, site, sun, materials, "
                                  f"geometry, levels or an exterior camera); only the building session may call "
                                  f"it, not the session of {session_room}"],
                          message="refused: a building-wide edit from a room session", tool=name)
            if remember:
                ctx.memory.record(room, ctx.round, name, args, out)
            return _reject(ctx, name, args, out)
        if remember:
            prev = _repeat_of(ctx, room, name, args)
            if prev is not None:
                ctx.memory.refused()
                state = ctx.session()
                key = MEM.edit_key(name, args)
                with ctx.lock:
                    ctx.refused_repeats += 1
                    # fix round after P4a: a refusal is a try of its target (max_tries), and the second identical
                    # refusal in the session closes the checklist step (module docstring)
                    target = _target(name, args)
                    ctx.tries[target] = ctx.tries.get(target, 0) + 1
                    state.refusals[key] = state.refusals.get(key, 0) + 1
                    closed = state.refusals[key] >= MEMORY_REFUSALS_CLOSE
                out = _result(False, [f"memory: the same edit was rejected in round {prev.get('round')}: "
                                      + "; ".join(prev.get("reasons") or ["rejected"])[:300]],
                              message="refused without validation: this exact edit was rejected before; try "
                                      "something else", refused_by_memory=True)
                if closed:
                    out["step_closed"] = True
                    out["closed_why"] = "the memory refused its edit twice"
                    out["message"] = (f"refused again without validation ({state.refusals[key]} times in this "
                                      "session): this exact edit was rejected before. Its checklist step is closed: "
                                      "go on with the next step, or call finish")
                return _reject(ctx, name, args, out)
        if name == "fix_fixture":
            # fix round after P4b (module docstring): the code's search found no spot; no centre will
            out = no_spot_refusal(ctx, args)
            if out is not None:
                return _reject(ctx, name, args, out)
        try:
            res = tool.handler(ctx, args)
        except Exception as exc:  # noqa: BLE001 - the model sees the error and may try another way
            return {"error": f"{name} failed: {type(exc).__name__}: {exc}"}
        if name == "fix_fixture":
            note_no_spot(ctx, args, res)
        failed = list(res.get("failed_checks") or [])
        if remember and "accepted" in res and not (failed and (failed[0].startswith("max_tries")
                                                              or failed[0] == "validator_unavailable")):
            ctx.memory.record(room, ctx.round, name, args, res)
        return res


def _repeat_of(ctx: ToolContext, room: Optional[str], name: str, args: dict) -> Optional[dict]:
    """The memory's earlier rejection of this edit (``memory.Memory.repeat_of``); fix round after P5: with the round,
    so a rejection about the round's finding list only refuses its repeat in that round."""
    try:
        return ctx.memory.repeat_of(room, name, args, round_no=ctx.round)
    except TypeError:                    # a memory without the round argument (an older one, a test fake)
        return ctx.memory.repeat_of(room, name, args)


# --------------------------------------------------------------------------
# Read tools (§3.1)
# --------------------------------------------------------------------------

def _round(v, n=3):
    try:
        return round(float(v), n)
    except (TypeError, ValueError):
        return v


def t_building_summary(ctx: ToolContext, args: dict) -> dict:
    b = ctx.building
    level = args.get("level")
    levels = [{"id": lv.get("id"), "label": lv.get("label"), "elevation": lv.get("elevation"),
               "ceiling_height": lv.get("ceiling_height")} for lv in b.get("levels") or []]
    furniture = b.get("furniture") or []
    rooms = []
    for r in b.get("rooms") or []:
        if level and r.get("level_id") != level:
            continue
        rooms.append({"id": r.get("id"), "label": r.get("label"), "type": r.get("room_type"),
                      "level_id": r.get("level_id"), "area": _round(r.get("area_computed"), 2),
                      "status": r.get("status"), "ceiling": r.get("ceiling_height"),
                      "pieces": sum(1 for f in furniture if f.get("room_id") == r.get("id"))})
    by_source: dict = {}
    for f in furniture:
        by_source[str(f.get("source"))] = by_source.get(str(f.get("source")), 0) + 1
    return {"levels": levels, "rooms": rooms,
            "counts": {"rooms": len(b.get("rooms") or []), "walls": len(b.get("walls") or []),
                       "openings": len(b.get("openings") or []), "furniture": by_source},
            "conflicts": list(b.get("conflicts") or [])[:20], "unverified": len(b.get("unverified") or [])}


def _room_walls(ctx: ToolContext, room: dict) -> list[dict]:
    from shapely.geometry import LineString, Polygon
    ring = Polygon(room["polygon"]).exterior
    out = []
    for w in ctx.building.get("walls") or []:
        if w.get("level_id") != room.get("level_id"):
            continue
        line = LineString([w["start"], w["end"]])
        if line.length < 1e-6:
            continue
        near = float(w.get("thickness") or 0.2) / 2.0 + 0.08
        if ring.distance(line.interpolate(0.5, normalized=True)) <= near:
            out.append({"id": w.get("id"), "start": w.get("start"), "end": w.get("end"),
                        "thickness": w.get("thickness"), "exterior": w.get("exterior")})
    return out


def t_room(ctx: ToolContext, args: dict) -> dict:
    room = ctx.room(args["room_id"])
    if room is None:
        return {"error": f"no room {args['room_id']}"}
    from wenart.furniture import placer
    doors, windows = placer.room_openings(ctx.building, room)
    swings: dict = {}
    try:
        rc = placer.room_context(ctx.building, room)
        swings = {d.id: [[_round(x), _round(y)] for x, y in d.swing.exterior.coords]
                  for d in rc.doors if d.swing is not None and not d.swing.is_empty and d.swing.geom_type == "Polygon"}
    except Exception:  # noqa: BLE001 - a room without a usable context still lists its openings
        pass
    fails: dict = {}
    for v in ctx.violations:
        fails.setdefault(v.get("target"), []).append(f"{v.get('check')} {v.get('severity')}: {v.get('message')}")
    pieces = []
    for f in TD.room_pieces(ctx.building, room["id"]):
        labels = [k for k in ("adjusted_by_ai", "inferred", "modified_by_ai", "completes_room") if f.get(k)]
        pieces.append({"id": f.get("id"), "type": f.get("type"), "source": f.get("source"),
                       "footprint": f.get("footprint"), "front_deg": f.get("front_deg"), "height": f.get("height"),
                       "status": f.get("status"), "labels": labels, "checks": fails.get(f.get("id"), [])})
    return {"id": room["id"], "label": room.get("label"), "type": room.get("room_type"),
            "level_id": room.get("level_id"), "area": _round(room.get("area_computed"), 2),
            "polygon": room.get("polygon"), "walls": _room_walls(ctx, room),
            "doors": [{"id": d.get("id"), "width": d.get("width"), "wall_id": d.get("wall_id"),
                       "center": d.get("center"), "swing_side": d.get("swing_side"),
                       "swing_polygon": swings.get(d.get("id"))} for d in doors],
            "windows": [{"id": w.get("id"), "width": w.get("width"), "wall_id": w.get("wall_id"),
                         "center": w.get("center"), "sill": w.get("sill_height"), "head": w.get("height")}
                        for w in windows],
            "pieces": pieces, "checks": fails.get(room["id"], [])}


def t_room_topdown(ctx: ToolContext, args: dict) -> dict:
    if ctx.room(args["room_id"]) is None:
        return {"error": f"no room {args['room_id']}"}
    if args.get("candidate"):
        # Milestone 12: the top-down image of solver candidate k (the brief lists their ranks and scores)
        fn = ctx.brief_fns.get("solver_fn")
        if fn is None:
            from wenart.furniture import solver
            fn = solver.solve_room
        cands = fn(ctx.building, args["room_id"], k=3) or []
        cand = next((c for c in cands if int(c.get("rank") or 0) == int(args["candidate"])), None)
        if cand is None:
            return {"error": f"no solver candidate {args['candidate']} for {args['room_id']} ({len(cands)} found)"}
        image = ctx.candidate_image(args["room_id"], int(args["candidate"]), cand)
        if image is None:
            return {"error": "the candidate image could not be drawn"}
        ctx.pending_images.append(ctx.images_dir().parent / image if not Path(image).is_absolute() else Path(image))
        return {"room_id": args["room_id"], "candidate": int(args["candidate"]), "image": image, "shown": True}
    path = ctx.topdown(args["room_id"], annotate=args.get("annotate", True))
    if path is None:
        return {"error": "the top-down image could not be drawn"}
    ctx.pending_images.append(path)
    return {"room_id": args["room_id"], "image": ctx.rel(path), "shown": True}


def t_room_brief(ctx: ToolContext, args: dict) -> dict:
    if ctx.room(args["room_id"]) is None:
        return {"error": f"no room {args['room_id']}"}
    return ctx.brief(args["room_id"])


# What the ``levels`` tool shows of a level mark and of an entrance (track L's fields, schema ``level_marks[]``,
# ``site.entrances[]``; docs/m12_tracks/L.md): its kind and its use, the AI labels.
LEVEL_MARK_FIELDS = ("id", "value", "relative", "absolute", "z", "kind", "point", "level_id", "room_id", "side",
                     "used_for", "status", "placement", "door_id", "corrected_by_ai", "inferred", "adjusted_by_ai",
                     "note")
ENTRANCE_FIELDS = ("door_id", "level_id", "room_id", "side", "main", "drawn", "solution", "rise", "into_air",
                   "below_ground", "terrain_lowered", "ground_source", "reason", "adjusted_by_ai")


def t_levels(ctx: ToolContext, args: dict) -> dict:
    """Milestone 12 (§3.6): the building's level data and the L-findings (``levels.checks.check_levels``)."""
    b = ctx.building
    site = b.get("site") or {}
    try:
        findings = [{"check": v.get("check"), "severity": v.get("severity"), "target": v.get("target"),
                     "message": v.get("message"), "metrics": v.get("metrics") or {}}
                    for v in ctx.level_check_fn()(b, ctx.scene, None) or []]
    except Exception as exc:  # noqa: BLE001 - the level data is still shown
        findings = [{"error": f"{type(exc).__name__}: {exc}"}]
    marks = [{k: m.get(k) for k in LEVEL_MARK_FIELDS if m.get(k) is not None} for m in b.get("level_marks") or []]
    ground = site.get("ground") or {}
    inference = b.get("level_inference") or {}
    return {"datum": (b.get("project") or {}).get("datum"),
            "levels": [{"id": lv.get("id"), "elevation": lv.get("elevation"),
                        "elevation_source": lv.get("elevation_source"), "ceiling_height": lv.get("ceiling_height")}
                       for lv in b.get("levels") or []],
            "marks": marks[:80], "marks_total": len(marks),
            "room_floors": [{"room_id": r.get("id"), "floor_offset_m": r.get("floor_offset_m"),
                             "floor_source": r.get("floor_source"), "floor_evidence": r.get("floor_evidence")}
                            for r in b.get("rooms") or [] if r.get("floor_offset_m") not in (None, 0, 0.0)
                            or r.get("floor_source")],
            "thresholds": [{"opening_id": o.get("id"), "threshold_z": o.get("threshold_z")}
                           for o in b.get("openings") or [] if o.get("threshold_z") is not None],
            "ground": {"points": list(ground.get("points") or [])[:60], "surface": ground.get("surface"),
                       "source": ground.get("source"), "terrain_override": ground.get("terrain_override"),
                       "light_wells": list(ground.get("light_wells") or [])[:10]},
            "terrain": site.get("terrain") or ground.get("surface"),
            "entrances": [{k: e.get(k) for k in ENTRANCE_FIELDS if e.get(k) is not None}
                          for e in site.get("entrances") or [] if isinstance(e, dict)],
            "plinth": site.get("plinth"),
            "level_inference": {k: (v[:20] if isinstance(v, list) else v) for k, v in inference.items()},
            "conflicts": [c for c in b.get("conflicts") or [] if "level" in json.dumps(c).lower()][:20],
            "findings": findings}


def t_plan_crop(ctx: ToolContext, args: dict) -> dict:
    room_id = args.get("room_id") or ctx.room_of(args.get("piece_id"))
    if not room_id or ctx.room(room_id) is None:
        return {"error": "give a room_id or a piece_id of this building"}
    path = ctx.plan_crop_path(room_id)
    if path is None:
        out = {"room_id": room_id, "image": None, "note": NO_PLAN_CROP_NOTE}
    else:
        ctx.pending_images.append(path)
        out = {"room_id": room_id, "image": str(path.relative_to(ctx.project_out)), "shown": True}
    own = ctx.own_crop_path(args.get("piece_id"))     # pass before P5, integration: the piece's own crop, newest last
    if own is not None:
        ctx.pending_images.append(own)
        out.update(piece_crop=str(own.relative_to(ctx.project_out)), piece_crop_note=PIECE_CROP_NOTE)
    return out


def t_plausibility(ctx: ToolContext, args: dict) -> dict:
    try:
        if args.get("room_id"):
            if ctx.room(args["room_id"]) is None:
                return {"error": f"no room {args['room_id']}"}
            return ctx.plaus().score_room(ctx.building, args["room_id"])
        res = ctx.plaus().score_building(ctx.building)
        return {"mean": res.get("mean"), "counts": res.get("counts"),
                "rooms": {rid: r.get("score") for rid, r in (res.get("rooms") or {}).items()}}
    except NotImplementedError:
        return {"error": "the plausibility score is not available in this build (wenart.furniture.plausibility)"}


def t_view(ctx: ToolContext, args: dict) -> dict:
    cam = ctx.camera(args["view_id"])
    if cam is None:
        return {"error": f"no view {args['view_id']}; views: {', '.join(c.get('name') for c in ctx.cameras())}"}
    preview = ctx.preview_path(cam["name"])
    if preview is not None:
        ctx.pending_images.append(preview)
    plan = ctx.plan_crop_path(cam.get("room_id")) if cam.get("room_id") else None
    return {"view_id": cam["name"], "kind": cam.get("kind") or ("exterior" if not cam.get("room_id") else "interior"),
            "room_id": cam.get("room_id"), "position": cam.get("position"), "target": cam.get("target"),
            "lens_mm": cam.get("lens_mm"), "visible_furniture": cam.get("visible_furniture"),
            "visible_openings": cam.get("visible_openings"),
            "image": str(preview.relative_to(ctx.project_out)) if preview else None,
            "plan_crop": str(plan.relative_to(ctx.project_out)) if plan else None, "shown": preview is not None}


def t_exterior_summary(ctx: ToolContext, args: dict) -> dict:
    b = ctx.building
    ext = [w for w in b.get("walls") or [] if w.get("exterior")]
    xs = [float(p[0]) for w in ext for p in (w["start"], w["end"])]
    ys = [float(p[1]) for w in ext for p in (w["start"], w["end"])]
    per_level: dict = {}
    for o in b.get("openings") or []:
        lv = per_level.setdefault(str(o.get("level_id")), {})
        lv[str(o.get("type"))] = lv.get(str(o.get("type")), 0) + 1
    return {"outline_bbox": [min(xs), min(ys), max(xs), max(ys)] if xs else None, "outer_walls": len(ext),
            "levels": [{"id": lv.get("id"), "elevation": lv.get("elevation"),
                        "ceiling_height": lv.get("ceiling_height")} for lv in b.get("levels") or []],
            "roof": b.get("roof"), "site": {k: v for k, v in (b.get("site") or {}).items() if k in
                                            ("plot", "ground", "paving", "front_court", "grade")},
            "facade": b.get("facade"), "openings_per_level": per_level,
            "lighting": ctx.scene.get("lighting"), "exterior_cameras": [
                {"view_id": c.get("name"), "position": c.get("position"), "target": c.get("target"),
                 "lens_mm": c.get("lens_mm")} for c in ctx.cameras() if c.get("kind") == "exterior"],
            "agent_overrides": (b.get("agent_overrides") or {}).get("exterior")}


# Fix round after P4a (integration of the library verifier's better_fix): how ``catalog`` names a generated model to the
# agent (P4a's agent called gen_fridge_mediterranean_3 "a real compact fridge model"); fit.fit_piece refuses a pin to
# one while a real product of the type fits within the caps.
GENERATED_MODEL_NOTE = "generated, units guessed (not a real product; a pin is refused while a real product fits)"


def t_catalog(ctx: ToolContext, args: dict) -> dict:
    entries = list(ctx.catalog().candidates(args["type"]))
    if args.get("style"):
        styled = [e for e in entries if args["style"] in (e.get("styles") or [])
                  or e.get("style_family") == args["style"]]
        entries = styled or entries
    size = args.get("size")
    if size:
        def dist(e):
            bb = e.get("bbox_m") or [0, 0, 0]
            return abs(float(bb[0]) - float(size[0])) + abs(float(bb[1]) - float(size[1]))
        entries = sorted(entries, key=dist)
    keep = ("id", "type", "source", "licence", "bbox_m", "styles", "style_family", "name")

    def row(e):
        out = {k: e.get(k) for k in keep}
        if e.get("source") == "generated":       # fix round after P4a: the fit refuses such a pin when a real one fits
            out["note"] = GENERATED_MODEL_NOTE
        return out
    return {"type": args["type"], "count": len(entries), "models": [row(e) for e in entries[:10]]}


def t_stage_status(ctx: ToolContext, args: dict) -> dict:
    run_dir = ctx.project_out / "run"
    out = {}
    names = [args["stage"]] if args.get("stage") else sorted(p.stem for p in run_dir.glob("*.json"))
    for name in names:
        rec = read_json(run_dir / f"{name}.json")
        if rec is not None:
            out[name] = {"status": rec.get("status"), "seconds": rec.get("seconds"), "note": rec.get("note")}
    return {"stages": out}


# --------------------------------------------------------------------------
# Edit tools (§3.2)
# --------------------------------------------------------------------------

def _target(tool: str, args: dict) -> str:
    """What an edit changes (the max-tries key): its piece, group, room, view, opening, wall, level, stage or slot;
    else the tool. Pod P5: without ``group_id`` every group edit counted on the tool's name, so after three group
    edits anywhere in the building the next 34 were refused with max_tries."""
    for key in ("piece_id", "group_id", "room_id", "view_id", "opening_id", "wall_id", "door_id", "level_id",
                "stage", "slot"):
        if args.get(key):
            return str(args[key])
    if tool == "set_exterior":
        # Milestone 13 (bug B4): one key per part set (roof, site, sun, ground), not one shared by every session
        keys = sorted(k for k in args if k not in ("reason",) and args.get(k) is not None)
        if keys:
            return "exterior:" + ",".join(keys)
    return tool


def target_findings(ctx: ToolContext, tool: str, args: dict) -> list[dict]:
    """Milestone 13: the findings an edit targets, from the round's findings (``ctx.findings``): the session's
    checklist step with this tool and target names them (``finding_ids``); else the most severe finding on the
    edit's target whose cause this tool fixes (``causes.tools_for_finding``), else any finding on the target; for a
    room tool the room's findings the tool fixes, for a group tool its members', for a building-wide tool the
    building-level ones. At most one finding unless the checklist named several."""
    findings = list(ctx.findings or [])
    if not findings:
        return []
    target = _target(tool, args)
    by_id = {f.get("id"): f for f in findings if f.get("id")}
    for step in ctx.session().checklist or []:
        if step.get("tool") != tool or step.get("target") not in (target, args.get("room_id"), args.get("group_id")):
            continue
        named = [by_id[i] for i in step.get("finding_ids") or [] if i in by_id]
        if named:
            return named

    def rank(f: dict):
        return (CS.SEVERITY_ORDER.get(f.get("severity"), 3), str(f.get("check")), str(f.get("target")))

    def fixes(f: dict) -> bool:
        return tool in CS.tools_for_finding(f)

    # round 2: a finding about an unbuilt anchor (``causes.anchor_of``) is on the anchor the edit builds
    on_target = sorted((f for f in findings if f.get("target") == target or CS.anchor_of(f) == target), key=rank)
    cands = [f for f in on_target if fixes(f)] or on_target
    if not cands and args.get("group_id"):
        members = {f.get("id") for f in ctx.building.get("furniture") or []
                   if (f.get("group") or {}).get("group_id") == args["group_id"]}
        cands = sorted((f for f in findings if f.get("target") in members and fixes(f)), key=rank)
    if not cands and args.get("room_id"):
        room = args["room_id"]
        cands = sorted((f for f in findings if (f.get("room_id") == room or f.get("target") == room) and fixes(f)),
                       key=rank)
    if not cands and CS.is_building_wide(tool, args):
        cands = sorted((f for f in findings if not f.get("room_id") and fixes(f)), key=rank)
    return cands[:1]


def changed_targets(tool: str, args: dict, result: dict, targets: list[dict], findings: Optional[list] = None) -> set:
    """Milestone 13: the ids an edit changed (for the dry re-check): the edit's piece, room, group or view, the
    validator's ``changed_ids``, the targets of the findings it addresses; a building-wide edit changes
    ``building`` and the exterior as a whole. Round 4: ``set_lighting`` changes the light of every view of its room,
    so the views of the room's ``lighting_dark`` findings in ``findings`` (the round's) are changed too (the next
    render re-meters them); without that a room with two dark views kept one of them as "still there"."""
    out = {args.get(k) for k in ("piece_id", "room_id", "group_id", "view_id") if args.get(k)}
    out |= {str(i) for i in (result.get("changed_ids") or [])}
    override = {k: v for k, v in args.items() if k != "reason"} if tool == "set_exterior" else None
    # fix round after P4b: a set_exterior changes a vision finding's target only through a slot of its cause
    out |= {f.get("target") for f in targets if f.get("target") is not None
            and (override is None or f.get("source") != "vision"
                 or CS.override_touches(f.get("cause") if f.get("cause") in CS.CAUSE_TOOLS else CS.cause_of(f),
                                        override))}
    if tool == "set_lighting" and args.get("room_id"):
        out |= {f.get("target") for f in findings or [] if f.get("room_id") == args["room_id"]
                and str(f.get("check")) in CS.LIGHTING_CHECKS and f.get("target") is not None}
    if CS.is_building_wide(tool, args):
        out.add(BUILDING)
    return {t for t in out if t}


def _too_many(ctx: ToolContext, tool: str, args: dict) -> Optional[dict]:
    """The refusal of an edit on a target that used its ``max_tries`` this round, else None (the try is counted).
    Fix round after P5: the refusal closes every checklist step on the target (``step_closed``,
    ``max_tries_target``) and says that every further edit of it is refused until the next round (P5's r2-s13 sent
    the same move six times after it)."""
    target = _target(tool, args)
    with ctx.lock:
        ctx.tries[target] = ctx.tries.get(target, 0) + 1
        if ctx.tries[target] > ctx.max_tries:
            why = f"max_tries: {target} was edited {ctx.max_tries} times in this round"
            return _result(False, [why], tool=tool, step_closed=True, closed_why=why, max_tries_target=target,
                           message=f"refused without validation: {target} was edited {ctx.max_tries} times in this "
                                   f"round, so every further edit of {target} is refused until the next round (the "
                                   f"same edit again changes nothing). Its checklist steps are closed: go on with "
                                   f"another target, or call finish")
    return None


# Fix round after P5: result flags of an edit refused before any validator ran (max tries, the memory, the code's
# fix_fixture search, a frozen camera)
UNVALIDATED_FLAGS = ("max_tries_target", "refused_by_memory", "no_spot", "frozen")


def refused_unvalidated(result: Optional[dict]) -> bool:
    """Fix round after P5: an edit result refused without validation (``UNVALIDATED_FLAGS``); the loop ends a
    session after ``loop.REFUSALS_END_SESSION`` of them in a row on already-refused targets."""
    return isinstance(result, dict) and not result.get("accepted") and any(result.get(k) for k in UNVALIDATED_FLAGS)


def acceptance_record(verdict: dict) -> dict:
    """An edit result's ``acceptance``: the loop's verdict without its finding list, with the dry re-check's fit record
    compact (fix round after P6b: ``{"overlaid", "refit"}``, at most 8 refit ids; the log keeps it)."""
    out = {k: v for k, v in verdict.items() if k not in ("after_findings", "fitted")}
    if isinstance(verdict.get("fitted"), dict):
        out["fitted"] = {"overlaid": verdict["fitted"].get("overlaid"),
                         "refit": list(verdict["fitted"].get("refit") or [])[:8]}
    return out


def apply_verdict(ctx: ToolContext, verdict: Optional[dict]) -> None:
    """An accepted edit's acceptance verdict (call under ``ctx.lock``): its finding list becomes the round's
    (``ctx.findings``) and, fix round after P5, the ids it changed join ``ctx.round_changed``."""
    if not isinstance(verdict, dict):
        return
    if isinstance(verdict.get("after_findings"), list):
        ctx.findings = list(verdict["after_findings"])
    ctx.round_changed |= {str(t) for t in verdict.get("changed") or [] if t}


def edit_room(ctx: ToolContext, args: dict) -> str:
    """The room an edit belongs to (memory key): its room, its piece's room, its group's room, its view's room, else
    ``building``."""
    if args.get("room_id"):
        return str(args["room_id"])
    for key in ("piece_id", "view_id"):
        room = ctx.room_of(args.get(key))
        if room:
            return room
    gid = args.get("group_id")
    if gid:
        for f in ctx.building.get("furniture") or []:
            if (f.get("group") or {}).get("group_id") == gid:
                return str(f.get("room_id"))
    return "building"


def _result(accepted: bool, failed: list, *, before=None, after=None, overrides_id=None, rerun_from=None,
            message: str = "", changed_ids=None, tool: str = "", **extra) -> dict:
    out = {"accepted": bool(accepted), "failed_checks": [str(f) for f in failed or []],
           "score_before": before, "score_after": after, "overrides_id": overrides_id,
           "rerun_from": rerun_from if accepted else None, "message": message,
           "changed_ids": list(changed_ids or [])}
    out.update(extra)
    return out


def _accept(ctx: ToolContext, tool: str, args: dict, result: dict) -> dict:
    if ctx.overrides is not None:
        result["overrides_id"] = ctx.overrides.add(ctx.round, tool, args, result, ctx.model_id)
    with ctx.lock:
        ctx.accepted.append({"tool": tool, "args": copy.deepcopy(args), "result": result})
    return result


def _reject(ctx: ToolContext, tool: str, args: dict, result: dict) -> dict:
    with ctx.lock:
        ctx.rejected.append({"tool": tool, "args": args, "result": result})
    return result


def _next_log_seq(ctx: ToolContext) -> int:
    """The ``log_seq`` of an edit: the seq its log event will get. Fix round after P3 (16-17 Oct 2026): reserved in
    the log (``AgentLog.reserve``) and used by the loop's ``log_edit`` for the edit's event; before, it was predicted
    with ``next_seq()`` and a parallel session's event took that seq first (7 of 39 P3 edits off by 1-2)."""
    if ctx.log is None:
        return 0
    reserve = getattr(ctx.log, "reserve", None)
    return int(reserve()) if callable(reserve) else int(ctx.log.next_seq())


def _building_edit(ctx: ToolContext, tool: str, args: dict, edit: dict, run: Callable[[dict], dict],
                   default_rerun: str) -> dict:
    """The shared part of a furniture or level edit: before image, validation (``run(building) -> apply_edit
    result``) and, when accepted, the new building with its decor synced (B3), the after image and the room's group
    checks now (§5.3: failed checks with numbers)."""
    room_id = edit_room(ctx, args)
    room_id = room_id if ctx.room(room_id) is not None else None
    before_png = ctx.topdown(room_id, what=f"{tool}_before") if room_id else None
    verdict = None
    with ctx.lock:
        try:
            res = run(ctx.building)
        except NotImplementedError as exc:
            out = _result(False, ["validator_unavailable"], message=f"the edit validator is not built yet ({exc})",
                          tool=tool)
            return _reject(ctx, tool, args, out)
        accepted = bool(res.get("accepted")) and isinstance(res.get("building"), dict)
        if accepted and ctx.acceptance is not None:
            # Milestone 13: the finding it targets must be gone in the dry re-check (module docstring)
            verdict = ctx.acceptance(ctx, tool, args, res, res["building"]) or {}
            accepted = bool(verdict.get("accepted"))
        if accepted:
            ctx.building = ctx.sync_fn()(res["building"])
            apply_verdict(ctx, verdict)
    failed = list(res.get("failed_checks") or ([] if accepted else ["rejected"]))
    message = str(res.get("message") or "")
    if verdict is not None and not accepted:
        failed = [f"acceptance: {verdict.get('reason')}"]
        message = f"{tool} rejected by the dry re-check: {verdict.get('reason')}"
    elif verdict is not None:
        message = (message + "; " if message else "") + str(verdict.get("reason") or "")
    out = _result(accepted, failed, before=res.get("score_before"), after=res.get("score_after"),
                  rerun_from=res.get("rerun_from") or default_rerun, message=message,
                  changed_ids=res.get("changed_ids"), log_seq=edit["log_seq"],
                  # the second condition is decided on the unfloored penalty (a score floored at 0 hides gains)
                  penalty_before=res.get("penalty_before"), penalty_after=res.get("penalty_after"))
    if verdict is not None:
        out["acceptance"] = acceptance_record(verdict)        # fix round after P6b: with the dry fit's record
    if before_png is not None:
        out["before_image"] = ctx.rel(before_png)
    if room_id:
        out["room_checks_now"] = ctx.group_checks_of(room_id)
    if not accepted:
        return _reject(ctx, tool, args, out)
    after_png = ctx.topdown(room_id, what=f"{tool}_after") if room_id else None
    if after_png is not None:
        out["after_image"] = ctx.rel(after_png)
    if tool == "relayout_room" and args.get("candidate") and ctx.memory is not None and room_id:
        ctx.memory.tried(room_id, int(args["candidate"]))
    return _accept(ctx, tool, args, out)


def no_spot_of(ctx: ToolContext, piece_id: Optional[str]) -> Optional[str]:
    """Fix round after P4b (module docstring): why the code's own ``fix_fixture`` search found no spot for
    ``piece_id``: this session's result, else an earlier round's rejection in the memory; None when it did not run
    or found one."""
    if not piece_id:
        return None
    seen = ctx.session().no_spot.get(str(piece_id))
    if seen:
        return seen
    if ctx.memory is not None and hasattr(ctx.memory, "no_spot"):
        hit = ctx.memory.no_spot(edit_room(ctx, {"piece_id": piece_id})).get(str(piece_id))
        if hit:
            return f"{hit['reason']} (round {hit['round']})"
    return None


def no_spot_refusal(ctx: ToolContext, args: dict) -> Optional[dict]:
    """Fix round after P4b: the refusal of a ``fix_fixture`` without a new ``size`` on a piece the code's search
    found no spot for (``no_spot_of``); counted as a try of the piece; it closes the step. None otherwise."""
    if args.get("size") is not None:
        return None                      # a real product size is another search (edit_ops decides)
    why = no_spot_of(ctx, args.get("piece_id"))
    if why is None:
        return None
    target = _target("fix_fixture", args)
    with ctx.lock:
        ctx.tries[target] = ctx.tries.get(target, 0) + 1
    return _result(False, [f"no_spot: {args.get('piece_id')}: the code searched every spot within 0.5 m and found "
                           f"none ({why[:200]}); do not try centres: the finding stays for review"],
                   message="refused without validation: no valid spot exists within 0.5 m (searched by the code); "
                           "do not try centres. Its checklist step is closed: go on with the next step, or call "
                           "finish", tool="fix_fixture", no_spot=True, step_closed=True,
                   closed_why="the code found no valid spot within 0.5 m")


def note_no_spot(ctx: ToolContext, args: dict, res: dict) -> None:
    """Fix round after P4b: a ``fix_fixture`` without ``center`` and ``size`` whose search found no valid spot is
    remembered for the session (``SessionState.no_spot``) and closes its step."""
    if args.get("center") is not None or args.get("size") is not None or res.get("accepted"):
        return
    hit = next((str(f) for f in res.get("failed_checks") or [] if NO_SPOT_PREFIX in str(f)), None)
    if hit is None:
        return
    ctx.session().no_spot[str(args.get("piece_id"))] = hit
    res["step_closed"] = True
    res["closed_why"] = "the code found no valid spot within 0.5 m"
    res["message"] = (str(res.get("message") or "") + "; " if res.get("message") else "") + \
        "no valid spot exists within 0.5 m: do not try centres, the finding stays for review"


def furniture_handler(tool: str) -> Callable[[ToolContext, dict], dict]:
    op = OV.FURNITURE_TOOLS[tool]

    def handler(ctx: ToolContext, args: dict) -> dict:
        refused = _too_many(ctx, tool, args)
        if refused is not None:
            return _reject(ctx, tool, args, refused)
        edit = {"op": op, **copy.deepcopy(args), "round": ctx.round, "log_seq": _next_log_seq(ctx),
                "model": ctx.model_id}
        edit = OV.resolve_edit(edit, ctx.known_ops())
        targeted = target_findings(ctx, tool, args)
        if targeted:
            # Milestone 13: the validator sees the finding (swap_model refuses an S2 cut below 0.03 m with it)
            edit["target_finding"] = finding_record(targeted[0])

        def run(building):
            catalog = ctx.catalog() if edit["op"] in CATALOG_OPS else None
            return ctx.edit_fn()(building, edit, catalog=catalog)
        out = _building_edit(ctx, tool, args, edit, run, "refit")
        if tool == "swap_model":
            # fix round after P4b (module docstring): a swap keeps the footprint
            piece = ctx.piece(args.get("piece_id") or "") or {}
            size = (piece.get("footprint") or {}).get("size") or []
            if len(size) >= 2:
                out["footprint_kept"] = (f"the footprint {float(size[0]):.2f} x {float(size[1]):.2f} m is kept; the "
                                         f"model is fitted to its width, so a swap does not change a wall cut across "
                                         f"the width and changes one across the depth by a few cm at most")
        return out

    return handler


def finding_record(f: dict) -> dict:
    """The compact finding an edit carries to the validator: check, target, severity, message, metrics, cause."""
    return {"check": f.get("check"), "target": f.get("target"), "severity": f.get("severity"),
            "message": str(f.get("message") or "")[:200], "metrics": dict(CS._metrics(f)),
            "cause": f.get("cause") or CS.cause_of(f)}


def level_handler(tool: str) -> Callable[[ToolContext, dict], dict]:
    """Milestone 12 (§3.6): a level edit through ``levels.edits.apply_level_edit`` (track L); re-run from build."""
    def handler(ctx: ToolContext, args: dict) -> dict:
        refused = _too_many(ctx, tool, args)
        if refused is not None:
            return _reject(ctx, tool, args, refused)
        edit = {"op": tool, **copy.deepcopy(args), "round": ctx.round, "log_seq": _next_log_seq(ctx),
                "model": ctx.model_id}
        return _building_edit(ctx, tool, args, edit, lambda b: ctx.level_fn()(b, edit), "build")
    return handler


def t_report_library_gap(ctx: ToolContext, args: dict) -> dict:
    """Milestone 12 (§6.4): record-only; the gap goes to ``agent_overrides.library_gaps`` and the report."""
    out = _result(True, [], message=f"library gap recorded: {args['type']} {args.get('style') or ''}".strip(),
                  log_seq=_next_log_seq(ctx), applied=False)
    return _accept(ctx, "report_library_gap", args, out)


def _validator_result(ctx: ToolContext, tool: str, args: dict, check: Callable[[], dict], stage: str,
                      trial: Optional[Callable[[], Optional[dict]]] = None) -> dict:
    """An override edit: the try budget, the validator's verdict, then (Milestone 13) the acceptance on the building
    ``trial()`` returns (the building with the override applied; the building itself when the override lives outside
    it, ``trial`` None or returning None).

    Review of 16 Oct 2026: ``trial`` is called under ``ctx.lock``, right before the acceptance, so it starts from the
    building as the parallel room sessions left it (a copy taken before the lock missed an edit another session was
    accepting, and its dry re-check showed that session's removed finding as new); and an accepted override that
    lives in the building (``agent_overrides``: set_lighting, set_exterior) is written into ``ctx.building`` at once,
    so the later edits of the round are re-checked with it (before, an accepted roof override was missing from every
    later trial and its X2 finding came back as a new critical one). ``ctx.building`` is never written to disk;
    ``building_agent.json`` is replayed from overrides.json (``overrides.apply``)."""
    refused = _too_many(ctx, tool, args)
    if refused is not None:
        ctx.rejected.append({"tool": tool, "args": args, "result": refused})
        return refused
    try:
        verdict = check() or {}
    except NotImplementedError as exc:
        out = _result(False, ["validator_unavailable"], message=f"the validator is not built yet ({exc})", tool=tool)
        ctx.rejected.append({"tool": tool, "args": args, "result": out})
        return out
    ok = bool(verdict.get("ok"))
    out = _result(ok, verdict.get("failed") or ([] if ok else ["rejected"]), rerun_from=stage,
                  message=str(verdict.get("message") or ""), log_seq=_next_log_seq(ctx),
                  changed_ids=[args.get("view_id")] if args.get("view_id") else [])
    if ok and ctx.acceptance is not None:
        with ctx.lock:
            after = trial() if trial is not None else None
            acc = ctx.acceptance(ctx, tool, args, out, after if after is not None else ctx.building) or {}
            ok = bool(acc.get("accepted"))
            if ok:
                apply_verdict(ctx, acc)
            if ok and isinstance(after, dict):
                ctx.building = dict(ctx.building, agent_overrides=copy.deepcopy(after.get("agent_overrides") or {}))
        out["acceptance"] = acceptance_record(acc)
        out["accepted"] = ok
        if not ok:
            out["failed_checks"] = [f"acceptance: {acc.get('reason')}"]
            out["message"] = f"{tool} rejected by the dry re-check: {acc.get('reason')}"
            out["rerun_from"] = None
        else:
            out["message"] = (out["message"] + "; " if out["message"] else "") + str(acc.get("reason") or "")
    if not ok:
        ctx.rejected.append({"tool": tool, "args": args, "result": out})
        return out
    return _accept(ctx, tool, args, out)


def same_pose(want: dict, have: Optional[dict]) -> bool:
    """Fix round after P4a: ``want`` (a camera override's ``position``, ``target`` and, when it names one,
    ``lens_mm``) is the pose ``have`` has already, within ``POSE_TOLERANCE_M`` / ``LENS_TOLERANCE_MM``."""
    if not isinstance(have, dict):
        return False
    try:
        for k in ("position", "target"):
            a, b = want.get(k), have.get(k)
            if not a or not b or len(a) != len(b) or \
                    any(abs(float(x) - float(y)) > POSE_TOLERANCE_M + 1e-9 for x, y in zip(a, b)):
                return False
        if want.get("lens_mm") is not None:
            if have.get("lens_mm") is None or \
                    abs(float(want["lens_mm"]) - float(have["lens_mm"])) > LENS_TOLERANCE_MM + 1e-9:
                return False
    except (TypeError, ValueError):
        return False
    return True


def camera_pose_now(ctx: ToolContext, view_id: str) -> tuple[Optional[dict], str]:
    """Fix round after P4a: ``(pose, where)`` the next build gives ``view_id``: its last accepted ``set`` / ``add``
    override (``overrides.json``, the accepted edits after the scheduler's rollbacks; without it the building's
    ``agent_overrides.cameras``; a later ``remove`` clears it), else its scene camera; ``(None, "")`` without
    either."""
    if ctx.overrides is not None:
        source = ctx.overrides.agent_overrides()
    else:
        source = ctx.building.get("agent_overrides") if isinstance(ctx.building.get("agent_overrides"), dict) else {}
    entries = [e for e in source.get("cameras") or [] if isinstance(e, dict)]
    last = None
    for e in entries:
        if e.get("view_id") != view_id:
            continue
        last = e if e.get("action") in ("set", "add") else None
    if last is not None:
        return last, f"the accepted override (overrides.json seq {last.get('seq')})"
    cam = ctx.camera(view_id)
    return (cam, "its camera in the scene manifest") if cam is not None else (None, "")


def entrance_of(building: dict, camera: dict) -> Optional[dict]:
    """Fix round after P4b: the entrance record (``site.entrances``: ``door_id``, ``face`` or ``centre``,
    ``outward``) an entrance view frames: the camera's own ``entrance`` door, else the main entrance, else the one
    nearest the camera's target; None without entrances."""
    recs = [r for r in ((building.get("site") or {}).get("entrances") or [])
            if isinstance(r, dict) and r.get("outward") and (r.get("face") or r.get("centre"))]
    if not recs:
        return None
    door = camera.get("entrance") or camera.get("door_id")
    rec = next((r for r in recs if door and r.get("door_id") == door), None) or \
        next((r for r in recs if r.get("main")), None)
    if rec is None:
        aim = camera.get("target") or camera.get("position") or [0.0, 0.0]
        rec = min(recs, key=lambda r: math.dist([float(v) for v in (r.get("face") or r["centre"])[:2]],
                                                [float(v) for v in aim[:2]]))
    return rec


def entrance_problem(building: dict, camera: dict, position, target, lens_mm=None) -> Optional[str]:
    """Fix round after P4b (module docstring, decision 2): why the pose ``position`` -> ``target`` is no longer the
    entrance view of ``camera``; None when it still is, or without an entrance record. Integration of the fix round:
    the rule is ``exterior_checks.entrance_view_problem`` (the same function as X6 and the build's view check; at
    most ``ENTRANCE_VIEW_MAX_M`` from the door face, within ``ENTRANCE_VIEW_MAX_DEG`` of the door's axis seen from the
    door, the door in the frame of ``lens_mm``): the look-direction rule refused the planner's own entrance pose,
    which ``exterior.frame_fixed`` turns 42 degrees off the axis on real03."""
    from wenart.blender import exterior_checks as X

    return X.entrance_view_problem(entrance_of(building, camera), position, target,
                                   lens_mm or camera.get("lens_mm"))


def frontal_problem(building: dict, camera: dict, position, target) -> Optional[str]:
    """Fix round after P4b (module docstring, decision 2): why the pose is no longer the frontal view of ``camera``
    (``build.agent_exterior_view``, the build's own rule: square, within 30 degrees, to the facade of its first
    side); None when it still is."""
    from wenart.blender import build as B
    from wenart.blender import site as S

    if not camera.get("sides"):
        return None                      # no facade to be square to: nothing to judge
    north, src = S.north_deg(building)
    plan = copy.deepcopy(dict(camera, position=list(position), target=list(target)))
    change = B.agent_exterior_view(plan, (0.0, 0.0), north, not str(src).startswith("assumed"))
    if change is None:
        return None
    sides = ", ".join(change.get("sides_was") or []) or "its"
    return (f"the pose no longer looks square (within {B.AGENT_FRONTAL_MAX_DEG:g} degrees) at the {sides} facade")


def planner_view(camera: Optional[dict]) -> tuple[Optional[str], list]:
    """Pass before P5, round 2 (module docstring): ``(view, sides)`` of the planner's record the next build re-applies
    the agent's overrides to: ``agent.view_was`` / ``agent.sides_was`` when ``camera`` carries them (an earlier
    build's relabel, ``build.agent_exterior_view``: the build plans the camera again and ``overrides.fixed_plan``
    copies the planner's view and sides), else the camera's own ``view`` and ``sides``."""
    if not isinstance(camera, dict):
        return None, []
    was = camera.get("agent") if isinstance(camera.get("agent"), dict) else {}
    if was.get("view_was"):
        return was["view_was"], list(was.get("sides_was") or [])
    return camera.get("view"), list(camera.get("sides") or [])


def next_view(ctx: ToolContext, name: str, pose: dict) -> tuple[Optional[str], dict]:
    """Pass before P5, round 2 (module docstring): ``(view, plan)`` the next build gives the exterior camera ``name``
    at ``pose`` (an override entry or a pose with ``position``, ``target`` and ``lens_mm``): the planner's view and
    sides (``planner_view``; ``agent`` for a new view) and the flags ``overrides.fixed_plan`` copies
    (``overrides.CAMERA_KEEP_KEYS``; the aerial flags an earlier build dropped, ``agent.flags_was``, are the planner's
    again), checked by ``build.agent_exterior_view`` on that pose as the build checks them."""
    from wenart.blender import overrides as BO

    cam = ctx.camera(name)
    base = cam if isinstance(cam, dict) else {}
    view, sides = planner_view(base)
    plan = {"name": str(name), "view": view or "agent", "sides": sides,
            "position": [float(v) for v in pose["position"]], "target": [float(v) for v in pose["target"]],
            "lens_mm": float(pose.get("lens_mm") or base.get("lens_mm") or 26.0)}
    was = base.get("agent") if isinstance(base.get("agent"), dict) else {}
    for key in BO.CAMERA_KEEP_KEYS:
        if key in pose:
            plan[key] = pose[key]
        elif key in base and base[key] is not None:
            plan[key] = base[key]
        elif key in (was.get("flags_was") or {}):
            plan[key] = was["flags_was"][key]
    if base.get("door_id"):
        plan["door_id"] = base["door_id"]
    try:
        from wenart.blender import build as B
        from wenart.blender import site as S
        north, src = S.north_deg(ctx.building)
        B.agent_exterior_view(plan, (0.0, 0.0), north, not str(src).startswith("assumed"),
                              (ctx.building.get("site") or {}).get("entrances"))
    except (KeyError, TypeError, ValueError, IndexError):
        pass                                 # the copied view stays (the build's check cannot be made)
    return plan.get("view"), plan


def built_view(ctx: ToolContext, name: str) -> tuple[Optional[str], Optional[dict]]:
    """Pass before P5 (module docstring): ``(view, pose)`` the next build gives the exterior camera ``name``: its
    pose now (``camera_pose_now``); the scene camera's own ``view`` when that pose is the scene's, else the view
    ``build.agent_exterior_view`` records for the accepted override's pose (``next_view``: the planner's view and
    sides, as ``overrides.fixed_plan`` copies them, ``agent.view_was`` / ``sides_was`` of a scene camera an earlier
    build relabelled; ``agent`` for a new view). ``(None, None)`` without a pose."""
    pose, _where = camera_pose_now(ctx, name)
    cam = ctx.camera(name)
    if not isinstance(pose, dict) or not pose.get("position") or not pose.get("target"):
        return None, None
    if pose is cam:
        return cam.get("view"), cam
    return next_view(ctx, name, pose)


def exterior_of(ctx: ToolContext) -> dict:
    """Fix round after P6a, part 2 (module docstring): ``{"prep", "model", "ridge"}`` of ``ctx.building``: the build's
    plan (``exterior_checks._prep``), its exterior model (``exterior_checks.exterior_model``, made on first use) and
    the roof's ridge (``critic_vision.high_view_line``), cached on the context (the building does not change within a
    context's checks; an accepted edit's building is a new context next round)."""
    from wenart.agent import critic_vision as CV
    from wenart.blender import exterior_checks as X

    with ctx.lock:
        if ctx._exterior is None or ctx._exterior.get("building") is not ctx.building:
            prep = X._prep(ctx.building) if isinstance(ctx.building, dict) else None
            line = CV.high_view_line(prep=prep) if isinstance(prep, dict) else None
            ctx._exterior = {"building": ctx.building, "prep": prep, "ridge": line[0] if line else None,
                             "model": None, "made": False}
        return ctx._exterior


def exterior_model_of(ctx: ToolContext):
    """Fix round after P6a, part 2: the build's exterior model of ``ctx.building`` (``exterior_of``), None when it
    cannot be made."""
    from wenart.blender import exterior_checks as X

    ext = exterior_of(ctx)
    with ctx.lock:
        if not ext["made"]:
            ext["model"] = X.exterior_model(ext["prep"]) if isinstance(ext["prep"], dict) else None
            ext["made"] = True
        return ext["model"]


def x6_frontal_of(ctx: ToolContext, camera: Optional[dict], main: Optional[dict]) -> bool:
    """Fix round after P6a, part 2 (module docstring): ``camera`` (a scene camera or a next-build plan) is X6's frontal
    view by X6's own rule (``exterior_checks.x6_frontal``, = ``critic_vision.x6_frontal`` with a building): its view
    is ``frontal``, or an ``elevation`` / ``agent`` view square to the main facade that frames the whole building with
    the sky, its frame the record's or measured on ``ctx.building``'s exterior model; a frame that cannot be measured
    keeps the pose rule."""
    from wenart.blender import exterior_checks as X

    if not isinstance(camera, dict):
        return False
    try:
        return bool(X.x6_frontal(camera, main, model=lambda: exterior_model_of(ctx), ridge=exterior_of(ctx)["ridge"]))
    except (KeyError, TypeError, ValueError, IndexError):
        return False


def x6_frontal_now(ctx: ToolContext, name: str, main: Optional[dict]) -> bool:
    """Pass before P5: the camera ``name`` is the frontal view X6 asks for at the pose and view the next build gives
    it (``built_view``, ``critic_vision.x6_frontal``). Fix round after P6a, part 2: with its frame measured on
    ``ctx.building`` (``x6_frontal_of``)."""
    view, pose = built_view(ctx, name)
    return pose is not None and x6_frontal_of(ctx, dict(pose, view=view), main)


def frontal_pose_problem(ctx: ToolContext, view_id: str, entry: dict, main: Optional[dict]) -> Optional[str]:
    """Pass before P5, round 2 (module docstring): why the ``set`` / ``add`` pose ``entry`` of X6's frontal view
    ``view_id`` would leave X6 without a frontal view: the next build's label of that pose (``next_view``) is not
    X6's frontal view (``critic_vision.x6_frontal``: a corner the build keeps, or a pose not square to the main
    facade) and no other camera stays X6's frontal view (``exterior_poses``, ``x6_frontal_now``); None otherwise.
    Fix round after P6a, part 2: X6's frontal view with its frame measured (``x6_frontal_of``)."""
    from wenart.blender import build as B
    from wenart.blender import site as S

    view, plan = next_view(ctx, view_id, entry)
    if x6_frontal_of(ctx, dict(plan, view=view), main):         # fix round after P6a, part 2: the frame measured
        return None
    if any(x6_frontal_now(ctx, n, main) for n in exterior_poses(ctx) if n != str(view_id)):
        return None                          # another camera stays X6's frontal view
    axis = (main or {}).get("axis")
    if view == "corner" and main:
        sides = [str(x) for x in plan.get("sides") or []]
        north, _src = S.north_deg(ctx.building)
        md = main["direction"]
        normals = {x: S.side_direction(x, north) for x in sides}
        other = [x for x, n in normals.items() if n is None or n[0] * md[0] + n[1] * md[1] < 0.99] or sides
        return (f"the next build keeps this pose the corner view of {', '.join(sides)} (it looks at each of those "
                f"facades less than {B.AGENT_CORNER_MAX_DEG:g} degrees off square), and X6 counts no corner view as "
                f"the frontal view of the main ({axis}) entrance facade: look square (within "
                f"{B.AGENT_FRONTAL_MAX_DEG:g} degrees) at that facade and at least {B.AGENT_CORNER_MAX_DEG:g} degrees "
                f"off square at the {', '.join(other)} facade")
    base_view, base_sides = planner_view(ctx.camera(view_id))
    if base_view in FRONTAL_VIEWS or not main:
        why = frontal_problem(ctx.building, dict(ctx.camera(view_id) or {}, view=base_view, sides=base_sides),
                              entry["position"], entry["target"])
        if why is not None:
            return why
    return (f"the pose no longer looks square (within {B.AGENT_FRONTAL_MAX_DEG:g} degrees) at the main ({axis}) "
            f"entrance facade, the frontal view X6 asks for")


AERIAL_ROLE_SOURCE = "docs/milestone13.md D8 and the site view rule"


def aerial_problem(ctx: ToolContext, view_id: str, entry: dict) -> Optional[str]:
    """Pass before P5, round 2 (module docstring): why the ``set`` / ``add`` pose ``entry`` would bring the aerial
    or site view the camera policy allows down to eye level: the next build would no longer label it ``aerial`` /
    ``site`` (``next_view``; ``build.agent_exterior_view``: it looks down less than ``AGENT_AERIAL_MIN_DOWN_DEG``) and
    would drop its ``aerial_allowed`` / ``site_view``; None while the pose stays an aerial one. Review of round 2: or
    the pose stands below the high-view line of the camera validator and code X6 (``critic_vision.high_view_line``:
    ``ridge_z`` + 1.0 m), where they judge it as an eye-level view. The reason states both rules."""
    from wenart.agent import critic_vision as CV
    from wenart.blender import build as B

    view, _plan = next_view(ctx, view_id, entry)
    ridge, line = CV.high_view_line(ctx.building)
    z = float(entry["position"][2])
    low = z < line                           # = validate_camera_override / _x6: below the line an eye-level view
    level = view not in B.AGENT_AERIAL_VIEWS
    if not low and not level:
        return None
    parts = []
    if low:
        parts.append(f"stands at z {z:.2f} m, below that line (the camera validator and code X6 judge it as an "
                     f"eye-level view)")
    if level:
        down = round(B._down_pitch_deg(entry["position"], entry["target"]), 1) + 0.0      # never "-0.0"
        parts.append(f"looks {down:.1f} degrees down, less than the {B.AGENT_AERIAL_MIN_DOWN_DEG:g} degrees (the "
                     f"next build would make it an eye-level view)")
    return (f"an aerial view stands at least {CV.HIGH_VIEW_ABOVE_RIDGE_M:g} m above the ridge (z {line:.2f} m or "
            f"more; the ridge is at {ridge:.2f} m) and looks down at least {B.AGENT_AERIAL_MIN_DOWN_DEG:g} degrees; "
            f"this pose {' and '.join(parts)}; its height above eye level and its downward pitch are by design, not "
            f"a finding")


def aerial_role(camera: Optional[dict], view: Optional[str]) -> Optional[str]:
    """Pass before P5, round 2: ``site view`` / ``aerial view`` for a camera (as the next build gives it) of view
    ``aerial`` / ``site`` with ``site_view`` / ``aerial_allowed`` (the views the camera policy allows above eye
    level, ``build.AGENT_AERIAL_FLAGS``), else None."""
    from wenart.blender import build as B

    if not isinstance(camera, dict) or view not in B.AGENT_AERIAL_VIEWS:
        return None
    if camera.get("site_view"):
        return "site view"
    return "aerial view" if camera.get("aerial_allowed") else None


def added_camera(ctx: ToolContext, view_id: str) -> Optional[dict]:
    """Pass before P5, round 2, review (module docstring): the record ``role_problem`` judges for an exterior camera
    added in this session: ``{"name", "kind": "exterior", "room_id": None}`` when the scene manifest has no camera
    ``view_id`` and its last accepted ``set`` / ``add`` entry (``camera_pose_now``; a later ``remove`` clears it) is
    an exterior one; None otherwise. It carries no view: ``next_view`` gives it the label the build gives a new view
    (``agent``, then ``build.agent_exterior_view`` on its pose)."""
    if ctx.camera(view_id) is not None:
        return None
    pose, _where = camera_pose_now(ctx, view_id)
    if not isinstance(pose, dict) or pose.get("kind") != "exterior":
        return None
    return {"name": str(view_id), "kind": "exterior", "room_id": None}


def room_views(ctx: ToolContext, room_id: str) -> list[str]:
    """Fix round after P5 (22 Oct 2026), review: the names of the interior views of ``room_id`` the next build
    makes: the scene's interior cameras and this session's accepted interior ``add`` entries, each in the room of its
    last accepted ``set`` / ``add`` entry (else its scene camera's), less those whose last accepted entry is a
    ``remove`` (the same sources as ``exterior_poses``)."""
    if ctx.overrides is not None:
        source = ctx.overrides.agent_overrides()
    else:
        source = ctx.building.get("agent_overrides") if isinstance(ctx.building.get("agent_overrides"), dict) else {}
    last: dict = {}
    for e in source.get("cameras") or []:
        if isinstance(e, dict) and e.get("view_id") is not None:
            last[str(e["view_id"])] = e
    rooms = {str(c.get("name")): c.get("room_id") for c in ctx.cameras()
             if (c.get("kind") or ("exterior" if not c.get("room_id") else "interior")) == "interior"}
    for name, e in last.items():
        if e.get("action") in ("set", "add") and e.get("kind", "interior") == "interior" and e.get("room_id"):
            rooms[name] = e["room_id"]
    return sorted(n for n, r in rooms.items()
                  if str(r) == str(room_id) and (last.get(n) or {}).get("action") != "remove")


def only_room_view_problem(ctx: ToolContext, view_id: str, cam: dict) -> Optional[str]:
    """Fix round after P5 (22 Oct 2026), review: why removing the interior view ``view_id`` would leave its room
    without a view (no other view of it in ``room_views``), else None. Why: the critical ``camera_blocked`` goes to
    ``set_camera`` and ``remove_camera``; on P5 real04 cam_r_L1_banyo_1 is the bathroom's only view, so once its
    moves were refused the dry re-check accepted ``remove_camera`` ("finding gone") and the room lost its render,
    which the render test (every room with something to show has a view) fails."""
    room = cam.get("room_id")
    if not room or [n for n in room_views(ctx, room) if n != str(view_id)]:
        return None
    return (f"role: {view_id} is the only view of {room} (every room with something to show keeps a view: the camera "
            f"policy and the render test): it is not removed; set_camera moves it to a free point of the room")


def role_problem(ctx: ToolContext, action: str, view_id: str, entry: dict) -> Optional[str]:
    """Fix round after P4b (module docstring, decision 2): why a camera edit would lose the view's role: a ``set`` /
    ``add`` that turns a frontal view into another pose or moves an entrance view away from its door, a ``remove`` of
    the only frontal or entrance view; None otherwise. Pass before P5: an ``agent`` view that is X6's frontal view
    (``x6_frontal_now``) has the frontal role too: its pose stays square (within 30 degrees) to the main facade, and
    a frontal view by X6's rule is removed only while another one stays (``exterior_poses``).

    Pass before P5, round 2 (module docstring): the role is read from the label the next build gives the camera
    (``built_view``). A ``set`` / ``add`` of X6's frontal view (by label or by pose) is refused unless the next build
    still counts the new pose as X6's frontal view (``frontal_pose_problem``: a corner the build keeps a corner is not)
    or another camera stays one. The aerial or site view the camera policy allows (``aerial_role``) is never brought
    down to eye level (``aerial_problem``); it may move to another aerial pose or be removed. Review of round 2: an
    exterior camera added in this session (``added_camera``) is guarded like a scene camera, so the frontal view the
    agent added is not added again at another pose, and the "another camera stays X6's frontal view" exception never
    rests on an unguarded camera.

    Fix round after P5 (22 Oct 2026), review: a ``remove`` of an interior view is refused while it is the only view
    of its room (``only_room_view_problem``)."""
    from wenart.agent import critic_vision as CV

    cam = ctx.camera(view_id)
    if cam is None:
        cam = added_camera(ctx, view_id)
    if isinstance(cam, dict) and action == "remove" and \
            (cam.get("kind") or ("exterior" if not cam.get("room_id") else "interior")) != "exterior":
        return only_room_view_problem(ctx, view_id, cam)
    if not isinstance(cam, dict) or (cam.get("kind") or ("exterior" if not cam.get("room_id") else "interior")) \
            != "exterior":
        return None
    built, plan = built_view(ctx, view_id)
    view = built or cam.get("view")
    main = CV.main_facade_of(ctx.scene, ctx.building)
    frontal_now = plan is not None and x6_frontal_of(ctx, dict(plan, view=view), main)   # = x6_frontal_now
    aerial = aerial_role(plan if plan is not None else cam, view)
    if view == ENTRANCE_VIEW:
        role = ENTRANCE_VIEW
    elif frontal_now or view in FRONTAL_VIEWS:
        role = "frontal"
    elif aerial:
        role = "aerial"
    else:
        return None
    if action == "remove":
        if role == "aerial":
            return None                      # removing the allowed aerial does not bring it to eye level
        others = [n for n in exterior_poses(ctx) if n != str(view_id)]
        if role == ENTRANCE_VIEW:
            same = [n for n in others if built_view(ctx, n)[0] == ENTRANCE_VIEW]
        elif frontal_now:
            same = [n for n in others if x6_frontal_now(ctx, n, main)]     # X6 still finds a frontal view
        else:                                # an elevation of another facade: any other frontal or elevation view
            same = [n for n in others if built_view(ctx, n)[0] in FRONTAL_VIEWS or x6_frontal_now(ctx, n, main)]
        if same:
            return None
        return (f"role: {view_id} is the only {role} view (the frontal view of the entrance facade X6 asks for, or "
                f"the view of the entrance door): it is not removed; add_camera with a new view id adds another view")
    if not entry.get("position") or not entry.get("target"):
        return None
    try:
        if role == ENTRANCE_VIEW:
            why = entrance_problem(ctx.building, cam, entry["position"], entry["target"], entry.get("lens_mm"))
        elif role == "aerial":
            why = aerial_problem(ctx, view_id, entry)
        elif frontal_now:
            why = frontal_pose_problem(ctx, view_id, entry, main)
        else:                                # an elevation of another facade: square to its own facade
            base_view, base_sides = planner_view(cam)
            why = frontal_problem(ctx.building, dict(cam, view=base_view, sides=base_sides), entry["position"],
                                  entry["target"])
    except (KeyError, TypeError, ValueError, IndexError):
        return None
    if why is None:
        return None
    if role == "aerial":
        return (f"role: {view_id} is the {aerial} the camera policy allows and keeps its role ({AERIAL_ROLE_SOURCE}): "
                f"{why}; add_camera with a new view id for an eye-level view")
    return (f"role: {view_id} is the {role} view and keeps its role (decision of 17 Oct 2026): {why}; add_camera "
            f"with a new view id for another view")


def eye_height_hint(ctx: ToolContext, entry: dict, failed: list) -> list:
    """Fix round after P4b (module docstring): an exterior camera refused for its eye height gets the ground z under
    it and the z to use; ``failed`` unchanged when the ground is not known. Pass before P5: the ground is
    ``critic_vision.ground_z`` on ``ctx.building``, the validator's own (the round's scene manifest only for a
    building the build makes no site of)."""
    if not any("eye height" in str(f) for f in failed or []) or not entry.get("position"):
        return failed
    from wenart.agent import critic_vision as CV
    from wenart.blender import exterior_checks as X

    x, y = (float(v) for v in entry["position"][:2])
    ground = CV.ground_z(ctx.building, ctx.scene, x, y)
    if ground is None:
        return failed
    lo, hi = (ground + v for v in X.EYE_LEVEL_RANGE_M)
    # pass before P5: "z -2.54 to -2.44", not "z -2.54--2.44" (real04's ground lies 0-4 m below zero)
    return list(failed) + [f"the ground at ({x:g}, {y:g}) is at z {ground:.2f} m: use z {lo:.2f} to {hi:.2f} for an "
                           f"eye-level view"]


FREE_STRIP_STEP_M = 0.1          # fix round after P5: the sampling step along the view line
FREE_STRIP_BEYOND_M = 10.0       # ... sampled this far beyond the refused position
FREE_STRIP_MIN_M = 1.0           # a free stretch shorter than this is not named
INSIDE_WORDS = "inside the building"


def free_strip_hint(ctx: ToolContext, entry: dict, failed: list) -> list:
    """Fix round after P5: an exterior camera refused because it stands inside a building (the main one or another
    on the plot, ``exterior_checks.validate_camera_override``) gets the free stretches of its view line, from the
    target back through the refused position (and ``FREE_STRIP_BEYOND_M`` beyond it), with the same 0.3 m margin as
    the validator; only the first free stretch is named (a building stands between any later one and the target).
    The hint says that a close view may be framed wider or tilted (the decision of 22 Oct 2026 for exterior views of
    long, low buildings; review: only for such a building, ``long_low_of``, else that the view keeps the eye-level
    lens). ``failed`` unchanged when there is nothing to name. Why: P5's add_camera ext_front_y was refused three times
    "inside the building b2" (y 28 and y 20) while the 6 m between the house (y 12) and b2 (y 18.57) was free; X6 "no
    frontal view" stayed open in all 4 rounds."""
    if not any(INSIDE_WORDS in str(f) for f in failed or []) or not entry.get("position") or not entry.get("target"):
        return failed
    from wenart import geometry as G
    from wenart.blender import copies as CP
    from wenart.blender import exterior_checks as X
    from wenart.blender import geom2d

    try:
        prep = X._prep(ctx.building) or {}
        shapes = [o for o in (prep.get("outlines") or {}).values() if len(o) >= 3]
        shapes += [fp for fp in CP.footprints(ctx.building) if len(fp) >= 3]
    except Exception:  # noqa: BLE001 - a hint only: the refusal stays as it is
        return failed
    if not shapes:
        return failed
    tx, ty = (float(v) for v in entry["target"][:2])
    px, py = (float(v) for v in entry["position"][:2])
    length = math.hypot(px - tx, py - ty)
    if length < 1e-6:
        return failed
    ux, uy = (px - tx) / length, (py - ty) / length

    def free(x: float, y: float) -> bool:
        return not any(G.point_in_polygon((x, y), o) or geom2d.distance_to_polygon_edges((x, y), o) < 0.3
                       for o in shapes)

    spans: list = []
    start = None
    steps = int((length + FREE_STRIP_BEYOND_M) / FREE_STRIP_STEP_M) + 1
    for k in range(steps + 1):
        d = k * FREE_STRIP_STEP_M
        ok = free(tx + ux * d, ty + uy * d)
        if ok and start is None:
            start = d
        if (not ok or k == steps) and start is not None:
            end = d if ok else d - FREE_STRIP_STEP_M
            if end - start >= FREE_STRIP_MIN_M:
                spans.append((start, end))
            start = None
    if not spans:
        return failed
    # only the first free stretch sees the target: a building lies between it and any later one
    a, b = spans[0]
    # fix round after P5 (22 Oct 2026), review: the wider or tilted framing is the long, low building's only
    from wenart.blender import exterior as E
    low = long_low_of(prep)
    stretch = (f"({tx + ux * a:.2f}, {ty + uy * a:.2f}) to ({tx + ux * b:.2f}, {ty + uy * b:.2f}), {a:.1f}-{b:.1f} m "
               f"from the target (a building stands beyond it)")
    # fix round after P6a, part 2 (module docstring): the stretch is named only where an eye-level view fits
    blocked = None if low else strip_frame_problem(prep, (tx, ty), (ux, uy), b, X.exterior_model)
    if blocked is not None:
        return list(failed) + [f"no eye-level view fits the free stretch on the view line from the target: {stretch}: "
                               f"{blocked}; whether this facade gets a frontal view is a user decision "
                               f"(docs/milestone13.md §14.13, decision 16): report it, add no camera in this stretch"]
    framing = ("a close view may be framed wider or tilted when the whole facade does not fit (a long, low building)"
               if low else
               f"the view keeps the {E.EYE_LENS_MM:g} mm eye-level lens, level (the wider or tilted framing is for a "
               f"long, low building only)")
    return list(failed) + [f"free on the view line from the target: {stretch}; a camera there stands at eye height "
                           f"over the ground there, and {framing}"]


def strip_frame_problem(prep: Optional[dict], target, direction, far: float, model_of: Callable) -> Optional[str]:
    """Fix round after P6a, part 2 (module docstring): why no eye-level view fits a free stretch that ends ``far``
    metres from ``target`` along ``direction``: a level ``exterior.EYE_LENS_MM`` camera at eye height over the ground
    at its far end, looking at ``target``, does not frame the whole building or shows less than
    ``exterior.SKY_MIN_SHARE`` sky (``exterior.frame_check``), with the distance the building needs
    (``exterior.fill_distance``); None when it fits with the sky, or when the build's exterior model (``model_of(prep)``)
    cannot be made (the hint then names the stretch as before)."""
    from wenart.blender import exterior as E

    try:
        model = model_of(prep) if isinstance(prep, dict) else None
        if model is None:
            return None
        tx, ty = (float(v) for v in target[:2])
        ux, uy = (float(v) for v in direction[:2])
        fx, fy = tx + ux * far, ty + uy * far
        z = E._eye(model, fx, fy)
        frame = E.frame_check(model, [fx, fy, z], [tx, ty, z], E.EYE_LENS_MM)
        if frame["fits"] and frame["sky_share"] >= E.SKY_MIN_SHARE - 1e-9:
            return None
        need, rec = E.fill_distance(model, (tx, ty), (ux, uy), (tx, ty, z), E.building_points(model), E.EYE_LENS_MM)
    except (KeyError, TypeError, ValueError, IndexError, ZeroDivisionError, FloatingPointError, AttributeError):
        return None
    parts = []
    if not frame["fits"]:
        parts.append(f"the building spans {float(frame['fill']):.2f} of the frame width (it does not fit)")
    if frame["sky_share"] < E.SKY_MIN_SHARE - 1e-9:
        parts.append(f"{float(frame['sky_share']):.0%} of its rays look up into the sky (at least "
                     f"{E.SKY_MIN_SHARE:.0%})")
    reach = (f"about {float(need):.1f} m" if rec and rec.get("fits") else f"more than {float(need):.0f} m")
    return (f"a level {E.EYE_LENS_MM:g} mm camera at eye height at its far end ({fx:.2f}, {fy:.2f}) frames no view: "
            f"{' and '.join(parts)}; a level eye-level view of the whole building stands {reach} from the target")


def long_low_of(prep: Optional[dict]) -> Optional[dict]:
    """Fix round after P5 (22 Oct 2026), review: ``exterior.long_low`` of the build's exterior model of the base
    variant (``exterior.build_model`` on ``build.prepare``'s building, roof and site, as the build makes it), None for
    any other building or when it cannot be made. Why: ``free_strip_hint`` offered the wider or tilted framing of the
    user's decision of 22 Oct 2026 to every building; it holds for long, low buildings only (real03, ratio 10.4; not
    real02 or real04, 1.5-1.7)."""
    if not isinstance(prep, dict) or not isinstance(prep.get("building"), dict):
        return None
    from wenart.blender import exterior as E

    try:
        b = prep["building"]
        return E.long_low(E.build_model(b, b.get("levels") or [], prep.get("roof"), prep.get("site")))
    except Exception:  # noqa: BLE001 - a hint only: no framing clause without the model
        return None


def _look_2d(position, target) -> Optional[tuple[float, float]]:
    """The horizontal view direction (unit) from ``position`` to ``target``, None when it looks straight down."""
    dx, dy = float(target[0]) - float(position[0]), float(target[1]) - float(position[1])
    n = math.hypot(dx, dy)
    return (dx / n, dy / n) if n > 1e-9 else None


def exterior_poses(ctx: ToolContext) -> dict[str, dict]:
    """``{name: pose}`` of the exterior cameras the next build makes (integration after P4b): the scene's exterior
    cameras and this session's accepted ``add`` entries, each at its last accepted ``set`` / ``add``
    (``camera_pose_now``); a camera whose last accepted entry is a ``remove`` is left out."""
    if ctx.overrides is not None:
        source = ctx.overrides.agent_overrides()
    else:
        source = ctx.building.get("agent_overrides") if isinstance(ctx.building.get("agent_overrides"), dict) else {}
    entries = [e for e in source.get("cameras") or [] if isinstance(e, dict)]
    last = {}
    for e in entries:
        last[str(e.get("view_id"))] = e
    names = [str(c.get("name")) for c in ctx.cameras()
             if (c.get("kind") or ("exterior" if not c.get("room_id") else "interior")) == "exterior"]
    names += [n for n, e in last.items() if e.get("kind") == "exterior" and n not in names]
    out = {}
    for name in names:
        if (last.get(name) or {}).get("action") == "remove":
            continue
        pose, _where = camera_pose_now(ctx, name)
        if isinstance(pose, dict) and pose.get("position") and pose.get("target"):
            out[name] = pose
    return out


def duplicate_view_problem(ctx: ToolContext, view_id: str, entry: dict) -> Optional[str]:
    """Integration after P4b (module docstring): why an exterior ``set`` / ``add`` pose would copy another exterior
    view (within ``DUPLICATE_VIEW_M`` and ``DUPLICATE_VIEW_DEG``), else None."""
    if entry.get("kind") != "exterior" or not entry.get("position") or not entry.get("target"):
        return None
    look = _look_2d(entry["position"], entry["target"])
    if look is None:
        return None
    for name, pose in sorted(exterior_poses(ctx).items()):
        if name == str(view_id):
            continue
        dist = math.dist([float(v) for v in entry["position"][:2]], [float(v) for v in pose["position"][:2]])
        if dist > DUPLICATE_VIEW_M + 1e-9:
            continue
        other = _look_2d(pose["position"], pose["target"])
        if other is None:
            continue
        ang = math.degrees(math.acos(max(-1.0, min(1.0, look[0] * other[0] + look[1] * other[1]))))
        if ang <= DUPLICATE_VIEW_DEG + 1e-9:
            return (f"duplicate: {view_id} would stand {dist:.1f} m from {name} and look {ang:.0f} degrees off its "
                    f"direction (within {DUPLICATE_VIEW_M:g} m and {DUPLICATE_VIEW_DEG:g} degrees it shows the same "
                    f"view): choose a pose that shows another facade or part of the site")
    return None


def camera_handler(tool: str) -> Callable[[ToolContext, dict], dict]:
    action = OV.CAMERA_TOOLS[tool]

    def handler(ctx: ToolContext, args: dict) -> dict:
        entry = dict({k: v for k, v in args.items() if k != "reason"}, action=action, reason=args.get("reason"))
        if action != "add" and ctx.camera(args["view_id"]) is None:
            out = _result(False, [f"no view {args['view_id']}"], tool=tool)
            ctx.rejected.append({"tool": tool, "args": args, "result": out})
            return out
        # fix round after P4b, decision 1: the replayed set 1 is frozen; decision 2: a view keeps its role
        refusal = None
        if CS.frozen_camera(ctx.camera(args["view_id"])):
            refusal = FROZEN_CAMERA.format(view=args["view_id"])
        else:
            refusal = role_problem(ctx, action, args["view_id"], entry)
        if refusal is None and action in ("set", "add"):
            refusal = duplicate_view_problem(ctx, args["view_id"], entry)      # integration after P4b
        if refusal is not None:
            target = str(args["view_id"])          # the view's try (an interior camera's _target is its room)
            with ctx.lock:
                ctx.tries[target] = ctx.tries.get(target, 0) + 1
            frozen = refusal.startswith("frozen")
            out = _result(False, [refusal], tool=tool, frozen=frozen,
                          message="refused: a replayed (set 1) camera is frozen" if frozen else
                          "refused: a near copy of another exterior view" if refusal.startswith("duplicate") else
                          "refused: the view keeps its role (frontal, entrance, the allowed aerial or the room's "
                          "only view)")
            ctx.rejected.append({"tool": tool, "args": args, "result": out})
            return out
        if action in ("set", "add"):
            # fix round after P4a: a pose the view has already is a no-op with the reason (module docstring)
            pose, where = camera_pose_now(ctx, args["view_id"])
            if same_pose(entry, pose):
                out = _result(False, [f"no_change: {args['view_id']} has this pose already ({where}): position "
                                      f"{entry.get('position')}, target {entry.get('target')}"
                                      + (f", lens {entry.get('lens_mm')} mm" if entry.get("lens_mm") is not None
                                         else "") + "; nothing to change"],
                              message="no-op: a camera override that changes nothing", tool=tool, no_op=True)
                ctx.rejected.append({"tool": tool, "args": args, "result": out})
                return out
        if action == "remove":
            # The camera entry of §17.3 names its kind and room: taken from the scene manifest.
            cam = ctx.camera(args["view_id"]) or {}
            entry.setdefault("kind", cam.get("kind") or ("exterior" if not cam.get("room_id") else "interior"))
            entry.setdefault("room_id", cam.get("room_id"))
        stored = {k: v for k, v in entry.items() if k != "action"}

        def check() -> dict:
            verdict = dict(ctx.checks().validate_camera_override(ctx.building, entry) or {})
            if not verdict.get("ok") and entry.get("kind") == "exterior":
                verdict["failed"] = eye_height_hint(ctx, entry, list(verdict.get("failed") or []))
                verdict["failed"] = free_strip_hint(ctx, entry, verdict["failed"])     # fix round after P5
            return verdict
        return _validator_result(ctx, tool, stored, check, "build")
    return handler


def t_set_material(ctx: ToolContext, args: dict) -> dict:
    override = {args["slot"]: args["look_id"]}
    return _validator_result(ctx, "set_material", args,
                             lambda: ctx.checks().validate_material_override(ctx.style, override), "build")


def lighting_state(ctx: ToolContext) -> dict:
    """Round 4: ``{room_id: factor}`` the next build applies: the building's ``agent_overrides.lighting`` (earlier
    rounds, ``overrides.apply``) under the accepted ``set_lighting`` edits of this run
    (``Overrides.agent_overrides``)."""
    out: dict = {}
    ov = ctx.building.get("agent_overrides") if isinstance(ctx.building.get("agent_overrides"), dict) else {}
    sources = [ov.get("lighting") or {}]
    if ctx.overrides is not None:
        sources.append(ctx.overrides.agent_overrides().get("lighting") or {})
    for src in sources:
        for rid, entry in (src.items() if isinstance(src, dict) else ()):
            try:
                out[str(rid)] = float((entry or {}).get("factor"))
            except (TypeError, ValueError, AttributeError):
                continue
    return out


def t_set_lighting(ctx: ToolContext, args: dict) -> dict:
    def check() -> dict:
        room = ctx.room(args["room_id"])
        if room is None:
            return {"ok": False, "failed": [f"no room {args['room_id']}"], "message": "unknown room"}
        factor = float(args["factor"])
        if not LIGHTING_FACTOR[0] <= factor <= LIGHTING_FACTOR[1]:
            return {"ok": False, "failed": ["factor"], "message": f"factor must lie in {LIGHTING_FACTOR}"}
        now = lighting_state(ctx).get(room["id"])
        if now is not None and abs(now - factor) < 1e-9:
            # Round 4: idempotent like set_exterior. The dry re-check counts the room's lighting_dark views as gone
            # (only a render re-meters them), so a repeated set_lighting with the factor the room has would be
            # accepted every round and re-render the room for nothing (real04's basement salon needs about x10).
            return {"ok": False, "failed": [f"no_change: {room['id']} has room lights x {factor:g} already"
                                            + (f" (the maximum, {LIGHTING_FACTOR[1]:g})"
                                               if factor >= LIGHTING_FACTOR[1] - 1e-9 else "")],
                    "message": "no-op: set_lighting with the factor the room has"}
        return {"ok": True, "message": f"{room['id']}: room lights x {factor:g} in the next build"}
    def trial() -> Optional[dict]:
        # review of 16 Oct 2026: the dry re-check predicts the room's dark views from the building after the edit
        # (``loop.lighting_kept``), so the trial carries the factors the next build applies with this edit's factor;
        # built under ``ctx.lock`` (``_validator_result``); the override also goes to overrides.json (``_accept``)
        try:
            rid, factor = str(args["room_id"]), float(args["factor"])
        except (KeyError, TypeError, ValueError):
            return None                      # the validator refuses the arguments with the reason
        lights = {r: {"factor": f} for r, f in lighting_state(ctx).items()}
        lights[rid] = {"factor": factor, "reason": args.get("reason")}
        out = copy.deepcopy(ctx.building)
        out["agent_overrides"] = dict(out.get("agent_overrides") or {}, lighting=lights)
        return out
    return _validator_result(ctx, "set_lighting", args, check, "build", trial=trial)


def _front_court(scene: dict) -> str:
    """The brief's ``site_options.front_court`` the build used (``scene_manifest.brief``), else ``auto``."""
    rec = ((scene or {}).get("brief") or {}).get("site_options.front_court")
    value = rec.get("value") if isinstance(rec, dict) else rec
    return value if value in ("auto", "yes", "no") else "auto"


def _site_values(site: Optional[dict], front_court: str = "auto") -> dict:
    """The site keys of ``site`` (an override's ``site`` or the building's) as the build reads them
    (``blender.overrides.site_options``: ``fence`` true is a hedge, ``trees`` true is 3); only the keys it sets."""
    from wenart.blender import overrides as BO
    if not isinstance(site, dict) or not site:
        return {}
    opts = BO.site_options({"agent_overrides": {"exterior": {"site": site}}}, front_court)
    return {k: opts[k] for k in BO.SITE_KEYS if opts["source"].get(k) == "agent"}


def exterior_state(ctx: ToolContext) -> dict:
    """What the exterior is now: the building's own roof, site and sun values under the accepted ``set_exterior``
    overrides (``Overrides.agent_overrides``), in the override's shape (``roof``, ``ground``, ``site``, ``sun``).

    Fix round after P4b (module docstring): the site is what the build makes (``blender.overrides.site_options``:
    a path, a hedge, 3 trees and the brief's front court by default; the building's own site keys on top) and the
    ground is the garden look the ground override writes (``scene_manifest.exterior_looks.garden``; the build's
    neutral ``ground`` slot is another one), so an override with those values is a no-op. P4b's ground 'grass' on the
    'grass' garden was accepted as a change."""
    from wenart.blender import overrides as BO
    b = ctx.building
    state: dict = {}
    roof = b.get("roof") if isinstance(b.get("roof"), dict) else {}
    if roof:
        state["roof"] = {k: roof.get(k) for k in ("type", "pitch_deg", "overhang_m") if roof.get(k) is not None}
    site = b.get("site") if isinstance(b.get("site"), dict) else {}
    front_court = _front_court(ctx.scene)
    defaults = BO.site_options({}, front_court)
    state["site"] = dict({k: defaults[k] for k in BO.SITE_KEYS},
                         **_site_values({k: site.get(k) for k in BO.SITE_KEYS if site.get(k) is not None},
                                        front_court))
    looks = ctx.scene.get("exterior_looks") if isinstance(ctx.scene.get("exterior_looks"), dict) else {}
    garden = (looks.get("garden") or {}).get("material") if isinstance(looks.get("garden"), dict) else None
    ground = garden or ((site.get("ground") or {}).get("look") if isinstance(site.get("ground"), dict) else None)
    if ground is not None:
        state["ground"] = ground
    sun = (ctx.scene.get("lighting") or {}).get("sun") if isinstance(ctx.scene.get("lighting"), dict) else None
    if isinstance(sun, dict):
        state["sun"] = {k: sun.get(k) for k in ("azimuth_deg", "elevation_deg") if sun.get(k) is not None}
    accepted = ((b.get("agent_overrides") or {}).get("exterior") or {}) if isinstance(b.get("agent_overrides"), dict) \
        else {}
    if ctx.overrides is not None:
        accepted = OV.merge_dict(accepted, ctx.overrides.agent_overrides().get("exterior") or {})
    return OV.merge_dict(state, normalised_override(accepted, front_court))


def normalised_override(override: dict, front_court: str = "auto") -> dict:
    """Fix round after P4b: a ``set_exterior`` override with its ``site`` as the build reads it (``_site_values``)."""
    out = dict(override or {})
    if isinstance(out.get("site"), dict):
        out["site"] = _site_values(out["site"], front_court) or dict(out["site"])
    return out


def main_facade_of(ctx: ToolContext) -> Optional[dict]:
    """The main facade ``{axis, direction}`` the build used (``scene_manifest.whole_building.main_facade``, else
    ``site.inferred.main_facade``), else ``exterior_checks._prep`` of the building; None when none is known."""
    for rec in ((ctx.scene.get("whole_building") or {}).get("main_facade"),
                ((ctx.scene.get("site") or {}).get("inferred") or {}).get("main_facade")):
        if isinstance(rec, dict) and rec.get("direction"):
            return rec
    try:
        prep = ctx.checks()._prep(ctx.building) if hasattr(ctx.checks(), "_prep") else None
    except Exception:  # noqa: BLE001 - no main facade: the azimuth is not checked here (the validator still runs)
        prep = None
    rec = (prep or {}).get("main_facade")
    return rec if isinstance(rec, dict) and rec.get("direction") else None


def sun_problems(ctx: ToolContext, sun: Optional[dict]) -> list[str]:
    """Fix round after P4b (module docstring): a sun override against the code's own X7 rule
    (``exterior_checks._x7``): the elevation within ``SUN_ELEVATION_RANGE`` (25-50 degrees), and the compass azimuth,
    turned to the building frame with ``site.north_deg`` (``lighting.building_azimuth``), on the side of the main
    facade (``main_facade_of``). Decision 4 of 17 Oct 2026: real02's assumed north stays as it is."""
    if not isinstance(sun, dict) or not sun:
        return []
    from wenart.blender import exterior_checks as X
    from wenart.blender import site as S
    out = []
    lo, hi = X.SUN_ELEVATION_RANGE
    el = sun.get("elevation_deg")
    if isinstance(el, (int, float)) and not lo - 1e-6 <= float(el) <= hi + 1e-6:
        out.append(f"sun: {float(el):g} degrees above the horizon is outside the X7 rule ({lo:g}-{hi:g} degrees)")
    az = sun.get("azimuth_deg")
    main = main_facade_of(ctx) if isinstance(az, (int, float)) else None
    if main is not None:
        north, src = S.north_deg(ctx.building)
        az_b = (float(az) - float(north)) % 360.0
        a = math.radians(az_b)
        dot = math.sin(a) * float(main["direction"][0]) + math.cos(a) * float(main["direction"][1])
        if dot <= 0.0:
            out.append(f"sun: azimuth {float(az):g} degrees (compass; {az_b:g} in the building frame, north "
                       f"{float(north):g}, {src}) lights the back: the X7 rule wants the sun on the side of the main "
                       f"({main.get('axis')}) facade")
    return out


def t_set_exterior(ctx: ToolContext, args: dict) -> dict:
    override = {k: v for k, v in args.items() if k != "reason"}
    if not override:
        return _result(False, ["nothing to change"], tool="set_exterior")
    current = exterior_state(ctx)
    if OV.merge_dict(current, normalised_override(override, _front_court(ctx.scene))) == current:
        # Milestone 13: idempotent: the same override twice (or values the building has) is a no-op with a reason
        out = _result(False, ["no_change: the exterior already has these values "
                              f"({json.dumps(override, sort_keys=True, default=str)[:200]}): nothing to change"],
                      message="no-op: set_exterior with values the building already has", tool="set_exterior",
                      no_op=True)
        return _reject(ctx, "set_exterior", args, out)
    def trial() -> dict:
        # built under ``ctx.lock`` (``_validator_result``, review of 16 Oct 2026)
        out = copy.deepcopy(ctx.building)
        out["agent_overrides"] = dict(out.get("agent_overrides") or {},
                                      exterior=OV.merge_dict((out.get("agent_overrides") or {}).get("exterior") or {},
                                                             override))
        return out

    def check() -> dict:
        # fix round after P4b: the sun against the code's own X7 rule first (module docstring)
        problems = sun_problems(ctx, override.get("sun"))
        if problems:
            return {"ok": False, "failed": problems, "message": "the sun override breaks the X7 rule"}
        return ctx.checks().validate_exterior_override(ctx.building, override)
    return _validator_result(ctx, "set_exterior", args, check, "build", trial=trial)


def t_correct_geometry(ctx: ToolContext, args: dict) -> dict:
    refused = _too_many(ctx, "correct_geometry", args)
    if refused is not None:
        ctx.rejected.append({"tool": "correct_geometry", "args": args, "result": refused})
        return refused
    verdict = GF.check(ctx.building, args)
    out = _result(verdict["ok"], verdict["failed"], rerun_from="pipeline_final", log_seq=_next_log_seq(ctx),
                  message="recorded (record-only in M11: the geometry is not changed; listed for the next full run)"
                  if verdict["ok"] else "not a clear drawing error", applied=False, metrics=verdict["metrics"])
    if not verdict["ok"]:
        ctx.rejected.append({"tool": "correct_geometry", "args": args, "result": out})
        return out
    return _accept(ctx, "correct_geometry", args, out)


def t_rerun_stage(ctx: ToolContext, args: dict) -> dict:
    from wenart.recognition.vlm_client import schema_errors
    stage, settings = args["stage"], dict(args.get("settings") or {})
    allowed = RERUN_WHITELIST.get(stage)
    failed = []
    if allowed is None:
        failed.append(f"stage {stage} is not on the white list ({', '.join(RERUN_WHITELIST)})")
    else:
        for key, value in settings.items():
            if key not in allowed:
                failed.append(f"setting {key} of {stage} is not on the white list")
            else:
                failed += [f"{key}: {e}" for e in schema_errors(allowed[key], value)]
    out = _result(not failed, failed, rerun_from=stage, log_seq=_next_log_seq(ctx),
                  message="the stage runs again with these settings" if not failed else "refused")
    if failed:
        ctx.rejected.append({"tool": "rerun_stage", "args": args, "result": out})
        return out
    return _accept(ctx, "rerun_stage", args, out)


def t_finish(ctx: ToolContext, args: dict) -> dict:
    ctx.finished = {"verdict": args["verdict"], "open_findings": list(args.get("open_findings") or [])}
    return {"ok": True, "round_ends": True}


# --------------------------------------------------------------------------
# The registry
# --------------------------------------------------------------------------

def with_reason(schema: dict) -> dict:
    """A tool's parameters: the schema without the edit meta fields (``op``, ``round``, ``log_seq``, ``model``:
    the loop sets them), plus a required ``reason``."""
    out = copy.deepcopy(schema) if schema else {"type": "object", "properties": {}}
    out.pop("$schema", None)
    out.setdefault("type", "object")
    props = out.setdefault("properties", {})
    for key in EDIT_META + ("action",):
        props.pop(key, None)
    required = [r for r in out.get("required") or [] if r not in EDIT_META + ("action",)]
    props["reason"] = dict(REASON)
    if "reason" not in required:
        required.append("reason")
    out["required"] = required
    return out


def edit_schemas() -> dict:
    """``EDIT_SCHEMAS`` of track B where filled in, else the fallbacks (module docstring)."""
    try:
        from wenart.furniture import edit_ops
        given = dict(getattr(edit_ops, "EDIT_SCHEMAS", {}) or {})
    except ImportError:
        given = {}
    return {op: given.get(op) or FALLBACK_EDIT_SCHEMAS[op] for op in FALLBACK_EDIT_SCHEMAS}


def override_schemas() -> tuple[dict, dict]:
    try:
        from wenart.blender import exterior_checks as XC
        cam = dict(getattr(XC, "CAMERA_OVERRIDE_SCHEMA", {}) or {})
        ext = dict(getattr(XC, "EXTERIOR_OVERRIDE_SCHEMA", {}) or {})
    except ImportError:
        cam, ext = {}, {}
    return cam or FALLBACK_CAMERA_SCHEMA, ext or FALLBACK_EXTERIOR_SCHEMA


READ_SCHEMAS = {
    "building_summary": _obj({"level": ID}, []),
    "room": _obj({"room_id": ID}, ["room_id"]),
    "room_topdown": _obj({"room_id": ID, "annotate": {"type": "boolean"}}, ["room_id"]),
    "plan_crop": _obj({"room_id": ID, "piece_id": ID}, []),
    "plausibility": _obj({"room_id": ID, "building": {"type": "boolean"}}, []),
    "view": _obj({"view_id": ID}, ["view_id"]),
    "exterior_summary": _obj({}, []),
    "catalog": _obj({"type": ID, "style": {"type": "string"}, "size": XY}, ["type"]),
    "stage_status": _obj({"stage": ID}, []),
    "room_brief": _obj({"room_id": ID}, ["room_id"]),
    "levels": _obj({}, []),
}
READ_SCHEMAS["room_topdown"] = _obj({"room_id": ID, "annotate": {"type": "boolean"},
                                     "candidate": {"type": "integer", "minimum": 1, "maximum": 3,
                                                   "description": "show solver candidate k instead of the room"}},
                                    ["room_id"])
READ_HANDLERS = {"building_summary": t_building_summary, "room": t_room, "room_topdown": t_room_topdown,
                 "plan_crop": t_plan_crop, "plausibility": t_plausibility, "view": t_view,
                 "exterior_summary": t_exterior_summary, "catalog": t_catalog, "stage_status": t_stage_status,
                 "room_brief": t_room_brief, "levels": t_levels}


def build_registry() -> Registry:
    tools: list[Tool] = [Tool(n, "read", DESCRIPTIONS[n], READ_SCHEMAS[n], READ_HANDLERS[n]) for n in READ_SCHEMAS]
    schemas = edit_schemas()
    for tool, op in OV.FURNITURE_TOOLS.items():
        tools.append(Tool(tool, "furniture", DESCRIPTIONS[tool], with_reason(schemas[op]), furniture_handler(tool)))
    cam_schema, ext_schema = override_schemas()
    remove_schema = _obj({"view_id": ID}, ["view_id"])
    for tool in OV.CAMERA_TOOLS:
        params = with_reason(remove_schema if tool == "remove_camera" else cam_schema)
        tools.append(Tool(tool, "override", DESCRIPTIONS[tool], params, camera_handler(tool), "build"))
    tools.append(Tool("set_material", "override", DESCRIPTIONS["set_material"], with_reason(MATERIAL_SCHEMA),
                      t_set_material, "build"))
    tools.append(Tool("set_exterior", "override", DESCRIPTIONS["set_exterior"], with_reason(ext_schema),
                      t_set_exterior, "build"))
    tools.append(Tool("set_lighting", "override", DESCRIPTIONS["set_lighting"], with_reason(LIGHTING_SCHEMA),
                      t_set_lighting, "build"))
    geometry = _obj({"kind": {"enum": list(GF.KINDS)}, "wall_ids": {"type": "array", "items": ID, "maxItems": 2},
                     "opening_id": ID, "evidence": {"type": "string", "minLength": 3}}, ["kind", "evidence"])
    tools.append(Tool("correct_geometry", "record", DESCRIPTIONS["correct_geometry"], with_reason(geometry),
                      t_correct_geometry, "pipeline_final"))
    rerun = _obj({"stage": {"enum": list(RERUN_WHITELIST)}, "settings": {"type": "object"}}, ["stage"])
    tools.append(Tool("rerun_stage", "record", DESCRIPTIONS["rerun_stage"], with_reason(rerun), t_rerun_stage))
    # Milestone 12: level edits (track L), library gaps, the free dry run
    for tool, schema in level_schemas().items():
        tools.append(Tool(tool, "level", DESCRIPTIONS[tool], with_reason(schema), level_handler(tool), "build"))
    tools.append(Tool("report_library_gap", "record", DESCRIPTIONS["report_library_gap"],
                      with_reason(LIBRARY_GAP_SCHEMA), t_report_library_gap))
    table = {t.name: t for t in tools}
    dry = _obj({"tool": {"enum": [n for n in table if table[n].kind in ("furniture", "level")]},
                "args": {"type": "object", "description": "the arguments you would send to that tool"}},
               ["tool", "args"])
    tools.append(Tool("dry_run", "control", DESCRIPTIONS["dry_run"], dry, dry_run_handler(table)))
    finish = _obj({"verdict": {"enum": ["done", "partly", "gave_up"]},
                   "open_findings": {"type": "array", "items": {"type": "string"}}}, ["verdict"])
    tools.append(Tool("finish", "control", DESCRIPTIONS["finish"], finish, t_finish))
    return Registry(tools)


def level_schemas() -> dict:
    """``LEVEL_EDIT_SCHEMAS`` of track L (contract §13.2) for every level tool."""
    try:
        from wenart.levels import edits
        given = dict(getattr(edits, "LEVEL_EDIT_SCHEMAS", {}) or {})
    except ImportError:
        given = {}
    return {op: given.get(op) or {"type": "object"} for op in OV.LEVEL_TOOLS}


def dry_run_repeat(ctx: ToolContext, name: str, inner: dict) -> Optional[dict]:
    """Fix round after P4b (module docstring): the answer to a dry run this session already sent with the same
    arguments (``memory.edit_key``) while no edit of the round was accepted in between: the first answer, marked
    ``repeat_of``, with "same as dry run #n"; counted as a try of its target (``_target``). None for a new one."""
    state = ctx.session()
    key = MEM.edit_key(name, inner)
    with ctx.lock:
        prev = state.dry_runs.get(key)
        if prev is None or prev["accepted"] != len(ctx.accepted):
            return None
        target = _target(name, inner)
        ctx.tries[target] = ctx.tries.get(target, 0) + 1
    first = prev["out"]
    reason = "; ".join(first.get("failed_checks") or []) or ("it would be accepted" if first.get("would_accept")
                                                              else "rejected")
    return dict(first, repeat_of=prev["n"], note="dry run repeated: answered from the first one, nothing was "
                                                 "validated again; counted as a try",
                message=f"same as dry run #{prev['n']} of this session: {reason[:300]}; try something else (a "
                        f"repeated dry run counts as a try of {target})")


def dry_run_handler(table: dict) -> Callable[[ToolContext, dict], dict]:
    """Milestone 12 (§5.3): the validator's answer for an edit without applying it. Free: no try is counted, nothing
    goes to the overrides or the memory; logged as a ``dry_run`` event. Fix round after P4b: a repeat in the session
    is answered from the first one and counts as a try (``dry_run_repeat``)."""
    def handler(ctx: ToolContext, args: dict) -> dict:
        from wenart.recognition.vlm_client import schema_errors
        name, inner = args["tool"], dict(args.get("args") or {})
        inner.setdefault("reason", "dry run")
        tool = table[name]
        errors = schema_errors(tool.parameters, inner)
        with ctx.lock:
            ctx.dry_runs += 1
        repeat = None if errors else dry_run_repeat(ctx, name, inner)
        if repeat is not None:
            if ctx.log is not None:
                ctx.log.event("dry_run", ctx.round, tool=name, args=inner, status="repeat",
                              note=repeat["message"][:300], room_id=edit_room(ctx, inner))
            return repeat
        if errors:
            out = {"would_accept": False, "failed_checks": [f"schema: {e}" for e in errors[:5]]}
        else:
            prev = _repeat_of(ctx, edit_room(ctx, inner), name, inner) if ctx.memory is not None else None
            if prev is not None:
                out = {"would_accept": False, "failed_checks": [f"memory: rejected in round {prev.get('round')}: "
                                                                 + "; ".join(prev.get("reasons") or [])[:300]]}
            else:
                edit = {"op": name if tool.kind == "level" else OV.FURNITURE_TOOLS[name], **inner,
                        "round": ctx.round, "log_seq": 0, "model": ctx.model_id}
                targeted = target_findings(ctx, name, inner)
                if targeted and tool.kind != "level":
                    # fix round after P5: as the real edits do: a furniture edit carries its finding to the validator,
                    # a level edit never (its schema has no target_finding: P5's dry_run set_terrain was refused
                    # "'target_finding' was unexpected" every time)
                    edit["target_finding"] = finding_record(targeted[0])
                try:
                    with ctx.lock:
                        if tool.kind == "level":
                            res = ctx.level_fn()(ctx.building, edit)
                        else:
                            edit = OV.resolve_edit(edit, ctx.known_ops())
                            catalog = ctx.catalog() if edit["op"] in CATALOG_OPS else None
                            if ctx.apply_edit is not None or ctx.acceptance is not None:
                                # Milestone 13: the acceptance needs the edited building (discarded after)
                                res = ctx.edit_fn()(ctx.building, edit, catalog=catalog)
                            else:
                                from wenart.furniture import edit_ops
                                res = edit_ops.dry_run(ctx.building, edit, catalog=catalog)
                        would = bool(res.get("accepted"))
                        failed = [str(f) for f in res.get("failed_checks") or []]
                        if would and ctx.acceptance is not None and isinstance(res.get("building"), dict):
                            acc = ctx.acceptance(ctx, name, inner, res, res["building"]) or {}
                            would = bool(acc.get("accepted"))
                            if not would:
                                failed = [f"acceptance: {acc.get('reason')}"]
                    out = {"would_accept": would, "failed_checks": failed,
                           "score_before": res.get("score_before"), "score_after": res.get("score_after"),
                           "message": str(res.get("message") or "")}
                except NotImplementedError as exc:
                    out = {"would_accept": False, "failed_checks": ["validator_unavailable"], "message": str(exc)}
        out["note"] = "dry run: nothing was applied, no try was counted"
        if not errors:
            state = ctx.session()
            with ctx.lock:
                state.dry_n += 1
                state.dry_runs[MEM.edit_key(name, inner)] = {"n": state.dry_n, "out": dict(out),
                                                             "accepted": len(ctx.accepted)}
        if ctx.log is not None:
            ctx.log.event("dry_run", ctx.round, tool=name, args=inner, status="would_accept" if out["would_accept"]
                          else "would_reject", note="; ".join(out["failed_checks"])[:300] or None,
                          room_id=edit_room(ctx, inner))
        return out
    return handler


EDIT_KINDS = ("furniture", "override", "record", "level")


def label_for(tool: str, ctx: ToolContext, args: dict) -> Optional[str]:
    """The label of an edit in the log (§9): added_by_ai, adjusted_by_ai, corrected_by_ai or agent_override."""
    if tool in ("add_piece", "add_group", "place_group", "complete_group"):
        return "added_by_ai"
    if tool == "correct_geometry" or tool in OV.LEVEL_TOOLS:
        return "corrected_by_ai"
    if tool == "report_library_gap":
        return "library_gap"
    if tool in OV.FURNITURE_TOOLS:
        piece = ctx.piece(args.get("piece_id") or "")
        if piece is not None and piece.get("source") == "added_by_ai":
            return "added_by_ai"
        return "adjusted_by_ai"
    if tool == "rerun_stage":
        return "agent_rerun"
    return "agent_override"
