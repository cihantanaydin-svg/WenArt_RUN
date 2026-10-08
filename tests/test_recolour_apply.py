"""Milestone 10 recolour, material tags and the refit's locked check (docs/milestone10.md §4.5, §2.7, §1.6b row 16;
track F).

The fit honours a piece's look (``furniture.design``, else ``style.json``): models whose judged ``material_tags`` lack
an asked tag ("glass coffee table") are skipped, an upholstered piece's fabric colour needs a ``recolourable_fabric``
model (its separable fabric slots recoloured: ``asset.recolour``) or a model already that colour (``colour_match``,
CIELAB Delta E), unjudged models are skipped for such a brief, nothing left -> parametric; the wood is recoloured on
``recolourable_wood`` models and preferred, never a reason to skip. The judged fields travel with the asset. The
fit CLI's ``--source`` / ``--completion`` run ``locked.check`` and exit 1 on a violation. The scene builder
recolours the slot materials of a library model (a Blender scene, skipped without ``WENART_BLENDER``).
"""
from __future__ import annotations

import copy
import json
import textwrap
from pathlib import Path

import pytest

from wenart.blender import cli
from wenart.blender import furniture as F
from wenart.furniture import catalog as C
from wenart.furniture import fit
from wenart.style import colours as CL

ROOT = Path(__file__).resolve().parents[1]
BLENDER = cli.find_blender()
needs_blender = pytest.mark.skipif(BLENDER is None, reason="no Blender binary (WENART_BLENDER)")
CREDIT = {"title": "t", "author": "a", "source_url": "https://example.org/m", "licence_url":
          "https://creativecommons.org/licenses/by/4.0/", "via": "ABO", "attribution": "t by a, CC BY 4.0"}


def _model(mid, ftype="sofa", bbox=(2.2, 0.9, 0.85), quality=None, **fields):
    e = {"id": mid, "type": ftype, "source": "abo", "licence": "CC-BY-4.0", "bbox_m": list(bbox),
         "bbox_model_m": list(bbox), "bbox_min_m": [-bbox[0] / 2, -bbox[1] / 2, 0.0],
         "bbox_max_m": [bbox[0] / 2, bbox[1] / 2, bbox[2]], "front_axis": "-Y", "up_axis": "+Z",
         "origin_offset": [0.0, 0.0, 0.0], "front_axis_confidence": "high", "glb": f"models/abo/{mid}.glb",
         "sha256_glb": "0" * 64, "uid": mid, "styles": ["neutral"], **CREDIT}
    if quality is not None:
        e["quality"] = quality
    e.update(fields)
    return e


def _slot(index, material, rgb=None, separable=True, share=0.6, name=None):
    return {"index": index, "name": name or f"mat{index}", "material": material, "materials": [material],
            "agreed": True, "separable": separable, "share": share, "textured": True, "base_colour": None,
            "colour_rgb": rgb}


def _grey_rgb(name="light grey"):
    return [round(CL.linear_to_srgb(c) * 255) for c in CL.linear_rgb(name)]


def _catalog(*models):
    base = json.loads((ROOT / "wenart" / "furniture" / "catalog.json").read_text(encoding="utf-8"))
    return C.Catalog(C.merge(base, {"entries": list(models)}, source="test"))


def _piece(ftype="sofa", size=(2.2, 0.9), **extra):
    return dict({"id": "f1", "type": ftype, "level_id": "L0", "room_id": "r", "source": "from_documents",
                 "footprint": {"center": [1.0, 1.0], "size": list(size), "rotation_deg": 0.0}, "front_deg": 270.0,
                 "height": None, "status": "verified", "evidence": [{"file": "x", "method": "vector",
                                                                     "confidence": 1.0}]}, **extra)


# --------------------------------------------------------------------------
# What a model can show
# --------------------------------------------------------------------------

