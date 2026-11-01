"""UL243 / UL245 (1 Nov 2026, the user on real04 run 20261031-194116-full, the bathrooms): "Give more details to shower
models" (a thin slide rail with a hand shower, a stiff hose of two straight segments, a bare glass panel with one bar;
no mixer detail, no real rain head, no drain, no niche, no profiles or seals, no finish on the tray) and "make this
better" (the WC flush plate: a flat black slab with two printed lines). The shower's fittings and the plate are real
products (``wenart.blender.shower_parts``, ``bath_objects.flush_plate``) in the family's finish, every size real and
every part inside the drawn bay; general rules, real04 is only the test case. Pure tests (no ``bpy``)."""
from __future__ import annotations

import math

import pytest

import test_bathroom_details_20261029 as T
import test_small_items_20261031 as TS
from wenart.blender import bath_objects as BO
from wenart.blender import bath_parts as BT
from wenart.blender import furniture as BF
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.blender import shower_parts as SH
from wenart.furniture import fit as F
from wenart.furniture import small_items as SI

MODERN = {"family": "modern", "finish": "black", "level_access": True}
CLASSIC = {"family": "classic", "finish": "brass", "level_access": True}


def _role(parts, role):
    return [p for p in parts if p["role"] == role]


def _box(parts):
    return P.parts_bbox(parts)


def _plain(key: str) -> str:
    return P.plain_key(key)


# --------------------------------------------------------------------------
# 1. the shower's fittings
# --------------------------------------------------------------------------

def test_the_thermostatic_mixer_has_its_plate_two_knurled_knobs_a_diverter_and_an_outlet():
    parts = SH.walk_in_shower_parts(1.83, 0.8, 2.0, MODERN)
    back = 0.4
    plate = _role(parts, "mixer")
    assert len(plate) == 1
    x0, y0, z0, x1, y1, z1 = _box(plate)
    assert (x1 - x0, z1 - z0) == pytest.approx(SH.MIXER["plate_m"]) and y1 == pytest.approx(back)
    assert y1 - y0 == pytest.approx(SH.MIXER["plate_t_m"]) and (z0 + z1) / 2.0 == pytest.approx(BT.MIXER_Z_M)
    knobs = _role(parts, "knob")
    assert len(knobs) == 4                                           # an escutcheon and a cap each ...
    grips = _role(parts, "knurl")
    assert len(grips) == 2 and all(len(p["verts"]) == 8 * SH.MIXER["ribs"] for p in grips)   # ... a knurled grip
    for g in grips:
        cx = (min(x for x, _y, _z in g["verts"]) + max(x for x, _y, _z in g["verts"])) / 2.0
        radii = {round(math.hypot(x - cx, z - BT.MIXER_Z_M), 4) for x, _y, z in g["verts"][:2 * SH.MIXER["ribs"]]}
        assert len(radii) == 2 and max(radii) - min(radii) == pytest.approx(SH.MIXER["rib_m"], abs=2e-4)
    assert len(_role(parts, "diverter")) == 1 and len(_role(parts, "stop")) == 1
    assert len(_role(parts, "outlet")) == 2                          # the wall outlet and its elbow
    assert {p["key"] for p in plate + knobs + grips} == {"dark"}     # matte black with a satin sheen
    assert P.part_bevel_radius(grips[0]) == 0.0                     # the knurl stays crisp
    assert {p["key"] for p in _role(SH.walk_in_shower_parts(1.83, 0.8, 2.0, CLASSIC), "knob")} == {"brass"}


