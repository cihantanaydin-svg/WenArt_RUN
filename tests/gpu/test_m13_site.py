"""Milestone 13 track T6 GPU tests (docs/milestone13.md §13.1, pod P1; ``pytest -m gpu tests/gpu/test_m13_site.py``;
skipped without a Blender binary): the vegetation and site objects built in Blender 5.2 with the expected object and
material counts, and the committed real04 building built and rendered with its site.

- ``test_hedge_tree_sources_and_pool_in_blender``: one script inside Blender (``cli.run_blender``) builds a hedge
  (``vegetation.hedge_object``: one hull mesh with a geometry-nodes modifier scattering leaf cards at the species'
  density; the leaf material with ``Thin Wall``), one tree per source (``cards`` always; ``sapling`` when the add-on
  is installed on the pod, through ``bpy.ops.curve.tree_add``: a curve object with a ``leaves`` mesh child that has
  leaf faces and the leaf-card material, round 3; ``polyhaven`` when the assets hold a Poly Haven tree: a collection
  instance of one imported glTF), a palm, a grass patch, the lawn material, and a pool and a stepped terrace through
  ``site.build_site`` (basin, water with a Volume Absorption link, coping; the terrace on a sloped ``terrain_model``
  record and the pool plan on a bare ``{kind, z}`` record: P1 raised ``KeyError: 'sides'`` there). Every expected
  object and material is counted; instances come from the evaluated depsgraph.
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
from wenart.blender import site as S
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
    # a real terrain record (terrain_model: kind, z, sides, north, changes), flat at 0
    terrain = S.terrain_model({"site": {"ground": {"levels": [{"side": "all", "z": {"value": 0.0}}]}}},
                              [(30, 0), (40, 0), (40, 8), (30, 8)])
    hedge = {"id": "h1", "polyline": [[0, 0], [8, 0]], "width_m": 0.7, "height_m": 1.2, "species": "cherry_laurel"}
    v, f, info = S.hedge_parts(hedge, terrain)
    hob, hrec = VG.hedge_object(dict(hedge, core_verts=v, core_faces=f), collection=col, name="hedge_h1")
    leaf = bpy.data.materials.get(hrec["material"])
    bsdf = next((n for n in leaf.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None)
    res["hedge"] = {"rec": hrec, "modifiers": [m.type for m in hob.modifiers], "instances": instances_of(hob),
                    "core_faces": len(hob.data.polygons), "core_info": info,
                    "thin_wall": bool(bsdf and bsdf.inputs["Thin Wall"].default_value),
                    "alpha_linked": bool(bsdf and bsdf.inputs["Alpha"].is_linked),
                    "tint": leaf.get("wenart_tint"), "mask": leaf.get("wenart_leaf_mask")}
    levers = {"instances": True, "sapling": True}
    trees = {}
    cob, crec = VG.tree_object("stone_pine", 8.0, 1, False, collection=col, name="tree_cards", position=(0, 5, 0),
                               levers={"instances": False, "sapling": False}, crown_m=6.0)
    trees["cards"] = {"rec": crec, "type": cob.type, "children": [(c.name, instances_of(c)) for c in cob.children]}
    if res["sapling"]["ok"]:
        sob, srec = VG.tree_object("olive", 5.6, 2, False, collection=col, name="tree_sapling", position=(6, 5, 0),
                                   levers=levers, crown_m=3.5)
        # matrix_world follows the post-scale and the location only after a depsgraph update (review of round 3:
        # measured without it, the curve top was the unscaled 4.87 m)
        bpy.context.view_layer.update()
        zs = [(sob.matrix_world @ p.co).z for sp in sob.data.splines for p in sp.bezier_points] if sob.type == "CURVE" else []
        kids = []
        for c in sob.children:
            mesh = c.type == "MESH"
            kids.append({"name": c.name, "type": c.type, "instance_type": c.instance_type,
                         "faces": len(c.data.polygons) if mesh else 0,
                         "materials": [m.name for m in c.data.materials] if mesh else [],
                         "uv_layers": [u.name for u in c.data.uv_layers] if mesh else [],
                         "top": round(max((c.matrix_world @ v.co).z for v in c.data.vertices), 2)
                         if mesh and len(c.data.vertices) else None})
        trees["sapling"] = {"rec": srec, "type": sob.type, "top": round(max(zs), 2) if zs else None, "children": kids}
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
    # the lawn material (round 3): a flat-colour material and a textured one (a Mapping node at a 4 m tile)
    flat = bpy.data.materials.new("lawn_flat"); flat.use_nodes = True
    flat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.077, 0.097, 0.0, 1.0)
    tex = bpy.data.materials.new("lawn_tex"); tex.use_nodes = True
    mp = tex.node_tree.nodes.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (0.25, 0.25, 1.0)
    rgb = tex.node_tree.nodes.new("ShaderNodeRGB")
    tex.node_tree.links.new(rgb.outputs[0], tex.node_tree.nodes["Principled BSDF"].inputs["Base Color"])
    # Blender 5.x gives every new material a node tree with a Principled BSDF (Material.use_nodes is deprecated):
    # the case lawn_material leaves alone is a node tree without a Principled BSDF
    plain = bpy.data.materials.new("lawn_plain")
    for n in [n for n in plain.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"]:
        plain.node_tree.nodes.remove(n)
    res["lawn"] = {"flat": VG.lawn_material(flat), "flat_again": VG.lawn_material(flat), "tex": VG.lawn_material(tex),
                   "plain": VG.lawn_material(plain), "tex_scale": list(mp.inputs["Scale"].default_value),
                   "flat_nodes": sorted(n.bl_idname for n in flat.node_tree.nodes),
                   "flat_base_linked": flat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].is_linked}
    # a pool through build_site on a tiny plan (deck level 0.0, the pools lever on) on a bare terrain record (P1
    # raised KeyError 'sides' here)
    bare = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}}
    plan = {"mode": "full", "terrain": bare, "outline": [(30, 0), (40, 0), (40, 8), (30, 8)], "plot": [], "plot_source": "none",
            "extent": [(20, -10), (50, -10), (50, 20), (20, 20)], "wells": [], "plot_walls": [], "areas": [], "trees": [],
            "not_built": [], "assumed": [], "warnings": [], "ground_is_grass": True, "inferred": None, "copy_holes": [],
            "pools": [{"id": "pool_t", "polygon": [(32, 10), (38, 10), (38, 14), (32, 14)], "depth": 1.5, "evidence": [],
                       "deck_z": 0.0}], "hedges": [], "platforms": [], "climate": {"climate": "temperate"},
            "levers": {k: (k != "sky") for k in S.SITE_LEVERS}, "near_extent": [(20, -10), (50, -10), (50, 20), (20, 20)],
            "species": {}}
    def mk(look):
        m = bpy.data.materials.get(str(look.get("material"))) or bpy.data.materials.new(str(look.get("material")))
        return m
    looks = {k: {"material": k, "colour": None, "source": "build"} for k in ("garden", "paving", "plot_wall", "light_well", "bark", "foliage", "ground", "steps", "railing", "facade")}
    pcol = bpy.data.collections.new("pool_site"); bpy.context.scene.collection.children.link(pcol)
    objs, assumed = [], []
    summary = S.build_site(plan, pcol, looks, mk, objs, assumed)
    pool_objs = sorted(o.name for o in pcol.objects if o.get("wenart_kind") == "site_pool")
    water = bpy.data.materials.get("pool_water")
    res["pool"] = {"objects": pool_objs, "water_volume": bool(water and any(l.to_socket.name == "Volume" for l in water.node_tree.links)),
                   "tiles_nodes": [n.bl_idname for n in bpy.data.materials["pool_tiles"].node_tree.nodes],
                   "summary_objects": summary["objects"], "terrain": summary["terrain"], "lawn": summary.get("lawn")}
    # a stepped terrace through build_site: a 'sides' terrain 2.5 m lower on the -x side, a terrace at the +x level
    sloped = S.terrain_model({"site": {"ground": {"levels": [{"side": "left", "z": {"value": -6.0}},
                                                              {"side": "right", "z": {"value": 0.0}}]}}},
                             [(60, 0), (70, 0), (70, 8), (60, 8)])
    # the terrace sits across the corner blend of the two sides (the ground falls 2.5 m over it)
    tsite = {"ground": {"levels": [], "points": []}, "paving": [{"id": "t1", "polygon": [[52, -8], [58, -8], [58, -2], [52, -2]],
                                                                 "build": True}], "parking": [], "pools": []}
    tpfs = S.platforms(tsite, sloped)
    tplan = dict(plan, terrain=sloped, outline=[(60, 0), (70, 0), (70, 8), (60, 8)], extent=[(40, -10), (80, -10), (80, 20), (40, 20)],
                 near_extent=[(40, -10), (80, -10), (80, 20), (40, 20)], pools=[], platforms=tpfs,
                 areas=[{"id": "t1", "kind": "paving", "polygon": [[52, -8], [58, -8], [58, -2], [52, -2]], "z": None, "material": None,
                         "colour": None, "source": "site_plan", "area_id": None, "lift": S.PAVING_LIFT, "platform_id": "t1"}])
    # pre-flight of P3: a drawn hedge beside the terrace, so the assumed entries of both kinds are checked
    tplan["hedges"] = [{"id": "hedge_t", "polyline": [[52, -10], [58, -10]], "width_m": 0.7, "height_m": 1.2,
                        "height_class": "mid", "species": "cherry_laurel", "species_inferred": True, "inferred": True,
                        "evidence": [], "source": "site.hedges", "symbol_ids": [], "reason": "a test hedge"}]
    tcol = bpy.data.collections.new("terrace_site"); bpy.context.scene.collection.children.link(tcol)
    tobjs, tassumed = [], []
    tsum = S.build_site(tplan, tcol, looks, mk, tobjs, tassumed)
    res["terrace"] = {"platforms": tsum["platforms"], "terrain": tsum["terrain"], "assumed": tassumed,
                      "objects": sorted(o.name for o in tcol.objects if o.get("wenart_kind") == S.site_kind("platform")),
                      "facade_material": mk(looks["facade"]).name,
                      "wall_materials": sorted({o.data.materials[0].name for o in tcol.objects if o.name.endswith("_wall") and o.data.materials})}
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
    # round 3: the hull core, the species' density and cover, the atlas opacity mask on the pod's assets
    assert h["rec"]["core"] == "hull" and h["core_info"]["core"] == "hull" and h["core_faces"] == 12
    assert h["rec"]["density"] == VG.hedge_density(0.9) and h["rec"]["cover_layers"] == pytest.approx(2.0, abs=0.05)
    assert h["rec"]["cards"] == round(26.48 * h["rec"]["density"])     # 8 m x (0.7 + 2 x 1.2) + 2 x 0.7 x 1.2 m²
    assert h["tint"] and "gain 1.6" in h["tint"]
    if h["rec"]["atlas"]:
        assert h["mask"] == "opacity_map"                               # the ambientCG Opacity map drives the alpha
    cards = res["trees"]["cards"]
    assert cards["rec"]["method"] == "cards" and cards["type"] == "MESH" and len(cards["children"]) == 2
    assert all(n > 0 for _name, n in cards["children"])
    palm = res["trees"]["palm"]
    assert palm["rec"]["method"] == "palm" and palm["children"][0][1] == 14
    if res["sapling"]["ok"]:
        sap = res["trees"]["sapling"]
        assert sap["rec"]["method"] == "sapling" and sap["type"] == "CURVE" and sap["top"] == pytest.approx(5.6, abs=0.4)
        # round 3 (P1: bare branches): the add-on's own 'rect' leaf quads in its leaves mesh with the leaf material
        assert sap["rec"]["leaf_faces"] > 0 and sap["rec"]["leaf_shape"] == "rect" and sap["rec"]["leaves"]
        leaves = next(c for c in sap["children"] if c["type"] == "MESH" and c["name"].endswith("_leaves"))
        assert leaves["faces"] == sap["rec"]["leaf_faces"] and leaves["materials"] == [sap["rec"]["material"]]
        assert leaves["instance_type"] == "NONE" and "leafUV" in leaves["uv_layers"]
        # the drawn height exactly: _tree_sapling scales the tree so its top (curve or leaves) is 5.6 m
        assert max(leaves["top"], sap["top"]) == pytest.approx(5.6, abs=0.05) and sap["top"] <= leaves["top"] + 0.01
        assert sap["rec"]["material"].startswith("veg_leaf_")           # the same material as the leaf cards
    if "polyhaven" in res["trees"]:
        hero = res["trees"]["polyhaven"]
        assert hero["rec"]["method"] == "polyhaven" and hero["instance_type"] == "COLLECTION"
        assert hero["rec"]["licence"] == "CC0" and hero["collection"].startswith("veg_") and hero["scale"] > 0
    g = res["grass"]
    assert g["instances"] > 0.8 * g["rec"]["count"] and not g["camera_visible"]
    # round 3: the lawn material: tiling clamped to 1-2 m, a noise-driven variation into the base colour, a bump
    lawn = res["lawn"]
    assert lawn["flat"]["applied"] and lawn["flat"]["tile_m"] is None and lawn["flat"]["bump"] and lawn["flat_base_linked"]
    assert lawn["flat_again"]["applied"] and lawn["flat_again"].get("bump") == lawn["flat"]["bump"]     # idempotent
    assert {"ShaderNodeTexNoise", "ShaderNodeValToRGB", "ShaderNodeMix", "ShaderNodeBump"} <= set(lawn["flat_nodes"])
    assert lawn["tex"]["applied"] and lawn["tex"]["tile_m"] == 2.0 and lawn["tex_scale"][0] == pytest.approx(0.5)
    assert not lawn["plain"]["applied"] and lawn["plain"]["reason"] == "no Principled BSDF"
    p = res["pool"]
    assert p["objects"] == ["pool_t_basin", "pool_t_coping", "pool_t_water"] and p["water_volume"]
    assert "ShaderNodeTexBrick" in p["tiles_nodes"]
    assert p["terrain"]["sides"] == [] and p["terrain"]["changes"] == [] and p["terrain"]["kind"] == "flat"
    assert {"pool_tiles", "pool_water", "veg_hedge_core", "veg_leaf_cherry_laurel"} <= set(res["materials"])
    # round 3: the stepped terrace: bands, every wall built within the cap, never the facade's material; 28 Oct 2026
    # (wenart/blender/grading.py): with room around it (no plot, nothing beside it) the terrace meets the ground by
    # lawn banks of at most 1:3 instead of tiers, its walls in the house's base stone with copings
    t = res["terrace"]
    assert t["terrain"]["kind"] == "sides" and len(t["terrain"]["sides"]) == 2
    ids = [q["id"] for q in t["platforms"]]
    t1 = next(q for q in t["platforms"] if q["id"] == "t1")
    assert any(q["parent"] == "t1" for q in t["platforms"]) or t1.get("banks")
    assert all(b["slope"] <= 0.5 + 1e-6 for b in t1.get("banks") or [])
    assert all(q["wall_max_m"] <= S.RETAINING_MAX_M + 1e-6 for q in t["platforms"]), \
        [(q["id"], q["wall_max_m"]) for q in t["platforms"]]
    assert all(w["height_m"] <= S.RETAINING_MAX_M + 1e-6 for q in t["platforms"] for w in q["walls"])
    assert all(q["ground_z"] and q["retaining_cap_m"] == S.RETAINING_MAX_M for q in t["platforms"])
    assert "platform_t1_slab" in t["objects"] and "platform_t1_wall" in t["objects"]
    # pre-flight of P3 (16 Oct 2026): every assumed entry of build_site matches the scene manifest schema (the
    # platform and hedge entries had ``kind`` without ``parent``: 32 errors in the real04 manifest)
    import jsonschema
    from wenart.blender import schemas
    kinds = {a.get("kind") for a in t["assumed"]}
    assert {"site_platform", "site_hedge"} <= kinds, kinds
    for a in t["assumed"]:
        jsonschema.validate(a, schemas.ASSUMED_ENTRY)
    assert t["wall_materials"] and t["facade_material"] not in t["wall_materials"]


DUMP_SCRIPT = textwrap.dedent("""
    import bpy, json, sys
    out = sys.argv[sys.argv.index("--") + 1]
    rows = {"kinds": {}, "veg": [], "hedge_mods": [], "proxy_trees": 0, "sapling_leaves": [], "lawn": None}
    for ob in bpy.data.objects:
        k = ob.get("wenart_kind")
        if k:
            rows["kinds"][k] = rows["kinds"].get(k, 0) + 1
        if ob.get("wenart_veg_method"):
            rows["veg"].append([ob.name, ob.get("wenart_veg_method"), ob.get("wenart_species")])
        if ob.get("wenart_veg_method") == "sapling":
            rows["sapling_leaves"].append([ob.name, ob.get("wenart_leaf_faces"),
                                           [len(c.data.polygons) for c in ob.children if c.type == "MESH"]])
        if ob.name == "ground" and ob.data.materials and ob.data.materials[0]:
            rows["lawn"] = ob.data.materials[0].get("wenart_lawn")
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
    assert all(h["method"] == "cards" and h["core"] == "hull" and h["cards_per_m2"] == VG.hedge_density(0.9)
               for h in site["hedges"])                                 # round 3: the hull, the species' density
    primary = sorted(p["id"] for p in site["platforms"] if not p.get("parent"))
    assert primary == ["sp_001", "sp_002", "sp_003", "sp_004", "spk_001"]
    assert all("slab" in p["parts"] for p in site["platforms"])
    # round 3 (P1 real04 ext_1 'platforms': a tall white box): stepped bands, no wall over the retaining cap except
    # the two next to the parking spk_001, recorded with what blocked their band (review of round 3); no wall or band
    # on the edges facing the building or the copy (sp_001 is drawn 0.65 m into the basement L-1)
    assert any(p.get("parent") for p in site["platforms"])
    over = {(p["id"], c["edge"]) for p in site["platforms"] for c in p.get("cap_exceeded") or []}
    assert all(c["blocked_by"] for p in site["platforms"] for c in p.get("cap_exceeded") or [])
    # (as tests/test_m13_site.py: the decks held by the driveway's wall, the band sides at sp_002's north end and, 28
    # Oct 2026, the walled end of sp_004_s1e7 where the bare slab side showed before)
    assert {pid for pid, _e in over} <= {"sp_002", "sp_003", "sp_004", "sp_002_s1e4", "sp_002_s1e5", "sp_004_s1e7"}
    assert all(p["wall_max_m"] <= S.RETAINING_MAX_M + 1e-6 or p["cap_exceeded"] for p in site["platforms"]), \
        [(p["id"], p["wall_max_m"]) for p in site["platforms"] if p["wall_max_m"] > S.RETAINING_MAX_M]
    assert all(w["height_m"] <= S.RETAINING_MAX_M + 1e-6 for p in site["platforms"] for w in p["walls"]
               if (p["id"], w["edge"]) not in over)
    assert all(w["edge"] not in p["against_edges"] for p in site["platforms"] for w in p["walls"])
    assert next(p for p in site["platforms"] if p["id"] == "sp_001")["against_edges"]
    assert all(p["ground_z"] and p["materials"].get("slab") for p in site["platforms"])
    # 28 Oct 2026: the 19 drawn shrubs and the inferred shrubs of the planted terrace tiers (grading.tier_plants)
    drawn = [v for v in site["vegetation"] if "_plant" not in v["id"]]
    assert len(drawn) == 19 and len(site["vegetation"]) > 19
    assert {v["method"] for v in site["vegetation"]} <= {"polyhaven", "sapling", "cards", "palm"}
    assert all(v["species"] == "oleander" and v["size_class"] == "shrub" for v in site["vegetation"])
    assert all((v["leaf_faces"] or 0) > 0 for v in site["vegetation"] if v["method"] == "sapling")
    assert site["lawn"] and site["lawn"]["applied"]                     # round 3: the lawn look on the ground
    names = {o["name"] for o in m["objects"]}
    assert {"ground", "ground_skirt", "ground_backdrop", "haze", "grass_near"} <= names
    ground = next(o for o in m["objects"] if o["name"] == "ground")
    assert ground["lawn"]["applied"]
    assert {f"pool_00{k}_{part}" for k in range(1, 5) for part in ("basin", "water", "coping")} <= names
    cams = {c["name"]: c for c in m["cameras"] if c.get("kind") == "exterior"}
    assert {"ext_1", "ext_2", "ext_3", "ext_4", "ext_5", "ext_7"} <= set(cams)
    assert 1 / 3 < cams["ext_7"]["horizon_frac"] < 1.0
    # fix round after P3 (16-17 Oct 2026): the aerial view ext_5 keeps the horizon in the upper part of its frame
    # (P3: 30 degrees down at 26.87 mm, horizon at 1.27, no sky); the terrace hedges stand on their terraces, kept on
    # the slab (hedge_003 on sp_001, hedge_004 on sp_004)
    assert cams["ext_5"]["view"] == "aerial" and 0.5 < cams["ext_5"]["horizon_frac"] < 0.95
    hedges = {h["id"]: h for h in site["hedges"]}
    levels = {p["id"]: p["z"] for p in site["platforms"]}
    for hid, pid in (("hedge_003", "sp_001"), ("hedge_004", "sp_004")):
        assert hedges[hid]["z_range"][0] == pytest.approx(levels[pid] - 0.1, abs=1e-3), hid
        assert hedges[hid]["fit"]["keeps"] == [pid] and not hedges[hid]["fit"]["narrowed"], hid
    if site.get("lawn_relief"):                                                      # the instances lever is on
        assert site["lawn_relief"]["range_m"][1] <= 0.0 and site["lawn_relief"]["edges_kept"]   # never rises
        # fix round part 2 (17 Oct 2026): level under real04's two entrance paths, the sloped parking, the 19 shrubs
        # and the hedges (CPU: 8776 of the 11138 inner vertices keep the relief), and the grass follows the ground
        keep = site["lawn_relief"]["keep"]
        assert keep.get("area", 0) >= 2 and keep.get("sloped_platform", 0) >= 1 and keep.get("shrub", 0) >= 19, keep
        assert site["lawn_relief"]["weighted"] > 0 and site["grass"]["relief"] and site["grass"]["relief_requested"]
    (tmp_path / "dump.py").write_text(DUMP_SCRIPT, encoding="utf-8")
    dump = tmp_path / "dump.json"
    cli.run_blender(tmp_path / "dump.py", [str(dump)], blend=str(manifest_path.parent / "scene.blend"))
    rows = json.loads(dump.read_text(encoding="utf-8"))
    assert rows["proxy_trees"] == 0 and len(rows["veg"]) >= 19 and rows["haze_volume"] and rows["backdrop"]
    assert all(mods == ["NODES"] for _n, mods in rows["hedge_mods"])
    assert all(n > 0 and any(f > 0 for f in faces) for _name, n, faces in rows["sapling_leaves"])   # never bare
    assert rows["lawn"] and "tile_m" in rows["lawn"]                    # the ground material carries the lawn look
    assert {"site_hedge", "site_platform", "site_grass", "atmosphere"} <= set(rows["kinds"])         # own kinds
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


