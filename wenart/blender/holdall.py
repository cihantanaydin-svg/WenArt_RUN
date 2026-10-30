"""A real-looking weekend holdall (30 Oct 2026; user, on a real04 run 20261030-043021-full render: "I did not
understand what this is if this is a bag it requires a lot more detail in the model"; lesson UL160; the ``bag`` decor
type, R29, ``detail_parts.bag_parts``).

What (pure: parts in the item's frame, bottom on z = 0, the front towards -Y, the length along X):

- the body: a soft barrel (``_barrel``): a rounded-rectangle section (``BAG["e_top"]`` above, a squarer
  ``BAG["e_bottom"]`` below), its top sagging and its sides bulging a little in the middle (``BAG["sag"]``,
  ``BAG["bulge"]``), rounded into flat end panels; the canvas in the item's colour (``colour_fabric``) over a leather
  base band (``LEATHER``);
- leather piping round both end panels and a front pocket with its own zip;
- the main zip along the top (a dark tape with a steel chain), its slider and a leather pull, a leather garage tab at
  each end of the zip;
- two rolled leather handles, each riveted to the body by two stitched leather tabs on its side and arched over the
  top, held together by a leather handle wrap where they meet;
- the detachable shoulder strap: a leather tab and a steel D-ring on each end panel, a steel clip on each end of the
  strap, the strap draped down the ends and lying on the floor in front of the bag;
- four steel base studs.

Sizes are those of a real 50-55 cm holdall (designer values, assumed: body ``BAG["length_m"]`` etc.), clamped to the
item's box; the caller (``detail_parts.bag_parts``) keeps everything inside the box (``contain``). Soft parts (the body,
the handles, the piping) are ``"smooth"``; flat leather straps and tabs are bevelled.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

Part = dict
Vec = tuple[float, float, float]

LEATHER = "leather"              # tan leather: handles, tabs, piping, base band, pulls (``leather_tan``)
CANVAS = "colour_fabric"         # the body in the item's colour (the family's bag tone, ``room_details.FAMILY_TONES``)
METAL = "steel"                  # rivets, D-rings, clips, studs, the zip chain and slider
TAPE = "dark"                    # the zip tape
BAG = {"length_m": (0.36, 0.56), "depth_m": (0.18, 0.28), "height_m": (0.17, 0.27),
       "e_top": 0.55, "e_bottom": 0.32, "sag": 0.10, "bulge": 0.05, "end_r": 0.035, "ring": 32, "stations": 9,
       "lift_m": 0.004, "base_band": 0.25, "piping_r": 0.0035, "handle_r": 0.0065, "handle_rise": 0.25,
       "tab_w": 0.034, "tab_t": 0.003, "strap_w": 0.032, "strap_t": 0.003}


# --------------------------------------------------------------------------
# small vector helpers
# --------------------------------------------------------------------------

def _sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _add(a: Vec, b: Vec, k: float = 1.0) -> Vec:
    return (a[0] + b[0] * k, a[1] + b[1] * k, a[2] + b[2] * k)


def _dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec, b: Vec) -> Vec:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit(a: Vec) -> Vec:
    m = math.sqrt(_dot(a, a)) or 1e-12
    return (a[0] / m, a[1] / m, a[2] / m)


def _sgnpow(v: float, e: float) -> float:
    return math.copysign(abs(v) ** e, v)


def volume(part: Part) -> float:
    """Signed volume of a closed part (positive when wound outwards)."""
    v, s = part["verts"], 0.0
    for f in part["faces"]:
        a = v[f[0]]
        for i in range(1, len(f) - 1):
            s += _dot(a, _cross(v[f[i]], v[f[i + 1]])) / 6.0
    return s


def _outward(part: Part) -> Part:
    if volume(part) < 0.0:
        part["faces"] = [list(reversed(f)) for f in part["faces"]]
    return part


def _compact(verts: list, faces: list, key: str, role: str, smooth: bool = False) -> Part:
    used = sorted({i for f in faces for i in f})
    remap = {old: new for new, old in enumerate(used)}
    part = {"verts": [verts[i] for i in used], "faces": [[remap[i] for i in f] for f in faces], "key": key,
            "role": role}
    if smooth:
        part["smooth"] = True
    return part


# --------------------------------------------------------------------------
# the body
# --------------------------------------------------------------------------

class Body:
    """The barrel's shape: ``point(x, theta)`` on its surface (``theta`` 0 at the back (+Y), pi/2 on top, pi at the
    front), ``normal(x, theta)`` outwards."""

    def __init__(self, length: float, depth: float, height: float, yc: float = 0.0):
        self.L, self.b, self.c = length, depth / 2.0, height / 2.0
        self.R = min(BAG["end_r"], length * 0.08, self.b * 0.4, self.c * 0.4)
        self.A = length / 2.0 - self.R                                    # the straight part's half length
        self.yc, self.zc = yc, BAG["lift_m"] + self.c
        self.sag, self.bulge = BAG["sag"] * self.c, BAG["bulge"]

    def section(self, theta: float) -> tuple[float, float]:
        ct, st = math.cos(theta), math.sin(theta)
        e = BAG["e_top"] if st >= 0.0 else BAG["e_bottom"]
        return self.b * _sgnpow(ct, BAG["e_top"]), self.c * _sgnpow(st, e)

    def point(self, x: float, theta: float) -> Vec:
        y, z = self.section(theta)
        ax = abs(x)
        if ax <= self.A:
            f = 1.0 - (x / self.A) ** 2 if self.A > 0 else 1.0
            y *= 1.0 + self.bulge * f * abs(math.cos(theta))
            z -= self.sag * f * max(0.0, math.sin(theta)) ** 2
            return (x, self.yc + y, self.zc + z)
        phi = min(math.pi / 2.0, math.asin(min(1.0, (ax - self.A) / self.R)))
        s = 1.0 - (self.R / min(self.b, self.c)) * (1.0 - math.cos(phi))
        return (x, self.yc + y * s, self.zc + z * s)

    def normal(self, x: float, theta: float) -> Vec:
        e = 1e-4
        dt = _sub(self.point(x, theta + e), self.point(x, theta - e))
        x0, x1 = x - e, x + e
        if abs(x) + e > self.A + self.R:
            x0, x1 = x - e, x
        dx = _sub(self.point(x1, theta), self.point(x0, theta))
        n = _unit(_cross(dx, dt))
        p = self.point(x, theta)
        out = (0.0, p[1] - self.yc, p[2] - self.zc)
        return n if _dot(n, out) >= 0.0 else (-n[0], -n[1], -n[2])

    def on(self, x: float, theta: float, off: float) -> Vec:
        """The surface point moved ``off`` along its normal."""
        return _add(self.point(x, theta), self.normal(x, theta), off)

    def stations(self) -> list[float]:
        n = BAG["stations"]
        mid = [-self.A + 2.0 * self.A * k / (n - 1) for k in range(n)]
        ends = [self.A + self.R * math.sin(math.radians(a)) for a in (30.0, 60.0, 90.0)]
        return [-x for x in reversed(ends)] + mid + ends

    def parts(self) -> list[Part]:
        """The canvas and its leather base band (one closed surface, two materials)."""
        n = BAG["ring"]
        thetas = [2.0 * math.pi * j / n for j in range(n)]
        xs = self.stations()
        verts: list = []
        for x in xs:
            verts += [self.point(x, t) for t in thetas]
        m = len(xs)
        left, right = len(verts), len(verts) + 1
        verts += [(xs[0], self.yc, self.zc), (xs[-1], self.yc, self.zc)]
        canvas, base = [], []
        band = -BAG["base_band"]
        for i in range(m - 1):
            for j in range(n):
                f = [i * n + j, i * n + (j + 1) % n, (i + 1) * n + (j + 1) % n, (i + 1) * n + j]
                mid = (thetas[j] + math.pi / n)
                (base if math.sin(mid) < band else canvas).append(f)
        for j in range(n):
            f0 = [left, (j + 1) % n, j]
            f1 = [right, (m - 1) * n + j, (m - 1) * n + (j + 1) % n]
            mid = thetas[j] + math.pi / n
            (base if math.sin(mid) < band else canvas).extend([f0, f1])
        whole = {"verts": verts, "faces": canvas + base, "key": CANVAS, "role": "body"}
        flip = volume(whole) < 0.0
        if flip:
            canvas = [list(reversed(f)) for f in canvas]
            base = [list(reversed(f)) for f in base]
        return [_compact(verts, canvas, CANVAS, "body", True), _compact(verts, base, LEATHER, "base", True)]


# --------------------------------------------------------------------------
# sweeps
# --------------------------------------------------------------------------

def _tangents(path: Sequence[Vec], closed: bool) -> list[Vec]:
    n = len(path)
    out = []
    for i in range(n):
        if closed:
            a, b = path[i - 1], path[(i + 1) % n]
        else:
            a, b = path[max(0, i - 1)], path[min(n - 1, i + 1)]
        out.append(_unit(_sub(b, a)))
    return out


def tube(path: Sequence[Vec], r: float, key: str, role: str, n: int = 8, closed: bool = False) -> Part:
    """A round tube of radius ``r`` along ``path`` (a parallel-transport frame: no twist), capped unless
    ``closed``; smooth, wound outwards."""
    ts = _tangents(path, closed)
    ref = (0.0, 0.0, 1.0) if abs(ts[0][2]) < 0.9 else (1.0, 0.0, 0.0)
    nrm = _unit(_cross(_cross(ts[0], ref), ts[0]))
    verts = []
    for i, p in enumerate(path):
        if i:
            nrm = _unit(_sub(nrm, _add((0.0, 0.0, 0.0), ts[i], _dot(nrm, ts[i]))))
        bi = _cross(ts[i], nrm)
        for k in range(n):
            a = 2.0 * math.pi * k / n
            verts.append(_add(_add(p, nrm, r * math.cos(a)), bi, r * math.sin(a)))
    m = len(path)
    faces = []
    for i in range(m if closed else m - 1):
        i1 = (i + 1) % m
        for k in range(n):
            faces.append([i * n + k, i * n + (k + 1) % n, i1 * n + (k + 1) % n, i1 * n + k])
    if not closed:
        faces.append(list(range(n - 1, -1, -1)))
        faces.append([(m - 1) * n + k for k in range(n)])
    return _outward({"verts": verts, "faces": faces, "key": key, "role": role, "smooth": True})


def ribbon(path: Sequence[Vec], faces_to: Sequence[Vec], width: float, thick: float, key: str, role: str) -> Part:
    """A flat strap along ``path``: ``width`` across, ``thick`` along ``faces_to`` (the direction its broad face
    looks, per point: a surface normal, +Z on the floor), capped; wound outwards."""
    ts = _tangents(path, False)
    verts = []
    for p, t, m in zip(path, ts, faces_to):
        s = _unit(_cross(t, m))
        mm = _unit(_cross(s, t))
        for a, b in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            verts.append(_add(_add(p, s, a * width / 2.0), mm, b * thick / 2.0))
    m = len(path)
    faces = []
    for i in range(m - 1):
        for k in range(4):
            faces.append([i * 4 + k, i * 4 + (k + 1) % 4, (i + 1) * 4 + (k + 1) % 4, (i + 1) * 4 + k])
    faces.append([3, 2, 1, 0])
    faces.append([(m - 1) * 4 + k for k in range(4)])
    return _outward({"verts": verts, "faces": faces, "key": key, "role": role})


def _rivet(p: Vec, n: Vec, r: float = 0.0035, h: float = 0.0022) -> Part:
    from wenart.blender.detail_parts import _rod

    return _outward(_rod(p, _add(p, n, h), r, METAL, "button", n=8))


def _box(cx: float, cy: float, z0: float, w: float, d: float, h: float, key: str, role: str) -> Part:
    from wenart.blender.parametric import _box as pbox

    return pbox(cx, cy, z0, w, d, h, key, role)


# --------------------------------------------------------------------------
# the bag
# --------------------------------------------------------------------------

def holdall_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """The parts of a weekend holdall for an item box ``w x d x h`` (not yet contained: ``detail_parts.bag_parts``)."""
    lo, hi = BAG["length_m"]
    length = max(lo, min(hi, w * 0.82))
    lo, hi = BAG["depth_m"]
    depth = max(lo, min(hi, d * 0.74))
    lo, hi = BAG["height_m"]
    height = max(lo, min(hi, h * 0.74))
    body = Body(length, depth, height, yc=max(0.0, d / 2.0 - depth / 2.0 * (1.0 + BAG["bulge"]) - 0.003))
    parts = body.parts()
    parts += _piping(body) + _zip(body) + _handles(body, height) + _pocket(body) + _strap(body, d)
    parts += _studs(body)
    return parts


def _piping(body: Body) -> list[Part]:
    out = []
    xp = body.A + body.R * math.sin(math.radians(50.0))
    for sx in (-1.0, 1.0):
        loop = [body.point(sx * xp, 2.0 * math.pi * j / 40) for j in range(40)]
        out.append(tube(loop, BAG["piping_r"], LEATHER, "piping", n=6, closed=True))
    return out


def _top(body: Body, x: float, off: float) -> tuple[Vec, Vec]:
    return body.on(x, math.pi / 2.0, off), body.normal(x, math.pi / 2.0)


def _zip(body: Body) -> list[Part]:
    span = body.A * 0.9
    xs = [-span + 2.0 * span * k / 12 for k in range(13)]
    tape = [_top(body, x, 0.0012) for x in xs]
    chain = [_top(body, x, 0.0030) for x in xs]
    out = [ribbon([p for p, _ in tape], [n for _, n in tape], 0.016, 0.0024, TAPE, "zip"),
           ribbon([p for p, _ in chain], [n for _, n in chain], 0.0045, 0.0018, METAL, "zip")]
    for sx in (-1.0, 1.0):                                         # a leather garage tab over each end of the zip
        gx = [sx * (span - 0.012 + 0.05 * k / 4) for k in range(5)]
        g = [_top(body, x, 0.0035) for x in gx]
        out.append(ribbon([p for p, _ in g], [n for _, n in g], 0.034, 0.004, LEATHER, "tab"))
    # the slider and its leather pull lying down the front
    xs_ = span * 0.45
    p, n = _top(body, xs_, 0.004)
    out.append(_box(p[0], p[1], p[2] - 0.002, 0.022, 0.014, 0.007, METAL, "button"))
    pull = [body.on(xs_, math.pi / 2.0 + 0.08 + 0.09 * k, 0.003) for k in range(6)]
    pn = [body.normal(xs_, math.pi / 2.0 + 0.08 + 0.09 * k) for k in range(6)]
    out.append(ribbon(pull, pn, 0.013, 0.004, LEATHER, "tab"))
    return out


def _handles(body: Body, height: float) -> list[Part]:
    """Two rolled leather handles, each on two riveted tabs, meeting over the zip in a leather wrap."""
    out = []
    xh = min(body.A * 0.55, 0.11)
    r = BAG["handle_r"]
    z_peak = body.zc + body.c + height * BAG["handle_rise"]
    th_lo, th_hi = 0.30, 1.00                                       # the tab: from low on the side to the shoulder
    for side in (-1.0, 1.0):                                       # -1: the front handle, +1: the back one
        def th(a: float) -> float:
            return math.pi - a if side < 0 else a
        for sx in (-1.0, 1.0):
            ts = [th_lo + (th_hi - th_lo) * k / 6 for k in range(7)]
            path = [body.on(sx * xh, th(t), BAG["tab_t"] / 2.0 + 0.0008) for t in ts]
            nrm = [body.normal(sx * xh, th(t)) for t in ts]
            out.append(ribbon(path, nrm, BAG["tab_w"], BAG["tab_t"], LEATHER, "tab"))
            for t in (th_lo + 0.12, th_lo + 0.42):                 # two rivets
                out.append(_rivet(body.on(sx * xh, th(t), BAG["tab_t"] + 0.0006), body.normal(sx * xh, th(t))))
        # the rolled handle: out of one tab's top, arched over the top, into the other tab
        foot = body.on(-xh, th(th_hi - 0.06), BAG["tab_t"] + r * 0.6)
        y_pk = body.yc + side * (r + 0.0008)
        path = [body.on(-xh, th(th_hi - 0.30), BAG["tab_t"] + r * 0.6), foot]
        for k in range(1, 16):
            a = math.pi * (1.0 - k / 16.0)
            s = math.sin(a)
            path.append((xh * math.cos(a), foot[1] + (y_pk - foot[1]) * s, foot[2] + (z_peak - foot[2]) * s))
        path.append((xh, foot[1], foot[2]))
        path.append(body.on(xh, th(th_hi - 0.30), BAG["tab_t"] + r * 0.6))
        out.append(tube(path, r, LEATHER, "handle", n=8))
    from wenart.blender.parametric import _superellipsoid

    wrap_h, wrap_d = 4.6 * r, 2.0 * (2.0 * r + 0.0008) + 0.006
    out.append(_superellipsoid(0.0, body.yc, z_peak - wrap_h / 2.0, min(0.10, xh * 0.8), wrap_d, wrap_h, 0.35, 0.35,
                               LEATHER, "wrap", n_eta=6, n_om=16))
    return out


def _pocket(body: Body) -> list[Part]:
    """A front pocket: a soft panel with leather piping and its own zip and pull."""
    from wenart.blender.parametric import _superellipsoid

    pw, ph, pd = body.A * 1.05, body.c * 0.95, 0.024
    zc = body.zc - body.c * 0.18
    y_front = body.point(0.0, math.pi)[1]
    out = [_superellipsoid(0.0, y_front + pd * 0.08, zc - ph / 2.0, pw, pd, ph, 0.3, 0.25, CANVAS, "pocket",
                           n_eta=8, n_om=24)]
    yz = y_front + pd * 0.08 - pd / 2.0
    zt = zc + ph / 2.0 - 0.016
    out.append(_box(0.0, yz - 0.0010, zt - 0.005, pw * 0.82, 0.002, 0.010, TAPE, "zip"))
    out.append(_box(0.0, yz - 0.0022, zt - 0.0012, pw * 0.82, 0.0016, 0.0024, METAL, "zip"))
    out.append(_box(pw * 0.25, yz - 0.004, zt - 0.006, 0.014, 0.006, 0.012, METAL, "button"))
    out.append(_box(pw * 0.25, yz - 0.004, zt - 0.040, 0.011, 0.004, 0.034, LEATHER, "tab"))
    return out


def _strap(body: Body, d: float) -> list[Part]:
    """The shoulder strap: a tab and a D-ring on each end panel, clips, the strap draped down the ends and lying on
    the floor in front of the bag."""
    out = []
    x_end = body.A + body.R
    z_ring = body.zc + body.c * 0.35
    w, t = BAG["strap_w"], BAG["strap_t"]
    y_floor = body.point(0.0, math.pi)[1] - 0.028
    ends = []
    for sx in (-1.0, 1.0):
        # the tab on the end panel and its D-ring standing out of it
        tab = [(sx * (x_end + 0.0018), body.yc, z_ring + 0.03 - 0.012 * k) for k in range(6)]
        out.append(ribbon(tab, [(sx, 0.0, 0.0)] * len(tab), 0.03, 0.0036, LEATHER, "tab"))
        out.append(_rivet((sx * (x_end + 0.0036), body.yc, z_ring + 0.015), (sx, 0.0, 0.0)))
        rr = 0.013
        ring = [(sx * (x_end + 0.003 + rr * math.sin(math.pi * k / 10)), body.yc,
                 z_ring - 0.03 - rr * (1.0 - math.cos(math.pi * k / 10))) for k in range(11)]
        ring.append((sx * (x_end + 0.003), body.yc, z_ring - 0.03 - 2.0 * rr))
        out.append(tube(ring, 0.0025, METAL, "ring", n=6, closed=True))
        clip_top = (sx * (x_end + 0.003 + rr), body.yc - 0.004, z_ring - 0.03 - rr)
        out.append(_box(clip_top[0] + sx * 0.006, clip_top[1], clip_top[2] - 0.05, 0.012, 0.016, 0.045, METAL,
                        "clip"))
        ends.append((sx, (clip_top[0] + sx * 0.006, clip_top[1], clip_top[2] - 0.05)))
    # the strap: from the left clip down the end panel to the floor beside it, round the front in a loose U, and up
    # the right end to its clip
    (sxl, pl), (sxr, pr) = ends
    z_floor = t / 2.0 + 0.0005
    lands = (body.yc - body.b * 0.4, body.yc - body.b * 0.2)       # a little uneven: a strap dropped, not laid
    path, facing = [], []

    def drop(p: Vec, sx: float, y_land: float, ks) -> None:
        for k in ks:
            f = k / 4.0
            path.append((p[0] + sx * 0.012 * math.sin(math.pi * f), p[1] + (y_land - p[1]) * f * f,
                         max(z_floor, p[2] * (1.0 - f) ** 1.6)))
            facing.append(_unit((sx * (1.0 - f), 0.0, f)))

    drop(pl, sxl, lands[0], range(5))
    n_floor = 18
    x0, x1 = pl[0], pr[0]
    for k in range(1, n_floor):
        f = k / n_floor
        x = x0 + (x1 - x0) * (1.0 - math.cos(math.pi * f)) / 2.0
        y_land = lands[0] + (lands[1] - lands[0]) * f
        y = y_land + (y_floor - y_land) * math.sin(math.pi * f) ** 0.4 + 0.006 * math.sin(3.0 * math.pi * f)
        path.append((x, y, z_floor))
        facing.append((0.0, 0.0, 1.0))
    drop(pr, sxr, lands[1], range(4, -1, -1))
    out.append(ribbon(path, facing, w, t, LEATHER, "strap"))
    return out


def _studs(body: Body) -> list[Part]:
    from wenart.blender.parametric import _cylinder_z

    lift = BAG["lift_m"]
    out = []
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            out.append(_cylinder_z(sx * (body.A - 0.015), body.yc + sy * (body.b - 0.035), 0.0, 0.0065, 0.0065,
                                   lift + 0.002, METAL, "foot", n=12))
    return out
