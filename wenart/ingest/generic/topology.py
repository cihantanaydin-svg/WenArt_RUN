"""Plot, building, faces and virtual separators of the generic plan core (docs/milestone7.md §2.5, §2.7.1).

``split_plot`` decides which wall components are the building and which are site elements:

- wall components are taken with every opening bridged (runs are already merged by ``openings``; door and window
  rectangles are added again so nothing depends on that);
- the **building** = the components whose faces (holes) hold at least one indoor room-name label block;
- a component without indoor labels whose convex hull contains the building outline is the **plot** (a C-shaped
  compound wall open on the gate side counts): its walls go to ``site.boundary_walls`` (``kind "plot"``) and the
  exterior label blocks (Parking, Garden, ...) outside the building and inside the hull go to ``site.areas``
  (``polygon`` only when a closed face exists);
- every other component without indoor labels goes to ``site.boundary_walls`` with ``kind "other"`` and a warning,
  except a component lying inside the building outline (a free-standing wall in a room), which stays a building
  wall with a warning; nothing is dropped silently;
- a building face whose only labels are exterior keywords is a site area with its polygon, not a room.

``separators`` closes open-plan faces only where the drawing needs it: candidates come only from free wall ends
whose end gap was empty (*end-to-wall*: the empty end gap itself, <= 2.4 m; *end-to-end*: two free ends of parallel
walls whose end faces lie within 0.20 m of one perpendicular line, <= 2.4 m apart). A candidate is kept only when a
face holding >= 2 room-name blocks gets fewer per face, or when it separates a stair from a labelled face; the others
are logged "considered, not needed".

All geometry is in page metres (y up). Review reasons are returned as warnings starting with ``REVIEW_PREFIX``.
"""
from __future__ import annotations

import math
from typing import Optional

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from wenart import building as B
from wenart.ingest.model import OpeningItem, WallItem

CLOSE_M = 0.002
HULL_SHARE = 0.99
SEPARATOR_MAX_M = 2.4
END_TO_END_ALIGN_M = 0.20
SEPARATOR_CONFIDENCE = 0.8
REVIEW_PREFIX = "needs_review: "


# --------------------------------------------------------------------------
# Shared geometry
# --------------------------------------------------------------------------

def wall_polygon(w) -> Polygon:
    """Rectangle of a WallItem or a ``{"start", "end", "thickness"}`` dict."""
    if isinstance(w, dict):
        start, end, t = w["start"], w["end"], w["thickness"]
    else:
        start, end, t = w.start, w.end, w.thickness
    return LineString([tuple(start), tuple(end)]).buffer(t / 2.0, cap_style=2, join_style=2)


def host_wall(opening: OpeningItem, walls: list) -> Optional[int]:
    """Index of the wall whose centre line carries the opening (parallel, centre within thickness/2 + 20 mm)."""
    best, best_d = None, math.inf
    rot = math.radians(opening.rotation_deg)
    od = (math.cos(rot), math.sin(rot))
    for k, w in enumerate(walls):
        start, end, t = (w["start"], w["end"], w["thickness"]) if isinstance(w, dict) else (w.start, w.end, w.thickness)
        length = math.dist(start, end)
        if length <= 0:
            continue
        wd = ((end[0] - start[0]) / length, (end[1] - start[1]) / length)
        if abs(od[0] * wd[1] - od[1] * wd[0]) > math.sin(math.radians(3.0)):
            continue
        d = LineString([tuple(start), tuple(end)]).distance(Point(opening.center))
        if d <= t / 2.0 + 0.02 and d < best_d:
            best, best_d = k, d
    return best


