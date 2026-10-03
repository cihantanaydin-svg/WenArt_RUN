"""CPU tests of the Milestone 4 furniture path (docs/milestone4.md §2):
parametric meshes for every furniture type (bbox equals the footprint
within 1 cm, origin on the floor, headboard / back on +Y, fronts on -Y),
the glTF import with re-orientation and fit scale (a tiny GLB exported
from Blender inside the test, no download), fallbacks with their reasons,
the proxy box for ``unknown`` pieces and behind ``--proxies``, decor on
host pieces, the scene-manifest fields, and the camera planner working
with fitted boxes.

The pure parts (parametric parts, frame rotation, fitting maths, asset
resolution, decor rules) need no Blender; the scene tests are skipped with
a reason when no Blender binary is found.
"""
from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

import pytest

from wenart.blender import cameras, cli, geom2d, schemas
from wenart.blender import furniture as F
from wenart.blender import parametric as P
from wenart.blender.proxies import PROXY_HEIGHTS, proxy_height
from wenart.synthetic.blocks import BLOCKS

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "tests" / "fixtures" / "blender_style.json"
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, "
                                                           "/workspace/tools/blender, /opt/wenart/blender, PATH)")

# Footprints per type: the drawing block sizes of Milestone 2 plus the types
# no block draws.
SIZES = {t: (w, d) for _, (t, w, d) in BLOCKS.items()}
SIZES.update({"bed": (1.4, 2.0), "kitchen_island": (1.8, 0.9)})


# --------------------------------------------------------------------------
# Parametric parts (pure)
# --------------------------------------------------------------------------

def _parts_ok(ftype: str, w: float, d: float) -> list[dict]:
    h, _ = proxy_height(ftype, None)
    parts = P.build_parts(ftype, w, d, h)
    assert len(parts) >= 3, ftype
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert abs((x1 - x0) - w) <= 0.01 and abs((y1 - y0) - d) <= 0.01, (ftype, x1 - x0, y1 - y0)
    assert abs(z0) < 1e-9, (ftype, z0)                       # origin on the floor
    assert z1 >= h - 0.02, (ftype, z1, h)                     # at least the type height
    assert {p["key"] for p in parts} <= set(P.MATERIAL_KEYS)
    for p in parts:
        verts, faces = p["verts"], p["faces"]
        cx = sum(v[0] for v in verts) / len(verts)
        cy = sum(v[1] for v in verts) / len(verts)
        cz = sum(v[2] for v in verts) / len(verts)
        for f in faces:  # every part is convex: normals point away from its centre
            n = geom2d.face_normal(verts, f)
            c = geom2d.face_center(verts, f)
            assert n != (0.0, 0.0, 0.0), (ftype, p["role"])
            assert n[0] * (c[0] - cx) + n[1] * (c[1] - cy) + n[2] * (c[2] - cz) > 0, (ftype, p["role"], f)
        ys = [v[1] for v in verts]
        if p["role"] == "back":
            assert max(ys) == pytest.approx(d / 2.0, abs=1e-6), (ftype, "back parts touch +Y")
        if p["role"] in ("front", "handle"):
            assert max(ys) < 0.0 and min(ys) >= -d / 2.0 - 0.01, (ftype, p["role"], "front parts on -Y")
    return parts


@pytest.mark.parametrize("ftype", P.PARAMETRIC_TYPES)
def test_every_type_has_a_recognisable_parametric_mesh(ftype):
    w, d = SIZES[ftype]
    parts = _parts_ok(ftype, w, d)
    roles = {p["role"] for p in parts}
    expected = {
        # Milestone 6: soft bedding (superellipsoid mattress, duvet, turn-down band, pillows).
        "bed": {"back", "pillow", "mattress", "duvet", "turndown"}, "bed_single": {"back", "pillow", "duvet"},
        "bed_double": {"back", "pillow", "mattress", "duvet", "turndown"},
        "sofa": {"back", "arm", "cushion"}, "armchair": {"back", "arm", "cushion"},
        "table_dining": {"top", "leg"}, "table_coffee": {"top", "leg"}, "desk": {"top", "leg", "drawers", "handle"},
        "chair": {"top", "back", "leg"}, "wardrobe": {"front", "handle"}, "dresser": {"front", "handle"},
        "nightstand": {"front", "handle"}, "tv_unit": {"front", "handle"}, "bookshelf": {"back", "shelf", "side"},
        "kitchen_counter": {"plinth", "top", "front", "handle"}, "kitchen_island": {"plinth", "top", "front"},
        "fridge": {"handle"}, "stove": {"ring", "handle"}, "sink_kitchen": {"basin", "tap"},
        "washbasin": {"pedestal", "basin", "tap"}, "toilet": {"back", "bowl", "seat"},
        "shower": {"tray", "front", "side"}, "bathtub": {"basin", "tap"}, "washing_machine": {"front"},
    }[ftype]
    assert expected <= roles, (ftype, roles)
    if ftype == "sofa":
        assert sum(p["role"] == "cushion" for p in parts) == 2   # 1.6 m sofa: two seat cushions
    if ftype == "bed_double":
        assert sum(p["role"] == "pillow" for p in parts) == 2
    if ftype == "bed_single":
        assert sum(p["role"] == "pillow" for p in parts) == 1


def test_parametric_types_cover_the_schema_and_the_spec_table():
    schema = json.loads((ROOT / "wenart" / "schema" / "building.schema.json").read_text(encoding="utf-8"))
    types = set(schema["$defs"]["furniture"]["properties"]["type"]["enum"])
    assert types - {"unknown"} <= set(P.PARAMETRIC_TYPES)
    assert set(PROXY_HEIGHTS) - {"unknown"} <= set(P.PARAMETRIC_TYPES)
    with pytest.raises(KeyError, match="unknown"):
        P.build_parts("unknown", 1.0, 1.0, 0.8)
    # Milestone 7 (docs/milestone7.md §6.4): every schema type has a type height; the stair is fixed
    # equipment built with the shell (shell.build_stairs), never by furniture.create_furniture.
    assert types <= set(PROXY_HEIGHTS)
    assert {"stair", "side_table", "floor_lamp", "potted_plant"} <= set(P.PARAMETRIC_TYPES)
    assert P.SHELL_TYPES == ("stair",)
    assert PROXY_HEIGHTS["stair"] == pytest.approx(2.70 + P.STAIR_SLAB_M)


# Milestone 7 parametric types (docs/milestone7.md §6.4): footprints from the furniture size table.
M7_SIZES = {"stair": (1.0, 3.0), "side_table": (0.45, 0.45), "floor_lamp": (0.4, 0.4), "potted_plant": (0.4, 0.4)}


@pytest.mark.parametrize("ftype", sorted(M7_SIZES))
def test_milestone_7_types_fill_their_footprints(ftype):
    parts = _parts_ok(ftype, *M7_SIZES[ftype])
    roles = {p["role"] for p in parts}
    assert {"stair": {"step", "riser", "rail", "post"}, "side_table": {"top", "leg", "shelf"},
            "floor_lamp": {"base", "pole", "shade"}, "potted_plant": {"pot", "soil", "stem", "crown"}}[ftype] <= roles
    w, d = (0.6, 0.35) if ftype != "stair" else (1.2, 2.4)        # a non-square footprint is filled as well
    _parts_ok(ftype, w, d)


