"""Room derivation (wenart/ingest/rooms.py): walls -> union -> faces -> labelled rooms."""
import pytest

from wenart import building as B
from wenart import geometry as G
from wenart.ingest import rooms as R
from wenart.ingest.dxf_extract import extract_dxf
from wenart.ingest.model import TextItem, WallItem
from wenart.ingest.pdf_extract import extract_pdf_page

from conftest import PROJECTS, load_truth

CASES = [("synthetic-01", "zemin_kat.dxf", 1, "L0"), ("synthetic-03", "mobilya_plani.dxf", 1, "L0"),
         ("synthetic-01", "1_kat.pdf", 1, "L1"), ("synthetic-03", "kat_planlari.pdf", 1, "L-1"),
         ("synthetic-03", "kat_planlari.pdf", 2, "L0"), ("synthetic-03", "kat_planlari.pdf", 3, "L1"),
         ("synthetic-02", "truth/plan.pdf", 1, "L0")]


def extraction(name, file, number, level_id):
    if file.endswith(".dxf"):
        return extract_dxf(PROJECTS / name / file, level_id, file)
    return extract_pdf_page(PROJECTS / name / file, number, level_id, file)


def label_points(ex):
    anchors = [G.apply_affine(ex.transform_to_building, t.start) for t in ex.labels]
    centres = [G.apply_affine(ex.transform_to_building, G.box_center(t.box)) for t in ex.labels]
    return anchors, centres


@pytest.mark.parametrize("name, file, number, level_id", CASES, ids=[f"{c[1]}-p{c[2]}" for c in CASES])
def test_rooms_match_truth(name, file, number, level_id):
    ex = extraction(name, file, number, level_id)
    anchors, centres = label_points(ex)
    result = R.derive_rooms(level_id, ex.walls, ex.labels, anchors, centres, file)
    truth_rooms = [r for r in load_truth(name)["rooms"] if r["level_id"] == level_id]
    assert result.closed and result.warnings == [] and result.unplaced_labels == []
    assert [r["id"] for r in result.rooms] == [r["id"] for r in truth_rooms]
    for room, expected in zip(result.rooms, truth_rooms):
        assert room["label"] == expected["label"] and room["room_type"] == expected["room_type"]
        assert room["label_raw"] == expected["label_raw"] and room["area_label"] == expected["area_label"]
        assert abs(room["area_computed"] - expected["area_computed"]) <= 0.01 * expected["area_computed"]
        assert len(room["polygon"]) == len(expected["polygon"])
        assert max(G.distance(a, b) for a, b in zip(room["polygon"], expected["polygon"])) < 0.005
        assert room["status"] == "verified" and room["evidence"][0]["text"] == expected["label_raw"]
        derived = next(e for e in expected["evidence"] if e["method"] == "derived")
        assert len(result.room_walls[room["id"]]) == len(derived["entity"].split(":", 1)[1].split(","))
    # The four outer walls are exterior, the inner walls are not.
    assert [w.exterior for w in ex.walls] == [True] * 4 + [False] * (len(ex.walls) - 4)
    assert R.outer_walls_closed(ex.walls)


def square_walls(size=5.0, t=0.25):
    h = t / 2
    return [WallItem((0.0, h), (size, h), t, [0, 0, 0, 0], "a", B.evidence("x.dxf", "vector", 1.0, entity="a")),
            WallItem((size - h, 0.0), (size - h, size), t, [0, 0, 0, 0], "b", B.evidence("x.dxf", "vector", 1.0, entity="b")),
            WallItem((0.0, size - h), (size, size - h), t, [0, 0, 0, 0], "c", B.evidence("x.dxf", "vector", 1.0, entity="c")),
            WallItem((h, 0.0), (h, size), t, [0, 0, 0, 0], "d", B.evidence("x.dxf", "vector", 1.0, entity="d"))]


def label(text, at, entity="TEXT:1"):
    return TextItem(text, at, [at[0], at[1], at[0] + 1, at[1] + 0.2], 0.0, entity, 0.2, role="room_label",
                    evidence=B.evidence("x.dxf", "vector", 1.0, entity=entity, text=text))


def test_unclosed_outer_walls():
    walls = square_walls()[:3]  # left wall missing
    assert not R.outer_walls_closed(walls)
    result = R.derive_rooms("L0", walls, [label("SALON", (1, 1))], [(1, 1)], None, "x.dxf")
    assert not result.closed and result.rooms == []
    assert any("closed loop" in w or "no enclosed room" in w for w in result.warnings)


