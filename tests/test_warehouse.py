"""The 3D Warehouse layer (the user's request of 23 Oct 2026; ``wenart/assets/warehouse.py``): the zip extraction,
the type from the folder and file names (unmapped models listed, never guessed), the unit, up axis and type from the
box, the SketchUp fix-ups written into the GLB (origin on the floor centre, double-sided faces, roughness and metallic
by material name and type), the catalogue entry and its licence fields (relaxed mode only), the growth steps
``ingest --source 3dwh`` and ``catalogue --only 3dwh`` on a small zip, and the m13.2 audit question with the logo
fields. Modelled on the HSSD tests (``tests/test_m13_library.py``); no network, no GPU."""
from __future__ import annotations

import json
import math
import struct
import zipfile
from argparse import Namespace
from pathlib import Path

import pytest

from test_library_growth_p4 import box_mesh, chair_mesh, gltf_doc, write_glb
from wenart.assets import fetch
from wenart.assets import warehouse as W
from wenart.assets.audit import ask as A
from wenart.assets.audit import decide as D
from wenart.assets.audit import glbmesh as GM
from wenart.assets.audit import growth_entries as GE
from wenart.assets.audit import growth_run as RUN
from wenart.assets.audit import items as I
from wenart.blender import furniture as BF
from wenart.furniture import catalog as C

ROOT = Path(__file__).resolve().parents[1]
STAMP = "2026-10-23T16:00:00Z"
IN = 1.0 / 0.0254                         # metres -> inches


def job(raw: Path, assets: Path, rel: str, cache: Path) -> dict:
    return {"id": W.uid_of(rel), "rel": rel, "raw": str(raw), "assets": str(assets), "cache": str(cache)}


# --------------------------------------------------------------------------
# Approval, extraction, listing
# --------------------------------------------------------------------------

def test_the_committed_approval_takes_the_whole_zip_and_others_are_refused(tmp_path):
    doc = W.approval(ROOT / "results" / "library")
    assert doc["rule"] == "whole_zip" and doc["drive_file_id"] == W.DRIVE_FILE_ID == "1nSHF5dvjLLcpruowus8zZUx8kSiDxkjD"
    assert doc["bytes"] == W.ZIP_BYTES and doc["licence"] == W.LICENCE and doc["licence_flag"] == "non_commercial"
    with pytest.raises(PermissionError, match="not found"):
        W.approval(tmp_path)
    (tmp_path / "growth").mkdir()
    (tmp_path / "growth" / "approved_3dwh.json").write_text(json.dumps(dict(doc, drive_file_id="another")))
    with pytest.raises(PermissionError, match="not the whole"):
        W.approval(tmp_path)
    (tmp_path / "growth" / "approved_3dwh.json").write_text(json.dumps(dict(doc, approved_by="")))
    with pytest.raises(PermissionError, match="missing approved_by"):
        W.approval(tmp_path)
    assert W.download_url() == ("https://drive.usercontent.google.com/download?id=1nSHF5dvjLLcpruowus8zZUx8kSiDxkjD"
                                "&export=download&confirm=t")


def test_extract_takes_only_safe_glb_members_and_resumes(tmp_path):
    src = write_glb(tmp_path / "src" / "a.glb", *box_mesh(1, 1, 1))
    zpath = tmp_path / "z.zip"
    data = src.read_bytes()
    with zipfile.ZipFile(zpath, "w") as zf:
        zf.write(src, "3D Warehouse Furniture/Furniture/Sofas/Good sofa.glb")
        for bad in ("../evil.glb", "/abs/evil.glb", "__MACOSX/Furniture/._Good sofa.glb", "C:/win/evil.glb"):
            zf.writestr(zipfile.ZipInfo(bad), data)                     # raw names (write() would clean them)
        zf.writestr("3D Warehouse Furniture/readme.txt", "x")
        zf.writestr("3D Warehouse Furniture/Furniture/Sofas/", "")
        link = zipfile.ZipInfo("3D Warehouse Furniture/link.glb")
        link.external_attr = (0o120777 << 16)
        zf.writestr(link, "/etc/passwd")
    raw = tmp_path / "raw"
    rec = W.extract(zpath, raw, log=lambda *a: None)
    assert rec["glb"] == 1 and rec["extracted"] == 1 and rec["other"] == {".txt": 1}
    assert sorted(rec["refused"]) == sorted(["../evil.glb", "/abs/evil.glb", "__MACOSX/Furniture/._Good sofa.glb",
                                             "C:/win/evil.glb", "3D Warehouse Furniture/link.glb"])
    good = "3D Warehouse Furniture/Furniture/Sofas/Good sofa.glb"
    files = sorted(p.name for p in raw.rglob("*") if p.is_file())
    assert files == sorted([f"{W.uid_of(good)}.glb", W.MEMBERS])         # the uid file and the member map only
    assert not (tmp_path / "evil.glb").exists()
    again = W.extract(zpath, raw, log=lambda *a: None)
    assert again["kept"] == 1 and again["extracted"] == 0
    listing = W.list_glbs(raw)
    assert [r["rel"] for r in listing] == [good] and listing[0]["stem"] == "Good sofa"
    assert listing[0]["id"] == W.uid_of(good) and len(listing[0]["id"]) == len("3dwh_") + 24
    assert listing[0]["file"] == f"{W.uid_of(good)}.glb"
    assert listing[0]["folders"] == ["3D Warehouse Furniture", "Furniture", "Sofas"]


