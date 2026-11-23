"""Wall pieces: a block of wall material is part of the wall that runs into it, and one wall on one line is one wall
(22 Nov 2026, the user's "start on the wall split and invented walls"; lesson UL366).

What (each level, on the building's walls, after the twin and double-leaf merges; every source alike):

- ``fold_blocks``: a **block** is a wall piece no longer than ``BLOCK_RATIO`` times its thickness (or shorter than
  ``BLOCK_MIN_M``): no wall run but a junction filler, a step where a wall changes its thickness or line, a jamb nub, a
  sliver along a thicker wall, a column inside a wall. The wall material it stands for is kept and given to the walls
  that run into it: a block lying inside other walls at least as high goes; else the one or two walls whose end touches
  it (``TOUCH_M``) are extended along their own line to its far side when the extensions cover it, add no material
  outside it and the other walls, cross no opening's gap, and the wall extended is a wall run (or longer than the
  block), as high as the block, and drawn when the block is drawn. "Cover" and "add no material": ``COVER_SHARE`` of
  the block's area, nothing wider than ``SLIVER_M`` (or half the block's thickness) left over, at most the rest of its
  area added (or ``SLIVER_M`` squared). A wall on the block's own line and of its thickness is preferred (the wall
  then runs on through the junction). A wall run (no block) goes only when it lies inside crossing walls or a wall of
  its own thickness (the same wall read twice). A piece inside a thicker wall on its own centre line is left alone in
  both cases (RC14 ``wall_in_wall``: a thin wall read in a thick band, or a thick band read over a thin wall; the
  drawing must say which). A block that holds an opening stays. The piece goes to ``building["walls_merged"]`` with
  the reason (``corrected_by_ai`` by code, rule ``RULE_FOLD``), the extended walls keep ``folded_blocks`` (the block's
  id, size and how far each was extended), every ``wall_id`` naming it names the wall that took its place.
- ``merge_collinear``: two walls on one line (offset ``LINE_M``, thickness within ``THICKNESS_M``, parallel within
  ``ANGLE_DEG``) whose spans touch or overlap (``JOIN_GAP_M``), as high, of one status and one side (exterior or not),
  are one wall: the drawn one (else the longer) keeps its id, line and thickness and runs over both spans (rule
  ``RULE_MERGE``). An inferred wall that only bridges a wide gap holding drawn openings (``drawn_bridge``: rule
  wide_gap, every opening on it a door or window read from the drawing, filling half of it) counts as drawn: the
  drawing shows that wall through its windows as a run gap does.

Must not fire (each a test): a pilaster or a column standing out of a wall face (the extension along the wall does not
cover it), a wall end turning at a jamb (the return stands across the wall), a pier between two openings (an extension
would cross a gap), a free-standing column or pier (no wall runs into it), a jog thinner than a sliver, a block that
holds an opening, a wall broken by a shaft (no material in the gap), a parapet beside a full-height wall (other
heights), a drawn wall beside an inferred one (other status), a bridge over an undrawn gap (an unverified opening), a
thin wall inside a thicker one on its line.

Why: the bench (107 Swiss Dwellings buildings in a Turkish drafting style, ``wenart/datasets/bench.py``) counted 1715
'wall split' and 1449 'wall invented' cases at C0089; about two thirds of them were pieces no longer than 1.5 times
their thickness (junction squares, steps, slivers, nubs, columns: the mask decomposition and the face-pair walls leave
such pieces where walls meet), and many of the rest long pieces of one wall kept apart (a wide gap's bridge beside the
drawn wall). The dataset's own truth lists no piece shorter than 1.5 times its thickness ("a reader may fairly fold them
into their neighbours", ``swiss_dwellings.is_listed_wall``) and runs one wall on through its junctions; a model built
from blocks is the same solid, but its walls end at every junction and the checks see walls that are not walls.
"""
from __future__ import annotations

import copy
import math
from typing import Callable, Optional

from shapely.geometry import Polygon
from shapely.ops import unary_union

BLOCK_RATIO = 1.5            # a piece no longer than 1.5 x its thickness is a block, not a wall run ...
BLOCK_MIN_M = 0.30           # ... and so is any piece shorter than this
TOUCH_M = 0.03               # a wall's end face this close to a block runs into it
SLIVER_M = 0.04              # material left over or added this thin (or thinner) does not count ...
COVER_SHARE = 0.75           # ... when the walls cover at least this share of the block (and add at most the rest)
GAP_CLEAR_M = 0.01           # an extension may touch an opening's jamb by this much
HEIGHT_M = 0.05
ANGLE_DEG = 1.0
LINE_M = 0.015
THICKNESS_M = 0.015
JOIN_GAP_M = 0.02
RULE_FOLD = "reading.wall_block"
RULE_MERGE = "reading.wall_line"


