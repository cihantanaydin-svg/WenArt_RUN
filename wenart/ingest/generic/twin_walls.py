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
of them (one opening read twice: it goes to ``building["openings_merged"]``; 12 Nov 2026: a door on the copy outranks a
plain gap of the kept wall when it is drawn (``_drawn``), the gap is merged into it; 26 Nov 2026, R27: when it is typed
(``typed_door``: a swing, sliding leaves on a door layer, a door block, a size tag), keeping its width); every other
``wall_id`` that names it names the kept wall.

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
# 20 Nov 2026 (pre-pod check R09-11, real09 L0-L2: a 0.23 m wall paired from the outer plaster line and a plaster line
# through the middle of the 0.40 m piers lay inside the 0.46 m front walls w_006 / w_007 (55 % and 41 % of it each, so
# no single wall made it a copy); its 2.9 m gaps became 2.9 m windows cut through the real wall beside the drawn 1.5 m
# ones): a thinner wall whose two faces lie inside the band of thicker parallel walls (within ``BAND_FACE_TOL_M``) that
# together cover ``OVERLAP_SHARE`` of its length is no wall of its own either
BAND_FACE_TOL_M = 0.02


def _drawn(o: dict) -> bool:
    """The door is read from its drawn swing (operation swing, or double: review B2 CB-3), with an evidence of method
    vector or raster and none inferred; not from leaf lines alone (real06: the 1.95 m 'sliding door' of six parallel
    lines in the kitchen's 2.9 m gap, user, 29 Oct 2026: "is there a door behind it?")."""
    ev = o.get("evidence") or []
    ev = ev if isinstance(ev, list) else [ev]
    return o.get("operation") in ("swing", "double") and \
        any(isinstance(e, dict) and e.get("method") in ("vector", "raster") for e in ev) and \
        not any(isinstance(e, dict) and e.get("method") == "inferred" for e in ev)


NO_SWING_OPERATIONS = ("sliding", "pocket", "folding")
TAG_RULES = ("size_tag", "size_tag_jamb", "size_tag_leaf_door")
BLOCK_NAME_NOTE = "door by its block name"


def typed_door(o: dict) -> Optional[str]:
    """26 Nov 2026 (R27, UL395; the user's C0100 on real06, "sliding door", which settles C0065's question): why a door
    is a typed opening that outranks an unclassified gap read over it when two readings of one opening merge, or None
    (pure): its drawn swing (``_drawn``); sliding (pocket, folding) leaves drawn on a door layer or in a door block
    (``openings._opening``: evidence ``door_layer``, or a door block by its name), read from vector or raster
    geometry and none inferred; or a door size tag (evidence rule ``size_tag*``). Leaf lines on no door layer (a frame's
    or a counter's lines can read so) are not enough: the gap stays."""
    if _drawn(o):
        return "its drawn swing"
    ev = o.get("evidence") or []
    ev = [e for e in (ev if isinstance(ev, list) else [ev]) if isinstance(e, dict)]
    if any(e.get("rule") in TAG_RULES for e in ev):
        return "its door size tag"
    if o.get("operation") in NO_SWING_OPERATIONS and any(e.get("method") in ("vector", "raster") for e in ev) \
            and not any(e.get("method") == "inferred" for e in ev):
        if any(e.get("door_layer") for e in ev):
            layer = next((e.get("layer") for e in ev if e.get("layer")), None)
            return f"its {o['operation']} leaves drawn on the door layer" + (f" '{layer}'" if layer else "")
        if any(str(e.get("note") or "").startswith(BLOCK_NAME_NOTE) for e in ev):
            return "its door block"
    return None


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


STAIR_WALL_EMBED_M = 0.03       # 13 Nov 2026: a wall face this deep inside a stair's flight is a reading error ...
STAIR_WALL_MIN_T_M = 0.05       # ... the wall keeps at least this thickness once its face is moved to the flight's side
STAIR_WALL_ALONG_M = 0.10       # ... running at least this far along the flight (real10's 0.14-0.29 m pairing stubs)
STAIR_WALL_DEEP = 0.25          # ... and only a face reaching a quarter of the flight in (the walking line runs half way in;
#                                 a flight read a little too wide is no reason to move a wall)


LEAFLESS_NOTE = "swing arc without a drawn leaf"     # ``openings._opening``: a door from an arc alone
ONE_DOOR_RULE = "reading.one_door_per_gap"


SLIDING_LINES_NOTE = "drawn parallel to the wall without a swing arc"   # ``openings._opening``: a door from lines alone
SECOND_LEAF_MIN_M = 0.30            # the rest of a door's frame beside its swung leaf this wide is a second leaf


