"""CC0 furniture models (wenart/assets/models.py, Milestone 4 section 1).

Offline: the file-table parser, the glTF bounding-box measurement on a
hand-written glTF (node transforms, Y-up to Z-up), the manifest ``models``
section with its licence refusal, the CLI wiring. Live (skipped only when
the network itself is unreachable): every catalogue id exists on the Poly
Haven model listing (one call, no download) and ArmChair_01 (1k, well under
20 MB) is downloaded into ``assets/`` (git-ignored, cached) and its measured
box matches the catalogue within 1 cm.
"""
import base64
import json
import math
import struct
from pathlib import Path

import pytest

from wenart.assets import fetch, models, web
from wenart.assets.__main__ import main as assets_main
from wenart.furniture import catalog as C

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
TEST_MODEL = "ArmChair_01"   # 1k glTF set ~0.8 MB


def network_or_skip(call, *args, **kwargs):
    try:
        return call(*args, **kwargs)
    except web.NetworkError as exc:
        pytest.skip(f"network unavailable: {exc}")


# --------------------------------------------------------------------------
# File table (offline, shape copied from the real /files/sofa_02 response)
# --------------------------------------------------------------------------

FILE_TABLE = {"gltf": {"1k": {"gltf": {
    "url": "https://dl.polyhaven.org/file/ph-assets/Models/gltf/1k/sofa_02/sofa_02_1k.gltf", "size": 4183,
    "md5": "ec2590dc8433a523d0fe9e507766c16f",
    "include": {"textures/sofa_02_diff_1k.jpg": {"size": 86514, "url": "u/diff.jpg", "md5": "a"},
                "sofa_02.bin": {"size": 74864, "url": "u/sofa_02.bin", "md5": "b"}}}}},
    "blend": {}, "Diffuse": {}}


def test_model_gltf_parser():
    item = models.model_gltf(FILE_TABLE, size="1k")
    assert item["url"].endswith("sofa_02_1k.gltf") and item["md5"] == "ec2590dc8433a523d0fe9e507766c16f"
    assert set(item["include"]) == {"textures/sofa_02_diff_1k.jpg", "sofa_02.bin"}
    with pytest.raises(KeyError, match="gltf/2k"):
        models.model_gltf(FILE_TABLE, size="2k")
    with pytest.raises(KeyError):
        models.model_gltf({}, size="1k")
    assert models.gltf_relpath("sofa_02") == "models/sofa_02/sofa_02_1k.gltf"


# --------------------------------------------------------------------------
# Bounding box from the glTF accessors (offline, hand-written glTF)
# --------------------------------------------------------------------------

def _box_gltf(path: Path, size, *, translation=None, rotation=None, parent_scale=None, data_uri=True) -> Path:
    """A glTF with one box mesh of ``size`` (glTF frame, Y-up) under a node with a transform."""
    sx, sy, sz = size
    path.parent.mkdir(parents=True, exist_ok=True)
    verts = [(x * sx / 2, y * sy / 2, z * sz / 2) for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)]
    blob = b"".join(struct.pack("<fff", *v) for v in verts)
    mins = [min(v[i] for v in verts) for i in range(3)]
    maxs = [max(v[i] for v in verts) for i in range(3)]
    node = {"mesh": 0}
    if translation:
        node["translation"] = translation
    if rotation:
        node["rotation"] = rotation
    nodes = [node]
    root = 0
    if parent_scale:
        nodes.append({"children": [0], "scale": parent_scale})
        root = 1
    gltf = {
        "asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [root]}], "nodes": nodes,
        "meshes": [{"primitives": [{"attributes": {"POSITION": 0}}]}],
        "accessors": [{"bufferView": 0, "componentType": 5126, "count": 8, "type": "VEC3", "min": mins, "max": maxs}],
        "bufferViews": [{"buffer": 0, "byteLength": len(blob)}],
        "buffers": [{"byteLength": len(blob)}],
    }
    if data_uri:
        gltf["buffers"][0]["uri"] = "data:application/octet-stream;base64," + base64.b64encode(blob).decode()
    else:
        (path.parent / "box.bin").write_bytes(blob)
        gltf["buffers"][0]["uri"] = "box.bin"
    path.write_text(json.dumps(gltf), encoding="utf-8")
    return path


