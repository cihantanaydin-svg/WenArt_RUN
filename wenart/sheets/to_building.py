"""From ``sheets.json`` to the Milestone 10 blocks of ``building.json`` (docs/milestone10.md §1.1, §1.6a, §1.6b).

What: pure functions the pipeline calls in a multi-region project: ``level_fields`` (kind, variant, region,
elevation and ceiling from the section, floor to floor), ``variants_block`` (with ``rooms_changed`` and
``exterior_changed``), ``slabs_block`` (outline = the outer face of the outer walls, stair voids, thickness from the
section; a slab that differs for an alternative again as ``sl_<above>__<variant id>``), ``roof_block`` (type,
heights, outline, break line, ridge lines, profile, terrace openings; ``planes`` left empty for track E; 27 Oct
2026: a roof plan's eaves loop put on the top level's walls and checked, ``roof_outline_record``, recorded as
``roof_plan_outline`` and used as the outline when it passes),
``facade_block`` (drawn faces and one ``elevations`` entry per elevation with its ``plan_check``) and
``site_block`` (drawn ground levels per side, north, label records, plot / paving / grass / parking / trees from
the registered site plan).

Why: the sheets stage reads heights and exterior evidence once; the building JSON carries them with their evidence.
Only drawn looks are written (§1.6b row 12): every other look is resolved by the build and listed there.
"""
from __future__ import annotations

import math
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
    if any(lv.get("id") == base_id and lv.get("roof_terrace") for lv in sheets.get("levels") or []):
        level["roof_terrace"] = True              # real10: the roof terrace floor (its stair house over a flat roof)
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


def _footprint_poly(f: dict) -> Polygon:
    fp = f["footprint"]
    return Polygon(G.rotated_rectangle(fp["center"], fp["size"], fp["rotation_deg"]))


def arrival_only(f: dict, below2_id: Optional[str], above_id: str, furniture: list[dict],
                 rooms: Optional[list[dict]]) -> bool:
    """4 Nov 2026 (real17: the two shop stairs of the ground floor go down to the shops' basement stores; the first
    floor got holes for them in its bedrooms): a stair drawn on a level that is the top of the stair from the level
    under it (a stair there on at least half its footprint), with no stair over it on the level above and a room there
    (not a stair, not a void) on at least half its footprint, ends on this level: no opening in the slab above."""
    if below2_id is None or not rooms:
        return False
    fp = _footprint_poly(f)
    if fp.area <= 0:
        return False
    if not any(_footprint_poly(g).intersection(fp).area >= 0.5 * min(fp.area, _footprint_poly(g).area)
               for g in _stairs(below2_id, furniture)):
        return False
    if any(_footprint_poly(g).intersection(fp).area > 0.2 * fp.area for g in _stairs(above_id, furniture)):
        return False
    cover = 0.0
    for r in rooms:
        if r.get("level_id") != above_id or r.get("room_type") == "stair" or B.is_void_label(r.get("label")) \
                or len(r.get("polygon") or []) < 3:
            continue
        poly = Polygon(r["polygon"])
        if poly.is_valid:
            cover += poly.intersection(fp).area
    return cover >= 0.5 * fp.area


def _slab(lv: dict, below: Optional[dict], unions: dict, furniture: list[dict], sec: Optional[dict],
          slab_default: float, slab_id: str, rooms: Optional[list[dict]] = None,
          voids: Optional[list[dict]] = None, below2_id: Optional[str] = None) -> Optional[dict]:
    """The slab under ``lv`` (over ``below``): outline = the larger of the two outer-wall outlines, stair voids over
    the stairs of the level below (not over a stair that only arrives there from ``below2_id``: ``arrival_only``), and
    the voids ``lv``'s plan draws (``void_openings``)."""
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
    # 27 Oct 2026 (real06's first floor: the opening cut out the whole stair footprint, its arrival floor too, and cut
    # the arrival off from the hall): a stair with drawn flights gets the opening it needs (its flights where the
    # headroom under this slab asks for it, its half landing, its last flight up to its last riser; never its arrival:
    # ``stair_access.opening_polygon``); a stair without drawn flights keeps its footprint
    from wenart.blender import stair_access as SA
    rise = float(lv.get("elevation") or 0.0) - float(below.get("elevation") or 0.0) if below else None
    ended = []
    for f in _stairs(below_id, furniture):
        if arrival_only(f, below2_id, lv["id"], furniture, rooms):
            ended.append(f["id"])
            continue
        fp = f["footprint"]
        poly = SA.derived_opening(f, rise, rise - thickness) if rise and rise > thickness else None
        if poly is None:
            poly = [[round(x, 4), round(y, 4)] for x, y in G.rotated_rectangle(fp["center"], fp["size"],
                                                                                  fp["rotation_deg"])]
        openings.append({"id": f"sv_{slab_id[3:]}_{len(openings) + 1:03d}", "kind": "stair_void",
                         "furniture_id": f["id"], "polygon": poly, "source": "derived"})
    if below is not None:
        for o in void_openings(lv["id"], rooms or [], voids):
            openings.append(dict(o, id=f"sv_{slab_id[3:]}_{len(openings) + 1:03d}"))
    ev = list(thick.get("evidence") or [])
    ev.append(B.evidence(lv["evidence"][0]["file"] if lv.get("evidence") else "", "derived", 1.0,
                         entity=f"outline of the outer walls of {lv['id']}" + (f" (larger {below_id} below)"
                                                                                 if outline is under else ""),
                         region_id=lv.get("region_id"), rule="outer_wall_outline"))
    if ended:
        e = B.evidence(lv["evidence"][0]["file"] if lv.get("evidence") else "", "derived", 1.0,
                       entity=", ".join(ended), region_id=lv.get("region_id"), rule="stair_ends_below")
        e["reason"] = (f"the stair(s) {', '.join(ended)} of {below_id} arrive from {below2_id} and {lv['id']} draws "
                       f"rooms over them: no opening in this slab")
        ev.append(e)
    return {"id": slab_id, "below_level_id": below_id, "above_level_id": lv["id"], "z_top": float(lv["elevation"]),
            "thickness": round(thickness, 3), "thickness_source": "section" if from_section else "assumed_default",
            "outline": outline, "openings": openings, "variants": [],
            "status": "verified" if from_section else "assumed", "evidence": ev}


