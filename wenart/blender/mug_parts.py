"""Coffee mugs as real ceramics (30 Oct 2026; lesson UL213, user on real06 run 20261029-100801-full: "coffee mugs around
the house also is a good decor item book and on top of a book coffee mug"). Pure (no ``bpy``): the parts of
``parametric`` (``verts``, ``faces``, ``key``, ``role``) in the item's own frame (bottom on z = 0, front -Y, centred).

- ``mug``: a turned stoneware mug (``MUG``: 8.2 cm across the rim, 9.6 cm high, assumed from common 300 ml mugs): a foot
  ring with the recessed base inside it and a small groove over it, a body that widens a little towards the rim, a
  rolled lip, the wall's thickness down to the inner floor, and a real loop handle (an oval strap with the hole
  between it and the body, its ends sunk into the wall). A mug that holds coffee (``coffee``) shows the dark liquid a
  centimetre under the rim. The glaze is the item's colour (``accent_ceramic``: ``wenart.furniture.mugs`` takes it
  from the style family's accents), the inside the same glaze.
- ``mug_on_books``: a small stack of books (``book_parts.stack``, as the ``books`` decor) with a mug centred on the top
  book's cover: the mug's foot on the cover's top, its plan inside the cover (``on_cover`` checks both; a mug that
  would reach past the cover is scaled down to it).
- ``mug_pair``: two mugs side by side (one glazed, one white), on a small tray for the families with one
  (``mugs.MUG_TRAY_FAMILIES``): what stands by a coffee machine.

Why: the rooms showed books, vases and candles but no sign of life; a mug on a book by the sofa or by the laptop is the
detail the user asked for.
"""
from __future__ import annotations

import math
from typing import Optional

from wenart.blender import appliance_parts as AP
from wenart.blender import small_parts as SM

Part = dict
LESSON = "UL213"
N = 24                            # the mug's turned segments: it is seen close, on a coffee table or a desk
# the mug (m): rim radius, foot radius, height, wall, inner floor over the bottom, the coffee under the rim, the handle
MUG = {"r": 0.041, "foot_r": 0.035, "h": 0.096, "wall": 0.0045, "floor": 0.010, "coffee_under": 0.011,
       "handle_reach": 0.031, "handle_r": 0.0056, "handle_squash": 0.62}
GLAZE_KEY = "accent_ceramic"      # the item's colour on the ceramic (the glaze)
WHITE_KEY = "ceramic"
COFFEE_KEY = "coffee"                # vocabulary ``coffee_liquid``: a very dark brown glossy liquid
BOOKS_SEED = 5


def _r_at(z: float) -> float:
    """The mug body's outer radius at ``z`` (the taper: the foot's radius to the rim's)."""
    m = MUG
    t = max(0.0, min(1.0, (z - 0.008) / (m["h"] - 0.013)))
    return (m["foot_r"] + 0.001) + (m["r"] - m["foot_r"] - 0.001) * (t ** 0.85)


def body_profile() -> list[tuple[float, float]]:
    """The turned mug's rings ``(r, z)``: the recessed base, the foot ring, the groove, the body up to the rolled lip,
    the inside down to the floor."""
    m = MUG
    R, Rf, H, wall, fl = m["r"], m["foot_r"], m["h"], m["wall"], m["floor"]
    zs = (0.03, 0.055, 0.08)
    out = [(0.0, 0.0035), (Rf - 0.0065, 0.0035), (Rf - 0.0055, 0.0004), (Rf - 0.0012, 0.0), (Rf, 0.003),
           (Rf - 0.0008, 0.0055), (_r_at(0.008), 0.008)]
    out += [(_r_at(z), z) for z in zs]
    out += [(R, H - 0.005), (R + 0.0008, H - 0.0025), (R + 0.0004, H - 0.0006), (R - 0.0012, H),
            (R - wall + 0.0006, H - 0.0008)]
    inside = [(R - wall, H - 0.003)] + [(_r_at(z) - wall, z) for z in reversed(zs)]
    inside += [(_r_at(fl + 0.006) - wall, fl + 0.006), (_r_at(fl) - wall - 0.005, fl + 0.0005), (0.0, fl)]
    return out + inside


def inner_r(z: float) -> float:
    return _r_at(z) - MUG["wall"]


def smooth_path(points, radii, k: int = 3) -> tuple[list, list]:
    """A Catmull-Rom curve through ``points`` (``k`` steps per span; the radii linear along it): a handle's loop reads
    round, not as a polygon."""
    pts = [tuple(float(c) for c in p) for p in points]
    ext = [pts[0]] + pts + [pts[-1]]
    out, rs = [], []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = ext[i], ext[i + 1], ext[i + 2], ext[i + 3]
        for s in range(k):
            t = s / k
            t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * (2 * p1[j] + (p2[j] - p0[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (3 * p1[j] - p0[j] - 3 * p2[j] + p3[j]) * t3) for j in range(3)))
            rs.append(radii[i] + (radii[i + 1] - radii[i]) * t)
    return out + [pts[-1]], rs + [radii[-1]]


