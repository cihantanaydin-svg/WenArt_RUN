"""Milestone 13 track T2 (docs/milestone13.md §13.1-13.2): module builders and the parametric families v2, pure.

Module plans (``wenart.blender.modules.module_plan``): real module sizes, the footprint kept within the cap, a
wardrobe run of 2.75 m from PAX frames, chairs split from a table footprint that includes them, an L sofa plan
for a 3.2 x 2.2 m footprint, a kitchen run with its sink under the window position passed in, the bath set; the
parts of every plan fill the plan's box with several material slots. Families v2 (``parametric.FAMILY_TYPES``):
real parts (legs, aprons, rails, cushions, drawer fronts) with at least two material slots, the Milestone 4 boxes
kept, the bed's textile bedding inside the footprint. The Blender side (material slots, bevel modifier, built
boxes) is tests/gpu/test_m13_modules.py.
"""
from __future__ import annotations

import math

import pytest

from wenart.blender import furniture as F
from wenart.blender import geom2d
from wenart.blender import modules as M
from wenart.blender import parametric as P
from wenart.blender import textiles as T
from wenart.blender.proxies import proxy_height
from wenart.furniture import schemas as SC

from test_blender_parametric_basins import assert_open_bowls, surface_under


def _piece(ftype, w, d, center=(0.0, 0.0), rot=0.0, **extra):
    piece = {"id": f"f_{ftype}", "type": ftype, "level_id": "L0", "room_id": "r", "source": "from_documents",
             "status": "verified", "footprint": {"center": list(center), "size": [w, d], "rotation_deg": rot},
             "front_deg": (270.0 + rot) % 360.0}
    piece.update(extra)
    return piece


def _bbox(parts):
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    return (x1 - x0, y1 - y0, z0, z1)


def _no_degenerate_faces(parts):
    for p in parts:
        for f in p["faces"]:
            assert geom2d.face_normal(p["verts"], f) != (0.0, 0.0, 0.0), p["role"]


# --------------------------------------------------------------------------
# Module plans
# --------------------------------------------------------------------------

def test_module_builders_and_the_plan_record():
    assert M.MODULE_BUILDERS == {"wardrobe": "wardrobe_run", "table_dining": "table_long", "sofa_corner": "sofa_l",
                                 "kitchen_counter": "kitchen_run", "kitchen_island": "kitchen_run",
                                 "washbasin": "bath_set", "shower": "bath_set",
                                 "wall_cabinet": "wall_run"}        # 28 Oct 2026: wall units on the base joints
    assert M.module_plan(_piece("chair", 0.45, 0.45)) is None                 # no builder for the type
    assert M.module_plan({"id": "x", "type": "wardrobe"}) is None             # no footprint
    assert M.module_plan(_piece("wardrobe", 0.0, 0.6)) is None                # no size
    plans = [M.module_plan(_piece("wardrobe", 2.75, 0.6)), M.module_plan(_piece("table_dining", 3.35, 1.0)),
             M.module_plan(_piece("sofa_corner", 3.2, 2.2, shape="L", chaise_side="right")),
             M.module_plan(_piece("kitchen_counter", 3.0, 0.6)), M.module_plan(_piece("washbasin", 1.0, 0.55)),
             M.module_plan(_piece("shower", 0.9, 0.9))]
    for plan in plans:
        assert plan is not None
        assert {"builder", "modules", "footprint_m", "height_m", "products"} <= set(plan)       # §13.2
        assert plan["method"] == "module" and plan["fit"]["within_cap"] and plan["products"]
        assert len(plan["footprint_m"]) == 2 and plan["height_m"] > 0
        for m in plan["modules"]:
            assert {"kind", "size_m", "pos_m", "rot_deg", "material"} <= set(m)
            assert len(m["size_m"]) == 3 and all(v > 0 for v in m["size_m"]) and len(m["pos_m"]) == 2
            assert m["material"] in P.MATERIAL_KEYS
        # the parts fill the plan's box (handles may stand 8 mm proud) with several material slots, on the floor
        parts = M.module_parts(plan)
        w, d, z0, z1 = _bbox(parts)
        assert abs(w - plan["footprint_m"][0]) <= 0.01 and abs(d - plan["footprint_m"][1]) <= 0.01, plan["builder"]
        assert abs(z0) < 1e-9 and z1 >= plan["height_m"] - 0.02
        assert len(M.material_keys(plan)) >= 2, plan["builder"]
        assert {p["key"] for p in parts} <= set(P.MATERIAL_KEYS)
        _no_degenerate_faces(parts)
        assert M.plan_bbox(plan) == pytest.approx((w, d, z1 - z0))
        assert any(P.part_bevel_radius(p) > 0 for p in parts)


def test_compose_run_uses_real_widths_with_small_fillers():
    assert M.compose_run(2.75, M.WARDROBE_FRAME_WIDTHS_M, M.WARDROBE_FILLER_MAX_M) == {
        "widths": [1.0, 1.0, 0.75], "filler_m": 0.0, "sum_m": 2.75}
    run = M.compose_run(3.11, M.WARDROBE_FRAME_WIDTHS_M, M.WARDROBE_FILLER_MAX_M)
    assert run["widths"] == [1.0, 1.0, 1.0] and run["filler_m"] == pytest.approx(0.055)
    assert M.compose_run(0.4, M.WARDROBE_FRAME_WIDTHS_M, M.WARDROBE_FILLER_MAX_M) is None    # below one frame
    assert M.compose_run(1.0, (0.3,), 0.05) == {"widths": [0.3, 0.3, 0.3], "filler_m": 0.05, "sum_m": 0.9}
    assert M.compose_run(1.0, (0.3,), 0.04) is None                                           # 0.05 filler each end
    kitchen = M.compose_run(2.13, M.KITCHEN_BASE_WIDTHS_M, M.KITCHEN_FILLER_MAX_M)
    assert sum(kitchen["widths"]) + 2 * kitchen["filler_m"] == pytest.approx(2.13)
    assert all(wd in M.KITCHEN_BASE_WIDTHS_M for wd in kitchen["widths"])


def test_wardrobe_run_of_2_75_m_is_real_pax_frames():
    plan = M.module_plan(_piece("wardrobe", 2.75, 0.6))
    frames = [m for m in plan["modules"] if m["kind"] == "frame"]
    widths = sorted(m["size_m"][0] for m in frames)
    assert widths == [0.75, 1.0, 1.0] and sum(widths) == pytest.approx(2.75)
    assert all(wd in M.WARDROBE_FRAME_WIDTHS_M for wd in widths)
    assert not [m for m in plan["modules"] if m["kind"] == "filler"]
    assert plan["footprint_m"] == [2.75, 0.6] and plan["drawn_m"] == [2.75, 0.6]
    assert plan["height_m"] == pytest.approx(2.01 + M.WARDROBE_PLINTH_M)         # the PAX height nearest 2.10
    assert all("PAX" in p for p in plan["products"])
    assert {m["kind"] for m in plan["modules"]} == {"plinth", "frame", "top"}
    # doors: a 100 frame takes two 50 doors, a 75 frame one; a vertical handle per door
    doors = sum(int(m["doors"]) for m in frames)
    assert doors == 5
    parts = M.module_parts(plan)
    handles = [p for p in parts if p["role"] == "handle"]
    assert len(handles) == doors and all(p["key"] == "handle" for p in handles)
    for p in handles:
        zs = [v[2] for v in p["verts"]]
        assert max(zs) - min(zs) > max(v[0] for v in p["verts"]) - min(v[0] for v in p["verts"])   # vertical
    assert {p["key"] for p in parts} >= {"dark", "wood", "front", "handle"}
    # 3.11 and 2.57 m runs (real04): fillers at both ends, never wider than the filler cap
    for w, d in ((3.11, 0.6), (2.57, 0.74)):
        plan = M.module_plan(_piece("wardrobe", w, d))
        fillers = [m for m in plan["modules"] if m["kind"] == "filler"]
        assert len(fillers) == 2 and all(m["size_m"][0] <= M.WARDROBE_FILLER_MAX_M for m in fillers)
        assert plan["footprint_m"] == [w, d] and M.plan_bbox(plan)[0] == pytest.approx(w)
    # a drawn height is kept; a shaker design gives shaker doors
    tall = M.module_plan(_piece("wardrobe", 2.0, 0.6, height=2.5))
    assert tall["height_m"] == pytest.approx(2.5) and M.plan_bbox(tall)[2] == pytest.approx(2.5)
    shaker = M.module_plan(_piece("wardrobe", 2.0, 0.6, design={"front_style": "shaker"}))
    assert sum(p["role"] == "front" for p in M.module_parts(shaker)) == 5 * 4
    assert M.module_plan(_piece("wardrobe", 0.4, 0.6)) is None                    # narrower than a frame
    assert M.module_plan(_piece("wardrobe", 2.0, 0.3)) is None                    # not a wardrobe depth


