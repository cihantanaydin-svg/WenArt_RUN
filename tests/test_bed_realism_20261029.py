"""A full, realistic bed (29 Oct 2026, lesson UL121; user, sending a photo of a full, soft bed: "look how realistic the
bed is looking full and nice I want this much detail in our models"; docs/reference_details_20261029.md R35, R36):
the style families' bedding table, the bed's free sides, the soft deep duvet with its rounded edge, folds and side
overhang, the pillow set per family resting against the headboard and each other, the woven and fringed throw pair,
the fabric looks, a made-up library bed measured against ours, the drum nightstand's decor set, the checks M30 and U34,
and real06's beds. CPU only: synthetic beds on the pure ray caster (``rest.MeshCaster``), synthetic rooms
(tests/_m11_room.py) and, when the main repository holds it, real06's run 20261029-100801-full."""
from __future__ import annotations

import copy
import json
import math
import sys
import types
from collections import Counter
from pathlib import Path

import numpy as np
import pytest

import _m11_room as M
from wenart.blender import bedding_parts as BP
from wenart.blender import geom2d
from wenart.blender import rest as R
from wenart.blender import textiles as T
from wenart.furniture import bedding as BG
from wenart.style import colours as COL

ROOT = Path(__file__).resolve().parents[1]
RUN = Path("/home/user/WenArt_RUN/runs/20261029-100801-full/results")
REAL06_BUILT = RUN / "renders" / "real06" / "building_built.json"
REAL06_MANIFEST = RUN / "renders" / "real06" / "scene_manifest.json"

BED_C = (2.5, 3.0)                   # a 1.6 x 2.0 m bed, its head on the north wall (y = 4.0) of the 5 x 4 m room
HOST = {"center": list(BED_C), "size": [1.6, 2.0], "rotation_deg": 0.0}


def bed_caster(center=BED_C, headboard: bool = True, top: float = 0.5):
    parts = [geom2d.box((center[0], center[1], top / 2.0), (1.6, 2.0, top))]
    if headboard:
        parts.append(geom2d.box((center[0], center[1] + 1.03, 0.55), (1.6, 0.06, 1.1)))
    v, f = geom2d.merge(parts)
    return R.MeshCaster(v, f)


def bed_piece(center=BED_C, pid="f_L0_001", **extra):
    return M.fp(pid, "bed_double", center, (1.6, 2.0), rotation=0.0, **extra)


def room(*pieces, w: float = 5.0, h: float = 4.0) -> dict:
    return M.building(w=w, h=h, room_type="bedroom", window=None, furniture=list(pieces))


def mesh_of(parts) -> tuple[list, list]:
    verts, faces = [], []
    for p in parts:
        off = len(verts)
        verts += [tuple(v) for v in p["verts"]]
        faces += [[i + off for i in f] for f in p["faces"]]
    return verts, faces


def roles(plan) -> Counter:
    return Counter(p["role"] for p in plan["parts"])


# --------------------------------------------------------------------------
# the family table
# --------------------------------------------------------------------------

def test_every_family_has_its_set_with_a_reason_real_looks_and_colour_names():
    from wenart.furniture import dressing as DR

    assert set(DR.FAMILY_BLANKET) <= set(BP.FAMILY_BEDDING)                      # every family the dressing knows
    for fam, row in BP.FAMILY_BEDDING.items():
        assert row["why"] and len(row["why"]) > 40, fam
        assert row["duvet"]["look"] in BP.LOOKS and 0.04 <= row["duvet"]["thickness_m"] <= 0.08, fam
        assert 0.0 < row["duvet"]["wrinkle_m"] <= 0.02 and 0.03 <= row["duvet"]["hem_m"] <= BP.HEM_MAX_M, fam
        for part in [row["duvet"], row["shams"], row["pillows"], *(row["accent"]), *([row["lumbar"]] if row["lumbar"]
                                                                                      else [])]:
            assert part["look"] in BP.LOOKS and COL.known(part["colour"]), (fam, part)
        assert row["throw"]["pattern"] in BP.PATTERNS and row["throw"]["runner_look"] in BP.LOOKS, fam
        assert 1 <= len(row["accent"]) <= 2, fam
    # the textured cushion of the photo (a knit or boucle one) in every family's accent set
    assert all(any(a["look"] in ("knit", "boucle", "velvet", "linen") for a in row["accent"])
               for row in BP.FAMILY_BEDDING.values())
    spec, why = BP.family_spec("baroque")
    assert spec["family"] == BP.DEFAULT_FAMILY and "no bedding row" in why
    assert BP.family_spec("Scandinavian")[0]["family"] == "scandinavian"


def test_what_a_bed_takes_follows_its_width():
    spec = BP.family_spec("modern")[0]
    assert BP.counts(spec, 1.6) == {"euro_shams": 2, "pillows": 2, "accent": 0, "lumbar": 1}     # UL163: five at most
    assert BP.counts(spec, 0.9) == {"euro_shams": 0, "pillows": 1, "accent": 1, "lumbar": 0}     # one pillow, one cushion
    assert BP.counts(BP.family_spec("japandi")[0], 1.6)["lumbar"] == 0                 # restrained: no lumbar
    assert BP.counts(spec, 0.8)["lumbar"] == 0


# --------------------------------------------------------------------------
# the sides and the duvet's overhang
# --------------------------------------------------------------------------

