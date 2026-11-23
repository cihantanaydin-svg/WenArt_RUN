"""The stairs round of 23 Nov 2026 (the user's choice "Stairs"; lesson UL375 and after): the AI checks' drawing of a
stair (``critic_checks.draw_arch``, ``sheets.stair_record``), the stair reader's rules and their must-not-fire cases,
and the storey height cross-check against a stair's risers."""
from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _real01_page as R  # noqa: E402
from wenart.ingest.generic import symbols as SY  # noqa: E402
from wenart.ingest.generic import topology as TP  # noqa: E402
from wenart.ingest.generic.model import Stroke  # noqa: E402
from wenart.reading_check import critic as CR
from wenart.reading_check import critic_checks as CC
from wenart.reading_check import sheets as SH

BOX = [0.0, 0.0, 20.0, 10.0]
TF = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]


def _stair_piece(**kw):
    f = {"id": "f_L0_001", "level_id": "L0", "type": "stair",
         "footprint": {"center": [10.0, 5.0], "size": [4.0, 1.2], "rotation_deg": 0.0}}
    f.update(kw)
    return f


FLIGHT = {"start": [8.2, 5.0], "end": [11.8, 5.0], "width": 1.2, "lines": 13, "spacing": 0.3}


def _dark_inside(path, box_px) -> int:
    from PIL import Image

    im = Image.open(path).convert("L")
    x0, y0, x1, y1 = box_px
    return sum(1 for x in range(x0, x1) for y in range(y0, y1) if im.getpixel((x, y)) < 200)


def _draw(tmp_path, piece, name):
    b = {"levels": [{"id": "L0", "elevation": 0.0}], "walls": [], "openings": [], "rooms": [], "site": {},
         "furniture": [piece]}
    fig, ax = CR._figure(BOX, (800, 400))
    CC.draw_arch(ax, b, "L0", TF)
    texts = [t.get_text() for t in ax.texts]
    return CR._save(fig, ax, BOX, (800, 400), tmp_path / name), texts


# ================================================================================ the AI checks' drawing of a stair
def test_stair_record_flights_win_over_a_later_mark():
    # the fire-escape mark (details.stair without flights) no longer hides the reader's flights
    f = _stair_piece(stair={"flights": [FLIGHT], "turn": "straight", "landing": None},
                     details={"stair": {"fire_escape": True, "fire_escape_reason": "named a fire stair"}})
    rec = SH.stair_record(f)
    assert rec["flights"] == [FLIGHT] and rec["fire_escape"] is True and rec["turn"] == "straight"
    # flights only in details.stair are found too; nothing anywhere gives none
    assert SH.stair_record(_stair_piece(details={"stair": {"flights": [FLIGHT]}}))["flights"] == [FLIGHT]
    assert not SH.stair_record(_stair_piece()).get("flights")
    assert not SH.stair_record(_stair_piece(details={"stair": {"fire_escape": True}})).get("flights")


def test_a_fire_stair_is_drawn_with_its_treads(tmp_path):
    f = _stair_piece(stair={"flights": [FLIGHT], "turn": "straight"},
                     details={"stair": {"fire_escape": True, "fire_escape_reason": "named a fire stair"}})
    p, texts = _draw(tmp_path, f, "fire.jpg")
    # the stair box spans x 8-12 m, y 4.4-5.6 m: 320-480 px across, 176-224 px down (40 px a metre)
    inside = _dark_inside(p, (330, 182, 470, 218))
    assert inside > 300                                     # 13 tread lines and the arrow
    assert "stair, flights unread" not in texts


def test_a_stair_without_flights_is_marked_unread(tmp_path):
    p, texts = _draw(tmp_path, _stair_piece(details={"stair": {"fire_escape": True}}), "unread.jpg")
    assert "stair, flights unread" in texts
    p2, texts2 = _draw(tmp_path, _stair_piece(stair={"flights": [FLIGHT]}), "read.jpg")
    assert "stair, flights unread" not in texts2


# ================================================================================ the stair reader's rules
TABLE = SY.FALLBACK_SIZE_TABLE
_N = [0]


def _s(pts, layer=None, closed=False):
    _N[0] += 1
    pts = [tuple(map(float, p)) for p in pts]
    return Stroke(id=f"t:{_N[0]}", kind="line" if len(pts) == 2 and not closed else "polyline", pts=pts,
                  closed=closed, colour=(0.0, 0.0, 0.0), layer=layer)


