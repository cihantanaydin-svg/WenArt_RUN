"""Milestone 13 track T6 GPU tests (docs/milestone13.md §13.1, pod P1; ``pytest -m gpu tests/gpu/test_m13_site.py``;
skipped without a Blender binary): the vegetation and site objects built in Blender 5.2 with the expected object and
material counts, and the committed real04 building built and rendered with its site.

- ``test_hedge_tree_sources_and_pool_in_blender``: one script inside Blender (``cli.run_blender``) builds a hedge
  (``vegetation.hedge_object``: one mesh with a geometry-nodes modifier scattering leaf cards; the leaf material with
  ``Thin Wall``), one tree per source (``cards`` always; ``sapling`` when the add-on is installed on the pod, through
  ``bpy.ops.curve.tree_add``: a curve object with a leaves mesh; ``polyhaven`` when the assets hold a Poly Haven tree:
  a collection instance of one imported glTF), a palm, a grass patch and a pool through ``site.build_site`` (basin,
  water with a Volume Absorption link, coping). Every expected object and material is counted; instances come from
  the evaluated depsgraph.
- ``test_real04_site_builds_and_the_site_view_sees_the_sky``: the committed real04 building built by the real build
  script (no textures): 4 hedges, 5 platforms with their parts, 4 pools with coping, the backdrop and the haze, every
  tree through the vegetation module (no ellipsoid proxy), the exterior cameras ext_1-5 and ext_7 (ext_3 / ext_4 were
  dropped in Milestone 12 behind the hedge "trees"); the site view rendered at 320 x 180: the top rows are sky, not
  black (the Milestone 12 band), and the VRAM is recorded.
"""
from __future__ import annotations

import json
import os
import textwrap
from pathlib import Path

import pytest

from wenart.blender import cli
from wenart.blender import vegetation as VG

pytestmark = pytest.mark.gpu

ROOT = Path(__file__).resolve().parents[2]
REAL04 = ROOT / "results" / "furniture" / "real04" / "building_final.json"
BLENDER = cli.find_blender()
if BLENDER is None:
    # Skipped at module level (the repo's convention for a GPU file with a CPU twin of the same basename, e.g.
    # tests/gpu/test_m13_modules.py): the module never enters sys.modules, so tests/test_m13_site.py collects too.
    pytest.skip("no Blender binary (WENART_BLENDER, /workspace/tools/blender, /opt/wenart/blender, PATH)",
                allow_module_level=True)
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary")

