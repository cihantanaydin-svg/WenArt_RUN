"""The architect's A6: the outdoor walk, checked and fixed (31 Oct 2026, user on real04 run 20261030-181158-full: "There
are still some path problems outside of the house, we need to develop a log that is checking the a person can walk
around the house using the designated pathways and able to reach the area, the pathways must be logical) Looked at the
marked area it is not making sense the person going to jump to reach the pool?").

What (pure on the build plan of ``build.prepare``, after A2 and B2 added their steps and paths; shapely through the
architect's route search):

- ``record_doors(building, prep)``: every outside door of the house with its landing point and its bottom level in the
  site plan (``site["outside_doors"]``): the walk's start points with the streets (``site_walk.outside_doors``).
- ``review_walk(building, prep)``: the walk check (``site_walk.analyse``) and the architect's fix of every finding, the
  check run again after each fix; a fix is kept only when the finding it targets is gone and no new major finding of
  the walk or of the site's sense (G8, G9, G14) appears, else it is undone (CLAUDE.md: "findings removed" is the
  measure). In the order tried:

  1. ``meet``: a path end that stops beside a surface at another level (a terrace, a flight's landing) is pinned to
     that surface's level (the area's ``meet``; ``grading.graded_paths``): the path's own steps make up the difference;
  2. ``extend``: a path end that stops short of a surface ahead (at most ``EXTEND_MAX_M``, nothing in the way) runs on
     to it and meets it at its level (the grading pins it, its steps make up the difference, landings and handrails by
     the path rules);
  3. ``connect``: a flight that ends on the lawn gets a path from its foot (or top) to the nearest path or drive
     (``architect.outside_access``, as A2 does for the decks without a door);
  4. ``flight``: a terrace or pool deck nobody can walk to and without a flight gets one on the edge nearest the
     nearest reachable surface (down where the ground is lower, up out of it where it is higher), then the path from it;
  5. ``link``: an area or the main entrance still cut off gets a path from it to the nearest reachable path or drive
     (the grading meets both ends at their levels and steps the difference: a ramp where the route is accessible).

  What stays is an open point with its place; the walk's log (``site_walk.walk_log``) with the fixes goes into the
  site plan (``site["walk"]``) and from there into the scene manifest's site block.
"""
from __future__ import annotations

import copy
from typing import Optional

from wenart import geometry as G

EXTEND_MAX_M = 3.0              # a dead end runs on to a surface at most this far ahead
EXTEND_STEP_M = 0.1
SURFACE_OVERLAP_M = 0.05        # a path that runs on to a surface ends this far inside it (architect.SURFACE_OVERLAP_M)
ROUNDS = 12                     # at most this many fixes are tried in one review (each one re-checks the walk)
UP_RISERS_MAX = 12              # site.up_flight's longest flight (no landing)


def record_doors(building: dict, prep: dict) -> list[dict]:
    """Every outside door of the house as a start of the walk (pure; in place: ``site["outside_doors"]``): ``[{"id",
    "level_id", "point" (the landing, ``architect.DOOR_PROBE_M`` out of the wall face), "z" (its bottom), "main"}]``."""
    from wenart.blender import architect as AR
    from wenart.blender import site as S

    site = prep.get("site") or {}
    levels = building.get("levels") or []
    mains = {str(e.get("door_id")) for e in (building.get("site") or {}).get("entrances") or []
             if isinstance(e, dict) and e.get("main")}
    mains |= {str(x) for x in ((site.get("inferred") or {}).get("main") or {}).get("opening_ids") or []}
    out = []
    try:
        recs = S.outer_openings(building, levels, prep.get("ground_outline") or [], prep.get("outlines"),
                                kinds=("door",))
    except (KeyError, TypeError, ValueError):
        recs = []
    for r in recs:
        (cx, cy), (ox, oy) = r["centre"], r["outward"]
        reach = float(r.get("half_t") or 0.1) + AR.DOOR_PROBE_M
        oid = str(r["opening"]["id"])
        out.append({"id": oid, "level_id": r["level"]["id"],
                    "point": [round(cx + ox * reach, 4), round(cy + oy * reach, 4)],
                    "z": round(float(r["bottom"]), 4), "main": oid in mains})
    site["outside_doors"] = out
    return out


def _key(f: dict) -> tuple:
    m = f.get("metrics") or {}
    return (m.get("problem"), str(f.get("target")), m.get("node"), m.get("end"))