def test_side_table_is_round_only_when_the_building_says_so():
    square = P.build_parts("side_table", 0.43, 0.43, 0.55)
    assert {p["role"] for p in square} == {"top", "leg", "shelf"} and len(square) == 6
    for piece in ({"shape": "round"}, {"details": {"shape": "Round"}}, {"details": {"circle_fit": {"share": 0.93}}}):
        parts = P.build_parts("side_table", 0.43, 0.43, 0.55, piece=piece)
        assert P.piece_is_round(piece) and [p["role"] for p in parts] == ["top", "leg", "base"], piece
        top = parts[0]
        radii = {round(math.hypot(x, y), 6) for x, y, _ in top["verts"]}
        assert radii == {0.215}                                    # a disc filling the drawn 0.43 m footprint
    for piece in (None, {}, {"details": {"circle_fit": {"share": 0.85}}}, {"details": {"shape": "square"}},
                  {"details": {"circle_fit": 0.95}}):
        assert not P.piece_is_round(piece)
        assert len(P.build_parts("side_table", 0.43, 0.43, 0.55, piece=piece)) == 6
    # The round reading is the piece's own, never inferred from a square footprint: both have the same box.
    assert P.parametric_bbox("side_table", 0.43, 0.43, 0.55, piece={"shape": "round"}) == pytest.approx(
        P.parametric_bbox("side_table", 0.43, 0.43, 0.55))


def test_floor_lamp_has_a_fabric_shade_and_no_light():
    parts = P.build_parts("floor_lamp", 0.45, 0.45, 1.6)
    by_role = {p["role"]: p for p in parts}
    assert set(by_role) == {"base", "pole", "shade"}
    assert by_role["shade"]["key"] == "bedding" and by_role["pole"]["key"] == "steel"
    shade_z = [v[2] for v in by_role["shade"]["verts"]]
    assert max(shade_z) == pytest.approx(1.6) and min(shade_z) == pytest.approx(1.6 - 0.4)
    assert max(v[2] for v in by_role["pole"]["verts"]) > min(shade_z)       # the pole reaches into the shade
    assert not [p for p in parts if p["key"] in ("light", "emission") or p["role"] in ("light", "bulb")]


def test_potted_plant_is_the_decor_plant_at_the_drawn_size():
    parts = P.build_parts("potted_plant", 0.5, 0.4, 1.0)
    decor = P.decor_parts("plant", 0.4, 0.4, 0.6)
    assert [(p["role"], p["key"]) for p in parts] == [(p["role"], p["key"]) for p in decor]
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert (x1 - x0, y1 - y0, z0, z1) == pytest.approx((0.5, 0.4, 0.0, 1.0))      # not capped at DECOR_MAX_M


def test_stair_piece_box_is_the_drawn_footprint():
    """``piece_bbox`` (cameras, fitter, vision check) builds a stair from its drawn flights in the piece frame:
    the footprint, rising to the rails under the shaft cap (rise 2.85 m = the type height, cap 0.5 m above
    the assumed 2.70 m ceiling)."""
    from test_blender_geometry import FT, real01_stair_piece

    piece = real01_stair_piece()
    w, d, h, source = P.piece_bbox(piece)
    assert source == "parametric" and (w, d) == pytest.approx((8.0 * FT, 5.008 * FT), abs=1e-6)
    assert h == pytest.approx(2.70 + P.STAIR_SHAFT_CAP_M - P.STAIR_CAP_CLEARANCE)
    parts = P.build_parts("stair", 8.0 * FT, 5.008 * FT, 2.85, piece=piece)
    assert sum(p["role"] == "step" for p in parts) == 14 and sum(p["role"] == "landing" for p in parts) == 1
    # Local frame (rotation 90): the flights run along local X; rise directions turn with the frame.
    assert {tuple(round(c, 6) for c in p["rise_dir"]) for p in parts if p["role"] == "step"} == {(1.0, 0.0), (-1.0, 0.0)}


@pytest.mark.parametrize("ftype,size", [("chair", (0.4, 0.4)), ("nightstand", (0.4, 0.35)), ("toilet", (0.36, 0.6)),
                                        ("sink_kitchen", (0.5, 0.4)), ("washbasin", (0.45, 0.35)),
                                        ("wardrobe", (0.6, 0.55)), ("sofa", (1.2, 0.8))])
def test_small_footprints_still_fit(ftype, size):
    _parts_ok(ftype, *size)


def test_shapes_rise_above_the_type_height_where_they_should():
    assert P.parametric_bbox("bed_double", 1.6, 2.0, 0.55)[2] == pytest.approx(1.0)   # headboard
    assert P.parametric_bbox("toilet", 0.4, 0.7, 0.4)[2] == pytest.approx(0.8)         # tank
    assert P.parametric_bbox("wardrobe", 1.8, 0.6, 2.1)[2] == pytest.approx(2.1)
    assert P.parametric_bbox("sofa", 2.2, 0.9, 0.85)[2] == pytest.approx(0.85)


def test_world_mesh_rotates_and_lifts_the_parts():
    parts = P.build_parts("chair", 0.45, 0.45, 0.9)
    verts, faces, keys = P.world_mesh(parts, (3.0, 4.0), 90.0, floor_z=3.0)
    assert len(keys) == len(faces) and set(keys) == {"wood"}
    x0, y0, z0, x1, y1, z1 = P.local_bbox_of_world_points(verts, (3.0, 4.0), 90.0)
    assert (x1 - x0, y1 - y0) == pytest.approx((0.45, 0.45), abs=1e-9) and z0 == pytest.approx(3.0)
    # The back (local +Y) turned by 90 degrees points to world -X.
    back = next(p for p in parts if p["role"] == "back")
    bverts, _, _ = P.world_mesh([back], (3.0, 4.0), 90.0, 3.0)
    assert max(v[0] for v in bverts) < 3.0 - 0.15


# --------------------------------------------------------------------------
# Fitted boxes, cameras (pure)
# --------------------------------------------------------------------------

def _piece(fid, ftype, center, size, rotation=0.0, **extra):
    return dict({"id": fid, "type": ftype, "room_id": "r", "level_id": "L0", "front_deg": 270.0 + rotation,
                 "source": "from_documents", "status": "verified",
                 "footprint": {"center": list(center), "size": list(size), "rotation_deg": rotation},
                 "evidence": [{"file": "plan.dxf", "method": "vector", "confidence": 1.0}]}, **extra)


