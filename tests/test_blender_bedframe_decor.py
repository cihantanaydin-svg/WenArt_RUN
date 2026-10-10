"""Milestone 8 builder (docs/milestone8.md §4; wenart/blender/furniture.py): a library bed frame made up with the
parametric mattress, duvet and pillows (one piece: one object, one wenart_id, one pass index), rugs (library,
flat on the rug size; parametric fallback) and wall art (library only, on the wall over the built top of its
piece, facing the room) as hostless decor with their own pass index; the model licence gate for the new
sources. The scene is built in Blender from the CPU decor and fit steps (``decor.add_decor`` and
``fit.fit_building`` with a canned catalogue of three tiny GLBs made in Blender here); skipped without Blender.
"""
from __future__ import annotations

import json
import math
import textwrap
from pathlib import Path

import pytest

from wenart import views as V
from wenart.blender import cli, schemas
from wenart.blender import furniture as BF
from wenart.blender import parametric as P
from wenart.furniture import decor as D
from wenart.furniture import fit as F

from test_blender_furniture import STYLE, needs_blender
from test_decor_m8 import of_type, room_building
from test_furniture_fit_v2 import FakeCatalog, decor_model, model

MODELS_SCRIPT = textwrap.dedent("""
    import bpy, sys
    out = sys.argv[sys.argv.index("--") + 1]

    def reset():
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def box(name, lo, hi, colour):
        verts = [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        faces = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
        me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
        mat = bpy.data.materials.get(name + "_mat") or bpy.data.materials.new(name + "_mat")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = colour
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)

    def export(name):
        bpy.ops.export_scene.gltf(filepath=f"{out}/{name}.glb", export_format="GLB", export_yup=True,
                                  export_apply=True)

    # Bed frame 1.6 x 2.1 m, headboard at +Y (front -Y), legs, side rails, a slatted deck whose top is 0.30 m.
    reset()
    wood = (0.4, 0.25, 0.1, 1.0)
    for i, (x, y) in enumerate([(-0.8, -1.05), (0.74, -1.05), (-0.8, 0.93), (0.74, 0.93)]):
        box(f"leg{i}", (x, y, 0.0), (x + 0.06, y + 0.06, 0.15), wood)
    box("rail_l", (-0.8, -1.05, 0.15), (-0.74, 0.99, 0.38), wood)
    box("rail_r", (0.74, -1.05, 0.15), (0.8, 0.99, 0.38), wood)
    box("rail_f", (-0.8, -1.05, 0.15), (0.8, -0.99, 0.38), wood)
    box("deck", (-0.74, -0.99, 0.25), (0.74, 0.99, 0.30), wood)
    box("headboard", (-0.8, 0.99, 0.0), (0.8, 1.05, 1.0), wood)
    export("frame")
    # Rug 2.0 x 1.4 m, 1 cm thick.
    reset()
    box("rug", (-1.0, -0.7, 0.0), (1.0, 0.7, 0.01), (0.6, 0.2, 0.2, 1.0))
    export("rug")
    # Wall art 0.8 x 0.6 m: a frame 3 cm deep with its canvas on the front (-Y) face.
    reset()
    box("art_frame", (-0.4, -0.01, 0.0), (0.4, 0.02, 0.6), (0.05, 0.05, 0.05, 1.0))
    box("art_canvas", (-0.37, -0.015, 0.03), (0.37, -0.01, 0.57), (0.9, 0.8, 0.3, 1.0))
    export("art")
""")

DUMP_SCRIPT = textwrap.dedent("""
    import bpy, json, sys
    out = sys.argv[sys.argv.index("--") + 1]
    rows = {}
    for ob in bpy.data.objects:
        if ob.type != "MESH" or not (ob.name.startswith("furn_") or ob.name.startswith("decor_")):
            continue
        me = ob.data
        pts = [list(ob.matrix_world @ v.co) for v in me.vertices]
        mats = [m.name if m else None for m in me.materials]
        faces = [{"material": mats[p.material_index] if p.material_index < len(mats) else None,
                  "smooth": p.use_smooth, "verts": list(p.vertices)} for p in me.polygons]
        rows[ob.name] = {"wenart_id": ob.get("wenart_id"), "kind": ob.get("wenart_kind"),
                         "pass_index": ob.pass_index, "verts": pts, "faces": faces, "materials": mats,
                         "props": {k: ob.get(k) for k in ("wenart_type", "wenart_asset", "wenart_host",
                                                          "wenart_anchor")}}
    json.dump(rows, open(out, "w"))
""")

