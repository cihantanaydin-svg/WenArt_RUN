"""real06 (``projects/real06/real06.dwg``, the user's DWG of 24 Oct 2026): the drawing-reading rules it needed.

The DWG names no unit ($INSUNITS 0) and is drawn in metres shrunk to 1:50 (1 unit = 50 m); its nine drawings (two
plans, a roof plan, two sections, four elevations, none titled) sit in a grid of frames drawn as four LINEs each; its
dimension chains have a layer of their own; its walls are plaster lines (``SIVA``) with pilasters at the window
jambs; its sliding door to the veranda draws each leaf as three lines; its bathroom door is 0.20 m narrower than its
gap (frames). Each rule is checked on its own here and on the real DWG at the end (LibreDWG needed).
"""
from __future__ import annotations

import math
from types import SimpleNamespace

import pytest

import _real01_page as R
from conftest import PROJECTS
from wenart.ingest import dwg
from wenart.ingest.generic import openings as O
from wenart.ingest.generic import walls as W
from wenart.ingest.generic.model import Stroke, TextRun
from wenart.sheets import classify as CL
from wenart.sheets import exterior as EX
from wenart.sheets import heights as H
from wenart.sheets import levels as LV
from wenart.sheets import split as SP
from wenart.sheets import units_check as UC
from wenart.sheets.model import Ent, Region, Sheet, Txt


def _line_ent(eid, a, b, layer="0"):
    st = Stroke(id=eid, kind="line", pts=[tuple(a), tuple(b)], layer=layer)
    return Ent(id=eid, kind="LINE", layer=layer, box=(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]),
                                                      max(a[1], b[1])), strokes=[st])


def _panel(prefix, x0, y0, x1, y1):
    return [_line_ent(f"LINE:{prefix}1", (x0, y0), (x1, y0)), _line_ent(f"LINE:{prefix}2", (x1, y0), (x1, y1)),
            _line_ent(f"LINE:{prefix}3", (x1, y1), (x0, y1)), _line_ent(f"LINE:{prefix}4", (x0, y1), (x0, y0))]


def _drawing(prefix, x0, x1, y0=10.0, y1=90.0):
    """A drawing of a few lines from x0 to x1 (a closed box and a cross)."""
    return [_line_ent(f"LINE:{prefix}a", (x0, y0), (x1, y0)), _line_ent(f"LINE:{prefix}b", (x1, y0), (x1, y1)),
            _line_ent(f"LINE:{prefix}c", (x1, y1), (x0, y1)), _line_ent(f"LINE:{prefix}d", (x0, y1), (x0, y0)),
            _line_ent(f"LINE:{prefix}e", (x0, y0), (x1, y1))]


# --------------------------------------------------------------------------
# Sheets: panels, the scaled unit, classes, levels, heights, roof
# --------------------------------------------------------------------------

def test_a_grid_of_line_drawn_frames_splits_its_drawings():
    """Two frames drawn as four LINEs each, sharing an edge; their drawings come 2 units apart across it (the gap is
    about 3.4 units): without the panels the clustering joins them, with them each frame holds its own region."""
    ents = _panel("A", 0, 0, 100, 100) + _panel("B", 100, 0, 200, 100) + _drawing("L", 10, 99) \
        + _drawing("R", 101, 190)
    sheet = Sheet(id="s1", space="model", file="t.dxf", page=1, ents=list(ents), texts=[])
    res = SP.split_sheet(sheet)
    assert len(res.frames) == 2 and len(res.clusters) == 2
    assert sorted(round(c.geometry_box[0]) for c in res.clusters) == [10, 101]
    assert all(c.frame is not None for c in res.clusters)
    # The same lines without the shared edge (one frame only, the other side open): no panels, one drawing.
    lone = _panel("A", 0, 0, 100, 100) + _drawing("L", 10, 99) + _drawing("R", 101, 190)
    res = SP.split_sheet(Sheet(id="s1", space="model", file="t.dxf", page=1, ents=list(lone), texts=[]))
    assert res.frames == [] and len(res.clusters) == 1


def test_an_empty_panel_gives_its_lines_back():
    ents = _panel("A", 0, 0, 100, 100) + _panel("B", 100, 0, 200, 100) + _drawing("L", 10, 90)
    res = SP.split_sheet(Sheet(id="s1", space="model", file="t.dxf", page=1, ents=list(ents), texts=[]))
    assert len(res.frames) == 1
    ids = {e.id for c in res.clusters for e in c.ents}
    assert {"LINE:B1", "LINE:B2", "LINE:B3", "LINE:B4"} <= ids        # the empty frame's own lines, unchanged


