"""Causes of findings, the tools per cause and the acceptance rule of an edit (docs/milestone13.md §1.5, §3.0 K4,
§13.2 rows ``loop.py`` and ``edit_ops.py``; CLAUDE.md evidence rule: "an agent edit is accepted only when the finding
it targets is gone in the dry re-check and no new critical finding appears").

What:

- ``cause_of(finding, building=None) -> str``: the cause behind a finding (``CAUSES``). The check id gives the family;
  the finding's metrics, message and target decide the rest: an F8 chair around an unbuilt table is
  ``missing_anchor`` (not ``floating``: moving the chair never helped, real04 0 of 24), an S2 cut below
  ``S2_TOLERANCE_M`` (0.03 m) is ``within_tolerance`` (invisible: 0 of 39 swaps helped), an X2 piece under the sloped
  roof is ``under_roof`` (move or lower the piece), an X2 on the roof itself is ``roof`` (building-wide).
  Round 2 of the build (15 Oct 2026): an F8 whose ``metrics.cause`` is ``anchor_not_built`` goes to the tools that
  BUILD the anchor, not to the chair's: ``anchor_untyped`` (the anchor is an ``unknown`` piece: ``retype_piece``
  types and builds it through the fit) or ``missing_anchor`` (a typed anchor the fit left unbuilt: ``place_group``
  re-solves the drawn group so the refit builds it, ``swap_model`` pins a model, ``retype_piece`` last);
  ``anchor_of(finding)`` names the anchor the edit must act on (the brief's ``edit_target``). A G8 whose
  ``metrics.tier`` names a tiered minimum (``groups.yaml`` ``tiers``: a small kitchen's aisle, a drawn run's
  landings and triangle) is ``soft_minimum``: a scored term of the solver, reported only, no tool.
- ``tools_for_finding(finding) -> [tool]``: the tools offered for the cause (``CAUSE_TOOLS``), best first; ``[]``
  when no tool fixes the cause: the finding is "not yours" in the brief (vision findings included: the critic's
  findings are offered only where a tool exists for the cause).
- ``is_building_wide(tool, args=None) -> bool``: a tool only the building session may call (the roof, site, sun,
  materials, geometry, levels, terrain and the exterior cameras); a room session is refused (real04: a corridor
  session flattened the roof of the whole building, 29 critical findings in round 5).
- ``accept_edit(before, after, edit) -> (bool, reason)``: pure. ``before`` and ``after`` are finding lists (the
  round's findings and the dry re-check after the edit); ``edit`` carries ``target_finding`` (one ``{check, target}``
  or a list of them) and may carry ``penalty_before`` / ``penalty_after`` (or ``score_before`` / ``score_after``).
  Accepted only when (1) the targeted finding is among ``before`` and gone in ``after``, (2) no critical finding is
  new in ``after`` and (round 4) no new critical or major room-set finding asks for a fixture the edit removed
  (``edit["removed"]``, see below), and (3) the old rule as a second condition: the plausibility penalty did not
  rise (the M12 rule of ``edit_ops.apply_edit`` was the only rule; 139 of 183 accepted edits left the score
  unchanged, 125 of 160 left their finding in place).
- ``findings_removed(before, after, severities=("critical", "major"))``: how many finding keys of ``before`` are
  gone in ``after`` (the success number of the loop and the metrics; "edits accepted" is none).

Round 4 of Milestone 13 (before pod P3's second attempt, 16 Oct 2026):

- ``lighting_dark`` (``wenart.blender.render.lighting_dark_entry``: a view whose metered EV passed the +3 cap, read by
  ``critic_code.lighting_items``) has the cause ``lighting`` (``set_lighting`` on the view's room: the room's lights
  and rig x factor); an exterior view (no room) has the cause ``lighting_exterior``: no agent tool sets the sun or
  the sky strength, so the finding is report-only with the reason (P1 decision, docs/milestone13.md §14.3: "a capped
  view is a lighting_dark finding routed to the lighting tools"; the CPU pre-flight found nothing read it);
  a room view that needs more light than ``set_lighting``'s maximum (``metrics.set_lighting_factor`` over
  ``tools.LIGHTING_FACTOR``'s top, x3) has the cause ``lighting_beyond_cap``: no tool. An edit is accepted only when
  the finding it targets is gone (CLAUDE.md), and no factor clears that view, so it is report-only with the reason
  instead of a set_lighting the acceptance must refuse every round (review of 16 Oct 2026: real04's basement salon
  needs about x10);
- the acceptance refuses an edit that took a fixture out of the scene (``edit["removed"]``, from ``removed_pieces``)
  when the dry re-check shows a NEW critical or major room-set finding (``ROOM_SET_CHECKS``: G9 a kitchen without
  its sink / hob / fridge, G10 a bathroom or WC without its toilet / washbasin / shower or bathtub) that names that
  fixture: fixed equipment is treated like walls (CLAUDE.md furniture rules). The CPU pre-flight's scripted round
  marked 5 real03 toilets as not furniture and the old rule (only new CRITICAL findings) accepted it with a major
  G10 "bathroom without a toilet" in each room.

Fix round after P3 (16-17 Oct 2026; docs/milestone13.md §14.8 "Attempt 2"):

- an X2 on a DECOR piece (``building["decor"]``, or a ``dec_`` / ``decor_`` id that is no furniture) has the cause
  ``decor_under_roof``: no agent tool edits decor (the edit tools act on ``building["furniture"]``), so it is "not
  yours" with the reason and is reported to the decor stage (``REPORT_TO``; the loop logs ``report_to: decor`` on
  the finding). Why: P3's wall mirror dec_L1_009 (top 5.26 m under the sloped L1 roof) was ``under_roof`` with the
  furniture tools, had no room, went to the building session and stayed critical for 4 rounds;
- ``accept_edit``'s reason labels its count "predicted": the dry re-check cannot re-render, and the next round's
  critics measure what is really gone (``metrics.findings_removed``).

Fix round after P4a (17 Oct 2026; pod P4a, real02 with the M11 cameras replayed):

- a door or window the build clipped under the sloped roof below a usable height (the X2 of ``build.prepare``'s
  clips: ``metrics.kind`` ``opening_clip``, "needs a dormer: review") has the cause ``opening_under_roof``: no tool,
  report-only with the reason. Why: P4a offered ``set_exterior`` for d_L1_004 / d_L1_005 and rejected 5 roof edits
  (one asked for a 70 degree gable); the roof comes from the drawings, a dormer is a design change;
- a vision finding the critic put on a piece while its message is about a light fixture (``critic_vision``: "the
  wall-mounted lamp next to the desk" on the desk) has the cause ``light_fixture``: no tool, reported to the lighting
  stage (``REPORT_TO``). Why: P4a sent a rig wall light's look to the desk; ``swap_model`` on the desk was accepted
  and the finding came back;
- S2 keys name the cut: ``finding_key`` of an S2 with ``metrics.other`` (a piece-piece cut) or ``metrics.wall_id``
  (a wall cut) is ``(S2, "<target>/<other or wall>")``. Why: P4a's ``S2:f_L1_021`` held a 0.055 m wall cut and a
  0.011 m chair cut under one key, so the acceptance and the metrics could not tell which one an edit removed. An
  edit target that names an S2 without its cut (no metrics) stands for every cut of the piece, as the old key did.
- (integration, the furniture track's ask) an F9 "through the room outline" (``metrics.outside_m2``) is a wall cut,
  never a wrong type: below ``S2_TOLERANCE_M`` deep (``metrics.depth_m``, ``plausibility._f9``) it is
  ``within_tolerance`` (report only), else ``collision`` (move the piece or its group, snap it to its wall; fix a
  drawn fixture). Why: P4a's seq-647 wardrobe F9 (0.052 m², 0.020 m deep) was ``wrong_type`` and offered
  ``mark_not_furniture``, which deleted the drawn wardrobe anchor f_L-1_024 for a 2 cm cut; ``edit_ops`` now refuses
  that mark for a drawn, code-typed piece, so without this routing the F9 had no tool at all.

Fix round after P4b (17 Oct 2026; pod P4b, real03, and the review of the P4a fix round; lead decisions of 17 Oct
2026):

- decision 1: a camera replayed from the baseline (set 1: ``source: replayed``, or a record that already replaced one,
  ``replaced_replayed``) is frozen for the before/after comparison (docs/milestone13.md §7). A camera-placement
  finding on it (``CAMERA_PLACEMENT_CHECKS``: X6, V1; ``mark_replayed`` sets ``metrics.replayed_camera`` from the
  scene manifest's cameras) has the cause ``replayed_camera``: no tool, reported (``REPORT_TO``: cameras). The agent
  may still add a new camera (an X6 "no frontal view" of the building keeps ``add_camera``);
- a ``lighting_dark`` view less than one exposure step (``critic_code.LIGHTING_STEP_STOPS``, 1/6 stop) over the cap
  is minor with ``metrics.below_exposure_step`` and the cause ``lighting_within_step``: no tool. Why: P4b re-lit and
  re-rendered three rooms for 0.01-0.04 stops; the render rounds the EV to 1/6 stop;
- a vision finding re-targeted to a decor light (``critic_vision``: a table lamp on the nightstand, a pendant over the
  table) has the cause ``decor_model``: no agent tool edits decor, reported to the decor stage;
- a vision X7 on one exterior view about over-exposure ("overexposed", "washed out", "blown") is
  ``lighting_exterior`` (the view's exposure, report-only), not ``sun``: P4b moved the sun to 55 degrees for the
  blown-out far pose of ext_7, outside the code's own 25-50 degrees;
- ``override_touches(cause, override)``: a ``set_exterior`` changes what a finding of that cause is about only when
  it sets one of the cause's slots (``EXTERIOR_SLOTS_OF_CAUSE``: site -> site or ground, roof -> roof, sun -> sun).
  The loop keeps a vision finding the override does not touch (P4b: a ground and a sun edit each counted the vision
  X4 "no path" as removed).

Fix round after P5 (22 Oct 2026; pod P5, real04):

- ``accept_edit`` reads ``edit["added"]`` (``added_pieces``: the pieces the edit put into the scene, new or typed
  differently, the mirror of ``removed_pieces``): when the piece of a target finding was removed and the dry re-check
  has the same check on an added piece of the same type in the same room (``recreated_finding``), the finding is still
  there, under a new id; the reason names both ids. Why: P5's relayout_room (seq 5383) "removed" X2:f_L1_049 by
  re-creating the same console table at the same centre as f_L1_056, and round 4 measured X2:f_L1_056 at the same
  0.84 / 0.82 m. Fix round after P5 (22 Oct 2026), review: that finding is critical or major (or as severe as the
  target), and an S2 is the same cut (the same wall, or a partner of the same id or type, ``edit["types"]``:
  ``piece_types``), so a minor touch of two re-created chairs no longer stands in for a cleared wall cut;
- the render's ``camera_blocked`` (``critic_code.blocked_items``: a preview whose lens touches a surface or whose
  frame one element fills) has the cause ``interior_camera`` (``set_camera`` / ``remove_camera`` on the view; an
  exterior view: ``exterior_camera``, the building session); a replayed (set 1) camera is frozen
  (``CAMERA_PLACEMENT_CHECKS``: ``replayed_camera``) and a view the camera search already called unavoidable
  (``metrics.blocked_unavoidable``) is reported only (``blocked_unavoidable``, no tool), as the GPU test allows it.

Fix round after P6a (22 Oct 2026; pod P6a, real04):

- ``accept_edit`` refuses a same-piece swap (``same_target_swap``): the dry re-check shows a new critical or major
  finding on a target of the edit (the target of one of its target findings; an S2 counts on the partner of its cut
  too) and the critical / major findings gone there are not more (compared critical first, then major: a critical
  traded for a major is a downgrade and passes; two majors traded for one pass). The reason starts with "swap:". Why:
  6 of P6a's 34 accepted edits traded one major for another on the same piece (F9 -> F4 / G6 on four chairs, G12 -> F3
  on two wardrobes: the wardrobe left its wall and still stood across the window); they were all of the run's "new"
  findings and all stayed to the end. P5's seq 4643 / 4651 (a chair's F9 and its S2 wall cut traded for one F8) still
  pass. An accepted reason names the new critical / major findings and the net (``findings_new``);
- a vision F1 / G14 (the type does not fit the room) on a drawn piece whose type the room's types hold
  (``drawn_type_held``: ``plausibility.allowed_in``, the room's aliases included) has the cause ``drawn_type``: no
  tool, reported for review (``REPORT_TO``). Why: P6a's vision critic called the drawn desk f_L0_026 "not standard
  for a bedroom" in all 4 rounds and the agent tried to retype it to a dresser (refused only by the score); CLAUDE.md
  keeps drawn furniture and trusts vector geometry over AI vision;
- an F3 / F8 on a drawn piece that no move within the drawn lock can clear (``drawn_layout_blocked``: no free wall
  place within 1.2 m of its drawn centre, and for an F8 no wall and no partner within a free 0.3 m move; or a room
  that keeps its drawn pieces) carries ``metrics.drawn_layout`` (``mark_drawn_layout``, called by the loop on the
  round's code findings) and has the cause ``drawn_layout``: no tool, reported. Why: P6a's drawn salon sofas
  f_L-1b_041 / 042 stand 2 m off every wall; their 8 moves were refused by the drawn lock, the wall snap or the memory
  in every round (60 of P6a's 150 refusals were moves of drawn pieces for F3 / F8 / G12). On P6a's round-1 findings
  the rule marks only those two sofas; the sofas f_L-1b_045 / 046 (a free wall place within 1.2 m), the plants
  f_L-1b_047 / 049 (a sofa within a free move) and the stoves and sinks a few cm off the wall inside their kitchen
  runs (the run pieces they already cut do not count: that cut is another finding) keep their tools. On the P4a / P4b
  / P5 round-1 findings it marks the free-standing drawn sofas 1.1-2.5 m off every wall and real03's washbasin
  f_L0_188 (through a wall and in a door, fix_fixture's).

Fix round after P6a, part 2 (23 Oct 2026; the exterior track's ask, verify:look:2 (4)): a vision X3 / X6 claim made
on the render of an exterior view the agent placed (``agent_view``: ``policy`` or ``view`` ``agent``; the loop names
the critique's view in ``evidence.view``) about that view or the building as a whole (no element id of the building)
is about that camera's framing: ``mark_agent_views`` sets its target to the view (the claimed target kept in
``metrics.claimed_target``) with ``metrics.agent_view``, and its cause is ``exterior_camera`` (set_camera,
remove_camera). Why: P6a seq 6856 "the entrance facade is a long, blank wall with no visible entrance door" on the
agent's ext_front_entrance (5 m from the facade, no sky) was dropped "no agent tool for the cause facade", so the
view that caused it was never moved or removed. A claim on a planner view, or about an element (an opening, a
wall), keeps the facade cause.

Fix round after P6b (23 Oct 2026; pod P6b, real03 on 8e8cc97, the review of its agent log and the verifiers' better
fixes):

- ``accept_edit`` lets a step's majors stay when its criticals are gone (``critical_cleared``): at least one target is
  critical, every critical target is gone, one of the gone criticals is measured by code (a vision finding on a changed
  target counts as gone unmeasured) and no kept target became more severe; the other checks (re-created finding, new
  critical, removed fixture, same-piece swap, penalty) still run with every target, and the accepted reason names the
  kept targets ("kept: G12:f_L0_200 (major)"). An all-major step keeps the old rule (every target gone). Why: P6b's
  fix_fixture of the fridges f_L0_200 / 202 / 206 (seq 1844 / 1849 / 1850: the critical F7 door swing and the G8 gone,
  the window G12 kept) and the bed move f_L0_141 (seq 1886 / 2834: the critical F3 gone, F4 / G5 / G11 kept) were
  refused "still there" and 4 criticals stayed to the end; a replay of every refusal of the P4a, P4b, P5 and P6a logs
  changes none of them;
- a vision F9 on a built piece about the rendered model ("rendered as", "hole", "placeholder", ...) is ``wrong_model``
  (swap_model, report_library_gap), one about a cut through a wall ("intersect", "clipping") is ``collision``, a
  placement opinion keeps the old route (``LOOK_WORDS``, ``WALL_CUT_WORDS``, ``PLACEMENT_WORDS``). Why: P6b's look
  claims (the holes in the coffee and dining tables, the slab fridge, the bunk bed, the small cabinet) got
  retype_piece only, and five same-type "confirms" were counted as removals (the loop's ``render_unchanged``);
- a vision F1 on a room that says it is empty (``EMPTY_ROOM_WORDS``) is ``empty_room`` (place_group, relayout_room),
  never set_room_type: P6b retyped r_L0_oda_19 bedroom -> balcony with an invented railing to clear "the room is
  completely empty" (the re-run never re-solves a layout after set_room_type);
- an RC on a symbol (no furniture piece: the reading moved it to ``building.symbols``) is ``resolved_by_code`` (no
  tool, reported): P6b's building session planned set_room_type on 11 symbol ids in rounds 2 and 3;
- an F7 / G12 / G8 on drawn fixed equipment that fix_fixture cannot move (``fixture_layout_blocked``: it stands
  through a wall or in a door, its size is real, and the code's own 0.5 m search finds no valid spot) is the drawn
  layout (``mark_drawn_layout``: ``metrics.drawn_layout`` ``"fixture"``; no tool, reported with
  ``FIXTURE_LAYOUT_REASON``). On P6b's round-1 findings it marks G12:f_L0_213 (a fridge in door d_L0_014) and
  G8:f_L0_010 (a counter 0.29 m² through its wall); the fridges f_L0_200 / 202 / 206 (a spot 0.15 m away) keep
  fix_fixture; nothing on P4a, P5 or P6a.
  Review: the search counts only the drawn pieces as obstacles (``drawn_obstacles_only``): a spot that only an
  added piece covers leaves the finding its tools (the added piece may move); the two P6b marks stay.

Fix round after P6b (23 Oct 2026), the reading track's asks (verify:library:2 better_fix (c), verify:look:2 step 3):

- an F7 of drawn fixed equipment at the edge of a doorless opening (``type: opening``) that leaves at least the main
  walkway clear (groups.yaml ``walkway_main``, 0.80 m; ``passage_clear``) carries ``metrics.drawn_layout``
  ``"passage_clear"`` with the clear width and is the drawn layout (no tool; ``PASSAGE_CLEAR_REASON``). Why: P6b's
  kitchen-run fridges f_L0_200 / 202 / 206 reach 0.12 m past the jamb of real03's 1.05 m passages and leave 0.93 m;
  their critical F7 drew 30 refused fix_fixture calls (one accepted on f_L0_204). A door with a leaf keeps its F7;
- an S2 wall cut or an F9 outline cut (``fixture_cut``) of drawn fixed equipment that ``fixture_layout_blocked`` holds
  (no valid spot within 0.5 m) is the drawn layout too (``"fixture"``, no tool), as its F7 / G12 / G8 were; a cut
  with another piece keeps its tools. On P6b's final building (F9): the counters f_L0_001 / 010, the washers
  f_L0_074-077 and the washbasin f_L0_188.

Fix round after P6a (23 Oct 2026), review: the F3 of a drawn piece that may stand free in its group (orientation rule
``wall_or_group``: a sofa facing its coffee table or TV unit), that the drawn lock holds off every wall and that has no
piece it may face within reach (``front_missing``) carries ``metrics.drawn_layout`` ``"missing_front"``
(``MISSING_FRONT``) and has the cause ``missing_member`` (complete_group, place_group, relayout_room), not
``drawn_layout``. Why: P6a's sofas f_L-1b_041 / 042 (and the same two on P4a's real02 data that P6c replays) have no
coffee table or TV unit in their rooms; with a coffee table 1 m in front of f_L-1b_041 the code reports no F3, so the
report blamed the drawing for an incomplete seating group (their G2 "has no coffee table" is minor and never worked).
The other drawn-layout F3s of P4a / P4b / P6a / P6b (sofas with a coffee table in reach, real03's washbasin) stay
``drawn_layout``. On P6a the sofas' anchors are unverified, so the room brief still locks complete_group for them
("retype_piece first") and the F3 is reported with that reason.

Milestone 13 final pass (23 Oct 2026; pod P6c, real02, verify:agent:3): a G3 whose angle is within groups.yaml
``armchair_facing.max_angle`` while its distance is over ``max_distance`` (``armchair_too_far``) has the cause
``group_layout`` (move_group, relayout_room, move_piece, rotate_piece, set_front), not ``orientation``. Why: P6c's
armchair f_L1_031 in r_L1_oyun_aktivite_ve_dinlenme_odasi faced its coffee table (12.1°, limit 30°) at 2.734 m (limit
2.50 m); ``orientation`` offered rotate_piece, set_front and relayout_room only, the plan checker removed the session's
move_piece ("move_piece does not fix c:G3:f_L1_032"), and the rendered room kept its G3 through three rounds (its
unrendered twin fixed it with an off-plan move). A G3 whose angle fails keeps ``orientation``.

26 Oct 2026 (Argus P10, "the agent tried N times and code refused every try"; the big loop's round 4 of real06):

- ``is_vision(finding)``: a finding an AI made by looking (``VISION_SOURCES``: the vision critic's on the previews,
  the AI judge's on the final renders, the inspector's, Argus AI's on the project) and that the dry re-check cannot
  measure. Every rule written for "a vision finding" reads it (``critical_cleared``: a gone judge critical is no code
  measure; ``cause_of``: a judge F1 / G14 on a drawn piece is ``drawn_type``, a judge F1 "empty" is ``empty_room``, a
  judge F9 about the rendered model is ``wrong_model``; ``mark_agent_views``). Why: the rules tested ``source ==
  "vision"`` and the judge's findings carry ``source: judge``; the loop's dry re-check dropped every one of them
  after the round's first accepted edit, so the next edits on them (swap_model on f_L1_017 for the judge's Q5) were
  refused "no target finding" and the first accepted edit counted 56 findings "removed";
- a Q5 that says the pieces do not match (``MISMATCH_WORDS``: "a mismatched set", "different models and colours")
  is ``wrong_model`` (swap_model), also when it counts the pieces ("the two armchairs"): the count words mean one
  piece too many (``wrong_type``) only without a mismatch. Why: real06's Q5 "The two armchairs are a mismatched set"
  was ``wrong_type`` and its checklist step offered retype_piece for a model's look.

Why: real04 (M12, §1.5) accepted 183 edits of which 20 removed their finding; the tools were mapped by check id
(``brief.CHECK_TOOLS``), so every room session got every tool for every check whatever the cause.

How: pure functions of dicts, a finding key is ``(check, target)`` (a finding dict of the critics or an ``edit`` /
``finding`` event of the log: ``check`` or ``checklist``, ``message`` or ``finding``; an S2 adds its cut to the
target, ``finding_key``); deterministic.
"""
from __future__ import annotations

