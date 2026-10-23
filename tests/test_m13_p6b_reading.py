"""Fix round after P6b (23 Oct 2026), track F_reading: walls and openings of the generic plan core.

Pod P6b (real03) showed three critical F7 findings on fridges beside 'doors' and four hall washers 0.14-0.19 m in a
wall. The verifiers traced both to the reading of real03's hall-living partition (LibreDWG strokes of
projects/real03/tekkat.dwg): the 30 cm shear walls (D BLOK_STA_NK) on the drawn 0.10 m partition (DUVAR) were read as
one 0.30 m wall from end to end, its gaps 'windows' made of the beam projections (IZ-1), the axis (AKS) and the area
outlines (ALAN-NET) lying on its faces. The rules checked here (``wenart.ingest.generic.openings``):

- a lined gap (a thinner wall along one face through the gap) is open and the thick pieces stay walls of their own,
  each marked ``corrected_by_ai`` (``_lining``, ``_mark_lined``);
- a gap inside other wall material is closed, never an opening (``_inside_wall``);
- a window needs lines of its own (``_confined``: ending within the gap +- ``OWN_MARGIN_M``) at >= ``WINDOW_LINES_MIN``
  offsets, >= ``GLASS_MIN_LINES`` of them glass strictly between the faces (gap windows and continuous-wall windows;
  traced raster lines keep the old rule);
- an end gap whose two faces are drawn on across it, with no glass or swing, extends the wall (no opening).

``tests/fixtures/m13_p6b_real03_hall.json`` holds the real input walls and strokes around the partition (the P6b
building frame); every real window of real02, real03 and real04 carries two or three glass lines and still passes
(checked on their LibreDWG replays in the session).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

import _real01_page as R
from wenart import building as B
from wenart.ingest.generic import core
from wenart.ingest.generic import openings as O
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import WallItem

FIXTURE = Path(__file__).parent / "fixtures" / "m13_p6b_real03_hall.json"


def _run(walls, strokes):
    return O.gaps_and_openings(walls, strokes, "test.dwg", None)


def _vertical(out_walls, x, t):
    """[((y0, y1), wall)] of the walls along x of thickness t, by y0."""
    rows = [(((w.start[1], w.end[1]) if w.start[1] < w.end[1] else (w.end[1], w.start[1])), w)
            for w in out_walls if abs(w.start[0] - x) < 0.01 and abs(w.end[0] - x) < 0.01
            and abs(w.thickness - t) < 0.006]
    return sorted(rows, key=lambda row: row[0])


# --------------------------------------------------------------------------
# real03: the hall-living partition as drawn
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def real03_hall():
    data = json.loads(FIXTURE.read_text(encoding="utf-8"))
    walls = []
    for w in data["walls"]:
        t = w["thickness"]
        xs, ys = (w["start"][0], w["end"][0]), (w["start"][1], w["end"][1])
        walls.append(WallItem(start=tuple(w["start"]), end=tuple(w["end"]), thickness=t,
                              box=[min(xs) - t / 2, min(ys) - t / 2, max(xs) + t / 2, max(ys) + t / 2],
                              entity=w["entity"],
                              evidence=B.evidence("tekkat.dwg", "vector", w["confidence"], entity=w["entity"])))
    strokes = [Stroke(id=s["id"], kind=s["kind"], pts=[tuple(p) for p in s["pts"]], closed=s.get("closed", False),
                      layer=s.get("layer"), block=s.get("block"), arc=s.get("arc")) for s in data["strokes"]]
    return O.gaps_and_openings(walls, strokes, "tekkat.dwg", None)


def test_real03_shear_walls_on_the_partition_are_walls_of_their_own(real03_hall):
    out_walls, openings, log, _ = real03_hall
    thick = _vertical(out_walls, 3.3049, 0.3)
    assert [tuple(round(v, 2) for v in span) for span, _ in thick] == [(0.14, 1.3), (5.82, 7.57), (12.1, 13.25)]
    for _, w in thick:
        label = w.corrected_by_ai
        assert label["rule"] == "lined_gap" and label["evidence"]["rule"] == "lined_gap"
        assert label["by"] == "code" and label["stage"] == "reading"
        assert label["before"]["thickness"] == 0.3
        assert label["before"]["start"][1] == pytest.approx(0.1402) and label["before"]["end"][1] == pytest.approx(
            13.2502)
        assert "a 0.10 m wall" in label["reason"] and "columns or shear walls" in label["reason"]
        assert "INSERT:7C9C9/22/" in label["evidence"]["entity"]           # the shear walls' and the lining's strokes
        assert "read as 3 walls" in w.evidence["note"]
    lined = [e for e in log if e.get("lining")]
    assert len(lined) == 4 and all(e["class"] == "open" and e["lining"]["lining_thickness"] == 0.1 for e in lined)
    # The drawn 0.10 m partition keeps its two 1.05 m hall-living passages, and nothing else is cut into it or the
    # concrete beside it (P6b: six 'windows' on the 0.30 m run, four in the core, two 'openings' in the core and one
    # in the north shear wall).
    thin = _vertical(out_walls, 3.2049, 0.1)
    assert [tuple(round(v, 2) for v in span) for span, _ in thin] == [(1.0, 13.4)]
    near = [o for o in openings if 3.0 < o.center[0] < 3.8]
    assert sorted((o.kind, round(o.center[1], 3), o.width) for o in near) == [("opening", 4.475, 1.05),
                                                                            ("opening", 8.925, 1.05)]


def test_real03_washer_niche_is_the_drawn_065_m(real03_hall):
    """The 'İŞLİK 0.45 m2' niche (0.65 x 0.69 m) between the partition's east face (x 3.2549) and the niche wall
    (x 3.9039): its south wall now runs to the partition, and no wall stands in the niche."""
    out_walls = real03_hall[0]
    south = [w for w in out_walls if abs(w.start[1] - 3.15) < 0.01 and abs(w.end[1] - 3.15) < 0.01]
    assert len(south) == 1 and min(south[0].start[0], south[0].end[0]) == pytest.approx(3.2549, abs=0.002)
    for w in out_walls:
        if abs(w.start[0] - w.end[0]) < 0.01 and 3.2 < w.start[0] < 3.9:
            lo, hi = sorted((w.start[1], w.end[1]))
            faces = (w.start[0] - w.thickness / 2, w.start[0] + w.thickness / 2)
            assert hi <= 3.2 or lo >= 3.95 or faces[1] <= 3.255 + 1e-3, (w.start, w.end, w.thickness)


def test_real03_real_windows_keep_their_glass(real03_hall):
    """The two facade windows in the fixture (CAM-PER frame lines and CAM panes) stay windows."""
    windows = [o for o in real03_hall[1] if o.kind == "window"]
    assert {(round(o.center[0], 1), round(o.center[1], 3)) for o in windows} >= {(5.0, 0.075), (5.0, 13.325)}
    assert all(o.width > 1.4 for o in windows if round(o.center[0], 1) == 5.0)


# --------------------------------------------------------------------------
# Lined gaps
# --------------------------------------------------------------------------

def _partition(lining=True, glass=False):
    """real03's partition in small: 0.30 m shear walls at x 3.15-3.45 (y 0-1.3, 5.7-7.7), the drawn 0.10 m wall at
    x 3.15-3.25 with a passage at y 3.95-5.0, the niche wall at y 3.15; a beam projection on both thick faces, the
    axis line and an area outline on the thin wall's face."""
    walls = [R.wall((3.3, 0.0), (3.3, 1.3), 0.3, entity="shear_s"), R.wall((3.3, 5.7), (3.3, 7.7), 0.3,
                                                                           entity="shear_n"),
             R.wall((3.25, 3.15), (3.9, 3.15), 0.1, entity="niche")]
    if lining:
        walls += [R.wall((3.2, 1.0), (3.2, 3.95), 0.1, entity="duvar_a"), R.wall((3.2, 5.0), (3.2, 7.2), 0.1,
                                                                                  entity="duvar_b")]
    strokes = [R.stroke(R.rect(3.15, 1.3, 3.45, 5.7), closed=True), R.stroke([(3.15, -1.0), (3.15, 9.0)]),
               R.stroke([(3.25, 1.3), (3.25, 3.1)])]
    if glass:                                                   # real glass in the open part of the band
        strokes += [R.stroke([(3.33, 1.3), (3.33, 3.1)]), R.stroke([(3.37, 1.3), (3.37, 3.1)])]
    return walls, strokes


