"""CPU tests of the exterior cameras and looks (wenart/blender/exterior.py, docs/milestone10.md §3.3 item 1,
§1.6b rows 11, 12): the triangle model of the outside, the inside tests, the framing (level cameras, lens shift),
the line-of-sight checks on a fake scene with a tree and a plot wall, the camera plan of the example building
(the corners, the aerial view, one view per drawn elevation along its view bearing, the camera fields), the
outside looks (documents > brief > style > the fallback of wenart/defaults.yaml) and the facade metering of
render.py."""
import copy
import json
import math
from pathlib import Path

import numpy as np
import pytest
import yaml

from wenart import views as V
from wenart.blender import exterior as E
from wenart.blender import geom2d
from wenart.blender import render as RD
from wenart.blender import roof as R
from wenart.blender import site as S

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = json.loads((ROOT / "docs" / "examples" / "building_m10.example.json").read_text(encoding="utf-8"))


def _example_model(building=None):
    b = V.variant_building(building or EXAMPLE, "base")
    outline = geom2d.ccw(b["slabs"][0]["outline"])
    plan = S.site_plan(b, b["levels"], outline, "full")
    roof = R.roof_model(b["roof"], b)
    return b, E.build_model(b, b["levels"], roof, plan), plan


def _box_building(trees=(), walls=()):
    """A 10 x 8 m box of one level (3 m) on flat ground, with optional site trees and plot walls."""
    pts = [(0, 0), (10, 0), (10, 8), (0, 8)]
    walls_b = [{"id": f"w{i}", "level_id": "L0", "start": list(pts[i]), "end": list(pts[(i + 1) % 4]), "thickness": 0.25,
                "exterior": True} for i in range(4)]
    site = {"ground": {"levels": [{"side": "all", "z": {"value": 0.0, "method": "vector"}}]}, "decor": list(trees),
            "boundary_walls": list(walls)}
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.8}], "walls": walls_b, "openings": [],
            "rooms": [], "slabs": [], "site": site, "facade": {}}


def _box_model(b):
    outline, _ = geom2d.wall_outline(b["walls"])
    plan = S.site_plan(b, b["levels"], outline, "full")
    return E.build_model(b, b["levels"], None, plan), plan


def test_the_model_of_the_example():
    _b, m, _ = _example_model()
    assert len(m.prisms) == 3 and m.roof is not None
    assert m.z_range == pytest.approx((-3.2, 6.888), abs=1e-3)
    assert m.inside((5.0, 4.0, 1.0)) == "building"
    assert m.inside((5.0, 4.0, 6.5)) == "building"                     # in the attic under the ridge
    assert m.inside((5.0, -0.4, 3.6)) == "roof"                        # in the eaves overhang
    assert m.inside((-2.875, -3.875, 2.0)) == "tree"
    assert m.inside((5.0, -7.9, -2.5)) == "plot_wall"
    assert m.inside((5.0, -5.0, -2.8)) == "ground"                     # the south side at the basement floor
    assert m.inside((5.0, -5.0, -1.4)) is None
    # the rays see the building, the roof and the ground
    labels, t = m.cast((5.0, -20.0, -1.4), np.array([[0.0, 1.0, 0.0], [0.0, 1.0, 0.3], [0.0, 1.0, -0.2]]))
    assert labels.tolist() == [E.LABELS["building"], E.LABELS["building"], E.LABELS["ground"]]
    assert t[0] == pytest.approx(20.0, abs=1e-6)                        # the south facade at y = 0


def test_framing_keeps_the_camera_level_and_the_building_in_the_frame():
    b = _box_building()
    m, _ = _box_model(b)
    pts = E.building_points(m)
    pos = (22.0, -10.0, 1.6)
    lens, shift_y, target, warning = E.frame(pos, (10.0, 0.0, 1.5), pts, level=True)
    assert warning is None and E.LENS_RANGE_MM[0] <= lens <= E.LENS_RANGE_MM[1]
    assert target[2] == pytest.approx(1.6)                             # pitch 0: straight verticals
    tangents = geom2d.frustum_tangents(lens, E.SENSOR_MM, E.RESOLUTION)
    assert all(geom2d.point_in_frustum(p, pos, target, tangents, shift_y=shift_y) for p in pts)
    aerial = E.frame((30.0, -20.0, 20.0), (5.0, 4.0, 1.5), pts, level=False)
    assert aerial[1] == 0.0                                            # a pitched camera needs no shift


