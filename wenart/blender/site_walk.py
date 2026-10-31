"""The outdoor walk: a person walks around the house along the designated paths and reaches every outdoor area (31 Oct
2026, user on real04 run 20261030-181158-full, an aerial view: "There are still some path problems outside of the house,
we need to develop a log that is checking the a person can walk around the house using the designated pathways and able
to reach the area, the pathways must be logical) Looked at the marked area it is not making sense the person going to
jump to reach the pool?"; in the marked area the stepped path from the house came down beside the pool terrace and
stopped below it, a raw step and a block of the terrace flight's foot landing between them).

What (pure, no shapely: it runs where the grading review runs, inside Blender too; general rules for every project,
the project is only the test case):

- ``walk_graph(site)``: the walk graph of a site plan (``build.prepare(...)["site"]``, the architect's paths in). Its
  nodes are the walkable surfaces with their levels: the flat platforms (terraces, pool decks, parkings; the planted
  tiers of a terrace are no walk), the paths as the grading builds them (``grading.graded_paths``: every built slice at
  its level), the foot landing of every flight down from a platform (``grading.down_flight``) and the top tread of
  every flight up out of one (``site.up_flight``), the entrance landings, steps and ramps (``inferred.steps``) and the
  streets and pavements. Two surfaces are joined where they touch (``TOUCH_M``) with at most one step between them
  (``STEP_MAX_M``: the most a step rises, ``site.DRAWN_RISER_MAX_M``), never across a railing, a handrail, a cheek
  wall, a hedge, a pool or a building; a flight joins its platform to its foot landing (or its top tread).
- Its start points: the streets and pavements, the parkings (the cars arrive there), every path end at the plot's edge
  (a gate) and every outside door of the house (``site["outside_doors"]``, the architect's record of the doors with
  their landings, A6; else the entrances of the site plan).
- ``review(site)``: the model review's G15 (M15, ``site_sense.review``): an outdoor area meant for use (a terrace, a
  pool deck, a parking, an entrance landing) no walk reaches from a start; the main entrance no walk reaches from the
  street; a flight whose foot (or top) touches no walkable surface (it ends on the lawn, at a drop or at a wall); a path
  end that meets the surface it arrives at with a step or a drop between them (its height); a path end with no
  destination (a dead end; at a drop when a surface lies just past or beside it at another level: "a person would have
  to jump"). Every finding names its place (``metrics.at``) and its levels.
- ``walk_log(site)``: the log of the walk (the starts, the surfaces, the joints with their heights, what is reached,
  the findings) that the architect keeps in the site plan (``site["walk"]``) and the scene manifest's site block shows.

The architect's fixes (A6, ``architect.review_walk``) read ``walk_log``: a path end beside a surface it should meet is
pinned to that surface's level (``meet``), a dead end with a surface just ahead runs on to it, a flight that ends on the
lawn and an area no walk reaches get steps and a path from the nearest reachable surface; the check runs again after
every fix and what stays is an open finding.
"""
from __future__ import annotations

import math
from typing import Callable, Optional

from wenart import geometry as G
from wenart.blender import geom2d

RULE = "G15"
STEP_MAX_M = 0.20               # the most one step rises between two surfaces (site.DRAWN_RISER_MAX_M); more: a drop
LEVEL_TOL_M = 0.03              # two walks that meet differ at most this in level (grading.JOIN_TOL_M)
TOUCH_M = 0.15                  # two surfaces this close touch (a joint, an edging, a kerb between them)
NEAR_M = 0.05                   # the first probe out of a surface's edge: a barrier there stands between
INSIDE_M = 0.02                 # a surface's level at its edge is read this far inside it
SAMPLE_M = 0.25                 # the edges are walked every this many metres
END_PROBE_M = 0.10              # a path's end meets what lies this far past it (grading.JOIN_PROBE_M)
DROP_LOOK_M = 0.60              # a dead end's surface this far past or beside its end is the drop it stops at
GATE_M = 0.30                   # a path end this close to the plot's edge (or past it) is a way in from outside
BUILDING_M = 0.50               # a path end this close to a building arrives at it
RAIL_GAP_M = 0.03               # a step across a railing or a handrail this close to it is blocked
USE_KINDS = ("terrace", "pool", "parking")
STREET_KINDS = ("road", "pavement")             # the outside roads (site.outside_roads); grading.walk_surfaces


# --------------------------------------------------------------------------
# Surfaces
# --------------------------------------------------------------------------

def _xy(poly) -> list[tuple[float, float]]:
    return [(float(q[0]), float(q[1])) for q in poly or []]


def _piece(poly, z: Optional[float] = None, fn: Optional[Callable] = None, holes=()) -> Optional[dict]:
    pts = geom2d.clean_polygon(_xy(poly))
    if len(pts) < 3 or abs(G.polygon_signed_area(pts)) < 1e-6:
        return None
    pts = geom2d.ccw(pts)
    return {"poly": pts, "box": G.bbox(pts), "z": None if z is None else float(z), "fn": fn,
            "holes": [geom2d.ccw(_xy(h)) for h in holes or () if len(h or []) >= 3]}


