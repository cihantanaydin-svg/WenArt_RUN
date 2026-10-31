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
    assert fetch._FLAGS == C.LICENCE_TEXT_FLAGS                       # Milestone 13: "none", ND the stricter flag
    # the catalogue's Milestone 13 flag words: "none" (or the older None) for CC0 / CC BY, an audit-only flag allowed
    credit = {"title": "t", "author": "a", "source_url": "u", "licence_url": "l", "via": "v", "attribution": "x"}
    for flag in ("none", None, "regional"):
        assert fetch.check_licence("abo", "CC-BY-4.0", kind="models", entry=dict(credit, id="abo_f", licence_flag=flag)) \
            == "CC-BY-4.0"
    with pytest.raises(fetch.LicenceError):
        fetch.check_licence("abo", "CC-BY-4.0", kind="models", entry=dict(credit, id="abo_f", licence_flag="non_commercial"))
    assert fetch.check_licence("hssd", "CC-BY-NC-4.0", kind="models",
                               entry=dict(credit, id="hssd_f", licence_flag="non_commercial")) == "CC-BY-NC-4.0"
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
                   "oak_veneer_02", "ash_veneer", "white_maple_veneer", "teak_veneer", "black_oak_veneer", "cherry_veneer",
                   # Milestone 13 round 4: the worktop's shell set (materials.SHELL_SLOTS), named by no style slot;
                   # fix round after P3: Marble012 (one jointless slab) instead of marble_01 (tiles)
                   "Marble012",
                   # fix round after P3: the site finishes the build puts on by itself (exterior.build_finish_slugs:
                   # the retaining walls' concrete_exposed, the inferred fence's wood_cladding)
                   "concrete_wall_001", "weathered_plank_siding",
                   # 24 Oct 2026: the default facade scheme's base (stone_wall_ledgestone)
                   "rustic_stone_wall_02",
                   # 27 Oct 2026: the outdoor spaces' floors (decking, paving_stone) and their wood ceiling
                   # (exterior.build_finish_slugs: site.OUTDOOR_FLOOR_LOOKS, OUTDOOR_SOFFIT_LOOK)
                   "synthetic_wood", "floor_tiles_02", "oak_wood_planks",
                   # 28 Oct 2026: the outdoor floors by use (grading.floor_set): the default family's gravel path
                   "gravel_floor_02"} | {a for _, a, _ in fetch.design_texture_rows()} \
        | {a for _, a, _ in V.furniture_textures()}   # 29 Oct 2026: every finish; 31 Oct 2026: the fabric/leather scans
    assert ("hdri", "kloppenheim_06", "1k") in calls
    assert ("texture", "Marble012", "1k") in calls and ("texture", "Marble012", "2k") in calls   # at --size
    out = capsys.readouterr().out
    assert "1 failed" in out and "Metal032" in out
    # fix round after P3: the front slot is a paint finish (no set), so three shell slots carry a set
    assert ("shell sets: 2 of 3 ready (ceiling white_plaster_02 ok, worktop Marble012 ok, "
            "metal Metal032 FAILED)") in out
    # fix round after P3 (integration): the site finish sets are in the stage log too (P3 never fetched them)
    site_line = next(line for line in out.splitlines() if line.startswith("site sets: "))
    assert "platform_wall concrete_wall_001 ok" in site_line and "FAILED" in site_line     # Metal032 (kit) failed


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


# --------------------------------------------------------------------------
# Milestone 13 round 3: complete reads and retries (docs/milestone13.md §14.6, pod P2: two cut ambientCG answers)
# --------------------------------------------------------------------------

class FakeResponse(io.BytesIO):
    """A urlopen answer: a body and the headers the server sent (``Content-Length`` may be absent or wrong)."""

    def __init__(self, body: bytes, length=None):
        super().__init__(body)
        self.headers = {} if length is None else {"Content-Length": str(length)}


class FakeOpener:
    """``urlopen`` stand-in: answers in turn (bytes, ``(bytes, Content-Length)`` or an exception); records URLs."""

    def __init__(self, *answers):
        self.answers, self.urls = list(answers), []

    def __call__(self, request, timeout=None):
        self.urls.append(request.full_url)
        assert request.get_header("User-agent") == web.USER_AGENT
        answer = self.answers.pop(0)
        if isinstance(answer, BaseException):
            raise answer
        body, length = answer if isinstance(answer, tuple) else (answer, len(answer))
        return FakeResponse(body, length)


