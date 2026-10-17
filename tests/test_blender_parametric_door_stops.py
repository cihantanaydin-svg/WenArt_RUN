"""Door stops (fix round after P3, 16-17 Oct 2026; docs/milestone13.md §14.8): a closed door leaks no light.

What: on pod P3 the corridor view cam_r_L1_koridor_2_2 saw the sunlit roof terrace through the 5 mm slit round a
closed door (depth 196 m against the 60 m interior bound, a glowing line round the leaf): the leaf was smaller than
its frame on every side and nothing covered the gap. These CPU tests check, in projection along the wall normal (y),
that every point of the clear opening above the floor is covered by the leaf or by a stop, for the Milestone 6 door
(``shell.door_m6_parts``, the path P3 used) and for every framed style of ``parametric.door_parts``; that the stops
stay inside the wall depth, sit on the face away from the swing and against the leaf, and leave the leaf object, its
material and the door rays as they were.
Why: the old geometry fails the coverage at |x| = w/2 - frame - 2.5 mm (the slit); the tests below show it on the
leaf alone. How: pure Python (no Blender); the GPU twin is tests/gpu/test_m13_modules.py (rays through the jambs of
a built scene).
"""
from __future__ import annotations

import pytest

from wenart.blender import geom2d
from wenart.blender import parametric as P
from wenart.blender import shell

FRAMED_STYLES = tuple(s for s in P.DOOR_STYLES if s not in ("sliding", "barn"))
FW = shell.DEFAULTS["frame_width"]


def _box_of(verts) -> tuple[float, float, float, float, float, float]:
    xs, ys, zs = zip(*verts)
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def first_gap(boxes, x_lo: float, x_hi: float, z_lo: float, z_hi: float):
    """The first ``(x, z)`` of the region not covered by any box in projection along y, or None (exact: the region
    is cut at every box edge in z and the x-intervals of each band are merged)."""
    cuts = sorted({z_lo, z_hi} | {b[4] for b in boxes if z_lo < b[4] < z_hi} | {b[5] for b in boxes if z_lo < b[5] < z_hi})
    for z0, z1 in zip(cuts, cuts[1:]):
        zm = (z0 + z1) / 2.0
        spans = sorted((b[0], b[1]) for b in boxes if b[4] <= zm <= b[5])
        x = x_lo
        for a, c in spans:
            if a > x + 1e-9:
                break
            x = max(x, c)
        if x < x_hi - 1e-9:
            return (round(x + 1e-4, 4), round(zm, 4))
    return None


# --------------------------------------------------------------------------
# The Milestone 6 door (the path pod P3 used)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("width", [0.7, 0.9, 1.2])
@pytest.mark.parametrize("thickness", [0.065, 0.1, 0.25])
@pytest.mark.parametrize("swing", [1.0, -1.0])
def test_m6_door_stops_close_the_slit_round_the_closed_leaf(width, thickness, swing):
    h = 2.1
    parts = shell.door_m6_parts(width, h, thickness, swing)
    leaf = [_box_of(v) for v, _f in parts["leaf"]]
    stops = [_box_of(v) for v, _f in parts["stops"]]
    inner = width / 2.0 - FW
    # the old door: the leaf alone leaves the 5 mm slit at the jamb (P3's leak)
    gap = first_gap(leaf, -inner, inner, 0.01, h - FW)
    assert gap is not None and abs(abs(gap[0]) - inner) < 0.006
    # with the stops nothing is open above the floor slot (no threshold stop: light under a door is real)
    assert first_gap(leaf + stops, -inner, inner, 0.01, h - FW) is None
    # the leaf and the frame of Milestone 6 are unchanged; the stops are the frame's last three boxes
    assert leaf == [_box_of(geom2d.box((0.0, 0.0, (h - FW) / 2.0),
                                       (width - 2 * FW - 0.01, shell.DEFAULTS["leaf_thickness"], h - FW - 0.01))[0])]
    assert len(parts["frame"]) == 3 + len(stops) == 6 and parts["frame"][3:] == parts["stops"]
    lt = shell.DEFAULTS["leaf_thickness"] / 2.0
    for x0, x1, y0, y1, z0, z1 in stops:
        assert -thickness / 2.0 - 1e-9 <= y0 and y1 <= thickness / 2.0 + 1e-9          # inside the wall depth
        assert -inner - 1e-9 <= x0 and x1 <= inner + 1e-9 and z0 >= -1e-9 and z1 <= h - FW + 1e-9
        if swing > 0:                                   # away from the room the door opens into, against the leaf
            assert y1 == pytest.approx(-lt) and y0 < -lt
        else:
            assert y0 == pytest.approx(lt) and y1 > lt
        assert y1 - y0 >= P.DOOR_STOP_MIN_T_M - 1e-9
    # the stops overlap the leaf by 10 mm on the jambs and the head
    jamb = max(stops, key=lambda b: b[1])
    assert jamb[1] - jamb[0] == pytest.approx(P.DOOR_STOP_W_M) and leaf[0][1] - jamb[0] == pytest.approx(0.01)
    head = max(stops, key=lambda b: b[4])
    assert head[5] - leaf[0][5] == pytest.approx(0.005) and leaf[0][5] - head[4] == pytest.approx(0.01)


def test_m6_door_keeps_the_door_ray_and_the_threshold_ray_free():
    """The ray through the door centre (``door_ray_checks``, 1 m up) crosses only the leaf; the downward rays of
    test_blender_build's threshold test (at the opening centre, 1 cm inside each wall face) meet no stop."""
    for t in (0.1, 0.25):
        parts = shell.door_m6_parts(0.9, 2.1, t, 1.0)
        for x0, x1, y0, y1, z0, z1 in (_box_of(v) for v, _f in parts["stops"]):
            assert not (x0 <= 0.0 <= x1 and z0 <= 1.0 <= z1)                       # nothing at the centre, 1 m up
            for y in (t / 2.0 - 0.01, -(t / 2.0 - 0.01)):
                assert not (x0 <= 0.0 <= x1 and y0 <= y <= y1 and z0 <= 0.5)      # nothing under 0.5 m there


