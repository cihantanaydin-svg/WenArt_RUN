"""Lesson UL106 (29 Oct 2026; user, showing a professional bedroom render: "look at this renders I want my renders to be
as professional as these ones"): the general rules that carry the reference's look to every project of the fitting
style families, checked on CPU.

- parquet floors (``wenart.blender.parquet``): the herringbone and chevron tilings, the rooms and their joins, the
  shell's floor slot, and the shader node group's arithmetic (evaluated on a fake bpy) against the pure ``cell``;
- feature walls (``wenart.blender.feature_walls``): the fluted panel and the classic wainscot on the accent wall,
  never over a window or door, cut at a tall piece, under a low slope left out, wall art standing off them;
- the decor stage's dressing (``wenart.furniture.dressing``): layered curtains on a ceiling track, layered bedding,
  the lights plan's statement fixture, downlights and bedside pendants (its spacing kept), the recipe's decisions;
- the builders' pure parts (curtains, downlights, euro shams, a layered throw), the fit's light roles, the level
  interior cameras, the judge's bar and the checks U23 (Argus) and M23 (model review).
"""
from __future__ import annotations

import copy
import math
import random
import sys
import types

import pytest

from test_decor_m8 import RID, room_building
from wenart.agent import causes as CS
from wenart.agent import judge as J
from wenart.audit import kinds as K
from wenart.audit import lessons as LS
from wenart.blender import cameras as CAM
from wenart.blender import feature_walls as FW
from wenart.blender import materials as M
from wenart.blender import model_review as MR
from wenart.blender import overrides as O
from wenart.blender import parametric as P
from wenart.blender import parquet as PQ
from wenart.blender import rest as R
from wenart.blender import shell
from wenart.blender import textiles as T
from wenart.furniture import dressing as DR
from wenart.furniture import fit as FIT
from wenart.run import stages as ST

SCANDI = {"family": "scandinavian", "floor": {"material": "wood_oak_light", "asset": "WoodFloor051"},
          "walls": {"material": "plaster_white"}, "wall_accent": None, "decor": {}}


def bedroom(width=4.0, depth=5.0, windows=(), furniture=None, ceiling=2.7):
    """A 4 x 5 m bedroom: the double bed's head on the north wall (y = depth), its two nightstands."""
    bed = ("bed_double", (2.0, depth - 1.0), 0.0, (1.6, 2.0))
    stands = [("nightstand", (0.95, depth - 0.21), 0.0, (0.45, 0.42)), ("nightstand", (3.05, depth - 0.21), 0.0,
                                                                         (0.45, 0.42))]
    b = room_building(width, depth, "bedroom", furniture=[bed] + stands + list(furniture or ()), windows=windows,
                      ceiling=ceiling)
    for f in b["furniture"]:
        f["height"] = {"bed_double": 0.5, "nightstand": 0.5}.get(f["type"], f.get("height"))
    return b


# --------------------------------------------------------------------------
# parquet
# --------------------------------------------------------------------------

def _diag(params):
    """The plank's longest diagonal: a herringbone block's, a chevron parallelogram's (its ends cut along its column)."""
    length, width = float(params["length_m"]), float(params["width_m"])
    if params["pattern"] == "chevron":
        a = math.radians(PQ.PLANK["chevron"]["cut_deg"])
        col = length * math.cos(a)
        return math.hypot(col, col * math.tan(a) + width / math.cos(a))
    return math.hypot(length, width)


@pytest.mark.parametrize("pattern,turn", [("herringbone", 45.0), ("herringbone", 12.0), ("chevron", 90.0)])
def test_the_parquet_tilings_are_exact(pattern, turn):
    params = {"pattern": pattern, "length_m": 0.6, "width_m": 0.12 if pattern == "herringbone" else 0.1,
              "turn_deg": turn}
    rng = random.Random(7)
    planks: dict = {}
    for _ in range(4000):
        x, y = rng.uniform(-2.0, 2.0), rng.uniform(-2.0, 2.0)
        c = PQ.cell(pattern, x, y, params)
        assert -1e-9 <= c["across_m"] <= params["width_m"] + 1e-9
        assert -1e-9 <= c["along_m"] <= params["length_m"] + 1e-6
        assert 0.0 <= c["seam"] <= 1.0
        planks.setdefault(c["plank"], []).append((x, y))
    # every plank id covers one plank: no two of its points farther apart than the plank's diagonal
    for pts in planks.values():
        assert max(math.dist(a, b) for a in pts for b in pts) <= _diag(params) + 1e-6
    if pattern == "herringbone":                 # half the floor is laid each way
        kinds = [k[0] for k, pts in planks.items() for _p in pts]
        assert 0.4 < kinds.count("h") / len(kinds) < 0.6


