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


def test_licence_gates_per_kind():
    """docs/milestone7.md §6.3: textures and HDRIs CC0 only; models CC0, or CC BY 4.0 from Objaverse with the
    credit fields; NC/ND/SA and unknown sources refused."""
    assert fetch.KINDS == ("textures", "hdris", "models") and fetch.CC_BY == "CC-BY-4.0"
    for kind in ("textures", "hdris"):
        assert fetch.check_licence("polyhaven", "CC0", kind=kind) == "CC0"
        for licence in ("CC0", "CC-BY-4.0"):
            with pytest.raises(fetch.LicenceError):
                fetch.check_licence("objaverse", licence, kind=kind)
    assert fetch.check_licence("polyhaven", kind="models") == "CC0"
    with pytest.raises(fetch.LicenceError):
        fetch.check_licence("polyhaven", "CC-BY-4.0", kind="models")          # Poly Haven is CC0 only
    assert fetch.check_licence("objaverse", "cc0", kind="models") == "CC0"
    assert fetch.check_licence("objaverse", "CC-BY-4.0", kind="models") == "CC-BY-4.0"
    # Milestone 8 (docs/milestone8.md §2, user decisions 3, 4): every catalogue licence of an Objaverse object is
    # taken (flagged in the catalogue); a spelling outside the catalogue table is still refused.
    from wenart.furniture import catalog as C
    assert fetch._FLAGS == C.LICENCE_FLAGS
    for ok in ("CC-BY-NC-4.0", "CC-BY-SA-4.0", "CC-BY-ND-4.0", "Sketchfab-Standard", "unknown"):
        assert fetch.check_licence("objaverse", ok, kind="models") == ok
    for bad in (None, "CC-BY", "CC-BY 4.0", "free standard", ""):
        with pytest.raises(fetch.LicenceError):
            fetch.check_licence("objaverse", bad, kind="models")
    with pytest.raises(fetch.LicenceError, match="licence_flag"):        # the flag must be the licence's
        fetch.check_licence("objaverse", "CC-BY-NC-4.0", kind="models", entry={"licence_flag": None})
    # ABO: CC BY 4.0 only, with the credit; generated models: a licence that says so.
    assert fetch.check_licence("abo", "CC-BY-4.0", kind="models") == "CC-BY-4.0"
    for bad in ("CC0", "CC-BY-NC-4.0", None):
        with pytest.raises(fetch.LicenceError):
            fetch.check_licence("abo", bad, kind="models")
    assert fetch.check_licence("generated", "generated (TRELLIS.2-4B, MIT)", kind="models").startswith("generated")
    with pytest.raises(fetch.LicenceError):
        fetch.check_licence("generated", "MIT", kind="models")
    with pytest.raises(fetch.LicenceError):
        fetch.check_licence("generated", "generated", kind="textures")
    with pytest.raises(fetch.LicenceError):
        fetch.check_licence("sketchfab", "CC0", kind="models")
    credits = {"title": "t", "author": "a", "source_url": "u", "licence_url": "l", "via": "Objaverse",
               "attribution": "a line"}
    assert fetch.check_licence("objaverse", "CC-BY-4.0", kind="models", entry=credits) == "CC-BY-4.0"
    for field in fetch.CC_BY_FIELDS:
        with pytest.raises(fetch.LicenceError, match=field):
            fetch.check_licence("objaverse", "CC-BY-4.0", kind="models", entry=dict(credits, **{field: " "}))
    assert fetch.check_licence("objaverse", "CC0", kind="models", entry={}) == "CC0"   # CC0 needs no credit
    with pytest.raises(ValueError):
        fetch.check_licence("polyhaven", kind="fonts")
    assert set(fetch.LICENCES) == {"polyhaven", "ambientcg"}               # the CC0 source list is unchanged


