"""CPU tests for the synthetic project generator (docs/milestone2.md §1).

The generator runs once into a temp folder (module fixture). Tests then check
files, schema validity, DXF content via ezdxf, PDF content via pdfplumber,
raster sizes and ink under the truth boxes, determinism, and that the
committed projects/ folder matches a fresh run.
"""
import json
import shutil
import subprocess
from pathlib import Path

import ezdxf
import numpy as np
import pdfplumber
import pytest
from ezdxf import recover
from PIL import Image

from wenart import building as B
from wenart import geometry as G
from wenart.synthetic import blocks
from wenart.synthetic.dxf_writer import dimension_printed_text
from wenart.synthetic.generate import generate_project, main
from wenart.synthetic.projects import all_projects

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "projects"
NAMES = ["synthetic-01", "synthetic-02", "synthetic-03"]

EXPECTED_FILES = {
    "synthetic-01": ["zemin_kat.dxf", "1_kat.pdf", "1_kat_scan.png", "brief.yaml", "truth/building.json", "truth/pages.json"],
    "synthetic-02": ["plan_scan.png", "plan_photo.jpg", "truth/plan.pdf", "truth/building.json", "truth/pages.json"],
    "synthetic-03": ["kat_planlari.pdf", "mobilya_plani.dxf", "brief.yaml", "truth/building.json", "truth/pages.json"],
}


@pytest.fixture(scope="module")
def generated(tmp_path_factory):
    out = tmp_path_factory.mktemp("projects")
    results = tmp_path_factory.mktemp("results")
    for project in all_projects():
        generate_project(project, out, results)
    return out, results


def truth(generated, name):
    return B.load(generated[0] / name / "truth" / "building.json")


def pages(generated, name):
    return json.loads((generated[0] / name / "truth" / "pages.json").read_text(encoding="utf-8"))["pages"]


# --------------------------------------------------------------------------
# Files, schema, determinism
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", NAMES)
def test_files_exist(generated, name):
    out = generated[0] / name
    for rel in EXPECTED_FILES[name]:
        assert (out / rel).is_file(), rel
    assert (out / "brief.yaml").exists() == (name != "synthetic-02")


@pytest.mark.parametrize("name", NAMES)
def test_truth_validates_against_schema(generated, name):
    b = truth(generated, name)  # B.load validates
    assert b["status"] == "ok"
    assert b["project"]["id"] == name and b["project"]["source_folder"] == f"projects/{name}"


def test_counts_match_spec(generated):
    b1 = truth(generated, "synthetic-01")
    assert [lv["id"] for lv in b1["levels"]] == ["L0", "L1"]
    assert sum(1 for r in b1["rooms"] if r["level_id"] == "L0") == 5
    assert sum(1 for r in b1["rooms"] if r["level_id"] == "L1") == 5
    furnished = {r["id"] for r in b1["rooms"] if r["has_documented_furniture"]}
    assert furnished == {"r_L0_salon", "r_L0_yatak_odasi", "r_L0_banyo"}
    assert all(f["level_id"] == "L0" for f in b1["furniture"])
    salon = next(r for r in b1["rooms"] if r["id"] == "r_L0_salon")
    assert salon["label_raw"] == "SALON 24,50 m²" and salon["area_label"] == 24.5 and salon["area_computed"] == 24.5
    assert b1["project"]["brief"]["style"].startswith("Scandinavian")

    b2 = truth(generated, "synthetic-02")
    assert len(b2["levels"]) == 1 and "brief" not in b2["project"]
    assert {r["label"] for r in b2["rooms"]} == {"Salon", "Yatak Odası", "Mutfak", "Banyo", "Antre"}
    assert all(r["has_documented_furniture"] for r in b2["rooms"])
    assert [d["file"] for d in b2["documents"]] == ["plan_scan.png", "plan_photo.jpg"]

    b3 = truth(generated, "synthetic-03")
    assert [lv["id"] for lv in b3["levels"]] == ["L-1", "L0", "L1"]
    assert [lv["label"] for lv in b3["levels"]] == ["Bodrum Kat", "Zemin Kat", "1. Kat"]
    assert len(b3["project"]["brief"]["styles"]) == 2
    assert [c["kind"] for c in b3["conflicts"]] == ["area_label_vs_computed", "dimension_vs_measured", "count_mismatch"]
    unknown = [f for f in b3["furniture"] if f["type"] == "unknown"]
    assert len(unknown) == 1 and unknown[0]["type_raw"] == "BLOK_A" and unknown[0]["status"] == "unverified"
    assert b3["unverified"] == [unknown[0]["id"]]
    assert {r["id"] for r in b3["rooms"] if r["level_id"] == "L-1"} >= {"r_L-1_kiler", "r_L-1_kiler_2"}


