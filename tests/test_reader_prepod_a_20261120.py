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
    from wenart.ingest import tag_grammar as TG     # 27 Nov 2026 (round 5a, R09): the one size-tag parser
    assert TG.parse("P:220/150") and TG.parse("150/150") and TG.parse("D1-90/210") and not TG.parse("SALON")


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


def test_the_wall_in_wall_check_flags_a_wall_inside_a_thicker_walls_band():
    """R09-11's machine check (RC14 wall_in_wall): any reading that still holds such a wall is flagged before a pod."""
    from wenart.reading_check import sense as SN

    b = {"levels": [{"id": "L0"}], "walls": [
        {"id": "thin", "level_id": "L0", "start": [0.0, 0.67], "end": [8.0, 0.67], "thickness": 0.23},
        {"id": "thick", "level_id": "L0", "start": [0.0, 0.79], "end": [8.0, 0.79], "thickness": 0.46}],
        "openings": [{"id": "o1", "level_id": "L0", "type": "opening", "wall_id": "thin", "center": [4.0, 0.67]}]}
    found = SN.wall_in_wall(b)
    assert [f["element_ids"] for f in found] == [["thin", "o1"]] and found[0]["severity"] == "major"
    b["walls"][0]["start"], b["walls"][0]["end"] = [0.0, 0.3], [8.0, 0.3]     # in front of it: no finding
    assert SN.wall_in_wall(b) == []


# --------------------------------------------------------------------------
# R10-P3 / P1 / P6: window size tags written as two texts; plain-layer tags over window frames
# --------------------------------------------------------------------------

def _run(text, x, y, rot=0.0, layer="TEXT", h=0.1):
    from wenart.ingest.generic.model import TextRun
    return TextRun(id=f"TEXT:{text}@{x},{y}", text=text, box=(x - 0.15, y - h / 2, x + 0.15, y + h / 2), height=h,
                   rotation_deg=rot, evidence=[{"layer": layer, "entity": f"TEXT:{text}"}])


def test_a_size_written_as_two_texts_one_over_the_other_is_one_width_over_height_tag():
    """A drawing that writes each window size as two texts ('150' over '220', '70' over '150') states width over
    height: the upper line is the width."""
    from wenart.ingest.generic import core as GC

    pairs = GC.paired_size_tags([_run("150", 2.0, 1.00), _run("220", 2.0, 1.13), _run("40", 6.0, 3.0, layer="DIM")])
    assert [t.text for t in pairs] == ["220/150"]
    # written along a vertical wall (rotated 90 degrees: 'up' is towards -x)
    pairs = GC.paired_size_tags([_run("165", 4.48, 1.0, rot=90.0), _run("210", 4.61, 1.0, rot=90.0)])
    assert [t.text for t in pairs] == ["165/210"]
    # two numbers side by side, or far apart, or on a dimension layer: no tag
    assert GC.paired_size_tags([_run("150", 2.0, 1.0), _run("150", 2.4, 1.0)]) == []
    assert GC.paired_size_tags([_run("150", 2.0, 1.0, layer="DIMV"), _run("150", 2.0, 1.13, layer="DIMV")]) == []


def test_a_plain_layer_tag_over_window_frames_makes_the_window_the_frame_lines_were_read_as_a_sliding_door():
    """real10 L-1: a 150/150 window on the window layer, its size as two texts on the text layer, its doubled frame
    lines read as a 1.44 m sliding door; with no window frames along the wall the same tag makes nothing."""
    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic.model import Stroke
    from wenart.ingest.model import OpeningItem, WallItem

    wall = WallItem(start=(0.0, 0.0), end=(6.0, 0.0), thickness=0.3, box=[0, 0, 0, 0], entity="LINE:1", evidence={})
    slider = OpeningItem(kind="door", width=1.44, center=(2.75, 0.0), rotation_deg=0.0, box=[0, 0, 0, 0],
                         entity="LINE:9", evidence={"note": "4 leaf/leaves drawn parallel to the wall without a swing "
                                                            "arc: a sliding door"}, operation="sliding")
    frames = [Stroke(id=f"LINE:f{k}", kind="line", layer="PENCERE", pts=[(2.0, y), (3.5, y)])
              for k, y in enumerate((-0.05, 0.05))]
    tags = [_run("150", 2.75, 0.45), _run("150", 2.75, 0.58)]
    ex = SimpleNamespace(notes=[])
    out = GC._window_tags(ex, "L-1", [wall], [slider], tags, 1.0, frames)
    assert out is not None and [o.kind for o in out] == ["window"]
    assert abs(out[0].width - 1.5) < 1e-6 and out[0].height == 1.5
    # the same tag with no window frames along its wall: not a window's tag
    ex = SimpleNamespace(notes=[])
    assert GC._window_tags(ex, "L-1", [wall], [slider], tags, 1.0, []) is None
    # the tag written across the wall just outside its face (rotated 90 degrees over a horizontal wall)
    across = [_run("150", 2.69, 0.28, rot=90.0), _run("150", 2.82, 0.28, rot=90.0)]
    ex = SimpleNamespace(notes=[])
    out = GC._window_tags(ex, "L-1", [wall], [slider], across, 1.0, frames)
    assert out is not None and [o.kind for o in out] == ["window"]
    # a door-high plain-layer tag stays the door tags' (never a window here)
    ex = SimpleNamespace(notes=[])
    assert GC._window_tags(ex, "L-1", [wall], [slider], [_run("90", 2.75, 0.58), _run("210", 2.75, 0.45)], 1.0,
                           frames) is None
    # a low tag (a transom or vent, '150/70') over an untyped gap keeps the gap (real07's garage door); a window-high
    # one ('150/150') types it as its window (real10's bay windows)
    gap = OpeningItem(kind="opening", width=1.5, center=(2.75, 0.0), rotation_deg=0.0, box=[0, 0, 0, 0],
                      entity="LINE:7", evidence={})
    ex = SimpleNamespace(notes=[])
    assert GC._window_tags(ex, "L0", [wall], [gap], [_run("150", 2.75, 0.58), _run("70", 2.75, 0.45)], 1.0,
                           frames) is None
    ex = SimpleNamespace(notes=[])
    out = GC._window_tags(ex, "L0", [wall], [gap], tags, 1.0, frames)
    assert out is not None and [o.kind for o in out] == ["window"]


