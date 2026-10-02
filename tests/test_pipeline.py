"""End-to-end vector path (wenart/ingest/pipeline.py) on the synthetic projects.

The four vector projects (synthetic-01, -03, -04, -05) must reproduce their
truth element by element; synthetic-02 (scan and photo only) stops at
``needs_review``. synthetic-04 draws one level twice (DXF + vector PDF, both
with furniture); synthetic-05 takes its furniture from a furniture-plan DXF
(docs/milestone6.md §3).
"""
import shutil

import ezdxf
import numpy as np
import pytest
from PIL import Image

from wenart import building as B
from wenart import geometry as G
from wenart.ingest import debug_image as DI
from wenart.ingest.dxf_extract import extract_dxf
from wenart.ingest.pipeline import PageWork, _debug_items, build_project, main
from wenart.synthetic.dxf_writer import write_dxf
from wenart.synthetic.model import Furniture
from wenart.synthetic.pdf_writer import write_pdf
from wenart.synthetic.projects import level_01_birinci, level_01_zemin

from conftest import (PROJECTS, assert_one_to_one, furniture_matches, load_truth, opening_matches, room_matches,
                      wall_matches)

NAMES = ["synthetic-01", "synthetic-02", "synthetic-03", "synthetic-04", "synthetic-05"]
VECTOR_NAMES = ["synthetic-01", "synthetic-03", "synthetic-04", "synthetic-05"]
FURNITURE_PLAN_TITLE = "ZEMİN KAT MOBİLYA PLANI"


def write_level_dxf(project, level, file, *, title_raw=None, page_class="floor_plan", **lists):
    """One level as a DXF document of ``project``; ``lists`` restrict what is drawn."""
    project.mkdir(parents=True, exist_ok=True)
    write_dxf(level, project / file, file, title_raw=title_raw or level.title_raw, page_class=page_class, **lists)


def write_level_pdf(project, level, file, *, title_raw=None, page_class="floor_plan", openings=None, furniture=None,
                    dimensions=None):
    """One level as a one-page vector PDF of ``project``; ``None`` draws everything."""
    project.mkdir(parents=True, exist_ok=True)
    write_pdf([{"level": level, "title_raw": title_raw or level.title_raw, "page_class": page_class,
                "openings": level.openings if openings is None else openings,
                "furniture": level.furniture if furniture is None else furniture,
                "dimensions": level.dimensions if dimensions is None else dimensions}], project / file, file)


def count_colour(image: Image.Image, colour, tol: int = 10) -> int:
    """Pixels whose RGB lies within ``tol`` of ``colour`` on every channel."""
    arr = np.asarray(image.convert("RGB")).astype(int)
    return int(np.all(np.abs(arr - np.array(colour)) <= tol, axis=-1).sum())


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("outputs")
    result = {}
    for name in NAMES:
        result[name] = (build_project(PROJECTS / name, out / name), out / name)
    return result


def conflict_keys(conflicts):
    return sorted((c["kind"], tuple(sorted(c["element_ids"]))) for c in conflicts)