def void_openings(level_id: str, rooms: list[dict], voids: Optional[list[dict]] = None) -> list[dict]:
    """3 Nov 2026 (real09, user: "each duplex flat has its inner stair and a 'galeri' void over the floor below"): the
    voids the plan of ``level_id`` labels (``generic.voids``: a drawn outline around a label galeri, boşluk, void, open
    to below, Luftraum ...) and its rooms whose label means a void (``building.is_void_label``) are openings of the
    floor slab under them (kind ``void``, source ``drawn``; the build cuts them out of the floor and the ceiling below
    and guards their free edges)."""
    out = []
    for v in voids or []:
        if v.get("level_id") != level_id or len(v.get("polygon") or []) < 3:
            continue
        out.append({"kind": "void", "room_id": None, "polygon": [[round(float(x), 4), round(float(y), 4)]
                                                                 for x, y in v["polygon"]],
                    "source": "drawn", "reason": v.get("reason"), "entity": v.get("entity")})
    for r in rooms:
        if r.get("level_id") != level_id or len(r.get("polygon") or []) < 3:
            continue
        if not (B.is_void_label(r.get("label_raw")) or B.is_void_label(r.get("label"))):
            continue
        out.append({"kind": "void", "room_id": r["id"], "polygon": [[round(float(x), 4), round(float(y), 4)]
                                                                     for x, y in r["polygon"]],
                    "source": "drawn", "reason": f"the room labelled '{r.get('label_raw') or r.get('label')}' is a "
                                                 f"void over the floor below"})
    return out


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
                warn, variants: Optional[list[dict]] = None, rooms: Optional[list[dict]] = None,
                voids: Optional[list[dict]] = None) -> list[dict]:
    """One slab under every built base level (``sl_<level id>``); for each alternative, the slabs under and over its
    level again as ``sl_<above>__<variant id>`` (``variants: [id]``, level ids naming the base levels) when their
    outline or stair voids differ (an alternative's stair within 0.1 m of the base stair keeps the base slab); when the
    base level was left out, the alternative's slabs are always written (listed)."""
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
        b1 = below_of(lv)
        b2 = below_of(b1) if b1 is not None else None
        slab = _slab(lv, b1, unions, furniture, by_base.get(lv["id"]), slab_default, f"sl_{lv['id']}",
                     rooms, voids, below2_id=b2["id"] if b2 else None)
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
            if alt is None:
                continue
            if base_lv is None:
                warn(f"variant {v['id']}: base level {ch['replaces']} left out; the slabs under and over "
                     f"{alt['id']} are built from the alternative")
            alt_as_base = dict(alt, id=alt["id"])
            ref = base_lv or alt                        # the level whose order places the alternative
            above = next((b for b in base if (b.get("order") or 0) == (ref.get("order") or 0) + 1), None)
            pairs = [(f"sl_{ch['replaces']}", alt_as_base, below_of(ref), ch["replaces"])]
            if above is not None:
                pairs.append((f"sl_{above['id']}", above, alt_as_base, above["id"]))
            for base_slab_id, top, under, above_id in pairs:
                mine = _slab(top, under, unions, furniture, by_base.get(above_id), slab_default,
                             f"{base_slab_id}__{v['id']}", rooms, voids)
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