def test_a_herringbone_point_that_is_no_horizontal_plank_lies_on_a_vertical_one():
    n = 5
    rng = random.Random(3)
    for _ in range(5000):
        u, v = rng.uniform(-30, 30), rng.uniform(-30, 30)
        if PQ._fmod(u - math.floor(v), 2 * n) >= n:
            assert PQ._fmod(v - math.floor(u) - 1.0, 2 * n) < n


def test_the_family_pattern_and_the_briefs_word():
    assert PQ.family_pattern(SCANDI)[0] == "herringbone"
    assert PQ.family_pattern(dict(SCANDI, family="mediterranean"))[0] == "chevron"
    for fam in ("minimal", "japandi", "rustic", "industrial"):
        assert PQ.family_pattern(dict(SCANDI, family=fam))[0] is None
    assert PQ.family_pattern(dict(SCANDI, floor={"material": "wood_wide_plank"}))[0] is None
    assert PQ.family_pattern(dict(SCANDI, floor={"material": "tiles_large_porcelain"}))[0] is None
    assert PQ.family_pattern(dict(SCANDI, floor={"material": "wood_oak_light", "pattern": "plank"}))[0] is None
    assert PQ.family_pattern(dict(SCANDI, family="minimal",
                                  floor={"material": "wood_oak_light", "pattern": "chevron"}))[0] == "chevron"


def _two_rooms(join_type="opening"):
    b = room_building(4.0, 4.0, "living")
    b["rooms"].append({"id": "r_hall", "level_id": "L0", "label": "Hall", "room_type": "hall",
                       "polygon": [[4.2, 0], [7.0, 0], [7.0, 4.0], [4.2, 4.0]], "area_computed": 11.2,
                       "status": "verified", "evidence": []})
    b["rooms"].append({"id": "r_bath", "level_id": "L0", "label": "Bath", "room_type": "bathroom",
                       "polygon": [[7.2, 0], [9.0, 0], [9.0, 4.0], [7.2, 4.0]], "area_computed": 7.2,
                       "status": "verified", "evidence": []})
    b["walls"] += [{"id": "w_mid", "level_id": "L0", "start": [4.1, 0.0], "end": [4.1, 4.0], "thickness": 0.2},
                   {"id": "w_mid2", "level_id": "L0", "start": [7.1, 0.0], "end": [7.1, 4.0], "thickness": 0.2}]
    b["openings"] += [{"id": "o_join", "type": join_type, "level_id": "L0", "wall_id": "w_mid", "center": [4.1, 2.0],
                       "width": 1.6},
                      {"id": "o_bath", "type": "opening", "level_id": "L0", "wall_id": "w_mid2", "center": [7.1, 2.0],
                       "width": 0.8}]
    return b


def test_a_patterned_floor_runs_on_through_a_doorless_opening_never_into_a_wet_room():
    plans = PQ.plan_rooms(_two_rooms(), SCANDI)
    assert plans[RID]["pattern"] == "herringbone" and plans["r_hall"]["joined_from"] == RID
    assert "r_bath" not in plans
    assert "r_hall" not in PQ.plan_rooms(_two_rooms("door"), SCANDI)      # a door: the hall keeps its planks
    off = PQ.plan_rooms(_two_rooms(), SCANDI, {RID: {"floor_pattern": False}})
    assert off == {}


def test_the_shell_lays_the_rooms_pattern_on_the_style_floor_only():
    b = bedroom()
    assert PQ.annotate(b, SCANDI)[0]["field"] == "floor_pattern"
    room = b["rooms"][0]
    slot, wet = shell.floor_style(room, SCANDI)
    assert not wet and slot["material"] == "wood_oak_light" and slot["params"]["parquet"]["pattern"] == "herringbone"
    assert slot["params"]["parquet"]["turn_deg"] == pytest.approx((45.0 - room["floor_pattern"]["angle_deg"]) % 360)
    assert SCANDI["floor"].get("params") is None                         # the style itself unchanged
    bath, wet = shell.floor_style({"room_type": "bathroom", "floor_pattern": room["floor_pattern"]},
                                  dict(SCANDI, wet_floor={"material": "tiles_light"}))
    assert wet and "params" not in bath
    assert shell.floor_style({"room_type": "living"}, SCANDI) == (SCANDI["floor"], False)
    assert M.parquet_of(slot["params"]) == slot["params"]["parquet"] and M.parquet_of({"pattern": "x"}) is None
    assert M.parquet_veneer_asset("wood_oak_light") == "oak_veneer_01"


# ---- the node group on a fake bpy that evaluates it ------------------------

class _Sock:
    def __init__(self, node, key, is_output):
        self.node, self.key, self.is_output, self.default_value = node, key, is_output, 0.0


