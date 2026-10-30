"""The towels of the bathroom details as real towels (30 Oct 2026, lesson UL138, user on real04 run
20261029-201533-full: "I am guessing these orange things are towels, they need more detail, a lot more detail": the
rolled towels were faceted 14-sided cylinders, the hanging towels flat slabs over a thin bar). Pure (no ``bpy``):
vertex and face lists the bathroom parts (``bath_parts``) put into their host's one mesh.

Every towel is cloth of a real thickness, a closed mesh (``cloth_loft``): a strip of cloth drawn as its middle line in
a cross-section, thick around it, its ends (the hems) rounded, swept along the towel's width with the side edges
rounded too, so no edge is a plate's:

- ``rolled_towel``: a bath towel folded in thirds and rolled: the end shows the spiral of the roll (``ROLL_TURNS``
  turns of the folded cloth, a groove between them), the outer end of the cloth lies on the roll, the ends of every
  turn are rounded, the roll sits a little flattened on its shelf.
- ``folded_towel`` / ``folded_stack``: a towel folded over at the front (one soft rounded fold) with its two layers and
  their hems at the back, the top layer a little shorter and pillowed; a stack's towels slightly off each other in
  place, turn and height, every other one in the second shade (``towel_shade``).
- ``draped_towel``: a towel hung over a bar, both layers (the front one longer), a soft curve where it leaves the bar
  and a little belly under it, gentle vertical folds growing towards the hem, a slight sag of the hem, rounded hems
  and a flat-woven band near the front hem (``BAND_KEY_SUFFIX``: the same colour in a smooth weave, proud of the pile).

The material keys: the towel's own key (``towel`` on a fixture, ``colour_towel`` on a decor item: the room's towel
colour, B26) is the terry cloth (``finishes`` slug ``fabric_terry``: the ``wenart_weave`` group's loop pile as a bump,
roughness 0.97, ``materials``); ``<key>_alt`` the second shade of a stack or a pair (``towel_shade``), ``<key>_band``
the woven band. Face counts are kept small (``ROLL_FACES_MAX``, ``FOLDED_FACES_MAX``, ``DRAPED_FACES_MAX``, measured
by tests/test_towels_20261030.py).
"""
from __future__ import annotations

import math
from typing import Callable, Optional, Sequence

Part = dict
LESSON = "UL138"
ALT_KEY_SUFFIX = "_alt"              # a stack's or a pair's second shade
BAND_KEY_SUFFIX = "_band"            # the flat-woven band near a hanging towel's hem
TERRY_SLUG = "fabric_terry"          # wenart.style.finishes: the terry cloth (a loop-pile bump, roughness 0.97)
BAND_SLUG = "fabric_cotton"          # ... and the band's smooth flat weave in the same colour

ROLL_TURNS = 2.25                    # turns of the folded towel in a roll (a bath towel folded in thirds)
ROLL_POINTS_PER_TURN = 16
ROLL_CORE_SHARE = 0.16               # the roll's hollow core: this share of its radius
ROLL_FILL = 0.84                     # the cloth's share of the pitch between turns (the rest: the groove you see)
ROLL_SQUASH = 0.94                   # a roll lying on a shelf is a little flattened
EDGE_SEGMENTS = 3                    # points of a rounded hem (a half round)
FOLDS_ACROSS = 3                     # gentle vertical folds across a hanging towel
FOLD_AMPLITUDE_M = 0.010             # ... their depth at the hem (growing from nothing at the bar)
HEM_SAG_M = 0.006                    # the hem's middle this much lower than its corners
BELLY_M = 0.005                      # the soft curve under the bar: the front layer bulges this much
BAND_FROM_HEM_M = 0.045              # the woven band's lower edge over the hem ...
BAND_H_M = 0.035                     # ... its height
BAND_T_M = 0.0014                    # ... and its thickness (proud of the pile)
DRAPE_T_M = 0.007                    # a hanging towel's thickness (a bath towel folded once lengthwise: two layers)
ROLL_FACES_MAX = 700
FOLDED_FACES_MAX = 600
DRAPED_FACES_MAX = 1800


def alt_key(key: str) -> str:
    return key + ALT_KEY_SUFFIX


def band_key(key: str) -> str:
    return key + BAND_KEY_SUFFIX