from typing import Optional

S2_TOLERANCE_M = 0.03           # scene_checks.TOLERANCES["overlap_fixture"]: a cut below it is not an agent's work
SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2}

# cause -> the tools that fix it, best first ([]: no tool, the finding is "not yours").
CAUSE_TOOLS: dict[str, tuple[str, ...]] = {
    "collision": ("move_piece", "move_group", "fix_fixture", "relayout_room", "swap_model"),
    "blocked_opening": ("move_piece", "move_group", "fix_fixture", "mark_not_furniture", "relayout_room",
                        "remove_piece"),
    "clearance": ("move_piece", "move_group", "relayout_room", "remove_piece"),
    "floating": ("move_piece", "move_group", "relayout_room", "remove_piece"),
    "off_wall": ("move_piece", "move_group", "relayout_room"),
    "orientation": ("rotate_piece", "set_front", "relayout_room"),
    "group_layout": ("move_group", "relayout_room", "move_piece", "rotate_piece", "set_front"),
    "built_front": ("swap_model", "rotate_piece", "set_front"),
    # round 2: an F8 around an unbuilt anchor is fixed on the ANCHOR (``anchor_of``), by the tools that build it
    "anchor_untyped": ("retype_piece", "mark_not_furniture", "place_group"),
    "missing_anchor": ("place_group", "swap_model", "retype_piece", "report_library_gap"),
    "missing_member": ("complete_group", "place_group", "relayout_room"),
    "wrong_type": ("retype_piece", "mark_not_furniture", "remove_piece", "set_room_type"),
    "untyped": ("retype_piece", "mark_not_furniture"),
    "size": ("resize_piece", "fix_fixture", "retype_piece"),
    "fixture_place": ("fix_fixture",),
    "fixture_clearance": ("fix_fixture",),
    "wrong_model": ("swap_model", "report_library_gap"),
    "library_gap": ("report_library_gap", "swap_model"),
    "decor_look": ("swap_model",),
    "under_roof": ("move_piece", "move_group", "remove_piece", "relayout_room"),
    # fix round after P3: a decor piece through the roof; no agent tool edits decor (module docstring)
    "decor_under_roof": (),
    "room_type": ("set_room_type",),
    # R5 and the render's lighting_dark (a view above the +3 EV cap): the room's lights x factor (tools.set_lighting)
    "lighting": ("set_lighting",),
    "material": ("set_material",),
    "geometry": ("correct_geometry",),
    "roof": ("set_exterior",),
    "site": ("set_exterior",),
    "sun": ("set_exterior",),
    "levels": ("set_mark_kind", "set_room_floor", "set_ground_point"),
    "terrain": ("set_terrain", "set_ground_point", "set_room_floor"),
    "entrance": ("set_entrance", "set_ground_point"),
    "exterior_camera": ("set_camera", "add_camera", "remove_camera"),
    "interior_camera": ("set_camera", "remove_camera"),
    # measured, but no agent tool: the finding is "not yours" with the reason of NO_TOOL_REASON
    "within_tolerance": (),
    "soft_minimum": (),
    "facade": (),
    "decor_rest": (),
    "render_match": (),
    "debug_marker": (),
    "ceiling": (),
    "scale": (),
    "polish": (),
    "lighting_exterior": (),
    "lighting_beyond_cap": (),
    # fix round after P4a: a door or window clipped under the roof (a dormer is a design change); a vision finding
    # about a light fixture put on a piece (the rig's lights are the lighting stage's)
    "opening_under_roof": (),
    "light_fixture": (),
    # fix round after P4b (module docstring): a camera of the replayed set 1 (decision 1 of 17 Oct 2026), a view
    # less than one exposure step over the cap, a decor light's model
    "replayed_camera": (),
    "lighting_within_step": (),
    "decor_model": (),
    # fix round after P5: a blocked view the camera search had no free point for (its "blocked unavoidable" warning)
    "blocked_unavoidable": (),
    # fix round after P6a (module docstring): an F3 / F8 on a drawn piece no move within the drawn lock clears; a
    # vision opinion on the type of a drawn piece whose type the room's types hold
    "drawn_layout": (),
    "drawn_type": (),
    # fix round after P6b (module docstring): a room the vision critic calls empty is furnished (set_room_type never
    # furnishes: the re-run replays the overrides after the layout); a reading conflict on a symbol is resolved
    "empty_room": ("place_group", "relayout_room"),
    "resolved_by_code": (),
    # 26 Oct 2026: the visitor checks (prompts Q1-Q9) the architect's code owns (a door into the air or off its floor,
    # a fall risk, the opening models' style, the rain water): reported to the architect, never silent
    "opening_sense": (),
    "guard": (),
    "opening_style": (),
    "rain_water": (),
    # 26 Oct 2026: the model review's M8 (steps of two doors that meet, a handrail or a ramp in front of another
    # door, steps in front of a garage): the site stage lays out every entrance's steps by code
    "entrance_layout": (),
    # 27 Oct 2026: the model review's M10 (a balcony nobody can step onto, an open edge, the garden paving on a veranda,
    # an uncovered veranda, a roof at a balcony's floor level, posts that do not match): the site stage plans them
    "outdoor_space": (),
    # 27 Oct 2026: the roof's outline against the roof plan (model review M11): the reading puts the roof plan's
    # eaves loop on the walls; no agent tool draws a roof outline
    "roof_reading": (),
    # 27 Oct 2026: the model review's M9 (a stair cut off from its floor, a floor opening across a door or cutting a
    # floor apart): the stair's reading and its opening are the architect's (K4 at build, stair_access.fix_arrivals)
    "stair_access": (),
    # 28 Oct 2026: the model review's M13 (a hob without a hood, an appliance off the worktop line, wall cabinets that
    # cover a window, leave odd gaps or are boxes of odd widths): the module builders and the completion's wall run
    # rule make the kitchen; no agent tool builds a hood or splits a wall cabinet
    "kitchen_design": (),
    # 28 Oct 2026: the model review's M15 (bare or staggered terrace tiers, loose or buried treads, steps through a
    # planter, a tilted path, a steep bank, bare concrete walls, one floor look everywhere): the site stage grades
    # the garden by code (wenart/blender/grading.py); no agent tool draws the terrain
    "site_grading": (),
    "unknown": (),
}
CAUSES: tuple[str, ...] = tuple(CAUSE_TOOLS)
NO_TOOL_REASON: dict[str, str] = {
    "within_tolerance": f"within tolerance: a cut below {S2_TOLERANCE_M:.2f} m is not visible (S2 class tolerance); "
                        "no tool is offered",
    "soft_minimum": "a tiered minimum (groups.yaml tiers: a small kitchen's aisle, a drawn run's landings and work "
                    "triangle) is a scored term of the solver, reported only; no tool is offered",
    "facade": "the facade openings come from the drawings; no agent tool",
    "decor_rest": "decor rest is placed by the decor stage on the built mesh (S5): no agent tool",
    "render_match": "the render/JSON match is checked by the final check",
    "debug_marker": "debug markers are a build setting, not an agent edit",
    "ceiling": "ceiling heights come from the drawings",
    "scale": "storey and door sizes come from the drawings",
    "polish": "the polish check is a build setting",
    "lighting_exterior": "an exterior view is lit by the sun lamp and the sky world; no agent tool sets their strength "
                         "(set_exterior moves the sun only), so a view above the EV cap is reported only",
    "lighting_beyond_cap": "the view needs more light than set_lighting's maximum (the room's lights x3): no factor "
                           "clears it and there is no add-lamp tool, so it is reported only",
    "decor_under_roof": "a decor piece placed by the decor stage pokes through the roof: no agent tool edits decor "
                        "(the edit tools act on furniture), so it is reported to the decor stage",
    "opening_under_roof": "a door or window under the sloped roof is clipped below a usable height: it needs a "
                          "dormer (a design change, review); the roof comes from the drawings and set_exterior cannot "
                          "fix it, so it is reported only",
    "light_fixture": "the finding is about a light fixture (the room's lighting rig), not the piece it names: no "
                     "agent tool changes a light's model, so it is reported to the lighting stage",
    "replayed_camera": "the camera is replayed from the baseline run (set 1): its pose is frozen for the before/after "
                       "comparison (docs/milestone13.md §7, decision of 17 Oct 2026), so set_camera and remove_camera "
                       "are refused for it; the finding is reported (add_camera with a new view id may add another "
                       "view)",
    "lighting_within_step": "the view is less than one exposure step (1/6 stop) over the EV cap: the render rounds "
                            "the exposure to that step, so a set_lighting re-render changes nothing visible; reported "
                            "only",
    "decor_model": "the finding is about a decor piece (a table lamp, a pendant or ceiling light the decor stage "
                   "placed): no agent tool edits decor, so it is reported to the decor stage",
    "blocked_unavoidable": "the camera search found no free point in the room and said so (blocked unavoidable): the "
                           "view is allowed and listed; reported to the cameras",
    "drawn_layout": "the piece is drawn and stands as the documents place it: a drawn piece moves at most 0.3 m, or "
                    "1.2 m when its back snaps onto a wall, and no free wall place (doors, windows, the other pieces) "
                    "or partner lies within that reach, so no move clears the finding; the drawn layout is reported "
                    "(CLAUDE.md: drawn furniture is kept)",
    "opening_sense": "a door off its floor or into the air is the architect's (E1, O2, D4: its defaults turn such a "
                     "door into a window or set its threshold); reported to the architect for the next build",
    "guard": "a guard in front of an opening or a void is built by code (the architect's W3 / K2 and the facade's "
             "guard); reported to the architect",
    "opening_style": "the door and window models are chosen by code for the whole building (one language); reported "
                     "to the openings stage",
    "rain_water": "the gutters and downpipes are planned by code for the whole roof (A1); reported to the architect",
    "outdoor_space": "the verandas, balconies and terraces are planned by code from the documents (their floors, "
                     "guards, covers and posts: wenart.levels.outdoor, site.space_platform); no agent tool changes "
                     "them, so the finding is reported to the site stage",
    "entrance_layout": "the landings, steps, ramps and handrails in front of the doors are laid out by code for all "
                       "the entrances together (site.entrance_layout: doors whose steps would meet share one platform "
                       "with one flight, a ramp and the handrails keep clear of the other doors); no agent tool moves "
                       "them, so the finding is reported to the site stage",
    "stair_access": "the walk from a stair into its floors (which end its half landing is at, which flight arrives, "
                    "how far its floor opening reaches) is the architect's: at build its K4 takes the reading of an "
                    "assumed stair that leads into both floors and cuts the opening to the flights, the half landing "
                    "and the headroom (stair_access.fix_arrivals); no agent tool moves a stair or a floor opening, so "
                    "the finding is reported to the architect",
    # 28 Oct 2026: the model review's M13
    "kitchen_design": "the kitchen run is designed by code: the fit builds a hob in a run into the worktop with an "
                      "oven and a cooker hood over it (modules.plan_kitchen_run), the completion hangs the wall "
                      "cabinets as one run beside the hood, windows and doors (complete.wall_cabinets_for) and the fit "
                      "composes them of real units on the base joints (modules.plan_wall_run); the build cuts them "
                      "at the windows of the building as built. No agent tool builds a hood or splits a wall "
                      "cabinet, so the finding is reported to the fit",
    "drawn_type": "the piece is drawn and its type is one the room's types hold (the code's room rules, aliases "
                  "included): drawn furniture is kept (CLAUDE.md), and a vision opinion on its type is no reading "
                  "error, so it is reported for review, not retyped",
    "resolved_by_code": "a reading conflict the code already resolved (the drawing won, the item was moved to the "
                        "symbols): it names no furniture piece or room, so there is nothing to edit; reported",
    "roof_reading": "the roof's outline comes from the roof plan (the reading puts its eaves loop on the walls, "
                    "wenart.sheets.to_building.roof_outline_record): no agent tool draws a roof outline, so the "
                    "finding is reported to the reading stage",
    "site_grading": "the garden on the slope is graded by code (wenart/blender/grading.py: terraces at one level per "
                    "side and planted, banks of at most 1:3 / 1:2, flights of solid treads with cheek walls and a "
                    "landing, paths level across and stepped, walls in the house's base stone with a coping, the "
                    "floors by use); no agent tool changes the terrain, so the finding is reported to the site stage",
    "unknown": "no agent tool fixes this check",
}
# Fix round after P6b: why a drawn fixed piece's F7 / G12 / G8 is "not yours" (``FIXTURE_LAYOUT``).
FIXTURE_LAYOUT_REASON = ("the piece is drawn fixed equipment (treated like walls): only fix_fixture may move it, at "
                         "most 0.5 m, and the code's search found no valid spot within that reach (inside the room, "
                         "off the doors and the other pieces), so no edit clears the finding; it is reported for review")
