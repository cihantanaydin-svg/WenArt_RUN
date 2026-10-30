"""Site elements only where they make sense (30 Oct 2026; the model review's M15 rules G8-G12; lessons UL129, UL141,
UL142, UL143, UL144 of the user's review of real04 run 20261029-201533-full).

What (pure, no shapely: it runs where the grading review runs):

- G8 ``fragments``: no stray piece of a site element: a flight whose footprint lies under another surface that has
  no cut for it (its treads buried, its cheeks standing as blocks on the paving: UL129's pairs of stone blocks on the
  drive), a path that runs into a building or on under another surface past its edge (UL129: real04's entrance
  paths through the second house and under the parking), a kerb along an edge another surface abuts;
- G9 ``flights_meet``: a flight never meets a wall or a block, and every flight ends on a landing or the ground: no
  cheek wall or tread of a platform's flight on a path's steps, no path tread through a flight (UL141: the cheek of
  sp_001's foot landing cut the lowest steps of the path from it), a stepped path begins and ends on a landing;
- G10 ``rails``: an outdoor stair over the levels' ``handrail_from`` has one continuous handrail on its open side,
  every post standing on its steps, reaching past its first and last step (UL144: a loose frame per flight); on the
  scene manifest, a stepped path built before the rule (its ``rail`` record missing) is a finding;
- G11 (``pool_extras.review``): every pool has a ladder, a deck with room has seating (UL143);
- G12 ``aprons``: the paved strip at the foot of a glazed facade covers its whole glazing run (UL142).

``review(site, manifest)`` returns ``(findings, checked)`` in the model review's format (``grading._f``).
"""
from __future__ import annotations

from typing import Optional

from wenart import geometry as G
from wenart.blender import geom2d

PATH_INTO_MAX_M2 = 0.25          # a path may reach this far into the surface it arrives at (its joint)
BUILDING_INTO_MAX_M2 = 0.05
SAMPLE_M = 0.1
EDGE_TOL_M = 0.05                # points this close to a region's edge are on the edge, not in it


def _area_in(poly, region, holes=(), step: float = SAMPLE_M) -> float:
    """The area of ``poly`` inside ``region`` (outside ``holes``), sampled on a ``step`` grid (pure)."""
    from wenart.blender import site as S

    poly = [tuple(map(float, q[:2])) for q in poly]
    reg = [tuple(map(float, q[:2])) for q in region]
    if len(poly) < 3 or len(reg) < 3:
        return 0.0
    ax0, ay0, ax1, ay1 = G.bbox(poly)
    bx0, by0, bx1, by1 = G.bbox(reg)
    if ax1 < bx0 or bx1 < ax0 or ay1 < by0 or by1 < ay0:
        return 0.0                                       # apart: nothing to sample
    pts = [p for p in S._grid_points(poly, step) if bx0 <= p[0] <= bx1 and by0 <= p[1] <= by1]
    hit = sum(1 for p in pts if G.point_in_polygon(p, reg) and geom2d.distance_to_polygon_edges(p, reg) > EDGE_TOL_M
              and not any(G.point_in_polygon(p, h) for h in holes if len(h) >= 3))
    return hit * step * step


