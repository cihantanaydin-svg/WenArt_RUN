"""Printed lettering: titles on book spines and covers, labels on kitchen bottles and jars (30 Oct 2026; user: "Writing
on the labels on the books are acceptable you can write things on them when needed", "Also wine vineger salt paper you
can write them when you see needed"; lesson UL199).

What (pure; the parts carry per-face UVs into one committed texture atlas, ``ATLAS_PATH``):

- the atlas (``scripts/make_print_atlas.py`` draws it once with the layout below; 2048 x 2048 RGBA): ``STRIPS`` title
  strips of 512 x 64 px (a title, an author line and a small publisher mark, transparent around the letters), half in
  light tones (gilt, cream: for dark bookcloth and jackets), half in dark tones (ink, rust: for light covers), in a few
  typographic styles (serif capitals, sans capitals, serif small capitals); and ``LABELS`` paper labels of 256 x 256 px
  (kitchen words such as OLIVE OIL, VINEGAR, SALT, PEPPER, SUGAR, FLOUR, COFFEE, and wine labels: an invented winery,
  a vintage year, a wine kind). Every title, author, winery and word is invented and brand-free.
- ``spine_title``: a thin print film on a standing book's spine (``book_parts`` frame: the spine at -Y), reading top
  to bottom with the letters' tops towards the front board, sized to the spine (the strip's 8:1 aspect kept).
- ``cover_title``: a print film on a book's front board (+X), reading across the cover, upright with the book.
- ``bottle_label``: a curved paper label round the front of a round bottle or jar, one ``LABELS`` cell on it.
- ``uvs`` of a part: one list per face, ``None`` or one (u, v) per corner; the faces that show no print sample a
  transparent corner of the atlas (``CLEAR_UV``). ``parametric.lettering_uvs`` gathers them in ``world_mesh`` order and
  the build writes them to the mesh's ``UV_LAYER`` (``furniture._mesh_object``), which only the lettering material
  (``materials.lettering_material``, key ``LETTERING_KEY``) reads: the other materials keep the box UVs.

Why: real books carry their titles; a shelf of blank spines reads as props. One atlas and one material keep it cheap: a
title is one thin box (8 vertices) per book.
"""
from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

Part = dict

ROOT = Path(__file__).resolve().parents[2]
ATLAS_PATH = ROOT / "assets" / "print" / "print_atlas.png"     # committed (.gitignore: !/assets/print/)
ATLAS_PX = 2048
UV_LAYER = "lettering"
LETTERING_KEY = "lettering"
ROLE = "lettering"

STRIP_PX = (512, 64)              # a spine strip: 8:1
STRIP_COLS, STRIP_ROWS = 4, 24
STRIPS = STRIP_COLS * STRIP_ROWS  # 96: the first half light tones, the second half dark
TONE_STRIPS = STRIPS // 2
LABEL_PX = (256, 256)
LABEL_TOP = STRIP_PX[1] * STRIP_ROWS          # 1536: the labels' rows start here
LABEL_COLS, LABEL_ROWS = 8, 2
CLEAR_PX = (2, 2)                 # a pixel of strip 0's margin: transparent
FILM_M = 0.0003                   # the print film's thickness
STAND_OFF_M = 0.00015             # ... and its gap in front of the surface it is printed on

# typographic styles of the strips (scripts/make_print_atlas.py draws them): (name, family, case, colour)
LIGHT_STYLES: tuple[tuple[str, str, str, tuple[int, int, int]], ...] = (
    ("gilt_serif", "serif_bold", "upper", (214, 178, 102)),
    ("cream_sans", "sans_semibold", "upper", (236, 228, 208)),
    ("cream_serif", "serif", "title", (232, 222, 200)),
    ("gilt_sans", "sans_semibold", "upper", (206, 170, 96)))
DARK_STYLES: tuple[tuple[str, str, str, tuple[int, int, int]], ...] = (
    ("ink_serif", "serif_bold", "upper", (28, 26, 28)),
    ("ink_sans", "sans_semibold", "upper", (34, 34, 38)),
    ("rust_serif", "serif", "title", (118, 52, 34)),
    ("navy_sans", "sans_semibold", "upper", (30, 42, 72)))

