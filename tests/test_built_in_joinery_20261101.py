"""Built-in wardrobes read as real high-end joinery (1 Nov 2026, lesson UL246; user on real04 run 20261031-194116-full,
the master bedroom's slatted built-in run: "More details more realism needed"). CPU, pure.

What the run showed: four doors of even, flat, square-cut slats in one flat wood colour, a thin dark frame, a flat
orange interior with blurred clothes, no hinges or track, a single long bar, no plinth detail, the top band the same
slats, no shadow lines between the doors, no shelves or drawers to read, uniform light.

The rules are general (``wenart/blender/wardrobe_fronts.py`` ``JOINERY`` / ``joinery``, ``modules.py``
``slat_parts`` / ``see_through_parts``, ``wardrobe_contents.bay_light``, ``furniture.tone_copy``): (1) slats of real
products by family (20-40 mm, 10-20 mm gaps, horizontal or vertical), rounded profiles, veneer tones and their own
veneer patch, a backing behind the gaps; (2) the doors' hardware: brush seals in the shadow lines, a bottom track, a
scribe line to the ceiling, the family's pulls on every leaf edge a hand reaches; a solid top band; (3) the inside its
own finish, banded shelves, an oval rail on brackets, an LED profile with a diffuser and a soft, tilted beam; (4) the
rules of UL223 and the footprint stay.
"""
from __future__ import annotations

import math

import pytest

from wenart.blender import furniture as F
from wenart.blender import geom2d as GE
from wenart.blender import modules as MOD
from wenart.blender import parametric as P
from wenart.blender import wardrobe_contents as WC
from wenart.blender import wardrobe_fronts as WF
from wenart.style import colours as C
from wenart.style import vocabulary as V

K = MOD.SEE_THROUGH


def _piece(kind="slats", fam="modern", width=3.11, glass=None, ceiling=2.995, height=2.1):
    st = {"kind": kind, "ceiling_m": ceiling, "look": WF.built_in_look({"family": fam})}
    if glass:
        st["glass"] = glass
    return {"id": "f_robe", "type": "wardrobe", "height": height, "see_through": st,
            "footprint": {"center": [0, 0], "size": [width, 0.6], "rotation_deg": 0.0}}


def _parts(**kw):
    plan = MOD.module_plan(_piece(**kw))
    return plan, MOD.module_parts(plan)


def _bb(p):
    return P.parts_bbox([p])


def _volume(part) -> float:
    """The signed volume of a closed part (divergence theorem over its faces, fan triangles): > 0 when every face is
    wound outwards."""
    vol = 0.0
    vs = part["verts"]
    for f in part["faces"]:
        a = vs[f[0]]
        for i in range(1, len(f) - 1):
            b, c = vs[f[i]], vs[f[i + 1]]
            vol += (a[0] * (b[1] * c[2] - b[2] * c[1]) - a[1] * (b[0] * c[2] - b[2] * c[0])
                    + a[2] * (b[0] * c[1] - b[1] * c[0])) / 6.0
    return vol


def _area2d(pts) -> float:
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))


# ------------------------------------------------------------------------------------------- (1) the slats

def test_a_slat_is_a_rounded_profile_wound_outwards():
    w, d, r = 0.030, 0.018, 0.003
    prof = MOD.slat_profile(w, d, r, 2, 0.001)
    assert len(prof) >= 10 and _area2d(prof) > 0                                  # counter-clockwise, closed
    xs, ts = [p[0] for p in prof], [p[1] for p in prof]
    assert max(xs) - min(xs) == pytest.approx(w) and max(ts) - min(ts) == pytest.approx(d)
    front = [p for p in prof if abs(p[1]) < 1e-9]
    assert max(p[0] for p in front) - min(p[0] for p in front) == pytest.approx(w - 2 * r)   # eased front edges
    assert 0.95 * w * d < _area2d(prof) < w * d                                    # corners off, a real section
    # swept along x (a horizontal slat) or z (a vertical one): closed, every face outwards, its volume its section's
    for ev in ((0.9, 0.0, 0.0), (0.0, 0.0, 2.0), (0.0, 0.0, -2.0)):
        sec = [(0.0, t, s) for s, t in prof] if ev[0] else [(s, t, 0.0) for s, t in prof]
        part = MOD.extrude(sec, ev, "front", "slat", bevel_m=0.0)
        assert _volume(part) == pytest.approx(_area2d(prof) * math.dist((0.0, 0.0, 0.0), ev), rel=1e-6)
        assert P.part_bevel_radius(part) == 0.0                                   # no second bevel on its facets


