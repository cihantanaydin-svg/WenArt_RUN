"""Real-looking books (30 Oct 2026; user, on the salon render of real04 run 20261030-043021-full: "I like this but
books could have been more detailed models"; lesson UL154).

What (pure: parts in the caller's local frame, the front towards -Y; every builder of books in a niche, on a shelf, in
a book set or a stack calls these, so one rule makes every book of every project):

- ``book`` : one hardcover book standing up: two cover boards (``BOOK["board_m"]``) a little larger than a cream page
  block (``PAPER_KEY``; the page edges show on the top and the fore-edge, ``BOOK["overhang_m"]``), a rounded spine (a
  half ellipse, ``BOOK["spine_bulge"]``) facing the viewer, and on most spines one or two bands or a label (a
  contrasting colour or a paper label). Covers in bookcloth (``cloth:linen:<colour>``, the bedding's linen scan in a
  muted palette, ``COVER_COLOURS``) or a dark glossy jacket now and then.
- ``row`` : a row of standing books from ``x0`` to ``x1``: varied thickness (``THICK_M``), height (70-100 % of the
  room) and depth, small gaps, and a book leaning on the row's end when the row is long enough (``LEAN``).
- ``stack`` : books lying flat, spines to the front, each a little smaller than the one under it and turned a little.

The parts stay inside the box the caller gives (thickness along X, depth along Y, height along Z); a caller that needs
a hard box runs ``detail_parts.contain`` as before. Sizes are designer values of real books (assumed): hardcovers
15-24 cm wide and 20-30 cm tall, 1.5-4.5 cm thick.
"""
from __future__ import annotations

import math

Part = dict

PAPER_KEY = "paper"              # the page block and the paper labels (``book_pages``: a cream matte paper)
JACKET_KEY = "dark"              # a dark glossy dust jacket now and then
COVER_PREFIX = "cloth:linen:"    # bookcloth: the linen scan in a cover colour (furniture.cloth_material_key)
# a curated, muted shelf (designer palette, assumed): mostly neutrals, a few deep or earthy accents
COVER_COLOURS: tuple[str, ...] = ("cream", "navy", "greige", "terracotta", "off white", "charcoal", "sand", "sage",
                                  "taupe", "dusty blue", "cream", "burgundy", "camel", "off white", "black", "greige")
BAND_COLOURS: dict[str, str] = {"navy": "gold", "charcoal": "cream", "burgundy": "gold", "olive": "cream",
                                "petrol": "cream", "rust": "charcoal", "ochre": "charcoal", "sage": "charcoal",
                                "cream": "rust", "off white": "navy", "taupe": "charcoal", "camel": "charcoal",
                                "terracotta": "cream", "dusty blue": "navy", "greige": "charcoal", "sand": "charcoal",
                                "black": "gold"}
BOOK = {"board_m": 0.0025, "overhang_m": 0.003, "spine_bulge": 0.22, "spine_seg": 8, "band_h_m": 0.006,
        "band_proud_m": 0.0006, "label_h": 0.16, "gap_m": 0.0015}
THICK_M: tuple[float, ...] = (0.028, 0.019, 0.036, 0.024, 0.044, 0.016, 0.031, 0.022, 0.040, 0.026)
LEAN = {"deg": 13.0, "min_row_m": 0.22, "min_books": 5}
ROLE = "book"
SPINE_ROLE = "book_spine"        # bevel 0: the spine is already round
PAGES_ROLE = "pages"


def cover_key(colour: str) -> str:
    return f"{COVER_PREFIX}{colour}"


