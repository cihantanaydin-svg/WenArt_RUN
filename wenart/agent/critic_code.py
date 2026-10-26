"""The code critic (docs/milestone11.md §4, §8 step 1; docs/milestone12.md §5.4): every checklist item that code can
measure.

What: ``run(building, scene_manifest, render_manifest, scene_dir=...)`` calls

- ``wenart.furniture.plausibility.score_building`` (F1–F9, R1–R4 per room),
- ``wenart.blender.exterior_checks.check_exterior`` (X1–X8) and ``check_views`` (V1, V3),
- Milestone 12: ``wenart.furniture.group_checks.check_building`` (track G: G1–G14), ``wenart.levels.checks.
  check_levels`` (track L: L1–L7), the scene checks the build wrote (track S: ``<scene_dir>/scene_<level>.json``,
  S1–S6) and the library gaps of the built pieces (``furniture[].library_gap``: check ``LG``),

and turns their violations (``{check, severity, target, room_id, message, metrics}``, contract §17.2 / §13.2) into
findings ``{id, source: "code", check, severity, target, room_id, message, evidence: {metrics}}``. It also returns
one record per check family (``status`` ok / unavailable / error) and the room scores.

Why: code is cheap (milliseconds), exact and the first judge; the vision critic only adds what an image shows and
gets these findings so it does not repeat them (``critic_vision``). The G-, L- and S-findings carry the numbers of
the arrangement checks M11 did not have (§1.2 "not checked by any rule today").

How: a family whose function is not built yet (``NotImplementedError``) or fails is recorded as ``unavailable`` /
``error`` and the loop goes on with the rest; the functions are injectable (tests). A violation without a room id
gets the room of its target piece. Finding ids are stable (``c:<check>:<target>``, a counter for repeats), so the
same problem keeps its id from round to round (the memory and the metrics rely on it).

Milestone 13, round 4 (before pod P3's second attempt): the ``lighting`` family reads the render manifest's
``lighting_dark`` entries (``lighting_items``; ``wenart.blender.render.lighting_dark_entry``: a view whose metered
EV passed the +3 cap, major, critical from 2 stops over; written per view and in the manifest's list). Each becomes a
finding on the camera with its room, the metered EV, the cap and the light factor the room would need
(``factor_needed`` = 2 ** stops over the cap); ``causes.cause_of`` routes it to ``set_lighting`` (an exterior view:
report-only). Before this nothing in the agent read them (CPU pre-flight of 16 Oct 2026: real04's basement salon
wanted +6.37 EV, 3.37 stops over the cap, and no finding reached the agent or the report).

Fix round after P3 (16-17 Oct 2026; docs/milestone13.md §14.8 "Attempt 2"):

- a ``lighting_dark`` finding asks for headroom: the message suggests ``min(x3, needed x LIGHTING_HEADROOM)``
  (``metrics.set_lighting_suggested``; ``LIGHTING_HEADROOM`` = 2 ** 0.5, half a stop), while
  ``set_lighting_factor`` (what the view needs) stays the acceptance threshold of ``loop.lighting_kept`` and the
  ``lighting_beyond_cap`` rule of ``causes.cause_of``. Why: P3's next renders gained 0.1-1.3 stops where x2.8-2.87
  predicted about 1.5 (part of a view's light does not scale with the room's lights), so the planner set x2.83 and
  then x2.95 on the same room; asking once for the headroom (often x3, the maximum) saves the second round;
- a violation on a decor piece gets the decor's room (before: furniture only; P3's X2 on the mirror dec_L1_009 had
  no room and went to the building session).

Fix round after P4a (17 Oct 2026; pod P4a, real02): an S2 cut below ``causes.S2_TOLERANCE_M`` (0.03 m, the cause
``within_tolerance``: invisible, no tool) is a MINOR finding (``within_tolerance_minor``; ``metrics.severity_was``
keeps the build's severity). Why: the build's default S2 tolerance is 0.010 m, so P4a logged 6-7 such cuts per round
as major findings no tool may fix; they inflated every round's major count and the report's "reported" rows.
Integration of the same round (the furniture track's ask): ``library_gaps`` leaves out a piece built from code by
design (``asset.by_design`` or ``catalog.by_design_parametric``: kitchen runs, stairs, sanitary fixtures, a vanity, a
built-in wardrobe), the rule of the final report's "built below library level" list (``report.final``), so the agent
and the report agree. P4a raised LG for the showers f_L0_013 / f_L0_014, which the report lists as "no (by design)".

Fix round after P4b (17 Oct 2026; pod P4b, real03): a ``lighting_dark`` view less than one exposure step
(``LIGHTING_STEP_STOPS`` = 1/6 stop, ``wenart.blender.render.EXPOSURE_STEP``) over the cap is a MINOR finding with
``metrics.below_exposure_step`` (``metrics.severity_was`` keeps the render's severity) and the message says it is
reported only; ``causes.cause_of`` gives it the cause ``lighting_within_step`` (no tool). Why: P4b re-lit and
re-rendered cam_r_L0_giris_holu_2_1 (0.01 stops over), giris_holu_4_2 and yasama_7_1 (0.04): the render rounds the
EV to 1/6 stop, so such a view is at the cap once rounded. The render side (whether the render raises it at all) is
the render track's.

Fix round after P5 (22 Oct 2026; pod P5, real04): the ``blocked`` family reads the render manifest's depth and index
statistics of every interior preview (``blocked_items``): a view whose nearest depth is within ``LENS_TOUCH_M``
(0.01 m) of the camera's clip start (the lens touches a surface) is CRITICAL, a view one element fills over
``camsearch.SCORE["blocked_single"]`` (0.50) of the frame is MAJOR; the finding ``camera_blocked`` names the element
(``pass_index``), the depth and the share, and goes to the camera tools (``causes``: ``interior_camera``; a
replayed camera is frozen, ``replayed_camera``). A view the camera search already marked unavoidable (its scene
camera's warning holds ``camsearch.BLOCKED_WARNING``, which the GPU test allows) is minor with
``metrics.blocked_unavoidable`` and reported only. Exterior views are left out (a facade fills them by design, as in
the GPU test). Why: P5's cam_r_L1_banyo_1 preview had depth min 0.0502 m (clip start 0.05) and the ceiling light
dec_L1_011 filling 55.7 % of the frame in every round; nothing in the agent read depth or index, the vision critic
kept 0 findings for the room, and three GPU tests failed on it. Fix round after P5 (22 Oct 2026), review: a nearest
depth of ``RENDER_MIN_DEPTH_M`` (0.1 m, the GPU render test's bound) or less is critical as well, so no view the
render test fails on depth passes the agent's rounds.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Optional

from wenart.agent.prompts import CHECKLIST, SEVERITIES

SCENE_CHECKS_GLOB = "scene_*.json"          # track S: <build --out>/checks/scene_<level>.json
# The build stage writes the scene to outputs/<p>/scene (``--out``), so its checks land in scene/checks; the
# contract (§13.3) names build/checks: both are read, the first one with scene checks wins.
SCENE_CHECKS_DIRS = (Path("scene") / "checks", Path("build") / "checks")
SCENE_CHECKS_DIR = SCENE_CHECKS_DIRS[0]
LIBRARY_GAP_CHECK = "LG"
REST_CHECK = "S5"


def scene_checks_dir(project_out) -> Path:
    """The folder of the build's scene checks (``SCENE_CHECKS_DIRS``, the first with a ``scene_*.json``)."""
    for rel in SCENE_CHECKS_DIRS:
        folder = Path(project_out) / rel
        if folder.is_dir() and any(folder.glob(SCENE_CHECKS_GLOB)):
            return folder
    return Path(project_out) / SCENE_CHECKS_DIR