def test_a_thinner_wall_along_one_face_splits_the_thick_run():
    out_walls, openings, log, _ = _run(*_partition())
    thick = _vertical(out_walls, 3.3, 0.3)
    assert [span for span, _ in thick] == [(0.0, 1.3), (5.7, 7.7)]
    for _, w in thick:
        assert w.corrected_by_ai["before"] == {"start": [3.3, 0.0], "end": [3.3, 7.7], "thickness": 0.3}
        assert "a 0.10 m wall (duvar_a, duvar_b)" in w.corrected_by_ai["reason"]
    assert not [o for o in openings if o.kind == "window"]
    # The thin wall's own gap stays the passage.
    assert [(o.kind, o.center, o.width) for o in openings] == [("opening", (3.2, 4.475), pytest.approx(1.05))]
    assert [e["class"] for e in log if e.get("lining")] == ["open", "open"]


def test_without_the_thin_wall_or_with_glass_beside_it_there_is_no_lining():
    out_walls, _, log, _ = _run(*_partition(lining=False))
    assert not [e for e in log if e.get("lining")]
    assert not [w for w in out_walls if getattr(w, "corrected_by_ai", None)]
    # One 1.8 m gap between two thick pieces with the thin wall along its face: lined, unless glass lies in the open
    # part of the band beside the thin wall (a sill strip drawn on the wall layer in front of a real window): then
    # the window stays and the run stays one wall.
    walls = [R.wall((3.3, 0.0), (3.3, 1.3), 0.3), R.wall((3.3, 3.1), (3.3, 4.4), 0.3),
             R.wall((3.2, 1.0), (3.2, 3.4), 0.1, entity="strip")]
    beam = R.stroke(R.rect(3.15, 1.3, 3.45, 3.1), closed=True)
    glass = [R.stroke([(3.33, 1.3), (3.33, 3.1)]), R.stroke([(3.37, 1.3), (3.37, 3.1)])]
    out_walls, openings, log, _ = _run(walls, [beam] + glass)
    assert not [e for e in log if e.get("lining")]
    assert [span for span, _ in _vertical(out_walls, 3.3, 0.3)] == [(0.0, 4.4)]
    assert [(o.kind, round(o.center[1], 3)) for o in openings] == [("window", 2.2)]
    out_walls, openings, log, _ = _run(walls, [beam])
    assert [e["class"] for e in log if e.get("lining")] == ["open"]
    assert [span for span, _ in _vertical(out_walls, 3.3, 0.3)] == [(0.0, 1.3), (3.1, 4.4)]
    assert openings == []


