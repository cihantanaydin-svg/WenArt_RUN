"""A real-looking weekend holdall (30 Oct 2026; user, on a real04 run 20261030-043021-full render: "I did not
understand what this is if this is a bag it requires a lot more detail in the model"; lesson UL160; the ``bag`` decor
type, R29, ``detail_parts.bag_parts``).

31 Oct 2026 (user on real04 run 20261030-181158-full: "This bag requires a lot more detail and a lot better texture for
example black leather like suite"; the bag read as a grey box with tan straps): a leather travel bag. The body is
leather in the bag's colour (``colour_leather``: the Poly Haven brown_leather scan's grain on the item's colour, the
family's bag tone of ``room_details.FAMILY_TONES``; ``leather_dark``, a black leather on the same scan, where the item
names none) with its trim in the same leather, tan stitching along every seam and strap (``thread``), brass hardware
(``brass``; steel on a pale leather), soft bulging panels. A canvas body with tan leather trim and steel stays for an
item with ``bag_material: canvas``.

What (pure: parts in the item's frame, bottom on z = 0, the front towards -Y, the length along X):

- the body: a soft barrel (``Body``): a rounded-rectangle section (``BAG["e_top"]`` above, a squarer ``BAG["e_bottom"]``
  below), its top sagging and its sides bulging in the middle (``BAG["sag"]``, ``BAG["bulge"]``), rounded into flat end
  panels; the base band below ``BAG["base_band"]`` its own part (the trim);
- leather piping round both end panels and along both edges of the base band, each seam stitched beside it;
- the main zip along the top (a dark tape with a metal chain, stitched along both edges), its slider with a metal pull
  plate and a leather tassel, a stitched leather garage tab at each end of the zip;
- two rolled leather handles, each riveted to the body by two stitched leather tabs on its side and arched over the
  top, a leather keeper round each handle at its feet, held together by a leather handle wrap where they meet;
- the detachable shoulder strap: a leather tab and a metal D-ring on each end panel, a metal clip and a buckle on each
  end of the strap, a padded shoulder pad in its middle, the strap stitched along both edges, draped down the ends and
  lying on the floor in front of the bag;
- a front pocket with its own piped zip and pull;
- four domed metal feet.

Sizes are those of a real 50-55 cm holdall (designer values, assumed: body ``BAG["length_m"]`` etc.), clamped to the
item's box; the caller (``detail_parts.bag_parts``) keeps everything inside the box (``contain``). Soft parts (the body,
the handles, the piping) are ``"smooth"``; flat leather straps and tabs are bevelled; stitches, keepers and buckles are
not.
"""
from __future__ import annotations

import math
from typing import Optional, Sequence

import numpy as np

Part = dict
Vec = tuple[float, float, float]

LEATHER = "leather"              # tan leather: the canvas bag's trim (``leather_tan``)
LEATHER_DARK = "leather_dark"    # black leather: the leather bag's body and trim where the item names no colour
LEATHER_COLOURED = "colour_leather"   # the leather bag's body and trim in the item's colour (the leather scan)
CANVAS = "colour_fabric"         # the canvas bag's body in the item's colour
METAL = "steel"                  # rivets, D-rings, clips, feet, the zip chain and slider on a canvas or pale bag
BRASS = "brass"                  # ... on a leather bag
THREAD = "thread"                # the stitching (``thread_waxed``)
TAPE = "dark"                    # the zip tape
MATERIALS = ("leather", "canvas")
LIGHT_LUMINANCE = 0.55           # a leather paler than this (relative luminance) takes brass hardware, else steel
BAG = {"length_m": (0.36, 0.56), "depth_m": (0.18, 0.28), "height_m": (0.17, 0.27),
       "e_top": 0.72, "e_bottom": 0.30, "sag": 0.13, "bulge": 0.09, "end_r": 0.035, "ring": 40, "stations": 13,
       "lift_m": 0.006, "base_band": 0.25, "piping_r": 0.0035, "handle_r": 0.0065, "handle_rise": 0.25,
       "tab_w": 0.034, "tab_t": 0.003, "strap_w": 0.032, "strap_t": 0.003,
       # 31 Oct 2026: the stitching (a dash every 8 mm, 4.5 mm long, proud of its leather), the keepers, the pad
       "stitch_pitch": 0.008, "stitch_len": 0.0045, "stitch_w": 0.0012, "stitch_h": 0.0007, "stitch_in": 0.006,
       "keeper_len": 0.014, "pad_len": 0.20, "pad_w": 0.052, "pad_t": 0.009, "foot_r": 0.008}