def test_manifest_entries_are_checked_by_their_kind(tmp_path):
    credits = {"title": "t", "author": "a", "source_url": "u", "licence_url": "l", "via": "Objaverse",
               "attribution": "a line"}
    manifest = fetch.empty_manifest()
    manifest["models"]["o"] = dict(credits, id="o", source="objaverse", licence="CC-BY-4.0", files={})
    fetch.save_manifest(tmp_path, manifest)
    assert fetch.load_manifest(tmp_path)["models"]["o"]["licence"] == "CC-BY-4.0"
    manifest["models"]["o"]["attribution"] = ""
    fetch.save_manifest(tmp_path, manifest)
    with pytest.raises(fetch.LicenceError):
        fetch.load_manifest(tmp_path)                                     # CC BY without its credit line
    manifest = fetch.empty_manifest()
    manifest["textures"]["o"] = dict(credits, id="o", source="objaverse", licence="CC0", files={})
    fetch.save_manifest(tmp_path, manifest)
    with pytest.raises(fetch.LicenceError):
        fetch.load_manifest(tmp_path)                                     # textures: CC0 sources only


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
        if asset_id == "Metal032":
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
    # tiles_light (the wet floor and walls) is procedural since its Tiles074 proved a dark marble checkerboard.
    assert ids == {"WoodFloor051", "white_plaster_02", "white_planks_clean", "Metal032",
                   "rough_linen", "oak_veneer_01", "walnut_veneer",   # Milestone 6 furniture textures
                   # Milestone 10: the default style's exterior looks (render, concrete roof tiles, pavers, lawn) and the
                   # furniture veneers (docs/milestone10.md §1.6b row 14); procedural looks have nothing to fetch
                   "grey_plaster", "grey_roof_01", "large_square_pattern_01", "Grass004",
                   "oak_veneer_02", "ash_veneer", "white_maple_veneer", "teak_veneer", "black_oak_veneer", "cherry_veneer"}
    assert ("hdri", "kloppenheim_06", "1k") in calls
    out = capsys.readouterr().out
    assert "1 failed" in out and "Metal032" in out


# --------------------------------------------------------------------------
# Live APIs
# --------------------------------------------------------------------------

def test_vocabulary_ids_exist_on_the_apis():
    """Every texture and HDRI id in the vocabulary exists (listing calls only, no download)."""
    rows = network_or_skip(fetch.verify_vocabulary)
    missing = [r for r in rows if not r["exists"]]
    assert not missing, missing
    assert {r["slug"] for r in rows if r["kind"] == "texture"} == {s for s, e in V.MATERIALS.items() if e.get("asset")}
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


# --------------------------------------------------------------------------
# Milestone 10 (docs/milestone10.md §4.3, §4.8, §4.9; track C): procedural looks, the check record, new ids
# --------------------------------------------------------------------------

def test_procedural_looks_have_nothing_to_fetch(tmp_path, monkeypatch):
    """A profile with tiles, a wallpaper, slats, a standing-seam roof and flat metal frames needs only the textures of its
    other slots; the fetcher is never asked for an entry without an asset id."""
    from wenart.style import profile as SP

    profile = SP.profile_from_text("zellige bathroom tiles, sage botanical wallpaper, dark bronze window frames, zinc roof, oak floor")
    for slug in ("tiles_zellige", "wallpaper_botanical", "dark_bronze", "standing_seam"):
        assert V.MATERIALS[slug]["source"] == "procedural" and V.MATERIALS[slug]["asset"] is None
    wanted = SP.assets_in_profile(profile)["textures"]
    slugs = {slug for _, _, slug in wanted}
    assert not (slugs & {"tiles_zellige", "wallpaper_botanical", "dark_bronze", "standing_seam"})
    calls = []

    def fake_texture(asset_id, out_dir, size="2k", source=None, licence=None):
        calls.append(asset_id)
        return {"id": asset_id, "source": source, "licence": "CC0", "size_m": [1.0, 1.0], "files": {}}

    monkeypatch.setattr(fetch, "fetch_texture", fake_texture)
    monkeypatch.setattr(fetch, "fetch_hdri", lambda *a, **k: {"file": "x", "source": "polyhaven"})
    result = fetch.fetch_for_style(profile, tmp_path, size="1k", log=lambda *_: None)
    assert result["failed"] == {} and None not in calls and "WoodFloor051" in calls
    assert len(calls) == len(set(calls))


