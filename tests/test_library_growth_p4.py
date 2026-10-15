"""Milestone 12 pod P4, the library growth (docs/milestone12.md §6.4; docs/m12_tracks/P4.md): the numpy model reader,
the catalogue entries per source, the GSO licence check and conversion jobs, the Infinigen factory matching, the
catalogue copies, the ingest gate and the steps of ``python -m wenart.assets growth run`` on small fixtures (no
network, no GPU; one conversion test runs Blender when it is installed)."""
from __future__ import annotations

import json
import struct
import subprocess
import sys
import urllib.error
import zipfile
from argparse import Namespace
from pathlib import Path

import numpy as np
import pytest

from wenart.assets import abo as AB
from wenart.assets import models as M
from wenart.assets import objaverse as OV
from wenart.assets.audit import glbmesh as GM
from wenart.assets.audit import growth as G
from wenart.assets.audit import growth_entries as GE
from wenart.assets.audit import growth_gso as GS
from wenart.assets.audit import growth_infinigen as GI
from wenart.assets.audit import growth_run as GR
from wenart.assets.audit import items as I
from wenart.furniture import catalog as C

ROOT = Path(__file__).resolve().parents[1]
LISTS = ROOT / "results" / "library"
STAMP = "2026-10-11T12:00:00Z"


# --------------------------------------------------------------------------
# A tiny glTF / GLB writer (positions given in Blender's Z-up frame, stored Y-up as glTF wants)
# --------------------------------------------------------------------------

def box_mesh(w, d, h, x0=0.0, y0=0.0, z0=0.0):
    v = [(x0 + x, y0 + y, z0 + z) for x in (0, w) for y in (0, d) for z in (0, h)]
    quads = [(0, 2, 3, 1), (4, 5, 7, 6), (0, 1, 5, 4), (2, 6, 7, 3), (0, 4, 6, 2), (1, 3, 7, 5)]
    tris = [t for a, b, c, e in quads for t in ((a, b, c), (a, c, e))]
    return v, tris


def to_yup(verts):
    return [(x, z, -y) for x, y, z in verts]


def gltf_doc(verts_zup, tris, node=None, uri=None, textured=False, colours=False):
    pos = np.asarray(to_yup(verts_zup), dtype="<f4")
    idx = np.asarray(tris, dtype="<u2").reshape(-1)
    pb, ib = pos.tobytes(), idx.tobytes()
    pad = b"\0" * (-len(pb) % 4)
    blob = pb + pad + ib
    attrs = {"POSITION": 0}
    doc = {"asset": {"version": "2.0"}, "scene": 0, "scenes": [{"nodes": [0]}],
           "nodes": [dict(node or {}, mesh=0)],
           "meshes": [{"primitives": [{"attributes": attrs, "indices": 1, "material": 0}]}],
           "materials": [{"pbrMetallicRoughness": {"baseColorTexture": {"index": 0}} if textured else {}}],
           "buffers": [{"byteLength": len(blob)} | ({"uri": uri} if uri else {})],
           "bufferViews": [{"buffer": 0, "byteOffset": 0, "byteLength": len(pb)},
                           {"buffer": 0, "byteOffset": len(pb) + len(pad), "byteLength": len(ib)}],
           "accessors": [{"bufferView": 0, "componentType": 5126, "count": len(pos), "type": "VEC3"},
                         {"bufferView": 1, "componentType": 5123, "count": len(idx), "type": "SCALAR"}]}
    if textured:
        doc.update(images=[{"uri": "t.png"}], textures=[{"source": 0}])
    if colours:
        doc["meshes"][0]["primitives"][0]["attributes"]["COLOR_0"] = 0
    return doc, blob


def write_glb(path, verts_zup, tris, **kw) -> Path:
    doc, blob = gltf_doc(verts_zup, tris, **kw)
    js = json.dumps(doc).encode("utf-8")
    js += b" " * (-len(js) % 4)
    blob += b"\0" * (-len(blob) % 4)
    data = struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob))
    data += struct.pack("<II", len(js), 0x4E4F534A) + js + struct.pack("<II", len(blob), 0x004E4942) + blob
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def write_gltf(folder, name, verts_zup, tris) -> Path:
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    doc, blob = gltf_doc(verts_zup, tris, uri=f"{name}.bin")
    (folder / f"{name}.bin").write_bytes(blob)
    (folder / f"{name}_1k.gltf").write_text(json.dumps(doc), encoding="utf-8")
    return folder / f"{name}_1k.gltf"


def chair_mesh(front_minus_y=True):
    """A seat box and a back box: the back (taller) at +Y -> front -Y (``back_taller``)."""
    v1, t1 = box_mesh(0.5, 0.5, 0.45, -0.25, -0.25, 0.0)
    v2, t2 = box_mesh(0.5, 0.08, 0.5, -0.25, 0.17 if front_minus_y else -0.25, 0.45)
    return v1 + v2, t1 + [(a + 8, b + 8, c + 8) for a, b, c in t2]


# --------------------------------------------------------------------------
# glbmesh
# --------------------------------------------------------------------------

def test_glb_box_in_the_importer_frame(tmp_path):
    v, t = box_mesh(0.4, 0.6, 0.9, x0=-0.2, y0=-0.3)
    m = GM.measure(write_glb(tmp_path / "a.glb", v, t, textured=True, colours=True))
    assert m["bbox_min_m"] == [-0.2, -0.3, 0.0] and m["bbox_max_m"] == [0.2, 0.3, 0.9]
    assert m["bbox_model_m"] == [0.4, 0.6, 0.9] and m["vertices"] == 8 and m["triangles"] == 12
    assert m["info"]["textured"] and m["info"]["vertex_colours"] and m["info"]["images"] == 1
    assert GM.triangles_of(tmp_path / "a.glb").shape == (12, 3, 3)


def test_node_transforms_and_gltf_with_external_buffer(tmp_path):
    v, t = box_mesh(1.0, 1.0, 1.0)
    # translation (glTF Y-up) and a scale: Blender frame box = scale x box + (tx, -tz, ty)
    m = GM.measure(write_glb(tmp_path / "n.glb", v, t, node={"translation": [1.0, 2.0, 3.0], "scale": [2, 2, 2]}))
    assert m["bbox_min_m"] == [1.0, -3.0, 2.0] and m["bbox_max_m"] == [3.0, -1.0, 4.0]
    g = write_gltf(tmp_path / "ph", "chair", v, t)
    assert GM.measure(g)["bbox_model_m"] == [1.0, 1.0, 1.0]
    doc = json.loads(g.read_text())
    doc["buffers"][0]["uri"] = "../escape.bin"
    g.write_text(json.dumps(doc))
    with pytest.raises(GM.MeshError, match="leaves"):
        GM.measure(g)


def test_draco_and_garbage_are_refused(tmp_path):
    v, t = box_mesh(1, 1, 1)
    p = write_glb(tmp_path / "d.glb", v, t)
    data = bytearray(p.read_bytes())
    doc, _ = gltf_doc(v, t)
    doc["meshes"][0]["primitives"][0]["extensions"] = {"KHR_draco_mesh_compression": {}}
    q = tmp_path / "d.gltf"
    (tmp_path / "d.bin").write_bytes(gltf_doc(v, t)[1])
    doc["buffers"][0]["uri"] = "d.bin"
    q.write_text(json.dumps(doc))
    with pytest.raises(GM.MeshError, match="Draco"):
        GM.measure(q)
    (tmp_path / "x.glb").write_bytes(b"not a model")
    with pytest.raises(GM.MeshError):
        GM.measure(tmp_path / "x.glb")
    assert data[:4] == b"glTF"