@pytest.mark.parametrize("name", VECTOR_NAMES)
def test_matches_truth(built, name):
    building, out_dir = built[name]
    truth = load_truth(name)
    assert building["status"] == "ok"
    B.validate(building)
    assert B.load(out_dir / "building.json") == building
    assert [lv["id"] for lv in building["levels"]] == [lv["id"] for lv in truth["levels"]]
    for mine, theirs in zip(building["levels"], truth["levels"]):
        assert (mine["label"], mine["order"], mine["elevation"]) == (theirs["label"], theirs["order"], theirs["elevation"])
        assert mine["ceiling_height"] == 2.7 and mine["ceiling_height_source"] == "assumed_default"
    assert_one_to_one(building["walls"], truth["walls"],
                      lambda w, t: w["level_id"] == t["level_id"] and wall_matches(w["start"], w["end"], w["thickness"], t),
                      "walls")
    assert_one_to_one(building["openings"], truth["openings"],
                      lambda o, t: o["level_id"] == t["level_id"] and opening_matches(o["type"], o["center"], o["width"], t),
                      "openings")
    assert_one_to_one(building["rooms"], truth["rooms"],
                      lambda r, t: r["level_id"] == t["level_id"] and room_matches(r["label"], r["area_computed"], t),
                      "rooms")
    assert_one_to_one(building["furniture"], truth["furniture"],
                      lambda f, t: f["level_id"] == t["level_id"] and furniture_matches(
                          f["type"], f["footprint"]["center"], f["footprint"]["size"], f["footprint"]["rotation_deg"], t),
                      "furniture")
    assert conflict_keys(building["conflicts"]) == conflict_keys(truth["conflicts"])
    assert building["unverified"] == truth["unverified"]
    assert building["project"].get("brief") == truth["project"].get("brief")
    # Every warning the truth expects is reported (synthetic-01 also reports its skipped scan page).
    assert [w for w in truth["warnings"] if w not in building["warnings"]] == []
    # Element ids, wall links and swing sides follow the same conventions as the truth.
    assert {w["id"] for w in building["walls"]} == {w["id"] for w in truth["walls"]}
    assert {o["id"] for o in building["openings"]} == {o["id"] for o in truth["openings"]}
    assert {r["id"] for r in building["rooms"]} == {r["id"] for r in truth["rooms"]}
    truth_openings = {o["id"]: o for o in truth["openings"]}
    for o in building["openings"]:
        t = truth_openings[o["id"]]
        assert o["wall_id"] == t["wall_id"] and o["swing_side"] == t["swing_side"] and o["status"] == t["status"]
    truth_rooms = {r["id"]: r for r in truth["rooms"]}
    for r in building["rooms"]:
        t = truth_rooms[r["id"]]
        assert r["has_documented_furniture"] == t["has_documented_furniture"]
        assert r["area_label"] == t["area_label"] and r["label_raw"] == t["label_raw"] and r["room_type"] == t["room_type"]
        assert r["status"] == t["status"]
        assert r["polygon"] == t["polygon"], r["id"]   # also the L-shaped rooms of synthetic-04 (6 vertices)
        assert any(e["method"] == "derived" for e in r["evidence"])
    truth_furniture = {f["id"]: f for f in truth["furniture"]}
    for f in building["furniture"]:
        t = truth_furniture[f["id"]]
        assert f["room_id"] == t["room_id"] and f["type_raw"] == t["type_raw"] and f["status"] == t["status"]
        assert f["source"] == "from_documents" and f["front_deg"] == t["front_deg"]


@pytest.mark.parametrize("name", VECTOR_NAMES)
def test_evidence_matches_truth(built, name):
    """Every vector evidence entry of the truth is reproduced (file, page, entity)."""
    building, _ = built[name]
    truth = load_truth(name)
    for key in ("walls", "openings", "rooms", "furniture"):
        mine = {e["id"]: e for e in building[key]}
        for element in truth[key]:
            expected = {(e["file"], e.get("page"), e["entity"]) for e in element["evidence"] if e["method"] == "vector"}
            got = {(e["file"], e.get("page"), e["entity"]) for e in mine[element["id"]]["evidence"] if e["method"] == "vector"}
            assert expected == got, (element["id"], expected, got)


def test_dxf_wins_over_pdf_for_zemin_kat(built):
    building, _ = built["synthetic-03"]
    l0_walls = [w for w in building["walls"] if w["level_id"] == "L0"]
    assert all(w["evidence"][0]["file"] == "mobilya_plani.dxf" for w in l0_walls)
    assert all(len(w["evidence"]) == 2 and w["evidence"][1]["file"] == "kat_planlari.pdf" for w in l0_walls)
    win = next(o for o in building["openings"] if o["id"] == "win_L0_004")
    assert [e["file"] for e in win["evidence"]] == ["mobilya_plani.dxf"] and win["status"] == "verified"
    conflict = next(c for c in building["conflicts"] if c["kind"] == "count_mismatch")
    assert conflict["element_ids"] == ["win_L0_004"] and "DXF wins" in conflict["resolution"]
    area = next(c for c in building["conflicts"] if c["kind"] == "area_label_vs_computed")
    assert area["element_ids"] == ["r_L0_salon"] and "within tolerance" in area["resolution"]
    dim = next(c for c in building["conflicts"] if c["kind"] == "dimension_vs_measured")
    assert dim["element_ids"] == ["w_L-1_004"] and "3,99" in dim["description"]
    assert [c["id"] for c in building["conflicts"]] == ["c_001", "c_002", "c_003"]
    salon = next(r for r in building["rooms"] if r["id"] == "r_L0_salon")
    assert [e["file"] for e in salon["evidence"]] == ["mobilya_plani.dxf", "kat_planlari.pdf", "mobilya_plani.dxf"]


