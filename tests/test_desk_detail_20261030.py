"""UL175 (30 Oct 2026, real04 run 20261030-112241-full, a bedroom desk): "laptop and stationary can be more detailed
models they are too plain" (a slab laptop with one dark key field, plain notebooks and a plain pen pot). Every desk's
laptop, monitor and stationery of every project are built as real products (``wenart.blender.desk_parts``). Pure
tests."""
from __future__ import annotations

from collections import Counter

import pytest

from wenart.blender import desk_parts as DK
from wenart.blender import furniture as F
from wenart.blender import parametric as P
from wenart.furniture import tabletop as TT


def _volume(part) -> float:
    v, s = part["verts"], 0.0
    for f in part["faces"]:
        a = v[f[0]]
        for i in range(1, len(f) - 1):
            b, c = v[f[i]], v[f[i + 1]]
            s += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                  + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return s


def _closed(part) -> bool:
    """Every edge used once in each direction: a closed, consistently wound mesh."""
    edges = Counter((f[i], f[(i + 1) % len(f)]) for f in part["faces"] for i in range(len(f)))
    return all(n == 1 and edges[(b, a)] == 1 for (a, b), n in edges.items())


def _mean(part, k: int) -> float:
    return sum(v[k] for v in part["verts"]) / len(part["verts"])


def _check(parts, box):
    assert all(_closed(p) and _volume(p) > 0 for p in parts)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert x1 - x0 <= box[0] + 1e-9 and y1 - y0 <= box[1] + 1e-9 and z1 - z0 <= box[2] + 1e-9 and z0 >= -1e-12
    keys, _assumed = F.style_material_keys({"floor": {"material": "wood_oak_light"}})
    assert {p["key"] for p in parts} <= set(P.MATERIAL_KEYS) and {p["key"] for p in parts} <= set(keys)


def test_the_laptop_has_keycaps_a_trackpad_a_hinge_and_a_rounded_shell():
    box = P.laptop_box(*TT.LAPTOP_BASES[0])
    parts = P.decor_parts("laptop", *box)
    _check(parts, box)
    roles = Counter(p["role"] for p in parts)
    assert roles["key"] >= 70 and roles["space_bar"] == 1 and roles["grille"] == 2
    assert roles["hinge"] == roles["camera"] == roles["logo"] == roles["trackpad"] == 1
    by = {p["role"]: p for p in parts}
    base, lid = by["base"], by["lid"]
    assert len(base["verts"]) > 8 and len(lid["verts"]) > 8                  # rounded corners, not a slab
    caps = [p for p in parts if p["role"] in ("key", "space_bar")]
    deck = max(v[2] for v in base["verts"])
    assert all(min(v[2] for v in p["verts"]) >= deck - 1e-9 for p in caps)     # on the deck, inside the well
    widths = sorted(round(max(v[0] for v in p["verts"]) - min(v[0] for v in p["verts"]), 4) for p in caps)
    assert widths[-1] > 4.0 * widths[0]                                       # the space bar spans several keys
    assert _mean(by["logo"], 1) > _mean(lid, 1)                                # the logo on the lid's back


def test_screens_show_a_desktop_in_front_of_the_screen():
    import math

    lean = math.radians(P.LAPTOP_OPEN_DEG - 90.0)
    for dtype, box, normal in (("laptop", P.laptop_box(*TT.LAPTOP_BASES[0]), (math.cos(lean), -math.sin(lean))),
                               ("monitor", TT.MONITOR_SIZE, (1.0, 0.0))):
        parts = P.decor_parts(dtype, *box)
        _check(parts, box)
        screen = next(p for p in parts if p["role"] == "screen")
        ui = [p for p in parts if p["role"] == "screen_ui"]
        assert len(ui) >= 15 and sum(1 for p in ui if p["key"] == DK.UI_KEY) >= 4, dtype
        assert {p["key"] for p in ui} - {DK.UI_KEY} >= {"dark"}, dtype           # text lines and icons on it
        front = min(v[1] * normal[0] + v[2] * normal[1] for v in screen["verts"])   # the screen's face (y, z)
        assert all(max(v[1] * normal[0] + v[2] * normal[1] for v in p["verts"]) <= front + 1e-9 for p in ui), dtype
        sx = [v[0] for v in screen["verts"]]
        assert all(min(sx) - 1e-9 <= v[0] <= max(sx) + 1e-9 for p in ui for v in p["verts"]), dtype
        assert all(P.part_bevel_radius(p) == 0.0 for p in ui)


