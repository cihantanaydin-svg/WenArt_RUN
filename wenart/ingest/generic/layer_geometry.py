"""A layer's role from what it draws, where the layer names say nothing (22 Nov 2026, S5; the user's pick "build S5,
S3, S4, S6").

What: ``names_say_nothing(strokes, texts)`` is True for a document whose layer names give a role
(``layer_names.name_role``) to less than ``NAMED_SHARE_MIN`` of its drawing (layers renamed L1, L2 ..., numbered or
pen-width layers); ``infer_roles(strokes, texts)`` then gives each layer (not ``0`` and ``Defpoints``, whose meaning
CAD fixes) the role its geometry and its blocks show, ``{layer: role}`` with ``evidence(...)`` saying why:

- the names of the blocks drawn on it (a door or window block keeps its name when the layers are renamed);
- ``dimension`` / ``axis`` / ``text``: texts make a fair share of the layer; mostly numbers (dimension values) or grid
  labels ('A', '12') in their bubbles, else words; a centre or dash-dot linetype on most strokes is an axis;
- ``door``: door swings (a quarter arc whose leaf runs from the arc's centre to one of its ends, as long as the radius)
  outnumber the window bundles;
- ``window``: bundles of three or more parallel lines of one extent close together across a wall (frame and glass);
- ``stair``: runs of five or more equal parallel lines at an even pitch (treads); ``finish`` when two such families
  cross each other (a tile grid);
- ``structure``: small closed boxes and circles (columns) make most of the layer;
- ``wall``: the layer whose long lines pair at a wall's thickness over the greatest length, and every other layer whose
  long lines pair as well and run along the first one's walls (plaster faces, concrete walls).

Sizes are measured in door radii (``unit_m``: the median radius of the document's door swings is taken as
``DOOR_RADIUS_M``), so a drawing in any unit, or with a wrong ``$INSUNITS``, gives the same answer.

Why: read twice with renamed layers (``reading_check twice``, 22 Nov 2026), real09 lost 290 of 388 walls and 25 rooms
and real10, real17, real19, real20, real21 changed in hundreds of places: the walls the reader joins by their name
(plaster, column layers), the door and window rules keyed on the door and window layers and the stairs the sheets
stage registers storeys by were all lost with the names. The rule (UL338): layer names are no evidence the reading may
depend on; where they say nothing, the geometry says it.

How: pure functions over the generic page's strokes and texts (no shapely); the result goes to the role registry of
``layer_names`` (``set_geometry_roles``), so every rule that asks a layer's role gets it; a document whose names say
something is not touched (its reading does not change).
"""
from __future__ import annotations

import bisect
import math
import re
from collections import defaultdict
from typing import Optional

from wenart import building as B

