"""UL154 (30 Oct 2026): "I like this but books could have been more detailed models" (real04 run
20261030-043021-full, cam_r_L-1_salon_1: the books in the lit niches beside the TV were plain coloured blocks).
Every book of every builder is a real-looking book (``wenart.blender.book_parts``)."""
from __future__ import annotations

import math
import re
from pathlib import Path

from wenart.blender import book_parts as BK
from wenart.blender import detail_parts as DP
from wenart.blender import parametric as P

ROOT = Path(__file__).resolve().parents[1]


def _volume(part) -> float:
    v, s = part["verts"], 0.0
    for f in part["faces"]:
        a = v[f[0]]
        for i in range(1, len(f) - 1):
            b, c = v[f[i]], v[f[i + 1]]
            s += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                  + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return s


def _books(parts):
    """The page blocks: one per book."""
    return [p for p in parts if p["role"] == BK.PAGES_ROLE]


def test_one_book_has_boards_pages_and_a_round_spine():
    parts = BK.book(0.03, 0.17, 0.24, seed=0)
    roles = [p["role"] for p in parts]
    assert roles.count(BK.ROLE) == 2 and roles.count(BK.PAGES_ROLE) == 1 and roles.count(BK.SPINE_ROLE) >= 1
    assert all(_volume(p) > 0 for p in parts)                        # closed, wound outwards
    pages = _books(parts)[0]
    covers = [p for p in parts if p["role"] == BK.ROLE]
    pz = [v[2] for v in pages["verts"]]
    cz = [v[2] for p in covers for v in p["verts"]]
    assert min(pz) > min(cz) and max(pz) < max(cz)                   # the boards overhang the page block
    assert pages["key"] == BK.PAPER_KEY and covers[0]["key"] != BK.PAPER_KEY
    spine = next(p for p in parts if p["role"] == BK.SPINE_ROLE)
    assert len(spine["faces"]) >= BK.BOOK["spine_seg"] + 3            # a rounded spine, not a flat face
    assert min(v[1] for v in spine["verts"]) < min(v[1] for v in pages["verts"])   # the spine faces the front


def test_spines_carry_bands_or_labels_on_most_books():
    marked = 0
    for seed in range(40):
        parts = BK.book(0.03, 0.17, 0.24, seed=seed)
        marked += sum(1 for p in parts if p["role"] == BK.SPINE_ROLE) > 1
    assert marked >= 25


def test_row_varies_sizes_and_leans_the_last_book():
    parts = BK.row(-0.35, 0.25, 0.0, 0.0, 0.17, 0.26, seed=4)
    pages = _books(parts)
    assert len(pages) >= 12
    thick = {round(max(v[0] for v in p["verts"]) - min(v[0] for v in p["verts"]), 3) for p in pages}
    tall = {round(max(v[2] for v in p["verts"]), 3) for p in pages}
    assert len(thick) >= 4 and len(tall) >= 4
    x0, y0, z0, x1, y1, z1 = DP.bbox(parts)
    assert x0 >= -0.35 - 0.001 and x1 <= 0.25 + 1e-6 and z0 >= -1e-9 and z1 <= 0.26 + 1e-6
    tilted = [p for p in pages if abs(p["verts"][4][0] - p["verts"][0][0]) > 0.01]   # a vertical edge that leans
    assert len(tilted) == 1
    covers = {p["key"] for p in parts if p["role"] == BK.ROLE}
    assert len(covers) >= 5 and all(k.startswith(BK.COVER_PREFIX) or k == BK.JACKET_KEY for k in covers)


def test_short_rows_stand_without_a_lean_and_stay_in_their_span():
    parts = BK.row(0.0, 0.12, 0.0, 0.5, 0.15, 0.2, seed=1)
    assert parts and DP.bbox(parts)[3] <= 0.12 + 1e-6 and DP.bbox(parts)[2] >= 0.5 - 1e-9
    assert all(abs(p["verts"][4][0] - p["verts"][0][0]) < 1e-9 for p in _books(parts))
    assert BK.row(0.0, 0.02, 0.0, 0.0, 0.15, 0.2) == []


def test_stack_lies_flat_spines_to_the_front():
    parts = BK.stack(0.0, 0.0, 0.1, 0.24, 0.17, 0.11, n=3, seed=2)
    pages = _books(parts)
    assert len(pages) == 3 and all(_volume(p) > 0 for p in parts)
    for p in pages:
        xs, zs = [v[0] for v in p["verts"]], [v[2] for v in p["verts"]]
        assert max(zs) - min(zs) < max(xs) - min(xs)                 # lying, not standing
    assert min(v[2] for p in parts for v in p["verts"]) >= 0.1 - 1e-9
    spines = [p for p in parts if p["role"] == BK.SPINE_ROLE]
    assert min(v[1] for p in spines for v in p["verts"]) < min(v[1] for p in pages for v in p["verts"])


def test_every_book_builder_makes_real_books():
    for dtype, box, item in (("books", (0.3, 0.22, 0.12), {}), ("book_set", (0.4, 0.2, 0.24), {}),
                             ("book_set", (0.4, 0.2, 0.24), {"styled": {"books_share": 0.6}}),
                             ("wall_niche", (1.0, 0.26, 2.2), {"niche": {"shelves": 4}}),
                             ("desk_wall_unit", (1.2, 0.32, 0.68), {})):
        parts = P.decor_parts(dtype, *box, item)
        assert len(_books(parts)) >= 3, dtype
        assert not [p for p in parts if p["role"] == "book" and not (
            p["key"].startswith(BK.COVER_PREFIX) or p["key"] == BK.JACKET_KEY)], dtype
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x1 - x0 <= box[0] + 1e-6 and y1 - y0 <= box[1] + 1e-6 and z1 - z0 <= box[2] + 1e-6, dtype


def test_no_builder_makes_block_books_any_more():
    for rel in ("wenart/blender/detail_parts.py", "wenart/blender/salon_parts.py", "wenart/blender/parametric.py",
                "wenart/blender/kitchen_details.py", "wenart/blender/modules.py"):
        src = (ROOT / rel).read_text()
        assert not re.search(r"_box\([^\n]*\"book\"\)", src), rel


def test_book_materials_resolve():
    from wenart.blender import furniture as F
    from wenart.style import vocabulary as V

    keys, _ = F.style_material_keys({})
    assert "paper" in P.MATERIAL_KEYS and keys["paper"][0] == "book_pages"
    assert "book_pages" in V.FLAT_COLOURS and "book_pages" in V.ROUGHNESS
    assert F.cloth_material_key(BK.cover_key("navy"), keys) == "textile_linen"
    for colour in set(BK.COVER_COLOURS) | set(BK.BAND_COLOURS.values()):
        assert F.cloth_colour(BK.cover_key(colour)) == colour
        from wenart.blender import materials as M
        assert M.colour_linear(colour) is not None, colour
    assert P.BEVEL_BY_ROLE[BK.SPINE_ROLE] == 0.0 and P.BEVEL_BY_ROLE[BK.PAGES_ROLE] <= 0.001
    thin = BK.book(0.016, 0.15, 0.2, seed=3)
    assert all(P.part_bevel_radius(p) <= 0.0025 / 3.0 + 1e-9 for p in thin if p["role"] == BK.ROLE)
    assert math.isclose(BK.LEAN["deg"], 13.0)
