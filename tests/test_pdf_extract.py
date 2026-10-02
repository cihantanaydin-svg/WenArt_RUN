"""Vector PDF extraction (wenart/ingest/pdf_extract.py) against the synthetic truth."""
import pdfplumber
import pytest

from wenart import geometry as G
from wenart.ingest.model import METRES_PER_POINT
from wenart.ingest.pdf_extract import extract_pdf_page, merge_chars, read_page_objects
from wenart.synthetic.pdf_writer import write_pdf
from wenart.synthetic.projects import PageSpec, level_01_birinci, level_03_bodrum

from conftest import PROJECTS, assert_one_to_one, furniture_matches, load_pages, load_truth, opening_matches, wall_matches

CASES = [("synthetic-01", "1_kat.pdf", 1, "L1"), ("synthetic-03", "kat_planlari.pdf", 1, "L-1"),
         ("synthetic-03", "kat_planlari.pdf", 2, "L0"), ("synthetic-03", "kat_planlari.pdf", 3, "L1"),
         ("synthetic-02", "truth/plan.pdf", 1, "L0")]


@pytest.fixture(scope="module", params=CASES, ids=[f"{c[1]}-p{c[2]}" for c in CASES])
def case(request):
    name, file, number, level_id = request.param
    ex = extract_pdf_page(PROJECTS / name / file, number, level_id, file)
    truth = load_truth(name)
    page = next(p for p in load_pages(name) if p["file"] == file and p["page"] == number)
    return ex, truth, page, file, number, level_id


def level_elements(truth, key, level_id):
    return [e for e in truth[key] if e["level_id"] == level_id]


def truth_entity(element, file, number):
    """Entity of the truth evidence on this page (None for the hidden PDF of synthetic-02)."""
    ev = next((e for e in element["evidence"] if e["file"] == file and e.get("page") == number), None)
    return ev["entity"] if ev else None


def test_scale_title_transform(case):
    ex, truth, page, file, number, level_id = case
    assert ex.scale["method"] == "pdf_scale_text"
    assert ex.scale["metres_per_unit"] == pytest.approx(100 * METRES_PER_POINT)
    assert ex.scale["evidence"]["text"] == "ÖLÇEK 1/100" and ex.scale["evidence"]["page"] == number
    expected = G.invert_affine(page["transform"]["building_to_page"])
    assert ex.transform_to_building == pytest.approx(expected, abs=1e-6)
    assert ex.title.text == page["level_label_raw"] and ex.page_size == page["size"]
    assert ex.warnings == [] and ex.conflicts == []


def test_walls(case):
    ex, truth, page, file, number, level_id = case
    walls = level_elements(truth, "walls", level_id)
    assert_one_to_one(ex.walls, walls, lambda w, t: wall_matches(w.start, w.end, w.thickness, t), "walls")
    for wall in ex.walls:
        hit = next(t for t in walls if wall_matches(wall.start, wall.end, wall.thickness, t))
        entity = truth_entity(hit, file, number)
        assert entity is None or wall.evidence["entity"] == entity
        rec = next(r for r in page["walls"] if r["id"] == hit["id"])
        assert G.box_iou(wall.box, rec["box"]) > 0.95


def test_openings(case):
    ex, truth, page, file, number, level_id = case
    shown = {s["id"] for s in page["symbols"]}
    openings = [o for o in level_elements(truth, "openings", level_id) if o["id"] in shown]
    assert_one_to_one(ex.openings, openings, lambda o, t: opening_matches(o.kind, o.center, o.width, t), "openings")
    rooms = level_elements(truth, "rooms", level_id)
    for opening in ex.openings:
        hit = next(t for t in openings if opening_matches(opening.kind, opening.center, opening.width, t))
        entity = truth_entity(hit, file, number)
        assert entity is None or opening.evidence["entity"] == entity
        symbol = next(s for s in page["symbols"] if s["id"] == hit["id"])
        diff = G.angle_difference_deg(opening.rotation_deg, symbol["rotation_deg"])
        assert diff < 1.0 or (opening.kind == "window" and abs(diff - 180.0) < 1.0)
        assert G.box_iou(opening.box, symbol["box"]) > 0.9
        if opening.kind == "door":
            room = next(r for r in rooms if r["id"] == hit["swing_side"])
            assert G.point_in_polygon(opening.swing_point, room["polygon"])


def test_zemin_page_of_synthetic_03_lacks_one_window():
    ex = extract_pdf_page(PROJECTS / "synthetic-03" / "kat_planlari.pdf", 2, "L0", "kat_planlari.pdf")
    truth = load_truth("synthetic-03")
    assert len(ex.windows()) == 5 and len([o for o in truth["openings"] if o["level_id"] == "L0" and o["type"] == "window"]) == 6
    missing = next(c for c in truth["conflicts"] if c["kind"] == "count_mismatch")["element_ids"][0]
    win = next(o for o in truth["openings"] if o["id"] == missing)
    assert not any(opening_matches("window", w.center, w.width, win) for w in ex.windows())