# Fix round after P6b, the reading track's ask: why an F7 of drawn fixed equipment at a doorless opening's edge is
# "not yours" (``PASSAGE_CLEAR``); ``{clear}`` / ``{width}`` / ``{need}``: metres.
PASSAGE_CLEAR_REASON = ("the piece is drawn fixed equipment (treated like walls) at the edge of a doorless opening: it "
                        "leaves {clear:.2f} m of the {width:.2f} m passage clear (at least the {need:.2f} m main "
                        "walkway), so the drawing is no clear error and the piece stays as drawn; the opening is "
                        "real and is never moved; reported for review")
# Fix round after P3: cause -> the stage a finding no agent tool fixes is reported to (the loop logs it on the
# finding event as ``report_to``). Fix round after P4a: a light fixture's look goes to the lighting stage.
REPORT_TO: dict[str, str] = {"decor_under_roof": "decor", "decor_rest": "decor", "light_fixture": "lighting",
                             # 26 Oct 2026: the visitor checks the architect's rules own (E1, O2, D4, W3, A1, K2)
                             "opening_sense": "architect", "guard": "architect", "opening_style": "openings",
                             "rain_water": "architect",
                             # 26 Oct 2026: the entrance steps (model review M8) are the site stage's
                             "entrance_layout": "site", "outdoor_space": "site",
                             # 27 Oct 2026: the roof against the roof plan (M11) is the reading's
                             "roof_reading": "reading",
                             # 27 Oct 2026: the walk from the stairs (model review M9) is the architect's
                             "stair_access": "architect",
                             # 28 Oct 2026: the kitchen design (model review M13) is the fit's and the completion's
                             "kitchen_design": "fit",
                             # 28 Oct 2026: the grading of the site (model review M15) is the site stage's
                             "site_grading": "site",
                             # fix round after P4b: a frozen replayed camera, a decor light's model
                             "replayed_camera": "cameras", "decor_model": "decor",
                             # fix round after P5: a blocked view the camera search could not avoid
                             "blocked_unavoidable": "cameras",
                             # fix round after P6a: a vision opinion on a drawn piece's type (kept, for review)
                             "drawn_type": "review"}
# Fix round after P4a: the X2 kind of an opening the build clipped under the roof (``exterior_checks._x2``), and the
# words of its message when an older finding has no kind.
OPENING_CLIP_KIND = "opening_clip"
OPENING_CLIP_WORDS = ("needs a dormer",)
# Fix round after P4a: an S2 key is "<target>/<other piece or wall>" (module docstring).
S2_KEY_SEP = "/"
# The render's finding of a view whose metered EV passed the cap (``wenart.blender.render.LIGHTING_DARK_CHECK``; the
# report and the agent read it from the render manifest).
LIGHTING_DARK_CHECK = "lighting_dark"
LIGHTING_CHECKS: tuple[str, ...] = (LIGHTING_DARK_CHECK,)
# Tools only the building session may call (docs/milestone13.md §3.0 K4: "building-wide tools only from the
# building session"); the camera tools join them for an exterior view (``is_building_wide``).
BUILDING_WIDE_TOOLS: tuple[str, ...] = ("set_exterior", "set_material", "correct_geometry", "rerun_stage",
                                        "set_mark_kind", "set_room_floor", "set_ground_point", "set_entrance",
                                        "set_terrain")
