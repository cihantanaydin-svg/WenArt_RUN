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


# --------------------------------------------------------------------------
# Milestone 13 round 3 (docs/milestone13.md §14.6): sizes the API does not offer, republished files
# --------------------------------------------------------------------------

def test_gltf_size_fallback_and_an_asset_without_gltf():
    """P2: decorative_book_set_01 had 'no gltf/2k (available: [])': its file table (16 Oct 2026) offers blend, fbx
    and usd only (NoGltf: dropped by the ingest, not a step failure); an asset with a smaller glTF takes it."""
    table = {"gltf": {"4k": {"gltf": {"url": "u4"}}, "1k": {"gltf": {"url": "u1"}}, "8k": {"gltf": {"url": "u8"}}},
             "blend": {}}
    assert models.gltf_sizes(table) == ["1k", "4k", "8k"]
    assert models.pick_gltf_size(table, "4k") == ("4k", None)
    used, why = models.pick_gltf_size(table, "2k")
    assert used == "1k" and "no glTF at 2k" in why and "next lower" in why
    used, why = models.pick_gltf_size({"gltf": {"4k": {"gltf": {"url": "u4"}}}}, "2k")
    assert used == "4k" and "smallest size offered" in why
    books = {"blend": {"1k": {}}, "fbx": {"1k": {}}, "usd": {"1k": {}}, "book_hardcover_01_diff": {"1k": {}}}
    for call in (lambda: models.pick_gltf_size(books, "2k"), lambda: models.model_gltf(books, "2k")):
        with pytest.raises(models.NoGltf, match=r"no glTF at any size .*\['blend', 'fbx', 'usd'\]") as exc:
            call()
        assert isinstance(exc.value, KeyError)                       # what the fit's handlers already catch


def test_fetch_model_size_fallback_and_a_republished_file(tmp_path, monkeypatch):
    """A fake Poly Haven with a 1k glTF only: ``size_fallback`` takes 1k and records why (a second call is
    offline); then the asset is republished at twice the size (vintage_wooden_drawer_01, 16 Oct 2026): a cached
    entry is still returned without ``expect_sha256_gltf``; with the new sha256 the files are fetched again, the
    old ``.gltf`` is kept beside as ``.superseded-<sha12>`` (nothing deleted) and the new box is measured."""
    import hashlib
    src = tmp_path / "src"
    served = {}

    def publish(size_xyz):
        g = _box_gltf(src / "fake_1k.gltf", size_xyz, data_uri=False)
        served["fake_1k.gltf"] = g.read_bytes().replace(b'"box.bin"', b'"fake.bin"')
        served["fake.bin"] = (src / "box.bin").read_bytes()

    def table(asset_id):
        md5 = {k: hashlib.md5(v).hexdigest() for k, v in served.items()}
        include = {"fake.bin": {"url": "https://x/fake.bin", "md5": md5["fake.bin"]}}
        return {"gltf": {"1k": {"gltf": {"url": "https://x/fake_1k.gltf", "md5": md5["fake_1k.gltf"],
                                         "include": include}}}, "blend": {}}
    calls = []

    def fake_download(url, path, expected_md5=None, timeout=60):
        calls.append(url.rsplit("/", 1)[-1])
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(served[url.rsplit("/", 1)[-1]])
        return Path(path)
    monkeypatch.setattr(models.polyhaven, "info", lambda a: {"name": "Fake", "dimensions": [860, 460, 550]})
    monkeypatch.setattr(models.polyhaven, "files", table)
    monkeypatch.setattr(models.web, "download", fake_download)
    publish((0.86, 0.55, 0.46))
    assets = tmp_path / "assets"
    e = models.fetch_model("fake", assets, size="2k", size_fallback=True)
    assert e["resolution"] == "1k" and e["resolution_requested"] == "2k" and "no glTF at 2k" in e["resolution_note"]
    assert e["files"]["gltf"] == "models/fake/fake_1k.gltf" and e["bbox_m"] == [0.86, 0.46, 0.55]
    assert sorted(calls) == ["fake.bin", "fake_1k.gltf"]
    calls.clear()
    assert models.fetch_model("fake", assets, size="2k", size_fallback=True) == e and not calls     # cached
    with pytest.raises(KeyError, match="gltf/2k"):
        models.fetch_model("fake", assets, size="2k")                   # without the switch: as before
    old_sha = e["sha256"]["gltf"]

    publish((1.72, 1.09, 1.01))                                         # republished: twice the size
    new_sha = hashlib.sha256(served["fake_1k.gltf"]).hexdigest()
    assert models.fetch_model("fake", assets, size="1k")["sha256"]["gltf"] == old_sha and not calls   # cache kept
    e2 = models.fetch_model("fake", assets, size="1k", expect_sha256_gltf=new_sha)
    assert e2["sha256"]["gltf"] == new_sha and e2["bbox_m"] == [1.72, 1.01, 1.09]
    assert calls == ["fake_1k.gltf", "fake.bin"]
    kept = assets / "models" / "fake" / f"fake_1k.gltf{models.SUPERSEDED}{old_sha[:12]}"
    assert kept.is_file() and web.sha256_file(kept) == old_sha
    assert kept.relative_to(assets).as_posix() in e2["superseded"] and len(e2["superseded"]) == 2   # .bin too
    calls.clear()
    assert models.fetch_model("fake", assets, size="1k", expect_sha256_gltf=new_sha) == e2 and not calls
    assert models.keep_aside(tmp_path / "nothing_here") is None
    # review of round 3: a later download that keeps nothing aside (here the current .gltf went missing) keeps the
    # entry's record of the files an older publication left beside
    (assets / e2["files"]["gltf"]).unlink()
    e3 = models.fetch_model("fake", assets, size="1k", expect_sha256_gltf=new_sha)
    assert calls == ["fake_1k.gltf"] and e3["superseded"] == e2["superseded"] and kept.is_file()


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
    with pytest.raises(fetch.LicenceError):                       # a licence spelling outside the catalogue table
        models.fetch_model("objaverse_chair", assets, source="objaverse", licence="CC BY-NC",
                           meta=_objaverse_meta(sha=sha))
    with pytest.raises(fetch.LicenceError, match="licence_flag"):  # M8: flagged licences carry their flag
        models.fetch_model("objaverse_chair", assets, source="objaverse", licence="CC-BY-NC-4.0",
                           meta=_objaverse_meta(sha=sha, licence_flag=None))
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