@pytest.mark.parametrize("w,d,look,size,shape", [
    (1.83, 0.8, MODERN, 0.30, "square"),
    (0.9, 0.7, {"family": "japandi", "finish": "black"}, 0.25, "round"),
    (1.2, 0.9, CLASSIC, 0.30, "round"),
])
def test_the_rain_head_is_a_real_head_with_its_nozzles_on_a_wall_arm(w, d, look, size, shape):
    lay = SH.layout(w, d, 2.0, look)
    assert lay["rain"]["size"] == pytest.approx(size) and lay["rain"]["shape"] == shape
    parts = SH.walk_in_shower_parts(w, d, 2.0, look)
    head = _role(parts, "head")
    assert len(head) == 1
    x0, y0, z0, x1, y1, z1 = _box(head)
    assert x1 - x0 == pytest.approx(size) and y1 - y0 == pytest.approx(size)
    assert z1 - z0 == pytest.approx(SH.RAIN["t_m"])
    cy = (y0 + y1) / 2.0
    reach = max(math.hypot(x, y - cy) for x, y, _z in head[0]["verts"])
    if shape == "round":
        assert reach == pytest.approx(size / 2.0, abs=1e-3)
    else:
        assert reach > size / 2.0 * 1.3                              # square corners
    nozzles = _role(parts, "nozzles")
    under = [p for p in nozzles if z0 - 0.003 <= min(z for _x, _y, z in p["verts"])
             and max(z for _x, _y, z in p["verts"]) <= z0 + 0.001]
    assert len(under) == 1 and len(under[0]["verts"]) // 12 >= 30    # a pattern of nozzles on its face
    assert max(z for _x, _y, z in _role(parts, "rosette")[0]["verts"]) == pytest.approx(BT.RAIN_HEAD_Z_M)
    ax0, ay0, _az0, ax1, ay1, _az1 = _box(_role(parts, "arm"))
    assert ay1 == pytest.approx(d / 2.0 - 0.010, abs=1e-6) and ay0 == pytest.approx(cy, abs=0.012)
    assert 0.25 <= d / 2.0 - cy <= 0.41                              # a 25-40 cm wall arm


def test_the_hand_shower_rides_on_a_slide_rail_with_a_slider_and_two_wall_brackets():
    lay = SH.layout(1.83, 0.8, 2.0, MODERN)
    parts = SH.walk_in_shower_parts(1.83, 0.8, 2.0, MODERN)
    xr = lay["rail_x"]
    rail = [p for p in _role(parts, "rail") if abs(_box([p])[0] - (xr - SH.RAIL["r_m"])) < 1e-6]
    assert len(rail) == 1
    _x0, _y0, z0, _x1, _y1, z1 = _box(rail)
    assert z0 == pytest.approx(BT.SLIDE_RAIL_Z_M[0] + SH.RAIL["end_m"]) and z1 - z0 > 0.75
    brackets = [p for p in _role(parts, "bracket") if abs((_box([p])[0] + _box([p])[3]) / 2.0 - xr) < 1e-6]
    assert len(brackets) == 6                                        # a rosette, a stand-off and an end block each
    assert len(_role(parts, "slider")) == 4
    hand = _role(parts, "hand_shower")
    handle, head = hand
    hx0, hy0, hz0, hx1, hy1, hz1 = _box([handle])
    assert hz1 - hz0 == pytest.approx(SH.HAND["handle_m"]) and len(handle["verts"]) > 18 * 40    # ribbed
    ex0, ey0, ez0, ex1, ey1, ez1 = _box([head])
    assert ex1 - ex0 == pytest.approx(2 * SH.HAND["head_r_m"], abs=1e-3) and ey0 < hy0       # the face looks in
    assert hz1 <= lay["rail_z"][1] and hz0 >= lay["rail_z"][0]


def test_the_hose_hangs_as_one_smooth_curve_of_a_real_length():
    for w in (1.83, 0.9):
        lay = SH.layout(w, 0.8, 2.0, MODERN)
        hx, hy, hz = lay["hand"]
        start = (hx, hy, hz - SH.HOSE["nut_m"])
        end = SH.outlet_end(lay["outlet"], lay["back"])
        end = (end[0], end[1], end[2] - SH.HOSE["nut_m"])
        length = SH.hose_length(start, end)
        assert length in SH.HOSE["lengths_m"] and length >= math.dist(start, end) + SH.HOSE["slack_m"]
        pts = SH.hose_path(start, end, length)
        assert pts[0] == pytest.approx(start) and pts[-1] == pytest.approx(end)
        assert sum(math.dist(a, b) for a, b in zip(pts, pts[1:])) == pytest.approx(length, rel=0.01)
        for a, b in ((pts[0], pts[1]), (pts[-1], pts[-2])):          # both ends hang straight down
            dz = b[2] - a[2]
            assert dz < 0 and abs(dz) > 0.9 * math.dist(a, b)
        low = min(p[2] for p in pts)
        assert SH.HOSE["min_z_m"] <= low < min(start[2], end[2]) - 0.15
        fine = SH.hose_path(start, end, length, n=int(length / SH.HOSE["pitch_m"]))     # as the builder sweeps it
        for a, b, c in zip(fine, fine[1:], fine[2:]):                # one smooth curve: no kink, no tight bend
            u = [b[i] - a[i] for i in range(3)]
            v = [c[i] - b[i] for i in range(3)]
            turn = math.acos(max(-1.0, min(1.0, sum(x * y for x, y in zip(u, v)) / (math.hypot(*u) * math.hypot(*v)))))
            assert turn < math.radians(12.0)
            assert math.dist(a, b) / max(turn, 1e-9) > 0.03          # bent no tighter than a 3 cm radius
        assert all(y <= lay["back"] for _x, y, _z in pts)
    parts = SH.walk_in_shower_parts(1.83, 0.8, 2.0, MODERN)
    hose = _role(parts, "hose")
    assert len(hose) == 3                                            # the hose and its two cone nuts
    tube = max(hose, key=lambda p: len(p["verts"]))
    rings = len(tube["verts"]) // SH.HOSE["sides"]
    assert rings > 150                                              # a rib every 7 mm (metal wound), not 2 sticks
    assert tube["smooth"] and tube["key"] == "dark"