# invented titles and authors (generic phrases and initials; no real book, author or brand)
TITLES: tuple[str, ...] = (
    "The Quiet Harbour", "Notes on Light", "Stone and Water", "A Year of Gardens", "Northern Rooms", "The Long Table",
    "Small Houses", "Field Notes", "The Salt Road", "Paper Lanterns", "Islands of Wind", "On Making", "The Orchard Book",
    "Coastal Walks", "Clay and Fire", "The Green Hour", "Atlas of Rivers", "Weekend Kitchen", "Simple Forms",
    "Wild Herbs", "The Blue Door", "Patterns", "City of Bridges", "Woodland Trees", "The Art of Rest", "Mountain Light",
    "Old Maps", "Linen and Oak", "Quiet Interiors", "A Short History of Chairs", "The Tide Table", "Olive Groves",
    "Twelve Rooms", "The Glass Garden", "Seasons", "Drawing Daily", "Tea and Rain", "The Workshop", "Courtyards",
    "Lakes and Valleys", "Modern Living", "The Copper Pot", "Bread", "Night Trains")
AUTHORS: tuple[str, ...] = (
    "E. Marlow", "J. Arden", "L. Okafor", "S. Lindqvist", "M. Brennan", "A. Castell", "R. Vidal", "N. Hale",
    "T. Moreau", "K. Sato", "I. Novak", "C. Ferraro", "D. Whitlow", "H. Aksoy", "P. Laurent", "G. Ellery",
    "F. Dunmore", "O. Reyes", "B. Calder", "V. Holm", "Y. Demir", "W. Ashby", "Z. Kerr", "U. Brandt")
# paper labels: (name, word, a small line under it); the wine labels: (name, winery, year, kind)
WORD_LABELS: tuple[tuple[str, str, str], ...] = (
    ("olive_oil", "OLIVE OIL", "extra virgin"), ("vinegar", "VINEGAR", "red wine"), ("salt", "SALT", "sea salt"),
    ("pepper", "PEPPER", "black, whole"), ("sugar", "SUGAR", "cane"), ("flour", "FLOUR", "plain"),
    ("coffee", "COFFEE", "whole beans"), ("tea", "TEA", "loose leaf"), ("rice", "RICE", "long grain"),
    ("pasta", "PASTA", "penne"), ("oats", "OATS", "rolled"), ("spices", "SPICES", "mixed"))
WINE_LABELS: tuple[tuple[str, str, str, str], ...] = (
    ("wine_1", "Clos Verdane", "2018", "Red wine"), ("wine_2", "Domaine Aubel", "2020", "White wine"),
    ("wine_3", "Tenuta Corvale", "2017", "Rosso"), ("wine_4", "Quinta da Serrela", "2019", "Tinto"))
LABEL_NAMES: tuple[str, ...] = tuple(n for n, *_ in WORD_LABELS) + tuple(n for n, *_ in WINE_LABELS)
# a kitchen jar's contents key -> its label (kitchen_details._jar)
JAR_WORDS: dict[str, str] = {"rattan": "pasta", "ceramic": "flour", "dark": "coffee", "sugar": "sugar",
                             "rice": "rice", "tea": "tea", "oats": "oats"}
# the title is light (gilt or cream) on a cover darker than this (relative luminance of the colour name's linear RGB,
# ``wenart.style.colours``; the linen scan renders a cloth at about 0.7 of its flat colour, so gilt reads best up to
# a mid tone: designer value, assumed) ...
LIGHT_BELOW = 0.25
# ... and on these keys the colours module does not name (the dark jacket)
LIGHT_ON: tuple[str, ...] = ("dark", "jacket")


def strip_text(k: int) -> dict:
    """The strip ``k``'s texts and style (the atlas script draws exactly this): ``{"title", "author", "style",
    "family", "case", "colour", "tone"}``."""
    k = int(k) % STRIPS
    light = k < TONE_STRIPS
    i = k % TONE_STRIPS
    styles = LIGHT_STYLES if light else DARK_STYLES
    name, family, case, colour = styles[i % len(styles)]
    title = TITLES[(i * 7 + (0 if light else 3)) % len(TITLES)]
    author = AUTHORS[(i * 5 + (2 if light else 11)) % len(AUTHORS)]
    return {"title": title, "author": author, "style": name, "family": family, "case": case, "colour": colour,
            "tone": "light" if light else "dark"}


