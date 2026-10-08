"""CPU tests of the exterior cameras (wenart/blender/exterior.py, docs/milestone10.md §3.3 item 1): the triangle
model of the outside, the inside tests, the framing (level cameras, lens shift), the line-of-sight checks on a
fake scene with a tree and a plot wall, the camera plan of the example building and the facade metering of
render.py."""
import json
import math
from pathlib import Path

import numpy as np
import pytest

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
    b, m, _ = _example_model()
    assert len(m.prisms) == 3 and m.roof is not None
    assert m.z_range == pytest.approx((-3.2, 6.888), abs=1e-3)
    assert m.inside((5.0, 4.0, 1.0)) == "building"
    assert m.inside((5.0, 4.0, 6.5)) == "building"                     # in the attic under the ridge
    assert m.inside((5.0, -0.5, 3.8)) == "roof"                        # in the eaves overhang
    assert m.inside((-3.0, -4.0, 2.0)) == "tree"
    assert m.inside((5.0, -8.0, -2.5)) == "plot_wall"
    assert m.inside((5.0, -5.0, -2.8)) == "ground"
    assert m.inside((5.0, -5.0, -1.4)) is None
    # the rays see the building, the roof and the ground
    labels, t = m.cast((5.0, -20.0, -1.4), np.array([[0.0, 1.0, 0.0], [0.0, 1.0, 0.3], [0.0, 1.0, -0.2]]))
    assert labels.tolist() == [E.LABELS["building"], E.LABELS["building"], E.LABELS["ground"]]
    assert t[0] == pytest.approx(20.0 - 0.125, abs=1e-6)


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


def test_a_blocked_camera_moves_along_its_diagonal_and_a_wall_all_around_drops_it():
    # a 3 m wall piece across the south-east diagonal, 12 m out (the nominal place): the camera moves to 10 m
    corner = (10.125, -0.125)
    d = (1 / math.sqrt(2), -1 / math.sqrt(2))
    c = (corner[0] + d[0] * 12.0, corner[1] + d[1] * 12.0)
    piece = {"id": "pw", "start": [c[0] - d[1] * 2.0, c[1] + d[0] * 2.0], "end": [c[0] + d[1] * 2.0, c[1] - d[0] * 2.0],
             "thickness": 0.3, "kind": "other", "height": {"value": 3.0, "method": "vector"}, "build": True}
    b = _box_building(walls=[piece])
    m, _ = _box_model(b)
    plans, dropped = E.plan_exterior(m, b, b["levels"])
    names = {p["name"] for p in plans}
    se = next((p for p in plans if p.get("corner") == 2), None)
    assert se is not None and se["warning"] and "moved" in se["warning"] and "inside the plot_wall" in se["warning"]
    assert se["placement"] == "10 m from the building corner along its diagonal"
    assert {"ext_1", "ext_3", "ext_4", "ext_5"} <= names
    # a 4 m wall all around, 5 m out: no corner camera (10-15 m out along the diagonals) sees the building over it
    ring = [(-5, -5), (15, -5), (15, 13), (-5, 13)]
    walls = [{"id": f"pw{i}", "start": list(ring[i]), "end": list(ring[(i + 1) % 4]), "thickness": 0.3, "kind": "plot",
              "height": {"value": 4.0, "method": "vector"}, "build": True} for i in range(4)]
    b = _box_building(walls=walls)
    m, _ = _box_model(b)
    plans, dropped = E.plan_exterior(m, b, b["levels"])
    corners = [d for d in dropped if d["view"] == "corner"]
    assert len(corners) == 4 and all("100% of the view of the building is blocked" in d["reason"] for d in corners)
    assert any(p["name"] == "ext_5" for p in plans)                     # the aerial view looks over it


def test_the_exterior_views_of_the_example():
    b, m, plan = _example_model()
    plans, dropped = E.plan_exterior(m, b, b["levels"], plan["plot"])
    names = [p["name"] for p in plans] + [d["name"] for d in dropped]
    assert sorted(names) == ["ext_1", "ext_2", "ext_3", "ext_4", "ext_5", "ext_6"]
    assert len(plans) >= 5                                              # acceptance: >= 5 exterior views
    for p in plans:
        assert p["kind"] == "exterior" and p["room_id"] is None and p["level_id"] is None
        assert m.inside(p["position"]) is None
        assert p["score"]["aim_visible"] and p["score"]["building_share"] >= E.MIN_BUILDING_SHARE
        if p["view"] != "aerial":
            gz = S.ground_z(m.terrain, p["position"][0], p["position"][1])
            assert p["position"][2] == pytest.approx(gz + E.EYE_HEIGHT, abs=1e-3)
            assert p["pitch_deg"] == pytest.approx(0.0, abs=1e-6) and abs(p["shift_y"]) <= E.MAX_SHIFT_Y
        else:
            assert p["pitch_deg"] == pytest.approx(-E.AERIAL_PITCH_DEG, abs=0.5)
    # the south elevation (facade.openings_seen) looks square at the south facade and sees its openings
    south = next(p for p in plans if p["view"] == "elevation")
    assert south["side"] == "south" and south["position"][0] == pytest.approx(5.0)
    assert {"win_L0_001", "win_L-1_001", "d_L-1_001"} <= set(south["visible_openings"])
    assert not set(south["visible_openings"]) & {"d_L0_001", "win_L0_002"}   # the north door, the west window
    # the south-west corner sees the building only through the tree: dropped with the reason
    sw = next(d for d in dropped if d["name"] == "ext_1")
    assert "blocked" in sw["reason"]


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