def test_slats_are_real_products_by_family_and_not_one_for_every_style():
    specs = {fam: tuple(WF.joinery(WF.built_in_look({"family": fam}))["slat"]) for fam in WF.JOINERY}
    assert len(set(specs.values())) >= 5 and {s[0] for s in specs.values()} == {"h", "v"}
    for fam, (direction, sw, sg, sdp) in specs.items():
        assert 0.020 <= sw <= 0.040 and 0.010 <= sg <= 0.020 and 0.016 <= sdp <= 0.020, fam
        _plan, parts = _parts(fam=fam)
        slats = [p for p in parts if p["role"] == "slat"]
        assert slats and all(len(p["verts"]) >= 16 and p.get("bevel_m") == 0.0 for p in slats), fam
        boxes = [_bb(p) for p in slats]
        across = [(b[5] - b[2]) if direction == "h" else (b[3] - b[0]) for b in boxes]
        along = [(b[3] - b[0]) if direction == "h" else (b[5] - b[2]) for b in boxes]
        assert all(a == pytest.approx(sw, abs=1e-6) for a in across) and min(along) > 10 * sw, fam
        # the gaps between neighbours on one leaf: the family's gap at least, never a slat more
        lanes: dict = {}
        for b in boxes:
            lane = (round(b[1], 4), round(b[0], 2) if direction == "h" else round(b[2], 2))
            lanes.setdefault(lane, []).append(b)
        for bs in lanes.values():
            key = 2 if direction == "h" else 0
            bs.sort(key=lambda b: b[key])
            gaps = [b[key] - a[key + 3] for a, b in zip(bs, bs[1:])]
            gaps = [g for g in gaps if g < 0.1]                                    # (a leaf's own slats)
            assert gaps and min(gaps) >= sg - 1e-6 and max(gaps) <= sg + sw + sg, fam
    # the master of the run that showed it (modern): horizontal; the Japandi and Scandinavian homes: vertical
    assert specs["modern"][0] == "h" and specs["japandi"][0] == specs["scandinavian"][0] == "v"


def test_each_slat_has_its_tone_and_its_own_patch_of_veneer_with_the_grain_along_it():
    plan, parts = _parts()
    slats = [p for p in parts if p["role"] == "slat"]
    tones = [P.tone_of(p["key"]) for p in slats]
    assert {base for base, _n in tones} == {"front"} and len({n for _b, n in tones}) >= 4    # veneer leaves differ
    again = [p["key"] for p in MOD.module_parts(MOD.module_plan(_piece())) if p["role"] == "slat"]
    assert [p["key"] for p in slats] == again                                      # one run, always the same tones
    for _hue, sat, val in P.TONE_SHIFTS:
        assert 0.80 <= val <= 1.20 and 0.9 <= sat <= 1.1                          # leaves of one veneer, not a barcode
    assert max(v for _h, _s, v in P.TONE_SHIFTS) - min(v for _h, _s, v in P.TONE_SHIFTS) >= 0.2   # visible
    assert P.TONE_SHIFTS[0] == (0.0, 1.0, 1.0) and all(abs(h) <= 0.012 for h, _s, _v in P.TONE_SHIFTS)
    assert P.tone_key("front", 0) == "front" and P.tone_key("front", P.TONE_STEPS + 1) == "front_tone1"
    assert P.tone_key("steel", 3) == "steel" and P.tone_of("front_tone3") == ("front", 3)
    # the build's UVs (furniture.piece_uvs: geom2d.oriented_box_uv, part_uv_offset): every slat's face its own patch,
    # the grain (v) along the slat
    offsets, along = set(), []
    for p in slats[:12]:
        for f in p["faces"]:
            pts = [p["verts"][i] for i in f]
            lo = [min(v[k] for v in pts) for k in range(3)]
            hi = [max(v[k] for v in pts) for k in range(3)]
            if hi[1] - lo[1] < 1e-9 and pts[0][1] == min(v[1] for v in p["verts"]):     # its front face (-Y)
                offsets.add(GE.part_uv_offset((0.0, -1.0, 0.0), lo, hi))
                ext = [hi[k] - lo[k] for k in range(3)]
                u0 = GE.oriented_box_uv(lo, (0.0, -1.0, 0.0), ext)
                u1 = GE.oriented_box_uv((hi[0], lo[1], lo[2]), (0.0, -1.0, 0.0), ext)
                along.append(abs(u1[1] - u0[1]) == pytest.approx(ext[0]))
    assert len(offsets) == 12 and all(along)