def test_deterministic(generated, tmp_path):
    out2 = tmp_path / "again"
    for project in all_projects():
        generate_project(project, out2, None)
    for name in NAMES:
        for rel in EXPECTED_FILES[name]:
            a = (generated[0] / name / rel).read_bytes()
            b = (out2 / name / rel).read_bytes()
            assert a == b, f"{name}/{rel} differs between runs"


@pytest.mark.skipif(not COMMITTED.exists(), reason="projects/ not present")
@pytest.mark.parametrize("name", NAMES)
def test_committed_projects_are_current(generated, name):
    for rel in EXPECTED_FILES[name]:
        committed = COMMITTED / name / rel
        assert committed.is_file(), f"run python -m wenart.synthetic.generate --out projects ({rel} missing)"
        assert committed.read_bytes() == (generated[0] / name / rel).read_bytes(), \
            f"{name}/{rel} is stale: run python -m wenart.synthetic.generate --out projects"


def test_cli_runs(tmp_path):
    assert main(["--out", str(tmp_path / "p"), "--results", "", "--only", "synthetic-02"]) == 0
    assert (tmp_path / "p" / "synthetic-02" / "plan_photo.jpg").is_file()
    assert not (tmp_path / "p" / "synthetic-01").exists()


# --------------------------------------------------------------------------
# Geometry consistency of the truth
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name", NAMES)
def test_truth_geometry_is_consistent(generated, name):
    b = truth(generated, name)
    walls = {w["id"]: w for w in b["walls"]}
    rooms = {r["id"]: r for r in b["rooms"]}
    for o in b["openings"]:
        w = walls[o["wall_id"]]
        assert w["level_id"] == o["level_id"]
        assert G.point_segment_distance(o["center"], w["start"], w["end"]) < 1e-6
        if o["type"] == "door":
            assert o["swing_side"] in rooms and rooms[o["swing_side"]]["level_id"] == o["level_id"]
        else:
            assert o["swing_side"] is None
    for f in b["furniture"]:
        room = rooms[f["room_id"]]
        corners = G.rotated_rectangle(f["footprint"]["center"], f["footprint"]["size"], f["footprint"]["rotation_deg"])
        assert all(G.point_in_polygon(c, room["polygon"]) for c in corners), f["id"]
        assert f["source"] == "from_documents"
        if f["type"] != "unknown":
            assert f["front_deg"] == G.front_direction_deg(f["footprint"]["rotation_deg"])
            assert f["type"] == blocks.furniture_type(f["type_raw"])
            assert tuple(f["footprint"]["size"]) == blocks.furniture_size(f["type_raw"])
    for r in b["rooms"]:
        assert abs(G.polygon_area(r["polygon"]) - r["area_computed"]) < 1e-3
        if r["area_label"] is not None:
            assert abs(r["area_label"] - r["area_computed"]) / r["area_label"] <= 0.03
        assert any(e["method"] == "derived" for e in r["evidence"])
    for e in b["walls"] + b["openings"] + b["rooms"] + b["furniture"]:
        assert e["evidence"], e["id"]


