"""CPU tests of the material and style side of the scene build
(wenart.blender.materials, the style and asset loading of build.py):

- the style vocabulary imports without PyYAML (Blender's Python has none)
  and materials.FLAT_COLOURS / ROUGHNESS are derived from it;
- texture sets and HDRIs that are not CC0 are refused with a warning;
- without --style the build uses the default profile of wenart.style (not a
  private copy), warns loudly, records it as assumed and textures the walls
  when the asset is in the manifest (one Blender build of synthetic-01 L0,
  skipped without a Blender binary).
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from wenart.assets import fetch
from wenart.blender import build, cli, materials, schemas
from wenart.style import vocabulary as V
from wenart.style.profile import default_profile

ROOT = Path(__file__).resolve().parents[1]
TRUTH = ROOT / "projects" / "synthetic-01" / "truth" / "building.json"
BLENDER = cli.find_blender()


# --------------------------------------------------------------------------
# Flat colours come from the vocabulary, also where PyYAML is missing
# --------------------------------------------------------------------------

NO_YAML = ("import sys, json; sys.modules['yaml'] = None\n"
           "from wenart.style import vocabulary as V\n"
           "from wenart.blender import materials as M\n"
           "print(json.dumps({'error': M.VOCABULARY_IMPORT_ERROR,"
           " 'flat': {s: list(M.flat_colour(s)) for s in V.MATERIALS},"
           " 'rough': {s: M.ROUGHNESS.get(s) for s in V.MATERIALS}}))\n")


def test_vocabulary_and_materials_import_without_yaml():
    proc = subprocess.run([sys.executable, "-c", NO_YAML], capture_output=True, text=True, cwd=str(ROOT), timeout=60)
    assert proc.returncode == 0, proc.stderr[-2000:]
    out = json.loads(proc.stdout)
    assert out["error"] is None
    for slug, entry in V.MATERIALS.items():
        assert out["flat"][slug] == pytest.approx(entry["flat"]), slug
        assert out["rough"][slug] == pytest.approx(V.ROUGHNESS[slug]), slug


@pytest.mark.skipif(BLENDER is None, reason="no Blender binary")
def test_blender_python_imports_the_vocabulary():
    """The same check inside the real Blender Python (no PyYAML there)."""
    expr = ("import sys, json; sys.path.insert(0, %r)\n" % str(ROOT)) + NO_YAML.split("\n", 1)[1]
    proc = subprocess.run([BLENDER, "-b", "--python-exit-code", "1", "--python-expr", expr],
                          capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    line = next(ln for ln in proc.stdout.splitlines() if ln.startswith("{"))
    out = json.loads(line)
    assert out["error"] is None
    assert out["flat"]["marble"] == pytest.approx(V.MATERIALS["marble"]["flat"])
    assert out["flat"]["plaster_charcoal"] == pytest.approx(V.MATERIALS["plaster_charcoal"]["flat"])


def test_every_vocabulary_slug_has_a_colour_and_a_roughness():
    assert set(V.MATERIALS) <= set(materials.FLAT_COLOURS) & set(materials.ROUGHNESS)
    for slug, entry in V.MATERIALS.items():
        assert materials.FLAT_COLOURS[slug] == pytest.approx(entry["flat"]), slug
        assert materials.flat_colour(slug) == pytest.approx(entry["flat"]), slug
        assert materials.ROUGHNESS[slug] == V.ROUGHNESS[slug] == entry["roughness"], slug
        assert 0.0 <= entry["roughness"] <= 1.0
    # Slugs only the scene builder uses keep a local colour.
    for slug in ("proxy_grey", "unknown", "plaster_exterior"):
        assert slug in materials.FLAT_COLOURS and slug in materials.ROUGHNESS
    assert materials.flat_colour("nobody_knows_this") == materials.FLAT_COLOURS["unknown"]


# --------------------------------------------------------------------------
# Licence check on the consumer side
# --------------------------------------------------------------------------

def _texture_files(root: Path, asset_id: str) -> dict:
    tex = root / "textures" / asset_id
    tex.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (16, 16), (200, 200, 195)).save(tex / "albedo.png")
    Image.new("RGB", (16, 16), (128, 128, 255)).save(tex / "normal.png")
    Image.new("L", (16, 16), 200).save(tex / "roughness.png")
    return {"albedo": f"textures/{asset_id}/albedo.png", "normal": f"textures/{asset_id}/normal.png",
            "roughness": f"textures/{asset_id}/roughness.png"}


def _manifest(root: Path) -> dict:
    """white_plaster_02 (CC0), Tiles074 (CC BY, refused), a texture from an
    unknown source (refused) and a non-CC0 HDRI (refused)."""
    (root / "hdris").mkdir(parents=True, exist_ok=True)
    (root / "hdris" / "fake.hdr").write_bytes(b"#?RADIANCE\n")
    manifest = {"schema_version": "0.1", "textures": {
        "white_plaster_02": {"id": "white_plaster_02", "source": "polyhaven", "licence": "CC0",
                             "size_m": [2.0, 2.0], "files": _texture_files(root, "white_plaster_02")},
        "Tiles074": {"id": "Tiles074", "source": "ambientcg", "licence": "CC BY 4.0",
                     "size_m": [1.0, 1.0], "files": _texture_files(root, "Tiles074")},
        "WoodFloor051": {"id": "WoodFloor051", "source": "sketchfab", "licence": "CC0",
                         "size_m": [1.8, 1.8], "files": _texture_files(root, "WoodFloor051")},
    }, "hdris": {
        "kloppenheim_06": {"id": "kloppenheim_06", "source": "polyhaven", "licence": "CC BY 4.0",
                           "file": "hdris/fake.hdr"},
    }}
    (root / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return manifest


def test_cc0_sources_match_the_fetcher():
    assert set(materials.CC0_SOURCES) == set(fetch.LICENCES)


def test_texture_set_refuses_non_cc0_entries(tmp_path):
    manifest = _manifest(tmp_path)
    lib = materials.MaterialLibrary(manifest["textures"], str(tmp_path))
    tset, reason = lib.texture_set("white_plaster_02")
    assert tset is not None and reason == "textured" and tset["licence"] == "CC0"
    tset, reason = lib.texture_set("Tiles074")
    assert tset is None and "CC BY 4.0" in reason and "refused" in reason
    tset, reason = lib.texture_set("WoodFloor051")
    assert tset is None and "sketchfab" in reason and "refused" in reason


def test_load_assets_drops_non_cc0_entries_with_a_warning(tmp_path):
    _manifest(tmp_path)
    warnings: list[str] = []
    textures, hdris, refused = build.load_assets(str(tmp_path), False, warnings)
    assert set(textures) == {"white_plaster_02"}
    assert hdris == {}
    assert set(refused) == {"Tiles074", "WoodFloor051", "kloppenheim_06"}
    assert "CC BY 4.0" in refused["Tiles074"] and "refused" in refused["Tiles074"]
    # The library reports the licence reason, not "not in the manifest".
    lib = materials.MaterialLibrary(textures, str(tmp_path), refused=refused)
    assert lib.texture_set("Tiles074") == (None, refused["Tiles074"])
    assert build.load_assets(str(tmp_path), True, warnings) == ({}, {}, {})
    assert any("Tiles074" in w and "CC BY 4.0" in w and "refused" in w for w in warnings)
    assert any("WoodFloor051" in w and "sketchfab" in w for w in warnings)
    assert any("kloppenheim_06" in w and "refused" in w for w in warnings)
    assert build.hdri_file(hdris, str(tmp_path), default_profile()) is None


# --------------------------------------------------------------------------
# Default style: the profile of wenart.style, loudly announced
# --------------------------------------------------------------------------

def test_load_style_without_a_file_uses_the_style_module_default(capsys):
    warnings: list[str] = []
    assumed: list[dict] = []
    style, path = build.load_style(None, warnings, assumed)
    assert path is None
    assert style == default_profile()
    assert style["walls"]["asset"] == V.MATERIALS["plaster_white"]["asset"] == "white_plaster_02"
    assert any("no --style" in w and "default style profile assumed" in w for w in warnings)
    assert [a for a in assumed if a["object"] == "style" and a["field"] == "profile"]
    assert "WARNING" in capsys.readouterr().err
    assert not hasattr(build, "DEFAULT_STYLE"), "build.py must not keep a private copy of the default profile"


def test_load_style_records_every_filled_slot_as_assumed(tmp_path):
    partial = {"source_text": "marble floor", "floor": {"material": "marble", "asset": "marble_01"}}
    path = tmp_path / "style.json"
    path.write_text(json.dumps(partial), encoding="utf-8")
    warnings: list[str] = []
    assumed: list[dict] = []
    style, used = build.load_style(str(path), warnings, assumed)
    assert used == str(path) and style["floor"]["material"] == "marble"
    assert style["walls"] == default_profile()["walls"]
    fields = {a["field"] for a in assumed if a["object"] == "style"}
    assert "walls" in fields and "lighting" in fields and "floor" not in fields
    assert any("walls" in w and "assumed" in w for w in warnings)


@pytest.fixture(scope="module")
def built_default(tmp_path_factory):
    """synthetic-01 L0 built with no --style and the manifest of ``_manifest``."""
    if BLENDER is None:
        pytest.skip("no Blender binary")
    tmp = tmp_path_factory.mktemp("blender_default_style")
    assets = tmp / "assets"
    _manifest(assets)
    out = tmp / "scene"
    cli.run_blender(cli.BUILD_SCRIPT, ["--building", str(TRUTH), "--assets", str(assets), "--out", str(out),
                                      "--level", "L0", "--no-preview", "--no-glb"],
                    log_path=out / "build.log", timeout=900)
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    return {"manifest": manifest, "log": (out / "build.log").read_text(encoding="utf-8")}


def test_default_style_build_textures_the_walls(built_default):
    m = built_default["manifest"]
    schemas.validate_scene_manifest(m)
    assert m["style"] is None and m["style_profile"] == default_profile()
    assert any("no --style" in w for w in m["warnings"])
    assert "WARNING" in built_default["log"]
    assert any(a["object"] == "style" and a["field"] == "profile" for a in m["assumed"])
    walls = [o for o in m["objects"] if o["kind"] == "wall" and not o.get("parent")]   # not the skirting (M6)
    assert walls and all(o["textured"] and o["material"] == "plaster_white__white_plaster_02" for o in walls)
    record = m["materials"]["plaster_white__white_plaster_02"]
    assert record["textured"] and record["asset"] == "white_plaster_02" and record["licence"] == "CC0"


def test_default_style_build_refuses_non_cc0_assets(built_default):
    m = built_default["manifest"]
    assert any("Tiles074" in w and "refused" in w for w in m["warnings"])
    assert any("kloppenheim_06" in w and "refused" in w for w in m["warnings"])
    for record in m["materials"].values():
        assert record["asset"] not in ("Tiles074", "WoodFloor051"), record
        assert record["licence"] in (None, "CC0")
    # The wet floor asks for Tiles074: flat, and the record says why.
    tiles = [r for r in m["materials"].values() if r["slug"] == "tiles_light" and "Tiles074" in r["reason"]]
    assert tiles and all(r["textured"] is False and "CC BY 4.0" in r["reason"] and "refused" in r["reason"]
                         for r in tiles)
    assert m["lighting"]["world"]["kind"] == "sky"