def manifest_summary(scene_manifest: Optional[dict]) -> dict:
    """What the build's furniture summary says about the scene checks (track S): ``scene_checks`` (counts per
    level), ``scene_checks_failed``, ``dressed_beds`` and ``decor_not_rested`` (counts; {} without a manifest)."""
    furn = (scene_manifest or {}).get("furniture") or {}
    if not isinstance(furn, dict) or not furn:
        return {}
    return {"scene_checks": furn.get("scene_checks") or {},
            "scene_checks_failed": bool(furn.get("scene_checks_failed")),
            "dressed_beds": len(furn.get("dressed_beds") or []),
            "decor_not_rested": len(furn.get("decor_not_rested") or [])}


def manifest_violations(scene_manifest: Optional[dict], scene: list[dict]) -> list[dict]:
    """Findings from the build's furniture summary: one minor ``S5`` per decor item the build did not make because
    it did not rest on its host (``decor_not_rested``: the room misses it; target its host), and one critical
    ``S5`` when the build says a built item failed S5 (``scene_checks_failed``) but no S5 violation was read."""
    furn = (scene_manifest or {}).get("furniture") or {}
    if not isinstance(furn, dict):
        return []
    out = []
    for rec in furn.get("decor_not_rested") or []:
        if not isinstance(rec, dict):
            continue
        out.append({"check": REST_CHECK, "severity": "minor", "target": rec.get("host_id") or rec.get("id"),
                    "room_id": rec.get("room_id"),
                    "message": f"decor {rec.get('type')} {rec.get('id')} on {rec.get('host_id')} did not rest "
                               f"({rec.get('reason')}); it is not built",
                    "metrics": {k: rec.get(k) for k in ("id", "type", "support", "attempts")
                                if rec.get(k) is not None}})
    if furn.get("scene_checks_failed") and not any(v.get("check") == REST_CHECK for v in scene):
        out.append({"check": REST_CHECK, "severity": "critical", "target": None, "room_id": None,
                    "message": "the build says a built decor item failed the rest check S5 (no scene check file read)",
                    "metrics": {}})
    return out


