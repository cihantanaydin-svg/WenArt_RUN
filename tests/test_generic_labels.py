"""CPU tests for wenart.ingest.generic.labels: room-name runs, label blocks, vocabulary and size-label checks
(docs/milestone7.md §2.7.2, §2.7.3), on hand-made text runs and on real01's texts."""
from pathlib import Path

import pdfplumber
import pytest
import yaml
from shapely.geometry import Point, Polygon, box

from wenart.ingest.generic import labels as L
from wenart.ingest.generic.model import TextRun
from wenart.ingest.pdf_extract import merge_chars

ROOT = Path(__file__).resolve().parents[1]
REAL01 = ROOT / "projects" / "real01" / "real01.pdf"
REFERENCE = ROOT / "tests" / "fixtures" / "real01_reference.yaml"

H = 0.3   # line height of the hand-made runs (any unit)


def run(text, x, y, width=None, height=H, rotation=0.0, rid=None, source="vector", evidence=None):
    """A run whose box has its lower-left corner at (x, y) (unrotated text)."""
    width = width if width is not None else 0.6 * height * max(len(text), 1)
    return TextRun(id=rid or f"t:{text}:{x}:{y}", text=text, box=(x, y, x + width, y + height), height=height,
                   rotation_deg=rotation, source=source, evidence=list(evidence or []))


def stack(*texts, x=0.0, y=10.0, gap=0.06, height=H):
    """Runs stacked top to bottom, each starting at x, ``gap`` apart."""
    out = []
    for i, text in enumerate(texts):
        out.append(run(text, x, y - i * (height + gap), height=height))
    return out


# --------------------------------------------------------------------------
# Vocabulary
# --------------------------------------------------------------------------

@pytest.mark.parametrize("name, room_type, exterior", [
    ("Drawing Room", "living", False),
    ("Dining", "dining", False),
    ("Bed Room", "bedroom", False),
    ("Kitchen", "kitchen", False),
    ("Bath+ Toilet", "bathroom", False),
    ("Toilet", "wc", False),
    ("Lobby", "hall", False),
    ("Balcony", "balcony", False),
    ("Store", "storage", False),
    ("Pooja", "prayer", False),
    ("Study", "other", False),
    ("SALON", "living", False),
    ("Banyo/WC", "wc", False),
    # §2.7.2 exterior row: site areas, not rooms
    ("Parking", "other", True),
    ("Car Porch", "other", True),
    ("PORCH", "other", True),
    ("Garden", "other", True),
    ("Lawn", "other", True),
    ("Sit Out", "other", True),
    ("Sit-out", "other", True),
    ("Setback", "other", True),
    ("OTLA", "other", True),
    ("Court", "other", True),
    ("Courtyard", "other", True),
    ("Drive", "other", True),
    ("Driveway", "other", True),
    ("Gate", "other", True),
    # a room keyword wins over a site word
    ("Terrace Garden", "balcony", False),
    ("Garden Store", "storage", False),
])
def test_room_type_for_with_exterior_flag(name, room_type, exterior):
    assert L.room_type_for(name) == (room_type, exterior)


def test_room_type_for_hall_uses_the_face():
    assert L.room_type_for("HALL") == ("hall", False)
    assert L.room_type_for("HALL", face_area_m2=15.0, face_aspect=1.2) == ("living", False)
    assert L.room_type_for("HALL", face_area_m2=15.0, face_aspect=4.0) == ("hall", False)


def test_room_name_runs_counts_indoor_names_only():
    runs = [run("Bed Room", 0, 0), run("Toilet", 0, 5), run("SALON 24,50 m²", 0, 10), run("Parking", 0, 15),
            run("50'", 0, 20), run("11' x 10'", 0, 25), run("UP", 0, 30), run("ZEMİN KAT PLANI", 0, 35),
            run("ÖLÇEK 1/100", 0, 40), run("BEDROOM 3,20 x 4,10", 0, 45),
            run("ALL KITCHEN COUNTERS ARE 600 MM DEEP UNLESS NOTED", 0, 50), run("", 0, 55)]
    assert [r.text for r in L.room_name_runs(runs)] == ["Bed Room", "Toilet", "SALON 24,50 m²",
                                                        "BEDROOM 3,20 x 4,10"]


def test_page_language():
    assert not L.page_is_turkish([run("Bed Room", 0, 0), run("Kitchen", 0, 5), run("SALON", 0, 10)])
    assert L.page_is_turkish([run("YATAK ODASI", 0, 0), run("MUTFAK", 0, 5), run("WC", 0, 10)])
    assert L.page_is_turkish([run("ÖLÇEK 1/100", 0, 0)]) and not L.page_is_turkish([run("50'", 0, 0)])


