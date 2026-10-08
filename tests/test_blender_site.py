"""CPU tests of the site around the whole building (wenart/blender/site.py, docs/milestone10.md §3.2 item 5,
§1.6b rows 1, 11, 12): the drawn ground (the example's flat ground at +-0.00) and the build's own terrain change
for the basement door (the south side at the basement floor, assumed, never written back), the sides and north,
light wells, the ground mesh, plot walls, trees, ``site: full`` / ``ground``, the sun turned by the building's
north and the object kinds of the site build."""
import copy
import json
from pathlib import Path

import pytest

from wenart import geometry as G
from wenart import views as V
from wenart.blender import geom2d, lighting
from wenart.blender import site as S

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))
OUTLINE = geom2d.ccw(EXAMPLE["slabs"][0]["outline"])          # outer faces of the outer walls: 0 .. 10.25 x 0 .. 8.25


def _base():
    return V.variant_building(EXAMPLE, "base")


def _terrain(b=None):
    """The example's terrain as the build makes it: the drawn ground and the basement door's side."""
    b = b or _base()
    return S.site_plan(b, b["levels"], OUTLINE, "full")["terrain"]


def test_the_drawn_ground_and_the_basement_door_terrain():
    before = copy.deepcopy(EXAMPLE["site"]["ground"])
    b = _base()
    drawn = S.terrain_model(b, OUTLINE)
    assert drawn["kind"] == "flat" and drawn["z"]["-y"] == 0.0 and not drawn["assumed"]     # drawn: all +-0.00
    doors = S.door_terrain(b, b["levels"], drawn, OUTLINE)
    assert list(doors) == ["-y"] and doors["-y"]["z"] == -3.0 and doors["-y"]["opening_ids"] == ["d_L-1_001"]
    t = S.terrain_model(b, OUTLINE, overrides=doors)
    assert t["kind"] == "sides" and t["z"] == {"-y": -3.0, "+y": 0.0, "+x": 0.0, "-x": 0.0}
    assert {a["field"] for a in t["assumed"]} == {"ground:-y", "terrain_slope"}      # the build's change, assumed
    assert t["changes"] == [{"axis": "-y", "z": -3.0, "reason": doors["-y"]["reason"], "opening_ids": ["d_L-1_001"]}]
    assert _terrain(b)["z"] == t["z"]                                                   # site_plan applies it
    assert EXAMPLE["site"]["ground"] == before                                          # never written back
    assert S.ground_z(t, 5.0, -4.0) == -3.0                                              # in front of the south facade
    assert S.ground_z(t, 5.0, 12.0) == 0.0 and S.ground_z(t, 14.0, 4.0) == 0.0
    # beyond the south-east corner the ground slopes from the east side (0) to the south side (-3)
    assert S.ground_z(t, 13.25, -1e-9) == pytest.approx(0.0, abs=1e-6)
    assert S.ground_z(t, 10.25 + 1e-9, -3.0) == pytest.approx(-3.0, abs=1e-6)
    assert S.ground_z(t, 13.25, -3.0) == pytest.approx(-1.5)
    assert S.ground_z(t, 0.0, 0.0) == -3.0                       # a building corner takes the lower of its sides
    assert t["north_deg"] == 0.0 and t["north_source"].startswith("site.north_deg")
    # a side with a drawn level of its own keeps it (a warning)
    own = copy.deepcopy(b)
    own["site"]["ground"]["levels"] = [{"side": "south", "azimuth_deg": 180.0, "z": {"value": -1.0, "method": "vector"}},
                                       {"side": "all", "z": {"value": 0.0, "method": "vector"}}]
    t = S.terrain_model(own, OUTLINE, overrides=doors)
    assert t["z"]["-y"] == -1.0 and not t["changes"] and any("drawn ground is kept" in w for w in t["warnings"])


def test_flat_ground_and_missing_sides():
    b = copy.deepcopy(EXAMPLE)
    b["site"]["ground"]["levels"] = [{"side": "all", "z": {"value": 0.0, "method": "vector"}}]
    t = S.terrain_model(b, OUTLINE)
    assert t["kind"] == "flat" and S.ground_z(t, 50.0, -50.0) == 0.0 and not t["assumed"]
    b["site"]["ground"]["levels"] = [{"side": "south", "azimuth_deg": 180.0, "z": {"value": -1.0, "method": "vector"}},
                                     {"side": "north", "azimuth_deg": 0.0, "z": {"value": 0.0, "method": "vector"}}]
    t = S.terrain_model(b, OUTLINE)
    assert t["z"]["+x"] == pytest.approx(-0.5) and t["z"]["-x"] == pytest.approx(-0.5)
    assert sum(a["field"].startswith("ground:") for a in t["assumed"]) == 2
    b["site"]["ground"] = {}
    t = S.terrain_model(b, OUTLINE, default_z=0.0)
    assert t["kind"] == "flat" and any(a["field"] == "ground" for a in t["assumed"])


