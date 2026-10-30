"""The towels as real towels (30 Oct 2026, lesson UL138, user on real04 run 20261029-201533-full: "I am guessing these
orange things are towels, they need more detail, a lot more detail": rolled towels were faceted cylinders, the hanging
towels flat slabs). CPU only: ``wenart.blender.towel_parts`` and the bathroom parts that use it, the terry material.

Every towel is a closed cloth mesh of real thickness, wound outwards, with rounded edges; a rolled towel shows its
spiral end; a folded stack its soft front folds and uneven layers in two shades; a hanging towel both layers over the
bar with a soft curve, folds, a sagging rounded hem and a woven band; the material is terry (a loop-pile bump, rough)
in the room's towel colour; the face counts stay small.
"""
from __future__ import annotations

import math
import sys
import types
from collections import Counter

import pytest

from wenart.blender import bath_parts as BT
from wenart.blender import bedding_parts as BP
from wenart.blender import furniture as BF
from wenart.blender import materials as MAT
from wenart.blender import parametric as P
from wenart.blender import towel_parts as TP
from wenart.style import finishes as FIN


def _closed(part) -> bool:
    """Every edge of the mesh is shared by exactly two faces, in opposite directions (a closed, consistently wound
    surface)."""
    edges = Counter()
    for f in part["faces"]:
        for i in range(len(f)):
            edges[(f[i], f[(i + 1) % len(f)])] += 1
    return all(n == 1 and edges.get((b, a)) == 1 for (a, b), n in edges.items())


def _towels(parts):
    return [p for p in parts if p["role"] in ("towel", "towel_band")]


# --------------------------------------------------------------------------
# The three towels
# --------------------------------------------------------------------------

def test_a_rolled_towel_shows_its_spiral_and_rests_on_its_shelf():
    r, length = 0.045, 0.22
    roll = TP.rolled_towel(0.1, 0.2, 0.5, r, length, "towel")
    assert _closed(roll) and TP._volume(roll) > 0 and roll.get("smooth")
    assert len(roll["faces"]) <= TP.ROLL_FACES_MAX
    x0, y0, z0, x1, y1, z1 = P.parts_bbox([roll])
    assert z0 == pytest.approx(0.5, abs=1e-9) and y1 - y0 == pytest.approx(length, abs=1e-9)
    assert 1.4 * r < x1 - x0 <= 2 * r + 1e-9 and z1 - z0 < x1 - x0                 # a roll, a little flattened
    path, t = TP.roll_path(r)
    angles = math.atan2(path[-1][1], path[-1][0]) - math.atan2(path[0][1], path[0][0])
    radii = [math.hypot(a, b) for a, b in path]
    assert radii == sorted(radii) and radii[-1] + t / 2.0 == pytest.approx(r)        # a spiral, out to r
    assert len(path) - 1 == round(TP.ROLL_TURNS * TP.ROLL_POINTS_PER_TURN) and angles  # two and a quarter turns
    pitch = t / TP.ROLL_FILL
    assert 0.004 < t < 0.02 and pitch - t > 0.001                                   # the cloth and the groove
    # the end shows the spiral: on the end face, the cloth's points lie on the turns, the groove between them is open
    end = [v for v in roll["verts"] if v[1] == pytest.approx(0.2 - length / 2.0)]
    assert len(end) == 2 * len(path) + 2 * TP.EDGE_SEGMENTS
    # the ends are rounded: the end outline is thinner than the cloth (0.45 of it)
    assert TP._rounded_stations(length / 2.0, t)[0][1] < 0.5


def test_a_folded_stack_has_soft_folds_uneven_layers_and_two_shades():
    stack = TP.folded_stack(0.0, 0.0, 1.0, 0.30, 0.25, 0.043, 3, "towel", seed=2)
    assert [p["key"] for p in stack] == ["towel", "towel_alt", "towel"]
    tops = []
    for k, towel in enumerate(stack):
        assert _closed(towel) and TP._volume(towel) > 0 and len(towel["faces"]) <= TP.FOLDED_FACES_MAX
        x0, y0, z0, x1, y1, z1 = P.parts_bbox([towel])
        assert x1 - x0 == pytest.approx(0.30, abs=0.02) and y1 - y0 == pytest.approx(0.25, abs=0.02)
        tops.append((z0, z1))
    heights = [z1 - z0 for z0, z1 in tops]
    assert len({round(h, 4) for h in heights}) == 3                                  # slightly uneven
    assert all(tops[k + 1][0] == pytest.approx(tops[k][0] + heights[k], abs=0.004) for k in range(2))  # stacked
    path, t = TP.folded_path(0.25, 0.043)
    front = min(a for a, _b in path)
    assert front == pytest.approx(-0.25 / 2.0 + t / 2.0, abs=1e-3)                  # one soft fold at the front ...
    fold = [p for p in path if p[0] < front + 0.002]
    assert fold and all(abs(b - 0.043 / 2.0) < 0.01 for _a, b in fold)              # ... round, at mid-height
    assert path[0][0] > path[-1][0]                                                  # the upper layer shorter: layers