# --------------------------------------------------------------------------
# Label blocks
# --------------------------------------------------------------------------

def test_bath_plus_toilet_with_size_line():
    blocks = L.merge_label_blocks(stack("Bath+", "Toilet", "7' x 5'"), file_rel="p.pdf", page=1)
    assert len(blocks) == 1
    b = blocks[0]
    assert b.name == "Bath+ Toilet" and b.room_type == "bathroom" and not b.exterior
    assert b.size_text == "7' x 5'" and b.area_text is None
    assert [round(v.metres, 4) for v in b.size] == [2.1336, 1.524]
    assert [r.text for r in b.name_runs] == ["Bath+", "Toilet"]
    assert [r.text for r in b.runs] == ["Bath+", "Toilet", "7' x 5'"]
    # Anchor = centre of the two name lines (not of the whole block).
    top, bottom = b.name_runs[0].box, b.name_runs[1].box
    assert b.anchor == pytest.approx(((min(top[0], bottom[0]) + max(top[2], bottom[2])) / 2,
                                      (bottom[1] + top[3]) / 2))
    assert len(b.evidence) == 3
    assert all(e["file"] == "p.pdf" and e["method"] == "vector" and e["page"] == 1 for e in b.evidence)
    assert [e["text"] for e in b.evidence] == ["Bath+", "Toilet", "7' x 5'"]


@pytest.mark.parametrize("texts, name, room_type", [
    (("Kitchen &", "Dining"), "Kitchen & Dining", "kitchen"),
    (("Living /", "Dining"), "Living / Dining", "living"),
    (("GUEST", "BED ROOM"), "GUEST BED ROOM", "bedroom"),
    (("MASTER", "BEDROOM", "14'-0\" X 12'-0\""), "MASTER BEDROOM", "bedroom"),
    (("BED-", "ROOM"), "BED-ROOM", "bedroom"),
    (("GYM", "12' x 10'"), "GYM", "other"),
])
def test_stacked_names_merge(texts, name, room_type):
    blocks = L.merge_label_blocks(stack(*texts))
    assert [(b.name, b.room_type) for b in blocks] == [(name, room_type)]


def test_connector_takes_a_line_a_little_further_away_or_to_the_right():
    far = [run("Kitchen &", 0, 10), run("Dining", 0, 10 - 1.4 * H)]          # gap 0.4 H: plain stacking
    assert [b.name for b in L.merge_label_blocks(far)] == ["Kitchen & Dining"]
    farther = [run("Kitchen &", 0, 10), run("Dining", 0, 10 - 2.2 * H)]      # gap 1.2 H: only via '&'
    assert [b.name for b in L.merge_label_blocks(farther)] == ["Kitchen & Dining"]
    plain = [run("Kitchen", 0, 10), run("Dining", 0, 10 - 2.2 * H)]          # no connector: two rooms
    assert sorted(b.name for b in L.merge_label_blocks(plain)) == ["Dining", "Kitchen"]
    side = [run("Bath+", 0, 10, width=1.0), run("Toilet", 1.1, 10, width=1.2)]
    assert [b.name for b in L.merge_label_blocks(side)] == ["Bath+ Toilet"]


def test_size_and_area_lines_end_a_block():
    runs = stack("Bed Room", "11' x 10'", "110 sq ft", "Toilet", "5' x 4'")
    blocks = L.merge_label_blocks(runs)
    assert [(b.name, b.size_text, b.area_text) for b in blocks] == [
        ("Bed Room", "11' x 10'", "110 sq ft"), ("Toilet", "5' x 4'", None)]
    assert blocks[0].area_m2 == pytest.approx(110 * 0.09290304)


def test_inline_area_and_size():
    blocks = L.merge_label_blocks([run("SALON 24,50 m²", 0, 0), run("BEDROOM 3,20 x 4,10", 20, 0)])
    by_name = {b.name: b for b in blocks}
    assert by_name["SALON"].area_text == "24,50 m²" and by_name["SALON"].area_m2 == 24.5
    assert by_name["SALON"].room_type == "living"
    assert by_name["BEDROOM"].size_text == "3,20 x 4,10"
    assert [v.metres for v in by_name["BEDROOM"].size] == [3.2, 4.1]


def test_non_labels_make_no_block():
    runs = [run("UP", 0, 0), run("N", 5, 0), run("D1", 10, 0), run("50'", 15, 0),
            run("11' x 10'", 20, 0),                     # a size line with no name above
            run("4,30", 25, 0), run("12", 30, 0)]
    assert L.merge_label_blocks(runs) == []