def test_dxf_and_pdf_of_the_same_level_agree_synthetic_04(built):
    """synthetic-04 draws L3 as DXF and vector PDF, both with furniture: the DXF is the master, every
    element is confirmed by the PDF (two evidence entries), the untyped PDF footprints take the DXF
    block types, and the 45-degree armchair is matched across both documents."""
    building, _ = built["synthetic-04"]
    assert building["status"] == "ok" and building["conflicts"] == [] and building["unverified"] == []
    assert [lv["id"] for lv in building["levels"]] == ["L3"] and building["levels"][0]["elevation"] == 9.0
    for key in ("walls", "openings", "furniture"):
        for element in building[key]:
            assert [e["file"] for e in element["evidence"]] == ["3_kat_plani.dxf", "3_kat_plani_pdf.pdf"], element["id"]
            assert element["status"] == "verified"
    for piece in building["furniture"]:
        assert piece["type"] != "unknown" and piece["source"] == "from_documents"
        dxf, pdf = piece["evidence"]
        assert dxf["entity"].startswith("INSERT:") and dxf["block"] == piece["type_raw"]
        assert pdf["entity"].startswith("path:") and pdf["page"] == 1
    armchair = next(f for f in building["furniture"] if f["type_raw"] == "KOLTUK")
    assert armchair["footprint"]["rotation_deg"] == pytest.approx(315.0) and armchair["front_deg"] == pytest.approx(225.0)
    assert armchair["room_id"] == "r_L3_salon_mutfak"
    rooms = {r["id"]: r for r in building["rooms"]}
    assert len(rooms["r_L3_salon_mutfak"]["polygon"]) == 6 and len(rooms["r_L3_hol"]["polygon"]) == 6
    assert rooms["r_L3_salon_mutfak"]["room_type"] == "living" and rooms["r_L3_salon_mutfak"]["area_label"] == 39.05
    assert not rooms["r_L3_hol"]["has_documented_furniture"] and not rooms["r_L3_cocuk_odasi"]["has_documented_furniture"]
    assert sorted(d["file"] for d in building["documents"]) == ["3_kat_plani.dxf", "3_kat_plani_pdf.pdf"]


def test_furniture_plan_is_the_furniture_source_synthetic_05(built):
    """synthetic-05: the floor-plan DXF draws no furniture, the furniture-plan DXF draws all 26 pieces; the
    pipeline takes them from the furniture plan and says so in a warning. The style photo is not a document."""
    building, out_dir = built["synthetic-05"]
    truth = load_truth("synthetic-05")
    assert building["status"] == "ok" and building["conflicts"] == [] and building["unverified"] == []
    expected = "Zemin Kat: furniture taken from zemin_kat_mobilya.dxf (26 pieces); zemin_kat.dxf draws none"
    assert expected in building["warnings"] and expected in truth["warnings"]
    assert expected in (out_dir / "report.md").read_text(encoding="utf-8")
    assert sorted(d["file"] for d in building["documents"]) == ["zemin_kat.dxf", "zemin_kat_mobilya.dxf"]
    assert len(building["furniture"]) == 26
    for piece in building["furniture"]:
        assert [e["file"] for e in piece["evidence"]] == ["zemin_kat_mobilya.dxf"] and piece["status"] == "verified"
    for wall in building["walls"]:
        assert [e["file"] for e in wall["evidence"]] == ["zemin_kat.dxf", "zemin_kat_mobilya.dxf"]
    assert sum(w["exterior"] for w in building["walls"]) == 6
    assert furnished_room_labels(building) == ["Banyo", "Ebeveyn Banyo", "Ebeveyn Yatak Odası", "Mutfak", "Salon",
                                               "Yatak Odası"]
    types = {r["label"]: r["room_type"] for r in building["rooms"]}
    assert types["Ebeveyn Banyo"] == "bathroom" and types["Çalışma Odası"] == "other"
    assert building["project"]["brief"]["style_photos"] == ["salon_referans.jpg"]
    assert building["project"]["brief"]["polish"] is False