def _majors(site: dict, walk_findings: list[dict]) -> set:
    """The major findings of the walk and of the site's sense (G8, G9, G14) as keys (the guard of every fix)."""
    from wenart.blender import site_sense as SS

    keys = {_key(f) for f in walk_findings if f.get("severity") == "major"}
    try:
        more = SS.fragments(site) + SS.flights_meet(site) + SS.walkways(site)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        more = []
    keys |= {((f.get("metrics") or {}).get("rule"), str(f.get("target")), f.get("message")) for f in more
             if f.get("severity") == "major"}
    return keys


def _try(site: dict, target: tuple, apply, before: set) -> tuple[bool, Optional[dict]]:
    """Carries out ``apply()`` on the site plan and keeps it only when the ``target`` finding is gone and no new major
    finding appears (pure; the areas and platforms are put back otherwise). Returns ``(kept, analysis)``."""
    from wenart.blender import site_walk as SW

    saved = {k: copy.deepcopy(site[k]) for k in ("areas", "platforms", "trees", "not_built") if k in site}
    try:
        done = apply()
    except (KeyError, TypeError, ValueError, ZeroDivisionError, IndexError, ImportError):
        done = False
    if done:
        rec = SW.analyse(site)
        keys = {_key(f) for f in rec["findings"]}
        if target not in keys and not (_majors(site, rec["findings"]) - before - {target}) \
                and not _too_steep(site):
            return True, rec
    for k in ("areas", "platforms", "trees", "not_built"):
        if k in saved:
            site[k] = saved[k]
        else:
            site.pop(k, None)
    return False, None


def _too_steep(site: dict) -> bool:
    from wenart.blender import grading as GR
    return any(r.get("too_steep") for r in GR.graded_paths(site) if r.get("graded"))


def _area(site: dict, pid) -> Optional[dict]:
    return next((a for a in site.get("areas") or [] if a.get("kind") == "path" and str(a.get("id")) == str(pid)), None)


def _end_of(rec: dict, f: dict) -> Optional[dict]:
    m = f.get("metrics") or {}
    return next((e for e in rec["ends"] if e["node"] == m.get("node") and e["end"] == m.get("end")), None)


def fix_meet(site: dict, rec: dict, f: dict) -> Optional[str]:
    """1. ``meet``: a path end that stops beside a surface (``site_walk.path_ends`` kind ``drop``, the surface beside
    its end landing) meets that surface's level (pure; in place)."""
    from wenart.blender import grading as GR

    e = _end_of(rec, f)
    a = _area(site, f.get("target"))
    if e is None or a is None or e.get("kind") != "drop" or not e.get("toward"):
        return None
    fr = GR.strip_frame(a["polygon"])
    if fr is None:
        return None
    t = (e["toward"][0] - fr["a"][0]) * fr["u"][0] + (e["toward"][1] - fr["a"][1]) * fr["u"][1]
    if not -1e-6 <= t <= fr["length"] + 1e-6:
        return None                                      # past the end: ``fix_extend``
    z = round(float(e["z"]) + float(e["dz"]), 4)
    why = (f"architect A6: path {a['id']} {'starts' if e['end'] == 'start' else 'ends'} beside {e['to_name']} "
           f"{abs(float(e['dz'])):.2f} m {'over' if e['dz'] < 0 else 'under'} it: its end meets it at {z:+.2f} m, the "
           f"path's steps make up the difference (no jump; inferred)")
    a.setdefault("meet", {})[e["end"]] = {"to": e["to"], "z": z, "reason": why}
    a["adjusted_by_ai"] = {"by": "architect", "reason": why}
    return why


def _corridor_free(site: dict, pts, half: float, skip_id: Optional[str]) -> bool:
    from wenart.blender import architect as AR
    keep = AR._Keep(AR.site_keep_out(site, skip_id or "", plants=False))
    return all(AR._free(p, keep, half * 0.9) for p in pts)