def test_a_blocked_camera_moves_along_its_line_and_a_wall_all_around_drops_it():
    # Milestone 11 (docs/milestone11.md §1.1 E14): a corner camera stands 30 degrees off the facade it faces at the
    # distance where the building fills ~70 % of the frame (the M10 rule: 12 m out on the exact 45 degree
    # diagonal). A 3 m wall piece across that nominal place: the camera moves along its line, 2 m further out.
    b0 = _box_building()
    m0, _ = _box_model(b0)
    nominal = next(p for p in E.plan_exterior(m0, b0, b0["levels"])[0] if p.get("corner") == 2)
    corner = (10.125, -0.125)
    dist = math.hypot(nominal["position"][0] - corner[0], nominal["position"][1] - corner[1])
    d = ((nominal["position"][0] - corner[0]) / dist, (nominal["position"][1] - corner[1]) / dist)
    assert nominal["placement"] == f"{dist:.1f} m from the building corner, 30 degrees off the front facade"
    assert math.degrees(math.acos(-d[1])) == pytest.approx(30.0, abs=1e-3)     # 30 off the front (-Y) normal
    c = nominal["position"]
    piece = {"id": "pw", "start": [c[0] - d[1] * 2.0, c[1] + d[0] * 2.0], "end": [c[0] + d[1] * 2.0, c[1] - d[0] * 2.0],
             "thickness": 0.3, "kind": "other", "height": {"value": 3.0, "method": "vector"}, "build": True}
    b = _box_building(walls=[piece])
    m, _ = _box_model(b)
    plans, dropped = E.plan_exterior(m, b, b["levels"])
    names = {p["name"] for p in plans}
    se = next((p for p in plans if p.get("corner") == 2), None)
    assert se is not None and se["warning"] and "moved" in se["warning"]
    moved = math.hypot(se["position"][0] - corner[0], se["position"][1] - corner[1])
    assert abs(moved - dist) >= 1.4 and se["placement"] == f"{moved:.1f} m from the building corner, 30 degrees off " \
                                                            f"the front facade"
    assert (se["position"][0] - corner[0]) / moved == pytest.approx(d[0], abs=1e-4)     # on the same line
    assert se["lens_mm"] == E.EYE_LENS_MM and E.FILL_RANGE[0] - 0.1 <= se["fill"] <= E.FILL_RANGE[1]
    assert {"ext_1", "ext_3", "ext_4", "ext_5"} <= names
    # a 4 m wall all around, 5 m out: no corner camera (10-15 m out along the diagonals) sees the building over it
    ring = [(-5, -5), (15, -5), (15, 13), (-5, 13)]
    walls = [{"id": f"pw{i}", "start": list(ring[i]), "end": list(ring[(i + 1) % 4]), "thickness": 0.3, "kind": "plot",
              "height": {"value": 4.0, "method": "vector"}, "build": True} for i in range(4)]
    b = _box_building(walls=walls)
    m, _ = _box_model(b)
    plans, dropped = E.plan_exterior(m, b, b["levels"])
    corners = [d for d in dropped if d["view"] == "corner"]
    assert len(corners) == 4 and all("100% of the view of the building is blocked" in d["dropped_reason"]
                                     for d in corners)
    assert all(d["kind"] == "exterior" and d["room_id"] is None and len(d["sides"]) == 2 for d in corners)
    assert any(p["name"] == "ext_5" for p in plans)                     # the aerial view looks over it