def test_a_thin_piece_only_as_long_as_the_gap_is_no_lining():
    """real02 L1: a 0.05 m piece inside the party-wall junction, exactly as long as the 0.40 m gap of the 0.15 m wall
    there; the wall stays one wall (its gap stays as before)."""
    walls = [R.wall((1.8, 7.517), (7.386, 7.517), 0.15), R.wall((7.786, 7.517), (13.372, 7.517), 0.15),
             R.wall((7.386, 7.566), (7.786, 7.566), 0.05), R.wall((7.586, 0.2), (7.586, 7.442), 0.4),
             R.wall((7.586, 7.59), (7.586, 9.734), 0.4)]
    out_walls, openings, log, _ = _run(walls, [])
    assert not [e for e in log if e.get("lining")]
    assert not [w for w in out_walls if getattr(w, "corrected_by_ai", None)]
    assert [(round(w.start[0], 3), round(w.end[0], 3)) for w in out_walls if w.thickness == 0.15] == [(1.8, 13.372)]


def test_a_lining_that_stops_in_the_gap_is_no_lining():
    """Review of the fix round: the thinner wall must run through the gap as one wall (its pieces apart by its own
    gaps <= GAP_MAX_M, ``_chains``). Here it stops 0.7 m before the far jamb and its next piece lies 5.6 m on: the
    gap is no lined gap, the thick run stays one wall with its doorway (the first version counted the far piece as
    reach and left a 0.7 m hole with no wall and no opening)."""
    walls = [R.wall((0, 0), (1.3, 0), 0.3), R.wall((3.1, 0), (4.4, 0), 0.3),
             R.wall((1.0, -0.1), (2.4, -0.1), 0.1, entity="lining_a"), R.wall((8.0, -0.1), (9.0, -0.1), 0.1,
                                                                             entity="lining_far")]
    out_walls, openings, log, _ = _run(walls, [])
    assert not [e for e in log if e.get("lining")]
    assert [(w.start, w.end) for w in out_walls if w.thickness == 0.3] == [((0.0, 0.0), (4.4, 0.0))]
    assert [(o.kind, round(o.center[0], 2)) for o in openings] == [("opening", 2.2)]
    # The same lining running on past the far jamb (with its own 0.8 m passage in the gap) lines it.
    walls[2:] = [R.wall((1.0, -0.1), (1.8, -0.1), 0.1, entity="lining_a"),
                 R.wall((2.6, -0.1), (5.0, -0.1), 0.1, entity="lining_b")]
    out_walls, openings, log, _ = _run(walls, [])
    assert [e["class"] for e in log if e.get("lining")] == ["open"]
    assert [(w.start, w.end) for w in out_walls if w.thickness == 0.3] == [((0.0, 0.0), (1.3, 0.0)),
                                                                            ((3.1, 0.0), (4.4, 0.0))]
    assert [(o.kind, round(o.center[0], 2), round(o.width, 2)) for o in openings] == [("opening", 2.2, 0.8)]


