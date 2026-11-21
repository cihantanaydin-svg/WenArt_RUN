"""Structural rules of 20 Nov 2026 (the user: "focus on real structural problems"; every fix general): synthetic cases,
none taken from a project.

- a level the reading adds after the variants were written is built (``views.building_variants``) and RC1 names a
  level no build takes (``views.levels_not_built``);
- a lower roof is a door's landing only for the storey right above it (``architect.lower_roof_landing``); RC17 names
  an upper door into the air and a slab open inside its storey's walls (``reading_check.structure``);
- R35: a wall drawn at an angle stays at its angle (``walls.angled_piece``, ``angled_face_walls``,
  ``join_angled_ends``; ``openings.angled_frames``) and RC17 names one built in axis steps.
"""
from __future__ import annotations

import math

from wenart import views as V


def _level(lid, elev, **kw):
    return dict({"id": lid, "label": lid, "elevation": elev, "variant": "base"}, **kw)


def _variants_building():
    return {"levels": [_level("L-1", -3.0, kind="basement"), _level("L0", 0.0), _level("L1", 3.0),
                       _level("L1b", 3.0, base_level_id="L1", variant="alt")],
            "variants": [{"id": "base", "base": True, "levels": ["L0", "L1"], "changes": []},
                         {"id": "alt", "base": False, "levels": ["L0", "L1b"],
                          "changes": [{"replaces": "L1", "level_id": "L1b"}]}],
            "walls": [{"id": "w1", "level_id": "L-1", "start": [0, 0], "end": [4, 0], "thickness": 0.2}],
            "openings": [], "rooms": []}


def test_a_level_added_after_the_variants_is_built():
    b = _variants_building()
    base = V.variant_record(b, "base")
    assert base["levels"] == ["L-1", "L0", "L1"] and base["levels_added"] == ["L-1"]
    assert V.variant_record(b, "alt")["levels"] == ["L0", "L1b"]          # an alternative variant is unchanged
    view = V.variant_building(b, "base")
    assert [lv["id"] for lv in view["levels"]] == ["L-1", "L0", "L1"] and view["walls"]
    assert V.levels_not_built(b) == []
    assert b["variants"][0]["levels"] == ["L0", "L1"]                      # the building itself is not changed


def test_rc1_names_a_level_no_build_takes():
    b = _variants_building()
    b["levels"].append(_level("L2x", 6.0, variant="other"))                 # a variant id no record carries
    left = V.levels_not_built(b)
    assert [x["id"] for x in left] == ["L2x"] and "lists it in no variant" in left[0]["reason"]


