"""CPU tests of the terrain surface (docs/milestone12.md §3.3 "Terrain"; wenart/levels/terrain.py): plane fit, the
triangulated surface, flat beyond the points, and the build's terrain model reading it (wenart/blender/site.py)."""
import pytest

from wenart.levels import terrain as T


def test_three_points_on_a_plane_give_a_planar_surface():
    pts = [(0, 0, 0.0), (10, 0, -1.0), (0, 10, 0.5), (10, 10, -0.5)]        # z = -0.1 x + 0.05 y
    s = T.fit_surface(pts)
    assert s["kind"] == "planar" and s["residual"] < 1e-6
    assert s["plane"][0] == pytest.approx(-0.1) and s["plane"][1] == pytest.approx(0.05)
    assert T.surface_z(s, 5, 5) == pytest.approx(-0.25)
    assert s["slope"] == pytest.approx((0.1 ** 2 + 0.05 ** 2) ** 0.5, abs=1e-4)


def test_points_off_a_plane_give_a_tin_through_them():
    pts = [(0, 0, 0.0), (10, 0, 0.0), (0, 10, 0.0), (10, 10, 0.0), (5, 5, 1.0)]   # a mound: 1 m off any plane
    s = T.fit_surface(pts)
    assert s["kind"] == "tin" and s["residual"] > 0.10 and len(s["triangles"]) == 4
    for x, y, z in pts:
        assert T.surface_z(s, x, y) == pytest.approx(z, abs=1e-6)               # through every point
    assert T.surface_z(s, 2.5, 5) == pytest.approx(0.5, abs=1e-6)
    assert T.delaunay(pts) == T.delaunay(pts)                                   # deterministic


def test_a_residual_within_tolerance_stays_planar():
    pts = [(0, 0, 0.0), (10, 0, 0.0), (0, 10, 0.0), (10, 10, 0.0), (5, 5, 0.08)]
    assert T.fit_surface(pts)["kind"] == "planar"
    assert T.fit_surface(pts, plane_residual=-1.0)["kind"] == "tin"             # forced (set_terrain tin)


def test_flat_beyond_the_points():
    pts = [(0, 0, 0.0), (10, 0, -1.0), (0, 10, 0.0), (10, 10, -1.0)]
    s = T.fit_surface(pts, blend_m=20.0, margin=2.0)
    assert s["flat_z"] == pytest.approx(-0.5)
    assert T.surface_z(s, 11.0, 5.0) == pytest.approx(-1.1)                      # within the margin: the plane
    assert T.surface_z(s, 12.0 + 20.0 + 5.0, 5.0) == pytest.approx(-0.5)        # 20 m past the margin: flat
    mid = T.surface_z(s, 12.0 + 10.0, 5.0)
    assert -1.2 < mid < -0.5                                                     # blending
    tin = T.fit_surface(pts + [(5, 5, 1.0)])
    assert T.surface_z(tin, 50.0, 50.0) == pytest.approx(tin["flat_z"])


def test_one_or_two_points_or_a_line_are_flat():
    assert T.fit_surface([])["kind"] == "flat"
    assert T.fit_surface([(0, 0, 1.0)])["flat_z"] == 1.0
    assert T.fit_surface([(0, 0, 0.0), (1, 1, 1.0), (2, 2, 2.0)])["kind"] == "flat"     # collinear
    assert T.surface_z({"kind": "flat", "flat_z": -0.15}, 3, 4) == -0.15


def test_the_build_reads_the_surface():
    """The build's terrain model takes a planar / tin surface of site.ground (Milestone 12) and evaluates it."""
    from wenart.blender import site as S
    surface = T.fit_surface([(0, 0, 0.0), (10, 0, -1.0), (0, 10, 0.0), (10, 10, -1.0)])
    b = {"site": {"ground": {"levels": [{"side": "all", "z": {"value": 0.0, "method": "vector"}}],
                             "surface": surface}}}
    outline = [(0, 0), (10, 0), (10, 10), (0, 10)]
    tm = S.terrain_model(b, outline)
    assert tm["kind"] == "planar" and S.ground_z(tm, 5, 5) == pytest.approx(-0.5)
    assert tm["z"]["+x"] < tm["z"]["-x"] and not S.is_flat(tm)
    over = S.terrain_model(b, outline, overrides={"-y": {"z": -3.0, "reason": "door", "opening_ids": ["d1"]}})
    assert over["kind"] == "planar" and any("surface is kept" in w for w in over["warnings"])
    verts, faces = S.draped_faces([(-5, -5), (15, -5), (15, 15), (-5, 15)], [outline], tm, step=5.0)
    assert faces and min(v[2] for v in verts) < -1.0 + 1e-6 < max(v[2] for v in verts)
    b["site"]["ground"]["surface"] = dict(surface, kind="flat")                 # a flat surface: the levels win
    assert S.terrain_model(b, outline)["kind"] == "flat"