def fragments(site: dict) -> list[dict]:
    """G8 (module docstring)."""
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    out = []
    terrain = GR.plan_terrain(site)
    pfs = list(site.get("platforms") or [])
    gz = (lambda x, y: S.ground_z(terrain, x, y)) if terrain else None
    for pf in pfs:
        flights = []
        up = pf.get("flight") if isinstance(pf.get("flight"), dict) else (S.up_flight(pf, terrain) if terrain else None)
        if up:
            flights.append(("up", up))
        if gz is not None:
            dn = GR.down_flight(pf, gz)
            if dn:
                flights.append(("down", dn))
        for how, fl in flights:
            for q in pfs:
                if q is pf or q.get("parent") == pf.get("id") or pf.get("parent") == q.get("id") or q.get("elevated"):
                    continue
                share = S.area_share(fl["footprint"], q.get("polygon") or [], q.get("holes") or [])
                if share <= S.CUT_SHARE:
                    continue
                if any(c.get("by") == pf.get("id") for c in q.get("cuts") or []):
                    continue
                out.append(GR._f("major", pf["id"], f"the flight {how} of {pf['id']} runs {share * 100:.0f} % under "
                                 f"{q['id']}: its treads are buried under that surface and its cheek walls stand on it "
                                 f"as loose blocks (a flight onto a surface is cut into it)", "G8", "no_sense",
                                 under=q["id"], share=round(share, 3), lesson="UL129"))
    buildings = [("the house", site.get("outline") or [])] + [(f"building copy {k + 1}", h) for k, h in
                                                             enumerate(site.get("copy_holes") or [])]
    for a in site.get("areas") or []:
        if a.get("kind") != "path" or a.get("platform_id") or len(a.get("polygon") or []) < 3:
            continue
        for name, poly in buildings:
            if len(poly) >= 3 and _area_in(a["polygon"], poly) > BUILDING_INTO_MAX_M2:
                out.append(GR._f("major", a.get("id"), f"path {a.get('id')} runs into {name} (a path ends before a "
                                 f"building in its way)", "G8", "no_sense", into=name, lesson="UL129"))
        for q in pfs:
            if q.get("elevated") or len(q.get("polygon") or []) < 3:
                continue
            got = _area_in(a["polygon"], q["polygon"], q.get("holes") or [])
            if got > PATH_INTO_MAX_M2:
                out.append(GR._f("major", a.get("id"), f"path {a.get('id')} runs {got:.1f} m2 on under {q['id']}: its "
                                 f"steps and edges stand in that surface (a path ends where it arrives at a surface)",
                                 "G8", "no_sense", into=q["id"], area_m2=round(got, 2), lesson="UL129"))
    for pf in pfs:
        if not (pf.get("edge") == "kerb" or pf.get("kind") in ("parking", "path")):
            continue
        want = S.kerb_gaps(pf, [q for q in pfs if q is not pf])
        have = [(int(g[0]), float(g[1]), float(g[2])) for g in pf.get("kerb_gaps") or []]
        missing = 0.0
        for i, t0, t1 in want:
            cov = sum(max(0.0, min(t1, h1) - max(t0, h0)) for j, h0, h1 in have if j == i)
            missing += max(0.0, (t1 - t0) - cov)
        if missing > 0.5:
            out.append(GR._f("minor", pf["id"], f"{pf['id']} builds {missing:.1f} m of kerb along edges another surface "
                             f"abuts (a kerb between two surfaces stands as a stray bar)", "G8", "no_sense",
                             kerb_m=round(missing, 2), lesson="UL129"))
    return out


def flights_meet(site: dict) -> list[dict]:
    """G9 (module docstring)."""
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    out = []
    terrain = GR.plan_terrain(site)
    if not terrain:
        return out
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    paths = []
    for rec in GR.graded_paths(site):
        if not rec.get("graded"):
            # a walk on the ground: its strip at the ground's level (one piece per metre along a straight strip)
            fr = GR.strip_frame(rec.get("polygon") or [])
            if fr is None:
                continue
            k = max(1, int(fr["length"]))
            for j in range(k):
                q = GR._slice(fr, fr["length"] * j / k, fr["length"] * (j + 1) / k)
                paths.append((rec.get("id"), q, gz(*G.polygon_centroid(q))))
            continue
        fr = rec["frame"]
        built = [s for s in rec["slices"] if not s.get("skip")]
        for s in built:
            paths.append((rec.get("id"), GR._slice(fr, s["t0"], s["t1"]), max(s["z0"], s["z1"])))
        if rec.get("kind") == "stepped" and built:
            # an end that joins another walk (a slice left to the other path, a surface beyond it) is no end
            walk = [w for w in GR.walkable(site) if not S._same_poly(w, rec.get("polygon") or [])]
            ends = []
            for e, t_out, first in ((built[0], built[0]["t0"] - 0.15, rec["slices"][0]),
                                    (built[-1], built[-1]["t1"] + 0.15, rec["slices"][-1])):
                joined = e is not first or any(G.point_in_polygon(GR._at(fr, t_out), w) for w in walk)
                if not joined:
                    ends.append(e)
            if any(e["kind"] != "landing" for e in ends):
                out.append(GR._f("major", rec.get("id"), f"path {rec.get('id')} starts or ends on a step, not on a "
                                 f"landing (every flight ends on a landing or the ground)", "G9", "no_sense",
                                 lesson="UL141"))
    for pf in site.get("platforms") or []:
        fl = GR.down_flight(pf, gz)
        if fl is None:
            continue
        for ch in fl["cheeks"]:
            hit = next((pid for pid, poly, _z in paths if S.convex_overlap(ch["polygon"], poly, tol=0.02)), None)
            if hit:
                out.append(GR._f("major", pf["id"], f"a cheek wall of the flight of {pf['id']} stands on the steps of "
                                 f"path {hit} (a flight never meets a wall or a block; the path leaves its foot "
                                 f"landing through an open side)", "G9", "no_sense", path=hit, lesson="UL141"))
                break
        for blk in list(fl["blocks"]) + [{"polygon": fl["foot"], "z_top": fl["foot_z"]}]:
            hit = next((pid for pid, poly, z in paths if S.convex_overlap(blk["polygon"], poly, tol=0.02)
                        and abs(z - float(blk["z_top"])) > 0.05), None)
            if hit:
                out.append(GR._f("major", pf["id"], f"path {hit} runs through the flight of {pf['id']} at another "
                                 f"level (its treads cut into the flight's steps)", "G9", "no_sense", path=hit,
                                 lesson="UL141"))
                break
    return out