# ------------------------------------------------------------------------------------------- a door into the air
def _square(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def test_a_lower_roof_is_a_landing_only_for_the_storey_right_above_it():
    from wenart.blender import architect as A
    levels = [_level("L0", 0.0), _level("L1", 3.0), _level("L2", 6.0)]
    outlines = {"L0": _square(0, 0, 10, 6), "L1": _square(0, 0, 6, 6), "L2": _square(0, 0, 6, 6)}
    probe = (8.0, 3.0)                                # over L0's roof, outside L1 and L2
    assert A.lower_roof_landing(levels, levels[1], probe, outlines)["id"] == "L0"
    assert A.lower_roof_landing(levels, levels[2], probe, outlines) is None      # 6 m above that roof: the air
    assert A.lower_roof_landing(levels, levels[0], probe, outlines) is None


def _box_walls(lid, x0, y0, x1, y1, t=0.2):
    pts = _square(x0, y0, x1, y1)
    return [{"id": f"w_{lid}_{k}", "level_id": lid, "start": list(pts[k]), "end": list(pts[(k + 1) % 4]),
             "thickness": t} for k in range(4)]


def _tower(balcony=False, notch=False):
    """L0 10 x 6 m, L1 and L2 6 x 6 m over its west part; a door in the east wall (x = 6) of L1 and of L2."""
    levels = [_level("L0", 0.0, order=0), _level("L1", 3.0, order=1), _level("L2", 6.0, order=2)]
    walls = _box_walls("L0", 0, 0, 10, 6) + _box_walls("L1", 0, 0, 6, 6) + _box_walls("L2", 0, 0, 6, 6)
    if notch:                                         # L2's north wall steps in around a notch open to the sky
        walls = [w for w in walls if w["id"] != "w_L2_2"] + [
            {"id": f"w_L2_n{k}", "level_id": "L2", "start": list(a), "end": list(b), "thickness": 0.2}
            for k, (a, b) in enumerate([((6, 6), (4, 6)), ((4, 6), (4, 3)), ((4, 3), (2, 3)), ((2, 3), (2, 6)),
                                        ((2, 6), (0, 6))])]
    openings = [{"id": "d_up", "level_id": "L2", "type": "door", "wall_id": "w_L2_1", "center": [6.0, 3.0],
                 "width": 0.9},
                {"id": "d_l1", "level_id": "L1", "type": "door", "wall_id": "w_L1_1", "center": [6.0, 3.0],
                 "width": 0.9}]
    site = {"outdoor_spaces": [{"id": "os_b", "level_id": "L2", "kind": "balcony",
                                "polygon": _square(6.0, 2.0, 7.5, 4.0)}] if balcony else []}
    return {"levels": levels, "walls": walls, "openings": openings, "rooms": [], "site": site}


def test_rc17_names_an_upper_door_into_the_air_and_not_one_onto_a_balcony_or_the_roof_below():
    from wenart.reading_check import structure as ST
    found = ST.doors_into_air(_tower())
    assert [f["element_ids"] for f in found] == [["d_up"]]            # d_l1 steps onto L0's roof
    assert found[0]["rule"] == "door_into_air" and found[0]["structural"]
    assert ST.doors_into_air(_tower(balcony=True)) == []


def test_rc17_names_a_slab_open_inside_a_storeys_walls():
    from wenart.reading_check import structure as ST
    assert ST.slabs_beyond_walls(_tower()) == []                      # L0's roof beside L1 is outside L1's walls
    found = ST.slabs_beyond_walls(_tower(notch=True))
    assert len(found) == 1 and found[0]["level_id"] == "L2" and found[0]["rule"] == "slab_beyond_walls"


# ------------------------------------------------------------------------------------------- R35: an angled wall
def test_rc17_names_a_drawn_angled_wall_built_in_axis_steps():
    from wenart.reading_check import structure as ST
    a, b = (0.0, 5.0), (8.0, 7.3)                                     # 16 degrees off the plan's axes
    segs = [(a, b), ((0.06, 4.81), (8.06, 7.11)), ((0, 0), (8, 0)), ((0, 0), (0, 5))]
    axis = [{"start": [0, 0], "end": [8, 0], "thickness": 0.2}, {"start": [0, 0], "end": [0, 5], "thickness": 0.2},
            {"start": [8, 0], "end": [8, 7.3], "thickness": 0.2}]
    stubs = [{"start": [x, 5.0 + 0.2875 * x], "end": [x + 1.0, 5.0 + 0.2875 * x], "thickness": 0.2}
             for x in range(8)]
    found = ST.angled_walls_straight(segs, axis + stubs, "L1")
    assert len(found) == 1 and found[0]["rule"] == "angled_wall_straight"
    slanted = [{"start": [0.03, 4.9], "end": [8.03, 7.2], "thickness": 0.2}]
    assert ST.angled_walls_straight(segs, axis + slanted, "L1") == []


def test_r35_an_angled_band_is_one_wall_at_its_angle():
    from wenart.ingest.generic import walls as W
    t, ang = 0.2, math.radians(16.0)
    ux, uy, nx, ny = math.cos(ang), math.sin(ang), -math.sin(ang), math.cos(ang)
    band = [(0, 0), (5 * ux, 5 * uy), (5 * ux + t * nx, 5 * uy + t * ny), (t * nx, t * ny)]
    piece = W.angled_piece(band, 0.0)
    assert piece is not None and abs(piece["angle_deg"] - 16.0) < 0.01 and abs(piece["thickness"] - t) < 1e-6
    assert abs(math.dist(piece["start"], piece["end"]) - 5.0) < 1e-6
    assert W.angled_piece(band, 16.0) is None                         # on the plan's own (turned) axes
    flat = [(0, 0), (5, 0.05), (5, 0.25), (0, 0.2)]                   # 0.6 degrees: an axis wall
    assert W.angled_piece(flat, 0.0) is None


def test_r35_a_wall_end_short_of_an_angled_wall_runs_on_to_it():
    from wenart.ingest.generic import walls as W
    from wenart.ingest.model import WallItem
    slanted = WallItem(start=(0.0, 5.0), end=(8.0, 7.3), thickness=0.2, box=[], entity="s", evidence={})
    post = WallItem(start=(4.0, 0.0), end=(4.0, 6.0), thickness=0.1, box=[], entity="p", evidence={})   # 0.15 short
    far = WallItem(start=(6.0, 0.0), end=(6.0, 5.0), thickness=0.1, box=[], entity="f", evidence={})    # 1.7 m short
    moved = W.join_angled_ends([slanted, post, far], [slanted])
    assert moved == 1 and abs(post.end[1] - (5.0 + 2.3 / 8.0 * 4.0)) < 1e-3 and far.end == (6.0, 5.0)


def test_r35_an_angled_wall_direction_gets_its_own_frame():
    from wenart.ingest.generic import openings as O
    from wenart.ingest.model import WallItem

    def wall(a, b, t=0.2):
        return WallItem(start=a, end=b, thickness=t, box=[], entity="w", evidence={})
    walls = [wall((0, 0), (8, 0)), wall((0, 0), (0, 5)), wall((8, 0), (8, 7.3)), wall((0, 5), (8, 7.3))]
    assert [round(a, 1) for a in O.angled_frames(walls, 0.0)] == [16.0]
    assert O.angled_frames(walls[:3], 0.0) == []


def _slanted_face_plan():
    """An 8 m house whose north wall is drawn 16 degrees off the plan's axes, its walls drawn as face lines (one
    stroke per face, 0.20 m outer walls, a 0.10 m inner wall with a door gap), two labelled rooms (synthetic)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    import _real01_page as R
    from wenart.ingest.generic.model import TextRun

    def on(layer, strokes):
        for st in strokes:
            st.layer = layer
        return strokes

    def top(x):                                      # the inner face of the slanted wall
        return 4.8078 + (x - 0.0553) * 2.3 / 8.0
    faces = [R.stroke([(0, 0), (8, 0), (8, 7.3), (0, 5)], closed=True),
             R.stroke([(0.2, 0.2), (3.95, 0.2)]), R.stroke([(4.05, 0.2), (7.8, 0.2)]),
             R.stroke([(0.2, top(0.2)), (3.95, top(3.95))]), R.stroke([(4.05, top(4.05)), (7.8, top(7.8))]),
             R.stroke([(0.2, 0.2), (0.2, top(0.2))]), R.stroke([(7.8, 0.2), (7.8, top(7.8))]),
             R.stroke([(3.95, 0.2), (3.95, 1.0), (4.05, 1.0), (4.05, 0.2)]),
             R.stroke([(3.95, top(3.95)), (3.95, 1.9), (4.05, 1.9), (4.05, top(4.05))])]
    door = [R.arc((4.0, 1.0), 0.9, 90, 180, prefix="door")]
    strokes = on("W1", faces) + on("KAPI", door)
    runs = [TextRun(id="t1", text="SALON", box=(1.4, 2.4, 2.4, 2.6), height=0.2),
            TextRun(id="t2", text="YATAK ODASI", box=(5.2, 2.4, 6.8, 2.6), height=0.2)]
    return R.synthetic_page(strokes, runs)


def test_r35_a_face_drawn_angled_wall_is_read_at_its_angle_and_closes_its_rooms():
    from shapely.geometry import Point

    from wenart.ingest.generic import openings as O
    from wenart.ingest.generic import topology as TP
    from wenart.ingest.generic import walls as W
    page = _slanted_face_plan()
    prims = W.wall_primitives(page, 1.0)
    prims, _choice = W.face_pair_walls(page, 1.0, prims)
    mask = W.wall_mask(page, prims, 1.0)
    ids = {i for p in prims for i in p.stroke_ids}
    rest = [s for s in page.strokes if s.id not in ids]
    walls, info = W.walls_from_mask(mask, rest, "test.pdf", 1)
    angled = [w for w in walls
              if 10.0 < math.degrees(math.atan2(w.end[1] - w.start[1], w.end[0] - w.start[0])) % 90 < 20.0]
    assert info.get("angled_walls", 0) >= 1 and sum(math.dist(w.start, w.end) for w in angled) > 6.0
    assert all(abs(w.thickness - 0.2) < 0.011 for w in angled)
    walls2, openings, _, _ = O.gaps_and_openings(walls, rest, "test.pdf", 1)
    faces = TP.faces(walls2, openings)
    for anchor in ((1.9, 2.5), (6.0, 2.5), (2.0, 5.2), (7.0, 6.6)):      # the last two right under the angled wall
        assert sum(f.contains(Point(anchor)) for f in faces) == 1, anchor
    assert [o.kind for o in openings] == ["door"]


def _recessed_balcony_plan():
    """The slanted house of ``_slanted_face_plan`` with a balcony recessed into its angled facade (x 1.2-2.8, its back
    wall at y 4.0-4.2 with a 0.9 m door into the living room) and the label BALKON in the recess (synthetic)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    import _real01_page as R
    from wenart.ingest.generic.model import TextRun

    def on(layer, strokes):
        for st in strokes:
            st.layer = layer
        return strokes

    def top(x):
        return 4.8078 + (x - 0.0553) * 2.3 / 8.0
    faces = [R.stroke([(2.45, 4.2), (2.8, 4.2), (2.8, 5.805), (8, 7.3), (8, 0), (0, 0), (0, 5), (1.2, 5.345),
                       (1.2, 4.2), (1.55, 4.2)]),
             R.stroke([(0.2, 0.2), (3.95, 0.2)]), R.stroke([(4.05, 0.2), (7.8, 0.2)]),
             R.stroke([(0.2, top(0.2)), (1.0, top(1.0))]), R.stroke([(3.0, top(3.0)), (3.95, top(3.95))]),
             R.stroke([(4.05, top(4.05)), (7.8, top(7.8))]),
             R.stroke([(0.2, 0.2), (0.2, top(0.2))]), R.stroke([(7.8, 0.2), (7.8, top(7.8))]),
             R.stroke([(1.0, top(1.0)), (1.0, 4.0), (1.55, 4.0)]), R.stroke([(2.45, 4.0), (3.0, 4.0), (3.0, top(3.0))]),
             R.stroke([(1.55, 4.0), (1.55, 4.2)]), R.stroke([(2.45, 4.0), (2.45, 4.2)]),
             R.stroke([(3.95, 0.2), (3.95, 1.0), (4.05, 1.0), (4.05, 0.2)]),
             R.stroke([(3.95, top(3.95)), (3.95, 1.9), (4.05, 1.9), (4.05, top(4.05))])]
    doors = [R.arc((4.0, 1.0), 0.9, 90, 180, prefix="door"), R.arc((1.55, 4.0), 0.9, 270, 360, prefix="door")]
    strokes = on("W1", faces) + on("KAPI", doors)
    runs = [TextRun(id="t1", text="SALON", box=(1.4, 2.4, 2.4, 2.6), height=0.2),
            TextRun(id="t2", text="YATAK ODASI", box=(5.2, 2.4, 6.8, 2.6), height=0.2),
            TextRun(id="t3", text="BALKON", box=(1.6, 4.8, 2.4, 5.0), height=0.2)]
    return R.synthetic_page(strokes, runs), [(2.0, 4.9)]


def test_r35_a_balcony_recessed_into_an_angled_facade_stays_open_with_its_door():
    from shapely.geometry import Point

    from wenart.ingest.generic import openings as O
    from wenart.ingest.generic import topology as TP
    from wenart.ingest.generic import walls as W
    page, outdoor = _recessed_balcony_plan()
    prims = W.wall_primitives(page, 1.0)
    prims, _choice = W.face_pair_walls(page, 1.0, prims)
    mask = W.wall_mask(page, prims, 1.0)
    ids = {i for p in prims for i in p.stroke_ids}
    rest = [s for s in page.strokes if s.id not in ids]
    walls, _info = W.walls_from_mask(mask, rest, "test.pdf", 1)
    walls2, openings, log, _ = O.gaps_and_openings(walls, rest, "test.pdf", 1, outdoor_points=outdoor)
    mouth = Point(2.0, 5.575)                                         # the angled line across the recess
    assert not any(TP.wall_polygon(w).contains(mouth) for w in walls2)
    assert not any(math.dist(o.center, (2.0, 5.575)) < 0.8 for o in openings)
    assert any("recessed outdoor space" in str(e.get("note")) for e in log)
    faces = TP.faces(walls2, openings)
    assert not any(f.contains(Point(2.0, 4.9)) for f in faces)        # the balcony is outside, no room
    assert sum(f.contains(Point(0.5, 4.9)) for f in faces) == 1       # the living room under the angled wall
    assert any(o.kind == "door" and math.dist(o.center, (2.0, 4.1)) < 0.3 for o in openings)


def _cut_span_plan(frame=True, jambs=True):
    """An 8 x 5 m house drawn as face lines on a wall layer; its inner wall (x 3.95-4.05) has a 0.9 m door span at
    y 1.0-1.9 closed by two lines on the wall's cut layer, framed by jamb lines across the wall, with the door's frame
    profiles on a door layer (no swing arc) and its size tag '90/210' beside it (synthetic)."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    import _real01_page as R
    from wenart.ingest.generic.model import TextRun

    def on(layer, strokes):
        for st in strokes:
            st.layer = layer
        return strokes
    faces = [R.stroke([(0, 0), (8, 0), (8, 5), (0, 5)], closed=True),
             R.stroke([(0.2, 0.2), (3.95, 0.2)]), R.stroke([(4.05, 0.2), (7.8, 0.2)]),
             R.stroke([(0.2, 4.8), (3.95, 4.8)]), R.stroke([(4.05, 4.8), (7.8, 4.8)]),
             R.stroke([(0.2, 0.2), (0.2, 4.8)]), R.stroke([(7.8, 0.2), (7.8, 4.8)]),
             R.stroke([(3.95, 0.2), (3.95, 1.0)]), R.stroke([(4.05, 0.2), (4.05, 1.0)]),
             R.stroke([(3.95, 1.9), (3.95, 4.8)]), R.stroke([(4.05, 1.9), (4.05, 4.8)])]
    if jambs:
        faces += [R.stroke([(3.95, 1.0), (4.05, 1.0)]), R.stroke([(3.95, 1.9), (4.05, 1.9)])]
    else:
        faces += [R.stroke([(3.95, 1.0), (3.95, 1.9)]), R.stroke([(4.05, 1.0), (4.05, 1.9)])]   # faces run on
    cuts = [R.stroke([(3.95, 1.0), (3.95, 1.9)]), R.stroke([(4.05, 1.0), (4.05, 1.9)])] if jambs else []
    door = [R.stroke([(3.93, 1.0), (3.93, 1.03), (4.07, 1.03), (4.07, 1.0)]),
            R.stroke([(3.93, 1.9), (3.93, 1.87), (4.07, 1.87), (4.07, 1.9)])] if frame else []
    strokes = on("DUVAR", faces + cuts) + on("KAPI", door)          # the cut lines pair into wall: the gap is closed
    runs = [TextRun(id="t1", text="SALON", box=(1.4, 2.4, 2.4, 2.6), height=0.2),
            TextRun(id="t2", text="YATAK ODASI", box=(5.2, 2.4, 6.8, 2.6), height=0.2),
            TextRun(id="t3", text="90/210", box=(4.2, 1.35, 4.7, 1.5), height=0.12)]
    return R.synthetic_page(strokes, runs)


def _cut_span_read(page):
    from wenart.ingest.generic import core as GC
    from wenart.ingest.generic import openings as O
    from wenart.ingest.generic import walls as W
    prims = W.wall_primitives(page, 1.0)
    prims, _choice = W.face_pair_walls(page, 1.0, prims)
    mask = W.wall_mask(page, prims, 1.0)
    ids = {i for p in prims for i in p.stroke_ids}
    rest = [s for s in page.strokes if s.id not in ids]
    walls, _info = W.walls_from_mask(mask, rest, "test.pdf", 1)
    walls2, openings, _, _ = O.gaps_and_openings(walls, rest, "test.pdf", 1)
    return walls2, openings, GC.doors_in_cut_spans(walls2, openings, page.strokes, page.texts, 1.0)


def test_a_door_whose_gap_the_cut_lines_close_is_read_from_its_tag_and_jambs():
    walls2, openings, spanned = _cut_span_read(_cut_span_plan())
    assert not any(o.kind == "door" for o in openings)                 # the cut lines closed the gap: no door read
    new = [o for o in spanned or [] if o.evidence.get("rule") == "cut_span_door"]
    assert len(new) == 1 and abs(new[0].width - 0.9) < 0.02 and math.dist(new[0].center, (4.0, 1.45)) < 0.05
    assert abs(new[0].height - 2.1) < 1e-6 and new[0].kind == "door"


def test_a_plain_wall_is_never_opened_by_a_tag_alone():
    _w, _o, spanned = _cut_span_read(_cut_span_plan(frame=False))      # jambs and cut lines: a drawn opening
    assert spanned is not None and abs(spanned[-1].width - 0.9) < 0.02
    _w, _o, spanned = _cut_span_read(_cut_span_plan(jambs=False))      # faces run on unbroken (the frame's lines
    assert spanned is None                                             # across the wall are no jambs)


def test_rc17_names_a_door_tag_with_no_opening_near_it():
    from wenart.reading_check import structure as ST
    page = _cut_span_plan()
    tf = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    b = {"openings": []}
    found = ST.doors_without_opening(page, tf, b, "L0")
    assert [f["rule"] for f in found] == ["door_without_opening"] and "90/210" in found[0]["message"]
    b["openings"] = [{"level_id": "L0", "type": "door", "center": [4.0, 1.45], "width": 0.9}]
    assert ST.doors_without_opening(page, tf, b, "L0") == []


def test_rc17_names_an_outdoor_label_lost_in_a_wall_or_naming_a_room():
    from wenart.reading_check import structure as ST
    b = _tower()
    b["walls"].append({"id": "w_f", "level_id": "L2", "start": [0, 5.0], "end": [6, 5.0], "thickness": 0.2})
    b["levels"][2]["reading_places"] = [{"kind": "unplaced_label", "text": "BALKON", "at": [3.0, 5.02]}]
    b["rooms"] = [{"id": "r_tiny", "level_id": "L2", "label": "Oda", "room_type": "hall", "area_computed": 1.1,
                   "polygon": _square(2.5, 4.0, 3.6, 4.9)},
                  {"id": "r_b", "level_id": "L1", "label": "Balkon", "room_type": "bedroom",
                   "polygon": _square(0.5, 0.5, 2.0, 2.0)}]
    found = ST.outdoor_labels_lost(b)
    assert {f["level_id"] for f in found} == {"L1", "L2"} and all(f["rule"] == "outdoor_label_lost" for f in found)
    lost = next(f for f in found if f["level_id"] == "L2")
    assert lost["element_ids"] == ["w_f", "r_tiny"]
    b["site"]["outdoor_spaces"] = [{"id": "os", "level_id": "L2", "kind": "balcony",
                                    "polygon": _square(2.0, 4.8, 4.0, 6.0)}]
    assert [f["level_id"] for f in ST.outdoor_labels_lost(b)] == ["L1"]


# ------------------------------------------- R35 in a filled wall region (21 Nov 2026, dataset bench: hatched bodies)
def _slanted_body():
    """The slanted house of ``_slanted_face_plan`` with its wall body drawn as one hatched region (outer ring and the
    room's ring, even-odd), the way a plan hatches its whole wall body: no face pair is a single band."""
    def top(x):
        return 4.8078 + (x - 0.0553) * 2.3 / 8.0
    outer = [(0.0, 0.0), (8.0, 0.0), (8.0, 7.3), (0.0, 5.0)]
    room = [(0.2, 0.2), (7.8, 0.2), (7.8, top(7.8)), (0.2, top(0.2))]
    return [outer, room]


def test_r35_an_angled_strip_of_a_hatched_wall_body_is_one_wall_at_its_angle():
    from wenart.ingest.generic import walls as W
    prim = W.WallPrim(kind="dxf_hatch", entity="HATCH:1", stroke_ids=["HATCH:1"], method="vector", confidence=1.0,
                      polygons=_slanted_body())
    bands = W.angled_bands([prim], 0.0)
    assert len(bands) == 1
    piece = bands[0][1]
    assert abs(piece["angle_deg"] - 16.04) < 0.1 and abs(piece["thickness"] - 0.2) < 0.005
    assert math.dist(piece["start"], piece["end"]) > 7.0
    assert W.angled_bands([prim], 16.04) != []                         # the axis walls are the angled ones then
    # a 0.4 m slot (a shaft) between two angled faces is a hole of the region, not a wall
    slot = [(2.0, 2.0), (6.0, 3.15), (5.89, 3.53), (1.89, 2.38)]
    block = W.WallPrim(kind="dxf_hatch", entity="HATCH:2", stroke_ids=["HATCH:2"], method="vector", confidence=1.0,
                       polygons=[[(0, 0), (8, 0), (8, 6), (0, 6)], slot])
    assert W.angled_bands([block], 0.0) == []


def test_r35_a_hatched_angled_wall_is_read_at_its_angle_not_in_steps():
    from wenart.ingest.generic import walls as W
    prim = W.WallPrim(kind="dxf_hatch", entity="HATCH:1", stroke_ids=["HATCH:1"], method="vector", confidence=1.0,
                      polygons=_slanted_body())
    mask = W.wall_mask(None, [prim], 1.0)
    walls, info = W.walls_from_mask(mask, [], "test.dxf", 1)

    def ang(w):
        return math.degrees(math.atan2(w.end[1] - w.start[1], w.end[0] - w.start[0])) % 180.0
    angled = [w for w in walls if 10.0 < ang(w) % 90 < 20.0]
    assert info.get("angled_walls", 0) == 1 and len(angled) == 1 and abs(angled[0].thickness - 0.2) < 0.011
    stubs = [w for w in walls if w not in angled and math.dist(w.start, w.end) < 0.5]
    assert len(stubs) <= 2, [(w.start, w.end) for w in stubs]           # no axis steps along the angled wall
    assert len(walls) <= 6