NAMED_SHARE_MIN = 0.2          # a document whose named layers draw less than this share of its strokes says nothing
KEEP_LAYERS = ("0", "DEFPOINTS")
DOOR_RADIUS_M = 0.85           # the median door swing's radius, the unit of the size tests
SWING_SWEEP_DEG = (70.0, 110.0)
SWING_LEAF = (0.8, 1.2)        # a leaf's length in radii; it starts at the arc's centre ...
SWING_END_TOL = 0.12           # ... within this many radii, and ends at one of the arc's ends
SWING_MIN = 3
BLOCK_SHARE = 0.5              # half of a layer's strokes in blocks whose names give one role: that role
TEXT_MIN = 5
TEXT_SHARE = 0.15              # texts among the layer's items
NUMERIC_SHARE = 0.7
GRID_LABEL_SHARE = 0.6
LINETYPE_SHARE = 0.5
ANGLE_TOL_DEG = 2.0
# in metres (converted with ``unit_m``)
LONG_M = 0.4                   # a wall face's piece is at least this long
LONG2_M = 2.0                  # walls run on: a wall layer draws this share of its length (WALL_LONG_SHARE) in lines this long
WALL_LONG_SHARE = 0.3
PAIR_M = (0.05, 0.60)          # a wall's thickness
BUNDLE_SPACING_M = 0.15        # window lines lie this close to their neighbours ...
BUNDLE_WIDTH_M = 0.45          # ... across a band at most this wide
BUNDLE_LEN_M = (0.3, 4.0)
BUNDLE_MIN = 3
END_SNAP_M = 0.05              # equal extents: both ends within this of the group's first line
TREAD_PITCH_M = (0.18, 0.45)
TREAD_LEN_M = (0.6, 3.0)
TREAD_MIN = 5
TREAD_EVEN = 0.2
COLUMN_SIDE_M = (0.15, 0.9)
COLUMN_CIRCLE_R_M = (0.08, 0.5)
STRUCTURE_SHARE = 0.4
STAIR_SHARE = 0.3
WINDOW_SHARE = 0.3
GRID_CROSS_SHARE = 0.3
WALL_PAIR_SHARE = 0.5          # the long lines that pair at a wall's thickness
WALL_SECOND_PAIR_SHARE = 0.65  # a second wall layer pairs better still (a floor hatch along the walls pairs less)
WALL_LENGTH_SHARE = 0.05       # a second wall layer pairs over this share of the first one's paired length ...
WALL_NEAR_SHARE = 0.5          # ... and this share of its paired length lies within ``WALL_NEAR_M`` of the first's lines
WALL_NEAR_M = 0.6
NUMERIC_RE = re.compile(r"^[+\-±−]?\s*\d+(?:[.,]\d+)?\s*(?:cm|mm|m)?$|^\d+(?:[.,]\d+)?\s*[/xX]\s*\d+(?:[.,]\d+)?$")
GRID_LABEL_RE = re.compile(r"^(?:[A-Z]{1,2}|\d{1,3})['′]?$")


def _key(name) -> str:
    return B.fold_ascii(str(name or "")).upper().strip()


def _kept(name) -> bool:
    return not name or _key(name) in KEEP_LAYERS


def _text_layer(t) -> Optional[str]:
    ev = getattr(t, "evidence", None) or []
    return ev[0].get("layer") if ev and isinstance(ev[0], dict) else None


def names_say_nothing(strokes, texts=()) -> bool:
    """True when the layers whose names give a role (``layer_names.name_role``) hold less than ``NAMED_SHARE_MIN`` of
    the document's strokes and texts outside layer ``0`` (the module docstring)."""
    from wenart.ingest.generic import layer_names as LN

    named = total = 0
    seen: dict = {}
    for layer in [getattr(st, "layer", None) for st in strokes or ()] + [_text_layer(t) for t in texts or ()]:
        if _kept(layer):
            continue
        if layer not in seen:
            seen[layer] = LN.name_role(layer) is not None
        total += 1
        named += seen[layer]
    return total > 0 and named < NAMED_SHARE_MIN * total


# --- the geometry of one layer (pure) -------------------------------------------------------------------------------

def _segments(st) -> list:
    if getattr(st, "arc", None) is not None:
        return []
    pts = [tuple(p) for p in getattr(st, "pts", None) or []]
    if getattr(st, "closed", False) and len(pts) > 2 and pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    return [(a, b) for a, b in zip(pts, pts[1:]) if a != b]


def _sweep(arc: dict) -> float:
    s = (float(arc.get("end_deg", 0.0)) - float(arc.get("start_deg", 0.0))) % 360.0
    return 360.0 if s == 0.0 else s


def _arc_end(arc: dict, deg: float) -> tuple:
    cx, cy = arc["center"]
    r = float(arc["radius"])
    return (cx + r * math.cos(math.radians(deg)), cy + r * math.sin(math.radians(deg)))