def test_a_side_with_a_piece_or_a_wall_along_the_duvet_is_blocked_the_others_free():
    dresser = M.fp("f_L0_002", "dresser", (1.45, 2.6), (1.0, 0.5), rotation=90.0)      # touches the left side mid-bed
    stand = M.fp("f_L0_003", "nightstand", (3.55, 3.75), (0.45, 0.4))                 # beside the head: not in the span
    b = room(bed_piece(), dresser, stand)
    sides = BP.bed_sides(b["furniture"][0], b)
    assert sides["left"] == {"clear_m": 0.0, "by": "f_L0_002", "free": False}
    assert sides["right"]["free"] and sides["right"]["by"] is None                     # the nightstand is at the head
    assert sides["foot"]["free"]
    # against the west wall (its inner face at x = 0): the left side is blocked by the wall
    b2 = room(bed_piece(center=(0.8, 3.0)))
    s2 = BP.bed_sides(b2["furniture"][0], b2)
    assert not s2["left"]["free"] and s2["left"]["by"] == "w_w" and s2["left"]["clear_m"] == pytest.approx(0.0)
    # a nightstand pushed down the side into the duvet's span blocks that side
    b3 = room(bed_piece(), M.fp("f_L0_004", "nightstand", (3.52, 2.9), (0.4, 0.42)))
    s3 = BP.bed_sides(b3["furniture"][0], b3)
    assert not s3["right"]["free"] and s3["right"]["by"] == "f_L0_004"
    # a turned bed: the sides are its own (front frame), not the world's
    turned = M.fp("f_L0_005", "bed_double", (3.7, 2.0), (1.6, 2.0), rotation=90.0)     # foot towards +x (x = 4.7)
    s4 = BP.bed_sides(turned, room(turned))
    assert s4["foot"] == {"clear_m": pytest.approx(0.3, abs=1e-3), "by": "w_e", "free": True}
    assert s4["left"]["by"] is None and s4["right"]["by"] is None
    near = M.fp("f_L0_006", "bed_double", (3.9, 2.0), (1.6, 2.0), rotation=90.0)       # 0.1 m from the wall: tucked
    assert not BP.bed_sides(near, room(near))["foot"]["free"]


def test_the_duvet_hangs_almost_to_the_floor_on_free_sides_and_stops_at_a_neighbour():
    dresser = M.fp("f_L0_002", "dresser", (1.45, 2.6), (1.0, 0.5), rotation=90.0)
    b = room(bed_piece(), dresser)
    sides = BP.bed_sides(b["furniture"][0], b)
    spec = BP.family_spec("modern")[0]
    plan = T.bedding_set(bed_caster(), HOST, 0.0, spec, sides)
    rec = plan["record"]
    hem = spec["duvet"]["hem_m"]
    assert rec["drops"]["left"]["drop_m"] == 0.0                                     # never through the dresser
    for side in ("right", "foot"):
        assert rec["drops"][side]["hem_over_floor_m"] == pytest.approx(hem, abs=0.015), side   # almost to the floor
        assert rec["drops"][side]["hem_over_floor_m"] <= BP.HEM_MAX_M
    duvet = next(p for p in plan["parts"] if p["role"] == "duvet")
    xs = [v[0] for v in duvet["verts"]]
    assert min(xs) >= 1.7 - 0.03                                                     # the dresser's face at x = 1.7
    assert max(xs) > 3.3 + spec["duvet"]["thickness_m"]                               # outside the right side
    assert R.penetration(bed_caster(), duvet["verts"]) <= 0.002                       # never into the bed
    # the duvet still covers the foot share and ends before the pillows; the turned-down band stays
    assert rec["duvet_rect_local"][3] <= -1.0 + T.DUVET_SHARE * 2.0 + 1e-6
    assert roles(plan)["turndown"] == 1 and rec["head_problems"] == []
    # every side free: it hangs on all three
    free = T.bedding_set(bed_caster(), HOST, 0.0, spec, None)["record"]["drops"]
    assert all(free[s]["drop_m"] > 0.35 for s in BP.SIDES)