def test_long_table_splits_the_chairs_from_a_deep_footprint():
    # a real 10-seat table (real02/real04 masa 3.35 x 1.00): no split, trestles, wood top on steel feet
    table = M.module_plan(_piece("table_dining", 3.35, 1.0))
    assert table["split"] is None and table["seats"] == 0
    assert {m["kind"] for m in table["modules"]} == {"top", "trestle"}
    assert set(M.material_keys(table)) == {"wood", "steel"}
    top = next(m for m in table["modules"] if m["kind"] == "top")
    assert top["size_m"] == [3.35, 1.0, M.TABLE_TOP_M] and top["z_m"] == pytest.approx(0.75 - M.TABLE_TOP_M)
    # a 2.3 x 1.6 m footprint is deeper than any real table: the table and three chairs per side
    both = M.module_plan(_piece("table_dining", 2.3, 1.6))
    assert both["split"]["table_m"][1] == pytest.approx(0.8) and both["split"]["chairs"] == 6
    assert "includes the chairs" in both["split"]["reason"]
    chairs = [m for m in both["modules"] if m["kind"] == "chair"]
    assert len(chairs) == 6 and all(m["size_m"][:2] == list(M.CHAIR_SIZE_M) for m in chairs)
    front = [m for m in chairs if m["pos_m"][1] < 0]
    back = [m for m in chairs if m["pos_m"][1] > 0]
    assert len(front) == len(back) == 3
    assert all(m["rot_deg"] == 180.0 for m in front) and all(m["rot_deg"] == 0.0 for m in back)  # facing the table
    assert both["footprint_m"] == [2.3, 1.6] and both["fit"]["within_cap"]
    w, d, z0, z1 = _bbox(M.module_parts(both))
    assert (w, d) == pytest.approx((2.3, 1.6), abs=0.01) and z0 == 0.0
    # the chairs' seats slide under the table edge: a chair box reaches past the table's long edge
    assert min(m["pos_m"][1] - M.CHAIR_SIZE_M[1] / 2.0 for m in back) < both["split"]["table_m"][1] / 2.0
    # a normal table on four legs; a footprint too small for a table: no plan
    legs = M.module_plan(_piece("table_dining", 1.6, 0.9))
    assert [m["kind"] for m in legs["modules"]].count("leg") == 4 and legs["split"] is None
    assert M.module_plan(_piece("table_dining", 0.7, 0.5)) is None


def test_sofa_l_plan_for_a_3_2_by_2_2_footprint():
    for side in ("left", "right"):
        plan = M.module_plan(_piece("sofa_corner", 3.2, 2.2, shape="L", chaise_side=side))
        assert plan["builder"] == "sofa_l" and plan["chaise_side"] == side and not plan["chaise_side_assumed"]
        seats = [m for m in plan["modules"] if m["kind"] == "seat_module"]
        chaise = next(m for m in plan["modules"] if m["kind"] == "chaise_module")
        arm = next(m for m in plan["modules"] if m["kind"] == "arm")
        assert len(seats) == 2
        for m in seats:
            assert M.SOFA_MODULE_RANGE_M[0] - 1e-9 <= m["size_m"][0] <= M.SOFA_MODULE_RANGE_M[1] + 1e-9
        assert M.SOFA_CHAISE_DEPTH_RANGE_M[0] - 1e-9 <= chaise["size_m"][1] <= M.SOFA_CHAISE_DEPTH_RANGE_M[1] + 1e-9
        assert chaise["size_m"][0] in M.SOFA_CHAISE_WIDTHS_M and arm["size_m"][0] in M.SOFA_ARM_WIDTHS_M
        # the chaise on its side, the arm at the other end; the modules fill the width exactly
        assert (chaise["pos_m"][0] < 0) == (side == "left") and (arm["pos_m"][0] > 0) == (side == "left")
        assert arm["size_m"][0] + sum(m["size_m"][0] for m in seats) + chaise["size_m"][0] == pytest.approx(3.2)
        # the footprint: the width kept, the depth = the deepest chaise module + the back, within the 10 % cap
        assert plan["footprint_m"][0] == 3.2 and plan["footprint_m"][1] == pytest.approx(1.8 + M.SOFA_BACK_M)
        assert plan["fit"]["within_cap"] and plan["fit"]["rel"] <= M.MODULE_FIT_TOL
        assert plan["rectangles"] == [[round(v, 4) for v in r]
                                      for r in P.l_parts((3.2, plan["footprint_m"][1]), side, plan["footprint_m"][1],
                                                         P.L_SEAT_DEPTH_M, chaise["size_m"][0])]
        parts = M.module_parts(plan)
        w, d, z0, z1 = _bbox(parts)
        assert (w, d) == pytest.approx((3.2, plan["footprint_m"][1]), abs=0.01) and z0 == 0.0
        assert z1 >= 0.85 - 0.02 and {p["key"] for p in parts} == {"fabric", "wood"}
        roles = {p["role"] for p in parts}
        assert {"back", "arm", "body", "leg", "cushion", "back_cushion"} <= roles
        assert sum(p["role"] == "cushion" for p in parts) == 3                   # two seats and the chaise
    # the real04 corner sofa 4.38 x 1.97 is kept exactly; a 1.5 m deep L cannot hold a 1.6 m chaise: no plan
    real = M.module_plan(_piece("sofa_corner", 4.38, 1.97))
    assert real["footprint_m"] == [4.38, 1.97] and real["chaise_side_assumed"]
    assert len([m for m in real["modules"] if m["kind"] == "seat_module"]) == 3
    assert M.module_plan(_piece("sofa_corner", 3.0, 1.5)) is None
    assert M.module_plan(_piece("sofa", 2.2, 0.9)) is None                        # a straight sofa: the family
    drawn_l = M.module_plan(_piece("sofa", 3.2, 2.2, shape="L", chaise_side="left"))   # a sofa drawn as an L
    assert drawn_l["builder"] == "sofa_l" and drawn_l["chaise_side"] == "left" and drawn_l["type"] == "sofa"