def swings(arcs: list, segs: list) -> list:
    """The door swings among ``arcs`` (``[(arc, stroke)]``): a sweep of ``SWING_SWEEP_DEG`` and a straight leaf among
    ``segs`` from the arc's centre to one of its ends, as long as the radius (``SWING_LEAF``). Returns the radii."""
    quarter = [(a, st) for a, st in arcs if SWING_SWEEP_DEG[0] <= _sweep(a) <= SWING_SWEEP_DEG[1]
               and float(a["radius"]) > 0]
    if not quarter or not segs:
        return []
    cell = max(1e-12, SWING_END_TOL * statistics_median([float(a["radius"]) for a, _ in quarter]))
    grid: dict = defaultdict(list)
    for a, b in segs:
        for p in (a, b):
            grid[(int(p[0] // cell), int(p[1] // cell))].append((a, b))
    out = []
    for arc, _st in quarter:
        r = float(arc["radius"])
        c = tuple(arc["center"])
        ends = (_arc_end(arc, float(arc.get("start_deg", 0.0))), _arc_end(arc, float(arc.get("end_deg", 0.0))))
        key = (int(c[0] // cell), int(c[1] // cell))
        k = min(3, int(math.ceil(SWING_END_TOL * r / cell)))
        near = [s for dx in range(-k, k + 1) for dy in range(-k, k + 1) for s in grid.get((key[0] + dx, key[1] + dy), ())]
        for a, b in near:
            for p, q in ((a, b), (b, a)):
                if math.dist(p, c) <= SWING_END_TOL * r and SWING_LEAF[0] * r <= math.dist(p, q) <= SWING_LEAF[1] * r \
                        and min(math.dist(q, e) for e in ends) <= max(SWING_END_TOL, 0.25) * r:
                    out.append(r)
                    break
            else:
                continue
            break
    return out


def statistics_median(xs: list) -> float:
    xs = sorted(xs)
    if not xs:
        return 0.0
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def _families(segs: list, min_len: float) -> list:
    """Straight pieces at least ``min_len`` long grouped by direction (``ANGLE_TOL_DEG``): ``[(u, n, [(off, s0, s1,
    length)])]`` with ``u`` the direction and ``n`` its normal, ``s`` along ``u`` and ``off`` along ``n``."""
    bins: dict = defaultdict(list)
    for a, b in segs:
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length < min_len:
            continue
        ang = math.degrees(math.atan2(dy, dx)) % 180.0
        bins[int(round(ang / ANGLE_TOL_DEG)) % int(180 / ANGLE_TOL_DEG)].append((a, b, length))
    out = []
    for k, items in bins.items():
        ang = math.radians(k * ANGLE_TOL_DEG)
        u = (math.cos(ang), math.sin(ang))
        n = (-u[1], u[0])
        rows = []
        for a, b, length in items:
            sa, sb = a[0] * u[0] + a[1] * u[1], b[0] * u[0] + b[1] * u[1]
            off = 0.5 * ((a[0] + b[0]) * n[0] + (a[1] + b[1]) * n[1])
            rows.append((off, min(sa, sb), max(sa, sb), length))
        rows.sort()
        out.append((u, n, rows))
    return out


def _overlap(r, q) -> float:
    return min(r[2], q[2]) - max(r[1], q[1])


def pair_stats(fams: list, unit: float) -> tuple:
    """``(long, paired, paired_length)``: the long lines, those with a parallel partner at a wall's thickness overlapping
    them by ``LONG_M``, and the paired lines' length (in metres)."""
    lo, hi, long_m = PAIR_M[0] / unit, PAIR_M[1] / unit, LONG_M / unit
    total = paired = 0
    plen = 0.0
    for _u, _n, all_rows in fams:
        rows = [r for r in all_rows if r[3] >= long_m]
        offs = [r[0] for r in rows]
        for i, r in enumerate(rows):
            total += 1
            j0 = bisect.bisect_left(offs, r[0] - hi)
            j1 = bisect.bisect_right(offs, r[0] + hi)
            if any(j != i and lo <= abs(rows[j][0] - r[0]) <= hi and _overlap(r, rows[j]) >= long_m
                   for j in range(j0, min(j1, j0 + 400))):
                paired += 1
                plen += r[3] * unit
    return total, paired, plen


HATCH_RUN = 6                  # a hatch: this many long parallel lines in a row at one even pitch ...
HATCH_PITCH_M = 0.6            # ... of at most this, whatever their extents (a pattern clipped by its boundary)
HATCH_EVEN = 0.1
HATCH_SHARE = 0.5              # ... drawing this share of the layer's long lines


def hatch_lines(fams: list, unit: float) -> int:
    """The layer's long lines (``LONG_M``) that lie in runs of ``HATCH_RUN`` neighbours at one even pitch (each step
    within ``HATCH_EVEN`` of the run's first) of at most ``HATCH_PITCH_M``, each overlapping the next: a hatch or tile
    pattern (a wall's faces pair, they never repeat at one pitch six times)."""
    long_m, pitch_max = LONG_M / unit, HATCH_PITCH_M / unit
    n = 0
    for _u, _n, all_rows in fams:
        rows = _collapse([r for r in all_rows if r[3] >= long_m], SAME_OFFSET_M / unit)
        i = 0
        while i < len(rows) - 1:
            step = rows[i + 1][0] - rows[i][0]
            j = i + 1
            if 1e-12 < step <= pitch_max:
                while j < len(rows) and abs((rows[j][0] - rows[j - 1][0]) - step) <= HATCH_EVEN * step \
                        and _overlap(rows[j], rows[j - 1]) > 0:
                    j += 1
            if j - i >= HATCH_RUN:
                n += j - i
                i = j
            else:
                i += 1
    return n


SAME_OFFSET_M = 0.002          # lines this close across are one line (duplicates, collinear pieces)


def _collapse(rows: list, tol: float) -> list:
    """Rows sorted by offset with those at one offset (within ``tol``) merged into one row spanning them all."""
    out: list = []
    for r in sorted(rows):
        if out and r[0] - out[-1][0] <= tol:
            o = out[-1]
            s0, s1 = min(o[1], r[1]), max(o[2], r[2])
            out[-1] = (o[0], s0, s1, max(o[3], s1 - s0))
        else:
            out.append(r)
    return out


def runs(fams: list, unit: float) -> tuple:
    """``(tread_lines, bundle_lines, bundles, bundle_ends)``: lines in tread runs (``TREAD_MIN`` equal lines at an even
    pitch of ``TREAD_PITCH_M``) and in window bundles (``BUNDLE_MIN`` equal lines within ``BUNDLE_SPACING_M`` of each other,
    the bundle at most ``BUNDLE_WIDTH_M`` wide)."""
    treads = bundle_lines = bundles = 0
    ends: list = []                # each bundle's outer lines' ends, for the jamb test of ``infer_roles``
    q = END_SNAP_M / unit
    for u, n, rows in fams:
        def close(cur):
            ends.append([((u[0] * x[1] + n[0] * x[0], u[1] * x[1] + n[1] * x[0]),
                          (u[0] * x[2] + n[0] * x[0], u[1] * x[2] + n[1] * x[0])) for x in (cur[0], cur[-1])])
        # equal-extent groups: lines whose two ends agree within END_SNAP_M of the group's first line
        groups: list = []
        index: dict = {}
        for r in rows:
            k0, k1 = round(r[1] / q), round(r[2] / q)
            g = next((index[(k0 + a, k1 + b)] for a in (-1, 0, 1) for b in (-1, 0, 1) if (k0 + a, k1 + b) in index
                      and abs(index[(k0 + a, k1 + b)][0][1] - r[1]) <= q
                      and abs(index[(k0 + a, k1 + b)][0][2] - r[2]) <= q), None)
            if g is None:
                g = [r]
                groups.append(g)
                index[(k0, k1)] = g
            else:
                g.append(r)
        for same in groups:
            if len(same) < BUNDLE_MIN:
                continue
            same = _collapse(same, SAME_OFFSET_M / unit)
            if len(same) < BUNDLE_MIN:
                continue
            r = same[0]
            offs = [x[0] for x in same]
            steps = [b - a for a, b in zip(offs, offs[1:])]
            length_m = r[3] * unit
            # a tread run: an even pitch of a tread's going
            if len(same) >= TREAD_MIN and TREAD_LEN_M[0] <= length_m <= TREAD_LEN_M[1]:
                med = statistics_median(steps)
                if TREAD_PITCH_M[0] <= med * unit <= TREAD_PITCH_M[1] \
                        and all(abs(s - med) <= TREAD_EVEN * med for s in steps):
                    treads += len(same)
                    continue
            # a window bundle: close lines across a narrow band
            if BUNDLE_LEN_M[0] <= length_m <= BUNDLE_LEN_M[1]:
                cur = [same[0]]
                for x, s in zip(same[1:], steps):
                    if s * unit <= BUNDLE_SPACING_M and (x[0] - cur[0][0]) * unit <= BUNDLE_WIDTH_M:
                        cur.append(x)
                        continue
                    if len(cur) >= BUNDLE_MIN:
                        bundles += 1
                        bundle_lines += len(cur)
                        close(cur)
                    cur = [x]
                if len(cur) >= BUNDLE_MIN:
                    bundles += 1
                    bundle_lines += len(cur)
                    close(cur)
    return treads, bundle_lines, bundles, ends


def grid_crossings(fams: list, unit: float) -> int:
    """How many lines of a layer's tread-like families cross lines of a family about 90 degrees off (a tile grid)."""
    big = [(u, rows) for u, _n, rows in fams if len(rows) >= TREAD_MIN]
    crossed = 0
    for i, (u1, r1) in enumerate(big):
        for u2, r2 in big[i + 1:]:
            if abs(u1[0] * u2[0] + u1[1] * u2[1]) > 0.1:
                continue
            # a line of family 1 at offset o1 spanning [s0, s1] along u1 crosses family 2's line when o2 lies in it
            offs2 = sorted(r[0] for r in r2)

            for r in r1[:2000]:
                j0, j1 = bisect.bisect_left(offs2, r[1]), bisect.bisect_right(offs2, r[2])
                if j1 - j0 >= 2:
                    crossed += 1
    return crossed


def columns(segs: list, circles: list, unit: float) -> int:
    """Strokes of the layer that draw columns: closed boxes of ``COLUMN_SIDE_M`` (as one polyline or four lines) and
    circles of ``COLUMN_CIRCLE_R_M``; returns the count of their pieces."""
    lo, hi = COLUMN_SIDE_M[0] / unit, COLUMN_SIDE_M[1] / unit
    n = sum(1 for r in circles if COLUMN_CIRCLE_R_M[0] / unit <= r <= COLUMN_CIRCLE_R_M[1] / unit) * 4
    q = max(lo * 0.05, 1e-12)

    def key(p):
        return (round(p[0] / q), round(p[1] / q))
    short = [(a, b) for a, b in segs if lo <= math.dist(a, b) <= hi]
    at: dict = defaultdict(set)
    for a, b in short:
        at[key(a)].add(key(b))
        at[key(b)].add(key(a))
    # a box: four short sides round four corners (a -> b -> c -> d -> a), each side meeting the next one
    in_box = set()
    for a, b in short:
        ka, kb = key(a), key(b)
        for kc in at[kb] - {ka}:
            for kd in at[kc] - {kb, ka}:
                if ka in at[kd]:
                    in_box.update({frozenset((ka, kb)), frozenset((kb, kc)), frozenset((kc, kd)), frozenset((kd, ka))})
                    break
    return n + len(in_box)


# --- the roles (pure) -----------------------------------------------------------------------------------------------

def unit_m(strokes, fallback: Optional[float] = None) -> float:
    """Metres per drawing unit from the document's door swings (their median radius is ``DOOR_RADIUS_M``); 1.0 when
    the drawing has fewer than ``SWING_MIN``: ``fallback`` (the header's unit) or 1.0."""
    arcs, segs = [], []
    for st in strokes or ():
        if _kept(getattr(st, "layer", None)):
            continue
        a = getattr(st, "arc", None)
        if a is not None:
            arcs.append((a, st))
        else:
            segs.extend(_segments(st))
    radii = swings(arcs, segs)
    return DOOR_RADIUS_M / statistics_median(radii) if len(radii) >= SWING_MIN else float(fallback or 1.0)


def layer_features(strokes, texts, unit: float) -> dict:
    """Per layer the counts the roles are chosen from (``infer_roles``)."""
    from wenart.ingest.generic import axes as AX
    from wenart.ingest.generic import layer_names as LN

    by: dict = defaultdict(lambda: {"segs": [], "arcs": [], "circles": [], "strokes": 0, "axis_lt": 0,
                                    "blocks": defaultdict(int), "texts": 0, "numeric": 0, "grid_labels": 0})
    for st in strokes or ():
        layer = getattr(st, "layer", None)
        if _kept(layer):
            continue
        f = by[layer]
        f["strokes"] += 1
        lt = getattr(st, "linetype", None)
        if lt and AX.AXIS_LINETYPE_RE.search(B.fold_ascii(str(lt)).upper()):
            f["axis_lt"] += 1
        blk = getattr(st, "block", None)
        if blk:
            role = next((LN.name_role(n) for n in reversed(str(blk).split("/")) if LN.name_role(n)), None)
            if role:
                f["blocks"][role] += 1
        a = getattr(st, "arc", None)
        if a is not None:
            if _sweep(a) >= 359.0 or getattr(st, "kind", "") == "circle":
                f["circles"].append(float(a["radius"]))
            else:
                f["arcs"].append((a, st))
        else:
            f["segs"].extend(_segments(st))
    for t in texts or ():
        layer = _text_layer(t)
        if _kept(layer):
            continue
        f = by[layer]
        f["texts"] += 1
        s = B.fold_ascii(str(getattr(t, "text", "") or "")).strip().upper()
        f["numeric"] += bool(NUMERIC_RE.match(s))
        f["grid_labels"] += bool(GRID_LABEL_RE.match(s))
    out = {}
    for layer, f in by.items():
        fams = _families(f["segs"], 0.05 / unit)
        long_n, paired, plen = pair_stats(fams, unit)
        total_m = sum(r[3] for _u, _n, rows in fams for r in rows) * unit
        long2_m = sum(r[3] for _u, _n, rows in fams for r in rows if r[3] * unit >= LONG2_M) * unit
        treads, bundle_lines, bundles, bundle_ends = runs(fams, unit)
        out[layer] = {
            "strokes": f["strokes"], "lines": len(f["segs"]), "arcs": len(f["arcs"]), "circles": len(f["circles"]),
            "texts": f["texts"], "numeric": f["numeric"], "grid_labels": f["grid_labels"], "axis_lt": f["axis_lt"],
            "blocks": dict(f["blocks"]), "swings": len(swings(f["arcs"], f["segs"])),
            "long": long_n, "paired": paired, "paired_m": round(plen, 2), "length_m": round(total_m, 2),
            "long2_m": round(long2_m, 2),
            "treads": treads, "bundle_lines": bundle_lines, "bundles": bundles, "_bundle_ends": bundle_ends,
            "grid": grid_crossings(fams, unit) if treads else 0, "hatch": hatch_lines(fams, unit),
            "columns": columns(f["segs"], f["circles"], unit),
            "_fams": fams}
    return out


def _near_share(fams: list, base: list, unit: float) -> float:
    """The share of ``fams``' long lines that lie within ``WALL_NEAR_M`` of a parallel line of ``base``."""
    reach = WALL_NEAR_M / unit
    long_m = LONG_M / unit
    by_dir = {}
    for u, _n, rows in base:                       # rows are sorted by offset (``_families``)
        by_dir[(round(u[0], 3), round(u[1], 3))] = ([r[0] for r in rows], rows)
    total = near = 0
    for u, _n, rows in fams:
        offs, brows = by_dir.get((round(u[0], 3), round(u[1], 3)), ([], []))
        for r in rows:
            if r[3] < long_m:
                continue
            total += 1
            j0, j1 = bisect.bisect_left(offs, r[0] - reach), bisect.bisect_right(offs, r[0] + reach)
            if any(_overlap(r, brows[j]) > 0 for j in range(j0, min(j1, j0 + 400))):
                near += 1
    return near / total if total else 0.0


def decide(f: dict) -> tuple[Optional[str], str]:
    """``(role, why)`` of one layer from its features, before the wall test (``infer_roles``)."""
    n = max(1, f["strokes"])
    if f["blocks"]:
        role, k = max(f["blocks"].items(), key=lambda kv: kv[1])
        if k >= BLOCK_SHARE * n:
            return role, f"{k} of its {n} strokes lie in blocks named for a {role}"
    lines = max(1, f["lines"])
    # a stair's treads first: its numbers 1, 2, 3 ... are no dimension texts
    if f["treads"] >= STAIR_SHARE * lines and f["treads"] >= TREAD_MIN:
        if f["grid"] >= GRID_CROSS_SHARE * f["treads"]:
            return "finish", f"{f['treads']} lines at an even pitch crossing each other ({f['grid']} crossings): a grid"
        return "stair", f"{f['treads']} of {lines} lines in tread runs"
    items = f["texts"] + f["strokes"]
    if f["texts"] >= TEXT_MIN and f["texts"] >= TEXT_SHARE * items:
        if f["numeric"] >= NUMERIC_SHARE * f["texts"]:
            return "dimension", f"{f['numeric']} of its {f['texts']} texts are numbers"
        if f["grid_labels"] >= GRID_LABEL_SHARE * f["texts"]:
            return "axis", f"{f['grid_labels']} of its {f['texts']} texts are grid labels"
        return "text", f"{f['texts']} texts among {items} items"
    if f["axis_lt"] >= LINETYPE_SHARE * n:
        return "axis", f"{f['axis_lt']} of its {n} strokes have a centre or dash-dot linetype"
    if f.get("hatch", 0) >= HATCH_SHARE * max(1, f["long"]) and f.get("hatch", 0) >= HATCH_RUN:
        return "hatch", f"{f['hatch']} of its {f['long']} long lines repeat at one even pitch (a hatch or tile pattern)"
    if f["columns"] >= STRUCTURE_SHARE * (lines + 4 * f["circles"]) and f["columns"] >= 8:
        return "structure", f"{f['columns']} pieces of column boxes or circles"
    if f["swings"] >= SWING_MIN and f["swings"] >= f["bundles"]:
        return "door", f"{f['swings']} door swings (quarter arcs with their leaf), {f['bundles']} window bundles"
    return None, ""                         # walls and windows: ``infer_roles`` (a window stands at the walls' jambs)


def long_share(f: dict) -> float:
    """The share of a layer's line length in lines of ``LONG2_M`` or more."""
    return f["long2_m"] / f["length_m"] if f.get("length_m") else 0.0


def infer_roles(strokes, texts=(), unit: Optional[float] = None, fallback: Optional[float] = None) -> dict:
    """``{layer: {"role", "why"}}`` for the document's layers (the module docstring); layers no test decides are left
    out."""
    unit = unit_m(strokes, fallback) if unit is None else unit
    feats = layer_features(strokes, texts, unit)
    out = {}
    for layer, f in feats.items():
        role, why = decide(f)
        if role:
            out[layer] = {"role": role, "why": why}
    # the walls: the layer whose long lines pair over the greatest length, then those pairing as well along its walls
    cands = [(f["paired_m"], layer) for layer, f in feats.items() if layer not in out and f["long"]
             and f["paired"] >= WALL_PAIR_SHARE * f["long"] and long_share(f) >= WALL_LONG_SHARE]
    if cands:
        best_m, best = max(cands)
        out[best] = {"role": "wall", "why": f"{feats[best]['paired']} of its {feats[best]['long']} long lines pair at "
                                            f"a wall's thickness ({best_m:.0f} m), the most of any layer"}
        for m, layer in sorted(cands, reverse=True):
            if layer == best or m < WALL_LENGTH_SHARE * best_m \
                    or feats[layer]["paired"] < WALL_SECOND_PAIR_SHARE * feats[layer]["long"]:
                continue
            near = _near_share(feats[layer]["_fams"], feats[best]["_fams"], unit)
            if near >= WALL_NEAR_SHARE:
                out[layer] = {"role": "wall", "why": f"{feats[layer]['paired']} of its {feats[layer]['long']} long lines "
                                                     f"pair ({m:.0f} m), {near:.0%} of them along '{best}''s walls"}
    # the windows: bundles of parallel lines whose two ends stand at the wall layers' jambs
    reach = JAMB_M / unit
    jambs = _endpoints([feats[k]["_fams"] for k, v in out.items() if v["role"] == "wall"], reach)
    for layer, f in feats.items():
        if layer in out or f["bundles"] < BUNDLE_MIN or long_share(f) >= WALL_LONG_SHARE \
                or f["bundle_lines"] < WINDOW_SHARE * max(1, f["long"]):
            continue
        at = sum(1 for outer in f["_bundle_ends"]
                 if any(_near_point(jambs, a, reach) and _near_point(jambs, b, reach) for a, b in outer))
        if at >= BUNDLE_MIN and at >= JAMB_SHARE * f["bundles"]:
            out[layer] = {"role": "window", "why": f"{at} of its {f['bundles']} bundles of parallel lines stand "
                                                   f"between the walls' jambs"}
    return out


JAMB_M = 0.15                   # a window bundle's end this near a wall layer's line end stands at a jamb ...
JAMB_SHARE = 0.5                # ... for this share of the layer's bundles


def _endpoints(fam_lists: list, cell: float) -> dict:
    grid: dict = defaultdict(list)
    for fams in fam_lists:
        for u, n, rows in fams:
            for off, s0, s1, _l in rows:
                for s in (s0, s1):
                    p = (u[0] * s + n[0] * off, u[1] * s + n[1] * off)
                    grid[(int(p[0] // cell), int(p[1] // cell))].append(p)
    return grid


def _near_point(grid: dict, p, reach: float) -> bool:
    k = (int(p[0] // reach), int(p[1] // reach))
    return any(math.dist(p, q) <= reach for dx in (-1, 0, 1) for dy in (-1, 0, 1)
               for q in grid.get((k[0] + dx, k[1] + dy), ()))


def roles_for(strokes, texts=(), unit: Optional[float] = None, fallback: Optional[float] = None) -> Optional[dict]:
    """``{layer: {"role", "why"}}`` to register (``layer_names.set_geometry_roles``) when the document's names say
    nothing (possibly empty), else None. ``unit``: the drawing's metres per unit when known (the sheets stage's unit
    check), else the door swings' or ``fallback``."""
    if not names_say_nothing(strokes, texts):
        return None
    return infer_roles(strokes, texts, unit=unit, fallback=fallback)


def register(file: str, page, unit: Optional[float] = None) -> Optional[dict]:
    """Infer and register the roles of one document's model space (``roles_for``, ``layer_names.set_geometry_roles``);
    returns what was registered (None for a document whose names say something: nothing registered)."""
    from wenart.ingest.generic import layer_names as LN

    roles = roles_for(page.strokes, page.texts, unit=unit, fallback=getattr(page, "units_to_m", None))
    LN.set_geometry_roles(file, roles)
    return roles
