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
    "unknown": "no agent tool fixes this check",
}
# Fix round after P3: cause -> the stage a finding no agent tool fixes is reported to (the loop logs it on the
# finding event as ``report_to``). Fix round after P4a: a light fixture's look goes to the lighting stage.
REPORT_TO: dict[str, str] = {"decor_under_roof": "decor", "decor_rest": "decor", "light_fixture": "lighting",
                             # fix round after P4b: a frozen replayed camera, a decor light's model
                             "replayed_camera": "cameras", "decor_model": "decor",
                             # fix round after P5: a blocked view the camera search could not avoid
                             "blocked_unavoidable": "cameras"}
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
    "S6": "wrong_model", "LG": "library_gap", "NR": "untyped", "RC": "wrong_type",
    "X1": "geometry", "X2": "roof", "X3": "facade", "X4": "site", "X5": "scale", "X6": "exterior_camera",
    "X7": "sun", "X8": "material",
    "V1": "interior_camera", "V2": "render_match", "V3": "debug_marker", "V4": "polish",
    "L1": "entrance", "L2": "entrance", "L3": "terrain", "L4": "levels", "L5": "entrance", "L6": "terrain",
    "L7": "exterior_camera",
    "D1": "decor_look", "D2": "wrong_model",
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


def accept_edit(before: list[dict], after: list[dict], edit: dict) -> tuple[bool, str]:
    """``(accepted, reason)`` of one edit from the findings before it and the dry re-check after it (module
    docstring). Pure: nothing is changed."""
    targets = target_keys(edit)
    if not targets:
        return False, "no target finding: an edit must name the finding it fixes (check id and target id)"
    before_by = {finding_key(f): f for f in before or []}
    after_by = {finding_key(f): f for f in after or []}
    # fix round after P4a: an S2 target without its cut (a caller that passes no metrics) stands for every cut of its
    # piece, as the old (check, target) key did
    expanded: list = []
    for t in targets:
        cuts = [] if t in before_by or t[0] != "S2" or S2_KEY_SEP in t[1] else \
            [k for k in before_by if k[0] == "S2" and base_key(k) == t]
        expanded += cuts or [t]
    targets = list(dict.fromkeys(expanded))
    present = [t for t in targets if t in before_by]
    if not present:
        return False, (f"target finding {', '.join(_fmt(t) for t in targets)} is not among the findings before the "
                       f"edit: nothing to fix there")
    kept = [t for t in present if t in after_by]
    if kept:
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
    pb, pa = _penalties(edit)
    if pb is not None and pa is not None and pa > pb + 1e-9:
        return False, (f"plausibility penalty rose {pb:g} -> {pa:g} (the old score rule, kept as the second "
                       f"condition)")
    removed = findings_removed(before, after)
    # fix round after P3: the dry re-check's count is a prediction; the next round's critics measure it
    return True, (f"finding {', '.join(_fmt(t) for t in present)} gone in the dry re-check; no new critical "
                  f"finding; {removed} critical/major finding(s) removed (predicted; the next round measures)")


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