def test_a_scaled_drawing_gets_its_unit_from_two_agreeing_checks():
    """real06: 164 level-mark pairs at 50 m per unit and door swings of 0.014 units (0.70 m at 50): 'm 1:50'. The
    marks alone are one check: no unit."""
    marks = UC.Check("level_marks", None, 0.0, 10, values=[50.0] * 9 + [19.1])
    doors = UC.Check("door_widths", None, 0.0, 5, values=[0.014] * 5)
    unit, mpu, support = UC.scaled_unit([marks, doors])
    assert unit == "m 1:50" and mpu == pytest.approx(50.0) and [c.check for c in support] == ["level_marks",
                                                                                               "door_widths"]
    assert UC.scaled_unit([marks]) is None
    # Doors that do not fit 50 m per unit give no second check.
    assert UC.scaled_unit([marks, UC.Check("door_widths", None, 0.0, 5, values=[0.1] * 5)]) is None
    # A plain unit is never a scaled candidate (cm 1:100 is m).
    assert "cm 1:100" not in UC.scaled_units() and UC.scaled_units()["m 1:50"] == 50.0


def _region(rid, room_labels, rule="slab_bands"):
    r = Region(id=rid, file="t.dxf", sheet=SimpleNamespace(page=1), box=(0, 0, 1, 1), geometry_box=(0, 0, 1, 1))
    r.cls, r.class_method, r.features = "section", "geometry", {"room_labels": room_labels}
    r.evidence = [{"rule": rule, "text": "slab_bands 2"}]
    return r


def test_sections_without_rooms_beside_sections_with_rooms_are_elevations():
    regions = [_region("r1", 0), _region("r2", 4), _region("r3", 0)]
    changed = CL.outside_views(regions)
    assert [r.id for r in changed] == ["r1", "r3"] and [r.cls for r in regions] == ["elevation", "section", "elevation"]
    assert regions[0].evidence[-1]["rule"] == "outside_view_beside_sections"
    # real02 / real04: their only sections show no room: they stay sections.
    alone = [_region("r1", 0), _region("r2", 0)]
    assert CL.outside_views(alone) == [] and [r.cls for r in alone] == ["section", "section"]


def test_untitled_plans_with_door_swings_are_plans_and_slope_texts_make_a_roof_plan():
    plan = {"room_labels": 5, "door_swings": 3, "wall_test": "hatch comb", "slab_bands": 6, "level_marks": 4}
    assert CL.geometry_rule(None, plan, [], 0.0) == ("floor_plan", "room_labels_door_swings_and_walls")
    assert CL.geometry_rule(None, dict(plan, door_swings=0), [], 0.0)[0] == "section"
    roof = {"room_labels": 0, "slope_texts": 10, "hip_lines": 13}
    assert CL.geometry_rule(None, roof, [], 0.0) == ("roof_plan", "slope_texts_with_hip_lines")
    assert CL.SLOPE_TEXT.search("EGIM%33") and not CL.SLOPE_TEXT.search("EGIM")


def _mark_region(rid, values):
    """A plan region whose level marks stand on a line under each text."""
    texts, ents = [], []
    for k, v in enumerate(values):
        x = 10.0 * k
        texts.append(Txt(id=f"TEXT:{rid}{k}", text=v, box=(x, 1.0, x + 2.0, 1.4), height=0.4))
        ents.append(_line_ent(f"LINE:{rid}{k}", (x - 0.5, 0.8), (x + 2.5, 0.8)))
    r = Region(id=rid, file="t.dxf", sheet=SimpleNamespace(page=1), box=(0, 0, 50, 2), geometry_box=(0, 0, 50, 2),
               ents=ents, texts=texts)
    r.evidence = [{"rule": "room_labels_door_swings_and_walls"}]
    return r


def test_untitled_plans_are_ordered_by_their_floor_marks():
    ground = _mark_region("a", ["+0,50", "+0,50", "+0,50", "±0,00"])
    first = _mark_region("b", ["+3,50"])
    assert LV.floor_mark(ground) == 0.5 and LV.floor_mark(first) == 3.5
    review, warnings = [], []
    LV.assign_levels([first, ground], review, warnings)
    assert review == [] and (ground.level["id"], first.level["id"]) == ("L0", "L1")
    assert ground.level["method"] == first.level["method"] == "assumed" and len(warnings) == 2
    # Marks less than a storey apart (two copies of one floor): the levels cannot be told.
    a, b = _mark_region("c", ["+0,50"]), _mark_region("d", ["+1,00"])
    review = []
    LV.assign_levels([a, b], review, [])
    assert len(review) == 2 and a.level is None and b.level is None


