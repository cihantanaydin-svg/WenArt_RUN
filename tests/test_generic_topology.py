"""Plot, building, faces and separators of the generic plan core (docs/milestone7.md §2.5, §2.7.1, §11 G2).

Synthetic plans (metres) check the C-shaped plot found by its convex hull, other wall components, a free-standing
wall inside the house, an exterior area enclosed by building walls, labels outside the building, and the separator
rules (end-to-wall and end-to-end candidates only from empty end gaps, kept only when two names share a face or a
stair shares a labelled face; Milestone 10: the end-to-face fallback). real01 checks the plot wall in ``site``, the
Parking area, exactly one separator (O2) and the single unlabelled hall face that holds the stair.
"""
import math

import pytest
from shapely.geometry import Point, box as sbox

import _real01_page as R
from wenart.ingest.generic import openings as O
from wenart.ingest.generic import topology as TP

FT = 0.3048
LB = R.LabelBlockStub


def _box_walls(x0, y0, x1, y1, t=0.2):
    return [R.wall((x0, y0), (x1, y0), t), R.wall((x1, y0), (x1, y1), t), R.wall((x1, y1), (x0, y1), t),
            R.wall((x0, y1), (x0, y0), t)]


def _plot_c(x0, y0, x1, y1, open_from, t=0.15):
    """A compound wall around the house, open on the east side below ``open_from``."""
    return [R.wall((x0, y0), (x1, y0), t), R.wall((x0, y0), (x0, y1), t), R.wall((x0, y1), (x1, y1), t),
            R.wall((x1, open_from), (x1, y1), t)]


# --------------------------------------------------------------------------
# split_plot
# --------------------------------------------------------------------------

def test_c_shaped_plot_wall_goes_to_site_by_its_convex_hull():
    house = _box_walls(0, 0, 6, 4)
    plot = _plot_c(-2, -2, 9, 6, open_from=2.5)
    labels = [LB("Kitchen", (3, 2), "kitchen"), LB("Garden", (7.5, 0.0), "other", exterior=True,
                                                    size_text="10' x 8'")]
    walls, openings, _, _ = O.gaps_and_openings(house + plot, [], "t.pdf", 1)
    bwalls, site, warnings = TP.split_plot(walls, openings, labels, level_id="L0")
    assert len(bwalls) == 4
    assert all(max(abs(c) for c in w.start + w.end) <= 6.0 for w in bwalls)
    assert [w["kind"] for w in site["boundary_walls"]] == ["plot"] * 4
    assert site["boundary_walls"][0]["id"] == "sw_L0_001"
    assert not [w for w in warnings if "not part of the building" in w]
    area = site["areas"][0]
    assert area["label"] == "Garden" and area["polygon"] is None and area["id"] == "sa_L0_garden"
    assert area["label_size"]["status"] == "unchecked"
    # Open extent around the label: house wall (x 6.1) to the plot hull (x 9.034 at y 0: the hull edge runs from the
    # south wall's end at x 9.0 to the east wall's outer face at x 9.075); plot wall faces y -1.925 to 5.925.
    assert area["extent_m"] == pytest.approx([9.034 - 6.1, 5.925 + 1.925], abs=0.01)


def test_other_component_is_site_other_with_a_warning():
    house = _box_walls(0, 0, 6, 4)
    stray = [R.wall((20, 20), (24, 20), 0.2)]
    labels = [LB("Living", (3, 2), "living")]
    bwalls, site, warnings = TP.split_plot(house + stray, [], labels)
    assert len(bwalls) == 4
    assert [w["kind"] for w in site["boundary_walls"]] == ["other"]
    assert any("not part of the building" in w for w in warnings)


def test_free_standing_wall_inside_the_house_stays_a_building_wall():
    house = _box_walls(0, 0, 8, 6)
    island = [R.wall((3, 3), (5, 3), 0.1)]
    labels = [LB("Living", (1.5, 1.5), "living")]
    bwalls, site, warnings = TP.split_plot(house + island, [], labels)
    assert len(bwalls) == 5 and not site["boundary_walls"]
    assert any("free-standing wall component inside the building" in w for w in warnings)


