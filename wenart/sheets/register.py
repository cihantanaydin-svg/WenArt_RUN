"""Registration of the plan regions into one building frame (docs/milestone10.md §3.1 item 5).

What: ``register(plans, reference, conflict, warnings)`` sets ``transform_to_building`` and ``registration`` of
every plan region: the affine ``[a, b, c, d, e, f]`` from source units to building metres and how it was found
(reference, outline ICP, columns), its rotation, shift, residual and whether the stairs of adjacent levels overlap.

Why: on one sheet the plans are drawn side by side; each level must sit over the one below. A difference is never
"fixed": a residual over 5 cm is a ``registration_residual`` conflict and every level is built as drawn.

How (metres):
- the outline of a plan is the outer boundary of its long straight strokes (>= 0.5 m), each grown by ``GROW_M``
  (0.75 m: an opening up to 1.5 m wide in walls drawn as face lines is bridged), merged, holes filled and shrunk back
  (the walls' outer faces; furniture and tiles inside do not matter); a closed outline that encloses all other strokes
  with a margin (the roof outline on an attic plan) and the section cut line (layers ``KESİT``, ``SECTION``,
  ``SCHNITT``, ``COUPE``, ``CUT``) are left out;
- the reference is the base ground-floor plan (else the lowest base plan); its frame: x right, y up, origin at the
  min corner of its outline (transform ``[s, 0, -s x0, 0, s, -s y0]``; the pipeline moves the origin to the min corner
  of the reference's outer walls once the core has read them, docs/milestone10.md §1.6b row 1);
- ``registration.shift_m`` / ``rotation_deg`` map a region's drawing onto the reference drawing, both in metres
  (``p_ref = R(rotation) (p metres_per_unit) + shift_m``); ``transform_to_building`` is that map followed by the
  reference's origin step;
- every other plan: candidates at 0/90/180/270 degrees, started from its outline box aligned to the reference's at
  the centre and at each corner, refined by trimmed ICP (the 80 % nearest outline points, translation only); the
  lowest trimmed RMS wins (0 degrees on ties). Columns (closed squares 0.15-0.8 m) that match within 0.10 m refine the
  shift when >= 3 match (method ``columns``). The residual is the RMS distance of all outline points to the
  reference outline; ``matched`` counts those within 5 cm;
- stairs (blocks or layers named ``merdiven``, ``stair``, ``treppe``, ``escalier``) of adjacent levels must overlap
  (``stairs_aligned``; a stair on one level only is listed, no stairs on either gives null).
"""
from __future__ import annotations

import math
import re
from typing import Callable, Optional

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Polygon
from shapely.ops import unary_union

from wenart.sheets import classify as SC
from wenart.sheets import units_check as UC
from wenart.sheets.model import box_union

SEGMENT_MIN_M = 0.5
GROW_M = 0.75
CUT_LAYER_RE = re.compile(r"KESIT|SECTION|SCHNITT|COUPE|\bCUT\b")
SAMPLE_M = 0.10
TRIM = 0.8
ICP_ITERS = 40
RESIDUAL_MAX_M = 0.05
MATCH_M = 0.05
COLUMN_MATCH_M = 0.10
COLUMNS_MIN = 3
ROOF_MARGIN_M = (0.2, 2.0)


def enclosing_outlines(region, mpu: Optional[float], max_margin_m: Optional[float] = None) -> list:
    """Closed outlines that enclose every other stroke of the region with a margin of at least 0.2 m on every side
    (and at most ``max_margin_m``): a roof outline drawn on the top plan (0.2-2 m), a page border. Their entity
    ids; such an outline is never a wall."""
    geom = region.geometry_box
    out = []
    lo = ROOF_MARGIN_M[0] / mpu if mpu else 0.0
    hi = max_margin_m / mpu if (mpu and max_margin_m is not None) else float("inf")
    for e in region.ents:
        if e.rect is None and not (len(e.strokes) == 1 and e.strokes[0].closed and len(e.strokes[0].pts) >= 4):
            continue
        b = e.box
        # Lines that end on the outline (a ridge or hip line drawn up to the eaves) do not count for the margin.
        others = [o.box for o in region.ents if o is not e and o.box != b and not _ends_on(o, b)]
        if not others or b != geom:
            continue
        ob = box_union(others)
        margins = [ob[0] - b[0], ob[1] - b[1], b[2] - ob[2], b[3] - ob[3]]
        if all(lo <= m <= hi and m > 0 for m in margins):
            out.append(e.id)
    return out