def test_the_fit_download_asks_for_the_size_of_the_gltf_the_build_loads(tmp_path, monkeypatch):
    """Milestone 13 round 3 (A1's ask, integration): pod P2 relinked 87 Poly Haven entries to ``2k``; the fit's
    download fetches the size of the entry's ``.gltf`` (the file the scene builder loads), not a fixed ``1k`` that would
    rewrite the asset manifest entry back to 1k (and fall to the parametric model on an offline pod)."""
    from wenart.furniture import fit as F

    asked = []

    def fake_fetch(asset_id, out_dir, size="1k", source="polyhaven", licence=None, meta=None, **kw):
        asked.append((asset_id, size, source))
        return {"id": asset_id}

    monkeypatch.setattr(models, "fetch_model", fake_fetch)
    pieces = [{"id": f"f{i}", "type": "sofa", "asset": {"method": "library", "library": "polyhaven", "asset_id": aid,
                                                       "licence": "CC0", "gltf": f"models/{aid}/{aid}_{size}.gltf"}}
              for i, (aid, size) in enumerate([("sofa_02", "2k"), ("armchair_01", "1k")])]
    result = F.download_fitted({"furniture": pieces}, tmp_path / "assets", log=lambda *_: None)
    assert result == {"fetched": ["sofa_02", "armchair_01"], "failed": {}}
    assert asked == [("sofa_02", "2k", "polyhaven"), ("armchair_01", "1k", "polyhaven")]
    assert F.polyhaven_size_of({"gltf": "models/x/x_2k.gltf"}) == "2k"
    assert F.polyhaven_size_of({"resolution": "2k"}) == "2k" and F.polyhaven_size_of({}) == "1k"


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
        if entry.get("growth"):
            continue  # pod P4: the box is the audit's Blender measurement of the file (the API box may differ: an
            #           articulated desk_lamp_arm_01, a 10x steel_frame_shelves_01 the audit removed)
        # vintage_wooden_drawer_01 was republished at twice the size (API 1715 x 1007 x 1091 mm since at least 12 Oct
        # 2026); on 16 Oct its current file was measured (1.7151 x 1.0069 x 1.0908 m, md5 checked) and the entry
        # updated, audit pending until the next audit judges it (test_the_republished_drawer_waits_for_its_reaudit):
        # every entry, that one included, must still agree with the live API here
        measured = entry["bbox_model_m"]
        api = [d / 1000.0 for d in row["dimensions_api_mm"]]
        assert abs(measured[2] - api[2]) <= 0.02, (entry["id"], measured, api)
        for a, b in zip(sorted(measured[:2]), sorted(api[:2])):
            assert abs(a - b) <= 0.02, (entry["id"], measured, api)