def test_the_exterior_views_of_the_example():
    b, m, plan = _example_model()
    plans, dropped = E.plan_exterior(m, b, b["levels"], plan["plot"], variant="base")
    names = [p["name"] for p in plans] + [d["name"] for d in dropped]
    assert sorted(names) == ["ext_1", "ext_2", "ext_3", "ext_4", "ext_5", "ext_6", "ext_7"]   # 2 drawn elevations
    assert len(plans) >= 5                                              # acceptance: >= 5 exterior views
    for p in plans:
        assert p["kind"] == "exterior" and p["room_id"] is None and p["level_id"] is None
        assert p["variant"] == "base" and p["dropped_reason"] is None and p["index"] == int(p["name"][4:])
        assert m.inside(p["position"]) is None
        assert p["score"]["aim_visible"] and p["score"]["building_share"] >= E.MIN_BUILDING_SHARE
        if p["view"] != "aerial":
            gz = S.ground_z(m.terrain, p["position"][0], p["position"][1])
            assert p["position"][2] == pytest.approx(gz + E.EYE_HEIGHT, abs=1e-3)
            assert p["pitch_deg"] == pytest.approx(0.0, abs=1e-6) and abs(p["shift_y"]) <= E.MAX_SHIFT_Y
        else:
            assert p["pitch_deg"] == pytest.approx(-E.AERIAL_PITCH_DEG, abs=0.5)
        if p["view"] == "corner":
            assert len(p["sides"]) == 2 and p["region_id"] is None
    # the south elevation (facade.elevations r7, view bearing 90: looking +Y) looks square at the south facade
    south = next(p for p in plans if p.get("region_id") == "r7")
    assert south["view"] == "elevation" and south["side"] == "south" and south["sides"] == ["south"]
    assert south["position"][0] == pytest.approx(5.125) and south["position"][1] < 0.0
    assert south["target"][0] == pytest.approx(5.125) and south["target"][1] == pytest.approx(0.0)
    assert {"win_L0_001", "win_L-1_001", "d_L-1_001"} <= set(south["visible_openings"])
    assert not set(south["visible_openings"]) & {"d_L0_001", "win_L0_002"}   # the north door, the west window
    # the east elevation (r8, bearing 180: looking -X): no openings drawn, none seen
    east = next(p for p in plans if p.get("region_id") == "r8")
    assert east["sides"] == ["east"] and east["position"][0] > 10.25 and east["position"][1] == pytest.approx(4.125)
    assert east["visible_openings"] == []
    # the south-west corner sees the building only through the tree: dropped with the reason
    sw = next(d for d in dropped if d["name"] == "ext_1")
    assert "blocked" in sw["dropped_reason"] and sw["sides"] == ["west", "south"] and sw["variant"] == "base"


def test_elevation_views_from_the_bearing_else_the_side():
    b = copy.deepcopy(EXAMPLE)
    views, warnings = E.elevation_views(b)
    assert [(v["region_id"], v["side"]) for v in views] == [("r7", "south"), ("r8", "east")] and not warnings
    assert views[0]["view"] == pytest.approx((0.0, 1.0)) and views[1]["outward"] == pytest.approx((1.0, 0.0))
    b["facade"]["elevations"][0]["view_bearing_deg"] = None            # no bearing: square to the side
    b["facade"]["elevations"].append({"region_id": "r99", "side": "all", "windows": 0, "doors": 0})
    views, warnings = E.elevation_views(b)
    assert views[0]["view"] == pytest.approx((0.0, 1.0)) and len(views) == 2
    assert any("r99" in w for w in warnings)


def _style(**extra):
    style = {"walls": {"material": "plaster_white"}, "window_frame": {"material": "painted_metal_white"},
             "door": {"material": "wood_oak_light"}}
    style.update(extra)
    return style


def test_exterior_fallback_equals_the_defaults_file():
    defaults = yaml.safe_load((ROOT / "wenart" / "defaults.yaml").read_text(encoding="utf-8"))
    assert E.EXTERIOR_FALLBACK == defaults["style"]["exterior_fallback"]
    assert set(E.EXTERIOR_SLOTS) == set(defaults["brief"]["exterior"]) == set(V.BRIEF_DEFAULTS["exterior"])