def _ends_on(ent, box, rel: float = 0.005) -> bool:
    """A single straight line inside ``box`` with an end on its boundary."""
    if len(ent.strokes) != 1 or ent.strokes[0].closed or len(ent.strokes[0].pts) != 2:
        return False
    tol = rel * max(box[2] - box[0], box[3] - box[1])
    for x, y in ent.strokes[0].pts:
        if not (box[0] - tol <= x <= box[2] + tol and box[1] - tol <= y <= box[3] + tol):
            return False
    return any(min(abs(x - box[0]), abs(x - box[2]), abs(y - box[1]), abs(y - box[3])) <= tol
               for x, y in ent.strokes[0].pts)


def cut_line_entities(region) -> set:
    """Entities on a section cut-line layer (``A-A`` with its arms and arrows): never part of the outline."""
    from wenart.sheets import titles as T
    return {e.id for e in region.ents if e.layer and CUT_LAYER_RE.search(T.fold(e.layer))}


CUT_MIN_M = 1.0                  # the cut line itself is at least 1 m long


def cut_line(plans: list, section) -> Optional[dict]:
    """The section's cut line drawn on a registered plan (``A-A``: a long line on a cut-line layer with two short
    arms at its ends pointing the way the viewer looks, letters at the ends). Returns ``{axis, at, flipped, view,
    region, entities, letter}`` in the building frame: ``axis`` the building axis the section's width runs along (the
    cut line's direction), ``at`` the building coordinate of the line on the other axis, ``flipped`` True when the
    viewer's left (the section's left end) is the max end along ``axis``. A line whose letter does not appear in the
    section's title is not used when the title names one; None when no plan draws a cut line."""
    from wenart.sheets import titles as T
    title = T.fold((section.title or {}).get("text") or "") if section is not None else ""
    named = re.match(r"^\s*([A-Z0-9]{1,2})\s*-\s*\1\b", title)
    for r in plans:
        tf, mpu = r.transform_to_building, r.metres_per_unit
        if tf is None or not mpu:
            continue
        ids = cut_line_entities(r)
        if not ids:
            continue
        segs = [(a, b, st) for e in r.ents if e.id in ids for a, b, st in UC.segments(e.strokes)]
        if not segs:
            continue
        a, b, st = max(segs, key=lambda s: math.dist(s[0], s[1]))
        length = math.dist(a, b)
        if length * mpu < CUT_MIN_M:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        tol = 0.02 * length
        arms = []
        for c, d, other in segs:
            if (c, d) == (a, b):
                continue
            for p, q in ((c, d), (d, c)):
                if min(math.dist(p, a), math.dist(p, b)) <= tol and math.dist(p, q) > 0:
                    vx, vy = q[0] - p[0], q[1] - p[1]
                    n = math.hypot(vx, vy)
                    if abs(vx / n * ux + vy / n * uy) <= 0.2:            # perpendicular to the cut line
                        arms.append((vx / n, vy / n, other.id))
        if not arms:
            continue
        vx = sum(x for x, _, _ in arms) / len(arms)
        vy = sum(y for _, y, _ in arms) / len(arms)
        letters = [t for t in r.texts if len(T.fold(t.text).strip()) <= 2
                   and min(math.dist(t.point, a), math.dist(t.point, b)) <= 0.1 * length]
        letter = T.fold(letters[0].text).strip() if letters else None
        if named and letter and letter != named.group(1):
            continue
        # Building frame: the linear part of the region's transform.
        bux, buy = tf[0] * ux + tf[1] * uy, tf[3] * ux + tf[4] * uy
        bvx, bvy = tf[0] * vx + tf[1] * vy, tf[3] * vx + tf[4] * vy
        axis = "x" if abs(bux) >= abs(buy) else "y"
        mid = ((a[0] + b[0]) / 2.0, (a[1] + b[1]) / 2.0)
        mx, my = tf[0] * mid[0] + tf[1] * mid[1] + tf[2], tf[3] * mid[0] + tf[4] * mid[1] + tf[5]
        at = my if axis == "x" else mx
        left = (-bvy, bvx)                                  # the viewer's left: the view turned 90 deg ccw
        flipped = (left[0] if axis == "x" else left[1]) > 0
        return {"axis": axis, "at": round(at, 4) + 0.0, "flipped": bool(flipped),
                "view": [round(bvx, 4) + 0.0, round(bvy, 4) + 0.0], "region": r.id,
                "entities": sorted({st.id} | {i for _, _, i in arms}), "letter": letter}
    return None