def test_measure_gltf_converts_y_up_to_z_up(tmp_path):
    # glTF x = 1.0 (width), y = 0.5 (height, up in glTF), z = 2.0 (depth): Blender frame (x, -z, y)
    path = _box_gltf(tmp_path / "box.gltf", (1.0, 0.5, 2.0), translation=[0.0, 0.25, 0.0])
    m = models.measure_gltf(path)
    assert m["bbox_m"] == [1.0, 2.0, 0.5]
    assert m["bbox_min_m"] == [-0.5, -1.0, 0.0] and m["bbox_max_m"] == [0.5, 1.0, 0.5]
    assert m["vertices"] == 8 and m["meshes"] == 1
    assert set(m["side_counts"]) == {"-x", "+x", "-y", "+y"} and m["side_counts"]["-x"] == 4


def test_measure_gltf_applies_node_transforms(tmp_path):
    # rotate 90 degrees about glTF Y (the up axis): x and z swap; parent scale 2 on x
    s = math.sqrt(0.5)
    path = _box_gltf(tmp_path / "rot.gltf", (1.0, 0.5, 2.0), rotation=[0.0, s, 0.0, s], parent_scale=[2.0, 1.0, 1.0],
                     data_uri=False)
    m = models.measure_gltf(path)
    assert m["bbox_m"] == pytest.approx([4.0, 1.0, 0.5], abs=1e-6)


def test_measure_gltf_rejects_empty(tmp_path):
    path = tmp_path / "empty.gltf"
    path.write_text(json.dumps({"asset": {"version": "2.0"}, "nodes": [], "meshes": [], "buffers": []}))
    with pytest.raises(models.ModelError):
        models.measure_gltf(path)
    missing = tmp_path / "missing.gltf"
    missing.write_text(json.dumps({"asset": {"version": "2.0"}, "buffers": [{"uri": "nope.bin", "byteLength": 1}]}))
    with pytest.raises(models.ModelError):
        models.measure_gltf(missing)


def test_api_dimensions_match():
    entry = {"bbox_m": [1.8072, 0.8178, 0.7095], "dimensions_api_mm": [1807.2, 817.8, 709.5]}
    assert models.api_dimensions_match(entry)
    assert not models.api_dimensions_match({"bbox_m": [0.6, 1.2, 0.39], "dimensions_api_mm": [1202, 600, 390]})
    assert not models.api_dimensions_match({"bbox_m": [1, 1, 1]})


# --------------------------------------------------------------------------
# Manifest section and licence (offline)
# --------------------------------------------------------------------------

def test_manifest_models_section_and_licence(tmp_path):
    assert "models" in fetch.empty_manifest()
    manifest = fetch.empty_manifest()
    manifest["models"]["x"] = {"id": "x", "source": "polyhaven", "licence": "CC-BY", "files": {}}
    fetch.save_manifest(tmp_path, manifest)
    with pytest.raises(fetch.LicenceError):
        fetch.load_manifest(tmp_path)
    with pytest.raises(fetch.LicenceError):
        models.fetch_model("sofa_02", tmp_path / "b", source="sketchfab")
    with pytest.raises(fetch.LicenceError):
        models.fetch_model("sofa_02", tmp_path / "b", licence="CC BY-NC")
    with pytest.raises(fetch.AssetNotFound):
        models.fetch_model("sofa_02", tmp_path / "b", source="ambientcg")