def bag_look(item: Optional[dict]) -> dict:
    """The keys of a bag's parts (pure): ``{"material", "body", "trim", "metal", "thread", "tape", "colour", "why"}``.
    A leather bag (the default; ``bag_material``) has its body and trim in ``colour_leather`` (the item's colour) or
    ``leather_dark`` (black, no colour named), brass hardware (steel on a leather paler than ``LIGHT_LUMINANCE``;
    ``hardware`` may name ``brass`` or ``steel``); a canvas bag its body in the item's colour with tan leather trim and
    steel."""
    it = item or {}
    material = it.get("bag_material") if it.get("bag_material") in MATERIALS else "leather"
    colour = it.get("colour")
    lum = None
    if colour:
        try:
            from wenart.style import colours as COL
            lum = float(COL.luminance(str(colour)))
        except (KeyError, ValueError, ImportError):
            lum = None
    if material == "canvas":
        body, trim, metal = CANVAS, LEATHER, METAL
    else:
        body = LEATHER_COLOURED if lum is not None else LEATHER_DARK
        trim = body
        # brass on a leather bag (warm on black and on the browns); steel on a pale leather (a grey, a white)
        metal = METAL if lum is not None and lum >= LIGHT_LUMINANCE else BRASS
    if it.get("hardware") in ("brass", "steel"):
        metal = BRASS if it["hardware"] == "brass" else METAL
    why = (f"a {material} holdall in {colour or 'black'}" + (" leather" if material == "leather" else "")
           + f", {'brass' if metal == BRASS else 'steel'} hardware, tan stitching")
    return {"material": material, "body": body, "trim": trim, "metal": metal, "thread": THREAD, "tape": TAPE,
            "colour": colour, "why": why}


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
            # the soft panels: the sides bulge most at mid height, the top sags between the handles
            y *= 1.0 + self.bulge * f * abs(math.cos(theta)) * (0.6 + 0.4 * (1.0 - abs(math.sin(theta))))
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

    def band_theta(self) -> tuple[float, float]:
        """The angles of the base band's top edge at the front and at the back."""
        a = math.asin(-BAG["base_band"])
        return math.pi - a, 2.0 * math.pi + a

    def parts(self, body_key: str = CANVAS, base_key: str = LEATHER) -> list[Part]:
        """The body and its base band (one closed surface, two parts)."""
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
        whole = {"verts": verts, "faces": canvas + base, "key": body_key, "role": "body"}
        flip = volume(whole) < 0.0
        if flip:
            canvas = [list(reversed(f)) for f in canvas]
            base = [list(reversed(f)) for f in base]
        return [_compact(verts, canvas, body_key, "body", True), _compact(verts, base, base_key, "base", True)]


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


def _edges_of(path: Sequence[Vec], faces_to: Sequence[Vec], width: float, lift: float,
              inset: float = 0.0035) -> tuple[list, list, list]:
    """The two edge lines of a strap's broad face (``ribbon``'s frame), ``inset`` in from its edges and ``lift``
    over its centre line: ``(left, right, normals)`` for its two rows of stitches."""
    ts = _tangents(path, False)
    left, right, nrm = [], [], []
    for p, t, m in zip(path, ts, faces_to):
        s = _unit(_cross(t, m))
        mm = _unit(_cross(s, t))
        left.append(_add(_add(p, s, -(width / 2.0 - inset)), mm, lift))
        right.append(_add(_add(p, s, width / 2.0 - inset), mm, lift))
        nrm.append(mm)
    return left, right, nrm