# 27 Oct 2026 (real06's roof plan drew the hip roof over the first-floor balcony; the roof was built over the outer
# walls + overhang): the roofs a roof plan draws (``exterior.roof_plan_outline``, in the roof plan's own metres) are
# put on the top level's outer walls and checked before the build uses them. Every value has a physical reason.
ROOF_FIT = {
    # a roof plan and a floor plan of one set agree to about a plaster layer: the drawn wall line (else the eaves loop
    # moved in by the overhang) lies on the top level's outer wall faces within this RMS ...
    "rms_max_m": 0.10,
    # ... along at least this share of its length (the rest: a balcony, terrace or porch the roof reaches over, piers)
    "share_min": 0.5,
    # the roof covers the top level's outer wall faces: at most this much of their plan may stick out (a pier, a few
    # cm of drawing error along a facade)
    "uncovered_max_m2": 0.5, "uncovered_max_share": 0.01,
    # eaves stand at most this far out of the walls; a roof that reaches farther covers something under it
    "overhang_max_m": 1.5,
    # ... a drawn outdoor space (a balcony, terrace, veranda, porch): its label or outline this close to that part
    "space_reach_m": 1.0,
    # a piece past the overhang smaller than this is the corner of the overhang, not a reach
    "piece_min_m2": 0.5,
    # a roof more than this many times the plan of the walls under it is no roof of this building (a plot line)
    "area_max_ratio": 3.0,
    # the overhangs tried when the roof plan draws no wall line and no section gives the overhang (usual eaves)
    "overhang_tries_m": (0.3, 0.4, 0.5, 0.6, 0.75, 1.0),
}


def _space_anchors(site: Optional[dict], rooms: list[dict], level_ids: set) -> list[tuple[str, object]]:
    """``[(id, shapely geometry)]`` of the drawn outdoor spaces of ``level_ids``: labelled site areas whose label
    names one (``wenart.levels.outdoor.space_kind``: their outline, else their label point) and balcony or terrace
    rooms (pure apart from shapely)."""
    from shapely.geometry import Point
    from wenart.levels import outdoor as OD

    out = []
    for a in (site or {}).get("areas") or []:
        if not isinstance(a, dict) or (a.get("level_id") not in level_ids and a.get("level_id") is not None):
            continue
        if OD.space_kind(a.get("label_raw") or a.get("label")) is None:
            continue
        poly = a.get("polygon") or ((a.get("outline_inferred") or {}).get("polygon")
                                    if isinstance(a.get("outline_inferred"), dict) else None)
        if poly and len(poly) >= 3 and Polygon(poly).is_valid:
            out.append((str(a.get("id")), Polygon(poly)))
        elif a.get("anchor"):
            out.append((str(a.get("id")), Point(a["anchor"])))
    for r in rooms:
        if r.get("level_id") in level_ids and r.get("room_type") in ("balcony", "terrace") \
                and len(r.get("polygon") or []) >= 3:
            out.append((str(r["id"]), Polygon(r["polygon"])))
    return out