def _in_piece(pc: dict, p, tol: float = 0.0) -> bool:
    x0, y0, x1, y1 = pc["box"]
    if not (x0 - tol <= p[0] <= x1 + tol and y0 - tol <= p[1] <= y1 + tol):
        return False
    inside = G.point_in_polygon(p, pc["poly"])
    if not inside and (tol <= 0.0 or geom2d.distance_to_polygon_edges(p, pc["poly"]) > tol):
        return False
    return not any(G.point_in_polygon(p, h) and geom2d.distance_to_polygon_edges(p, h) > tol for h in pc["holes"])


def _piece_z(pc: dict, p) -> Optional[float]:
    if pc["z"] is not None:
        return pc["z"]
    try:
        z = pc["fn"](p)
    except (KeyError, TypeError, ValueError, ZeroDivisionError):
        return None
    return None if z is None else float(z)


def node_piece(node: dict, p, tol: float = 0.0) -> Optional[dict]:
    """The piece of a surface under the point ``p`` (pure), or None."""
    return next((pc for pc in node["pieces"] if _in_piece(pc, p, tol)), None)


def level_at(node: dict, p, tol: float = INSIDE_M) -> Optional[float]:
    """The walking level of a surface at ``p`` (pure; within ``tol`` of its edge), None off it."""
    pc = node_piece(node, p, tol)
    return None if pc is None else _piece_z(pc, p)


def _node(nid: str, kind: str, name: str, element, pieces, use: bool = False, **extra) -> Optional[dict]:
    pieces = [pc for pc in pieces if pc is not None]
    if not pieces:
        return None
    xs = [b for pc in pieces for b in (pc["box"][0], pc["box"][2])]
    ys = [b for pc in pieces for b in (pc["box"][1], pc["box"][3])]
    return {"id": nid, "kind": kind, "name": name, "element": element, "pieces": pieces, "use": use,
            "box": (min(xs), min(ys), max(xs), max(ys)), **extra}


def _strip(mid, out, d0: float, d1: float, s0: float, s1: float) -> list:
    """The plan rectangle ``d0``-``d1`` out of ``mid`` along ``out`` and ``s0``-``s1`` across it (pure)."""
    ux, uy = -out[1], out[0]
    return [(mid[0] + out[0] * d + ux * s, mid[1] + out[1] * d + uy * s)
            for d, s in ((d0, s0), (d1, s0), (d1, s1), (d0, s1))]


def _rect(mid, out, d0: float, d1: float, half: float) -> list:
    return _strip(mid, out, d0, d1, -half, half)


def _ramp_fn(ramp: dict) -> Callable:
    poly = _xy(ramp["polygon"])
    a = ((poly[0][0] + poly[3][0]) / 2.0, (poly[0][1] + poly[3][1]) / 2.0)
    b = ((poly[1][0] + poly[2][0]) / 2.0, (poly[1][1] + poly[2][1]) / 2.0)
    length = max(G.distance(a, b), 1e-6)
    u = ((b[0] - a[0]) / length, (b[1] - a[1]) / length)
    z0, z1 = float(ramp["z_start"]), float(ramp["z_end"])

    def fn(p):
        t = min(1.0, max(0.0, ((p[0] - a[0]) * u[0] + (p[1] - a[1]) * u[1]) / length))
        return z0 + (z1 - z0) * t
    return fn


def plot_of(site: dict) -> list[tuple[float, float]]:
    """The plot a site plan builds on (pure): the drawn plot, else the inferred one (an empty list when neither)."""
    return _xy(site.get("plot") or (site.get("inferred") or {}).get("plot") or [])


def outside_doors(site: dict) -> list[dict]:
    """The outside doors a person walks out of (pure): the architect's record (``site["outside_doors"]``: every door
    in an outer wall with its landing point and bottom level, A6), else the entrances of the site plan
    (``inferred.entrances``). ``[{"id", "point", "z", "main"}]``."""
    rec = site.get("outside_doors")
    if isinstance(rec, list):
        return [d for d in rec if isinstance(d, dict) and d.get("point")]
    inf = site.get("inferred") or {}
    mains = set(str(x) for x in (inf.get("main") or {}).get("opening_ids") or [])
    out = []
    for e in inf.get("entrances") or []:
        if not e.get("centre") or not e.get("outward"):
            continue
        (cx, cy), (ox, oy) = e["centre"], e["outward"]
        reach = float(e.get("half_t") or 0.1) + 0.4
        out.append({"id": str(e.get("opening_id")), "point": [cx + ox * reach, cy + oy * reach],
                    "z": float(e.get("bottom") or 0.0), "main": str(e.get("opening_id")) in mains
                    or bool((e.get("record") or {}).get("main"))})
    return out