def _default(name: str) -> Callable:
    if name == "plausibility":
        from wenart.furniture import plausibility
        return plausibility.score_building
    if name == "groups":
        from wenart.furniture import group_checks
        return group_checks.check_building
    if name == "levels":
        from wenart.levels import checks
        return checks.check_levels
    from wenart.blender import exterior_checks
    return getattr(exterior_checks, name)


def finding(v: dict, source: str = "code", prefix: str = "c") -> dict:
    check = str(v.get("check") or "?")
    severity = v.get("severity") if v.get("severity") in SEVERITIES else (
        CHECKLIST.get(check, {}).get("severity") or "minor")
    target = v.get("target")
    return {"id": f"{prefix}:{check}:{target}", "source": source, "check": check, "severity": severity,
            "target": None if target is None else str(target), "room_id": v.get("room_id"),
            "message": str(v.get("message") or CHECKLIST.get(check, {}).get("what") or check),
            "evidence": {"metrics": dict(v.get("metrics") or {})}}


def _unique(findings: list[dict]) -> list[dict]:
    seen: dict = {}
    for f in findings:
        n = seen.get(f["id"], 0)
        seen[f["id"]] = n + 1
        if n:
            f["id"] = f"{f['id']}#{n + 1}"
    return findings


def within_tolerance_minor(v: dict) -> dict:
    """Fix round after P4a (module docstring): an S2 violation whose cut (``metrics.depth_m``) is below
    ``causes.S2_TOLERANCE_M`` becomes minor, with ``metrics.severity_was`` and ``metrics.within_tolerance``; any other
    violation is returned as it is."""
    from wenart.agent.causes import S2_TOLERANCE_M
    metrics = v.get("metrics") if isinstance(v.get("metrics"), dict) else {}
    if str(v.get("check")) != "S2" or v.get("severity") == "minor":
        return v
    try:
        depth = float(metrics["depth_m"])
    except (KeyError, TypeError, ValueError):
        return v
    if depth >= S2_TOLERANCE_M - 1e-9:
        return v
    return dict(v, severity="minor", metrics=dict(metrics, severity_was=v.get("severity"), within_tolerance=True))


