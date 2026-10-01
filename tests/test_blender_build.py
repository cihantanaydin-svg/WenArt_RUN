"""CPU tests that run Blender: scene build for synthetic-01 L0 (with a tiny
fake texture set) and synthetic-03 L0 (flat colours, unverified piece), the
custom properties of every object, boolean holes (door rays), proxies,
cameras, manifests, and one 320x180 / 16-sample Cycles render.

Skipped with a reason when no Blender binary is found (WENART_BLENDER,
/workspace/tools/blender/blender, /opt/wenart/blender/blender, PATH).
"""
import json
import subprocess
import textwrap
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from wenart import geometry as G
from wenart.blender import cli, schemas
from wenart.ingest.pipeline import build_project

ROOT = Path(__file__).resolve().parents[1]
STYLE = ROOT / "tests" / "fixtures" / "blender_style.json"
BLENDER = cli.find_blender()
pytestmark = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER, /workspace/tools/blender, "
                                                        "/opt/wenart/blender, PATH)")

DUMP_SCRIPT = textwrap.dedent("""
    import bpy, json, sys
    out = sys.argv[sys.argv.index("--") + 1]
    rows = []
    for ob in bpy.data.objects:
        rows.append({"name": ob.name, "type": ob.type, "wenart_id": ob.get("wenart_id"),
                     "kind": ob.get("wenart_kind"), "status": ob.get("wenart_status"),
                     "pass_index": ob.pass_index, "uv": [l.name for l in ob.data.uv_layers] if ob.type == "MESH" else [],
                     "materials": [m.name if m else None for m in ob.data.materials] if ob.type == "MESH" else [],
                     "verts": len(ob.data.vertices) if ob.type == "MESH" else 0})
    json.dump(rows, open(out, "w"))
""")


def _fake_assets(root: Path) -> Path:
    """A 16x16 texture set for WoodFloor051 so the textured path is exercised."""
    tex = root / "textures" / "WoodFloor051"
    tex.mkdir(parents=True)
    Image.new("RGB", (16, 16), (150, 110, 70)).save(tex / "albedo.png")
    Image.new("RGB", (16, 16), (128, 128, 255)).save(tex / "normal.png")
    Image.new("L", (16, 16), 120).save(tex / "roughness.png")
    manifest = {"textures": {"WoodFloor051": {
        "id": "WoodFloor051", "source": "ambientcg", "licence": "CC0", "size_m": [1.0, 1.0],
        "files": {"albedo": "textures/WoodFloor051/albedo.png", "normal": "textures/WoodFloor051/normal.png",
                  "roughness": "textures/WoodFloor051/roughness.png"}}}, "hdris": {}}
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return root


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    """synthetic-01 L0 from the pipeline output, built with the fake texture set."""
    tmp = tmp_path_factory.mktemp("blender01")
    building = build_project(ROOT / "projects" / "synthetic-01", tmp / "pipeline")
    assert building["status"] == "ok"
    assets = _fake_assets(tmp / "assets")
    out = tmp / "scene"
    cli.build(tmp / "pipeline" / "building.json", out, style=STYLE, assets=assets, level="L0", preview_samples=4)
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    # Reopen scene.blend in Blender and dump what every object really carries.
    dump = tmp / "objects.json"
    (tmp / "dump.py").write_text(DUMP_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "dump.py", [str(dump)], blend=str(out / "scene.blend"))
    objects = json.loads(dump.read_text(encoding="utf-8"))
    return {"building": building, "out": out, "manifest": manifest, "objects": objects, "tmp": tmp}


def test_manifest_validates_and_files_exist(built):
    schemas.validate_scene_manifest(built["manifest"])
    out = built["out"]
    assert (out / "scene.blend").stat().st_size > 10_000
    assert (out / "scene.glb").stat().st_size > 1_000
    assert built["manifest"]["files"].get("glb") == "scene.glb"
    assert built["manifest"]["blender_version"].startswith("5.")


def test_object_counts_per_kind_match_the_json(built):
    b, m = built["building"], built["manifest"]
    walls = [w for w in b["walls"] if w["level_id"] == "L0"]
    doors = [o for o in b["openings"] if o["level_id"] == "L0" and o["type"] == "door"]
    windows = [o for o in b["openings"] if o["level_id"] == "L0" and o["type"] == "window"]
    rooms = [r for r in b["rooms"] if r["level_id"] == "L0"]
    furniture = [f for f in b["furniture"] if f["level_id"] == "L0"]
    ids = {}
    for o in m["objects"]:
        ids.setdefault(o["kind"], set()).add(o["wenart_id"])
    assert ids["wall"] == {w["id"] for w in walls}
    assert ids["door"] == {o["id"] for o in doors}
    assert ids["window"] == {o["id"] for o in windows}
    assert ids["floor"] == ids["ceiling"] == {r["id"] for r in rooms}
    assert ids["furniture_proxy"] == {f"proxy:{f['id']}" for f in furniture}
    assert len(ids["camera"]) == 3 * len(rooms)
    # Nothing beyond the JSON: every element-bound object carries the element's evidence.
    for o in m["objects"]:
        if o["kind"] in ("wall", "door", "window", "floor", "ceiling", "furniture_proxy"):
            assert o["evidence"], o["name"]
            assert o["evidence"][0]["method"] in ("vector", "ocr", "ai", "derived")


