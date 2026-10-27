"""27 Oct 2026 (pod run 130756 on real06: the judge named "lollipop trees on a flat green plane" in 58 findings, nearly
every view): the horizon context's trees are instances of the photoscanned Poly Haven trees (``site.CONTEXT_SCANS``,
``context_scan_plan``, ``build_context_scans``), and the ground beyond the lawn by the house gets field-scale patches
(``vegetation.LAWN_FIELDS``). CPU checks with a fake bpy; the Blender side is in tests/gpu/test_site_window_views.py."""
from __future__ import annotations

import json
import math
import sys
import types
from pathlib import Path

import pytest

from wenart.blender import site as S
from wenart.blender import vegetation as VG

ROOT = Path(__file__).resolve().parents[1]
REAL06 = ROOT / "tests" / "fixtures" / "real06_site_trees_20261026.json"
MODELS = {"island_tree_02": {"height_m": 3.41, "width_m": 3.9}, "jacaranda_tree": {"height_m": 19.83, "width_m": 17.0},
          "fir_sapling_medium": {"height_m": 9.16, "width_m": 4.6}, "searsia_lucida": {"height_m": 2.34, "width_m": 2.6}}


def _ctx():
    d = json.loads(REAL06.read_text(encoding="utf-8"))
    terrain = dict(d["terrain"], warnings=[], assumed=[])
    return S.horizon_context(d["outline"], d["near_extent"], terrain, d["climate"], d["height_m"])


def test_a_context_tree_takes_its_species_scan_else_its_crown_shapes():
    """The species' own Poly Haven scan first (an olive's island_tree_02), else the scan of its crown shape (a stone
    pine's umbrella crown: the jacaranda; a cypress's column: the fir), else none (a palm: a blob crown)."""
    assert S.context_scan_asset("olive", "round", MODELS) == ("island_tree_02", False)
    assert S.context_scan_asset("plane", "spreading", MODELS) == ("jacaranda_tree", False)
    assert S.context_scan_asset("stone_pine", "umbrella", MODELS) == ("jacaranda_tree", True)
    assert S.context_scan_asset("cypress", "columnar", MODELS) == ("fir_sapling_medium", True)
    assert S.context_scan_asset("palm", "palm", MODELS) == (None, False)
    # the species' own scan is not on the volume: its shape's stand-in
    assert S.context_scan_asset("oak", "spreading", MODELS) == ("jacaranda_tree", True)
    assert S.context_scan_asset("olive", "round", {}) == (None, False)


def test_the_scan_plan_scales_every_tree_to_its_height_and_width():
    """real06's context (Mediterranean: stone pine, olive, cypress, plane): every tree is a scan instance, scaled to
    its height, its width within ``xy_ratio`` of the uniform scale, its base on its ground point less ``sink_m``,
    turned by its seed (the same plan twice); the stand-ins are named per species."""
    ctx = _ctx()
    plan = S.context_scan_plan(ctx, MODELS)
    assert not plan["blobs"] and len(plan["scans"]) == ctx["count"]
    assert sum(plan["assets"].values()) == ctx["count"]
    assert plan["stand_ins"] == {"stone_pine": "jacaranda_tree", "cypress": "fir_sapling_medium"}
    lo, hi = S.CONTEXT_SCANS["xy_ratio"]
    for s in plan["scans"]:
        t = ctx["trees"][s["tree"]]
        m = MODELS[s["asset"]]
        sx, sy, sz = s["scale"]
        assert sz * m["height_m"] == pytest.approx(t["height"], abs=1e-3)
        assert sx == sy and lo * sz - 1e-3 <= sx <= hi * sz + 1e-3
        assert s["position"][:2] == [float(t["center"][0]), float(t["center"][1])]
        assert s["position"][2] == pytest.approx(float(t["z"]) - S.CONTEXT_SCANS["sink_m"], abs=1e-3)
        assert 0.0 <= s["yaw"] <= 2 * math.pi
    # a cypress is narrow: its fir is squeezed to the lower bound or near it
    cyp = [s for s in plan["scans"] if ctx["trees"][s["tree"]]["species"] == "cypress"]
    assert cyp and all(s["scale"][0] < s["scale"][2] for s in cyp)
    assert S.context_scan_plan(ctx, MODELS) == plan


