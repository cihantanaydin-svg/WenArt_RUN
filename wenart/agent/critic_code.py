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
    """One ``LG`` violation (minor) per built piece whose fit found no audited model (``library_gap``, track S)."""
    out = []
    for f in building.get("furniture") or []:
        gap = f.get("library_gap")
        if not gap or f.get("build", True) is False:
            continue
        g = gap if isinstance(gap, dict) else {"note": str(gap)}
        what = ", ".join(f"{k} {v}" for k, v in sorted(g.items()) if not isinstance(v, (dict, list)))[:200]
        out.append({"check": LIBRARY_GAP_CHECK, "severity": "minor", "target": f.get("id"),
                    "room_id": f.get("room_id"), "message": f"library gap for {f.get('type')}: {what or 'no model'}",
                    "metrics": {k: v for k, v in g.items() if isinstance(v, (int, float, str))}})
    return out


def run(building: dict, scene_manifest: Optional[dict] = None, render_manifest: Optional[dict] = None, *,
        plausibility_fn: Optional[Callable] = None, exterior_fn: Optional[Callable] = None,
        views_fn: Optional[Callable] = None, groups_fn: Optional[Callable] = None,
        levels_fn: Optional[Callable] = None, scene_dir=None, scene_fn: Optional[Callable] = None) -> dict:
    """``{"findings": [...], "checks": [{source, status, note, counts}], "scores": {room_id: score}, "mean"}``.
    ``scene_dir``: the build's checks folder (``outputs/<p>/build/checks``); without it (and without ``scene_fn``)
    the scene family is not run."""
    findings: list[dict] = []
    checks: list[dict] = []
    scores: dict = {}
    mean = None
    room_of = {f.get("id"): f.get("room_id") for f in building.get("furniture") or []}

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
        return got

    if scene_fn is not None or scene_dir is not None:
        family("scene", None, scene_fn or (lambda: scene_violations(scene_dir)), scene)
    if (scene_manifest or {}).get("furniture"):
        family("scene_manifest", None, lambda: manifest_violations(scene_manifest, scene_read), lambda fn: fn())
    family("library", None, lambda: library_gaps(building), lambda fn: fn())
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
             LIBRARY_GAP_CHECK: "library"}
