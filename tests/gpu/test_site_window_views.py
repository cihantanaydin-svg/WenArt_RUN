"""26 Oct 2026 (real06's "flat grey void" through every window; ``pytest -m gpu tests/gpu/test_site_window_views.py``;
skipped without a Blender binary). Two checks in Blender 5.2 of the CPU-tested rules of
``tests/test_site_views_20261026.py``:

- ``test_lawn_through_a_window_pane_keeps_its_colour``: a lawn plane with ``vegetation.lawn_material`` under a sun,
  rendered (64 x 48, 16 spp) straight and through a pane of ``materials.window_glass_material``: the median saturation
  of the view through the pane is at least ``PANE_LAWN_RATIO`` of the straight view (the rule of a623f66 turned the
  lawn 75 % grey for every ray but the camera's: the pane view kept about a third of the straight view's saturation),
  and the material's Light Path link is 'Diffuse Depth' (a wrong socket name raises in Blender).
- ``test_horizon_context_object_in_blender``: ``site.build_context`` of a small box's ``horizon_context`` gives one
  ``context_trees`` mesh with the faces of ``site.context_parts`` (27 Oct 2026: a trunk and a crown of foliage
  masses, not 68 faces a tree), a material per species and the bark, hidden from shadow, diffuse and
  volume rays, seen by the camera, transmission and glossy rays, smooth shaded."""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

from wenart.blender import cli

pytestmark = pytest.mark.gpu

ROOT = Path(__file__).resolve().parents[2]
BLENDER = cli.find_blender()
if BLENDER is None:
    pytest.skip("no Blender binary (WENART_BLENDER, /workspace/tools/blender, /opt/wenart/blender, PATH)",
                allow_module_level=True)

PANE_LAWN_RATIO = 0.7          # through the pane / straight: the new rule about 0.9-1.0, the old one about 0.3

SCRIPT = textwrap.dedent("""
    import bpy, json, math, sys
    sys.path.insert(0, sys.argv[sys.argv.index("--") + 2])
    out = sys.argv[sys.argv.index("--") + 1]
    tmp = sys.argv[sys.argv.index("--") + 3]
    from wenart.blender import materials as M
    from wenart.blender import site as S
    from wenart.blender import vegetation as VG
    res = {}
    scene = bpy.context.scene
    for ob in list(scene.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 16
    scene.render.resolution_x, scene.render.resolution_y, scene.render.resolution_percentage = 64, 48, 100
    world = bpy.data.worlds.new("w")
    scene.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.bl_idname == "ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.35, 0.42, 0.55, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    me = bpy.data.meshes.new("lawn")
    me.from_pydata([(-200, -200, 0), (200, -200, 0), (200, 200, 0), (-200, 200, 0)], [], [(0, 1, 2, 3)])
    lawn = bpy.data.objects.new("lawn", me)
    scene.collection.objects.link(lawn)
    mat = bpy.data.materials.new("lawn_mat")
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.08, 0.25, 0.05, 1.0)
    res["lawn"] = VG.lawn_material(mat)
    me.materials.append(mat)
    res["lawn_links"] = [(l.from_socket.name, l.to_node.bl_idname, getattr(l.to_node, "operation", None))
                         for l in mat.node_tree.links if l.from_node.bl_idname == "ShaderNodeLightPath"]
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.0
    sob = bpy.data.objects.new("sun", sun)
    sob.rotation_euler = (math.radians(40.0), 0.0, math.radians(30.0))
    scene.collection.objects.link(sob)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.location = (0.0, 0.0, 1.5)
    cam.rotation_euler = (math.radians(70.0), 0.0, 0.0)          # +y, 20 degrees down: lawn in the whole frame
    scene.collection.objects.link(cam)
    scene.camera = cam
    pv = [(-1.5, 1.0, 0.0), (1.5, 1.0, 0.0), (1.5, 1.006, 0.0), (-1.5, 1.006, 0.0),
          (-1.5, 1.0, 3.0), (1.5, 1.0, 3.0), (1.5, 1.006, 3.0), (-1.5, 1.006, 3.0)]
    pf = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    pme = bpy.data.meshes.new("pane")
    pme.from_pydata(pv, [], pf)
    pane = bpy.data.objects.new("pane", pme)
    pme.materials.append(M.window_glass_material("pane_glass"))
    scene.collection.objects.link(pane)

    def median_saturation(path):
        img = bpy.data.images.load(path, check_existing=False)
        px = list(img.pixels)
        sats = []
        for i in range(0, len(px), 4):
            r, g, b = px[i:i + 3]
            hi, lo = max(r, g, b), min(r, g, b)
            sats.append((hi - lo) / hi if hi > 0 else 0.0)
        sats.sort()
        return sats[len(sats) // 2]

    for name, hidden in (("straight", True), ("pane", False)):
        pane.hide_render = hidden
        scene.render.filepath = f"{tmp}/{name}.png"
        bpy.ops.render.render(write_still=True)
        res[name] = median_saturation(f"{tmp}/{name}.png")
    # the horizon context of a small box
    col = bpy.data.collections.new("site")
    scene.collection.children.link(col)
    terrain = S.terrain_model({"site": {"ground": {"levels": [{"side": "all", "z": {"value": 0.0}}]}}},
                              [(0, 0), (10, 0), (10, 8), (0, 8)])
    outline = [(0, 0), (10, 0), (10, 8), (0, 8)]
    ctx = S.horizon_context(outline, S.ground_extent(outline, S.inferred_plot(outline)), terrain, "temperate", 6.0)
    entries = []
    rec = S.build_context(ctx, col, lambda *a: entries.append(a))
    ob = bpy.data.objects.get(S.CONTEXT_NAME)
    res["context"] = {"rec": {k: v for k, v in rec.items() if k != "rings"}, "count": ctx["count"],
                      "parts_faces": len(S.context_parts(ctx)["faces"]),
                      "species": len(ctx["species"]), "entries": len(entries),
                      "object": None if ob is None else {
                          "faces": len(ob.data.polygons), "materials": [m.name for m in ob.data.materials],
                          "smooth": all(p.use_smooth for p in ob.data.polygons),
                          "visible": {a: bool(getattr(ob, a)) for a in ("visible_camera", "visible_diffuse",
                                                                        "visible_glossy", "visible_transmission",
                                                                        "visible_volume_scatter", "visible_shadow")}}}
    # 27 Oct 2026 (pod run 091638: the judge saw pale "cloud" crowns in the window views): one context tree alone in
    # the sun, framed by a camera at three crown widths, film transparent: the crown's median colour (alpha > 0.5)
    lawn.hide_render = True
    pane.hide_render = True
    t0 = max(ctx["trees"], key=lambda t: t["height"])
    tx, ty = t0["center"][0], t0["center"][1]
    h = float(t0["height"])
    dist = 3.0 * max(h, 4.0)
    cam.location = (tx, ty - dist, float(t0.get("z") or 0.0) + h * 0.55)
    cam.rotation_euler = (math.radians(90.0), 0.0, 0.0)
    scene.render.film_transparent = True
    scene.render.filepath = f"{tmp}/crown.png"
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(f"{tmp}/crown.png", check_existing=False)
    px = list(img.pixels)
    sat, val = [], []
    for i in range(0, len(px), 4):
        r, g, b, a = px[i:i + 4]
        if a < 0.5:
            continue
        hi, lo = max(r, g, b), min(r, g, b)
        sat.append((hi - lo) / hi if hi > 0 else 0.0)
        val.append(hi)
    sat.sort()
    val.sort()
    res["crown"] = {"pixels": len(sat), "saturation": sat[len(sat) // 2] if sat else None,
                    "value": val[len(val) // 2] if val else None, "tree": t0.get("species")}
    with open(out, "w") as fh:
        json.dump(res, fh)
""")