class _Socks(dict):
    def __init__(self, node, is_output):
        super().__init__()
        self.node, self.out = node, is_output

    def __missing__(self, key):
        self[key] = _Sock(self.node, key, self.out)
        return self[key]


class _Node:
    def __init__(self, kind):
        self.bl_idname, self.operation, self.uv_map, self.node_tree = kind, None, None, None
        self.inputs, self.outputs = _Socks(self, False), _Socks(self, True)


class _Tree:
    def __init__(self, name):
        self.name = name
        self.nodes = types.SimpleNamespace(new=self._new)
        self.links = types.SimpleNamespace(new=self._link)
        self.interface = types.SimpleNamespace(new_socket=lambda **kw: None)
        self.all, self.edges = [], {}

    def _new(self, kind):
        self.all.append(_Node(kind))
        return self.all[-1]

    def _link(self, a, b):
        self.edges[id(b)] = a


def _eval(tree, sock, uv, inputs):
    src = tree.edges.get(id(sock)) if not sock.is_output else sock
    if src is None:
        return sock.default_value
    node = src.node

    def inp(key):
        return _eval(tree, node.inputs[key], uv, inputs)
    k = node.bl_idname
    if k == "NodeGroupInput":
        return inputs[src.key]
    if k == "ShaderNodeUVMap":
        return (uv[0], uv[1], 0.0)
    if k == "ShaderNodeSeparateXYZ":
        return inp("Vector")["XYZ".index(src.key)]
    if k == "ShaderNodeCombineXYZ":
        return tuple(float(inp(c)) for c in "XYZ")
    if k == "ShaderNodeTexWhiteNoise":
        return (hash(tuple(round(float(c), 6) for c in inp("Vector"))) % 10007) / 10007.0
    if k == "ShaderNodeMath":
        a, b, c = (float(inp(i)) for i in (0, 1, 2))
        op = node.operation
        return {"ADD": lambda: a + b, "SUBTRACT": lambda: a - b, "MULTIPLY": lambda: a * b,
                "DIVIDE": lambda: a / b if b else 0.0, "FLOOR": lambda: math.floor(a),
                "FLOORED_MODULO": lambda: a - b * math.floor(a / b) if b else 0.0,
                "LESS_THAN": lambda: 1.0 if a < b else 0.0, "MINIMUM": lambda: min(a, b),
                "MAXIMUM": lambda: max(a, b), "MULTIPLY_ADD": lambda: a * b + c}[op]()
    raise KeyError(k)


@pytest.mark.parametrize("pattern", ["herringbone", "chevron"])
def test_the_parquet_node_group_is_the_cells_arithmetic(pattern, monkeypatch):
    groups = {}
    bpy = types.SimpleNamespace(data=types.SimpleNamespace(node_groups=types.SimpleNamespace(
        get=lambda name: groups.get(name), new=lambda name, kind: groups.setdefault(name, _Tree(name)))))
    monkeypatch.setitem(sys.modules, "bpy", bpy)
    tree = PQ.parquet_group(pattern)
    gout = next(n for n in tree.all if n.bl_idname == "NodeGroupOutput")
    params = {"pattern": pattern, "length_m": 0.6, "width_m": 0.12 if pattern == "herringbone" else 0.1,
              "turn_deg": 45.0 if pattern == "herringbone" else 90.0}
    inputs = PQ.group_inputs(params, 1.83)
    rng = random.Random(11)
    noise_of: dict = {}
    for _ in range(400):
        x, y = rng.uniform(-3, 3), rng.uniform(-3, 3)
        c = PQ.cell(pattern, x, y, params)
        vec = _eval(tree, gout.inputs["Vector"], (x, y), inputs)
        seam = _eval(tree, gout.inputs["Seam"], (x, y), inputs)
        rnd = _eval(tree, gout.inputs["Random"], (x, y), inputs)
        noise_of.setdefault(c["plank"], set()).add(round(rnd, 9))
        # Vector = (across, along) in metres + the plank's random offsets (< Repeat)
        assert 0.0 <= vec[0] - c["across_m"] < 1.83 + 1e-9 and 0.0 <= vec[1] - c["along_m"] < 1.83 + 1e-9
        assert seam == pytest.approx(c["seam"], abs=1e-9)
    assert all(len(v) == 1 for v in noise_of.values())        # one random value per plank


# --------------------------------------------------------------------------
# feature walls
# --------------------------------------------------------------------------

def _plan(b, style=SCANDI, decisions=None):
    plans, skipped = FW.plan_feature_walls(b, b["levels"][0], style, decisions)
    return plans, skipped


