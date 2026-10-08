"""From ``sheets.json`` to the Milestone 10 blocks of ``building.json`` (docs/milestone10.md §1.1, §1.6a, §1.6b).

What: pure functions the pipeline calls in a multi-region project: ``level_fields`` (kind, variant, region,
elevation and ceiling from the section, floor to floor), ``variants_block`` (with ``rooms_changed`` and
``exterior_changed``), ``slabs_block`` (outline = the outer face of the outer walls, stair voids, thickness from the
section; a slab that differs for an alternative again as ``sl_<above>__<variant id>``), ``roof_block`` (type,
heights, outline, break line, ridge lines, profile, terrace openings; ``planes`` left empty for track E),
``facade_block`` (drawn faces and one ``elevations`` entry per elevation with its ``plan_check``) and
``site_block`` (drawn ground levels per side, north, label records, plot / paving / grass / parking / trees from
the registered site plan).

Why: the sheets stage reads heights and exterior evidence once; the building JSON carries them with their evidence.
Only drawn looks are written (§1.6b row 12): every other look is resolved by the build and listed there.
"""
from __future__ import annotations

from typing import Callable, Optional

from shapely.geometry import Point, Polygon

from wenart import building as B
from wenart import geometry as G
from wenart.sheets import exterior as EX

MATCH_M = 0.02                 # exterior_changed: walls and openings match within 2 cm
STAIR_MATCH_M = 0.10           # an alternative's stair at the base stair's position (within 0.1 m) keeps the slab
SIDE_ANGLE_DEG = 45.0          # plan_check: a wall faces a side when its outward normal is within 45 degrees
AREA_TARGET = {"paving": "paving", "garden": "grass", "parking": "parking"}
SURFACE_PREFIX = {"paving": "sp", "grass": "sg", "parking": "spk"}
DUPLICATE_M = 0.10             # site plan vs ground-floor plan: duplicates within 0.1 m merge


Shift = tuple[float, float]


def moved(points: Optional[list], shift: Shift) -> Optional[list]:
    """Sheets building metres -> the pipeline's frame: minus ``shift`` (how far the reference's outer wall faces lie
    from the sheets outline corner, ``ProjectBuild.frame_shift``)."""
    if not points or not (shift[0] or shift[1]):
        return points
    return [[round(p[0] - shift[0], 4) + 0.0, round(p[1] - shift[1], 4) + 0.0] for p in points]


def _heights_by_level(sheets: dict) -> dict[str, dict]:
    return {h["level_id"]: h for h in (sheets.get("heights") or {}).get("levels") or []}


def level_fields(level: dict, record, sheets: dict, warn) -> None:
    """Add the M10 level fields to a level dict (mutated) from its region record and the section heights."""
    base_id = record.base_level_id or level["id"]
    level["kind"] = record.level_kind or ("basement" if (level.get("order") or 0) < 0 else "floor")
    level["variant_group"] = record.variant_group
    level["variant"] = record.variant or "base"
    level["variant_slug"] = record.variant_slug or ("base" if not record.base_level_id else None)
    level["base_level_id"] = record.base_level_id
    level["region_id"] = record.region_id
    h = _heights_by_level(sheets).get(base_id)
    if not h:
        level["elevation_source"] = "assumed_default"
        level["floor_to_floor"] = None
        return
    floor = h.get("floor_z") or {}
    if floor.get("value") is not None:
        level["elevation"] = round(float(floor["value"]), 3)
    level["elevation_source"] = "section" if floor.get("method") not in (None, "assumed") else "assumed_default"
    ceiling = h.get("ceiling_height") or {}
    if ceiling.get("value") is not None:
        level["ceiling_height"] = round(float(ceiling["value"]), 3)
        level["ceiling_height_source"] = "section" if ceiling.get("method") != "assumed" else "assumed_default"
    level["floor_to_floor"] = h.get("floor_to_floor")
    if level["elevation_source"] == "assumed_default":
        warn(f"Level {level['id']}: elevation {level['elevation']:.2f} m assumed ({floor.get('note') or 'no section'})")
    if level["ceiling_height_source"] == "assumed_default":
        warn(f"Level {level['id']}: ceiling height {level['ceiling_height']:.2f} m assumed "
             f"({ceiling.get('note') or 'no section'})")