CAMERA_TOOLS: tuple[str, ...] = ("set_camera", "add_camera", "remove_camera")
EXTERIOR_VIEW_PREFIX = "ext_"
BUILDING_WIDE_CAUSES: tuple[str, ...] = ("roof", "site", "sun", "geometry", "levels", "terrain", "entrance",
                                         "exterior_camera", "material")
# check -> its default cause (the rules of ``cause_of`` refine it from the metrics and the message).
CHECK_CAUSE: dict[str, str] = {
    "F1": "wrong_type", "F2": "size", "F3": "off_wall", "F4": "orientation", "F5": "missing_member",
    "F6": "clearance", "F7": "blocked_opening", "F8": "floating", "F9": "wrong_type",
    "R1": "room_type", "R2": "ceiling", "R3": "blocked_opening", "R4": "material", "R5": "lighting",
    "G1": "group_layout", "G2": "clearance", "G3": "orientation", "G4": "group_layout", "G5": "clearance",
    "G6": "orientation", "G7": "clearance", "G8": "fixture_clearance", "G9": "missing_member",
    "G10": "fixture_clearance", "G11": "clearance", "G12": "blocked_opening", "G13": "clearance",
    "G14": "wrong_type",
    "S1": "wrong_model", "S2": "collision", "S3": "built_front", "S4": "size", "S5": "decor_rest",
    "S6": "wrong_model", "LG": "library_gap", "LT": "wrong_model", "NR": "untyped", "RC": "wrong_type",
    "X1": "geometry", "X2": "roof", "X3": "facade", "X4": "site", "X5": "scale", "X6": "exterior_camera",
    "X7": "sun", "X8": "material",
    "V1": "interior_camera", "V2": "render_match", "V3": "debug_marker", "V4": "polish",
    "L1": "entrance", "L2": "entrance", "L3": "terrain", "L4": "levels", "L5": "entrance", "L6": "terrain",
    "L7": "exterior_camera",
    "D1": "decor_look", "D2": "wrong_model", "D3": "wrong_model",
    # 26 Oct 2026: the visitor checks (cause_of refines Q4-Q6 from the message)
    "Q1": "opening_sense", "Q2": "wrong_model", "Q3": "guard", "Q4": "empty_room", "Q5": "wrong_model",
    "Q6": "orientation", "Q7": "opening_style", "Q8": "rain_water", "Q9": "entrance_layout",
    # 28 Oct 2026: what the user pointed at (prompts Q10-Q15, X9, X10)
    "Q10": "wrong_type", "Q11": "light_fixture", "Q12": "missing_member", "Q13": "missing_member", "Q14": "material",
    "Q15": "decor_look", "X9": "terrain", "X10": "roof",
    # 26 Oct 2026: the review of the 3D model as built (wenart/blender/model_review.py; cause_of refines M7)
    "M1": "levels", "M2": "wrong_model", "M3": "guard", "M4": "opening_sense", "M5": "rain_water",
    "M6": "opening_style", "M7": "missing_anchor", "M8": "entrance_layout", "M9": "stair_access",
    "M10": "outdoor_space", "M11": "roof_reading",
    "M12": "opening_sense",          # 27 Oct 2026: doors side by side (the architect and Argus own it)
    "M13": "kitchen_design",         # 28 Oct 2026: the kitchen as one designed kitchen (the fit's module builders)
    "M14": "decor_rest",             # 28 Oct 2026: decor not attached to its support (the decor stage owns it)
    "M15": "site_grading",           # 28 Oct 2026: the grading of the site and its outdoor floors
    LIGHTING_DARK_CHECK: "lighting",
    # fix round after P5: a blocked preview (critic_code.blocked_items)
    "camera_blocked": "interior_camera",
}
_PIECE_PREFIXES = ("f_", "furn_", "decor_", "dec_")
# Fix round after P4b (module docstring): the camera-placement checks a replayed camera is frozen for, the metrics flag
# ``mark_replayed`` sets, the words of a single view's over-exposure (X7), and the set_exterior slots of a cause.
CAMERA_PLACEMENT_CHECKS: tuple[str, ...] = ("X6", "V1", "camera_blocked")      # fix round after P5: + blocked
CAMERA_BLOCKED_CHECK = "camera_blocked"     # = critic_code.CAMERA_BLOCKED_CHECK (fix round after P5)
BLOCKED_UNAVOIDABLE_FLAG = "blocked_unavoidable"
REPLAYED_FLAG = "replayed_camera"
OVEREXPOSED_WORDS = ("overexpos", "over-expos", "over expos", "washed out", "washed-out", "blown", "too bright",
                     "blinding", "burnt out", "burned out", "clipped white")
EXTERIOR_SLOTS_OF_CAUSE: dict[str, tuple[str, ...]] = {"site": ("site", "ground"), "roof": ("roof",),
                                                       "sun": ("sun",)}
_MISSING_WORDS = ("missing", " no ", "without", "lacks", "needs a", "has no", " only")
# Fix round after P6a (module docstring): the checks a drawn layout may hold for good (``drawn_layout``), the metrics
# flag ``mark_drawn_layout`` sets, and the type checks a vision opinion on a drawn piece's type comes with.
DRAWN_LAYOUT_CHECKS: tuple[str, ...] = ("F3", "F8")
DRAWN_LAYOUT_FLAG = "drawn_layout"
DRAWN_TYPE_CHECKS: tuple[str, ...] = ("F1", "G14")
# Fix round after P6a (23 Oct 2026), review (module docstring): the flag's value on the F3 of a drawn piece the drawn
# lock holds off every wall while no piece it may face stands in reach (``front_missing``): cause ``missing_member``.
MISSING_FRONT = "missing_front"
# Fix round after P6b (module docstring): the checks of drawn fixed equipment that only fix_fixture may clear, held for
# good when its 0.5 m search finds no valid spot (``fixture_layout_blocked``), and the flag's value then.
FIXTURE_LAYOUT_CHECKS: tuple[str, ...] = ("F7", "G12", "G8")
FIXTURE_LAYOUT = "fixture"
# Fix round after P6b, the reading track's asks (module docstring): the cuts of drawn fixed equipment through a wall
# (S2 with a ``wall_id``) or the room outline (F9 with ``outside_m2``) that fix_fixture's search cannot clear either,
# and the flag's value of an F7 at a doorless opening's edge that leaves the passage clear (``passage_clear``).
FIXTURE_CUT_CHECKS: tuple[str, ...] = ("S2", "F9")
PASSAGE_CLEAR = "passage_clear"
# Fix round after P6b (module docstring): the words of a vision F1 on a room that says it is empty (cause
# ``empty_room``), and of a vision F9 on a built piece: a cut through a wall (``collision``), a placement opinion (the
# old route), a claim about the rendered model (``wrong_model``).
EMPTY_ROOM_WORDS: tuple[str, ...] = ("empty", "lacking", "lacks", "missing", "no furniture", "unfurnished", " bare ")
WALL_CUT_WORDS: tuple[str, ...] = ("intersect", "clipping", "passing through", "passes through", "through the wall")
PLACEMENT_WORDS: tuple[str, ...] = ("placement", "positioned", "placed", "facing")
LOOK_WORDS: tuple[str, ...] = ("rendered as", "rendered with", "hole", "looks", "model", "placeholder", "geometry")
# Fix round after P6a, part 2 (module docstring): the vision claims about what an exterior view shows that an agent
# view's framing causes, and the metrics flag ``mark_agent_views`` sets (the view's name).
AGENT_VIEW_CHECKS: tuple[str, ...] = ("X3", "X6")
AGENT_VIEW_FLAG = "agent_view"
# 26 Oct 2026 (module docstring): the sources of findings an AI made by looking, which the dry re-check cannot measure
# (``critic_vision``: "vision"; ``judge.judge_view``: "judge"; the inspector; ``audit.argus_ai.work_findings``:
# "argus"), and the words of a Q5 about pieces that do not match (a model's look, not one piece too many).
VISION_SOURCES: tuple[str, ...] = ("vision", "judge", "inspector", "argus")
MISMATCH_WORDS: tuple[str, ...] = ("mismatch", "not match", "n't match", "should match", "different model",
                                   "different style", "different colour", "different color", "clash")


def is_vision(finding: Optional[dict]) -> bool:
    """26 Oct 2026 (module docstring): ``finding`` was made by an AI looking at a render or the project
    (``VISION_SOURCES``), not measured by code: the dry re-check keeps it on an unchanged target and counts it as
    re-judged (gone) on a target the edit changed; the next render's critics measure it."""
    return isinstance(finding, dict) and str(finding.get("source") or "") in VISION_SOURCES


def _text(finding: dict) -> str:
    return str(finding.get("message") or finding.get("finding") or "").lower()


def _metrics(finding: dict) -> dict:
    ev = finding.get("evidence") if isinstance(finding.get("evidence"), dict) else {}
    m = ev.get("metrics") if isinstance(ev.get("metrics"), dict) else finding.get("metrics")
    return m if isinstance(m, dict) else {}


def is_decor(target: Optional[str], building: Optional[dict] = None) -> bool:
    """Fix round after P3: ``target`` is a decor piece: an id of ``building["decor"]``, or (without a building, or an
    id that is in neither list) a ``dec_`` / ``decor_`` id; never a furniture id."""
    if not target:
        return False
    if building is not None:
        if any(f.get("id") == target for f in building.get("furniture") or [] if isinstance(f, dict)):
            return False
        if any(d.get("id") == target for d in building.get("decor") or [] if isinstance(d, dict)):
            return True
    return str(target).startswith(("dec_", "decor_"))


def _is_piece(target: Optional[str], building: Optional[dict]) -> bool:
    if not target:
        return False
    if building is not None:
        if any(f.get("id") == target for f in building.get("furniture") or []):
            return True
        if any(d.get("id") == target for d in building.get("decor") or []):
            return True
    return str(target).startswith(_PIECE_PREFIXES)


def _built_piece(building: Optional[dict], target: Optional[str]) -> bool:
    """Fix round after P6b: ``target`` is a furniture piece of ``building`` that the build makes with a model
    (``_built``); False without a building."""
    if not isinstance(building, dict) or not target:
        return False
    piece = next((f for f in building.get("furniture") or [] if isinstance(f, dict) and f.get("id") == target), None)
    return piece is not None and _built(piece)


def _missing(text: str, metrics: dict) -> bool:
    if metrics.get("missing") or metrics.get("missing_types"):
        return True
    padded = f" {text} "
    return any(w in padded for w in _MISSING_WORDS)