# --------------------------------------------------------------------------
# DXF
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name, file", [("synthetic-01", "zemin_kat.dxf"), ("synthetic-03", "mobilya_plani.dxf")])
def test_dxf_content(generated, name, file):
    path = generated[0] / name / file
    doc, auditor = recover.readfile(str(path))
    assert not auditor.has_errors
    assert doc.header["$INSUNITS"] == 4
    assert set(blocks.LAYERS) <= {layer.dxf.name for layer in doc.layers}
    msp = doc.modelspace()
    b = truth(generated, name)
    page = next(p for p in pages(generated, name) if p["file"] == file)
    level_id = page["level_id"]
    level_walls = [w for w in b["walls"] if w["level_id"] == level_id]
    level_openings = [o for o in b["openings"] if o["level_id"] == level_id]
    level_furniture = [f for f in b["furniture"] if f["level_id"] == level_id]

    # Walls: closed 4-point LWPOLYLINEs on DUVAR whose centre line matches the truth within 5 mm.
    polylines = {e.dxf.handle: e for e in msp.query("LWPOLYLINE")}
    assert len(polylines) == len(level_walls)
    for w in level_walls:
        ev = next(e for e in w["evidence"] if e["file"] == file)
        ent = polylines[ev["entity"].split(":")[1]]
        assert ent.dxf.layer == "DUVAR" and ent.closed and len(ent) == 4
        start, end, t = G.rectangle_to_centerline([(p[0] / 1000, p[1] / 1000) for p in ent.get_points("xy")])
        assert G.distance(start, w["start"]) < 0.005 and G.distance(end, w["end"]) < 0.005
        assert abs(t - w["thickness"]) < 0.005

    # Openings and furniture: INSERTs with block name, position and rotation.
    inserts = {e.dxf.handle: e for e in msp.query("INSERT")}
    assert len(inserts) == len(level_openings) + len(level_furniture)
    for o in level_openings:
        ev = next(e for e in o["evidence"] if e["file"] == file)
        ent = inserts[ev["entity"].split(":")[1]]
        kind, width = blocks.opening_from_block(ent.dxf.name)
        assert kind == o["type"] and width == o["width"] and ent.dxf.name == ev["block"]
        assert ent.dxf.layer == ("KAPI" if kind == "door" else "PENCERE")
        assert G.distance((ent.dxf.insert.x / 1000, ent.dxf.insert.y / 1000), o["center"]) < 0.001
    for f in level_furniture:
        ev = next(e for e in f["evidence"] if e["file"] == file)
        ent = inserts[ev["entity"].split(":")[1]]
        assert ent.dxf.name == f["type_raw"] and ent.dxf.layer == "MOBILYA"
        assert G.distance((ent.dxf.insert.x / 1000, ent.dxf.insert.y / 1000), f["footprint"]["center"]) < 0.001
        assert G.angle_difference_deg(ent.dxf.rotation, f["footprint"]["rotation_deg"]) < 1e-6
        # The block definition carries the footprint rectangle (used for unknown blocks).
        rect = next(e for e in doc.blocks.get(ent.dxf.name) if e.dxftype() == "LWPOLYLINE")
        box = G.bbox([(p[0] / 1000, p[1] / 1000) for p in rect.get_points("xy")])
        assert abs((box[2] - box[0]) - f["footprint"]["size"][0]) < 1e-6
        assert abs((box[3] - box[1]) - f["footprint"]["size"][1]) < 1e-6
    used_blocks = {e.dxf.name for e in inserts.values()}
    defined = {blk.name for blk in doc.blocks if not blk.name.startswith("*") and not blk.name.startswith("_")}
    assert used_blocks == defined

    # Texts: title, scale and one label per room, on YAZI.
    texts = {e.dxf.handle: e for e in msp.query("TEXT")}
    assert all(e.dxf.layer == "YAZI" for e in texts.values())
    text_values = {e.dxf.text for e in texts.values()}
    assert page["level_label_raw"] in text_values and "ÖLÇEK 1/100" in text_values
    for r in (r for r in b["rooms"] if r["level_id"] == level_id):
        ev = next(e for e in r["evidence"] if e["file"] == file)
        assert texts[ev["entity"].split(":")[1]].dxf.text == r["label_raw"]
        assert G.point_in_polygon((texts[ev["entity"].split(":")[1]].dxf.insert.x / 1000,
                                   texts[ev["entity"].split(":")[1]].dxf.insert.y / 1000), r["polygon"])

    # Dimensions: aligned DIMENSION entities on OLCU; printed text = metres with comma.
    dims = list(msp.query("DIMENSION"))
    assert len(dims) == len(page["dimensions"])
    assert all(d.dxf.layer == "OLCU" for d in dims)
    printed = sorted(dimension_printed_text(d) for d in dims)
    assert printed == sorted(d["printed"] for d in page["dimensions"])
    for d in dims:
        # ezdxf writes "aligned" dimensions as linear dimensions rotated to the
        # direction of the two definition points, so the measurement is their distance.
        assert d.dimtype in (0, 1)
        measured = d.get_measurement() / 1000
        p2, p3 = d.dxf.defpoint2, d.dxf.defpoint3
        assert abs(G.distance((p2.x, p2.y), (p3.x, p3.y)) / 1000 - measured) < 1e-6
        rec = next(r for r in page["dimensions"] if r["entity"] == f"DIMENSION:{d.dxf.handle}")
        assert abs(measured - rec["measured"]) < 1e-6