# ----------------------------------------------------------------------------------------------------------------
# Variants
# ----------------------------------------------------------------------------------------------------------------

def _close(a, b, tol: float = MATCH_M) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return abs(float(a) - float(b)) <= tol


def _same_wall(a: dict, b: dict) -> bool:
    ends = (G.distance(a["start"], b["start"]) <= MATCH_M and G.distance(a["end"], b["end"]) <= MATCH_M) or \
        (G.distance(a["start"], b["end"]) <= MATCH_M and G.distance(a["end"], b["start"]) <= MATCH_M)
    return ends and _close(a["thickness"], b["thickness"])


def _same_opening(a: dict, b: dict) -> bool:
    return a["type"] == b["type"] and G.distance(a["center"], b["center"]) <= MATCH_M \
        and _close(a["width"], b["width"]) and _close(a.get("height"), b.get("height")) \
        and _close(a.get("sill_height"), b.get("sill_height"))


def exterior_changed(alt_id: str, base_id: str, walls: list[dict], openings: list[dict]) -> bool:
    """True when an exterior wall of the alternative level (start/end within 2 cm, thickness) or an opening on one
    (type, centre, width, height, sill within 2 cm) has no base match, or a base one has no match on the
    alternative (a window walled up changes the outside too)."""
    def outside(level_id: str) -> tuple[list[dict], list[dict]]:
        ws = [w for w in walls if w["level_id"] == level_id and w.get("exterior")]
        ids = {w["id"] for w in ws}
        return ws, [o for o in openings if o["level_id"] == level_id and o.get("wall_id") in ids]

    aw, ao = outside(alt_id)
    bw, bo = outside(base_id)
    for mine, theirs, same in ((aw, bw, _same_wall), (bw, aw, _same_wall), (ao, bo, _same_opening),
                               (bo, ao, _same_opening)):
        if any(not any(same(x, y) for y in theirs) for x in mine):
            return True
    return False


def variants_block(sheets: dict, levels: list[dict], rooms: list[dict], walls: Optional[list[dict]] = None,
                   openings: Optional[list[dict]] = None) -> list[dict]:
    """``variants[]`` for the levels that were built: the base and every alternative whose level was built."""
    built = {lv["id"] for lv in levels}
    out = []
    for v in sheets.get("variants") or []:
        ids = [i for i in v["levels"] if i in built]
        if not v["base"] and not all(i in built for i in v["levels"] if i not in _base_ids(sheets)):
            continue
        if not ids:
            continue
        entry = {"id": v["id"], "label": v["label"], "levels": ids, "base": bool(v["base"]), "changes": [],
                 "rooms_changed": [], "exterior_changed": False, "evidence": list(v.get("evidence") or [])}
        if not v["base"]:
            for lv in levels:
                if lv["id"] in ids and lv.get("base_level_id"):
                    entry["changes"].append({"variant_group": lv.get("variant_group") or f"vg_{lv['base_level_id']}",
                                             "level_id": lv["id"], "replaces": lv["base_level_id"]})
                    entry["rooms_changed"] += [r["id"] for r in rooms if r["level_id"] == lv["id"]
                                               and not r.get("same_as")]
                    if walls is not None and openings is not None and lv["base_level_id"] in built:
                        entry["exterior_changed"] = entry["exterior_changed"] or \
                            exterior_changed(lv["id"], lv["base_level_id"], walls, openings)
                    else:
                        entry["exterior_changed"] = None        # no base level to compare with: not computed
        out.append(entry)
    return out


def _base_ids(sheets: dict) -> set:
    return {lv["id"] for lv in sheets.get("levels") or []}


# ----------------------------------------------------------------------------------------------------------------
# Slabs
# ----------------------------------------------------------------------------------------------------------------

def _outline(union) -> Optional[list]:
    if union is None or getattr(union, "geom_type", None) != "Polygon":
        return None
    return [[round(x, 4) + 0.0, round(y, 4) + 0.0] for x, y in list(union.exterior.coords)[:-1]]


def _stairs(level_id: Optional[str], furniture: list[dict]) -> list[dict]:
    return [f for f in furniture if level_id is not None and f["level_id"] == level_id and f["type"] == "stair"]


