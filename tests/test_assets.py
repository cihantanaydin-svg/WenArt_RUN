"""CC0 asset fetcher (wenart/assets, Milestone 3 section 2).

Offline tests cover the licence refusal, the manifest, the file-table parsers
and the ambientCG zip unpacking with a fake zip. The network tests list the
vocabulary ids against the live APIs and download one 1k texture set plus one
1k HDRI into ``assets/`` (git-ignored, cached: a second run downloads nothing).
They skip when the network is unreachable (connection-level failure only; an
HTTP error or a missing id is a real failure).
"""
import io
import json
import zipfile
from pathlib import Path

import pytest
from PIL import Image

from wenart.assets import ambientcg, fetch, polyhaven, web
from wenart.assets.__main__ import main as assets_main
from wenart.style import vocabulary as V

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
TEST_TEXTURE = "white_plaster_02"   # Poly Haven, 1k jpg set ~1.5 MB
TEST_HDRI = "kloppenheim_06"        # Poly Haven, 1k hdr ~1.5 MB


def network_or_skip(call, *args, **kwargs):
    """Run an API call; skip the test when the network itself is unavailable."""
    try:
        return call(*args, **kwargs)
    except web.NetworkError as exc:
        pytest.skip(f"network unavailable: {exc}")


# --------------------------------------------------------------------------
# Licence and manifest (offline)
# --------------------------------------------------------------------------

def test_licence_refuses_everything_but_cc0(tmp_path):
    assert fetch.check_licence("polyhaven") == "CC0"
    assert fetch.check_licence("ambientcg", "CC0") == "CC0"
    with pytest.raises(fetch.LicenceError):
        fetch.check_licence("polyhaven", "CC-BY 4.0")
    with pytest.raises(fetch.LicenceError):
        fetch.check_licence("sketchfab")
    with pytest.raises(fetch.LicenceError):
        fetch.fetch_texture("anything", tmp_path, source="textures.com")
    with pytest.raises(fetch.LicenceError):
        fetch.fetch_texture("white_plaster_02", tmp_path, licence="CC BY-NC")
    with pytest.raises(fetch.LicenceError):
        fetch.fetch_hdri("kloppenheim_06", tmp_path, licence="CC-BY")
    with pytest.raises(fetch.AssetNotFound):
        fetch.fetch_hdri("kloppenheim_06", tmp_path, source="ambientcg")


def test_manifest_with_non_cc0_entry_is_refused(tmp_path):
    manifest = fetch.empty_manifest()
    manifest["textures"]["x"] = {"id": "x", "source": "polyhaven", "licence": "CC-BY", "files": {}}
    fetch.save_manifest(tmp_path, manifest)
    with pytest.raises(fetch.LicenceError):
        fetch.load_manifest(tmp_path)
    assert fetch.load_manifest(tmp_path / "missing") == fetch.empty_manifest()


def test_source_inference():
    assert fetch.source_of_texture("WoodFloor051") == "ambientcg"
    assert fetch.source_of_texture("white_plaster_02") == "polyhaven"
    assert fetch.source_of_texture("Bricks074") == "ambientcg"      # by id shape
    assert fetch.source_of_texture("some_new_texture") == "polyhaven"
    assert ambientcg.looks_like_id("PaintedWood007A") and not ambientcg.looks_like_id("wood_floor")


# --------------------------------------------------------------------------
# API response parsing (offline, shapes copied from real responses)
# --------------------------------------------------------------------------

