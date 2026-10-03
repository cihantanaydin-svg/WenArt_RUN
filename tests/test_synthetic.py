"""CPU tests for the synthetic project generator (docs/milestone2.md §1, docs/milestone6.md §3, docs/milestone7.md
§5.2).

The generator runs once into a temp folder (module fixture). Tests then check
files, schema validity, DXF content via ezdxf, PDF content via pdfplumber,
raster sizes and ink under the truth boxes, determinism, that the
committed projects/ folder matches a fresh run, the projects' counts,
the non-rectangular outline builder, the copied style photo, and synthetic-06
(the CAD project delivered as a DWG, its truth and the titled fixture).
"""
import json
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

ROOT = Path(__file__).resolve().parents[1]
COMMITTED = ROOT / "projects"
# The Level-based projects (Milestones 2 and 6); synthetic-06 is drawn the CAD way and has tests of its own.
NAMES = ["synthetic-01", "synthetic-02", "synthetic-03", "synthetic-04", "synthetic-05"]
ALL_NAMES = NAMES + ["synthetic-06"]
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
}
# Preview JPEGs per project: one per visible page (results/synthetic/<project>_<file stem>_p<page>.jpg).
EXPECTED_PREVIEWS = {
    "synthetic-01": ["zemin_kat_p1", "1_kat_p1", "1_kat_scan_p1"],
    "synthetic-02": ["plan_scan_p1", "plan_photo_p1"],
    "synthetic-03": ["kat_planlari_p1", "kat_planlari_p2", "kat_planlari_p3", "mobilya_plani_p1"],
    "synthetic-04": ["3_kat_plani_p1", "3_kat_plani_pdf_p1"],
    "synthetic-05": ["zemin_kat_p1", "zemin_kat_mobilya_p1"],
    "synthetic-06": ["synthetic-06_p1"],
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

def test_all_projects_lists_six():
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
    """results/synthetic holds exactly one preview per visible page of the six projects."""
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
    b2 = truth(generated, "synthetic-02")
    photo = next(d for d in b2["documents"] if d["file"] == "plan_photo.jpg")["pages"][0]
    assert photo["kind"] == "photo" and photo["scale"] is None and photo["transform_to_building"] is None


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
