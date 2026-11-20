"""The reader fixes of the pre-pod check of 20 Nov 2026 (reader A), each a general rule with the project that showed it
as its test case only (user rule of 26 Oct 2026: "fix should be general ... don't ever forget that")."""
from __future__ import annotations

from types import SimpleNamespace

from shapely.geometry import Polygon, box


# --------------------------------------------------------------------------
# R09-1: a labelled room's mirror twin closed from its drawn frames; the shell checks
# --------------------------------------------------------------------------

def _text(s: str, x: float, y: float):
    return SimpleNamespace(text=s, box=(x - 0.3, y - 0.05, x + 0.3, y + 0.05))


def test_a_mirror_twin_face_is_kept_only_when_it_mirrors_its_twin_and_the_drawing_marks_a_room_there():
    """real09 L0-L2: the left salon (its facade drawn as frames tagged 'P:220/150', 'P:150/150' and a 'K:80/240' balcony
    door) stayed open because the missing salon made the shell 89 % symmetric, under the 90 % of the mirror fixes."""
    from wenart.ingest.generic import core as GC

    axis = ("x", 10.0)
    twin = box(14.0, 0.0, 18.5, 5.0)
    face = box(1.5, 0.0, 6.0, 5.0)                     # the mirror of the twin about x = 10
    tags = [_text("P:220/150", 1.0, 2.5), _text("K:80/240", 3.0, -0.6)]
    why, ev = GC.twin_evidence(face, twin, axis, tags, [], [], [], [])
    assert why is None and any("P:220/150" in e for e in ev) and "100%" in ev[0]
    # the same face with nothing drawn that says a room stands there: not closed
    why, ev = GC.twin_evidence(face, twin, axis, [_text("BALKON", 3.0, 2.0)], [], [], [], [])
    assert why and "marks no room" in why and ev == []
    # a tag inside another closed face is that room's
    why, _ev = GC.twin_evidence(face, twin, axis, [_text("P:150/150", 6.5, 2.5)], [], [], [], [box(6.2, 0.0, 9.0, 5.0)])
    assert why
    # a face that is not its twin's mirror: not closed
    why, _ev = GC.twin_evidence(box(1.5, 0.0, 4.0, 2.0), twin, axis, tags, [], [], [], [])
    assert why and "overlaps the twin's face" in why
    # a drawn door on its outline is evidence too
    door = SimpleNamespace(kind="door", virtual=False, center=(6.0, 2.5))
    why, ev = GC.twin_evidence(face, twin, axis, [], [door], [], [], [])
    assert why is None and any("door" in e for e in ev)
    assert GC.OPENING_TAG_RE.match("P:220/150") and GC.OPENING_TAG_RE.match("150/150") \
        and GC.OPENING_TAG_RE.match("D1-90/210") and not GC.OPENING_TAG_RE.match("SALON")


def test_a_room_closed_as_a_mirror_twin_takes_its_twins_label_and_type():
    """real09 L2: the left kitchen is drawn 2.44 m wide against its twin's 1.84 m, too far off for the mirror-label
    rule; the reader closed it as the twin of MUTFAK, so it takes that label, inferred with the axis and evidence."""
    from wenart.ingest import pipeline as P

    warned = []
    build = SimpleNamespace(warn=warned.append)
    ex = SimpleNamespace(report={"units_to_m": 1.0, "mirror_twins": {
        "axis": ["x", 10.0], "rooms": [{"label": "MUTFAK", "seed": [3.0, 2.0], "of": [17.0, 2.0],
                                        "evidence": ["size tags P:150/150"]}]}},
        transform_to_building=[1.0, 0.0, 0.0, 0.0, 1.0, 0.0])
    blank = {"id": "r_L2_oda", "level_id": "L2", "label": "Oda", "label_raw": None, "room_type": "hall",
             "polygon": [[1.0, 0.0], [5.0, 0.0], [5.0, 4.0], [1.0, 4.0]]}
    named = {"id": "r_L2_mutfak", "level_id": "L2", "label": "Mutfak", "label_raw": "MUTFAK", "room_type": "kitchen",
             "polygon": [[15.0, 0.0], [19.0, 0.0], [19.0, 4.0], [15.0, 4.0]]}
    P._mirror_twin_rooms(build, "L2", ex, [blank, named])
    assert blank["label"] == "Mutfak" and blank["room_type"] == "kitchen" and blank["label_raw"] is None
    assert blank["label_inferred"]["method"] == "mirror" and blank["label_inferred"]["rule"] == "mirror_twin"
    assert blank["label_inferred"]["of"] == "r_L2_mutfak" and warned
    # the mirror-label rule leaves it alone (no second naming)
    from wenart.ingest import twins as TW
    before = dict(blank["label_inferred"])
    TW.mirror_labels([blank, named], [])
    assert blank["label_inferred"] == before