def test_look_of_reads_tags_recolour_and_colour():
    glass = _model("t1", "table_coffee", material_tags=["glass", "metal"])
    wood = _model("t2", "table_coffee", material_tags=["wood"])
    unjudged = _model("t3", "table_coffee")
    design = {"material_tags": ["glass"]}
    assert fit.look_of(glass, "table_coffee", design) == ({"tags": ["glass"]}, None)
    assert fit.look_of(wood, "table_coffee", design)[1] == "material tags ['wood'] lack glass"
    assert "no judged material tags" in fit.look_of(unjudged, "table_coffee", design)[1]
    rec = _model("s1", recolourable_fabric=True, material_slots=[_slot(0, "fabric", name="Fabric"), _slot(1, "wood")])
    look, why = fit.look_of(rec, "sofa", {"fabric_colour": "light grey"})
    assert why is None and look["recolour"] == {"fabric": {"colour": "light grey",
                                                           "slots": [{"index": 0, "name": "Fabric"}]}}
    same = _model("s2", material_slots=[_slot(0, "fabric", rgb=_grey_rgb(), separable=False)])
    look, why = fit.look_of(same, "sofa", {"fabric_colour": "light grey"})
    assert look["colour_match"]["colour"] == "light grey" and look["colour_match"]["delta_e"] < 1.0
    red = _model("s3", material_slots=[_slot(0, "fabric", rgb=[160, 30, 30], separable=False)])
    assert "Delta E away" in fit.look_of(red, "sofa", {"fabric_colour": "light grey"})[1]
    assert "no recolourable fabric slot" in fit.look_of(_model("s4"), "sofa", {"fabric_colour": "light grey"})[1]
    # A small separable fabric slot is not recoloured (below RECOLOUR_MIN_SHARE).
    tiny = _model("s5", recolourable_fabric=True, material_slots=[_slot(0, "fabric", share=0.01)])
    assert fit.look_of(tiny, "sofa", {"fabric_colour": "light grey"})[0] is None
    oak = _model("s6", recolourable_wood=True, material_slots=[_slot(0, "wood", name="Legs")])
    look, _ = fit.look_of(oak, "sofa", {"wood": "wood_veneer_oak_light"})
    assert look["recolour"]["wood"]["slots"] == [{"index": 0, "name": "Legs"}]
    from wenart.style import vocabulary as V
    assert look["recolour"]["wood"]["rgb"] == V.FURNITURE_MATERIALS["wood_veneer_oak_light"]["flat"]
    assert fit.look_of(_model("s7"), "sofa", {"wood": "wood_veneer_oak_light"}) == ({}, None)   # wood never skips
    assert fit.colour_distance([211, 211, 211], "light grey") == pytest.approx(0.0, abs=0.01)
    assert fit.colour_distance(None, "light grey") is None and fit.colour_distance([1, 2, 3], "nocolour") is None


def test_fit_piece_takes_the_model_that_shows_the_design():
    plain = _model("a_plain", quality=[5, 5])
    rec = _model("b_rec", quality=[3, 3], recolourable_fabric=True,
                 material_slots=[_slot(0, "fabric", name="Fabric")], material_tags=["fabric"])
    catalog = _catalog(plain, rec)
    free = fit.fit_piece(_piece(), catalog)
    assert free["asset_id"] == "a_plain" and "recolour" not in free         # no design: the fit v2 order
    asset = fit.fit_piece(_piece(), catalog, design={"fabric_colour": "light grey"})
    assert asset["asset_id"] == "b_rec" and asset["recolour"]["fabric"]["colour"] == "light grey"
    assert asset["material_slots"][0]["name"] == "Fabric" and asset["recolourable_fabric"] is True
    assert {"id": "a_plain", "reason": asset["excluded"][0]["reason"]} in asset["excluded"]
    none = fit.fit_piece(_piece(), _catalog(plain), design={"fabric_colour": "light grey"})
    assert none["method"] == "parametric" and "can show the design" in none["fallback_reason"]
    tags = fit.fit_piece(_piece("table_coffee", (1.0, 0.6)),
                         _catalog(_model("g1", "table_coffee", (1.0, 0.6, 0.45), material_tags=["glass"]),
                                  _model("w1", "table_coffee", (1.0, 0.6, 0.45), quality=[5, 5],
                                         material_tags=["wood"])),
                         design={"material_tags": ["glass"]})
    assert tags["asset_id"] == "g1" and tags["material_tags_asked"] == ["glass"]


def test_fit_building_reads_the_design_or_the_style():
    rec = _model("b_rec", recolourable_fabric=True, material_slots=[_slot(0, "fabric")])
    catalog = _catalog(_model("a_plain", quality=[5, 5]), rec)
    building = {"furniture": [_piece()], "decor": []}
    style = {"furniture": {"by_type": {"sofa": {"fabric_colour": "light grey"}}}}
    assert fit.fit_building(building, catalog)["furniture"][0]["asset"]["asset_id"] == "a_plain"
    assert fit.fit_building(building, catalog, style=style)["furniture"][0]["asset"]["asset_id"] == "b_rec"
    with_design = {"furniture": [_piece(design={"fabric_colour": "light grey"})], "decor": []}
    assert fit.fit_building(with_design, catalog)["furniture"][0]["asset"]["asset_id"] == "b_rec"
    report = fit.fit_report(dict(fit.fit_building(with_design, catalog), project={"id": "p"}))
    assert "## Recolour and colour matches" in report and "recoloured light grey" in report
    for field in ("material_slots", "material_tags", "recolourable_fabric", "recolourable_wood", "species", "pot"):
        assert field in fit.GLB_ASSET_FIELDS