def test_the_republished_drawer_waits_for_its_reaudit():
    """Item 5 of round 3 (docs/milestone13.md §14.6): the catalogue entry of vintage_wooden_drawer_01 carries the box
    of the current Poly Haven file (measured on 16 Oct 2026 with glbmesh.measure after the md5 check: twice the old
    size, drawers pulled out), the old values under audit.before, the evidence under audit.reaudit, and it stays out
    of the fit (audit pending) until the next audit has rendered and judged the new file (growth run refetch, then
    the catalogue step puts it into new_ids.json)."""
    from wenart.assets.audit import growth_run as GR
    doc = json.loads((ROOT / "wenart" / "furniture" / "catalog.json").read_text(encoding="utf-8"))
    e = next(x for x in doc["entries"] if isinstance(x, dict) and x.get("id") == "vintage_wooden_drawer_01")
    a = e["audit"]
    assert e["sha256_gltf"] == a["reaudit"]["files"]["gltf"]["sha256"] == \
        "4080ecdac2228759dd41a5d5705b984f993bbf6b0f66570824a9dcbbeaa49e51"
    assert a["reaudit"]["files"]["gltf"]["md5"] == "88e36661f5a778b4b5b2c4a3715c4e11"           # the API's md5
    assert a["reaudit"]["files"]["bin"]["md5"] == "61ea9192d2199cd76f54623942b5bde4"
    assert a["reaudit"]["measured"]["bbox_model_m"] == [1.7151, 1.0069, 1.0908]
    old = a["before"]
    assert old["bbox_model_m"] == [0.8576, 0.4574, 0.5454] and old["audit"]["status"] == "keep"
    if a["status"] != "pending":
        # judged by the next audit (pod P2b) and its copy taken into the repo: ``audit write`` keeps the reaudit
        # evidence and the before values (write.CARRIED); the entry has a decision and waits no longer
        assert a["status"] in ("keep", "fix", "removed") and a.get("decision_sha"), a
        assert e["id"] not in [x["id"] for x in GR.reaudit_entries(doc)]
        return
    assert a["reasons"] == ["republished at a new size on Poly Haven, 15 Oct 2026"]
    assert e["bbox_model_m"] == [1.7151, 1.0069, 1.0908] and e["dimensions_api_mm"] == [1715, 1007, 1091]
    assert e["origin_offset"] == C.origin_offset(e["bbox_min_m"], e["bbox_max_m"])
    for i in (0, 2):                                                    # width and height: twice the old file
        assert abs(e["bbox_model_m"][i] - 2 * old["bbox_model_m"][i]) <= 0.001
    assert not C.usable(e, "commercial") and not C.usable(e, "relaxed")
    assert [x["id"] for x in GR.reaudit_entries(doc)] == ["vintage_wooden_drawer_01"]


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


# --------------------------------------------------------------------------
# Milestone 8: every library source from the cache (docs/milestone8.md §2)
# --------------------------------------------------------------------------

