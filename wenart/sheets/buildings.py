"""Several buildings on one plot (user request of 11 Oct 2026, project real04: "there can be multiple buildings in the
same plot").

What: ``site_buildings(region, plans, outlines, warnings, heights=None) -> list[dict] | None`` finds every copy of the
drawn building on a site plan and registers the site plan onto the building frame through the first copy (it sets
``region.transform_to_building`` and ``region.registration`` like ``register.register_site``). Each copy is
``{"id", "reference", "footprint" (building metres), "rotation_deg", "translate", "dz", "plan_region", "size_m",
"orientation", "entrance_ground", "entities", "evidence", "method", "note"}``; ``rotation_deg`` / ``translate`` /
``dz`` move the building as modelled (the first copy) onto that copy (``p' = R(rotation) p + translate``, z + dz).
``site_datum(...)`` gives ±0.00 in absolute metres from the ground marks at the first copy's entrance.

Why: real04's site plan (r14, "4 ADET VİLLA") holds two twin-villa blocks tilted 11 degrees; each block is two
inserts of the block ``bina`` (one villa each: three sides of a 12.0 x 7.59 m rectangle and a hatch), so no closed
outline of the plans' size exists and ``register_site`` (one closed outline at 0/90/180/270 degrees) found none. The
ground falls 9 m across the plot (marks 37-46 m): the blocks stand 3 m apart in height.

How:

- candidates: every entity of the site plan whose strokes make a rectangle-like polygon (a closed stroke, or an open
  stroke of >= 4 points closed by its end points: a three-sided outline; the union of an entity's polygons), at
  least ``MIN_AREA_M2``; a candidate covering most of the plot is no footprint;
- a footprint is one candidate, or two candidates that touch (``PAIR_GAP_M``) and whose union is rectangle-like,
  whose minimum rotated rectangle matches a read plan's outline rectangle within ``SIZE_TOL_M`` (either way round);
  matches are taken by size error, never overlapping;
- the transform: rotation = the plan outline's long axis minus the footprint's (+180 degrees), the footprint's
  rectangle centre onto the plan outline's. The two angles 180 degrees apart are told apart by the entrance markers
  next to the footprint (blocks, layers or texts naming an entrance: ``G_BINA``, ``GİRİŞ``, ``ENTRANCE`` ...): the
  angle that puts them nearest to the exterior door swings of the entrance plan (arcs of 0.55-1.3 m radius hinged on
  its outline) wins; without markers or doors, or when both angles score alike, the lower angle is kept and the copy
  is marked ``orientation: ambiguous`` (listed);
- the first copy (lowest x, then y, on the sheet) is the reference: the building as modelled; the site plan is
  registered through it;
- heights: the absolute level marks of the site plan (``KOT`` texts, mark attributes ``BDK`` / ``KOT`` ...) within
  ``ENTRANCE_MARK_M`` of a copy's entrance markers are its entrance ground; ``dz`` = that minus the reference's
  (0, listed, when either is unknown).
"""
from __future__ import annotations

import math
import re
from typing import Optional

from shapely.geometry import Point, Polygon
from shapely.ops import unary_union

from wenart.sheets import titles as T

MIN_AREA_M2 = 20.0
RECT_FILL = 0.92                 # polygon area / its minimum rotated rectangle
SIZE_TOL_M = 0.35
PAIR_GAP_M = 0.10
PLOT_SHARE = 0.6                 # a candidate covering this much of the largest closed outline is the plot
ENTRANCE_RE = re.compile(r"G_?BINA|GIRIS|ENTRANCE|ENTRY|EINGANG|ENTREE")
ENTRANCE_REACH_M = 4.0           # an entrance marker belongs to a footprint this near
ENTRANCE_MARK_M = 3.5            # a level mark this near an entrance marker gives the entrance ground
DOOR_RADIUS_M = (0.55, 1.3)
DOOR_REACH_M = 0.45
ORIENT_MARGIN_M = 1.0            # the two angles must differ by this much in their mean marker-door distance


def rect_of(poly: Polygon) -> tuple[float, float, float, float, float]:
    """``(cx, cy, length, width, angle_deg)`` of the minimum rotated rectangle; ``angle_deg`` in [0, 180) is the
    direction of the long side."""
    mrr = poly.minimum_rotated_rectangle
    c = list(mrr.exterior.coords)
    a, b = math.dist(c[0], c[1]), math.dist(c[1], c[2])
    if a >= b:
        ang = math.degrees(math.atan2(c[1][1] - c[0][1], c[1][0] - c[0][0]))
        length, width = a, b
    else:
        ang = math.degrees(math.atan2(c[2][1] - c[1][1], c[2][0] - c[1][0]))
        length, width = b, a
    ctr = mrr.centroid
    return ctr.x, ctr.y, length, width, ang % 180.0