FRAME = model("frame", "bed_double", 1.6, 2.1, 1.0, has_mattress=False, bed_frame=True, deck_height_m=0.30)
RUG = decor_model("rug", "rug", 2.0, 1.4, 0.01)
ART = decor_model("art", "wall_art", 0.8, 0.035, 0.6)


def bounds(points):
    return [[min(p[i] for p in points), max(p[i] for p in points)] for i in range(3)]


def to_local(p, fp):
    """A world point in the piece frame of ``fp`` (footprint)."""
    a = math.radians(float(fp["rotation_deg"]))
    dx, dy = p[0] - fp["center"][0], p[1] - fp["center"][1]
    return (math.cos(a) * dx + math.sin(a) * dy, -math.sin(a) * dx + math.cos(a) * dy, p[2])


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    pytest.importorskip("jsonschema")
    if cli.find_blender() is None:
        pytest.skip("no Blender binary")
    tmp = tmp_path_factory.mktemp("m8_scene")
    assets = tmp / "assets"
    (assets / "models" / "abo").mkdir(parents=True)
    (tmp / "models.py").write_text(MODELS_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "models.py", [str(assets / "models" / "abo")])
    # The CPU steps: decor rules, then the fit with the canned catalogue.
    b = room_building(width=8.0, depth=6.0, furniture=[
        ("sofa", (2.5, 5.53), 0.0, (2.2, 0.9)), ("table_coffee", (2.5, 4.38), 0.0, (1.2, 0.6)),
        ("bed_double", (6.5, 1.02), 180.0, (1.6, 2.0)),          # head against the south wall (local +Y = south)
        ("table_dining", (6.3, 4.3), 0.0, (1.4, 0.8))])
    decorated, _rows = D.add_decor(b)
    fitted = F.fit_building(decorated, FakeCatalog([FRAME], decor=[RUG, ART]), style_family="scandinavian")
    rugs, arts = of_type(fitted, "rug"), of_type(fitted, "wall_art")
    assert len(rugs) == 2 and len(arts) == 1 and all(r["asset"] for r in rugs) and arts[0]["asset"]
    rugs[1]["asset"] = None                                     # the dining rug: no model -> parametric rug
    bare_art = dict(arts[0], id="dec_L0_099", asset=None)       # wall art without a model: not built
    fitted["decor"].append(bare_art)
    path = tmp / "building.json"
    path.write_text(json.dumps(fitted), encoding="utf-8")
    out = tmp / "scene"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(path), "--style", str(STYLE), "--assets", str(assets),
                                             "--out", str(out), "--no-textures", "--no-preview", "--no-glb"],
                    log_path=out / "build.log")
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    (tmp / "dump.py").write_text(DUMP_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "dump.py", [str(tmp / "dump.json")], blend=str(out / "scene.blend"))
    dump = json.loads((tmp / "dump.json").read_text(encoding="utf-8"))
    return {"building": fitted, "manifest": manifest, "objects": dump, "path": path, "assets": assets, "tmp": tmp}


@needs_blender
def test_scene_manifest_validates_with_rugs_wall_art_and_a_bed_frame(built):
    m = built["manifest"]
    schemas.validate_scene_manifest(m)
    s = m["furniture"]
    assert s["by_method"]["library"] == 1 and not [f for f in s["fallbacks"] if f["type"] == "bed_double"]
    (skipped,) = s["decor_skipped"]
    assert skipped["id"] == "dec_L0_099" and "no library wall art model" in skipped["reason"]
    assert "decor_dec_L0_099" not in built["objects"] and "dec_L0_099" not in m["pass_index"]
    assert not [w for w in m["warnings"] if "deck" in w or "capped at 0.6" in w]