def stitches(path: Sequence[Vec], normals: Sequence[Vec], key: str = THREAD, closed: bool = False,
             pitch: Optional[float] = None, length: Optional[float] = None) -> Optional[Part]:
    """31 Oct 2026: a row of stitches along a seam (pure numpy): ``path`` on the leather's surface (already lifted
    over it), ``normals`` the surface's (the stitches lie flat on it); a dash ``BAG["stitch_len"]`` long every
    ``BAG["stitch_pitch"]``, ``BAG["stitch_w"]`` wide and ``BAG["stitch_h"]`` proud; one part for the row, None when
    the path is shorter than one stitch."""
    pitch = float(pitch or BAG["stitch_pitch"])
    length = float(length or BAG["stitch_len"])
    P = np.asarray(path, dtype=np.float64).reshape(-1, 3)
    N = np.asarray(normals, dtype=np.float64).reshape(-1, 3)
    if closed:
        P = np.concatenate([P, P[:1]], axis=0)
        N = np.concatenate([N, N[:1]], axis=0)
    if len(P) < 2:
        return None
    seg = np.linalg.norm(np.diff(P, axis=0), axis=1)
    total = float(seg.sum())
    n = int(total / pitch)
    if n < 1:
        return None
    pos = np.concatenate([[0.0], np.cumsum(seg)])
    s = pitch * (np.arange(n) + 0.5)
    j = np.clip(np.searchsorted(pos, s, side="right") - 1, 0, len(seg) - 1)
    f = ((s - pos[j]) / np.maximum(seg[j], 1e-12))[:, None]
    c = P[j] * (1.0 - f) + P[j + 1] * f
    t = P[j + 1] - P[j]
    t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-12)
    nn = N[j] * (1.0 - f) + N[j + 1] * f
    nn -= t * np.sum(nn * t, axis=1, keepdims=True)
    nn /= np.maximum(np.linalg.norm(nn, axis=1, keepdims=True), 1e-12)
    b = np.cross(nn, t)                                          # (t, b, nn) right-handed: the box below is outward
    hl, hw, h = length / 2.0, BAG["stitch_w"] / 2.0, BAG["stitch_h"]
    corners = []
    for zz in (0.0, h):
        for sl, sw in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            corners.append(c + t * (sl * hl) + b * (sw * hw) + nn * zz)
    V = np.stack(corners, axis=1).reshape(-1, 3)                 # (n * 8, 3)
    box = np.array([[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]])
    F = (np.arange(n)[:, None, None] * 8 + box[None]).reshape(-1, 4)
    return {"verts": [tuple(p) for p in V.tolist()], "faces": F.tolist(), "key": key, "role": "stitch",
            "stitches": int(n)}


def _rivet(p: Vec, n: Vec, key: str = METAL, r: float = 0.0035, h: float = 0.0022) -> Part:
    from wenart.blender.detail_parts import _rod

    return _outward(_rod(p, _add(p, n, h), r, key, "button", n=8))


def _box(cx: float, cy: float, z0: float, w: float, d: float, h: float, key: str, role: str) -> Part:
    from wenart.blender.parametric import _box as pbox

    return pbox(cx, cy, z0, w, d, h, key, role)


def _frame(centre: Vec, along: Vec, across: Vec, w: float, h: float, r: float, key: str, role: str) -> Part:
    """A rectangular metal frame (a buckle): a closed tube round a ``w`` x ``h`` rectangle in the plane of ``along`` /
    ``across`` about ``centre`` (rounded corners)."""
    a, c = _unit(along), _unit(across)
    pts = []
    for k in range(16):
        ang = 2.0 * math.pi * (k + 0.5) / 16
        ca, sa = math.cos(ang), math.sin(ang)
        x = (w / 2.0) * _sgnpow(ca, 0.35)
        y = (h / 2.0) * _sgnpow(sa, 0.35)
        pts.append(_add(_add(centre, a, x), c, y))
    return tube(pts, r, key, role, n=6, closed=True)


