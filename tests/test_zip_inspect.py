"""CPU tests of wenart.assets.zip_inspect (the beds.zip inspection, 3 Nov 2026): scan, units, typing, verdicts and
the report, without Blender (no conversion, no renders)."""
import json
import struct
import zipfile

import pytest

from wenart.assets import warehouse as WH
from wenart.assets import zip_inspect as ZI


def box_glb(path, w, d, h):
    """A GLB box w x d x h in its own units, glTF Y up (h along Y)."""
    xs, ys, zs = (0.0, w), (0.0, h), (0.0, d)
    verts = [(x, y, z) for x in xs for y in ys for z in zs]
    faces = [(0, 1, 3), (0, 3, 2), (4, 6, 7), (4, 7, 5), (0, 4, 5), (0, 5, 1),
             (2, 3, 7), (2, 7, 6), (0, 2, 6), (0, 6, 4), (1, 5, 7), (1, 7, 3)]
    pos = b"".join(struct.pack("<3f", *v) for v in verts)
    idx = b"".join(struct.pack("<3H", *f) for f in faces)
    idx += b"\x00" * (-len(idx) % 4)
    doc = {"asset": {"version": "2.0", "generator": "test"}, "scene": 0, "scenes": [{"nodes": [0]}],
           "nodes": [{"mesh": 0}], "meshes": [{"primitives": [{"attributes": {"POSITION": 0}, "indices": 1}]}],
           "buffers": [{"byteLength": len(pos) + len(idx)}],
           "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(pos)},
                           {"buffer": 0, "byteOffset": len(pos), "byteLength": 36 * 2}],
           "accessors": [{"bufferView": 0, "componentType": 5126, "count": 8, "type": "VEC3",
                          "min": [0.0, 0.0, 0.0], "max": [w, h, d]},
                         {"bufferView": 1, "componentType": 5123, "count": 36, "type": "SCALAR"}]}
    WH.write_glb(path, doc, pos + idx)


@pytest.fixture
def beds_zip(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    box_glb(src / "a.glb", 63.0, 80.0, 40.0)          # a queen bed in inches (SketchUp)
    box_glb(src / "b.glb", 0.95, 2.0, 0.9)            # a single bed in metres, no type word in its name
    box_glb(src / "c.glb", 5.0, 5.0, 5.0)             # fits no bed in any unit
    z = tmp_path / "beds.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.write(src / "a.glb", "beds/Double bed Oslo [2693fa00]/model.glb")
        zf.write(src / "b.glb", "beds/Model_17.glb")
        zf.write(src / "c.glb", "beds/cube.glb")
        zf.writestr("beds/readme.txt", "hello")
        zf.writestr("../evil.obj", "v 0 0 0")
        zf.writestr("beds/oldbed.max", b"\x00" * 10)
    return z


def test_scan_lists_members_and_refuses_unsafe(beds_zip, tmp_path):
    sc = ZI.scan(beds_zip, tmp_path / "work")
    assert sc["by_ext"][".glb"]["files"] == 3
    assert sc["by_ext"][".txt"]["files"] == 1
    assert "../evil.obj" in sc["refused"]
    assert not (tmp_path / "evil.obj").exists()
    assert len(ZI.model_list(tmp_path / "work")) == 3


def test_run_types_units_and_verdicts(beds_zip, tmp_path):
    out = tmp_path / "out"
    rc = ZI.main(["run", "--zip", str(beds_zip), "--work", str(tmp_path / "work"), "--out", str(out),
                  "--types", "bed_single,bed_double", "--no-render"])
    assert rc == 0
    doc = json.loads((out / "inspect.json").read_text())
    rows = {r["rel"]: r for r in doc["models"]}
    a = rows["beds/Double bed Oslo [2693fa00]/model.glb"]
    assert a["type"] == "bed_double" and a["unit"] == "inches" and a["fits"]
    assert sorted(a["box_m"][:2]) == pytest.approx([1.6002, 2.032], abs=1e-3)
    b = rows["beds/Model_17.glb"]
    assert b["type"] == "bed_single" and b["unit"] == "metres" and b["fits"]
    c = rows["beds/cube.glb"]
    assert c["verdict"] == "not_usable" and not c["fits"]
    # a 12-triangle box is no usable model whatever its size
    assert a["verdict"] == "not_usable" and any("low poly" in n for n in a["notes"])
    report = (out / "report.md").read_text()
    assert "Formats Blender cannot open" in report and ".max" in report
    assert (out / "inspect.csv").is_file()


def fake_skp(version="23.1.340"):
    """A SketchUp-like file: the UTF-16 header with the version and an embedded PNG preview."""
    import io
    from PIL import Image
    buf = io.BytesIO()
    Image.new("RGB", (16, 12), (10, 200, 30)).save(buf, "PNG")
    head = ("﻿SketchUp Model{" + version + "}").encode("utf-16-le")
    return b"\xff\xfe\xff\x0e" + head + b"\x00" * 64 + buf.getvalue() + b"\x00" * 32


def test_nested_zips_skp_and_meta(tmp_path):
    import io
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, "w") as zf:
        zf.writestr("72673.skp", fake_skp())
    src = tmp_path / "g.glb"
    box_glb(src, 1.6, 2.1, 1.0)
    inner2 = io.BytesIO()
    with zipfile.ZipFile(inner2, "w") as zf:
        zf.write(src, "bed.glb")
    z = tmp_path / "beds.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("beds/riva/my-bed/72673.skp.zip", inner.getvalue())
        zf.writestr("beds/riva/my-bed/meta.json", json.dumps({"name": "My Bed"}))
        zf.writestr("beds/maxalto/selene/14366.zip", inner2.getvalue())
        zf.writestr("beds/maxalto/selene/meta.json", json.dumps({"title": "Selene"}))
    out = tmp_path / "out"
    assert ZI.main(["run", "--zip", str(z), "--work", str(tmp_path / "w"), "--out", str(out),
                    "--types", "bed_single,bed_double", "--no-render"]) == 0
    doc = json.loads((out / "inspect.json").read_text())
    rows = {r["format"]: r for r in doc["models"]}
    sk = rows[".skp"]
    assert sk["title"] == "My Bed" and sk["verdict"] == "needs_sketchup_export"
    assert sk["skp"]["version"] == "23.1.340" and sk["skp"]["sketchup_year"] == 2023
    assert (out / "skp_previews" / f"{sk['n']:03d}.png").read_bytes()[:4] == b"\x89PNG"
    g = rows[".glb"]
    assert g["title"] == "Selene" and g["type"] == "bed_double" and g["fits"]
    assert len(doc["scan"]["nested"]) == 2
    assert set(json.loads((out / "meta_all.json").read_text())) == {"beds/riva/my-bed/meta.json",
                                                                     "beds/maxalto/selene/meta.json"}
    assert "SketchUp files" in (out / "report.md").read_text()