def test_a_door_in_the_gap_is_never_lined():
    walls, strokes = _partition()
    strokes += [R.arc((3.45, 1.3), 1.8, 90, 180)]                 # a 1.8 m swing hinged at the shear wall's face
    _, openings, log, _ = _run(walls, strokes)
    assert not [e for e in log if e.get("lining") and e["p0"][1] < 3.15]


# --------------------------------------------------------------------------
# Gaps inside wall material
# --------------------------------------------------------------------------

def test_a_gap_inside_another_piece_is_closed_not_an_opening():
    """real03's core: the 0.62 m core piece covers the gap the decomposition left in the 0.10 m run."""
    walls = [R.wall((0, 0), (2, 0), 0.1), R.wall((2.6, 0), (5, 0), 0.1), R.wall((1.9, 0.25), (2.7, 0.25), 0.6,
                                                                                 entity="core")]
    out_walls, openings, log, _ = _run(walls, [])
    assert openings == []
    thin = [w for w in out_walls if w.thickness == 0.1]
    assert [(w.start, w.end) for w in thin] == [((0.0, 0.0), (5.0, 0.0))]
    entry = [e for e in log if e["kind"] == "run" and e["width"] == pytest.approx(0.6)][0]
    assert entry["class"] == "closed" and "inside wall material" in entry["note"] and "warning" not in entry
    # A piece that covers only part of the band, or only part of the gap, is no cover: the gap stays a doorway.
    for core_wall in (R.wall((1.9, 0.3), (2.7, 0.3), 0.5), R.wall((2.1, 0.25), (2.7, 0.25), 0.6)):
        _, openings, _, _ = _run(walls[:2] + [core_wall], [])
        assert [o.kind for o in openings] == ["opening"]


def test_a_door_symbol_in_a_covered_gap_keeps_its_door():
    """Review of the fix round (23 Oct 2026): a drawn swing outranks the decomposition. A 0.9 m gap of a 0.10 m run
    that a 0.30 m piece covers, with a door arc hinged at its jamb, stays a door (the first version closed it as wall
    material before classifying it). Fails when ``_inside_wall`` also runs on door gaps."""
    walls = [R.wall((0, 0), (2, 0), 0.1), R.wall((2.9, 0), (5, 0), 0.1), R.wall((1.9, 0), (3.0, 0), 0.3,
                                                                                 entity="core")]
    swing = R.arc((2.0, 0.05), 0.9, 0, 90)
    _, openings, log, _ = _run(walls, [swing])
    assert [(o.kind, round(o.width, 2)) for o in openings] == [("door", 0.9)]
    assert [e["class"] for e in log if e["kind"] == "run" and e["width"] == pytest.approx(0.9)] == ["door"]
    # Without the swing the same gap is wall material.
    _, openings, log, _ = _run(walls, [])
    assert openings == [] and [e.get("rule") for e in log if e["kind"] == "run"] == ["inside_wall"]