def test_get_json_tries_a_cut_answer_again_and_names_the_url_and_try_count():
    """P2: Metal051A arrived cut at char 61440 with no error from urllib. A cut body (no Content-Length, or fewer
    bytes than it says) or one that does not parse is asked again: 2 tries here; 3 cut answers fail with the URL and
    'try 3 of 3'."""
    good = json.dumps({"foundAssets": [{"assetId": "Metal051A", "x": "y" * 70000}]}).encode()
    waits = []
    opener = FakeOpener((good[:61440], None), good)                 # cut without Content-Length, then whole
    data = web.get_json("https://ambientcg.com/api/v2/full_json?id=Metal051A", opener=opener, sleep=waits.append)
    assert data["foundAssets"][0]["assetId"] == "Metal051A" and len(opener.urls) == 2 and waits == [1.0]
    opener = FakeOpener((good[:1000], len(good)), good)             # shorter than Content-Length
    assert web.get_json("https://x/a", opener=opener, sleep=lambda s: None)["foundAssets"]
    assert len(opener.urls) == 2
    waits.clear()
    opener = FakeOpener((good[:61440], None), (good[:-5], None), (good[:10], None))
    with pytest.raises(web.IncompleteBody) as exc:
        web.get_json("https://ambientcg.com/api/v2/full_json?id=Tiles074", opener=opener, sleep=waits.append)
    msg = str(exc.value)
    assert "https://ambientcg.com/api/v2/full_json?id=Tiles074" in msg and "try 3 of 3" in msg
    assert "does not parse" in msg
    assert len(opener.urls) == web.TRIES == 3 and waits == [1.0, 2.0]
    assert isinstance(exc.value, web.NetworkError)                  # callers that catch NetworkError still do


def test_http_status_retries_only_busy_servers():
    import urllib.error
    not_found = urllib.error.HTTPError("https://x/a", 404, "nf", {}, None)
    opener = FakeOpener(not_found)
    with pytest.raises(web.HTTPStatusError) as exc:
        web.get_bytes("https://x/a", opener=opener, sleep=lambda s: None)
    assert exc.value.status == 404 and len(opener.urls) == 1        # a 404 stays a 404: one try
    busy = urllib.error.HTTPError("https://x/a", 503, "busy", {}, None)
    opener = FakeOpener(busy, ConnectionResetError("reset"), b"ok")
    assert web.get_bytes("https://x/a", opener=opener, sleep=lambda s: None) == b"ok" and len(opener.urls) == 3
    opener = FakeOpener(urllib.error.URLError("proxy"), urllib.error.URLError("proxy"), urllib.error.URLError("proxy"))
    with pytest.raises(web.NetworkError, match=r"https://x/a: URLError: .*proxy.* \(try 3 of 3\)"):
        web.get_bytes("https://x/a", opener=opener, sleep=lambda s: None)


def test_download_retries_a_short_body_and_asks_the_origin_after_an_md5_mismatch(tmp_path):
    """16 Oct 2026: the CDN edge served a stale vintage_wooden_drawer_01.bin (md5 efa2b557...) for the plain URL;
    the URL with a query string reached the origin. A short body is tried again; after an md5 mismatch the next try
    asks ``<url>?wenart_fresh=<time>``; three mismatches fail with ChecksumError (a RuntimeError, as before)."""
    import hashlib
    good, stale = b"current file " * 100, b"stale copy " * 120
    want = hashlib.md5(good).hexdigest()
    url = "https://dl.polyhaven.org/file/ph-assets/Models/gltf/8k/x/x.bin"
    opener = FakeOpener((good[:50], len(good)), stale, good)
    out = web.download(url, tmp_path / "x.bin", expected_md5=want, opener=opener, sleep=lambda s: None)
    assert out.read_bytes() == good and not (tmp_path / "x.bin.part").exists()
    assert opener.urls[0] == url and opener.urls[1] == url and opener.urls[2].startswith(url + "?wenart_fresh=")
    fresh = web.fresh_url("https://ambientcg.com/get?file=a.zip")
    assert fresh.startswith("https://ambientcg.com/get?file=a.zip&wenart_fresh=")
    opener = FakeOpener(stale, stale, stale)
    with pytest.raises(web.ChecksumError) as exc:
        web.download(url, tmp_path / "y.bin", expected_md5=want, opener=opener, sleep=lambda s: None)
    assert isinstance(exc.value, RuntimeError) and "try 3 of 3" in str(exc.value) and url in str(exc.value)
    assert not (tmp_path / "y.bin").exists() and not (tmp_path / "y.bin.part").exists()
    assert [u.startswith(url + "?wenart_fresh=") for u in opener.urls] == [False, True, True]