def roof_outlines(region, mpu: float) -> list:
    """Closed outlines around the whole top plan with a 0.2-2 m margin (the roof outline drawn on it)."""
    return enclosing_outlines(region, mpu, ROOF_MARGIN_M[1])


def outline(region, mpu: float, exclude: set) -> Optional[Polygon]:
    """The plan's outline polygon in source units (None when nothing long enough is drawn)."""
    lines = []
    min_len = SEGMENT_MIN_M / mpu
    for e in region.ents:
        if e.id in exclude or e.dim is not None:
            continue
        for a, b, _ in UC.segments(e.strokes):
            if math.dist(a, b) >= min_len:
                lines.append(LineString([a, b]))
    if not lines:
        return None
    grow = GROW_M / mpu
    merged = unary_union([ln.buffer(grow, cap_style="square", join_style="mitre") for ln in lines])
    polys = list(merged.geoms) if isinstance(merged, MultiPolygon) else [merged]
    best = max(polys, key=lambda p: p.area)
    filled = Polygon(best.exterior).buffer(-grow, join_style="mitre")
    if filled.is_empty:
        return None
    if isinstance(filled, MultiPolygon):
        filled = max(filled.geoms, key=lambda p: p.area)
    return filled


def _points(poly: Polygon, scale: float) -> np.ndarray:
    ring = shapely.segmentize(LineString(np.asarray(poly.exterior.coords) * scale), SAMPLE_M)
    return np.asarray(ring.coords)[:-1]


def _rot(theta_deg: float) -> np.ndarray:
    t = math.radians(theta_deg)
    return np.array([[math.cos(t), -math.sin(t)], [math.sin(t), math.cos(t)]])


def _nearest(ring: LineString, pts: np.ndarray) -> np.ndarray:
    geoms = shapely.points(pts)
    d = shapely.line_locate_point(ring, geoms)
    q = shapely.line_interpolate_point(ring, d)
    return shapely.get_coordinates(q)


def icp(moving: np.ndarray, ring: LineString, shift: np.ndarray) -> tuple[np.ndarray, float]:
    """Trimmed translation-only ICP; returns the shift and the trimmed RMS."""
    t = shift.copy()
    rms = math.inf
    for _ in range(ICP_ITERS):
        p = moving + t
        q = _nearest(ring, p)
        d = np.hypot(*(q - p).T)
        keep = np.argsort(d)[: max(3, int(TRIM * len(d)))]
        step = (q[keep] - p[keep]).mean(axis=0)
        t = t + step
        rms = float(np.sqrt(np.mean(d[keep] ** 2)))
        if np.hypot(*step) < 1e-5:
            break
    return t, rms


