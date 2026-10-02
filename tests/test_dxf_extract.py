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


def _dxf_with_furniture_block(path, name: str, rect_mm):
    """One wall plus one MOBILYA insert of block ``name``; ``rect_mm`` = (width, depth) of the
    rectangle drawn inside the block, or None for a block without any geometry."""
    doc = ezdxf.new("R2010")
    doc.header["$INSUNITS"] = 4
    for layer in ("DUVAR", "MOBILYA"):
        doc.layers.add(layer)
    blk = doc.blocks.new(name)
    if rect_mm is not None:
        w, d = rect_mm
        blk.add_lwpolyline([(-w / 2, -d / 2), (w / 2, -d / 2), (w / 2, d / 2), (-w / 2, d / 2)], close=True)
        blk.add_line((-w / 4, -d / 2 + 50), (w / 4, -d / 2 + 50))
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (6000, 0), (6000, 250), (0, 250)], close=True, dxfattribs={"layer": "DUVAR"})
    insert = msp.add_blockref(name, (3000, 2000), dxfattribs={"layer": "MOBILYA"})
    doc.saveas(path)
    return f"INSERT:{insert.dxf.handle}"


def test_known_block_drawn_larger_keeps_drawn_size_and_is_unverified(tmp_path):
    # KANEPE_3LU is 2.2 x 0.9 m in the block table; here it is drawn 1.3 times larger.
    entity = _dxf_with_furniture_block(tmp_path / "big.dxf", "KANEPE_3LU", (2860, 1170))
    ex = extract_dxf(tmp_path / "big.dxf", "L0", "big.dxf")
    assert len(ex.furniture) == 1
    piece = ex.furniture[0]
    assert piece.type == "sofa" and piece.type_raw == "KANEPE_3LU"
    assert piece.size == pytest.approx((2.86, 1.17))          # the drawn rectangle is the footprint
    assert piece.center == (3.0, 2.0) and piece.status == "unverified" and piece.front_deg is None
    assert piece.box == pytest.approx([1570.0, 1415.0, 4430.0, 2585.0])
    assert len(ex.conflicts) == 1
    conflict = ex.conflicts[0]
    assert conflict["kind"] == "type_disagreement" and conflict["element_ids"] == []
    assert entity in conflict["description"] and "KANEPE_3LU" in conflict["description"]
    assert "2.86 x 1.17" in conflict["description"] and "2.20 x 0.90" in conflict["description"]
    assert "drawn" in conflict["resolution"] and "unverified" in conflict["resolution"]


def test_known_block_drawn_at_table_size_stays_verified(tmp_path):
    _dxf_with_furniture_block(tmp_path / "ok.dxf", "KANEPE_3LU", (2200, 900))
    ex = extract_dxf(tmp_path / "ok.dxf", "L0", "ok.dxf")
    piece = ex.furniture[0]
    assert piece.size == (2.2, 0.9) and piece.status == "verified" and piece.front_deg == 270.0
    assert ex.conflicts == [] and ex.warnings == []


def test_known_block_without_geometry_uses_table_size_but_is_unverified(tmp_path):
    entity = _dxf_with_furniture_block(tmp_path / "empty.dxf", "DOLAP", None)
    ex = extract_dxf(tmp_path / "empty.dxf", "L0", "empty.dxf")
    piece = ex.furniture[0]
    assert piece.type == "wardrobe" and piece.size == (1.8, 0.6) and piece.status == "unverified"
    assert ex.conflicts == []
    assert any(entity in w and "no drawn footprint" in w for w in ex.warnings)


def test_rotated_and_aligned_dimensions_measure_like_cad(tmp_path):
    from wenart.synthetic.dxf_writer import DIMSTYLE, DIMSTYLE_ATTRIBS

    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4
    for layer in ("DUVAR", "OLCU"):
        doc.layers.add(layer)
    doc.dimstyles.new(DIMSTYLE, dxfattribs=DIMSTYLE_ATTRIBS)
    msp = doc.modelspace()
    msp.add_lwpolyline([(0, 0), (5300, 0), (5300, 250), (0, 250)], close=True, dxfattribs={"layer": "DUVAR"})
    dim_attribs = {"layer": "OLCU"}
    # Horizontal (rotated) dimension from the wall corner to a point on another face: CAD prints the
    # projection onto the dimension direction (5300), not the distance of the definition points (5393.5).
    rotated = msp.add_linear_dim(base=(0, -600), p1=(0, 0), p2=(5300, 1000), angle=0, dimstyle=DIMSTYLE,
                                 dxfattribs=dim_attribs)
    rotated.render()
    # Aligned dimension between diagonal points, as ezdxf writes it (dimtype 0 with the angle set).
    aligned = msp.add_aligned_dim(p1=(0, 250), p2=(3000, 4250), distance=300, dimstyle=DIMSTYLE, dxfattribs=dim_attribs)
    aligned.render()
    # A true aligned dimension (dimtype 1) as CAD programs write it: no rotation angle stored.
    cad_aligned = msp.add_aligned_dim(p1=(5300, 250), p2=(2300, 4250), distance=300, dimstyle=DIMSTYLE,
                                      dxfattribs=dim_attribs)
    cad_aligned.render()
    cad_aligned.dimension.dxf.dimtype = (cad_aligned.dimension.dxf.dimtype & ~15) | 1
    cad_aligned.dimension.dxf.discard("angle")
    path = tmp_path / "dims.dxf"
    doc.saveas(path)

    ex = extract_dxf(path, "L0", "dims.dxf")
    by_entity = {d.entity: d for d in ex.dimensions}
    assert len(by_entity) == 3

    rot = by_entity[f"DIMENSION:{rotated.dimension.dxf.handle}"]
    assert rot.printed == "5,30" and rot.printed_value == 5.3
    assert rot.measured == pytest.approx(5.30, abs=1e-6)
    # Span end points lie on the dimension line (y = -0.6 m), so wall linking sees a horizontal span.
    assert rot.p1 == pytest.approx((0.0, -0.6), abs=1e-6) and rot.p2 == pytest.approx((5.3, -0.6), abs=1e-6)

    ali = by_entity[f"DIMENSION:{aligned.dimension.dxf.handle}"]
    assert ali.printed == "5,00" and ali.measured == pytest.approx(5.0, abs=1e-6)
    # Span on the dimension line: 300 mm to the left of p1 -> p2 (direction (0.6, 0.8)).
    assert ali.p1 == pytest.approx((-0.24, 0.43), abs=1e-6) and ali.p2 == pytest.approx((2.76, 4.43), abs=1e-6)

    cad = by_entity[f"DIMENSION:{cad_aligned.dimension.dxf.handle}"]
    assert cad.printed == "5,00" and cad.measured == pytest.approx(5.0, abs=1e-6)
    assert cad.p1 == pytest.approx((5.3, 0.25), abs=1e-6) and cad.p2 == pytest.approx((2.3, 4.25), abs=1e-6)