def test_exterior_face_inside_the_building_is_a_site_area():
    walls = _box_walls(0, 0, 8, 4) + [R.wall((4, 0), (4, 4), 0.15)]
    labels = [LB("Kitchen", (2, 2), "kitchen"), LB("Courtyard", (6, 2), "other", exterior=True)]
    bwalls, site, warnings = TP.split_plot(walls, [], labels, level_id="L0")
    assert len(bwalls) == 5
    area = site["areas"][0]
    assert area["label"] == "Courtyard" and area["polygon"] is not None
    assert TP.Polygon(area["polygon"]).area == pytest.approx((7.9 - 4.075) * 3.8, rel=0.01)
    assert any("enclosed by building walls" in w for w in warnings)
    assert not [w for w in warnings if w.startswith(TP.REVIEW_PREFIX)]


def test_room_label_outside_the_building_is_a_warning():
    labels = [LB("Living", (3, 2), "living"), LB("Store", (30, 30), "storage")]
    _, _, warnings = TP.split_plot(_box_walls(0, 0, 6, 4), [], labels)
    assert any("'Store'" in w and "outside the building" in w for w in warnings)


def test_outer_loop_problem():
    assert TP.outer_loop_problem(_box_walls(0, 0, 6, 4)) is None
    open_box = _box_walls(0, 0, 6, 4)[:3]
    assert "enclose no face" in TP.outer_loop_problem(open_box)


# --------------------------------------------------------------------------
# separators
# --------------------------------------------------------------------------

def _open_plan(labels, door=False):
    """An 8 x 4 m box with a partition at x 4 from the south wall to y 2.5: its free end leaves a 1.4 m end gap."""
    walls = _box_walls(0, 0, 8, 4) + [R.wall((4, 0), (4, 2.5), 0.15)]
    strokes = []
    if door:
        strokes = [R.arc((4.06, 3.88), 1.36, 270, 180)]              # a door swing hinged at the north wall face
    walls2, openings, log, owned = O.gaps_and_openings(walls, strokes, "t.pdf", 1)
    return walls2, openings, log


def test_end_to_wall_separator_is_kept_when_two_names_share_a_face():
    walls, openings, log = _open_plan(None)
    labels = [LB("Living", (2, 2), "living"), LB("Dining", (6, 2), "dining")]
    kept, slog = TP.separators(walls, openings, log, labels, [])
    assert len(kept) == 1
    s = kept[0]
    assert s.kind == "opening" and s.virtual and s.line is not None
    assert s.line[0] == pytest.approx((4.0, 2.5)) and s.line[1] == pytest.approx((4.0, 3.9))
    assert s.width == pytest.approx(1.4)
    assert s.evidence["method"] == "derived" and "two room names" in s.evidence["note"]
    assert slog[0]["kept"] is True and slog[0]["kind"] == "end_to_wall"
    faces = TP.faces(walls, openings, kept)
    assert len(faces) == 2


def test_separator_not_needed_is_listed_as_dropped():
    walls, openings, log = _open_plan(None)
    kept, slog = TP.separators(walls, openings, log, [LB("Living", (2, 2), "living")], [])
    assert kept == []
    assert slog and slog[0]["kept"] is False and slog[0]["reason"] == "considered, not needed"


def test_end_gap_holding_a_door_gives_no_separator_candidate():
    walls, openings, log = _open_plan(None, door=True)
    assert [o.kind for o in openings] == ["door"]
    labels = [LB("Living", (2, 2), "living"), LB("Dining", (6, 2), "dining")]
    kept, slog = TP.separators(walls, openings, log, labels, [])
    assert kept == [] and slog == []
    assert len(TP.faces(walls, openings)) == 2                        # the extended wall closes the face