def test_polyhaven_parsers():
    table = {"Diffuse": {"1k": {"jpg": {"url": "u/d_1k.jpg", "md5": "a", "size": 1}}},
             "nor_gl": {"1k": {"jpg": {"url": "u/n_1k.jpg", "md5": "b", "size": 1}}},
             "Rough": {"1k": {"jpg": {"url": "u/r_1k.jpg", "md5": "c", "size": 1}}},
             "Displacement": {"1k": {"png": {"url": "u/disp.png", "md5": "d", "size": 1}}}}
    urls = polyhaven.texture_urls(table, size="1k")
    assert set(urls) == {"albedo", "normal", "roughness"}  # displacement only as jpg
    with pytest.raises(KeyError):
        polyhaven.texture_urls(table, size="2k")
    assert polyhaven.size_m({"dimensions": [1799.99995, 1800]}) == [1.8, 1.8]
    assert polyhaven.size_m({"dimensions": None}) is None and polyhaven.size_m({}) is None
    assert polyhaven.hdri_url({"hdri": {"2k": {"hdr": {"url": "h"}}}}, size="2k") == {"url": "h"}
    with pytest.raises(KeyError):
        polyhaven.hdri_url({"hdri": {}}, size="2k")


def test_ambientcg_parsers():
    record = {"assetId": "WoodFloor051", "dimensionX": 180, "dimensionY": 180, "downloadFolders": {"default": {
        "downloadFiletypeCategories": {"zip": {"downloads": [
            {"attribute": "1K-JPG", "downloadLink": "https://ambientcg.com/get?file=WoodFloor051_1K-JPG.zip",
             "fileName": "WoodFloor051_1K-JPG.zip", "size": 5104319},
            {"attribute": "2K-JPG", "downloadLink": "https://ambientcg.com/get?file=WoodFloor051_2K-JPG.zip",
             "fileName": "WoodFloor051_2K-JPG.zip", "size": 16427258}]}}}}}
    assert ambientcg.size_m(record) == ([1.8, 1.8], False)
    assert ambientcg.size_m({"dimensionX": 0, "dimensionY": 0}) == ([1.0, 1.0], True)
    assert ambientcg.zip_download(record, size="2k")["fileName"] == "WoodFloor051_2K-JPG.zip"
    with pytest.raises(KeyError):
        ambientcg.zip_download(record, size="8k")


def _fake_jpg(colour) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), colour).save(buf, format="JPEG")
    return buf.getvalue()


def test_ambientcg_zip_extraction(tmp_path):
    zip_path = tmp_path / "Fake001_1K-JPG.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("Fake001_1K-JPG_Color.jpg", _fake_jpg((200, 180, 160)))
        zf.writestr("Fake001_1K-JPG_NormalGL.jpg", _fake_jpg((128, 128, 255)))
        zf.writestr("Fake001_1K-JPG_NormalDX.jpg", _fake_jpg((128, 128, 255)))
        zf.writestr("Fake001_1K-JPG_Roughness.jpg", _fake_jpg((128, 128, 128)))
        zf.writestr("Fake001_1K-JPG_Displacement.jpg", _fake_jpg((128, 128, 128)))
        zf.writestr("Fake001_1K-JPG_AmbientOcclusion.jpg", _fake_jpg((255, 255, 255)))
    files = ambientcg.extract_set(zip_path, tmp_path / "out")
    assert set(files) == {"albedo", "normal", "roughness", "displacement"}
    assert files["normal"].name == "Fake001_1K-JPG_NormalGL.jpg"
    assert all(p.is_file() for p in files.values())
    assert not (tmp_path / "out" / "Fake001_1K-JPG_NormalDX.jpg").exists()
    # a zip without a roughness map is an error, not a silent partial set
    bad = tmp_path / "Bad001.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("Bad001_1K-JPG_Color.jpg", _fake_jpg((1, 2, 3)))
        zf.writestr("Bad001_1K-JPG_NormalGL.jpg", _fake_jpg((1, 2, 3)))
    with pytest.raises(KeyError):
        ambientcg.extract_set(bad, tmp_path / "out2")


# --------------------------------------------------------------------------
# CLI wiring (offline: fetchers replaced)
# --------------------------------------------------------------------------

