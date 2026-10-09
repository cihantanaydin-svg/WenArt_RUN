"""The clear-error checks of ``correct_geometry`` (docs/milestone11.md §3.2, §5; CLAUDE.md evidence rules).

What: ``check(building, args)`` says whether a geometry correction the agent proposes is one of the three clear
errors the rules allow, measured on the building JSON:

- ``close_gap``: two walls of one level whose nearest end points are at most ``GAP_MAX_M`` = 0.15 m apart (and not
  already touching, > 0.005 m);
- ``merge_duplicate_wall``: two walls of one level that are parallel (within 2 deg), whose centre lines lie within
  ``DUPLICATE_MAX_M`` = 0.02 m of each other and overlap along their length;
- ``fix_opening_on_wall``: an opening whose centre lies at most ``OPENING_OFF_MAX_M`` = 0.10 m off the centre line
  of the wall it names (and more than 0.005 m: else nothing to fix).

Why record-only: a corrected wall changes the room outlines the pipeline derives from the walls; applying it means
re-running ``pipeline_final`` and everything after it, which throws away the furniture rounds. In M11 an accepted
correction is stored in ``overrides.json`` and ``building["agent_overrides"]["geometry"]``, logged as
``corrected_by_ai`` and listed in the report as an open item for the next full run; the geometry is not changed.

How: pure Python (no shapely), metres; ``{"ok", "failed": [reasons], "metrics": {...}}``.
"""
from __future__ import annotations

import math

GAP_MAX_M = 0.15
DUPLICATE_MAX_M = 0.02
OPENING_OFF_MAX_M = 0.10
TOUCH_M = 0.005
PARALLEL_DEG = 2.0
KINDS = ("close_gap", "merge_duplicate_wall", "fix_opening_on_wall")


def _pt(p) -> tuple[float, float]:
    return float(p[0]), float(p[1])


def _dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def point_line_distance(p, a, b) -> float:
    """Distance of ``p`` from the infinite line through ``a`` and ``b``."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    if n < 1e-9:
        return _dist(p, a)
    return abs(dx * (p[1] - a[1]) - dy * (p[0] - a[0])) / n


def projection_t(p, a, b) -> float:
    """Where ``p`` falls along ``a`` -> ``b`` (0 at a, 1 at b)."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    n2 = dx * dx + dy * dy
    return 0.0 if n2 < 1e-12 else ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / n2


def _angle(a, b) -> float:
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180.0


def _walls(building: dict) -> dict:
    return {w.get("id"): w for w in building.get("walls") or [] if isinstance(w, dict)}


def check(building: dict, args: dict) -> dict:
    kind = args.get("kind")
    walls = _walls(building)
    failed: list[str] = []
    metrics: dict = {"kind": kind}
    if kind not in KINDS:
        return {"ok": False, "failed": [f"unknown kind {kind!r} (known: {', '.join(KINDS)})"], "metrics": metrics}
    if kind in ("close_gap", "merge_duplicate_wall"):
        ids = list(args.get("wall_ids") or [])
        if len(ids) != 2 or ids[0] == ids[1]:
            return {"ok": False, "failed": ["give exactly two different wall ids"], "metrics": metrics}
        missing = [i for i in ids if i not in walls]
        if missing:
            return {"ok": False, "failed": [f"unknown wall id {m}" for m in missing], "metrics": metrics}
        w1, w2 = walls[ids[0]], walls[ids[1]]
        if w1.get("level_id") != w2.get("level_id"):
            return {"ok": False, "failed": ["the walls are on different levels"], "metrics": metrics}
        a1, b1, a2, b2 = _pt(w1["start"]), _pt(w1["end"]), _pt(w2["start"]), _pt(w2["end"])
        if kind == "close_gap":
            gap = min(_dist(p, q) for p in (a1, b1) for q in (a2, b2))
            metrics["gap_m"] = round(gap, 4)
            if gap <= TOUCH_M:
                failed.append(f"the walls already touch (gap {gap:.3f} m)")
            elif gap > GAP_MAX_M:
                failed.append(f"gap {gap:.3f} m > {GAP_MAX_M} m: not a clear drawing error")
        else:
            diff = abs(_angle(a1, b1) - _angle(a2, b2))
            diff = min(diff, 180.0 - diff)
            off = max(point_line_distance(a2, a1, b1), point_line_distance(b2, a1, b1))
            t = sorted((projection_t(a2, a1, b1), projection_t(b2, a1, b1)))
            overlap = min(1.0, t[1]) - max(0.0, t[0])
            metrics.update(angle_diff_deg=round(diff, 3), offset_m=round(off, 4), overlap_share=round(overlap, 3))
            if diff > PARALLEL_DEG:
                failed.append(f"not parallel ({diff:.1f} deg)")
            if off > DUPLICATE_MAX_M:
                failed.append(f"centre lines {off:.3f} m apart > {DUPLICATE_MAX_M} m")
            if overlap <= 0.0:
                failed.append("the walls do not overlap along their length")
    else:
        oid, wid = args.get("opening_id"), (args.get("wall_ids") or [None])[0] or args.get("wall_id")
        opening = next((o for o in building.get("openings") or [] if o.get("id") == oid), None)
        if opening is None:
            return {"ok": False, "failed": [f"unknown opening id {oid}"], "metrics": metrics}
        wid = wid or opening.get("wall_id")
        wall = walls.get(wid)
        if wall is None:
            return {"ok": False, "failed": [f"unknown wall id {wid}"], "metrics": metrics}
        a, b, c = _pt(wall["start"]), _pt(wall["end"]), _pt(opening.get("center") or (0.0, 0.0))
        off = point_line_distance(c, a, b)
        t = projection_t(c, a, b)
        metrics.update(offset_m=round(off, 4), along=round(t, 3), wall_id=wid)
        if off <= TOUCH_M:
            failed.append(f"the opening already lies on the wall ({off:.3f} m)")
        elif off > OPENING_OFF_MAX_M:
            failed.append(f"the opening is {off:.3f} m off the wall > {OPENING_OFF_MAX_M} m: not a clear error")
        if not (0.0 <= t <= 1.0):
            failed.append("the opening's centre is beyond the wall's ends")
    if not str(args.get("evidence") or "").strip():
        failed.append("no evidence given")
    return {"ok": not failed, "failed": failed, "metrics": metrics}
