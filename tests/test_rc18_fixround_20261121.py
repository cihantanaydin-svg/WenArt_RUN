"""21 Nov 2026 (user OK: "yes put the reader fix round first"): the reader fix round for the general structural faults
the RC18 regulation checks exposed. Each fix is a general rule of the reader with a synthetic test here and a code check
that raises the fault on any future reading. CPU only, pure, no project data.

- (a) a glazed facade's inferred walls lie on the drawn facade line (``facade.facade_band``), not ``BAND_M / 2`` inside
  the frames (built off, ``FACADE_LINE_SNAP``; switched on the same day with the user's OK once the truth record C0001
  had its walls moved onto the drawn facade line, ``tests/test_facade_on_20261121.py``); RC17
  ``inferred_wall_off_facade`` raises an inferred wall standing into the room off the drawn face;
- (b) a framed window is never added where the openings read in the band together cover the frames
  (``core.covered_share``); RC17 ``opening_off_wall`` raises an opening off its wall's band;
- (c) an air shaft (H.B 50/50, a doorless face under 1.0 m across) is no light well (``topology.well_kind``,
  ``room_subtype`` air_shaft); RC18 judges it by PAİY 32(3); RC14 ``well_type`` raises a light well that is one;
- (e) a word drawn inside a doorless face (YÜKLÜK, on any layer) names it before its size makes it a light well;
- RC18 does not judge the rooms an inferred ground floor was cut to (the drawing does not draw them).
"""
from __future__ import annotations

from types import SimpleNamespace

import pytest
from shapely.geometry import Point, Polygon, box

from wenart import building as B
from wenart.ingest import completion as CP
from wenart.ingest.generic import core as CORE
from wenart.ingest.generic import facade as FC
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import OpeningItem, WallItem
from wenart.reading_check import regulations as RG
from wenart.reading_check import sense as SN
from wenart.reading_check import structure as SR


def _wall(s, e, t=0.2):
    return WallItem(start=s, end=e, thickness=t, box=[0, 0, 0, 0], evidence={"file": "x.dwg", "entity": "W"},
                    entity="W")


def _line(k, a, b, layer="kapı-pencere"):
    return Stroke(id=f"LINE:{k}", kind="line", pts=[a, b], layer=layer)


# ------------------------------------------------------------------------------------------- (a) the facade line
def _glazed_room():
    """A 4 x 4 m room (inner faces x 0-4, y 0-4): drawn walls 0.2 m thick on the north, east and south; its west facade
    (the band x -0.2 to 0) drawn as two short wall pieces at the corners and a window between them (frame lines inside
    the band, a sill line 3 cm into the room)."""
    walls = [_wall((-0.2, 4.1), (4.2, 4.1)), _wall((4.1, 4.2), (4.1, -0.2)), _wall((4.2, -0.1), (-0.2, -0.1)),
             _wall((-0.1, -0.2), (-0.1, 0.6)), _wall((-0.1, 3.4), (-0.1, 4.2))]
    strokes = [_line(1, (-0.15, 0.7), (-0.15, 3.3)), _line(2, (-0.1, 0.7), (-0.1, 3.3)),
               _line(3, (-0.05, 0.7), (-0.05, 3.3)), _line(4, (0.03, 0.7), (0.03, 3.3))]
    return walls, strokes


def test_frames_in_a_drawn_wall_line_take_that_walls_band():
    walls, strokes = _glazed_room()
    lines = FC.joinery_lines(strokes, theta=0.0)
    frames = FC._wall_frames(walls)
    bands = [FC.facade_band(ln, frames) for ln in lines]
    assert all(b is not None for b in bands)
    for b in bands:                                                     # the drawn facade's faces, x -0.2 to 0
        x0, _y0, x1, _y1 = b.bounds
        assert x0 == pytest.approx(-0.2, abs=1e-6) and x1 == pytest.approx(0.0, abs=1e-6)
    lone = FC.facade_band(FC.joinery_lines([_line(9, (2.0, 1.0), (2.0, 3.0))], 0.0)[0], frames)
    assert lone is None                                                # a frame in no drawn wall's line keeps its band