def _slab(lv: dict, below: Optional[dict], unions: dict, furniture: list[dict], sec: Optional[dict],
          slab_default: float, slab_id: str) -> Optional[dict]:
    """The slab under ``lv`` (over ``below``): outline = the larger of the two outer-wall outlines, stair voids over
    the stairs of the level below."""
    below_id = below["id"] if below else None
    own = _outline(unions.get(lv["id"]))
    under = _outline(unions.get(below_id)) if below_id else None
    outline = own
    if own and under and G.polygon_area(under) > G.polygon_area(own) * 1.001:
        outline = under
    if outline is None:
        return None
    thick = (sec or {}).get("thickness") or {}
    from_section = thick.get("method") not in (None, "assumed") and thick.get("value") is not None
    thickness = float(thick["value"]) if from_section else slab_default
    openings = []
    for f in _stairs(below_id, furniture):
        fp = f["footprint"]
        poly = G.rotated_rectangle(fp["center"], fp["size"], fp["rotation_deg"])
        openings.append({"id": f"sv_{slab_id[3:]}_{len(openings) + 1:03d}", "kind": "stair_void",
                         "furniture_id": f["id"],
                         "polygon": [[round(x, 4), round(y, 4)] for x, y in poly], "source": "derived"})
    ev = list(thick.get("evidence") or [])
    ev.append(B.evidence(lv["evidence"][0]["file"] if lv.get("evidence") else "", "derived", 1.0,
                         entity=f"outline of the outer walls of {lv['id']}" + (f" (larger {below_id} below)"
                                                                                 if outline is under else ""),
                         region_id=lv.get("region_id"), rule="outer_wall_outline"))
    return {"id": slab_id, "below_level_id": below_id, "above_level_id": lv["id"], "z_top": float(lv["elevation"]),
            "thickness": round(thickness, 3), "thickness_source": "section" if from_section else "assumed_default",
            "outline": outline, "openings": openings, "variants": [],
            "status": "verified" if from_section else "assumed", "evidence": ev}


def _same_slab(a: dict, b: dict, furniture: list[dict]) -> bool:
    pa, pb = Polygon(a["outline"]), Polygon(b["outline"])
    if not pa.is_valid or not pb.is_valid or pa.hausdorff_distance(pb) > MATCH_M:
        return False
    if len(a["openings"]) != len(b["openings"]):
        return False
    centres = {f["id"]: f["footprint"]["center"] for f in furniture}
    for o in a["openings"]:
        c = centres.get(o.get("furniture_id"))
        if c is None or not any(G.distance(c, centres.get(p.get("furniture_id"), (1e9, 1e9))) <= STAIR_MATCH_M
                                for p in b["openings"]):
            return False
    return True