def test_kitchen_run_puts_the_sink_under_the_window_passed_in():
    # a 3.0 m run along a wall, rotated 90 degrees; the window centre in world coordinates
    piece = _piece("kitchen_counter", 3.0, 0.6, center=(4.0, 2.0), rot=90.0,
                   module_hints={"window_pos_m": [4.3, 3.0]})
    plan = M.module_plan(piece)
    assert plan["cutouts"] == ["sink"]
    worktop = next(m for m in plan["modules"] if m["kind"] == "worktop")
    (sink,) = worktop["cutouts"]
    assert sink["kind"] == "sink" and sink["x_m"] == pytest.approx(1.0) and sink["w_m"] in M.KITCHEN_SINK_UNIT_WIDTHS_M
    sink_unit = next(m for m in plan["modules"] if m.get("holds") == "sink")
    assert abs(sink_unit["pos_m"][0] - 1.0) <= 0.01
    units = [m for m in plan["modules"] if m["kind"] == "base_unit"]
    assert all(m["size_m"][0] in M.KITCHEN_BASE_WIDTHS_M for m in units)
    assert all(m["size_m"][1] == 0.6 for m in units) and all("base unit" in m["product"] for m in units)
    fillers = [m for m in plan["modules"] if m["kind"] == "filler"]
    assert sum(m["size_m"][0] for m in units + fillers) == pytest.approx(3.0)
    # the slit between the sink unit and the wall is a filler panel narrower than the smallest unit
    assert all(m["size_m"][0] < min(M.KITCHEN_BASE_WIDTHS_M) for m in fillers)
    # a sink unit within 10 cm of the wall moves to the wall instead of leaving a slit
    against = M.module_plan(_piece("kitchen_counter", 3.0, 0.6, module_hints={"sink_x_m": 1.25}))
    sink_at_wall = next(m for m in against["modules"] if m.get("holds") == "sink")
    assert sink_at_wall["pos_m"][0] + sink_at_wall["size_m"][0] / 2.0 == pytest.approx(1.5)
    assert not [m for m in against["modules"] if m["kind"] == "filler" and m["pos_m"][0] > 1.0]
    assert worktop["size_m"] == [3.0, 0.6, M.KITCHEN_WORKTOP_M]
    assert worktop["z_m"] + M.KITCHEN_WORKTOP_M == pytest.approx(M.KITCHEN_WORKTOP_HEIGHT_M)
    parts = M.module_parts(plan)
    roles = {p["role"] for p in parts}
    assert {"plinth", "body", "front", "handle", "top", "basin", "tap"} <= roles and "hob" not in roles
    basin = [p for p in parts if p["role"] == "basin"]
    assert all(p["key"] == "steel" for p in basin)
    bx = [v[0] for p in basin for v in p["verts"]]
    assert abs((min(bx) + max(bx)) / 2.0 - 1.0) < 0.02                           # the bowl under the window
    w, d, z0, z1 = _bbox(parts)
    assert (w, d, z0) == pytest.approx((3.0, 0.6, 0.0), abs=0.01)
    assert 0.9 < z1 <= 0.9 + 0.30 + 1e-9                                            # the tap over the worktop
    assert {p["key"] for p in parts} >= {"dark", "front", "painted", "handle", "worktop", "steel"}
    assert plan["height_m"] == pytest.approx(0.9) and not [m for m in plan["modules"] if m["kind"] == "wall_unit"]
    # the hob at a local x; wall units only when asked, from 1.40 to 2.10 m, 0.35 deep at the back
    plan2 = M.module_plan(_piece("kitchen_counter", 3.0, 0.6,
                                 module_hints={"sink_x_m": 0.6, "hob_x_m": -0.9, "wall_units": True}))
    assert plan2["cutouts"] == ["hob", "sink"]
    assert "hob" in {p["role"] for p in M.module_parts(plan2)}
    walls = [m for m in plan2["modules"] if m["kind"] == "wall_unit"]
    assert walls and all(m["z_m"] == M.KITCHEN_WALL_BOTTOM_M and m["size_m"][1] == M.KITCHEN_WALL_DEPTH_M for m in walls)
    assert all(m["z_m"] + m["size_m"][2] == pytest.approx(M.KITCHEN_WALL_TOP_M) for m in walls)
    assert all(m["size_m"][0] in M.KITCHEN_WALL_WIDTHS_M for m in walls)
    # 28 Oct 2026: the hob's cooker hood rises to the ceiling (the 2.40 m default without the fit's hood_top_m); the
    # plan's height stays the wall units' top
    assert plan2["height_m"] == pytest.approx(M.KITCHEN_WALL_TOP_M)
    assert M.plan_bbox(plan2)[2] == pytest.approx(M.HOOD_TOP_DEFAULT_M) and plan2["hood"]["kind"] == "chimney"
    # no hint: no cutout (the drawn sink and stove are their own pieces), and the plan says so
    plain = M.module_plan(_piece("kitchen_counter", 2.4, 0.6))
    assert plain["cutouts"] == [] and any("no sink or hob cutout" in n for n in plain["notes"])
    assert "basin" not in {p["role"] for p in M.module_parts(plain)}
    # an island: fronts on the front, a panel on the back, the plinth recessed all round
    island = M.module_plan(_piece("kitchen_island", 2.13, 0.9))
    assert island["island"] and "panel" in {p["role"] for p in M.module_parts(island)}
    plinth = next(m for m in island["modules"] if m["kind"] == "plinth")
    assert plinth["size_m"][0] == pytest.approx(2.13 - 2 * M.KITCHEN_PLINTH_RECESS_M)
    assert _bbox(M.module_parts(island))[:2] == pytest.approx((2.13, 0.9), abs=0.01)


def test_bath_set_vanity_with_mirror_and_shower_tray():
    vanity = M.module_plan(_piece("washbasin", 1.0, 0.55))
    assert vanity["builder"] == "bath_set" and vanity["basins"] == 1
    assert [m["kind"] for m in vanity["modules"]] == ["vanity", "top", "basin", "mirror"]
    mirror = next(m for m in vanity["modules"] if m["kind"] == "mirror")
    assert mirror["z_m"] >= M.VANITY_MIRROR_BOTTOM_MIN_M and mirror["material"] == "mirror"
    assert vanity["height_m"] == pytest.approx(mirror["z_m"] + M.VANITY_MIRROR_H_M)
    parts = M.module_parts(vanity)
    roles = {p["role"] for p in parts}
    assert {"body", "front", "handle", "top", "basin", "tap", "frame", "glass"} <= roles
    assert {p["key"] for p in parts} >= {"wood", "front", "handle", "ceramic", "steel", "mirror"}
    w, d, z0, z1 = _bbox(parts)
    assert (w, d) == pytest.approx((1.0, 0.55), abs=0.01) and z0 == 0.0 and z1 == pytest.approx(vanity["height_m"])
    cab = next(m for m in vanity["modules"] if m["kind"] == "vanity")
    assert cab["z_m"] == M.VANITY_BOTTOM_M and cab["drawers"] == 2                 # wall-hung, two drawers
    double = M.module_plan(_piece("washbasin", 1.2, 0.55))
    assert double["basins"] == 2 and sum(m["kind"] == "basin" for m in double["modules"]) == 2
    assert M.module_plan(_piece("washbasin", 0.6, 0.4)) is None                   # a shallow basin: the pedestal family
    shower = M.module_plan(_piece("shower", 1.2, 0.8))
    assert shower["footprint_m"] == [1.2, 0.8] and shower["modules"][0]["product"] == "shower tray 120x80 cm"
    assert {p["key"] for p in M.module_parts(shower)} == {"ceramic", "steel", "glass"}
    assert M.module_plan(_piece("shower", 1.0, 1.0))["footprint_m"] == [0.9, 0.9]  # the nearest product, within cap
    assert M.module_plan(_piece("toilet", 0.4, 0.7)) is None                      # the toilet stays with the family


def test_piece_bbox_and_the_furniture_dispatch_read_the_module_plan():
    piece = _piece("wardrobe", 3.11, 0.6)
    plan = M.module_plan(piece)
    with_plan = dict(piece, asset={"method": "module", "module_plan": plan})
    w, d, h, source = P.piece_bbox(with_plan)
    assert source == "module" and (w, d, h) == pytest.approx(M.plan_bbox(plan))
    assert P.obstacle_rect(with_plan)["size"] == pytest.approx([3.11, 0.608], abs=1e-6)
    # a module asset without a stored plan: the family's box; a broken plan: the family's box too
    assert P.piece_bbox(dict(piece, asset={"method": "module"}))[3] == "parametric"
    assert P.piece_bbox(dict(piece, asset={"method": "module", "module_plan": {"builder": "nope"}}))[3] == "parametric"
    # furniture.module_plan_of: the fit's plan first, else the plan of the piece, else the reason
    got, why = F.module_plan_of(with_plan)
    assert got is plan and why == "the fit's module plan"
    got, why = F.module_plan_of(dict(piece, asset={"method": "module"}))
    assert got["builder"] == "wardrobe_run" and "stored none" in why
    got, why = F.module_plan_of(dict(_piece("chair", 0.45, 0.45), asset={"method": "module"}))
    assert got is None and "no module builder fits a chair" in why
    # a module asset is neither refused nor a library file
    assert F.refused_piece(with_plan) is None and F.resolve_asset(with_plan["asset"], None)[0] is None


def test_gap_list_names_every_type_without_a_module_builder_or_a_family():
    gaps = M.gap_types()
    assert not set(gaps) & set(M.MODULE_BUILDERS) and not set(gaps) & set(P.FAMILY_TYPES)
    assert set(gaps) | set(M.MODULE_BUILDERS) | set(P.FAMILY_TYPES) == set(P.PARAMETRIC_TYPES)
    assert gaps == ["bar_stool", "bathtub", "bench", "bunk_bed", "chaise", "console_table", "crib",
                    "display_cabinet", "floor_lamp", "fridge", "office_chair", "ottoman", "potted_plant",
                    "shoe_cabinet", "side_table", "sideboard", "sink_kitchen", "stair", "stove", "tall_cabinet",
                    "toilet", "washing_machine"]          # 28 Oct 2026: wall_cabinet has its wall_run builder


# --------------------------------------------------------------------------
# Families v2
# --------------------------------------------------------------------------

SIZES = {t: SC.SIZE_OPTIONS[t][SC.DEFAULT_SIZE_INDEX] for t in P.FAMILY_TYPES if t in SC.SIZE_OPTIONS}
SIZES["bed"] = (1.4, 2.0)