def test_a_cut_body_from_a_local_server_is_read_again(tmp_path):
    """The same through real urllib and http.client: a local server sends ``Content-Length`` and closes the
    connection half-way on the first request; the second request gets the whole body."""
    import http.server
    import threading
    import urllib.request
    body = json.dumps({"foundAssets": [{"assetId": "Tiles074", "pad": "z" * 200000}]}).encode()
    hits = []

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802 - http.server API
            hits.append(self.path)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body if len(hits) > 1 else body[:len(body) // 2])
            self.wfile.flush()
            self.close_connection = True

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({})).open    # no proxy for 127.0.0.1
        url = f"http://127.0.0.1:{server.server_address[1]}/api/v2/full_json?id=Tiles074"
        data = web.get_json(url, timeout=10, opener=opener, sleep=lambda s: None)
        assert data["foundAssets"][0]["assetId"] == "Tiles074" and len(hits) == 2
        hits.clear()
        path = web.download(url, tmp_path / "t.json", timeout=10, opener=opener, sleep=lambda s: None)
        assert path.read_bytes() == body and len(hits) == 2
    finally:
        server.shutdown()
        server.server_close()


def test_a_cut_ambientcg_zip_is_fetched_once_more(tmp_path, monkeypatch):
    """A zip cut without Content-Length (chunked) passes web.download; extract_set raises BadZipFile: one more
    download, then the set; two cut zips fail with IncompleteBody (a NetworkError) naming the link."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for suffix in ("Color", "NormalGL", "Roughness"):
            zf.writestr(f"Tiles074_2K-JPG_{suffix}.jpg", b"jpg")
    whole = buf.getvalue()
    record = {"assetId": "Tiles074", "displayName": "Tiles 074", "dimensionX": 100, "dimensionY": 100,
              "downloadFolders": {"default": {"downloadFiletypeCategories": {"zip": {"downloads": [
                  {"attribute": "2K-JPG", "downloadLink": "https://ambientcg.com/get?file=Tiles074_2K-JPG.zip",
                   "fileName": "Tiles074_2K-JPG.zip", "size": len(whole)}]}}}}}
    monkeypatch.setattr(ambientcg, "info", lambda aid: record)
    bodies = [whole[:len(whole) // 2], whole]

    def fake_download(url, path, expected_md5=None, timeout=60):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(bodies.pop(0))
        return Path(path)
    monkeypatch.setattr(web, "download", fake_download)
    entry = fetch.fetch_texture("Tiles074", tmp_path, size="2k", source="ambientcg")
    assert set(entry["files"]) == {"albedo", "normal", "roughness"} and not bodies
    assert not (tmp_path / "downloads" / "Tiles074_2K-JPG.zip").exists()
    bodies[:] = [whole[:100], whole[:200]]
    with pytest.raises(web.IncompleteBody, match="Tiles074_2K-JPG.zip: not a whole zip after 2 downloads"):
        fetch.fetch_texture("Tiles074", tmp_path / "b", size="2k", source="ambientcg")


# --------------------------------------------------------------------------
# Milestone 13 round 4 (docs/milestone13.md §14.8, the CPU pre-flight of pod P3): the shell slots' texture sets
# --------------------------------------------------------------------------

# Fix round after P3 (16-17 Oct 2026): the worktop is ambientCG Marble012 (one jointless slab; Poly Haven marble_01 is a
# set of tiles), the front slot is a paint finish without a set (the plank photo's seams showed on the skirting).
SHELL_ROWS = [("polyhaven", "white_plaster_02", "shell:ceiling"), ("ambientcg", "Marble012", "shell:worktop"),
              ("ambientcg", "Metal032", "shell:metal")]


def _real04_like_profile():
    """A profile like P3's real04 style.json (dark bronze window frames, oak floor): it names neither the worktop's
    marble_01 nor the handles' Metal032, the two shell sets pod P1 and the pre-flight found missing."""
    from wenart.style import profile as SP

    profile = SP.profile_from_text("dark bronze window frames, oak floor")
    named = {asset_id for _, asset_id, _ in SP.assets_in_profile(profile)["textures"]}
    assert not named & {"marble_01", "Marble012", "Metal032"}, named
    return profile