def test_furniture_footprints(case):
    ex, truth, page, file, number, level_id = case
    furniture = level_elements(truth, "furniture", level_id) if page["symbols"] and any(
        s["type"] not in ("door", "window") for s in page["symbols"]) else []
    assert_one_to_one(ex.furniture, furniture,
                      lambda f, t: furniture_matches(f.type, f.center, f.size, f.rotation_deg, t, check_type=False),
                      "furniture")
    for piece in ex.furniture:
        # A PDF carries no block name: footprint only, type unknown and unverified.
        assert piece.type == "unknown" and piece.type_raw is None and piece.status == "unverified"
        hit = next(t for t in furniture if furniture_matches("unknown", piece.center, piece.size, piece.rotation_deg, t, False))
        assert piece.front_deg == pytest.approx(hit["front_deg"])


def test_dimensions(case):
    ex, truth, page, file, number, level_id = case
    assert len(ex.dimensions) == len(page["dimensions"])
    for dim in ex.dimensions:
        rec = next(d for d in page["dimensions"] if d["entity"] == dim.entity)
        assert dim.printed == rec["printed"] and abs(dim.measured - rec["measured"]) < 0.005
        assert dim.tick_count == 2 and dim.evidence["text"] == rec["printed"]
        assert dim.evidence["entity"] == rec["text_entity"]
        assert G.box_iou(dim.box, rec["box"]) > 0.5


def test_bodrum_dimension_override():
    ex = extract_pdf_page(PROJECTS / "synthetic-03" / "kat_planlari.pdf", 1, "L-1", "kat_planlari.pdf")
    bad = [d for d in ex.dimensions if abs(d.printed_value - d.measured) > 0.01]
    assert len(bad) == 1 and bad[0].printed == "3,99" and abs(bad[0].measured - 3.80) < 0.005
    # The median of the dimension ratios still agrees with the scale note.
    assert ex.scale["method"] == "pdf_scale_text"


def test_texts(case):
    ex, truth, page, file, number, level_id = case
    rooms = level_elements(truth, "rooms", level_id)
    assert sorted(t.text for t in ex.labels) == sorted(r["label_raw"] for r in rooms)
    for item in ex.texts:
        rec = next(t for t in page["texts"] if t["entity"] == item.entity)
        assert rec["text"] == item.text
        assert G.box_iou(item.box, rec["box"]) > 0.5
        assert item.role == rec["role"] or (rec["role"] == "room_label" and item.role == "room_label")


def test_merge_chars_keeps_rotation():
    with pdfplumber.open(str(PROJECTS / "synthetic-01" / "1_kat.pdf")) as pdf:
        runs = merge_chars(pdf.pages[0].chars)
    vertical = [r for r in runs if abs(r.rotation_deg - 90.0) < 1e-6]
    assert sorted(r.text for r in vertical) == ["3,00", "4,20", "7,20"]
    horizontal = [r for r in runs if r.rotation_deg == 0.0]
    assert "EBEVEYN YATAK ODASI" in {r.text for r in horizontal}
    assert all(r.entity.startswith("char:") for r in runs)


@pytest.fixture(scope="module")
def pdf_without_scale_note(tmp_path_factory):
    """A 1:100 plan with dimensions but no ÖLÇEK text, and one with neither."""
    out = tmp_path_factory.mktemp("noscale")
    level = level_01_birinci()
    level.scale_text = ""
    write_pdf([{"level": level, "title_raw": level.title_raw, "page_class": "floor_plan", "openings": level.openings,
                "furniture": [], "dimensions": level.dimensions}], out / "dims_only.pdf", "dims_only.pdf")
    write_pdf([{"level": level, "title_raw": level.title_raw, "page_class": "floor_plan", "openings": level.openings,
                "furniture": [], "dimensions": []}], out / "nothing.pdf", "nothing.pdf")
    return out


def test_scale_from_dimension_texts(pdf_without_scale_note):
    ex = extract_pdf_page(pdf_without_scale_note / "dims_only.pdf", 1, "L1", "dims_only.pdf")
    assert ex.scale["method"] == "dimension_text" and ex.scale["confidence"] == 0.9
    assert ex.scale["metres_per_unit"] == pytest.approx(100 * METRES_PER_POINT, rel=1e-4)
    assert ex.scale["evidence"]["entity"].startswith("char:")
    assert len(ex.walls) == 8


def test_no_scale_source(pdf_without_scale_note):
    ex = extract_pdf_page(pdf_without_scale_note / "nothing.pdf", 1, "L1", "nothing.pdf")
    assert ex.scale is None and ex.transform_to_building is None
    assert any("no scale source" in w for w in ex.warnings)


