"""From ``sheets.json`` to the Milestone 10 blocks of ``building.json`` (docs/milestone10.md §1.1, §1.6a).

What: pure functions the pipeline calls in a multi-region project: ``level_fields`` (kind, variant, region,
elevation and ceiling from the section, floor to floor), ``variants_block``, ``slabs_block`` (outline = the outer
face of the outer walls, stair voids, thickness from the section), ``roof_block`` (type, heights, outline, break
line, terrace openings; ``planes`` left empty for track E), ``facade_block`` (drawn faces only, no ``default``) and
``site_block`` (ground levels per side, north, area kinds, plot, paving / grass / parking with polygons).

Why: the sheets stage reads heights and exterior evidence once; the building JSON carries them with their evidence,
and every value no drawing gives is ``assumed`` (listed in ``warnings`` and the roof's ``assumed``).
"""
from __future__ import annotations

from typing import Optional

from wenart import geometry as G

AREA_TARGET = {"paving": "paving", "garden": "grass", "parking": "parking"}


def _heights_by_level(sheets: dict) -> dict[str, dict]:
    return {h["level_id"]: h for h in (sheets.get("heights") or {}).get("levels") or []}


def level_fields(level: dict, record, sheets: dict, warn) -> None:
    """Add the M10 level fields to a level dict (mutated) from its region record and the section heights."""
    base_id = record.base_level_id or level["id"]
    level["kind"] = record.level_kind or ("basement" if (level.get("order") or 0) < 0 else "floor")
    level["variant_group"] = record.variant_group
    level["variant"] = record.variant or "base"
    level["variant_slug"] = record.variant_slug
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


def variants_block(sheets: dict, levels: list[dict], rooms: list[dict]) -> list[dict]:
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
                 "rooms_changed": [], "exterior_changed": None, "evidence": []}
        if not v["base"]:
            for lv in levels:
                if lv["id"] in ids and lv.get("base_level_id"):
                    entry["changes"].append({"variant_group": lv.get("variant_group") or f"vg_{lv['base_level_id']}",
                                             "level_id": lv["id"], "replaces": lv["base_level_id"]})
                    entry["rooms_changed"] = [r["id"] for r in rooms if r["level_id"] == lv["id"]
                                              and not r.get("same_as")]
        out.append(entry)
    return out


def _base_ids(sheets: dict) -> set:
    return {lv["id"] for lv in sheets.get("levels") or []}


def _outline(union) -> Optional[list]:
    if union is None or getattr(union, "geom_type", None) != "Polygon":
        return None
    return [[round(x, 4) + 0.0, round(y, 4) + 0.0] for x, y in list(union.exterior.coords)[:-1]]


def slabs_block(sheets: dict, levels: list[dict], unions: dict, furniture: list[dict], slab_default: float,
                warn) -> list[dict]:
    """One slab under every built level: ``sl_<level id>``."""
    by_base = {}
    for s in (sheets.get("heights") or {}).get("slabs") or []:
        if s["between"][1]:
            by_base[s["between"][1]] = s
    ordered = sorted(levels, key=lambda lv: (lv.get("order") or 0, lv["id"]))
    variants = {v["id"]: v for v in sheets.get("variants") or []}
    out = []
    for lv in ordered:
        base_id = lv.get("base_level_id") or lv["id"]
        below = [b for b in ordered if (b.get("order") or 0) == (lv.get("order") or 0) - 1
                 and not b.get("base_level_id")]
        below_id = below[0]["id"] if below else None
        own = _outline(unions.get(lv["id"]))
        under = _outline(unions.get(below_id)) if below_id else None
        outline = own
        if own and under and G.polygon_area(under) > G.polygon_area(own) * 1.001:
            outline = under
        if outline is None:
            warn(f"slab under {lv['id']}: no closed outer wall outline; slab not written")
            continue
        sec = by_base.get(base_id)
        thick = (sec or {}).get("thickness") or {}
        from_section = thick.get("method") not in (None, "assumed") and thick.get("value") is not None
        thickness = float(thick["value"]) if from_section else slab_default
        if not from_section:
            warn(f"slab under {lv['id']}: thickness {thickness:.2f} m assumed (brief slab_thickness)")
        openings = []
        if below_id:
            for f in furniture:
                if f["level_id"] == below_id and f["type"] == "stair":
                    fp = f["footprint"]
                    poly = G.rotated_rectangle(fp["center"], fp["size"], fp["rotation_deg"])
                    openings.append({"id": f"sv_{lv['id']}_{len(openings) + 1:02d}", "kind": "stair_void",
                                     "furniture_id": f["id"], "polygon": [[round(x, 4), round(y, 4)] for x, y in poly],
                                     "source": "derived"})
        alt_variants = [vid for vid, v in variants.items() if not v["base"] and lv["id"] in v["levels"]] \
            if lv.get("base_level_id") else []
        ev = list(thick.get("evidence") or [])
        ev.append({"file": lv["evidence"][0]["file"] if lv.get("evidence") else "", "method": "derived",
                   "confidence": 1.0, "entity": f"outline of the outer walls of {lv['id']}"
                   + (f" (larger {below_id} below)" if outline is under else ""), "region_id": lv.get("region_id")})
        out.append({"id": f"sl_{lv['id']}", "below_level_id": below_id, "above_level_id": lv["id"],
                    "z_top": float(lv["elevation"]), "thickness": round(thickness, 3),
                    "thickness_source": "section" if from_section else "assumed_default", "outline": outline,
                    "openings": openings, "variants": alt_variants,
                    "status": "verified" if from_section else "assumed", "evidence": ev})
    return out


