"""The elevation check (docs/milestone10.md §3.3 item 4): the building against the drawn elevations and the section.

What: ``elevation_check`` compares, per drawn elevation (``building.facade.elevations[]``, else the
``exterior.openings_seen`` of ``sheets.json``):

- the **window and door count** of the building JSON on the outer walls that face the elevation's side with the
  count the elevation draws;
- their **positions**: the x of each opening along the facade seen from outside (from its left end), and its
  sill and head in building z, against the elevation's ``positions_m``. A common x offset (the drawn outline may
  include the roof overhang) and a common z offset (an elevation without a level mark takes its lowest long line
  as the ground, z 0.00 assumed) are estimated and listed; a mirrored order (the facade read from the wrong side)
  is tried and listed;
- the **built eaves and ridge heights** (the roof object of the scene manifest: the lowest and highest point of
  its planes) against the section (``sheets.json`` ``heights.roof.eaves_z`` / ``ridge_z``, else ``building.roof``;
  the record says which one it used).

Why: the vision check of an exterior view says what the render shows; this check says whether the building the
render was made from still agrees with the elevations and the section the documents gave. It is deterministic
(no model), so a disagreement is a finding of the documents or the reading, listed in the report, never fixed.

How: pure Python on the JSON files (no render, no model); ``wenart.blender.shell`` and ``site`` (pure) give the
opening heights and the compass sides. An elevation without a side or a view bearing, or without outer walls
facing it, is ``not_checked`` with the reason. A value that is ``assumed`` in the building (a roof height no
section gave) is ``not_checked``: there is nothing drawn to compare with. Tolerances: ``check.yaml:
elevation``.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Optional

SIDE_ANGLE_DEG = 45.0
TOL_X_M = 0.35
TOL_Z_M = 0.25
MAX_OFFSET_M = 1.0
ROOF_TOL_M = 0.05
Z_OFFSET_NOTE_M = 0.05                 # a common vertical offset of the drawn heights is listed from this size


def sheets_path(project_out) -> Optional[Path]:
    """``sheets.json`` of a project output (a variant's sub-output reads the base project's)."""
    out = Path(project_out).resolve()
    candidates = [out / "sheets.json"]
    if out.parent.name == "variants":
        candidates.append(out.parent.parent / "sheets.json")
    return next((c for c in candidates if c.is_file()), None)


def load_sheets(project_out) -> Optional[dict]:
    path = sheets_path(project_out)
    return json.loads(path.read_text(encoding="utf-8")) if path is not None else None


# --------------------------------------------------------------------------
# Matching (pure)
# --------------------------------------------------------------------------

def _median(values: list) -> float:
    v = sorted(values)
    n = len(v)
    if not n:
        return 0.0
    return v[n // 2] if n % 2 else (v[n // 2 - 1] + v[n // 2]) / 2.0


def _offset(drawn: list, built: list) -> float:
    """The common x offset (drawn - built): the median over the rank-paired openings of each kind."""
    diffs = []
    for kind in ("window", "door"):
        d = sorted(p["x"] for p in drawn if p["kind"] == kind)
        b = sorted(p["x"] for p in built if p["kind"] == kind)
        diffs.extend(x - y for x, y in zip(d, b))
    return _median(diffs)


def _offset_z(drawn: list, built: list) -> float:
    """The common z offset (drawn - built): the median of the sill (else head) differences of the openings paired
    by their order along the facade, per kind. A drawn ground at z 0.00 (assumed) shifts every opening alike."""
    diffs = []
    for kind in ("window", "door"):
        d = sorted((p for p in drawn if p["kind"] == kind), key=lambda p: p["x"])
        b = sorted((p for p in built if p["kind"] == kind), key=lambda p: p["x"])
        for p, q in zip(d, b):
            key = "sill" if p.get("sill") is not None and q.get("sill") is not None else "head"
            if p.get(key) is not None and q.get(key) is not None:
                diffs.append(p[key] - q[key])
    return _median(diffs)


def _greedy(drawn: list, built: list, offset: float, tol_x: float, tol_z: float,
            offset_z: float = 0.0) -> tuple[list, list, list]:
    free = list(range(len(built)))
    pairs, missing = [], []
    for i, d in sorted(enumerate(drawn), key=lambda it: it[1]["x"]):
        best, best_dx = None, None
        for j in free:
            b = built[j]
            if b["kind"] != d["kind"]:
                continue
            dx = d["x"] - (b["x"] + offset)
            if abs(dx) > tol_x:
                continue
            dz = max((abs(d[k] - offset_z - b[k]) for k in ("sill", "head")
                      if d.get(k) is not None and b.get(k) is not None), default=0.0)
            if dz > tol_z:
                continue
            if best is None or abs(dx) < abs(best_dx):
                best, best_dx = (j, dz), dx
        if best is None:
            missing.append(i)
        else:
            free.remove(best[0])
            pairs.append({"drawn": i, "built": best[0], "dx": round(best_dx, 3), "dz": round(best[1], 3)})
    return pairs, missing, free


def match_openings(drawn: list, built: list, tol_x: float = TOL_X_M, tol_z: float = TOL_Z_M) -> dict:
    """Match the drawn openings of an elevation with the built ones (pure).

    Items are ``{"kind": window|door, "x", "sill", "head"}``. Tries the order as it is and mirrored (x -> -x) and
    keeps the one that matches more; returns ``{"matched", "missing_in_building" (drawn, no building opening),
    "extra_in_building", "offset_x_m", "offset_z_m", "mirrored", "max_dx_m", "max_dz_m"}`` (the max values after the
    common offsets)."""
    best = None
    for mirrored in (False, True):
        b = [dict(p, x=-p["x"]) for p in built] if mirrored else [dict(p) for p in built]
        off = _offset(drawn, b)
        off_z = _offset_z(drawn, b)
        pairs, missing, free = _greedy(drawn, b, off, tol_x, tol_z, off_z)
        key = (len(pairs), 0 if mirrored else 1, -abs(off))
        if best is None or key > best[0]:
            best = (key, mirrored, off, pairs, missing, free, off_z)
    _key, mirrored, off, pairs, missing, free, off_z = best
    return {"matched": len(pairs), "missing_in_building": [drawn[i] for i in missing],
            "extra_in_building": [built[j] for j in sorted(free)], "offset_x_m": round(off, 3),
            "offset_z_m": round(off_z, 3),
            "mirrored": bool(mirrored and pairs), "max_dx_m": max((abs(p["dx"]) for p in pairs), default=0.0),
            "max_dz_m": max((p["dz"] for p in pairs), default=0.0)}


# --------------------------------------------------------------------------
# The building's openings on a facade
# --------------------------------------------------------------------------

def facing(outward, out_dir) -> bool:
    return (outward[0] * out_dir[0] + outward[1] * out_dir[1]) >= math.cos(math.radians(SIDE_ANGLE_DEG))


def elevation_out(elev: dict, north: float) -> tuple[Optional[tuple], str]:
    """``(outward unit vector of the facade, how)``: from the elevation's ``view_bearing_deg`` (the viewer looks
    along it, so the facade faces the opposite way), else from its compass or drawing-relative ``side``."""
    from wenart.blender import site

    b = elev.get("view_bearing_deg")
    if isinstance(b, (int, float)) and not isinstance(b, bool):
        a = math.radians(float(b))
        return (-math.cos(a), -math.sin(a)), "view_bearing_deg"
    d = site.side_direction(elev.get("side"), north)
    return (d, "side") if d is not None else (None, "none")


def facade_openings(vb: dict, out_dir, sc_openings: dict) -> tuple[list, Optional[float]]:
    """``([{"id", "kind", "x", "sill", "head", "wall_id", "level_id"}], x_left)``: the outer openings of ``vb``
    facing ``out_dir``, ``x`` measured to the right seen from outside from the facade's left end (the leftmost
    end of the outer walls that face that way); ``x_left`` is None when no outer wall faces that way."""
    from wenart.blender.shell import opening_centre_on_wall, opening_vertical

    view = (-out_dir[0], -out_dir[1])
    right = (view[1], -view[0])                              # the viewer's right-hand side
    walls = {w["id"]: w for w in vb.get("walls") or []}
    levels = {lv["id"]: lv for lv in vb.get("levels") or []}
    from wenart.vision_check import exterior as EXT
    outer_walls = EXT.outer_wall_sides(vb, {"north": 0.0, "north_known": False})
    ends = []
    for wid, (outward, _side) in outer_walls.items():
        if not facing(outward, out_dir):
            continue
        w = walls[wid]
        ends += [float(p[0]) * right[0] + float(p[1]) * right[1] for p in (w["start"], w["end"])]
    if not ends:
        return [], None
    x_left = min(ends)
    items = []
    for oid, info in sc_openings.items():
        if not facing(info["outward"], out_dir):
            continue
        o = next((q for q in vb.get("openings") or [] if q.get("id") == oid), None)
        wall, level = walls.get(info["wall_id"]), levels.get(info["level_id"])
        if o is None or wall is None or level is None:
            continue
        cx, cy, _ = opening_centre_on_wall(o, wall)
        above = any(float(lv["elevation"]) > float(level["elevation"]) for lv in vb.get("levels") or [])
        bottom, top, _ = opening_vertical(o, level, above)
        items.append({"id": oid, "kind": o["type"], "x": round(cx * right[0] + cy * right[1] - x_left, 3),
                      "sill": round(bottom, 3), "head": round(top, 3), "wall_id": wall["id"],
                      "level_id": level["id"]})
    return sorted(items, key=lambda p: (p["x"], p["sill"])), x_left


def drawn_elevations(building: dict, sheets: Optional[dict]) -> tuple[list[dict], str]:
    """``(elevations, source)``: ``building.facade.elevations`` when it has entries, else the sheets' ``exterior``
    ``openings_seen`` (keys renamed to the building's)."""
    ev = [e for e in (building.get("facade") or {}).get("elevations") or [] if isinstance(e, dict)]
    if ev:
        return ev, "building.json facade.elevations"
    seen = [s for s in ((sheets or {}).get("exterior") or {}).get("openings_seen") or [] if isinstance(s, dict)]
    return ([{"region_id": s.get("region"), "title": s.get("title"), "side": s.get("side"),
              "view_bearing_deg": s.get("view_bearing_deg"), "windows": s.get("windows", 0),
              "doors": s.get("doors", 0), "positions_m": s.get("positions_m") or [],
              "plan_check": s.get("plan_check")} for s in seen], "sheets.json exterior.openings_seen")


def _facade(elev: dict, vb: dict, sc: dict, tol: dict) -> dict:
    out_dir, how = elevation_out(elev, sc["north"])
    rec = {"region_id": elev.get("region_id"), "title": elev.get("title"), "side": elev.get("side"),
           "direction_from": how, "drawn": {"windows": int(elev.get("windows") or 0),
                                            "doors": int(elev.get("doors") or 0),
                                            "positions": len(elev.get("positions_m") or [])},
           "plan_check": elev.get("plan_check"), "result": "not_checked", "notes": []}
    if out_dir is None:
        rec["notes"].append("the elevation has neither a view bearing nor a side: nothing to compare")
        return rec
    built, x_left = facade_openings(vb, out_dir, sc["openings"])
    if x_left is None:
        rec["notes"].append("no outer wall of the variant faces this elevation")
        return rec
    rec["building"] = {"windows": sum(p["kind"] == "window" for p in built),
                       "doors": sum(p["kind"] == "door" for p in built), "openings": built}
    counts = {}
    for kind, key in (("window", "windows"), ("door", "doors")):
        d, b = rec["drawn"][key], rec["building"][key]
        counts[key] = "ok" if d == b else ("fewer" if b < d else "more")
    rec["counts"] = counts
    positions = [p for p in elev.get("positions_m") or [] if isinstance(p, dict) and p.get("x") is not None
                 and p.get("kind") in ("window", "door")]
    drawn = [{"kind": p["kind"], "x": float(p["x"]), "sill": p.get("sill"), "head": p.get("head")}
             for p in positions]
    if drawn:
        m = match_openings(drawn, built, tol["x"], tol["z"])
        rec["positions"] = {k: m[k] for k in ("matched", "offset_x_m", "offset_z_m", "mirrored", "max_dx_m",
                                              "max_dz_m")}
        rec["positions"]["missing_in_building"] = m["missing_in_building"]
        rec["positions"]["extra_in_building"] = [{k: p[k] for k in ("id", "kind", "x", "sill", "head")}
                                                 for p in m["extra_in_building"]]
        ok_pos = not m["missing_in_building"] and not m["extra_in_building"]
        if abs(m["offset_x_m"]) > tol["max_offset"]:
            rec["notes"].append(f"the drawn left end is {m['offset_x_m']:+.2f} m from the wall's: more than the "
                                f"{tol['max_offset']} m a roof overhang explains; positions not trusted")
            ok_pos = False
        if abs(m["offset_z_m"]) > tol["max_offset"]:
            rec["notes"].append(f"the drawn heights are {m['offset_z_m']:+.2f} m from the building's: more than the "
                                f"{tol['max_offset']} m a drawn ground at z 0.00 can explain; positions not trusted")
            ok_pos = False
        elif abs(m["offset_z_m"]) >= Z_OFFSET_NOTE_M:
            rec["notes"].append(f"the drawn heights are {m['offset_z_m']:+.2f} m from the building's (an elevation "
                                f"without a level mark takes its ground as z 0.00, assumed): a common offset, "
                                f"listed")
        if m["mirrored"]:
            rec["notes"].append("the openings match only mirrored: the elevation may be read from the wrong side")
            ok_pos = False
    else:
        ok_pos = True
        rec["positions"] = None
        rec["notes"].append("the elevation lists no opening positions: counts only")
    rec["result"] = "ok" if ok_pos and all(v == "ok" for v in counts.values()) else "mismatch"
    return rec


def roof_check(vb: dict, scene: Optional[dict], sheets: Optional[dict], tol_m: float) -> dict:
    """Built eaves and ridge (the roof object of the scene manifest) against the section's values."""
    rec = {"built": None, "drawn": None, "drawn_source": {}, "result": "not_checked", "notes": [], "deltas": {}}
    roof_obj = next((o for o in (scene or {}).get("objects") or [] if o.get("kind") == "roof"), None)
    planes = (roof_obj or {}).get("planes") or []
    zs = [float(p[2]) for pl in planes for p in pl.get("points") or [] if len(p) >= 3]
    if zs:
        rec["built"] = {"eaves": round(min(zs), 4), "ridge": round(max(zs), 4),
                        "planes_source": (roof_obj or {}).get("planes_source")}
    elif roof_obj is not None and (roof_obj.get("z_range") or None):
        rec["built"] = {"eaves": None, "ridge": round(float(roof_obj["z_range"][1]), 4), "planes_source": None}
        rec["notes"].append("the scene manifest lists no roof planes: only the highest point is known")
    else:
        rec["notes"].append("no roof object in the scene manifest (the build made a flat roof, or no scene)")
    drawn_sheet = ((sheets or {}).get("heights") or {}).get("roof") or {}
    drawn_roof = vb.get("roof") if isinstance(vb.get("roof"), dict) else {}
    drawn = {}
    for key, bkey in (("eaves", "eaves_height"), ("ridge", "ridge_height")):
        # sheets.json writes ``eaves_z`` / ``ridge_z`` (the section's reading); ``eaves`` / ``ridge`` is the older
        # spelling. Without the section the building's own roof is the reference, and the record says so.
        v = next((drawn_sheet[k] for k in (f"{key}_z", key) if isinstance(drawn_sheet.get(k), dict)), None)
        source = "sheets.json heights.roof"
        if v is None:
            v, source = drawn_roof.get(bkey), "building.json roof"
        if isinstance(v, dict) and isinstance(v.get("value"), (int, float)):
            drawn[key] = {"value": float(v["value"]), "method": v.get("method")}
            rec["drawn_source"][key] = source
    rec["drawn"] = drawn or None
    if rec["built"] is None:
        return rec
    ok, checked = True, 0
    for key in ("eaves", "ridge"):
        d, b = drawn.get(key), rec["built"].get(key)
        if d is None or b is None:
            continue
        if d["method"] == "assumed":
            rec["notes"].append(f"{key}: the building's value is assumed (no section gave it): not checked")
            continue
        delta = round(b - d["value"], 4)
        rec["deltas"][key] = delta
        checked += 1
        ok &= abs(delta) <= tol_m + 1e-9
    if checked:
        rec["result"] = "ok" if ok else "mismatch"
    elif not drawn:
        rec["notes"].append("no eaves or ridge height in sheets.json or the building JSON")
    return rec


def elevation_check(building: dict, scene: Optional[dict] = None, sheets: Optional[dict] = None,
                    cfg: Optional[dict] = None, variant: str = "base") -> dict:
    """The elevation check of one variant (module docstring): ``{"kind": "elevation_check", "variant",
    "source", "facades": [...], "roof": {...}, "summary": {...}, "warnings": [...]}``."""
    from wenart.vision_check import exterior as EXT

    ecfg = (cfg or {}).get("elevation") or {}
    tol = {"x": float(ecfg.get("tolerance_x_m", TOL_X_M)), "z": float(ecfg.get("tolerance_z_m", TOL_Z_M)),
           "max_offset": float(ecfg.get("max_offset_m", MAX_OFFSET_M))}
    sc = EXT.scope({"variant": variant}, scene or {}, building)
    vb = sc["building"]
    elevations, source = drawn_elevations(building, sheets)
    facades = [_facade(e, vb, sc, tol) for e in elevations]
    roof = roof_check(vb, scene, sheets, float(ecfg.get("roof_height_tolerance_m", ROOF_TOL_M)))
    summary = {"facades": len(facades), "ok": sum(f["result"] == "ok" for f in facades),
               "mismatch": sum(f["result"] == "mismatch" for f in facades),
               "not_checked": sum(f["result"] == "not_checked" for f in facades), "roof": roof["result"]}
    return {"kind": "elevation_check", "variant": variant, "source": source, "north": sc["north"],
            "north_source": sc["north_source"], "facades": facades, "roof": roof, "summary": summary,
            "warnings": list(sc["warnings"])}


def lines(check: dict) -> list[str]:
    """One readable line per finding (CLI and check report)."""
    out = []
    for f in check.get("facades") or []:
        if f["result"] == "mismatch":
            c = f.get("counts") or {}
            bad = ", ".join(f"{k} {v}" for k, v in c.items() if v != "ok")
            pos = f.get("positions") or {}
            extra = []
            if pos.get("missing_in_building"):
                extra.append(f"{len(pos['missing_in_building'])} drawn opening(s) without a building opening")
            if pos.get("extra_in_building"):
                extra.append(f"{len(pos['extra_in_building'])} building opening(s) the elevation does not draw")
            out.append(f"{f.get('side')} ({f.get('region_id')}): " + "; ".join(x for x in [bad] + extra + f["notes"] if x))
    roof = check.get("roof") or {}
    if roof.get("result") == "mismatch":
        out.append("roof: built " + ", ".join(f"{k} {v:+.2f} m" for k, v in roof["deltas"].items()) + " from the section")
    return out