def _library_asset(bbox, scale=(1.0, 1.0, 1.0), **extra):
    return dict({"library": "polyhaven", "asset_id": "test_cube", "licence": "CC0", "method": "library",
                 "fit_scale": list(scale), "bbox_m": list(bbox), "file": "models/test_cube/test_cube.glb",
                 "front_axis": "+X", "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0]}, **extra)


def test_piece_bbox_uses_the_fitted_or_parametric_box():
    bed = _piece("b", "bed_double", (0, 0), (1.6, 2.0))
    *box, source = P.piece_bbox(bed)
    assert box == pytest.approx([1.6, 2.0, 1.0]) and source == "parametric"
    # asset.bbox_m is the fitted box (the fitter already applied fit_scale): no second scaling
    lib = _piece("a", "tv_unit", (0, 0), (1.6, 0.45), asset=_library_asset([1.6, 0.45, 1.2], (1.0, 1.0, 1.5)))
    *box, source = P.piece_bbox(lib)
    assert box == pytest.approx([1.6, 0.45, 1.2]) and source == "library"
    unknown = _piece("u", "unknown", (0, 0), (1.0, 0.5))
    assert P.piece_bbox(unknown) == (1.0, 0.5, 0.8, "proxy")
    small = _piece("s", "chair", (0, 0), (0.5, 0.5), asset=_library_asset([0.4, 0.4, 0.9]))  # box smaller than drawn
    assert P.obstacle_rect(small)["size"] == [0.5, 0.5]
    assert P.obstacle_rect(lib)["size"] == [1.6, 0.45]


def _room(furniture=()) -> dict:
    t, h, size = 0.25, 0.125, 4.0
    walls = [
        {"id": "w_s", "level_id": "L0", "start": [-t, -h], "end": [size + t, -h], "thickness": t},
        {"id": "w_e", "level_id": "L0", "start": [size + h, -t], "end": [size + h, size + t], "thickness": t},
        {"id": "w_n", "level_id": "L0", "start": [size + t, size + h], "end": [-t, size + h], "thickness": t},
        {"id": "w_w", "level_id": "L0", "start": [-h, size + t], "end": [-h, -t], "thickness": t},
    ]
    openings = [
        {"id": "win", "level_id": "L0", "type": "window", "wall_id": "w_s", "width": 1.5, "center": [2.0, -h]},
        {"id": "door", "level_id": "L0", "type": "door", "wall_id": "w_e", "width": 0.9, "center": [size + h, 1.0]},
    ]
    return {"levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "walls": walls,
            "openings": openings, "rooms": [{"id": "r", "level_id": "L0", "polygon": [[0, 0], [4, 0], [4, 4], [0, 4]]}],
            "furniture": list(furniture)}


def test_door_camera_avoids_a_tall_fitted_asset_but_not_a_low_parametric_one():
    # No camera stands in any footprint (Milestone 3 rule): a 0.5 m tv_unit
    # 0.2 m inside the door moves the door camera just like one whose fitted
    # asset is 1.6 m tall; both moves are recorded.
    low = _piece("tv", "tv_unit", (3.5, 1.0), (0.6, 1.2))
    tall = _piece("tv", "tv_unit", (3.5, 1.0), (0.6, 1.2), asset=_library_asset([0.6, 1.2, 1.6]))
    for piece in (low, tall):
        plan = {p["index"]: p for p in cameras.plan_cameras(_room([piece]), "L0")}[2]
        fp = piece["footprint"]
        assert geom2d.distance_to_rect(plan["position"][:2], fp["center"], fp["size"], fp["rotation_deg"]) \
            >= cameras.CAMERA_OBSTACLE_CLEARANCE - 1e-6
        assert plan["warning"] is not None
    # Centroid fallback: only a box taller than the camera forbids the centroid.
    centre_low = _piece("c", "table_coffee", (2.0, 2.0), (3.9, 3.9))
    centre_tall = _piece("c", "table_coffee", (2.0, 2.0), (3.9, 3.9), asset=_library_asset([3.9, 3.9, 1.5]))
    assert cameras.plan_cameras(_room([centre_low]), "L0")[0]["position"][:2] == pytest.approx([2.0, 2.0])
    plans = cameras.plan_cameras(_room([centre_tall]), "L0")
    assert all("INSIDE" in (p["warning"] or "") for p in plans)   # nothing else is free: said loudly


def test_decor_entries_among_the_furniture_are_ignored_by_the_cameras():
    sofa = _piece("s", "sofa", (2.0, 3.5), (2.2, 0.9))
    cushion = dict(_piece("d", "sofa", (2.0, 2.0), (3.9, 3.9)), kind="decor")
    plans = cameras.plan_cameras(_room([sofa, cushion]), "L0")
    assert all(p["warning"] is None for p in plans) and all("d" not in p["visible_furniture"] for p in plans)


# --------------------------------------------------------------------------
# Frame rotation, fitting maths, asset resolution, materials, decor (pure)
# --------------------------------------------------------------------------

@pytest.mark.parametrize("front,up", [("-Y", "+Z"), ("+X", "+Z"), ("+Y", "+Z"), ("-X", "+Z"), ("-Z", "+Y"), ("+Y", "-Z")])
def test_frame_rotation_maps_front_to_minus_y_and_up_to_plus_z(front, up):
    R = F.frame_rotation(front, up)
    assert F.apply_rotation(R, F.AXES[front]) == pytest.approx((0.0, -1.0, 0.0))
    assert F.apply_rotation(R, F.AXES[up]) == pytest.approx((0.0, 0.0, 1.0))
    det = (R[0][0] * (R[1][1] * R[2][2] - R[1][2] * R[2][1]) - R[0][1] * (R[1][0] * R[2][2] - R[1][2] * R[2][0])
           + R[0][2] * (R[1][0] * R[2][1] - R[1][1] * R[2][0]))
    assert det == pytest.approx(1.0)   # a proper rotation, never a mirror
    with pytest.raises(ValueError):
        F.frame_rotation("+Z", "+Z")


def test_fit_vertices_recentres_scales_and_places():
    # a box 0.5 (x) by 0.8 (y) by 0.9 (z) with its corner at (1, 2, 3), front +X
    verts = [(1 + x, 2 + y, 3 + z) for x in (0, 0.5) for y in (0, 0.8) for z in (0, 0.9)]
    asset = {"front_axis": "+X", "up_axis": "+Z", "fit_scale": [1.2, 1.0, 1.1]}
    world, info = F.fit_vertices(verts, asset, {"center": [10.0, 20.0], "size": [0.96, 0.5], "rotation_deg": 90.0},
                                 floor_z=3.0)
    assert info["bbox_raw_m"] == pytest.approx([0.8, 0.5, 0.9]) and info["bbox_m"] == pytest.approx([0.96, 0.5, 0.99])
    assert info["fit_scale"] == [1.2, 1.0, 1.1] and info["origin_offset_applied"] == pytest.approx([-2.4, 1.25, -3.0])
    x0, y0, z0, x1, y1, z1 = P.local_bbox_of_world_points(world, (10.0, 20.0), 90.0)
    assert (x1 - x0, y1 - y0, z1 - z0) == pytest.approx((0.96, 0.5, 0.99))
    assert (x0 + x1) / 2 == pytest.approx(10.0) and (y0 + y1) / 2 == pytest.approx(20.0) and z0 == pytest.approx(3.0)
    # decor: scaled to a target size, height from the mean of x and y when not given
    world, info = F.fit_vertices(verts, {"front_axis": "+X"}, {"center": [0, 0], "size": [0.4, 0.25], "rotation_deg": 0},
                                 0.0, target_size=[0.4, 0.25])
    assert info["fit_scale"] == pytest.approx([0.5, 0.5, 0.5]) and info["bbox_m"] == pytest.approx([0.4, 0.25, 0.45])


def test_resolve_asset_reasons(tmp_path):
    assert F.resolve_asset(None, str(tmp_path)) == (None, "no asset in the building JSON")
    assert F.resolve_asset({"library": "parametric", "method": "parametric"}, str(tmp_path))[1].startswith("fitting chose")
    lib = _library_asset([1, 1, 1])
    assert "missing" in F.resolve_asset(lib, str(tmp_path))[1]
    assert "not CC0" in F.resolve_asset(dict(lib, licence="CC-BY"), str(tmp_path))[1]
    assert "not CC0" in F.resolve_asset(dict(lib, license="CC-BY-4.0", licence=None), str(tmp_path))[1]
    f = tmp_path / "models" / "test_cube" / "test_cube.glb"
    f.parent.mkdir(parents=True)
    f.write_bytes(b"glTF")
    assert F.resolve_asset(lib, str(tmp_path)) == (f, None)
    assert F.resolve_asset(dict(lib, file=str(f)), None) == (f, None)                    # absolute path
    assert F.resolve_asset({k: v for k, v in lib.items() if k != "file"}, str(tmp_path)) == (f, None)  # by id


def test_style_material_keys_follow_the_style():
    style = json.loads(STYLE.read_text(encoding="utf-8"))
    keys, assumed = F.style_material_keys(style)
    # Milestone 6: furniture wood = the veneer of the floor's wood tone (not the floor planks), the
    # fabrics carry the Poly Haven linen weave (flat albedo mode), the duvet the textile.
    assert style["floor"]["material"] == "wood_oak_light" and keys["wood"] == ("wood_veneer_oak", "oak_veneer_01", None)
    assert keys["fabric"] == ("fabric_linen", "rough_linen", None) and [a["field"] for a in assumed] == ["fabric"]
    assert keys["duvet"] == keys["fabric"] and keys["bedding"] == ("fabric_white", "rough_linen", None)
    assert keys["painted"][0] == "painted_wood_white" and keys["ceramic"][0] == "ceramic_white"
    walnut, _ = F.style_material_keys({"floor": {"material": "wood_walnut"}})
    assert walnut["wood"] == ("wood_veneer_walnut", "walnut_veneer", None)
    keys, assumed = F.style_material_keys({"floor": {"material": "concrete_polished"},
                                           "textiles": {"material": "carpet"}})
    assert keys["wood"] == ("wood_veneer_oak", "oak_veneer_01", None) and keys["fabric"][0] == "carpet"
    assert keys["duvet"][0] == "carpet" and [a["field"] for a in assumed] == ["wood"]
    from wenart.style import vocabulary as V
    for key in P.MATERIAL_KEYS:
        slug = keys[key][0]
        assert slug == "glass" or slug in V.FLAT_COLOURS and slug in V.ROUGHNESS, slug


def test_decor_rules():
    assert P.decor_size("cushion", [0.45, 0.45]) == (0.45, 0.45, 0.12)
    assert P.decor_size("plant", [0.9, 0.9, 1.5]) == (0.6, 0.6, 0.6)          # capped at 0.6 m
    assert P.decor_rest_height("sofa", 0.85, "cushion") == pytest.approx(0.45)
    assert P.decor_rest_height("bed_double", 0.55, "cushion") == pytest.approx(0.55)      # library bed: type height
    # A parametric bed (its footprint given): on the soft bedding top (Milestone 6), above the type height.
    top = P.bedding_top(1.6, 2.0, 0.55)
    assert P.decor_rest_height("bed_double", 0.55, "cushion", (1.6, 2.0)) == pytest.approx(top, abs=1e-4)
    assert 0.65 < top < 1.0
    assert P.decor_rest_height("bookshelf", 1.8, "book_set") == pytest.approx(0.7)
    assert P.decor_rest_height("desk", 0.75, "book_set") == pytest.approx(0.75)
    assert P.decor_rest_height("sofa", 0.85, "plant") == 0.0
    for dtype in P.DECOR_TYPES:
        parts = P.decor_parts(dtype, 0.4, 0.3, 0.2)
        x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
        assert x1 - x0 <= 0.4 + 1e-9 and y1 - y0 <= 0.3 + 1e-9 and z1 - z0 <= 0.2 + 1e-9 and z0 == 0.0
    building = {"furniture": [_piece("s", "sofa", (0, 0), (2, 1)), dict(_piece("b", "bed_double", (0, 0), (1.6, 2)),
                                                                        level_id="L1", decor=[{"type": "plant"}])],
                "decor": [{"type": "cushion", "host_id": "s"}, {"type": "cushion", "host_id": "nope"},
                          {"type": "book_set", "host_id": "b"}]}
    assert [(i["type"], h["id"]) for i, h in F.collect_decor(building, "L0")] == [("cushion", "s")]
    assert [(i["type"], h["id"]) for i, h in F.collect_decor(building, "L1")] == [("book_set", "b"), ("plant", "b")]
    assert F.unknown_decor_hosts(building) == ["nope"]
    assert F.decor_height_above_floor({"type": "cushion", "center": [0, 0, 0.3]}, building["furniture"][0]) == (0.3, "center[2]")
    assert F.decor_height_above_floor({"type": "cushion", "center": [0, 0]}, building["furniture"][0])[0] == pytest.approx(0.45)


# --------------------------------------------------------------------------
# Blender: a hand-made building with every type, a tiny GLB, decor
# --------------------------------------------------------------------------

GLB_SCRIPT = textwrap.dedent("""
    import bpy, sys
    out = sys.argv[sys.argv.index("--") + 1]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    def box(name, lo, hi, colour):
        verts = [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        faces = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
        me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
        uv = me.uv_layers.new(name="UVMap")
        for i, loop in enumerate(uv.data):
            loop.uv = ((i % 4) / 4.0, (i // 4) / 6.0)   # any UVs: the import must carry them over
        mat = bpy.data.materials.new(name + "_mat"); mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = colour
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
        return ob
    # part A spans x 1..1.5, y 2..2.8, z 3..3.9; part B sits inside it under an empty parent
    a = box("cube_a", (1.0, 2.0, 3.0), (1.5, 2.8, 3.9), (0.8, 0.1, 0.1, 1.0))
    parent = bpy.data.objects.new("cube_root", None); bpy.context.scene.collection.objects.link(parent)
    parent.location = (0.1, 0.1, 0.5)
    b = box("cube_b", (1.0, 2.0, 3.0), (1.2, 2.2, 3.2), (0.1, 0.1, 0.8, 1.0))
    b.parent = parent
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_yup=True, export_apply=True)
""")

DUMP_SCRIPT = textwrap.dedent("""
    import bpy, json, sys
    out = sys.argv[sys.argv.index("--") + 1]
    rows = []
    for ob in bpy.data.objects:
        row = {"name": ob.name, "type": ob.type, "kind": ob.get("wenart_kind"), "status": ob.get("wenart_status"),
               "wenart_id": ob.get("wenart_id"), "pass_index": ob.pass_index,
               "props": {k: ob.get(k) for k in ("wenart_type", "wenart_source", "wenart_asset", "wenart_host")}}
        if ob.type == "MESH":
            pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
            row["bounds"] = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
            row["verts"] = [list(p) for p in pts] if len(pts) <= 64 else []
            row["uv"] = [l.name for l in ob.data.uv_layers]
            row["uv_render"] = ob.data.uv_layers.active_render.name if ob.data.uv_layers else None
            row["uv_active"] = ob.data.uv_layers.active.name if ob.data.uv_layers.active else None
            row["materials"] = [m.name if m else None for m in ob.data.materials]
        rows.append(row)
    mats = {}
    for m in bpy.data.materials:
        nodes = m.node_tree.nodes if m.use_nodes and m.node_tree else []
        mats[m.name] = {"stripes": any(n.bl_idname == "ShaderNodeTexWave" for n in nodes),
                        "images": any(n.bl_idname == "ShaderNodeTexImage" for n in nodes)}
    json.dump({"objects": rows, "materials": mats, "collections": [c.name for c in bpy.data.collections]},
              open(out, "w"))
""")


def _building(assets_dir: Path) -> dict:
    """One 12 x 8 m room with every parametric type on a grid, library
    pieces using the test GLB, two fallbacks, one unknown piece, decor."""
    W, D = 12.0, 8.0
    t = 0.25
    walls = [
        {"id": "w_s", "level_id": "L0", "start": [-t, -t / 2], "end": [W + t, -t / 2], "thickness": t},
        {"id": "w_e", "level_id": "L0", "start": [W + t / 2, -t], "end": [W + t / 2, D + t], "thickness": t},
        {"id": "w_n", "level_id": "L0", "start": [W + t, D + t / 2], "end": [-t, D + t / 2], "thickness": t},
        {"id": "w_w", "level_id": "L0", "start": [-t / 2, D + t], "end": [-t / 2, -t], "thickness": t},
    ]
    ev = [{"file": "plan.dxf", "method": "vector", "confidence": 1.0, "layer": "DUVAR"}]
    for w in walls:
        w.update({"status": "verified", "evidence": ev, "exterior": True})
    openings = [
        {"id": "d_1", "level_id": "L0", "type": "door", "wall_id": "w_e", "width": 0.9, "center": [W + t / 2, 1.0],
         "height": None, "sill_height": None, "status": "verified", "evidence": ev},
        {"id": "win_1", "level_id": "L0", "type": "window", "wall_id": "w_s", "width": 1.8, "center": [6.0, -t / 2],
         "height": None, "sill_height": None, "status": "verified", "evidence": ev},
    ]
    room = {"id": "r_L0_salon", "level_id": "L0", "label": "salon", "room_type": "living",
            "polygon": [[0, 0], [W, 0], [W, D], [0, D]], "area_computed": W * D, "status": "verified",
            "has_documented_furniture": True, "evidence": ev}
    furniture = []
    x, y, row_h = 1.2, 1.4, 0.0
    for i, ftype in enumerate(P.PARAMETRIC_TYPES):
        w, d = SIZES[ftype]
        rot = 90.0 if ftype in ("bed_single", "desk", "fridge") else (30.0 if ftype == "chair" else 0.0)
        span = max(w, d) + 0.5
        if x + span > W - 0.6:
            x, y, row_h = 1.2, y + row_h + 0.3, 0.0
        piece = _piece(f"f_{i:02d}", ftype, (x + span / 2, y), (w, d), rot)
        if ftype == "sofa":
            piece["status"] = "unverified"
        furniture.append(piece)
        x += span
        row_h = max(row_h, span)
    furniture += [
        _piece("f_lib", "armchair", (9.0, 6.5), (0.96, 0.5), 0.0,
               asset=_library_asset([0.8, 0.5, 0.9], (1.2, 1.0, 1.1))),
        _piece("f_lib_rot", "chair", (10.8, 6.5), (0.8, 0.5), 90.0, status="unverified",
               asset=_library_asset([0.8, 0.5, 0.9])),
        _piece("f_missing", "tv_unit", (7.0, 6.5), (1.6, 0.45), 0.0,
               asset=_library_asset([1.6, 0.45, 0.5], file="models/nope/nope.glb")),
        _piece("f_licence", "nightstand", (4.5, 6.5), (0.5, 0.4), 0.0,
               asset=_library_asset([0.5, 0.4, 0.5], licence="CC-BY")),
        dict(_piece("f_unknown", "unknown", (2.0, 6.5), (1.2, 0.6), 0.0), status="unverified"),
    ]
    sofa = next(f for f in furniture if f["type"] == "sofa")
    desk = next(f for f in furniture if f["type"] == "desk")
    bed = next(f for f in furniture if f["type"] == "bed_double")
    decor = [
        {"type": "cushion", "host_id": sofa["id"], "center": [sofa["footprint"]["center"][0] - 0.5,
                                                                sofa["footprint"]["center"][1] + 0.1],
         "rotation_deg": 0.0, "size": [0.45, 0.45], "asset": None},
        {"type": "plant", "host_id": sofa["id"], "center": [sofa["footprint"]["center"][0] + 1.6,
                                                              sofa["footprint"]["center"][1]],
         "rotation_deg": 0.0, "size": [0.9, 0.9, 1.4], "asset": None},
        {"type": "book_set", "host_id": desk["id"], "center": list(desk["footprint"]["center"]), "rotation_deg": 90.0,
         "size": [0.3, 0.15, 0.22], "asset": None},
        {"type": "cushion", "host_id": bed["id"], "center": [bed["footprint"]["center"][0],
                                                              bed["footprint"]["center"][1] + 0.5],
         "rotation_deg": 0.0, "size": [0.4, 0.25], "asset": _library_asset([0.8, 0.5, 0.9], asset_id="test_cube")},
        {"type": "cushion", "host_id": "f_nope", "center": [1, 1], "rotation_deg": 0.0, "size": [0.4, 0.4],
         "asset": None},
        # a potted plant on the floor: no host (decor.py writes host_id None for plants)
        {"id": "dec_L0_001", "kind": "decor", "type": "plant", "level_id": "L0", "room_id": "r_L0_salon",
         "center": [0.3, 0.3], "rotation_deg": 0.0, "size": [0.4, 0.4], "asset": None, "host_id": None},
    ]
    return {"schema_version": "0.1", "status": "ok", "project": {"id": "furniture-test"},
            "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}],
            "walls": walls, "openings": openings, "rooms": [room], "furniture": furniture, "decor": decor,
            "warnings": [], "unverified": ["f_unknown"]}


@pytest.fixture(scope="module")
def glb(tmp_path_factory) -> Path:
    tmp = tmp_path_factory.mktemp("glb")
    assets = tmp / "assets"
    out = assets / "models" / "test_cube" / "test_cube.glb"
    out.parent.mkdir(parents=True)
    (tmp / "make_glb.py").write_text(GLB_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "make_glb.py", [str(out)])
    assert out.stat().st_size > 500
    return assets


def _build(tmp: Path, assets: Path, extra=()) -> dict:
    building = _building(assets)
    path = tmp / "building.json"
    path.write_text(json.dumps(building), encoding="utf-8")
    out = tmp / "scene"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(path), "--style", str(STYLE), "--assets", str(assets),
                                             "--out", str(out), "--no-textures", "--no-preview", "--no-glb", *extra],
                    log_path=out / "build.log")
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    (tmp / "dump.py").write_text(DUMP_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "dump.py", [str(tmp / "dump.json")], blend=str(out / "scene.blend"))
    dump = json.loads((tmp / "dump.json").read_text(encoding="utf-8"))
    return {"building": building, "manifest": manifest, "objects": {o["name"]: o for o in dump["objects"]},
            "materials": dump["materials"], "collections": dump["collections"], "out": out}