# --------------------------------------------------------------------------
# the bag
# --------------------------------------------------------------------------

def holdall_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """The parts of a weekend holdall for an item box ``w x d x h`` (not yet contained: ``detail_parts.bag_parts``)."""
    look = bag_look(item)
    lo, hi = BAG["length_m"]
    length = max(lo, min(hi, w * 0.82))
    lo, hi = BAG["depth_m"]
    depth = max(lo, min(hi, d * 0.70))
    lo, hi = BAG["height_m"]
    height = max(lo, min(hi, h * 0.74))
    body = Body(length, depth, height, yc=max(0.0, d / 2.0 - depth / 2.0 * (1.0 + BAG["bulge"]) - 0.003))
    parts = body.parts(look["body"], look["trim"])
    parts += _piping(body, look) + _zip(body, look) + _handles(body, height, look) + _pocket(body, look)
    parts += _strap(body, d, look) + _feet(body, look)
    return [p for p in parts if p is not None]


def _piping(body: Body, look: dict) -> list[Part]:
    """Piping round both end panels and along both edges of the base band, a row of stitches beside each."""
    out = []
    pr = BAG["piping_r"]
    xp = body.A + body.R * math.sin(math.radians(50.0))
    xs_ = body.A + body.R * math.sin(math.radians(20.0))            # the stitches on the body side of the piping
    for sx in (-1.0, 1.0):
        loop = [body.point(sx * xp, 2.0 * math.pi * j / 48) for j in range(48)]
        out.append(tube(loop, pr, look["trim"], "piping", n=6, closed=True))
        thetas = [2.0 * math.pi * j / 64 for j in range(64)]
        row = [body.on(sx * xs_, t, 0.0004) for t in thetas]
        out.append(stitches(row, [body.normal(sx * xs_, t) for t in thetas], look["thread"], closed=True))
    span = body.A * 0.98
    xs = [-span + 2.0 * span * k / 24 for k in range(25)]
    for t in body.band_theta():                                       # the base band's top edge, front and back
        out.append(tube([body.point(x, t) for x in xs], pr * 0.85, look["trim"], "piping", n=6))
        above = t - 0.10 if math.cos(t) < 0 else t + 0.10            # on the body, over the band's edge
        out.append(stitches([body.on(x, above, 0.0004) for x in xs], [body.normal(x, above) for x in xs],
                            look["thread"]))
    return out


def _top(body: Body, x: float, off: float) -> tuple[Vec, Vec]:
    return body.on(x, math.pi / 2.0, off), body.normal(x, math.pi / 2.0)