def test_a_hanging_towel_has_two_layers_a_curve_folds_a_rounded_hem_and_a_band():
    bar_y, bar_z, bar_r, drop, w = 0.0, 1.0, 0.009, 0.43, 0.45
    towel, band = TP.draped_towel(0.0, bar_y, bar_z, bar_r, w, drop, "colour_towel", seed=1)
    for p in (towel, band):
        assert _closed(p) and TP._volume(p) > 0 and p.get("smooth")
    assert len(towel["faces"]) + len(band["faces"]) <= TP.DRAPED_FACES_MAX
    assert towel["key"] == "colour_towel" and band["key"] == "colour_towel_band" and band["role"] == "towel_band"
    xs, ys, zs = zip(*towel["verts"])
    assert min(zs) == pytest.approx(bar_z - drop, abs=1e-9)                         # down to its box's bottom
    assert max(xs) - min(xs) == pytest.approx(w, abs=1e-9)
    # never inside the bar: every point at least the bar's radius off its axis
    assert min(math.hypot(y - bar_y, z - bar_z) for _x, y, z in towel["verts"]) >= bar_r
    # both layers: cloth in front of the bar and behind it, the front longer
    front = [z for _x, y, z in towel["verts"] if y < bar_y - bar_r]
    back = [z for _x, y, z in towel["verts"] if y > bar_y + bar_r]
    assert front and back and min(front) < min(back) - 0.05
    # real thickness, not a plate: the cloth's two faces at mid-drop are about DRAPE_T_M apart
    mid = [y for x, y, z in towel["verts"] if abs(x) < 0.01 and abs(z - (bar_z - 0.25)) < 0.02 and y < bar_y]
    assert max(mid) - min(mid) >= TP.DRAPE_T_M * 0.9
    # gentle folds growing towards the hem: the front face moves more across the width at the hem than under the bar
    def spread(z_at):                              # the front layer's room-side face across the width at z_at
        face: dict = {}
        for x, y, z in towel["verts"]:
            if abs(z - z_at) < 0.025 and y < bar_y and abs(x) < w / 2.0 - 0.02:
                face[round(x, 4)] = min(face.get(round(x, 4), 1.0), y)
        return max(face.values()) - min(face.values())
    assert spread(bar_z - drop + 0.03) > 0.7 * TP.FOLD_AMPLITUDE_M
    assert spread(bar_z - 0.12) < 0.3 * TP.FOLD_AMPLITUDE_M
    # the woven band: a strip on the front face, 4.5 cm over the hem, 3.5 cm high, proud of the pile
    bx, by, bz = zip(*band["verts"])
    hem = bar_z - drop
    assert min(bz) == pytest.approx(hem + TP.BAND_FROM_HEM_M, abs=0.01) and max(bz) - min(bz) < TP.BAND_H_M + 0.01
    assert max(by) < bar_y - bar_r and max(bx) - min(bx) == pytest.approx(w, abs=0.002)