def test_the_duvet_has_volume_a_rounded_edge_and_the_same_folds_every_build():
    spec = BP.family_spec("scandinavian")[0]
    a = T.bedding_set(bed_caster(), HOST, 0.0, spec, None)
    b = T.bedding_set(bed_caster(), HOST, 0.0, spec, None)
    da = next(p for p in a["parts"] if p["role"] == "duvet")
    db = next(p for p in b["parts"] if p["role"] == "duvet")
    assert da["verts"] == db["verts"]                                                 # deterministic
    top = np.asarray(da["verts"][:len(da["verts"]) // 2])                             # the cloth's top layer
    loc = top - np.array([BED_C[0], BED_C[1], 0.0])
    on = (np.abs(loc[:, 0]) < 0.5) & (loc[:, 1] < 0.3) & (loc[:, 1] > -0.7)
    thick = spec["duvet"]["thickness_m"]
    assert loc[on, 2].min() >= 0.5 + T.CLOTH_OFFSET_M + thick - 1e-6                  # its volume over the mattress
    assert 0.003 < float(np.ptp(loc[on, 2])) <= spec["duvet"]["wrinkle_m"] + 1e-6     # gentle folds, never into it
    # the edge rounds: right over the side face, points between the top and 5 cm below it, out of the side
    edge = (loc[:, 0] > 0.8) & (loc[:, 2] > 0.45) & (loc[:, 2] < 0.5 + thick)
    assert edge.sum() >= 4
    assert float(loc[edge, 0].min()) < 0.8 + T.CLOTH_OFFSET_M + thick - 0.01            # on the arc, not a square fold
    # the hanging side's flutes: out of the side, never into it (away from the foot's corner)
    hang = (loc[:, 0] > 0.8) & (loc[:, 2] < 0.3) & (loc[:, 1] > -0.9)
    assert float(loc[hang, 0].min()) >= 0.8 + T.CLOTH_OFFSET_M + thick - 1e-6
    assert float(np.ptp(loc[hang, 0])) > 0.01


# --------------------------------------------------------------------------
# the pillow set
# --------------------------------------------------------------------------

@pytest.mark.parametrize("fam", ["modern", "scandinavian", "japandi", "classic", "minimal"])
def test_the_pillow_set_follows_the_family_and_every_piece_rests_without_cutting(fam):
    spec = BP.family_spec(fam)[0]
    plan = T.bedding_set(bed_caster(), HOST, 0.0, spec, None)
    want = BP.counts(spec, 1.6)
    got = roles(plan)
    assert got[T.SHAM_ROLE] == want["euro_shams"] and got["pillow"] == want["pillows"]
    assert got[T.ACCENT_ROLE] == want["accent"] and got[T.LUMBAR_ROLE] == want["lumbar"]
    assert plan["record"]["set"] == want and plan["record"]["explained"] == {}
    assert plan["record"]["pillows_upright"] is True                                  # standing against the shams
    keys = {p["role"]: p["key"] for p in plan["parts"]}
    assert keys[T.SHAM_ROLE] == BP.textile_key(spec["shams"]["look"])
    assert keys["pillow"] == BP.textile_key(spec["pillows"]["look"])
    assert keys["duvet"] == BP.textile_key(spec["duvet"]["look"])
    bed = bed_caster()
    soft = [p for p in plan["parts"] if p["role"] in ("pillow", T.SHAM_ROLE, T.ACCENT_ROLE, T.LUMBAR_ROLE)]
    for p in soft:                     # measured on the bed, the band and the other pillows (the duvet lies in front)
        others = mesh_of([q for q in plan["parts"] if q is not p and q["role"] != "duvet"])
        host = R.MultiCaster([bed, R.MeshCaster(*others)])
        arr = np.asarray(p["verts"])
        lo, hi = arr.min(axis=0), arr.max(axis=0)
        foot = {"center": [float((lo[0] + hi[0]) / 2), float((lo[1] + hi[1]) / 2)],
                "size": [float(hi[0] - lo[0]) * 0.8, float(hi[1] - lo[1]) * 0.5], "rotation_deg": 0.0}
        m = R.measure_rest(p["verts"], p["faces"], host, foot, True)
        assert R.rest_ok(m)[0], (fam, p["role"], m)                                    # no floating, no cutting
        assert hi[1] <= BED_C[1] + 1.0 + 1e-6                                          # never into the headboard
    # the accent cushions and the lumbar lean on what is behind them (their upper part rests)
    for a in plan["record"]["accent"] + ([plan["record"]["lumbar"]] if plan["record"]["lumbar"] else []):
        assert a["upper_gap_m"] <= BP.STACK_BACK_GAP_M and a["contact_m"] >= -BP.STACK_PRESS_M - 1e-6
    # the AI's cushion colours go to the set's cushions first (30 Oct 2026, UL163: against the shams the lumbar alone)
    coloured = T.bedding_set(bed_caster(), HOST, 0.0, spec, None, colours=["mustard"])
    front = coloured["record"]["accent"] + ([coloured["record"]["lumbar"]] if coloured["record"]["lumbar"] else [])
    assert not front or front[0]["colour"] == "mustard"


def test_a_bed_without_a_headboard_has_no_shams_and_says_why():
    spec = BP.family_spec("modern")[0]
    plan = T.bedding_set(bed_caster(headboard=False), HOST, 0.0, spec, None)
    assert plan["record"]["euro_shams"] == 0 and "headboard" in plan["record"]["explained"]["euro_shams"]
    assert plan["record"]["pillows_upright"] is False and roles(plan)["pillow"] == 2   # lying, as before
    assert all(y > 0.3 for y in plan["record"]["pillow_local_y"])


def test_pillows_are_plump_closed_meshes_not_boxes():
    p = BP.plump_cushion(0.45, 0.15, 0.45, key="x", role="accent_cushion")
    v = np.asarray(p["verts"])
    assert v[:, 2].min() == pytest.approx(0.0) and v[:, 0].max() <= 0.225 + 1e-9
    centre = (np.abs(v[:, 0]) < 0.05) & (np.abs(v[:, 2] - v[:, 2].max() / 2.0) < 0.05)
    rim = (np.abs(v[:, 0]) > 0.2)
    assert np.ptp(v[centre, 1]) > 0.13 and np.ptp(v[rim, 1]) < 0.06     # full in the middle, thin at the seam
    edges = Counter()
    for f in p["faces"]:
        for a, b in zip(f, f[1:] + f[:1]):
            edges[tuple(sorted((a, b)))] += 1
    assert set(edges.values()) == {2}                                                  # closed (watertight)
    # the sides are drawn in between the corners (soft "ears")
    mid_side = v[(np.abs(v[:, 2] - 0.225) < 0.02) & (v[:, 0] > 0)][:, 0].max()
    assert mid_side < 0.225 - 0.005


# --------------------------------------------------------------------------
# the throw pair: the woven pattern and the fringe
# --------------------------------------------------------------------------

def test_the_throw_pair_by_family_and_its_fringe_and_pattern_as_built():
    w = BP.throw_weave("modern")
    assert w["pattern"] == "houndstooth" and w["fringe"] is True and w["runner_look"] == "knit"
    assert BP.throw_weave("scandinavian")["pattern"] == "stripe"
    assert BP.throw_weave("minimal")["fringe"] is False
    caster = bed_caster()
    item = {"center": [BED_C[0], BED_C[1] - 0.7], "size": [1.52, 0.5, 0.05], "layers": 2, "type": "throw",
            "weave": w}
    # 30 Oct 2026 (UL146, P14): a layered pair on a bed with a free side: the plain blanket over the foot (S5 measures
    # parts[0]), hanging down the free sides and the foot, and the patterned throw draped at the right side with its
    # fringe at both ends (on the top and under its hem)
    got = T.throw_parts(caster, HOST, item, 0.0)
    keys = [(p["key"], p["role"]) for p in got["parts"]]
    assert keys[0] == (BP.runner_key("knit"), "throw") and got["weave"]["layout"] == "p14"
    assert keys[1] == (BP.textile_key("houndstooth"), T.RUNNER_FOLD_ROLE)
    blanket = np.asarray(got["parts"][0]["verts"])
    assert blanket[:, 0].min() < BED_C[0] - 0.8 and blanket[:, 0].max() > BED_C[0] + 0.8   # over both sides ...
    assert blanket[:, 2].min() == pytest.approx(0.5 - T.BLANKET_DROP_M, abs=0.02)        # ... down to its hem
    assert blanket[:, 1].min() < BED_C[1] - 1.0                                          # and over the foot
    throw = np.asarray(got["parts"][1]["verts"])
    assert throw[:, 0].min() > BED_C[0] and throw[:, 0].max() > BED_C[0] + 0.8          # at the right side
    assert throw[:, 2].min() == pytest.approx(0.5 - T.SIDE_THROW_DROP_M, abs=0.03)
    fringes = [p for p in got["parts"] if p["role"] == "fringe"]
    assert len(fringes) == 2 and all(p["key"] == BP.textile_key("houndstooth") for p in fringes)
    assert got["weave"]["fringe_strands"] == sum(p["strands"] for p in fringes)
    assert abs(got["weave"]["fringe_strands"] - 2 * T.SIDE_THROW_W_M / BP.FRINGE_PITCH_M) <= 4
    zs = [v[2] for p in fringes for v in p["verts"]]
    assert min(zs) < 0.5 - T.SIDE_THROW_DROP_M                                          # under its hem
    assert not got["weave"]["blanket_look"]["lumpy"] and not got["weave"]["blanket_look"]["wavy_hem"]
    plan = R.plan_throw(item, {"id": "bed", "type": "bed_double", "footprint": dict(HOST)}, caster, 0.0)
    assert "not_rested" not in plan and plan["weave"]["pattern"] == "houndstooth"
    # only the left side free (the decor stage's fringe_ends from bed_sides): the throw on the left
    left = T.throw_parts(caster, HOST, dict(item, weave=dict(w, fringe_ends=["left"])), 0.0)
    assert left["weave"]["throw_side"] == "left" and np.asarray(left["parts"][1]["verts"])[:, 0].max() < BED_C[0]
    # both sides blocked: the pair across the foot of before (the pattern below, the fringed runner over it)
    blocked = {s: {"free": s == "foot"} for s in BP.SIDES}
    foot = T.throw_parts(caster, HOST, dict(item, weave=dict(w, fringe_ends=[])), 0.0, sides=blocked)
    assert [(p["key"], p["role"]) for p in foot["parts"]][:2] == [(BP.textile_key("houndstooth"), "throw"),
                                                                  (BP.runner_key("knit"), T.RUNNER_FOLD_ROLE)]
    assert "layout" not in foot["weave"]
    right = T.throw_parts(caster, HOST, dict(item, weave=dict(w, fringe_ends=["right"])), 0.0,
                          sides={"left": {"free": False}, "right": {"free": True}, "foot": {"free": True}})
    assert right["weave"]["fringe_ends"] == ["right"] and right["weave"]["throw_side"] == "right"
    # a throw in one layer carries both the pattern and the fringe
    one = T.throw_parts(caster, HOST, dict(item, layers=1), 0.0)
    assert [p["role"] for p in one["parts"]] == ["throw", "fringe", "fringe"]
    assert one["parts"][1]["key"] == BP.textile_key("houndstooth")
    # without a weave the Milestone 12 / UL106 throw is unchanged
    plain = T.throw_parts(caster, HOST, {k: v for k, v in item.items() if k != "weave"}, 0.0)
    assert [p["key"] for p in plain["parts"]] == ["colour_fabric", T.RUNNER_KEY] and "weave" not in plain


def test_the_build_gives_a_pattern_its_ink_and_the_runner_its_accent_colour():
    from wenart.blender import furniture as F

    item = {"colour": "off white", "accent_colour": "charcoal", "rotation_deg": 90.0}
    host = {"footprint": {"rotation_deg": 270.0}}
    assert F.part_colour(item, BP.runner_key("knit")) == "charcoal"
    assert F.part_colour(item, BP.textile_key("houndstooth")) == "off white"
    assert F.part_params(item, BP.textile_key("houndstooth"), host) == {"ink": "charcoal", "angle_deg": 90.0}
    assert F.part_params(item, BP.runner_key("knit"), host) is None
    assert F.part_params({"colour": "beige"}, BP.textile_key("stripe"))["ink"] == F.PATTERN_INK
    keys, _a = F.style_material_keys({"floor": {"material": "wood_oak_light"}})
    assert keys["textile_boucle"][0] == "fabric_boucle" and keys["runner_knit"][0] == "fabric_knit"
    assert keys["textile_houndstooth"][0] == "fabric_houndstooth"
    assert keys["textile_linen"][:2] == ("fabric_linen", "rough_linen")              # linen keeps its scan
    verts, faces, fkeys = F.dressing_mesh([{"verts": [(0, 0, 0)] * 3, "faces": [[0, 1, 2]], "key": "a"},
                                           {"verts": [(0, 0, 0)] * 3, "faces": [[0, 1, 2]], "key": "b",
                                            "colour": "sage"}])
    assert fkeys == ["a", "b|sage"] and F.split_key("b|sage") == ("b", "sage") and F.split_key("a") == ("a", None)
    assert faces == [[0, 1, 2], [3, 4, 5]]


# --------------------------------------------------------------------------
# the fabric looks: weave normals and sheen per fabric (PBR)
# --------------------------------------------------------------------------

def test_every_fabric_look_is_a_vocabulary_slug_with_its_sheen():
    from wenart.blender import materials as MAT
    from wenart.style import vocabulary as V

    for look, slug in list(BP.LOOK_SLUGS.items()) + list(BP.PATTERN_SLUGS.items()):
        e = V.FURNITURE_MATERIALS[slug]
        assert e["kind"] == "fabric" and MAT.colourable(slug), slug
        if slug != "fabric_linen":
            assert MAT.procedural_for(slug, False, True) == "wenart_weave", slug
            layers = MAT.material_kind_layers(slug)
            assert 0.0 < layers["sheen"]["weight"] <= 1.0, slug
    assert MAT.material_kind_layers("fabric_velvet")["sheen"]["weight"] > \
        MAT.material_kind_layers("fabric_cotton")["sheen"]["weight"]                  # velvet's pile shines
    assert MAT.material_kind_layers("fabric_linen") == {"sheen": {"weight": 0.5, "roughness": 0.5}}
    assert MAT.procedural_group_name("wenart_weave", {"weave": "boucle", "pattern": "plain"}) == \
        "wenart_weave_boucle_plain"
    assert MAT.procedural_group_name("wenart_weave", {"weave": "nope", "pattern": "nope"}) == \
        "wenart_weave_cotton_plain"
    note = MAT.procedural_note_for("wenart_weave", "fabric_houndstooth",
                                   MAT.procedural_params("fabric_houndstooth", {"ink": "charcoal"}))
    assert "houndstooth" in note and "charcoal" in note


class _Sock:
    def __init__(self, node, key, is_output):
        self.node, self.key, self.identifier, self.is_output, self.default_value = node, key, key, is_output, 0.0


_MIX_IDS = ("Factor_Float", "A_Color", "B_Color", "Result_Color", "A_Vector", "B_Vector", "Result_Vector",
            "A_Float", "B_Float", "Result_Float")


class _Socks(dict):
    def __init__(self, node, is_output):
        super().__init__()
        self.node, self.out = node, is_output

    def __missing__(self, key):
        self[key] = _Sock(self.node, key, self.out)
        return self[key]

    def __iter__(self):
        return iter([self[k] for k in _MIX_IDS])


class _Node:
    def __init__(self, kind):
        self.bl_idname, self.operation, self.node_tree = kind, None, None
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
    if k == "ShaderNodeMath":
        a, b, c = (float(inp(i)) for i in (0, 1, 2))
        return {"ADD": lambda: a + b, "SUBTRACT": lambda: a - b, "MULTIPLY": lambda: a * b,
                "DIVIDE": lambda: a / b if b else 0.0, "FLOOR": lambda: math.floor(a),
                "FRACT": lambda: a - math.floor(a), "FLOORED_MODULO": lambda: a - b * math.floor(a / b) if b else 0.0,
                "LESS_THAN": lambda: 1.0 if a < b else 0.0, "MINIMUM": lambda: min(a, b),
                "MAXIMUM": lambda: max(a, b), "MULTIPLY_ADD": lambda: a * b + c, "ABSOLUTE": lambda: abs(a),
                "SINE": lambda: math.sin(a)}[node.operation]()
    raise KeyError(k)


@pytest.mark.parametrize("pattern", ["houndstooth", "stripe", "herringbone"])
def test_the_weave_groups_pattern_is_the_pure_patterns_arithmetic(pattern, monkeypatch):
    from wenart.blender import materials as MAT

    groups = {}
    bpy = types.SimpleNamespace(data=types.SimpleNamespace(node_groups=types.SimpleNamespace(
        get=lambda name: groups.get(name), new=lambda name, kind: groups.setdefault(name, _Tree(name)))))
    monkeypatch.setitem(sys.modules, "bpy", bpy)
    tree = MAT.weave_group("wool", pattern)
    gout = next(n for n in tree.all if n.bl_idname == "NodeGroupOutput")
    rep, ang = BP.PATTERN_REPEAT_M[pattern], math.radians(30.0)
    inputs = {"Repeat": rep, "Cos": math.cos(ang), "Sin": math.sin(ang), "Thread": 0.004, "Roughness": 0.9,
              "Color": (1, 1, 1, 1), "Ink": (0, 0, 0, 1)}
    rng = np.random.default_rng(5)
    ink = 0
    for x, y in rng.uniform(-0.4, 0.4, size=(300, 2)):
        xr, yr = x * math.cos(ang) + y * math.sin(ang), y * math.cos(ang) - x * math.sin(ang)
        got = _eval(tree, gout.inputs["Share"], (x, y), inputs)
        assert got == pytest.approx(BP.pattern_share(pattern, xr, yr, rep)), (x, y)
        ink += got
    assert 0.2 < ink / 300 < 0.65                                                     # a real two-colour weave
    assert any(n.bl_idname == "ShaderNodeBump" for n in tree.all)                     # the weave's normal detail


# --------------------------------------------------------------------------
# a made-up library bed's own bedding, measured
# --------------------------------------------------------------------------

def _top_grid(head_bump: float, wrinkle: float, n: int = 40):
    xs, ys = np.meshgrid(np.linspace(-0.75, 0.75, n), np.linspace(-0.95, 0.95, n), indexing="ij")
    z = 0.5 + wrinkle * np.sin(xs * 23.0) * np.sin(ys * 17.0)
    z = z + np.where(ys > 0.55, head_bump, 0.0)
    return np.stack([xs + BED_C[0], ys + BED_C[1], z], axis=-1).reshape(-1, 3)


def test_a_made_up_bed_is_dressed_when_its_bedding_is_flat_or_poorer_than_ours():
    asset = {"has_bedding": True, "has_pillows": True}
    flat_box = np.asarray(geom2d.box((BED_C[0], BED_C[1], 0.25), (1.6, 2.0, 0.5))[0])
    rel = BP.bedding_relief(flat_box, BED_C, 0.0, (1.6, 2.0))
    mode, why = BP.dress_mode(asset, rel)
    assert mode == "full" and "flat" in why
    made = BP.bedding_relief(_top_grid(0.35, 0.012), BED_C, 0.0, (1.6, 2.0))
    assert made["pillow_bump_m"] > BP.BUMP_MIN_M and made["relief_m"] > BP.RELIEF_MIN_M
    assert BP.dress_mode(asset, made)[0] is None                                      # made up as well as ours
    # 30 Oct 2026 (UL137, then UL195: at most five pieces on a bed): its own pillows lying flat (a 15 cm bump) are its
    # set; no pillows of ours on top of them
    flat = BP.bedding_relief(_top_grid(0.15, 0.012), BED_C, 0.0, (1.6, 2.0))
    mode, why = BP.dress_mode(asset, flat, width=1.6)
    assert mode is None and "lie flat" in why and "UL195" in why
    assert BP.dress_mode(asset, flat, width=0.9)[0] is None                           # a single bed takes no shams
    no_pillows = BP.bedding_relief(_top_grid(0.0, 0.012), BED_C, 0.0, (1.6, 2.0))
    assert BP.dress_mode(asset, no_pillows)[0] == "pillows"                            # our pillow set, its duvet kept
    assert BP.dress_mode({"has_bedding": True, "has_pillows": False}, {})[0] == "pillows"
    assert BP.dress_mode(asset, {})[0] is None
    # the pillows-only set leaves the duvet out
    spec = BP.family_spec("modern")[0]
    plan = T.bedding_set(bed_caster(), HOST, 0.0, spec, None, mode="pillows")
    assert "duvet" not in roles(plan) and roles(plan)["pillow"] == 2 and plan["record"]["mode"] == "pillows"


# --------------------------------------------------------------------------
# R36: the drum nightstand's decor set
# --------------------------------------------------------------------------

def _counter():
    n = [0]

    def new_id(level):
        n[0] += 1
        return f"dec_{level}_{900 + n[0]}"
    return new_id


def test_a_drum_nightstand_gets_the_photos_decor_set_on_its_round_top():
    stand = M.fp("f_L0_003", "nightstand", (3.6, 3.7), (0.45, 0.45), form="drum", height=0.55)
    b = room(bed_piece(), stand)
    notes = BG.nightstand_sets(b, {"family": "modern"}, _counter())
    (it,) = [d for d in b["decor"] if d.get("set") == "bedside"]
    assert it["type"] == "vase" and it["host_id"] == "f_L0_003" and it["stems"] == "palm"
    assert it["source"] == "added_by_ai"
    r = 0.45 / 2.0 - BG.NIGHTSTAND_MARGIN_M
    d = math.hypot(it["center"][0] - 3.6, it["center"][1] - 3.7)
    assert d + math.hypot(*it["size"][:2]) / 2.0 <= r + 1e-6                          # inside the round top
    assert BP.BEDSIDE_SET_MIN_H_M <= it["size"][2] <= BP.BEDSIDE_SET_H_M and notes
    assert b["bedding"]["nightstand_sets"] == [it["id"]]
    from wenart.furniture import fit as FIT

    assert FIT.fit_decor_item(it, {"entries": []}) is None                           # ours, never a library vase
    # under a bedside pendant hung 0.55 m over its top
    b2 = room(bed_piece(), copy.deepcopy(stand))
    b2["decor"].append({"id": "dec_L0_1", "type": "pendant_light", "anchor_ids": ["f_L0_003"], "room_id": M.ROOM_ID,
                        "level_id": "L0", "center": [3.6, 3.7, 0.55 + 0.55], "size": [0.18, 0.18, 1.0]})
    BG.nightstand_sets(b2, {"family": "modern"}, _counter())
    (it2,) = [d for d in b2["decor"] if d.get("set") == "bedside"]
    assert it2["size"][2] <= 0.55 - BG.PENDANT_CLEAR_M + 1e-6
    # a table lamp taking the round top: no room, said why
    b3 = room(bed_piece(), copy.deepcopy(stand))
    b3["decor"].append({"id": "dec_L0_2", "type": "table_lamp", "host_id": "f_L0_003", "room_id": M.ROOM_ID,
                        "level_id": "L0", "center": [3.6, 3.7], "size": [0.3, 0.3, 0.45], "rotation_deg": 0.0})
    notes3 = BG.nightstand_sets(b3, {"family": "modern"}, _counter())
    assert not [d for d in b3["decor"] if d.get("set") == "bedside"] and "full" in notes3[0]
    # a standing nightstand gets none (only the round drum of R17 has the set)
    b4 = room(bed_piece(), M.fp("f_L0_003", "nightstand", (3.6, 3.7), (0.45, 0.45)))
    BG.nightstand_sets(b4, {"family": "modern"}, _counter())
    assert not [d for d in b4["decor"] if d.get("set") == "bedside"]


def test_the_decor_set_is_one_mesh_of_vases_a_palm_leaf_and_a_box_inside_its_box():
    from wenart.blender import parametric as P

    parts = P.decor_parts("vase", 0.30, 0.18, 0.55, {"set": "bedside", "stems": "palm"})
    assert Counter(p["role"] for p in parts) == {"vase": 2, "box": 1, "lid": 1, "stem": 1, "leaf": 1}
    assert {p["key"] for p in parts} == set(BP.BEDSIDE_SET_KEYS)
    v = np.asarray([q for p in parts for q in p["verts"]])
    assert v[:, 0].min() >= -0.15 - 1e-6 and v[:, 0].max() <= 0.15 + 1e-6
    assert v[:, 1].min() >= -0.09 - 1e-6 and v[:, 1].max() <= 0.09 + 1e-6
    assert v[:, 2].min() >= -1e-9 and v[:, 2].max() <= 0.55 + 1e-6
    vases = [np.asarray(p["verts"]) for p in parts if p["role"] == "vase"]
    for vv in vases:                                                                   # faceted: not round
        r = np.hypot(vv[:, 0] - vv[:, 0].mean(), vv[:, 1] - vv[:, 1].mean())
        assert len(np.unique(np.round(r, 4))) > 2


# --------------------------------------------------------------------------
# the decor stage's plan
# --------------------------------------------------------------------------

def test_the_decor_stage_plans_each_beds_set_its_sides_and_its_throws_weave():
    throw = {"id": "dec_L0_5", "type": "throw", "host_id": "f_L0_001", "room_id": M.ROOM_ID, "level_id": "L0",
             "center": [2.5, 2.3], "size": [1.52, 0.5, 0.05], "rotation_deg": 0.0, "layers": 2,
             "accent_colour": "charcoal"}
    made_up = bed_piece(center=(1.0, 1.5), pid="f_L0_009", asset={"has_bedding": True, "has_pillows": True})
    b = room(bed_piece(), made_up)
    b["decor"].append(throw)
    BG.dress_beds(b, {"family": "scandinavian"}, _counter())
    bed = b["furniture"][0]
    bl = bed["bedding_layers"]
    assert bl["family"] == "scandinavian" and bl["set"]["duvet"]["look"] == "linen" and bl["bedding_rule"] == BP.RULE
    assert bl["expected"] == BP.counts(bl["set"], 1.6) and set(bl["sides"]) == set(BP.SIDES) and bl["bedding_why"]
    assert throw["weave"]["pattern"] == "stripe" and throw["weave"]["fringe"]
    # the made-up model gets a throw too, built only when the build dresses it
    (t2,) = [d for d in b["decor"] if d.get("host_id") == "f_L0_009" and d["type"] == "throw"]
    assert t2["when_dressed"] is True and t2["layers"] == 2 and t2["weave"]["pattern"] == "stripe"
    assert b["bedding"]["beds"]["f_L0_001"]["expected"]["accent"] == 0                 # UL163: shams, no accent row
    from wenart.blender import furniture as F

    spec, why = F.bed_bedding_spec(bed, {"family": "modern"})
    assert spec["family"] == "scandinavian" and why                                  # the decor stage's set wins
    spec2, why2 = F.bed_bedding_spec(bed_piece(), {"family": "classic"})
    assert spec2["family"] == "classic" and "build time" in why2


# --------------------------------------------------------------------------
# the checks: M30 (model review) and U34 (Argus), kind taste
# --------------------------------------------------------------------------

def _built_and_manifest(set_counts=None, sides=None, drops=None, weave=None, throw=True, dressed=True):
    spec = BP.family_spec("modern")[0]
    b = room(bed_piece())
    b["dressing"] = {"family": "modern"}
    full = BP.counts(spec, 1.6)
    rec = {"set": dict(full, **(set_counts or {})), "explained": {}, "mode": "full",
           "sides": sides or {s: {"free": True} for s in BP.SIDES},
           "drops": drops or {s: {"drop_m": 0.44, "hem_over_floor_m": 0.06} for s in BP.SIDES}}
    entry = {"kind": "furniture", "wenart_id": "f_L0_001", "type": "bed_double"}
    if dressed:
        entry["dressing"] = {"record": rec}
    objects = [entry]
    if throw:
        objects.append({"kind": "decor", "type": "throw", "host_id": "f_L0_001",
                        "weave": weave if weave is not None else {"pattern": "houndstooth", "fringe": True,
                                                                  "fringe_strands": 38}})
    return b, {"objects": objects, "style_profile": {"family": "modern"}}


def _problems(built, manifest):
    got, n = BP.review(built, manifest, check="U34")
    assert n == 1
    return sorted(g["problem"] for g in got)


def test_the_review_flags_a_bed_that_misses_its_familys_set():
    assert _problems(*_built_and_manifest()) == []                                      # the full set as built
    assert _problems(*_built_and_manifest(set_counts={"accent": 0, "lumbar": 0})) == ["too_few_pillows"]
    # 30 Oct 2026 (UL163): without shams the decorative pair stands in front of the pillows, no lumbar
    b, m = _built_and_manifest(set_counts={"euro_shams": 0, "accent": 2, "lumbar": 0})
    m["objects"][0]["dressing"]["record"]["explained"] = {"euro_shams": "no headboard"}
    assert _problems(b, m) == []                                                        # explained: no headboard
    assert _problems(*_built_and_manifest(drops={"left": {"drop_m": 0.1, "hem_over_floor_m": 0.4},
                                                 "right": {"drop_m": 0.44, "hem_over_floor_m": 0.06},
                                                 "foot": {"drop_m": 0.44, "hem_over_floor_m": 0.06}})) == \
        ["no_overhang"]
    blocked = {"left": {"free": False}, "right": {"free": True}, "foot": {"free": True}}
    assert _problems(*_built_and_manifest(sides=blocked, drops={"left": {"drop_m": 0.0, "hem_over_floor_m": 0.5},
                                                                "right": {"drop_m": 0.44, "hem_over_floor_m": 0.06},
                                                                "foot": {"drop_m": 0.44,
                                                                         "hem_over_floor_m": 0.06}})) == []
    assert _problems(*_built_and_manifest(weave={})) == ["throw_fringe", "throw_pattern"]
    assert _problems(*_built_and_manifest(weave={"pattern": "houndstooth", "fringe": True})) == ["throw_fringe"]
    assert _problems(*_built_and_manifest(weave={"pattern": "houndstooth", "fringe": True, "fringe_ends": [],
                                                 "fringe_strands": 0})) == []      # both sides blocked: explained
    assert _problems(*_built_and_manifest(throw=False)) == ["no_throw"]
    b, m = _built_and_manifest()
    m["objects"][0]["dressing"]["record"] = {"pillows": 2, "euro_shams": 0}            # a dressing from before UL121
    assert _problems(b, m) == ["too_few_pillows"]
    # a made-up model measured poorer than ours and left as it was
    b, m = _built_and_manifest(dressed=False, throw=False)
    m["objects"][0]["bedding_test"] = {"own_bedding": True, "poorer": True, "reason": "its cover is flat"}
    assert _problems(b, m) == ["flat_bedding"]
    # a made-up model kept (made up as well as ours) has no throw by design
    m["objects"][0]["bedding_test"] = {"own_bedding": True, "poorer": False}
    assert _problems(b, m) == []
    # without a manifest: the plan
    b = room(bed_piece())
    b["dressing"] = {"family": "modern"}
    assert [g["problem"] for g in BP.review(b, None)[0]] == ["too_few_pillows"]
    BG.dress_beds(b, {"family": "modern"}, _counter())
    assert BP.review(b, None)[0] == []


def test_m30_and_u34_are_wired_as_the_other_checks():
    from wenart.agent import causes as CA
    from wenart.audit import kinds as K
    from wenart.audit import lessons as AL
    from wenart.blender import model_review as MR

    assert "M30" in MR.CHECKS and K.CHECK_KIND["M30"] == "taste" and K.CHECK_KIND["U34"] == "taste"
    assert CA.CHECK_CAUSE["M30"] == "decor_look" and AL.CHECK_LESSONS["U34"] == ("UL121", "UL136", "UL137", "UL146")
    b, m = _built_and_manifest(throw=False)
    rec = MR.review(b, m)
    assert rec["checks"]["M30"]["status"] == "ok" and rec["checks"]["M30"]["checked"] == 1
    (f,) = [f for f in rec["findings"] if f["check"] == "M30"]
    assert f["kind"] == "taste" and f["metrics"]["problem"] == "no_throw" and "bedding" in f["fix"]
    out = AL.audit(b, m)
    assert out["checked"]["U34"] == 1
    (u,) = [f for f in out["findings"] if f["check"] == "U34"]
    assert u["severity"] == "minor" and "decor" in u["fix"] and u["evidence"]["lesson"] == "UL121"
    assert AL.coverage()["UL121"]["code"] == ["U34"]


def test_lesson_ul121_is_built():
    rows = json.loads((ROOT / "wenart" / "blender" / "architect_lessons.json").read_text(encoding="utf-8"))
    (ul,) = [x for x in rows["lessons"] if x["id"] == "UL121"]
    assert ul["status"] == "built" and ul["checks"] == ["build"] and "bedding_parts" in ul["lesson"]


# --------------------------------------------------------------------------
# the build's cost (UL111): one mesh per bed from vertex arrays
# --------------------------------------------------------------------------

def test_the_bedding_is_a_few_parts_built_from_arrays():
    spec = BP.family_spec("modern")[0]
    plan = T.bedding_set(bed_caster(), HOST, 0.0, spec, None)
    assert len(plan["parts"]) <= 12                                                    # one part per pillow or cloth
    from wenart.blender import furniture as F

    verts, faces, keys = F.dressing_mesh(plan["parts"])
    assert len(set(keys)) <= 8 and len(verts) < 20000                                  # a few material slots


# --------------------------------------------------------------------------
# real06 (run 20261029-100801-full)
# --------------------------------------------------------------------------

@pytest.mark.skipif(not REAL06_BUILT.is_file(), reason="the real06 run 20261029-100801-full is not in this checkout")
def test_real06_beds_get_their_scandinavian_set_and_sides():
    b = json.loads(REAL06_BUILT.read_text(encoding="utf-8"))
    style = json.loads(REAL06_MANIFEST.read_text(encoding="utf-8"))["style_profile"]
    assert style["family"] == "scandinavian"
    bb = copy.deepcopy(b)
    BG.dress_beds(bb, style, _counter())
    beds = {p["id"]: p for p in bb["furniture"] if p["type"] in BP.BED_TYPES}
    sides = {pid: {s: v["free"] for s, v in p["bedding_layers"]["sides"].items()} for pid, p in beds.items()}
    print("\nreal06 beds (run 20261029-100801-full):")
    for pid, p in sorted(beds.items()):
        bl = p["bedding_layers"]
        print(f"  {pid} {p['type']} {p['room_id']}: expected {bl['expected']}, sides "
              + ", ".join(f"{s} {'free' if v['free'] else 'blocked by ' + str(v['by'])}"
                          for s, v in bl["sides"].items()))
    assert sides["f_L1_010"] == {"left": True, "right": True, "foot": True}
    assert sides["f_L1_013"]["left"] is False                                         # against its room's wall
    assert beds["f_L1_013"]["bedding_layers"]["expected"] == {"euro_shams": 0, "pillows": 1, "accent": 1, "lumbar": 0}
    throws = [d for d in bb["decor"] if d.get("type") == "throw" and d.get("host_id") in beds]
    assert throws and all(d["weave"]["pattern"] == "stripe" for d in throws)
    manifest = json.loads(REAL06_MANIFEST.read_text(encoding="utf-8"))
    got, n = BP.review(b, manifest)
    assert n == 4
    print("  U34 on the run as built: " + "; ".join(f"{g['target']} {g['problem']}" for g in got))
    assert {g["target"] for g in got if g["problem"] == "too_few_pillows"} == {"f_L1_010", "f_L1_013"}
    assert not [g for g in got if g["target"] in ("f_L1_004", "f_L1_007")]           # made up: kept, no throw by design


def test_a_storage_bed_with_a_bare_mattress_gets_the_full_set():
    """30 Oct 2026 (user on real04 run 20261029-201533-full: "this bed model needs fixing some sheets etc"): a storage
    bed whose mattress is a box of a few big faces over drawers was read as a folded duvet (its middle cells held only
    the drawers' vertices) and got our pillows only; a headboard alone is no pillow set."""
    asset = {"has_bedding": True, "has_pillows": True}
    mv, mf = geom2d.box((BED_C[0], BED_C[1], 0.40), (1.6, 2.0, 0.20))                  # top at 0.50 m, 6 faces
    tris = [[q[0], q[k], q[k + 1]] for q in mf for k in range(1, len(q) - 1)]
    mattress = np.concatenate([np.asarray(mv), BP.surface_samples(mv, tris)])     # as _evaluated_world_points
    xs, ys = np.meshgrid(np.linspace(-0.7, 0.7, 30), np.linspace(-0.9, 0.6, 30), indexing="ij")
    drawers = np.stack([xs + BED_C[0], ys + BED_C[1], 0.02 + 0.11 * ((xs * 7).astype(int) % 2)], axis=-1)
    headboard = np.asarray(geom2d.box((BED_C[0], BED_C[1] + 0.97, 0.6), (1.6, 0.06, 1.2))[0])
    verts = np.concatenate([mattress, drawers.reshape(-1, 3), headboard])
    rel = BP.bedding_relief(verts, BED_C, 0.0, (1.6, 2.0))
    assert rel["top_m"] == pytest.approx(0.50, abs=0.01) and rel["relief_m"] < BP.RELIEF_MIN_M
    mode, why = BP.dress_mode(asset, rel)
    assert mode == "full" and "flat" in why                                     # our duvet, sheet band and throw
    # without the samples the drawers under the mattress were read as a folded duvet
    drawers_only = BP.bedding_relief(np.concatenate([np.asarray(mv), drawers.reshape(-1, 3), headboard]), BED_C,
                                     0.0, (1.6, 2.0))
    assert drawers_only["top_m"] < 0.2
    # a made-up bed (standing pillows) keeps its own bedding; the same duvet with a headboard and no pillows gets ours
    made = BP.bedding_relief(np.concatenate([_top_grid(0.35, 0.012), headboard]), BED_C, 0.0, (1.6, 2.0))
    assert BP.dress_mode(asset, made)[0] is None
    bare = BP.bedding_relief(np.concatenate([_top_grid(0.0, 0.012), headboard]), BED_C, 0.0, (1.6, 2.0))
    assert bare["pillow_vertices"] < BP.PILLOW_VERTS_MIN and BP.dress_mode(asset, bare)[0] == "pillows"
