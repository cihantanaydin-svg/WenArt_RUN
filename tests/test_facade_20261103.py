"""3 Nov 2026 (user: "go ahead with the glazed facades"): rooms whose facade is drawn as window and door frames (and
short pieces on other layers) are closed along those frames (``wenart.ingest.generic.facade``). CPU only, pure."""
from __future__ import annotations

from types import SimpleNamespace

from shapely.geometry import Point

from wenart.ingest.generic import facade as FC
from wenart.ingest.generic import topology as TP
from wenart.ingest.generic.model import Stroke


def _wall(s, e, t=0.2):
    return SimpleNamespace(start=s, end=e, thickness=t, box=[0, 0, 0, 0], evidence={"file": "x.dwg", "entity": "W"},
                           entity="W", status="verified", inferred=False, exterior=False)


def _line(k, a, b, layer="kapı-pencere"):
    return Stroke(id=f"LINE:{k}", kind="line", pts=[a, b], layer=layer)


def _room():
    """A 5 x 4 m living room: walls on the north and the west side; its east side a window run (two frame lines)
    stopping 0.15 m short of the north wall; its south side a window frame ending 0.6 m from the window run's foot
    (an L-shaped gap at the south-east corner, a short wall on another layer there)."""
    walls = [_wall((0, 4), (5.2, 4)), _wall((0, 4.1), (0, -0.1)), _wall((0, 0), (1.0, 0))]
    strokes = [_line(1, (5.0, 3.75), (5.0, 0.6)), _line(2, (5.1, 3.75), (5.1, 0.6)),     # the east window run
               _line(3, (1.1, 0.0), (4.4, 0.0)), _line(4, (1.1, -0.08), (4.4, -0.08)),   # the south window
               _line(5, (2.0, 0.0), (2.4, 0.9)),                                       # a casement drawn open
               _line(6, (4.4, 0.0), (5.0, 0.6), layer="0")]                            # a short piece, other layer
    return walls, strokes


def test_a_room_with_a_facade_of_frames_is_closed():
    walls, strokes = _room()
    assert not any(f.contains(Point(2.5, 2.0)) for f in TP.faces(walls))             # open: no face holds it
    faces, links = FC.close_rooms(walls, strokes, [(2.5, 2.0)])
    assert 0 in faces and 17.0 < faces[0].area < 21.0
    assert links                                                                       # the gap at the corner
    new = FC.facade_wall_items(walls, list(faces.values()), [], "x.dwg", None)
    assert new and all(w.inferred and w.status == "unverified" and w.evidence["rule"] == "glazed_facade"
                       and w.evidence["method"] == "inferred" for w in new)
    assert any(f.contains(Point(2.5, 2.0)) for f in TP.faces(list(walls) + new))     # closed by the drawn + inferred


def test_frame_lines_keep_out_open_casements_and_door_leaves():
    leaf = _line(7, (6, 0), (6, 0.9))
    swing = Stroke(id="ARC:1", kind="arc", pts=[(6, 0.9), (6.9, 0)], layer="kapı-pencere",
                   arc={"center": (6.0, 0.0), "radius": 0.9, "start_deg": 0.0, "end_deg": 90.0})
    walls, strokes = _room()
    lines = FC.joinery_lines(strokes + [leaf, swing], theta=0.0)
    lengths = sorted(round(ln.length, 2) for ln in lines)
    assert 0.99 not in lengths and 0.9 not in lengths                                  # the casement, the door leaf
    assert lengths.count(3.15) == 2 and lengths.count(3.3) == 2                        # the frames stay
    assert all(ln.length > 0.5 for ln in lines)                                        # the 'other layer' piece is no frame


def test_framed_openings_are_windows_and_doors_by_their_swing():
    walls, strokes = _room()
    faces, _ = FC.close_rooms(walls, strokes, [(2.5, 2.0)])
    new = FC.facade_wall_items(walls, list(faces.values()), [], "x.dwg", None)
    got = FC.frame_windows(new, strokes, [], walls)
    assert got and {o.kind for o in got} == {"window"} and all(o.status == "unverified" for o in got)
    door = Stroke(id="ARC:2", kind="arc", pts=[(5.05, 3.0), (4.2, 2.2)], layer="kapı-pencere",
                  arc={"center": (5.05, 2.2), "radius": 0.85, "start_deg": 90.0, "end_deg": 180.0})
    got = FC.frame_windows(new, strokes + [door], [], walls)
    assert "door" in {o.kind for o in got}                                             # the balcony door's swing