# --------------------------------------------------------------------------
# Windows need glass
# --------------------------------------------------------------------------

def test_lines_on_the_faces_running_past_the_gap_are_no_window():
    """A beam projection on both faces and the axis line (real03's 'windows' between columns): no glass."""
    walls = [R.wall((0, 0), (2, 0), 0.3), R.wall((3.5, 0), (5, 0), 0.3)]
    beam = R.stroke(R.rect(-0.5, -0.15, 6.0, 0.15), closed=True)
    axis = R.stroke([(-2.0, 0.15), (8.0, 0.15)])
    _, openings, log, _ = _run(walls, [beam, axis])
    assert [(o.kind, o.type_raw) for o in openings] == [("opening", "unclassified gap content")]
    assert "0 of them ending at its jambs and 0 glass" in openings[0].evidence["note"]
    # The real03 window symbol (CAM-PER frame on the faces, two frame lines and the panes inside): a window.
    frame = [R.stroke(R.rect(2.0, -0.15, 3.5, 0.15), closed=True), R.stroke([(2.06, -0.03), (3.44, -0.03)]),
             R.stroke([(2.06, 0.03), (3.44, 0.03)]), R.stroke(R.rect(2.06, -0.01, 3.44, 0.01), closed=True)]
    _, openings, log, _ = _run(walls, [beam, axis] + frame)
    assert [o.kind for o in openings] == ["window"]
    assert [e["class"] for e in log if e["kind"] == "run"] == ["window"]
    # One line of its own alone is not enough (an area outline along a thin wall's face inside a thick band) ...
    _, openings, _, _ = _run(walls, [beam, axis, R.stroke([(2.0, 0.05), (3.5, 0.05)])])
    assert [o.kind for o in openings] == ["opening"]
    # ... nor two on the faces without glass between them (a door leaf drawn closed in the wall plane, real03's
    # flat entrance); the synthetic convention (both faces and the glass, ending at the jambs) is a window.
    leaf = [R.stroke([(2.0, -0.15), (3.5, -0.15)]), R.stroke([(2.0, 0.15), (3.5, 0.15)])]
    _, openings, _, _ = _run(walls, [beam, axis] + leaf)
    assert [o.kind for o in openings] == ["opening"]
    _, openings, _, _ = _run(walls, [beam, axis] + leaf + [R.stroke([(2.0, 0.0), (3.5, 0.0)])])
    assert [o.kind for o in openings] == ["window"]


def test_traced_raster_lines_keep_the_old_window_rule():
    """A scan's or photo's double-line walls: the traced window lines carry the tracing's error at their ends and
    offsets, so lines on the faces still make a window there (synthetic-02's scan keeps its windows)."""
    walls = [R.wall((0, 0), (2, 0), 0.3), R.wall((3.5, 0), (5, 0), 0.3)]
    lines = [R.stroke([(1.9, -0.15), (3.6, -0.15)]), R.stroke([(1.9, 0.15), (3.6, 0.15)])]
    for st in lines:
        st.source = "raster"
    _, openings, _, _ = _run(walls, lines)
    assert [o.kind for o in openings] == ["window"]
    wall = R.wall((0, 0), (6, 0), 0.6)
    outline = R.stroke(R.rect(-0.3, -0.3, 6.3, 0.0), closed=True)
    outline.source = "raster"
    faces = R.wall_faces(wall)
    for st in faces:
        st.source = "raster"
    _, openings, _, _ = O.gaps_and_openings([wall], [outline] + faces, "scan.png", 1, units_to_m=0.001)
    assert [o.kind for o in openings] == ["window"]