@pytest.fixture(scope="module")
def scene(tmp_path_factory, glb):
    pytest.importorskip("jsonschema")
    return _build(tmp_path_factory.mktemp("furniture_scene"), glb)


@needs_blender
def test_manifest_validates_and_summarises_the_furniture(scene):
    m = scene["manifest"]
    schemas.validate_scene_manifest(m)
    s = m["furniture"]
    assert s["pieces"] == len(scene["building"]["furniture"]) and s["proxies"] == 1 and s["decor"] == 5
    assert s["by_method"] == {"proxy": 1, "library": 2, "parametric": len(P.PARAMETRIC_TYPES) + 2}
    reasons = {f["id"]: f["reason"] for f in s["fallbacks"]}
    assert set(reasons) == {f["id"] for f in scene["building"]["furniture"]
                            if f["type"] != "unknown" and f["id"] not in ("f_lib", "f_lib_rot")}
    assert reasons["f_missing"].startswith("asset file missing: ") and reasons["f_missing"].endswith("nope.glb")
    assert "not CC0" in reasons["f_licence"]
    assert all(reasons[f["id"]] == "no asset in the building JSON" for f in scene["building"]["furniture"]
               if f.get("asset") is None and f["type"] != "unknown")
    assert [w for w in m["warnings"] if w.startswith("f_missing:") and "parametric mesh used" in w]
    assert [w for w in m["warnings"] if w.startswith("f_licence:") and "not CC0" in w]
    assert not [w for w in m["warnings"] if "differs from the footprint" in w]
    assert {a["field"] for a in m["assumed"] if a["object"] == "furniture"} == {"fabric"}