def opening_polygon(opening: OpeningItem, walls: list, extra: float = 0.0) -> Optional[Polygon]:
    """The gap rectangle of an opening on its host wall (virtual separators: a thin strip along the line)."""
    if opening.virtual and opening.line:
        return LineString([tuple(opening.line[0]), tuple(opening.line[1])]).buffer(CLOSE_M, cap_style=2)
    k = host_wall(opening, walls)
    if k is None:
        return None
    w = walls[k]
    t = w["thickness"] if isinstance(w, dict) else w.thickness
    rot = math.radians(opening.rotation_deg)
    dx, dy = math.cos(rot) * (opening.width / 2.0 + extra), math.sin(rot) * (opening.width / 2.0 + extra)
    c = opening.center
    return LineString([(c[0] - dx, c[1] - dy), (c[0] + dx, c[1] + dy)]).buffer(t / 2.0, cap_style=2, join_style=2)


def separator_polygon(line) -> Polygon:
    """A virtual separator as a thin strip that reaches 2 mm into the walls at both ends."""
    (x0, y0), (x1, y1) = line
    length = math.dist((x0, y0), (x1, y1)) or 1.0
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    a = (x0 - ux * CLOSE_M, y0 - uy * CLOSE_M)
    b = (x1 + ux * CLOSE_M, y1 + uy * CLOSE_M)
    return LineString([a, b]).buffer(CLOSE_M, cap_style=2)


def bridged_union(walls: list, openings: list = (), separators: list = ()):
    """Union of the wall rectangles, the opening rectangles and the separator strips, tiny gaps closed."""
    polys = [wall_polygon(w) for w in walls]
    for o in openings:
        p = opening_polygon(o, walls)
        if p is not None:
            polys.append(p)
    for s in separators:
        line = s.line if isinstance(s, OpeningItem) else s
        if line:
            polys.append(separator_polygon(line))
    if not polys:
        return Polygon()
    u = unary_union(polys)
    return u.buffer(CLOSE_M, join_style=2).buffer(-CLOSE_M, join_style=2)


def _parts(geom) -> list[Polygon]:
    if geom.is_empty:
        return []
    return list(getattr(geom, "geoms", [geom]))


def faces(walls: list, openings: list = (), separators: list = ()) -> list[Polygon]:
    """Holes of the bridged wall union: the faces rooms are made of (§2.7.1)."""
    out = []
    for part in _parts(bridged_union(walls, openings, separators)):
        out.extend(Polygon(ring) for ring in part.interiors)
    return out


def building_outline(walls: list, openings: list = ()):
    """The filled outline of the building walls (exterior rings of the bridged union, holes filled)."""
    parts = [Polygon(p.exterior) for p in _parts(bridged_union(walls, openings))]
    return unary_union(parts) if parts else Polygon()


def outer_loop_problem(walls: list, openings: list = ()) -> Optional[str]:
    """Why the building walls do not form one closed outer loop, or None (§2.5)."""
    parts = _parts(bridged_union(walls, openings))
    if not parts:
        return "no building walls"
    if len(parts) > 1:
        return f"building walls form {len(parts)} separate parts"
    if not parts[0].interiors:
        return "building walls enclose no face"
    return None


def _label_in(poly: Polygon, block) -> bool:
    return poly.contains(Point(block.anchor))


# --------------------------------------------------------------------------
# Plot and building (§2.5)
# --------------------------------------------------------------------------

