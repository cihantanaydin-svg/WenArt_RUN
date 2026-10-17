"""Fix round after P3, part 2 (17 Oct 2026): a cabinet under an inset basin is hollow above the basin bottom.

P3's review: the kitchen run's sink unit (``modules._base_unit_parts``) was one solid body up to the worktop's
underside, so its top face closed the 18 cm steel bowl 4 cm under the rim (a tray with a cabinet-paint floor). The
parametric sink cabinet (``parametric._sink``), the parametric vanity (``parametric._vanity``) and the module vanity
(``modules._bath_parts``) had the same solid body. ``parametric.open_carcass`` keeps the solid body only up to
``BASIN_CLEAR_M`` under the basin bottom and closes the rest with side, back (and front) boards; the outer box stays.

The checks are pure (no ``bpy``): a ray straight down through the bowl (``rest.MeshCaster`` per part) must meet the
basin's own bottom first, and no part other than the basin may reach into the bowl's inner void. The helpers are
imported by ``tests/test_m13_modules.py`` for the module builders.
"""
from __future__ import annotations

import pytest

from wenart.blender import parametric as P
from wenart.blender import rest as R
from wenart.blender.proxies import proxy_height


def surface_under(parts, x, y, z_from):
    """``(z, part)`` of the highest part surface a ray straight down from ``(x, y, z_from)`` meets, or None."""
    best = None
    for p in parts:
        hit = R.MeshCaster(p["verts"], p["faces"]).ray((x, y, z_from), (0.0, 0.0, -1.0))
        if hit is not None and (best is None or z_from - hit[0] > best[0]):
            best = (z_from - hit[0], p)
    return best


def _bbox(part):
    xs, ys, zs = zip(*part["verts"])
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def bowl_voids(parts):
    """The inner voids ``(x0, x1, y0, y1, z0, z1)`` of the basins among ``parts`` (role ``basin``; a basin is four
    walls and a bottom whose height is the wall thickness), one per bottom plate: ``z0`` is the top of the bottom
    plate, ``z1`` the rim."""
    basin = [p for p in parts if p["role"] == "basin"]
    out = []
    for bottom in basin:
        x0, x1, y0, y1, z0, z1 = _bbox(bottom)
        walls = []
        for b in basin:
            bx0, bx1, by0, by1, bz0, bz1 = _bbox(b)
            touches = bx0 <= x1 + 1e-6 and bx1 >= x0 - 1e-6 and by0 <= y1 + 1e-6 and by1 >= y0 - 1e-6
            if b is not bottom and touches and abs(bz0 - z0) < 1e-6 and bz1 > z1 + 1e-6:
                walls.append(b)
        if len(walls) != 4:
            continue                                  # a wall, not a bottom plate
        out.append((x0, x1, y0, y1, z1, max(_bbox(b)[5] for b in walls)))
    return out


def assert_open_bowls(parts, expected_bowls=1):
    """Every bowl among ``parts`` is open down to its own bottom (the module docstring)."""
    voids = bowl_voids(parts)
    assert len(voids) == expected_bowls, voids
    for x0, x1, y0, y1, zb, rim in voids:
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        for x, y in ((cx, cy), (cx - (x1 - x0) / 4.0, cy - (y1 - y0) / 4.0), (cx + (x1 - x0) / 4.0, cy + (y1 - y0) / 4.0)):
            z, part = surface_under(parts, x, y, rim - 1e-4)
            assert part["role"] == "basin" and z == pytest.approx(zb, abs=1e-6), (x, y, z, part["role"], part["key"])
        plate = min(_bbox(p)[4] for p in parts if p["role"] == "basin" and abs(_bbox(p)[5] - zb) < 1e-9)
        for p in parts:
            if p["role"] == "basin":
                continue
            # nothing else reaches into the bowl, down to the underside of its bottom plate (a carcass top inside
            # the plate is hidden but a coplanar mess for the bevel and the renderer)
            bx0, bx1, by0, by1, bz0, bz1 = _bbox(p)
            inside = bx0 < x1 - 1e-6 and bx1 > x0 + 1e-6 and by0 < y1 - 1e-6 and by1 > y0 + 1e-6 \
                and bz0 < rim - 1e-6 and bz1 > plate + 1e-6
            assert not inside, (p["role"], p["key"], _bbox(p), (x0, x1, y0, y1, plate, rim))
    return voids


def test_open_carcass_keeps_the_box_and_is_hollow_above_the_opening():
    parts = P.open_carcass(0.1, 0.02, 0.10, 0.8, 0.56, 0.76, 0.70, "painted")
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert (x0, x1, y0, y1, z0, z1) == pytest.approx((-0.3, 0.5, -0.26, 0.30, 0.10, 0.86))   # the solid box's
    assert {p["key"] for p in parts} == {"painted"} and {p["role"] for p in parts} == {"body"}
    z, part = surface_under(parts, 0.1, 0.02, 1.0)
    assert z == pytest.approx(0.70) and part is parts[0]                    # the cavity's floor, not 0.86
    assert len(parts) == 4                                                  # body, two sides, the back board
    front = P.open_carcass(0.0, 0.0, 0.0, 0.6, 0.5, 0.88, 0.70, "painted", front=True)
    assert len(front) == 5 and min(v[1] for v in front[-1]["verts"]) == pytest.approx(-0.25)
    # clamped: an opening at the bottom leaves only the boards, one at the top the solid box
    assert len(P.open_carcass(0.0, 0.0, 0.3, 0.6, 0.5, 0.5, 0.1, "wood")) == 3
    assert len(P.open_carcass(0.0, 0.0, 0.3, 0.6, 0.5, 0.5, 0.9, "wood")) == 1


@pytest.mark.parametrize("size", [(0.8, 0.6), (0.6, 0.6), (0.5, 0.4), (1.0, 0.55)])
def test_the_parametric_sink_cabinet_has_an_open_bowl_and_the_same_box(size):
    w, d = size
    h, _ = proxy_height("sink_kitchen", None)
    parts = P.build_parts("sink_kitchen", w, d, h)
    (x0, x1, y0, y1, zb, rim), = assert_open_bowls(parts)
    assert rim == pytest.approx(h) and zb == pytest.approx(h - 0.18 + 0.01)    # 17 cm deep, not 2 cm
    bx0, by0, bz0, bx1, by1, bz1 = P.parts_bbox(parts)
    assert (bx1 - bx0, by1 - by0, bz0) == pytest.approx((w, d, 0.0), abs=0.01)
    assert P.parametric_bbox("sink_kitchen", w, d, h)[2] == pytest.approx(bz1)


@pytest.mark.parametrize("size", [(0.8, 0.5), (0.6, 0.46), (1.2, 0.55)])
def test_the_parametric_vanity_has_an_open_bowl_and_the_same_box(size):
    w, d = size
    h, _ = proxy_height("washbasin", None)
    parts = P.build_parts("washbasin", w, d, h, piece={"design": {"vanity": True}})
    assert "pedestal" not in {p["role"] for p in parts}
    (_x0, _x1, _y0, _y1, zb, rim), = assert_open_bowls(parts)
    assert rim - zb > 0.10                                                      # the 15 cm basin, not 3 cm
    bx0, by0, bz0, bx1, by1, _bz1 = P.parts_bbox(parts)
    assert (bx1 - bx0, by1 - by0, bz0) == pytest.approx((w, d, 0.0), abs=0.01)
    # the pedestal basin of Milestone 4 keeps its own open bowl (no carcass)
    assert_open_bowls(P.build_parts("washbasin", w, d, h))
