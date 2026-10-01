"""DXF extraction (wenart/ingest/dxf_extract.py) against the synthetic truth."""
import ezdxf
import pytest

from wenart import geometry as G
from wenart.ingest.dxf_extract import extract_dxf, metres_per_unit_from_insunits
from wenart.synthetic import blocks

from conftest import PROJECTS, assert_one_to_one, furniture_matches, load_pages, load_truth, opening_matches, wall_matches

CASES = [("synthetic-01", "zemin_kat.dxf", "L0"), ("synthetic-03", "mobilya_plani.dxf", "L0")]


@pytest.fixture(scope="module", params=CASES, ids=[c[1] for c in CASES])
def case(request):
    name, file, level_id = request.param
    ex = extract_dxf(PROJECTS / name / file, level_id, file)
    truth = load_truth(name)
    page = next(p for p in load_pages(name) if p["file"] == file)
    return ex, truth, page, file, level_id


def level_elements(truth, key, level_id):
    return [e for e in truth[key] if e["level_id"] == level_id]


def test_scale_and_transform(case):
    ex, truth, page, file, level_id = case
    assert ex.scale["method"] == "dxf_insunits" and ex.scale["metres_per_unit"] == 0.001
    assert ex.scale["evidence"]["entity"] == "$INSUNITS=4"
    doc_page = next(d for d in truth["documents"] if d["file"] == file)["pages"][0]
    assert ex.transform_to_building == pytest.approx(doc_page["transform_to_building"])
    assert ex.title.text == page["level_label_raw"] and ex.scale_text.text == "ÖLÇEK 1/100"
    assert ex.warnings == []


def test_walls(case):
    ex, truth, page, file, level_id = case
    walls = level_elements(truth, "walls", level_id)
    assert_one_to_one(ex.walls, walls, lambda w, t: wall_matches(w.start, w.end, w.thickness, t), "walls")
    for wall in ex.walls:
        hit = next(t for t in walls if wall_matches(wall.start, wall.end, wall.thickness, t))
        truth_ev = next(e for e in hit["evidence"] if e["file"] == file)
        assert wall.evidence["entity"] == truth_ev["entity"] and wall.evidence["layer"] == "DUVAR"
        assert wall.evidence["method"] == "vector" and wall.evidence["confidence"] == 1.0


def test_openings(case):
    ex, truth, page, file, level_id = case
    openings = level_elements(truth, "openings", level_id)
    assert_one_to_one(ex.openings, openings, lambda o, t: opening_matches(o.kind, o.center, o.width, t), "openings")
    rooms = level_elements(truth, "rooms", level_id)
    for opening in ex.openings:
        hit = next(t for t in openings if opening_matches(opening.kind, opening.center, opening.width, t))
        truth_ev = next(e for e in hit["evidence"] if e["file"] == file)
        assert opening.evidence["entity"] == truth_ev["entity"] and opening.evidence["block"] == truth_ev["block"]
        assert opening.status == "verified" and opening.block == truth_ev["block"]
        symbol = next(s for s in page["symbols"] if s["id"] == hit["id"])
        assert G.angle_difference_deg(opening.rotation_deg, symbol["rotation_deg"]) < 1e-6
        assert G.box_iou(opening.box, symbol["box"]) > 0.95
        if opening.kind == "door":
            room = next(r for r in rooms if r["id"] == hit["swing_side"])
            assert G.point_in_polygon(opening.swing_point, room["polygon"])
        else:
            assert opening.swing_point is None


def test_furniture(case):
    ex, truth, page, file, level_id = case
    furniture = level_elements(truth, "furniture", level_id)
    assert_one_to_one(ex.furniture, furniture,
                      lambda f, t: furniture_matches(f.type, f.center, f.size, f.rotation_deg, t), "furniture")
    for piece in ex.furniture:
        hit = next(t for t in furniture if furniture_matches(piece.type, piece.center, piece.size, piece.rotation_deg, t))
        assert piece.type_raw == hit["type_raw"] and piece.status == hit["status"]
        assert piece.front_deg == hit["front_deg"]
        assert piece.evidence["entity"] == next(e for e in hit["evidence"] if e["file"] == file)["entity"]
        assert piece.type == blocks.furniture_type(piece.type_raw)