def slabs_block(sheets: dict, levels: list[dict], unions: dict, furniture: list[dict], slab_default: float,
                warn, variants: Optional[list[dict]] = None) -> list[dict]:
    """One slab under every built base level (``sl_<level id>``); for each alternative, the slabs under and over its
    level again as ``sl_<above>__<variant id>`` (``variants: [id]``, level ids naming the base levels) when their
    outline or stair voids differ (an alternative's stair within 0.1 m of the base stair keeps the base slab)."""
    by_base = {}
    for s in (sheets.get("heights") or {}).get("slabs") or []:
        if s["between"][1]:
            by_base[s["between"][1]] = s
    ordered = sorted(levels, key=lambda lv: (lv.get("order") or 0, lv["id"]))
    base = [lv for lv in ordered if not lv.get("base_level_id")]

    def below_of(lv: dict) -> Optional[dict]:
        under = [b for b in base if (b.get("order") or 0) < (lv.get("order") or 0)]
        return under[-1] if under and (under[-1].get("order") or 0) == (lv.get("order") or 0) - 1 else None

    out = []
    for lv in base:
        slab = _slab(lv, below_of(lv), unions, furniture, by_base.get(lv["id"]), slab_default, f"sl_{lv['id']}")
        if slab is None:
            warn(f"slab under {lv['id']}: no closed outer wall outline; slab not written")
            continue
        if slab["thickness_source"] != "section":
            warn(f"slab under {lv['id']}: thickness {slab['thickness']:.2f} m assumed (brief slab_thickness)")
        out.append(slab)
    by_id = {s["id"]: s for s in out}
    for v in variants or []:
        if v["base"]:
            continue
        for ch in v.get("changes") or []:
            alt = next((lv for lv in levels if lv["id"] == ch["level_id"]), None)
            base_lv = next((lv for lv in base if lv["id"] == ch["replaces"]), None)
            if alt is None or base_lv is None:
                continue
            alt_as_base = dict(alt, id=alt["id"])
            above = next((b for b in base if below_of(b) is base_lv), None)
            pairs = [(f"sl_{base_lv['id']}", alt_as_base, below_of(base_lv), base_lv["id"])]
            if above is not None:
                pairs.append((f"sl_{above['id']}", above, alt_as_base, above["id"]))
            for base_slab_id, top, under, above_id in pairs:
                mine = _slab(top, under, unions, furniture, by_base.get(above_id), slab_default,
                             f"{base_slab_id}__{v['id']}")
                theirs = by_id.get(base_slab_id)
                if mine is None or (theirs is not None and _same_slab(mine, theirs, furniture)):
                    continue
                # Level ids name base ids; the variant maps them through its changes (§1.6b row 8).
                mine["above_level_id"] = above_id
                mine["below_level_id"] = ch["replaces"] if under is alt_as_base else (under or {}).get("id")
                mine["variants"] = [v["id"]]
                out.append(mine)
    return out


# ----------------------------------------------------------------------------------------------------------------
# Roof
# ----------------------------------------------------------------------------------------------------------------

def roof_block(sheets: dict, levels: list[dict], rooms: list[dict], walls: Optional[list[dict]] = None,
               shift: Shift = (0.0, 0.0)) -> Optional[dict]:
    """The roof over the top level, or None when neither a section nor a plan draws it (the build then makes a flat
    roof over the top level, assumed)."""
    heights = sheets.get("heights") or {}
    hroof = heights.get("roof") or {}
    ex = (sheets.get("exterior") or {}).get("roof")
    if not ex and not hroof.get("eaves_z"):
        return None
    base = [lv for lv in levels if not lv.get("base_level_id")]
    top = max(base, key=lambda lv: lv.get("order") or 0) if base else None
    assumed = list((ex or {}).get("assumed") or [])
    profile = None
    if hroof.get("profile"):
        axis = heights.get("cut_axis")
        ds = shift[0] if axis == "x" else shift[1] if axis == "y" else 0.0
        profile = {"region_id": (heights.get("section_regions") or [None])[0], "cut_axis": axis,
                   "points": [[round(p[0] - ds, 4) + 0.0, p[1]] for p in hroof["profile"]], "method": "vector"}
    roof = {"type": (ex or {}).get("type") or "other", "type_source": (ex or {}).get("type_source") or "assumed",
            "over_level_id": top["id"] if top else None,
            "eaves_height": hroof.get("eaves_z"), "ridge_height": hroof.get("ridge_z"),
            "pitches_deg": list(hroof.get("pitches_deg") or []), "overhang": hroof.get("overhang"),
            "thickness": hroof.get("thickness"), "knee_wall": hroof.get("knee_wall"), "profile": profile,
            "outline": moved((ex or {}).get("outline"), shift),
            "break_line": moved((ex or {}).get("break_line"), shift),
            "ridge_lines": [moved(r, shift) for r in (ex or {}).get("ridge_lines") or []], "planes": [], "openings": [],
            "covering": (ex or {}).get("covering"), "covering_colour": None,
            "covering_source": (ex or {}).get("covering_source") if (ex or {}).get("covering") else None,
            "assumed": assumed, "evidence": list((ex or {}).get("evidence") or [])}
    if not ex:
        roof["assumed"].append("roof type (no roof plan, elevation or plan roof lines)")
    if roof["outline"] is None:
        roof["assumed"].append("outline (the outer walls + overhang)")
    for r in rooms:
        if top is not None and r["level_id"] == top["id"] and r.get("room_type") == "balcony":
            polygon, parapets = terrace_opening(r, [w for w in walls or [] if w["level_id"] == top["id"]],
                                                roof["outline"])
            roof["openings"].append({"id": f"ro_{len(roof['openings']) + 1:03d}", "kind": "terrace", "room_id": r["id"],
                                     "polygon": polygon,
                                     "parapet_height": {"value": None, "method": "assumed", "confidence": 0.0,
                                                        "evidence": [], "note": "not drawn"},
                                     "parapet_wall_ids": parapets, "source": "derived"})
    if not roof["evidence"]:
        roof["evidence"] = [e for k in ("eaves_z", "ridge_z") for e in (hroof.get(k) or {}).get("evidence") or []][:2]
    roof["status"] = "verified" if ex and roof["type_source"] != "assumed" else "assumed"
    return roof