def test_poly_haven_record_types():
    assert (polyhaven.TYPE_HDRI, polyhaven.TYPE_TEXTURE, polyhaven.TYPE_MODEL) == (0, 1, 2) and fetch.PH_TEXTURE_TYPE == 1
    assert polyhaven.is_texture({"type": 1}) and not polyhaven.is_texture({"type": 0}) and not polyhaven.is_texture({})


def test_source_of_texture_knows_the_new_ids():
    assert fetch.source_of_texture("oak_wood_planks") == "polyhaven" and fetch.source_of_texture("Cork002") == "ambientcg"
    assert fetch.source_of_texture("WoodFloor034") == "ambientcg" and fetch.source_of_texture("PaintedBricks004") == "ambientcg"


def test_mean_linear_rgb_and_the_check_record_round_trip(tmp_path):
    Image.new("RGB", (32, 32), (128, 128, 128)).save(tmp_path / "grey.jpg", quality=100)
    assert fetch.mean_linear_rgb(tmp_path / "grey.jpg") == pytest.approx([0.216, 0.216, 0.216], abs=0.002)       # sRGB 128 -> 0.2158
    Image.new("RGB", (4, 4), (255, 0, 0)).save(tmp_path / "red.png")
    assert fetch.mean_linear_rgb(tmp_path / "red.png", side=2) == [1.0, 0.0, 0.0]
    checks = {"schema": fetch.CHECKS_SCHEMA, "checked": "2026-10-08", "textures": {}, "hdris": {}, "problems": []}
    path = fetch.write_checks(checks, tmp_path / "sub" / "checks.json")
    assert fetch.load_checks(path) == checks and path.read_text(encoding="utf-8").endswith("}\n")
    assert fetch.load_checks(tmp_path / "missing.json") == {}
    assert fetch.CHECKS_PATH.name == "asset_checks_m10.json" and fetch.CHECKS_PATH.parent.name == "style"


def test_download_support_covers_the_new_poly_haven_ids_and_hdris():
    """Every new Poly Haven texture of the vocabulary has the jpg maps the downloader reads at 1k and 2k, every HDRI the
    hdr file (the committed check record of the live APIs, 8 Oct 2026: no new fetch code was needed)."""
    from wenart.style import finishes as FIN

    checks = fetch.load_checks()
    for slug, e in list(FIN.MATERIALS.items()) + list(FIN.FURNITURE_MATERIALS.items()):
        if e.get("source") == "polyhaven":
            record = checks["textures"][f"polyhaven:{e['asset']}"]
            for key in polyhaven.TEXTURE_MAPS.values():
                assert {"1k", "2k"} <= set(record["maps"][key]), (slug, key)
        if e.get("source") == "ambientcg":
            record = checks["textures"][f"ambientcg:{e['asset']}"]
            assert {"1K-JPG", "2K-JPG"} <= set(record["downloads"]) and {"color", "normal", "roughness"} <= set(record["maps"]), slug
    for mood in ("bright noon", "blue hour", "cloudy soft", "interior evening"):
        hdri = V.LIGHTING[mood]["hdri"]
        assert {"1k", "2k"} <= set(checks["hdris"][hdri]["sizes"]) and checks["hdris"][hdri]["hdr_1k_2k"], hdri


def test_download_a_new_texture_and_hdri(monkeypatch):
    """One new Poly Haven texture set (1k) and one new HDRI (1k) through the unchanged downloader (network; cached in assets/)."""
    entry = network_or_skip(fetch.fetch_texture, "oak_veneer_02", ASSETS, size="1k")
    assert entry["source"] == "polyhaven" and entry["size_m"] == [1.0, 1.0] and set(entry["files"]) >= {"albedo", "normal", "roughness"}
    hdri = network_or_skip(fetch.fetch_hdri, V.LIGHTING["cloudy soft"]["hdri"], ASSETS, size="1k")
    assert hdri["licence"] == "CC0" and (ASSETS / hdri["file"]).is_file()