def test_resolve_looks_documents_brief_style_fallback():
    looks = E.resolve_looks(EXAMPLE, _style())
    # the example draws only a stone plinth (a z band of the south side): the facade itself is the fallback
    assert looks["facade"]["source"] == "fallback" and looks["facade"]["material"] == "render"
    assert looks["facade"]["rgb"] is not None and looks["facade"]["assumed"]           # colour "walls"
    assert (looks["roof"]["material"], looks["roof"]["colour"]) == ("concrete_tiles", "anthracite")
    assert looks["window_frame"]["material"] == "painted_metal_white"                    # "interior"
    assert looks["door"]["material"] == "wood_oak_light"
    assert (looks["paving"]["material"], looks["paving"]["colour"]) == ("paving", "grey")
    assert looks["garden"]["material"] == "grass"
    assert {"sill", "plot_wall", "light_well", "railing", "soffit", "bark", "foliage", "ground"} <= set(looks)
    assert looks["plot_wall"]["material"] == looks["facade"]["material"] and looks["plot_wall"]["source"] == "build"
    # the style profile's exterior slots (track C) win over the fallback; an assumed one counts as the fallback
    style = _style(exterior={"facade": {"material": "brick_red", "colour": None, "source": "style"},
                             "roof": {"material": "slate", "colour": None, "assumed": True}})
    looks = E.resolve_looks(EXAMPLE, style)
    assert (looks["facade"]["material"], looks["facade"]["source"]) == ("brick_red", "style")
    assert (looks["roof"]["material"], looks["roof"]["source"]) == ("slate", "fallback")
    # the brief's exterior words win over the style; a phrase without a material word is a warning
    brief = {"values": {"exterior": {"facade": "white render", "roof": "red clay tiles", "paving": "nice"}},
             "assumed": []}
    looks = E.resolve_looks(EXAMPLE, style, brief)
    assert (looks["facade"]["material"], looks["facade"]["colour"], looks["facade"]["source"]) == \
        ("render", "white", "brief")
    # Track C's tables: a clay roof keeps the colour of its photo texture (the colour word is a warning).
    assert (looks["roof"]["material"], looks["roof"]["colour"]) == ("clay_tiles", None)
    assert looks["paving"]["source"] == "fallback" and "nice" in looks["paving"]["warnings"][0]
    # the documents win over everything: a drawn whole facade and a drawn roof covering
    b = copy.deepcopy(EXAMPLE)
    b["facade"]["faces"].append({"side": "all", "wall_id": None, "level_id": None, "z_range": None,
                                 "material": "wood_cladding", "colour": "walnut brown", "source": "elevation",
                                 "evidence": [{"file": "x.dxf", "method": "vector", "confidence": 1.0}]})
    b["roof"]["covering"], b["roof"]["covering_colour"] = "standing_seam", "anthracite"
    looks = E.resolve_looks(b, style, brief)
    assert (looks["facade"]["material"], looks["facade"]["source"]) == ("wood_cladding", "documents")
    assert looks["facade"]["evidence"] and not looks["facade"]["assumed"]
    assert (looks["roof"]["material"], looks["roof"]["source"]) == ("standing_seam", "documents")
    assert EXAMPLE["facade"]["faces"][0]["material"] == "stone_cladding"                 # nothing written back


def test_brief_looks_agree_with_the_style_profile_and_its_assets():
    # review #29/#34: the brief's exterior words give the scene the style profile's (track C) slugs and the assets
    # it fetched
    from wenart.style import profile as P

    words = {"facade": "white painted brick", "window_frame": "black steel", "roof": "red clay tiles"}
    style = P.profile_from_brief({"style": "Scandinavian, white walls", "exterior": words})
    looks = E.resolve_looks(EXAMPLE, style, {"exterior": words})
    for slot in words:
        got = (looks[slot]["material"], looks[slot]["asset"], looks[slot]["source"])
        assert got == (style["exterior"][slot]["material"], style["exterior"][slot]["asset"], "brief"), slot
    assert looks["facade"]["asset"] == "PaintedBricks004"
    # without the profile's reading (a style without exterior slots) the same words give the same slug and asset
    bare = E.resolve_looks(EXAMPLE, _style(), {"exterior": words})
    assert (bare["facade"]["material"], bare["facade"]["asset"]) == ("brick_white", "PaintedBricks004")


def test_look_words():
    assert E.look_from_words("facade", "Light grey fibre cement panels") == {"material": "fibre_cement",
                                                                             "colour": "light grey"}
    assert E.look_from_words("window_frame", "anthracite aluminium") == {"material": "aluminium_anthracite",
                                                                         "colour": None}      # track C's slug
    assert E.look_from_words("roof", "something else") is None


def test_meter_stats_meter_the_facade_of_an_exterior_view():
    h, w = 40, 80
    light = np.zeros((h, w, 3))
    light[:20] = 1.0                                                    # the facade: bright
    light[20:] = 8.0                                                    # the ground: brighter
    albedo = np.full((h, w, 3), 0.5)
    index = np.zeros((h, w))
    depth = np.full((h, w), 10.0)
    nz = np.zeros((h, w))
    nz[20:] = 1.0                                                       # the ground faces up
    plain = RD.meter_stats(light, albedo, index, depth, set(), blocks_across=8)
    facade = RD.meter_stats(light, albedo, index, depth, set(), blocks_across=8, normal_z=nz)
    assert "metered" not in plain and facade["metered"] == "facade"
    assert facade["incident_p50"] == pytest.approx(1.0) and plain["incident_p50"] > 1.0
    tiny = np.ones((h, w))
    tiny[0, 0] = 0.0                                                    # a single facade pixel: every surface
    assert RD.meter_stats(light, albedo, index, depth, set(), blocks_across=8, normal_z=tiny)["metered"] == "surfaces"