def test_desktop_layers_stand_off_the_screen_in_order():
    parts = DK.desktop_parts(0.30, 0.19, -0.001)
    assert all(max(v[1] for v in p["verts"]) <= -0.001 + 1e-12 for p in parts)
    deepest = min(v[1] for p in parts for v in p["verts"])
    assert -0.001 - deepest <= 6 * DK.DESKTOP_LAYER_M + 1e-12
    assert all(-0.15 - 1e-9 <= v[0] <= 0.15 + 1e-9 and -1e-9 <= v[2] <= 0.19 + 1e-9 for p in parts for v in p["verts"])


def test_the_screen_ui_glows_faintly_and_never_lights_the_room():
    from wenart.blender import lighting as LI
    from wenart.blender import materials as M

    ui = max(M.SCREEN_UI_RGB) * M.SCREEN_UI_EMISSION
    wallpaper = max(max(rgb) for _pos, rgb in M.SCREEN_WALLPAPER) * M.SCREEN_EMISSION
    assert wallpaper < ui <= LI.SHADE_EMISSION_WM2SR / 4.0
    keys, _ = F.style_material_keys({})
    assert keys["screen_ui"][0] == keys["screen"][0] == "screen_black"


def test_the_stationery_is_real_notebooks_pens_pencils_a_pot_and_a_phone():
    box = DK.STATIONERY_SIZE
    parts = P.decor_parts("stationery", *box)
    _check(parts, box)
    roles = Counter(p["role"] for p in parts)
    assert roles["pages"] == 2 and roles["book"] >= 6 and roles["strap"] >= 2 and roles["clip"] >= 3
    assert roles["phone"] == 2 and roles["pot"] == 3
    pages = [p for p in parts if p["role"] == "pages"]
    assert all(p["key"] == "paper" for p in pages)
    longest = max(max(max(v[k] for v in p["verts"]) - min(v[k] for v in p["verts"]) for k in (0, 1)) for p in pages)
    assert longest >= DK.NOTEBOOK[0] - 0.003                                   # A5 at full size: never shrunk
    covers = {p["key"] for p in parts if p["role"] == "book"}
    assert {"dark", "leather"} <= covers
    pot = [p for p in parts if p["role"] == "pot"]
    cx, cy = _mean(pot[0], 0), _mean(pot[0], 1)
    radii = sorted({round(((v[0] - cx) ** 2 + (v[1] - cy) ** 2) ** 0.5, 4) for v in pot[0]["verts"]})
    assert radii[-1] - radii[0] == pytest.approx(DK.POT_WALL_M, abs=1e-4)      # a hollow pot with a real wall
    assert all(P.part_bevel_radius(p) <= DK.POT_WALL_M / 3.0 for p in pot)
    cones = [p for p in parts if p["role"] == "rod" and p["key"] == "wood"]
    assert len(cones) == 2                                                    # two sharpened pencils


def test_the_desk_set_stays_light_for_the_build():
    n = sum(len(p["verts"]) for t, box in (("laptop", P.laptop_box(*TT.LAPTOP_BASES[0])),
                                           ("stationery", DK.STATIONERY_SIZE), ("monitor", TT.MONITOR_SIZE))
            for p in P.decor_parts(t, *box))
    assert n < 4000
