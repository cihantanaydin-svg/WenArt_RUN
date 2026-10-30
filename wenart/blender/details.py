"""Architectural details built like real products (pure; 25 Oct 2026, user: "better architectural details needed,
better internal stairs, better finishes in the fences on top of the parapets, architect needs to understand what is
better architectural details and needs to do the changes").

What: the balustrades of balconies, terraces, parapets and pool decks and the parts of a stair's balustrade and wall
handrail, as meshes with a slot per face (0 metal, 1 glass). Three balustrade kinds:

- ``glass_channel``: frameless glass (``DIMS["glass_t"]``) clamped in a metal base channel (``channel_w`` x
  ``channel_h``) with a metal cap rail on its top edge; no posts (contemporary and minimal houses);
- ``glass_posts``: round posts with square base plates at most ``post_every`` apart, a glass bay between each pair
  held ``bay_gap`` off the posts, a round handrail on the posts (the default);
- ``bars``: vertical bars at most ``bar_pitch`` apart (gaps under 0.11 m) between a bottom rail and a round
  handrail, posts at the ends and at most ``post_every`` apart (classic, rustic, industrial, Mediterranean houses).

Why: the railings were one square bar on a glass slab with square posts, the stair rail one flat bar without
balusters and the stair steps plain blocks. A real balustrade has a handrail one can hold (round, 40-50 mm), an
infill that a child cannot pass, posts fixed by base plates, glass in a shoe or clamps; a real stair has a tread with
a nosing over the riser, a balustrade on its open side and a handrail on the wall side (``parametric.stair_parts``).

How: ``balustrade_kind(style)`` picks the kind from the project style (``style.json`` ``family`` and the railing slot
when it names glass or bars); ``balustrade(p, q, floor_z, height, kind)`` returns ``(metal meshes, glass meshes)``;
``tube`` is a round bar between two 3D points; ``coping(p, q, z, width)`` is the stone cap a railing stands on.

26 Oct 2026 (user on real06: "an unguarded stair void at the upper landing"; "The house needs to make sense"):

- What: ``void_guard_runs(void_polygon, walls, arrival_edges)`` finds the edges of a floor opening (a stair void cut
  out of the floor above the stair) that need a guard: every stretch of an edge that no wall runs along (within
  ``GUARD["wall_reach"]`` of the wall's face) and that is not where the stair comes up (``arrival_edges``: the top
  line of the stair's last flight, within ``GUARD["arrival_reach"]``); ``void_guards(...)`` builds a ``balustrade``
  of the house's kind, ``GUARD["height"]`` high, on each run, ``GUARD["inset"]`` back on the floor.
- Why: a flight's balustrade stands only on its open sides below; the floor above kept a bare edge over the stairwell
  (a fall of a storey), which no rule guarded.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

from wenart.blender import geom2d
from wenart import geometry as G

KINDS = ("glass_channel", "glass_posts", "bars")
# 30 Oct 2026 (lesson UL145, user on real04 run 20261029-201533-full: "better handrails in the terras is needed"): the
# glass channel's cap is a 50 mm handrail (a 28 mm cap read as a thin bare tube over glass that vanishes from outside)
DIMS = {"glass_t": 0.012, "channel_w": 0.06, "channel_h": 0.09, "cap_w": 0.05, "cap_h": 0.045,
        "handrail_r": 0.022, "post_r": 0.021, "post_every": 1.2, "plate": 0.10, "plate_t": 0.008,
        "bay_gap": 0.03, "glass_bottom": 0.06, "bar_w": 0.016, "bar_pitch": 0.115, "bottom_rail_z": 0.08,
        "flat_w": 0.05, "flat_t": 0.012, "tube_sides": 10, "coping_t": 0.05, "coping_proud": 0.03,
        "bracket_r": 0.008, "wall_gap": 0.06, "bracket_every": 1.0}
# 30 Oct 2026 (UL145): an outdoor guard's glass is a light low-iron grey-green (linear RGB), so its panel reads from
# outside instead of vanishing (materials.thin_glass_material ``tint``)
GUARD_GLASS_RGB = (0.80, 0.87, 0.85)
# Style families (wenart.style.vocabulary.STYLE_FAMILIES) and the balustrade a designer puts in them.
STYLE_KINDS = {"modern": "glass_channel", "minimal": "glass_channel", "modern minimal": "glass_channel",
               "contemporary": "glass_channel", "japandi": "bars", "scandinavian": "glass_posts",
               "industrial": "bars", "rustic": "bars", "classic": "bars", "mediterranean": "bars"}
DEFAULT_KIND = "glass_posts"


# 30 Oct 2026 (lesson UL209, user on real06's balcony between its two columns: "handrails not making sense"): a guard
# that columns frame needs no posts of its own (glass on posts with clamps set a thin second row of posts beside the
# columns): a glass family's guard there is frameless glass in a base channel under a slim cap; bars stay bars
FRAMED_KINDS = {"glass_posts": "glass_channel"}


def framed_kind(kind: str) -> str:
    """The balustrade kind of a guard that columns stand on (pure; lesson UL209, ``FRAMED_KINDS``)."""
    return FRAMED_KINDS.get(kind, kind)


def balustrade_kind(style: Optional[dict]) -> str:
    """The balustrade kind of a project (pure): a railing slot that names glass (``glass_channel``) or bars wins, else
    the style family's kind (``STYLE_KINDS``), else ``DEFAULT_KIND``."""
    style = style or {}
    rail = style.get("railing") if isinstance(style.get("railing"), dict) else {}
    words = " ".join(str(v) for v in (rail.get("material"), rail.get("style"), rail.get("kind")) if v).lower()
    if "glass" in words:
        return "glass_channel"
    if any(w in words for w in ("bar", "baluster", "spindle", "wrought")):
        return "bars"
    return STYLE_KINDS.get(str(style.get("family") or "").lower(), DEFAULT_KIND)