def test_nearly_parallel_roof_lines_put_no_corner_far_away():
    """real06's section: two roof lines 2 cm apart and almost parallel meet about 1 km away; the corner of the
    envelope stays where one line takes over from the other."""
    lines = [H.Line((0.0, 0.0), (6.0, 1.2), "L1", "L1"), H.Line((4.0, 0.82), (10.0, 2.0201), "L2", "L2")]
    pts, _, _ = H._envelope(lines, 0.001)
    assert all(-1e-6 <= x <= 10.0 + 1e-6 for x, _ in pts) and max(y for _, y in pts) < 2.1


def test_a_roof_plan_whose_slope_texts_agree_is_a_hip_roof():
    texts = [Txt(id=f"TEXT:{k}", text="EĞİM%33", box=(k, 0, k + 1, 0.2), height=0.2) for k in range(4)]
    r = Region(id="r6", file="t.dxf", sheet=SimpleNamespace(page=1), box=(0, 0, 9, 9), geometry_box=(0, 0, 9, 9),
               texts=texts)
    r.features = {"hip_lines": 4}
    hip = EX.roof_from_roof_plan([r])
    assert hip["type"] == "hip" and hip["slope_pct"] == 33.0
    assert hip["pitch_deg"] == pytest.approx(math.degrees(math.atan(0.33)))
    r.texts = texts[:2] + [Txt(id="TEXT:9", text="EĞİM%45", box=(0, 1, 1, 1.2), height=0.2)]
    assert EX.roof_from_roof_plan([r]) is None                   # slopes that disagree say nothing


# --------------------------------------------------------------------------
# Walls and openings
# --------------------------------------------------------------------------

def test_a_stepped_pier_between_two_windows_is_one_wall_piece():
    """A 0.85 m pier: the room face runs straight, the outer face steps out 0.20 m at both jambs (pilasters): three
    pairs of 0.25-0.35 m, none 0.4 m long, all on the room face: one run of 0.85 m, every piece primary."""
    u, n = (0.0, 1.0), (-1.0, 0.0)
    room = W._Line(0.0, 0.0, 0.85, ["room"])
    mid = W._Line(0.25, 0.25, 0.60, ["mid"])
    low, high = W._Line(0.45, 0.0, 0.25, ["low"]), W._Line(0.45, 0.60, 0.85, ["high"])
    pairs = W._pairs_of([room, mid, low, high], "SIVA", u, n)
    assert sorted((round(p.lo, 2), round(p.hi, 2), round(p.width, 2)) for p in pairs) == [
        (0.0, 0.25, 0.45), (0.25, 0.6, 0.25), (0.6, 0.85, 0.45)]
    assert not any(p.primary for p in pairs)
    W.stepped_runs(pairs)
    assert all(p.primary and p.run == pytest.approx(0.85) for p in pairs)
    # A cap line on the other side of the room face pairs with it but is no part of the pier's run.
    cap = W._Line(-0.30, 0.0, 0.20, ["cap"])
    pairs = W._pairs_of([cap, room, mid, low, high], "SIVA", u, n)
    W.stepped_runs(pairs)
    assert [p.primary for p in pairs if p.lines[0] is cap] == [False]


def test_dimension_lines_leave_the_wall_choice_only_on_a_dimension_layer():
    """Two rooms whose walls are drawn on layer 'W' (one face of the right wall also taken by the dimension finder)
    and a dimension chain pair on layer 'D' through both: the chain lines take no part, the wall face stays."""
    def lines(layer, segs):
        return [Stroke(id=f"{layer}:{k}", kind="line", pts=[a, b], layer=layer) for k, (a, b) in enumerate(segs)]

    walls = lines("W", [((0, 0), (8, 0)), ((0, 0.2), (8, 0.2)), ((0, 5), (8, 5)), ((0, 4.8), (8, 4.8)),
                        ((0, 0), (0, 5)), ((0.2, 0.2), (0.2, 4.8)), ((8, 0), (8, 5)), ((7.8, 0.2), (7.8, 4.8)),
                        ((4.0, 0.2), (4.0, 4.8)), ((4.2, 0.2), (4.2, 4.8))])
    chain = lines("D", [((-1, 2.4), (9, 2.4)), ((-1, 2.7), (9, 2.7))])
    texts = [TextRun(id="t1", text="SALON", box=(1.5, 3.0, 2.5, 3.2), height=0.2),
             TextRun(id="t2", text="MUTFAK", box=(5.5, 3.0, 6.5, 3.2), height=0.2)]
    page = R.synthetic_page(walls + chain, texts)
    dims = frozenset({"D:0", "D:1", "W:6"})
    prims, choice = W.face_pair_walls(page, 1.0, [], dims)
    assert choice["used"] and choice["layer"] == "W"
    assert any("W:6" in p.stroke_ids for p in prims)              # the wall face the finder took stays a wall face
    assert not any(i.startswith("D:") for p in prims for i in p.stroke_ids)