def test_fetch_cli_collects_style_assets(tmp_path, monkeypatch, capsys):
    style = json.loads((ROOT / "tests" / "fixtures" / "style_synthetic-01.json").read_text(encoding="utf-8"))
    style_path = tmp_path / "style.json"
    style_path.write_text(json.dumps(style), encoding="utf-8")
    calls = []

    def fake_texture(asset_id, out_dir, size="2k", source=None, licence=None):
        calls.append(("texture", asset_id, size))
        if asset_id == "Tiles074":
            raise web.NetworkError("blocked host (simulated)")
        return {"id": asset_id, "source": source, "licence": "CC0", "size_m": [1.0, 1.0], "files": {}}

    def fake_hdri(asset_id, out_dir, size="2k", source="polyhaven", licence=None):
        calls.append(("hdri", asset_id, size))
        return {"id": asset_id, "file": f"hdris/{asset_id}_{size}.hdr", "licence": "CC0", "source": source}

    monkeypatch.setattr(fetch, "fetch_texture", fake_texture)
    monkeypatch.setattr(fetch, "fetch_hdri", fake_hdri)
    assert assets_main(["fetch", "--style", str(style_path), "--assets", str(tmp_path / "a"), "--size", "1k"]) == 0
    assert assets_main(["fetch", "--style", str(style_path), "--assets", str(tmp_path / "a"), "--strict"]) == 1
    ids = {c[1] for c in calls if c[0] == "texture"}
    assert ids == {"WoodFloor051", "white_plaster_02", "Tiles074", "white_planks_clean", "Metal032",
                   "rough_linen", "oak_veneer_01", "walnut_veneer"}  # Milestone 6 furniture textures
    assert ("hdri", "kloppenheim_06", "1k") in calls
    out = capsys.readouterr().out
    assert "1 failed" in out and "Tiles074" in out


# --------------------------------------------------------------------------
# Live APIs
# --------------------------------------------------------------------------

def test_vocabulary_ids_exist_on_the_apis():
    """Every texture and HDRI id in the vocabulary exists (listing calls only, no download)."""
    rows = network_or_skip(fetch.verify_vocabulary)
    missing = [r for r in rows if not r["exists"]]
    assert not missing, missing
    assert {r["slug"] for r in rows if r["kind"] == "texture"} == set(V.MATERIALS)
    assert {r["id"] for r in rows if r["kind"] == "hdri"} == set(V.HDRIS)
    for row in rows:
        if row["kind"] == "texture":
            assert row["size_m"] and row["size_m"][0] > 0 and row["size_m"][1] > 0, row


def test_download_one_texture_set_and_one_hdri(monkeypatch):
    """One 1k texture set and one 1k HDRI into assets/ (cached), manifest entries follow the shared interface."""
    entry = network_or_skip(fetch.fetch_texture, TEST_TEXTURE, ASSETS, size="1k")
    assert entry["source"] == "polyhaven" and entry["licence"] == "CC0"
    assert entry["size_m"] == [1.0, 1.0] and "size_assumed" not in entry
    assert set(entry["files"]) >= {"albedo", "normal", "roughness"}
    for key, rel in entry["files"].items():
        path = ASSETS / rel
        assert path.is_file() and path.stat().st_size > 0
        assert web.sha256_file(path) == entry["sha256"][key]
    with Image.open(ASSETS / entry["files"]["albedo"]) as img:
        assert img.size == (1024, 1024)

    hdri = network_or_skip(fetch.fetch_hdri, TEST_HDRI, ASSETS, size="1k")
    assert hdri["licence"] == "CC0" and hdri["source"] == "polyhaven"
    assert (ASSETS / hdri["file"]).is_file() and hdri["file"].endswith("_1k.hdr")

    manifest = fetch.load_manifest(ASSETS)
    assert manifest["textures"][TEST_TEXTURE]["files"] == entry["files"]
    assert manifest["hdris"][TEST_HDRI]["file"] == hdri["file"]

    # Idempotent: a second call touches the network for nothing.
    def no_network(*args, **kwargs):
        raise AssertionError("network call on a cached asset")
    monkeypatch.setattr(web, "download", no_network)
    monkeypatch.setattr(web, "get_json", no_network)
    assert fetch.fetch_texture(TEST_TEXTURE, ASSETS, size="1k") == entry
    assert fetch.fetch_hdri(TEST_HDRI, ASSETS, size="1k") == hdri