def cause_of(finding: dict, building: Optional[dict] = None) -> str:
    """The cause of a finding (module docstring). ``building`` (optional) tells whether a target is a piece."""
    given = finding.get("cause")
    if given in CAUSE_TOOLS:
        return str(given)
    check = str(finding.get("check") or finding.get("checklist") or "")
    text = _text(finding)
    metrics = _metrics(finding)
    target = finding.get("target")
    base = CHECK_CAUSE.get(check, "unknown")
    if check in DRAWN_TYPE_CHECKS and is_vision(finding) and drawn_type_held(building, target):
        return "drawn_type"                    # fix round after P6a: a vision opinion, the drawing's type stays
    if check == "F1" and is_vision(finding) and target and not _is_piece(target, building) \
            and any(w in f" {text} " for w in EMPTY_ROOM_WORDS):
        return "empty_room"                    # fix round after P6b: furnish the room, never retype it away
    if check == "RC" and target and not _is_piece(target, building):
        return "resolved_by_code"              # fix round after P6b: a symbol the reading moved out of the furniture
    # 26 Oct 2026: the model review's rooms: a missing anchor is furnished, an extra dining table is one too many
    if check == "M7":
        return "wrong_type" if target and _is_piece(target, building) else "empty_room"
    # 27 Oct 2026: an M9 door blocked by a movable piece is the furniture's (move it); the rest is the architect's
    if check == "M9" and metrics.get("kind") == "pieces" and any(t != "stair" for t in metrics.get("blocked_types")
                                                                  or []):
        return "blocked_opening"
    # 26 Oct 2026: the visitor checks, refined from the message
    if check == "Q4":
        if target and _is_piece(target, building):
            return "wrong_type"                # a piece of another room: retype or remove it
        return "empty_room" if any(w in f" {text} " for w in EMPTY_ROOM_WORDS + (" no ", "without")) \
            else "room_type"
    if check == "Q5" and any(w in text for w in MISMATCH_WORDS):
        return "wrong_model"                   # 26 Oct 2026: pieces that do not match: swap the odd one's model
    if check == "Q5" and target and _is_piece(target, building) and \
            any(w in text for w in ("several", "two ", "three", "four", "duplicate", "repeat", "extra", "second")):
        return "wrong_type"                    # one piece too many: retype it (its group's member) or remove it
    if check == "Q6" and any(w in text for w in ("window", "door", "blocks", "in front of")):
        return "blocked_opening"
    if check == "Q6" and any(w in text for w in ("free", "middle", "floating", "away from the wall")):
        return "off_wall"
    if check in FIXTURE_LAYOUT_CHECKS + FIXTURE_CUT_CHECKS and metrics.get(DRAWN_LAYOUT_FLAG) in (FIXTURE_LAYOUT,
                                                                                               PASSAGE_CLEAR):
        # fix round after P6b: fix_fixture's search found no valid spot; (asks) an S2 / F9 wall or outline cut of such
        # a piece, an F7 at a doorless opening's edge that leaves the passage clear
        return "drawn_layout"
    if check in FIXTURE_LAYOUT_CHECKS and metrics.get(DRAWN_LAYOUT_FLAG):
        return "drawn_layout"                  # fix round after P6b: fix_fixture's search found no valid spot
    if check in AGENT_VIEW_CHECKS and is_vision(finding) and metrics.get(AGENT_VIEW_FLAG):
        return "exterior_camera"               # fix round after P6a, part 2: the agent's view frames it so
    if check == "F8":
        if metrics.get("cause") == "anchor_not_built" or metrics.get("missing_anchor") or "not built" in text:
            # round 2: an unknown anchor is typed and built by retype_piece; a typed one the fit left unbuilt is
            # re-solved (place_group) or given a model (swap_model)
            anchor = metrics.get("missing_anchor")
            atype = metrics.get("anchor_type")
            if building is not None and anchor:
                piece = next((f for f in building.get("furniture") or [] if f.get("id") == anchor), None)
                if piece is not None:
                    atype = piece.get("type")
            return "anchor_untyped" if atype == "unknown" and anchor else "missing_anchor"
        if metrics.get(DRAWN_LAYOUT_FLAG):
            return "drawn_layout"              # fix round after P6a: no move within the drawn lock clears it
        return "floating"
    if check == "S2":
        depth = metrics.get("depth_m", metrics.get("overlap_m"))
        try:
            if depth is not None and float(depth) < S2_TOLERANCE_M - 1e-9:
                return "within_tolerance"
        except (TypeError, ValueError):
            pass
        return "collision"
    if check == "F9":
        if metrics.get("outside_m2") is not None or "through the room outline" in text:
            # fix round after P4a (module docstring): a cut through the outline is no wrong type
            depth = metrics.get("depth_m")
            try:
                if depth is not None and float(depth) < S2_TOLERANCE_M - 1e-9:
                    return "within_tolerance"
            except (TypeError, ValueError):
                pass
            return "collision"
        if "overlap" in text or "through a wall" in text or metrics.get("overlap_m2") or metrics.get("other"):
            return "collision"
        if "float" in text or "middle of the room" in text:
            return "floating"
        if "duplicate" in text:
            return "wrong_type"
        if is_vision(finding) and _built_piece(building, target):
            # fix round after P6b (module docstring): a claim about the rendered model is a model's, not a type's
            if any(w in text for w in WALL_CUT_WORDS):
                return "collision"
            if not any(w in text for w in PLACEMENT_WORDS) and any(w in text for w in LOOK_WORDS):
                return "wrong_model"
        return "wrong_type"
    if check == "X2":
        if is_decor(target, building):
            return "decor_under_roof"          # fix round after P3: no agent tool edits decor
        if _is_piece(target, building):
            return "under_roof"
        if metrics.get("kind") == OPENING_CLIP_KIND or any(w in text for w in OPENING_CLIP_WORDS):
            return "opening_under_roof"        # fix round after P4a: a dormer is no set_exterior (module docstring)
        return "roof"
    if check in ("G2", "G4", "G7", "G9", "G10", "G6", "F5"):
        if _missing(text, metrics):
            return "missing_member"
        if check == "G6":
            return "clearance" if ("pull" in text or "behind" in text) else "orientation"
        if check == "G10":
            return "fixture_clearance"
        return base
    if check == "G5":
        return "off_wall" if (metrics.get("part") == "headboard" or "headboard" in text) else "clearance"
    if check == "G3" and armchair_too_far(metrics):
        return "group_layout"                  # final pass: it faces its target but stands too far (move it)
    if check == "F3" and metrics.get(DRAWN_LAYOUT_FLAG) == MISSING_FRONT:
        return "missing_member"                # fix round after P6a, review: the group member it faces is missing
    if check == "F3" and metrics.get(DRAWN_LAYOUT_FLAG):
        return "drawn_layout"                  # fix round after P6a: no wall place within the drawn lock
    if check == "G8":
        return "soft_minimum" if metrics.get("tier") else "fixture_clearance"
    if check in CAMERA_PLACEMENT_CHECKS and metrics.get(REPLAYED_FLAG):
        return "replayed_camera"               # fix round after P4b, decision 1: set 1 is frozen (module docstring)
    if check == CAMERA_BLOCKED_CHECK and metrics.get(BLOCKED_UNAVOIDABLE_FLAG):
        return "blocked_unavoidable"           # fix round after P5: the camera search knew (module docstring)
    if check in ("V1", CAMERA_BLOCKED_CHECK):
        return "exterior_camera" if str(target or "").startswith(EXTERIOR_VIEW_PREFIX) else "interior_camera"
    if check == "X7" and str(target or "").startswith(EXTERIOR_VIEW_PREFIX) \
            and any(w in text for w in OVEREXPOSED_WORDS):
        return "lighting_exterior"             # fix round after P4b: one view's exposure, not the sun
    if check in LIGHTING_CHECKS:
        # round 4: set_lighting needs the view's room; an exterior view (no room) is lit by the sun and the sky only
        if not finding.get("room_id") or str(target or "").startswith(EXTERIOR_VIEW_PREFIX):
            return "lighting_exterior"
        if metrics.get("below_exposure_step"):
            return "lighting_within_step"      # fix round after P4b: under the 1/6-stop exposure step
        # review of 16 Oct 2026: a view no set_lighting factor can clear (module docstring)
        try:
            want = float(metrics["set_lighting_factor"])
        except (KeyError, TypeError, ValueError):
            want = None
        if want is not None:
            from wenart.agent.tools import LIGHTING_FACTOR
            if want > float(LIGHTING_FACTOR[1]) + 1e-9:
                return "lighting_beyond_cap"
        return "lighting"
    if check == "LG":
        if building is not None:
            piece = next((f for f in building.get("furniture") or [] if f.get("id") == target), None)
            if piece is not None and not _built(piece):
                return "missing_anchor"
        return "library_gap"
    return base


def armchair_too_far(metrics: dict) -> bool:
    """Milestone 13 final pass (23 Oct 2026; module docstring): a G3 whose angle (``angle_deg``) is within groups.yaml
    ``armchair_facing.max_angle`` while its distance (``distance_m``) is over ``max_distance``: the armchair faces its
    target and only a move fixes it. False when a metric is missing or the angle fails too."""
    try:
        angle, distance = float(metrics["angle_deg"]), float(metrics["distance_m"])
    except (KeyError, TypeError, ValueError):
        return False
    from wenart.furniture import groups as GR

    rule = GR.rule("armchair_facing")
    return angle <= float(rule["max_angle"]) + 1e-9 and distance > float(rule["max_distance"]) + 1e-9


def _built(piece: dict) -> bool:
    if piece.get("build", True) is False or piece.get("type") == "unknown":
        return False
    asset = piece.get("asset") if isinstance(piece.get("asset"), dict) else {}
    return asset.get("method") != "none"


def anchor_of(finding: dict) -> Optional[str]:
    """Round 2: the unbuilt anchor an F8 / LG finding is really about (``metrics.missing_anchor``), when it is not
    the finding's own target: the piece the fixing edit must act on (the brief's ``edit_target``); else None."""
    metrics = _metrics(finding)
    anchor = metrics.get("missing_anchor")
    if not anchor or anchor == finding.get("target"):
        return None
    return str(anchor)


def tools_for_finding(finding: dict) -> list[str]:
    """The tools offered for the cause of ``finding`` (``CAUSE_TOOLS``; the finding's ``cause`` when the loop set
    it, else ``cause_of`` on the finding alone), best first; ``[]`` when no tool fixes the cause."""
    return list(CAUSE_TOOLS.get(cause_of(finding), ()))


def no_tool_reason(finding: dict) -> str:
    """Why a finding without tools is "not yours"."""
    cause = cause_of(finding)
    if cause == "drawn_layout" and _metrics(finding).get(DRAWN_LAYOUT_FLAG) == FIXTURE_LAYOUT:
        return FIXTURE_LAYOUT_REASON           # fix round after P6b
    if cause == "drawn_layout" and _metrics(finding).get(DRAWN_LAYOUT_FLAG) == PASSAGE_CLEAR:
        m = _metrics(finding)                  # fix round after P6b, the reading track's ask
        try:
            return PASSAGE_CLEAR_REASON.format(clear=float(m["passage_clear_m"]), width=float(m["passage_width_m"]),
                                               need=float(m["passage_need_m"]))
        except (KeyError, TypeError, ValueError):
            # a dry re-check's copy carries the flag only (``loop.carry_drawn_layout``)
            return PASSAGE_CLEAR_REASON.split(": it leaves", 1)[0] + (": it leaves at least the main walkway of the "
                                                                     "passage clear, so the piece stays as drawn; "
                                                                     "reported for review")
    return NO_TOOL_REASON.get(cause, f"no agent tool fixes {finding.get('check') or finding.get('checklist')} "
                                     f"(cause {cause})")


def is_building_wide(tool: str, args: Optional[dict] = None) -> bool:
    """A tool only the building session may call: ``BUILDING_WIDE_TOOLS``, and a camera tool on an exterior view
    (``view_id`` starting with ``ext_`` or ``kind: exterior``)."""
    if tool in BUILDING_WIDE_TOOLS:
        return True
    if tool in CAMERA_TOOLS:
        a = args or {}
        return str(a.get("view_id") or "").startswith(EXTERIOR_VIEW_PREFIX) or a.get("kind") == "exterior"
    return False


def frozen_camera(camera: Optional[dict]) -> bool:
    """Fix round after P4b (decision 1 of 17 Oct 2026): a camera of the replayed set 1: ``source: replayed``, or a
    record that already replaced a replayed one (``replaced_replayed``: its name is still set 1's)."""
    return isinstance(camera, dict) and (camera.get("source") == "replayed"
                                         or isinstance(camera.get("replaced_replayed"), dict))


def mark_replayed(findings: list[dict], cameras) -> list[dict]:
    """Fix round after P4b (module docstring): every finding of ``CAMERA_PLACEMENT_CHECKS`` on a frozen camera
    (``frozen_camera``; ``cameras``: the scene manifest's camera records) gets ``metrics.replayed_camera`` (in its
    ``evidence.metrics``, where ``cause_of`` reads it) and a ``cause`` it carried before is dropped, so the cause is
    taken again. Changes the findings in place and returns them."""
    frozen = {str(c.get("name")) for c in cameras or [] if frozen_camera(c) and c.get("name")}
    if not frozen:
        return findings
    for f in findings or []:
        check = str(f.get("check") or f.get("checklist") or "")
        if check not in CAMERA_PLACEMENT_CHECKS or str(f.get("target")) not in frozen:
            continue
        evidence = f.get("evidence") if isinstance(f.get("evidence"), dict) else {}
        evidence["metrics"] = dict(_metrics(f), **{REPLAYED_FLAG: True})
        f["evidence"] = evidence
        if f.get("cause") not in (None, "replayed_camera"):
            f.pop("cause", None)
    return findings


def agent_view(camera: Optional[dict]) -> bool:
    """Fix round after P6a, part 2 (module docstring): ``camera`` is an exterior view the agent placed (its plan's
    ``policy`` or its ``view`` is ``agent``; the build's agent plans, ``overrides.fixed_plan``)."""
    if not isinstance(camera, dict):
        return False
    kind = camera.get("kind") or ("exterior" if not camera.get("room_id") else "interior")
    return kind == "exterior" and (camera.get("policy") == "agent" or camera.get("view") == "agent")


def _element_ids(building: Optional[dict]) -> set:
    if not isinstance(building, dict):
        return set()
    out: set = set()
    for key in ("openings", "walls", "rooms", "furniture", "decor", "levels", "slabs"):
        out |= {str(e.get("id")) for e in building.get(key) or [] if isinstance(e, dict) and e.get("id")}
    return out