def walk_graph(site: dict) -> dict:
    """The walk graph of a site plan (pure; module docstring): ``{"nodes": [...], "edges": {(a, b): joint},
    "contacts": {(a, b): joint}, "starts": {node id: why}, "doors": [...], "barriers", "rails", "gz"}``; a joint is
    ``{"dz", "at", "kind": touch | flight}`` (``dz`` the smallest level difference found along it, ``at`` where);
    ``edges`` keeps the joints of at most one step, ``contacts`` every touch (the drops too)."""
    from wenart.blender import grading as GR
    from wenart.blender import site as S

    terrain = GR.plan_terrain(site)
    gz = (lambda x, y: S.ground_z(terrain, x, y)) if terrain else (lambda x, y: 0.0)
    gzp = (lambda p: gz(p[0], p[1]))
    nodes: list[dict] = []
    barriers: list[list] = []
    rails: list[tuple] = []
    flight_edges: list[tuple] = []

    def add(n):
        if n is not None:
            nodes.append(n)
        return n

    # the buildings and the pools stand between surfaces
    barriers += [_xy(p) for p in [site.get("outline") or []] + list(site.get("copy_holes") or []) if len(p) >= 3]
    barriers += [_xy(p["polygon"]) for p in site.get("pools") or [] if len(p.get("polygon") or []) >= 3]
    try:
        hedges = S.hedge_records(site)
    except (KeyError, TypeError, ValueError):
        hedges = list(site.get("hedges") or [])
    for h in hedges:
        barriers += [_xy(p) for p in S._hedge_footprints(h)]
    for pf in site.get("platforms") or []:
        poly = pf.get("polygon") or []
        if pf.get("parent") or len(poly) < 3 or not isinstance(pf.get("z"), (int, float)):
            continue                                     # a terrace's planted tier is a bed, no walk
        kind = str(pf.get("kind") or "terrace")
        name = f"{'pool deck' if pf.get('pools') else kind} {pf['id']}"
        holes = list(pf.get("holes") or []) + [c["polygon"] for c in pf.get("cuts") or [] if c.get("polygon")]
        pc = _piece(poly, None if pf.get("sloped") else float(pf["z"]), gzp if pf.get("sloped") else None, holes)
        me = add(_node(f"platform:{pf['id']}", "platform", name, pf["id"], [pc], use=kind in USE_KINDS,
                       platform_kind=kind, elevated=bool(pf.get("elevated")), z=float(pf["z"])))
        if me is None:
            continue
        ring = geom2d.ccw(_xy(poly))
        n = len(ring)
        for i in pf.get("railing_edges") or []:
            if not 0 <= int(i) < n:
                continue
            for a, b in S.railing_runs(ring[int(i)], ring[(int(i) + 1) % n], int(i), pf):
                rails.append((tuple(a[:2]), tuple(b[:2])))
        if pf.get("steps_edge") is None or pf.get("sloped") or pf.get("steps_edge") in (pf.get("shared_edges") or []):
            continue
        fl = GR.down_flight(pf, gz) if pf.get("steps_dir") != "up" else None
        if fl is not None:
            foot = add(_node(f"foot:{pf['id']}", "foot", f"the foot landing of the flight of {pf['id']}", pf["id"],
                             [_piece(fl["foot"], float(fl["foot_z"]))], z=float(fl["foot_z"])))
            barriers += [_xy(c["polygon"]) for c in fl["cheeks"]]
            if foot is not None:
                flight_edges.append((me["id"], foot["id"], {"dz": round(float(fl["foot_z"]) - float(pf["z"]), 3),
                                                            "at": [round(float(fl["mid"][0]), 3),
                                                                   round(float(fl["mid"][1]), 3)],
                                                            "kind": "flight", "risers": fl["count"]}))
        up = None
        if pf.get("steps_dir") == "up":
            up = pf.get("flight") if isinstance(pf.get("flight"), dict) else S.up_flight(pf, terrain)
        if up:
            tread, half, t = S.PLATFORM["step_tread"], float(up["half_w"]), S.PLATFORM["wall_t"]
            mid, out, d = up["mid"], up["out"], float(up["length"])
            top_z = float(pf["z"]) + float(up["rise"])
            d0, d1 = (-tread, 0.0) if up.get("inward") else (d - tread, d)
            top = add(_node(f"top:{pf['id']}", "top", f"the top step of the flight of {pf['id']}", pf["id"],
                            [_piece(_rect(mid, out, d0, d1, half), top_z)], z=top_z))
            lo, hi = (-d, 0.0) if up.get("inward") else (0.0, d)
            barriers += [_strip(mid, out, lo, hi, half, half + t), _strip(mid, out, lo, hi, -half - t, -half)]
            if top is not None:
                flight_edges.append((me["id"], top["id"], {"dz": round(float(up["rise"]), 3),
                                                           "at": [round(float(mid[0]), 3), round(float(mid[1]), 3)],
                                                           "kind": "flight", "risers": up.get("count")}))
    # the paths as the grading builds them (a route's corner landing has no ends of its own: its legs meet it)
    corners = {str(a.get("id")) for a in site.get("areas") or [] if a.get("kind") == "path" and a.get("landing")}
    for rec in GR.graded_paths(site):
        pid = str(rec.get("id"))
        if rec.get("graded") and rec.get("frame"):
            fr = rec["frame"]
            pcs = [_piece(GR._slice(fr, s["t0"], s["t1"]), None, (lambda p, r=rec: GR.level_on(r, p)))
                   for s in rec["slices"] if not s.get("skip") and s["t1"] - s["t0"] > 1e-3]
            if rec.get("kind") == "stepped":
                r = GR.stair_rail(rec, gz)
                for line in (r or {}).get("pieces") or []:
                    rails += [(tuple(a[:2]), tuple(b[:2])) for a, b in zip(line, line[1:])]
        else:
            pcs = [_piece(rec.get("polygon") or [], None, gzp)]
        add(_node(f"path:{pid}", "path", f"path {pid}", pid, pcs, rec=rec, corner=pid in corners))
    # the entrances: their landings, steps and ramps (the doors open onto them)
    for st in (site.get("inferred") or {}).get("steps") or []:
        pcs = [_piece(b["polygon"], float(b["z_top"])) for b in st.get("blocks") or []
               if len(b.get("polygon") or []) >= 3]
        if isinstance(st.get("ramp"), dict) and len(st["ramp"].get("polygon") or []) >= 3:
            pcs.append(_piece(st["ramp"]["polygon"], None, _ramp_fn(st["ramp"])))
        barriers += [_xy(c["polygon"]) for c in st.get("cheeks") or [] if len(c.get("polygon") or []) >= 3]
        for a, b in st.get("rails") or []:
            rails.append((tuple(a[:2]), tuple(b[:2])))
        add(_node(f"entrance:{st.get('opening_id')}", "entrance", f"the entrance of {st.get('opening_id')}",
                  st.get("opening_id"), pcs, use=True))
    # the streets and pavements outside the plot (draped on the ground)
    add(_node("street", "street", "the street", "street",
              [_piece(a["polygon"], None, gzp) for a in site.get("areas") or []
               if str(a.get("kind") or "") in STREET_KINDS and len(a.get("polygon") or []) >= 3]))
    by_id = {n["id"]: n for n in nodes}
    contacts = _contacts(nodes, barriers, rails)
    for a, b, j in flight_edges:                         # the flight joins its platform and its landing (its own joint)
        key = (a, b) if a < b else (b, a)
        contacts[key] = j if key[0] == a else dict(j, dz=-j["dz"])
    edges = {k: j for k, j in contacts.items() if j["kind"] == "flight" or abs(j["dz"]) <= STEP_MAX_M + 1e-9}
    starts, doors = _starts(site, nodes, by_id)
    return {"nodes": nodes, "by_id": by_id, "contacts": contacts, "edges": edges, "starts": starts, "doors": doors,
            "barriers": barriers, "rails": rails, "gz": gz}