def test_every_blender_object_has_the_custom_properties(built):
    kinds = {"wall", "floor", "ceiling", "door", "window", "opening", "furniture_proxy", "camera", "light"}
    by_name = {o["name"]: o for o in built["manifest"]["objects"]}
    assert built["objects"], "no objects in scene.blend"
    for ob in built["objects"]:
        assert ob["wenart_id"], ob["name"]
        assert ob["kind"] in kinds, ob
        assert ob["status"] in ("verified", "unverified", "assumed"), ob
        assert ob["name"] in by_name, f"{ob['name']} not in the manifest"
        assert by_name[ob["name"]]["wenart_id"] == ob["wenart_id"]
        if ob["type"] == "MESH":
            assert "box_m" in ob["uv"], ob["name"]
            assert ob["verts"] > 0
    assert not [o["name"] for o in built["objects"] if o["name"].startswith("cut_")], "cutters must be deleted"
    assert not [o["name"] for o in built["objects"] if o["name"] == "top_preview"], "preview camera must be deleted"


def test_door_rays_hit_no_wall(built):
    rays = built["manifest"]["checks"]["door_rays"]
    doors = [o for o in built["building"]["openings"] if o["level_id"] == "L0" and o["type"] == "door"]
    assert {r["opening_id"] for r in rays} == {d["id"] for d in doors}
    for r in rays:
        assert r["hit_kind"] != "wall", r
        assert r["hit_kind"] == "door", "the closed leaf should be hit"  # leaf sits in the opening


def test_pass_indices_unique_for_proxies_and_openings(built):
    m = built["manifest"]
    table = m["pass_index"]
    assert len(set(table.values())) == len(table) and min(table.values()) == 1
    furniture = [f for f in built["building"]["furniture"] if f["level_id"] == "L0"]
    assert all(f"proxy:{f['id']}" in table for f in furniture)
    for ob in built["objects"]:
        if ob["kind"] in ("furniture_proxy", "door", "window"):
            assert ob["pass_index"] == table[ob["wenart_id"]], ob


def test_proxies_keep_footprint_size_rotation_and_height(built):
    m = built["manifest"]
    furniture = {f["id"]: f for f in built["building"]["furniture"]}
    proxies = [o for o in m["objects"] if o["kind"] == "furniture_proxy"]
    for o in proxies:
        f = furniture[o["element_id"]]
        fp = f["footprint"]
        assert o["center"][:2] == pytest.approx(fp["center"])
        assert o["size"][:2] == pytest.approx(fp["size"])
        assert o["rotation_deg"] == pytest.approx(fp["rotation_deg"])
        assert o["front_deg"] == f["front_deg"]
        assert o["assumed"].get("height") == o["size"][2]  # no height in the JSON -> table value, assumed
        assert o["material"] in ("proxy", "proxy_glass", "proxy_unverified")
    shower = next(o for o in proxies if o["type"] == "shower")
    assert shower["material"] == "proxy_glass" and shower["size"][2] == 2.0


def test_materials_textured_or_flat_are_recorded(built):
    mats = built["manifest"]["materials"]
    floor = mats["wood_oak_light__WoodFloor051"]
    assert floor["textured"] is True and floor["asset"] == "WoodFloor051" and floor["slug"] == "wood_oak_light"
    # the fake albedo (150,110,70) is 0.18 linear luminance, darker than light oak (0.47): gain ~2.6
    assert 2.0 < floor["albedo_gain"] <= 4.0 and 0.1 < floor["albedo_mean_luminance"] < 0.3
    assert mats["wood_oak_light"]["albedo_gain"] is None  # flat materials carry no gain
    assert mats["wood_oak_light"]["textured"] is False  # the door leaf: no asset in the style
    walls = next(m for m in mats.values() if m["slug"] == "plaster_white" and m["tint"])
    assert walls["textured"] is False and "Plaster001" in walls["reason"]
    floors = [o for o in built["manifest"]["objects"] if o["kind"] == "floor"]
    assert all(o["textured"] and o["material"] == "wood_oak_light__WoodFloor051" for o in floors if not o["wet"])
    assert all(o["material"].startswith("tiles_light") and not o["textured"] for o in floors if o["wet"])
    for o in built["objects"]:
        assert None not in o["materials"], f"{o['name']} has an empty material slot"
    assert built["manifest"]["lighting"]["world"]["kind"] == "sky"  # no HDRI in the fake manifest


def test_cameras_inside_rooms_and_in_the_blend(built):
    m = built["manifest"]
    rooms = {r["id"]: r for r in built["building"]["rooms"]}
    names = {o["name"] for o in built["objects"] if o["type"] == "CAMERA"}
    for cam in m["cameras"]:
        assert cam["name"] in names
        assert G.point_in_polygon(cam["position"][:2], rooms[cam["room_id"]]["polygon"])
        assert cam["position"][2] == pytest.approx(1.4)