def test_documents_and_outputs(built):
    building, out_dir = built["synthetic-01"]
    docs = {d["file"]: d for d in building["documents"]}
    assert set(docs) == {"zemin_kat.dxf", "1_kat.pdf", "1_kat_scan.png"}
    assert docs["zemin_kat.dxf"]["id"] == "doc_zemin_kat_dxf" and docs["zemin_kat.dxf"]["format"] == "dxf"
    dxf_page = docs["zemin_kat.dxf"]["pages"][0]
    assert dxf_page["scale"]["method"] == "dxf_insunits" and dxf_page["transform_to_building"] == [0.001, 0.0, 0.0, 0.0, 0.001, 0.0]
    assert dxf_page["debug_image"] == "debug/zemin_kat_dxf_p1.png"
    pdf_page = docs["1_kat.pdf"]["pages"][0]
    assert pdf_page["scale"]["method"] == "pdf_scale_text" and pdf_page["level_id"] == "L1"
    assert pdf_page["transform_to_building"] == pytest.approx(
        next(p for p in load_truth("synthetic-01")["documents"] if p["file"] == "1_kat.pdf")["pages"][0]["transform_to_building"])
    scan_page = docs["1_kat_scan.png"]["pages"][0]
    assert scan_page["kind"] == "scan" and scan_page["class"] == "other" and scan_page["skip_reason"]
    for doc in building["documents"]:
        for page in doc["pages"]:
            assert page["debug_image"] and (out_dir / page["debug_image"]).is_file()
    # The debug image is the page raster plus the detected elements: vector
    # green for walls/openings/furniture, derived grey for the room polygons.
    plain = DI.raster_from_dxf(PROJECTS / "synthetic-01" / "zemin_kat.dxf").image
    with Image.open(out_dir / "debug/zemin_kat_dxf_p1.png") as debug:
        assert debug.size == plain.size
        diff = np.abs(np.asarray(debug.convert("RGB")).astype(int) - np.asarray(plain).astype(int))
        assert diff.mean() > 1.0
        assert count_colour(plain, DI.COLOURS["vector"]) == 0 and count_colour(debug, DI.COLOURS["vector"]) > 1000
        assert count_colour(debug, DI.COLOURS["derived"]) - count_colour(plain, DI.COLOURS["derived"]) > 100
        assert count_colour(debug, DI.UNVERIFIED_COLOUR) == 0
    report = (out_dir / "report.md").read_text(encoding="utf-8")
    for heading in ("## Documents", "## Levels", "## Rooms", "## Furniture", "## Conflicts", "## Unverified", "## Warnings"):
        assert heading in report
    assert "r_L0_salon" in report and "Status: **ok**" in report
    assert any("ceiling height assumed 2.70 m" in w for w in building["warnings"])
    assert building["project"]["brief"]["style"].startswith("Scandinavian")


def test_debug_image_draws_unverified_items_dashed_red(built):
    """synthetic-03's BLOK_A (unknown block) must show up in red on the DXF page."""
    building, out_dir = built["synthetic-03"]
    assert building["unverified"] == ["f_L0_021"]
    plain = DI.raster_from_dxf(PROJECTS / "synthetic-03" / "mobilya_plani.dxf").image
    with Image.open(out_dir / "debug/mobilya_plani_dxf_p1.png") as debug:
        assert count_colour(plain, DI.UNVERIFIED_COLOUR) == 0 and count_colour(debug, DI.UNVERIFIED_COLOUR) > 50
        assert count_colour(debug, DI.COLOURS["vector"]) > 1000


def test_debug_items_cover_every_element(built):
    """One overlay per room, wall, opening, furniture piece, text and dimension."""
    building, _ = built["synthetic-03"]
    ex = extract_dxf(PROJECTS / "synthetic-03" / "mobilya_plani.dxf", "L0", "mobilya_plani.dxf")
    work = PageWork(record=None, extraction=ex, rooms=[r for r in building["rooms"] if r["level_id"] == "L0"])
    items = _debug_items(work)
    texts = [t for t in ex.texts if t.role != "dimension"]
    assert len(items) == len(work.rooms) + len(ex.walls) + len(ex.openings) + len(ex.furniture) + len(texts) + len(ex.dimensions)
    assert len(work.rooms) == 7 and len(ex.furniture) == 21
    assert {item.method for item in items} == {"derived", "vector"}
    unverified = [item for item in items if item.status == "unverified"]
    assert len(unverified) == 1 and unverified[0].label.endswith("unknown")
    assert all(len(item.polygon) == 4 for item in items if item.method == "vector")


def test_raster_only_project_needs_review(built):
    building, out_dir = built["synthetic-02"]
    assert building["status"] == "needs_review"
    B.validate(building)
    assert building["levels"] == [] and building["walls"] == [] and "brief" not in building["project"]
    assert [d["file"] for d in building["documents"]] == ["plan_photo.jpg", "plan_scan.png"]
    kinds = {d["file"]: d["pages"][0]["kind"] for d in building["documents"]}
    assert kinds == {"plan_photo.jpg": "photo", "plan_scan.png": "scan"}
    assert all(d["pages"][0]["skip_reason"] for d in building["documents"])
    assert any("needs review" in w for w in building["warnings"])
    assert "Status: **needs_review**" in (out_dir / "report.md").read_text(encoding="utf-8")


def test_project_without_scale_source_needs_review(tmp_path):
    project = tmp_path / "noscale"
    project.mkdir()
    level = level_01_birinci()
    level.scale_text = ""
    write_pdf([{"level": level, "title_raw": level.title_raw, "page_class": "floor_plan", "openings": level.openings,
                "furniture": [], "dimensions": []}], project / "kat.pdf", "kat.pdf")
    building = build_project(project, tmp_path / "out")
    assert building["status"] == "needs_review"
    assert any("no scale source" in w for w in building["warnings"])
    assert building["levels"] == [] and building["documents"][0]["pages"][0]["scale"] is None
    B.validate(building)