def mark_agent_views(findings: list[dict], cameras, building: Optional[dict] = None) -> list[dict]:
    """Fix round after P6a, part 2 (module docstring): every vision finding of ``AGENT_VIEW_CHECKS`` made on the render
    of an exterior view the agent placed (``agent_view``; the view is the finding's ``evidence.view``, the critique's
    key, else its target when that names a camera) whose target is that view or no element of ``building`` (the
    building, the facade) gets the view as its target, ``metrics.agent_view`` (and ``metrics.claimed_target`` when the
    target changes); a ``cause`` it carried is dropped, so the cause is taken again (``exterior_camera``). Changes the
    findings in place and returns them."""
    by_name = {str(c.get("name")): c for c in cameras or [] if isinstance(c, dict) and c.get("name")}
    elements = None
    for f in findings or []:
        check = str(f.get("check") or f.get("checklist") or "")
        if check not in AGENT_VIEW_CHECKS or not is_vision(f):
            continue
        evidence = f.get("evidence") if isinstance(f.get("evidence"), dict) else {}
        target = None if f.get("target") is None else str(f.get("target"))
        view = evidence.get("view") or (target if target in by_name else None)
        if not view or not agent_view(by_name.get(str(view))):
            continue
        if target != str(view):
            elements = _element_ids(building) if elements is None else elements
            if target in elements:
                continue                         # a claim about an element of the facade keeps its cause
        metrics = dict(_metrics(f), **{AGENT_VIEW_FLAG: str(view)})
        if target != str(view):
            metrics["claimed_target"] = target
        f["evidence"] = dict(evidence, metrics=metrics)
        f["target"] = str(view)
        if f.get("cause") not in (None, "exterior_camera"):
            f.pop("cause", None)
    return findings


def _room_of_piece(building: dict, piece: dict) -> Optional[dict]:
    return next((r for r in building.get("rooms") or [] if isinstance(r, dict) and r.get("id") == piece.get("room_id")),
                None)


def drawn_type_held(building: Optional[dict], target: Optional[str]) -> bool:
    """Fix round after P6a (module docstring): ``target`` is a drawn piece (``from_documents``) of ``building`` whose
    type the types of its room hold (``plausibility.allowed_in``: the room's type, its other labels and its alias
    kind, as F1 reads them); False without a building, for an AI piece, an untyped piece or a type the room never
    holds (the code's F1 names that one)."""
    if not isinstance(building, dict) or not target:
        return False
    piece = next((f for f in building.get("furniture") or [] if isinstance(f, dict) and f.get("id") == target), None)
    if piece is None or piece.get("source") != "from_documents" or piece.get("type") in (None, "unknown"):
        return False
    room = _room_of_piece(building, piece)
    if room is None:
        return False
    try:
        from wenart.furniture import plausibility as PL
        return piece["type"] in PL.allowed_in(building, room)
    except Exception:  # noqa: BLE001 - without the room rules the finding keeps its tools
        return False


def front_missing(building: dict, piece: dict) -> bool:
    """Fix round after P6a (23 Oct 2026), review: ``piece``'s type may stand free in its group (``schemas
    .orientation_rule``: back ``wall_or_group`` with ``front_to`` types; a sofa facing its coffee table or TV unit) and
    no built ``front_to`` piece of its room stands within ``reach_m`` of it (edge to edge, as
    ``plausibility._faced_group`` reads it), so its F3 goes once the group's member is added. False otherwise and
    whenever the geometry cannot be read."""
    try:
        from wenart.furniture import placer, schemas
        rule = schemas.orientation_rule(str(piece.get("type")))
        if rule.get("back") != "wall_or_group" or not rule.get("front_to"):
            return False
        poly = placer.drawn_piece(piece).polygon()
        reach = float(rule.get("reach_m") or 0.0) + 1e-9
        return not any(f.get("type") in rule["front_to"] and placer.drawn_piece(f).polygon().distance(poly) <= reach
                       for f in building.get("furniture") or [] if isinstance(f, dict)
                       and f.get("id") != piece.get("id") and f.get("room_id") == piece.get("room_id") and _built(f))
    except Exception:  # noqa: BLE001 - a geometry that cannot be read keeps the drawn-layout verdict
        return False


def drawn_layout_blocked(building: dict, piece: dict, check: str) -> bool:
    """Fix round after P6a (module docstring): no edit within the drawn lock clears the ``check`` (F3 / F8) of the
    drawn piece ``piece``: the room keeps its drawn pieces (``edit_ops.kept_room``), or no wall place of the room lies
    within ``schemas.WALL_SNAP_MAX_M`` (1.2 m) of the piece's drawn centre (``placer.snap_to_wall``: inside the room,
    off the doors' swings and the windows, off the room's other floor pieces but those it already cuts, which are
    another finding's), and for an F8 also no wall and no
    partner of its type (``schemas.orientation_rule``) within a free move (``edit_ops.SNAP_MAX_M``, 0.3 m, measured
    from where the piece stands now plus how far it already moved: never less reach than the lock gives). False for a
    piece that is not drawn, not built or untyped, and whenever the geometry cannot be read (the finding keeps its
    tools). Fix round after P6a (23 Oct 2026), review: False also for the F3 of a piece whose group member in front of
    it is missing (``drawn_layout_state`` ``MISSING_FRONT``): adding that member clears it."""
    return drawn_layout_state(building, piece, check) is True


def drawn_layout_state(building: dict, piece: dict, check: str):
    """Fix round after P6a (23 Oct 2026), review: the verdict of ``drawn_layout_blocked`` (True / False), or
    ``MISSING_FRONT`` for an F3 the drawn lock holds off every wall (no wall place within reach) while no piece the
    piece may face stands in reach (``front_missing``: a drawn sofa without its coffee table or TV unit). Why: P6a's
    drawn salon sofas f_L-1b_041 / 042 have no coffee table or TV unit in their rooms; with a coffee table 1 m in front
    of f_L-1b_041 the code reports no F3, so the incomplete seating group is the cause (``missing_member``:
    complete_group, place_group), not the drawing."""
    if not isinstance(piece, dict) or piece.get("source") != "from_documents" or not in_scene(piece) \
            or piece.get("type") in (None, "unknown"):
        return False
    room = _room_of_piece(building, piece)
    if room is None:
        return False
    try:
        from wenart import geometry as G
        from wenart.furniture import edit_ops as EO
        from wenart.furniture import placer, schemas
        from wenart.furniture import plausibility as PL
        if EO.kept_room(building, room):
            return True
        ctx = placer.room_context(building, room)
        p = placer.drawn_piece(piece)
        drawn = (piece.get("drawn_footprint") or piece["footprint"])["center"]
        drift = G.distance(p.center, drawn)
        floor = [f for f in building.get("furniture") or [] if isinstance(f, dict) and f.get("id") != piece.get("id")
                 and f.get("room_id") == room.get("id") and in_scene(f) and f.get("type") not in (None, "unknown")
                 and not schemas.off_floor(f)]
        here = p.polygon()
        # a piece it already cuts (a sink in its counter run) is another finding's (S2 / F9), not a missing wall place
        pairs = [(f, placer.drawn_piece(f)) for f in floor]
        pairs = [(f, o) for f, o in pairs if o.polygon().intersection(here).area < placer.AREA_EPS]
        floor, others = [f for f, _ in pairs], [o for _, o in pairs]
        found = placer.snap_to_wall(p, ctx, max_shift=schemas.WALL_SNAP_MAX_M + drift, others=others)
        if found is not None and G.distance(found[0], drawn) <= schemas.WALL_SNAP_MAX_M + 1e-6:
            return False
        if check == "F8":
            reach = float(EO.SNAP_MAX_M) + drift
            poly = here
            if poly.exterior.distance(ctx.ring) <= PL.SIDE_WALL_M + reach + 1e-9:
                return False
            rule = schemas.orientation_rule(piece["type"])
            partners = set(rule.get("partners") or ())
            limit = float(rule.get("partner_m") or 0.0) + reach + 1e-9
            if any(f.get("type") in partners and o.polygon().distance(poly) <= limit for f, o in zip(floor, others)):
                return False
        if check == "F3" and front_missing(building, piece):
            return MISSING_FRONT             # fix round after P6a, review: its group member, not the drawing
        return True
    except Exception:  # noqa: BLE001 - a geometry that cannot be read keeps the finding's tools
        return False


def mark_drawn_layout(findings: list[dict], building: Optional[dict]) -> list[dict]:
    """Fix round after P6a (module docstring): every code finding of ``DRAWN_LAYOUT_CHECKS`` on a drawn piece that
    ``drawn_layout_blocked`` holds gets ``metrics.drawn_layout`` (in its ``evidence.metrics``, where ``cause_of``
    reads it) and a ``cause`` it carried before is dropped, so the cause is taken again. An F8 around an unbuilt
    anchor (``metrics.missing_anchor``) is left alone: building the anchor is its fix. Changes the findings in place
    and returns them. Fix round after P6a (23 Oct 2026), review: an F3 whose missing group member is the fix
    (``drawn_layout_state``) gets the flag's value ``MISSING_FRONT`` (cause ``missing_member``; the dry re-check
    carries the value like the others)."""
    if not isinstance(building, dict):
        return findings
    pieces = {f.get("id"): f for f in building.get("furniture") or [] if isinstance(f, dict) and f.get("id")}
    fixtures: dict = {}                      # fix round after P6b: one spot search per piece
    for f in findings or []:
        check = str(f.get("check") or f.get("checklist") or "")
        if is_vision(f) or _metrics(f).get("missing_anchor"):
            continue
        piece = pieces.get(f.get("target"))
        if piece is None:
            continue
        state = drawn_layout_state(building, piece, check) if check in DRAWN_LAYOUT_CHECKS else False
        extra: dict = {}
        passage = passage_clear(building, piece, _metrics(f).get("door")) if check == "F7" else None
        if state:
            flag = state
        elif passage is not None:
            # fix round after P6b, the reading track's ask (module docstring): the doorless passage stays usable
            flag, extra = PASSAGE_CLEAR, passage
        elif check in FIXTURE_CUT_CHECKS and not fixture_cut(f):
            continue
        elif check in FIXTURE_LAYOUT_CHECKS + FIXTURE_CUT_CHECKS:
            # fix round after P6b (module docstring): drawn fixed equipment fix_fixture finds no valid spot for
            if piece.get("id") not in fixtures:
                fixtures[piece.get("id")] = fixture_layout_blocked(building, piece)
            if not fixtures[piece.get("id")]:
                continue
            flag = FIXTURE_LAYOUT
        else:
            continue
        evidence = f.get("evidence") if isinstance(f.get("evidence"), dict) else {}
        evidence["metrics"] = dict(_metrics(f), **extra, **{DRAWN_LAYOUT_FLAG: flag})
        f["evidence"] = evidence
        f.pop("cause", None)
    return findings


def fixture_cut(finding: dict) -> bool:
    """Fix round after P6b, the reading track's ask (module docstring): an S2 that cuts a wall (``metrics.wall_id``, no
    ``metrics.other``) or an F9 through the room outline (``metrics.outside_m2``): the cuts fix_fixture answers by
    moving the piece. A cut with another piece is not one (the other piece may move)."""
    check = str(finding.get("check") or finding.get("checklist") or "")
    m = _metrics(finding)
    if check == "S2":
        return bool(m.get("wall_id")) and not m.get("other")
    if check == "F9":
        return m.get("outside_m2") is not None
    return False


def passage_clear(building: dict, piece: dict, door_id: Optional[str]) -> Optional[dict]:
    """Fix round after P6b, the reading track's ask (verify:library:2 better_fix (c)): for the F7 of drawn fixed
    equipment (``edit_ops._fixed``, ``from_documents``) at a doorless opening (``type: opening``: no leaf, no swing)
    whose approach strip it reaches into while the opening keeps at least the main walkway clear (groups.yaml
    ``walkway_main``: 0.80 m; ``passage_clear_m``: the longer free stretch of the opening's width beside the piece),
    ``{"passage_clear_m", "passage_width_m", "passage_need_m"}``; None otherwise (a door with a leaf keeps its F7: a
    piece in a door is a clear error) and whenever the geometry cannot be read. Why: P6b's real03 kitchen-run fridges
    f_L0_200 / 202 / 206 reach 0.12 m past the jamb of the 1.05 m passages (DUVAR end caps at both jambs, a real
    opening) and leave 0.93 m clear; the critical F7 sent fix_fixture after them."""
    if not door_id or not isinstance(piece, dict) or piece.get("source") != "from_documents" or not in_scene(piece):
        return None
    opening = next((o for o in building.get("openings") or [] if isinstance(o, dict) and o.get("id") == door_id), None)
    if opening is None or opening.get("type") != "opening":
        return None
    try:
        from wenart.furniture import edit_ops as EO
        from wenart.furniture import groups as GR
        from wenart.furniture import placer
        room = _room_of_piece(building, piece)
        if room is None or not EO._fixed(piece):
            return None
        ctx = placer.room_context(building, room)
        door = next((d for d in ctx.doors if d.id == door_id), None)
        if door is None or door.along is None:
            return None
        hit = placer.drawn_piece(piece).polygon().intersection(door.zone)
        parts = placer.polygon_parts(hit)
        if not parts:
            return None                      # the F7 was not measured on this building: its tools stay
        width = float(door.width)
        half = width / 2.0
        (x0, y0), (ux, uy) = door.inner_point, door.along
        ts = [(x - x0) * ux + (y - y0) * uy for part in parts for x, y in part.exterior.coords]
        lo, hi = max(-half, min(ts)), min(half, max(ts))
        clear = max(0.0, lo + half, half - hi)
        need = float(GR.rule("walkway_main")["min"])
        if clear < need - 1e-9:
            return None
        return {"passage_clear_m": round(clear, 3), "passage_width_m": round(width, 3), "passage_need_m": need}
    except Exception:  # noqa: BLE001 - a geometry that cannot be read keeps the finding's tools
        return None