def test_the_scan_plan_uses_at_most_max_models_and_leaves_the_rest_blobs():
    """At most ``max_models`` scans (the most wanted first); a tree with no scan left is a blob crown."""
    ctx = _ctx()
    plan = S.context_scan_plan(ctx, MODELS, {"max_models": 1})
    assert len(plan["assets"]) == 1
    [only] = plan["assets"]
    assert plan["assets"][only] == len(plan["scans"]) and plan["blobs"]
    assert len(plan["scans"]) + len(plan["blobs"]) == ctx["count"]
    assert S.context_scan_plan(ctx, {}) == {"scans": [], "blobs": list(range(ctx["count"])), "assets": {},
                                            "stand_ins": {}}


def test_context_scans_switch(monkeypatch):
    monkeypatch.delenv(S.CONTEXT_SCANS_ENV, raising=False)
    assert S.context_scans_on() and not S.context_scans_on(False) and S.context_scans_on(True)
    monkeypatch.setenv(S.CONTEXT_SCANS_ENV, "off")
    assert not S.context_scans_on() and S.context_scans_on(True)


class _Ob(dict):
    def __init__(self, name, data=None):
        super().__init__()
        self.name, self.data, self.parent = name, data, None
        self.instance_type = self.instance_collection = None
        self.scale = self.rotation_euler = self.location = None
        for attr in ("visible_camera", "visible_diffuse", "visible_glossy", "visible_transmission",
                     "visible_volume_scatter", "visible_shadow"):
            setattr(self, attr, True)


class _Col:
    def __init__(self, name):
        self.name = name
        self.objects = types.SimpleNamespace(items=[], link=lambda ob: self.objects.items.append(ob))


@pytest.fixture()
def fake_scene(monkeypatch):
    objs: dict = {}
    removed: list = []

    def new(name, data):
        objs[name] = _Ob(name, data)
        return objs[name]

    def remove(ob, do_unlink=True):
        removed.append(ob.name)
        objs.pop(ob.name, None)
    scene_col = _Col("scene")
    bpy = types.SimpleNamespace(
        data=types.SimpleNamespace(objects=types.SimpleNamespace(new=new, remove=remove, get=objs.get),
                                   collections={"veg_lib": _Col("veg_lib")}),
        context=types.SimpleNamespace(scene=types.SimpleNamespace(collection=scene_col)))
    monkeypatch.setitem(sys.modules, "bpy", bpy)
    heroes = {a: {"id": a, "path": f"/x/{a}.gltf", "height_m": m["height_m"], "base_z": 0.0, "licence": "CC0",
                  "licence_url": VG.POLYHAVEN_LICENCE_URL, "name": a} for a, m in MODELS.items()}
    monkeypatch.setattr(VG, "scan_model", lambda a, *x, **k: heroes.get(a))
    imported = []

    def scan_library(hero):
        imported.append(hero["id"])
        m = MODELS[hero["id"]]
        return {"collection": "veg_lib", "height_m": m["height_m"], "width_m": m["width_m"], "base_z": -0.1,
                "count": 0}
    monkeypatch.setattr(VG, "scan_library", scan_library)
    return types.SimpleNamespace(bpy=bpy, objs=objs, removed=removed, imported=imported, col=_Col("site"))


def test_build_context_makes_scan_instances_with_one_manifest_entry_per_scan(fake_scene):
    """``build_context``: the trees with a scan are collection instances of it (children of ``context_scan_<id>``,
    scaled, their base on the ground, hidden from diffuse and volume rays, casting shadows), one manifest entry per
    scan (``veg_method`` polyhaven, the asset, CC0, the species it stands in for); no blob mesh when every tree is a
    scan."""
    ctx = _ctx()
    entries = []
    rec = S.build_context(ctx, fake_scene.col, lambda *a: entries.append(a), scans=True)
    assert rec["built"] and rec["faces"] == 0 and rec["blob_trees"] == 0
    sc = rec["scans"]
    assert sc["built"] and sc["instances"] == ctx["count"] and sorted(sc["assets"]) == sorted(fake_scene.imported)
    assert sc["hidden_rays"] == ["visible_diffuse", "visible_volume_scatter"]
    inst = [o for o in fake_scene.col.objects.items if o.instance_type == "COLLECTION"]
    assert len(inst) == ctx["count"]
    for k, o in enumerate(inst):                      # every tree a scan: in the trees' order
        t = ctx["trees"][k]
        assert o.instance_collection.name == "veg_lib" and o.parent is not None
        assert o.parent.name == "context_scan_" + o.name.split("context_scan_")[1].rsplit("_", 1)[0]
        assert not o.visible_diffuse and not o.visible_volume_scatter
        assert o.visible_shadow and o.visible_camera and o.visible_transmission and o.visible_glossy
        assert o.location[:2] == (float(t["center"][0]), float(t["center"][1]))
        assert o.location[2] == pytest.approx(float(t["z"]) - S.CONTEXT_SCANS["sink_m"] + 0.1 * o.scale[2], abs=1e-3)
    assert len(entries) == len(sc["assets"])
    for name, wid, kind, mat, status, extra in entries:
        assert name.startswith("context_scan_") and kind == "site_decor" and status == "assumed"
        assert extra["veg_method"] == "polyhaven" and extra["asset"] in MODELS and extra["licence"] == "CC0"
        assert extra["site_part"] == "context" and extra["context_trees"] == sc["assets"][extra["asset"]]
        assert "Poly Haven scan" in extra["assumed"]["reason"]
    jac = next(e for e in entries if e[5]["asset"] == "jacaranda_tree")[5]
    assert jac["stand_in_for"] == ["stone_pine"] and "inferred look" in jac["assumed"]["reason"]