def test_unclosed_outer_walls_need_review(tmp_path):
    project = tmp_path / "open"
    project.mkdir()
    doc = ezdxf.readfile(str(PROJECTS / "synthetic-01" / "zemin_kat.dxf"))
    msp = doc.modelspace()
    walls = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "DUVAR"]
    msp.delete_entity(walls[2])   # the top outer wall
    doc.saveas(project / "zemin_kat.dxf")
    building = build_project(project, tmp_path / "out")
    assert building["status"] == "needs_review"
    # Salon and Yatak Odası are still enclosed; Mutfak, Hol and Banyo are open to the outside.
    assert any("walls do not close" in w and "'MUTFAK'" in w for w in building["warnings"])
    assert len(building["walls"]) == 7 and sorted(r["label"] for r in building["rooms"]) == ["Salon", "Yatak Odası"]
    B.validate(building)
    # Without the left wall as well, only Yatak Odası stays enclosed.
    msp.delete_entity(walls[3])
    doc.saveas(project / "zemin_kat.dxf")
    building = build_project(project, tmp_path / "out2")
    assert building["status"] == "needs_review"
    assert [r["label"] for r in building["rooms"]] == ["Yatak Odası"]
    assert any("walls do not close" in w and "'SALON 24,50 m²'" in w for w in building["warnings"])