def _frame(d):
    """Two unit vectors square to the 3D direction ``d`` (the first horizontal when ``d`` is not vertical)."""
    dx, dy, dz = d
    if abs(dx) + abs(dy) < 1e-9:
        return (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)
    h = math.hypot(dx, dy)
    a = (-dy / h, dx / h, 0.0)                                   # horizontal, square to d
    b = (d[1] * a[2] - d[2] * a[1], d[2] * a[0] - d[0] * a[2], d[0] * a[1] - d[1] * a[0])
    n = math.sqrt(sum(c * c for c in b)) or 1.0
    return a, (b[0] / n, b[1] / n, b[2] / n)


def tube(p0, p1, r: float, sides: Optional[int] = None, phase: float = 0.5) -> tuple[list, list]:
    """``(verts, faces)`` of a round bar (a ``sides``-gon prism) of radius ``r`` from 3D point ``p0`` to ``p1``;
    ``phase`` 0 with ``sides`` a multiple of 4 puts a vertex on top (a handrail whose top is exact)."""
    sides = int(sides or DIMS["tube_sides"])
    d = [float(p1[k]) - float(p0[k]) for k in range(3)]
    length = math.sqrt(sum(c * c for c in d))
    if length < 1e-9:
        return [], []
    d = [c / length for c in d]
    a, b = _frame(d)
    verts = []
    for p in (p0, p1):
        for k in range(sides):
            t = 2.0 * math.pi * (k + phase) / sides
            ca, sb = math.cos(t) * r, math.sin(t) * r
            verts.append(tuple(float(p[j]) + a[j] * ca + b[j] * sb for j in range(3)))
    faces = [list(range(sides)), list(range(sides, 2 * sides))]
    faces += [[k, (k + 1) % sides, sides + (k + 1) % sides, sides + k] for k in range(sides)]
    return geom2d.convex_solid(verts, faces)


def _box_between(p, q, z0: float, z1: float, w: float, offset: float = 0.0) -> tuple[list, list]:
    """A box along ``p``-``q`` (plan), ``w`` thick across, from ``z0`` to ``z1``, its centre line ``offset`` to the
    left of the run."""
    length = G.distance(p, q)
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    mid = G.segment_midpoint(p, q)
    c = (mid[0] - uy * offset, mid[1] + ux * offset, (z0 + z1) / 2.0)
    return geom2d.box(c, (length, w, z1 - z0), G.segment_angle_deg(p, q))


def _posts_at(length: float, every: float, inset: float) -> list[float]:
    n = max(1, int(math.ceil(length / every - 1e-9)))
    return [min(max(length * i / n, inset), length - inset) for i in range(n + 1)]