def test_a_backing_behind_the_gaps_by_family():
    for fam, backing in (("modern", "glass"), ("minimal", "glass"), ("japandi", "scrim"), ("industrial", "scrim")):
        plan, parts = _parts(fam=fam)
        assert MOD.joinery_of(plan)["backing"] == backing
        slats = [p for p in parts if p["role"] == "slat"]
        backs = [p for p in parts if p["role"] == "backing"]
        assert backs and all(p["key"] == "backing" for p in backs), fam
        # behind the slats of its leaf, within the frame's depth
        for b in backs:
            bb = _bb(b)
            mine = [s for s in slats if _bb(s)[0] >= bb[0] - 0.01 and _bb(s)[3] <= bb[3] + 0.01
                    and abs(_bb(s)[1] - bb[1]) < K["panel_t"]]
            assert mine and max(_bb(s)[4] for s in mine) < bb[1], fam
    over = WF.look_overrides(_piece(fam="japandi"))
    assert over["backing"] == {"slug": WF.BACKING_SLUG, "asset": None, "colour": "ivory"}
    assert WF.look_overrides(_piece(fam="industrial"))["backing"]["colour"] == "charcoal"     # a dark mesh
    # a lightly tinted pane in the tone of the look's glass (about 80 % through: the contents read between the slats)
    glass = {"slug": "glass", "asset": None, "colour": None, "tone": "bronze"}
    assert WF.look_overrides(_piece(fam="modern"))["backing"] == glass
    assert WF.look_overrides(_piece(fam="minimal"))["backing"]["tone"] == "grey"
    from wenart.blender import materials as M
    for tone in ("clear_grey", "clear_bronze"):
        assert sum(M.TINTED_GLASS[tone]) / 3.0 >= 0.75 > sum(M.TINTED_GLASS["grey"]) / 3.0
    assert WF.BACKING_SLUG == F.SHEER_SLUG and "backing" in P.MATERIAL_KEYS


# ------------------------------------------------------------------------------------------- (2) the doors

def test_the_doors_show_shadow_lines_with_brush_seals_a_bottom_track_and_a_scribe_to_the_ceiling():
    plan, parts = _parts()
    n = plan["see_through"]["panels"]
    assert n == 4                                                                  # 3.11 m: four leaves
    seals = [p for p in parts if p["role"] == "brush_seal"]
    assert len(seals) == n - 1 and all(p["key"] == "dark" for p in seals)
    bw, _bd = K["brush_m"]
    assert all(_bb(p)[3] - _bb(p)[0] == pytest.approx(bw) for p in seals)       # a 4 mm shadow line
    frames = [p for p in parts if p["role"] == "panel_frame"]
    front_y = min(_bb(p)[1] for p in frames)
    for s in seals:                                                                # between the two tracks
        assert front_y + K["panel_t"] < _bb(s)[1] and _bb(s)[4] < front_y + 2 * K["panel_t"] + K["track_gap_m"]
    track = [p for p in parts if p["role"] == "bottom_track"]
    assert len(track) == 1 and track[0]["key"] == "handle"
    assert _bb(track[0])[5] == pytest.approx(MOD.WARDROBE_PLINTH_M, abs=0.001)    # on the plinth line, under the doors
    assert [p for p in parts if p["role"] == "track"]                              # the top track behind the fascia
    scribe = [p for p in parts if p["role"] == "scribe"]
    fascias = [p for p in parts if p["role"] == "fascia"]
    assert len(scribe) == 1 and scribe[0]["key"] == "dark" and len(fascias) == 2
    assert max(_bb(p)[5] for p in fascias) == pytest.approx(plan["height_m"])     # the fillet to the ceiling
    assert _bb(scribe[0])[1] > min(_bb(p)[1] for p in fascias) + 0.002             # its groove set back
    plinth = next(p for p in parts if p["role"] == "plinth")
    assert plinth["key"] == "dark" and _bb(plinth)[1] > _bb(track[0])[4]          # recessed behind the doors


@pytest.mark.parametrize("fam, handle", [("modern", "bar"), ("japandi", "leather"), ("minimal", "recessed"),
                                         ("modern minimal", "grip")])