def test_outlines_inside_a_thick_continuous_wall_are_no_window():
    """real03's core: a shear wall outline inside a 0.60 m wall piece; real04: wardrobe backs along a 0.12 m
    partition. Neither has two glass lines confined to the window."""
    core_wall = R.wall((0, 0), (1.4, 0), 0.6)
    outline = R.stroke(R.rect(-0.3, -0.3, 1.7, 0.0), closed=True)     # runs past both ends of the piece
    _, openings, _, _ = _run([core_wall], [outline] + R.wall_faces(core_wall))
    assert openings == []
    # real04: the 2.09 m wardrobe backs on both faces run 0.11 m past the 1.87 m line between them.
    part = R.wall((0, 0), (4, 0), 0.12)
    wardrobes = [R.stroke(R.rect(0.3, 0.06, 2.39, 0.66), closed=True), R.stroke(R.rect(0.3, -0.645, 2.39, -0.06),
                                                                               closed=True),
                 R.stroke([(0.41, -0.039), (2.28, -0.039)])]
    _, openings, _, _ = _run([part], wardrobes)
    assert openings == []
    # The synthetic convention (both faces and one glass line, all ending at the jambs) is a window.
    synthetic = [R.stroke([(0.41, 0.06), (2.28, 0.06)]), R.stroke([(0.41, -0.06), (2.28, -0.06)]),
                 R.stroke([(0.41, 0.0), (2.28, 0.0)])]
    _, openings, _, _ = _run([part], synthetic)
    assert [(o.kind, o.width) for o in openings] == [("window", pytest.approx(1.87))]
    # Fixtures drawn into a thick wall's band (real03's sanitary ware in a 0.45 m duct wall): their edges end with
    # the piece, but the shapes stand out of the band, so they are no window lines.
    duct = R.wall((0, 0), (4, 0), 0.45)
    fixtures = [R.stroke(R.rect(1.0, -0.104, 1.5, 0.6), closed=True), R.stroke(R.rect(1.0, 0.05, 1.5, 0.7),
                                                                            closed=True)]
    _, openings, _, _ = _run([duct], fixtures + R.wall_faces(duct))
    assert openings == []
    # A cistern inside the band beside the face: its two long edges end with it, but only the face lies beside the
    # inner one: no glass between two lines of a window.
    cistern = [R.stroke(R.rect(1.0, 0.104, 1.5, 0.224), closed=True)]
    _, openings, _, _ = _run([duct], cistern + R.wall_faces(duct))
    assert openings == []
    # A real continuous-wall window (two frame lines inside, confined to the window) is kept.
    wall = R.wall((0, 0), (6, 0), 0.15)
    win = [R.stroke(R.rect(2.0, -0.075, 3.6, 0.075), closed=True), R.stroke([(2.06, -0.03), (3.54, -0.03)]),
           R.stroke([(2.06, 0.03), (3.54, 0.03)])]
    _, openings, _, _ = _run([wall], win + R.wall_faces(wall))
    assert [(o.kind, o.width) for o in openings] == [("window", pytest.approx(1.48))]     # the frame lines


# --------------------------------------------------------------------------
# Walls drawn across a gap on a wall layer
# --------------------------------------------------------------------------

DUVAR = "D BLOK_MERDİVEN_NK$0$MYD - DUVAR"          # real03's stair-core wall layer (LibreDWG strokes)
ALAN_NET = "D BLOK_ZK$0$MYD - ALAN-NET"              # its net-area (room) outlines


def _layered(st, layer):
    st.layer = layer
    return st