VEG_SCRIPT = textwrap.dedent("""
    import bpy, json, sys
    sys.path.insert(0, sys.argv[sys.argv.index("--") + 2])
    out = sys.argv[sys.argv.index("--") + 1]
    from wenart.blender import site as S
    from wenart.blender import vegetation as VG
    res = {"sapling": VG.ensure_sapling(), "assets_dir": str(VG.assets_dir())}
    col = bpy.data.collections.new("site"); bpy.context.scene.collection.children.link(col)
    def instances_of(ob):
        dg = bpy.context.evaluated_depsgraph_get()
        return sum(1 for i in dg.object_instances if i.is_instance and i.parent and i.parent.original == ob)
    terrain = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}
    hedge = {"id": "h1", "polyline": [[0, 0], [8, 0]], "width_m": 0.7, "height_m": 1.2, "species": "cherry_laurel"}
    v, f, info = S.hedge_parts(hedge, terrain)
    hob, hrec = VG.hedge_object(dict(hedge, core_verts=v, core_faces=f), collection=col, name="hedge_h1")
    leaf = bpy.data.materials.get(hrec["material"])
    bsdf = next((n for n in leaf.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    res["hedge"] = {"rec": hrec, "modifiers": [m.type for m in hob.modifiers], "instances": instances_of(hob),
                    "thin_wall": bool(bsdf and bsdf.inputs["Thin Wall"].default_value),
                    "alpha_linked": bool(bsdf and bsdf.inputs["Alpha"].is_linked)}
    levers = {"instances": True, "sapling": True}
    trees = {}
    cob, crec = VG.tree_object("stone_pine", 8.0, 1, False, collection=col, name="tree_cards", position=(0, 5, 0),
                               levers={"instances": False, "sapling": False}, crown_m=6.0)
    trees["cards"] = {"rec": crec, "type": cob.type, "children": [(c.name, instances_of(c)) for c in cob.children]}
    if res["sapling"]["ok"]:
        sob, srec = VG.tree_object("olive", 5.6, 2, False, collection=col, name="tree_sapling", position=(6, 5, 0),
                                   levers=levers, crown_m=3.5)
        zs = [(sob.matrix_world @ p.co).z for sp in sob.data.splines for p in sp.bezier_points] if sob.type == "CURVE" else []
        trees["sapling"] = {"rec": srec, "type": sob.type, "top": round(max(zs), 2) if zs else None,
                            "children": [(c.name, c.type, c.instance_type) for c in sob.children]}
    hero = VG.hero_model("olive")
    if hero is not None:
        pob, prec = VG.tree_object("olive", 4.0, 3, True, collection=col, name="tree_hero", position=(12, 5, 0), levers=levers)
        trees["polyhaven"] = {"rec": prec, "type": pob.type, "instance_type": pob.instance_type,
                              "collection": pob.instance_collection.name if pob.instance_collection else None,
                              "scale": round(pob.scale[2], 4)}
    palm, palm_rec = VG.tree_object("palm", 7.0, 4, False, collection=col, name="tree_palm", position=(18, 5, 0), levers=levers)
    trees["palm"] = {"rec": palm_rec, "children": [(c.name, len(c.data.polygons)) for c in palm.children]}
    res["trees"] = trees
    gob, grec = VG.grass_patch([(0, 10), (10, 10), (10, 16), (0, 16)], 4.0, collection=col, terrain=terrain, name="grass_near")
    res["grass"] = {"rec": grec, "instances": instances_of(gob), "camera_visible": gob.visible_camera}
    # a pool through build_site on a tiny plan (deck level 0.0, the pools lever on)
    plan = {"mode": "full", "terrain": terrain, "outline": [(30, 0), (40, 0), (40, 8), (30, 8)], "plot": [], "plot_source": "none",
            "extent": [(20, -10), (50, -10), (50, 20), (20, 20)], "wells": [], "plot_walls": [], "areas": [], "trees": [],
            "not_built": [], "assumed": [], "warnings": [], "ground_is_grass": True, "inferred": None, "copy_holes": [],
            "pools": [{"id": "pool_t", "polygon": [(32, 10), (38, 10), (38, 14), (32, 14)], "depth": 1.5, "evidence": [],
                       "deck_z": 0.0}], "hedges": [], "platforms": [], "climate": {"climate": "temperate"},
            "levers": {k: (k != "sky") for k in S.SITE_LEVERS}, "near_extent": [(20, -10), (50, -10), (50, 20), (20, 20)],
            "species": {}}
    def mk(look):
        m = bpy.data.materials.get(str(look.get("material"))) or bpy.data.materials.new(str(look.get("material")))
        return m
    looks = {k: {"material": k, "colour": None, "source": "build"} for k in ("garden", "paving", "plot_wall", "light_well", "bark", "foliage", "ground", "steps", "railing")}
    pcol = bpy.data.collections.new("pool_site"); bpy.context.scene.collection.children.link(pcol)
    objs, assumed = [], []
    summary = S.build_site(plan, pcol, looks, mk, objs, assumed)
    pool_objs = sorted(o.name for o in pcol.objects if o.get("wenart_kind") == "site_pool")
    water = bpy.data.materials.get("pool_water")
    res["pool"] = {"objects": pool_objs, "water_volume": bool(water and any(l.to_socket.name == "Volume" for l in water.node_tree.links)),
                   "tiles_nodes": [n.bl_idname for n in bpy.data.materials["pool_tiles"].node_tree.nodes],
                   "summary_objects": summary["objects"]}
    res["materials"] = sorted(m.name for m in bpy.data.materials if m.name.startswith(("veg_", "pool_", "site_")))
    json.dump(res, open(out, "w"), indent=1, default=str)
""")