def _boundary(pc: dict, step: float = SAMPLE_M):
    """Points along a piece's outer edge, each with the outward normal of its edge (counter-clockwise ring)."""
    ring = pc["poly"]
    n = len(ring)
    for i in range(n):
        a, b = ring[i], ring[(i + 1) % n]
        length = G.distance(a, b)
        if length < 1e-6:
            continue
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        k = max(1, int(math.ceil(length / step)))
        for j in range(k):
            t = length * (j + 0.5) / k
            yield (a[0] + ux * t, a[1] + uy * t), (uy, -ux)


def _seg_dist(p, q, a, b) -> float:
    """The smallest distance between the segments ``p``-``q`` and ``a``-``b`` (pure)."""
    def cross(o, s, t):
        return (s[0] - o[0]) * (t[1] - o[1]) - (s[1] - o[1]) * (t[0] - o[0])
    d1, d2, d3, d4 = cross(a, b, p), cross(a, b, q), cross(p, q, a), cross(p, q, b)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)):
        return 0.0
    return min(G.point_segment_distance(p, a, b), G.point_segment_distance(q, a, b),
               G.point_segment_distance(a, p, q), G.point_segment_distance(b, p, q))


def _contacts(nodes: list[dict], barriers: list, rails: list) -> dict:
    """``{(a, b): {"dz", "at", "kind": "touch", "samples"}}``: every pair of surfaces that touch, the smallest level
    difference along the touch and where (pure)."""
    bars = [(G.bbox(b), b) for b in barriers if len(b) >= 3]
    out: dict = {}
    for a in nodes:
        ax0, ay0, ax1, ay1 = a["box"]
        near = [b for b in nodes if b is not a and not (b["box"][0] > ax1 + TOUCH_M or b["box"][2] < ax0 - TOUCH_M
                                                         or b["box"][1] > ay1 + TOUCH_M or b["box"][3] < ay0 - TOUCH_M)]
        if not near:
            continue
        for pc in a["pieces"]:
            for q, nrm in _boundary(pc):
                p_in = (q[0] - nrm[0] * INSIDE_M, q[1] - nrm[1] * INSIDE_M)
                p_near = (q[0] + nrm[0] * NEAR_M, q[1] + nrm[1] * NEAR_M)
                p_far = (q[0] + nrm[0] * TOUCH_M, q[1] + nrm[1] * TOUCH_M)
                if node_piece(a, p_near) is not None:
                    continue                             # an inner joint between two pieces of one surface
                za = _piece_z(pc, p_in)
                if za is None:
                    continue
                for b in near:
                    hit, probe = None, None
                    for pr in (p_near, p_far):
                        hit = node_piece(b, pr)
                        if hit is not None:
                            probe = pr
                            break
                    if hit is None:
                        continue
                    if probe is p_far and any(bx[0] <= p_near[0] <= bx[2] and bx[1] <= p_near[1] <= bx[3]
                                              and G.point_in_polygon(p_near, poly) for bx, poly in bars):
                        continue                         # a cheek wall, a hedge, a building between them
                    if any(_seg_dist(p_in, probe, r0, r1) <= RAIL_GAP_M for r0, r1 in rails):
                        continue                         # a railing or a handrail between them
                    zb = _piece_z(hit, probe)
                    if zb is None:
                        continue
                    key = (a["id"], b["id"]) if a["id"] < b["id"] else (b["id"], a["id"])
                    dz = (zb - za) if key[0] == a["id"] else (za - zb)
                    cur = out.get(key)
                    if cur is None or abs(dz) < abs(cur["dz"]) - 1e-9:
                        out[key] = {"dz": round(dz, 3), "at": [round(q[0], 3), round(q[1], 3)], "kind": "touch",
                                    "samples": (cur or {}).get("samples", 0) + 1}
                    else:
                        cur["samples"] = cur.get("samples", 0) + 1
    return out