def test_a_fluted_panel_on_the_bed_wall_keeps_clear_of_a_window():
    b = bedroom(windows=(("win", "n", 0.6, 0.8),))
    plans, _sk = _plan(b)
    (p,) = plans
    assert p["room_id"] == RID and p["wall_id"] == "w_n" and p["kind"] == "fluted" and p["anchor_id"] == "f_L0_001"
    # the face runs along the north wall (y = 5); the window [0.2, 1.0] + 0.30 m margin
    xs = sorted([p["p"][0], p["q"][0]])
    assert xs[0] == pytest.approx(1.30, abs=1e-3) and xs[1] == pytest.approx(4.0 - FW.END_GAP_M, abs=1e-3)
    assert p["p"][1] == pytest.approx(5.0 - FW.FLUTED["wall_gap"], abs=1e-6) and p["n"] == [0.0, -1.0]
    assert p["z0"] == 0.0 and p["z1"] == pytest.approx(2.7 - FW.FLUTED["ceiling_gap"])
    assert p["blocked"] == ["window win"]
    boxes = FW.panel_boxes(p)
    keys = [bx[3] for bx in boxes]
    assert {"wood", "backing", "plinth"} == set(keys) and keys.count("wood") > 60
    for (cx, cy, cz), (sw, sd, sh), _rot, _k in boxes:            # inside the panel's span, depth and height
        assert xs[0] - 1e-6 <= cx - sw / 2 and cx + sw / 2 <= xs[1] + 1e-6
        assert 5.0 - p["depth_m"] - 1e-6 <= cy - sd / 2 and cy + sd / 2 <= 5.0
        assert p["z0"] <= cz - sh / 2 + 1e-9 and cz + sh / 2 <= p["z1"] + 1e-9


def test_the_slats_never_overlap_and_stay_between_the_end_boards():
    slats = FW.slat_layout(2.7, FW.FLUTED)
    assert slats[0][0] >= FW.FLUTED["end_w"] - 1e-9 and slats[-1][1] <= 2.7 - FW.FLUTED["end_w"] + 1e-9
    assert all(b0 >= a1 - 1e-9 for (_a0, a1), (b0, _b1) in zip(slats, slats[1:]))
    pitch = (slats[-1][0] - slats[0][0]) / (len(slats) - 1)
    assert 0.030 <= pitch <= 0.040                                  # a 3-4 cm fluted pitch
    assert FW.slat_layout(2.0, FW.FAMILY_FEATURE_WALLS["japandi"])[0][1] - \
        FW.slat_layout(2.0, FW.FAMILY_FEATURE_WALLS["japandi"])[0][0] == pytest.approx(0.04)


def test_a_tall_piece_against_the_wall_cuts_the_panel_and_a_short_stretch_keeps_the_paint():
    b = bedroom(furniture=[("wardrobe", (3.6, 4.7), 0.0, (0.8, 0.6))])
    b["furniture"][-1]["height"] = 2.1
    (p,), _ = _plan(b)
    assert max(p["p"][0], p["q"][0]) <= 3.2 + 1e-6 and "wardrobe f_L0_004" in p["blocked"]
    b = bedroom(windows=(("w1", "n", 0.9, 1.2), ("w2", "n", 3.1, 1.2)))
    plans, skipped = _plan(b)
    assert plans == [] and "the panel needs" in skipped[0]["reason"]


def test_a_classic_home_gets_a_painted_wainscot_in_its_accent_colour():
    (p,), _ = _plan(bedroom(), dict(SCANDI, family="classic"))
    assert p["kind"] == "wainscot" and p["z1"] == pytest.approx(p["z0"] + FW.WAINSCOT["height"])
    assert p["spec"]["colour"] == "pale dusty blue"
    boxes = FW.panel_boxes(p)
    assert {bx[3] for bx in boxes} == {"paint"} and len(boxes) > 6           # board, cap rail and the frames


def test_the_brief_the_recipe_and_a_low_slope_turn_the_panel_off():
    b = bedroom()
    assert _plan(b, dict(SCANDI, feature_wall="none"))[0] == []
    assert _plan(b, dict(SCANDI, wall_accent={"material": "paint", "colour": "sage"}))[0] == []
    assert _plan(b, dict(SCANDI, wall_accent={"material": "wood_slat"}))[0][0]["kind"] == "fluted"
    assert _plan(b, dict(SCANDI, family="industrial"))[0] == []
    plans, skipped = _plan(b, SCANDI, {RID: {"feature_wall": False, "feature_wall_why": "photos: no panelling"}})
    assert plans == [] and skipped[0]["reason"] == "photos: no panelling"
    low = copy.deepcopy(b)
    low["levels"][0]["ceiling_planes"] = [(0.0, 0.0, 1.9)]
    plans, skipped = _plan(low)
    assert plans == [] and "fluted panel needs" in skipped[0]["reason"]