def balustrade(p, q, floor_z: float, height: float = 1.0, kind: str = DEFAULT_KIND,
               dims: Optional[dict] = None, ends: tuple = (True, True)) -> tuple[list, list]:
    """``(metal, glass)``: lists of ``(verts, faces)`` of a balustrade along ``p``-``q`` standing on ``floor_z``,
    ``height`` to the top of its handrail (pure; see the module docstring for the kinds). ``ends``: False at an end
    that stops against a column (30 Oct 2026, lesson UL209): no post there, the rail and the glass run to the end
    (the column holds them; a post beside a column read as a second, thinner column)."""
    c = dict(DIMS, **(dims or {}))
    length = G.distance(p, q)
    if length < 0.05:
        return [], []
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    top = floor_z + float(height)
    metal, glass = [], []

    def at(s, z):
        return (p[0] + ux * s, p[1] + uy * s, z)

    if kind == "glass_channel":
        metal.append(_box_between(p, q, floor_z, floor_z + c["channel_h"], c["channel_w"]))
        metal.append(_box_between(p, q, top - c["cap_h"], top, c["cap_w"]))
        g0, g1 = floor_z + c["channel_h"] - 0.03, top - c["cap_h"] + 0.012
        glass.append(_box_between(p, q, g0, g1, c["glass_t"]))
        return metal, glass
    r = c["handrail_r"]
    metal.append(tube(at(0.0, top - r), at(length, top - r), r))
    posts = _posts_at(length, c["post_every"], c["post_r"])
    bays = list(posts)
    if not ends[0]:
        posts, bays[0] = posts[1:], -c["post_r"] - c["bay_gap"] + 0.005     # the glass runs to the column
    if not ends[1]:
        posts, bays[-1] = posts[:-1], length + c["post_r"] + c["bay_gap"] - 0.005
    for s in posts:
        metal.append(tube(at(s, floor_z + c["plate_t"]), at(s, top - 2 * r), c["post_r"]))
        x, y, _ = at(s, 0.0)
        metal.append(geom2d.box((x, y, floor_z + c["plate_t"] / 2.0), (c["plate"], c["plate"], c["plate_t"]),
                                G.segment_angle_deg(p, q)))
    if kind == "bars":
        z_b = floor_z + c["bottom_rail_z"]
        metal.append(_box_between(p, q, z_b, z_b + c["flat_t"] * 2, c["flat_w"] * 0.6))
        z0, z1 = z_b + c["flat_t"] * 2, top - 2 * r
        for t0, t1 in zip(bays, bays[1:]):                       # bars spread evenly in each bay
            a, b = t0 + c["post_r"], t1 - c["post_r"]
            n = max(1, int(math.ceil((b - a) / c["bar_pitch"] - 1e-9)))
            for k in range(1, n):
                x, y, _ = at(a + (b - a) * k / n, 0.0)
                metal.append(geom2d.box((x, y, (z0 + z1) / 2.0), (c["bar_w"], c["bar_w"], z1 - z0),
                                        G.segment_angle_deg(p, q)))
        return metal, glass
    for s0, s1 in zip(bays, bays[1:]):                           # glass_posts: one bay between two posts
        a, b = s0 + c["post_r"] + c["bay_gap"], s1 - c["post_r"] - c["bay_gap"]
        if b - a < 0.1:
            continue
        glass.append(_box_between((p[0] + ux * a, p[1] + uy * a), (p[0] + ux * b, p[1] + uy * b),
                                  floor_z + c["glass_bottom"], top - 2 * r - 0.06, c["glass_t"]))
        for s in (a + 0.02, b - 0.02):                           # a clamp at the top and the bottom of each edge
            for z in (floor_z + c["glass_bottom"] + 0.1, top - 2 * r - 0.16):
                x, y, _ = at(s, 0.0)
                metal.append(geom2d.box((x, y, z), (0.05, c["glass_t"] + 0.016, 0.05), G.segment_angle_deg(p, q)))
    return metal, glass


def coping(p, q, z: float, width: float, dims: Optional[dict] = None) -> tuple[list, list]:
    """The cap on a parapet or a low wall a railing stands on (pure): ``coping_t`` thick on ``z``, ``coping_proud``
    over each face of a wall ``width`` thick, a little longer than the run."""
    c = dict(DIMS, **(dims or {}))
    length = G.distance(p, q)
    if length < 0.05:
        return [], []
    ux, uy = (q[0] - p[0]) / length, (q[1] - p[1]) / length
    e = c["coping_proud"]
    return _box_between((p[0] - ux * e, p[1] - uy * e), (q[0] + ux * e, q[1] + uy * e), z, z + c["coping_t"],
                        float(width) + 2 * e)