@pytest.mark.parametrize("ftype", P.FAMILY_TYPES)
def test_every_family_has_real_parts_and_two_material_slots(ftype):
    w, d = SIZES[ftype]
    h, _ = proxy_height(ftype, None)
    parts = P.build_parts(ftype, w, d, h)
    bw, bd, z0, z1 = _bbox(parts)
    assert (bw, bd) == pytest.approx((w, d), abs=0.01) and z0 == 0.0 and z1 >= h - 0.02
    keys = {p["key"] for p in parts}
    assert len(keys) >= 2 and keys <= set(P.MATERIAL_KEYS), (ftype, keys)
    assert any(P.part_bevel_radius(p) > 0 for p in parts), ftype
    _no_degenerate_faces(parts)
    roles = {p["role"] for p in parts}
    expected = {
        "bed": {"plinth", "body", "bottom", "back", "panel", "mattress", "duvet", "turndown", "pillow"},
        "bed_single": {"plinth", "body", "back", "panel", "mattress", "duvet", "pillow"},
        "bed_double": {"plinth", "body", "bottom", "back", "panel", "mattress", "duvet", "turndown", "pillow"},
        "sofa": {"leg", "body", "arm", "back", "cushion", "back_cushion"},
        "armchair": {"leg", "body", "arm", "back", "cushion", "back_cushion"},
        "table_dining": {"top", "apron", "leg", "foot"}, "table_coffee": {"top", "apron", "leg", "foot", "shelf"},
        "desk": {"top", "apron", "leg", "foot", "drawers", "handle"},
        "nightstand": {"plinth", "body", "top", "front", "handle"}, "dresser": {"plinth", "body", "top", "front", "handle"},
        "bookshelf": {"plinth", "side", "bottom", "top", "back", "shelf"},
        "tv_unit": {"leg", "body", "top", "front", "handle"}, "wardrobe": {"plinth", "body", "top", "front", "handle"},
        "chair": {"leg", "foot", "apron", "top", "back"},                            # round 4: the chair v2
    }[ftype]
    assert expected <= roles, (ftype, roles)
    # the old code's flat looks are gone: no bare box body without legs or fronts
    if ftype in P.BED_TYPES:                    # a platform bed: wood frame, dark plinth, fabric headboard, bedding
        assert {"wood", "dark", "fabric", "bedding", "duvet"} <= keys and sum(p["role"] == "plinth" for p in parts) == 1
    if ftype in ("sofa", "armchair"):
        assert {"fabric", "wood"} <= keys and sum(p["role"] == "leg" for p in parts) == 4
    if ftype in ("table_dining", "table_coffee", "desk"):
        assert "steel" in keys and sum(p["role"] == "foot" for p in parts) == 4
    if ftype in ("nightstand", "dresser", "tv_unit", "wardrobe"):
        assert {"front", "handle"} <= keys and sum(p["role"] == "handle" for p in parts) >= 1
    if ftype == "bookshelf":
        assert "painted" in keys
    if ftype == "chair":                        # a wooden frame, an upholstered pad and back, dark floor glides
        assert {"wood", "fabric", "dark"} <= keys and sum(p["role"] == "foot" for p in parts) == 4


def test_bed_v2_keeps_its_box_and_drapes_its_own_bedding():
    w, d, h = 1.6, 2.0, 0.55
    parts = P.build_parts("bed_double", w, d, h)
    assert P.parametric_bbox("bed_double", w, d, h) == pytest.approx((w, d, 1.0))     # the Milestone 4 box
    by_role = {}
    for p in parts:
        by_role.setdefault(p["role"], []).append(p)
    assert len(by_role["pillow"]) == 2 and len(P.build_parts("bed_single", 0.9, 2.0, h)) and \
        sum(p["role"] == "pillow" for p in P.build_parts("bed_single", 0.9, 2.0, h)) == 1
    duvet = by_role["duvet"][0]
    assert duvet["key"] == "duvet" and duvet.get("smooth") and len(duvet["faces"]) > 100
    xs = [v[0] for v in duvet["verts"]]
    ys = [v[1] for v in duvet["verts"]]
    zs = [v[2] for v in duvet["verts"]]
    assert -w / 2.0 <= min(xs) and max(xs) <= w / 2.0 and min(ys) >= -d / 2.0          # inside the footprint
    assert max(zs) <= h + P.CLOTH_OFFSET_M + P.BED_DUVET_M + P.FOLD_AMPLITUDE_M + 1e-6
    assert 0.3 - 1e-6 <= min(zs) <= 0.3 + P.BED_DUVET_M + 1e-6   # hangs to the rails' ledge (the M6 frame top), never below
    assert max(zs) - min(zs) >= 0.2                                                  # it does hang down the sides
    # the duvet covers the foot share of the mattress and stops before the pillows
    mattress = by_role["mattress"][0]
    m_ys = [v[1] for v in mattress["verts"]]
    assert max(ys) < min(v[1] for p in by_role["pillow"] for v in p["verts"]) + 1e-9
    assert max(ys) - min(m_ys) >= P.DUVET_SHARE * (max(m_ys) - min(m_ys)) - 0.5         # the foot share (minus the pillow zone)
    # pillows lean on the headboard: the head end higher than the foot end
    for pillow in by_role["pillow"]:
        pv = pillow["verts"]
        head = max(v[2] for v in pv if v[1] > sum(q[1] for q in pv) / len(pv))
        foot = max(v[2] for v in pv if v[1] < sum(q[1] for q in pv) / len(pv))
        assert head > foot and max(v[1] for v in pv) < d / 2.0
    assert by_role["turndown"][0]["key"] == "bedding"
    # the headboard: wooden posts and a fabric panel touching +Y; bedding_top above the mattress
    backs = by_role["back"]
    assert {p["key"] for p in backs} == {"wood"} and all(max(v[1] for v in p["verts"]) == pytest.approx(d / 2.0) for p in backs)
    panel = next(p for p in parts if p["role"] == "panel")                             # upholstered, recessed 4 mm
    assert panel["key"] == "fabric" and max(v[1] for v in panel["verts"]) == pytest.approx(d / 2.0 - 0.004)
    # the frame: side rails on the footprint's edges over the full length, the mattress 6 cm inside them (a real
    # frame is wider than its mattress), the plinth recessed; the mattress' sides and foot leave the duvet's gap
    rails = [p for p in parts if p["role"] == "body"]
    assert min(v[0] for p in rails for v in p["verts"]) == -w / 2.0 and max(v[1] for p in rails for v in p["verts"]) == d / 2.0
    assert max(v[0] for v in mattress["verts"]) == pytest.approx(w / 2.0 - P.BED_RAIL_M - P.BED_MATTRESS_GAP_M, abs=1e-6)
    plinth = next(p for p in parts if p["role"] == "plinth")
    assert max(v[0] for v in plinth["verts"]) < w / 2.0 - 0.04 and max(v[2] for v in plinth["verts"]) < 0.3
    # a bed drawn sideways (real03 f_L0_061, 1.95 x 0.95 m): the pillows shrink with the mattress depth
    short = [p for p in P.build_parts("bed_single", 1.95, 0.95, 0.55) if p["role"] == "pillow"]
    assert short and all(max(v[1] for v in p["verts"]) - min(v[1] for v in p["verts"]) <= 0.25 * 0.95 for p in short)
    assert P.bedding_top(w, d, h) > h
    # textiles re-exports the bedding numbers and the pure drape
    assert T.DUVET_SHARE == P.DUVET_SHARE == 0.75 and T.PILLOW_SIZE == P.PILLOW_SIZE and T.TWO_PILLOW_MIN_W == 1.30
    assert T.box_drape_grid is P.box_drape_grid and T.bed_bedding_parts is P.bed_bedding_parts


def test_box_drape_grid_lies_on_the_top_and_hangs_down_the_sides():
    grid = P.box_drape_grid((-0.8, -1.2, 0.8, 0.2), 0.6, -1.0, 0.9, top_z=0.5, drop=0.3)
    out = P.CLOTH_OFFSET_M + P.BED_DUVET_M
    nu, nv = grid.shape[0] - 1, grid.shape[1] - 1
    top = [grid[i, j] for i in range(nu + 1) for j in range(nv + 1) if abs(grid[i, j, 0]) <= 0.6 and grid[i, j, 1] >= -1.0]
    assert all(0.5 + out <= p[2] <= 0.5 + out + P.FOLD_AMPLITUDE_M + 1e-9 for p in top)
    hanging = [grid[i, j] for i in range(nu + 1) for j in range(nv + 1) if grid[i, j, 2] < 0.5 + out - 1e-9]
    assert hanging and min(p[2] for p in hanging) >= 0.5 + out - 0.3 - 1e-9
    assert all(abs(p[0]) <= 0.6 + out + 1e-9 and p[1] >= -1.0 - out - 1e-9 for p in hanging)   # pushed out of the box
    part = P.cloth_solid(grid, P.BED_DUVET_M, key="duvet", role="duvet")
    _no_degenerate_faces([part])