def fix_extend(site: dict, rec: dict, f: dict) -> Optional[str]:
    """2. ``extend``: a path end that stops short of a walkable surface straight ahead (a drop past it, or a dead end
    with a surface within ``EXTEND_MAX_M``) runs on to it, ``SURFACE_OVERLAP_M`` inside, where nothing stands in the
    way; the grading meets it at the surface's level (pure; in place)."""
    from wenart.blender import grading as GR
    from wenart.blender import site_walk as SW

    m = f.get("metrics") or {}
    a = _area(site, f.get("target"))
    if a is None or m.get("end") not in ("start", "end"):
        return None
    fr = GR.strip_frame(a["polygon"])
    if fr is None:
        return None
    g = rec["graph"]
    me = g["by_id"].get(m.get("node"))
    sign = -1.0 if m["end"] == "start" else 1.0
    t_end = 0.0 if m["end"] == "start" else fr["length"]
    hit, d = None, EXTEND_STEP_M
    while d <= EXTEND_MAX_M + 1e-9 and hit is None:
        p = GR._at(fr, t_end + sign * d)
        for n in g["nodes"]:
            if n is me or n["kind"] == "street":
                continue
            sides = [GR._at(fr, t_end + sign * d, s * fr["width"] * 0.4) for s in (-1.0, 1.0)]
            if SW.node_piece(n, p) is not None and all(SW.node_piece(n, q) is not None for q in sides):
                hit = (n, d)
                break
        d += EXTEND_STEP_M
    if hit is None:
        return None
    n, d = hit
    edge = d
    while edge - 0.01 > 0.0 and SW.node_piece(n, GR._at(fr, t_end + sign * (edge - 0.01))) is not None:
        edge -= 0.01                                     # the surface's edge, to the centimetre
    run = edge + SURFACE_OVERLAP_M
    pts = [GR._at(fr, t_end + sign * x, s * fr["width"] / 2.0 * 0.9) for x in
           [run * k / 6.0 for k in range(1, 6)] for s in (-1.0, 0.0, 1.0)]
    skip = n["element"] if n["kind"] == "platform" else None
    if not _corridor_free(site, pts, 0.05, skip):
        return None
    old = [list(q) for q in a["polygon"]]
    t0, t1 = (-run, fr["length"]) if m["end"] == "start" else (0.0, fr["length"] + run)
    a["polygon"] = [list(q) for q in GR._slice(fr, t0, t1)]
    why = (f"architect A6: path {a['id']} stopped {edge:.2f} m short of {n['name']}"
           + (f" ({abs(float(m.get('dz_m'))):.2f} m {'lower' if float(m.get('dz_m')) < 0 else 'higher'})"
              if isinstance(m.get("dz_m"), (int, float)) else "")
           + f": it runs on {run:.2f} m to it and meets it at its level, its steps making up the difference (no jump; "
             f"inferred)")
    a["adjusted_by_ai"] = {"by": "architect", "drawn_polygon": old, "reason": why}
    return why


def _platform(site: dict, pid) -> Optional[dict]:
    return next((p for p in site.get("platforms") or [] if str(p.get("id")) == str(pid)), None)


def fix_connect(site: dict, rec: dict, f: dict) -> Optional[str]:
    """3. ``connect``: a flight whose foot (or top) touches no walkable surface gets a path to the nearest path or
    drive (``architect.outside_access``; pure; in place)."""
    from wenart.blender import architect as AR

    pf = _platform(site, f.get("target"))
    if pf is None or pf.get("steps_edge") is None:
        return None
    areas = AR.outside_access(pf, site)
    if not areas:
        return None
    site.setdefault("areas", []).extend(areas)
    pf["outside_access"] = "path"
    why = areas[-1]["reason"].replace("architect A2:", "architect A6:")
    for x in areas:
        x["reason"] = x["reason"].replace("architect A2:", "architect A6:")
    pf.setdefault("architect", []).append({"question": "A6", "change": why})
    return why


def _nearest_point(rec: dict, f: dict, pf: dict) -> Optional[tuple[float, float]]:
    near = (f.get("metrics") or {}).get("nearest") or {}
    n = rec["graph"]["by_id"].get(near.get("node"))
    if n is None:
        return None
    c = G.polygon_centroid([tuple(q[:2]) for q in pf["polygon"]])
    return min((q for pc in n["pieces"] for q in pc["poly"]), key=lambda q: G.distance(q, c))