def test_build_context_keeps_blob_crowns_for_the_trees_without_a_scan(fake_scene, monkeypatch):
    """A tree without a scan stays in the ``context_trees`` blob mesh (its entry counts only those); scans off (or
    no scan on the volume) keeps every tree a blob."""
    from wenart.blender import common

    made = {}

    def new_mesh_object(name, verts, faces, *, collection, wenart_id, kind, status, materials=(),
                        face_material_indices=None):
        made.update(name=name, faces=len(faces))
        ob = _Ob(name, types.SimpleNamespace(shade_smooth=lambda: None))
        made["ob"] = ob
        return ob
    monkeypatch.setattr(common, "new_mesh_object", new_mesh_object)
    monkeypatch.setattr(VG, "context_material", lambda s: types.SimpleNamespace(name=f"veg_context_{s}",
                                                                                get=lambda k, d=None: ""))
    monkeypatch.setattr(VG, "bark_material", lambda: types.SimpleNamespace(name="veg_bark", get=lambda k, d=None: ""))
    ctx = _ctx()
    entries = []
    rec = S.build_context(ctx, fake_scene.col, lambda *a: entries.append(a), scans=True)
    n_cypress = sum(1 for t in ctx["trees"] if t["species"] == "cypress")
    monkeypatch.setitem(S.CONTEXT_SCANS["standin"], "columnar", None)       # no stand-in for a column
    entries.clear()
    rec = S.build_context(ctx, fake_scene.col, lambda *a: entries.append(a), scans=True)
    assert rec["built"] and rec["blob_trees"] == n_cypress and rec["scans"]["instances"] == ctx["count"] - n_cypress
    blob = [e for e in entries if e[0] == S.CONTEXT_NAME]
    assert len(blob) == 1 and blob[0][5]["context_trees"] == n_cypress and blob[0][5]["veg_method"] == "context"
    entries.clear()
    rec = S.build_context(ctx, fake_scene.col, lambda *a: entries.append(a), scans=False)
    assert "scans" not in rec and rec["blob_trees"] == ctx["count"] and len(entries) == 1


