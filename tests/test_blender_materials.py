"""CPU tests of the material and style side of the scene build
(wenart.blender.materials, the style and asset loading of build.py):

- the style vocabulary imports without PyYAML (Blender's Python has none)
  and materials.FLAT_COLOURS / ROUGHNESS are derived from it;
- texture sets and HDRIs that are not CC0 are refused with a warning;
- without --style the build uses the default profile of wenart.style (not a
  private copy), warns loudly, records it as assumed and textures the walls
  when the asset is in the manifest (one Blender build of synthetic-01 L0,
  skipped without a Blender binary).

Fix round after P4a (17 Oct 2026; P4a's bathroom mirrors rendered as blank frosted panels): the glass texels of a
library mirror (neutral albedo, ``materials.mirror_glass_texel``) become the vocabulary's mirror, the frame keeps
its maps (``materials.mirror_glass_material``; a Cycles render in Blender, skipped without a binary).
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
    # Milestone 13 round 3 (docs/milestone13.md §14.3): the shell material table is a production default. The
    # walls are the ``plaster`` slot (their own set, named as before); the ceilings ask for plaster_white without
    # an asset, which is the ``ceiling`` slot: the slot's set white_plaster_02 stands in and the material name
    # carries ``__ceiling`` so the two never collide into a Blender ``.001`` twin.
    assert record["shell_slot"] == "plaster"
    ceilings = [o for o in m["objects"] if o["kind"] == "ceiling"]
    assert ceilings and all(o["material"] == "plaster_white__white_plaster_02__ceiling" for o in ceilings)
    ceiling = m["materials"]["plaster_white__white_plaster_02__ceiling"]
    assert ceiling["shell_slot"] == "ceiling" and ceiling["textured"] and ceiling["asset"] == "white_plaster_02"
    assert "ao" in ceiling["shell_layers"]["applied"]
    # (wood_veneer_oak.001 / tiles_light.001 twins come from the library key of a refused asset, an older quirk
    # outside this round; the plaster names must not have one)
    assert not any(name.startswith("plaster_white") and name.endswith(".001") for name in m["materials"])


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
            # Milestone 13: under the shell lever the roughness variation group sits beside the look's group.
            groups = [g for g in rec["groups"] if g != materials.IMPERFECTION_GROUP]
            assert groups == [materials.procedural_group_name(rec["procedural"], entry.get("params") or {})]
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


def test_material_maps_and_recolour_parts_for_metric_10():
    """Milestone 13 (round 2, T8 metric 10): a material record lists the PBR maps it got (``maps``: the texture
    set's files pbr_material wires; [] for a flat or procedural material), and a scene object's ``recolour`` record
    gets one key per applied part (``fabric``, ``wood``) next to ``applied`` / ``missing`` so the metric finds
    ``recolour.fabric`` on the upholstered pieces."""
    files = {"albedo": "/a/alb.jpg", "normal": "/a/nor.png", "roughness": "/a/rough.jpg"}
    tset = {"id": "fabric_pattern_07", "files": files, "size_m": [1.0, 1.0], "source": "polyhaven", "licence": "CC0"}
    assert materials.material_maps(tset) == ["albedo", "normal", "roughness"]
    assert materials.material_maps(None) == [] and materials.material_maps({"files": {}}) == []
    more = dict(tset, files=dict(tset["files"], zzz="/a/z.png", displacement="/a/disp.png", opacity=""))
    assert materials.material_maps(more) == ["albedo", "normal", "roughness", "displacement", "zzz"]
    names = " ".join(materials.material_maps(tset)).lower()
    assert "normal" in names and "rough" in names                  # what metrics13.metric_10 looks for
    record = {"applied": [{"material": "sofa_fabric", "part": "fabric", "colour": "sage green",
                           "copy": "sofa_fabric__sage"},
                          {"material": "legs", "part": "wood", "colour": "oak", "copy": "legs__oak"},
                          {"material": "seat", "part": "fabric", "colour": "sage green", "copy": "seat__sage"}],
              "missing": ["cushion: colour 'x' unknown"]}
    parts = materials.recolour_parts(record)
    assert parts["applied"] == record["applied"] and parts["missing"] == record["missing"]
    assert parts["fabric"] == {"colour": "sage green", "materials": ["sofa_fabric", "seat"],
                               "copies": ["sofa_fabric__sage", "seat__sage"]}
    assert parts["wood"] == {"colour": "oak", "materials": ["legs"], "copies": ["legs__oak"]}
    assert "fabric" not in materials.recolour_parts({"applied": [], "missing": []})
    assert materials.recolour_parts(None) == {}
    assert materials.recolour_parts({"fabric": {"colour": "x"}}) == {"fabric": {"colour": "x"}}
    assert materials.recolour_parts(parts) == parts                    # idempotent on the manifest's shape
    # build.recolour_parts_of rewrites the scene objects in place and counts the changed records.
    objs = [{"wenart_id": "f_1", "recolour": dict(record)}, {"wenart_id": "f_2"},
            {"wenart_id": "f_3", "recolour": {"applied": []}}]
    assert build.recolour_parts_of(objs) == 1 and objs[0]["recolour"]["fabric"]["colour"] == "sage green"
    assert build.recolour_parts_of(objs) == 0
    # The record shape metrics13 reads: a dict with a truthy ``fabric`` key.
    assert isinstance(objs[0]["recolour"], dict) and objs[0]["recolour"].get("fabric")


SHELL_RECORDS = (
    "import sys, json\n"
    "sys.path.insert(0, %r)\n"
    "from wenart.blender import materials as M\n"
    "man = json.loads(open(%r, encoding='utf-8').read())\n"
    "lib = M.MaterialLibrary(man['textures'], %r, levers={'shell': True, 'rig': True, 'ev_cap': True, 'sun_wm2': 1000.0})\n"
    "out = {}\n"
    "for slug in ('plaster_white', 'stone_worktop', 'steel_brushed', 'metal_black'):\n"
    "    r = lib.records[lib.get(slug).name]\n"
    "    out[slug] = {k: r.get(k) for k in ('textured', 'shell_slot', 'shell_asset', 'shell_asset_missing')}\n"
    "print('SHELLREC ' + json.dumps(out))\n")


@pytest.mark.skipif(BLENDER is None, reason="no Blender binary")
def test_preflight_p3_a_shell_slot_set_is_recorded_only_when_the_material_uses_it():
    """Pre-flight of pod P3 (16 Oct 2026, real04 built on the CPU): the worktop record said ``shell_asset: marble_01``
    and a shell reason "on the Poly Haven marble_01 set" while ``textured`` was false (marble_01 was not in the
    assets). The slot's set is recorded only when the material uses it; a missing set is named with the reason. The
    repo's assets hold white_plaster_02 (the ceiling's set) and neither marble_01 nor Metal032."""
    assets = ROOT / "assets"
    expr = SHELL_RECORDS % (str(ROOT), str(assets / "manifest.json"), str(assets))
    proc = subprocess.run([BLENDER, "-b", "--python-exit-code", "1", "--python-expr", expr],
                          capture_output=True, text=True, timeout=300, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout[-2000:] + proc.stderr[-2000:]
    out = json.loads(next(ln for ln in proc.stdout.splitlines() if ln.startswith("SHELLREC "))[len("SHELLREC "):])
    assert out["plaster_white"]["textured"] and out["plaster_white"]["shell_asset"] == "white_plaster_02"
    assert out["plaster_white"]["shell_asset_missing"] is None
    worktop = out["stone_worktop"]
    assert worktop["shell_slot"] == "worktop" and not worktop["textured"] and worktop["shell_asset"] is None
    # fix round after P3: the worktop's set is Marble012 (one jointless slab), not in the repo's assets either
    assert worktop["shell_asset_missing"]["asset"] == "Marble012" and "Marble012" in worktop["shell_asset_missing"]["reason"]
    assert out["steel_brushed"]["shell_asset"] is None and out["steel_brushed"]["shell_asset_missing"]["asset"] == "Metal032"
    # the metal slot's set stands in for brushed steel only: black metal never claims or misses it
    assert out["metal_black"]["shell_asset"] is None and out["metal_black"]["shell_asset_missing"] is None


# --------------------------------------------------------------------------
# Fix round after P3 (16-17 Oct 2026): the worktop is one jointless slab, painted trim has no plank seams
# --------------------------------------------------------------------------

def test_p3_the_worktop_is_one_jointless_slab_and_painted_trim_has_no_plank_seams():
    """P3's kitchen worktops read as tiles (Poly Haven marble_01: "smooth, even cream-beige tiles", a joint every
    0.75 m) and the skirting showed a plank joint every ~10 cm (the white_planks_clean photo under the paint). The
    worktop slot is ambientCG Marble012 (CC0, a seamless polished slab, the vocabulary's marble_slab), repeated every
    2 m while its real size is unknown (``slot_repeat_m``); the front slot is a paint finish that leaves the plank
    photo out (``paint_drop``), also when a caller passes it; a set the style names itself stays. Fails on the code of
    the P3 results commit (marble_01, white_planks_clean, no slot_repeat_m / paint_drop)."""
    from wenart.blender import materials as M

    assets = M.shell_assets()
    assert assets["worktop"] == "Marble012" and assets["front"] is None
    checks = json.loads(fetch.CHECKS_PATH.read_text(encoding="utf-8"))["textures"]
    record = checks["ambientcg:Marble012"]
    assert record["exists"] and record["licence"] == "CC0" and record["has_required_maps"] and record["jpg_1k_2k"]
    assert V.MATERIALS["marble_slab"]["asset"] == "Marble012" and V.MATERIALS["marble"]["asset"] == "marble_01"
    worktop, front = M.shell_slot_spec("worktop", {}), M.shell_slot_spec("front", {})
    # the repeat: only for the slot's own set and only while the manifest knows no real size
    assert M.slot_repeat_m(worktop, "Marble012", {"size_m": [1.0, 1.0], "size_assumed": True}) == [2.0, 2.0]
    assert M.slot_repeat_m(worktop, "Marble012", {"files": {}}) == [2.0, 2.0]
    assert M.slot_repeat_m(worktop, "Marble012", {"size_m": [2.4, 2.4]}) is None
    assert M.slot_repeat_m(worktop, "marble_01", {"size_assumed": True}) is None
    assert M.slot_repeat_m(front, None, None) is None and M.slot_repeat_m(None, "Marble012", {}) is None
    # the paint finish: the slug's own plank set is dropped, another set (the style's) stays, other slots untouched
    assert front["paint"] and V.MATERIALS["painted_wood_white"]["asset"] == "white_planks_clean"
    assert M.paint_drop(front, "painted_wood_white", "white_planks_clean") == "white_planks_clean"
    assert M.paint_drop(front, "painted_wood_white", "oak_veneer_01") is None
    assert M.paint_drop(front, "painted_wood_white", None) is None
    assert M.paint_drop(worktop, "stone_worktop", "Marble012") is None
    assert M.shell_slot_spec("front", {"trim": {"material": "painted_wood_white", "asset": "oak_veneer_01"}})["asset"] \
        == "oak_veneer_01"
    # the assets stage fetches the new worktop set and no front set any more
    rows = fetch.shell_texture_rows()
    assert ("ambientcg", "Marble012", "shell:worktop") in rows and not [r for r in rows if r[2] == "shell:front"]


# --------------------------------------------------------------------------
# Fix round after P4a (17 Oct 2026): the glass of a library mirror is a mirror
# --------------------------------------------------------------------------

def _srgb(*c):
    return tuple(materials.srgb_to_linear(v) for v in c)


def test_p4a_mirror_glass_texels_are_the_neutral_ones():
    """The seven ABO mirrors of real02 (abo_B07B4W5R8N, B071HBBDZ1, B0718ZKQK8, B07RNMMYNR, B071V8LJQJ, B071V8M937,
    B084HTY39G) paint their glass as an exactly neutral grey ramp on one atlas with the frame, at roughness 1.0 / 0.4
    / 0 dielectric or 0.1 metal: P4a's "blank frosted panels". Their measured albedos (sRGB, means of the texel
    clusters): glass 0.81 / 0.53 / 0.83 / 0.74 / 0.62 / 0.50 / 0.66 grey; frames: walnut (0.41, 0.25, 0.17), painted
    white trim (0.89, 0.88, 0.87), hammered metal (0.37, 0.36, 0.33), gold (0.77, 0.62, 0.37); a black back 0.14
    grey. The rule keeps every frame and takes every glass."""
    for v in (0.81, 0.53, 0.83, 0.74, 0.62, 0.50, 0.66):
        assert materials.mirror_glass_texel(_srgb(v, v, v)), v
    for frame in ((0.41, 0.25, 0.17), (0.89, 0.88, 0.87), (0.37, 0.36, 0.33), (0.77, 0.62, 0.37), (0.14, 0.14, 0.14),
                  (0.63, 0.41, 0.25)):
        assert not materials.mirror_glass_texel(_srgb(*frame)), frame
    spec = materials.mirror_glass_spec()
    entry = V.FURNITURE_MATERIALS.get("mirror") or V.MATERIALS.get("mirror")
    assert spec["base"] == pytest.approx(tuple(entry["flat"])) and spec["roughness"] == entry["roughness"]
    assert spec["metallic"] == 1.0 and materials.srgb_to_linear(0.5) == pytest.approx(0.2140, abs=1e-4)


MIRROR_GLASS = r"""
import bpy, json, sys
sys.path.insert(0, %(root)r)
from wenart.blender import materials as M

