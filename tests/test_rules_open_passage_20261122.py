"""22 Nov 2026 (the user's "build the open-passage rule"; C0053 on real07 L1; lesson UL363, the general form of UL327): a
partition that ends short of the next wall or column with nothing drawn in the gap leaves an open passage up to the
ceiling, never a wall with a door-high opening across it.

- What is drawn in a doorless gap (``openings.passage_marks``): only floor hatch, the notation and lines that end beyond
  the band may be there (``clear``); a swing, jamb or frame marks, a dashed lintel or beam (or an arch / lintel word),
  the gap's own size tag or a line along it keep the opening.
- The building rule (``twins.passage_case`` / ``twins.open_passages``): a clear gap in an inner partition between two
  rooms opens up to the ceiling; never in the outline, a party wall, a wall thicker than a partition, a slot, or into a
  shaft; a wet room's gap stays at door height and its only way in is an RC14 info finding (``sense.open_passage``).
  The dressing-room passages of UL327 are kept.
- synthetic-34-open-passage read end to end through the CPU pipeline (generated into a temporary folder).
"""
from __future__ import annotations

import copy
import math

import pytest

from wenart.ingest import twins as TW
from wenart.ingest.generic import decisions as DEC
from wenart.ingest.generic import openings as O
from wenart.ingest.generic.decisions import _Text
from wenart.ingest.generic.model import Stroke
from wenart.ingest.model import WallItem
from wenart.reading_check import score as SC
from wenart.reading_check import sense as SN
from wenart.synthetic import failure_classes as FC
from wenart.synthetic import weak_projects as WP


# --- what is drawn in the gap: the pure parts ------------------------------------------------------------------------

def _gap(a=0.0, b=2.0, t=0.15):
    """A run gap along x from ``a`` to ``b`` on the line y = 0, ``t`` thick (band y -t/2 .. t/2)."""
    return O.Gap("run", "h", 0.0, t, a, b, [])


def _items(*strokes):
    return O.StrokeIndex(list(strokes), 0.0).items


def _line(sid, p, q, layer="0", linetype=None):
    return Stroke(sid, "line", [p, q], layer=layer, linetype=linetype)


def test_hatch_notation_and_lines_ending_beyond_the_band_leave_the_gap_clear():
    items = _items(_line("h1", (0.2, -0.6), (1.4, 0.6), "TARAMA"),          # floor hatch across the gap
                   _line("h2", (0.8, -0.6), (2.0, 0.6), "KARO"),            # tiles
                   _line("t1", (1.0, -1.2), (1.0, 1.2), "MB"),              # a stair's tread through the gap
                   _line("t2", (0.02, -1.0), (0.02, -0.075), "MB"),         # ... and one ending on the face at a jamb
                   _line("r1", (0.5, -0.9), (1.5, 0.9), "CATI", "DASHED"),  # a roof's hip, dashed and diagonal
                   _line("w1", (0.0, -0.075), (0.0, 0.075), "DUVAR"),       # the wall end's own closing line
                   _line("w2", (2.0, -0.075), (2.0, 0.075), "A-101"))       # ... on a layer named for nothing
    verdict, note, ids = O.passage_marks(_gap(), items, wall_ids={"w2"})
    assert verdict == "clear" and ids == [], note


def test_a_dashed_lintel_or_beam_along_the_gap_keeps_the_opening():
    beam = _line("b1", (0.0, 0.075), (2.0, 0.075), "KIRIS", "DASHED")
    assert O.passage_marks(_gap(), _items(beam))[0] == "lintel"
    # the linetype from the page (the strokes in metres carry none)
    plain = _line("b2", (0.0, -0.075), (2.0, -0.075), "KIRIS")
    assert O.passage_marks(_gap(), _items(plain), linetypes={"b2": "HIDDEN"})[0] == "lintel"
    # a PDF's dashes: short pieces in one line with breaks between them
    dashes = [_line(f"d{k}", (0.1 + 0.4 * k, 0.07), (0.35 + 0.4 * k, 0.07)) for k in range(5)]
    assert O.passage_marks(_gap(), _items(*dashes))[0] == "lintel"


