"""CPU tests for the synthetic project generator (docs/milestone2.md §1, docs/milestone6.md §3, docs/milestone7.md
§5.2, docs/milestone10.md §3.4).

The generator runs once into a temp folder (module fixture). Tests then check
files, schema validity, DXF content via ezdxf, PDF content via pdfplumber,
raster sizes and ink under the truth boxes, determinism, that the
committed projects/ folder matches a fresh run, the projects' counts,
the non-rectangular outline builder, the copied style photo, synthetic-06
(the CAD project delivered as a DWG, its truth and the titled fixture) and
synthetic-07 (one CAD sheet with every drawing kind: the truth files are checked
against the drawing itself, read back with ezdxf, never against the layout code).
"""
import json
import math
import re
import shutil
import subprocess
from collections import Counter
from pathlib import Path

import ezdxf
import numpy as np
import pdfplumber
import pytest
import yaml
from ezdxf import recover
from PIL import Image
from shapely.geometry import Point, Polygon

from wenart import building as B
from wenart import geometry as G
from wenart import units
from wenart.ingest import dwg as dwg_tool
from wenart.synthetic import blocks
from wenart.synthetic.dxf_writer import dimension_printed_text
from wenart.synthetic.generate import generate_project, generate_titled_fixture, main, write_style_photos
from wenart.synthetic.model import LevelBuilder, outer_wall_lines, wall_union
from wenart.synthetic.projects import (DWG_SHA256_06, INCH, OUTLINE_05, STYLE_PHOTO_05, Project, all_projects,
                                       feet_inches, plan_06, project_06)
from wenart.synthetic.sheet import project_07

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "projects"
# The Level-based projects (Milestones 2 and 6); synthetic-06 is drawn the CAD way and has tests of its own.
NAMES = ["synthetic-01", "synthetic-02", "synthetic-03", "synthetic-04", "synthetic-05"]
ALL_NAMES = NAMES + ["synthetic-06", "synthetic-07"]
HAS_DXF2DWG = dwg_tool.find_tool("dxf2dwg") is not None
TITLED_06 = ROOT / "tests" / "fixtures" / "synthetic-06-titled"

