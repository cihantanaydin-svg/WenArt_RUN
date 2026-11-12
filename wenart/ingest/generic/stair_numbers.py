"""Stairs read from their numbered treads (3 Nov 2026).

What: ``chains(texts)`` -> the runs of tread numbers a plan writes on a stair (1, 2, 3 ... N; small integer texts,
each the next within ``STEP_M``; one missing number bridged); ``stair_of(chain, strokes)`` -> the stair they describe
(page metres): its straight arms (the runs of numbers in one direction) as flights, measured on the tread lines the
numbers stand on, the turn between two arms as the landing holding the winders (its numbers), the rise from 1 to N
(drawn, not assumed); ``apply(pieces, cands, texts, strokes, ...)`` adds each numbered stair no stair piece already
holds and drops the candidates and pieces inside it (its parts).

Why: real09 (user: "each duplex flat has its inner stair (winders 1-17)"): the duplex flats' U stairs with winders
have four straight treads per arm, fewer than the stair rule's five evenly spaced lines (``symbols.STAIR_MIN_TREADS``);
they were read as two untyped 3.49 x 1.46 m boxes. Their treads are numbered 1-16, which says what they are, how many
risers they have and which way they rise.

How: pure geometry on the page's texts and strokes (page metres). Straight stairs and stairs of two arms (U and L, the
turn between them a landing holding its winders) are built; other shapes are listed (``notes``) and left to the stair
rule.
"""
from __future__ import annotations

import math
import re
from typing import Optional

from shapely.geometry import LineString, MultiPoint, Point, Polygon
from shapely.ops import unary_union

from wenart import building as B

NUMBER_RE = re.compile(r"^\s*(\d{1,2})\s*$")
NUMBER_H_MAX_M = 0.30           # tread numbers are small texts
STEP_M = (0.08, 0.60)           # the next number this far away (a tread's going, a winder's)
TURN_JUMP_M = 3.0               # 4 Nov 2026: across a half landing to the next arm at most this far (it must lead on)
TURN_NEAR_RATIO = 2.0           # 6 Nov 2026: a number on the landing this many times nearer wins (``chains``)
MIN_STEPS = 6                   # a chain of at least this many numbers, the last at least this
ARM_TURN_DEG = 25.0             # numbers in one arm: their steps within this of the arm's first step
ARM_MIN_POINTS = 3              # an arm holds at least this many numbers
TREAD_REACH_M = 0.22            # a tread line passes this close to its number
TREAD_PERP = 0.25               # ... nearly across the arm (|cos| under this)
WIDTH_M = (0.6, 2.0)            # an arm this wide (the median tread line)
WIDTH_DEFAULT_M = 0.9
INSIDE_SHARE = 0.5              # a stair piece holding this share of the numbers already reads the stair


def _numbers(texts: list) -> list[tuple[int, tuple[float, float], object]]:
    out = []
    for t in texts or []:
        m = NUMBER_RE.match(str(getattr(t, "text", "") or ""))
        if not m or float(getattr(t, "height", 0.0) or 0.0) > NUMBER_H_MAX_M:
            continue
        v = int(m.group(1))
        if 1 <= v <= 60:
            out.append((v, ((t.box[0] + t.box[2]) / 2.0, (t.box[1] + t.box[3]) / 2.0), t))
    return out


def chains(texts: list) -> list[list[tuple[int, tuple[float, float], object]]]:
    """The runs of tread numbers (the module docstring), longest first (of equal ones the most regular); each number
    in one run only, a run built again without the numbers a longer one took (pure)."""
    nums = _numbers(texts)
    by_value: dict[int, list[int]] = {}
    for k, (v, _p, _t) in enumerate(nums):
        by_value.setdefault(v, []).append(k)
    # 6 Nov 2026 (real10 L7, the roof terrace: the plan of the top floor numbers the arriving stair 2-17, its first
    # tread under the plan's cut; real07 L1 the same, 2-18): a 2 with no 1 within a step of it starts a chain too
    starts = list(by_value.get(1, []))
    starts += [k for k in by_value.get(2, []) if not any(math.dist(nums[k][1], nums[j][1]) <= STEP_M[1]
                                                          for j in by_value.get(1, []))]

    def build(start: int, banned: set) -> list[int]:
        """The chain from ``start``, never through a number of ``banned`` (another stair's)."""
        chain = [start]
        held = set(banned) | {start}
        while True:
            v, p, _t = nums[chain[-1]]
            nxt = None

            def leads(k: int, value: int) -> bool:
                # 4 Nov 2026 (real07, user: "Stairs are missing in the project"): a candidate the next number follows
                q = nums[k][1]
                return any(STEP_M[0] <= math.dist(q, nums[j][1]) <= STEP_M[1] for j in by_value.get(value + 1, [])
                           if j not in held and j != k)

            for skip, (lo, hi) in ((1, STEP_M), (2, (STEP_M[0] * 2, STEP_M[1] * 2))):
                cands = [(math.dist(p, nums[k][1]), k) for k in by_value.get(v + skip, [])
                         if k not in held and lo <= math.dist(p, nums[k][1]) <= hi]
                if cands:
                    # a candidate that leads on wins (the U-stair's step 9 had the wall-thickness text '10' beside it;
                    # its real step 10 lies across the landing)
                    on = [c for c in cands if leads(c[1], v + skip)]
                    nxt = min(on or cands)[1]
                    # 6 Nov 2026 (real13 L-1: the near stair's 7 ends its arm, its 8 stands on the landing 1.1 m on,
                    # and the other stair's 7 led on, 2.5 m away): a near number that runs on the arm (the last
                    # step's direction within ARM_TURN_DEG, at most twice its length) is the next tread
                    if not on and len(chain) >= 2 and skip == 1:
                        q0, q1 = nums[chain[-2]][1], p
                        last = math.dist(q0, q1)
                        d0 = _unit(q0, q1)
                        d1 = _unit(q1, nums[nxt][1])
                        if last > 0 and math.dist(q1, nums[nxt][1]) <= 2.0 * last \
                                and abs(_angle(d0, d1)) <= ARM_TURN_DEG:
                            on = [c for c in cands if c[1] == nxt]
                    if not on:
                        far = [(math.dist(p, nums[k][1]), k) for k in by_value.get(v + 1, [])
                               if k not in held and STEP_M[1] < math.dist(p, nums[k][1]) <= TURN_JUMP_M
                               and leads(k, v + 1)]
                        if far:
                            nxt = min(far)[1]
                    break
            if nxt is None:
                # the turn: the next number across the landing, where the next arm starts (it leads on)
                far = [(math.dist(p, nums[k][1]), k) for k in by_value.get(v + 1, [])
                       if k not in held and STEP_M[1] < math.dist(p, nums[k][1]) <= TURN_JUMP_M and leads(k, v + 1)]
                if far:
                    nxt = min(far)[1]
                # 6 Nov 2026 (real13 L-1: two stairs side by side; the near stair's 8 stands on its landing, 1.1 m from
                # 7 and from 9, and the other stair's 8 led on, 2.8 m away): a nearer number on the landing that the
                # next one follows across it (within TURN_JUMP_M) wins over one more than twice as far
                # (only after an arm of tread steps: a row of grid numbers 1.3 m apart is no stair)
                arm = len(chain) >= ARM_MIN_POINTS and all(
                    math.dist(nums[a][1], nums[b][1]) <= STEP_M[1] for a, b in zip(chain[-ARM_MIN_POINTS:],
                                                                                  chain[-ARM_MIN_POINTS + 1:]))
                near = [(math.dist(p, nums[k][1]), k) for k in by_value.get(v + 1, [])
                        if arm and k not in held and STEP_M[1] < math.dist(p, nums[k][1]) <= TURN_JUMP_M
                        and any(STEP_M[0] <= math.dist(nums[k][1], nums[j][1]) <= TURN_JUMP_M
                                for j in by_value.get(v + 2, []) if j not in held and j != k)]
                if near and (not far or min(near)[0] * TURN_NEAR_RATIO < min(far)[0]):
                    nxt = min(near)[1]
            if nxt is None:
                break
            chain.append(nxt)
            held.add(nxt)
        return chain

    def jump(chain: list[int]) -> float:
        return max((math.dist(nums[a][1], nums[b][1]) for a, b in zip(chain, chain[1:])), default=0.0)

    # 6 Nov 2026 (real18 L3: three numbered stairs side by side; one stair's 1-8 jumped 1.6 m to another's 9-15 and that
    # 15-number chain won over the other stair's own regular 1-15): the longest chain first, of equal ones the one with
    # the shortest longest step; the others are built again without the numbers taken
    out = []
    used: set = set()
    while True:
        found = []
        for start in starts:
            if start in used:
                continue
            chain = build(start, used)
            if len(chain) >= MIN_STEPS and nums[chain[-1]][0] >= MIN_STEPS:
                found.append(chain)
        if not found:
            break
        best = min(found, key=lambda c: (-len(c), round(jump(c), 3), c[0]))
        used |= set(best)
        out.append([nums[k] for k in best])
    return out


