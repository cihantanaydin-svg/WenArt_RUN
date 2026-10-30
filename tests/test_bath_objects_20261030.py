"""UL166 / UL168 (30 Oct 2026, a bathroom of real04 run 20261030-043021-full): "Here models needs more details" (the
lit shelf column held a glass box with two black squares, loose pebbles, sticks with white balls, a green egg in a
white cylinder) and "These switches requires a rework" (the WC's flush plate: a black frame with two flat white
panes). The bathroom's styled objects are real products (``wenart.blender.bath_objects``). Pure tests."""
from __future__ import annotations

import math

import pytest

from wenart.blender import bath_objects as BO
from wenart.blender import bath_parts as BT
from wenart.blender import parametric as P


def _volume(part) -> float:
    v, s = part["verts"], 0.0
    for f in part["faces"]:
        a = v[f[0]]
        for i in range(1, len(f) - 1):
            b, c = v[f[i]], v[f[i + 1]]
            s += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                  + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return s


def _plain(key: str) -> str:
    for prefix in ("colour_", "accent_"):
        if key.startswith(prefix):
            key = key[len(prefix):]
    return key


def _roles(parts) -> set:
    return {p["role"] for p in parts}


PRODUCTS = {
    "pump": lambda: BO.pump_bottle(0, 0, 0, 0.03, 0.18, "terracotta"),
    "jar_cotton": lambda: BO.apothecary_jar(0, 0, 0, 0.04, 0.12, "wood", "cotton"),
    "jar_pads": lambda: BO.apothecary_jar(0, 0, 0, 0.035, 0.10, "wood", "pads"),
    "jar_pebbles": lambda: BO.apothecary_jar(0, 0, 0, 0.045, 0.11, "steel", "pebbles"),
    "jar_salt": lambda: BO.apothecary_jar(0, 0, 0, 0.035, 0.06, "wood", "salt"),
    "diffuser": lambda: BO.reed_diffuser(0, 0, 0, 0.035, 0.10, 0.2),
    "plant": lambda: BO.potted_plant(0, 0, 0, 0.05, 0.08, 0.22),
    "perfume": lambda: BO.perfume_bottle(0, 0, 0, 0.05, 0.03, 0.10),
    "candle": lambda: BO.candle_glass(0, 0, 0, 0.035, 0.08),
    "soap": lambda: BO.soap_dish(0, 0, 0, 0.05),
    "basket": lambda: BO.woven_basket(0, 0, 0, 0.30, 0.24, 0.14),
    "cotton": lambda: BO.cotton_stem((0, 0, 0), (0, 0, 1), 0.3),
    "flush": lambda: BO.flush_plate(0, 0.3, 0.98),
}


@pytest.mark.parametrize("name", sorted(PRODUCTS))
def test_every_product_is_closed_wound_outwards_with_known_keys(name):
    parts = PRODUCTS[name]()
    assert parts and all(_volume(p) > 0 for p in parts), name
    assert all(0 <= i < len(p["verts"]) for p in parts for f in p["faces"] for i in f)
    assert {_plain(p["key"]) for p in parts} <= set(P.MATERIAL_KEYS), name
    assert sum(len(p["verts"]) for p in parts) < 1500, name                    # small: low face counts


def test_a_pump_bottle_has_its_collar_pump_nozzle_and_label():
    parts = BO.pump_bottle(0, 0, 0, 0.03, 0.18, "dark", "handle")
    assert {"bottle", "cap", "pump", "nozzle", "label"} <= _roles(parts)
    nozzle = [v for p in parts if p["role"] == "nozzle" for v in p["verts"]]
    assert min(y for _x, y, _z in nozzle) < -0.025                                 # reaching forward (-Y)
    top = max(z for p in parts for _x, _y, z in p["verts"])
    assert top == pytest.approx(0.18, abs=0.003)
    # 30 Oct 2026 (UL184, "Better models with more details is needed"): a printed paper label on the bottle's front,
    # its lines of print in a contrasting ink, not a band round the bottle
    label = next(p for p in parts if p["role"] == "label")
    assert label["key"] == "paper" and max(y for _x, y, _z in label["verts"]) < 0.0
    assert [p for p in parts if p["role"] == "print"]
    white = BO.pump_bottle(0, 0, 0, 0.03, 0.18, "ceramic")
    assert {p["key"] for p in white if p["role"] == "print"} == {"dark"}


@pytest.mark.parametrize("fill", ["cotton", "pads", "pebbles"])
def test_an_apothecary_jar_has_a_lid_with_a_knob_and_its_fill_inside(fill):
    r, h = 0.04, 0.12
    parts = BO.apothecary_jar(0, 0, 0, r, h, "wood", fill)
    lid = [p for p in parts if p["role"] == "lid"]
    assert len(lid) == 2 and min(z for p in lid for _x, _y, z in p["verts"]) >= h - 0.003
    assert max(z for p in parts for _x, _y, z in p["verts"]) <= h + BO.JAR_LID_M + 1e-6
    inside = [v for p in parts if p["role"] == "fill" for v in p["verts"]]
    assert inside and max(math.hypot(x, y) for x, y, _z in inside) <= r - BO.JAR_GLASS_M + 1e-6
    assert max(z for _x, _y, z in inside) < h