def test_separator_kept_when_it_separates_a_stair_from_a_labelled_face():
    walls, openings, log = _open_plan(None)
    stair = R.wall((6, 1), (6, 3))                                     # anything with a centre
    stair.center = (6.0, 2.0)
    kept, slog = TP.separators(walls, openings, log, [LB("Living", (2, 2), "living")], [stair])
    assert len(kept) == 1 and "separates the stair" in kept[0].evidence["note"]


def test_end_to_end_separator_between_two_parallel_stubs():
    walls = _box_walls(0, 0, 6, 6) + [R.wall((0, 2), (3, 2), 0.15), R.wall((0, 4), (3.1, 4), 0.15)]
    walls2, openings, log, _ = O.gaps_and_openings(walls, [], "t.pdf", 1)
    labels = [LB("Bath", (1.5, 3), "bathroom"), LB("Hall", (4.5, 1), "hall")]
    kept, slog = TP.separators(walls2, openings, log, labels, [])
    assert [e["kind"] for e in slog if e["kept"]] == ["end_to_end"]
    line = kept[0].line
    assert line[0][0] == pytest.approx(3.0) and line[1][0] == pytest.approx(3.0)      # at the shorter stub's end
    assert sorted((line[0][1], line[1][1])) == pytest.approx([2.075, 3.925])
    # The end-to-wall candidates from the same free ends are 2.9 m long: over 2.4 m.
    assert any(e["kind"] == "end_to_wall" and "longer than" in e["reason"] for e in slog)


def test_unlabelled_face_type():
    """Openings are bridged, so a doorless opening separates two faces; the middle room of a row with an opening
    on each side touches two openings: a hall."""
    row = _box_walls(0, 0, 9, 4) + [R.wall((3, 0), (3, 1.5), 0.15), R.wall((3, 2.5), (3, 4), 0.15),
                                    R.wall((6, 0), (6, 1.5), 0.15), R.wall((6, 2.5), (6, 4), 0.15)]
    walls, openings, _, _ = O.gaps_and_openings(row, [], "t.pdf", 1)
    faces = TP.faces(walls, openings)
    assert len(faces) == 3
    middle = [f for f in faces if f.contains(Point(4.5, 2))][0]
    side = [f for f in faces if f.contains(Point(1.5, 2))][0]
    assert TP.unlabelled_face_type(middle, walls, openings) == ("hall", "unlabelled face touching 2 doors/openings")
    assert TP.unlabelled_face_type(side, walls, openings)[0] == "unknown"
    stair = type("S", (), {"center": (1.0, 1.0)})()
    assert TP.unlabelled_face_type(side, walls, openings, [stair]) == ("hall", "unlabelled face holding the stair")


# --------------------------------------------------------------------------
# real01
# --------------------------------------------------------------------------

def test_end_to_face_separator_when_the_cast_runs_through_a_door():
    """real02's basement: a wall's free end points across the corridor at a door in the far wall; its cast finds no
    wall within 3 m (it runs through the door gap), so only the end-to-face fallback separates the two names."""
    walls = _box_walls(0, 0, 8, 6) + [R.wall((2, 0), (2, 2.6), 0.2), R.wall((2, 3.4), (2, 6), 0.2),
                                      R.wall((8, 3), (4, 3), 0.15)]
    door = [R.arc((2.0, 2.6), 0.8, 90, 0)]
    walls2, openings, log, _ = O.gaps_and_openings(walls, door, "t.pdf", 1)
    assert [o.kind for o in openings] == ["door"]
    assert any(e["kind"] == "free_end" and e["gap_class"] == "none" for e in log)
    labels = [LB("Kitchen", (6, 4.5), "kitchen"), LB("Living", (6, 1.5), "living")]
    kept, slog = TP.separators(walls2, openings, log, labels, [])
    assert [e["kind"] for e in slog] == ["end_to_face"] and slog[0]["kept"]
    line = kept[0].line
    assert sorted(p[0] for p in line) == pytest.approx([2.1, 4.0], abs=0.01) and all(p[1] == 3.0 for p in line)
    faces = TP.faces(walls2, openings, kept)
    assert all(sum(f.contains(Point(p)) for f in faces) == 1 for p in ((6, 4.5), (6, 1.5)))
    # One name in the face: the fallback is not tried (the log stays as before).
    kept, slog = TP.separators(walls2, openings, log, labels[:1], [])
    assert kept == [] and slog == []