def test_lines_must_overlap_and_be_close():
    apart = [run("Bed Room", 0, 10), run("11' x 10'", 5, 10 - H - 0.06)]       # no horizontal overlap
    blocks = L.merge_label_blocks(apart)
    assert [(b.name, b.size_text) for b in blocks] == [("Bed Room", None)]
    far = [run("Bed Room", 0, 10), run("11' x 10'", 0, 10 - 2.5 * H)]          # gap 1.5 H
    assert [(b.name, b.size_text) for b in L.merge_label_blocks(far)] == [("Bed Room", None)]


def test_rotated_labels_stack_in_their_own_frame():
    # Text rotated 90 degrees (reading upwards): the next line lies to the right (+x) of the first.
    first = TextRun(id="a", text="Bed Room", box=(0.0, 0.0, 0.3, 2.4), height=0.3, rotation_deg=90.0)
    second = TextRun(id="b", text="11' x 10'", box=(0.36, 0.1, 0.66, 2.2), height=0.3, rotation_deg=90.0)
    blocks = L.merge_label_blocks([first, second])
    assert [(b.name, b.size_text) for b in blocks] == [("Bed Room", "11' x 10'")]
    # Mixed rotations never stack.
    upright = TextRun(id="c", text="11' x 10'", box=(0.36, 0.1, 2.4, 0.4), height=0.3, rotation_deg=0.0)
    assert [(b.name, b.size_text) for b in L.merge_label_blocks([first, upright])] == [("Bed Room", None)]


def test_evidence_of_ocr_runs_is_kept():
    ev = {"file": "scan.png", "method": "ocr", "confidence": 0.91, "model": "tesseract", "text": "KITCHEN"}
    blocks = L.merge_label_blocks([run("KITCHEN", 0, 0, source="ocr", evidence=[ev])], file_rel="scan.png")
    assert blocks[0].evidence == [ev]
    bare = L.merge_label_blocks([run("KITCHEN", 0, 0, source="ocr")], file_rel="scan.png")
    assert bare[0].evidence[0]["method"] == "ocr" and bare[0].evidence[0]["confidence"] == 0.5


def test_page_unit_system_decides_bare_size_pairs():
    imperial_page = stack("Bed Room", "11 x 10") + [run("50'", 50, 0), run("30'", 60, 0)]
    block = L.merge_label_blocks(imperial_page)[0]
    assert block.size[0].system == "imperial" and block.size[0].metres == pytest.approx(11 * 0.3048)
    metric_page = stack("YATAK ODASI", "11 x 10") + [run("4,30", 50, 0)]
    assert L.merge_label_blocks(metric_page)[0].size[0].metres == 11.0


# --------------------------------------------------------------------------
# real01 (vector texts read with pdfplumber)
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real01_runs():
    with pdfplumber.open(str(REAL01)) as pdf:
        items = merge_chars(pdf.pages[0].chars)
    return [TextRun(id=t.entity, text=t.text, box=tuple(t.box), height=t.height, rotation_deg=t.rotation_deg)
            for t in items]


@pytest.fixture(scope="module")
def reference():
    return yaml.safe_load(REFERENCE.read_text(encoding="utf-8"))


def _pt_to_ref_ft(p, ref):
    """PDF point (y up) -> reference feet (origin = the house's min corner, top 459.84 pt = y-up 135.16 pt)."""
    s = ref["scale"]["pt_per_ft"]
    return ((p[0] - 165.64) / s, (p[1] - (ref["source"]["page_size_pt"][1] - 459.84)) / s)


def test_real01_room_name_runs(real01_runs):
    assert [r.text for r in L.room_name_runs(real01_runs)] == [
        "Bed Room", "Bed Room", "Bath+", "Toilet", "Drawing Room", "Dining", "Kitchen", "Pooja", "Store"]
    assert not L.page_is_turkish(real01_runs)


def test_real01_label_blocks_match_the_reference(real01_runs, reference):
    blocks = L.merge_label_blocks(real01_runs, file_rel="projects/real01/real01.pdf", page=1)
    assert len(blocks) == 9
    rooms = [b for b in blocks if not b.exterior]
    assert len(rooms) == 8
    tol = reference["tolerances_default"]["room"]["label_anchor"]
    for ref_room in reference["rooms"]:
        anchor = ref_room["label_name_anchor_ft"]
        near = [b for b in rooms if abs(_pt_to_ref_ft(b.anchor, reference)[0] - anchor[0]) <= tol
                and abs(_pt_to_ref_ft(b.anchor, reference)[1] - anchor[1]) <= tol]
        assert len(near) == 1, ref_room["id"]
        b = near[0]
        assert b.name == ref_room["label"]
        assert b.size_text == ref_room["label_size_text"]
        assert b.room_type == ref_room["room_type"]
        assert [round(v.metres / 0.3048, 3) for v in b.size] == ref_room["label_size_ft"]
        assert b.evidence and all(e["method"] == "vector" for e in b.evidence)
    parking = [b for b in blocks if b.exterior]
    assert [(b.name, b.room_type, b.size_text) for b in parking] == [("Parking", "other", "11' 3\" x 15' 3\"")]