def test_strided_and_normalized_accessors(tmp_path):
    doc, _ = gltf_doc(*box_mesh(1, 1, 1))
    # interleave positions with a 4-byte pad (stride 16) and use normalized int16 positions (value / 32767)
    pos = np.asarray(to_yup(box_mesh(1, 1, 1)[0]), dtype=np.float32)
    q = np.round(pos * 32767).astype("<i2")
    rows = b"".join(r.tobytes() + b"\0\0" for r in q)                       # 6 + 2 bytes per vertex
    idx = np.asarray(box_mesh(1, 1, 1)[1], dtype="<u2").reshape(-1).tobytes()
    blob = rows + idx
    doc["buffers"] = [{"byteLength": len(blob), "uri": "s.bin"}]
    doc["bufferViews"] = [{"buffer": 0, "byteOffset": 0, "byteLength": len(rows), "byteStride": 8},
                          {"buffer": 0, "byteOffset": len(rows), "byteLength": len(idx)}]
    doc["accessors"][0].update(componentType=5122, normalized=True)
    (tmp_path / "s.bin").write_bytes(blob)
    (tmp_path / "s.gltf").write_text(json.dumps(doc))
    m = GM.measure(tmp_path / "s.gltf")
    assert m["bbox_model_m"] == [1.0, 1.0, 1.0]


def test_front_stats_match_the_python_version(tmp_path):
    v, t = chair_mesh()
    arr, tri = np.asarray(v, dtype=float), np.asarray(t)
    polys = [OV.poly_record([v[a], v[b], v[c]]) for a, b, c in t]
    ref = OV.front_stats(v, polys)
    got = GM.front_stats(arr, tri)
    assert got["side_counts"] == ref["side_counts"] and got["top_centroid_n"] == ref["top_centroid_n"]
    assert got["panel_fraction"] == pytest.approx(ref["panel_fraction"], abs=1e-3)
    rules = OV.load_config()["front_rules"]
    assert OV.geometric_front(got, "back_taller", rules)[0] == "-Y"


# --------------------------------------------------------------------------
# Entries
# --------------------------------------------------------------------------

def measure_of(tmp_path, name="m", mesh=None):
    v, t = mesh or chair_mesh()
    return GM.measure(write_glb(tmp_path / f"{name}.glb", v, t, textured=True))


def validate_one(e):
    doc = {"entries": [], "decor": [e]} if e["type"].startswith("decor_") else {"entries": [e]}
    C.validate(doc, complete=False)


def test_front_rules():
    assert GE.front_of("vase", None)[:2] == ("-Y", "low")
    assert GE.front_of("wall_art", {"x": 1})[1] == "low"                     # documented: only the source knows
    assert GE.front_of("sofa", None, documented="-Y")[:2] == ("-Y", "high")
    stats = GM.front_stats(np.asarray(chair_mesh(False)[0], dtype=float), np.asarray(chair_mesh(False)[1]))
    axis, conf, note = GE.front_of("chair", stats)
    assert (axis, conf) == ("+Y", "medium") and note.startswith("geometry: back_taller")
    from wenart.assets.audit import checks as CK
    assert CK.geometric_front({"front_axis_note": note}) == "+Y"             # the audit reads the same note
    flat = GM.front_stats(np.asarray(box_mesh(1, 1, 1)[0], dtype=float), np.asarray(box_mesh(1, 1, 1)[1]))
    assert GE.front_of("chair", flat)[:2] == ("-Y", "low")


def test_polyhaven_entries_follow_catalog_json(tmp_path):
    m = measure_of(tmp_path)
    cand = {"id": "wooden_chair_09", "type": "chair", "kind": "furniture", "title": "Wooden Chair 09",
            "category": "Furniture/Seating/Chairs", "styles_hint": ["rustic"], "dims_m": [0.5, 0.5, 0.95]}
    e = GE.polyhaven_entry(cand, m, "models/wooden_chair_09/wooden_chair_09_1k.gltf", "a" * 64, "1k", STAMP)
    validate_one(e)
    assert e["source"] == "polyhaven" and e["licence"] == "CC0" and e["resolution"] == "1k"
    assert e["styles"] == ["rustic"] and e["front_axis"] == "-Y" and e["front_axis_confidence"] == "medium"
    assert e["dimensions_api_mm"] == [500, 500, 950] and e["audit"]["status"] == "pending"
    assert not C.usable(e)                                                    # nothing uses it before the audit
    vase = GE.polyhaven_entry(dict(cand, id="brass_vase_01", type="vase", kind="decor", styles_hint=[]), m,
                              "models/brass_vase_01/brass_vase_01_1k.gltf", None, "1k", STAMP)
    validate_one(vase)
    assert vase["type"] == "decor_vase" and "kind" not in vase and vase["styles"] == ["neutral"]
    bed = GE.polyhaven_entry(dict(cand, id="vintage_day_bed", type="bed_single"), m, "x_1k.gltf", None, "1k", STAMP)
    validate_one(bed)
    assert bed["has_mattress"] is False and bed["bed_frame"] is False


def test_abo_entry_is_credited_with_the_documented_front(tmp_path):
    m = measure_of(tmp_path)
    cand = json.loads((LISTS / "growth" / "candidates_abo.json").read_text())["candidates"]
    c = next(x for x in cand if x["type"] == "armchair")
    e = GE.abo_entry(c, m, "b" * 64, AB.load_config(), STAMP)
    validate_one(e)
    assert e["glb"] == M.library_relpath("abo", e["uid"]) and e["author"] == "Amazon.com"
    assert e["front_axis"] == "-Y" and e["front_axis_confidence"] == "high" and "documented front" in \
        e["front_axis_note"]
    assert e["attribution"].startswith(f"\"{c['title']}\" by Amazon.com") and e["units_known"] is True
    assert e["styles"] == [c["family"]] and e["growth"]["family"] == c["family"]
    corner = next(x for x in cand if x["type"] == "sofa_corner")
    fp = OV.footprint_occupancy(GM.triangles_of(tmp_path / "m.glb"), m["bbox_min_m"], m["bbox_max_m"])
    e2 = GE.abo_entry(corner, m, "c" * 64, AB.load_config(), STAMP, footprint=fp)
    validate_one(e2)
    assert "chaise_note" in e2


def test_gso_and_infinigen_entries(tmp_path):
    m = measure_of(tmp_path, mesh=box_mesh(0.2, 0.2, 0.08))
    rec = {"id": "gso_Footed_Bowl_Sand", "uid": "gso_Footed_Bowl_Sand", "name": "Footed_Bowl_Sand",
           "title": "Footed Bowl Sand", "type": "bowl", "file": "Footed_Bowl_Sand.zip", "revision": "6139aa3",
           "author": "Google Research", "page": "https://app.gazebosim.org/GoogleResearch/fuel/models/Footed_Bowl_Sand",
           "evidence": [{"method": "fuel_api", "url": "u", "fields": {"license_url": C.CC_BY}}]}
    e = GE.gso_entry(rec, m, "d" * 64, STAMP)
    validate_one(e)
    assert e["source"] == "gso" and e["type"] == "decor_bowl" and e["kind"] == "decor"
    assert e["glb"] == M.library_relpath("gso", e["uid"]) == "models/gso/gso_Footed_Bowl_Sand.glb"
    assert e["licence_evidence"] and "Google Scanned Objects (CC BY 4.0)" in e["attribution"]
    job = {"id": "infinigen_toilet_0", "factory": "toilet", "type": "toilet", "kind": "furniture", "seed": 0,
           "class": "ToiletFactory", "dotted": "infinigen.assets.objects.bathroom.ToiletFactory"}
    ig = GE.infinigen_entry(job, measure_of(tmp_path, "t"), "e" * 64, GI.COMMIT, GI.TAG, STAMP)
    validate_one(ig)
    assert ig["source"] == "generated" and ig["licence"] == "generated (Infinigen v1.19.0, BSD-3-Clause)"
    assert ig["generated"]["revision"] == GI.COMMIT and ig["generated"]["generator"] == "infinigen"
    assert ig["glb"] == M.library_relpath("generated", ig["uid"])
    from wenart.assets.audit import write as W
    doc = {"entries": [ig]}
    assert W.generated_credit(doc) == 0 and ig["via"].startswith("generated for WenArt_RUN with Infinigen")


@pytest.fixture
def pre_p4(tmp_path, monkeypatch):
    """The repo's catalogues as pod P4 found them (commit a57b64a; gzipped in tests/fixtures/m12_p4): since P4 the
    committed catalogues hold the growth entries, so the tests of the growth steps start from this snapshot."""
    import gzip
    out = tmp_path / "pre_p4"
    out.mkdir()
    for name in ("catalog_library", "catalog"):
        src = ROOT / "tests" / "fixtures" / "m12_p4" / f"{name}_pre_p4.json.gz"
        (out / f"{name}.json").write_bytes(gzip.decompress(src.read_bytes()))
    monkeypatch.setattr(I, "LIBRARY_PATH", out / "catalog_library.json")
    monkeypatch.setattr(I, "POLYHAVEN_PATH", out / "catalog.json")
    return out