def mug(cx: float, cy: float, z0: float, key: str = GLAZE_KEY, coffee: bool = False, handle_deg: float = 0.0,
        s: float = 1.0) -> list[Part]:
    """One mug standing at ``(cx, cy, z0)``, its handle towards ``handle_deg`` (0: +X), scaled ``s``."""
    m = MUG
    body = SM.turned(body_profile(), key, "mug", n=N)
    parts = [body]
    if coffee:
        zc = m["h"] - m["coffee_under"]
        rc = inner_r(zc) - 0.0006
        parts.append(SM.turned([(0.0, zc - 0.002), (rc, zc - 0.002), (rc, zc), (0.0, zc)], COFFEE_KEY, "coffee", n=N))
    # the loop handle in the XZ plane: out of the body under the lip, round, back into the body over the foot
    R, reach = m["r"], m["handle_reach"]
    path = [(_r_at(0.078) - 0.003, 0.0, 0.078), (R + 0.010, 0.0, 0.0815), (R + 0.023, 0.0, 0.0755),
            (R + reach, 0.0, 0.062), (R + reach, 0.0, 0.043), (R + 0.023, 0.0, 0.029), (R + 0.010, 0.0, 0.0235),
            (_r_at(0.024) - 0.003, 0.0, 0.024)]
    hr = m["handle_r"]
    radii = [hr * 1.18, hr * 1.02, hr, hr * 0.96, hr * 0.96, hr, hr * 1.02, hr * 1.18]
    path, radii = smooth_path(path, radii)
    parts.append(SM.tube(path, radii, key, "mug_handle", sides=10, squash=m["handle_squash"]))
    out = []
    for p in parts:
        q = AP.rot_z(p, handle_deg) if abs(handle_deg) > 1e-9 else p
        out.append(dict(q, verts=[(cx + x * s, cy + y * s, z0 + z * s) for x, y, z in q["verts"]]))
    return out


def mug_extent(handle_deg: float = 0.0) -> tuple[float, float, float, float]:
    """``(x0, y0, x1, y1)`` of a mug at the origin with its handle towards ``handle_deg``."""
    vs = [v for p in mug(0.0, 0.0, 0.0, handle_deg=handle_deg) for v in p["verts"]]
    return (min(v[0] for v in vs), min(v[1] for v in vs), max(v[0] for v in vs), max(v[1] for v in vs))


def _rec(item: Optional[dict]) -> dict:
    return dict((item or {}).get("mug") or {})