def towel_shade(colour: Optional[str]) -> str:
    """The second shade of a towel colour (a stack, a pair): ``light <colour>`` when the colour table knows it, else
    the colour itself; white towels (no colour) get a light grey one."""
    if not colour:
        return "light grey"
    try:
        from wenart.style import colours as C

        name = f"light {colour}"
        return name if C.known(name) else str(colour)
    except ImportError:                                            # pragma: no cover - the style package ships with us
        return str(colour)


def _jitter(seed: int, k: int) -> float:
    """A fixed pseudo-random number in [-1, 1] (no ``random``: the same towel every build)."""
    v = math.sin(seed * 12.9898 + k * 78.233) * 43758.5453
    return 2.0 * (v - math.floor(v)) - 1.0


# --------------------------------------------------------------------------
# The cloth strip and its loft
# --------------------------------------------------------------------------

def strip_loop(path: Sequence[Sequence[float]], thickness, edge_segments: int = EDGE_SEGMENTS
               ) -> list[tuple[float, float]]:
    """The closed outline (2D) of a strip of cloth around ``path`` (its middle line, at least 2 points): one side at
    ``+thickness / 2`` along the path's left normal, a half round at the end, the other side back, a half round at the
    start. ``thickness``: one value or one per path point. The outline has ``2 * len(path) + 2 * edge_segments``
    points in that order (``cloth_loft`` relies on it)."""
    n = len(path)
    ts = [float(thickness)] * n if isinstance(thickness, (int, float)) else [float(v) for v in thickness]
    normals, tangents = [], []
    for i in range(n):
        a = path[max(0, i - 1)]
        b = path[min(n - 1, i + 1)]
        tx, ty = float(b[0]) - float(a[0]), float(b[1]) - float(a[1])
        length = math.hypot(tx, ty) or 1.0
        tangents.append((tx / length, ty / length))
        normals.append((-ty / length, tx / length))               # the left normal
    left = [(p[0] + nx * t / 2.0, p[1] + ny * t / 2.0) for p, (nx, ny), t in zip(path, normals, ts)]
    right = [(p[0] - nx * t / 2.0, p[1] - ny * t / 2.0) for p, (nx, ny), t in zip(path, normals, ts)]

    def half_round(p, nrm, tan, t, forward):
        pts = []
        for k in range(1, edge_segments + 1):
            phi = math.pi * k / (edge_segments + 1)
            s = 1.0 if forward else -1.0
            pts.append((p[0] + t / 2.0 * (math.cos(phi) * nrm[0] + s * math.sin(phi) * tan[0]),
                        p[1] + t / 2.0 * (math.cos(phi) * nrm[1] + s * math.sin(phi) * tan[1])))
        return pts
    end = half_round(path[-1], normals[-1], tangents[-1], ts[-1], True)
    start = half_round(path[0], (-normals[0][0], -normals[0][1]), tangents[0], ts[0], False)
    return left + end + right[::-1] + start


def cloth_loft(sections: Sequence[tuple[float, list]], frame: Callable[[float, float, float], tuple],
               n_path: int, key: str, role: str = "towel", edge_segments: int = EDGE_SEGMENTS) -> Part:
    """One closed cloth mesh: ``sections`` = ``[(s, loop)]`` (``strip_loop`` outlines of the same path length
    ``n_path``, at stations ``s`` along the towel's width, in order), ``frame(a, b, s)`` the world point of an outline
    point ``(a, b)`` at station ``s``. The side faces join the stations; the two end caps are the strip's quads (one
    side's point to the other's) and the hems' half rounds. Faces wound outwards (checked on the volume)."""
    m = len(sections[0][1])
    verts = []
    for s, loop in sections:
        if len(loop) != m or m != 2 * n_path + 2 * edge_segments:
            raise ValueError(f"cloth_loft: outlines of {len(loop)} points, {m} expected for a path of {n_path}")
        verts.extend(frame(a, b, s) for a, b in loop)
    faces = []
    for j in range(len(sections) - 1):
        o0, o1 = j * m, (j + 1) * m
        for i in range(m):
            i1 = (i + 1) % m
            faces.append([o0 + i, o0 + i1, o1 + i1, o1 + i])

    def cap(o: int) -> list[list[int]]:
        """The end cap's faces wound against the outline's order (the first station's side faces run with it)."""
        out = []
        left = list(range(n_path))
        right = [2 * n_path + edge_segments - 1 - i for i in range(n_path)]     # the right side, path order
        for i in range(n_path - 1):
            out.append([o + left[i], o + right[i], o + right[i + 1], o + left[i + 1]])
        end = [left[-1]] + [n_path + k for k in range(edge_segments)] + [right[-1]]
        start = [right[0]] + [2 * n_path + edge_segments + k for k in range(edge_segments)] + [left[0]]
        out.append([o + v for v in end][::-1])
        out.append([o + v for v in start][::-1])
        return out
    last = (len(sections) - 1) * m
    faces += cap(0) + [f[::-1] for f in cap(last)]
    part = {"verts": verts, "faces": faces, "key": key, "role": role, "smooth": True}
    if _volume(part) < 0.0:                                         # a left-handed frame or a clockwise outline
        part["faces"] = [f[::-1] for f in faces]
    return part