@pytest.mark.skipif(__import__("shutil").which("assimp") is None, reason="assimp not installed")
def test_3ds_through_assimp_with_texture(tmp_path):
    import subprocess
    from PIL import Image
    d = tmp_path / "src"
    d.mkdir()
    Image.new("RGB", (8, 8), (200, 120, 60)).save(d / "WOOD.JPG")
    (d / "cube.mtl").write_text("newmtl wood\nKd 1 1 1\nmap_Kd WOOD.JPG\n")
    v = [(x, y, z) for x in (0, 63) for y in (0, 80) for z in (0, 40)]       # a queen bed box in inches, Z up as 3DS
    f = [(1, 2, 4, 3), (5, 7, 8, 6), (1, 5, 6, 2), (3, 4, 8, 7), (1, 3, 7, 5), (2, 6, 8, 4)]
    (d / "cube.obj").write_text("mtllib cube.mtl\n" + "".join("v %g %g %g\n" % p for p in v)
                                + "vt 0 0\nvt 1 0\nvt 1 1\nvt 0 1\nusemtl wood\n"
                                + "".join("f %d/1 %d/2 %d/3 %d/4\n" % q for q in f))
    subprocess.run(["assimp", "export", str(d / "cube.obj"), str(d / "66196.3ds"), "-f3ds"], check=True,
                   capture_output=True)
    z = tmp_path / "beds.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.write(d / "66196.3ds", "beds/horm/ebridi/66196.3ds")
        zf.write(d / "WOOD.JPG", "beds/horm/ebridi/WOOD.JPG")
    out = tmp_path / "out"
    assert ZI.main(["run", "--zip", str(z), "--work", str(tmp_path / "w"), "--out", str(out),
                    "--types", "bed_single,bed_double", "--no-render"]) == 0
    r = json.loads((out / "inspect.json").read_text())["models"][0]
    assert r["ok"] and r["format"] == ".3ds" and r["convert"]["importer"] == "assimp"
    assert r["type"] == "bed_double" and r["unit"] == "inches" and r["fits"]
    doc, _ = WH.read_glb(r["fixed"])
    assert not WH.external_files(doc) and doc.get("images")