def _hash(*v: int) -> int:
    h = 2166136261
    for x in v:
        h = ((h ^ (int(x) & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
    return h


def _cuboid(x0: float, x1: float, y0: float, y1: float, z0: float, z1: float, key: str, role: str) -> Part:
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def _half_prism(rx: float, ry: float, y_back: float, z0: float, z1: float, key: str, role: str, n: int) -> Part:
    """A vertical half-elliptic prism: its flat back on ``y = y_back``, its round face bulging to -Y by ``ry``, its
    width ``2 rx`` along X centred on x = 0 (wound outwards)."""
    ring = [(rx * math.cos(math.pi * k / n), y_back - ry * math.sin(math.pi * k / n)) for k in range(n + 1)]
    # ring runs from +X round the front (-Y) to -X: that order is clockwise seen from above
    m = len(ring)
    verts = [(x, y, z0) for x, y in ring] + [(x, y, z1) for x, y in ring]
    faces = [list(range(m)), list(range(2 * m - 1, m - 1, -1))]          # bottom (down), top (up)
    for k in range(m - 1):
        faces.append([k, m + k, m + k + 1, k + 1])                      # the round face, outwards
    faces.append([m - 1, 2 * m - 1, m, 0])                             # the flat back at +Y
    return {"verts": verts, "faces": faces, "key": key, "role": role}


def book(t: float, w: float, h: float, seed: int = 0, cover: str | None = None) -> list[Part]:
    """One standing hardcover book in its own frame: thickness ``t`` along X (centred on x = 0), the spine at
    y = -w/2 facing -Y, the fore-edge at +w/2, from z = 0 to ``h``."""
    s = _hash(seed, 7)
    if cover is None:
        cover = JACKET_KEY if s % 9 == 0 else cover_key(COVER_COLOURS[s % len(COVER_COLOURS)])
    b = min(BOOK["board_m"], t * 0.12)
    o = min(BOOK["overhang_m"], h * 0.02, w * 0.03)
    bulge = max(0.002, min(0.008, t * BOOK["spine_bulge"]))
    y_spine = -w / 2.0 + bulge                                       # the spine's flat back (where the boards start)
    parts = [
        _cuboid(-t / 2.0, -t / 2.0 + b, y_spine, w / 2.0, 0.0, h, cover, ROLE),                     # back board
        _cuboid(t / 2.0 - b, t / 2.0, y_spine, w / 2.0, 0.0, h, cover, ROLE),                       # front board
        _cuboid(-t / 2.0 + b, t / 2.0 - b, y_spine, w / 2.0 - o, o, h - o, PAPER_KEY, PAGES_ROLE),  # page block
        _half_prism(t / 2.0, bulge, y_spine, 0.0, h, cover, SPINE_ROLE, BOOK["spine_seg"]),
    ]
    trim = cover.removeprefix(COVER_PREFIX)
    mark = s // 7 % 4                                                # 0: two bands, 1: a label, 2: one band, 3: plain
    band_key = cover_key(BAND_COLOURS.get(trim, "cream")) if cover != JACKET_KEY else cover_key("gold")
    bh = min(BOOK["band_h_m"], h * 0.03)
    p = BOOK["band_proud_m"]
    if mark in (0, 2) and h > 0.08:
        for f in ((0.10, 0.86) if mark == 0 else (0.80,)):
            parts.append(_half_prism(t / 2.0 + p, bulge + p, y_spine, h * f, h * f + bh, band_key, SPINE_ROLE,
                                     BOOK["spine_seg"]))
    elif mark == 1 and h > 0.10 and t > 0.018:
        lh = h * BOOK["label_h"]
        parts.append(_half_prism(t / 2.0 * 0.72, bulge * 0.72 + p, y_spine, h * 0.62, h * 0.62 + lh, PAPER_KEY,
                                 SPINE_ROLE, BOOK["spine_seg"]))
    return parts


def _move(parts: list[Part], dx: float, dy: float, dz: float, ry_deg: float = 0.0, rz_deg: float = 0.0,
          pivot: tuple[float, float] = (0.0, 0.0)) -> list[Part]:
    """The parts turned by ``ry_deg`` about the Y axis through ``pivot`` (x, z), then by ``rz_deg`` about Z, then
    moved (in place, returned). Proper rotations keep the winding."""
    ca, sa = math.cos(math.radians(ry_deg)), math.sin(math.radians(ry_deg))
    cz, sz = math.cos(math.radians(rz_deg)), math.sin(math.radians(rz_deg))
    px, pz = pivot
    for part in parts:
        out = []
        for x, y, z in part["verts"]:
            x, z = x - px, z - pz
            x, z = x * ca + z * sa, -x * sa + z * ca
            x, z = x + px, z + pz
            x, y = x * cz - y * sz, x * sz + y * cz
            out.append((x + dx, y + dy, z + dz))
        part["verts"] = out
    return parts


def row(x0: float, x1: float, y: float, z: float, depth: float, max_h: float, seed: int = 0,
        lean: bool = True) -> list[Part]:
    """Standing books from ``x0`` to ``x1``, centred on ``y``, on a board at ``z``: varied thickness, heights 70-100 %
    of ``max_h``, depths 75-100 % of ``depth`` (fore-edges to the back, spines in a line at the front); the last book
    leans on the row when the row is long enough."""
    out: list[Part] = []
    span = x1 - x0
    if span < 0.03 or max_h < 0.04:
        return out
    depth = min(depth, 0.26)
    books, x, k = [], x0, 0
    want_lean = lean and span >= LEAN["min_row_m"]
    a = math.radians(LEAN["deg"])
    while True:
        t = THICK_M[_hash(seed, k) % len(THICK_M)] * (0.7 if max_h < 0.12 else 1.0)
        f = 0.72 + 0.28 * (_hash(seed, k, 3) % 9) / 8.0
        d = depth * (0.78 + 0.22 * (_hash(seed, k, 5) % 5) / 4.0)
        reserve = (max_h * math.sin(a) + 0.045) if want_lean and len(books) + 1 >= LEAN["min_books"] else 0.0
        if x + t > x1 - reserve and books:
            break
        if x + t > x1:
            t = x1 - x
            if t < 0.008:
                break
        books.append((x + t / 2.0, t, d, max_h * f, k))
        x += t + BOOK["gap_m"]
        k += 1
        if k > 40:
            break
    y_front = y - depth / 2.0
    for cx, t, d, bh, kk in books:
        out += _move(book(t, d, bh, seed=_hash(seed, kk, 11)), cx, y_front + d / 2.0, z)
    if want_lean and len(books) >= LEAN["min_books"]:
        cx, t, d, hu, kk = books[-1]
        xr = cx + t / 2.0                                            # the last upright book's free side
        tl = THICK_M[_hash(seed, 99) % len(THICK_M)]
        hl = hu * 0.94
        g = hl * math.sin(a)
        if xr + g + tl * math.cos(a) <= x1 + 1e-9:
            dl = depth * 0.9
            leaning = book(tl, dl, hl, seed=_hash(seed, 101))
            # its bottom-left edge on the board, its top resting on the upright book's side
            _move(leaning, 0.0, 0.0, 0.0, ry_deg=-LEAN["deg"], pivot=(-tl / 2.0, 0.0))
            out += _move(leaning, xr + g + tl / 2.0, y_front + dl / 2.0, z)
    return out


def stack(cx: float, cy: float, z: float, w: float, d: float, max_h: float, n: int = 3, seed: int = 0
          ) -> list[Part]:
    """``n`` books lying flat centred on (``cx``, ``cy``) from ``z``: the biggest at the bottom (``w`` long along X,
    ``d`` deep), spines to the front (-Y), each a little smaller and turned a few degrees, the stack within ``max_h``."""
    out: list[Part] = []
    if n < 1 or max_h < 0.01 or w < 0.04 or d < 0.04:
        return out
    zz = z + BOOK["band_proud_m"]                                  # the bands stand a little proud
    for k in range(n):
        t = min(THICK_M[_hash(seed, k, 17) % len(THICK_M)], max_h / n)
        s = 1.0 - 0.07 * k
        bl, bd = w * s, d * s
        lying = book(t, bd, bl, seed=_hash(seed, k, 19))
        # stand-up frame (thickness X, depth Y, height Z) -> lying: the height along +X from 0, the thickness up
        _move(lying, -bl / 2.0, 0.0, t / 2.0, ry_deg=90.0)
        turn = (-3.0, 4.0, -2.0, 2.5)[k % 4] * (1 if seed % 2 == 0 else -1)
        out += _move(lying, cx + 0.006 * (k % 2), cy, zz, rz_deg=turn)
        zz += t
    return out


def keys(parts: list[Part]) -> set[str]:
    return {p["key"] for p in parts}