def roof_outline_record(plan: dict, walls: list[dict], level_id: str, site: Optional[dict] = None,
                        rooms: Optional[list[dict]] = None, overhang: Optional[float] = None,
                        levels: Optional[list[dict]] = None) -> dict:
    """The roof plan's roofs put on the building (pure apart from shapely; ``ROOF_FIT``).

    How: the drawn wall line of the roof plan (else its eaves loop moved in by ``overhang``, else by each of
    ``overhang_tries_m``) is fitted onto the outer wall faces of ``level_id`` (``geom2d.wall_outline``) by the trimmed
    ICP of the plan registration (``register.fit_ring``: 0/90/180/270 degrees); the eaves loop and every other roof
    move with it. The eaves loop is used as the roof's outline when: the fit is close (``rms_max_m`` along at least
    ``share_min`` of the line); it covers the outer wall faces (``uncovered_max_*``); it is not much larger than the
    walls' plan (``area_max_ratio``); and every part of it farther than ``overhang_max_m`` from the walls covers a drawn
    outdoor space of the level or one below (``space_reach_m``: the balcony a roof plan draws the roof over). Else the
    reason is given and the build keeps the walls + overhang (assumed).

    ``{"region_id", "used", "reason", "points" (building metres, None when not placed), "others": [{"points",
    "area_m2", "touches_main", "layers", "entities"}], "fit": {"rotation_deg", "shift", "rms_m", "within_m", "line"},
    "reaches": [{"area_m2", "spaces"}], "min_overhang_m", "drawn_overhang_m", "evidence", "note"}``."""
    from shapely.geometry import Polygon as SPolygon

    from wenart.blender import geom2d
    from wenart.sheets import register as RG

    cfg = ROOF_FIT
    rec = {"region_id": plan.get("region_id"), "used": False, "reason": None, "points": None, "others": [],
           "fit": None, "reaches": [], "min_overhang_m": None, "drawn_overhang_m": plan.get("overhang_m"),
           "evidence": [dict(e, rule="roof_plan_outline") for e in plan.get("evidence") or []],
           "note": plan.get("note")}
    wall_line, _how = geom2d.wall_outline([w for w in walls if w.get("level_id") == level_id])
    if len(wall_line) < 3:
        rec["reason"] = f"no outer walls of {level_id} to put the roof plan on"
        return rec
    ref = SPolygon(wall_line)
    eaves = SPolygon(plan["points"])
    if not eaves.is_valid or eaves.area <= 0:
        rec["reason"] = "the roof plan's eaves loop is no valid polygon"
        return rec
    tries = []
    if plan.get("wall_line"):
        tries.append((SPolygon(plan["wall_line"]), "the drawn wall line"))
    offsets = [] if tries else ([overhang] if overhang else []) + list(cfg["overhang_tries_m"])
    for d in offsets:
        moved_in = eaves.buffer(-float(d), join_style=2)
        if moved_in.geom_type == "Polygon" and not moved_in.is_empty:
            tries.append((moved_in, f"the eaves loop {float(d):.2f} m in"))
    best = None
    for poly, what in tries:
        fit = RG.fit_ring(poly, ref)
        if best is None or fit["rms_m"] < best[0]["rms_m"]:
            best = (fit, what)
    if best is None:
        rec["reason"] = "nothing of the roof plan to fit on the walls"
        return rec
    fit, what = best
    rec["fit"] = dict(fit, line=what, within_m={str(k): v for k, v in fit["within_m"].items()})
    if fit["rms_m"] > cfg["rms_max_m"] or fit["within_m"][0.10] < cfg["share_min"]:
        rec["reason"] = (f"{what} of {plan.get('region_id')} does not fit on the outer walls of {level_id} (RMS "
                         f"{fit['rms_m']:.2f} m, {fit['within_m'][0.10]:.0%} of it within 0.10 m; needs "
                         f"{cfg['rms_max_m']:.2f} m along {cfg['share_min']:.0%})")
        return rec
    th = math.radians(fit["rotation_deg"])
    ca, sa = math.cos(th), math.sin(th)
    tx, ty = fit["shift"]

    def place(pts: list) -> list:
        return [[round(ca * x - sa * y + tx, 4) + 0.0, round(sa * x + ca * y + ty, 4) + 0.0] for x, y in pts]

    rec["points"] = place(plan["points"])
    rec["others"] = [dict({k: o.get(k) for k in ("area_m2", "touches_main", "layers", "entities", "hip_lines")},
                          points=place(o["points"])) for o in plan.get("others") or []]
    roof_poly = SPolygon(rec["points"])
    over = roof_poly.exterior.distance(ref.exterior) if roof_poly.contains(ref) else None
    rec["min_overhang_m"] = round(over, 3) if over is not None else None       # the least eaves-to-wall distance
    uncovered = ref.difference(roof_poly).area
    if uncovered > max(cfg["uncovered_max_m2"], cfg["uncovered_max_share"] * ref.area):
        rec["reason"] = (f"placed on the walls, the roof plan's eaves loop leaves {uncovered:.2f} m2 of the outer "
                         f"walls of {level_id} uncovered")
        return rec
    if roof_poly.area > cfg["area_max_ratio"] * ref.area:
        rec["reason"] = (f"the roof plan's eaves loop ({roof_poly.area:.1f} m2) is more than "
                         f"{cfg['area_max_ratio']:g} times the plan of the walls of {level_id} ({ref.area:.1f} m2)")
        return rec
    order = {lv["id"]: float(lv.get("elevation") or 0.0) for lv in levels or []}
    top_z = order.get(level_id)
    under = {lid for lid, z in order.items() if top_z is None or z <= top_z + 1e-6} | {level_id}
    spaces = _space_anchors(site, rooms or [], under)
    far = roof_poly.difference(ref.buffer(cfg["overhang_max_m"], join_style=2))
    lost = []
    for piece in getattr(far, "geoms", [far]):
        if piece.is_empty or piece.area < cfg["piece_min_m2"]:
            continue
        near = sorted({sid for sid, g in spaces if g.distance(piece) <= cfg["space_reach_m"]})
        rec["reaches"].append({"area_m2": round(piece.area, 3), "spaces": near})
        if not near:
            lost.append(piece.area)
    if lost:
        rec["reason"] = (f"placed on the walls, the roof plan's eaves loop reaches more than "
                         f"{cfg['overhang_max_m']:.1f} m past the walls of {level_id} over {sum(lost):.2f} m2 where no "
                         f"balcony, terrace, veranda or porch is drawn")
        return rec
    rec["used"] = True
    rec["note"] = (plan.get("note") or "") + (f"; put on the outer walls of {level_id} by {what} (RMS "
                                              f"{fit['rms_m']:.3f} m, turned {fit['rotation_deg']:.0f} deg)")
    return rec