def test_shell_texture_rows_are_the_materials_table():
    """One source of truth: the rows are read from wenart/blender/materials.py SHELL_SLOTS (importable without bpy),
    every id is a vocabulary id the committed check record lists as an existing CC0 set with 2k jpg maps."""
    import subprocess
    import sys

    from wenart.blender import materials as M

    # The pure table: a fresh interpreter imports materials.py and reads it without loading bpy.
    probe = ("import sys; from wenart.assets import fetch; rows = fetch.shell_texture_rows(); "
             "assert 'bpy' not in sys.modules, 'bpy loaded'; print(len(rows))")
    done = subprocess.run([sys.executable, "-c", probe], cwd=ROOT, capture_output=True, text=True, timeout=120)
    assert done.returncode == 0 and done.stdout.strip() == "3", done.stderr
    rows = fetch.shell_texture_rows()
    assert rows == SHELL_ROWS
    assert [a for _, a, _ in rows] == [a for a in M.shell_assets().values() if a]
    checks = json.loads(fetch.CHECKS_PATH.read_text(encoding="utf-8"))
    for source, asset_id, label in rows:
        record = checks["textures"][f"{source}:{asset_id}"]
        assert record["exists"] is True and record["licence"] == "CC0" and record["jpg_1k_2k"] is True, label
        assert record["has_required_maps"] is True and source in M.CC0_SOURCES and fetch.LICENCES[source] == "CC0"
    # The style's own slot set (ceiling.asset, trim.asset; materials.shell_slot_spec) is added, the table's stays.
    style = {"ceiling": {"material": "plaster_white", "asset": "plastered_wall"}}
    assert fetch.shell_texture_rows(style) == [SHELL_ROWS[0], ("polyhaven", "plastered_wall", "shell:ceiling")] \
        + SHELL_ROWS[1:]


def test_shell_texture_rows_follow_a_change_of_the_table(monkeypatch):
    """No copy of the ids in the fetcher: a new set in the table is what the stage fetches."""
    from wenart.blender import materials as M

    monkeypatch.setitem(M.SHELL_SLOTS["worktop"], "asset", "Marble006")
    monkeypatch.setitem(M.SHELL_SLOTS["ceramic"], "asset", "Porcelain001")
    rows = fetch.shell_texture_rows()
    assert ("ambientcg", "Marble006", "shell:worktop") in rows and ("ambientcg", "Porcelain001", "shell:ceramic") in rows
    assert "Marble012" not in {a for _, a, _ in rows}


def test_the_fetch_plan_adds_the_shell_sets_a_style_does_not_name():
    """P3's real04 case: the plan holds the worktop's set and Metal032 (labelled by their slot), after the style's and
    the furniture's sets, once each; a set the style already names keeps the style's label. Fix round after P3: the
    worktop's set is Marble012 and the site finishes' sets come last (``site:<part>``)."""
    from wenart.style import profile as SP

    profile = _real04_like_profile()
    plan = fetch.texture_plan(profile)
    ids = [a for _, a, _ in plan]
    assert len(ids) == len(set(ids))
    # 31 Oct 2026 (UL218): Metal032 is also the furniture's metal_black scan, so the furniture row names it first
    assert ("ambientcg", "Marble012", "shell:worktop") in plan and ("ambientcg", "Metal032", "metal_black") in plan
    style_rows = SP.assets_in_profile(profile)["textures"]
    assert plan[:len(style_rows)] == [tuple(r) for r in style_rows]
    assert ids.index("Marble012") > max(ids.index(a) for _, a, _ in V.furniture_textures())
    labels = {a: label for _, a, label in plan}
    assert labels["white_plaster_02"] == "plaster_white" and labels["white_planks_clean"] == "painted_wood_white"
    assert labels["concrete_wall_001"] == "site:platform_wall" and ids.index("concrete_wall_001") > ids.index("Marble012")
    assert set(ids) == ({a for _, a, _ in style_rows} | {a for _, a, _ in V.furniture_textures()}
                        | {a for _, a, _ in SHELL_ROWS} | {a for _, a, _ in fetch.site_texture_rows(profile)}
                        | {a for _, a, _ in fetch.design_texture_rows()})     # 29 Oct 2026: every finish's set
    assert "WoodFloor034" in ids                      # the herringbone parquet a design rule may lay (real04 run 201533)


