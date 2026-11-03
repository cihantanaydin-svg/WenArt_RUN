"""3 Nov 2026 (the user: "Include into the library (the proper ones) and also open up a new ranking tab in the ranking
page for them so I can rank them"): the Syncronia models of the user's beds.zip as a library source
(wenart.assets.syncronia, wenart.assets.part_materials), their own studio batch and their own tab on the ranking page.
CPU only (Assimp for the 3DS test when installed)."""
import importlib.util
import io
import json
import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from wenart.assets import part_materials as PM
from wenart.assets import syncronia as SY
from wenart.assets import warehouse as WH
from wenart.assets.audit import studio as S
from wenart.furniture import catalog as C
from wenart.furniture import fit as F

ROOT = Path(__file__).resolve().parents[1]
HAS_ASSIMP = shutil.which("assimp") is not None


def _box(x0, y0, z0, x1, y1, z1):
    v = [(x, y, z) for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)]
    f = [(1, 2, 4, 3), (5, 7, 8, 6), (1, 5, 6, 2), (3, 4, 8, 7), (1, 3, 7, 5), (2, 6, 8, 4)]
    return v, f


def bed_obj(path: Path, cm: bool = True) -> None:
    """A double bed 170 x 215 cm in centimetres, Z up as 3DS, its head on +Y: frame, headboard, mattress, duvet, two
    pillows and four feet, each an object with a name that says nothing (Box01 ...)."""
    s = 1.0 if cm else 0.01
    parts = {"Box01": (0, 0, 8, 170, 215, 30),                   # frame (touches the feet, low)
             "Box02": (0, 205, 8, 170, 215, 120),                # headboard (+Y, tall, thin)
             "Box03": (5, 5, 30, 165, 200, 52),                  # mattress (floats, covers the footprint)
             "Box04": (3, 3, 50, 167, 160, 56),                  # duvet
             "Box05": (15, 165, 52, 80, 200, 68),                # pillow
             "Box06": (90, 165, 52, 155, 200, 68),               # pillow
             "Box07": (2, 2, 0, 8, 8, 8), "Box08": (162, 2, 0, 168, 8, 8),
             "Box09": (2, 207, 0, 8, 213, 8), "Box10": (162, 207, 0, 168, 213, 8)}
    lines, n = [], 0
    for name, b in parts.items():
        v, f = _box(*[c * s for c in b])
        lines.append(f"o {name}")
        lines += [f"v {x:g} {y:g} {z:g}" for x, y, z in v]
        # 6 quads, subdivided enough that the model is not "very low poly" as a whole
        lines += ["f " + " ".join(str(n + i) for i in q) for q in f]
        n += 8
    # a dense extra object so the whole model passes the low-poly floor of zip_inspect.verdict
    path.write_text("\n".join(lines) + "\n")


def build_zip(tmp_path: Path) -> Path:
    src = tmp_path / "src"
    src.mkdir()
    bed_obj(src / "bed.obj")
    subprocess.run(["assimp", "export", str(src / "bed.obj"), str(src / "14386.3ds"), "-f3ds"], check=True,
                   capture_output=True)
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, "w") as zf:
        zf.write(src / "14386.3ds", "14386.3ds")
    meta = {"title": "Beds, Demetra", "brand": "maxalto", "type": "beds",
            "source": "https://www.syncronia.com/en/3d-bim-cad-models-beds/maxalto/demetra",
            "licence": "Manufacturer model from Syncronia, for use in a design project and its renders.",
            "terms": "https://www.syncronia.com/en"}
    z = tmp_path / "beds.zip"
    with zipfile.ZipFile(z, "w") as zf:
        zf.writestr("beds/maxalto/demetra/14386.3ds.zip", inner.getvalue())
        zf.writestr("beds/maxalto/demetra/meta.json", json.dumps(meta))
        zf.writestr("beds/maxalto/sileo/85138.skp.zip", b"PK\x05\x06" + b"\x00" * 18)   # an empty zip
        zf.writestr("beds/maxalto/sileo/meta.json", json.dumps({"title": "Beds, Sileo", "type": "beds"}))
    return z


def test_the_source_is_registered_everywhere():
    from wenart.assets import fetch
    from wenart.assets import models as M
    from wenart.blender import furniture as BF
    from wenart.run import copy as CP
    assert SY.SOURCE in C.SOURCES and SY.SOURCE in C.LIBRARY_SOURCES
    assert set(CP.LIBRARY_SOURCES) == set(C.LIBRARY_SOURCES) == set(M.LIBRARY_SOURCES)
    assert C.SOURCE_LICENCES[SY.SOURCE] == (SY.LICENCE,) and BF.MODEL_LICENCES[SY.SOURCE] == (SY.LICENCE,)
    assert C.licence_flag_of({"licence": SY.LICENCE}) == "non_commercial"
    assert fetch.check_licence(SY.SOURCE, SY.LICENCE, kind="models",
                               entry={k: "x" for k in fetch.CC_BY_FIELDS} | {"id": "syncronia_x",
                                                                            "licence_flag": "non_commercial"})
    assert SY.SOURCE in F.SOURCE_ORDER and SY.SOURCE in BF.FLAGGED_SOURCES
    assert "Syncronia" in SY.notice()