def _starts(site: dict, nodes: list[dict], by_id: dict) -> tuple[dict, list[dict]]:
    """The start points: ``({node id: why}, doors)``; every door with the surface it opens onto (``node``, None when
    it opens onto no walkable surface)."""
    starts: dict = {}
    if "street" in by_id:
        starts["street"] = "the street and its pavements"
    for n in nodes:
        if n["kind"] == "platform" and n.get("platform_kind") == "parking":
            starts[n["id"]] = f"the parking {n['element']} (the cars arrive there)"
    plot = plot_of(site)
    if len(plot) >= 3:
        from wenart.blender import grading as GR
        for n in nodes:
            if n["kind"] != "path" or n.get("corner"):
                continue
            fr = (n.get("rec") or {}).get("frame") or GR.strip_frame((n.get("rec") or {}).get("polygon") or [])
            if fr is None:
                continue
            for t, sign in ((0.0, -1.0), (fr["length"], 1.0)):
                if _at_gate(GR._at(fr, t), GR._at(fr, t + sign * GATE_M), plot):
                    starts.setdefault(n["id"], f"{n['name']} reaches the plot's edge (a way in from outside)")
    doors = []
    for d in outside_doors(site):
        p = (float(d["point"][0]), float(d["point"][1]))
        z = float(d.get("z") or 0.0)
        best = None
        for n in nodes:
            if n["kind"] == "street":
                continue
            lv = level_at(n, p, tol=0.1)
            if lv is not None and abs(lv - z) <= STEP_MAX_M + 1e-9 and (best is None or abs(lv - z) < best[0]):
                best = (abs(lv - z), n)
        if best is None:
            ent = by_id.get(f"entrance:{d['id']}")
            best = (0.0, ent) if ent is not None else None
        doors.append(dict(d, node=best[1]["id"] if best else None))
        if best is not None:
            starts.setdefault(best[1]["id"], f"door {d['id']} of the house")
    return starts, doors


def _at_gate(p_end, p_out, plot) -> bool:
    """Whether a path end at ``p_end`` heading to ``p_out`` (``GATE_M`` past it) leaves the plot there: the end lies
    outside the plot, or the point past it does (a way in from the street or a gate)."""
    return not G.point_in_polygon(p_end, plot) or not G.point_in_polygon(p_out, plot) \
        or geom2d.distance_to_polygon_edges(p_out, plot) <= 0.02


def reach(graph: dict, starts) -> set:
    """The surfaces a person walks to from ``starts`` along the graph's edges (pure)."""
    adj: dict = {}
    for a, b in graph["edges"]:
        adj.setdefault(a, set()).add(b)
        adj.setdefault(b, set()).add(a)
    seen = set(s for s in starts if s in graph["by_id"])
    todo = list(seen)
    while todo:
        n = todo.pop()
        for m in adj.get(n, ()):
            if m not in seen:
                seen.add(m)
                todo.append(m)
    return seen


def _touching(graph: dict, nid: str, steps_only: bool = True) -> list[tuple[str, dict]]:
    """The surfaces touching ``nid`` with their joints, ``dz`` turned to the other surface's level less ``nid``'s."""
    out = []
    for (a, b), j in (graph["edges"] if steps_only else graph["contacts"]).items():
        if nid == a:
            out.append((b, j))
        elif nid == b:
            out.append((a, dict(j, dz=-j["dz"])))
    return out


def _centre(node: dict) -> list[float]:
    pts = [q for pc in node["pieces"] for q in pc["poly"]]
    big = max(node["pieces"], key=lambda pc: abs(G.polygon_signed_area(pc["poly"])))
    c = G.polygon_centroid(big["poly"]) if pts else (0.0, 0.0)
    return [round(c[0], 3), round(c[1], 3)]


def _gap(a: dict, b: dict) -> float:
    """The plan distance between two surfaces (pure; their pieces' corners and edges)."""
    best = math.inf
    for pa in a["pieces"]:
        for pb in b["pieces"]:
            if any(G.point_in_polygon(q, pb["poly"]) for q in pa["poly"]) or \
                    any(G.point_in_polygon(q, pa["poly"]) for q in pb["poly"]):
                return 0.0
            best = min(best, min(geom2d.distance_to_polygon_edges(q, pb["poly"]) for q in pa["poly"]),
                       min(geom2d.distance_to_polygon_edges(q, pa["poly"]) for q in pb["poly"]))
    return best