def test_fetch_model_is_idempotent_and_measures(tmp_path, monkeypatch):
    """A fake API and a fake download: the entry carries files, sha256 and the measured box; a second call is offline."""
    src = _box_gltf(tmp_path / "src" / "fake_1k.gltf", (0.8, 0.9, 0.7), translation=[0.0, 0.45, 0.0], data_uri=False)
    (tmp_path / "src" / "textures").mkdir()
    (tmp_path / "src" / "textures" / "fake_diff_1k.jpg").write_bytes(b"jpg")
    calls = []

    def fake_info(asset_id):
        return {"name": "Fake", "category": "Furniture/Seating", "dimensions": [800, 900, 700], "polycount": 12}

    def fake_files(asset_id):
        return {"gltf": {"1k": {"gltf": {"url": "https://x/fake_1k.gltf", "include": {
            "fake.bin": {"url": "https://x/box.bin"}, "textures/fake_diff_1k.jpg": {"url": "https://x/t.jpg"}}}}}}

    def fake_download(url, path, expected_md5=None, timeout=60):
        calls.append(url)
        name = url.rsplit("/", 1)[-1]
        source = {"fake_1k.gltf": src, "box.bin": src.parent / "box.bin", "t.jpg": src.parent / "textures" / "fake_diff_1k.jpg"}[name]
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        data = source.read_bytes()
        if name == "fake_1k.gltf":
            data = data.replace(b'"box.bin"', b'"fake.bin"')
        Path(path).write_bytes(data)
        return Path(path)

    monkeypatch.setattr(models.polyhaven, "info", fake_info)
    monkeypatch.setattr(models.polyhaven, "files", fake_files)
    monkeypatch.setattr(models.web, "download", fake_download)
    assets = tmp_path / "assets"
    entry = models.fetch_model("fake", assets, size="1k")
    assert entry["licence"] == "CC0" and entry["source"] == "polyhaven"
    assert entry["files"]["gltf"] == "models/fake/fake_1k.gltf"
    assert set(entry["files"]) == {"gltf", "fake.bin", "textures/fake_diff_1k.jpg"}
    for key, rel in entry["files"].items():
        assert (assets / rel).is_file() and web.sha256_file(assets / rel) == entry["sha256"][key]
    assert entry["bbox_m"] == [0.8, 0.7, 0.9] and entry["bbox_min_m"][2] == 0.0  # glTF y=0.9 up -> Blender z
    assert entry["dimensions_api_mm"] == [800, 900, 700]
    assert fetch.load_manifest(assets)["models"]["fake"] == entry
    assert len(calls) == 3
    # cached: no API call, no download
    monkeypatch.setattr(models.polyhaven, "info", lambda a: (_ for _ in ()).throw(AssertionError("network")))
    monkeypatch.setattr(models.web, "download", lambda *a, **k: (_ for _ in ()).throw(AssertionError("network")))
    assert models.fetch_model("fake", assets, size="1k") == entry
    assert models.total_size_bytes(assets) > 0
    with pytest.raises(models.ModelError):
        monkeypatch.setattr(models.polyhaven, "info", fake_info)
        monkeypatch.setattr(models.web, "download", fake_download)
        monkeypatch.setattr(models.polyhaven, "files", lambda a: {"gltf": {"1k": {"gltf": {
            "url": "https://x/fake_1k.gltf", "include": {"../evil.bin": {"url": "https://x/box.bin"}}}}}})
        models.fetch_model("evil", assets, size="1k")


def test_models_cli_verify_and_fetch(monkeypatch, capsys):
    monkeypatch.setattr(models, "verify_catalog", lambda ids: [
        {"id": i, "exists": i != "ghost", "name": i, "category": "Furniture", "dimensions_api_mm": [1000, 500, 800],
         "polycount": 1} for i in ids])
    assert assets_main(["models", "verify", "--ids", "sofa_02", "ghost"]) == 1
    out = capsys.readouterr().out
    assert "ghost" in out and "MISSING" in out and "1 missing" in out

    def fake_fetch(asset_id, out_dir, size="1k", source="polyhaven", licence=None):
        if asset_id == "ghost":
            raise fetch.AssetNotFound("polyhaven: no model 'ghost'")
        return {"id": asset_id, "licence": "CC0", "bbox_m": [1, 1, 1], "vertices": 8, "files": {"gltf": "x"}}

    monkeypatch.setattr(models, "fetch_model", fake_fetch)
    monkeypatch.setattr(models, "total_size_bytes", lambda d, ids=None: 0)
    assert assets_main(["models", "fetch", "--ids", "sofa_02", "ghost", "--assets", "/nonexistent"]) == 0
    assert assets_main(["models", "fetch", "--ids", "ghost", "--assets", "/nonexistent", "--strict"]) == 1
    assert "FAILED" in capsys.readouterr().out