EXPECTED_FILES = {
    "synthetic-01": ["zemin_kat.dxf", "1_kat.pdf", "1_kat_scan.png", "brief.yaml", "truth/building.json", "truth/pages.json"],
    "synthetic-02": ["plan_scan.png", "plan_photo.jpg", "truth/plan.pdf", "truth/building.json", "truth/pages.json"],
    "synthetic-03": ["kat_planlari.pdf", "mobilya_plani.dxf", "brief.yaml", "truth/building.json", "truth/pages.json"],
    "synthetic-04": ["3_kat_plani.dxf", "3_kat_plani_pdf.pdf", "brief.yaml", "truth/building.json", "truth/pages.json"],
    "synthetic-05": ["zemin_kat.dxf", "zemin_kat_mobilya.dxf", "style_photos/salon_referans.jpg", "brief.yaml",
                     "truth/building.json", "truth/pages.json"],
    # The DWG is written by LibreDWG's dxf2dwg; where it is not built the generator skips it (and says so).
    "synthetic-06": (["synthetic-06.dwg"] if HAS_DXF2DWG else []) + ["source/synthetic-06.dxf", "brief.yaml",
                                                                      "truth/building.json", "truth/pages.json"],
    # One CAD sheet; its DWG copy is not a project document (source/), written where dxf2dwg exists.
    "synthetic-07": (["source/sheet.dwg"] if HAS_DXF2DWG else []) + [
        "sheet.dxf", "brief.yaml", "truth/building.json", "truth/sheets_truth.json", "truth/heights_truth.json",
        "truth/exterior_truth.json"],
}
# Preview JPEGs per project: one per visible page (results/synthetic/<project>_<file stem>_p<page>.jpg).
EXPECTED_PREVIEWS = {
    "synthetic-01": ["zemin_kat_p1", "1_kat_p1", "1_kat_scan_p1"],
    "synthetic-02": ["plan_scan_p1", "plan_photo_p1"],
    "synthetic-03": ["kat_planlari_p1", "kat_planlari_p2", "kat_planlari_p3", "mobilya_plani_p1"],
    "synthetic-04": ["3_kat_plani_p1", "3_kat_plani_pdf_p1"],
    "synthetic-05": ["zemin_kat_p1", "zemin_kat_mobilya_p1"],
    "synthetic-06": ["synthetic-06_p1"],
    "synthetic-07": ["sheet_p1"],
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

def test_all_projects_lists_seven():
    assert [p.name for p in all_projects()] == ALL_NAMES


@pytest.mark.parametrize("name", ALL_NAMES)
def test_files_exist(generated, name):
    out = generated[0] / name
    for rel in EXPECTED_FILES[name]:
        assert (out / rel).is_file(), rel
    assert (out / "brief.yaml").exists() == (name != "synthetic-02")
    # Nothing but the expected files (a stale or misnamed document would be read by the ingest).
    written = sorted(p.relative_to(out).as_posix() for p in out.rglob("*") if p.is_file())
    assert written == sorted(EXPECTED_FILES[name])
    assert (out / "style_photos").is_dir() == (name == "synthetic-05")


@pytest.mark.parametrize("name", ALL_NAMES)
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


def _counts(b) -> tuple:
    """(walls, exterior walls, openings, doors, windows, rooms, furniture, conflicts, unverified)."""
    return (len(b["walls"]), sum(w["exterior"] for w in b["walls"]), len(b["openings"]),
            sum(o["type"] == "door" for o in b["openings"]), sum(o["type"] == "window" for o in b["openings"]),
            len(b["rooms"]), len(b["furniture"]), len(b["conflicts"]), len(b["unverified"]))


def _wall_ids_of(b, room) -> set:
    """Walls whose rectangle touches the room polygon (as the generator's ``derive_rooms`` does)."""
    shp = Polygon(room["polygon"])
    return {w["id"] for w in b["walls"] if w["level_id"] == room["level_id"]
            and Polygon(G.centerline_to_rectangle(w["start"], w["end"], w["thickness"])).distance(shp) < 1e-6}


def _openings_on(b, room, kind: str) -> list:
    """Openings of ``kind`` in the room's walls along the room itself (not on a neighbour's stretch of a
    shared wall): the opening centre sits half the wall thickness from the room polygon."""
    walls = {w["id"]: w for w in b["walls"] if w["id"] in _wall_ids_of(b, room)}
    shp = Polygon(room["polygon"])
    return [o for o in b["openings"] if o["type"] == kind and o["wall_id"] in walls
            and shp.distance(Point(o["center"])) <= walls[o["wall_id"]]["thickness"] / 2 + 1e-6]


def _doors_on(b, room) -> list:
    return _openings_on(b, room, "door")


def _windows_on(b, room) -> list:
    return _openings_on(b, room, "window")


def test_counts_match_spec_synthetic_04(generated):
    """docs/milestone6.md §3.1: one level L3 drawn as DXF and vector PDF, two L-shaped rooms."""
    b = truth(generated, "synthetic-04")
    assert [(lv["id"], lv["label"], lv["elevation"]) for lv in b["levels"]] == [("L3", "3. Kat", 9.0)]
    assert _counts(b) == (10, 4, 15, 5, 10, 5, 21, 0, 0)
    assert b["project"]["brief"] == {"style": "Japandi, walnut floor, cream walls, warm daylight, linen and paper lamps"}
    assert [d["file"] for d in b["documents"]] == ["3_kat_plani.dxf", "3_kat_plani_pdf.pdf"]
    rooms = {r["id"]: r for r in b["rooms"]}
    expected = {  # id: (vertices, area, area label, documented pieces, doors on its walls, windows)
        "r_L3_salon_mutfak": (6, 39.05, 39.05, 14, 1, 5), "r_L3_hol": (6, 8.32, None, 0, 5, 0),
        "r_L3_yatak_odasi": (4, 20.21, None, 4, 1, 2), "r_L3_banyo": (4, 4.86, None, 3, 1, 1),
        "r_L3_cocuk_odasi": (4, 11.47, None, 0, 1, 2),
    }
    assert set(rooms) == set(expected)
    for room_id, (n, area, label_area, pieces, doors, windows) in expected.items():
        r = rooms[room_id]
        assert (len(r["polygon"]), r["area_computed"], r["area_label"]) == (n, area, label_area), room_id
        assert sum(f["room_id"] == room_id for f in b["furniture"]) == pieces, room_id
        assert r["has_documented_furniture"] == (pieces > 0)
        assert (len(_doors_on(b, r)), len(_windows_on(b, r))) == (doors, windows), room_id
    # The living room's five windows are on three walls.
    assert len({o["wall_id"] for o in _windows_on(b, rooms["r_L3_salon_mutfak"])}) == 3
    assert rooms["r_L3_salon_mutfak"]["room_type"] == "living"   # combined living + kitchen label
    kitchen = {f["type"] for f in b["furniture"] if f["room_id"] == "r_L3_salon_mutfak"}
    assert {"kitchen_counter", "sink_kitchen", "stove", "fridge"} <= kitchen  # kitchen pieces stay kitchen pieces
    armchair = next(f for f in b["furniture"] if f["type_raw"] == "KOLTUK")
    assert armchair["footprint"]["rotation_deg"] == 315.0 and armchair["front_deg"] == 225.0
    bathtub = next(f for f in b["furniture"] if f["type_raw"] == "KUVET")
    assert bathtub["type"] == "bathtub" and bathtub["room_id"] == "r_L3_banyo"
    # Both documents show every piece: DXF INSERT + PDF path.
    for f in b["furniture"]:
        assert [(e["file"], e["entity"].split(":")[0]) for e in f["evidence"]] == [
            ("3_kat_plani.dxf", "INSERT"), ("3_kat_plani_pdf.pdf", "path")], f["id"]
    assert [w for w in b["warnings"] if "ceiling height" not in w] == []


def test_counts_match_spec_synthetic_05(generated):
    """docs/milestone6.md §3.2: notched outline, floor plan without furniture + furniture plan, style photo."""
    b = truth(generated, "synthetic-05")
    assert [(lv["id"], lv["label"], lv["elevation"]) for lv in b["levels"]] == [("L0", "Zemin Kat", 0.0)]
    assert _counts(b) == (14, 6, 19, 9, 10, 9, 26, 0, 0)
    assert b["project"]["brief"] == {"style": "Modern, white walls, warm daylight, linen textiles, brass details",
                                     "style_photos": ["salon_referans.jpg"], "polish": False}
    assert [(d["file"], d["pages"][0]["class"]) for d in b["documents"]] == [
        ("zemin_kat.dxf", "floor_plan"), ("zemin_kat_mobilya.dxf", "furniture_plan")]
    rooms = {r["id"]: r for r in b["rooms"]}
    expected = {  # id: (room_type, area, documented pieces, doors on its walls, windows)
        "r_L0_salon": ("living", 19.76, 6, 1, 2), "r_L0_ebeveyn_yatak_odasi": ("bedroom", 17.86, 5, 2, 1),
        "r_L0_ebeveyn_banyo": ("bathroom", 5.945, 3, 1, 1), "r_L0_mutfak": ("kitchen", 14.72, 6, 1, 2),
        "r_L0_hol": ("hall", 7.92, 0, 7, 0), "r_L0_antre": ("hall", 4.95, 0, 2, 0),
        "r_L0_banyo": ("bathroom", 6.6, 3, 1, 1), "r_L0_yatak_odasi": ("bedroom", 9.57, 3, 1, 1),
        "r_L0_calisma_odasi": ("other", 13.8, 0, 1, 2),
    }
    assert set(rooms) == set(expected)
    for room_id, (room_type, area, pieces, doors, windows) in expected.items():
        r = rooms[room_id]
        assert (r["room_type"], r["area_computed"], len(r["polygon"])) == (room_type, area, 4), room_id
        assert sum(f["room_id"] == room_id for f in b["furniture"]) == pieces, room_id
        assert (len(_doors_on(b, r)), len(_windows_on(b, r))) == (doors, windows), room_id
    assert rooms["r_L0_salon"]["area_label"] == 19.76
    # The en-suite is reached through the master bedroom only; its window looks onto the recess.
    en_suite_door = _doors_on(b, rooms["r_L0_ebeveyn_banyo"])[0]
    assert en_suite_door["swing_side"] == "r_L0_ebeveyn_banyo"
    assert en_suite_door["wall_id"] in _wall_ids_of(b, rooms["r_L0_ebeveyn_yatak_odasi"])
    assert _windows_on(b, rooms["r_L0_ebeveyn_banyo"])[0]["wall_id"] == "w_L0_003"
    assert sorted(f["type_raw"] for f in b["furniture"] if f["type"] == "bed_single") == ["YATAK_TEK", "YATAK_TEK"]
    # Furniture comes from the furniture plan only; walls are on both documents.
    assert all([e["file"] for e in f["evidence"]] == ["zemin_kat_mobilya.dxf"] for f in b["furniture"])
    assert all([e["file"] for e in w["evidence"]] == ["zemin_kat.dxf", "zemin_kat_mobilya.dxf"] for w in b["walls"])
    assert [w for w in b["warnings"] if "ceiling height" not in w] == [
        "Zemin Kat: furniture taken from zemin_kat_mobilya.dxf (26 pieces); zemin_kat.dxf draws none"]
    # The six outer walls follow the notched outline (outer faces on the outline edges).
    outer = [w for w in b["walls"] if w["exterior"]]
    assert [(w["id"], w["start"], w["end"]) for w in outer] == [
        ("w_L0_001", [0.0, 0.125], [10.5, 0.125]), ("w_L0_002", [10.375, 0.0], [10.375, 2.0]),
        ("w_L0_003", [10.25, 1.875], [13.5, 1.875]), ("w_L0_004", [13.375, 1.75], [13.375, 9.0]),
        ("w_L0_005", [0.0, 8.875], [13.5, 8.875]), ("w_L0_006", [0.125, 0.0], [0.125, 9.0])]


def test_deterministic(generated, tmp_path):
    out2 = tmp_path / "again"
    for project in all_projects():
        generate_project(project, out2, None)
    for name in ALL_NAMES:
        for rel in EXPECTED_FILES[name]:
            a = (generated[0] / name / rel).read_bytes()
            b = (out2 / name / rel).read_bytes()
            assert a == b, f"{name}/{rel} differs between runs"


RASTER_SUFFIXES = (".png", ".jpg")
RASTER_MAX_MEAN_DIFF = 2.0          # grey levels; encoder/anti-aliasing noise is far below this
RASTER_STRONG_DIFF = 64             # a pixel differing by more than this is content, not noise
RASTER_MAX_STRONG_FRACTION = 0.001  # at most 0.1 % such pixels (a missing symbol gives more)


def json_close(a, b, rel: float = 1e-9) -> bool:
    """Two JSON values equal up to the last digits of their floats (numpy/OpenCV builds differ there)."""
    if isinstance(a, float) or isinstance(b, float):
        return isinstance(a, (int, float)) and isinstance(b, (int, float)) and abs(a - b) <= rel * max(1.0, abs(a), abs(b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(json_close(a[k], b[k], rel) for k in a)
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(json_close(x, y, rel) for x, y in zip(a, b))
    return a == b


def rasters_match(a: Path, b: Path, max_mean_diff: float = RASTER_MAX_MEAN_DIFF,
                  max_strong_fraction: float = RASTER_MAX_STRONG_FRACTION) -> bool:
    """Same size and mode, mean absolute pixel difference below ``max_mean_diff`` and
    fewer than ``max_strong_fraction`` of the pixels differing by more than
    ``RASTER_STRONG_DIFF`` grey levels.

    The scans and photos come from pdftoppm (poppler + freetype) and OpenCV, whose
    anti-aliasing and encoders differ by a few grey levels between builds, so the
    rasters are compared by content; the vector files and the truth JSON stay
    byte-identical across machines. The pages are mostly white, so the mean alone
    would miss a blanked region; the strong-difference fraction catches that.
    """
    with Image.open(a) as ia, Image.open(b) as ib:
        if ia.size != ib.size or ia.mode != ib.mode:
            return False
        diff = np.abs(np.asarray(ia, dtype=np.float32) - np.asarray(ib, dtype=np.float32))
    return float(diff.mean()) < max_mean_diff and float((diff > RASTER_STRONG_DIFF).mean()) < max_strong_fraction


def test_rasters_match_tolerates_encoder_noise_but_not_content(tmp_path):
    src = COMMITTED / "synthetic-02" / "plan_scan.png"
    img = np.asarray(Image.open(src), dtype=np.int16)
    rng = np.random.default_rng(0)
    noisy = img.copy()
    mask = rng.random(img.shape) < 0.01                      # 1 % of the pixels off by one level
    noisy[mask] += rng.choice([-1, 1], size=int(mask.sum()))
    noisy_png = tmp_path / "noisy.png"
    Image.fromarray(np.clip(noisy, 0, 255).astype(np.uint8), "L").save(noisy_png)
    assert rasters_match(src, noisy_png)
    # A moved sheet or a missing symbol is content, not noise.
    shifted = np.roll(img, 30, axis=1)
    shifted_png = tmp_path / "shifted.png"
    Image.fromarray(shifted.astype(np.uint8), "L").save(shifted_png)
    assert not rasters_match(src, shifted_png)
    blanked = img.copy()
    blanked[300:900, 300:1200] = 255
    blanked_png = tmp_path / "blanked.png"
    Image.fromarray(blanked.astype(np.uint8), "L").save(blanked_png)
    assert not rasters_match(src, blanked_png)
    # A different size never matches.
    small_png = tmp_path / "small.png"
    Image.fromarray(img[:-1].astype(np.uint8), "L").save(small_png)
    assert not rasters_match(src, small_png)


@pytest.mark.skipif(not COMMITTED.exists(), reason="projects/ not present")
@pytest.mark.parametrize("name", ALL_NAMES)
def test_committed_projects_are_current(generated, name):
    for rel in EXPECTED_FILES[name]:
        committed = COMMITTED / name / rel
        fresh = generated[0] / name / rel
        assert committed.is_file(), f"run python -m wenart.synthetic.generate --out projects ({rel} missing)"
        if committed.suffix in RASTER_SUFFIXES and not rel.startswith("style_photos/"):
            # Rasters: by content (pdftoppm/OpenCV builds differ in the last grey level).
            # Style photos are byte copies and compared by bytes.
            assert rasters_match(committed, fresh), \
                f"{name}/{rel} differs in content: run python -m wenart.synthetic.generate --out projects"
        elif committed.suffix == ".json" and "/truth/" in "/" + rel:
            # Truth JSON holds float matrices from numpy/OpenCV: equal up to the last digits.
            assert json_close(json.loads(committed.read_text(encoding="utf-8")), json.loads(fresh.read_text(encoding="utf-8"))), \
                f"{name}/{rel} is stale: run python -m wenart.synthetic.generate --out projects"
        else:
            assert committed.read_bytes() == fresh.read_bytes(), \
                f"{name}/{rel} is stale: run python -m wenart.synthetic.generate --out projects"


def test_cli_runs(tmp_path):
    assert main(["--out", str(tmp_path / "p"), "--results", "", "--only", "synthetic-02"]) == 0
    assert (tmp_path / "p" / "synthetic-02" / "plan_photo.jpg").is_file()
    assert not (tmp_path / "p" / "synthetic-01").exists()
    assert main(["--out", str(tmp_path / "p"), "--results", str(tmp_path / "r"), "--only", "synthetic-05"]) == 0
    assert (tmp_path / "p" / "synthetic-05" / "style_photos" / "salon_referans.jpg").is_file()
    assert sorted(p.name for p in (tmp_path / "r").iterdir()) == [
        "synthetic-05_zemin_kat_mobilya_p1.jpg", "synthetic-05_zemin_kat_p1.jpg"]


@pytest.mark.skipif(not COMMITTED.exists(), reason="projects/ not present")
def test_committed_previews_are_current(generated):
    """results/synthetic holds exactly one preview per visible page of the seven projects."""
    committed = sorted(p.stem for p in (ROOT / "results" / "synthetic").glob("*.jpg"))
    assert committed == sorted(p.stem for p in generated[1].glob("*.jpg"))


# --------------------------------------------------------------------------
# Style photos (synthetic-05)
# --------------------------------------------------------------------------

def test_style_photo_copied_byte_for_byte(generated):
    src = ROOT / STYLE_PHOTO_05
    copied = generated[0] / "synthetic-05" / "style_photos" / "salon_referans.jpg"
    assert copied.read_bytes() == src.read_bytes()
    brief = yaml.safe_load((generated[0] / "synthetic-05" / "brief.yaml").read_text(encoding="utf-8"))
    assert brief["style_photos"] == ["salon_referans.jpg"] and brief["polish"] is False
    # The photo is not a document: not in the truth, not in pages.json.
    b = truth(generated, "synthetic-05")
    assert all(not d["file"].startswith("style_photos") for d in b["documents"])
    assert all(not p["file"].startswith("style_photos") for p in pages(generated, "synthetic-05"))


def test_style_photo_sources_and_copy(tmp_path):
    photo = tmp_path / "ref.jpg"
    photo.write_bytes(b"\xff\xd8 not really a jpeg")
    project = Project(name="p", brief=None, levels=[], documents=[],
                      style_photos={"a.jpg": str(photo), "b.jpg": STYLE_PHOTO_05})
    assert project.style_photo_sources() == {"a.jpg": photo, "b.jpg": ROOT / STYLE_PHOTO_05}
    written = write_style_photos(project, tmp_path / "out")
    assert [p.relative_to(tmp_path / "out").as_posix() for p in written] == ["style_photos/a.jpg", "style_photos/b.jpg"]
    assert (tmp_path / "out" / "style_photos" / "a.jpg").read_bytes() == photo.read_bytes()
    # No style photos: nothing written, no folder.
    assert write_style_photos(Project(name="q", brief=None, levels=[], documents=[]), tmp_path / "q") == []
    assert not (tmp_path / "q").exists()
    # A missing source is an error, never a silently missing photo.
    with pytest.raises(FileNotFoundError):
        write_style_photos(Project(name="r", brief=None, levels=[], documents=[],
                                   style_photos={"x.jpg": str(tmp_path / "missing.jpg")}), tmp_path / "r")


# --------------------------------------------------------------------------
# Outline of a level (LevelBuilder(outline=...))
# --------------------------------------------------------------------------

def _wall_lines(level):
    return [(w.start, w.end, w.thickness, w.exterior) for w in level.walls]


def test_default_outline_is_the_rectangle():
    """The default builder and an explicit rectangle outline give the same four outer walls (indices 0..3:
    bottom, right, top, left), so synthetic-01..03 are unchanged."""
    default = LevelBuilder("ZEMİN KAT PLANI", 9.6, 7.2)
    explicit = LevelBuilder("ZEMİN KAT PLANI", outline=[(0, 0), (9.6, 0), (9.6, 7.2), (0, 7.2)])
    assert _wall_lines(default.level) == _wall_lines(explicit.level) == [
        ((0.0, 0.125), (9.6, 0.125), 0.25, True), ((9.475, 0.0), (9.475, 7.2), 0.25, True),
        ((0.0, 7.075), (9.6, 7.075), 0.25, True), ((0.125, 0.0), (0.125, 7.2), 0.25, True)]
    assert (explicit.width, explicit.height, explicit.level.title_at) == (9.6, 7.2, (0.0, 8.4))


def test_notched_outline_walls_close_and_meet_at_the_reflex_corner():
    b = LevelBuilder("ZEMİN KAT PLANI", outline=OUTLINE_05)
    assert (b.width, b.height) == (13.5, 9.0)
    lines = [(w.start, w.end) for w in b.level.walls]
    assert lines == [((0.0, 0.125), (10.5, 0.125)), ((10.375, 0.0), (10.375, 2.0)), ((10.25, 1.875), (13.5, 1.875)),
                     ((13.375, 1.75), (13.375, 9.0)), ((0.0, 8.875), (13.5, 8.875)), ((0.125, 0.0), (0.125, 9.0))]
    union = wall_union(b.level)
    assert union.geom_type == "Polygon" and len(union.interiors) == 1
    # Outer face = the outline; inner face = the outline moved in by the wall thickness.
    assert union.exterior.equals(Polygon(OUTLINE_05).exterior)
    assert Polygon(union.interiors[0]).equals(Polygon(OUTLINE_05).buffer(-0.25, join_style=2))
    # One room filling the inside: the derived polygon keeps the notch (6 vertices).
    b.label("SALON", (1.0, 1.0))
    level = b.build()
    assert len(level.rooms) == 1 and len(level.rooms[0].polygon) == 6
    assert level.rooms[0].area_computed == pytest.approx(13.0 * 8.5 - 3.0 * 1.75)


def test_outline_orientation_does_not_change_the_walls():
    ccw = outer_wall_lines(OUTLINE_05, 0.25)
    cw = outer_wall_lines(list(reversed(OUTLINE_05)), 0.25)

    def norm(lines):
        return sorted(tuple(sorted([G.snap_point(a), G.snap_point(b)])) for a, b in lines)

    assert norm(ccw) == norm(cw)
    # A closing point equal to the first vertex is ignored.
    assert outer_wall_lines(OUTLINE_05 + [OUTLINE_05[0]], 0.25) == ccw


@pytest.mark.parametrize("outline, message", [
    ([(0, 0), (4, 0), (0, 3)], "at least 4"),
    ([(0, 0), (4, 0), (5, 3), (0, 3)], "horizontal or vertical"),
    ([(0, 0), (4, 0), (4, 0), (4, 3), (0, 3)], "horizontal or vertical"),
    ([(0, 0), (2, 0), (4, 0), (4, 3), (0, 3)], "collinear"),
    ([(0, 0), (4, 0), (4, 3), (2, 3), (2, -1), (0, -1)], "simple polygon"),
])
def test_bad_outline_is_refused(outline, message):
    with pytest.raises(ValueError, match=message):
        outer_wall_lines(outline, 0.25)


def test_level_builder_outline_arguments_are_checked():
    with pytest.raises(ValueError, match="width and height"):
        LevelBuilder("ZEMİN KAT PLANI")
    with pytest.raises(ValueError, match="origin"):
        LevelBuilder("ZEMİN KAT PLANI", outline=[(1, 1), (5, 1), (5, 4), (1, 4)])
    with pytest.raises(ValueError, match="do not match"):
        LevelBuilder("ZEMİN KAT PLANI", 13.0, 9.0, outline=OUTLINE_05)
    assert LevelBuilder("ZEMİN KAT PLANI", 13.5, 9.0, outline=OUTLINE_05).width == 13.5


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

@pytest.mark.parametrize("name, file", [("synthetic-01", "zemin_kat.dxf"), ("synthetic-03", "mobilya_plani.dxf"),
                                        ("synthetic-04", "3_kat_plani.dxf"), ("synthetic-05", "zemin_kat.dxf"),
                                        ("synthetic-05", "zemin_kat_mobilya.dxf")])
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
    # Pieces this page draws (a floor plan next to a furniture plan draws none).
    level_furniture = [f for f in b["furniture"] if f["level_id"] == level_id
                       and any(e["file"] == file for e in f["evidence"])]
    assert len(level_furniture) == (0 if (name, file) == ("synthetic-05", "zemin_kat.dxf") else
                                    sum(f["level_id"] == level_id for f in b["furniture"]))

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


@pytest.mark.parametrize("name, file", [("synthetic-03", "mobilya_plani.dxf"), ("synthetic-05", "zemin_kat_mobilya.dxf")])
def test_dxf_furniture_plan_has_no_dimensions(generated, name, file):
    doc = ezdxf.readfile(str(generated[0] / name / file))
    assert len(doc.modelspace().query("DIMENSION")) == 0
    titles = {e.dxf.text for e in doc.modelspace().query("TEXT")}
    assert "ZEMİN KAT MOBİLYA PLANI" in titles
    assert B.normalise_level_label("ZEMİN KAT MOBİLYA PLANI") == ("Zemin Kat", 0)


def test_dxf_floor_plan_of_synthetic_05_draws_no_furniture(generated):
    msp = ezdxf.readfile(str(generated[0] / "synthetic-05" / "zemin_kat.dxf")).modelspace()
    assert not [e for e in msp.query("INSERT") if e.dxf.layer == blocks.LAYER_FURNITURE]
    assert {e.dxf.name for e in msp.query("INSERT")} <= set(blocks.DOOR_BLOCKS + blocks.WINDOW_BLOCKS)
    assert len(msp.query("DIMENSION")) == 6   # two chains of two segments plus two overall dimensions
    furniture_plan = ezdxf.readfile(str(generated[0] / "synthetic-05" / "zemin_kat_mobilya.dxf")).modelspace()
    assert {e.dxf.name for e in furniture_plan.query("INSERT") if e.dxf.layer == blocks.LAYER_FURNITURE} >= {
        "YATAK_TEK", "KUVET", "DUS", "SIFONYER", "CAMASIR_MAK"}


# --------------------------------------------------------------------------
# PDF
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name, file, n_pages", [("synthetic-01", "1_kat.pdf", 1), ("synthetic-03", "kat_planlari.pdf", 3),
                                                 ("synthetic-02", "truth/plan.pdf", 1),
                                                 ("synthetic-04", "3_kat_plani_pdf.pdf", 1)])
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
            # Door arcs are the only Bezier curves on the page; a piece of furniture at a non-right angle is a
            # straight-sided polygon, which pdfplumber also lists under ``curves``.
            n_doors = sum(1 for s in rec["symbols"] if s["type"] == "door")
            arcs = [c for c in page.curves if any(op[0] == "c" for op in c["path"])]
            assert len(arcs) == n_doors
            n_angled = sum(1 for s in rec["symbols"] if s["type"] not in ("door", "window") and s["rotation_deg"] % 90)
            assert len(page.curves) - len(arcs) == n_angled
            if name == "synthetic-04":
                assert n_angled == 1   # the armchair at 45 degrees


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
    assert scan_page["scale"]["method"] == "dimension_text"           # Milestone 7: scale from dimensions (§4.3)
    b2 = truth(generated, "synthetic-02")
    photo = next(d for d in b2["documents"] if d["file"] == "plan_photo.jpg")["pages"][0]
    assert photo["kind"] == "photo" and photo["scale"] is None and photo["transform_to_building"] is None
    # Milestone 7 (§4.4): raster evidence is method "raster" for geometry, "ai" for the furniture types, and the
    # scan's scale comes from a dimension text read by OCR.
    scan2 = next(d for d in b2["documents"] if d["file"] == "plan_scan.png")["pages"][0]
    assert scan2["scale"]["method"] == "dimension_text" and scan2["scale"]["evidence"]["method"] == "ocr"
    for key in ("walls", "openings", "furniture"):
        assert {e["method"] for el in b2[key] for e in el["evidence"]} == ({"raster", "ai"} if key == "furniture"
                                                                            else {"raster"}), key
    assert all(any(e["method"] == "ai" and e["text"] == f"type: {f['type']}" for e in f["evidence"])
               for f in b2["furniture"])


def test_previews_are_small(generated):
    results = generated[1]
    jpgs = sorted(results.glob("*.jpg"))
    # One preview per visible page; different file stems keep the names unique (synthetic-04: DXF + PDF).
    assert sorted(j.stem for j in jpgs) == sorted(f"{name}_{stem}" for name, stems in EXPECTED_PREVIEWS.items()
                                                  for stem in stems)
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


# --------------------------------------------------------------------------
# synthetic-06: the CAD project delivered as a DWG (docs/milestone7.md §5.2)
# --------------------------------------------------------------------------

def test_feet_inches_texts_parse_back():
    assert [feet_inches(v) for v in (108, 180, 288, 156, 66, 144, 366)] == [
        "9'-0\"", "15'-0\"", "24'-0\"", "13'-0\"", "5'-6\"", "12'-0\"", "30'-6\""]
    for dim in plan_06().dimensions:
        length = units.parse_length(dim.text)
        assert length.system == "imperial"
        assert length.metres == pytest.approx(G.distance(dim.p1, dim.p2) * INCH, abs=1e-9)


def test_synthetic_06_truth_fields(generated):
    b = truth(generated, "synthetic-06")
    assert b["project"]["unit_system"] == "imperial" and b["project"]["brief"]["style"].startswith("Mid-century")
    doc = b["documents"][0]
    assert len(b["documents"]) == 1 and (doc["file"], doc["format"]) == ("synthetic-06.dwg", "dwg")
    assert doc["converter"].startswith("libredwg dwg2dxf 0.14 d9468ae")
    assert (doc["unit_system"], doc["source_kind"]) == ("imperial", "dxf")
    page = doc["pages"][0]
    assert (page["class"], page["level_id"], page["level_label_raw"], page["classifier"], page["confidence"]) == (
        "floor_plan", "L0", None, "generic_labels", 0.6)
    assert page["scale"]["method"] == "dxf_insunits" and page["scale"]["metres_per_unit"] == INCH
    assert page["transform_to_building"] == [INCH, 0.0, -480 * INCH, 0.0, INCH, -240 * INCH]
    level = b["levels"][0]
    assert (level["id"], level["label"], level["label_source"]) == ("L0", "Ground floor", "assumed")
    assert {e["text"] for e in level["evidence"]} == {"LIVING ROOM", "KITCHEN", "LOBBY", "BATH", "BED ROOM",
                                                     "MASTER BED ROOM"}
    assert "level title missing: assumed L0 Ground floor" in b["warnings"]
    walls, openings = b["walls"], b["openings"]
    assert (len(walls), sum(w["exterior"] for w in walls)) == (9, 4)
    assert sorted({w["thickness"] for w in walls}) == [0.1524, 0.2286]
    assert all(w["evidence"][0]["entity"].startswith("HATCH:") and w["evidence"][0]["layer"] == "A-WALL"
               for w in walls)
    assert [sum(o["type"] == t for o in openings) for t in ("door", "window", "opening")] == [5, 8, 1]
    sep = next(o for o in openings if o["type"] == "opening")
    assert sep["virtual"] is True and sep["wall_id"] is None and sep["width"] == pytest.approx(72 * INCH)
    assert sep["evidence"][0]["method"] == "derived"
    assert all(o["assumed"] == ["height"] and o["height"] == 2.10 for o in openings if o["type"] == "door")
    assert all(o["assumed"] == ["height", "sill_height"] and (o["sill_height"], o["height"]) == (0.90, 1.20)
               for o in openings if o["type"] == "window")
    rooms = {r["label"]: r for r in b["rooms"]}
    assert {k: r["room_type"] for k, r in rooms.items()} == {
        "Kitchen": "kitchen", "Living Room": "living", "Bath": "bathroom", "Lobby": "hall", "Bed Room": "bedroom",
        "Master Bed Room": "bedroom"}
    size = rooms["Living Room"]["label_size"]
    assert size["text"] == "14'-0\" X 12'-0\"" and size["status"] == "ok"
    assert size["measured"] == pytest.approx([size["width_m"], size["length_m"]])
    assert {k for k, r in rooms.items() if r["has_documented_furniture"]} == {
        "Kitchen", "Living Room", "Bath", "Master Bed Room"}
    assert rooms["Kitchen"]["evidence"][0]["entity"].startswith("ATTRIB:")
    assert rooms["Kitchen"]["evidence"][0]["block"] == "ROOMTAG"
    assert rooms["Living Room"]["evidence"][0]["entity"].startswith("MTEXT:")
    furniture = b["furniture"]
    assert all(f["type_method"] == "block_name" and f["status"] == "verified" for f in furniture)
    assert Counter(f["type"] for f in furniture) == Counter(
        {"chair": 6, "sofa": 1, "table_dining": 1, "bed_double": 1, "toilet": 1, "washbasin": 1})
    assert {f["type_raw"] for f in furniture if f["type"] == "chair"} == {"DINING-6/CHAIR"}
    assert [f["front_deg"] for f in furniture if f["type"] == "table_dining"] == [None]
    assert b["conflicts"] == [] and b["unverified"] == []


def test_synthetic_06_truth_geometry_is_consistent(generated):
    b = truth(generated, "synthetic-06")
    walls = {w["id"]: w for w in b["walls"]}
    rooms = {r["id"]: r for r in b["rooms"]}
    for o in b["openings"]:
        if o.get("virtual"):
            # The separator runs from the stub's free end along its axis to the opposite wall face.
            (x0, y0), (x1, y1) = o["line"]
            stub = next(w for w in walls.values() if w["start"] == [x0, y0] or w["end"] == [x0, y0])
            assert x0 == x1 == stub["start"][0] and G.distance(o["center"], [x0, (y0 + y1) / 2]) < 1e-9
            continue
        w = walls[o["wall_id"]]
        assert G.point_segment_distance(o["center"], w["start"], w["end"]) < 1e-6
        if o["type"] == "door":
            assert rooms[o["swing_side"]]["level_id"] == "L0"
    polys = [Polygon(r["polygon"]) for r in b["rooms"]]
    assert all(a.intersection(c).area < 1e-9 for i, a in enumerate(polys) for c in polys[i + 1:])
    for r in b["rooms"]:
        assert abs(G.polygon_area(r["polygon"]) - r["area_computed"]) < 1e-3
    for f in b["furniture"]:
        fp = f["footprint"]
        corners = G.rotated_rectangle(fp["center"], fp["size"], fp["rotation_deg"])
        assert all(G.point_in_polygon(c, rooms[f["room_id"]]["polygon"]) for c in corners), f["id"]
        name = f["type_raw"].split("/")[-1]
        ftype, width, depth = blocks.CAD_BLOCKS[name]
        assert f["type"] == ftype and fp["size"] == pytest.approx([width * INCH, depth * INCH])
        if f["front_deg"] is not None:
            assert f["front_deg"] == G.front_direction_deg(fp["rotation_deg"])


def test_synthetic_06_source_is_drawn_the_cad_way(generated):
    path = generated[0] / "synthetic-06" / "source" / "synthetic-06.dxf"
    doc, auditor = recover.readfile(str(path))
    assert not auditor.has_errors and doc.dxfversion == "AC1015"
    assert (doc.header["$INSUNITS"], doc.header["$MEASUREMENT"], doc.header["$LUNITS"]) == (1, 0, 4)
    assert {name for name, _ in blocks.CAD_LAYERS} <= {layer.dxf.name for layer in doc.layers}
    assert not set(blocks.LAYERS) & {layer.dxf.name for layer in doc.layers}
    msp = doc.modelspace()
    hatches = msp.query("HATCH")
    assert len(hatches) == 1 and hatches[0].dxf.solid_fill == 1 and hatches[0].dxf.color == 7
    assert len(hatches[0].paths) == 6 and hatches[0].dxf.layer == "A-WALL"
    assert not msp.query("TEXT").query('*[text ? "PLAN"]')                      # untitled
    dims = msp.query("DIMENSION")
    assert sorted(d.dimtype for d in dims) == [0] * 4 + [1] * 4                # rotated and aligned
    assert all(d.dxf.hasattr("angle") for d in dims if d.dimtype == 0)
    # LibreDWG's dxf2dwg reads no MTEXT rotation angle: the upright dimension texts carry a direction vector.
    dim_texts = [e for blk in doc.blocks if blk.name.startswith("*D") for e in blk if e.dxftype() == "MTEXT"]
    assert len(dim_texts) == 8 and not any(e.dxf.hasattr("rotation") for e in dim_texts)
    assert sorted(tuple(e.dxf.text_direction)[:2] for e in dim_texts if e.dxf.hasattr("text_direction")) == \
        [(0.0, 1.0)] * 5
    mtext = msp.query("MTEXT")[0]
    assert mtext.text == "\\H9;LIVING ROOM\\P14'-0\" X 12'-0\""
    tag = msp.query("INSERT[name=='ROOMTAG']")[0]
    assert [(a.dxf.tag, a.dxf.text) for a in tag.attribs] == [("NAME", "KITCHEN")]
    dining = doc.blocks.get("DINING-6")
    assert [e.dxf.name for e in dining.query("INSERT")] == ["CHAIR"] * 6


@pytest.mark.skipif(not HAS_DXF2DWG, reason="LibreDWG dxf2dwg not built here (scripts/cloud-setup.sh)")
def test_synthetic_06_dwg_hash(generated):
    import hashlib
    fresh = generated[0] / "synthetic-06" / "synthetic-06.dwg"
    assert hashlib.sha256(fresh.read_bytes()).hexdigest() == DWG_SHA256_06


def test_synthetic_06_titled_fixture(generated, tmp_path):
    fresh = generate_titled_fixture(project_06(), tmp_path)
    name = "synthetic-06-titled"
    for rel in (f"{name}.dxf", "truth/building.json"):
        assert (TITLED_06 / rel).read_bytes() == (tmp_path / name / rel).read_bytes(), \
            f"tests/fixtures/{name}/{rel} is stale: run python -m wenart.synthetic.generate --out projects"
    assert sorted(p.relative_to(TITLED_06).as_posix() for p in TITLED_06.rglob("*") if p.is_file()) == [
        f"{name}.dxf", "truth/building.json"]
    project = truth(generated, "synthetic-06")
    doc = fresh["documents"][0]
    assert (doc["file"], doc["format"], doc["converter"]) == (f"{name}.dxf", "dxf", None)
    page = doc["pages"][0]
    assert (page["level_label_raw"], page["classifier"], page["confidence"]) == ("GROUND FLOOR PLAN", "title", 1.0)
    level = fresh["levels"][0]
    assert (level["label"], level["label_source"]) == ("Ground Floor", "title")
    assert level["evidence"][0]["text"] == "GROUND FLOOR PLAN" and level["evidence"][0]["entity"].startswith("TEXT:")
    assert not any("level title missing" in w for w in fresh["warnings"])
    # Everything drawn is the same as in the untitled project, evidence included: the title is written last, so
    # every other entity keeps its handle.

    def same(elements):
        return json.loads(json.dumps(elements).replace(f"{name}.dxf", "synthetic-06.dwg"))

    for key in ("walls", "openings", "rooms", "furniture"):
        assert same(fresh[key]) == project[key], key
    texts = [e.dxf.text for e in recover.readfile(str(TITLED_06 / f"{name}.dxf"))[0].modelspace().query("TEXT")]
    assert "GROUND FLOOR PLAN" in texts


# --------------------------------------------------------------------------
# synthetic-07: one CAD sheet with every drawing kind (docs/milestone10.md §3.4)
# --------------------------------------------------------------------------
# The truth files are checked against the DXF as ezdxf reads it back (never against the layout code): boxes by an
# independent clustering, heights and positions by reading the drawn lines and applying the truth's own transforms.

P7 = "synthetic-07"
WALL_WORD = re.compile("WALL|DUVAR|MUR|PARED", re.IGNORECASE)
TOL = 1e-6


@pytest.fixture(scope="module")
def sheet(generated):
    """The written sheet (``recover.readfile`` decodes the \\U+XXXX escapes of the R2000 file) and the four truth files."""
    folder = generated[0] / P7
    doc, auditor = recover.readfile(str(folder / "sheet.dxf"))

    def load(name):
        return json.loads((folder / "truth" / name).read_text(encoding="utf-8"))

    return {"doc": doc, "auditor": auditor, "msp": doc.modelspace(), "folder": folder, "sheets": load("sheets_truth.json"),
            "heights": load("heights_truth.json"), "exterior": load("exterior_truth.json"),
            "building": B.load(folder / "truth" / "building.json")}


def _regions(sheet):
    return sheet["sheets"]["regions"]


def _region(sheet, **match):
    hits = [r for r in _regions(sheet) if all(r.get(k) == v for k, v in match.items())]
    assert len(hits) == 1, (match, len(hits))
    return hits[0]


def _entity(sheet, entity_string):
    kind, handle = entity_string.split(":")
    entity = sheet["doc"].entitydb.get(handle)
    assert entity is not None and entity.dxftype() == kind, entity_string
    return entity


def _box_of(entity):
    from ezdxf import bbox

    ext = bbox.extents([entity])
    return [ext.extmin.x, ext.extmin.y, ext.extmax.x, ext.extmax.y]


def _box_distance(a, b):
    return math.hypot(max(a[0] - b[2], b[0] - a[2], 0.0), max(a[1] - b[3], b[1] - a[3], 0.0))


def _within(box, outer, tol=1e-3):
    return outer[0] - tol <= box[0] and outer[1] - tol <= box[1] and box[2] <= outer[2] + tol and box[3] <= outer[3] + tol


def _in_region(sheet, region, dxftype=None, layer=None):
    """Geometry entities of one layer / type whose box lies inside the region's box."""
    out = []
    for e in sheet["msp"]:
        if (dxftype and e.dxftype() != dxftype) or (layer and e.dxf.layer != layer) or e.dxftype() in ("TEXT", "MTEXT"):
            continue
        if _within(_box_of(e), region["box"]):
            out.append(e)
    return out


def _apply(region, point):
    a, b, c, d, e, f = region["transform_to_building"]
    return (a * point[0] + b * point[1] + c, d * point[0] + e * point[1] + f)


def _rect_of(entity):
    pts = [(x, y) for x, y in entity.get_points("xy")]
    assert entity.closed and len(pts) == 4, entity
    return [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]


def test_synthetic_07_sheet_is_one_cad_drawing_in_centimetres(sheet):
    doc, msp = sheet["doc"], sheet["msp"]
    assert not sheet["auditor"].has_errors and doc.dxfversion == "AC1015"
    assert doc.header["$INSUNITS"] == 5 and doc.header["$MEASUREMENT"] == 1
    assert all(not WALL_WORD.search(layer.dxf.name) for layer in doc.layers)         # no layer says "wall"
    # Walls: open two-point face lines on one layer, never a closed polygon or a hatch.
    faces = msp.query('LWPOLYLINE[layer=="AR_w_sld"]')
    assert len(faces) > 60 and all(len(f) == 2 and not f.closed for f in faces)
    assert {f.dxftype() for f in msp if f.dxf.layer == "AR_w_sld"} == {"LWPOLYLINE"}
    # Columns: closed 0.25 m squares on a structural layer, six per plan.
    columns = msp.query('LWPOLYLINE[layer=="S-BETON"]')
    assert len(columns) == 24
    for column in columns:
        x0, y0, x1, y1 = _rect_of(column)
        assert (x1 - x0, y1 - y0) == (25.0, 25.0)
    # Doors and windows are INSERTs of blocks; a swing door's block holds a leaf and an arc, the double door two arcs, the
    # sliding door a leaf rectangle and no arc.
    door_blocks = {e.dxf.name for e in msp.query('INSERT[layer=="A_Kapi"]')}
    assert door_blocks == {"KAPI_80", "KAPI_90", "KAPI_SURME_90", "KAPI_CIFT_140"}
    assert {e.dxf.name for e in msp.query('INSERT[layer=="A_Pencere"]')} == {"PENCERE_60", "PENCERE_120"}
    arcs = {name: len(doc.blocks.get(name).query("ARC")) for name in door_blocks}
    assert arcs == {"KAPI_80": 1, "KAPI_90": 1, "KAPI_SURME_90": 0, "KAPI_CIFT_140": 2}
    assert len(doc.blocks.get("KAPI_SURME_90").query("LWPOLYLINE")) == 1
    assert {e.dxf.name for e in msp.query('INSERT[layer=="A_Mobilya"]')} == {
        "KANEPE_3LU", "BUZDOLABI", "TEZGAH", "EVIYE", "OCAK", "YATAK_CIFT", "KLOZET", "LAVABO", "DUS", "MERDIVEN"}
    # Room labels: MTEXT with the name and the area line, the height also inline; titles and the title block.
    labels = sorted(e.text for e in msp.query("MTEXT") if "M2" in e.text)
    assert "\\H20;SALON\\P43.5M2" in labels and "\\H20;SALON + AÇIK MUTFAK\\P57.2M2" in labels and len(labels) == 11
    texts = {e.dxf.text for e in msp.query("TEXT")} | {e.plain_text() for e in msp.query("MTEXT")}
    assert not any("\\U+" in t for t in texts)
    for needed in ("BODRUM KAT PLANI", "BODRUM KAT PLANI (AÇIK MUTFAK)", "ZEMİN KAT PLANI", "ÇATI KAT PLANI", "A-A KESİTİ",
                   "GÜNEY GÖRÜNÜŞÜ", "DOĞU GÖRÜNÜŞÜ", "VAZİYET PLANI", "LEJANT", "PROJE", "ÇİZEN", "ÖLÇEK 1/100", "TARİH",
                   "PAFTA", "-3.00", "±0.00", "+3.00", "N", "OTOPARK", "BAHÇE", "YOL", "SIVA", "TAŞ KAPLAMA", "KİREMİT"):
        assert needed in texts, needed
    # Frame, hatch and the stray line.
    frame = msp.query('LWPOLYLINE[layer=="A_Cerceve"]')
    assert len(frame) == 1 and _rect_of(frame[0]) == [0.0, 0.0, 11000.0, 5600.0]
    assert len(msp.query("HATCH")) == 2 and all(h.dxf.pattern_name == "ANSI31" for h in msp.query("HATCH"))
    stray = [e for e in msp.query("LINE") if e.dxf.layer == "0"]
    assert len(stray) == 1 and stray[0].dxf.start.x < -50000


def test_synthetic_07_regions_equal_an_independent_clustering(sheet):
    """The spec's split (docs/milestone10.md §3.1.1): boxes of the non-text entities, the frame left out, clustered with
    a gap of 1.5 % of the frame's diagonal, give exactly the truth's regions (and one stray)."""
    document = sheet["sheets"]["documents"][0]["sheets"][0]
    frame = document["frames"][0]["box"]
    gap = 0.015 * math.hypot(frame[2] - frame[0], frame[3] - frame[1])
    assert gap == pytest.approx(document["gap_units"], abs=1e-3)
    items = [(e, _box_of(e)) for e in sheet["msp"] if e.dxftype() not in ("TEXT", "MTEXT") and e.dxf.layer != "A_Cerceve"]
    parent = list(range(len(items)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if _box_distance(items[i][1], items[j][1]) <= gap:
                parent[find(i)] = find(j)
    clusters: dict = {}
    for i, (_, box) in enumerate(items):
        clusters.setdefault(find(i), []).append(box)
    found = sorted(([min(b[0] for b in m), min(b[1] for b in m), max(b[2] for b in m), max(b[3] for b in m), len(m)]
                    for m in clusters.values()), key=lambda c: (-c[3], c[0]))
    stray = sheet["sheets"]["stray"]
    assert len(stray) == 1 and found[0][:4] == pytest.approx(stray[0]["box"]) and found[0][4] == 1
    truth = [r["box"] + [r["geometry_entities"]] for r in _regions(sheet)]
    assert len(found) == 1 + len(truth)
    assert [v for c in found[1:] for v in c[:4]] == pytest.approx([v for t in truth for v in t[:4]], abs=1e-3)
    assert [c[4] for c in found[1:]] == [t[4] for t in truth]
    # Far from everything: the stray is a stray (docs/milestone10.md §1.6b row 5).
    assert stray[0]["distance_m"] > 1000 and stray[0]["entity"].startswith("LINE:")
    assert all(_within(r["box"], frame) for r in _regions(sheet))


def test_synthetic_07_texts_join_their_region_and_titles_sit_below_it(sheet):
    regions = _regions(sheet)
    counts: Counter = Counter()
    for e in sheet["msp"].query("TEXT MTEXT"):
        at = [e.dxf.insert.x, e.dxf.insert.y] * 2
        dist = sorted((_box_distance(at, r["box"]), r["id"]) for r in regions)
        assert dist[1][0] - dist[0][0] >= 100.0 or dist[0][0] == 0.0, (e.dxf.handle, dist[:2])
        counts[dist[0][1]] += 1
    assert {r["id"]: r["text_entities"] for r in regions} == {r["id"]: counts.get(r["id"], 0) for r in regions}
    for r in regions:
        if r["title"] is None:
            assert r["class"] == "title_block"
            continue
        entity = _entity(sheet, r["title"]["entity"])
        text = entity.dxf.text if entity.dxftype() == "TEXT" else entity.plain_text()
        assert text == r["title"]["text"]
        x0, y0, x1, y1 = r["title"]["box"]
        height = r["box"][3] - r["box"][1]
        assert y1 <= r["box"][1] and r["box"][1] - y1 <= 0.3 * height            # below, within 0.3 x the region height
        assert abs(x0 - r["box"][0]) < 1e-6


def test_synthetic_07_region_truth_fields(sheet):
    regions = _regions(sheet)
    assert [r["id"] for r in regions] == [f"r{i}" for i in range(1, 11)]                 # reading order, no ties
    tops = [r["box"][3] for r in regions]
    assert tops == sorted(tops, reverse=True) and all(a - b > 1.0 for a, b in zip(tops, tops[1:]))
    assert [(r["class"], r["use"]) for r in regions] == [
        ("floor_plan", "read"), ("alternative_floor_plan", "read"), ("floor_plan", "read"), ("floor_plan", "read"),
        ("site_plan", "exterior"), ("section", "heights"), ("elevation", "exterior"), ("elevation", "exterior"),
        ("legend", "ignored"), ("title_block", "ignored")]
    assert [r["title"]["text"] if r["title"] else None for r in regions] == [
        "BODRUM KAT PLANI", "BODRUM KAT PLANI (AÇIK MUTFAK)", "ZEMİN KAT PLANI", "ÇATI KAT PLANI", "VAZİYET PLANI",
        "A-A KESİTİ", "GÜNEY GÖRÜNÜŞÜ", "DOĞU GÖRÜNÜŞÜ", "LEJANT", None]
    plans = {r["id"]: r for r in regions if r["level"]}
    assert {rid: (r["level"]["id"], r["level"]["order"], r["level"]["kind"], r["variant"], r["variant_slug"],
                 r["variant_group"]) for rid, r in plans.items()} == {
        "r1": ("L-1", -1, "basement", "base", "base", "vg_L-1"),
        "r2": ("L-1b", -1, "basement", "Açık mutfak", "acik-mutfak", "vg_L-1"),
        "r3": ("L0", 0, "floor", "base", "base", None), "r4": ("L1", 1, "attic", "base", "base", None)}
    assert plans["r2"]["variant_gloss"] == "open kitchen"
    assert [(lv["id"], lv["base_region"], [a["region"] for a in lv["alternatives"]]) for lv in sheet["sheets"]["levels"]] == [
        ("L-1", "r1", ["r2"]), ("L0", "r3", []), ("L1", "r4", [])]
    assert [(v["id"], v["levels"], v["regions"]) for v in sheet["sheets"]["variants"]] == [
        ("base", ["L-1", "L0", "L1"], ["r1", "r3", "r4"]), ("l-1b-acik-mutfak", ["L-1b", "L0", "L1"], ["r2", "r3", "r4"])]
    units = sheet["sheets"]["documents"][0]["units"]
    assert (units["insunits"], units["metres_per_unit"], units["conflict"]) == (5, 0.01, None)
    assert sheet["sheets"]["conflicts"] == []
    # One entity per title: no title serves two regions.
    entities = [r["title"]["entity"] for r in regions if r["title"]]
    assert len(entities) == len(set(entities)) == 9


def test_synthetic_07_registration_and_transforms_match_the_drawing(sheet):
    """Registration: p_ref = p * 0.01 + shift_m puts every plan on the ground-floor drawing, and transform_to_building
    maps the outer faces of every plan onto the one building frame (origin = min corner of the ground plan's outer faces)."""
    corners = {}
    for r in _regions(sheet):
        if not r["level"]:
            continue
        pts = [p for f in _in_region(sheet, r, "LWPOLYLINE", "AR_w_sld") for p in f.get_points("xy")]
        lo, hi = (min(p[0] for p in pts), min(p[1] for p in pts)), (max(p[0] for p in pts), max(p[1] for p in pts))
        corners[r["id"]] = lo
        assert _apply(r, lo) == pytest.approx((0.0, 0.0), abs=TOL) and _apply(r, hi) == pytest.approx((10.0, 8.0), abs=TOL)
        reg = r["registration"]
        assert reg["rotation_deg"] == 0.0 and reg["residual_m"] == 0.0 and reg["stairs_aligned"] is True
        assert reg["reference"] == (None if r["id"] == "r3" else "r3")
    ref = (corners["r3"][0] * 0.01, corners["r3"][1] * 0.01)
    for rid, lo in corners.items():
        shift = _region(sheet, id=rid)["registration"]["shift_m"]
        assert (lo[0] * 0.01 + shift[0], lo[1] * 0.01 + shift[1]) == pytest.approx(ref, abs=TOL)
    assert _region(sheet, id="r1")["registration"]["shift_m"] == pytest.approx([34.0, -1.6])
    assert _region(sheet, id="r3")["registration"]["shift_m"] == [0.0, 0.0]
    # The site plan registers through its building outline.
    site = _region(sheet, id="r5")
    outline = [e for e in sheet["msp"].query("LWPOLYLINE") if e.dxf.layer == "V_Bina"][0]
    x0, y0, x1, y1 = _rect_of(outline)
    assert _apply(site, (x0, y0)) == pytest.approx((0.0, 0.0), abs=TOL)
    assert _apply(site, (x1, y1)) == pytest.approx((10.0, 8.0), abs=TOL)
    shift = site["registration"]["shift_m"]
    assert (x0 * 0.01 + shift[0], y0 * 0.01 + shift[1]) == pytest.approx(ref, abs=TOL)
    # Section: x -> building y (not flipped), y -> z. Elevations: x from the facade's left end seen from outside.
    section = _region(sheet, id="r6")
    bands = [e for e in _in_region(sheet, section, "LWPOLYLINE", "K_Kesit") if e.closed]
    spans = sorted(_apply(section, _rect_of(e)[:2]) + _apply(section, _rect_of(e)[2:]) for e in bands)
    assert spans == [pytest.approx(s) for s in ((0.0, -3.2, 8.0, -3.0), (0.0, -0.2, 8.0, 0.0), (0.0, 2.8, 8.0, 3.0))]
    assert sheet["heights"]["cut_axis"] == "y" and sheet["heights"]["flipped"] is False and sheet["heights"]["cut_at"] == 3.0
    south = _region(sheet, id="r7")
    wall = [e for e in _in_region(sheet, south, "LWPOLYLINE", "G_Cephe") if e.closed][0]
    box = _rect_of(wall)
    assert _apply(south, box[:2]) == pytest.approx((0.0, 0.0), abs=TOL) and _apply(south, box[2:])[0] == pytest.approx(10.0)
    east = _region(sheet, id="r8")
    gable = [e for e in _in_region(sheet, east, "LWPOLYLINE", "G_Cephe") if e.closed][0]
    pts = [_apply(east, p) for p in gable.get_points("xy")]
    assert min(p[0] for p in pts) == pytest.approx(0.0) and max(p[0] for p in pts) == pytest.approx(8.0)
    # The cut line A-A on the ground plan is the one the section's cut_at names: a line along Y at x = cut_at (building).
    ground = _region(sheet, id="r3")
    cut = sheet["msp"].query('LINE[layer=="A_Kesit_Cizgisi"]')
    lines = [(_apply(ground, (e.dxf.start.x, e.dxf.start.y)), _apply(ground, (e.dxf.end.x, e.dxf.end.y))) for e in cut]
    assert any(a[0] == pytest.approx(3.0) and b[0] == pytest.approx(3.0) and abs(a[1] - b[1]) > 9 for a, b in lines)


def _section_numbers(sheet):
    """What the heights truth names, read from the drawn section (region r6) with the region's own transform."""
    section = _region(sheet, id="r6")
    to_sz = lambda p: _apply(section, p)                                                # noqa: E731
    bands = sorted((e for e in _in_region(sheet, section, "LWPOLYLINE", "K_Kesit") if e.closed), key=lambda e: _rect_of(e)[1])
    slabs = [(to_sz(_rect_of(e)[2:])[1], to_sz(_rect_of(e)[2:])[1] - to_sz(_rect_of(e)[:2])[1]) for e in bands]
    marks = []
    for tri in _in_region(sheet, section, "LWPOLYLINE", "K_Kot"):
        apex = min(tri.get_points("xy"), key=lambda p: p[1])
        near = [t for t in sheet["msp"].query("TEXT") if abs(t.dxf.insert.y - apex[1]) < 20 and 0 < apex[0] - t.dxf.insert.x < 200]
        assert len(near) == 1                                                           # one printed mark per triangle
        marks.append((round(to_sz(apex)[1], 6), near[0].dxf.text))
    roof = [e for e in _in_region(sheet, section, "LWPOLYLINE", "K_Cati") if e.closed][0]
    pts = [to_sz(p) for p in roof.get_points("xy")]
    assert len(pts) == 6                      # top line (3 points), tip drop, underside back (2 points)
    pitch = math.degrees(math.atan2(pts[1][1] - pts[0][1], pts[1][0] - pts[0][0]))
    vertical_gap = pts[1][1] - pts[4][1]
    lines = [(to_sz((e.dxf.start.x, e.dxf.start.y)), to_sz((e.dxf.end.x, e.dxf.end.y)))
             for e in _in_region(sheet, section, "LINE", "K_Kesit")]
    vertical = [(a, b) for a, b in lines if abs(a[0] - b[0]) < 1e-9]
    outer, far = min(a[0] for a, _ in vertical), max(a[0] for a, _ in vertical)           # the two outer wall faces
    knee = [round(b[1] - a[1], 6) for a, b in vertical if min(abs(a[0] - outer), abs(a[0] - far)) < 1e-9 and abs(a[1] - 3.0) < 1e-9]
    ground = [round(a[1], 6) for a, _ in ((to_sz((e.dxf.start.x, e.dxf.start.y)), 0) for e in _in_region(sheet, section, "LINE", "K_Zemin"))]
    return {"slabs": [(round(t, 6), round(d, 6)) for t, d in slabs], "marks": sorted(marks), "pitch": pitch,
            "eaves": pts[0][1], "ridge": pts[1][1], "ridge_under": pts[4][1], "eaves_under": pts[5][1],
            "overhang": outer - pts[0][0], "thickness": vertical_gap * math.cos(math.radians(pitch)), "knee": sorted(knee),
            "ground": ground, "profile": [list(p) for p in pts[:3]], "roof_entity": f"LWPOLYLINE:{roof.dxf.handle}"}


def test_synthetic_07_heights_truth_equals_the_drawn_section(sheet):
    h = sheet["heights"]
    got = _section_numbers(sheet)
    # Slab tops and thicknesses (three bands of 0.20 m); the printed mark equals the z its triangle points at.
    assert got["slabs"] == [(-3.0, 0.2), (0.0, 0.2), (3.0, 0.2)]
    assert [(t["z_top"], t["thickness"]) for t in h["slabs"]] == got["slabs"]
    assert got["marks"] == [(-3.0, "-3.00"), (0.0, "±0.00"), (3.0, "+3.00")]
    assert [(lv["level_id"], lv["level_mark"], lv["level_mark_target_z"], lv["level_mark_text"]) for lv in h["levels"]] == [
        ("L-1", -3.0, -3.0, "-3.00"), ("L0", 0.0, 0.0, "±0.00"), ("L1", 3.0, 3.0, "+3.00")]
    assert h["datum"]["value"] == 0.0 and h["datum"]["printed"] == "±0.00"
    # Heights add up: floor to floor = difference of the slab tops, ceiling = the slab above's underside - the floor.
    tops = [t["z_top"] for t in h["slabs"]]
    levels = {lv["level_id"]: lv for lv in h["levels"]}
    assert [levels[i]["floor_z"] for i in ("L-1", "L0", "L1")] == tops
    assert [levels[i]["floor_to_floor"] for i in ("L-1", "L0", "L1")] == [tops[1] - tops[0], tops[2] - tops[1], None] == [3.0, 3.0, None]
    assert [levels[i]["ceiling_height"] for i in ("L-1", "L0")] == [tops[1] - 0.2 - tops[0], tops[2] - 0.2 - tops[1]] == [2.8, 2.8]
    roof = h["roof"]
    assert levels["L1"]["ceiling_height"] == pytest.approx(roof["ridge_underside_z"] - 3.0, abs=1e-5)    # no flat part is drawn
    assert got["ground"] == [0.0, 0.0] and [g["z"] for g in h["ground"]] == [0.0, 0.0, 0.0]
    assert [g["side"] for g in h["ground"]] == ["south", "north", "east"]
    # The roof: 35 degrees, eaves and ridge = the top line, 0.25 m thick perpendicular to the slope, 0.5 m overhang,
    # knee wall 1.00 m (outer face from the attic floor to the roof underside).
    assert got["pitch"] == pytest.approx(35.0, abs=1e-6) and roof["pitches_deg"] == [35.0]
    assert got["eaves"] == pytest.approx(roof["eaves_z"], abs=1e-5) and got["ridge"] == pytest.approx(roof["ridge_z"], abs=1e-5)
    assert got["ridge_under"] == pytest.approx(roof["ridge_underside_z"], abs=1e-5)
    assert got["eaves_under"] == pytest.approx(roof["eaves_underside_z"], abs=1e-5)
    assert got["thickness"] == pytest.approx(roof["thickness"], abs=1e-5) == pytest.approx(0.25)
    assert got["overhang"] == pytest.approx(roof["overhang"]) == pytest.approx(0.5)
    assert got["knee"] == [1.0, 1.0] and roof["knee_wall"] == 1.0
    assert [v for p in roof["profile"] for v in p] == pytest.approx([v for p in got["profile"] for v in p], abs=1e-5)
    assert roof["entities"]["roof"] == got["roof_entity"]
    tan = math.tan(math.radians(35.0))
    assert roof["eaves_underside_z"] == pytest.approx(3.0 + roof["knee_wall"] - roof["overhang"] * tan, abs=1e-5)
    assert roof["ridge_z"] - roof["eaves_z"] == pytest.approx((4.0 + roof["overhang"]) * tan, abs=1e-5)   # ridge over the middle
    # The same numbers are in the building truth.
    levels_b = {lv["id"]: lv for lv in sheet["building"]["levels"]}
    assert levels_b["L1"]["ceiling_height"] == levels["L1"]["ceiling_height"] and levels_b["L0"]["ceiling_height"] == 2.8
    assert all(levels_b[i]["floor_to_floor"]["value"] == 3.0 for i in ("L-1", "L-1b", "L0")) and levels_b["L1"]["floor_to_floor"] is None
    assert [levels_b[i]["elevation"] for i in ("L-1", "L-1b", "L0", "L1")] == [-3.0, -3.0, 0.0, 3.0]


def _elevation_rects(sheet, region):
    """(kind, centre x, width, z0, z1) of every window / door rectangle of an elevation, in metres (region transform)."""
    out = []
    for layer, kind in (("G_Pencere", "window"), ("G_Kapi", "door")):
        for e in _in_region(sheet, region, "LWPOLYLINE", layer):
            (x0, z0), (x1, z1) = _apply(region, _rect_of(e)[:2]), _apply(region, _rect_of(e)[2:])
            out.append((kind, round((x0 + x1) / 2, 6), round(x1 - x0, 6), round(z0, 6), round(z1, 6)))
    return sorted(out, key=lambda t: t[1])


def _plan_openings_on(building, side):
    """The openings on the outer wall of one facade (south: the wall at y 0.125, east: at x 9.875) and their position along
    the facade seen from outside. A viewer outside the south facade looks north (up = +Z): east is on his right, so the
    facade runs west to east (x); outside the east facade he looks west, north is on his right, so it runs south to north (y)."""
    walls = {w["id"]: w for w in building["walls"]}
    out = []
    for o in building["openings"]:
        w = walls[o["wall_id"]]
        if side == "south" and w["exterior"] and w["start"][1] == w["end"][1] == 0.125:
            out.append((o, o["center"][0]))
        elif side == "east" and w["exterior"] and w["start"][0] == w["end"][0] == 9.875:
            out.append((o, o["center"][1]))
    return out


def test_synthetic_07_elevation_openings_match_the_plan_openings(sheet):
    building = sheet["building"]
    elevation = {lv["id"]: lv["elevation"] for lv in building["levels"]}
    seen = {(item["region"]): item for item in sheet["exterior"]["openings_seen"]}
    for rid, side in (("r7", "south"), ("r8", "east")):
        region = _region(sheet, id=rid)
        drawn = _elevation_rects(sheet, region)
        plan = _plan_openings_on(building, side)
        above, below = [(o, x) for o, x in plan if o["height"] is not None], [(o, x) for o, x in plan if o["height"] is None]
        # Every drawn rectangle is a plan opening of that facade at the same position, width, sill and head; none is missing.
        expected = sorted((o["type"], round(x, 6), o["width"], round(elevation[o["level_id"]] + o["sill_height"], 6),
                           round(elevation[o["level_id"]] + o["sill_height"] + o["height"], 6)) for o, x in above)
        assert [d for d in sorted(drawn)] == expected
        # What is not drawn stands below the ground line (the basement, plans only) and has no height in the truth.
        assert below and {o["level_id"] for o, _ in below} == {"L-1", "L-1b"}
        assert all(elevation[o["level_id"]] + 2.0 + 0.6 <= 0.0 for o, _ in below)
        # The exterior truth lists the same rectangles, with the entities that draw them.
        item = seen[rid]
        assert item["side"] == side and item["windows"] == sum(d[0] == "window" for d in drawn) and item["doors"] == sum(d[0] == "door" for d in drawn)
        assert [(p["kind"], p["x"], p["width"], p["sill"], p["head"]) for p in item["positions_m"]] == [
            (d[0], d[1], d[2], d[3], d[4]) for d in drawn]
        assert {p["opening_id"] for p in item["positions_m"]} == {o["id"] for o, _ in above}
        for p in item["positions_m"]:
            assert _entity(sheet, p["entity"]).dxf.layer == ("G_Kapi" if p["kind"] == "door" else "G_Pencere")
    assert (seen["r7"]["view_bearing_deg"], seen["r8"]["view_bearing_deg"]) == (90.0, 180.0)      # looking north / west
    assert [(d[0], d[1]) for d in _elevation_rects(sheet, _region(sheet, id="r7"))] == [("window", 1.5), ("door", 4.5), ("window", 8.0)]


def test_synthetic_07_exterior_truth_equals_the_drawing(sheet):
    ext, msp = sheet["exterior"], sheet["msp"]
    attic, site, south = _region(sheet, id="r4"), _region(sheet, id="r5"), _region(sheet, id="r7")
    # Roof: the dashed outline 0.5 m outside the outer faces and the ridge line on the attic plan.
    outline = [e for e in _in_region(sheet, attic, "LWPOLYLINE", "A_Cati") if e.closed][0]
    assert outline.dxf.linetype == "DASHED"
    lo, hi = _apply(attic, _rect_of(outline)[:2]), _apply(attic, _rect_of(outline)[2:])
    faces = [p for f in _in_region(sheet, attic, "LWPOLYLINE", "AR_w_sld") for p in f.get_points("xy")]
    f0, f1 = _apply(attic, (min(p[0] for p in faces), min(p[1] for p in faces))), _apply(attic, (max(p[0] for p in faces), max(p[1] for p in faces)))
    assert (f0[0] - lo[0], f0[1] - lo[1], hi[0] - f1[0], hi[1] - f1[1]) == pytest.approx((0.5,) * 4)
    assert ext["roof"]["outline"] == [[lo[0], lo[1]], [hi[0], lo[1]], [hi[0], hi[1]], [lo[0], hi[1]]]
    ridge = [e for e in _in_region(sheet, attic, "LINE", "A_Cati")][0]
    a, b = _apply(attic, (ridge.dxf.start.x, ridge.dxf.start.y)), _apply(attic, (ridge.dxf.end.x, ridge.dxf.end.y))
    assert [list(a), list(b)] == ext["roof"]["ridge_lines"][0] and a[1] == b[1] == 4.0 and ext["roof"]["break_line"] is None
    assert ext["roof"]["type"] == "gable" and ext["roof"]["type_source"] == "section"
    terrace = ext["roof"]["openings"][0]
    assert terrace["room_id"] == "r_L1_teras" and [w for w in terrace["parapet_wall_ids"]] == ["w_L1_001", "w_L1_002"]
    assert Polygon(terrace["polygon"]).bounds == pytest.approx((6.1, -0.5, 10.5, 4.0))
    # Facade: the stone plinth is a hatch on the south elevation (z 0 .. 0.6, the whole width), labelled; SIVA and KİREMİT
    # are labels.
    hatch = [h for h in msp.query("HATCH") if _within(_box_of(h), south["box"])][0]
    path = [_apply(south, p) for p in hatch.paths[0].vertices]
    assert (min(p[0] for p in path), max(p[0] for p in path), min(p[1] for p in path), max(p[1] for p in path)) == pytest.approx(
        (0.0, 10.0, 0.0, 0.6))
    stone, render_s, render_e = ext["facade"]
    assert (stone["side"], stone["material"], stone["source"], stone["z_range"]) == ("south", "stone_cladding", "hatch", [0.0, 0.6])
    assert (render_s["material"], render_s["source"], render_e["side"]) == ("render", "label", "east")
    for item, text in ((stone, "TAŞ KAPLAMA"), (render_s, "SIVA"), (render_e, "SIVA")):
        assert text in {_entity(sheet, e).dxf.text for e in item["entities"] if e.startswith("TEXT")}
    assert _entity(sheet, ext["roof"]["covering_entity"]).dxf.text == "KİREMİT" and ext["roof"]["covering"] == "clay_tiles"
    # Site plan: plot boundary, plot walls, building outline, parking, trees, road, north arrow, labels (building metres).
    s = ext["site"]
    to_b = lambda e: [list(_apply(site, p)) for p in e.get_points("xy")]                  # noqa: E731
    plot = [e for e in _in_region(sheet, site, "LWPOLYLINE", "V_Parsel")][0]
    assert [v for p in to_b(plot) for v in p] == pytest.approx([v for p in s["plot"] for v in p])
    outer, inner = sorted((_rect_of(e) for e in _in_region(sheet, site, "LWPOLYLINE", "V_Sinir_Duv")), key=lambda r: r[0])
    assert (inner[0] - outer[0], inner[1] - outer[1], outer[2] - inner[2], outer[3] - inner[3]) == pytest.approx((20.0,) * 4)
    cx0, cy0, cx1, cy1 = [(a + b) / 2 for a, b in zip(outer, inner)]                          # centre lines of the 0.20 m walls
    corners = [_apply(site, p) for p in ((cx0, cy0), (cx1, cy0), (cx1, cy1), (cx0, cy1))]
    assert [v for w in s["plot_walls"] for v in w["start"] + w["end"]] == pytest.approx(
        [v for i in range(4) for v in list(corners[i]) + list(corners[(i + 1) % 4])])
    assert all(w["thickness"] == 0.2 for w in s["plot_walls"]) and len(s["plot_walls"]) == 4
    parking = [e for e in _in_region(sheet, site, "LWPOLYLINE", "V_Yol") if len(e) == 4 and _rect_of(e)[2] - _rect_of(e)[0] < 1000]
    assert len(parking) == 1 and [v for p in to_b(parking[0]) for v in p] == pytest.approx([v for p in s["parking"][0]["polygon"] for v in p])
    trees = sorted(tuple(_apply(site, (e.dxf.insert.x, e.dxf.insert.y))) for e in _in_region(sheet, site, "INSERT", "V_Agac"))
    assert [v for t in trees for v in t] == pytest.approx([v for t in sorted(t["center"] for t in s["trees"]) for v in t])
    assert all(e.dxf.name == "AGAC" for e in _in_region(sheet, site, "INSERT", "V_Agac"))
    north = [e for e in _in_region(sheet, site, "INSERT", "V_Kuzey")][0]
    assert north.dxf.name == "KUZEY" and north.dxf.rotation == 0.0 and ext["north"]["value"] == 0.0     # building +Y is north
    arrow = [e for e in sheet["doc"].blocks.get("KUZEY") if e.dxftype() == "LWPOLYLINE"][0]
    assert min(arrow.get_points("xy"), key=lambda p: p[1]) != max(arrow.get_points("xy"), key=lambda p: p[1])
    assert max(arrow.get_points("xy"), key=lambda p: p[1]) == (0.0, 70.0)                          # the tip points up the sheet
    assert {t["text"]: tuple(_apply(site, (_entity(sheet, t["entity"]).dxf.insert.x, _entity(sheet, t["entity"]).dxf.insert.y)))
            for t in s["labels"]} == {t["text"]: pytest.approx(tuple(t["at"])) for t in s["labels"]}
    assert _entity(sheet, ext["north"]["letter_entity"]).dxf.text == "N" and _entity(sheet, s["road"]["entity"]).dxf.layer == "V_Yol"
    assert ext["brief_exterior_words"] == yaml.safe_load((sheet["folder"] / "brief.yaml").read_text(encoding="utf-8"))["exterior"]


def test_synthetic_07_building_truth_is_the_usual_plan_truth(sheet):
    b, msp = sheet["building"], sheet["msp"]
    assert [lv["id"] for lv in b["levels"]] == ["L-1", "L-1b", "L0", "L1"]
    assert [(lv["kind"], lv["variant"], lv["variant_slug"], lv["variant_group"], lv["base_level_id"], lv["region_id"])
            for lv in b["levels"]] == [
        ("basement", "base", "base", "vg_L-1", None, "r1"), ("basement", "Açık mutfak", "acik-mutfak", "vg_L-1", "L-1", "r2"),
        ("floor", "base", "base", None, None, "r3"), ("attic", "base", "base", None, None, "r4")]
    assert [(v["id"], v["rooms_changed"], v["exterior_changed"]) for v in b["variants"]] == [
        ("base", [], False), ("l-1b-acik-mutfak", ["r_L-1b_salon_acik_mutfak"], False)]
    assert [(len(b[k])) for k in ("walls", "openings", "rooms", "furniture")] == [24, 34, 11, 18]
    assert b["conflicts"] == [] and b["unverified"] == [] and b["status"] == "ok"
    # Pages: one record per region read, used for the heights or the exterior, with the region's box.
    pages = b["documents"][0]["pages"]
    assert [p["region_id"] for p in pages] == ["r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8"]
    for page in pages:
        region = _region(sheet, id=page["region_id"])
        assert page["region_box"] == region["box"] and page["region_class"] == region["class"]
        assert page["transform_to_building"] == region["transform_to_building"] and page["scale"]["metres_per_unit"] == 0.01
    # Doors: one sliding door per basement plan, one double door (the entrance), the rest swing; windows have no operation.
    doors = [o for o in b["openings"] if o["type"] == "door"]
    assert Counter((o["level_id"], o["operation"]) for o in doors if o["operation"] != "swing") == Counter(
        {("L-1", "sliding"): 1, ("L-1b", "sliding"): 1, ("L0", "double"): 1})
    assert len(doors) == 12 and all(o["operation_source"] == "geometry" for o in doors)
    assert all("operation" not in o for o in b["openings"] if o["type"] == "window")
    by_block = {o["id"]: o["evidence"][0]["block"] for o in b["openings"]}
    assert {by_block[o["id"]] for o in doors if o["operation"] == "sliding"} == {"KAPI_SURME_90"}
    assert {by_block[o["id"]] for o in doors if o["operation"] == "double"} == {"KAPI_CIFT_140"}
    # Furniture only where the brief says: one bed (the bedroom), a 3-seat sofa (the basement salon), toilet, washbasin and
    # shower (the bathroom), the stair on every level (same footprint), the counter run.
    types = Counter((f["room_id"], f["type"]) for f in b["furniture"])
    assert types[("r_L0_yatak_odasi", "bed_double")] == 1 and sum(f["type"] == "bed_double" for f in b["furniture"]) == 1
    assert types[("r_L-1_salon", "sofa")] == 1 and types[("r_L-1b_salon_acik_mutfak", "sofa")] == 1
    assert {t for (room, t) in types if room == "r_L0_banyo"} == {"toilet", "washbasin", "shower"}
    assert {t for (room, t) in types if room == "r_L-1_mutfak"} == {"kitchen_counter", "fridge", "sink_kitchen", "stove"}
    stairs = [f for f in b["furniture"] if f["type"] == "stair"]
    assert len(stairs) == 4 and len({json.dumps(f["footprint"]) for f in stairs}) == 1 and all(f["front_deg"] is None for f in stairs)
    assert {f["room_id"] for f in stairs} == {f"r_{lv}_hol" for lv in ("L-1", "L-1b", "L0", "L1")}
    # Rooms: labels, area lines that match the polygons, the open-kitchen room, same_as.
    rooms = {r["id"]: r for r in b["rooms"]}
    assert rooms["r_L-1_salon"]["label_raw"] == "SALON\n43.5M2" and rooms["r_L1_teras"]["room_type"] == "balcony"
    assert not rooms["r_L1_oyun_odasi"]["has_documented_furniture"] and not rooms["r_L1_teras"]["has_documented_furniture"]
    assert len(rooms["r_L-1b_salon_acik_mutfak"]["polygon"]) == 6 and rooms["r_L-1b_hol"]["same_as"] == "r_L-1_hol"
    for r in rooms.values():
        assert abs(r["area_label"] - r["area_computed"]) / r["area_label"] <= 0.01
        assert Polygon(r["polygon"]).is_valid and all(0.25 - 1e-9 <= x <= 9.75 + 1e-9 and 0.25 - 1e-9 <= y <= 7.75 + 1e-9
                                                      for x, y in r["polygon"])
    for level in ("L-1", "L-1b", "L0", "L1"):
        polys = [Polygon(r["polygon"]) for r in rooms.values() if r["level_id"] == level]
        assert all(p.intersection(q).area < 1e-9 for i, p in enumerate(polys) for q in polys[i + 1:])
    # Every wall: the same outline on every level (outer faces 0..10 x 0..8, building frame), openings on their walls.
    walls = {w["id"]: w for w in b["walls"]}
    for level in ("L-1", "L-1b", "L0", "L1"):
        outer = [w for w in b["walls"] if w["level_id"] == level and w["exterior"]]
        assert [(w["start"], w["end"], w["thickness"]) for w in outer] == [
            ([0.0, 0.125], [10.0, 0.125], 0.25), ([9.875, 0.0], [9.875, 8.0], 0.25), ([0.0, 7.875], [10.0, 7.875], 0.25),
            ([0.125, 0.0], [0.125, 8.0], 0.25)]
    for o in b["openings"]:
        w = walls[o["wall_id"]]
        assert G.point_segment_distance(o["center"], w["start"], w["end"]) < 1e-6 and w["level_id"] == o["level_id"]
        if o["type"] == "door":
            assert rooms[o["swing_side"]]["level_id"] == o["level_id"]
    # Evidence points at the drawn entities: wall face lines (each line serves exactly one wall), INSERTs, labels.
    face_lines = {f"LWPOLYLINE:{f.dxf.handle}" for f in msp.query('LWPOLYLINE[layer=="AR_w_sld"]')}
    used = [e["entity"] for w in b["walls"] for e in w["evidence"]]
    assert len(used) == len(set(used)) and set(used) == face_lines
    for o in b["openings"]:
        e = _entity(sheet, o["evidence"][0]["entity"])
        assert e.dxftype() == "INSERT" and e.dxf.name == o["evidence"][0]["block"]
        region = _region(sheet, id=next(lv["region_id"] for lv in b["levels"] if lv["id"] == o["level_id"]))
        assert _apply(region, (e.dxf.insert.x, e.dxf.insert.y)) == pytest.approx(tuple(o["center"]), abs=TOL)
    for f in b["furniture"]:
        e = _entity(sheet, f["evidence"][0]["entity"])
        region = _region(sheet, id=next(lv["region_id"] for lv in b["levels"] if lv["id"] == f["level_id"]))
        assert e.dxf.name == f["type_raw"] and G.angle_difference_deg(e.dxf.rotation, f["footprint"]["rotation_deg"]) < 1e-6
        assert _apply(region, (e.dxf.insert.x, e.dxf.insert.y)) == pytest.approx(tuple(f["footprint"]["center"]), abs=TOL)
        if f["type"] != "stair":
            assert f["front_deg"] == G.front_direction_deg(f["footprint"]["rotation_deg"])
    for r in b["rooms"]:
        assert _entity(sheet, r["evidence"][0]["entity"]).text == "\\H20;" + r["label_raw"].replace("\n", "\\P")


def test_synthetic_07_wall_faces_stop_at_every_opening(sheet):
    """The face lines are cut at each opening: the gap is the opening's clear width, the faces go on right behind it."""
    b = sheet["building"]
    walls = {w["id"]: w for w in b["walls"]}
    for level in b["levels"]:
        region = _region(sheet, id=level["region_id"])
        segments = [[_apply(region, p) for p in f.get_points("xy")] for f in _in_region(sheet, region, "LWPOLYLINE", "AR_w_sld")]

        def covered(p):
            return any(G.point_segment_distance(p, a, c) < 1e-6 for a, c in segments)

        for o in (o for o in b["openings"] if o["level_id"] == level["id"]):
            w = walls[o["wall_id"]]
            length = G.distance(w["start"], w["end"])
            u = ((w["end"][0] - w["start"][0]) / length, (w["end"][1] - w["start"][1]) / length)
            n = (-u[1], u[0])
            for side in (-1, 1):
                off = side * w["thickness"] / 2
                base = (o["center"][0] + n[0] * off, o["center"][1] + n[1] * off)
                inside = [(base[0] + u[0] * k * (o["width"] / 2 - 0.01), base[1] + u[1] * k * (o["width"] / 2 - 0.01)) for k in (-1, 0, 1)]
                behind = [(base[0] + u[0] * k * (o["width"] / 2 + 0.01), base[1] + u[1] * k * (o["width"] / 2 + 0.01)) for k in (-1, 1)]
                assert not any(covered(p) for p in inside), (o["id"], side)
                assert all(covered(p) for p in behind), (o["id"], side)


@pytest.mark.skipif(not HAS_DXF2DWG, reason="LibreDWG dxf2dwg not built here (scripts/cloud-setup.sh)")
def test_synthetic_07_dwg_copy(generated, sheet, tmp_path):
    import hashlib

    from wenart.synthetic.projects import DWG_SHA256_07

    dwg = generated[0] / P7 / "source" / "sheet.dwg"
    assert hashlib.sha256(dwg.read_bytes()).hexdigest() == DWG_SHA256_07
    # The DWG reads like its DXF: the same entities, layers, blocks and texts (only the MTEXT height field is lost, it is
    # also written inline); the project folder holds one document, the DXF.
    conv = dwg_tool.convert(dwg, tmp_path)
    assert conv.acadver == "AC1015" and conv.audit_errors == 0
    from_dwg, _ = recover.readfile(str(conv.dxf_path))

    def key(e):
        t, layer = e.dxftype(), e.dxf.layer
        if t == "LINE":
            return (t, layer, tuple(round(v, 3) for v in e.dxf.start), tuple(round(v, 3) for v in e.dxf.end))
        if t == "LWPOLYLINE":
            return (t, layer, bool(e.closed), tuple((round(x, 3), round(y, 3)) for x, y in e.get_points("xy")))
        if t == "INSERT":
            return (t, layer, e.dxf.name, tuple(round(v, 3) for v in e.dxf.insert), round(e.dxf.rotation, 3))
        if t == "TEXT":
            return (t, layer, e.dxf.text, tuple(round(v, 3) for v in e.dxf.insert), e.dxf.height)
        if t == "MTEXT":
            return (t, layer, e.text, tuple(round(v, 3) for v in e.dxf.insert))
        return (t, layer)

    assert Counter(key(e) for e in from_dwg.modelspace()) == Counter(key(e) for e in sheet["msp"])
    assert from_dwg.header["$INSUNITS"] == 5
    assert sorted(b.name for b in from_dwg.blocks if not b.name.startswith(("*", "_"))) == sorted(
        b.name for b in sheet["doc"].blocks if not b.name.startswith(("*", "_")))
    assert [p.name for p in (generated[0] / P7).iterdir() if p.suffix in (".dxf", ".dwg")] == ["sheet.dxf"]


def test_synthetic_07_brief(sheet):
    from wenart import brief as BR

    raw = yaml.safe_load((sheet["folder"] / "brief.yaml").read_text(encoding="utf-8"))
    assert raw["style"] and raw["exterior"] == {"facade": "white render", "roof": "clay tiles",
                                               "window_frame": "anthracite aluminium"}
    merged = BR.merge_brief(raw)
    assert merged["warnings"] == [] and BR.value(merged, "exterior.facade") == "white render"
    assert BR.value(merged, "exterior.window_frame") == "anthracite aluminium" and "exterior.paving" in merged["assumed"]
    assert sheet["building"]["project"]["brief"] == raw


def test_synthetic_07_reading_order_refuses_a_tie():
    project = project_07()
    assert list(project.region_ids().values()) == [f"r{i}" for i in range(1, 11)]
    other = project.drawing("basement_alt")
    other.origin = (other.origin[0], project.drawing("basement").origin[1])
    with pytest.raises(ValueError, match="same box top"):
        project.reading_order()


def test_synthetic_07_sheets_truth_follows_the_sheets_schema(sheet):
    """The truth uses the field names of sheets.json: documents, regions, stray, levels and variants validate against the
    frozen schema's definitions (heights and exterior are plain-number files of their own)."""
    import jsonschema

    schema = json.loads((ROOT / "wenart" / "schema" / "sheets.schema.json").read_text(encoding="utf-8"))
    truth = sheet["sheets"]
    for key, definition in (("documents", "document"), ("regions", "region"), ("stray", "stray"), ("levels", "level"),
                            ("variants", "variant"), ("conflicts", "conflict")):
        validator = jsonschema.Draft202012Validator({"$ref": f"#/$defs/{definition}", "$defs": schema["$defs"]})
        for item in truth[key]:
            errors = [f"{'/'.join(map(str, e.absolute_path))}: {e.message}" for e in validator.iter_errors(item)]
            assert errors == [], (key, errors)
    # The heights and exterior files use the schema's keys too.
    heights = set(schema["$defs"]["heights"]["properties"])
    assert {"cut_axis", "cut_at", "flipped", "datum", "levels", "slabs", "ground", "roof"} <= heights
    assert set(sheet["heights"]) >= {"cut_axis", "cut_at", "flipped", "datum", "levels", "slabs", "ground", "roof"}
    assert {"floor_z", "ceiling_height", "floor_to_floor", "level_mark", "level_mark_target_z"} <= set(sheet["heights"]["levels"][0])
    assert set(sheet["heights"]["roof"]) >= {"eaves_z", "ridge_z", "pitches_deg", "knee_wall", "overhang", "thickness", "profile"}
    assert {"roof", "facade", "openings_seen", "site", "north"} <= set(sheet["exterior"])
    assert {"type", "type_source", "outline", "break_line", "ridge_lines", "covering"} <= set(sheet["exterior"]["roof"])


def test_synthetic_07_wall_faces_are_long_enough_to_pair_up(sheet):
    """Every wall face piece is at least 0.40 m long (the face-line wall rule of docs/milestone10.md §3.1.11 pairs faces with
    >= 0.4 m overlap): no pier between two openings, or between an opening and a corner, is shorter."""
    shortest = []
    for level in sheet["building"]["levels"]:
        region = _region(sheet, id=level["region_id"])
        for f in _in_region(sheet, region, "LWPOLYLINE", "AR_w_sld"):
            a, b = [_apply(region, p) for p in f.get_points("xy")]
            shortest.append((G.distance(a, b), level["id"], a, b))
    assert min(shortest)[0] >= 0.40 - 1e-9, min(shortest)


def test_synthetic_07_walls_and_rooms_match_the_face_lines(sheet):
    """Walls and rooms of building.json against the drawn face lines (read back, in building metres): every face line of a wall
    lies on that wall's side faces (centre line +- thickness / 2, inside its extent), and every room's polygon edge runs along
    a face line or across an opening's gap."""
    b = sheet["building"]
    rooms_by_level: dict = {}
    for r in b["rooms"]:
        rooms_by_level.setdefault(r["level_id"], []).append(r)
    for level in b["levels"]:
        region = _region(sheet, id=level["region_id"])
        lines = {f"LWPOLYLINE:{f.dxf.handle}": [_apply(region, p) for p in f.get_points("xy")]
                 for f in _in_region(sheet, region, "LWPOLYLINE", "AR_w_sld")}
        for w in (w for w in b["walls"] if w["level_id"] == level["id"]):
            length = G.distance(w["start"], w["end"])
            ux, uy = (w["end"][0] - w["start"][0]) / length, (w["end"][1] - w["start"][1]) / length
            for ev in w["evidence"]:
                a, c = lines[ev["entity"]]
                for p in (a, c):
                    along = (p[0] - w["start"][0]) * ux + (p[1] - w["start"][1]) * uy
                    across = (p[0] - w["start"][0]) * -uy + (p[1] - w["start"][1]) * ux
                    assert abs(abs(across) - w["thickness"] / 2) < 1e-6, (w["id"], ev["entity"])
                    assert -w["thickness"] / 2 - 1e-6 <= along <= length + w["thickness"] / 2 + 1e-6
        openings = [o for o in b["openings"] if o["level_id"] == level["id"]]
        walls = {w["id"]: w for w in b["walls"]}

        def in_gap(p):
            for o in openings:
                w = walls[o["wall_id"]]
                length = G.distance(w["start"], w["end"])
                ux, uy = (w["end"][0] - w["start"][0]) / length, (w["end"][1] - w["start"][1]) / length
                along = (p[0] - o["center"][0]) * ux + (p[1] - o["center"][1]) * uy
                across = (p[0] - o["center"][0]) * -uy + (p[1] - o["center"][1]) * ux
                if abs(along) <= o["width"] / 2 + 1e-6 and abs(across) <= w["thickness"] / 2 + 1e-6:
                    return True
            return False

        for room in rooms_by_level[level["id"]]:
            poly = room["polygon"]
            for i, a in enumerate(poly):
                c = poly[(i + 1) % len(poly)]
                n = max(2, int(G.distance(a, c) / 0.05))
                for k in range(n + 1):
                    p = (a[0] + (c[0] - a[0]) * k / n, a[1] + (c[1] - a[1]) * k / n)
                    assert any(G.point_segment_distance(p, s0, s1) < 1e-6 for s0, s1 in lines.values()) or in_gap(p), (room["id"], p)
        for f in (f for f in b["furniture"] if f["level_id"] == level["id"]):
            corners = G.rotated_rectangle(f["footprint"]["center"], f["footprint"]["size"], f["footprint"]["rotation_deg"])
            room = next(r for r in rooms_by_level[level["id"]] if r["id"] == f["room_id"])
            assert all(Polygon(room["polygon"]).buffer(1e-6).contains(Point(c)) for c in corners), f["id"]