def nearest_reached(graph: dict, target: dict, reached: set) -> Optional[dict]:
    """The reached surface nearest an unreached one (pure): ``{"node", "gap_m", "dz"}`` (``dz``: the target's level
    less the reached surface's, at their nearest points), or None."""
    best = None
    for nid in reached:
        n = graph["by_id"].get(nid)
        if n is None or n["kind"] == "street":
            continue
        g = _gap(n, target)
        if best is None or g < best[1] - 1e-9:
            best = (n, g)
    if best is None:
        return None
    n = best[0]
    zt = target.get("z")
    zn = n.get("z")
    if zt is None:
        zt = _piece_z(target["pieces"][0], target["pieces"][0]["poly"][0])
    if zn is None:
        c = min((q for pc in n["pieces"] for q in pc["poly"]),
                key=lambda q: min(geom2d.distance_to_polygon_edges(q, pc2["poly"]) for pc2 in target["pieces"]))
        zn = level_at(n, c, tol=0.05)
    dz = None if zt is None or zn is None else round(float(zt) - float(zn), 3)
    return {"node": n["id"], "name": n["name"], "gap_m": round(best[1], 2), "dz": dz}


# --------------------------------------------------------------------------
# Path ends
# --------------------------------------------------------------------------

def path_ends(graph: dict, site: dict) -> list[dict]:
    """Where every path end arrives (pure): ``[{"path", "end": start | end, "at", "z", "to": node id or None, "dz",
    "kind": joint | building | gate | side | drop | short | dead_end, ...}]``. ``joint``: a surface lies past the end
    (``dz`` its level less the end's); ``side``: none past it, one beside its end landing within a step; ``building``,
    ``gate``: the end arrives at a building or the plot's edge; ``drop``: nothing within a step touches it, the nearest
    surface within ``DROP_LOOK_M`` past or beside it lies more than a step higher or lower (the jump); ``short``: that
    surface is within a step but a strip of lawn lies between (``gap_m``); ``dead_end``: nothing at all."""
    from wenart.blender import grading as GR

    plot = plot_of(site)
    buildings = [_xy(p) for p in [site.get("outline") or []] + list(site.get("copy_holes") or []) if len(p) >= 3]
    out = []
    for n in graph["nodes"]:
        if n["kind"] != "path":
            continue
        rec = n.get("rec") or {}
        fr = rec.get("frame") or GR.strip_frame(rec.get("polygon") or [])
        if fr is None:
            continue
        L, w = float(fr["length"]), float(fr["width"])
        end_m = min(GR.GRADE["end_landing_m"], max(w, 0.6), L / 2.0)
        for key, t_end, sign in (("start", 0.0, -1.0), ("end", L, 1.0)):
            p_end = GR._at(fr, t_end - sign * INSIDE_M * 2.0)
            z_end = level_at(n, p_end, tol=0.05)
            if z_end is None:
                z_end = graph["gz"](*p_end)
            rec_end = {"path": n["element"], "node": n["id"], "end": key,
                       "at": [round(GR._at(fr, t_end)[0], 3), round(GR._at(fr, t_end)[1], 3)], "z": round(z_end, 3)}
            past = [GR._at(fr, t_end + sign * END_PROBE_M, s * w / 2.0) for s in (0.0, -0.6, 0.6)]
            hit = None
            for p in past:
                for m in graph["nodes"]:
                    if m is n:
                        continue
                    lv = level_at(m, p, tol=0.0)
                    if lv is not None:
                        hit = (m, lv)
                        break
                if hit:
                    break
            if n.get("corner") and (hit is None or hit[0]["kind"] not in ("foot", "top", "entrance")):
                continue                # a route's corner landing: only the flight or the door its route starts at is
                #                         a joint of it; its open sides are no dead ends (grading.graded_paths)
            if hit is not None:
                out.append(dict(rec_end, kind="joint", to=hit[0]["id"], to_name=hit[0]["name"],
                                dz=round(hit[1] - z_end, 3)))
                continue
            if any(geom2d.distance_to_polygon_edges(p, b) <= BUILDING_M or G.point_in_polygon(p, b)
                   for b in buildings for p in past):
                out.append(dict(rec_end, kind="building", to=None, dz=None))
                continue
            if len(plot) >= 3 and _at_gate(GR._at(fr, t_end), GR._at(fr, t_end + sign * GATE_M), plot):
                out.append(dict(rec_end, kind="gate", to=None, dz=None))
                continue
            # beside the end landing: a surface within a step there joins it sideways
            side = []
            for d in (NEAR_M, TOUCH_M, 0.3, 0.45, DROP_LOOK_M):
                for s in (-1.0, 1.0):
                    for f in (0.25, 0.5, 0.75):
                        t = t_end - sign * end_m * f
                        side.append((d, GR._at(fr, t, s * (w / 2.0 + d))))
                for f in (0.0, -0.4, 0.4):
                    side.append((d, GR._at(fr, t_end + sign * d, f * w)))
            touch, near = None, None
            for d, p in side:
                for m in graph["nodes"]:
                    if m is n:
                        continue
                    lv = level_at(m, p, tol=0.0)
                    if lv is None:
                        continue
                    dz = lv - z_end
                    if d <= TOUCH_M + 1e-9 and abs(dz) <= STEP_MAX_M + 1e-9 and (touch is None or abs(dz) < touch[1]):
                        touch = (m, dz)
                    if near is None or (d, abs(dz)) < (near[2], abs(near[1])):
                        near = (m, dz, d, p)
            if touch is not None:
                out.append(dict(rec_end, kind="side", to=touch[0]["id"], to_name=touch[0]["name"],
                                dz=round(touch[1], 3)))
            elif near is not None:
                # a surface just past or beside it: at another level a drop (the jump), else a strip of lawn between
                m, dz, d, p = near
                out.append(dict(rec_end, kind="drop" if abs(dz) > STEP_MAX_M else "short", to=m["id"],
                                to_name=m["name"], dz=round(dz, 3), gap_m=round(d, 2),
                                toward=[round(p[0], 3), round(p[1], 3)]))
            else:
                out.append(dict(rec_end, kind="dead_end", to=None, dz=None))
    return out