def test_copies_validate_and_replace_parametric_types(tmp_path, pre_p4):
    m = measure_of(tmp_path)
    cand = {"id": "painted_wooden_bench", "type": "bench", "kind": "furniture", "title": "Painted Wooden Bench",
            "styles_hint": ["rustic"]}
    ph_e = GE.polyhaven_entry(cand, m, "models/x/x_1k.gltf", None, "1k", STAMP)
    rec = {"id": "gso_x", "uid": "gso_x", "name": "x", "title": "X bowl", "type": "bowl", "evidence": []}
    gso_e = GE.gso_entry(rec, measure_of(tmp_path, "g", box_mesh(0.2, 0.2, 0.1)), "f" * 64, STAMP)
    lib0, ph0 = I.read_json(I.LIBRARY_PATH), I.read_json(I.POLYHAVEN_PATH)
    assert any(p.get("parametric") and p["type"] == "bench" for p in ph0["entries"])
    lib, ph, stats = GE.build_copies(lib0, ph0, [ph_e, gso_e])
    assert stats["parametric_replaced"] == ["bench"] and stats["polyhaven"]["added"] == 1
    assert not any(p.get("parametric") and p["type"] == "bench" for p in ph["entries"])
    assert "gso" in lib["sources"] and lib["datasets"]["gso"]["licence"] == C.CC_BY
    merged = C.Catalog(C.merge(ph, lib))
    assert merged.entry("gso_x") and merged.entry("painted_wooden_bench")
    lib2, _, stats2 = GE.build_copies(lib, ph0, [dict(gso_e, title="X bowl 2")])         # same id: replaced
    assert stats2["library"] == {"added": 0, "replaced": 1}
    assert I.read_json(I.LIBRARY_PATH) == lib0                               # the repo's files are never touched


def test_vision_fields_add_styles_and_the_mattress(tmp_path):
    m = measure_of(tmp_path)
    bed = GE.polyhaven_entry({"id": "b", "type": "bed_single", "kind": "furniture", "title": "B", "styles_hint": []},
                             m, "b_1k.gltf", None, "1k", STAMP)
    chair = GE.polyhaven_entry({"id": "c", "type": "chair", "kind": "furniture", "title": "C",
                                "styles_hint": ["rustic"]}, m, "c_1k.gltf", None, "1k", STAMP)
    doc = {"entries": [bed, chair]}
    got = GE.apply_vision_fields(doc, {"b": {"styles": ["modern", "neutral"], "has_bedding": True},
                                       "c": {"styles": ["classic", "modern", "industrial", "japandi"]}},
                                 {"b", "c"}, {"b": [], "c": ["rustic"]})
    assert got == {"styled": 2, "beds": 1}
    assert bed["styles"] == ["modern"] and bed["has_mattress"] is True
    assert chair["styles"] == ["classic", "industrial", "modern", "rustic"]       # hint + 3 of the answer
    C.validate({"entries": [bed, chair]}, complete=False)


# --------------------------------------------------------------------------
# GSO
# --------------------------------------------------------------------------

def test_gso_uid_fits_the_cache_path():
    long = "Eat_to_Live_The_Amazing_NutrientRich_Program_for_Fast_and_Sustained_Weight_Loss_Revised_Edition_Book"
    uid = GS.gso_uid(long)
    assert len(uid) <= 64 and uid == GS.gso_uid(long) and M.library_relpath("gso", uid)
    assert GS.gso_uid("Footed_Bowl_Sand") == "gso_Footed_Bowl_Sand" and GS.name_of("gso_Footed_Bowl_Sand") == \
        "Footed_Bowl_Sand"


def test_archives_are_unpacked_safely(tmp_path):
    with pytest.raises(GS.ArchiveError, match="leaves"):
        GS.safe_members([("../x", 1, False)])
    with pytest.raises(GS.ArchiveError, match="leaves"):
        GS.safe_members([("/etc/x", 1, False)])
    with pytest.raises(GS.ArchiveError, match="link"):
        GS.safe_members([("a", 1, True)])
    with pytest.raises(GS.ArchiveError, match="MB"):
        GS.safe_members([("a", GS.MAX_UNPACKED + 1, False)])
    good = tmp_path / "good.zip"
    with zipfile.ZipFile(good, "w") as z:
        z.writestr("Bowl/meshes/model.obj", "v 0 0 0\n")
        z.writestr("Bowl/meshes/model.mtl", "newmtl m\n")
        z.writestr("Bowl/materials/textures/texture.png", b"png")
        z.writestr("Bowl/model.config", "<model><name>Bowl</name><author><name>Google</name></author></model>")
        z.writestr("Bowl/thumbnails/0.jpg", b"jpg")
    info = GS.safe_extract(good, tmp_path / "out")
    assert info["members"] == 5
    lay = GS.layout(tmp_path / "out")
    assert lay["obj"] == "Bowl/meshes/model.obj" and lay["texture"] == "Bowl/materials/textures/texture.png"
    assert lay["config"] == "Bowl/model.config" and "Bowl/model.config" in lay["texts"]
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as z:
        z.writestr("../../evil.txt", "x")
    with pytest.raises(GS.ArchiveError):
        GS.safe_extract(bad, tmp_path / "out2")
    assert not (tmp_path / "evil.txt").exists()


def test_licence_evidence_rules():
    ev, no = GS.evidence_in_texts({"LICENSE": "Released under CC-BY 4.0 by Google."})
    assert ev == {"method": "archive", "file": "LICENSE", "text": "Released under CC-BY 4.0 by Google."} and no is None
    ev, no = GS.evidence_in_texts({"README": "Creative Commons Attribution-NonCommercial 4.0"})
    assert ev is None and "another licence" in no
    assert GS.evidence_in_texts({"model.config": "<model><name>x</name></model>"}) == (None, None)
    url = GS.fuel_url("Bowl")
    rec = {"name": "Bowl", "owner": "GoogleResearch", "license_name": "Creative Commons - Attribution",
           "license_url": "http://creativecommons.org/licenses/by/4.0/"}
    ev, no = GS.evidence_in_fuel(rec, url, "Bowl")
    assert ev["method"] == "fuel_api" and ev["fields"]["license_url"].endswith("/by/4.0/") and no is None
    nc = dict(rec, license_name="Creative Commons - Attribution - Non Commercial",
              license_url="https://creativecommons.org/licenses/by-nc/4.0/")
    assert GS.evidence_in_fuel(nc, url, "Bowl")[0] is None
    assert "owner" in GS.evidence_in_fuel(dict(rec, owner="Someone"), url, "Bowl")[1]
    assert GS.evidence_in_fuel({"name": "Bowl"}, url, "Bowl") == (None, None)
    assert GS.evidence_in_fuel(dict(rec, license_url="", license_name="Creative Commons - Attribution"), url,
                               "Bowl")[0] is None                               # no version named: not confirmed
    keep = GS.decide("Bowl", None, None, ev, None, None)
    assert keep["kept"] and "Gazebo Fuel" in keep["reason"]
    drop = GS.decide("Bowl", None, None, None, None, "HTTP 404")
    assert not drop["kept"] and "HTTP 404" in drop["reason"]
    both = GS.decide("Bowl", {"method": "archive"}, None, None, "the Fuel record names another licence", None)
    assert not both["kept"]