def fixture_layout_blocked(building: dict, piece: dict) -> bool:
    """Fix round after P6b (module docstring): ``piece`` is drawn fixed equipment (``edit_ops._fixed``) in the scene
    whose only tool, ``fix_fixture``, cannot move it anywhere: it stands through a wall or in a door
    (``edit_ops.fixture_problems``: a place problem), its size is real (no misread size to fix, no bath or shower bay
    to shrink into) and the code's own search within 0.5 m (``edit_ops._nearest_valid``, as ``fix_fixture`` without a
    centre runs it) finds no valid spot. False otherwise, and whenever the geometry cannot be read (the finding keeps
    its tools). A piece without a place problem is left alone: the brief's lock already says fix_fixture refuses it.
    Fix round after P6b (23 Oct 2026), review: the search counts only the drawn pieces as obstacles
    (``drawn_obstacles_only``): a piece the AI added may be moved or removed, so a spot that only an added piece covers
    is no drawing fact and the finding keeps its tools."""
    if not isinstance(piece, dict) or not in_scene(piece) or piece.get("type") in (None, "unknown"):
        return False
    try:
        from wenart.furniture import edit_ops as EO
        from wenart.furniture import placer
        room = _room_of_piece(building, piece)
        if room is None or not EO._fixed(piece):
            return False
        probs = EO.fixture_problems(building, piece)
        if probs.get("size") is not None or probs.get("place") is None:
            return False
        if EO._bay_fix(building, room, piece) is not None:
            return False
        drawn = drawn_obstacles_only(building, room.get("id"))
        return EO._nearest_valid(drawn, room, piece, placer.drawn_piece(piece)) is None
    except Exception:  # noqa: BLE001 - a geometry that cannot be read keeps the finding's tools
        return False


def drawn_obstacles_only(building: dict, room_id: Optional[str]) -> dict:
    """Fix round after P6b (23 Oct 2026), review: a shallow copy of ``building`` in which the pieces of room ``room_id``
    that are not from the documents (``added_by_ai``: the agent may move or remove them) are not built (``build``
    false), so ``edit_ops._nearest_valid`` meets only the drawn pieces. Why: with an added sideboard over the only free
    spots, a drawn fridge in a door swing was marked the drawn layout (no tool, "no edit clears the finding") although
    moving the sideboard clears it. The building itself is not changed."""
    furniture = [dict(f, build=False) if isinstance(f, dict) and f.get("room_id") == room_id
                 and f.get("source") != "from_documents" else f for f in building.get("furniture") or []]
    return dict(building, furniture=furniture)


def override_slots(override: Optional[dict]) -> set:
    """Fix round after P4b: the top-level slots a ``set_exterior`` override sets (``roof``, ``site``, ``ground``,
    ``sun``), without ``reason`` and empty values."""
    return {str(k) for k, v in (override or {}).items() if k != "reason" and v not in (None, {}, [])}


def override_touches(cause: Optional[str], override: Optional[dict]) -> bool:
    """Fix round after P4b (module docstring): a ``set_exterior`` override changes what a finding of ``cause`` is
    about (``EXTERIOR_SLOTS_OF_CAUSE``); False for a cause without exterior slots (a facade, a camera, a material)."""
    return bool(set(EXTERIOR_SLOTS_OF_CAUSE.get(str(cause), ())) & override_slots(override))


# --------------------------------------------------------------------------
# Acceptance
# --------------------------------------------------------------------------

def finding_key(finding: dict) -> tuple[str, str]:
    """``(check, target)``: the identity of a finding across rounds (the ids of vision findings change per call).
    Fix round after P4a: an S2 names its cut, ``(S2, "<target>/<metrics.other or metrics.wall_id>")``, so a wall cut
    and a chair cut of one piece are two findings (an S2 without either keeps ``(S2, target)``)."""
    check = str(finding.get("check") or finding.get("checklist") or "?")
    target = str(finding.get("target"))
    if check == "S2":
        metrics = _metrics(finding)
        part = metrics.get("other") or metrics.get("wall_id")
        if part:
            target = f"{target}{S2_KEY_SEP}{part}"
    return (check, target)


def base_key(key: tuple[str, str]) -> tuple[str, str]:
    """Fix round after P4a: ``(check, target)`` of a key without the S2 cut (``finding_key``): the key an older log
    names."""
    check, target = key
    return (check, target.split(S2_KEY_SEP, 1)[0]) if check == "S2" else (check, target)


def parse_key(text: str) -> tuple[str, str]:
    """A ``check:target`` string of the log (``key_list``, ``evidence.acceptance.target``) as a key."""
    check, _, target = str(text).partition(":")
    return (check, target)


def _fmt(key) -> str:
    return f"{key[0]}:{key[1]}"


def target_keys(edit: dict) -> list[tuple[str, str]]:
    """The finding keys an edit targets: ``edit["target_finding"]`` (a dict or a list of dicts with ``check`` and
    ``target``, and for an S2 its ``metrics``: ``finding_key``), else ``edit["target_findings"]``; [] without one."""
    raw = edit.get("target_finding")
    if raw is None:
        raw = edit.get("target_findings")
    items = raw if isinstance(raw, (list, tuple)) else [raw] if isinstance(raw, dict) else []
    out = []
    for it in items:
        if isinstance(it, dict) and (it.get("check") or it.get("checklist")) and it.get("target") is not None:
            key = finding_key(it)
            if key not in out:
                out.append(key)
    return out


def _penalties(edit: dict) -> tuple[Optional[float], Optional[float]]:
    """``(penalty_before, penalty_after)``: the penalties when the edit carries them, else from the scores (a
    higher score is better: penalty = -score); ``(None, None)`` without numbers."""
    pb, pa = edit.get("penalty_before"), edit.get("penalty_after")
    if pb is None or pa is None:
        sb, sa = edit.get("score_before"), edit.get("score_after")
        if sb is None or sa is None:
            return None, None
        try:
            return -float(sb), -float(sa)
        except (TypeError, ValueError):
            return None, None
    try:
        return float(pb), float(pa)
    except (TypeError, ValueError):
        return None, None


# Round 4: the room-set checks of ``wenart.furniture.group_checks`` (``_g8_g9``: G9 "kitchen <zone> has no <kind>";
# ``_g10``: G10 "<room type> without a <type>") carry ``metrics.missing``, the fixture kind the room needs; kind ->
# the piece types that give it (G9's kinds are ``group_checks.KITCHEN_FIXTURES``; pinned equal by
# tests/test_m13_agent.py). Several G10 findings of one room share the key (G10, room id), so the missing kind is
# part of their identity here.
ROOM_SET_CHECKS: tuple[str, ...] = ("G9", "G10")
SET_KIND_TYPES: dict[str, tuple[str, ...]] = {
    "toilet": ("toilet",), "washbasin": ("washbasin",), "shower|bathtub": ("shower", "bathtub"),
    "sink": ("sink_kitchen",), "hob": ("stove",), "fridge": ("fridge",),
}


def in_scene(piece: dict) -> bool:
    """A piece the build makes: ``build`` not false (a removed, not-furniture or unbuilt piece is out)."""
    return isinstance(piece, dict) and piece.get("build", True) is not False


def removed_pieces(before: Optional[dict], after: Optional[dict]) -> list[dict]:
    """``[{id, type, room_id}]``: the pieces of ``before`` in the scene (``in_scene``) that ``after`` no longer has
    there as the same type (deleted, ``build: false`` such as ``mark_not_furniture``, or typed differently). Pure."""
    now = {f.get("id"): f for f in (after or {}).get("furniture") or [] if isinstance(f, dict)}
    out = []
    for f in (before or {}).get("furniture") or []:
        if not in_scene(f):
            continue
        g = now.get(f.get("id"))
        if g is None or not in_scene(g) or g.get("type") != f.get("type"):
            out.append({"id": f.get("id"), "type": f.get("type"), "room_id": f.get("room_id")})
    return out


def added_pieces(before: Optional[dict], after: Optional[dict]) -> list[dict]:
    """Fix round after P5: ``[{id, type, room_id}]``: the pieces of ``after`` in the scene (``in_scene``) that
    ``before`` does not have there as the same type (new, built again, or typed differently); the mirror of
    ``removed_pieces``. Pure."""
    then = {f.get("id"): f for f in (before or {}).get("furniture") or [] if isinstance(f, dict)}
    out = []
    for f in (after or {}).get("furniture") or []:
        if not in_scene(f):
            continue
        g = then.get(f.get("id"))
        if g is None or not in_scene(g) or g.get("type") != f.get("type"):
            out.append({"id": f.get("id"), "type": f.get("type"), "room_id": f.get("room_id")})
    return out


def piece_types(*buildings: Optional[dict]) -> dict[str, str]:
    """Fix round after P5 (22 Oct 2026), review: ``{piece id: type}`` of every piece of ``buildings`` (a later
    building's type wins), for the S2 partner rule of ``recreated_finding`` (``edit["types"]``). Pure."""
    out: dict[str, str] = {}
    for b in buildings:
        for f in (b or {}).get("furniture") or []:
            if isinstance(f, dict) and f.get("id") is not None:
                out[str(f["id"])] = str(f.get("type"))
    return out


def _as_severe(finding: dict, target: dict) -> bool:
    """Fix round after P5, review: ``finding`` is critical or major, or at least as severe as ``target``."""
    rank = SEVERITY_ORDER.get(str(finding.get("severity")), 3)
    return rank <= max(SEVERITY_ORDER["major"], SEVERITY_ORDER.get(str(target.get("severity")), 3))


def recreated_finding(target: tuple, before_by: dict, after_by: dict, removed: list[dict],
                      added: list[dict], types: Optional[dict] = None) -> Optional[tuple[tuple, dict]]:
    """Fix round after P5: ``(key, piece)`` of a finding of ``after_by`` with the same check as the target finding
    ``target`` on a piece the edit added (``added``) of the type and room of the target's piece the edit removed
    (``removed``), else None: the same finding on the same piece under a new id (P5's relayout_room re-created the
    console table f_L1_049 as f_L1_056 under the same 0.82 m slope).

    Fix round after P5 (22 Oct 2026), review: the finding after the edit counts only when it is critical or major
    (or at least as severe as the target), and an S2 only when it is the same cut: a wall cut of the same wall
    (``metrics.wall_id``), a piece cut (``metrics.other``) with the same partner or a partner of the same type
    (``types``: ``{id: type}``, ``piece_types``; the removed and added records count too), whichever of the two
    pieces the check names (the re-created piece may be its ``other``). Why: a dining-room relayout that cleared the
    major wall cut S2:f_9/w_3 re-created the chairs as f_20 / f_21, which touch each other within tolerance (a minor
    S2:f_20/f_21); the edit was refused as "still there", although the same-id rule (``kept``) compares the cut
    too."""
    finding = before_by.get(target) or {}
    gone = next((p for p in removed if p.get("id") == finding.get("target")), None)
    if gone is None:
        return None
    kinds = {str(p.get("id")): str(p.get("type")) for p in list(removed) + list(added) if p.get("id") is not None}
    kinds.update({str(k): str(v) for k, v in (types or {}).items()})

    def recreated(pid) -> Optional[dict]:
        return next((p for p in added if p.get("id") == pid and p.get("type") == gone.get("type")
                     and p.get("room_id") == gone.get("room_id")), None)

    def same_partner(pid, partner) -> bool:
        if pid is None or partner is None:
            return False
        if str(pid) == str(partner):
            return True
        return kinds.get(str(pid)) is not None and kinds.get(str(pid)) == kinds.get(str(partner))

    was = _metrics(finding)
    for key in sorted(after_by):
        f = after_by[key]
        if key[0] != target[0] or f.get("target") == gone.get("id") or not _as_severe(f, finding):
            continue
        now = _metrics(f)
        if target[0] != "S2" or not (was.get("wall_id") or was.get("other")):
            hit = recreated(f.get("target"))
        elif was.get("wall_id"):
            hit = recreated(f.get("target")) if now.get("wall_id") == was.get("wall_id") else None
        else:
            hit = recreated(f.get("target")) if same_partner(now.get("other"), was.get("other")) else None
            if hit is None and same_partner(f.get("target"), was.get("other")):
                hit = recreated(now.get("other"))          # the check names the partner, the re-created piece is other
        if hit is not None:
            return key, hit
    return None


