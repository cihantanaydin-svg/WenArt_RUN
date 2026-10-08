"""Milestone 10 cabinets and furniture looks (docs/milestone10.md §4.4, §4.5, §1.6b row 15; track F).

CPU tests of the parametric cabinet fronts (flat, shaker, slatted, glass) and handles, the kitchen counter run, wall,
tall, shoe and display cabinets, sideboards, the vanity and built-in wardrobe looks, the corner sofa from
``schemas.l_parts``, wall-hung pieces (``mount_bottom_m``), the designs of ``looks.design_for`` (the layout's
``furniture.design`` first, else ``style.json`` and the vanity / built-in rules) and the material keys a design
changes (``furniture.design_overrides``); the catalogue and the proxy table know the 14 new types. A Blender scene
(skipped without ``WENART_BLENDER``) builds a kitchen, a bathroom and a living room with these looks.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import pytest

from wenart.blender import cli, looks, proxies
from wenart.blender import furniture as F
from wenart.blender import parametric as P
from wenart.furniture import catalog as C
from wenart.furniture import schemas as SC

ROOT = Path(__file__).resolve().parents[1]
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER)")
NEW_TYPES = ("sofa_corner", "chaise", "ottoman", "bench", "bar_stool", "office_chair", "console_table", "crib",
             "bunk_bed", "sideboard", "shoe_cabinet", "display_cabinet", "tall_cabinet", "wall_cabinet")


def _piece(ftype, design=None, size=None, **extra):
    w, d = size or SC.SIZE_OPTIONS.get(ftype, [(1.0, 0.6)] * 3)[1]
    piece = {"id": f"f_{ftype}", "type": ftype, "level_id": "L0", "room_id": "r",
             "footprint": {"center": [0.0, 0.0], "size": [w, d], "rotation_deg": 0.0}, "front_deg": 270.0}
    if design is not None:
        piece["design"] = design
    piece.update(extra)
    return piece


def _parts(ftype, design=None, size=None, **extra):
    piece = _piece(ftype, design, size, **extra)
    w, d = piece["footprint"]["size"]
    h, _ = proxies.proxy_height(ftype, None)
    return P.build_parts(ftype, w, d, h, piece=piece), (w, d, h)


def _ys(part):
    return [v[1] for v in part["verts"]]


# --------------------------------------------------------------------------
# Tables shared with track B and C
# --------------------------------------------------------------------------

def test_the_new_types_are_known_everywhere():
    assert set(NEW_TYPES) <= set(P.PARAMETRIC_TYPES) and set(NEW_TYPES) <= set(C.FURNITURE_TYPES)
    for t in NEW_TYPES:
        assert proxies.PROXY_HEIGHTS[t] == SC.HEIGHTS[t] == C.PARAMETRIC_HEIGHTS[t], t
    catalog = C.load(library=False)
    assert set(NEW_TYPES) <= set(catalog.parametric_types)
    # looks.py repeats track B's tables (schemas needs jsonschema, Blender's Python has none)
    assert looks.CABINET_TYPES == SC.CABINET_TYPES and looks.FABRIC_TYPES == SC.FABRIC_TYPES
    assert looks.VANITY_MIN_DEPTH_M == SC.VANITY_MIN_DEPTH_M
    assert P.FRONT_STYLES == SC.FRONT_STYLES
    from wenart.style import finishes as FIN
    assert set(looks.HANDLE_SLUGS.items()) == set(FIN.CABINET_HANDLES.items())
    assert P.L_SEAT_DEPTH_M == SC.L_SEAT_DEPTH_M and P.L_CHAISE_WIDTH_M == SC.L_CHAISE_WIDTH_M


@pytest.mark.parametrize("size,side,depth,seat,width", [((2.6, 1.6), "right", 1.6, None, None),
                                                         ((2.6, 1.6), "left", None, 0.85, 1.0),
                                                         ((3.0, 1.7), None, 1.5, 0.95, 0.8),
                                                         ((1.6, 1.4), "left", 2.0, 2.0, 1.2)])
def test_corner_sofa_rectangles_are_schemas_l_parts(size, side, depth, seat, width):
    assert P.l_parts(size, side, depth, seat, width) == SC.l_parts(size, side, depth, seat, width)


# --------------------------------------------------------------------------
# Fronts and handles
# --------------------------------------------------------------------------

@pytest.mark.parametrize("style", P.FRONT_STYLES)
@pytest.mark.parametrize("ftype", ("kitchen_counter", "kitchen_island", "sideboard", "tall_cabinet", "wall_cabinet",
                                   "shoe_cabinet", "display_cabinet"))
def test_fronts_of_every_style_stand_on_the_front_with_their_handles(ftype, style):
    parts, (w, d, h) = _parts(ftype, {"front_style": style, "handle": "brass"})
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert (x1 - x0) == pytest.approx(w, abs=0.01) and (y1 - y0) == pytest.approx(d, abs=0.01)
    assert z0 == pytest.approx(0.0) and z1 >= h - 0.02
    body = [p for p in parts if p["role"] in ("body", "side")]
    fronts = [p for p in parts if p["role"] == "front"]
    handles = [p for p in parts if p["role"] == "handle"]
    assert fronts and handles and all(p["key"] == "handle" for p in handles)
    face = min(v[1] for p in body for v in p["verts"])
    for p in fronts:                                       # the fronts stand before the carcass face, on -Y
        assert max(_ys(p)) <= face - P.FRONT_GAP + 1e-9 and min(_ys(p)) >= -d / 2.0 - 1e-9
    front_face = min(v[1] for p in fronts for v in p["verts"])
    for p in handles:
        assert max(_ys(p)) == pytest.approx(face - P.FRONT_GAP - P.FRONT_THICKNESS, abs=1e-6) or \
            max(_ys(p)) == pytest.approx(front_face, abs=1e-6)
    keys = {p["key"] for p in fronts}
    assert keys <= {"front", "dark", "glass"}
    if style == "glass":
        assert "glass" in keys
    if style == "slatted":
        assert "dark" in keys and sum(p["key"] == "front" for p in fronts) > 2 * len(handles)
    if style == "shaker":
        assert sum(1 for p in fronts) == 5 * len(handles) or ftype == "tall_cabinet"


def test_the_flat_counter_keeps_the_milestone_6_fronts():
    parts, (w, d, h) = _parts("kitchen_counter", None, (2.4, 0.6))
    assert sum(p["role"] == "front" for p in parts) == sum(p["role"] == "handle" for p in parts) == 4
    assert {p["key"] for p in parts if p["role"] == "front"} == {"front"}
    details = F.design_details("kitchen_counter", parts)
    assert "4 front(s)" in details[0]["value"]
    sb, _ = _parts("sideboard", {"front_style": "shaker"})
    assert F.design_details("sideboard", sb)[0]["kind"] == "cabinet_fronts"


def test_display_cabinet_shows_glass_and_shelves_by_default():
    parts, _ = _parts("display_cabinet")
    assert any(p["key"] == "glass" and p["role"] == "front" for p in parts)
    assert sum(p["role"] == "shelf" for p in parts) >= 3


def test_vanity_and_built_in_looks_keep_the_drawn_type_and_box():
    plain, (w, d, h) = _parts("washbasin", None, (0.8, 0.5))
    assert "pedestal" in {p["role"] for p in plain}
    vanity, _ = _parts("washbasin", {"vanity": True, "front_style": "slatted", "colour": "walnut brown"}, (0.8, 0.5))
    roles = {p["role"] for p in vanity}
    assert {"basin", "tap", "front", "body"} <= roles and "pedestal" not in roles
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(vanity)
    assert (x1 - x0, y1 - y0) == pytest.approx((0.8, 0.5), abs=0.01) and z0 == 0.0
    built, (w, d, h) = _parts("wardrobe", {"built_in": True, "front_style": "shaker"}, (2.4, 0.6))
    fronts = [p for p in built if p["role"] == "front"]
    assert min(v[0] for p in fronts for v in p["verts"]) == pytest.approx(-1.2, abs=0.01)    # wall to wall
    assert max(v[0] for p in fronts for v in p["verts"]) == pytest.approx(1.2, abs=0.01)


def test_table_tops_follow_the_material_tags():
    glass, _ = _parts("table_coffee", {"material_tags": ["glass"]})
    assert next(p for p in glass if p["role"] == "top")["key"] == "glass"
    assert any(p["role"] == "shelf" for p in glass)                    # the frame under a glass top
    marble, _ = _parts("table_dining", {"material_tags": ["marble", "metal"]})
    assert next(p for p in marble if p["role"] == "top")["key"] == "marble"
    assert {p["key"] for p in marble if p["role"] == "leg"} == {"steel"}


# --------------------------------------------------------------------------
# Corner sofa, wall cabinets
# --------------------------------------------------------------------------

@pytest.mark.parametrize("side", ["right", "left"])
def test_corner_sofa_puts_the_chaise_on_its_side(side):
    parts, (w, d, h) = _parts("sofa_corner", None, (2.6, 1.6), shape="L", chaise_side=side, chaise_depth=1.6)
    cushions = [p for p in parts if p["role"] == "cushion"]
    chaise = min(cushions, key=lambda p: min(_ys(p)))          # the one reaching furthest to the front
    xs = [v[0] for v in chaise["verts"]]
    assert (min(xs) > 0) if side == "right" else (max(xs) < 0)
    assert min(_ys(chaise)) < -d / 2.0 + 0.05
    arm = next(p for p in parts if p["role"] == "arm")
    assert (max(v[0] for v in arm["verts"]) < 0) if side == "right" else (min(v[0] for v in arm["verts"]) > 0)
    info = P.sofa_corner_parts_info(_piece("sofa_corner", size=(2.6, 1.6), chaise_side=side))
    assert info["chaise_side"] == side and not info["chaise_side_assumed"]
    assert P.sofa_corner_parts_info(_piece("sofa_corner", size=(2.6, 1.6)))["chaise_side_assumed"]


def test_wall_cabinets_hang_at_their_mount_height():
    hung = _piece("wall_cabinet", mount_bottom_m=1.5)
    assert proxies.mount_bottom(hung) == (1.5, False)
    assert proxies.mount_bottom(_piece("wall_cabinet")) == (proxies.DEFAULT_MOUNT_BOTTOM_M, True)
    assert proxies.mount_bottom(_piece("sideboard")) == (0.0, False)
    geo = proxies.proxy_geometry(dict(hung, height=None), 0.0)
    zs = [v[2] for v in geo["box"][0]]
    assert min(zs) == pytest.approx(1.5) and max(zs) == pytest.approx(1.5 + proxies.PROXY_HEIGHTS["wall_cabinet"])


# --------------------------------------------------------------------------
# Designs: the layout's design first, the style's fallback and the rules
# --------------------------------------------------------------------------

STYLE = {"cabinets": {"front_style": "shaker", "colour": "sage", "handle": "brass", "worktop": "stone", "wood": None},
         "furniture": {"wood": "wood_veneer_oak_light", "fabric_colour": None,
                       "by_type": {"sofa": {"fabric_colour": "light grey", "colour": None, "material_tags": ["fabric"]},
                                   "table_coffee": {"fabric_colour": None, "colour": None,
                                                    "material_tags": ["glass"]}}}}


def _walls(*segments):
    return [{"id": f"w{i}", "level_id": "L0", "start": list(a), "end": list(b), "thickness": 0.2}
            for i, (a, b) in enumerate(segments)]


def test_design_for_reads_the_layout_design_first():
    given = {"front_style": "flat", "colour": None, "handle": None}
    design, notes = looks.design_for(_piece("kitchen_counter", given), STYLE)
    assert design == given and notes == ["furniture.design (layout stage)"]


def test_design_for_falls_back_to_the_style_and_the_rules():
    design, notes = looks.design_for(_piece("kitchen_counter"), STYLE)
    assert design["front_style"] == "shaker" and design["colour"] == "sage" and design["worktop"] == "stone"
    wall, _ = looks.design_for(_piece("wall_cabinet"), STYLE)
    assert "worktop" not in wall and wall["handle"] == "brass"
    sofa, _ = looks.design_for(_piece("sofa"), STYLE)
    assert sofa["fabric_colour"] == "light grey" and sofa["material_tags"] == ["fabric"]
    assert sofa["wood"] == "wood_veneer_oak_light"
    deep, notes = looks.design_for(_piece("washbasin", size=(0.6, 0.5)), STYLE)
    assert deep["vanity"] and deep["front_style"] == "shaker" and any("vanity" in n for n in notes)
    shallow, _ = looks.design_for(_piece("washbasin", size=(0.6, 0.4)), STYLE)
    assert "vanity" not in shallow
    # A wardrobe between two walls (its ends touch them) is built in; one that stands free is not.
    building = {"walls": _walls(((-0.9, -1.0), (-0.9, 1.0)), ((0.9, -1.0), (0.9, 1.0)))}
    wardrobe = _piece("wardrobe", size=(1.6, 0.6))
    built, notes = looks.design_for(wardrobe, STYLE, building)
    assert built.get("built_in") and any("built_in" in n for n in notes)
    free, _ = looks.design_for(wardrobe, STYLE, {"walls": _walls(((-0.9, -1.0), (-0.9, 1.0)))})
    assert "built_in" not in free
    turned = dict(wardrobe, footprint={"center": [0.0, 0.0], "size": [1.6, 0.6], "rotation_deg": 90.0}, front_deg=0.0)
    building_y = {"walls": _walls(((-1.0, -0.9), (1.0, -0.9)), ((-1.0, 0.9), (1.0, 0.9)))}
    assert looks.design_for(turned, STYLE, building_y)[0].get("built_in")


def test_design_overrides_give_the_material_keys():
    over, notes = F.design_overrides({"front_style": "shaker", "colour": "sage", "handle": "brass", "worktop": "terrazzo"},
                                     "kitchen_counter")
    assert over["front"]["slug"] == "painted_wood_white" and over["front"]["colour"] == "sage"
    assert over["handle"]["slug"] == "metal_brass" and over["worktop"]["slug"] == "terrazzo"
    assert "wood" not in over                                       # cabinets: only the fronts take the colour
    wood, _ = F.design_overrides({"wood": "wood_veneer_walnut"}, "sideboard")
    assert wood["front"]["slug"] == "wood_veneer_walnut" and wood["wood"]["asset"] == "walnut_veneer"
    sofa, _ = F.design_overrides({"fabric_colour": "light grey"}, "sofa")
    assert sofa["fabric"]["colour"] == sofa["duvet"]["colour"] == "light grey"
    table, _ = F.design_overrides({"colour": "black"}, "table_dining")
    assert table["wood"]["colour"] == "black"                       # a coloured table is painted
    assert F.design_overrides({"handle": "gold"}, "sideboard")[0] == {}
    keys, _ = F.style_material_keys(STYLE | {"floor": {"material": "concrete_polished"}})
    assert keys["wood"][0] == "wood_veneer_oak_light"               # the style's furniture wood wins
    assert {"front", "handle", "pot", "bulb", "marble", "rattan"} <= set(keys)


def test_lamps_turn_on_in_the_interior_evening_only():
    assert F.lamps_on({"lighting": {"mood": "interior evening"}})
    assert not F.lamps_on({"lighting": {"mood": "warm daylight"}}) and not F.lamps_on({})
    assert F.decor_lit({"type": "pendant_light"}, True) and not F.decor_lit({"type": "pendant_light"}, False)
    assert not F.decor_lit({"type": "pendant_light", "light_on": False}, True)
    assert not F.decor_lit({"type": "vase"}, True)
    parts = P.build_parts("floor_lamp", 0.4, 0.4, 1.6)
    x, y, z = F.lamp_light_point("floor_lamp", parts, (2.0, 3.0), 0.0, 0.0)
    shade = min(v[2] for p in parts if p["role"] == "shade" for v in p["verts"])
    assert (x, y) == (2.0, 3.0) and z == pytest.approx(shade - 0.05)
    pend = P.decor_parts("pendant_light", 0.45, 0.45, 0.7)
    assert F.lamp_light_point("pendant_light", pend, (0, 0), 0.0, 2.0)[2] < 2.0 + 0.1


# --------------------------------------------------------------------------
# A Blender scene with the looks
# --------------------------------------------------------------------------

def _scene_building() -> dict:
    ev = [{"file": "t.dxf", "method": "vector", "confidence": 1.0}]
    w, d, t = 8.0, 5.0, 0.2
    walls = [{"id": "w_s", "start": [-t / 2, -t / 2], "end": [w + t / 2, -t / 2]},
             {"id": "w_e", "start": [w + t / 2, -t / 2], "end": [w + t / 2, d + t / 2]},
             {"id": "w_n", "start": [w + t / 2, d + t / 2], "end": [-t / 2, d + t / 2]},
             {"id": "w_w", "start": [-t / 2, d + t / 2], "end": [-t / 2, -t / 2]},
             {"id": "w_m", "start": [4.0, 0.0], "end": [4.0, d]}]
    walls = [dict(x, level_id="L0", thickness=t, status="verified", evidence=ev, exterior=x["id"] != "w_m") for x in walls]
    rooms = [{"id": "r_kit", "label": "Kitchen", "room_type": "kitchen", "polygon": [[0, 0], [3.9, 0], [3.9, d], [0, d]]},
             {"id": "r_liv", "label": "Living", "room_type": "living", "polygon": [[4.1, 0], [w, 0], [w, d], [4.1, d]]}]
    rooms = [dict(r, level_id="L0", status="verified", evidence=ev, has_documented_furniture=True,
                  area_computed=1.0) for r in rooms]
    openings = [{"id": "win_1", "type": "window", "wall_id": "w_s", "center": [6.0, -0.1], "width": 1.6, "height": 1.3,
                 "sill_height": 0.9},
                {"id": "d_1", "type": "door", "wall_id": "w_m", "center": [4.0, 4.2], "width": 0.9, "height": 2.1,
                 "sill_height": 0.0, "operation": "sliding", "operation_source": "block_name"}]
    openings = [dict(o, level_id="L0", status="verified", evidence=ev) for o in openings]

    def piece(pid, ftype, room, center, size, rot=0.0, **extra):
        return dict({"id": pid, "level_id": "L0", "room_id": room, "type": ftype, "type_raw": None,
                     "source": "from_documents", "footprint": {"center": list(center), "size": list(size),
                                                               "rotation_deg": rot},
                     "front_deg": (270 + rot) % 360, "height": None, "asset": None, "status": "verified",
                     "evidence": ev}, **extra)

    furniture = [
        piece("f_run", "kitchen_counter", "r_kit", (1.6, 4.7), (3.0, 0.6), 0.0,
              design={"front_style": "shaker", "colour": "sage", "handle": "brass", "worktop": "stone"}),
        piece("f_wall", "wall_cabinet", "r_kit", (1.6, 4.825), (3.0, 0.35), 0.0, mount_bottom_m=1.45,
              source="added_by_ai", completes_room=True, method="rule",
              design={"front_style": "shaker", "colour": "sage", "handle": "brass"}),
        piece("f_tall", "tall_cabinet", "r_kit", (0.4, 0.6), (0.6, 0.6), 90.0),
        piece("f_sofa", "sofa_corner", "r_liv", (6.0, 4.2), (2.6, 1.6), 0.0, shape="L", chaise_side="right",
              chaise_depth=1.6, design={"fabric_colour": "light grey"}),
        piece("f_table", "table_coffee", "r_liv", (5.6, 2.6), (1.0, 0.6), 0.0, source="added_by_ai",
              completes_room=True, design={"material_tags": ["glass"]}),
        piece("f_lamp", "floor_lamp", "r_liv", (7.6, 0.4), (0.4, 0.4), 0.0),
    ]
    decor = [
        {"id": "dec_1", "kind": "decor", "type": "pendant_light", "level_id": "L0", "room_id": "r_liv",
         "center": [5.6, 2.6, 2.0], "size": [0.45, 0.45, 0.5], "rotation_deg": 0.0, "host_id": None,
         "anchor_ids": ["f_table"], "source": "added_by_ai", "method": "ai", "colour": "brass", "light_on": True},
        {"id": "dec_2", "kind": "decor", "type": "plant_large", "level_id": "L0", "room_id": "r_liv",
         "center": [7.55, 4.55], "size": [0.6, 0.6, 1.6], "rotation_deg": 0.0, "host_id": None,
         "species": "monstera", "pot": {"material": "rattan", "colour": "cream"}, "source": "added_by_ai",
         "method": "ai"},
        {"id": "dec_3", "kind": "decor", "type": "curtain", "level_id": "L0", "room_id": "r_liv",
         "center": [6.0, 0.1, 0.01], "size": [2.0, 0.08, 2.3], "rotation_deg": 0.0, "host_id": None,
         "window_id": "win_1", "source": "added_by_ai", "method": "ai", "colour": "cream"},
        {"id": "dec_4", "kind": "decor", "type": "cushion", "level_id": "L0", "room_id": "r_liv",
         "center": [5.2, 4.75], "size": [0.45, 0.15], "rotation_deg": 0.0, "host_id": "f_sofa",
         "source": "added_by_ai", "method": "rule", "colour": "mustard"},
    ]
    return {"schema_version": "0.1", "status": "ok", "project": {"id": "cabinets-test"},
            "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "walls": walls,
            "openings": openings, "rooms": rooms, "furniture": furniture, "decor": decor, "warnings": [],
            "unverified": []}


SCENE_STYLE = {
    "source_text": "test", "family": "modern",
    "floor": {"material": "wood_oak_light", "asset": None, "colour": None},
    "walls": {"material": "paint", "asset": None, "colour": "warm greige"},
    "wall_accent": {"material": "paint", "asset": None, "colour": "sage", "room_types": ["living", "bedroom"],
                    "rule": "test"},
    "ceiling": {"material": "plaster_white", "colour": None},
    "wet_floor": {"material": "tiles_light", "asset": None, "colour": None},
    "wet_walls": {"material": "tiles_subway", "asset": None, "tile_size_m": [0.2, 0.1], "pattern": "running_bond",
                  "colour": "white", "grout_colour": "charcoal"},
    "trim": {"material": "painted_wood_white", "colour": None},
    "door": {"material": "wood_oak_light", "asset": None, "style": "shaker_panel", "colour": None, "handle": "black"},
    "window_frame": {"material": "dark_bronze", "asset": None, "colour": None},
    "cabinets": {"front_style": None, "colour": None, "handle": None, "worktop": None, "wood": None},
    "furniture": {"wood": "wood_veneer_oak_light", "fabric_colour": None, "by_type": {}},
    "lighting": {"hdri": "sunset_jhbcentral", "sun_elevation_deg": -3, "sun_azimuth_deg": 285, "sun_strength": 0.0,
                 "colour_temperature_k": 3000, "mood": "interior evening"},
}


@pytest.fixture(scope="module")
def looks_scene(tmp_path_factory):
    pytest.importorskip("jsonschema")
    if BLENDER is None:
        pytest.skip("no Blender binary")
    tmp = tmp_path_factory.mktemp("cabinets_scene")
    (tmp / "building.json").write_text(json.dumps(_scene_building()), encoding="utf-8")
    (tmp / "style.json").write_text(json.dumps(SCENE_STYLE), encoding="utf-8")
    (tmp / "assets").mkdir()
    out = tmp / "scene"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(tmp / "building.json"), "--style", str(tmp / "style.json"),
                                             "--assets", str(tmp / "assets"), "--out", str(out), "--no-preview",
                                             "--no-glb"], log_path=out / "build.log")
    return json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))


@needs_blender
def test_scene_builds_the_designs_mounts_lights_and_accent_wall(looks_scene):
    from wenart.blender import schemas

    m = looks_scene
    schemas.validate_scene_manifest(m)
    objs = {o["name"]: o for o in m["objects"]}
    run = objs["furn_f_run"]
    assert run["design"]["front_style"] == "shaker" and run["material_keys"]["front"] == "painted_wood_white"
    assert run["material_keys"]["handle"] == "metal_brass" and run["material_keys"]["worktop"] == "stone_worktop"
    front = next(n for n in run["materials"] if n.startswith("painted_wood_white__sage"))
    assert m["materials"][front]["colour_applied"] and m["materials"][front]["colour"] == "sage"
    hung = objs["furn_f_wall"]
    assert hung["mount_bottom_m"] == pytest.approx(1.45) and hung["center"][2] == pytest.approx(1.45 + 0.35)
    tall = objs["furn_f_tall"]
    assert "design" not in tall or not tall["design"].get("front_style")       # no design, no style cabinets
    sofa = objs["furn_f_sofa"]
    assert sofa["l_shape"]["chaise_side"] == "right" and sofa["material_keys"]["fabric"] == "fabric_linen"
    assert any(n.startswith("fabric_linen") and "light_grey" in n for n in sofa["materials"])
    assert "thin_glass" in objs["furn_f_table"]["materials"]                   # the glass coffee table top
    assert objs["furn_f_lamp"]["light"]["energy_w"] == F.LAMP_LIGHTS["floor_lamp"][0]     # interior evening
    pend = next(o for o in m["objects"] if o.get("wenart_id") == "dec_1")
    assert pend["light"]["energy_w"] > 0 and any("lamp_light" in n for n in pend["materials"])
    assert pend["bbox_m"][2] == pytest.approx(0.7, abs=0.01)                   # the cord reaches the ceiling
    plant = next(o for o in m["objects"] if o.get("wenart_id") == "dec_2")
    assert plant["species"] == "monstera" and plant["pot"]["slug"] == "rattan"
    curtain = next(o for o in m["objects"] if o.get("wenart_id") == "dec_3")
    assert curtain["window_id"] == "win_1" and any("cream" in n for n in curtain["materials"])
    lights = [a for a in m["assumed"] if a.get("kind") == "light" and a.get("field") == "lamp_light"]
    assert {a["parent"] for a in lights} >= {"f_lamp", "dec_1"}
    accent = [o for o in m["objects"] if o.get("kind") == "wall" and o.get("accent")]
    assert [o["wenart_id"] for o in accent] == ["w_n"] and accent[0]["room_ids"] == ["r_liv"]
    assert "sofa corner f_sofa" in accent[0]["accent_reason"]
    walls = m["materials"]
    assert any(k.startswith("paint__warm_greige") for k in walls) and any(k.startswith("paint__sage") for k in walls)
    tiles = next(v for k, v in walls.items() if k.startswith("tiles_subway"))
    assert tiles["procedural"] == "wenart_tiles" and tiles["group"] == "wenart_tiles_running_bond"
    assert tiles["params"]["tile_size_m"] == [0.2, 0.1] and tiles["params"]["grout_colour"] == "charcoal"