def tone_for(cover_key: str) -> str:
    """``light`` lettering on a dark cover, ``dark`` lettering on a light one (``cover_key``: a ``cloth:linen:<colour>``
    key, the jacket's ``dark`` or a paper key): by the cover colour's luminance, so every cover colour gets the
    readable tone."""
    colour = str(cover_key).rsplit(":", 1)[-1].strip().lower()
    if colour in LIGHT_ON:
        return "light"
    try:
        from wenart.style import colours as C

        r, g, b = C.linear_rgb(colour.replace("_", " "))[:3]
    except (ImportError, KeyError, ValueError, TypeError):
        return "dark"
    return "light" if 0.2126 * r + 0.7152 * g + 0.0722 * b < LIGHT_BELOW else "dark"


def strip_for(seed: int, tone: str, index: Optional[int] = None) -> int:
    """The strip of a book (deterministic): ``index`` (a book's place in its row) picks distinct strips along a row,
    ``seed`` where to start."""
    base = (int(seed) * 2654435761) % TONE_STRIPS
    i = (base + (int(index) if index is not None else 0)) % TONE_STRIPS
    return i if tone == "light" else TONE_STRIPS + i


def strip_cell(k: int) -> tuple[float, float, float, float]:
    """``(u0, v0, u1, v1)`` of strip ``k`` (v up from the image's bottom row, as Blender reads it), 1 px inside."""
    k = int(k) % STRIPS
    col, row = k % STRIP_COLS, k // STRIP_COLS
    x0, y0 = col * STRIP_PX[0], row * STRIP_PX[1]
    return _cell(x0, y0, x0 + STRIP_PX[0], y0 + STRIP_PX[1])


def strip_box_px(k: int) -> tuple[int, int, int, int]:
    """The strip's pixel box ``(x0, y0, x1, y1)`` (the image's top row y = 0)."""
    k = int(k) % STRIPS
    col, row = k % STRIP_COLS, k // STRIP_COLS
    return col * STRIP_PX[0], row * STRIP_PX[1], (col + 1) * STRIP_PX[0], (row + 1) * STRIP_PX[1]


def label_box_px(name: str) -> tuple[int, int, int, int]:
    i = LABEL_NAMES.index(name)
    col, row = i % LABEL_COLS, i // LABEL_COLS
    x0, y0 = col * LABEL_PX[0], LABEL_TOP + row * LABEL_PX[1]
    return x0, y0, x0 + LABEL_PX[0], y0 + LABEL_PX[1]


def label_cell(name: str) -> tuple[float, float, float, float]:
    return _cell(*label_box_px(name))


def _cell(x0: int, y0: int, x1: int, y1: int) -> tuple[float, float, float, float]:
    n = float(ATLAS_PX)
    return ((x0 + 1) / n, 1.0 - (y1 - 1) / n, (x1 - 1) / n, 1.0 - (y0 + 1) / n)


CLEAR_UV = ((CLEAR_PX[0] + 0.5) / ATLAS_PX, 1.0 - (CLEAR_PX[1] + 0.5) / ATLAS_PX)


def _film(x0, x1, y0, y1, z0, z1, face: int, corner_uvs) -> Part:
    """A thin box with the print on its face ``face`` (``book_parts._cuboid``'s order: 0 bottom, 1 top, 2 -Y, 3 +X,
    4 +Y, 5 -X); the other faces sample the transparent corner."""
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
    uvs = [[CLEAR_UV] * 4 for _ in faces]
    uvs[face] = [tuple(c) for c in corner_uvs]
    return {"verts": verts, "faces": faces, "key": LETTERING_KEY, "role": ROLE, "uvs": uvs}