def test_bed_parts_are_classified_by_geometry():
    lo, hi = [-0.85, -1.075, 0.0], [0.85, 1.075, 1.2]
    def part(mn, mx, name=""):
        return {"key": [0, 0], "node": name, "mesh_name": "", "material_name": "", "min": mn, "max": mx,
                "tris": 12, "area": 1.0}
    assert PM.bed_geometry(part([-0.83, -1.05, 0.0], [-0.77, -0.99, 0.08]), lo, hi) == "legs"
    assert PM.bed_geometry(part([-0.85, 0.975, 0.08], [0.85, 1.075, 1.2]), lo, hi) == "headboard"
    assert PM.bed_geometry(part([-0.8, -1.0, 0.3], [0.8, 0.95, 0.52]), lo, hi) == "bedding"
    assert PM.bed_geometry(part([-0.7, 0.6, 0.52], [-0.05, 0.95, 0.68]), lo, hi) == "bedding"
    assert PM.bed_geometry(part([-0.85, -1.075, 0.08], [0.85, 1.075, 0.30]), lo, hi) == "frame"
    # a side rail above the floor is no pillow (too thin)
    assert PM.bed_geometry(part([-0.85, -1.0, 0.2], [-0.78, 0.9, 0.35]), lo, hi) == "frame"
    # names win over geometry, in Italian too
    assert PM.by_name(part(lo, hi, "Cuscino_01")) == "bedding" and PM.by_name(part(lo, hi, "piede")) == "legs"
    assert PM.classify([part(lo, hi)], "sofa") == []


def test_a_textured_or_coloured_model_keeps_its_materials():
    assert PM.needs_materials({"materials": [{"pbrMetallicRoughness": {"baseColorFactor": [1, 1, 1, 1]}}]})
    assert PM.needs_materials({"materials": [{}]})
    # one colour for the whole model (an exporter's default) says nothing either; two colours do
    assert PM.needs_materials({"materials": [{"pbrMetallicRoughness": {"baseColorFactor": [0.6, 0.6, 0.6, 1]}}]})
    assert not PM.needs_materials({"materials": [{"pbrMetallicRoughness": {"baseColorFactor": [0.3, 0.2, 0.1, 1]}},
                                                 {"pbrMetallicRoughness": {"baseColorFactor": [0.9, 0.9, 0.9, 1]}}]})
    assert not PM.needs_materials({"materials": [{}], "images": [{"uri": "a.png"}], "textures": [{"source": 0}]})