def test_real01_size_labels_against_the_reference_faces(real01_runs, reference):
    """Every room-size label of real01 is `ok` against the reference room boxes (§2.7.3)."""
    blocks = [b for b in L.merge_label_blocks(real01_runs) if not b.exterior]
    s = reference["scale"]["pt_per_ft"]
    y0 = reference["source"]["page_size_pt"][1] - 459.84
    for ref_room in reference["rooms"]:
        x_lo, y_lo, x_hi, y_hi = ref_room["bbox_ft"]
        face_pt = box(165.64 + x_lo * s, y0 + y_lo * s, 165.64 + x_hi * s, y0 + y_hi * s)
        block = [b for b in blocks if face_pt.contains(Point(b.anchor))]
        assert len(block) == 1, ref_room["id"]
        face_ft = box(x_lo, y_lo, x_hi, y_hi)
        face_m = Polygon([(x * 0.3048, y * 0.3048) for x, y in face_ft.exterior.coords])
        check = L.check_label_size(block[0], face_m)
        assert check["status"] == ref_room["label_size_check"] == "ok", ref_room["id"]
        assert check["text"] == ref_room["label_size_text"]
        assert max(abs(v) for v in check["off_pct"]) <= 3.2
        assert check["unverified"] is False


# --------------------------------------------------------------------------
# Size-label checks (§2.7.3)
# --------------------------------------------------------------------------

def _block(size_text):
    return L.merge_label_blocks(stack("Bed Room", size_text))[0]


def test_check_label_size_ok_in_both_orientations():
    block = _block("11' x 10'")
    for face in (box(0, 0, 3.353, 3.048), box(0, 0, 3.048, 3.353)):
        got = L.check_label_size(block, face)
        assert got["status"] == "ok" and got["measured"] == [3.353, 3.048]
        assert got["width_m"] == pytest.approx(3.3528) and got["length_m"] == pytest.approx(3.048)
        assert got["off_pct"] == [0.0, 0.0] and got["unverified"] is False


def test_check_label_size_tolerances():
    block = _block("4,00 x 3,00")
    assert L.check_label_size(block, box(0, 0, 4.19, 3.0))["status"] == "ok"        # 4.5 % < 5 %
    over = L.check_label_size(block, box(0, 0, 3.75, 3.0))                          # 6.7 % off
    assert over["status"] == "conflict" and over["unverified"] is False
    far = L.check_label_size(block, box(0, 0, 3.5, 3.0))                            # 14 % off
    assert far["status"] == "conflict" and far["unverified"] is True
    small = _block("1,20 x 1,00")                                                   # 0.15 m floor for small rooms
    assert L.check_label_size(small, box(0, 0, 1.34, 1.0))["status"] == "ok"
    assert L.check_label_size(small, box(0, 0, 1.40, 1.0))["status"] == "conflict"


def test_check_label_size_rotated_face_and_no_size():
    import shapely.affinity
    face = shapely.affinity.rotate(box(0, 0, 4.0, 3.0), 30, origin=(0, 0))
    assert L.check_label_size(_block("4,00 x 3,00"), face)["status"] == "ok"
    no_size = L.merge_label_blocks([run("Kitchen", 0, 0)])[0]
    assert L.check_label_size(no_size, face) is None


def test_check_label_size_unchecked_on_l_shaped_faces():
    # L-shaped face, area 12 m² in a 4 x 4 rectangle (0.75 < 0.9): sides not checked, area at 8 %.
    face = Polygon([(0, 0), (4, 0), (4, 2), (2, 2), (2, 4), (0, 4)])
    good = L.check_label_size(_block("4,00 x 3,00"), face)
    assert good["status"] == "unchecked" and good["off_pct"] == [0.0] and good["unverified"] is False
    assert good["area_m2"] == {"label": 12.0, "face": 12.0}
    bad = L.check_label_size(_block("4,00 x 3,50"), face)                           # 14 m² vs 12 m²: +16.7 %
    assert bad["status"] == "conflict" and bad["unverified"] is False
    worse = L.check_label_size(_block("4,00 x 4,00"), face)                         # +33 %
    assert worse["status"] == "conflict" and worse["unverified"] is True
