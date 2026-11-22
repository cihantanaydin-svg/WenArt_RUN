"""A facade drawn as two leaves is one wall (22 Nov 2026, the user's "build S2 and double-wall rule"; C0086 on real10 L0:
"it is a sliding window").

What: two parallel walls of one level (within ``ANGLE_DEG``) whose bands stand apart by a cavity of at most
``CAVITY_MAX_M`` (touching bands included, ``CAVITY_MIN_M``), each a leaf (at most ``LEAF_MAX_T_M`` thick), running
along each other (overlapping ``OVERLAP_SHARE`` of the longer one, at least ``MIN_LEAF_M``), with a room beyond one of
them and none beyond the other nor in the cavity (``SIDE_PROBE_M`` past each far face, at ``SIDE_SAMPLES`` along the
overlap, most samples agreeing) and at least one of them an exterior wall, are one facade wall of their total thickness
(``merge_double_leaves``): the longer one is kept on the band from the outer face of one leaf to the outer face of the
other, the other goes to ``building["walls_merged"]`` with the reason (``corrected_by_ai`` by code, rule ``RULE``) and
every ``wall_id`` naming it names the kept wall. A gap in one leaf facing a gap in the other (their openings overlapping
``SAME_OPENING_SHARE`` of the narrower along the wall) is one opening through the whole wall: the better typed one is
kept (``_rank``: a door from its drawn swing, a door, a window, read from the drawing before inferred, an untyped gap
last), at the drawn gap's place when it was placed by a size tag only, the other goes to ``building["openings_merged"]``;
an opening in one leaf only keeps what the reader decided. Every opening of the merged wall stands on its new centre
line (``drawn_center`` keeps the old place).

``facing_gaps``: an empty gap (an untyped opening, nothing drawn in it) in a band standing parallel outside a facade wall
(within ``FACING_MAX_M`` of its outer face, a room beyond the facade, none beyond the band) facing a door or window of
the facade is that opening read again (a window surround, a cladding's or a reveal's cut): it is merged into the facade
opening and the band stops at the opening's jambs (real10: the 0.30 m fins beside every window, read as a 0.10 m or
0.30 m "wall" with an empty 1.4 m gap 0.24 m outside the sashes, where the user's C0086 stands).

Why: real10's facades are a 17 cm inner leaf, a 3 cm cavity, a 20 cm outer leaf and 4 cm of render (the Turkish
double wall, TS 825: 19 + 3-5 cm insulation or air + 8.5-19 cm, so a drawn cavity stays under 10 cm; an insulation
or a ventilated cladding skin stands 5-12 cm off the masonry); the reader built each leaf as a wall of its own with a
window in each (one from the size tag, one from the gap with the sashes) and an empty gap in the fins outside: three
openings for one window. Party walls, an expansion joint (rooms on both sides), a shaft or a duct (a wider gap, or a
room in it) and a parapet (metres off the facade) are not leaves and stay walls of their own.
"""
from __future__ import annotations

import copy
import math
from typing import Callable, Optional

from shapely.geometry import Point, Polygon

ANGLE_DEG = 3.0
CAVITY_MAX_M = 0.10
CAVITY_MIN_M = -0.01
LEAF_MAX_T_M = 0.25
OVERLAP_SHARE = 0.8
MIN_LEAF_M = 0.8
SIDE_PROBE_M = 0.25
SIDE_SAMPLES = (0.25, 0.5, 0.75)
SAME_OPENING_SHARE = 0.5
FACING_MAX_M = 0.30
JAMB_MIN_M = 0.05            # a band's rest beside a facing gap shorter than this is no piece
RULE = "reading.double_leaf"


def _axis(w: dict) -> Optional[tuple]:
    (x0, y0), (x1, y1) = [float(v) for v in w["start"][:2]], [float(v) for v in w["end"][:2]]
    length = math.hypot(x1 - x0, y1 - y0)
    if length <= 1e-6:
        return None
    return (x0, y0), ((x1 - x0) / length, (y1 - y0) / length), length


def _t(ax: tuple, p) -> float:
    (x0, y0), (ux, uy), _ = ax
    return (float(p[0]) - x0) * ux + (float(p[1]) - y0) * uy


def _o(ax: tuple, p) -> float:
    """Signed offset of ``p`` from the axis (positive on its left)."""
    (x0, y0), (ux, uy), _ = ax
    return -(float(p[0]) - x0) * uy + (float(p[1]) - y0) * ux