def roof_block(sheets: dict, levels: list[dict], rooms: list[dict], walls: Optional[list[dict]] = None,
               shift: Shift = (0.0, 0.0), site: Optional[dict] = None, terrace: Optional[dict] = None) -> Optional[dict]:
    """The roof over the top level, or None when neither a section nor a plan draws it (the build then makes a flat
    roof over the top level, assumed). 27 Oct 2026: a roof plan's eaves loop becomes the outline when it fits the top
    level's walls (``roof_outline_record``; ``site``: the drawn outdoor spaces a roof may reach over); the record is
    ``roof_plan_outline``."""
    heights = sheets.get("heights") or {}
    hroof = heights.get("roof") or {}
    ex = (sheets.get("exterior") or {}).get("roof")
    base = [lv for lv in levels if not lv.get("base_level_id")]
    top = max(base, key=lambda lv: lv.get("order") or 0) if base else None
    if top is not None and top.get("roof_terrace") and terrace is not None:
        # real10 (1 Nov 2026): a roof terrace floor on top: a flat roof over its stair house only (the terrace is
        # open, its edge a parapet); the section's roof lines are the parapet and the stair house, no pitched roof.
        z = round(float(top["elevation"]) + float(terrace["house_height"]), 3)
        src = terrace["sources"]["house_height"]
        ev = [dict(e) for e in (top.get("evidence") or [])[:1]]
        val = {"value": z, "method": "vector" if src == "level_mark" and ev else "assumed",
               "confidence": 0.9 if src == "level_mark" and ev else 0.0, "evidence": ev if src == "level_mark" else [],
               "note": "the stair house's roof on the roof terrace floor"
                       + (" (the section's level marks)" if src == "level_mark" else " (the level's ceiling height)")}
        return {"type": "flat", "type_source": "roof_plan", "over_level_id": top["id"], "eaves_height": val,
                "ridge_height": dict(val), "pitches_deg": [], "overhang": None, "thickness": None,
                "knee_wall": None, "profile": None, "outline": terrace["outline"], "outline_source": "roof_terrace",
                "break_line": None, "ridge_lines": [], "planes": [], "openings": [], "covering": None,
                "covering_colour": None, "covering_source": None,
                "assumed": [] if src == "level_mark" else ["stair house height (the level's ceiling height)"],
                "evidence": [e for lv in [top] for e in (lv.get("evidence") or [])[:1]],
                "roof_terrace": {"parapet_height": terrace["parapet_height"], "sources": terrace["sources"]},
                "status": "verified" if src == "level_mark" else "assumed"}
    if not ex and not hroof.get("eaves_z"):
        return None
    assumed = list((ex or {}).get("assumed") or [])
    profile = None
    axis = heights.get("cut_axis")
    if hroof.get("profile"):
        # s runs from the building's min outer wall face along the axis: the core's frame already (no shift).
        profile = {"region_id": (heights.get("section_regions") or [None])[0], "cut_axis": axis,
                   "points": [[p[0], p[1]] for p in hroof["profile"]], "method": "vector"}
    # A ridge read from the section: its position along the cut axis is a profile s (no shift); its ends come from
    # the roof outline (the sheets frame: shifted).
    across = (0.0, shift[1]) if axis == "x" else (shift[0], 0.0) if axis == "y" else shift
    roof = {"type": (ex or {}).get("type") or "other", "type_source": (ex or {}).get("type_source") or "assumed",
            "over_level_id": top["id"] if top else None,
            "eaves_height": hroof.get("eaves_z"), "ridge_height": hroof.get("ridge_z"),
            "pitches_deg": list((ex or {}).get("pitches_deg") or hroof.get("pitches_deg") or []),
            "overhang": hroof.get("overhang"),
            "thickness": hroof.get("thickness"), "knee_wall": hroof.get("knee_wall"), "profile": profile,
            "outline": moved((ex or {}).get("outline"), shift),
            "break_line": moved((ex or {}).get("break_line"), shift),
            "ridge_lines": [moved(r, across) for r in (ex or {}).get("ridge_lines") or []], "planes": [],
            "openings": [],
            "covering": (ex or {}).get("covering"), "covering_colour": None,
            "covering_source": (ex or {}).get("covering_source") if (ex or {}).get("covering") else None,
            "assumed": assumed, "evidence": list((ex or {}).get("evidence") or [])}
    if not ex:
        roof["assumed"].append("roof type (no roof plan, elevation or plan roof lines)")
    why_not = None
    plan = (ex or {}).get("plan_outline")
    if isinstance(plan, dict) and plan.get("points") and top is not None:
        # 27 Oct 2026: the roof plan's own outline (its eaves loop, the balcony or porch it reaches over), put on the
        # top level's walls; the drawn outline of the top plan (roof_from_plan) stays first
        rec = roof_outline_record(plan, walls or [], top["id"], site, rooms, _value_of(hroof.get("overhang")), levels)
        roof["roof_plan_outline"] = rec
        if roof["outline"] is None and rec["used"]:
            roof["outline"], roof["outline_source"] = rec["points"], "roof_plan"
            roof["evidence"] = list(roof["evidence"]) + rec["evidence"]
        elif roof["outline"] is None:
            why_not = rec["reason"]
    elif (ex or {}).get("plan_outline_note"):
        why_not = ex["plan_outline_note"]
        roof["roof_plan_outline"] = {"region_id": None, "used": False, "reason": why_not, "points": None,
                                     "others": [], "evidence": []}
    if roof["outline"] is None:
        roof["assumed"].append("outline (the outer walls + overhang)" + (f": {why_not}" if why_not else ""))
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