@pytest.fixture(scope="module")
def result(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("site_window_views")
    script = tmp / "views.py"
    script.write_text(SCRIPT, encoding="utf-8")
    out = tmp / "views.json"
    cli.run_blender(script, [str(out), str(ROOT), str(tmp)], log_path=tmp / "views.log")
    return json.loads(out.read_text(encoding="utf-8"))


def test_lawn_through_a_window_pane_keeps_its_colour(result):
    print(f"lawn median saturation: straight {result['straight']:.3f}, through the pane {result['pane']:.3f}")
    assert result["lawn"]["applied"] and result["lawn"]["own_colour_rays"] == "Diffuse Depth 0"
    assert ("Diffuse Depth", "ShaderNodeMath", "MINIMUM") in [tuple(x) for x in result["lawn_links"]]
    assert not [x for x in result["lawn_links"] if x[0] == "Is Camera Ray"]
    assert result["straight"] > 0.2
    assert result["pane"] >= PANE_LAWN_RATIO * result["straight"], result


def test_horizon_context_object_in_blender(result):
    ctx = result["context"]
    rec, ob = ctx["rec"], ctx["object"]
    assert rec["built"] and not rec.get("error") and ctx["entries"] == 1 and ob is not None
    assert ob["faces"] == ctx["parts_faces"] == rec["faces"]
    assert 250 * ctx["count"] <= ob["faces"] <= 600 * ctx["count"]        # crowns of foliage masses, not lollipops
    assert len(ob["materials"]) == ctx["species"] + 1 and ob["materials"][-1] == "veg_bark" and ob["smooth"]
    vis = ob["visible"]
    assert vis["visible_camera"] and vis["visible_transmission"] and vis["visible_glossy"]
    assert not vis["visible_shadow"] and not vis["visible_diffuse"] and not vis["visible_volume_scatter"]


CROWN_SATURATION_MIN = 0.25    # a green crown, not a pale grey "cloud"
CROWN_VALUE_MAX = 0.80         # under a 3 W/m2 sun and a 1.0 sky: not washed white


def test_a_context_crown_reads_green_in_the_sun(result):
    """27 Oct 2026 (pod run 091638): the context crowns read as pale clouds through the windows. One context tree
    alone in the sun: its median crown colour is a saturated, not washed-out green."""
    crown = result["crown"]
    print(f"context crown ({crown['tree']}): {crown['pixels']} px, median saturation {crown['saturation']}, "
          f"median value {crown['value']}")
    assert crown["pixels"] > 20
    assert crown["saturation"] >= CROWN_SATURATION_MIN and crown["value"] <= CROWN_VALUE_MAX, crown