def terrace_opening(room: dict, walls: list[dict], outline: Optional[list]) -> tuple[list, list]:
    """A roof terrace's opening in the roof (§1.6b row 13): the room's box grown over the walls around it, to the roof
    outline across an exterior wall (its parapet) and to the centre line of an inner wall; ``(polygon,
    parapet_wall_ids)``. A room that is not a rectangle keeps its polygon (the parapets still listed)."""
    from shapely.geometry import LineString
    poly = Polygon(room["polygon"])
    b = list(poly.bounds)
    rect = abs(poly.area - (b[2] - b[0]) * (b[3] - b[1])) <= 0.01 * max(poly.area, 1e-9)
    ob = None
    if outline:
        xs, ys = [p[0] for p in outline], [p[1] for p in outline]
        ob = (min(xs), min(ys), max(xs), max(ys))
    parapets = []
    grown = list(b)
    for w in walls:
        line = LineString([w["start"], w["end"]])
        reach = w["thickness"] / 2.0 + 0.05
        if line.distance(poly.exterior) > reach or line.intersection(poly.buffer(reach)).length < 0.5:
            continue
        (x0, y0), (x1, y1) = w["start"], w["end"]
        vertical = abs(x1 - x0) < abs(y1 - y0)
        c = (x0 + x1) / 2.0 if vertical else (y0 + y1) / 2.0
        side = (0 if c < b[0] + 1e-9 or abs(c - b[0]) <= reach else 2) if vertical else \
            (1 if c < b[1] + 1e-9 or abs(c - b[1]) <= reach else 3)
        if w.get("exterior"):
            parapets.append(w["id"])
            if ob is not None:
                grown[side] = ob[side]
            else:
                grown[side] = c - w["thickness"] / 2.0 if side in (0, 1) else c + w["thickness"] / 2.0
        else:
            grown[side] = c
    if not rect:
        return [list(p) for p in room["polygon"]], parapets
    x0, y0, x1, y1 = (round(v, 4) + 0.0 for v in grown)
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]], parapets


# ----------------------------------------------------------------------------------------------------------------
# Facade
# ----------------------------------------------------------------------------------------------------------------

def _outward_deg(wall: dict, union) -> Optional[float]:
    """The outward normal of an exterior wall (degrees ccw from +X): the side of its centre line outside the level's
    outer outline."""
    import math
    (x0, y0), (x1, y1) = wall["start"], wall["end"]
    length = math.hypot(x1 - x0, y1 - y0)
    if length <= 0 or union is None:
        return None
    nx, ny = -(y1 - y0) / length, (x1 - x0) / length
    mx, my = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    reach = wall["thickness"] / 2.0 + 0.05
    filled = Polygon(union.exterior) if getattr(union, "geom_type", None) == "Polygon" else None
    if filled is None:
        return None
    for sign in (1.0, -1.0):
        if not filled.contains(Point(mx + sign * nx * reach, my + sign * ny * reach)):
            return math.degrees(math.atan2(sign * ny, sign * nx)) % 360.0
    return None


def _angle_gap(a: float, b: float) -> float:
    d = abs(a - b) % 360.0
    return min(d, 360.0 - d)