def test_open_outer_wall_with_an_enclosed_room_is_not_closed():
    """One half of the top wall is missing: the right room is still a hole of
    the union, so the ring count alone says 'closed'. The left outer wall now
    ends in the open, which is what the closure check must catch."""
    size, t = 5.0, 0.25
    h = t / 2
    ev = B.evidence("x.dxf", "vector", 1.0, entity="w")
    walls = [WallItem((0.0, h), (size, h), t, [0, 0, 0, 0], "bottom", ev),
             WallItem((size - h, 0.0), (size - h, size), t, [0, 0, 0, 0], "right", ev),
             WallItem((h, 0.0), (h, size), t, [0, 0, 0, 0], "left", ev),
             WallItem((2.5, size - h), (size, size - h), t, [0, 0, 0, 0], "top-right", ev),
             WallItem((2.5, t), (2.5, size - t), 0.1, [0, 0, 0, 0], "inner", ev)]
    assert R.wall_union(walls).geom_type == "Polygon" and len(R.wall_union(walls).interiors) == 1
    assert not R.outer_walls_closed(walls)
    labels = [label("SALON", (1, 1), "TEXT:1"), label("MUTFAK", (3.5, 3), "TEXT:2")]
    result = R.derive_rooms("L0", walls, labels, [(1, 1), (3.5, 3)], None, "x.dxf")
    assert not result.closed
    assert any("closed loop" in w and "left" in w for w in result.warnings)
    # The enclosed room is still derived so the review report can show it.
    assert [r["label"] for r in result.rooms] == ["Mutfak"]
    assert result.unplaced_labels == [labels[0]]
    # The complete drawing is closed.
    walls.append(WallItem((0.0, size - h), (2.5, size - h), t, [0, 0, 0, 0], "top-left", ev))
    assert R.outer_walls_closed(walls)
    result = R.derive_rooms("L0", walls, labels, [(1, 1), (3.5, 3)], None, "x.dxf")
    assert result.closed and [r["label"] for r in result.rooms] == ["Salon", "Mutfak"]


def test_room_without_label_is_unverified():
    result = R.derive_rooms("L0", square_walls(), [], [], None, "x.dxf")
    assert result.closed and len(result.rooms) == 1
    room = result.rooms[0]
    assert room["status"] == "unverified" and room["room_type"] == "unknown" and room["label_raw"] is None
    assert room["id"] == "r_L0_oda" and abs(room["area_computed"] - 4.5 * 4.5) < 1e-6
    assert any("no label" in w for w in result.warnings)


def test_label_outside_every_room_is_reported():
    lab = label("SALON", (9, 9))
    result = R.derive_rooms("L0", square_walls(), [lab], [(9, 9)], [(9.5, 9.1)], "x.dxf")
    assert result.unplaced_labels == [lab] and result.rooms[0]["status"] == "unverified"
    assert any("outside every room" in w for w in result.warnings)


def test_two_labels_in_one_room():
    labels = [label("SALON", (1, 1), "TEXT:1"), label("MUTFAK", (3, 3), "TEXT:2")]
    result = R.derive_rooms("L0", square_walls(), labels, [(1, 1), (3, 3)], None, "x.dxf")
    room = result.rooms[0]
    assert room["label"] == "Salon" and room["status"] == "unverified" and len(room["evidence"]) == 2
    assert any("more labels" in w for w in result.warnings)


def test_fallback_point_places_label():
    lab = label("SALON 20,00 m²", (-1, 1))  # anchor outside, box centre inside
    result = R.derive_rooms("L0", square_walls(), [lab], [(-1, 1)], [(2, 2)], "x.dxf")
    room = result.rooms[0]
    assert room["label"] == "Salon" and room["area_label"] == 20.0 and room["status"] == "verified"


def test_tiny_gaps_do_not_merge_rooms():
    walls = square_walls()
    # Inner wall that stops 0.3 mm short of the outer faces on both ends.
    walls.append(WallItem((2.5, 0.2503), (2.5, 4.7497), 0.1, [0, 0, 0, 0], "e", B.evidence("x.dxf", "vector", 1.0, entity="e")))
    labels = [label("SALON", (1, 1), "TEXT:1"), label("MUTFAK", (3, 3), "TEXT:2")]
    result = R.derive_rooms("L0", walls, labels, [(1, 1), (3, 3)], None, "x.dxf")
    assert [r["label"] for r in result.rooms] == ["Salon", "Mutfak"]
    assert all(r["status"] == "verified" for r in result.rooms)


def test_room_containing():
    rooms = [{"id": "a", "polygon": [[0, 0], [2, 0], [2, 2], [0, 2]]}]
    assert R.room_containing(rooms, (1, 1))["id"] == "a"
    assert R.room_containing(rooms, (3, 1)) is None


# --------------------------------------------------------------------------
# Generic core pages (docs/milestone7.md §2.7): label blocks, separators, placeholders, size labels
# --------------------------------------------------------------------------