def roof_block(sheets: dict, levels: list[dict], rooms: list[dict]) -> Optional[dict]:
    """The roof over the top level, or None when neither a section nor a plan draws it."""
    hroof = (sheets.get("heights") or {}).get("roof") or {}
    ex = (sheets.get("exterior") or {}).get("roof")
    if not ex and not hroof.get("eaves_z"):
        return None
    base = [lv for lv in levels if not lv.get("base_level_id")]
    top = max(base, key=lambda lv: lv.get("order") or 0) if base else None
    assumed = list((ex or {}).get("assumed") or [])
    roof = {"type": (ex or {}).get("type") or "other", "type_source": (ex or {}).get("type_source") or "assumed",
            "over_level_id": top["id"] if top else None,
            "eaves_height": hroof.get("eaves_z"), "ridge_height": hroof.get("ridge_z"),
            "pitches_deg": list(hroof.get("pitches_deg") or []), "overhang": hroof.get("overhang"),
            "thickness": hroof.get("thickness"), "knee_wall": hroof.get("knee_wall"),
            "outline": (ex or {}).get("outline"), "break_line": (ex or {}).get("break_line"),
            "ridge_lines": list((ex or {}).get("ridge_lines") or []), "planes": [], "openings": [],
            "covering": None, "assumed": assumed, "evidence": list((ex or {}).get("evidence") or [])}
    if not ex:
        roof["assumed"].append("roof type (no roof plan, elevation or plan roof lines)")
    if roof["outline"] is None:
        roof["assumed"].append("outline (the outer walls + overhang)")
    roof["assumed"].append("covering (from the exterior style)")
    for r in rooms:
        if top is not None and r["level_id"] == top["id"] and r.get("room_type") == "balcony":
            roof["openings"].append({"id": f"ro_{len(roof['openings']) + 1:02d}", "kind": "terrace", "room_id": r["id"],
                                     "polygon": [list(p) for p in r["polygon"]],
                                     "parapet_height": {"value": None, "method": "assumed", "confidence": 0.0,
                                                        "evidence": [], "note": "not drawn"},
                                     "source": "derived"})
    if not roof["evidence"]:
        roof["evidence"] = [e for k in ("eaves_z", "ridge_z") for e in (hroof.get(k) or {}).get("evidence") or []][:2]
    roof["status"] = "verified" if ex and roof["type_source"] != "assumed" else "assumed"
    return roof


def facade_block(sheets: dict, walls: list[dict], warn) -> dict:
    """Drawn facade faces only (no ``default``): an elevation's material on the outer walls of its side when the
    north is known; otherwise listed, not mapped."""
    ex = sheets.get("exterior") or {}
    faces = []
    for entry in ex.get("facade") or []:
        warn(f"facade: {entry['material']} on the {entry['side']} side ({entry['source']} in {entry.get('region')}) "
             f"not mapped onto walls (the elevation's side needs the north and the cut direction)")
    return {"faces": faces, "openings_seen": list(ex.get("openings_seen") or []),
            "evidence": [e for f in ex.get("facade") or [] for e in f.get("evidence") or []]}


def site_block(site: dict, sheets: dict, area_kind) -> dict:
    """The M10 site additions on top of the M7 ``site`` block (mutated and returned)."""
    heights = sheets.get("heights") or {}
    ground = heights.get("ground") or []
    levels = [{"side": g["side"] if g["side"] in ("left", "right", "front", "back", "north", "east", "south",
                                                 "west") else "all", "azimuth_deg": None, "z": g["z"]} for g in ground]
    if not levels:
        levels = [{"side": "all", "azimuth_deg": None,
                   "z": {"value": 0.0, "method": "assumed", "confidence": 0.0, "evidence": [],
                         "note": "no ground line drawn: the ground floor's level"}}]
    zs = {round(float(lv["z"]["value"]), 3) for lv in levels if lv["z"].get("value") is not None}
    site["ground"] = {"levels": levels, "terrain": "flat" if len(zs) <= 1 else "sides", "light_wells": []}
    north = (sheets.get("exterior") or {}).get("north")
    site["north_deg"] = north if north else {"value": 0.0, "method": "assumed", "confidence": 0.0, "evidence": [],
                                             "note": "no north arrow drawn: +Y taken as north"}
    for key in ("paving", "grass", "parking"):
        site.setdefault(key, [])
    for a in site.get("areas") or []:
        kind = area_kind(a.get("label") or "") or "other"
        a["kind"] = kind
        a.setdefault("build", a.get("polygon") is not None)
        target = AREA_TARGET.get(kind)
        if target and a.get("polygon") and len(a["polygon"]) >= 3:
            site[target].append({"id": f"{target}_{len(site[target]) + 1:02d}", "polygon": a["polygon"], "z": None,
                                 "material": None, "source": "plan", "build": True,
                                 "evidence": list(a.get("evidence") or [])})
    plot_walls = [w for w in site.get("boundary_walls") or [] if w.get("kind") == "plot"]
    if plot_walls and site.get("plot") is None:
        from shapely.geometry import MultiPoint
        hull = MultiPoint([tuple(p) for w in plot_walls for p in (w["start"], w["end"])]).convex_hull
        if hull.geom_type == "Polygon":
            site["plot"] = {"id": "plot", "polygon": [[round(x, 4), round(y, 4)] for x, y in
                                                      list(hull.exterior.coords)[:-1]],
                            "z": None, "material": None, "source": "plan", "build": True,
                            "evidence": [e for w in plot_walls for e in w.get("evidence") or []][:4]}
    site.setdefault("plot", None)
    return site