def scene_violations(scene_dir) -> list[dict]:
    """The violations of every ``scene_<level>.json`` in ``scene_dir`` (track S); FileNotFoundError without one."""
    folder = Path(scene_dir)
    files = sorted(folder.glob(SCENE_CHECKS_GLOB)) if folder.is_dir() else []
    if not files:
        raise FileNotFoundError(f"no scene checks in {folder}")
    out = []
    for path in files:
        data = json.loads(path.read_text(encoding="utf-8"))
        out += [v for v in data.get("violations") or [] if isinstance(v, dict)]
    return out


def library_gaps(building: dict) -> list[dict]:
    """One ``LG`` violation (minor) per built piece whose fit found no audited model (``library_gap``, track S);
    fix round after P4a: none for a piece built from code by design (module docstring)."""
    from wenart.furniture import catalog as CAT

    out = []
    for f in building.get("furniture") or []:
        gap = f.get("library_gap")
        if not gap or f.get("build", True) is False:
            continue
        asset = f.get("asset") if isinstance(f.get("asset"), dict) else {}
        if asset.get("by_design") or CAT.by_design_parametric(f):
            continue
        g = gap if isinstance(gap, dict) else {"note": str(gap)}
        what = ", ".join(f"{k} {v}" for k, v in sorted(g.items()) if not isinstance(v, (dict, list)))[:200]
        out.append({"check": LIBRARY_GAP_CHECK, "severity": "minor", "target": f.get("id"),
                    "room_id": f.get("room_id"), "message": f"library gap for {f.get('type')}: {what or 'no model'}",
                    "metrics": {k: v for k, v in g.items() if isinstance(v, (int, float, str))}})
    return out


LIGHTING_DARK_CHECK = "lighting_dark"       # = wenart.blender.render.LIGHTING_DARK_CHECK (pinned by the tests)
# Fix round after P3: the factor a lighting_dark message suggests is the needed one x this (half a stop of headroom),
# capped at set_lighting's maximum; the acceptance still counts the view clear at the needed factor.
LIGHTING_HEADROOM = 2.0 ** 0.5
# Fix round after P4b (module docstring): an overage below one exposure step is minor and report-only.
LIGHTING_STEP_STOPS = 1.0 / 6.0             # = wenart.blender.render.EXPOSURE_STEP (pinned by the tests)