def _room(x0=0.0, y0=0.0, x1=10.0, y1=8.0, t=0.2):
    return [R.wall((x0, y0), (x1, y0), t), R.wall((x1, y0), (x1, y1), t), R.wall((x1, y1), (x0, y1), t),
            R.wall((x0, y1), (x0, y0), t)]


def _furn(strokes, walls=None, texts=(), notes=None):
    walls = walls or _room()
    outline = TP.building_outline(walls, [])
    return SY.furniture(strokes, set(), walls, [], list(texts), [], outline, [], level_id="L0", file_rel="t.dxf",
                        page_no=1, size_table=TABLE, notes=notes if notes is not None else [])


def _rot(p, deg, c=(0.0, 0.0)):
    a = math.radians(deg)
    x, y = p[0] - c[0], p[1] - c[1]
    return (c[0] + x * math.cos(a) - y * math.sin(a), c[1] + x * math.sin(a) + y * math.cos(a))


def _flight(x0, y0, width, step, n, deg=0.0, layer=None, outline=True, arrow=True, skew=0.0):
    """A straight flight rising along +y: n tread lines ``step`` apart, its outline, a walking line with an arrow head,
    turned ``deg`` about its first corner; ``skew`` turns only the outline (an outline drawn askew)."""
    c = (x0, y0)
    L = (n + 1) * step
    out = [_s([_rot((x0, y0 + k * step), deg, c), _rot((x0 + width, y0 + k * step), deg, c)], layer)
           for k in range(1, n + 1)]
    if outline:
        ring = [(x0, y0), (x0 + width, y0), (x0 + width, y0 + L), (x0, y0 + L)]
        ring = [_rot(_rot(p, skew, c), deg, c) for p in ring]
        out += [_s([ring[i], ring[(i + 1) % 4]], layer) for i in range(4)]
    if arrow:
        xm = x0 + width / 2
        tip = (xm, y0 + L - step / 2)
        out += [_s([_rot((xm, y0 + step / 2), deg, c), _rot(tip, deg, c)], layer),
                _s([_rot(tip, deg, c), _rot((xm - 0.08, tip[1] - 0.15), deg, c)], layer),
                _s([_rot(tip, deg, c), _rot((xm + 0.08, tip[1] - 0.15), deg, c)], layer)]
    return out


def _stairs(pieces):
    return [p for p in pieces if p.type == "stair"]


class _T:
    def __init__(self, text, box, height=0.12):
        self.text, self.box, self.height = text, box, height


def test_an_angled_flight_is_read_in_its_own_frame():
    pieces, _c, _d = _furn(_flight(3.0, 2.0, 1.1, 0.28, 10, deg=5.0))
    st = _stairs(pieces)
    assert len(st) == 1
    rec = st[0].details["stair"]
    assert rec["angled_deg"] == pytest.approx(5.0, abs=0.3) and len(rec["flights"]) == 1
    assert rec["flights"][0]["lines"] >= 10


def test_own_angle_needs_parallel_lines_and_a_real_turn():
    cl = SY.Cluster(SY._segments(_flight(3.0, 2.0, 1.1, 0.28, 10, deg=0.4), set()))
    assert SY.own_angle(cl, 0.0) is None                 # under ANGLED_MIN_DEG: the plan's own frame
    few = SY.Cluster(SY._segments([_s([(0, 0), (1, 0.1)]), _s([(0, 1), (1, 1.1)])], set()))
    assert SY.own_angle(few, 0.0) is None


def test_must_not_fire_an_angled_grille_or_tile_grid():
    # a grille turned 5 degrees: lines 0.10 m apart (finer than any going) is no stair
    grille = [_s([_rot((3.0, 2.0 + 0.1 * k), 5.0, (3, 2)), _rot((4.2, 2.0 + 0.1 * k), 5.0, (3, 2))]) for k in range(15)]
    assert not _stairs(_furn(grille)[0])
    # a tile grid turned 5 degrees: 0.30 m both ways
    grid = [_s([_rot((3.0, 2.0 + 0.3 * k), 5.0, (3, 2)), _rot((4.8, 2.0 + 0.3 * k), 5.0, (3, 2))]) for k in range(7)]
    grid += [_s([_rot((3.0 + 0.3 * k, 2.0), 5.0, (3, 2)), _rot((3.0 + 0.3 * k, 3.8), 5.0, (3, 2))]) for k in range(7)]
    assert not _stairs(_furn(grid)[0])


