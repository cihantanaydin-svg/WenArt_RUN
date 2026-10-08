"""Milestone 10 doors, windows and wall looks (docs/milestone10.md §4.1, §4.3, §4.7, §1.6b rows 17, 20; track F).

CPU tests of ``wenart/blender/looks.py`` (the functions ``shell.py`` calls: wall faces, wet walls with the brief's
tile size and grout, the accent wall behind the sofa or the bed head else the longest wall without a window, door
looks with the drawn operation first, window frames, the facade) and of the pure door and window parts of
``wenart/blender/parametric.py`` (every door style, frames by material with mullions, transoms and an inside
sill); ``shell.py``'s wrappers hand over to them; the outside words come from track C's tables.
"""
from __future__ import annotations

import pytest

from wenart.blender import exterior as E
from wenart.blender import looks
from wenart.blender import parametric as P
from wenart.blender import shell

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
    assert max(v[2] for v in sill["verts"]) == pytest.approx(0.0)
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