ROOF_TERRACE_PARAPET_M = 1.10      # real10: a roof terrace's parapet when no mark gives it (assumed)
# 4 Nov 2026 (real10, user: "Too much wall on top a little wall with handrails should have been enough"): a roof
# terrace's parapet is a low wall with a handrail on it up to the guard height (the section's mark or more)
PARAPET_LOW_M = 0.50               # the low wall ...
GUARD_TOP_M = 1.10                 # ... and the top of the handrail on it, at least


def _guarded(w: dict, top_m: float, source: str) -> None:
    """A parapet wall as a ``PARAPET_LOW_M`` low wall with a handrail on it to ``top_m`` (``guard``)."""
    w["height"] = round(min(float(w.get("height") or PARAPET_LOW_M), PARAPET_LOW_M), 3)
    w["guard"] = {"top_m": round(max(float(top_m), GUARD_TOP_M), 3), "kind": "handrail", "source": source}
HOUSE_REACH_M = 0.40               # a wall within this of the top level's rooms belongs to the stair house


def roof_terrace(b: dict, sheets: dict, warn) -> Optional[dict]:
    """real10 (1 Nov 2026): the top level is a roof terrace floor (``roof_terrace``): its rooms (the stair house:
    stair, lift, machine room) keep full walls under a flat roof at the stair house's height; every other wall of
    the level stands on the terrace's edge: a parapet (``height`` = the section's parapet mark, else
    ``ROOF_TERRACE_PARAPET_M`` assumed; ``parapet: true``). Returns ``{"level_id", "outline", "house_height",
    "parapet_height", "sources"}`` for the roof, or None."""
    from shapely.geometry import LineString
    from shapely.ops import unary_union

    top = next((lv for lv in b.get("levels") or [] if lv.get("roof_terrace") and not lv.get("base_level_id")), None)
    if top is None:
        return None
    rt = (sheets.get("heights") or {}).get("roof_terrace") or {}
    rooms = [Polygon(r["polygon"]) for r in b.get("rooms") or [] if r["level_id"] == top["id"]
             and len(r.get("polygon") or []) >= 3]
    house = unary_union([r.buffer(HOUSE_REACH_M, join_style=2) for r in rooms]) if rooms else None
    parapet = rt.get("parapet_height")
    house_h = rt.get("house_height")
    n_par = 0
    for w in b.get("walls") or []:
        if w["level_id"] != top["id"]:
            continue
        if house is not None and LineString([w["start"], w["end"]]).within(house):
            if house_h is not None:
                w["height"] = round(float(house_h), 3)
            continue
        w["height"] = round(float(parapet if parapet is not None else ROOF_TERRACE_PARAPET_M), 3)
        w["parapet"] = True
        _guarded(w, w["height"], "section mark" if parapet is not None else "assumed")
        n_par += 1
    # 4 Nov 2026 (real10, user: "If nothing is built in the last floor roof etc, putting a bit parapet would be nice so
    # people on the last floor can walk safely"): the terrace plan drew only three short parapet pieces, the edge stood
    # open; where no wall of the top level stands on the edge of the floor below, a parapet is inferred along it
    edge = _edge_parapets(b, top, float(parapet if parapet is not None else ROOF_TERRACE_PARAPET_M),
                          "section mark" if parapet is not None else "assumed")
    if house_h is not None:
        top["ceiling_height"] = round(float(house_h), 3)
        top["ceiling_height_source"] = "section"
    outline = None
    if house is not None and not house.is_empty:
        main = max(getattr(house, "geoms", [house]), key=lambda g: g.area)
        shrunk = main.buffer(-HOUSE_REACH_M + 0.15, join_style=2)        # to the house walls' outer faces
        main = shrunk if not shrunk.is_empty else main
        outline = [[round(x, 4) + 0.0, round(y, 4) + 0.0] for x, y in list(main.exterior.coords)[:-1]]
    sources = {"parapet_height": "level_mark" if parapet is not None else "assumed",
               "house_height": "level_mark" if house_h is not None else "assumed"}
    if edge:
        warn(f"roof terrace {top['id']}: {edge} parapet piece(s) inferred along the terrace's open edge (the outer walls "
             f"of the floor below), {parapet if parapet is not None else ROOF_TERRACE_PARAPET_M:.2f} m high, so the "
             f"terrace is safe to walk on")
    warn(f"roof terrace {top['id']}: {n_par} wall(s) on the terrace's edge are parapets "
         f"{parapet if parapet is not None else ROOF_TERRACE_PARAPET_M:.2f} m high "
         f"({'section mark' if parapet is not None else 'assumed'}); the stair house "
         f"({len(rooms)} room(s)) keeps full walls under a flat roof"
         + (f" {house_h:.2f} m above the terrace (section mark)" if house_h is not None else ""))
    return {"level_id": top["id"], "outline": outline,
            "house_height": float(house_h) if house_h is not None else float(top["ceiling_height"]),
            "parapet_height": float(parapet if parapet is not None else ROOF_TERRACE_PARAPET_M), "sources": sources}