def test_licence_record_and_fuel_fetch(tmp_path):
    folder = tmp_path / "obj"
    (folder / "meshes").mkdir(parents=True)
    (folder / "meshes" / "model.obj").write_text("v 0 0 0\n")
    (folder / "model.config").write_text("<model><name>Footed_Bowl_Sand</name><author><name>Google</name>"
                                         "</author></model>")
    cand = {"id": "gso_Footed_Bowl_Sand", "type": "bowl", "title": "Footed Bowl Sand", "file": "Footed_Bowl_Sand.zip"}
    rec_ok = {"name": "Footed_Bowl_Sand", "owner": "GoogleResearch", "license_url":
              "https://creativecommons.org/licenses/by/4.0/"}
    r = GS.licence_record(cand, folder, "rev", (rec_ok, "u", None))
    assert r["kept"] and r["author"] == "Google Research" and r["uid"] == "gso_Footed_Bowl_Sand"
    assert GS.convert_jobs([r], tmp_path / "w")[0]["axes"][0] == ["Z", "Y"]
    r2 = GS.licence_record(cand, folder, "rev", None)
    assert not r2["kept"] and "not asked" in r2["reason"]

    class Resp:
        def __init__(self, data):
            self.data = data

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def read(self, n=-1):
            return self.data
    got = GS.fetch_fuel("Footed_Bowl_Sand", opener=lambda req, timeout: Resp(json.dumps(rec_ok).encode()))
    assert got[0] == rec_ok and got[2] is None and "GoogleResearch/models/Footed_Bowl_Sand" in got[1]

    def err(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 404, "nf", {}, None)
    assert GS.fetch_fuel("x", opener=err)[2] == "HTTP 404"


# --------------------------------------------------------------------------
# Infinigen
# --------------------------------------------------------------------------

def test_infinigen_jobs_follow_the_approved_plan():
    plan = json.loads((LISTS / "growth" / "plan_infinigen.json").read_text())
    approved = G.approved("infinigen", LISTS)["ids"]
    jobs = GI.jobs_of(plan, approved)
    assert len(jobs) == 30 and {j["id"] for j in jobs} == set(approved)
    assert [j["seed"] for j in jobs[:12]] == [0] * 12                          # every factory once first
    assert next(j for j in jobs if j["factory"] == "pot")["type"] == "plant_small"
    assert next(j for j in jobs if j["factory"] == "dishwasher")["kind"] is None


def test_factory_listing_and_matching(tmp_path):
    listing = ("infinigen.assets.objects.bathroom.ToiletFactory\n# comment\n"
               "infinigen.assets.objects.tableware.PotFactory\n")
    sources = {"infinigen/assets/objects/tableware/plant_container.py":
               "class PlantPotFactory(PotFactory):\n    pass\nclass PlantContainerFactory(AssetFactory):\n",
               "infinigen/assets/objects/appliances/fridge.py": "class BeverageFridgeFactory(AssetFactory):\n",
               "infinigen/assets/sim_objects/fridge.py": "class FridgeFactory(AssetFactory):\n"}
    facs = GI.factories_of(listing, sources)
    assert facs["ToiletFactory"] == "infinigen.assets.objects.bathroom.ToiletFactory"
    assert facs["PlantContainerFactory"] == "infinigen.assets.objects.tableware.plant_container.PlantContainerFactory"
    assert GI.match("pot", facs)["class"] == "PlantContainerFactory"           # a pot with a plant, not a cooking pot
    assert GI.match("toilet", facs)["how"].startswith("preferred")
    m = GI.match("fridge", facs)
    assert m["class"] == "BeverageFridgeFactory" or m["class"] == "FridgeFactory"
    assert GI.match("beverage fridge", facs)["class"] == "BeverageFridgeFactory"
    assert GI.match("washing machine", facs) is None
    assert GI.words("BeverageFridgeFactory") == ["beverage", "fridge"]


def test_infinigen_job_states_and_plan(tmp_path):
    plan = json.loads((LISTS / "growth" / "plan_infinigen.json").read_text())
    approved = G.approved("infinigen", LISTS)["ids"]
    facs = {c: f"infinigen.assets.objects.x.{c}" for cs in GI.PREFERRED.values() for c in cs}
    (tmp_path / "infinigen_toilet_0").mkdir()
    obj = tmp_path / "infinigen_toilet_0" / "a.obj"
    obj.write_text("v 0 0 0\n")
    (tmp_path / "infinigen_toilet_0" / "result.json").write_text(json.dumps({"ok": True, "obj": str(obj)}))
    (tmp_path / "infinigen_bowl_0").mkdir()
    (tmp_path / "infinigen_bowl_0" / "result.json").write_text(json.dumps({"ok": False, "attempts": 2}))
    (tmp_path / "infinigen_pot_0").mkdir()
    (tmp_path / "infinigen_pot_0" / "result.json").write_text(json.dumps({"ok": False, "attempts": 1}))
    p = GI.plan_jobs(plan, approved, facs, tmp_path)
    assert p["done"] == ["infinigen_toilet_0"] and p["failed"] == ["infinigen_bowl_0"]
    assert "infinigen_pot_0" in p["todo"] and len(p["todo"]) == 28 and not p["missing"]
    assert next(j for j in p["jobs"] if j["id"] == "infinigen_pot_0")["class"] == "PlantContainerFactory"
    assert GI.plan_jobs(plan, approved, None, tmp_path)["matched"] == {}


FAKE_GIA = '''
import sys
from pathlib import Path
from contextlib import contextmanager

def configure_cycles_devices(*a, **k):
    raise RuntimeError("the driver must not configure the GPU")

def make_args():
    a = sys.argv
    class N: pass
    n = N()
    n.output_folder = Path(a[a.index("--output_folder") + 1]); n.factories = [a[a.index("-f") + 1]]
    n.no_mod = False; n.fire = False; n.film_transparent = 1; n.hdri = False
    return n

@contextmanager
def FixedSeed(s):
    yield

def build_and_save_asset(payload):
    if "Bad" in payload["fac"]:
        raise ValueError("this factory fails")
    configure_cycles_devices()
    idx = payload["idx"]
    out = payload["args"].output_folder
    (out / f"{payload['fac']}_{idx:03d}").mkdir(parents=True, exist_ok=True)
    (out / f"{payload['fac']}_{idx:03d}" / "scene.blend").write_bytes(b"blend")
    e = out / f"export_{idx:03d}"
    e.mkdir(parents=True, exist_ok=True)
    (e / f"export_{idx:03d}.obj").write_text("v 0 0 0\\n")
'''
FAKE_BPY = '''
class _App:
    version_string = "4.2.0"
app = _App()
class _Data:
    objects = []
data = _Data()
'''