def test_dxf_furniture_plan_has_no_dimensions(generated):
    doc = ezdxf.readfile(str(generated[0] / "synthetic-03" / "mobilya_plani.dxf"))
    assert len(doc.modelspace().query("DIMENSION")) == 0
    titles = {e.dxf.text for e in doc.modelspace().query("TEXT")}
    assert "ZEMİN KAT MOBİLYA PLANI" in titles
    assert B.normalise_level_label("ZEMİN KAT MOBİLYA PLANI") == ("Zemin Kat", 0)


# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name, file, n_pages", [("synthetic-01", "1_kat.pdf", 1), ("synthetic-03", "kat_planlari.pdf", 3),
                                                 ("synthetic-02", "truth/plan.pdf", 1)])
def test_pdf_content(generated, name, file, n_pages):
    recs = [p for p in pages(generated, name) if p["file"] == file]
    b = truth(generated, name)
    with pdfplumber.open(str(generated[0] / name / file)) as pdf:
        assert len(pdf.pages) == n_pages == len(recs)
        for rec, page in zip(recs, pdf.pages):
            assert abs(page.width - 1190.55) < 0.1 and abs(page.height - 841.89) < 0.1  # A3 landscape
            text = page.extract_text()
            assert rec["level_label_raw"] in text and "ÖLÇEK 1/100" in text
            chars = page.chars
            for item in rec["texts"]:
                index = int(item["entity"].split(":")[1])
                got = "".join(ch["text"] for ch in chars[index:index + len(item["text"])])
                assert got == item["text"], (item, got)
                run = chars[index:index + len(item["text"])]
                box = [min(c["x0"] for c in run), min(page.height - c["bottom"] for c in run),
                       max(c["x1"] for c in run), max(page.height - c["top"] for c in run)]
                assert G.box_iou(box, item["box"]) > 0.5, (item["text"], box, item["box"])
            # Walls are closed rectangles with the wall line width; nothing else uses 0.5 pt.
            wall_rects = [r for r in page.rects if abs(r["linewidth"] - 0.5) < 1e-6]
            n_walls = sum(1 for w in b["walls"] if w["level_id"] == rec["level_id"])
            assert len(wall_rects) == n_walls == len(rec["walls"])
            for w in (w for w in b["walls"] if w["level_id"] == rec["level_id"]):
                box = next(x for x in rec["walls"] if x["id"] == w["id"])["box"]
                hit = [r for r in wall_rects if G.box_iou([r["x0"], page.height - r["bottom"], r["x1"], page.height - r["top"]], box) > 0.9]
                assert len(hit) == 1, w["id"]
            # Door arcs are the only curves on the page.
            n_doors = sum(1 for s in rec["symbols"] if s["type"] == "door")
            assert len(page.curves) == n_doors