# --------------------------------------------------------------------------
# Fix round after P3 (16-17 Oct 2026; docs/milestone13.md §14.8 attempt 2)
# --------------------------------------------------------------------------

FIX_SCRIPT = textwrap.dedent("""
    import bpy, json, os, sys
    sys.path.insert(0, sys.argv[sys.argv.index("--") + 2])
    out, maps = sys.argv[sys.argv.index("--") + 1], sys.argv[sys.argv.index("--") + 3]
    from wenart.blender import materials as M
    from wenart.blender import site as S
    from wenart.blender import vegetation as VG
    res = {}
    # 1. a terrace on a sloped ground with a hedge drawn 0.1 m inside its west edge (site_plan fits it, build_site
    #    builds it on the terrace's level), the far lawn's relief and the grass on it
    sloped = S.terrain_model({"site": {"ground": {"levels": [{"side": "left", "z": {"value": -6.0}},
                                                              {"side": "right", "z": {"value": 0.0}}]}}},
                             [(60, 0), (70, 0), (70, 8), (60, 8)])
    tsite = {"ground": {"levels": [], "points": []}, "paving": [{"id": "t1", "polygon": [[52, -8], [58, -8], [58, -2],
                                                                                         [52, -2]], "build": True}],
             "parking": [], "pools": []}
    pfs = S.platforms(tsite, sloped)
    t1 = next(p for p in pfs if p["id"] == "t1")
    hedge = {"id": "hedge_t", "polyline": [[52.1, -7], [52.1, -3]], "width_m": 0.7, "height_m": 1.2,
             "height_class": "mid", "species": "cherry_laurel", "species_inferred": True, "inferred": True,
             "evidence": [], "source": "site.hedges", "symbol_ids": [], "reason": "a test hedge"}
    hedges, fit_assumed = S.fit_hedges([hedge], pfs, [[(60, 0), (70, 0), (70, 8), (60, 8)]])
    plan = {"mode": "full", "terrain": sloped, "outline": [(60, 0), (70, 0), (70, 8), (60, 8)], "plot": [],
            "plot_source": "none", "extent": [(40, -12), (80, -12), (80, 20), (40, 20)], "wells": [], "plot_walls": [],
            "areas": [{"id": "t1", "kind": "paving", "polygon": [[52, -8], [58, -8], [58, -2], [52, -2]], "z": None,
                       "material": None, "colour": None, "source": "site_plan", "area_id": None,
                       "lift": S.PAVING_LIFT, "platform_id": "t1"},
                      # fix round part 2: a draped path on the lawn (no platform) and a shrub on the lawn
                      {"id": "path_g", "kind": "path", "polygon": [[42, -7], [50, -7], [50, -5.8], [42, -5.8]],
                       "z": None, "material": None, "colour": None, "source": "assumed", "area_id": None,
                       "lift": S.PAVING_LIFT, "inferred": True}],
            "trees": [{"id": "shrub_t", "kind": "tree", "center": [55.0, -5.0], "size": [0.718, 0.718]},
                      {"id": "shrub_l", "kind": "tree", "center": [45.0, 5.0], "size": [0.718, 0.718]}],
            "not_built": [], "assumed": fit_assumed, "warnings": [], "ground_is_grass": True, "inferred": None,
            "copy_holes": [], "pools": [], "hedges": hedges, "platforms": pfs, "climate": {"climate": "temperate"},
            "levers": {k: (k != "sky") for k in S.SITE_LEVERS}, "near_extent": [(40, -12), (80, -12), (80, 20), (40, 20)],
            "species": {}}
    def mk(look):
        return bpy.data.materials.get(str(look.get("material"))) or bpy.data.materials.new(str(look.get("material")))
    looks = {k: {"material": k, "colour": None, "source": "build"} for k in ("garden", "paving", "plot_wall",
             "light_well", "bark", "foliage", "ground", "steps", "railing", "facade")}
    col = bpy.data.collections.new("fix_site"); bpy.context.scene.collection.children.link(col)
    objs, assumed = [], []
    summary = S.build_site(plan, col, looks, mk, objs, assumed)
    hob = bpy.data.objects["hedge_t"]
    hz = [(hob.matrix_world @ v.co).z for v in hob.data.vertices]
    hx = [(hob.matrix_world @ v.co).x for v in hob.data.vertices]
    tree = next(o for o in col.objects if o.name.startswith("tree_shrub_t"))
    ground = bpy.data.objects["ground"]
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ground.evaluated_get(dg).to_mesh()
    rise = max(ev.vertices[i].co.z - ground.data.vertices[i].co.z for i in range(len(ground.data.vertices)))
    drop = min(ev.vertices[i].co.z - ground.data.vertices[i].co.z for i in range(len(ground.data.vertices)))
    grass = bpy.data.objects.get("grass_near")
    # fix round part 2: the relief leaves the ground level under the draped path and around the lawn shrub
    off = [(v.co.x, v.co.y, ev.vertices[i].co.z - v.co.z) for i, v in enumerate(ground.data.vertices)]
    under_path = [d for x, y, d in off if 42 <= x <= 50 and -7 <= y <= -5.8]
    at_shrub = [d for x, y, d in off if (x - 45.0) ** 2 + (y - 5.0) ** 2 <= 0.6 ** 2]
    lawn_shrub = next(o for o in col.objects if o.name.startswith("tree_shrub_l"))
    res["site"] = {"t1_z": t1["z"], "hedge_z": [min(hz), max(hz)], "hedge_x": [min(hx), max(hx)],
                   "hedge_fit": summary["hedges"][0].get("fit"), "tree_z": tree.location.z,
                   "relief": {"mid": ground.modifiers["lawn_relief"].mid_level,
                              "group": ground.modifiers["lawn_relief"].vertex_group, "rise": rise, "drop": drop},
                   "lawn_relief": summary.get("lawn_relief"),
                   "grass_mods": [m.type for m in grass.modifiers] if grass else None,
                   "under_path": [len(under_path), max(abs(d) for d in under_path)],
                   "at_shrub": [len(at_shrub), max(abs(d) for d in at_shrub)],
                   "lawn_shrub_z": lawn_shrub.location.z, "shrub_ground_z": S.ground_z(sloped, 45.0, 5.0),
                   "grass": {k: summary["grass"].get(k) for k in ("relief", "relief_requested")}}
    # fix round part 2: a flat site: the ground gets no relief (convex pieces: no inner vertex), nor does the grass
    for o in list(col.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    flat = {"kind": "flat", "z": {k: 0.0 for k in S.AXES}, "warnings": [], "assumed": []}
    fplan = dict(plan, terrain=flat, platforms=[], hedges=[], areas=plan["areas"][1:], trees=plan["trees"][1:])
    col2 = bpy.data.collections.new("fix_site_flat"); bpy.context.scene.collection.children.link(col2)
    fsummary = S.build_site(fplan, col2, looks, mk, [], [])
    fground = next(o for o in col2.objects if o.name.startswith("ground"))
    fgrass = next(o for o in col2.objects if o.name.startswith("grass_near"))
    res["flat"] = {"ground_mods": [m.type for m in fground.modifiers], "grass_mods": [m.type for m in fgrass.modifiers],
                   "lawn_relief": fsummary.get("lawn_relief"), "grass_relief": fsummary["grass"].get("relief")}
    # 2. the shell slots: the front slot paints (no plank photo), the worktop's Marble012 repeats every 2 m
    tex = {}
    for aid, assumed_size in (("white_planks_clean", False), ("Marble012", True)):
        tex[aid] = {"id": aid, "source": "ambientcg" if aid == "Marble012" else "polyhaven", "licence": "CC0",
                    "size_m": [1.0, 1.0] if assumed_size else [1.8, 1.8],
                    "files": {k: os.path.join(maps, f"{aid}_{k}.jpg") for k in ("albedo", "normal", "roughness")},
                    **({"size_assumed": True} if assumed_size else {})}
    lib = M.MaterialLibrary(tex, maps, levers={"shell": True})
    mats = {}
    for name, mat in (("trim", lib.get("painted_wood_white")), ("front", lib.get("painted_wood_white", "white_planks_clean", colour="white")),
                      ("worktop", lib.get("stone_worktop"))):
        rec = lib.records[mat.name]
        mats[name] = {"images": sorted(n.image.name for n in mat.node_tree.nodes
                                       if n.bl_idname == "ShaderNodeTexImage" and n.image),
                      "mapping": [list(n.inputs["Scale"].default_value) for n in mat.node_tree.nodes
                                  if n.bl_idname == "ShaderNodeMapping"],
                      "dropped": rec.get("shell_photo_dropped"), "size_m": rec.get("size_m"), "slot": rec.get("shell_slot")}
    res["materials"] = mats
    json.dump(res, open(out, "w"), indent=1, default=str)
""")


