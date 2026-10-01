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
from wenart.blender import cli, schemas, shell
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
    # Floors: one per room plus one threshold per door (kind floor, bound to the door).
    assert ids["floor"] == {r["id"] for r in rooms} | {o["id"] for o in doors}
    assert ids["ceiling"] == {r["id"] for r in rooms}
    # Milestone 4: furniture objects (kind furniture, wenart_id = piece id) replace the proxies;
    # synthetic-01 has no ``unknown`` piece, so no proxy box is left.
    assert ids["furniture"] == {f["id"] for f in furniture} and "furniture_proxy" not in ids
    assert len(ids["camera"]) == 3 * len(rooms)
    # Nothing beyond the JSON: every element-bound object carries the element's evidence.
    for o in m["objects"]:
        if o["kind"] in ("wall", "door", "window", "floor", "ceiling", "furniture_proxy", "furniture"):
            assert o["evidence"], o["name"]
            assert o["evidence"][0]["method"] in ("vector", "ocr", "ai", "derived")


def test_every_blender_object_has_the_custom_properties(built):
    kinds = {"wall", "floor", "ceiling", "door", "window", "opening", "furniture_proxy", "furniture", "decor",
             "camera", "light"}
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
        # Door parts are stepped over, so the ray tests the wall: it must pass through.
        assert r["hit"] is False and r["hit_kind"] is None and r["hit_object"] is None, r
        assert f"{r['opening_id']}_leaf" in r["passed"], r  # the closed leaf sits in the opening
    assert not [w for w in built["manifest"]["warnings"] if "door ray" in w]


def test_threshold_floor_under_every_door(built):
    """The room floors stop at the wall faces and the cutter removes the wall
    bottom: a threshold face with the adjacent floor's material fills the gap."""
    objects = built["manifest"]["objects"]
    doors = [o for o in built["building"]["openings"] if o["level_id"] == "L0" and o["type"] == "door"]
    thresholds = {o["wenart_id"]: o for o in objects if o["name"].endswith("_threshold")}
    assert set(thresholds) == {d["id"] for d in doors}
    floors = {o["wenart_id"]: o for o in objects if o["kind"] == "floor" and not o["name"].endswith("_threshold")}
    by_name = {o["name"] for o in built["objects"]}
    for door in doors:
        t = thresholds[door["id"]]
        assert t["kind"] == "floor" and t["name"] == f"{door['id']}_threshold" and t["name"] in by_name
        assert t["evidence"] == door["evidence"] and t["element_id"] == door["id"]
        assert t["room_id"] in floors and t["material"] == floors[t["room_id"]]["material"]
        assert t["lifted"] == 0.0  # lowest level: nothing stacked below


def test_pass_indices_unique_for_proxies_and_openings(built):
    m = built["manifest"]
    table = m["pass_index"]
    assert len(set(table.values())) == len(table) and min(table.values()) == 1
    furniture = [f for f in built["building"]["furniture"] if f["level_id"] == "L0"]
    assert all(f["id"] in table for f in furniture)   # Milestone 4: one index per piece, keyed by its id
    for ob in built["objects"]:
        if ob["kind"] in ("furniture_proxy", "furniture", "door", "window"):
            assert ob["pass_index"] == table[ob["wenart_id"]], ob


def test_proxies_keep_footprint_size_rotation_and_height(built):
    # Milestone 4: the furniture objects keep every proxy field of Milestone 3.
    m = built["manifest"]
    furniture = {f["id"]: f for f in built["building"]["furniture"]}
    proxies = [o for o in m["objects"] if o["kind"] in ("furniture_proxy", "furniture")]
    assert len(proxies) == len([f for f in furniture.values() if f["level_id"] == "L0"])
    for o in proxies:
        f = furniture[o["element_id"]]
        fp = f["footprint"]
        assert o["center"][:2] == pytest.approx(fp["center"])
        assert o["size"][:2] == pytest.approx(fp["size"])
        assert o["rotation_deg"] == pytest.approx(fp["rotation_deg"])
        assert o["front_deg"] == f["front_deg"]
        assert o["assumed"].get("height") == o["size"][2]  # no height in the JSON -> table value, assumed
        assert o["material"] in m["materials"]  # a style material (parametric mesh) or a proxy look
    shower = next(o for o in proxies if o["type"] == "shower")
    assert "thin_glass" in shower["materials"] and shower["size"][2] == 2.0


def test_materials_textured_or_flat_are_recorded(built):
    mats = built["manifest"]["materials"]
    floor = mats["wood_oak_light__WoodFloor051"]
    assert floor["textured"] is True and floor["asset"] == "WoodFloor051" and floor["slug"] == "wood_oak_light"
    # the fake albedo (150,110,70) is 0.18 linear luminance, darker than light oak (0.47): gain ~2.6
    assert 2.0 < floor["albedo_gain"] <= 4.0 and 0.1 < floor["albedo_mean_luminance"] < 0.3
    assert mats["wood_oak_light"]["albedo_gain"] is None  # flat materials carry no gain
    assert mats["wood_oak_light"]["textured"] is False  # the door leaf: no asset in the style
    walls = next(m for m in mats.values() if m["slug"] == "plaster_white" and m["tint"])
    assert walls["textured"] is False and "white_plaster_02" in walls["reason"]  # not in the fake manifest
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
    expected = {built["manifest"]["pass_index"][f] for f in cam["visible_furniture"]}
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