def test_the_checks_flag_an_untyped_opening_over_window_frames_and_a_two_text_tag_with_no_window():
    """The machine checks of R10-P1 / P3 (RC11): an untyped opening with window frames drawn across it, and a W/H tag
    written as two texts with no opening of its width at its gap."""
    from wenart.reading_check import crossdoc as CD

    walls = [{"id": "w1", "level_id": "L0", "start": [0.0, 0.0], "end": [6.0, 0.0], "thickness": 0.3}]
    ops = [{"id": "o1", "level_id": "L0", "type": "opening", "width": 2.1, "center": [3.0, 0.0], "wall_id": "w1"}]
    page = SimpleNamespace(strokes=[SimpleNamespace(pts=[(1.95, y), (4.05, y)], layer="PENCERE", arc=None)
                                    for y in (-0.05, 0.05)],
                           texts=[_run("210", 3.0, 0.58), _run("150", 3.0, 0.45)])
    found = CD.framed_openings("L0", page, None, walls, ops)
    assert [f["element_ids"] for f in found] == [["o1"]]
    page.strokes = []
    assert CD.framed_openings("L0", page, None, walls, ops) == []
    tags = CD.size_tags(CD.paired_texts(page, None))
    assert [(t["w"], t["h"]) for t in tags] == [(2.1, 1.5)]
    assert CD.rc11("L0", tags, walls, []) and not CD.rc11("L0", tags, walls, [dict(ops[0], type="window")])



# --------------------------------------------------------------------------
# R10-P2: window frame lines inside a wall band between two jambs
# --------------------------------------------------------------------------

def _framed_plan(tag=("165", "210")):
    from wenart.ingest.generic.model import Stroke
    from wenart.ingest.model import WallItem

    def wall(a, b, t):
        return WallItem(start=a, end=b, thickness=t, box=[0, 0, 0, 0], entity=f"LINE:{a}{b}", evidence={})
    walls = [wall((0.0, 0.0), (6.0, 0.0), 0.46), wall((6.0, 0.0), (6.0, 4.0), 0.2), wall((6.0, 4.0), (0.0, 4.0), 0.2),
             wall((0.0, 4.0), (0.0, 0.0), 0.2)]
    st = []
    for k, y in enumerate((0.03, 0.055, 0.08, 0.105)):                   # the frame and sash lines in the band
        st.append(Stroke(id=f"LINE:f{k}", kind="line", layer="PENCERE", pts=[(2.0, y), (3.65, y)]))
    for k, x in enumerate((2.0, 3.65)):                                 # the wall-layer jambs across the band
        st.append(Stroke(id=f"LINE:j{k}", kind="line", layer="DUVAR", pts=[(x, -0.23), (x, 0.23)]))
    for k, y in enumerate((-0.23, 0.23)):                               # the plaster lines straight across the bay
        st.append(Stroke(id=f"LINE:p{k}", kind="line", layer="SIVA", pts=[(2.0, y), (3.65, y)]))
    st.append(Stroke(id="LINE:lead", kind="line", layer="TEXT", pts=[(2.8, 0.85), (2.8, 0.06)]))
    texts = [_run(tag[0], 2.76, 0.95, rot=90.0), _run(tag[1], 2.89, 0.95, rot=90.0)]
    return walls, st, texts