def _axis(w: dict) -> Optional[tuple]:
    try:
        (x0, y0), (x1, y1) = [float(v) for v in w["start"][:2]], [float(v) for v in w["end"][:2]]
    except (KeyError, TypeError, ValueError):
        return None
    length = math.hypot(x1 - x0, y1 - y0)
    if length <= 1e-6 or not float(w.get("thickness") or 0.0) > 0.0:
        return None
    return (x0, y0), ((x1 - x0) / length, (y1 - y0) / length), length


def _band(o: tuple, u: tuple, s0: float, s1: float, t: float) -> Polygon:
    nx, ny = -u[1] * t / 2.0, u[0] * t / 2.0
    a = (o[0] + u[0] * s0, o[1] + u[1] * s0)
    b = (o[0] + u[0] * s1, o[1] + u[1] * s1)
    return Polygon([(a[0] + nx, a[1] + ny), (b[0] + nx, b[1] + ny), (b[0] - nx, b[1] - ny), (a[0] - nx, a[1] - ny)])


def rect(w: dict) -> Optional[Polygon]:
    ax = _axis(w)
    return None if ax is None else _band(ax[0], ax[1], 0.0, ax[2], float(w["thickness"]))


def is_block(w: dict) -> bool:
    """A piece no longer than ``BLOCK_RATIO`` x its thickness, or shorter than ``BLOCK_MIN_M`` (pure)."""
    ax = _axis(w)
    return ax is not None and ax[2] <= max(BLOCK_MIN_M, BLOCK_RATIO * float(w["thickness"])) + 1e-9


def thin(geom, width: float = SLIVER_M) -> bool:
    """Nothing of ``geom`` is wider than ``width`` (an empty geometry is thin; pure)."""
    if geom is None or geom.is_empty or geom.area <= 1e-9:
        return True
    return geom.buffer(-width / 2.0, join_style=2).is_empty


def _proj(ax: tuple, poly: Polygon) -> tuple[float, float, float, float]:
    """``(s_min, s_max, d_min, d_max)``: the polygon's extent along and across the axis."""
    (ox, oy), (ux, uy), _l = ax
    s = [(x - ox) * ux + (y - oy) * uy for x, y in poly.exterior.coords]
    d = [-(x - ox) * uy + (y - oy) * ux for x, y in poly.exterior.coords]
    return min(s), max(s), min(d), max(d)


def _gaps(b: dict, lid: str, walls: dict) -> list[Polygon]:
    """The gap of every opening of the level: its width along its wall, the wall's thickness across (less the
    ``GAP_CLEAR_M`` an extension may touch at each jamb)."""
    out = []
    for o in b.get("openings") or []:
        if not isinstance(o, dict) or str(o.get("level_id")) != lid or not o.get("center"):
            continue
        w = walls.get(o.get("wall_id"))
        ax = _axis(w) if w else None
        width = float(o.get("width") or 0.0)
        if ax is None or width <= 2 * GAP_CLEAR_M:
            continue
        (ox, oy), (ux, uy), _l = ax
        c = [float(v) for v in o["center"][:2]]
        s = (c[0] - ox) * ux + (c[1] - oy) * uy
        d = -(c[0] - ox) * uy + (c[1] - oy) * ux
        out.append(_band((ox - uy * d, oy + ux * d), (ux, uy), s - width / 2.0 + GAP_CLEAR_M,
                         s + width / 2.0 - GAP_CLEAR_M, float(w["thickness"]) + 2 * TOUCH_M))
    return out


def _same_height(a: dict, c: dict) -> bool:
    ha, hc = a.get("height"), c.get("height")
    return (ha is None) == (hc is None) and (ha is None or abs(float(ha) - float(hc)) <= HEIGHT_M) and \
        bool(a.get("parapet")) == bool(c.get("parapet"))


def _drawn(w: dict) -> bool:
    return w.get("status") != "unverified" and not w.get("inferred")