@needs_blender
def test_hedge_tree_sources_and_pool_in_blender(tmp_path):
    script = tmp_path / "veg.py"
    script.write_text(VEG_SCRIPT, encoding="utf-8")
    out = tmp_path / "veg.json"
    cli.run_blender(script, [str(out), str(ROOT)], log_path=tmp_path / "veg.log")
    res = json.loads(out.read_text(encoding="utf-8"))
    h = res["hedge"]
    assert h["modifiers"] == ["NODES"] and h["rec"]["method"] == "cards" and h["thin_wall"] and h["alpha_linked"]
    assert h["instances"] > 0.5 * h["rec"]["cards"]                     # the leaf cards scattered on the core
    cards = res["trees"]["cards"]
    assert cards["rec"]["method"] == "cards" and cards["type"] == "MESH" and len(cards["children"]) == 2
    assert all(n > 0 for _name, n in cards["children"])
    palm = res["trees"]["palm"]
    assert palm["rec"]["method"] == "palm" and palm["children"][0][1] == 14
    if res["sapling"]["ok"]:
        sap = res["trees"]["sapling"]
        assert sap["rec"]["method"] == "sapling" and sap["type"] == "CURVE" and sap["top"] == pytest.approx(5.6, abs=0.3)
        assert any(c[2] == "FACES" for c in sap["children"])            # the leaf card instanced on the leaf faces
    if "polyhaven" in res["trees"]:
        hero = res["trees"]["polyhaven"]
        assert hero["rec"]["method"] == "polyhaven" and hero["instance_type"] == "COLLECTION"
        assert hero["rec"]["licence"] == "CC0" and hero["collection"].startswith("veg_") and hero["scale"] > 0
    g = res["grass"]
    assert g["instances"] > 0.8 * g["rec"]["count"] and not g["camera_visible"]
    p = res["pool"]
    assert p["objects"] == ["pool_t_basin", "pool_t_coping", "pool_t_water"] and p["water_volume"]
    assert "ShaderNodeTexBrick" in p["tiles_nodes"]
    assert {"pool_tiles", "pool_water", "veg_hedge_core", "veg_leaf_cherry_laurel"} <= set(res["materials"])


DUMP_SCRIPT = textwrap.dedent("""
    import bpy, json, sys
    out = sys.argv[sys.argv.index("--") + 1]
    rows = {"kinds": {}, "veg": [], "hedge_mods": [], "proxy_trees": 0}
    for ob in bpy.data.objects:
        k = ob.get("wenart_kind")
        if k:
            rows["kinds"][k] = rows["kinds"].get(k, 0) + 1
        if ob.get("wenart_veg_method"):
            rows["veg"].append([ob.name, ob.get("wenart_veg_method"), ob.get("wenart_species")])
        if ob.name.startswith("hedge_"):
            rows["hedge_mods"].append([ob.name, [m.type for m in ob.modifiers]])
        if ob.name.startswith("tree_") and ob.type == "MESH" and not ob.get("wenart_veg_method") and not ob.parent:
            rows["proxy_trees"] += 1
    rows["haze_volume"] = bool(bpy.data.materials.get("site_haze") and any(l.to_socket.name == "Volume" for l in bpy.data.materials["site_haze"].node_tree.links))
    rows["backdrop"] = bpy.data.objects.get("ground_backdrop") is not None
    rows["cameras"] = sorted(o.name for o in bpy.data.objects if o.type == "CAMERA" and o.get("wenart_camera_kind") == "exterior")
    json.dump(rows, open(out, "w"))
""")