def register(plans: list, reference, conflict: Callable, warnings: list) -> dict:
    """Registers ``plans`` (regions with ``metres_per_unit``) onto ``reference``. Returns ``{region id: outline
    polygon in building metres}`` for the outline cross-checks."""
    outlines: dict[str, Polygon] = {}
    ref_mpu = reference.metres_per_unit
    excl = set(enclosing_outlines(reference, ref_mpu)) | cut_line_entities(reference)
    ref_poly = outline(reference, ref_mpu, excl)
    if ref_poly is None:
        for r in plans:
            r.registration = {"reference": None, "method": "none", "rotation_deg": 0.0, "shift_m": [0.0, 0.0],
                              "residual_m": None, "matched": 0, "stairs_aligned": None,
                              "note": "the reference plan has no outline"}
        warnings.append(f"registration: the reference plan {reference.id} has no outline; plans not registered")
        return outlines
    x0, y0 = ref_poly.bounds[0], ref_poly.bounds[1]
    ref_t = np.array([-x0 * ref_mpu, -y0 * ref_mpu])
    reference.transform_to_building = [ref_mpu, 0.0, _r(ref_t[0]), 0.0, ref_mpu, _r(ref_t[1])]
    reference.registration = {"reference": None, "method": "reference", "rotation_deg": 0.0,
                              "shift_m": [0.0, 0.0], "residual_m": 0.0, "matched": 0,
                              "stairs_aligned": None, "note": None}
    ref_m = affinity.affine_transform(ref_poly, [ref_mpu, 0, 0, ref_mpu, ref_t[0], ref_t[1]])
    outlines[reference.id] = ref_m
    ring = LineString(ref_m.exterior.coords)
    ref_cols = np.array([(c[0] * ref_mpu + ref_t[0], c[1] * ref_mpu + ref_t[1])
                         for c in SC.columns_of(reference, ref_mpu)]).reshape(-1, 2)
    rb = ref_m.bounds
    for r in plans:
        if r is reference:
            continue
        mpu = r.metres_per_unit
        poly = outline(r, mpu, set(enclosing_outlines(r, mpu)) | cut_line_entities(r))
        if poly is None:
            r.registration = {"reference": reference.id, "method": "none", "rotation_deg": 0.0, "shift_m": [0.0, 0.0],
                              "residual_m": None, "matched": 0, "stairs_aligned": None, "note": "no outline"}
            warnings.append(f"registration: {r.file} {r.id} has no outline; not registered")
            continue
        pts0 = _points(poly, mpu)
        best = None
        for theta in (0.0, 90.0, 180.0, 270.0):
            rot = _rot(theta)
            pts = pts0 @ rot.T
            mb = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max())
            inits = [((rb[0] + rb[2]) / 2 - (mb[0] + mb[2]) / 2, (rb[1] + rb[3]) / 2 - (mb[1] + mb[3]) / 2),
                     (rb[0] - mb[0], rb[1] - mb[1]), (rb[2] - mb[2], rb[1] - mb[1]),
                     (rb[0] - mb[0], rb[3] - mb[3]), (rb[2] - mb[2], rb[3] - mb[3])]
            for init in inits:
                t, rms = icp(pts, ring, np.array(init, dtype=float))
                key = (round(rms, 4), theta != 0.0)
                if best is None or key < best[0]:
                    best = (key, theta, t, rms)
        _, theta, t, rms = best
        rot = _rot(theta)
        pts = pts0 @ rot.T + t
        method = "outline_icp"
        cols = np.array([np.asarray(c) * mpu @ rot.T + t for c in SC.columns_of(r, mpu)]).reshape(-1, 2)
        matched_cols = []
        if len(cols) and len(ref_cols):
            for c in cols:
                d = np.hypot(*(ref_cols - c).T)
                k = int(np.argmin(d))
                if d[k] <= COLUMN_MATCH_M:
                    matched_cols.append(ref_cols[k] - c)
        note = None
        if len(matched_cols) >= COLUMNS_MIN:
            t = t + np.mean(matched_cols, axis=0)
            pts = pts0 @ rot.T + t
            method = "columns"
            note = f"{len(matched_cols)} columns matched"
        q = _nearest(ring, pts)
        d = np.hypot(*(q - pts).T)
        residual = float(np.sqrt(np.mean(d ** 2)))
        matched = int((d <= MATCH_M).sum())
        a = mpu * math.cos(math.radians(theta))
        b = mpu * math.sin(math.radians(theta))
        r.transform_to_building = [_r(a), _r(-b), _r(t[0]), _r(b), _r(a), _r(t[1])]
        r.registration = {"reference": reference.id, "method": method, "rotation_deg": theta,
                          "shift_m": [_r(t[0] - ref_t[0]), _r(t[1] - ref_t[1])], "residual_m": round(residual, 4),
                          "matched": matched, "stairs_aligned": None, "note": note}
        outlines[r.id] = affinity.affine_transform(poly, [a, -b, b, a, t[0], t[1]])
        if residual > RESIDUAL_MAX_M:
            cid = conflict("registration_residual", [r.id, reference.id],
                           f"{r.file} {r.id} ({(r.level or {}).get('id')}) registered onto {reference.id} "
                           f"({(reference.level or {}).get('id')}) with an RMS outline distance of {residual:.3f} m "
                           f"({matched} of {len(d)} outline points within {MATCH_M * 100:.0f} cm; outlines "
                           f"{_size(outlines[r.id])} vs {_size(ref_m)})",
                           "unresolved: each level is built as drawn")
            r.conflicts.append(cid)
    return outlines