def test_the_pulls_by_family_on_every_leaf_edge_a_hand_reaches(fam, handle):
    plan, parts = _parts(fam=fam)
    assert MOD.joinery_of(plan)["handle"] == handle
    n = plan["see_through"]["panels"]
    fronts = (n + 1) // 2
    grips = [p for p in parts if p["role"] == "grip"]
    if handle == "bar":
        bars = [p for p in parts if p["role"] == "pull"]
        posts = [p for p in parts if p["role"] == "pull_post"]
        assert len(bars) == fronts and len(posts) == 2 * fronts and all(p["key"] == "handle" for p in bars + posts)
        assert all(_bb(p)[5] - _bb(p)[2] >= 0.6 for p in bars)                   # long bar pulls
    if handle == "leather":
        tabs = [p for p in parts if p["role"] == "tab"]
        plates = [p for p in parts if p["role"] == "tab_plate"]
        assert len(plates) == fronts and tabs and all(p["key"] == "leather" for p in tabs)
        assert all(p["key"] == "handle" for p in plates)
    if handle in ("bar", "leather", "recessed"):
        # the rear leaf at the run's end a short flush pull (it slides behind the front leaves)
        assert len(grips) == (fronts if handle == "recessed" else 0) + (1 if n % 2 == 0 else 0)
        assert all(_bb(p)[5] - _bb(p)[2] <= K["recess_len_m"] for p in grips)
    else:
        assert len(grips) == fronts + (1 if n % 2 == 0 else 0)
        assert max(_bb(p)[5] - _bb(p)[2] for p in grips) >= 1.0                   # the integrated long channel
    # every pull inside the drawn footprint (the doors stand back by the pulls' stand-off)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert y0 >= -0.3 - 1e-6 and y1 <= 0.3 + 1e-6 and x0 >= -3.11 / 2 - 1e-6 and x1 <= 3.11 / 2 + 1e-6
    assert MOD.door_zone(plan) == pytest.approx(K["door_zone_m"] + MOD.handle_proud(MOD.joinery_of(plan)))


def test_a_slatted_leaf_has_a_solid_top_band_and_a_glass_leaf_keeps_its_glass():
    plan, parts = _parts(kind="slats_glass", glass="smoked_glass")
    assert plan.get("carcass_m") is not None                                      # a top box over the frames
    tops = [p for p in parts if p["role"] == "top_panel"]
    slatted = [i for i in range(plan["see_through"]["panels"]) if MOD.panel_kind(plan["see_through"], i) == "slats"]
    assert len(tops) == len(slatted) and all(p["key"] == "front" for p in tops)
    assert all(_bb(p)[2] >= plan["carcass_m"] - 0.05 for p in tops)               # over the top box's floor
    glass = [p for p in parts if p["role"] == "glass"]
    assert any(_bb(p)[2] >= plan["carcass_m"] - 0.05 for p in glass)              # the glass leaves' top band
    assert not [p for p in parts if p["role"] == "slat" and _bb(p)[2] >= plan["carcass_m"]]


# ------------------------------------------------------------------------------------------- (3) the inside

def test_the_inside_is_its_own_finish_with_banded_shelves_a_rail_on_brackets_and_an_led_profile():
    plan, parts = _parts()
    carcass = [p for p in parts if p["role"] in ("body", "shelf")]
    assert carcass and all(p["key"] == "interior" for p in carcass)
    shelves = [p for p in parts if p["role"] == "shelf"]
    bands = [p for p in parts if p["role"] == "band"]
    assert len(bands) == len(shelves) and all(p["key"] == "wood" for p in bands)
    for s in shelves:                                                              # each band before its shelf
        assert any(abs(_bb(b)[2] - _bb(s)[2]) < 1e-6 and _bb(b)[4] < _bb(s)[1] for b in bands)
    rails = [p for p in parts if p["role"] == "rail"]
    assert rails and all((_bb(p)[5] - _bb(p)[2]) > 1.5 * (_bb(p)[4] - _bb(p)[1]) for p in rails)   # oval, upright
    assert len([p for p in parts if p["role"] == "rail_bracket"]) == 2 * len(rails)
    leds = [p for p in parts if p["role"] == "led"]
    profiles = [p for p in parts if p["role"] == "led_profile"]
    assert len(leds) == len(profiles) and all(p["key"] == "steel" for p in profiles)
    for led in leds:                                                               # the diffuser under its profile
        assert any(_bb(led)[5] < _bb(pr)[2] and _bb(pr)[2] - _bb(led)[5] < 0.001 for pr in profiles)
    roles = {p["role"] for p in parts}
    assert {"garment", "sleeve", "collar", "hanger", "folded", "drawer", "box"} <= roles
    narrow = {p["role"] for p in MOD.module_parts(MOD.module_plan(_piece(width=2.27)))}
    assert {"shoe", "shelf", "band", "garment"} <= narrow                         # a shelf bay: its shoe shelf
    # the hangers stay wood; the inside differs from the fronts in every family
    assert all(p["key"] in ("wood", "steel") for p in parts if p["role"] == "hanger")
    for fam in WF.JOINERY:
        over = WF.look_overrides(_piece(fam=fam))
        assert over["interior"]["slug"] != over["front"]["slug"], fam
    over = WF.look_overrides(_piece(fam="modern"))
    assert over["interior"] == {"slug": WF.INTERIOR_SLUG, "asset": "rough_linen", "colour": "greige"}
    e = V.FURNITURE_MATERIALS[WF.INTERIOR_SLUG]
    assert e["kind"] == "hard" and e["albedo_mode"] == "flat" and e["colourable"] and e["detail"] <= 0.2
    keys, _a = F.style_material_keys({})
    assert keys["interior"][0] == WF.INTERIOR_SLUG and keys["backing"][0] in V.FLAT_COLOURS
    assert all(keys[k] == keys[base] for k, (base, _n) in P.TONE_KEYS.items())
    # the style's own veneer on the shell: the inside never takes it (a light linen melamine instead)
    look = WF.built_in_look({"family": "contemporary", "furniture": {"wood": "wood_veneer_oak_light"}})
    assert look["interior"] == WF.INTERIOR_SLUG and look["interior_colour"] in C.COLOURS