# --------------------------------------------------------------------------
# Milestone 7: the Objaverse cache (docs/milestone7.md §6.3), offline by design
# --------------------------------------------------------------------------

def _objaverse_meta(uid="0123456789abcdef0123456789abcdef", sha="", **extra):
    meta = {"uid": uid, "sha256_glb": sha, "glb": f"models/objaverse/{uid}.glb", "title": "Chair",
            "author": "someone", "source_url": f"https://sketchfab.com/3d-models/{uid}",
            "licence_url": "https://creativecommons.org/licenses/by/4.0/",
            "via": "Objaverse (allenai/objaverse, ODC-By 1.0)", "attribution": '"Chair" by someone, CC BY 4.0'}
    meta.update(extra)
    return meta


def test_objaverse_models_come_from_the_cache_only(tmp_path, monkeypatch):
    """A cache hit with the catalogue sha256 is recorded with its credit line; a miss or another sha256 is
    AssetNotFound (the fit turns it into the parametric fallback); the network is never touched."""
    def no_network(*a, **k):
        raise AssertionError("network")

    monkeypatch.setattr(models.web, "download", no_network)
    monkeypatch.setattr(models.polyhaven, "info", no_network)
    monkeypatch.setattr(models.polyhaven, "files", no_network)
    assets = tmp_path / "assets"
    uid = "0123456789abcdef0123456789abcdef"
    glb = assets / models.objaverse_relpath(uid)
    assert models.objaverse_relpath(uid) == f"models/objaverse/{uid}.glb" and models.OBJAVERSE_CACHE == "models/objaverse"
    with pytest.raises(fetch.AssetNotFound, match="not in the cache"):
        models.fetch_model("objaverse_chair", assets, source="objaverse", licence="CC-BY-4.0",
                           meta=_objaverse_meta(sha="0" * 64))
    glb.parent.mkdir(parents=True)
    glb.write_bytes(b"glTF\x02\x00\x00\x00 fake glb")
    sha = web.sha256_file(glb)
    with pytest.raises(fetch.AssetNotFound, match="sha256"):
        models.fetch_model("objaverse_chair", assets, source="objaverse", licence="CC-BY-4.0",
                           meta=_objaverse_meta(sha="f" * 64))
    with pytest.raises(fetch.AssetNotFound, match="sha256_glb"):
        models.fetch_model("objaverse_chair", assets, source="objaverse", licence="CC-BY-4.0", meta=_objaverse_meta())
    with pytest.raises(fetch.AssetNotFound, match="plain object id"):
        models.fetch_model("objaverse_chair", assets, source="objaverse", licence="CC0",
                           meta=_objaverse_meta(uid="../../etc/passwd", sha=sha))
    with pytest.raises(fetch.LicenceError, match="credit line"):
        models.fetch_model("objaverse_chair", assets, source="objaverse", licence="CC-BY-4.0",
                           meta=_objaverse_meta(sha=sha, attribution=""))
    with pytest.raises(fetch.LicenceError):
        models.fetch_model("objaverse_chair", assets, source="objaverse", licence="CC-BY-NC-4.0",
                           meta=_objaverse_meta(sha=sha))
    entry = models.fetch_model("objaverse_chair", assets, source="objaverse", licence="CC-BY-4.0",
                               meta=_objaverse_meta(sha=sha))
    assert entry["source"] == "objaverse" and entry["licence"] == "CC-BY-4.0" and entry["cache_only"] is True
    assert entry["files"] == {"glb": f"models/objaverse/{uid}.glb"} and entry["sha256"] == {"glb": sha}
    assert entry["attribution"].startswith('"Chair" by someone') and entry["uid"] == uid
    assert fetch.load_manifest(assets)["models"]["objaverse_chair"] == entry
    mtime = fetch.manifest_path(assets).stat().st_mtime_ns
    assert models.fetch_model("objaverse_chair", assets, source="objaverse", licence="CC-BY-4.0",
                              meta=_objaverse_meta(sha=sha)) == entry                    # idempotent, no rewrite
    assert fetch.manifest_path(assets).stat().st_mtime_ns == mtime