@needs_blender
def test_p3_fix_round_plants_on_the_terrace_lawn_relief_and_shell_finishes_in_blender(tmp_path):
    """Fix round after P3 in Blender 5.2: a hedge drawn 0.1 m inside a terrace edge is built on the terrace's level
    with its hull on the slab (``fit_hedges`` + ``stand_terrain``), a shrub on the terrace stands on it; the far
    lawn's Displace relief only goes down and keeps the ground's edges (``lawn_relief``: mid level 1, the vertex
    group), the grass surface gets the same relief before its scatter; the front shell slot paints without the plank
    photo (``paint_drop``) and the worktop's Marble012 repeats every 2 m (``slot_repeat_m``). Fix round part 2
    (17 Oct 2026): the relief leaves the ground level under a draped path and around a lawn shrub
    (``site.relief_keep``), and a flat site's ground and grass get no relief."""
    from PIL import Image

    maps = tmp_path / "maps"
    maps.mkdir()
    for aid in ("white_planks_clean", "Marble012"):
        for key in ("albedo", "normal", "roughness"):
            Image.new("RGB", (8, 8), (180, 180, 180)).save(maps / f"{aid}_{key}.jpg")
    script = tmp_path / "fix.py"
    script.write_text(FIX_SCRIPT, encoding="utf-8")
    out = tmp_path / "fix.json"
    cli.run_blender(script, [str(out), str(ROOT), str(maps)], log_path=tmp_path / "fix.log")
    res = json.loads(out.read_text(encoding="utf-8"))
    site = res["site"]
    assert site["hedge_z"][0] == pytest.approx(site["t1_z"] - 0.1, abs=1e-3)
    assert site["hedge_z"][1] == pytest.approx(site["t1_z"] + 1.2, abs=1e-3)
    assert site["hedge_x"][0] >= 52.0 - 1e-3 and site["hedge_fit"]["keeps"] == ["t1"]      # the hull on the slab
    assert site["tree_z"] == pytest.approx(site["t1_z"], abs=1e-3)
    assert site["relief"]["mid"] == 1.0 and site["relief"]["group"] == VG.LAWN_RELIEF_GROUP
    assert site["relief"]["rise"] <= 1e-5 and site["relief"]["drop"] < -1e-3
    assert site["lawn_relief"]["range_m"] == list(VG.relief_range())
    assert site["grass_mods"] == ["DISPLACE", "NODES"]
    # fix round part 2 (17 Oct 2026): level under the draped path and around the lawn shrub, which stands on it; the
    # grass follows the ground's relief; on a flat site neither the ground nor the grass gets a relief
    assert site["under_path"][0] >= 10 and site["under_path"][1] <= 1e-6
    assert site["at_shrub"][0] >= 1 and site["at_shrub"][1] <= 1e-6
    assert site["lawn_shrub_z"] == pytest.approx(site["shrub_ground_z"], abs=1e-4)
    assert site["lawn_relief"]["weighted"] > 0 and site["lawn_relief"]["keep"]["area"] == 1
    assert site["lawn_relief"]["keep"]["shrub"] == 2 and site["lawn_relief"]["keep"]["hedge"] == 1
    assert site["grass"] == {"relief": True, "relief_requested": True}
    flat = res["flat"]
    assert flat["ground_mods"] == [] and flat["grass_mods"] == ["NODES"] and flat["grass_relief"] is False
    assert flat["lawn_relief"]["weighted"] == 0 and not flat["lawn_relief"]["applied"]
    mats = res["materials"]
    assert mats["trim"]["images"] == [] and mats["front"]["images"] == [] and mats["trim"]["slot"] == "front"
    assert mats["front"]["dropped"]["asset"] == "white_planks_clean"
    assert len(mats["worktop"]["images"]) == 3 and mats["worktop"]["size_m"] == [2.0, 2.0]
    assert mats["worktop"]["mapping"] and mats["worktop"]["mapping"][0][:2] == [pytest.approx(0.5)] * 2