def test_pdf_page_2_of_synthetic_03_misses_one_window(generated):
    b = truth(generated, "synthetic-03")
    rec = next(p for p in pages(generated, "synthetic-03") if p["file"] == "kat_planlari.pdf" and p["page"] == 2)
    windows_truth = [o for o in b["openings"] if o["level_id"] == "L0" and o["type"] == "window"]
    windows_pdf = [s for s in rec["symbols"] if s["type"] == "window"]
    assert len(windows_pdf) == len(windows_truth) - 1
    conflict = next(c for c in b["conflicts"] if c["kind"] == "count_mismatch")
    missing = conflict["element_ids"][0]
    assert missing not in {s["id"] for s in windows_pdf}
    win = next(o for o in windows_truth if o["id"] == missing)
    assert [e["file"] for e in win["evidence"]] == ["mobilya_plani.dxf"]


def test_dimension_conflict_in_bodrum_page(generated):
    b = truth(generated, "synthetic-03")
    rec = next(p for p in pages(generated, "synthetic-03") if p["file"] == "kat_planlari.pdf" and p["page"] == 1)
    bad = [d for d in rec["dimensions"] if abs(float(d["printed"].replace(",", ".")) - d["measured"]) > 1e-6]
    assert len(bad) == 1 and bad[0]["printed"] == "3,99" and bad[0]["measured"] == 3.8
    conflict = next(c for c in b["conflicts"] if c["kind"] == "dimension_vs_measured")
    assert conflict["element_ids"] == bad[0]["wall_ids"]
    good = [d for d in rec["dimensions"] if d not in bad]
    assert all(abs(float(d["printed"].replace(",", ".")) - d["measured"]) < 1e-6 for d in good)


# --------------------------------------------------------------------------
# Rasters and pages.json
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name, file, kind", [("synthetic-01", "1_kat_scan.png", "scan"),
                                              ("synthetic-02", "plan_scan.png", "scan"),
                                              ("synthetic-02", "plan_photo.jpg", "photo")])
def test_raster_pages(generated, name, file, kind):
    rec = next(p for p in pages(generated, name) if p["file"] == file)
    with Image.open(generated[0] / name / file) as im:
        assert im.mode == "L" and im.format == ("PNG" if kind == "scan" else "JPEG")
        assert [im.width, im.height] == rec["size"] == [2481, 1754]  # A3 at 150 dpi
        img = np.asarray(im, dtype=float)
    assert rec["kind"] == kind and rec["class"] == "floor_plan" and rec["units"] == "px"
    assert rec["transform"]["kind"] == ("affine" if kind == "scan" else "homography")
    h = rec["H_building_to_pixels"]
    assert len(h) == 3 and all(len(row) == 3 for row in h)
    if kind == "scan":
        assert rec["dpi"] == 150 and abs(rec["scale_metres_per_unit"] - 1 / 59.0551) < 1e-4
        assert G.apply_homography(h, (0, 0)) == pytest.approx(G.apply_affine(rec["transform"]["building_to_page"], (0, 0)))
    else:
        assert rec["dpi"] is None and rec["scale_metres_per_unit"] is None
    # The truth boxes must sit on ink: clearly darker pixels than the paper around them.
    for item in rec["texts"] + rec["symbols"]:
        x0, y0, x1, y1 = [int(round(v)) for v in item["box"]]
        crop = img[y0:y1, x0:x1]
        ring = img[max(0, y0 - 40):y1 + 40, max(0, x0 - 40):x1 + 40]
        paper = np.median(ring)
        assert crop.size > 0 and crop.min() < paper - 60, (item, crop.min(), paper)
        if item.get("role") in ("title", "room_label"):
            assert (crop < paper - 60).mean() > 0.03, item
    # The photo keeps a visible grey background around the warped paper.
    if kind == "photo":
        assert img[5:20, 5:20].mean() < 150