@pytest.fixture(scope="module")
def chain():
    return R.g2_chain()


def test_real01_plot_wall_is_in_site_and_not_in_the_building(chain):
    site = chain["site"]
    assert [w["kind"] for w in site["boundary_walls"]] == ["plot"] * 4
    house = sbox(*R.ref_box([0.0, 0.0, 42.508, 24.0])).buffer(0.01)
    for w in chain["building_walls"]:
        assert house.contains(Point(w.start)) and house.contains(Point(w.end)), w
    plot = R.reference()["site"]["plot_wall"]
    outer = sbox(*R.ref_box(plot["outer_bbox_ft"]))
    for w in site["boundary_walls"]:
        assert outer.buffer(0.05).contains(Point(w["start"])) and not house.contains(Point(w["start"]))
    assert not [w for w in chain["site_warnings"] if w.startswith(TP.REVIEW_PREFIX)]


def test_real01_parking_is_a_site_area_without_polygon(chain):
    areas = chain["site"]["areas"]
    assert [a["label"] for a in areas] == ["Parking"]
    parking = areas[0]
    assert parking["polygon"] is None
    assert parking["label_size"]["status"] == "unchecked"          # the area is not closed: reported only
    ext = sorted(v / FT for v in parking["extent_m"])
    assert ext[0] == pytest.approx(11.25, abs=0.3)                 # W_SE outer face to the S plot wall
    assert 15.0 <= ext[1] <= 15.6                                  # house wall to the plot line (C07: 15.0-15.5)


def test_real01_one_separator_o2(chain):
    seps = chain["separators"]
    assert len(seps) == 1
    o2 = [o for o in R.reference()["openings"] if o["id"] == "O2"][0]
    s = seps[0]
    c = R.to_ref(s.center)
    assert math.dist(c, o2["centre_ft"]) <= o2["tol"]["centre"]
    assert s.width / FT == pytest.approx(o2["width_ft"], abs=o2["tol"]["width"])
    assert s.virtual and s.kind == "opening"
    dropped = [e for e in chain["separator_log"] if not e["kept"]]
    kept = [e for e in chain["separator_log"] if e["kept"]]
    assert len(kept) == 1 and kept[0]["kind"] == "end_to_wall"
    assert all(e["reason"] for e in dropped)


def test_real01_faces_and_the_unlabelled_hall(chain):
    faces = chain["faces"]
    labelled = [f for f in faces if f["label"]]
    assert len(labelled) == 8                                     # every room label in its own face
    assert len({id(f) for f in labelled}) == 8
    unlabelled = [f for f in faces if not f["label"]]
    assert len(unlabelled) == 1                                   # lobby + stair space: the merged hall face
    want = R.reference()["circulation"]["merged_face"]
    b = unlabelled[0]["polygon"].bounds
    got = R.to_ref(b[:2]) + R.to_ref(b[2:])
    assert got == pytest.approx(want["bbox_ft"], abs=want["tol"]["edge"])
    stairs = [p for p in chain["pieces"] if p.type == "stair"]
    kind, reason = TP.unlabelled_face_type(unlabelled[0]["polygon"], chain["building_walls"],
                                           chain["building_openings"], stairs)
    assert kind == "hall" and "stair" in reason
    assert TP.outer_loop_problem(chain["building_walls"], chain["building_openings"]) is None