def split_plot(walls: list[WallItem], openings: list[OpeningItem], label_blocks: list,
               level_id: Optional[str] = None) -> tuple[list[WallItem], dict, list[str]]:
    """Building walls, the ``site`` block (page metres) and warnings.

    ``site["openings"]`` holds the openings whose host wall went to the site (with ``index`` = position in
    ``openings``); the caller drops them from the building. Warnings starting with ``REVIEW_PREFIX`` are review
    reasons.
    """
    warnings: list[str] = []
    site = {"boundary_walls": [], "areas": [], "decor": [], "openings": []}
    if not walls:
        return [], site, warnings
    union = bridged_union(walls, openings)
    comps = _parts(union)
    wall_comp: dict[int, int] = {}
    for k, w in enumerate(walls):
        poly = wall_polygon(w)
        best = max(range(len(comps)), key=lambda i: comps[i].intersection(poly).area) if comps else None
        wall_comp[k] = best
    indoor = [b for b in label_blocks if not getattr(b, "exterior", False)]
    outdoor = [b for b in label_blocks if getattr(b, "exterior", False)]
    comp_labels = {i: [b for b in indoor if any(_label_in(Polygon(r), b) for r in comps[i].interiors)]
                   for i in range(len(comps))}
    building = {i for i, labels in comp_labels.items() if labels}
    if not building:
        warnings.append("no wall component encloses an indoor room label: every wall is kept as a building wall")
        building = set(range(len(comps)))
    outline = unary_union([Polygon(comps[i].exterior) for i in building])

    kinds: dict[int, str] = {}
    for i, comp in enumerate(comps):
        if i in building:
            continue
        hull = comp.convex_hull
        if not outline.is_empty and hull.intersection(outline).area >= HULL_SHARE * outline.area:
            kinds[i] = "plot"
        elif outline.contains(comp.representative_point()):
            kinds[i] = "inside"
            building.add(i)
            warnings.append(f"free-standing wall component inside the building at "
                            f"({comp.centroid.x:.2f}, {comp.centroid.y:.2f}) m kept as building walls")
        else:
            kinds[i] = "other"
            warnings.append(f"wall component without room labels at ({comp.centroid.x:.2f}, {comp.centroid.y:.2f}) m "
                            f"({comp.bounds[2] - comp.bounds[0]:.2f} x {comp.bounds[3] - comp.bounds[1]:.2f} m) is "
                            f"not part of the building: recorded in site, not built")

    building_walls: list[WallItem] = []
    site_wall_index: dict[int, int] = {}
    n = 0
    for k, w in enumerate(walls):
        comp = wall_comp[k]
        if comp in building:
            building_walls.append(w)
            continue
        n += 1
        item = {"start": [round(v, 4) for v in w.start], "end": [round(v, 4) for v in w.end],
                "thickness": w.thickness, "evidence": [w.evidence], "kind": kinds.get(comp, "other")}
        if level_id:
            item["id"] = f"sw_{level_id}_{n:03d}"
        site_wall_index[k] = len(site["boundary_walls"])
        site["boundary_walls"].append(item)
    for j, o in enumerate(openings):
        k = host_wall(o, walls) if not o.virtual else None
        if k is not None and k in site_wall_index:
            site["openings"].append({"index": j, "type": o.kind, "center": list(o.center), "width": o.width,
                                     "boundary_wall": site_wall_index[k], "evidence": [o.evidence],
                                     "status": o.status})

    # Exterior labels: building faces labelled only with exterior keywords, or areas between house and plot.
    plot_hulls = [comps[i].convex_hull for i, kind in kinds.items() if kind == "plot"]
    building_faces = [Polygon(r) for i in building for r in comps[i].interiors]
    used_outdoor = set()
    for face in building_faces:
        inside = [b for b in label_blocks if _label_in(face, b)]
        if inside and all(getattr(b, "exterior", False) for b in inside):
            for b in inside:
                used_outdoor.add(id(b))
                site["areas"].append(_area(b, [list(p) for p in list(face.exterior.coords)[:-1]], level_id,
                                           note="exterior area enclosed by building walls"))
            warnings.append(f"exterior area '{inside[0].name}' is enclosed by building walls: recorded in site, "
                            f"not a room")
            rest = [f for f in building_faces if f is not face]
            if not rest:
                warnings.append(REVIEW_PREFIX + "exterior area inside the building outline and no indoor face left")
    all_walls_geom = [wall_polygon(w) for w in walls]
    for b in outdoor:
        if id(b) in used_outdoor:
            continue
        pt = Point(b.anchor)
        if not outline.is_empty and outline.contains(pt):
            warnings.append(f"exterior label '{b.name}' lies inside the building but in no closed face")
            site["areas"].append(_area(b, None, level_id, note="inside the building outline, no closed face"))
            continue
        in_plot = any(h.contains(pt) for h in plot_hulls)
        extent = _free_extent(b.anchor, all_walls_geom, plot_hulls)
        site["areas"].append(_area(b, None, level_id, extent=extent,
                                   note=None if in_plot else "outside the plot wall"))
    for b in indoor:
        if any(_label_in(f, b) for f in building_faces):
            continue
        if not outline.is_empty and outline.contains(Point(b.anchor)):
            continue                                     # inside the outline but in no face: rooms report it
        where = "inside the plot" if any(h.contains(Point(b.anchor)) for h in plot_hulls) else "outside the plot"
        warnings.append(f"room label '{b.name}' at ({b.anchor[0]:.2f}, {b.anchor[1]:.2f}) m lies outside the "
                        f"building ({where})")
    return building_walls, site, warnings