def test_window_frames_between_two_jambs_inside_a_wall_band_are_a_window_sized_by_its_leader_tag():
    """real10 L0-L6: each kitchen's window drawn as frame and sash lines between two jambs, a '165' over '210' tag with a
    leader line, two plaster lines straight across the bay; no opening was read."""
    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic.model import Stroke
    from wenart.ingest.model import OpeningItem

    walls, st, texts = _framed_plan()
    out = GC._framed_windows(SimpleNamespace(notes=[]), "L0", walls, [], st, texts, 1.0)
    assert out is not None and len(out) == 1 and out[0].kind == "window"
    assert abs(out[0].width - 1.65) < 1e-6 and out[0].height == 2.1 and out[0].sill == 0.0
    # a door's size on frames between jambs 0.8 m apart: a glazed door
    walls, st, texts = _framed_plan(tag=("80", "210"))
    st = [x for x in st if not x.id.startswith("LINE:f") and x.id != "LINE:j1"]
    st += [Stroke(id=f"LINE:g{k}", kind="line", layer="PENCERE", pts=[(2.0, y), (2.8, y)])
           for k, y in enumerate((0.03, 0.08))]
    st.append(Stroke(id="LINE:j9", kind="line", layer="DUVAR", pts=[(2.8, -0.23), (2.8, 0.23)]))
    out = GC._framed_windows(SimpleNamespace(notes=[]), "L0", walls, [], st, texts, 1.0)
    assert out is not None and out[0].kind == "door" and abs(out[0].width - 0.8) < 1e-6
    # an opening already read there: nothing new; frames on one line only: no window
    walls, st, texts = _framed_plan()
    read = OpeningItem(kind="window", width=1.6, center=(2.8, 0.0), rotation_deg=0.0, box=[0, 0, 0, 0], entity="x",
                       evidence={})
    assert GC._framed_windows(SimpleNamespace(notes=[]), "L0", walls, [read], st, texts, 1.0) is None
    one = [x for x in st if x.id not in ("LINE:f1", "LINE:f2", "LINE:f3")]
    assert GC._framed_windows(SimpleNamespace(notes=[]), "L0", walls, [], one, texts, 1.0) is None


def test_the_check_flags_window_frames_inside_a_facade_wall_with_no_opening():
    """R10-P2's machine check (RC11 framed_walls)."""
    from wenart.reading_check import crossdoc as CD

    _walls, st, _texts = _framed_plan()
    page = SimpleNamespace(strokes=st, texts=[])
    walls = [{"id": "w_s", "level_id": "L0", "start": [0.0, 0.0], "end": [6.0, 0.0], "thickness": 0.46,
              "exterior": True}]
    found = CD.framed_walls("L0", page, None, walls, [])
    assert [f["element_ids"] for f in found] == [["w_s"]]
    win = {"id": "win", "type": "window", "width": 1.65, "center": [2.825, 0.0], "wall_id": "w_s"}
    assert CD.framed_walls("L0", page, None, walls, [win]) == []



# --------------------------------------------------------------------------
# real21 areas: RC3 names the cause when a storey's rooms sit far under their area texts
# --------------------------------------------------------------------------

def test_rc3_names_why_a_storeys_rooms_sit_far_under_their_area_texts():
    """real21: the ground floor's rooms sat 15-25 % under their area texts while the drawn storey above matched them
    (the ground floor built to another footprint); gross area texts (wall halves included) are named, not 'fixed'."""
    from shapely.geometry import box as sbox

    from wenart import reading_check as RC

    def room(lid, k, poly, area):
        return {"id": f"r_{lid}_{k}", "level_id": lid, "label": f"Oda {k}", "area_label": area,
                "polygon": [list(c) for c in poly.exterior.coords[:-1]]}
    full = [sbox(4.0 * k, 0.0, 4.0 * k + 3.0, 4.0) for k in range(4)]            # 12 m2 each
    walls = [{"id": f"w{k}", "level_id": lid, "start": [0, 0], "end": [1, 0], "thickness": 0.2}
             for lid in ("L0", "L1") for k in range(3)]
    b = {"rooms": [room("L1", k, p, 12.0) for k, p in enumerate(full)]
         + [room("L0", k, sbox(*p.bounds[:2], p.bounds[2], 3.0), 12.0) for k, p in enumerate(full)], "walls": walls}
    found = RC.storey_area_causes(b)
    assert [f["level_id"] for f in found] == ["L0"] and "the same rooms on L1 match" in found[0]["message"]
    # gross texts: every room 0.1 m (half a 0.2 m wall) short on each side, on every storey
    gross = {"rooms": [room(lid, k, p, round(p.buffer(0.1, join_style=2).area, 2))
                       for lid in ("L0", "L1") for k, p in enumerate(full)], "walls": walls}
    found = RC.storey_area_causes(gross)
    assert found == [] or all("gross" in f["message"] for f in found)
    small = {"rooms": [room("L0", k, sbox(*p.bounds[:2], p.bounds[2] - 0.6, 3.4), 12.0) for k, p in enumerate(full)],
             "walls": [dict(w, thickness=0.6) for w in walls]}
    found = RC.storey_area_causes(small)
    assert found and "gross" in found[0]["message"] and "read thick" in found[0]["message"]