def _extensions(p: dict, prect: Polygon, walls: list[dict], gaps: list[Polygon]) -> list[tuple]:
    """Every wall whose end runs into block ``p``, extended along its line to the block's far side, that adds no
    material outside the block and the other walls and crosses no gap: ``(wall, end, new_s, extension, rank)``."""
    others = [w for w in walls if w is not p]
    rest = unary_union([r for r in (rect(w) for w in others) if r is not None] + [prect])
    lp = _axis(p)[2]
    out = []
    for q in others:
        ax = _axis(q)
        if ax is None or not _same_height(p, q) or (_drawn(p) and not _drawn(q)):
            continue
        if is_block(q) and ax[2] <= lp:
            continue
        tq = float(q["thickness"])
        s0, s1, d0, d1 = _proj(ax, prect)
        if d1 <= -tq / 2.0 + 1e-6 or d0 >= tq / 2.0 - 1e-6:
            continue                                    # the block lies beside the wall's band, not in its line
        for end in ("end", "start"):
            if end == "end":
                if not (s1 > ax[2] + 0.005 and s0 <= ax[2] + TOUCH_M):
                    continue
                lo, hi, new = ax[2], s1, s1
            else:
                if not (s0 < -0.005 and s1 >= -TOUCH_M):
                    continue
                lo, hi, new = s0, 0.0, s0
            if hi - lo > max(lp, float(p["thickness"])) + TOUCH_M:
                continue
            ext = _band(ax[0], ax[1], lo, hi, tq)
            added = ext.difference(rest)
            if not thin(added) or added.area > max((1.0 - COVER_SHARE) * prect.area, SLIVER_M ** 2) + 1e-9 or any(ext.intersection(g).area > 1e-6 for g in gaps):
                continue
            same_line = abs(d0 + tq / 2.0) <= THICKNESS_M and abs(d1 - tq / 2.0) <= THICKNESS_M
            out.append((q, end, new, ext, (0 if same_line else 1, -ext.intersection(prect).area, str(q["id"]))))
    return out


def covers(prect: Polygon, geom, thickness: float) -> bool:
    """``geom`` covers the block: ``COVER_SHARE`` of its area, and nothing left over wider than ``SLIVER_M`` or half
    the block's thickness (a block thinner than a sliver is never covered by its slivers; pure)."""
    rest = prect.difference(geom)
    return rest.area <= (1.0 - COVER_SHARE) * prect.area + 1e-9 and thin(rest, min(SLIVER_M, thickness / 2.0))


def _parallel(a: dict, c: dict, deg: float = 3.0) -> bool:
    ua, uc = _axis(a)[1], _axis(c)[1]
    return abs(ua[0] * uc[1] - ua[1] * uc[0]) <= math.sin(math.radians(deg))


def _centred(w: dict, prect: Polygon) -> bool:
    """The block's middle lies on wall ``w``'s centre line (within ``2 * LINE_M``; pure)."""
    ax = _axis(w)
    _s0, _s1, d0, d1 = _proj(ax, prect)
    return abs((d0 + d1) / 2.0) <= 2 * LINE_M


def _as_high(q: dict, p: dict) -> bool:
    hq, hp = q.get("height"), p.get("height")
    return hp is None or (hq is not None and float(hq) >= float(hp) - HEIGHT_M)


def _fold_one(p: dict, walls: list[dict], gaps: list[Polygon], inside_only: bool = False) -> Optional[tuple]:
    """How block ``p`` folds: ``(reason, [(wall, end, new_s), ...], kept_by)`` or None (module docstring); with
    ``inside_only`` (a wall run) only when it lies inside other walls at least as high."""
    prect = rect(p)
    tp = float(p["thickness"])
    others = [w for w in walls if w is not p]
    near = [w for w in others if rect(w) is not None and rect(w).distance(prect) <= TOUCH_M and _as_high(w, p)]
    # a piece inside a thicker wall on its own centre line is RC14's wall_in_wall: which of the two is right the
    # drawing must say (a thin wall read in a thick band, or a thick band read over a thin wall), so such a wall does
    # not count; a wall run counts only crossing walls or a wall of its own thickness (the same wall read twice)
    near = [w for w in near if not _parallel(w, p) or abs(float(w["thickness"]) - tp) <= THICKNESS_M
            or (not inside_only and not _centred(w, prect))]
    covered = unary_union([rect(w) for w in near]) if near else None
    if covered is not None and covers(prect, covered, tp):
        inside = sorted(str(w["id"]) for w in near if rect(w).intersection(prect).area > 1e-6)
        if inside:
            return f"lies inside {', '.join(inside)}", [], inside[0]
    if inside_only:
        return None
    cands = sorted(_extensions(p, prect, walls, gaps), key=lambda c: c[4])
    base = covered if covered is not None else Polygon()
    for c in cands:
        if covers(prect, base.union(c[3]), tp):
            return "", [c[:3]], str(c[0]["id"])
    for i, c in enumerate(cands):
        for e in cands[i + 1:]:
            if e[0] is c[0]:
                continue
            if covers(prect, base.union(c[3]).union(e[3]), tp):
                return "", [c[:3], e[:3]], str(c[0]["id"])
    return None