def _area(block, polygon, level_id: Optional[str], extent=None, note: Optional[str] = None) -> dict:
    item = {"label": block.name, "label_raw": " ".join(getattr(r, "text", "") for r in getattr(block, "name_runs", []))
            or block.name, "polygon": polygon, "evidence": list(getattr(block, "evidence", []) or [])}
    if level_id:
        item["id"] = f"sa_{level_id}_{B.slugify(block.name) or 'area'}"
    size_text = getattr(block, "size_text", None)
    if size_text:
        item["label_size"] = _label_size(size_text, polygon, extent, getattr(block, "size", None))
    if extent is not None:
        item["extent_m"] = [round(extent[0], 3), round(extent[1], 3)]
    item["anchor"] = [round(block.anchor[0], 4), round(block.anchor[1], 4)]
    if note:
        item["note"] = note
    return item


def _label_size(text: str, polygon, extent, pair=None) -> dict:
    """``label_size`` of a site area: printed size, the measured extent; never a conflict (areas are not rooms).
    ``pair`` is the label block's parsed size (G1); without it the text is parsed here."""
    out = {"text": text, "width_m": None, "length_m": None, "measured": None, "status": "unchecked"}
    if pair is None:
        try:
            from wenart import units as U
            pair = U.parse_size_pair(text)
        except Exception:                                # units module missing or text not a size
            pair = None
    if pair:
        out["width_m"], out["length_m"] = round(pair[0].metres, 4), round(pair[1].metres, 4)
    if polygon:
        poly = Polygon(polygon)
        rect = poly.minimum_rotated_rectangle
        c = list(rect.exterior.coords)
        out["measured"] = sorted([round(math.dist(c[0], c[1]), 3), round(math.dist(c[1], c[2]), 3)])
    elif extent is not None:
        out["measured"] = [round(extent[0], 3), round(extent[1], 3)]
    return out


def _free_extent(anchor, wall_polys: list[Polygon], hulls: list[Polygon], reach: float = 30.0):
    """Open extent around an exterior label: distance along +-x and +-y to the nearest wall face (or the plot hull
    where no wall is hit). Returns (x extent, y extent) or None."""
    x, y = anchor
    stops = []
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ray = LineString([(x, y), (x + dx * reach, y + dy * reach)])
        best = math.inf
        for poly in wall_polys + [h.exterior for h in hulls]:
            inter = ray.intersection(poly)
            if inter.is_empty:
                continue
            d = Point(x, y).distance(inter)
            best = min(best, d)
        if not math.isfinite(best):
            return None
        stops.append(best)
    return (stops[0] + stops[1], stops[2] + stops[3])


# --------------------------------------------------------------------------
# Separators (§2.7.1)
# --------------------------------------------------------------------------

