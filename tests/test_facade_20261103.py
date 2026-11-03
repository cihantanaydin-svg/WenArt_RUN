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


# ------------------------------------------------------------------ the storeys a section names at their floor marks
from wenart.sheets import heights as HT  # noqa: E402
from wenart.sheets import levels as LV  # noqa: E402
from wenart.sheets.model import Txt  # noqa: E402


def _section():
    """real09's B-B: the storeys named just above their floors, the floor marks and the sill / head marks between."""
    marks = [("±0.00", 0), ("+2.20", 220), ("+2.50", 250), ("+3.40", 340), ("+4.90", 490), ("+5.50", 550),
             ("+6.40", 640), ("+8.50", 850), ("+9.40", 940), ("+11.50", 1150), ("+15.20", 1520)]
    names = [("1.BODRUM KAT", 20), ("ZEMİN KAT", 275), ("1.NORMAL KAT", 575), ("2.NORMAL KAT", 875), ("ÇATI KAT", 1175)]
    texts = [Txt(id=f"m{k}", text=t, box=(-200, y, -150, y + 12), height=12.0) for k, (t, y) in enumerate(marks)]
    texts += [Txt(id=f"n{k}", text=t, box=(100, y, 220, y + 12), height=12.0) for k, (t, y) in enumerate(names)]
    return SimpleNamespace(texts=texts)


def test_the_storeys_a_section_names_take_their_floor_marks():
    got = LV.storey_elevations([_section()])
    assert got == {-1: 0.0, 0: 2.5, 1: 5.5, 2: 8.5, "top": 11.5}


def test_a_plan_titled_by_its_elevation_is_the_storey_at_that_level_and_the_floors_follow_the_marks():
    def plan(text):
        return SimpleNamespace(title={"text": text, "box": [0, 0, 1, 1]}, texts=[], evidence=[], file="x", id=text)
    plans = [plan("1.BODRUM KAT PLANI (0,00)"), plan("NORMAL KAT PLANI (2,50-5,50)"), plan("DUBLEKS KAT PLANI (8,50)"),
             plan("ÇATI KAT PLANI (11,50)")]
    words = {id(r): LV.level_of(r.title["text"]) for r in plans}
    storey_el = LV.storey_elevations([_section()])
    LV._by_storey_elevation(plans, words, storey_el, {2: "2. Normal Kat"}, [])
    assert words[id(plans[2])].order == 2 and words[id(plans[2])].label == "2. Normal Kat"
    levels = [{"id": f"L{o}", "order": o, "kind": "floor"} for o in (-1, 0, 1, 2, 3)]
    out = {"levels": [], "slabs": []}
    HT.apply_storey_marks(out, levels, storey_el, 0.2, "x.dwg", "r9")
    z = {e["level_id"]: e["floor_z"]["value"] for e in out["levels"]}
    assert z == {"L-1": -2.5, "L0": 0.0, "L1": 3.0, "L2": 6.0, "L3": 9.0}
    assert all(e["floor_z"]["method"] == "vector" for e in out["levels"])