def test_infinigen_driver_resumes_and_records_failures(tmp_path):
    repo = tmp_path / "repo"
    (repo / "infinigen_examples").mkdir(parents=True)
    (repo / "infinigen_examples" / "__init__.py").write_text("")
    (repo / "infinigen_examples" / "generate_individual_assets.py").write_text(FAKE_GIA)
    (repo / "bpy.py").write_text(FAKE_BPY)
    jobs = [{"id": "infinigen_toilet_0", "dotted": "x.ToiletFactory", "class": "ToiletFactory", "seed": 0,
             "folder": str(tmp_path / "out" / "infinigen_toilet_0")},
            {"id": "infinigen_bad_0", "dotted": "x.BadFactory", "class": "BadFactory", "seed": 0,
             "folder": str(tmp_path / "out" / "infinigen_bad_0")}]
    jp = tmp_path / "jobs.json"
    jp.write_text(json.dumps({"jobs": jobs}))
    driver = ROOT / "wenart" / "assets" / "audit" / "infinigen_driver.py"
    cmd = [sys.executable, str(driver), "generate", "--repo", str(repo), "--jobs", str(jp), "--job-timeout", "60"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    assert r.returncode == 1 and "infinigen_toilet_0 ok" in r.stdout and "infinigen_bad_0 failed" in r.stdout
    ok = json.loads((tmp_path / "out" / "infinigen_toilet_0" / "result.json").read_text())
    assert ok["ok"] and ok["obj"].endswith("export_000/export_000.obj") and ok["bpy"] == "4.2.0"
    bad = json.loads((tmp_path / "out" / "infinigen_bad_0" / "result.json").read_text())
    assert not bad["ok"] and bad["attempts"] == 1 and "this factory fails" in bad["log_tail"]
    r2 = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    assert "infinigen_toilet_0" not in r2.stdout.replace("INFINIGEN batch", "")     # done: not run again
    assert json.loads((tmp_path / "out" / "infinigen_bad_0" / "result.json").read_text())["attempts"] == 2
    r3 = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    assert "1 done, 1 failed, 0 not started" in r3.stdout                          # failed twice: not tried again
    r4 = subprocess.run(cmd + ["--deadline", "1"], capture_output=True, text=True, timeout=120)
    assert r4.returncode == 1


# --------------------------------------------------------------------------
# Conversion in Blender (skipped without a Blender binary)
# --------------------------------------------------------------------------

def test_obj_to_glb_in_blender_keeps_the_axes(tmp_path):
    from wenart.blender import cli as BC
    blender = BC.find_blender()
    if blender is None:
        pytest.skip("no Blender binary (WENART_BLENDER)")
    v, t = box_mesh(0.1, 0.2, 0.3)
    obj = tmp_path / "model.obj"
    obj.write_text("mtllib model.mtl\no m\n" + "".join("v %g %g %g\n" % p for p in v) + "usemtl m\n"
                   + "".join("f %d %d %d\n" % (a + 1, b + 1, c + 1) for a, b, c in t))
    (tmp_path / "model.mtl").write_text("newmtl m\nKd 0.8 0.2 0.2\nmap_Kd missing.png\n")
    from PIL import Image
    Image.new("RGB", (8, 8), (10, 200, 10)).save(tmp_path / "texture.png")
    jobs = [{"id": "gso", "src": str(obj), "dst": str(tmp_path / "o" / "gso.glb"), "axes": [["Z", "Y"]],
             "expect_dims": None, "texture": str(tmp_path / "texture.png")},
            {"id": "ig", "src": str(obj), "dst": str(tmp_path / "o" / "ig.glb"),
             "axes": [["Y", "NEGATIVE_Z"], ["Z", "Y"]], "expect_dims": [0.1, 0.2, 0.3], "texture": None},
            {"id": "broken", "src": str(tmp_path / "missing.obj"), "dst": str(tmp_path / "o" / "b.glb"),
             "axes": [["Z", "Y"]], "expect_dims": None, "texture": None}]
    got = GR.run_blender_jobs(blender, jobs, tmp_path / "w", "t", 300)
    assert got["gso"]["ok"] and got["gso"]["fallback_textures"] == 1 and got["gso"]["images"] == 1
    assert got["ig"]["ok"] and (got["ig"]["up"], got["ig"]["forward"]) == ("Z", "Y")      # the axes that match
    assert not got["broken"]["ok"]
    for name in ("gso", "ig"):
        m = GM.measure(tmp_path / "o" / f"{name}.glb")
        assert m["bbox_model_m"] == [0.1, 0.2, 0.3]
    assert GM.measure(tmp_path / "o" / "gso.glb")["info"]["textured"]


# --------------------------------------------------------------------------
# Steps of python -m wenart.assets growth run
# --------------------------------------------------------------------------

def run_args(tmp_path, **kw) -> Namespace:
    a = GR.parser().parse_args(["report", "--growth", str(tmp_path / "g"), "--assets", str(tmp_path / "assets"),
                                "--p4", str(tmp_path / "p4"), "--p3", str(tmp_path / "p3"), "--lists", str(LISTS)])
    for k, v in kw.items():
        setattr(a, k, v)
    return a


def test_download_retries_and_limits(tmp_path):
    calls = []

    def flaky(url, dest, max_bytes):
        calls.append(url)
        if len(calls) < 2:
            raise urllib.error.URLError("reset")
        Path(dest).write_bytes(b"x")
    assert GR.download_retry("u", tmp_path / "f", 10, fetch=flaky, sleep=lambda s: None) == 2

    def big(url, dest, max_bytes):
        calls.append("big")
        raise AB.TooLarge("over")
    with pytest.raises(AB.TooLarge):
        GR.download_retry("u", tmp_path / "g", 10, fetch=big, sleep=lambda s: None)
    assert calls.count("big") == 1

    def missing(url, dest, max_bytes):
        calls.append("404")
        raise urllib.error.HTTPError(url, 404, "nf", {}, None)
    with pytest.raises(urllib.error.HTTPError):
        GR.download_retry("u", tmp_path / "h", 10, fetch=missing, sleep=lambda s: None)
    assert calls.count("404") == 1
    assert GR.size_limit(10) == 15e6 and GR.size_limit(100) == 125e6 and GR.size_limit(None) == 120e6


def test_ingest_gate_and_resume(tmp_path, monkeypatch, capsys):
    lists = tmp_path / "lists"
    (lists / "growth").mkdir(parents=True)
    a = run_args(tmp_path, lists=str(lists), source="abo", workers=2, size="1k")
    assert GR.cmd_ingest(a) == 1 and "refused" in capsys.readouterr().out          # no approval: nothing downloads
    assert json.loads((tmp_path / "g" / "report" / "ingest_abo.json").read_text())["refused"]
    (lists / "growth" / "approved_abo.json").write_text(json.dumps(
        {"source": "abo", "approved_by": "test", "approved_utc": STAMP, "ids": ["abo_A", "abo_B"]}))
    (lists / "growth" / "candidates_abo.json").write_text(json.dumps({"candidates": [
        {"id": "abo_A", "glb": "A/A.glb", "size_mb": 1.0}, {"id": "abo_B", "glb": "B/B.glb", "size_mb": None}]}))
    got = []

    def fake(url, dest, max_bytes):
        got.append((url, max_bytes))
        Path(dest).parent.mkdir(parents=True, exist_ok=True)
        Path(dest).write_bytes(b"glb")
    monkeypatch.setattr(AB, "download", fake)
    assert GR.cmd_ingest(a) == 0
    assert sorted(u for u, _ in got)[0].endswith("/3dmodels/original/A/A.glb")
    assert dict((u.rsplit("/", 1)[1], m) for u, m in got) == {"A.glb": 6e6, "B.glb": 120e6}
    rep = json.loads((tmp_path / "g" / "report" / "ingest_abo.json").read_text())
    assert rep["ok"] == 2 and rep["records"][0]["glb"] == "models/abo/abo_A.glb"
    assert (tmp_path / "assets" / "models" / "abo" / "abo_A.glb").is_file()
    got.clear()
    assert GR.cmd_ingest(a) == 0 and not got                                      # resume: present files kept
    assert all(r.get("kept") for r in json.loads((tmp_path / "g" / "report" / "ingest_abo.json").read_text())[
        "records"])


def test_committed_approvals_pass_the_gate():
    for source, n in (("polyhaven", 88), ("abo", 232), ("gso", 36), ("infinigen", 30)):
        doc = G.approved(source, LISTS)
        assert len(doc["ids"]) == n, source


def fixture_growth(tmp_path):
    """Ingest and conversion records of every source for the catalogue step, with real model files."""
    g, assets = tmp_path / "g", tmp_path / "assets"
    rep = g / "report"
    rep.mkdir(parents=True)
    lists = tmp_path / "lists"
    (lists / "growth").mkdir(parents=True)
    ph_c = json.loads((LISTS / "growth" / "candidates_polyhaven.json").read_text())
    abo_c = json.loads((LISTS / "growth" / "candidates_abo.json").read_text())
    for name in ("candidates_gso.json", "plan_infinigen.json", "approved_infinigen.json"):
        (lists / "growth" / name).write_text((LISTS / "growth" / name).read_text())
    chair = next(c for c in ph_c["candidates"] if c["type"] == "chair")
    vase = next(c for c in ph_c["candidates"] if c["type"] == "vase")
    (lists / "growth" / "candidates_polyhaven.json").write_text(json.dumps({"candidates": [chair, vase]}))
    arm = next(c for c in abo_c["candidates"] if c["type"] == "armchair")
    head = next(c for c in abo_c["candidates"] if c["type"] == "headboard")
    (lists / "growth" / "candidates_abo.json").write_text(json.dumps({"candidates": [arm, head]}))
    ph_recs = []
    for c, mesh in ((chair, chair_mesh()), (vase, box_mesh(0.15, 0.15, 0.3, -0.075, -0.075))):
        gl = write_gltf(assets / "models" / c["id"], c["id"], *mesh)
        rel = gl.relative_to(assets).as_posix()
        ph_recs.append({"id": c["id"], "ok": True, "gltf": rel, "sha256": {"gltf": GR.sha256_file(gl)}, "size": "1k"})
    (rep / "ingest_polyhaven.json").write_text(json.dumps({"records": ph_recs, "approved": 2, "ok": 2}))
    abo_recs = []
    for c, mesh in ((arm, chair_mesh()), (head, box_mesh(1.6, 0.1, 1.2))):
        p = write_glb(assets / "models" / "abo" / f"{c['id']}.glb", *mesh, textured=True)
        abo_recs.append({"id": c["id"], "ok": True, "glb": f"models/abo/{c['id']}.glb", "sha256": GR.sha256_file(p)})
    abo_recs.append({"id": "abo_MISSING", "ok": False, "error": "HTTPError: 404"})
    (rep / "ingest_abo.json").write_text(json.dumps({"records": abo_recs, "approved": 3, "ok": 2}))
    # GSO: one kept and converted, one dropped for its licence
    gso = {"id": "gso_Footed_Bowl_Sand", "uid": "gso_Footed_Bowl_Sand", "name": "Footed_Bowl_Sand", "type": "bowl",
           "title": "Footed Bowl Sand", "kept": True, "reason": "ok", "evidence": [{"method": "archive",
                                                                                     "file": "LICENSE"}]}
    (g / "gso").mkdir()
    (g / "gso" / "licences.json").write_text(json.dumps({"records": [gso, {
        "id": "gso_Target_Basket_Medium", "uid": "gso_Target_Basket_Medium", "kept": False,
        "reason": "no CC BY 4.0 statement"}]}))
    p = write_glb(assets / "models" / "gso" / "gso_Footed_Bowl_Sand.glb", *box_mesh(0.2, 0.2, 0.08), textured=True)
    (rep / "convert_gso.json").write_text(json.dumps({"results": {"gso_Footed_Bowl_Sand": {
        "ok": True, "glb": "models/gso/gso_Footed_Bowl_Sand.glb", "sha256": GR.sha256_file(p)}}}))
    # Infinigen: a toilet (typed), a dishwasher (preview only) and a failed bowl
    ig = g / "infinigen"
    jobs = []
    for jid, factory, ftype, kind, state in (("infinigen_toilet_0", "toilet", "toilet", "furniture", "done"),
                                             ("infinigen_dishwasher_0", "dishwasher", None, None, "done"),
                                             ("infinigen_bowl_0", "bowl", "bowl", "decor", "failed")):
        folder = ig / jid
        folder.mkdir(parents=True)
        (folder / "result.json").write_text(json.dumps({"ok": state == "done", "error": "boom", "attempts": 2}))
        jobs.append({"id": jid, "factory": factory, "type": ftype, "kind": kind, "seed": 0, "state": state,
                     "folder": str(folder), "class": factory.title() + "Factory",
                     "dotted": f"infinigen.assets.objects.x.{factory.title()}Factory"})
    (ig / "jobs.json").write_text(json.dumps({"jobs": jobs, "tag": GI.TAG, "commit": GI.COMMIT}))
    conv = {}
    for jid in ("infinigen_toilet_0", "infinigen_dishwasher_0"):
        p = write_glb(assets / "models" / "generated" / f"{jid}.glb", *chair_mesh(), textured=True)
        conv[jid] = {"ok": True, "glb": f"models/generated/{jid}.glb", "sha256": GR.sha256_file(p)}
    (rep / "convert_infinigen.json").write_text(json.dumps({"results": conv}))
    return run_args(tmp_path, lists=str(lists), checked_utc=STAMP)


def test_catalogue_step_writes_valid_copies(tmp_path):
    a = fixture_growth(tmp_path)
    lib_before = I.LIBRARY_PATH.read_bytes()
    assert GR.cmd_catalogue(a) == 0
    assert I.LIBRARY_PATH.read_bytes() == lib_before                       # copies only
    nid = json.loads((tmp_path / "p4" / "audit" / "new_ids.json").read_text())
    assert nid["by_source"] == {"polyhaven": 2, "abo": 1, "gso": 1, "infinigen": 1}
    assert [p["id"] for p in nid["previews"]] == ["infinigen_dishwasher_0"]
    lib = json.loads((tmp_path / "p4" / "audit" / "catalogue" / "catalog_library.json").read_text())
    ph = json.loads((tmp_path / "p4" / "audit" / "catalogue" / "catalog.json").read_text())
    C.validate(lib, complete=False)
    C.Catalog(C.merge(ph, lib))
    items = {i["id"]: i for i in I.load_items(tmp_path / "p4" / "audit" / "catalogue" / "catalog_library.json",
                                              tmp_path / "p4" / "audit" / "catalogue" / "catalog.json")}
    for iid in nid["ids"]:
        assert items[iid]["audit"]["status"] == "pending"
    rep = json.loads((tmp_path / "g" / "report" / "catalogue.json").read_text())
    why = {d["id"]: d["reason"] for d in rep["dropped"]}
    assert "headboard" in why[next(i for i in why if i.startswith("abo_") and i != "abo_MISSING")]
    assert "404" in why["abo_MISSING"] and "licence not confirmed" in why["gso_Target_Basket_Medium"]
    assert "not generated" in why["infinigen_bowl_0"]
    # the audit render takes the copies and the ids file
    from wenart.assets.audit import cli as CLI
    args = CLI.parser().parse_args(["render", "--assets", str(tmp_path / "assets"), "--out", str(tmp_path / "p4"),
                                    "--catalog", str(tmp_path / "p4/audit/catalogue/catalog_library.json"),
                                    "--polyhaven", str(tmp_path / "p4/audit/catalogue/catalog.json"),
                                    "--ids-file", str(tmp_path / "p4/audit/new_ids.json"), "--plan"])
    assert CLI.cmd_render(args) == 0
    plan = json.loads((tmp_path / "p4" / "audit" / "render_plan.json").read_text())
    assert sorted(plan["jobs"]) == sorted(nid["ids"]) and not plan["missing"]
    # code checks: the new models only, compared with the whole library
    code_args = CLI.parser().parse_args(["code", "--out", str(tmp_path / "p4"), "--catalog",
                                         str(tmp_path / "p4/audit/catalogue/catalog_library.json"), "--polyhaven",
                                         str(tmp_path / "p4/audit/catalogue/catalog.json"), "--ids-file",
                                         str(tmp_path / "p4/audit/new_ids.json")])
    assert CLI.cmd_code(code_args) == 0
    code = json.loads((tmp_path / "p4" / "audit" / "code.json").read_text())
    assert sorted(code["checks"]) == sorted(nid["ids"])
    # gaps over the whole library, the plan of the ask without a render, the report
    assert GR.cmd_gaps(a) == 0
    gaps = json.loads((tmp_path / "p4" / "audit" / "gaps.json").read_text())
    assert gaps["scope"] == "whole library after P4" and gaps["rows"]
    assert GR.unanswered(GR.ask_args(tmp_path / "p4", None, None, "agent", None, "both", 1, None), None, [1, 2]) == 0
    assert GR.cmd_report(a) == 0
    md = (tmp_path / "g" / "report" / "growth.md").read_text()
    assert "| abo | 3 | 2 |" in md and "Infinigen: tag v1.19.0" in md


def test_pending_step_needs_the_p3_folder(tmp_path, capsys, pre_p4):
    a = fixture_growth(tmp_path)
    assert GR.cmd_catalogue(a) == 0
    a.model_key = "agent"
    assert GR.cmd_pending(a) == 1 and "P3's folder is missing" in capsys.readouterr().out


def test_growth_cli_dispatch():
    assert G.main(["run", "infinigen-list"]) == 1                  # --repo is needed
    r = subprocess.run([sys.executable, "-m", "wenart.assets", "growth", "run", "--help"], capture_output=True,
                       text=True, cwd=ROOT, timeout=60)
    assert r.returncode == 0 and "gso-licence" in r.stdout


# --------------------------------------------------------------------------
# The new source across the files that resolve library models
# --------------------------------------------------------------------------

def test_gso_is_a_library_source_everywhere(tmp_path):
    from wenart.assets import fetch
    from wenart.blender import furniture as BF
    from wenart.run import copy as CP
    assert "gso" in C.LIBRARY_SOURCES and C.SOURCE_LICENCES["gso"] == (C.CC_BY,)
    assert set(CP.LIBRARY_SOURCES) == set(C.LIBRARY_SOURCES) == set(M.LIBRARY_SOURCES)
    assert BF.MODEL_LICENCES["gso"] == (C.CC_BY,) and "gso" in BF.LIBRARIES
    credit = {k: "x" for k in fetch.CC_BY_FIELDS}
    asset = dict(credit, library="gso", licence=C.CC_BY, asset_id="gso_x", method="library")
    assert BF.licence_refusal(asset) is None
    assert "not" in (BF.licence_refusal(dict(asset, licence="CC-BY-NC-4.0")) or "not")
    assert fetch.check_licence("gso", C.CC_BY, kind="models", entry=dict(credit, id="gso_x")) == C.CC_BY
    with pytest.raises(fetch.LicenceError):
        fetch.check_licence("gso", "CC0", kind="models")
    text = CP.attribution_text("Renders", [{"credit": "\"Bowl\" by Google Research", "pieces": [("d1", "bowl")],
                                            "source": "gso"}])
    assert "Google Scanned Objects" in text and OV.GSO_NOTICE in text
    from wenart.assets.audit import decide as D
    assert D.default_flags({"source": "gso", "kind": "decor", "type": "bowl"})["real_product"] is True


# --------------------------------------------------------------------------
# The audit chain after the vision question (fake answers): decide, write, vision fields, P3 pending, plan of the ask
# --------------------------------------------------------------------------

def fake_answers(items_by_id):
    """A fake vision client: every model is its type, a real product, quality 4, styles modern."""
    from types import SimpleNamespace

    from wenart.assets.audit import ask as A

    class Client:
        model = A.model_of("agent").id                      # the store keeps answers of the model asked

        def run_schema(self, images, prompt, schema, **kw):
            iid = Path(images[0]).stem
            it = items_by_id[iid]
            if "is_type" not in schema["properties"]:
                data = {"type_guess": it["type"]}
            else:
                bed = it["type"] in ("bed_single", "bed_double")
                data = {"is_type": True, "type_guess": it["type"], "single_object": True, "real_product": True,
                        "indoor": "indoor", "upright": True, "size_plausible": True, "parts_open": False,
                        "styles": ["modern"], "quality": 4,
                        "front_shown": "front" if A.has_front(it["type"]) else "none",
                        "has_bedding": True if bed else None, "has_pillows": False if bed else None,
                        "has_cushions": None, "contact": "flat_bottom" if it["kind"] == "decor" else None}
                if "materials" in schema["properties"]:           # the Milestone 13 question (material tags gate)
                    data["materials"] = ["wood", "fabric"]
            return SimpleNamespace(data=data, raw_text="{}", error=None, attempts=1, latency_s=0.01)
    return lambda m, s: Client()


def fake_render(audit: Path, items: list) -> dict:
    """Sheets and measurements as the audit render writes them (``measure.json``)."""
    from PIL import Image
    from wenart.assets.objaverse import pixels_sha256
    mdoc = {"sheets": {}, "measures": {}}
    for it in items:
        rel = f"sheets/{it['type']}/{it['id']}.jpg"
        (audit / rel).parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", (16, 16), (len(it["id"]) % 255, 90, 90)).save(audit / rel)
        mdoc["sheets"][it["id"]] = rel
        mdoc["measures"][it["id"]] = {"ok": True, "size": it["bbox_m"], "faces": 20000, "device": "OPTIX",
                                      "model_box_min": it.get("bbox_min_m"), "model_box_max": it.get("bbox_max_m"),
                                      "sheet_sha256": pixels_sha256(audit / rel)["sha256"]}
    audit.mkdir(parents=True, exist_ok=True)
    (audit / "measure.json").write_text(json.dumps(mdoc))
    return mdoc


def ask_fake(out_root: Path, items: list, passes, by_id):
    from wenart.assets.audit import ask as A
    from wenart.assets.audit import cli as CLI
    audit = out_root / "audit"
    model = A.model_of("agent")
    mdoc = json.loads((audit / "measure.json").read_text())
    from wenart.assets.audit import load_config
    for n in passes:
        only = CLI.second_pass_ids(items, A.load_answers(audit, model)) if n == 2 else None
        # Milestone 13: the question version per item (the materials question for models without material tags)
        A.build_requests(items, mdoc, audit, "m12.1", only, n == 2, cfg_ask=load_config().get("ask") or {})
        assert A.ask(audit, model, "http://fake", second=n == 2, workers=1, client_factory=fake_answers(by_id),
                     log=lambda *a: None) == 0


def test_the_audit_chain_after_the_ask(tmp_path, pre_p4):
    from wenart.assets.audit import checks as CK
    from wenart.assets.audit import cli as CLI
    from wenart.assets.audit import load_config
    a = fixture_growth(tmp_path)
    assert GR.cmd_catalogue(a) == 0
    lib_p, ph_p = GR.copies(a)
    nid = json.loads((tmp_path / "p4" / "audit" / "new_ids.json").read_text())
    items = I.load_items(lib_p, ph_p)
    by_id = {i["id"]: i for i in items}
    new = [by_id[i] for i in nid["ids"]]
    fake_render(tmp_path / "p4" / "audit", new)
    common = ["--out", str(tmp_path / "p4"), "--catalog", str(lib_p), "--polyhaven", str(ph_p)]
    ids = ["--ids-file", str(tmp_path / "p4" / "audit" / "new_ids.json")]
    assert CLI.main(["code"] + common + ids) == 0
    ask_fake(tmp_path / "p4", items, (1, 2), by_id)
    assert CLI.main(["decide", "--model-key", "agent"] + common + ids) == 0
    audit = json.loads((tmp_path / "p4" / "audit" / "audit.json").read_text())
    assert sorted(r["id"] for r in audit["items"]) == sorted(nid["ids"])
    assert all(r["status"] in ("keep", "fix", "removed") for r in audit["items"]), \
        [(r["id"], r["status"], r["pending"]) for r in audit["items"]]
    assert CLI.main(["write"] + common) == 0
    a.model_key = "agent"
    assert GR.cmd_vision_fields(a) == 0
    lib = json.loads(lib_p.read_text())
    ph = json.loads(ph_p.read_text())
    C.validate(lib, complete=False)
    C.Catalog(C.merge(ph, lib))
    after = {i["id"]: i for i in I.load_items(lib_p, ph_p)}
    for iid in nid["ids"]:
        assert after[iid]["audit"]["status"] in ("keep", "fix", "removed"), iid
        assert "modern" in after[iid]["styles"] or after[iid]["audit"]["status"] == "removed", iid
    assert CLI.main(["sheets"] + common) == 0
    assert list((tmp_path / "p4" / "audit" / "contact").glob("*.jpg"))
    # the plan of the ask: every request answered (no P3 folder here)
    assert GR.unanswered(GR.ask_args(tmp_path / "p4", lib_p, ph_p, "agent", None, "both", 1, None),
                         __import__("wenart.assets.audit.ask", fromlist=["x"]).model_of("agent"), [1, 2]) == 0
    # the P3 models still pending: decided from P3's folder (code checks, both passes) into the copies
    pend = [i for i in after.values() if i["audit"]["status"] == "pending"]
    assert len(pend) == 4
    p3 = tmp_path / "p3" / "audit"
    fake_render(p3, pend)
    checks = CK.run_checks(list(after.values()), load_config(), {})
    (p3 / "code.json").write_text(json.dumps({"checks": {i["id"]: checks[i["id"]] for i in pend}}))
    ask_fake(tmp_path / "p3", pend, (1, 2), {i["id"]: i for i in pend})
    assert GR.cmd_pending(a) == 0
    final = {i["id"]: i for i in I.load_items(lib_p, ph_p)}
    assert not [i for i in final.values() if i["audit"]["status"] == "pending"]
    assert (tmp_path / "p4" / "audit" / "pending_p3" / "audit.md").is_file()
    C.validate(json.loads(lib_p.read_text()), complete=False)


def gso_zip(path: Path, name: str, licence_text: str = "") -> Path:
    v, t = box_mesh(0.2, 0.2, 0.08, -0.1, -0.1)
    obj = "mtllib model.mtl\no m\n" + "".join("v %g %g %g\n" % p for p in v) + "usemtl m\n" + \
        "".join("f %d %d %d\n" % (a + 1, b + 1, c + 1) for a, b, c in t)
    from io import BytesIO

    from PIL import Image
    png = BytesIO()
    Image.new("RGB", (8, 8), (200, 180, 120)).save(png, format="PNG")
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(f"{name}/meshes/model.obj", obj)
        z.writestr(f"{name}/meshes/model.mtl", "newmtl m\nmap_Kd ../materials/textures/missing.png\n")
        z.writestr(f"{name}/materials/textures/texture.png", png.getvalue())
        z.writestr(f"{name}/model.config", f"<model><name>{name}</name><author><name>Google</name></author></model>")
        if licence_text:
            z.writestr(f"{name}/LICENSE.txt", licence_text)
    return path


def test_gso_licence_and_conversion_steps(tmp_path):
    a = run_args(tmp_path, workers=2, no_fuel=True)
    zips = tmp_path / "g" / "gso" / "zips"
    zips.mkdir(parents=True)
    ok = gso_zip(zips / "Footed_Bowl_Sand.zip", "Footed_Bowl_Sand", "Licensed under CC BY 4.0 "
                 "(https://creativecommons.org/licenses/by/4.0/).")
    no = gso_zip(zips / "Target_Basket_Medium.zip", "Target_Basket_Medium")
    recs = [{"id": "gso_Footed_Bowl_Sand", "ok": True, "path": str(ok), "sha256": GR.sha256_file(ok)},
            {"id": "gso_Target_Basket_Medium", "ok": True, "path": str(no), "sha256": GR.sha256_file(no)},
            {"id": "gso_Footed_Bowl_Sand_missing", "ok": False, "error": "HTTPError: 404"}]
    (tmp_path / "g" / "report").mkdir(parents=True)
    (tmp_path / "g" / "report" / "ingest_gso.json").write_text(json.dumps({"records": recs}))
    assert GR.cmd_gso_licence(a) == 0
    rep = json.loads((tmp_path / "g" / "report" / "gso_licences.json").read_text())
    by = {r["id"]: r for r in rep["records"]}
    assert rep["kept"] == 1 and by["gso_Footed_Bowl_Sand"]["kept"]
    assert by["gso_Footed_Bowl_Sand"]["evidence"][0]["file"] == "Footed_Bowl_Sand/LICENSE.txt"
    assert not by["gso_Target_Basket_Medium"]["kept"] and "not asked" in by["gso_Target_Basket_Medium"]["reason"]
    assert "not downloaded" in by["gso_Footed_Bowl_Sand_missing"]["reason"]
    assert "| gso_Footed_Bowl_Sand | yes |" in (tmp_path / "g" / "report" / "gso_licences.md").read_text()
    assert GR.cmd_gso_licence(a) == 0                                          # resume: archives not unpacked again
    from wenart.blender import cli as BC
    blender = BC.find_blender()
    if blender is None:
        pytest.skip("no Blender binary (WENART_BLENDER) for the conversion")
    a.source, a.blender = "gso", blender
    assert GR.cmd_convert(a) == 0
    conv = json.loads((tmp_path / "g" / "report" / "convert_gso.json").read_text())
    r = conv["results"]["gso_Footed_Bowl_Sand"]
    assert r["ok"] and r["glb"] == "models/gso/gso_Footed_Bowl_Sand.glb" and r["fallback_textures"] == 1
    glb = tmp_path / "assets" / r["glb"]
    m = GM.measure(glb)
    assert m["bbox_model_m"] == [0.2, 0.2, 0.08] and m["info"]["textured"]       # Z up kept, metres
    assert GR.cmd_convert(a) == 0                                                # resume: nothing converted again
    assert json.loads((tmp_path / "g" / "report" / "convert_gso.json").read_text())["redone"] == 0


def test_catalogue_step_m13_relinks_2k_previews_vegetation_and_builds_hssd_entries(tmp_path):
    """Milestone 13 (track T7): the Poly Haven models fetched again at 2K are relinked in the copy (never re-made as
    pending entries), vegetation models are previews (no furniture entry), HSSD records become ``source: hssd``
    entries with the CC BY-NC 4.0 flags (or are dropped by catalog.validate until the lead adds the source)."""
    from wenart.assets import hssd as H
    a = fixture_growth(tmp_path)
    assets, g, lists = tmp_path / "assets", tmp_path / "g", tmp_path / "lists"
    rep = g / "report"
    ph_doc = json.loads(I.POLYHAVEN_PATH.read_text(encoding="utf-8"))
    sofa = next(e for e in ph_doc["entries"] if e["id"] == "sofa_02")
    gl2k = write_gltf(assets / "models" / "sofa_02", "sofa_02", *box_mesh(1.8, 0.8, 0.7))
    rel2k = gl2k.relative_to(assets).as_posix().replace("_1k", "_2k")
    (assets / rel2k).write_bytes(gl2k.read_bytes())
    veg = write_gltf(assets / "models" / "jacaranda_tree", "jacaranda_tree", *box_mesh(2.0, 2.0, 9.0))
    (rep / "ingest_polyhaven_m13.json").write_text(json.dumps({"records": [
        {"id": "sofa_02", "ok": True, "gltf": rel2k, "sha256": {"gltf": "f" * 64}, "size": "2k"},
        {"id": "jacaranda_tree", "ok": True, "gltf": veg.relative_to(assets).as_posix(), "sha256": {}, "size": "2k"}],
        "approved": 2, "ok": 2}))
    (lists / "growth" / "candidates_polyhaven_m13.json").write_text(json.dumps({"candidates": [
        {"id": "jacaranda_tree", "type": "tree", "kind": "vegetation", "licence": "CC0"}]}))
    hid = "c" * 40
    glb = write_glb(assets / "models" / "hssd" / f"hssd_{hid}.glb", *box_mesh(1.9, 0.9, 0.85), textured=True)
    (lists / "growth" / "candidates_hssd.json").write_text(json.dumps({"candidates": [
        {"id": f"hssd_{hid}", "hssd_id": hid, "title": "Taylor Sofa", "type": "sofa", "kind": "furniture",
         "bin": "2.00x0.90", "demand": 4, "projects": ["real02"], "dims_m": [1.9, 0.9, 0.85], "fits_caps": True,
         "multi": False, "articulated": False, "found_in": "living room", "synset": "sofa.n.01",
         "path": f"objects/c/{hid}.glb", "pick": True}]}))
    (rep / "ingest_hssd.json").write_text(json.dumps({"records": [
        {"id": f"hssd_{hid}", "hssd_id": hid, "ok": True, "glb": f"models/hssd/hssd_{hid}.glb",
         "sha256": GR.sha256_file(glb)}], "approved": 1, "ok": 1}))
    assert GR.cmd_catalogue(a) == 0
    ph = json.loads((tmp_path / "p4" / "audit" / "catalogue" / "catalog.json").read_text())
    lib = json.loads((tmp_path / "p4" / "audit" / "catalogue" / "catalog_library.json").read_text())
    C.validate(ph, complete=True)
    C.validate(lib, complete=False)
    sofa_after = next(e for e in ph["entries"] if e["id"] == "sofa_02")
    assert sofa_after["gltf"] == rel2k and sofa_after["gltf_1k"] == sofa["gltf"] and sofa_after["resolution"] == "2k"
    assert sofa_after.get("audit") == sofa.get("audit")                     # relinked, not re-made
    assert sum(1 for e in ph["entries"] if e.get("id") == "sofa_02") == 1          # parametric rows have no id
    rep_doc = json.loads((rep / "catalogue.json").read_text())
    assert rep_doc["stats"]["polyhaven_relinked_2k"] == 1
    assert any(p["id"] == "jacaranda_tree" and p["kind"] == "vegetation" for p in rep_doc["previews"])
    assert not any(e.get("id") == "jacaranda_tree" for e in ph["entries"] + ph["decor"])
    hssd = [e for e in lib["entries"] if e.get("source") == "hssd"]
    if "hssd" in C.SOURCES:
        assert len(hssd) == 1 and hssd[0]["licence_flag"] == "non_commercial" and hssd[0]["commercial_safe"] is False
        assert hssd[0]["audit"]["status"] == "pending" and hssd[0]["pbr_maps"]["base_colour"] is True
        assert "hssd" in lib["sources"] and lib["datasets"]["hssd"]["licence"] == "CC-BY-NC-4.0"
        assert any(H.DATASET["name"] in n or "HSSD" in n for n in lib["notes"])
    else:
        why = {d["id"]: d["reason"] for d in rep_doc["dropped"]}
        assert "refused by catalog.validate" in why[f"hssd_{hid}"] and "hssd" in why[f"hssd_{hid}"]