@pytest.mark.parametrize("name", NAMES)
def test_pages_json_structure(generated, name):
    recs = pages(generated, name)
    b = truth(generated, name)
    visible = [p for p in recs if not p.get("hidden")]
    assert len(visible) == sum(len(d["pages"]) for d in b["documents"])
    for p in recs:
        assert {"file", "page", "class", "kind", "level_id", "scale_metres_per_unit", "transform", "texts", "symbols"} <= set(p)
        assert p["transform"]["kind"] in ("affine", "homography")
        assert len(p["transform"]["building_to_page"]) == (6 if p["transform"]["kind"] == "affine" else 9)
        for t in p["texts"]:
            assert len(t["box"]) == 4 and t["box"][0] <= t["box"][2] and t["box"][1] <= t["box"][3]
        for s in p["symbols"]:
            assert {"id", "type", "block", "box", "rotation_deg"} <= set(s)
            assert s["type"] in ("door", "window") or s["type"] == blocks.furniture_type(s["block"])
        # Every symbol box maps back to the element's building position.
        if p["transform"]["kind"] == "affine":
            inv = G.invert_affine(p["transform"]["building_to_page"])
            for s in p["symbols"]:
                element = next(e for e in b["openings"] + b["furniture"] if e["id"] == s["id"])
                center = element.get("center") or element["footprint"]["center"]
                back = G.box_center(G.transform_box(inv, s["box"]))
                tolerance = 0.03 if p["units"] == "px" else 0.001
                if element.get("type") == "door":
                    # door boxes cover the swing square, not centred on the opening
                    assert G.distance(back, center) < element["width"] + tolerance
                else:
                    assert G.distance(back, center) < tolerance, (s["id"], back, center)


def test_documents_in_truth(generated):
    b = truth(generated, "synthetic-01")
    docs = {d["file"]: d for d in b["documents"]}
    assert docs["zemin_kat.dxf"]["format"] == "dxf" and docs["1_kat.pdf"]["format"] == "pdf"
    assert docs["1_kat_scan.png"]["format"] == "image"
    dxf_page = docs["zemin_kat.dxf"]["pages"][0]
    assert dxf_page["scale"]["method"] == "dxf_insunits" and dxf_page["scale"]["metres_per_unit"] == 0.001
    assert dxf_page["transform_to_building"] == [0.001, 0.0, 0.0, 0.0, 0.001, 0.0]
    pdf_page = docs["1_kat.pdf"]["pages"][0]
    assert pdf_page["scale"]["method"] == "pdf_scale_text" and pdf_page["level_id"] == "L1"
    assert pdf_page["evidence"][0]["text"] == "1. KAT PLANI"
    scan_page = docs["1_kat_scan.png"]["pages"][0]
    assert scan_page["kind"] == "scan" and scan_page["scale"]["evidence"]["method"] == "ocr"
    b2 = truth(generated, "synthetic-02")
    photo = next(d for d in b2["documents"] if d["file"] == "plan_photo.jpg")["pages"][0]
    assert photo["kind"] == "photo" and photo["scale"] is None and photo["transform_to_building"] is None


def test_previews_are_small(generated):
    results = generated[1]
    jpgs = sorted(results.glob("*.jpg"))
    assert len(jpgs) == 9
    for jpg in jpgs:
        assert jpg.stat().st_size <= 300 * 1024, jpg.name
        with Image.open(jpg) as im:
            assert im.width <= 1200
    assert not list(results.glob(".*.png"))  # no leftover temp files


def test_rendered_scan_looks_like_a_plan(generated):
    """A rendered page has a mostly white sheet with a small share of dark ink."""
    img = np.asarray(Image.open(generated[0] / "synthetic-02" / "plan_scan.png"), dtype=float)
    dark = (img < 128).mean()
    assert 0.002 < dark < 0.05
    assert shutil.which("pdftoppm")  # the generator depends on poppler
    out = subprocess.run(["pdftoppm", "-v"], capture_output=True, text=True)
    assert "pdftoppm" in (out.stdout + out.stderr)