def rect_like(poly: Polygon) -> bool:
    if poly.is_empty or poly.geom_type != "Polygon" or poly.area <= 0:
        return False
    _, _, length, width, _ = rect_of(poly)
    return length * width > 0 and poly.area / (length * width) >= RECT_FILL


def _stroke_polygon(st, mpu: float) -> Optional[Polygon]:
    pts = [(p[0] * mpu, p[1] * mpu) for p in st.pts]
    if st.kind in ("circle", "arc") or len(pts) < 3:
        return None
    if not st.closed and len(pts) < 4:
        return None                              # an open stroke closes to a footprint only with >= 3 sides
    poly = Polygon(pts).buffer(0)
    if poly.geom_type != "Polygon" or poly.area <= 0:
        return None
    return poly


def candidates(region, mpu: float) -> list[dict]:
    """Rectangle-like polygons of the site plan's entities (source metres: source units x ``mpu``)."""
    out = []
    for e in region.ents:
        polys = [p for st in e.strokes for p in [_stroke_polygon(st, mpu)] if p is not None and p.area >= 1.0]
        if not polys:
            continue
        u = unary_union(polys)
        shapes = [u] if u.geom_type == "Polygon" else list(getattr(u, "geoms", []))
        for poly in shapes:
            if poly.area >= MIN_AREA_M2 and rect_like(poly):
                out.append({"poly": poly, "entities": [e.id], "blocks": [e.block] if e.block else [],
                            "layer": e.layer})
    if out:                                       # the plot (the largest closed outline) is no footprint
        big = max(c["poly"].area for c in out)
        out = [c for c in out if c["poly"].area < PLOT_SHARE * big or c["poly"].area < 400.0]
    return out


def _size_error(rect, plan_rect) -> float:
    return max(abs(rect[2] - plan_rect[2]), abs(rect[3] - plan_rect[3]))


def footprints(cands: list[dict], plan_rects: dict) -> list[dict]:
    """The candidates (one, or two that touch) whose rectangle matches a plan outline (``plan_rects``: region id ->
    ``rect_of``), never overlapping, smallest size error first."""
    options = []
    for c in cands:
        options.append((c["poly"], [c]))
    for i, a in enumerate(cands):
        for b in cands[i + 1:]:
            if a["poly"].distance(b["poly"]) > PAIR_GAP_M or a["poly"].intersection(b["poly"]).area > 0.05 * min(
                    a["poly"].area, b["poly"].area):
                continue
            u = unary_union([a["poly"].buffer(PAIR_GAP_M / 2, join_style="mitre"),
                             b["poly"].buffer(PAIR_GAP_M / 2, join_style="mitre")]).buffer(-PAIR_GAP_M / 2,
                                                                                         join_style="mitre")
            if u.geom_type == "Polygon" and rect_like(u):
                options.append((u, [a, b]))
    scored = []
    for poly, parts in options:
        rect = rect_of(poly)
        best = min(((_size_error(rect, pr), rid) for rid, pr in plan_rects.items()), default=None)
        if best is not None and best[0] <= SIZE_TOL_M:
            scored.append((best[0], len(parts), poly, parts, best[1], rect))
    scored.sort(key=lambda s: (s[0], s[1]))
    taken: list[dict] = []
    for err, _n, poly, parts, rid, rect in scored:
        if any(poly.intersection(t["poly"]).area > 0.2 * poly.area for t in taken):
            continue
        taken.append({"poly": poly, "parts": parts, "plan_region": rid, "rect": rect, "size_error": round(err, 3)})
    taken.sort(key=lambda t: (round(t["rect"][0], 1), round(t["rect"][1], 1)))
    return taken


def entrance_points(region, mpu: float) -> list[tuple[float, float]]:
    """Points (source metres) of the entrance markers: entities whose block or layer, or texts that name an entrance."""
    pts = []
    for e in region.ents:
        name = T.fold(" ".join(x for x in (e.block or "", e.layer or "") if x))
        if ENTRANCE_RE.search(name):
            pts.append((e.centre[0] * mpu, e.centre[1] * mpu))
    for t in region.texts:
        if ENTRANCE_RE.search(T.fold(t.text)):
            pts.append((t.point[0] * mpu, t.point[1] * mpu))
    return pts


def door_hinges(plan, outline: Polygon) -> list[tuple[float, float]]:
    """Exterior door swings of a registered plan: arcs of a door's radius hinged within ``DOOR_REACH_M`` of its
    outline (building metres)."""
    tf = plan.transform_to_building
    mpu = plan.metres_per_unit
    if tf is None or not mpu:
        return []
    ring = outline.exterior
    out = []
    for st in plan.strokes():
        if st.kind != "arc" or not st.arc:
            continue
        r = float(st.arc.get("radius") or 0.0) * mpu
        if not DOOR_RADIUS_M[0] <= r <= DOOR_RADIUS_M[1]:
            continue
        cx, cy = st.arc["center"]
        p = (tf[0] * cx + tf[1] * cy + tf[2], tf[3] * cx + tf[4] * cy + tf[5])
        if ring.distance(Point(p)) <= DOOR_REACH_M:
            out.append(p)
    return out