@needs_blender
def test_parametric_pieces_sit_on_their_footprints(scene):
    m, objects = scene["manifest"], scene["objects"]
    entries = {o["element_id"]: o for o in m["objects"] if o["kind"] == "furniture"}
    for piece in scene["building"]["furniture"]:
        if piece.get("asset") is not None and piece["id"] in ("f_lib", "f_lib_rot") or piece["type"] == "unknown":
            continue
        e = entries[piece["id"]]
        ob = objects[f"furn_{piece['id']}"]
        fp = piece["footprint"]
        assert e["name"] == ob["name"] and ob["kind"] == "furniture" and ob["wenart_id"] == piece["id"]
        assert e["method"].startswith("parametric (fallback: ") and e["fit_scale"] == [1.0, 1.0, 1.0]
        assert ob["props"]["wenart_asset"] == "parametric" and ob["props"]["wenart_type"] == piece["type"]
        assert ob["props"]["wenart_source"] == "from_documents"
        assert "box_m" in ob["uv"] and None not in ob["materials"]
        # Milestone 3 fields are kept: centre, size (type height), rotation, front, assumed height.
        assert e["center"][:2] == pytest.approx(fp["center"]) and e["size"][:2] == pytest.approx(fp["size"])
        assert e["rotation_deg"] == fp["rotation_deg"] and e["front_deg"] == piece["front_deg"]
        assert e["assumed"]["height"] == e["size"][2] == proxy_height(piece["type"], None)[0]
        # The real box (bbox_m) equals the footprint within 1 cm and stands on the floor.
        bx, by, bz = e["bbox_m"]
        assert abs(bx - fp["size"][0]) <= 0.01 and abs(by - fp["size"][1]) <= 0.01 and bz >= e["size"][2] - 0.02
        (x0, x1), (y0, y1), (z0, z1) = ob["bounds"]
        assert z0 == pytest.approx(0.0, abs=1e-4) and z1 == pytest.approx(bz, abs=1e-4)
        rad = math.radians(fp["rotation_deg"])
        ext_x = abs(bx * math.cos(rad)) + abs(by * math.sin(rad))
        ext_y = abs(bx * math.sin(rad)) + abs(by * math.cos(rad))
        assert (x1 - x0, y1 - y0) == pytest.approx((ext_x, ext_y), abs=0.011), piece["id"]
        assert ((x0 + x1) / 2, (y0 + y1) / 2) == pytest.approx(fp["center"], abs=0.011), piece["id"]
        assert e["pass_index"] == ob["pass_index"] == m["pass_index"][piece["id"]]
    sofa = entries[next(f["id"] for f in scene["building"]["furniture"] if f["type"] == "sofa")]
    assert sofa["status"] == "unverified" and all(m.endswith("__unverified") for m in sofa["materials"])
    assert all(scene["materials"][name]["stripes"] for name in sofa["materials"])
    shower = entries[next(f["id"] for f in scene["building"]["furniture"] if f["type"] == "shower")]
    assert "thin_glass" in shower["materials"] and shower["material_keys"]["glass"] == "glass"  # thin pane: the index pass sees through
    bed = entries[next(f["id"] for f in scene["building"]["furniture"] if f["type"] == "bed_double")]
    assert bed["material_keys"] == {"wood": "wood_veneer_oak", "bedding": "fabric_white", "duvet": "fabric_linen"}
    assert bed["bbox_m"][2] == pytest.approx(1.0) and bed["size"][2] == 0.55
    # Milestone 6: one Bevel modifier per parametric piece, recorded; the bedding is a design detail.
    assert bed["bevel"]["width_m"] == P.BEVEL_WIDTH_M and bed["bevel"]["segments"] == P.BEVEL_SEGMENTS
    assert bed["bevel"]["edges"] > 0 and 0 < bed["bevel"]["max_radius_m"] <= P.BEVEL_WIDTH_M
    assert "bedding" in bed["assumed"]


