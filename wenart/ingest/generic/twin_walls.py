"""One wall read twice (29 Oct 2026, user on real06 run 20261028-154514-full: "I am not understanding this scene is there a
door behind it?").

What: two walls of one level that lie in each other (parallel within ``ANGLE_DEG``, the centre line of one inside the
other's thickness, overlapping along at least ``OVERLAP_SHARE`` of the shorter) are one wall read twice (the wall
faces paired twice, e.g. real06's w_L0_009 and w_L0_010 between the kitchen and the living room, 2.5 cm apart). The
shorter one (else the thinner, else the higher id) is not built when it is a copy (at least ``MIN_COPY_M`` long and no
thicker than the kept wall: a short, thicker block in a wall is a column or a pier, kept): it goes to
``building["walls_merged"]`` with the
reason (``corrected_by_ai`` by code, CLAUDE.md: "a duplicated wall" is a clear error); its openings move onto the kept
wall, projected on its centre line, unless an opening of the kept wall already covers at least ``SAME_OPENING_SHARE``
of them (one opening read twice: it goes to ``building["openings_merged"]``); every other ``wall_id`` that names it
names the kept wall.

Why: real06's 2.9 m gap between the kitchen and the living room was read on both walls; the architect then made one
copy a serving hatch over the counter and the other a 1.95 m double door "of the room no door reached": a wooden double
door stood in the hatch, behind the counter.
"""
from __future__ import annotations

import copy
import math
from typing import Callable, Optional

ANGLE_DEG = 3.0
OVERLAP_SHARE = 0.8
SAME_OPENING_SHARE = 0.5
MIN_COPY_M = 1.0          # a shorter piece in a wall is a pier or a column (real06: 0.1-0.75 m KOLON blocks)
THICKER_TOL_M = 0.01
RULE = "reading.twin_walls"


def _axis(w: dict) -> Optional[tuple]:
    (x0, y0), (x1, y1) = [float(v) for v in w["start"][:2]], [float(v) for v in w["end"][:2]]
    length = math.hypot(x1 - x0, y1 - y0)
    if length <= 1e-6:
        return None
    return (x0, y0), ((x1 - x0) / length, (y1 - y0) / length), length


def _t(axis: tuple, p) -> float:
    (x0, y0), (ux, uy), _ = axis
    return (float(p[0]) - x0) * ux + (float(p[1]) - y0) * uy


def _off(axis: tuple, p) -> float:
    (x0, y0), (ux, uy), _ = axis
    return abs(-(float(p[0]) - x0) * uy + (float(p[1]) - y0) * ux)


def twin_of(a: dict, b: dict) -> bool:
    """Whether walls ``a`` and ``b`` are one wall read twice (pure; module docstring)."""
    if a.get("level_id") != b.get("level_id"):
        return False
    ax, bx = _axis(a), _axis(b)
    if ax is None or bx is None:
        return False
    if abs(ax[1][0] * bx[1][1] - ax[1][1] * bx[1][0]) > math.sin(math.radians(ANGLE_DEG)):
        return False
    half = max(float(a.get("thickness") or 0.0), float(b.get("thickness") or 0.0)) / 2.0
    mid = [(float(b["start"][i]) + float(b["end"][i])) / 2.0 for i in (0, 1)]
    if _off(ax, mid) > half + 1e-6:
        return False
    t0, t1 = sorted((_t(ax, b["start"]), _t(ax, b["end"])))
    overlap = min(ax[2], t1) - max(0.0, t0)
    return overlap >= OVERLAP_SHARE * min(ax[2], bx[2]) - 1e-6


def _rank(w: dict) -> tuple:
    ax = _axis(w)
    return (ax[2] if ax else 0.0, float(w.get("thickness") or 0.0), "".join(chr(255 - ord(c)) for c in str(w["id"])))