def test_sofa_v2_and_table_v2_proportions():
    sofa = P.build_parts("sofa", 2.2, 0.9, 0.85)
    assert P.parametric_bbox("sofa", 2.2, 0.9, 0.85) == pytest.approx((2.2, 0.9, 0.85))
    seat = [p for p in sofa if p["role"] == "cushion"]
    assert len(seat) == 2 and all(p.get("smooth") for p in seat)                   # rounded cushions
    assert max(v[2] for p in seat for v in p["verts"]) == pytest.approx(P.sofa_seat_height(0.85), abs=1e-6)
    backs = [p for p in sofa if p["role"] == "back_cushion"]
    assert len(backs) == 2 and max(v[2] for p in backs for v in p["verts"]) <= 0.85 + 1e-6
    legs = [p for p in sofa if p["role"] == "leg"]
    assert all(p["key"] == "wood" and min(v[2] for v in p["verts"]) == 0.0 for p in legs)
    arm = next(p for p in sofa if p["role"] == "arm")
    assert min(v[2] for v in arm["verts"]) == pytest.approx(min(P.SOFA_LEG_M, 0.85 * 0.12))
    chair = P.build_parts("armchair", 0.9, 0.9, 0.85)
    assert sum(p["role"] == "cushion" for p in chair) == 1
    table = P.build_parts("table_dining", 1.6, 0.9, 0.75)
    top = next(p for p in table if p["role"] == "top")
    assert max(v[2] for v in top["verts"]) - min(v[2] for v in top["verts"]) == pytest.approx(P.TABLE_TOP_M)
    aprons = [p for p in table if p["role"] == "apron"]
    assert len(aprons) == 4 and max(v[2] for p in aprons for v in p["verts"]) == pytest.approx(0.75 - P.TABLE_TOP_M - P.FRONT_GAP)
    feet = [p for p in table if p["role"] == "foot"]
    assert len(feet) == 4 and all(p["key"] == "steel" and min(v[2] for v in p["verts"]) == 0.0 for p in feet)
    legs = [p for p in table if p["role"] == "leg"]
    for leg in legs:                                                                # tapered: wider at the top
        zs = [v[2] for v in leg["verts"]]
        top_ring = [v for v in leg["verts"] if abs(v[2] - max(zs)) < 1e-9]
        bottom_ring = [v for v in leg["verts"] if abs(v[2] - min(zs)) < 1e-9]
        span = lambda ring: max(v[0] for v in ring) - min(v[0] for v in ring)
        assert span(top_ring) > span(bottom_ring)
    glass = P.build_parts("table_coffee", 1.0, 0.6, 0.45, piece={"design": {"material_tags": ["glass", "metal"]}})
    assert next(p for p in glass if p["role"] == "top")["key"] == "glass"
    assert {p["key"] for p in glass if p["role"] in ("leg", "apron")} == {"steel"}
    assert P.parametric_bbox("desk", 1.4, 0.7, 0.75) == pytest.approx((1.4, 0.7, 0.75))


def test_storage_v2_fronts_follow_the_design():
    plain = P.build_parts("nightstand", 0.5, 0.4, 0.5)
    assert sum(p["role"] == "handle" for p in plain) == 2                            # two drawers at 0.5 m
    dresser = P.build_parts("dresser", 1.2, 0.5, 0.8)
    assert sum(p["role"] == "handle" for p in dresser) == 4
    shaker = P.build_parts("dresser", 1.2, 0.5, 0.8, piece={"design": {"front_style": "shaker"}})
    assert sum(p["role"] == "front" for p in shaker) == 5 * 4
    wardrobe = P.build_parts("wardrobe", 1.8, 0.6, 2.1)
    assert sum(p["role"] == "handle" for p in wardrobe) == 4                         # 0.50 m door modules
    assert next(p for p in wardrobe if p["role"] == "plinth")["key"] == "dark"
    assert next(p for p in wardrobe if p["role"] == "top")["key"] == "wood"
    slatted = P.build_parts("wardrobe", 1.8, 0.6, 2.1, piece={"design": {"front_style": "slatted"}})
    assert "dark" in {p["key"] for p in slatted if p["role"] == "front"}
    tv = P.build_parts("tv_unit", 1.6, 0.45, 0.5)
    assert sum(p["role"] == "leg" for p in tv) == 4 and all(p["key"] == "steel" for p in tv if p["role"] == "leg")
    assert sum(p["role"] == "handle" for p in tv) == 3
    shelf = P.build_parts("bookshelf", 1.0, 0.35, 1.8)
    back = next(p for p in shelf if p["role"] == "back")
    assert back["key"] == "painted" and max(v[1] for v in back["verts"]) == pytest.approx(0.175)
    assert sum(p["role"] == "shelf" for p in shelf) >= 3
    # every family builder takes the piece (its design) through build_parts
    for ftype in P.FAMILY_TYPES:
        assert ftype in P._PIECE_BUILDERS or ftype in ("table_dining", "table_coffee", "desk", "wardrobe"), ftype


def _extent(parts, axis):
    vals = [v[axis] for p in parts for v in p["verts"]]
    return max(vals) - min(vals)


@pytest.mark.parametrize("size", [(0.45, 0.45), (0.5, 0.45), (0.5, 0.5), (0.48, 0.55)])
def test_round4_chair_v2_has_real_proportions_and_two_material_slots(size):
    """Round 4 (docs/milestone13.md §14.8, the P3 pre-flight: a chair below library level was the one-material box
    chair, P3's fit sends f_L1_023 and f_L1_025 there): the chair family v2 at the size table's chair products and
    real04's drawn chairs (0.5 x 0.45). Seat height 0.45-0.47 m, seat depth 0.40-0.45 m, back 0.80-0.90 m (secondary
    compilations: "Dining chair seat height 450-470 mm"; "Dining chair 0.46 x 0.52 x 0.9 ... seat pad at 0.45 with a
    0.42 seat depth"); at least two material slots; bevelled frame edges, a smooth pad; the box kept; the back on
    the rear band camsearch's profile models (min(0.04, 0.1 d), every back part touching +Y). Fails on the round-3
    code (one ``wood`` key, a 0.04 m seat slab, ``chair`` not in FAMILY_TYPES)."""
    w, d = size
    h, _ = proxy_height("chair", None)
    assert h == pytest.approx(0.9) and "chair" in P.FAMILY_TYPES and "chair" in P._PIECE_BUILDERS
    parts = P.build_parts("chair", w, d, h)
    assert _bbox(parts) == pytest.approx((w, d, 0.0, h), abs=1e-9)                 # the Milestone 4 box
    keys = {p["key"] for p in parts}
    assert len(keys) >= 2 and keys == {"wood", "fabric", "dark"}                    # frame, pad and back, glides
    seat = [p for p in parts if p["role"] == "top"]
    seat_top = max(v[2] for p in seat for v in p["verts"])
    assert 0.45 <= seat_top <= 0.47 and seat_top == pytest.approx(P.chair_seat_height(h))
    pad = next(p for p in seat if p["key"] == "fabric")
    assert pad.get("smooth") and 0.40 <= _extent([pad], 1) <= 0.45                   # the sitting surface's depth
    back = [p for p in parts if p["role"] == "back"]
    assert 0.80 <= max(v[2] for p in back for v in p["verts"]) <= 0.90
    t = min(P.CHAIR_BACK_T_M, d * 0.1)
    assert all(max(v[1] for v in p["verts"]) == pytest.approx(d / 2.0) for p in back)
    assert min(v[1] for p in back for v in p["verts"]) == pytest.approx(d / 2.0 - t)
    assert any(p["key"] == "fabric" for p in back)                                  # an upholstered back panel
    legs = [p for p in parts if p["role"] == "leg"]
    assert len(legs) == 2 and sum(p["role"] == "foot" for p in parts) == 4           # front legs + posts, 4 glides
    for leg in legs:                                                                # tapered: wider at the top
        zs = [v[2] for v in leg["verts"]]
        top = [v for v in leg["verts"] if abs(v[2] - max(zs)) < 1e-9]
        low = [v for v in leg["verts"] if abs(v[2] - min(zs)) < 1e-9]
        assert max(v[0] for v in top) - min(v[0] for v in top) > max(v[0] for v in low) - min(v[0] for v in low)
    wood = [p for p in parts if p["key"] == "wood"]
    assert wood and all(P.part_bevel_radius(p) > 0 for p in wood)                   # bevelled frame edges
    _no_degenerate_faces(parts)