def test_fetch_for_style_fetches_the_shell_sets_at_the_stage_size(tmp_path, monkeypatch):
    calls = []

    def fake_texture(asset_id, out_dir, size="2k", source=None, licence=None):
        calls.append((asset_id, source, size))
        if asset_id == "Metal032":
            raise web.NetworkError("blocked host (simulated)")
        return {"id": asset_id, "source": source, "licence": "CC0", "size_m": [1.5, 1.5], "files": {}}

    monkeypatch.setattr(fetch, "fetch_texture", fake_texture)
    monkeypatch.setattr(fetch, "fetch_hdri", lambda *a, **k: {"file": "x.hdr"})
    result = fetch.fetch_for_style(_real04_like_profile(), tmp_path, size="2k", log=lambda *_: None)
    assert ("Marble012", "ambientcg", "2k") in calls and ("Metal032", "ambientcg", "2k") in calls
    assert ("concrete_wall_001", "polyhaven", "2k") in calls                   # fix round after P3: a site finish
    assert len(calls) == len({c[0] for c in calls})
    assert result["shell"] == [
        {"slot": "ceiling", "asset": "white_plaster_02", "source": "polyhaven", "ready": True},
        {"slot": "worktop", "asset": "Marble012", "source": "ambientcg", "ready": True},
        {"slot": "metal", "asset": "Metal032", "source": "ambientcg", "ready": False}]
    assert result["site"][0] == {"part": "platform_wall", "asset": "concrete_wall_001", "source": "polyhaven",
                                 "ready": True}
    assert "Metal032" in result["failed"] and "Marble012" in result["textures"]


def test_an_unreadable_shell_table_is_recorded_and_the_style_sets_still_come(tmp_path, monkeypatch):
    def broken(style=None):
        raise ImportError("simulated")

    monkeypatch.setattr(fetch, "shell_texture_rows", broken)
    monkeypatch.setattr(fetch, "design_texture_rows", lambda: [])      # the shell table's own sets are the question
    monkeypatch.setattr(fetch, "fetch_texture", lambda aid, out, size="2k", source=None, licence=None:
                        {"id": aid, "source": source, "licence": "CC0", "size_m": [1, 1], "files": {}})
    monkeypatch.setattr(fetch, "fetch_hdri", lambda *a, **k: {"file": "x.hdr"})
    result = fetch.fetch_for_style(_real04_like_profile(), tmp_path, log=lambda *_: None)
    assert "ImportError: simulated" in result["failed"]["shell_slots"] and result["shell"] == []
    assert "WoodFloor051" in result["textures"] and "Marble012" not in result["textures"]