def rails(site: dict, manifest: Optional[dict] = None) -> list[dict]:
    """G10 (module docstring)."""
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    out = []
    terrain = GR.plan_terrain(site)
    if not terrain:
        return out
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    for rec in GR.graded_paths(site):
        if not rec.get("graded") or rec.get("kind") != "stepped" or not rec.get("handrails"):
            continue
        r = GR.stair_rail(rec, gz)
        pid = rec.get("id")
        if r is None:
            out.append(GR._f("major", pid, f"the stair of path {pid} rises over the handrail height rule and has no "
                             f"handrail", "G10", "no_sense", lesson="UL144"))
            continue
        poly = rec["polygon"]
        off = [p for p, _t in r["posts"] if not (G.point_in_polygon(p[:2], poly)
                                                  or geom2d.distance_to_polygon_edges(p[:2], poly) < 0.01)]
        if off:
            out.append(GR._f("major", pid, f"{len(off)} handrail post(s) of path {pid} stand off its steps (in the "
                             f"ground beside it)", "G10", "no_sense", lesson="UL144"))
        if r["spacing_m"] > GR.RAIL["post_max_m"] + 0.11:
            out.append(GR._f("minor", pid, f"the handrail posts of path {pid} stand {r['spacing_m']:.2f} m apart "
                             f"(at most 1.5 m)", "G10", "no_sense", lesson="UL144"))
    for p in ((manifest or {}).get("site") or {}).get("paths") or []:
        if p.get("kind") == "stepped" and p.get("handrails") and not (p.get("rail") or {}).get("continuous"):
            out.append(GR._f("major", p.get("id"), f"the handrails of path {p.get('id')} were built flight by flight: "
                             f"short frames of two posts and a bar beside the stair, gaps between the flights (one "
                             f"continuous rail on the open side, over the landings, 0.3 m past the ends)", "G10",
                             "no_sense", lesson="UL144"))
    return out


def aprons(site: dict, manifest: Optional[dict] = None) -> list[dict]:
    """G12 (module docstring): on the plan's ``glazing_runs``; on the scene manifest, a light well beside other
    openings of its run that no apron covers (a build before the rule: the manifest names no ``glazing_runs``)."""
    from wenart.blender import grading as GR

    out = []
    for run in site.get("glazing_runs") or []:
        left = [i for i in run.get("run_ids") or [] if i not in (run.get("covered_ids") or [])]
        if left:
            out.append(GR._f("major", run.get("well"), f"the light well of {run.get('well')} paves only part of its "
                             f"glazed facade: {', '.join(left)} of the same run stand on the lawn (the strip runs the "
                             f"whole glazing run)", "G12", "no_sense", missing=left, lesson="UL142"))
    ms = (manifest or {}).get("site") or {}
    if manifest and ms.get("light_wells") and "glazing_runs" not in ms:
        runs = {r.get("well"): r for r in site.get("glazing_runs") or []}
        for w in ms.get("light_wells") or []:
            r = runs.get(w.get("opening_id"))
            if r and len(r.get("run_ids") or []) > 1:
                out.append(GR._f("major", w.get("opening_id"), f"the light well of {w.get('opening_id')} was built "
                                 f"for its window alone: {', '.join(i for i in r['run_ids'] if i != w.get('opening_id'))}"
                                 f" of the same glazed facade stand on the lawn", "G12", "no_sense", lesson="UL142"))
    return out


def review(site: Optional[dict], manifest: Optional[dict] = None) -> tuple[list[dict], int]:
    """G8-G12 on a site plan (pure; module docstring)."""
    from wenart.blender import pool_extras as PX

    if not site or not site.get("terrain"):
        return [], 0
    findings = fragments(site) + flights_meet(site) + rails(site, manifest) + aprons(site, manifest)
    more, n = PX.review(site, manifest)
    checked = len(site.get("platforms") or []) + len([a for a in site.get("areas") or [] if a.get("kind") == "path"]) \
        + len(site.get("glazing_runs") or []) + n
    return findings + more, checked