def test_round4_chair_v2_follows_the_design_tags_and_the_long_table_builds_it():
    """The design's material tags pick the frame and the seat (``chair_design``): ``metal`` a steel sled base with
    the pad on a dark shell, ``wood`` a shaped wooden seat and back panel, ``rattan`` a rattan seat; every variant
    keeps two or more material slots and the box. The long table module (a footprint that includes its chairs)
    builds its chairs through ``build_parts("chair")``: the same family, so they are no box chairs either."""
    w, d, h = 0.45, 0.45, 0.9
    sled = P.build_parts("chair", w, d, h, piece={"design": {"material_tags": ["metal"]}})
    assert {p["key"] for p in sled} == {"steel", "dark", "fabric"}
    assert sum(p["role"] == "base" for p in sled) == 2 and not any(p["role"] == "foot" for p in sled)
    assert all(p["key"] == "steel" and min(v[2] for v in p["verts"]) == pytest.approx(0.0)
               for p in sled if p["role"] == "base")                                 # runners on the floor
    wooden = P.build_parts("chair", w, d, h, piece={"design": {"material_tags": ["wood"]}})
    assert {p["key"] for p in wooden} == {"wood", "dark"}
    assert {p["key"] for p in wooden if p["role"] == "top"} == {"wood"}
    rattan = P.build_parts("chair", w, d, h, piece={"design": {"material_tags": ["rattan", "wood"]}})
    assert {p["key"] for p in rattan if p["role"] == "top"} == {"rattan"} and len({p["key"] for p in rattan}) >= 2
    assert P.chair_design({"design": {"material_tags": ["metal", "wood"]}}) == {
        "frame": "steel", "seat": "wood", "base": "sled", "back": "panel"}
    for parts in (sled, wooden, rattan):
        assert _bbox(parts) == pytest.approx((w, d, 0.0, h), abs=1e-9)
        assert max(v[2] for p in parts if p["role"] == "top" for v in p["verts"]) == pytest.approx(0.45)
        _no_degenerate_faces(parts)
    # the long table splits its chairs from a deep footprint and builds them with the v2 family
    plan = M.module_plan(_piece("table_dining", 2.3, 1.6))
    chairs = [m for m in plan["modules"] if m["kind"] == "chair"]
    assert chairs and M.material_keys(plan) and {"fabric", "dark"} <= set(M.material_keys(plan))
    parts = M.module_parts(plan)
    assert sum(p["role"] == "foot" and p["key"] == "dark" for p in parts) == 4 * len(chairs)


# --------------------------------------------------------------------------
# Fix round after P3 (16-17 Oct 2026): drawn sinks built into a run, gaps for drawn stoves
# --------------------------------------------------------------------------

def _xspan(parts, roles):
    xs = [v[0] for p in parts if p["role"] in roles for v in p["verts"]]
    return (min(xs), max(xs)) if xs else None


def _covers(parts, roles, x0, x1):
    """True when a part of these roles reaches into the open interval (x0, x1) of the run's x axis."""
    return any(min(v[0] for v in p["verts"]) < x1 - 1e-6 and max(v[0] for v in p["verts"]) > x0 + 1e-6
               for p in parts if p["role"] in roles)


def test_member_in_run_measures_the_share_and_the_span_along_the_run():
    run = _piece("kitchen_counter", 1.8766, 0.6, center=(1.5007, 10.2618), rot=90.0)
    sink = _piece("sink_kitchen", 0.7885, 0.5, center=(1.4507, 10.2592), rot=90.0)     # real04 f_L-1_067
    got = M.member_in_run(run, sink)
    assert got["share"] == pytest.approx(1.0) and got["w_m"] == pytest.approx(0.7885, abs=1e-4)
    assert got["x_m"] == pytest.approx(10.2592 - 10.2618, abs=1e-4)                    # along the run (rot 90: +y)
    stove = _piece("stove", 0.75, 0.5491, center=(2.5832, 11.4672))                    # real04 f_L-1_008 in f_L-1_002
    run2 = _piece("kitchen_counter", 2.3213, 0.5999, center=(2.3613, 11.5001))
    got2 = M.member_in_run(run2, stove)
    assert 0.98 < got2["share"] < 0.99 and (got2["x0_m"], got2["x1_m"]) == pytest.approx((-0.1531, 0.5969), abs=1e-4)
    beside = _piece("sink_kitchen", 0.8, 0.5, center=(3.0, 0.0))                       # next to a 2.4 m run
    assert M.member_in_run(_piece("kitchen_counter", 2.4, 0.6), beside)["share"] == 0.0
    turned = _piece("stove", 0.6, 0.6, center=(0.0, 0.3), rot=45.0)                    # half out, turned
    assert 0.0 < M.member_in_run(_piece("kitchen_counter", 2.4, 0.6), turned)["share"] < 0.7
    assert M.member_in_run(_piece("kitchen_counter", 2.4, 0.6), {"id": "x", "type": "stove"}) is None


def test_a_drawn_stove_stands_in_a_gap_of_the_run():
    """The verifier's case (gpu_tests lens of P3): a 1.88 m run with a centred 0.79 m stove gets no base unit, no
    plinth and no worktop over [-0.395, 0.395]; the rest of the run is real units and fillers; the plan lists the
    gap; the box the planners read keeps the run's width."""
    piece = _piece("kitchen_counter", 1.88, 0.6,
                   module_hints={"ranges": [{"id": "f_st", "type": "stove", "x0_m": -0.395, "x1_m": 0.395}]})
    plan = M.module_plan(piece)
    assert plan["gaps"] == [{"id": "f_st", "kind": "range", "type": "stove", "x_m": 0.0, "w_m": 0.79}]
    assert plan["cutouts"] == [] and any("gap for the drawn stove f_st" in n for n in plan["notes"])
    parts = M.module_parts(plan)
    for roles in (("body", "front", "handle"), ("plinth",), ("top",)):
        assert not _covers(parts, roles, -0.395, 0.395), roles
    units = [m for m in plan["modules"] if m["kind"] in ("base_unit", "filler")]
    assert sum(m["size_m"][0] for m in units) == pytest.approx(1.88 - 0.79)
    assert all(m["size_m"][0] in M.KITCHEN_BASE_WIDTHS_M for m in units if m["kind"] == "base_unit")
    tops = [m for m in plan["modules"] if m["kind"] == "worktop"]
    assert [(m["size_m"][0], m["pos_m"][0]) for m in tops] == [(pytest.approx(0.545), pytest.approx(-0.6675)),
                                                                (pytest.approx(0.545), pytest.approx(0.6675))]
    assert _xspan(parts, ("top",)) == pytest.approx((-0.94, 0.94))
    assert M.plan_bbox(plan)[0] == pytest.approx(1.88) and M.module_record(plan)["gaps"] == plan["gaps"]
    _no_degenerate_faces(parts)
    # a stove at the run's end: the gap stays where it is drawn (no end shift), the worktop stops at it
    end = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "ranges": [{"id": "f_st", "type": "stove", "x0_m": 0.55, "x1_m": 1.15}]}))
    assert end["gaps"][0]["x_m"] == pytest.approx(0.85) and end["gaps"][0]["w_m"] == pytest.approx(0.6)
    eparts = M.module_parts(end)
    assert not _covers(eparts, ("body", "front", "top", "plinth"), 0.55, 1.15)
    assert _covers(eparts, ("front",), 1.15, 1.2)                         # the 5 cm slit to the wall is a filler
    assert M.plan_bbox(end)[0] == pytest.approx(2.4)                      # the planners' box keeps the run
    # without hints the plan is the one of before (one plinth, one worktop over the run)
    plain = M.module_plan(_piece("kitchen_counter", 1.88, 0.6))
    assert [m["kind"] for m in plain["modules"]].count("worktop") == 1 and "gaps" not in plain