@needs_blender
def test_bed_frame_gets_the_bedding_in_its_inner_box_on_the_deck(built):
    bed = next(f for f in built["building"]["furniture"] if f["type"] == "bed_double")
    fp, asset = bed["footprint"], bed["asset"]
    assert asset["bed_frame"] is True and asset["library"] == "abo"
    m, objects = built["manifest"], built["objects"]
    entry = next(o for o in m["objects"] if o.get("element_id") == bed["id"] and o["kind"] == "furniture")
    ob = objects[f"furn_{bed['id']}"]
    # one piece: the frame and the bedding are one object with the bed's id and pass index
    assert [n for n, o in objects.items() if o["wenart_id"] == bed["id"] and o["kind"] == "furniture"] == [entry["name"]]
    assert ob["pass_index"] == entry["pass_index"] == m["pass_index"][bed["id"]]
    assert entry["method"] == "library" and ob["props"]["wenart_asset"] == FRAME["id"]
    sz = entry["fit_scale"][2]
    deck = 0.30 * sz
    rec = entry["bedding"]
    assert rec["deck_z_m"] == pytest.approx(deck, abs=1e-4) and rec["z_scale"] == pytest.approx(sz, abs=1e-4)
    assert rec["mattress_top_m"] == pytest.approx(deck + 0.20, abs=1e-4)
    assert rec["material_keys"] == {"bedding": "fabric_white", "duvet": "fabric_linen"}
    # The bedding vertices are the parametric parts in the piece frame, placed like the piece.
    parts = P.frame_bedding(fp["size"][0], fp["size"][1], deck)
    want, _faces, _keys = P.world_mesh(parts, fp["center"], fp["rotation_deg"], 0.0)
    got = ob["verts"][-len(want):]
    assert max(abs(a - b) for p, q in zip(got, want) for a, b in zip(p, q)) < 1e-4
    offset = len(ob["verts"]) - len(want)
    mattress = parts[0]
    assert mattress["role"] == "mattress"
    local = [to_local(p, fp) for p in got[:len(mattress["verts"])]]
    (x0, x1), (y0, y1), (z0, z1) = bounds(local)
    assert (x1 - x0, y1 - y0) == pytest.approx((1.6 * 0.92, 2.0 * 0.92), abs=1e-4)           # the inner box
    assert ((x0 + x1) / 2, (y0 + y1) / 2) == pytest.approx((0.0, 0.0), abs=1e-4)
    assert z0 == pytest.approx(deck, abs=1e-4) and z1 == pytest.approx(deck + 0.20, abs=1e-4)  # on the deck
    # the frame's own deck top (0.30 m in the model, scaled) is where the mattress starts
    frame_local = [to_local(p, fp) for p in ob["verts"][:offset]]
    deck_corners = [v for v in frame_local if abs(v[2] - deck) < 1e-4]
    assert len(deck_corners) >= 4 and max(abs(v[0]) for v in deck_corners) < 0.8
    # pillows at the head (local +Y, the headboard side; here the south wall), the duvet from the foot
    pillow_ys = [sum(to_local(p, fp)[1] for p in got[i:i + len(q["verts"])]) / len(q["verts"])
                 for i, q in _part_offsets(parts) if q["role"] == "pillow"]
    assert len(pillow_ys) == 2 and min(pillow_ys) > 0.5
    head_world = [p for p in got if p[2] > deck + 0.15]
    assert sum(p[1] for p in head_world) / len(head_world) < fp["center"][1] + 0.5            # south half
    # bedding faces carry the style materials and are smooth; the frame keeps its own material
    bedding_faces = [f for f in ob["faces"] if min(f["verts"]) >= offset]
    assert {f["material"] for f in bedding_faces} == {"fabric_white", "fabric_linen"}
    assert all(f["smooth"] for f in bedding_faces)
    frame_mats = {f["material"] for f in ob["faces"] if max(f["verts"]) < offset}
    assert frame_mats and all(name.endswith("_mat") for name in frame_mats)          # the model's own materials
    # the manifest records the design detail and a box covering the bedding
    assert "bedding" in entry["assumed"] and entry["bbox_m"][2] >= rec["top_m"] - 1e-6
    detail = next(a for a in m["assumed"] if a.get("parent") == bed["id"] and a["field"] == "bedding")
    assert detail["kind"] == "bedding" and "bed frame" in detail["reason"]
    assert entry["box3d"]["size"][2] == pytest.approx(max(1.0 * sz, rec["top_m"]), abs=1e-3)