def test_utf8_names_without_the_zip_flag_and_names_over_255_bytes_extract(tmp_path):
    """The first 3dwh pod (23 Oct 2026): the zip stores UTF-8 names without the UTF-8 flag (Python reads them as
    CP437: a Russian lamp name became mojibake) and one model folder passed the 255-byte name limit."""
    src = write_glb(tmp_path / "src" / "a.glb", *box_mesh(0.6, 0.6, 0.5))
    lamp = ("3D Warehouse Furniture/Lamps/lamp chandelier pendant light светильник лампа люстра подвесной свет "
            "[2693fa00]/model.glb")
    long_name = "3D Warehouse Furniture/Sofas/" + "очень длинный диван " * 12 + "[abcdef12]/model.glb"
    assert len(long_name.split("/")[2].encode("utf-8")) > 255
    zpath = tmp_path / "z.zip"
    with zipfile.ZipFile(zpath, "w") as zf:
        for i, name in enumerate((lamp, long_name)):
            zf.write(src, f"{i}" * len(name.encode("utf-8")))         # an ASCII name of the same byte length
    data = zpath.read_bytes()
    for i, name in enumerate((lamp, long_name)):
        data = data.replace(f"{i}".encode() * len(name.encode("utf-8")), name.encode("utf-8"))
    zpath.write_bytes(data)                                             # UTF-8 names, flag bit 11 not set
    with zipfile.ZipFile(zpath) as zf:
        assert not zf.infolist()[0].flag_bits & W.UTF8_FLAG and zf.infolist()[0].filename != lamp
        assert W.member_name(zf.infolist()[0]) == lamp
    raw = tmp_path / "glb"
    rec = W.extract(zpath, raw, log=lambda *a: None)
    assert rec["glb"] == 2 and rec["extracted"] == 2 and not rec["refused"]
    listing = W.list_glbs(raw)
    assert sorted(r["rel"] for r in listing) == sorted([lamp, long_name])
    r = W.name_type(lamp)
    assert r["mapped"] and r["candidates"][0] == "pendant_light" and r["where"] == "file"
    assert r["title"] == "lamp chandelier pendant light светильник лампа люстра подвесной свет"
    long_r = W.name_type(long_name)
    assert long_r["candidates"][0] == "sofa" and len(long_r["title"]) <= W.TITLE_MAX
    rec = W.process(job(raw, tmp_path / "assets", lamp, tmp_path / "c") | {"file": listing[0]["file"]
                                                                            if listing[0]["rel"] == lamp
                                                                            else listing[1]["file"]})
    assert rec["ok"] and rec["type"] == "pendant_light", rec


# --------------------------------------------------------------------------
# Types from names
# --------------------------------------------------------------------------

@pytest.mark.parametrize("rel, group, first, where", [
    ("3D Warehouse Furniture/Furniture/Sofas/Model_123.glb", "furniture", "sofa", "folder Sofas"),
    ("3D Warehouse Furniture/Furniture/IKEA_KIVIK_corner_sofa.glb", "furniture", "sofa_corner", "file"),
    ("3D Warehouse Furniture/Trees/Olive tree big.glb", "vegetation", "tree", "group folder Trees"),
    ("3D Warehouse Furniture/Trees/Boxwood_bush.glb", "vegetation", "shrub", "file"),
    ("3D Warehouse Furniture/Trees/X1.glb", "vegetation", "tree", "group folder Trees"),
    ("3D Warehouse Furniture/Doors/Door_80x210_oak.glb", "door", "door", "file"),
    ("3D Warehouse Furniture/Doors & Windows/Window 120x150.glb", "window", "window", "file"),
    ("3D Warehouse Furniture/Decor/Olive tree in pot.glb", "furniture", "potted_plant", "file"),
    ("3D Warehouse Furniture/Furniture/Wardrobe with sliding doors.glb", "furniture", "wardrobe", "file"),
    ("3D Warehouse Furniture/Decor/Vases/thing.glb", "decor", "vase", "folder Vases"),
    ("Bedside table lamp.glb", "furniture", "floor_lamp", "file"),        # the head noun (a lamp) leads
    ("Sofa with cushions.glb", "furniture", "sofa", "file"),
    ("Palm tree.glb", "vegetation", "palm", "file"),
])
def test_types_come_from_the_folder_and_file_names(rel, group, first, where):
    r = W.name_type(rel)
    assert r["mapped"] and r["group"] == group and r["candidates"][0] == first and r["where"] == where, r


