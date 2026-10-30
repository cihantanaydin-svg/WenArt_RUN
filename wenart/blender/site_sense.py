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
- G12 ``aprons``: the paved strip at the foot of a glazed facade covers its whole glazing run (UL142);
- G13 ``access`` (30 Oct 2026, UL198: "Understand that the cars should be able to enter to this location and exit"):
  a car drives into every parking from a street and out again (``site.vehicle_access``: a clear stretch of its edge
  at least 3 m wide, no kerb, railing, step, wall, fence, hedge or flight across it, a gradient a car takes, and a
  second way out or room to turn); a way in that is not usable is a minor finding when another one is;
- G14 ``walkways`` (30 Oct 2026, UL202: "make sure the walkways are walkable"): two paths meet edge to edge on a level
  landing (no wedge of two strips at different levels, no step of one across the other's walk), a path joins a path
  or leaves a door's landing square to it, nothing (a tree, a plant, a handrail post) stands in a walk, a walk on the
  ground is level across.

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


def access(site: dict) -> list[dict]:
    """G13 (module docstring): every parking's way in from a street and out again (``site.vehicle_access``; shapely,
    so none where it is missing)."""
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    try:
        rows = S.vehicle_access(site)
    except ImportError:
        return []
    out = []
    for r in rows:
        if not r["ok"]:
            out.append(GR._f("major", r["platform"], f"a car cannot use the parking {r['platform']}: "
                             + "; ".join(r["problems"]), "G13", "no_sense", lesson="UL198"))
            continue
        for c in r["connections"]:
            if c["problems"]:
                out.append(GR._f("minor", r["platform"], f"the way into {r['platform']} at its edge {c['edge']} is "
                                 f"not usable by a car: {', '.join(c['problems'])} (another way in is)", "G13",
                                 "no_sense", lesson="UL198", edge=c["edge"]))
    return out


SQUARE_SIN = 0.035              # a path leaves a landing or joins a path square to it (within 2 degrees)
OVERLAP_M2 = 0.05                # two path strips that share more than this overlap


def _risers(rec: dict) -> list[float]:
    """The ``t`` of every riser of a planned path (pure): a level change between two built slices."""
    built = sorted((s for s in rec.get("slices") or [] if not s.get("skip")), key=lambda s: s["t0"])
    return [a["t1"] for a, b in zip(built, built[1:]) if abs(max(a["z0"], a["z1"]) - max(b["z0"], b["z1"])) > 0.01]


def _inside(p, poly) -> bool:
    return G.point_in_polygon(p, poly) and geom2d.distance_to_polygon_edges(p, poly) > EDGE_TOL_M


def _square(u, v) -> bool:
    """Whether two directions are parallel or at right angles (within ``SQUARE_SIN``)."""
    cross = abs(u[0] * v[1] - u[1] * v[0])
    return cross <= SQUARE_SIN or abs(u[0] * v[0] + u[1] * v[1]) <= SQUARE_SIN


def walkways(site: dict) -> list[dict]:
    """G14 (30 Oct 2026, lesson UL202, user on real04: "something is wrong here. also for the outside areas also make
    sure the walkways are walkable"): two paths meet edge to edge on a level landing (no wedge of two strips at
    different levels, no step of one running across the other's walk), a path joins a path or leaves a door's landing
    square to it, nothing (a tree, a plant, a handrail post) stands in a walk, and a walk on the ground is level
    across (pure)."""
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    terrain = GR.plan_terrain(site)
    if not terrain:
        return []
    gz = (lambda x, y: S.ground_z(terrain, x, y))
    recs = [r for r in GR.graded_paths(site) if len(r.get("polygon") or []) >= 3]
    by_id = {r.get("id"): r for r in recs}
    out = []
    for i, a in enumerate(recs):
        for b in recs[i + 1:]:
            pa = [tuple(map(float, q[:2])) for q in a["polygon"]]
            pb = [tuple(map(float, q[:2])) for q in b["polygon"]]
            if _area_in(pb, pa) <= OVERLAP_M2:
                continue
            pts = [p for p in S._grid_points(pb, 0.2) if _inside(p, pa)]
            dz = max((abs(za - zb) for za, zb in ((GR.level_on(a, p, gz), GR.level_on(b, p, gz)) for p in pts)
                      if za is not None and zb is not None), default=0.0)
            steps = []
            for r, other in ((a, pb), (b, pa)):
                fr = r.get("frame")
                if fr is None:
                    continue
                for t in _risers(r):
                    if any(_inside(GR._at(fr, t, s * fr["width"] / 2.0), other) for s in (-0.8, -0.4, 0.0, 0.4, 0.8)):
                        steps.append(r.get("id"))
                        break
            if dz > GR.JOIN_TOL_M or steps:
                fa, fb = a.get("frame"), b.get("frame")
                oblique = fa is not None and fb is not None and abs(fa["u"][0] * fb["u"][1] - fa["u"][1] * fb["u"][0]) > SQUARE_SIN
                out.append(GR._f("major", b.get("id"), f"paths {a.get('id')} and {b.get('id')} run one over the other "
                                 f"at levels up to {dz * 100:.0f} cm apart"
                                 + (f"; a step of {', '.join(steps)} runs {'obliquely ' if oblique else ''}across the "
                                    f"other's walk" if steps else "")
                                 + " (two paths meet edge to edge on a level landing)", "G14", "no_sense",
                                 other=a.get("id"), dz_m=round(dz, 3), steps=steps, lesson="UL202"))
    for r in recs:
        fr = r.get("frame") or GR.strip_frame(r.get("polygon") or [])
        if fr is None:
            continue
        for j in r.get("joins") or []:
            t_end = 0.0 if j["end"] == "start" else fr["length"]
            sign = -1.0 if j["end"] == "start" else 1.0
            mine = GR.level_on(r, GR._at(fr, t_end - sign * 0.05), gz)
            if j["kind"] == "path":
                q = by_id.get(j["to"])
                if q is None:
                    continue
                theirs = GR.level_on(q, GR._at(fr, t_end + sign * GR.JOIN_PROBE_M), gz)
                qf = q.get("frame") or GR.strip_frame(q.get("polygon") or [])
                if qf is not None and not _square(fr["u"], qf["u"]):
                    out.append(GR._f("major", r.get("id"), f"path {r.get('id')} joins {q.get('id')} at an angle (a "
                                     f"path meets another square to it)", "G14", "no_sense", other=q.get("id"),
                                     lesson="UL202"))
                if q.get("graded") and qf is not None:
                    t0, t1 = GR.joint_span(fr, t_end, qf)
                    if not GR.joint_ok(q, t0 + 0.02, t1 - 0.02):
                        out.append(GR._f("major", r.get("id"), f"path {r.get('id')} joins {q.get('id')} on its steps, "
                                         f"not on a level landing", "G14", "no_sense", other=q.get("id"),
                                         lesson="UL202"))
            else:
                land = next((ld for ld in GR.entrance_landings(site) if ld["id"] == j["to"]), None)
                theirs = land["z"] if land else None
                if land is not None:
                    poly = land["polygon"]
                    p = GR._at(fr, t_end + sign * GR.JOIN_PROBE_M)
                    k = min(range(len(poly)), key=lambda m: G.point_segment_distance(p, poly[m],
                                                                                    poly[(m + 1) % len(poly)]))
                    e0, e1 = poly[k], poly[(k + 1) % len(poly)]
                    length = max(G.distance(e0, e1), 1e-9)
                    ed = ((e1[0] - e0[0]) / length, (e1[1] - e0[1]) / length)
                    if abs(ed[0] * fr["u"][0] + ed[1] * fr["u"][1]) > SQUARE_SIN:
                        out.append(GR._f("major", r.get("id"), f"path {r.get('id')} leaves the landing of "
                                         f"{j['to'].split(':')[-1]} at an angle (a path leaves a door's landing square "
                                         f"to its edge)", "G14", "no_sense", lesson="UL202"))
            if mine is not None and theirs is not None and abs(mine - theirs) > GR.JOIN_TOL_M:
                out.append(GR._f("major", r.get("id"), f"path {r.get('id')} meets {j['to']} {abs(mine - theirs) * 100:.0f}"
                                 f" cm {'above' if mine > theirs else 'below'} its level (a step at the joint; two "
                                 f"walks meet level)", "G14", "no_sense", other=j["to"],
                                 dz_m=round(mine - theirs, 3), lesson="UL202"))
        if not r.get("graded") and r.get("cross") is not None and float(r["cross"]) > GR.GRADE["cross_fall_max"] + 1e-6:
            out.append(GR._f("major", r.get("id"), f"walk {r.get('id')} tilts {float(r['cross']) * 100:.1f} % across "
                             f"(level across, at most {GR.GRADE['cross_fall_max'] * 100:.1f} %)", "G14", "no_sense",
                             lesson="UL202"))
    # nothing stands in a walk: the trees and plants, the handrail posts of the other paths and of the entrances
    things = [(f"{t.get('kind') or 'plant'} {t.get('id')}", (float(t["center"][0]), float(t["center"][1])), None)
              for t in site.get("trees") or [] if t.get("center")]
    for r in recs:
        rail = GR.stair_rail(r, gz) if r.get("graded") and r.get("kind") == "stepped" else None
        for foot, _top in (rail or {}).get("posts") or []:
            things.append((f"a handrail post of path {r.get('id')}", (foot[0], foot[1]), r.get("id")))
    for st in (site.get("inferred") or {}).get("steps") or []:
        for foot, _top in st.get("posts") or []:
            things.append((f"a handrail post of the steps of {st['opening_id']}", (foot[0], foot[1]), None))
    for r in recs:
        poly = [tuple(map(float, q[:2])) for q in r["polygon"]]
        for name, c, owner in things:
            if owner == r.get("id"):
                continue
            if _inside(c, poly):
                out.append(GR._f("major", r.get("id"), f"{name} stands in the walk of path {r.get('id')} (nothing stands "
                                 f"within a path's walking width)", "G14", "no_sense", thing=name, lesson="UL202"))
    return out


def review(site: Optional[dict], manifest: Optional[dict] = None) -> tuple[list[dict], int]:
    """G8-G14 on a site plan (pure; module docstring)."""
    from wenart.blender import pool_extras as PX

    if not site or not site.get("terrain"):
        return [], 0
    findings = fragments(site) + flights_meet(site) + rails(site, manifest) + aprons(site, manifest) + access(site) \
        + walkways(site)
    more, n = PX.review(site, manifest)
    checked = len(site.get("platforms") or []) + len([a for a in site.get("areas") or [] if a.get("kind") == "path"]) \
        + len(site.get("glazing_runs") or []) + n
    return findings + more, checked