def fix_flight(site: dict, rec: dict, f: dict) -> Optional[str]:
    """4. ``flight``: a terrace or pool deck nobody can walk to, without a flight, gets one on the free edge nearest the
    nearest reachable surface: down to the lower ground (``grading.down_flight``) or up out of a sunken deck into the
    higher ground (``site.up_flight``), the railing open there, then the path from it (``architect.outside_access``;
    pure; in place)."""
    from wenart.blender import architect as AR
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    pf = _platform(site, f.get("target"))
    if pf is None or pf.get("steps_edge") is not None or pf.get("sloped") or pf.get("elevated") \
            or pf.get("kind") not in ("terrace", "pool"):
        return None
    terrain = site.get("terrain")
    if not terrain:
        return None
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    toward = _nearest_point(rec, f, pf)
    poly = pf["polygon"]
    n = len(poly)
    drops = pf.get("edge_drops") or {}
    blocked = set(pf.get("against_edges") or []) | {int(k) for k in (pf.get("edge_floor") or {})}
    tol = S.PLATFORM["level_tol"]
    cands = []
    for i in range(n):
        length = G.distance(poly[i], poly[(i + 1) % n])
        drop = drops.get(i, drops.get(str(i)))
        need = S.PLATFORM["step_width"] + 2 * (AR.STEP_GAP_M + S.PLATFORM["wall_t"])
        if i in blocked or drop is None or length < need:
            continue
        drop = float(drop)
        if tol < drop <= AR.ACCESS_MAX_DROP_M:
            way = "down"
        elif tol < -drop <= UP_RISERS_MAX * S.PLATFORM["step_rise"]:
            way = "up"
        else:
            continue
        mid = G.segment_midpoint(poly[i], poly[(i + 1) % n])
        cands.append((G.distance(mid, toward) if toward else 0.0, abs(drop), i, way))
    others = [q["polygon"] for q in site.get("platforms") or [] if q is not pf and not q.get("sloped")
              and len(q.get("polygon") or []) >= 3]
    others += [p for h in site.get("hedges") or [] for p in S._hedge_footprints(h)]
    others += [p["polygon"] for p in site.get("pools") or [] if len(p.get("polygon") or []) >= 3]
    keys = ("steps_edge", "edge", "steps_dir", "flight", "railing_gaps", "foot_open")
    old = {k: copy.deepcopy(pf[k]) for k in keys if k in pf}
    for _d, _drop, i, way in sorted(cands):
        trial = dict(pf, steps_edge=i, steps_dir="up" if way == "up" else None)
        trial.pop("flight", None)
        fl = S.up_flight(trial, terrain) if way == "up" else GR.down_flight(trial, gz)
        if fl is None or any(S.convex_overlap(fl["footprint"], q, tol=0.01) for q in others):
            continue
        pf["steps_edge"] = i
        pf["edge"] = "steps"
        if way == "up":
            pf["steps_dir"] = "up"
            pf["flight"] = fl
        else:
            pf.pop("steps_dir", None)
        if i in (pf.get("railing_edges") or []):
            pf.setdefault("railing_gaps", []).append(i)
        areas = AR.outside_access(pf, site)
        if areas is None:                                # no walkable route from this flight: the next edge
            for k in keys:
                pf.pop(k, None)
            pf.update(copy.deepcopy(old))
            continue
        site.setdefault("areas", []).extend(areas)
        for x in areas:
            x["reason"] = x["reason"].replace("architect A2:", "architect A6:")
        near = ((f.get("metrics") or {}).get("nearest") or {}).get("name", "paths")
        path = areas[-1]["reason"].split("(", 1)[0].replace("architect A6: ", "").strip() if areas else ""
        why = (f"architect A6: nobody could walk to {pf['id']} (no door, no flight): a flight {way} on edge {i}, the one "
               f"nearest the reachable {near}" + (f", and {path}" if path else "") + " (inferred)")
        pf.setdefault("architect", []).append({"question": "A6", "change": why})
        return why
    return None