# --------------------------------------------------------------------------
# The Milestone 10 styles (parametric.door_parts)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("style", FRAMED_STYLES)
@pytest.mark.parametrize("side", [1, -1])
def test_every_framed_door_style_is_closed_by_its_stops(style, side):
    w, h, t = 0.9, 2.1, 0.2
    parts, record = P.door_parts({"door_style": style, "side": side}, w, h, t)
    roles = {p["role"] for p in parts}
    assert "stop" in roles and record["stop_side"] == ("both" if style == "pocket" else -side)
    inner = w / 2.0 - FW
    closing = [_box_of(p["verts"]) for p in parts if p["role"] in ("leaf", "panel", "glass", "stop", "astragal")]
    leaves = [_box_of(p["verts"]) for p in parts if p["role"] in ("leaf", "panel", "glass")]
    # the old door: the leaves alone leave the slit at the jambs (5 mm; 6 mm and a 2 mm meeting gap for two leaves)
    assert first_gap(leaves, -inner, inner, 0.01, h - FW) is not None
    assert first_gap(closing, -inner, inner, 0.01, h - FW) is None, style
    stops = [p for p in parts if p["role"] == "stop"]
    assert len(stops) == (6 if style == "pocket" else 3) and all(p["key"] == "frame" for p in stops)
    leaf_t = record["leaf_thickness"]
    face = leaf_t / 2.0 + (P.DOOR_PANEL_PROUD_M if style == "shaker_panel" else 0.0)
    for p in stops:
        x0, x1, y0, y1, z0, z1 = _box_of(p["verts"])
        assert -inner - 1e-9 <= x0 and x1 <= inner + 1e-9 and z0 >= -1e-9 and z1 <= h - FW + 1e-9
        assert min(abs(y0), abs(y1)) == pytest.approx(face)                          # against the leaf, no air slit
        if style != "pocket":
            assert (y0 + y1) / 2.0 * side < 0                                      # away from the swing
    if style in ("double", "folding"):
        (astragal,) = [p for p in parts if p["role"] == "astragal"]
        x0, x1, y0, y1, _z0, _z1 = _box_of(astragal["verts"])
        assert astragal["key"] == "leaf" and x0 < -0.001 and x1 > 0.001 and (y0 + y1) / 2.0 * side < 0


@pytest.mark.parametrize("style", [s for s in FRAMED_STYLES if s != "entrance"])
def test_stops_stay_inside_a_thin_wall(style):
    """real03 has door walls of 0.065 and 0.085 m: the stop is clamped to the wall face (never thinner than
    ``DOOR_STOP_MIN_T_M``); an entrance leaf (0.065 m) fills such a wall, see the next test."""
    for t in (0.065, 0.085):
        parts, _ = P.door_parts({"door_style": style, "side": 1}, 0.8, 2.1, t)
        for p in parts:
            if p["role"] in ("stop", "astragal"):
                ys = [v[1] for v in p["verts"]]
                assert -t / 2.0 - 1e-9 <= min(ys) and max(ys) <= t / 2.0 + 1e-9, (style, t)
                assert max(ys) - min(ys) >= P.DOOR_STOP_MIN_T_M - 1e-9


def test_door_stop_boxes_clamp_and_skip():
    boxes = P.door_stop_boxes(0.9, 2.1, 0.05, 0.0325, 0.065, -1)                  # a leaf that fills the wall
    assert all(b[4] == pytest.approx(P.DOOR_STOP_MIN_T_M) for b in boxes)
    assert all(b[1] == pytest.approx(-(0.0325 + P.DOOR_STOP_MIN_T_M / 2.0)) for b in boxes)
    narrow = P.door_stop_boxes(0.13, 2.1, 0.05, 0.02, 0.1, 1)                      # no room for a head stop
    assert len(narrow) == 2


def test_the_leaf_object_and_its_material_do_not_change():
    """build_door_m10 groups the parts by ``shell.FRAME_ROLES``: the stops go into ``<id>_frame``; the leaf group
    and its first material (the leaf entry's manifest material) are the leaf's, as before (verifier of the P3
    analysis: a stop in the leaf object turned its material into the frame paint)."""
    class Mat:
        def __init__(self, name):
            self.name = name

    by = {"frame": Mat("trim"), "rail": Mat("metal"), "groove": Mat("metal"), "leaf": Mat("oak"),
          "glass": Mat("glass"), "handle": Mat("metal")}
    assert "stop" in shell.FRAME_ROLES
    for style in FRAMED_STYLES:
        parts, _ = P.door_parts({"door_style": style, "side": -1}, 0.9, 2.1, 0.2)
        frame = [p for p in parts if p["role"] in shell.FRAME_ROLES]
        leaf = [p for p in parts if p["role"] not in shell.FRAME_ROLES and p["key"] != "handle"]
        assert {p["role"] for p in frame} == {"frame", "stop"}
        assert "stop" not in {p["role"] for p in leaf}
        _v, _f, mats, _i = shell.opening_parts_mesh(leaf, by, (0.0, 0.0, 0.0), 0.0)
        assert mats[0].name == "oak", style
        _v, _f, fmats, _i = shell.opening_parts_mesh(frame, by, (0.0, 0.0, 0.0), 0.0)
        assert [m.name for m in fmats] == ["trim"]