def test_the_linear_drain_has_a_frame_and_a_slotted_grate_flush_with_the_floor():
    w, d = 1.83, 0.8
    parts = SH.walk_in_shower_parts(w, d, 2.0, MODERN)
    drain = _role(parts, "drain")
    assert len(drain) == 1 + 4 + SH.DRAIN["bars"]                   # the channel, the frame, the grate's bars
    x0, y0, z0, x1, y1, z1 = _box(drain)
    assert x1 - x0 == pytest.approx(w - 2 * SH.DRAIN["end_gap_m"]) and y1 - y0 == pytest.approx(SH.DRAIN["w_m"])
    assert (y0 + y1) / 2.0 == pytest.approx(d / 2.0 - SH.DRAIN["from_wall_m"])
    assert z0 >= -1e-9 and z1 <= BT.DRAIN_T_M + 1e-9               # flush with the floor (UL201)
    bars = [p for p in drain if abs((_box([p])[4] - _box([p])[1]) - SH.DRAIN["bar_m"]) < 1e-9]
    assert len(bars) == SH.DRAIN["bars"]
    ys = sorted((_box([p])[1] + _box([p])[4]) / 2.0 for p in bars)
    assert all(b - a > SH.DRAIN["bar_m"] for a, b in zip(ys, ys[1:]))      # slots between the bars
    assert any(p["key"] == SH.SHADOW_KEY for p in drain)            # the dark channel under the grate


def test_the_low_tray_has_its_stone_finish_and_a_fall_to_the_drain():
    w, d = 1.83, 0.8
    look = dict(MODERN, family="japandi", level_access=False)
    parts = SH.walk_in_shower_parts(w, d, 2.0, look)
    tray = _role(parts, "tray")
    assert tray and {p["key"] for p in tray} == {"worktop"}         # the family's dark stone
    drain_y = d / 2.0 - SH.DRAIN["from_wall_m"]
    y_d = drain_y - SH.DRAIN["w_m"] / 2.0
    z_front = SH.tray_top(-d / 2.0, d, drain_y)
    z_drain = SH.tray_top(y_d, d, drain_y)
    assert z_front == pytest.approx(BT.SHOWER_TRAY_T_M)
    assert (z_front - z_drain) / (y_d + d / 2.0) == pytest.approx(SH.FALL)          # 1.5 % to the drain
    front = tray[0]
    top = sorted({round(z, 5) for _x, _y, z in front["verts"] if z > 0})
    assert top == pytest.approx(sorted([z_drain, z_front]), abs=1e-4)
    drain = _role(parts, "drain")
    assert max(z for p in drain for _x, _y, z in p["verts"]) == pytest.approx(z_drain)   # its grate flush with the tray
    glass = _role(parts, "glass")
    assert min(z for p in glass for _x, _y, z in p["verts"]) == pytest.approx(
        SH.tray_top(SH.layout(w, d, 2.0, look)["gy"], d, drain_y))                   # the glass stands on the tray