def mug_parts(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """A single mug in its box (the handle to +X, or the record's ``handle_deg``)."""
    rec = _rec(item)
    a = float(rec.get("handle_deg") or 0.0)
    x0, y0, x1, y1 = mug_extent(a)
    parts = mug(-(x0 + x1) / 2.0, -(y0 + y1) / 2.0, 0.0, coffee=bool(rec.get("coffee")), handle_deg=a)
    return AP.contain(parts, w, d, h)


def mug_on_books(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """A stack of ``books`` (the record's, 2 by default) up to ``books_h`` with a mug centred on the top cover."""
    from wenart.blender import book_parts as BK
    from wenart.blender import detail_parts as DP

    rec = _rec(item)
    n = int(rec.get("books") or 2)
    hb = float(rec.get("books_h") or max(0.03, h - MUG["h"]))
    books = DP.contain(BK.stack(0.0, 0.0, 0.0, w * 0.94, d * 0.94, hb, n=n, seed=int(rec.get("seed") or BOOKS_SEED)),
                       w, d, hb)
    zt = max(v[2] for p in books for v in p["verts"])
    cover = top_cover(books)
    a = float(rec.get("handle_deg") or -35.0)
    x0, y0, x1, y1 = mug_extent(a)
    cw, cd = (cover[2] - cover[0]) - 0.012, (cover[3] - cover[1]) - 0.012      # 6 mm of the cover round the mug
    s = min(1.0, cw / (x1 - x0), cd / (y1 - y0), max(0.3, h - zt) / MUG["h"])
    ccx, ccy = (cover[0] + cover[2]) / 2.0, (cover[1] + cover[3]) / 2.0
    cup = mug(ccx - (x0 + x1) / 2.0 * s, ccy - (y0 + y1) / 2.0 * s, zt, coffee=rec.get("coffee", True) is not False,
              handle_deg=a, s=s)
    return books + cup


def top_cover(parts: list[Part], band: float = 0.004) -> tuple[float, float, float, float]:
    """``(x0, y0, x1, y1)``: the plan box of the stack's top cover (the book parts' vertices within ``band`` of the
    stack's top), shrunk to the box inside a turned cover (its corners cut by the turn)."""
    books = [p for p in parts if not str(p.get("role", "")).startswith("mug") and p.get("role") != "coffee"]
    zt = max(v[2] for p in books for v in p["verts"])
    vs = [v for p in books for v in p["verts"] if v[2] >= zt - band]
    x0, x1 = min(v[0] for v in vs), max(v[0] for v in vs)
    y0, y1 = min(v[1] for v in vs), max(v[1] for v in vs)
    # a cover turned a few degrees: its plan box's inner box (cut by the turn's sine of the other side)
    k = 0.07                                    # sin 4 degrees
    dx, dy = (y1 - y0) * k, (x1 - x0) * k
    return (x0 + dx, y0 + dy, x1 - dx, y1 - dy)


def on_cover(parts: list[Part], tol: float = 0.001) -> Optional[str]:
    """Why the mug of a ``mug_on_books`` part list does not stand on the top book (UL213), None when it does: its
    foot on the cover's top (within ``tol``), its plan inside the cover."""
    books = [p for p in parts if not str(p.get("role", "")).startswith("mug") and p.get("role") != "coffee"]
    cup = [p for p in parts if str(p.get("role", "")).startswith("mug")]
    if not books or not cup:
        return "no books or no mug"
    zt = max(v[2] for p in books for v in p["verts"])
    z0 = min(v[2] for p in cup for v in p["verts"])
    if abs(z0 - zt) > tol:
        return f"the mug's foot {z0 - zt:+.4f} m off the top cover"
    x0, y0, x1, y1 = top_cover(parts)
    vs = [v for p in cup for v in p["verts"]]
    if min(v[0] for v in vs) < x0 - tol or max(v[0] for v in vs) > x1 + tol \
            or min(v[1] for v in vs) < y0 - tol or max(v[1] for v in vs) > y1 + tol:
        return "the mug reaches past the top cover"
    return None


def mug_pair(w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    """Two mugs (the glazed one with coffee, a white one) side by side, on a small tray when the record says so."""
    rec = _rec(item)
    parts: list[Part] = []
    z = 0.0
    if rec.get("tray"):
        parts.append(SM.tray(0.0, 0.0, 0.0, w / 2.0, d / 2.0, key=str(rec.get("tray_key") or "wood"), lip=0.008,
                             t=0.014))
        z = SM.tray_floor(0.0, 0.014)
    rim = 0.024 if rec.get("tray") else 0.0
    gap = 0.014
    if d > w:                                    # a narrow place (by a machine at a run end): one behind the other
        a_f, a_b = -30.0, 20.0
        e_f, e_b = mug_extent(a_f), mug_extent(a_b)
        span = (e_f[3] - e_f[1]) + gap + (e_b[3] - e_b[1])
        s = min(1.0, (d - rim) / span, (w - rim) / max(e_f[2] - e_f[0], e_b[2] - e_b[0]), (h - z) / MUG["h"])
        y = -span * s / 2.0
        parts += mug(-(e_f[0] + e_f[2]) / 2.0 * s, y - e_f[1] * s, z, GLAZE_KEY, coffee=True, handle_deg=a_f, s=s)
        y += (e_f[3] - e_f[1] + gap) * s
        parts += mug(-(e_b[0] + e_b[2]) / 2.0 * s, y - e_b[1] * s, z, WHITE_KEY, coffee=False, handle_deg=a_b, s=s)
        return AP.contain(parts, w, d, h)
    a_r, a_l = -30.0, 210.0                      # the handles out to the front corners
    e_r, e_l = mug_extent(a_r), mug_extent(a_l)
    span = (e_l[2] - e_l[0]) + gap + (e_r[2] - e_r[0])
    s = min(1.0, (w - rim) / span, (d - rim) / max(e_r[3] - e_r[1], e_l[3] - e_l[1]), (h - z) / MUG["h"])
    x = -span * s / 2.0
    parts += mug(x - e_l[0] * s, -(e_l[1] + e_l[3]) / 2.0 * s, z, WHITE_KEY, coffee=False, handle_deg=a_l, s=s)
    x += (e_l[2] - e_l[0] + gap) * s
    parts += mug(x - e_r[0] * s, -(e_r[1] + e_r[3]) / 2.0 * s, z, GLAZE_KEY, coffee=True, handle_deg=a_r, s=s)
    return AP.contain(parts, w, d, h)


BUILDERS = {"mug": mug_parts, "mug_on_books": mug_on_books, "mug_pair": mug_pair}
MUG_TYPES: tuple[str, ...] = tuple(BUILDERS)


def parts(dtype: str, w: float, d: float, h: float, item: Optional[dict] = None) -> list[Part]:
    return BUILDERS[dtype](w, d, h, item)


def handle_hole(parts_: list[Part]) -> float:
    """The handle's free span (m) between the body and the inside of the loop, at the loop's middle height (a real
    handle takes a finger: about 2 cm), for a mug with its handle towards +X at the origin."""
    body = next(p for p in parts_ if p["role"] == "mug")
    handle = next(p for p in parts_ if p["role"] == "mug_handle")
    zm = (0.043 + 0.062) / 2.0
    rb = max(math.hypot(v[0], v[1]) for v in body["verts"] if abs(v[2] - zm) < 0.02)
    near = [v for v in handle["verts"] if abs(v[2] - zm) < 0.012]
    return min(v[0] for v in near) - rb