def test_a_straight_flight_of_a_whole_storey_is_longer_than_furniture():
    # 18 treads at 0.28 m: 5.3 m long, over MAX_SIDE_M (4.5 m), under STAIR_MAX_M (6.0 m)
    pieces, _c, _d = _furn(_flight(3.0, 1.0, 1.0, 0.28, 18))
    st = _stairs(pieces)
    assert len(st) == 1 and max(st[0].size) > SY.MAX_SIDE_M
    assert SY.STAIR_MAX_M >= 5.7


def test_the_walking_line_does_not_split_a_wide_flight():
    # a 1.5 m flight with its walking line (arrow head) down the middle: one flight, not a U of two 0.75 m flights
    st = _stairs(_furn(_flight(3.0, 2.0, 1.5, 0.28, 10))[0])
    assert len(st) == 1 and len(st[0].details["stair"]["flights"]) == 1
    assert st[0].details["stair"]["flights"][0]["width"] == pytest.approx(1.5, abs=0.02)


def test_must_not_fire_the_line_between_two_flights_still_splits_a_u_stair():
    # two flights side by side with the line between them (no arrow head on it): a U stair of two flights
    strokes = [_s([(3.0, 2.0 + 0.25 * k), (4.6, 2.0 + 0.25 * k)]) for k in range(8)]
    strokes.append(_s([(3.8, 2.0), (3.8, 2.0 + 7 * 0.25 + 1.0)]))
    st = _stairs(_furn(strokes)[0])
    assert len(st) == 1 and len(st[0].details["stair"]["flights"]) == 2


def test_arrow_end_reads_an_arrow_head_only():
    shaft = _s([(0.0, 0.0), (0.0, 2.0)])
    heads = [_s([(0.0, 2.0), (-0.08, 1.85)]), _s([(0.0, 2.0), (0.08, 1.85)])]
    segs = SY._segments([shaft] + heads, set())
    assert SY.arrow_end([s for s in segs if s.length > 1.0][0], segs)
    tee = SY._segments([shaft, _s([(-0.1, 2.0), (0.1, 2.0)])], set())          # a stringer's end tick: no arrow
    assert not SY.arrow_end([s for s in tee if s.length > 1.0][0], tee)


def test_an_outline_drawn_askew_keeps_its_end_lines():
    # 4 treads only, the outline askew by 0.5 degrees: its two ends make the 6 lines of a flight
    assert len(_stairs(_furn(_flight(3.0, 2.0, 0.9, 0.3, 4, skew=0.5, arrow=False))[0])) == 1


def test_split_strips_join_on_the_treads_they_share():
    a = {"offsets": [0.3 * k for k in range(9)], "u": 0.0, "v": 0.48, "lines": 9, "spacing": 0.3, "segs": []}
    b = {"offsets": [0.3 * k for k in range(7)], "u": 0.48, "v": 0.77, "lines": 7, "spacing": 0.3, "segs": []}
    out = SY._join_split_strips([a, b])
    assert len(out) == 1 and out[0]["lines"] == 7 and out[0]["v"] == pytest.approx(0.77)
    c = dict(b, offsets=[0.0, 0.3, 0.6], lines=3)              # must not fire: 3 shared treads of 9
    assert len(SY._join_split_strips([a, c])) == 2


def test_a_tread_under_a_room_label_stays_a_tread():
    strokes = _flight(3.0, 2.0, 0.85, 0.3, 6, layer="A-MERDIVEN", outline=False)
    texts = [_T("MERDIVEN ALAN 1.89 M2", (2.9, 2.85, 3.95, 3.05), 0.15)]      # holds the tread at y 2.9 whole
    assert len(_stairs(_furn(strokes, texts=texts)[0])) == 1
    # a stroke on another layer under the same text is still a glyph (the old rule)
    assert not SY._stair_layer_line(SY._segments([_s([(3.0, 2.9), (3.85, 2.9)], layer="YAZI")], set())[0])