def plan_check(seen: dict, north_deg: Optional[float], levels: list[dict], walls: list[dict], openings: list[dict],
               unions: dict) -> Optional[dict]:
    """Openings on the plans' exterior walls facing the elevation's side (base levels) against the ones the
    elevation draws: ``{matched, missing (on the plans only), extra (on the elevation only), plan_windows,
    plan_doors}`` by count per kind; None when the side cannot be placed (a compass side without a north)."""
    normal = EX.normal_deg(seen.get("side"), north_deg)
    if normal is None:
        return None
    base = {lv["id"] for lv in levels if not lv.get("base_level_id")}
    facing = {}
    for w in walls:
        if w["level_id"] in base and w.get("exterior"):
            out = _outward_deg(w, unions.get(w["level_id"]))
            if out is not None and _angle_gap(out, normal) <= SIDE_ANGLE_DEG:
                facing[w["id"]] = w
    plan = {"window": 0, "door": 0}
    floor = {lv["id"]: lv["elevation"] for lv in levels}
    grounds = [g["z"]["value"] for g in seen.get("ground") or [] if (g.get("z") or {}).get("value") is not None]
    ground_z = min(grounds) if grounds else None
    for o in openings:
        if o.get("wall_id") in facing and o["type"] in plan:
            head = floor.get(o["level_id"], 0.0) + (o.get("sill_height") or 0.0) + (o.get("height") or 0.0)
            if ground_z is not None and head <= ground_z + MATCH_M:
                continue                          # below the ground line: an elevation does not draw it
            plan[o["type"]] += 1
    seen_n = {"window": int(seen.get("windows") or 0), "door": int(seen.get("doors") or 0)}
    matched = sum(min(plan[k], seen_n[k]) for k in plan)
    return {"matched": matched, "missing": sum(plan.values()) - matched, "extra": sum(seen_n.values()) - matched,
            "plan_windows": plan["window"], "plan_doors": plan["door"], "walls": sorted(facing)}


def _level_of_band(z_range: Optional[list], levels: list[dict]) -> Optional[str]:
    if not z_range:
        return None
    base = sorted((lv for lv in levels if not lv.get("base_level_id")), key=lambda lv: lv["elevation"])
    lo, hi = min(z_range), max(z_range)
    for k, lv in enumerate(base):
        top = base[k + 1]["elevation"] if k + 1 < len(base) else lv["elevation"] + lv["ceiling_height"]
        if lv["elevation"] - MATCH_M <= lo and hi <= top + MATCH_M:
            return lv["id"]
    return None


def facade_block(sheets: dict, walls: list[dict], warn, levels: Optional[list[dict]] = None,
                 openings: Optional[list[dict]] = None, unions: Optional[dict] = None) -> dict:
    """Drawn facade faces only (§1.6b row 12): an elevation's hatch or label on its side (``wall_id`` null = every
    outward wall face of that side; ``z_range`` in building z, null = the whole height), and one ``elevations``
    entry per elevation region with its ``plan_check``. Faces of an elevation without a side are listed, not
    written. No ``default``: the build resolves every other look."""
    ex = sheets.get("exterior") or {}
    north = (ex.get("north") or {}).get("value")
    levels = levels or []
    faces = []
    for entry in ex.get("facade") or []:
        if entry["side"] == "all":
            warn(f"facade: {entry['material']} ({entry['source']} in {entry.get('region')}) on an elevation without "
                 f"a side: not written")
            continue
        faces.append({"side": entry["side"], "wall_id": None, "level_id": _level_of_band(entry.get("z_range"), levels),
                      "z_range": entry.get("z_range"), "material": entry["material"], "colour": entry.get("colour"),
                      "source": "elevation", "evidence": list(entry.get("evidence") or [])})
    elevations = []
    ground = (sheets.get("heights") or {}).get("ground") or []
    for seen in ex.get("openings_seen") or []:
        check = plan_check(dict(seen, ground=ground), north, levels, walls, openings or [], unions or {}) \
            if levels else None
        if check is None:
            warn(f"elevation {seen['region']} ({seen['side']}): its openings are not checked against the plans "
                 f"(the side needs the north arrow)")
        elevations.append({"region_id": seen["region"], "title": seen.get("title"), "side": seen["side"],
                           "view_bearing_deg": seen.get("view_bearing_deg"), "windows": seen["windows"],
                           "doors": seen["doors"], "positions_m": list(seen.get("positions_m") or []),
                           "plan_check": check})
    return {"faces": faces, "elevations": elevations,
            "evidence": [e for f in faces for e in f.get("evidence") or []]}