def test_north_turns_the_sides_and_the_sun():
    b = copy.deepcopy(EXAMPLE)
    b["site"]["north_deg"] = {"value": 90.0, "method": "vector"}         # the building's +Y points east
    assert S.compass_to_building(0.0, 90.0) == pytest.approx((-1.0, 0.0))  # north is -X
    b["site"]["ground"]["levels"] = [{"side": "south", "z": {"value": -3.0, "method": "vector"}},
                                     {"side": "all", "z": {"value": 0.0, "method": "vector"}}]
    t = S.terrain_model(b, OUTLINE)
    assert t["z"]["+x"] == -3.0 and t["z"]["-y"] == 0.0                  # the south side is +X now
    assert lighting.building_azimuth(210.0, 90.0) == pytest.approx(120.0)
    assert lighting.building_azimuth(210.0, 0.0) == pytest.approx(210.0)
    del b["site"]["north_deg"]
    north, source = S.north_deg(b)
    assert north == 0.0 and source.startswith("assumed")


def test_sides_compass_and_drawing_relative():
    # $defs/side: compass with the building's north, else front = -Y, back = +Y, left = -X, right = +X
    assert S.side_direction("south", 0.0) == pytest.approx((0.0, -1.0))
    assert S.side_direction("south", 90.0) == pytest.approx((1.0, 0.0))
    assert S.side_direction("front") == (0.0, -1.0) and S.side_direction("all") is None
    assert S.side_of((0.0, -1.0), 0.0) == "south" and S.side_of((1.0, 0.0), 90.0) == "south"
    assert S.side_of((0.7, 0.71), 0.0) == "north" and S.side_of((0.71, 0.7), 0.0) == "east"
    assert S.side_of((0.0, -1.0), 0.0, north_known=False) == "front"
    assert S.side_of((-1.0, 0.1), 0.0, north_known=False) == "left"


def test_light_wells_for_basement_windows_below_the_ground():
    b = _base()
    wells, warnings = S.light_wells(b, b["levels"], _terrain(b), OUTLINE)
    assert wells == [] and warnings == []                                # the south side is open at -3.00
    flat = S.terrain_model(b, OUTLINE)                                   # the drawn flat ground alone
    wells, warnings = S.light_wells(b, b["levels"], flat, OUTLINE)
    assert {w["opening_id"] for w in wells} == {"win_L-1_001", "win_L-1_002"}
    assert any("d_L-1_001" in w and "below the ground" in w for w in warnings)
    w = next(w for w in wells if w["opening_id"] == "win_L-1_001")
    assert w["source"] == "assumed" and w["floor_z"] == pytest.approx(-2.1 - 0.15) and w["top_z"] == 0.0
    ys = [p[1] for p in w["polygon"]]
    xs = [p[0] for p in w["polygon"]]
    assert (min(ys), max(ys)) == pytest.approx((-0.8, 0.0))              # in front of the wall face
    assert (min(xs), max(xs)) == pytest.approx((4.625 - 1.2, 4.625 + 1.2))
    verts, _faces = S.light_well_faces(w)
    assert min(v[2] for v in verts) == pytest.approx(-2.25) and max(v[2] for v in verts) == pytest.approx(0.05)
    # a drawn light well is used as drawn
    b = copy.deepcopy(b)
    b["site"]["ground"]["light_wells"] = [{"opening_id": "win_L-1_002", "polygon": [[7, -1], [9, -1], [9, 0], [7, 0]],
                                           "depth": 2.5, "source": "drawn"}]
    wells, _ = S.light_wells(b, b["levels"], flat, OUTLINE)
    drawn = next(w for w in wells if w["opening_id"] == "win_L-1_002")
    assert drawn["source"] == "drawn" and drawn["floor_z"] == pytest.approx(-2.5)