def _part_offsets(parts):
    i = 0
    for p in parts:
        yield i, p
        i += len(p["verts"])


@needs_blender
def test_cushions_on_a_bed_frame_rest_on_its_bedding(built):
    """Milestone 12 (docs/milestone12.md §4.7): the cushions rest on the frame's mattress and bedding by rays and lean
    against its pillows or headboard; Milestone 11 put them on the pillow top (``bedding.top_m``)."""
    bed = next(f for f in built["building"]["furniture"] if f["type"] == "bed_double")
    m, objects = built["manifest"], built["objects"]
    rec = next(o for o in m["objects"] if o.get("element_id") == bed["id"] and o["kind"] == "furniture")["bedding"]
    cushions = [o for o in m["objects"] if o["kind"] == "decor" and o.get("host_id") == bed["id"]]
    assert cushions
    for c in cushions:
        assert c["pass_index"] == m["pass_index"][bed["id"]] and c["wenart_id"] == bed["id"]
        low = bounds(objects[c["name"]]["verts"])[2][0]
        assert rec["mattress_top_m"] - 0.03 <= low < rec["top_m"] - 0.05        # on the mattress, not the pillows
        assert c["rest"]["gap_m"] <= 0.010 and c["rest"]["penetration_m"] <= 0.030 and c["support"] == "headboard"


@needs_blender
def test_rugs_lie_flat_on_their_size_with_their_own_pass_index(built):
    m, objects = built["manifest"], built["objects"]
    lib_rug, par_rug = of_type(built["building"], "rug")
    pass_values = list(m["pass_index"].values())
    for item in (lib_rug, par_rug):
        entry = next(o for o in m["objects"] if o["wenart_id"] == item["id"])
        ob = objects[entry["name"]]
        assert entry["kind"] == ob["kind"] == "decor" and entry["type"] == "rug" and entry["host_id"] is None
        assert entry["anchor_ids"] == item["anchor_ids"] and ob["props"]["wenart_anchor"] == ",".join(item["anchor_ids"])
        assert ob["pass_index"] == entry["pass_index"] == m["pass_index"][item["id"]]
        assert pass_values.count(entry["pass_index"]) == 1                                    # its own element
        (x0, x1), (y0, y1), (z0, z1) = bounds(ob["verts"])
        w, d = item["size"]
        assert (x1 - x0, y1 - y0) == pytest.approx((w, d), abs=2e-3)                         # rotation 0 / 180
        assert ((x0 + x1) / 2, (y0 + y1) / 2) == pytest.approx(item["center"], abs=2e-3)
        assert z0 == pytest.approx(0.0, abs=1e-6) and z1 <= F.RUG_MAX_THICKNESS_M + 1e-6
    lib = next(o for o in m["objects"] if o["wenart_id"] == lib_rug["id"])
    par = next(o for o in m["objects"] if o["wenart_id"] == par_rug["id"])
    assert lib["method"] == "library" and lib["asset"]["asset_id"] == RUG["id"]
    assert bounds(objects[lib["name"]]["verts"])[2][1] == pytest.approx(0.01, abs=1e-4)      # the model's 1 cm
    assert par["method"] == "parametric (fallback: no asset in the building JSON)"
    assert bounds(objects[par["name"]]["verts"])[2][1] == pytest.approx(P.RUG_THICKNESS_M, abs=1e-4)
    assert objects[par["name"]]["materials"] == ["fabric_linen"]