def wall_handrail(path: Sequence[Sequence[float]], wall_side: Sequence[float], dims: Optional[dict] = None
                  ) -> list[tuple[list, list]]:
    """A round handrail along the 3D polyline ``path`` (its centre line) with a bracket to the wall at most
    ``bracket_every`` apart (pure): ``wall_side`` is the plan unit vector from the rail to the wall face, which lies
    ``wall_gap`` away."""
    c = dict(DIMS, **(dims or {}))
    out = []
    pts = [tuple(float(v) for v in q) for q in path]
    for a, b in zip(pts, pts[1:]):
        out.append(tube(a, b, c["handrail_r"]))
        length = math.dist(a, b)
        n = max(1, int(math.ceil(length / c["bracket_every"] - 1e-9)))
        for k in range(n + 1):
            if k == 0 and a is not pts[0]:
                continue
            t = min(max(k / n, 0.08), 0.92)
            m = tuple(a[j] + (b[j] - a[j]) * t for j in range(3))
            stem = (m[0], m[1], m[2] - c["handrail_r"] - 0.03)
            wall = (stem[0] + wall_side[0] * c["wall_gap"], stem[1] + wall_side[1] * c["wall_gap"], stem[2])
            out.append(tube(m, stem, c["bracket_r"], 6))
            out.append(tube(stem, wall, c["bracket_r"], 6))
    return [m for m in out if m[0]]


# 26 Oct 2026: the guard around a floor opening (a stair void). ``wall_reach``: an edge this near a wall face that
# runs along it is carried by the wall; ``arrival_reach``: an edge this near the stair's top line, along it, is where
# the stair comes up (open); ``inset``: the guard stands this far back on the floor (its base plates and channel clear
# of the stair's own balustrade, which rises at the void's edge); ``parallel_cos``: "along" means within ~25 degrees.
GUARD = {"height": 1.00, "wall_reach": 0.15, "arrival_reach": 0.30, "inset": 0.08, "parallel_cos": 0.9,
         "min_run": 0.10, "step": 0.05, "wall_body": 0.005}


def _unit(p, q):
    length = math.hypot(q[0] - p[0], q[1] - p[1])
    return ((q[0] - p[0]) / length, (q[1] - p[1]) / length) if length > 1e-12 else (0.0, 0.0)


def _blocked_at(x, u, walls, arrivals, g) -> bool:
    """True when the point ``x`` of a void edge running along ``u`` needs no guard: inside a wall body, near the face
    of a wall that runs along the edge, or on an arrival edge along it."""
    for w in walls:
        d = G.point_segment_distance(x, w["start"], w["end"])
        half = float(w.get("thickness") or 0.0) / 2.0
        if d <= half + g["wall_body"]:
            return True
        wu = _unit(w["start"], w["end"])
        if abs(u[0] * wu[0] + u[1] * wu[1]) >= g["parallel_cos"] and d <= half + g["wall_reach"]:
            return True
    for a, b in arrivals:
        au = _unit(a, b)
        if abs(u[0] * au[0] + u[1] * au[1]) < g["parallel_cos"]:
            continue
        s = (x[0] - a[0]) * au[0] + (x[1] - a[1]) * au[1]
        across = abs((x[0] - a[0]) * au[1] - (x[1] - a[1]) * au[0])
        if -g["step"] <= s <= G.distance(a, b) + g["step"] and across <= g["arrival_reach"]:
            return True
    return False