def lighting_items(render_manifest: Optional[dict], building: Optional[dict] = None) -> list[dict]:
    """Round 4: one ``lighting_dark`` violation per view of the render manifest whose metered EV passed the cap: the
    view entry's ``lighting_dark`` (or its ``exposure.lighting_dark``), else the manifest's ``lighting_dark`` list (the
    same records; one per camera). The render's message, severity, room and metrics are kept; ``metrics`` adds
    ``factor_needed`` (the light the room needs over now, 2 ** stops over the cap) and the message says what one
    ``set_lighting`` can give (``tools.LIGHTING_FACTOR``). FileNotFoundError without a render manifest (the family is
    then ``unavailable``, not a silent ok).

    Review of round 4: ``set_lighting``'s factor is absolute (the room's lights x factor over the default rig,
    ``wenart.blender.lighting.build_lighting``), and the render metered the room with the factor the building already
    has (``building``'s ``agent_overrides.lighting``, read by the build's own ``overrides.lighting_of``). So the factor
    to ask for is that factor x ``factor_needed`` (``metrics.set_lighting_factor``, with ``lighting_factor_now``);
    before, a room at x2 that was 0.87 stops over was told "set_lighting factor about x1.82", a darker room."""
    if not isinstance(render_manifest, dict):
        raise FileNotFoundError("no render manifest: the lighting_dark entries of the views are not known")
    from wenart.agent.tools import LIGHTING_FACTOR
    from wenart.blender.overrides import lighting_of

    now_of = lighting_of(building) if isinstance(building, dict) else {}

    by_camera: dict = {}
    for e in render_manifest.get("renders") or []:
        if not isinstance(e, dict):
            continue
        rec = e.get("lighting_dark") or (e.get("exposure") or {}).get("lighting_dark")
        if isinstance(rec, dict) and rec.get("target"):
            by_camera.setdefault(str(rec["target"]), dict(rec, room_id=rec.get("room_id") or e.get("room_id")))
    for rec in render_manifest.get("lighting_dark") or []:
        if isinstance(rec, dict) and rec.get("target"):
            by_camera.setdefault(str(rec["target"]), dict(rec))
    out = []
    top = float(LIGHTING_FACTOR[1])
    for cam in sorted(by_camera):
        rec = by_camera[cam]
        metrics = dict(rec.get("metrics") or {})
        message = str(rec.get("message") or f"{cam}: the view is too dark for the EV cap")
        try:
            over = float(metrics.get("stops_over_cap"))
        except (TypeError, ValueError):
            over = None
        severity = rec.get("severity") or "major"
        if over is not None and 0 < over < LIGHTING_STEP_STOPS - 1e-9:
            # fix round after P4b (module docstring): under one exposure step, report only
            metrics.update(below_exposure_step=True, severity_was=severity)
            severity = "minor"
            message += (f"; {over:.2f} stops is less than one exposure step ({LIGHTING_STEP_STOPS:.2f} stop): "
                        f"reported only, no set_lighting")
        elif over is not None and over > 0:
            need = round(2.0 ** over, 2)
            metrics["factor_needed"] = need
            if rec.get("room_id"):
                now = float((now_of.get(str(rec["room_id"])) or {}).get("factor") or 1.0)
                want = round(now * 2.0 ** over, 2)
                metrics["lighting_factor_now"] = now
                metrics["set_lighting_factor"] = want
                has = f"; it has x{now:g} now" if abs(now - 1.0) > 1e-9 else ""
                if want > top + 1e-9:
                    message += (f"; the room needs about x{need:g} its light, set_lighting gives up to x{top:g}"
                                + (f" ({has[2:]})" if has else ""))
                else:
                    # fix round after P3: ask for half a stop more than the view needs (module docstring)
                    ask = round(min(top, want * LIGHTING_HEADROOM), 2)
                    metrics["set_lighting_suggested"] = ask
                    message += (f"; set_lighting factor x{ask:g} on {rec['room_id']} (the view needs about "
                                f"x{want:g}; the headroom covers light that does not scale with the room's lights"
                                f"{has})")
        out.append({"check": LIGHTING_DARK_CHECK, "severity": severity, "target": cam,
                    "room_id": rec.get("room_id"), "message": message, "metrics": metrics})
    return out


CAMERA_BLOCKED_CHECK = "camera_blocked"     # = causes.CAMERA_BLOCKED_CHECK (fix round after P5)
LENS_TOUCH_M = 0.01                         # a nearest depth this close to the clip start: the lens touches a surface
# fix round after P5 (22 Oct 2026), review: the render test's bound (tests/gpu/test_render.py ``MIN_DEPTH_M``: every
# view needs its nearest surface farther than 0.1 m); a nearer surface is critical too
RENDER_MIN_DEPTH_M = 0.1