def test_the_led_has_a_soft_tilted_beam():
    plan = MOD.module_plan(_piece())
    lights = MOD.bay_lights(plan)
    assert lights
    for li in lights:
        dx, dy, dz = li["direction"]
        assert math.isclose(math.hypot(dx, dy, dz), 1.0, abs_tol=1e-3) and dz < -0.9 and dy > 0.1   # down, to the back
        assert li["spread_deg"] == WC.LED_SPREAD_DEG < 180.0 and li["tilt_deg"] == WC.LED_TILT_DEG
        assert li["size_m"][1] <= 0.02 and "opal diffuser" in li["source"]
        assert li["center"][1] > -0.3 + MOD.door_zone(plan)                       # inside, behind the doors


# ------------------------------------------------------------------------------------------- (4) the rules stay

def test_the_joinery_is_checked_and_recorded_and_old_records_still_build():
    j = WF.joinery({"family": "modern", "slat": ["h", 0.08, 0.002, 0.05], "handle": "knob", "backing": "paper",
                    "interior": "wood_veneer_oak", "shell_slug": "wood_veneer_oak"})
    assert j["slat"] == ("h", 0.040, 0.010, 0.020) and j["handle"] == "grip" and j["backing"] == "glass"
    assert j["interior"] == WF.INTERIOR_SLUG                                       # never the shell's own slug
    plan = MOD.module_plan(_piece())
    rec = plan["see_through"]["joinery"]
    assert rec["slat"] == list(WF.JOINERY["modern"]["slat"]) and rec["handle"] == "bar"
    assert any("joinery:" in n and "UL246" in n for n in plan["notes"])
    assert "rounded slats" in plan["see_through"]["look"]["why"]
    # a piece recorded before (no look): the default family's joinery, every key a known one
    old = {"id": "f_old", "type": "wardrobe", "height": None, "see_through": {"kind": "slats"},
           "footprint": {"center": [0, 0], "size": [2.27, 0.6], "rotation_deg": 0.0}}
    parts = MOD.module_parts(MOD.module_plan(old))
    keys = {P.plain_key(p["key"]) for p in parts}
    assert keys <= set(P.MATERIAL_KEYS) and any(p["role"] == "slat" for p in parts)
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert y0 >= -0.3 - 1e-6 and y1 <= 0.3 + 1e-6 and x0 >= -2.27 / 2 - 1e-6 and x1 <= 2.27 / 2 + 1e-6
    # UL223 stays: at most two rooms, a built-in starts at a wall
    assert WF.BUILT_IN_ROOMS_MAX == 2 and WF.END_TOUCH_M == 0.05 and WF.EXTEND_MAX_M == 0.50


def test_the_run_stays_in_its_footprint_and_under_the_ceiling_with_a_reasonable_vertex_count():
    for fam in WF.JOINERY:
        for kind in ("slats", "slats_glass", "smoked_glass", "reeded_glass"):
            plan, parts = _parts(fam=fam, kind=kind, glass="smoked_glass" if kind == "slats_glass" else None)
            x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
            assert x0 >= -3.11 / 2 - 1e-6 and x1 <= 3.11 / 2 + 1e-6 and y0 >= -0.3 - 1e-6 and y1 <= 0.3 + 1e-6
            assert z0 >= -1e-9 and z1 <= plan["height_m"] + 1e-6 <= 2.995 + 1e-6
            assert {P.plain_key(p["key"]) for p in parts} <= set(P.MATERIAL_KEYS)
            verts = sum(len(p["verts"]) for p in parts)
            assert verts < 14000, (fam, kind, verts)                               # 3.11 m run: about 6-11 k
