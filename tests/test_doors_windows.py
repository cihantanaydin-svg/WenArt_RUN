"""Milestone 10 doors, windows and wall looks (docs/milestone10.md §4.1, §4.3, §4.7, §1.6b rows 17, 20; track F).

CPU tests of ``wenart/blender/looks.py`` (the functions ``shell.py`` calls: wall faces, wet walls with the brief's
tile size and grout, the accent wall behind the sofa or the bed head else the longest wall without a window, door
looks with the drawn operation first, window frames, the facade) and of the pure door and window parts of
``wenart/blender/parametric.py`` (every door style, frames by material with mullions, transoms and an inside
sill); ``shell.py``'s wrappers hand over to them; the outside words come from track C's tables.

Milestone 10 opening geometry in the shell (``shell.build_door_m10`` / ``build_window_m10``): which doors and
windows get it (a project without Milestone 10 door, window or colour values keeps the Milestone 6-9 ones), the
room side of a sliding door and an inside sill, the outside sill from the frame profile; a Blender scene (skipped
without ``WENART_BLENDER``) with every drawn door operation, a window with mullions and a transom and a coloured
floor, ceiling and trim.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from wenart.blender import cli
from wenart.blender import exterior as E
from wenart.blender import looks
from wenart.blender import parametric as P
from wenart.blender import shell

ROOT = Path(__file__).resolve().parents[1]
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER)")

STYLE = {"walls": {"material": "paint", "asset": "plastered_wall", "colour": "warm greige"},
         "wall_accent": {"material": "paint", "asset": "plastered_wall", "colour": "sage",
                         "room_types": ["living", "bedroom"], "rule": "one accent wall"},
         "wet_walls": {"material": "tiles_zellige", "asset": None, "tile_size_m": [0.1, 0.1], "pattern": "grid",
                       "colour": "sage", "grout_colour": "white"},
         "door": {"material": "wood_walnut", "asset": "WoodFloor046", "style": "shaker_panel", "colour": None,
                  "handle": "brass"},
         "window_frame": {"material": "dark_bronze", "asset": None, "colour": None}}


# --------------------------------------------------------------------------
# Walls
# --------------------------------------------------------------------------

def test_wall_looks_are_the_style_slots_with_their_colour_and_tile_params():
    look = looks.wall_face_material(STYLE)
    assert look == {"material": "paint", "asset": "plastered_wall", "tint": None, "colour": "warm greige"}
    legacy = looks.wall_face_material({"walls": {"material": "plaster_cream", "asset": "beige_wall_001",
                                                 "colour": None}})
    assert legacy == {"material": "plaster_cream", "asset": "beige_wall_001", "tint": None}      # the M9 look
    wet = looks.wet_wall_look(STYLE, {"room_type": "bathroom"})
    assert wet["material"] == "tiles_zellige" and wet["colour"] == "sage"
    assert wet["params"] == {"tile_size_m": [0.1, 0.1], "pattern": "grid", "grout_colour": "white"}
    assert "params" not in looks.wet_wall_look({"wet_walls": {"material": "tiles_light", "asset": "Tiles074"}})
    assert shell.wall_face_material(STYLE)["colour"] == "warm greige"            # the shell's wrapper hands over
    assert shell.wet_wall_look(STYLE)["params"]["grout_colour"] == "white"


def _room_building(furniture=(), windows=()):
    t = 0.2
    walls = [{"id": "w_s", "start": [0.0, -t / 2], "end": [6.0, -t / 2]},
             {"id": "w_e", "start": [6.0 + t / 2, 0.0], "end": [6.0 + t / 2, 4.0]},
             {"id": "w_n", "start": [6.0, 4.0 + t / 2], "end": [0.0, 4.0 + t / 2]},
             {"id": "w_w", "start": [-t / 2, 4.0], "end": [-t / 2, 0.0]}]
    walls = [dict(w, level_id="L0", thickness=t) for w in walls]
    rooms = [{"id": "r", "level_id": "L0", "room_type": "living", "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]]},
             {"id": "k", "level_id": "L0", "room_type": "kitchen", "polygon": [[0, 0], [6, 0], [6, 4], [0, 4]]}]
    openings = [{"id": wid, "type": "window", "level_id": "L0", "wall_id": wall, "center": c, "width": 1.2}
                for wid, wall, c in windows]
    pieces = [{"id": pid, "type": ftype, "level_id": "L0", "room_id": "r",
               "footprint": {"center": list(c), "size": list(size), "rotation_deg": rot},
               "front_deg": (270 + rot) % 360}
              for pid, ftype, c, size, rot in furniture]
    return {"walls": walls, "rooms": rooms, "openings": openings, "furniture": pieces}


def test_accent_wall_is_behind_the_sofa_else_the_longest_wall_without_a_window():
    level = {"id": "L0"}
    b = _room_building(furniture=[("f1", "sofa", (3.0, 0.45), (2.2, 0.9), 180.0)])      # back to the south wall
    out = looks.accent_walls(b, level, STYLE)
    assert list(out) == ["w_s"] and list(out["w_s"]) == ["r"]                          # the kitchen gets none
    look = out["w_s"]["r"]
    assert look["material"] == "paint" and look["colour"] == "sage" and look["accent"] is True
    assert "behind the sofa f1" in look["reason"]
    # No sofa: the longest wall without a window (the south and north walls are 6 m; the north one has a window).
    b = _room_building(windows=[("win", "w_n", [3.0, 4.1])])
    assert list(looks.accent_walls(b, level, STYLE)) == ["w_s"]
    b = _room_building(windows=[("win", "w_s", [3.0, -0.1])])
    out = looks.accent_walls(b, level, STYLE)
    assert list(out) == ["w_n"] and "longest wall without a window" in out["w_n"]["r"]["reason"]
    assert looks.accent_walls(b, level, {"walls": STYLE["walls"]}) == {}                 # no accent in the style
    assert shell.accent_walls(b, level, STYLE) == out
    assert looks.room_walls(b["rooms"][0], b["walls"])[0][1] == pytest.approx(6.0)


# --------------------------------------------------------------------------
# Doors: the drawn operation first
# --------------------------------------------------------------------------

@pytest.mark.parametrize("operation,style,expected", [
    (None, "shaker_panel", "shaker_panel"), ("swing", "glazed", "glazed"), ("swing", "barn", "flush"),
    ("swing", None, "flush"), ("sliding", "barn", "barn"), ("sliding", "shaker_panel", "sliding"),
    ("pocket", "glazed", "pocket"), ("double", None, "double"), ("folding", "flush", "folding"),
    ("fixed", "entrance", "flush"), ("unknown", "entrance", "entrance")])
def test_door_style_follows_the_drawn_operation(operation, style, expected):
    door = dict(STYLE["door"], style=style)
    look = looks.door_look({"door": door}, {"id": "d", "type": "door", "operation": operation})
    assert look["door_style"] == expected
    assert look["operation_assumed"] is (operation is None)
    if style and style != expected:
        assert "does not fit" in look["reason"]


def test_door_look_takes_the_veneer_and_the_handle():
    look = looks.door_look(STYLE, {"id": "d", "operation": "swing"})
    assert (look["material"], look["asset"]) == ("wood_veneer_walnut", "walnut_veneer")
    assert look["handle"] == "brass" and look["handle_material"] == "metal_brass" and not look["handle_assumed"]
    painted = looks.door_look({"door": {"material": "painted_wood_white", "colour": "dusty blue"}}, None)
    assert painted["material"] == "painted_wood_white" and painted["colour"] == "dusty blue"
    assert painted["handle"] == "brushed_steel" and painted["handle_assumed"]
    assert shell.door_look(STYLE, {"id": "d", "operation": "pocket"})["door_style"] == "pocket"


@pytest.mark.parametrize("style", P.DOOR_STYLES)
def test_door_parts_of_every_style(style):
    w, h, t = 0.9, 2.1, 0.12
    parts, record = P.door_parts({"door_style": style}, w, h, t)
    assert record["door_style"] == style
    assert {p["key"] for p in parts} <= set(P.OPENING_KEYS)
    roles = {p["role"] for p in parts}
    assert "leaf" in roles and "handle" in roles
    x0, y0, z0, x1, y1, z1 = P.parts_bbox(parts)
    assert z0 == pytest.approx(0.0)
    if style in ("sliding", "barn"):                         # on the room face of the wall, past the opening
        assert record["surface_mounted"] and "rail" in roles and "frame" not in roles
        leaf = [p for p in parts if p["role"] == "leaf"]
        assert all(max(v[1] for v in p["verts"]) <= -t / 2.0 for p in leaf)
        assert max(v[0] for p in leaf for v in p["verts"]) >= w / 2.0 + P.SLIDING_OVERLAP_M - 0.005   # planks
    else:                                                    # inside the opening and the wall
        assert x0 >= -w / 2.0 - 1e-9 and x1 <= w / 2.0 + 1e-9 and "frame" in roles
        leaves = [p for p in parts if p["role"] == "leaf"]
        assert all(abs(v[1]) <= t / 2.0 + 1e-9 for p in leaves for v in p["verts"])
    if style == "glazed":
        assert "glass" in roles
    if style in ("double", "folding"):
        assert sum(p["role"] == "leaf" for p in parts) == 2
    if style == "shaker_panel":
        assert sum(p["role"] == "panel" for p in parts) == 10
    if style == "entrance":
        assert record["leaf_thickness"] == P.ENTRANCE_LEAF_T
    flipped, rec = P.door_parts({"door_style": "sliding", "side": 1}, w, h, t)
    assert rec["side"] == 1.0 and min(v[1] for p in flipped if p["role"] == "leaf" for v in p["verts"]) >= t / 2.0
    assert record["handles"]
    fixed, rec = P.door_parts({"door_style": style, "operation": "fixed"}, w, h, t)
    assert not rec["handles"] and not [p for p in fixed if p["key"] == "handle"]       # a drawn fixed leaf
    assert [p for p in fixed if p["role"] == "leaf"]


# --------------------------------------------------------------------------
# Windows
# --------------------------------------------------------------------------

def test_window_frame_look_and_profiles():
    look = looks.window_frame_look(STYLE, {"id": "w", "mullions": 2, "transoms": 0})
    assert look["material"] == "dark_bronze" and look["mullions"] == 2 and "transoms" not in look
    painted = looks.window_frame_look({"window_frame": {"material": "painted_metal_white", "colour": "sage"}})
    assert painted["colour"] == "sage" and "in sage" in painted["reason"]
    assert shell.window_frame_look(STYLE, {"id": "w"})["material"] == "dark_bronze"
    from wenart.style import finishes as FIN
    assert set(P.WINDOW_PROFILES) == set(FIN.WINDOW_FRAME_MATERIALS)
    assert P.window_profile("steel_black")[0] < P.window_profile("pvc_white")[0]      # slim steel, wide PVC
    assert P.window_profile("nonsense") == P.DEFAULT_WINDOW_PROFILE


@pytest.mark.parametrize("material", ["pvc_white", "steel_black", "oak"])
def test_window_parts_frame_bars_glass_and_inside_sill(material):
    w, h, t = 1.6, 1.4, 0.25
    parts, rec = P.window_parts({"material": material}, w, h, t, mullions=1, transoms=1, inside=-1)
    fw, depth = P.window_profile(material)
    assert rec["frame_width"] == fw and rec["mullions"] == 1 and rec["transoms"] == 1 and rec["profile_assumed"]
    roles = [p["role"] for p in parts]
    assert roles.count("frame") == 4 and roles.count("mullion") == 1 and roles.count("transom") == 1
    assert "glass" in roles and {p["key"] for p in parts} <= set(P.OPENING_KEYS)
    sill = next(p for p in parts if p["role"] == "sill")
    ys = [v[1] for v in sill["verts"]]
    assert max(ys) <= -depth / 2.0 + 1e-9 and min(ys) == pytest.approx(-t / 2.0 - P.INSIDE_SILL["depth_proud"])
    assert min(v[2] for v in sill["verts"]) == pytest.approx(0.0)               # on the reveal
    assert max(v[2] for v in sill["verts"]) == pytest.approx(P.INSIDE_SILL["thickness"])
    plain, rec = P.window_parts({"material": material}, w, h, t)
    assert rec["mullions"] == rec["transoms"] == 0 and "mullion" not in {p["role"] for p in plain}


# --------------------------------------------------------------------------
# Facade and outside words (track C's tables)
# --------------------------------------------------------------------------

def test_facade_look_and_outside_words():
    resolved = {"facade": {"material": "render", "colour": "warm greige", "source": "fallback"}}
    assert looks.facade_look(resolved, {"id": "w"}) is resolved["facade"]
    assert shell.facade_look(resolved) is resolved["facade"]
    assert E.look_from_words("window_frame", "anthracite aluminium") == {"material": "aluminium_anthracite",
                                                                         "colour": None}
    assert E.look_from_words("facade", "Light grey fibre cement panels") == {"material": "fibre_cement",
                                                                             "colour": "light grey"}
    assert E.look_from_words("roof", "something else") is None
    assert not hasattr(E, "EXTERIOR_WORDS") and not hasattr(shell, "_SRGB")
    assert shell.colour_rgb("warm greige") is not None and shell.colour_rgb("not a colour") is None
    assert set(shell.LOOK_RGB) <= {"stone", "concrete", "bark", "foliage", "soil", "soffit", "glass"}



# --------------------------------------------------------------------------
# The shell's Milestone 10 doors and windows
# --------------------------------------------------------------------------

M9_STYLE = json.loads((ROOT / "tests" / "fixtures" / "blender_style.json").read_text(encoding="utf-8"))


def test_which_doors_and_windows_get_the_milestone_10_geometry():
    """A project without Milestone 10 door, window or colour values keeps the Milestone 6-9 door and window; a
    drawn non-swing operation, a style door style / handle / colour, an M10 frame material or colour, or drawn
    mullions / transoms switch to door_parts / window_parts."""
    swing = {"id": "d", "type": "door", "operation": "swing"}
    assert not shell.door_geometry_m10(M9_STYLE, swing) and not shell.door_geometry_m10(M9_STYLE, {"id": "d"})
    assert not shell.window_geometry_m10(M9_STYLE, {"id": "w"})
    for op in ("sliding", "pocket", "double", "folding", "fixed"):
        assert shell.door_geometry_m10(M9_STYLE, dict(swing, operation=op)), op
    assert not shell.door_geometry_m10(M9_STYLE, dict(swing, operation="unknown"))
    for key, value in (("style", "shaker_panel"), ("handle", "brass"), ("colour", "sage")):
        assert shell.door_geometry_m10({"door": {"material": "wood_oak_light", key: value}}, swing), key
    assert shell.window_geometry_m10(STYLE, {"id": "w"})                                   # dark bronze
    assert shell.window_geometry_m10({"window_frame": {"material": "painted_metal_white", "colour": "sage"}})
    assert shell.window_geometry_m10(M9_STYLE, {"id": "w", "mullions": 1})
    assert not shell.window_geometry_m10(M9_STYLE, {"id": "w", "mullions": 0, "transoms": True})


def test_opening_room_side_and_the_outside_sill_from_the_frame_profile():
    wall = {"id": "w", "start": [0.0, 0.0], "end": [0.0, 4.0], "thickness": 0.2}         # left normal: -x
    rooms = [{"id": "r_a", "polygon": [[-3, 0], [-0.1, 0], [-0.1, 4], [-3, 4]]},
             {"id": "r_b", "polygon": [[0.1, 0], [3, 0], [3, 4], [0.1, 4]]}]
    assert shell.opening_room_side((0.0, 2.0), wall, rooms, "r_b") == (-1, "r_b", False)
    assert shell.opening_room_side((0.0, 2.0), wall, rooms, "r_a") == (1, "r_a", False)
    assert shell.opening_room_side((0.0, 2.0), wall, rooms) == (-1, "r_b", True)          # both sides: assumed
    assert shell.opening_room_side((0.0, 2.0), wall, rooms[:1]) == (1, "r_a", False)      # the only room
    assert shell.opening_room_side((0.0, 2.0), wall, []) == (-1, None, True)
    window = {"id": "w1", "type": "window", "center": [0.0, 2.0], "width": 1.0, "height": 1.2, "sill_height": 0.9}
    level = {"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}
    _v, _f, m9 = shell.sill_box(window, wall, level, False, (1.0, 0.0))
    _v, _f, m10 = shell.sill_box(window, wall, level, False, (1.0, 0.0), {"frame_depth": 0.045})
    assert m10["depth"] == pytest.approx(m9["depth"] + (0.08 - 0.045) / 2.0)             # from the slimmer frame


def test_opening_parts_mesh_gives_each_role_its_material():
    class Mat:
        def __init__(self, name):
            self.name = name

    frame, leaf, metal = Mat("trim"), Mat("oak"), Mat("black")
    parts, _ = P.door_parts({"door_style": "barn"}, 0.9, 2.1, 0.2)
    verts, faces, mats, idx = shell.opening_parts_mesh(parts, {"rail": metal, "leaf": leaf, "handle": metal,
                                                               "frame": frame}, (1.0, 2.0, 0.0), 90.0)
    assert [m.name for m in mats] == ["oak", "black"]
    assert len(idx) == len(faces) == sum(len(p["faces"]) for p in parts)
    assert sum(1 for i in idx if i == 1) == sum(len(p["faces"]) for p in parts if p["key"] in ("rail", "handle"))
    xs = [v[0] for v in verts]
    assert min(xs) > 1.0 + 0.1 - 1e-9                     # wall along +y: local -y (the default side) is world +x


DOORS_STYLE = {
    "source_text": "test", "family": "modern",
    "floor": {"material": "microcement", "asset": None, "colour": "warm greige"},
    "walls": {"material": "paint", "asset": None, "colour": "white"},
    "ceiling": {"material": "plaster_white", "colour": "sage"},
    "wet_floor": {"material": "tiles_light", "asset": None, "colour": None},
    "wet_walls": {"material": "tiles_light", "asset": None, "tile_size_m": None, "pattern": None, "colour": None,
                  "grout_colour": None},
    "trim": {"material": "painted_wood_white", "colour": "charcoal"},
    "door": {"material": "wood_oak_light", "asset": None, "style": "shaker_panel", "colour": None, "handle": "black"},
    "window_frame": {"material": "steel_black", "asset": None, "colour": None,
                     "outside": {"material": "steel_black", "colour": None}},
    "lighting": {"hdri": "kloofendal_48d_partly_cloudy", "sun_elevation_deg": 40, "sun_azimuth_deg": 200,
                 "sun_strength": 3.0, "colour_temperature_k": 5500, "mood": "warm daylight"},
}


def _doors_building() -> dict:
    ev = [{"file": "t.dxf", "method": "vector", "confidence": 1.0}]
    w, d, t = 8.0, 6.0, 0.2
    walls = [{"id": "w_s", "start": [-t / 2, -t / 2], "end": [w + t / 2, -t / 2]},
             {"id": "w_e", "start": [w + t / 2, -t / 2], "end": [w + t / 2, d + t / 2]},
             {"id": "w_n", "start": [w + t / 2, d + t / 2], "end": [-t / 2, d + t / 2]},
             {"id": "w_w", "start": [-t / 2, d + t / 2], "end": [-t / 2, -t / 2]},
             {"id": "w_m", "start": [4.0, 0.0], "end": [4.0, d]}]
    walls = [dict(x, level_id="L0", thickness=t, status="verified", evidence=ev, exterior=x["id"] != "w_m")
             for x in walls]
    rooms = [{"id": "r_a", "label": "Living", "room_type": "living", "polygon": [[0, 0], [3.9, 0], [3.9, d], [0, d]]},
             {"id": "r_b", "label": "Bed", "room_type": "bedroom", "polygon": [[4.1, 0], [w, 0], [w, d], [4.1, d]]}]
    rooms = [dict(r, level_id="L0", status="verified", evidence=ev, area_computed=1.0) for r in rooms]

    def door(oid, wall, centre, width, operation, **extra):
        return dict({"id": oid, "type": "door", "wall_id": wall, "center": list(centre), "width": width,
                     "height": 2.1, "sill_height": 0.0, "operation": operation, "operation_source": "block_name",
                     "swing_side": None}, **extra)

    openings = [door("d_slide", "w_m", (4.0, 0.8), 0.9, "sliding", swing_side="r_b"),
                door("d_double", "w_m", (4.0, 2.2), 1.3, "double"),
                door("d_pocket", "w_m", (4.0, 3.5), 0.8, "pocket"),
                door("d_fixed", "w_m", (4.0, 4.5), 0.7, "fixed"),
                door("d_fold", "w_m", (4.0, 5.4), 0.8, "folding"),
                door("d_entry", "w_s", (1.0, -0.1), 0.9, None),
                {"id": "win_m", "type": "window", "wall_id": "w_s", "center": [6.0, -0.1], "width": 1.8,
                 "height": 1.4, "sill_height": 0.8, "mullions": 2, "transoms": 1},
                {"id": "win_p", "type": "window", "wall_id": "w_w", "center": [-0.1, 3.0], "width": 1.0,
                 "height": 1.2, "sill_height": 0.9}]
    openings = [dict(o, level_id="L0", status="verified", evidence=ev) for o in openings]
    return {"schema_version": "0.1", "status": "ok", "project": {"id": "doors-test"},
            "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "walls": walls,
            "openings": openings, "rooms": rooms, "furniture": [], "decor": [], "warnings": [], "unverified": []}


DUMP = """
import bpy, json, sys
out = sys.argv[sys.argv.index("--") + 1]
rows = {}
for ob in bpy.data.objects:
    if ob.type != "MESH" or not len(ob.data.vertices):
        continue
    mw = ob.matrix_world
    vs = [mw @ v.co for v in ob.data.vertices]
    mats = [m.name if m else None for m in ob.data.materials]
    rows[ob.name] = {"min": [min(v[i] for v in vs) for i in range(3)],
                     "max": [max(v[i] for v in vs) for i in range(3)], "materials": mats}