def test_unknown_block_is_unverified():
    ex = extract_dxf(PROJECTS / "synthetic-03" / "mobilya_plani.dxf", "L0", "mobilya_plani.dxf")
    unknown = [f for f in ex.furniture if f.type == "unknown"]
    assert len(unknown) == 1
    piece = unknown[0]
    assert piece.type_raw == "BLOK_A" and piece.status == "unverified" and piece.front_deg is None
    assert piece.size == (1.2, 0.5) and piece.rotation_deg == 90.0


def test_labels_and_dimensions(case):
    ex, truth, page, file, level_id = case
    rooms = level_elements(truth, "rooms", level_id)
    assert sorted(t.text for t in ex.labels) == sorted(r["label_raw"] for r in rooms)
    for label in ex.labels:
        room = next(r for r in rooms if r["label_raw"] == label.text and
                    G.point_in_polygon((label.start[0] / 1000, label.start[1] / 1000), r["polygon"]))
        assert label.evidence["entity"] == next(e for e in room["evidence"] if e["file"] == file)["entity"]
    assert len(ex.dimensions) == len(page["dimensions"])
    assert sorted(d.printed for d in ex.dimensions) == sorted(d["printed"] for d in page["dimensions"])
    for dim in ex.dimensions:
        rec = next(d for d in page["dimensions"] if d["entity"] == dim.entity)
        assert abs(dim.measured - rec["measured"]) < 1e-6
        assert dim.printed_value == float(rec["printed"].replace(",", "."))
        assert dim.evidence["layer"] == "OLCU"


def test_insunits_codes():
    assert metres_per_unit_from_insunits(4) == 0.001
    assert metres_per_unit_from_insunits(6) == 1.0
    assert metres_per_unit_from_insunits(5) == 0.01
    assert metres_per_unit_from_insunits(1) == pytest.approx(0.0254)
    assert metres_per_unit_from_insunits(0) is None
    assert metres_per_unit_from_insunits(99) is None


def test_dxf_without_units_has_no_scale(tmp_path):
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 0
    doc.layers.add("DUVAR")
    doc.modelspace().add_lwpolyline([(0, 0), (5000, 0), (5000, 250), (0, 250)], close=True, dxfattribs={"layer": "DUVAR"})
    path = tmp_path / "nounits.dxf"
    doc.saveas(path)
    ex = extract_dxf(path, "L0", "nounits.dxf")
    assert ex.scale is None and ex.transform_to_building is None and ex.walls == []
    assert any("no unit" in w for w in ex.warnings)


def test_unknown_opening_block_and_bad_wall(tmp_path):
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    for layer in ("DUVAR", "KAPI"):
        doc.layers.add(layer)
    blk = doc.blocks.new("KAPI_OZEL")
    blk.add_line((-350, 0), (-350, 700))
    blk.add_line((-350, 0), (350, 0))
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (5000, 0), (5000, 250), (0, 250)], close=True, dxfattribs={"layer": "DUVAR"})
    msp.add_lwpolyline([(0, 0), (5000, 0), (5000, 250), (2500, 400), (0, 250)], close=True, dxfattribs={"layer": "DUVAR"})
    msp.add_blockref("KAPI_OZEL", (2500, 125), dxfattribs={"layer": "KAPI"})
    path = tmp_path / "odd.dxf"
    doc.saveas(path)
    ex = extract_dxf(path, "L0", "odd.dxf")
    assert len(ex.walls) == 1 and any("5 corners" in w for w in ex.warnings)
    assert len(ex.openings) == 1
    door = ex.openings[0]
    assert door.kind == "door" and door.status == "unverified" and door.width == pytest.approx(0.7)
    assert door.center == (2.5, 0.125)