def test_the_glazed_facade_wall_lies_on_the_drawn_facade_line():
    walls, strokes = _glazed_room()
    faces, _links = FC.close_rooms(walls, strokes, [(2.0, 2.0)], snap=True)
    assert 0 in faces
    face = faces[0]
    assert face.bounds[0] == pytest.approx(0.0, abs=0.02)               # the room reaches the drawn inner face
    assert face.area == pytest.approx(16.0, abs=0.3)
    new = FC.facade_wall_items(walls, [face], [], "x.dwg", None)
    west = [w for w in new if abs(w.start[0] - w.end[0]) < 1e-6 and w.start[0] < 0.5]
    assert west
    for w in west:                                                      # the inferred wall in the drawn band
        assert w.start[0] + float(w.thickness) / 2.0 == pytest.approx(0.0, abs=0.02)
    # the rule as shipped before (off): the frames' own bands, the room's face inside the frames (the fault RC17 names)
    old, _ = FC.close_rooms(walls, strokes, [(2.0, 2.0)], snap=False)
    from shapely.geometry import LineString
    assert old[0].intersection(LineString([(-1, 2.0), (5, 2.0)])).bounds[0] > 0.1
    assert face.intersection(LineString([(-1, 2.0), (5, 2.0)])).bounds[0] == pytest.approx(0.0, abs=0.02)


def test_a_run_of_frames_reaches_the_drawn_wall_through_each_other():
    frames = FC._wall_frames([_wall((-0.1, 3.4), (-0.1, 4.2))])         # one drawn piece at the top only
    lines = FC.joinery_lines([_line(1, (-0.1, 2.3), (-0.1, 3.3)), _line(2, (-0.1, 1.0), (-0.1, 2.2)),
                              _line(3, (-0.1, -1.0), (-0.1, 0.4))], 0.0)
    bands = FC.facade_bands(lines, frames)
    assert bands[0] is not None and bands[1] is not None               # chained 0.1 m apart
    assert bands[2] is None                                             # 0.6 m from the run: another facade


def _bld(walls, rooms=(), openings=()):
    return {"levels": [{"id": "L0", "order": 0, "elevation": 0.0}], "walls": list(walls), "rooms": list(rooms),
            "openings": list(openings)}