def test_the_stair_layer_is_read_on_its_own_outside_a_broken_outline():
    # walls that close no ring (an open U of walls): the building outline is the walls only; the flight on the stair
    # layer inside the walls' hull is read; the same lines on a furniture layer are not
    walls = [R.wall((0, 0), (10, 0)), R.wall((0, 0), (0, 8)), R.wall((10, 0), (10, 8))]
    st = _stairs(_furn(_flight(4.0, 2.0, 1.0, 0.28, 10, layer="MERDIVEN"), walls=walls)[0])
    assert len(st) == 1 and st[0].details["stair"].get("read_by") == "stair layer"
    assert not _stairs(_furn(_flight(4.0, 2.0, 1.0, 0.28, 10, layer="MOBILYA"), walls=walls)[0])
    # must not fire: a stair-layer flight far outside the building's walls (site steps) stays site decor
    assert not _stairs(_furn(_flight(20.0, 2.0, 1.0, 0.28, 10, layer="MERDIVEN"), walls=walls)[0])


def test_must_not_fire_the_stair_layer_pass_on_a_numbered_stair_or_a_ladder():
    walls = [R.wall((0, 0), (10, 0)), R.wall((0, 0), (0, 8)), R.wall((10, 0), (10, 8))]
    nums = [_T(str(k), (4.3, 2.0 + 0.28 * k + 0.05, 4.45, 2.0 + 0.28 * k + 0.17)) for k in range(1, 6)]
    notes: list = []
    _furn(_flight(4.0, 2.0, 1.0, 0.28, 10, layer="MERDIVEN"), walls=walls, texts=nums, notes=notes)
    assert not any("stair layer: a stair" in n for n in notes)        # left to the numbered-stair reader
    # a ladder: rungs 0.45 m wide at 0.28 m, narrower than a walkable flight
    assert not _stairs(_furn(_flight(4.0, 2.0, 0.45, 0.28, 10, layer="MERDIVEN", arrow=False), walls=walls)[0])


# ================================================================================ the storey height against the stairs
def _house(upper_z=7.824, lines=17, marks=((0.5, 0.5, 0.5), (3.5, 3.5)), source="section"):
    sq = [[0, 0], [10, 0], [10, 8], [0, 8]]
    b = {"levels": [{"id": "L0", "order": 0, "elevation": 0.0, "elevation_source": "section", "ceiling_height": 7.674,
                     "ceiling_height_source": "section",
                     "floor_to_floor": {"value": upper_z, "method": "vector", "evidence": []}},
                    {"id": "L1", "order": 1, "elevation": upper_z, "elevation_source": source, "ceiling_height": 2.7,
                     "ceiling_height_source": "assumed_default", "floor_to_floor": None}],
         "rooms": [{"id": "r0", "level_id": "L0", "room_type": "living", "polygon": sq},
                   {"id": "r1", "level_id": "L1", "room_type": "bedroom", "polygon": sq}],
         "walls": [{"id": "w0", "level_id": "L0", "start": [0, 0], "end": [10, 0], "thickness": 0.2, "height": 7.674},
                   {"id": "w1", "level_id": "L1", "start": [0, 0], "end": [10, 0], "thickness": 0.2, "height": 2.7}],
         "openings": [{"id": "o0", "level_id": "L0", "type": "opening", "center": [5, 0], "width": 0.9,
                       "height": 7.674}],
         "slabs": [{"id": "s1", "below_level_id": "L0", "above_level_id": "L1", "z_top": upper_z}],
         "furniture": [{"id": "f0", "level_id": "L0", "type": "stair",
                        "footprint": {"center": [3, 3], "size": [1.2, 4.5], "rotation_deg": 0.0},
                        "stair": {"flights": [{"start": [3, 1], "end": [3, 5.5], "width": 1.2, "lines": lines}]}}]}
    lm = [{"id": f"m{k}", "kind": "floor", "z": z, "room_id": rid}
          for rid, zs in zip(("r0", "r1"), marks) for k, z in enumerate(zs)]
    return b, lm


def _storey(b, lm):
    from wenart.levels import model as LMO

    conflicts, inferred, warnings = [], [], []
    LMO._storey_vs_stairs(b, lm, {"mark_tol": 0.05}, conflicts, inferred, warnings)
    return conflicts, inferred, warnings