@needs_blender
def test_library_asset_is_imported_oriented_fitted_and_placed(scene):
    m, objects = scene["manifest"], scene["objects"]
    e = next(o for o in m["objects"] if o["element_id"] == "f_lib")
    ob = objects["furn_f_lib"]
    assert e["method"] == "library" and e["fit_scale"] == [1.2, 1.0, 1.1] and e["asset"]["asset_id"] == "test_cube"
    assert e["bbox_m"] == pytest.approx([0.96, 0.5, 0.99], abs=1e-3)
    assert e["fit"]["bbox_raw_m"] == pytest.approx([0.8, 0.5, 0.9], abs=1e-3)   # catalogue box after re-orientation
    assert e["fit"]["front_axis"] == "+X" and e["file"].endswith("test_cube.glb")
    assert sorted(e["imported_objects"]) == ["cube_a", "cube_b", "cube_root"]
    (x0, x1), (y0, y1), (z0, z1) = ob["bounds"]
    assert (x1 - x0, y1 - y0, z1 - z0) == pytest.approx((0.96, 0.5, 0.99), abs=1e-3)
    assert ((x0 + x1) / 2, (y0 + y1) / 2, z0) == pytest.approx((9.0, 6.5, 0.0), abs=1e-3)
    assert ob["kind"] == "furniture" and ob["props"]["wenart_asset"] == "test_cube" and ob["wenart_id"] == "f_lib"
    assert set(ob["materials"]) == {"cube_a_mat", "cube_b_mat"} == set(e["materials"]) and e["textured"] is False
    # One import per file and build: three pieces use the GLB, no "cube_a_mat.001" copies appear.
    assert not [n for n in scene["materials"] if n.startswith("cube_") and ".00" in n], sorted(scene["materials"])
    assert "box_m" in ob["uv"] and ob["uv_active"] == "UVMap"   # the asset's own UVs stay active
    assert ob["uv_render"] == "UVMap"                             # ... and are what the textures sample
    assert e["pass_index"] == ob["pass_index"] == m["pass_index"]["f_lib"]
    # The imported source objects and the importer's collection are gone.
    assert not {"cube_a", "cube_b", "cube_root"} & set(objects)
    assert not [c for c in scene["collections"] if "test_cube" in c]
    # Both cubes are in the merged mesh: the glTF exporter splits a UV-mapped
    # cube into 24 per-face vertices, so 2 x 24.
    assert len(ob["verts"]) == 48
    # A fitted piece is counted as library, not as a fallback.
    assert "f_lib" not in {f["id"] for f in m["furniture"]["fallbacks"]}