def _library_meta(source, uid, sha, **extra):
    meta = {"uid": uid, "sha256_glb": sha, "glb": f"models/{source}/{uid}.glb", "title": "Rug", "author": "Amazon.com",
            "source_url": f"https://amazon-berkeley-objects.s3.amazonaws.com/index.html#{uid[4:]}",
            "licence_url": "https://creativecommons.org/licenses/by/4.0/", "via": "Amazon Berkeley Objects (CC BY 4.0)",
            "attribution": '"Rug" by Amazon.com, Amazon Berkeley Objects (CC BY 4.0), '
                           "https://amazon-berkeley-objects.s3.amazonaws.com/index.html", "licence_flag": None}
    meta.update(extra)
    return meta


def test_abo_generated_and_flagged_objaverse_models_come_from_the_cache_only(tmp_path, monkeypatch):
    """ABO and generated models use the same cache-only fetch as Objaverse (``<assets>/models/<source>/<uid>.glb``,
    sha256 checked against the catalogue); the manifest keeps the credit fields, the licence flag and the
    generated record; a flagged Objaverse licence is fetched with its flag."""
    def no_network(*a, **k):
        raise AssertionError("network")

    monkeypatch.setattr(models.web, "download", no_network)
    monkeypatch.setattr(models.polyhaven, "info", no_network)
    assets = tmp_path / "assets"

    def put(source, uid):
        path = assets / models.library_relpath(source, uid)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(f"glTF {source} {uid}".encode())
        return web.sha256_file(path)

    # hssd: Milestone 13 pod P2 (build round 2); = catalog.LIBRARY_SOURCES, the cache layout of every library source
    assert models.LIBRARY_SOURCES == ("objaverse", "abo", "generated", "gso", "hssd", "3dwh") == models.CACHE_SOURCES
    from wenart.furniture import catalog as C
    assert set(models.LIBRARY_SOURCES) == set(C.LIBRARY_SOURCES)
    assert models.library_relpath("abo", "abo_B07B4SCB6T") == "models/abo/abo_B07B4SCB6T.glb"
    with pytest.raises(fetch.AssetNotFound, match="not a library source"):
        models.library_relpath("polyhaven", "x")
    sha = put("abo", "abo_B071777YN3")
    entry = models.fetch_model("abo_B071777YN3", assets, source="abo", licence="CC-BY-4.0",
                               meta=_library_meta("abo", "abo_B071777YN3", sha))
    assert entry["source"] == "abo" and entry["files"] == {"glb": "models/abo/abo_B071777YN3.glb"}
    assert entry["licence"] == "CC-BY-4.0" and entry["licence_flag"] is None and entry["author"] == "Amazon.com"
    assert entry["cache_only"] is True and fetch.load_manifest(assets)["models"]["abo_B071777YN3"] == entry
    with pytest.raises(fetch.LicenceError):                                # ABO is CC BY 4.0
        models.fetch_model("abo_B071777YN3", assets, source="abo", licence="CC0",
                           meta=_library_meta("abo", "abo_B071777YN3", sha))
    with pytest.raises(fetch.LicenceError, match="credit line"):
        models.fetch_model("abo_B071777YN3", assets, source="abo", licence="CC-BY-4.0",
                           meta=_library_meta("abo", "abo_B071777YN3", sha, author=""))
    with pytest.raises(fetch.AssetNotFound, match="sha256"):
        models.fetch_model("abo_B071777YN3", assets, source="abo", licence="CC-BY-4.0",
                           meta=_library_meta("abo", "abo_B071777YN3", "e" * 64))
    with pytest.raises(fetch.AssetNotFound, match="not in the cache"):
        models.fetch_model("abo_other", assets, source="abo", licence="CC-BY-4.0",
                           meta=_library_meta("abo", "abo_other", "e" * 64))
    gen_uid = "gen_chair_scandinavian_1_ab12cd34"
    gsha = put("generated", gen_uid)
    record = {"prompt": "a single scandinavian style chair", "image_sha256": "c" * 64,
              "model": "microsoft/TRELLIS.2-4B", "revision": "af44b45", "seed": 7}
    gen = models.fetch_model(gen_uid, assets, source="generated", licence="generated (TRELLIS.2-4B, MIT)",
                             meta={"uid": gen_uid, "sha256_glb": gsha, "licence_flag": None, "generated": record})
    assert gen["source"] == "generated" and gen["generated"] == record and gen["licence"].startswith("generated")
    uid = "0123456789abcdef0123456789abcdef"
    osha = put("objaverse", uid)
    nc = models.fetch_model(f"objaverse_{uid}", assets, source="objaverse", licence="CC-BY-NC-4.0",
                            meta=_objaverse_meta(uid=uid, sha=osha, licence_flag="non_commercial"))
    assert nc["licence"] == "CC-BY-NC-4.0" and nc["licence_flag"] == "non_commercial"
    assert set(fetch.load_manifest(assets)["models"]) == {"abo_B071777YN3", gen_uid, f"objaverse_{uid}"}
    # Build round 2: an HSSD model (Milestone 13 pod P2, CC BY-NC 4.0 per the dataset card) comes from the same cache
    # layout with its flag and credit line; any other licence text is refused, like a missing credit field.
    hid = "hssd_" + "a" * 40
    hsha = put("hssd", hid)
    assert models.library_relpath("hssd", hid) == f"models/hssd/{hid}.glb"
    hmeta = _library_meta("hssd", hid, hsha, title="Taylor sofa", author="the HSSD authors",
                          source_url="https://huggingface.co/datasets/hssd/hssd-models/blob/x/objects/a/a.glb",
                          licence_url="https://huggingface.co/datasets/hssd/hssd-models",
                          via="HSSD: Habitat Synthetic Scenes Dataset (hssd/hssd-models) (CC BY-NC 4.0)",
                          attribution='"Taylor sofa" from HSSD, CC BY-NC 4.0', licence_flag="non_commercial")
    hs = models.fetch_model(hid, assets, source="hssd", licence="CC-BY-NC-4.0", meta=hmeta)
    assert hs["source"] == "hssd" and hs["files"] == {"glb": f"models/hssd/{hid}.glb"} and hs["cache_only"] is True
    assert hs["licence"] == "CC-BY-NC-4.0" and hs["licence_flag"] == "non_commercial" and hs["author"] == "the HSSD authors"
    with pytest.raises(fetch.LicenceError):                                # HSSD is CC BY-NC 4.0 only
        models.fetch_model(hid, assets, source="hssd", licence="CC0", meta=hmeta)
    with pytest.raises(fetch.LicenceError, match="credit line"):
        models.fetch_model(hid, assets, source="hssd", licence="CC-BY-NC-4.0", meta=dict(hmeta, attribution=""))
    assert hid in fetch.load_manifest(assets)["models"]