def test_the_bathroom_sets_have_no_slab_or_cylinder_towel_left():
    """Every towel of the bathroom parts (B7 rail, B18 shelf, B25 bar, B16 shower, B3/B12 vanity shelf, B5 column
    cubbies) is a cloth mesh (smooth, many faces) in the towel keys; the sets stay cheap."""
    sets = {
        "towel_rail": BT.towel_rail_parts(*BT.TOWEL_RAIL_SIZE),
        "towel_shelf": BT.towel_shelf_parts(*BT.TOWEL_SHELF_SIZE),
        "towel_bar": BT.towel_bar_parts(*BT.TOWEL_BAR_SIZE),
        "shower": BT.walk_in_shower_parts(0.9, 0.9, 2.0),
        "vanity": BT.stone_slab_vanity_parts(0.9, 0.5, 0.85),
        "column": BT.open_column_parts(0.4, 0.35, 1.8),
    }
    budget = {"towel_rail": 2000, "towel_shelf": 3200, "towel_bar": 2000, "shower": 2400, "vanity": 3500,
              "column": 5000}
    for name, parts in sets.items():
        towels = _towels(parts)
        assert towels, name
        for p in towels:
            assert p.get("smooth") and len(p["faces"]) > 100 and _closed(p), (name, p["role"], len(p["faces"]))
            assert p["key"].split("colour_")[-1] in ("towel", "towel_alt", "towel_band"), (name, p["key"])
        assert sum(len(p["faces"]) for p in towels) <= budget[name], (name, sum(len(p["faces"]) for p in towels))
    keys = {p["key"] for p in _towels(sets["towel_shelf"])}
    assert keys == {"colour_towel", "colour_towel_alt", "colour_towel_band"}           # a pair of shades, a band
    rolled = [p for p in _towels(sets["towel_shelf"]) if p["role"] == "towel" and
              P.parts_bbox([p])[2] > 0.2]                                           # the rolls on the board
    assert len(rolled) == 2
    # the towel over the ladder rail clears every bar of it (its lower bars pass between the towel's layers)
    for bar in [p for p in sets["towel_rail"] if p["role"] == "bar"]:
        xs, ys, zs = zip(*bar["verts"])
        cy, cz, r = (min(ys) + max(ys)) / 2.0, (min(zs) + max(zs)) / 2.0, (max(zs) - min(zs)) / 2.0
        for towel in _towels(sets["towel_rail"]):
            assert all(math.hypot(y - cy, z - cz) >= r - 1e-6 for x, y, z in towel["verts"]
                       if min(xs) <= x <= max(xs)), (towel["role"], cz)
    column_keys = {p["key"] for p in _towels(sets["column"])}
    assert {"towel", "towel_alt"} <= column_keys
    assert all(k in P.MATERIAL_KEYS for k in ("towel", "towel_alt", "towel_band"))


# --------------------------------------------------------------------------
# The terry cloth
# --------------------------------------------------------------------------

def test_the_towels_are_terry_cloth_in_the_rooms_colour_and_its_second_shade():
    entry = FIN.FURNITURE_MATERIALS[TP.TERRY_SLUG]
    assert entry["procedural"] == "wenart_weave" and entry["params"]["weave"] == "terry"
    assert entry["roughness"] >= 0.95 and MAT.weave_of(entry["params"]) == ("terry", "plain")
    strength, distance, pitch = BP.LOOK_LAYERS["terry"]["bump"]
    assert strength >= 0.8 and distance >= 0.002 and 0.002 <= pitch <= 0.004       # a deep loop pile
    assert "terry" not in BP.LOOKS                                                   # no bedding look
    keys, _assumed = BF.style_material_keys({})
    assert keys["towel"][0] == keys["towel_alt"][0] == TP.TERRY_SLUG and keys["towel_band"][0] == TP.BAND_SLUG
    over, notes = BF.design_overrides({"towel_colour": "rust"}, "washbasin")
    assert over["towel"] == {"slug": TP.TERRY_SLUG, "asset": None, "colour": "rust"}
    assert over["towel_alt"]["colour"] == "light rust" and over["towel_band"]["slug"] == TP.BAND_SLUG
    item = {"towel_colour": "olive", "colour": "black"}
    assert BF.towel_part_colour(item, "colour_towel") == "olive"
    assert BF.towel_part_colour(item, "colour_towel_alt") == "light olive"
    assert BF.towel_part_colour(item, "colour_towel_band") == "olive"
    assert BF.towel_part_colour(item, "colour_steel") is None
    assert TP.towel_shade(None) == "light grey" and TP.towel_shade("no such colour") == "no such colour"


def test_the_terry_weave_group_has_a_loop_pile_bump(monkeypatch):
    from test_bed_realism_20261029 import _Tree

    groups = {}
    bpy = types.SimpleNamespace(data=types.SimpleNamespace(node_groups=types.SimpleNamespace(
        get=lambda name: groups.get(name), new=lambda name, kind: groups.setdefault(name, _Tree(name)))))
    monkeypatch.setitem(sys.modules, "bpy", bpy)
    tree = MAT.weave_group("terry", "plain")
    kinds = [n.bl_idname for n in tree.all]
    assert tree.name == "wenart_weave_terry_plain"
    assert "ShaderNodeTexVoronoi" in kinds and "ShaderNodeTexNoise" in kinds and "ShaderNodeBump" in kinds