PROBE_SCRIPT = textwrap.dedent("""
    import bpy, json, sys
    from mathutils import Vector
    spec = json.load(open(sys.argv[sys.argv.index("--") + 1]))
    depsgraph = bpy.context.evaluated_depsgraph_get()
    scene = bpy.context.scene
    out = {"rays": {}, "bounds": {}}
    for name, ray in spec["rays"].items():
        hit, loc, _n, _i, ob, _m = scene.ray_cast(depsgraph, Vector(ray["origin"]), Vector(ray["direction"]),
                                                  distance=ray["distance"])
        out["rays"][name] = {"hit": bool(hit), "object": ob.name if hit else None,
                             "kind": ob.get("wenart_kind") if hit else None, "location": list(loc) if hit else None}
    for name in spec["bounds"]:
        ob = bpy.data.objects[name]
        pts = [ob.matrix_world @ v.co for v in ob.data.vertices]
        out["bounds"][name] = [[min(p[i] for p in pts), max(p[i] for p in pts)] for i in range(3)]
    json.dump(out, open(spec["out"], "w"))
""")


@pytest.fixture(scope="module")
def built_variant(tmp_path_factory):
    """synthetic-01 with hand-edited openings, both levels, flat colours:
    two L0 doors moved off the wall centre line (a door block drawn on the
    wall face, which the ingest accepts) and the L1 door d_L1_001 turned into
    a plain opening without a height on the top level."""
    tmp = tmp_path_factory.mktemp("blender01_variant")
    building = build_project(ROOT / "projects" / "synthetic-01", tmp / "pipeline")
    assert building["status"] == "ok"
    openings = {o["id"]: o for o in building["openings"]}
    openings["d_L0_001"]["center"] = [6.15, 7.195]   # w_L0_003 (0.25 m, centre y 7.075): 0.12 m, on the face
    openings["d_L0_003"]["center"] = [5.36, 6.1]     # w_L0_005 (0.10 m, centre x 5.3): 0.06 m, past the face
    openings["d_L1_001"].update({"type": "opening", "height": None, "sill_height": None})
    path = tmp / "building.json"
    path.write_text(json.dumps(building), encoding="utf-8")
    out = tmp / "scene"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(path), "--style", str(STYLE), "--out", str(out),
                                             "--no-textures", "--no-preview", "--no-glb"])
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    schemas.validate_scene_manifest(manifest)
    return {"building": building, "out": out, "manifest": manifest, "tmp": tmp}


def _probe(variant, rays: dict, bounds: list) -> dict:
    """Ray casts and world bounds evaluated inside Blender on the variant scene."""
    tmp = variant["tmp"]
    spec = tmp / f"probe_{len(list(tmp.glob('probe_*.json')))}.json"
    result = spec.with_suffix(".out.json")
    spec.write_text(json.dumps({"rays": rays, "bounds": bounds, "out": str(result)}), encoding="utf-8")
    (tmp / "probe.py").write_text(PROBE_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp / "probe.py", [str(spec)], blend=str(variant["out"] / "scene.blend"))
    return json.loads(result.read_text(encoding="utf-8"))


def test_off_centre_door_is_cut_through_and_recorded(built_variant):
    m = built_variant["manifest"]
    rays = {r["opening_id"]: r for r in m["checks"]["door_rays"]}
    for door in ("d_L0_001", "d_L0_003"):
        assert rays[door]["hit"] is False and rays[door]["hit_kind"] is None, rays[door]
        assert f"{door}_leaf" in rays[door]["passed"]
    assert not [w for w in m["warnings"] if "door ray" in w]
    # The shift is recorded (assumed above 1 mm, warning above half the thickness), never applied silently.
    shifts = {a["object"]: a["value"] for a in m["assumed"] if a["field"] == "center_shift"}
    assert shifts == {"d_L0_001": pytest.approx(0.12), "d_L0_003": pytest.approx(0.06)}
    assert [w for w in m["warnings"] if w.startswith("d_L0_003:") and "half its thickness" in w]
    assert not [w for w in m["warnings"] if w.startswith("d_L0_001:")]
    entries = {o["name"]: o for o in m["objects"]}
    assert entries["d_L0_001_leaf"]["center_shift"] == pytest.approx(0.12)
    assert entries["d_L0_002_leaf"]["center_shift"] == 0.0
    # Wall-only rays from both sides pass through the moved doors; the leaf and frame sit inside the wall.
    probe = _probe(built_variant, {
        "d1_from_hall": {"origin": [6.15, 6.5, 1.0], "direction": [0, 1, 0], "distance": 1.2},
        "d1_from_outside": {"origin": [6.15, 7.7, 1.0], "direction": [0, -1, 0], "distance": 1.2},
        "d3_from_salon": {"origin": [4.8, 6.1, 1.0], "direction": [1, 0, 0], "distance": 1.0},
    }, ["d_L0_001_leaf", "d_L0_001_frame", "d_L0_003_leaf", "w_L0_003"])
    for name, r in probe["rays"].items():
        assert r["kind"] in (None, "door"), (name, r)  # nothing but the door parts on the way
    for name in ("d_L0_001_leaf", "d_L0_001_frame"):
        y0, y1 = probe["bounds"][name][1]
        assert 6.95 - 1e-6 <= y0 and y1 <= 7.2 + 1e-6, (name, probe["bounds"][name])
    x0, x1 = probe["bounds"]["d_L0_003_leaf"][0]
    assert 5.25 - 1e-6 <= x0 and x1 <= 5.35 + 1e-6