EDGE_PARAPET_MIN_M = 0.30          # an open stretch of the terrace's edge shorter than this needs no parapet piece
EDGE_COVERED_M = 0.30              # a top-level wall this close to the edge already stands on it
EDGE_PARAPET_T_M = 0.20            # an inferred parapet's thickness (at most the outer walls')
EDGE_SIMPLIFY_M = 0.05             # the edge's jogs from outer walls of different thickness are straightened this much
EDGE_CORNER_MIN_M = 0.05           # a whole edge of the outline this short still gets its piece (the corners stay closed)


def _edge_parapets(b: dict, top: dict, height: float, source: str) -> int:
    """4 Nov 2026: parapet walls (``parapet: true``, inferred) along the open stretches of a roof terrace's edge: the
    centre line of the outer walls of the highest level below that has walls, less where a wall of the top level
    stands within ``EDGE_COVERED_M``. Returns the number of pieces added to ``b["walls"]``."""
    import statistics
    from shapely.geometry import LineString
    from shapely.ops import unary_union

    below = []
    for lv in sorted((lv for lv in b.get("levels") or [] if lv.get("order") is not None
                      and lv["order"] < (top.get("order") or 0)), key=lambda lv: -lv["order"]):
        below = [w for w in b.get("walls") or [] if w["level_id"] == lv["id"] and w["start"] != w["end"]]
        if below:
            break
    if not below:
        return 0
    u = unary_union([LineString([w["start"], w["end"]]).buffer(float(w.get("thickness") or 0.2) / 2.0, cap_style=2,
                                                                 join_style=2) for w in below])
    u = u.buffer(0.02, join_style=2).buffer(-0.02, join_style=2)
    parts = [g for g in getattr(u, "geoms", [u]) if not g.is_empty]
    if not parts:
        return 0
    filled = Polygon(max(parts, key=lambda g: Polygon(g.exterior).area).exterior)
    outer = [float(w["thickness"]) for w in below if w.get("exterior") and w.get("thickness")]
    t_out = statistics.median(outer) if outer else 0.25
    ring = filled.buffer(-t_out / 2.0, join_style=2)
    if ring.is_empty:
        return 0
    ring = max(getattr(ring, "geoms", [ring]), key=lambda g: g.area).simplify(EDGE_SIMPLIFY_M)
    own = [LineString([w["start"], w["end"]]) for w in b.get("walls") or []
           if w["level_id"] == top["id"] and w["start"] != w["end"]]
    covered = unary_union([ln.buffer(EDGE_COVERED_M) for ln in own]) if own else None
    pts = list(ring.exterior.coords)
    n = 0
    for a, c in zip(pts, pts[1:]):
        seg = LineString([a, c])
        rest = seg.difference(covered) if covered is not None else seg
        whole = abs(rest.length - seg.length) < 1e-6
        for piece in getattr(rest, "geoms", [rest]):
            # a whole edge of the ring keeps the parapet closed round its corners; a stretch left between walls of the
            # top level needs ``EDGE_PARAPET_MIN_M``
            if piece.is_empty or piece.length < (EDGE_CORNER_MIN_M if whole else EDGE_PARAPET_MIN_M):
                continue
            (x0, y0), (x1, y1) = piece.coords[0], piece.coords[-1]
            n += 1
            b["walls"].append({
                "id": f"w_{top['id']}_edge_parapet_{n:03d}", "level_id": top["id"],
                "start": [round(x0, 4) + 0.0, round(y0, 4) + 0.0], "end": [round(x1, 4) + 0.0, round(y1, 4) + 0.0],
                "thickness": round(min(t_out, EDGE_PARAPET_T_M), 3), "height": round(min(height, PARAPET_LOW_M), 3),
                "exterior": True,
                "status": "unverified", "parapet": True,
                "guard": {"top_m": round(max(float(height), GUARD_TOP_M), 3), "kind": "handrail", "source": source},
                "evidence": [B.evidence("building.json", "inferred", 0.6, rule="roof_terrace_edge_parapet",
                                        text=f"the terrace's edge over the outer walls of the floor below stands "
                                             f"open: a {min(height, PARAPET_LOW_M):.2f} m low wall with a handrail "
                                             f"to {max(height, GUARD_TOP_M):.2f} m ({source}) so the terrace is safe "
                                             f"to walk on")]})
    return n


def _value_of(entry) -> Optional[float]:
    v = entry.get("value") if isinstance(entry, dict) else entry
    try:
        return None if v is None else float(v)
    except (TypeError, ValueError):
        return None