def test_the_diffuser_fans_out_its_reeds_and_has_no_balls():
    parts = BO.reed_diffuser(0, 0, 0, 0.035, 0.10, 0.2, seed=1)
    reeds = [p for p in parts if p["role"] == "reed"]
    assert len(reeds) == BO.DIFFUSER["reeds"] and not (_roles(parts) & {"ball", "cotton"})
    tips = [max(p["verts"], key=lambda v: v[2]) for p in reeds]
    spread = max(math.hypot(x, y) for x, y, _z in tips)
    assert 0.03 < spread < 0.1                                                    # fanned, not a bundle


def test_the_plant_has_leaves_on_stems_inside_its_reach():
    parts = BO.potted_plant(0, 0, 0, 0.05, 0.08, 0.24, max_r=0.12)
    leaves = [p for p in parts if p["role"] == "leaf"]
    assert len(leaves) >= 6 and all(p["smooth"] for p in leaves) and "crown" not in _roles(parts)
    assert max(math.hypot(x, y) for p in parts for x, y, _z in p["verts"]) <= 0.12 + 0.01
    assert {"pot", "soil", "stem", "leaf"} <= _roles(parts)


def test_the_column_cubbies_hold_real_products():
    parts = BT.open_column_parts(0.4, 0.35, 1.8)
    roles = _roles(parts)
    assert {"leaf", "label", "nozzle", "reed", "lid", "fill", "liquid", "basket", "soap"} <= roles
    assert not roles & {"crown", "pebble", "cotton"}            # no egg, no loose pebbles, no balls on sticks
    assert BT.column_items(1.6)[:3] == ["towels", "pump bottles", "plant"]
    assert "basket" in BT.column_items(1.6) and "pebbles" in BT.CUBBY_STYLES
    # the perfume is a flacon with its scent inside, never a glass box with a black square on it
    perfume = [p for p in parts if p["role"] == "perfume"]
    liquid = [p for p in parts if p["role"] == "liquid"]
    assert perfume and len(liquid) == len(perfume) and all(p["key"] == "terracotta" for p in liquid)


def test_the_vanity_and_the_towel_shelf_take_the_real_products():
    parts = BT.stone_slab_vanity_parts(0.531, 0.342, 0.85)
    assert {"label", "nozzle", "fill", "lid"} <= _roles(parts)
    shelf = BT.towel_shelf_parts(*BT.TOWEL_SHELF_SIZE)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(shelf)
    assert z1 <= BT.TOWEL_SHELF_SIZE[2] + 1e-6 and {"jar", "lid", "fill"} <= _roles(shelf)
    stems = BT._stems(0, 0, 0, 0.05, 0.16, 0.45)
    # 30 Oct 2026 (UL184: the plumes and cotton bolls read as lollipops): pampas stems with plumes of fine wisps
    assert {"vase", "stem", "plume"} <= _roles(stems) and not {"cotton", "calyx"} & _roles(stems)


def test_the_flush_plate_is_a_real_dual_flush_actuator():
    """UL168: a slim rounded plate with a chamfer, a small and a large button with a fine shadow gap and a line each,
    in the room's finish; never a frame with two white panes."""
    y_wall, zb = 0.3, BT.FLUSH_PLATE_Z_M
    parts = BO.flush_plate(0.0, y_wall, zb, "handle", "handle")
    plate = parts[0]
    assert plate["role"] == "plate" and plate["key"] == "handle"
    xs = [x for x, _y, _z in plate["verts"]]
    zs = [z for _x, _y, z in plate["verts"]]
    ys = [y for _x, y, _z in plate["verts"]]
    assert max(xs) - min(xs) == pytest.approx(0.246) and max(zs) - min(zs) == pytest.approx(0.164)
    assert max(ys) == pytest.approx(y_wall) and y_wall - min(ys) == pytest.approx(BO.FLUSH["proud_m"])
    assert len(plate["verts"]) > 8                                                # rounded corners, a chamfer
    buttons = [p for p in parts if p["role"] == "button"]
    widths = sorted(max(x for x, _y, _z in p["verts"]) - min(x for x, _y, _z in p["verts"]) for p in buttons)
    assert len(buttons) == 2 and widths[0] < 0.75 * widths[1]                     # a small and a large button
    assert all(p["key"] == "handle" for p in buttons)                             # in the finish, no white panes
    assert sum(p["role"] == "gap" for p in parts) == 2 and sum(p["role"] == "symbol" for p in parts) == 3
    front = y_wall - BO.FLUSH["proud_m"]
    for b in buttons:                                                             # proud of the plate, inside it
        assert min(y for _x, y, _z in b["verts"]) < front - 0.001
        assert min(z for _x, _y, z in b["verts"]) > zb and max(z for _x, _y, z in b["verts"]) < zb + 0.164
    wc = BT.wall_hung_wc_parts(0.445, 0.705, 0.8)
    assert [p["role"] for p in wc].count("button") == 2 and BT.FLUSH_PLATE_M[:2] == BO.FLUSH["size_m"]