def _volume(part: Part) -> float:
    v, out = part["verts"], 0.0
    for f in part["faces"]:
        a = v[f[0]]
        for k in range(1, len(f) - 1):
            b, c = v[f[k]], v[f[k + 1]]
            out += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return out


def _rounded_stations(half: float, t: float) -> list[tuple[float, float]]:
    """``(s, thickness factor)`` of a cloth's side edges rounded over its thickness ``t``: the end at 0.45, then 0.85,
    then full; mirrored about the middle (``half`` = half the width)."""
    e1, e2 = min(0.35 * t, half * 0.2), min(t, half * 0.4)
    one = [(-half, 0.45), (-half + e1, 0.85), (-half + e2, 1.0)]
    return one + [(-s, f) for s, f in one[::-1]]


# --------------------------------------------------------------------------
# Rolled towels
# --------------------------------------------------------------------------

def roll_path(r: float, turns: float = ROLL_TURNS, per_turn: int = ROLL_POINTS_PER_TURN
              ) -> tuple[list[tuple[float, float]], float]:
    """``(path, cloth thickness)`` of a roll of radius ``r``: an Archimedean spiral from the core out, its last turn's
    outer face at ``r`` (centre 0, 0)."""
    core = ROLL_CORE_SHARE * r
    pitch = (r - core) / (turns + ROLL_FILL)                       # the last turn's outer face at r
    t = ROLL_FILL * pitch
    n = max(8, int(round(turns * per_turn)) + 1)
    path = []
    for k in range(n):
        theta = 2.0 * math.pi * turns * k / (n - 1)
        rho = core + t / 2.0 + pitch * theta / (2.0 * math.pi)
        path.append((rho * math.cos(theta - math.pi / 2.0), rho * math.sin(theta - math.pi / 2.0)))
    return path, t


def rolled_towel(x: float, y: float, z0: float, r: float, length: float, key: str = "towel",
                 axis: str = "y", seed: int = 0) -> Part:
    """A rolled towel of radius ``r`` and ``length`` lying on ``z0`` with its axis along ``axis`` (``y``: the depth,
    as on a shelf; ``x``: the width), centred on ``(x, y)`` (module docstring)."""
    path, t = roll_path(r)
    turn = 0.35 + 0.15 * _jitter(seed, 1)                           # where the cloth's outer end lies on the roll
    c, s_ = math.cos(turn), math.sin(turn)
    path = [(px * c - py * s_, (px * s_ + py * c)) for px, py in path]
    sections = []
    for s, f in _rounded_stations(length / 2.0, t):
        loop = strip_loop(path, t * f)
        sections.append((s, [(a, b * ROLL_SQUASH) for a, b in loop]))
    zc = z0 - min(b for _s, loop in sections for _a, b in loop)    # the roll rests on z0

    if axis == "x":
        def frame(a, b, s):
            return (x + s, y + a, zc + b)
    else:
        def frame(a, b, s):
            return (x + a, y + s, zc + b)
    return cloth_loft(sections, frame, len(path), key)


# --------------------------------------------------------------------------
# Folded towels and stacks
# --------------------------------------------------------------------------