def test_an_arch_or_lintel_word_or_the_gaps_own_size_tag_keeps_the_opening():
    g = _gap(0.0, 1.5)
    assert O.passage_marks(g, [], texts=[_Text(at=(0.75, 0.5), text="KEMER", height=0.2)])[0] == "lintel"
    assert O.passage_marks(g, [], texts=[_Text(at=(0.75, 0.4), text="150/230", height=0.12,
                                               size_tag=(1.5, 2.3))])[0] == "tag"
    # a neighbouring door's tag (90 wide by a 1.50 m gap) or a word far away says nothing about this gap
    assert O.passage_marks(g, [], texts=[_Text(at=(0.75, 0.4), text="90/210", height=0.12, size_tag=(0.9, 2.1)),
                                         _Text(at=(0.75, 3.0), text="KEMER", height=0.2)])[0] == "clear"


def test_jamb_or_frame_marks_keep_the_opening_of_a_door_drawn_without_its_leaf():
    cap = _line("k1", (0.03, -0.075), (0.03, 0.075), "KAPI")                 # a frame cap on the door layer
    assert O.passage_marks(_gap(), _items(cap))[0] == "jambs"
    frame = _line("f1", (1.97, -0.075), (1.97, 0.075), "FRAME")              # a frame line on a layer of no role
    assert O.passage_marks(_gap(), _items(frame))[0] == "jambs"
    wall = WallItem((0, 0), (0.04, 0), 0.15, [0, 0, 0, 0], "LWPOLYLINE:S1", {})
    stub = O.Piece(0, "h", 0.0, 0.15, -0.04, 0.0, wall)                      # an end cap (a jamb stub) at the jamb
    assert O.passage_marks(_gap(), [], caps=[stub])[0] == "jambs"


def test_a_swing_or_a_line_along_the_gap_keeps_the_opening():
    arc = Stroke("a1", "arc", [(0.9 * math.cos(k / 10), 0.075 + 0.9 * math.sin(k / 10)) for k in range(16)], layer="0",
                 arc={"center": (0.0, 0.075), "radius": 0.9, "start_deg": 0.0, "end_deg": 90.0})
    assert O.passage_marks(_gap(), _items(arc))[0] == "swing"
    sill = _line("s1", (0.0, 0.0), (2.0, 0.0), "0")                          # a solid line along it
    assert O.passage_marks(_gap(), _items(sill))[0] == "lines"
    window = _line("g1", (0.5, 0.01), (0.9, 0.01), "PENCERE")                # a window stroke in the band
    assert O.passage_marks(_gap(), _items(window))[0] == "lines"


# --- the building rule: the pure parts -------------------------------------------------------------------------------

def _room(rid, x0, y0, x1, y1, rtype="living", label=None):
    return {"id": rid, "level_id": "L0", "room_type": rtype, "label": label or rid,
            "polygon": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]}


def _wall(wid, a, b, t=0.15, **kw):
    return dict({"id": wid, "level_id": "L0", "start": list(a), "end": list(b), "thickness": t, "exterior": False}, **kw)


def _gap_op(oid, wall, cx, cy, w, verdict="clear"):
    return {"id": oid, "type": "opening", "level_id": "L0", "wall_id": wall, "center": [cx, cy], "width": w,
            "height": 2.1, "evidence": [{"method": "derived", "passage": verdict}]}


def _flat(op_width=2.0, t=0.15, side_type="hall", **wall_kw):
    """A living room below a partition on y = 4.4 and a hall (or ``side_type``) above it; a gap in the partition."""
    rooms = [_room("r_salon", 0.0, 0.0, 7.0, 4.325), _room("r_hol", 0.0, 4.475, 7.0, 5.8, side_type)]
    walls = [_wall("w_part", (0.0, 4.4), (7.0, 4.4), t, **wall_kw)]
    ops = [_gap_op("o_1", "w_part", 5.5, 4.4, op_width)]
    return rooms, walls, ops