def spine_title(t: float, w: float, h: float, z_lo: float, z_hi: float, k: int) -> Optional[Part]:
    """Strip ``k`` on the spine of a standing book (``book_parts.book``'s frame: thickness ``t`` along X, the spine's
    crown at y = -w/2, height ``h``) between ``z_lo`` and ``z_hi``: the text runs down the spine (-Z), the letters'
    tops towards the front board (+X), the strip's 8:1 aspect kept (as wide as the spine allows, as long as the
    stretch allows). None where it would be under 4 mm wide."""
    aspect = STRIP_PX[0] / STRIP_PX[1]
    half = min(t * 0.34, (z_hi - z_lo) / aspect / 2.0)
    if half < 0.002:
        return None
    length = 2.0 * half * aspect
    zc = (z_lo + z_hi) / 2.0
    za, zb = zc - length / 2.0, zc + length / 2.0
    y0 = -w / 2.0 - STAND_OFF_M - FILM_M
    u0, v0, u1, v1 = strip_cell(k)
    # face 2 (-Y): corners (x0, z0), (x1, z0), (x1, z1), (x0, z1): the top of the book (z1) is the text's start
    return _film(-half, half, y0, y0 + FILM_M, za, zb, 2, [(u1, v0), (u1, v1), (u0, v1), (u0, v0)])


def cover_title(t: float, w: float, h: float, k: int) -> Optional[Part]:
    """Strip ``k`` across a book's front board (+X; the spine at -Y): upright with the book, in its upper third, as
    wide as the cover allows less its margins."""
    aspect = STRIP_PX[0] / STRIP_PX[1]
    ya, yb = -w / 2.0 + w * 0.16, w / 2.0 - w * 0.10
    if yb - ya < 0.04:
        return None
    hh = (yb - ya) / aspect
    zc = h * 0.70
    x0 = t / 2.0 + STAND_OFF_M
    u0, v0, u1, v1 = strip_cell(k)
    # face 3 (+X): corners (y0, z0), (y1, z0), (y1, z1), (y0, z1): the text runs +Y, its letters up +Z
    return _film(x0, x0 + FILM_M, ya, yb, zc - hh / 2.0, zc + hh / 2.0, 3, [(u0, v0), (u1, v0), (u1, v1), (u0, v1)])


def bottle_label(cx: float, cy: float, z0: float, r: float, z_lo: float, z_hi: float, name: str,
                 n: int = 6) -> Part:
    """The paper label ``name`` (``LABEL_NAMES``) round the front (-Y) of a round bottle or jar of radius ``r`` (its
    bottom at ``z0``), from ``z_lo`` to ``z_hi`` over it: a curved film whose arc matches the label's square (at most
    150 degrees of the round), the label's text upright, read from the front."""
    hgt = z_hi - z_lo
    deg = min(150.0, math.degrees(hgt / max(r, 1e-6)))
    a0 = math.radians(-90.0 - deg / 2.0)
    ring = [a0 + math.radians(deg) * i / n for i in range(n + 1)]
    r_in, r_out = r + STAND_OFF_M, r + STAND_OFF_M + FILM_M
    outer = [(cx + r_out * math.cos(a), cy + r_out * math.sin(a)) for a in ring]
    inner = [(cx + r_in * math.cos(a), cy + r_in * math.sin(a)) for a in reversed(ring)]
    loop = outer + inner
    m = len(loop)
    za, zb = z0 + z_lo, z0 + z_hi
    verts = [(x, y, za) for x, y in loop] + [(x, y, zb) for x, y in loop]
    faces = [list(range(m - 1, -1, -1)), [m + i for i in range(m)]] + \
        [[i, (i + 1) % m, m + (i + 1) % m, m + i] for i in range(m)]
    u0, v0, u1, v1 = label_cell(name)
    uvs = [[CLEAR_UV] * len(f) for f in faces]
    for i in range(n):                              # the outer strips, left to right seen from the front
        ua, ub = u0 + (u1 - u0) * i / n, u0 + (u1 - u0) * (i + 1) / n
        uvs[2 + i] = [(ua, v0), (ub, v0), (ub, v1), (ua, v1)]
    part = {"verts": verts, "faces": faces, "key": LETTERING_KEY, "role": ROLE, "uvs": uvs}
    if signed_volume(part) < 0.0:
        part["faces"] = [list(reversed(f)) for f in part["faces"]]
        part["uvs"] = [list(reversed(u)) for u in part["uvs"]]
    return part


def signed_volume(part: Part) -> float:
    v, s = part["verts"], 0.0
    for f in part["faces"]:
        a = v[f[0]]
        for i in range(1, len(f) - 1):
            b, c = v[f[i]], v[f[i + 1]]
            s += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                  + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return s


def has_print(parts) -> bool:
    return any(p.get("uvs") for p in parts)