def test_wall_art_on_a_panel_stands_off_it_and_a_dado_leaves_art_above_it():
    b = bedroom()
    (p,), _ = _plan(b)
    art = {"id": "dec_1", "type": "wall_art", "level_id": "L0", "room_id": RID, "wall_point": [2.0, 5.0],
           "center": [2.0, 4.98], "bottom_m": 1.1}
    other = dict(art, id="dec_2", level_id="L1")
    out, notes = FW.standoff_decor([art, other, {"id": "x", "type": "vase"}], [p])
    assert out[0]["wall_point"][1] == pytest.approx(5.0 - p["depth_m"]) and out[0]["feature_wall_standoff_m"] > 0.02
    assert out[1] is other and out[2]["id"] == "x" and len(notes) == 1
    (w,), _ = _plan(b, dict(SCANDI, family="classic"))
    assert FW.standoff_decor([art], [w])[0][0] is art                 # hung above the 1.0 m dado
    room = dict(b["rooms"][0], feature_wall=FW.summary(p))
    assert FW.finish_depth_at(room, (2.0, 5.0), 1.2) == pytest.approx(p["depth_m"], abs=1e-3)
    assert FW.finish_depth_at(room, (4.3, 5.0), 1.2) == 0.0 and FW.finish_depth_at(room, (2.0, 2.5), 1.2) == 0.0
    assert FW.finish_depth_at(room, (2.0, 5.0), 3.5) == 0.0                    # above the panel


def test_a_face_runs_over_collinear_wall_segments():
    b = bedroom()
    w_n = next(w for w in b["walls"] if w["id"] == "w_n")
    b["walls"].remove(w_n)
    b["walls"] += [dict(w_n, id="w_n1", start=[4.2, 5.1], end=[2.5, 5.1]),
                   dict(w_n, id="w_n2", start=[2.5, 5.1], end=[-0.2, 5.1])]
    face = FW.face_of(b["rooms"][0], b["walls"][-2], b["walls"])
    assert face["length"] == pytest.approx(4.0, abs=1e-6)
    assert FW.face_of(b["rooms"][0], b["walls"][-2])["length"] == pytest.approx(1.5, abs=1e-6)


# --------------------------------------------------------------------------
# the decor stage's dressing
# --------------------------------------------------------------------------

def _dressed_bedroom(extra_decor=(), style=SCANDI, ceiling=2.7):
    b = bedroom(ceiling=ceiling)
    b["decor"] = [{"id": "dec_L0_001", "kind": "decor", "type": "curtain", "level_id": "L0", "room_id": RID,
                   "center": [2.0, 0.1, 0.01], "rotation_deg": 0.0, "size": [2.0, 0.08, 2.24], "window_id": "win",
                   "reason": "curtains at window win"},
                  {"id": "dec_L0_002", "kind": "decor", "type": "throw", "level_id": "L0", "room_id": RID,
                   "host_id": "f_L0_001", "slot": "f_L0_001.throw", "colour": "beige", "center": [2.0, 3.28],
                   "rotation_deg": 0.0, "size": [1.52, 0.5, 0.05]},
                  {"id": "dec_L0_003", "kind": "decor", "type": "ceiling_light", "level_id": "L0", "room_id": RID,
                   "rule": "decor.ceiling_lights", "anchor_ids": ["f_L0_001"], "center": [2.0, 4.0, 2.58],
                   "size": [0.4, 0.4, 0.12], "reason": "lighting rule: over the bed"},
                  {"id": "dec_L0_004", "kind": "decor", "type": "ceiling_light", "level_id": "L0", "room_id": RID,
                   "rule": "decor.ceiling_lights", "center": [2.0, 1.2, 2.58], "size": [0.4, 0.4, 0.12],
                   "reason": "lighting rule: general light for the area"}] + list(extra_decor)
    ids = iter(range(50, 99))
    return DR.dress(b, style, None, lambda lv: f"dec_{lv}_{next(ids):03d}")


def test_curtains_hang_in_two_layers_on_a_ceiling_track():
    b, notes = _dressed_bedroom()
    c = next(d for d in b["decor"] if d["type"] == "curtain")
    assert c["layers"] == ["sheer", "drape"] and c["track"] == "ceiling"
    assert c["size"][2] == pytest.approx(2.7 - DR.TRACK_CLEAR_M - 0.01) and c["size"][1] == DR.LAYERED_DEPTH_M
    assert any("ceiling track" in n for n in notes)
    rustic, _ = _dressed_bedroom(style=dict(SCANDI, family="rustic"))      # layered, on its rod
    c = next(d for d in rustic["decor"] if d["type"] == "curtain")
    assert c["layers"] == ["sheer", "drape"] and "track" not in c and c["size"][2] == 2.24
    industrial, _ = _dressed_bedroom(style=dict(SCANDI, family="industrial"))
    assert "layers" not in next(d for d in industrial["decor"] if d["type"] == "curtain")