# ----------------------------------------------------------------------------------------------------------------
# Site
# ----------------------------------------------------------------------------------------------------------------

def _ground_levels(sheets: dict, north: Optional[float]) -> list[dict]:
    """Drawn ground levels (section ground lines); sides named by compass when the north is known."""
    out = []
    for g in (sheets.get("heights") or {}).get("ground") or []:
        side, azimuth = g["side"], None
        normal = EX.LOCAL_NORMAL_DEG.get(side)
        if north is not None and normal is not None:
            side, azimuth = EX.compass_of(normal, north)
        out.append({"side": side, "azimuth_deg": azimuth, "z": g["z"]})
    return out


def _moved_site(sp: dict, shift: Shift) -> dict:
    if not (shift[0] or shift[1]) or not sp:
        return sp
    out = dict(sp, plot=moved(sp.get("plot"), shift))
    for key in ("paving", "grass", "parking"):
        out[key] = [dict(x, polygon=moved(x["polygon"], shift)) for x in sp.get(key) or []]
    out["trees"] = [dict(x, points=moved(x["points"], shift)) for x in sp.get("trees") or []]
    out["plot_walls"] = [dict(x, start=moved([x["start"]], shift)[0], end=moved([x["end"]], shift)[0])
                         for x in sp.get("plot_walls") or []]
    out["labels"] = [dict(x, point=moved([x["point"]], shift)[0] if x.get("point") else None)
                     for x in sp.get("labels") or []]
    return out


def _surface(prefix: str, n: int, polygon: list, area_id: Optional[str], source: str, evidence: list) -> dict:
    return {"id": f"{prefix}_{n:03d}", "polygon": [list(p) for p in polygon], "z": None, "material": None,
            "colour": None, "area_id": area_id, "source": source, "build": True, "evidence": list(evidence)}