def importer_like(name):
    # wired like the glTF importer's ABO material: albedo -> Base Color; a Non-Color metal/roughness image ->
    # Separate Color -> Green: Roughness, Blue: Metallic. Left half of the atlas: the painted grey ramp of the glass
    # (roughness 1, dielectric); right half: walnut (roughness 0.7).
    w, h = 64, 32
    alb, mr = bpy.data.images.new(name + "_alb", w, h), bpy.data.images.new(name + "_mr", w, h)
    mr.colorspace_settings.name = "Non-Color"
    pa, pm = [], []
    for y in range(h):
        for x in range(w):
            glass = x < w // 2
            v = 0.55 + 0.3 * x / w
            pa += [v, v, v, 1.0] if glass else [0.42, 0.25, 0.15, 1.0]
            pm += [1.0, 1.0, 0.0, 1.0] if glass else [1.0, 0.7, 0.0, 1.0]
    alb.pixels, mr.pixels = pa, pm
    mat = bpy.data.materials.new(name); mat.use_nodes = True
    nt = mat.node_tree; bsdf = nt.nodes["Principled BSDF"]
    ta = nt.nodes.new("ShaderNodeTexImage"); ta.image = alb; ta.interpolation = "Closest"
    tm = nt.nodes.new("ShaderNodeTexImage"); tm.image = mr; tm.interpolation = "Closest"
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(ta.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tm.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])
    return mat