def test_the_niche_is_lined_in_stone_with_a_shelf_two_bottles_and_a_soap_dish():
    w, d = 1.83, 0.8
    lay = SH.layout(w, d, 2.0, MODERN)
    niche = lay["niche"]
    assert niche["x1"] - niche["x0"] == pytest.approx(SH.NICHE["w_m"])
    assert niche["z1"] - niche["z0"] == pytest.approx(SH.NICHE["h_m"])
    parts = SH.walk_in_shower_parts(w, d, 2.0, MODERN)
    lining = _role(parts, "niche")
    assert len(lining) == 5 and {p["key"] for p in lining} == {"terrazzo"}     # the family's stone (modern)
    x0, y0, z0, x1, y1, z1 = _box(lining)
    assert (x0, x1, z0, z1) == pytest.approx((niche["x0"], niche["x1"], niche["z0"], niche["z1"]))
    assert y1 == pytest.approx(d / 2.0) and y1 - y0 == pytest.approx(SH.NICHE["d_m"])   # on the back wall
    shelf = _role(parts, "shelf")
    assert len(shelf) == 1 and abs((_box(shelf)[2] - z0) - (z1 - _box(shelf)[5])) < 0.01   # in its middle
    assert len(_role(parts, "trim")) == 4 and {p["key"] for p in _role(parts, "trim")} == {"dark"}
    inside = [p for p in parts if p["role"] == "bottle" and x0 <= _box([p])[0] and _box([p])[3] <= x1]
    assert len(inside) == 2
    assert all(_box([p])[2] == pytest.approx(z0 + SH.NICHE["t_m"]) for p in inside)    # on its floor
    assert len(_role(parts, "dish")) == 1
    # clear of the mixer, the rail and the hand shower
    assert niche["z0"] > BT.MIXER_Z_M + SH.MIXER["plate_m"][1] / 2.0
    assert niche["x1"] < lay["rail_x"] - SH.HAND["head_r_m"]
    # the small-items rules: a library slot for each when the fit picked a model of its kind
    slots = P.library_slots(SH.walk_in_shower_parts(w, d, 2.0, MODERN, BO.ALL))
    assert sorted(s["kind"] for s in slots) == ["pump_bottle", "pump_bottle", "soap_dish"]
    assert SI.host_slots("shower", w, d, 2.0, MODERN) == slots
    assert SH.layout(1.2, 0.5, 2.0, MODERN)["niche"] is None        # a shower too shallow for it


def test_the_glass_has_its_profiles_seals_rollers_and_a_stabiliser():
    w, d = 1.83, 0.8
    lay = SH.layout(w, d, 2.0, CLASSIC)
    slide = SH.walk_in_shower_parts(w, d, 2.0, dict(CLASSIC, shower_sides={"left": "wall", "right": "wall"}))
    assert len(_role(slide, "profile")) == 2 and len(_role(slide, "rail_bracket")) == 2
    assert len(_role(slide, "roller")) == 2 and len(_role(slide, "guide")) == 1 and len(_role(slide, "handle")) == 3
    assert len(_role(slide, "seal")) >= 3 and {p["key"] for p in _role(slide, "seal")} == {SH.SEAL_KEY}
    rail = [p for p in _role(slide, "rail") if _box([p])[3] - _box([p])[0] > w - 0.01]
    assert len(rail) == 1
    rail_top = _box(rail)[5]
    for roller in _role(slide, "roller"):                            # each grooved wheel rides on the rail
        assert _box([roller])[2] == pytest.approx(rail_top - 0.004, abs=0.0015)
    assert {p["key"] for p in _role(slide, "roller") + _role(slide, "profile") + rail} == {"brass"}
    fixed = SH.walk_in_shower_parts(0.9, 0.9, 2.0, MODERN)
    assert len(_role(fixed, "profile")) == 1 and len(_role(fixed, "glass_clamp")) == 1
    assert len(_role(fixed, "seal")) == 2 and "roller" not in {p["role"] for p in fixed}
    stab = _role(fixed, "stabiliser")
    assert len(stab) == 2                                            # the bar and its wall rosette
    sx0, sy0, _sz0, sx1, sy1, _sz1 = _box(stab)
    gy = SH.layout(0.9, 0.9, 2.0, MODERN)["gy"]
    assert sy0 < gy + 0.02 and sy1 == pytest.approx(0.45)            # from the glass to the back wall
    half = SH.layout(0.9, 0.9, 2.0, MODERN)["rain"]["size"] / 2.0
    assert sx1 < -half or sx0 > half                                 # clear of the rain head
    corner = SH.walk_in_shower_parts(1.2, 0.9, 2.2, {"shower_sides": {"left": "glass", "right": "wall"}})
    assert len(_role(corner, "clamp")) == 2 and len(_role(corner, "profile")) == 2      # the corner post, the closing
    assert lay["sliding"]