json.dump(rows, open(out, "w"))
"""


@pytest.fixture(scope="module")
def doors_scene(tmp_path_factory):
    pytest.importorskip("jsonschema")
    if BLENDER is None:
        pytest.skip("no Blender binary")
    tmp = tmp_path_factory.mktemp("doors_scene")
    (tmp / "building.json").write_text(json.dumps(_doors_building()), encoding="utf-8")
    (tmp / "style.json").write_text(json.dumps(DOORS_STYLE), encoding="utf-8")
    (tmp / "assets").mkdir()
    out = tmp / "scene"
    args = ["--building", str(tmp / "building.json"), "--style", str(tmp / "style.json"),
            "--assets", str(tmp / "assets"), "--out", str(out), "--no-preview", "--no-glb"]
    cli.run_blender(Path(cli.BUILD_SCRIPT), args, log_path=out / "build.log")
    (tmp / "dump.py").write_text(DUMP, encoding="utf-8")
    cli.run_blender(tmp / "dump.py", [str(tmp / "objects.json")], blend=str(out / "scene.blend"))
    return {"manifest": json.loads((out / "scene_manifest.json").read_text(encoding="utf-8")),
            "objects": json.loads((tmp / "objects.json").read_text(encoding="utf-8"))}


@needs_blender
def test_scene_builds_every_drawn_door_operation(doors_scene):
    from wenart.blender import schemas

    m, objs = doors_scene["manifest"], doors_scene["objects"]
    schemas.validate_scene_manifest(m)
    entries = {o["name"]: o for o in m["objects"]}
    styles = {n[:-5]: e["door"]["door_style"] for n, e in entries.items() if n.endswith("_leaf") and "door" in e}
    assert styles == {"d_slide": "sliding", "d_double": "double", "d_pocket": "pocket", "d_fixed": "flush",
                      "d_fold": "folding", "d_entry": "shaker_panel"}                  # the drawn operation wins
    # the sliding door hangs on the face of r_b (x > 4.1), its rail in the handle metal in d_slide_frame
    slide = entries["d_slide_leaf"]["door"]
    assert slide["surface_mounted"] and slide["side_room"] == "r_b" and slide["side_assumed"] is False
    assert objs["d_slide_leaf"]["min"][0] > 4.0 + 0.1 - 1e-6
    assert objs["d_slide_leaf"]["max"][1] - objs["d_slide_leaf"]["min"][1] >= 0.9 + 2 * P.SLIDING_OVERLAP_M - 0.01
    assert any(n.startswith("metal_black") for n in objs["d_slide_frame"]["materials"])
    # the others sit in the wall; the fixed one has no handles
    for oid in ("d_double", "d_pocket", "d_fixed", "d_fold"):
        assert 4.0 - 0.1 - 1e-6 <= objs[f"{oid}_leaf"]["min"][0] and objs[f"{oid}_leaf"]["max"][0] <= 4.1 + 1e-6
        assert f"{oid}_frame" in objs
    assert "d_fixed_handle" not in objs and entries["d_fixed_leaf"]["door"]["handles"] is False
    handle = entries["d_double_handle"]
    assert handle["status"] == "assumed" and handle["parent"] == "d_double"
    assert handle["material"].startswith("metal_black")
    # the swing entrance door: the style's shaker panels in oak veneer, black handles, swing assumed
    entry = entries["d_entry_leaf"]
    assert entry["door"]["operation_assumed"] is True and entry["material"].startswith("wood_veneer_oak")
    assert objs["d_entry_leaf"]["max"][1] - objs["d_entry_leaf"]["min"][1] > P.DOOR_LEAF_T     # panels proud
    assert {a["object"] for a in m["assumed"] if a["field"] == "door_handles"} >= {"d_entry_handle",
                                                                                  "d_slide_handle"}
    rays = {r["opening_id"]: r for r in m["checks"]["door_rays"]}
    assert set(rays) >= set(styles) and all(not r["hit"] for r in rays.values())       # every door cut through


@needs_blender
def test_scene_builds_windows_with_bars_and_sills_and_coloured_surfaces(doors_scene):
    m, objs = doors_scene["manifest"], doors_scene["objects"]
    entries = {o["name"]: o for o in m["objects"]}
    win = entries["win_m_frame"]["window"]
    fw, depth = P.window_profile("steel_black")
    assert (win["material"], win["mullions"], win["transoms"]) == ("steel_black", 2, 1)
    assert win["frame_width"] == fw and win["frame_depth"] == pytest.approx(depth)
    assert win["inside_side"] == 1 and win["room_id"] == "r_b" and win["inside_assumed"] is False
    frame = objs["win_m_frame"]
    assert frame["max"][1] - frame["min"][1] == pytest.approx(depth, abs=1e-4)          # the steel profile
    sill = objs["win_m_inside_sill"]
    assert sill["min"][1] > -0.1 and sill["max"][1] == pytest.approx(P.INSIDE_SILL["depth_proud"], abs=1e-4)
    assert sill["min"][2] == pytest.approx(0.8, abs=1e-4)                               # on the reveal
    assert entries["win_m_inside_sill"]["status"] == "assumed"
    assert entries["win_m_inside_sill"]["material"].startswith("painted_wood_white__charcoal")
    assert entries["win_p_frame"]["window"]["mullions"] == 0 and "win_p_glass" in objs
    # coloured floor, ceiling and trim (skirting, door frames)
    floor, ceiling = entries["r_a_floor"], entries["r_b_ceiling"]
    assert floor["material"].startswith("microcement__warm_greige")
    assert ceiling["material"].startswith("plaster_white__sage")
    assert m["materials"][floor["material"]]["colour_applied"] and m["materials"][ceiling["material"]]["colour_applied"]
    skirting = [o for o in m["objects"] if (o.get("assumed") or {}).get("detail") == "skirting"]
    assert skirting and all(o["material"].startswith("painted_wood_white__charcoal") for o in skirting)
    assert entries["d_entry_frame"]["material"].startswith("painted_wood_white__charcoal")