def blocked_items(render_manifest: Optional[dict], scene_manifest: Optional[dict] = None) -> list[dict]:
    """Fix round after P5 (module docstring): one ``camera_blocked`` violation per interior preview whose lens touches
    a surface (``depth.min`` <= ``clip.start_m`` + ``LENS_TOUCH_M``: critical) or whose frame one element fills over
    ``camsearch.SCORE["blocked_single"]`` (index pass, index 0 left out: major). FileNotFoundError without a render
    manifest (the family is then ``unavailable``).

    Fix round after P5 (22 Oct 2026), review: a nearest depth of ``RENDER_MIN_DEPTH_M`` (0.1 m, the GPU render test's
    bound) or less is critical too ("a surface is ... from the lens"); before, a view at 0.06-0.10 m had no finding
    and failed the render test after the last round (none of P4a, P4b, P5's previews lies there: P5's bathroom is at
    0.0502 m, real03's nearest at 0.112 m)."""
    if not isinstance(render_manifest, dict):
        raise FileNotFoundError("no render manifest: the depth and index of the views are not known")
    from wenart.blender import camsearch as CAM

    single_max = float(CAM.SCORE["blocked_single"])
    names = {int(v): str(k) for k, v in (render_manifest.get("pass_index") or {}).items()
             if isinstance(v, (int, float)) and not isinstance(v, bool)}
    cams = {str(c.get("name")): c for c in (scene_manifest or {}).get("cameras") or []
            if isinstance(c, dict) and c.get("name")}
    # a view carried from an earlier build was rendered from that build's scene: its index values may not be this
    # manifest's pass_index (P5's preview of cam_r_L1_banyo_1 has index 254, which this pass_index does not hold)
    carried = {str(c) for c in render_manifest.get("carried_from_earlier_build") or []}
    out = []
    for e in render_manifest.get("renders") or []:
        if not isinstance(e, dict) or not e.get("camera") or e.get("skipped"):
            continue
        cam = str(e["camera"])
        plan = cams.get(cam) or {}
        kind = plan.get("kind") or ("exterior" if cam.startswith("ext_") or not (e.get("room_id")
                                                                                 or plan.get("room_id"))
                                    else "interior")
        if kind == "exterior":
            continue
        depth = e.get("depth") if isinstance(e.get("depth"), dict) else {}
        clip = e.get("clip") if isinstance(e.get("clip"), dict) else {}
        try:
            near = float(depth["min"])
        except (KeyError, TypeError, ValueError):
            near = None
        start = float(clip.get("start_m") or 0.0)
        res = e.get("resolution") or []
        total = float(res[0]) * float(res[1]) if len(res) >= 2 else 0.0
        share, top = 0.0, None
        for k, v in (e.get("index_stats") or {}).items():
            try:
                idx, px = int(k), float((v or {}).get("pixels") or 0.0)
            except (TypeError, ValueError, AttributeError):
                continue
            if idx != 0 and total > 0 and px / total > share:
                share, top = px / total, idx
        element = names.get(top, f"index {top}") if top is not None else None
        if top is not None and cam in carried:
            element += " (an earlier build's index: the name may differ)"
        touch = near is not None and near <= max(start + LENS_TOUCH_M, RENDER_MIN_DEPTH_M) + 1e-12
        fills = share > single_max
        if not touch and not fills:
            continue
        parts = []
        if touch and near <= start + LENS_TOUCH_M:
            parts.append(f"the lens touches a surface (nearest depth {near:.3f} m, clip start {start:g} m)")
        elif touch:
            parts.append(f"a surface is {near:.3f} m from the lens (the render test needs more than "
                         f"{RENDER_MIN_DEPTH_M:g} m)")
        if fills:
            parts.append(f"{element} fills {share * 100:.1f} % of the frame (over {single_max * 100:.0f} %)")
        metrics = {"depth_min_m": None if near is None else round(near, 4), "clip_start_m": start,
                   "largest_share": round(share, 4), "largest_element": element,
                   "lens_mm": e.get("lens_mm") or plan.get("lens_mm")}
        severity = "critical" if touch else "major"
        message = f"{cam}: the view is blocked: " + " and ".join(parts)
        if CAM.BLOCKED_WARNING in str(plan.get("warning") or ""):
            metrics.update(blocked_unavoidable=True, severity_was=severity)
            severity = "minor"
            message += f"; the camera search found no free point ({CAM.BLOCKED_WARNING}): reported only"
        else:
            message += "; move the camera to a free point of the room with headroom (set_camera)"
        out.append({"check": CAMERA_BLOCKED_CHECK, "severity": severity, "target": cam,
                    "room_id": e.get("room_id") or plan.get("room_id"), "message": message, "metrics": metrics})
    return out


NEEDS_REVIEW_CHECK = "NR"
READING_CONFLICT_CHECK = "RC"