def test_the_towel_bar_moves_to_a_side_wall_when_the_niche_fills_the_back_wall():
    assert SH.layout(1.83, 0.8, 2.0, MODERN)["towel"]["wall"] == "back"
    narrow = SH.layout(0.9, 0.9, 2.0, {})
    assert narrow["niche"] and narrow["towel"]["wall"] == "left"
    parts = SH.walk_in_shower_parts(0.9, 0.9, 2.0, {})
    bar = _role(parts, "towel_bar")
    x0, y0, _z0, x1, y1, _z1 = _box(bar)
    assert x0 >= -0.45 - 1e-6 and x1 <= -0.45 + 0.07                 # on the left wall, along the depth
    assert y1 - y0 == pytest.approx(narrow["towel"]["length"]) and y0 > narrow["gy"] + 0.1
    assert _box(_role(parts, "towel"))[0] >= -0.45 - 1e-6             # its towel hangs inside the shower
    sides = {"left": "glass", "right": "wall"}
    assert SH.layout(0.9, 0.9, 2.0, {"shower_sides": sides})["towel"]["wall"] == "right"
    assert SH.layout(0.9, 0.9, 2.0, {"shower_sides": {"left": "glass", "right": "glass"}})["towel"] is None


@pytest.mark.parametrize("w,d,look", [
    (1.83, 0.8, MODERN), (1.83, 0.8, dict(MODERN, level_access=False)), (0.9, 0.9, {}),
    (1.2, 0.9, {"shower_sides": {"left": "glass", "right": "glass"}}), (1.4, 0.6, CLASSIC),
    (0.7, 0.8, {"family": "minimal", "finish": "chrome"}),
])
def test_every_shower_stays_in_its_bay_on_the_floor_and_under_its_headroom(w, d, look):
    parts = SH.walk_in_shower_parts(w, d, 2.2, look)
    assert all(-w / 2.0 - 1e-6 <= x <= w / 2.0 + 1e-6 and -d / 2.0 - 1e-6 <= y <= d / 2.0 + 1e-6
               for p in parts for x, y, _z in p["verts"])
    zs = [z for p in parts for _x, _y, z in p["verts"]]
    assert min(zs) >= -1e-9 and max(zs) <= BT.RAIN_HEAD_Z_M + 1e-9    # build.shower_headroom's 2.10 m
    assert all(T.volume(p) > -1e-9 for p in parts)
    assert all(0 <= i < len(p["verts"]) for p in parts for f in p["faces"] for i in f)
    assert {_plain(p["key"]) for p in parts} <= set(P.MATERIAL_KEYS)
    assert sum(len(p["verts"]) for p in parts) < 20000
    assert BT.walk_in_shower_parts(w, d, 2.2, look) == parts         # the bathroom builder's entry point


# --------------------------------------------------------------------------
# 2. the WC's flush plate
# --------------------------------------------------------------------------

def test_the_flush_plate_has_a_bezel_two_recessed_push_buttons_and_no_printed_lines():
    y_wall, zb = 0.3, BT.FLUSH_PLATE_Z_M
    F_ = BO.FLUSH
    parts = BO.flush_plate(0.0, y_wall, zb, "dark", "dark")
    a, b = F_["size_m"][0] / 2.0, F_["size_m"][1] / 2.0
    zc = zb + b
    ia, ib = a - F_["border_m"], b - F_["border_m"]
    bezel = parts[0]
    assert bezel["role"] == "plate"
    ri = F_["inner_r_m"]
    assert not any(abs(x) < ia - ri and abs(z - zc) < ib - ri for x, _y, z in bezel["verts"])       # a frame
    assert max(x for x, _y, _z in bezel["verts"]) == pytest.approx(a)
    depths = {round(y_wall - y, 5) for _x, y, _z in bezel["verts"]}
    assert len(depths) >= 6 and max(depths) == pytest.approx(F_["proud_m"])          # its edge rounded over
    well = _role(parts, "gap")
    assert len(well) == 1 and well[0]["key"] == "glass_black"
    well_front = min(y for _x, y, _z in well[0]["verts"])
    buttons = _role(parts, "button")
    assert len(buttons) == 2 and not _role(parts, "symbol")
    face = y_wall - F_["proud_m"] + F_["recess_m"]
    small, large = sorted(buttons, key=lambda p: _box([p])[0])
    for btn in buttons:
        bx0, by0, bz0, bx1, by1, bz1 = _box([btn])
        assert by0 == pytest.approx(face)                            # set back in the bezel
        assert well_front - by0 >= 0.003                              # a deep gap round it
        assert bz0 == pytest.approx(zc - ib + F_["gap_m"]) and bz1 == pytest.approx(zc + ib - F_["gap_m"])
        cap = btn["verts"][-20:]                                     # the dished face's middle
        assert min(y for _x, y, _z in cap) == pytest.approx(face + F_["dish_m"])
    assert _box([small])[0] == pytest.approx(-ia + F_["gap_m"]) and _box([large])[3] == pytest.approx(ia - F_["gap_m"])
    assert _box([large])[0] - _box([small])[3] == pytest.approx(F_["mid_gap_m"])
    ws, wl = (_box([p])[3] - _box([p])[0] for p in (small, large))
    assert ws / (ws + wl) == pytest.approx(F_["small_share"])
    assert all(_box([p])[3] - _box([p])[0] > 0.06 and _box([p])[5] - _box([p])[2] > 0.12 for p in buttons)