def _leafless(o: dict) -> bool:
    ev = o.get("evidence") or []
    return any(isinstance(e, dict) and e.get("note") == LEAFLESS_NOTE for e in (ev if isinstance(ev, list) else [ev]))


def _lines_only(o: dict) -> bool:
    """A sliding door read from lines parallel to its wall, no swing arc (a frame's lines can read so)."""
    ev = o.get("evidence") or []
    return o.get("operation") == "sliding" and any(
        isinstance(e, dict) and SLIDING_LINES_NOTE in str(e.get("note") or "") for e in (ev if isinstance(ev, list) else [ev]))


def one_door_per_gap(b: dict, warn: Callable[[str], None] = lambda _m: None) -> list[str]:
    """19 Nov 2026 (review A3, M5: real09 L-1..L2, one bedroom door read as two in one gap: d_L0_020 from its own arc
    and leaf, d_L0_014 from the arc ARC:82D alone, which is the swing of the flat's entrance door in the cross wall): two
    doors on one wall covering at least ``SAME_OPENING_SHARE`` of the narrower are one door read twice when one of them is
    read from a swing arc alone (``LEAFLESS_NOTE``) and the other from its drawn swing with its leaf (``_drawn``): the
    arc-only door goes to ``openings_merged`` (``corrected_by_ai``, merged into the other). Mutates ``b``; returns the
    merged ids.

    19 Nov 2026 (review A3, A3FC-3: real13's main entrance, one 150 cm double door in its KAPI-KASA frame, read as a
    1.50 m sliding door from the frame lines of the 100 cm leaf and a 0.91 m swing door inside it): a sliding door read
    from lines alone (``_lines_only``) over which a drawn swing door stands is that door's frame: the swing door takes
    the frame's span, a double door when the rest beside its leaf is a leaf wide (``SECOND_LEAF_MIN_M``), and the
    sliding door goes to ``openings_merged``."""
    walls = {w["id"]: w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id")}
    doors = [o for o in b.get("openings") or [] if isinstance(o, dict) and o.get("type") == "door"
             and o.get("wall_id") in walls and o.get("center")]
    gone: list[str] = []
    for o in doors:
        if o["id"] in gone or not _lines_only(o):
            continue
        ax = _axis(walls[o["wall_id"]])
        if ax is None:
            continue
        t, half = _t(ax, o["center"]), float(o.get("width") or 0.0) / 2.0
        for p in doors:
            if p is o or p["id"] in gone or p.get("wall_id") != o["wall_id"] or not _drawn(p) or _leafless(p):
                continue
            tp, hp = _t(ax, p["center"]), float(p.get("width") or 0.0) / 2.0
            cover = min(t + half, tp + hp) - max(t - half, tp - hp)
            if cover < SAME_OPENING_SHARE * max(min(2 * half, 2 * hp), 1e-6) or 2 * hp > 2 * half + 0.05:
                continue
            lo, hi = min(t - half, tp - hp), max(t + half, tp + hp)
            rest = (hi - lo) - 2 * hp
            (x0, y0), (ux, uy), _ = ax
            before = {"center": list(p["center"]), "width": p.get("width"), "operation": p.get("operation")}
            p["center"] = [round(x0 + ux * (lo + hi) / 2.0, 4), round(y0 + uy * (lo + hi) / 2.0, 4)]
            p["width"] = round(hi - lo, 4)
            if rest >= SECOND_LEAF_MIN_M:
                p["operation"], p["operation_source"] = "double", "geometry"
            reason = (f"the sliding door {o['id']} ({2 * half:.2f} m) is read from lines alone where the swing door "
                      f"{p['id']} ({2 * hp:.2f} m) stands: the lines are its frame; the door takes the frame's "
                      f"{hi - lo:.2f} m" + (f", the {rest:.2f} m beside its leaf a second leaf (double door)"
                                             if rest >= SECOND_LEAF_MIN_M else ""))
            p["corrected_by_ai"] = {"by": "code", "rule": ONE_DOOR_RULE, "reason": reason, "before": before,
                                    "evidence": [o["id"]]}
            b["openings"] = [x for x in b["openings"] if x is not o]
            b.setdefault("openings_merged", []).append(dict(copy.deepcopy(o), merged_into=p["id"], corrected_by_ai={
                "by": "code", "rule": ONE_DOOR_RULE, "reason": reason, "evidence": [p["id"]]}))
            gone.append(o["id"])
            warn(f"one door per gap: {reason}")
            break
    for o in doors:
        if o["id"] in gone or not _leafless(o):
            continue
        ax = _axis(walls[o["wall_id"]])
        if ax is None:
            continue
        t, half = _t(ax, o["center"]), float(o.get("width") or 0.0) / 2.0
        for p in doors:
            if p is o or p["id"] in gone or p.get("wall_id") != o["wall_id"] or _leafless(p) or not _drawn(p):
                continue
            tp, hp = _t(ax, p["center"]), float(p.get("width") or 0.0) / 2.0
            cover = min(t + half, tp + hp) - max(t - half, tp - hp)
            if cover < SAME_OPENING_SHARE * max(min(2 * half, 2 * hp), 1e-6):
                continue
            arcs = ", ".join(str(e.get("entity")) for e in o.get("evidence") or [] if isinstance(e, dict)
                             and e.get("entity"))
            reason = (f"{o['id']} ({float(o.get('width') or 0):.2f} m) is read from a swing arc alone ({arcs}) in the gap "
                      f"the door {p['id']} fills with its own arc and leaf: one door read twice, the arc another "
                      f"door's swing")
            b["openings"] = [x for x in b["openings"] if x is not o]
            b.setdefault("openings_merged", []).append(dict(copy.deepcopy(o), merged_into=p["id"], corrected_by_ai={
                "by": "code", "rule": ONE_DOOR_RULE, "reason": reason, "evidence": [p["id"]]}))
            gone.append(o["id"])
            warn(f"one door per gap: {reason}")
            break
    return gone


def stair_side_walls(b: dict, warn: Callable[[str], None] = lambda _m: None) -> list[str]:
    """13 Nov 2026 (review BLD-05: real10's stairwell plaster faces were paired with the stairs' walking lines, drawn on
    the same layer, into walls 0.57-0.71 m thick standing across half of each flight): a wall running along a stair's
    flight whose face lies more than ``STAIR_WALL_EMBED_M`` inside the flight while its other face lies outside it has
    that face moved to the flight's side (its thickness and centre line follow); the wall is labelled
    ``corrected_by_ai`` (by code) with its drawn line and thickness. Walls across a flight, or wholly inside it, are left
    as read. Mutates ``b["walls"]``; returns one line per wall."""
    notes = []
    walls = b.get("walls") or []
    for f in b.get("furniture") or []:
        st = f.get("stair") or {}
        if f.get("type") != "stair" or not st.get("flights"):
            continue
        for fl in st["flights"]:
            try:
                s0, e0, fw = tuple(fl["start"][:2]), tuple(fl["end"][:2]), float(fl["width"])
            except (KeyError, TypeError, ValueError):
                continue
            length = math.dist(s0, e0)
            if length < 0.3 or fw <= 0:
                continue
            u = ((e0[0] - s0[0]) / length, (e0[1] - s0[1]) / length)
            n = (-u[1], u[0])
            for w in walls:
                if w.get("level_id") != f.get("level_id") or w.get("start") == w.get("end"):
                    continue
                a, c = tuple(w["start"][:2]), tuple(w["end"][:2])
                wl = math.dist(a, c)
                wu = ((c[0] - a[0]) / wl, (c[1] - a[1]) / wl)
                if abs(u[0] * wu[1] - u[1] * wu[0]) > 0.05:
                    continue                                         # not along the flight
                ta = sorted(((q[0] - s0[0]) * u[0] + (q[1] - s0[1]) * u[1]) for q in (a, c))
                if min(ta[1], length) - max(ta[0], 0.0) < min(STAIR_WALL_ALONG_M, length / 2.0):
                    continue
                off = (a[0] - s0[0]) * n[0] + (a[1] - s0[1]) * n[1]
                t = float(w.get("thickness") or 0.0) / 2.0
                lo, hi = off - t, off + t
                deep = max(STAIR_WALL_EMBED_M, STAIR_WALL_DEEP * fw)
                if off >= 0 and lo < fw / 2.0 - deep and hi > fw / 2.0 + 0.02:
                    nlo, nhi = fw / 2.0, hi
                elif off < 0 and hi > -fw / 2.0 + deep and lo < -fw / 2.0 - 0.02:
                    nlo, nhi = lo, -fw / 2.0
                else:
                    continue
                if nhi - nlo < STAIR_WALL_MIN_T_M:
                    continue
                shift = (nlo + nhi) / 2.0 - off
                before = {"start": list(w["start"]), "end": list(w["end"]), "thickness": w.get("thickness")}
                w["start"] = [round(a[0] + n[0] * shift, 4), round(a[1] + n[1] * shift, 4)]
                w["end"] = [round(c[0] + n[0] * shift, 4), round(c[1] + n[1] * shift, 4)]
                w["thickness"] = round(nhi - nlo, 4)
                reason = (f"its face stood {abs((lo if off >= 0 else hi) - (fw / 2.0 if off >= 0 else -fw / 2.0)):.2f} m "
                          f"inside the flight of stair {f.get('id')} (a stair line paired with the stairwell's face): "
                          f"the face moved to the flight's side")
                w["corrected_by_ai"] = {"by": "code", "rule": "stair_side_wall", "reason": reason, "before": before}
                notes.append(f"{w.get('id')}: {before['thickness']} -> {w['thickness']} m thick, {reason}")
                warn(f"stair side wall: {notes[-1]}")
    return notes


def in_band(d: dict, walls: list) -> list:
    """The thicker walls (``THICKER_TOL_M``) parallel to ``d`` (``ANGLE_DEG``) whose band holds both of ``d``'s faces
    (within ``BAND_FACE_TOL_M``) along part of its length, when together they cover ``OVERLAP_SHARE`` of it; else []
    (pure; R09-11)."""
    ad = _axis(d)
    if ad is None or ad[2] < MIN_COPY_M:
        return []
    td = float(d.get("thickness") or 0.0)
    spans, hosts = [], []
    for c in walls:
        if c is d or c.get("level_id") != d.get("level_id"):
            continue
        ac = _axis(c)
        tc = float(c.get("thickness") or 0.0)
        if ac is None or tc <= td + THICKER_TOL_M:
            continue
        if abs(ad[1][0] * ac[1][1] - ad[1][1] * ac[1][0]) > math.sin(math.radians(ANGLE_DEG)):
            continue
        if max(_off(ac, d["start"]), _off(ac, d["end"])) + td / 2.0 > tc / 2.0 + BAND_FACE_TOL_M:
            continue
        t0, t1 = sorted((_t(ad, c["start"]), _t(ad, c["end"])))
        lo, hi = max(0.0, t0), min(ad[2], t1)
        if hi > lo:
            spans.append((lo, hi))
            hosts.append(c)
    covered, end = 0.0, None
    for lo, hi in sorted(spans):
        if end is None or lo > end:
            covered += hi - lo
            end = hi
        elif hi > end:
            covered += hi - end
            end = hi
    return hosts if covered >= OVERLAP_SHARE * ad[2] - 1e-6 else []


def merge_twin_walls(b: dict, warn: Callable[[str], None] = lambda _m: None) -> list[str]:
    """Drop every wall read twice (mutates ``b``; module docstring) and every thinner wall inside the band of thicker
    collinear walls (``in_band``, R09-11: its openings go to the host wall they stand on). Returns the dropped wall
    ids."""
    walls = [w for w in b.get("walls") or [] if isinstance(w, dict) and w.get("id")]
    dropped: dict[str, str] = {}
    hosts_of: dict[str, list] = {}
    for i, a in enumerate(walls):
        for c in walls[i + 1:]:
            if a["id"] in dropped or c["id"] in dropped or not twin_of(a, c):
                continue
            keep, dup = (a, c) if _rank(a) >= _rank(c) else (c, a)
            if _axis(dup)[2] < MIN_COPY_M or \
                    float(dup.get("thickness") or 0.0) > float(keep.get("thickness") or 0.0) + THICKER_TOL_M:
                continue                       # a column or a pier in the wall, not a copy of it
            dropped[dup["id"]] = keep["id"]
    for d in walls:
        if d["id"] in dropped:
            continue
        hosts = [c for c in in_band(d, [w for w in walls if w["id"] not in dropped])]
        if hosts:
            ad = _axis(d)

            def along(c):
                t0, t1 = sorted((_t(ad, c["start"]), _t(ad, c["end"])))
                return min(ad[2], t1) - max(0.0, t0)
            dropped[d["id"]] = max(hosts, key=along)["id"]
            hosts_of[d["id"]] = [c["id"] for c in hosts]
    if not dropped:
        return []
    by_id = {w["id"]: w for w in walls}
    ops = [o for o in b.get("openings") or [] if isinstance(o, dict)]
    for dup_id, keep_id in dropped.items():
        while keep_id in dropped:                      # a chain of copies ends at the kept one
            keep_id = dropped[keep_id]
        dup, keep = by_id[dup_id], by_id[keep_id]
        ax = _axis(keep)
        if dup_id in hosts_of:
            reason = (f"{dup_id} ({float(dup.get('thickness') or 0):.2f} m) lies with both faces inside the band of the "
                      f"thicker parallel wall(s) {', '.join(hosts_of[dup_id])}, which cover "
                      f"{OVERLAP_SHARE:.0%} or more of it: a line inside the wall read as a wall; {dup_id} is not built")
        else:
            reason = (f"{dup_id} lies in {keep_id} ({_off(ax, [(float(dup['start'][i]) + float(dup['end'][i])) / 2.0 for i in (0, 1)]):.3f} m "
                      f"apart, parallel, overlapping): one wall read twice; {dup_id} is not built")
        moved, merged = [], []
        for o in [o for o in ops if o.get("wall_id") == dup_id]:
            host_id = keep_id
            if dup_id in hosts_of:
                # R09-11: the opening goes to the host wall it stands on (the nearest along its line)
                def gap(c, o=o):
                    ac = _axis(c)
                    t = _t(ac, o["center"])
                    return max(0.0, -t, t - ac[2])
                host_id = min(hosts_of[dup_id], key=lambda cid: gap(by_id[cid]))
                while host_id in dropped:
                    host_id = dropped[host_id]
            ax = _axis(by_id[host_id])
            keep_here = host_id
            t = _t(ax, o["center"])
            half = float(o.get("width") or 0.0) / 2.0
            same = None
            for p in ops:
                if p is o or p.get("wall_id") != keep_here:
                    continue
                tp, hp = _t(ax, p["center"]), float(p.get("width") or 0.0) / 2.0
                cover = min(t + half, tp + hp) - max(t - half, tp - hp)
                if cover >= SAME_OPENING_SHARE * max(min(2 * half, 2 * hp), 1e-6):
                    same = p
                    break
            why = typed_door(o) if same is not None and o.get("type") == "door" and same.get("type") == "opening" \
                and not same.get("virtual") else None
            if why:
                # 12 Nov 2026 (real07 C0047, the user's correction: the Kat Kal. door read on the copy, a 1.56 m gap read
                # over it on the kept wall; the door was merged into the gap and lost): a drawn door outranks a gap
                # read over it, the gap is merged into the door. 26 Nov 2026 (R27, UL395, the user's C0100 on real06:
                # "sliding door"): any typed door does (``typed_door``: a swing, sliding leaves on a door layer, a door
                # block, a size tag); it keeps its own width, the rest of the gap is the wall's (the drawn piers)
                b["openings"] = [x for x in b["openings"] if x is not same]
                ops = [x for x in ops if x is not same]
                b.setdefault("openings_merged", []).append(dict(copy.deepcopy(same), merged_into=o["id"], corrected_by_ai={
                    "by": "code", "rule": RULE, "reason": f"{same['id']} ({float(same.get('width') or 0):.2f} m) of "
                                                           f"{keep_here} is the door {o['id']} "
                                                           f"({float(o.get('width') or 0):.2f} m) on {dup_id} read "
                                                           f"twice; the door is typed by {why}, the gap is not, so the "
                                                           f"door stays with its width and the rest of the gap is "
                                                           f"wall ({reason})"}))
                merged.append(f"{same['id']} -> {o['id']}")
                same = None
            if same is not None:
                b["openings"] = [x for x in b["openings"] if x is not o]
                ops = [x for x in ops if x is not o]
                b.setdefault("openings_merged", []).append(dict(copy.deepcopy(o), merged_into=same["id"], corrected_by_ai={
                    "by": "code", "rule": RULE, "reason": f"{o['id']} on {dup_id} is {same['id']} of {keep_here} read "
                                                           f"twice ({reason})"}))
                merged.append(f"{o['id']} -> {same['id']}")
                continue
            (x0, y0), (ux, uy), _ = ax
            o.setdefault("drawn_center", list(o["center"]))
            o["center"] = [round(x0 + ux * t, 4), round(y0 + uy * t, 4)]
            o["wall_id"] = keep_here
            o["corrected_by_ai"] = {"by": "code", "rule": RULE, "reason": f"moved onto {keep_here}: {reason}",
                                    "changed": {"wall_id": dup_id}}
            moved.append(o["id"])
        b["walls"] = [w for w in b["walls"] if w.get("id") != dup_id]
        _rename(b, dup_id, keep_id)
        b.setdefault("walls_merged", []).append(dict(copy.deepcopy(dup), merged_into=keep_id, corrected_by_ai={
            "by": "code", "rule": RULE, "reason": reason, "evidence": list(dup.get("evidence") or [])
            + list(keep.get("evidence") or [])}))
        warn(f"{dup_id}: {reason}" + (f"; openings moved: {', '.join(moved)}" if moved else "")
             + (f"; openings read twice, merged: {', '.join(merged)}" if merged else ""))
    return sorted(dropped)
