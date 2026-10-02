"""CPU tests for wenart.building (IDs, label normalisation, schema validation)
and the wenart.geometry helpers both other milestone-2 modules import."""
import json
import math
from pathlib import Path

import jsonschema
import pytest

from wenart import building as B
from wenart import geometry as G

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "docs" / "examples" / "building.example.json"


# --------------------------------------------------------------------------
# building.py
# --------------------------------------------------------------------------

def test_example_validates_and_broken_copy_fails():
    example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert B.validation_errors(example) == []
    B.validate(example)
    broken = json.loads(json.dumps(example))
    broken["walls"][0]["status"] = "maybe"
    del broken["rooms"][0]["polygon"]
    errors = B.validation_errors(broken)
    assert any("walls/0/status" in e for e in errors)
    assert any("rooms/0" in e and "polygon" in e for e in errors)
    with pytest.raises(jsonschema.ValidationError):
        B.validate(broken)


def test_empty_building_is_valid_and_complete():
    b = B.empty_building("p", "projects/p", "abc", created_utc="2026-10-01T00:00:00Z", brief={"style": "x"})
    B.validate(b)
    assert set(b) == set(B.load_schema()["required"])
    assert b["project"]["brief"] == {"style": "x"}
    assert B.empty_building("p", "projects/p", "abc")["project"]["created_utc"].endswith("Z")


def test_evidence_constructor():
    ev = B.evidence("a.dxf", "vector", 1.0, layer="DUVAR", entity="LWPOLYLINE:3F", pass_=2)
    assert ev == {"file": "a.dxf", "method": "vector", "confidence": 1.0, "layer": "DUVAR",
                  "entity": "LWPOLYLINE:3F", "pass": 2}
    with pytest.raises(ValueError):
        B.evidence("a", "guess", 1.0)
    with pytest.raises(ValueError):
        B.evidence("a", "ai", 1.5)


@pytest.mark.parametrize("raw, label, room_type, area", [
    ("SALON 24,50 m²", "Salon", "living", 24.5),
    ("SALON", "Salon", "living", None),
    ("YATAK ODASI", "Yatak Odası", "bedroom", None),
    ("ÇOCUK ODASI", "Çocuk Odası", "bedroom", None),
    ("EBEVEYN YATAK ODASI", "Ebeveyn Yatak Odası", "bedroom", None),
    ("MUTFAK 8.25 m2", "Mutfak", "kitchen", 8.25),
    ("BANYO", "Banyo", "bathroom", None),
    ("WC", "WC", "wc", None),
    ("HOL", "Hol", "hall", None),
    ("ANTRE", "Antre", "hall", None),
    ("KORİDOR", "Koridor", "hall", None),
    ("BALKON", "Balkon", "balcony", None),
    ("KİLER", "Kiler", "storage", None),
    ("DEPO", "Depo", "storage", None),
    ("ÇALIŞMA ODASI", "Çalışma Odası", "other", None),
    ("  salon   24,5 m² ", "Salon", "living", 24.5),
    # docs/milestone6.md §3.3: several keywords -> the highest priority wins; keywords match at word start.
    ("SALON + MUTFAK 39,05 m²", "Salon + Mutfak", "living", 39.05),
    ("EBEVEYN BANYO", "Ebeveyn Banyo", "bathroom", None),
    ("EBEVEYN BANYOSU", "Ebeveyn Banyosu", "bathroom", None),
    ("LAVABO", "Lavabo", "wc", None),
    ("TUVALET", "Tuvalet", "wc", None),
    ("DUŞ", "Duş", "bathroom", None),
    ("GİRİŞ", "Giriş", "hall", None),
    ("TERAS", "Teras", "balcony", None),
    ("YEMEK ODASI", "Yemek Odası", "other", None),
])
def test_normalise_room_label(raw, label, room_type, area):
    assert B.normalise_room_label(raw) == (label, room_type, area)


@pytest.mark.parametrize("label, room_type", [
    # Priority: wc > bathroom > storage > balcony > bedroom > living > kitchen > hall > other.
    ("BANYO VE WC", "wc"),
    ("WC + DUŞ", "wc"),
    ("BANYO KİLER", "bathroom"),
    ("KİLER BALKON", "storage"),
    ("YATAK ODASI BALKONU", "balcony"),
    ("ÇOCUK SALONU", "bedroom"),
    ("MUTFAK SALON", "living"),
    ("MUTFAK HOLÜ", "kitchen"),
    ("GİRİŞ HOLÜ", "hall"),
    ("ÇALIŞMA YATAK ODASI", "bedroom"),
    ("ÇALIŞMA HOLÜ", "hall"),
    # Word start only: a keyword inside a word does not count.
    ("ALKOHOL DOLABI", "other"),
    ("MİNİ BANYO", "bathroom"),
    ("SALONLAR", "living"),
    ("Banyo/WC", "wc"),
    ("2.YATAK ODASI", "bedroom"),
    ("", "other"),
])
def test_room_type_priority_and_word_start(label, room_type):
    assert B.room_type_for(label) == room_type