def test_the_shell_sets_go_through_the_fetchers_into_the_manifest_and_are_kept(tmp_path, monkeypatch):
    """Poly Haven and ambientCG faked at the API and download level: the shell sets (three since the fix round after
    P3) land in the manifest at 2k (CC0, the source, sha256 per map); a second run keeps the present files and makes
    no network call."""
    import hashlib

    monkeypatch.setattr(V, "furniture_textures", lambda: [])      # only the shell sets: style {} names nothing
    monkeypatch.setattr(fetch, "design_texture_rows", lambda: [])  # (29 Oct 2026: nor the design finishes)
    bodies, served = {}, []
    ph_ids = [a for s, a, _ in SHELL_ROWS if s == "polyhaven"]
    for aid in ph_ids:
        for key, colour in (("diff", (200, 190, 180)), ("nor_gl", (128, 128, 255)), ("rough", (90, 90, 90))):
            bodies[f"https://dl.polyhaven.org/{aid}_{key}_2k.jpg"] = _fake_jpg(colour)

    def ph_files(aid):
        assert aid in ph_ids, aid
        table = {}
        for key, name in (("diff", "Diffuse"), ("nor_gl", "nor_gl"), ("rough", "Rough")):
            url = f"https://dl.polyhaven.org/{aid}_{key}_2k.jpg"
            table[name] = {"2k": {"jpg": {"url": url, "md5": hashlib.md5(bodies[url]).hexdigest(),
                                          "size": len(bodies[url])}}}
        return table

    acg_records = {}
    for aid in [a for src, a, _ in SHELL_ROWS if src == "ambientcg"]:     # Marble012 (worktop), Metal032 (handles)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for suffix, colour in (("Color", (150, 150, 150)), ("NormalGL", (128, 128, 255)),
                                   ("Roughness", (80, 80, 80))):
                zf.writestr(f"{aid}_2K-JPG_{suffix}.jpg", _fake_jpg(colour))
        zip_url = f"https://ambientcg.com/get?file={aid}_2K-JPG.zip"
        bodies[zip_url] = buf.getvalue()
        acg_records[aid] = {"assetId": aid, "displayName": aid, "dimensionX": 0, "dimensionY": 0,
                            "downloadFolders": {"default": {"downloadFiletypeCategories": {"zip": {"downloads": [
                                {"attribute": "2K-JPG", "downloadLink": zip_url, "fileName": f"{aid}_2K-JPG.zip",
                                 "size": len(bodies[zip_url])}]}}}}}

    def fake_download(url, path, expected_md5=None, timeout=60):
        served.append(url)
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_bytes(bodies[url])
        return Path(path)

    monkeypatch.setattr(polyhaven, "info", lambda aid: {"name": aid, "type": 1, "dimensions": [1500.0, 1500.0]})
    monkeypatch.setattr(polyhaven, "files", ph_files)
    monkeypatch.setattr(ambientcg, "info", lambda aid: acg_records.get(aid))
    monkeypatch.setattr(web, "download", fake_download)
    monkeypatch.setattr(fetch, "site_texture_rows", lambda style=None: [])   # this test: the shell sets only
    result = fetch.fetch_for_style({}, tmp_path, size="2k", log=lambda *_: None)
    assert result["failed"] == {} and [r["ready"] for r in result["shell"]] == [True] * 3
    assert len(served) == 3 * 1 + 2                       # 3 maps of white_plaster_02, the 2 ambientCG zips
    manifest = fetch.load_manifest(tmp_path)
    assert sorted(manifest["textures"]) == sorted(a for _, a, _ in SHELL_ROWS)
    for source, aid, _ in SHELL_ROWS:
        entry = manifest["textures"][aid]
        assert entry["source"] == source and entry["licence"] == "CC0" and entry["resolution"] == "2k"
        assert set(entry["files"]) == {"albedo", "normal", "roughness"}
        for key, rel in entry["files"].items():
            assert web.sha256_file(tmp_path / rel) == entry["sha256"][key]
    assert manifest["textures"]["white_plaster_02"]["size_m"] == [1.5, 1.5]
    assert manifest["textures"]["Metal032"]["size_assumed"] is True       # ambientCG gives 0 x 0 for Metal032
    assert manifest["textures"]["Marble012"]["size_assumed"] is True      # and for Marble012 (materials.slot_repeat_m)

    def no_network(*args, **kwargs):
        raise AssertionError("network call for a set already on the volume")

    for module, name in ((web, "download"), (web, "get_json"), (polyhaven, "info"), (polyhaven, "files"),
                         (ambientcg, "info")):
        monkeypatch.setattr(module, name, no_network)
    again = fetch.fetch_for_style({}, tmp_path, size="2k", log=lambda *_: None)
    assert again["failed"] == {} and again["textures"] == result["textures"]
    assert fetch.load_manifest(tmp_path) == manifest


def test_the_shell_sets_exist_on_their_sites_at_2k():
    """Live APIs (listing and file tables only, no download): every shell set exists on its site with the 2k jpg
    maps the stage fetches."""
    for source, asset_id, label in fetch.shell_texture_rows():
        if source == "polyhaven":
            record = network_or_skip(polyhaven.info, asset_id)
            assert polyhaven.is_texture(record), label
            urls = polyhaven.texture_urls(network_or_skip(polyhaven.files, asset_id), size="2k", fmt="jpg")
            assert {"albedo", "normal", "roughness"} <= set(urls), label
        else:
            record = network_or_skip(ambientcg.info, asset_id)
            assert record is not None, label
            assert {"color", "normal", "roughness"} <= set(record.get("maps") or []), label
            assert ambientcg.zip_download(record, size="2k", fmt="JPG")["fileName"] == f"{asset_id}_2K-JPG.zip"