def folded_path(d: float, h: float, back_short: float = 0.012) -> tuple[list[tuple[float, float]], float]:
    """``(path, layer thickness)`` of a towel folded over at the front (depth ``d`` along ``a``, front at ``-d / 2``;
    height ``h`` from 0): the lower layer from its hem at the back to the front, one soft fold up, the upper layer back
    to its hem ``back_short`` short of the lower one."""
    t = h / 2.0 * 0.96
    rad = (h - t) / 2.0
    yf = -d / 2.0 + rad + t / 2.0
    back = d / 2.0 - t / 2.0
    lower = [(back - (back - yf) * k / 3.0, t / 2.0) for k in range(4)]
    fold = [(yf - rad * math.sin(math.pi * k / 8.0), h / 2.0 - rad * math.cos(math.pi * k / 8.0)) for k in range(1, 8)]
    upper = [(yf + (back - back_short - yf) * k / 3.0, h - t / 2.0) for k in range(4)]
    return lower + fold + upper, t


def folded_towel(cx: float, cy: float, z0: float, w: float, d: float, h: float, key: str = "towel",
                 rotation_deg: float = 0.0, seed: int = 0) -> Part:
    """One folded towel ``w`` wide, ``d`` deep, ``h`` high (its fold to the front, -Y), the upper layer pillowed a few
    millimetres in the middle, turned by ``rotation_deg`` about its centre."""
    path, t = folded_path(d, h, 0.008 + 0.006 * (1.0 + _jitter(seed, 2)))
    half = w / 2.0
    stations = _rounded_stations(half, t) if half > 0.06 else [(-half, 0.6), (half, 0.6)]
    mids = [-half * 0.5, 0.0, half * 0.5]
    stations = sorted(stations + [(s, 1.0) for s in mids], key=lambda p: p[0])
    upper0 = len(path) - 4                                          # the upper layer's four points (fold side first)
    lift = (0.0, 1.0, 1.0, 0.4)                                     # ... pillowed in the middle of the depth
    sections = []
    for s, f in stations:
        pillow = 0.003 * max(0.0, 1.0 - (2.0 * s / w) ** 2)
        pts = [(a, b + (pillow * lift[k - upper0] if k >= upper0 else 0.0)) for k, (a, b) in enumerate(path)]
        sections.append((s, strip_loop(pts, t * f)))
    r = math.radians(rotation_deg)
    c, sn = math.cos(r), math.sin(r)

    def frame(a, b, s):
        lx, ly = s, a                                              # width along x, depth along y
        return (cx + c * lx - sn * ly, cy + sn * lx + c * ly, z0 + b)
    return cloth_loft(sections, frame, len(path), key)


def folded_stack(cx: float, cy: float, z0: float, w: float, d: float, h_each: float, count: int,
                 key: str = "towel", seed: int = 0) -> list[Part]:
    """``count`` folded towels stacked from ``z0`` (each ``h_each`` high), each a little off the one under it in place,
    turn and height, every other one in the second shade (``alt_key``)."""
    parts, z = [], z0
    for k in range(count):
        hk = h_each * (1.0 + 0.06 * _jitter(seed + k, 3))
        dx, dy = 0.004 * _jitter(seed + k, 4), 0.004 * _jitter(seed + k, 5)
        parts.append(folded_towel(cx + dx, cy + dy, z, w, d, hk, key if k % 2 == 0 else alt_key(key),
                                  1.2 * _jitter(seed + k, 6), seed + k))
        z += hk
    return parts


# --------------------------------------------------------------------------
# Hanging towels
# --------------------------------------------------------------------------

def draped_path(bar_y: float, bar_z: float, bar_r: float, drop: float, back_drop: float, t: float = DRAPE_T_M
                ) -> tuple[list[tuple[float, float]], int, int]:
    """``(path, index of the bar's first point, index of its last)`` of a towel hung over a bar (the cross-section:
    ``a`` = y, ``b`` = z): from the front hem (its sagging middle's rounded edge ``drop`` under the bar's centre) up
    the front, over the bar, down the back to its hem (``back_drop``); the front layer leaves the bar in a soft curve
    and bulges a little under it."""
    rad = bar_r + t / 2.0 + 0.0008
    top = bar_z
    yf, yb = bar_y - rad, bar_y + rad
    n_front, n_back, n_arc = 12, 9, 9
    hem = top - drop + t / 2.0 + HEM_SAG_M        # the sagging hem's lowest point (its rounded edge) at top - drop
    front = []
    for k in range(n_front):
        u = k / (n_front - 1)                                       # 0 at the hem, 1 at the bar
        z = hem + (top - hem) * u
        depth = top - z                                             # under the bar
        belly = BELLY_M * math.sin(math.pi * min(1.0, depth / max(0.12, drop * 0.45))) if depth < drop * 0.45 else 0.0
        front.append((yf - belly, z))
    arc = [(bar_y - rad * math.cos(math.pi * k / (n_arc - 1)), top + rad * math.sin(math.pi * k / (n_arc - 1)))
           for k in range(1, n_arc - 1)]
    back_hem = top - back_drop + t / 2.0 + HEM_SAG_M
    back = [(yb, top - (top - back_hem) * k / (n_back - 1)) for k in range(n_back)]
    path = front + arc + back
    return path, n_front - 1, n_front + len(arc)