def terrace_opening(room: dict, walls: list[dict], outline: Optional[list]) -> tuple[list, list]:
    """A roof terrace's opening in the roof (§1.6b row 13): the room's box grown over the walls around it, to the roof
    outline across an exterior wall (its parapet) and to the centre line of an inner wall; ``(polygon,
    parapet_wall_ids)``. A room with only axis-parallel edges that is not a rectangle (real02's L-shaped terraces) moves
    the vertices on its box sides the same way (a wall along an inner edge is not crossed); any other room keeps its
    polygon (the parapets still listed)."""
    from shapely.geometry import LineString
    poly = Polygon(room["polygon"])
    b = list(poly.bounds)
    rect = abs(poly.area - (b[2] - b[0]) * (b[3] - b[1])) <= 0.01 * max(poly.area, 1e-9)
    pts = [tuple(p) for p in room["polygon"]]
    rectilinear = all(abs(p[0] - q[0]) <= 1e-6 or abs(p[1] - q[1]) <= 1e-6 for p, q in zip(pts, pts[1:] + pts[:1]))
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
        if rect:
            side = (0 if c < b[0] + 1e-9 or abs(c - b[0]) <= reach else 2) if vertical else \
                (1 if c < b[1] + 1e-9 or abs(c - b[1]) <= reach else 3)
        else:
            lo, hi = (0, 2) if vertical else (1, 3)
            side = lo if abs(c - b[lo]) <= reach else hi if abs(c - b[hi]) <= reach else None
        if w.get("exterior"):
            parapets.append(w["id"])
        if side is None:
            continue                                     # a wall along an inner edge of the room: not crossed
        if w.get("exterior"):
            if ob is not None:
                grown[side] = ob[side]
            else:
                grown[side] = c - w["thickness"] / 2.0 if side in (0, 1) else c + w["thickness"] / 2.0
        else:
            grown[side] = c
    if not rect:
        if not rectilinear:
            return [list(p) for p in room["polygon"]], parapets

        def moved(v, lo, hi):
            return grown[lo] if abs(v - b[lo]) <= 1e-6 else grown[hi] if abs(v - b[hi]) <= 1e-6 else v

        return [[round(moved(x, 0, 2), 4) + 0.0, round(moved(y, 1, 3), 4) + 0.0] for x, y in pts], parapets
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
        if entry["material"] == "hatched":
            # An unlabelled hatch names no material: listed (unverified), not a face.
            warn(f"facade: an unlabelled hatch on the {entry['side']} side ({entry.get('region')}, z "
                 f"{entry.get('z_range')}) names no material: not written (unverified)")
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
    out["hedges"] = [dict(x, polyline=moved(x["polyline"], shift)) for x in sp.get("hedges") or []]   # M13 (T6)
    out["pools"] = [dict(x, polygon=moved(x["polygon"], shift)) for x in sp.get("pools") or []]
    out["buildings"] = [moved_copy(c, shift) for c in sp.get("buildings") or []] or sp.get("buildings")
    out["plot_walls"] = [dict(x, start=moved([x["start"]], shift)[0], end=moved([x["end"]], shift)[0])
                         for x in sp.get("plot_walls") or []]
    out["labels"] = [dict(x, point=moved([x["point"]], shift)[0] if x.get("point") else None)
                     for x in sp.get("labels") or []]
    return out


def moved_copy(copy: dict, shift: Shift) -> dict:
    """A building copy (``sheets.buildings``) in a frame moved by ``shift`` (``p' = p - shift``): its footprint moves;
    its map ``p -> R p + t`` becomes ``p' -> R p' + (t + R shift - shift)``."""
    a = math.radians(float(copy.get("rotation_deg") or 0.0))
    rs = (math.cos(a) * shift[0] - math.sin(a) * shift[1], math.sin(a) * shift[0] + math.cos(a) * shift[1])
    t = copy.get("translate") or [0.0, 0.0]
    return dict(copy, footprint=moved(copy.get("footprint"), shift),
                translate=[round(t[0] + rs[0] - shift[0], 4) + 0.0, round(t[1] + rs[1] - shift[1], 4) + 0.0])


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
    # 11 Oct 2026 (real04): the pools of the site plan and every copy of the building on the plot.
    pools = site.setdefault("pools", [])
    for k, item in enumerate(sp.get("pools") or []):
        pools.append({"id": f"pool_{k + 1:03d}", "polygon": [list(p) for p in item["polygon"]], "label": item.get("label"),
                      "depth": {"value": 1.5, "method": "assumed", "confidence": 0.0, "evidence": [],
                                "note": "no pool section drawn: a 1.5 m deep pool assumed"},
                      "source": "site_plan", "build": True, "evidence": list(item["evidence"])})
    if sp.get("buildings"):
        site["buildings"] = [dict(c) for c in sp["buildings"]]
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
    # Milestone 13 (T6, §13.2): the hedge rows of wenart.sheets.exterior.hedge_rows (their symbols are no longer
    # single trees) as site.hedges.
    if sp.get("hedges"):
        site["hedges"] = [dict(h) for h in sp["hedges"]]
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