def _at(ax: tuple, t: float, o: float) -> tuple:
    (x0, y0), (ux, uy), _ = ax
    return (x0 + ux * t - uy * o, y0 + uy * t + ux * o)


def _parallel(ax: tuple, cx: tuple) -> bool:
    return abs(ax[1][0] * cx[1][1] - ax[1][1] * cx[1][0]) <= math.sin(math.radians(ANGLE_DEG))


def _rooms(b: dict) -> dict:
    out: dict = {}
    for r in b.get("rooms") or []:
        if len(r.get("polygon") or []) >= 3:
            try:
                out.setdefault(r.get("level_id"), []).append(Polygon(r["polygon"]).buffer(0))
            except (ValueError, TypeError):
                continue
    return out


def _in_room(rooms: list, pt: tuple) -> bool:
    q = Point(pt)
    return any(r.contains(q) for r in rooms)


def _band(ax: tuple, w: dict) -> tuple[float, float, float, float]:
    """``(o_lo, o_hi, t_lo, t_hi)`` of wall ``w`` in the frame of axis ``ax``."""
    o = (_o(ax, w["start"]) + _o(ax, w["end"])) / 2.0
    h = float(w.get("thickness") or 0.0) / 2.0
    t0, t1 = sorted((_t(ax, w["start"]), _t(ax, w["end"])))
    return o - h, o + h, t0, t1


def _facade_side(ax: tuple, inner: tuple, outer: tuple, lo: float, hi: float, rooms: list) -> Optional[int]:
    """+1 when a room lies beyond the band ``inner`` = (o_lo, o_hi) on its far side from ``outer`` and none beyond
    ``outer`` (nor between them), -1 the other way round, None otherwise: the majority of ``SIDE_SAMPLES`` along
    ``lo``-``hi`` decides (pure)."""
    sgn = 1.0 if (outer[0] + outer[1]) > (inner[0] + inner[1]) else -1.0
    gap_mid = ((inner[1] if sgn > 0 else inner[0]) + (outer[0] if sgn > 0 else outer[1])) / 2.0
    votes = {1: 0, -1: 0}
    for f in SIDE_SAMPLES:
        t = lo + f * (hi - lo)
        beyond_in = (inner[0] - SIDE_PROBE_M) if sgn > 0 else (inner[1] + SIDE_PROBE_M)
        beyond_out = (outer[1] + SIDE_PROBE_M) if sgn > 0 else (outer[0] - SIDE_PROBE_M)
        a, c = _in_room(rooms, _at(ax, t, beyond_in)), _in_room(rooms, _at(ax, t, beyond_out))
        if _in_room(rooms, _at(ax, t, gap_mid)):
            return None                                   # a room in the gap: a shaft, a duct, a corridor
        if a and not c:
            votes[1] += 1
        elif c and not a:
            votes[-1] += 1
    need = len(SIDE_SAMPLES) // 2 + 1
    return 1 if votes[1] >= need else (-1 if votes[-1] >= need else None)


def leaf_pair(a: dict, c: dict, rooms: list) -> Optional[dict]:
    """Whether walls ``a`` and ``c`` are the two leaves of one facade wall (pure; module docstring): ``{"cavity",
    "inner", "outer"}`` (the ids of the leaf on the room side and the other one) or None."""
    if a.get("level_id") != c.get("level_id") or a.get("id") == c.get("id"):
        return None
    ax, cx = _axis(a), _axis(c)
    if ax is None or cx is None or not _parallel(ax, cx):
        return None
    ta, tc = float(a.get("thickness") or 0.0), float(c.get("thickness") or 0.0)
    if not (0.0 < ta <= LEAF_MAX_T_M + 1e-9 and 0.0 < tc <= LEAF_MAX_T_M + 1e-9):
        return None
    if not (a.get("exterior") or c.get("exterior")):
        return None
    alo, ahi = -ta / 2.0, ta / 2.0
    clo, chi, c0, c1 = _band(ax, c)
    cavity = max(clo - ahi, alo - chi)
    if not CAVITY_MIN_M - 1e-9 <= cavity <= CAVITY_MAX_M + 1e-9:
        return None
    lo, hi = max(0.0, c0), min(ax[2], c1)
    if hi - lo < MIN_LEAF_M - 1e-9 or hi - lo < OVERLAP_SHARE * max(ax[2], cx[2]) - 1e-6:
        return None
    side = _facade_side(ax, (alo, ahi), (clo, chi), lo, hi, rooms)
    if side is None:
        return None
    inner, outer = (a, c) if side > 0 else (c, a)
    return {"cavity": round(cavity, 4), "inner": inner["id"], "outer": outer["id"]}