def render(make, tag):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 16
    sc.render.resolution_x, sc.render.resolution_y = 64, 32
    sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.0, 0.0, 0.0)
    me = bpy.data.meshes.new("p"); me.from_pydata([(-1, -0.5, 0), (1, -0.5, 0), (1, 0.5, 0), (-1, 0.5, 0)], [],
                                                  [[0, 1, 2, 3]])
    uv = me.uv_layers.new(name="UVMap")
    for li, c in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = c
    sc.collection.objects.link(bpy.data.objects.new("p", me)); me.materials.append(make())
    em = bpy.data.materials.new("em"); em.use_nodes = True; nt = em.node_tree      # a checker seen only reflected
    nt.nodes.remove(nt.nodes["Principled BSDF"])
    ch = nt.nodes.new("ShaderNodeTexChecker"); ch.inputs["Scale"].default_value = 12.0
    ch.inputs["Color1"].default_value = (1, 1, 1, 1); ch.inputs["Color2"].default_value = (0, 0, 0, 1)
    es = nt.nodes.new("ShaderNodeEmission"); es.inputs["Strength"].default_value = 3.0
    nt.links.new(ch.outputs["Color"], es.inputs["Color"])
    nt.links.new(es.outputs[0], nt.nodes["Material Output"].inputs["Surface"])
    me2 = bpy.data.meshes.new("e")
    me2.from_pydata([(-4, -4, 4), (4, -4, 4), (4, 4, 4), (-4, 4, 4)], [], [[0, 3, 2, 1]])
    sc.collection.objects.link(bpy.data.objects.new("e", me2)); me2.materials.append(em)
    cam = bpy.data.cameras.new("c"); cam.type = "ORTHO"; cam.ortho_scale = 2.0
    co = bpy.data.objects.new("c", cam); co.location = (0, 0, 2); sc.collection.objects.link(co); sc.camera = co
    sc.render.filepath = %(out)r + f"/mirror_{tag}.png"; sc.render.image_settings.file_format = "PNG"
    bpy.ops.render.render(write_still=True)
    img = bpy.data.images.load(sc.render.filepath); px = list(img.pixels); w, h = img.size
    out = {}
    for half, xs in (("glass", range(4, w // 2 - 4)), ("wood", range(w // 2 + 4, w - 4))):
        vals = [sum(px[(y * w + x) * 4:(y * w + x) * 4 + 3]) / 3 for y in range(4, h - 4) for x in xs]
        m = sum(vals) / len(vals)
        out[half] = {"mean": m, "std": (sum((v - m) ** 2 for v in vals) / len(vals)) ** 0.5}
    return out

res = {"before": render(lambda: importer_like("abo"), "before"),
       "after": render(lambda: M.mirror_glass_material(importer_like("abo")), "after")}
res["record"] = json.loads(bpy.data.materials["abo__mirror"]["wenart_mirror_glass"])
bpy.ops.wm.read_factory_settings(use_empty=True)
grey = bpy.data.materials.new("grey"); grey.use_nodes = True
grey.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.6, 0.6, 0.6, 1.0)
wood = bpy.data.materials.new("wood"); wood.use_nodes = True
wood.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.4, 0.2, 0.1, 1.0)
mats, record = M.mirror_glass_materials([grey, None, wood])
g = mats[0].node_tree.nodes["Principled BSDF"].inputs
wd = mats[2].node_tree.nodes["Principled BSDF"].inputs
res["const"] = {"names": [m.name if m else None for m in mats], "record": record,
                "grey": [g["Metallic"].default_value, g["Roughness"].default_value,
                         list(g["Base Color"].default_value)[:3]],
                "wood": [wd["Metallic"].default_value, wd["Roughness"].default_value],
                "again": M.mirror_glass_material(grey).name == mats[0].name}
print("RESULT " + json.dumps(res))
"""


@pytest.mark.skipif(BLENDER is None, reason="no Blender binary")
def test_p4a_library_mirror_glass_reflects_and_its_frame_stays(tmp_path):
    """A material wired as the glTF importer wires the ABO mirrors: before, the glass half is a matte grey panel (a
    checker above the camera, seen only in a reflection, leaves no pattern); after ``mirror_glass_material`` it
    reflects the checker and the walnut half renders as before. Measured on the real abo_B07B4W5R8N and
    abo_B071V8M937 GLBs (17 Oct 2026, same render): the centre's std 0.03 -> 0.40 and 0.04 -> 0.32, frames
    unchanged. A constant neutral base colour is all glass; a brown one is left alone; the copy is cached."""
    proc = subprocess.run([BLENDER, "-b", "--factory-startup", "--python-exit-code", "1", "--python-expr",
                           MIRROR_GLASS % {"root": str(ROOT), "out": str(tmp_path)}],
                          capture_output=True, text=True, timeout=600, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout[-3000:] + proc.stderr[-3000:]
    out = json.loads(next(ln for ln in proc.stdout.splitlines() if ln.startswith("RESULT "))[7:])
    before, after = out["before"], out["after"]
    assert before["glass"]["std"] < 0.06 and after["glass"]["std"] > 0.25, out    # the checker shows: a mirror
    assert after["wood"]["mean"] == pytest.approx(before["wood"]["mean"], abs=0.01)
    assert after["wood"]["std"] < 0.02                                            # the frame does not reflect
    assert out["record"]["mask"] == "texture" and out["record"]["slug"] == "mirror"
    const = out["const"]
    assert const["names"] == ["grey__mirror", None, "wood__mirror"] and const["again"]
    assert const["record"] == {"grey": "all", "wood": "none"}
    assert const["grey"][:2] == pytest.approx([1.0, 0.03]) and const["grey"][2] == pytest.approx([0.9, 0.9, 0.9])
    assert const["wood"][0] == pytest.approx(0.0) and const["wood"][1] == pytest.approx(0.5)