def _unit(a, b) -> tuple[float, float]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    return dx / n, dy / n


def _angle(u, v) -> float:
    return math.degrees(math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1]))


def _arms(points: list, segs: Optional[list] = None) -> list[list[int]]:
    """The arms of a numbered stair: the straight run from the first number (its steps within ``ARM_TURN_DEG`` of the
    first step) and the straight run back from the last; one arm when the first run holds every number. What lies
    between them is the turn (winders or a landing)."""
    def run(idx: list[int]) -> list[int]:
        out = idx[:2]
        ref = _unit(points[idx[0]], points[idx[1]])
        for k in idx[2:]:
            if abs(_angle(ref, _unit(points[out[-1]], points[k]))) > ARM_TURN_DEG:
                break
            out.append(k)
        return out

    n = len(points)
    if n < 2:
        return []
    first = run(list(range(n)))
    if len(first) == n:
        return [first]
    # 4 Nov 2026 (real10's fire escape stair, user: "There should have been fire escape ladders here": its top number
    # 16 stands by the arrow on the landing, off the arm's line, so the run back from it turned at once): an end number
    # off its arm is on the landing; the arm runs from the number next to it
    if len(first) < ARM_MIN_POINTS and n > ARM_MIN_POINTS + 1:
        inner = run(list(range(1, n)))
        if len(inner) >= ARM_MIN_POINTS:
            first = inner
    last = run(list(range(n - 1, -1, -1)))[::-1]
    if len(last) < ARM_MIN_POINTS and n > ARM_MIN_POINTS + 1:
        inner = run(list(range(n - 2, -1, -1)))[::-1]
        if len(inner) >= ARM_MIN_POINTS:
            last = inner
    if set(first) & set(last):
        return [first] if len(first) >= len(last) else [last]
    # 6 Nov 2026 (synthetic-15, UL286): an arm's treads are evenly spaced; the number at its turn end that stands a
    # different step away (> ARM_STEP_SPREAD off the arm's median step) is the first winder, not the arm's last tread
    first = _trim_arm(points, first, at_end=True, segs=segs)
    last = _trim_arm(points, last, at_end=False, segs=segs)
    return [r for r in (first, last) if len(r) >= ARM_MIN_POINTS]


ARM_STEP_SPREAD = 0.25          # 6 Nov 2026: a tread's step within this share of its arm's median step
ALONG_COS = 0.9                 # 12 Nov 2026: a line this near the arm's direction runs along it (a string, a wall)


EDGE_REACH = 1.5                # 12 Nov 2026: a tread's far edge lies within this many of its own steps ahead of its number


def _tread_edge(p, ahead, axis, reach: float, segs: list):
    """The far edge of the tread number ``p`` stands on (pure): the drawn line nearest to ``p`` that the ray from ``p``
    along ``ahead`` (the arm's direction into the turn) crosses within ``reach``, not running along the arm
    (``ALONG_COS``), as ``|cos|`` of its angle to the arm's ``axis``; None when no line is drawn there. (Not the step to
    the next number: across a U stair's half landing that runs along the landing's edge.)"""
    ray = LineString([p, (p[0] + ahead[0] * reach, p[1] + ahead[1] * reach)])
    best = None
    for a, b, _sid in segs or []:
        u = _unit(a, b)
        c = abs(u[0] * axis[0] + u[1] * axis[1])
        if c >= ALONG_COS:
            continue
        seg = LineString([a, b])
        if seg.distance(ray) > 1e-6:
            continue
        d = seg.distance(Point(p))
        if best is None or d < best[0]:
            best = (d, c)
    return None if best is None else best[1]