def test_a_wall_layer_outline_across_a_gap_continues_the_wall():
    """real03's stair core (the LibreDWG strokes of tekkat.dwg): the two stair-core walls are DUVAR outlines (0.15 m,
    INSERT:7C9C9/21/0 and /21/84) with a door block inside, so no wall primitive. P6b read their gaps as 1.55 m
    'windows' (from the area outlines and beam lines on their faces): an end gap at y 8.925 from the door's wall piece
    to the column, and a run gap at y 7.475 between the floor hall and the fire stair. Both faces are drawn across on
    the wall layer: the wall continues (closed, no opening). Fails on BASE (a window each); the review of the fix
    round's first version (any lines on both faces, end gaps only) left the run gap an unverified 1.55 m opening."""
    column = R.wall((0, -1), (0, 1), 0.3)
    wall = R.wall((1.7, 0), (3.0, 0), 0.15)
    duvar = _layered(R.stroke(R.rect(0.15, -0.075, 3.0, 0.075), closed=True), DUVAR)
    out_walls, openings, log, _ = _run([column, wall], [duvar])
    assert openings == []
    horiz = [w for w in out_walls if w.start[1] == 0.0 and w.end[1] == 0.0]
    assert len(horiz) == 1 and sorted((horiz[0].start[0], horiz[0].end[0])) == [pytest.approx(0.15), 3.0]
    assert horiz[0].evidence["method"] == "derived"
    assert "both faces of the wall are drawn on" in horiz[0].evidence["note"] and "MYD - DUVAR" in \
        horiz[0].evidence["note"]
    entry = [e for e in log if e["kind"] == "end"][0]
    assert entry["class"] == "closed" and "warning" not in entry and entry["rule"] == "wall_faces"
    # The run gap (y 7.475): a wall piece on both sides, the outline under them: one wall, no opening.
    left = R.wall((-1.5, 0), (0.6, 0), 0.15)
    out_walls, openings, log, _ = _run([left, wall], [_layered(R.stroke(R.rect(-1.5, -0.075, 3.0, 0.075),
                                                                         closed=True), DUVAR)])
    assert openings == [] and [(w.start, w.end) for w in out_walls] == [((-1.5, 0.0), (3.0, 0.0))]
    assert [(e["class"], e.get("rule")) for e in log if e["kind"] == "run"] == [("closed", "wall_faces")]


def test_only_wall_geometry_across_a_gap_closes_it():
    """Room outlines (ALAN-NET), lines without a layer, a wall-layer line on one face only or over part of the gap,
    and a swing reaching in keep the gap: a doorless passage whose room outlines close across it stays a passage
    (run gap: an unverified opening; end gap: a candidate, no wall extended)."""
    column = R.wall((0, -1), (0, 1), 0.3)
    wall = R.wall((1.7, 0), (3.0, 0), 0.15)
    left = R.wall((-1.5, 0), (0.6, 0), 0.15)

    def faces(layer, x0=-1.5, x1=3.0, sides=(-0.075, 0.075)):
        return [_layered(R.stroke([(x0, y), (x1, y)]), layer) for y in sides]

    # (the last: wall-layer lines over 82-87 % of the gap, ending 0.2 m short of the far jamb)
    for strokes in (faces(ALAN_NET), faces(None), faces(DUVAR, sides=(0.075,)) + faces(ALAN_NET, sides=(-0.075,)),
                    faces(DUVAR, x0=1.0) + faces(DUVAR, x0=-1.5, x1=0.8), faces(DUVAR, x1=1.5)):
        _, openings, log, _ = _run([left, wall], strokes)
        assert [(o.kind, o.type_raw) for o in openings] == [("opening", "unclassified gap content")]
        assert [e["class"] for e in log if e["kind"] == "run"] == ["unclassified"]
        _, openings, log, _ = _run([column, wall], strokes)
        assert openings == [] and [e["class"] for e in log if e["kind"] == "end"] == ["unclassified"]
    # A swing reaching into the gap keeps it (no wall across a door).
    swing = R.arc((0.6, 0.075), 1.0, 0, 90)
    _, _, log, _ = _run([left, wall], faces(DUVAR) + [swing])
    assert [e["class"] for e in log if e["kind"] == "run"] != ["closed"]
    # Wall-layer face lines confined to the gap (a threshold drawn on the wall layer) are no wall across it either.
    _, _, log, _ = _run([column, wall], faces(DUVAR, x0=0.15, x1=1.7))
    assert [e["class"] for e in log if e["kind"] == "end"] != ["closed"]


# --------------------------------------------------------------------------
# The label travels
# --------------------------------------------------------------------------