def _w(wid, a, b, t=0.2, ext=True, inferred=False):
    w = {"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t, "exterior": ext}
    if inferred:
        w.update(inferred=True, evidence=[{"method": "inferred", "rule": "glazed_facade"}])
    return w


def test_rc17_raises_an_inferred_wall_standing_into_the_room_off_the_drawn_facade():
    room = {"id": "r_L0_salon", "level_id": "L0", "polygon": [[0.2, 0.0], [4.0, 0.0], [4.0, 4.0], [0.2, 4.0]]}
    drawn = _w("w_L0_1", (-0.1, 3.0), (-0.1, 6.0), t=0.2)                # the drawn facade, inner face x = 0
    bad = _w("w_L0_2", (0.05, 0.0), (0.05, 3.0), t=0.3, inferred=True)  # inner face x = 0.2: 0.2 m into the room
    found = SR.inferred_walls_off_facade(_bld([drawn, bad], [room]))
    assert [f["element_ids"] for f in found] == [["w_L0_2", "w_L0_1"]] and "0.20 m into the room" in found[0]["message"]
    good = _w("w_L0_3", (-0.05, 0.0), (-0.05, 3.0), t=0.1, inferred=True)   # thinner, inner face on the line
    room2 = dict(room, polygon=[[0.0, 0.0], [4.0, 0.0], [4.0, 4.0], [0.0, 4.0]])
    assert not SR.inferred_walls_off_facade(_bld([drawn, good], [room2]))
    assert SR.RULES["inferred_wall_off_facade"]


# ------------------------------------------------------------------------------------- (b) openings and the band
def test_openings_read_together_cover_the_frames():
    assert CORE.covered_share(0.0, 1.8, [(0.1, 0.85), (0.95, 1.7)]) == pytest.approx(1.5 / 1.8)
    assert CORE.covered_share(0.0, 1.8, [(0.1, 0.85)]) < 0.5                # one casement alone: under half
    assert CORE.covered_share(0.0, 1.0, [(0.0, 0.6), (0.4, 0.8)]) == pytest.approx(0.8)   # overlaps counted once
    assert CORE.covered_share(1.0, 1.0, [(0.0, 2.0)]) == 0.0


def test_a_double_casement_gets_no_third_window_from_its_sill_lines():
    """A 0.2 m facade wall with two 0.77 m casements read in its band and two 1.8 m sill lines drawn 0.2 m outside it
    (real17): no framed window is added over them."""
    wall = _wall((0.0, 0.0), (0.0, 6.0), t=0.2)
    thin = _wall((-0.29, 0.0), (-0.29, 6.0), t=0.05)                    # the outer line pair read as a thin wall
    case = [OpeningItem(kind="window", width=0.77, center=(0.0, c), rotation_deg=90.0, box=[0, 0, 0, 0], entity="b",
                        evidence={}) for c in (2.4, 3.3)]
    sill = [Stroke(id=f"LINE:{k}", kind="line", pts=[(x, 1.95), (x, 3.75)], layer="pencere")
            for k, x in ((1, -0.31), (2, -0.26))]
    one = CORE._framed_windows(SimpleNamespace(notes=[]), "t", [wall, thin], case[:1], sill, [], 1.0)
    assert one and len(one) == 2                                        # one casement alone: the frames add a window
    got = CORE._framed_windows(SimpleNamespace(notes=[]), "t", [wall, thin], list(case), sill, [], 1.0)
    assert got is None                                                  # both casements cover them: nothing added


def test_rc17_raises_an_opening_off_its_walls_band():
    w = _w("w_L0_1", (0.0, 0.0), (0.0, 6.0), t=0.2)
    ok = {"id": "win_L0_1", "type": "window", "level_id": "L0", "wall_id": "w_L0_1", "center": [0.0, 2.4], "width": 0.77}
    off = {"id": "win_L0_2", "type": "window", "level_id": "L0", "wall_id": "w_L0_1", "center": [-0.29, 2.85],
           "width": 1.8}
    found = SR.openings_off_wall(_bld([w], openings=[ok, off]))
    assert [f["element_ids"][0] for f in found] == ["win_L0_2"] and "0.29 m off the axis" in found[0]["message"]


# ------------------------------------------------------------------------------- (c), (e) air shafts and closets
def test_an_air_shaft_word_or_an_air_shafts_size_is_no_light_well():
    assert TP.well_kind(box(0, 0, 0.5, 0.5), [("H.B 50/50", (0.25, 0.25))])[0] == "air_shaft"
    assert TP.well_kind(box(0, 0, 0.5, 0.65), [("Hava Bacası 50*65 cm", (0.25, 0.3))])[0] == "air_shaft"
    assert TP.well_kind(box(0, 0, 0.85, 0.9), [])[0] == "air_shaft"                 # by its size alone
    assert TP.well_kind(box(0, 0, 1.6, 2.4), [])[0] == "light_well"
    assert TP.well_kind(box(0, 0, 0.8, 0.8), [("AYDINLIK", (0.4, 0.4))])[0] == "light_well"   # the drawing's word
    kind, why, word = TP.well_kind(box(0, 0, 0.47, 2.29), [("YUKLUK", (0.2, 1.1))])
    assert kind == "room" and word == "YUKLUK" and "closet" in why
    assert TP.well_kind(box(0, 0, 0.5, 0.5), [("H.B", (3.0, 3.0))])[0] == "air_shaft"   # a word outside: by size


def _shaft_plan(size=(0.5, 0.5)):
    """A 3 x 3 m bathroom with a window onto a doorless face east of it (``size``), both closed by walls."""
    sx, sy = size
    walls = [_wall((0, 0), (3 + sx + 0.1, 0), 0.1), _wall((3 + sx + 0.1, 0), (3 + sx + 0.1, 3), 0.1),
             _wall((3 + sx + 0.1, 3), (0, 3), 0.1), _wall((0, 3), (0, 0), 0.1),
             _wall((3.05, 0), (3.05, 3), 0.1)]
    if sy < 3:
        walls.append(_wall((3.05, sy + 0.05), (3 + sx + 0.1, sy + 0.05), 0.1))
    win = OpeningItem(kind="window", width=0.4, center=(3.05, min(sy, 3) / 2.0 + 0.025), rotation_deg=90.0,
                      box=[0, 0, 0, 0], entity="win", evidence={})
    faces = TP.faces(walls, [win])
    shaft = next(f for f in faces if f.contains(Point(3.1 + sx / 2.0, min(sy, 3) / 2.0)))
    return walls, [win], faces, shaft


def test_a_doorless_face_with_hb_inside_is_an_air_shaft_named_so():
    walls, ops, faces, shaft = _shaft_plan()
    rtype, reason = TP.unlabelled_face_type(shaft, walls, ops, others=faces,
                                            texts=[("H.B 50/50", tuple(shaft.centroid.coords)[0])])
    assert rtype == "shaft" and reason.startswith("air shaft")
    assert TP.light_well_label(reason, True) == "Hava Bacası"
    # with no text it is still an air shaft by its size, never a light well
    assert TP.unlabelled_face_type(shaft, walls, ops, others=faces)[1].startswith("air shaft")


def test_a_closet_word_drawn_inside_names_the_face():
    walls, ops, faces, shaft = _shaft_plan((0.47, 2.29))
    rtype, reason = TP.unlabelled_face_type(shaft, walls, ops, others=faces,
                                            texts=[("YUKLUK", tuple(shaft.centroid.coords)[0])])
    assert rtype == "storage" and reason.startswith("named:") and TP.light_well_label(reason, True) == "Yukluk"


def test_a_large_doorless_face_stays_a_light_well():
    walls, ops, faces, shaft = _shaft_plan((1.6, 2.4))
    rtype, reason = TP.unlabelled_face_type(shaft, walls, ops, others=faces)
    assert rtype == "shaft" and reason.startswith("light well") and TP.light_well_label(reason, True) == "Işıklık"


def test_completion_keeps_an_air_shaft_its_subtype_and_opens_it_like_a_well():
    rooms = [{"id": "r_L0_hb", "level_id": "L0", "label": "Hava Bacası", "room_type": "shaft",
              "polygon": [[0, 0], [0.5, 0], [0.5, 0.5], [0, 0.5]]},
             {"id": "r_L0_well", "level_id": "L0", "label": "Işıklık", "room_type": "shaft",
              "polygon": [[2, 0], [4, 0], [4, 2.5], [2, 2.5]]}]
    b = {"levels": [{"id": "L0", "order": 0}], "rooms": rooms, "openings": [], "walls": [], "slabs": []}
    build = SimpleNamespace(building=b, warn=lambda *_: None, ids=B.IdCounter())
    rec = CP._light_wells(build, {"L0": []})
    hb, well = rooms
    assert hb["room_subtype"] == "air_shaft" and hb["label"] == "Hava Bacası"
    assert well["room_subtype"] == "light_well"
    assert set(rec["rooms"]["L0"]) == {"r_L0_hb", "r_L0_well"}
    assert CP.is_light_well(hb) and CP.is_air_shaft(hb) and not CP.is_air_shaft(well)


def test_rc18_judges_an_air_shaft_by_its_own_limits():
    from test_regulations_tr_20261121 import block, room, rect
    b = block()
    hb = room("hb", "Hava Bacası", "shaft", rect(50, 0, 50.5, 0.5), "L0")              # 0.25 m2: under 0.36
    hb2 = room("hb2", "Işıklık", "shaft", rect(60, 0, 60.85, 0.9), "L0")               # typed air shaft by the reader
    hb2["room_subtype"] = "air_shaft"
    b["rooms"] += [hb, hb2]
    found = [f for f in RG.findings(b) if f["rule"] == "light_well_size"]
    assert [(f["element_ids"][0], f["limit"]) for f in found] == [("r_L0_hb", "paiy32_air_shaft")]


def test_rc14_raises_a_light_well_that_is_an_air_shaft_or_a_closet():
    rooms = [{"id": "r_L0_isiklik", "level_id": "L0", "label": "Işıklık", "room_type": "shaft",
              "room_subtype": "light_well", "polygon": [[0, 0], [0.5, 0], [0.5, 0.5], [0, 0.5]]},
             {"id": "r_L0_isiklik_2", "level_id": "L0", "label": "Işıklık", "room_type": "shaft",
              "room_subtype": "light_well", "polygon": [[2, 0], [2.47, 0], [2.47, 2.29], [2, 2.29]]},
             {"id": "r_L0_isiklik_3", "level_id": "L0", "label": "Işıklık", "room_type": "shaft",
              "room_subtype": "light_well", "polygon": [[5, 0], [6.6, 0], [6.6, 2.4], [5, 2.4]]}]
    b = {"levels": [{"id": "L0", "order": 0}], "rooms": rooms}
    found = SN.well_type(b, {"L0": [{"text": "YUKLUK", "x": 2.2, "y": 1.1}]})
    assert sorted(f["element_ids"][0] for f in found) == ["r_L0_isiklik", "r_L0_isiklik_2"]
    assert "rule" in found[0] and SN.RULES["well_type"]


# --------------------------------------------------------------------------- RC18: rooms an inferred cut made
def test_rc18_does_not_judge_the_rooms_an_inferred_ground_floor_was_cut_to():
    from test_regulations_tr_20261121 import block, rect
    b = block()
    salon = next(r for r in b["rooms"] if r["id"] == "r_L0_salon_a")
    salon["polygon"] = rect(0.1, 3.1, 5.4, 5.9)                     # cut by an inferred footprint to 2.80 m across
    salon["area_computed"] = round(Polygon(salon["polygon"]).area, 3)
    assert any(salon["id"] in f["element_ids"] for f in RG.findings(b))
    b["level_inference"] = {"storeys": {"ground_floor": {"cut": {"rooms_cut": [salon["id"]]}}}}
    assert RG.not_drawn_rooms(b) == [salon["id"]]
    assert not any(salon["id"] in f["element_ids"] for f in RG.findings(b))


# ------------------------------------------------------------------------------- (f) the crop shown to a judge
def test_a_crop_draws_every_line_crossing_it_not_only_lines_starting_in_it():
    """real21: the party wall's two lines run the building's whole length and start outside the light well's crop; the
    judged crop left them out and the well looked open onto the neighbour (``sheets._entities``)."""
    import ezdxf
    from wenart.reading_check import sheets as SH

    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_line((15.2, 0.4), (15.4, 29.0))                    # crosses the box, starts far below it
    msp.add_lwpolyline([(0.0, 0.0), (1.0, 0.0)])               # nowhere near it
    msp.add_line((14.0, 10.0), (14.5, 10.0))                   # starts inside it
    got = SH._entities(doc, [13.0, 9.0, 16.0, 12.0])
    assert sorted(e.dxftype() for e in got) == ["LINE", "LINE"]