def test_a_cache_miss_is_a_parametric_fallback_in_the_fit(tmp_path, capsys):
    from wenart.furniture import fit as F

    asset = dict(_objaverse_meta(sha="a" * 64), method="library", library="objaverse", asset_id="objaverse_chair",
                 licence="CC-BY-4.0")
    piece = {"id": "f_L0_001", "type": "chair", "footprint": {"center": [0, 0], "size": [0.5, 0.5], "rotation_deg": 0},
             "asset": asset}
    building = {"furniture": [piece]}
    result = F.download_fitted(building, tmp_path / "assets")
    assert result["fetched"] == [] and "AssetNotFound" in result["failed"]["objaverse_chair"]
    fallback = building["furniture"][0]["asset"]
    assert fallback["method"] == "parametric" and fallback["fallback_reason"].startswith("download of objaverse_chair")
    assert "not in the cache" in fallback["fallback_reason"]


# --------------------------------------------------------------------------
# Live API
# --------------------------------------------------------------------------

def test_catalog_ids_exist_on_the_api():
    """Every Poly Haven library and decor id of the catalogue is on the Poly Haven model listing (one call;
    Milestone 7: Objaverse entries of a merged catalogue come from the prep pod, not from this listing)."""
    catalog = C.load()
    ids = [e["id"] for e in catalog.models + catalog.decor if e["source"] == "polyhaven"]
    rows = network_or_skip(models.verify_catalog, ids)
    missing = [r["id"] for r in rows if not r["exists"]]
    assert not missing, missing
    assert len(rows) == len(ids) >= 30
    for row in rows:
        entry = catalog.entry(row["id"])
        assert row["dimensions_api_mm"] and len(row["dimensions_api_mm"]) == 3
        # the API box (mm) agrees with the measured model-frame box within 2 cm; the API lists x/y swapped for
        # modern_coffee_table_01 and wooden_display_shelves_01, so the horizontal pair is compared as a set
        if entry["id"] == "throw_pillows_01":
            continue  # the API box of the pillows is 8 cm larger than the glTF geometry (checked by hand)
        measured = entry["bbox_model_m"]
        api = [d / 1000.0 for d in row["dimensions_api_mm"]]
        assert abs(measured[2] - api[2]) <= 0.02, (entry["id"], measured, api)
        for a, b in zip(sorted(measured[:2]), sorted(api[:2])):
            assert abs(a - b) <= 0.02, (entry["id"], measured, api)


def test_download_armchair_and_compare_with_catalog():
    """ArmChair_01 at 1k into assets/ (cached): files, sha256, box within 1 cm of the catalogue, under 20 MB."""
    entry = network_or_skip(models.fetch_model, TEST_MODEL, ASSETS, size="1k")
    assert entry["licence"] == "CC0" and entry["source"] == "polyhaven"
    size = 0
    for key, rel in entry["files"].items():
        path = ASSETS / rel
        assert path.is_file() and web.sha256_file(path) == entry["sha256"][key]
        size += path.stat().st_size
    assert size < 20 * 1024 * 1024
    assert (ASSETS / entry["files"]["gltf"]).name == f"{TEST_MODEL}_1k.gltf"
    cat = C.load().entry(TEST_MODEL)
    assert cat is not None and cat["gltf"] == entry["files"]["gltf"]
    for a, b in zip(entry["bbox_m"], cat["bbox_model_m"]):
        assert abs(a - b) <= 0.01
    assert models.api_dimensions_match(entry)
    assert fetch.load_manifest(ASSETS)["models"][TEST_MODEL]["bbox_m"] == entry["bbox_m"]