def test_top_down_preview_is_100_px_per_metre(built):
    png = built["out"] / built["manifest"]["previews"]["L0"]
    im = Image.open(png)
    # Outer footprint 9.6 x 7.2 m plus 0.5 m margin on every side.
    assert im.size == (1060, 820)
    arr = np.asarray(im.convert("L"))
    assert arr.std() > 10, "preview looks empty"


def test_assumed_defaults_are_listed(built):
    assumed = built["manifest"]["assumed"]
    fields = {(a["object"], a["field"]) for a in assumed}
    assert ("d_L0_001", "height") in fields
    assert ("win_L0_001", "sill_height") in fields and ("win_L0_001", "height") in fields
    assert ("w_L0_001", "slab_thickness") in fields
    assert ("level_L0", "ceiling_height") in fields
    assert ("light_r_L0_hol", "area_light") in fields  # hall has no window


@pytest.fixture(scope="module")
def rendered(built):
    out = built["tmp"] / "renders"
    cli.render(built["out"] / "scene.blend", out, cameras="cam_r_L0_salon_3", samples=16, res="320x180",
               device="cpu")
    return out, json.loads((out / "render_manifest.json").read_text(encoding="utf-8"))


def test_cpu_render_files_and_passes(built, rendered):
    out, manifest = rendered
    schemas.validate_render_manifest(manifest)
    assert manifest["device"] == "CPU" and manifest["samples"] == 16 and manifest["resolution"] == [320, 180]
    entry = manifest["renders"][0]
    assert entry["camera"] == "cam_r_L0_salon_3" and not entry["skipped"]
    assert Image.open(out / entry["png"]).size == (320, 180)
    assert (out / entry["exr"]).stat().st_size > 1_000
    assert (out / entry["preview"]).stat().st_size <= 300_000
    depth = entry["depth"]
    assert 0.3 < depth["min"] < depth["max"] < 30.0 and depth["coverage"] > 0.9
    cam = next(c for c in built["manifest"]["cameras"] if c["name"] == "cam_r_L0_salon_3")
    expected = {built["manifest"]["pass_index"][f"proxy:{f}"] for f in cam["visible_furniture"]}
    assert expected and expected <= set(entry["index_values"])
    index_png = np.asarray(Image.open(out / entry["index_png"]))
    assert expected <= set(np.unique(index_png).tolist())
    depth_png = np.asarray(Image.open(out / entry["depth_png"]))
    assert depth_png.dtype == np.uint16 and depth_png.min() < depth_png.max()


def test_render_is_idempotent(built, rendered):
    out, _ = rendered
    cli.render(built["out"] / "scene.blend", out, cameras="cam_r_L0_salon_3", samples=16, res="320x180", device="cpu")
    manifest = json.loads((out / "render_manifest.json").read_text(encoding="utf-8"))
    assert manifest["renders"][0]["skipped"] is True
    assert manifest["renders"][0]["depth"]["min"] > 0  # stats carried over from the first run


def test_render_script_failure_is_reported(built):
    with pytest.raises(RuntimeError, match="unknown cameras|exited with"):
        cli.render(built["out"] / "scene.blend", built["tmp"] / "bad", cameras="cam_nope", samples=1, res="32x18",
                   device="cpu")


def test_synthetic_03_unverified_piece_and_three_levels(tmp_path):
    building = build_project(ROOT / "projects" / "synthetic-03", tmp_path / "pipeline")
    assert building["status"] == "ok" and "f_L0_021" in building["unverified"]
    out = tmp_path / "scene"
    proc = subprocess.run(
        [BLENDER, "-b", "--python-exit-code", "1", "--python", str(ROOT / "wenart" / "blender" / "build.py"), "--",
         "--building", str(tmp_path / "pipeline" / "building.json"), "--out", str(out), "--level", "L0",
         "--no-textures", "--no-preview", "--no-glb"],
        capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    schemas.validate_scene_manifest(manifest)
    unknown = next(o for o in manifest["objects"] if o["wenart_id"] == "proxy:f_L0_021")
    assert unknown["status"] == "unverified" and unknown["material"] == "proxy_unverified"
    assert all(m["textured"] is False for m in manifest["materials"].values())
    assert all(r["hit_kind"] != "wall" for r in manifest["checks"]["door_rays"])
    # Stove and sink drawn on the counter: lifted so the top faces do not coincide.
    lifted = [a for a in manifest["assumed"] if a["field"] == "height_lift"]
    assert lifted
    assert manifest["previews"] == {}


def test_needs_review_building_is_refused(tmp_path):
    building = {"schema_version": "0.1", "status": "needs_review", "project": {"id": "x"}, "levels": [],
                "walls": [], "openings": [], "rooms": [], "furniture": [], "warnings": []}
    (tmp_path / "building.json").write_text(json.dumps(building))
    proc = subprocess.run(
        [BLENDER, "-b", "--python-exit-code", "1", "--python", str(ROOT / "wenart" / "blender" / "build.py"), "--",
         "--building", str(tmp_path / "building.json"), "--out", str(tmp_path / "scene"), "--no-preview"],
        capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert proc.returncode == 2 and "needs review" in proc.stdout