def _zip(body: Body, look: dict) -> list[Part]:
    span = body.A * 0.9
    xs = [-span + 2.0 * span * k / 18 for k in range(19)]
    tape = [_top(body, x, 0.0012) for x in xs]
    chain = [_top(body, x, 0.0030) for x in xs]
    out = [ribbon([p for p, _ in tape], [n for _, n in tape], 0.016, 0.0024, look["tape"], "zip"),
           ribbon([p for p, _ in chain], [n for _, n in chain], 0.0045, 0.0018, look["metal"], "zip")]
    for dt in (-0.075, 0.075):                                       # stitched along both edges of the tape
        row = [body.on(x, math.pi / 2.0 + dt, 0.0006) for x in xs]
        out.append(stitches(row, [body.normal(x, math.pi / 2.0 + dt) for x in xs], look["thread"]))
    for sx in (-1.0, 1.0):                                         # a leather garage tab over each end of the zip
        gx = [sx * (span - 0.012 + 0.05 * k / 6) for k in range(7)]
        g = [_top(body, x, 0.0035) for x in gx]
        out.append(ribbon([p for p, _ in g], [n for _, n in g], 0.034, 0.004, look["trim"], "tab"))
        left, right, nrm = _edges_of([p for p, _ in g], [n for _, n in g], 0.034, 0.0022)
        out.append(stitches(left, nrm, look["thread"]))
        out.append(stitches(right, nrm, look["thread"]))
    # the slider, its metal pull plate lying down the front and a leather tassel on it
    xs_ = span * 0.45
    p, n = _top(body, xs_, 0.004)
    out.append(_box(p[0], p[1], p[2] - 0.002, 0.022, 0.014, 0.007, look["metal"], "button"))
    plate = [body.on(xs_, math.pi / 2.0 + 0.06 + 0.035 * k, 0.0045) for k in range(4)]
    pn = [body.normal(xs_, math.pi / 2.0 + 0.06 + 0.035 * k) for k in range(4)]
    out.append(ribbon(plate, pn, 0.008, 0.0022, look["metal"], "pull"))
    tassel = [body.on(xs_, math.pi / 2.0 + 0.16 + 0.09 * k, 0.0035) for k in range(5)]
    tn = [body.normal(xs_, math.pi / 2.0 + 0.16 + 0.09 * k) for k in range(5)]
    out.append(ribbon(tassel, tn, 0.013, 0.004, look["trim"], "tab"))
    out.append(_rivet(body.on(xs_, math.pi / 2.0 + 0.17, 0.0055), tn[0], look["metal"], r=0.0022, h=0.0015))
    return out