def test_read_page_objects_order_matches_stream():
    with pdfplumber.open(str(PROJECTS / "synthetic-03" / "kat_planlari.pdf")) as pdf:
        objects = read_page_objects(pdf.pages[0])
    assert objects.paths[0].kind == "rect" and objects.paths[0].linewidth == 1.0   # page border = path:0
    assert objects.paths[1].entity == "path:1" and objects.paths[1].linewidth == 0.5  # first wall
    assert objects.n_chars > 0 and objects.n_images == 0


@pytest.fixture(scope="module")
def bodrum_pages(tmp_path_factory):
    """Variants of the synthetic-03 Bodrum page, whose left chain prints 3,99 for a 3,80 segment.
    Returns ``(write, override, correct)``: ``write(name, dimensions, note)`` -> path of a one-page PDF."""
    out = tmp_path_factory.mktemp("bodrum")
    level = level_03_bodrum()

    def write(name: str, dimensions, note: bool = True):
        level.scale_text = "ÖLÇEK 1/100" if note else ""
        write_pdf([{"level": level, "title_raw": level.title_raw, "page_class": "floor_plan",
                    "openings": level.openings, "furniture": [], "dimensions": dimensions}], out / name, name)
        return out / name

    override = [d for d in level.dimensions if d.text_override]
    correct = [d for d in level.dimensions if not d.text_override]
    assert len(override) == 1 and override[0].text_override == "3,99" and len(correct) == 6
    return write, override, correct


def _scale_conflicts(ex):
    return [c for c in ex.conflicts if c["kind"] == "scale_disagreement"]


@pytest.mark.parametrize("n_correct", [0, 1])
def test_override_does_not_rescale_page_with_scale_note(bodrum_pages, n_correct):
    write, override, correct = bodrum_pages
    name = f"note_override_{n_correct}.pdf"
    ex = extract_pdf_page(write(name, override + correct[:n_correct]), 1, "L-1", name)
    # The scale note wins; the text override cannot move the page scale.
    assert ex.scale["method"] == "pdf_scale_text"
    assert ex.scale["metres_per_unit"] == pytest.approx(100 * METRES_PER_POINT)
    assert ex.scale["confidence"] < 0.9
    assert ex.scale["evidence"]["text"] == "ÖLÇEK 1/100"
    conflicts = _scale_conflicts(ex)
    assert len(conflicts) == 1 and len(ex.conflicts) == 1
    assert "scale note kept" in conflicts[0]["resolution"]
    assert "3,99" in conflicts[0]["description"] and "5.0%" in conflicts[0]["description"]
    # Geometry at the note's scale: the outer wall is 0.25 m thick and the override still measures 3,80.
    assert max(w.thickness for w in ex.walls) == pytest.approx(0.25, abs=0.002)
    bad = next(d for d in ex.dimensions if d.printed == "3,99")
    assert bad.measured == pytest.approx(3.80, abs=0.005)
    for dim in ex.dimensions:
        if dim.printed != "3,99":
            assert dim.measured == pytest.approx(dim.printed_value, abs=0.005)


def test_lone_or_split_dimension_texts_give_no_scale_without_note(bodrum_pages):
    write, override, correct = bodrum_pages
    ex = extract_pdf_page(write("lone.pdf", override, note=False), 1, "L-1", "lone.pdf")
    assert ex.scale is None and ex.transform_to_building is None
    assert any("dimension text" in w for w in ex.warnings)
    # Three ratios of which one disagrees: not enough agreement to trust the dimension texts.
    ex = extract_pdf_page(write("split.pdf", override + correct[:2], note=False), 1, "L-1", "split.pdf")
    assert ex.scale is None
    assert any("3,99" in w for w in ex.warnings)


def test_three_agreeing_dimension_texts_give_scale_without_note(bodrum_pages):
    write, override, correct = bodrum_pages
    ex = extract_pdf_page(write("three.pdf", correct[:3], note=False), 1, "L-1", "three.pdf")
    assert ex.scale["method"] == "dimension_text" and ex.scale["confidence"] == 0.9
    assert ex.scale["metres_per_unit"] == pytest.approx(100 * METRES_PER_POINT, rel=1e-4)
    assert ex.conflicts == [] and ex.warnings == []
    # A majority of agreeing texts still gives the scale, with lower confidence and the odd one named.
    ex = extract_pdf_page(write("majority.pdf", override + correct, note=False), 1, "L-1", "majority.pdf")
    assert ex.scale["method"] == "dimension_text" and ex.scale["confidence"] == 0.7
    assert ex.scale["metres_per_unit"] == pytest.approx(100 * METRES_PER_POINT, rel=1e-4)
    assert any("3,99" in w for w in ex.warnings)
    bad = next(d for d in ex.dimensions if d.printed == "3,99")
    assert bad.measured == pytest.approx(3.80, abs=0.005)