def _rename(node, old: str, new: str) -> None:
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "wall_id" and v == old:
                node[k] = new
            else:
                _rename(v, old, new)
    elif isinstance(node, list):
        for v in node:
            _rename(v, old, new)


def merge_twin_walls(b: dict, warn: Callable[[str], None] = lambda _m: None) -> list[str]:
    """Drop every wall read twice (mutates ``b``; module docstring). Returns the dropped wall ids."""
    walls = [w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id")]
    dropped: dict[str, str] = {}
    for i, a in enumerate(walls):
        for c in walls[i + 1:]:
            if a["id"] in dropped or c["id"] in dropped or not twin_of(a, c):
                continue
            keep, dup = (a, c) if _rank(a) >= _rank(c) else (c, a)
            if _axis(dup)[2] < MIN_COPY_M or \
                    float(dup.get("thickness") or 0.0) > float(keep.get("thickness") or 0.0) + THICKER_TOL_M:
                continue                       # a column or a pier in the wall, not a copy of it
            dropped[dup["id"]] = keep["id"]
    if not dropped:
        return []
    by_id = {w["id"]: w for w in walls}
    ops = [o for o in b.get("openings") or [] if isinstance(o, dict)]
    for dup_id, keep_id in dropped.items():
        while keep_id in dropped:                      # a chain of copies ends at the kept one
            keep_id = dropped[keep_id]
        dup, keep = by_id[dup_id], by_id[keep_id]
        ax = _axis(keep)
        reason = (f"{dup_id} lies in {keep_id} ({_off(ax, [(float(dup['start'][i]) + float(dup['end'][i])) / 2.0 for i in (0, 1)]):.3f} m "
                  f"apart, parallel, overlapping): one wall read twice; {dup_id} is not built")
        moved, merged = [], []
        for o in [o for o in ops if o.get("wall_id") == dup_id]:
            t = _t(ax, o["center"])
            half = float(o.get("width") or 0.0) / 2.0
            same = None
            for p in ops:
                if p is o or p.get("wall_id") != keep_id:
                    continue
                tp, hp = _t(ax, p["center"]), float(p.get("width") or 0.0) / 2.0
                cover = min(t + half, tp + hp) - max(t - half, tp - hp)
                if cover >= SAME_OPENING_SHARE * max(min(2 * half, 2 * hp), 1e-6):
                    same = p
                    break
            if same is not None:
                b["openings"] = [x for x in b["openings"] if x is not o]
                ops = [x for x in ops if x is not o]
                b.setdefault("openings_merged", []).append(dict(copy.deepcopy(o), merged_into=same["id"], corrected_by_ai={
                    "by": "code", "rule": RULE, "reason": f"{o['id']} on {dup_id} is {same['id']} of {keep_id} read "
                                                           f"twice ({reason})"}))
                merged.append(f"{o['id']} -> {same['id']}")
                continue
            (x0, y0), (ux, uy), _ = ax
            o.setdefault("drawn_center", list(o["center"]))
            o["center"] = [round(x0 + ux * t, 4), round(y0 + uy * t, 4)]
            o["wall_id"] = keep_id
            o["corrected_by_ai"] = {"by": "code", "rule": RULE, "reason": f"moved onto {keep_id}: {reason}",
                                    "changed": {"wall_id": dup_id}}
            moved.append(o["id"])
        b["walls"] = [w for w in b["walls"] if w.get("id") != dup_id]
        _rename(b, dup_id, keep_id)
        b.setdefault("walls_merged", []).append(dict(copy.deepcopy(dup), merged_into=keep_id, corrected_by_ai={
            "by": "code", "rule": RULE, "reason": reason, "evidence": list(dup.get("evidence") or [])
            + list(keep.get("evidence") or [])}))
        warn(f"{dup_id}: {reason}" + (f"; openings moved onto {keep_id}: {', '.join(moved)}" if moved else "")
             + (f"; openings read twice, merged: {', '.join(merged)}" if merged else ""))
    return sorted(dropped)