def test_downward_ray_in_a_door_hits_the_threshold_floor(built_variant):
    building = built_variant["building"]
    walls = {w["id"]: w for w in building["walls"]}
    rays = {}
    for o in building["openings"]:
        if o["type"] not in ("door", "opening"):
            continue
        wall = walls[o["wall_id"]]
        cx, cy, _ = shell.opening_centre_on_wall(o, wall)
        nx, ny = G.unit_normal_left(wall["start"], wall["end"])
        z = {"L0": 0.0, "L1": 3.0}[o["level_id"]] + 0.5
        for side in (1, -1):  # beside the closed leaf, inside the wall footprint
            d = side * (wall["thickness"] / 2.0 - 0.01)
            rays[f"{o['id']}_{side}"] = {"origin": [cx + nx * d, cy + ny * d, z], "direction": [0, 0, -1],
                                        "distance": 1.0}
    probe = _probe(built_variant, rays, [])
    for name, r in probe["rays"].items():
        opening_id = name.rsplit("_", 1)[0]
        assert r["kind"] == "floor" and r["object"] == f"{opening_id}_threshold", (name, r)


def test_plain_opening_runs_to_the_ceiling_with_a_soffit(built_variant):
    m = built_variant["manifest"]
    entries = {o["name"]: o for o in m["objects"]}
    assert entries["d_L1_001"]["kind"] == "opening" and not entries["d_L1_001"]["has_geometry"]
    assert entries["d_L1_001"]["assumed"]["height"] == pytest.approx(2.7)
    assert "d_L1_001_frame" not in entries and "d_L1_001_leaf" not in entries
    assert entries["d_L1_001_soffit"]["kind"] == "ceiling" and entries["d_L1_001_threshold"]["kind"] == "floor"
    assert entries["d_L1_001_threshold"]["lifted"] == pytest.approx(0.001)  # L0 lies below
    ray = {r["opening_id"]: r for r in m["checks"]["door_rays"]}["d_L1_001"]
    assert ray["hit"] is False and ray["passed"] == []
    # L1: floor 3.0, ceiling 5.7, wall w_L1_005 at x 4.25..4.35, opening 0.9 wide at y 2.0.
    probe = _probe(built_variant, {
        "just_below_ceiling": {"origin": [3.9, 2.0, 5.6995], "direction": [1, 0, 0], "distance": 0.8},
        "up_inside_opening": {"origin": [4.3, 2.0, 4.0], "direction": [0, 0, 1], "distance": 3.0},
        "up_beside_opening": {"origin": [4.3, 1.4, 4.0], "direction": [0, 0, 1], "distance": 3.0},
    }, ["w_L1_005"])
    assert probe["rays"]["just_below_ceiling"]["hit"] is False, probe["rays"]["just_below_ceiling"]
    soffit = probe["rays"]["up_inside_opening"]
    assert soffit["object"] == "d_L1_001_soffit" and soffit["kind"] == "ceiling"
    assert soffit["location"][2] == pytest.approx(5.7, abs=1e-4)
    assert probe["rays"]["up_beside_opening"]["object"] == "w_L1_005"  # the wall head stays closed elsewhere


def test_needs_review_building_is_refused(tmp_path):
    building = {"schema_version": "0.1", "status": "needs_review", "project": {"id": "x"}, "levels": [],
                "walls": [], "openings": [], "rooms": [], "furniture": [], "warnings": []}
    (tmp_path / "building.json").write_text(json.dumps(building))
    proc = subprocess.run(
        [BLENDER, "-b", "--python-exit-code", "1", "--python", str(ROOT / "wenart" / "blender" / "build.py"), "--",
         "--building", str(tmp_path / "building.json"), "--out", str(tmp_path / "scene"), "--no-preview"],
        capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert proc.returncode == 2 and "needs review" in proc.stdout