def _gap_walls(gap_from, gap_to, t=0.25):
    return [R.wall((0.0, 0.0), (gap_from, 0.0), t), R.wall((gap_to, 0.0), (gap_to + 1.0, 0.0), t)]


def _line(a, b, layer="KAPI"):
    return Stroke(id=R.sid("l"), kind="line", pts=[tuple(a), tuple(b)], layer=layer)


def test_a_two_panel_sliding_door_drawn_with_lines_is_a_door():
    """real06's veranda door: a 2.95 m gap, frame lines on both faces, two leaves of three lines each on two tracks
    (real06's are 0.449 x the gap, just under one sliding leaf's 0.45; here 1.25 m, 0.42 x)."""
    strokes = [_line((1.05, -0.125), (3.90, -0.125)), _line((1.05, 0.125), (3.90, 0.125))]
    strokes += [_line((1.10, y), (2.35, y)) for y in (0.0, 0.025, 0.05)]
    strokes += [_line((2.53, y), (3.78, y)) for y in (-0.05, -0.025, 0.0)]
    _, openings, _, _ = O.gaps_and_openings(_gap_walls(1.0, 3.95), strokes, "t.dwg", None)
    assert [(o.kind, round(o.width, 2)) for o in openings] == [("door", 2.95)]
    # One leaf alone (no second track) is no two-panel door.
    _, openings, _, _ = O.gaps_and_openings(_gap_walls(1.0, 3.95), strokes[:5], "t.dwg", None)
    assert not [o for o in openings if o.kind == "door"]


def test_a_door_leaf_narrower_than_its_gap_by_the_frames_is_a_door():
    """real06's bathroom door: a 0.70 m swing hinged at one end of a 0.90 m gap (the frames take the rest)."""
    strokes = [R.arc((1.0, 0.0), 0.70, 0.0, 90.0), _line((1.0, 0.0), (1.0, 0.70))]
    _, openings, _, _ = O.gaps_and_openings(_gap_walls(1.0, 1.9), strokes, "t.dwg", None)
    assert [(o.kind, round(o.width, 2)) for o in openings] == [("door", 0.9)]
    # A swing 0.30 m narrower than the gap is not this gap's door.
    strokes = [R.arc((1.0, 0.0), 0.60, 0.0, 90.0), _line((1.0, 0.0), (1.0, 0.60))]
    _, openings, _, _ = O.gaps_and_openings(_gap_walls(1.0, 1.9), strokes, "t.dwg", None)
    assert not [o for o in openings if o.kind == "door" and round(o.width, 2) == 0.9]


# --------------------------------------------------------------------------
# The real DWG
# --------------------------------------------------------------------------

needs_real06 = pytest.mark.skipif(not dwg.available_converters() or not (PROJECTS / "real06").is_dir(),
                                  reason="LibreDWG dwg2dxf not installed")


@pytest.fixture(scope="module")
def real06(tmp_path_factory):
    from wenart.ingest import pipeline as PL

    out = tmp_path_factory.mktemp("real06")
    building, build = PL.run_project(PROJECTS / "real06", out, no_ai=True)
    import json
    return json.loads((out / "sheets.json").read_text(encoding="utf-8")), building


@needs_real06
def test_real06_sheets(real06):
    sheets, _ = real06
    units = sheets["documents"][0]["units"]
    assert units["metres_per_unit"] == pytest.approx(50.0) and units["scaled"]["unit"] == "m 1:50"
    classes = sorted(r["class"] for r in sheets["regions"])
    assert classes == ["elevation"] * 4 + ["floor_plan"] * 2 + ["roof_plan"] + ["section"] * 2
    plans = sorted((r["level"]["id"], r["id"]) for r in sheets["regions"] if r["class"] == "floor_plan")
    assert [lv for lv, _ in plans] == ["L0", "L1"]
    roof = sheets["exterior"]["roof"]
    assert roof["type"] == "hip" and roof["type_source"] == "roof_plan"
    floors = {lv["level_id"]: lv["floor_z"]["value"] for lv in sheets["heights"]["levels"]}
    assert floors == {"L0": pytest.approx(0.0), "L1": pytest.approx(3.0)}
    assert sheets["heights"]["roof"]["ridge_z"]["value"] < 9.0          # no corner far away


@needs_real06
def test_real06_building(real06):
    _, building = real06
    assert building["status"] == "ok"
    rooms = {(r["level_id"], r["room_type"]) for r in building["rooms"]}
    assert {("L0", "living"), ("L0", "kitchen"), ("L0", "bathroom"), ("L1", "bathroom"), ("L1", "bedroom")} <= rooms
    assert sum(1 for r in building["rooms"] if r["level_id"] == "L1" and r["room_type"] == "bedroom") >= 3
    assert any(o["type"] == "door" and o.get("operation") == "sliding" for o in building["openings"])