def _ev(o: dict) -> list:
    ev = o.get("evidence") or []
    return [e for e in (ev if isinstance(ev, list) else [ev]) if isinstance(e, dict)]


def _from_gap(o: dict) -> bool:
    """The opening was read from a drawn gap (its evidence names the gap's strokes)."""
    return any(str(e.get("entity") or "").startswith("gap:") for e in _ev(o))


def _rank(o: dict) -> tuple:
    from wenart.ingest.generic import twin_walls as TW

    kind = o.get("type")
    base = {"door": 3, "window": 2}.get(kind, 0)
    if kind == "door" and TW._drawn(o):
        base = 4
    drawn = any(e.get("method") in ("vector", "raster") for e in _ev(o))
    return (base, drawn, _from_gap(o), float(o.get("width") or 0.0), str(o.get("id")))


def _empty(o: dict) -> bool:
    """An untyped gap with nothing drawn in it (no operation, no subtype, not virtual, not an open passage)."""
    return o.get("type") == "opening" and not o.get("virtual") and not o.get("operation") and not o.get("subtype") \
        and not o.get("open_passage") and o.get("drawn_type") in (None, "opening")


def _span(ax: tuple, o: dict) -> tuple[float, float]:
    t, h = _t(ax, o["center"]), float(o.get("width") or 0.0) / 2.0
    return t - h, t + h


def _overlap(s: tuple, q: tuple) -> float:
    return min(s[1], q[1]) - max(s[0], q[0])


def _faces(s: tuple, q: tuple) -> bool:
    return _overlap(s, q) >= SAME_OPENING_SHARE * max(min(s[1] - s[0], q[1] - q[0]), 1e-6) - 1e-9


def _merge_opening(b: dict, keep: dict, gone: dict, ax: tuple, reason: str) -> None:
    """``gone`` is ``keep`` read again (mutates ``b``): it goes to ``openings_merged``; ``keep`` takes the drawn gap's
    place when it was placed by a tag only."""
    if not _from_gap(keep) and _from_gap(gone):
        t = _t(ax, gone["center"])
        keep.setdefault("drawn_center", list(keep["center"]))
        keep["center"] = [round(v, 4) for v in _at(ax, t, _o(ax, keep["center"]))]
    b["openings"] = [x for x in b["openings"] if x is not gone]
    b.setdefault("openings_merged", []).append(dict(copy.deepcopy(gone), merged_into=keep["id"], corrected_by_ai={
        "by": "code", "rule": RULE, "reason": reason}))


def _on_axis(o: dict, ax: tuple, wall_id: str, note: str) -> None:
    t = _t(ax, o["center"])
    new = [round(v, 4) for v in _at(ax, t, 0.0)]
    if math.dist(new, [float(v) for v in o["center"][:2]]) > 1e-3:
        o.setdefault("drawn_center", list(o["center"]))
    o["center"] = new
    o["wall_id"] = wall_id
    o.setdefault("double_leaf", note)