def test_room_type_priority_covers_every_keyword_type():
    keyword_types = {room_type for _, room_type in B._ROOM_TYPE_KEYWORDS}
    assert keyword_types <= set(B.ROOM_TYPE_PRIORITY) <= set(B.ROOM_TYPES)
    assert len(B.ROOM_TYPE_PRIORITY) == len(set(B.ROOM_TYPE_PRIORITY))
    assert B.ROOM_TYPE_PRIORITY == ("wc", "bathroom", "storage", "balcony", "bedroom", "living", "kitchen", "hall",
                                    "other")


# Every room of the five synthetic projects: id -> (label as drawn, room_type). The Milestone 2 projects
# must keep their room types (their truth must not change, docs/milestone6.md §3.3).
PINNED_ROOM_TYPES = {
    "synthetic-01": {
        "r_L0_salon": ("SALON 24,50 m²", "living"),
        "r_L0_yatak_odasi": ("YATAK ODASI", "bedroom"),
        "r_L0_hol": ("HOL", "hall"),
        "r_L0_banyo": ("BANYO", "bathroom"),
        "r_L0_mutfak": ("MUTFAK", "kitchen"),
        "r_L1_ebeveyn_yatak_odasi": ("EBEVEYN YATAK ODASI", "bedroom"),
        "r_L1_hol": ("HOL", "hall"),
        "r_L1_yatak_odasi": ("YATAK ODASI", "bedroom"),
        "r_L1_banyo": ("BANYO", "bathroom"),
        "r_L1_cocuk_odasi": ("ÇOCUK ODASI", "bedroom"),
    },
    "synthetic-02": {
        "r_L0_salon": ("SALON", "living"),
        "r_L0_yatak_odasi": ("YATAK ODASI", "bedroom"),
        "r_L0_mutfak": ("MUTFAK", "kitchen"),
        "r_L0_antre": ("ANTRE", "hall"),
        "r_L0_banyo": ("BANYO", "bathroom"),
    },
    "synthetic-03": {
        "r_L-1_kiler": ("KİLER", "storage"),
        "r_L-1_hol": ("HOL", "hall"),
        "r_L-1_yatak_odasi": ("YATAK ODASI", "bedroom"),
        "r_L-1_kiler_2": ("KİLER", "storage"),
        "r_L-1_wc": ("WC", "wc"),
        "r_L-1_banyo": ("BANYO", "bathroom"),
        "r_L0_salon": ("SALON 24,00 m²", "living"),
        "r_L0_hol": ("HOL", "hall"),
        "r_L0_yatak_odasi": ("YATAK ODASI", "bedroom"),
        "r_L0_mutfak": ("MUTFAK", "kitchen"),
        "r_L0_antre": ("ANTRE", "hall"),
        "r_L0_wc": ("WC", "wc"),
        "r_L0_kiler": ("KİLER", "storage"),
        "r_L1_ebeveyn_yatak_odasi": ("EBEVEYN YATAK ODASI", "bedroom"),
        "r_L1_hol": ("HOL", "hall"),
        "r_L1_yatak_odasi": ("YATAK ODASI", "bedroom"),
        "r_L1_cocuk_odasi": ("ÇOCUK ODASI", "bedroom"),
        "r_L1_banyo": ("BANYO", "bathroom"),
        "r_L1_balkon": ("BALKON", "balcony"),
    },
    "synthetic-04": {
        "r_L3_salon_mutfak": ("SALON + MUTFAK 39,05 m²", "living"),
        "r_L3_yatak_odasi": ("YATAK ODASI", "bedroom"),
        "r_L3_hol": ("HOL", "hall"),
        "r_L3_cocuk_odasi": ("ÇOCUK ODASI", "bedroom"),
        "r_L3_banyo": ("BANYO", "bathroom"),
    },
    "synthetic-05": {
        "r_L0_salon": ("SALON 19,76 m²", "living"),
        "r_L0_ebeveyn_yatak_odasi": ("EBEVEYN YATAK ODASI", "bedroom"),
        "r_L0_ebeveyn_banyo": ("EBEVEYN BANYO", "bathroom"),
        "r_L0_mutfak": ("MUTFAK", "kitchen"),
        "r_L0_hol": ("HOL", "hall"),
        "r_L0_calisma_odasi": ("ÇALIŞMA ODASI", "other"),
        "r_L0_antre": ("ANTRE", "hall"),
        "r_L0_banyo": ("BANYO", "bathroom"),
        "r_L0_yatak_odasi": ("YATAK ODASI", "bedroom"),
    },
}