def test_a_storey_no_stair_can_climb_follows_the_marks_the_stair_climbs():
    from wenart.levels import model as LMO

    assert LMO.stair_rise_range(17) == (2.4, 3.61) and LMO.stair_rise_range(4) is None
    b, lm = _house()
    conflicts, inferred, _w = _storey(b, lm)
    l0, l1 = b["levels"]
    assert l1["elevation"] == pytest.approx(3.0) and l1["elevation_source"] == "level_mark"
    assert l1["elevation_before"] == pytest.approx(7.824)
    assert conflicts and conflicts[0]["kind"] == "storey_height_mismatch" and "f0" in conflicts[0]["element_ids"]
    # the storey under it: its ceiling, walls and openings of that ceiling height, its floor to floor; the slab above
    assert l0["ceiling_height"] == pytest.approx(2.85) and l0["floor_to_floor"]["value"] == pytest.approx(3.0)
    assert b["walls"][0]["height"] == pytest.approx(2.85) and b["walls"][1]["height"] == pytest.approx(2.7)
    assert b["openings"][0]["height"] == pytest.approx(2.85) and b["slabs"][0]["z_top"] == pytest.approx(3.0)
    assert any(i["item"] == "level L1 elevation" for i in inferred)
    # run again: the level is now a level mark's, nothing moves twice
    assert _storey(b, lm) == ([], [], [])


def test_below_the_ground_floor_the_basement_moves_never_the_ground_floor():
    # real17's case: the basement L-1 4.05 m under the ground floor by the section, its 17-step stair and its floor
    # marks -2.80 / +0.20 say 3.00 m: L-1 moves up to -3.00, the ground floor stays at 0
    b, lm = _house(marks=((-2.8,) * 4, (0.2,) * 4))
    l0, l1 = b["levels"]
    l0.update(id="L-1", order=-1, elevation=-4.048, ceiling_height=3.848)
    l1.update(id="L0", order=0, elevation=0.0, elevation_source="section")
    for key in ("rooms", "walls", "openings", "furniture"):
        for e in b[key]:
            e["level_id"] = {"L0": "L-1", "L1": "L0"}[e["level_id"]]
    b["walls"][0]["height"] = b["openings"][0]["height"] = 3.848
    b["slabs"] = [{"id": "s0", "above_level_id": "L-1", "z_top": -4.048},
                  {"id": "s1", "below_level_id": "L-1", "above_level_id": "L0", "z_top": 0.0}]
    conflicts, inferred, _w = _storey(b, lm)
    assert l1["elevation"] == 0.0 and l1["elevation_source"] == "section"
    assert l0["elevation"] == pytest.approx(-3.0) and l0["elevation_source"] == "level_mark"
    assert l0["ceiling_height"] == pytest.approx(2.8) and b["walls"][0]["height"] == pytest.approx(2.8)
    assert b["slabs"][0]["z_top"] == pytest.approx(-3.0) and b["slabs"][1]["z_top"] == 0.0
    assert conflicts[0]["kind"] == "storey_height_mismatch"


def test_must_not_fire_a_storey_the_stair_climbs_or_no_marks_or_marks_the_stair_cannot_climb():
    b, lm = _house(upper_z=3.06)                                  # a 3.06 m storey and a 17-line stair: nothing
    assert _storey(b, lm) == ([], [], []) and b["levels"][1]["elevation"] == pytest.approx(3.06)
    b, lm = _house(marks=((), ()))                               # no floor marks: a conflict, nothing moves
    conflicts, inferred, _w = _storey(b, lm)
    assert conflicts and "unresolved" in conflicts[0]["resolution"] and not inferred
    assert b["levels"][1]["elevation"] == pytest.approx(7.824)
    b, lm = _house(marks=((0.5, 0.5), (7.0, 7.0)))               # marks of 6.5 m: the stair cannot climb them either
    conflicts, inferred, _w = _storey(b, lm)
    assert conflicts and not inferred and b["levels"][1]["elevation"] == pytest.approx(7.824)
    b, lm = _house(source="level_mark")                          # a level its own marks give: never moved here
    assert _storey(b, lm) == ([], [], [])
    b, lm = _house(lines=4)                                      # a stair of 4 lines says nothing about a storey
    assert _storey(b, lm) == ([], [], [])


def test_the_storey_finding_of_rc14():
    from wenart.reading_check import sense as SN

    b, _lm = _house()
    found = SN.storey_stair_risers(b)
    assert len(found) == 1 and found[0]["rule"] == "storey_stair_risers" and found[0]["severity"] == "major"
    assert "7.82 m above L0" in found[0]["message"] and found[0]["element_ids"][:2] == ["L0", "L1"]
    b, _lm = _house(upper_z=3.0)
    assert not SN.storey_stair_risers(b)
    b["furniture"] = []                                           # a storey with no stair drawn: not this rule's
    b["levels"][1]["elevation"] = 7.824
    assert not SN.storey_stair_risers(b)