def test_the_drawn_sink_is_built_into_the_run_and_a_stove_gap_never_moves():
    """real04 f_L-1_003 with its drawn sink f_L-1_067 (0.79 m, centred): an 0.80 m sink unit at the drawn centre,
    the cutout with the bowl and the tap, ``built_ins`` naming the sink. synthetic-03's run: the sink at the run's
    end and a 0.60 m stove gap at its drawn span; a sink unit that would overlap a gap is not made."""
    run = _piece("kitchen_counter", 1.8766, 0.6, center=(1.5007, 10.2618), rot=90.0,
                 module_hints={"sink_pos_m": [1.4507, 10.2592], "sink_w_m": 0.7885, "sink_piece": "f_L-1_067"})
    plan = M.module_plan(run)
    assert plan["cutouts"] == ["sink"]
    assert plan["built_ins"] == [{"id": "f_L-1_067", "kind": "sink", "x_m": pytest.approx(-0.0026, abs=1e-4),
                                  "w_m": 0.8, "drawn_x_m": pytest.approx(-0.0026, abs=1e-4),
                                  "shift_m": pytest.approx(0.0, abs=1e-4),     # part 2: the shift is recorded
                                  "drawn_y_m": pytest.approx(0.05, abs=1e-4),  # part 3: and the offset across
                                  "shift_y_m": pytest.approx(-0.05, abs=1e-4)}]
    roles = {p["role"] for p in M.module_parts(plan)}
    assert {"basin", "tap"} <= roles and M.module_record(plan)["built_ins"] == plan["built_ins"]
    both = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_pos_m": [-0.8, 0.0], "sink_w_m": 0.8, "sink_piece": "f_sink",
        "ranges": [{"id": "f_stove", "type": "stove", "x0_m": 0.45, "x1_m": 1.05}]}))
    sink = next(m for m in both["modules"] if m.get("holds") == "sink")
    assert sink["pos_m"][0] == pytest.approx(-0.8) and both["gaps"][0]["x_m"] == pytest.approx(0.75)
    parts = M.module_parts(both)
    assert not _covers(parts, ("body", "front", "top", "plinth"), 0.45, 1.05)
    basin = _xspan(parts, ("basin",))
    assert (basin[0] + basin[1]) / 2.0 == pytest.approx(-0.8, abs=0.01)
    clash = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 0.6, "sink_w_m": 0.8, "sink_piece": "f_sink",
        "ranges": [{"id": "f_stove", "type": "stove", "x0_m": 0.45, "x1_m": 1.05}]}))
    assert clash["cutouts"] == [] and "built_ins" not in clash
    assert any("no sink unit" in n for n in clash["notes"])


def test_an_island_with_a_stove_gap_has_no_panel_across_it():
    plan = M.module_plan(_piece("kitchen_island", 2.13, 0.9, module_hints={
        "ranges": [{"id": "f_st", "type": "stove", "x0_m": -0.3, "x1_m": 0.3}]}))
    parts = M.module_parts(plan)
    assert not _covers(parts, ("panel", "plinth", "top", "body"), -0.3, 0.3)
    assert _xspan(parts, ("panel",)) == pytest.approx((-1.065, 1.065))
    plinths = [m for m in plan["modules"] if m["kind"] == "plinth"]
    assert plinths[0]["pos_m"][0] - plinths[0]["size_m"][0] / 2.0 == pytest.approx(-1.065 + M.KITCHEN_PLINTH_RECESS_M)
    assert plinths[-1]["pos_m"][0] + plinths[-1]["size_m"][0] / 2.0 == pytest.approx(1.065 - M.KITCHEN_PLINTH_RECESS_M)


def test_module_plan_of_reads_the_hints_the_fit_kept_in_the_asset():
    """The fit never writes ``module_hints`` onto the building piece; furniture.module_plan_of merges
    ``asset.module_hints`` into the piece when it must make the plan itself."""
    piece = _piece("kitchen_counter", 2.4, 0.6)
    hints = {"ranges": [{"id": "f_st", "type": "stove", "x0_m": 0.45, "x1_m": 1.05}]}
    plan, why = F.module_plan_of(dict(piece, asset={"method": "module", "module_hints": hints}))
    assert "stored none" in why and plan["gaps"][0]["id"] == "f_st"
    assert "module_hints" not in piece


# --------------------------------------------------------------------------
# Fix round after P3, part 2 (17 Oct 2026): the sink unit's open bowl, a sink off its unit, never an empty run
# --------------------------------------------------------------------------

def test_part2_the_sink_unit_is_hollow_under_its_bowl_and_closed_around_it():
    """P3 review: the sink unit's solid body reached the worktop's underside, so the bowl (0.18 m under the worktop's
    top face) showed a 4 cm tray with a cabinet-paint floor. Now a ray down through the bowl meets the steel bottom
    first, the unit keeps its box (two sides and a back board up to the worktop), the other units stay solid."""
    hints = {"sink_pos_m": [-0.8, 0.0], "sink_w_m": 0.8, "sink_piece": "f_sink"}
    plan = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints=hints))
    parts = M.module_parts(plan)
    (x0, x1, _y0, _y1, zb, rim), = assert_open_bowls(parts)
    top = M.KITCHEN_WORKTOP_HEIGHT_M
    assert rim == pytest.approx(top) and zb == pytest.approx(top - M.KITCHEN_SINK_BOWL_M + 0.008)
    assert (x0 + x1) / 2.0 == pytest.approx(-0.8)
    z, part = surface_under(parts, -0.8, -0.1, 1.5)
    assert part["key"] == "steel" and part["role"] == "basin" and z < top - 0.15      # the GPU ray's bound
    unit = next(m for m in plan["modules"] if m.get("holds") == "sink")
    body = [p for p in M._base_unit_parts(unit, {}, 0.6) if p["role"] == "body"]
    bx0, _by0, bz0, bx1, _by1, bz1 = P.parts_bbox(body)
    assert (bx0, bx1, bz0, bz1) == pytest.approx((-1.199, -0.401, M.KITCHEN_PLINTH_M, top - M.KITCHEN_WORKTOP_M))
    solid = min(body, key=lambda p: min(v[2] for v in p["verts"]))
    assert len(body) == 4                                                        # solid under the bowl, three boards
    assert max(v[2] for v in solid["verts"]) == pytest.approx(top - M.KITCHEN_SINK_BOWL_M - P.BASIN_CLEAR_M)
    for m in plan["modules"]:
        if m["kind"] == "base_unit" and not m.get("holds"):
            assert len([p for p in M._base_unit_parts(m, {}, 0.6) if p["role"] == "body"]) == 1
    # a drawn counter height moves the bowl and the hollow with it
    low = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, height=0.85, module_hints=hints))
    (_x0, _x1, _y0, _y1, zb2, rim2), = assert_open_bowls(M.module_parts(low))
    assert rim2 == pytest.approx(0.85) and zb2 == pytest.approx(0.85 - M.KITCHEN_SINK_BOWL_M + 0.008)


def test_part2_the_module_vanity_is_hollow_under_its_basins():
    one = M.module_plan(_piece("washbasin", 0.8, 0.5, height=0.85))
    assert one["builder"] == "bath_set" and one["basins"] == 1
    assert_open_bowls(M.module_parts(one))
    two = M.module_plan(_piece("washbasin", 1.2, 0.5, height=0.85))
    assert two["basins"] == 2
    assert_open_bowls(M.module_parts(two), expected_bowls=2)
    x0, y0, z0, x1, y1, _z1 = P.parts_bbox([p for p in M.module_parts(two) if p["role"] in ("body", "front")])
    assert (x1 - x0, z0) == pytest.approx((1.2, M.VANITY_BOTTOM_M), abs=0.005)    # the cabinet keeps its box