@pytest.mark.parametrize("look,plate,button", [
    (None, "handle", "handle"),
    ({"family": "modern", "finish": "black"}, "dark", "dark"),
    ({"family": "minimal", "finish": "chrome"}, "glass_white", "steel"),
    ({"family": "scandinavian", "finish": "black"}, "glass_white", "dark"),
    ({"family": "japandi", "finish": "black"}, "glass_black", "dark"),
    ({"family": "classic", "finish": "brass"}, "brass", "brass"),
    ({"family": "japandi", "finish": "black", "flush": "metal"}, "dark", "dark"),
])
def test_the_flush_plate_takes_the_familys_metal_or_glass(look, plate, button):
    assert BT.flush_keys(look) == (plate, button)
    parts = BT.wall_hung_wc_parts(0.445, 0.705, 0.8, look=look)
    assert next(p for p in parts if p["role"] == "plate")["key"] == plate
    assert {p["key"] for p in parts if p["role"] in ("button", "hinge")} == {button}
    keys, _assumed = BF.style_material_keys({})
    assert keys["glass_white"][0] == "ceramic_white" and keys["glass_black"][0] == "screen_black"
    assert {"glass_white", "glass_black"} <= set(P.MATERIAL_KEYS)


def test_the_layout_stage_records_the_plates_finish_and_the_rain_heads_shape():
    b, st = T.full("scandinavian")
    by = {f["id"]: f for f in b["furniture"]}
    assert by["t1"]["bath_look"]["flush"] == "glass_white" and "UL245" in by["t1"]["bath_look"]["reason"]
    assert by["s1"]["bath_look"]["rain_head"] == "square" and "UL243" in by["s1"]["bath_look"]["reason"]
    built = P.build_parts("toilet", 0.4, 0.7, 0.8, piece=by["t1"])
    assert next(p for p in built if p["role"] == "plate")["key"] == "glass_white"
    b2, _st2 = T.full("japandi")
    assert {f["id"]: f for f in b2["furniture"]}["s1"]["bath_look"]["rain_head"] == "round"


def test_the_fit_gives_the_showers_niche_its_small_items_and_the_plan_names_every_fitting():
    b, st = T.full("scandinavian")
    by = {f["id"]: f for f in b["furniture"]}
    cat = TS._cat(extras=[TS._dispenser()])
    asset = F.bath_made_fit(by["s1"], "scandinavian", "relaxed", st, cat)
    rec = asset["small_items"]
    assert asset["module_plan"]["small_items"] is rec
    assert set(rec["picks"]) | set(rec["gaps"]) == {"pump_bottle", "soap_dish"}
    built = MOD.module_parts(asset["module_plan"])
    kinds = sorted(s["kind"] for s in P.library_slots(built))
    assert kinds == sorted(["pump_bottle"] * 2 * ("pump_bottle" in rec["picks"])
                           + ["soap_dish"] * ("soap_dish" in rec["picks"]))
    words = asset["module_plan"]["products"][0]
    for word in ("thermostatic mixer", "rain head", "slide rail", "metal-wound hose", "linear drain", "niche",
                 "seal strips"):
        assert word in words, word
    plan = MOD.plan_bath_made(by["s1"])
    assert plan["height_m"] >= max(z for p in MOD.module_parts(plan) for _x, _y, z in p["verts"]) - 1e-9