def _rot(theta_deg: float, p) -> tuple[float, float]:
    c, s = math.cos(math.radians(theta_deg)), math.sin(math.radians(theta_deg))
    return c * p[0] - s * p[1], s * p[0] + c * p[1]


def _site_to_building(rect, plan_rect, flip: bool) -> tuple[float, tuple[float, float]]:
    """``(theta, t)``: ``p_building = R(theta) p_site_metres + t`` that lays the footprint rectangle on the plan's."""
    theta = (plan_rect[4] - rect[4] + (180.0 if flip else 0.0)) % 360.0
    rc = _rot(theta, (rect[0], rect[1]))
    return theta, (plan_rect[0] - rc[0], plan_rect[1] - rc[1])


def _apply(theta: float, t, p) -> tuple[float, float]:
    q = _rot(theta, p)
    return q[0] + t[0], q[1] + t[1]


def _orientation(fp: dict, plan_rect, markers: list, hinges: list) -> tuple[bool, str, Optional[float]]:
    """``(flip, how, score)``: the angle that puts the footprint's entrance markers nearest to the doors."""
    near = [m for m in markers if fp["poly"].distance(Point(m)) <= ENTRANCE_REACH_M]
    if not near or not hinges:
        return False, "ambiguous", None
    scores = []
    for flip in (False, True):
        theta, t = _site_to_building(fp["rect"], plan_rect, flip)
        d = [min(math.dist(_apply(theta, t, m), h) for h in hinges) for m in near]
        scores.append(sum(d) / len(d))
    if abs(scores[0] - scores[1]) < ORIENT_MARGIN_M:
        return False, "ambiguous", round(min(scores), 3)
    flip = scores[1] < scores[0]
    return flip, "entrances", round(min(scores), 3)


def absolute_marks(region, mpu: float) -> list[tuple[tuple[float, float], float, str]]:
    """The site plan's absolute level marks: ``[((x, y) source metres, value, entity)]`` (a mark attribute's bare
    value counts: ``BDK 44.00``)."""
    from wenart.levels import marks as LM

    out = []
    for t in region.texts:
        tag = (t.evidence or {}).get("attrib_tag") if isinstance(t.evidence, dict) else None
        rec = LM.read_mark(t.text, bare=LM.is_mark_tag(tag))
        if rec is None or rec["relative"] or rec.get("note"):
            continue
        out.append(((t.point[0] * mpu, t.point[1] * mpu), float(rec["value"]), t.id))
    return out