def test_ground_faces_flat_and_on_a_slope():
    b = copy.deepcopy(EXAMPLE)
    flat = S.terrain_model(b, OUTLINE)
    ext = S.ground_extent(OUTLINE, [])
    verts, faces = S.draped_faces(ext, [OUTLINE], flat)
    area = sum(abs(G.polygon_signed_area([verts[i][:2] for i in f])) for f in faces)
    assert area == pytest.approx(G.polygon_area(ext) - G.polygon_area(OUTLINE), rel=1e-9)
    assert {v[2] for v in verts} == {0.0}
    t = _terrain()
    verts, faces = S.draped_faces(ext, [OUTLINE], t)
    assert all(len(f) == 3 for f in faces)
    assert all(v[2] == pytest.approx(S.ground_z(t, v[0], v[1])) for v in verts)
    assert min(v[2] for v in verts) == -3.0 and max(v[2] for v in verts) == 0.0
    for f in faces:                                                     # nothing under the building
        c = [sum(verts[i][k] for i in f) / 3.0 for k in range(2)]
        assert not G.point_in_polygon(c, OUTLINE)
    lifted, _ = S.draped_faces(ext, [OUTLINE], t, lift=S.GRASS_LIFT)
    assert all(v[2] == pytest.approx(S.ground_z(t, v[0], v[1]) + S.GRASS_LIFT) for v in lifted)
    fixed, _ = S.draped_faces([(0, 9), (2, 9), (2, 10), (0, 10)], [], t, lift=S.PAVING_LIFT, z=0.0)
    assert {v[2] for v in fixed} == {S.PAVING_LIFT}


def test_plot_walls_step_with_the_ground_and_trees_stand_on_it():
    t = _terrain()
    south = next(w for w in EXAMPLE["site"]["boundary_walls"] if w["id"] == "sw_L0_001")
    _verts, _faces, info = S.plot_wall_parts(south, t)
    assert info["height_assumed"] and info["height"] == 1.2 and info["segments"] == 11
    assert info["z_range"][0] == pytest.approx(-3.1)                    # 0.1 m under the lowest ground
    north = next(w for w in EXAMPLE["site"]["boundary_walls"] if w["id"] == "sw_L0_003")
    _, _, info = S.plot_wall_parts(north, t)
    assert info["z_range"] == pytest.approx([-0.1, 1.2])
    tree = EXAMPLE["site"]["decor"][0]
    parts = S.tree_parts(tree, t)
    gz = S.ground_z(t, *tree["center"])
    assert parts["height"] == pytest.approx(max(4.0, 1.6 * 3.0))
    assert parts["crown_z"][1] == pytest.approx(gz + parts["height"], abs=1e-3)
    crown = parts["crown"][0]
    assert max(v[0] for v in crown) - min(v[0] for v in crown) == pytest.approx(3.0, abs=0.01)
    bush = S.tree_parts(dict(tree, kind="plant", size=[1.0, 1.0]), t)
    assert bush["trunk"] is None and bush["height"] == S.DEFAULTS["plant_height"]


def test_site_plan_full_and_ground():
    b = _base()
    plan = S.site_plan(b, b["levels"], OUTLINE, "full")
    assert plan["ground_is_grass"]                                     # the grass covers the plot
    assert [a["id"] for a in plan["areas"]] == ["sp_001", "spk_001"]
    assert [a["area_id"] for a in plan["areas"]] == [None, "sa_L0_otopark"]
    assert [w["id"] for w in plan["plot_walls"]] == ["sw_L0_001", "sw_L0_002", "sw_L0_003", "sw_L0_004"]
    assert [x["id"] for x in plan["trees"]] == ["sd_L0_001"]
    assert {n["id"] for n in plan["not_built"]} == {"sa_L0_otopark", "sa_L0_bahce"}      # area labels: build false
    assert plan["plot"] and plan["plot_source"].startswith("site.plot")
    assert plan["terrain"]["changes"][0]["opening_ids"] == ["d_L-1_001"]
    ext = plan["extent"]
    m, pm = S.MARGIN_M, S.PLOT_MARGIN_M                                  # around the building and the plot
    assert G.bbox(ext) == pytest.approx([min(0.0 - m, -5.875 - pm), min(0.0 - m, -7.875 - pm),
                                         max(10.25 + m, 16.125 + pm), max(8.25 + m, 14.125 + pm)])
    ground = S.site_plan(b, b["levels"], OUTLINE, "ground")
    assert ground["plot_walls"] == [] and ground["areas"] == [] and ground["trees"] == []
    assert ground["not_built"][0]["kind"] == "site"
    assert ground["terrain"]["z"]["-y"] == -3.0                          # the basement door's side in both modes
    off = copy.deepcopy(b)
    off["site"]["boundary_walls"][0]["build"] = False
    assert len(S.site_plan(off, off["levels"], OUTLINE, "full")["plot_walls"]) == 3


def test_area_looks_drawn_first_then_the_resolved_ones():
    looks = {"garden": {"material": "grass", "source": "fallback"}, "paving": {"material": "paving", "source": "brief"}}
    assert S.area_look({"kind": "grass", "material": None}, looks)["material"] == "grass"
    assert S.area_look({"kind": "parking", "material": None}, looks)["source"] == "brief"
    own = S.area_look({"kind": "paving", "id": "sp_1", "material": "gravel", "colour": "sand"}, looks)
    assert (own["material"], own["colour"], own["source"]) == ("gravel", "sand", "documents")