def test_part2_a_drawn_sink_off_its_unit_is_not_built_in_and_stands_in_a_gap():
    """A drawn sink overhanging the run's end: its 0.80 m unit, clamped into the run, would stand 0.30 m from the
    drawn centre (part 1 built it there with no record). It is not built in: a gap at its drawn span (the sink keeps
    its own model there, as drawn). Within KITCHEN_END_SHIFT_MAX_M it is built in and the shift is recorded."""
    plan = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 1.1, "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    assert "built_ins" not in plan and plan["cutouts"] == []
    (gap,) = plan["gaps"]
    assert (gap["id"], gap["type"]) == ("f_sink", "sink_kitchen")
    assert (gap["x_m"], gap["w_m"]) == (pytest.approx(0.95), pytest.approx(0.5))
    assert "0.30 m from the drawn centre" in gap["reason"]
    assert any("f_sink is not built in" in n for n in plan["notes"])
    parts = M.module_parts(plan)
    assert not _covers(parts, ("body", "front", "handle", "top", "plinth", "basin", "tap"), 0.70, 1.2)
    assert _covers(parts, ("top",), -1.2, 0.70) and not [p for p in parts if p["role"] == "basin"]
    assert M.plan_bbox(plan)[0] == pytest.approx(2.4)
    # at the limit (0.10 m) it is built in; just past it, it is not
    at = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 0.90, "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    assert at["built_ins"][0]["shift_m"] == pytest.approx(-0.10) and "gaps" not in at
    past = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 0.92, "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    assert "built_ins" not in past and past["gaps"][0]["id"] == "f_sink"
    # a small shift is built in, recorded and named
    near = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 0.85, "sink_w_m": 0.75, "sink_piece": "f_sink"}))
    (b,) = near["built_ins"]
    assert (b["x_m"], b["drawn_x_m"], b["shift_m"]) == (pytest.approx(0.8), pytest.approx(0.85), pytest.approx(-0.05))
    assert any("0.05 m from the drawn centre" in n for n in near["notes"])
    # the sink's position from the fit (world ``sink_pos_m``, a turned run): the same decision
    turned = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, center=(1.0, 2.0), rot=90.0, module_hints={
        "sink_pos_m": [1.0, 3.1], "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    assert "built_ins" not in turned and turned["gaps"][0]["x_m"] == pytest.approx(0.95)
    # a sink unit that would overlap a stove's gap: not built in, and its gap would overlap the stove's: none
    clash = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 0.6, "sink_w_m": 0.8, "sink_piece": "f_sink",
        "ranges": [{"id": "f_stove", "type": "stove", "x0_m": 0.45, "x1_m": 1.05}]}))
    assert "built_ins" not in clash and [g["id"] for g in clash["gaps"]] == ["f_stove"]
    assert any("f_sink is not built in" in n and "no gap either" in n for n in clash["notes"])
    # without a drawn sink piece (an inferred place, e.g. under the window) the unit is clamped as before
    inferred = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={"sink_x_m": 1.1, "sink_w_m": 0.8}))
    assert inferred["cutouts"] == ["sink"] and "gaps" not in inferred and "built_ins" not in inferred


def test_part2_a_stove_over_its_whole_run_never_empties_the_plan():
    """P3 review (reproduced with bpy 5.2.2): a 0.6 m counter with a 0.6 m stove on it gave a plan with no module;
    the scene linked an empty ``furn_<id>`` and the fallback box became ``furn_<id>.001``. Now the gap that would
    leave nothing of the run is not made (the run is built whole; S2 reports the stove), and ``build_module``
    refuses a plan without parts before it links anything."""
    run = _piece("kitchen_counter", 0.6, 0.6, module_hints={
        "ranges": [{"id": "f_st", "type": "stove", "x0_m": -0.3, "x1_m": 0.3}]})
    plan = M.module_plan(run)
    assert "gaps" not in plan and {"plinth", "worktop", "base_unit"} <= {m["kind"] for m in plan["modules"]}
    assert M.module_parts(plan)
    assert any("no gap for the drawn stove f_st: it would leave nothing of the run" in n for n in plan["notes"])
    two = M.module_plan(_piece("kitchen_counter", 1.2, 0.6, module_hints={
        "ranges": [{"id": "a", "type": "stove", "x0_m": -0.6, "x1_m": 0.0},
                   {"id": "b", "type": "stove", "x0_m": 0.0, "x1_m": 0.6}]}))
    assert [g["id"] for g in two["gaps"]] == ["a"] and _covers(M.module_parts(two), ("top",), 0.0, 0.6)
    # an island stretch narrower than the plinth recess: no plinth (its width was negative)
    island = M.module_plan(_piece("kitchen_island", 2.13, 0.9, module_hints={
        "ranges": [{"id": "f_st", "type": "stove", "x0_m": 0.465, "x1_m": 1.035}]}))
    plinths = [m for m in island["modules"] if m["kind"] == "plinth"]
    assert len(plinths) == 1 and all(v > 0 for m in plinths for v in m["size_m"])
    _no_degenerate_faces(M.module_parts(island))
    with pytest.raises(ValueError, match="no parts"):
        M.build_module({"builder": "kitchen_run", "modules": [], "footprint_m": [0.6, 0.6]}, run, {})


# --------------------------------------------------------------------------
# Fix round after P3, part 3 (17 Oct 2026): the drawn sink is measured across the run too
# --------------------------------------------------------------------------

def test_part3_a_drawn_sink_off_the_run_s_centreline_is_not_built_in_and_stands_in_a_gap():
    """The review's case: a 2.4 x 0.6 m run (rotation 90) and a drawn 0.8 x 0.5 m sink centred 0.25 m in front of the
    run's centreline (40 % of it over the front edge). Part 2 measured only along the run (shift 0) and built the bowl
    on the centreline, 0.25 m from the drawn centre, with no record. Now the bowl's distance to the drawn centre is
    measured across the run too: past KITCHEN_END_SHIFT_MAX_M the sink is not built in and gets a gap at its drawn
    span with the reason; within it, it is built in and the offset across is recorded and named."""
    run = _piece("kitchen_counter", 2.4, 0.6, rot=90.0)
    front = M.module_plan(dict(run, module_hints={"sink_pos_m": [0.25, 0.0], "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    assert "built_ins" not in front and front["cutouts"] == []
    (gap,) = front["gaps"]
    assert (gap["id"], gap["type"], gap["x_m"], gap["w_m"]) == ("f_sink", "sink_kitchen", pytest.approx(0.0),
                                                                pytest.approx(0.8))
    assert "0.25 m from the drawn centre" in gap["reason"] and "0.25 m across it" in gap["reason"]
    assert "toward the run's front edge" in gap["reason"]
    assert any("f_sink is not built in" in n and "gap at its drawn span" in n for n in front["notes"])
    parts = M.module_parts(front)
    assert not _covers(parts, ("body", "front", "handle", "top", "plinth", "basin", "tap"), -0.4, 0.4)
    assert _covers(parts, ("top",), -1.2, -0.4) and _covers(parts, ("top",), 0.4, 1.2)
    assert M.plan_bbox(front)[0] == pytest.approx(2.4)
    # the same place in the run's frame (sink_x_m / sink_y_m); toward the back edge too
    local = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 0.0, "sink_y_m": -0.25, "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    assert local["gaps"] == front["gaps"]
    back = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 0.0, "sink_y_m": 0.15, "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    assert "built_ins" not in back and "toward the run's back edge" in back["gaps"][0]["reason"]
    # one distance for both axes: 0.08 m along (the unit clamped to the run's end) and 0.08 m across is 0.11 m
    both = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 0.88, "sink_y_m": 0.08, "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    assert "built_ins" not in both
    assert "0.11 m from the drawn centre (0.08 m along the run" in both["gaps"][0]["reason"]
    # at the limit across (0.10 m) it is built in, the offset recorded and named; the bowl stays on the centreline
    at = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 0.0, "sink_y_m": -0.10, "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    (b,) = at["built_ins"]
    assert (b["shift_m"], b["drawn_y_m"], b["shift_y_m"]) == (pytest.approx(0.0), pytest.approx(-0.10),
                                                              pytest.approx(0.10))
    assert any("the bowl stands 0.10 m behind the drawn sink centre" in n for n in at["notes"]) and "gaps" not in at
    (x0, x1, y0, y1, _zb, _rim), = assert_open_bowls(M.module_parts(at))
    assert (x0 + x1) / 2.0 == pytest.approx(0.0, abs=0.01) and (y0 + y1) / 2.0 == pytest.approx(0.0, abs=0.01)
    # real04's sinks lie 0.05 m behind the centreline: built in as before, the 0.05 m named
    real = M.module_plan(dict(run, module_hints={"sink_pos_m": [-0.05, 0.0], "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    assert real["built_ins"][0]["shift_y_m"] == pytest.approx(-0.05)
    assert any("the bowl stands 0.05 m in front of the drawn sink centre" in n for n in real["notes"])
    # without a drawn place across the run (sink_x_m only) the decision is the one along the run, as in part 2
    along = M.module_plan(_piece("kitchen_counter", 2.4, 0.6, module_hints={
        "sink_x_m": 0.0, "sink_w_m": 0.8, "sink_piece": "f_sink"}))
    assert "shift_y_m" not in along["built_ins"][0] and "gaps" not in along