@needs_blender
def test_rotated_unverified_library_piece_keeps_stripes_on_copied_materials(scene):
    m, objects = scene["manifest"], scene["objects"]
    e = next(o for o in m["objects"] if o["element_id"] == "f_lib_rot")
    ob = objects["furn_f_lib_rot"]
    (x0, x1), (y0, y1), (z0, z1) = ob["bounds"]
    assert (x1 - x0, y1 - y0, z1 - z0) == pytest.approx((0.5, 0.8, 0.9), abs=1e-3)   # 90 degrees: width along Y
    assert ((x0 + x1) / 2, (y0 + y1) / 2, z0) == pytest.approx((10.8, 6.5, 0.0), abs=1e-3)
    assert e["status"] == ob["status"] == "unverified"
    assert set(ob["materials"]) == {"cube_a_mat__unverified", "cube_b_mat__unverified"}
    assert all(scene["materials"][n]["stripes"] for n in ob["materials"])
    assert not scene["materials"]["cube_a_mat"]["stripes"]   # the verified piece's materials are untouched
    assert e["bbox_m"] == pytest.approx([0.8, 0.5, 0.9], abs=1e-3)


@needs_blender
def test_unknown_piece_keeps_the_striped_proxy_box(scene):
    m, objects = scene["manifest"], scene["objects"]
    e = next(o for o in m["objects"] if o["wenart_id"] == "proxy:f_unknown")
    ob = objects["proxy_f_unknown"]
    assert e["kind"] == ob["kind"] == "furniture_proxy" and e["material"] == "proxy_unverified"
    assert e["pass_index"] == ob["pass_index"] == m["pass_index"]["proxy:f_unknown"]
    assert "furn_f_unknown" not in objects
    assert e["size"] == [1.2, 0.6, 0.8] and e["assumed"]["height"] == 0.8


@needs_blender
def test_decor_sits_on_its_hosts_and_shares_their_pass_index(scene):
    m, objects = scene["manifest"], scene["objects"]
    building = scene["building"]
    decor = [o for o in m["objects"] if o["kind"] == "decor"]
    assert len(decor) == 5 and all(o["source"] == "added_by_ai" and o["status"] == "assumed" for o in decor)
    # The hostless plant stands on the floor with its own id and pass index.
    (floor_plant,) = [o for o in decor if o["host_id"] is None]
    assert floor_plant["wenart_id"] == floor_plant["element_id"] == "dec_L0_001" and floor_plant["type"] == "plant"
    assert floor_plant["name"] == "decor_dec_L0_001" and floor_plant["room_id"] == "r_L0_salon"
    assert floor_plant["pass_index"] == m["pass_index"]["dec_L0_001"] == objects[floor_plant["name"]]["pass_index"]
    assert list(m["pass_index"].values()).count(floor_plant["pass_index"]) == 1
    (x0, x1), (y0, y1), (z0, z1) = objects[floor_plant["name"]]["bounds"]
    assert z0 == pytest.approx(0.0, abs=1e-4) and ((x0 + x1) / 2, (y0 + y1) / 2) == pytest.approx((0.3, 0.3), abs=1e-3)
    assert objects[floor_plant["name"]]["props"]["wenart_host"] == ""
    assert not [w for w in m["warnings"] if "'None'" in w]
    decor = [o for o in decor if o["host_id"] is not None]
    by_host: dict[str, list] = {}
    for o in decor:
        by_host.setdefault(o["host_id"], []).append(o)
    hosts = {f["id"]: f for f in building["furniture"]}
    sofa = next(f for f in building["furniture"] if f["type"] == "sofa")
    desk = next(f for f in building["furniture"] if f["type"] == "desk")
    bed = next(f for f in building["furniture"] if f["type"] == "bed_double")
    entries = {o["element_id"]: o for o in m["objects"] if o["kind"] == "furniture"}
    for host_id, items in by_host.items():
        host_entry = entries[host_id]
        assert [d["name"] for d in host_entry["decor"]] == [o["name"] for o in items]
        for o in items:
            ob = objects[o["name"]]
            assert o["name"].startswith(f"decor_{host_id}_") and ob["wenart_id"] == host_id
            assert o["pass_index"] == ob["pass_index"] == m["pass_index"][host_id]
            assert ob["props"]["wenart_host"] == host_id and ob["props"]["wenart_source"] == "added_by_ai"
            assert max(o["size"]) <= P.DECOR_MAX_M + 1e-9
            (x0, x1), (y0, y1), (z0, z1) = ob["bounds"]
            assert x1 - x0 <= P.DECOR_MAX_M * math.sqrt(2) + 1e-6 and z1 - z0 <= P.DECOR_MAX_M + 1e-6
    cushion, plant = by_host[sofa["id"]]
    assert cushion["type"] == "cushion" and objects[cushion["name"]]["bounds"][2][0] == pytest.approx(0.45, abs=1e-4)
    assert cushion["assumed"]["rest_height"] == pytest.approx(0.45)
    assert plant["type"] == "plant" and objects[plant["name"]]["bounds"][2] == pytest.approx([0.0, 0.6], abs=1e-4)
    assert plant["size"] == [0.6, 0.6, 0.6]
    assert [w for w in m["warnings"] if "capped at 0.6" in w and "plant" in w]
    (books,) = by_host[desk["id"]]
    assert books["type"] == "book_set" and objects[books["name"]]["bounds"][2][0] == pytest.approx(0.75, abs=1e-4)
    assert books["method"].startswith("parametric")
    (lib_cushion,) = by_host[bed["id"]]
    assert lib_cushion["method"] == "library" and lib_cushion["asset"]["asset_id"] == "test_cube"
    (x0, x1), (y0, y1), (z0, z1) = objects[lib_cushion["name"]]["bounds"]
    # On the parametric bed's soft bedding (Milestone 6), not at the type height inside the pillows.
    top = P.bedding_top(*bed["footprint"]["size"], 0.55)
    assert (x1 - x0, y1 - y0) == pytest.approx((0.4, 0.25), abs=1e-3) and z0 == pytest.approx(top, abs=1e-4)
    assert lib_cushion["assumed"]["rest_height"] == pytest.approx(top, abs=1e-4)
    assert lib_cushion["fit"]["fit_scale"] == pytest.approx([0.5, 0.5, 0.5])
    assert [w for w in m["warnings"] if "decor host 'f_nope'" in w]
    assert hosts and m["furniture"]["decor"] == 5