def wall(start, end, t=0.2, entity="w"):
    ev = B.evidence("p.pdf", "vector", 0.95, entity=entity)
    return WallItem(tuple(start), tuple(end), t, [0, 0, 0, 0], entity, ev)


def two_rooms(open_plan: bool = False):
    """Outer box 0..8 x 0..4 (0.2 m walls) split at x = 4 (a stub from the top to y = 2.6 when ``open_plan``)."""
    walls = [wall((0, 0.1), (8, 0.1)), wall((0, 3.9), (8, 3.9)), wall((0.1, 0), (0.1, 4)), wall((7.9, 0), (7.9, 4))]
    walls.append(wall((4, 3.8), (4, 2.6)) if open_plan else wall((4, 0.2), (4, 3.8)))
    return walls


def blocks_at(*items, turkish=False):
    """Label blocks built by generic.labels from (name, size or None, anchor) and their TextItems."""
    from wenart.ingest.generic import labels as LB
    from wenart.ingest.generic.model import TextRun

    runs = []
    for k, (name, size, (x, y)) in enumerate(items):
        runs.append(TextRun(id=f"char:{10 * k}", text=name, box=(x - 0.5, y, x + 0.5, y + 0.2), height=0.2))
        if size:
            runs.append(TextRun(id=f"char:{10 * k + 5}", text=size, box=(x - 0.5, y - 0.3, x + 0.5, y - 0.1),
                                height=0.2))
    blocks = LB.merge_label_blocks(runs, "p.pdf", 1)
    labels = [TextItem(b.name, b.anchor, list(b.box), 0.0, b.name_runs[0].id, 0.2, role="room_label",
                       evidence=b.evidence[0], block=b, turkish=turkish) for b in blocks]
    return labels, [b.anchor for b in blocks]


def test_generic_labels_name_type_and_check_the_printed_size():
    # Faces: 3.7 x 3.6 m (x 0.2-3.9, y 0.2-3.8) and 3.6 x 3.6 m.
    labels, points = blocks_at(("LIVING ROOM", "12' 2\" x 11' 10\"", (2, 2)), ("BED ROOM", "11' x 10'", (6, 2)))
    result = R.derive_rooms("L0", two_rooms(), labels, points, None, "p.pdf")
    rooms = {r["label"]: r for r in result.rooms}
    assert set(rooms) == {"Living Room", "Bed Room"}
    living, bed = rooms["Living Room"], rooms["Bed Room"]
    assert living["label_raw"] == "LIVING ROOM" and living["room_type"] == "living" and living["status"] == "verified"
    assert living["label_size"]["status"] == "ok" and living["label_size"]["measured"] == [3.7, 3.6]
    assert len(living["evidence"]) == 2                                   # name run and size run
    # 11' x 10' (3.35 x 3.05 m) in a 3.7 x 3.6 m face: a conflict, beyond 10 % -> unverified.
    assert bed["label_size"]["status"] == "conflict" and bed["status"] == "unverified"
    assert result.label_size_conflicts == [(bed["id"], result.label_size_conflicts[0][1])]
    assert result.label_size_conflicts[0][1]["text"] == "11' x 10'"
    assert result.multi_labels == []


def test_virtual_separator_splits_an_open_plan_face():
    from wenart.ingest.model import OpeningItem
    labels, points = blocks_at(("KITCHEN", None, (2, 2)), ("DINING", None, (6, 2)))
    merged = R.derive_rooms("L0", two_rooms(open_plan=True), labels, points, None, "p.pdf")
    assert len(merged.rooms) == 1 and merged.rooms[0]["status"] == "unverified"
    assert merged.multi_labels == [(merged.rooms[0]["id"], "Kitchen", ["DINING"])]
    sep = OpeningItem(kind="opening", width=2.4, center=(4.0, 1.4), rotation_deg=90.0, box=[0, 0, 0, 0], entity="sep",
                      evidence=B.evidence("p.pdf", "derived", 0.8, entity="sep"), virtual=True,
                      line=((4.0, 0.2), (4.0, 2.6)))
    split = R.derive_rooms("L0", two_rooms(open_plan=True), labels, points, None, "p.pdf", separators=[sep])
    assert sorted((r["label"], r["room_type"], r["status"]) for r in split.rooms) == \
        [("Dining", "dining", "verified"), ("Kitchen", "kitchen", "verified")]
    # A ready union (walls, openings and separators bridged) gives the same faces; the separators are passed with
    # it so the faces are snapped back onto the separator line (review2 dwgblender-1).
    from wenart.ingest.generic import topology as TP
    union = TP.bridged_union(two_rooms(open_plan=True), [], [sep])
    ready = R.derive_rooms("L0", two_rooms(open_plan=True), labels, points, None, "p.pdf", union=union,
                           separators=[sep])
    assert sorted(r["polygon"] == s["polygon"] for r, s in zip(ready.rooms, split.rooms)) == [True, True]