def site_block(site: dict, sheets: dict, area_kind: Callable, ground_level_id: Optional[str] = None,
               shift: Shift = (0.0, 0.0)) -> dict:
    """The M10 site additions on top of the M7 ``site`` block (mutated and returned): drawn ground levels (one
    assumed ``all 0.0`` when none is drawn), the north (null when no arrow is drawn), every area a label record
    (``build: false``) and the surfaces built from drawn outlines (``plot``, ``paving``, ``grass``, ``parking`` with
    the ``area_id`` of their label), the site plan's trees as decor; duplicates of the ground-floor plan's site
    elements within 0.1 m merge (the site plan wins, both evidences kept)."""
    ex = sheets.get("exterior") or {}
    north = ex.get("north")
    levels = _ground_levels(sheets, north["value"] if north else None)
    if not levels:
        levels = [{"side": "all", "azimuth_deg": None,
                   "z": {"value": 0.0, "method": "assumed", "confidence": 0.0, "evidence": [],
                         "note": "no ground line drawn: the ground floor's level"}}]
    zs = {round(float(lv["z"]["value"]), 3) for lv in levels if lv["z"].get("value") is not None}
    site["ground"] = {"levels": levels, "terrain": "flat" if len(zs) <= 1 else "sides", "light_wells": []}
    site["north_deg"] = north if north else None
    for key in ("paving", "grass", "parking"):
        site.setdefault(key, [])
    level_id = ground_level_id or next((a.get("level_id") for a in site.get("areas") or []), None) or "L0"

    # Site-plan labels become area records (the site plan wins over the ground-floor plan's duplicates).
    sp = _moved_site(ex.get("site") or {}, shift)
    areas = site.setdefault("areas", [])
    for lab in sp.get("labels") or []:
        if lab.get("point") is None:
            continue
        dup = next((a for a in areas if a.get("anchor") and G.distance(a["anchor"], lab["point"]) <= DUPLICATE_M
                    and area_kind(a.get("label") or "") == lab["kind"]), None)
        if dup is not None:
            dup["evidence"] = list(lab["evidence"]) + list(dup.get("evidence") or [])
            continue
        areas.append({"id": f"sa_{level_id}_{B.slugify(lab['label'])}", "level_id": level_id,
                      "label": lab["label"].capitalize(), "label_raw": lab["label"], "polygon": None,
                      "anchor": list(lab["point"]), "kind": lab["kind"], "evidence": list(lab["evidence"])})
    for a in areas:
        a["kind"] = area_kind(a.get("label") or "") or a.get("kind") or "other"
        a["build"] = False

    # Surfaces: the ground-floor plan's areas with a closed face, then the site plan's outlines with a label.
    for a in areas:
        target = AREA_TARGET.get(a["kind"])
        if target and a.get("polygon") and len(a["polygon"]) >= 3:
            site[target].append(_surface(SURFACE_PREFIX[target], len(site[target]) + 1, a["polygon"], a.get("id"),
                                         "plan", a.get("evidence") or []))
    for target in ("paving", "grass", "parking"):
        for item in sp.get(target) or []:
            label_ev = next((e for e in item["evidence"] if e.get("text")), None)
            area = next((a for a in areas if label_ev is not None and any(
                e.get("entity") == label_ev.get("entity") for e in a.get("evidence") or [])), None)
            dup = next((s for s in site[target] if Polygon(s["polygon"]).hausdorff_distance(
                Polygon(item["polygon"])) <= DUPLICATE_M), None)
            if dup is not None:
                dup["evidence"] = list(item["evidence"]) + list(dup["evidence"])
                dup["source"] = "site_plan"
                continue
            site[target].append(_surface(SURFACE_PREFIX[target], len(site[target]) + 1, item["polygon"],
                                         area["id"] if area else None, "site_plan", item["evidence"]))
    if sp.get("plot"):
        site["plot"] = {"id": "plot", "polygon": [list(p) for p in sp["plot"]], "z": None, "material": None,
                        "colour": None, "area_id": None, "source": "site_plan", "build": True,
                        "evidence": list(sp.get("evidence") or [])}
    walls = site.setdefault("boundary_walls", [])
    for pw in sp.get("plot_walls") or []:
        dup = next((w for w in walls if G.distance(w["start"], pw["start"]) <= DUPLICATE_M
                    and G.distance(w["end"], pw["end"]) <= DUPLICATE_M), None)
        if dup is not None:
            dup["evidence"] = list(pw["evidence"]) + list(dup.get("evidence") or [])
            continue
        walls.append({"id": f"sw_{level_id}_{len(walls) + 1:03d}", "level_id": level_id, "start": list(pw["start"]),
                      "end": list(pw["end"]), "thickness": pw["thickness"], "kind": "plot",
                      "height": {"value": None, "method": "assumed", "confidence": 0.0, "evidence": [],
                                 "note": "no elevation of the plot wall: the build assumes its height"},
                      "build": True, "evidence": list(pw["evidence"])})
    decor = site.setdefault("decor", [])
    for k, tree in enumerate(sp.get("trees") or []):
        centre = tree["points"][0]
        dup = next((d for d in decor if d.get("kind") == "tree" and G.distance(d["center"], centre) <= DUPLICATE_M),
                   None)
        if dup is not None:
            dup["evidence"] = list(tree["evidence"]) + list(dup.get("evidence") or [])
            continue
        size = round(2.0 * float(tree.get("radius_m") or 1.5), 3)
        decor.append({"id": f"sd_{level_id}_{len(decor) + 1:03d}", "level_id": level_id, "kind": "tree",
                      "center": list(centre), "size": [size, size], "build": True,
                      "evidence": list(tree["evidence"])})
    plot_walls = [w for w in site.get("boundary_walls") or [] if w.get("kind") == "plot"]
    if plot_walls and site.get("plot") is None:
        from shapely.geometry import MultiPoint
        hull = MultiPoint([tuple(p) for w in plot_walls for p in (w["start"], w["end"])]).convex_hull
        if hull.geom_type == "Polygon":
            site["plot"] = {"id": "plot", "polygon": [[round(x, 4), round(y, 4)] for x, y in
                                                      list(hull.exterior.coords)[:-1]],
                            "z": None, "material": None, "colour": None, "area_id": None, "source": "plan",
                            "build": True, "evidence": [e for w in plot_walls for e in w.get("evidence") or []][:4]}
    site.setdefault("plot", None)
    return site