# --------------------------------------------------------------------------
# The check
# --------------------------------------------------------------------------

def _designated(graph: dict) -> bool:
    """Whether the site has designated ways (paths or streets): else the garden itself is the way (no dead ends)."""
    return any(n["kind"] in ("path", "street") for n in graph["nodes"])


def _f(severity: str, target, message: str, problem: str, **metrics) -> dict:
    from wenart.blender import grading as GR
    return GR._f(severity, target, message, RULE, "no_sense", problem=problem,
                 user_review="real04 run 20261030-181158-full", **metrics)


def analyse(site: dict) -> dict:
    """The walk of a site plan (pure): ``{"graph", "reached", "street_reached", "ends", "findings"}``."""
    graph = walk_graph(site)
    by_id = graph["by_id"]
    reached = reach(graph, graph["starts"])
    street_starts = [k for k, why in graph["starts"].items() if not why.startswith("door ")]
    street_reached = reach(graph, street_starts) if street_starts else set()
    findings: list[dict] = []
    designated = _designated(graph)
    doors_known = isinstance(site.get("outside_doors"), list)
    # the areas meant for use: every one reached from a start
    for n in graph["nodes"]:
        if not n.get("use") or n["id"] in reached:
            continue
        if n.get("elevated") and not doors_known:
            continue                                     # a balcony on columns: its door is not recorded here
        near = nearest_reached(graph, n, reached)
        how = ""
        if near is not None:
            # ``dz``: the area's level less the reached surface's (the area lies lower when negative)
            lv = "" if near["dz"] is None else (f", {abs(near['dz']):.2f} m {'higher' if near['dz'] < 0 else 'lower'}"
                                                 if abs(near["dz"]) > LEVEL_TOL_M else ", at its level")
            how = f"; the nearest surface a person reaches, {near['name']}, lies {near['gap_m']:.1f} m away{lv}"
        findings.append(_f("major", n["element"], f"nobody can walk to {n['name']}: no path, step, flight or door "
                           f"leads to it from the street or the house{how} (every outdoor area is reached along "
                           f"designated paths)", "unreachable", at=_centre(n), node=n["id"], nearest=near))
    # the arrival: the main entrance from the street
    if street_starts:
        mains = [d for d in graph["doors"] if d.get("main")]
        if mains and not any(d.get("node") in street_reached for d in mains):
            d = mains[0]
            findings.append(_f("major", d["id"], f"no walk leads from the street to the main entrance {d['id']} along "
                               f"the designated paths (the paths, terraces and flights from the street never reach "
                               f"its landing)", "arrival", at=[round(float(d["point"][0]), 3),
                                                               round(float(d["point"][1]), 3)]))
    # flights: both ends on a walkable surface
    if designated:
        for n in graph["nodes"]:
            if n["kind"] not in ("foot", "top"):
                continue
            on = [m for m, j in _touching(graph, n["id"]) if j["kind"] != "flight"]
            if on:
                continue
            drops = [(m, j) for m, j in _touching(graph, n["id"], steps_only=False) if j["kind"] != "flight"]
            what = "its foot" if n["kind"] == "foot" else "its top"
            if drops:
                m, j = min(drops, key=lambda mj: abs(mj[1]["dz"]))
                msg = (f"the flight of {n['element']} ends at a drop: {what} meets {by_id[m]['name']} "
                       f"{abs(j['dz']):.2f} m {'lower' if j['dz'] < 0 else 'higher'} with no step between (a flight "
                       f"lands on a walkable surface at both ends; a person would have to jump)")
                findings.append(_f("major", n["element"], msg, "dead_flight", at=j["at"], node=n["id"],
                                   dz_m=j["dz"], to=m))
            else:
                findings.append(_f("major", n["element"], f"the flight of {n['element']} ends on the lawn: no path, "
                                   f"terrace or landing at {what} (a flight lands on a walkable surface at both ends)",
                                   "dead_flight", at=_centre(n), node=n["id"]))
        for n in graph["nodes"]:
            if n["kind"] != "entrance" or _touching(graph, n["id"]):
                continue
            findings.append(_f("minor", n["element"], f"{n['name']} lands on the lawn: no path or terrace leads on "
                               f"from its landing or steps", "dead_flight", at=_centre(n), node=n["id"]))
    # path ends: level at the surface they arrive at; never a dead end
    ends = path_ends(graph, site) if designated else []
    joins = {}
    for n in graph["nodes"]:
        for j in ((n.get("rec") or {}).get("joins") or []):
            if j.get("kind") in ("path", "landing"):
                joins[(n["id"], j["end"])] = j["to"]
    for e in ends:
        pid = e["path"]
        where = "starts" if e["end"] == "start" else "ends"
        if e["kind"] == "joint" and abs(e["dz"]) > LEVEL_TOL_M:
            to = e["to"]
            g14 = joins.get((e["node"], e["end"]))
            if g14 is not None and (to == f"path:{g14}" or to == f"entrance:{str(g14).split(':')[-1]}"):
                continue                                 # G14 measures a join it planned
            big = abs(e["dz"]) > STEP_MAX_M
            msg = (f"path {pid} {where} {abs(e['dz']) * 100:.0f} cm {'below' if e['dz'] > 0 else 'above'} "
                   f"{e['to_name']}: " + ("a drop at the joint, a person would have to jump (two walks meet level "
                                          "or by a flight with landings)" if big else
                                          "a raw step at the joint (two walks meet level)"))
            findings.append(_f("major", pid, msg, "junction_drop" if big else "junction_step", at=e["at"],
                               node=e["node"], end=e["end"], to=to, dz_m=e["dz"]))
        elif e["kind"] == "drop":
            findings.append(_f("major", pid, f"path {pid} {where} at a drop: {e['to_name']} lies {e['gap_m']:.2f} m "
                               f"past it {abs(e['dz']):.2f} m {'lower' if e['dz'] < 0 else 'higher'} with no step "
                               f"or flight between (a person would have to jump; a path arrives at its destination)",
                               "dead_end_drop", at=e["at"], node=e["node"], end=e["end"], to=e["to"], dz_m=e["dz"],
                               gap_m=e["gap_m"]))
        elif e["kind"] == "short":
            findings.append(_f("minor", pid, f"path {pid} {where} {e['gap_m']:.2f} m short of {e['to_name']}, a strip "
                               f"of lawn between them (a path arrives at its destination)", "dead_end", at=e["at"],
                               node=e["node"], end=e["end"], to=e["to"], dz_m=e["dz"], gap_m=e["gap_m"]))
        elif e["kind"] == "dead_end":
            findings.append(_f("minor", pid, f"path {pid} {where} on the lawn with no destination: no path, terrace, "
                               f"door or gate at its end (a path leads somewhere)", "dead_end", at=e["at"],
                               node=e["node"], end=e["end"]))
    return {"graph": graph, "reached": reached, "street_reached": street_reached, "ends": ends,
            "findings": findings}