def void_guard_runs(void_polygon: Sequence[Sequence[float]], walls: Sequence[dict] = (),
                    arrival_edges: Sequence = (), guard: Optional[dict] = None,
                    keep_out: Sequence[Sequence[Sequence[float]]] = ()) -> list[tuple]:
    """The runs of a floor opening that need a guard (pure): ``[(p, q)]`` stretches of the edges of ``void_polygon``
    whose points are free (``_blocked``: not in a wall, not along a wall face within ``wall_reach``, not along an
    ``arrival_edges`` segment ``(a, b)`` within ``arrival_reach``), sampled every ``step`` and refined to 1 mm, at
    least ``min_run`` long, moved ``inset`` outward of the void onto the floor; two runs that meet at a corner of the
    void meet at the corner of their moved lines too.

    30 Oct 2026 (lesson UL192, user on real04 run 20261030-112241-full: "Something wrong with the stairs": the L0 floor
    opening where the basement stair arrives lies under the L0 stair; its glass-channel guard ran across that stair's
    first flight and through its well, the steel cap a bar floating across the flight, the shoe a block at its foot):
    ``keep_out`` (the footprints of the level's own stairs, ``shell.own_stair_footprints``) hold no guard; their own
    balustrades guard their flights and well."""
    g = dict(GUARD, **(guard or {}))
    poly = geom2d.ccw([(float(p[0]), float(p[1])) for p in void_polygon])
    n = len(poly)
    walls = [w for w in walls or () if G.distance(w["start"], w["end"]) > 1e-9]
    arrivals = [((float(a[0]), float(a[1])), (float(b[0]), float(b[1]))) for a, b in arrival_edges or ()
                if G.distance(a, b) > 1e-9]
    outs = [[(float(q[0]), float(q[1])) for q in k] for k in keep_out or () if len(k or ()) >= 3]

    def _blocked(x, u, walls_, arrivals_, g_):                     # the module's rule and the level's own stairs
        return _blocked_at(x, u, walls_, arrivals_, g_) or any(G.point_in_polygon(x, k) for k in outs)
    per_edge = []
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        length = G.distance(p, q)
        runs = []
        if length >= 1e-6:
            u = _unit(p, q)
            k = max(2, int(math.ceil(length / g["step"])))
            free = [not _blocked(G.point_along_segment(p, q, j / k), u, walls, arrivals, g) for j in range(k + 1)]

            def edge_t(t_free, t_blocked):
                for _ in range(12):                                # refine the run's end to about 1 mm
                    mid = (t_free + t_blocked) / 2.0
                    if _blocked(G.point_along_segment(p, q, mid), u, walls, arrivals, g):
                        t_blocked = mid
                    else:
                        t_free = mid
                return t_free

            j = 0
            while j <= k:
                if not free[j]:
                    j += 1
                    continue
                j0 = j
                while j <= k and free[j]:
                    j += 1
                t0 = 0.0 if j0 == 0 else edge_t(j0 / k, (j0 - 1) / k)
                t1 = 1.0 if j - 1 == k else edge_t((j - 1) / k, j / k)
                if (t1 - t0) * length >= g["min_run"]:
                    runs.append([t0, t1])
        per_edge.append(runs)
    out = []
    inset = g["inset"]
    for i in range(n):
        p, q = poly[i], poly[(i + 1) % n]
        u = _unit(p, q)
        nx, ny = u[1], -u[0]                                       # outward of a counter-clockwise void
        length = G.distance(p, q)
        for t0, t1 in per_edge[i]:
            e0 = e1 = 0.0
            prev = per_edge[i - 1]
            if t0 <= 1e-9 and prev and prev[-1][1] >= 1.0 - 1e-9:   # a corner with the run before
                e0 = _miter(poly[i - 1], p, q, inset)
            nxt = per_edge[(i + 1) % n]
            if t1 >= 1.0 - 1e-9 and nxt and nxt[0][0] <= 1e-9:    # a corner with the run after
                e1 = _miter(p, q, poly[(i + 2) % n], inset)
            s0, s1 = t0 * length - e0, t1 * length + e1
            if s1 - s0 < g["min_run"]:
                continue
            a = (p[0] + u[0] * s0 + nx * inset, p[1] + u[1] * s0 + ny * inset)
            b = (p[0] + u[0] * s1 + nx * inset, p[1] + u[1] * s1 + ny * inset)
            out.append((a, b))
    return out


def _miter(a, b, c, inset: float) -> float:
    """How far a run moved ``inset`` outward of a counter-clockwise polygon reaches past the corner ``b`` of the edges
    ``a``-``b`` and ``b``-``c`` to meet the next one: ``inset * tan(turn / 2)`` (negative at an inner corner)."""
    u, v = _unit(a, b), _unit(b, c)
    turn = math.atan2(u[0] * v[1] - u[1] * v[0], u[0] * v[0] + u[1] * v[1])
    return inset * math.tan(max(-1.4, min(1.4, turn / 2.0)))


def void_guards(void_polygon: Sequence[Sequence[float]], walls: Sequence[dict] = (), arrival_edges: Sequence = (),
                floor_z: float = 0.0, kind: str = DEFAULT_KIND, height: Optional[float] = None,
                guard: Optional[dict] = None, keep_out: Sequence = ()) -> tuple[list, list, list]:
    """``(metal, glass, runs)``: a ``balustrade`` of ``kind``, ``GUARD["height"]`` high, standing on ``floor_z`` along
    each run of ``void_guard_runs`` (pure; 26 Oct 2026; ``keep_out``: the level's own stairs, UL192)."""
    runs = void_guard_runs(void_polygon, walls, arrival_edges, guard, keep_out)
    metal, glass = [], []
    h = float(height if height is not None else dict(GUARD, **(guard or {}))["height"])
    for p, q in runs:
        m, g = balustrade(p, q, floor_z, h, kind)
        metal += m
        glass += g
    return metal, glass, runs