@pytest.mark.parametrize("name", sorted(PINNED_ROOM_TYPES))
def test_room_types_pinned_for_synthetic_projects(name):
    """The committed truth and a fresh label lookup both give the pinned room types."""
    truth = B.load(ROOT / "projects" / name / "truth" / "building.json")
    got = {r["id"]: (r["label_raw"], r["room_type"]) for r in truth["rooms"]}
    assert got == PINNED_ROOM_TYPES[name]
    for label_raw, room_type in PINNED_ROOM_TYPES[name].values():
        assert B.normalise_room_label(label_raw)[1] == room_type, label_raw


@pytest.mark.parametrize("raw, expected", [
    ("ZEMİN KAT PLANI", ("Zemin Kat", 0)),
    ("1. KAT PLANI", ("1. Kat", 1)),
    ("2. KAT PLANI", ("2. Kat", 2)),
    ("12.KAT PLANI", ("12. Kat", 12)),
    ("BODRUM KAT PLANI", ("Bodrum Kat", -1)),
    ("ZEMİN KAT MOBİLYA PLANI", ("Zemin Kat", 0)),
    ("MOBİLYA PLANI", None),
    ("ÖLÇEK 1/100", None),
])
def test_normalise_level_label(raw, expected):
    assert B.normalise_level_label(raw) == expected


def test_turkish_case_and_slug():
    assert B.turkish_lower("KİLER I") == "kiler ı"
    assert B.turkish_upper("kiler ı") == "KİLER I"
    assert B.slugify("Yatak Odası") == "yatak_odasi"
    assert B.slugify("Çocuk Odası") == "cocuk_odasi"
    assert B.slugify("") == "room"


def test_id_convention():
    assert B.level_id(0) == "L0" and B.level_id(1) == "L1" and B.level_id(-1) == "L-1"
    ids = B.IdCounter()
    assert [ids.next("wall", "L0") for _ in range(2)] == ["w_L0_001", "w_L0_002"]
    assert ids.next("door", "L0") == "d_L0_001"
    assert ids.next("window", "L0") == "win_L0_001"
    assert ids.next("opening", "L1") == "o_L1_001"
    assert ids.next("furniture", "L1") == "f_L1_001"
    assert ids.next("conflict") == "c_001" and ids.next("conflict") == "c_002"
    assert ids.room("L0", "Salon") == "r_L0_salon"
    assert ids.room("L0", "Kiler") == "r_L0_kiler"
    assert ids.room("L0", "Kiler") == "r_L0_kiler_2"
    assert ids.room("L0", "Kiler") == "r_L0_kiler_3"
    with pytest.raises(ValueError):
        B.element_id("wall", None, 1)


def test_save_and_load_roundtrip(tmp_path):
    b = B.empty_building("p", "projects/p", "abc", created_utc="2026-10-01T00:00:00Z")
    path = B.save(b, tmp_path / "sub" / "building.json")
    assert B.load(path) == b
    b["status"] = "broken"
    with pytest.raises(jsonschema.ValidationError):
        B.save(b, tmp_path / "x.json")


# --------------------------------------------------------------------------
# geometry.py
# --------------------------------------------------------------------------

def test_polygon_area_and_point_in_polygon():
    square = [(0, 0), (2, 0), (2, 2), (0, 2)]
    assert G.polygon_area(square) == 4.0
    assert G.polygon_signed_area(list(reversed(square))) == -4.0
    assert G.polygon_centroid(square) == (1.0, 1.0)
    assert G.point_in_polygon((1, 1), square)
    assert G.point_in_polygon((2, 1), square)  # on the edge counts as inside
    assert not G.point_in_polygon((3, 1), square)
    concave = [(0, 0), (4, 0), (4, 4), (2, 4), (2, 2), (0, 2)]
    assert G.point_in_polygon((1, 1), concave) and not G.point_in_polygon((1, 3), concave)