def test_material_fields_and_plant_variant_reach_the_manifest_only_when_the_catalogue_has_them(tmp_path):
    """Milestone 10: ``material_slots``, ``material_tags``, ``recolourable_fabric/wood`` and a large plant's
    ``species`` / ``pot`` are copied to the manifest entry when the catalogue entry has them, and are absent otherwise
    (an M8/M9 entry stays byte-identical)."""
    assets = tmp_path / "assets"
    uid = "abo_B071777YN3"
    path = assets / models.library_relpath("abo", uid)
    path.parent.mkdir(parents=True)
    path.write_bytes(b"glTF abo m10")
    sha = web.sha256_file(path)
    plain = models.fetch_model(uid, assets, source="abo", licence="CC-BY-4.0", meta=_library_meta("abo", uid, sha))
    assert not set(models.LIBRARY_OPTIONAL) & set(plain)
    rows = [{"index": 0, "name": "Material_0", "material": "fabric", "materials": ["fabric"], "agreed": True,
             "separable": True, "share": 1.0, "textured": True, "base_colour": None, "colour_rgb": [120, 110, 90]}]
    extra = {"material_slots": rows, "material_tags": ["fabric"], "recolourable_fabric": True,
             "recolourable_wood": False, "species": "olive", "pot": {"material": "terracotta", "colour": None},
             "attributes_status": "assumed"}
    rich = models.fetch_model(uid, assets, source="abo", licence="CC-BY-4.0",
                              meta=_library_meta("abo", uid, sha, **extra))
    assert {k: rich[k] for k in extra} == extra                            # False is kept: it is an answer
    assert fetch.load_manifest(assets)["models"][uid] == rich