def merge_double_leaves(b: dict, warn: Callable[[str], None] = lambda _m: None) -> list[dict]:
    """Merge every facade drawn as two leaves into one wall (mutates ``b``; module docstring). Returns a record per
    merge: ``{level_id, kind: "leaves", walls: [kept, merged], openings: [merged ...], text, place}``."""
    from wenart.ingest.generic import twin_walls as TW

    rooms = _rooms(b)
    notes = []
    levels = sorted({str(w.get("level_id")) for w in b.get("walls") or [] if isinstance(w, dict)})
    pending = list(levels)
    while pending:
        lid = pending[0]
        walls = [w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id") and str(w.get("level_id")) == lid
                 and 0.0 < float(w.get("thickness") or 0.0) <= LEAF_MAX_T_M + 1e-9 and _axis(w)]
        best = None
        for i, a in enumerate(walls):
            for c in walls[i + 1:]:
                info = leaf_pair(a, c, rooms.get(a.get("level_id"), []))
                if info is not None and (best is None or info["cavity"] < best[2]["cavity"]):
                    best = (a, c, info)
        if best is None:
            pending.pop(0)
            continue
        a, c, info = best
        keep, gone = (a, c) if (_axis(a)[2], str(c["id"])) >= (_axis(c)[2], str(a["id"])) else (c, a)
        kx = _axis(keep)
        klo, khi = -float(keep["thickness"]) / 2.0, float(keep["thickness"]) / 2.0
        glo, ghi, g0, g1 = _band(kx, gone)
        lo, hi = min(klo, glo), max(khi, ghi)
        m = (lo + hi) / 2.0
        t0, t1 = min(0.0, g0), max(kx[2], g1)
        before = {"start": list(keep["start"]), "end": list(keep["end"]), "thickness": keep["thickness"]}
        ta, tc = float(a["thickness"]), float(c["thickness"])
        keep["start"] = [round(v, 4) for v in _at(kx, t0, m)]
        keep["end"] = [round(v, 4) for v in _at(kx, t1, m)]
        keep["thickness"] = round(hi - lo, 4)
        keep["exterior"] = bool(keep.get("exterior") or gone.get("exterior"))
        reason = (f"{info['inner']} and {info['outer']} are the two leaves of one facade wall ({ta:.2f} "
                  f"and {tc:.2f} m, a {info['cavity']:.2f} m cavity, a room beyond one of them only): "
                  f"one wall {keep['thickness']:.2f} m thick; {gone['id']} is not built")
        keep["leaves"] = list(keep.get("leaves") or []) + [
            {"id": w["id"], "thickness": float(w["thickness"]), "offset_m": round(o - m, 4)}
            for w, o in ((dict(before, id=keep["id"]), 0.0), (gone, (glo + ghi) / 2.0))]
        keep.setdefault("corrected_by_ai", {"by": "code", "rule": RULE, "reason": reason, "changed": before})
        keep["evidence"] = list(keep.get("evidence") or []) + list(gone.get("evidence") or [])
        nx = _axis(keep)
        ops = [o for o in b.get("openings") or [] if isinstance(o, dict) and o.get("center")]
        ok = [o for o in ops if o.get("wall_id") == keep["id"]]
        og = [o for o in ops if o.get("wall_id") == gone["id"]]
        merged, merged_ids = [], []
        pairs = sorted(((_overlap(_span(nx, p), _span(nx, q)), p, q) for p in ok for q in og
                        if _faces(_span(nx, p), _span(nx, q))), key=lambda x: -x[0])
        used: set = set()
        for _ov, p, q in pairs:
            if id(p) in used or id(q) in used:
                continue
            used.update((id(p), id(q)))
            win, los = (p, q) if _rank(p) >= _rank(q) else (q, p)
            _merge_opening(b, win, los, nx, f"{los['id']} and {win['id']} face each other in the two leaves of one "
                                            f"facade wall: one opening through the whole wall ({reason})")
            merged.append(f"{los['id']} -> {win['id']}")
            merged_ids += [los["id"], win["id"]]
        for o in ok + og:
            if any(x is o for x in b["openings"]):
                _on_axis(o, nx, keep["id"], f"on the one wall of the leaves {info['inner']} and {info['outer']}")
        b["walls"] = [w for w in b["walls"] if w is not gone]
        TW._rename(b, gone["id"], keep["id"])
        b.setdefault("walls_merged", []).append(dict(copy.deepcopy(gone), merged_into=keep["id"], corrected_by_ai={
            "by": "code", "rule": RULE, "reason": reason, "evidence": list(gone.get("evidence") or [])}))
        line = f"{keep.get('level_id')}: {reason}" + (f"; openings read twice, merged: {', '.join(merged)}" if merged
                                                      else "")
        notes.append({"level_id": keep.get("level_id"), "kind": "leaves", "walls": [keep["id"], gone["id"]],
                      "openings": merged_ids, "text": line,
                      "place": [round(v, 3) for v in _at(nx, nx[2] / 2.0, 0.0)]})
        warn(f"double leaf: {line}")
    return notes