@needs_blender
@pytest.mark.skipif(not REAL04.is_file(), reason="no committed real04 building")
def test_real04_site_builds_and_the_site_view_sees_the_sky(tmp_path, monkeypatch):
    monkeypatch.delenv("WENART_SITE_VARIANT", raising=False)
    manifest_path = cli.build(str(REAL04), tmp_path / "scene", no_textures=True, preview_samples=1,
                              camera_policy="search", brief=str(ROOT / "projects" / "real04"))
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    site = m["whole_building"]["site"]
    assert [h["id"] for h in site["hedges"]] == ["hedge_001", "hedge_002", "hedge_003", "hedge_004"]
    assert all(h["method"] == "cards" for h in site["hedges"])
    assert sorted(p["id"] for p in site["platforms"]) == ["sp_001", "sp_002", "sp_003", "sp_004", "spk_001"]
    assert all("slab" in p["parts"] for p in site["platforms"])
    assert len(site["vegetation"]) == 19 and {v["method"] for v in site["vegetation"]} <= {"polyhaven", "sapling", "cards", "palm"}
    assert all(v["species"] == "oleander" and v["size_class"] == "shrub" for v in site["vegetation"])
    names = {o["name"] for o in m["objects"]}
    assert {"ground", "ground_skirt", "ground_backdrop", "haze", "grass_near"} <= names
    assert {f"pool_00{k}_{part}" for k in range(1, 5) for part in ("basin", "water", "coping")} <= names
    cams = {c["name"]: c for c in m["cameras"] if c.get("kind") == "exterior"}
    assert {"ext_1", "ext_2", "ext_3", "ext_4", "ext_5", "ext_7"} <= set(cams)
    assert 1 / 3 < cams["ext_7"]["horizon_frac"] < 1.0
    (tmp_path / "dump.py").write_text(DUMP_SCRIPT, encoding="utf-8")
    dump = tmp_path / "dump.json"
    cli.run_blender(tmp_path / "dump.py", [str(dump)], blend=str(manifest_path.parent / "scene.blend"))
    rows = json.loads(dump.read_text(encoding="utf-8"))
    assert rows["proxy_trees"] == 0 and len(rows["veg"]) >= 19 and rows["haze_volume"] and rows["backdrop"]
    assert all(mods == ["NODES"] for _n, mods in rows["hedge_mods"])
    # the site view rendered small: its top rows are sky (no black band), the render records the VRAM on the GPU
    renders = cli.render(str(manifest_path.parent / "scene.blend"), tmp_path / "renders", cameras="ext_7", samples=8,
                         res="320x180")
    rm = json.loads(Path(renders).read_text(encoding="utf-8")) if str(renders).endswith(".json") \
        else json.loads((tmp_path / "renders" / "render_manifest.json").read_text(encoding="utf-8"))
    entries = rm.get("renders") or rm.get("cameras") or []
    rec = next(r for r in entries if r.get("name") == "ext_7" or r.get("camera") == "ext_7")
    assert rec.get("seconds") is not None
    from PIL import Image
    preview = next(tmp_path.glob("renders/ext_7*preview*.jpg"), None) or next(tmp_path.glob("renders/ext_7*.png"))
    with Image.open(preview) as im:
        im = im.convert("RGB")
        w, h = im.size
        top = [im.getpixel((x, y)) for y in range(0, max(1, h // 10)) for x in range(0, w, 4)]
        mean_top = sum(sum(p) for p in top) / (3 * len(top))
        black = sum(1 for y in range(0, h, 2) for x in range(0, w, 2) if max(im.getpixel((x, y))) < 6) / ((h // 2) * (w // 2))
    assert mean_top > 25 and black < 0.05
    if os.environ.get("CUDA_VISIBLE_DEVICES", "x") != "":
        assert rec.get("vram_mib") is None or rec["vram_mib"] > 0
