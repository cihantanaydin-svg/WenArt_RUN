"""Causes of findings, the tools per cause and the acceptance rule of an edit (docs/milestone13.md §1.5, §3.0 K4,
§13.2 rows ``loop.py`` and ``edit_ops.py``; CLAUDE.md evidence rule: "an agent edit is accepted only when the finding
it targets is gone in the dry re-check and no new critical finding appears").

What:

- ``cause_of(finding, building=None) -> str``: the cause behind a finding (``CAUSES``). The check id gives the family;
  the finding's metrics, message and target decide the rest: an F8 chair around an unbuilt table is
  ``missing_anchor`` (not ``floating``: moving the chair never helped, real04 0 of 24), an S2 cut below
  ``S2_TOLERANCE_M`` (0.03 m) is ``within_tolerance`` (invisible: 0 of 39 swaps helped), an X2 piece under the sloped
  roof is ``under_roof`` (move or lower the piece), an X2 on the roof itself is ``roof`` (building-wide).
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
  new in ``after``, and (3) the old rule as a second condition: the plausibility penalty did not rise (the M12 rule
  of ``edit_ops.apply_edit`` was the only rule; 139 of 183 accepted edits left the score unchanged, 125 of 160 left
  their finding in place).
- ``findings_removed(before, after, severities=("critical", "major"))``: how many finding keys of ``before`` are
  gone in ``after`` (the success number of the loop and the metrics; "edits accepted" is none).

Why: real04 (M12, §1.5) accepted 183 edits of which 20 removed their finding; the tools were mapped by check id
(``brief.CHECK_TOOLS``), so every room session got every tool for every check whatever the cause.

How: pure functions of dicts, a finding key is ``(check, target)`` (a finding dict of the critics or an ``edit`` /
``finding`` event of the log: ``check`` or ``checklist``, ``message`` or ``finding``); deterministic.
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
    "missing_anchor": ("place_group", "report_library_gap"),
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
    "room_type": ("set_room_type",),
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
    "facade": (),
    "decor_rest": (),
    "render_match": (),
    "debug_marker": (),
    "ceiling": (),
    "scale": (),
    "polish": (),
    "unknown": (),
}
CAUSES: tuple[str, ...] = tuple(CAUSE_TOOLS)
NO_TOOL_REASON: dict[str, str] = {
    "within_tolerance": f"within tolerance: a cut below {S2_TOLERANCE_M:.2f} m is not visible (S2 class tolerance); "
                        "no tool is offered",
    "facade": "the facade openings come from the drawings; no agent tool",
    "decor_rest": "decor rest is placed by the decor stage on the built mesh (S5): no agent tool",
    "render_match": "the render/JSON match is checked by the final check",
    "debug_marker": "debug markers are a build setting, not an agent edit",
    "ceiling": "ceiling heights come from the drawings",
    "scale": "storey and door sizes come from the drawings",
    "polish": "the polish check is a build setting",
    "unknown": "no agent tool fixes this check",
}
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
}
_PIECE_PREFIXES = ("f_", "furn_", "decor_", "dec_")
_MISSING_WORDS = ("missing", " no ", "without", "lacks", "needs a", "has no", " only")


def _text(finding: dict) -> str:
    return str(finding.get("message") or finding.get("finding") or "").lower()


def _metrics(finding: dict) -> dict:
    ev = finding.get("evidence") if isinstance(finding.get("evidence"), dict) else {}
    m = ev.get("metrics") if isinstance(ev.get("metrics"), dict) else finding.get("metrics")
    return m if isinstance(m, dict) else {}


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
            return "missing_anchor"
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
        if "overlap" in text or "through a wall" in text or metrics.get("overlap_m2") or metrics.get("other"):
            return "collision"
        if "float" in text or "middle of the room" in text:
            return "floating"
        if "duplicate" in text:
            return "wrong_type"
        return "wrong_type"
    if check == "X2":
        if _is_piece(target, building):
            return "under_roof"
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
        return "fixture_clearance"
    if check == "V1":
        return "exterior_camera" if str(target or "").startswith(EXTERIOR_VIEW_PREFIX) else "interior_camera"
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


# --------------------------------------------------------------------------
# Acceptance
# --------------------------------------------------------------------------

def finding_key(finding: dict) -> tuple[str, str]:
    """``(check, target)``: the identity of a finding across rounds (the ids of vision findings change per call)."""
    return (str(finding.get("check") or finding.get("checklist") or "?"), str(finding.get("target")))


def _fmt(key) -> str:
    return f"{key[0]}:{key[1]}"


def target_keys(edit: dict) -> list[tuple[str, str]]:
    """The finding keys an edit targets: ``edit["target_finding"]`` (a dict or a list of dicts with ``check`` and
    ``target``), else ``edit["target_findings"]``; [] without one."""
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
    present = [t for t in targets if t in before_by]
    if not present:
        return False, (f"target finding {', '.join(_fmt(t) for t in targets)} is not among the findings before the "
                       f"edit: nothing to fix there")
    kept = [t for t in present if t in after_by]
    if kept:
        f = after_by[kept[0]]
        return False, (f"finding {_fmt(kept[0])} is still there after the edit ({str(f.get('message') or f.get('finding') or '')[:160]})"
                       + (f"; {len(kept) - 1} more kept" if len(kept) > 1 else ""))
    new_critical = sorted(k for k, f in after_by.items() if f.get("severity") == "critical" and k not in before_by)
    if new_critical:
        f = after_by[new_critical[0]]
        return False, (f"new critical finding {_fmt(new_critical[0])}: "
                       f"{str(f.get('message') or f.get('finding') or '')[:160]}"
                       + (f"; {len(new_critical) - 1} more" if len(new_critical) > 1 else ""))
    pb, pa = _penalties(edit)
    if pb is not None and pa is not None and pa > pb + 1e-9:
        return False, (f"plausibility penalty rose {pb:g} -> {pa:g} (the old score rule, kept as the second "
                       f"condition)")
    removed = findings_removed(before, after)
    return True, (f"finding {', '.join(_fmt(t) for t in present)} gone in the dry re-check; no new critical "
                  f"finding; {removed} critical/major finding(s) removed")


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