def test_rooms_split_by_a_separator_share_the_line_exactly():
    """review2 dwgblender-1: the separator strip is 4 mm wide; the two faces are snapped back onto the line, so
    their floors and ceilings meet there (no slit to the sky), with a union passed or built here."""
    from shapely.geometry import LineString, Point, Polygon

    from wenart.ingest.generic import topology as TP
    from wenart.ingest.model import OpeningItem
    labels, points = blocks_at(("KITCHEN", None, (2, 2)), ("DINING", None, (6, 2)))
    for line in (((4.0, 0.2), (4.0, 2.6)), ((4.0, 2.6), (4.0, 0.2))):
        sep = OpeningItem(kind="opening", width=2.4, center=(4.0, 1.4), rotation_deg=90.0, box=[0, 0, 0, 0],
                          entity="sep", evidence=B.evidence("p.pdf", "derived", 0.8, entity="sep"), virtual=True,
                          line=line)
        union = TP.bridged_union(two_rooms(open_plan=True), [], [sep])
        for kwargs in ({"separators": [sep]}, {"separators": [sep], "union": union}):
            result = R.derive_rooms("L0", two_rooms(open_plan=True), labels, points, None, "p.pdf", **kwargs)
            rooms = {r["label"]: r for r in result.rooms}
            kitchen, dining = Polygon(rooms["Kitchen"]["polygon"]), Polygon(rooms["Dining"]["polygon"])
            shared = kitchen.intersection(dining)
            assert shared.geom_type == "LineString" and shared.length == pytest.approx(2.4, abs=1e-6)
            assert shared.equals(LineString([(4.0, 0.2), (4.0, 2.6)]))
            assert kitchen.union(dining).area == pytest.approx(kitchen.area + dining.area)    # no overlap
            # Every point of the line is covered by both floors: no 4 mm slit.
            assert all(kitchen.buffer(1e-9).contains(Point(4.0, y)) and dining.buffer(1e-9).contains(Point(4.0, y))
                       for y in (0.25, 1.0, 2.0, 2.55))
            assert rooms["Kitchen"]["area_computed"] == pytest.approx(3.8 * 2.4 + 3.7 * 1.2)   # to x = 4.0 exactly
    # The stub's end face is untouched: the kitchen still ends at the stub (x 3.9) above y = 2.6.
    assert any(abs(p[0] - 3.9) < 1e-9 and abs(p[1] - 3.8) < 1e-9 for p in rooms["Kitchen"]["polygon"])


def test_exterior_face_is_no_room_and_unlabelled_faces_get_the_placeholder():
    labels, points = blocks_at(("GARDEN", None, (2, 2)))
    result = R.derive_rooms("L0", two_rooms(), labels, points, None, "p.pdf", unlabelled_label="Room",
                            face_type=lambda poly: ("hall", "unlabelled face touching 2 doors/openings"))
    assert len(result.rooms) == 1                                         # the garden face is not a room
    room = result.rooms[0]
    assert (room["label"], room["label_raw"], room["room_type"], room["status"]) == ("Room", None, "hall", "unverified")
    assert room["id"] == "r_L0_room" and "label_size" not in room
    assert any("has no label: unlabelled face touching 2 doors/openings" in w for w in result.warnings)
    assert result.unplaced_labels == []


def test_generic_label_outside_the_building_is_no_review_reason_but_one_on_a_wall_is():
    labels, points = blocks_at(("STUDY", None, (12, 2)), ("OFFICE", None, (4, 2)))
    result = R.derive_rooms("L0", two_rooms(), labels, points, None, "p.pdf")
    assert [t.text for t in result.unplaced_labels] == ["OFFICE"]         # on the partition: walls do not close
    assert all(r["label_raw"] is None for r in result.rooms)


def test_hall_alone_in_a_large_compact_face_is_a_living_room_and_turkish_casing():
    labels, points = blocks_at(("HALL", None, (2, 2)), ("SALON", None, (6, 2)), turkish=False)
    labels[1].turkish = True
    result = R.derive_rooms("L0", two_rooms(), labels, points, None, "p.pdf")
    rooms = {r["label"]: r for r in result.rooms}
    assert rooms["Hall"]["room_type"] == "living"                          # 13.3 m², aspect 1.03
    assert rooms["Salon"]["room_type"] == "living" and rooms["Salon"]["label_raw"] == "SALON"
    narrow = [wall((0, 0.1), (8, 0.1)), wall((0, 1.9), (8, 1.9)), wall((0.1, 0), (0.1, 2)), wall((7.9, 0), (7.9, 2))]
    labels, points = blocks_at(("HALL", None, (2, 1)))
    assert R.derive_rooms("L0", narrow, labels, points, None, "p.pdf").rooms[0]["room_type"] == "hall"