def test_open_outer_wall_without_labels_needs_review(tmp_path):
    """The closure check must not depend on a label sitting in the open area."""
    project = tmp_path / "open"
    project.mkdir()
    doc = ezdxf.readfile(str(PROJECTS / "synthetic-01" / "zemin_kat.dxf"))
    msp = doc.modelspace()
    walls = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "DUVAR"]
    msp.delete_entity(walls[2])   # the top outer wall: Mutfak, Hol and Banyo open to the outside
    for text in list(msp.query("TEXT")):
        if text.dxf.text in ("MUTFAK", "HOL", "BANYO"):
            msp.delete_entity(text)
    doc.saveas(project / "zemin_kat.dxf")
    building = build_project(project, tmp_path / "out")
    assert building["status"] == "needs_review"
    assert any("needs review" in w and "closed loop" in w for w in building["warnings"])
    assert "Status: **needs_review**" in (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    # The enclosed rooms are still reported for the reviewer.
    assert sorted(r["label"] for r in building["rooms"]) == ["Salon", "Yatak Odası"]
    B.validate(building)


def test_detached_wall_rectangle_does_not_crash_outline_check(tmp_path):
    """A wall group that touches nothing makes the union a MultiPolygon; the
    project must end as needs_review with its files written, not with a traceback."""
    project = tmp_path / "detached"
    project.mkdir()
    shutil.copy(PROJECTS / "synthetic-01" / "1_kat.pdf", project / "1_kat.pdf")
    doc = ezdxf.readfile(str(PROJECTS / "synthetic-01" / "zemin_kat.dxf"))
    doc.modelspace().add_lwpolyline([(20000, 20000), (22000, 20000), (22000, 20250), (20000, 20250)], close=True,
                                    dxfattribs={"layer": "DUVAR"})
    doc.saveas(project / "zemin_kat.dxf")
    out = tmp_path / "out"
    building = build_project(project, out)
    assert building["status"] == "needs_review"
    assert (out / "building.json").is_file() and (out / "report.md").is_file()
    assert any("needs review" in w and "L0" in w and "closed loop" in w for w in building["warnings"])
    assert any("outline check skipped" in w and "L0" in w for w in building["warnings"])
    assert [lv["id"] for lv in building["levels"]] == ["L0", "L1"]
    assert not [c for c in building["conflicts"] if c["kind"] == "outline_mismatch"]
    B.validate(building)


def test_cli(tmp_path):
    assert main([str(PROJECTS / "synthetic-01"), "--out", str(tmp_path / "o")]) == 0
    assert (tmp_path / "o" / "building.json").is_file() and (tmp_path / "o" / "report.md").is_file()
    assert main([str(PROJECTS / "synthetic-02"), "--out", str(tmp_path / "o2")]) == 1


def test_outline_mismatch_is_a_conflict(tmp_path):
    """Two levels with different footprints -> outline_mismatch conflict, status stays ok."""
    from wenart.synthetic.model import LevelBuilder
    project = tmp_path / "outline"
    project.mkdir()
    small = LevelBuilder("1. KAT PLANI", 8.0, 6.0)
    small.label("SALON", (1.0, 1.0))
    small.door(0, (4.0, 0.125), 90, "SALON")
    small.dimension_chain("bottom", [0.0, 8.0])
    l1 = small.build()
    shutil.copy(PROJECTS / "synthetic-01" / "zemin_kat.dxf", project / "zemin_kat.dxf")
    write_pdf([{"level": l1, "title_raw": l1.title_raw, "page_class": "floor_plan", "openings": l1.openings,
                "furniture": [], "dimensions": l1.dimensions}], project / "1_kat.pdf", "1_kat.pdf")
    building = build_project(project, tmp_path / "out")
    assert building["status"] == "ok"
    kinds = [c["kind"] for c in building["conflicts"]]
    assert kinds == ["outline_mismatch"]
    assert sorted(building["conflicts"][0]["element_ids"]) == ["L0", "L1"]
    assert G.polygon_area(next(r for r in building["rooms"] if r["level_id"] == "L1")["polygon"]) == pytest.approx(7.5 * 5.5, abs=0.01)


# --------------------------------------------------------------------------
# Several documents of one level
# --------------------------------------------------------------------------

def furnished_room_labels(building, level_id="L0"):
    return sorted(r["label"] for r in building["rooms"] if r["level_id"] == level_id and r["has_documented_furniture"])


def test_pdf_furniture_plan_furnishes_level_when_dxf_floor_plan_has_none(tmp_path):
    """DXF floor plan without furniture + PDF furniture plan of the same level:
    the furniture plan is the furniture source, nothing is dropped, no conflict."""
    project = tmp_path / "p"
    level = level_01_zemin()
    write_level_dxf(project, level, "zemin_kat.dxf", furniture=[])
    write_level_pdf(project, level, "mobilya.pdf", title_raw=FURNITURE_PLAN_TITLE, page_class="furniture_plan",
                    dimensions=[])
    building = build_project(project, tmp_path / "out")
    assert building["status"] == "ok"
    assert all(w["evidence"][0]["file"] == "zemin_kat.dxf" for w in building["walls"])
    assert len(building["furniture"]) == len(level.furniture) == 13
    truth = load_truth("synthetic-01")
    assert_one_to_one(building["furniture"], [f for f in truth["furniture"] if f["level_id"] == "L0"],
                      lambda f, t: furniture_matches(None, f["footprint"]["center"], f["footprint"]["size"],
                                                     f["footprint"]["rotation_deg"], t, check_type=False), "furniture")
    for piece in building["furniture"]:
        # Vector PDF footprints carry no block name: type unknown, hence unverified, but kept.
        assert piece["type"] == "unknown" and piece["status"] == "unverified" and piece["source"] == "from_documents"
        assert [(e["file"], e["page"]) for e in piece["evidence"]] == [("mobilya.pdf", 1)]
        assert piece["room_id"] is not None
    assert furnished_room_labels(building) == ["Banyo", "Salon", "Yatak Odası"]
    assert [c["kind"] for c in building["conflicts"]] == []
    assert building["unverified"] == [f["id"] for f in building["furniture"]]
    B.validate(building)


def test_dxf_furniture_plan_furnishes_level_when_dxf_floor_plan_has_none(tmp_path):
    """DXF floor plan without furniture + DXF furniture plan: the pieces come
    from the furniture plan with their block types, verified, no conflict."""
    project = tmp_path / "p"
    level = level_01_zemin()
    write_level_dxf(project, level, "zemin_kat.dxf", furniture=[])
    write_level_dxf(project, level, "mobilya_plani.dxf", title_raw=FURNITURE_PLAN_TITLE, page_class="furniture_plan",
                    dimensions=[])
    building = build_project(project, tmp_path / "out")
    assert building["status"] == "ok"
    assert all(w["evidence"][0]["file"] == "zemin_kat.dxf" and len(w["evidence"]) == 2 for w in building["walls"])
    truth = load_truth("synthetic-01")
    assert_one_to_one(building["furniture"], [f for f in truth["furniture"] if f["level_id"] == "L0"],
                      lambda f, t: furniture_matches(f["type"], f["footprint"]["center"], f["footprint"]["size"],
                                                     f["footprint"]["rotation_deg"], t), "furniture")
    for piece in building["furniture"]:
        assert piece["status"] == "verified" and piece["source"] == "from_documents"
        assert [e["file"] for e in piece["evidence"]] == ["mobilya_plani.dxf"]
    assert furnished_room_labels(building) == ["Banyo", "Salon", "Yatak Odası"]
    assert building["conflicts"] == [] and building["unverified"] == []
    B.validate(building)


def test_secondary_floor_plan_with_extra_elements_adds_them_unverified(tmp_path):
    """The DXF master lacks a window and a furniture piece the PDF floor plan
    draws: both are added as unverified with a count_mismatch conflict each."""
    project = tmp_path / "p"
    level = level_01_zemin()
    windows = level.windows()
    write_level_dxf(project, level, "zemin_kat.dxf", openings=[o for o in level.openings if o is not windows[0]],
                    furniture=level.furniture[1:])
    write_level_pdf(project, level, "zemin.pdf")
    building = build_project(project, tmp_path / "out")
    assert building["status"] == "ok"
    assert len(building["openings"]) == len(level.openings) == 11
    assert len(building["furniture"]) == len(level.furniture) == 13
    extra_window = next(o for o in building["openings"] if o["type"] == "window" and o["status"] == "unverified")
    assert G.distance(extra_window["center"], windows[0].center) <= 0.01
    assert [e["file"] for e in extra_window["evidence"]] == ["zemin.pdf"]
    extra_piece = next(f for f in building["furniture"] if f["status"] == "unverified")
    assert G.distance(extra_piece["footprint"]["center"], level.furniture[0].center) <= 0.01
    assert [e["file"] for e in extra_piece["evidence"]] == ["zemin.pdf"] and extra_piece["room_id"] == "r_L0_salon"
    assert building["unverified"] == [extra_window["id"], extra_piece["id"]]
    conflicts = {c["element_ids"][0]: c for c in building["conflicts"]}
    assert set(conflicts) == {extra_window["id"], extra_piece["id"]}
    assert all(c["kind"] == "count_mismatch" and "1 extra from vector PDF added as unverified" in c["resolution"]
               for c in conflicts.values())
    assert "zemin_kat.dxf has 5 windows, zemin.pdf p1 has 6" in conflicts[extra_window["id"]]["description"]
    assert "zemin_kat.dxf has 12 furniture pieces, zemin.pdf p1 has 13" in conflicts[extra_piece["id"]]["description"]
    for piece in building["furniture"]:
        if piece is not extra_piece:
            assert piece["status"] == "verified" and [e["file"] for e in piece["evidence"]] == ["zemin_kat.dxf", "zemin.pdf"]
    B.validate(building)


def test_furniture_footprint_or_rotation_disagreement_is_a_conflict(tmp_path):
    """A second document that draws a piece with another size or facing the
    other way must not confirm the master: unverified + conflict, master kept."""
    project = tmp_path / "p"
    level = level_01_zemin()
    altered = []
    for piece in level.furniture:
        if piece.block == "YATAK_CIFT":
            altered.append(Furniture(piece.block, piece.center, 180.0))              # turned around
        elif piece.block == "SEHPA":
            altered.append(Furniture(piece.block, piece.center, piece.rotation_deg, size=(1.2, 0.6)))  # 20 cm longer
        else:
            altered.append(piece)
    write_level_dxf(project, level, "zemin_kat.dxf")
    write_level_pdf(project, level, "zemin.pdf", furniture=altered)
    building = build_project(project, tmp_path / "out")
    assert building["status"] == "ok"
    assert len(building["furniture"]) == 13
    by_type = {f["type"]: f for f in building["furniture"]}
    bed, table = by_type["bed_double"], by_type["table_coffee"]
    assert bed["footprint"]["rotation_deg"] == 0.0 and bed["front_deg"] == 270.0      # master (DXF) kept
    assert table["footprint"]["size"] == [1.0, 0.6]
    for piece in (bed, table):
        assert piece["status"] == "unverified"
        assert [e["file"] for e in piece["evidence"]] == ["zemin_kat.dxf", "zemin.pdf"]
    assert sorted(building["unverified"]) == sorted([bed["id"], table["id"]])
    others = [f for f in building["furniture"] if f["id"] not in (bed["id"], table["id"])]
    assert all(f["status"] == "verified" and len(f["evidence"]) == 2 for f in others)
    conflicts = {c["element_ids"][0]: c for c in building["conflicts"]}
    assert set(conflicts) == {bed["id"], table["id"]}
    for c in conflicts.values():
        assert c["kind"] == "type_disagreement" and "DXF wins over vector PDF" in c["resolution"]
        assert "zemin_kat.dxf" in c["description"] and "zemin.pdf p1" in c["description"]
    assert "rotation" in conflicts[bed["id"]]["description"]
    assert "1.20 x 0.60" in conflicts[table["id"]]["description"] and "1.00 x 0.60" in conflicts[table["id"]]["description"]
    B.validate(building)


def test_room_label_disagreement_is_a_conflict(tmp_path):
    """Two documents label the same room differently: master wins, the room is
    unverified and a type_disagreement conflict is recorded."""
    project = tmp_path / "p"
    level = level_01_zemin()
    write_level_dxf(project, level, "zemin_kat.dxf")
    mutfak = next(lab for lab in level.labels if lab.label_raw == "MUTFAK")
    mutfak.label_raw = "YEMEK ODASI"
    write_level_pdf(project, level, "zemin.pdf", furniture=[])
    building = build_project(project, tmp_path / "out")
    assert building["status"] == "ok"
    room = next(r for r in building["rooms"] if r["id"] == "r_L0_mutfak")
    assert room["label"] == "Mutfak" and room["room_type"] == "kitchen" and room["status"] == "unverified"
    assert [(e["file"], e["text"]) for e in room["evidence"] if e["method"] == "vector"] == [
        ("zemin_kat.dxf", "MUTFAK"), ("zemin.pdf", "YEMEK ODASI")]
    assert building["unverified"] == ["r_L0_mutfak"]
    conflicts = building["conflicts"]
    assert len(conflicts) == 1 and conflicts[0]["kind"] == "type_disagreement"
    assert conflicts[0]["element_ids"] == ["r_L0_mutfak"]
    assert "'Mutfak'" in conflicts[0]["description"] and "'Yemek Odası'" in conflicts[0]["description"]
    assert "DXF wins over vector PDF" in conflicts[0]["resolution"]
    assert all(r["status"] == "verified" for r in building["rooms"] if r["id"] != "r_L0_mutfak")
    B.validate(building)


def test_area_label_over_tolerance_marks_room_unverified(tmp_path):
    """Label vs computed area: 2.9 % stays verified, more than 3 % -> unverified."""
    truth_area = 24.50
    for label, expected in (("SALON 30,00 m²", "unverified"), ("SALON 25,20 m²", "verified")):
        level = level_01_zemin()
        level.labels[0].label_raw = label
        project = tmp_path / B.slugify(label)
        write_level_dxf(project, level, "zemin_kat.dxf")
        building = build_project(project, project / "out")
        assert building["status"] == "ok"
        salon = next(r for r in building["rooms"] if r["id"] == "r_L0_salon")
        assert salon["status"] == expected and salon["area_computed"] == pytest.approx(truth_area, abs=0.01)
        area = [c for c in building["conflicts"] if c["kind"] == "area_label_vs_computed"]
        assert len(area) == 1 and area[0]["element_ids"] == ["r_L0_salon"]
        if expected == "unverified":
            assert building["unverified"] == ["r_L0_salon"] and "over 3%" in area[0]["resolution"]
            assert "r_L0_salon" in (project / "out" / "report.md").read_text(encoding="utf-8").split("## Unverified")[1]
        else:
            assert building["unverified"] == [] and "within tolerance" in area[0]["resolution"]


def test_door_swing_side_through_thick_wall(tmp_path):
    """The swing probe must reach past the wall face whatever the thickness;
    a probe that lands in no room makes the door unverified, not silently None."""
    project = tmp_path / "thick"
    project.mkdir()
    doc = ezdxf.readfile(str(PROJECTS / "synthetic-01" / "zemin_kat.dxf"))
    msp = doc.modelspace()
    walls = [e for e in msp.query("LWPOLYLINE") if e.dxf.layer == "DUVAR"]
    # Wall 7 (Hol | Banyo, x = 7.00 m, 0.10 m thick) becomes 0.70 m thick.
    thick = walls[7]
    thick.set_points([(6650.0 if x < 7000 else 7350.0, y) for x, y in thick.get_points("xy")], format="xy")
    # A second door on the same wall whose swing side (local +Y at rotation 270
    # = +X) lands inside the top outer wall, i.e. in no room.
    msp.add_blockref("KAPI_80", (7000.0, 7000.0), dxfattribs={"layer": "KAPI", "rotation": 270.0})
    doc.saveas(project / "zemin_kat.dxf")
    building = build_project(project, tmp_path / "out")
    assert building["status"] == "ok"
    wall = next(w for w in building["walls"] if abs(w["start"][0] - 7.0) < 1e-6 and abs(w["end"][0] - 7.0) < 1e-6)
    assert wall["thickness"] == pytest.approx(0.70)
    banyo_door = next(o for o in building["openings"] if o["type"] == "door" and o["center"] == [7.0, 5.4])
    assert banyo_door["wall_id"] == wall["id"]
    assert banyo_door["swing_side"] == "r_L0_banyo" and banyo_door["status"] == "verified"
    lost_door = next(o for o in building["openings"] if o["type"] == "door" and o["center"] == [7.0, 7.0])
    assert lost_door["wall_id"] == wall["id"]
    assert lost_door["swing_side"] is None and lost_door["status"] == "unverified"
    assert any(lost_door["id"] in w and "swing" in w for w in building["warnings"])
    assert building["unverified"] == [lost_door["id"]]
    # Every other door still opens into its room.
    truth = {tuple(o["center"]): o for o in load_truth("synthetic-01")["openings"] if o["type"] == "door"}
    for door in building["openings"]:
        if door["type"] == "door" and door["id"] not in (banyo_door["id"], lost_door["id"]):
            assert door["swing_side"] == truth[tuple(door["center"])]["swing_side"]
    B.validate(building)