def fix_link(site: dict, rec: dict, f: dict) -> Optional[str]:
    """5. ``link``: an area (or the main entrance) still cut off gets a path from its edge to the nearest reachable path
    or drive (the shortest walkable route, ``architect.access_path``; the grading meets both ends at their levels; a
    ramp where the area is on an accessible route; pure; in place)."""
    from wenart.blender import architect as AR
    from wenart.blender.site import INFERRED

    m = f.get("metrics") or {}
    g = rec["graph"]
    if m.get("problem") == "arrival":
        door = next((d for d in g["doors"] if d["id"] == str(f.get("target"))), None)
        node = g["by_id"].get(door.get("node")) if door else None
        reached = rec["street_reached"]
    else:
        node = g["by_id"].get(m.get("node"))
        reached = rec["reached"]
    if node is None:
        return None
    half = INFERRED["path_width"] / 2.0
    paths = [a for a in site.get("areas") or [] if a.get("kind") == "path" and f"path:{a.get('id')}" in reached]
    drives = [a for a in site.get("areas") or [] if a.get("kind") == "parking" and len(a.get("polygon") or []) >= 3
              and f"platform:{a.get('id')}" in reached]
    if not paths and not drives:
        return None
    skip = node["element"] if node["kind"] == "platform" else ""
    keep = AR._Keep(AR.site_keep_out(site, str(skip)))
    plot = site.get("plot") or []
    ok = (lambda r: AR.route_problem(r, half, site.get("terrain"), start_back=0.8 + SURFACE_OVERLAP_M))
    targets = AR.join_targets(site, paths, half) + AR.path_targets(drives, 0.2)
    best = None
    for pc in node["pieces"]:
        starts = sorted(AR._edge_points(pc["poly"], 1.0), key=lambda s: min(
            (abs(t[0] - s[0]) + abs(t[1] - s[1]) for t in targets), default=1e9))
        for s in starts[:12]:
            route = AR.access_path(s, targets, keep, half, within=plot or None, ok=ok)
            if route and (best is None or AR._length(route) < AR._length(best)):
                best = route
    if best is None:
        return None
    joined = AR.path_end_at(best, paths)
    if joined is not None:
        best = joined
    acc = bool(node["kind"] == "entrance" and any(isinstance(st.get("ramp"), dict) for st in (
        site.get("inferred") or {}).get("steps") or [] if str(st.get("opening_id")) == str(node["element"])))
    why = (f"architect A6: nobody could walk to {node['name']} from the "
           f"{'street' if m.get('problem') == 'arrival' else 'paths'}: a path from it to the nearest reachable "
           f"{'path' if joined is not None else 'surface'} ({AR._length(best):.1f} m; its ends meet both surfaces at "
           f"their levels, steps or a ramp between; inferred)")
    areas = AR.path_areas(f"walk_{node['element']}", best, half, why, end_extend=joined is None,
                          start_back=0.8 + SURFACE_OVERLAP_M)
    for x in areas:
        if acc:
            x["accessible"] = True
    site.setdefault("areas", []).extend(areas)
    return why


FIXES = {"dead_end_drop": (fix_meet, fix_extend), "dead_end": (fix_extend,), "dead_flight": (fix_connect,),
         "unreachable": (fix_flight, fix_link), "arrival": (fix_link,)}


def review_walk(building: dict, prep: dict) -> dict:
    """A6 (module docstring): the walk checked, every finding fixed where a rule can, the walk checked again; the
    answers name every fix and every open point with its place; ``site["walk"]`` keeps the log."""
    from wenart.blender import architect as AR
    from wenart.blender import site_walk as SW

    q = AR._q("A6")
    site = prep.get("site") or {}
    if not site.get("terrain"):
        return q
    record_doors(building, prep)
    rec = SW.analyse(site)
    first = list(rec["findings"])
    fixes, tried = [], set()
    for _round in range(ROUNDS):
        before = _majors(site, rec["findings"])
        order = sorted(rec["findings"], key=lambda f: (f.get("severity") != "major", _key(f)))
        progress = False
        for f in order:
            key = _key(f)
            for fn in FIXES.get((f.get("metrics") or {}).get("problem"), ()):
                if (key, fn.__name__) in tried:
                    continue
                tried.add((key, fn.__name__))
                out: dict = {}

                def apply(fn=fn, f=f, out=out):
                    out["why"] = fn(site, rec, f)
                    return out["why"] is not None
                kept, again = _try(site, key, apply, before)
                if kept:
                    fixes.append({"fix": fn.__name__.replace("fix_", ""), "finding": f["message"],
                                  "target": f.get("target"), "at": (f.get("metrics") or {}).get("at"),
                                  "change": out["why"]})
                    q["answers"].append({"element": str(f.get("target")), "found": f["message"],
                                         "change": out["why"].replace("architect A6: ", ""), "fixed": True})
                    rec = again
                    progress = True
                    break
            if progress:
                break
        if not progress:
            break
    for f in rec["findings"]:
        m = f.get("metrics") or {}
        q["answers"].append({"element": str(f.get("target")), "found": f["message"], "change": None, "open": True,
                             "ask": "How should a person walk here: steps, a ramp or a path, or keep it as it is?",
                             "where": {"kind": "site", "level_id": None, "centre": m.get("at")},
                             "severity": f.get("severity")})
        if f.get("severity") == "major":
            q["status"] = "open"
    if not rec["findings"]:
        g = rec["graph"]
        use = [n for n in g["nodes"] if n.get("use")]
        q["answers"].append({"element": "site", "found": f"a person walks from the street and the "
                             f"{len(g['doors'])} outside door(s) along the designated paths to all {len(use)} outdoor "
                             f"areas; every flight lands on a walkable surface and every path arrives somewhere",
                             "change": None})
    if fixes and q["status"] == "ok":
        q["status"] = "fixed"
    log = SW.walk_log(site, rec)
    log["first_findings"] = len(first)
    log["fixes"] = fixes
    site["walk"] = log
    return q