def facing_gaps(b: dict, warn: Callable[[str], None] = lambda _m: None) -> list[dict]:
    """Merge every empty gap of a band outside a facade into the facade opening it faces, the band stopping at the
    opening's jambs (mutates ``b``; module docstring). Returns a record per merge: ``{level_id, kind: "facing", walls:
    [band, facade], openings: [gap, facade opening], text, place}``."""
    rooms = _rooms(b)
    notes = []
    walls = [w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id") and _axis(w)]
    by_id = {w["id"]: w for w in walls}
    for o2 in [o for o in b.get("openings") or [] if isinstance(o, dict) and o.get("center") and _empty(o)]:
        band = by_id.get(o2.get("wall_id"))
        if band is None:
            continue
        bx = _axis(band)
        lv = rooms.get(band.get("level_id"), [])
        s2 = _span(bx, o2)
        best = None
        for w in walls:
            if w is band or w.get("level_id") != band.get("level_id") or not w.get("exterior"):
                continue
            wx = _axis(w)
            if not _parallel(bx, wx):
                continue
            wlo, whi, w0, w1 = _band(bx, w)
            blo, bhi = -float(band.get("thickness") or 0.0) / 2.0, float(band.get("thickness") or 0.0) / 2.0
            gap = max(blo - whi, wlo - bhi)
            if not 0.0 <= gap <= FACING_MAX_M + 1e-9:
                continue
            if _facade_side(bx, (wlo, whi), (blo, bhi), max(s2[0], w0), min(s2[1], w1), lv) != 1:
                continue                                  # the band must stand outside the facade
            for o1 in b["openings"]:
                if o1 is o2 or o1.get("wall_id") != w["id"] or o1.get("type") not in ("door", "window"):
                    continue
                s1 = _span(bx, o1)
                if _faces(s1, s2) and (best is None or _overlap(s1, s2) > best[2]):
                    best = (w, o1, _overlap(s1, s2))
        if best is None:
            continue
        w, o1, _ov = best
        reason = (f"{o2['id']}, an empty gap in {band['id']} ({float(band.get('thickness') or 0):.2f} m) standing "
                  f"outside the facade wall {w['id']}, faces its {o1['type']} {o1['id']}: the same opening read again "
                  f"(a surround, a reveal or a cladding cut); {band['id']} stops at its jambs")
        b["openings"] = [x for x in b["openings"] if x is not o2]
        b.setdefault("openings_merged", []).append(dict(copy.deepcopy(o2), merged_into=o1["id"], corrected_by_ai={
            "by": "code", "rule": RULE, "reason": reason}))
        # the band stops at the gap's jambs: its part beyond the far jamb becomes a wall piece of its own
        t0, t1 = 0.0, bx[2]
        g0, g1 = max(s2[0], t0), min(s2[1], t1)
        rest = [(t0, g0), (g1, t1)]
        keep = [(x0, x1) for x0, x1 in rest if x1 - x0 >= JAMB_MIN_M]
        if keep:
            first = keep[0]
            band_orig = copy.deepcopy(band)
            band["start"] = [round(v, 4) for v in _at(bx, first[0], 0.0)]
            band["end"] = [round(v, 4) for v in _at(bx, first[1], 0.0)]
            band.setdefault("corrected_by_ai", {"by": "code", "rule": RULE, "reason": reason,
                                                "changed": {"start": band_orig["start"], "end": band_orig["end"]}})
            for k, (x0, x1) in enumerate(keep[1:], start=1):
                piece = dict(copy.deepcopy(band_orig), id=f"{band['id']}_j{k}",
                             start=[round(v, 4) for v in _at(bx, x0, 0.0)], end=[round(v, 4) for v in _at(bx, x1, 0.0)],
                             corrected_by_ai={"by": "code", "rule": RULE, "reason": reason})
                b["walls"].append(piece)
                for o in b["openings"]:
                    if o.get("wall_id") == band["id"] and x0 - 1e-6 <= _t(bx, o["center"]) <= x1 + 1e-6:
                        o["wall_id"] = piece["id"]
        else:
            b["walls"] = [x for x in b["walls"] if x is not band]
            b.setdefault("walls_merged", []).append(dict(copy.deepcopy(band), merged_into=w["id"], corrected_by_ai={
                "by": "code", "rule": RULE, "reason": reason}))
        line = f"{band.get('level_id')}: {reason}"
        notes.append({"level_id": band.get("level_id"), "kind": "facing", "walls": [band["id"], w["id"]],
                      "openings": [o2["id"], o1["id"]], "text": line, "place": list(o2["center"][:2])})
        warn(f"facing gap: {line}")
        walls = [x for x in b.get("walls") or [] if isinstance(x, dict) and x.get("id") and _axis(x)]
        by_id = {x["id"]: x for x in walls}
    return notes