def _size(poly) -> str:
    b = poly.bounds
    return f"{b[2] - b[0]:.2f} x {b[3] - b[1]:.2f} m"


def _r(v: float) -> float:
    return round(float(v), 6) + 0.0


def stairs_check(plans: list, conflict: Callable, warnings: list) -> None:
    """``stairs_aligned`` of each plan with the plan of the level below in the same variant (base levels with base
    levels, an alternative with the base levels next to it); the lowest level is checked against the level above."""
    def boxes(r) -> list:
        tf = r.transform_to_building
        if tf is None:
            return []
        out = []
        for b in SC.stairs_of(r):
            pts = [(tf[0] * x + tf[1] * y + tf[2], tf[3] * x + tf[4] * y + tf[5]) for x, y in
                   ((b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3]))]
            out.append(Polygon(pts))
        return out

    by_order: dict[int, list] = {}
    for r in plans:
        if r.level is not None and r.registration is not None:
            by_order.setdefault(r.level["order"], []).append(r)
    for order, regions in by_order.items():
        below = [b for b in by_order.get(order - 1, []) if b.variant in ("base", None)]
        if not below and order - 1 not in by_order:
            below = [b for b in by_order.get(order + 1, []) if b.variant in ("base", None)]
        if not below:
            continue
        for r in regions:
            mine = boxes(r)
            theirs = [s for b in below for s in boxes(b)]
            if not mine and not theirs:
                continue
            if not mine or not theirs:
                r.registration["stairs_aligned"] = False
                warnings.append(f"registration: {r.id} ({r.level['id']}): stairs drawn on "
                                f"{'the level next to it only' if theirs else 'this level only'}")
                continue
            ok = any(a.intersects(b) for a in mine for b in theirs)
            r.registration["stairs_aligned"] = ok
            if not ok:
                cid = conflict("stair_alignment", [r.id] + [b.id for b in below],
                               f"{r.id} ({r.level['id']}): its stairs do not overlap the stairs of the level "
                               f"next to it",
                               "unresolved: each level is built as drawn")
                r.conflicts.append(cid)


SITE_SIZE_TOL = (0.05, 0.30)          # a site plan's building outline: within 5 % or 0.30 m of the reference's size
SITE_RESIDUAL_MAX_M = 0.30            # site plans are drawn coarser (1/200, 1/500)


CHORD_SHARE = 0.8                     # wall_extent: the chord length most cross-sections reach
CHORD_SAMPLES = 41


def wall_extent(outline_m: Polygon) -> tuple[float, float]:
    """(x, y) extent of the outline that most of it reaches: per axis, the 80th-percentile chord length over 41
    cross-sections. A protrusion along less than 20 % of the other side (entrance steps, a stair, a terrace edge
    line) does not count, unlike in the box of the outline."""
    b = outline_m.bounds
    out = []
    for axis in ("x", "y"):
        lo, hi = (b[1], b[3]) if axis == "x" else (b[0], b[2])
        chords = []
        for k in range(CHORD_SAMPLES):
            c = lo + (hi - lo) * (k + 0.5) / CHORD_SAMPLES
            ray = LineString([(b[0] - 1.0, c), (b[2] + 1.0, c)] if axis == "x" else [(c, b[1] - 1.0), (c, b[3] + 1.0)])
            chords.append(ray.intersection(outline_m).length)
        chords.sort()
        out.append(chords[min(len(chords) - 1, int(CHORD_SHARE * len(chords)))])
    return out[0], out[1]