def _set_span(w: dict, end: str, new_s: float) -> float:
    (ox, oy), (ux, uy), length = _axis(w)
    if end == "end":
        w["end"] = [round(ox + ux * new_s, 4), round(oy + uy * new_s, 4)]
        return new_s - length
    w["start"] = [round(ox + ux * new_s, 4), round(oy + uy * new_s, 4)]
    return -new_s


def _retire(b: dict, gone: dict, keep_id: str, rule: str, reason: str) -> None:
    from wenart.ingest.generic import twin_walls as TW

    b["walls"] = [w for w in b["walls"] if w is not gone]
    TW._rename(b, gone["id"], keep_id)
    b.setdefault("walls_merged", []).append(dict(copy.deepcopy(gone), merged_into=keep_id, corrected_by_ai={
        "by": "code", "rule": rule, "reason": reason, "evidence": list(gone.get("evidence") or [])}))


def fold_blocks(b: dict, warn: Callable[[str], None] = lambda _m: None) -> list[dict]:
    """Fold every block into the walls that run into it (mutates ``b``; module docstring). Returns one record per
    block: ``{level_id, kind: "block", walls: [block, wall ...], text, place}``."""
    notes = []
    levels = sorted({str(w.get("level_id")) for w in b.get("walls") or [] if isinstance(w, dict)})
    for lid in levels:
        refused: set = set()
        while True:
            walls = [w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id")
                     and str(w.get("level_id")) == lid and _axis(w)]
            by_id = {w["id"]: w for w in walls}
            gaps = _gaps(b, lid, by_id)
            hosts = {o.get("wall_id") for o in b.get("openings") or [] if isinstance(o, dict)}
            blocks = sorted((w for w in walls if w["id"] not in refused and w["id"] not in hosts),
                            key=lambda w: (not is_block(w), rect(w).area, str(w["id"])))
            done = False
            for p in blocks:
                how = _fold_one(p, walls, gaps, inside_only=not is_block(p))
                if how is None:
                    refused.add(p["id"])
                    continue
                inside, exts, keep_id = how
                lp, tp = _axis(p)[2], float(p["thickness"])
                moved = []
                for q, end, new_s in exts:
                    before = {"start": list(q["start"]), "end": list(q["end"])}
                    grown = _set_span(q, end, new_s)
                    q.setdefault("folded_blocks", []).append(
                        {"id": p["id"], "length": round(lp, 4), "thickness": round(tp, 4),
                         "extended_m": round(grown, 4), "end": end, "before": before})
                    moved.append(f"{q['id']} {grown:+.2f} m at its {end}")
                if not is_block(p):
                    what = f"a {lp:.2f} m wall {tp:.2f} m thick {inside}: the same wall material read twice"
                else:
                    what = (f"a {lp:.2f} m piece {tp:.2f} m thick is a block of wall material, not a wall run: "
                            + (inside if inside else f"the walls that run into it cover it ({'; '.join(moved)})"))
                ctr = rect(p).centroid
                for o in b.get("openings") or []:
                    if isinstance(o, dict) and o.get("wall_id") == p["id"] and o.get("center"):
                        o["wall_id"] = _host(o, [w for w in walls if w is not p]) or keep_id
                _retire(b, p, keep_id, RULE_FOLD, what)
                notes.append({"level_id": lid, "kind": "block", "walls": [p["id"]] + [q["id"] for q, _e, _s in exts],
                              "text": f"{lid}: {p['id']}: {what}", "place": [round(ctr.x, 3), round(ctr.y, 3)]})
                done = True
                break
            if not done:
                break
    if notes:
        warn(f"wall blocks: {len(notes)} blocks of wall material folded into the walls that run into them")
    return notes


def _host(o: dict, walls: list[dict]) -> Optional[str]:
    from shapely.geometry import Point

    c = Point(float(o["center"][0]), float(o["center"][1]))
    best = min(((rect(w).distance(c), str(w["id"])) for w in walls if rect(w) is not None), default=None)
    return best[1] if best is not None and best[0] <= 0.05 else None


