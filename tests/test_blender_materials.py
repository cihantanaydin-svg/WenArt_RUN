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


def test_milestone_10_slugs_reach_the_blender_tables():
    """The vocabulary's Milestone 10 entries (procedural looks, flat metals, new veneers) are in the tables Blender reads
    (flat colour, roughness, albedo mode, metallic) and a procedural entry has no texture set to look for."""
    for slug in ("paint", "tiles_subway", "wallpaper_botanical", "dark_bronze", "pvc_white", "wood_veneer_oak_light", "metal_brass",
                 "rattan", "wood_oak_natural", "standing_seam"):
        assert slug in materials.FLAT_COLOURS and slug in materials.ROUGHNESS, slug
        assert materials.flat_colour(slug) == pytest.approx((V.MATERIALS.get(slug) or V.FURNITURE_MATERIALS[slug])["flat"]), slug
    assert materials.metallic("dark_bronze") == 0.8 and materials.metallic("metal_brass") == 1.0 and materials.metallic("paint") == 0.0
    assert materials.albedo_mode("paint") == ("flat", 0.2) and materials.albedo_mode("wood_oak_natural") == ("texture", None)
    assert materials.albedo_mode("tiles_subway") == ("flat", 0.0)            # a procedural look: the flat colour, no photo detail
    texture, why = materials.MaterialLibrary({}, None).texture_set(V.MATERIALS["tiles_subway"]["asset"])
    assert texture is None and "no asset" in why
    assert V.MATERIALS["tiles_subway"]["procedural"] == "wenart_tiles" and V.MATERIALS["tiles_subway"]["params"]["pattern"] == "running_bond"


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
    # Milestone 7: a style file without ``family`` (pre-M7) keeps none; it is never guessed from the default.
    assert "family" not in style and "family" not in fields and not [w for w in warnings if "'family'" in w]


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
    # Milestone 11 step 0 (docs/milestone11.md §1.3 M1, commit ad86494): tiles_light is a procedural light
    # ceramic, it asks for no image asset (Tiles074, the dark checkerboard, is refused but no longer used).
    tiles = [r for r in m["materials"].values() if r["slug"] == "tiles_light"]
    assert tiles and all(r["textured"] is False and r["procedural"] == "wenart_tiles" and r["asset"] is None
                         for r in tiles)
    assert m["lighting"]["world"]["kind"] == "sky"


# --------------------------------------------------------------------------
# Milestone 10 (track F): every slug resolves to a material; colours, procedural looks, the outside
# --------------------------------------------------------------------------

def test_every_milestone_10_slug_has_a_look():
    """Every vocabulary slug is a texture set, a procedural node group or a plain flat material, and a colour phrase
    reaches the slugs that take one (flat albedo mode and the procedural looks, not the wood tones or frame metals)."""
    from wenart.style import finishes as FIN
    from wenart.style.profile import is_colourable

    for slug, entry in list(V.MATERIALS.items()) + list(V.FURNITURE_MATERIALS.items()):
        proc = materials.procedural_for(slug, False, True)
        if entry.get("source") == "procedural":
            assert proc == entry.get("procedural"), slug              # a group, or None: a plain Principled
            assert proc is None or proc in materials.PROCEDURAL_GROUPS
        elif slug.startswith("tiles_"):
            assert proc == "glazed_tiles", slug                        # Milestone 6: an image set that is missing
        else:
            assert proc is None, slug
        assert materials.procedural_for(slug, False, False) is None
        assert materials.procedural_for(slug, True, True) is None
        assert materials.colourable(slug) == is_colourable(slug), slug
    for slug in FIN.TILE_PATTERNS:
        assert materials.procedural_params(slug)["tile_size_m"] == FIN.TILE_PATTERNS[slug]["tile_size_m"]
    over = materials.procedural_params("tiles_subway", {"tile_size_m": [0.2, 0.1], "pattern": None})
    assert over["tile_size_m"] == [0.2, 0.1] and over["pattern"] == "running_bond"
    assert materials.procedural_group_name("wenart_tiles", {"pattern": "hexagon"}) == "wenart_tiles_hexagon"
    assert materials.procedural_group_name("wenart_wallpaper", {"pattern": "nonsense"}) == "wenart_wallpaper_stripe"
    assert "0.200 x 0.100 m" in materials.procedural_note_for("wenart_tiles", "tiles_subway", over)
    assert materials.colour_linear("warm greige") is not None and materials.colour_linear("nope") is None
    assert materials.takes_colour("ceramic_white", False) and not materials.takes_colour("wood_veneer_oak", True)
    assert not materials.takes_colour("dark_bronze", False) and materials.takes_colour("paint", True)
    for mood in ("bright noon", "blue hour", "cloudy soft", "interior evening"):
        assert materials._MOOD_HDRI_STRENGTH[mood] == V.LIGHTING[mood]["hdri_strength"]