def test_a_clear_gap_in_an_inner_partition_opens_up_to_the_ceiling():
    rooms, walls, ops = _flat()
    notes = TW.open_passages(rooms, ops, [{"id": "L0", "ceiling_height": 2.8}], walls)
    assert ops[0]["open_passage"] is True and ops[0]["height"] == 2.8 and len(notes) == 1
    assert ops[0]["evidence"][-1]["rule"] == "open_passage"
    # what stands of the wall: the passage is cut out of it (the score's view, C0053)
    pieces = SC.solid_pieces(walls[0], ops, 2.8)
    assert [round(p["end"][0] - p["start"][0], 2) for p in pieces] == [4.5, 0.5]


def test_never_in_the_outline_a_party_wall_or_a_thick_wall():
    # 0.25 m: a stair or lift core's wall (real21) or a shelter's (real18), no partition
    for kw, t in (({"exterior": True}, 0.15), ({"party_wall": True}, 0.15), ({}, 0.25), ({}, 0.30)):
        rooms, walls, ops = _flat(t=t, **kw)
        if kw.get("exterior"):
            rooms = rooms[:1]           # 23 Nov 2026 (UL372): the outline: the open air beyond the wall, no room
        case = TW.passage_case(ops[0], rooms, {w["id"]: w for w in walls}, ops)
        assert not case["open"], (kw, t, case["why"])
    # 23 Nov 2026 (UL372, real15 o_L0_001): a wall flagged exterior with a room on both sides of the gap is no outline
    # there (its flag read before the outline was final): the passage opens
    rooms, walls, ops = _flat(exterior=True)
    assert TW.passage_case(ops[0], rooms, {w["id"]: w for w in walls}, ops)["open"]


def test_never_into_a_shaft_never_a_slot_never_a_gap_with_marks():
    rooms, walls, ops = _flat(side_type="shaft")
    assert not TW.passage_case(ops[0], rooms, {w["id"]: w for w in walls}, ops)["open"]
    rooms, walls, ops = _flat(side_type="storage")
    rooms[1]["label"] = "Sığınak"                          # a shelter's way in has a blast door
    assert not TW.passage_case(ops[0], rooms, {w["id"]: w for w in walls}, ops)["open"]
    rooms[1]["label"] = "Depo"                              # a store room: open
    assert TW.passage_case(ops[0], rooms, {w["id"]: w for w in walls}, ops)["open"]
    rooms, walls, ops = _flat(op_width=0.05)               # a few cm: the reader closes those (GAP_MIN_M) anyway
    assert not TW.passage_case(ops[0], rooms, {w["id"]: w for w in walls}, ops)["open"]
    assert O.GAP_MIN_M <= TW.OPEN_PASSAGE_MIN_M
    for verdict in ("lintel", "jambs", "tag", "lines", "swing"):
        rooms, walls, ops = _flat()
        ops[0]["evidence"][0]["passage"] = verdict
        assert not TW.passage_case(ops[0], rooms, {w["id"]: w for w in walls}, ops)["open"], verdict
    rooms, walls, ops = _flat()
    ops[0]["evidence"][0].pop("passage")                    # an opening the reader did not judge (angled, raster)
    assert TW.open_passages(rooms, ops, [], walls) == [] and not ops[0].get("open_passage")


def test_a_wet_rooms_only_way_in_stays_at_door_height_and_is_an_info_finding():
    rooms, walls, ops = _flat(op_width=0.8, side_type="bathroom")
    notes = TW.open_passages(rooms, ops, [], walls)
    assert not ops[0].get("open_passage") and ops[0]["height"] == 2.1 and "privacy" in notes[0]
    case = TW.passage_case(ops[0], rooms, {w["id"]: w for w in walls}, ops)
    assert case["wet_only"]["id"] == "r_hol"
    found = SN.apply_trust(SN.open_passage({"levels": [{"id": "L0"}], "rooms": rooms, "walls": walls,
                                            "openings": ops}), SN.load_trust())
    assert len(found) == 1 and found[0]["severity"] == "info" and "only way into" in found[0]["message"]
    # a second way in: kept at door height all the same, no finding
    ops.append({"id": "d_2", "type": "door", "level_id": "L0", "wall_id": "w_x", "center": [0.0, 5.0], "width": 0.8})
    assert TW.passage_case(ops[0], rooms, {w["id"]: w for w in walls}, ops)["wet_only"] is None
    assert not TW.passage_case(ops[0], rooms, {w["id"]: w for w in walls}, ops)["open"]