@needs_blender
def test_proxies_flag_restores_the_milestone_3_boxes(tmp_path, glb):
    scene = _build(tmp_path, glb, extra=["--proxies"])
    m = scene["manifest"]
    schemas.validate_scene_manifest(m)
    furniture = scene["building"]["furniture"]
    kinds = {o["kind"] for o in m["objects"] if o["kind"] in ("furniture", "furniture_proxy")}
    assert kinds == {"furniture_proxy"}
    assert {o["wenart_id"] for o in m["objects"] if o["kind"] == "furniture_proxy"} == {f"proxy:{f['id']}" for f in furniture}
    assert m["furniture"]["proxies"] == len(furniture) and m["furniture"]["proxies_forced"] is True
    assert m["furniture"]["by_method"] == {"proxy": len(furniture)} and m["furniture"]["fallbacks"] == []
    assert not [n for n in scene["objects"] if n.startswith("furn_")]
    # Decor still lands on the proxies (same pass index as the host proxy).
    decor = [o for o in m["objects"] if o["kind"] == "decor"]
    assert len(decor) == 5
    for o in decor:
        if o["host_id"] is None:                      # the floor plant has its own index
            assert o["pass_index"] == m["pass_index"][o["wenart_id"]]
        else:
            assert o["pass_index"] == m["pass_index"][f"proxy:{o['host_id']}"]


# --------------------------------------------------------------------------
# Milestone 7: library licence gate, Objaverse GLBs from the cache, build: false (docs/milestone7.md §6.3-6.4)
# --------------------------------------------------------------------------

OBJ_UID = "0123456789abcdef0123456789abcdef"
CREDITS = {"title": "Cube", "author": "someone", "source_url": "https://sketchfab.com/3d-models/x",
           "licence_url": "https://creativecommons.org/licenses/by/4.0/",
           "via": "Objaverse (allenai/objaverse, ODC-By 1.0)", "attribution": '"Cube" by someone, CC BY 4.0'}


def _objaverse_asset(bbox, **extra):
    asset = _library_asset(bbox, library="objaverse", asset_id=f"objaverse_{OBJ_UID}", licence="CC-BY-4.0",
                           uid=OBJ_UID, glb=f"models/objaverse/{OBJ_UID}.glb", **CREDITS)
    asset.pop("file")
    asset.update(extra)
    return asset


def test_model_licence_gate_matches_the_asset_rule():
    from wenart.assets import fetch

    assert F.MODEL_LICENCES == {"polyhaven": ("CC0",), "objaverse": ("CC0", "CC-BY-4.0")}
    assert F.CC_BY_FIELDS == fetch.CC_BY_FIELDS and F.CC_BY == fetch.CC_BY
    assert F.licence_refusal(_library_asset([1, 1, 1])) is None
    assert F.licence_refusal(_objaverse_asset([1, 1, 1])) is None
    assert F.licence_refusal(_objaverse_asset([1, 1, 1], licence="CC0", attribution="")) is None
    assert "not CC0" in F.licence_refusal(_library_asset([1, 1, 1], licence="CC-BY-4.0"))        # Poly Haven
    for bad in ("CC-BY-NC-4.0", "CC-BY-SA-4.0", None, "CC-BY"):
        assert "is not CC0 or CC-BY-4.0" in F.licence_refusal(_objaverse_asset([1, 1, 1], licence=bad)), bad
    for field in F.CC_BY_FIELDS:
        why = F.licence_refusal(_objaverse_asset([1, 1, 1], **{field: ""}))
        assert why and field in why and "no credit line" in why
    assert "not a model source" in F.licence_refusal(_library_asset([1, 1, 1], library="sketchfab"))
    no_library = {k: v for k, v in _library_asset([1, 1, 1], licence="CC-BY-4.0", **CREDITS).items() if k != "library"}
    assert "not CC0" in F.licence_refusal(no_library)                       # held to the Poly Haven rule


def test_resolve_asset_finds_the_objaverse_glb_in_the_cache(tmp_path):
    asset = _objaverse_asset([1, 1, 1])
    assert F.resolve_asset(asset, str(tmp_path))[1] == f"asset file missing: {tmp_path / 'models/objaverse' / (OBJ_UID + '.glb')}"
    glb = tmp_path / F.OBJAVERSE_CACHE / f"{OBJ_UID}.glb"
    glb.parent.mkdir(parents=True)
    glb.write_bytes(b"glTF")
    assert F.resolve_asset(asset, str(tmp_path)) == (glb, None)
    by_uid = {k: v for k, v in asset.items() if k != "glb"}
    assert F.resolve_asset(by_uid, str(tmp_path)) == (glb, None)
    refused = F.resolve_asset(dict(asset, attribution=None), str(tmp_path))
    assert refused[0] is None and "no credit line" in refused[1]


def test_build_false_pieces_are_not_built():
    assert F.is_built({"type": "sofa"}) and F.is_built({"type": "sofa", "build": True})
    assert not F.is_built({"type": "unknown", "build": False})
    assert "not_furniture" in F.NOT_BUILT_REASON


@needs_blender
def test_objaverse_glb_cc_by_and_build_false_in_a_scene(tmp_path, glb):
    """An Objaverse CC BY piece is imported from the cache GLB with its credit kept in the manifest; one without
    the credit line falls back to the parametric mesh with the reason; a build: false symbol is not built at all
    (no object, no proxy, no pass index, its decor skipped) and listed under not_built."""
    import shutil

    assets = tmp_path / "assets"
    cache = assets / F.OBJAVERSE_CACHE / f"{OBJ_UID}.glb"
    cache.parent.mkdir(parents=True)
    shutil.copy(glb / "models" / "test_cube" / "test_cube.glb", cache)
    building = _building(assets)
    room = building["rooms"][0]["id"]
    building["furniture"] = [
        _piece("f_obj", "armchair", (3.0, 3.0), (0.8, 0.5), 0.0, asset=_objaverse_asset([0.8, 0.5, 0.9]), room_id=room),
        _piece("f_nocredit", "armchair", (5.0, 3.0), (0.8, 0.5), 0.0,
               asset=_objaverse_asset([0.8, 0.5, 0.9], attribution=""), room_id=room),
        dict(_piece("f_symbol", "unknown", (7.0, 3.0), (0.6, 0.6), 0.0, room_id=room), build=False,
             status="unverified"),
    ]
    building["decor"] = [{"type": "cushion", "host_id": "f_symbol", "center": [7.0, 3.0], "rotation_deg": 0.0,
                          "size": [0.4, 0.4], "asset": None}]
    building["unverified"] = ["f_symbol"]
    path = tmp_path / "building.json"
    path.write_text(json.dumps(building), encoding="utf-8")
    out = tmp_path / "scene"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(path), "--style", str(STYLE), "--assets", str(assets),
                                             "--out", str(out), "--no-textures", "--no-preview", "--no-glb"],
                    log_path=out / "build.log")
    m = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    schemas.validate_scene_manifest(m)
    entries = {o["wenart_id"]: o for o in m["objects"] if o["kind"] in ("furniture", "furniture_proxy", "decor")}
    assert entries["f_obj"]["method"] == "library" and entries["f_obj"]["file"] == str(cache)
    assert entries["f_obj"]["asset"]["attribution"] == CREDITS["attribution"]
    assert entries["f_nocredit"]["method"].startswith("parametric (fallback: ")
    assert "no credit line" in entries["f_nocredit"]["fallback_reason"]
    assert "f_symbol" not in entries and "proxy:f_symbol" not in entries
    assert "f_symbol" not in m["pass_index"] and "proxy:f_symbol" not in m["pass_index"]
    assert not [o for o in m["objects"] if o.get("element_id") == "f_symbol" or o.get("host_id") == "f_symbol"]
    assert m["furniture"]["pieces"] == 2 and m["furniture"]["proxies"] == 0
    assert [r["id"] for r in m["furniture"]["not_built"]] == ["f_symbol"]
    assert all("f_symbol" not in c["visible_furniture"] for c in m["cameras"])