BUILD_EVERY_SLUG = """
import json, sys
sys.path.insert(0, %r)
from wenart.blender import materials as M
from wenart.style import vocabulary as V
lib = M.MaterialLibrary({}, None, use_textures=True)
out = {}
for slug in list(V.MATERIALS) + list(V.FURNITURE_MATERIALS):
    for colour in (None, "sage"):
        mat = lib.get(slug, None, colour=colour)
        rec = lib.records[mat.name]
        out[mat.name] = {"slug": slug, "procedural": rec["procedural"], "colour_applied": rec.get("colour_applied"),
                         "groups": [n.node_tree.name for n in mat.node_tree.nodes if n.bl_idname == "ShaderNodeGroup"],
                         "base": list(mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value)[:3]}
ext = M.exterior_material(lib, "render", "warm greige")
out["_ext"] = {"name": ext.name, "colour": lib.records[ext.name].get("colour")}
wet = lib.get("tiles_hexagon", None, colour="white", params={"tile_size_m": [0.2, 0.231], "grout_colour": "charcoal"})
out["_wet"] = lib.records[wet.name]
lit = M.light_material("lamp_light")
out["_light"] = {"name": lit.name, "strength": lit["wenart_light"]}
print("RESULT " + json.dumps(out))
"""


@pytest.mark.skipif(BLENDER is None, reason="no Blender binary")
def test_blender_builds_every_slug_with_its_colour_and_node_group():
    proc = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python-expr",
                           BUILD_EVERY_SLUG % str(ROOT)], capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    out = json.loads(next(ln for ln in proc.stdout.splitlines() if ln.startswith("RESULT "))[7:])
    sage = [round(min(v, materials.MAX_ALBEDO), 4) for v in materials.colour_linear("sage")]
    slugs = set()
    for name, rec in out.items():
        if name.startswith("_"):
            continue
        slugs.add(rec["slug"])
        entry = V.MATERIALS.get(rec["slug"]) or V.FURNITURE_MATERIALS.get(rec["slug"])
        if rec["procedural"] in materials.PROCEDURAL_GROUPS:
            assert rec["groups"] == [materials.procedural_group_name(rec["procedural"], entry.get("params") or {})]
        if name.endswith("__sage"):                    # no texture in use here: every slug but the fixed ones takes it
            assert rec["colour_applied"] and entry.get("colourable") is not False, name
            if not rec["groups"]:
                assert rec["base"] == pytest.approx(sage, abs=1e-3), name
        elif rec["colour_applied"] is False:
            assert entry.get("colourable") is False, name
    assert slugs == set(V.MATERIALS) | set(V.FURNITURE_MATERIALS)              # every slug resolves to a material
    assert out["_ext"]["name"] == "render__warm_greige" and out["_ext"]["colour"] == "warm greige"
    assert out["_wet"]["group"] == "wenart_tiles_hexagon" and out["_wet"]["params"]["grout_colour"] == "charcoal"
    assert out["_light"]["strength"] > 0
