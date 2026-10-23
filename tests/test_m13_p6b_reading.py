"""Fix round after P6b (23 Oct 2026), track F_reading: walls and openings of the generic plan core.

Pod P6b (real03) showed three critical F7 findings on fridges beside 'doors' and four hall washers 0.14-0.19 m in a
wall. The verifiers traced both to the reading of real03's hall-living partition (LibreDWG strokes of
projects/real03/tekkat.dwg): the 30 cm shear walls (D BLOK_STA_NK) on the drawn 0.10 m partition (DUVAR) were read as
one 0.30 m wall from end to end, its gaps 'windows' made of the beam projections (IZ-1), the axis (AKS) and the area
outlines (ALAN-NET) lying on its faces. The rules checked here (``wenart.ingest.generic.openings``):

- a lined gap (a thinner wall along one face through the gap) is open and the thick pieces stay walls of their own,
  each marked ``corrected_by_ai`` (``_lining``, ``_mark_lined``);
- a gap inside other wall material is closed, never an opening (``_inside_wall``);
- a window needs glass: >= ``GLASS_MIN_LINES`` distinct lines strictly between the faces and within the gap +-
  ``OWN_MARGIN_M`` (``_is_glass``; gap windows and continuous-wall windows);
- an end gap whose two faces are drawn on across it, with no glass or swing, extends the wall (no opening).

``tests/fixtures/m13_p6b_real03_hall.json`` holds the real input walls and strokes around the partition (the P6b
building frame); every real window of real02, real03 and real04 carries two or three glass lines and still passes
(checked on their LibreDWG replays in the session).
"""
from __future__ import annotations

import json
import math
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
    return sorted(((w.start[1], w.end[1]) if w.start[1] < w.end[1] else (w.end[1], w.start[1]), w)
                  for w in out_walls if abs(w.start[0] - x) < 0.01 and abs(w.end[0] - x) < 0.01
                  and abs(w.thickness - t) < 0.006)


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
        walls += [R.wall((3.2, 1.3), (3.2, 3.95), 0.1, entity="duvar_a"), R.wall((3.2, 5.0), (3.2, 5.7), 0.1,
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
             R.wall((3.2, 1.3), (3.2, 3.1), 0.1, entity="strip")]
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
    assert "0 of them glass" in openings[0].evidence["note"]
    # The real03 window symbol (CAM-PER frame on the faces, two frame lines and the panes inside): a window.
    frame = [R.stroke(R.rect(2.0, -0.15, 3.5, 0.15), closed=True), R.stroke([(2.06, -0.03), (3.44, -0.03)]),
             R.stroke([(2.06, 0.03), (3.44, 0.03)]), R.stroke(R.rect(2.06, -0.01, 3.44, 0.01), closed=True)]
    _, openings, log, _ = _run(walls, [beam, axis] + frame)
    assert [o.kind for o in openings] == ["window"]
    assert [e["class"] for e in log if e["kind"] == "run"] == ["window"]
    # One glass line alone is not enough (an area outline along a thin wall's face inside a thick band).
    _, openings, _, _ = _run(walls, [beam, axis, R.stroke([(2.0, 0.05), (3.5, 0.05)])])
    assert [o.kind for o in openings] == ["opening"]


def test_outlines_inside_a_thick_continuous_wall_are_no_window():
    """real03's core: a shear wall outline inside a 0.60 m wall piece; real04: wardrobe backs along a 0.12 m
    partition. Neither has two glass lines confined to the window."""
    core_wall = R.wall((0, 0), (1.4, 0), 0.6)
    outline = R.stroke(R.rect(-0.3, -0.3, 1.7, 0.0), closed=True)     # runs past both ends of the piece
    _, openings, _, _ = _run([core_wall], [outline] + R.wall_faces(core_wall))
    assert openings == []
    part = R.wall((0, 0), (4, 0), 0.12)
    wardrobes = [R.stroke(R.rect(0.3, 0.06, 2.4, 0.66), closed=True), R.stroke(R.rect(0.3, -0.645, 2.4, -0.06),
                                                                              closed=True),
                 R.stroke([(0.3, 0.021), (2.4, 0.021)])]
    _, openings, _, _ = _run([part], wardrobes)
    assert openings == []
    # A real continuous-wall window (two frame lines inside, confined to the window) is kept.
    wall = R.wall((0, 0), (6, 0), 0.15)
    win = [R.stroke(R.rect(2.0, -0.075, 3.6, 0.075), closed=True), R.stroke([(2.06, -0.03), (3.54, -0.03)]),
           R.stroke([(2.06, 0.03), (3.54, 0.03)])]
    _, openings, _, _ = _run([wall], win + R.wall_faces(wall))
    assert [(o.kind, o.width) for o in openings] == [("window", pytest.approx(1.48))]     # the frame lines


# --------------------------------------------------------------------------
# End gaps whose faces are drawn across
# --------------------------------------------------------------------------

def test_an_end_gap_with_both_faces_drawn_on_extends_the_wall_without_an_opening():
    """real03's stair core: the room outlines on both faces run on across the gap from a free wall end to the
    column (the DUVAR outline there is no wall primitive); P6b read a 1.55 m window."""
    column = R.wall((0, -1), (0, 1), 0.3)
    wall = R.wall((1.7, 0), (3.0, 0), 0.15)
    faces = [R.stroke([(0.15, -0.075), (3.0, -0.075)]), R.stroke([(0.15, 0.075), (3.0, 0.075)])]
    out_walls, openings, log, _ = _run([column, wall], faces)
    assert openings == []
    horiz = [w for w in out_walls if w.start[1] == 0.0 and w.end[1] == 0.0]
    assert len(horiz) == 1 and sorted((horiz[0].start[0], horiz[0].end[0])) == [pytest.approx(0.15), 3.0]
    assert horiz[0].evidence["method"] == "derived"
    assert "both faces of the wall are drawn on" in horiz[0].evidence["note"]
    entry = [e for e in log if e["kind"] == "end"][0]
    assert entry["class"] == "closed" and "warning" not in entry and "both faces" in entry["note"]
    # A swing reaching into the gap keeps it an opening candidate (no wall across a door).
    _, _, log2, _ = _run([column, wall], faces + [R.arc((0.15, 0.075), 1.0, 0, 90)])
    assert [e["class"] for e in log2 if e["kind"] == "end"] != ["closed"]
    # Face lines confined to the gap (a threshold) are no wall: the gap stays a candidate.
    _, _, log3, _ = _run([column, wall], [R.stroke([(0.15, -0.075), (1.7, -0.075)]),
                                          R.stroke([(0.15, 0.075), (1.7, 0.075)])])
    assert [e["class"] for e in log3 if e["kind"] == "end"] != ["closed"]


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