def review(site: Optional[dict]) -> tuple[list[dict], int]:
    """G15 on a site plan (pure; module docstring): ``(findings, checked)`` in the model review's format."""
    if not site or not site.get("terrain"):
        return [], 0
    rec = analyse(site)
    checked = sum(1 for n in rec["graph"]["nodes"] if n.get("use") or n["kind"] in ("foot", "top")) + len(rec["ends"])
    return rec["findings"], checked


def walk_log(site: dict, rec: Optional[dict] = None) -> dict:
    """The log of the walk (pure; JSON): the starts, every surface with its level and whether it is reached, every
    joint with its height, the path ends and the findings (with their places)."""
    rec = rec or analyse(site)
    g = rec["graph"]
    surfaces = []
    for n in g["nodes"]:
        z = n.get("z")
        surfaces.append({"id": n["id"], "kind": n["kind"], "name": n["name"], "use": bool(n.get("use")),
                         "z": None if z is None else round(float(z), 3), "at": _centre(n),
                         "reached": n["id"] in rec["reached"], "start": g["starts"].get(n["id"])})
    joints = [{"a": a, "b": b, "dz_m": j["dz"], "at": j["at"], "kind": j["kind"],
               "walkable": j["kind"] == "flight" or abs(j["dz"]) <= STEP_MAX_M + 1e-9}
              for (a, b), j in sorted(g["contacts"].items())]
    use = [s for s in surfaces if s["use"]]
    return {"rule": f"{RULE}: a person walks along the designated paths from the street and every outside door to "
                    f"every outdoor area; surfaces join where they touch with at most a {STEP_MAX_M:.2f} m step, or by "
                    f"a flight that lands on a walkable surface at both ends",
            "starts": [{"node": k, "why": v} for k, v in g["starts"].items()],
            "doors": [{"id": d["id"], "on": d.get("node"), "main": bool(d.get("main"))} for d in g["doors"]],
            "surfaces": surfaces, "joints": joints,
            "ends": [{k: v for k, v in e.items() if k != "node"} for e in rec["ends"]],
            "reached": sorted(rec["reached"]), "areas": len(use), "areas_reached": sum(1 for s in use if s["reached"]),
            "findings": [{"severity": f["severity"], "target": f["target"], "message": f["message"],
                          "problem": f["metrics"].get("problem"), "at": f["metrics"].get("at")}
                         for f in rec["findings"]]}