def test_large_plants_prefer_their_species():
    def plant(mid, species):
        e = _model(mid, "decor_plant_large", (0.6, 0.6, 1.6), species=species)
        e.update(kind="decor", decor_type="plant_large")
        return e

    base = json.loads((ROOT / "wenart" / "furniture" / "catalog.json").read_text(encoding="utf-8"))
    catalog = C.Catalog(C.merge(base, {"entries": [], "decor": [plant("p_palm", "palm"), plant("p_fern", "fern"),
                                                                 plant("p_mon", "monstera")]}, source="test"))
    item = {"id": "dec_1", "type": "plant_large", "size": [0.6, 0.6, 1.6], "species": "fern"}
    asset = fit.fit_decor_item(item, catalog)
    assert asset["asset_id"] == "p_fern" and asset["species"] == "fern"
    other = fit.fit_decor_item(dict(item, species="olive"), catalog)
    assert other["asset_id"] in ("p_palm", "p_fern", "p_mon")                 # none of that species: any
    with pytest.raises(C.CatalogError):
        C.validate({"entries": [], "decor": [plant("p_bad", "cactus")]}, complete=False)


# --------------------------------------------------------------------------
# Refit: the locked check
# --------------------------------------------------------------------------

def test_fit_cli_runs_the_locked_check(tmp_path):
    src = ROOT / "docs" / "examples" / "building_m10.example.json"
    building = json.loads(src.read_text(encoding="utf-8"))
    path = tmp_path / "building_final.json"
    path.write_text(json.dumps(building), encoding="utf-8")
    out = tmp_path / "fitted.json"
    completion = tmp_path / "completion.json"
    completion.write_text(json.dumps({"settings": {"furnished_rooms": "complete"}, "rooms": []}), encoding="utf-8")
    args = [str(path), "--out", str(out), "--source", str(src), "--completion", str(completion)]
    assert fit.main(args) == 0 and out.is_file()
    assert "Locked check" in (tmp_path / "fitted_report.md").read_text(encoding="utf-8")
    moved = copy.deepcopy(building)
    drawn = next(f for f in moved["furniture"] if f["type"] == "bed_double")
    drawn["footprint"]["center"][0] += 0.3
    path.write_text(json.dumps(moved), encoding="utf-8")
    out.unlink()
    assert fit.main(args) == 1 and not out.is_file()
    report = (tmp_path / "fitted_report.md").read_text(encoding="utf-8")
    assert "anchor" in report and drawn["id"] in report
    problems, how = fit.locked_check(src, moved)
    assert problems and "no completion.json" in how


# --------------------------------------------------------------------------
# The scene builder recolours a library model's slots
# --------------------------------------------------------------------------

def test_recolour_plan_maps_slots_by_name():
    plan, missing = F.recolour_plan(["Fabric", "Wood.001", None],
                                    {"fabric": {"colour": "light grey", "slots": [{"index": 0, "name": "Fabric"}]},
                                     "wood": {"colour": "wood_veneer_oak", "rgb": [0.6, 0.4, 0.2],
                                              "slots": [{"index": 1, "name": "Wood"}, {"index": 2, "name": "Leg"}]}})
    assert plan == {"Fabric": ("fabric", "light grey", None), "Wood.001": ("wood", "wood_veneer_oak", [0.6, 0.4, 0.2])}
    assert missing == ["wood slot 2 (Leg)"]
    one, _ = F.recolour_plan(["Material_0"], {"fabric": {"colour": "sage", "slots": [{"index": 0, "name": "x"}]}})
    assert one == {"Material_0": ("fabric", "sage", None)}                   # a one-material model: its index 0


GLB_SCRIPT = textwrap.dedent("""
    import bpy, sys
    out = sys.argv[sys.argv.index("--") + 1]
    bpy.ops.wm.read_factory_settings(use_empty=True)
    def box(name, lo, hi, colour):
        verts = [(x, y, z) for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])]
        faces = [[0, 1, 3, 2], [4, 6, 7, 5], [0, 4, 5, 1], [2, 3, 7, 6], [0, 2, 6, 4], [1, 5, 7, 3]]
        me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
        mat = bpy.data.materials.new(name); mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = colour
        me.materials.append(mat)
        ob = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(ob)
    box("Fabric", (-1.1, -0.45, 0.1), (1.1, 0.45, 0.85), (0.8, 0.1, 0.1, 1.0))
    box("Wood", (-1.1, -0.45, 0.0), (1.1, 0.45, 0.1), (0.3, 0.2, 0.1, 1.0))
    bpy.ops.export_scene.gltf(filepath=out, export_format="GLB", export_yup=True, export_apply=True)
""")
DUMP = textwrap.dedent("""
    import bpy, json, sys
    out = sys.argv[sys.argv.index("--") + 1]
    rows = {}
    for m in bpy.data.materials:
        bsdf = next((n for n in m.node_tree.nodes if n.bl_idname == "ShaderNodeBsdfPrincipled"), None) \\
            if m.use_nodes and m.node_tree else None
        rows[m.name] = list(bsdf.inputs["Base Color"].default_value)[:3] if bsdf else None
    json.dump(rows, open(out, "w"))
""")