def _line_pair(a: dict, c: dict) -> Optional[tuple[float, float]]:
    """``(lo, hi)`` along ``a``'s axis when ``c`` lies on ``a``'s line and their spans touch (pure)."""
    ax, cx = _axis(a), _axis(c)
    if ax is None or cx is None:
        return None
    (ox, oy), (ux, uy), la = ax
    if abs(ux * cx[1][1] - uy * cx[1][0]) > math.sin(math.radians(ANGLE_DEG)):
        return None
    s, d = [], []
    for p in (c["start"], c["end"]):
        dx, dy = float(p[0]) - ox, float(p[1]) - oy
        s.append(dx * ux + dy * uy)
        d.append(-dx * uy + dy * ux)
    if max(abs(v) for v in d) > LINE_M:
        return None
    lo, hi = min(s), max(s)
    if lo > la + JOIN_GAP_M or hi < -JOIN_GAP_M:
        return None
    return min(0.0, lo), max(la, hi)


BRIDGE_RULES = ("wide_gap",)          # inferred walls that only bridge a gap between two drawn jambs ...
BRIDGE_OPENING_SHARE = 0.5            # ... whose drawn openings fill at least this share of it


def drawn_bridge(w: dict, openings: list) -> bool:
    """An inferred wall that bridges a wide gap (``BRIDGE_RULES``) holding only openings read from the drawing (doors
    and windows, status verified) that fill ``BRIDGE_OPENING_SHARE`` of it: the drawing shows that wall, as a run gap
    shows the wall through its openings (pure)."""
    rules = {e.get("rule") for e in w.get("evidence") or [] if isinstance(e, dict)}
    if not rules or not rules <= set(BRIDGE_RULES):
        return False
    ax = _axis(w)
    own = [o for o in openings if isinstance(o, dict) and o.get("wall_id") == w.get("id")]
    if ax is None or not own or any(o.get("status") == "unverified" or o.get("type") not in ("door", "window")
                                    for o in own):
        return False
    return sum(float(o.get("width") or 0.0) for o in own) >= BRIDGE_OPENING_SHARE * ax[2]


def merge_collinear(b: dict, warn: Callable[[str], None] = lambda _m: None) -> list[dict]:
    """Merge every two walls on one line whose spans touch into one wall (mutates ``b``; module docstring)."""
    notes = []
    levels = sorted({str(w.get("level_id")) for w in b.get("walls") or [] if isinstance(w, dict)})
    for lid in levels:
        while True:
            walls = sorted((w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id")
                            and str(w.get("level_id")) == lid and _axis(w)),
                           key=lambda w: (-_axis(w)[2], str(w["id"])))
            ops = b.get("openings") or []
            drawn = {w["id"]: _drawn(w) or drawn_bridge(w, ops) for w in walls}
            found = None
            for i, a in enumerate(walls):
                for c in walls[i + 1:]:
                    if abs(float(a["thickness"]) - float(c["thickness"])) > THICKNESS_M or not _same_height(a, c) \
                            or drawn[a["id"]] != drawn[c["id"]] or bool(a.get("exterior")) != bool(c.get("exterior")) \
                            or a.get("leaves") or c.get("leaves"):
                        continue
                    if _line_pair(a, c) is not None:
                        found = (a, c) if _drawn(a) or not _drawn(c) else (c, a)    # a drawn wall keeps its id
                        break
                if found:
                    break
            if not found:
                break
            a, c = found
            lo, hi = _line_pair(a, c)
            (ox, oy), (ux, uy), la = _axis(a)
            before = {"start": list(a["start"]), "end": list(a["end"])}
            a["start"] = [round(ox + ux * lo, 4), round(oy + uy * lo, 4)]
            a["end"] = [round(ox + ux * hi, 4), round(oy + uy * hi, 4)]
            a["evidence"] = list(a.get("evidence") or []) + [e for e in c.get("evidence") or []
                                                            if e not in (a.get("evidence") or [])]
            bridge = _drawn(a) and not _drawn(c)
            a.setdefault("joined_walls", []).append({"id": c["id"], "before": before, **(
                {"bridge": "a wide gap's inferred wall holding only drawn openings"} if bridge else {})})
            why = (f"{c['id']} lies on the line of {a['id']} ({float(c['thickness']):.2f} and "
                   f"{float(a['thickness']):.2f} m thick) and touches it: one wall on one line, {hi - lo:.2f} m"
                   + ("; it bridged a wide gap whose openings are all drawn" if bridge else ""))
            _retire(b, c, a["id"], RULE_MERGE, why)
            notes.append({"level_id": lid, "kind": "line", "walls": [a["id"], c["id"]], "text": f"{lid}: {why}",
                          "place": [round(ox + ux * (lo + hi) / 2, 3), round(oy + uy * (lo + hi) / 2, 3)]})
    if notes:
        warn(f"wall lines: {len(notes)} walls joined the wall on their line")
    return notes