def separators(walls: list[WallItem], openings: list[OpeningItem], gap_log: list[dict], label_blocks: list,
               stairs: list, units_to_m: Optional[float] = None) -> tuple[list[OpeningItem], list[dict]]:
    """Virtual separators that keep two room names (or a stair and a room name) out of one face.

    ``walls``: the building walls; ``gap_log``: the log of ``openings.gaps_and_openings`` (its wall indices refer to
    the walls before the plot split, so the walls a separator touches are found by geometry); ``stairs``:
    FurnitureItems (or anything with ``center``). Returns the kept separators (``box`` in page units when
    ``units_to_m`` is given) and one log dict per candidate.
    """
    names = [b for b in label_blocks if not getattr(b, "exterior", False)]
    cands = _candidates(walls, gap_log)
    log: list[dict] = []
    kept: list[dict] = []
    base_faces = faces(walls, openings)
    score = _score(base_faces, names, stairs)
    for cand in sorted(cands, key=lambda c: c["length"]):
        entry = {k: v for k, v in cand.items() if k != "poly"}
        if cand["length"] > SEPARATOR_MAX_M:
            entry.update(kept=False, reason=f"longer than {SEPARATOR_MAX_M} m")
            log.append(entry)
            continue
        trial = faces(walls, openings, [c["line"] for c in kept] + [cand["line"]])
        new = _score(trial, names, stairs)
        reasons = []
        if new["excess"] < score["excess"]:
            reasons.append("two room names shared one face")
        if new["stair_mixed"] < score["stair_mixed"]:
            reasons.append("separates the stair from a labelled face")
        if reasons:
            cand["reason"] = "; ".join(reasons)
            kept.append(cand)
            score = new
            entry.update(kept=True, reason=cand["reason"])
        else:
            entry.update(kept=False, reason="considered, not needed")
        log.append(entry)
    items = [_separator_item(c, walls, units_to_m) for c in kept]
    return items, log


def _candidates(walls: list[WallItem], gap_log: list[dict]) -> list[dict]:
    out = []
    for e in gap_log:
        if e.get("kind") == "end" and e.get("class") == "empty":
            line = [tuple(e["line"][0]), tuple(e["line"][1])]
            out.append({"kind": "end_to_wall", "line": line, "length": round(math.dist(*line), 4),
                        "walls": [e.get("free_wall"), e.get("hit_wall")]})
    ends = [e for e in gap_log if e.get("kind") == "free_end" and e.get("gap_class") in ("empty", "none")
            and not e.get("same_as_run_gap")]
    for i in range(len(ends)):
        for j in range(i + 1, len(ends)):
            a, b = ends[i], ends[j]
            if a.get("wall") == b.get("wall"):
                continue
            da, db = a["direction"], b["direction"]
            if abs(da[0] * db[1] - da[1] * db[0]) > 0.05:          # walls not parallel
                continue
            pa, pb = a["point"], b["point"]
            # Offset along the wall direction must be small (end faces on one perpendicular line).
            along = abs((pb[0] - pa[0]) * da[0] + (pb[1] - pa[1]) * da[1])
            if along > END_TO_END_ALIGN_M:
                continue
            across = abs(-(pb[0] - pa[0]) * da[1] + (pb[1] - pa[1]) * da[0])
            if across <= max(a["thickness"], b["thickness"]):
                continue
            # The line must touch both walls: for stubs pointing the same way it sits at the end of the shorter one,
            # for opposite stubs in the middle of their overlap (none -> no candidate).
            ea = pa[0] * da[0] + pa[1] * da[1]
            eb = pb[0] * da[0] + pb[1] * da[1]
            if da[0] * db[0] + da[1] * db[1] > 0:
                at = min(ea, eb)
            elif eb <= ea:
                at = (ea + eb) / 2.0
            else:
                continue
            off = ((pa[0] + pb[0]) / 2.0) * -da[1] + ((pa[1] + pb[1]) / 2.0) * da[0]
            mid_along = (da[0] * at - da[1] * off, da[1] * at + da[0] * off)
            n = (-da[1], da[0])
            sa = (pa[0] - mid_along[0]) * n[0] + (pa[1] - mid_along[1]) * n[1]
            sb = (pb[0] - mid_along[0]) * n[0] + (pb[1] - mid_along[1]) * n[1]
            lo, hi = sorted((sa, sb))
            ta = a["thickness"] / 2.0 if sa < sb else b["thickness"] / 2.0
            tb = b["thickness"] / 2.0 if sa < sb else a["thickness"] / 2.0
            p0 = (mid_along[0] + n[0] * (lo + ta), mid_along[1] + n[1] * (lo + ta))
            p1 = (mid_along[0] + n[0] * (hi - tb), mid_along[1] + n[1] * (hi - tb))
            line = [(round(p0[0], 4), round(p0[1], 4)), (round(p1[0], 4), round(p1[1], 4))]
            out.append({"kind": "end_to_end", "line": line, "length": round(math.dist(*line), 4),
                        "walls": [a.get("wall"), b.get("wall")]})
    return out


