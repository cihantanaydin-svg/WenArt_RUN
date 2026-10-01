"""End-to-end vector path (wenart/ingest/pipeline.py) on the synthetic projects."""
import shutil

import ezdxf
import pytest

from wenart import building as B
from wenart import geometry as G
from wenart.ingest.pipeline import build_project, main
from wenart.synthetic.pdf_writer import write_pdf
from wenart.synthetic.projects import level_01_birinci

from conftest import (PROJECTS, assert_one_to_one, furniture_matches, load_truth, opening_matches, room_matches,
                      wall_matches)

NAMES = ["synthetic-01", "synthetic-02", "synthetic-03"]


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    out = tmp_path_factory.mktemp("outputs")
    result = {}
    for name in NAMES:
        result[name] = (build_project(PROJECTS / name, out / name), out / name)
    return result


def conflict_keys(conflicts):
    return sorted((c["kind"], tuple(sorted(c["element_ids"]))) for c in conflicts)


@pytest.mark.parametrize("name", ["synthetic-01", "synthetic-03"])
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
        assert any(e["method"] == "derived" for e in r["evidence"])
    truth_furniture = {f["id"]: f for f in truth["furniture"]}
    for f in building["furniture"]:
        t = truth_furniture[f["id"]]
        assert f["room_id"] == t["room_id"] and f["type_raw"] == t["type_raw"] and f["status"] == t["status"]
        assert f["source"] == "from_documents" and f["front_deg"] == t["front_deg"]


@pytest.mark.parametrize("name", ["synthetic-01", "synthetic-03"])
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
    report = (out_dir / "report.md").read_text(encoding="utf-8")
    for heading in ("## Documents", "## Levels", "## Rooms", "## Furniture", "## Conflicts", "## Unverified", "## Warnings"):
        assert heading in report
    assert "r_L0_salon" in report and "Status: **ok**" in report
    assert any("ceiling height assumed 2.70 m" in w for w in building["warnings"])
    assert building["project"]["brief"]["style"].startswith("Scandinavian")


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