@needs_blender
def test_wall_art_hangs_over_the_built_sofa_facing_the_room(built):
    m, objects = built["manifest"], built["objects"]
    art = next(d for d in of_type(built["building"], "wall_art") if d["asset"])
    sofa = next(f for f in built["building"]["furniture"] if f["type"] == "sofa")
    sofa_entry = next(o for o in m["objects"] if o.get("element_id") == sofa["id"] and o["kind"] == "furniture")
    entry = next(o for o in m["objects"] if o["wenart_id"] == art["id"])
    ob = objects[entry["name"]]
    assert entry["kind"] == "decor" and entry["type"] == "wall_art" and entry["host_id"] is None
    assert entry["pass_index"] == m["pass_index"][art["id"]] != m["pass_index"][sofa["id"]]
    (x0, x1), (y0, y1), (z0, z1) = bounds(ob["verts"])
    w, dp, h = art["asset"]["bbox_m"]
    assert x1 - x0 == pytest.approx(w, abs=1e-3) and z1 - z0 == pytest.approx(h, abs=1e-3)
    assert (x0 + x1) / 2 == pytest.approx(art["wall_point"][0], abs=1e-3)                   # centred on the sofa
    assert z0 == pytest.approx(sofa_entry["bbox_m"][2] + D.WALL_ART_GAP_M, abs=1e-4)         # 0.25 m above its top
    assert entry["mount"]["host_top_m"] == pytest.approx(sofa_entry["bbox_m"][2], abs=1e-4)
    # its back on the north wall face (y = 6.0, 5 mm off it), the canvas on the room side
    assert y1 == pytest.approx(6.0 - BF.WALL_ART_WALL_GAP_M, abs=1e-4)
    canvas = [ob["verts"][i] for f in ob["faces"] if f["material"] == "art_canvas_mat" for i in f["verts"]]
    frame = [ob["verts"][i] for f in ob["faces"] if f["material"] == "art_frame_mat" for i in f["verts"]]
    assert canvas and min(p[1] for p in canvas) < min(p[1] for p in frame)
    assert z1 <= 2.7 - BF.WALL_ART_CEILING_M + 1e-6


@needs_blender
def test_views_and_cameras_see_rugs_and_wall_art_as_decor(built):
    m = built["manifest"]
    table = V.index_table(m)
    kinds = {e["wenart_id"]: (e["kind"], e["type"]) for e in table.values()}
    for d in built["building"]["decor"]:
        if d["type"] in ("rug", "wall_art") and d["id"] in m["pass_index"]:
            assert kinds[d["id"]] == ("decor", d["type"])
    furniture_types = {e["type"] for e in table.values() if e["kind"] == "furniture"}
    assert not furniture_types & {"rug", "wall_art"}
    for cam in m["cameras"]:
        assert not set(cam.get("visible_furniture") or []) & {d["id"] for d in built["building"]["decor"]}


@needs_blender
def test_behind_proxies_wall_art_hangs_over_the_proxy_box_and_rugs_stay(built):
    out = built["tmp"] / "scene_proxies"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(built["path"]), "--style", str(STYLE), "--assets",
                                             str(built["assets"]), "--out", str(out), "--no-textures", "--no-preview",
                                             "--no-glb", "--proxies"], log_path=out / "build.log")
    m = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    schemas.validate_scene_manifest(m)
    sofa = next(f for f in built["building"]["furniture"] if f["type"] == "sofa")
    proxy = next(o for o in m["objects"] if o["wenart_id"] == f"proxy:{sofa['id']}")
    art = next(d for d in of_type(built["building"], "wall_art") if d["asset"])
    entry = next(o for o in m["objects"] if o["wenart_id"] == art["id"])
    assert entry["mount"]["host_top_m"] == pytest.approx(proxy["size"][2]) and not [
        w for w in m["warnings"] if "is not built" in w]
    assert {o["type"] for o in m["objects"] if o["kind"] == "decor" and o.get("host_id") is None} >= {"rug", "wall_art"}
    assert not [o for o in m["objects"] if o.get("bedding")]           # no frame built, so no bedding


# --------------------------------------------------------------------------
# The model licence gate of the new sources (pure)
# --------------------------------------------------------------------------

CREDITS = {"title": "Bed", "author": "Amazon.com", "source_url": "https://amazon-berkeley-objects.s3.amazonaws.com/index.html",
           "licence_url": "https://creativecommons.org/licenses/by/4.0/", "via": "Amazon Berkeley Objects",
           "attribution": '"Bed" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0)'}


def _asset(library, licence, **extra):
    return dict({"library": library, "asset_id": f"{library}_x", "licence": licence, "method": "library",
                 "uid": "x", "glb": f"models/{library}/x.glb"}, **extra)