def test_a_file_named_model_takes_its_folder_name():
    r = W.name_type("3D Warehouse Furniture/Beds/Queen bed Malm [00aa11bb]/model.glb")
    assert r["candidates"] == ["bed_double"]                     # "queen bed" names the double bed
    assert r["where"] == "file" and r["title"] == "Queen bed Malm"
    r = W.name_type("3D Warehouse Furniture/Chairs/X 12 [00aa11bb]/model.glb")       # the folder above names it
    assert r["candidates"][0] == "chair" and r["where"] == "folder Chairs" and r["title"] == "X 12 (Chairs)"
    assert W.generic_stem("Model") and W.generic_stem("scene") and not W.generic_stem("Model chair")
    assert not W.generic_stem("Model_2")
    assert W.clean_title("Sofa_IKEA [2693fa00]") == "Sofa IKEA"


def test_second_pod_typing_fixes_of_the_first_pod_findings():
    """The first full 3dwh pod (23 Oct 2026): the zip's top folder "3D Warehouse Furniture" put every model into the
    furniture group (a bathroom door became a toilet, trees outside a tree folder were left out), the Doors folder holds
    cabinets named by their doors, an outdoor olive tree read as a potted plant, cooktops named no type."""
    r = W.name_type("3D Warehouse Furniture/Bathroom/Bathroom door toilet door [674e476a]/model.glb")
    assert r["group"] == "door" and r["candidates"][0] == "door"
    r = W.name_type("3D Warehouse Furniture/Doors/Alfreton 4 Door Cabinet [598acd0a]/model.glb")
    assert r["group"] == "furniture" and r["candidates"][0] == "wardrobe" and "door" not in r["candidates"]
    assert W.name_type("3D Warehouse Furniture/Doors/Oak door [11223344]/model.glb")["candidates"] == ["door"]
    r = W.name_type("3D Warehouse Furniture/Outdoor/Olive tree [aa112233]/model.glb")
    assert r["candidates"][-1] == "tree" and r["candidates"][0] == "potted_plant"
    assert W.choose(r["candidates"], (4.0, 4.0, 6.0))["type"] == "tree"
    assert W.choose(r["candidates"], (0.6, 0.6, 1.6))["type"] == "potted_plant"
    assert "tree" not in W.name_type("3D Warehouse Furniture/Decor/Olive tree in pot [aa]/model.glb")["candidates"]
    assert W.name_type("3D Warehouse Furniture/Kitchen/Cooktop Inox Fischer [27d99bbb]/model.glb")["candidates"] == \
        ["stove"]
    assert W.folder_group(["3D Warehouse Furniture"]) == ("furniture", "3D Warehouse Furniture")   # why it is cut


def test_a_glb_whose_json_does_not_parse_is_dropped_not_failed(tmp_path):
    raw = tmp_path / "raw"
    js = b'{"asset": {"version": "2.0"}, "accessors": [{"min": [nan, 0, 0]}]}  '
    data = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js)) + struct.pack("<II", len(js), 0x4E4F534A) + js
    (raw / "Chairs").mkdir(parents=True)
    (raw / "Chairs" / "Chair x.glb").write_bytes(data + b" " * 300)
    r = W.process(job(raw, tmp_path / "assets", "Chairs/Chair x.glb", tmp_path / "c"))
    assert not r["ok"] and "does not parse" in r["dropped"] and not r.get("error")


def test_a_cached_fix_is_reused_only_while_the_name_typing_is_the_same(tmp_path, monkeypatch):
    raw, assets, cache = tmp_path / "raw", tmp_path / "assets", tmp_path / "cache"
    rel = "Furniture/Sofas/Big sofa.glb"
    write_glb(raw / rel, *box_mesh(2.1, 0.9, 0.85))
    assert W.process(job(raw, assets, rel, cache))["ok"]
    assert W.process(job(raw, assets, rel, cache)).get("kept")
    real = W.name_type
    monkeypatch.setattr(W, "name_type", lambda r: dict(real(r), candidates=["bench", "sofa"]))
    again = W.process(job(raw, assets, rel, cache))
    assert again["ok"] and not again.get("kept") and again["names"]["candidates"] == ["bench", "sofa"]


def test_unmapped_names_go_to_review_and_titles_carry_only_a_type_folder():
    for rel in ("3D Warehouse Furniture/Furniture/abc.glb", "3D Warehouse Furniture/Furniture/Coat tree.glb",
                "Thing 7.glb"):
        r = W.name_type(rel)
        assert not r["mapped"] and r["candidates"] == [], rel
    # the file name names no type: the title carries the folder that does, never the root folder (the root's word
    # "Warehouse" is an other_use flag of the audit's title check)
    r = W.name_type("3D Warehouse Furniture/Furniture/Sofas/Model_123.glb")
    assert r["title"] == "Model 123 (Sofas)" and "Warehouse" not in r["title"]
    assert W.name_type("3D Warehouse Furniture/Furniture/Big_sofa.glb")["title"] == "Big sofa"
    assert W.clean_title("Sofa_IKEA__Kivik - ") == "Sofa IKEA Kivik"


# --------------------------------------------------------------------------
# Unit, up axis and type from the box
# --------------------------------------------------------------------------