def test_segments_and_angles():
    assert G.segment_length((0, 0), (3, 4)) == 5.0
    assert G.segment_midpoint((0, 0), (2, 4)) == (1.0, 2.0)
    assert G.segment_angle_deg((0, 0), (0, 1)) == 90.0
    assert G.segment_angle_deg((1, 1), (0, 1)) == 180.0
    assert G.normalise_angle(-90) == 270.0 and G.normalise_angle(360) == 0.0
    assert G.angle_difference_deg(350, 10) == 20.0
    assert G.point_segment_distance((1, 1), (0, 0), (2, 0)) == 1.0
    assert G.point_segment_distance((5, 0), (0, 0), (2, 0)) == 3.0
    assert G.unit_normal_left((0, 0), (1, 0)) == (0.0, 1.0)
    x, y = G.rotate_point((1, 0), 90)
    assert abs(x) < 1e-12 and abs(y - 1) < 1e-12
    assert G.point_at_distance((0, 0), (10, 0), 2.5) == (2.5, 0.0)


def test_rectangle_centerline_roundtrip():
    start, end, t = G.rectangle_to_centerline([(0, 0), (9.6, 0), (9.6, 0.25), (0, 0.25)])
    assert start == (0.0, 0.125) and end == (9.6, 0.125) and abs(t - 0.25) < 1e-12
    # Any corner order and an explicit closing point give the same answer.
    start2, end2, t2 = G.rectangle_to_centerline([(9.6, 0.25), (9.6, 0), (0, 0), (0, 0.25), (9.6, 0.25)])
    assert (start2, end2) == (start, end) and abs(t2 - t) < 1e-12
    corners = G.centerline_to_rectangle((5.3, 0.25), (5.3, 6.95), 0.1)
    s, e, t = G.rectangle_to_centerline(corners)
    assert s == (5.3, 0.25) and e == (5.3, 6.95) and abs(t - 0.1) < 1e-9
    with pytest.raises(ValueError):
        G.rectangle_to_centerline([(0, 0), (1, 0), (1, 1)])


def test_rotated_rectangle_and_front():
    corners = G.rotated_rectangle((1, 1), (2, 1), 90)
    xs = sorted(round(c[0], 9) for c in corners)
    ys = sorted(round(c[1], 9) for c in corners)
    assert xs == [0.5, 0.5, 1.5, 1.5] and ys == [0.0, 0.0, 2.0, 2.0]
    assert G.front_direction_deg(0) == 270.0 and G.front_direction_deg(90) == 0.0


def test_boxes():
    assert G.bbox([(1, 2), (-1, 5), (3, 0)]) == [-1, 0, 3, 5]
    assert G.box_iou([0, 0, 2, 2], [1, 1, 3, 3]) == pytest.approx(1 / 7)
    assert G.box_iou([0, 0, 1, 1], [2, 2, 3, 3]) == 0.0
    assert G.box_iou([0, 0, 1, 1], [0, 0, 1, 1]) == 1.0
    assert G.box_center([0, 0, 2, 4]) == (1.0, 2.0)
    with pytest.raises(ValueError):
        G.bbox([])


def test_affine_and_homography():
    a = G.affine_from_scale_translate(28.3465, 28.3465, 200, 150)
    p = G.apply_affine(a, (3.3, 4.4))
    back = G.apply_affine(G.invert_affine(a), p)
    assert back == pytest.approx((3.3, 4.4))
    flip = [1, 0, 0, 0, -1, 10]
    composed = G.compose_affine(flip, a)  # a first, then flip
    assert G.apply_affine(composed, (1, 1)) == pytest.approx(G.apply_affine(flip, G.apply_affine(a, (1, 1))))
    m = G.affine_to_matrix(a)
    assert G.matrix_to_affine(m) == a
    assert G.apply_homography(m, (1, 2)) == pytest.approx(G.apply_affine(a, (1, 2)))
    flat = [v for row in m for v in row]
    assert G.apply_homography(flat, (1, 2)) == pytest.approx(G.apply_affine(a, (1, 2)))
    h = [[1, 0.1, 5], [0.05, 1, 7], [0.001, 0.002, 1]]
    q = G.apply_homography(h, (10, 20))
    assert G.apply_homography(G.invert_homography(h), q) == pytest.approx((10, 20))
    assert G.transform_box(a, [0, 0, 1, 1]) == pytest.approx([200, 150, 228.3465, 178.3465])
    with pytest.raises(ValueError):
        G.matrix_to_affine(h)
    with pytest.raises(ZeroDivisionError):
        G.invert_affine([1, 2, 0, 2, 4, 0])
    assert math.isclose(G.snap(0.1 + 0.2), 0.3) and G.snap(-1e-9) == 0.0
