"""The code critic (docs/milestone11.md §4, §8 step 1): every checklist item that code can measure.

What: ``run(building, scene_manifest, render_manifest)`` calls

- ``wenart.furniture.plausibility.score_building`` (track B: F1–F9, R1–R4 per room),
- ``wenart.blender.exterior_checks.check_exterior`` (track C: X1–X8) and ``check_views`` (V1, V3),

and turns their violations (``{check, severity, target, room_id, message, metrics}``, contract §17.2) into
findings ``{id, source: "code", check, severity, target, room_id, message, evidence: {metrics}}``. It also
returns one record per check family (``status`` ok / unavailable / error) and the room scores.

Why: code is cheap (milliseconds), exact and the first judge; the vision critic only adds what an image shows
and is dropped where the code contradicts it (``critic_vision``).

How: a family whose function is not built yet (``NotImplementedError``, a stub of another track) or fails is
recorded as ``unavailable`` / ``error`` and the loop goes on with the rest; the functions are injectable (tests).
Finding ids are stable (``c:<check>:<target>``, a counter for repeats), so the same problem keeps its id from round
to round.
"""
from __future__ import annotations

from typing import Callable, Optional

from wenart.agent.prompts import CHECKLIST, SEVERITIES


def _default(name: str) -> Callable:
    if name == "plausibility":
        from wenart.furniture import plausibility
        return plausibility.score_building
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


def run(building: dict, scene_manifest: Optional[dict] = None, render_manifest: Optional[dict] = None, *,
        plausibility_fn: Optional[Callable] = None, exterior_fn: Optional[Callable] = None,
        views_fn: Optional[Callable] = None) -> dict:
    """``{"findings": [...], "checks": [{source, status, note, counts}], "scores": {room_id: score}, "mean"}``."""
    findings: list[dict] = []
    checks: list[dict] = []
    scores: dict = {}
    mean = None

    def family(source: str, fn_name: str, fn: Optional[Callable], call: Callable[[Callable], list]) -> None:
        try:
            got = call(fn or _default(fn_name))
        except NotImplementedError as exc:
            checks.append({"source": source, "status": "unavailable", "note": f"not built yet ({exc})"})
            return
        except Exception as exc:  # noqa: BLE001 - one broken family never stops the critic
            checks.append({"source": source, "status": "error", "note": f"{type(exc).__name__}: {exc}"})
            return
        new = [finding(v) for v in got]
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

    family("plausibility", "plausibility", plausibility_fn, plaus)
    family("exterior", "check_exterior", exterior_fn, exterior)
    family("views", "check_views", views_fn, views)
    return {"findings": _unique(findings), "checks": checks, "scores": scores, "mean": mean}


def measured(code: dict) -> set:
    """``{source}`` of the families that ran (a vision finding can only be contradicted by a family that ran)."""
    return {c["source"] for c in code.get("checks") or [] if c.get("status") == "ok"}


FAMILY_OF = {**{k: "plausibility" for k in ("F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "R1", "R2", "R3",
                                             "R4")},
             **{k: "exterior" for k in ("X1", "X2", "X3", "X4", "X5", "X6", "X7", "X8")},
             **{k: "views" for k in ("V1", "V3")}}