def _sq(x0, y0, x1, y1):
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _shell_building(missing: bool = True) -> dict:
    """Three storeys of two mirrored flats about x = 10 (rooms 0-10 and 10-20, 0-8); the middle storey misses the left
    front room (0-5 x 0-5) when ``missing``; a terrace on the top storey over that corner; a door on the middle storey's
    front wall at x 7."""
    levels = [{"id": f"L{i}", "elevation": 3.0 * i, "order": i, "base_level_id": None} for i in range(3)]
    rooms, walls = [], []
    for i in range(3):
        lid = f"L{i}"
        parts = [("a", _sq(5, 0, 10, 5)), ("b", _sq(0, 5, 10, 8)), ("c", _sq(10, 0, 15, 5)),
                 ("d", _sq(15, 0, 20, 5)), ("e", _sq(10, 5, 20, 8))]
        if not (missing and i == 1):
            parts.append(("f", _sq(0, 0, 5, 5)))
        for k, poly in parts:
            room = {"id": f"r_{lid}_{k}", "level_id": lid, "label": "Oda", "room_type": "bedroom", "polygon": poly}
            if k == "d":
                room["label_inferred"] = {"method": "mirror", "of": f"r_{lid}_f", "axis": ["x", 10.0]}
            rooms.append(room)
    walls.append({"id": "w_L1_front", "level_id": "L1", "start": [5.0, 0.0], "end": [10.0, 0.0], "thickness": 0.2,
                  "exterior": True})
    openings = [{"id": "d_L1_x", "level_id": "L1", "type": "door", "width": 0.9, "center": [7.0, 0.0],
                 "wall_id": "w_L1_front"}]
    site = {"outdoor_spaces": [{"id": "os_L2_t", "level_id": "L2", "kind": "terrace", "label": "TERAS",
                                "polygon": _sq(0, 0, 5, 5)}]}
    if missing:
        rooms = [r for r in rooms if not (r["level_id"] == "L2" and r["id"].endswith("_f"))]
    return {"levels": levels, "rooms": rooms, "walls": walls, "openings": openings, "site": site}


def test_the_shell_checks_find_a_missing_twin_a_terrace_on_nothing_a_room_with_no_floor_above_and_a_door_to_the_air():
    """R09-1 post-checks: every storey's outline has no twin-sized notch, every room is under the storey above, every
    terrace stands on a built storey, every outer door above the ground has a balcony, a terrace or a room behind it."""
    from wenart.reading_check import sense as SN

    b = _shell_building(missing=True)
    notch = SN.twin_notch(b)
    assert [f["level_id"] for f in notch] == ["L1"] and "mirror" in notch[0]["message"]
    assert [f["level_id"] for f in SN.terrace_support(b)] == ["L2"]
    cover = SN.slab_cover(b)
    assert any(f["element_ids"] == ["r_L0_f"] for f in cover)
    door = SN.door_to_air(b)
    assert [f["element_ids"] for f in door] == [["d_L1_x"]]
    # a balcony behind the door: no finding
    b["site"]["outdoor_spaces"].append({"id": "os_L1_b", "level_id": "L1", "kind": "balcony",
                                        "polygon": _sq(6, -1.5, 8, -0.1)})
    assert SN.door_to_air(b) == []
    # the whole building: none of the shell findings
    full = _shell_building(missing=False)
    full["site"]["outdoor_spaces"] = []
    assert SN.twin_notch(full) == [] and SN.slab_cover(full) == [] and SN.terrace_support(full) == []
    for rule in ("twin_notch", "slab_cover", "terrace_support", "door_to_air"):
        assert rule in SN.RULES


# --------------------------------------------------------------------------
# R09-11: a thinner wall inside the band of thicker collinear walls
# --------------------------------------------------------------------------

def test_a_thin_wall_inside_the_band_of_two_thicker_walls_is_not_built_and_its_gaps_go_to_them():
    """real09 L0-L2: a 0.23 m wall (the outer plaster line paired with a plaster line through the piers) lay inside the
    0.46 m front walls w_006 / w_007, 55 % and 41 % of it each; its 2.9 m gaps became 2.9 m windows cut through the real
    wall beside the drawn 1.5 m ones."""
    from wenart.ingest.generic import twin_walls as TWW

    ev = [{"method": "vector"}]
    b = {"walls": [
        {"id": "w5", "level_id": "L0", "start": [5.0, 0.674], "end": [16.0, 0.674], "thickness": 0.23, "evidence": ev},
        {"id": "w6", "level_id": "L0", "start": [5.0, 0.79], "end": [10.6, 0.79], "thickness": 0.46, "evidence": ev},
        {"id": "w7", "level_id": "L0", "start": [10.87, 0.79], "end": [16.0, 0.79], "thickness": 0.46, "evidence": ev},
        {"id": "w9", "level_id": "L0", "start": [5.0, 3.0], "end": [16.0, 3.0], "thickness": 0.1, "evidence": ev}],
        "openings": [
            {"id": "o1", "level_id": "L0", "type": "opening", "width": 2.9, "center": [9.08, 0.674], "wall_id": "w5"},
            {"id": "o2", "level_id": "L0", "type": "opening", "width": 2.9, "center": [12.18, 0.674], "wall_id": "w5"},
            {"id": "d1", "level_id": "L0", "type": "door", "width": 1.5, "center": [9.08, 0.79], "wall_id": "w6"},
            {"id": "x1", "level_id": "L0", "type": "window", "width": 1.0, "center": [14.5, 0.674], "wall_id": "w5"}]}
    assert TWW.merge_twin_walls(b) == ["w5"]
    assert [w["id"] for w in b["walls"]] == ["w6", "w7", "w9"]
    merged = {o["id"]: o["merged_into"] for o in b["openings_merged"]}
    assert merged == {"o1": "d1"}                      # the gap read over the drawn 1.5 m opening
    by = {o["id"]: o for o in b["openings"]}
    assert by["o2"]["wall_id"] == "w7" and by["x1"]["wall_id"] == "w7"
    assert "band" in b["walls_merged"][0]["corrected_by_ai"]["reason"]
    # a thin wall in front of a thicker one (its outer face outside the band) stays
    b2 = {"walls": [
        {"id": "a", "level_id": "L0", "start": [0.0, 0.0], "end": [6.0, 0.0], "thickness": 0.1},
        {"id": "b", "level_id": "L0", "start": [0.0, 0.2], "end": [6.0, 0.2], "thickness": 0.3}], "openings": []}
    assert TWW.merge_twin_walls(b2) == []