def test_the_bed_is_layered_and_the_lights_take_their_roles():
    b, notes = _dressed_bedroom()
    bed = next(f for f in b["furniture"] if f["type"] == "bed_double")
    assert bed["bedding_layers"]["euro_shams"] == 2
    throw = next(d for d in b["decor"] if d["type"] == "throw")
    assert throw["layers"] == 2 and throw["accent_colour"] == "charcoal"
    over = next(d for d in b["decor"] if d["id"] == "dec_L0_003")
    assert over["fixture"] == "statement" and over["type"] == "pendant_light"
    assert over["center"][2] == DR.STATEMENT_BOTTOM_M and over["size"][2] == pytest.approx(0.7)
    down = next(d for d in b["decor"] if d["id"] == "dec_L0_004")
    assert down["fixture"] == "downlight" and down["size"] == list(DR.DOWNLIGHT_SIZE)
    assert down["center"][2] == pytest.approx(2.7 - DR.DOWNLIGHT_SIZE[2])
    bedside = [d for d in b["decor"] if d.get("fixture") == "bedside"]
    assert len(bedside) == 2 and all(d["type"] == "pendant_light" and d["center"][2] == pytest.approx(1.05)
                                     for d in bedside)
    lights = [d for d in b["decor"] if d["type"] in DR.LIGHT_TYPES]
    for a in lights:                                  # the lights plan's spacing is kept
        for c in lights:
            if a is not c:
                assert math.dist(a["center"][:2], c["center"][:2]) >= DR.FIXTURE_GAP_M - 1e-9
    assert b["dressing"]["lesson"] == "UL106"


def test_no_bedside_pendants_beside_a_table_lamp_or_too_close_to_a_light():
    lamp = {"id": "dec_L0_009", "kind": "decor", "type": "table_lamp", "level_id": "L0", "room_id": RID,
            "host_id": "f_L0_002", "center": [0.95, 4.79], "size": [0.3, 0.3, 0.5]}
    b, _ = _dressed_bedroom([lamp])
    assert not [d for d in b["decor"] if d.get("fixture") == "bedside"]
    near = {"id": "dec_L0_010", "kind": "decor", "type": "ceiling_light", "level_id": "L0", "room_id": RID,
            "rule": "x", "center": [1.2, 4.0, 2.58], "size": [0.4, 0.4, 0.12]}
    b, notes = _dressed_bedroom([near])
    assert not [d for d in b["decor"] if d.get("fixture") == "bedside"] and any("spacing" in n for n in notes)


def test_the_recipe_decides_the_feature_wall():
    room = {"id": RID, "room_type": "bedroom"}
    b = {"rooms": [room]}
    photos = {"source": "photos", "n": 8, "layers": {"wall_panelling": {"share": 0.625}},
              "palette": {"floor": {"value": "light_wood"}}}
    assert DR.finish_decisions(b, SCANDI, lambda r: photos)[RID]["feature_wall"] is True
    none = dict(photos, layers={"wall_panelling": {"share": 0.1}}, palette={"floor": {"value": "stone_tile"}})
    dec = DR.finish_decisions(b, SCANDI, lambda r: none)[RID]
    assert dec["feature_wall"] is False and dec["floor_pattern"] is False
    assert DR.finish_decisions(b, SCANDI, lambda r: {"source": "default", "n": 0}) == {}


# --------------------------------------------------------------------------
# the builders' pure parts
# --------------------------------------------------------------------------

def test_a_layered_curtain_has_its_sheer_behind_the_drape_under_a_track():
    parts = P.curtain_parts(2.4, 0.14, 2.69, item={"layers": ["sheer", "drape"], "track": "ceiling"})
    keys = [p["key"] for p in parts]
    assert keys[0] == "painted" and keys.count("sheer") == 2 and keys.count("colour_fabric") == 2
    sheer_y = [v[1] for p in parts if p["key"] == "sheer" for v in p["verts"]]
    drape_y = [v[1] for p in parts if p["key"] == "colour_fabric" for v in p["verts"]]
    assert min(sheer_y) > max(drape_y) - 1e-9                          # the sheer on the window side (+Y)
    plain = P.curtain_parts(2.4, 0.08, 2.2)
    assert [p["key"] for p in plain] == ["steel", "colour_fabric", "colour_fabric"]
    assert [p["key"] for p in P.decor_parts("ceiling_light", 0.09, 0.09, 0.012, {"fixture": "downlight"})] == \
        ["painted", "bulb"]