def _trim_arm(points: list, arm: list[int], at_end: bool, segs: Optional[list] = None) -> list[int]:
    """``arm`` without the numbers at its turn end (its end for the first arm, its start for the last) that are winders;
    at least ``ARM_MIN_POINTS`` numbers are kept (pure). A number there is a winder when its step from its neighbour in
    the arm differs from the arm's median step by more than ``ARM_STEP_SPREAD`` and (12 Nov 2026, review B S10: the
    5-degree offset of the label was tuned between two drawings) its tread's far edge turns from the arm's tread lines
    (a radial or diagonal line, ``|cos|`` to the arm over ``TREAD_PERP``; ``_tread_edge``, ahead of the number into the
    turn within ``EDGE_REACH`` of its step); a deeper tread whose edge is square to the arm stays the arm's (real18: the
    8 and the 9 by the half landing, 0.41 and 0.36 m on), and so does a number with no line drawn there (nothing drawn
    says the stair turns there). Both ends of a U are judged alike."""
    out = list(arm)
    while len(out) > ARM_MIN_POINTS:
        steps = [math.dist(points[a], points[b]) for a, b in zip(out, out[1:])]
        med = sorted(steps)[len(steps) // 2]
        edge = steps[-1] if at_end else steps[0]
        if med <= 0 or abs(edge - med) <= ARM_STEP_SPREAD * med:
            break
        rest = out[:-1] if at_end else out[1:]
        axis = _unit(points[rest[0]], points[rest[-1]])
        tip = out[-1] if at_end else out[0]
        ahead = axis if at_end else (-axis[0], -axis[1])
        c = _tread_edge(points[tip], ahead, axis, EDGE_REACH * edge, segs)
        if c is None or c <= TREAD_PERP:
            break
        out = rest
    return out


def _treads(points: list, axis, segs: list) -> list[tuple]:
    """The tread lines the numbers of one arm stand on: straight segments nearly across ``axis`` passing within
    ``TREAD_REACH_M`` of a number."""
    out = []
    for p in points:
        best = None
        for a, b, sid in segs:
            u = _unit(a, b)
            if abs(u[0] * axis[0] + u[1] * axis[1]) > TREAD_PERP:
                continue
            d = LineString([a, b]).distance(Point(p))
            if d <= TREAD_REACH_M and (best is None or d < best[0]):
                best = (d, a, b, sid)
        if best is not None:
            out.append(best[1:])
    return out


def _near_segs(pts: list, strokes: list) -> list:
    """The straight segments (0.3 m to a wide arm's width long, arcs left out) of ``strokes`` near the numbers."""
    segs = []
    for st in strokes or []:
        if getattr(st, "arc", None):
            continue
        p = [tuple(q) for q in getattr(st, "pts", []) or []]
        for a, b in zip(p[:-1], p[1:]):
            if 0.3 <= math.dist(a, b) <= WIDTH_M[1] + 0.3:
                segs.append((a, b, st.id))
    near = MultiPoint(pts).convex_hull.buffer(WIDTH_M[1])
    return [s for s in segs if near.intersects(LineString([s[0], s[1]]))]


def stair_of(chain: list, strokes: list) -> Optional[dict]:
    """The stair one chain of numbers describes (the module docstring): ``{"flights", "landing", "winders",
    "turn_winders", "turn", "direction", "polygon", "steps", "entities", "reason"}`` (page metres; the flights in
    climbing order, each rising from its start to its end; ``turn_winders`` the winders in each turn) or ``{"skip":
    reason}`` (pure). 6 Nov 2026: numbers on a circle (a curved stair) give a curved stair (``curved_stair_of``) where
    the straight arms give none."""
    out = _straight_stair_of(chain, strokes)
    if out is None or out.get("skip"):
        curved = curved_stair_of(chain, strokes)
        if curved is not None and not curved.get("skip"):
            return curved
        # 6 Nov 2026 (real13 L-1, "numbered treads always give a stair"): a stair of more arms, each straight run of
        # numbers a flight (``_runs``), when the runs hold at least half the numbers
        pts = [c[1] for c in chain]
        runs = _runs(pts, _near_segs(pts, strokes))
        if len(runs) >= 2 and sum(len(r) for r in runs) >= RUNS_SHARE * len(pts):
            multi = _straight_stair_of(chain, strokes, arms=runs)
            if multi is not None and not multi.get("skip"):
                return multi
        if curved is not None and out is not None:
            out = dict(out, skip=f"{out['skip']}; not a curved stair either ({curved['skip']})")
    return out


RUNS_SHARE = 0.5                # 6 Nov 2026: the straight runs of a stair of many arms hold this share of its numbers


def _runs(points: list, segs: Optional[list] = None) -> list[list[int]]:
    """The straight runs of a chain's numbers in order (pure): each the longest run from its first number whose steps
    stay within ``ARM_TURN_DEG`` of its first step, at least ``ARM_MIN_POINTS`` numbers, its ends trimmed of the
    numbers a different step away (``_trim_arm``, the winders at its turns)."""
    out, i, n = [], 0, len(points)
    while i < n - 1:
        run = [i, i + 1]
        ref = _unit(points[i], points[i + 1])
        j = i + 2
        while j < n and abs(_angle(ref, _unit(points[j - 1], points[j]))) <= ARM_TURN_DEG:
            run.append(j)
            j += 1
        if len(run) >= ARM_MIN_POINTS:
            run = _trim_arm(points, _trim_arm(points, run, at_end=True, segs=segs), at_end=False, segs=segs)
            out.append(run)
            i = run[-1] + 1
        else:
            i += 1
    return out


def _straight_stair_of(chain: list, strokes: list, arms: Optional[list] = None) -> Optional[dict]:
    pts = [c[1] for c in chain]
    values = [c[0] for c in chain]
    segs = _near_segs(pts, strokes)
    arms = _arms(pts, segs) if arms is None else arms
    if not arms or (len(arms) == 1 and len(arms[0]) < len(pts)):
        return {"skip": f"no two straight arms of {ARM_MIN_POINTS} numbers at the ends of {values[0]}-{values[-1]}"}
    # 3 Nov 2026 (real10's core: the arms read from the numbers lay 2-8 degrees askew, the box tilted and the winders
    # around the eye fell outside it): the arms follow the drawing's main directions (within SNAP_DEG) and the footprint
    # is a rectangle in that frame holding the arms and every number of the turn
    main = _main_angle(segs) if segs else math.degrees(math.atan2(*reversed(_unit(pts[arms[0][0]], pts[arms[0][-1]]))))
    flights, shapes, ids = [], [], set()
    arm_axes = []
    # 12 Nov 2026 (review B S8: the treads the numbers count reached no built stair): an arm holds a line for every
    # number from its first to its last, a number the chain bridged included; the numbers before the first arm and
    # after the last are their flights' first and last treads; those between two arms are that turn's winders
    # (two or more numbers past an end arm that turn away from it are a short last or first flight of their own)
    tail = list(range(arms[-1][-1] + 1, len(pts)))
    if len(tail) >= 2 and not _along(pts, arms[-1], tail[-1]):
        arms = arms + [tail]
    head = list(range(0, arms[0][0]))
    if len(head) >= 2 and not _along(pts, arms[0], head[0]):
        arms = [head] + arms
    lead, trail = values[arms[0][0]] - values[0], values[-1] - values[arms[-1][-1]]
    turn_winders = [values[b[0]] - values[a[-1]] - 1 for a, b in zip(arms, arms[1:])]
    for ai, arm in enumerate(arms):
        apts = [pts[i] for i in arm]
        axis = _snap(_unit(apts[0], apts[-1]), main)
        normal = (-axis[1], axis[0])
        treads = _treads(apts, axis, segs)
        widths = sorted(math.dist(a, b) for a, b, _ in treads)
        width = widths[len(widths) // 2] if widths else WIDTH_DEFAULT_M
        width = min(max(width, WIDTH_M[0]), WIDTH_M[1])
        if treads:                                             # the arm's centre line: the tread lines' middles
            offs = sorted(((a[0] + b[0]) / 2.0 - p[0]) * normal[0] + ((a[1] + b[1]) / 2.0 - p[1]) * normal[1]
                          for (a, b, _), p in zip(treads, apts))
            off = offs[len(offs) // 2]
        else:
            off = 0.0
        cx = sum(q[0] for q in apts) / len(apts) + normal[0] * off
        cy = sum(q[1] for q in apts) / len(apts) + normal[1] * off
        proj = [(q[0] - cx) * axis[0] + (q[1] - cy) * axis[1] for q in apts]
        s = (cx + axis[0] * proj[0], cy + axis[1] * proj[0])
        e = (cx + axis[0] * proj[-1], cy + axis[1] * proj[-1])
        n_lines = values[arm[-1]] - values[arm[0]] + 1
        going = math.dist(s, e) / max(n_lines - 1, 1)
        if ai == 0 and lead:
            s = (s[0] - axis[0] * going * lead, s[1] - axis[1] * going * lead)
            n_lines += lead
        if ai == len(arms) - 1 and trail:
            e = (e[0] + axis[0] * going * trail, e[1] + axis[1] * going * trail)
            n_lines += trail
        ids |= {sid for _, _, sid in treads}
        flights.append({"start": [round(s[0], 4), round(s[1], 4)], "end": [round(e[0], 4), round(e[1], 4)],
                        "width": round(width, 4), "lines": n_lines, "spacing": round(going, 4)})
        half = going / 2.0
        s0 = (s[0] - axis[0] * half, s[1] - axis[1] * half)
        e0 = (e[0] + axis[0] * half, e[1] + axis[1] * half)
        shapes.append(LineString([s0, e0]).buffer(width / 2.0, cap_style=2))
        arm_axes.append(axis)
    in_arms = {i for arm in arms for i in arm}
    turn_pts = [pts[i] for i in range(len(pts)) if i not in in_arms]
    landing = None
    winders = 0
    turn = "straight"
    # the footprint: the arms and the turn's tread lines (the winders run from the eye to the stair's outer edge; without
    # them, each turn number grown by half the widest arm), as a rectangle in the main frame
    wmax = max(f["width"] for f in flights)
    theta = math.radians(main)
    ct, st_ = math.cos(theta), math.sin(theta)
    to_f = lambda q: (q[0] * ct + q[1] * st_, -q[0] * st_ + q[1] * ct)
    from_f = lambda q: (q[0] * ct - q[1] * st_, q[0] * st_ + q[1] * ct)
    cloud = [c for sh in shapes for c in sh.exterior.coords]
    for q in [pts[i] for i in range(len(pts)) if i not in {k for arm in arms for k in arm}]:
        lines = [sg for sg in segs if LineString([sg[0], sg[1]]).distance(Point(q)) <= TREAD_REACH_M
                 and math.dist(sg[0], sg[1]) <= wmax * 1.6]
        if lines:
            cloud += [c for sg in lines for c in (sg[0], sg[1])]
            ids |= {sg[2] for sg in lines}
        else:
            cloud += [(q[0] + dx, q[1] + dy) for dx, dy in ((wmax / 2, 0), (-wmax / 2, 0), (0, wmax / 2),
                                                            (0, -wmax / 2))]
    fx = [to_f(q) for q in cloud]
    bx = (min(q[0] for q in fx), min(q[1] for q in fx), max(q[0] for q in fx), max(q[1] for q in fx))
    poly = Polygon([from_f(q) for q in ((bx[0], bx[1]), (bx[2], bx[1]), (bx[2], bx[3]), (bx[0], bx[3]))])
    if len(arms) == 2:
        a1, a2 = arm_axes
        ang = abs(_angle(a1, a2))
        turn = "U" if ang >= 150.0 else ("L" if 60.0 <= ang <= 120.0 else "other")
        if turn == "other":
            return {"skip": f"two arms {ang:.0f} degrees apart in the numbers {values[0]}-{values[-1]}"}
        if turn == "U":
            # a U stair's turn is the band beyond the arms' far ends, across the whole stair (the eye between the arms
            # is no landing)
            top = max(max(x * a1[0] + y * a1[1] for x, y in sh.exterior.coords) for sh in shapes)
            n1 = (-a1[1], a1[0])
            corners = list(poly.exterior.coords)[:4]
            far = max(x * a1[0] + y * a1[1] for x, y in corners)
            lo = min(x * n1[0] + y * n1[1] for x, y in corners)
            hi = max(x * n1[0] + y * n1[1] for x, y in corners)
            if far - top >= 0.2:
                land = Polygon([(a1[0] * u + n1[0] * v, a1[1] * u + n1[1] * v)
                                for u, v in ((top, lo), (far, lo), (far, hi), (top, hi))])
                landing = {"polygon": [[round(x, 4), round(y, 4)] for x, y in list(land.exterior.coords)[:-1]],
                           "depth": round(far - top, 4)}
        else:
            landing = _junction(flights, shapes, arm_axes)
        winders = sum(turn_winders)
    elif len(arms) > 2:
        # 6 Nov 2026 (real13 L-1: a stair of four arms round a well, 1-18): every straight run a flight, the numbers
        # between them winders, the turn "other"
        turn = "other"
        winders = sum(turn_winders)
    first = flights[0]
    d = _unit(first["start"], first["end"])
    reason = (f"the treads are numbered {values[0]}-{values[-1]} ({len(values)} numbers): "
              f"{len(arms)} straight arm(s) of {', '.join(str(f['lines']) for f in flights)} treads"
              + (f", a {turn} turn with {winders} winder(s)" if len(arms) == 2 else "")
              + (f", {len(arms) - 1} turns with {winders} winder(s)" if len(arms) > 2 else "")
              + f"; it rises from {values[0]} to {values[-1]} (drawn)")
    return {"flights": flights, "landing": landing, "winders": winders, "turn_winders": turn_winders, "turn": turn,
            "direction": [round(d[0], 4), round(d[1], 4)], "polygon": poly, "steps": values[-1],
            "entities": sorted({str(c[2].id) for c in chain}) + sorted(ids), "reason": reason}


def _along(points: list, arm: list[int], k: int) -> bool:
    """Number ``k`` lies on the line of ``arm`` (from the arm's nearer end, within ``ARM_TURN_DEG`` of its axis)."""
    axis = _unit(points[arm[0]], points[arm[-1]])
    if k > arm[-1]:
        return abs(_angle(axis, _unit(points[arm[-1]], points[k]))) <= ARM_TURN_DEG
    return abs(_angle(axis, _unit(points[k], points[arm[0]]))) <= ARM_TURN_DEG


def _junction(flights: list, shapes: list, axes: list) -> Optional[dict]:
    """12 Nov 2026 (review B S4: the largest leftover of the footprint, a strip along the long flight, was taken for the
    landing): an L stair's landing is the square where its two arms' bands meet, beyond the first arm's last line and
    before the second's first (the arms' own treads cut out), when both arms reach it (within the wider arm's width);
    else None (pure)."""
    (f1, f2), (a1, a2) = flights, axes
    n1 = (-a1[1], a1[0])
    w = max(f1["width"], f2["width"])
    v1 = f1["start"][0] * n1[0] + f1["start"][1] * n1[1]
    u2 = f2["start"][0] * a1[0] + f2["start"][1] * a1[1]
    u0, u1 = u2 - f2["width"] / 2.0, u2 + f2["width"] / 2.0
    v0, v1_ = v1 - f1["width"] / 2.0, v1 + f1["width"] / 2.0
    sq = Polygon([(a1[0] * u + n1[0] * v, a1[1] * u + n1[1] * v) for u, v in ((u0, v0), (u1, v0), (u1, v1_), (u0, v1_))])
    if sq.distance(Point(f1["end"])) > w or sq.distance(Point(f2["start"])) > w:
        return None
    rest = sq.difference(unary_union(shapes).buffer(0.01))
    if rest.is_empty:
        return None
    part = max(getattr(rest, "geoms", [rest]), key=lambda g: g.area)
    land = part.minimum_rotated_rectangle
    if land.area < 0.2:
        return None
    lc = list(land.exterior.coords)
    return {"polygon": [[round(x, 4), round(y, 4)] for x, y in lc[:-1]],
            "depth": round(min(math.dist(lc[0], lc[1]), math.dist(lc[1], lc[2])), 4)}


# 6 Nov 2026 (synthetic-22, real07's curved stair, user: "Stairs are missing in the project"): numbers on a circle
CURVE_FIT_M = 0.08              # the numbers lie on their fitted circle within this (RMS) ...
CURVE_FIT_REL = 0.08            # ... or within this share of its radius
CURVE_RADIUS_M = (0.3, 6.0)     # the walking line's radius
CURVE_STEP_DEG = (2.0, 45.0)    # one tread turns this far about the centre ...
CURVE_STEP_SPREAD = 0.35        # ... every step within this share of the median step (per number)
CURVE_SWEEP_MIN_DEG = 40.0      # a curved stair turns at least this far (less is a straight arm)
CURVE_RADIAL_DEG = 15.0         # a tread line of a curved stair runs within this of the radius through it
CURVE_FLIGHT_DEG = 30.0         # the curve is written as chord flights of at most this sweep (12 Nov 2026, review B S2:
                                # back from 90; RC14 counts a curved stair as one flight)


def _circle(pts: list) -> Optional[tuple[tuple[float, float], float, float]]:
    """``(centre, radius, rms)`` of the least-squares circle through ``pts`` (Kasa), or None (pure)."""
    n = len(pts)
    if n < 3:
        return None
    mx = sum(p[0] for p in pts) / n
    my = sum(p[1] for p in pts) / n
    suu = svv = suv = suuu = svvv = suvv = svuu = 0.0
    for x, y in pts:
        u, v = x - mx, y - my
        suu += u * u
        svv += v * v
        suv += u * v
        suuu += u * u * u
        svvv += v * v * v
        suvv += u * v * v
        svuu += v * u * u
    det = suu * svv - suv * suv
    if abs(det) < 1e-12:
        return None
    b1 = 0.5 * (suuu + suvv)
    b2 = 0.5 * (svvv + svuu)
    uc = (b1 * svv - b2 * suv) / det
    vc = (suu * b2 - suv * b1) / det
    c = (mx + uc, my + vc)
    r = math.sqrt(uc * uc + vc * vc + (suu + svv) / n)
    rms = math.sqrt(sum((math.dist(p, c) - r) ** 2 for p in pts) / n)
    return c, r, rms


def curved_stair_of(chain: list, strokes: list) -> Optional[dict]:
    """The curved stair a chain of numbers describes (6 Nov 2026): the numbers lie on one circle (``CURVE_FIT_M``),
    each the next a like turn about its centre in one sense (``CURVE_STEP_DEG``, ``CURVE_STEP_SPREAD``), the whole
    turning >= ``CURVE_SWEEP_MIN_DEG``. The tread lines are the radial lines by the numbers (their inner and outer
    ends give the stair's two radii; without them the walking line +- half the default width). The footprint is the
    smallest rectangle round the annular sector (in the drawing's directions or along the chord); the curve is written
    as chord ``flights`` of <= ``CURVE_FLIGHT_DEG`` each (turn ``curved``) and as ``curved`` (centre, radii, start
    and sweep). ``{"skip": reason}`` when the numbers are not on a circle (pure)."""
    pts = [c[1] for c in chain]
    values = [c[0] for c in chain]
    fit = _circle(pts)
    if fit is None:
        return {"skip": "the numbers fit no circle"}
    centre, rm, rms = fit
    if not CURVE_RADIUS_M[0] <= rm <= CURVE_RADIUS_M[1]:
        return {"skip": f"the numbers' circle has a radius of {rm:.2f} m"}
    if rms > max(CURVE_FIT_M, CURVE_FIT_REL * rm):
        return {"skip": f"the numbers lie {rms:.2f} m off their circle"}
    ang = [math.degrees(math.atan2(p[1] - centre[1], p[0] - centre[0])) for p in pts]
    steps = []
    for k in range(1, len(ang)):
        d = (ang[k] - ang[k - 1] + 180.0) % 360.0 - 180.0
        dv = max(1, values[k] - values[k - 1])
        steps.append(d / dv)
    if not steps or not (all(s > 0 for s in steps) or all(s < 0 for s in steps)):
        return {"skip": "the numbers do not turn one way about their circle"}
    med = sorted(abs(s) for s in steps)[len(steps) // 2]
    if not CURVE_STEP_DEG[0] <= med <= CURVE_STEP_DEG[1] or \
            any(abs(abs(s) - med) > CURVE_STEP_SPREAD * med for s in steps):
        return {"skip": f"the numbers turn unevenly about their circle (median {med:.1f} degrees a tread)"}
    sense = 1.0 if steps[0] > 0 else -1.0
    sweep = sense * sum(s * max(1, values[k + 1] - values[k]) for k, s in enumerate(steps))
    if sweep < CURVE_SWEEP_MIN_DEG:
        return {"skip": f"the numbers turn only {sweep:.0f} degrees"}
    # the tread lines: straight segments near a number running within CURVE_RADIAL_DEG of its radius
    segs = _near_segs(pts, strokes)
    inner, outer, ids = [], [], set()
    for p in pts:
        radial = _unit(centre, p)
        best = None
        for a, b, sid in segs:
            u = _unit(a, b)
            if abs(u[0] * radial[0] + u[1] * radial[1]) < math.cos(math.radians(CURVE_RADIAL_DEG)):
                continue
            # the line's own radius through it, not only through the number
            mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
            own = _unit(centre, mid)
            if abs(u[0] * own[0] + u[1] * own[1]) < math.cos(math.radians(CURVE_RADIAL_DEG)):
                continue
            d = LineString([a, b]).distance(Point(p))
            if d <= TREAD_REACH_M and (best is None or d < best[0]):
                best = (d, a, b, sid)
        if best is not None:
            _, a, b, sid = best
            ra, rb = math.dist(a, centre), math.dist(b, centre)
            inner.append(min(ra, rb))
            outer.append(max(ra, rb))
            ids.add(sid)
    if len(inner) >= max(2, len(pts) // 3):
        r_in = sorted(inner)[len(inner) // 2]
        r_out = sorted(outer)[len(outer) // 2]
    else:
        r_in, r_out = rm - WIDTH_DEFAULT_M / 2.0, rm + WIDTH_DEFAULT_M / 2.0
    r_in = max(0.0, r_in)
    if not WIDTH_M[0] <= r_out - r_in <= WIDTH_M[1] + 0.5 or not r_in < rm < r_out:
        r_in, r_out = max(0.0, rm - WIDTH_DEFAULT_M / 2.0), rm + WIDTH_DEFAULT_M / 2.0
    a_start = ang[0] - sense * med / 2.0
    total = sweep + med
    # the annular sector (the stair's own shape) and the smallest rectangle round it
    n_arc = max(2, int(math.ceil(abs(total) / 5.0)))
    arc_a = [a_start + sense * total * k / n_arc for k in range(n_arc + 1)]
    ring = [(centre[0] + r_out * math.cos(math.radians(a)), centre[1] + r_out * math.sin(math.radians(a)))
            for a in arc_a]
    ring += [(centre[0] + r_in * math.cos(math.radians(a)), centre[1] + r_in * math.sin(math.radians(a)))
             for a in reversed(arc_a)]
    sector = Polygon(ring) if r_in > 0 else Polygon(ring[:len(arc_a)] + [centre])
    others = [s for s in segs if s[2] not in ids]
    chord = _unit(ring[0], ring[len(arc_a) - 1])
    cands = [_main_angle(others) if others else 0.0, 0.0, math.degrees(math.atan2(chord[1], chord[0])) % 90.0]
    best = None
    for theta_deg in cands:
        theta = math.radians(theta_deg)
        ct, st_ = math.cos(theta), math.sin(theta)
        fx = [(q[0] * ct + q[1] * st_, -q[0] * st_ + q[1] * ct) for q in ring]
        bx = (min(q[0] for q in fx), min(q[1] for q in fx), max(q[0] for q in fx), max(q[1] for q in fx))
        area = (bx[2] - bx[0]) * (bx[3] - bx[1])
        if best is None or area < best[0] - 1e-6:
            corners = [(u * ct - v * st_, u * st_ + v * ct) for u, v in ((bx[0], bx[1]), (bx[2], bx[1]),
                                                                        (bx[2], bx[3]), (bx[0], bx[3]))]
            best = (area, Polygon(corners))
    poly = best[1]
    # chord flights along the walking line, each <= CURVE_FLIGHT_DEG and of 2 lines at least (12 Nov 2026, review B
    # S1/S2): a line (a riser) at the front of every tread, the flights one after the other in climbing order, the
    # tread between one flight's last line and the next one's first being their turn (``parametric.turn_treads``)
    rw = (r_in + r_out) / 2.0
    treads = values[-1] - values[0] + 1
    n_fl = max(1, min(int(math.ceil(abs(total) / CURVE_FLIGHT_DEG - 0.05)), treads // 2))
    cuts = [int(round(treads * k / n_fl)) for k in range(n_fl + 1)]
    flights = []

    def at(t):
        a = math.radians(a_start + sense * total * t / treads)
        return (centre[0] + rw * math.cos(a), centre[1] + rw * math.sin(a))
    for k in range(n_fl):
        s, e = at(cuts[k]), at(cuts[k + 1] - 1)
        lines = cuts[k + 1] - cuts[k]
        flights.append({"start": [round(s[0], 4), round(s[1], 4)], "end": [round(e[0], 4), round(e[1], 4)],
                        "width": round(r_out - r_in, 4), "lines": lines,
                        "spacing": round(math.dist(s, e) / max(lines - 1, 1), 4)})
    a0r = math.radians(ang[0])
    tangent = (-math.sin(a0r) * sense, math.cos(a0r) * sense)
    reason = (f"the treads are numbered {values[0]}-{values[-1]} ({len(values)} numbers) on a circle: a curved stair "
              f"turning {sweep + med:.0f} degrees, radii {r_in:.2f}-{r_out:.2f} m, {med:.1f} degrees a tread "
              f"({len(ids)} radial tread lines found); it rises from {values[0]} to "
              f"{values[-1]} (drawn)")
    return {"flights": flights, "landing": None, "winders": 0, "turn_winders": [0] * (len(flights) - 1),
            "turn": "curved",
            "direction": [round(tangent[0], 4), round(tangent[1], 4)], "polygon": poly, "shape": sector,
            "steps": values[-1],
            "curved": {"centre": [round(centre[0], 4), round(centre[1], 4)], "radius_inner": round(r_in, 4),
                       "radius_outer": round(r_out, 4), "start_deg": round(a_start % 360.0, 3),
                       "sweep_deg": round(sense * total, 3)},
            "entities": sorted({str(c[2].id) for c in chain}) + sorted(ids), "reason": reason}


SNAP_DEG = 15.0                 # an arm within this of the drawing's main directions follows them


def _main_angle(segs: list) -> float:
    """The main direction of the stair's lines (degrees modulo 90): the length-weighted mode in 2 degree bins."""
    bins: dict = {}
    for a, b, _sid in segs:
        L = math.dist(a, b)
        k = int(round((math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 90.0) / 2.0)) % 45
        bins[k] = bins.get(k, 0.0) + L
    return 2.0 * max(bins, key=bins.get) if bins else 0.0


def _snap(u, main: float) -> tuple[float, float]:
    """``u`` turned onto the nearest of the main directions when within ``SNAP_DEG``."""
    ang = math.degrees(math.atan2(u[1], u[0]))
    best = min((main + 90.0 * k for k in range(-4, 5)), key=lambda c: abs((ang - c + 180.0) % 360.0 - 180.0))
    if abs((ang - best + 180.0) % 360.0 - 180.0) <= SNAP_DEG:
        r = math.radians(best)
        return math.cos(r), math.sin(r)
    return u


def _footprint(poly: Polygon, axis) -> tuple[tuple[float, float], tuple[float, float], float]:
    """``(centre, (width, depth), rotation_deg)`` of a rotated rectangle, its local +Y along ``axis``."""
    c = list(poly.exterior.coords)[:4]
    e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1])
    e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    l1, l2 = math.hypot(*e1), math.hypot(*e2)
    along = e1 if abs(e1[0] * axis[0] + e1[1] * axis[1]) / (l1 or 1) >= \
        abs(e2[0] * axis[0] + e2[1] * axis[1]) / (l2 or 1) else e2
    depth = l1 if along is e1 else l2
    width = l2 if along is e1 else l1
    ang = math.degrees(math.atan2(along[1], along[0])) - 90.0
    ang = (ang + 180.0) % 360.0 - 180.0
    cen = poly.centroid
    return (round(cen.x, 4), round(cen.y, 4)), (round(width, 4), round(depth, 4)), round(ang, 3)


def apply(pieces: list, cands: list, texts: list, strokes: list, units_to_m: float, file_rel: str, page_no: int,
          notes: list) -> tuple[list, list, list]:
    """``(pieces, cands, polygons)`` with the numbered stairs (``stair_of``) no stair piece holds added as stair
    pieces, the candidates and non-stair pieces whose centre stands inside one of them dropped (its parts), and the new
    stairs' footprints (page metres). 6 Nov 2026 (synthetic-15, UL286: the winders read as a flat landing): a stair
    piece that holds a chain keeps its footprint and flights, and takes what the numbers say (``enrich``): the treads
    drawn, the winders in the turn, the rise direction and the turn."""
    from wenart.ingest.model import FurnitureItem

    found = chains(texts)
    if not found:
        return pieces, cands, []
    pieces, cands = list(pieces), list(cands)
    polys: list = []
    for chain in found:
        pts = [Point(c[1]) for c in chain]
        holder = None
        for p in pieces:
            if p.type != "stair":
                continue
            fp = _piece_poly(p)
            if fp is not None and sum(1 for q in pts if fp.buffer(0.1).contains(q)) >= INSIDE_SHARE * len(pts):
                holder = p
                break
        values = f"{chain[0][0]}-{chain[-1][0]}"
        st = stair_of(chain, strokes)
        if holder is not None:
            said = enrich(holder, chain, st)
            notes.append(f"numbered stair {values}: a stair piece already holds its numbers (the stair rule's "
                         f"footprint kept)" + (f"; from the numbers: {said}" if said else ""))
            continue
        if st is None or st.get("skip"):
            notes.append(f"numbered stair {values}: {st.get('skip') if st else 'not read'}")
            continue
        centre, size, rot = _footprint(st["polygon"], st["direction"])
        inside = st["polygon"].buffer(-0.05)
        dropped = [c for c in cands if inside.contains(Point(c["footprint"]["center"]))]
        cands = [c for c in cands if c not in dropped]
        parts = [p for p in pieces if p.type != "stair" and inside.contains(Point(p.center))]
        pieces = [p for p in pieces if p not in parts]
        xs = [x for x, _ in st["polygon"].exterior.coords]
        ys = [y for _, y in st["polygon"].exterior.coords]
        box = [round(v / units_to_m, 3) for v in (min(xs), min(ys), max(xs), max(ys))] if units_to_m else \
            [min(xs), min(ys), max(xs), max(ys)]
        ev = B.evidence(file_rel, "vector", 0.85, page=page_no, entity=",".join(st["entities"][:40]) or None)
        ev["note"] = f"numbered treads: {st['reason']}"
        ev["rule"] = "numbered_treads"
        details = {"stair": {"flights": st["flights"], "landing": st["landing"], "direction": st["direction"],
                             "direction_assumed": False, "turn": "U" if st["turn"] == "U" else
                             ("straight" if st["turn"] == "straight" else "other"),
                             "turn_assumed": False, "void_assumed": True, "riser_m": None, "riser_source": None,
                             "reason": st["reason"], "steps_drawn": st["steps"],
                             # 12 Nov 2026 (review B S1): built in this order, each turn with its winders
                             "flights_ordered": True, "turn_winders": list(st.get("turn_winders") or [])}}
        if st["winders"]:
            details["stair"]["winders"] = st["winders"]
        if st.get("curved"):
            details["stair"]["curved"] = st["curved"]
        if st["landing"] is None and len(st["flights"]) >= 2 and not st.get("curved"):
            details["stair"]["landing_assumed"] = True
        pieces.append(FurnitureItem(type="stair", type_raw=None, center=centre, size=size, rotation_deg=rot,
                                    front_deg=None, box=box, entity=st["entities"][0], evidence=ev,
                                    status="verified", type_method="rule", details=details))
        polys.append(st["polygon"])
        notes.append(f"numbered stair {values}: {st['reason']}; footprint {size[0]:.2f} x {size[1]:.2f} m"
                     + (f"; {len(dropped) + len(parts)} candidate(s) inside it are its parts" if dropped or parts
                        else ""))
    return pieces, cands, polys


def enrich(piece, chain: list, st: Optional[dict]) -> str:
    """What a chain of tread numbers says about the stair piece that holds it (6 Nov 2026), written into the piece's
    ``details["stair"]`` in place; the footprint and the flights' places stay the stair rule's. The numbers are drawn
    evidence, the stair rule's guesses (``direction_assumed``, ``turn_assumed``) are not: ``steps_drawn`` (the last
    number), the ``winders`` (the numbers in the turn, where the rule read a flat landing), the rise ``direction`` and
    the flights' order (the flight by number 1 first, each running up the numbers), the ``turn`` (U or L) and a curved
    stair's ``curved``. Returns the note (empty when nothing changed)."""
    data = (piece.details or {}).get("stair")
    if data is None:
        return ""
    said = []
    values = [c[0] for c in chain]
    if st is None or st.get("skip"):
        return "; ".join(said)
    # the turn and the winders only where the stair rule read the same flights as the numbers' arms (real09: the rule
    # read one straight flight of a U stair numbered 1-17; a U turn on one flight would be no stair the build knows)
    same = len(data.get("flights") or []) == len(st.get("flights") or [])
    if not same:
        # 12 Nov 2026 (review B S8): the treads the numbers count are written only where they reach the built stair
        said.append(f"the numbers make {len(st.get('flights') or [])} flight(s) ({st.get('turn')}) of "
                    f"{values[-1]} treads, the stair rule {len(data.get('flights') or [])}: the rule's flights kept "
                    f"as drawn")
    if same and st.get("winders") and not data.get("winders"):
        data["winders"] = int(st["winders"])
        said.append(f"{st['winders']} winder(s) in the turn")
    if not same:
        pass
    elif st.get("curved") and not data.get("curved"):
        data["curved"] = st["curved"]
        data["turn"], data["turn_assumed"] = "other", False
        said.append("a curved stair")
    elif st.get("turn") in ("U", "L") and data.get("turn_assumed", True):
        data["turn"] = "U" if st["turn"] == "U" else "other"
        data["turn_assumed"] = False
        said.append(f"a {st['turn']} turn")
    flights = data.get("flights") or []
    if flights and data.get("direction_assumed", True):
        nums = [c[1] for c in chain]

        # 12 Nov 2026 (review B S9: a flight within one width took the other arm's number 1 and turned round): every
        # number goes to its nearest flight only
        lines_of = [LineString([fl["start"], fl["end"]]) for fl in flights]
        mine: dict = {}
        for v, q in zip(values, nums):
            ds = [ln.distance(Point(q)) for ln in lines_of]
            k = min(range(len(ds)), key=ds.__getitem__)
            if ds[k] <= max(0.6, flights[k].get("width", 1.0)):
                mine.setdefault(k, []).append((v, q))

        def low(k, fl) -> tuple[float, float]:
            # the lowest number standing by the flight's line, and its distance along it from the start
            s, e = fl["start"], fl["end"]
            if not mine.get(k):
                return (float("inf"), 0.0)
            v, q = min(mine[k])
            return (v, math.dist(q, s) - math.dist(q, e))

        rows = []
        for k, fl in enumerate(flights):
            v, lead = low(k, fl)
            if lead > 0:                                          # number 1's end is the flight's end: turn it round
                fl["start"], fl["end"] = fl["end"], fl["start"]
            rows.append((v, fl))
        if all(v != float("inf") for v, _ in rows):
            data["flights"] = [fl for _, fl in sorted(rows, key=lambda r: r[0])]
            d = _unit(data["flights"][0]["start"], data["flights"][0]["end"])
            data["direction"] = [round(d[0], 4), round(d[1], 4)]
            data["direction_assumed"] = False
            data["direction_source"] = "numbered treads"
            said.append(f"it rises from {values[0]} to {values[-1]}")
            if same:
                # 12 Nov 2026 (review B S1/S8): the flights climbed in this order with the numbers' treads and winders
                data["flights_ordered"] = True
                if len(st.get("turn_winders") or []) == len(data["flights"]) - 1:
                    data["turn_winders"] = list(st["turn_winders"])
                for fl, sf in zip(data["flights"], st["flights"]):
                    if int(fl.get("lines") or 0) != int(sf["lines"]):
                        fl["lines"] = int(sf["lines"])
                if data.get("steps_drawn") != values[-1]:
                    data["steps_drawn"] = values[-1]
                    said.append(f"{values[-1]} treads drawn")
    if said:
        data["reason"] = (str(data.get("reason") or "") + f"; numbered treads {values[0]}-{values[-1]}: "
                          + ", ".join(said)).lstrip("; ")
        ev = piece.evidence if isinstance(piece.evidence, dict) else None
        if ev is not None:
            ev["note"] = (str(ev.get("note") or "") + f"; numbered treads {values[0]}-{values[-1]}").lstrip("; ")
    return "; ".join(said)


def _piece_poly(p) -> Optional[Polygon]:
    try:
        cx, cy = p.center
        w, d = p.size
        a = math.radians(float(p.rotation_deg or 0.0))
    except (TypeError, ValueError):
        return None
    ca, sa = math.cos(a), math.sin(a)
    return Polygon([(cx + ca * u - sa * v, cy + sa * u + ca * v)
                    for u, v in ((-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2))])