def _score(face_list: list[Polygon], names: list, stairs: list) -> dict:
    excess = 0
    stair_mixed = 0
    for f in face_list:
        n = sum(1 for b in names if _label_in(f, b))
        excess += max(0, n - 1)
        for s in stairs:
            c = s.center if hasattr(s, "center") else s["center"]
            if f.contains(Point(c)) and n > 0:
                stair_mixed += 1
    return {"excess": excess, "stair_mixed": stair_mixed}


def _separator_item(cand: dict, walls: list[WallItem], units_to_m: Optional[float] = None) -> OpeningItem:
    """The kept candidate as a virtual opening; its evidence names the walls its ends touch (found by geometry,
    because the gap log indexes the walls before the plot split)."""
    (x0, y0), (x1, y1) = cand["line"]
    touching = [w for w in walls if wall_polygon(w).distance(Point(x0, y0)) <= 0.01
                or wall_polygon(w).distance(Point(x1, y1)) <= 0.01]
    ref = touching[0] if touching else (walls[0] if walls else None)
    file_rel = ref.evidence.get("file", "") if ref else ""
    page = ref.evidence.get("page") if ref else None
    entity = "separator:" + "|".join(w.entity for w in touching)
    ev = B.evidence(file_rel, "derived", SEPARATOR_CONFIDENCE, page=page, entity=entity)
    ev["note"] = f"virtual separator ({cand['kind'].replace('_', '-')}, {cand['length']:.2f} m): {cand['reason']}"
    angle = math.degrees(math.atan2(y1 - y0, x1 - x0)) % 180.0
    box = [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]
    if units_to_m:
        box = [v / units_to_m for v in box]
    return OpeningItem(kind="opening", width=round(math.dist((x0, y0), (x1, y1)), 4),
                       center=(round((x0 + x1) / 2, 4), round((y0 + y1) / 2, 4)), rotation_deg=round(angle, 3),
                       box=[round(v, 4) for v in box], entity=entity, evidence=ev, virtual=True,
                       line=((x0, y0), (x1, y1)))


# --------------------------------------------------------------------------
# Unlabelled faces (§2.7.1)
# --------------------------------------------------------------------------

def unlabelled_face_type(face, walls: list, openings: list, stairs: list = ()) -> tuple[str, str]:
    """``("hall", reason)`` when an unlabelled face holds a stair or touches >= 2 doors/openings, else
    ``("unknown", reason)``. The room stays ``unverified`` either way."""
    poly = face if isinstance(face, Polygon) else Polygon(face)
    for s in stairs:
        c = s.center if hasattr(s, "center") else s["center"]
        if poly.contains(Point(c)):
            return "hall", "unlabelled face holding the stair"
    touching = 0
    for o in openings:
        if o.kind == "window":
            continue
        p = opening_polygon(o, walls)
        if p is not None and p.distance(poly) <= 0.02:
            touching += 1
    if touching >= 2:
        return "hall", f"unlabelled face touching {touching} doors/openings"
    return "unknown", f"unlabelled face touching {touching} door/opening"