def _bed_caster(headboard=True):
    from wenart.blender import geom2d

    parts = [geom2d.box((0.0, 0.0, 0.25), (1.6, 2.0, 0.5))]
    if headboard:
        parts.append(geom2d.box((0.0, 1.03, 0.55), (1.6, 0.06, 1.1)))
    v, f = geom2d.merge(parts)
    return R.MeshCaster(v, f)


HOST = {"center": [0.0, 0.0], "size": [1.6, 2.0], "rotation_deg": 0.0}


def test_euro_shams_stand_against_a_headboard_and_the_pillows_lean_on_them():
    plan = T.duvet_and_pillows(_bed_caster(), HOST, 0.0, shams=2)
    assert plan is not None and plan["record"]["euro_shams"] == 2
    shams = [p for p in plan["parts"] if p.get("role") == T.SHAM_ROLE]
    pillows = [p for p in plan["parts"] if p.get("role") == "pillow"]
    assert len(shams) == 2 and len(pillows) == 2
    assert max(v[1] for p in pillows for v in p["verts"]) <= max(v[1] for p in shams for v in p["verts"])
    assert min(v[2] for p in shams for v in p["verts"]) >= 0.5 - 0.02          # on the mattress
    plain = T.duvet_and_pillows(_bed_caster(headboard=False), HOST, 0.0, shams=2)
    assert plain is not None and plain["record"]["euro_shams"] == 0             # no headboard: no shams
    assert T.lean_parts(plan["parts"])[1] and T.sham_mesh(plan["parts"])[1]


def test_a_layered_throw_lays_its_second_blanket_on_the_first():
    item = {"center": [0.0, -0.7], "size": [1.52, 0.5, 0.05], "layers": 2, "type": "throw"}
    got = T.throw_parts(_bed_caster(), HOST, item, 0.0)
    assert len(got["parts"]) == 2 and got["parts"][1]["key"] == T.RUNNER_KEY
    top1 = max(v[2] for v in got["parts"][0]["verts"])
    assert max(v[2] for v in got["parts"][1]["verts"]) > top1                 # it lies over the first throw
    plan = R.plan_throw(item, {"id": "bed", "type": "bed_double", "footprint": dict(HOST)}, _bed_caster(), 0.0)
    assert "not_rested" not in plan
    assert len(plan["verts"]) == sum(len(p["verts"]) for p in plan["parts"])
    from wenart.blender import furniture as F

    assert F.part_colour({"colour": "beige", "accent_colour": "charcoal"}, T.RUNNER_KEY) == "charcoal"
    assert F.part_colour({"colour": "beige", "accent_colour": "charcoal"}, "colour_fabric") == "beige"


# --------------------------------------------------------------------------
# the fit, the cameras, the judge and the checks
# --------------------------------------------------------------------------

def test_the_fits_light_roles():
    assert FIT.is_statement_title("Roll Hill - Modo Chandelier - 3 Sided 10 Globes")
    assert FIT.is_statement_title("Amazon Brand - Rivet Hugh Mid-Century Modern 3-Light Pendant Chandelier")
    assert not FIT.is_statement_title("Stone & Beam Industrial Farmhouse Double Pendant")       # no "arm" in farm
    fits = [({"id": "a", "title": "wire pendant light", "bbox_m": [0.6, 0.6, 0.7]}, {}),
            ({"id": "b", "title": "Coco Bead Chandelier", "bbox_m": [0.5, 0.5, 0.4]}, {}),
            ({"id": "c", "title": "Gubi Semi Pendant", "bbox_m": [0.14, 0.14, 0.99]}, {})]
    assert [e["id"] for e, _f in FIT.fixture_pool(fits, {"fixture": "statement"})[0]] == ["b"]
    assert [e["id"] for e, _f in FIT.fixture_pool(fits, {"fixture": "bedside"})[0]] == ["c"]
    assert FIT.fixture_pool(fits, {})[0] == fits
    assert FIT.fit_decor_item({"type": "ceiling_light", "size": [0.09, 0.09, 0.012], "fixture": "downlight"},
                              None) is None
    assert FIT.decor_pick_key({"type": "pendant_light", "room_id": "r", "fixture": "bedside"}) == \
        "r:pendant_light:bedside"
    assert FIT.decor_pick_key({"type": "pendant_light", "room_id": "r"}) == "r:pendant_light"