def test_the_dressing_room_passage_of_ul327_is_kept():
    rooms = [_room("r_yatak", 0.0, 0.0, 4.0, 3.925, "bedroom"),
             _room("r_giyinme", 0.0, 4.075, 4.0, 6.0, "storage", label="Giyinme Soyunma")]
    ops = [{"id": "o_1", "type": "opening", "level_id": "L0", "wall_id": "w_1", "center": [2.0, 4.0], "width": 0.72,
            "height": 2.1, "evidence": [{"method": "derived"}]}]           # no passage verdict, no walls given
    notes = TW.open_passages(rooms, ops, [{"id": "L0", "ceiling_height": 2.7}])
    assert ops[0]["open_passage"] is True and ops[0]["height"] == 2.7 and "dressing room" in notes[0]
    # a slot beside a dressing room is no way through (real15 L1's 0.25 m gap)
    ops = [dict(ops[0], width=0.25, height=2.1, open_passage=None)]
    assert TW.open_passages(rooms, ops, [{"id": "L0", "ceiling_height": 2.7}]) == [] and not ops[0]["open_passage"]


def test_the_rule_is_registered_and_the_check_is_uncalibrated():
    assert DEC.RULE_CONFIDENCE["open_passage"] == TW.OPEN_PASSAGE_CONFIDENCE
    assert "open_passage" in SN.RULES
    trust = SN.load_trust()["rules"]["open_passage"]
    assert trust["precision"] is None and trust["trusted"] is False


def test_the_score_matches_an_asserted_open_passage_only_on_a_passage():
    truth = [{"center": [5.5, 4.4], "attrs": {"open_passage": True}}, {"center": [1.0, 4.4],
                                                                       "attrs": {"open_passage": False}}]
    read = [{"center": [5.5, 4.4]}, {"center": [1.0, 4.4]}]
    assert SC.match_attrs("openings", truth, read) == [(1, 1)]
    read[0]["open_passage"] = True
    assert sorted(SC.match_attrs("openings", truth, read)) == [(0, 0), (1, 1)]


# --- synthetic-34-open-passage end to end ----------------------------------------------------------------------------

@pytest.fixture(scope="module")
def reading(tmp_path_factory):
    from wenart.ingest import pipeline as PL

    root = tmp_path_factory.mktemp("rules_open_passage")
    project = WP.project_34()
    FC.generate_failure_project(project, root)
    building, _build = PL.run_project(root / project.name, root / f"{project.name}-out", no_ai=True)
    return project, root, building


def _at(building, x, y, kind=None):
    return [o for o in building["openings"] if (kind is None or o["type"] == kind)
            and math.dist(o["center"][:2], (x, y)) <= 0.3]


def test_synthetic_34_opens_the_passage_and_keeps_the_others(reading):
    _project, _root, b = reading
    passage = _at(b, 5.7625, 4.4)
    assert len(passage) == 1 and passage[0]["open_passage"] is True and passage[0]["height"] >= 2.6
    beam, banyo = _at(b, 2.0, 5.8), _at(b, 5.2, 5.8)
    assert len(beam) == 1 and not beam[0].get("open_passage") and beam[0]["evidence"][0]["passage"] == "lintel"
    assert len(banyo) == 1 and not banyo[0].get("open_passage") and banyo[0]["height"] < 2.5
    facade = _at(b, 0.125, 7.4)
    assert len(facade) == 1 and not facade[0].get("open_passage")
    rc14 = [f for f in SN.run(copy.deepcopy(b)) if f["rule"] == "open_passage"]
    assert [f["element_ids"][0] for f in rc14] == [banyo[0]["id"]]


def test_synthetic_34_scores_100(reading):
    from wenart.reading_check import truth as TR

    project, root, b = reading
    truth = TR.synthetic_truth(project.name, root / project.name / FC.TRUTH_FILE)
    assert SC.match(truth, SC.reading_for(truth, b, project.name), b)["total"] == 100.0