def test_model_licence_gate_takes_abo_generated_and_flagged_models():
    assert BF.licence_refusal(_asset("abo", "CC-BY-4.0", **CREDITS)) is None
    assert "no credit line" in BF.licence_refusal(_asset("abo", "CC-BY-4.0", **dict(CREDITS, attribution="")))
    assert "is not CC-BY-4.0" in BF.licence_refusal(_asset("abo", "CC0"))
    assert BF.licence_refusal(_asset("generated", "generated (TRELLIS.2-4B, MIT)")) is None
    assert "does not say so" in BF.licence_refusal(_asset("generated", "MIT"))
    # Objaverse: another licence passes when the catalogue flagged it (credit line still needed for CC BY-*)
    nc = _asset("objaverse", "CC-BY-NC-4.0", licence_flag="non_commercial", **CREDITS)
    assert BF.licence_refusal(nc) is None
    assert "no credit line" in BF.licence_refusal(dict(nc, author=""))
    assert BF.licence_refusal(_asset("objaverse", "proprietary", licence_flag="unknown")) is None
    assert "is not CC0 or CC-BY-4.0" in BF.licence_refusal(_asset("objaverse", "CC-BY-NC-4.0"))
    assert "is not CC0 or CC-BY-4.0" in BF.licence_refusal(_asset("objaverse", "CC-BY-NC-4.0", licence_flag="maybe"))
    # the flag never opens Poly Haven or ABO to another licence
    assert "not CC0" in BF.licence_refusal(_asset("polyhaven", "CC-BY-4.0", licence_flag="unknown"))
    assert "is not CC-BY-4.0" in BF.licence_refusal(_asset("abo", "CC-BY-NC-4.0", licence_flag="non_commercial"))


def test_glbs_of_every_source_resolve_in_their_cache(tmp_path):
    for source in ("abo", "generated"):
        glb = tmp_path / "models" / source / "x.glb"
        glb.parent.mkdir(parents=True, exist_ok=True)
        glb.write_bytes(b"glTF")
        licence = "CC-BY-4.0" if source == "abo" else "generated (TRELLIS.2-4B, MIT)"
        asset = _asset(source, licence, **CREDITS)
        assert BF.resolve_asset(asset, str(tmp_path)) == (glb, None)
        by_uid = {k: v for k, v in asset.items() if k != "glb"}
        assert BF.resolve_asset(by_uid, str(tmp_path)) == (glb, None)


def test_frame_bedding_plan_and_wall_art_placement_are_pure():
    plan = BF.frame_bedding_plan({"bed_frame": True, "deck_height_m": 0.3}, {"size": [1.6, 2.0]}, 0.9)
    assert plan["record"]["deck_z_m"] == pytest.approx(0.27) and plan["record"]["mattress_top_m"] == pytest.approx(0.47)
    for bad in ({}, {"bed_frame": True}, {"bed_frame": True, "deck_height_m": -1}, {"deck_height_m": 0.3}):
        assert BF.frame_bedding_plan(bad, {"size": [1.6, 2.0]}, 1.0) is None
    item = {"wall_point": [3.0, 5.0], "rotation_deg": 0.0, "gap_m": 0.25, "bottom_m": 1.1}
    fp, rec = BF.wall_art_placement(item, [1.0, 0.04, 0.8], 0.85, 2.7)
    assert fp["center"] == pytest.approx([3.0, 5.0 - 0.02 - BF.WALL_ART_WALL_GAP_M])
    assert rec["bottom_m"] == pytest.approx(1.1) and rec["top_m"] == pytest.approx(1.9) and rec["scale"] == 1.0
    # too tall for the room left under the ceiling: scaled down uniformly
    fp, rec = BF.wall_art_placement(item, [1.0, 0.04, 1.6], 0.85, 2.7)
    assert rec["top_m"] == pytest.approx(2.6) and rec["box_m"][0] == pytest.approx(1.0 * 1.5 / 1.6, abs=1e-4)
    # no room at all: refused with the reason
    fp, rec = BF.wall_art_placement(item, [1.0, 0.04, 1.6], 2.2, 2.7)
    assert fp is None and "narrower than" in rec["reason"]
    # the piece not built: the item's bottom_m
    fp, rec = BF.wall_art_placement(item, [1.0, 0.04, 0.8], None, 2.7)
    assert rec["bottom_m"] == 1.1 and rec["host_top_m"] is None