def test_an_interior_camera_aimed_up_or_down_is_levelled_with_a_lens_shift():
    plan = {"name": "c", "kind": "interior", "room_id": "r", "position": [1.0, 1.0, 1.25],
            "target": [4.0, 1.0, 1.25 - 3.0 * math.tan(math.radians(10.0))], "lens_mm": 18.0, "sensor_mm": 36.0,
            "shift_y": 0.0}
    rec = CAM.level_interior(plan)
    assert rec["pitch_deg_was"] == pytest.approx(-10.0, abs=1e-6) and plan["target"][2] == 1.25
    assert plan["shift_y"] == pytest.approx(18.0 * math.tan(math.radians(-10.0)) / 36.0, abs=1e-4)
    assert plan["pitch_deg"] == 0.0 and plan["levelled"] == rec
    assert CAM.level_interior(plan) is None                                     # level now
    steep = dict(plan, target=[2.0, 1.0, 0.0], shift_y=-0.1)
    CAM.level_interior(steep)
    assert steep["shift_y"] == -CAM.INTERIOR_SHIFT_MAX
    ext = {"name": "ext_1", "kind": "exterior", "position": [0, 0, 1.6], "target": [10, 0, 0]}
    assert CAM.level_interior(ext) is None and ext["target"] == [10, 0, 0]
    rot = {"name": "r", "kind": "interior", "room_id": "r", "position": [0, 0, 1.25],
           "rotation_euler_deg": [80.0, 0.0, 30.0], "lens_mm": 18.0}
    CAM.level_interior(rot)
    assert rot["rotation_euler_deg"] == [90.0, 0.0, 30.0] and rot["shift_y"] < 0
    agent = O.fixed_plan({"view_id": "cam_x", "action": "set", "kind": "interior", "room_id": "r",
                          "position": [1.0, 1.0, 1.25], "target": [3.0, 1.0, 1.6]}, "L0")
    assert agent["target"][2] == 1.25 and agent["shift_y"] > 0 and agent["levelled"]["pitch_deg_was"] > 0


def test_the_judge_asks_the_professional_bar_of_living_rooms_and_bedrooms():
    text = J.pro_bar_text("bedroom")
    for word in ("fluted", "herringbone", "sheer", "euro shams", "statement", "downlights", "missing layer"):
        assert word in text
    assert J.pro_bar_text("kitchen") == "" and J.pro_bar_text(None) == ""
    from wenart.agent import prompts as PR

    room = {"id": "r1", "label": "Bedroom", "room_type": "bedroom", "area_computed": 14.0}
    assert "fluted" in PR.room_look_prompt(room, [], ["cam_1"], ["the render"], [])        # the inspector's critic
    assert "fluted" not in PR.room_look_prompt(dict(room, room_type="kitchen"), [], ["cam_1"], ["the render"], [])
    assert {"D3", "V1"} <= set(PR.ROOM_LOOK_CHECKS)
    # a missing layer is the decor stage's and the build's dressing, never a model swap
    assert CS.cause_of({"check": "D3", "target": "r1", "message": "missing layer: feature wall"}, {}) == "decor_look"
    assert CS.cause_of({"check": "D3", "target": "r1", "message": "a third wood tone"}, {}) == "wrong_model"


def _manifest(panel: bool):
    objs = [{"kind": "wall", "detail": "feature_wall", "room_id": RID}] if panel else [{"kind": "wall"}]
    return {"objects": objs, "style_profile": dict(SCANDI)}


def test_u23_and_m23_measure_the_professional_bar():
    b, _ = _dressed_bedroom()
    PQ.annotate(b, SCANDI)
    found, n = DR.review(b, _manifest(False))
    assert n == 1 and found[0]["missing"] == ["no fluted panel on the accent wall"]
    assert DR.review(b, _manifest(True))[0] == []
    bare = bedroom()
    bare["decor"] = [{"id": "c", "type": "curtain", "room_id": RID}, {"id": "t", "type": "throw", "room_id": RID,
                                                                       "host_id": "f_L0_001"}]
    bare["dressing"] = {"family": "scandinavian", "rooms": {}}
    (f,), _n = DR.review(bare, _manifest(True))
    assert any("herringbone" in m for m in f["missing"]) and any("one layer" in m for m in f["missing"])
    got = LS.audit(bare, _manifest(True))
    assert got["checked"]["U23"] == 1 and LS.CHECK_LESSONS["U23"] == ("UL106",)
    u23 = next(x for x in got["findings"] if x["check"] == "U23")
    assert u23["kind"] == "taste" and u23["evidence"]["lesson"] == "UL106"
    assert LS.audit(bare, None)["checked"]["U23"] == "no scene manifest: not run"
    rec = MR.review(bare, _manifest(True))
    assert "M23" in MR.CHECKS and rec["checks"]["M23"]["failed"] == 1
    assert next(x for x in rec["findings"] if x["check"] == "M23")["kind"] == "taste"
    assert K.kind_of({"check": "M23"}) == "taste" and CS.CHECK_CAUSE["M23"] == "decor_look"


def test_the_decor_stage_fingerprint_holds_the_dressing():
    assert "wenart/furniture/dressing.py" in ST.DECOR_CODE
    assert M.sheer_density(True) < 0.5 <= 0.5 and M.sheer_density(False) < M.sheer_density(True)