def test_a_failed_scan_build_removes_its_objects_and_leaves_blobs(fake_scene, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("no instance")
    monkeypatch.setattr(VG, "context_instance", boom)
    ctx = _ctx()
    rec = S.build_context_scans(ctx, fake_scene.col, lambda *a: None)
    assert not rec["built"] and rec["error"] == "RuntimeError: no instance"
    assert rec["blobs"] == list(range(ctx["count"])) and fake_scene.removed
    assert not [n for n in fake_scene.objs if n.startswith("context_scan_")]


def test_no_scan_on_the_volume_leaves_blobs(monkeypatch):
    monkeypatch.setattr(VG, "scan_model", lambda a, *x, **k: None)
    ctx = _ctx()
    rec = S.build_context_scans(ctx, None, lambda *a: None)
    assert not rec["built"] and "no Poly Haven scan" in rec["reason"] and rec["blobs"] == list(range(ctx["count"]))


def test_a_scan_entry_is_credited_as_its_poly_haven_model(tmp_path):
    from wenart.run import copy as C

    (tmp_path / "scene").mkdir()
    (tmp_path / "scene" / "scene_manifest.json").write_text(json.dumps({"objects": [
        {"name": "context_scan_jacaranda_tree", "wenart_id": "context_scan_jacaranda_tree", "veg_method": "polyhaven",
         "asset": "jacaranda_tree", "site_part": "context"}]}), encoding="utf-8")
    [row] = C.vegetation_credits(tmp_path)
    assert row["asset_id"] == "jacaranda_tree" and row["licence"] == "CC0" and row["kind"] == "model"


# --- the field-scale patches of the ground -------------------------------------------------------------------------

class _Sock:
    def __init__(self, node, key):
        self.node, self.key, self.default_value, self.links = node, key, (0.0, 0.0, 0.0, 1.0), []


class _Socks:
    def __init__(self, node):
        self.node, self.d = node, {}

    def __getitem__(self, key):
        if key not in self.d:
            self.d[key] = _Sock(self.node, key)
        return self.d[key]


class _Link:
    def __init__(self, a, b):
        self.from_socket, self.to_socket = a, b


class _Links(list):
    def new(self, a, b):
        self.append(_Link(a, b))
        b.links = [self[-1]]
        return self[-1]

    def remove(self, link):
        list.remove(self, link)
        link.to_socket.links = []


class _Node:
    def __init__(self, idname):
        self.bl_idname, self.operation = idname, None
        self.inputs, self.outputs = _Socks(self), _Socks(self)
        self.color_ramp = types.SimpleNamespace(elements=[types.SimpleNamespace(color=None, position=0.0),
                                                          types.SimpleNamespace(color=None, position=1.0)])


class _Nodes(list):
    def new(self, idname):
        self.append(_Node(idname))
        return self[-1]


class _Mat(dict):
    def __init__(self):
        super().__init__()
        self.name = "garden"
        self.node_tree = types.SimpleNamespace(nodes=_Nodes(), links=_Links())


def _edges(tree):
    return [(ln.from_socket.node.bl_idname, ln.from_socket.node.operation, ln.from_socket.key,
             ln.to_socket.node.bl_idname, ln.to_socket.node.operation, ln.to_socket.key) for ln in tree.links]


def test_the_ground_beyond_the_lawn_gets_field_patches_in_the_climates_tint():
    """``lawn_material(mat, fields_centre, climate)``: a field-scale noise (``LAWN_FIELDS["scale_per_m"]``) through a
    ramp from no tint to the climate's tint, faded in from ``near_m`` to ``far_m`` from the building's centre (a
    Map Range of the distance), multiplied after the lawn's own variation; the bounce greying and the Base Color
    follow it. Without a centre: no patches (the lawn of before)."""
    mat = _Mat()
    tree = mat.node_tree
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    rec = VG.lawn_material(mat, fields_centre=(12.0, 5.0), climate="mediterranean")
    f = rec["fields"]
    assert f["centre"] == [12.0, 5.0] and f["climate"] == "mediterranean" and f["patch_m"] > 50
    assert f["tint"] == list(VG.LAWN_FIELDS["tint"]["mediterranean"])
    edges = _edges(tree)
    assert ("ShaderNodeVectorMath", "SUBTRACT", "Vector", "ShaderNodeVectorMath", "LENGTH", 0) in edges
    assert ("ShaderNodeVectorMath", "LENGTH", "Value", "ShaderNodeMapRange", None, "Value") in edges
    assert ("ShaderNodeMapRange", None, "Result", "ShaderNodeMix", None, "Factor") in edges
    ramps = [n for n in tree.nodes if n.bl_idname == "ShaderNodeValToRGB"]
    framp = next(r for r in ramps if r.color_ramp.elements[1].color[:3] == VG.LAWN_FIELDS["tint"]["mediterranean"])
    assert framp.color_ramp.elements[0].color == (1.0, 1.0, 1.0, 1.0)
    assert framp.color_ramp.elements[0].position < framp.color_ramp.elements[1].position
    fade = next(n for n in tree.nodes if n.bl_idname == "ShaderNodeMapRange")
    assert fade.inputs["From Min"].default_value == VG.LAWN_FIELDS["near_m"] < fade.inputs["From Max"].default_value
    sub = next(n for n in tree.nodes if n.operation == "SUBTRACT")
    assert sub.inputs[1].default_value == (12.0, 5.0, 0.0)
    fmix = next(ln.to_socket.node for ln in tree.links if ln.from_socket.node is fade)
    assert ("ShaderNodeMix", None, 2, "ShaderNodeRGBToBW", None, "Color") in edges
    assert [ln for ln in tree.links if ln.from_socket.node is fmix and ln.to_socket.node.bl_idname == "ShaderNodeRGBToBW"]
    assert bsdf.inputs["Base Color"].links
    plain = _Mat()
    plain.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    assert VG.lawn_material(plain)["fields"] is None
    assert not [n for n in plain.node_tree.nodes if n.bl_idname == "ShaderNodeMapRange"]
    other = _Mat()
    other.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    assert VG.lawn_material(other, fields_centre=(0, 0), climate="arctic")["fields"]["climate"] == "temperate"