def reading_items(building: dict) -> list[dict]:
    """Milestone 12 (docs/milestone12.md §4.1, track R): one ``NR`` violation (major) per untyped drawn piece the reading
    left for review (``needs_review``; not built, never an unexplained box: the agent may type it from its plan crop
    or record it as not furniture) and one ``RC`` violation (minor) per ``type_disagreement`` conflict (the drawing
    overruled an AI type)."""
    out = []
    for item in building.get("needs_review") or []:
        crop = f" (plan crop {item['crop']})" if item.get("crop") else ""
        out.append({"check": NEEDS_REVIEW_CHECK, "severity": "major", "target": item.get("id"),
                    "room_id": item.get("room_id"),
                    "message": f"untyped drawn piece left for review: {item.get('reason') or item.get('kind')}{crop}",
                    "metrics": {"kind": item.get("kind")}})
    for c in building.get("conflicts") or []:
        if c.get("kind") != "type_disagreement":
            continue
        ids = list(c.get("element_ids") or [])
        out.append({"check": READING_CONFLICT_CHECK, "severity": "minor", "target": ids[0] if ids else None,
                    "room_id": None, "message": str(c.get("description") or "type disagreement")[:300],
                    "metrics": {"resolution": str(c.get("resolution") or "")[:200]}})
    return out


def model_items(built: Optional[dict], scene_manifest: Optional[dict]) -> list[dict]:
    """The review of the model as built (``model_review.review``) as code violations (26 Oct 2026)."""
    if not built:
        raise FileNotFoundError("no building as built (scene/building_built.json)")
    from wenart.blender import model_review as MR
    return list(MR.review(built, scene_manifest).get("findings") or [])