def test_choose_reads_metres_inches_centimetres_and_the_z_up_export():
    m = W.choose(["sofa"], (2.1, 0.9, 0.85))
    assert (m["unit"], m["up_fix"], m["fits"], m["units_known"]) == ("metres", None, True, True)
    inch = W.choose(["sofa"], (2.1 * IN, 0.9 * IN, 0.85 * IN))
    assert inch["unit"] == "inches" and inch["fits"] and inch["box_m"] == [2.1, 0.9, 0.85]
    assert W.choose(["wardrobe"], (100.0, 60.0, 210.0))["unit"] == "centimetres"
    # a wardrobe exported Z-up without the glTF turn: the importer frame shows it lying on its back
    z = W.choose(["wardrobe"], (1.0, 2.1, 0.6))
    assert z["up_fix"] == "z_up" and z["unit"] == "metres" and z["box_m"] == [1.0, 0.6, 2.1]
    # the size picks between the name's candidates (a bed: single or double); the name's order breaks ties
    assert W.choose(["bed_single", "bed_double"], (1.6, 2.1, 0.9))["type"] == "bed_double"
    assert W.choose(["bed_single", "bed_double"], (0.95, 2.0, 0.9))["type"] == "bed_single"
    assert W.choose(["bed_single", "bed_double"], (0.95, 2.0, 0.9))["type_from"] == "name+size"
    assert W.choose(["door"], (0.9, 0.05, 2.1))["fits"] and W.choose(["tree"], (4.0, 4.0, 7.0))["fits"]


def test_choose_keeps_metres_for_a_box_no_unit_fits():
    odd = W.choose(["sofa"], (0.2, 0.2, 3.0))          # a pole: no unit makes it a sofa
    assert not odd["fits"] and not odd["units_known"] and odd["unit"] == "metres" and odd["up_fix"] is None
    assert odd["error"] > W.FIT_TOL and any(t["unit"] == "inches" for t in odd["tried"])
    # far too large in metres but no unit fits exactly: the clearly better unit is taken, units still unknown
    big = W.choose(["table_dining"], (180.0 * 1.6, 90.0 * 1.6, 75.0 * 1.6))
    assert big["unit"] == "centimetres" and not big["units_known"]


# --------------------------------------------------------------------------
# Materials
# --------------------------------------------------------------------------

def test_roughness_and_metallic_by_material_name_then_type():
    assert W.material_rule("Translucent_Glass_Gray", "sofa") == ("glass", 0.05, 0.0)
    assert W.material_rule("Metal_Corrogated_Shiny", "sofa") == ("metal", 0.35, 1.0)
    assert W.material_rule("Chrome", "toilet") == ("chrome", 0.12, 1.0)
    assert W.material_rule("Wood_Floor_Light", "x") == ("wood", 0.55, 0.0)
    assert W.material_rule("Fabric_Carpet_Loop", "x") == ("fabric", 0.9, 0.0)
    assert W.material_rule("Color_A01", "toilet") == ("type:toilet", 0.15, 0.0)
    assert W.material_rule("Material3", "sofa") == ("type:sofa", 0.85, 0.0)
    assert W.material_rule("FrontColor", "unknown_type") == ("default", W.DEFAULT_ROUGHNESS, 0.0)
    assert W.material_rule("Camel leather", "x") == ("leather", 0.45, 0.0)      # "cam" (glass) is a whole word only