def register_site(region, reference, reference_outline: Polygon, warnings: list) -> bool:
    """Registers a site plan onto the reference plan through the building's outline drawn on it (``site_outline``):
    a closed polyline of the reference outline's size (either way round), fitted at 0/90/180/270 degrees by the
    same trimmed ICP. Sets ``transform_to_building`` and ``registration`` (``outline_entities`` names the outline);
    False (listed) when no such outline fits within 0.30 m. A symmetric outline cannot tell an angle from the one
    180 degrees away: the lower angle is kept and listed."""
    mpu = region.metres_per_unit
    ref_tf = reference.transform_to_building
    if not mpu or ref_tf is None:
        return False
    rb = reference_outline.bounds
    rw, rh = rb[2] - rb[0], rb[3] - rb[1]
    ring = LineString(reference_outline.exterior.coords)

    def fits(a: float, b: float) -> bool:
        return abs(a - b) <= max(SITE_SIZE_TOL[0] * b, SITE_SIZE_TOL[1])

    tried = []
    for e in region.ents:
        if len(e.strokes) != 1 or not e.strokes[0].closed or len(e.strokes[0].pts) < 4:
            continue
        poly = Polygon(e.strokes[0].pts)
        if not poly.is_valid or poly.area <= 0:
            continue
        b = poly.bounds
        w, h = (b[2] - b[0]) * mpu, (b[3] - b[1]) * mpu
        if not ((fits(w, rw) and fits(h, rh)) or (fits(w, rh) and fits(h, rw))):
            continue
        pts0 = _points(poly, mpu)
        for theta in (0.0, 90.0, 180.0, 270.0):
            pts = pts0 @ _rot(theta).T
            mb = (pts[:, 0].min(), pts[:, 1].min(), pts[:, 0].max(), pts[:, 1].max())
            init = np.array([(rb[0] + rb[2]) / 2 - (mb[0] + mb[2]) / 2, (rb[1] + rb[3]) / 2 - (mb[1] + mb[3]) / 2])
            t, rms = icp(pts, ring, init)
            tried.append(((round(rms, 4), theta), theta, t, e, pts0))
    best = min(tried, key=lambda x: x[0]) if tried else None
    if best is None or best[0][0] > SITE_RESIDUAL_MAX_M:
        found = "" if best is None else f" (best fit {best[0][0]:.2f} m)"
        warnings.append(f"site plan {region.id}: no closed outline of the building's size ({rw:.2f} x {rh:.2f} m) "
                        f"fits{found}: not registered")
        region.registration = {"reference": reference.id, "method": "none", "rotation_deg": 0.0,
                               "shift_m": [0.0, 0.0], "residual_m": None, "matched": 0, "stairs_aligned": None,
                               "note": "no building outline of the reference's size"}
        return False
    _, theta, t, e, pts0 = best
    pts = pts0 @ _rot(theta).T + t
    d = np.hypot(*(_nearest(ring, pts) - pts).T)
    residual = float(np.sqrt(np.mean(d ** 2)))
    a = mpu * math.cos(math.radians(theta))
    b = mpu * math.sin(math.radians(theta))
    region.transform_to_building = [_r(a), _r(-b), _r(t[0]), _r(b), _r(a), _r(t[1])]
    region.registration = {"reference": reference.id, "method": "site_outline", "rotation_deg": theta,
                           "shift_m": [_r(t[0] - ref_tf[2]), _r(t[1] - ref_tf[5])], "residual_m": round(residual, 4),
                           "matched": int((d <= MATCH_M).sum()), "stairs_aligned": None,
                           "note": f"the building outline {e.id} on the site plan", "outline_entities": [e.id]}
    twin = [x for x in tried if x[3] is e and x[1] == (theta + 180.0) % 360.0 and x[0][0] - best[0][0] <= 0.01]
    if twin:
        warnings.append(f"site plan {region.id}: its building outline {e.id} fits at {theta:.0f} and "
                        f"{(theta + 180.0) % 360.0:.0f} deg alike (symmetric): {theta:.0f} deg kept")
    return True