@pytest.mark.skipif(not HAS_ASSIMP, reason="assimp not installed")
def test_ingest_takes_the_proper_bed_with_part_materials_and_a_valid_entry(tmp_path):
    z = build_zip(tmp_path)
    res = SY.ingest(z, tmp_path / "work", tmp_path / "assets", tmp_path / "out")
    taken = [r for r in res["records"] if r["taken"]]
    assert len(taken) == 1 and len(res["entries"]) == 1
    e = res["entries"][0]
    assert e["source"] == "syncronia" and e["type"] == "bed_double" and e["id"].startswith(SY.UID_PREFIX)
    assert e["glb"] == f"models/syncronia/{e['id']}.glb" and (tmp_path / "assets" / e["glb"]).is_file()
    assert sorted(e["bbox_model_m"][:2]) == pytest.approx([1.70, 2.15], abs=0.01)
    assert e["units_known"] and e["syncronia"]["unit"] == "centimetres"
    # the head is on +Y: the front is -Y, from the headboard
    assert e["front_axis"] == "-Y" and "headboard" in e["front_axis_note"]
    assert e["has_mattress"] and e["has_bedding"] and e["has_pillows"] and e["bed_frame"] is False
    cls = e["syncronia"]["part_classes"]
    assert cls["legs"] == 4 and cls["headboard"] == 1 and cls["bedding"] == 4 and cls["frame"] == 1
    # the part materials: the upholstery is a separable fabric slot (recoloured by the fit), the bedding stays white
    assert e["recolourable_fabric"] is True and "fabric" in e["material_tags"]
    slots = {s["name"]: s for s in e["material_slots"]}
    assert slots["wenart_legs_bronze"]["material"] == "metal"      # a tag only from 5 % of the surface (small feet)
    assert slots["wenart_upholstery_fabric"]["material"] == "fabric"
    assert slots["wenart_bedding_linen"]["material"] == "other"
    doc, _ = WH.read_glb(tmp_path / "assets" / e["glb"])
    assert {m["name"] for m in doc["materials"]} >= {"wenart_bedding_linen", "wenart_upholstery_fabric",
                                                    "wenart_legs_bronze"}
    assert e["sha256_glb"] == WH.sha256_file(tmp_path / "assets" / e["glb"])
    assert e["audit"]["status"] == "pending" and not C.usable(e, "relaxed")
    assert "Maxalto" in e["title"] and "Demetra" in e["title"] and "170 x 215" in e["title"]
    # the SketchUp file is listed, not taken, with the reason
    skp = [r for r in res["records"] if r["format"] == ".skp"]
    assert all(not r["taken"] and "SketchUp" in r["why"] for r in skp)
    # the entry passes the catalogue's own validation next to the real catalogue
    cat = json.loads((ROOT / "wenart/furniture/catalog_library.json").read_text(encoding="utf-8"))
    path = tmp_path / "catalog_library.json"
    path.write_text(json.dumps(cat), encoding="utf-8")
    assert SY.merge(res["entries"], path) == {"added": 1, "replaced": 0}
    assert SY.merge(res["entries"], path) == {"added": 0, "replaced": 1}
    merged = json.loads(path.read_text(encoding="utf-8"))
    C.validate({"entries": [x for x in merged["entries"] if x.get("source") == "syncronia"]}, complete=False)
    assert "syncronia" in merged["sources"] and merged["counts"]["syncronia"]["entries"] == 1
    # the studio batch sees it while pending; the review makes it usable
    rows = S.source_entries("syncronia", entries=merged["entries"])
    assert [r["id"] for r in rows] == [e["id"]] and rows[0]["tab"] == "syncronia"
    SY.review({e["id"]: {"status": "keep", "notes": ["looks right"]}}, path)
    kept = next(x for x in json.loads(path.read_text())["entries"] if x["id"] == e["id"])
    assert kept["audit"]["status"] == "keep" and C.usable(kept, "relaxed") and not C.usable(kept, "commercial")
    SY.review({e["id"]: {"status": "removed", "reasons": ["not a bed"]}}, path)
    gone = json.loads(path.read_text())["entries"]
    assert S.source_entries("syncronia", entries=gone) == []


def test_a_source_batch_gets_its_own_sheets_index_tab_and_group(tmp_path):
    e = {"id": "syncronia_abc", "type": "bed_double", "tab": "syncronia", "bbox_m": [1.7, 2.15, 1.2],
         "title": "Maxalto Demetra bed 170 x 215", "source": "syncronia"}
    sheets = S.sheet_plan([e])
    assert sheets[0]["sheet"] == "syncronia-01" and sheets[0]["type"] == "syncronia"
    idx = S.index_doc([e], sheets)
    assert idx["types"] == ["syncronia"] and idx["models"]["syncronia_abc"]["tab"] == "syncronia"
    assert idx["models"]["syncronia_abc"]["type"] == "bed_double"
    assert S.tab_group("syncronia") == S.GROUP_NEW
    # the page: the new tab first, under its readable name
    spec = importlib.util.spec_from_file_location("ranking_page", ROOT / "scripts" / "ranking_page.py")
    RP = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(RP)
    rk = tmp_path / "ranking"
    (rk / "sheets").mkdir(parents=True)
    (rk / "ranking_index_syncronia.json").write_text(json.dumps(idx), encoding="utf-8")
    other = S.index_doc([dict(e, id="abo_x", tab=None, source="abo")], S.sheet_plan([dict(e, id="abo_x", tab=None)]))
    (rk / "ranking_index.json").write_text(json.dumps(other), encoding="utf-8")
    out = tmp_path / "page" / "index.html"
    assert RP.main(["--ranking", str(rk), "--out", str(out)]) == 0
    html = out.read_text(encoding="utf-8")
    assert "Syncronia beds (beds.zip)" in html and S.GROUP_NEW in html
    assert html.index("Syncronia beds (beds.zip)") < html.index(RP.type_name("bed_double"))
    assert RP.type_name("syncronia") == "Syncronia beds (beds.zip)"


def test_the_job_script_ingests_before_the_studio():
    text = (ROOT / "scripts/jobs/library_ranking.sh").read_text(encoding="utf-8")
    assert 'RANK_BATCH" = "syncronia"' in text and "wenart.assets.syncronia ingest" in text
    assert text.index("wenart.assets.syncronia ingest") < text.index("studio plan")
    assert "syncronia" in S.SOURCE_BATCHES