def draped_towel(cx: float, bar_y: float, bar_z: float, bar_r: float, w: float, drop: float, key: str = "towel",
                 back_share: float = 0.8, t: float = DRAPE_T_M, seed: int = 0) -> list[Part]:
    """A towel ``w`` wide hung over a bar along x (centre ``(cx, bar_y)``, its top at ``bar_z`` - the bar's centre
    height, radius ``bar_r``), its front layer ``drop`` long under the bar, its back one ``back_share`` of that (module
    docstring); the towel and its woven band (``band_key``), two parts of the host's mesh."""
    path, i_bar0, _i_bar1 = draped_path(bar_y, bar_z, bar_r, drop, drop * back_share, t)
    half = w / 2.0
    across = [(-half + w * k / 12.0, 1.0) for k in range(1, 12)]
    stations = sorted(_rounded_stations(half, t)[:3] + across + _rounded_stations(half, t)[3:], key=lambda p: p[0])
    phase = 0.8 * _jitter(seed, 7)
    sections = []
    for s, f in stations:
        u = (s + half) / w
        pts = []
        for k, (a, b) in enumerate(path):
            depth = max(0.0, bar_z - b)
            share = min(1.0, depth / max(1e-6, drop)) ** 1.3
            # the folds only bulge outwards (the front layer to the room, the back one to the wall): never into the
            # bar's plane, where a ladder rail's lower bars pass between the layers
            fold = FOLD_AMPLITUDE_M * share * (0.5 + 0.5 * math.sin(2.0 * math.pi * FOLDS_ACROSS * u + phase))
            sag = HEM_SAG_M * share * (1.0 - (2.0 * u - 1.0) ** 2)
            sign = -1.0 if k <= i_bar0 else 1.0
            pts.append((a + sign * fold if depth > 0 else a, b - sag))
        sections.append((s, strip_loop(pts, t * f)))
    parts = [cloth_loft(sections, lambda a, b, s: (cx + s, a, b), len(path), key)]
    # The woven band on the front layer's face near its hem. The path rises up the front layer (+b), so its left side
    # (the outline's first points) is the face towards the room (-y); the band is a thin strip on it, from
    # BAND_FROM_HEM_M over that station's hem, following the station's folds, embedded 0.3 mm in the pile.
    band_sections = []
    for s, f in stations:
        face = next(loop for st, loop in sections if st == s)[:i_bar0 + 1]
        z_lo = face[0][1] + BAND_FROM_HEM_M
        mid = []
        for k in range(3):
            z = z_lo + BAND_H_M * k / 2.0
            mid.append((_side_at(face, z) - BAND_T_M / 2.0 + 0.0003, z))
        band_sections.append((s, strip_loop(mid, BAND_T_M * f, edge_segments=1)))
    parts.append(cloth_loft(band_sections, lambda a, b, s: (cx + s, a, b), 3, band_key(key), "towel_band",
                            edge_segments=1))
    # the hem's sampled half rounds stop a fraction of a millimetre short of ``drop``: the towel under the bar is
    # stretched by that much, so its lowest point is exactly ``drop`` under the bar's centre (a box's bottom)
    low = min(v[2] for v in parts[0]["verts"])
    if bar_z - low > 1e-9:
        k = drop / (bar_z - low)
        for p in parts:
            p["verts"] = [(x, y, bar_z - (bar_z - z) * k if z < bar_z else z) for x, y, z in p["verts"]]
    return parts


def _side_at(side, z: float) -> float:
    """The ``a`` of a strip side (its points rising in ``b``) at height ``z``."""
    for k in range(1, len(side)):
        if side[k][1] >= z:
            (a0, z0), (a1, z1) = side[k - 1], side[k]
            w = 0.0 if abs(z1 - z0) < 1e-12 else (z - z0) / (z1 - z0)
            return a0 + (a1 - a0) * w
    return side[-1][0]