def _set_kind(finding: dict) -> Optional[str]:
    missing = _metrics(finding).get("missing")
    return None if missing is None else str(missing)


def _set_key(finding: dict) -> tuple[str, str, str]:
    return finding_key(finding) + (str(_set_kind(finding) or _text(finding)),)


def _kind_types(kind: Optional[str], text: str) -> set:
    """The piece types a room-set finding asks for: from ``metrics.missing``, else the words of its message."""
    if kind is not None:
        return set(SET_KIND_TYPES.get(kind) or kind.split("|"))
    words = set(text.replace("/", " ").replace("(", " ").replace(")", " ").split())
    out: set = set()
    for k, types in SET_KIND_TYPES.items():
        if k in words or words & set(types):
            out |= set(types)
    return out


def removed_fixture_findings(before: list[dict], after: list[dict], removed: list[dict]) -> list[tuple[dict, dict]]:
    """``[(finding, piece)]``: the critical / major room-set findings (``ROOM_SET_CHECKS``) of ``after`` that are new
    against ``before`` (by check, target and missing kind) and ask for a fixture the edit removed (``removed``:
    ``removed_pieces``) in the same room."""
    if not removed:
        return []
    seen = {_set_key(f) for f in before or [] if str(f.get("check") or f.get("checklist")) in ROOM_SET_CHECKS}
    out = []
    for f in after or []:
        if str(f.get("check") or f.get("checklist")) not in ROOM_SET_CHECKS or \
                f.get("severity") not in ("critical", "major") or _set_key(f) in seen:
            continue
        types = _kind_types(_set_kind(f), _text(f))
        hit = next((p for p in removed if p.get("type") in types and (
            not f.get("room_id") or not p.get("room_id") or p.get("room_id") == f.get("room_id"))), None)
        if hit is not None:
            out.append((f, hit))
    return out


def findings_removed(before: list[dict], after: list[dict], severities=("critical", "major")) -> int:
    """How many finding keys of ``before`` with a severity in ``severities`` are gone in ``after``."""
    after_keys = {finding_key(f) for f in after or []}
    gone = {finding_key(f) for f in before or [] if f.get("severity") in severities} - after_keys
    return len(gone)


def findings_new(before: list[dict], after: list[dict], severities=("critical", "major")) -> int:
    """Fix round after P6a: how many finding keys of ``after`` with a severity in ``severities`` are not in
    ``before`` (the dry re-check's new findings; ``findings_removed`` minus this is the predicted net)."""
    before_keys = {finding_key(f) for f in before or []}
    return len({finding_key(f) for f in after or [] if f.get("severity") in severities} - before_keys)


SEVERE = ("critical", "major")


def _on_targets(finding: dict, targets: set) -> bool:
    """Fix round after P6a: ``finding`` is on one of ``targets``: its target, or for an S2 the partner of its cut
    (``metrics.other``)."""
    if str(finding.get("target")) in targets:
        return True
    check = str(finding.get("check") or finding.get("checklist") or "")
    return check == "S2" and _metrics(finding).get("other") is not None and str(_metrics(finding)["other"]) in targets


def _severe_counts(findings: list[dict]) -> tuple[int, int]:
    return (sum(1 for f in findings if f.get("severity") == "critical"),
            sum(1 for f in findings if f.get("severity") == "major"))


def same_target_swap(before_by: dict, after_by: dict, present: list) -> Optional[tuple[list[dict], list[dict]]]:
    """Fix round after P6a (module docstring): ``(new, gone)`` when the dry re-check shows a new critical or major
    finding on a target of the edit (the target of a finding in ``present``; an S2 counts on its partner too) and the
    critical / major findings gone there are not more (critical first, then major: ``(1, 0)`` gone and ``(0, 1)`` new
    is a downgrade, accepted); else None. ``before_by`` / ``after_by``: ``{finding_key: finding}``."""
    targets = {str((before_by.get(t) or {}).get("target")) for t in present} - {"None"}
    if not targets:
        return None
    new = [after_by[k] for k in sorted(after_by) if k not in before_by
           and after_by[k].get("severity") in SEVERE and _on_targets(after_by[k], targets)]
    if not new:
        return None
    gone = [before_by[k] for k in sorted(before_by) if k not in after_by
            and before_by[k].get("severity") in SEVERE and _on_targets(before_by[k], targets)]
    return (new, gone) if _severe_counts(new) >= _severe_counts(gone) else None


def critical_cleared(present: list, kept: list, before_by: dict, after_by: dict) -> Optional[list]:
    """Fix round after P6b (module docstring): ``kept`` (the targets still in the dry re-check) when the edit may keep
    them: at least one target is critical, every critical target is gone, at least one of the gone criticals is
    measured by code (its source is not ``vision``: a vision finding on a changed target counts as gone unmeasured),
    and no kept target became more severe; else None (the edit is refused "still there", as before). An all-major step
    keeps the old rule (every target gone; real02 / real04 logs: 14 edits it would let through, overlaps left).
    26 Oct 2026: "vision" is every source an AI made by looking (``is_vision``: the judge's, the inspector's too)."""
    crit = [t for t in present if (before_by.get(t) or {}).get("severity") == "critical"]
    if not crit or any(t in after_by for t in crit):
        return None
    if not any(not is_vision(before_by.get(t) or {}) for t in crit):
        return None
    for t in kept:
        if SEVERITY_ORDER.get(str(after_by[t].get("severity")), 3) < \
                SEVERITY_ORDER.get(str((before_by.get(t) or {}).get("severity")), 3):
            return None
    return list(kept)


def kept_text(kept: list, after_by: dict) -> str:
    """Fix round after P6b: ``"<check:target> (<severity>), ..."`` of the kept targets of an accepted edit."""
    return ", ".join(f"{_fmt(t)} ({(after_by.get(t) or {}).get('severity')})" for t in kept)


def expand_targets(targets: list, before_by: dict) -> list:
    """Fix round after P4a: the target keys with an S2 target without its cut (a caller that passes no metrics)
    standing for every cut of its piece among ``before_by`` (``{finding_key: finding}``), as the old (check, target)
    key did; duplicates dropped, order kept. Fix round after P6b, review: shared by ``accept_edit`` and
    ``kept_targets``."""
    expanded: list = []
    for t in targets:
        cuts = [] if t in before_by or t[0] != "S2" or S2_KEY_SEP in t[1] else \
            [k for k in before_by if k[0] == "S2" and base_key(k) == t]
        expanded += cuts or [t]
    return list(dict.fromkeys(expanded))


def kept_targets(before: list[dict], after: list[dict], edit: dict) -> list[tuple[str, str]]:
    """Fix round after P6b (23 Oct 2026), review: the target keys of ``edit`` as ``accept_edit`` reads them
    (``target_keys``, ``expand_targets``) that are among ``before`` and stay in ``after``: the targets an accepted
    edit kept (``critical_cleared``; the loop's acceptance record ``kept``, which ``metrics.edit_target_keys``
    leaves out)."""
    before_by = {finding_key(f): f for f in before or []}
    after_keys = {finding_key(f) for f in after or []}
    return [t for t in expand_targets(target_keys(edit), before_by) if t in before_by and t in after_keys]


def accept_edit(before: list[dict], after: list[dict], edit: dict) -> tuple[bool, str]:
    """``(accepted, reason)`` of one edit from the findings before it and the dry re-check after it (module
    docstring). Pure: nothing is changed."""
    targets = target_keys(edit)
    if not targets:
        return False, "no target finding: an edit must name the finding it fixes (check id and target id)"
    before_by = {finding_key(f): f for f in before or []}
    after_by = {finding_key(f): f for f in after or []}
    targets = expand_targets(targets, before_by)
    present = [t for t in targets if t in before_by]
    if not present:
        return False, (f"target finding {', '.join(_fmt(t) for t in targets)} is not among the findings before the "
                       f"edit: nothing to fix there")
    kept = [t for t in present if t in after_by]
    # fix round after P6b (module docstring): every targeted critical gone, measured by code, lets majors stay
    if kept and critical_cleared(present, kept, before_by, after_by) is None:
        f = after_by[kept[0]]
        return False, (f"finding {_fmt(kept[0])} is still there after the edit ({str(f.get('message') or f.get('finding') or '')[:160]})"
                       + (f"; {len(kept) - 1} more kept" if len(kept) > 1 else ""))
    # fix round after P5 (module docstring): a removed piece re-created under a new id keeps its finding
    for t in present:
        again = recreated_finding(t, before_by, after_by, list(edit.get("removed") or []),
                                  list(edit.get("added") or []), edit.get("types"))
        if again is not None:
            key, p = again
            f = after_by[key]
            return False, (f"finding {_fmt(t)} is still there after the edit as {_fmt(key)}: the edit re-created "
                           f"{p.get('type')} {(before_by.get(t) or {}).get('target')} as {p.get('id')} in "
                           f"{p.get('room_id')} ({str(f.get('message') or f.get('finding') or '')[:140]})")
    new_critical = sorted(k for k, f in after_by.items() if f.get("severity") == "critical" and k not in before_by)
    if new_critical:
        f = after_by[new_critical[0]]
        return False, (f"new critical finding {_fmt(new_critical[0])}: "
                       f"{str(f.get('message') or f.get('finding') or '')[:160]}"
                       + (f"; {len(new_critical) - 1} more" if len(new_critical) > 1 else ""))
    # Round 4 (module docstring): an edit that removed a fixture the room needs is refused even when the room-set
    # finding it creates is only major (real03 pre-flight: 5 toilets marked as not furniture, 5 G10 "bathroom without
    # a toilet" accepted).
    lost = removed_fixture_findings(before, after, list(edit.get("removed") or []))
    if lost:
        f, p = lost[0]
        return False, (f"new {f.get('severity')} finding {_fmt(finding_key(f))} "
                       f"({str(f.get('message') or f.get('finding') or '')[:120]}): the edit removed {p.get('type')} "
                       f"{p.get('id')}, the fixture the room needs; fixed equipment is treated like walls (CLAUDE.md "
                       f"furniture rules)" + (f"; {len(lost) - 1} more" if len(lost) > 1 else ""))
    # Fix round after P6a (module docstring): a finding traded for another as severe on the same piece is no removal
    swap = same_target_swap(before_by, after_by, present)
    if swap is not None:
        new, gone = swap
        f = new[0]
        return False, (f"swap: {_fmt(finding_key(f))} replaces "
                       f"{', '.join(_fmt(finding_key(g)) for g in gone) or 'nothing'} on {f.get('target')} "
                       f"({str(f.get('message') or f.get('finding') or '')[:120]}): the piece keeps as many critical / "
                       f"major findings, so nothing is removed" + (f"; {len(new) - 1} more new" if len(new) > 1 else ""))
    pb, pa = _penalties(edit)
    if pb is not None and pa is not None and pa > pb + 1e-9:
        return False, (f"plausibility penalty rose {pb:g} -> {pa:g} (the old score rule, kept as the second "
                       f"condition)")
    removed = findings_removed(before, after)
    new_count = findings_new(before, after)
    gone = [t for t in present if t not in kept]
    # fix round after P3: the dry re-check's count is a prediction; the next round's critics measure it; fix round
    # after P6a: the new critical / major findings and the net are named too; fix round after P6b: and the kept targets
    return True, (f"finding {', '.join(_fmt(t) for t in gone)} gone in the dry re-check; no new critical "
                  f"finding; {removed} critical/major finding(s) removed"
                  + (f", {new_count} new (net {removed - new_count})" if new_count else "")
                  + " (predicted; the next round measures)"
                  + (f"; kept: {kept_text(kept, after_by)}" if kept else ""))


def key_list(findings: list[dict], severities=("critical", "major"), limit: int = 60) -> list[str]:
    """Short ``check:target`` strings of the findings (the log's before/after lists of an edit), the most severe
    first, at most ``limit``."""
    items = sorted((f for f in findings or [] if f.get("severity") in severities),
                   key=lambda f: (SEVERITY_ORDER.get(f.get("severity"), 3), finding_key(f)))
    out: list[str] = []
    for f in items:
        s = _fmt(finding_key(f))
        if s not in out:
            out.append(s)
    return out[:limit]