def test_fix_materials_sets_factors_double_sides_and_keeps_texture_driven_ones():
    doc = {"materials": [{"name": "Color_A01"},
                         {"name": "Glass", "pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 0.3]}},
                         {"name": "Textured", "doubleSided": True,
                          "pbrMetallicRoughness": {"metallicRoughnessTexture": {"index": 0}, "metallicFactor": 1}},
                         {"name": "Old", "extensions": {"KHR_materials_pbrSpecularGlossiness": {}}}],
           "meshes": [{"primitives": [{"attributes": {}, "material": 0}, {"attributes": {}}]}]}
    rec = W.fix_materials(doc, "toilet")
    m = doc["materials"]
    assert all(x["doubleSided"] for x in m) and rec["double_sided"] == 3
    assert m[0]["pbrMetallicRoughness"] == {"roughnessFactor": 0.15, "metallicFactor": 0.0}
    assert m[1]["pbrMetallicRoughness"]["roughnessFactor"] == 0.05 and m[1]["alphaMode"] == "BLEND"
    assert m[2]["pbrMetallicRoughness"] == {"metallicRoughnessTexture": {"index": 0}, "metallicFactor": 1}
    assert "roughnessFactor" not in m[3]["pbrMetallicRoughness"]
    assert m[4]["name"] == W.DEFAULT_MATERIAL and doc["meshes"][0]["primitives"][1]["material"] == 4
    assert rec["default_added"] == 1 and rec["blend"] == 1
    assert rec["materials"][0]["was"] == {"metallic": "default 1.0", "roughness": "default 1.0"}


# --------------------------------------------------------------------------
# The fix-up and one model end to end
# --------------------------------------------------------------------------

def test_process_fixes_an_inch_model_onto_the_floor_centre_and_keeps_the_binary(tmp_path):
    raw, assets, cache = tmp_path / "raw", tmp_path / "assets", tmp_path / "cache"
    rel = "3D Warehouse Furniture/Furniture/Sofas/Big sofa.glb"
    src = write_glb(raw / rel, *box_mesh(2.1 * IN, 0.9 * IN, 0.85 * IN, x0=50, y0=-20, z0=7))
    rec = W.process(job(raw, assets, rel, cache))
    assert rec["ok"] and rec["type"] == "sofa" and rec["kind"] == "furniture" and rec["glb"] == W.model_rel(rec["id"])
    assert rec["choice"]["unit"] == "inches" and rec["choice"]["units_known"] and "tried" not in rec["choice"]
    m = GM.measure(assets / rec["glb"])
    assert m["bbox_model_m"] == [2.1, 0.9, 0.85]
    assert m["bbox_min_m"] == [-1.05, -0.45, 0.0] and m["bbox_max_m"] == [1.05, 0.45, 0.85]
    _doc0, bin0 = W.read_glb(src)
    doc1, bin1 = W.read_glb(assets / rec["glb"])
    assert bin1[:len(bin0)] == bin0                         # the meshes and textures are byte-identical
    root = doc1["nodes"][doc1["scenes"][0]["nodes"][0]]
    assert root["name"] == W.FIX_ROOT_NAME and root["children"] == [0] and root["scale"] == [0.0254] * 3
    assert doc1["materials"][0]["doubleSided"] and doc1["materials"][0]["pbrMetallicRoughness"]["metallicFactor"] == 0
    assert doc1["asset"]["extras"]["wenart_fix"] == W.FIX_VERSION
    assert rec["sha256"] == W.sha256_file(assets / rec["glb"]) and rec["src_sha256"] == W.sha256_file(src)
    again = W.process(job(raw, assets, rel, cache))
    assert again.get("kept") and again["sha256"] == rec["sha256"]


def test_process_turns_a_z_up_export_upright(tmp_path):
    raw, assets = tmp_path / "raw", tmp_path / "assets"
    rel = "Furniture/Wardrobes/Tall wardrobe.glb"
    write_glb(raw / rel, *box_mesh(1.0, 2.1, 0.6))          # importer frame: lying on its back
    rec = W.process(job(raw, assets, rel, tmp_path / "c"))
    assert rec["ok"] and rec["choice"]["up_fix"] == "z_up"
    m = GM.measure(assets / rec["glb"])
    assert m["bbox_model_m"] == [1.0, 0.6, 2.1] and m["bbox_min_m"][2] == 0.0
    assert math.isclose(m["bbox_min_m"][0], -0.5) and math.isclose(m["bbox_min_m"][1], -0.3)


def test_process_lists_unmapped_external_and_broken_files_as_dropped(tmp_path):
    raw, assets = tmp_path / "raw", tmp_path / "assets"
    write_glb(raw / "Furniture/abc.glb", *box_mesh(1, 1, 1))
    r = W.process(job(raw, assets, "Furniture/abc.glb", tmp_path / "c"))
    assert not r["ok"] and r["mapped"] is False and r["dropped"].startswith("unmapped")
    write_glb(raw / "Furniture/Chair ext.glb", *chair_mesh(), textured=True)       # names t.png outside the GLB
    r = W.process(job(raw, assets, "Furniture/Chair ext.glb", tmp_path / "c"))
    assert not r["ok"] and "external" in r["dropped"]
    (raw / "Furniture/Broken chair.glb").write_bytes(b"not a glb at all" * 40)
    r = W.process(job(raw, assets, "Furniture/Broken chair.glb", tmp_path / "c"))
    assert not r["ok"] and "not a GLB" in r["dropped"] and not r.get("error")
    assert not (assets / "models" / "3dwh").exists() or not list((assets / "models" / "3dwh").glob("*.glb"))


def test_write_glb_round_trip_and_scenes_without_a_scene_list(tmp_path):
    doc, blob = gltf_doc(*box_mesh(1, 1, 1))
    doc.pop("scenes")
    doc.pop("scene")
    n = W.wrap_scenes(doc, {"name": W.FIX_ROOT_NAME, "translation": [0.0, 0.5, 0.0]})
    assert n == 1 and doc["scenes"] == [{"nodes": [1]}] and doc["nodes"][1]["children"] == [0]
    p = W.write_glb(tmp_path / "x.glb", doc, blob)
    data = p.read_bytes()
    assert data[:4] == b"glTF" and struct.unpack_from("<I", data, 8)[0] == len(data) and len(data) % 4 == 0
    assert GM.measure(p)["bbox_min_m"] == [0.0, 0.0, 0.5]           # glTF +0.5 m up = the importer's +Z


# --------------------------------------------------------------------------
# The catalogue entry and the source's licence
# --------------------------------------------------------------------------

def _fixed(tmp_path, rel="Furniture/Sofas/Big sofa.glb", mesh=None):
    raw, assets = tmp_path / "raw", tmp_path / "assets"
    write_glb(raw / rel, *(mesh or box_mesh(2.1 * IN, 0.9 * IN, 0.85 * IN)))
    rec = W.process(job(raw, assets, rel, tmp_path / "c"))
    assert rec["ok"], rec
    return rec, GM.measure(assets / rec["glb"]), assets


def test_the_entry_validates_with_the_licence_fields_of_the_relaxed_mode(tmp_path):
    rec, m, assets = _fixed(tmp_path)
    e = GE.warehouse_entry(rec, m, STAMP)
    C.validate({"entries": [e]}, complete=False)
    assert e["source"] == "3dwh" and e["licence"] == "3DWH-UNREVIEWED" and e["licence_flag"] == "non_commercial"
    assert e["commercial_safe"] is False and e["licence_declared_by"] == "uploader"
    assert e["licence_url"] == "https://3dwarehouse.sketchup.com/" and e["units_known"] is True
    assert e["glb"] == f"models/3dwh/{rec['id']}.glb" and e["bbox_m"] == [2.1, 0.9, 0.85]
    assert e["audit"]["status"] == "pending" and e["3dwh"]["unit"] == "inches" and e["3dwh"]["rel"] == rec["rel"]
    assert "the user's zip" in e["attribution"] and "relaxed licence mode only" in e["attribution"]
    assert e["author"].startswith("unknown 3D Warehouse uploader")
    assert C.licence_text_flag("3DWH-UNREVIEWED") == "non_commercial" and C.licence_flag_of(e) == "non_commercial"
    keep = dict(e, audit={"status": "keep"})
    assert not C.usable(keep, "commercial") and C.usable(keep, "relaxed")
    assert fetch.check_licence("3dwh", e["licence"], kind="models", entry=e) == "3DWH-UNREVIEWED"
    asset = dict(e, library="3dwh", asset_id=e["id"])
    assert BF.licence_refusal(asset) is None
    assert "must carry licence_flag" in BF.licence_refusal(dict(asset, licence_flag="none"))
    assert C.SOURCE_LICENCES["objaverse"] == tuple(C.LICENCE_TEXT_FLAGS)     # Objaverse never takes the 3dwh text
    item = I.item_of(e, "library", "entries")
    assert item["units_known"] and item["source"] == "3dwh"


def test_an_entry_of_unknown_units_says_so_and_a_bed_waits_for_its_mattress(tmp_path):
    rec, m, _assets = _fixed(tmp_path, "Furniture/Sofas/Odd sofa.glb", box_mesh(0.2, 0.2, 3.0))
    e = GE.warehouse_entry(rec, m, STAMP)
    assert e["units_known"] is False and e["unit_note"].startswith("units unknown")
    rec, m, _assets = _fixed(tmp_path, "Furniture/Beds/Double bed.glb", box_mesh(1.6, 2.1, 0.5))
    e = GE.warehouse_entry(rec, m, STAMP)
    assert e["type"] == "bed_double" and e["has_mattress"] is False
    C.validate({"entries": [e]}, complete=False)


def test_build_copies_add_the_source_record_and_note(tmp_path):
    rec, m, _assets = _fixed(tmp_path)
    e = GE.warehouse_entry(rec, m, STAMP)
    lib, _ph, stats = GE.build_copies(I.read_json(I.LIBRARY_PATH), I.read_json(I.POLYHAVEN_PATH), [e])
    assert stats["library"]["added"] == 1 and "3dwh" in lib["sources"] and lib["datasets"]["3dwh"] == W.DATASET
    assert GE.WAREHOUSE_NOTE in lib["notes"]


# --------------------------------------------------------------------------
# The growth steps on a small zip
# --------------------------------------------------------------------------

def _lists(tmp_path) -> Path:
    lists = tmp_path / "lists"
    (lists / "growth").mkdir(parents=True)
    doc = json.loads((ROOT / "results" / "library" / "growth" / "approved_3dwh.json").read_text())
    (lists / "growth" / "approved_3dwh.json").write_text(json.dumps(doc))
    return lists


def _zip(tmp_path) -> Path:
    src = tmp_path / "src"
    members = {
        "3D Warehouse Furniture/Furniture/Sofas/Big sofa.glb": box_mesh(2.1 * IN, 0.9 * IN, 0.85 * IN),
        "3D Warehouse Furniture/Furniture/Chairs/Dining chair.glb": chair_mesh(),
        "3D Warehouse Furniture/Decor/Vases/Tall vase.glb": box_mesh(0.2, 0.2, 0.4),
        "3D Warehouse Furniture/Trees/Olive tree.glb": box_mesh(4.0, 4.0, 6.0, x0=-2, y0=-2),
        "3D Warehouse Furniture/Doors/Door 90.glb": box_mesh(0.9, 0.05, 2.1),
        "3D Warehouse Furniture/Furniture/abc.glb": box_mesh(1, 1, 1),
    }
    zpath = tmp_path / "lib" / "zip" / W.ZIP_NAME
    zpath.parent.mkdir(parents=True)
    with zipfile.ZipFile(zpath, "w") as zf:
        for name, mesh in members.items():
            zf.write(write_glb(src / name, *mesh), name)
    return zpath


def _args(tmp_path, **kw) -> Namespace:
    a = dict(growth=str(tmp_path / "g"), report=None, p4=str(tmp_path / "p4"), p3=str(tmp_path / "p3"),
             assets=str(tmp_path / "assets"), lists=str(_lists(tmp_path) if not (tmp_path / "lists").exists()
                                                         else tmp_path / "lists"),
             source="3dwh", library=str(tmp_path / "lib"), workers=1, size="1k", token_env="HF_TOKEN", m13=False,
             checked_utc=STAMP, only=None)
    a.update(kw)
    return Namespace(**a)


@pytest.mark.parametrize("workers", [1, 2])
def test_ingest_3dwh_writes_the_records_the_review_list_and_the_extras(tmp_path, workers, monkeypatch):
    zpath = _zip(tmp_path)
    monkeypatch.setattr(W, "ZIP_BYTES", zpath.stat().st_size)
    a = _args(tmp_path, workers=workers)
    assert RUN.cmd_ingest(a) == 0
    rep = Path(a.growth) / "report"
    ing = json.loads((rep / "ingest_3dwh.json").read_text())
    assert ing["listed"] == 6 and ing["ok"] == 5 and ing["unmapped"] == 1 and ing["failed"] == 0
    assert ing["by_group"] == {"decor": 1, "door": 1, "furniture": 2, "vegetation": 1}
    assert ing["units"] == {"inches": 1, "metres": 4} and ing["extract"]["glb"] == 6
    review = json.loads((rep / "3dwh_review.json").read_text())
    assert [r["rel"] for r in review["unmapped"]] == ["3D Warehouse Furniture/Furniture/abc.glb"]
    extras = json.loads((rep / "3dwh_extras.json").read_text())["models"]
    assert sorted((x["kind"], x["type"]) for x in extras) == [("opening", "door"), ("vegetation", "tree")]
    tree = next(x for x in extras if x["type"] == "tree")
    assert tree["crown_m"] == 4.0 and tree["height_m"] == 6.0 and tree["fits"]
    for r in ing["records"]:
        if r["ok"]:
            assert (Path(a.assets) / r["glb"]).is_file()
    # the catalogue step: furniture and decor entries, trees and doors as previews, the copies validate
    assert RUN.cmd_catalogue(_args(tmp_path, only="3dwh")) == 0
    nid = json.loads((Path(a.p4) / "audit" / "new_ids.json").read_text())
    assert len(nid["ids"]) == 3 and nid["by_source"] == {"3dwh": 3} and nid["only"] == ["3dwh"]
    assert sorted(p["type"] for p in nid["previews"]) == ["door", "tree"]
    lib = json.loads((Path(a.p4) / "audit" / "catalogue" / "catalog_library.json").read_text())
    new = [e for s in ("entries", "decor") for e in lib[s] if e["id"] in nid["ids"]]
    assert sorted(e["type"] for e in new) == ["chair", "decor_vase", "sofa"]
    C.validate(lib, complete=False)
    cat = json.loads((rep / "catalogue.json").read_text())
    assert any(d["source"] == "3dwh" and "unmapped" in d["reason"] for d in cat["dropped"])
    item = RUN.preview_item(nid["previews"][0], Path(a.assets))
    assert item["source"] == "3dwh" and item["licence"] == W.LICENCE and "3D Warehouse" in item["title"]


def test_ingest_3dwh_refuses_without_approval_or_with_a_cut_zip(tmp_path, monkeypatch, capsys):
    zpath = _zip(tmp_path)
    a = _args(tmp_path)
    (Path(a.lists) / "growth" / "approved_3dwh.json").unlink()
    assert RUN.cmd_ingest(a) == 1 and "refused" in capsys.readouterr().out
    _lists(tmp_path.joinpath("again"))
    a = _args(tmp_path, lists=str(tmp_path / "again" / "lists"))
    monkeypatch.setattr(W, "ZIP_BYTES", zpath.stat().st_size + 1)          # not the Drive file's size
    assert RUN.cmd_ingest(a) == 1 and "incomplete download" in capsys.readouterr().out
    assert not (tmp_path / "lib" / "raw").exists()


def test_catalogue_only_keeps_the_earlier_previews_of_other_sources_and_adds_its_own(tmp_path, monkeypatch):
    zpath = _zip(tmp_path)
    monkeypatch.setattr(W, "ZIP_BYTES", zpath.stat().st_size)
    a = _args(tmp_path)
    assert RUN.cmd_ingest(a) == 0
    earlier = {"ids": ["abo_x"], "previews": [{"id": "infinigen_1", "glb": "models/generated/i.glb"},
                                              {"id": "old_3dwh", "source": "3dwh", "glb": "x.glb"}]}
    RUN.write_json(Path(a.p4) / "audit" / "new_ids.json", earlier)
    assert RUN.cmd_catalogue(_args(tmp_path, only="3dwh")) == 0
    nid = json.loads((Path(a.p4) / "audit" / "new_ids.json").read_text())
    ids = [p["id"] for p in nid["previews"]]
    assert "infinigen_1" in ids and "old_3dwh" not in ids and len(ids) == 3 and "abo_x" in nid["kept_ids"]


# --------------------------------------------------------------------------
# The audit question with the logo fields, and the decision
# --------------------------------------------------------------------------

def test_the_3dwh_question_asks_for_the_logo_and_the_server_schema_follows_the_version():
    cfg = {"version": "m12.1", "version_materials": "m13.1", "version_logo": "m13.2"}
    item = {"id": "3dwh_x", "type": "sofa", "kind": "furniture", "source": "3dwh", "title": "Big sofa"}
    assert A.version_for(item, cfg) == "m13.2" and A.version_for(dict(item, source="hssd"), cfg) == "m13.1"
    assert A.with_logo("m13.2") and not A.with_logo("m13.1") and A.with_materials("m13.2")
    req = A.request_item(item, "../sheets/sofa/3dwh_x.jpg", "abc", [2.1, 0.9, 0.85], "m13.2")
    assert req["context"]["version"] == "m13.2" and "brand_logo" in req["prompt"] and "text_print" in req["prompt"]
    desc = {"version": "m13.2", "task": A.TASK, "system": A.SYSTEM, "prompt": req["prompt"],
            "schema": A.schema("furniture", "m13.2"), "sheet": "abc"}
    assert req["input_sha256"] == A._sha(desc)               # the context version is no part of the input hash
    spec = A.spec_for(False)
    assert {"brand_logo", "text_print", "materials"} <= set(spec.schema_of(req)["properties"])
    # the m12.1 / m13.1 requests keep the m12.1 server schema (unchanged; ask.py docstring: the m13.1 gap)
    m131 = A.request_item(dict(item, source="hssd"), "../s.jpg", "abc", [1, 1, 1], "m13.1")
    assert not {"materials", "brand_logo"} & set(spec.schema_of(m131)["properties"])
    old = {"context": {"kind": "furniture"}}                   # a request written before the context version
    assert "materials" not in spec.schema_of(old)["properties"]
    # an m13.2 model keeps its question when the write step gives it material tags (no re-ask on the next run)
    assert A.version_for(dict(item, material_tags=["fabric"]), cfg) == "m13.2"
    base = {"is_type": True, "type_guess": "sofa", "single_object": True, "real_product": True, "indoor": "indoor",
            "upright": True, "size_plausible": True, "parts_open": False, "styles": [], "quality": 4,
            "front_shown": "front", "has_bedding": None, "has_pillows": None, "has_cushions": False, "contact": None}
    assert A.valid(base, "furniture") and A.valid(dict(base, materials=["fabric"]), "furniture")
    assert A.valid(dict(base, materials=["fabric"], brand_logo=False, text_print=False), "furniture")
    assert not A.valid(dict(base, brand_logo="yes", text_print=False, materials=[]), "furniture")
    assert (ROOT / "wenart" / "assets" / "audit.yaml").read_text().count("version_logo: m13.2") == 1


def test_a_logo_or_a_print_the_vision_check_reads_removes_the_model():
    item = {"id": "3dwh_x", "type": "sofa", "kind": "furniture", "source": "3dwh", "title": "Big sofa"}
    title = [{"check": "title", "status": "ok", "reason": "", "metrics": {"verdict": "match"}}]
    answer = {"is_type": True, "type_guess": "sofa", "single_object": True, "real_product": True, "indoor": "indoor",
              "upright": True, "size_plausible": True, "parts_open": False, "styles": ["modern"], "quality": 4,
              "front_shown": "front", "brand_logo": False, "text_print": False}
    assert D.decide(item, title, answer)["status"] == "keep"
    logo = D.decide(item, title, dict(answer, brand_logo=True))
    assert logo["status"] == "removed" and "logo" in logo["reasons"][0] and "trademarks" in logo["reasons"][0]
    text = D.decide(item, title, dict(answer, text_print=True))
    assert text["status"] == "removed" and "lettering" in text["reasons"][0]


def test_the_source_is_registered_everywhere_the_library_sources_are_listed():
    from wenart.assets import models as M
    from wenart.assets import objaverse as OV
    from wenart.assets.audit import checks as CH
    from wenart.furniture import fit as F
    from wenart.run import copy as CP
    assert "3dwh" in C.SOURCES and C.LIBRARY_SOURCES == M.LIBRARY_SOURCES == CP.LIBRARY_SOURCES
    assert "3dwh" in C.LIBRARY_SOURCES and C.SOURCE_LICENCES["3dwh"] == (W.LICENCE,)
    assert C.LICENCE_DECLARED_BY["3dwh"] == "uploader" and C.SOURCE_TEXT_FLAGS == fetch._SOURCE_FLAGS
    assert F.SOURCE_ORDER == OV.SOURCE_ORDER and F.SOURCE_ORDER.index("3dwh") == F.SOURCE_ORDER.index("objaverse") - 1
    assert CH.SOURCE_RANK["3dwh"] < CH.SOURCE_RANK["objaverse"] and "3dwh" in CP.CREDIT_SOURCES
    assert M.library_relpath("3dwh", W.uid_of("a/b.glb")) == f"models/3dwh/{W.uid_of('a/b.glb')}.glb"
    text = CP.attribution_text("These images", [{"credit": "x", "source": "3dwh", "asset_id": "3dwh_a",
                                                 "licence": W.LICENCE, "licence_flag": "non_commercial",
                                                 "commercial_safe": False, "licence_url": W.LICENCE_URL,
                                                 "pieces": [("f1", "sofa")], "kind": "model", "changes": "x"}],
                                mode="relaxed")
    assert W.notice() in text and "3D Warehouse (the user's zip)" in text