def _handles(body: Body, height: float, look: dict) -> list[Part]:
    """Two rolled leather handles, each on two riveted, stitched tabs, a keeper round each at its feet, meeting over
    the zip in a leather wrap."""
    out = []
    xh = min(body.A * 0.55, 0.11)
    r = BAG["handle_r"]
    z_peak = body.zc + body.c + height * BAG["handle_rise"]
    th_lo, th_hi = 0.30, 1.00                                       # the tab: from low on the side to the shoulder
    for side in (-1.0, 1.0):                                       # -1: the front handle, +1: the back one
        def th(a: float) -> float:
            return math.pi - a if side < 0 else a
        for sx in (-1.0, 1.0):
            ts = [th_lo + (th_hi - th_lo) * k / 8 for k in range(9)]
            path = [body.on(sx * xh, th(t), BAG["tab_t"] / 2.0 + 0.0008) for t in ts]
            nrm = [body.normal(sx * xh, th(t)) for t in ts]
            out.append(ribbon(path, nrm, BAG["tab_w"], BAG["tab_t"], look["trim"], "tab"))
            left, right, sn = _edges_of(path, nrm, BAG["tab_w"], BAG["tab_t"] / 2.0 + 0.0003)
            out.append(stitches(left, sn, look["thread"]))
            out.append(stitches(right, sn, look["thread"]))
            for t in (th_lo + 0.12, th_lo + 0.42):                 # two rivets
                out.append(_rivet(body.on(sx * xh, th(t), BAG["tab_t"] + 0.0006), body.normal(sx * xh, th(t)),
                                  look["metal"]))
        # the rolled handle: out of one tab's top, arched over the top, into the other tab
        foot = body.on(-xh, th(th_hi - 0.06), BAG["tab_t"] + r * 0.6)
        y_pk = body.yc + side * (r + 0.0008)
        path = [body.on(-xh, th(th_hi - 0.30), BAG["tab_t"] + r * 0.6), foot]
        for k in range(1, 20):
            a = math.pi * (1.0 - k / 20.0)
            s = math.sin(a)
            path.append((xh * math.cos(a), foot[1] + (y_pk - foot[1]) * s, foot[2] + (z_peak - foot[2]) * s))
        path.append((xh, foot[1], foot[2]))
        path.append(body.on(xh, th(th_hi - 0.30), BAG["tab_t"] + r * 0.6))
        out.append(tube(path, r, look["trim"], "handle", n=10))
        for k in (2, len(path) - 3):                                # a keeper round the handle at each foot
            a, b = path[k], path[k + (1 if k < len(path) // 2 else -1)]
            t = _unit(_sub(b, a))
            seg = [_add(a, t, BAG["keeper_len"] * (q / 3.0 - 0.5)) for q in range(4)]
            out.append(tube(seg, r + 0.0018, look["trim"], "keeper", n=10))
    from wenart.blender.parametric import _superellipsoid

    wrap_h, wrap_d = 4.6 * r, 2.0 * (2.0 * r + 0.0008) + 0.006
    out.append(_superellipsoid(0.0, body.yc, z_peak - wrap_h / 2.0, min(0.10, xh * 0.8), wrap_d, wrap_h, 0.35, 0.35,
                               look["trim"], "wrap", n_eta=6, n_om=16))
    ww, dd = min(0.10, xh * 0.8) / 2.0, wrap_d / 2.0 + 0.0004
    for dz in (0.25, 0.75):                                          # two rows of stitches across the wrap's front
        row = [(ww * 0.8 * (2.0 * k / 11 - 1.0), body.yc - dd, z_peak - wrap_h / 2.0 + wrap_h * dz)
               for k in range(12)]
        out.append(stitches(row, [(0.0, -1.0, 0.0)] * len(row), look["thread"]))
    return out


def _pocket(body: Body, look: dict) -> list[Part]:
    """A front pocket: a soft panel with its own piped zip, its pull, its edge stitched."""
    from wenart.blender.parametric import _superellipsoid

    pw, ph, pd = body.A * 1.05, body.c * 0.95, 0.024
    zc = body.zc - body.c * 0.18
    y_front = body.point(0.0, math.pi)[1]
    out = [_superellipsoid(0.0, y_front + pd * 0.08, zc - ph / 2.0, pw, pd, ph, 0.3, 0.25, look["body"], "pocket",
                           n_eta=8, n_om=24)]
    yz = y_front + pd * 0.08 - pd / 2.0
    zt = zc + ph / 2.0 - 0.016
    out.append(_box(0.0, yz - 0.0010, zt - 0.005, pw * 0.82, 0.002, 0.010, look["tape"], "zip"))
    out.append(_box(0.0, yz - 0.0022, zt - 0.0012, pw * 0.82, 0.0016, 0.0024, look["metal"], "zip"))
    out.append(_box(pw * 0.25, yz - 0.004, zt - 0.006, 0.014, 0.006, 0.012, look["metal"], "button"))
    out.append(_box(pw * 0.25, yz - 0.0045, zt - 0.026, 0.007, 0.002, 0.020, look["metal"], "pull"))
    out.append(_box(pw * 0.25, yz - 0.004, zt - 0.058, 0.011, 0.004, 0.034, look["trim"], "tab"))
    for dz in (0.009, -0.009):                                       # stitched above and below the zip
        row = [(-pw * 0.42 + pw * 0.84 * k / 30, yz - 0.0013, zt + dz) for k in range(31)]
        out.append(stitches(row, [(0.0, -1.0, 0.0)] * 31, look["thread"]))
    return out


def _strap(body: Body, d: float, look: dict) -> list[Part]:
    """The shoulder strap: a tab and a D-ring on each end panel, clips and buckles, the strap draped down the ends and
    lying on the floor in front of the bag, a shoulder pad in its middle, stitched along both edges."""
    out = []
    x_end = body.A + body.R
    z_ring = body.zc + body.c * 0.35
    w, t = BAG["strap_w"], BAG["strap_t"]
    y_floor = body.point(0.0, math.pi)[1] - 0.028
    ends = []
    for sx in (-1.0, 1.0):
        # the tab on the end panel and its D-ring standing out of it
        tab = [(sx * (x_end + 0.0018), body.yc, z_ring + 0.03 - 0.012 * k) for k in range(6)]
        out.append(ribbon(tab, [(sx, 0.0, 0.0)] * len(tab), 0.03, 0.0036, look["trim"], "tab"))
        left, right, sn = _edges_of(tab, [(sx, 0.0, 0.0)] * len(tab), 0.03, 0.0021)
        out += [stitches(left, sn, look["thread"]), stitches(right, sn, look["thread"])]
        out.append(_rivet((sx * (x_end + 0.0036), body.yc, z_ring + 0.015), (sx, 0.0, 0.0), look["metal"]))
        rr = 0.013
        ring = [(sx * (x_end + 0.003 + rr * math.sin(math.pi * k / 10)), body.yc,
                 z_ring - 0.03 - rr * (1.0 - math.cos(math.pi * k / 10))) for k in range(11)]
        ring.append((sx * (x_end + 0.003), body.yc, z_ring - 0.03 - 2.0 * rr))
        out.append(tube(ring, 0.0025, look["metal"], "ring", n=6, closed=True))
        clip_top = (sx * (x_end + 0.003 + rr), body.yc - 0.004, z_ring - 0.03 - rr)
        out.append(_box(clip_top[0] + sx * 0.006, clip_top[1], clip_top[2] - 0.05, 0.012, 0.016, 0.045,
                        look["metal"], "clip"))
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
    n_floor = 24
    x0, x1 = pl[0], pr[0]
    for k in range(1, n_floor):
        f = k / n_floor
        x = x0 + (x1 - x0) * (1.0 - math.cos(math.pi * f)) / 2.0
        y_land = lands[0] + (lands[1] - lands[0]) * f
        y = y_land + (y_floor - y_land) * math.sin(math.pi * f) ** 0.4 + 0.006 * math.sin(3.0 * math.pi * f)
        path.append((x, y, z_floor))
        facing.append((0.0, 0.0, 1.0))
    drop(pr, sxr, lands[1], range(4, -1, -1))
    out.append(ribbon(path, facing, w, t, look["trim"], "strap"))
    left, right, sn = _edges_of(path, facing, w, t / 2.0 + 0.0003, inset=0.004)
    out += [stitches(left, sn, look["thread"]), stitches(right, sn, look["thread"])]
    # a buckle on each end, just under the clip (the strap's length adjuster)
    for idx in (2, len(path) - 3):
        p = path[idx]
        a = _unit(_sub(path[idx + 1], path[idx - 1]))
        across = _unit(_cross(a, facing[idx]))
        out.append(_frame(p, across, facing[idx], w + 0.006, t + 0.006, 0.0016, look["metal"], "buckle"))
    # the shoulder pad: a padded leather sleeve over the middle of the strap lying on the floor
    mid = len(path) // 2
    seg = path[mid - 3: mid + 4]
    seg = [(q[0], q[1], q[2] + BAG["pad_t"] / 2.0 - t / 2.0) for q in seg]
    out.append(ribbon(seg, [(0.0, 0.0, 1.0)] * len(seg), BAG["pad_w"], BAG["pad_t"], look["trim"], "pad"))
    left, right, sn = _edges_of(seg, [(0.0, 0.0, 1.0)] * len(seg), BAG["pad_w"], BAG["pad_t"] / 2.0 + 0.0003,
                                inset=0.005)
    out += [stitches(left, sn, look["thread"]), stitches(right, sn, look["thread"])]
    return out


def _feet(body: Body, look: dict) -> list[Part]:
    """Four domed metal feet under the base, the body resting on them."""
    from wenart.blender.parametric import _superellipsoid

    lift = BAG["lift_m"]
    fr = BAG["foot_r"]
    out = []
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            out.append(_superellipsoid(sx * (body.A - 0.02), body.yc + sy * (body.b - 0.04), 0.0, 2.0 * fr, 2.0 * fr,
                                       lift + 0.004, 0.55, 1.0, look["metal"], "foot", n_eta=6, n_om=14))
    return out