def _entrance_ground(fp: dict, markers: list, marks: list) -> Optional[float]:
    near = [m for m in markers if fp["poly"].distance(Point(m)) <= ENTRANCE_REACH_M]
    vals = [v for p, v, _ in marks if any(math.dist(p, m) <= ENTRANCE_MARK_M for m in near)]
    if not vals:
        return None
    vals.sort()
    return round(vals[len(vals) // 2], 3)


def site_buildings(region, plans: list, outlines: dict, warnings: list, entrance_plan=None) -> Optional[list[dict]]:
    """The copies of the building on a site plan (module docstring), or None when fewer than one footprint matches.
    ``plans``: the read plan regions (registered); ``outlines``: region id -> outline (building metres);
    ``entrance_plan``: the plan whose exterior doors the entrance markers are matched to (default: the level at
    ±0.00, else the reference)."""
    mpu = region.metres_per_unit
    if not mpu or not outlines:
        return None
    plan_rects = {rid: rect_of(poly) for rid, poly in outlines.items() if poly is not None and not poly.is_empty}
    fps = footprints(candidates(region, mpu), plan_rects)
    if not fps:
        return None
    markers = entrance_points(region, mpu)
    by_id = {p.id: p for p in plans}
    if entrance_plan is None:
        at_zero = [p for p in plans if (p.level or {}).get("order") == 0 and p.id in outlines]
        entrance_plan = at_zero[0] if at_zero else next((p for p in plans if p.id in outlines), None)
    hinges = door_hinges(entrance_plan, outlines[entrance_plan.id]) if entrance_plan is not None else []
    marks = absolute_marks(region, mpu)
    copies = []
    for k, fp in enumerate(fps):
        plan_rect = plan_rects[fp["plan_region"]]
        flip, how, score = _orientation(fp, plan_rect, markers, hinges)
        theta, t = _site_to_building(fp["rect"], plan_rect, flip)
        ents = [i for part in fp["parts"] for i in part["entities"]]
        blocks = sorted({b for part in fp["parts"] for b in part["blocks"]})
        copies.append({"fp": fp, "theta": theta, "t": t, "orientation": how, "score": score,
                       "entrance_ground": _entrance_ground(fp, markers, marks), "entities": ents, "blocks": blocks})
    ref = copies[0]
    a, b = mpu * math.cos(math.radians(ref["theta"])), mpu * math.sin(math.radians(ref["theta"]))
    region.transform_to_building = [round(a, 9), round(-b, 9), round(ref["t"][0], 6), round(b, 9), round(a, 9),
                                    round(ref["t"][1], 6)]
    region.registration = {"reference": next((p.id for p in plans if (p.registration or {}).get("method") ==
                                              "reference"), None),
                           "method": "site_buildings", "rotation_deg": round(ref["theta"], 4),
                           "shift_m": [round(ref["t"][0], 4), round(ref["t"][1], 4)],
                           "residual_m": ref["fp"]["size_error"], "matched": len(copies), "stairs_aligned": None,
                           "note": f"{len(copies)} building footprint(s) of the plans' size on the site plan; "
                                   f"registered through {', '.join(ref['entities'])}",
                           "outline_entities": [i for c in copies for i in c["entities"]]}
    out = []
    for k, c in enumerate(copies):
        rot = (ref["theta"] - c["theta"]) % 360.0          # A_ref o A_c^-1: p -> R(rot) p + tau
        rt = _rot(rot, c["t"])
        tau = (ref["t"][0] - rt[0], ref["t"][1] - rt[1])
        dz = 0.0
        dz_note = None
        if k > 0:
            if c["entrance_ground"] is not None and ref["entrance_ground"] is not None:
                dz = round(c["entrance_ground"] - ref["entrance_ground"], 3)
            else:
                dz_note = "no level mark at both entrances: the copy stands at the reference's height (assumed)"
                warnings.append(f"site plan {region.id}: building copy b{k + 1}: {dz_note}")
        foot = [list(_apply(ref["theta"], ref["t"], p)) for p in list(c["fp"]["poly"].exterior.coords)[:-1]]
        L, W = c["fp"]["rect"][2], c["fp"]["rect"][3]
        note = (f"{'one outline' if len(c['fp']['parts']) == 1 else 'two outlines'} "
                f"({', '.join(c['blocks']) or 'no block'}) of {L:.2f} x {W:.2f} m match the plan "
                f"{c['fp']['plan_region']} within {c['fp']['size_error']:.2f} m")
        if c["orientation"] == "ambiguous":
            note += "; its 180-degree turn is not told apart by entrance markers and doors (the lower angle kept)"
            warnings.append(f"site plan {region.id}: building copy b{k + 1}: orientation ambiguous (180 degrees)")
        out.append({"id": f"b{k + 1}", "reference": k == 0,
                    "footprint": [[round(x, 4), round(y, 4)] for x, y in foot],
                    "rotation_deg": round(rot if rot <= 180.0 else rot - 360.0, 4) + 0.0,
                    "translate": [round(tau[0], 4) + 0.0, round(tau[1], 4) + 0.0], "dz": dz + 0.0,
                    "plan_region": c["fp"]["plan_region"], "size_m": [round(L, 3), round(W, 3)],
                    "orientation": c["orientation"], "orientation_score_m": c["score"],
                    "entrance_ground": c["entrance_ground"], "entities": c["entities"],
                    "evidence": [{"file": region.file, "method": "vector", "confidence": 0.9 if
                                  c["orientation"] == "entrances" else 0.7, "entity": e, "region_id": region.id,
                                  "rule": "site_building"} for e in c["entities"]],
                    "method": "vector", "dz_note": dz_note, "note": note})
    return out


def site_datum(copies: list[dict], heights: Optional[dict]) -> Optional[dict]:
    """±0.00 in absolute metres: the reference copy's entrance ground minus the section's ground on the entrance
    side (the highest ground the section gives; -0.15 m, D3a, without one)."""
    if not copies or copies[0].get("entrance_ground") is None:
        return None
    grounds = [g["z"]["value"] for g in (heights or {}).get("ground") or [] if (g.get("z") or {}).get("value")
               is not None]
    g = max(grounds) if grounds else -0.15
    value = round(copies[0]["entrance_ground"] - g, 3)
    return {"value": value, "method": "inferred", "confidence": 0.7,
            "note": f"±0.00 = {value:.2f}: the site plan's level marks at the entrances of building {copies[0]['id']} "
                    f"read {copies[0]['entrance_ground']:.2f}, the section's ground there is {g:+.2f}"
                    + ("" if grounds else " (none drawn: 0.15 m below the ground floor, D3a)")}