def test_the_corrected_label_survives_trimming_and_the_building_shift():
    w = R.wall((0, 0), (2, 0), 0.3)
    w.corrected_by_ai = {"reason": "r", "before": {"start": [0.0, 0.0], "end": [5.0, 0.0], "thickness": 0.3}}
    moved = O._replace_wall(w, start=(0.1, 0.0))
    assert moved.corrected_by_ai is w.corrected_by_ai and moved.start == (0.1, 0.0)
    core._shift_wall(moved, core._Shift(1.0, 2.0))
    assert moved.start == (-0.9, -2.0)
    assert moved.corrected_by_ai["before"]["start"] == [-1.0, -2.0]
    assert moved.corrected_by_ai["before"]["end"] == [4.0, -2.0]
    plain = R.wall((0, 0), (1, 0))
    core._shift_wall(plain, core._Shift(1.0, 0.0))
    assert not getattr(plain, "corrected_by_ai", None)


def test_the_page_notes_list_the_gap_rules_and_the_corrected_walls(real03_hall):
    """CLAUDE.md: nothing changes silently. ``core.gap_rule_notes`` gives one note per rule with the gaps it decided
    (building metres) and one per wall marked ``corrected_by_ai``; ``core.extract`` adds them to the page notes (the
    ingest report's Notes). real03's partition: 4 lined gaps, the 3 shear walls."""
    out_walls, _, log, _ = real03_hall
    notes = core.gap_rule_notes(log, out_walls, (1.0, 2.0))
    lined = [n for n in notes if "lined by a thinner wall" in n]
    assert len(lined) == 1 and lined[0].startswith("4 gap(s)") and "(2.30, -0.70)-(2.30, 1.10) 1.80 m" in lined[0]
    inside = [n for n in notes if "inside wall material" in n]
    assert len(inside) == 1 and inside[0].startswith("13 gap(s)") and "(2.20, 4.00)-(2.20, 4.56) 0.56 m" in inside[0]
    walls = [n for n in notes if "corrected_by_ai (lined_gap)" in n]
    assert len(walls) == 3 and all("read as 3 walls, not one 0.30 m wall" in n for n in walls)
    assert core.gap_rule_notes([{"kind": "run", "class": "door", "p0": [0, 0], "p1": [1, 0], "width": 1.0}],
                               [R.wall((0, 0), (1, 0))], (0.0, 0.0)) == []


def test_core_extract_adds_the_gap_rule_notes(tmp_path, monkeypatch):
    """The wiring: ``core.extract`` passes the gap log, its building walls and the frame origin to
    ``gap_rule_notes`` and keeps the notes (the hand-made DXF of tests/test_outline_walls.py, walls hatched; the
    openings step is wrapped to add one lined-gap entry and one corrected wall). Fails without the call."""
    import test_outline_walls as OW
    from wenart.ingest import dxf_generic as DG

    real = O.gaps_and_openings

    def wrapped(walls, strokes, file_rel, page_no, units_to_m=None):
        out_walls, openings, log, owned = real(walls, strokes, file_rel, page_no, units_to_m=units_to_m)
        out_walls[0].corrected_by_ai = {"rule": "lined_gap", "reason": "stand-in reason",
                                        "before": {"start": [0.0, 0.0], "end": [1.0, 0.0], "thickness": 0.3}}
        log.append({"kind": "run", "class": "open", "width": 1.0, "p0": [2.0, 3.0], "p1": [3.0, 3.0],
                    "rule": "lined_gap"})
        return out_walls, openings, log, owned

    monkeypatch.setattr(core.O, "gaps_and_openings", wrapped)
    path = tmp_path / "plan.dxf"
    OW._plan(walls=True, frame=False).saveas(path)
    ex = core.extract(DG.read_page(path, "plan.dxf"), "L0", "plan.dxf", no_ai=True)
    ox, oy = ex.report["origin_m"]
    lined = [n for n in ex.notes if "lined by a thinner wall" in n]
    assert lined == [f"plan.dxf: 1 gap(s) {core.GAP_RULE_TEXT['lined_gap']} (fix round after P6b): "
                     f"({2.0 - ox:.2f}, {3.0 - oy:.2f})-({3.0 - ox:.2f}, {3.0 - oy:.2f}) 1.00 m"]
    assert [n for n in ex.notes if "corrected_by_ai (lined_gap): stand-in reason" in n]