@needs_blender
def test_scene_recolours_the_fabric_slot_of_a_library_sofa(tmp_path):
    pytest.importorskip("jsonschema")
    assets = tmp_path / "assets"
    glb = assets / "models" / "sofa_test" / "sofa_test.glb"
    glb.parent.mkdir(parents=True)
    (tmp_path / "make.py").write_text(GLB_SCRIPT, encoding="utf-8")
    cli.run_blender(tmp_path / "make.py", [str(glb)])
    ev = [{"file": "x.dxf", "method": "vector", "confidence": 1.0}]
    walls = [{"id": f"w{i}", "level_id": "L0", "start": s, "end": e, "thickness": 0.2, "status": "verified",
              "evidence": ev, "exterior": True}
             for i, (s, e) in enumerate((([-0.1, -0.1], [5.1, -0.1]), ([5.1, -0.1], [5.1, 4.1]),
                                         ([5.1, 4.1], [-0.1, 4.1]), ([-0.1, 4.1], [-0.1, -0.1])))]
    piece = _piece(id="f_sofa")
    piece.update(room_id="r", footprint={"center": [2.5, 3.0], "size": [2.2, 0.9], "rotation_deg": 0.0},
                 asset={"library": "polyhaven", "asset_id": "sofa_test", "licence": "CC0", "method": "library",
                        "fit_scale": [1.0, 1.0, 1.0], "bbox_m": [2.2, 0.9, 0.85],
                        "file": "models/sofa_test/sofa_test.glb",
                        "front_axis": "-Y", "up_axis": "+Z", "origin_offset": [0.0, 0.0, 0.0],
                        "recolour": {"fabric": {"colour": "light grey", "slots": [{"index": 0, "name": "Fabric"}]},
                                     "wood": {"colour": "wood_veneer_walnut", "rgb": [0.25, 0.14, 0.08],
                                              "slots": [{"index": 1, "name": "Wood"}, {"index": 2, "name": "Gone"}]}}})
    building = {"schema_version": "0.1", "status": "ok", "project": {"id": "recolour-test"},
                "levels": [{"id": "L0", "elevation": 0.0, "ceiling_height": 2.7}], "walls": walls, "openings": [],
                "rooms": [{"id": "r", "level_id": "L0", "label": "Living", "room_type": "living", "status": "verified",
                           "polygon": [[0, 0], [5, 0], [5, 4], [0, 4]], "evidence": ev, "area_computed": 20.0,
                           "has_documented_furniture": True}],
                "furniture": [piece], "decor": [], "warnings": [], "unverified": []}
    (tmp_path / "building.json").write_text(json.dumps(building), encoding="utf-8")
    out = tmp_path / "scene"
    cli.run_blender(Path(cli.BUILD_SCRIPT), ["--building", str(tmp_path / "building.json"), "--assets", str(assets),
                                             "--out", str(out), "--no-textures", "--no-preview", "--no-glb"],
                    log_path=out / "build.log")
    manifest = json.loads((out / "scene_manifest.json").read_text(encoding="utf-8"))
    entry = next(o for o in manifest["objects"] if o["name"] == "furn_f_sofa")
    assert entry["method"] == "library"
    applied = {a["part"]: a for a in entry["recolour"]["applied"]}
    assert set(applied) == {"fabric", "wood"} and entry["recolour"]["missing"] == ["wood slot 2 (Gone)"]
    assert applied["fabric"]["copy"] in entry["materials"] and applied["fabric"]["copy"].startswith("Fabric__light")
    assert any("recolour slot wood slot 2 (Gone)" in w for w in manifest["warnings"])
    (tmp_path / "dump.py").write_text(DUMP, encoding="utf-8")
    cli.run_blender(tmp_path / "dump.py", [str(tmp_path / "mats.json")], blend=str(out / "scene.blend"))
    colours = json.loads((tmp_path / "mats.json").read_text(encoding="utf-8"))
    assert colours[applied["fabric"]["copy"]] == pytest.approx(CL.linear_rgb("light grey"), abs=1e-3)
    assert colours[applied["wood"]["copy"]] == pytest.approx([0.25, 0.14, 0.08], abs=1e-3)
    assert applied["fabric"]["material"] == "Fabric"           # the glTF material (unused now: not saved)