def run(building: dict, scene_manifest: Optional[dict] = None, render_manifest: Optional[dict] = None, *,
        plausibility_fn: Optional[Callable] = None, exterior_fn: Optional[Callable] = None,
        views_fn: Optional[Callable] = None, groups_fn: Optional[Callable] = None,
        levels_fn: Optional[Callable] = None, scene_dir=None, scene_fn: Optional[Callable] = None,
        built: Optional[dict] = None, model_fn: Optional[Callable] = None) -> dict:
    """``{"findings": [...], "checks": [{source, status, note, counts}], "scores": {room_id: score}, "mean"}``.
    ``scene_dir``: the build's checks folder (``outputs/<p>/build/checks``); without it (and without ``scene_fn``)
    the scene family is not run."""
    findings: list[dict] = []
    checks: list[dict] = []
    scores: dict = {}
    mean = None
    # fix round after P3: a decor piece's violation gets the decor's room too
    room_of = {f.get("id"): f.get("room_id") for f in (building.get("decor") or []) + (building.get("furniture") or [])
               if isinstance(f, dict)}

    def family(source: str, fn_name: Optional[str], fn: Optional[Callable], call: Callable[[Callable], list]) -> None:
        try:
            got = call(fn or (_default(fn_name) if fn_name else None))
        except NotImplementedError as exc:
            checks.append({"source": source, "status": "unavailable", "note": f"not built yet ({exc})"})
            return
        except FileNotFoundError as exc:
            checks.append({"source": source, "status": "unavailable", "note": str(exc)})
            return
        except Exception as exc:  # noqa: BLE001 - one broken family never stops the critic
            checks.append({"source": source, "status": "error", "note": f"{type(exc).__name__}: {exc}"})
            return
        new = [finding(dict(v, room_id=v.get("room_id") or room_of.get(v.get("target")))) for v in got]
        counts = {s: sum(1 for f in new if f["severity"] == s) for s in SEVERITIES}
        checks.append({"source": source, "status": "ok", "note": None, "counts": counts})
        findings.extend(new)

    def plaus(fn):
        nonlocal mean
        res = fn(building) or {}
        out = []
        for rid, r in (res.get("rooms") or {}).items():
            scores[rid] = r.get("score")
            for v in r.get("violations") or []:
                out.append(dict(v, room_id=v.get("room_id") or rid))
        mean = res.get("mean")
        return out

    def exterior(fn):
        return list((fn(building, scene_manifest, render_manifest) or {}).get("violations") or [])

    def views(fn):
        if render_manifest is None:
            return []
        out = []
        for vid, items in ((fn(building, render_manifest) or {}).get("views") or {}).items():
            out += [dict(v, target=v.get("target") or vid) for v in items or []]
        return out

    def groups(fn):
        # Track G: plausibility already reports G1-G13 (F5's place) and leaves G5's headboard part to F3; the group
        # family adds only what plausibility did not report (G14, rooms it skipped): one finding per fault.
        seen = {(f["check"], f["target"]) for f in findings}
        out = []
        for rid, items in ((fn(building) or {}).get("rooms") or {}).items():
            for v in items or []:
                target = None if v.get("target") is None else str(v.get("target"))
                if (str(v.get("check")), target) in seen:
                    continue
                if v.get("check") == "G5" and (v.get("metrics") or {}).get("part") == "headboard" \
                        and ("F3", target) in seen:
                    continue
                out.append(dict(v, room_id=v.get("room_id") or rid))
        return out

    def levels(fn):
        return list(fn(building, scene_manifest, render_manifest) or [])

    family("plausibility", "plausibility", plausibility_fn, plaus)
    family("exterior", "check_exterior", exterior_fn, exterior)
    family("views", "check_views", views_fn, views)
    family("groups", "groups", groups_fn, groups)
    family("levels", "levels", levels_fn, levels)
    scene_read: list = []

    def scene(fn):
        got = list(fn() or [])
        scene_read.extend(got)
        # fix round after P4a: a cut below 0.03 m is invisible and no agent's work: minor (module docstring)
        return [within_tolerance_minor(v) if isinstance(v, dict) else v for v in got]

    if scene_fn is not None or scene_dir is not None:
        family("scene", None, scene_fn or (lambda: scene_violations(scene_dir)), scene)
    if (scene_manifest or {}).get("furniture"):
        family("scene_manifest", None, lambda: manifest_violations(scene_manifest, scene_read), lambda fn: fn())
    family("library", None, lambda: library_gaps(building), lambda fn: fn())
    family("reading", None, lambda: reading_items(building), lambda fn: fn())
    # round 4: the views the EV cap held too dark (render manifest; unavailable without one)
    family("lighting", None, lambda: lighting_items(render_manifest, building), lambda fn: fn())
    # fix round after P5: the views whose lens touches a surface or that one element fills (render manifest)
    family("blocked", None, lambda: blocked_items(render_manifest, scene_manifest), lambda fn: fn())
    # 26 Oct 2026 (user: "reviewing the 3d model itself could be better"): the review of the model as built (doors
    # on their floors, working heights, guards, doors into the air, rain water, one opening language, rooms that make
    # sense: wenart/blender/model_review.py), on the building as built (``built``: scene/building_built.json)
    if model_fn is not None or built is not None:
        family("model", None, model_fn or (lambda: model_items(built, scene_manifest)), lambda fn: fn())
    return {"findings": _unique(findings), "checks": checks, "scores": scores, "mean": mean,
            "scene_summary": manifest_summary(scene_manifest)}


def measured(code: dict) -> set:
    """``{source}`` of the families that ran (a vision finding can only be contradicted by a family that ran)."""
    return {c["source"] for c in code.get("checks") or [] if c.get("status") == "ok"}


FAMILY_OF = {**{k: "plausibility" for k in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "R1", "R2", "R3",
                                             "R4")},
             **{k: "exterior" for k in ("X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8")},
             **{k: "views" for k in ("V1", "V3")},
             **{f"G{i}": "groups" for i in range(1, 15)},
             **{f"L{i}": "levels" for i in range(1, 8)},
             **{f"S{i}": "scene" for i in range(1, 7)},
             LIBRARY_GAP_CHECK: "library", NEEDS_REVIEW_CHECK: "reading", READING_CONFLICT_CHECK: "reading",
             LIGHTING_DARK_CHECK: "lighting", CAMERA_BLOCKED_CHECK: "blocked"}
